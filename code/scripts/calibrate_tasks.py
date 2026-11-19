#!/usr/bin/env python3
"""Calibrate task thresholds on the engine under the behaviour mix (brief, section 6, "Tasks and the verdict").

For every held-out start state and horizon H: draw N behaviour-mix plans (each produced by a policy
playing closed-loop in the engine, then kept as an open-loop action log with its forced-disaster
column cleared), replay each open-loop under a fresh seed with the task's own forced disaster, and
choose theta per task on the first n_fit plans so the engine's success rate is about 0.35. The
remaining n_val plans give an independent estimate of the base rate.

The plans and their engine trajectories are saved: they are the behaviour distribution every later
stage needs (confusion rates for the noise floor, calibration scores, search initialisation).

Usage:  python code/scripts/calibrate_tasks.py --horizon 24 --workers 22 --out-dir results/calibration
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc import tasks as T  # noqa: E402
from dc.behaviour import rollout_behaviour, sample_behaviour  # noqa: E402
from dc.engine import PROTO_VERSION, Engine  # noqa: E402
from dc.families import load_manifest, starts  # noqa: E402
from dc.grammar import compile_plan  # noqa: E402
from dc.oracle import replay  # noqa: E402
from dc.seeds import seed_for  # noqa: E402

_ENG = None


def _one_start(args):
    global _ENG
    start_id, family_id, cty, H, n, out_dir = args
    if _ENG is None:
        _ENG = Engine()
    eng = _ENG
    plans = np.zeros((n, H, 25), dtype=np.int16)
    labels = []
    scal_plain = np.zeros((n, H + 1, 20), dtype=np.int64)     # no forced disaster (grow, solvent, treasury, power)
    scal_recover = np.zeros((n, H + 1, 20), dtype=np.int64)   # the recover task's forced disaster
    for j in range(n):
        rng = np.random.default_rng(seed_for("cal-policy", start_id, H, j))
        policy, label = sample_behaviour(rng)
        plan, _ = rollout_behaviour(eng, cty, policy, H, seed_for("cal-gen", start_id, H, j), False, rng)
        plan = np.asarray(plan, dtype=np.int16).copy()
        plan[:, 4] = 0                                         # task plans carry no forced disasters of their own
        actions, _ = compile_plan(plan)
        s_eval = seed_for("cal-eval", start_id, H, j)
        scal_plain[j] = replay(eng, cty, actions, s_eval).scalars
        scal_recover[j] = replay(eng, cty, actions, s_eval, forced=T.forced_for("recover")).scalars
        plans[j] = plan
        labels.append(label)
    np.savez_compressed(Path(out_dir) / f"{start_id}.npz", plans=plans, labels=np.asarray(labels),
                        scal_plain=scal_plain, scal_recover=scal_recover)
    return start_id, family_id, scal_plain, scal_recover


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--n-fit", type=int, default=600)
    ap.add_argument("--n-val", type=int, default=400)
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--split", default="heldout")
    ap.add_argument("--out-dir", default=str(ROOT / "results" / "calibration"))
    ap.add_argument("--manifest", default="", help="families manifest whose starts are calibrated (default "
                    "data/families.json; data/families_x.json for the held-out extension)")
    ap.add_argument("--tasks-out", default="", help="tasks file written (default data/tasks_H<H>.json)")
    a = ap.parse_args()
    H, n = a.horizon, a.n_fit + a.n_val
    out_dir = Path(a.out_dir) / f"H{H}"
    out_dir.mkdir(parents=True, exist_ok=True)
    st = starts(a.split, load_manifest(a.manifest)) if a.manifest else starts(a.split)
    jobs = [(sid, fid, str(p), H, n, str(out_dir)) for sid, fid, p in st]
    if a.manifest:          # never overwrite another manifest's calibration file
        clash = [j[0] for j in jobs if (out_dir / f"{j[0]}.npz").exists()]
        if clash:
            raise SystemExit(f"calibration files exist for {clash[:5]} ... in {out_dir}")
    t0 = time.time()
    instances = []
    with mp.get_context("fork").Pool(min(a.workers, len(jobs))) as pool:
        for start_id, family_id, plain, recover in pool.imap_unordered(_one_start, jobs):
            for task in T.TASKS:
                sc = recover if task == "recover" else plain
                fit, val = sc[: a.n_fit], sc[a.n_fit:]
                theta, rate_fit, feas = T.calibrate_theta(task, fit)
                rate_val = float(np.mean(T.verdict(task, val, theta))) if len(val) else None
                ok = T.feasible(task, sc)
                st = T.statistic(task, sc)
                sd = float(np.std(st[ok])) if ok.sum() > 1 else float(np.std(st))
                inst = T.TaskInstance(
                    family_id=family_id, start_id=start_id, task=task, horizon=H, theta=theta,
                    base_rate_fit=rate_fit, base_rate_val=rate_val, n_fit=a.n_fit, n_val=a.n_val,
                    feasible_rate=feas, in_band=bool(T.BAND[0] <= (rate_val if rate_val is not None else rate_fit) <= T.BAND[1]),
                    stat_sd=sd if sd > 0 else 1.0,
                )
                instances.append(inst.to_dict())
    instances.sort(key=lambda d: (d["start_id"], T.TASKS.index(d["task"])))
    months = len(jobs) * n * H * 3
    meta = {"protocol": PROTO_VERSION, "horizon": H, "n_fit": a.n_fit, "n_val": a.n_val, "split": a.split,
            "target": T.TARGET_BASE_RATE, "band": list(T.BAND), "engine_city_months": months,
            "seconds": round(time.time() - t0, 1)}
    if a.manifest:
        meta["manifest"] = str(a.manifest)
    (ROOT / "data").mkdir(exist_ok=True)
    out = Path(a.tasks_out) if a.tasks_out else ROOT / "data" / f"tasks_H{H}.json"
    out.write_text(json.dumps({"meta": meta, "instances": instances}, indent=1))
    # printed report
    print(f"calibrated {len(instances)} task instances on {len(jobs)} starts, H={H}, {n} plans each, "
          f"{months:,} engine city-months in {meta['seconds']} s")
    print("task        in band   base rate (validation): mean   min    max   | feasible share: mean  min")
    for task in T.TASKS:
        sub = [d for d in instances if d["task"] == task]
        r = np.array([d["base_rate_val"] for d in sub]); f = np.array([d["feasible_rate"] for d in sub])
        print(f"{task:10s}  {sum(d['in_band'] for d in sub):3d}/{len(sub):<3d}                        "
              f"{r.mean():.3f}  {r.min():.3f}  {r.max():.3f}  |                 {f.mean():.3f} {f.min():.3f}")
    bad = [d for d in instances if not d["in_band"]]
    print(f"out of band: {len(bad)}")
    for d in bad[:40]:
        print(f"  {d['start_id']:14s} {d['task']:9s} val={d['base_rate_val']:.3f} fit={d['base_rate_fit']:.3f} feasible={d['feasible_rate']:.3f} theta={d['theta']:.4g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
