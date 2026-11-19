"""The pressure axis of the pool-seeded search on one checkpoint (paper/THREAD.md, section 3).

For the instances of the 10,000-evaluation run (100, twenty per task family, in the first run) this puts the
search at 10, 100, 1,000 and 10,000 evaluations inside the emulator beside the same search inside a perfect
emulator (the engine judging on fresh seeds), on the same instances, and tests the two trends the section states:

* false acceptance (the judge accepts the selected plan, the majority oracle rejects it), its excess over the
  perfect emulator, and the change of that excess between budgets;
* real success (the majority oracle accepts the selected plan), its shortfall against the perfect emulator, and
  the change of that shortfall between budgets.

Top-level fields (``rows``, ``contrasts``, ``families``): percentile intervals, as since the first version.
Fields added later , none of the above changed:

* ``bca``: the same instances, both searches with one interval method (BCa cluster bootstrap over held-out cities,
  ``hpr_dream.stats.conditional_mean``, the same resamples as the percentile fields): the pool-seeded search at
  10 to 10,000 and random search at every budget it has (1 to 1,000), each beside its perfect emulator; the three
  contrasts at 10,000 (against 10, 100, 1,000) of the excess false acceptance, of the real-success shortfall and of
  each arm's real success, each with a per-comparison 95 per cent interval and one corrected for the three
  contrasts (Bonferroni, 98.33 per cent); the 10,000-minus-1,000 contrasts leaving out each task family in turn;
* ``decision_79_point_7``: whether the corrected 10,000-minus-1,000 interval of the excess excludes zero, applied
  only when every instance of the 193-instance set is on the axis;
* ``well_posed``: every quantity above on the well-posed instances among those on the axis (the records'
  ``in_band`` flag, the subset the 193-instance tables report as well posed), its own city families as clusters;
* ``coverage``: which instances the 10,000-evaluation directories hold, on each side;
* ``zero_event_bounds``: every rate in the file that is 0 (or 1), and which interval or bound is given for it.

Inputs (records.jsonl.gz of each run; nothing is recomputed):
  emulator, B = 1..1,000:   results/audit/ladder/<run>/<checkpoint>/tasks_v2_H24_cem_seeded   (pool-seeded)
                            results/audit/ladder/<run>/<checkpoint>/tasks_v2_H24              (random)
  emulator, B = 10,000:     --emulator-high DIR [DIR ...]  (default .../tasks_v2_H24_cem_seeded_1e4)
  perfect,  B = 1..1,000:   results/audit/engine_reference/tasks_v2_H24/cem_seeded_B_economy, .../B_economy
  perfect,  B = 10,000:     --perfect-high DIR [DIR ...]   (default .../cem_seeded_1e4_i100)
The axis is on the instances that both sides hold at 10,000; an (instance, budget) found twice (in one directory
or in two) stops the script.
Statistics: means over instances; 95 per cent intervals from a cluster bootstrap over city families
(``hpr_dream.stats.cluster_draws``, 2,000 resamples, seed 0), every quantity recomputed on each resample, so
differences and contrasts are paired by instance.

Usage: PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/pressure_axis.py [--checkpoint os_50m_full/samples_006000000]
       [--emulator-high DIR ...] [--perfect-high DIR ...] [--out DIR]
Writes pressure_axis.md and pressure_axis.json (default results/analysis/).
"""
from __future__ import annotations

import argparse
import gzip
import json
import time
from pathlib import Path

import numpy as np

from hpr_dream import stats as hs

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = ("grow", "solvent", "treasury", "recover", "power")
METHOD = "cem_seeded"
NAMES = ("false_acceptance", "real_success", "judge_accepts")
CEM_BUDGETS = [10, 100, 1000, 10000]
RANDOM_BUDGETS = [1, 10, 100, 1000]
N_CONTRASTS = 3                                   # the three contrasts at 10,000 (against 10, 100 and 1,000)
LEVEL = 0.95
LEVEL_CORRECTED = 1 - (1 - LEVEL) / N_CONTRASTS   # Bonferroni for three comparisons: 0.98333...
FULL_SET = 193                                    # the main checkpoint's 40-city instances 
D79_RISES = "rises at 10,000"
D79_NO_RISE = "no rise in the excess false acceptance is established at any budget"


def load(run: Path, method: str = METHOD) -> dict:
    """(instance, budget) -> (false acceptance, real success, judge accepts, cluster, task, in_band) for the method.
    An (instance, budget) that occurs twice for the method stops the script."""
    out = {}
    with gzip.open(Path(run) / "records.jsonl.gz", "rt") as fh:
        for line in fh:
            r = json.loads(line)
            if r["method"] != method:
                continue
            acc = r["grader_p_fresh"] >= 0.5
            orc = bool(r["oracle_accept"])
            key = (r["instance"], int(r["budget"]))
            if key in out:
                raise SystemExit(f"{run}: {method} record {key} occurs twice")
            out[key] = (acc and not orc, orc, acc, r["cluster"], r["task"], bool(r["in_band"]))
    return out


def load_many(runs, method: str = METHOD) -> dict:
    """``load`` over several directories (shards of one run); an (instance, budget) in two of them stops the script."""
    out, where = {}, {}
    for run in runs:
        for k, v in load(run, method).items():
            if k in out:
                raise SystemExit(f"{k} is in two directories: {where[k]} and {run}")
            out[k], where[k] = v, run
    return out


def axis(X: dict, cluster: np.ndarray, task: np.ndarray, budgets: list, n_boot: int, seed: int) -> dict:
    """Rows, contrasts and per-family means on the units of ``X`` (X[side][stat]: budgets x units 0/1 arrays);
    percentile intervals over ``n_boot`` resamples of the units' own clusters (``hs.cluster_draws``, ``seed``)."""
    n = len(cluster)
    codes, C = hs._encode(cluster)
    members = [np.flatnonzero(codes == c) for c in range(C)]
    draws = hs.cluster_draws(C, n_boot, seed)
    resamples = [np.concatenate([members[c] for c in row]) for row in draws]

    def est(fn):
        """fn(index array) -> float; value on the units and the percentile interval over cluster resamples."""
        v = fn(np.arange(n))
        bs = [fn(r) for r in resamples if r.size]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return {"value": float(v), "lo": float(lo), "hi": float(hi)}

    m = lambda side, nm, j: (lambda idx: float(X[side][nm][j][idx].mean()))
    diff = lambda nm, j: (lambda idx: float(X["emulator"][nm][j][idx].mean() - X["perfect"][nm][j][idx].mean()))
    res = {"n_clusters": int(C), "rows": [], "contrasts": [], "families": []}
    for j, B in enumerate(budgets):
        row = {"budget": B}
        for nm in NAMES:
            row[nm] = {"emulator": est(m("emulator", nm, j)), "perfect": est(m("perfect", nm, j)),
                       "difference": est(diff(nm, j))}
        res["rows"].append(row)
    jb = {B: j for j, B in enumerate(budgets)}

    def contrast(label, fn):
        res["contrasts"].append({"contrast": label, **est(fn)})

    for B1, B0 in ((10000, 1000), (10000, 100), (10000, 10), (1000, 10)):
        j1, j0 = jb[B1], jb[B0]
        contrast(f"excess false acceptance at {B1:,} minus at {B0:,}",
                 lambda idx, j1=j1, j0=j0: diff("false_acceptance", j1)(idx) - diff("false_acceptance", j0)(idx))
        contrast(f"real-success shortfall (emulator minus perfect) at {B1:,} minus at {B0:,}",
                 lambda idx, j1=j1, j0=j0: diff("real_success", j1)(idx) - diff("real_success", j0)(idx))
        for side in ("emulator", "perfect"):
            contrast(f"real success, {side}: at {B1:,} minus at {B0:,}",
                     lambda idx, j1=j1, j0=j0, side=side: m(side, "real_success", j1)(idx) - m(side, "real_success", j0)(idx))
            contrast(f"false acceptance, {side}: at {B1:,} minus at {B0:,}",
                     lambda idx, j1=j1, j0=j0, side=side: m(side, "false_acceptance", j1)(idx) - m(side, "false_acceptance", j0)(idx))
    for t in FAMILIES:
        sel = task == t
        for j, B in enumerate(budgets):
            fam = {"family": t, "budget": B, "n": int(sel.sum())}
            for nm in NAMES:
                fam[nm] = ({"emulator": float(X["emulator"][nm][j][sel].mean()),
                            "perfect": float(X["perfect"][nm][j][sel].mean())} if sel.any() else
                           {"emulator": None, "perfect": None})
            res["families"].append(fam)
    return res


# ---------------------------------------------------------------------------------------------------------------
# BCa (one interval method for both searches; R1 M3) and the corrected contrasts 
# ---------------------------------------------------------------------------------------------------------------
def bca_est(v, cluster, n_boot: int, seed: int, level: float = LEVEL, rate: bool = False) -> dict:
    """Mean of the per-instance values ``v`` with the cluster bootstrap's percentile and BCa intervals at ``level``
    (``hs.conditional_mean``: cluster weights from ``hs.cluster_draws(C, n_boot, seed)``, jackknife over clusters).
    A rate with no event (or with every unit an event) gets the exact one-sided binomial bound on clusters in place
    of the BCa interval, as ``hs.hackability`` does for a zero count; ``interval`` says which was given."""
    v = np.asarray(v, dtype=np.float64)
    e = hs.conditional_mean(v, None, cluster, n_boot=n_boot, seed=seed, level=level, bca=True)
    d = {"value": e.value, "level": level, "pct_lo": e.lo, "pct_hi": e.hi, "bca_lo": e.bca_lo, "bca_hi": e.bca_hi,
         "n_units": e.n_units, "n_clusters": e.n_clusters, "interval": f"two-sided {level:.2%} BCa"}
    if rate and not v.any():
        d.update(bca_lo=0.0, bca_hi=hs.zero_count_upper_bound(e.n_clusters, level),
                 interval=f"no event: [0, one-sided {level:.2%} exact binomial upper bound on {e.n_clusters} clusters]")
    elif rate and v.all():
        d.update(bca_lo=1.0 - hs.zero_count_upper_bound(e.n_clusters, level), bca_hi=1.0,
                 interval=f"every unit an event: [one-sided {level:.2%} exact binomial lower bound on "
                          f"{e.n_clusters} clusters, 1]")
    elif not (np.isfinite(e.bca_lo) and np.isfinite(e.bca_hi)):
        d["interval"] = "BCa undefined (every resample on one side of the estimate, or no spread): percentile only"
    for k in ("pct_lo", "pct_hi", "bca_lo", "bca_hi"):
        d[k] = float(d[k]) if np.isfinite(d[k]) else None
    return d


def excludes_zero(e: dict, kind: str = "bca") -> bool | None:
    lo, hi = e[f"{kind}_lo"], e[f"{kind}_hi"]
    if lo is None or hi is None:
        return None
    return bool(lo > 0 or hi < 0)


QUANTITIES = {   # name -> per-instance value at budget index j (V[side][stat][j])
    "excess false acceptance": lambda V, j: V["emulator"]["false_acceptance"][j] - V["perfect"]["false_acceptance"][j],
    "real-success shortfall (emulator minus perfect)":
        lambda V, j: V["emulator"]["real_success"][j] - V["perfect"]["real_success"][j],
    "real success, emulator": lambda V, j: V["emulator"]["real_success"][j],
    "real success, perfect": lambda V, j: V["perfect"]["real_success"][j],
}


def bca_block(Xc: dict, Xr: dict, cluster: np.ndarray, task: np.ndarray, n_boot: int, seed: int) -> dict:
    """Both searches on the same units with BCa intervals; the three contrasts at 10,000 at 95 per cent and corrected
    for three comparisons; the 10,000-minus-1,000 contrasts leaving out each task family in turn."""
    E = lambda v, lev=LEVEL, rate=False, cl=cluster: bca_est(v, cl, n_boot, seed, lev, rate)  # noqa: E731

    def rows(X, budgets):
        out = []
        for j, B in enumerate(budgets):
            row = {"budget": B}
            for nm in NAMES:
                row[nm] = {"emulator": E(X["emulator"][nm][j], rate=True), "perfect": E(X["perfect"][nm][j], rate=True),
                           "difference": E(X["emulator"][nm][j] - X["perfect"][nm][j])}
            out.append(row)
        return out

    jb = {B: j for j, B in enumerate(CEM_BUDGETS)}
    con = []
    for q, fn in QUANTITIES.items():
        for B0 in (10, 100, 1000):
            v = fn(Xc, jb[10000]) - fn(Xc, jb[B0])
            con.append({"quantity": q, "contrast": f"{q}: at 10,000 minus at {B0:,}", "budgets": [10000, B0],
                        "per_comparison": E(v), "corrected": E(v, LEVEL_CORRECTED)})
    lofo = []
    for t in FAMILIES:
        keep = task != t
        if not keep.any() or keep.all():
            continue
        for q, fn in QUANTITIES.items():
            v = (fn(Xc, jb[10000]) - fn(Xc, jb[1000]))[keep]
            lofo.append({"left_out": t, "quantity": q, "contrast": f"{q}: at 10,000 minus at 1,000, without {t}",
                         "n_instances": int(keep.sum()),
                         "per_comparison": E(v, cl=cluster[keep]), "corrected": E(v, LEVEL_CORRECTED, cl=cluster[keep])})
    return {"interval": f"BCa cluster bootstrap over held-out cities (city families), {n_boot} resamples, seed {seed}, "
                        "hpr_dream.stats.conditional_mean; percentile bounds of the same resamples beside it (pct_*)",
            "levels": {"per_comparison": LEVEL, "corrected": LEVEL_CORRECTED,
                       "correction": f"Bonferroni over the {N_CONTRASTS} contrasts at 10,000 (against 10, 100, 1,000)"},
            "pool_seeded": {"method": METHOD, "budgets": CEM_BUDGETS, "rows": rows(Xc, CEM_BUDGETS)},
            "random": {"method": "random", "budgets": RANDOM_BUDGETS, "rows": rows(Xr, RANDOM_BUDGETS)},
            "contrasts_at_10000": con, "leave_one_family_out": lofo}


def zero_events(res: dict) -> list:
    """Every rate in ``res`` whose value is 0 or 1, with the interval or bound the file gives for it (R1 m16)."""
    out = []

    def visit(path, side, e):
        if isinstance(e, dict) and "value" in e and e["value"] in (0.0, 1.0):
            if "interval" in e:
                kind = e["interval"]
            else:
                kind = ("two-sided 95 % percentile interval: every resample gives the same value, so the interval "
                        f"is degenerate [{e['value']:.0f}, {e['value']:.0f}]; it is not a bound")
            out.append({"field": f"{path}.{side}", "value": e["value"], "interval_given": kind})
        elif isinstance(e, (int, float)) and e in (0.0, 1.0) and not isinstance(e, bool):
            out.append({"field": f"{path}.{side}", "value": float(e), "interval_given": "none (family rows carry no interval)"})

    def scan(x, path=""):
        if isinstance(x, dict):
            for nm in NAMES:
                if nm in x and isinstance(x[nm], dict):
                    for side in ("emulator", "perfect"):
                        if side in x[nm]:
                            visit(f"{path}.{nm}" if path else nm, side, x[nm][side])
            for k, v in x.items():
                if k not in NAMES:
                    scan(v, f"{path}.{k}" if path else k)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                lab = i
                if isinstance(v, dict) and "family" in v:
                    lab = f"family={v['family']},budget={v['budget']}"
                elif isinstance(v, dict) and "budget" in v:
                    lab = f"budget={v['budget']}"
                scan(v, f"{path}[{lab}]")

    scan(res)
    return out


def tables(res: dict, fam_note: str) -> list:
    """Markdown tables of one ``axis`` result."""
    f = lambda e: f"{e['value']:.3f} [{e['lo']:.3f}, {e['hi']:.3f}]"
    g = lambda e: f"{e['value']:+.3f} [{e['lo']:+.3f}, {e['hi']:+.3f}]"
    h = lambda v: "-" if v is None else f"{v:.2f}"
    L = ["## False acceptance (the judge accepts the selected plan, the 32-seed majority rejects it)", "",
         "| evaluations | emulator | perfect emulator | excess |", "|---|---|---|---|"]
    for row in res["rows"]:
        e = row["false_acceptance"]
        L.append(f"| {row['budget']:,} | {f(e['emulator'])} | {f(e['perfect'])} | {g(e['difference'])} |")
    L += ["", "## Real success (the 32-seed majority accepts the selected plan)", "",
          "| evaluations | emulator | perfect emulator | shortfall |", "|---|---|---|---|"]
    for row in res["rows"]:
        e = row["real_success"]
        L.append(f"| {row['budget']:,} | {f(e['emulator'])} | {f(e['perfect'])} | {g(e['difference'])} |")
    L += ["", "## The judge's own acceptance of the selected plan", "",
          "| evaluations | emulator | perfect emulator | difference |", "|---|---|---|---|"]
    for row in res["rows"]:
        e = row["judge_accepts"]
        L.append(f"| {row['budget']:,} | {f(e['emulator'])} | {f(e['perfect'])} | {g(e['difference'])} |")
    L += ["", "## Trends (paired contrasts between budgets)", "", "| contrast | estimate [95 %] | excludes 0 |", "|---|---|---|"]
    for c in res["contrasts"]:
        L.append(f"| {c['contrast']} | {g(c)} | {'yes' if c['lo'] > 0 or c['hi'] < 0 else 'no'} |")
    L += ["", f"## By task family (emulator / perfect emulator; {fam_note}, no intervals)", "",
          "| family | evaluations | false acceptance | real success | judge accepts |", "|---|---|---|---|---|"]
    for r in res["families"]:
        L.append(f"| {r['family']} | {r['budget']:,} | {h(r['false_acceptance']['emulator'])} / {h(r['false_acceptance']['perfect'])} | "
                 f"{h(r['real_success']['emulator'])} / {h(r['real_success']['perfect'])} | "
                 f"{h(r['judge_accepts']['emulator'])} / {h(r['judge_accepts']['perfect'])} |")
    return L


def bca_tables(b: dict, head: str = "##") -> list:
    def iv(e, signed=False):
        s = "+" if signed else ""
        v = f"{e['value']:{s}.3f}"
        if e["bca_lo"] is None:
            return f"{v} [pct {e['pct_lo']:{s}.3f}, {e['pct_hi']:{s}.3f}]"
        return v + f" [{e['bca_lo']:{s}.3f}, {e['bca_hi']:{s}.3f}]" + ("*" if e["interval"].startswith(("no event", "every")) else "")
    L = [f"{head} Both searches on these instances, one interval method (BCa)", "",
         f"Intervals: {b['interval']}. * = no event (or every unit an event): the exact one-sided binomial bound on "
         "clusters is given (`interval` in the json).", "",
         "| search | evaluations | false acceptance: emulator | perfect | excess | real success: emulator | perfect | shortfall |",
         "|---|---|---|---|---|---|---|---|"]
    for key, lab in (("random", "random"), ("pool_seeded", "pool-seeded")):
        for r in b[key]["rows"]:
            fa, rs = r["false_acceptance"], r["real_success"]
            L.append(f"| {lab} | {r['budget']:,} | {iv(fa['emulator'])} | {iv(fa['perfect'])} | {iv(fa['difference'], True)} | "
                     f"{iv(rs['emulator'])} | {iv(rs['perfect'])} | {iv(rs['difference'], True)} |")
    L += ["", f"{head} Contrasts at 10,000 (pool-seeded search), per comparison and corrected for three", "",
          "| contrast | BCa 95 % | excludes 0 | BCa 98.33 % | excludes 0 |", "|---|---|---|---|---|"]
    yn = lambda x: "-" if x is None else ("yes" if x else "no")  # noqa: E731
    for c in b["contrasts_at_10000"]:
        L.append(f"| {c['contrast']} | {iv(c['per_comparison'], True)} | {yn(excludes_zero(c['per_comparison']))} | "
                 f"{iv(c['corrected'], True)} | {yn(excludes_zero(c['corrected']))} |")
    L += ["", f"{head} 10,000 minus 1,000, leaving out one task family", "",
          "| contrast | n | BCa 95 % | excludes 0 | BCa 98.33 % | excludes 0 |", "|---|---|---|---|---|---|"]
    for c in b["leave_one_family_out"]:
        L.append(f"| {c['contrast']} | {c['n_instances']} | {iv(c['per_comparison'], True)} | "
                 f"{yn(excludes_zero(c['per_comparison']))} | {iv(c['corrected'], True)} | {yn(excludes_zero(c['corrected']))} |")
    return L


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checkpoint", default="os_50m_full/samples_006000000")
    ap.add_argument("--emulator-high", nargs="+", default=None,
                    help="directories holding the emulator's 10,000-evaluation records (default: the first run)")
    ap.add_argument("--perfect-high", nargs="+", default=None,
                    help="directories holding the perfect emulator's 10,000-evaluation records (default: the first run)")
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=str(ROOT / "results/analysis"))
    a = ap.parse_args(argv)
    lad = ROOT / "results/audit/ladder" / a.checkpoint
    ref = ROOT / "results/audit/engine_reference/tasks_v2_H24"
    high = {"emulator": [Path(p) for p in (a.emulator_high or [lad / "tasks_v2_H24_cem_seeded_1e4"])],
            "perfect": [Path(p) for p in (a.perfect_high or [ref / "cem_seeded_1e4_i100"])]}
    low = {"emulator": lad / "tasks_v2_H24_cem_seeded", "perfect": ref / "cem_seeded_B_economy"}
    rnd = {"emulator": lad / "tasks_v2_H24", "perfect": ref / "B_economy"}
    D = {side: {"low": load(low[side]), "high": load_many(high[side])} for side in low}
    R = {side: load(rnd[side], "random") for side in rnd}
    src = lambda B: "high" if B == 10000 else "low"
    hi_inst = {side: {i for i, b in D[side]["high"] if b == 10000} for side in D}
    inst = sorted(hi_inst["emulator"] & hi_inst["perfect"])
    full_set = sorted({i for i, b in D["emulator"]["low"] if b == 1000})
    for side in D:
        for B in CEM_BUDGETS:
            missing = [i for i in inst if (i, B) not in D[side][src(B)]]
            if missing:
                raise SystemExit(f"{side} at B={B}: {len(missing)} of {len(inst)} instances missing, e.g. {missing[0]}")
        for B in RANDOM_BUDGETS:
            missing = [i for i in inst if (i, B) not in R[side]]
            if missing:
                raise SystemExit(f"random, {side} at B={B}: {len(missing)} of {len(inst)} instances missing, e.g. {missing[0]}")
    cluster = np.array([D["emulator"]["high"][(i, 10000)][3] for i in inst])
    task = np.array([D["emulator"]["high"][(i, 10000)][4] for i in inst])
    in_band = np.array([D["emulator"]["high"][(i, 10000)][5] for i in inst])
    for side in D:                      # the instance's cluster, task and flag come from the tasks file: all must agree
        for B in CEM_BUDGETS:
            if any(D[side][src(B)][(i, B)][3:] != (c, t, w) for i, c, t, w in zip(inst, cluster, task, in_band)):
                raise SystemExit(f"{side} at B={B}: cluster, task or in_band differs from the emulator's 10,000 run")
        for B in RANDOM_BUDGETS:
            if any(R[side][(i, B)][3:] != (c, t, w) for i, c, t, w in zip(inst, cluster, task, in_band)):
                raise SystemExit(f"random, {side} at B={B}: cluster, task or in_band differs from the emulator's 10,000 run")
    # X[side][stat][budget index] = per-instance 0/1 vector
    X = {side: {nm: np.array([[float(D[side][src(B)][(i, B)][k]) for i in inst] for B in CEM_BUDGETS])
                for k, nm in enumerate(NAMES)} for side in D}
    XR = {side: {nm: np.array([[float(R[side][(i, B)][k]) for i in inst] for B in RANDOM_BUDGETS])
                 for k, nm in enumerate(NAMES)} for side in R}
    full = axis(X, cluster, task, CEM_BUDGETS, a.n_boot, a.seed)
    C = full["n_clusters"]
    rel = lambda p: str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)  # noqa: E731
    hin = lambda side: rel(high[side][0]) if len(high[side]) == 1 else [rel(p) for p in high[side]]  # noqa: E731
    res = {"checkpoint": a.checkpoint, "method": METHOD, "n_instances": len(inst), "n_clusters": int(C),
           "per_family": {t: int((task == t).sum()) for t in FAMILIES}, "budgets": CEM_BUDGETS,
           "bootstrap": f"{a.n_boot} cluster resamples, seed {a.seed}, percentile, hpr_dream.stats.cluster_draws",
           "inputs": {s: {"low": rel(low[s]), "high": hin(s)} for s in low},
           "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "rows": full["rows"], "contrasts": full["contrasts"], "families": full["families"]}
    res["inputs_random"] = {s: rel(p) for s, p in rnd.items()}
    res["coverage"] = {
        "full_set": f"the {len(full_set)} instances of the emulator's 1 to 1,000-evaluation run "
                    f"({rel(low['emulator'])})",
        "n_full_set": len(full_set),
        "n_emulator_10000": len(hi_inst["emulator"]), "n_perfect_10000": len(hi_inst["perfect"]),
        "n_on_axis": len(inst), "all_of_full_set": inst == full_set,
        "emulator_only": sorted(hi_inst["emulator"] - hi_inst["perfect"]),
        "perfect_only": sorted(hi_inst["perfect"] - hi_inst["emulator"]),
        "outside_full_set": sorted(set(inst) - set(full_set)),
        "duplicates": "none: an (instance, budget) twice in one directory or in two stops the script",
        "directories_10000": {s: [rel(p) for p in high[s]] for s in high}}
    res["bca"] = bca_block(X, XR, cluster, task, a.n_boot, a.seed)
    rule = {"rule": "the analysis plan (7): the paper says the excess false acceptance 'rises at 10,000' only if the "
                    "10,000-minus-1,000 contrast on all 193 instances excludes zero after correction for the three "
                    "contrasts (98.33 per cent intervals); otherwise 'no rise in the excess false acceptance is "
                    "established at any budget'. Interval used: BCa at 98.33 per cent (bca.contrasts_at_10000).",
            "n_on_axis": len(inst), "n_required": FULL_SET}
    c = next(x for x in res["bca"]["contrasts_at_10000"] if x["contrast"] == "excess false acceptance: at 10,000 minus at 1,000")
    if len(full_set) == FULL_SET and inst == full_set:
        ex = excludes_zero(c["corrected"])
        rule.update(status="applied", contrast=c["corrected"], excludes_zero=ex,
                    wording=None if ex is None else (D79_RISES if ex and c["corrected"]["value"] > 0 else D79_NO_RISE))
    else:
        rule.update(status=f"not applied: {len(inst)} of {FULL_SET} instances on the axis", excludes_zero=None,
                    wording=None)
    res["decision_79_point_7"] = rule
    w = np.flatnonzero(in_band)
    Xw = {side: {nm: v[:, w] for nm, v in d.items()} for side, d in X.items()}
    XRw = {side: {nm: v[:, w] for nm, v in d.items()} for side, d in XR.items()}
    wp = axis(Xw, cluster[w], task[w], CEM_BUDGETS, a.n_boot, a.seed)
    res["well_posed"] = {
        "definition": "the records' in_band flag (tasks file: well_posed32, amendment 3), the subset the 193-instance "
                      "tables report as well posed (run_audit.py compare_reference, subset in_band)",
        "n_instances": int(w.size), "n_clusters": wp["n_clusters"],
        "per_family": {t: int((task[w] == t).sum()) for t in FAMILIES},
        "bootstrap": f"{a.n_boot} resamples of the subset's own city families, seed {a.seed}, percentile, "
                     "hpr_dream.stats.cluster_draws (the procedure of the top-level fields, run on the subset)",
        "instances_not_well_posed": [i for i, b in zip(inst, in_band) if not b],
        "rows": wp["rows"], "contrasts": wp["contrasts"], "families": wp["families"],
        "bca": bca_block(Xw, XRw, cluster[w], task[w], a.n_boot, a.seed)}
    res["zero_event_bounds"] = {
        "note": "R1 m16: every rate in this file whose value is 0 or 1 and the interval given for it. Percentile "
                "fields (lo/hi) are two-sided 95 per cent percentile intervals and are degenerate at 0 or 1; the BCa "
                "fields (bca_lo/bca_hi) give the exact one-sided binomial bound on clusters there (field interval).",
        "fields": []}
    res["zero_event_bounds"]["fields"] = zero_events({k: v for k, v in res.items() if k != "zero_event_bounds"})
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "pressure_axis.json").write_text(json.dumps(res, indent=1))
    per_family = ", ".join(f"{t} {res['per_family'][t]}" for t in FAMILIES)
    pf = set(res["per_family"].values())
    L = [f"# The pressure axis: the pool-seeded search on `{a.checkpoint}`, 10 to 10,000 evaluations", "",
         f"Generated {res['generated']} by `code/scripts/pressure_axis.py`. {len(inst)} instances "
         f"({per_family}) in {C} city families: the instances of the "
         "10,000-evaluation run, at every budget. The perfect emulator is the engine judging on fresh seeds under the "
         f"same search. Intervals: {res['bootstrap']}; differences and contrasts are paired by instance.", ""]
    L += tables(full, f"{pf.pop()} instances each" if len(pf) == 1 else "n per family in the header")
    cov = res["coverage"]
    L += ["", "# Added fields ", "",
          f"Coverage: {cov['n_on_axis']} of the {cov['n_full_set']} instances are on the axis (emulator holds "
          f"{cov['n_emulator_10000']} at 10,000, perfect emulator {cov['n_perfect_10000']}; on one side only: "
          f"{len(cov['emulator_only'])} emulator, {len(cov['perfect_only'])} perfect). 10,000-evaluation directories: "
          + "; ".join(f"{s}: " + ", ".join(f"`{p}`" for p in v) for s, v in cov["directories_10000"].items())
          + f". Random search: `{res['inputs_random']['emulator']}` beside `{res['inputs_random']['perfect']}`.", ""]
    L += bca_tables(res["bca"])
    L += ["", "## The analysis plan", "", f"{rule['status']}." + (
        f" Corrected 10,000-minus-1,000 excess {rule['contrast']['value']:+.3f} [{rule['contrast']['bca_lo']:+.3f}, "
        f"{rule['contrast']['bca_hi']:+.3f}]: excludes zero {rule['excludes_zero']}; wording: \"{rule['wording']}\"."
        if rule["status"] == "applied" and rule["contrast"]["bca_lo"] is not None else ""), ""]
    W = res["well_posed"]
    wf = ", ".join(f"{t} {W['per_family'][t]}" for t in FAMILIES)
    L += ["# The same on the well-posed instances", "",
          f"{W['n_instances']} of the {len(inst)} instances are well posed ({wf}) in {W['n_clusters']} city families "
          f"(flag `in_band`, as in the 193-instance tables). Percentile intervals: {W['bootstrap']}. Not well posed: "
          + (", ".join(f"`{i}`" for i in W["instances_not_well_posed"]) or "none") + ".", ""]
    L += tables(wp, "n per family above")
    L += [""] + bca_tables(W["bca"])
    Z = res["zero_event_bounds"]["fields"]
    L += ["", "# Zero-event rates (R1 m16)", "", res["zero_event_bounds"]["note"], "",
          f"{len(Z)} such fields; outside the family rows (which carry no interval): "
          + (", ".join(f"`{z['field']}` ({z['interval_given'][:60]})" for z in Z if "family=" not in z["field"]) or "none")
          + "."]
    (out / "pressure_axis.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[4:]))


if __name__ == "__main__":
    main()
