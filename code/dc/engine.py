"""ctypes binding to the patched city engine (``engine/libmicropolis.so``).

Exact-replay protocol. A simulator state is only ever produced by

* the engine's seeded map generator (``new_terrain``),
* the engine's own city-file loader after a full reset (``load_start``),
* tool calls and month steps.

There is no state injection. An earlier version restored a partial state
(tiles, eight overlays, twenty scalars) into a live simulator and left
everything else from the previous city, which made a replay depend on what the
instance had simulated before. That path is removed here and in the C shim.

Protocol constants are fixed below and written into REPRODUCE.md. Changing any
of them changes every result.

Sufficient observation (2026-11-10). The tile map, overlays and twenty scalars
do not contain everything the monthly update reads. ``Obs.ledger`` (names in
``LEDGER_NAMES``) and the two carried maps ``Obs.terrain`` and ``Obs.com_rate``
hold the rest; with the generator state (``Engine.rng_state``) and the sprite
list (``Engine.sprites``) they determine the next month exactly
(results/oracle/observation_sufficiency.md). ``Engine._test_restore`` exists
only for that proof and is never used to produce a state.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB_PATH = REPO_ROOT / "engine" / "libmicropolis.so"

# ----------------------------------------------------------------------------
# Protocol constants (REPRODUCE.md, "Replay protocol")
# ----------------------------------------------------------------------------
PROTO_SPEED = 1        # engine simSpeed. At 1 the power scan and the pollution/land-value scan run
                       # every 2 simulation cycles and the crime, population-density and fire scans
                       # every cycle; a month is 4 cycles, so every observation is current.
PROTO_PASSES = 1       # simulator passes per tick
PROTO_LEVEL = 0        # game level (easy) for every city, including bundled ones
PROTO_VERSION = "dc-replay-1"

WORLD_W, WORLD_H = 120, 100
WORLD_W_2, WORLD_H_2 = 60, 50
WORLD_W_8, WORLD_H_8 = 15, 13
NUM_SCALARS = 20

# Tile word: low 10 bits tile index, high 6 bits flags.
LOMASK = 0x03FF
ZONEBIT, ANIMBIT, BULLBIT, BURNBIT, CONDBIT, PWRBIT = 0x0400, 0x0800, 0x1000, 0x2000, 0x4000, 0x8000

# Editing tools (engine/src/tool.h)
TOOL_RESIDENTIAL, TOOL_COMMERCIAL, TOOL_INDUSTRIAL = 0, 1, 2
TOOL_FIRESTATION, TOOL_POLICESTATION, TOOL_QUERY = 3, 4, 5
TOOL_WIRE, TOOL_BULLDOZER, TOOL_RAILROAD, TOOL_ROAD = 6, 7, 8, 9
TOOL_STADIUM, TOOL_PARK, TOOL_SEAPORT = 10, 11, 12
TOOL_COALPOWER, TOOL_NUCLEARPOWER, TOOL_AIRPORT = 13, 14, 15

TOOL_NAMES = {
    0: "res", 1: "com", 2: "ind", 3: "fire", 4: "police", 5: "query", 6: "wire", 7: "bulldoze",
    8: "rail", 9: "road", 10: "stadium", 11: "park", 12: "seaport", 13: "coal", 14: "nuclear", 15: "airport",
}
# Nominal tool costs from the engine's cost table (tool.cpp). The engine's own accounting is
# authoritative: ``Engine.apply`` returns what a month's tool calls actually cost.
TOOL_COSTS = {0: 100, 1: 100, 2: 100, 3: 500, 4: 500, 5: 0, 6: 5, 7: 1, 8: 20, 9: 10,
              10: 5000, 11: 10, 12: 3000, 13: 3000, 14: 5000, 15: 10000}
# Footprint edge in tiles. For 3x3 buildings (x, y) is the centre; for 4x4 and 6x6 the engine
# anchors one tile up-left of the centre-left tile (see tool.cpp).
TOOL_SIZES = {0: 3, 1: 3, 2: 3, 3: 3, 4: 3, 6: 1, 7: 1, 8: 1, 9: 1, 10: 4, 11: 1, 12: 4, 13: 4, 14: 4, 15: 6}

# Scalars (index into Obs.scalars)
SC_FUNDS, SC_TAX, SC_RES_VALVE, SC_COM_VALVE, SC_IND_VALVE = 0, 1, 2, 3, 4
SC_POP, SC_RES_POP, SC_COM_POP, SC_IND_POP, SC_TIME, SC_SCORE = 5, 6, 7, 8, 9, 10
SC_TAX_FUND, SC_ROAD_SPEND, SC_FIRE_SPEND, SC_POLICE_SPEND = 11, 12, 13, 14
SC_POWERED, SC_UNPOWERED, SC_COAL, SC_NUCLEAR, SC_ROAD_TOTAL = 15, 16, 17, 18, 19
SCALAR_NAMES = [
    "funds", "tax", "res_valve", "com_valve", "ind_valve", "pop", "res_pop", "com_pop", "ind_pop",
    "city_time", "score", "tax_fund", "road_spend", "fire_spend", "police_spend",
    "powered_zones", "unpowered_zones", "coal_plants", "nuclear_plants", "road_total",
]

# Ledger (index into Obs.ledger): simulator members carried from one month to a later one that the
# observation above does not determine. Order mirrors enum LedgerIndex in engine/c_api.cpp; append
# only. Source references for each entry: results/oracle/observation_sufficiency.md.
LEDGER_NAMES = [
    "sim_cycle",        # simCycle 0..1023: cycle counter; parity gates setValves and the power and
                        # pollution scans, multiples of 5 gate the rate-of-growth decay
    "sprite_cycle",     # spriteCycle (int16): tick counter; sprite cadence (speedCycle = this mod 1024)
    "disasters",        # enableDisasters 0/1: the trajectory's disaster switch
    "initial_eval",     # doInitialEval 0/1: 1 only at the boundary right after a load
    "total_pop",        # totalPop: set by setValves on even cycles from the previous cycle's census
    "res_hist0", "res_hist1",   # resHist[0..1]: last two monthly censuses of resPop / 8 (setValves)
    "com_hist0", "com_hist1",   # comHist[0..1]
    "ind_hist0", "ind_hist1",   # indHist[0..1]
    "res_cap", "com_cap", "ind_cap",   # demand caps 0/1 (no stadium / airport / seaport)
    "need_hospital", "need_church",    # -1, 0, 1 from the monthly census
    "road_fund", "police_fund", "fire_fund",   # funding requested at the last tax collection
    "auto_budget",      # autoBudget 0/1: the engine switches it off when the treasury cannot pay
    "fire_pop",         # fire tiles counted by the last cycle (read by the initial evaluation)
    "city_center_x", "city_center_y",       # zone centre of mass at the last population scan
    "pollution_max_x", "pollution_max_y",   # most polluted block (generator tie-breaks); monster target
    "flood_count",      # flood spreads while > 0
    "abs_dist",         # last sprite distance from getDir, read stale by aircraft and the monster
]
NUM_LEDGER = len(LEDGER_NAMES)
LG = {n: i for i, n in enumerate(LEDGER_NAMES)}
LEDGER_ALL = (1 << NUM_LEDGER) - 1

# Carried maps that are not observed.
TERRAIN_SHAPE = (WORLD_W // 4, WORLD_H // 4)      # (30, 25) uint8 terrainDensityMap
COM_RATE_SHAPE = (WORLD_W_8, WORLD_H_8)           # (15, 13) int16 comRateMap

# Sprite rows (Engine.sprites), one int32 per field, in the engine's list order.
SPRITE_FIELDS = [
    "type", "frame", "x", "y", "width", "height", "x_offset", "y_offset", "x_hot", "y_hot",
    "orig_x", "orig_y", "dest_x", "dest_y", "count", "sound_count", "dir", "new_dir", "step", "flag",
    "control", "turn", "accel", "speed", "is_global",
]
SPRITE_TRAIN, SPRITE_HELICOPTER, SPRITE_AIRPLANE, SPRITE_SHIP = 1, 2, 3, 4
SPRITE_MONSTER, SPRITE_TORNADO, SPRITE_EXPLOSION, SPRITE_BUS = 5, 6, 7, 8

# Forced disasters (mc_force_disaster)
DISASTER_FIRE, DISASTER_FLOOD, DISASTER_EARTHQUAKE, DISASTER_TORNADO, DISASTER_MONSTER, DISASTER_MELTDOWN = 1, 2, 3, 4, 5, 6


@dataclass
class Obs:
    """What a player (and the emulator) sees at a month boundary."""

    tiles: np.ndarray      # (120, 100) uint16, raw tile words (index | flags)
    half: np.ndarray       # (5, 60, 50) uint8: population density, traffic, pollution, land value, crime
    power: np.ndarray      # (120, 100) uint8: power grid
    eighth: np.ndarray     # (3, 15, 13) int16: rate of growth, fire coverage, police coverage
    scalars: np.ndarray    # (20,) int64, see SCALAR_NAMES
    ledger: Optional[np.ndarray] = None    # (NUM_LEDGER,) int64, see LEDGER_NAMES
    terrain: Optional[np.ndarray] = None   # (30, 25) uint8: terrain density (carried, not an overlay)
    com_rate: Optional[np.ndarray] = None  # (15, 13) int16: commercial rate map (carried)

    @property
    def pop(self) -> int:
        return int(self.scalars[SC_POP])

    @property
    def funds(self) -> int:
        return int(self.scalars[SC_FUNDS])

    @property
    def zones(self) -> int:
        return int(self.scalars[SC_POWERED] + self.scalars[SC_UNPOWERED])

    @property
    def powered_fraction(self) -> float:
        z = self.zones
        return float(self.scalars[SC_POWERED]) / z if z > 0 else 1.0

    @property
    def plants(self) -> int:
        return int(self.scalars[SC_COAL] + self.scalars[SC_NUCLEAR])


_EMPTY_TOOLS = np.zeros((0, 3), dtype=np.int16)


@dataclass
class MonthAction:
    """One month of play: budget settings, then tool calls in order, then the month advances."""

    tax: int = 7
    road: int = 100
    fire: int = 100
    police: int = 100
    tools: np.ndarray = field(default_factory=lambda: _EMPTY_TOOLS)  # (n, 3) int16: tool, x, y

    def __post_init__(self) -> None:
        t = np.asarray(self.tools, dtype=np.int16).reshape(-1, 3)
        self.tools = t
        self.tax = int(min(20, max(0, self.tax)))
        self.road, self.fire, self.police = (int(min(100, max(0, v))) for v in (self.road, self.fire, self.police))

    def to_list(self) -> list:
        return [self.tax, self.road, self.fire, self.police, self.tools.astype(int).tolist()]

    @staticmethod
    def from_list(v: Sequence) -> "MonthAction":
        return MonthAction(int(v[0]), int(v[1]), int(v[2]), int(v[3]), np.asarray(v[4], dtype=np.int16).reshape(-1, 3))


NOOP = MonthAction()

_LIB: Optional[ctypes.CDLL] = None


def _lib() -> ctypes.CDLL:
    global _LIB
    if _LIB is None:
        if not LIB_PATH.exists():
            raise FileNotFoundError(f"{LIB_PATH} not built; run `make -C engine`")
        L = ctypes.CDLL(str(LIB_PATH))
        vp, ci = ctypes.c_void_p, ctypes.c_int
        L.mc_create.restype = vp
        L.mc_destroy.argtypes = [vp]
        L.mc_init_generated.argtypes = [vp, ci, ci, ci, ci, ci, ci]
        L.mc_load_start.argtypes = [vp, ctypes.c_char_p, ci, ci, ci]
        L.mc_load_start.restype = ci
        L.mc_save_city.argtypes = [vp, ctypes.c_char_p]
        L.mc_save_city.restype = ci
        L.mc_set_funds.argtypes = [vp, ci]
        L.mc_set_game_level.argtypes = [vp, ci]
        L.mc_seed.argtypes = [vp, ci]
        L.mc_set_disasters.argtypes = [vp, ci]
        L.mc_set_tax.argtypes = [vp, ci]
        L.mc_set_funding.argtypes = [vp, ctypes.c_float, ctypes.c_float, ctypes.c_float]
        L.mc_do_tool.argtypes = [vp, ci, ci, ci]
        L.mc_do_tool.restype = ci
        L.mc_force_disaster.argtypes = [vp, ci]
        L.mc_step_month.argtypes = [vp]
        L.mc_get_build_cost.argtypes = [vp]
        L.mc_get_build_cost.restype = ctypes.c_int64
        L.mc_hash_state.argtypes = [vp]
        L.mc_hash_state.restype = ctypes.c_uint64
        L.mc_hash_full.argtypes = [vp]
        L.mc_hash_full.restype = ctypes.c_uint64
        L.mc_get_state.argtypes = [
            vp, ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_int16), ctypes.POINTER(ctypes.c_int64),
        ]
        # Ledger and read-only accessors (2026-11-10).
        L.mc_ledger_len.restype = ci
        L.mc_sprite_fields.restype = ci
        L.mc_aux_len.restype = ci
        L.mc_get_ledger.argtypes = [vp, ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_uint8),
                                    ctypes.POINTER(ctypes.c_int16)]
        L.mc_get_rng.argtypes = [vp]
        L.mc_get_rng.restype = ctypes.c_uint64
        L.mc_get_sprites.argtypes = [vp, ctypes.POINTER(ctypes.c_int32), ci]
        L.mc_get_sprites.restype = ci
        L.mc_hash_dynamic.argtypes = [vp]
        L.mc_hash_dynamic.restype = ctypes.c_uint64
        # Test only (see Engine._test_restore).
        L.mc_test_get_aux.argtypes = [vp, ctypes.POINTER(ctypes.c_int64)]
        L.mc_test_restore.argtypes = [
            vp, ctypes.POINTER(ctypes.c_uint16), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_int16), ctypes.POINTER(ctypes.c_int64),
            ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_int16),
            ctypes.c_uint64, ctypes.POINTER(ctypes.c_int32), ci, ctypes.POINTER(ctypes.c_int64),
            ctypes.c_uint64, ci, ci, ci, ci,
        ]
        L.mc_test_restore.restype = ci
        if L.mc_ledger_len() != NUM_LEDGER or L.mc_sprite_fields() != len(SPRITE_FIELDS):
            raise RuntimeError("engine/libmicropolis.so ledger layout differs from dc.engine; run `make -C engine`")
        _LIB = L
    return _LIB


class Engine:
    """One simulator instance. Safe to reuse across replays: ``load_start`` is a full reset."""

    def __init__(self) -> None:
        self._L = _lib()
        self._p = self._L.mc_create()
        self._tiles = np.zeros((WORLD_W, WORLD_H), dtype=np.uint16)
        self._half = np.zeros((5, WORLD_W_2, WORLD_H_2), dtype=np.uint8)
        self._power = np.zeros((WORLD_W, WORLD_H), dtype=np.uint8)
        self._eighth = np.zeros((3, WORLD_W_8, WORLD_H_8), dtype=np.int16)
        self._scal = np.zeros((NUM_SCALARS,), dtype=np.int64)
        self._ledger = np.zeros((NUM_LEDGER,), dtype=np.int64)
        self._terrain = np.zeros(TERRAIN_SHAPE, dtype=np.uint8)
        self._com_rate = np.zeros(COM_RATE_SHAPE, dtype=np.int16)

    def close(self) -> None:
        if getattr(self, "_p", None):
            self._L.mc_destroy(self._p)
            self._p = None

    def __del__(self) -> None:  # pragma: no cover
        try:
            self.close()
        except Exception:
            pass

    # -- producing a state -----------------------------------------------------------------
    def new_terrain(self, map_seed: int, funds: int = 20000) -> None:
        """Seeded map generator. Used only to build start-state families."""
        self._L.mc_init_generated(self._p, int(map_seed), int(funds), PROTO_SPEED, PROTO_PASSES, 0, PROTO_LEVEL)

    def load_start(self, cty_path) -> None:
        """Full reset, then the engine's own loader. The only way a replay starts."""
        ok = self._L.mc_load_start(self._p, str(cty_path).encode(), PROTO_LEVEL, PROTO_SPEED, PROTO_PASSES)
        if not ok:
            raise RuntimeError(f"engine could not load {cty_path}")

    def save_city(self, cty_path) -> None:
        if not self._L.mc_save_city(self._p, str(cty_path).encode()):
            raise RuntimeError(f"engine could not save {cty_path}")

    def set_funds(self, funds: int) -> None:
        self._L.mc_set_funds(self._p, int(funds))

    # -- playing -----------------------------------------------------------------------------
    def seed(self, seed: int) -> None:
        self._L.mc_seed(self._p, int(seed) & 0x7FFFFFFF)

    def set_disasters(self, on: bool) -> None:
        self._L.mc_set_disasters(self._p, 1 if on else 0)

    def force_disaster(self, kind: int) -> None:
        self._L.mc_force_disaster(self._p, int(kind))

    def apply(self, act: MonthAction) -> Tuple[np.ndarray, int]:
        """Apply a month's settings and tool calls. Returns (per-call result codes, funds spent).

        Result code 1 is success; anything else means the engine refused the call
        (no funds, blocked, out of bounds) and nothing was built.
        """
        L, p = self._L, self._p
        L.mc_set_tax(p, act.tax)
        L.mc_set_funding(p, act.road / 100.0, act.fire / 100.0, act.police / 100.0)
        n = act.tools.shape[0]
        res = np.zeros((n,), dtype=np.int8)
        tl = act.tools
        for i in range(n):
            res[i] = L.mc_do_tool(p, int(tl[i, 0]), int(tl[i, 1]), int(tl[i, 2]))
        return res, int(L.mc_get_build_cost(p))

    def step_month(self) -> None:
        self._L.mc_step_month(self._p)

    # -- reading -----------------------------------------------------------------------------
    def observe(self) -> Obs:
        self._L.mc_get_state(
            self._p,
            self._tiles.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16)),
            self._half.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            self._power.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            self._eighth.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
            self._scal.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        )
        self._L.mc_get_ledger(
            self._p,
            self._ledger.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self._terrain.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            self._com_rate.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
        )
        return Obs(self._tiles.copy(), self._half.copy(), self._power.copy(), self._eighth.copy(), self._scal.copy(),
                   self._ledger.copy(), self._terrain.copy(), self._com_rate.copy())

    def scalars(self) -> np.ndarray:
        self._L.mc_get_state(self._p, None, None, None, None, self._scal.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)))
        return self._scal.copy()

    def ledger(self) -> np.ndarray:
        """The ledger vector alone (names in LEDGER_NAMES)."""
        self._L.mc_get_ledger(self._p, self._ledger.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)), None, None)
        return self._ledger.copy()

    def rng_state(self) -> int:
        """Full state of the engine's random generator (64-bit)."""
        return int(self._L.mc_get_rng(self._p))

    def sprites(self) -> np.ndarray:
        """The sprite list, (n, len(SPRITE_FIELDS)) int32 in the engine's list order."""
        n = int(self._L.mc_get_sprites(self._p, None, 0))
        if n < 0:
            raise RuntimeError("sprite with a non-empty name in the engine's list")
        out = np.zeros((n, len(SPRITE_FIELDS)), dtype=np.int32)
        if n:
            self._L.mc_get_sprites(self._p, out.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)), n)
        return out

    def hash_full(self) -> int:
        return int(self._L.mc_hash_full(self._p))

    def hash_dynamic(self) -> int:
        """Hash of every field the monthly update can read (mc_hash_full without the graph histories past
        index 1, totalPopLast, cityTaxAverage, cityYes and cityClass, plus the carried members mc_hash_full
        leaves out; see engine/c_api.cpp)."""
        return int(self._L.mc_hash_dynamic(self._p))

    # -- test only ---------------------------------------------------------------------------
    # _test_aux and _test_restore exist only to prove that the extended observation (Obs with ledger,
    # terrain, com_rate) plus the generator state, and optionally the sprite list, determine the next
    # month: code/tests/test_observation_sufficient.py and code/scripts/check_sufficiency.py. They are
    # never called by dc.oracle, the data generator or any experiment (a test greps the tree). A
    # replay starts only from load_start (REBUILD_SPEC.md, ground rule 3).
    def _test_aux(self) -> np.ndarray:
        """TEST ONLY. Members mc_hash_full hashes that the monthly update never reads."""
        out = np.zeros((int(self._L.mc_aux_len()),), dtype=np.int64)
        self._L.mc_test_get_aux(self._p, out.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)))
        return out

    def _test_restore(self, obs: Obs, rng_state: int, sprites: Optional[np.ndarray] = None, *,
                      aux: Optional[np.ndarray] = None, ledger_mask: int = LEDGER_ALL, map_mask: int = 7) -> None:
        """TEST ONLY. Full reset of this instance, then set it from an extended observation.

        ``obs`` must carry ``ledger``, ``terrain`` and ``com_rate`` (as ``observe`` returns them).
        ``sprites``: rows from ``sprites()``, or None for an empty sprite list. ``aux``: from
        ``_test_aux()``, or None. ``ledger_mask``: bit i restores ledger entry i (a cleared bit leaves
        the reset value). ``map_mask``: bit 0 terrain map, bit 1 com_rate map, bit 2 members derived
        from the observation (cityPop, crime / pollution / land-value averages, speedCycle).
        """
        if obs.ledger is None or obs.terrain is None or obs.com_rate is None:
            raise ValueError("observation without ledger / carried maps")

        def c(a, dt, shape):
            a = np.ascontiguousarray(a, dtype=dt)
            if a.shape != shape:
                raise ValueError(f"shape {a.shape} != {shape}")
            return a

        tiles = c(obs.tiles, np.uint16, (WORLD_W, WORLD_H))
        half = c(obs.half, np.uint8, (5, WORLD_W_2, WORLD_H_2))
        power = c(obs.power, np.uint8, (WORLD_W, WORLD_H))
        eighth = c(obs.eighth, np.int16, (3, WORLD_W_8, WORLD_H_8))
        scal = c(obs.scalars, np.int64, (NUM_SCALARS,))
        led = c(obs.ledger, np.int64, (NUM_LEDGER,))
        terr = c(obs.terrain, np.uint8, TERRAIN_SHAPE)
        com = c(obs.com_rate, np.int16, COM_RATE_SHAPE)
        P = ctypes.POINTER
        if sprites is not None and len(sprites):
            spr = c(sprites, np.int32, (len(sprites), len(SPRITE_FIELDS)))
            sp_ptr, ns = spr.ctypes.data_as(P(ctypes.c_int32)), len(spr)
        else:
            spr, sp_ptr, ns = None, None, 0
        if aux is not None:
            aux = c(aux, np.int64, (int(self._L.mc_aux_len()),))
            aux_ptr = aux.ctypes.data_as(P(ctypes.c_int64))
        else:
            aux_ptr = None
        self._L.mc_test_restore(
            self._p, tiles.ctypes.data_as(P(ctypes.c_uint16)), half.ctypes.data_as(P(ctypes.c_uint8)),
            power.ctypes.data_as(P(ctypes.c_uint8)), eighth.ctypes.data_as(P(ctypes.c_int16)),
            scal.ctypes.data_as(P(ctypes.c_int64)), led.ctypes.data_as(P(ctypes.c_int64)),
            terr.ctypes.data_as(P(ctypes.c_uint8)), com.ctypes.data_as(P(ctypes.c_int16)),
            ctypes.c_uint64(int(rng_state) & 0xFFFFFFFFFFFFFFFF), sp_ptr, ns, aux_ptr,
            ctypes.c_uint64(int(ledger_mask)), int(map_mask), PROTO_LEVEL, PROTO_SPEED, PROTO_PASSES,
        )
