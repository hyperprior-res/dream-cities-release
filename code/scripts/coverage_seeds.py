#!/usr/bin/env python
"""The coverage model against three training seeds of the main configuration .

    CUDA_VISIBLE_DEVICES= PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/coverage_seeds.py

A referee asked whether the coverage model's difference from the main checkpoint exceeds what another training seed
gives. The main configuration (``os_50m_full``, 6,000,000 samples) has three training seeds: the main checkpoint (seed
0) and ``os_50m_full_s1`` and ``os_50m_full_s2``; the coverage model is ``os_50m_cov`` (same code, seed and samples,
wider data). Each is audited on the 193 instances of the 40 original cities (``data/tasks_v2_H24.json``) by random
search and by the pool-seeded (adaptive) search; this script reads both audits at 1,000 evaluations for all four.

Quantities, per model and search, with the definitions of ``analyse_ladder.py`` (its readers are imported, nothing in
it is changed): the false acceptance of the selected plans (the emulator accepts, pass share >= 0.5 of 8 samples, and
the 32-seed majority oracle rejects); the perfect-emulator reference's false acceptance on the same instances; (i) the
excess, false acceptance minus the reference's, paired by instance; (ii) real success, the oracle's acceptance of the
selected plans; (iii) false rejection, among the selected plans the oracle accepts the share the emulator rejects
(defined where at least one selected plan passes). For each quantity: the three seeds' minimum, maximum and mean, and
the paired difference coverage minus the mean of the three seeds (per instance for (i) and (ii); a difference of
ratios for (iii)), cluster bootstrap over start-state families, 2,000 resamples, seed 0, BCa with the percentile
interval where BCa is undefined (the interval ``analyse_ladder.py`` uses for ``decision_fidelity`` and the coverage
arm). The analysis plan's reading (fixed before any number of the two further seeds was read): the coverage model's value
``below_all`` (below the lowest seed), ``above_all`` (above the highest) or ``within``; its wording is fixed for (i)
and (ii); (iii) is printed side by side only and carries the same position key without a wording. Positions are
compared on exact counts (every rate of (i) and (ii) has the same 193 instances as its denominator).

Checks (the script stops if one fails): every audit reads ``ok`` with ``analyse_ladder.read_audit`` and is paired with
the perfect emulator on all 193 instances; the four models hold the same instances, start-state families and reference
verdicts; each audit's card names its own run's checkpoint, and the two searches of a run name the same sha256; each
audit reproduces its ``reference.json`` (all instances, value and intervals); the main checkpoint's and the coverage
model's statistics and their paired difference equal ``results/analysis/coverage.json``, and the main checkpoint's
equal ``results/analysis/replication.json`` (40 cities).

Outputs: ``results/analysis/coverage_seeds.json`` and ``.md``. Read: the eight audits under ``results/audit/ladder/``,
their perfect-emulator reference under ``results/audit/engine_reference/``, the tasks file and the two analysis files;
no checkpoint file is opened (the cards' sha256 are compared instead), and nothing but the two outputs is written.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "code" / "scripts", ROOT / "code", ROOT / "hpr-dream"):
    sys.path.insert(0, str(p))

import numpy as np  # noqa: E402

import analyse_ladder as al  # noqa: E402  (Reader, read_audit, units_all_families, arm, model_difference, formats)
import hpr_dream.stats as hs  # noqa: E402

SAMPLES = 6_000_000
SEEDS = ("os_50m_full", "os_50m_full_s1", "os_50m_full_s2")       # training seeds 0 (the main checkpoint), 1, 2
COV = "os_50m_cov"
MODELS = SEEDS + (COV,)
LABEL = {"os_50m_full": "seed 0 (main checkpoint)", "os_50m_full_s1": "seed 1", "os_50m_full_s2": "seed 2",
         COV: "coverage model"}
METHODS = ("random", "cem_seeded")
METHOD_LABEL = {"random": "random search", "cem_seeded": "pool-seeded (adaptive) search"}
B = 1000
QUANTITIES = (("excess", "(i) excess false acceptance over the perfect emulator", True),
              ("real_success", "(ii) real success of the selected plans", True),
              ("false_rejection", "(iii) false rejection of the selected plans", False))
# the analysis plan's two fixed wordings ("[above]" written out), used as written
WORDING = {"below_all": "lies below all three training seeds of the original configuration",
           "above_all": "lies above all three training seeds of the original configuration",
           "within": "lies within the spread of three training seeds of the original configuration, so its difference "
                     "from the main checkpoint cannot be told from seed-to-seed variation"}
LOOSE = "three seeds bound the spread loosely"
TOL = 1e-12


def entry(run: str) -> dict:
    """``read_audit``'s checkpoint entry; the sha256 is checked against the cards below (``check_cards``), so no
    checkpoint file is read."""
    return {"checkpoint": f"{run}-samples_{SAMPLES:09d}", "run": run, "samples": SAMPLES, "sha256": None}


def check_cards(root: Path, auds: dict, rd: al.Reader) -> dict:
    """Each audit's card names its own run's checkpoint; a run's two searches name one sha256; the runs differ."""
    sha = {}
    for run in MODELS:
        got = set()
        for m in METHODS:
            card = rd.json(root / auds[(run, m)]["dir"] / "card.json") or {}
            j = (card.get("meta") or {}).get("judge") or {}
            p = Path(j.get("ckpt", ""))
            if p.name != f"samples_{SAMPLES:09d}.pt" or p.parent.name != run or not j.get("ckpt_sha256"):
                raise SystemExit(f"{auds[(run, m)]['dir']}: the card's judge is {p}, not {run}'s checkpoint")
            got.add(j["ckpt_sha256"])
        if len(got) != 1:
            raise SystemExit(f"{run}: the two searches name different checkpoints {sorted(got)}")
        sha[run] = got.pop()
    if len(set(sha.values())) != len(MODELS):
        raise SystemExit(f"two runs name the same checkpoint: {sha}")
    return sha


def aligned_units(auds: dict, method: str) -> dict:
    """Each model's units at B on every instance, in the main checkpoint's order; the same instances, start-state
    families and reference verdicts in all four (one perfect emulator for all)."""
    us = {}
    for run in MODELS:
        u = al.units_all_families(auds[(run, method)], B)
        if u is None:
            raise SystemExit(f"{run}, {method}: a family is incomplete at B={B}")
        if u.get("gr") is None or u["n_paired"] != u["n"]:
            raise SystemExit(f"{run}, {method}: not paired with the perfect emulator on every instance")
        us[run] = u
    base = [k[0] for k in us[SEEDS[0]]["keys"]]
    if len(set(base)) != len(base):
        raise SystemExit(f"{method}: an instance appears twice")
    out = {}
    for run, u in us.items():
        pos = {k[0]: i for i, k in enumerate(u["keys"])}
        if set(pos) != set(base):
            raise SystemExit(f"{run}, {method}: other instances than the main checkpoint's")
        ix = np.array([pos[k] for k in base])
        v = {"status": "ok", "n": u["n"], "n_paired": u["n_paired"], "keys": [u["keys"][i] for i in ix],
             "cl": [u["cl"][i] for i in ix]}
        for f in ("ga", "oa", "gr", "orr"):
            v[f] = np.asarray(u[f])[ix]
        out[run] = v
    b = out[SEEDS[0]]
    for run, v in out.items():
        if v["cl"] != b["cl"]:
            raise SystemExit(f"{run}, {method}: start-state families differ from the main checkpoint's records")
        if not (np.array_equal(v["gr"], b["gr"]) and np.array_equal(v["orr"], b["orr"])):
            raise SystemExit(f"{run}, {method}: the perfect-emulator verdicts differ from the main checkpoint's")
    return out


def _hacked(u: dict) -> np.ndarray:
    return (u["ga"] & ~u["oa"]).astype(float)


def _ref_hacked(u: dict) -> np.ndarray:
    return (u["gr"] & ~u["orr"]).astype(float)


def counts(u: dict) -> dict:
    ga, oa = u["ga"], u["oa"]
    return {"n": int(ga.size), "hacked": int((ga & ~oa).sum()), "perfect_hacked": int((u["gr"] & ~u["orr"]).sum()),
            "oracle_accepts": int(oa.sum()), "emulator_accepts": int(ga.sum()),
            "falsely_rejected": int((oa & ~ga).sum())}


def exact(q: str, c: dict):
    """A quantity as an exact number (for the analysis plan's comparison): (i) and (ii) over the same instances."""
    if q == "excess":
        return Fraction(c["hacked"] - c["perfect_hacked"], c["n"])
    if q == "real_success":
        return Fraction(c["oracle_accepts"], c["n"])
    return Fraction(c["falsely_rejected"], c["oracle_accepts"]) if c["oracle_accepts"] else None


def position(cov, seeds) -> str | None:
    """The analysis plan: below the lowest seed, above the highest, or within the spread (ties with a seed are within)."""
    if cov is None or any(s is None for s in seeds):
        return None
    if cov < min(seeds):
        return "below_all"
    if cov > max(seeds):
        return "above_all"
    return "within"


def model_values(u: dict, n_boot: int, seed: int) -> dict:
    """One model's statistics on the units (``analyse_ladder.arm``: BCa, percentile where undefined)."""
    a = al.arm(u, n_boot, seed)
    e = a["emulator"]
    return {"arm": a, "false_acceptance": e["hackability"], "perfect_false_acceptance": a["perfect_emulator"]["hackability"],
            "excess": a["difference"], "real_success": e["oracle_accept"], "false_rejection": e["false_rejection"],
            "emulator_accepts": e["judge_accept"], "counts": counts(u)}


def seed_mean_difference(units: dict, n_boot: int, seed: int) -> dict:
    """Coverage minus the mean of the three seeds, on the same cluster resamples. (i) and (ii): per instance,
    ``hpr_dream.stats.excess``; (iii): the coverage model's ratio minus the mean of the seeds' ratios."""
    kw = dict(n_boot=n_boot, seed=seed, bca=True)
    uc, ss = units[COV], [units[s] for s in SEEDS]
    cl = list(uc["cl"])
    r = _ref_hacked(uc)
    out = {"excess": hs.excess(_hacked(uc) - r, np.mean([_hacked(s) for s in ss], axis=0) - r, cl, **kw),
           "real_success": hs.excess(uc["oa"].astype(float), np.mean([s["oa"].astype(float) for s in ss], axis=0),
                                     cl, **kw)}
    if not all(u["oa"].any() for u in (uc, *ss)):
        out["false_rejection"] = None
        return out
    codes, C = al._encode(cl)
    sums = [(np.bincount(codes, weights=(u["oa"] & ~u["ga"]).astype(float), minlength=C),
             np.bincount(codes, weights=u["oa"].astype(float), minlength=C)) for u in (uc, *ss)]

    def stat(W):
        with np.errstate(invalid="ignore", divide="ignore"):
            rat = [np.where(W @ d > 0, (W @ n) / np.where(W @ d > 0, W @ d, 1), np.nan) for n, d in sums]
        return rat[0] - np.mean(rat[1:], axis=0)
    out["false_rejection"] = hs._from_weights(stat, C, len(cl), n_boot, seed, hs.LEVEL, True)[0]
    return out


def _est_equal(mine: hs.Estimate | None, theirs: dict | None) -> list[str]:
    """Value and every interval limit equal (NaN equals NaN / None); returns the fields that differ."""
    if mine is None or theirs is None:
        return [] if mine is None and theirs is None else ["presence"]
    bad = []
    for fld in ("value", "lo", "hi", "bca_lo", "bca_hi", "n_units", "n_clusters"):
        x, y = getattr(mine, fld), theirs.get(fld)
        xn = x is None or (isinstance(x, float) and np.isnan(x))
        yn = y is None or (isinstance(y, float) and np.isnan(y))
        if xn and yn:
            continue
        if xn != yn or not np.isclose(float(x), float(y), rtol=0, atol=TOL):
            bad.append(f"{fld}: {x} vs {y}")
    return bad


def check_against_analysis(vals: dict, diffs_main: dict, coverage_json: dict, replication_json: dict | None) -> list[str]:
    """The main checkpoint's and the coverage model's statistics (and coverage minus main) as
    ``results/analysis/coverage.json`` holds them; the main checkpoint's as ``replication.json`` (40 cities)."""
    done = []
    if coverage_json.get("main") != f"{SEEDS[0]}-samples_{SAMPLES:09d}" or \
            coverage_json.get("coverage") != f"{COV}-samples_{SAMPLES:09d}":
        raise SystemExit("coverage.json: other models than the main checkpoint and the coverage model")
    for m in METHODS:
        g = coverage_json["methods"][m]["budgets"][str(B)]["all"]
        for who, run in (("main", SEEDS[0]), ("coverage", COV)):
            a, t = vals[m][run]["arm"], g[who]
            pairs = [(f"emulator.{k}", a["emulator"][k], t["emulator"][k])
                     for k in ("hackability", "judge_accept", "oracle_accept", "false_rejection")]
            pairs += [("perfect_emulator.hackability", a["perfect_emulator"]["hackability"],
                       t["perfect_emulator"]["hackability"]),
                      ("perfect_emulator.oracle_accept", a["perfect_emulator"]["oracle_accept"],
                       t["perfect_emulator"]["oracle_accept"]), ("difference", a["difference"], t["difference"])]
            for name, mine, theirs in pairs:
                bad = _est_equal(mine, theirs)
                if bad:
                    raise SystemExit(f"coverage.json, {m}, {who}: {name} differs ({'; '.join(bad)})")
            if a["n"] != t["n"] or a["n_paired"] != t["n_paired"]:
                raise SystemExit(f"coverage.json, {m}, {who}: counts differ")
        for k in ("hackability", "oracle_accept", "judge_accept", "false_rejection", "excess_over_perfect"):
            bad = _est_equal(diffs_main[m][k], g["coverage_minus_main"][k])
            if bad:
                raise SystemExit(f"coverage.json, {m}: coverage_minus_main.{k} differs ({'; '.join(bad)})")
        done.append(f"{m}: the main checkpoint's and the coverage model's statistics and their paired difference equal "
                    f"results/analysis/coverage.json")
        if replication_json is not None:
            r = replication_json["methods"][m][str(B)]["c40"]
            a = vals[m][SEEDS[0]]["arm"]
            for name, mine, theirs in (("emulator.hackability", a["emulator"]["hackability"], r["emulator"]["hackability"]),
                                       ("emulator.oracle_accept", a["emulator"]["oracle_accept"],
                                        r["emulator"]["oracle_accept"]),
                                       ("emulator.false_rejection", a["emulator"]["false_rejection"],
                                        r["emulator"]["false_rejection"]),
                                       ("difference", a["difference"], r["difference"])):
                bad = _est_equal(mine, theirs)
                if bad:
                    raise SystemExit(f"replication.json, {m}, 40 cities: {name} differs ({'; '.join(bad)})")
            done.append(f"{m}: the main checkpoint's statistics equal results/analysis/replication.json (40 cities)")
    return done


def check_reference_json(root: Path, aud: dict, method: str, a: dict, rd: al.Reader) -> dict:
    """The run's own reference.json (all instances, this search, B): value and intervals of the emulator's false
    acceptance, the perfect emulator's and the difference (as ``analyse_ladder.replication`` checks the main's)."""
    refj = rd.json(root / aud["dir"] / "reference.json")
    if refj is None:
        return {"status": "no reference.json"}
    grp = [x for x in refj.get("subsets", {}).get("all", {}).get("groups", [])
           if x.get("method") == method and int(x.get("budget", -1)) == B]
    if len(grp) != 1:
        raise SystemExit(f"{aud['dir']}: reference.json has {len(grp)} all-instance groups for {method} at B={B}")
    g = grp[0]
    bad = []
    for name, mine, theirs in (("difference", a["difference"], g["difference"]),
                               ("hackability", a["emulator"]["hackability"], g["emulator"]["hackability"]),
                               ("perfect", a["perfect_emulator"]["hackability"], g["perfect_emulator"]["hackability"])):
        for fld in ("value", "bca_lo", "bca_hi", "lo", "hi"):
            x, y = getattr(mine, fld), theirs.get(fld)
            if not ((y is None and not np.isfinite(x)) or (y is not None and np.isclose(x, y, rtol=0, atol=1e-9))):
                bad.append(f"{name} {fld}: {x} vs {y}")
    if any(b.split()[1] == "value:" for b in bad) or g.get("n_paired") != a["n"]:
        raise SystemExit(f"{aud['dir']}: the records disagree with reference.json ({'; '.join(bad[:4])})")
    return {"status": "ok", "n_paired": g.get("n_paired"), "differ": bad,
            "per_family_check": aud.get("reference_json_check")}


def build(root: Path, tasks_path: Path, ref_root: Path, coverage_path: Path, replication_path: Path | None,
          n_boot: int, seed: int) -> dict:
    rd = al.Reader(root)
    tasks = al.load_tasks(tasks_path)
    n_tasks = sum(tasks["n"].values())
    ref_cache: dict = {}
    auds = {(run, m): al.read_audit(entry(run), m, tasks, root, ref_root, rd, ref_cache) for run in MODELS for m in METHODS}
    for (run, m), a in auds.items():
        if a["status"] != "ok":
            raise SystemExit(f"{run}, {m}: audit {a['status']} ({a['dir']})")
        rc = a.get("reference_json_check") or {}
        if rc.get("differ"):
            raise SystemExit(f"{run}, {m}: reference.json disagrees with the records: {rc['differ'][:4]}")
    sha = check_cards(root, auds, rd)
    out = {"decision": "the analysis plan , the specification, slot C3", "budget": B, "tasks": tasks["stem"],
           "tasks_sha256": tasks["sha256"], "seeds": list(SEEDS), "coverage": COV, "labels": LABEL,
           "checkpoints": {run: {"checkpoint": f"{run}-samples_{SAMPLES:09d}", "sha256": sha[run],
                                 "audits": {m: auds[(run, m)]["dir"] for m in METHODS},
                                 "reference": {m: auds[(run, m)].get("reference") for m in METHODS}} for run in MODELS},
           "definitions": {q: d for q, d, _ in QUANTITIES},
           "interval": f"cluster bootstrap over start-state families, {n_boot} resamples, seed {seed}, BCa 95 per cent "
                       "(percentile where BCa is undefined; the exact one-sided bound where no unit is falsely accepted), "
                       "hpr_dream.stats, as analyse_ladder.py's decision_fidelity and coverage arm",
           "paired_difference": "coverage model minus the mean of the three seeds on the same instances and the same "
                                "cluster resamples: per instance for (i) and (ii) (the reference is common, so (i)'s "
                                "difference is the difference in false acceptance); for (iii) the coverage model's ratio "
                                "minus the mean of the seeds' ratios",
           "reading_rule": "the analysis plan: the coverage model's value below the lowest of the three seeds (below_all), "
                           "above the highest (above_all), otherwise within (a tie with a seed is within); compared on "
                           "exact counts; the wording is fixed for (i) and (ii), and (iii) carries the position only",
           "wording": WORDING, "always": LOOSE, "methods": {}, "checks": [], "notes": []}
    vals, diffs_main = {}, {}
    for m in METHODS:
        units = aligned_units(auds, m)
        n = units[SEEDS[0]]["n"]
        if any(units[r]["n"] != n_tasks for r in MODELS):
            raise SystemExit(f"{m}: {[units[r]['n'] for r in MODELS]} instances, the tasks file has {n_tasks}")
        vals[m] = {run: model_values(units[run], n_boot, seed) for run in MODELS}
        for run in MODELS:
            vals[m][run]["reference_json"] = check_reference_json(root, auds[(run, m)], m, vals[m][run]["arm"], rd)
        diffs_main[m] = al.model_difference(units[COV], units[SEEDS[0]], True, n_boot, seed)
        sd = seed_mean_difference(units, n_boot, seed)
        q_out = {}
        for q, desc, worded in QUANTITIES:
            ex = {run: exact(q, vals[m][run]["counts"]) for run in MODELS}
            est = {run: vals[m][run][q] for run in MODELS}
            sv = [None if est[s] is None else est[s].value for s in SEEDS]
            pos = position(ex[COV], [ex[s] for s in SEEDS])
            q_out[q] = {"definition": desc, "coverage": None if est[COV] is None else est[COV].value,
                        "seeds": sv, "seed_min": None if None in sv else min(sv),
                        "seed_max": None if None in sv else max(sv),
                        "seed_mean": None if None in sv else float(np.mean(sv)),
                        "exact": {run: None if ex[run] is None else f"{ex[run].numerator}/{ex[run].denominator}"
                                  for run in MODELS},
                        "coverage_minus_seed_mean": sd[q], "position": pos,
                        "decision_87_wording_applies": worded,
                        "reading": pos if worded else None,
                        "wording": WORDING[pos] if worded and pos else None}
            if est[COV] is not None and sd[q] is not None and est[COV] is not None and None not in sv:
                if not np.isclose(sd[q].value, est[COV].value - np.mean(sv), rtol=0, atol=1e-12):
                    raise SystemExit(f"{m}, {q}: the paired difference's point disagrees with the values")
        fa = [vals[m][run]["false_acceptance"].value for run in SEEDS]
        q_out["false_acceptance"] = {"definition": "false acceptance of the selected plans (beside (i); the reference "
                                                   "is common, so its position is (i)'s)",
                                     "coverage": vals[m][COV]["false_acceptance"].value, "seeds": fa,
                                     "seed_min": min(fa), "seed_max": max(fa), "seed_mean": float(np.mean(fa))}
        out["methods"][m] = {
            "search": METHOD_LABEL[m], "n": n, "n_clusters": len(set(units[SEEDS[0]]["cl"])),
            "perfect_false_acceptance": vals[m][SEEDS[0]]["perfect_false_acceptance"],
            "perfect_real_success": vals[m][SEEDS[0]]["arm"]["perfect_emulator"]["oracle_accept"],
            "models": {run: {k: v for k, v in vals[m][run].items() if k != "arm"} for run in MODELS},
            "quantities": q_out, "coverage_minus_main": diffs_main[m]}
    out["checks"].append(f"every audit reads ok with analyse_ladder.read_audit, paired with the perfect emulator on all "
                         f"{n_tasks} instances of the tasks file; the four models hold the same instances, start-state families and "
                         "reference verdicts; each card names its own run's checkpoint")
    for m in METHODS:
        for run in MODELS:
            rj = vals[m][run]["reference_json"]
            if rj["status"] != "ok":
                out["notes"].append(f"{run}, {m}: {rj['status']}")
            elif rj["differ"]:
                out["notes"].append(f"{run}, {m}: reference.json intervals differ in {len(rj['differ'])} limits "
                                    f"({'; '.join(rj['differ'][:3])})")
    out["checks"].append("each audit's all-instance false acceptance, perfect-emulator false acceptance and excess equal "
                         "its reference.json (values; any interval limit that differs is listed in notes)")
    cov_json = json.loads(Path(coverage_path).read_text())
    rep_json = json.loads(Path(replication_path).read_text()) if replication_path and Path(replication_path).is_file() \
        else None
    out["checks"] += check_against_analysis(vals, diffs_main, cov_json, rep_json)
    out["inputs"] = rd.manifest
    out["status"] = "complete"
    return out


def write_md(path: Path, res: dict, cmd: str, generated: str):
    L = ["# The coverage model against three training seeds of the main configuration ", "",
         f"Generated {generated} by `{cmd}`. Tasks `{res['tasks']}` (the 40 original cities), budget {res['budget']:,}; "
         f"models: " + "; ".join(f"`{res['checkpoints'][r]['checkpoint']}` ({res['labels'][r]})" for r in MODELS)
         + f". Intervals: {res['interval']}. Paired difference: {res['paired_difference']}. Reading: "
         f"{res['reading_rule']}. Status: {res['status'].upper()}.", ""]
    for m, v in res["methods"].items():
        L += [f"## {v['search']} ({v['n']} instances, {v['n_clusters']} start-state families)", "",
              f"Perfect emulator: false acceptance {al.fb(v['perfect_false_acceptance'])}, real success "
              f"{al.fb(v['perfect_real_success'])}.", "",
              "| model | false acceptance | excess over perfect | real success | false rejection | emulator accepts | "
              "falsely accepted / perfect / oracle accepts / falsely rejected |", "|---|---|---|---|---|---|---|"]
        for run in MODELS:
            x, c = v["models"][run], v["models"][run]["counts"]
            L.append(f"| {res['labels'][run]} | {al.fb(x['false_acceptance'])} | {al.fbs(x['excess'])} | "
                     f"{al.fb(x['real_success'])} | {al.fb(x['false_rejection'])} | {al.fb(x['emulator_accepts'])} | "
                     f"{c['hacked']} / {c['perfect_hacked']} / {c['oracle_accepts']} / {c['falsely_rejected']} |")
        L += ["", "| quantity | coverage | seeds 0, 1, 2 | seeds' min / max / mean | coverage minus seed mean | "
                  "position  | wording |", "|---|---|---|---|---|---|---|"]
        for q, _, worded in QUANTITIES:
            x = v["quantities"][q]
            sv = ", ".join(al.fx(s) for s in x["seeds"])
            mm = (f"{al.fx(x['seed_min'])} / {al.fx(x['seed_max'])} / {al.fx(x['seed_mean'])}"
                  if x["seed_min"] is not None else "n/a")
            L.append(f"| {x['definition']} | {al.fx(x['coverage'])} | {sv} | {mm} | "
                     f"{al.fbs(x['coverage_minus_seed_mean'])} | {x['position']} | "
                     f"{x['wording'] if worded else '(no wording fixed: printed side by side)'} |")
        cm = v["coverage_minus_main"]
        L += ["", f"Beside it, coverage minus the main checkpoint (as `coverage.json`): excess "
                  f"{al.fbs(cm['excess_over_perfect'])}, real success {al.fbs(cm['oracle_accept'])}, false rejection "
                  f"{al.fbs(cm['false_rejection'])}.", ""]
    L += ["## Checks", ""] + [f"- {c}" for c in res["checks"]] + [""]
    if res["notes"]:
        L += ["## Notes", ""] + [f"- {n}" for n in res["notes"]] + [""]
    L += [f"The sentence always says that {res['always']}.", ""]
    Path(path).write_text("\n".join(L))


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--tasks", default=str(al.TASKS_40))
    ap.add_argument("--engine-reference", default=str(al.ENGINE_REF))
    ap.add_argument("--coverage-json", default=str(ROOT / "results" / "analysis" / "coverage.json"))
    ap.add_argument("--replication-json", default=str(ROOT / "results" / "analysis" / "replication.json"))
    ap.add_argument("--out", default=str(ROOT / "results" / "analysis"))
    ap.add_argument("--n-boot", type=int, default=hs.N_BOOT)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    res = build(Path(a.root), Path(a.tasks), Path(a.engine_reference), Path(a.coverage_json),
                Path(a.replication_json) if a.replication_json else None, a.n_boot, a.seed)
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cmd = "PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/coverage_seeds.py" + \
        ("" if argv is None and len(sys.argv) == 1 else " " + " ".join(sys.argv[1:] if argv is None else argv))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "coverage_seeds.json").write_text(json.dumps(al._jsonable({"generated_utc": generated, "command": cmd,
                                                                       **res}), indent=1))
    write_md(out / "coverage_seeds.md", res, cmd, generated)
    for m, v in res["methods"].items():
        print(f"{m}: " + "; ".join(f"{q} {v['quantities'][q]['position']}" for q, _, _ in QUANTITIES))
    return res


if __name__ == "__main__":
    main()
