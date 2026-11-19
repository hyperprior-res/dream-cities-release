#!/usr/bin/env python
"""Threshold placement re-read .

    PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/threshold_reread.py

Random search at 1,000 evaluations on the main checkpoint (``os_50m_full``, 6,000,000 samples, the 40 cities, 193
instances): can the false acceptance, its perfect-emulator value, the excess and the real success be re-read exactly
at the thresholds a quarter and three quarters of the way from the best constant plan (c) to the engine-side search's
best (e), ``theta32_l25`` and ``theta32_l75`` of ``data/tasks_v2_H24.json`` (the audit's theta is ``theta32_l50``)?

Exact needs (i) the selection unchanged or recomputable from stored candidate scores, and (ii) per-sample outcomes of
the selected plans for the emulator (8 fresh samples), the oracle (32 seeds) and the perfect emulator (8 fresh engine
seeds and the same 32 oracle seeds). The records store (ii) as per-sample margins (``grader_margins_fresh``,
``oracle_margins_seeds``), and a margin is ``dc.tasks.margin``: the minimum over the task's clauses of each clause's
slack, the statistic's clause being (statistic - theta) / stat_sd. Where the statistic's clause is the only clause and
every trajectory is feasible (checked below on ``dc.tasks`` itself), a change of theta shifts every margin by the same
constant: random search's argmax over the two-sample mean margins is unchanged (checked against the stored candidate
scores: the selected plan's lead over the runner-up exceeds any floating-point error) and each sample passes at theta'
exactly when its margin at theta is at least (theta' - theta) / stat_sd. Where another clause enters the minimum, the
stored margin does not say which clause binds: neither the selection nor the verdicts at theta' can be recovered, and
nothing is computed for that family.

Statistics: the audit's estimators (``hpr_dream.stats``), cluster bootstrap over start-state families, 2,000 resamples,
seed 0, BCa (percentile where BCa is undefined; the exact one-sided bound where no unit is hacked), as the audit's
reference tables. Output: ``results/analysis/threshold_reread.{json,md}``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "code" / "scripts", ROOT / "code", ROOT / "hpr-dream"):
    sys.path.insert(0, str(p))

import numpy as np  # noqa: E402

import analyse_ladder as al  # noqa: E402  (Reader, read_audit conventions, nine_seed_means, the interval format)
import hpr_dream.stats as hs  # noqa: E402
from dc import audit as A  # noqa: E402
from dc import tasks as T  # noqa: E402

AUDIT = ROOT / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000" / "tasks_v2_H24"
TASKS = ROOT / "data" / "tasks_v2_H24.json"
REF_ROOT = ROOT / "results" / "audit" / "engine_reference"
METHOD, B = "random", 1000
LEVELS = (("l25", "theta32_l25", "a quarter of the way from c to e"), ("l50", "theta32_l50", "halfway (the audit's)"),
          ("l75", "theta32_l75", "three quarters of the way from c to e"))
GAP_TOL = 1e-9          # a selected plan's lead and a sample's distance to the shifted bar must exceed this
N_PROBE = 4000          # random trajectories for the margin-structure check


def margin_is_a_shift(task: str, rng: np.random.Generator) -> dict:
    """On ``dc.tasks`` itself: is every trajectory feasible and does ``margin`` at theta' equal the margin at theta
    minus (theta' - theta) / stat_sd on random trajectories? A counterexample shows that another clause enters."""
    H = 24
    s = rng.normal(size=(N_PROBE, H + 1, 20)) * 50 + 100
    s[..., T.SC_FUNDS] = rng.normal(size=(N_PROBE, H + 1)) * 5000 + rng.choice([-3000, 3000], size=(N_PROBE, 1))
    s[..., T.SC_TAX] = rng.integers(0, 21, size=(N_PROBE, H + 1))
    st = T.statistic(task, s)
    theta, sd = float(np.median(st)), float(np.std(st)) or 1.0
    d = 0.3 * sd
    m0, m1 = T.margin(task, s, theta, sd), T.margin(task, s, theta + d, sd)
    feas = T.feasible(task, s)
    shift_err = float(np.max(np.abs((m0 - m1) - d / sd)))
    return {"all_feasible": bool(feas.all()), "max_deviation_from_uniform_shift": shift_err,
            "uniform_shift": bool(feas.all() and shift_err < 1e-9), "n_probe": N_PROBE}


def _load(path: Path) -> list:
    return A.read_records(path)


def reread(audit: Path, tasks_path: Path, ref_root: Path, n_boot: int, seed: int) -> dict:
    rd = al.Reader(ROOT)
    tasks = al.load_tasks(tasks_path)
    inst = {i["start_id"] + "|" + i["task"] + "|H" + str(i["horizon"]): i
            for i in json.loads(Path(tasks_path).read_text())["instances"]}
    cfg = rd.json(audit / "config.json")
    if (cfg or {}).get("config", {}).get("tasks_sha256") != tasks["sha256"]:
        raise SystemExit(f"{audit}: another tasks file")
    refj = rd.json(audit / "reference.json") or {}
    ref_dir = Path(refj.get("reference") or (ref_root / tasks["stem"] / al.REF_NAME[METHOD]))
    if str(ref_dir).startswith("<repo>/"):
        ref_dir = ROOT / str(ref_dir)[len("<repo>/"):]
    elif not ref_dir.is_absolute():
        ref_dir = ROOT / ref_dir
    recs = {r["instance"]: r for r in rd.records(audit / "records.jsonl.gz")
            if r["method"] == METHOD and int(r["budget"]) == B}
    refs = {r["instance"]: r for r in rd.records(ref_dir / "records.jsonl.gz")
            if r["method"] == METHOD and int(r["budget"]) == B}
    out = {"audit": str(audit.relative_to(ROOT)), "reference": str(ref_dir), "tasks": str(Path(tasks_path).name),
           "search": METHOD, "budget": B, "n_instances": len(recs), "levels": {k: d for k, _, d in LEVELS},
           "interval": f"cluster bootstrap over start-state families, {n_boot} resamples, seed {seed}, BCa (percentile "
                       "where BCa is undefined; exact one-sided bound where no unit is hacked)", "families": {}}
    # the operative theta is theta32_l50 on every instance
    bad = [k for k in recs if inst[k]["theta"] != inst[k]["theta32_l50"]]
    out["theta_is_theta32_l50_on_every_instance"] = not bad
    m9 = al.nine_seed_means(ref_root, tasks, rd)
    zr = rd.npz(audit / "pools.npz")
    zf = rd.npz(ref_dir / "pools.npz")
    rng = np.random.default_rng(0)
    for f in al.FAMILIES:
        keys = sorted(k for k in recs if recs[k]["task"] == f)
        fam = {"n_instances": len(keys), "margin_structure": margin_is_a_shift(f, rng)}
        out["families"][f] = fam
        if not fam["margin_structure"]["uniform_shift"]:
            fam["status"] = ("not computed: the margin is the minimum over the statistic's clause and "
                             + {"grow": "the funds clause", "solvent": "the funds-floor clause",
                                "treasury": "the funds and tax-rate clauses",
                                "power": "the powered-share and plant-count clauses"}[f]
                             + "; a stored margin does not say which clause binds, so a change of theta does not shift "
                               "every candidate's score by one constant (the selection cannot be recomputed from the "
                               "stored candidate scores) and the per-sample verdicts at another theta cannot be read "
                               "from the stored per-sample margins")
            continue
        # (i) the selection: unchanged under a uniform shift; the selected plan's lead over the runner-up
        lead = {"emulator": [], "perfect_emulator": []}
        ties = {"emulator": [], "perfect_emulator": []}
        for who, z, R in (("emulator", zr, recs), ("perfect_emulator", zf, refs)):
            if m9.get("status") != "ok" or z is None:
                fam["status"] = f"not computed: candidate scores not recoverable ({m9.get('status')})"
                break
            for k in keys:
                st = k.replace("|", "__")
                sc = z[st + al.DEC_RES][:B, 0] + m9["m9"][k][:B]
                j = int(R[k]["best_index"])
                if abs(sc[j] - float(R[k]["grader_score"])) > GAP_TOL or int(np.argmax(sc)) != j:
                    fam["status"] = f"not computed: {who} {k}: stored candidate scores do not reproduce the selection"
                    break
                gap = float(sc[j] - np.max(np.delete(sc, j)))
                tied = [int(i) for i in np.flatnonzero(np.abs(sc - sc[j]) <= GAP_TOL) if i != j]
                lead[who].append(gap)
                if tied:
                    ties[who].append({"instance": k, "selected": j, "tied_with": tied, "lead": gap,
                                      "selected_is_first": bool(j < min(tied))})
            if "status" in fam:
                break
        if "status" in fam:
            continue
        # a tie on the score at theta is a tie at every theta (one shift for all candidates); the search's rule takes the
        # first of tied candidates (``hpr_dream.attack.random_shooting``: argmax), so the selection is unchanged in exact
        # arithmetic; a rerun in floating point could break such a tie the other way, and the other plan's per-sample
        # outcomes are not stored: each tied instance is listed and can move each count by at most one
        fam["selection"] = {who: {"min_lead_over_runner_up": float(min(v)), "n_instances": len(v),
                                  "ties_within_floating_point": ties[who],
                                  "unchanged": bool(all(t["selected_is_first"] for t in ties[who]))}
                            for who, v in lead.items()}
        if not all(v["unchanged"] for v in fam["selection"].values()):
            fam["status"] = "not computed: a tied selection is not the first of its tied candidates"
            continue
        # (ii) the verdicts at each level from the per-sample margins
        cl = [recs[k]["cluster"] for k in keys]
        fam["levels"] = {}
        min_gap = math.inf
        for lv, field, desc in LEVELS:
            ga, oa, gr, orr = [], [], [], []
            for k in keys:
                i = inst[k]
                delta = (float(i[field]) - float(i["theta"])) / max(float(i["stat_sd"]), 1e-9)
                for r, gl, ol in ((recs[k], ga, oa), (refs[k], gr, orr)):
                    g8 = np.asarray(r["grader_margins_fresh"], float)
                    o32 = np.asarray(r["oracle_margins_seeds"], float)
                    if g8.size != 8 or o32.size != T.ORACLE_N:
                        raise SystemExit(f"{k}: per-sample margins of another size")
                    if lv != "l50":
                        min_gap = min(min_gap, float(np.min(np.abs(np.r_[g8, o32] - delta))))
                    gl.append(np.mean(g8 >= delta) >= A.ACCEPT_P)
                    ol.append(2 * int(np.sum(o32 >= delta)) >= o32.size)
            ga, oa, gr, orr = map(np.array, (ga, oa, gr, orr))
            kw = dict(n_boot=n_boot, seed=seed, bca=True)
            v = {"theta_field": field, "description": desc, "n": len(keys), "n_clusters": len(set(cl)),
                 "false_acceptance": hs.hackability(ga, oa, cl, **kw),
                 "perfect_false_acceptance": hs.hackability(gr, orr, cl, **kw),
                 "excess": hs.excess(ga & ~oa, gr & ~orr, cl, **kw),
                 "real_success": hs.conditional_mean(oa, None, cl, **kw),
                 "perfect_real_success": hs.conditional_mean(orr, None, cl, **kw),
                 "emulator_accepts": hs.conditional_mean(ga, None, cl, **kw),
                 "counts": {"hacked": int((ga & ~oa).sum()), "perfect_hacked": int((gr & ~orr).sum()),
                            "oracle_accepts": int(oa.sum()), "perfect_oracle_accepts": int(orr.sum()),
                            "emulator_accepts": int(ga.sum())}}
            if lv == "l50":   # the audit's own threshold: the re-read must reproduce the stored verdicts
                v["reproduces_stored_verdicts"] = bool(
                    all(ga == np.array([recs[k]["grader_p"] >= A.ACCEPT_P for k in keys]))
                    and all(oa == np.array([bool(recs[k]["oracle_accept"]) for k in keys]))
                    and all(gr == np.array([refs[k]["grader_p"] >= A.ACCEPT_P for k in keys]))
                    and all(orr == np.array([bool(refs[k]["oracle_accept"]) for k in keys])))
            fam["levels"][lv] = v
        fam["min_distance_of_a_sample_margin_to_the_shifted_bar"] = min_gap
        fam["status"] = ("ok" if fam["levels"]["l50"]["reproduces_stored_verdicts"] and min_gap > GAP_TOL else
                         "not computed: the re-read at theta does not reproduce the stored verdicts, or a sample sits "
                         "within floating-point error of the shifted bar")
        if fam["status"] != "ok":
            fam.pop("levels")
    return out


def _jsonable(o):
    return al._jsonable(o)


def write_md(path: Path, res: dict, cmd: str, generated: str):
    L = ["# Threshold placement re-read: random search at 1,000 on the main checkpoint ", "",
         f"Generated {generated} by `{cmd}`. Records: `{res['audit']}`; perfect emulator: `{res['reference']}`; "
         f"{res['n_instances']} instances. Thresholds: theta32_l25 (a quarter of the way from the best constant plan c to "
         "the engine-side search's best e), theta32_l50 (halfway, the audit's) and theta32_l75, from the tasks file. "
         f"Intervals: {res['interval']}. The audit's theta equals theta32_l50 on every instance: "
         f"{al._yn(res['theta_is_theta32_l50_on_every_instance'])}.", "",
         "Exact re-read needs the selection unchanged and the selected plans' per-sample outcomes at the new threshold. "
         "Both hold only where the margin is the statistic's clause alone and every trajectory is feasible (a change of "
         "theta then shifts every margin by one constant); this is checked on `dc.tasks` itself for each family.", "",
         "| family | instances | margin a uniform shift of theta | status |", "|---|---|---|---|"]
    for f, v in res["families"].items():
        ms = v["margin_structure"]
        L.append(f"| {f} | {v['n_instances']} | {al._yn(ms['uniform_shift'])} (all feasible: {al._yn(ms['all_feasible'])}; "
                 f"largest deviation {ms['max_deviation_from_uniform_shift']:.3g}) | {v['status']} |")
    L.append("")
    for f, v in res["families"].items():
        if v["status"] != "ok":
            continue
        sel = v["selection"]
        L += [f"## {f}", "",
              f"Selection unchanged: the selected plan's smallest lead over the runner-up among the {B} candidate scores "
              f"(stored, recovered as the analysis plan does): emulator {sel['emulator']['min_lead_over_runner_up']:.3g}, "
              f"perfect emulator {sel['perfect_emulator']['min_lead_over_runner_up']:.3g}. "
              + "".join(f"Tied on the {w.replace('_', ' ')}'s score (within {GAP_TOL:g}): " + "; ".join(
                  f"{t['instance']} (selected candidate {t['selected']}, tied with {t['tied_with']})" for t in sel[w][
                      'ties_within_floating_point']) + ". A tie at theta is a tie at every theta and the search takes the "
                  "first tied candidate, so the selection is unchanged in exact arithmetic; a rerun in floating point "
                  "could break the tie the other way, the other plan's per-sample outcomes are not stored, and the "
                  "instance can move each count by at most one. " for w in sel if sel[w]["ties_within_floating_point"])
              + f"Smallest distance of a "
              f"per-sample margin to a shifted bar: {v['min_distance_of_a_sample_margin_to_the_shifted_bar']:.3g}. At "
              f"theta32_l50 the re-read reproduces every stored verdict: "
              f"{al._yn(v['levels']['l50']['reproduces_stored_verdicts'])}.", "",
              "| threshold | n | false acceptance | perfect emulator | excess | real success | perfect emulator's real "
              "success | emulator accepts | hacked / perfect hacked / oracle accepts / perfect oracle accepts |",
              "|---|---|---|---|---|---|---|---|---|"]
        for lv, x in v["levels"].items():
            c = x["counts"]
            L.append(f"| {x['theta_field']} ({x['description']}) | {x['n']} | {al.fb(x['false_acceptance'])} | "
                     f"{al.fb(x['perfect_false_acceptance'])} | {al.fbs(x['excess'])} | {al.fb(x['real_success'])} | "
                     f"{al.fb(x['perfect_real_success'])} | {al.fb(x['emulator_accepts'])} | {c['hacked']} / "
                     f"{c['perfect_hacked']} / {c['oracle_accepts']} / {c['perfect_oracle_accepts']} |")
        L.append("")
    Path(path).write_text("\n".join(L))


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--audit", default=str(AUDIT))
    ap.add_argument("--tasks", default=str(TASKS))
    ap.add_argument("--engine-reference", default=str(REF_ROOT))
    ap.add_argument("--out", default=str(ROOT / "results" / "analysis"))
    ap.add_argument("--n-boot", type=int, default=hs.N_BOOT)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    res = reread(Path(a.audit), Path(a.tasks), Path(a.engine_reference), a.n_boot, a.seed)
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cmd = "PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/threshold_reread.py" + \
        ("" if argv is None and len(sys.argv) == 1 else " " + " ".join(sys.argv[1:] if argv is None else argv))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "threshold_reread.json").write_text(json.dumps(_jsonable({"generated_utc": generated, "command": cmd,
                                                                      **res}), indent=1))
    write_md(out / "threshold_reread.md", res, cmd, generated)
    for f, v in res["families"].items():
        print(f"{f}: {v['status'][:100]}")
    return res


if __name__ == "__main__":
    main()
