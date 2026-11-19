"""Tests of ``dc.fast`` (CPU, tiny size, model code of the tag ladder-v2 through ``dc.audit``)."""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest
import torch

from dc import audit as A
from dc import fast
from dc import grammar as G
from dc.seeds import seed_for

H = 24


@pytest.fixture(scope="module")
def judge(tmp_path_factory):
    """A tiny three-stage model, written as a checkpoint and loaded by the audit's judge from the tag."""
    from dc import model as Mw            # the working tree's model.py equals the tag's (only used to write weights)
    torch.manual_seed(0)
    cfg = dataclasses.replace(Mw.SIZES["tiny"], bookkeeping=True, bk_width=32, bk_depth=1)
    m = Mw.Emulator(cfg)
    with torch.no_grad():                 # non-zero FiLM so the conditioning path is exercised
        for blk in m.modules():
            if isinstance(blk, Mw.Block):
                blk.film.weight.normal_(0.0, 0.05)
    p = tmp_path_factory.mktemp("tiny") / "tiny.pt"
    torch.save({"model_config": cfg.to_dict(), "model": m.state_dict(), "ema": None, "samples": 0}, p)
    return A.EmulatorJudge(p, device="cpu", chunk=8, buckets=(8,), compile_trunk=False, model_src="ladder-v2")


def _plans(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    inst = A.load_instances(A.TASKS_JSON, horizon=H)[0]
    return inst, A.effective(np.stack([G.random_plan(rng, H, p_noop_macro=0.3) for _ in range(n)]), inst.task, H)


def test_reference_source_is_the_tags(judge):
    """The fused trunk restates the tag's Trunk.forward and Block.forward: their source equals the reference."""
    assert fast._source_sha(judge.model) == fast.LADDER_V2_SOURCE_SHA


def test_refuses_other_source(judge, monkeypatch):
    monkeypatch.setattr(fast, "LADDER_V2_SOURCE_SHA", "0" * 64)
    with pytest.raises(RuntimeError):
        fast.make_fused_trunk(judge.model)


def test_fused_trunk_equals_tag_trunk(judge):
    """Every trunk output of the fused restatement equals the tag's trunk to float32 rounding (CPU, no autocast)."""
    m = judge.model
    inst, plans = _plans(4, 1)
    s0 = judge.state0(inst)
    B = 4
    st = {k: v.expand(B, *v.shape[1:]).contiguous() for k, v in s0.items()}
    r = fast.raster_rows(plans[:, 0], "cpu")
    a = torch.from_numpy(G.action_scalars_batch(plans[:, 0]))
    torch.manual_seed(3)
    z = torch.randn(B, m.cfg.z_dim)
    with torch.no_grad():
        cond = m.cond_mlp(torch.cat([m.cond_input(st, a, r), z], 1))
        args = (st["tile_index"], st["flags"], st["power"], st["half"], st["eighth"], r, cond, st["terrain"], st["com_rate"])
        ref = m.trunk(*args)
        out = fast.make_fused_trunk(m)(*args)
    assert len(ref) == len(out) == 7
    for x, y in zip(ref, out):
        assert x.shape == y.shape and x.dtype == y.dtype
        torch.testing.assert_close(y, x, rtol=1e-5, atol=1e-5)


def test_raster_rows_equals_raster_batch():
    """The raster built with torch equals dc.grammar.raster_batch exactly (random plans, overlapping macros)."""
    rng = np.random.default_rng(11)
    rows = G.clip_plan(np.concatenate([G.random_plan(rng, H, p_noop_macro=p) for p in (0.0, 0.3, 0.9)]))
    got = fast.raster_rows(rows, "cpu").numpy()
    want = G.raster_batch(rows)
    assert got.dtype == want.dtype == np.float32
    np.testing.assert_array_equal(got, want)


def test_rollout_identical_to_audit_adaptor(judge):
    """fast.emulator_rollout (raster on the device) equals dc.audit.emulator_rollout element for element under
    the same seed, with and without the accelerated (fused) trunk."""
    inst, plans = _plans(4, 2)
    s0 = judge.state0(inst)
    m = judge.model
    torch.manual_seed(seed_for("test-fast", 1))
    ref = A.emulator_rollout(m, s0, plans, 2, "cpu", max_batch=8)
    torch.manual_seed(seed_for("test-fast", 1))
    got = fast.emulator_rollout(m, s0, plans, 2, "cpu", max_batch=8)
    np.testing.assert_array_equal(got, ref)
    fast.accelerate(m)
    try:
        assert fast.describe(m)["fused"] and not fast.describe(m)["graphs"]
        torch.manual_seed(seed_for("test-fast", 1))
        acc = fast.emulator_rollout(m, s0, plans, 2, "cpu", max_batch=8)
        for overlay in ("sample", "mean"):          # both decodings, accelerated against the tag's trunk
            torch.manual_seed(seed_for("test-fast", 2))
            a1 = fast.emulator_rollout(m, s0, plans, 2, "cpu", max_batch=8, overlay=overlay)
            object.__setattr__(m, "_trunk_fn", m.trunk)
            torch.manual_seed(seed_for("test-fast", 2))
            a0 = fast.emulator_rollout(m, s0, plans, 2, "cpu", max_batch=8, overlay=overlay)
            fast.accelerate(m)
            np.testing.assert_array_equal(a1, a0)
    finally:
        object.__setattr__(m, "_trunk_fn", m.trunk)
    np.testing.assert_array_equal(acc, ref)


def test_judge_samples_identical(judge):
    """The audit judge's samples are the same with the one-line switches applied (accelerate + fast rollout)."""
    inst, plans = _plans(6, 3)
    ref = judge.samples(inst, plans, 2, ("t", 0))
    orig = A.emulator_rollout
    fast.accelerate(judge.model)
    try:
        A.emulator_rollout = fast.emulator_rollout
        got = judge.samples(inst, plans, 2, ("t", 0))
    finally:
        A.emulator_rollout = orig
        object.__setattr__(judge.model, "_trunk_fn", judge.model.trunk)
    np.testing.assert_array_equal(got, ref)


def test_scalar_stage_restatement_equals_tag(judge):
    """The refused tail lever's restated second stage (its static part split out to be compiled) equals the tag's
    ScalarStage.forward exactly (CPU, uncompiled), on a sampled next state with changed tiles: the restatement is
    exact; what the GPU measurement refused was the compilation (see dc.fast)."""
    import inspect, hashlib, sys
    m = judge.model
    mod = sys.modules[type(m).__module__]
    assert hashlib.sha256(inspect.getsource(mod.ScalarStage.forward).encode()).hexdigest() == fast.SCALAR_STAGE_SOURCE_SHA
    ss = m.scalar_stage
    inst, plans = _plans(4, 4)
    s0 = judge.state0(inst)
    st = {k: v.expand(4, *v.shape[1:]).contiguous() for k, v in s0.items()}
    r = fast.raster_rows(plans[:, 0], "cpu")
    a = torch.from_numpy(G.action_scalars_batch(plans[:, 0]))
    torch.manual_seed(7)
    with torch.no_grad():
        s1 = m.sample_next(st, r, a)
        assert (s1["tile_index"] != st["tile_index"]).any()
        cond_in = m.cond_input(st, a, r)
        pooled = m._dense(st, r, cond_in, torch.zeros(4, m.cfg.z_dim))[4]
        state_x, direct = m.stage_inputs(st)
        ref = ss(pooled, st, s1, r, m.spend_cost, cond_in, state_x, direct)
        got = fast._scalar_stage_forward(ss, fast._scalar_stage_dense(ss))(pooled, st, s1, r, m.spend_cost, cond_in,
                                                                            state_x, direct)
    for x, y in zip(ref, got):
        assert torch.equal(x, y)
