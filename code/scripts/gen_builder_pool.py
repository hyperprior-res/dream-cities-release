#!/usr/bin/env python3
"""Builder pool for best-of-N: scripted-builder plans per held-out start, saved like the calibration files.

For every start state of the split and horizon H: draw N plans, each produced by one scripted builder
(``dc.behaviour.make_policy("builder/<style>")``, style drawn uniformly from ``BUILDER_STYLES`` by the
plan's own generator) playing H months closed-loop in the engine, kept as an open-loop action log with
its forced-disaster column cleared. Each plan is then replayed open-loop under its own evaluation seed,
once with no forced event (``scal_plain``) and once with the recover task's forced event
(``scal_recover``), exactly as ``code/scripts/calibrate_tasks.py`` does for the behaviour mix.

Seeds, per (start, H, j): policy generator ``seed_for("bon-policy", start, H, j)``, closed-loop engine
seed ``seed_for("bon-gen", start, H, j)``, evaluation seed ``seed_for("bon-eval", start, H, j)``.

Output: ``<out-dir>/H<H>/<start_id>.npz`` with ``plans`` (N, H, 25) int16, ``labels`` (N,),
``scal_plain`` and ``scal_recover`` (N, H+1, 20) int64; ``<out-dir>/H<H>/meta.json`` with the counts
that ran. A start whose file exists with N plans is skipped (resumable).

Usage:  python code/scripts/gen_builder_pool.py --horizon 24 --n 1000 --workers 12
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc import tasks as T  # noqa: E402
from dc.behaviour import BUILDER_STYLES, make_policy, rollout_behaviour  # noqa: E402
from dc.engine import PROTO_VERSION, Engine  # noqa: E402
from dc.families import starts  # noqa: E402
from dc.grammar import compile_plan  # noqa: E402
from dc.oracle import replay  # noqa: E402
from dc.seeds import seed_for  # noqa: E402

DEFAULT_OUT = Path("<cache>/audit/builder_pool")
STYLES = tuple(sorted(BUILDER_STYLES))
_ENG = None


def builder_plan(eng: Engine, start_id: str, cty, H: int, j: int):
    """Plan j of a start: (plan int16 (H, 25), label). The forced-disaster column is cleared."""
    rng = np.random.default_rng(seed_for("bon-policy", start_id, H, j))
    style = STYLES[int(rng.integers(len(STYLES)))]
    label = f"builder/{style}"
    plan, _ = rollout_behaviour(eng, cty, make_policy(label), H, seed_for("bon-gen", start_id, H, j), False, rng,
                                record="scalars")
    plan = np.asarray(plan, dtype=np.int16).copy()
    plan[:, 4] = 0
    return plan, label


def _one_start(args):
    global _ENG
    start_id, cty, H, n, out_dir = args
    path = Path(out_dir) / f"{start_id}.npz"
    if path.exists():
        with np.load(path) as z:
            if z["plans"].shape[0] == n:
                return start_id, 0, 0.0, True
    if _ENG is None:
        _ENG = Engine()
    t0 = time.time()
    plans = np.zeros((n, H, 25), dtype=np.int16)
    scal_plain = np.zeros((n, H + 1, 20), dtype=np.int64)
    scal_recover = np.zeros((n, H + 1, 20), dtype=np.int64)
    labels = []
    for j in range(n):
        plan, label = builder_plan(_ENG, start_id, cty, H, j)
        acts, forced = compile_plan(plan)
        assert not forced
        s_eval = seed_for("bon-eval", start_id, H, j)
        scal_plain[j] = replay(_ENG, cty, acts, s_eval).scalars
        scal_recover[j] = replay(_ENG, cty, acts, s_eval, forced=T.forced_for("recover")).scalars
        plans[j] = plan
        labels.append(label)
    tmp = path.with_name(path.stem + ".tmp.npz")
    np.savez_compressed(tmp, plans=plans, labels=np.asarray(labels), scal_plain=scal_plain, scal_recover=scal_recover)
    os.replace(tmp, path)
    return start_id, n * H * 3, time.time() - t0, False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--split", default="heldout")
    ap.add_argument("--starts", default="", help="comma-separated start ids (default: every start of the split)")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT))
    a = ap.parse_args()
    H, n = a.horizon, a.n
    out_dir = Path(a.out_dir) / f"H{H}"
    out_dir.mkdir(parents=True, exist_ok=True)
    want = set(s for s in a.starts.split(",") if s)
    jobs = [(sid, str(p), H, n, str(out_dir)) for sid, fid, p in starts(a.split) if not want or sid in want]
    t0 = time.time()
    months, done, skipped = 0, 0, 0
    with mp.get_context("fork").Pool(max(1, min(a.workers, len(jobs)))) as pool:
        for sid, m, sec, skip in pool.imap_unordered(_one_start, jobs):
            months += m
            done += 1
            skipped += int(skip)
            print(f"{done}/{len(jobs)} {sid} {'skipped (exists)' if skip else f'{m:,} city-months in {sec:.1f} s'}",
                  flush=True)
    sec = time.time() - t0
    meta = {"protocol": PROTO_VERSION, "horizon": H, "n_per_start": n, "split": a.split, "styles": list(STYLES),
            "starts": len(jobs), "starts_skipped": skipped, "engine_city_months_this_run": months,
            "seconds_this_run": round(sec, 1), "workers": a.workers,
            "seeds": {"policy": "seed_for('bon-policy', start, H, j)", "closed_loop": "seed_for('bon-gen', start, H, j)",
                      "eval": "seed_for('bon-eval', start, H, j)"}}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"builder pool: {len(jobs)} starts ({skipped} already present), {n} plans each, H={H}, "
          f"{months:,} engine city-months in {sec:.1f} s -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
