"""Mechanism attribution by oracle patching (study protocol section 1, mechanism claim; section 6).

A plan is *accepted-but-rejected* when the emulator accepts it (at least 4 of 8 sampled rollouts satisfy the
task; the audit record's ``grader_p``) and the engine's oracle rejects it (the record's ``oracle_accept``). For
each such plan the emulator's rollout is run again with one subsystem's entries of the state overwritten, after
every month's step, by the values the real engine had at that month under the same plan; everything else is
predicted as usual and the next step starts from the patched state. If the emulator's verdict on the patched
rollouts (8 samples, accepted at 4 of 8) is rejection, that subsystem's error was necessary for the false
acceptance.

Engine values. The plan's effective form (``dc.audit.effective``: the task's forced events written in) is
replayed by ``dc.oracle.replay(..., record="full")`` on the instance's oracle seeds 0..K-1
(``dc.tasks.oracle_seeds``); patched sample k takes its values from oracle seed k. The states are converted to
the emulator's state format by the model revision's own ``train.obs_to_numpy`` / ``numpy_to_state`` (the audit
judge's conversion of the start state), with the oracle's ledger rows, and the engine's charged build cost of
month t (``Replay.build_cost[t]``) is the state's ``build_cost`` at month t+1.

Patching (``patched_rollout_batch``; one plan and one mask: ``patched_rollout``). The model revision's own
``sample_next`` is stepped month by month, exactly as its ``rollout`` steps it (same batch layout: sample k of unit
u at row u*K + k; same raster and action scalars as ``dc.audit.emulator_rollout``; the decoding is the defaults of
the model's ``rollout``, which is what the audit uses). After step h the mask's entries of the state are replaced
by the engine's at month h+1 and the scalars (and build cost and ledger) of the patched state are recorded. The
start state is not patched (it is the engine's month-0 state; tested). With an empty mask the function is the
audit judge's rollout: element for element under the same seed and batch layout (tested); with the full mask every
month's state is the engine's (tested). The random generator of the controls is numpy's, so the torch stream the
model draws from is untouched.

Masks (``SUBSYSTEMS``, entries of ``dc.model``'s state dictionary; ``mask_table`` prints them):

  global  power        flags[:, 4] (PWRBIT, the powered flag plane, 120 x 100), power (the power-grid map,
                       120 x 100), scalars powered_zones and unpowered_zones
          treasury     scalars funds, tax_fund, road_spend, fire_spend, police_spend
          valves       scalars res_valve, com_valve, ind_valve
  local   zone_growth  tile_index on the cells whose engine tile code at that month is a zone tile, ZONE_CODES
          pollution    half[:, 2]
          traffic      half[:, 1] and tile_index on the cells whose engine tile code at that month is a road tile,
                       ROAD_CODES (the code carries the traffic level)
          land_value   half[:, 3]
          crime        half[:, 4]
          fire         eighth[:, 1] (fire coverage) and tile_index on the cells whose engine tile code at that
                       month is a fire tile, FIRE_CODES

Cell rules read the engine's tile code at that month (and that seed) only: a cell the emulator turned into a zone,
road or fire tile where the engine has none is not overwritten. Option (off unless the mask is named; the specification,
the analysis plan): ``fire_sym`` (``SYMMETRIC``), the fire patch with a symmetric cell rule: eighth[:, 1] and
tile_index on the cells where the engine's tile code *or the emulator's own sampled tile code* at that month is a
fire tile (the union of both sides' fire cells), written with the engine's tile there; ``zone_growth_sym`` likewise,
tile_index on the union of both sides' zone cells (ZONE_CODES). Their controls (``random~<name>``,
``changed~<name>``) follow the rules below, the size-matched one taking its size per class, month and sample from
its subject's own unit in the same call (a symmetric mask's size depends on that unit's rollout).
``run_mask_names`` and every other mask are unchanged. Pairs: the union of two global masks. Controls
(``control_mask``), one of each kind for every subsystem and pair, drawn class by class from entries of the same kind
(``CLASSES``: the 20 scalars; full-resolution map cells of tile_index, the five flag planes and the power map;
half-resolution overlay cells; eighth-resolution overlay cells) with one permutation per class per plan (seeded):
``random~S`` (matched on size) overwrites the first n entries of the permutation at a month where S overwrites n
entries of that class (a subsystem whose size varies by month and seed has a nested control of the same size at every
month and seed); ``changed~S`` (matched on entries changed, amendment 5) overwrites, among the entries of that class
where its own rollout differs from the engine's at that month, the m of lowest rank, m being the number of entries S's
own patch changes at that month in the same call (all of them if fewer differ). ``none`` (the empty mask, the same
rollout re-drawn: the verdict's own noise) is run beside them.

Direct and indirect. ``predicate_reads(task)`` finds the scalar columns ``dc.tasks.margin`` reads by perturbing one
entry at a time; a (task, mask) pair is *direct* when the mask overwrites any of them (for a control: in any month
or sample), otherwise indirect.

Treasury identity (``treasury_identity``). Money moves in the engine only through tool calls (the charged build
cost) and the yearly budget (``collectTax`` when cityTime is a multiple of 48, simulate.cpp:206, which runs in the
month whose start city_time is 44 mod 48). Form A, as protocol: funds[t+1] = funds[t] - build_cost[t] +
[budget month] (tax_fund[t+1] - road_spend[t+1] - fire_spend[t+1] - police_spend[t+1]). Form B, the engine's
accounting: in a budget month with auto-budget on after it, the money paid is sum_i (int)(fund_i * level_i)
(budget.cpp:118-120, 296-306), with fund_i the ledger's road_fund, fire_fund, police_fund at t+1 and level_i the
month's funding levels; the reported spends are then the requested funds, not what was paid. Otherwise form A.
Form B is primary, form A beside it (amendment 5). The secondary claim's measure (``created_share``): per trajectory,
the cumulative signed residual over the H months (money the emulator created) as a share of the starting treasury;
*breached* above 5 per cent, with 1 and 10 per cent beside it (``MATERIAL_SHARES``).

Goodhart types and matched interventions: not built here (``goodhart_type``, ``matched_intervention``).
"""

from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import tasks as T
from .engine import (LG, NUM_LEDGER, NUM_SCALARS, SC_COM_VALVE, SC_FIRE_SPEND, SC_FUNDS, SC_IND_VALVE,
                     SC_POLICE_SPEND, SC_POWERED, SC_RES_VALVE, SC_ROAD_SPEND, SC_TAX_FUND, SC_TIME, SC_UNPOWERED,
                     SCALAR_NAMES, WORLD_H, WORLD_H_2, WORLD_H_8, WORLD_W, WORLD_W_2, WORLD_W_8)
from .grammar import N_COLS, action_scalars_batch, compile_plan, raster_batch
from .seeds import seed_for

PATCHING_VERSION = 1
K_PATCH = 8                      # samples per verdict (dc.audit.K_VERDICT); sample k takes oracle seed k

# Tile codes (engine/src/micropolis.h). Inclusive ranges of the low 10 bits of a tile word.
ZONE_CODES = (240, 692)   # RESBASE (240, :523) to the last industrial tile (684--692, :578; PORTBASE = 693, :583):
                          # residential incl. hospital 405-413 (:532) and church 414-422 (:535), commercial from
                          # COMBASE 423 (:542), industrial from INDBASE 612 (:552). Seaport, airport, power plants,
                          # stations and stadiums are placed by tools, not grown, and are outside the range.
ROAD_CODES = (64, 206)    # ROADBASE = HBRIDGE (64, :442-443) to LASTROAD (206, :476): bridges, roads at no, light
                          # and heavy traffic, road-power crossings
FIRE_CODES = (56, 63)     # FIRE = FIREBASE (56, :438) to LASTFIRE (63, :440)
CELL_RULES = {"zone": ZONE_CODES, "road": ROAD_CODES, "fire": FIRE_CODES}

# Entry layout of the emulator's state (dc.model State; dc.train.numpy_to_state). Channel count or None.
MAP_KEYS = {"tile_index": None, "flags": 5, "power": None, "half": 5, "eighth": 3, "terrain": None, "com_rate": None}
MAP_SHAPES = {"tile_index": (WORLD_W, WORLD_H), "flags": (5, WORLD_W, WORLD_H), "power": (WORLD_W, WORLD_H),
              "half": (5, WORLD_W_2, WORLD_H_2), "eighth": (3, WORLD_W_8, WORLD_H_8), "terrain": (30, 25),
              "com_rate": (WORLD_W_8, WORLD_H_8)}
VEC_KEYS = {"scalars": NUM_SCALARS, "ledger": NUM_LEDGER}
COST_KEY = "build_cost"
ALL_KEYS = tuple(MAP_KEYS) + tuple(VEC_KEYS) + (COST_KEY,)

# Kinds of entries for the random controls: class -> planes (state key, channel or None), in flattening order.
CLASSES: Dict[str, Tuple[Tuple[str, Optional[int]], ...]] = {
    "scalar": (("scalars", None),),
    "full": (("tile_index", None),) + tuple(("flags", c) for c in range(5)) + (("power", None),),
    "half": tuple(("half", c) for c in range(5)),
    "eighth": tuple(("eighth", c) for c in range(3)),
}
CLASS_OF = {"scalars": "scalar", "tile_index": "full", "flags": "full", "power": "full", "half": "half",
            "eighth": "eighth"}


def _plane_size(key: str) -> int:
    if key == "scalars":
        return NUM_SCALARS
    s = MAP_SHAPES[key]
    return int(np.prod(s[1:] if MAP_KEYS[key] else s))


CLASS_SIZE = {c: sum(_plane_size(k) for k, _ in planes) for c, planes in CLASSES.items()}


# ----------------------------------------------------------------------------------------------
# Masks
# ----------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Part:
    """Entries of one state key: ``index`` = channels (flags, half, eighth) or columns (scalars, ledger), None for
    all; ``cells`` = None for every cell, or a name in ``CELL_RULES``: the cells whose engine tile code at that
    month lies in that range (tile_index only). ``both``: the cells whose engine tile code or whose emulator tile
    code (the unit's own sampled state at that month, before the patch) lies in the range (the symmetric rule)."""

    key: str
    index: Optional[Tuple[int, ...]] = None
    cells: Optional[str] = None
    both: bool = False

    def __post_init__(self) -> None:
        if self.key not in ALL_KEYS:
            raise ValueError(f"unknown state key {self.key!r}")
        if self.cells is not None and (self.cells not in CELL_RULES or self.key != "tile_index"):
            raise ValueError(f"cell rule {self.cells!r} on {self.key!r}")
        if self.index is not None and self.key not in ("flags", "half", "eighth", "scalars", "ledger"):
            raise ValueError(f"{self.key!r} has no channels")
        if self.both and self.cells is None:
            raise ValueError("the symmetric rule ('both') needs a cell rule")


@dataclass(frozen=True)
class Mask:
    """The state entries a patched rollout overwrites. ``full``: every entry of every key. ``like``: a random
    control for that subsystem or pair, drawn with ``seed`` (``control_mask``): ``match="size"`` overwrites as many
    entries per class as the subsystem's mask does; ``match="changed"`` overwrites, among entries of each class that
    differ from the engine's at that month, as many as the subsystem's own patch changes at that month (its unit must
    be in the same batched call)."""

    name: str
    parts: Tuple[Part, ...] = ()
    full: bool = False
    like: Optional[str] = None
    seed: Optional[int] = None
    match: Optional[str] = None

    @property
    def empty(self) -> bool:
        return not self.parts and not self.full and self.like is None

    @property
    def reads_rollout(self) -> bool:
        """Its entries depend on the unit's own sampled state (a symmetric cell rule)."""
        return any(p.both for p in self.parts)


def _sc(*idx) -> Tuple[int, ...]:
    return tuple(int(i) for i in idx)


SUBSYSTEMS: Dict[str, Mask] = {
    "power": Mask("power", (Part("flags", (4,)), Part("power"), Part("scalars", _sc(SC_POWERED, SC_UNPOWERED)))),
    "treasury": Mask("treasury", (Part("scalars", _sc(SC_FUNDS, SC_TAX_FUND, SC_ROAD_SPEND, SC_FIRE_SPEND,
                                                      SC_POLICE_SPEND)),)),
    "valves": Mask("valves", (Part("scalars", _sc(SC_RES_VALVE, SC_COM_VALVE, SC_IND_VALVE)),)),
    "zone_growth": Mask("zone_growth", (Part("tile_index", cells="zone"),)),
    "pollution": Mask("pollution", (Part("half", (2,)),)),
    "traffic": Mask("traffic", (Part("half", (1,)), Part("tile_index", cells="road"))),
    "land_value": Mask("land_value", (Part("half", (3,)),)),
    "crime": Mask("crime", (Part("half", (4,)),)),
    "fire": Mask("fire", (Part("eighth", (1,)), Part("tile_index", cells="fire"))),
}
GLOBAL = ("power", "treasury", "valves")
LOCAL = ("zone_growth", "pollution", "traffic", "land_value", "crime", "fire")
PAIRS = (("power", "treasury"), ("power", "valves"), ("treasury", "valves"))
NONE = Mask("none")
FULL = Mask("full", full=True)
# Optional masks, used only when named (not in run_mask_names): the two cell-rule subsystems with the symmetric cell
# rule (the union of the engine's and the unit's own cells of that rule), and the overlay-only ("indirect") fire mask
# that patches only the eighth-resolution fire_coverage overlay channel (leaving tile_index, flags, power, half and
# scalars untouched).
SYMMETRIC: Dict[str, Mask] = {
    "fire_sym": Mask("fire_sym", (Part("eighth", (1,)), Part("tile_index", cells="fire", both=True))),
    "zone_growth_sym": Mask("zone_growth_sym", (Part("tile_index", cells="zone", both=True),)),
}
OVERLAY_ONLY: Dict[str, Mask] = {
    "fire_overlay": Mask("fire_overlay", (Part("eighth", (1,)),)),
}
SYMMETRIC_FIRE_MASKS = ("fire_sym", "random~fire_sym", "changed~fire_sym")
SYMMETRIC_ZONE_MASKS = ("zone_growth_sym", "random~zone_growth_sym", "changed~zone_growth_sym")
INDIRECT_FIRE_MASKS = ("fire_overlay", "random~fire_overlay", "changed~fire_overlay")


def pair_mask(a: str, b: str) -> Mask:
    return Mask(f"{a}+{b}", SUBSYSTEMS[a].parts + SUBSYSTEMS[b].parts)


def named_mask(name: str) -> Mask:
    """A subsystem, an optional mask (``SYMMETRIC``, ``OVERLAY_ONLY``) or a pair of subsystems ("a+b") by name."""
    if name in SUBSYSTEMS:
        return SUBSYSTEMS[name]
    if name in SYMMETRIC:
        return SYMMETRIC[name]
    if name in OVERLAY_ONLY:
        return OVERLAY_ONLY[name]
    p = name.split("+")
    if len(p) == 2 and all(x in SUBSYSTEMS for x in p):
        return pair_mask(*p)
    raise ValueError(f"unknown subsystem or pair {name!r}")


CONTROL_PREFIX = {"size": "random~", "changed": "changed~"}


def control_mask(like: str, seed: int, match: str = "size") -> Mask:
    named_mask(like)
    return Mask(f"{CONTROL_PREFIX[match]}{like}", like=like, seed=int(seed), match=match)


def run_mask_names(symmetric_fire: bool = False, symmetric_zone: bool = False,
                   indirect_fire: bool = False) -> Tuple[str, ...]:
    """The masks of a run, in order: none, the nine subsystems, the three pairs, then for each subsystem and pair the
    size-matched control (random~) and the changed-matched control (changed~). ``symmetric_fire`` /
    ``symmetric_zone`` / ``indirect_fire`` (default off) append the symmetric fire / zone-growth / overlay-only fire
    patch and its two controls (``SYMMETRIC_FIRE_MASKS``, ``SYMMETRIC_ZONE_MASKS``, ``INDIRECT_FIRE_MASKS``)."""
    pairs = tuple(f"{a}+{b}" for a, b in PAIRS)
    subj = GLOBAL + LOCAL + pairs
    out = (("none",) + subj + tuple(f"random~{s}" for s in subj) + tuple(f"changed~{s}" for s in subj))
    return (out + (SYMMETRIC_FIRE_MASKS if symmetric_fire else ())
            + (SYMMETRIC_ZONE_MASKS if symmetric_zone else ())
            + (INDIRECT_FIRE_MASKS if indirect_fire else ()))


def plan_masks(names: Sequence[str], control_seed_keys: tuple) -> List[Mask]:
    """Masks by name. Seeds: a size-matched control ``seed_for("patching-control", *control_seed_keys, subject)``, a
    changed-matched one ``seed_for("patching-control-changed", *control_seed_keys, subject)``."""
    out = []
    for n in names:
        if n == "none":
            out.append(NONE)
        elif n == "full":
            out.append(FULL)
        elif n.startswith("random~"):
            out.append(control_mask(n[7:], seed_for("patching-control", *control_seed_keys, n[7:]), "size"))
        elif n.startswith("changed~"):
            out.append(control_mask(n[8:], seed_for("patching-control-changed", *control_seed_keys, n[8:]), "changed"))
        else:
            try:
                out.append(named_mask(n))
            except ValueError:
                raise ValueError(f"unknown mask {n!r}") from None
    return out


def mask_spec(m: Mask) -> dict:
    """A JSON description of a mask (for digests and tables)."""
    return {"name": m.name, "full": m.full, "like": m.like, "match": m.match,
            "parts": [dict({"key": p.key, "index": list(p.index) if p.index is not None else None,
                            "index_names": ([SCALAR_NAMES[i] for i in p.index] if (p.key == "scalars" and p.index)
                                            else None),
                            "cells": p.cells, "codes": list(CELL_RULES[p.cells]) if p.cells else None},
                           **({"both": True} if p.both else {})) for p in m.parts]}


def masks_digest(names: Sequence[str]) -> str:
    specs = [mask_spec(m) for m in plan_masks(names, ("digest",))]
    for s in specs:   # the controls' seeds are per plan; their rule is in the code version
        s.pop("seed", None)
    blob = json.dumps({"v": PATCHING_VERSION, "masks": specs, "cells": CELL_RULES, "classes": CLASSES},
                      sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


# ----------------------------------------------------------------------------------------------
# Resolving a mask at one month (torch)
# ----------------------------------------------------------------------------------------------
def _key_shape(key: str) -> Tuple[int, ...]:
    if key in MAP_SHAPES:
        return MAP_SHAPES[key]
    if key in VEC_KEYS:
        return (VEC_KEYS[key],)
    return ()


class Resolver:
    """A mask on a device: ``at(E_t)`` -> {state key: bool (K, *entry shape)} for the engine's month-t state E_t
    ({key: (K, *shape)}; tile codes in E_t["tile_index"]). Static parts are built once; cell rules read E_t, and a
    symmetric cell rule also the unit's own state ``cur`` ({key: (K, *shape)}; ``at(E_t, cur)``). A size-matched
    control of a mask that reads the rollout (``from_subject``) is resolved with ``at_counts`` from its subject's
    counts in the same call."""

    def __init__(self, mask: Mask, device, K: int) -> None:
        import torch
        self.torch = torch
        self.mask, self.device, self.K = mask, device, int(K)
        self.static: Dict[str, "torch.Tensor"] = {}
        self.cells: List[Part] = []
        self.inner: Optional[Resolver] = None
        self.ranks: Dict[str, "torch.Tensor"] = {}
        self.from_subject = False
        if mask.full or mask.empty:
            return
        if mask.like is not None:
            if mask.match == "size":
                self.inner = Resolver(named_mask(mask.like), device, K)
                self.from_subject = named_mask(mask.like).reads_rollout
            elif mask.match != "changed":
                raise ValueError(f"control match {mask.match!r}")
            for c, n in CLASS_SIZE.items():
                rng = np.random.default_rng(seed_for("patching-control-perm", int(mask.seed), c))
                perm = rng.permutation(n)
                rank = np.empty(n, dtype=np.int64)
                rank[perm] = np.arange(n)
                self.ranks[c] = torch.from_numpy(rank).to(device)
            return
        for p in mask.parts:
            if p.cells is not None:
                self.cells.append(p)
                continue
            sel = self.static.get(p.key)
            if sel is None:
                sel = torch.zeros(_key_shape(p.key), dtype=torch.bool, device=device)
            if p.index is None:
                sel[...] = True
            else:
                sel[list(p.index)] = True
            self.static[p.key] = sel

    def at(self, E_t: Dict[str, "torch.Tensor"], cur: Optional[Dict[str, "torch.Tensor"]] = None
           ) -> Dict[str, "torch.Tensor"]:
        torch, K = self.torch, self.K
        m = self.mask
        if m.empty:
            return {}
        if m.full:
            return {k: torch.ones(v.shape, dtype=torch.bool, device=v.device) for k, v in E_t.items()}
        if self.inner is not None:
            if self.from_subject:
                raise ValueError(f"{m.name}: its subject reads the rollout; it is resolved with at_counts")
            return self.at_counts(class_counts(self.inner.at(E_t), K))
        if m.match == "changed":
            raise ValueError(f"{m.name}: a changed-matched control is resolved with at_changed")
        out = {k: v.unsqueeze(0).expand(K, *v.shape) for k, v in self.static.items()}
        for p in self.cells:
            lo, hi = CELL_RULES[p.cells]
            code = E_t["tile_index"]
            sel = (code >= lo) & (code <= hi)
            if p.both:
                if cur is None:
                    raise ValueError(f"{m.name}: the symmetric cell rule needs the unit's own state")
                own = cur["tile_index"]
                sel = sel | ((own >= lo) & (own <= hi))
            out[p.key] = (out[p.key] | sel) if p.key in out else sel
        return out

    def at_counts(self, counts: Dict[str, "torch.Tensor"]) -> Dict[str, "torch.Tensor"]:
        """Size-matched control: per class c and sample k, the first ``counts[c][k]`` entries of this plan's
        permutation of the class."""
        out: Dict[str, "torch.Tensor"] = {}
        for c, planes in CLASSES.items():
            n = counts.get(c)
            if n is None or not bool((n > 0).any()):
                continue
            selc = self.ranks[c].unsqueeze(0) < n.unsqueeze(1)                     # (K, size of class)
            _unflatten_into(out, c, selc)
        return out

    def at_changed(self, E_t: Dict[str, "torch.Tensor"], cur: Dict[str, "torch.Tensor"],
                   target: Dict[str, "torch.Tensor"]) -> Dict[str, "torch.Tensor"]:
        """Changed-matched control at month t: per class c and sample k, among the entries of that class where this
        unit's state ``cur`` ({key: (K, *shape)}) differs from the engine's ``E_t``, the ``target[c][k]`` entries of
        lowest rank in this plan's permutation of the class (all of them if fewer differ)."""
        torch, K = self.torch, self.K
        out: Dict[str, torch.Tensor] = {}
        for c, n in target.items():
            if n is None or not bool((n > 0).any()):
                continue
            diff = torch.cat([_plane(cur, k, ch, K) != _plane(E_t, k, ch, K).to(cur[k].dtype)
                              for k, ch in CLASSES[c]], dim=1)                            # (K, size of class)
            rank = self.ranks[c].unsqueeze(0).expand(K, -1)
            big = torch.iinfo(torch.int64).max
            srt = torch.sort(torch.where(diff, rank, torch.full_like(rank, big)), dim=1).values
            nn = n.to(torch.int64).clamp(min=0, max=srt.shape[1])
            thr = srt.gather(1, (nn - 1).clamp(min=0).unsqueeze(1)).squeeze(1)
            thr = torch.where(nn > 0, thr, torch.full_like(thr, -1))
            _unflatten_into(out, c, diff & (rank <= thr.unsqueeze(1)))
        return out


def _plane(d: Dict[str, "torch.Tensor"], key: str, ch: Optional[int], K: int):
    """One plane of a class, flattened to (K, n)."""
    v = d[key]
    if ch is not None:
        v = v[:, ch]
    return v.reshape(K, -1)


def _unflatten_into(out: dict, c: str, selc) -> None:
    """Class-flat selections (K, n) -> per-key selections, OR-ed into ``out``."""
    torch = __import__("torch")
    K = selc.shape[0]
    a = 0
    for key, ch in CLASSES[c]:
        n = _plane_size(key)
        part = selc[:, a:a + n]
        a += n
        if key == "scalars":
            sel = part
        elif ch is None:
            sel = part.reshape(K, *MAP_SHAPES[key])
        else:
            full = torch.zeros((K,) + MAP_SHAPES[key], dtype=torch.bool, device=selc.device)
            full[:, ch] = part.reshape(K, *MAP_SHAPES[key][1:])
            sel = full
        out[key] = (out[key] | sel) if key in out else sel


def class_counts(sel: Dict[str, "torch.Tensor"], K: int) -> Dict[str, "torch.Tensor"]:
    """Entries a resolved mask overwrites, per class and sample: {class: (K,) int64}."""
    out = {}
    for key, s in sel.items():
        c = CLASS_OF.get(key)
        if c is None:
            continue
        n = s.reshape(K, -1).sum(1)
        out[c] = out[c] + n if c in out else n
    return out


# ----------------------------------------------------------------------------------------------
# Engine values
# ----------------------------------------------------------------------------------------------
_W_ENG = None


def _engine():
    global _W_ENG
    if _W_ENG is None:
        from .engine import Engine
        _W_ENG = Engine()
    return _W_ENG


def replay_job(args):
    """(cty, effective plan bytes, H, seed, record) -> (scalars int64 (H+1, 20), build_cost int64 (H,), ledger int64
    (H+1, 27), states list of H+1 Obs or None). The engine only through dc.oracle.replay."""
    from .oracle import replay
    cty, pb, H, seed, record = args
    plan = np.frombuffer(pb, dtype=np.int16).reshape(H, N_COLS)
    acts, forced = compile_plan(plan)
    rp = replay(_engine(), cty, acts, int(seed), forced=forced or None, record=record)
    return rp.scalars, rp.build_cost, rp.ledger, rp.states


def engine_state_tensors(results, Tr, device) -> Dict[str, "torch.Tensor"]:
    """Full replays on K seeds (``replay_job`` results with states) -> {key: (K, H+1, *shape)} in the emulator's
    state format (the model revision's ``obs_to_numpy`` with the oracle's ledger rows, then ``numpy_to_state``),
    plus "build_cost": (K, H) float32, the engine's charged cost of month t (the state's build_cost at t+1)."""
    import torch
    per = []
    for scal, cost, led, states in results:
        if states is None:
            raise ValueError("engine values need full replays (record='full')")
        d = Tr.obs_to_numpy(states, ledger=led)
        per.append(Tr.numpy_to_state(d, device))
    out = {k: torch.stack([p[k] for p in per]) for k in per[0]}
    out[COST_KEY] = torch.tensor(np.stack([r[1] for r in results]), dtype=torch.float32, device=device)
    return out


def engine_at(E: Dict[str, "torch.Tensor"], t: int) -> Dict[str, "torch.Tensor"]:
    """The engine's states at month t, {key: (K, *shape)}; build_cost only for t >= 1."""
    out = {k: v[:, t] for k, v in E.items() if k != COST_KEY}
    if t >= 1 and COST_KEY in E:
        out[COST_KEY] = E[COST_KEY][:, t - 1]
    return out


# ----------------------------------------------------------------------------------------------
# The patched rollout
# ----------------------------------------------------------------------------------------------
def rollout_decoding(model) -> dict:
    """The decoding the audit uses: the defaults of the model revision's ``rollout``."""
    prm = inspect.signature(model.rollout).parameters
    return {k: prm[k].default for k in ("temperature", "overlay") if k in prm}


@dataclass
class Patched:
    scalars: np.ndarray                        # (U, K, H+1, 20) float64, the patched state's scalars per month
    build_cost: Optional[np.ndarray]           # (U, K, H) float64, the state's build_cost after month t's step
    ledger: Optional[np.ndarray]               # (U, K, H+1, 27) float64
    counts: List[Dict[str, np.ndarray]]        # per unit: {class: (H, K) int} entries overwritten at months 1..H
    scalar_cols: List[np.ndarray]              # per unit: (20,) bool, scalar columns overwritten in any month/sample
    states: Optional[List[dict]] = None        # keep_states: H+1 dicts {key: (U*K, ...) CPU tensor}
    month_steps: int = 0                       # rows x months stepped (with padding)
    changed: Optional[List[Dict[str, np.ndarray]]] = None   # per unit: {class: (H, K)} overwritten entries whose
                                                            # sampled value differed from the engine's
    targets: Optional[List[Dict[str, np.ndarray]]] = None   # per unit: {class: (H, K)} a changed-matched control's
                                                            # target (its subject's changed count); 0 elsewhere


def patched_rollout_batch(model, state0: dict, plans: np.ndarray, engines: Sequence[Optional[dict]],
                          masks: Sequence[Mask], K: int = K_PATCH, *, seed: Optional[int] = None,
                          pad_rows: Optional[int] = None, max_batch: Optional[int] = None,
                          keep_states: bool = False) -> Patched:
    """Units u = 0..U-1, each an effective plan ``plans[u]`` (H, 25) with its engine values ``engines[u]``
    (``engine_state_tensors``; None only for an empty mask) and mask ``masks[u]``; K samples per unit at rows
    u*K + k. ``seed``: ``torch.manual_seed`` right before the first step (None: the caller's stream).
    ``pad_rows``: pad with copies of the last unit to this many rows (the audit judge's bucket padding).
    ``max_batch``: passed to ``sample_next`` (default: the number of rows)."""
    import torch
    P = np.ascontiguousarray(np.asarray(plans), dtype=np.int16)
    if P.ndim != 3 or P.shape[2] != N_COLS:
        raise ValueError(f"plans of shape {P.shape}")
    U, H = P.shape[0], P.shape[1]
    if len(masks) != U or len(engines) != U:
        raise ValueError("one mask and one engine entry per plan")
    masks, engines = list(masks), list(engines)
    for m, e in zip(masks, engines):
        if e is None and not m.empty:
            raise ValueError(f"mask {m.name!r} needs the engine's values")
    Up = U
    if pad_rows is not None:
        if pad_rows % K or pad_rows < U * K:
            raise ValueError(f"pad_rows {pad_rows} must be a multiple of K = {K} and at least {U * K}")
        Up = pad_rows // K
        if Up > U:
            P = np.concatenate([P, np.repeat(P[-1:], Up - U, axis=0)])
            masks += [masks[-1]] * (Up - U)
            engines += [engines[-1]] * (Up - U)
    dev = state0["tile_index"].device
    on_card = dev.type == "cuda"
    R = Up * K
    dec = rollout_decoding(model)
    act = torch.from_numpy(action_scalars_batch(P.reshape(-1, N_COLS)).reshape(Up, H, -1)).to(dev)

    def raster(h):            # exactly dc.audit.emulator_rollout's raster
        if on_card:
            from . import fast
            return fast.raster_rows(P[:, h], dev)
        return torch.from_numpy(raster_batch(P[:, h])).to(dev, non_blocking=True)

    res = [Resolver(m, dev, K) for m in masks]
    patching = any(not m.empty for m in masks)
    s0 = {k: v.expand(Up, *v.shape[1:]) for k, v in state0.items()}
    s = {k: v.repeat_interleave(K, dim=0) for k, v in s0.items()}
    traj = torch.empty(R, H + 1, NUM_SCALARS, dtype=torch.float64, device=dev)
    traj[:, 0] = s["scalars"].double()
    led = None
    if "ledger" in s:
        led = torch.empty(R, H + 1, NUM_LEDGER, dtype=torch.float64, device=dev)
        led[:, 0] = s["ledger"].double()
    cost = None
    counts = [{c: np.zeros((H, K), dtype=np.int64) for c in CLASSES} for _ in range(Up)]
    changed = [{c: np.zeros((H, K), dtype=np.int64) for c in CLASSES} for _ in range(Up)]
    targets = [{c: np.zeros((H, K), dtype=np.int64) for c in CLASSES} for _ in range(Up)]
    scols = [np.zeros(NUM_SCALARS, dtype=bool) for _ in range(Up)]
    names = {(id(e), m.name) for m, e in zip(masks, engines)}
    for m, e, rs in zip(masks, engines, res):
        if (m.match == "changed" or rs.from_subject) and (id(e), m.like) not in names:
            raise ValueError(f"{m.name}: its subject {m.like!r} must be patched in the same call on the same plan")
    kept = [{k: v.detach().cpu().clone() for k, v in s.items()}] if keep_states else None
    if seed is not None:
        torch.manual_seed(int(seed))
    mb = int(max_batch or R)
    for h in range(H):
        r = raster(h)
        r = r.to(s["flags"].dtype).repeat_interleave(K, dim=0)
        a = act[:, h].float().repeat_interleave(K, dim=0)
        s = model.sample_next(s, r, a, max_batch=mb, **dec)
        if patching:
            s = _apply(s, h + 1, engines, res, counts, scols, K, changed, targets)
        traj[:, h + 1] = s["scalars"].double()
        if led is not None:
            led[:, h + 1] = s["ledger"].double()
        if COST_KEY in s:
            if cost is None:
                cost = torch.full((R, H), float("nan"), dtype=torch.float64, device=dev)
            cost[:, h] = s[COST_KEY].double()
        if keep_states:
            kept.append({k: v.detach().cpu().clone() for k, v in s.items()})
    sc = traj.view(Up, K, H + 1, NUM_SCALARS).double().cpu().numpy()[:U]
    lg = None if led is None else led.view(Up, K, H + 1, NUM_LEDGER).cpu().numpy()[:U]
    bc = None if cost is None else cost.view(Up, K, H).cpu().numpy()[:U]
    return Patched(sc, bc, lg, counts[:U], scols[:U], kept, R * H, changed[:U], targets[:U])


def _apply(s: dict, t: int, engines: list, res: List[Resolver], counts, scols, K: int, changed=None,
           targets=None) -> dict:
    """Overwrite each unit's mask entries of the state ``s`` (rows u*K + k) by its engine's month-t values. Units with
    a changed-matched control are resolved after the others, from their subject's changed counts at this month."""
    import torch
    U = len(res)
    E_t = {}
    for u in range(U):
        e = engines[u]
        if e is not None and id(e) not in E_t:
            E_t[id(e)] = engine_at(e, t)

    def n_changed(u, sel):
        out = {}
        Eu = E_t.get(id(engines[u]))
        for key, m in sel.items():
            c = CLASS_OF.get(key)
            if c is None or key not in s:
                continue
            cur = s[key][u * K:(u + 1) * K]
            n = (m & (Eu[key].to(cur.dtype) != cur)).reshape(K, -1).sum(1)
            out[c] = out[c] + n if c in out else n
        return out

    sels: List[dict] = [{} for _ in range(U)]
    chg: List[dict] = [{} for _ in range(U)]
    subject = {}
    for u in range(U):
        m = res[u].mask
        if m.match == "changed" or res[u].from_subject:
            continue
        cur_u = {k: v[u * K:(u + 1) * K] for k, v in s.items()} if m.reads_rollout else None
        sels[u] = res[u].at(E_t[id(engines[u])], cur_u) if not m.empty else {}
        chg[u] = n_changed(u, sels[u])
        subject.setdefault((id(engines[u]), m.name), u)
    for u in range(U):                    # size-matched controls of a mask that reads the rollout: its unit's size
        if not res[u].from_subject:
            continue
        m = res[u].mask
        r = subject[(id(engines[u]), m.like)]
        sels[u] = res[u].at_counts(class_counts(sels[r], K))
        chg[u] = n_changed(u, sels[u])
    for u in range(U):
        m = res[u].mask
        if m.match != "changed":
            continue
        r = subject[(id(engines[u]), m.like)]
        cur_u = {k: v[u * K:(u + 1) * K] for k, v in s.items()}
        tgt = {c: chg[r].get(c) for c in CLASSES if chg[r].get(c) is not None}
        sels[u] = res[u].at_changed(E_t[id(engines[u])], cur_u, tgt)
        chg[u] = n_changed(u, sels[u])
        if targets is not None:
            for c, n in tgt.items():
                targets[u][c][t - 1] = n.cpu().numpy()
    for u in range(U):
        sel = sels[u]
        for c, n in class_counts(sel, K).items():
            counts[u][c][t - 1] = n.cpu().numpy()
        if changed is not None:
            for c, n in chg[u].items():
                changed[u][c][t - 1] = n.cpu().numpy()
        if "scalars" in sel:
            scols[u] |= sel["scalars"].reshape(K, -1).any(0).cpu().numpy()
    keys = sorted({k for sel in sels for k in sel})
    out = dict(s)
    for key in keys:
        if key not in s:
            continue
        cur = s[key]
        shape = cur.shape[1:]
        sel_rows, val_rows = [], []
        for u in range(U):
            sel = sels[u].get(key)
            if sel is None:
                sel_rows.append(torch.zeros((K,) + tuple(shape), dtype=torch.bool, device=cur.device))
                val_rows.append(cur[u * K:(u + 1) * K])
            else:
                if tuple(sel.shape[1:]) != tuple(shape):
                    raise ValueError(f"{key}: selection {tuple(sel.shape)} for state {tuple(cur.shape)}")
                sel_rows.append(sel)
                val_rows.append(E_t[id(engines[u])][key].to(cur.dtype))
        sel = torch.cat(sel_rows)
        val = torch.cat(val_rows)
        out[key] = torch.where(sel, val, cur)
    return out


def patched_rollout(model, state0: dict, plan: np.ndarray, engine_states: Optional[dict], mask: Mask,
                    K: int = K_PATCH, **kw) -> Patched:
    """One effective plan (H, 25), its engine values (``engine_state_tensors`` on K seeds) and one mask. Keyword
    arguments as ``patched_rollout_batch``; the returned arrays keep the leading unit axis of length 1."""
    return patched_rollout_batch(model, state0, np.asarray(plan)[None], [engine_states], [mask], K, **kw)


# ----------------------------------------------------------------------------------------------
# What a predicate reads
# ----------------------------------------------------------------------------------------------
def predicate_reads(task: str, n_traj: int = 32, H: int = 24, seed: int = 0) -> frozenset:
    """Scalar columns ``dc.tasks.margin`` reads for ``task``: a column is read when changing one of its entries
    (any row, by +-1e7) changes some margin of random trajectories with the threshold at the statistic's median."""
    rng = np.random.default_rng(seed)
    base = rng.uniform(1.0, 1000.0, size=(n_traj, H + 1, NUM_SCALARS))
    theta = float(np.median(T.statistic(task, base)))
    m0 = T.margin(task, base, theta, 1.0)
    out = set()
    for c in range(NUM_SCALARS):
        for r in range(H + 1):
            for d in (1e7, -1e7):
                x = base.copy()
                x[:, r, c] += d
                m = T.margin(task, x, theta, 1.0)
                if not np.array_equal(np.nan_to_num(m, nan=1e300), np.nan_to_num(m0, nan=1e300)):
                    out.add(c)
                    break
            if c in out:
                break
    return frozenset(out)


# ----------------------------------------------------------------------------------------------
# Treasury identity
# ----------------------------------------------------------------------------------------------
FLOAT32_EXACT = 2 ** 24          # integers above this are not all representable in the emulator's float32 state


def budget_months(scal: np.ndarray) -> np.ndarray:
    """(..., H+1, 20) -> (..., H) bool: month t contains the yearly tax collection (cityTime reaches a multiple of
    48 during it, simulate.cpp:206; city_time advances by 4 a month)."""
    ct = np.rint(np.asarray(scal, dtype=np.float64)[..., :-1, SC_TIME]).astype(np.int64)
    return np.mod(ct + 4, 48) == 0


def funding_levels(plan: np.ndarray) -> np.ndarray:
    """Effective plan (H, 25) -> (H, 3) int: the month's road, fire and police funding levels (per cent)."""
    acts, _ = compile_plan(np.asarray(plan))
    return np.array([[a.road, a.fire, a.police] for a in acts], dtype=np.int64)


def _paid(fund: np.ndarray, level: np.ndarray) -> np.ndarray:
    """(int)(fund * percent) with the engine's float arithmetic: percent = float(level / 100.0) (c_api.cpp:139-141,
    via ctypes c_float), fund converted to float, product truncated toward zero (budget.cpp:118-120)."""
    pct = (np.asarray(level, dtype=np.float64) / 100.0).astype(np.float32)
    return np.trunc(np.asarray(fund, dtype=np.float64).astype(np.float32) * pct).astype(np.float64)


def treasury_identity(scal: np.ndarray, build_cost: np.ndarray, ledger: Optional[np.ndarray] = None,
                      levels: Optional[np.ndarray] = None) -> dict:
    """Month-by-month residuals of the treasury identity on trajectories.

    ``scal`` (..., H+1, 20), ``build_cost`` (..., H) (the month's charged cost), ``ledger`` (..., H+1, 27) and
    ``levels`` (..., H, 3) (road, fire, police per cent) for form B. Returns {"budget": (..., H) bool,
    "resid_A": (..., H), "resid_B": (..., H) or None, "auto_after": (..., H) or None, "unrepresentable": (..., H)
    bool (|funds| >= 2**24 at t or t+1)}. Form A (protocol): funds[t+1] - funds[t] + cost[t] - [budget]
    (tax_fund - road_spend - fire_spend - police_spend)[t+1]. Form B: in budget months with auto-budget on at t+1
    the paid amounts sum_i (int)(fund_i * level_i) replace the reported spends; otherwise form A."""
    s = np.asarray(scal, dtype=np.float64)
    c = np.asarray(build_cost, dtype=np.float64)
    bud = budget_months(s)
    f0, f1 = s[..., :-1, SC_FUNDS], s[..., 1:, SC_FUNDS]
    tax = s[..., 1:, SC_TAX_FUND]
    spend = s[..., 1:, SC_ROAD_SPEND] + s[..., 1:, SC_FIRE_SPEND] + s[..., 1:, SC_POLICE_SPEND]
    base = f1 - f0 + c
    rA = base - np.where(bud, tax - spend, 0.0)
    out = {"budget": bud, "resid_A": rA, "resid_B": None, "auto_after": None,
           "unrepresentable": (np.abs(f0) >= FLOAT32_EXACT) | (np.abs(f1) >= FLOAT32_EXACT)}
    if ledger is not None and levels is not None:
        L = np.asarray(ledger, dtype=np.float64)
        lv = np.broadcast_to(np.asarray(levels), s.shape[:-2] + (s.shape[-2] - 1, 3))
        funds_req = np.stack([L[..., 1:, LG["road_fund"]], L[..., 1:, LG["fire_fund"]], L[..., 1:, LG["police_fund"]]],
                             axis=-1)
        paid = _paid(funds_req, lv).sum(-1)
        auto = np.rint(L[..., 1:, LG["auto_budget"]]) == 1
        rB = base - np.where(bud, tax - np.where(auto, paid, spend), 0.0)
        out["resid_B"] = rB
        out["auto_after"] = auto
    return out


MATERIAL_SHARES = (0.01, 0.05, 0.10)    # amendment 5: breached above 5 per cent, 1 and 10 per cent beside it
MATERIAL_PRIMARY = 0.05


def created_share(scal: np.ndarray, resid: np.ndarray) -> np.ndarray:
    """(..., H+1, 20) scalars and (..., H) monthly residuals -> (...,) the cumulative signed residual (money created:
    funds rose by more than the accounts allow) as a share of the starting treasury (funds at row 0). NaN where the
    starting treasury is not positive or a month's residual is NaN."""
    f0 = np.asarray(scal, dtype=np.float64)[..., 0, SC_FUNDS]
    tot = np.asarray(resid, dtype=np.float64).sum(-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(f0 > 0, tot / np.where(f0 > 0, f0, 1.0), np.nan)


# ----------------------------------------------------------------------------------------------
# Later work (study protocol section 6, last item): not built
# ----------------------------------------------------------------------------------------------
def goodhart_type(*_a, **_k):
    """PLACEHOLDER, NOT BUILT. Goodhart type per exploit (regressional if the matched floor explains it; extremal by
    density or disagreement; causal by the matched-intervention test). Comes later; nothing here computes it."""
    raise NotImplementedError("Goodhart types are not built yet (study protocol section 6, last item)")


def matched_intervention(*_a, **_k):
    """PLACEHOLDER, NOT BUILT. The matched-intervention test (cut a wire, raise tax five points, add a plant, in
    both emulator and engine). Comes later."""
    raise NotImplementedError("matched interventions are not built yet (study protocol section 6, last item)")
