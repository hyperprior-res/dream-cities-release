"""Engine-only task frontiers and the thresholds-v2 rule .

Everything here is computed from the engine (``dc.oracle.replay`` through ``dc.audit.EngineJudge``);
no emulator is involved.

Per task instance i (start state, task family, horizon H) with the nine verdict seeds (the primary
``dc.audit.primary_seed`` and the eight ``dc.audit.secondary_seeds``):

* **c_i, the do-nothing frontier.** The 2,625 constant plans (``GRID``: tax 0..20 by the five funding
  levels of each of roads, fire and police; no macro; the same row every month) are replayed on the
  primary seed; the 20 best by ``J`` are replayed on the eight secondary seeds as well. c_i is the
  largest statistic of a feasible trajectory among all of those replays; if none is feasible, c_i is
  the largest statistic among them regardless of feasibility (``c_feasible`` False).
* **J**, the ordering every candidate is ranked by on the primary seed: the statistic when the
  trajectory is feasible, otherwise ``J_INFEASIBLE`` plus the slack of the violated clause (negative),
  so every infeasible plan lies below every feasible one and infeasible plans are ordered by how far
  they miss. Slacks are in the units of ``dc.tasks.margin``: funds as a share of the starting treasury,
  powered share in units of 5 points, plants in plants, population (treasury v2) as a share of the
  starting population.
* **e_i, the engine-side frontier.** Among finalists replayed on all nine seeds, the largest nine-seed
  mean statistic of a plan feasible on all nine seeds (``frontier_e``). The frontier plan's
  seed-to-seed standard deviation of the statistic (nine seeds, ddof = 1) is ``seed_sd``.
* **theta_i(lambda) = c_i + lambda (e_i - c_i)**; **well posed** when e_i - c_i >= 4 seed_sd.

Variants (``VARIANTS``): the five task families of ``dc.tasks`` with two predicates for ``treasury``:
``treasury_v1`` (``dc.tasks`` as it stands: funds at H >= theta) and ``treasury_v2`` (funds at H >=
theta and population at H >= population at the start). A variant's seeds and effective plans are those
of its base task (``base_task``), so the two treasury variants share every replay of a plan.
"""

from __future__ import annotations

import itertools
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

from . import tasks as T
from .behaviour import Policy
from .engine import SC_COAL, SC_FUNDS, SC_NUCLEAR, SC_POP, SC_POWERED, SC_TAX, SC_TAX_FUND, SC_UNPOWERED
from .grammar import N_COLS, NOOP_ROW, clip_plan

# ----------------------------------------------------------------------------------------------
# Constants of the rule
# ----------------------------------------------------------------------------------------------
LAMBDAS = (0.25, 0.5, 0.75)
LAMBDA_PRIMARY = 0.5
WELL_POSED_K = 4.0            # e - c >= this many seed standard deviations of the frontier plan
N_CONST_TOP = 20              # constant plans replayed on the secondary seeds
N_FINALISTS = 50              # finalists per candidate source
J_INFEASIBLE = -1.0e9         # J of an infeasible trajectory = this + its (negative) violated-clause slack (float64
                              # resolution at 1e9 is 1.2e-7 slack units; every statistic lies far above)

# Constant settings: (tax, road level, fire level, police level), level index 0..4 = 0..100 per cent.
GRID: np.ndarray = np.array([(t, r, f, p) for t in range(21) for r, f, p in itertools.product(range(5), repeat=3)],
                            dtype=np.int16)
assert GRID.shape == (2625, 4)
DEFAULT_SETTING = (7, 4, 4, 4)

VARIANTS: Dict[str, Tuple[str, str]] = {
    "grow": ("grow", "v1"),
    "solvent": ("solvent", "v1"),
    "treasury_v1": ("treasury", "v1"),
    "treasury_v2": ("treasury", "v2"),
    "recover": ("recover", "v1"),
    "power": ("power", "v1"),
    # alternative treasury predicate (tested only if treasury_v2 is degenerate): tax revenue
    "treasury_rev": ("treasury", "rev"),
}
# the five families as adopted (study protocol), in dc.tasks order: treasury in its revenue form
PROPOSAL_VARIANTS: Tuple[str, ...] = ("grow", "solvent", "treasury_rev", "recover", "power")
PREDICATES: Dict[str, str] = {
    "grow": "population at H >= theta and funds never negative",
    "solvent": "population at H >= theta and funds never below half the starting treasury",
    "treasury_v1": "funds at H >= theta",
    "treasury_v2": "funds at H >= theta and population at H >= population at the start",
    "recover": "earthquake forced in month 0; population at H / population at the start >= theta",
    "power": "at H: >= 95 per cent of zones powered, <= plants at start + 1 plants, zones >= theta",
    "treasury_rev": "tax collected at the last yearly budget up to H (tax_fund at H) >= theta, funds never negative, "
                    "and the tax rate never above the rate at the start",
}


def base_task(variant: str) -> str:
    return VARIANTS[variant][0]


# ----------------------------------------------------------------------------------------------
# Plans
# ----------------------------------------------------------------------------------------------
def constant_plans(H: int, settings: Optional[np.ndarray] = None) -> np.ndarray:
    """int16 (n, H, 25): a no-op row with each setting's tax and funding levels, every month."""
    S = GRID if settings is None else np.asarray(settings, dtype=np.int16).reshape(-1, 4)
    P = np.tile(NOOP_ROW, (S.shape[0], H, 1)).astype(np.int16)
    P[:, :, 0:4] = S[:, None, :]
    return clip_plan(P)


def overwrite_budget(plans: np.ndarray, setting) -> np.ndarray:
    """Plans (n, H, 25) with the tax and the three funding columns of every month set to ``setting``."""
    P = np.array(plans, dtype=np.int16, copy=True)
    P[..., 0:4] = np.asarray(setting, dtype=np.int16).reshape(4)
    return clip_plan(P)


def setting_str(setting) -> str:
    t, r, f, p = (int(v) for v in setting)
    return f"tax {t}, road {25 * r}%, fire {25 * f}%, police {25 * p}%"


# ----------------------------------------------------------------------------------------------
# Statistic, feasibility, slack, J
# ----------------------------------------------------------------------------------------------
def statistic(variant: str, scal: np.ndarray) -> np.ndarray:
    # The three treasury predicates of the study are stated here in full: since amendment 3 ``dc.tasks``
    # holds the revenue form as ``treasury`` (a test checks that ``treasury_rev`` equals it), and the two
    # funds forms (v1, v2) exist only in this module, for the record of why they were dropped.
    task, ver = VARIANTS[variant]
    if task == "treasury":
        s = np.asarray(scal, dtype=np.float64)
        return s[..., -1, SC_TAX_FUND] if ver == "rev" else s[..., -1, SC_FUNDS]
    return T.statistic(task, scal)


def feasible(variant: str, scal: np.ndarray) -> np.ndarray:
    task, ver = VARIANTS[variant]
    if task != "treasury":
        return T.feasible(task, scal)
    s = np.asarray(scal, dtype=np.float64)
    if ver == "v2":
        return s[..., -1, SC_POP] >= s[..., 0, SC_POP]
    if ver == "rev":
        return (s[..., :, SC_FUNDS].min(axis=-1) >= 0.0) & (s[..., 1:, SC_TAX].max(axis=-1) <= s[..., 0, SC_TAX])
    return np.ones(s.shape[:-2], dtype=bool)


def slack(variant: str, scal: np.ndarray) -> np.ndarray:
    """Minimum over the variant's uncalibrated clauses of each clause's slack; >= 0 exactly where
    ``feasible`` (up to rounding); +inf for a variant with no such clause."""
    task, ver = VARIANTS[variant]
    s = np.asarray(scal, dtype=np.float64)
    funds = s[..., :, SC_FUNDS]
    f0 = np.maximum(np.abs(funds[..., 0]), 1.0)
    terms = []
    if task == "grow":
        terms.append(funds.min(axis=-1) / f0)
    elif task == "solvent":
        terms.append((funds.min(axis=-1) - T.SOLVENT_FLOOR * funds[..., 0]) / f0)
    elif task == "power":
        powered, unpowered = s[..., -1, SC_POWERED], s[..., -1, SC_UNPOWERED]
        zones = powered + unpowered
        frac = np.where(zones > 0, powered / np.maximum(zones, 1.0), 0.0)
        terms.append((frac - T.POWER_FRACTION) / 0.05)
        k = s[..., 0, SC_COAL] + s[..., 0, SC_NUCLEAR] + T.POWER_EXTRA_PLANTS
        terms.append(k - (s[..., -1, SC_COAL] + s[..., -1, SC_NUCLEAR]))
    if task == "treasury" and ver == "v2":
        p0 = s[..., 0, SC_POP]
        terms.append((s[..., -1, SC_POP] - p0) / np.maximum(p0, 1.0))
    if ver == "rev":
        terms.append(funds.min(axis=-1) / f0)
        terms.append((s[..., 0, SC_TAX] - s[..., 1:, SC_TAX].max(axis=-1)) / 20.0)
    if not terms:
        return np.full(s.shape[:-2], np.inf)
    return np.minimum.reduce(terms)


def J(variant: str, scal: np.ndarray) -> np.ndarray:
    """The ranking score: the statistic if feasible, else ``J_INFEASIBLE`` + the violated clause's slack."""
    ok = feasible(variant, scal)
    st = statistic(variant, scal)
    sl = np.minimum(slack(variant, scal), 0.0)
    sl = np.where(np.isfinite(sl), sl, 0.0)
    return np.where(ok, st, J_INFEASIBLE + sl)


def verdict(variant: str, scal: np.ndarray, theta: float) -> np.ndarray:
    return feasible(variant, scal) & (statistic(variant, scal) >= theta)


def margin(variant: str, scal: np.ndarray, theta: float, stat_sd: float) -> np.ndarray:
    """``dc.tasks.margin`` for the variant: for treasury v2 the population clause's slack (as a share of
    the starting population) joins the minimum. ``margin >= 0`` exactly where ``verdict``."""
    task, ver = VARIANTS[variant]
    if task == "treasury":                    # all three forms: the statistic's slack and the clauses' slack
        return np.minimum((statistic(variant, scal) - theta) / max(float(stat_sd), 1e-9), slack(variant, scal))
    return T.margin(task, scal, theta, stat_sd)


def top_k(scores: np.ndarray, k: int, tie=None) -> np.ndarray:
    """Indices of the k largest scores, descending. Ties are broken by ``tie`` (larger first; e.g. the
    feasibility slack, so that among equal statistics the plan with more room in its other clauses comes
    first; non-finite values count as 0), then by position (earliest first)."""
    s = np.asarray(scores, dtype=np.float64)
    idx = np.arange(s.size)
    if tie is None:
        order = np.argsort(-s, kind="stable")
    else:
        t = np.asarray(tie, dtype=np.float64)
        t = np.where(np.isfinite(t), t, 0.0)
        order = np.lexsort((idx, -t, -s))
    return order[: min(int(k), s.size)]


# ----------------------------------------------------------------------------------------------
# The rule
# ----------------------------------------------------------------------------------------------
def frontier_c(variant: str, const_primary: np.ndarray, top_idx: np.ndarray, const_secondary: np.ndarray) -> dict:
    """c_i from the constant replays.

    ``const_primary`` (n_grid, H+1, 20): every constant plan on the primary seed; ``top_idx`` (k,): the
    plans also replayed on the secondary seeds; ``const_secondary`` (k, n_sec, H+1, 20).
    Returns c, whether it came from a feasible replay, and where (grid index, seed index 0 = primary).
    """
    st_p, ok_p = statistic(variant, const_primary), feasible(variant, const_primary)
    st_s, ok_s = statistic(variant, const_secondary), feasible(variant, const_secondary)
    # candidates: (statistic, feasible, grid index, seed index)
    stats = np.concatenate([st_p, st_s.reshape(-1)])
    oks = np.concatenate([ok_p, ok_s.reshape(-1)])
    gidx = np.concatenate([np.arange(st_p.size), np.repeat(np.asarray(top_idx), st_s.shape[1])])
    sidx = np.concatenate([np.zeros(st_p.size, dtype=np.int64), np.tile(np.arange(1, st_s.shape[1] + 1), st_s.shape[0])])
    c_feasible = bool(oks.any())
    pool = np.where(oks, stats, -np.inf) if c_feasible else stats
    j = int(np.argmax(pool))
    # diagnostic, not part of the rule: the like-for-like counterpart of e (nine-seed mean of the best constant
    # plan feasible on all nine seeds, among those replayed on the nine seeds)
    st9 = np.concatenate([st_p[np.asarray(top_idx)][:, None], st_s], axis=1)
    ok9 = np.concatenate([ok_p[np.asarray(top_idx)][:, None], ok_s], axis=1).all(axis=1)
    m9 = st9.mean(axis=1)
    if ok9.any():
        j9 = int(np.argmax(np.where(ok9, m9, -np.inf)))
        c_mean9, c_mean9_sd = float(m9[j9]), float(np.std(st9[j9], ddof=1))
        c_mean9_stats, c_mean9_index = [float(v) for v in st9[j9]], int(np.asarray(top_idx)[j9])
    else:
        c_mean9 = c_mean9_sd = float("nan")
        c_mean9_stats, c_mean9_index = None, -1
    return {"c": float(stats[j]), "c_feasible": c_feasible, "c_grid_index": int(gidx[j]), "c_seed_index": int(sidx[j]),
            "c_setting": [int(v) for v in GRID[int(gidx[j])]] if const_primary.shape[0] == GRID.shape[0] else None,
            "c_primary_only": float(np.max(np.where(ok_p, st_p, -np.inf))) if ok_p.any() else float(np.max(st_p)),
            "c_mean9": c_mean9, "c_mean9_seed_sd": c_mean9_sd, "c_mean9_stats": c_mean9_stats,
            "c_mean9_grid_index": c_mean9_index,
            "n_const_replays": int(st_p.size + st_s.size), "n_const_feasible_replays": int(oks.sum())}


def frontier_e(variant: str, scal9: np.ndarray) -> dict:
    """e_i from finalists replayed on the nine verdict seeds, ``scal9`` (n, 9, H+1, 20), seed 0 primary.

    e = the largest nine-seed mean statistic among finalists feasible on all nine seeds; NaN if none is.
    """
    st = statistic(variant, scal9)                       # (n, 9)
    ok9 = feasible(variant, scal9).all(axis=1)
    mean = st.mean(axis=1)
    out = {"n_finalists": int(st.shape[0]), "n_feasible_all_seeds": int(ok9.sum())}
    if not ok9.any():
        out.update(e=float("nan"), frontier_index=-1, seed_sd=float("nan"), e_primary=float("nan"))
        return out
    j = int(np.argmax(np.where(ok9, mean, -np.inf)))
    out.update(e=float(mean[j]), frontier_index=j, seed_sd=float(np.std(st[j], ddof=1)), e_primary=float(st[j, 0]),
               frontier_stats=[float(v) for v in st[j]])
    return out


def theta_of(c: float, e: float, lam: float) -> float:
    return float(c + lam * (e - c))


def well_posed(c: float, e: float, seed_sd: float, k: float = WELL_POSED_K) -> bool:
    if not (np.isfinite(c) and np.isfinite(e) and np.isfinite(seed_sd)):
        return False
    return bool(e - c >= k * seed_sd)


def rule(variant: str, const_primary, top_idx, const_secondary, finalist_scal9, stat_sd: float) -> dict:
    """The whole rule on one instance: c, e, thetas, well-posedness, headroom in seed sd and stat_sd."""
    cd = frontier_c(variant, const_primary, top_idx, const_secondary)
    ed = frontier_e(variant, finalist_scal9)
    c, e, sd = cd["c"], ed["e"], ed["seed_sd"]
    out = {**cd, **ed}
    for lam in LAMBDAS:
        out[f"theta_l{int(round(100 * lam))}"] = theta_of(c, e, lam) if np.isfinite(e) else float("nan")
    out["theta"] = out[f"theta_l{int(round(100 * LAMBDA_PRIMARY))}"]
    out["well_posed"] = well_posed(c, e, sd)
    out["headroom"] = float(e - c) if np.isfinite(e) else float("nan")
    out["headroom_seed_sd"] = float((e - c) / sd) if (np.isfinite(e) and sd > 0) else (
        float("inf") if (np.isfinite(e) and sd == 0 and e > c) else float("nan"))
    out["headroom_stat_sd"] = float((e - c) / stat_sd) if (np.isfinite(e) and stat_sd > 0) else float("nan")
    return out


# ----------------------------------------------------------------------------------------------
# Search initialisation
# ----------------------------------------------------------------------------------------------
def centred_init(space, pool_flat: np.ndarray, setting, H: int):
    """CEM init: per-column marginals fitted to ``pool_flat`` (n, H*25) with CEM's floors
    (``hpr_dream.fit_marginals``), then the Gaussian mean of every month's tax and three funding
    columns moved to ``setting``; their standard deviations stay as fitted (floored)."""
    import hpr_dream as hd
    m = hd.fit_marginals(space, pool_flat)
    L = space._layout
    pos = {int(c): j for j, c in enumerate(L.int_cols)}
    for t in range(H):
        for k in range(4):
            col = t * N_COLS + k
            m.mu[pos[col]] = float(setting[k])
    m._cdf = None
    return m


# ----------------------------------------------------------------------------------------------
# Closed-loop builders under a fixed budget setting (candidate source c)
# ----------------------------------------------------------------------------------------------
class BudgetOverride(Policy):
    """Wraps a policy: every month's tax and funding columns are set to ``setting`` and the disaster
    column to the task's own forced event of that month (so the closed loop sees what the replay will)."""

    def __init__(self, base, setting, forced: Optional[Dict[int, int]] = None):
        self.base = base
        self.setting = np.asarray(setting, dtype=np.int64).reshape(4)
        self.forced = dict(forced or {})
        self.label = getattr(base, "label", "policy") + "+budget"

    def reset(self, obs, rng):
        super().reset(obs, rng)
        self.base.reset(obs, rng)

    def act(self, obs, t):
        row = np.asarray(self.base.act(obs, t)).astype(np.int64).copy()
        row[0:4] = self.setting
        row[4] = int(self.forced.get(t, 0))
        return clip_plan(row)


def builder_styles() -> Tuple[str, ...]:
    from .behaviour import BUILDER_STYLES
    return tuple(sorted(BUILDER_STYLES))


def closed_loop_seeds(start_id: str, H: int, forced_key: str, setting, j: int) -> Tuple[int, int]:
    from .seeds import seed_for
    s = "-".join(str(int(v)) for v in setting)
    return (seed_for("tv2-c-policy", start_id, H, forced_key, s, j), seed_for("tv2-c-gen", start_id, H, forced_key, s, j))


def closed_loop_plan(eng, start_id: str, cty, H: int, setting, forced: Dict[int, int], forced_key: str, j: int):
    """Plan j of source c: a scripted builder (style drawn uniformly from ``BUILDER_STYLES`` by the plan's own
    generator, as ``scripts/gen_builder_pool.py`` does) plays H months closed loop in the engine with the budget
    columns held at ``setting`` and the task's forced events applied. Returns (raw plan int16 (H, 25) with the
    forced column cleared, style label)."""
    from .behaviour import make_policy, rollout_behaviour
    s_pol, s_gen = closed_loop_seeds(start_id, H, forced_key, setting, j)
    rng = np.random.default_rng(s_pol)
    styles = builder_styles()
    style = styles[int(rng.integers(len(styles)))]
    label = f"builder/{style}"
    pol = BudgetOverride(make_policy(label), setting, forced)
    plan, _ = rollout_behaviour(eng, cty, pol, H, s_gen, False, rng, record="scalars")
    plan = np.asarray(plan, dtype=np.int16).copy()
    plan[:, 4] = 0
    return plan, label


_W_ENG = None


def closed_loop_job(args) -> Tuple[bytes, str]:
    """Process-pool job: (start_id, cty, H, setting, forced, forced_key, j) -> (plan bytes, label)."""
    global _W_ENG
    if _W_ENG is None:
        from .engine import Engine
        _W_ENG = Engine()
    start_id, cty, H, setting, forced, forced_key, j = args
    plan, label = closed_loop_plan(_W_ENG, start_id, cty, H, setting, forced, forced_key, j)
    return plan.tobytes(), label


# ----------------------------------------------------------------------------------------------
# Plan description (what frontier plans do)
# ----------------------------------------------------------------------------------------------
def describe_plan(plan: np.ndarray) -> dict:
    """Macros per month by kind (attempted, non-NOOP), and the tax and funding the plan uses."""
    from .grammar import MACRO_NAMES, M
    P = np.asarray(plan).reshape(-1, N_COLS)
    H = P.shape[0]
    kinds = P[:, 5::5][:, :M].reshape(-1)
    cnt = np.bincount(kinds.astype(np.int64), minlength=len(MACRO_NAMES))
    per_month = {MACRO_NAMES[k]: float(cnt[k] / H) for k in range(1, len(MACRO_NAMES)) if cnt[k]}
    return {"macros_per_month": float((kinds != 0).sum() / H), "by_kind_per_month": per_month,
            "builds_nothing": bool((kinds == 0).all()),
            "tax_mean": float(P[:, 0].mean()), "tax_min": int(P[:, 0].min()), "tax_max": int(P[:, 0].max()),
            "road_pct_mean": float(25 * P[:, 1].mean()), "fire_pct_mean": float(25 * P[:, 2].mean()),
            "police_pct_mean": float(25 * P[:, 3].mean()),
            "constant_budget": bool((P[:, 0:4] == P[0, 0:4]).all())}


# ----------------------------------------------------------------------------------------------
# The majority rule on fresh oracle seeds (added 2026-11-10)
# ----------------------------------------------------------------------------------------------
N_ORACLE = 32
WELL_POSED_SE = 6.0           # e32 - c32 >= this many standard errors of the median
SE_MEDIAN_FACTOR = 1.2533     # standard error of a median ~ 1.2533 sd / sqrt(n) (normal approximation)


def majority_value(stat: np.ndarray, feas: np.ndarray) -> np.ndarray:
    """m_n: the ceil(n/2)-th largest over the last axis (seeds) of the statistic where feasible, minus infinity
    where not (for n = 32, the 16th largest, the upper median). ``m_n >= theta`` holds exactly when the predicate
    passes on at least half of the seeds; an exact 16 of 32 passes."""
    v = np.where(np.asarray(feas, dtype=bool), np.asarray(stat, dtype=np.float64), -np.inf)
    n = v.shape[-1]
    k = int(np.ceil(n / 2))
    return -np.sort(-v, axis=-1)[..., k - 1]


def majority_pass(stat: np.ndarray, feas: np.ndarray, theta: float) -> np.ndarray:
    """Pass under the majority rule, counted directly (at least half of the seeds pass)."""
    v = np.asarray(feas, dtype=bool) & (np.asarray(stat, dtype=np.float64) >= theta)
    return v.sum(axis=-1) * 2 >= v.shape[-1]


def rule32(const_stat: np.ndarray, const_feas: np.ndarray, front_stat: Optional[np.ndarray],
           front_feas: Optional[np.ndarray]) -> dict:
    """c32, e32, theta32(lambda) and well-posedness on the oracle seeds.

    ``const_*`` (20, n): the 20 best constant plans; ``front_*`` (n,): the nine-seed rule's frontier plan (None if
    the nine-seed rule has none). c32 = the largest majority value among the constants, e32 = the frontier plan's;
    seed_sd32 = sd over the n seeds of the frontier plan's statistic (ddof 1, feasibility aside); well posed when
    e32 - c32 >= 6 x 1.2533 seed_sd32 / sqrt(n), or, where seed_sd32 is 0, when e32 - c32 > 0."""
    mc = majority_value(const_stat, const_feas)
    jc = int(np.argmax(mc))
    out = {"c32": float(mc[jc]), "c32_const_rank": jc, "c32_finite": bool(np.isfinite(mc[jc]))}
    if front_stat is None:
        out.update(e32=float("nan"), seed_sd32=float("nan"), se32=float("nan"), well_posed32=False,
                   front_feasible_seeds32=0)
    else:
        n = front_stat.shape[-1]
        e32 = float(majority_value(front_stat, front_feas))
        sd = float(np.std(front_stat, ddof=1))
        se = SE_MEDIAN_FACTOR * sd / np.sqrt(n)
        h = e32 - out["c32"]
        ok = bool(np.isfinite(h) and ((h >= WELL_POSED_SE * se) if sd > 0 else (h > 0)))
        out.update(e32=e32, seed_sd32=sd, se32=float(se), well_posed32=ok,
                   front_feasible_seeds32=int(np.sum(front_feas)))
    c32, e32 = out["c32"], out["e32"]
    fin = bool(np.isfinite(c32) and np.isfinite(e32))
    for lam in LAMBDAS:
        out[f"theta32_l{int(round(100 * lam))}"] = float(c32 + lam * (e32 - c32)) if fin else float("nan")
    out["headroom32"] = float(e32 - c32) if fin else float("nan")
    out["headroom32_se"] = (float((e32 - c32) / out["se32"]) if out["se32"] > 0 else
                            (float("inf") if e32 > c32 else float("nan"))) if fin else float("nan")
    return out
