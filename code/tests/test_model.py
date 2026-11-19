"""Tests for the emulator, its training loop and the fidelity metrics (CPU, real engine observations)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc.engine import SC_POP, SC_TAX, SC_TIME, MonthAction  # noqa: E402
from dc.fidelity import (  # noqa: E402
    TileNN, engine_floor_onestep, engine_floor_rollouts, eval_baselines_onestep, eval_model_onestep,
    eval_model_rollouts, horizon_errors, pick_plans, pick_transitions, prf, tile_change_counts,
    trajectories_from_engine,
)
from dc.model import (  # noqa: E402
    EIGHTH_HI, EIGHTH_LO, INF, N_CODES, SIZES, Emulator, compute_norm_stats, dlogistic_mix_logp,
    gated_logp, month_features,
)
from dc.train import EnginePool, TrainConfig, Trainer, lr_at, milestones, sha256_file  # noqa: E402

CITIES = [ROOT / "data" / "cities" / f"{c}.cty" for c in ("haight", "badnews")]


@pytest.fixture(scope="module")
def pool():
    return EnginePool.generate(CITIES, trajs_per_city=1, months=6, seed=0, device="cpu")


@pytest.fixture(scope="module")
def stats(pool):
    return compute_norm_stats(pool.all_batches(4), 10)


@pytest.fixture()
def tiny(stats):
    torch.manual_seed(0)
    m = Emulator("tiny")
    m.set_norm_stats(stats)
    return m


def test_param_counts():
    for size, target in (("15m", 15e6), ("50m", 50e6), ("100m", 100e6)):
        m = Emulator(size)
        n = m.num_parameters()
        print(size, n)
        assert abs(n - target) / target <= 0.10, (size, n)
        assert m.safe_batch * 120 * 100 * m.cfg.d0 < 2**31 <= 2 * m.safe_batch * 120 * 100 * m.cfg.d0


def test_loader_format_and_identities(pool):
    s0, r, a, s1 = next(pool.batches(4, seed=0))
    assert s0["tile_index"].dtype == torch.int64 and s0["tile_index"].shape == (4, 120, 100)
    assert s0["flags"].shape == (4, 5, 120, 100) and s0["power"].shape == (4, 120, 100)
    assert s0["half"].shape == (4, 5, 60, 50) and s0["eighth"].shape == (4, 3, 15, 13)
    assert s0["scalars"].shape == (4, 20) and r.shape == (4, 15, 120, 100) and a.shape == (4, 11)
    assert int(s0["tile_index"].max()) < 1024
    m = Emulator("tiny")
    assert int(m.derived_violations(s0, a, s1).sum()) == 0


def test_norm_stats_in_state_dict(stats, tiny):
    assert int(stats["n"]) == 12 and bool((stats["delta_scale"] >= 1).all())
    sd = tiny.state_dict()
    for k in ("cond_mean", "cond_std", "delta_scale", "norm_n"):
        assert k in sd
    assert tiny.norm_ready


def test_month_features():
    f = month_features(torch.tensor([0.0, 4.0, 47.0, 48.0, 4839.0]))
    assert f.shape == (5, 18)
    assert torch.allclose(f[0], f[3])
    assert int(f[2, 2:14].argmax()) == 11 and int(f[2, 14:].argmax()) == 3


def test_dlogistic_normalises():
    torch.manual_seed(0)
    for lo, hi in ((0.0, 255.0), (-200.0, 200.0)):
        x = torch.arange(int(lo), int(hi) + 1).float()
        lpi, mu, ls = torch.randn(3), torch.randn(3) * 50, torch.randn(3) + 2
        lp = dlogistic_mix_logp(x, lpi.expand(len(x), 3), mu.expand(len(x), 3), ls.expand(len(x), 3),
                                torch.full_like(x, lo), torch.full_like(x, hi))
        assert abs(float(lp.exp().sum()) - 1.0) < 1e-4
        g = gated_logp(x, torch.full_like(x, 17.0), torch.full_like(x, 0.3), lp)
        assert abs(float(g.exp().sum()) - 1.0) < 1e-4
    # unbounded, sharp and wide components
    x = torch.arange(-20000, 20001).float()
    lpi, mu, ls = torch.tensor([0.0, 1.0]), torch.tensor([4.0, 300.0]), torch.tensor([-6.0, 6.0])
    lp = dlogistic_mix_logp(x, lpi.expand(len(x), 2), mu.expand(len(x), 2), ls.expand(len(x), 2),
                            torch.full_like(x, -INF), torch.full_like(x, INF))
    assert abs(float(lp.exp().sum()) - 1.0) < 1e-3


def test_tile_distribution_is_proper(pool, tiny):
    s0, r, a, s1 = next(pool.batches(2, seed=1))
    with torch.no_grad():
        cond_in = tiny.cond_input(s0, a, r)
        feat, dense, *_ = tiny._dense(s0, r, cond_in, torch.zeros(2, 32))
        for (b, x, y) in ((0, 3, 4), (1, 60, 50), (1, 119, 99)):
            g = torch.sigmoid(dense[b, x, y, 0].float())
            cur = s0["tile_index"][b, x, y]
            cat = torch.softmax(tiny._cat_logits(feat[b, x, y][None], cur[None]), -1)[0]
            assert float(cat[cur]) == 0.0
            assert abs(float((1 - g) + g * cat.sum()) - 1.0) < 1e-5


def test_logprob_terms(pool, tiny):
    batch = next(pool.batches(3, seed=2))
    lp = tiny.log_prob(batch, k_iw=2)
    for k in tiny.recon_terms + ("kl", "elbo", "iw_bound"):
        assert lp[k].shape == (3,) and torch.isfinite(lp[k]).all(), k
    assert (lp["kl"] >= 0).all() and (lp["derived_viol"] == 0).all()
    rec = sum(lp[k] for k in tiny.recon_terms)
    assert torch.allclose(lp["elbo"], rec - lp["kl"])


def test_sample_next_format(pool, tiny):
    s0, r, a, s1 = next(pool.batches(3, seed=3))
    for T in (1.0, 0.0, 2.0):
        ns = tiny.sample_next(s0, r, a, temperature=T)
        for k, v in s0.items():
            assert ns[k].shape == v.shape and ns[k].dtype == v.dtype, k
        assert int(ns["tile_index"].min()) >= 0 and int(ns["tile_index"].max()) < N_CODES
        assert set(ns["flags"].unique().tolist()) <= {0.0, 1.0} and set(ns["power"].unique().tolist()) <= {0.0, 1.0}
        assert float(ns["half"].min()) >= 0 and float(ns["half"].max()) <= 255
        assert torch.equal(ns["half"], ns["half"].round()) and torch.equal(ns["eighth"], ns["eighth"].round())
        for c in range(3):
            assert float(ns["eighth"][:, c].min()) >= EIGHTH_LO[c] and float(ns["eighth"][:, c].max()) <= EIGHTH_HI[c]
        sc = ns["scalars"].double()
        assert torch.equal(sc, sc.round())
        assert torch.equal(sc[:, SC_TAX], (a[:, 0].double() * 20).round())
        assert torch.equal(sc[:, SC_TIME], s0["scalars"][:, SC_TIME].double() + 4)
        assert torch.equal(sc[:, SC_POP], 20 * (sc[:, 6] + 8 * (sc[:, 7] + sc[:, 8])))
    z = torch.zeros(3, 32)
    m1 = tiny.sample_next(s0, r, a, z=z, temperature=0.0)
    m2 = tiny.sample_next(s0, r, a, z=z, temperature=0.0)
    assert all(torch.equal(m1[k], m2[k]) for k in m1)
    chunked = tiny.sample_next(s0, r, a, z=z, temperature=0.0, max_batch=2)
    assert all(torch.equal(m1[k], chunked[k]) for k in m1)


def test_rollout(pool, tiny):
    s0, r, a, _ = next(pool.batches(2, seed=4))
    H, K = 3, 4
    R = r[:, None].repeat(1, H, 1, 1, 1)
    A = a[:, None].repeat(1, H, 1)
    traj, fin = tiny.rollout(s0, R, A, K=K)
    assert traj.shape == (2, K, H + 1, 20) and fin["tile_index"].shape == (2 * K, 120, 100)
    assert torch.equal(traj[:, :, 0], s0["scalars"].double()[:, None].expand(2, K, 20))
    assert torch.equal(traj[:, :, -1, SC_TIME], s0["scalars"][:, None, SC_TIME].double().expand(2, K) + 4 * H)
    traj2, _ = tiny.rollout(s0, lambda h: R[:, h], A, K=1)
    assert traj2.shape == (2, 1, H + 1, 20)


def _trainer(tmp_path, stats, **kw):
    cfg = TrainConfig(size="tiny", samples=kw.pop("samples", 64), batch_size=4, compile=False, lr=3e-3,
                      log_every=2, resume_every_s=1e9, **kw)
    return Trainer(cfg, tmp_path, "cpu", data_info={"source": "test"}, norm_stats=stats)


def test_training_reduces_loss(tmp_path, pool, stats):
    torch.manual_seed(0)
    tr = _trainer(tmp_path, stats, samples=10_000, kl_warmup=0.0, warmup_frac=0.0)
    batch = next(pool.batches(4, seed=5))
    first = float(tr.train_step(batch)["loss"])
    for _ in range(40):
        last = float(tr.train_step(batch)["loss"])
    assert last < 0.7 * first, (first, last)
    assert tr.samples == 41 * 4


def test_checkpoint_resume_and_milestones(tmp_path, pool, stats):
    torch.manual_seed(0)
    a = _trainer(tmp_path / "a", stats, samples=24, save_samples=(8,))
    a.run(pool.batches(4, seed=6))
    names = sorted(p.name for p in (tmp_path / "a").glob("samples_*.pt"))
    assert names == ["samples_000000008.pt", "samples_000000012.pt", "samples_000000024.pt"]
    for n in names:
        p = tmp_path / "a" / n
        assert (tmp_path / "a" / (n + ".sha256")).read_text().split()[0] == sha256_file(p)
        ck = torch.load(p, weights_only=False)
        assert ck["samples"] == int(n[8:17]) and ck["data"] == {"source": "test"} and "commit" in ck["git"]
    # resume: a fresh trainer picks up the saved state and continues identically
    b = _trainer(tmp_path / "a", stats, samples=24, save_samples=(8,))
    assert b.resume(tmp_path / "a" / "latest.pt") and b.samples == 24 and b.step == 6
    for pa, pb in zip(a.model.parameters(), b.model.parameters()):
        assert torch.equal(pa, pb)
    batch = next(pool.batches(4, seed=7))
    torch.manual_seed(1)
    a.train_step(batch)
    torch.manual_seed(1)
    b.train_step(batch)
    for pa, pb in zip(a.model.parameters(), b.model.parameters()):
        assert torch.allclose(pa, pb, atol=1e-6)


def test_selfforce_step(tmp_path, pool, stats):
    torch.manual_seed(0)
    tr = _trainer(tmp_path, stats, mode="selfforce", sf_k=3, sf_tf_ratio=0.0)
    st = tr.train_step(next(pool.multistep_batches(2, 3, seed=8)))
    assert st["sf_unroll"] in (1, 2) and math.isfinite(float(st["loss"])) and tr.samples == 2


def test_schedule():
    cfg = TrainConfig(samples=1000, batch_size=10, lr=1.0, warmup_frac=0.1, min_lr_frac=0.05,
                      save_samples=(150, 300))
    assert lr_at(cfg, 0) == pytest.approx(0.1)
    assert lr_at(cfg, 100) == pytest.approx(1.0)
    assert lr_at(cfg, 1000) == pytest.approx(0.05)
    assert milestones(cfg) == [150, 300, 500, 1000]


def test_tile_counts_and_prf():
    cur = torch.zeros(1, 4, 4, dtype=torch.long)
    true = cur.clone(); true[0, 0, 0] = 5; true[0, 1, 1] = 6; true[0, 2, 2] = 7
    pred = cur.clone(); pred[0, 0, 0] = 5; pred[0, 1, 1] = 9; pred[0, 3, 3] = 1
    c = tile_change_counts(cur, pred, true)
    assert c.tolist() == [[1, 2, 2]]
    r = prf(c.numpy())
    assert r["precision"] == pytest.approx(1 / 3) and r["recall"] == pytest.approx(1 / 3) and r["f1"] == pytest.approx(1 / 3)
    copy = prf(tile_change_counts(cur, cur, true).numpy())
    assert copy["f1"] == 0.0 and copy["recall"] == 0.0 and math.isnan(copy["precision"])


def test_horizon_errors():
    rng = np.random.default_rng(0)
    true = rng.integers(0, 1000, (5, 20)).astype(float)
    start = true + 10
    pred = np.repeat(true[:, None], 3, 1) + 5
    e = horizon_errors(pred, true, start)
    assert e["scalars"]["funds"]["ratio_sample"] == pytest.approx(0.5)


def test_fidelity_end_to_end(pool, tiny):
    trajs = trajectories_from_engine(CITIES, per_city=1, months=3, seed=1)
    pairs = pick_transitions(trajs, 4, seed=0)
    nn = TileNN().fit(pool.all_batches(4), 12)
    base = eval_baselines_onestep(trajs, pairs, nn, "cpu")
    for kind in ("raw", "structural"):
        assert base["copy"][kind]["f1"] == 0.0 and 0.0 <= base["nn_mode"][kind]["f1"] <= 1.0
    res = eval_model_onestep(tiny, trajs, pairs, "cpu", batch=2)
    assert 0.0 <= res["model_T1"]["raw"]["recall"] <= 1.0 and 0.0 <= res["model_T1"]["structural"]["recall"] <= 1.0
    plans = pick_plans(trajs, 2, H=3, seed=0)
    ro = eval_model_rollouts(tiny, trajs, plans, "cpu", H=3, K=2, horizons=(1, 3))
    assert set(ro) >= {"h1", "h3"} and set(ro["h3"]["tile_since_start"]) == {"raw", "structural"}
    fl = engine_floor_onestep(trajs, pairs)
    assert fl["prefix_mismatches"] == 0 and fl["n_transitions"] == 4
    # structural changes are a subset of raw changes
    assert fl["tile"]["structural"]["tp"] + fl["tile"]["structural"]["fn"] <= fl["tile"]["raw"]["tp"] + fl["tile"]["raw"]["fn"]
    fr = engine_floor_rollouts(trajs, plans, H=3, horizons=(1, 3))
    assert fr["h3"]["scalars"]["city_time"]["mae_sample"] == 0.0 and "structural" in fr["h1"]["tile_since_start"]


def test_canonical_table():
    from dc.fidelity import canonical_table, engine_animation_table
    t = canonical_table()
    nxt = engine_animation_table()
    assert t.shape == (1024,) and bool((t <= np.arange(1024)).all()) and bool((t[t] == t).all())
    assert bool((t == t[nxt]).all())                          # animation successors share a class
    for s in range(16):                                       # light and heavy traffic -> same shape, no traffic
        assert {int(t[c]) for c in (64 + s, 80 + s, 96 + s, 112 + s, 128 + s, 144 + s, 160 + s, 176 + s, 192 + s)} == {64 + s}
    assert set(t[56:64].tolist()) == {56} and t[852] == 621 and t[244] == 244 and t[0] == 0


def test_canonical_road_traffic_on_engine():
    """A road tile whose only change in a month is its traffic level counts as unchanged."""
    from dc.engine import Engine, LOMASK
    from dc.fidelity import canonical_table, canon
    from dc.oracle import replay
    t = canonical_table()
    eng = Engine()
    rp = replay(eng, CITIES[0], [MonthAction()] * 6, seed=3, record="full")
    idx = np.stack([o.tiles & LOMASK for o in rp.states]).astype(np.int64)
    a, b = idx[:-1], idx[1:]
    road = (a >= 64) & (a < 208) & (b >= 64) & (b < 208) & (a != b)
    same = road & (((a - 64) & 15) == ((b - 64) & 15))
    assert int(same.sum()) > 0
    assert bool((t[a[same]] == t[b[same]]).all()) and bool((t[a[road & ~same]] != t[b[road & ~same]]).all())
    cur, nxt_ = torch.from_numpy(a[:1]), torch.from_numpy(b[:1])
    m = tile_change_counts(canon(cur), canon(cur), canon(nxt_))      # copy-last-state, structurally
    assert int(m[0, 2]) == int((t[a[0]] != t[b[0]]).sum())


def test_spend_features(pool, tiny):
    s0, _, a, _ = next(pool.batches(2, seed=9))
    r = torch.zeros(2, 15, 120, 100)
    r[0, 8, 10, 10:20] = 1.0                 # ten road tiles: 10 calls x 10
    r[1, 0, 30:36, 30:33] = 1.0              # two residential zones: 2 calls x 100
    f = tiny.spend_features(s0, r) * 10.0
    assert f.shape == (2, 17)
    assert float(f[0, 8].expm1()) == pytest.approx(100.0, rel=1e-4) and float(f[0, 15].expm1()) == pytest.approx(100.0, rel=1e-4)
    assert float(f[1, 0].expm1()) == pytest.approx(200.0, rel=1e-4) and float(f[1, 15].expm1()) == pytest.approx(200.0, rel=1e-4)
    assert torch.allclose(f[:, 16], torch.log1p(s0["scalars"][:, 0].clamp(min=0)))
    with pytest.raises(ValueError):
        tiny.cond_input(s0, a)


def test_overlay_mean_decoding_and_old_config(pool, tiny, stats):
    import dataclasses
    s0, r, a, _ = next(pool.batches(2, seed=10))
    z = torch.randn(2, 32)
    m1 = tiny.sample_next(s0, r, a, z=z, overlay="mean")
    m2 = tiny.sample_next(s0, r, a, z=z, overlay="mean")
    assert torch.equal(m1["half"], m2["half"]) and torch.equal(m1["eighth"], m2["eighth"])
    assert float(m1["half"].min()) >= 0 and float(m1["half"].max()) <= 255
    assert float(m1["eighth"][:, 0].abs().max()) <= 200 and float(m1["eighth"][:, 1:].min()) >= 0
    old = Emulator(dataclasses.replace(SIZES["tiny"], spend_features=False, scalar_stage="pooled", ledger=False))
    old.set_norm_stats(stats)
    assert "spend_cost" not in old.state_dict() and "ledger_mean" not in old.state_dict()
    ns = old.sample_next({k: v for k, v in s0.items() if k not in ("ledger", "terrain", "com_rate")}, r, a)
    assert ns["tile_index"].shape == s0["tile_index"].shape


def test_scalar_stage(pool, tiny):
    """Second stage: unchanged map -> zero changed-tile contributions; scalar terms finite and depend on
    the next spatial state; budget window from city_time."""
    from dc.train import budget_window
    s0, r, a, s1 = next(pool.batches(3, seed=11))
    ss = tiny.scalar_stage
    with torch.no_grad():
        torch.nn.init.normal_(ss.delta_skip.weight)               # make the tables non-zero for the check
        ci = tiny.cond_input(s0, a, r)
        feat, dense, hp, ep, pooled, tp, cp, cond_in = tiny._dense(s0, r, ci, torch.zeros(3, 32))
        sx, dr = tiny.stage_inputs(s0)
        par, skip = ss(pooled, s0, s0, r, tiny.spend_cost, cond_in, sx, dr)
        assert torch.equal(skip, torch.zeros_like(skip))
        par2, skip2 = ss(pooled, s0, s1, r, tiny.spend_cost, cond_in, sx, dr)
        assert bool((s1["tile_index"] != s0["tile_index"]).any()) and not torch.equal(skip2, torch.zeros_like(skip2))
        assert not torch.equal(par, par2)
    lp = tiny.log_prob((s0, r, a, s1))
    assert torch.isfinite(lp["scalars"]).all()
    assert budget_window(torch.tensor([44.0, 47.0, 48.0, 4843.0, 4844.0])).tolist() == [True, True, False, False, True]


def test_ledger_state_and_sampling(pool, tiny, stats):
    from dc.engine import LG, NUM_LEDGER
    from dc.model import LEARNED_LEDGER, LEDGER_BOUNDS
    s0, r, a, s1 = next(pool.batches(4, seed=12))
    assert s0["ledger"].shape == (4, NUM_LEDGER) and s0["terrain"].shape == (4, 30, 25) and s0["com_rate"].shape == (4, 15, 13)
    assert "ledger_delta_scale" in stats and int(tiny.derived_violations(s0, a, s1).sum()) == 0
    # row 0 of each trajectory carries the trajectory's disaster switch (Replay.ledger), constant along it
    L = pool.obs["ledger"][:, LG["disasters"]]
    for st in pool.traj_start.tolist():
        row0 = int(pool.src[st])
        assert torch.equal(L[row0:row0 + pool.months + 1], L[row0].expand(pool.months + 1))
    lp = tiny.log_prob((s0, r, a, s1))
    for k in ("ledger", "terrain", "com_rate", "lg_res_hist1", "lg_road_fund"):
        assert torch.isfinite(lp[k]).all(), k
    ns = tiny.sample_next(s0, r, a)
    assert ns["ledger"].shape == s0["ledger"].shape and ns["terrain"].shape == s0["terrain"].shape
    assert torch.equal(ns["ledger"][:, LG["sim_cycle"]], torch.remainder(s0["ledger"][:, LG["sim_cycle"]] + 4, 1024))
    assert bool((ns["ledger"][:, LG["initial_eval"]] == 0).all())
    assert torch.equal(ns["ledger"][:, LG["disasters"]], s0["ledger"][:, LG["disasters"]])
    for i, (lo, hi) in LEDGER_BOUNDS.items():
        v = ns["ledger"][:, i]
        assert (lo is None or float(v.min()) >= lo) and (hi is None or float(v.max()) <= hi)
    assert float(ns["com_rate"].min()) >= -64 and float(ns["com_rate"].max()) <= 64
    assert float(ns["terrain"].min()) >= 0 and float(ns["terrain"].max()) <= 255


def test_micro_batch_step(tmp_path, pool, stats):
    torch.manual_seed(0)
    tr = _trainer(tmp_path, stats, micro_batch=2)
    st = tr.train_step(next(pool.batches(4, seed=13)))
    assert tr.samples == 4 and math.isfinite(float(st["loss"]))


def test_bookkeeping_stage(tmp_path, pool, stats):
    import dataclasses
    import importlib.util
    from dc.engine import LG, SC_TIME, TOOL_COSTS
    from dc.model import next_map_summary
    from dc.train import BookData
    # the cache builder's numpy summary equals the model's torch summary on engine states
    spec = importlib.util.spec_from_file_location("bkdiag", ROOT / "code/scripts/bookkeeping_diag.py")
    bkdiag = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bkdiag)
    s0, r, a, s1 = next(pool.batches(4, seed=14))
    tiles = (s1["tile_index"].numpy().astype(np.uint16) | (s1["flags"][:, 0].numpy().astype(np.uint16) << 10))

    class _St:
        pass
    st = _St()
    st.tiles = tiles.view(np.int16)
    st.half = s1["half"].numpy().astype(np.uint8)
    bkdiag._ST = st
    ref = bkdiag._chunk(np.arange(4))
    assert np.allclose(ref, next_map_summary(s1).numpy())
    # a tiny model with the third stage: terms, a training step with its own updates, sampling
    torch.manual_seed(0)
    cfg = TrainConfig(size="tiny", samples=64, batch_size=4, compile=False, lr=3e-3, log_every=2, resume_every_s=1e9,
                      model_overrides={"bookkeeping": True, "bk_width": 32, "bk_depth": 1}, bk_updates=2, bk_batch=8)
    m0 = Emulator(dataclasses.replace(SIZES["tiny"], bookkeeping=True, bk_width=32, bk_depth=1))
    m0.set_norm_stats(stats)
    book = BookData.from_pool(pool, m0)
    tr = Trainer(cfg, tmp_path, "cpu", norm_stats=stats, book_data=book)
    assert float(tr.model.cost_scale) >= 1.0
    lp = tr.model.log_prob((s0, r, a, s1))
    for k in ("build_cost", "scalars", "ledger", "sc_res_valve", "lg_res_hist1"):
        assert torch.isfinite(lp[k]).all(), k
    st_ = tr.train_step((s0, r, a, s1))
    assert tr.samples == 4 and tr.bk_samples == 16 and math.isfinite(float(st_["nll_bk"]))
    ns = tr.model.sample_next(s0, r, a)
    assert torch.isfinite(ns["scalars"]).all() and torch.isfinite(ns["ledger"]).all()
    assert torch.equal(ns["ledger"][:, LG["sim_cycle"]], torch.remainder(s0["ledger"][:, LG["sim_cycle"]] + 4, 1024))
    assert torch.equal(ns["scalars"][:, SC_TIME], s0["scalars"][:, SC_TIME] + 4)


def test_censored_likelihood_is_the_sampler():
    """Sampling then pinning to the bounds draws exactly the censored distribution that is trained."""
    from dc.model import censor_limits, censored_next, dlogistic_mix_sample
    torch.manual_seed(0)
    bounds = ((0.0,), (10.0,))
    lo_d, hi_d = censor_limits(torch.tensor([[3.0]]), bounds)              # value 3 in [0, 10]: d in [-3, 7]
    assert float(lo_d) == -3.0 and float(hi_d) == 7.0
    lpi, mu, ls = torch.tensor([0.0, 0.5]), torch.tensor([-4.0, 9.0]), torch.tensor([1.0, 0.5])
    sup = torch.arange(-3, 8).float()
    n = len(sup)
    lp = dlogistic_mix_logp(sup, lpi.expand(n, 2), mu.expand(n, 2), ls.expand(n, 2), lo_d.view(1).expand(n),
                            hi_d.view(1).expand(n))
    p = lp.exp()
    assert abs(float(p.sum()) - 1.0) < 1e-5 and float(p[0]) > 0.2 and float(p[-1]) > 0.1   # mass on both bounds
    N = 400_000
    d = dlogistic_mix_sample(lpi.expand(N, 2), mu.expand(N, 2), ls.expand(N, 2), lo_d.view(1).expand(N),
                             hi_d.view(1).expand(N), 1.0)
    freq = torch.bincount((d + 3).long(), minlength=n).float() / N
    assert float((freq - p).abs().max()) < 4e-3
    nxt = censored_next(torch.full((N, 1), 3.0), d.view(N, 1), lo_d.expand(N, 1), hi_d.expand(N, 1), bounds)
    assert float(nxt.min()) == 0.0 and float(nxt.max()) == 10.0 and torch.equal(nxt.view(-1), 3.0 + d.double())
    # a value on its bound, a value whose float32 limit is inexact (above 2^24), an unbounded entry
    cur = torch.tensor([[0.0, 50_000_003.0, -7.0]], dtype=torch.float64)
    b2 = ((0.0, 0.0, -INF), (INF, INF, INF))
    lo2, hi2 = censor_limits(cur, b2)
    assert float(lo2[0, 0]) == 0.0 and float(lo2[0, 1]) != -50_000_003.0 and float(lo2[0, 2]) < -1e8
    d2 = torch.stack([lo2[0, 0], lo2[0, 1], torch.tensor(3.0)]).view(1, 3)       # first two in the lower edge bin
    assert censored_next(cur, d2, lo2, hi2, b2).tolist() == [[0.0, 0.0, -4.0]]


def test_bounds_table_covers_every_learned_target():
    from dc.engine import LEDGER_NAMES, SCALAR_NAMES
    from dc.model import (BOUND_SOURCES, COM_RATE_HI, COM_RATE_LO, EIGHTH_HI, EIGHTH_LO, HALF_HI, HALF_LO, LEARNED_LEDGER,
                          LEARNED_SCALARS, LEDGER_BOUNDS, SCALAR_BOUNDS, TERRAIN_HI, TERRAIN_LO)
    names = {(k, n) for k, n, *_ in BOUND_SOURCES}
    assert all(("scalar", SCALAR_NAMES[i]) in names for i in LEARNED_SCALARS)
    assert all(("ledger", LEDGER_NAMES[i]) in names for i in LEARNED_LEDGER)
    assert ("cost", "build_cost") in names and set(SCALAR_BOUNDS) == set(LEARNED_SCALARS)
    from dc.engine import LG
    assert LG["sprite_cycle"] not in LEDGER_BOUNDS                       # wraps: no bound
    rows = {n: (lo, hi) for k, n, lo, hi, *_ in BOUND_SOURCES if k == "overlay"}
    assert rows["half overlays (5)"] == (HALF_LO[0], HALF_HI[0]) and rows["rate of growth"] == (EIGHTH_LO[0], EIGHTH_HI[0])
    assert rows["terrain"] == (TERRAIN_LO[0], TERRAIN_HI[0]) and rows["com_rate"] == (COM_RATE_LO[0], COM_RATE_HI[0])
    assert all(src for *_, src, _cav in BOUND_SOURCES)


def test_bookkeeping_samples_respect_bounds_at_the_bounds(pool, stats):
    """States sitting on their bounds: samples never leave the bounds, and land on them (the network is
    untrained, so its predictive spread is wide); the likelihood of an on-bound target is finite."""
    import dataclasses
    from dc.engine import LG, SC_FUNDS, SC_RES_VALVE, SC_SCORE
    from dc.model import LEDGER_BOUNDS, SCALAR_BOUNDS
    torch.manual_seed(0)
    m = Emulator(dataclasses.replace(SIZES["tiny"], bookkeeping=True, bk_width=32, bk_depth=1))
    m.set_norm_stats(stats)
    s0, r, a, s1 = next(pool.batches(4, seed=15))
    rep = lambda s: {k: v.repeat_interleave(64, 0) for k, v in s.items()}
    s0, s1 = rep(s0), rep(s1)
    r, a = r.repeat_interleave(64, 0), a.repeat_interleave(64, 0)
    s0["scalars"][:, SC_FUNDS] = 0
    s0["scalars"][:, SC_RES_VALVE] = 2000
    s0["scalars"][:, SC_SCORE] = 1000
    s0["ledger"][:, LG["flood_count"]] = 30
    s0["ledger"][:, LG["need_church"]] = -1
    ns = m.sample_next(s0, r, a)
    for i, (lo, hi) in SCALAR_BOUNDS.items():
        v = ns["scalars"][:, i]
        assert (lo is None or float(v.min()) >= lo) and (hi is None or float(v.max()) <= hi), i
    for i, (lo, hi) in LEDGER_BOUNDS.items():
        v = ns["ledger"][:, i]
        assert (lo is None or float(v.min()) >= lo) and (hi is None or float(v.max()) <= hi), i
    assert float((ns["scalars"][:, SC_FUNDS] == 0).float().mean()) > 0.2
    s1["scalars"][:, SC_FUNDS] = 0
    s1["scalars"][:, SC_RES_VALVE] = 2000
    s1["build_cost"] = torch.zeros(s1["scalars"].shape[0])
    lp = m.log_prob((s0, r, a, s1))
    assert torch.isfinite(lp["sc_funds"]).all() and torch.isfinite(lp["sc_res_valve"]).all()
    assert torch.isfinite(lp["build_cost"]).all()


def test_selections_are_disjoint():
    """The test selection shares no plan and no transition with the development selection; plan sources."""
    from types import SimpleNamespace
    from dc import fidelity as fd
    labs = ["noop", "budget_sweep", "random/uniform", "random/sprinkle", "builder/grid", "noop+perturb"]
    trajs = [SimpleNamespace(H=48 if j % 6 else 120, label=labs[j % len(labs)]) for j in range(1200)]
    dp, dl, dd = fd.selection(trajs, "dev")
    assert dp == fd.pick_transitions(trajs, 2000, 20261109) and dl == fd.pick_plans(trajs, 500, 24, 20261110)
    tp, tl, td = fd.selection(trajs, "test", n_plans=10**9)
    assert len(tl) == 700 and not set(tl) & set(dl) and not set(tp) & set(dp) and len(tp) == 2000
    assert all(i not in set(dl) for i, _ in tp)
    assert td["plans_shared_with_development"] == 0 and td["transitions_shared_with_development"] == 0
    assert [fd.plan_source(l) for l in labs] == ["open_loop"] * 3 + ["state_reading"] * 3
    assert dd["plans_by_source"]["open_loop"] + dd["plans_by_source"]["state_reading"] == 500
