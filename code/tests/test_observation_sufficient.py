"""The extended observation is sufficient for the engine's monthly update .

``Obs`` + ``Obs.ledger`` + the carried maps (``terrain``, ``com_rate``) + the generator state, and the
sprite list, determine the next month: restore them into a reset instance (``Engine._test_restore``,
test only), apply the month's actions, step, and every field and the dynamic hash equal the true run's.
The long run with all variants is code/scripts/check_sufficiency.py (results/oracle/sufficiency/).

    CUDA_VISIBLE_DEVICES="" PYTHONPATH=code pytest code/tests/test_observation_sufficient.py
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "scripts"))

import check_sufficiency as C  # noqa: E402
from dc.behaviour import make_policy, rollout_behaviour  # noqa: E402
from dc.engine import (  # noqa: E402
    COM_RATE_SHAPE, DISASTER_FIRE, DISASTER_FLOOD, DISASTER_MONSTER, DISASTER_TORNADO, LEDGER_ALL, LEDGER_NAMES, LG,
    NUM_LEDGER, NUM_SCALARS, SCALAR_NAMES, SPRITE_FIELDS, TERRAIN_SHAPE, Engine, MonthAction, _lib,
)
from dc.grammar import compile_month  # noqa: E402
from dc.oracle import replay  # noqa: E402

FAM = ROOT / "data" / "families"
# one start per group: train/bundled, train/generated, heldout/generated
STARTS = ["tr-b-bruce-v1", "tr-g-07-v2", "ho-g-05-v0"]
ORIGINAL_SCALARS = [
    "funds", "tax", "res_valve", "com_valve", "ind_valve", "pop", "res_pop", "com_pop", "ind_pop",
    "city_time", "score", "tax_fund", "road_spend", "fire_spend", "police_spend",
    "powered_zones", "unpowered_zones", "coal_plants", "nuclear_plants", "road_total",
]


def _trajectory(start: str, label: str, months: int, seed: int, disasters: bool, forced=None):
    eng = Engine()
    policy = make_policy(label)
    if forced:
        policy = C.ForcedDisasters(policy, forced)
    plan, rep = rollout_behaviour(eng, FAM / f"{start}.cty", policy, months, seed, disasters,
                                  np.random.default_rng(seed + 1), record="scalars", want_hash=True)
    acts = [compile_month(r) for r in plan]
    snaps = C.true_run(eng, FAM / f"{start}.cty", disasters, seed, acts, aux=True)
    assert [s.hf for s in snaps] == [int(h) for h in rep.hashes]
    eng.close()
    return acts, snaps


def _exact(A, B) -> bool:
    return all(bool(C.eq(a, b)[C.EXT].all()) and a.hd == b.hd for a, b in zip(A, B))


def test_layout_unchanged_and_ledger_named():
    assert SCALAR_NAMES == ORIGINAL_SCALARS and NUM_SCALARS == 20
    assert _lib().mc_ledger_len() == NUM_LEDGER == len(set(LEDGER_NAMES))
    assert _lib().mc_sprite_fields() == len(SPRITE_FIELDS)
    eng = Engine()
    try:
        eng.load_start(FAM / f"{STARTS[0]}.cty")
        o = eng.observe()
        assert [f for f in o.__dataclass_fields__][:5] == ["tiles", "half", "power", "eighth", "scalars"]
        assert (o.tiles.shape, o.tiles.dtype) == ((120, 100), np.uint16)
        assert (o.half.shape, o.half.dtype) == ((5, 60, 50), np.uint8)
        assert (o.power.shape, o.power.dtype) == ((120, 100), np.uint8)
        assert (o.eighth.shape, o.eighth.dtype) == ((3, 15, 13), np.int16)
        assert (o.scalars.shape, o.scalars.dtype) == ((20,), np.int64)
        assert (o.ledger.shape, o.ledger.dtype) == ((NUM_LEDGER,), np.int64)
        assert (o.terrain.shape, o.terrain.dtype) == (TERRAIN_SHAPE, np.uint8)
        assert (o.com_rate.shape, o.com_rate.dtype) == (COM_RATE_SHAPE, np.int16)
        assert o.ledger[LG["initial_eval"]] == 1 and o.ledger[LG["sim_cycle"]] == 0
    finally:
        eng.close()


def test_replay_carries_ledger_trajectory():
    acts, snaps = _trajectory(STARTS[0], "random/sprinkle", 6, 3, True)
    eng = Engine()
    try:
        actions = [a for a, _ in acts]
        forced = {m: k for m, (_, k) in enumerate(acts) if k}
        r_full = replay(eng, FAM / f"{STARTS[0]}.cty", actions, 3, disasters=True, forced=forced, record="full")
        r_scal = replay(eng, FAM / f"{STARTS[0]}.cty", actions, 3, disasters=True, forced=forced, record="scalars")
    finally:
        eng.close()
    want = np.stack([s.obs.ledger for s in snaps])
    assert r_full.ledger.shape == (7, NUM_LEDGER)
    assert np.array_equal(r_full.ledger, want) and np.array_equal(r_scal.ledger, want)
    # obs0 is read right after the load, before set_disasters; every other entry and row agree
    states = np.stack([o.ledger for o in r_full.states])
    d = LG["disasters"]
    assert np.array_equal(states, want) and want[0, d] == 1  # obs0 is read after the disasters switch is set
    assert np.array_equal(np.delete(states[0], d), np.delete(want[0], d))


@pytest.mark.parametrize("start", STARTS)
def test_restore_is_exact_one_month_and_twelve(start):
    """Variant a (fresh instance per transition) and a_full, disasters off and on."""
    for disasters in (False, True):
        acts, snaps = _trajectory(start, "builder/transit", 15, 17 + int(disasters), disasters)
        for t in (0, 1, 3):
            fresh = Engine()
            C.restore(fresh, snaps[t])
            assert C.eq(C.snap(fresh), snaps[t])[C.EXT].all(), "round trip"
            B = C.play(fresh, acts, t, 12)
            fresh.close()
            assert _exact(snaps[t + 1:t + 13], B), (start, disasters, t)
            full = Engine()
            C.restore(full, snaps[t], aux=True)
            B = C.play(full, acts, t, 12)
            full.close()
            assert all(a.hf == b.hf for a, b in zip(snaps[t + 1:t + 13], B)), ("mc_hash_full", start, disasters, t)


def test_restore_into_dirty_instance_matches_fresh():
    acts, snaps = _trajectory(STARTS[1], "random/uniform", 10, 5, True)
    dirty = Engine()
    try:
        replay(dirty, FAM / f"{STARTS[2]}.cty", [MonthAction()] * 7, 99, disasters=True)
        for t in (0, 4):
            C.restore(dirty, snaps[t])
            assert _exact(snaps[t + 1:t + 7], C.play(dirty, acts, t, 6))
    finally:
        dirty.close()


def test_forced_disasters_restore_exact():
    """Monster (pollution_max target), flood (flood_count), tornado and fire, and the months after."""
    acts, snaps = _trajectory(STARTS[0], "random/sprinkle", 16, 23, True,
                              forced={1: DISASTER_MONSTER, 2: DISASTER_FLOOD, 4: DISASTER_TORNADO, 5: DISASTER_FIRE})
    w = Engine()
    try:
        for t in (1, 2, 3, 4, 6):
            C.restore(w, snaps[t])
            assert _exact(snaps[t + 1:t + 11], C.play(w, acts, t, 10)), t
        # the flood entry is live after the forced flood, and leaving it out changes the city
        assert snaps[3].obs.ledger[LG["flood_count"]] > 0
        C.restore(w, snaps[3], ledger_mask=LEDGER_ALL & ~(1 << LG["flood_count"]))
        assert not _exact(snaps[4:10], C.play(w, acts, 3, 6))
    finally:
        w.close()


def test_fire_pop_needed_after_loading_a_burning_city(tmp_path):
    """fire_pop is read only by the evaluation that runs at the first cycle after a load."""
    eng = Engine()
    try:
        eng.load_start(FAM / f"{STARTS[0]}.cty")
        eng.set_disasters(False)
        eng.seed(5)
        for _ in range(6):
            eng.force_disaster(DISASTER_FIRE)
        eng.apply(MonthAction())
        eng.step_month()
        burning = tmp_path / "burning.cty"
        eng.save_city(burning)
        eng.load_start(burning)
        eng.set_disasters(False)
        eng.seed(11)
        s0 = C.snap(eng)
        assert s0.obs.ledger[LG["fire_pop"]] > 0 and s0.obs.ledger[LG["initial_eval"]] == 1
        acts = [(MonthAction(), 0)] * 2
        A = C.play(eng, acts, 0, 2)
        w = Engine()
        C.restore(w, s0)
        assert _exact(A, C.play(w, acts, 0, 2))
        C.restore(w, s0, ledger_mask=LEDGER_ALL & ~(1 << LG["fire_pop"]))
        B = C.play(w, acts, 0, 2)
        assert A[0].obs.scalars[10] != B[0].obs.scalars[10]   # the city score
        w.close()
    finally:
        eng.close()


def test_auto_budget_needed_after_the_engine_switches_it_off(tmp_path):
    """auto_budget is read only at the yearly collection: switched off, the engine pays the funding
    percentages; on, it records full funding. A start state with an empty treasury and tax 0 switches it
    off at the first collection; with tax 20 and 25 % funding the next collection differs."""
    eng = Engine()
    try:
        eng.load_start(FAM / f"{STARTS[0]}.cty")
        eng.set_funds(0)
        broke = tmp_path / "broke.cty"
        eng.save_city(broke)
        eng.load_start(broke)
        eng.set_disasters(False)
        eng.seed(3)
        snaps, acts, off_at = [C.snap(eng)], [], None
        for m in range(30):
            act = (MonthAction(0, 100, 100, 100) if off_at is None else MonthAction(20, 25, 25, 25), 0)
            acts.append(act)
            C.month(eng, act)
            snaps.append(C.snap(eng))
            if off_at is None and snaps[-1].obs.ledger[LG["auto_budget"]] == 0:
                off_at = m + 1
        assert off_at is not None and off_at + 12 <= 30
        w = Engine()
        C.restore(w, snaps[off_at])
        assert _exact(snaps[off_at + 1:off_at + 13], C.play(w, acts, off_at, 12))
        C.restore(w, snaps[off_at], ledger_mask=LEDGER_ALL & ~(1 << LG["auto_budget"]))
        B = C.play(w, acts, off_at, 12)
        sp = [C.FI[f"scalar:{n}"] for n in ("road_spend", "fire_spend", "police_spend")]
        assert any(not C.eq(a, b)[sp].all() for a, b in zip(snaps[off_at + 1:off_at + 13], B))
        w.close()
    finally:
        eng.close()


def test_entries_needed_on_a_short_run():
    """A few entries whose omission shows up within one month on an ordinary city."""
    acts, snaps = _trajectory(STARTS[0], "builder/grid", 8, 31, False)
    w = Engine()
    try:
        # the reset value of initial_eval is 1 (the reset ends in doSimInit), so it matters at t >= 1
        for name in ("initial_eval", "res_hist1", "com_hist1", "sim_cycle"):
            t = 1
            C.restore(w, snaps[t], ledger_mask=LEDGER_ALL & ~(1 << LG[name]))
            B = C.play(w, acts, t, 5)
            other = C.EXT & np.array([f != f"ledger:{name}" for f in C.FIELDS])
            assert any(not C.eq(a, b)[other].all() for a, b in zip(snaps[t + 1:t + 6], B)), name
        C.restore(w, snaps[1], map_mask=7 & ~1)   # terrain density map left out
        assert not _exact(snaps[2:3], C.play(w, acts, 1, 1))
    finally:
        w.close()


def test_reseeded_restore_matches_reseeded_true_run():
    """Variant c control: restoring then re-seeding equals the true run re-seeded with the same seed."""
    acts, snaps = _trajectory(STARTS[2], "random/sprinkle", 10, 41, True)
    w = Engine()
    try:
        for t in (0, 3):
            R = C.reseeded_true(w, FAM / f"{STARTS[2]}.cty", True, 41, acts, t, 1234567, 6)
            C.restore(w, snaps[t])
            w.seed(1234567)
            assert _exact(R, C.play(w, acts, t, 6))
    finally:
        w.close()


def test_test_restore_used_only_by_the_sufficiency_test():
    """mc_test_restore / _test_restore / the aux accessors appear only at their definition and in the
    sufficiency test and its script: never in dc.oracle, the data generator or any experiment."""
    pat = re.compile(r"mc_test_restore|_test_restore|mc_test_get_aux|_test_aux")
    allowed = {"engine/c_api.cpp", "code/dc/engine.py", "code/tests/test_observation_sufficient.py",
               "code/scripts/check_sufficiency.py"}
    skip_dirs = {".git", ".venv", "legacy", "data", "wandb", "ckpt", "storage_bulk", "cache_fast", "logs",
                 "scratch", "ext", "results", "__pycache__", "node_modules", "paper", "briefs"}
    suffixes = {".py", ".cpp", ".cc", ".c", ".h", ".hpp", ".sh", ".js", ".ts", ".ipynb"}
    hits = set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix not in suffixes and fn != "Makefile":
                continue
            try:
                text = p.read_text(errors="ignore")
            except OSError:
                continue
            if pat.search(text):
                hits.add(str(p.relative_to(ROOT)))
    assert hits - allowed == set(), hits - allowed
    assert {"engine/c_api.cpp", "code/dc/engine.py"} <= hits
    oracle_text = (ROOT / "code" / "dc" / "oracle.py").read_text()
    assert "restore" not in oracle_text.replace("restores a state", "")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
