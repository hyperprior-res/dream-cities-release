"""Attackers: search space, CEM distribution, selection rules, budget accounting."""

from __future__ import annotations

import numpy as np
import pytest

from hpr_dream import attack as A
from hpr_dream.attack import BudgetError, Marginals, Space, best_of_n, cem, fit_marginals, random_shooting


def mixed_space():
    return Space.concat(Space.categorical_columns([3, 5, 2]), Space.integer_columns([-4, 0], [4, 50]),
                        Space.categorical_columns([4]).freeze([0], [3]))


class Recorder:
    """score = X @ w, recording every batch it is handed."""

    def __init__(self, w):
        self.w = np.asarray(w, float)
        self.batches = []

    def __call__(self, X):
        self.batches.append(np.array(X))
        return X @ self.w

    @property
    def all(self):
        return np.concatenate(self.batches)


# ------------------------------------------------------------------------------------------ space


def test_space_validation_and_ops():
    sp = mixed_space()
    assert sp.D == 6
    assert list(sp.n_values) == [3, 5, 2, 9, 51, 4]
    rng = np.random.default_rng(0)
    X = sp.sample_uniform(rng, 2000)
    assert sp.contains(X).all()
    assert (X[:, 5] == 3).all()
    assert X[:, 3].min() == -4 and X[:, 3].max() == 4
    clipped = sp.clip(np.array([[9, -1, 5, 10, -3, 0]]))
    assert clipped.tolist() == [[2, 0, 1, 4, 0, 3]]
    assert not sp.contains(np.array([[0, 0, 0, 0, 0, 2]]))[0]  # frozen column at the wrong value
    with pytest.raises(ValueError):
        Space([1], [3], [True])  # categorical must start at 0
    with pytest.raises(ValueError):
        Space([0], [-1], [False])
    with pytest.raises(ValueError):
        Space.categorical_columns([3]).freeze([0], [3])  # frozen value out of range


# ------------------------------------------------------------------------------------------ marginals


def test_uniform_marginals_sample_uniformly():
    sp = mixed_space()
    m = Marginals.uniform_over(sp)
    X = m.sample(np.random.default_rng(1), 60000)
    assert sp.contains(X).all()
    f = np.bincount(X[:, 1], minlength=5) / X.shape[0]
    assert np.abs(f - 0.2).max() < 0.01
    f = np.bincount(X[:, 4], minlength=51) / X.shape[0]
    assert np.abs(f - 1 / 51).max() < 0.004  # integer columns exactly uniform in the first generation


def test_categorical_sampling_matches_probabilities():
    sp = Space.categorical_columns([4, 3, 1])
    m = Marginals(sp, np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.0, 0.5, 1.0]), np.zeros(0), np.zeros(0), np.zeros(0, bool))
    X = m.sample(np.random.default_rng(2), 100000)
    for col, p in ((0, [0.1, 0.2, 0.3, 0.4]), (1, [0.5, 0.0, 0.5]), (2, [1.0])):
        f = np.bincount(X[:, col], minlength=len(p)) / X.shape[0]
        assert np.abs(f - p).max() < 0.006, (col, f)
    assert (X[:, 1] != 1).all()  # zero-probability value never drawn


def test_integer_gaussian_sampling_is_rounded_and_clipped():
    sp = Space.integer_columns([0], [10])
    m = Marginals(sp, np.zeros(0), np.array([9.7]), np.array([2.0]), np.zeros(1, bool))
    X = m.sample(np.random.default_rng(3), 50000)[:, 0]
    assert X.min() >= 0 and X.max() <= 10
    # P(X = 10) = P(9.7 + 2 z >= 9.5) = P(z >= -0.1)
    from scipy.stats import norm
    assert abs((X == 10).mean() - norm.sf(-0.1)) < 0.01


def test_fit_and_floors():
    sp = Space.concat(Space.categorical_columns([4]), Space.integer_columns([0], [100]))
    plans = np.array([[0, 50]] * 10)
    m = fit_marginals(sp, plans, prob_floor=0.01, std_floor=0.5, std_floor_frac=0.02)
    p = m.probs(0)
    assert np.isclose(p.sum(), 1.0) and (p >= 0.01 - 1e-15).all()
    assert np.allclose(p, [0.97, 0.01, 0.01, 0.01])
    mu, sd = m.gaussian(1)
    assert mu == 50.0 and sd == 2.0  # max(0.5, 0.02 * 100)
    # a vector already above the floor is unchanged
    m2 = Marginals(Space.categorical_columns([4]), np.array([0.1, 0.2, 0.3, 0.4]), np.zeros(0), np.zeros(0), np.zeros(0, bool))
    m2.apply_floors(0.01, 0.5, 0.02)
    assert np.allclose(m2.probs(0), [0.1, 0.2, 0.3, 0.4])
    # many values: the floor is capped at 0.5 / n so it never takes more than half the mass
    m3 = fit_marginals(Space.categorical_columns([200]), np.zeros((5, 1), int))
    p3 = m3.probs(0)
    assert np.isclose(p3.min(), 0.5 / 200) and np.isclose(p3.sum(), 1.0)


def test_smoothing_moves_seventy_percent_towards_the_elite_fit():
    sp = Space.concat(Space.categorical_columns([2]), Space.integer_columns([0], [10]))
    m = Marginals(sp, np.array([0.5, 0.5]), np.array([5.0]), np.array([3.0]), np.zeros(1, bool))
    m.smooth_towards(np.array([[1, 9], [1, 7]]), 0.7)
    assert np.allclose(m.probs(0), [0.3 * 0.5, 0.7 + 0.3 * 0.5])
    mu, sd = m.gaussian(1)
    assert np.isclose(mu, 0.7 * 8 + 0.3 * 5) and np.isclose(sd, 0.7 * 1 + 0.3 * 3)


# ------------------------------------------------------------------------------------------ shooting


def test_random_shooting_selection_nesting_and_b1():
    rng = np.random.default_rng(4)
    P = rng.integers(0, 10, size=(100, 3))
    w = np.array([1.0, -1.0, 0.5])
    rec = Recorder(w)
    plan, log = random_shooting(rec, P, 1)
    assert np.array_equal(plan, P[0]) and log["n_scored"] == 1
    for B in (10, 50, 100):
        rec = Recorder(w)
        plan, log = random_shooting(rec, P, B)
        s = P[:B] @ w
        assert np.array_equal(plan, P[int(np.argmax(s))])
        assert np.array_equal(rec.all, P[:B])  # the first B, in order, in one call
        assert log["n_scored"] == B and log["n_score_calls"] == 1 and log["best_score"] == s.max()
    # ties: the first maximiser
    plan, log = random_shooting(lambda X: np.zeros(len(X)), P, 10)
    assert log["best_index"] == 0 and np.array_equal(plan, P[0])
    # the returned plan is a copy
    plan[0] = 12345
    assert P[0, 0] != 12345


def test_best_of_n_is_first_b_over_the_zoo():
    Z = np.arange(30).reshape(10, 3)
    plan, log = best_of_n(lambda X: -X[:, 0].astype(float), Z, 5)
    assert np.array_equal(plan, Z[0]) and log["attacker"] == "best_of_n" and log["n_scored"] == 5


def test_shooting_rejects_bad_inputs():
    P = np.zeros((5, 2), int)
    with pytest.raises(ValueError):
        random_shooting(lambda X: X[:, 0], P, 6)  # fewer proposals than the budget
    with pytest.raises(ValueError):
        random_shooting(lambda X: X[:, 0], P, 0)
    with pytest.raises(TypeError):
        random_shooting(lambda X: X[:, 0], P.astype(float), 2)
    with pytest.raises(ValueError):
        random_shooting(lambda X: np.zeros(len(X) + 1), P, 2)  # wrong output length
    with pytest.raises(ValueError):
        random_shooting(lambda X: np.full(len(X), np.nan), P, 2)


def test_score_cannot_mutate_plans():
    P = np.zeros((5, 2), int)

    def bad(X):
        X[0, 0] = 1
        return X[:, 0]

    with pytest.raises(ValueError):
        random_shooting(bad, P, 3)
    assert (P == 0).all()


def test_batch_size_chunks_are_counted():
    P = np.arange(200).reshape(100, 2)
    rec = Recorder([1.0, 0.0])
    plan, log = random_shooting(rec, P, 100, batch_size=30)
    assert [len(b) for b in rec.batches] == [30, 30, 30, 10]
    assert log["n_scored"] == 100 and log["n_score_calls"] == 4 and log["max_batch"] == 30
    assert np.array_equal(plan, P[99])


# ------------------------------------------------------------------------------------------ cem


def test_cem_schedule():
    assert A.cem_schedule(1) == (1, 1)
    assert A.cem_schedule(10) == (2, 5)
    assert A.cem_schedule(100) == (4, 25)
    assert A.cem_schedule(1000) == (5, 200)
    assert A.cem_schedule(10000) == (10, 1000)
    for B, (g, n) in A.CEM_SCHEDULE.items():
        assert g * n == B
    with pytest.raises(ValueError):
        A.cem_schedule(500)
    sp = mixed_space()
    with pytest.raises(ValueError):
        cem(lambda X: X[:, 0], sp, 500, np.random.default_rng(0), schedule=(5, 99))
    plan, log = cem(lambda X: X[:, 0].astype(float), sp, 500, np.random.default_rng(0), schedule=(5, 100))
    assert log["n_scored"] == 500 and (log["generations"], log["population"]) == (5, 100)


@pytest.mark.parametrize("B", [1, 10, 100, 1000, 10000])
def test_cem_budget_batches_and_best_seen(B):
    sp = mixed_space()
    rec = Recorder(np.random.default_rng(B).normal(size=sp.D))
    plan, log = cem(rec, sp, B, np.random.default_rng(B))
    G, N = A.CEM_SCHEDULE[B]
    assert [len(b) for b in rec.batches] == [N] * G  # one whole population per call
    assert log["n_scored"] == B == len(rec.all)
    s = rec.all @ rec.w
    assert np.array_equal(plan, rec.all[int(np.argmax(s))])  # best seen in the whole run, earliest on ties
    assert log["best_index"] == int(np.argmax(s)) and log["best_score"] == s.max()
    assert sp.contains(rec.all).all()
    assert log["n_elite"] == max(1, -(-N // 10))


def test_cem_b1_is_one_draw_from_init():
    sp = mixed_space()
    init = fit_marginals(sp, sp.sample_uniform(np.random.default_rng(0), 300))
    plan, log = cem(lambda X: X[:, 0].astype(float), sp, 1, np.random.default_rng(42), init)
    expected = init.copy().apply_floors(0.01, 0.5, 0.02).sample(np.random.default_rng(42), 1)[0]
    assert np.array_equal(plan, expected) and log["n_scored"] == 1
    plan_u, _ = cem(lambda X: X[:, 0].astype(float), sp, 1, np.random.default_rng(42), None)
    assert np.array_equal(plan_u, Marginals.uniform_over(sp).sample(np.random.default_rng(42), 1)[0])


def test_cem_init_from_plans_equals_init_from_marginals():
    sp = mixed_space()
    beh = sp.sample_uniform(np.random.default_rng(1), 300)
    f = lambda X: (X * np.arange(1, sp.D + 1)).sum(1).astype(float)
    a = cem(f, sp, 100, np.random.default_rng(3), beh)
    b = cem(f, sp, 100, np.random.default_rng(3), fit_marginals(sp, beh))
    assert np.array_equal(a.plan, b.plan)


def test_cem_optimises_a_separable_problem():
    sp = Space.concat(Space.categorical_columns([6] * 10), Space.integer_columns([0] * 3, [40] * 3))
    target_cat = np.arange(10) % 6
    target_int = np.array([5, 20, 35])

    def f(X):
        return (X[:, :10] == target_cat).sum(1) - np.abs(X[:, 10:] - target_int).sum(1) / 10.0

    best_rs = np.mean([f(sp.sample_uniform(np.random.default_rng(s), 1000)).max() for s in range(5)])
    best_cem = np.mean([cem(f, sp, 1000, np.random.default_rng(s)).log["best_score"] for s in range(5)])
    assert best_cem > best_rs + 1.0
    plan, log = cem(f, sp, 10000, np.random.default_rng(0))
    assert log["best_score"] >= 9.0


def test_cem_frozen_columns_never_move():
    sp = mixed_space()
    rec = Recorder(np.ones(sp.D))
    cem(rec, sp, 1000, np.random.default_rng(5))
    assert (rec.all[:, 5] == 3).all()


def test_counter_raises_budget_error():
    c = A._Counter(lambda X: np.zeros(len(X)), None)
    c(np.zeros((3, 2), int))
    with pytest.raises(BudgetError):
        c.check("x", 4)


# --------------------------------------------------------------------------------------------
# cem_seeded

def block_space(n_blocks=6, block=4):
    """Plans of n_blocks blocks of `block` columns: column 0 of a block categorical (3 values), the rest integer 0..9,
    the last column of every block frozen at 0 (as the audit's forced-disaster column)."""
    one = Space.concat(Space.categorical_columns([3]), Space.integer_columns([0] * (block - 1), [9] * (block - 1)))
    sp = Space.concat(*[one] * n_blocks)
    return sp.freeze([block * m + block - 1 for m in range(n_blocks)], 0)


@pytest.mark.parametrize("B", [1, 10, 100, 1000])
def test_cem_seeded_one_generation_is_random_shooting(B):
    """With one generation (schedule (1, B)) it scores seeds[:B] in one call and selects what random shooting does,
    ties included; at B = 1 the stated schedule is already one generation."""
    sp = block_space()
    rng = np.random.default_rng(0)
    seeds = sp.sample_uniform(rng, 1200)
    w = np.random.default_rng(1).normal(size=sp.D)
    score = lambda X: np.floor(X @ w)                      # integer scores: ties happen
    r = random_shooting(score, seeds, B)
    c = A.cem_seeded(score, sp, B, np.random.default_rng(5), seeds, block=4, schedule=(1, B))
    assert np.array_equal(c.plan, r.plan) and c.log["best_index"] == r.log["best_index"]
    assert c.log["n_scored"] == B == c.log["n_score_calls"] * B and c.log["best_score"] == r.log["best_score"]
    if B == 1:
        d = A.cem_seeded(score, sp, 1, np.random.default_rng(5), seeds, block=4)
        assert np.array_equal(d.plan, seeds[0])


@pytest.mark.parametrize("B", [10, 100, 1000])
def test_cem_seeded_generations_elites_and_block_mutation(B):
    """Stated schedule; generation 0 is seeds[:N]; every later child equals some elite of the plans scored before it
    except in whole replaced blocks; frozen columns stay; the selection is the best of all plans scored."""
    sp = block_space()
    seeds = sp.sample_uniform(np.random.default_rng(2), 300)
    rec = Recorder(np.random.default_rng(3).normal(size=sp.D))
    c = A.cem_seeded(rec, sp, B, np.random.default_rng(4), seeds, block=4)
    G, N = A.cem_schedule(B)
    assert len(rec.batches) == G and all(b.shape == (N, sp.D) for b in rec.batches)
    assert np.array_equal(rec.batches[0], seeds[:N])
    n_e = max(2, int(np.ceil(0.1 * N)))
    assert c.log["n_elite"] == n_e and c.log["generations"] == G and c.log["population"] == N
    P = np.concatenate(rec.batches)
    s = P @ rec.w
    j = int(np.argmax(s))
    assert np.array_equal(c.plan, P[j]) and c.log["best_index"] == j and np.isclose(c.log["best_score"], s[j])
    for g in range(1, G):
        prev = P[:g * N]
        elite = prev[np.argsort(-(prev @ rec.w), kind="stable")[:n_e]]
        assert sp.contains(rec.batches[g]).all()
        # a child keeps each block of its elite with probability 0.75: the elite agreeing with it on the most blocks
        # agrees on 4.5 of 6 in expectation
        agree = [max(int((x.reshape(-1, 4) == e.reshape(-1, 4)).all(axis=1).sum()) for e in elite) for x in rec.batches[g]]
        assert np.mean(agree) >= 3.5
    assert c.log["blocks_replaced"] > 0


def test_cem_seeded_p_replace_extremes_and_repair():
    """p_replace 0: children are copies of elites (after repair); p_replace 1: no block of an elite is kept on
    purpose (children are fresh draws); repair is applied to every child, never to the seeds."""
    sp = block_space()
    seeds = sp.sample_uniform(np.random.default_rng(6), 200)
    rec = Recorder(np.random.default_rng(7).normal(size=sp.D))
    A.cem_seeded(rec, sp, 100, np.random.default_rng(8), seeds, block=4, p_replace=0.0)
    elites_seen = {x.tobytes() for x in seeds[:25]}
    for b in rec.batches[1:]:
        assert all(x.tobytes() in elites_seen for x in b)
        elites_seen |= {x.tobytes() for x in b}
    calls = []

    def repair(X):
        calls.append(len(X))
        Y = X.copy()
        Y[:, 1] = 7                                         # an arbitrary canonical form
        return Y

    rec2 = Recorder(rec.w)
    A.cem_seeded(rec2, sp, 100, np.random.default_rng(8), seeds, block=4, p_replace=1.0, repair=repair)
    assert calls == [25, 25, 25] and np.array_equal(rec2.batches[0], seeds[:25])
    assert all((b[:, 1] == 7).all() for b in rec2.batches[1:])
    with pytest.raises(ValueError):
        A.cem_seeded(rec, sp, 100, np.random.default_rng(8), seeds, block=5)          # 5 does not divide 24
    with pytest.raises(ValueError):
        A.cem_seeded(rec, sp, 100, np.random.default_rng(8), seeds[:10], block=4)     # fewer seeds than N
    with pytest.raises(ValueError):
        A.cem_seeded(rec, sp, 100, np.random.default_rng(8), seeds, block=4, schedule=(3, 25))


def test_cem_seeded_climbs_a_block_structured_problem():
    """A plan scores only where a whole block is right (the zone, its road and its wire): column-independent CEM from
    the seeds' marginals and the seeded search at the same budget; the seeded search ends higher."""
    sp = block_space(n_blocks=6, block=4)
    rng = np.random.default_rng(9)
    target = sp.sample_uniform(rng, 1)[0]

    def score(X):
        return (X.reshape(len(X), -1, 4) == target.reshape(-1, 4)).all(axis=2).sum(axis=1).astype(float)

    seeds = sp.sample_uniform(rng, 1000)
    hits = 0
    for k in range(20):
        a = A.cem_seeded(score, sp, 1000, np.random.default_rng(100 + k), seeds, init=seeds, block=4)
        b = cem(score, sp, 1000, np.random.default_rng(100 + k), init=seeds)
        hits += a.log["best_score"] > b.log["best_score"]
    assert hits >= 15
