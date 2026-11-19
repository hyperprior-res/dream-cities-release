"""Rollout isolation, ported from the independent review's isolation_test.py (review/emulator_ladder_v1).

For a fixed noise seed the model's sampled outputs on the three evaluation paths

  A. ``Emulator.rollout`` from row 0 of each trajectory with its plan,
  B. ``dc.fidelity.eval_model_rollouts`` (every state ``sample_next`` returns is recorded),
  C. ``dc.fidelity.eval_model_onestep`` (every sampled next state is recorded),

must be bit-identical (NaN-aware) when every observation row the path is not allowed to read is
replaced by garbage (NaN for the float-converted arrays, random codes for tiles and random flags), the
charged build cost is garbage, and ``dc.engine.Engine`` and ``dc.oracle.replay`` raise when touched.
A rollout may read row 0 only; the one-month path may read row t of each selected pair (row t + 1 is
the truth, read for metrics and the teacher-forced log-likelihood, never for sampling).
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc import engine as dce, fidelity as fd, oracle  # noqa: E402
from dc.model import SIZES, Emulator, compute_norm_stats  # noqa: E402
from dc.train import EnginePool  # noqa: E402

CITIES = [ROOT / "data" / "cities" / f"{c}.cty" for c in ("haight", "badnews")]
H, K = 4, 2


@pytest.fixture(scope="module")
def setup():
    trajs = fd.trajectories_from_engine(CITIES, per_city=2, months=H, seed=5)
    pool = EnginePool.generate(CITIES, trajs_per_city=1, months=4, seed=0, device="cpu")
    stats = compute_norm_stats(pool.all_batches(4), 10)
    torch.manual_seed(0)
    m = Emulator(dataclasses.replace(SIZES["tiny"], bookkeeping=True, bk_width=32, bk_depth=1))
    m.set_norm_stats(stats)
    return trajs, m.eval()


def _poisoned(tr: fd.EvalTrajectory, allowed, seed: int) -> fd.EvalTrajectory:
    rng = np.random.default_rng(seed)
    real = tr._rows_fn

    def rows_fn(rows):
        bad = np.array([r not in allowed for r in rows])
        out = {}
        for k, v in real(rows).items():
            v = v.copy()
            if k == "tile_index":
                v[bad] = rng.integers(0, 1024, size=v[bad].shape)
            elif v.dtype == bool:
                v[bad] = rng.integers(0, 2, size=v[bad].shape).astype(bool)
            else:
                v = v.astype(np.float64)
                v[bad] = np.nan
            out[k] = v
        return out

    return fd.EvalTrajectory(tr.start_path, tr.actions, tr.forced, tr.seed, tr.disasters, tr.family, tr.traj_id,
                             tr._raster_fn, tr._act_fn, rows_fn, label=tr.label,
                             cost_fn=lambda ts: rng.integers(-10**9, 10**9, size=len(ts)).astype(np.float64))


class _Recorder:
    def __init__(self, m):
        self.m, self.orig, self.out = m, m.sample_next, []

    def __enter__(self):
        def wrapped(*a, **kw):
            s = self.orig(*a, **kw)
            self.out.append({k: v.detach().clone() for k, v in s.items()})
            return s
        self.m.sample_next = wrapped
        return self

    def __exit__(self, *e):
        del self.m.sample_next


def _same(a: torch.Tensor, b: torch.Tensor) -> bool:
    if a.shape != b.shape or a.dtype != b.dtype:
        return False
    if a.is_floating_point():
        return bool(torch.equal(torch.isnan(a), torch.isnan(b)) and torch.equal(torch.nan_to_num(a), torch.nan_to_num(b)))
    return bool(torch.equal(a, b))


def _run(model, trajs, trajs_one, plans, pairs, dec):
    T, ov = fd.DECODINGS[dec]
    out = []
    s0 = fd._stack_states([trajs[i].state([0], "cpu") for i in plans])
    raster = torch.from_numpy(np.stack([trajs[i].raster(list(range(H))) for i in plans]))
    act = torch.from_numpy(np.stack([trajs[i].act(list(range(H))) for i in plans]))
    torch.manual_seed(1234)
    sc, fin = model.rollout(s0, raster, act, K=K, temperature=T, overlay=ov)
    out.append({"scalars": sc, **fin})
    with _Recorder(model) as rec:
        fd.eval_model_rollouts(model, trajs, plans, "cpu", H=H, K=K, batch_plans=2, temperature=T, seed=0,
                               horizons=(1, H), overlay=ov)
    out += rec.out
    with _Recorder(model) as rec:
        fd.eval_model_onestep(model, trajs_one, pairs, "cpu", batch=4, seed=0)
    out += rec.out
    return out


@pytest.mark.parametrize("dec", ["a", "b", "c"])
def test_rollouts_read_only_their_start_rows(setup, monkeypatch, dec):
    trajs, model = setup
    plans = [0, 1, 3]
    pairs = [(0, 1), (1, 3), (2, 0), (3, 2)]
    clean = _run(model, trajs, trajs, plans, pairs, dec)

    def boom(*a, **k):
        raise RuntimeError("engine touched during an isolated evaluation")
    monkeypatch.setattr(dce.Engine, "__init__", boom)
    monkeypatch.setattr(oracle, "replay", boom)
    # rollouts may read row 0 of each trajectory, the one-month path row t of each of its pairs
    roll = [_poisoned(tr, {0}, seed=10 + i) for i, tr in enumerate(trajs)]
    one = [_poisoned(tr, {t for j, t in pairs if j == i}, seed=20 + i) for i, tr in enumerate(trajs)]
    dirty = _run(model, roll, one, plans, pairs, dec)
    with pytest.raises(RuntimeError):
        dce.Engine()
    assert len(clean) == len(dirty)
    bad = [(n, k) for n, (p, q) in enumerate(zip(clean, dirty)) for k in p if not _same(p[k], q[k])]
    assert not bad, bad
    assert all(not (v.is_floating_point() and bool(torch.isnan(v).any())) for s in dirty for v in s.values())
