"""Plan grammar and action raster (dc.grammar).

pytest code/tests/test_grammar.py; run directly for the acceptance printout (footprint table,
encode / decode round trip on 10,000 random plans).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc.engine import TOOL_COSTS, TOOL_NAMES, WORLD_H, WORLD_W, Engine  # noqa: E402
from dc.grammar import (  # noqa: E402
    BUDGET_LEVELS, COL_HIGH, COL_LOW, FOOTPRINTS, M, MACRO_KINDS, MACRO_SPEC, N_ACTION_SCALARS, N_CHANNELS, N_COLS,
    NOOP_ROW, PLAN_COLUMNS, RASTER_TOOLS, GrammarMonth, Macro, action_scalars, action_scalars_batch, clip_plan,
    compile_month, compile_plan, decode_plan, encode_plan, is_valid_plan, measure_footprints, measure_zone_tiling,
    month_calls, n_calls, nominal_cost, nominal_cost_batch, random_plan, raster, raster_batch,
)
from dc.oracle import replay  # noqa: E402

N_ROUNDTRIP = 10_000
H_ROUNDTRIP = 24


def random_structured_plan(rng: np.random.Generator, H: int):
    """A random valid plan in structured form (each macro drawn within its kind's ranges)."""
    plan = []
    for _ in range(H):
        macs = []
        for _ in range(M):
            k = int(rng.integers(0, len(MACRO_SPEC)))
            _, _, (alo, ahi), (blo, bhi) = MACRO_SPEC[k]
            if k == 0:
                macs.append(Macro())
                continue
            macs.append(Macro(k, int(rng.integers(0, WORLD_W)), int(rng.integers(0, WORLD_H)),
                              int(rng.integers(alo, ahi + 1)), int(rng.integers(blo, bhi + 1))))
        plan.append(GrammarMonth(int(rng.integers(0, 21)), int(rng.choice(BUDGET_LEVELS)), int(rng.choice(BUDGET_LEVELS)),
                                 int(rng.choice(BUDGET_LEVELS)), int(rng.integers(0, 7)), tuple(macs)))
    return plan


def roundtrip(n: int, H: int, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    ok_struct = ok_arr = 0
    for _ in range(n):
        p = random_structured_plan(rng, H)
        a = encode_plan(p)
        if decode_plan(a) == p and a.dtype == np.int16 and a.shape == (H, N_COLS):
            ok_struct += 1
        b = random_plan(rng, H)            # valid array -> structured -> array
        if np.array_equal(encode_plan(decode_plan(b)), b):
            ok_arr += 1
    return {"plans": n, "months_each": H, "struct_ok": ok_struct, "array_ok": ok_arr}


# ----------------------------------------------------------------------------------------------
def test_columns():
    assert len(PLAN_COLUMNS) == N_COLS == 25
    names = [c[0] for c in PLAN_COLUMNS]
    assert names[:5] == ["tax", "road", "fire", "police", "disaster"]
    assert PLAN_COLUMNS[0][1:] == (0, 20) and PLAN_COLUMNS[4][1:] == (0, 6)
    assert MACRO_KINDS["NOOP"] == 0 and len(MACRO_KINDS) == 19
    assert N_CHANNELS == 15 and N_ACTION_SCALARS == 11


def test_footprints_measured():
    meas = measure_footprints()
    for tool in RASTER_TOOLS:
        m = meas[tool]
        assert m["result"] == 1, TOOL_NAMES[tool]
        assert m["cost"] == TOOL_COSTS[tool], TOOL_NAMES[tool]
        assert (m["dx"], m["dy"], m["w"], m["h"]) == FOOTPRINTS[tool], TOOL_NAMES[tool]
        assert m["changed"] == FOOTPRINTS[tool][2] * FOOTPRINTS[tool][3]


def test_zone_blocks_tile():
    z = measure_zone_tiling()
    assert z["accepted"] == 9 and z["calls"] == 9 and z["cost"] == 900
    assert z["changed_equals_9x9"] and z["zone_tiles_in_square"] == 81 and z["raster_equals_changed"]
    assert z["centres"] == [(3 * i, 3 * j) for i in range(3) for j in range(3)]


def test_roundtrip_small():
    r = roundtrip(500, 12, seed=1)
    assert r["struct_ok"] == r["plans"] and r["array_ok"] == r["plans"]


def test_clip_total_and_idempotent():
    rng = np.random.default_rng(2)
    a = rng.integers(-1000, 1000, size=(400, N_COLS))
    c = clip_plan(a)
    assert c.dtype == np.int16 and is_valid_plan(c)
    assert np.array_equal(clip_plan(c), c)
    assert (c >= COL_LOW).all() and (c <= COL_HIGH).all()
    for row in a:                                      # compile is total on any integers
        act, dis = compile_month(row)
        assert 0 <= dis <= 6 and 0 <= act.tax <= 20
        for t, x, y in act.tools.tolist():
            dx, dy, w, h = FOOTPRINTS[t]
            assert x + dx >= 0 and y + dy >= 0 and x + dx + w <= WORLD_W and y + dy + h <= WORLD_H


def test_noop_macro_canonical():
    r = NOOP_ROW.copy()
    r[5:10] = (0, 50, 60, 7, 3)
    assert np.array_equal(clip_plan(r), NOOP_ROW)
    r[5:10] = (MACRO_KINDS["COAL"], 50, 60, 7, 3)
    assert list(clip_plan(r)[5:10]) == [MACRO_KINDS["COAL"], 50, 60, 0, 0]


def test_off_map_calls_dropped():
    r = NOOP_ROW.copy()
    r[5:10] = (MACRO_KINDS["ZONE_R"], 0, 0, 3, 3)      # first column and row off the map
    calls = month_calls(r)
    assert sorted((x, y) for _, x, y in calls) == [(x, y) for x in (3, 6) for y in (3, 6)]
    r[5:10] = (MACRO_KINDS["ROAD_H"], 110, 5, 30, 0)  # runs off the right edge
    assert [x for _, x, _ in month_calls(r)] == list(range(110, 120))
    r[5:10] = (MACRO_KINDS["AIRPORT"], 116, 50, 0, 0)  # 6x6 from x-1: 115..120 is off
    assert month_calls(r) == []
    assert raster(r).sum() == 0 and nominal_cost(r) == 0


def test_raster_cost_scalars_consistent():
    rng = np.random.default_rng(3)
    P = random_plan(rng, 300)
    R = raster_batch(P)
    C = nominal_cost_batch(P)
    S = action_scalars_batch(P)
    for i in range(len(P)):
        act, dis = compile_month(P[i])
        assert np.array_equal(raster(act), R[i])
        assert np.array_equal(raster(P[i]), R[i])
        calls = month_calls(P[i])
        assert n_calls(P[i]) == len(calls)
        assert C[i] == nominal_cost(P[i]) == sum(TOOL_COSTS[t] for t, _, _ in calls)
        s = action_scalars(P[i])
        assert np.array_equal(s, S[i])
        assert s[0] == np.float32(P[i, 0] / 20) and s[1] == np.float32(P[i, 1] * 0.25)
        assert s[4 + P[i, 4]] == 1 and s[4:].sum() == 1
    assert R.dtype == np.float32 and R.shape == (300, 15, WORLD_W, WORLD_H)


def test_compile_plan_replays():
    rng = np.random.default_rng(4)
    P = random_plan(rng, 12, p_noop_macro=0.5)
    P[3, 4] = 1
    acts, forced = compile_plan(P)
    assert len(acts) == 12 and forced.get(3) == 1
    eng = Engine()
    try:
        a = replay(eng, ROOT / "data" / "cities" / "linecity.cty", acts, 5, forced=forced, want_hash=True)
        b = replay(eng, ROOT / "data" / "cities" / "linecity.cty", acts, 5, forced=forced, want_hash=True)
        assert np.array_equal(a.hashes, b.hashes)
        assert sum(len(o) for o in a.tool_ok) == sum(n_calls(r) for r in P)
    finally:
        eng.close()


# ----------------------------------------------------------------------------------------------
def acceptance() -> None:
    print("B1 acceptance 2: measured footprint of every tool (engine placement on clear land, terrain seed 1)")
    meas = measure_footprints()
    print(f"{'tool':9s} {'code':>4s} {'result':>6s} {'cost':>6s} {'dx':>3s} {'dy':>3s} {'w':>2s} {'h':>2s} {'tiles':>5s}  table")
    for tool in RASTER_TOOLS:
        m = meas[tool]
        tab = FOOTPRINTS[tool]
        same = (m["dx"], m["dy"], m["w"], m["h"]) == tab
        print(f"{TOOL_NAMES[tool]:9s} {tool:4d} {m['result']:6d} {m['cost']:6d} {m['dx']:3d} {m['dy']:3d} {m['w']:2d} "
              f"{m['h']:2d} {m['changed']:5d}  {tab} {'match' if same else 'MISMATCH'}")
    z = measure_zone_tiling()
    print(f"ZONE_R 3x3 block: {z['accepted']}/{z['calls']} calls accepted, cost {z['cost']}, changed tiles == 9x9 "
          f"square: {z['changed_equals_9x9']}, zone tiles in square {z['zone_tiles_in_square']}/81, raster == changed: "
          f"{z['raster_equals_changed']}, zone centres at {z['centres']}")
    print()
    print(f"B1 acceptance 3: encode / decode round trip on {N_ROUNDTRIP:,} random plans of {H_ROUNDTRIP} months")
    t0 = time.time()
    r = roundtrip(N_ROUNDTRIP, H_ROUNDTRIP, seed=20261109)
    print(f"structured -> array -> structured identical: {r['struct_ok']:,} / {r['plans']:,}")
    print(f"valid array -> structured -> array identical: {r['array_ok']:,} / {r['plans']:,}")
    print(f"({time.time() - t0:.1f} s)")


if __name__ == "__main__":
    acceptance()
