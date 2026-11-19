"""The emulator ladder: a learned, stochastic one-month transition model of the engine.

Architecture (one module, three sizes ``15m``, ``50m``, ``100m``):

* Full-resolution input (120 x 100 tiles): an embedding of the 1,024 tile codes, the five flags,
  the power map and the fifteen action-raster channels, summed into ``d0`` channels.
* A patchified ConvNeXt U-Net: 2 x 2 patches to 60 x 50 (``d1``, where the five half-resolution
  overlays and the up-sampled eighth-resolution overlays enter), 30 x 25 (``d2``) and 15 x 13
  (``d3``, where the eighth-resolution overlays enter again), then back up to 60 x 50 and a
  full-resolution ConvNeXt block at 120 x 100 with a skip from the input.
* Every block is FiLM-conditioned on one vector built from the normalised scalars (symmetric log
  for the wide-range ones; statistics are a checkpointed buffer, see ``compute_norm_stats``), the
  month of the year (sin / cos plus one-hot of the 4-unit month bucket and of city_time mod 4,
  because the budget lands when city_time is a multiple of 48), the 11 action scalars and a noise
  token ``z`` of width 32.
* ``z`` is a proper latent variable: training maximises the evidence lower bound with a posterior
  ``q(z | s_t, a_t, s_t+1)`` (a small encoder of what changed) and the prior N(0, I). Without a
  posterior a likelihood-trained model ignores z and its per-tile noise is independent, which
  under-disperses whole-city outcomes over many months.

Output distribution (every term is a log-probability of the exact integer outcome, in nats):

* tile index: a change gate g per tile and, for tiles that change, a 1,024-way categorical with
  the current code masked out, so p(same) = 1 - g and p(k) = g * softmax_{k != current}. The
  categorical is evaluated only where it is needed (changed tiles in training, sampled changes in
  sampling), which keeps it a full softmax at a cost proportional to the number of changes.
* flags (5) and power map: Bernoulli logits per tile; where the tile index changes, the logits come
  from a head that sees the new code (flags are mostly a property of the code), elsewhere from a
  dense head with a learned copy term.
* half (5 x 60 x 50, 0..255) and eighth (3 x 15 x 13) overlays: per cell a point mass on "unchanged"
  mixed with a discretised logistic mixture centred on bounded residuals (edge bins at the bounds).
* scalars: 17 of the 20 are learned, each as a point mass on "no change" mixed with a discretised
  logistic mixture over the integer one-month change. Three are bookkeeping identities measured on
  the engine (0 violations in 1,536 transitions over 32 cities) and are derived, not learned:
  ``tax`` at t+1 is the action's tax, ``city_time`` advances by 4, and
  ``pop = 20 * (res_pop + 8 * (com_pop + ind_pop))`` (the C shim's definition).
* bounds: every learned quantity with a bound that is a fact of the engine (``BOUND_SOURCES``: valves,
  score, non-negative counts and treasury figures, the charged build cost, ledger flags and map
  coordinates, the overlays) has a censored likelihood: the predictive mass beyond the bound is the
  probability of the bound. Sampling rounds and pins the draw to the bound, which is exactly that
  distribution, so nothing is clipped after sampling.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from .engine import (
    NUM_SCALARS, SC_COAL, SC_COM_POP, SC_COM_VALVE, SC_FIRE_SPEND, SC_FUNDS, SC_IND_POP, SC_IND_VALVE,
    SC_NUCLEAR, SC_POLICE_SPEND, SC_POP, SC_POWERED, SC_RES_POP, SC_RES_VALVE, SC_ROAD_SPEND,
    SC_ROAD_TOTAL, SC_SCORE, SC_TAX, SC_TAX_FUND, SC_TIME, SC_UNPOWERED, SCALAR_NAMES,
    WORLD_H, WORLD_H_2, WORLD_H_8, WORLD_W, WORLD_W_2, WORLD_W_8,
    COM_RATE_SHAPE, LEDGER_NAMES, LG, NUM_LEDGER, TERRAIN_SHAPE,
)

State = Dict[str, torch.Tensor]

N_CODES = 1024
N_FLAGS = 5            # zone, bulldozable, burnable, conductive, powered (loader order)
N_TOOLS = 15           # action raster channels
N_ACT = 11             # tax/20, road/100, fire/100, police/100, one-hot(7) forced disaster kind
Z_DIM = 32
N_HALF, N_EIGHTH = 5, 3

# Scalars ------------------------------------------------------------------------------------
DERIVED_SCALARS = (SC_TAX, SC_POP, SC_TIME)
LEARNED_SCALARS = tuple(i for i in range(NUM_SCALARS) if i not in DERIVED_SCALARS)   # 17
# Absolute city time is not given to the model (month-of-year features are); everything else is.
COND_SCALARS = tuple(i for i in range(NUM_SCALARS) if i != SC_TIME)                  # 19
SYMLOG_SCALARS = (SC_FUNDS, SC_POP, SC_RES_POP, SC_COM_POP, SC_IND_POP, SC_TIME, SC_TAX_FUND,
                  SC_ROAD_SPEND, SC_FIRE_SPEND, SC_POLICE_SPEND, SC_POWERED, SC_UNPOWERED, SC_ROAD_TOTAL)
# Bounds of the engine's state space. Every bounded learned quantity has a censored likelihood: the
# predictive mass beyond a bound is the probability of the bound (edge bins of the discretised
# logistic mixture at bound - current value, see ``censor_limits``), so "sample, then clip at the
# bound" is exactly the distribution that was trained, and sampling needs no clamp afterwards. A
# bound is kept only where the engine makes it a fact; the paper's table (results/fidelity/bounds.md)
# is generated from this one by code/scripts/bounds_table.py. Paths are under engine/ (src/ for the
# simulator). Fields: kind, name, lower, upper (None = unbounded), source, caveat ("" = none).
_SHORT_WRAP = "16-bit short: would wrap only above 32,767"
BOUND_SOURCES = (
    ("scalar", "funds", 0, None,
     "totalFunds changes only in spend/setFunds (src/micropolis.cpp:1066-1081): a tool is refused when "
     "totalFunds < cost (src/tool.cpp:154, charged at :127); the budget pays at most taxFund + totalFunds, "
     "otherwise nothing and auto-budget switches off (src/budget.cpp:124-230, 268-310); setFunds is "
     "otherwise called only at load or reset",
     "spend/setFunds take a 32-bit int: holds below 2,147,483,647"),
    ("scalar", "res_valve", -2000, 2000,
     "clamp to +-RES_VALVE_RANGE (src/simulate.cpp:671; = 2000, src/micropolis.h:286)", ""),
    ("scalar", "com_valve", -1500, 1500,
     "clamp to +-COM_VALVE_RANGE (src/simulate.cpp:672; = 1500, src/micropolis.h:287)", ""),
    ("scalar", "ind_valve", -1500, 1500,
     "clamp to +-IND_VALVE_RANGE (src/simulate.cpp:673; = 1500, src/micropolis.h:288)", ""),
    ("scalar", "res_pop", 0, None,
     "zeroed by the census (src/simulate.cpp:699), then += zone population 0..40 "
     "(src/zone.cpp:556-562, 711-715)", _SHORT_WRAP + " (more than 819 fully grown residential zones)"),
    ("scalar", "com_pop", 0, None,
     "zeroed by the census (src/simulate.cpp:700), then += zone population 0..5 (src/zone.cpp:774, 866-873)", ""),
    ("scalar", "ind_pop", 0, None,
     "zeroed by the census (src/simulate.cpp:701), then += zone population 0..4 (src/zone.cpp:926, 1001-1008)", ""),
    ("scalar", "score", 0, 1000,
     "cityScore = (cityScore + clamp(z, 0, 1000)) / 2 (src/evaluate.cpp:464-466); starts at 500 "
     "(src/evaluate.cpp:155, src/initialize.cpp:94); a loaded score outside 1..999 becomes 500 "
     "(src/simulate.cpp:504-506)", ""),
    ("scalar", "tax_fund", 0, None,
     "totalPop * landValueAverage / 120 * cityTax * FLevels, all factors non-negative "
     "(src/simulate.cpp:887); 0 at src/simulate.cpp:559", ""),
    ("scalar", "road_spend", 0, None,
     "set to an allocation min(fund x percent, cash left) or to the fund (src/budget.cpp:115-230, 280-282, "
     "306-308); percents clamped to [0, 1] (c_api.cpp:139-141)", ""),
    ("scalar", "fire_spend", 0, None, "as road_spend (src/budget.cpp:280, 306)", ""),
    ("scalar", "police_spend", 0, None, "as road_spend (src/budget.cpp:281, 307)", ""),
    ("scalar", "powered_zones", 0, None,
     "zeroed by the census (src/simulate.cpp:694), ++ per powered zone (src/zone.cpp:100)", ""),
    ("scalar", "unpowered_zones", 0, None,
     "zeroed by the census (src/simulate.cpp:695), ++ per unpowered zone (src/zone.cpp:102)", ""),
    ("scalar", "coal_plants", 0, None,
     "zeroed by the census (src/simulate.cpp:710), ++ per plant (src/simulate.cpp:1462)", ""),
    ("scalar", "nuclear_plants", 0, None,
     "zeroed by the census (src/simulate.cpp:711), ++ per plant (src/simulate.cpp:1482)", ""),
    ("scalar", "road_total", 0, None,
     "zeroed by the census (src/simulate.cpp:697), += 1, 2 or 4 per road tile "
     "(src/simulate.cpp:1077, 1102, 1113)", _SHORT_WRAP),
    ("cost", "build_cost", 0, None,
     "monthBuildCost += before - after only when funds fell (c_api.cpp:151-153); zeroed every month "
     "(c_api.cpp:178)", ""),
    ("ledger", "sprite_cycle", None, None,
     "unbounded: tick counter spriteCycle++ (src/sprite.cpp:570) in a short; it wraps from 32,767 to "
     "-32,768, so a saturating bound would be wrong", ""),
    ("ledger", "total_pop", 0, None,
     "(short)(resPop / 8 + comPop + indPop) (src/simulate.cpp:611-613); 1 or 0 at src/simulate.cpp:314, 418",
     "non-negative while res_pop is"),
    ("ledger", "res_hist0", 0, None, "resHist[0] = resPop / 8 (src/simulate.cpp:733, 761)", "non-negative while res_pop is"),
    ("ledger", "res_hist1", 0, None, "previous resHist[0] (shift at src/simulate.cpp:748)", "non-negative while res_pop is"),
    ("ledger", "com_hist0", 0, None, "comHist[0] = comPop (src/simulate.cpp:762)", ""),
    ("ledger", "com_hist1", 0, None, "previous comHist[0] (src/simulate.cpp:749)", ""),
    ("ledger", "ind_hist0", 0, None, "indHist[0] = indPop (src/simulate.cpp:763)", ""),
    ("ledger", "ind_hist1", 0, None, "previous indHist[0] (src/simulate.cpp:750)", ""),
    ("ledger", "res_cap", 0, 1, "bool resCap (src/micropolis.h:2117)", ""),
    ("ledger", "com_cap", 0, 1, "bool comCap (src/micropolis.h:2118)", ""),
    ("ledger", "ind_cap", 0, 1, "bool indCap (src/micropolis.h:2119)", ""),
    ("ledger", "need_hospital", -1, 1,
     "assigned only -1, 0 or 1 (src/simulate.cpp:778-787; src/zone.cpp:296)", ""),
    ("ledger", "need_church", -1, 1, "assigned only -1, 0 or 1 (src/simulate.cpp:792-801; src/zone.cpp:312)", ""),
    ("ledger", "road_fund", 0, None,
     "(roadTotal + 2 railTotal) * RLevels (src/simulate.cpp:886); 0 at src/initialize.cpp:101", ""),
    ("ledger", "police_fund", 0, None, "policeStationPop * 100 (src/simulate.cpp:884); 0 at src/initialize.cpp:102", ""),
    ("ledger", "fire_fund", 0, None, "fireStationPop * 100 (src/simulate.cpp:885); 0 at src/initialize.cpp:103", ""),
    ("ledger", "auto_budget", 0, 1, "bool autoBudget (src/micropolis.h:2354)", ""),
    ("ledger", "fire_pop", 0, None,
     "zeroed by the census (src/simulate.cpp:696), ++ per fire tile (src/simulate.cpp:975)", ""),
    ("ledger", "city_center_x", 0, WORLD_W - 1,
     "mean x of zone tiles, x in 0..119, or WORLD_W / 2 with no zones (src/scan.cpp:143-154, 177-182)", ""),
    ("ledger", "city_center_y", 0, WORLD_H - 1,
     "mean y of zone tiles, y in 0..99, or WORLD_H / 2 with no zones (src/scan.cpp:143-154, 177-182)", ""),
    ("ledger", "pollution_max_x", 0, WORLD_W - 2,
     "x of a 2 x 2 pollution block, x = 0, 2, ..., 118 (src/scan.cpp:305-317); 0 at src/micropolis.cpp:516", ""),
    ("ledger", "pollution_max_y", 0, WORLD_H - 2,
     "y of a 2 x 2 pollution block, y = 0, 2, ..., 98 (src/scan.cpp:305-317); 0 at src/micropolis.cpp:516", ""),
    ("ledger", "flood_count", 0, 30,
     "set to 30 (src/disasters.cpp:369), decremented while non-zero (src/disasters.cpp:102-103)", ""),
    ("ledger", "abs_dist", 0, None,
     "absoluteValue(dispX) + absoluteValue(dispY) (src/sprite.cpp:508-510); 0 at src/micropolis.cpp:613", ""),
    ("overlay", "half overlays (5)", 0, 255,
     "byte maps MapByte2 (src/map_type.h:346; src/micropolis.h:1262-1266)", ""),
    ("overlay", "rate of growth", -200, 200,
     "clamp to +-200 (src/zone.cpp:355; decay src/simulate.cpp:385, 392)", ""),
    ("overlay", "fire, police coverage", 0, None,
     "sums of non-negative station effects (src/simulate.cpp:1515-1517, 1545-1547), smoothed by "
     "averaging (src/scan.cpp:90-112)", ""),
    ("overlay", "terrain", 0, 255, "byte map MapByte4 (src/micropolis.h:1273)", ""),
    ("overlay", "com_rate", -64, 64,
     "64 - 4 * (min(distance, 64) / 2) (src/scan.cpp:591-594, 408)", ""),
)
_SC = {n: i for i, n in enumerate(SCALAR_NAMES)}
SCALAR_BOUNDS = {_SC[n]: (lo, hi) for k, n, lo, hi, _, _ in BOUND_SOURCES if k == "scalar"}
COST_BOUNDS = next((lo, hi) for k, n, lo, hi, _, _ in BOUND_SOURCES if k == "cost")
# Overlay bounds: half overlays are bytes; rate of growth is clamped to +-200 in zone.cpp; fire and
# police coverage are non-negative with no fixed ceiling.
INF = 1.0e9
HALF_LO, HALF_HI = (0.0,) * 5, (255.0,) * 5
EIGHTH_LO, EIGHTH_HI = (-200.0, 0.0, 0.0), (200.0, INF, INF)
HALF_IN_SCALE = 255.0
EIGHTH_IN_SCALE = (200.0, 256.0, 256.0)

# Ledger (dc.engine.LEDGER_NAMES; results/oracle/observation_sufficiency.md). Three entries are set by
# definition: sim_cycle is a clock (+4 a month, mod 1024: 1,728 of 1,728 transitions measured),
# initial_eval is 1 only right after a load and 0 at every later boundary, disasters is the
# trajectory's switch (constant within a trajectory). The other 24 entries are learned.
DERIVED_LEDGER = (LG["sim_cycle"], LG["initial_eval"], LG["disasters"])
LEARNED_LEDGER = tuple(i for i in range(NUM_LEDGER) if i not in DERIVED_LEDGER)       # 24
SYMLOG_LEDGER = tuple(LG[n] for n in ("sprite_cycle", "total_pop", "res_hist0", "res_hist1", "com_hist0",
                                      "com_hist1", "ind_hist0", "ind_hist1", "road_fund", "police_fund",
                                      "fire_fund", "fire_pop", "abs_dist"))
LEDGER_BOUNDS = {LG[n]: (lo, hi) for k, n, lo, hi, _, _ in BOUND_SOURCES
                 if k == "ledger" and (lo is not None or hi is not None)}
LEDGER_FEATS = NUM_LEDGER + 5      # standardised ledger + one-hot of (sim_cycle / 4) mod 5 (growth-decay gate)
TERRAIN_LO, TERRAIN_HI = (0.0,), (255.0,)          # uint8 (measured 0..127)
COM_RATE_LO, COM_RATE_HI = (-64.0,), (64.0,)       # int16 (measured -64..64)

# Third stage (bookkeeping on scalars only): the census read off the next map stays in the second stage
# together with the month's charged build cost (an internal quantity, learned from the store's accounting,
# that stage 3 needs for funds); everything the engine computes from scalars moves to stage 3.
STAGE2_SCALARS = (SC_RES_POP, SC_COM_POP, SC_IND_POP, SC_POWERED, SC_UNPOWERED, SC_COAL, SC_NUCLEAR, SC_ROAD_TOTAL)
STAGE3_SCALARS = (SC_RES_VALVE, SC_COM_VALVE, SC_IND_VALVE, SC_SCORE, SC_FUNDS, SC_TAX_FUND, SC_ROAD_SPEND,
                  SC_FIRE_SPEND, SC_POLICE_SPEND)
# next-map summary (read off the next tiles and overlays): centre-tile counts of fire stations, police
# stations, hospitals, churches, stadiums, seaports, airports (zone-flagged), fire tiles, the zone tiles'
# centre of mass, and overlay averages (land value over cells > 0, pollution over > 0, crime over land value
# > 0, traffic over > 0, population density over > 0, number of land-value cells). Same definitions as
# code/scripts/bookkeeping_diag.py (tested equal).
SUMMARY_CENTRES = {1: (765,), 2: (774,), 3: (409,), 4: (418,) + tuple(960 + 9 * k for k in range(7)), 5: (784, 800),
                   6: (698,), 7: (716,)}
N_SUMMARY = 16
BK_RAW = NUM_SCALARS + NUM_LEDGER + 9 + N_SUMMARY + 1 + N_TOOLS + 1      # 89 raw inputs
BK_CENSUS = (SC_RES_POP, SC_COM_POP, SC_IND_POP, SC_POP, SC_POWERED, SC_UNPOWERED, SC_COAL, SC_NUCLEAR, SC_ROAD_TOTAL)

MONTH_FEATS = 2 + 12 + 4
SPEND_FEATS = N_TOOLS + 2          # attempted spend per tool channel, total, and funds (log scale)
COND_IN = len(COND_SCALARS) + MONTH_FEATS + N_ACT          # without z or spend features


def cond_in_dim(cfg: "ModelConfig") -> int:
    return COND_IN + (SPEND_FEATS if cfg.spend_features else 0) + (LEDGER_FEATS if cfg.ledger else 0)


def n_targets(cfg: "ModelConfig") -> int:
    """Learned second-stage outputs: 17 scalars (+ 24 ledger entries); with the third stage, the 8 census
    scalars and the charged build cost."""
    if cfg.bookkeeping:
        return len(STAGE2_SCALARS) + 1
    return len(LEARNED_SCALARS) + (len(LEARNED_LEDGER) if cfg.ledger else 0)


def stage2_scalar_ids(cfg: "ModelConfig") -> Tuple[int, ...]:
    return STAGE2_SCALARS if cfg.bookkeeping else LEARNED_SCALARS


def next_map_summary(st: State) -> torch.Tensor:
    """(B, 16) float64 summary of a (next) map; see SUMMARY_CENTRES."""
    codes = st["tile_index"].long()
    lut = torch.zeros(N_CODES, dtype=torch.long, device=codes.device)
    for c, cs in SUMMARY_CENTRES.items():
        lut[list(cs)] = c
    lut[56:64] = 8
    cat = lut[codes]
    zone = st["flags"][:, 0] > 0.5
    cat = torch.where((cat >= 1) & (cat <= 7) & ~zone, torch.zeros_like(cat), cat)
    cnt = torch.stack([(cat == k).sum(dim=(1, 2)) for k in range(1, 9)], dim=1).double()
    z = zone.double()
    zc = z.sum(dim=(1, 2))
    cx = (z.sum(dim=2) * torch.arange(z.shape[1], device=z.device, dtype=torch.float64)).sum(1) / zc.clamp(min=1)
    cy = (z.sum(dim=1) * torch.arange(z.shape[2], device=z.device, dtype=torch.float64)).sum(1) / zc.clamp(min=1)
    h = st["half"].double()
    pd, tr, po, lv, cr = (h[:, i] for i in range(5))

    def avg(v, m):
        k = m.double().sum(dim=(1, 2))
        return torch.where(k > 0, (v * m).sum(dim=(1, 2)) / k.clamp(min=1), torch.zeros_like(k))

    ov = torch.stack([avg(lv, lv > 0), avg(po, po > 0), avg(cr, lv > 0), avg(tr, tr > 0), avg(pd, pd > 0),
                      (lv > 0).double().sum(dim=(1, 2))], dim=1)
    return torch.cat([cnt, cx[:, None], cy[:, None], ov], dim=1)


def spend_cost_per_tile() -> torch.Tensor:
    """(15,) engine unit cost per raster tile of each tool channel: TOOL_COSTS[tool] / footprint tiles
    of one call, from dc.grammar's measured footprint table. Attempted spend of a month is then
    sum over channels of (raster tiles x cost per tile): a function of the plan alone."""
    from . import grammar
    from .engine import TOOL_COSTS
    out = []
    for t in grammar.RASTER_TOOLS:
        _, _, w, h = grammar.FOOTPRINTS[t]
        out.append(TOOL_COSTS[t] / float(w * h))
    return torch.tensor(out, dtype=torch.float32)


# ----------------------------------------------------------------------------------------------
# Sizes
# ----------------------------------------------------------------------------------------------
@dataclass
class ModelConfig:
    size: str = "50m"
    d0: int = 96                      # full resolution (120 x 100)
    dims: Tuple[int, int, int] = (192, 384, 768)    # 60x50, 30x25, 15x13
    enc: Tuple[int, int, int] = (2, 3, 6)           # blocks per level, encoder (level 3 = bottleneck)
    dec: Tuple[int, int] = (2, 2)                   # decoder blocks at 30x25, 60x50
    full_blocks: int = 1
    full_ratio: int = 4
    mlp_ratio: int = 4
    cond_dim: int = 512
    cat_hidden: int = 384             # hidden width of the sparse tile categorical head
    z_dim: int = Z_DIM
    k_mix_overlay: int = 2
    k_mix_scalar: int = 3
    post_dim: int = 96                # posterior encoder width
    layer_scale: float = 0.1
    spend_features: bool = False      # attempted spend (from the raster) and funds in the conditioning
    scalar_stage: str = "pooled"      # "pooled": scalars from pooled trunk features (pilots 1, 2);
                                      # "twostage": p(scalars | sampled next spatial state, state, action)
    ss_table_dim: int = 32            # two-stage: width of the changed-tile key table features
    ss_change_dim: int = 32           # two-stage: width of the changed-tile network features
    ss_level_dim: int = 0             # two-stage: width of the absolute next-map key histogram (0 = off)
    ss_direct_cond: bool = False      # two-stage: also feed the raw conditioning inputs (normalised scalars,
                                      # month of year, action scalars, listed price) to the second stage
    ledger: bool = False              # the sufficient observation: 27-entry ledger and the terrain and
                                      # com_rate maps as inputs and as predicted outputs
    bookkeeping: bool = False         # third stage: scalars-only network for valves, score, treasury, ledger
    bk_width: int = 384
    bk_depth: int = 4

    def to_dict(self) -> dict:
        d = asdict(self)
        d["dims"], d["enc"], d["dec"] = list(self.dims), list(self.enc), list(self.dec)
        return d

    @staticmethod
    def from_dict(d: dict) -> "ModelConfig":
        d = dict(d)
        for k in ("dims", "enc"):
            d[k] = tuple(d[k])
        d["dec"] = tuple(d["dec"])
        return ModelConfig(**d)


SIZES: Dict[str, ModelConfig] = {
    "15m": ModelConfig(size="15m", d0=64, dims=(128, 256, 448), enc=(2, 2, 4), dec=(2, 2),
                       cond_dim=256, cat_hidden=256, post_dim=64, spend_features=True, scalar_stage="twostage",
                       ss_level_dim=32, ledger=True, bookkeeping=True, bk_width=256),
    "50m": ModelConfig(size="50m", d0=96, dims=(192, 384, 768), enc=(2, 3, 6), dec=(2, 2),
                       cond_dim=512, cat_hidden=384, post_dim=96, spend_features=True, scalar_stage="twostage",
                       ss_level_dim=32, ledger=True, bookkeeping=True, bk_width=384),
    "100m": ModelConfig(size="100m", d0=128, dims=(256, 512, 1024), enc=(2, 3, 8), dec=(2, 3),
                        cond_dim=512, cat_hidden=512, post_dim=128, spend_features=True, scalar_stage="twostage",
                        ss_level_dim=32, ledger=True, bookkeeping=True, bk_width=512),
    # for tests only
    "tiny": ModelConfig(size="tiny", d0=16, dims=(32, 48, 64), enc=(1, 1, 1), dec=(1, 1),
                        cond_dim=32, cat_hidden=32, post_dim=16, mlp_ratio=2, full_ratio=2, spend_features=True,
                        scalar_stage="twostage", ss_table_dim=8, ss_change_dim=8, ss_level_dim=8, ss_direct_cond=True,
                        ledger=True),
}


# ----------------------------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------------------------
def symlog(x: torch.Tensor) -> torch.Tensor:
    return torch.sign(x) * torch.log1p(x.abs())


def month_features(city_time: torch.Tensor) -> torch.Tensor:
    """(B,) raw city_time -> (B, 18): sin, cos of the year phase, one-hot month bucket, one-hot mod 4."""
    c = city_time.round().to(torch.int64)
    m48 = torch.remainder(c, 48)
    ph = m48.float() * (2.0 * math.pi / 48.0)
    return torch.cat([
        torch.stack([torch.sin(ph), torch.cos(ph)], dim=-1),
        F.one_hot(torch.div(m48, 4, rounding_mode="floor"), 12).float(),
        F.one_hot(torch.remainder(c, 4), 4).float(),
    ], dim=-1)


def log1mexp(a: torch.Tensor) -> torch.Tensor:
    """log(1 - exp(a)) for a < 0, stable."""
    a = a.clamp(max=-1e-7)
    return torch.where(a > -0.6931472, torch.log(-torch.expm1(a)), torch.log1p(-torch.exp(a)))


def dlogistic_mix_logp(x: torch.Tensor, logit_pi: torch.Tensor, mu: torch.Tensor, log_s: torch.Tensor,
                       lo: torch.Tensor, hi: torch.Tensor) -> torch.Tensor:
    """log P(x) of a discretised logistic mixture over the integers, edge bins at lo and hi.

    x: (...); logit_pi, mu, log_s: (..., K); lo, hi broadcastable to x (use +-INF for no edge).
    Mass below lo is assigned to lo and mass above hi to hi, so the distribution sums to one over
    the integers in [lo, hi] (or over all integers when unbounded).
    """
    x = x.unsqueeze(-1)
    lo = lo.unsqueeze(-1) if lo.dim() > 0 else lo
    hi = hi.unsqueeze(-1) if hi.dim() > 0 else hi
    inv_s = torch.exp(-log_s)
    c = x - mu
    plus_in = inv_s * (c + 0.5)
    min_in = inv_s * (c - 0.5)
    log_cdf_plus = plus_in - F.softplus(plus_in)            # log sigmoid(plus_in)
    log_1m_cdf_min = -F.softplus(min_in)                    # log (1 - sigmoid(min_in))
    # log(sigmoid(plus) - sigmoid(min)) computed stably on whichever side of the mode x lies.
    # For c >= 0 use the upper tails: S(-min) - S(-plus); else S(plus) - S(min).
    a = torch.where(c >= 0, -min_in, plus_in)
    b = torch.where(c >= 0, -plus_in, min_in)
    log_sa = a - F.softplus(a)
    log_sb = b - F.softplus(b)
    log_mid = log_sa + log1mexp(log_sb - log_sa)
    # fall back to the density at the centre when the bin is numerically tiny
    mid_in = inv_s * c
    log_pdf = mid_in - log_s - 2.0 * F.softplus(mid_in)
    log_mid = torch.where(log_mid > -30.0, log_mid, log_pdf)
    lp = torch.where(x <= lo, log_cdf_plus, torch.where(x >= hi, log_1m_cdf_min, log_mid))
    return torch.logsumexp(F.log_softmax(logit_pi, dim=-1) + lp, dim=-1)


def dlogistic_mix_sample(logit_pi: torch.Tensor, mu: torch.Tensor, log_s: torch.Tensor,
                         lo: torch.Tensor, hi: torch.Tensor, temperature: float) -> torch.Tensor:
    """Sample (or, at temperature 0, take the mode component's centre), rounded and clamped."""
    if temperature <= 0:
        k = logit_pi.argmax(-1, keepdim=True)
        v = mu.gather(-1, k).squeeze(-1)
    else:
        g = -torch.log(-torch.log(torch.rand_like(logit_pi).clamp_(1e-12, 1 - 1e-7)))
        k = (logit_pi + g).argmax(-1, keepdim=True)
        m = mu.gather(-1, k).squeeze(-1)
        s = torch.exp(log_s.gather(-1, k).squeeze(-1)) * temperature
        u = torch.rand_like(m).clamp_(1e-6, 1 - 1e-6)
        v = m + s * (torch.log(u) - torch.log1p(-u))
    v = torch.round(v)
    return torch.maximum(torch.minimum(v, hi), lo)


def target_bounds(scalar_idx: Sequence[int] = (), ledger_idx: Sequence[int] = (), cost: bool = False):
    """(lo, hi) tuples of floats (+-INF where unbounded) for a target vector laid out as the given
    scalars, then the given ledger entries, then (optionally) the month's charged build cost."""
    b = [SCALAR_BOUNDS.get(i, (None, None)) for i in scalar_idx] + \
        [LEDGER_BOUNDS.get(i, (None, None)) for i in ledger_idx] + ([COST_BOUNDS] if cost else [])
    return (tuple(-INF if lo is None else float(lo) for lo, _ in b),
            tuple(INF if hi is None else float(hi) for _, hi in b))


_CONST_CACHE: Dict[Tuple[Tuple[float, ...], str], torch.Tensor] = {}


def _const(values: Tuple[float, ...], device: torch.device) -> torch.Tensor:
    """A float64 constant on ``device``, made once (a host-to-device copy per call would stall the stream)."""
    key = (values, str(device))
    t = _CONST_CACHE.get(key)
    if t is None:
        t = _CONST_CACHE[key] = torch.tensor(values, dtype=torch.float64, device=device)
    return t


def censor_limits(cur: torch.Tensor, bounds) -> Tuple[torch.Tensor, torch.Tensor]:
    """Edge-bin limits of the change d = next - cur for quantities bounded in [lo, hi]: lo - cur and
    hi - cur (computed in float64, so a target that sits on a bound equals its limit exactly). The
    clamps keep "no change" in the support should a current value ever lie outside its bounds (the
    engine's data never do: code/scripts/bounds_table.py counts them)."""
    lo, hi = bounds
    cur = cur.double()
    lo_d = (_const(lo, cur.device) - cur).clamp(max=0.0)
    hi_d = (_const(hi, cur.device) - cur).clamp(min=0.0)
    return lo_d.float(), hi_d.float()


def censored_next(cur: torch.Tensor, d: torch.Tensor, lo_d: torch.Tensor, hi_d: torch.Tensor, bounds) -> torch.Tensor:
    """cur + d in float64 for a censored sample d, with a sample in an edge bin mapped onto its bound
    exactly (float32 limits are inexact only for |cur| above 2^24; this is not a clamp: in exact
    arithmetic cur + d already equals the bound there)."""
    lo, hi = bounds
    nxt = cur.double() + d.double()
    lo_t = _const(lo, nxt.device).expand_as(nxt)
    hi_t = _const(hi, nxt.device).expand_as(nxt)
    nxt = torch.where((d <= lo_d) & (lo_t > -INF), lo_t, nxt)
    return torch.where((d >= hi_d) & (hi_t < INF), hi_t, nxt)


# Bounds of each head's target vector (same layout as its targets).
S2_BOUNDS = target_bounds(LEARNED_SCALARS)                                   # no ledger, no third stage
S2_BOUNDS_LEDGER = target_bounds(LEARNED_SCALARS, LEARNED_LEDGER)            # ledger, no third stage
S2_BOUNDS_BK = target_bounds(STAGE2_SCALARS, cost=True)                      # census + charged cost
BK_BOUNDS = target_bounds(STAGE3_SCALARS, LEARNED_LEDGER)                    # third stage


def gated_logp(x: torch.Tensor, cur: torch.Tensor, gate_logit: torch.Tensor, dlm_logp: torch.Tensor) -> torch.Tensor:
    """p(x) = (1 - g) [x == cur] + g DLM(x)."""
    lg = F.logsigmoid(gate_logit)
    l1g = F.logsigmoid(-gate_logit)
    same = x == cur
    return torch.where(same, torch.logaddexp(l1g, lg + dlm_logp), lg + dlm_logp)


def bernoulli_logp(x: torch.Tensor, logit: torch.Tensor) -> torch.Tensor:
    return -F.binary_cross_entropy_with_logits(logit, x, reduction="none")


# ----------------------------------------------------------------------------------------------
# Blocks
# ----------------------------------------------------------------------------------------------
class Block(nn.Module):
    """ConvNeXt block with FiLM: dw 7x7 -> LayerNorm -> FiLM -> MLP -> layer scale, residual.

    Tensors are NCHW in channels_last memory, so the permute to NHWC for the MLP is free.
    """

    def __init__(self, dim: int, cond_dim: int, mlp_ratio: int = 4, layer_scale: float = 0.1) -> None:
        super().__init__()
        self.dw = nn.Conv2d(dim, dim, 7, padding=3, groups=dim)
        self.norm = nn.LayerNorm(dim, elementwise_affine=False)
        self.film = nn.Linear(cond_dim, 2 * dim)
        self.fc1 = nn.Linear(dim, mlp_ratio * dim)
        self.fc2 = nn.Linear(mlp_ratio * dim, dim)
        self.gamma = nn.Parameter(torch.full((dim,), float(layer_scale)))
        nn.init.zeros_(self.film.weight)
        nn.init.zeros_(self.film.bias)

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        h = self.dw(x).permute(0, 2, 3, 1)
        h = self.norm(h)
        g, b = self.film(cond)[:, None, None, :].chunk(2, dim=-1)
        h = h * (1.0 + g) + b
        h = self.fc2(F.gelu(self.fc1(h), approximate="tanh")) * self.gamma
        return x + h.permute(0, 3, 1, 2)


class PlainBlock(nn.Module):
    """ConvNeXt block without conditioning (posterior encoder)."""

    def __init__(self, dim: int) -> None:
        super().__init__()
        self.dw = nn.Conv2d(dim, dim, 7, padding=3, groups=dim)
        self.norm = nn.LayerNorm(dim, elementwise_affine=False)
        self.fc1 = nn.Linear(dim, 2 * dim)
        self.fc2 = nn.Linear(2 * dim, dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.norm(self.dw(x).permute(0, 2, 3, 1))
        h = self.fc2(F.gelu(self.fc1(h), approximate="tanh"))
        return x + h.permute(0, 3, 1, 2)


class ChanNorm(nn.Module):
    """LayerNorm over channels of an NCHW (channels_last) tensor (no affine: the next layer is linear)."""

    def __init__(self, dim: int) -> None:
        super().__init__()
        self.ln = nn.LayerNorm(dim, elementwise_affine=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.ln(x.permute(0, 2, 3, 1)).permute(0, 3, 1, 2)


def _cl(x: torch.Tensor) -> torch.Tensor:
    return x.contiguous(memory_format=torch.channels_last)


def nhwc_to_nchw(x: torch.Tensor) -> torch.Tensor:
    """(B,H,W,C) contiguous -> (B,C,H,W) view in channels_last memory (no copy)."""
    return x.permute(0, 3, 1, 2)


# ----------------------------------------------------------------------------------------------
# The trunk: dense outputs from (state, action, cond)
# ----------------------------------------------------------------------------------------------
class Trunk(nn.Module):
    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        d0, (d1, d2, d3) = cfg.d0, cfg.dims
        C = cfg.cond_dim
        self.cfg = cfg
        self.tile_emb = nn.Embedding(N_CODES, d0)
        self.full_in = nn.Linear(N_FLAGS + 1 + N_TOOLS, d0)
        self.full_norm = nn.LayerNorm(d0, elementwise_affine=False)
        self.patch = nn.Conv2d(d0, d1, 2, stride=2)
        self.half_in = nn.Linear(N_HALF + N_EIGHTH, d1)
        self.eighth_in = nn.Linear(N_EIGHTH, d3)
        self.enc1 = nn.ModuleList([Block(d1, C, cfg.mlp_ratio, cfg.layer_scale) for _ in range(cfg.enc[0])])
        self.down1 = nn.Sequential(ChanNorm(d1), nn.Conv2d(d1, d2, 2, stride=2))
        self.enc2 = nn.ModuleList([Block(d2, C, cfg.mlp_ratio, cfg.layer_scale) for _ in range(cfg.enc[1])])
        self.down2_norm = ChanNorm(d2)
        self.down2 = nn.Conv2d(d2, d3, 2, stride=2)
        self.bot = nn.ModuleList([Block(d3, C, cfg.mlp_ratio, cfg.layer_scale) for _ in range(cfg.enc[2])])
        self.up2 = nn.Sequential(ChanNorm(d3), nn.ConvTranspose2d(d3, d2, 2, stride=2))
        self.dec2 = nn.ModuleList([Block(d2, C, cfg.mlp_ratio, cfg.layer_scale) for _ in range(cfg.dec[0])])
        self.up1 = nn.Sequential(ChanNorm(d2), nn.ConvTranspose2d(d2, d1, 2, stride=2))
        self.dec1 = nn.ModuleList([Block(d1, C, cfg.mlp_ratio, cfg.layer_scale) for _ in range(cfg.dec[1])])
        self.up0 = nn.Sequential(ChanNorm(d1), nn.ConvTranspose2d(d1, d0, 2, stride=2))
        self.full = nn.ModuleList([Block(d0, C, cfg.full_ratio, cfg.layer_scale) for _ in range(cfg.full_blocks)])
        self.full_out_norm = nn.LayerNorm(d0, elementwise_affine=False)
        # heads
        self.head_full = nn.Linear(d0, 1 + N_FLAGS + 1)          # gate, 5 flags, power
        self.copy_gain = nn.Parameter(torch.full((N_FLAGS + 1,), 3.0))
        k = cfg.k_mix_overlay
        self.half_norm = nn.LayerNorm(d1, elementwise_affine=False)
        self.head_half = nn.Linear(d1, N_HALF * (1 + 3 * k))
        self.eighth_norm = nn.LayerNorm(d3, elementwise_affine=False)
        self.head_eighth = nn.Linear(d3, N_EIGHTH * (1 + 3 * k))
        ks = cfg.k_mix_scalar
        if cfg.ledger:
            self.terrain_in = nn.Linear(1, d2)                   # 30 x 25 (4 x 4 tiles), at the d2 level
            self.com_rate_in = nn.Linear(1, d3)                  # 15 x 13, at the bottleneck
            self.terrain_norm = nn.LayerNorm(d2, elementwise_affine=False)
            self.head_terrain = nn.Linear(d2, 1 + 3 * k)
            self.head_com_rate = nn.Linear(d3, 1 + 3 * k)
        if cfg.scalar_stage == "pooled":
            self.head_scalar = nn.Sequential(
                nn.Linear(d3 + d1 + C, C), nn.GELU(approximate="tanh"), nn.Linear(C, len(LEARNED_SCALARS) * (1 + 3 * ks)))

    def forward(self, tile_index: torch.Tensor, flags: torch.Tensor, power: torch.Tensor, half: torch.Tensor,
                eighth: torch.Tensor, raster: torch.Tensor, cond: torch.Tensor,
                terrain: Optional[torch.Tensor] = None, com_rate: Optional[torch.Tensor] = None):
        B = tile_index.shape[0]
        # full resolution, NHWC
        other = torch.cat([flags, power.unsqueeze(1), raster.to(flags.dtype)], dim=1)       # (B,21,X,Y)
        f0 = self.tile_emb(tile_index) + self.full_in(other.permute(0, 2, 3, 1))
        f0 = self.full_norm(f0)                                                              # (B,X,Y,d0)
        x0 = nhwc_to_nchw(f0)
        # 60 x 50
        e8 = torch.stack([eighth[:, i] / s for i, s in enumerate(EIGHTH_IN_SCALE)], dim=1)   # (B,3,15,13)
        e8_up = e8.repeat_interleave(4, dim=2).repeat_interleave(4, dim=3)[:, :, :, :WORLD_H_2]
        ov = torch.cat([half / HALF_IN_SCALE, e8_up], dim=1).permute(0, 2, 3, 1)
        h1 = self.patch(x0) + nhwc_to_nchw(self.half_in(ov))
        for b in self.enc1:
            h1 = b(h1, cond)
        # 30 x 25
        h2 = self.down1(h1)
        if terrain is not None:
            h2 = h2 + nhwc_to_nchw(self.terrain_in((terrain.float() / 255.0).unsqueeze(-1)))
        for b in self.enc2:
            h2 = b(h2, cond)
        # 15 x 13 (right-pad 25 -> 26 so cells align with the engine's 8 x 8 blocks)
        h3 = self.down2(F.pad(self.down2_norm(h2), (0, 1)))
        h3 = h3 + nhwc_to_nchw(self.eighth_in(e8.permute(0, 2, 3, 1)))
        if com_rate is not None:
            h3 = h3 + nhwc_to_nchw(self.com_rate_in((com_rate.float() / 64.0).unsqueeze(-1)))
        for b in self.bot:
            h3 = b(h3, cond)
        # back up
        u2 = self.up2(h3)[:, :, :, :WORLD_H_2 // 2] + h2
        for b in self.dec2:
            u2 = b(u2, cond)
        u1 = self.up1(u2) + h1
        for b in self.dec1:
            u1 = b(u1, cond)
        u0 = self.up0(u1) + x0
        for b in self.full:
            u0 = b(u0, cond)
        feat = self.full_out_norm(u0.permute(0, 2, 3, 1))                                    # (B,X,Y,d0)
        dense = self.head_full(feat)                                                         # (B,X,Y,7)
        cur = torch.cat([flags, power.unsqueeze(1)], dim=1).permute(0, 2, 3, 1)              # (B,X,Y,6)
        dense = torch.cat([dense[..., :1], dense[..., 1:] + self.copy_gain * (2.0 * cur - 1.0)], dim=-1)
        half_par = self.head_half(self.half_norm(u1.permute(0, 2, 3, 1)))                    # (B,60,50,5*(1+3k))
        eighth_par = self.head_eighth(self.eighth_norm(h3.permute(0, 2, 3, 1)))              # (B,15,13,3*(1+3k))
        pooled = torch.cat([h3.mean(dim=(2, 3)), u1.mean(dim=(2, 3)), cond], dim=1)
        terrain_par = com_par = None
        if terrain is not None:
            terrain_par = self.head_terrain(self.terrain_norm(u2.permute(0, 2, 3, 1)))      # (B,30,25,1+3k)
            com_par = self.head_com_rate(self.eighth_norm(h3.permute(0, 2, 3, 1)))         # (B,15,13,1+3k)
        return feat, dense, half_par, eighth_par, pooled, terrain_par, com_par


def scalar_keys(st: State) -> torch.Tensor:
    """(B,X,Y) int64 per-tile key: code * 16 + (zone, burnable, powered flag, power map) bits."""
    f = st["flags"] > 0.5
    bits = (f[:, 0].long() | (f[:, 2].long() << 1) | (f[:, 4].long() << 2) | ((st["power"] > 0.5).long() << 3))
    return (st["tile_index"].long() << 4) | bits


class ScalarStage(nn.Module):
    """Second stage: p(next scalars | next spatial state, current state, action), trained teacher-forced on
    the engine's next spatial state and fed the model's own sampled one in rollouts.

    Features (all learned functions; no engine rule is written in):
    * changed-tile key tables: for every tile whose key (code and four bits) differs between the current
      and the next map, sum e[key_next] - e[key_cur]. Unchanged tiles contribute exactly zero, so any
      change of a per-tile count is representable exactly and the sum runs over the changed tiles only.
      One table (``delta_skip``, one column per learned scalar, in units of the scalar's delta scale) is
      added directly to the location of the scalar's change distribution; a second (``delta_feat``) feeds
      the network.
    * a changed-tile network on (current code, next code, action raster at the tile, listed price per
      tile, key bits), sum-pooled, with the same two outputs (location skip and features): the month's
      spend is visible in the map change inside the action footprint.
    * overlays: a per-cell network on (next, current) half and eighth overlays, pooled;
    * the trunk's pooled features (current-state context and the conditioning vector: normalised
      scalars, month of year, action scalars, listed price, z).
    """

    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        nL = n_targets(cfg)
        d1, d3, C = cfg.dims[0], cfg.dims[2], cfg.cond_dim
        self.nL = nL
        self.ledger = cfg.ledger
        if cfg.ledger:
            # learned linear path from the current scalars and ledger (raw, in units of each entry's delta
            # scale) to the location of every learned change: carried bookkeeping is representable exactly
            self.state_skip = nn.Linear(NUM_SCALARS + NUM_LEDGER, nL, bias=False)
        self.delta_skip = nn.Embedding(N_CODES * 16, nL)
        self.delta_feat = nn.Embedding(N_CODES * 16, cfg.ss_table_dim)
        self.code_emb = nn.Embedding(N_CODES, 16)
        self.change_mlp = nn.Sequential(nn.Linear(16 + 16 + N_TOOLS + 1 + 8, 128), nn.GELU(approximate="tanh"),
                                        nn.Linear(128, nL + cfg.ss_change_dim))
        self.half_mlp = nn.Sequential(nn.Linear(2 * N_HALF, 32), nn.GELU(approximate="tanh"), nn.Linear(32, 16))
        self.eighth_mlp = nn.Sequential(nn.Linear(2 * N_EIGHTH, 16), nn.GELU(approximate="tanh"), nn.Linear(16, 8))
        in_dim = (cfg.ss_table_dim + cfg.ss_change_dim + 16 + 8 + d3 + d1 + C + cfg.ss_level_dim
                  + (cond_in_dim(cfg) if cfg.ss_direct_cond else 0)
                  + ((len(COND_SCALARS) + LEDGER_FEATS) if cfg.ledger else 0))
        self.ss_direct_cond = cfg.ss_direct_cond
        self.norm = nn.LayerNorm(in_dim)
        self.mlp = nn.Sequential(nn.Linear(in_dim, C), nn.GELU(approximate="tanh"), nn.Linear(C, C),
                                 nn.GELU(approximate="tanh"), nn.Linear(C, nL * (1 + 3 * cfg.k_mix_scalar)))
        self.ss_change_dim = cfg.ss_change_dim
        self.ss_table_dim = cfg.ss_table_dim
        self.ss_level_dim = cfg.ss_level_dim
        if cfg.ss_level_dim > 0:
            # absolute levels of the next map: sum over all tiles of a learned vector per key, so totals of
            # stations, roads, zones and the like are representable (budget-month amounts, valves, score)
            self.level = nn.EmbeddingBag(N_CODES * 16, cfg.ss_level_dim, mode="sum")
            nn.init.normal_(self.level.weight, std=0.02)
            self.level_norm = nn.LayerNorm(cfg.ss_level_dim)

    def reset_skips(self) -> None:
        nn.init.zeros_(self.delta_skip.weight)
        if self.ledger:
            nn.init.zeros_(self.state_skip.weight)
        with torch.no_grad():
            self.change_mlp[-1].weight[: self.nL].zero_()
            self.change_mlp[-1].bias[: self.nL].zero_()

    def forward(self, pooled: torch.Tensor, s0: State, s1: State, raster: torch.Tensor, spend_cost: torch.Tensor,
                cond_in: Optional[torch.Tensor] = None, state_x: Optional[torch.Tensor] = None,
                direct: Optional[torch.Tensor] = None):
        k0, k1 = scalar_keys(s0), scalar_keys(s1)
        B = k0.shape[0]
        dev = k0.device
        skip = torch.zeros(B, self.nL, device=dev)
        tfeat = torch.zeros(B, self.ss_table_dim, device=dev)
        cfeat = torch.zeros(B, self.ss_change_dim, device=dev)
        bi, xi, yi = (k0 != k1).nonzero(as_tuple=True)
        if bi.numel() > 0:
            a, b = k0[bi, xi, yi], k1[bi, xi, yi]
            skip = skip.index_add(0, bi, self.delta_skip(b) - self.delta_skip(a))
            tfeat = tfeat.index_add(0, bi, self.delta_feat(b) - self.delta_feat(a))
            r = raster[bi, :, xi, yi].float()
            price = (r * spend_cost).sum(-1, keepdim=True) / 100.0
            sh = torch.arange(4, device=dev)
            x = torch.cat([self.code_emb(a >> 4), self.code_emb(b >> 4), r, price,
                           ((a & 15).unsqueeze(1) >> sh & 1).float(), ((b & 15).unsqueeze(1) >> sh & 1).float()], dim=1)
            o = self.change_mlp(x)
            skip = skip.index_add(0, bi, o[:, :self.nL])
            cfeat = cfeat.index_add(0, bi, o[:, self.nL:])
        hv = torch.cat([s1["half"], s0["half"]], dim=1).float().permute(0, 2, 3, 1) / HALF_IN_SCALE
        hp = self.half_mlp(hv).sum(dim=(1, 2)) / (WORLD_W_2 * WORLD_H_2)
        sc = torch.tensor(EIGHTH_IN_SCALE * 2, device=dev)
        ev = torch.cat([s1["eighth"], s0["eighth"]], dim=1).float().permute(0, 2, 3, 1) / sc
        ep = self.eighth_mlp(ev).sum(dim=(1, 2)) / (WORLD_W_8 * WORLD_H_8)
        parts = [tfeat, cfeat / 10.0, hp, ep, pooled.float()]
        if self.ss_level_dim > 0:
            lv = self.level(k1.reshape(B, -1)) / 1000.0
            parts.append(self.level_norm(lv) + lv)
        if self.ss_direct_cond:
            parts.append(cond_in.float())
        if self.ledger:
            parts.append(direct.float())
            skip = skip + self.state_skip(state_x.float())
        h = self.norm(torch.cat(parts, dim=1))
        return self.mlp(h), skip


class _Res(nn.Module):
    def __init__(self, w: int) -> None:
        super().__init__()
        self.n = nn.LayerNorm(w)
        self.f = nn.Sequential(nn.Linear(w, 2 * w), nn.GELU(approximate="tanh"), nn.Linear(2 * w, w))

    def forward(self, x):
        return x + self.f(self.n(x))


class BookStage(nn.Module):
    """Third stage, on scalars only: p(valves, score, treasury, ledger at t+1 | this month's scalars and ledger,
    the action, the listed price, month of year, the next month's census, next-map summary and charged
    cost). Trained on the true next census (its own sample count and optimiser), fed the model's own
    predicted ones in rollouts. A residual MLP on symmetric-log and linearly scaled inputs."""

    TARGET_SCALARS = STAGE3_SCALARS

    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        w = cfg.bk_width
        self.nT = len(STAGE3_SCALARS) + len(LEARNED_LEDGER)
        self.inp = nn.Linear(2 * BK_RAW + N_ACT + MONTH_FEATS, w)
        self.blocks = nn.Sequential(*[_Res(w) for _ in range(cfg.bk_depth)])
        self.out = nn.Sequential(nn.LayerNorm(w), nn.Linear(w, self.nT * (1 + 3 * cfg.k_mix_scalar)))
        for k in ("bk_mean_l", "bk_mean_r"):
            self.register_buffer(k, torch.zeros(BK_RAW, dtype=torch.float64))
        for k in ("bk_std_l", "bk_std_r"):
            self.register_buffer(k, torch.ones(BK_RAW, dtype=torch.float64))

    def features(self, raw: torch.Tensor, act: torch.Tensor, month: torch.Tensor) -> torch.Tensor:
        raw = raw.double()
        a = (symlog(raw) - self.bk_mean_l) / self.bk_std_l
        b = ((raw - self.bk_mean_r) / self.bk_std_r).clamp(-50, 50)
        return torch.cat([a.float(), b.float(), act.float(), month.float()], dim=1)

    def forward(self, raw: torch.Tensor, act: torch.Tensor, month: torch.Tensor) -> torch.Tensor:
        return self.out(self.blocks(self.inp(self.features(raw, act, month))))


def bk_raw(s0: State, s1: State, cost: torch.Tensor, spend: torch.Tensor) -> torch.Tensor:
    """(B, 89) raw stage-3 inputs: current scalars and ledger, next census (with pop), next-map summary,
    charged cost, listed price per tool channel and total. ``spend``: (B, 15) listed price per channel."""
    return torch.cat([s0["scalars"].double(), s0["ledger"].double(), s1["scalars"][:, list(BK_CENSUS)].double(),
                      next_map_summary(s1), cost.double().view(-1, 1), spend.double(),
                      spend.double().sum(1, keepdim=True)], dim=1)


class Posterior(nn.Module):
    """q(z | s_t, a_t, s_t+1): what changed, pooled to a diagonal Gaussian."""

    def __init__(self, cfg: ModelConfig) -> None:
        super().__init__()
        p = cfg.post_dim
        self.new_emb = nn.Embedding(N_CODES, 8)
        self.full_in = nn.Conv2d(1 + 8 + N_FLAGS + 1, p, 4, stride=4)          # 120x100 -> 30x25
        self.half_in = nn.Conv2d(N_HALF, p, 2, stride=2)                       # 60x50 -> 30x25
        self.b1 = PlainBlock(p)
        self.down = nn.Conv2d(p, 2 * p, 2, stride=2)                           # 30x26 -> 15x13
        self.eighth_in = nn.Linear(N_EIGHTH, 2 * p)
        self.b2 = PlainBlock(2 * p)
        self.mlp = nn.Sequential(nn.Linear(4 * p + NUM_SCALARS + (NUM_LEDGER if cfg.ledger else 0) + cond_in_dim(cfg), 2 * p),
                                 nn.GELU(approximate="tanh"),
                                 nn.Linear(2 * p, 2 * cfg.z_dim))
        nn.init.zeros_(self.mlp[-1].weight)
        nn.init.zeros_(self.mlp[-1].bias)

    def forward(self, s0: State, s1: State, dscal: torch.Tensor, cond_in: torch.Tensor):
        changed = (s1["tile_index"] != s0["tile_index"])
        dt = flags_dtype(s0)
        ne = self.new_emb(s1["tile_index"]) * changed.unsqueeze(-1).to(dt)                  # (B,X,Y,8)
        dfl = (s1["flags"] - s0["flags"]).permute(0, 2, 3, 1)
        dpw = (s1["power"] - s0["power"]).unsqueeze(-1)
        full = torch.cat([changed.unsqueeze(-1).to(dt), ne.to(dt), dfl.to(dt), dpw.to(dt)], dim=-1)
        h = self.full_in(nhwc_to_nchw(full))
        h = h + self.half_in(_cl((s1["half"] - s0["half"]) / 32.0))
        h = self.b1(h)
        h = self.down(F.pad(h, (0, 1)))
        de = torch.stack([(s1["eighth"][:, i] - s0["eighth"][:, i]) / s for i, s in enumerate(EIGHTH_IN_SCALE)], 1)
        h = h + nhwc_to_nchw(self.eighth_in(de.permute(0, 2, 3, 1)))
        h = self.b2(h)
        pooled = torch.cat([h.mean(dim=(2, 3)), h.amax(dim=(2, 3))], dim=1)
        out = self.mlp(torch.cat([pooled, dscal, cond_in], dim=1))
        mu, logvar = out.float().chunk(2, dim=1)
        return mu, logvar.clamp(-12.0, 6.0)


def flags_dtype(s: State) -> torch.dtype:
    return s["flags"].dtype


# ----------------------------------------------------------------------------------------------
# The emulator
# ----------------------------------------------------------------------------------------------
class Emulator(nn.Module):
    """Stochastic one-month transition model p(s_t+1 | s_t, a_t) = E_z p(s_t+1 | s_t, a_t, z)."""

    def __init__(self, size: Union[str, ModelConfig] = "50m") -> None:
        super().__init__()
        cfg = SIZES[size] if isinstance(size, str) else size
        self.cfg = cfg
        C = cfg.cond_dim
        self.cond_mlp = nn.Sequential(nn.Linear(cond_in_dim(cfg) + cfg.z_dim, C), nn.GELU(approximate="tanh"),
                                      nn.Linear(C, C), nn.GELU(approximate="tanh"))
        self.trunk = Trunk(cfg)
        self.posterior = Posterior(cfg)
        d0 = cfg.d0
        self.cat_head = nn.Sequential(nn.Linear(2 * d0, cfg.cat_hidden), nn.GELU(approximate="tanh"),
                                      nn.Linear(cfg.cat_hidden, N_CODES))
        self.new_flag_emb = nn.Embedding(N_CODES, N_FLAGS + 1)
        self.new_flag_lin = nn.Linear(d0, N_FLAGS + 1)
        if cfg.scalar_stage == "twostage":
            if not cfg.spend_features:
                raise ValueError("the two-stage scalar pathway uses the listed price: spend_features must be on")
            self.scalar_stage = ScalarStage(cfg)
        elif cfg.scalar_stage != "pooled":
            raise ValueError(f"scalar_stage {cfg.scalar_stage!r}")
        if cfg.ledger and cfg.scalar_stage != "twostage":
            raise ValueError("the ledger entries are predicted by the second stage: scalar_stage must be twostage")
        if cfg.bookkeeping:
            if not cfg.ledger:
                raise ValueError("the third stage reads the ledger: ledger must be on")
            self.bk = BookStage(cfg)
            self.register_buffer("cost_scale", torch.ones((), dtype=torch.float64))
        # normalisation statistics (checkpointed; set by set_norm_stats from compute_norm_stats)
        self.register_buffer("cond_mean", torch.zeros(NUM_SCALARS, dtype=torch.float64))
        self.register_buffer("cond_std", torch.ones(NUM_SCALARS, dtype=torch.float64))
        self.register_buffer("delta_scale", torch.ones(NUM_SCALARS, dtype=torch.float64))
        self.register_buffer("norm_n", torch.zeros((), dtype=torch.int64))
        if cfg.spend_features:
            self.register_buffer("spend_cost", spend_cost_per_tile())
        if cfg.ledger:
            self.register_buffer("ledger_mean", torch.zeros(NUM_LEDGER, dtype=torch.float64))
            self.register_buffer("ledger_std", torch.ones(NUM_LEDGER, dtype=torch.float64))
            self.register_buffer("ledger_delta_scale", torch.ones(NUM_LEDGER, dtype=torch.float64))
        self._init_weights()
        # plain attributes (not registered submodules): the possibly compiled trunk, chunking
        object.__setattr__(self, "_trunk_fn", self.trunk)
        self.max_batch: Optional[int] = None

    # -- init / utilities ----------------------------------------------------------------------
    def _init_weights(self) -> None:
        for m in self.modules():
            if isinstance(m, (nn.Linear, nn.Conv2d, nn.ConvTranspose2d)):
                nn.init.trunc_normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
        for blk in self.modules():
            if isinstance(blk, Block):
                nn.init.zeros_(blk.film.weight)
                nn.init.zeros_(blk.film.bias)
        nn.init.zeros_(self.posterior.mlp[-1].weight)
        nn.init.zeros_(self.posterior.mlp[-1].bias)
        nn.init.normal_(self.trunk.tile_emb.weight, std=1.0)
        if self.cfg.scalar_stage == "twostage":
            self.scalar_stage.reset_skips()
        # priors: about 1 per cent of tiles change; overlays change in about a fifth of cells
        with torch.no_grad():
            self.trunk.head_full.bias[0] = -4.6
            k = self.cfg.k_mix_overlay
            self.trunk.head_half.bias.view(N_HALF, 1 + 3 * k)[:, 0] = -1.4
            self.trunk.head_eighth.bias.view(N_EIGHTH, 1 + 3 * k)[:, 0] = -1.4
            if self.cfg.ledger:
                self.trunk.head_terrain.bias[0] = -2.6
                self.trunk.head_com_rate.bias[0] = -2.0

    @property
    def safe_batch(self) -> int:
        """Largest power-of-two batch whose full-resolution conv tensors stay under 2**31 elements
        (cuDNN convolutions index with 32 bits; above that they fault). sample_next chunks to it."""
        n = (2**31 - 1) // (WORLD_W * WORLD_H * self.cfg.d0)
        return 1 << (n.bit_length() - 1)

    def num_parameters(self, sampling_path_only: bool = False) -> int:
        n = sum(p.numel() for p in self.parameters())
        if sampling_path_only:
            n -= sum(p.numel() for p in self.posterior.parameters())
        return n

    def compile_trunk(self, **kw) -> None:
        """torch.compile the dense trunk (fixed shapes); heads and sparse parts stay eager."""
        object.__setattr__(self, "_trunk_fn", torch.compile(self.trunk, **kw))

    def uncompile_trunk(self) -> None:
        object.__setattr__(self, "_trunk_fn", self.trunk)

    @property
    def norm_ready(self) -> bool:
        return int(self.norm_n.item()) > 0

    def set_norm_stats(self, stats: Dict[str, torch.Tensor]) -> None:
        self.cond_mean.copy_(stats["cond_mean"].to(self.cond_mean))
        self.cond_std.copy_(stats["cond_std"].to(self.cond_std))
        self.delta_scale.copy_(stats["delta_scale"].to(self.delta_scale))
        self.norm_n.fill_(int(stats["n"]))
        if self.cfg.ledger:
            for k in ("ledger_mean", "ledger_std", "ledger_delta_scale"):
                getattr(self, k).copy_(stats[k].to(getattr(self, k)))
        if self.cfg.bookkeeping and "cost_scale" in stats:
            self.cost_scale.fill_(float(stats["cost_scale"]))

    def set_bk_stats(self, stats: Dict[str, torch.Tensor]) -> None:
        for k in ("bk_mean_l", "bk_std_l", "bk_mean_r", "bk_std_r"):
            getattr(self.bk, k).copy_(stats[k].to(getattr(self.bk, k)))

    @property
    def recon_terms(self) -> Tuple[str, ...]:
        """Terms of the held-out likelihood (every stage, teacher-forced)."""
        return (self.RECON_TERMS + (("ledger", "terrain", "com_rate") if self.cfg.ledger else ())
                + (("build_cost",) if self.cfg.bookkeeping else ()))

    @property
    def train_terms(self) -> Tuple[str, ...]:
        """Terms the main optimiser trains (the third stage has its own schedule)."""
        if not self.cfg.bookkeeping:
            return self.recon_terms
        return ("tile_gate", "tile_cat", "flags", "power", "half", "eighth", "scalars_s2", "build_cost", "terrain", "com_rate")

    # -- conditioning ----------------------------------------------------------------------------
    def norm_scalars(self, scalars: torch.Tensor) -> torch.Tensor:
        """(B,20) raw -> (B,20) standardised (symlog for wide-range scalars)."""
        x = scalars.double()
        sl = torch.zeros(NUM_SCALARS, dtype=torch.bool, device=x.device)
        sl[list(SYMLOG_SCALARS)] = True
        t = torch.where(sl, symlog(x), x)
        return ((t - self.cond_mean) / self.cond_std).float()

    def spend_features(self, state: State, raster: torch.Tensor) -> torch.Tensor:
        """(B, 17): log1p(attempted spend per tool channel), log1p(total), log1p(funds), all / 10.
        Attempted spend uses the raster (every attempted call) and the engine's unit costs only."""
        per = raster.float().sum(dim=(2, 3)) * self.spend_cost                       # (B, 15)
        funds = state["scalars"][:, SC_FUNDS].float().clamp(min=0)
        return torch.cat([torch.log1p(per), torch.log1p(per.sum(1, keepdim=True)),
                          torch.log1p(funds).unsqueeze(1)], dim=1) / 10.0

    def norm_ledger(self, ledger: torch.Tensor) -> torch.Tensor:
        """(B,27) raw -> (B,32): standardised (symmetric log for wide entries) + one-hot of (sim_cycle/4) mod 5."""
        x = ledger.double()
        sl = torch.zeros(NUM_LEDGER, dtype=torch.bool, device=x.device)
        sl[list(SYMLOG_LEDGER)] = True
        t = torch.where(sl, symlog(x), x)
        ph = torch.remainder(torch.div(ledger[:, LG["sim_cycle"]].round().long(), 4, rounding_mode="floor"), 5)
        return torch.cat([((t - self.ledger_mean) / self.ledger_std).float(), F.one_hot(ph, 5).float()], dim=1)

    def cond_input(self, state: State, act: torch.Tensor, raster: Optional[torch.Tensor] = None) -> torch.Tensor:
        ns = self.norm_scalars(state["scalars"])[:, list(COND_SCALARS)]
        parts = [ns, month_features(state["scalars"][:, SC_TIME]), act.float()]
        if self.cfg.spend_features:
            if raster is None:
                raise ValueError("this model conditions on attempted spend: pass the action raster")
            parts.append(self.spend_features(state, raster))
        if self.cfg.ledger:
            parts.append(self.norm_ledger(state["ledger"]))
        return torch.cat(parts, dim=1)

    def scalar_delta_feats(self, s0: State, s1: State) -> torch.Tensor:
        d = (s1["scalars"].double() - s0["scalars"].double()) / self.delta_scale
        out = [symlog(d).float()]
        if self.cfg.ledger:
            out.append(symlog((s1["ledger"].double() - s0["ledger"].double()) / self.ledger_delta_scale).float())
        return torch.cat(out, dim=1)

    # -- dense pass ------------------------------------------------------------------------------
    def _dense(self, state: State, raster: torch.Tensor, cond_in: torch.Tensor, z: torch.Tensor):
        cond = self.cond_mlp(torch.cat([cond_in, z.to(cond_in.dtype)], dim=1))
        if self.cfg.ledger:
            out = self._trunk_fn(state["tile_index"], state["flags"], state["power"], state["half"],
                                 state["eighth"], raster, cond, state["terrain"], state["com_rate"])
        else:
            out = self._trunk_fn(state["tile_index"], state["flags"], state["power"], state["half"],
                                 state["eighth"], raster, cond)
        return (*out, cond_in)

    def _cat_logits(self, feat: torch.Tensor, cur_idx: torch.Tensor) -> torch.Tensor:
        """feat (N, d0), cur_idx (N,) -> (N, 1024) float32 logits with the current code masked."""
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=feat.is_cuda):
            h = torch.cat([feat, self.trunk.tile_emb(cur_idx).to(feat.dtype)], dim=-1)
            lg = self.cat_head(h).float()
        return lg.scatter(1, cur_idx.unsqueeze(1), float("-inf"))

    def _new_flag_logits(self, feat: torch.Tensor, new_idx: torch.Tensor) -> torch.Tensor:
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=feat.is_cuda):
            return self.new_flag_lin(feat).float() + self.new_flag_emb(new_idx).float()

    # -- likelihood ------------------------------------------------------------------------------
    def _split_overlay(self, par: torch.Tensor, n_ch: int):
        k = self.cfg.k_mix_overlay
        par = par.float().unflatten(-1, (n_ch, 1 + 3 * k))           # (B,h,w,C,1+3k)
        gate = par[..., 0]
        lpi, dmu, ls = par[..., 1:1 + k], par[..., 1 + k:1 + 2 * k], par[..., 1 + 2 * k:]
        return gate, lpi, 16.0 * dmu, ls.clamp(-4.0, 6.0) + 1.0

    def _scalar_dist(self, pooled: torch.Tensor, s0: State, s1: State, raster: torch.Tensor,
                     cond_in: Optional[torch.Tensor] = None):
        """Scalar change distribution: from pooled trunk features (pooled mode) or the second stage given
        the next spatial state ``s1`` (teacher-forced in training, sampled in rollouts)."""
        if self.cfg.scalar_stage == "pooled":
            # pilots 1 and 2 trained this head inside the trunk, under bf16 autocast: keep those numerics
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=pooled.is_cuda):
                par = self.trunk.head_scalar(pooled)
            return self._split_scalar(par)
        state_x, direct = self.stage_inputs(s0)
        par, skip = self.scalar_stage(pooled, s0, s1, raster, self.spend_cost, cond_in, state_x, direct)
        return self._split_scalar(par, skip)

    def stage_inputs(self, s0: State):
        """Second-stage inputs from the current state (ledger models): raw scalars and ledger in units of
        their delta scales (for the learned linear path) and their normalised features (direct input)."""
        if not self.cfg.ledger:
            return None, None
        state_x = torch.cat([s0["scalars"].double() / self.delta_scale,
                             s0["ledger"].double() / self.ledger_delta_scale], dim=1).float()
        direct = torch.cat([self.norm_scalars(s0["scalars"])[:, list(COND_SCALARS)],
                            self.norm_ledger(s0["ledger"])], dim=1)
        return state_x, direct

    def target_delta_scale(self) -> torch.Tensor:
        if self.cfg.bookkeeping:
            return torch.cat([self.delta_scale[list(STAGE2_SCALARS)].float(), self.cost_scale.float().view(1)])
        D = self.delta_scale[list(LEARNED_SCALARS)].float()
        if self.cfg.ledger:
            D = torch.cat([D, self.ledger_delta_scale[list(LEARNED_LEDGER)].float()])
        return D

    def bk_delta_scale(self) -> torch.Tensor:
        return torch.cat([self.delta_scale[list(STAGE3_SCALARS)].float(), self.ledger_delta_scale[list(LEARNED_LEDGER)].float()])

    def listed_spend(self, raster: torch.Tensor) -> torch.Tensor:
        """(B, 15) listed price per tool channel: raster tiles x engine unit cost per tile."""
        return raster.float().sum(dim=(2, 3)).double() * self.spend_cost.double()

    def bk_dist_from_raw(self, raw: torch.Tensor, act: torch.Tensor, city_time: torch.Tensor):
        par = self.bk(raw, act, month_features(city_time))
        ks = self.cfg.k_mix_scalar
        D = self.bk_delta_scale()
        par = par.float().unflatten(-1, (D.shape[0], 1 + 3 * ks))
        gate, lpi = par[..., 0], par[..., 1:1 + ks]
        mu = par[..., 1 + ks:1 + 2 * ks] * D[:, None]
        ls = par[..., 1 + 2 * ks:].clamp(-9.0, 6.0) + torch.log(D)[:, None]
        return gate, lpi, mu, ls

    def bk_targets(self, s0: State, s1: State) -> torch.Tensor:
        """(B, 33) one-month changes of the third stage's targets."""
        d = s1["scalars"][:, list(STAGE3_SCALARS)].double() - s0["scalars"][:, list(STAGE3_SCALARS)].double()
        dl = s1["ledger"][:, list(LEARNED_LEDGER)].double() - s0["ledger"][:, list(LEARNED_LEDGER)].double()
        return torch.cat([d, dl], dim=1).float()

    @staticmethod
    def s2_current(s0: State) -> torch.Tensor:
        """(B, 9) current values of the second stage's targets (third-stage models): the census
        scalars and 0 for the month's charged build cost, which is a level, not a change."""
        cur = s0["scalars"][:, list(STAGE2_SCALARS)].double()
        return torch.cat([cur, torch.zeros_like(cur[:, :1])], dim=1)

    @staticmethod
    def bk_current(raw: torch.Tensor) -> torch.Tensor:
        """(B, 33) current values of the third stage's targets, read from its raw inputs (columns 0..19
        are the current scalars and 20..46 the current ledger, see ``bk_raw``)."""
        return torch.cat([raw[:, list(STAGE3_SCALARS)], raw[:, [NUM_SCALARS + i for i in LEARNED_LEDGER]]], dim=1)

    def bk_logp(self, raw, act, city_time, d) -> torch.Tensor:
        """(B, 33) log-probabilities of the third stage's targets given its raw inputs (censored at the
        engine's bounds, see ``BOUND_SOURCES``)."""
        gate, lpi, mu, ls = self.bk_dist_from_raw(raw, act, city_time)
        lo_d, hi_d = censor_limits(self.bk_current(raw), BK_BOUNDS)
        lp = dlogistic_mix_logp(d, lpi, mu, ls, lo_d, hi_d)
        return gated_logp(d, torch.zeros_like(d), gate, lp)

    def _split_scalar(self, par: torch.Tensor, skip: Optional[torch.Tensor] = None):
        ks = self.cfg.k_mix_scalar
        D = self.target_delta_scale() if self.cfg.scalar_stage == "twostage" else self.delta_scale[list(LEARNED_SCALARS)].float()
        par = par.float().unflatten(-1, (D.shape[0], 1 + 3 * ks))
        gate = par[..., 0]
        lpi = par[..., 1:1 + ks]
        mu = par[..., 1 + ks:1 + 2 * ks] * D[:, None]
        if skip is not None:
            mu = mu + (skip.float() * D).unsqueeze(-1)
        ls = par[..., 1 + 2 * ks:].clamp(-9.0, 6.0) + torch.log(D)[:, None]
        return gate, lpi, mu, ls

    def _overlay_logp(self, par, cur, nxt, lo, hi, n_ch):
        """cur, nxt: (B,C,h,w) raw. Returns (B,) summed log p."""
        gate, lpi, dmu, ls = self._split_overlay(par, n_ch)
        c = cur.permute(0, 2, 3, 1).float()
        x = nxt.permute(0, 2, 3, 1).float()
        lo_t = torch.tensor(lo, device=c.device)
        hi_t = torch.tensor(hi, device=c.device)
        mu = c.unsqueeze(-1) + dmu
        lp = dlogistic_mix_logp(x, lpi, mu, ls, lo_t.expand_as(x), hi_t.expand_as(x))
        return gated_logp(x, c, gate, lp).sum(dim=(1, 2, 3))

    def _terms(self, dense, s0: State, s1: State, act: torch.Tensor, raster: torch.Tensor) -> Dict[str, torch.Tensor]:
        feat, dl, half_par, eighth_par, pooled, terrain_par, com_par, cond_in = dense
        B = s0["tile_index"].shape[0]
        dl = dl.float()
        i0, i1 = s0["tile_index"], s1["tile_index"]
        changed = i1 != i0
        # tile gate
        lg = dl[..., 0]
        t_gate = torch.where(changed, F.logsigmoid(lg), F.logsigmoid(-lg)).sum(dim=(1, 2))
        # tile categorical and new-code flags at changed tiles
        bi, xi, yi = changed.nonzero(as_tuple=True)
        t_cat = torch.zeros(B, device=lg.device)
        fl_logit = dl[..., 1:]                                            # (B,X,Y,6)
        if bi.numel() > 0:
            f = feat[bi, xi, yi]
            logits = self._cat_logits(f, i0[bi, xi, yi])
            lp = torch.log_softmax(logits, dim=-1).gather(1, i1[bi, xi, yi].unsqueeze(1)).squeeze(1)
            t_cat = t_cat.index_add(0, bi, lp)
            nfl = self._new_flag_logits(f, i1[bi, xi, yi])
            fl_logit = fl_logit.index_put((bi, xi, yi), nfl)
        tgt = torch.cat([s1["flags"], s1["power"].unsqueeze(1)], dim=1).permute(0, 2, 3, 1).float()
        lpf = bernoulli_logp(tgt, fl_logit)
        t_flags = lpf[..., :N_FLAGS].sum(dim=(1, 2, 3))
        t_power = lpf[..., N_FLAGS].sum(dim=(1, 2))
        t_half = self._overlay_logp(half_par, s0["half"], s1["half"], HALF_LO, HALF_HI, N_HALF)
        t_eighth = self._overlay_logp(eighth_par, s0["eighth"], s1["eighth"], EIGHTH_LO, EIGHTH_HI, N_EIGHTH)
        # scalars: learned ones over the integer change, given the next spatial state (teacher-forced)
        gate, lpi, mu, ls = self._scalar_dist(pooled, s0, s1, raster, cond_in)
        if self.cfg.bookkeeping:
            return self._terms_bk(t_gate, t_cat, t_flags, t_power, t_half, t_eighth, terrain_par, com_par, changed,
                                  gate, lpi, mu, ls, s0, s1, act, raster)
        L = list(LEARNED_SCALARS)
        cur, nxt = s0["scalars"][:, L].double(), s1["scalars"][:, L].double()
        if self.cfg.ledger:
            LL = list(LEARNED_LEDGER)
            cur = torch.cat([cur, s0["ledger"][:, LL].double()], dim=1)
            nxt = torch.cat([nxt, s1["ledger"][:, LL].double()], dim=1)
        d = (nxt - cur).float()
        lo_d, hi_d = censor_limits(cur, S2_BOUNDS_LEDGER if self.cfg.ledger else S2_BOUNDS)
        lp = dlogistic_mix_logp(d, lpi, mu, ls, lo_d, hi_d)
        t_all = gated_logp(d, torch.zeros_like(d), gate, lp)            # (B, 17 [+ 24])
        t_sc = t_all[:, :len(L)]
        out = {"tile_gate": t_gate, "tile_cat": t_cat, "flags": t_flags, "power": t_power,
               "half": t_half, "eighth": t_eighth, "scalars": t_sc.sum(1)}
        for j, i in enumerate(L):
            out["sc_" + SCALAR_NAMES[i]] = t_sc[:, j]
        if self.cfg.ledger:
            t_lg = t_all[:, len(L):]
            out["ledger"] = t_lg.sum(1)
            for j, i in enumerate(LEARNED_LEDGER):
                out["lg_" + LEDGER_NAMES[i]] = t_lg[:, j]
            out["terrain"] = self._overlay_logp(terrain_par, s0["terrain"].unsqueeze(1), s1["terrain"].unsqueeze(1),
                                                TERRAIN_LO, TERRAIN_HI, 1)
            out["com_rate"] = self._overlay_logp(com_par, s0["com_rate"].unsqueeze(1), s1["com_rate"].unsqueeze(1),
                                                 COM_RATE_LO, COM_RATE_HI, 1)
        out["n_changed"] = changed.sum(dim=(1, 2)).float()
        return out

    def _terms_bk(self, t_gate, t_cat, t_flags, t_power, t_half, t_eighth, terrain_par, com_par, changed,
                  gate, lpi, mu, ls, s0, s1, act, raster) -> Dict[str, torch.Tensor]:
        """Likelihood terms with the third stage (all teacher-forced on the engine's next state)."""
        if "build_cost" not in s1:
            raise ValueError("the third-stage model needs the month's charged build cost in the next state")
        L2 = list(STAGE2_SCALARS)
        cur2 = self.s2_current(s0)
        d2 = torch.cat([s1["scalars"][:, L2].double(), s1["build_cost"].double().view(-1, 1)], dim=1) - cur2
        d2 = d2.float()
        lo_d, hi_d = censor_limits(cur2, S2_BOUNDS_BK)
        t2 = gated_logp(d2, torch.zeros_like(d2), gate, dlogistic_mix_logp(d2, lpi, mu, ls, lo_d, hi_d))
        raw = bk_raw(s0, s1, s1["build_cost"], self.listed_spend(raster))
        t3 = self.bk_logp(raw, act, s0["scalars"][:, SC_TIME], self.bk_targets(s0, s1))
        n3 = len(STAGE3_SCALARS)
        out = {"tile_gate": t_gate, "tile_cat": t_cat, "flags": t_flags, "power": t_power, "half": t_half,
               "eighth": t_eighth, "scalars_s2": t2[:, :len(L2)].sum(1), "build_cost": t2[:, len(L2)],
               "scalars": t2[:, :len(L2)].sum(1) + t3[:, :n3].sum(1), "ledger": t3[:, n3:].sum(1), "bk": t3.sum(1)}
        for j, i in enumerate(L2):
            out["sc_" + SCALAR_NAMES[i]] = t2[:, j]
        for j, i in enumerate(STAGE3_SCALARS):
            out["sc_" + SCALAR_NAMES[i]] = t3[:, j]
        for j, i in enumerate(LEARNED_LEDGER):
            out["lg_" + LEDGER_NAMES[i]] = t3[:, n3 + j]
        out["terrain"] = self._overlay_logp(terrain_par, s0["terrain"].unsqueeze(1), s1["terrain"].unsqueeze(1),
                                            TERRAIN_LO, TERRAIN_HI, 1)
        out["com_rate"] = self._overlay_logp(com_par, s0["com_rate"].unsqueeze(1), s1["com_rate"].unsqueeze(1),
                                             COM_RATE_LO, COM_RATE_HI, 1)
        out["n_changed"] = changed.sum(dim=(1, 2)).float()
        return out

    def derived_violations(self, s0: State, act: torch.Tensor, s1: State) -> torch.Tensor:
        """(B,) number of the derived scalars (and ledger entries) that s1 does not satisfy (should be 0)."""
        d = self.derive_scalars(s0["scalars"], act, s1["scalars"].clone())
        v = (d[:, list(DERIVED_SCALARS)] != s1["scalars"][:, list(DERIVED_SCALARS)]).sum(1)
        if self.cfg.ledger:
            dl = self.derive_ledger(s0["ledger"], s1["ledger"].clone())
            v = v + (dl[:, list(DERIVED_LEDGER)] != s1["ledger"][:, list(DERIVED_LEDGER)]).sum(1)
        return v

    @staticmethod
    def derive_ledger(prev: torch.Tensor, nxt: torch.Tensor) -> torch.Tensor:
        nxt[:, LG["sim_cycle"]] = torch.remainder(prev[:, LG["sim_cycle"]] + 4, 1024)
        nxt[:, LG["initial_eval"]] = 0
        nxt[:, LG["disasters"]] = prev[:, LG["disasters"]]
        return nxt

    @staticmethod
    def derive_scalars(prev: torch.Tensor, act: torch.Tensor, nxt: torch.Tensor) -> torch.Tensor:
        nxt[:, SC_TAX] = torch.round(act[:, 0].to(nxt.dtype) * 20.0)
        nxt[:, SC_TIME] = prev[:, SC_TIME] + 4
        nxt[:, SC_POP] = 20 * (nxt[:, SC_RES_POP] + 8 * (nxt[:, SC_COM_POP] + nxt[:, SC_IND_POP]))
        return nxt

    def loss_terms(self, s0: State, raster: torch.Tensor, act: torch.Tensor, s1: State,
                   z_from_posterior: bool = True, autocast: bool = True) -> Dict[str, torch.Tensor]:
        """Per-sample log-likelihood terms (B,) and the KL of the posterior (B,).

        With ``z_from_posterior`` one z is drawn from q(z | s_t, a_t, s_t+1) (reparameterised), so
        sum(terms) - kl is a one-sample evidence lower bound on log p(s_t+1 | s_t, a_t).
        """
        B = s0["tile_index"].shape[0]
        dev = s0["tile_index"].device
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=autocast and dev.type == "cuda"):
            cond_in = self.cond_input(s0, act, raster)
            if z_from_posterior:
                mu, logvar = self.posterior(s0, s1, self.scalar_delta_feats(s0, s1), cond_in)
                z = mu + torch.exp(0.5 * logvar) * torch.randn_like(mu)
                kl = 0.5 * (mu.pow(2) + logvar.exp() - 1.0 - logvar).sum(1)
            else:
                z = torch.randn(B, self.cfg.z_dim, device=dev)
                kl = torch.zeros(B, device=dev)
                mu = logvar = None
            dense = self._dense(s0, raster, cond_in, z)
        out = self._terms(dense, s0, s1, act, raster)
        out["kl"] = kl
        out["_z"] = z.detach()
        if mu is not None:
            out["_post"] = (mu.detach(), logvar.detach())
        return out

    RECON_TERMS = ("tile_gate", "tile_cat", "flags", "power", "half", "eighth", "scalars")

    @torch.no_grad()
    def log_prob(self, batch, k_iw: int = 1) -> Dict[str, torch.Tensor]:
        """Held-out log-likelihood terms (nats, per sample, shape (B,)) for a one-step batch.

        Returns every reconstruction term (z drawn from the posterior), the KL, ``elbo`` =
        sum(terms) - kl, and, when k_iw > 1, ``iw_bound``: the importance-weighted bound with k_iw
        posterior samples, a tighter lower bound on log p(s_t+1 | s_t, a_t). Also ``derived_viol``,
        the count of derived-scalar identities the target violates (0 on engine data).
        """
        s0, raster, act, s1 = batch
        out = self.loss_terms(s0, raster, act, s1)
        rec = sum(out[k] for k in self.recon_terms)
        res = {k: v for k, v in out.items() if not k.startswith("_")}
        res["elbo"] = rec - out["kl"]
        if k_iw > 1:
            mu, logvar = out["_post"]
            ws = []
            for _ in range(k_iw):
                z = mu + torch.exp(0.5 * logvar) * torch.randn_like(mu)
                with torch.autocast("cuda", dtype=torch.bfloat16, enabled=z.is_cuda):
                    dense = self._dense(s0, raster, self.cond_input(s0, act, raster), z)
                t = self._terms(dense, s0, s1, act, raster)
                r = sum(t[k] for k in self.recon_terms)
                log_pz = (-0.5 * z.pow(2) - 0.5 * math.log(2 * math.pi)).sum(1)
                log_qz = (-0.5 * (z - mu).pow(2) / logvar.exp() - 0.5 * logvar - 0.5 * math.log(2 * math.pi)).sum(1)
                ws.append(r + log_pz - log_qz)
            res["iw_bound"] = torch.logsumexp(torch.stack(ws), 0) - math.log(k_iw)
        res["derived_viol"] = self.derived_violations(s0, act, s1).float()
        return res

    # -- sampling --------------------------------------------------------------------------------
    @torch.no_grad()
    def sample_next(self, state: State, raster: torch.Tensor, act: torch.Tensor, z: Optional[torch.Tensor] = None,
                    temperature: float = 1.0, max_batch: Optional[int] = None, overlay: str = "sample") -> State:
        """One month forward, batched, in the loader's state format.

        temperature T scales z (z ~ N(0, T^2 I) when not given), divides the gate / categorical /
        Bernoulli logits and multiplies the logistic scales. T = 0 is the deterministic mode:
        z = 0, gates at 0.5, arg-max codes, mixture centres.
        overlay: "sample" (follow T) or "mean": the eight overlays take their distribution's mean,
        (1 - g) * current + g * clamp(sum_k pi_k mu_k), unrounded, while tiles and scalars follow T.
        """
        mb = min(max_batch or self.max_batch or self.safe_batch, self.safe_batch)
        B = state["tile_index"].shape[0]
        if mb is not None and B > mb:
            outs = []
            for a in range(0, B, mb):
                sl = slice(a, min(B, a + mb))
                outs.append(self.sample_next({k: v[sl] for k, v in state.items()}, raster[sl], act[sl],
                                             None if z is None else z[sl], temperature, max_batch=mb, overlay=overlay))
            return {k: torch.cat([o[k] for o in outs]) for k in outs[0]}
        dev = state["tile_index"].device
        T = float(temperature)
        if z is None:
            z = torch.randn(B, self.cfg.z_dim, device=dev) * T
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev.type == "cuda"):
            cond_in = self.cond_input(state, act, raster)
            dense = self._dense(state, raster, cond_in, z)
        return self._sample_from_dense(dense, state, act, T, overlay, raster)

    def _bern(self, logit: torch.Tensor, T: float) -> torch.Tensor:
        if T <= 0:
            return (logit > 0).float()
        return (torch.rand_like(logit) < torch.sigmoid(logit / T)).float()

    def _sample_from_dense(self, dense, state: State, act: torch.Tensor, T: float, overlay: str = "sample",
                           raster: Optional[torch.Tensor] = None) -> State:
        feat, dl, half_par, eighth_par, pooled, terrain_par, com_par, cond_in = dense
        dl = dl.float()
        i0 = state["tile_index"]
        ch = self._bern(dl[..., 0], T).bool()
        i1 = i0.clone()
        fl_logit = dl[..., 1:]
        bi, xi, yi = ch.nonzero(as_tuple=True)
        n = bi.numel()
        if n > 0:
            new = torch.empty(n, dtype=i0.dtype, device=i0.device)
            nfl = torch.empty(n, N_FLAGS + 1, device=i0.device)
            CH = 1 << 17
            for a in range(0, n, CH):
                s = slice(a, min(n, a + CH))
                f = feat[bi[s], xi[s], yi[s]]
                lg = self._cat_logits(f, i0[bi[s], xi[s], yi[s]])
                if T <= 0:
                    new[s] = lg.argmax(-1)
                else:
                    g = -torch.log(-torch.log(torch.rand_like(lg).clamp_(1e-12, 1 - 1e-7)))
                    new[s] = (lg / T + g).argmax(-1)
                nfl[s] = self._new_flag_logits(f, new[s])
            i1[bi, xi, yi] = new
            fl_logit = fl_logit.index_put((bi, xi, yi), nfl)
        fp = self._bern(fl_logit, T)                                          # (B,X,Y,6)
        flags = fp[..., :N_FLAGS].permute(0, 3, 1, 2).contiguous()
        power = fp[..., N_FLAGS].contiguous()
        half = self._sample_overlay(half_par, state["half"], HALF_LO, HALF_HI, N_HALF, T, overlay)
        eighth = self._sample_overlay(eighth_par, state["eighth"], EIGHTH_LO, EIGHTH_HI, N_EIGHTH, T, overlay)
        # scalars (and ledger), given the sampled next spatial state
        s1 = {"tile_index": i1, "flags": flags, "power": power, "half": half, "eighth": eighth}
        if self.cfg.ledger:
            s1["terrain"] = self._sample_overlay(terrain_par, state["terrain"].unsqueeze(1), TERRAIN_LO, TERRAIN_HI,
                                                 1, T, overlay).squeeze(1)
            s1["com_rate"] = self._sample_overlay(com_par, state["com_rate"].unsqueeze(1), COM_RATE_LO, COM_RATE_HI,
                                                  1, T, overlay).squeeze(1)
        gate, lpi, mu, ls = self._scalar_dist(pooled, state, s1, raster, cond_in)
        # Censored sampling: the draw is rounded and pinned to [lo - cur, hi - cur], which is the trained
        # distribution (mass beyond a bound sits on the bound); no clamp follows.
        prev = state["scalars"].double()
        if self.cfg.bookkeeping:
            cur = self.s2_current(state)
            bounds = S2_BOUNDS_BK
        else:
            L = list(LEARNED_SCALARS)
            cur = prev[:, L]
            if self.cfg.ledger:
                cur = torch.cat([cur, state["ledger"][:, list(LEARNED_LEDGER)].double()], dim=1)
            bounds = S2_BOUNDS_LEDGER if self.cfg.ledger else S2_BOUNDS
        lo_d, hi_d = censor_limits(cur, bounds)
        d = dlogistic_mix_sample(lpi, mu, ls, lo_d, hi_d, T)
        moved = self._bern(gate, T).bool()
        d = torch.where(moved, d, torch.zeros_like(d))
        new = censored_next(cur, d, lo_d, hi_d, bounds)
        if self.cfg.bookkeeping:
            return self._sample_bk(new, s1, state, act, raster, T)
        nxt = prev.clone()
        nxt[:, L] = new[:, :len(L)]
        nxt = self.derive_scalars(prev, act.double(), nxt)
        s1["scalars"] = nxt.to(state["scalars"].dtype)
        if self.cfg.ledger:
            pl = state["ledger"].double()
            nl = pl.clone()
            nl[:, list(LEARNED_LEDGER)] = new[:, len(L):]
            nl = self.derive_ledger(pl, nl)
            s1["ledger"] = nl.to(state["ledger"].dtype)
        return s1

    def _sample_bk(self, new2, s1: State, state: State, act: torch.Tensor, raster: torch.Tensor, T: float) -> State:
        """Census and charged cost (stage 2, sampled: ``new2`` holds their next values) then the third
        stage on scalars, fed the sampled ones."""
        prev = state["scalars"].double()
        nxt = prev.clone()
        L2 = list(STAGE2_SCALARS)
        nxt[:, L2] = new2[:, :len(L2)]
        nxt = self.derive_scalars(prev, act.double(), nxt)
        cost = new2[:, len(L2)]
        s1["scalars"] = nxt.to(state["scalars"].dtype)
        s1["build_cost"] = cost.float()                 # the sampled charged cost (read by evaluations only)
        raw = bk_raw(state, s1, cost, self.listed_spend(raster))
        gate, lpi, mu, ls = self.bk_dist_from_raw(raw, act, state["scalars"][:, SC_TIME])
        cur3 = self.bk_current(raw)
        lo_d, hi_d = censor_limits(cur3, BK_BOUNDS)
        d3 = dlogistic_mix_sample(lpi, mu, ls, lo_d, hi_d, T)
        d3 = torch.where(self._bern(gate, T).bool(), d3, torch.zeros_like(d3))
        new3 = censored_next(cur3, d3, lo_d, hi_d, BK_BOUNDS)
        n3 = len(STAGE3_SCALARS)
        nxt[:, list(STAGE3_SCALARS)] = new3[:, :n3]
        nxt = self.derive_scalars(prev, act.double(), nxt)
        s1["scalars"] = nxt.to(state["scalars"].dtype)
        pl = state["ledger"].double()
        nl = pl.clone()
        nl[:, list(LEARNED_LEDGER)] = new3[:, n3:]
        s1["ledger"] = self.derive_ledger(pl, nl).to(state["ledger"].dtype)
        return s1

    def _sample_overlay(self, par, cur, lo, hi, n_ch, T, overlay: str = "sample"):
        gate, lpi, dmu, ls = self._split_overlay(par, n_ch)
        c = cur.permute(0, 2, 3, 1).float()
        lo_t = torch.tensor(lo, device=c.device).expand_as(c)
        hi_t = torch.tensor(hi, device=c.device).expand_as(c)
        if overlay == "mean":
            m = (torch.softmax(lpi, dim=-1) * (c.unsqueeze(-1) + dmu)).sum(-1)
            m = torch.maximum(torch.minimum(m, hi_t), lo_t)
            g = torch.sigmoid(gate)
            v = torch.maximum(torch.minimum((1 - g) * c + g * m, hi_t), lo_t)
            return v.permute(0, 3, 1, 2).contiguous().to(cur.dtype)
        if overlay != "sample":
            raise ValueError(f"overlay decoding {overlay!r}")
        v = dlogistic_mix_sample(lpi, c.unsqueeze(-1) + dmu, ls, lo_t, hi_t, T)
        moved = self._bern(gate, T).bool()
        v = torch.where(moved, v, c)
        return v.permute(0, 3, 1, 2).contiguous().to(cur.dtype)

    @torch.no_grad()
    def rollout(self, state0: State, raster, act: torch.Tensor, K: int = 1, temperature: float = 1.0,
                max_batch: Optional[int] = None, overlay: str = "sample"):
        """Open-loop rollout of B plans for H months with K noise samples per plan.

        Default decoding a (``dc.fidelity.DEFAULT_DECODING``): everything is sampled at ``temperature``
        (z, tiles, flags, power, overlays, scalars and ledger), so the third stage's map summary is
        computed on sampled integer overlays exactly as in training. ``overlay="mean"`` (decoding b)
        survives only for the appendix comparison.

        raster: a tensor (B, H, 15, 120, 100) of any dtype, or a callable h -> (B, 15, 120, 100);
        act: (B, H, 11). Returns (scalars (B, K, H+1, 20) float64, final states with batch B*K,
        sample k of plan b at row b*K + k).
        """
        B, H = act.shape[0], act.shape[1]
        s = {k: v.repeat_interleave(K, dim=0) for k, v in state0.items()}
        traj = torch.empty(B * K, H + 1, NUM_SCALARS, dtype=torch.float64, device=act.device)
        traj[:, 0] = s["scalars"].double()
        for h in range(H):
            r = raster(h) if callable(raster) else raster[:, h]
            r = r.to(s["flags"].dtype).repeat_interleave(K, dim=0)
            a = act[:, h].float().repeat_interleave(K, dim=0)
            s = self.sample_next(s, r, a, temperature=temperature, max_batch=max_batch, overlay=overlay)
            traj[:, h + 1] = s["scalars"].double()
        return traj.view(B, K, H + 1, NUM_SCALARS), s


# ----------------------------------------------------------------------------------------------
# Normalisation statistics
# ----------------------------------------------------------------------------------------------
@torch.no_grad()
def compute_norm_stats(batches, max_batches: int = 200) -> Dict[str, torch.Tensor]:
    """Scalar statistics from any iterator of one-step batches (state_t, raster, act, state_t+1).

    cond_mean / cond_std: mean and standard deviation of the transformed scalars of state_t
    (symmetric log for SYMLOG_SCALARS, identity otherwise; std floored at 1e-3, 1 if constant).
    delta_scale: per scalar, the 90th percentile of |one-month change| over transitions where it
    changed (1 if it never changes), used as the unit of the scalar heads.
    n: the number of transitions used.
    """
    xs, ds, xl, dl, costs = [], [], [], [], []
    for k, (s0, _r, _a, s1) in enumerate(batches):
        if k >= max_batches:
            break
        xs.append(s0["scalars"].double().cpu())
        ds.append((s1["scalars"].double() - s0["scalars"].double()).cpu())
        if "build_cost" in s1:
            costs.append(s1["build_cost"].double().cpu())
        if "ledger" in s0:
            xl.append(s0["ledger"].double().cpu())
            dl.append((s1["ledger"].double() - s0["ledger"].double()).cpu())
    X = torch.cat(xs)
    D = torch.cat(ds)
    sl = torch.zeros(NUM_SCALARS, dtype=torch.bool)
    sl[list(SYMLOG_SCALARS)] = True
    T = torch.where(sl, symlog(X), X)
    mean = T.mean(0)
    std = T.std(0)
    std = torch.where(std < 1e-3, torch.ones_like(std), std)
    dscale = torch.ones(NUM_SCALARS, dtype=torch.float64)
    for i in range(NUM_SCALARS):
        nz = D[:, i][D[:, i] != 0].abs()
        if nz.numel() > 0:
            dscale[i] = max(1.0, float(torch.quantile(nz, 0.9)))
    out = {"cond_mean": mean, "cond_std": std, "delta_scale": dscale, "n": torch.tensor(X.shape[0])}
    if costs:
        cst = torch.cat(costs)
        nz = cst[cst > 0]
        out["cost_scale"] = torch.tensor(max(1.0, float(torch.quantile(nz, 0.9))) if nz.numel() else 1.0, dtype=torch.float64)
    if xl:
        XL, DL = torch.cat(xl), torch.cat(dl)
        sl = torch.zeros(NUM_LEDGER, dtype=torch.bool)
        sl[list(SYMLOG_LEDGER)] = True
        TL = torch.where(sl, symlog(XL), XL)
        lstd = TL.std(0)
        out["ledger_mean"] = TL.mean(0)
        out["ledger_std"] = torch.where(lstd < 1e-3, torch.ones_like(lstd), lstd)
        lds = torch.ones(NUM_LEDGER, dtype=torch.float64)
        for i in range(NUM_LEDGER):
            nz = DL[:, i][DL[:, i] != 0].abs()
            if nz.numel() > 0:
                lds[i] = max(1.0, float(torch.quantile(nz, 0.9)))
        out["ledger_delta_scale"] = lds
    return out


def set_numerics() -> None:
    """The numerics every training run and every evaluation uses (fixed before the ladder): the trunk
    and its dense heads under bf16 autocast; the sparse heads (tile categorical, new-code flags) under
    bf16 autocast with float32 logits; every distribution computation (likelihoods, sampling) and the
    whole second stage in float32; TF32 allowed for float32 matmuls and convolutions; cuDNN autotuning on."""
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True


def build(size: str, device="cpu") -> Emulator:
    m = Emulator(size).to(device)
    if torch.device(device).type == "cuda":
        m = m.to(memory_format=torch.channels_last)
    return m
