"""Behaviour mix: the policies that generate training trajectories and calibrate tasks.

Every policy looks at the current observation (``dc.engine.Obs``) and returns one grammar month
(an int16 row of 25, see ``dc.grammar``), so every behaviour plan lies in the search space.
Policies may keep internal state (a layout plan, a queue of macros) and draw from the generator
handed to them at ``reset``; the action log they produce is all a replay needs.

Policy families (``BEHAVIOUR_MIX`` gives the trajectory-level proportions):

* scripted builders (``LatticeBuilder`` with a style): a road (or rail) lattice of 10 x 7 blocks
  (two rows of three zones between horizontal roads, a vertical road every ten columns), grown block
  by block. Plants, stadium, seaport and airport sit in blocks of their own. Every block is wired to
  its built neighbours by single wire tiles laid across the shared road (roads do not conduct, zones
  and wires do). Zone types follow the demand valves and a style-specific mix; plants are added
  before demand nears capacity (coal 700, nuclear 2,000 tile visits of the engine's power scan,
  about 1.6 visits per conductive tile on this lattice) and when the builder's own blocks brown out;
  nothing is queued that the treasury cannot pay for. When the built-up area has no free
  neighbouring block left, a new cluster with its own plant starts on the largest free patch.
  Styles (``BUILDER_STYLES``): grid, corridor, satellite, industry, frugal, boom, transit.
* random editors: uniform random grammar months; zone sprinkling next to existing roads.
* no-op months and budget sweeps (tax and funding changes, nothing built).
* perturbations, mixed into any trajectory (``Perturbed``): cut a wire or road segment, remove a
  plant, a tax shock for k months, a funding cut for k months, a forced disaster of each kind.

``rollout_behaviour`` plays a policy in the engine month by month in exactly the order of
``dc.oracle.replay`` and returns the action log; replaying that log with the same seed reproduces
the trajectory (tested).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .engine import (
    CONDBIT, LOMASK, NUM_SCALARS, SC_COM_POP, SC_COM_VALVE, SC_FUNDS, SC_IND_POP, SC_IND_VALVE, SC_RES_POP,
    SC_RES_VALVE, SC_TAX, WORLD_H, WORLD_W, ZONEBIT, Engine, Obs,
)
from .grammar import (
    BUDGET_LEVELS, COL_HIGH, COL_LOW, LINE_MAX, M, MACRO_KINDS, N_COLS, NOOP_ROW, Macro, clip_plan, compile_month,
    nominal_cost,
)
from .oracle import Replay

K = MACRO_KINDS

# ----------------------------------------------------------------------------------------------
# Tile classes (engine tile indices, low 10 bits)
# ----------------------------------------------------------------------------------------------
T_RIVER_EDGE_LO, T_RUBBLE_HI = 5, 47        # 5..47: river edges, trees, rubble (auto-bulldozed)
T_ROAD_LO, T_ROAD_HI = 64, 206              # roads, bridges, crossings, traffic animations
T_WIRE_LO, T_WIRE_HI = 208, 222             # power lines incl. rail/power crossings
T_RAIL_LO, T_RAIL_HI = 224, 238
T_FREEZ, T_COMCLR, T_INDCLR = 244, 427, 616  # empty zone centres
T_RES_LO, T_RES_HI = 240, 422               # residential incl. hospital, church
T_COM_LO, T_COM_HI = 423, 611
T_IND_LO, T_IND_HI = 612, 692
T_PORT_LO, T_PORT_HI = 693, 708
T_AIRPORT_LO, T_AIRPORT_HI = 709, 744
T_COAL_LO, T_COAL_HI = 745, 760
T_STADIUM_LO, T_STADIUM_HI = 779, 810
T_NUCLEAR_LO, T_NUCLEAR_HI = 811, 826
T_FULLSTADIUM_LO, T_FULLSTADIUM_HI = 784, 799


def tile_index(obs: Obs) -> np.ndarray:
    return (obs.tiles & LOMASK).astype(np.int32)


def buildable_mask(idx: np.ndarray) -> np.ndarray:
    """Clear land or land the engine auto-bulldozes (trees, river edges, rubble)."""
    return (idx == 0) | ((idx >= T_RIVER_EDGE_LO) & (idx <= T_RUBBLE_HI))


def road_mask(idx: np.ndarray) -> np.ndarray:
    return (idx >= T_ROAD_LO) & (idx <= T_ROAD_HI)


def empty_zone_counts(idx: np.ndarray) -> np.ndarray:
    """Zones with nobody in them, by type (R, C, I): empty commercial or industrial centres, and
    residential centres (FREEZ) whose eight surrounding tiles are still empty-zone tiles."""
    r = 0
    pts = np.argwhere(idx == T_FREEZ)
    if len(pts):
        pts = pts[(pts[:, 0] > 0) & (pts[:, 0] < WORLD_W - 1) & (pts[:, 1] > 0) & (pts[:, 1] < WORLD_H - 1)]
        ok = np.ones(len(pts), dtype=bool)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                v = idx[pts[:, 0] + dx, pts[:, 1] + dy]
                ok &= (v >= 240) & (v <= 248)
        r = int(ok.sum())
    return np.array([r, int((idx == T_COMCLR).sum()), int((idx == T_INDCLR).sum())], dtype=np.int64)


def empty_zone_count(idx: np.ndarray) -> int:
    return int(empty_zone_counts(idx).sum())


def _sat(mask: np.ndarray) -> np.ndarray:
    """Summed-area table with a zero border: S[x, y] = sum(mask[:x, :y])."""
    s = np.zeros((mask.shape[0] + 1, mask.shape[1] + 1), dtype=np.int32)
    s[1:, 1:] = mask.astype(np.int32).cumsum(0).cumsum(1)
    return s


def _rect_sum(S: np.ndarray, x0, y0, x1, y1):
    """Sum over [x0, x1) x [y0, y1) (vectorised over array arguments)."""
    return S[x1, y1] - S[x0, y1] - S[x1, y0] + S[x0, y0]


def _runs(mask_line: np.ndarray) -> List[Tuple[int, int]]:
    """(start, length) of runs of True in a 1-D boolean array."""
    out = []
    n = len(mask_line)
    i = 0
    while i < n:
        if mask_line[i]:
            j = i
            while j < n and mask_line[j]:
                j += 1
            out.append((i, j - i))
            i = j
        else:
            i += 1
    return out


def _row(tax: int, road: int, fire: int, police: int, macros: Sequence[Macro] = (), disaster: int = 0) -> np.ndarray:
    r = np.zeros((N_COLS,), dtype=np.int16)
    r[0] = tax
    r[1], r[2], r[3] = road // 25, fire // 25, police // 25
    r[4] = disaster
    for i, mc in enumerate(list(macros)[:M]):
        r[5 + 5 * i: 10 + 5 * i] = tuple(mc)
    return clip_plan(r)


def _macro_cost(mc: Macro) -> int:
    r = NOOP_ROW.copy()
    r[5:10] = tuple(mc)
    return nominal_cost(r)


# ----------------------------------------------------------------------------------------------
# Policy interface
# ----------------------------------------------------------------------------------------------
class Policy:
    """A behaviour policy. ``reset`` once per trajectory, then ``act`` once per month."""

    label = "policy"

    def reset(self, obs: Obs, rng: np.random.Generator) -> None:
        self.rng = rng

    def act(self, obs: Obs, t: int) -> np.ndarray:  # pragma: no cover - interface
        raise NotImplementedError


class NoopPolicy(Policy):
    """No-op months: the tax observed at the start, full funding, nothing built."""

    label = "noop"

    def reset(self, obs, rng):
        super().reset(obs, rng)
        self.tax = int(np.clip(obs.scalars[SC_TAX], 0, 20))

    def act(self, obs, t):
        return _row(self.tax, 100, 100, 100)


class BudgetSweep(Policy):
    """Tax and funding change over the trajectory, nothing is built.

    The trajectory is cut into segments of 3 to 12 months; each segment holds a tax drawn from
    0..20 (a random walk around the start tax half of the time) and road, fire and police levels.
    """

    label = "budget_sweep"

    def reset(self, obs, rng):
        super().reset(obs, rng)
        self.tax = int(np.clip(obs.scalars[SC_TAX], 0, 20))
        self.left = 0
        self.cur = (self.tax, 100, 100, 100)

    def act(self, obs, t):
        rng = self.rng
        if self.left <= 0:
            self.left = int(rng.integers(3, 13))
            if rng.random() < 0.5:
                tax = int(rng.integers(0, 21))
            else:
                tax = int(np.clip(self.cur[0] + rng.integers(-4, 5), 0, 20))
            lv = [int(rng.choice(BUDGET_LEVELS, p=[0.1, 0.1, 0.15, 0.15, 0.5])) for _ in range(3)]
            self.cur = (tax, *lv)
        self.left -= 1
        return _row(*self.cur)


class UniformRandom(Policy):
    """Uniform random grammar months: every macro column uniform over its range.

    Each month is a uniform random row with probability ``p_month`` (else a no-op month at the
    current tax); the disaster column is zero (forced disasters come from perturbations).
    Tax and funding are redrawn uniformly with probability ``p_budget`` a month.
    """

    label = "random/uniform"

    def __init__(self, p_month: float = 0.6, p_budget: float = 0.15):
        self.p_month, self.p_budget = p_month, p_budget

    def reset(self, obs, rng):
        super().reset(obs, rng)
        self.budget = np.array([int(np.clip(obs.scalars[SC_TAX], 0, 20)), 4, 4, 4], dtype=np.int64)

    def act(self, obs, t):
        rng = self.rng
        if rng.random() < self.p_budget:
            self.budget = rng.integers(COL_LOW[:4], COL_HIGH[:4] + 1)
        r = NOOP_ROW.astype(np.int64).copy()
        if rng.random() < self.p_month:
            r = rng.integers(COL_LOW, COL_HIGH + 1)
        r[:4] = self.budget
        r[4] = 0
        return clip_plan(r)


class ZoneSprinkler(Policy):
    """Zones dropped next to existing roads, with short road spurs and wires.

    Each month 0..4 macros: a zone (type weighted by the demand valves) centred two tiles from a
    random road tile, perpendicular to it; sometimes a short road spur or a wire run from a powered
    tile towards an unpowered zone.
    """

    label = "random/sprinkle"

    def reset(self, obs, rng):
        super().reset(obs, rng)
        self.tax = int(np.clip(obs.scalars[SC_TAX], 0, 20))

    def act(self, obs, t):
        rng = self.rng
        idx = tile_index(obs)
        roads = np.argwhere(road_mask(idx))
        free = buildable_mask(idx)
        n = int(rng.integers(0, M + 1))
        macs: List[Macro] = []
        sc = obs.scalars
        v = np.array([sc[SC_RES_VALVE], sc[SC_COM_VALVE], sc[SC_IND_VALVE]], dtype=np.float64)
        w = np.maximum(v, 0) + 300.0
        w /= w.sum()
        for _ in range(n):
            u = rng.random()
            if len(roads) == 0 or u < 0.1:
                kind = int(rng.choice([K["ROAD_H"], K["ROAD_V"]]))
                macs.append(Macro(kind, int(rng.integers(0, WORLD_W)), int(rng.integers(0, WORLD_H)), int(rng.integers(3, 15)), 0))
                continue
            if u < 0.8:
                # up to 20 tries for a road tile with clear land for a 3x3 zone two tiles off it
                kind = int(rng.choice([K["ZONE_R"], K["ZONE_C"], K["ZONE_I"]], p=w))
                for _try in range(20):
                    rx, ry = roads[int(rng.integers(len(roads)))]
                    dx, dy = [(0, -2), (0, 2), (-2, 0), (2, 0)][int(rng.integers(4))]
                    zx, zy = int(rx + dx), int(ry + dy)
                    if 1 <= zx < WORLD_W - 1 and 1 <= zy < WORLD_H - 1 and free[zx - 1:zx + 2, zy - 1:zy + 2].all():
                        macs.append(Macro(kind, zx, zy, 1, 1))
                        break
                continue
            rx, ry = roads[int(rng.integers(len(roads)))]
            if u < 0.9:
                kind = int(rng.choice([K["ROAD_H"], K["ROAD_V"]]))
                macs.append(Macro(kind, int(rx), int(ry), int(rng.integers(2, 10)), 0))
            else:
                kind = int(rng.choice([K["WIRE_H"], K["WIRE_V"]]))
                macs.append(Macro(kind, int(rx), int(ry), int(rng.integers(2, 8)), 0))
        return _row(self.tax, 100, 100, 100, macs)


# ----------------------------------------------------------------------------------------------
# Scripted builders
# ----------------------------------------------------------------------------------------------
PX, PY = 10, 7          # block pitch: zone area 9 x 6 plus one road column and one road row
SLOTS = [(s, r) for r in range(2) for s in range(3)]   # zone slots of a block: centre (bx+2+3s, by+2+3r)

B_FREE, B_ZONE, B_SPECIAL, B_AIRPORT = 0, 1, 2, 3
ZT = "RCI"
MAX_CLUSTERS = 6
# The engine's power scan charges plant capacity once per tile visit, and tiles where the flood fill
# branches are visited again when popped from its stack. On this lattice a fully wired 300-zone city
# browned out at 2,535 powered of 2,869 conductive tiles with 4,000 nominal capacity: 1.58 visits a
# tile. Builders plan capacity with this factor.
POWER_VISIT_FACTOR = 1.6
BROWNOUT_SHARE = 0.15             # unpowered share of a cluster's conductive tiles that calls for a plant
BROWNOUT_COOLDOWN = 6             # months between brown-out plants of one cluster


@dataclass(frozen=True)
class BuilderStyle:
    name: str
    order: str = "compact"            # compact | corridor | satellite
    mix: Tuple[float, float, float] = (0.55, 0.30, 0.15)   # target shares of R, C, I zones
    valve_weight: float = 1.0         # how strongly the demand valves steer the zone type
    tax: int = 7
    reserve_frac: float = 0.0         # keep this fraction of the treasury
    reserve_abs: int = 0              # and at least this much
    macros_per_month: int = 4
    empty_slack: int = 6              # build a block of a type while it has fewer empty zones than this
    plant: str = "nuclear"            # coal | nuclear | mixed (coal first, then nuclear)
    plant_headroom: float = 0.75      # add a plant when demand exceeds this share of capacity
    transport: str = "road"           # road | rail | mixed (rail in the residential sector)
    sectors: bool = True              # industry (and polluting buildings) on one side of the city
    police_every: int = 24            # one police station per this many zones (0: none)
    fire_every: int = 30              # one fire station per this many zones (0: none)
    park_prob: float = 0.0            # chance a residential block gets a park slot
    clusters: int = 1                 # satellite: number of separately wired clusters
    services_first: bool = False      # stadium, seaport and airport as soon as affordable


BUILDER_STYLES: Dict[str, BuilderStyle] = {
    "grid": BuilderStyle("grid", park_prob=0.15),
    "corridor": BuilderStyle("corridor", order="corridor", plant="mixed", sectors=False),
    "satellite": BuilderStyle("satellite", order="satellite", clusters=3, plant="coal", sectors=False),
    "industry": BuilderStyle("industry", mix=(0.40, 0.15, 0.45), valve_weight=0.5, plant="coal",
                             police_every=30, fire_every=20),
    "frugal": BuilderStyle("frugal", tax=8, reserve_frac=0.4, reserve_abs=3000, macros_per_month=2, empty_slack=3,
                           plant="coal", police_every=40, fire_every=60),
    "boom": BuilderStyle("boom", tax=6, empty_slack=14, plant_headroom=0.6, transport="mixed",
                         police_every=18, fire_every=24, park_prob=0.1, services_first=True),
    "transit": BuilderStyle("transit", transport="rail", empty_slack=10, park_prob=0.1, services_first=True),
}


def transport_mask(idx: np.ndarray) -> np.ndarray:
    """Tiles a zone accepts as its perimeter road: roads, rails and their crossings."""
    return ((idx >= T_ROAD_LO) & (idx <= T_ROAD_HI)) | ((idx >= 222) & (idx <= T_RAIL_HI))


class LatticeBuilder(Policy):
    """Scripted city builder on a 10 x 7 lattice of blocks (see the module docstring).

    A block is a ring of road (or rail) around a 9 x 6 zone area: two rows of three 3 x 3 zones.
    Blocks are claimed from a frontier around the blocks already built, in the order set by the
    style. A block holds zones of one main type, or up to two 4 x 4 buildings (plants, stadium,
    seaport), or an airport. With ``sectors`` on, industry, coal plants, the seaport and the airport
    go on one side of the first block and housing on the other (pollution above 128 stops housing
    from growing, and pollution lowers land value, which housing needs).
    """

    def __init__(self, style: BuilderStyle):
        self.style = style
        self.label = f"builder/{style.name}"

    # -- setup ---------------------------------------------------------------------------------
    def reset(self, obs: Obs, rng: np.random.Generator) -> None:
        super().reset(obs, rng)
        st = self.style
        idx = tile_index(obs)
        free = buildable_mask(idx)
        roadok = free | transport_mask(idx)
        Sf, Sr = _sat(free), _sat(roadok)
        # lattice offset: one of the three with the most usable blocks
        best = []
        for ox in range(PX):
            for oy in range(PY):
                n = int(self._usable(Sf, Sr, ox, oy)[2].sum())
                best.append((n, rng.random(), ox, oy))
        best.sort(reverse=True)
        top = best[:3]
        _, _, self.ox, self.oy = top[int(rng.integers(len(top)))]
        self.ni, self.nj, usable, slots = self._usable(Sf, Sr, self.ox, self.oy, want_slots=True)
        self.usable = usable                      # (ni, nj) bool
        self.slot_free = slots                    # (ni, nj, 6) bool
        self.state = np.zeros((self.ni, self.nj), dtype=np.int8)
        self.special_fill = np.zeros((self.ni, self.nj), dtype=np.int8)   # 4x4 slots used in a special block
        self.cluster = -np.ones((self.ni, self.nj), dtype=np.int16)
        self.queue: List[Macro] = []
        self.n_zone = np.zeros(3, dtype=np.int64)      # R, C, I zones placed by us
        self.n_police = self.n_fire = 0
        self.have_stadium = self._count(idx, T_STADIUM_LO, T_STADIUM_HI) > 0
        self.have_seaport = self._count(idx, T_PORT_LO, T_PORT_HI) > 0
        self.have_airport = self._count(idx, T_AIRPORT_LO, T_AIRPORT_HI) > 0
        self.tax = int(np.clip(st.tax + rng.integers(-1, 2), 0, 20))
        self.roots = self._choose_roots(obs, idx)
        for c, (i, j) in enumerate(self.roots):
            self.cluster[i, j] = c
        nc = len(self.roots)
        self.cluster_plants = [0] * nc
        self.cluster_tiles = [0] * nc
        self.cluster_cap = [0] * nc
        self.corridor_axis = int(rng.integers(2))
        self.next_cluster = 0
        ang = rng.uniform(0, 2 * np.pi)
        self.u = np.array([np.cos(ang), np.sin(ang)])   # direction of the industrial sector
        self.block_types: Dict[Tuple[int, int], str] = {}
        self.t = 0
        self.last_plant_t = [-10 ** 6] * nc

    def _usable(self, Sf, Sr, ox, oy, want_slots=False):
        ni = (WORLD_W - 1 - ox) // PX
        nj = (WORLD_H - 1 - oy) // PY
        ii, jj = np.meshgrid(np.arange(ni), np.arange(nj), indexing="ij")
        bx, by = ox + PX * ii, oy + PY * jj
        ring = (_rect_sum(Sr, bx, by, bx + PX + 1, by + 1) == PX + 1) \
            & (_rect_sum(Sr, bx, by + PY, bx + PX + 1, by + PY + 1) == PX + 1) \
            & (_rect_sum(Sr, bx, by, bx + 1, by + PY + 1) == PY + 1) \
            & (_rect_sum(Sr, bx + PX, by, bx + PX + 1, by + PY + 1) == PY + 1)
        slots = np.zeros((ni, nj, 6), dtype=bool)
        for k, (s, r) in enumerate(SLOTS):
            x0, y0 = bx + 1 + 3 * s, by + 1 + 3 * r
            slots[..., k] = _rect_sum(Sf, x0, y0, x0 + 3, y0 + 3) == 9
        usable = ring & (slots.sum(-1) >= 4)
        if want_slots:
            return ni, nj, usable, slots
        return ni, nj, usable

    @staticmethod
    def _count(idx, lo, hi) -> int:
        return int(((idx >= lo) & (idx <= hi)).sum())

    def _block_xy(self, i, j):
        return self.ox + PX * i, self.oy + PY * j

    def _choose_roots(self, obs: Obs, idx: np.ndarray) -> List[Tuple[int, int]]:
        st, rng = self.style, self.rng
        cand = np.argwhere(self.usable)
        if len(cand) == 0:
            return []
        u = self.usable.astype(np.int32)
        room = np.zeros_like(u)
        for di in range(-2, 3):
            for dj in range(-2, 3):
                sh = np.zeros_like(u)
                xs = slice(max(0, di), u.shape[0] + min(0, di))
                xd = slice(max(0, -di), u.shape[0] + min(0, -di))
                ys = slice(max(0, dj), u.shape[1] + min(0, dj))
                yd = slice(max(0, -dj), u.shape[1] + min(0, -dj))
                sh[xd, yd] = u[xs, ys]
                room += sh
        zone_pts = np.argwhere((obs.tiles & ZONEBIT) != 0)
        if len(zone_pts) > 0:
            cx, cy = zone_pts.mean(0)            # existing city: start next to its development
        else:
            cx = WORLD_W / 2 + rng.normal(0, 12)
            cy = WORLD_H / 2 + rng.normal(0, 10)
        bxy = np.stack([self.ox + PX * cand[:, 0] + PX / 2, self.oy + PY * cand[:, 1] + PY / 2], 1)
        d = np.hypot(bxy[:, 0] - cx, bxy[:, 1] - cy)
        score = d - 4.0 * room[cand[:, 0], cand[:, 1]] + rng.normal(0, 3, len(cand))
        roots = [tuple(int(v) for v in cand[int(np.argmin(score))])]
        for _ in range(1, st.clusters):
            dmin = np.min([np.hypot((cand[:, 0] - r[0]) * PX, (cand[:, 1] - r[1]) * PY) for r in roots], axis=0)
            sc = dmin + 2.0 * room[cand[:, 0], cand[:, 1]] + rng.normal(0, 3, len(cand))
            sc[dmin < 25] = -1e9
            k = int(np.argmax(sc))
            if sc[k] < -1e8:
                break
            roots.append(tuple(int(v) for v in cand[k]))
        return roots

    # -- per month -------------------------------------------------------------------------------
    def act(self, obs: Obs, t: int) -> np.ndarray:
        st = self.style
        self.t = t
        funds = int(obs.scalars[SC_FUNDS])
        if not self.queue:
            self._plan(obs)
        reserve = max(st.reserve_abs, int(st.reserve_frac * funds))
        budget = funds - reserve
        out: List[Macro] = []
        spent = 0
        while self.queue and len(out) < st.macros_per_month:
            mc = self.queue[0]
            c = _macro_cost(mc) + 20  # margin for auto-bulldozing trees
            if spent + c > budget:
                break
            out.append(self.queue.pop(0))
            spent += c
        return _row(self.tax, 100, 100, 100, out)

    # -- planning ----------------------------------------------------------------------------------
    def _plan(self, obs: Obs) -> None:
        st = self.style
        sc = obs.scalars
        funds = int(sc[SC_FUNDS])
        idx = tile_index(obs)
        if not self.roots:
            return
        # 1. power: every cluster gets a plant first, and another before demand nears capacity
        for c in range(len(self.roots)):
            built = (self.cluster == c) & (self.state != B_FREE)
            if self.cluster_plants[c] == 0 and not built.any():
                self._queue_special(obs, c, "plant")
                return
            if self.cluster_tiles[c] * POWER_VISIT_FACTOR + 60 > st.plant_headroom * self.cluster_cap[c]:
                self._queue_special(obs, c, "plant")
                return
            if self.cluster_plants[c] > 0 and self.t - self.last_plant_t[c] >= BROWNOUT_COOLDOWN \
                    and self._brownout(obs, c) > BROWNOUT_SHARE:
                self._queue_special(obs, c, "plant")
                return
        # 2. growth caps: stadium (housing), seaport (industry), airport (commerce)
        res_pop, com_pop, ind_pop = int(sc[SC_RES_POP]), int(sc[SC_COM_POP]), int(sc[SC_IND_POP])
        early = st.services_first
        if not self.have_stadium and (res_pop > 350 or (early and res_pop > 150)) and funds > 6000:
            self._queue_special(obs, 0, "stadium")
            return
        if not self.have_seaport and (ind_pop > 50 or (early and ind_pop > 20)) and funds > 4000:
            self._queue_special(obs, 0, "seaport")
            return
        if not self.have_airport and (com_pop > 70 or (early and com_pop > 30)) and funds > 11000:
            self._queue_special(obs, 0, "airport")
            return
        # 3. a zone block of the type in demand whose zones are filling up
        empty = empty_zone_counts(idx)
        valves = np.array([sc[SC_RES_VALVE] / 2000.0, sc[SC_COM_VALVE] / 1500.0, sc[SC_IND_VALVE] / 1500.0])
        n = self.n_zone.astype(np.float64)
        share = n / max(1.0, n.sum())
        need = np.asarray(st.mix) - share + st.valve_weight * 0.25 * valves + self.rng.normal(0, 0.03, 3)
        if n.sum() < 6:
            need = np.array([1.0, -1.0, 0.6])        # houses and jobs first
        for z in np.argsort(-need):
            if valves[z] < -0.5 and n.sum() >= 6:
                continue
            if empty[z] < st.empty_slack:
                if not self._queue_zone_block(obs, idx, int(z)):
                    self._spawn_cluster()
                return

    def _spawn_cluster(self) -> bool:
        """The built-up area has no free neighbouring block left: start a new cluster (with its own
        plant) in the largest remaining patch of usable blocks, nearest the existing city."""
        if len(self.roots) >= MAX_CLUSTERS:
            return False
        from scipy import ndimage
        freeb = self.usable & (self.state == B_FREE)
        lab, n = ndimage.label(freeb)
        if n == 0:
            return False
        sizes = ndimage.sum(freeb, lab, index=np.arange(1, n + 1))
        built = np.argwhere(self.state != B_FREE)
        centre = built.mean(0) if len(built) else np.array(self.roots[0], dtype=np.float64)
        best, bs = None, -1e18
        for k in range(1, n + 1):
            if sizes[k - 1] < 3:
                continue
            pts = np.argwhere(lab == k)
            d = np.hypot((pts[:, 0] - centre[0]) * PX, (pts[:, 1] - centre[1]) * PY)
            q = int(np.argmin(d))
            score = 3.0 * min(sizes[k - 1], 12) - 0.5 * d[q] + self.rng.normal(0, 2)
            if score > bs:
                best, bs = tuple(int(v) for v in pts[q]), score
        if best is None:
            return False
        self.roots.append(best)
        self.cluster[best] = len(self.roots) - 1
        self.cluster_plants.append(0)
        self.cluster_tiles.append(0)
        self.cluster_cap.append(0)
        self.last_plant_t.append(-10 ** 6)
        return True

    def _brownout(self, obs: Obs, c: int) -> float:
        """Share of the conductive tiles in this cluster's built blocks that the engine left unpowered."""
        blocks = np.argwhere((self.cluster == c) & (self.state != B_FREE))
        if len(blocks) == 0:
            return 0.0
        cond = (obs.tiles & CONDBIT) != 0
        unp = cond & (obs.power == 0)
        n_c = n_u = 0
        for i, j in blocks:
            bx, by = self._block_xy(int(i), int(j))
            n_c += int(cond[bx + 1:bx + PX, by + 1:by + PY].sum())
            n_u += int(unp[bx + 1:bx + PX, by + 1:by + PY].sum())
        return n_u / n_c if n_c else 0.0

    def _sector_score(self, i: int, j: int, c: int, want: str) -> float:
        """Lower is better: distance to the cluster root, plus a sector preference."""
        ri, rj = self.roots[c]
        v = np.array([(i - ri) * PX, (j - rj) * PY], dtype=np.float64)
        dist = abs(v[0]) + abs(v[1])
        st = self.style
        if st.order == "corridor":
            off, along = (abs(j - rj), abs(i - ri)) if self.corridor_axis == 0 else (abs(i - ri), abs(j - rj))
            dist = along * PX + 60.0 * off
        if not st.sectors:
            return dist
        proj = float(v @ self.u)
        if want in ("I", "coal", "seaport", "airport"):
            return dist - 2.0 * proj + (40.0 if proj < 8 else 0.0)
        if want == "R":
            return dist + 1.5 * max(0.0, proj + 5)
        return dist     # commerce, stadium, nuclear: anywhere near the centre

    def _frontier(self, c: int) -> List[Tuple[int, int]]:
        built = (self.state != B_FREE) & (self.cluster == c)
        if not built.any():
            i, j = self.roots[c]
            return [(i, j)] if self.state[i, j] == B_FREE and self.usable[i, j] else []
        nb = np.zeros_like(built)
        nb[1:, :] |= built[:-1, :]
        nb[:-1, :] |= built[1:, :]
        nb[:, 1:] |= built[:, :-1]
        nb[:, :-1] |= built[:, 1:]
        cand = np.argwhere(nb & ~built & (self.state == B_FREE) & self.usable)
        return [tuple(int(v) for v in p) for p in cand]

    def _next_block(self, c: int, want: str) -> Optional[Tuple[int, int]]:
        fr = self._frontier(c)
        if not fr:
            return None
        best, bs = None, 1e18
        for (i, j) in fr:
            s = self._sector_score(i, j, c, want) + self.rng.random() * 3.0
            if s < bs:
                best, bs = (i, j), s
        return best

    def _find_block(self, c: int, want: str) -> Tuple[Optional[Tuple[int, int]], int]:
        blk = self._next_block(c, want)
        if blk is None:
            for c2 in range(len(self.roots)):
                blk = self._next_block(c2, want)
                if blk is not None:
                    return blk, c2
        return blk, c

    def _use_rail(self, want: str) -> bool:
        tr = self.style.transport
        return tr == "rail" or (tr == "mixed" and want == "R")

    def _line_runs(self, idx: np.ndarray, x0: int, y0: int, n: int, horizontal: bool, rail: bool) -> List[Macro]:
        line = idx[x0:x0 + n, y0] if horizontal else idx[x0, y0:y0 + n]
        need = ~transport_mask(line) & ~((line >= T_WIRE_LO) & (line <= 221))
        kind = K[("RAIL_" if rail else "ROAD_") + ("H" if horizontal else "V")]
        out = []
        for s, ln in _runs(need):
            while ln > 0:
                k = min(ln, LINE_MAX)
                out.append(Macro(kind, x0 + s, y0, k, 0) if horizontal else Macro(kind, x0, y0 + s, k, 0))
                s += k
                ln -= k
        return out

    def _ring(self, idx: np.ndarray, i: int, j: int, rail: bool) -> List[Macro]:
        bx, by = self._block_xy(i, j)
        m = []
        m += self._line_runs(idx, bx, by, PX + 1, True, rail)
        m += self._line_runs(idx, bx, by + PY, PX + 1, True, rail)
        m += self._line_runs(idx, bx, by + 1, PY - 1, False, rail)
        m += self._line_runs(idx, bx + PX, by + 1, PY - 1, False, rail)
        return m

    def _crossings(self, i: int, j: int) -> List[Macro]:
        """Single wire tiles across the shared road to every built neighbour of the same cluster."""
        bx, by = self._block_xy(i, j)
        m = []
        for di, dj, x, y in ((0, -1, bx + 5, by), (0, 1, bx + 5, by + PY), (-1, 0, bx, by + 5), (1, 0, bx + PX, by + 5)):
            ii, jj = i + di, j + dj
            if 0 <= ii < self.ni and 0 <= jj < self.nj and self.state[ii, jj] != B_FREE \
                    and self.cluster[ii, jj] == self.cluster[i, j]:
                m.append(Macro(K["WIRE_H"], x, y, 1, 0))
        return m

    def _claim(self, i, j, c, state):
        self.state[i, j] = state
        self.cluster[i, j] = c

    def _plant_kind(self, c: int) -> str:
        p = self.style.plant
        if p == "mixed":
            return "nuclear" if self.cluster_plants[c] >= 1 else "coal"
        return p

    def _queue_special(self, obs: Obs, c: int, what: str) -> None:
        idx = tile_index(obs)
        want = self._plant_kind(c) if what == "plant" else what
        if what != "airport":
            cand = np.argwhere((self.state == B_SPECIAL) & (self.cluster == c) & (self.special_fill < 2))
            if len(cand):
                i, j = (int(v) for v in cand[0])
                self._fill_special(i, j, c, what)
                return
        blk, c = self._find_block(c, want)
        if blk is None:
            return
        i, j = blk
        bx, by = self._block_xy(i, j)
        self._claim(i, j, c, B_AIRPORT if what == "airport" else B_SPECIAL)
        self.queue += self._ring(idx, i, j, rail=False)
        if what == "airport":
            self.queue.append(Macro(K["AIRPORT"], bx + 2, by + 2, 0, 0))
            self.queue.append(Macro(K["WIRE_H"], bx + 7, by + 5, 3, 0))
            self.have_airport = True
            self._add_tiles(c, 36 + 3)
        else:
            self.queue.append(Macro(K["WIRE_H"], bx + 1, by + 5, 9, 0))
            self.queue.append(Macro(K["WIRE_H"], bx + 5, by + 6, 1, 0))
            self._add_tiles(c, 10)
            self._fill_special(i, j, c, what)
        cr = self._crossings(i, j)
        self.queue += cr
        self._add_tiles(c, len(cr))

    def _fill_special(self, i, j, c, what):
        bx, by = self._block_xy(i, j)
        x = bx + 6 if self.special_fill[i, j] == 0 else bx + 2   # first building next to the wire column
        if what == "plant":
            nuc = self._plant_kind(c) == "nuclear"
            self.queue.append(Macro(K["NUCLEAR"] if nuc else K["COAL"], x, by + 2, 0, 0))
            self.cluster_plants[c] += 1
            self.cluster_cap[c] += 2000 if nuc else 700
            self.last_plant_t[c] = self.t
        elif what == "stadium":
            self.queue.append(Macro(K["STADIUM"], x, by + 2, 0, 0))
            self.have_stadium = True
        elif what == "seaport":
            self.queue.append(Macro(K["SEAPORT"], x, by + 2, 0, 0))
            self.have_seaport = True
        self.special_fill[i, j] += 1
        self._add_tiles(c, 16)

    def _add_tiles(self, c, n):
        self.cluster_tiles[c] += n

    def _queue_zone_block(self, obs: Obs, idx: np.ndarray, z: int) -> None:
        st, rng = self.style, self.rng
        c = 0
        if st.order == "satellite":
            c = self.next_cluster % len(self.roots)
            self.next_cluster += 1
        want = ZT[z]
        blk, c = self._find_block(c, want)
        if blk is None:
            return False
        i, j = blk
        bx, by = self._block_xy(i, j)
        self._claim(i, j, c, B_ZONE)
        free = self.slot_free[i, j].copy()
        bfree = buildable_mask(idx)
        for k, (s, r) in enumerate(SLOTS):
            x0, y0 = bx + 1 + 3 * s, by + 1 + 3 * r
            free[k] = bool(bfree[x0:x0 + 3, y0:y0 + 3].all())
        types = self._slot_types(want, free)
        macros = self._ring(idx, i, j, rail=self._use_rail(want))
        for r in range(2):
            s = 0
            while s < 3:
                tk = types[r * 3 + s]
                if tk is None:
                    s += 1
                    continue
                e = s
                while e + 1 < 3 and types[r * 3 + e + 1] == tk and tk in ZT:
                    e += 1
                x, y = bx + 2 + 3 * s, by + 2 + 3 * r
                if tk in ZT:
                    macros.append(Macro(K["ZONE_" + tk], x, y, e - s + 1, 1))
                elif tk == "P":
                    macros.append(Macro(K["POLICE"], x, y, 0, 0))
                elif tk == "F":
                    macros.append(Macro(K["FIRE"], x, y, 0, 0))
                elif tk == "K":
                    macros.append(Macro(K["PARK"], x - 1, y - 1, 3, 3))
                s = e + 1
        n_cond = sum(1 for tk in types if tk is not None and tk != "K")
        cr = self._crossings(i, j)
        macros += cr
        self._add_tiles(c, 9 * n_cond + len(cr))
        self.block_types[(i, j)] = want
        self.queue += macros
        return True

    def _slot_types(self, want: str, free: np.ndarray) -> List[Optional[str]]:
        st, rng = self.style, self.rng
        types: List[Optional[str]] = [None] * 6
        nz_total = int(self.n_zone.sum())
        service = None
        if st.police_every and (nz_total + 6) // st.police_every > self.n_police:
            service = "P"
        elif st.fire_every and (nz_total + 6) // st.fire_every > self.n_fire:
            service = "F"
        park = want == "R" and rng.random() < st.park_prob
        # a commercial row in some housing blocks (commerce does not pollute and raises density)
        mixed_row = want == "R" and rng.random() < 0.25
        for k in range(6):
            if not free[k]:
                continue
            s, r = SLOTS[k]
            if service is not None and s == 1:
                types[k] = service
                if service == "P":
                    self.n_police += 1
                else:
                    self.n_fire += 1
                service = None
                continue
            if park and r == 0 and s in (0, 2):
                types[k] = "K"
                park = False
                continue
            tk = "C" if (mixed_row and r == 1) else want
            types[k] = tk
            self.n_zone[ZT.index(tk)] += 1
        return types


# ----------------------------------------------------------------------------------------------
# Perturbations
# ----------------------------------------------------------------------------------------------
PERTURBATIONS = ("cut_wire", "cut_road", "remove_plant", "tax_shock", "funding_cut", "disaster")


class Perturbed(Policy):
    """Wraps any policy and mixes perturbation events into its months.

    1 to 3 events per 24 months, at random months, each one of ``PERTURBATIONS``:
    cut a wire or road segment (bulldozer on 1 to 4 tiles of a run), remove a power plant (bulldozer
    on its centre tile), a tax shock (tax 0..3 or 15..20 for 2..8 months), a funding cut (road, fire or
    police at 0 or 25 per cent for 3..12 months), or a forced disaster (kind 1..6). Event macros take
    the last macro slots of the month.
    """

    def __init__(self, base: Policy, rate_per_24: Tuple[int, int] = (1, 3)):
        self.base = base
        self.rate = rate_per_24
        self.label = base.label + "+perturb"

    def reset(self, obs, rng):
        super().reset(obs, rng)
        self.base.reset(obs, rng)
        self.events: Dict[int, str] = {}
        self.tax_override: Dict[int, int] = {}
        self.fund_override: Dict[int, Tuple[int, int]] = {}
        self.horizon_hint = 0

    def _schedule(self, t0: int) -> None:
        rng = self.rng
        n = int(rng.integers(self.rate[0], self.rate[1] + 1))
        for _ in range(n):
            t = t0 + int(rng.integers(0, 24))
            kind = PERTURBATIONS[int(rng.integers(len(PERTURBATIONS)))]
            self.events[t] = kind
            if kind == "tax_shock":
                tax = int(rng.integers(0, 4)) if rng.random() < 0.5 else int(rng.integers(15, 21))
                for u in range(t, t + int(rng.integers(2, 9))):
                    self.tax_override[u] = tax
            elif kind == "funding_cut":
                which = int(rng.integers(1, 4))
                lv = int(rng.choice([0, 25]))
                for u in range(t, t + int(rng.integers(3, 13))):
                    self.fund_override[u] = (which, lv)

    def act(self, obs, t):
        if t % 24 == 0:
            self._schedule(t)
        row = self.base.act(obs, t).astype(np.int64)
        rng = self.rng
        ev = self.events.get(t)
        if t in self.tax_override:
            row[0] = self.tax_override[t]
        if t in self.fund_override:
            which, lv = self.fund_override[t]
            row[which] = lv // 25
        if ev in ("cut_wire", "cut_road", "remove_plant"):
            idx = tile_index(obs)
            mc = None
            if ev == "cut_wire":
                pts = np.argwhere((idx >= T_WIRE_LO) & (idx <= T_WIRE_HI))
            elif ev == "cut_road":
                pts = np.argwhere(road_mask(idx))
            else:
                pts = np.argwhere(((obs.tiles & ZONEBIT) != 0) & (((idx >= T_COAL_LO) & (idx <= T_COAL_HI))
                                                                   | ((idx >= T_NUCLEAR_LO) & (idx <= T_NUCLEAR_HI))))
            if len(pts):
                x, y = pts[int(rng.integers(len(pts)))]
                if ev == "remove_plant":
                    mc = Macro(K["BULLDOZE"], int(x), int(y), 1, 1)
                else:
                    horiz = rng.random() < 0.5
                    ln = int(rng.integers(1, 5))
                    mc = Macro(K["BULLDOZE"], int(x), int(y), ln if horiz else 1, 1 if horiz else ln)
            if mc is not None:
                row[5 + 5 * (M - 1): 5 + 5 * M] = tuple(mc)
        elif ev == "disaster":
            row[4] = int(rng.integers(1, 7))
        return clip_plan(row)


# ----------------------------------------------------------------------------------------------
# The mix
# ----------------------------------------------------------------------------------------------
def _make(label: str) -> Policy:
    if label.startswith("builder/"):
        return LatticeBuilder(BUILDER_STYLES[label.split("/", 1)[1]])
    return {"random/uniform": UniformRandom, "random/sprinkle": ZoneSprinkler, "noop": NoopPolicy,
            "budget_sweep": BudgetSweep}[label]()


# (label, share of trajectories). Each is wrapped in perturbations with probability P_PERTURB.
BEHAVIOUR_MIX: List[Tuple[str, float]] = [
    ("builder/grid", 0.12),
    ("builder/corridor", 0.07),
    ("builder/satellite", 0.07),
    ("builder/industry", 0.07),
    ("builder/frugal", 0.07),
    ("builder/boom", 0.07),
    ("builder/transit", 0.07),
    ("random/uniform", 0.10),
    ("random/sprinkle", 0.14),
    ("noop", 0.10),
    ("budget_sweep", 0.12),
]
P_PERTURB = 0.30
assert abs(sum(w for _, w in BEHAVIOUR_MIX) - 1.0) < 1e-9


def make_policy(label: str) -> Policy:
    """Policy from a label such as 'builder/grid' or 'noop+perturb'."""
    if label.endswith("+perturb"):
        return Perturbed(_make(label[: -len("+perturb")]))
    return _make(label)


def sample_behaviour(rng: np.random.Generator) -> Tuple[Policy, str]:
    labels = [l for l, _ in BEHAVIOUR_MIX]
    p = np.array([w for _, w in BEHAVIOUR_MIX], dtype=np.float64)
    label = labels[int(rng.choice(len(labels), p=p / p.sum()))]
    if rng.random() < P_PERTURB:
        label += "+perturb"
    return make_policy(label), label


# ----------------------------------------------------------------------------------------------
# The coverage mix : scripted builders under one budget setting from the whole grid
# ----------------------------------------------------------------------------------------------
class HeldBudget(Policy):
    """Wraps a policy: every month's tax and funding columns are set to one ``setting`` held for the
    whole trajectory, and the forced-disaster column is set to ``forced`` ({month: disaster kind}; none by
    default, so the column is cleared). ``setting`` is in plan-column units: (tax 0..20, road, fire,
    police levels 0..4 = 0, 25, 50, 75, 100 per cent). The wrapped policy still plays closed loop: it sees
    the engine's observation (funds, valves, power) under the held setting and after any forced event."""

    def __init__(self, base: Policy, setting: Sequence[int], forced: Optional[Dict[int, int]] = None):
        s = tuple(int(v) for v in setting)
        if len(s) != 4 or not (0 <= s[0] <= 20) or not all(0 <= v <= 4 for v in s[1:]):
            raise ValueError(f"budget setting {setting!r} outside tax 0..20, levels 0..4")
        self.base = base
        self.setting = s
        self.forced = {int(m): int(k) for m, k in (forced or {}).items()}
        if any(not (1 <= k <= 6) for k in self.forced.values()):
            raise ValueError(f"forced disaster kinds {forced!r} outside 1..6")
        self.label = base.label + "+held" + ("+forced" if self.forced else "")

    def reset(self, obs, rng):
        super().reset(obs, rng)
        self.base.reset(obs, rng)

    def act(self, obs, t):
        row = np.asarray(self.base.act(obs, t)).astype(np.int64).copy()
        row[0:4] = self.setting
        row[4] = self.forced.get(int(t), 0)
        return clip_plan(row)


COVERAGE_STYLES: Tuple[str, ...] = tuple(sorted(BUILDER_STYLES))   # the seven scripted builder styles


def sample_coverage_behaviour(rng: np.random.Generator) -> Tuple[Policy, str]:
    """The coverage mix: a scripted builder style uniform over ``COVERAGE_STYLES`` and one budget setting
    uniform over the whole grid (tax uniform on 0..20; road, fire and police each uniform on their five
    levels), held for the trajectory; no perturbations. Draw order: style, tax, road, fire, police. The
    label is ``builder/<style>+held``; the setting is in the plan's budget columns."""
    style = COVERAGE_STYLES[int(rng.integers(len(COVERAGE_STYLES)))]
    tax = int(rng.integers(0, 21))
    road, fire, police = (int(rng.integers(0, 5)) for _ in range(3))
    pol = HeldBudget(LatticeBuilder(BUILDER_STYLES[style]), (tax, road, fire, police))
    return pol, pol.label


def sample_listed_behaviour(rng: np.random.Generator, settings: Sequence[Sequence[int]],
                            forced: Optional[Dict[int, int]] = None) -> Tuple[Policy, str]:
    """The second coverage mix: a scripted builder style uniform over ``COVERAGE_STYLES`` and one budget
    setting drawn uniformly from ``settings`` (the start's own list), held for the trajectory, with the
    forced events ``forced``. Draw order: style, setting. Label ``builder/<style>+held[+forced]``."""
    if len(settings) == 0:
        raise ValueError("empty settings list")
    style = COVERAGE_STYLES[int(rng.integers(len(COVERAGE_STYLES)))]
    setting = settings[int(rng.integers(len(settings)))]
    pol = HeldBudget(LatticeBuilder(BUILDER_STYLES[style]), setting, forced)
    return pol, pol.label


# ----------------------------------------------------------------------------------------------
# Rollout
# ----------------------------------------------------------------------------------------------
def rollout_behaviour(
    eng: Engine,
    cty_path,
    policy: Policy,
    months: int,
    seed: int,
    disasters: bool,
    rng: np.random.Generator,
    *,
    record: str = "full",
    want_hash: bool = False,
) -> Tuple[np.ndarray, Replay]:
    """Play ``policy`` from ``cty_path`` for ``months`` months under ``seed``.

    Order per month is ``dc.oracle.replay``'s: budget settings and tool calls, forced disaster,
    one month, observation. Returns (plan int16 (months, 25), Replay). ``record="full"`` keeps every
    observation in ``Replay.states``.
    """
    eng.load_start(cty_path)
    eng.set_disasters(disasters)   # before the first observation: the flag is part of the ledger
    obs = eng.observe()
    obs0 = obs
    eng.seed(seed)
    policy.reset(obs, rng)
    plan = np.zeros((months, N_COLS), dtype=np.int16)
    scal = np.empty((months + 1, NUM_SCALARS), dtype=np.int64)
    scal[0] = obs.scalars
    cost = np.zeros((months,), dtype=np.int64)
    ok: List[np.ndarray] = []
    states = [obs0] if record == "full" else None
    hashes = np.empty((months + 1,), dtype=np.uint64) if want_hash else None
    if hashes is not None:
        hashes[0] = eng.hash_full()
    for t in range(months):
        row = clip_plan(policy.act(obs, t))
        plan[t] = row
        act, dis = compile_month(row)
        res, c = eng.apply(act)
        ok.append(res)
        cost[t] = c
        if dis:
            eng.force_disaster(dis)
        eng.step_month()
        obs = eng.observe()
        scal[t + 1] = obs.scalars
        if states is not None:
            states.append(obs)
        if hashes is not None:
            hashes[t + 1] = eng.hash_full()
    return plan, Replay(obs0, scal, cost, ok, states, hashes)
