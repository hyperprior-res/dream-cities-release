"""Plan grammar and action raster.

A plan is a list of H grammar months. A grammar month is

    (tax 0..20, road, fire, police funding each in {0, 25, 50, 75, 100} per cent,
     forced disaster kind 0..6 where 0 is none, four macros (kind, x, y, a, b)).

Flat integer form (what action logs store and what search attackers optimise): an int16 array of
shape (H, 25). Columns 0..3 are tax, road, fire, police (the three funding columns hold the level
index 0..4, i.e. percent / 25), column 4 is the forced disaster kind (``dc.engine.DISASTER_*``), then
four macros of five columns each: kind, x, y, a, b. The per-column ranges are the data
``PLAN_COLUMNS`` (name, low, high inclusive). Any integer array is mapped into range by
``clip_plan``; any in-range array compiles (``compile_month`` is total).

Macro kinds (``MACRO_KINDS``, NOOP = 0) and what they compile to:

=========================================  ========  ==========================================
kind                                       a, b      calls
=========================================  ========  ==========================================
NOOP                                       -         none
ZONE_R, ZONE_C, ZONE_I                     1..3      a x b zones on a 3-tile pitch; zone (i, j)
                                                     is centred at (x + 3i, y + 3j)
ROAD_H, RAIL_H, WIRE_H                     a 1..30   a single-tile calls (x + i, y)
ROAD_V, RAIL_V, WIRE_V                     a 1..30   a single-tile calls (x, y + i)
COAL, NUCLEAR, POLICE, FIRE, STADIUM,      -         one call at (x, y)
SEAPORT, AIRPORT
PARK, BULLDOZE                             1..4      a x b calls at (x + i, y + j)
=========================================  ========  ==========================================

A call whose footprint (``FOOTPRINTS``, measured from the engine) does not lie entirely on the
120 x 100 map is dropped at compile time: the engine would refuse it. Everything else is passed
to the engine, which refuses what it cannot build (blocked, water, no money) and charges nothing
for a refused call. Fields a macro kind does not use are zero in canonical form.

The action raster (``raster``) has one channel per tool and marks the footprint of every attempted
call; it is computed from the plan row alone and says nothing about what the engine accepted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

import numpy as np

from .engine import (
    LOMASK, TOOL_AIRPORT, TOOL_BULLDOZER, TOOL_COALPOWER, TOOL_COMMERCIAL, TOOL_COSTS, TOOL_FIRESTATION,
    TOOL_INDUSTRIAL, TOOL_NUCLEARPOWER, TOOL_PARK, TOOL_POLICESTATION, TOOL_RAILROAD, TOOL_RESIDENTIAL,
    TOOL_ROAD, TOOL_SEAPORT, TOOL_STADIUM, TOOL_WIRE, WORLD_H, WORLD_W, Engine, MonthAction,
)

# ----------------------------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------------------------
M = 4                       # macros per month
N_COLS = 5 + 5 * M          # 25
BUDGET_LEVELS = (0, 25, 50, 75, 100)   # funding per cent for level index 0..4
N_DISASTER = 7              # 0 none, 1..6 = dc.engine.DISASTER_FIRE .. DISASTER_MELTDOWN
LINE_MAX = 30

MACRO_NAMES = [
    "NOOP", "ZONE_R", "ZONE_C", "ZONE_I", "ROAD_H", "ROAD_V", "RAIL_H", "RAIL_V", "WIRE_H", "WIRE_V",
    "COAL", "NUCLEAR", "POLICE", "FIRE", "STADIUM", "SEAPORT", "AIRPORT", "PARK", "BULLDOZE",
]
MACRO_KINDS: Dict[str, int] = {n: i for i, n in enumerate(MACRO_NAMES)}
N_KINDS = len(MACRO_NAMES)

# macro shape families
F_NONE, F_ZONE, F_HLINE, F_VLINE, F_BUILDING, F_RECT = 0, 1, 2, 3, 4, 5

# kind -> (engine tool or -1, shape family, (a_lo, a_hi), (b_lo, b_hi)); (0, 0) means unused (canonical 0)
_K = MACRO_KINDS
MACRO_SPEC: Dict[int, Tuple[int, int, Tuple[int, int], Tuple[int, int]]] = {
    _K["NOOP"]: (-1, F_NONE, (0, 0), (0, 0)),
    _K["ZONE_R"]: (TOOL_RESIDENTIAL, F_ZONE, (1, 3), (1, 3)),
    _K["ZONE_C"]: (TOOL_COMMERCIAL, F_ZONE, (1, 3), (1, 3)),
    _K["ZONE_I"]: (TOOL_INDUSTRIAL, F_ZONE, (1, 3), (1, 3)),
    _K["ROAD_H"]: (TOOL_ROAD, F_HLINE, (1, LINE_MAX), (0, 0)),
    _K["ROAD_V"]: (TOOL_ROAD, F_VLINE, (1, LINE_MAX), (0, 0)),
    _K["RAIL_H"]: (TOOL_RAILROAD, F_HLINE, (1, LINE_MAX), (0, 0)),
    _K["RAIL_V"]: (TOOL_RAILROAD, F_VLINE, (1, LINE_MAX), (0, 0)),
    _K["WIRE_H"]: (TOOL_WIRE, F_HLINE, (1, LINE_MAX), (0, 0)),
    _K["WIRE_V"]: (TOOL_WIRE, F_VLINE, (1, LINE_MAX), (0, 0)),
    _K["COAL"]: (TOOL_COALPOWER, F_BUILDING, (0, 0), (0, 0)),
    _K["NUCLEAR"]: (TOOL_NUCLEARPOWER, F_BUILDING, (0, 0), (0, 0)),
    _K["POLICE"]: (TOOL_POLICESTATION, F_BUILDING, (0, 0), (0, 0)),
    _K["FIRE"]: (TOOL_FIRESTATION, F_BUILDING, (0, 0), (0, 0)),
    _K["STADIUM"]: (TOOL_STADIUM, F_BUILDING, (0, 0), (0, 0)),
    _K["SEAPORT"]: (TOOL_SEAPORT, F_BUILDING, (0, 0), (0, 0)),
    _K["AIRPORT"]: (TOOL_AIRPORT, F_BUILDING, (0, 0), (0, 0)),
    _K["PARK"]: (TOOL_PARK, F_RECT, (1, 4), (1, 4)),
    _K["BULLDOZE"]: (TOOL_BULLDOZER, F_RECT, (1, 4), (1, 4)),
}

# Flat column ranges (inclusive). Kind-specific ranges for a and b are in MACRO_SPEC; compile_month
# clamps a and b into them, so any vector within PLAN_COLUMNS compiles.
PLAN_COLUMNS: List[Tuple[str, int, int]] = [
    ("tax", 0, 20),
    ("road", 0, 4),      # funding level index: per cent = 25 * value
    ("fire", 0, 4),
    ("police", 0, 4),
    ("disaster", 0, N_DISASTER - 1),
]
for _i in range(M):
    PLAN_COLUMNS += [
        (f"m{_i}_kind", 0, N_KINDS - 1),
        (f"m{_i}_x", 0, WORLD_W - 1),
        (f"m{_i}_y", 0, WORLD_H - 1),
        (f"m{_i}_a", 0, LINE_MAX),
        (f"m{_i}_b", 0, 4),
    ]
assert len(PLAN_COLUMNS) == N_COLS
COL_LOW = np.array([c[1] for c in PLAN_COLUMNS], dtype=np.int64)
COL_HIGH = np.array([c[2] for c in PLAN_COLUMNS], dtype=np.int64)

# Footprint of one call, measured from the engine (``measure_footprints``): tiles changed when the
# tool is used at (x, y) on clear land. (dx, dy, w, h): the footprint covers x+dx .. x+dx+w-1 and
# y+dy .. y+dy+h-1. 3x3 buildings are centred on (x, y); 4x4 and 6x6 buildings extend one tile up
# and left of (x, y) and the rest down and right. The bulldozer's footprint is the tile it is
# used on (on a zone's centre tile it clears the whole zone; on any other zone tile it is refused).
FOOTPRINTS: Dict[int, Tuple[int, int, int, int]] = {
    TOOL_RESIDENTIAL: (-1, -1, 3, 3),
    TOOL_COMMERCIAL: (-1, -1, 3, 3),
    TOOL_INDUSTRIAL: (-1, -1, 3, 3),
    TOOL_FIRESTATION: (-1, -1, 3, 3),
    TOOL_POLICESTATION: (-1, -1, 3, 3),
    TOOL_WIRE: (0, 0, 1, 1),
    TOOL_BULLDOZER: (0, 0, 1, 1),
    TOOL_RAILROAD: (0, 0, 1, 1),
    TOOL_ROAD: (0, 0, 1, 1),
    TOOL_STADIUM: (-1, -1, 4, 4),
    TOOL_PARK: (0, 0, 1, 1),
    TOOL_SEAPORT: (-1, -1, 4, 4),
    TOOL_COALPOWER: (-1, -1, 4, 4),
    TOOL_NUCLEARPOWER: (-1, -1, 4, 4),
    TOOL_AIRPORT: (-1, -1, 6, 6),
}
ZONE_PITCH = 3

# Raster channels, one per tool, in this order.
RASTER_TOOLS = [TOOL_RESIDENTIAL, TOOL_COMMERCIAL, TOOL_INDUSTRIAL, TOOL_FIRESTATION, TOOL_POLICESTATION,
                TOOL_WIRE, TOOL_BULLDOZER, TOOL_RAILROAD, TOOL_ROAD, TOOL_STADIUM, TOOL_PARK, TOOL_SEAPORT,
                TOOL_COALPOWER, TOOL_NUCLEARPOWER, TOOL_AIRPORT]
RASTER_CHANNELS = ["res", "com", "ind", "fire", "police", "wire", "bulldoze", "rail", "road", "stadium",
                   "park", "seaport", "coal", "nuclear", "airport"]
N_CHANNELS = len(RASTER_TOOLS)
TOOL_TO_CHANNEL = {t: i for i, t in enumerate(RASTER_TOOLS)}
N_ACTION_SCALARS = 4 + N_DISASTER

# Per-kind lookup arrays for the vectorised paths
_KIND_TOOL = np.array([MACRO_SPEC[k][0] for k in range(N_KINDS)], dtype=np.int64)
_KIND_FAM = np.array([MACRO_SPEC[k][1] for k in range(N_KINDS)], dtype=np.int64)
_KIND_ALO = np.array([MACRO_SPEC[k][2][0] for k in range(N_KINDS)], dtype=np.int64)
_KIND_AHI = np.array([MACRO_SPEC[k][2][1] for k in range(N_KINDS)], dtype=np.int64)
_KIND_BLO = np.array([MACRO_SPEC[k][3][0] for k in range(N_KINDS)], dtype=np.int64)
_KIND_BHI = np.array([MACRO_SPEC[k][3][1] for k in range(N_KINDS)], dtype=np.int64)
_KIND_CHAN = np.array([TOOL_TO_CHANNEL.get(int(t), -1) for t in _KIND_TOOL], dtype=np.int64)
_KIND_COST = np.array([TOOL_COSTS.get(int(t), 0) if t >= 0 else 0 for t in _KIND_TOOL], dtype=np.int64)
_FP = np.zeros((N_KINDS, 4), dtype=np.int64)   # dx, dy, w, h per kind
for _k in range(N_KINDS):
    _t = int(_KIND_TOOL[_k])
    _FP[_k] = FOOTPRINTS[_t] if _t >= 0 else (0, 0, 1, 1)


# ----------------------------------------------------------------------------------------------
# Structured form
# ----------------------------------------------------------------------------------------------
class Macro(NamedTuple):
    kind: int = 0
    x: int = 0
    y: int = 0
    a: int = 0
    b: int = 0


NOOP_MACRO = Macro()


@dataclass(frozen=True)
class GrammarMonth:
    tax: int = 7
    road: int = 100          # per cent, one of BUDGET_LEVELS
    fire: int = 100
    police: int = 100
    disaster: int = 0
    macros: Tuple[Macro, ...] = field(default_factory=lambda: (NOOP_MACRO,) * M)


NOOP_ROW = np.array([7, 4, 4, 4, 0] + [0] * (5 * M), dtype=np.int16)


def noop_row(tax: int = 7, road: int = 100, fire: int = 100, police: int = 100) -> np.ndarray:
    r = NOOP_ROW.copy()
    r[0] = tax
    r[1], r[2], r[3] = road // 25, fire // 25, police // 25
    return r


# ----------------------------------------------------------------------------------------------
# Range handling
# ----------------------------------------------------------------------------------------------
def clip_plan(arr) -> np.ndarray:
    """Map any integer array of shape (..., 25) into the column ranges and canonical form.

    Columns are clipped to ``PLAN_COLUMNS``; then each macro's a and b are clamped into its kind's
    range and fields its kind does not use are zeroed (a NOOP macro becomes all zeros). The result
    is a valid plan array: ``encode_plan(decode_plan(clip_plan(a))) == clip_plan(a)``.
    """
    a = np.asarray(arr)
    if a.shape[-1] != N_COLS:
        raise ValueError(f"plan rows must have {N_COLS} columns, got shape {a.shape}")
    out = np.clip(a.astype(np.int64), COL_LOW, COL_HIGH)
    mac = out[..., 5:].reshape(out.shape[:-1] + (M, 5))
    k = mac[..., 0]
    mac[..., 3] = np.clip(mac[..., 3], _KIND_ALO[k], _KIND_AHI[k])
    mac[..., 4] = np.clip(mac[..., 4], _KIND_BLO[k], _KIND_BHI[k])
    noop = k == 0
    mac[..., 1] = np.where(noop, 0, mac[..., 1])
    mac[..., 2] = np.where(noop, 0, mac[..., 2])
    out[..., 5:] = mac.reshape(out.shape[:-1] + (5 * M,))
    return out.astype(np.int16)


def is_valid_plan(arr) -> bool:
    a = np.asarray(arr)
    return bool(a.shape[-1] == N_COLS and np.array_equal(clip_plan(a), a.astype(np.int16)))


# ----------------------------------------------------------------------------------------------
# Encode / decode
# ----------------------------------------------------------------------------------------------
def encode_month(m: GrammarMonth) -> np.ndarray:
    r = np.zeros((N_COLS,), dtype=np.int16)
    r[0] = m.tax
    r[1], r[2], r[3] = m.road // 25, m.fire // 25, m.police // 25
    r[4] = m.disaster
    macs = tuple(m.macros) + (NOOP_MACRO,) * (M - len(m.macros))
    if len(macs) != M:
        raise ValueError(f"at most {M} macros a month")
    for i, mc in enumerate(macs):
        r[5 + 5 * i: 10 + 5 * i] = (mc.kind, mc.x, mc.y, mc.a, mc.b)
    return r


def decode_month(row) -> GrammarMonth:
    r = clip_plan(np.asarray(row).reshape(N_COLS))
    macs = tuple(Macro(*(int(v) for v in r[5 + 5 * i: 10 + 5 * i])) for i in range(M))
    return GrammarMonth(int(r[0]), BUDGET_LEVELS[int(r[1])], BUDGET_LEVELS[int(r[2])], BUDGET_LEVELS[int(r[3])],
                        int(r[4]), macs)


def encode_plan(plan: Sequence[GrammarMonth]) -> np.ndarray:
    """List of grammar months -> int16 (H, 25)."""
    if len(plan) == 0:
        return np.zeros((0, N_COLS), dtype=np.int16)
    return np.stack([encode_month(m) for m in plan]).astype(np.int16)


def decode_plan(arr) -> List[GrammarMonth]:
    """int array (H, 25) -> list of grammar months (the array is clipped into range first)."""
    a = np.asarray(arr).reshape(-1, N_COLS)
    return [decode_month(r) for r in a]


# ----------------------------------------------------------------------------------------------
# Compile
# ----------------------------------------------------------------------------------------------
def _on_map(tool: int, x: int, y: int) -> bool:
    dx, dy, w, h = FOOTPRINTS[tool]
    return x + dx >= 0 and y + dy >= 0 and x + dx + w <= WORLD_W and y + dy + h <= WORLD_H


def macro_calls(kind: int, x: int, y: int, a: int, b: int) -> List[Tuple[int, int, int]]:
    """Engine tool calls (tool, x, y) of one canonical macro, in order, off-map calls dropped."""
    tool, fam, _, _ = MACRO_SPEC[kind]
    if fam == F_NONE:
        return []
    if fam == F_ZONE:
        pts = [(x + ZONE_PITCH * i, y + ZONE_PITCH * j) for j in range(b) for i in range(a)]
    elif fam == F_HLINE:
        pts = [(x + i, y) for i in range(a)]
    elif fam == F_VLINE:
        pts = [(x, y + i) for i in range(a)]
    elif fam == F_BUILDING:
        pts = [(x, y)]
    else:  # F_RECT
        pts = [(x + i, y + j) for j in range(b) for i in range(a)]
    return [(tool, px, py) for px, py in pts if _on_map(tool, px, py)]


def month_calls(row) -> List[Tuple[int, int, int]]:
    r = clip_plan(np.asarray(row).reshape(N_COLS))
    calls: List[Tuple[int, int, int]] = []
    for i in range(M):
        k, x, y, a, b = (int(v) for v in r[5 + 5 * i: 10 + 5 * i])
        calls.extend(macro_calls(k, x, y, a, b))
    return calls


def _as_row(month) -> np.ndarray:
    if isinstance(month, GrammarMonth):
        return encode_month(month)
    return np.asarray(month).reshape(N_COLS)


def compile_month(month) -> Tuple[MonthAction, int]:
    """One grammar month (row of 25 ints or GrammarMonth) -> (MonthAction, forced disaster kind).

    Deterministic and total: the row is clipped into range first.
    """
    r = clip_plan(_as_row(month))
    calls = month_calls(r)
    tools = np.asarray(calls, dtype=np.int16).reshape(-1, 3)
    act = MonthAction(int(r[0]), BUDGET_LEVELS[int(r[1])], BUDGET_LEVELS[int(r[2])], BUDGET_LEVELS[int(r[3])], tools)
    return act, int(r[4])


def compile_plan(arr) -> Tuple[List[MonthAction], Dict[int, int]]:
    """Plan (H, 25) -> (MonthActions, {month: forced disaster kind}) for ``dc.oracle.replay``."""
    if not isinstance(arr, np.ndarray) and len(arr) and isinstance(arr[0], GrammarMonth):
        arr = encode_plan(arr)
    a = np.asarray(arr).reshape(-1, N_COLS)
    acts: List[MonthAction] = []
    forced: Dict[int, int] = {}
    for t in range(a.shape[0]):
        act, d = compile_month(a[t])
        acts.append(act)
        if d:
            forced[t] = d
    return acts, forced


# ----------------------------------------------------------------------------------------------
# Raster, action scalars, nominal cost
# ----------------------------------------------------------------------------------------------
def _macro_geometry(rows: np.ndarray):
    """Vectorised geometry of every macro of canonical rows (N, 25).

    Returns per macro (N, M) arrays: channel, x0, x1, y0, y1 (union of the footprints of the calls
    kept, half-open), number of calls kept, tool. A macro with no kept call has n == 0.
    """
    mac = rows[:, 5:].reshape(-1, M, 5).astype(np.int64)
    k, x, y, a, b = (mac[..., i] for i in range(5))
    fam = _KIND_FAM[k]
    dx, dy, w, h = (_FP[k][..., i] for i in range(4))
    one = np.ones_like(a)
    # index ranges along each axis: positions x + step*i for i in [0, na), y + step*j for j in [0, nb)
    na = np.where(fam == F_ZONE, a, np.where(fam == F_HLINE, a, np.where(fam == F_RECT, a, one)))
    nb = np.where(fam == F_ZONE, b, np.where(fam == F_VLINE, a, np.where(fam == F_RECT, b, one)))
    sx = np.where(fam == F_ZONE, ZONE_PITCH, 1)
    sy = sx
    # call i is on the map iff 0 <= x + sx*i + dx and x + sx*i + dx + w <= W
    lo_i = np.ceil(np.maximum(0, -(x + dx)) / sx).astype(np.int64)
    hi_i = np.floor((WORLD_W - w - x - dx) / sx).astype(np.int64)      # inclusive
    lo_j = np.ceil(np.maximum(0, -(y + dy)) / sy).astype(np.int64)
    hi_j = np.floor((WORLD_H - h - y - dy) / sy).astype(np.int64)
    i0, i1 = lo_i, np.minimum(hi_i, na - 1)
    j0, j1 = lo_j, np.minimum(hi_j, nb - 1)
    ni = np.maximum(0, i1 - i0 + 1)
    nj = np.maximum(0, j1 - j0 + 1)
    n = np.where(fam == F_NONE, 0, ni * nj)
    x0 = x + dx + sx * i0
    x1 = x + dx + sx * i1 + w
    y0 = y + dy + sy * j0
    y1 = y + dy + sy * j1 + h
    return _KIND_CHAN[k], x0, x1, y0, y1, n, _KIND_TOOL[k]


def _rows2d(rows) -> np.ndarray:
    if isinstance(rows, MonthAction):
        raise TypeError("pass plan rows, not MonthActions, to the batch functions")
    if isinstance(rows, (list, tuple)) and len(rows) and isinstance(rows[0], GrammarMonth):
        rows = encode_plan(rows)
    a = np.asarray(rows)
    return clip_plan(a.reshape(-1, N_COLS))


def raster_batch(rows) -> np.ndarray:
    """Plan rows (B, 25) (or a list of rows / GrammarMonths) -> float32 (B, 15, 120, 100)."""
    r = _rows2d(rows)
    B = r.shape[0]
    out = np.zeros((B, N_CHANNELS, WORLD_W, WORLD_H), dtype=np.float32)
    ch, x0, x1, y0, y1, n, _ = _macro_geometry(r)
    bi, mi = np.nonzero(n > 0)
    for b_, m_ in zip(bi.tolist(), mi.tolist()):
        out[b_, ch[b_, m_], x0[b_, m_]:x1[b_, m_], y0[b_, m_]:y1[b_, m_]] = 1.0
    return out


def raster(action) -> np.ndarray:
    """One month -> float32 (15, 120, 100).

    ``action`` is a plan row (25 ints), a GrammarMonth, or a compiled MonthAction (the footprints
    of its tool calls are marked). Every attempted call counts, accepted or not.
    """
    if isinstance(action, MonthAction):
        out = np.zeros((N_CHANNELS, WORLD_W, WORLD_H), dtype=np.float32)
        for t, x, y in action.tools.astype(int).tolist():
            if t not in TOOL_TO_CHANNEL or not _on_map(t, x, y):
                continue
            dx, dy, w, h = FOOTPRINTS[t]
            out[TOOL_TO_CHANNEL[t], x + dx:x + dx + w, y + dy:y + dy + h] = 1.0
        return out
    return raster_batch(_as_row(action)[None])[0]


def action_scalars_batch(rows) -> np.ndarray:
    r = _rows2d(rows).astype(np.int64)
    out = np.zeros((r.shape[0], N_ACTION_SCALARS), dtype=np.float32)
    out[:, 0] = r[:, 0] / 20.0
    out[:, 1] = r[:, 1] * 25 / 100.0
    out[:, 2] = r[:, 2] * 25 / 100.0
    out[:, 3] = r[:, 3] * 25 / 100.0
    out[np.arange(r.shape[0]), 4 + r[:, 4]] = 1.0
    return out


def action_scalars(row) -> np.ndarray:
    """float32 (11,): tax/20, road/100, fire/100, police/100, one-hot of the forced disaster kind (7)."""
    return action_scalars_batch(_as_row(row)[None])[0]


def nominal_cost_batch(rows) -> np.ndarray:
    r = _rows2d(rows)
    _, _, _, _, _, n, tool = _macro_geometry(r)
    cost = np.where(tool >= 0, _KIND_COST[r[:, 5::5].astype(np.int64)], 0)
    return (cost * n).sum(axis=1).astype(np.int64)


def nominal_cost(row) -> int:
    """Cost from the engine's cost table assuming every compiled call succeeds."""
    return int(nominal_cost_batch(_as_row(row)[None])[0])


def n_calls_batch(rows) -> np.ndarray:
    r = _rows2d(rows)
    return _macro_geometry(r)[5].sum(axis=1).astype(np.int64)


def n_calls(row) -> int:
    return int(n_calls_batch(_as_row(row)[None])[0])


# ----------------------------------------------------------------------------------------------
# Random plans (for tests, the uniform random editor and optimisers)
# ----------------------------------------------------------------------------------------------
def random_plan(rng: np.random.Generator, H: int, p_noop_macro: float = 0.0) -> np.ndarray:
    """Uniform random valid plan (H, 25): every column uniform over its range, then canonicalised."""
    a = rng.integers(COL_LOW, COL_HIGH + 1, size=(H, N_COLS))
    if p_noop_macro > 0:
        kill = rng.random((H, M)) < p_noop_macro
        a[:, 5::5][kill] = 0
    return clip_plan(a)


# ----------------------------------------------------------------------------------------------
# Empirical footprint measurement (used by the tests and the acceptance report)
# ----------------------------------------------------------------------------------------------
FOOTPRINT_PROBE_SEED = 1     # terrain seed used for the measurement


def _find_clear_square(tiles: np.ndarray, k: int, margin: int = 8) -> Optional[Tuple[int, int]]:
    t = tiles & LOMASK
    for x in range(margin, WORLD_W - k - margin):
        for y in range(margin, WORLD_H - k - margin):
            if not (t[x:x + k, y:y + k]).any():
                return x, y
    return None


def measure_footprints(eng: Optional[Engine] = None, seed: int = FOOTPRINT_PROBE_SEED) -> Dict[int, dict]:
    """Place every tool once on clear land of a generated terrain and read the tile map.

    Returns {tool: {"result": engine code, "cost": funds charged, "dx": .., "dy": .., "w": .., "h": ..,
    "changed": number of tiles changed}}. For the bulldozer, a road tile is laid first and then
    bulldozed. Used to check ``FOOTPRINTS``.
    """
    own = eng is None
    eng = eng or Engine()
    try:
        eng.new_terrain(seed, 1_000_000)
        sq = _find_clear_square(eng.observe().tiles, 10)
        if sq is None:
            raise RuntimeError("no clear 10x10 square on the probe terrain")
        cx, cy = sq[0] + 3, sq[1] + 3
        out: Dict[int, dict] = {}
        for tool in RASTER_TOOLS:
            eng.new_terrain(seed, 1_000_000)
            if tool == TOOL_BULLDOZER:
                eng.apply(MonthAction(tools=np.array([[TOOL_ROAD, cx, cy]])))
            before = eng.observe().tiles.copy()
            res, cost = eng.apply(MonthAction(tools=np.array([[tool, cx, cy]])))
            if tool == TOOL_BULLDOZER:
                cost -= TOOL_COSTS[TOOL_ROAD]
            d = np.argwhere(before != eng.observe().tiles)
            rec = {"result": int(res[0]), "cost": int(cost), "changed": int(len(d)), "at": (cx, cy)}
            if len(d):
                (x0, y0), (x1, y1) = d.min(0), d.max(0)
                rec.update(dx=int(x0 - cx), dy=int(y0 - cy), w=int(x1 - x0 + 1), h=int(y1 - y0 + 1))
            out[tool] = rec
        return out
    finally:
        if own:
            eng.close()


def measure_zone_tiling(eng: Optional[Engine] = None, seed: int = FOOTPRINT_PROBE_SEED) -> dict:
    """Compile ZONE_R 3x3 on clear land, apply it, and check the 9 zones tile a 9x9 square exactly."""
    own = eng is None
    eng = eng or Engine()
    try:
        eng.new_terrain(seed, 1_000_000)
        sq = _find_clear_square(eng.observe().tiles, 10)
        x, y = sq[0] + 1, sq[1] + 1
        row = NOOP_ROW.copy()
        row[5:10] = (MACRO_KINDS["ZONE_R"], x, y, 3, 3)
        act, _ = compile_month(row)
        before = eng.observe().tiles.copy()
        res, cost = eng.apply(act)
        after = eng.observe().tiles
        changed = before != after
        zone_tiles = ((after & LOMASK) >= 240) & ((after & LOMASK) <= 248)
        centres = np.argwhere((after & 0x0400) != 0)
        expect = np.zeros_like(changed)
        expect[x - 1:x + 8, y - 1:y + 8] = True
        return {
            "accepted": int((res == 1).sum()), "calls": int(len(res)), "cost": int(cost),
            "changed_equals_9x9": bool(np.array_equal(changed, expect)),
            "zone_tiles_in_square": int(zone_tiles[x - 1:x + 8, y - 1:y + 8].sum()),
            "centres": sorted((int(a - x), int(b - y)) for a, b in centres),
            "raster_equals_changed": bool(np.array_equal(raster(row)[0] > 0, changed)),
        }
    finally:
        if own:
            eng.close()
