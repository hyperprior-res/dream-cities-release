"""B20: the existing stores are still what the edited generator produces.

For each original split, ``n`` trajectories chosen at random (seeded) are generated again from scratch with the
current ``gen_data.SplitJob`` (closed loop in the engine, as the generation ran) and compared with the stored
record: start, behaviour label, engine seed, disasters flag, the whole action log and the final full-state hash.
Also: the job's generation config equals the stored one (apart from code hashes and provenance, which
``dc.data.generate`` also ignores on a finished store).

    PYTHONPATH=code:hpr-dream .venv/bin/python results/coverage/regen_check.py --n 100 --workers 16
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
sys.path.insert(0, str(ROOT / "code" / "scripts"))

import gen_data as G  # noqa: E402
from dc import data as D  # noqa: E402

_JOB = None
_ENG = None


def _init(name):
    global _JOB, _ENG
    from dc.engine import Engine
    _JOB = G.SplitJob(name, G.RealProvider())
    _ENG = Engine()


def _one(args):
    name, j = args
    st = D.TrajStore(D.DATA_ROOT / name)
    rec = st.record(j)
    out = _JOB.run(int(j), _ENG)
    plan = np.asarray(out["plan"])
    stored = np.asarray(st.plan[rec["first_trans"]:rec["first_trans"] + rec["H"]])
    return {"j": int(j), "plan": bool(np.array_equal(plan, stored)), "hash": int(out["final_hash"]) == rec["final_hash"],
            "label": out["label"] == rec["label"], "seed": int(out["seed"]) == rec["seed"],
            "start": st.starts[int(out["start_idx"])]["start_id"] == rec["start_id"],
            "disasters": bool(out["disasters"]) == rec["disasters"]}


def main() -> None:
    import multiprocessing as mp

    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--splits", default="train_full,heldout_eval,train_eval")
    args = ap.parse_args()
    res = {}
    for name in args.splits.split(","):
        t0 = time.time()
        st = D.TrajStore(D.DATA_ROOT / name)
        job = G.SplitJob(name, G.RealProvider())
        skip = ("content_files", "provenance")
        a = {k: v for k, v in json.loads((st.path / "gen_config.json").read_text()).items() if k not in skip}
        b = {k: v for k, v in D._full_config(job).items() if k not in skip}
        ids = np.sort(np.random.default_rng(G.seed_for("b20-regen", name)).choice(st.n_traj, size=min(args.n, st.n_traj),
                                                                               replace=False))
        with mp.get_context("fork").Pool(args.workers, initializer=_init, initargs=(name,)) as pool:
            rows = pool.map(_one, [(name, int(j)) for j in ids], chunksize=1)
        fields = ("plan", "hash", "label", "seed", "start", "disasters")
        res[name] = {"config_equal": a == b, "config_diff": sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k)),
                     "checked": len(rows), **{f"{f}_equal": int(sum(r[f] for r in rows)) for f in fields},
                     "all_equal": int(sum(all(r[f] for f in fields) for r in rows)), "seconds": round(time.time() - t0, 1)}
        print(f"[regen {name}] {json.dumps(res[name])}", flush=True)
    out = Path(__file__).resolve().parent / "regen_check.json"
    out.write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
