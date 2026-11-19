"""Tests of the thresholds-v2 rule (dc.frontier) and of the frontier script's plumbing. CPU only, under a minute."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "hpr-dream"))
sys.path.insert(0, str(ROOT / "code" / "scripts"))

from dc import audit as A  # noqa: E402
from dc import frontier as F  # noqa: E402
from dc import tasks as T  # noqa: E402
from dc.engine import SC_COAL, SC_FUNDS, SC_NUCLEAR, SC_POP, SC_POWERED, SC_UNPOWERED  # noqa: E402
from dc.grammar import N_COLS, NOOP_ROW, compile_plan  # noqa: E402
from dc.oracle import replay  # noqa: E402

H = 24


def traj(pop_h, funds_min=10000.0, funds_h=10000.0, pop0=1000.0, funds0=10000.0):
    """Synthetic scalar trajectories (..., H+1, 20): population linear from pop0 to pop_h, funds from funds0
    through funds_min at month H // 2 to funds_h."""
    pop_h = np.asarray(pop_h, dtype=np.float64)
    shape = np.broadcast_shapes(pop_h.shape, np.shape(funds_min), np.shape(funds_h))
    s = np.zeros(shape + (H + 1, 20))
    s[..., SC_POP] = pop0 + (np.broadcast_to(pop_h, shape)[..., None] - pop0) * np.linspace(0, 1, H + 1)
    s[..., SC_FUNDS] = funds0
    s[..., H // 2, SC_FUNDS] = np.broadcast_to(funds_min, shape)
    s[..., H, SC_FUNDS] = np.broadcast_to(funds_h, shape)
    return s


def test_rule_on_a_synthetic_case():
    # constants on the primary seed: plan 2 is the best by population but goes bankrupt (infeasible for grow)
    pops = np.array([1000.0, 2000.0, 9000.0, 2500.0, 500.0])
    fmin = np.array([10000.0, 10000.0, -5.0, 10000.0, 10000.0])
    const_p = traj(pops, fmin)
    J = F.J("grow", const_p)
    top = F.top_k(J, 2)
    assert list(top) == [3, 1]                                   # feasible first, by statistic
    # top-2 on eight secondary seeds: plan 3 reaches 2600 on one seed
    sec_pops = np.array([[2400.0] * 7 + [2600.0], [1900.0] * 8])
    const_s = traj(sec_pops)
    # finalists on nine seeds: 0 feasible everywhere (mean 5000), 1 better but bankrupt on one seed, 2 feasible (mean 4000)
    f0 = 5000.0 + np.array([-400, -300, -200, -100, 0, 100, 200, 300, 400], dtype=np.float64)
    fin_pops = np.stack([f0, np.full(9, 6000.0), np.full(9, 4000.0)])
    fin_fmin = np.full((3, 9), 10000.0)
    fin_fmin[1, 4] = -1.0
    scal9 = traj(fin_pops, fin_fmin)
    r = F.rule("grow", const_p, top, const_s, scal9, stat_sd=1000.0)
    assert r["c"] == 2600.0 and r["c_feasible"] and r["c_grid_index"] == 3 and r["c_seed_index"] == 8
    assert r["c_primary_only"] == 2500.0
    assert r["e"] == pytest.approx(5000.0) and r["frontier_index"] == 0 and r["n_feasible_all_seeds"] == 2
    sd = float(np.std(f0, ddof=1))
    assert r["seed_sd"] == pytest.approx(sd)
    assert r["theta"] == pytest.approx(2600.0 + 0.5 * 2400.0)
    assert r["theta_l25"] == pytest.approx(2600.0 + 0.25 * 2400.0)
    assert r["theta_l75"] == pytest.approx(2600.0 + 0.75 * 2400.0)
    assert r["well_posed"] == (2400.0 >= 4 * sd)
    assert r["headroom_seed_sd"] == pytest.approx(2400.0 / sd)
    assert r["headroom_stat_sd"] == pytest.approx(2.4)
    # the bar lies above every constant replay and below the frontier plan's mean
    assert (F.verdict("grow", const_p, r["theta"]).sum(), F.verdict("grow", const_s, r["theta"]).sum()) == (0, 0)
    # not well posed when the frontier plan is noisy
    noisy = scal9.copy()
    noisy[0, :, :, SC_POP] = traj(5000.0 + 1500.0 * np.array([-1, 1] * 4 + [0]))[..., SC_POP]
    assert not F.rule("grow", const_p, top, const_s, noisy, 1000.0)["well_posed"]


def test_rule_fallbacks():
    # no feasible constant replay: c is the largest statistic regardless, flagged
    const_p = traj(np.array([3000.0, 4000.0]), np.array([-1.0, -1.0]))
    const_s = traj(np.array([[3500.0] * 8]), np.full((1, 8), -1.0))
    r = F.rule("grow", const_p, np.array([0]), const_s, traj(np.full((1, 9), 9000.0)), 1000.0)
    assert r["c"] == 4000.0 and not r["c_feasible"]
    # no finalist feasible on all nine seeds: e undefined, theta NaN, not well posed
    bad = traj(np.full((2, 9), 9000.0), np.where(np.arange(9) == 0, -1.0, 1.0)[None].repeat(2, 0))
    r2 = F.rule("grow", const_p, np.array([0]), const_s, bad, 1000.0)
    assert np.isnan(r2["e"]) and np.isnan(r2["theta"]) and not r2["well_posed"] and r2["frontier_index"] == -1


def _random_traj(rng, n):
    s = np.zeros((n, H + 1, 20))
    s[..., SC_POP] = rng.uniform(1000, 5000, (n, H + 1))
    s[..., SC_FUNDS] = rng.uniform(-2000, 20000, (n, H + 1))
    s[..., 0, SC_FUNDS] = 10000.0
    s[..., SC_COAL] = rng.integers(0, 3, (n, 1))
    s[..., SC_NUCLEAR] = 0
    s[..., SC_POWERED] = rng.integers(50, 200, (n, H + 1))
    s[..., SC_UNPOWERED] = rng.integers(0, 10, (n, H + 1))
    return s


@pytest.mark.parametrize("variant", list(F.VARIANTS))
def test_J_ordering(variant):
    rng = np.random.default_rng(0)
    s = _random_traj(rng, 4000)
    Jv, ok, st, sl = F.J(variant, s), F.feasible(variant, s), F.statistic(variant, s), F.slack(variant, s)
    np.testing.assert_array_equal(Jv[ok], st[ok])                 # J is the statistic where feasible
    if (~ok).any():
        assert ok.any() and Jv[~ok].max() < Jv[ok].min()           # every infeasible plan below every feasible one
        order = np.argsort(Jv[~ok])
        assert (np.diff(sl[~ok][order]) >= -1e-6).all()            # ordered by the violated slack (to float resolution)
        assert (sl[~ok] < 0).all()
    assert ((sl >= 0) == ok).all()
    # margin >= 0 exactly where the verdict holds, at a threshold inside the statistic's range
    th = float(np.median(st))
    np.testing.assert_array_equal(F.margin(variant, s, th, 100.0) >= 0, F.verdict(variant, s, th))
    if variant in ("grow", "solvent", "recover", "power", "treasury_rev"):   # these are dc.tasks exactly
        np.testing.assert_array_equal(F.verdict(variant, s, th), T.verdict(F.base_task(variant), s, th))
        np.testing.assert_allclose(F.margin(variant, s, th, 100.0), T.margin(F.base_task(variant), s, th, 100.0))


def test_treasury_v2_clause():
    s = traj(np.array([900.0, 1000.0, 1100.0]), funds_h=np.array([50000.0, 40000.0, 30000.0]))
    assert list(F.feasible("treasury_v2", s)) == [False, True, True]
    assert list(F.feasible("treasury_v1", s)) == [True, True, True]
    assert list(F.statistic("treasury_v2", s)) == [50000.0, 40000.0, 30000.0]
    assert F.J("treasury_v2", s)[0] == pytest.approx(F.J_INFEASIBLE - 0.1)
    assert list(F.verdict("treasury_v2", s, 35000.0)) == [False, True, False]


def test_constant_plans_and_overwrite():
    P = F.constant_plans(H)
    assert P.shape == (2625, H, N_COLS) and len({tuple(r) for r in F.GRID.tolist()}) == 2625
    assert (P[:, :, 5:] == 0).all() and (P[:, :, 4] == 0).all()
    assert (P[:, :, 0:4] == F.GRID[:, None, :]).all()
    assert (P[F.GRID.tolist().index(list(F.DEFAULT_SETTING))] == np.tile(NOOP_ROW, (H, 1))).all()
    eff = A.effective(P[:3], "recover", H)
    assert (eff[:, 0, 4] == T.RECOVER_DISASTER).all() and (eff[:, 1:, 4] == 0).all()
    plans = np.tile(NOOP_ROW, (2, H, 1)).astype(np.int16)
    plans[:, :, 5:10] = (1, 50, 50, 2, 2)
    ow = F.overwrite_budget(plans, (20, 0, 1, 2))
    assert (ow[..., 0:4] == (20, 0, 1, 2)).all() and (ow[..., 5:] == plans[..., 5:]).all()


def test_centred_init_moves_only_budget_means():
    import hpr_dream as hd
    rng = np.random.default_rng(1)
    pool = rng.integers(A.plan_space(H).low, A.plan_space(H).high + 1, size=(50, H * N_COLS))
    pool = A.plan_space(H).clip(pool)
    sp = A.plan_space(H)
    m0 = hd.fit_marginals(sp, pool)
    m = F.centred_init(sp, pool, (17, 1, 2, 3), H)
    L = sp._layout
    for j, c in enumerate(L.int_cols):
        if c % N_COLS < 4:
            assert m.mu[j] == (17, 1, 2, 3)[c % N_COLS]
        else:
            assert m.mu[j] == m0.mu[j]
    np.testing.assert_array_equal(m.sigma, m0.sigma)
    np.testing.assert_array_equal(m.p, m0.p)


def _small_start():
    insts = A.load_instances()
    return min((i for i in insts if i.task == "grow"), key=lambda i: Path(i.cty).stat().st_size)


def test_replays_go_through_the_cache(tmp_path):
    inst = _small_start()
    judge = A.EngineJudge(tmp_path / "cache", workers=0, H=H)
    try:
        P = A.effective(F.constant_plans(H, F.GRID[[0, 1000]]), inst.task, H)
        s1 = judge.scalars(inst, P, A.primary_seed(inst))
        assert judge.counters()["engine_replays"] == 2 and judge.counters()["engine_cache_hits"] == 0
        s2 = judge.scalars(inst, P, A.primary_seed(inst))
        assert judge.counters()["engine_replays"] == 2 and judge.counters()["engine_cache_hits"] == 2
        np.testing.assert_array_equal(s1, s2)
        from dc.engine import Engine
        eng = Engine()
        acts, forced = compile_plan(P[1])
        np.testing.assert_array_equal(replay(eng, inst.cty, acts, A.primary_seed(inst), forced=forced or None).scalars, s1[1])
    finally:
        judge.close()


class CountingJudge:
    """Stands in for dc.audit.EngineJudge: synthetic trajectories, every request counted."""

    def __init__(self):
        self.n = 0

    def scalars(self, inst, eff, seeds):
        eff = np.asarray(eff).reshape(-1, H, N_COLS)
        self.n += len(eff)
        tax = eff[:, :, 0].mean(axis=1)
        seeds = np.broadcast_to(np.asarray(seeds), (len(eff),))
        noise = (seeds % 97) / 97.0
        return traj(1000.0 + 100.0 * (20 - np.abs(tax - 9)) + 50 * noise).astype(np.int64)

    def counters(self):
        return {"engine_requests": self.n, "engine_cache_hits": 0, "engine_replays": self.n, "engine_replays_remote": 0,
                "engine_city_months_replayed": self.n * H, "engine_seconds": 0.0}


def test_const_stage_requests_every_replay_through_the_judge(tmp_path, monkeypatch):
    import task_frontier as TF
    monkeypatch.setattr(TF, "CACHE", tmp_path)
    inst = _small_start()
    judge = CountingJudge()
    run = TF.Runner(H, judge, A.Pools(H=H), 1, lambda s: None)
    run.run_instance(inst, "grow", ["const"])
    d = TF.load_npz(TF.inst_dir(H, inst, "grow") / "const.npz")
    assert judge.n == 2625 + F.N_CONST_TOP * 8
    assert d["scal"].shape == (2625, H + 1, 20) and d["sec_scal"].shape == (F.N_CONST_TOP, 8, H + 1, 20)
    assert (F.GRID[d["top"][:3], 0] == 9).all()                  # the synthetic optimum is tax 9
    assert json.loads(str(d["counts"]))["engine_requests"] == 2625 + 160


def test_no_constant_plan_passes_at_theta_on_three_real_instances():
    """On three real instances (three families): no constant plan passes the nine-seed theta(0.5) on the primary
    seed (where e > c), and none of the 20 best constants passes theta = theta32(0.5) under the majority rule on the
    32 oracle seeds (where e32 > c32). Every replay is served from the engine cache the frontier run filled."""
    path = ROOT / "data" / "tasks_v2_H24.json"
    if not path.exists():
        pytest.skip("data/tasks_v2_H24.json not written yet")
    rows = json.loads(path.read_text())["instances"]
    insts = {i.key: i for i in A.load_instances()}
    picked, fams = [], set()
    for r in rows:
        if r["task"] in fams or r["e"] is None or not r["e"] > r["c"]:
            continue
        if r.get("e32") is not None and (r.get("c32") is None or not r["e32"] > r["c32"]):
            continue
        picked.append(r)
        fams.add(r["task"])
        if len(picked) == 3:
            break
    assert len(picked) == 3
    judge = A.EngineJudge(workers=0, H=H)
    try:
        for r in picked:
            inst = insts[f"{r['start_id']}|{r['task']}|H24"]
            variant = "treasury_rev" if r["task"] == "treasury" else r["task"]   # the file's treasury is the revenue form
            P = A.effective(F.constant_plans(H), inst.task, H)
            scal = judge.scalars(inst, P, A.primary_seed(inst))
            th9 = r.get("theta_l50", r["theta"])
            assert F.verdict(variant, scal, th9).sum() == 0, r["start_id"]
            if r.get("theta32_l50") is not None:
                top = F.top_k(F.J(variant, scal), F.N_CONST_TOP, F.slack(variant, scal))
                seeds = T.oracle_seeds(inst.start_id, inst.task, H)
                s32 = judge.scalars(inst, np.repeat(P[top], len(seeds), axis=0), np.tile(seeds, len(top)))
                s32 = s32.reshape(len(top), len(seeds), H + 1, 20)
                m32 = F.majority_value(F.statistic(variant, s32), F.feasible(variant, s32))
                assert np.max(m32) == pytest.approx(r["c32"])
                assert not F.majority_pass(F.statistic(variant, s32), F.feasible(variant, s32), r["theta"]).any()
        if (A.CACHE_ROOT / "engine").is_dir():
            assert judge.counters()["engine_replays"] == 0           # served from the engine cache the frontier run filled
    finally:
        judge.close()


def test_treasury_rev_clauses():
    from dc.engine import SC_TAX, SC_TAX_FUND
    s = traj(np.array([1000.0, 1000.0, 1000.0]), funds_min=np.array([10.0, 10.0, -1.0]))
    s[..., SC_TAX] = 7.0
    s[1, 5, SC_TAX] = 8.0                                        # a tax rise above the start rate
    s[..., -1, SC_TAX_FUND] = [300.0, 900.0, 500.0]
    assert list(F.statistic("treasury_rev", s)) == [300.0, 900.0, 500.0]
    assert list(F.feasible("treasury_rev", s)) == [True, False, False]
    assert F.slack("treasury_rev", s)[1] == pytest.approx(-1 / 20)
    assert list(F.verdict("treasury_rev", s, 200.0)) == [True, False, False]


def test_majority_value_is_the_upper_median_and_16_of_32_passes():
    rng = np.random.default_rng(3)
    st = rng.normal(100, 10, (500, 32))
    fe = rng.random((500, 32)) > 0.1
    m = F.majority_value(st, fe)
    for th in (80.0, 95.0, 100.0, 105.0):
        np.testing.assert_array_equal(m >= th, F.majority_pass(st, fe, th))
        np.testing.assert_array_equal(m >= th, (fe & (st >= th)).sum(axis=1) >= 16)
    exact = np.r_[np.full(16, 10.0), np.full(16, 0.0)]                 # exactly 16 of 32 reach 10
    assert F.majority_value(exact, np.ones(32, bool)) == 10.0 and F.majority_pass(exact, np.ones(32, bool), 10.0)
    assert F.majority_value(exact, np.r_[np.zeros(1, bool), np.ones(31, bool)]) == 0.0   # 15 of 32: fails at 10


def test_rule32_on_a_synthetic_case():
    cst = np.tile(np.arange(32.0), (20, 1)) + np.arange(20)[:, None]   # constant k: values k..k+31, m32 = k + 16
    cfe = np.ones((20, 32), bool)
    fst = np.arange(32.0) + 100.0                                      # frontier: m32 = 116
    r = F.rule32(cst, cfe, fst, np.ones(32, bool))
    assert r["c32"] == 19 + 16 and r["e32"] == 116.0
    assert r["theta32_l50"] == pytest.approx(35 + 0.5 * 81)
    se = 1.2533 * np.std(fst, ddof=1) / np.sqrt(32)
    assert r["se32"] == pytest.approx(se) and r["well_posed32"] == (81 >= 6 * se)
    flat = F.rule32(cst, cfe, np.full(32, 40.0), np.ones(32, bool))   # zero seed sd: any positive headroom counts
    assert flat["seed_sd32"] == 0 and flat["well_posed32"]
    worse = F.rule32(cst, cfe, np.full(32, 30.0), np.ones(32, bool))
    assert worse["headroom32"] < 0 and not worse["well_posed32"]


@pytest.mark.parametrize("variant", ["grow", "solvent", "recover", "power", "treasury_rev"])
def test_majority_value_matches_dc_tasks_oracle(variant):
    task = F.base_task(variant)
    rng = np.random.default_rng(4)
    s = _random_traj(rng, 64 * 32).reshape(64, 32, H + 1, 20)
    np.testing.assert_array_equal(T.oracle_value(task, s), F.majority_value(F.statistic(variant, s), F.feasible(variant, s)))
    th = float(np.median(F.statistic(variant, s)))
    np.testing.assert_array_equal(T.oracle_verdict(task, s, th), F.majority_pass(F.statistic(variant, s), F.feasible(variant, s), th))
