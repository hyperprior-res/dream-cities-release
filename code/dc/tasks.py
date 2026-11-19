"""Task families and the shared predicate.

A task instance is (held-out start state, task family, horizon, threshold). Its predicate is one
function of a scalar trajectory, a float or integer array of shape (..., H+1, 20) in the layout of
``dc.engine.SCALAR_NAMES``, where row 0 is the start observation. The same function is applied to the
engine's replayed trajectory and to the emulator's predicted trajectory, so the two verdicts can differ
only through dynamics.

Five families (brief, section 6):

``grow``      population at H at least theta, and funds never negative.
``solvent``   population at H at least theta, and funds never below half the starting treasury.
``treasury``  (revenue form, study protocol) tax collected at the last yearly budget up to
              H (the engine's ``tax_fund`` at H) at least theta, funds never negative, and the tax
              rate never above the rate at the start. The first form, "funds at H at least theta",
              had a corner solution (maximum tax, no funding, build nothing).
``recover``   an earthquake is forced in month 0; population at H at least theta times the
              population before it.
``power``     at H: at least 95 per cent of zones powered, at most k plants (k = plants at the start
              plus one), and at least theta zones.

Each family has one calibrated number, theta, per instance. Since amendment 3 it sits halfway
between the best outcome of a constant no-build plan and the best outcome an engine-side search found
(``data/tasks_v2_H*.json``, built by ``dc.frontier``); ``calibrate_theta`` below is the first rule
(35 per cent success under the behaviour mix), kept for the record. Everything else is fixed here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, Optional, Tuple

import numpy as np

from .engine import (DISASTER_EARTHQUAKE, SC_COAL, SC_FUNDS, SC_NUCLEAR, SC_POP, SC_POWERED, SC_TAX, SC_TAX_FUND,
                     SC_UNPOWERED)
from .seeds import seed_for

TASKS: Tuple[str, ...] = ("grow", "solvent", "treasury", "recover", "power")
TARGET_BASE_RATE = 0.35
BAND = (0.20, 0.50)

SOLVENT_FLOOR = 0.5          # share of the starting treasury that must never be breached
POWER_FRACTION = 0.95        # share of zones that must be powered at H
POWER_EXTRA_PLANTS = 1       # k = plants at start + this
RECOVER_DISASTER = DISASTER_EARTHQUAKE
RECOVER_MONTH = 0


def forced_for(task: str) -> Dict[int, int]:
    """Forced disasters that belong to the task itself (the planner cannot change them)."""
    return {RECOVER_MONTH: RECOVER_DISASTER} if task == "recover" else {}


def statistic(task: str, scal: np.ndarray) -> np.ndarray:
    """The quantity theta is compared with. ``scal`` has shape (..., H+1, 20)."""
    s = np.asarray(scal, dtype=np.float64)
    if task in ("grow", "solvent"):
        return s[..., -1, SC_POP]
    if task == "treasury":
        return s[..., -1, SC_TAX_FUND]
    if task == "recover":
        return s[..., -1, SC_POP] / np.maximum(s[..., 0, SC_POP], 1.0)
    if task == "power":
        return s[..., -1, SC_POWERED] + s[..., -1, SC_UNPOWERED]
    raise ValueError(task)


def feasible(task: str, scal: np.ndarray) -> np.ndarray:
    """The clauses that carry no calibrated number."""
    s = np.asarray(scal, dtype=np.float64)
    funds = s[..., :, SC_FUNDS]
    if task == "grow":
        return funds.min(axis=-1) >= 0.0
    if task == "solvent":
        return funds.min(axis=-1) >= SOLVENT_FLOOR * funds[..., 0]
    if task == "treasury":
        # initial=-inf: a prefix that holds only the start row has no month yet and breaks no clause
        return (funds.min(axis=-1) >= 0.0) & (s[..., 1:, SC_TAX].max(axis=-1, initial=-np.inf) <= s[..., 0, SC_TAX])
    if task == "recover":
        return np.ones(s.shape[:-2], dtype=bool)
    if task == "power":
        powered, unpowered = s[..., -1, SC_POWERED], s[..., -1, SC_UNPOWERED]
        zones = powered + unpowered
        frac = np.where(zones > 0, powered / np.maximum(zones, 1.0), 0.0)
        k = s[..., 0, SC_COAL] + s[..., 0, SC_NUCLEAR] + POWER_EXTRA_PLANTS
        plants = s[..., -1, SC_COAL] + s[..., -1, SC_NUCLEAR]
        return (frac >= POWER_FRACTION) & (plants <= k)
    raise ValueError(task)


def verdict(task: str, scal: np.ndarray, theta: float) -> np.ndarray:
    """The shared predicate: True where the trajectory satisfies the task."""
    return feasible(task, scal) & (statistic(task, scal) >= theta)


# ----------------------------------------------------------------------------------------------
# The engine's verdict as a majority over seeds (study protocol)
# ----------------------------------------------------------------------------------------------
# The engine is stochastic, and a verdict on one fixed seed rewards plans fitted to that seed's luck
# (measured: plans selected by search on one seed pass on it far more often than on other seeds).
# The oracle is therefore the predicate's pass share over ORACLE_N seeds that are used for nothing
# else, accepted at ORACLE_PASS, the same convention as the emulator's verdict (4 of 8 samples).
ORACLE_N = 32
ORACLE_PASS = 0.5
ORACLE_SEED_NAME = "task-oracle"


def oracle_seeds(start_id: str, task: str, horizon: int, n: int = ORACLE_N):
    """The oracle's seeds for an instance: ``seed_for("task-oracle", start id, task, H, k)``."""
    return [seed_for(ORACLE_SEED_NAME, start_id, task, int(horizon), k) for k in range(n)]


def oracle_share(task: str, scal: np.ndarray, theta: float) -> np.ndarray:
    """Share of seeds on which the predicate holds. ``scal`` has shape (..., n_seeds, H+1, 20)."""
    return verdict(task, scal, theta).mean(axis=-1)


def oracle_verdict(task: str, scal: np.ndarray, theta: float) -> np.ndarray:
    """True where the predicate holds on at least ORACLE_PASS of the seeds (16 of 32 passes)."""
    v = verdict(task, scal, theta)
    return v.sum(axis=-1) * 2 >= v.shape[-1] if ORACLE_PASS == 0.5 else v.mean(axis=-1) >= ORACLE_PASS


def oracle_value(task: str, scal: np.ndarray) -> np.ndarray:
    """The largest theta the plan passes under the majority rule: the ceil(n/2)-th largest over seeds
    of the statistic where the trajectory is feasible (minus infinity where it is not). So
    ``oracle_verdict(task, scal, theta) == (oracle_value(task, scal) >= theta)``."""
    st = np.where(feasible(task, scal), statistic(task, scal), -np.inf)      # (..., n)
    n = st.shape[-1]
    k = int(np.ceil(n * ORACLE_PASS))
    return -np.sort(-st, axis=-1)[..., k - 1]


def margin(task: str, scal: np.ndarray, theta: float, stat_sd: float) -> np.ndarray:
    """Signed distance to passing: ``margin >= 0`` exactly where ``verdict`` is True.

    The minimum over the task's clauses of each clause's slack: the statistic's slack in units of its
    spread under the behaviour mix (``stat_sd``), funds slack as a share of the starting treasury,
    tax-rate slack in twentieths (the rate's range), power slack in units of 5 points of powered
    fraction, plant slack in plants. Search attackers
    maximise this on the emulator's rollouts; the instrument compares it between emulator and engine.
    """
    s = np.asarray(scal, dtype=np.float64)
    terms = [(statistic(task, s) - theta) / max(float(stat_sd), 1e-9)]
    funds = s[..., :, SC_FUNDS]
    f0 = np.maximum(np.abs(funds[..., 0]), 1.0)
    if task == "grow":
        terms.append(funds.min(axis=-1) / f0)
    elif task == "solvent":
        terms.append((funds.min(axis=-1) - SOLVENT_FLOOR * funds[..., 0]) / f0)
    elif task == "treasury":
        terms.append(funds.min(axis=-1) / f0)
        terms.append((s[..., 0, SC_TAX] - s[..., 1:, SC_TAX].max(axis=-1, initial=-np.inf)) / 20.0)
    elif task == "power":
        powered, unpowered = s[..., -1, SC_POWERED], s[..., -1, SC_UNPOWERED]
        zones = powered + unpowered
        frac = np.where(zones > 0, powered / np.maximum(zones, 1.0), 0.0)
        terms.append((frac - POWER_FRACTION) / 0.05)
        k = s[..., 0, SC_COAL] + s[..., 0, SC_NUCLEAR] + POWER_EXTRA_PLANTS
        terms.append(k - (s[..., -1, SC_COAL] + s[..., -1, SC_NUCLEAR]))
    return np.minimum.reduce(terms)


@dataclass
class TaskInstance:
    family_id: str
    start_id: str
    task: str
    horizon: int
    theta: float
    base_rate_fit: float                 # success rate on the calibration sample at theta
    base_rate_val: Optional[float] = None  # success rate on an independent validation sample
    n_fit: int = 0
    n_val: int = 0
    feasible_rate: float = 1.0           # share of behaviour plans meeting the uncalibrated clauses
    in_band: bool = True                 # base_rate_val (or fit) inside BAND
    stat_sd: float = 0.0                 # spread of the statistic under the behaviour mix (for normalising)
    note: str = ""

    @property
    def key(self) -> str:
        return f"{self.start_id}|{self.task}|H{self.horizon}"

    def to_dict(self) -> dict:
        return asdict(self)


def calibrate_theta(task: str, scal: np.ndarray, target: float = TARGET_BASE_RATE) -> Tuple[float, float, float]:
    """Choose theta from behaviour-mix trajectories ``scal`` (N, H+1, 20).

    Returns (theta, success rate at theta on this sample, share feasible). theta is the largest value
    at which the success rate is still at least ``target``; with ties in the statistic the rate can
    exceed the target, and if fewer than ``target`` of plans are feasible theta is the smallest feasible
    statistic (success rate = share feasible).
    """
    ok = feasible(task, scal)
    st = statistic(task, scal)
    n = len(st)
    feas = st[ok]
    if feas.size == 0:
        return float("inf"), 0.0, 0.0
    order = np.sort(feas)[::-1]                       # descending
    k = int(np.ceil(target * n))                      # how many plans should succeed
    k = min(max(k, 1), feas.size)
    theta = float(order[k - 1])
    rate = float(np.mean(ok & (st >= theta)))
    if rate > BAND[1]:
        # ties pushed the rate above the band: step theta up to the next distinct value if that lands in band
        higher = np.unique(feas[feas > theta])
        if higher.size:
            alt = float(higher[0])
            alt_rate = float(np.mean(ok & (st >= alt)))
            if BAND[0] <= alt_rate <= BAND[1] or abs(alt_rate - target) < abs(rate - target):
                theta, rate = alt, alt_rate
    return theta, rate, float(np.mean(ok))
