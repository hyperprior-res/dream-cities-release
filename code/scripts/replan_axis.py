#!/usr/bin/env python3
"""The monthly replanning run : measures, excesses and the readings R-a to R-d.

Inputs: the records of ``code/scripts/run_replan.py`` for the emulator (``--emulator DIR``) and for the perfect emulator
(``--engine DIR``), paired by instance (the analysis is on the instances both hold; ``coverage`` lists the rest).
Per model and arm (``replan``: replanned every month; ``open_loop``: the month-0 choice executed in full on the same
realised seed):

* (a) real success: the share of instances whose realised trajectory passes;
* (b) false acceptance: the share of instances where the model accepts its month-0 choice (the paper's verdict, 8
  samples, at least 4 pass) and the realised trajectory fails;
* the excess false acceptance (emulator minus perfect emulator) and the shortfall in real success (perfect emulator
  minus emulator), paired by instance, per arm; pooled and by task family.

Readings : R-a, the excess false acceptance under replanning; R-b, the replanning
excess minus the open-loop excess on the same instances and seed; R-c, the shortfall in real success under
replanning; R-d, the replanning shortfall minus the open-loop shortfall. Each reading is ``above`` (the interval lies
above zero), ``includes_zero`` or ``below``, with its interval. Intervals: cluster bootstrap over start-state families
(the records' ``cluster``), 2,000 resamples, seed 0, BCa 95 per cent (``pressure_axis.bca_est``, ``hpr_dream.stats``);
where BCa is undefined the percentile limits of the same resamples decide (``interval_used``); a rate with no event
gets the exact one-sided binomial bound on clusters, as in ``pressure_axis``.

Also the open-loop arm judged by the oracle's majority of 32 seeds beside the audit's stored random search at the same
budget on the same instances (``--audit-emulator``, ``--audit-engine``; ``pressure_axis.load``): they should agree up
to the fresh proposal draws; both are printed, nothing is tested.

Usage: PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/replan_axis.py --emulator DIR --engine DIR [--out DIR]
Writes replan.json and replan.md (default results/analysis/).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "hpr-dream"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pressure_axis as PA  # noqa: E402
from dc import audit as A  # noqa: E402

FAMILIES = ("grow", "solvent", "treasury", "recover", "power")
MODELS = ("emulator", "engine")
ARMS = ("replan", "open_loop")
N_BOOT, SEED = 2000, 0
EXCESS = "excess false acceptance"
SHORT = "shortfall in real success"
# the analysis plan, verbatim
WORDING = {
    "R-a": {"above": "the excess false acceptance survives monthly replanning",
            "includes_zero": "under monthly replanning no excess false acceptance is established on these instances",
            "below": "under monthly replanning the emulator is falsely accepted less often than a perfect emulator"},
    "R-b": {"below": "replanning reduces the excess",
            "includes_zero": "no change in the excess under replanning is established",
            "above": "replanning increases the excess"},
}
# R-c and R-d: "the same two readings for the shortfall in real success (perfect emulator minus emulator) with
# 'shortfall in real success' in place of 'excess'". In R-a's sentences the excess is named "excess false acceptance",
# in R-b's "the excess"; each is replaced by the shortfall's name. R-a's below-zero sentence names no excess (it speaks
# of being falsely accepted), so the analysis plan gave R-c no below-zero wording; the analysis plan (point 3) fixed it before any
# run, verbatim below.
WORDING["R-c"] = {"above": "the shortfall in real success survives monthly replanning",
                  "includes_zero": "under monthly replanning no shortfall in real success is established on these "
                                   "instances",
                  "below": "under monthly replanning the emulator's choices truly pass more often than a perfect "
                           "emulator's"}
WORDING["R-d"] = {k: v.replace("the excess", "the shortfall in real success") for k, v in WORDING["R-b"].items()}
WORDING_NOTE = {}
INCLUDES_ZERO_NOTE = "the paper gives the interval's width and says this is not evidence of absence"


def load(run) -> dict:
    """instance -> record of one run directory; an instance twice stops the script."""
    out = {}
    for r in A.read_records(Path(run) / "records.jsonl.gz"):
        if r["instance"] in out:
            raise SystemExit(f"{run}: instance {r['instance']} occurs twice")
        out[r["instance"]] = r
    return out


def units(emu: dict, eng: dict):
    """Per-instance 0/1 arrays on the instances both runs hold (sorted by the emulator's order index)."""
    keys = sorted(set(emu) & set(eng), key=lambda k: (emu[k].get("order_index", 0), k))
    for k in keys:
        if (emu[k]["cluster"], emu[k]["task"]) != (eng[k]["cluster"], eng[k]["task"]):
            raise SystemExit(f"{k}: the two runs disagree on the instance's family or task")
        if emu[k]["realised_seed"] != eng[k]["realised_seed"]:
            raise SystemExit(f"{k}: the two runs have different realised seeds")
    U = {"keys": keys, "cluster": np.array([emu[k]["cluster"] for k in keys]),
         "task": np.array([emu[k]["task"] for k in keys])}
    for m, R in (("emulator", emu), ("engine", eng)):
        acc = np.array([bool(R[k]["accept0"]) for k in keys], dtype=bool)
        U[m] = {"judge_accepts": acc.astype(float)}
        for arm, field in (("replan", "replan_pass"), ("open_loop", "open_loop_pass")):
            ok = np.array([bool(R[k][field]) for k in keys], dtype=bool)
            U[m][arm] = {"real_success": ok.astype(float), "false_acceptance": (acc & ~ok).astype(float)}
        orc = np.array([bool(R[k]["open_loop"]["oracle_accept"]) for k in keys], dtype=bool)
        U[m]["open_loop_oracle"] = {"real_success": orc.astype(float), "false_acceptance": (acc & ~orc).astype(float)}
        # months (of 23) the plan in hand was kept; None where the records do not carry it (controller version 1)
        kept = [R[k].get("incumbent_kept_months") for k in keys]
        U[m]["incumbent_kept_months"] = (None if any(v is None for v in kept)
                                         else np.array(kept, dtype=np.float64))
    return U


def est(v, cl, rate=False, n_boot=N_BOOT, seed=SEED) -> dict:
    return PA.bca_est(np.asarray(v, dtype=np.float64), np.asarray(cl), n_boot, seed, rate=rate)


def limits(e: dict):
    """The interval a reading uses: BCa where defined, else the percentile limits of the same resamples."""
    if e.get("bca_lo") is not None and e.get("bca_hi") is not None:
        return e["bca_lo"], e["bca_hi"], "bca"
    return e["pct_lo"], e["pct_hi"], "percentile"


def reading_of(e: dict) -> str:
    lo, hi, _ = limits(e)
    return "above" if lo > 0 else ("below" if hi < 0 else "includes_zero")


def quantities(U: dict, idx=None) -> dict:
    """Per-instance vectors of the four readings' quantities (on ``idx``)."""
    s = (lambda v: v) if idx is None else (lambda v: v[idx])
    E, P = U["emulator"], U["engine"]
    ex = {arm: s(E[arm]["false_acceptance"] - P[arm]["false_acceptance"]) for arm in ARMS}
    sh = {arm: s(P[arm]["real_success"] - E[arm]["real_success"]) for arm in ARMS}
    return {"R-a": ex["replan"], "R-b": ex["replan"] - ex["open_loop"],
            "R-c": sh["replan"], "R-d": sh["replan"] - sh["open_loop"], "_excess": ex, "_shortfall": sh}


QUANTITY_NAMES = {
    "R-a": "excess false acceptance under replanning (emulator minus perfect emulator)",
    "R-b": "excess false acceptance under replanning minus the open-loop excess, same instances and seed",
    "R-c": "shortfall in real success under replanning (perfect emulator minus emulator)",
    "R-d": "shortfall in real success under replanning minus the open-loop shortfall, same instances and seed"}


def block(U: dict, idx, n_boot=N_BOOT, seed=SEED) -> dict:
    """Measures (a), (b) per model and arm, the excess and the shortfall per arm, on the units ``idx``."""
    cl = U["cluster"][idx]
    out = {"n_instances": int(len(idx)), "n_clusters": int(len(set(cl.tolist())))}
    for m in MODELS:
        out[m] = {"judge_accepts": est(U[m]["judge_accepts"][idx], cl, True, n_boot, seed)}
        for arm in ARMS + ("open_loop_oracle",):
            out[m][arm] = {nm: est(U[m][arm][nm][idx], cl, True, n_boot, seed) for nm in ("real_success",
                                                                                     "false_acceptance")}
        kept = U[m]["incumbent_kept_months"]
        out[m]["incumbent_kept_months_mean"] = None if kept is None else float(kept[idx].mean())
    q = quantities(U, idx)
    out["excess_false_acceptance"] = {arm: est(q["_excess"][arm], cl, False, n_boot, seed) for arm in ARMS}
    out["shortfall_real_success"] = {arm: est(q["_shortfall"][arm], cl, False, n_boot, seed) for arm in ARMS}
    out["excess_false_acceptance_open_loop_oracle"] = est(
        U["emulator"]["open_loop_oracle"]["false_acceptance"][idx] - U["engine"]["open_loop_oracle"]["false_acceptance"][idx],
        cl, False, n_boot, seed)
    return out


def readings(U: dict, n_boot=N_BOOT, seed=SEED) -> dict:
    q = quantities(U)
    out = {}
    for r in ("R-a", "R-b", "R-c", "R-d"):
        e = est(q[r], U["cluster"], False, n_boot, seed)
        lo, hi, kind = limits(e)
        key = reading_of(e)
        d = {"quantity": QUANTITY_NAMES[r], "estimate": e, "interval_used": kind, "lo": lo, "hi": hi,
             "interval_width": float(hi - lo), "reading": key, "wording": WORDING[r][key], "wordings": WORDING[r]}
        if key == "includes_zero" and r in ("R-a", "R-c"):
            d["note"] = INCLUDES_ZERO_NOTE
        if r in WORDING_NOTE:
            d["wording_note"] = WORDING_NOTE[r]
        out[r] = d
    return out


def beside_audit(U: dict, audit: dict, budget: int, n_boot=N_BOOT, seed=SEED) -> dict:
    """The open-loop arm under the oracle's majority beside the audit's stored random search at ``budget`` (per model:
    judge accepts, real success, false acceptance; values with intervals; per-instance agreement counts)."""
    out = {"budget": int(budget), "note": "the replanning run draws fresh proposals at month 0, the audit searched the "
                                          "logged plans: the two agree up to those draws; both are printed"}
    for m in MODELS:
        if audit.get(m) is None:
            out[m] = {"status": "no audit records given"}
            continue
        recs = audit[m]
        have = [i for i, k in enumerate(U["keys"]) if (k, budget) in recs]
        if not have:
            out[m] = {"status": f"the audit holds none of these instances at B = {budget}"}
            continue
        idx = np.array(have)
        cl = U["cluster"][idx]
        fa = np.array([recs[(U["keys"][i], budget)][0] for i in have], dtype=float)
        ok = np.array([recs[(U["keys"][i], budget)][1] for i in have], dtype=float)
        acc = np.array([recs[(U["keys"][i], budget)][2] for i in have], dtype=float)
        R = U[m]
        out[m] = {"n_instances": int(len(idx)),
                  "replan_open_loop_oracle": {"judge_accepts": est(R["judge_accepts"][idx], cl, True, n_boot, seed),
                                              "real_success": est(R["open_loop_oracle"]["real_success"][idx], cl, True,
                                                                  n_boot, seed),
                                              "false_acceptance": est(R["open_loop_oracle"]["false_acceptance"][idx],
                                                                      cl, True, n_boot, seed)},
                  "audit_stored": {"judge_accepts": est(acc, cl, True, n_boot, seed),
                                   "real_success": est(ok, cl, True, n_boot, seed),
                                   "false_acceptance": est(fa, cl, True, n_boot, seed)},
                  "agreement": {"judge_accepts_same": int((R["judge_accepts"][idx] == acc).sum()),
                                "oracle_accepts_same": int((R["open_loop_oracle"]["real_success"][idx] == ok).sum()),
                                "false_acceptance_same": int((R["open_loop_oracle"]["false_acceptance"][idx] == fa).sum())}}
    return out


def complete_prefix(emu: dict, eng: dict) -> int:
    """The analysis plan: the largest n, a multiple of 5 (k a family), such that every order position 0..n-1 is held by both
    sides. An instance held by both must have the same order position on both."""
    for k in set(emu) & set(eng):
        if emu[k].get("order_index") != eng[k].get("order_index"):
            raise SystemExit(f"{k}: the two runs give the instance different order positions")
    both = {int(emu[k]["order_index"]) for k in set(emu) & set(eng)}
    n = 0
    while all(p in both for p in range(n, n + 5)):
        n += 5
    return n


def analyse(emu: dict, eng: dict, audit=None, audit_budget: int = 1000, n_boot=N_BOOT, seed=SEED,
            allow_unequal_plans: bool = False, prefix: bool = True) -> dict:
    """``prefix``: analyse the largest prefix of the fixed order, 5k positions, complete on both
    sides (``complete_prefix``); instances both sides hold beyond it are listed under ``coverage.beyond_prefix``.
    ``prefix=False``: every instance both sides hold (the intersection)."""
    cov = {"emulator_only": sorted(set(emu) - set(eng)), "engine_only": sorted(set(eng) - set(emu))}
    if prefix:
        n_pre = complete_prefix(emu, eng)
        if n_pre == 0:
            raise SystemExit("no prefix of 5 or more order positions is complete on both sides")
        both = set(emu) & set(eng)
        cov["beyond_prefix"] = sorted(int(emu[k]["order_index"]) for k in both if int(emu[k]["order_index"]) >= n_pre)
        emu = {k: r for k, r in emu.items() if int(r["order_index"]) < n_pre}
        eng = {k: r for k, r in eng.items() if int(r["order_index"]) < n_pre}
    U = units(emu, eng)
    n = len(U["keys"])
    if n == 0:
        raise SystemExit("the two runs share no instance")
    vers = {m: sorted({int(r.get("controller_version", 1)) for r in R.values()}) for m, R in (("emulator", emu),
                                                                                          ("engine", eng))}
    if len(vers["emulator"]) != 1 or vers["emulator"] != vers["engine"]:
        raise SystemExit(f"controller versions differ within or between the runs: {vers}")
    streams = {m: sorted({str(r.get("seed_stream") or "") for r in R.values()}) for m, R in (("emulator", emu),
                                                                                           ("engine", eng))}
    if any(len(v) != 1 for v in streams.values()):      # one seed stream per side; the two sides may differ by design
        raise SystemExit(f"a run holds records of more than one seed stream: {streams}")
    plans = {r["n_plans"] for k in U["keys"] for r in (emu[k], eng[k])}
    if len(plans) != 1 and not allow_unequal_plans:
        raise SystemExit(f"the two runs used different numbers of plans per replan ({sorted(plans)})")
    res = {"decision": 88, "controller_version": vers["emulator"][0],
           "seed_stream": {m: (v[0] or None) for m, v in streams.items()}, "n_instances": n, "n_clusters": int(len(set(U["cluster"].tolist()))),
           "per_family": {t: int((U["task"] == t).sum()) for t in FAMILIES},
           "n_plans": {"emulator": sorted({r["n_plans"] for r in emu.values()}),
                       "engine": sorted({r["n_plans"] for r in eng.values()})},
           "statistics": f"means over instances; cluster bootstrap over start-state families, {n_boot} resamples, "
                         f"seed {seed}, BCa 95 per cent (pressure_axis.bca_est); differences paired by instance; a "
                         "reading uses the BCa limits, or the percentile limits where BCa is undefined",
           "definitions": {
               "real_success": "the realised trajectory (the instance's oracle seed 0) passes the task",
               "false_acceptance": "the model accepts its month-0 choice (8 samples, at least 4 pass) and the realised "
                                   "trajectory fails",
               "replan": "random search replanned every month from the engine's real state, the selected plan's month "
                         "executed each month",
               "open_loop": "the model's month-0 choice executed in full on the same realised seed",
               "open_loop_oracle": "the open-loop arm judged by the oracle's majority of 32 seeds (as the audit judges)",
               "excess_false_acceptance": "emulator minus perfect emulator, paired by instance",
               "shortfall_real_success": "perfect emulator minus emulator, paired by instance"},
           "coverage": cov, "prefix": bool(prefix),
           "order_index": sorted(int(emu[k]["order_index"]) for k in U["keys"]),
           "pooled": block(U, np.arange(n), n_boot, seed), "by_family": {}}
    for t in FAMILIES:
        idx = np.flatnonzero(U["task"] == t)
        if idx.size:
            res["by_family"][t] = block(U, idx, n_boot, seed)
    res["readings"] = readings(U, n_boot, seed)
    if audit is not None:
        res["open_loop_beside_audit"] = beside_audit(U, audit, audit_budget, n_boot, seed)
    return res


def _iv(e, signed=False) -> str:
    s = "+" if signed else ""
    lo, hi, kind = limits(e)
    return f"{e['value']:{s}.3f} [{lo:{s}.3f}, {hi:{s}.3f}]" + ("" if kind == "bca" else " pct")


def markdown(res: dict, inputs: dict) -> str:
    P = res["pooled"]
    L = ["# Monthly replanning ", "",
         f"Generated {res.get('generated', '')} by `code/scripts/replan_axis.py` from {inputs}. {res['n_instances']} "
         f"instances ({', '.join(f'{t} {n}' for t, n in res['per_family'].items())}) in {res['n_clusters']} start-state "
         f"families; plans per replan {res['n_plans']}. {res['statistics']}.", "",
         "Definitions: " + "; ".join(f"**{k}**: {v}" for k, v in res["definitions"].items()) + ".", "",
         "## Readings", "", "| reading | quantity | estimate [interval] | reading | wording |", "|---|---|---|---|---|"]
    for r, d in res["readings"].items():
        w = d["wording"] if d["wording"] is not None else f"(none: {d.get('wording_note', '')})"
        extra = f" Interval width {d['interval_width']:.3f}; {d['note']}." if "note" in d else ""
        L.append(f"| {r} | {d['quantity']} | {_iv(d['estimate'], True)} | {d['reading']} | \"{w}\".{extra} |")
    L += ["", "## Measures per model and arm", "",
          "| subset | n | model | judge accepts month-0 choice | real success, replan | real success, open loop | "
          "false acceptance, replan | false acceptance, open loop | months the plan in hand was kept (mean, of 23) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, b in [("pooled", P)] + list(res["by_family"].items()):
        for m in MODELS:
            x = b[m]
            L.append(f"| {name} | {b['n_instances']} | {m} | {_iv(x['judge_accepts'])} | {_iv(x['replan']['real_success'])} | "
                     f"{_iv(x['open_loop']['real_success'])} | {_iv(x['replan']['false_acceptance'])} | "
                     f"{_iv(x['open_loop']['false_acceptance'])} | "
                     + ("n/a" if x["incumbent_kept_months_mean"] is None else f"{x['incumbent_kept_months_mean']:.1f}")
                     + " |")
    L += ["", "## Excess false acceptance and shortfall in real success, per arm", "",
          "| subset | n | excess, replan | excess, open loop | shortfall, replan | shortfall, open loop |",
          "|---|---|---|---|---|---|"]
    for name, b in [("pooled", P)] + list(res["by_family"].items()):
        L.append(f"| {name} | {b['n_instances']} | {_iv(b['excess_false_acceptance']['replan'], True)} | "
                 f"{_iv(b['excess_false_acceptance']['open_loop'], True)} | {_iv(b['shortfall_real_success']['replan'], True)} | "
                 f"{_iv(b['shortfall_real_success']['open_loop'], True)} |")
    ba = res.get("open_loop_beside_audit")
    if ba:
        L += ["", f"## The open-loop arm under the oracle's majority beside the audit's random search at B = {ba['budget']:,}",
              "", ba["note"] + ".", "",
              "| model | n | source | judge accepts | real success (majority) | false acceptance (majority) | agreement |",
              "|---|---|---|---|---|---|---|"]
        for m in MODELS:
            x = ba[m]
            if "status" in x:
                L.append(f"| {m} | 0 | {x['status']} | | | | |")
                continue
            g = x["agreement"]
            for src, lab in (("replan_open_loop_oracle", "replanning run, month-0 choice"), ("audit_stored", "audit")):
                y = x[src]
                L.append(f"| {m} | {x['n_instances']} | {lab} | {_iv(y['judge_accepts'])} | {_iv(y['real_success'])} | "
                         f"{_iv(y['false_acceptance'])} | " + (f"same judge verdict {g['judge_accepts_same']}, same oracle "
                                                                f"verdict {g['oracle_accepts_same']}, same false "
                                                                f"acceptance {g['false_acceptance_same']}" if src == "audit_stored"
                                                                else "") + " |")
    cov = res["coverage"]
    L += ["", f"Coverage: emulator only {len(cov['emulator_only'])}, perfect emulator only {len(cov['engine_only'])}."
          + (f" Analysed: the first {len(res['order_index'])} positions of the fixed order (the largest prefix of 5k "
             f"complete on both sides); held by both beyond it: {len(cov.get('beyond_prefix', []))}."
             if res.get("prefix") else " Analysed: every instance both sides hold (no prefix rule).")]
    return "\n".join(L) + "\n"


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--emulator", required=True)
    ap.add_argument("--engine", required=True)
    ap.add_argument("--audit-emulator", default=str(ROOT / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24"))
    ap.add_argument("--audit-engine", default=str(ROOT / "results/audit/engine_reference/tasks_v2_H24/B_economy"))
    ap.add_argument("--audit-budget", type=int, default=1000)
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", default=str(ROOT / "results/analysis"))
    ap.add_argument("--prefix", action=argparse.BooleanOptionalAction, default=True,
                    help="analyse the largest prefix of the fixed order, 5k positions, complete on both sides (decision "
                         "92; default); --no-prefix: every instance both sides hold")
    ap.add_argument("--allow-unequal-plans", action="store_true", help="pair runs made with different numbers of "
                    "plans per replan (dry runs only)")
    a = ap.parse_args(argv)
    emu, eng = load(a.emulator), load(a.engine)
    audit = {}
    for m, d in (("emulator", a.audit_emulator), ("engine", a.audit_engine)):
        audit[m] = PA.load(Path(d), "random") if d and (Path(d) / "records.jsonl.gz").exists() else None
    res = analyse(emu, eng, audit, a.audit_budget, a.n_boot, a.seed, a.allow_unequal_plans, a.prefix)
    rel = lambda p: str(Path(p).resolve().relative_to(ROOT)) if Path(p).resolve().is_relative_to(ROOT) else str(p)  # noqa: E731
    res["inputs"] = {"emulator": rel(a.emulator), "engine": rel(a.engine), "audit_emulator": rel(a.audit_emulator),
                     "audit_engine": rel(a.audit_engine)}
    res["generated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "replan.json").write_text(json.dumps(res, indent=1))
    (out / "replan.md").write_text(markdown(res, res["inputs"]))
    print(f"wrote {out / 'replan.json'} and {out / 'replan.md'}")
    for r, d in res["readings"].items():
        print(f"{r}: {d['estimate']['value']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}] ({d['interval_used']}) -> {d['reading']}: "
              f"{d['wording']}")


if __name__ == "__main__":
    main()
