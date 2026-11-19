#!/usr/bin/env python3
"""The positive control of the monthly replanning run : the controller inside the perfect emulator.

Input: the records of ``code/scripts/run_replan.py --model engine`` (``--engine DIR``). On the realised seed, per
instance, the replanned trajectory's pass (0/1) minus the open-loop arm's pass (the month-0 choice executed in full on
the same seed). The gate reads the pooled paired difference: if its 95 per cent interval lies wholly below zero, the
comparison does not enter the paper . The family bar  reads the same difference within each
task family: if any family's interval lies wholly below zero, the comparison does not enter the paper either. The
interval is the one ``replan_axis.py`` uses for every reading: cluster bootstrap over start-state families, 2,000
resamples, seed 0, BCa, the percentile limits of the same resamples where BCa is undefined. The by-family table is
printed either way.

Usage: PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/replan_control.py --engine DIR [--out DIR]
Writes replan_control.json and replan_control.md (default results/analysis/).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import replan_axis as RA  # noqa: E402

GATE = ("if the paired difference between replanned and open-loop real success on the realised seed has a 95 per cent "
        "interval wholly below zero, the comparison does not enter the paper ")
FAMILY_BAR = ("if any task family's paired difference has a 95 per cent interval wholly below zero, the comparison "
              "does not enter the paper ")


def incomplete(eng: dict, n_instances: int, per_family: int, n_plans: int) -> list:
    """Why the run is not the one the gates are fixed on (all instances, balanced families, the full number of
    proposals); empty when it is."""
    why = []
    if len(eng) != n_instances:
        why.append(f"{len(eng)} instances, not {n_instances}")
    fam = {f: sum(r["task"] == f for r in eng.values()) for f in RA.FAMILIES}
    if any(v != per_family for v in fam.values()):
        why.append(f"instances per family {fam}, not {per_family} each")
    plans = sorted({int(r.get("n_plans", -1)) for r in eng.values()})
    if plans != [n_plans]:
        why.append(f"proposals per month {plans}, not {n_plans}")
    return why


def control(eng: dict, n_boot=RA.N_BOOT, seed=RA.SEED) -> dict:
    keys = sorted(eng, key=lambda k: (eng[k].get("order_index", 0), k))
    vers = sorted({int(eng[k].get("controller_version", 1)) for k in keys})
    if len(vers) != 1:
        raise SystemExit(f"controller versions differ within the run: {vers}")
    cl = np.array([eng[k]["cluster"] for k in keys])
    task = np.array([eng[k]["task"] for k in keys])
    rp = np.array([bool(eng[k]["replan_pass"]) for k in keys], dtype=float)
    ol = np.array([bool(eng[k]["open_loop_pass"]) for k in keys], dtype=float)
    acc = np.array([bool(eng[k]["accept0"]) for k in keys], dtype=float)

    def one(idx) -> dict:
        d = RA.est(rp[idx] - ol[idx], cl[idx], False, n_boot, seed)
        lo, hi, kind = RA.limits(d)
        return {"n_instances": int(len(idx)), "n_clusters": int(len(set(cl[idx].tolist()))),
                "replan_pass": int(rp[idx].sum()), "open_loop_pass": int(ol[idx].sum()),
                "judge_accepts": int(acc[idx].sum()),
                "replan_only": int(((rp[idx] == 1) & (ol[idx] == 0)).sum()),
                "open_loop_only": int(((rp[idx] == 0) & (ol[idx] == 1)).sum()),
                "difference": d, "interval_used": kind, "lo": lo, "hi": hi}

    allidx = np.arange(len(keys))
    pooled = one(allidx)
    fails = bool(pooled["hi"] < 0)
    fam = {f: one(np.flatnonzero(task == f)) for f in RA.FAMILIES if (task == f).any()}
    lost = [f for f, b in fam.items() if b["hi"] is not None and b["hi"] < 0]
    kept = {f: (float(np.mean([int(eng[k]["incumbent_kept_months"]) for k in keys if eng[k]["task"] == f]))
                if vers[0] >= 2 else None) for f in fam}       # version 1 has no incumbent
    return {"decision": 94, "controller_version": vers[0], "gate": GATE, "family_bar": FAMILY_BAR, "pooled": pooled,
            "gate_fails": fails, "families_below_zero": lost, "family_bar_fails": bool(lost),
            "enters_paper_if_complete_and_reviewed": not (fails or lost),
            "by_family": fam, "incumbent_kept_months_mean": kept, "n_boot": int(n_boot), "seed": int(seed)}


def render(res: dict) -> str:
    p = res["pooled"]
    L = ["# Monthly replanning: the controller inside the perfect emulator ", "",
         f"Controller version {res['controller_version']}; {p['n_instances']} instances, {p['n_clusters']} start-state "
         f"families; realised seed; cluster bootstrap, {res['n_boot']} resamples, seed {res['seed']}.", "",
         f"Gate: {res['gate']}.", "",
         f"Pooled: replanned passes {p['replan_pass']} of {p['n_instances']}, open loop {p['open_loop_pass']} of "
         f"{p['n_instances']}; paired difference {p['difference']['value']:+.3f} "
         f"[{p['lo']:+.3f}, {p['hi']:+.3f}] ({p['interval_used']}); replanning alone passes {p['replan_only']}, open "
         f"loop alone {p['open_loop_only']}.", "",
         "Reading: the interval " + ("lies wholly below zero: the comparison does not enter the paper."
                                     if res["gate_fails"] else
                                     "does not lie wholly below zero: the pooled gate does not stop the comparison."), "",
         f"Family bar: {res['family_bar']}.", "",
         "Reading: " + ("the interval lies wholly below zero in " + ", ".join(res["families_below_zero"])
                        + ": the comparison does not enter the paper." if res["family_bar_fails"] else
                        "no family's interval lies wholly below zero: the family bar does not stop the comparison."), "",
         "Mean months (of 23) on which the plan chosen the month before was kept: "
         + ", ".join(f"{f} " + ("n/a" if v is None else f"{v:.1f}")
                     for f, v in res["incumbent_kept_months_mean"].items()) + ".", "",
         "By family (printed either way):", "",
         "| family | instances | replanned passes | open loop passes | replanning alone | open loop alone | difference "
         "| 95% interval |", "|---|---|---|---|---|---|---|---|"]
    for f, b in res["by_family"].items():
        lo = "n/a" if b["lo"] is None else f"{b['lo']:+.3f}"
        hi = "n/a" if b["hi"] is None else f"{b['hi']:+.3f}"
        L.append(f"| {f} | {b['n_instances']} | {b['replan_pass']} | {b['open_loop_pass']} | {b['replan_only']} | "
                 f"{b['open_loop_only']} | {b['difference']['value']:+.3f} | [{lo}, {hi}] |")
    return "\n".join(L) + "\n"


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--engine", required=True)
    ap.add_argument("--n-boot", type=int, default=RA.N_BOOT)
    ap.add_argument("--seed", type=int, default=RA.SEED)
    ap.add_argument("--out", default=str(ROOT / "results/analysis"))
    ap.add_argument("--instances", type=int, default=100, help="the run the gates are fixed on: this many instances,")
    ap.add_argument("--per-family", type=int, default=20, help="this many in each family,")
    ap.add_argument("--plans", type=int, default=1000, help="and this many proposals a month; anything else stops")
    a = ap.parse_args(argv)
    eng = RA.load(a.engine)
    why = incomplete(eng, a.instances, a.per_family, a.plans)
    if why:
        raise SystemExit(f"{a.engine}: no gate is read on this run: " + "; ".join(why))
    res = control(eng, a.n_boot, a.seed)
    src = Path(a.engine).resolve()
    res["inputs"] = {"engine": str(src.relative_to(ROOT)) if src.is_relative_to(ROOT) else str(src)}
    res["written"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "replan_control.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    md = render(res)
    (out / "replan_control.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
