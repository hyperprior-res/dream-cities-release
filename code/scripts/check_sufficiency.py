"""Is the extended observation sufficient for the engine's monthly update?

For transitions drawn from behaviour-mix trajectories: record the extended observation (``Obs`` with
``ledger``, ``terrain``, ``com_rate``), the generator state and the sprite list at month t; let the
true run continue to get A; in another instance restore (``Engine._test_restore``, test only), apply
the same months' actions and step to get B; compare field by field after one month and over a
12-month continuation. Variants:

  a       everything restored including sprites (a fresh ``Engine()`` per transition);
  a_full  as a, plus the members that nothing in the monthly update reads (graph histories, ...),
          so that ``mc_hash_full`` can be compared too;
  b       sprites not restored;
  c       as a, then the generator re-seeded; compared on the fields that never differ across seeds
          in the true run (measured by re-seeding the true run, which is replayed from its start
          state with the oracle protocol, at month t with three other seeds);
  ablate  as a with one ledger entry (or carried map, or the derived members) left at its reset
          value, to show that every entry is needed.

Run (8 workers, writes results/oracle/sufficiency/):

    CUDA_VISIBLE_DEVICES="" PYTHONPATH=code python code/scripts/check_sufficiency.py --workers 8

``Engine._test_restore`` is used only here and in code/tests/test_observation_sufficient.py.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc.behaviour import (  # noqa: E402
    T_AIRPORT_HI, T_AIRPORT_LO, T_PORT_HI, T_PORT_LO, Policy, make_policy, rollout_behaviour, sample_behaviour,
)
from dc.engine import (  # noqa: E402
    LEDGER_ALL, LEDGER_NAMES, LOMASK, NUM_LEDGER, SCALAR_NAMES, Engine, MonthAction, Obs,
)
from dc.grammar import clip_plan, compile_month  # noqa: E402

FAMILIES_JSON = ROOT / "data" / "families.json"
FAMILY_DIR = ROOT / "data" / "families"
OUT_DIR = ROOT / "results" / "oracle" / "sufficiency"

HALF_NAMES = ["pop_density", "traffic", "pollution", "land_value", "crime"]
EIGHTH_NAMES = ["growth", "fire_cov", "police_cov"]
FIELDS: List[str] = (
    ["tiles"] + [f"half:{n}" for n in HALF_NAMES] + ["power"] + [f"eighth:{n}" for n in EIGHTH_NAMES]
    + [f"scalar:{n}" for n in SCALAR_NAMES] + [f"ledger:{n}" for n in LEDGER_NAMES]
    + ["map:terrain", "map:com_rate", "rng", "sprites", "hash_dynamic", "hash_full"]
)
F = len(FIELDS)
FI = {f: i for i, f in enumerate(FIELDS)}
EXT = np.array([not f.startswith("hash_") for f in FIELDS])          # the extended observation + rng + sprites
NO_SPRITE = EXT & np.array([f != "sprites" for f in FIELDS])

# Ablations: (name, ledger_mask, map_mask)
ABLATIONS: List[Tuple[str, int, int]] = (
    [(f"ledger:{n}", LEDGER_ALL & ~(1 << i), 7) for i, n in enumerate(LEDGER_NAMES)]
    + [("map:terrain", LEDGER_ALL, 7 & ~1), ("map:com_rate", LEDGER_ALL, 7 & ~2), ("derived", LEDGER_ALL, 7 & ~4)]
)
A_N = len(ABLATIONS)
# For each ablation, the fields that are the left-out item itself (a carried value differs from itself
# trivially); "earns its place" is judged on the other fields.
ABL_OTHER = np.stack([EXT & np.array([f != name for f in FIELDS]) for name, _, _ in ABLATIONS])

RAIL_LO, RAIL_HI = 224, 239   # doRail: RAILBASE <= tile < RESBASE (simulate.cpp mapScan)


# ----------------------------------------------------------------------------------------------
# Snapshots and comparison
# ----------------------------------------------------------------------------------------------
@dataclass
class Snap:
    obs: Obs
    rng: int
    sprites: np.ndarray
    hd: int
    hf: int
    aux: Optional[np.ndarray] = None


def snap(eng: Engine, aux: bool = False) -> Snap:
    return Snap(eng.observe(), eng.rng_state(), eng.sprites(), eng.hash_dynamic(), eng.hash_full(),
                eng._test_aux() if aux else None)


def eq(a: Snap, b: Snap) -> np.ndarray:
    """Field-by-field identity of two snapshots (FIELDS order)."""
    oa, ob = a.obs, b.obs
    v = np.zeros((F,), dtype=bool)
    v[FI["tiles"]] = np.array_equal(oa.tiles, ob.tiles)
    for i, n in enumerate(HALF_NAMES):
        v[FI[f"half:{n}"]] = np.array_equal(oa.half[i], ob.half[i])
    v[FI["power"]] = np.array_equal(oa.power, ob.power)
    for i, n in enumerate(EIGHTH_NAMES):
        v[FI[f"eighth:{n}"]] = np.array_equal(oa.eighth[i], ob.eighth[i])
    k = FI[f"scalar:{SCALAR_NAMES[0]}"]
    v[k:k + len(SCALAR_NAMES)] = oa.scalars == ob.scalars
    k = FI[f"ledger:{LEDGER_NAMES[0]}"]
    v[k:k + NUM_LEDGER] = oa.ledger == ob.ledger
    v[FI["map:terrain"]] = np.array_equal(oa.terrain, ob.terrain)
    v[FI["map:com_rate"]] = np.array_equal(oa.com_rate, ob.com_rate)
    v[FI["rng"]] = a.rng == b.rng
    v[FI["sprites"]] = np.array_equal(a.sprites, b.sprites)
    v[FI["hash_dynamic"]] = a.hd == b.hd
    v[FI["hash_full"]] = a.hf == b.hf
    return v


Acts = List[Tuple[MonthAction, int]]


def month(eng: Engine, act: Tuple[MonthAction, int]) -> None:
    """One protocol month (dc.oracle.replay order): settings and tool calls, forced disaster, step."""
    a, k = act
    eng.apply(a)
    if k:
        eng.force_disaster(k)
    eng.step_month()


def play(eng: Engine, acts: Acts, t: int, n: int, aux: bool = False) -> List[Snap]:
    out = []
    for m in range(t, t + n):
        month(eng, acts[m])
        out.append(snap(eng, aux))
    return out


def true_run(eng: Engine, cty, disasters: bool, seed: int, acts: Acts, aux: bool = True) -> List[Snap]:
    """The oracle protocol (load, disasters, seed, months), snapshot at every boundary."""
    eng.load_start(cty)
    eng.set_disasters(disasters)
    eng.seed(seed)
    snaps = [snap(eng, aux)]
    snaps += play(eng, acts, 0, len(acts), aux)
    return snaps


def reseeded_true(eng: Engine, cty, disasters: bool, seed: int, acts: Acts, t: int, reseed: int, n: int) -> List[Snap]:
    """Replay the true run to boundary t, re-seed the generator, continue n months."""
    eng.load_start(cty)
    eng.set_disasters(disasters)
    eng.seed(seed)
    for m in range(t):
        month(eng, acts[m])
    eng.seed(reseed)
    return play(eng, acts, t, n)


def restore(eng: Engine, s: Snap, *, sprites: bool = True, aux: bool = False, ledger_mask: int = LEDGER_ALL,
            map_mask: int = 7) -> None:
    eng._test_restore(s.obs, s.rng, s.sprites if sprites else None, aux=s.aux if aux else None,
                      ledger_mask=ledger_mask, map_mask=map_mask)


def eq_runs(A: Sequence[Snap], B: Sequence[Snap], mask: np.ndarray = EXT) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(identical at month 1, identical at every month, first month with a difference in ``mask`` or 0)."""
    vs = np.stack([eq(a, b) for a, b in zip(A, B)])
    bad = ~vs[:, mask].all(axis=1)
    first = int(np.argmax(bad)) + 1 if bad.any() else 0
    return vs[0], vs.all(axis=0), np.int16(first)


def city_kinds(obs: Obs) -> Tuple[bool, bool, bool]:
    idx = obs.tiles & LOMASK
    rail = bool(((idx >= RAIL_LO) & (idx <= RAIL_HI)).any())
    port = bool(((idx >= T_PORT_LO) & (idx <= T_PORT_HI)).any())
    airport = bool(((idx >= T_AIRPORT_LO) & (idx <= T_AIRPORT_HI)).any())
    return rail, port, airport


# ----------------------------------------------------------------------------------------------
# Trajectories
# ----------------------------------------------------------------------------------------------
class ForcedDisasters(Policy):
    """Wraps a behaviour policy and forces disaster ``kind`` at the given months (stress set)."""

    def __init__(self, base: Policy, schedule: Dict[int, int]):
        self.base, self.schedule = base, dict(schedule)
        self.label = base.label + "+forced"

    def reset(self, obs, rng):
        super().reset(obs, rng)
        self.base.reset(obs, rng)

    def act(self, obs, t):
        row = np.asarray(self.base.act(obs, t), dtype=np.int64).copy()
        if t in self.schedule:
            row[4] = self.schedule[t]
        return clip_plan(row)


@dataclass
class Spec:
    tid: int
    start_id: str
    split: str
    kind: str
    disasters: bool
    label: str
    policy_seed: int
    seed: int
    months: int
    tmax: int
    horizon: int
    forced: Dict[int, int]
    stress: bool
    ablate: bool = True
    variant_c: bool = True


def select_starts(n_per_group: int, seed: int) -> List[Tuple[str, str, str]]:
    """(start_id, split, kind) for n starts from each of train/bundled, train/generated, heldout/generated."""
    fam = json.loads(FAMILIES_JSON.read_text())["families"]
    rng = np.random.default_rng(seed)
    out = []
    for split, kind in (("train", "bundled"), ("train", "generated"), ("heldout", "generated")):
        group = [f for f in fam if f["split"] == split and f["kind"] == kind]
        order = rng.permutation(len(group))
        picked: List[Tuple[str, str, str]] = []
        rnd = 0
        while len(picked) < n_per_group and rnd < 8:
            for j in order:
                starts = group[int(j)]["starts"]
                if rnd < len(starts):
                    s = starts[(rnd + int(j)) % len(starts)]
                    if (FAMILY_DIR / s["file"]).exists() and all(p[0] != s["start_id"] for p in picked):
                        picked.append((s["start_id"], split, kind))
                if len(picked) >= n_per_group:
                    break
            rnd += 1
        out += picked
    return out


def make_specs(n_per_group: int, per_start: int, months: int, tmax: int, horizon: int, seed: int,
               stress_per_start: int = 1) -> List[Spec]:
    rng = np.random.default_rng(seed)
    specs: List[Spec] = []
    tid = 0
    for start_id, split, kind in select_starts(n_per_group, seed):
        for disasters in (False, True):
            for _ in range(per_start):
                _, label = sample_behaviour(rng)
                specs.append(Spec(tid, start_id, split, kind, disasters, label, int(rng.integers(1 << 31)),
                                  int(rng.integers(1, (1 << 31) - 1)), months, tmax, horizon, {}, False))
                tid += 1
        for j in range(stress_per_start):
            _, label = sample_behaviour(rng)
            k1 = 1 + (tid % 6)
            k2 = 1 + ((tid + 3) % 6)
            specs.append(Spec(tid, start_id, split, kind, bool((tid + j) % 2), label, int(rng.integers(1 << 31)),
                              int(rng.integers(1, (1 << 31) - 1)), months, tmax, horizon, {2: k1, 13: k2}, True))
            tid += 1
    return specs


def process(spec: Spec) -> Dict[str, np.ndarray]:
    """All variants for every transition t = 0..tmax of one trajectory."""
    try:
        os.nice(5)
    except OSError:
        pass
    cty = FAMILY_DIR / f"{spec.start_id}.cty"
    eng = Engine()
    policy = make_policy(spec.label)
    if spec.forced:
        policy = ForcedDisasters(policy, spec.forced)
    plan, rep = rollout_behaviour(eng, cty, policy, spec.months, spec.seed, spec.disasters,
                                  np.random.default_rng(spec.policy_seed), record="scalars", want_hash=True)
    acts = [compile_month(r) for r in plan]
    snaps = true_run(eng, cty, spec.disasters, spec.seed, acts, aux=True)
    if [s.hf for s in snaps] != [int(h) for h in rep.hashes]:
        raise RuntimeError(f"instrumented run differs from rollout_behaviour on {spec}")
    if not np.array_equal(np.stack([s.obs.ledger for s in snaps]), rep.ledger if rep.ledger is not None
                          else np.stack([s.obs.ledger for s in snaps])):
        raise RuntimeError("ledger trajectory differs")

    H, T = spec.horizon, spec.tmax + 1
    res: Dict[str, np.ndarray] = {
        "t": np.arange(T, dtype=np.int16),
        "roundtrip": np.zeros((T, F), bool),
        "a_m1": np.zeros((T, F), bool), "a_all": np.zeros((T, F), bool), "a_first": np.zeros((T,), np.int16),
        "afull_m1": np.zeros((T, F), bool), "afull_all": np.zeros((T, F), bool),
        "b_m1": np.zeros((T, F), bool), "b_all": np.zeros((T, F), bool), "b_first": np.zeros((T,), np.int16),
        "inv_m1": np.zeros((T, F), bool), "inv_all": np.zeros((T, F), bool),
        "c_m1": np.zeros((T, F), bool), "c_all": np.zeros((T, F), bool),
        "rc_m1": np.zeros((T, F), bool), "rc_all": np.zeros((T, F), bool),
        "crc_m1": np.zeros((T, F), bool), "crc_all": np.zeros((T, F), bool),
        "abl_m1": np.zeros((T, A_N, F), bool), "abl_first": np.zeros((T, A_N), np.int16),
        "abl_first_other": np.zeros((T, A_N), np.int16),
        "rail": np.zeros((T,), bool), "port": np.zeros((T,), bool), "airport": np.zeros((T,), bool),
        "n_sprites": np.zeros((T,), np.int16), "sprite_types": np.zeros((T, 9), bool),
        "pop": np.zeros((T,), np.int64), "forced_now": np.zeros((T,), np.int8),
    }
    work = Engine()   # reused (dirty) instance for b, c and ablations
    reseeds = [(spec.seed + 1000003 * (k + 1)) & 0x7FFFFFFF for k in range(3)]
    c_seed = (spec.seed + 7777777) & 0x7FFFFFFF
    for t in range(T):
        s_t = snaps[t]
        A = snaps[t + 1:t + 1 + H]
        res["rail"][t], res["port"][t], res["airport"][t] = city_kinds(s_t.obs)
        res["n_sprites"][t] = len(s_t.sprites)
        for ty in s_t.sprites[:, 0]:
            if 0 <= ty < 9:
                res["sprite_types"][t, ty] = True
        res["pop"][t] = s_t.obs.scalars[5]
        res["forced_now"][t] = acts[t][1]

        # a: fresh instance, everything restored
        fresh = Engine()
        restore(fresh, s_t)
        res["roundtrip"][t] = eq(snap(fresh), s_t)
        B = play(fresh, acts, t, H)
        res["a_m1"][t], res["a_all"][t], res["a_first"][t] = eq_runs(A, B)
        fresh.close()

        # a_full: plus the members nothing reads, so mc_hash_full is comparable
        restore(work, s_t, aux=True)
        B = play(work, acts, t, H)
        res["afull_m1"][t], res["afull_all"][t], _ = eq_runs(A, B)

        # b: sprites not restored
        restore(work, s_t, sprites=False)
        B = play(work, acts, t, H)
        res["b_m1"][t], res["b_all"][t], res["b_first"][t] = eq_runs(A, B)

        # c: restore, then re-seed; invariant set from the true run re-seeded at t
        if spec.variant_c:
            inv_m1 = np.ones((F,), bool)
            inv_all = np.ones((F,), bool)
            for rs in reseeds:
                R = reseeded_true(work, cty, spec.disasters, spec.seed, acts, t, rs, H)
                m1, al, _ = eq_runs(A, R)
                inv_m1 &= m1
                inv_all &= al
            res["inv_m1"][t], res["inv_all"][t] = inv_m1, inv_all
            restore(work, s_t)
            work.seed(c_seed)
            B = play(work, acts, t, H)
            res["c_m1"][t], res["c_all"][t], _ = eq_runs(A, B)
            # control: the true run re-seeded with the same seed (exactness under re-seeding)
            Rc = reseeded_true(work, cty, spec.disasters, spec.seed, acts, t, c_seed, H)
            res["rc_m1"][t], res["rc_all"][t], _ = eq_runs(A, Rc)
            res["crc_m1"][t], res["crc_all"][t], _ = eq_runs(Rc, B)

        # ablations
        if spec.ablate:
            for j, (_, lm, mm) in enumerate(ABLATIONS):
                restore(work, s_t, ledger_mask=lm, map_mask=mm)
                B = play(work, acts, t, H)
                m1, al, first = eq_runs(A, B)
                same_other = np.stack([eq(a, b) for a, b in zip(A, B)])[:, ABL_OTHER[j]].all(axis=1)
                res["abl_m1"][t, j], res["abl_first"][t, j] = m1, first
                res["abl_first_other"][t, j] = int(np.argmin(same_other)) + 1 if not same_other.all() else 0
    work.close()
    eng.close()
    return res


def _worker(spec: Spec):
    t0 = time.perf_counter()
    r = process(spec)
    return spec, r, time.perf_counter() - t0


# ----------------------------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------------------------
def cat(res: Dict[str, np.ndarray], key: str) -> np.ndarray:
    return res[key]


def summarise(specs: List[Spec], results: List[Dict[str, np.ndarray]]) -> Tuple[Dict, str]:
    R = {k: np.concatenate([r[k] for r in results]) for k in results[0]}
    meta = {
        "stress": np.concatenate([np.full(len(r["t"]), s.stress) for s, r in zip(specs, results)]),
        "disasters": np.concatenate([np.full(len(r["t"]), s.disasters) for s, r in zip(specs, results)]),
        "split": np.concatenate([np.full(len(r["t"]), s.split) for s, r in zip(specs, results)]),
        "kind": np.concatenate([np.full(len(r["t"]), s.kind) for s, r in zip(specs, results)]),
    }
    N = len(R["t"])
    lines: List[str] = []
    P = lines.append
    starts = sorted({s.start_id for s in specs})
    P(f"trajectories: {len(specs)} ({sum(s.stress for s in specs)} in the forced-disaster stress set); "
      f"start states: {len(starts)} (train/bundled {len({s.start_id for s in specs if s.split == 'train' and s.kind == 'bundled'})}, "
      f"train/generated {len({s.start_id for s in specs if s.split == 'train' and s.kind == 'generated'})}, "
      f"heldout/generated {len({s.start_id for s in specs if s.split == 'heldout'})}); "
      f"months per trajectory: {specs[0].months}; transitions: {N} "
      f"(disasters off {int((~meta['disasters']).sum())}, on {int(meta['disasters'].sum())}; "
      f"t = 0..{specs[0].tmax}); continuation: {specs[0].horizon} months")
    P(f"transitions with sprites at t: {int((R['n_sprites'] > 0).sum())}; with rail {int(R['rail'].sum())}, "
      f"seaport {int(R['port'].sum())}, airport {int(R['airport'].sum())}; "
      f"with a forced disaster in month t: {int((R['forced_now'] > 0).sum())}")
    P("")
    P("Round trip (restore, then read back): extended observation identical in "
      f"{int(R['roundtrip'][:, EXT].all(axis=1).sum())}/{N}")
    P("")
    P("| field | a: month 1 | a: all 12 months | a_full: month 1 | a_full: all 12 | b: month 1 | b: all 12 |")
    P("|---|---|---|---|---|---|---|")
    for i, f in enumerate(FIELDS):
        P(f"| {f} | {int(R['a_m1'][:, i].sum())} | {int(R['a_all'][:, i].sum())} | {int(R['afull_m1'][:, i].sum())} | "
          f"{int(R['afull_all'][:, i].sum())} | {int(R['b_m1'][:, i].sum())} | {int(R['b_all'][:, i].sum())} |")
    P(f"| (of) | {N} | {N} | {N} | {N} | {N} | {N} |")
    P("")
    a_ok1 = R["a_m1"][:, EXT].all(axis=1) & R["a_m1"][:, FI["hash_dynamic"]]
    a_ok12 = R["a_all"][:, EXT].all(axis=1) & R["a_all"][:, FI["hash_dynamic"]]
    P(f"variant a: every field of the extended observation and the dynamic hash identical at month 1 in "
      f"{int(a_ok1.sum())}/{N}; at every month of the continuation in {int(a_ok12.sum())}/{N}")
    P(f"variant a_full: mc_hash_full identical at month 1 in {int(R['afull_m1'][:, FI['hash_full']].sum())}/{N}; "
      f"at every month in {int(R['afull_all'][:, FI['hash_full']].sum())}/{N}")
    P("")

    # variant b split
    P("Variant b (sprites not restored): transitions with any difference in the extended observation without "
      "the sprite list (month 1 / within 12 months)")
    P("")
    P("| city at t | transitions | with sprites at t | differ at month 1 | differ within 12 months |")
    P("|---|---|---|---|---|")
    b_bad1 = ~R["b_m1"][:, NO_SPRITE].all(axis=1)
    b_bad12 = ~R["b_all"][:, NO_SPRITE].all(axis=1)
    any_tr = R["rail"] | R["port"] | R["airport"]
    groups = [("no rail, seaport or airport", ~any_tr), ("rail (any)", R["rail"]), ("seaport (any)", R["port"]),
              ("airport (any)", R["airport"]), ("rail, no seaport/airport", R["rail"] & ~R["port"] & ~R["airport"]),
              ("seaport or airport", R["port"] | R["airport"]), ("all", np.ones(N, bool))]
    for name, g in groups:
        P(f"| {name} | {int(g.sum())} | {int((g & (R['n_sprites'] > 0)).sum())} | {int((g & b_bad1).sum())} | "
          f"{int((g & b_bad12).sum())} |")
    P("")
    P(f"variant b, first month with a difference (transitions that differ within 12 months): "
      + ", ".join(f"m{m}: {int((R['b_first'] == m).sum())}" for m in range(1, specs[0].horizon + 1)))
    P("")

    # variant c
    if R["inv_m1"].any():
        g_m1 = R["inv_m1"].all(axis=0)
        g_all = R["inv_all"].all(axis=0)
        P("Variant c (generator re-seeded after the restore).")
        P(f"fields that never differ across seeds in the true run at one month (all {N} transitions, 3 re-seeds "
          f"each): {', '.join(f for f, k in zip(FIELDS, g_m1) if k) or 'none'}")
        P(f"over the 12-month continuation: {', '.join(f for f, k in zip(FIELDS, g_all) if k) or 'none'}")
        c_g1 = (R["c_m1"][:, g_m1]).all(axis=1)
        c_g12 = (R["c_all"][:, g_all]).all(axis=1)
        c_t1 = np.array([R["c_m1"][i, R["inv_m1"][i]].all() for i in range(N)])
        c_t12 = np.array([R["c_all"][i, R["inv_all"][i]].all() for i in range(N)])
        # where the restored-and-re-seeded run leaves the measured set, does the true run with the same seed too?
        rc_t1 = np.array([R["rc_m1"][i, R["inv_m1"][i]].all() for i in range(N)])
        rc_t12 = np.array([R["rc_all"][i, R["inv_all"][i]].all() for i in range(N)])
        P(f"restored and re-seeded run matches the true run on every field of the global one-month set in "
          f"{int(c_g1.sum())}/{N}; on the global 12-month set in {int(c_g12.sum())}/{N}")
        crc1 = R["crc_m1"][:, EXT].all(axis=1) & R["crc_m1"][:, FI["hash_dynamic"]]
        crc12 = R["crc_all"][:, EXT].all(axis=1) & R["crc_all"][:, FI["hash_dynamic"]]
        P(f"control: restored-and-re-seeded run identical to the true run re-seeded with the same seed, every field "
          f"and the dynamic hash, at month 1 in {int(crc1.sum())}/{N}; at every month in {int(crc12.sum())}/{N}")
        P(f"per-transition sets (fields equal across the 3 re-seeded true runs of that transition): match at month 1 "
          f"in {int(c_t1.sum())}/{N}; over 12 months in {int(c_t12.sum())}/{N}; mean set size "
          f"{R['inv_m1'].sum(axis=1).mean():.1f} fields at month 1, {R['inv_all'].sum(axis=1).mean():.1f} over 12 months")
        P(f"the true run re-seeded with that same seed leaves its per-transition set in the same transitions: "
          f"month 1 {int((c_t1 == rc_t1).sum())}/{N} agree, 12 months {int((c_t12 == rc_t12).sum())}/{N} agree")
        P("")
        P("| field | invariant across seeds at month 1 (transitions) | c identical at month 1 | invariant over 12 months | c identical over 12 months |")
        P("|---|---|---|---|---|")
        for i, f in enumerate(FIELDS):
            P(f"| {f} | {int(R['inv_m1'][:, i].sum())} | {int(R['c_m1'][:, i].sum())} | {int(R['inv_all'][:, i].sum())} | "
              f"{int(R['c_all'][:, i].sum())} |")
        P("")

    # ablations
    if R["abl_m1"].any():
        P("Ablation (variant a with one item left at its reset value): transitions where the extended observation "
          "differs from the true run")
        P("")
        P("| item left out | other fields differ at month 1 | other fields differ within 12 months | the item itself differs at month 1 | most affected other fields at month 1 (transitions) |")
        P("|---|---|---|---|---|")
        for j, (name, _, _) in enumerate(ABLATIONS):
            m1 = R["abl_m1"][:, j]
            oth = ABL_OTHER[j]
            bad1 = ~m1[:, oth].all(axis=1)
            bad12 = R["abl_first_other"][:, j] > 0
            self1 = int((~m1[:, FI[name]]).sum()) if name in FI else 0
            cnt = (~m1[:, oth]).sum(axis=0)
            top = np.argsort(-cnt)[:4]
            oth_names = [f for f, e in zip(FIELDS, oth) if e]
            tops = ", ".join(f"{oth_names[k]} {int(cnt[k])}" for k in top if cnt[k] > 0)
            P(f"| {name} | {int(bad1.sum())} | {int(bad12.sum())} | {self1 if name in FI else '-'} | {tops} |")
        P("")

    # stress set
    st = meta["stress"]
    if st.any():
        P(f"Forced-disaster stress set: {int(st.sum())} transitions; variant a identical at month 1 in "
          f"{int(a_ok1[st].sum())}, over 12 months in {int(a_ok12[st].sum())}; by forced kind in month t: "
          + ", ".join(f"kind {k}: {int((st & (R['forced_now'] == k)).sum())} ({int((st & (R['forced_now'] == k) & a_ok12).sum())} identical over 12)"
                      for k in range(1, 7)))
    summary = {
        "transitions": N, "trajectories": len(specs), "start_states": starts,
        "variant_a_month1_identical": int(a_ok1.sum()), "variant_a_all12_identical": int(a_ok12.sum()),
        "variant_a_full_hash_full_month1": int(R["afull_m1"][:, FI["hash_full"]].sum()),
        "variant_a_full_hash_full_all12": int(R["afull_all"][:, FI["hash_full"]].sum()),
        "variant_b_differ_month1": int(b_bad1.sum()), "variant_b_differ_within12": int(b_bad12.sum()),
        "fields": FIELDS, "ablations": [a[0] for a in ABLATIONS],
    }
    if R["inv_m1"].any():
        summary.update({"variant_c_global_set_month1": [f for f, k in zip(FIELDS, g_m1) if k],
                        "variant_c_global_set_all12": [f for f, k in zip(FIELDS, g_all) if k],
                        "variant_c_global_match_month1": int(c_g1.sum()), "variant_c_global_match_all12": int(c_g12.sum()),
                        "variant_c_pertransition_match_month1": int(c_t1.sum()),
                        "variant_c_pertransition_match_all12": int(c_t12.sum()),
                        "variant_c_control_identical_month1": int(crc1.sum()),
                        "variant_c_control_identical_all12": int(crc12.sum())})
    if R["abl_m1"].any():
        summary["ablation_other_fields_differ_month1"] = {a[0]: int((~R["abl_m1"][:, j][:, ABL_OTHER[j]].all(axis=1)).sum())
                                                          for j, a in enumerate(ABLATIONS)}
        summary["ablation_other_fields_differ_within12"] = {a[0]: int((R["abl_first_other"][:, j] > 0).sum())
                                                            for j, a in enumerate(ABLATIONS)}
    return summary, "\n".join(lines)


# ----------------------------------------------------------------------------------------------
# Derivability: is a ledger entry a function of the observation after all?
# ----------------------------------------------------------------------------------------------
FIRE_LO, FIRE_HI = 56, 63        # FIREBASE .. LASTFIRE (micropolis.h); mapScan counts 56 <= tile < 64


def candidates(o: Obs) -> Dict[str, int]:
    """The obvious candidate for each ledger entry computed from the observation alone."""
    s, idx = o.scalars, o.tiles & LOMASK
    zx, zy = np.nonzero(o.tiles & 0x0400)                       # ZONEBIT
    cx, cy = (int(zx.sum() // len(zx)), int(zy.sum() // len(zy))) if len(zx) else (60, 50)
    pol = o.half[2]
    if pol.max() > 0:
        flat = np.flatnonzero(pol == pol.max())                 # scan order x-major, like the engine
        px, py = (int(flat[0] // pol.shape[1]) * 2, int(flat[0] % pol.shape[1]) * 2)
        ties = len(flat) > 1
    else:
        px = py = -1
        ties = False
    return {
        "total_pop": int(s[6] / 8.0 + s[7] + s[8]),
        "res_hist0": int(s[6] // 8), "com_hist0": int(s[7]), "ind_hist0": int(s[8]),
        "road_fund": int(s[12]), "fire_fund": int(s[13]), "police_fund": int(s[14]),
        "fire_pop": int(((idx >= FIRE_LO) & (idx <= FIRE_HI)).sum()),
        "city_center_x": cx, "city_center_y": cy,
        "pollution_max_x": px, "pollution_max_y": py, "_pollution_ties": int(ties),
    }


def derivability_one(spec: Spec) -> Dict[str, np.ndarray]:
    cty = FAMILY_DIR / f"{spec.start_id}.cty"
    eng = Engine()
    policy = make_policy(spec.label)
    if spec.forced:
        policy = ForcedDisasters(policy, spec.forced)
    plan, rep = rollout_behaviour(eng, cty, policy, spec.months, spec.seed, spec.disasters,
                                  np.random.default_rng(spec.policy_seed), record="full")
    eng.close()
    keys = list(candidates(rep.states[0]).keys())
    out = {k: np.zeros(len(rep.states), bool) for k in keys}
    out["city_time_mod4"] = np.array([int(o.scalars[9]) % 4 for o in rep.states], np.int8)
    for t, o in enumerate(rep.states):
        c = candidates(o)
        for k in keys:
            if k.startswith("_"):
                out[k][t] = bool(c[k])
            else:
                out[k][t] = c[k] == int(o.ledger[LEDGER_NAMES.index(k)])
    return out


def derivability_report(specs: List[Spec], workers: int) -> str:
    with mp.get_context("spawn").Pool(workers) as pool:
        rs = pool.map(derivability_one, specs)
    R = {k: np.concatenate([r[k] for r in rs]) for k in rs[0]}
    n = len(R["total_pop"])
    m4 = R.pop("city_time_mod4") == 0
    ties = R.pop("_pollution_ties")
    lines = [f"Boundaries examined: {n} (all boundaries of {len(specs)} trajectories); "
             f"with city time = 0 mod 4 (census in the last cycle): {int(m4.sum())}",
             "", "| ledger entry | candidate from the observation | equal to the engine's value | equal, city time = 0 mod 4 | equal, other |",
             "|---|---|---|---|---|"]
    desc = {"total_pop": "res_pop / 8 + com_pop + ind_pop", "res_hist0": "res_pop // 8", "com_hist0": "com_pop",
            "ind_hist0": "ind_pop", "road_fund": "road_spend", "fire_fund": "fire_spend", "police_fund": "police_spend",
            "fire_pop": "fire tiles in the tile map", "city_center_x": "mean x of zone centres",
            "city_center_y": "mean y of zone centres", "pollution_max_x": "first maximum of the pollution overlay",
            "pollution_max_y": "first maximum of the pollution overlay"}
    for k, v in R.items():
        lines.append(f"| {k} | {desc.get(k, '')} | {int(v.sum())}/{n} | {int(v[m4].sum())}/{int(m4.sum())} | "
                     f"{int(v[~m4].sum())}/{int((~m4).sum())} |")
    lines.append("")
    lines.append(f"boundaries where the pollution maximum is tied (the engine breaks ties with the generator): {int(ties.sum())}/{n}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--per-group", type=int, default=16, help="start states per group (3 groups)")
    ap.add_argument("--per-start", type=int, default=2, help="behaviour trajectories per start and disaster setting")
    ap.add_argument("--stress-per-start", type=int, default=1)
    ap.add_argument("--months", type=int, default=36)
    ap.add_argument("--tmax", type=int, default=24)
    ap.add_argument("--horizon", type=int, default=12)
    ap.add_argument("--seed", type=int, default=20261110)
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    ap.add_argument("--limit", type=int, default=0, help="first n trajectories only (smoke run)")
    ap.add_argument("--derivability", action="store_true",
                    help="only compare ledger entries with candidates computed from the observation")
    args = ap.parse_args()
    assert args.tmax + args.horizon <= args.months
    specs = make_specs(args.per_group, args.per_start, args.months, args.tmax, args.horizon, args.seed,
                       args.stress_per_start)
    if args.limit:
        specs = specs[:args.limit]
    args.out.mkdir(parents=True, exist_ok=True)
    if args.derivability:
        text = derivability_report(specs, args.workers)
        (args.out / "derivability.md").write_text(text + "\n")
        print(text)
        return
    t0 = time.perf_counter()
    done: Dict[int, Tuple[Spec, Dict[str, np.ndarray]]] = {}
    with mp.get_context("spawn").Pool(args.workers) as pool:
        for spec, r, dt in pool.imap_unordered(_worker, specs):
            done[spec.tid] = (spec, r)
            a_bad = int((~(r["a_all"][:, EXT].all(axis=1) & r["a_all"][:, FI["hash_dynamic"]])).sum())
            print(f"[{len(done)}/{len(specs)}] {spec.start_id} dis={int(spec.disasters)} {spec.label}"
                  f"{' forced' + str(spec.forced) if spec.forced else ''}: {len(r['t'])} transitions, "
                  f"variant a differing: {a_bad}, {dt:.0f}s", flush=True)
    order = sorted(done)
    specs = [done[k][0] for k in order]
    results = [done[k][1] for k in order]
    summary, text = summarise(specs, results)
    summary["wall_seconds"] = round(time.perf_counter() - t0, 1)
    summary["workers"] = args.workers
    summary["command"] = " ".join(sys.argv)
    np.savez_compressed(args.out / "raw.npz", **{k: np.concatenate([r[k] for r in results]) for k in results[0]},
                        traj=np.concatenate([np.full(len(r["t"]), s.tid) for s, r in zip(specs, results)]))
    (args.out / "specs.json").write_text(json.dumps([s.__dict__ for s in specs], indent=1, default=str))
    (args.out / "summary.json").write_text(json.dumps(summary, indent=1))
    (args.out / "tables.md").write_text(text + "\n")
    print(text)
    print(f"wall time {summary['wall_seconds']} s on {args.workers} workers")


if __name__ == "__main__":
    main()
