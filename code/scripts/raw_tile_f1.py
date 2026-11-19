"""Raw beside structural changed-tile F1 on every run's test selection .

The fidelity JSON of each run's final checkpoint on the test selection
(``results/fidelity/ladder/<run>/test/<run>_samples_<N>_dec-a.json``, the file ``paper/scripts/make_numbers.py``
reads for Table 8) stores both forms of the changed-tile F1: ``gap_closed.tile_F1_1m_{structural,raw}_T1``
(model, engine under another seed = floor, copy-last-state) and the 12-month changed-since-start F1
``gap_closed.tile_F1_since_start_12m_{structural,raw}``; ``onestep.model_T1.{structural,raw}`` carries the
one-month counts (tp, fp, fn) and ``f1_ci95_by_family``, the evaluation's own 95 per cent interval (bootstrap over
city families). Structural merges tile codes along animation cycles and road traffic levels (protocol);
raw compares tile codes as stored. Nothing is recomputed.

    PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/raw_tile_f1.py

Writes results/analysis/raw_tile_f1.json and raw_tile_f1.md.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LADDER = ROOT / "results/fidelity/ladder"
TEST_RUNS = ["os_15m_small", "sf_15m_small", "os_15m_full", "sf_15m_full", "os_50m_small", "sf_50m_small",
             "os_50m_full", "sf_50m_full", "os_100m_small", "sf_100m_small", "os_100m_full", "sf_100m_full",
             "os_50m_full_s1", "sf_50m_full_s1", "os_50m_full_s2", "sf_50m_full_s2"]   # make_numbers.TEST_RUNS
FINAL = {"os": 6000000, "sf": 1500032}                                                  # make_numbers.FINAL


def test_json(ladder: Path, run: str) -> Path:
    return ladder / run / "test" / f"{run}_samples_{FINAL[run[:2]]:09d}_dec-a.json"


def row(path: Path) -> dict:
    d = json.loads(path.read_text())
    g, o = d["gap_closed"], d["onestep"]["model_T1"]
    out = {"path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
           "selection": d["selection"]["name"], "n_onestep": d["selection"]["n_onestep"]}
    for form in ("structural", "raw"):
        one = g[f"tile_F1_1m_{form}_T1"]
        twelve = g[f"tile_F1_since_start_12m_{form}"]
        cnt = o[form]
        if abs(cnt["f1"] - one["model"]) > 1e-12:
            raise SystemExit(f"{path}: onestep.model_T1.{form}.f1 {cnt['f1']} differs from gap_closed's {one['model']}")
        out[form] = {"f1_1m": {"model": one["model"], "floor": one["floor"], "copy": one["copy"],
                               "share_closed": one.get("share_closed"),
                               "model_ci95_by_family": cnt.get("f1_ci95_by_family"),
                               "tp": cnt["tp"], "fp": cnt["fp"], "fn": cnt["fn"]},
                     "f1_since_start_12m": {"model": twelve["model"], "floor": twelve["floor"], "copy": twelve["copy"]}}
    return out


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ladder", default=str(LADDER))
    ap.add_argument("--out", default=str(ROOT / "results/analysis"))
    a = ap.parse_args(argv)
    lad = Path(a.ladder)
    rows, missing = {}, []
    for run in TEST_RUNS:
        p = test_json(lad, run)
        if p.exists():
            rows[run] = row(p)
        else:
            missing.append(str(p))
    res = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "question": "is raw (unmerged) changed-tile F1 stored for every run's test selection beside the structural F1?",
           "answer": "yes" if not missing else f"no: {len(missing)} of {len(TEST_RUNS)} test files missing",
           "n_runs": len(rows), "runs": rows, "missing": missing,
           "definitions": {"structural": "tile codes merged along animation cycles and road traffic levels (protocol)",
                           "raw": "tile codes compared as stored",
                           "floor": "the engine under another seed", "copy": "copy-last-state",
                           "model_ci95_by_family": "the fidelity evaluation's 95 % interval, bootstrap over city families",
                           "f1_1m": "changed-tile F1 at one month (T1), one model sample",
                           "f1_since_start_12m": "changed-since-start F1 at 12 months"}}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "raw_tile_f1.json").write_text(json.dumps(res, indent=1))
    ci = lambda c: f"[{c[0]:.3f}, {c[1]:.3f}]" if c else "-"  # noqa: E731
    L = ["# Raw and structural changed-tile F1 on the test selection, final checkpoints", "",
         f"Generated {res['generated']} by `code/scripts/raw_tile_f1.py` from each run's "
         "`results/fidelity/ladder/<run>/test/<run>_samples_<N>_dec-a.json` (`gap_closed`, `onestep.model_T1`). "
         f"Raw F1 stored for every run: **{res['answer']}**. One-month F1 of the model with the evaluation's interval "
         "over city families; floor = the engine under another seed; 12 months = changed since start.", "",
         "| run | transitions | structural 1 month | floor | raw 1 month | floor | structural 12 months | floor | raw 12 months | floor |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for run, r in rows.items():
        s, w = r["structural"], r["raw"]
        L.append(f"| `{run}` | {r['n_onestep']} | {s['f1_1m']['model']:.3f} {ci(s['f1_1m']['model_ci95_by_family'])} | "
                 f"{s['f1_1m']['floor']:.3f} | {w['f1_1m']['model']:.3f} {ci(w['f1_1m']['model_ci95_by_family'])} | "
                 f"{w['f1_1m']['floor']:.3f} | {s['f1_since_start_12m']['model']:.3f} | {s['f1_since_start_12m']['floor']:.3f} | "
                 f"{w['f1_since_start_12m']['model']:.3f} | {w['f1_since_start_12m']['floor']:.3f} |")
    if missing:
        L += ["", "Missing: " + ", ".join(f"`{m}`" for m in missing)]
    (out / "raw_tile_f1.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
