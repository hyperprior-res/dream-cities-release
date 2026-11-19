"""Every statistic against a hand-computed case, and every interval against a naive bootstrap."""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats as sps

from hpr_dream import stats as S


def naive_interval(stat, arrays, clusters, n_boot=2000, seed=0, level=0.95):
    """Reference cluster bootstrap: expand each resample explicitly and recompute the statistic."""
    _, codes = np.unique(np.asarray(clusters), return_inverse=True)
    codes = codes.reshape(-1)
    draws = S.cluster_draws(codes.max() + 1, n_boot, seed)
    vals = []
    for d in draws:
        idx = np.concatenate([np.flatnonzero(codes == c) for c in d])
        vals.append(stat(*[np.asarray(a)[idx] for a in arrays]))
    vals = np.asarray(vals, dtype=float)
    ok = np.isfinite(vals)
    lo, hi = np.quantile(vals[ok], [(1 - level) / 2, (1 + level) / 2])
    return lo, hi, int((~ok).sum())


def close(a, b, tol=1e-12):
    assert abs(a - b) <= tol, (a, b)


def check_interval(est, ref):
    lo, hi, und = ref
    close(est.lo, lo, 1e-10)
    close(est.hi, hi, 1e-10)
    assert est.n_boot_undefined == und


# a small clustered data set used by several tests
RNG = np.random.default_rng(7)
CL = np.repeat(np.arange(12), RNG.integers(2, 7, size=12))
N = CL.size
G = RNG.random(N) < 0.6
O = RNG.random(N) < 0.5


def test_hackability_hand():
    g = np.array([1, 1, 0, 1, 0, 1], bool)
    o = np.array([0, 1, 0, 0, 1, 1], bool)
    e = S.hackability(g, o, [0, 0, 1, 1, 2, 2])
    close(e.value, 2 / 6)
    assert (e.n_units, e.n_clusters, e.n_boot) == (6, 3, 2000)


def test_hackability_interval_matches_naive():
    e = S.hackability(G, O, CL)
    check_interval(e, naive_interval(lambda g, o: np.mean(g & ~o), [G, O], CL))


def test_two_cluster_interval_is_exact():
    # cluster a all 0, cluster b all 1, equal sizes: resample means are 0, 0.5, 1 w.p. 1/4, 1/2, 1/4
    g = np.ones(6, bool)
    o = np.array([0, 0, 0, 1, 1, 1], bool)
    e = S.hackability(g, o, ["a"] * 3 + ["b"] * 3)
    close(e.value, 0.5)
    assert (e.lo, e.hi) == (0.0, 1.0)


def test_single_cluster_interval_is_the_point():
    e = S.hackability([1, 0, 1, 1], [0, 0, 1, 0], [5, 5, 5, 5])
    close(e.value, 0.5)
    assert e.lo == e.hi == 0.5


def test_bootstrap_is_seeded_and_shared():
    a = S.hackability(G, O, CL, seed=3)
    b = S.hackability(G, O, CL, seed=3)
    assert a == b
    assert np.array_equal(S.cluster_draws(12, 2000, 3), S.cluster_draws(12, 2000, 3))
    assert not np.array_equal(S.cluster_draws(12, 2000, 3), S.cluster_draws(12, 2000, 4))
    # the interval moves with the seed only through the draws: the naive reference with seed 3 agrees
    check_interval(a, naive_interval(lambda g, o: np.mean(g & ~o), [G, O], CL, seed=3))


def test_cluster_labels_any_type():
    e1 = S.hackability(G, O, CL)
    e2 = S.hackability(G, O, np.array([f"fam{c:02d}" for c in CL]))
    assert e1 == e2


def test_conditional_reject_hand_and_undefined_resamples():
    g = np.array([1, 1, 0, 1, 0, 1], bool)
    o = np.array([0, 1, 0, 0, 1, 1], bool)
    close(S.conditional_reject(g, o, [0, 0, 1, 1, 2, 2]).value, 2 / 4)
    # cluster 1 has no accepts: resamples drawing only cluster 1 are undefined
    g2 = np.array([1, 1, 0, 0], bool)
    o2 = np.array([0, 1, 0, 1], bool)
    cl2 = [0, 0, 1, 1]
    e = S.conditional_reject(g2, o2, cl2)
    d = S.cluster_draws(2, 2000, 0)
    assert e.n_boot_undefined == int((d == 1).all(axis=1).sum()) > 0
    check_interval(e, naive_interval(lambda g, o: np.sum(g & ~o) / np.sum(g) if g.any() else np.nan, [g2, o2], cl2))
    check_interval(S.conditional_reject(G, O, CL),
                   naive_interval(lambda g, o: np.sum(g & ~o) / np.sum(g) if g.any() else np.nan, [G, O], CL))


def test_conditional_mean_hand_and_interval():
    v = np.array([0.25, 0.75, 1.0, 0.5, 0.0, 0.5])
    c = np.array([1, 1, 0, 1, 0, 0], bool)
    cl = [0, 0, 1, 1, 2, 2]
    close(S.conditional_mean(v, c, cl).value, (0.25 + 0.75 + 0.5) / 3)
    close(S.conditional_mean(v, None, cl).value, v.mean())
    # cluster 2 has no unit with the condition: resamples drawing only cluster 2 are undefined
    e = S.conditional_mean(v, c, cl)
    assert e.n_boot_undefined == int((S.cluster_draws(3, 2000, 0) == 2).all(axis=1).sum()) > 0
    V = RNG.random(N)
    check_interval(S.conditional_mean(V, G, CL),
                   naive_interval(lambda x, g: x[g].mean() if g.any() else np.nan, [V, G], CL))
    check_interval(S.conditional_mean(V, None, CL), naive_interval(lambda x: x.mean(), [V], CL))
    # with a 0/1 condition equal to the grader's accept and values the oracle's reject, it is conditional_reject
    assert S.conditional_mean(~O, G, CL) == S.conditional_reject(G, O, CL)
    with pytest.raises(ValueError):
        S.conditional_mean([0.5, np.nan], None, [0, 1])


def test_unlucky_share_hand():
    g = np.array([1, 1, 1, 0, 1], bool)
    o = np.array([0, 0, 1, 0, 0], bool)
    seeds = np.array([[1, 1, 0], [0, 1, 0], [1, 1, 1], [1, 1, 1], [1, 1, 1]], bool)
    # hacked: rows 0, 1, 4; majority (>= 2 of 3): rows 0, 4 -> 2/3
    close(S.unlucky_share(g, o, seeds, [0, 0, 1, 1, 2]).value, 2 / 3)
    # even S: exactly half is not a majority
    s2 = np.array([[1, 0], [1, 1], [0, 0], [0, 0], [0, 1]], bool)
    close(S.unlucky_share(g, o, s2, [0, 0, 1, 1, 2]).value, 1 / 3)


def test_false_rejection_hand():
    close(S.false_rejection([1, 0, 1, 1], [0, 1, 1, 2]).value, 0.25)
    e = S.false_rejection(G, CL)
    check_interval(e, naive_interval(lambda g: np.mean(~g), [G], CL))


def test_dream_overfit_hand():
    gs = [np.array([3, 1, 2.0]), np.array([1, 2, 3, 0.0]), np.array([5, 5, 0.0])]
    os_ = [np.array([0, 5, 4.0]), np.array([1, 2, 3, 4.0]), np.array([1, 9, 5.0])]
    # 1: top cand 0, oracle 0 < median 4 -> 1;  2: top cand 2, oracle 3 vs median 2.5 -> 0;
    # 3: tied tops (oracle 1 and 9) vs median 5 -> (1 + 0) / 2
    e = S.dream_overfit_probability(gs, os_, [0, 1, 2])
    close(e.value, (1 + 0 + 0.5) / 3)
    # rectangular input gives the same as a list of rows
    g2 = np.array([[3, 1, 2.0], [1, 2, 0.0]])
    o2 = np.array([[0, 5, 4.0], [1, 2, 3.0]])
    close(S.dream_overfit_probability(g2, o2, [0, 1]).value, (1 + 0) / 2)


def test_brier_hand_no_within_bin_term():
    p = np.array([0.1, 0.1, 0.5, 0.5, 0.9])
    y = np.array([0, 1, 1, 0, 1], bool)
    d = S.brier_decomposition(p, y, [0, 1, 2, 3, 4])
    close(d.brier.value, 0.266)
    close(d.reliability.value, 0.066)
    close(d.resolution.value, 0.04)
    close(d.uncertainty.value, 0.24)
    close(d.within_bin_variance.value, 0.0)
    close(d.within_bin_covariance.value, 0.0)


def test_brier_hand_with_within_bin_term():
    p = np.array([0.12, 0.18, 0.7, 0.75])
    y = np.array([0, 1, 1, 1], bool)
    d = S.brier_decomposition(p, y, [0, 0, 1, 1])
    close(d.brier.value, 0.209825)
    close(d.reliability.value, 0.0990625)
    close(d.resolution.value, 0.0625)
    close(d.uncertainty.value, 0.1875)
    close(d.within_bin_variance.value, 0.0007625)
    close(d.within_bin_covariance.value, 0.015)
    close(d.within_bin.value, 0.0007625 - 0.015)
    close(d.reliability.value - d.resolution.value + d.uncertainty.value + d.within_bin.value, d.brier.value)


def test_brier_binning_edges():
    d = S.brier_decomposition(np.array([0.0, 0.3, 0.7, 1.0, 0.125, 0.875]), np.zeros(6, bool), np.arange(6))
    counts = np.array(d.bin_counts)
    assert counts[0] == 1 and counts[3] == 1 and counts[7] == 1 and counts[1] == 1 and counts[8] == 1
    assert counts[9] == 1 and counts.sum() == 6


def test_brier_identity_and_interval_on_random_data():
    rng = np.random.default_rng(1)
    p = rng.random(N)
    y = rng.random(N) < p
    d = S.brier_decomposition(p, y, CL)
    close(d.reliability.value - d.resolution.value + d.uncertainty.value + d.within_bin.value, d.brier.value, 1e-12)
    close(d.brier.value, np.mean((p - y) ** 2), 1e-12)
    check_interval(d.brier, naive_interval(lambda p, y: np.mean((p - y) ** 2), [p, y], CL))

    def rel(p, y):
        k = np.minimum((p * 10).astype(int), 9)
        return sum((k == b).sum() * (p[k == b].mean() - y[k == b].mean()) ** 2 for b in range(10) if (k == b).any()) / p.size

    check_interval(d.reliability, naive_interval(rel, [p, y], CL))


def test_log_score_hand():
    e = S.log_score([0.0, 1.0, 0.5], [0, 0, 1], [0, 1, 2], K=8)
    close(e.value, (math.log2(16 / 15) + 4.0 + 1.0) / 3)


def test_auc_hand_and_ties():
    close(S.auc([0.1, 0.4, 0.35, 0.8], [0, 0, 1, 1], [0, 1, 2, 3]).value, 0.75)
    close(S.auc([1, 1, 2, 0], [1, 0, 1, 0], [0, 1, 2, 3]).value, 0.875)


def test_auc_interval_matches_naive():
    rng = np.random.default_rng(2)
    s = np.round(rng.normal(size=N) + O, 1)  # rounded: many ties

    def ref(s, lab):
        if lab.all() or (~lab).all():
            return np.nan
        u = sps.mannwhitneyu(s[lab], s[~lab]).statistic
        return u / (lab.sum() * (~lab).sum())

    e = S.auc(s, O, CL)
    close(e.value, ref(s, O))
    check_interval(e, naive_interval(ref, [s, O], CL))


def test_spearman_kendall_hand():
    x = [1, 2, 3, 4, 5]
    y = [2, 1, 4, 3, 5]
    close(S.clustered_spearman(x, y, [0, 0, 1, 1, 2]).value, 0.8)
    close(S.clustered_kendall(x, y, [0, 0, 1, 1, 2]).value, 0.6)


def test_spearman_kendall_interval_matches_naive():
    rng = np.random.default_rng(3)
    x = rng.normal(size=N)
    y = x + rng.normal(size=N)
    for fn, ref in ((S.clustered_spearman, sps.spearmanr), (S.clustered_kendall, sps.kendalltau)):
        e = fn(x, y, CL)
        check_interval(e, naive_interval(lambda a, b: ref(a, b).statistic, [x, y], CL))


def test_noise_floor_flip_hand():
    close(S.noise_floor_flip(0.5, 0.25, 0.25, 1), 0.125)
    close(S.noise_floor_flip(0.5, 0.25, 0.25, 2), 0.75 * 0.25)
    close(S.noise_floor_flip(0.3, 0.1, 0.2, 1), 0.7 * 0.1)  # B = 1: (1 - pi) fp
    assert S.noise_floor_flip(1.0, 0.3, 0.0, 10) == 0.0  # nothing for the oracle to reject
    assert S.noise_floor_flip(0.0, 0.0, 0.5, 10) == 0.0  # a = 0
    close(S.noise_floor_flip(0.0, 0.2, 0.0, 3), 1 - 0.8**3)
    h = S.noise_floor_flip(np.array([0.5, 0.3]), 0.25, 0.25, np.array([[1], [2]]))
    assert h.shape == (2, 2)
    close(h[1, 0], 0.1875)


def test_noise_floor_flip_monte_carlo():
    # simulate the flip grader directly: B candidates, oracle accepts w.p. pi, flips at fp / fn,
    # pick uniformly among the accepted candidates
    rng = np.random.default_rng(4)
    pi, fp, fn, B, T = 0.3, 0.15, 0.25, 7, 200_000
    o = rng.random((T, B)) < pi
    flip = np.where(o, rng.random((T, B)) < fn, rng.random((T, B)) < fp)
    acc = o ^ flip
    pick = np.argmax(acc + 1e-6 * rng.random((T, B)), axis=1)
    hacked = acc[np.arange(T), pick] & ~o[np.arange(T), pick]
    se = math.sqrt(hacked.mean() * (1 - hacked.mean()) / T)
    assert abs(hacked.mean() - S.noise_floor_flip(pi, fp, fn, B)) < 4 * se


def test_excess_paired():
    r = np.array([1, 0, 1, 0, 1, 1], float)
    f = np.array([0, 0, 1, 1, 0, 1], float)
    e = S.excess(r, f, [0, 0, 1, 1, 2, 2])
    close(e.value, 4 / 6 - 3 / 6)
    same = S.excess(r, r, [0, 0, 1, 1, 2, 2])
    assert same.value == same.lo == same.hi == 0.0
    check_interval(S.excess(G.astype(float), O.astype(float), CL),
                   naive_interval(lambda a, b: a.mean() - b.mean(), [G.astype(float), O.astype(float)], CL))


def test_flip_floor_hand():
    g = np.array([1, 0, 1, 0, 1, 1], bool)
    o = np.array([1, 1, 0, 0, 0, 0], bool)
    inst = np.array([0, 0, 0, 0, 1, 1])
    ff = S.flip_floor(1, g, o, inst, ["a", "b"], hacked=[1.0, 0.0])
    close(ff.fp.value, 3 / 4)
    close(ff.fn.value, 1 / 2)
    close(ff.base_rate.value, 1 / 3)
    close(ff.floor.value, (0.5 * 0.75 + 1.0 * 0.75) / 2)
    close(ff.floor_pooled_base_rate.value, (2 / 3) * 0.75)
    close(ff.excess.value, 0.5 - 0.5625)
    ff3 = S.flip_floor(3, g, o, inst, ["a", "b"])
    close(ff3.floor.value, ((1 - 0.375**3) * 0.375 / 0.625 + (1 - 0.25**3)) / 2)
    assert ff3.excess is None


def test_flip_floor_interval_matches_naive():
    rng = np.random.default_rng(5)
    n_inst = 30
    cl = np.repeat(np.arange(10), 3)
    inst = np.repeat(np.arange(n_inst), 20)
    o = rng.random(inst.size) < rng.uniform(0.1, 0.6, n_inst)[inst]
    g = np.where(o, rng.random(inst.size) > 0.2, rng.random(inst.size) < 0.1)
    hacked = (rng.random(n_inst) < 0.3).astype(float)
    B = 10
    ff = S.flip_floor(B, g, o, inst, cl, hacked=hacked)

    # naive: expand instances per resample (an instance drawn twice counts twice)
    draws = S.cluster_draws(10, 2000, 0)
    floors, exs = [], []
    for d in draws:
        ins = np.concatenate([np.flatnonzero(cl == c) for c in d])
        rows = np.concatenate([np.flatnonzero(inst == i) for i in ins])
        fp = np.sum(g[rows] & ~o[rows]) / np.sum(~o[rows])
        fn = np.sum(~g[rows] & o[rows]) / np.sum(o[rows])
        pis = np.array([o[inst == i].mean() for i in ins])
        fl = np.mean(S.noise_floor_flip(pis, fp, fn, B))
        floors.append(fl)
        exs.append(hacked[ins].mean() - fl)
    lo, hi = np.quantile(floors, [0.025, 0.975])
    close(ff.floor.lo, lo, 1e-10)
    close(ff.floor.hi, hi, 1e-10)
    lo, hi = np.quantile(exs, [0.025, 0.975])
    close(ff.excess.lo, lo, 1e-10)
    close(ff.excess.hi, hi, 1e-10)


def test_input_validation():
    with pytest.raises(ValueError):
        S.hackability([1, 0], [1], [0, 1])
    with pytest.raises(ValueError):
        S.hackability([1, 0], [1, 0], [0])
    with pytest.raises(ValueError):
        S.hackability([2, 0], [1, 0], [0, 1])
    with pytest.raises(ValueError):
        S.brier_decomposition([1.2], [1], [0])
    with pytest.raises(ValueError):
        S.noise_floor_flip(0.5, 1.5, 0.1, 1)
    with pytest.raises(ValueError):
        S.noise_floor_flip(0.5, 0.5, 0.1, 0)


# ------------------------------------------------------------------------------------------ BCa and the zero bound


def naive_bca(stat, arrays, clusters, n_boot=2000, seed=0, level=0.95):
    """Reference BCa: explicit resamples with the package's draws, explicit leave-one-cluster-out."""
    from scipy.special import ndtr, ndtri
    _, codes = np.unique(np.asarray(clusters), return_inverse=True)
    codes = codes.reshape(-1)
    C = codes.max() + 1
    value = stat(*arrays)
    boot = []
    for d in S.cluster_draws(C, n_boot, seed):
        idx = np.concatenate([np.flatnonzero(codes == c) for c in d])
        boot.append(stat(*[np.asarray(a)[idx] for a in arrays]))
    boot = np.array(boot, float)
    boot = boot[np.isfinite(boot)]
    jack = np.array([stat(*[np.asarray(a)[codes != c] for a in arrays]) for c in range(C)], float)
    share = (np.sum(boot < value) + np.sum(boot <= value)) / (2 * boot.size)
    z0 = ndtri(share)
    d = jack.mean() - jack
    a = np.sum(d**3) / (6 * np.sum(d**2) ** 1.5)
    qs = [ndtr(z0 + (z0 + z) / (1 - a * (z0 + z))) for z in (ndtri((1 - level) / 2), ndtri((1 + level) / 2))]
    return tuple(np.quantile(boot, qs))


def test_bca_matches_naive_reference():
    e = S.hackability(G, O, CL, bca=True)
    lo, hi = naive_bca(lambda g, o: np.mean(g & ~o), [G, O], CL)
    close(e.bca_lo, lo, 1e-10)
    close(e.bca_hi, hi, 1e-10)
    rng = np.random.default_rng(11)
    s = rng.normal(size=N) + O
    e = S.auc(s, O, CL, bca=True)

    def ref(s, lab):
        return sps.mannwhitneyu(s[lab], s[~lab]).statistic / (lab.sum() * (~lab).sum())

    lo, hi = naive_bca(ref, [s, O], CL)
    close(e.bca_lo, lo, 1e-10)
    close(e.bca_hi, hi, 1e-10)
    x = rng.normal(size=N)
    y = x + rng.normal(size=N)
    e = S.clustered_spearman(x, y, CL, bca=True)
    lo, hi = naive_bca(lambda a, b: sps.spearmanr(a, b).statistic, [x, y], CL)
    close(e.bca_lo, lo, 1e-10)
    close(e.bca_hi, hi, 1e-10)


def test_bca_off_by_default_and_percentile_unchanged():
    a = S.hackability(G, O, CL)
    b = S.hackability(G, O, CL, bca=True)
    assert math.isnan(a.bca_lo) and math.isnan(a.bca_hi)
    assert (a.value, a.lo, a.hi) == (b.value, b.lo, b.hi)


def test_zero_hacked_gives_exact_binomial_upper_bound_on_clusters():
    g = np.ones(200, bool)
    o = np.ones(200, bool)  # nothing hacked
    cl = np.repeat(np.arange(40), 5)
    e = S.hackability(g, o, cl, bca=True)
    assert e.value == 0.0 and e.lo == 0.0
    close(e.hi, 1 - 0.05 ** (1 / 40))
    close(e.hi, 0.07216, 1e-5)
    assert e.method == S.ZERO_BOUND_METHOD
    assert (e.bca_lo, e.bca_hi) == (0.0, e.hi)
    # Clopper-Pearson: 0 successes in C trials, one-sided upper limit = beta quantile
    from scipy.stats import beta
    close(e.hi, beta.ppf(0.95, 1, 40), 1e-12)
    # a single hacked unit switches back to the bootstrap
    o2 = o.copy()
    o2[0] = False
    assert S.hackability(g, o2, cl).method != S.ZERO_BOUND_METHOD
