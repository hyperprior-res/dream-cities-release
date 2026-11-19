"""Fidelity of an emulator against the engine, with baselines and the engine's own floor.

Everything is measured on held-out trajectories described as ``EvalTrajectory`` records (start
file, engine action log, seed, disasters, forced disasters, model inputs, stored observations), so
the same code runs on the ``heldout_eval`` (``trajectories_from_store``) and on engine replays made
here for tests (``trajectories_from_engine``).

Metrics (plain tile accuracy is never computed):

* one month, changed-tile precision / recall / F1: a tile counts as changed if its index changes;
  a predicted change is correct only if the predicted new index equals the engine's. Counts are
  pooled over all tiles of all transitions (micro average) and kept per family for bootstraps.
  Every tile metric is reported twice: on the raw codes and "structural", after mapping codes to
  their class under ``canonical_table`` (animation cycles and road traffic levels merged).
* tile agreement along rollouts: changed-since-start precision / recall / F1 at months 1, 12, 24.
  Rows: the model sampled at T=1 (and, in the appendix, at its mode T=0) and the engine under another
  seed; copy-last-state predicts no changes, so its recall and F1 are 0. The nearest-neighbour
  baseline (``TileNN``) is a one-month baseline only.
* open-loop rollouts of 24-month plans, K samples per plan: per-scalar mean absolute error at 1, 12
  and 24 months and its ratio to copy-last-state's (the start state held fixed); funds and
  population also as median relative error; the same for the eight overlays. Every rollout result is
  also split by plan source (``plan_source``): plans from state-reading policies (builders and
  perturbed plans read the true trajectory) and open-loop plans (noop, budget_sweep, random/uniform).
* held-out log-likelihood per term (nats per transition) from ``Emulator.log_prob``.
* the engine yardstick: the same metrics for an engine run under a different seed against the stored
  run. One month: for each held-out transition (trajectory j, month t) the prefix is replayed with
  the stored seed through ``dc.oracle.replay`` (checked identical to the stored observation at t),
  then the generator is reseeded through ``Engine.seed`` and month t is played; rollouts: the plan is
  replayed from the start under a different seed. It is a sample-against-sample yardstick for one
  model sample (T=1, one draw) against the stored run, not a bound: a mean of K samples or a mode can
  have a lower error than any single run, so those rows are not compared with it.

Selections (``selection``): "dev" (seed 20261109, the selection the ladder is monitored on), "test"
(a fresh seed on the held-out plans and transitions the development selection does not contain;
nothing is tuned on it and the paper's tables come from it) and "train_eval" (the unused split of
training-distribution trajectories).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import torch

from .engine import (
    LEDGER_NAMES, NUM_LEDGER, NUM_SCALARS, SC_FUNDS, SC_POP, SCALAR_NAMES, Engine, MonthAction,
)
from .model import Emulator, State
from .train import numpy_to_state, obs_to_numpy, random_month, stand_in_action_scalars, stand_in_raster

HORIZONS = (1, 12, 24)
# rollout decodings: (temperature, overlay decoding). a: everything sampled at T = 1; b: overlays at
# their distribution's mean, tiles, flags, power, scalars and z sampled; c: everything at the mode (z = 0)
DECODINGS = {"a": (1.0, "sample"), "b": (1.0, "mean"), "c": (0.0, "sample")}
# decoding a, everything sampled: the generative model that was trained (the third stage's map summary
# is computed on sampled integer overlays exactly as in training). b and c survive only for the
# appendix comparison.
DEFAULT_DECODING = "a"
# plan sources: open-loop plans do not read the trajectory; every other label (builders, random/sprinkle
# and any "+perturb") comes from a policy that reads the true state
OPEN_LOOP_LABELS = ("noop", "budget_sweep", "random/uniform")
PLAN_SOURCES = ("state_reading", "open_loop")
# selections: development (the ladder's monitoring selection, seed 20261109: transitions with the seed,
# plans with seed + 1), test and train_eval (fresh seeds)
DEV_SEED, TEST_SEED, TRAIN_EVAL_SEED = 20261109, 20261123, 20261147
DEV_N_ONESTEP, DEV_N_PLANS, DEV_H = 2000, 500, 24
HALF_NAMES = ["pop_density", "traffic", "pollution", "land_value", "crime"]
EIGHTH_NAMES = ["rate_of_growth", "fire_coverage", "police_coverage"]


# ----------------------------------------------------------------------------------------------
# Data description
# ----------------------------------------------------------------------------------------------
class EvalTrajectory:
    """One held-out trajectory: what the engine needs to replay it, and lazy access to the model's
    inputs (``raster(ts)``, ``act(ts)``) and the stored observations (``rows(rows)``, compact numpy as
    ``obs_to_numpy``), so a large held-out set is never held in memory."""

    def __init__(self, start_path: str, actions: List[MonthAction], forced: Dict[int, int], seed: int,
                 disasters: bool, family: str, traj_id: int, raster_fn: Callable, act_fn: Callable,
                 rows_fn: Callable, label: str = "", cost_fn: Optional[Callable] = None,
                 fields_fn: Optional[Callable] = None) -> None:
        self.label = str(label)
        self._cost_fn = cost_fn
        self._fields_fn = fields_fn
        self.start_path, self.actions, self.forced = str(start_path), actions, forced
        self.seed, self.disasters, self.family, self.traj_id = int(seed), bool(disasters), str(family), int(traj_id)
        self._raster_fn, self._act_fn, self._rows_fn = raster_fn, act_fn, rows_fn

    @property
    def H(self) -> int:
        return len(self.actions)

    def raster(self, ts: Sequence[int]) -> np.ndarray:
        return np.asarray(self._raster_fn(list(ts)), dtype=np.float32)

    def act(self, ts: Sequence[int]) -> np.ndarray:
        return np.asarray(self._act_fn(list(ts)), dtype=np.float32)

    def rows(self, rows: Sequence[int]) -> Dict[str, np.ndarray]:
        return self._rows_fn(list(rows))

    def cost(self, ts: Sequence[int]) -> Optional[np.ndarray]:
        """The engine's charged build cost of months ``ts`` (None if not known)."""
        return None if self._cost_fn is None else np.asarray(self._cost_fn(list(ts)), dtype=np.float64)

    def row(self, key: str, r: int) -> np.ndarray:
        return self.rows([r])[key][0]

    def fields(self, rows: Sequence[int], keys: Sequence[str]) -> Dict[str, np.ndarray]:
        """Only the arrays ``keys`` (e.g. scalars, ledger) of observation rows ``rows``."""
        if self._fields_fn is not None:
            return self._fields_fn(list(rows), list(keys))
        d = self.rows(rows)
        return {k: d[k] for k in keys if k in d}

    def state(self, rows: Sequence[int], device) -> State:
        return numpy_to_state(self.rows(rows), device)


def trajectories_from_engine(cities: Sequence[Path], per_city: int, months: int, seed: int) -> List[EvalTrajectory]:
    """Development stand-in: random months on bundled cities, replayed by the oracle (kept in memory)."""
    from .oracle import replay
    rng = np.random.default_rng(seed)
    eng = Engine()
    out = []
    for c in cities:
        for _ in range(per_city):
            ml = [random_month(rng) for _ in range(months)]
            acts = [m[0] for m in ml]
            forced = {i: k for i, (_, k) in enumerate(ml) if k}
            sd = int(rng.integers(1, 2**31 - 1))
            rp = replay(eng, c, acts, seed=sd, disasters=False, forced=forced, record="full")
            obs = obs_to_numpy(rp.states, rp.ledger)
            out.append(EvalTrajectory(
                str(c), acts, forced, sd, False, Path(c).stem, len(out),
                (lambda ts, acts=acts: np.stack([stand_in_raster(acts[t]) for t in ts])),
                (lambda ts, ml=ml: np.stack([stand_in_action_scalars(*ml[t]) for t in ts])),
                (lambda rows, obs=obs: {k: v[rows] for k, v in obs.items()}), label="random",
                cost_fn=(lambda ts, c=rp.build_cost: c[ts])))
    eng.close()
    return out


def store_rows_compact(store, rows: Sequence[int]) -> Dict[str, np.ndarray]:
    """Observation rows of a ``dc.data.TrajStore`` in the compact form of ``obs_to_numpy``."""
    from .data import unpack_power
    from .train import FLAG_BITS
    rows = np.asarray(rows, dtype=np.int64)
    tiles = np.asarray(store.tiles[rows]).view(np.uint16)
    out = {
        "tile_index": (tiles & 0x3FF).astype(np.int16),
        "flags": np.stack([(tiles & b) > 0 for b in FLAG_BITS], axis=1),
        "power": np.stack([unpack_power(p) for p in np.asarray(store.power_packed[rows])]).astype(np.uint8),
        "half": np.asarray(store.half[rows]),
        "eighth": np.asarray(store.eighth[rows]),
        "scalars": np.asarray(store.scalars[rows]),
    }
    for k in ("ledger", "terrain", "com_rate"):
        arr = store_array(store, k)
        if arr is not None:
            out[k] = np.asarray(arr[rows])
    return out


def store_array(store, name: str):
    """the per-observation array ``name`` (ledger, terrain, com_rate), or None if the store has no
    ledger files (``TrajStore.has_ledger``); any other failure propagates."""
    if not getattr(store, "has_ledger", True):
        return None
    a = store._maps()[name] if hasattr(store, "_maps") else getattr(store, name)
    return a if len(a) > 0 else None


def trajectories_from_store(store, traj_ids: Sequence[int]) -> List[EvalTrajectory]:
    """Held-out trajectories of the ``TrajStore``, actions compiled with the grammar."""
    from . import grammar
    out = []
    for j in traj_ids:
        rec = store.record(int(j))
        o, t, H = rec["first_obs"], rec["first_trans"], rec["H"]
        plan = np.asarray(store.plan[t:t + H])
        acts, forced = grammar.compile_plan(plan)
        out.append(EvalTrajectory(
            rec["cty_path"], acts, forced, rec["seed"], rec["disasters"], rec["family_id"], int(j),
            (lambda ts, plan=plan: grammar.raster_batch(plan[ts])),
            (lambda ts, plan=plan: grammar.action_scalars_batch(plan[ts])),
            (lambda rows, o=o: store_rows_compact(store, [o + r for r in rows])), label=rec["label"],
            cost_fn=(lambda ts, t=t: np.asarray(store.build_cost[[t + x for x in ts]])),
            fields_fn=(lambda rows, keys, o=o: {k: np.asarray((store_array(store, k) if k == "ledger" else getattr(store, k))
                                                              [[o + r for r in rows]]) for k in keys})))
    return out


# ----------------------------------------------------------------------------------------------
# Tile change metrics
# ----------------------------------------------------------------------------------------------
def tile_change_counts(cur: torch.Tensor, pred: torch.Tensor, true: torch.Tensor) -> torch.Tensor:
    """(B,X,Y) int codes -> (B, 3) int64 counts (tp, fp, fn) of changed tiles."""
    tch = true != cur
    pch = pred != cur
    tp = (pch & tch & (pred == true)).sum(dim=(1, 2))
    return torch.stack([tp, pch.sum(dim=(1, 2)) - tp, tch.sum(dim=(1, 2)) - tp], dim=1).long()


# ----------------------------------------------------------------------------------------------
# Structural canonicalisation of tile codes (a metric only; the model works on the raw codes)
# ----------------------------------------------------------------------------------------------
ENGINE_SRC = Path(__file__).resolve().parents[2] / "engine" / "src"


def _engine_enum(names: Sequence[str]) -> Dict[str, int]:
    """Integer values of tile-enum constants in micropolis.h (read, never edited)."""
    import re
    txt = (ENGINE_SRC / "micropolis.h").read_text()
    def value(n: str, depth: int = 0) -> int:
        m = re.search(rf"\b{n}\s*=\s*(\w+)\s*,", txt)
        if m is None or depth > 4:
            raise ValueError(f"{n} not found in micropolis.h")
        v = m.group(1)
        return int(v) if v.isdigit() else value(v, depth + 1)     # aliases such as ROADBASE = HBRIDGE
    return {n: value(n) for n in names}


def engine_animation_table() -> np.ndarray:
    """The engine's ``animatedTiles`` successor table (1,024 entries), parsed from animate.cpp."""
    import re
    txt = (ENGINE_SRC / "animate.cpp").read_text()
    a = txt.index("static short animatedTiles[TILE_COUNT] = {")
    b = txt.index("};", a)
    body = re.sub(r"/\*.*?\*/", " ", txt[a + len("static short animatedTiles[TILE_COUNT] = {"):b], flags=re.S)
    body = re.sub(r"//[^\n]*", " ", body)
    vals = [int(v) for v in re.findall(r"\d+", body)]
    if len(vals) != 1024:
        raise ValueError(f"animatedTiles has {len(vals)} entries, expected 1024")
    return np.asarray(vals, dtype=np.int64)


def canonical_table() -> np.ndarray:
    """(1024,) int64: the structural class representative (smallest member) of every tile code.

    Classes are the connected components of two relations:
    * animation: c and animatedTiles[c] (engine/src/animate.cpp), transitive closure;
    * road traffic: a road tile carrying light or heavy traffic and the same-shaped road tile with
      no traffic. In simulate.cpp ``doRoad`` sets z = ((tile - ROADBASE) & 15) + {ROADBASE, LTRFBASE,
      HTRFBASE}[level], so every code t in [LTRFBASE, HTRFBASE + 64) joins ROADBASE + ((t - ROADBASE) & 15)
      (the heavy block holds four animation frames of sixteen shapes, ending at 207).
    """
    nxt = engine_animation_table()
    k = _engine_enum(["ROADBASE", "LTRFBASE", "HTRFBASE"])
    parent = np.arange(1024)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    for c in range(1024):
        union(c, int(nxt[c]))
    for t in range(k["LTRFBASE"], k["HTRFBASE"] + 64):
        union(t, k["ROADBASE"] + ((t - k["ROADBASE"]) & 15))
    return np.array([find(c) for c in range(1024)], dtype=np.int64)


_CANON: Dict[str, torch.Tensor] = {}


def canon(idx: torch.Tensor) -> torch.Tensor:
    """Map tile codes to their structural class representative."""
    key = str(idx.device)
    if key not in _CANON:
        _CANON[key] = torch.from_numpy(canonical_table()).to(idx.device)
    return _CANON[key][idx.long()]


def canonical_summary() -> Dict[str, object]:
    t = canonical_table()
    sizes = np.bincount(t, minlength=1024)
    classes = sorted({int(r) for r in t})
    multi = {r: [int(c) for c in np.flatnonzero(t == r)] for r in classes if sizes[r] > 1}
    return {"codes": 1024, "classes": len(classes), "codes_merged_into_another": int((t != np.arange(1024)).sum()),
            "codes_in_multi_member_classes": int(sum(len(v) for v in multi.values())),
            "multi_member_classes": len(multi),
            "class_ranges": {str(r): _ranges(v) for r, v in multi.items()},
            "animate_cpp_sha256": _sha256(ENGINE_SRC / "animate.cpp")}


def _ranges(v: Sequence[int]) -> str:
    out, s, p = [], v[0], v[0]
    for x in list(v[1:]) + [None]:
        if x is not None and x == p + 1:
            p = x
            continue
        out.append(f"{s}-{p}" if p > s else f"{s}")
        if x is not None:
            s = p = x
    return ",".join(out)


def _sha256(path) -> str:
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_change_share(store, chunk_traj: int = 50) -> Dict[str, object]:
    """Over every one-month transition of a ``TrajStore``: index changes, how many are structural
    (still a change after canonicalisation), and the road-traffic check: tiles whose old and new code
    are road tiles of the same shape (only the traffic level / frame differs) must all map to
    unchanged, and road tiles whose shape changes must all stay changed."""
    T = canonical_table()
    k = _engine_enum(["ROADBASE", "HTRFBASE"])
    lo, hi = k["ROADBASE"], k["HTRFBASE"] + 64
    n_ch = n_struct = n_trans = 0
    road_level_only = road_level_only_unchanged = road_shape = road_shape_changed = 0
    for a in range(0, store.n_traj, chunk_traj):
        js = range(a, min(store.n_traj, a + chunk_traj))
        o0 = int(store.traj[js[0]]["first_obs"])
        o1 = int(store.traj[js[-1]]["first_obs"] + store.traj[js[-1]]["H"] + 1)
        idx = np.asarray(store.tiles[o0:o1]).view(np.uint16) & 0x3FF
        for j in js:
            o = int(store.traj[j]["first_obs"]) - o0
            H = int(store.traj[j]["H"])
            x0, x1 = idx[o:o + H], idx[o + 1:o + H + 1]
            ch = x0 != x1
            c0, c1 = T[x0[ch]], T[x1[ch]]
            n_trans += H
            n_ch += int(ch.sum())
            n_struct += int((c0 != c1).sum())
            a0, a1 = x0[ch].astype(np.int64), x1[ch].astype(np.int64)
            road = (a0 >= lo) & (a0 < hi) & (a1 >= lo) & (a1 < hi)
            same_shape = road & (((a0 - lo) & 15) == ((a1 - lo) & 15))
            road_level_only += int(same_shape.sum())
            road_level_only_unchanged += int((same_shape & (c0 == c1)).sum())
            diff_shape = road & ~same_shape
            road_shape += int(diff_shape.sum())
            road_shape_changed += int((diff_shape & (c0 != c1)).sum())
    return {"transitions": n_trans, "index_changes": n_ch, "structural_changes": n_struct,
            "share_becoming_unchanged": (n_ch - n_struct) / n_ch if n_ch else float("nan"),
            "index_changes_per_transition": n_ch / max(1, n_trans),
            "structural_changes_per_transition": n_struct / max(1, n_trans),
            "road_traffic_only_changes": road_level_only, "of_which_unchanged_after_canon": road_level_only_unchanged,
            "road_shape_changes": road_shape, "of_which_still_changed": road_shape_changed}


def count_identity_check(store, traj_ids: Sequence[int], chunk_rows: int = 20000) -> Dict[str, object]:
    """Are the census count scalars exact functions of the end-of-month tile map? Over every
    observation row of the given trajectories except the first (the state right after a load), compare
    the engine's scalar with candidates computed from that row's tile words and power map:
    coal_plants = zone tiles with code POWERPLANT (750); nuclear_plants = zone tiles with code NUCLEAR (816);
    zones = zone-flagged tiles with code >= POWERBASE (208), split powered / unpowered by the PWRBIT of
    the tile or by the power map; road_total = sum over codes 64..207 of 1 + 4 (bridge: no BURNBIT) + 1
    (heavy-traffic code >= 144), mirroring simulate.cpp doRoad. Returns violation counts per candidate."""
    from .data import unpack_power
    from .engine import (BURNBIT, LOMASK, PWRBIT, SC_COAL, SC_NUCLEAR, SC_POWERED, SC_ROAD_TOTAL,
                         SC_UNPOWERED, ZONEBIT)
    rows = np.concatenate([np.arange(int(store.traj[j]["first_obs"]) + 1,
                                     int(store.traj[j]["first_obs"]) + int(store.traj[j]["H"]) + 1) for j in traj_ids])
    viol: Dict[str, int] = {}
    for a in range(0, len(rows), chunk_rows):
        rr = rows[a:a + chunk_rows]
        tiles = np.asarray(store.tiles[rr]).view(np.uint16)
        sc = np.asarray(store.scalars[rr])
        pw = np.stack([unpack_power(p) for p in np.asarray(store.power_packed[rr])]) > 0
        idx = tiles & LOMASK
        zone = (tiles & ZONEBIT) > 0
        zc = zone & (idx >= 208)
        pbit = (tiles & PWRBIT) > 0
        road = (idx >= 64) & (idx < 208)
        cand = {
            "coal_plants": (((idx == 750) & zone).sum((1, 2)), sc[:, SC_COAL]),
            "nuclear_plants": (((idx == 816) & zone).sum((1, 2)), sc[:, SC_NUCLEAR]),
            "zones_total": (zc.sum((1, 2)), sc[:, SC_POWERED] + sc[:, SC_UNPOWERED]),
            "powered_zones_by_pwrbit": ((zc & pbit).sum((1, 2)), sc[:, SC_POWERED]),
            "unpowered_zones_by_pwrbit": ((zc & ~pbit).sum((1, 2)), sc[:, SC_UNPOWERED]),
            "powered_zones_by_power_map": ((zc & pw).sum((1, 2)), sc[:, SC_POWERED]),
            "unpowered_zones_by_power_map": ((zc & ~pw).sum((1, 2)), sc[:, SC_UNPOWERED]),
            "road_total": ((road * (1 + 4 * ((tiles & BURNBIT) == 0) + (idx >= 144))).sum((1, 2)), sc[:, SC_ROAD_TOTAL]),
        }
        for k, (d, e) in cand.items():
            viol[k] = viol.get(k, 0) + int((d != e).sum())
    return {"rows": int(len(rows)), "trajectories": len(traj_ids), "violations": viol,
            "violation_rate": {k: v / len(rows) for k, v in viol.items()}}


def tile_metrics(cur: torch.Tensor, pred: torch.Tensor, true: torch.Tensor) -> Dict[str, torch.Tensor]:
    """(tp, fp, fn) counts per sample on the raw codes and on the structural classes."""
    return {"raw": tile_change_counts(cur, pred, true),
            "structural": tile_change_counts(canon(cur), canon(pred), canon(true))}


def summarise_counts(C: Dict[str, List[np.ndarray]], fam: Sequence[str]) -> Dict[str, object]:
    out = {}
    for kind, lst in C.items():
        X = np.concatenate(lst)
        out[kind] = {**prf(X), "f1_ci95_by_family": bootstrap_f1(X, fam)}
    return out


def prf(counts) -> Dict[str, float]:
    tp, fp, fn = (float(x) for x in np.asarray(counts, dtype=np.float64).reshape(-1, 3).sum(0))
    p = tp / (tp + fp) if tp + fp > 0 else float("nan")
    r = tp / (tp + fn) if tp + fn > 0 else float("nan")
    f = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else float("nan")
    return {"precision": p, "recall": r, "f1": f, "tp": tp, "fp": fp, "fn": fn}


def bootstrap_f1(counts: np.ndarray, groups: Sequence[str], n_boot: int = 1000, seed: int = 0) -> Tuple[float, float]:
    """95 per cent interval of pooled F1, resampling groups (families) with replacement."""
    counts = np.asarray(counts, dtype=np.float64)
    keys = sorted(set(groups))
    per = np.stack([counts[np.asarray(groups) == k].sum(0) for k in keys])
    rng = np.random.default_rng(seed)
    f = []
    for _ in range(n_boot):
        c = per[rng.integers(0, len(keys), len(keys))].sum(0)
        d = 2 * c[0] + c[1] + c[2]
        f.append(2 * c[0] / d if d > 0 else np.nan)
    return float(np.nanpercentile(f, 2.5)), float(np.nanpercentile(f, 97.5))


class TileNN:
    """Nearest-neighbour baseline in a discrete per-tile context space.

    Context = (current code, attempted tool at the tile or none, powered flag). Fitted by counting,
    over training transitions, how often each context changes and to which code. Prediction: the
    mode (change to the most frequent new code if the context changed in more than half of its
    training occurrences) or a sample from the context's empirical distribution. Unseen contexts
    back off to the current code alone, then to no change.
    """

    N_CTX = 1024 * 16 * 2

    def __init__(self, device="cpu") -> None:
        self.device = torch.device(device)
        self.total = torch.zeros(self.N_CTX, dtype=torch.int64, device=self.device)
        self.trans = torch.zeros(self.N_CTX * 1024, dtype=torch.int64, device=self.device)
        self.n_transitions = 0

    @staticmethod
    def context(state: State, raster: torch.Tensor) -> torch.Tensor:
        r = raster > 0.5
        any_tool = r.any(dim=1)
        tool = torch.where(any_tool, r.float().argmax(dim=1), torch.full_like(any_tool, 15, dtype=torch.long))
        pw = (state["flags"][:, 4] > 0.5).long()
        return (state["tile_index"].long() * 16 + tool.long()) * 2 + pw

    @torch.no_grad()
    def fit(self, batches: Iterable, n_transitions: int) -> "TileNN":
        for s0, r, a, s1 in batches:
            if self.n_transitions >= n_transitions:
                break
            s0 = {k: v.to(self.device) for k, v in s0.items()}
            s1 = {k: v.to(self.device) for k, v in s1.items()}
            ctx = self.context(s0, r.to(self.device))
            self.total += torch.bincount(ctx.flatten(), minlength=self.N_CTX)
            ch = s1["tile_index"] != s0["tile_index"]
            key = ctx[ch] * 1024 + s1["tile_index"][ch].long()
            self.trans += torch.bincount(key, minlength=self.N_CTX * 1024)
            self.n_transitions += int(s0["tile_index"].shape[0])
        self._finalise()
        return self

    def _finalise(self) -> None:
        T = self.trans.view(self.N_CTX, 1024)
        changed = T.sum(1)
        self.mode_code = T.argmax(1)
        self.p_change = torch.where(self.total > 0, changed.double() / self.total.clamp(min=1).double(),
                                    torch.full_like(changed, -1, dtype=torch.float64))
        # back-off table on the current code alone
        tot_c = self.total.view(1024, 32).sum(1)
        T_c = T.view(1024, 32, 1024).sum(1)
        self.mode_code_c = T_c.argmax(1)
        self.p_change_c = T_c.sum(1).double() / tot_c.clamp(min=1).double()
        self.T, self.T_c = T, T_c

    def state_dict(self) -> dict:
        return {"total": self.total.cpu(), "trans": self.trans.cpu(), "n_transitions": self.n_transitions}

    @staticmethod
    def from_state_dict(d: dict, device="cpu") -> "TileNN":
        nn_ = TileNN(device)
        nn_.total = d["total"].to(nn_.device)
        nn_.trans = d["trans"].to(nn_.device)
        nn_.n_transitions = int(d["n_transitions"])
        nn_._finalise()
        return nn_

    @torch.no_grad()
    def predict(self, state: State, raster: torch.Tensor, sample: bool = False, seed: int = 0) -> torch.Tensor:
        cur = state["tile_index"].to(self.device).long()
        ctx = self.context({k: v.to(self.device) for k, v in state.items()}, raster.to(self.device))
        seen = self.p_change[ctx] >= 0
        p = torch.where(seen, self.p_change[ctx], self.p_change_c[cur])
        if not sample:
            mode = torch.where(seen, self.mode_code[ctx], self.mode_code_c[cur])
            return torch.where(p > 0.5, mode, cur)
        g = torch.Generator(device=self.device).manual_seed(seed)
        u = torch.rand(cur.shape, generator=g, device=self.device)
        bi = (u < p).nonzero(as_tuple=True)
        code = cur.clone()
        if bi[0].numel() == 0:
            return code
        c_ctx, c_cur, c_seen = ctx[bi], cur[bi], seen[bi]
        w = torch.where(c_seen.unsqueeze(1), self.T[c_ctx], self.T_c[c_cur]).double()
        code[bi] = torch.multinomial(w, 1, generator=g).squeeze(1)
        return code


# ----------------------------------------------------------------------------------------------
# Selections
# ----------------------------------------------------------------------------------------------
def pick_transitions(trajs: Sequence[EvalTrajectory], n: int, seed: int) -> List[Tuple[int, int]]:
    """n (trajectory index, month) pairs uniformly over all held-out transitions, without replacement."""
    pairs = [(i, t) for i, tr in enumerate(trajs) for t in range(tr.H)]
    rng = np.random.default_rng(seed)
    sel = rng.choice(len(pairs), size=min(n, len(pairs)), replace=False)
    return sorted(pairs[k] for k in sel)


def pick_plans(trajs: Sequence[EvalTrajectory], n: int, H: int, seed: int) -> List[int]:
    ok = [i for i, tr in enumerate(trajs) if tr.H >= H]
    rng = np.random.default_rng(seed)
    return sorted(rng.choice(ok, size=min(n, len(ok)), replace=False).tolist())


def plan_source(label: str) -> str:
    """"open_loop" for plans that never read the trajectory, else "state_reading"."""
    return "open_loop" if label in OPEN_LOOP_LABELS else "state_reading"


def selection(trajs: Sequence[EvalTrajectory], name: str, n_onestep: int = DEV_N_ONESTEP, n_plans: int = DEV_N_PLANS,
              H: int = DEV_H, seed: Optional[int] = None) -> Tuple[List[Tuple[int, int]], List[int], Dict[str, object]]:
    """(pairs, plans, description) of a named selection.

    dev: ``pick_transitions(trajs, n_onestep, seed)`` and ``pick_plans(trajs, n_plans, H, seed + 1)``
    (seed 20261109), the selection the pilots and the ladder have been monitored on.
    test: on the same held-out trajectories, the plans are drawn (seed + 1) from the trajectories that
    are not development plans (all of them when n_plans covers them) and the transitions (seed) from
    all months of those trajectories, excluding every development transition; the development
    selection is the fixed one above, whatever the arguments.
    train_eval: the development procedure with its own seed on the train_eval split.
    """
    if name in ("dev", "train_eval"):
        sd = (DEV_SEED if name == "dev" else TRAIN_EVAL_SEED) if seed is None else seed
        pairs, plans = pick_transitions(trajs, n_onestep, sd), pick_plans(trajs, n_plans, H, sd + 1)
        desc = {"name": name, "seed": sd, "n_trajectories": len(trajs)}
    elif name == "test":
        sd = TEST_SEED if seed is None else seed
        dev_pairs = set(pick_transitions(trajs, DEV_N_ONESTEP, DEV_SEED))
        dev_plans = set(pick_plans(trajs, DEV_N_PLANS, DEV_H, DEV_SEED + 1))
        ok = [i for i, tr in enumerate(trajs) if tr.H >= H and i not in dev_plans]
        rng = np.random.default_rng(sd + 1)
        plans = sorted(rng.choice(ok, size=min(n_plans, len(ok)), replace=False).tolist())
        rest = sorted(i for i in range(len(trajs)) if i not in dev_plans)
        pool = [(i, t) for i in rest for t in range(trajs[i].H) if (i, t) not in dev_pairs]
        rng = np.random.default_rng(sd)
        pairs = sorted(pool[k] for k in rng.choice(len(pool), size=min(n_onestep, len(pool)), replace=False))
        pset = set(plans)
        desc = {"name": name, "seed": sd, "n_trajectories": len(trajs), "eligible_plans": len(ok),
                "development_plans_excluded": len(dev_plans), "development_transitions_excluded": len(dev_pairs),
                "plans_shared_with_development": len(pset & dev_plans),
                "transitions_shared_with_development": len(set(pairs) & dev_pairs),
                "development_transitions_inside_test_plan_windows":
                    sum(1 for i, t in dev_pairs if i in pset and t < H)}
    else:
        raise ValueError(f"unknown selection {name!r} (dev, test, train_eval)")
    if not pairs or not plans:
        raise ValueError(f"selection {name!r} is empty on these {len(trajs)} trajectories "
                         f"({len(pairs)} transitions, {len(plans)} plans)")
    src = [plan_source(trajs[i].label) for i in plans]
    desc.update({"n_onestep": len(pairs), "n_plans": len(plans), "H": H,
                 "plans_by_source": {k: src.count(k) for k in PLAN_SOURCES},
                 "transitions_by_source": {k: sum(plan_source(trajs[i].label) == k for i, _ in pairs) for k in PLAN_SOURCES}})
    return pairs, plans, desc


def onestep_batch(trajs, pairs, device):
    s0 = _stack_states([trajs[i].state([t], device) for i, t in pairs])
    s1 = _stack_states([trajs[i].state([t + 1], device) for i, t in pairs])
    costs = [trajs[i].cost([t]) for i, t in pairs]
    if all(c is not None for c in costs):
        s1["build_cost"] = torch.from_numpy(np.concatenate(costs)).float().to(device)
    r = torch.from_numpy(np.concatenate([trajs[i].raster([t]) for i, t in pairs])).to(device)
    a = torch.from_numpy(np.concatenate([trajs[i].act([t]) for i, t in pairs])).to(device)
    return s0, r, a, s1


def _stack_states(states: List[State]) -> State:
    return {k: torch.cat([s[k] for s in states]) for k in states[0]}


# ----------------------------------------------------------------------------------------------
# Scalar and overlay errors
# ----------------------------------------------------------------------------------------------
def horizon_errors(pred_sc: np.ndarray, true_sc: np.ndarray, start_sc: np.ndarray,
                   pred_half=None, true_half=None, start_half=None,
                   pred_eighth=None, true_eighth=None, start_eighth=None,
                   pred_lg=None, true_lg=None, start_lg=None) -> Dict[str, object]:
    """Errors at one horizon.

    pred_sc: (N, K, 20) samples; true_sc, start_sc: (N, 20). Overlays: pred (N, K, C, h, w), true and
    start (N, C, h, w). Returns per scalar: mean |sample - true| (``mae_sample``), mean |mean_K - true|
    (``mae_mean``), copy-last-state's mean |start - true| (``mae_copy``) and the ratios; funds and pop
    also as median relative error |x - true| / max(|true|, 1).
    """
    out: Dict[str, object] = {}
    t = true_sc[:, None, :]
    e_s = np.abs(pred_sc - t).mean(axis=1)                    # (N, 20)
    e_m = np.abs(pred_sc.mean(axis=1) - true_sc)
    e_c = np.abs(start_sc - true_sc)
    sc = {}
    for i, name in enumerate(SCALAR_NAMES):
        c = float(e_c[:, i].mean())
        sc[name] = {"mae_sample": float(e_s[:, i].mean()), "mae_mean": float(e_m[:, i].mean()), "mae_copy": c,
                    "ratio_sample": float(e_s[:, i].mean() / c) if c > 0 else float("nan"),
                    "ratio_mean": float(e_m[:, i].mean() / c) if c > 0 else float("nan")}
    out["scalars"] = sc
    for i, name in ((SC_FUNDS, "funds"), (SC_POP, "pop")):
        den = np.maximum(np.abs(true_sc[:, i]), 1.0)
        out[f"median_rel_{name}"] = {
            "sample": float(np.median(np.abs(pred_sc[:, :, i] - true_sc[:, None, i]) / den[:, None])),
            "mean": float(np.median(np.abs(pred_sc[:, :, i].mean(1) - true_sc[:, i]) / den)),
            "copy": float(np.median(np.abs(start_sc[:, i] - true_sc[:, i]) / den))}
    # aggregate over the 18 scalars that are not bookkeeping identities (tax is the action's, city_time
    # advances by 4: every predictor that knows the protocol gets them exactly, which flatters any mean)
    valid = [r for n, r in sc.items() if np.isfinite(r["ratio_sample"]) and n not in ("tax", "city_time")]
    out["mean_ratio_sample"] = float(np.mean([r["ratio_sample"] for r in valid])) if valid else float("nan")
    out["mean_ratio_mean"] = float(np.mean([r["ratio_mean"] for r in valid])) if valid else float("nan")
    out["mean_ratio_scalars"] = [n for n, r in sc.items() if np.isfinite(r["ratio_sample"]) and n not in ("tax", "city_time")]
    if pred_lg is not None:
        el_s = np.abs(pred_lg - true_lg[:, None, :]).mean(axis=1)
        el_m = np.abs(pred_lg.mean(axis=1) - true_lg)
        el_c = np.abs(start_lg - true_lg)
        out["ledger"] = {}
        for i, name in enumerate(LEDGER_NAMES):
            c = float(el_c[:, i].mean())
            out["ledger"][name] = {"mae_sample": float(el_s[:, i].mean()), "mae_mean": float(el_m[:, i].mean()),
                                   "mae_copy": c, "ratio_sample": float(el_s[:, i].mean() / c) if c > 0 else float("nan"),
                                   "ratio_mean": float(el_m[:, i].mean() / c) if c > 0 else float("nan")}
    for tag, P, T, S, names in (("half", pred_half, true_half, start_half, HALF_NAMES),
                                ("eighth", pred_eighth, true_eighth, start_eighth, EIGHTH_NAMES)):
        if P is None:
            continue
        es = np.abs(P - T[:, None]).mean(axis=(0, 1, 3, 4))
        ec = np.abs(S - T).mean(axis=(0, 2, 3))
        out[tag] = {n: {"mae_sample": float(es[c]), "mae_copy": float(ec[c]),
                        "ratio_sample": float(es[c] / ec[c]) if ec[c] > 0 else float("nan")}
                    for c, n in enumerate(names)}
    return out


# ----------------------------------------------------------------------------------------------
# Shares at the engine's bounds
# ----------------------------------------------------------------------------------------------
def bounded_entries() -> List[Tuple[str, int, str, Optional[float], Optional[float]]]:
    """(kind, index, name, lower, upper) of every learned entry with a bound (``dc.model.BOUND_SOURCES``);
    kind "cost" is the month's charged build cost (index 0)."""
    from .model import COST_BOUNDS, LEDGER_BOUNDS, SCALAR_BOUNDS
    out = [("scalar", i, SCALAR_NAMES[i], lo, hi) for i, (lo, hi) in sorted(SCALAR_BOUNDS.items())]
    out += [("ledger", i, LEDGER_NAMES[i], lo, hi) for i, (lo, hi) in sorted(LEDGER_BOUNDS.items())]
    return out + [("cost", 0, "build_cost", *COST_BOUNDS)]


class BoundCounter:
    """Counts of values at the lower and at the upper bound of every bounded entry, per source."""

    def __init__(self) -> None:
        self.entries = bounded_entries()
        self.c: Dict[str, np.ndarray] = {}

    def add(self, src: str, scalars=None, ledger=None, cost=None) -> None:
        arrs = {"scalar": scalars, "ledger": ledger, "cost": None if cost is None else np.asarray(cost).reshape(-1, 1)}
        c = self.c.setdefault(src, np.zeros((len(self.entries), 4), dtype=np.int64))
        for e, (kind, i, _n, lo, hi) in enumerate(self.entries):
            a = arrs[kind]
            if a is None:
                continue
            v = np.asarray(a, dtype=np.float64)[:, i]
            c[e, 0] += v.size
            c[e, 1] += int((v == lo).sum()) if lo is not None else 0
            c[e, 2] += int((v == hi).sum()) if hi is not None else 0
            c[e, 3] += int(((v < lo) if lo is not None else np.zeros(v.shape, bool)).sum()
                           + ((v > hi) if hi is not None else np.zeros(v.shape, bool)).sum())

    def report(self) -> Dict[str, object]:
        out = {}
        for e, (kind, _i, n, lo, hi) in enumerate(self.entries):
            row = {"kind": kind, "lower": lo, "upper": hi}
            for src, c in self.c.items():
                N = int(c[e, 0])
                row[src] = {"n": N, "share_at_lower": float(c[e, 1] / N) if N and lo is not None else None,
                            "share_at_upper": float(c[e, 2] / N) if N and hi is not None else None,
                            "beyond_bounds": int(c[e, 3])}
            out[n] = row
        return out


# ----------------------------------------------------------------------------------------------
# Model evaluation
# ----------------------------------------------------------------------------------------------
@torch.no_grad()
def eval_model_onestep(model: Emulator, trajs, pairs, device, batch: int = 128, seed: int = 0,
                       k_iw: int = 1) -> Dict[str, object]:
    model.eval()
    torch.manual_seed(seed)
    cnt = {"model_T1": {"raw": [], "structural": []}, "model_T0": {"raw": [], "structural": []}}
    ll: Dict[str, List[float]] = {}
    sc_err = {"T1": [], "T0": [], "copy": []}
    lg_err = {"T1": [], "T0": [], "copy": []}
    funds = {"true": [], "start": [], "T1": [], "T0": []}
    bounds = BoundCounter()
    for a in range(0, len(pairs), batch):
        p = pairs[a:a + batch]
        s0, r, act, s1 = onestep_batch(trajs, p, device)
        bounds.add("engine", s1["scalars"].double().cpu().numpy(),
                   s1["ledger"].double().cpu().numpy() if "ledger" in s1 else None,
                   s1["build_cost"].double().cpu().numpy() if "build_cost" in s1 else None)
        funds["true"].extend(s1["scalars"][:, SC_FUNDS].double().cpu().tolist())
        funds["start"].extend(s0["scalars"][:, SC_FUNDS].double().cpu().tolist())
        for T, tag in ((1.0, "model_T1"), (0.0, "model_T0")):
            ns = model.sample_next(s0, r, act, temperature=T)
            for kind, c in tile_metrics(s0["tile_index"], ns["tile_index"], s1["tile_index"]).items():
                cnt[tag][kind].append(c.cpu().numpy())
            sc_err["T1" if T > 0 else "T0"].append((ns["scalars"].double() - s1["scalars"].double()).abs().cpu().numpy())
            funds["T1" if T > 0 else "T0"].extend(ns["scalars"][:, SC_FUNDS].double().cpu().tolist())
            if "ledger" in ns and "ledger" in s1:
                lg_err["T1" if T > 0 else "T0"].append((ns["ledger"].double() - s1["ledger"].double()).abs().cpu().numpy())
            if T > 0:
                bounds.add("model_T1", ns["scalars"].double().cpu().numpy(),
                           ns["ledger"].double().cpu().numpy() if "ledger" in ns else None,
                           ns["build_cost"].double().cpu().numpy() if "build_cost" in ns else None)
        sc_err["copy"].append((s0["scalars"].double() - s1["scalars"].double()).abs().cpu().numpy())
        if "ledger" in s1:
            lg_err["copy"].append((s0["ledger"].double() - s1["ledger"].double()).abs().cpu().numpy())
        lp = model.log_prob((s0, r, act, s1), k_iw=k_iw)
        for k, v in lp.items():
            ll.setdefault(k, []).extend(v.double().cpu().tolist())
    fam = [trajs[i].family for i, _ in pairs]
    res = {tag: summarise_counts(c, fam) for tag, c in cnt.items()}
    res["loglik_nats_per_transition"] = {k: float(np.mean(v)) for k, v in ll.items()}
    E = {k: np.concatenate(v) for k, v in sc_err.items()}
    res["scalar_mae_1m"] = {n: {"T1": float(E["T1"][:, i].mean()), "T0": float(E["T0"][:, i].mean()),
                                "copy": float(E["copy"][:, i].mean())} for i, n in enumerate(SCALAR_NAMES)}
    if lg_err["copy"] and lg_err["T1"]:
        EL = {k: np.concatenate(v) for k, v in lg_err.items()}
        res["ledger_mae_1m"] = {n: {"T1": float(EL["T1"][:, i].mean()), "T0": float(EL["T0"][:, i].mean()),
                                    "copy": float(EL["copy"][:, i].mean())} for i, n in enumerate(LEDGER_NAMES)}
    res["funds_items"] = {**funds, "label": [trajs[i].label for i, _ in pairs], "pairs": [list(q) for q in pairs]}
    res["bound_shares"] = bounds.report()
    # the same one-month results by plan source of the transition's trajectory
    srcs = np.array([plan_source(trajs[i].label) for i, _ in pairs])
    res["by_subset"] = {}
    for src in PLAN_SOURCES:
        sel = srcs == src
        if not sel.any():
            continue
        fam_s = [f for f, ok in zip(fam, sel) if ok]
        sub = {"n_transitions": int(sel.sum())}
        for tag, c in cnt.items():
            sub[tag] = summarise_counts({k: [np.concatenate(v)[sel]] for k, v in c.items()}, fam_s)
        sub["scalar_mae_1m"] = {n: {"T1": float(E["T1"][sel, i].mean()), "T0": float(E["T0"][sel, i].mean()),
                                    "copy": float(E["copy"][sel, i].mean())} for i, n in enumerate(SCALAR_NAMES)}
        res["by_subset"][src] = sub
    return res


def eval_baselines_onestep(trajs, pairs, nn: Optional[TileNN], device, batch: int = 256) -> Dict[str, object]:
    cnt = {k: {"raw": [], "structural": []} for k in ("copy", "nn_mode", "nn_sample")}
    for a in range(0, len(pairs), batch):
        p = pairs[a:a + batch]
        s0, r, act, s1 = onestep_batch(trajs, p, device)
        cur, tru = s0["tile_index"], s1["tile_index"]
        for kind, c in tile_metrics(cur, cur, tru).items():
            cnt["copy"][kind].append(c.cpu().numpy())
        if nn is not None:
            for tag, smp in (("nn_mode", False), ("nn_sample", True)):
                pr = nn.predict(s0, r, sample=smp, seed=a).to(cur.device)
                for kind, c in tile_metrics(cur, pr, tru).items():
                    cnt[tag][kind].append(c.cpu().numpy())
    fam = [trajs[i].family for i, _ in pairs]
    out = {tag: summarise_counts(c, fam) for tag, c in cnt.items() if c["raw"]}
    out["by_subset"] = _tile_counts_by_source(trajs, pairs, {tag: c for tag, c in cnt.items() if c["raw"]})
    if nn is not None:
        out["nn_fit_transitions"] = nn.n_transitions
    return out


def _tile_counts_by_source(trajs, pairs, cnt: Dict[str, Dict[str, List[np.ndarray]]]) -> Dict[str, object]:
    """{source: {tag: summarise_counts}} of per-transition tile counts, by the plan source of each pair."""
    srcs = np.array([plan_source(trajs[i].label) for i, _ in pairs])
    fam = [trajs[i].family for i, _ in pairs]
    out = {}
    for src in PLAN_SOURCES:
        sel = srcs == src
        if sel.any():
            fs = [f for f, ok in zip(fam, sel) if ok]
            out[src] = {"n_transitions": int(sel.sum()),
                        **{tag: summarise_counts({k: [np.concatenate(v)[sel]] for k, v in c.items()}, fs)
                           for tag, c in cnt.items()}}
    return out


@torch.no_grad()
def eval_model_rollouts(model: Emulator, trajs, plan_ids: Sequence[int], device, H: int = 24, K: int = 8,
                        batch_plans: int = 64, temperature: float = 1.0, seed: int = 0,
                        horizons=HORIZONS, overlay: str = "sample",
                        extra_subsets: Optional[Dict[str, Sequence[bool]]] = None) -> Dict[str, object]:
    """Open-loop rollouts of the plans, K samples each; also the shares of model samples and of the
    engine's months at each bound, pooled over months 1..H (``bound_shares``)."""
    model.eval()
    torch.manual_seed(seed)
    bounds = BoundCounter()
    hs = [h for h in horizons if h <= H]
    P_sc = {h: [] for h in hs}
    P_half = {h: [] for h in hs}
    P_e8 = {h: [] for h in hs}
    TC = {h: {"raw": [], "structural": []} for h in hs}
    P_lg = {h: [] for h in hs}
    for a in range(0, len(plan_ids), batch_plans):
        ids = plan_ids[a:a + batch_plans]
        s = _stack_states([trajs[i].state([0], device) for i in ids])
        s = {k: v.repeat_interleave(K, 0) for k, v in s.items()}
        start = s["tile_index"]
        ref = {h: torch.from_numpy(np.stack([trajs[i].row("tile_index", h) for i in ids]).astype(np.int64))
               .to(device).repeat_interleave(K, 0) for h in hs}
        n = len(ids)
        for i in ids:
            tr = trajs[i]
            f = tr.fields(range(1, H + 1), ("scalars", "ledger"))
            bounds.add("engine", f["scalars"], f.get("ledger"), tr.cost(range(H)))
        for m in range(H):
            r = torch.from_numpy(np.concatenate([trajs[i].raster([m]) for i in ids])).to(device).repeat_interleave(K, 0)
            act = torch.from_numpy(np.concatenate([trajs[i].act([m]) for i in ids])).to(device).repeat_interleave(K, 0)
            s = model.sample_next(s, r, act, temperature=temperature, overlay=overlay)
            bounds.add("model", s["scalars"].double().cpu().numpy(),
                       s["ledger"].double().cpu().numpy() if "ledger" in s else None,
                       s["build_cost"].double().cpu().numpy() if "build_cost" in s else None)
            if m + 1 in P_sc:
                P_sc[m + 1].append(s["scalars"].double().view(n, K, -1).cpu().numpy())
                P_half[m + 1].append(s["half"].view(n, K, 5, 60, 50).cpu().numpy())
                P_e8[m + 1].append(s["eighth"].view(n, K, 3, 15, 13).cpu().numpy())
                for kind, c in tile_metrics(start, s["tile_index"], ref[m + 1]).items():
                    TC[m + 1][kind].append(c.cpu().numpy())
                if "ledger" in s:
                    P_lg[m + 1].append(s["ledger"].double().view(n, K, -1).cpu().numpy())
    rep = _rollout_report(trajs, plan_ids, {h: np.concatenate(P_sc[h]) for h in hs},
                          {h: np.concatenate(P_half[h]) for h in hs}, {h: np.concatenate(P_e8[h]) for h in hs},
                          K=K, tiles=TC, P_lg={h: np.concatenate(P_lg[h]) for h in hs} if P_lg[hs[0]] else None,
                          extra_subsets=extra_subsets)
    rep["funds_items"] = {f"h{h}": np.concatenate(P_sc[h])[:, :, SC_FUNDS].tolist() for h in hs}
    rep["funds_items"]["label"] = [trajs[i].label for i in plan_ids]
    rep["bound_shares"] = bounds.report()
    return rep


def _rollout_report(trajs, plan_ids, P_sc, P_half, P_e8, K, tiles=None, P_lg=None,
                    extra_subsets: Optional[Dict[str, Sequence[bool]]] = None) -> Dict[str, object]:
    """``tiles``: {h: {"raw"/"structural": [(n*K, 3) counts]}} of changes since the start state at month
    h (a change is correct only if the code at month h equals the engine's): tile agreement along the
    rollout without plain accuracy. Copy-last-state scores 0 by construction.

    The same report is repeated under ``by_subset`` for the plan sources (``plan_source``: state-reading
    and open-loop plans) and for any ``extra_subsets`` (boolean masks over ``plan_ids``)."""
    labels = [trajs[i].label for i in plan_ids]
    subsets = {k: np.array([plan_source(l) == k for l in labels]) for k in PLAN_SOURCES}
    for k, v in (extra_subsets or {}).items():
        subsets[k] = np.asarray(v, dtype=bool)
    need = sorted(set(P_sc) | {0})
    got = [trajs[i].rows(need) for i in plan_ids]
    st = lambda key, row: np.stack([g[key][need.index(row)] for g in got]).astype(np.float64)
    T_sc = {h: st("scalars", h) for h in need}
    T_half = {h: st("half", h) for h in need}
    T_e8 = {h: st("eighth", h) for h in need}
    T_lg = {h: st("ledger", h) for h in need} if P_lg is not None and "ledger" in got[0] else None
    tile_rows = {h: {kind: np.concatenate(v) for kind, v in tiles[h].items()} for h in tiles} if tiles is not None else None

    def report(sel: np.ndarray) -> Dict[str, object]:
        fam_k = [trajs[i].family for i, ok in zip(plan_ids, sel) if ok for _ in range(K)]
        rep = {"n_plans": int(sel.sum()), "K": K}
        if sel.sum() == 0:
            return rep
        for h in sorted(P_sc):
            lg = (P_lg[h][sel], T_lg[h][sel], T_lg[0][sel]) if T_lg is not None else (None, None, None)
            e = horizon_errors(P_sc[h][sel], T_sc[h][sel], T_sc[0][sel],
                               P_half[h][sel].astype(np.float64), T_half[h][sel], T_half[0][sel],
                               P_e8[h][sel].astype(np.float64), T_e8[h][sel], T_e8[0][sel], *lg)
            if tile_rows is not None:
                rows = np.repeat(sel, K)
                e["tile_since_start"] = summarise_counts({k: [v[rows]] for k, v in tile_rows[h].items()}, fam_k)
            ov = [v["ratio_sample"] for tag in ("half", "eighth") for v in e.get(tag, {}).values()]
            ov = [x for x in ov if np.isfinite(x)]
            e["mean_ratio_overlays"] = float(np.mean(ov)) if ov else float("nan")
            both = [e["scalars"][n]["ratio_sample"] for n in e["mean_ratio_scalars"]] + ov
            e["mean_ratio_scalars_and_overlays"] = float(np.mean(both)) if both else float("nan")
            rep[f"h{h}"] = e
        return rep

    out = report(np.ones(len(plan_ids), dtype=bool))
    out["by_subset"] = {k: report(v) for k, v in subsets.items()}
    return out


# ----------------------------------------------------------------------------------------------
# Engine floor
# ----------------------------------------------------------------------------------------------
def _alt_seed(seed: int, salt: int) -> int:
    return int((seed * 1000003 + 7919 * (salt + 1)) % (2**31 - 1)) or 1


def engine_floor_onestep(trajs, pairs, salt: int = 1) -> Dict[str, object]:
    """Seed against seed at one month: replay the prefix with the stored seed (checked identical to
    the stored observation), reseed, play month t, compare with the stored month t+1."""
    from .oracle import replay
    eng = Engine()
    counts, fam, sc_err, mism = {"raw": [], "structural": []}, [], [], 0
    f_other = []
    lg_errs = []
    half_err, e8_err = [], []
    for i, t in pairs:
        tr = trajs[i]
        pre_forced = {m: k for m, k in tr.forced.items() if m < t}
        replay(eng, tr.start_path, tr.actions[:t], tr.seed, disasters=tr.disasters, forced=pre_forced)
        o_t = eng.observe()
        ref = tr.rows([t, t + 1])
        if not (np.array_equal(o_t.tiles & 0x3FF, ref["tile_index"][0]) and np.array_equal(o_t.scalars, ref["scalars"][0])):
            mism += 1
        eng.seed(_alt_seed(tr.seed, salt + t))
        eng.apply(tr.actions[t])
        if t in tr.forced:
            eng.force_disaster(tr.forced[t])
        eng.step_month()
        o = obs_to_numpy([eng.observe()])
        cur = torch.from_numpy(ref["tile_index"][0:1].astype(np.int64))
        tru = torch.from_numpy(ref["tile_index"][1:2].astype(np.int64))
        for kind, c in tile_metrics(cur, torch.from_numpy(o["tile_index"].astype(np.int64)), tru).items():
            counts[kind].append(c.numpy())
        fam.append(tr.family)
        sc_err.append(np.abs(o["scalars"][0].astype(np.float64) - ref["scalars"][1]))
        f_other.append(float(o["scalars"][0][SC_FUNDS]))
        if "ledger" in o and "ledger" in ref:
            lg_errs.append(np.abs(o["ledger"][0].astype(np.float64) - ref["ledger"][1]))
        half_err.append(np.abs(o["half"][0].astype(np.float64) - ref["half"][1]).mean(axis=(1, 2)))
        e8_err.append(np.abs(o["eighth"][0].astype(np.float64) - ref["eighth"][1]).mean(axis=(1, 2)))
    eng.close()
    E = np.stack(sc_err)
    extra = {}
    if lg_errs:
        EL = np.stack(lg_errs)
        extra["ledger_mae_1m"] = {n: float(EL[:, i].mean()) for i, n in enumerate(LEDGER_NAMES)}
    by = _tile_counts_by_source(trajs, pairs, {"tile": counts})
    return {"n_transitions": len(pairs), "prefix_mismatches": mism, "tile": summarise_counts(counts, fam), "by_subset": by,
            "funds_items": {"other_seed": f_other}, **extra,
            "scalar_mae_1m": {n: float(E[:, i].mean()) for i, n in enumerate(SCALAR_NAMES)},
            "half_mae_1m": dict(zip(HALF_NAMES, np.stack(half_err).mean(0).tolist())),
            "eighth_mae_1m": dict(zip(EIGHTH_NAMES, np.stack(e8_err).mean(0).tolist()))}


def engine_floor_rollouts(trajs, plan_ids, H: int = 24, n_seeds: int = 1, salt: int = 1,
                          horizons=HORIZONS, extra_subsets: Optional[Dict[str, Sequence[bool]]] = None) -> Dict[str, object]:
    """Seed against seed over H-month plans from the start state: replay each plan under n_seeds other
    seeds and report the rollout errors with those runs in place of model samples (K = n_seeds); also
    the changed-tile counts at month 1 from the start."""
    from .oracle import replay
    eng = Engine()
    hs = [h for h in horizons if h <= H]
    P_sc = {h: [] for h in hs}
    P_half = {h: [] for h in hs}
    P_e8 = {h: [] for h in hs}
    P_lg = {h: [] for h in hs}
    TC = {h: {"raw": [], "structural": []} for h in hs}
    for i in plan_ids:
        tr = trajs[i]
        forced = {m: k for m, k in tr.forced.items() if m < H}
        runs = []
        for s_ in range(n_seeds):
            rp = replay(eng, tr.start_path, tr.actions[:H], _alt_seed(tr.seed, salt + s_),
                        disasters=tr.disasters, forced=forced, record="full")
            runs.append(obs_to_numpy(rp.states, rp.ledger))
        for h in hs:
            P_sc[h].append(np.stack([r["scalars"][h] for r in runs]).astype(np.float64))
            P_half[h].append(np.stack([r["half"][h] for r in runs]))
            P_e8[h].append(np.stack([r["eighth"][h] for r in runs]))
            if "ledger" in runs[0]:
                P_lg[h].append(np.stack([r["ledger"][h] for r in runs]).astype(np.float64))
        ref = tr.rows([0] + hs)["tile_index"].astype(np.int64)
        start = torch.from_numpy(np.repeat(ref[0:1], n_seeds, 0))
        for q, h in enumerate(hs):
            pred = torch.from_numpy(np.stack([r["tile_index"][h] for r in runs]).astype(np.int64))
            tru = torch.from_numpy(np.repeat(ref[q + 1:q + 2], n_seeds, 0))
            for kind, c in tile_metrics(start, pred, tru).items():
                TC[h][kind].append(c.numpy())
    eng.close()
    rep = _rollout_report(trajs, plan_ids, {h: np.stack(P_sc[h]) for h in hs}, {h: np.stack(P_half[h]) for h in hs},
                          {h: np.stack(P_e8[h]) for h in hs}, K=n_seeds, tiles=TC,
                          P_lg={h: np.stack(P_lg[h]) for h in hs} if P_lg[hs[0]] else None, extra_subsets=extra_subsets)
    rep["funds_items"] = {f"h{h}": np.stack(P_sc[h])[:, :, SC_FUNDS].tolist() for h in hs}
    return rep


def to_json(obj, path) -> None:
    def conv(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, tuple):
            return list(o)
        raise TypeError(type(o))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=1, default=conv, allow_nan=True))


def funds_split(trajs, pairs, plans, onestep: dict, rollouts: dict, floor_1: Optional[dict], floor_r: Optional[dict],
                budget_of=None) -> Dict[str, object]:
    """Funds error split by behaviour type and by whether the month contains the yearly budget.

    One month: the one-step transitions (model sample at T=1, mode at T=0, copy-last-state, engine under
    another seed). Twelve months: the open-loop rollouts from the plans' start states (every 12-month
    window contains exactly one budget month, so it is split by behaviour type only). Reported per group:
    n, median relative error |x - true| / max(|true|, 1) and mean absolute error.
    """
    from .train import budget_window
    fi = onestep["funds_items"]
    true1, start1 = np.asarray(fi["true"]), np.asarray(fi["start"])
    preds1 = {"model_T1": np.asarray(fi["T1"]), "model_T0": np.asarray(fi["T0"]), "copy": start1}
    if floor_1 and "funds_items" in floor_1:
        preds1["engine_floor"] = np.asarray(floor_1["funds_items"]["other_seed"])
    ct = np.array([trajs[i].row("scalars", t)[9] for i, t in pairs], dtype=np.float64)
    bud = budget_window(torch.from_numpy(ct)).numpy()
    lab1 = np.asarray(fi["label"])

    def stats(pred, true, sel):
        if sel.sum() == 0:
            return None
        e = np.abs(pred[sel] - true[sel])
        return {"n": int(sel.sum()), "median_rel": float(np.median(e / np.maximum(np.abs(true[sel]), 1.0))),
                "mae": float(e.mean())}

    out: Dict[str, object] = {"one_month": {}, "twelve_months": {}}
    src1 = np.array([plan_source(l) for l in lab1])
    groups = ["all"] + [f"source: {k}" for k in PLAN_SOURCES] + sorted(set(lab1.tolist()))
    for g in groups:
        gs = (np.ones_like(bud) if g == "all" else (src1 == g[len("source: "):]) if g.startswith("source: ")
              else (lab1 == g))
        for bname, bsel in (("budget_month", bud), ("other_months", ~bud)):
            sel = gs & bsel
            out["one_month"][f"{g} | {bname}"] = {k: stats(v, true1, sel) for k, v in preds1.items()}
    fr = rollouts["funds_items"]
    lab12 = np.asarray(fr["label"])
    got = [trajs[i].rows([0, 12]) for i in plans]
    true12 = np.array([g["scalars"][1][SC_FUNDS] for g in got], dtype=np.float64)
    start12 = np.array([g["scalars"][0][SC_FUNDS] for g in got], dtype=np.float64)
    pm = np.asarray(fr["h12"])                                         # (n, K)
    pf = np.asarray(floor_r["funds_items"]["h12"])[:, 0] if floor_r and "funds_items" in floor_r else None
    src12 = np.array([plan_source(l) for l in lab12])
    for g in ["all"] + [f"source: {k}" for k in PLAN_SOURCES] + sorted(set(lab12.tolist())):
        sel = (np.ones(len(plans), dtype=bool) if g == "all" else (src12 == g[len("source: "):]) if g.startswith("source: ")
               else (lab12 == g))
        if not sel.any():
            continue
        e = np.abs(pm[sel] - true12[sel, None])
        out["twelve_months"][g] = {
            "model_sample": {"n": int(sel.sum()), "median_rel": float(np.median(e / np.maximum(np.abs(true12[sel, None]), 1.0))),
                             "mae": float(e.mean())},
            "copy": stats(start12, true12, sel),
            "engine_floor": stats(pf, true12, sel) if pf is not None else None}
    return out
