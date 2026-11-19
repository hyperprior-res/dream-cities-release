#!/usr/bin/env python
"""Side-by-side check of two checkpoints' evaluations (eval_fidelity.py JSONs on one selection).

  pilot_check.py --ref p5=<json> [--ref-repeat <json of the same checkpoint, another --eval-seed>]
                 --new p6=<json> [--new-repeat <json>] [--new-seed <json of the new config, another training seed>]
                 --out <md>

Rows: tiles (one-month structural F1 of one sample, changed-since-start structural F1 at 12 and 24
months), funds and population (median relative error of one sample at 12 and 24 months), valves and
score (one month from the plans' start states and mean absolute error at 12 and 24 months, ratio to
copy-last-state), the 24-month mean ratio over scalars. Every row is the headline kind: one model
sample at T=1. Evaluation noise is the difference between the two evaluations of the reference
checkpoint under different noise seeds; training noise, when --new-seed is given, is the difference
between the new configuration trained with two seeds (each evaluated once, so it contains evaluation
noise too). The verdict is "better" when the new checkpoint is better, "within noise" when it is worse
by at most twice the larger noise, otherwise "worse". The shares at the engine's bounds follow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROWS = [  # (label, path into the JSON, higher is better)
    ("tile structural F1, one month", ("onestep", "model_T1", "structural", "f1"), True),
    ("tile structural F1 since start, 12 months", ("rollouts", "h12", "tile_since_start", "structural", "f1"), True),
    ("tile structural F1 since start, 24 months", ("rollouts", "h24", "tile_since_start", "structural", "f1"), True),
    ("funds median rel. error, 12 months", ("rollouts", "h12", "median_rel_funds", "sample"), False),
    ("funds median rel. error, 24 months", ("rollouts", "h24", "median_rel_funds", "sample"), False),
    ("population median rel. error, 12 months", ("rollouts", "h12", "median_rel_pop", "sample"), False),
    ("population median rel. error, 24 months", ("rollouts", "h24", "median_rel_pop", "sample"), False),
    ("res_valve, one month from start (x copy)", ("rollouts", "h1", "scalars", "res_valve", "ratio_sample"), False),
    ("com_valve, one month from start (x copy)", ("rollouts", "h1", "scalars", "com_valve", "ratio_sample"), False),
    ("ind_valve, one month from start (x copy)", ("rollouts", "h1", "scalars", "ind_valve", "ratio_sample"), False),
    ("score, one month from start (x copy)", ("rollouts", "h1", "scalars", "score", "ratio_sample"), False),
    ("res_valve, 12 months (x copy)", ("rollouts", "h12", "scalars", "res_valve", "ratio_sample"), False),
    ("com_valve, 12 months (x copy)", ("rollouts", "h12", "scalars", "com_valve", "ratio_sample"), False),
    ("ind_valve, 12 months (x copy)", ("rollouts", "h12", "scalars", "ind_valve", "ratio_sample"), False),
    ("res_valve, 24 months (x copy)", ("rollouts", "h24", "scalars", "res_valve", "ratio_sample"), False),
    ("com_valve, 24 months (x copy)", ("rollouts", "h24", "scalars", "com_valve", "ratio_sample"), False),
    ("ind_valve, 24 months (x copy)", ("rollouts", "h24", "scalars", "ind_valve", "ratio_sample"), False),
    ("funds, one month on random transitions (MAE)", ("onestep", "scalar_mae_1m", "funds", "T1"), False),
    ("mean ratio over scalars, 24 months", ("rollouts", "h24", "mean_ratio_sample"), False),
]


def get(d, path):
    """The value at ``path``, or None when the evaluation has no such entry (e.g. a shorter horizon)."""
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return float(d)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--ref-repeat", default="")
    ap.add_argument("--new", required=True)
    ap.add_argument("--new-repeat", default="")
    ap.add_argument("--new-seed", default="", help="evaluation JSON of the new configuration trained with another seed")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rl, rp = args.ref.split("=", 1)
    nl, np_ = args.new.split("=", 1)
    R, N = json.loads(Path(rp).read_text()), json.loads(Path(np_).read_text())
    R2 = json.loads(Path(args.ref_repeat).read_text()) if args.ref_repeat else None
    N2 = json.loads(Path(args.new_repeat).read_text()) if args.new_repeat else None
    NS = json.loads(Path(args.new_seed).read_text()) if args.new_seed else None
    for x in (R, N, R2, N2, NS):
        if x is not None and x["selection_key"] != R["selection_key"]:
            raise SystemExit("evaluations on different selections")
    sel = R.get("selection", {})
    L = [f"# Check: {nl} against {rl}", "",
         f"Selection {sel.get('name')} ({sel.get('n_onestep')} transitions, {sel.get('n_plans')} plans, key "
         f"{R['selection_key']}); {rl}: {R['checkpoint']} ({R['samples']:,} samples, decoding {R['decoding']['name']}, "
         f"weights {R['weights']}); {nl}: {N['checkpoint']} ({N['samples']:,} samples, decoding {N['decoding']['name']}, "
         f"weights {N['weights']}). One model sample at T=1 in every row." +
         (f" Training-seed replicate: {NS['checkpoint']}." if NS else ""), "",
         f"| metric | {rl} | {rl}, other noise seed | {nl} |" + (f" {nl}, other noise seed |" if N2 else "") +
         (f" {nl}, other training seed |" if NS else "") + " evaluation noise |" + (" training noise |" if NS else "") +
         " verdict |", "|---|---|---|---|" + ("---|" if N2 else "") + ("---|---|" if NS else "") + "---|---|"]
    counts = {"better": 0, "within noise": 0, "worse": 0, "n/a": 0}
    for lab, path, hib in ROWS:
        r, n = get(R, path), get(N, path)
        if r is None or n is None:
            continue
        r2 = get(R2, path) if R2 else None
        n2 = get(N2, path) if N2 else None
        ns = get(NS, path) if NS else None
        noise = abs(r - r2) if r2 is not None else None
        tnoise = abs(n - ns) if ns is not None else None
        n2 = n2 if n2 is not None else float("nan")
        better = n > r if hib else n < r
        big = max(x for x in (noise, tnoise, -1.0) if x is not None)
        if better:
            v = "better"
        elif big < 0:
            v = "n/a"
        else:
            v = "within noise" if abs(n - r) <= 2 * big else "worse"
        counts[v] += 1
        L.append(f"| {lab} | {r:.4f} | {'n/a' if r2 is None else f'{r2:.4f}'} | {n:.4f} |" +
                 (f" {n2:.4f} |" if N2 else "") + (f" {ns:.4f} |" if NS else "") +
                 f" {'n/a' if noise is None else f'{noise:.4f}'} |" + (f" {tnoise:.4f} |" if NS else "") + f" {v} |")
    L += ["", "Verdicts: " + ", ".join(f"{k} {v}" for k, v in counts.items() if v), ""]
    for tag, src in (("one month (random transitions)", N["onestep"].get("bound_shares")),
                     ("rollouts (months 1..H of the plans)", N["rollouts"].get("bound_shares"))):
        if not src:
            continue
        mk, ek = ("model_T1", "engine") if "one month" in tag else ("model", "engine")
        L += [f"## {nl}: shares at the engine's bounds, {tag}", "",
              "| entry | bounds | model at lower | engine at lower | model at upper | engine at upper | model beyond | engine beyond |",
              "|---|---|---|---|---|---|---|---|"]
        pct = lambda x: "n/a" if x is None else f"{100 * x:.2f}%"
        for name, row in src.items():
            m, e = row.get(mk, {}), row.get(ek, {})
            lo, hi = row["lower"], row["upper"]
            L.append(f"| {name} | [{'-inf' if lo is None else int(lo)}, {'inf' if hi is None else int(hi)}] | "
                     f"{pct(m.get('share_at_lower'))} | {pct(e.get('share_at_lower'))} | {pct(m.get('share_at_upper'))} | "
                     f"{pct(e.get('share_at_upper'))} | {m.get('beyond_bounds')} | {e.get('beyond_bounds')} |")
        L.append("")
    Path(args.out).write_text("\n".join(L))
    print("wrote", args.out)
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
