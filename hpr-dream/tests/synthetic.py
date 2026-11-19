"""Synthetic audit problems with known truth, for the end-to-end checks of the specification (6.5).

Plan space (D = 13): eight categorical columns with 5 values, four integer columns in [0, 20],
one categorical column with 3 values frozen at 1.

Behaviour distribution (shared by all instances): categorical column j has probabilities
roll((0.30, 0.25, 0.20, 0.15, 0.10), j); integer column k is Binomial(20, (0.35, 0.45, 0.55,
0.65)[k]); the frozen column is 1.

Instances: n_clusters x per_cluster. Cluster c draws a value table A_c (8 x 5, standard normal),
integer targets t_c (uniform 0..20) and a difficulty q_c ~ U(0.5, 0.95); its instances perturb
them (A_i = A_c + 0.5 N(0, 1), t_i = clip(t_c + U{-2..2}, 0, 20), q_i = q_c + U(-0.03, 0.03)).
Raw quality s_i(x) = sum_j A_i[j, x_j] - sum_k (x_{8+k} - t_ik)^2 / 50. The task is calibrated on
the behaviour distribution, as real tasks are: on 4,000 reference behaviour plans, tau_i is the
q_i quantile of s_i and sd_i its standard deviation, and the oracle margin is
m_i(x) = (s_i(x) - tau_i) / sd_i, so about 1 - q_i of behaviour plans pass.

Grader: sample k of the grader's margin is m_i(x) + noise_sd * e_i(x) + sample_sd * xi_k.
e_i(x) is standard normal, independent across plans and instances, and a fixed function of
(instance, plan) (computed from a hash), as a learned grader's per-plan error is; xi_k is standard
normal, drawn afresh for every sample of every call (the grader's sampling noise). The attacker's
score is the mean of K = 2 samples; the verdict re-scores a plan on 8 fresh samples and accepts
when at least 4 pass (success probability = share passing). sample_sd = 0 gives the all-K-equal
grader: every sample equals m_i(x) + noise_sd * e_i(x).

Hole (check 2): the region R = {x_0 = 2, x_1 = 3, x_2 = 4} (each value has behaviour probability
0.20, so R holds 0.8 % of behaviour plans). In R the oracle margin is hole_oracle_margin (-1: the
task fails) and the grader margin is m_i(x) + noise_sd * e_i(x) + hole_bonus (3 sd of the
behaviour quality), where m_i is the margin the plan would have had without the hole.
"""

from __future__ import annotations

import numpy as np
from scipy.special import ndtri

from hpr_dream import Space

N_CAT, N_VAL, N_INT, INT_HIGH = 8, 5, 4, 20
BEH_BASE = np.array([0.30, 0.25, 0.20, 0.15, 0.10])
BEH_INT_Q = np.array([0.35, 0.45, 0.55, 0.65])
HOLE_COLS = np.array([0, 1, 2])
HOLE_VALUES = np.array([(2 + j) % N_VAL for j in HOLE_COLS])  # value with behaviour probability 0.20

_U64 = np.uint64


def _splitmix64(x: np.ndarray) -> np.ndarray:
    z = x + _U64(0x9E3779B97F4A7C15)
    z = (z ^ (z >> _U64(30))) * _U64(0xBF58476D1CE4E5B9)
    z = (z ^ (z >> _U64(27))) * _U64(0x94D049BB133111EB)
    return z ^ (z >> _U64(31))


class Problem:
    def __init__(self, seed: int, *, n_clusters: int = 40, per_cluster: int = 5, noise_sd: float = 0.5,
                 sample_sd: float = 0.0, hole: bool = False, hole_bonus: float = 3.0, hole_oracle_margin: float = -1.0, n_ref: int = 4000):
        ss = np.random.SeedSequence(seed)
        s_param, s_ref, s_hash = ss.spawn(3)
        rng = np.random.default_rng(s_param)
        self.space = Space.concat(
            Space.categorical_columns([N_VAL] * N_CAT),
            Space.integer_columns([0] * N_INT, [INT_HIGH] * N_INT),
            Space.categorical_columns([3]).freeze([0], [1]),
        )
        self.beh_cat = np.stack([np.roll(BEH_BASE, j) for j in range(N_CAT)])
        self.beh_cdf = np.cumsum(self.beh_cat, axis=1)
        n = n_clusters * per_cluster
        self.n = n
        self.cluster = np.repeat(np.arange(n_clusters), per_cluster)
        A_c = rng.normal(size=(n_clusters, N_CAT, N_VAL))
        t_c = rng.integers(0, INT_HIGH + 1, size=(n_clusters, N_INT))
        q_c = rng.uniform(0.5, 0.95, size=n_clusters)
        self.A = A_c[self.cluster] + 0.5 * rng.normal(size=(n, N_CAT, N_VAL))
        self.t = np.clip(t_c[self.cluster] + rng.integers(-2, 3, size=(n, N_INT)), 0, INT_HIGH)
        self.q = np.clip(q_c[self.cluster] + rng.uniform(-0.03, 0.03, size=n), 0.01, 0.99)
        ref = self.behaviour(np.random.default_rng(s_ref), n_ref)
        raw = np.stack([self._raw(i, ref) for i in range(n)])
        self.tau = np.array([np.quantile(raw[i], self.q[i]) for i in range(n)])
        self.sd = raw.std(axis=1)
        hr = np.random.default_rng(s_hash)
        self.mult = hr.integers(1, 2**63, size=self.space.D, dtype=np.uint64) * _U64(2) + _U64(1)
        self.salt = hr.integers(0, 2**63, size=n, dtype=np.uint64)
        self.tie_salt = hr.integers(0, 2**63, size=n, dtype=np.uint64)
        self.noise_sd = float(noise_sd)
        self.sample_sd = float(sample_sd)
        self.hole = bool(hole)
        self.hole_bonus = float(hole_bonus)
        self.hole_oracle_margin = float(hole_oracle_margin)

    # behaviour --------------------------------------------------------------------------
    def behaviour(self, rng: np.random.Generator, n: int) -> np.ndarray:
        X = np.empty((n, self.space.D), dtype=np.int64)
        u = rng.random((n, N_CAT))
        X[:, :N_CAT] = (u[:, :, None] >= self.beh_cdf[None, :, :-1]).sum(-1)
        X[:, N_CAT:N_CAT + N_INT] = rng.binomial(INT_HIGH, BEH_INT_Q, size=(n, N_INT))
        X[:, -1] = 1
        return X

    # truth --------------------------------------------------------------------------------
    def _raw(self, i: int, X: np.ndarray) -> np.ndarray:
        cat = self.A[i][np.arange(N_CAT)[None, :], X[:, :N_CAT]].sum(axis=1)
        d = X[:, N_CAT:N_CAT + N_INT] - self.t[i]
        return cat - (d * d).sum(axis=1) / 50.0

    def base_margin(self, i: int, X: np.ndarray) -> np.ndarray:
        return (self._raw(i, X) - self.tau[i]) / self.sd[i]

    def in_hole(self, X: np.ndarray) -> np.ndarray:
        if not self.hole:
            return np.zeros(X.shape[0], bool)
        return (X[:, HOLE_COLS] == HOLE_VALUES).all(axis=1)

    def _uniform(self, salt: np.uint64, X: np.ndarray) -> np.ndarray:
        h = (X.astype(np.uint64) * self.mult).sum(axis=1, dtype=np.uint64) + salt
        z = _splitmix64(_splitmix64(h))
        return ((z >> _U64(11)).astype(np.float64) + 0.5) / 2.0**53

    def noise(self, i: int, X: np.ndarray) -> np.ndarray:
        return ndtri(self._uniform(self.salt[i], X))

    def tie_break(self, i: int, X: np.ndarray) -> np.ndarray:
        return self._uniform(self.tie_salt[i], X)

    def oracle_margin(self, i: int, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X)
        m = self.base_margin(i, X)
        return np.where(self.in_hole(X), self.hole_oracle_margin, m) if self.hole else m

    def grader_margin(self, i: int, X: np.ndarray) -> np.ndarray:
        """The grader's margin without sampling noise (the mean of its samples)."""
        X = np.asarray(X)
        g = self.base_margin(i, X) + self.noise_sd * self.noise(i, X)
        return g + self.hole_bonus * self.in_hole(X) if self.hole else g

    def samples(self, i: int, X: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
        """(n, k) sampled grader margins, sampling noise drawn afresh from ``rng``."""
        g = self.grader_margin(i, X)[:, None]
        if self.sample_sd == 0:
            return np.repeat(g, k, axis=1)
        return g + self.sample_sd * rng.standard_normal((g.shape[0], k))

    def search_score(self, i: int, X: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        """The attacker's score: mean of K = 2 sampled margins."""
        return self.samples(i, X, 2, rng).mean(axis=1)

    def verdict(self, i: int, X: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
        """Re-score on 8 fresh samples: (success probability, 4th-largest sampled margin).
        Accept <=> at least 4 of 8 pass <=> 4th-largest >= 0 <=> probability >= 0.5."""
        s = self.samples(i, X, 8, rng)
        return (s >= 0).mean(axis=1), np.sort(s, axis=1)[:, -4]
