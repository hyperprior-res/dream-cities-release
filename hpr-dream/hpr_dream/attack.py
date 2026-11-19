"""Attackers with exact budget accounting.

Every attacker takes ``score(plans) -> scores``: ``plans`` is an integer array of shape (n, D),
the return value a float array of shape (n,), higher is better. Each attacker returns the single
selected plan and a log (a :class:`Selected`), and scores exactly ``B`` plans: a counter inside the
scoring wrapper counts every plan handed to ``score`` and the attacker raises :class:`BudgetError`
if the count differs from ``B``. The log records the counted number (``n_scored``), never the
nominal budget alone.

``score`` is handed large batches: random shooting and best-of-n score all ``B`` plans in one call,
CEM scores one whole population per call. ``batch_size`` splits a call into chunks of at most that
many plans (for graders with a memory limit); chunks are counted like any other call.
"""

from __future__ import annotations

import math
from typing import Callable, NamedTuple, Sequence

import numpy as np

__all__ = [
    "BudgetError",
    "CEM_SCHEDULE",
    "Marginals",
    "Selected",
    "Space",
    "best_of_n",
    "cem",
    "cem_schedule",
    "cem_seeded",
    "fit_marginals",
    "random_shooting",
]

ScoreFn = Callable[[np.ndarray], np.ndarray]

#: CEM budget -> (generations, population), generations x population == budget.
#: B = 1 is one draw from the initial distribution.
CEM_SCHEDULE: dict[int, tuple[int, int]] = {
    1: (1, 1),
    10: (2, 5),
    100: (4, 25),
    1000: (5, 200),
    10000: (10, 1000),
}


class BudgetError(RuntimeError):
    """An attacker handed ``score`` a number of plans different from its budget."""


class Selected(NamedTuple):
    """An attacker's result: the selected plan (1-D int array) and its log (dict)."""

    plan: np.ndarray
    log: dict


def _check_budget(B) -> int:
    if isinstance(B, (bool, np.bool_)) or int(B) != B or int(B) < 1:
        raise ValueError(f"budget must be a positive integer, got {B!r}")
    return int(B)


class _Counter:
    """Wraps ``score``: validates its output and counts every plan and call."""

    __slots__ = ("fn", "batch_size", "n_plans", "n_calls", "max_batch")

    def __init__(self, fn: ScoreFn, batch_size: int | None):
        if not callable(fn):
            raise TypeError("score must be callable")
        if batch_size is not None and int(batch_size) < 1:
            raise ValueError("batch_size must be >= 1")
        self.fn = fn
        self.batch_size = None if batch_size is None else int(batch_size)
        self.n_plans = 0
        self.n_calls = 0
        self.max_batch = 0

    def __call__(self, plans: np.ndarray) -> np.ndarray:
        n = plans.shape[0]
        bs = self.batch_size
        if bs is None or n <= bs:
            return self._one(plans)
        return np.concatenate([self._one(plans[i : i + bs]) for i in range(0, n, bs)])

    def _one(self, plans: np.ndarray) -> np.ndarray:
        view = plans.view()
        view.flags.writeable = False  # score must not mutate the attacker's plans
        n = plans.shape[0]
        s = np.array(self.fn(view), dtype=np.float64, copy=True)
        if s.shape != (n,):
            raise ValueError(f"score returned shape {s.shape} for {n} plans; expected ({n},)")
        if np.isnan(s).any():
            raise ValueError("score returned NaN")
        self.n_plans += n
        self.n_calls += 1
        if n > self.max_batch:
            self.max_batch = n
        return s

    def check(self, name: str, B: int) -> None:
        if self.n_plans != B:
            raise BudgetError(f"{name}: scored {self.n_plans} plans, budget {B}")

    def log(self) -> dict:
        return {"n_scored": self.n_plans, "n_score_calls": self.n_calls, "max_batch": self.max_batch}


# --------------------------------------------------------------------------------------------
# Search space


class _Layout(NamedTuple):
    cat_cols: np.ndarray  # free categorical columns
    cat_n: np.ndarray  # number of values per free categorical column
    cat_start: np.ndarray  # offset of each column in the flat probability vector
    cat_seg: np.ndarray  # flat index -> local categorical column
    cdf_start: np.ndarray  # offset of each column's boundaries in the flat cdf
    int_cols: np.ndarray  # free integer columns
    int_low: np.ndarray
    int_high: np.ndarray


class Space:
    """Per-column search space for integer plans of length D.

    A column is either categorical with ``n`` values (0..n-1) or integer in ``[low, high]``
    (inclusive). ``frozen`` marks columns held at ``frozen_values``; samplers and :meth:`clip`
    write the fixed value into them and CEM never searches them.
    """

    def __init__(self, low, high, categorical, frozen=None, frozen_values=None):
        low = np.array(low, dtype=np.int64).reshape(-1)
        high = np.array(high, dtype=np.int64).reshape(-1)
        cat = np.array(categorical, dtype=bool).reshape(-1)
        D = low.size
        if high.size != D or cat.size != D:
            raise ValueError("low, high and categorical must have the same length")
        if D == 0:
            raise ValueError("a space needs at least one column")
        if (high < low).any():
            raise ValueError("high < low in some column")
        if (cat & (low != 0)).any():
            raise ValueError("categorical columns take the values 0..n-1 (low must be 0)")
        fr = np.zeros(D, bool) if frozen is None else np.array(frozen, dtype=bool).reshape(-1)
        fv = np.zeros(D, np.int64) if frozen_values is None else np.array(frozen_values, dtype=np.int64).reshape(-1)
        if fr.size != D or fv.size != D:
            raise ValueError("frozen and frozen_values must have length D")
        if (fr & ((fv < low) | (fv > high))).any():
            raise ValueError("a frozen value lies outside its column's range")
        fv = np.where(fr, fv, 0)
        for a in (low, high, cat, fr, fv):
            a.flags.writeable = False
        self.low, self.high, self.categorical, self.frozen, self.frozen_values = low, high, cat, fr, fv
        self._layout_cache: _Layout | None = None

    # constructors -----------------------------------------------------------------------
    @classmethod
    def categorical_columns(cls, n_values: Sequence[int]) -> "Space":
        n = np.array(n_values, dtype=np.int64).reshape(-1)
        if (n < 1).any():
            raise ValueError("a categorical column needs at least one value")
        return cls(np.zeros_like(n), n - 1, np.ones(n.size, bool))

    @classmethod
    def integer_columns(cls, low: Sequence[int], high: Sequence[int]) -> "Space":
        low = np.array(low, dtype=np.int64).reshape(-1)
        return cls(low, high, np.zeros(low.size, bool))

    @staticmethod
    def concat(*spaces: "Space") -> "Space":
        return Space(
            np.concatenate([s.low for s in spaces]),
            np.concatenate([s.high for s in spaces]),
            np.concatenate([s.categorical for s in spaces]),
            np.concatenate([s.frozen for s in spaces]),
            np.concatenate([s.frozen_values for s in spaces]),
        )

    def freeze(self, columns, values) -> "Space":
        """A copy with ``columns`` (indices or a boolean mask) frozen at ``values``."""
        cols = np.arange(self.D)[np.asarray(columns)] if np.asarray(columns).dtype == bool else np.asarray(columns, np.int64).reshape(-1)
        fr = self.frozen.copy()
        fv = self.frozen_values.copy()
        fr[cols] = True
        fv[cols] = np.broadcast_to(np.asarray(values, np.int64), cols.shape)
        return Space(self.low, self.high, self.categorical, fr, fv)

    # properties -------------------------------------------------------------------------
    @property
    def D(self) -> int:
        return int(self.low.size)

    @property
    def n_values(self) -> np.ndarray:
        """Number of admissible values per column (high - low + 1)."""
        return self.high - self.low + 1

    @property
    def _layout(self) -> _Layout:
        if self._layout_cache is None:
            free = ~self.frozen
            cat_cols = np.flatnonzero(self.categorical & free)
            cat_n = (self.high[cat_cols] + 1).astype(np.int64)
            cat_start = np.concatenate([[0], np.cumsum(cat_n)[:-1]]).astype(np.int64)
            cat_seg = np.repeat(np.arange(cat_cols.size), cat_n)
            cdf_start = np.concatenate([[0], np.cumsum(cat_n - 1)[:-1]]).astype(np.int64)
            int_cols = np.flatnonzero(~self.categorical & free)
            self._layout_cache = _Layout(
                cat_cols, cat_n, cat_start, cat_seg, cdf_start, int_cols,
                self.low[int_cols].astype(np.int64), self.high[int_cols].astype(np.int64),
            )
        return self._layout_cache

    # operations -------------------------------------------------------------------------
    def sample_uniform(self, rng: np.random.Generator, n: int) -> np.ndarray:
        """``n`` plans, every free column uniform over its admissible values."""
        X = rng.integers(self.low, self.high + 1, size=(int(n), self.D), dtype=np.int64)
        if self.frozen.any():
            X[:, self.frozen] = self.frozen_values[self.frozen]
        return X

    def clip(self, plans) -> np.ndarray:
        """Clip into range and write frozen values (int64 copy)."""
        X = np.clip(np.asarray(plans, dtype=np.int64), self.low, self.high)
        if self.frozen.any():
            X[..., self.frozen] = self.frozen_values[self.frozen]
        return X

    def contains(self, plans) -> np.ndarray:
        """Whether each plan lies in the space (in range and frozen columns at their values)."""
        X = np.asarray(plans)
        ok = ((X >= self.low) & (X <= self.high)).all(axis=-1)
        if self.frozen.any():
            ok &= (X[..., self.frozen] == self.frozen_values[self.frozen]).all(axis=-1)
        return ok

    def __repr__(self) -> str:
        return (
            f"Space(D={self.D}, categorical={int(self.categorical.sum())}, "
            f"integer={int((~self.categorical).sum())}, frozen={int(self.frozen.sum())})"
        )


# --------------------------------------------------------------------------------------------
# CEM distribution


def _uniform_sd(low: np.ndarray, high: np.ndarray) -> np.ndarray:
    k = (high - low + 1).astype(np.float64)
    return np.sqrt((k * k - 1.0) / 12.0)


class Marginals:
    """Independent per-column distribution over a :class:`Space`.

    Categorical columns: a probability vector. Integer columns: a Gaussian (mean, standard
    deviation) sampled as ``clip(rint(mean + sd * z), low, high)``. An integer column may also be
    flagged *uniform* (exactly uniform over ``[low, high]``), which is how CEM's uniform
    initialisation is represented; its mean and standard deviation are then the uniform's, and
    the flag clears at the first CEM update.
    """

    def __init__(self, space: Space, p: np.ndarray, mu: np.ndarray, sigma: np.ndarray, uniform: np.ndarray):
        L = space._layout
        self.space = space
        self.p = np.array(p, dtype=np.float64)
        self.mu = np.array(mu, dtype=np.float64)
        self.sigma = np.array(sigma, dtype=np.float64)
        self.uniform = np.array(uniform, dtype=bool)
        if self.p.shape != (int(L.cat_n.sum()),):
            raise ValueError("probability vector does not match the space")
        if self.mu.shape != (L.int_cols.size,) or self.sigma.shape != self.mu.shape or self.uniform.shape != self.mu.shape:
            raise ValueError("integer-column parameters do not match the space")
        self._cdf: np.ndarray | None = None

    @classmethod
    def uniform_over(cls, space: Space) -> "Marginals":
        L = space._layout
        p = 1.0 / L.cat_n[L.cat_seg] if L.cat_seg.size else np.zeros(0)
        mu = (L.int_low + L.int_high) / 2.0
        return cls(space, p, mu, _uniform_sd(L.int_low, L.int_high), np.ones(L.int_cols.size, bool))

    @classmethod
    def fit(cls, space: Space, plans) -> "Marginals":
        """Frequencies (categorical) and mean / population sd (integer) of ``plans``; no floors."""
        p, mu, sd = _fit_raw(space, plans)
        return cls(space, p, mu, sd, np.zeros(mu.size, bool))

    def copy(self) -> "Marginals":
        return Marginals(self.space, self.p, self.mu, self.sigma, self.uniform)

    # accessors --------------------------------------------------------------------------
    def probs(self, column: int) -> np.ndarray:
        L = self.space._layout
        j = int(np.flatnonzero(L.cat_cols == column)[0])
        return self.p[L.cat_start[j] : L.cat_start[j] + L.cat_n[j]].copy()

    def gaussian(self, column: int) -> tuple[float, float]:
        L = self.space._layout
        j = int(np.flatnonzero(L.int_cols == column)[0])
        return float(self.mu[j]), float(self.sigma[j])

    # floors -----------------------------------------------------------------------------
    def apply_floors(self, prob_floor: float, std_floor: float, std_floor_frac: float) -> "Marginals":
        """Floor every probability and every standard deviation (in place; returns self).

        Categorical column with n values: floor f = min(prob_floor, 0.5 / n). The floored vector
        is f + (1 - n f) (max(p, f) - f) / sum(max(p, f) - f): every entry is at least f, the
        vector sums to one, and a vector already above the floor is unchanged.
        Integer column: sd >= max(std_floor, std_floor_frac * (high - low)).
        """
        L = self.space._layout
        if L.cat_cols.size:
            f_col = np.minimum(float(prob_floor), 0.5 / L.cat_n)
            f = f_col[L.cat_seg]
            ex = np.maximum(self.p, f) - f
            seg_sum = np.add.reduceat(ex, L.cat_start)
            self.p = f + ((1.0 - L.cat_n * f_col) / seg_sum)[L.cat_seg] * ex
            self._cdf = None
        if L.int_cols.size:
            sf = np.maximum(float(std_floor), float(std_floor_frac) * (L.int_high - L.int_low))
            self.sigma = np.maximum(self.sigma, sf)
        return self

    # sampling ---------------------------------------------------------------------------
    def _flat_cdf(self) -> np.ndarray:
        """Inner boundaries of every column's cdf, column j shifted by 2j, as one sorted array."""
        if self._cdf is None:
            L = self.space._layout
            cs = np.cumsum(self.p)
            before = np.concatenate([[0.0], cs[L.cat_start[1:] - 1]]) if L.cat_cols.size > 1 else np.zeros(L.cat_cols.size)
            within = cs - before[L.cat_seg]
            keep = np.ones(self.p.size, bool)
            keep[L.cat_start + L.cat_n - 1] = False  # drop each column's last boundary (= 1)
            self._cdf = (within + 2.0 * L.cat_seg)[keep]
        return self._cdf

    def sample(self, rng: np.random.Generator, n: int) -> np.ndarray:
        sp = self.space
        L = sp._layout
        n = int(n)
        X = np.empty((n, sp.D), dtype=np.int64)
        if sp.frozen.any():
            X[:, sp.frozen] = sp.frozen_values[sp.frozen]
        dc = L.cat_cols.size
        if dc:
            u = rng.random((n, dc))
            q = u + 2.0 * np.arange(dc)
            pos = np.searchsorted(self._flat_cdf(), q.ravel(), side="right").reshape(n, dc)
            X[:, L.cat_cols] = pos - L.cdf_start
        di = L.int_cols.size
        if di:
            if self.uniform.all():
                X[:, L.int_cols] = rng.integers(L.int_low, L.int_high + 1, size=(n, di), dtype=np.int64)
            else:
                z = rng.standard_normal((n, di))
                v = np.clip(np.rint(self.mu + self.sigma * z), L.int_low, L.int_high).astype(np.int64)
                if self.uniform.any():
                    w = rng.integers(L.int_low, L.int_high + 1, size=(n, di), dtype=np.int64)
                    v = np.where(self.uniform, w, v)
                X[:, L.int_cols] = v
        return X

    # update -----------------------------------------------------------------------------
    def smooth_towards(self, plans: np.ndarray, smoothing: float) -> "Marginals":
        """In place: parameters <- smoothing * fit(plans) + (1 - smoothing) * parameters."""
        p, mu, sd = _fit_raw(self.space, plans)
        a = float(smoothing)
        self.p = a * p + (1.0 - a) * self.p
        self.mu = a * mu + (1.0 - a) * self.mu
        self.sigma = a * sd + (1.0 - a) * self.sigma
        self.uniform = np.zeros_like(self.uniform)
        self._cdf = None
        return self


def _fit_raw(space: Space, plans) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    X = np.asarray(plans)
    if X.ndim != 2 or X.shape[1] != space.D or X.shape[0] < 1:
        raise ValueError(f"expected plans of shape (n >= 1, {space.D}), got {X.shape}")
    L = space._layout
    n = X.shape[0]
    if L.cat_cols.size:
        v = X[:, L.cat_cols].astype(np.int64)
        if ((v < 0) | (v >= L.cat_n)).any():
            raise ValueError("plan value outside a categorical column's range")
        p = np.bincount((v + L.cat_start).ravel(), minlength=int(L.cat_n.sum())) / n
    else:
        p = np.zeros(0)
    if L.int_cols.size:
        w = X[:, L.int_cols].astype(np.float64)
        mu, sd = w.mean(axis=0), w.std(axis=0)
    else:
        mu = sd = np.zeros(0)
    return p.astype(np.float64), mu, sd


def fit_marginals(space: Space, behaviour_plans, *, prob_floor: float = 0.01, std_floor: float = 0.5,
                  std_floor_frac: float = 0.02) -> Marginals:
    """Per-column marginals fitted to behaviour plans (CEM's ``init``), with CEM's default floors."""
    return Marginals.fit(space, behaviour_plans).apply_floors(prob_floor, std_floor, std_floor_frac)


# --------------------------------------------------------------------------------------------
# Attackers


def _first_b(name: str, score: ScoreFn, plans, B, batch_size) -> Selected:
    B = _check_budget(B)
    P = np.asarray(plans)
    if P.ndim != 2:
        raise ValueError(f"{name}: plans must be a 2-D array (n, D), got shape {P.shape}")
    if not np.issubdtype(P.dtype, np.integer):
        raise TypeError(f"{name}: plans must be an integer array, got {P.dtype}")
    if P.shape[0] < B:
        raise ValueError(f"{name}: {P.shape[0]} plans supplied for budget {B}")
    counter = _Counter(score, batch_size)
    s = counter(P[:B])
    j = int(np.argmax(s))
    counter.check(name, B)
    log = {"attacker": name, "budget": B, **counter.log(), "best_index": j, "best_score": float(s[j])}
    return Selected(np.array(P[j], copy=True), log)


def random_shooting(score: ScoreFn, proposals, B: int, *, batch_size: int | None = None) -> Selected:
    """Score the first ``B`` behaviour proposals, select the highest-scoring (first on ties).

    ``proposals`` holds at least ``B`` plans drawn from the behaviour distribution; using the
    first ``B`` makes budgets nest. ``B = 1`` selects the first proposal.
    """
    return _first_b("random_shooting", score, proposals, B, batch_size)


def best_of_n(score: ScoreFn, candidates, B: int, *, batch_size: int | None = None) -> Selected:
    """As :func:`random_shooting`, over a caller-supplied candidate zoo (first ``B`` rows)."""
    return _first_b("best_of_n", score, candidates, B, batch_size)


def cem_schedule(B: int) -> tuple[int, int]:
    """(generations, population) for budget ``B``; only the stated budgets have a schedule."""
    B = _check_budget(B)
    if B not in CEM_SCHEDULE:
        raise ValueError(
            f"no stated CEM schedule for B = {B} (stated: {sorted(CEM_SCHEDULE)}); "
            "pass schedule=(generations, population) with generations * population == B"
        )
    return CEM_SCHEDULE[B]


def cem(score: ScoreFn, space: Space, B: int, rng: np.random.Generator, init=None, *,
        schedule: tuple[int, int] | None = None, elite_frac: float = 0.1, smoothing: float = 0.7,
        prob_floor: float = 0.01, std_floor: float = 0.5, std_floor_frac: float = 0.02,
        batch_size: int | None = None) -> Selected:
    """Cross-entropy method over independent per-column distributions.

    ``init``: a :class:`Marginals` (e.g. from :func:`fit_marginals` on behaviour plans), an array
    of behaviour plans (fitted here), or None for uniform. Generation g draws ``population`` plans
    from the current distribution and scores them in one call; the top ``ceil(elite_frac *
    population)`` (at least one; ties broken by draw order) are fitted and the distribution moves
    ``smoothing`` of the way to the fit, then floors are applied (see
    :meth:`Marginals.apply_floors`). The schedule is :data:`CEM_SCHEDULE` unless ``schedule`` is
    given. The selected plan is the best-scoring plan seen in the whole run (earliest on ties).
    """
    B = _check_budget(B)
    G, N = cem_schedule(B) if schedule is None else (int(schedule[0]), int(schedule[1]))
    if G < 1 or N < 1 or G * N != B:
        raise ValueError(f"schedule {G} x {N} does not multiply to the budget {B}")
    if init is None:
        dist = Marginals.uniform_over(space)
    elif isinstance(init, Marginals):
        if init.space is not space and not _same_space(init.space, space):
            raise ValueError("init was built for a different space")
        dist = init.copy()
    else:
        dist = Marginals.fit(space, init)
    dist.apply_floors(prob_floor, std_floor, std_floor_frac)
    n_elite = max(1, math.ceil(elite_frac * N))
    counter = _Counter(score, batch_size)
    best_plan = None
    best_score = -np.inf
    best_index = -1
    best_per_gen: list[float] = []
    for g in range(G):
        X = dist.sample(rng, N)
        s = counter(X)
        j = int(np.argmax(s))
        if best_plan is None or s[j] > best_score:
            best_plan, best_score, best_index = X[j].copy(), float(s[j]), g * N + j
        best_per_gen.append(float(s[j]))
        if g + 1 < G:
            elite = X[np.argsort(-s, kind="stable")[:n_elite]]
            dist.smooth_towards(elite, smoothing).apply_floors(prob_floor, std_floor, std_floor_frac)
    counter.check("cem", B)
    log = {
        "attacker": "cem", "budget": B, **counter.log(), "generations": G, "population": N,
        "n_elite": n_elite, "best_index": best_index, "best_score": best_score,
        "best_per_generation": best_per_gen,
    }
    return Selected(best_plan, log)


def cem_seeded(score: ScoreFn, space: Space, B: int, rng: np.random.Generator, seeds, init=None, *, block: int,
               schedule: tuple[int, int] | None = None, elite_frac: float = 0.1, min_elite: int = 2,
               p_replace: float = 0.25, smoothing: float = 0.7, prob_floor: float = 0.01, std_floor: float = 0.5,
               std_floor_frac: float = 0.02, repair: Callable[[np.ndarray], np.ndarray] | None = None,
               batch_size: int | None = None) -> Selected:
    """Cross-entropy search seeded with proposals and mutated by whole blocks of columns.

    The schedule (generations G x population N) is :data:`CEM_SCHEDULE`'s unless ``schedule`` is given.
    Generation 0 is ``seeds[:N]`` (e.g. the behaviour proposals random shooting takes first), scored like any
    candidate. Before each later generation the elites are the top ``max(min_elite, ceil(elite_frac * N))`` of
    every plan scored so far (ties: scored earlier first; at most as many as have been scored); the distribution
    (``init`` as in :func:`cem`; None: fitted to ``seeds[:N]``) moves ``smoothing`` of the way to the elites' fit
    and the floors are applied (:meth:`Marginals.smooth_towards`, :meth:`Marginals.apply_floors`, as in
    :func:`cem`). Each of the N children is a copy of an elite chosen uniformly in which every block of ``block``
    consecutive columns (a month of a plan laid out month by month) is replaced, independently with probability
    ``p_replace``, by that block of a fresh draw from the distribution (column by column, independent columns);
    then ``repair`` (e.g. a grammar's canonical form; plans (n, D) -> (n, D)) and :meth:`Space.clip`. The selected
    plan is the best-scoring plan of the whole run (earliest on ties), so with one generation it is random
    shooting's selection over ``seeds[:B]``.
    """
    B = _check_budget(B)
    G, N = cem_schedule(B) if schedule is None else (int(schedule[0]), int(schedule[1]))
    if G < 1 or N < 1 or G * N != B:
        raise ValueError(f"schedule {G} x {N} does not multiply to the budget {B}")
    block = int(block)
    if block < 1 or space.D % block:
        raise ValueError(f"block {block} does not divide the plan length {space.D}")
    if not 0.0 <= float(p_replace) <= 1.0:
        raise ValueError("p_replace must lie in [0, 1]")
    S = np.asarray(seeds)
    if S.ndim != 2 or S.shape[1] != space.D:
        raise ValueError(f"seeds must be a 2-D array (n, {space.D}), got shape {S.shape}")
    if not np.issubdtype(S.dtype, np.integer):
        raise TypeError(f"seeds must be an integer array, got {S.dtype}")
    if S.shape[0] < N:
        raise ValueError(f"{S.shape[0]} seed plans supplied for a generation of {N}")
    if init is None:
        dist = Marginals.fit(space, S[:N])
    elif isinstance(init, Marginals):
        if init.space is not space and not _same_space(init.space, space):
            raise ValueError("init was built for a different space")
        dist = init.copy()
    else:
        dist = Marginals.fit(space, init)
    dist.apply_floors(prob_floor, std_floor, std_floor_frac)
    n_elite = max(int(min_elite), math.ceil(elite_frac * N))
    n_blocks = space.D // block
    counter = _Counter(score, batch_size)
    plans: list[np.ndarray] = []
    scores: list[np.ndarray] = []
    best_per_gen: list[float] = []
    replaced = 0
    X = np.array(S[:N], dtype=np.int64, copy=True)
    for g in range(G):
        if g > 0:
            P, s_all = np.concatenate(plans), np.concatenate(scores)
            elite = P[np.argsort(-s_all, kind="stable")[:min(n_elite, P.shape[0])]]
            dist.smooth_towards(elite, smoothing).apply_floors(prob_floor, std_floor, std_floor_frac)
            parent = elite[rng.integers(0, elite.shape[0], size=N)]
            mask = rng.random((N, n_blocks)) < float(p_replace)
            fresh = dist.sample(rng, N)
            X = np.where(np.repeat(mask, block, axis=1), fresh, parent)
            if repair is not None:
                X = np.asarray(repair(X), dtype=np.int64).reshape(N, space.D)
            X = space.clip(X)
            replaced += int(mask.sum())
        s = counter(X)
        plans.append(X)
        scores.append(s)
        best_per_gen.append(float(s.max()))
    counter.check("cem_seeded", B)
    s_all = np.concatenate(scores)
    j = int(np.argmax(s_all))
    log = {
        "attacker": "cem_seeded", "budget": B, **counter.log(), "generations": G, "population": N,
        "n_elite": n_elite, "block": block, "p_replace": float(p_replace), "blocks_replaced": replaced,
        "best_index": j, "best_score": float(s_all[j]), "best_per_generation": best_per_gen,
    }
    return Selected(np.concatenate(plans)[j].copy(), log)


def _same_space(a: Space, b: Space) -> bool:
    return all(np.array_equal(getattr(a, k), getattr(b, k)) for k in ("low", "high", "categorical", "frozen", "frozen_values"))
