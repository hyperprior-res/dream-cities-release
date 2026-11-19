"""Noise-only surrogates and the surrogate attack."""

from __future__ import annotations

import math

import numpy as np
import pytest

from hpr_dream import stats as S
from hpr_dream.attack import BudgetError, Space, cem, random_shooting
from hpr_dream.noise import (TIE_BREAK, FlipSurrogate, OracleCache, PoolTooSmall, ResidualFamily, ResidualSurrogate,
                             SurrogateGrader, attack_surrogate, flip_surrogate, pool_family_residuals, residual_surrogate)


def test_flip_surrogate_extremes_and_score_range():
    m = np.array([-2.0, -0.1, 0.0, 0.5, 3.0])
    rng = np.random.default_rng(0)
    d = flip_surrogate(m, 0.0, 0.0, rng)
    assert d.accept.tolist() == [False, False, True, True, True]  # margin 0 passes
    assert ((d.score - d.accept) >= 0).all() and ((d.score - d.accept) < TIE_BREAK).all()
    d = flip_surrogate(m, 1.0, 1.0, rng)
    assert d.accept.tolist() == [True, True, False, False, False]


def test_flip_surrogate_rates():
    rng = np.random.default_rng(1)
    m = np.where(rng.random(400000) < 0.3, 1.0, -1.0)
    d = flip_surrogate(m, 0.12, 0.3, rng)
    o = m >= 0
    assert abs((d.accept & ~o).sum() / (~o).sum() - 0.12) < 0.003
    assert abs((~d.accept & o).sum() / o.sum() - 0.3) < 0.004


def test_residual_surrogate():
    m = np.array([-1.0, 0.5, 2.0])
    d = residual_surrogate(m, [0.75], np.random.default_rng(2))
    assert np.allclose(d.score, m + 0.75) and d.accept.tolist() == [False, True, True]
    pool = np.array([-3.0, 1.0, 10.0])
    d = residual_surrogate(np.zeros(30000), pool, np.random.default_rng(3))
    assert set(np.unique(d.score)) <= set(pool)
    assert abs((d.score == 10.0).mean() - 1 / 3) < 0.01
    with pytest.raises(ValueError):
        residual_surrogate(m, [], np.random.default_rng(0))


class Oracle:
    def __init__(self, w, c=0.0):
        self.w, self.c, self.n = np.asarray(w, float), c, 0

    def __call__(self, X):
        self.n += len(X)
        return X @ self.w - self.c


def test_surrogate_grader_memo_is_a_fixed_function_of_the_plan():
    orc = Oracle([1.0, -1.0])
    gr = SurrogateGrader(ResidualSurrogate(np.linspace(-1, 1, 101)), orc, np.random.default_rng(4))
    X = np.array([[1, 2], [3, 0], [1, 2], [5, 5]])
    s1 = gr(X)
    assert s1[0] == s1[2]
    assert orc.n == 3 and gr.n_oracle_evals == 3 and gr.n_scored == 4  # oracle once per distinct plan
    s2 = gr(X[::-1])
    assert np.array_equal(s2, s1[::-1]) and orc.n == 3 and gr.n_scored == 8
    sc, acc, mar = gr.lookup(np.array([3, 0]))
    assert sc == s1[1] and mar == 3.0 and acc == (sc >= 0)


def test_surrogate_grader_without_memo_draws_per_row():
    orc = Oracle([1.0, 0.0])
    gr = SurrogateGrader(FlipSurrogate(0.5, 0.5), orc, np.random.default_rng(5), memo=False)
    X = np.zeros((50, 2), int)
    s = gr(X)
    assert len(np.unique(s)) == 50 and orc.n == 50
    assert gr.lookup(None, 7)[0] == s[7]
    s2 = gr(X[:5])
    assert gr.lookup(None, 52)[0] == s2[2]


def test_attack_surrogate_returns_the_selected_plans_verdicts():
    rng = np.random.default_rng(6)
    P = rng.integers(0, 10, size=(200, 2))
    orc = Oracle([1.0, 1.0], c=12.0)
    pool = np.r_[np.zeros(50), np.full(50, 3.0)]
    res = attack_surrogate(lambda s: random_shooting(s, P, 100), ResidualSurrogate(pool), orc,
                           np.random.default_rng(7), budget=100)
    assert res.log["n_scored"] == 100 == res.log["surrogate_n_scored"]
    assert res.log["residual_pool_size"] == 100 and res.log["residual_pool_kind"] == "per-instance"
    assert res.log["residual_pool_paired"] is False and res.log["residual_pooled_instances"] == 1
    assert res.oracle_margin == float(res.plan @ orc.w - 12.0)
    assert res.oracle_accept == (res.oracle_margin >= 0)
    assert res.surrogate_accept == (res.surrogate_score >= 0)
    assert res.surrogate_score - res.oracle_margin in (0.0, 3.0)
    assert res.hacked == (res.surrogate_accept and not res.oracle_accept)
    # the selected plan has the highest surrogate score of the 100 scored
    gr = SurrogateGrader(ResidualSurrogate(pool), orc, np.random.default_rng(7))
    scores = gr(P[:100])
    assert res.surrogate_score == scores.max()


def test_attack_surrogate_with_cem_and_shared_grader():
    sp = Space.integer_columns([0, 0], [20, 20])
    orc = Oracle([1.0, -1.0])
    gr = SurrogateGrader(FlipSurrogate(0.2, 0.2), orc, np.random.default_rng(8))
    for B in (10, 100, 1000):
        r = attack_surrogate(lambda s, B=B: cem(s, sp, B, np.random.default_rng(B)), gr)
        assert r.log["surrogate_n_scored"] == B
        assert r.log["n_oracle_evals"] <= B
    assert gr.n_scored == 1110 and gr.n_oracle_evals <= 21 * 21


def test_attack_surrogate_budget_cross_check():
    P = np.zeros((10, 2), int)
    orc = Oracle([1.0, 0.0])

    def cheating_attack(score):
        score(P[:3])  # an extra call the attacker's log does not know about
        return random_shooting(score, P, 5)

    with pytest.raises(BudgetError):
        attack_surrogate(cheating_attack, FlipSurrogate(0.1, 0.1), orc, np.random.default_rng(0))


def test_flip_surrogate_attack_matches_closed_form():
    # random shooting against the flip surrogate, many independent instances with known pi:
    # the hack rate must match noise_floor_flip(pi, fp, fn, B)
    pi, fp, fn, B, T = 0.25, 0.1, 0.2, 10, 4000
    rng = np.random.default_rng(9)
    hacked = np.empty(T, bool)
    for t in range(T):
        props = rng.integers(0, 1 << 30, size=(B, 1))
        passes = rng.random(B) < pi
        lookup = {int(p[0]): (1.0 if ok else -1.0) for p, ok in zip(props, passes)}
        oracle = lambda X: np.array([lookup[int(x[0])] for x in X])
        r = attack_surrogate(lambda s: random_shooting(s, props, B), FlipSurrogate(fp, fn), oracle, rng)
        hacked[t] = r.hacked
    expect = S.noise_floor_flip(pi, fp, fn, B)
    se = math.sqrt(expect * (1 - expect) / T)
    assert abs(hacked.mean() - expect) < 4 * se, (hacked.mean(), expect)


# ------------------------------------------------------------------------------------------ paired and pooled pools


def test_paired_pool_uses_column_0_for_score_and_column_1_for_accept():
    m = np.array([1.0, -0.5, 0.2])
    d = residual_surrogate(m, np.array([[0.5, -2.0]]), np.random.default_rng(0))
    assert np.allclose(d.score, m + 0.5)
    assert d.accept.tolist() == [False, False, False]  # m - 2 < 0 everywhere
    m2 = np.array([1.0, -0.6, -0.5])
    d = residual_surrogate(m2, np.array([[-5.0, 0.5]]), np.random.default_rng(0))
    assert np.allclose(d.score, m2 - 5.0) and d.accept.tolist() == [True, False, True]  # margin 0 passes
    # rows stay paired: column 0 and column 1 of the same row are used together
    pool = np.array([[0.0, -10.0], [100.0, 10.0]])
    d = residual_surrogate(np.zeros(2000), pool, np.random.default_rng(1))
    assert np.array_equal(d.score >= 50, d.accept)


def test_pool_family_residuals_hand():
    target = np.array([1.0, 2.0, 3.0])  # median 2, MAD 1
    other = np.array([10.0, 20.0, 30.0, 40.0, 50.0])  # median 30, MAD 10
    out = pool_family_residuals(target, [target, other])
    assert np.allclose(out[:, 0], [1, 2, 3, 0, 1, 2, 3, 4])
    assert np.allclose(pool_family_residuals(target, ResidualFamily([target, other])), out)
    # paired: each column with its own median and MAD
    t2 = np.stack([target, 10 * target], axis=1)  # column 1: median 20, MAD 10
    o2 = np.stack([other, other], axis=1)
    out2 = pool_family_residuals(t2, [o2])
    assert np.allclose(out2[:, 0], [0, 1, 2, 3, 4]) and np.allclose(out2[:, 1], [0, 10, 20, 30, 40])
    with pytest.raises(ValueError):
        pool_family_residuals(target, [np.ones(5)])  # zero MAD


def test_pool_smaller_than_budget_is_refused():
    m = np.zeros(10)
    small = np.linspace(-1, 1, 50)
    with pytest.raises(PoolTooSmall):
        residual_surrogate(m, small, np.random.default_rng(0), budget=100)
    residual_surrogate(m, small, np.random.default_rng(0), budget=50)
    fam = [np.linspace(-1, 1, 50) + k for k in range(3)]  # 150 rows pooled
    d = residual_surrogate(m, small, np.random.default_rng(0), budget=100, pooled=True, family_pools=fam)
    assert d.score.size == 10
    with pytest.raises(PoolTooSmall):
        residual_surrogate(m, small, np.random.default_rng(0), budget=200, pooled=True, family_pools=fam)
    with pytest.raises(ValueError):
        residual_surrogate(m, small, np.random.default_rng(0), pooled=True)
    # inside an attack: refused before the oracle is asked anything
    orc = Oracle([1.0, 0.0])
    P = np.arange(400).reshape(200, 2)
    with pytest.raises(PoolTooSmall):
        attack_surrogate(lambda s: random_shooting(s, P, 100), ResidualSurrogate(small), orc, np.random.default_rng(0))
    assert orc.n == 0
    with pytest.raises(PoolTooSmall):
        attack_surrogate(lambda s: random_shooting(s, P, 100), ResidualSurrogate(small), orc, np.random.default_rng(0),
                         budget=100)
    r = attack_surrogate(lambda s: random_shooting(s, P, 100), ResidualSurrogate(small, family_pools=fam), orc,
                         np.random.default_rng(0), budget=100)
    assert r.log["residual_pool_kind"] == "pooled" and r.log["residual_pool_size"] == 150
    assert r.log["residual_pooled_instances"] == 3


def test_oracle_cache_is_shared_by_both_surrogates():
    orc = Oracle([1.0, -1.0])
    cache = OracleCache(orc)
    P = np.random.default_rng(3).integers(0, 50, size=(300, 2))
    distinct = len({tuple(r) for r in P[:200]})
    flip = SurrogateGrader(FlipSurrogate(0.1, 0.1), cache, np.random.default_rng(1))
    resid = SurrogateGrader(ResidualSurrogate(np.linspace(-1, 1, 300)), cache, np.random.default_rng(2))
    a = attack_surrogate(lambda s: random_shooting(s, P, 200), flip, budget=200)
    b = attack_surrogate(lambda s: random_shooting(s, P, 200), resid, budget=200)
    assert orc.n == distinct == cache.n_evals
    assert a.log["n_oracle_evals"] == distinct and b.log["n_oracle_evals"] == 0
    assert a.log["oracle_cache_shared"] and b.log["n_oracle_requests"] == distinct
    assert cache.n_requests == 2 * distinct
    assert np.allclose(cache(P[:5]), P[:5] @ orc.w) and orc.n == distinct


def test_accept_margin_remakes_the_accept_with_the_drawn_verdict_residual():
    """With accept_margin, the selected plan's accept is accept_margin(plan) + the verdict residual drawn for it,
    not the search basis plus that residual; scores and selection are unchanged."""
    X = np.arange(40, dtype=np.int64).reshape(20, 2)
    basis = lambda P: P[:, 0].astype(float) / 10.0                  # search basis: 0.0 .. 3.8
    low = lambda P: -5.0 * np.ones(len(P))                           # accept basis: far below the bar
    pool = np.stack([np.linspace(-1, 1, 25), np.linspace(-0.5, 0.5, 25)], axis=1)
    plain = SurrogateGrader(ResidualSurrogate(pool), OracleCache(basis), np.random.default_rng(4))
    r0 = attack_surrogate(lambda sc: random_shooting(sc, X, 20), plain, budget=20)
    two = SurrogateGrader(ResidualSurrogate(pool), OracleCache(basis), np.random.default_rng(4), accept_margin=low)
    r1 = attack_surrogate(lambda sc: random_shooting(sc, X, 20), two, budget=20)
    assert np.array_equal(r0.plan, r1.plan) and r0.surrogate_score == r1.surrogate_score
    assert r0.surrogate_accept and not r1.surrogate_accept
    vr = r1.log["verdict_residual_drawn"]
    assert r1.log["accept_basis_margin"] == -5.0 and r1.log["accept_at_search"] == r0.surrogate_accept
    assert r1.log["search_basis_margin"] + vr >= 0 and vr in set(pool[:, 1])
    high = SurrogateGrader(ResidualSurrogate(pool), OracleCache(basis), np.random.default_rng(4),
                           accept_margin=lambda P: 5.0 * np.ones(len(P)))
    assert attack_surrogate(lambda sc: random_shooting(sc, X, 20), high, budget=20).surrogate_accept
    single = SurrogateGrader(ResidualSurrogate(pool[:, :1]), OracleCache(basis), np.random.default_rng(4),
                             accept_margin=low)
    with pytest.raises(ValueError):
        attack_surrogate(lambda sc: random_shooting(sc, X, 20), single, budget=20)


def test_volatility_neighbours_nearest_in_log_and_ties_by_pool_order():
    from hpr_dream.noise import volatility_neighbours
    sd = np.array([0.0, 1.0, 10.0, 1.0, 0.1, 100.0, 1.0])
    nb = volatility_neighbours(sd, [1.0, 0.0, 50.0], k=3, eps=1e-3)
    assert nb[0].tolist() == [1, 3, 6]                    # the three exact matches, in pool order
    assert nb[1].tolist() == [0, 4, 1]                    # log(0.001) -> 0.0, then 0.1, then the first 1.0
    assert nb[2].tolist() == [5, 2, 1]                    # log(50): 100 (0.69) before 10 (1.61), then the first 1.0
    for bad in (dict(k=0, eps=1e-3), dict(k=8, eps=1e-3), dict(k=2, eps=0.0)):
        with pytest.raises(ValueError):
            volatility_neighbours(sd, [1.0], **bad)
    with pytest.raises(ValueError):
        volatility_neighbours(sd, [-1.0], k=2, eps=1e-3)


def test_volatility_surrogate_draws_from_the_neighbours_only():
    """Each candidate's residual row is one of its k nearest pool rows in log(sd + eps), every one of them reached;
    the score is margin + column 0 and the accept margin + column 1 of that row."""
    from hpr_dream.noise import VolatilityResidualSurrogate, volatility_neighbours
    rng = np.random.default_rng(0)
    n = 200
    sd = np.exp(rng.normal(0, 1.5, n))
    pool = np.stack([np.arange(n, dtype=float), 1000.0 + np.arange(n)], axis=1)      # row index readable from the value
    sg = VolatilityResidualSurrogate(pool, sd, k=10, eps=1e-3)
    assert sg.describe()["residual_draw"] == "volatility" and not sg.no_spread and sg.pool_size == n
    cand = np.full(4000, sd[17])
    d = sg(np.zeros(4000), np.random.default_rng(1), volatility=cand)
    rows = d.score.astype(int)
    assert set(rows.tolist()) == set(volatility_neighbours(sd, [sd[17]], 10, 1e-3)[0].tolist())
    assert np.array_equal(d.verdict_residual, 1000.0 + rows) and d.accept.all()
    with pytest.raises(ValueError):
        sg(np.zeros(3), np.random.default_rng(1))                                    # the draw needs volatility=
    with pytest.raises(ValueError):
        VolatilityResidualSurrogate(pool, sd[:-1], k=10, eps=1e-3)


def test_volatility_surrogate_without_spread_is_the_plain_draw():
    from hpr_dream.noise import VolatilityResidualSurrogate
    pool = np.stack([np.linspace(-1, 1, 50), np.linspace(-2, 2, 50)], axis=1)
    m = np.linspace(-0.5, 0.5, 30)
    v = VolatilityResidualSurrogate(pool, np.full(50, 0.3), k=10, eps=1e-3)
    assert v.no_spread and v.describe()["residual_draw_no_spread"]
    a = v(m, np.random.default_rng(7), volatility=np.linspace(0, 5, 30))
    b = ResidualSurrogate(pool)(m, np.random.default_rng(7))
    assert np.array_equal(a.score, b.score) and np.array_equal(a.accept, b.accept)
    assert np.array_equal(a.verdict_residual, b.verdict_residual)


def test_grader_hands_the_candidates_volatility_to_the_surrogate():
    """SurrogateGrader(volatility=...) calls it on the rows it scores, after the oracle margin, and the selected
    plan's draw comes from the neighbours of that plan's sd; memo keeps one draw per plan."""
    from hpr_dream.noise import VolatilityResidualSurrogate, volatility_neighbours
    X = np.arange(60, dtype=np.int64).reshape(30, 2)
    basis = lambda P: np.zeros(len(P))
    vol = lambda P: P[:, 0].astype(float) / 10.0                     # sd of a plan: 0.0 .. 5.8
    pool_sd = np.linspace(0, 6, 120)
    pool = np.stack([np.arange(120, dtype=float), np.arange(120, dtype=float)], axis=1)
    seen = []
    gr = SurrogateGrader(VolatilityResidualSurrogate(pool, pool_sd, k=5, eps=1e-3), OracleCache(basis),
                         np.random.default_rng(2), volatility=lambda P: (seen.append(len(P)), vol(P))[1])
    r = attack_surrogate(lambda sc: random_shooting(sc, X, 30), gr, budget=30)
    assert seen == [30] and r.log["residual_draw"] == "volatility" and r.log["residual_draw_k"] == 5
    for x in X:
        s, _, _ = gr.lookup(x)
        assert int(s) in set(volatility_neighbours(pool_sd, vol(x[None]), 5, 1e-3)[0].tolist())
    gr(X[:3])
    assert seen == [30]                                               # memoised: no new call for plans already scored
    with pytest.raises(TypeError):
        SurrogateGrader(ResidualSurrogate(pool), OracleCache(basis), np.random.default_rng(2), volatility=3)


def test_calibrated_neighbours_ranks_ties_and_exclusion():
    """Nearest pool rows in the plane of the pool's own ranks (share of pool rows strictly below), Euclidean, ties by
    pool order; excluded rows are never returned; argument checks."""
    from hpr_dream.noise import calibrated_neighbours
    m = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    s = np.array([0.0, 0.0, 1.0, 1.0, 2.0, 2.0])
    # pool counts below: m -> 0..5, s -> 0, 0, 2, 2, 4, 4; candidate (2.5, 1.0) -> (3, 2)
    # squared distances 13, 8, 1, 0, 5, 8: rows 3, 2, 4, then 1 before 5 (pool order)
    assert calibrated_neighbours(m, s, [2.5], [1.0], 5)[0].tolist() == [3, 2, 4, 1, 5]
    # candidate (2.0, 1.0) -> (2, 2) is pool row 2 itself; with row 2 left out: 3 (1), 1 (5), then 0 before 4 (8)
    assert calibrated_neighbours(m, s, [2.0], [1.0], 1)[0].tolist() == [2]
    assert calibrated_neighbours(m, s, [2.0], [1.0], 4, exclude=[[2]])[0].tolist() == [3, 1, 0, 4]
    # beyond the pool's range: counts 0 and n; a constant column ranks every row 0, so the other column decides
    assert calibrated_neighbours(m, s, [99.0], [2.0], 2)[0].tolist() == [5, 4]        # (6, 4): 1, then 4
    assert calibrated_neighbours(m, np.full(6, 0.3), [1.5], [7.0], 3)[0].tolist() == [2, 1, 3]
    # rank, not value: a monotone transform of either column changes nothing
    assert np.array_equal(calibrated_neighbours(m, s, [2.5, -1.0], [1.0, 3.0], 4),
                          calibrated_neighbours(np.exp(m), s ** 3, np.exp([2.5, -1.0]), [1.0, 27.0], 4))
    # several candidates, each with its own exclusion (duplicate rows of one plan all left out)
    nb = calibrated_neighbours(m, s, [2.0, 2.0], [1.0, 1.0], 2, exclude=[[2, 3], []])
    assert nb.tolist() == [[1, 0], [2, 3]]                  # 5, then 0 before 4 (8 each); unexcluded: 0, 1
    for bad in (dict(k=0), dict(k=7)):
        with pytest.raises(ValueError):
            calibrated_neighbours(m, s, [1.0], [1.0], **bad)
    with pytest.raises(ValueError):
        calibrated_neighbours(m, s, [1.0], [1.0], 5, exclude=[[0, 1]])          # 4 rows left, k = 5
    with pytest.raises(ValueError):
        calibrated_neighbours(m, s, [1.0], [-1.0], 2)
    with pytest.raises(ValueError):
        calibrated_neighbours(m, s[:-1], [1.0], [1.0], 2)
    with pytest.raises(ValueError):
        calibrated_neighbours(m, s, [1.0], [1.0], 2, exclude=[[9]])


def test_calibrated_surrogate_draws_from_the_neighbours_only():
    """Each candidate's row is one of its k nearest pool rows in rank space, every one of them reached, its own rows
    never; the random numbers are the volatility draw's (one integer in 0..k-1 per candidate)."""
    from hpr_dream.noise import (CalibratedResidualSurrogate, VolatilityResidualSurrogate, calibrated_neighbours,
                                 volatility_neighbours)
    rng = np.random.default_rng(0)
    n = 200
    pm, ps = rng.normal(0, 1, n), np.exp(rng.normal(0, 1.5, n))
    pool = np.stack([np.arange(n, dtype=float), 1000.0 + np.arange(n)], axis=1)
    sg = CalibratedResidualSurrogate(pool, pm, ps, k=10)
    assert sg.describe()["residual_draw"] == "calibrated" and sg.pool_size == n and sg.paired
    own = [np.array([17])] * 4000
    d = sg(np.full(4000, pm[17]), np.random.default_rng(1), volatility=np.full(4000, ps[17]), pool_rows=own)
    rows = np.rint(d.score - pm[17]).astype(int)
    want = calibrated_neighbours(pm, ps, [pm[17]], [ps[17]], 10, exclude=[[17]])[0]
    assert 17 not in want and set(rows.tolist()) == set(want.tolist())
    assert np.allclose(d.verdict_residual, 1000.0 + rows) and d.accept.all()
    # same random numbers as the volatility draw: the j-th neighbour drawn is the same j
    v = VolatilityResidualSurrogate(pool, ps, k=10, eps=1e-3)
    dv = v(np.zeros(50), np.random.default_rng(3), volatility=np.full(50, ps[5]))
    dc = sg(np.full(50, pm[5]), np.random.default_rng(3), volatility=np.full(50, ps[5]), pool_rows=[[]] * 50)
    jv = [list(volatility_neighbours(ps, [ps[5]], 10, 1e-3)[0]).index(int(r)) for r in np.rint(dv.score).astype(int)]
    nb5 = list(calibrated_neighbours(pm, ps, [pm[5]], [ps[5]], 10)[0])
    jc = [nb5.index(int(r)) for r in np.rint(dc.score - pm[5]).astype(int)]
    assert jv == jc
    with pytest.raises(ValueError):
        sg(np.zeros(3), np.random.default_rng(1), pool_rows=[[]] * 3)            # needs volatility=
    with pytest.raises(ValueError):
        sg(np.zeros(3), np.random.default_rng(1), volatility=np.ones(3))         # needs pool_rows=
    with pytest.raises(ValueError):
        CalibratedResidualSurrogate(pool, pm[:-1], ps, k=10)


def test_grader_hands_the_candidates_own_rows_to_the_calibrated_surrogate():
    """SurrogateGrader(volatility=..., pool_rows=...) hands each scored plan's own pool rows to the surrogate, which
    never draws them; pool_rows without volatility is refused."""
    from hpr_dream.noise import CalibratedResidualSurrogate
    n = 40
    X = np.arange(2 * n, dtype=np.int64).reshape(n, 2)              # pool plan j is X[j]
    pm = np.zeros(n)                                                   # every plan alike: neighbours by pool order
    ps = np.zeros(n)
    pool = np.stack([np.arange(n, dtype=float), np.arange(n, dtype=float)], axis=1)
    seen = []

    def rows_of(P):
        seen.append(len(P))
        return [np.array([int(p[0]) // 2]) for p in P]
    gr = SurrogateGrader(CalibratedResidualSurrogate(pool, pm, ps, k=1), OracleCache(lambda P: np.zeros(len(P))),
                         np.random.default_rng(2), volatility=lambda P: np.zeros(len(P)), pool_rows=rows_of)
    r = attack_surrogate(lambda sc: random_shooting(sc, X, n), gr, budget=n)
    assert seen == [n] and r.log["residual_draw"] == "calibrated"
    for j, x in enumerate(X):                     # k = 1, all ties: row 0, or row 1 for plan 0 (its own row left out)
        assert int(gr.lookup(x)[0]) == (1 if j == 0 else 0)
    with pytest.raises(ValueError):
        SurrogateGrader(CalibratedResidualSurrogate(pool, pm, ps, k=1), OracleCache(lambda P: np.zeros(len(P))),
                        np.random.default_rng(2), pool_rows=rows_of)
