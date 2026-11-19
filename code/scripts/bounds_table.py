#!/usr/bin/env python
"""The paper's table of the engine's bounds (results/fidelity/bounds.md and bounds.json).

Every row comes from ``dc.model.BOUND_SOURCES`` (entry, bound, engine source line or data type), and
beside it the stores' own values: minimum, maximum, share of observations at the lower and at the
upper bound, and the number beyond the bounds (which must be 0), on train_full, heldout_eval and
train_eval. Scalars and ledger entries are counted over every observation row, the charged build cost
over every transition; overlays over every observation of heldout_eval and train_eval (train_full's
overlays, 45 GB, are not scanned).

  bounds_table.py [--out-dir results/fidelity]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc import data  # noqa: E402
from dc.engine import LG, SCALAR_NAMES  # noqa: E402
from dc.model import BOUND_SOURCES  # noqa: E402

SPLITS = ("train_full", "heldout_eval", "train_eval")
SC = {n: i for i, n in enumerate(SCALAR_NAMES)}
# overlay rows of BOUND_SOURCES -> (store array, channels)
OVERLAY_ARRAYS = {"half overlays (5)": ("half", None), "rate of growth": ("eighth", [0]),
                  "fire, police coverage": ("eighth", [1, 2]), "terrain": ("terrain", None), "com_rate": ("com_rate", None)}
FUNDS_VERDICT = (
    "Funds below zero is impossible in the engine, not merely unseen: totalFunds changes only through spend and "
    "setFunds (src/micropolis.cpp:1066-1081); every charge is checked first (a tool is refused when totalFunds < cost, "
    "src/tool.cpp:154; the yearly budget pays at most taxFund + totalFunds and otherwise pays nothing and switches "
    "auto-budget off, src/budget.cpp:124-230, 268-310); setFunds is otherwise called only at load or reset with a "
    "fixed positive amount. The one caveat is arithmetic: spend and setFunds take a 32-bit int, so the bound holds "
    "while funds stay below 2,147,483,647.")


class Stat:
    def __init__(self, lo, hi) -> None:
        self.lo, self.hi = lo, hi
        self.n = self.at_lo = self.at_hi = self.beyond = 0
        self.vmin, self.vmax = np.inf, -np.inf

    def add(self, v: np.ndarray) -> None:
        v = np.asarray(v).reshape(-1)
        if v.size == 0:
            return
        self.n += v.size
        self.vmin, self.vmax = min(self.vmin, float(v.min())), max(self.vmax, float(v.max()))
        if self.lo is not None:
            self.at_lo += int((v == self.lo).sum())
            self.beyond += int((v < self.lo).sum())
        if self.hi is not None:
            self.at_hi += int((v == self.hi).sum())
            self.beyond += int((v > self.hi).sum())

    def report(self) -> dict:
        if self.n == 0:
            return {"n": 0}
        return {"n": self.n, "min": self.vmin, "max": self.vmax, "beyond": self.beyond,
                "share_at_lower": self.at_lo / self.n if self.lo is not None else None,
                "share_at_upper": self.at_hi / self.n if self.hi is not None else None}


def scan(split: str, chunk: int = 200_000) -> dict:
    store, _ = data.open_split(split)
    stats = {}
    rows = [r for r in BOUND_SOURCES]
    for kind, name, lo, hi, _src, _cav in rows:
        stats[(kind, name)] = Stat(lo, hi)
    n_obs, n_tr = store.n_obs, store.n_trans
    for a in range(0, n_obs, chunk):
        sc = np.asarray(store.scalars[a:a + chunk])
        lg = np.asarray(store.ledger[a:a + chunk])
        for kind, name, *_ in rows:
            if kind == "scalar":
                stats[(kind, name)].add(sc[:, SC[name]])
            elif kind == "ledger":
                stats[(kind, name)].add(lg[:, LG[name]])
        if split != "train_full":
            for kind, name, *_ in rows:
                if kind == "overlay":
                    arr, ch = OVERLAY_ARRAYS[name]
                    x = np.asarray(getattr(store, arr)[a:a + chunk])
                    stats[(kind, name)].add(x if ch is None else x[:, ch])
    for a in range(0, n_tr, chunk):
        stats[("cost", "build_cost")].add(np.asarray(store.build_cost[a:a + chunk]))
    return {f"{k}:{n}": s.report() for (k, n), s in stats.items()}


def fmt_bound(lo, hi) -> str:
    return f"[{'-inf' if lo is None else lo}, {'inf' if hi is None else hi}]"


def pct(x) -> str:
    return "n/a" if x is None else (f"{100 * x:.2f}%" if x >= 1e-4 or x == 0 else f"{100 * x:.4f}%")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=str(ROOT / "results/fidelity"))
    args = ap.parse_args()
    res = {s: scan(s) for s in SPLITS}
    out = {"rows": [{"kind": k, "entry": n, "lower": lo, "upper": hi, "source": src, "caveat": cav}
                    for k, n, lo, hi, src, cav in BOUND_SOURCES], "data": res, "funds_verdict": FUNDS_VERDICT}
    od = Path(args.out_dir)
    (od / "bounds.json").write_text(json.dumps(out, indent=1))
    L = ["# Bounds of the engine's state space", "",
         "Each bounded quantity has a censored likelihood: the predictive mass beyond a bound is the probability of the "
         "bound, so sampling and pinning to the bound is exactly the trained model (dc.model.BOUND_SOURCES; "
         "code/scripts/bounds_table.py writes this file). A bound is kept only where the engine makes it a fact; "
         "paths are under engine/ (src/ for the simulator).", "",
         "## Table", "",
         "| kind | entry | bound | engine source or data type | caveat |", "|---|---|---|---|---|"]
    for k, n, lo, hi, src, cav in BOUND_SOURCES:
        L.append(f"| {k} | {n} | {fmt_bound(lo, hi) if (lo is not None or hi is not None) else 'none'} | {src} | {cav or ''} |")
    L += ["", "Derived, not learned (no likelihood): sim_cycle (+4 mod 1024), initial_eval (0), disasters (copied); "
          "tax (the action's), city_time (+4), pop = 20 (res_pop + 8 (com_pop + ind_pop)).", "",
          "## Funds below zero", "", FUNDS_VERDICT, "",
          "## The stores' values", "",
          "Minimum and maximum, share of observations at the lower / upper bound, and observations beyond the bounds "
          "(transitions for build_cost). Overlays: every cell of every observation of heldout_eval and train_eval.", ""]
    for split in SPLITS:
        L += [f"### {split}", "", "| entry | bound | n | min | max | at lower | at upper | beyond |", "|---|---|---|---|---|---|---|---|"]
        for k, n, lo, hi, _src, _cav in BOUND_SOURCES:
            if lo is None and hi is None and k != "ledger":
                continue
            r = res[split][f"{k}:{n}"]
            if r.get("n", 0) == 0:
                continue
            L.append(f"| {n} | {fmt_bound(lo, hi)} | {r['n']:,} | {r['min']:.0f} | {r['max']:.0f} | {pct(r['share_at_lower'])} | "
                     f"{pct(r['share_at_upper'])} | {r['beyond']} |")
        L.append("")
    (od / "bounds.md").write_text("\n".join(L))
    print("wrote", od / "bounds.md", od / "bounds.json")
    bad = [(s, e) for s in SPLITS for e, r in res[s].items() if r.get("beyond")]
    print("observations beyond a bound:", bad if bad else "none")


if __name__ == "__main__":
    main()
