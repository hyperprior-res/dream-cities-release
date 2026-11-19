"""Noise-only surrogate graders, the shared oracle cache and the surrogate attack.

A surrogate grader is built from the oracle's margin of each candidate plus noise that does not
depend on the plan. Running an attacker against it at the same budget measures how much
hackability a grader with plan-independent errors would produce: the noise floor. Each floor is
matched to one way of scoring candidates:

- :func:`residual_surrogate`: the matched floor for **margin-scored** attackers (the primary ones:
  random shooting and CEM on the grader's mean margin). Score = oracle margin + a residual drawn
  independently per candidate from a pool of grader-minus-oracle residuals measured on behaviour
  plans. It keeps the grader's whole error distribution, bias included, and removes only the
  error's dependence on the plan.

  The pool is either one column of residuals (the score's residual also decides acceptance:
  accept when score >= 0) or **paired**, shape (n, 2): for each behaviour plan, column 0 = the
  search residual (mean of the K = 2 sampled grader margins minus the oracle margin) and column 1
  = the verdict residual (the 4th-largest of 8 fresh sampled grader margins minus the oracle
  margin, so that oracle margin + verdict residual >= 0 exactly when at least 4 of the 8 samples
  pass). One pool row is drawn per candidate: column 0 makes the score handed to the attacker,
  column 1 the surrogate's accept decision.

  Pool size: a pool with fewer rows than the attack budget truncates the residual tail and biases
  the floor low (README, "Residual pool size"). The surrogate refuses such an attack
  (:class:`PoolTooSmall`). ``family_pools`` gives the pooled option: every instance of the same task
  family contributes its rows, each column centred and scaled by its own instance's median and MAD
  and then rescaled to the target instance's median and MAD (:func:`pool_family_residuals`). A
  pooled pool smaller than the budget is refused too.

  :class:`VolatilityResidualSurrogate` is the same surrogate with a draw that follows the candidate's own
  volatility: given each pool row's seed-to-seed standard deviation of the oracle margin and the candidate's,
  the row is drawn uniformly from the k pool rows nearest in log(sd + eps) (:func:`volatility_neighbours`), so
  that a plan whose real outcome varies more across seeds gets the errors of plans like it.

  :class:`CalibratedResidualSurrogate` draws matched on true quality and volatility: given each pool row's mean
  oracle margin m_j and seed-to-seed standard deviation s_j and the candidate's m(y) and s(y), the row is drawn
  uniformly from the k pool rows nearest to the candidate in the plane of the pool's own ranks (u_m, u_s), u_m(x) =
  the share of pool rows with m_j < x, u_s likewise (:func:`calibrated_neighbours`), the rows holding the candidate
  itself left out. Its null: the grader's error depends on a plan only through how good and how volatile the plan
  truly is.
- :func:`flip_surrogate`: the brief's pre-registered baseline and the matched floor for
  **verdict-scored** selection (the attacker sees accept / reject only). The oracle's verdict is
  flipped independently per candidate at rates fp (reject -> accept) and fn (accept -> reject); the
  score is 1 for accept, 0 for reject, plus a uniform tie-breaker in [0, 1e-6). Random shooting
  against it has the closed form :func:`hpr_dream.stats.noise_floor_flip`.

:class:`SurrogateGrader` turns a surrogate into a ``score`` function for an attacker and evaluates
the oracle on every candidate. With ``memo=True`` (default) the surrogate is a fixed random
function of the plan: a plan proposed again (in the same attack, or in another attack sharing the
grader) gets the same draw. :class:`OracleCache` wraps ``oracle_margin`` so that several graders
(e.g. the flip and the residual surrogate of one instance) evaluate each distinct plan once.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, NamedTuple, Sequence

import numpy as np

from .attack import BudgetError, Selected

__all__ = [
    "CalibratedResidualSurrogate",
    "FlipSurrogate",
    "OracleCache",
    "PoolTooSmall",
    "ResidualFamily",
    "ResidualSurrogate",
    "SurrogateDraw",
    "SurrogateGrader",
    "SurrogateResult",
    "VolatilityResidualSurrogate",
    "attack_surrogate",
    "calibrated_neighbours",
    "flip_surrogate",
    "pool_family_residuals",
    "residual_surrogate",
    "volatility_neighbours",
]

TIE_BREAK = 1e-6


class PoolTooSmall(ValueError):
    """A residual pool has fewer rows than the attack budget."""


class SurrogateDraw(NamedTuple):
    score: np.ndarray  # handed to the attacker
    accept: np.ndarray  # the surrogate's verdict
    verdict_residual: np.ndarray | None = None  # paired residual pools: the verdict residual of each drawn row


def _margins(oracle_margin) -> np.ndarray:
    m = np.asarray(oracle_margin, dtype=np.float64).reshape(-1)
    if np.isnan(m).any():
        raise ValueError("NaN oracle margin")
    return m


def flip_surrogate(oracle_margin, fp, fn, rng: np.random.Generator) -> SurrogateDraw:
    """Oracle verdict (margin >= 0) flipped independently per candidate; fp, fn may broadcast."""
    m = _margins(oracle_margin)
    fp = np.broadcast_to(np.asarray(fp, dtype=np.float64), m.shape)
    fn = np.broadcast_to(np.asarray(fn, dtype=np.float64), m.shape)
    if ((fp < 0) | (fp > 1) | (fn < 0) | (fn > 1)).any():
        raise ValueError("fp and fn must lie in [0, 1]")
    o = m >= 0
    u = rng.random(m.size)
    flip = np.where(o, u < fn, u < fp)
    accept = o ^ flip
    score = accept.astype(np.float64) + TIE_BREAK * rng.random(m.size)
    return SurrogateDraw(score, accept)


# --------------------------------------------------------------------------------------------
# residual pools


def _as_pool(pool) -> np.ndarray:
    """(n, 1) or (n, 2) float array."""
    a = np.asarray(pool, dtype=np.float64)
    if a.ndim == 1:
        a = a[:, None]
    if a.ndim != 2 or a.shape[1] not in (1, 2) or a.shape[0] == 0:
        raise ValueError("a residual pool is a non-empty array of shape (n,), (n, 1) or (n, 2)")
    if not np.isfinite(a).all():
        raise ValueError("residual pool must be finite")
    return a


def _med_mad(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    med = np.median(a, axis=0)
    return med, np.median(np.abs(a - med), axis=0)


class ResidualFamily:
    """The residual pools of one task family, each standardised once by its own median and MAD
    (column by column). Pass it as ``family_pools`` to avoid re-standardising for every target.

    ``zero_mad``: "raise" (default) refuses a pool with zero MAD in some column. "centre" applies the
    zero-MAD rule: such a pool's column contributes its residuals centred by its median and unscaled
    (added to the target's median as they are), and a target with zero MAD in a column takes the
    standardised rows scaled by the family's median non-zero MAD of that column. ``n_zero_mad`` counts,
    per column, the instances whose pool took the unscaled path."""

    def __init__(self, family_pools: Sequence, zero_mad: str = "raise"):
        if zero_mad not in ("raise", "centre"):
            raise ValueError("zero_mad must be 'raise' or 'centre'")
        z, d, sc, mads, cols = [], [], [], [], None
        for j, p in enumerate(family_pools):
            a = _as_pool(p)
            if cols is not None and a.shape[1] != cols:
                raise ValueError(f"family pool {j} has {a.shape[1]} columns, pool 0 has {cols}")
            cols = a.shape[1]
            med, mad = _med_mad(a)
            zero = mad == 0
            if zero.any() and zero_mad == "raise":
                raise ValueError(f"family pool {j} has zero MAD in some column")
            scaled = np.broadcast_to(~zero, a.shape)
            z.append(np.where(scaled, (a - med) / np.where(zero, 1.0, mad), 0.0))
            d.append(np.where(scaled, 0.0, a - med))
            sc.append(scaled.copy())
            mads.append(mad)
        if not z:
            raise ValueError("family_pools is empty")
        self.z = np.concatenate(z, axis=0)
        self.d = np.concatenate(d, axis=0)
        self.scaled = np.concatenate(sc, axis=0)
        self.mads = np.stack(mads)
        self.n_instances = len(z)
        self.zero_mad = zero_mad
        self.n_zero_mad = (self.mads == 0).sum(axis=0)
        self.median_nonzero_mad = np.array(
            [float(np.median(c[c > 0])) if (c > 0).any() else 0.0 for c in self.mads.T])

    def __len__(self) -> int:
        return self.n_instances


def pool_family_residuals(target_pool, family_pools, zero_mad: str = "raise") -> np.ndarray:
    """The pooled residual pool for one target instance.

    Every pool in ``family_pools`` (all instances of the target's task family, the target
    included; a list of pools or a :class:`ResidualFamily`) is centred and scaled column by column
    by its own median and median absolute deviation (MAD), stacked, and mapped back with the
    target's median and MAD: r_target = med_t + MAD_t (r_j - med_j) / MAD_j. Rows stay paired. A
    pool with zero MAD in some column cannot be standardised and raises, unless the zero-MAD rule
    is chosen (``zero_mad="centre"``, or a :class:`ResidualFamily` built with it; see there).
    """
    t = _as_pool(target_pool)
    med_t, mad_t = _med_mad(t)
    fam = family_pools if isinstance(family_pools, ResidualFamily) else ResidualFamily(family_pools, zero_mad)
    if fam.z.shape[1] != t.shape[1]:
        raise ValueError(f"family pools have {fam.z.shape[1]} columns, the target {t.shape[1]}")
    if (mad_t == 0).any():
        if fam.zero_mad == "raise":
            raise ValueError("the target pool has zero MAD in some column")
        mad_t = np.where(mad_t > 0, mad_t, fam.median_nonzero_mad)
    return med_t + np.where(fam.scaled, mad_t * fam.z, fam.d)


def _check_budget(rows: int, budget: int | None, pooled: bool) -> None:
    if budget is not None and rows < int(budget):
        kind = "pooled" if pooled else "per-instance"
        hint = "" if pooled else "; pass the task family's pools (pooled option) or a larger pool"
        raise PoolTooSmall(f"{kind} residual pool has {rows} rows, fewer than the budget {int(budget)}{hint}")


def residual_surrogate(oracle_margin, residual_pool, rng: np.random.Generator, *, budget: int | None = None,
                       pooled: bool = False, family_pools: Sequence | None = None) -> SurrogateDraw:
    """Oracle margin plus residual rows drawn uniformly with replacement from the pool.

    ``residual_pool``: the instance's own pool, (n,) or paired (n, 2) (module docstring). With
    ``pooled=True``, ``family_pools`` (the task family's pools) are pooled by
    :func:`pool_family_residuals`. ``budget``: the attack's budget; a pool with fewer rows raises
    :class:`PoolTooSmall`.
    """
    if pooled:
        if family_pools is None:
            raise ValueError("pooled=True needs family_pools")
        pool = pool_family_residuals(residual_pool, family_pools)
    else:
        pool = _as_pool(residual_pool)
    _check_budget(pool.shape[0], budget, pooled)
    return _draw_residual(_margins(oracle_margin), pool, rng)


def _draw_residual(m: np.ndarray, pool: np.ndarray, rng: np.random.Generator) -> SurrogateDraw:
    r = pool[rng.integers(0, pool.shape[0], size=m.size)]
    score = m + r[:, 0]
    accept = (m + r[:, 1] >= 0) if pool.shape[1] == 2 else (score >= 0)
    return SurrogateDraw(score, accept, r[:, 1].copy() if pool.shape[1] == 2 else None)


def volatility_neighbours(pool_sd, cand_sd, k: int, eps: float) -> np.ndarray:
    """(n_cand, k) row indices: for each candidate the ``k`` pool rows whose log(sd + eps) is nearest to the
    candidate's log(sd + eps) (absolute difference; ties by pool order, i.e. the lower row index first)."""
    ps = np.asarray(pool_sd, dtype=np.float64).reshape(-1)
    cs = np.asarray(cand_sd, dtype=np.float64).reshape(-1)
    if not (np.isfinite(ps).all() and np.isfinite(cs).all()) or (ps < 0).any() or (cs < 0).any():
        raise ValueError("standard deviations must be finite and non-negative")
    if not 1 <= int(k) <= ps.size:
        raise ValueError(f"k = {k} must lie in 1..{ps.size} (the pool's rows)")
    if not eps > 0:
        raise ValueError("eps must be positive")
    d = np.abs(np.log(ps + eps)[None, :] - np.log(cs + eps)[:, None])
    return np.argsort(d, axis=1, kind="stable")[:, :int(k)]


@dataclass(eq=False)
class VolatilityResidualSurrogate:
    """Residual surrogate whose draw follows the candidate's own seed-to-seed volatility.

    ``pool``: the instance's paired (or single-column) residual pool, as for :class:`ResidualSurrogate`;
    ``pool_sd``: per pool row, the standard deviation of that plan's oracle margin across the truth seeds.
    For a candidate with standard deviation s (passed as ``volatility`` with the oracle margins; a
    :class:`SurrogateGrader` built with ``volatility=`` does that), the residual row is drawn uniformly from the
    ``k`` pool rows nearest to it in log(sd + eps) (:func:`volatility_neighbours`). A pool whose ``pool_sd`` has no
    spread (every row equal) draws as the plain surrogate does, uniformly from every row and with the same random
    numbers. Everything else (pairing, accept rule) is the plain surrogate's."""

    pool: np.ndarray
    pool_sd: np.ndarray
    k: int
    eps: float
    kind = "residual"
    effective_pool: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
        self.effective_pool = _as_pool(self.pool)
        self.pool_sd = np.asarray(self.pool_sd, dtype=np.float64).reshape(-1)
        if self.pool_sd.size != self.effective_pool.shape[0]:
            raise ValueError(f"pool_sd has {self.pool_sd.size} rows, the pool {self.effective_pool.shape[0]}")
        volatility_neighbours(self.pool_sd, self.pool_sd[:1], self.k, self.eps)          # argument checks
        self.no_spread = bool(np.ptp(self.pool_sd) == 0)

    pooled = False

    @property
    def pool_size(self) -> int:
        return int(self.effective_pool.shape[0])

    @property
    def paired(self) -> bool:
        return self.effective_pool.shape[1] == 2

    def check_budget(self, budget: int) -> None:
        _check_budget(self.pool_size, budget, False)

    def describe(self) -> dict:
        return {"residual_pool_kind": "per-instance", "residual_pool_size": self.pool_size,
                "residual_pool_paired": self.paired, "residual_pooled_instances": 1,
                "residual_draw": "volatility", "residual_draw_k": int(self.k), "residual_draw_eps": float(self.eps),
                "residual_draw_no_spread": self.no_spread}

    def __call__(self, oracle_margin, rng, volatility=None):
        m = _margins(oracle_margin)
        if self.no_spread:
            return _draw_residual(m, self.effective_pool, rng)
        if volatility is None:
            raise ValueError("the volatility draw needs each candidate's standard deviation (volatility=)")
        v = np.asarray(volatility, dtype=np.float64).reshape(-1)
        if v.size != m.size:
            raise ValueError(f"{v.size} standard deviations for {m.size} candidates")
        nb = volatility_neighbours(self.pool_sd, v, self.k, self.eps)
        rows = nb[np.arange(m.size), rng.integers(0, int(self.k), size=m.size)]
        pool = self.effective_pool
        r = pool[rows]
        score = m + r[:, 0]
        accept = (m + r[:, 1] >= 0) if pool.shape[1] == 2 else (score >= 0)
        return SurrogateDraw(score, accept, r[:, 1].copy() if pool.shape[1] == 2 else None)


def _rank_counts(pool_values: np.ndarray, x: np.ndarray) -> np.ndarray:
    """For each x, the number of pool values strictly below it (int64)."""
    return np.searchsorted(np.sort(pool_values), x, side="left").astype(np.int64)


def calibrated_neighbours(pool_m, pool_s, cand_m, cand_s, k: int, exclude: Sequence | None = None) -> np.ndarray:
    """(n_cand, k) row indices: for each candidate the ``k`` pool rows nearest to it in the plane of the pool's own
    ranks (u_m, u_s), Euclidean distance, ties by pool order (the lower row index first).

    u_m(x) = the share of pool rows whose m_j lies below x (strictly), u_s(x) likewise with s_j; a pool row's own
    coordinates are (u_m(m_j), u_s(s_j)), a candidate's (u_m(m(y)), u_s(s(y))). Distances are computed on the counts
    (n u), in integers, so that equal distances are exactly equal and fall to pool order. ``exclude`` (optional): per
    candidate the pool rows left out of its neighbours (the rows holding the candidate itself); at least ``k`` rows
    must remain."""
    pm = np.asarray(pool_m, dtype=np.float64).reshape(-1)
    ps = np.asarray(pool_s, dtype=np.float64).reshape(-1)
    cm = np.asarray(cand_m, dtype=np.float64).reshape(-1)
    cs = np.asarray(cand_s, dtype=np.float64).reshape(-1)
    if pm.size != ps.size or cm.size != cs.size:
        raise ValueError("pool_m and pool_s (and cand_m and cand_s) must have the same length")
    if not (np.isfinite(pm).all() and np.isfinite(ps).all() and np.isfinite(cm).all() and np.isfinite(cs).all()):
        raise ValueError("margins and standard deviations must be finite")
    if (ps < 0).any() or (cs < 0).any():
        raise ValueError("standard deviations must be non-negative")
    n, k = pm.size, int(k)
    if not 1 <= k <= n:
        raise ValueError(f"k = {k} must lie in 1..{n} (the pool's rows)")
    pu, ps_ = _rank_counts(pm, pm), _rank_counts(ps, ps)
    cu, cs_ = _rank_counts(pm, cm), _rank_counts(ps, cs)
    d2 = (pu[None, :] - cu[:, None]) ** 2 + (ps_[None, :] - cs_[:, None]) ** 2
    if exclude is not None:
        if len(exclude) != cm.size:
            raise ValueError(f"exclude has {len(exclude)} entries for {cm.size} candidates")
        far = np.int64(2 * n * n + 1)                     # beyond every real distance (counts lie in 0..n)
        for i, rows in enumerate(exclude):
            rows = np.unique(np.asarray(rows, dtype=np.int64).reshape(-1))
            if rows.size:
                if rows.min() < 0 or rows.max() >= n:
                    raise ValueError("excluded rows must be pool row indices")
                if n - rows.size < k:
                    raise ValueError(f"candidate {i}: {n - rows.size} pool rows remain after the exclusion, fewer than k = {k}")
                d2[i, rows] = far
    return np.argsort(d2, axis=1, kind="stable")[:, :k]


@dataclass(eq=False)
class CalibratedResidualSurrogate:
    """Residual surrogate whose draw is matched on the candidate's true quality and volatility.

    ``pool``: the instance's paired (or single-column) residual pool, as for :class:`ResidualSurrogate`; ``pool_m``,
    ``pool_s``: per pool row, the mean and the standard deviation of that plan's oracle margin across the truth seeds.
    For a candidate with mean m (the oracle margins the surrogate is called with) and standard deviation s (passed as
    ``volatility``), the residual row is drawn uniformly from the ``k`` pool rows nearest to it in the plane of the
    pool's own ranks (:func:`calibrated_neighbours`), leaving out the rows that hold the candidate itself (passed as
    ``pool_rows``: per candidate a sequence of row indices, empty when the candidate is not a pool plan; a
    :class:`SurrogateGrader` built with ``pool_rows=`` does that). The random numbers are the volatility draw's (one
    ``rng.integers(0, k)`` per candidate). Everything else (pairing, accept rule) is the plain surrogate's. There is no
    fallback for a pool without spread: the ranks of a constant column are all 0 and the draw is then by the other
    coordinate."""

    pool: np.ndarray
    pool_m: np.ndarray
    pool_s: np.ndarray
    k: int
    kind = "residual"
    effective_pool: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
        self.effective_pool = _as_pool(self.pool)
        self.pool_m = np.asarray(self.pool_m, dtype=np.float64).reshape(-1)
        self.pool_s = np.asarray(self.pool_s, dtype=np.float64).reshape(-1)
        n = self.effective_pool.shape[0]
        if self.pool_m.size != n or self.pool_s.size != n:
            raise ValueError(f"pool_m and pool_s have {self.pool_m.size} and {self.pool_s.size} rows, the pool {n}")
        calibrated_neighbours(self.pool_m, self.pool_s, self.pool_m[:1], self.pool_s[:1], self.k)    # argument checks

    pooled = False

    @property
    def pool_size(self) -> int:
        return int(self.effective_pool.shape[0])

    @property
    def paired(self) -> bool:
        return self.effective_pool.shape[1] == 2

    def check_budget(self, budget: int) -> None:
        _check_budget(self.pool_size, budget, False)

    def describe(self) -> dict:
        return {"residual_pool_kind": "per-instance", "residual_pool_size": self.pool_size,
                "residual_pool_paired": self.paired, "residual_pooled_instances": 1,
                "residual_draw": "calibrated", "residual_draw_k": int(self.k),
                "residual_draw_space": "pool ranks of (mean, sd) of the oracle margin over the truth seeds; Euclidean"}

    def __call__(self, oracle_margin, rng, volatility=None, pool_rows=None):
        m = _margins(oracle_margin)
        if volatility is None:
            raise ValueError("the calibrated draw needs each candidate's standard deviation (volatility=)")
        if pool_rows is None:
            raise ValueError("the calibrated draw needs each candidate's own pool rows (pool_rows=; empty if none)")
        v = np.asarray(volatility, dtype=np.float64).reshape(-1)
        if v.size != m.size or len(pool_rows) != m.size:
            raise ValueError(f"{v.size} standard deviations and {len(pool_rows)} pool-row lists for {m.size} candidates")
        nb = calibrated_neighbours(self.pool_m, self.pool_s, m, v, self.k, exclude=pool_rows)
        rows = nb[np.arange(m.size), rng.integers(0, int(self.k), size=m.size)]
        pool = self.effective_pool
        r = pool[rows]
        score = m + r[:, 0]
        accept = (m + r[:, 1] >= 0) if pool.shape[1] == 2 else (score >= 0)
        return SurrogateDraw(score, accept, r[:, 1].copy() if pool.shape[1] == 2 else None)


@dataclass(frozen=True)
class FlipSurrogate:
    fp: float
    fn: float
    kind = "flip"

    def __call__(self, oracle_margin, rng):
        return flip_surrogate(oracle_margin, self.fp, self.fn, rng)


@dataclass(eq=False)
class ResidualSurrogate:
    """Residual surrogate for one instance. ``pool``: the instance's own pool ((n,) or paired
    (n, 2)); ``family_pools``: the task family's pools for the pooled option (None: per-instance)."""

    pool: np.ndarray
    family_pools: Sequence | None = None
    kind = "residual"
    effective_pool: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
        if self.family_pools is None:
            self.effective_pool = _as_pool(self.pool)
        else:
            self.effective_pool = pool_family_residuals(self.pool, self.family_pools)

    @property
    def pooled(self) -> bool:
        return self.family_pools is not None

    @property
    def pool_size(self) -> int:
        return int(self.effective_pool.shape[0])

    @property
    def paired(self) -> bool:
        return self.effective_pool.shape[1] == 2

    def check_budget(self, budget: int) -> None:
        _check_budget(self.pool_size, budget, self.pooled)

    def describe(self) -> dict:
        out = {"residual_pool_kind": "pooled" if self.pooled else "per-instance",
               "residual_pool_size": self.pool_size, "residual_pool_paired": self.paired,
               "residual_pooled_instances": len(self.family_pools) if self.pooled else 1}
        if isinstance(self.family_pools, ResidualFamily) and self.family_pools.zero_mad == "centre":
            out["residual_zero_mad_instances"] = [int(x) for x in self.family_pools.n_zero_mad]
            out["residual_target_zero_mad"] = [bool(x) for x in (_med_mad(_as_pool(self.pool))[1] == 0)]
        return out

    def __call__(self, oracle_margin, rng):
        return _draw_residual(_margins(oracle_margin), self.effective_pool, rng)


# --------------------------------------------------------------------------------------------
# oracle cache and surrogate grader


class OracleCache:
    """``oracle_margin`` evaluated once per distinct plan, shared by every grader that holds it.

    Counts: ``n_requests`` (rows asked for), ``n_evals`` (rows sent to the oracle), ``n_calls``."""

    def __init__(self, oracle_margin: Callable):
        if not callable(oracle_margin):
            raise TypeError("oracle_margin must be callable")
        self.oracle_margin = oracle_margin
        self._memo: dict[bytes, float] = {}
        self.n_requests = 0
        self.n_evals = 0
        self.n_calls = 0

    def __call__(self, plans) -> np.ndarray:
        X = np.ascontiguousarray(plans, dtype=np.int64)
        keys = [r.tobytes() for r in X]
        new: dict[bytes, int] = {}
        for i, k in enumerate(keys):
            if k not in self._memo and k not in new:
                new[k] = i
        if new:
            rows = np.fromiter(new.values(), dtype=np.int64, count=len(new))
            m = _margins(self.oracle_margin(X[rows]))
            if m.size != rows.size:
                raise ValueError(f"oracle_margin returned {m.size} margins for {rows.size} plans")
            for j, k in enumerate(new):
                self._memo[k] = float(m[j])
            self.n_evals += rows.size
            self.n_calls += 1
        self.n_requests += len(keys)
        return np.array([self._memo[k] for k in keys], dtype=np.float64)


class SurrogateGrader:
    """A surrogate as an attacker's ``score`` function, with the oracle evaluated per candidate.

    ``surrogate(oracle_margins, rng) -> SurrogateDraw``; ``oracle_margin(plans) -> margins`` (an
    :class:`OracleCache` to share evaluations). ``judge_margin`` (optional): the oracle function that
    judges the selected plan in :func:`attack_surrogate` when it differs from the one the surrogate is
    built on (e.g. the surrogate on a mean over oracle seeds, the verdict on the primary seed); the
    default judges with ``oracle_margin``. ``accept_margin`` (optional; paired residual surrogates only):
    the surrogate's accept decision on the selected plan is remade in :func:`attack_surrogate` as
    ``accept_margin(plan) + the verdict residual drawn for that plan >= 0``, so that the estimate of the
    plan's true margin used to accept is not the one search selected on (``oracle_margin`` then only
    makes the scores). ``volatility`` (optional): plans -> each plan's standard deviation of the oracle margin
    across seeds, called after ``oracle_margin`` on the same rows and handed to the surrogate as
    ``volatility=`` (:class:`VolatilityResidualSurrogate`). ``pool_rows`` (optional): plans -> for each plan the
    rows of the surrogate's pool that hold that same plan (empty for a plan outside the pool), called after
    ``volatility`` on the same rows and handed to the surrogate as ``pool_rows=`` (:class:`CalibratedResidualSurrogate`
    leaves them out of the draw). Counts: ``n_scored`` (rows handed to it),
    ``n_oracle_evals`` (rows it sent to ``oracle_margin``). A surrogate with a ``pool_size`` (the
    residual surrogate) refuses an attack that scores more rows than the pool holds.
    """

    def __init__(self, surrogate: Callable, oracle_margin: Callable, rng: np.random.Generator, memo: bool = True,
                 judge_margin: Callable | None = None, accept_margin: Callable | None = None,
                 volatility: Callable | None = None, pool_rows: Callable | None = None):
        if not callable(surrogate) or not callable(oracle_margin):
            raise TypeError("surrogate and oracle_margin must be callable")
        if judge_margin is not None and not callable(judge_margin):
            raise TypeError("judge_margin must be callable")
        if accept_margin is not None and not callable(accept_margin):
            raise TypeError("accept_margin must be callable")
        if volatility is not None and not callable(volatility):
            raise TypeError("volatility must be callable")
        if pool_rows is not None and not callable(pool_rows):
            raise TypeError("pool_rows must be callable")
        if pool_rows is not None and volatility is None:
            raise ValueError("pool_rows is handed to a surrogate that also takes volatility=")
        self.surrogate = surrogate
        self.oracle_margin = oracle_margin
        self.judge_margin = judge_margin
        self.accept_margin = accept_margin
        self.volatility = volatility
        self.pool_rows = pool_rows
        self.rng = rng
        self.memo = bool(memo)
        self._memo: dict[bytes, tuple[float, bool, float]] = {}
        self._vres: dict[bytes, float] = {}
        self._hist: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []
        self._hist_vres: list[np.ndarray | None] = []
        self._last_vres: np.ndarray | None = None
        self.n_scored = 0
        self.n_oracle_evals = 0
        self._attack_start = 0

    def begin_attack(self) -> None:
        self._attack_start = self.n_scored

    def _evaluate(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        m = _margins(self.oracle_margin(X))
        if m.size != X.shape[0]:
            raise ValueError(f"oracle_margin returned {m.size} margins for {X.shape[0]} plans")
        self.n_oracle_evals += X.shape[0]
        if self.volatility is None:
            d = self.surrogate(m, self.rng)
        else:
            v = np.asarray(self.volatility(X), dtype=np.float64).reshape(-1)
            if v.size != X.shape[0]:
                raise ValueError(f"volatility returned {v.size} values for {X.shape[0]} plans")
            if self.pool_rows is None:
                d = self.surrogate(m, self.rng, volatility=v)
            else:
                own = list(self.pool_rows(X))
                if len(own) != X.shape[0]:
                    raise ValueError(f"pool_rows returned {len(own)} entries for {X.shape[0]} plans")
                d = self.surrogate(m, self.rng, volatility=v, pool_rows=own)
        s = np.asarray(d.score, dtype=np.float64).reshape(-1)
        a = np.asarray(d.accept, dtype=bool).reshape(-1)
        if s.size != m.size or a.size != m.size:
            raise ValueError("surrogate returned the wrong number of draws")
        vr = getattr(d, "verdict_residual", None)
        self._last_vres = None if vr is None else np.asarray(vr, dtype=np.float64).reshape(-1)
        return s, a, m

    def __call__(self, plans) -> np.ndarray:
        X = np.ascontiguousarray(plans, dtype=np.int64)
        if X.ndim != 2:
            raise ValueError("plans must be 2-D")
        n = X.shape[0]
        cap = getattr(self.surrogate, "pool_size", None)
        if cap is not None and self.n_scored - self._attack_start + n > cap:
            raise PoolTooSmall(f"residual pool has {cap} rows; this attack would score "
                               f"{self.n_scored - self._attack_start + n} plans")
        if not self.memo:
            s, a, m = self._evaluate(X)
            self._hist.append((s, a, m))
            self._hist_vres.append(self._last_vres)
            self.n_scored += n
            return s.copy()
        keys = [r.tobytes() for r in X]
        new: dict[bytes, int] = {}
        for i, k in enumerate(keys):
            if k not in self._memo and k not in new:
                new[k] = i
        if new:
            rows = np.fromiter(new.values(), dtype=np.int64, count=len(new))
            s, a, m = self._evaluate(X[rows])
            for j, k in enumerate(new):
                self._memo[k] = (float(s[j]), bool(a[j]), float(m[j]))
                if self._last_vres is not None:
                    self._vres[k] = float(self._last_vres[j])
        self.n_scored += n
        return np.array([self._memo[k][0] for k in keys], dtype=np.float64)

    def lookup(self, plan, position: int | None = None) -> tuple[float, bool, float]:
        """(surrogate score, surrogate accept, oracle margin) of a scored plan.

        With ``memo=False`` the draw is identified by its ``position`` among all rows this grader
        has scored (0-based)."""
        if self.memo:
            key = np.ascontiguousarray(plan, dtype=np.int64).reshape(-1).tobytes()
            if key not in self._memo:
                raise KeyError("plan was never scored by this grader")
            return self._memo[key]
        if position is None:
            raise ValueError("memo=False needs the plan's scoring position")
        p = int(position)
        for s, a, m in self._hist:
            if p < s.size:
                return float(s[p]), bool(a[p]), float(m[p])
            p -= s.size
        raise IndexError("position beyond the rows scored")

    def verdict_residual(self, plan, position: int | None = None) -> float | None:
        """The verdict residual drawn for a scored plan (paired residual surrogates; None otherwise)."""
        if self.memo:
            key = np.ascontiguousarray(plan, dtype=np.int64).reshape(-1).tobytes()
            if key not in self._memo:
                raise KeyError("plan was never scored by this grader")
            return self._vres.get(key)
        p = int(position)
        for (s, _, _), vr in zip(self._hist, self._hist_vres):
            if p < s.size:
                return None if vr is None else float(vr[p])
            p -= s.size
        raise IndexError("position beyond the rows scored")


@dataclass(frozen=True)
class SurrogateResult:
    plan: np.ndarray
    surrogate_accept: bool
    oracle_accept: bool  # oracle margin >= 0
    surrogate_score: float
    oracle_margin: float
    log: dict

    @property
    def hacked(self) -> bool:
        return bool(self.surrogate_accept and not self.oracle_accept)


def attack_surrogate(attack: Callable[[Callable], Selected], surrogate, oracle_margin: Callable | None = None,
                     rng: np.random.Generator | None = None, *, memo: bool = True,
                     budget: int | None = None) -> SurrogateResult:
    """Run ``attack(score) -> Selected`` against a surrogate grader; return the selected plan's
    surrogate verdict and oracle verdict (by the grader's ``judge_margin`` when it has one; the
    margin the surrogate was built on is then ``log["score_basis_margin"]``).

    ``attack`` binds an attacker from :mod:`hpr_dream.attack` to its arguments, e.g.
    ``lambda score: random_shooting(score, proposals, B)``. ``surrogate`` is either a
    :class:`SurrogateGrader` (shared, e.g. across budgets of one instance; then ``oracle_margin``
    and ``rng`` are not given) or a surrogate callable such as :class:`FlipSurrogate`, from which
    a fresh grader is built with ``oracle_margin`` and ``rng``. ``budget``, if given, is checked
    against a residual pool before the attack starts (it is always checked while the attack runs)
    and against the attacker's log afterwards. The log is the attacker's log plus the surrogate
    grader's counts for this attack and, for the residual surrogate, the pool kind and size.
    """
    if isinstance(surrogate, SurrogateGrader):
        if oracle_margin is not None or rng is not None:
            raise ValueError("a SurrogateGrader already carries its oracle and rng")
        grader = surrogate
    else:
        if oracle_margin is None or rng is None:
            raise ValueError("oracle_margin and rng are required to build a surrogate grader")
        grader = SurrogateGrader(surrogate, oracle_margin, rng, memo=memo)
    if budget is not None and hasattr(grader.surrogate, "check_budget"):
        grader.surrogate.check_budget(budget)
    cache = grader.oracle_margin if isinstance(grader.oracle_margin, OracleCache) else None
    start_scored, start_oracle = grader.n_scored, grader.n_oracle_evals
    start_cache = cache.n_evals if cache is not None else 0
    grader.begin_attack()
    plan, log = attack(grader)
    used = grader.n_scored - start_scored
    if used != log["n_scored"] or used != log["budget"] or (budget is not None and used != int(budget)):
        raise BudgetError(f"surrogate grader scored {used} plans; attacker logged {log['n_scored']}, "
                          f"budget {log['budget']}" + ("" if budget is None else f", declared {budget}"))
    s, a, m = grader.lookup(plan, start_scored + log["best_index"])
    out_log = dict(log)
    if grader.accept_margin is not None:
        vr = grader.verdict_residual(plan, start_scored + log["best_index"])
        if vr is None:
            raise ValueError("accept_margin needs a paired residual surrogate")
        ma = float(_margins(grader.accept_margin(np.asarray(plan)[None]))[0])
        out_log.update(search_basis_margin=float(m), accept_basis_margin=ma, accept_at_search=bool(a),
                       verdict_residual_drawn=vr)
        a = bool(ma + vr >= 0)
    if grader.judge_margin is not None:
        out_log["score_basis_margin"] = float(m)
        m = float(_margins(grader.judge_margin(np.asarray(plan)[None]))[0])
    out_log.update(surrogate=getattr(grader.surrogate, "kind", type(grader.surrogate).__name__),
                   surrogate_n_scored=used, n_oracle_requests=grader.n_oracle_evals - start_oracle,
                   n_oracle_evals=(cache.n_evals - start_cache) if cache is not None else grader.n_oracle_evals - start_oracle,
                   oracle_cache_shared=cache is not None, memo=grader.memo)
    if hasattr(grader.surrogate, "describe"):
        out_log.update(grader.surrogate.describe())
    return SurrogateResult(np.asarray(plan).copy(), bool(a), bool(m >= 0), float(s), float(m), out_log)
