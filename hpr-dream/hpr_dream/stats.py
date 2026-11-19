"""Statistics with cluster-bootstrap intervals.

Every estimator takes per-unit arrays (one entry per task instance, or per plan where stated)
plus ``clusters`` (one label per unit: the start-state family) and returns an :class:`Estimate`:
the statistic on the full sample and a 95 per cent interval from a cluster bootstrap.

Cluster bootstrap: the C distinct cluster labels are sorted (``np.unique``) and numbered 0..C-1.
Resample b draws C cluster numbers uniformly with replacement,
``np.random.default_rng(seed).integers(0, C, size=(n_boot, C))``; every unit of a drawn cluster
enters the resample once per draw (clusters stay whole). The statistic is recomputed on each
resample; resamples on which it is undefined (an empty denominator, a constant ranking) are
dropped and counted in ``n_boot_undefined``. The draws depend only on (seed, n_boot, C), so two
statistics on the same clusters with the same seed use the same resamples; paired statistics
(:func:`excess`, :func:`flip_floor`) compute both arms on each resample.

Intervals:

- percentile (always): the (1 - level)/2 and (1 + level)/2 quantiles of the defined resamples
  (``np.quantile``, linear interpolation);
- BCa (with ``bca=True``, in ``bca_lo``, ``bca_hi``): bias correction z0 = Phi^-1 of the mid-rank
  share of resamples below the estimate, ((# < value) + (# <= value)) / (2 n), acceleration from
  the leave-one-cluster-out jackknife, a = sum d^3 / (6 (sum d^2)^1.5) with d = mean(jack) - jack;
  the interval is the quantiles at Phi(z0 + (z0 + z) / (1 - a (z0 + z))) for z = Phi^-1 of the two
  percentile levels. Undefined (NaN) when z0 is infinite;
- :func:`hackability` with no hacked unit: the interval is [0, u] with u = 1 - (1 - level)^(1/C),
  the exact one-sided binomial (Clopper-Pearson) upper bound on the share of clusters with any
  hacked unit, which bounds the hackability whatever the dependence within clusters; ``method``
  says so. The bootstrap would return [0, 0].
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

import numpy as np
from scipy import stats as _sps
from scipy.special import ndtr, ndtri

__all__ = [
    "BrierDecomposition",
    "Estimate",
    "FlipFloor",
    "LEVEL",
    "N_BOOT",
    "ZERO_BOUND_METHOD",
    "auc",
    "brier_decomposition",
    "cluster_draws",
    "clustered_kendall",
    "clustered_spearman",
    "conditional_mean",
    "conditional_reject",
    "dream_overfit_probability",
    "excess",
    "false_rejection",
    "flip_floor",
    "hackability",
    "log_score",
    "noise_floor_flip",
    "unlucky_share",
    "zero_count_upper_bound",
]

N_BOOT = 2000
LEVEL = 0.95
PERCENTILE_METHOD = "cluster bootstrap, percentile"
ZERO_BOUND_METHOD = "no hacked unit: one-sided exact binomial upper bound on clusters"
_NAN = float("nan")


@dataclass(frozen=True)
class Estimate:
    """Point estimate with a cluster-bootstrap interval (see the module docstring)."""

    value: float
    lo: float
    hi: float
    n_units: int
    n_clusters: int
    n_boot: int
    n_boot_undefined: int
    level: float = LEVEL
    method: str = PERCENTILE_METHOD
    bca_lo: float = _NAN
    bca_hi: float = _NAN

    def contains(self, x: float) -> bool:
        return bool(self.lo <= x <= self.hi)

    def excludes_zero(self) -> bool:
        return bool(self.lo > 0 or self.hi < 0)

    def as_dict(self) -> dict:
        return asdict(self)

    def fmt(self, digits: int = 3) -> str:
        return f"{self.value:.{digits}f} [{self.lo:.{digits}f}, {self.hi:.{digits}f}]"

    def __str__(self) -> str:
        return self.fmt()


# --------------------------------------------------------------------------------------------
# bootstrap machinery


def _encode(clusters, n: int | None = None) -> tuple[np.ndarray, int]:
    c = np.asarray(clusters)
    if c.ndim != 1:
        raise ValueError("clusters must be 1-D")
    if n is not None and c.size != n:
        raise ValueError(f"clusters has {c.size} entries for {n} units")
    if c.size == 0:
        raise ValueError("no units")
    _, codes = np.unique(c, return_inverse=True)
    return codes.reshape(-1), int(codes.max()) + 1


def cluster_draws(n_clusters: int, n_boot: int = N_BOOT, seed: int = 0) -> np.ndarray:
    """The resampled cluster numbers, shape (n_boot, n_clusters)."""
    return np.random.default_rng(seed).integers(0, n_clusters, size=(n_boot, n_clusters))


def _weights(n_clusters: int, n_boot: int, seed: int) -> np.ndarray:
    """W[b, c] = number of times cluster c is drawn in resample b."""
    d = cluster_draws(n_clusters, n_boot, seed)
    flat = (d + n_clusters * np.arange(n_boot)[:, None]).ravel()
    return np.bincount(flat, minlength=n_boot * n_clusters).reshape(n_boot, n_clusters).astype(np.float64)


def _jack_weights(n_clusters: int) -> np.ndarray:
    """Leave-one-cluster-out weights, shape (C, C)."""
    return 1.0 - np.eye(n_clusters)


def _csum(codes: np.ndarray, C: int, values: np.ndarray) -> np.ndarray:
    return np.bincount(codes, weights=np.asarray(values, dtype=np.float64), minlength=C)


def _div(a, b):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(b > 0, a / np.where(b > 0, b, 1.0), np.nan)


def _bca(value: float, boot_ok: np.ndarray, jack: np.ndarray | None, level: float) -> tuple[float, float]:
    if jack is None or boot_ok.size == 0 or not np.isfinite(value):
        return _NAN, _NAN
    share = ((boot_ok < value).sum() + (boot_ok <= value).sum()) / (2.0 * boot_ok.size)
    if share <= 0.0 or share >= 1.0:
        return _NAN, _NAN
    z0 = float(ndtri(share))
    jk = jack[np.isfinite(jack)]
    d = jk.mean() - jk if jk.size else np.zeros(0)
    den = 6.0 * float((d * d).sum()) ** 1.5
    a = float((d**3).sum()) / den if den > 0 else 0.0
    out = []
    for z in (ndtri((1 - level) / 2), ndtri((1 + level) / 2)):
        t = 1.0 - a * (z0 + z)
        if t <= 0:
            return _NAN, _NAN
        out.append(float(ndtr(z0 + (z0 + z) / t)))
    lo, hi = np.quantile(boot_ok, out)
    return float(lo), float(hi)


def _finish(value: float, boot: np.ndarray, n_units: int, C: int, n_boot: int, level: float,
            jack: np.ndarray | None = None) -> Estimate:
    ok = np.isfinite(boot)
    n_und = int((~ok).sum())
    if ok.any() and np.isfinite(value):
        lo, hi = np.quantile(boot[ok], [(1 - level) / 2, (1 + level) / 2])
    else:
        lo = hi = _NAN
    blo, bhi = _bca(value, boot[ok], jack, level)
    return Estimate(float(value), float(lo), float(hi), int(n_units), int(C), int(n_boot), n_und, float(level),
                    PERCENTILE_METHOD, blo, bhi)


def _from_weights(stat: Callable[[np.ndarray], np.ndarray], C: int, n_units: int, n_boot: int, seed: int,
                  level: float, bca: bool) -> list[Estimate]:
    """``stat(W)`` maps cluster weights (rows, C) to statistics (rows,) or (rows, k)."""
    point = np.atleast_1d(stat(np.ones((1, C)))[0])
    boot = stat(_weights(C, n_boot, seed)).reshape(n_boot, -1)
    jack = stat(_jack_weights(C)).reshape(C, -1) if bca else None
    return [_finish(point[j], boot[:, j], n_units, C, n_boot, level, None if jack is None else jack[:, j])
            for j in range(point.size)]


def _ratio(num, den, clusters, n_boot: int = N_BOOT, seed: int = 0, level: float = LEVEL,
           bca: bool = False) -> Estimate:
    """sum(num) / sum(den) over units, resampled by cluster."""
    num = np.asarray(num, dtype=np.float64).reshape(-1)
    den = np.asarray(den, dtype=np.float64).reshape(-1)
    codes, C = _encode(clusters, num.size)
    sn, sd = _csum(codes, C, num), _csum(codes, C, den)
    return _from_weights(lambda W: _div(W @ sn, W @ sd), C, num.size, n_boot, seed, level, bca)[0]


def _bool(x, name: str, n: int | None = None) -> np.ndarray:
    a = np.asarray(x)
    if a.dtype != bool:
        if not np.isin(a, (0, 1)).all():
            raise ValueError(f"{name} must be boolean (or 0/1)")
        a = a.astype(bool)
    if n is not None and a.shape[0] != n:
        raise ValueError(f"{name} has {a.shape[0]} entries, expected {n}")
    return a


def zero_count_upper_bound(n_clusters: int, level: float = LEVEL) -> float:
    """Exact one-sided binomial upper bound for 0 events in ``n_clusters`` trials: 1 - (1 - level)^(1/C)."""
    return float(1.0 - (1.0 - level) ** (1.0 / int(n_clusters)))


# --------------------------------------------------------------------------------------------
# hackability family


def hackability(grader_accept, oracle_accept, clusters, *, n_boot: int = N_BOOT, seed: int = 0,
                level: float = LEVEL, bca: bool = False) -> Estimate:
    """Mean over units of (grader accepts and oracle rejects).

    With no hacked unit the interval is [0, 1 - (1 - level)^(1/C)] (see the module docstring)."""
    g = _bool(grader_accept, "grader_accept").reshape(-1)
    o = _bool(oracle_accept, "oracle_accept", g.size).reshape(-1)
    hacked = g & ~o
    e = _ratio(hacked, np.ones(g.size), clusters, n_boot, seed, level, bca)
    if hacked.any():
        return e
    u = zero_count_upper_bound(e.n_clusters, level)
    return Estimate(0.0, 0.0, u, e.n_units, e.n_clusters, e.n_boot, e.n_boot_undefined, e.level,
                    ZERO_BOUND_METHOD, 0.0 if bca else _NAN, u if bca else _NAN)


def conditional_reject(grader_accept, oracle_accept, clusters, *, n_boot: int = N_BOOT, seed: int = 0,
                       level: float = LEVEL, bca: bool = False) -> Estimate:
    """P(oracle rejects | grader accepts) = #(accept and reject) / #(accept)."""
    g = _bool(grader_accept, "grader_accept").reshape(-1)
    o = _bool(oracle_accept, "oracle_accept", g.size).reshape(-1)
    return _ratio(g & ~o, g, clusters, n_boot, seed, level, bca)


def unlucky_share(grader_accept, oracle_accept_primary, oracle_accept_seeds, clusters, *,
                  n_boot: int = N_BOOT, seed: int = 0, level: float = LEVEL, bca: bool = False) -> Estimate:
    """Among hacked units (grader accepts, oracle rejects on the primary seed), the share the oracle
    accepts on a strict majority (more than half) of its other seeds."""
    g = _bool(grader_accept, "grader_accept").reshape(-1)
    o = _bool(oracle_accept_primary, "oracle_accept_primary", g.size).reshape(-1)
    s = _bool(oracle_accept_seeds, "oracle_accept_seeds", g.size)
    if s.ndim != 2 or s.shape[1] < 1:
        raise ValueError("oracle_accept_seeds must have shape (n, S) with S >= 1")
    majority = 2 * s.sum(axis=1) > s.shape[1]
    hacked = g & ~o
    return _ratio(hacked & majority, hacked, clusters, n_boot, seed, level, bca)


def conditional_mean(values, condition, clusters, *, n_boot: int = N_BOOT, seed: int = 0,
                     level: float = LEVEL, bca: bool = False) -> Estimate:
    """Mean of ``values`` over the units where ``condition`` holds: sum(values * condition) /
    sum(condition), resampled by cluster (resamples with no such unit are undefined). ``condition``
    None: the plain mean over all units (e.g. an acceptance rate, or an oracle's mean pass share)."""
    v = np.asarray(values, dtype=np.float64).reshape(-1)
    if np.isnan(v).any():
        raise ValueError("NaN value")
    c = np.ones(v.size, bool) if condition is None else _bool(condition, "condition", v.size).reshape(-1)
    return _ratio(np.where(c, v, 0.0), c, clusters, n_boot, seed, level, bca)


def false_rejection(grader_accept_on_verified, clusters, *, n_boot: int = N_BOOT, seed: int = 0,
                    level: float = LEVEL, bca: bool = False) -> Estimate:
    """Share of oracle-verified plans (one unit per plan) that the grader rejects."""
    g = _bool(grader_accept_on_verified, "grader_accept_on_verified").reshape(-1)
    return _ratio(~g, np.ones(g.size), clusters, n_boot, seed, level, bca)


def dream_overfit_probability(grader_scores, oracle_scores, clusters, *, n_boot: int = N_BOOT,
                              seed: int = 0, level: float = LEVEL, bca: bool = False) -> Estimate:
    """Per instance: does the grader's top-ranked candidate score strictly below the median of the
    oracle's scores over the same candidate set? Mean over instances.

    ``grader_scores`` and ``oracle_scores``: shape (n, M), or sequences of n 1-D arrays (candidate
    sets may differ in size). Ties for the grader's top rank count fractionally: the indicator is
    averaged over the tied top candidates (its expectation under uniform tie-breaking).
    """
    gs, os_ = list(grader_scores), list(oracle_scores)
    if len(gs) != len(os_):
        raise ValueError("grader_scores and oracle_scores have different numbers of instances")
    ind = np.empty(len(gs))
    for i, (g, o) in enumerate(zip(gs, os_)):
        g = np.asarray(g, dtype=np.float64).reshape(-1)
        o = np.asarray(o, dtype=np.float64).reshape(-1)
        if g.size != o.size or g.size == 0:
            raise ValueError(f"instance {i}: candidate sets differ in size or are empty")
        if np.isnan(g).any() or np.isnan(o).any():
            raise ValueError(f"instance {i}: NaN score")
        top = g == g.max()
        ind[i] = float((o[top] < np.median(o)).mean())
    return _ratio(ind, np.ones(ind.size), clusters, n_boot, seed, level, bca)


# --------------------------------------------------------------------------------------------
# probabilistic scores

_BRIER_NAMES = ("brier", "reliability", "resolution", "uncertainty", "within_bin_variance",
                "within_bin_covariance", "within_bin")


@dataclass(frozen=True)
class BrierDecomposition:
    """Brier score and its decomposition, each with a cluster-bootstrap interval.

    brier = reliability - resolution + uncertainty + within_bin_variance - within_bin_covariance
    (exact). ``within_bin`` = within_bin_variance - within_bin_covariance is the term by which the
    classical three-term Murphy decomposition misses the score; it is zero when every forecast in
    a bin is equal.
    """

    brier: Estimate
    reliability: Estimate
    resolution: Estimate
    uncertainty: Estimate
    within_bin_variance: Estimate
    within_bin_covariance: Estimate
    within_bin: Estimate
    bins: int
    edges: tuple
    bin_counts: tuple
    binning: str

    def as_dict(self) -> dict:
        out = {k: getattr(self, k).as_dict() for k in _BRIER_NAMES}
        out.update(bins=self.bins, edges=list(self.edges), bin_counts=list(self.bin_counts), binning=self.binning)
        return out


def _brier_terms(T: np.ndarray) -> np.ndarray:
    """T[..., k, :] = (n, sum p, sum y, sum p^2, sum p*y) for bin k. Returns [..., 7] terms."""
    n, sp, sy, spp, spy = (T[..., i] for i in range(5))
    N = n.sum(-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        safe = np.where(n > 0, n, 1.0)
        pbar = np.where(n > 0, sp / safe, 0.0)
        obar_k = np.where(n > 0, sy / safe, 0.0)
        obar = sy.sum(-1) / N
        brier = (spp.sum(-1) - 2 * spy.sum(-1) + sy.sum(-1)) / N
        rel = (n * (pbar - obar_k) ** 2).sum(-1) / N
        res = (n * (obar_k - obar[..., None]) ** 2).sum(-1) / N
        unc = obar * (1 - obar)
        wbv = (spp - n * pbar**2).sum(-1) / N
        wbc = 2 * (spy - n * pbar * obar_k).sum(-1) / N
    out = np.stack([brier, rel, res, unc, wbv, wbc, wbv - wbc], axis=-1)
    return np.where((N > 0)[..., None], out, np.nan)


def _bin_index(p: np.ndarray, bins: int) -> tuple[np.ndarray, np.ndarray]:
    edges = np.arange(bins + 1) / bins  # exact k / bins
    k = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, bins - 1)
    return k, edges


def brier_decomposition(p, y, clusters, bins: int = 10, *, n_boot: int = N_BOOT, seed: int = 0,
                        level: float = LEVEL, bca: bool = False) -> BrierDecomposition:
    """Brier score of forecasts ``p`` against outcomes ``y`` with the Murphy decomposition.

    Binning: ``bins`` equal-width bins [k/bins, (k+1)/bins), the last closed at 1. Within bin k,
    pbar_k and obar_k are the mean forecast and outcome frequency. With obar the overall outcome
    frequency and N the number of forecasts:
    reliability = sum_k n_k (pbar_k - obar_k)^2 / N; resolution = sum_k n_k (obar_k - obar)^2 / N;
    uncertainty = obar (1 - obar); within_bin_variance = sum_i (p_i - pbar_k(i))^2 / N;
    within_bin_covariance = 2 sum_i (p_i - pbar_k(i)) (y_i - obar_k(i)) / N (Stephenson et al. 2008).
    """
    p = np.asarray(p, dtype=np.float64).reshape(-1)
    y = _bool(y, "y", p.size).reshape(-1).astype(np.float64)
    if np.isnan(p).any() or (p < 0).any() or (p > 1).any():
        raise ValueError("p must lie in [0, 1]")
    bins = int(bins)
    codes, C = _encode(clusters, p.size)
    k, edges = _bin_index(p, bins)
    feats = np.stack([np.ones_like(p), p, y, p * p, p * y], axis=1)
    S = np.zeros((C, bins, 5))
    np.add.at(S, (codes, k), feats)
    ests = _from_weights(lambda W: _brier_terms(np.einsum("bc,ckf->bkf", W, S)), C, p.size, n_boot, seed, level, bca)
    counts = np.bincount(k, minlength=bins)
    return BrierDecomposition(**dict(zip(_BRIER_NAMES, ests)), bins=bins, edges=tuple(float(e) for e in edges),
                              bin_counts=tuple(int(c) for c in counts),
                              binning=f"{bins} equal-width bins [k/{bins}, (k+1)/{bins}), last bin closed at 1")


def log_score(p, y, clusters, K: int, *, n_boot: int = N_BOOT, seed: int = 0, level: float = LEVEL,
              bca: bool = False) -> Estimate:
    """Mean negative log2-likelihood in bits (lower is better), probabilities clipped to
    [1/(2K), 1 - 1/(2K)] where K is the number of grader samples behind each probability."""
    p = np.asarray(p, dtype=np.float64).reshape(-1)
    y = _bool(y, "y", p.size).reshape(-1)
    K = int(K)
    if K < 1:
        raise ValueError("K must be >= 1")
    eps = 1.0 / (2 * K)
    q = np.clip(p, eps, 1 - eps)
    loss = -np.log2(np.where(y, q, 1 - q))
    return _ratio(loss, np.ones(p.size), clusters, n_boot, seed, level, bca)


# --------------------------------------------------------------------------------------------
# ranking statistics


def _auc_from(P: np.ndarray, Nn: np.ndarray) -> np.ndarray:
    """Weighted Mann-Whitney AUC from per-distinct-score positive and negative weights (..., U)."""
    below = np.cumsum(Nn, axis=-1) - Nn
    num = (P * (below + 0.5 * Nn)).sum(-1)
    den = P.sum(-1) * Nn.sum(-1)
    return _div(num, den)


def auc(score, label, clusters, *, n_boot: int = N_BOOT, seed: int = 0, level: float = LEVEL,
        bca: bool = False) -> Estimate:
    """Area under the ROC curve of ``score`` for ``label`` (P(score_pos > score_neg) + 0.5 P(tie))."""
    s = np.asarray(score, dtype=np.float64).reshape(-1)
    lab = _bool(label, "label", s.size).reshape(-1)
    if np.isnan(s).any():
        raise ValueError("NaN score")
    codes, C = _encode(clusters, s.size)
    u, inv = np.unique(s, return_inverse=True)
    U = u.size
    inv = inv.reshape(-1)
    Mp = np.bincount(codes[lab] * U + inv[lab], minlength=C * U).reshape(C, U).astype(np.float64)
    Mn = np.bincount(codes[~lab] * U + inv[~lab], minlength=C * U).reshape(C, U).astype(np.float64)
    chunk = max(1, int(2e7 // max(U, 1)))

    def stat(W):
        return np.concatenate([_auc_from(W[i : i + chunk] @ Mp, W[i : i + chunk] @ Mn) for i in range(0, W.shape[0], chunk)])

    return _from_weights(stat, C, s.size, n_boot, seed, level, bca)[0]


def _members(codes: np.ndarray, C: int) -> list[np.ndarray]:
    order = np.argsort(codes, kind="stable")
    bounds = np.concatenate([[0], np.cumsum(np.bincount(codes, minlength=C))])
    return [order[bounds[c] : bounds[c + 1]] for c in range(C)]


def _corr_boot(fn, x, y, clusters, n_boot, seed, level, bca) -> Estimate:
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    if x.size != y.size:
        raise ValueError("x and y differ in length")
    codes, C = _encode(clusters, x.size)

    def stat(ix):
        xs, ys = x[ix], y[ix]
        if xs.size < 2 or np.ptp(xs) == 0 or np.ptp(ys) == 0:
            return np.nan
        return float(fn(xs, ys).statistic)

    value = stat(np.arange(x.size))
    mem = _members(codes, C)
    draws = cluster_draws(C, n_boot, seed)
    boot = np.array([stat(np.concatenate([mem[c] for c in d])) for d in draws])
    jack = np.array([stat(np.flatnonzero(codes != c)) for c in range(C)]) if bca else None
    return _finish(value, boot, x.size, C, n_boot, level, jack)


def clustered_spearman(x, y, clusters, *, n_boot: int = N_BOOT, seed: int = 0, level: float = LEVEL,
                       bca: bool = False) -> Estimate:
    """Spearman rank correlation over all units (mid-ranks for ties), cluster-bootstrap interval."""
    return _corr_boot(_sps.spearmanr, x, y, clusters, n_boot, seed, level, bca)


def clustered_kendall(x, y, clusters, *, n_boot: int = N_BOOT, seed: int = 0, level: float = LEVEL,
                      bca: bool = False) -> Estimate:
    """Kendall tau-b over all units, cluster-bootstrap interval."""
    return _corr_boot(_sps.kendalltau, x, y, clusters, n_boot, seed, level, bca)


# --------------------------------------------------------------------------------------------
# noise floors


def noise_floor_flip(base_rate, fp, fn, B):
    """Closed-form hackability of random shooting with budget B against a grader that flips the
    oracle's verdict independently per candidate (fp = P(accept | oracle rejects), fn =
    P(reject | oracle accepts)) and picks uniformly among the candidates it accepts:

        hackability = (1 - (1 - a)^B) (1 - pi) fp / a,   a = pi (1 - fn) + (1 - pi) fp,

    and 0 where a = 0. Broadcasts over array arguments. This is the noise floor of verdict-scored
    selection (the attacker sees accept / reject only); see the README for margin-scored attackers.
    """
    pi, fp_, fn_, b = np.broadcast_arrays(*(np.asarray(v, dtype=np.float64) for v in (base_rate, fp, fn, B)))
    for nm, v in (("base_rate", pi), ("fp", fp_), ("fn", fn_)):
        if np.isnan(v).any() or (v < 0).any() or (v > 1).any():
            raise ValueError(f"{nm} must lie in [0, 1]")
    if (b < 1).any() or (b != np.round(b)).any():
        raise ValueError("B must be a positive integer")
    a = pi * (1 - fn_) + (1 - pi) * fp_
    with np.errstate(invalid="ignore", divide="ignore"):
        hit = -np.expm1(b * np.log1p(-np.minimum(a, 1.0)))  # 1 - (1 - a)^B, accurate for small a
        h = np.where(a > 0, hit * (1 - pi) * fp_ / np.where(a > 0, a, 1.0), 0.0)
    return float(h) if h.ndim == 0 else h


def excess(hack_real, hack_floor, clusters, *, n_boot: int = N_BOOT, seed: int = 0, level: float = LEVEL,
           bca: bool = False) -> Estimate:
    """Mean of (hack_real - hack_floor) over units, both arms on the same cluster resamples.

    Arms are per-unit 0/1 indicators or per-unit expectations (e.g. a closed-form floor)."""
    r = np.asarray(hack_real, dtype=np.float64).reshape(-1)
    f = np.asarray(hack_floor, dtype=np.float64).reshape(-1)
    if r.size != f.size:
        raise ValueError("arms differ in length")
    return _ratio(r - f, np.ones(r.size), clusters, n_boot, seed, level, bca)


@dataclass(frozen=True)
class FlipFloor:
    """The flip closed form evaluated on measured behaviour rates (see :func:`flip_floor`)."""

    B: int
    floor: Estimate  # mean over instances of noise_floor_flip(pi_i, fp, fn, B)
    floor_pooled_base_rate: Estimate  # noise_floor_flip(pooled pi, fp, fn, B)
    fp: Estimate
    fn: Estimate
    base_rate: Estimate  # pooled
    excess: Estimate | None  # mean(hacked) - floor, paired
    n_behaviour_plans: int

    def as_dict(self) -> dict:
        return {k: (getattr(self, k).as_dict() if isinstance(getattr(self, k), Estimate) else getattr(self, k))
                for k in ("B", "floor", "floor_pooled_base_rate", "fp", "fn", "base_rate", "excess", "n_behaviour_plans")}


def flip_floor(B: int, beh_grader_accept, beh_oracle_accept, beh_instance, clusters, hacked=None, *,
               n_boot: int = N_BOOT, seed: int = 0, level: float = LEVEL, bca: bool = False) -> FlipFloor:
    """Flip noise floor for verdict-scored random shooting at budget ``B`` from behaviour verdicts.

    Instances are numbered 0..n-1; ``clusters`` (n,) gives each instance's cluster. Behaviour
    plan j belongs to instance ``beh_instance[j]`` and has verdicts ``beh_grader_accept[j]``,
    ``beh_oracle_accept[j]``. fp = #(grader accepts, oracle rejects) / #(oracle rejects) and fn =
    #(grader rejects, oracle accepts) / #(oracle accepts), pooled over behaviour plans; pi_i is
    instance i's oracle acceptance rate. ``floor`` = mean_i noise_floor_flip(pi_i, fp, fn, B);
    ``floor_pooled_base_rate`` uses one pooled pi instead (it differs from ``floor`` when pi varies
    across instances because the closed form is nonlinear in pi). On every resample fp, fn, the
    pi_i and, if ``hacked`` (n,) is given, the real hackability are recomputed together, so
    ``excess`` = mean(hacked) - floor has a paired interval that includes the uncertainty of the
    measured rates.
    """
    B = int(B)
    g = _bool(beh_grader_accept, "beh_grader_accept").reshape(-1)
    o = _bool(beh_oracle_accept, "beh_oracle_accept", g.size).reshape(-1)
    inst = np.asarray(beh_instance).reshape(-1)
    if inst.size != g.size or not np.issubdtype(inst.dtype, np.integer):
        raise ValueError("beh_instance must be integer instance numbers, one per behaviour plan")
    codes, C = _encode(clusters)
    n = codes.size
    if inst.min() < 0 or inst.max() >= n:
        raise ValueError("beh_instance out of range")
    N_i = np.bincount(inst, minlength=n).astype(np.float64)
    if (N_i == 0).any():
        raise ValueError(f"{int((N_i == 0).sum())} instances have no behaviour plans")
    A_i = np.bincount(inst, weights=o.astype(float), minlength=n)
    FPn = np.bincount(inst, weights=(g & ~o).astype(float), minlength=n)
    FNn = np.bincount(inst, weights=(~g & o).astype(float), minlength=n)
    FPd, FNd = N_i - A_i, A_i
    pi_i = A_i / N_i
    h = None
    if hacked is not None:
        h = np.asarray(hacked, dtype=np.float64).reshape(-1)
        if h.size != n:
            raise ValueError("hacked must have one entry per instance")

    def stat(W):
        wt = W[:, codes]  # (rows, n) instance weights
        fp, fn = _div(wt @ FPn, wt @ FPd), _div(wt @ FNn, wt @ FNd)
        pi_pool = _div(wt @ A_i, wt @ N_i)
        ok = np.isfinite(fp) & np.isfinite(fn)
        fp_s, fn_s = np.where(ok, fp, 0.0), np.where(ok, fn, 0.0)
        H = noise_floor_flip(pi_i[None, :], fp_s[:, None], fn_s[:, None], B)
        floor = np.where(ok, _div((wt * H).sum(1), wt.sum(1)), np.nan)
        pooled = np.where(ok, np.asarray(noise_floor_flip(np.nan_to_num(pi_pool), fp_s, fn_s, B), float), np.nan)
        ex = np.full(W.shape[0], np.nan) if h is None else _div(wt @ h, wt.sum(1)) - floor
        return np.stack([fp, fn, pi_pool, floor, pooled, ex], axis=1)

    e = _from_weights(stat, C, n, n_boot, seed, level, bca)
    return FlipFloor(B=B, floor=e[3], floor_pooled_base_rate=e[4], fp=e[0], fn=e[1], base_rate=e[2],
                     excess=e[5] if h is not None else None, n_behaviour_plans=int(g.size))
