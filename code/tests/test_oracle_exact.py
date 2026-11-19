"""The oracle is exact: a replay is a function of (start file, action log, seed) and nothing else.

Run with pytest, or directly for a printed report:  python code/tests/test_oracle_exact.py
"""

from __future__ import annotations

import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc.engine import (  # noqa: E402
    DISASTER_FIRE, TOOL_BULLDOZER, TOOL_COALPOWER, TOOL_COMMERCIAL, TOOL_INDUSTRIAL, TOOL_PARK,
    TOOL_RESIDENTIAL, TOOL_ROAD, TOOL_WIRE, WORLD_H, WORLD_W, Engine, MonthAction,
)
from dc.oracle import replay  # noqa: E402

CITIES = sorted((ROOT / "data" / "cities").glob("*.cty"))
MONTHS = 240
SEED = 20261109


def action_log(city_index: int, months: int = MONTHS):
    rng = np.random.default_rng(1000 + city_index)
    pool = [TOOL_ROAD, TOOL_WIRE, TOOL_RESIDENTIAL, TOOL_COMMERCIAL, TOOL_INDUSTRIAL, TOOL_PARK, TOOL_BULLDOZER, TOOL_COALPOWER]
    out = []
    for _ in range(months):
        n = 0 if rng.random() < 0.5 else int(rng.integers(1, 7))
        tools = [(int(rng.choice(pool)), int(rng.integers(2, WORLD_W - 3)), int(rng.integers(2, WORLD_H - 3))) for _ in range(n)]
        out.append(MonthAction(int(rng.integers(5, 10)), 100, 100, 100, np.asarray(tools, dtype=np.int16).reshape(-1, 3)))
    return out


def hashes_for(city_index: int, eng: Engine | None = None, seed: int = SEED) -> np.ndarray:
    own = eng is None
    eng = eng or Engine()
    try:
        r = replay(eng, CITIES[city_index], action_log(city_index), seed, disasters=True,
                   forced={12: DISASTER_FIRE}, want_hash=True)
        return r.hashes
    finally:
        if own:
            eng.close()


def _worker(i: int) -> np.ndarray:
    return hashes_for(i)


def test_fresh_repeat():
    for i in range(len(CITIES)):
        assert np.array_equal(hashes_for(i), hashes_for(i)), CITIES[i].name


def test_reused_instance_matches_fresh():
    ref = [hashes_for(i) for i in range(len(CITIES))]
    eng = Engine()
    try:
        order = np.random.default_rng(7).permutation(len(CITIES))
        for rep in range(2):
            for i in order[:: (1 if rep == 0 else -1)]:
                # dirty the instance with a different city and seed first
                replay(eng, CITIES[(i * 7 + 3) % len(CITIES)], action_log(int(i) + 99, 36), 555 + int(i), disasters=True)
                got = hashes_for(int(i), eng)
                assert np.array_equal(got, ref[int(i)]), f"reused instance diverged on {CITIES[int(i)].name}"
    finally:
        eng.close()


def test_cross_process():
    ref = [hashes_for(i) for i in range(0, len(CITIES), 4)]
    with mp.get_context("spawn").Pool(4) as pool:
        got = pool.map(_worker, list(range(0, len(CITIES), 4)))
    for a, b in zip(ref, got):
        assert np.array_equal(a, b)


def test_seed_and_log_matter():
    # hashes include the random generator's state, so they differ from boundary 0 on;
    # the observation at the start must not depend on the seed.
    a = hashes_for(0)
    b = hashes_for(0, seed=SEED + 1)
    assert not np.array_equal(a[1:], b[1:])
    eng = Engine()
    try:
        r1 = replay(eng, CITIES[0], action_log(0, 6), SEED, record="full")
        r2 = replay(eng, CITIES[0], action_log(0, 6), SEED + 1, record="full")
    finally:
        eng.close()
    for f in ("tiles", "half", "power", "eighth", "scalars"):
        assert np.array_equal(getattr(r1.obs0, f), getattr(r2.obs0, f)), f
    assert not np.array_equal(r1.states[-1].tiles, r2.states[-1].tiles) or not np.array_equal(r1.scalars[-1], r2.scalars[-1])


if __name__ == "__main__":
    assert len(CITIES) == 32, f"expected 32 bundled cities, found {len(CITIES)}"
    t0 = time.perf_counter()
    ref = [hashes_for(i) for i in range(len(CITIES))]
    dt = time.perf_counter() - t0
    print(f"cities: {len(CITIES)}; months each: {MONTHS}; disasters on; one forced fire")
    print(f"throughput, one core, with action log and full-state hash every month: {len(CITIES) * MONTHS / dt:,.0f} city-months/s")
    rep = sum(int(np.array_equal(ref[i], hashes_for(i))) for i in range(len(CITIES)))
    print(f"fresh instance repeated: identical at every month in {rep}/{len(CITIES)} cities")
    test_reused_instance_matches_fresh()
    print("reused instance (dirtied by another city before every replay, two orders): identical to fresh in 32/32 cities")
    test_cross_process()
    print("across processes (spawned pool): identical")
    test_seed_and_log_matter()
    print("different seed: same start, different trajectory (the hash is not constant)")
    distinct = len({int(h) for r in ref for h in r})
    print(f"distinct full-state hashes seen: {distinct} of {len(CITIES) * (MONTHS + 1)}")
    np.save(ROOT / "results" / "oracle" / "bundled_hashes.npy", np.stack(ref)) if (ROOT / "results" / "oracle").exists() else None
