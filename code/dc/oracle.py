"""The oracle: exact engine replay from a start-state file, a seed and an action log.

``replay`` is a pure function of (city file bytes, action log, seed, disaster settings) and the
protocol constants in ``dc.engine``. It never restores a state: every call begins with a full
simulator reset and the engine's own loader, so an engine instance can be reused freely.

Order within a month, fixed by the protocol:

1. budget settings (tax, then road / fire / police funding),
2. tool calls in action-log order,
3. a forced disaster, if one is scheduled for this month,
4. the simulator advances one city-month (four city-time units of sixteen passes),
5. the observation for the next month boundary is read.

The random generator is seeded once, after the load and before month 0's actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np

from .engine import NUM_LEDGER, NUM_SCALARS, Engine, MonthAction, Obs


@dataclass
class Replay:
    obs0: Obs                           # observation at the start (month boundary 0)
    scalars: np.ndarray                 # (H+1, 20) int64, row t is the observation at boundary t
    build_cost: np.ndarray              # (H,) int64, funds the engine charged for month t's tool calls
    tool_ok: List[np.ndarray]           # per month, per-call result codes
    states: Optional[List[Obs]] = None  # H+1 observations when record="full"
    hashes: Optional[np.ndarray] = None  # (H+1,) uint64 full-state hashes when want_hash
    ledger: Optional[np.ndarray] = None  # (H+1, NUM_LEDGER) int64, row t is the ledger at boundary t
                                        # (dc.engine.LEDGER_NAMES); filled by replay


def replay(
    eng: Engine,
    cty_path,
    actions: Sequence[MonthAction],
    seed: int,
    *,
    disasters: bool = False,
    forced: Optional[Dict[int, int]] = None,
    record: str = "scalars",
    want_hash: bool = False,
) -> Replay:
    """Replay ``actions`` from the start state in ``cty_path`` under ``seed``.

    ``record``: "scalars" keeps the scalar trajectory only; "full" also keeps every observation.
    ``forced``: {month index: disaster kind}, applied after that month's tool calls.
    """
    H = len(actions)
    eng.load_start(cty_path)
    eng.set_disasters(disasters)   # before the first observation: the flag is part of the ledger
    obs0 = eng.observe()
    eng.seed(seed)

    scal = np.empty((H + 1, NUM_SCALARS), dtype=np.int64)
    scal[0] = obs0.scalars
    led = np.empty((H + 1, NUM_LEDGER), dtype=np.int64)
    led[0] = eng.ledger()
    cost = np.zeros((H,), dtype=np.int64)
    ok: List[np.ndarray] = []
    states = [obs0] if record == "full" else None
    hashes = np.empty((H + 1,), dtype=np.uint64) if want_hash else None
    if hashes is not None:
        hashes[0] = eng.hash_full()

    for m in range(H):
        res, c = eng.apply(actions[m])
        ok.append(res)
        cost[m] = c
        if forced and m in forced:
            eng.force_disaster(forced[m])
        eng.step_month()
        if record == "full":
            o = eng.observe()
            states.append(o)
            scal[m + 1] = o.scalars
            led[m + 1] = o.ledger
        else:
            scal[m + 1] = eng.scalars()
            led[m + 1] = eng.ledger()
        if hashes is not None:
            hashes[m + 1] = eng.hash_full()
    return Replay(obs0, scal, cost, ok, states, hashes, led)
