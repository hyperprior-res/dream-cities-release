"""Trajectory store, generation driver, verify, index helpers and loaders .

The tests run on a stand-in for the modules defined here (``STANDIN``): random legal tool calls on
bundled cities, written as plan rows of a minimal encoding behind the same function signatures as
``dc.grammar`` / ``dc.behaviour`` / ``dc.families``. Everything else is the real code path, including
``code/scripts/gen_data.py``.

    pytest code/tests/test_data.py                          # the tests (CPU, under two minutes)
    python code/tests/test_data.py standin --root DIR       # a stand-in generation of ~3,000 transitions
"""

from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "scripts"))

from dc import data as D  # noqa: E402
from dc.engine import (  # noqa: E402
    TOOL_BULLDOZER, TOOL_COALPOWER, TOOL_COMMERCIAL, TOOL_FIRESTATION, TOOL_INDUSTRIAL, TOOL_PARK,
    TOOL_POLICESTATION, TOOL_RESIDENTIAL, TOOL_ROAD, TOOL_SIZES, TOOL_WIRE, WORLD_H, WORLD_W, Engine, MonthAction, LG,
)
from dc.oracle import replay  # noqa: E402
import gen_data as G  # noqa: E402

CITIES = ROOT / "data" / "cities"

# ----------------------------------------------------------------------------------------------
# stand-in for B1: minimal plan encoding with the same (H, 25) layout
# ----------------------------------------------------------------------------------------------
# macro kind -> (engine tool, line?) ; kind 0 is a no-op
_KINDS = {1: (TOOL_RESIDENTIAL, False), 2: (TOOL_COMMERCIAL, False), 3: (TOOL_INDUSTRIAL, False),
          4: (TOOL_ROAD, True), 5: (TOOL_WIRE, True), 6: (TOOL_PARK, False), 7: (TOOL_BULLDOZER, False),
          8: (TOOL_COALPOWER, False), 9: (TOOL_FIRESTATION, False), 10: (TOOL_POLICESTATION, False)}
# raster channel order (spec 3.1): res, com, ind, fire, police, wire, bulldoze, rail, road, stadium, park, seaport, coal, nuclear, airport
_CHANNEL = {TOOL_RESIDENTIAL: 0, TOOL_COMMERCIAL: 1, TOOL_INDUSTRIAL: 2, TOOL_FIRESTATION: 3, TOOL_POLICESTATION: 4,
            TOOL_WIRE: 5, TOOL_BULLDOZER: 6, TOOL_ROAD: 8, TOOL_PARK: 10, TOOL_COALPOWER: 12}


def standin_compile_month(row):
    calls = []
    for m in range(4):
        kind, x, y, a, b = (int(v) for v in row[5 + 5 * m: 10 + 5 * m])
        if kind not in _KINDS:
            continue
        tool, line = _KINDS[kind]
        n = max(1, min(a, 12)) if line else 1
        for i in range(n):
            if 0 <= x + i < WORLD_W and 0 <= y < WORLD_H:
                calls.append((tool, x + i, y))
    return MonthAction(int(row[0]), int(row[1]), int(row[2]), int(row[3]),
                       np.asarray(calls, dtype=np.int16).reshape(-1, 3))


def standin_compile_plan(arr):
    arr = np.asarray(arr)
    forced = {m: int(arr[m, 4]) for m in range(arr.shape[0]) if int(arr[m, 4]) != 0}
    return [standin_compile_month(r) for r in arr], forced


def standin_raster_batch(rows):
    rows = np.asarray(rows)
    out = np.zeros((rows.shape[0], 15, WORLD_W, WORLD_H), dtype=np.float32)
    for i, r in enumerate(rows):
        for tool, x, y in standin_compile_month(r).tools.astype(int):
            s = TOOL_SIZES[tool]
            x0 = x - 1 if s >= 3 else x
            y0 = y - 1 if s >= 3 else y
            out[i, _CHANNEL[tool], max(0, x0):x0 + s, max(0, y0):y0 + s] = 1.0
    return out


def standin_action_scalars(row):
    v = np.zeros((11,), dtype=np.float32)
    v[0], v[1], v[2], v[3] = row[0] / 20.0, row[1] / 100.0, row[2] / 100.0, row[3] / 100.0
    v[4 + int(row[4])] = 1.0
    return v


class StandIn:
    name = "standin"
    STARTS = {
        "train": [("haight_v0", "fam_haight", CITIES / "haight.cty"),
                  ("joffburg_v0", "fam_joff", CITIES / "joffburg.cty"),
                  ("joffburg_v1", "fam_joff", CITIES / "kowloon.cty")],
        "heldout": [("happisle_v0", "fam_happisle", CITIES / "happisle.cty")],
    }
    LABELS = ("random_editor", "noop", "budget_sweep")

    def starts(self, split):
        return list(self.STARTS[split])

    def sample_behaviour(self, rng):
        k = int(rng.integers(len(self.LABELS)))
        return {"kind": k}, self.LABELS[k]

    def sample_coverage_behaviour(self, rng):
        """Stand-in of the coverage mix: random building under one budget setting held for the trajectory."""
        setting = (int(rng.integers(0, 21)), 25 * int(rng.integers(0, 5)), 25 * int(rng.integers(0, 5)),
                   25 * int(rng.integers(0, 5)))
        return {"kind": 0, "held": setting}, "random_editor+held"

    def sample_listed_behaviour(self, rng, settings, forced):
        """Stand-in of the second coverage mix: random building under one setting from the start's list."""
        t, r, f, p = settings[int(rng.integers(len(settings)))]
        return {"kind": 0, "held": (int(t), 25 * int(r), 25 * int(f), 25 * int(p)), "forced": dict(forced or {})}, \
            "random_editor+held" + ("+forced" if forced else "")

    def recover_forced(self):
        return {0: 3}

    def rollout_behaviour(self, eng, cty_path, policy, months, seed, disasters, rng):
        plan = np.zeros((months, 25), dtype=np.int16)
        for m in range(months):
            plan[m, 0:4] = policy["held"] if "held" in policy else \
                (int(rng.integers(0, 21)), 25 * int(rng.integers(0, 5)), 100, 100)
            if policy["kind"] == 0:
                for j in range(int(rng.integers(0, 5))):
                    plan[m, 5 + 5 * j: 10 + 5 * j] = (int(rng.integers(1, 11)), int(rng.integers(0, WORLD_W)),
                                                      int(rng.integers(0, WORLD_H)), int(rng.integers(1, 13)), 1)
            if "forced" in policy:
                plan[m, 4] = int(policy["forced"].get(m, 0))
            elif "held" not in policy and rng.random() < 0.05:
                plan[m, 4] = int(rng.integers(1, 7))
        actions, forced = standin_compile_plan(plan)
        rep = replay(eng, cty_path, actions, seed, disasters=disasters, forced=forced, record="full")
        return plan, rep      # hashes left None: gen_data falls back to eng.hash_full() at the final state

    def compile_plan(self, arr):
        return standin_compile_plan(arr)

    def grammar(self):
        return standin_raster_batch, standin_action_scalars


STANDIN = StandIn()
TRAIN_SPEC = {"source": "train", "H": [[6, 6], [10, 2]], "disaster_rate": 0.3}
HELD_SPEC = {"source": "heldout", "per_family": [[6, 2], [10, 1]], "disaster_rate": 0.0}
DATA_FILES = [f for f, _, _ in D.ALL_FILES.values()] + ["traj.rec", "labels.json", "starts.json"]


def _job(spec=TRAIN_SPEC, name="train_full"):
    return G.SplitJob(name, STANDIN, master=7, spec=spec)


def _gen(path, workers=1, spec=TRAIN_SPEC, **kw):
    return D.generate(path, _job(spec), workers=workers, log=lambda s: None, **kw)


def _shas(path):
    return {f: hashlib.sha256((Path(path) / f).read_bytes()).hexdigest() for f in DATA_FILES}


@pytest.fixture(scope="module")
def ref_store(tmp_path_factory):
    p = tmp_path_factory.mktemp("ref") / "train_full"
    _gen(p, workers=1)
    return p


# ----------------------------------------------------------------------------------------------
# tests
# ----------------------------------------------------------------------------------------------
def test_power_pack_roundtrip():
    rng = np.random.default_rng(0)
    p = rng.integers(0, 2, size=(3, WORLD_W, WORLD_H)).astype(np.uint8)
    q = D.pack_power(p)
    assert q.shape == (3, 1500) and q.dtype == np.uint8
    assert np.array_equal(D.unpack_power(q), p)
    with pytest.raises(ValueError):
        D.pack_power(p * 2)


def test_store_roundtrip(ref_store):
    st = D.TrajStore(ref_store)
    job = _job()
    assert st.complete and st.n_traj == job.n == 8
    assert st.n_trans == int(job.Hs.sum()) and st.n_obs == int((job.Hs + 1).sum())
    assert D.check_manifest(st)["mismatched"] == []
    man = st.manifest
    assert man["counts"] == {"trajectories": 8, "observations": st.n_obs, "transitions": st.n_trans, "city_months": st.n_trans}
    for k, (f, dt, shape) in D.ALL_FILES.items():
        assert (ref_store / f).stat().st_size == man["arrays"][k]["bytes"]
    # every trajectory equals an independent oracle replay of its stored action log
    eng = Engine()
    for j in range(st.n_traj):
        d = st.trajectory(j)
        assert d["H"] == job.Hs[j] and d["seed"] == job.seeds[j]
        actions, forced = standin_compile_plan(d["plan"])
        rep = replay(eng, d["cty_path"], actions, d["seed"], disasters=d["disasters"], forced=forced, record="full", want_hash=True)
        assert np.array_equal(d["tiles"], np.stack([o.tiles for o in rep.states]))
        assert np.array_equal(d["power"], np.stack([o.power for o in rep.states]))
        assert np.array_equal(d["half"], np.stack([o.half for o in rep.states]))
        assert np.array_equal(d["eighth"], np.stack([o.eighth for o in rep.states]))
        assert np.array_equal(d["scalars"], rep.scalars)
        assert np.array_equal(d["build_cost"], rep.build_cost)
        assert int(rep.hashes[-1]) == d["final_hash"]
        assert np.array_equal(d["ledger"], rep.ledger) and np.array_equal(d["ledger"], np.stack([o.ledger for o in rep.states]))
        assert np.array_equal(d["terrain"], np.stack([o.terrain for o in rep.states]))
        assert np.array_equal(d["com_rate"], np.stack([o.com_rate for o in rep.states]))
        assert d["ledger"][0, LG["disasters"]] == int(d["disasters"])
        # transition(k) and obs(row) agree with trajectory(j)
        for m in (0, d["H"] - 1):
            o0, month, o1 = st.transition(d["first_trans"] + m)
            assert np.array_equal(o0.tiles, d["tiles"][m]) and np.array_equal(o1.tiles, d["tiles"][m + 1])
            assert np.array_equal(o1.power, d["power"][m + 1]) and np.array_equal(month, d["plan"][m])
            assert np.array_equal(o1.ledger, d["ledger"][m + 1]) and np.array_equal(o0.com_rate, d["com_rate"][m])
    # the per-trajectory table
    with np.load(ref_store / "traj.npz") as z:
        assert np.array_equal(z["final_hash"], st.traj["final_hash"])
        assert list(z["label"]) == [st.labels[i] for i in st.traj["label_idx"]]
        assert set(z["family_id"]) <= {"fam_haight", "fam_joff"}
    assert st.traj["n_forced"].sum() == np.count_nonzero(np.asarray(st.plan[:, 4]))


def test_verify_and_tamper(ref_store, tmp_path):
    res = D.verify(ref_store, workers=2, compile_plan=standin_compile_plan)
    assert res["checked"] == 8 and res["mismatched"] == 0, res
    st = D.TrajStore(ref_store)
    p = tmp_path / "tampered"
    shutil.copytree(ref_store, p)
    j = 3
    d = st.record(j)
    with open(p / "tiles.u16", "r+b") as f:     # one tile word, one observation
        off = (d["first_obs"] + 2) * D.ROW_BYTES["tiles"] + 4321 * 2
        f.seek(off)
        w = f.read(2)
        f.seek(off)
        f.write(bytes([w[0] ^ 1, w[1]]))
    with open(p / "scalars.i64", "r+b") as f:   # funds of the last observation of trajectory 5
        f.seek((st.record(5)["first_obs"] + st.record(5)["H"]) * D.ROW_BYTES["scalars"])
        f.write(np.int64(-1).tobytes())
    res = D.verify(p, compile_plan=standin_compile_plan)
    assert res["mismatched"] == 2 and res["mismatched_ids"] == [3, 5]
    assert res["by_field"] == {"tiles": 1, "scalars": 1}
    # a changed action log is detected too
    with open(p / "plan.i16", "r+b") as f:
        f.seek(st.record(1)["first_trans"] * D.ROW_BYTES["plan"])
        tax = int(np.frombuffer(f.read(2), dtype="<i2")[0])
        f.seek(st.record(1)["first_trans"] * D.ROW_BYTES["plan"])
        f.write(np.int16((tax + 7) % 21).tobytes())          # month 0 tax
    assert 1 in D.verify(p, traj_ids=[1], compile_plan=standin_compile_plan)["mismatched_ids"]
    # and so is a changed ledger entry
    with open(p / "ledger.i64", "r+b") as f:
        f.seek((st.record(6)["first_obs"] + 1) * D.ROW_BYTES["ledger"])
        f.write(np.int64(-12345).tobytes())
    r6 = D.verify(p, traj_ids=[6], compile_plan=standin_compile_plan)
    assert r6["mismatched_ids"] == [6] and "ledger" in r6["by_field"]


def _crash_child(path, workers, crash_after):
    _gen(path, workers=workers, commit_seconds=0.0, crash_after=crash_after)


@pytest.mark.parametrize("workers", [1, 3])
def test_crash_resume(ref_store, tmp_path, workers):
    p = tmp_path / "train_full"
    proc = mp.get_context("fork").Process(target=_crash_child, args=(p, workers, 4))
    proc.start()
    proc.join(60)
    assert proc.exitcode == 17
    n_committed = (p / "traj.rec").stat().st_size // D.TRAJ_DTYPE.itemsize
    assert 0 < n_committed < 8 and not (p / "manifest.json").exists()
    assert (p / "traj.rec").stat().st_size % D.TRAJ_DTYPE.itemsize != 0     # a partial record was left
    # a reader sees exactly the committed part
    st = D.TrajStore(p)
    assert st.n_traj == n_committed and not st.complete
    stats = _gen(p, workers=workers)
    assert stats["resumed_at"] == n_committed
    assert _shas(p) == _shas(ref_store)


def test_worker_count_independence(ref_store, tmp_path):
    p = tmp_path / "train_full"
    _gen(p, workers=3, commit_seconds=0.0)
    assert _shas(p) == _shas(ref_store)


def test_resume_refuses_other_config(ref_store, tmp_path):
    p = tmp_path / "train_full"
    shutil.copytree(ref_store, p)
    spec = dict(TRAIN_SPEC, disaster_rate=0.5)
    with pytest.raises(RuntimeError, match="config differs"):
        _gen(p, spec=spec)


def test_seeds_disjoint_and_deterministic():
    a, b = _job(), _job()
    assert np.array_equal(a.seeds, b.seeds) and np.array_equal(a.Hs, b.Hs)
    ev = G.SplitJob("train_eval", STANDIN, master=7, spec={"source": "train", "H": [[6, 50]], "disaster_rate": 0.0})
    assert not (set(ev.seeds.tolist()) & G.train_full_seeds(7))
    h = G.SplitJob("heldout_eval", STANDIN, master=7, spec=HELD_SPEC)
    assert h.Hs.tolist() == [6, 6, 10] and h.n == 3


def test_existing_specs_unchanged():
    """The coverage option leaves the three original splits' specs (and so their generation configs) as they
    were, and is not generated by ``all``."""
    assert G.SPECS["train_full"] == {"source": "train", "H": [[48, 40000], [120, 9000]], "disaster_rate": 0.15}
    assert G.SPECS["train_eval"] == {"source": "train", "H": [[48, 2000]], "disaster_rate": 0.15}
    assert G.SPECS["heldout_eval"] == {"source": "heldout", "per_family": [[48, 25], [120, 5]], "disaster_rate": 0.0}
    assert G.SPLIT_ORDER == ("train_full", "heldout_eval", "train_eval")
    assert "behaviour" not in _job().config()["spec"] and _job().behaviour == "mix"
    cov = G.SPECS["train_cov"]
    assert cov == {"source": "train", "H": [[24, 25000]], "disaster_rate": 0.0, "behaviour": "coverage"}
    assert sum(h * c for h, c in cov["H"]) == 600_000
    with pytest.raises(ValueError, match="behaviour"):
        G.SplitJob("x", STANDIN, master=7, spec=dict(TRAIN_SPEC, behaviour="other"))


COV_SPEC = {"source": "train", "H": [[6, 7]], "disaster_rate": 0.0, "behaviour": "coverage"}


def test_coverage_split(ref_store, tmp_path):
    """A coverage spec draws its behaviour from ``sample_coverage_behaviour``: one budget setting per trajectory,
    held every month; no disasters; training starts only; seeds disjoint from train_full's; verified by replay;
    store independent of the worker count; a mix-behaviour job of the same name and draw seeds differs."""
    job = G.SplitJob("train_cov", STANDIN, master=7, spec=COV_SPEC)
    assert job.behaviour == "coverage" and job.n == 7 and job.config()["spec"]["behaviour"] == "coverage"
    assert not (set(job.seeds.tolist()) & G.train_full_seeds(7))
    p1, p3 = tmp_path / "a" / "train_cov", tmp_path / "b" / "train_cov"
    D.generate(p1, job, workers=1, log=lambda s: None)
    D.generate(p3, G.SplitJob("train_cov", STANDIN, master=7, spec=COV_SPEC), workers=3, commit_seconds=0.0,
               log=lambda s: None)
    assert _shas(p1) == _shas(p3)
    st = D.TrajStore(p1)
    assert st.complete and st.n_trans == 42 and set(st.labels) == {"random_editor+held"}
    assert not st.traj["disasters"].any() and st.traj_ids(split="train").size == 7
    for j in range(st.n_traj):
        P = st.trajectory(j)["plan"]
        assert (P[:, 0:4] == P[0, 0:4]).all() and (P[:, 4] == 0).all()
    assert len({tuple(st.trajectory(j)["plan"][0, 0:4]) for j in range(st.n_traj)}) > 1
    assert D.verify(st, compile_plan=standin_compile_plan)["mismatched"] == 0
    mix = G.SplitJob("train_cov", STANDIN, master=7, spec={k: v for k, v in COV_SPEC.items() if k != "behaviour"})
    p_mix = tmp_path / "c" / "train_cov"
    D.generate(p_mix, mix, workers=1, log=lambda s: None)
    assert set(D.TrajStore(p_mix).labels) <= set(STANDIN.LABELS)


def test_listed_split(tmp_path):
    """The second coverage option: each trajectory's setting is drawn from its start's list in the settings file,
    every fifth (j % 5 == 4) with the forced event in month 0 and a setting from the start's recover list; seeds
    are disjoint from train_full's and from every split in ``avoid_seeds_of``; the file's sha256 is in the config."""
    sf = tmp_path / "settings.json"
    tab = {"haight_v0": {"settings": [[0, 0, 0, 0], [3, 1, 0, 2]], "recover": [[20, 4, 4, 4]]},
           "joffburg_v0": {"settings": [[5, 0, 0, 0]], "recover": [[1, 0, 0, 0], [2, 0, 0, 0]]},
           "joffburg_v1": {"settings": [[7, 4, 4, 4], [6, 0, 0, 0]], "recover": [[9, 2, 2, 2]]}}
    sf.write_text(json.dumps({"meta": {}, "starts": tab}))
    spec = {"source": "train", "H": [[6, 10]], "disaster_rate": 0.0, "behaviour": "listed", "settings_file": str(sf),
            "quake_every": 5, "avoid_seeds_of": ["train_eval"]}
    job = G.SplitJob("train_cov2", STANDIN, master=7, spec=spec)
    ev = G.SplitJob("train_eval", STANDIN, master=7)
    assert not (set(job.seeds.tolist()) & (G.train_full_seeds(7) | set(ev.seeds.tolist())))
    assert job.config()["settings_sha256"] == D.sha256_file(sf) and job.config()["forced_quake"] == {"0": 3}
    p = tmp_path / "train_cov2"
    D.generate(p, job, workers=2, commit_seconds=0.0, log=lambda s: None)
    st = D.TrajStore(p)
    assert st.n_traj == 10 and D.verify(st, compile_plan=standin_compile_plan)["mismatched"] == 0
    for j in range(st.n_traj):
        d = st.trajectory(j)
        P = d["plan"]
        quake = j % 5 == 4
        allowed = tab[d["start_id"]]["recover" if quake else "settings"]
        assert [int(P[0, 0]), int(P[0, 1]) // 25, int(P[0, 2]) // 25, int(P[0, 3]) // 25] in allowed
        assert (P[:, 0:4] == P[0, 0:4]).all() and not d["disasters"]
        assert int(P[0, 4]) == (3 if quake else 0) and (P[1:, 4] == 0).all()
        assert d["label"] == "random_editor+held" + ("+forced" if quake else "")


def test_cov2_select():
    """Per family the three best settings by dc.frontier.J (ties by slack, then grid order), their union in family
    then rank order, and the recover list; checked on constructed scalar trajectories (no engine)."""
    from dc import frontier as F
    from dc.engine import SC_FUNDS, SC_POP, SC_TAX, SC_TAX_FUND
    n = len(F.GRID)
    sc = np.zeros((n, 25, 20), dtype=np.int64)
    sc[:, :, SC_FUNDS] = 1000
    sc[:, :, SC_TAX] = 7
    sc[:, 1:, SC_TAX] = F.GRID[:, 0][:, None]
    sc[:, 0, SC_POP] = 100
    sc[:, -1, SC_POP] = np.arange(n)                       # population grows with the grid index
    sc[n - 1, 5, SC_FUNDS] = -1                            # ... but the last setting goes into debt (both infeasible)
    sc[n - 2, 5, SC_FUNDS] = 400                           # and the one before falls below half the start (solvent only)
    sc[:, -1, SC_TAX_FUND] = (np.arange(n) % 97)
    qk = sc.copy()
    qk[:, -1, SC_POP] = n - np.arange(n)                   # under the earthquake the first settings recover best
    arrs = G.const_family_arrays(sc, qk)
    rec = G.cov2_select(arrs, 3)
    g = lambda i: [int(v) for v in F.GRID[i]]              # noqa: E731
    assert rec["by_family"]["grow"]["settings"] == [g(n - 2), g(n - 3), g(n - 4)]
    assert rec["by_family"]["solvent"]["settings"] == [g(n - 3), g(n - 4), g(n - 5)]
    assert rec["by_family"]["recover"]["settings"] == [g(0), g(1), g(2)] == rec["recover"]
    tre = rec["by_family"]["treasury"]
    assert all(F.GRID[i][0] <= 7 for i in tre["grid_index"]) and all(tre["feasible"])
    assert len(rec["settings"]) == len({tuple(x) for x in rec["settings"]}) <= 12
    assert rec["settings"][:3] == rec["by_family"]["grow"]["settings"]


def test_index_helpers(ref_store):
    st = D.TrajStore(ref_store)
    all_t = st.transition_ids()
    assert np.array_equal(all_t, np.arange(st.n_trans))
    for fam in st.families:
        js = st.traj_ids(families=[fam])
        assert all(st.record(j)["family_id"] == fam for j in js)
        t = st.transition_ids(js)
        assert t.size == st.traj["H"][js].sum()
        assert np.array_equal(np.unique(st.traj_of(t)), js)
    for lab in st.labels:
        js = st.traj_ids(labels=[lab])
        assert all(st.record(j)["label"] == lab for j in js)
    assert np.array_equal(st.traj_ids(H=[10]), np.flatnonzero(st.traj["H"] == 10))
    assert st.traj_ids(split="heldout").size == 0 and st.traj_ids(split="train").size == 8
    # obs rows: transition k goes from row r to r + 1 of the same trajectory
    k = np.arange(st.n_trans)
    r = st.obs_row_of(k)
    j = st.traj_of(k)
    assert np.all(r >= st.traj["first_obs"][j]) and np.all(r + 1 <= st.traj["first_obs"][j] + st.traj["H"][j])
    # multistep starts lie in one trajectory
    ms = st.multistep_starts(all_t, 4)
    assert np.all(st.month_of(ms) + 4 <= st.traj["H"][st.traj_of(ms)])
    assert ms.size == int(np.maximum(st.traj["H"] - 3, 0).sum())
    sub = st.transition_ids(traj_ids=[0, 2])
    ms2 = st.multistep_starts(sub, 2)
    assert set(st.traj_of(ms2).tolist()) <= {0, 2}
    # stratified subset: exactly round(frac * n) per months value, spread over families x labels
    sel = D.stratified_traj_subset(st, 0.5, seed=1, by=("H", "family", "label"))
    for h in np.unique(st.traj["H"]):
        assert (st.traj["H"][sel] == h).sum() == round(0.5 * (st.traj["H"] == h).sum())
    assert np.array_equal(sel, np.unique(sel))
    assert np.array_equal(D.stratified_traj_subset(st, 0.5, seed=1), sel)


def test_loader_shapes_dtypes_values(ref_store):
    import torch

    st = D.TrajStore(ref_store)
    idx = st.transition_ids()
    it = D.OneStepBatches(st, idx, 16, seed=3, device="cpu", num_workers=2,
                          raster_fn=standin_raster_batch, scalars_fn=standin_action_scalars)
    s0, rast, asc, s1 = next(it)
    ids = it.last_ids.copy()
    want = {"tile_index": (torch.int64, (16, 120, 100)), "flags": (torch.float32, (16, 5, 120, 100)),
            "power": (torch.float32, (16, 120, 100)), "half": (torch.float32, (16, 5, 60, 50)),
            "eighth": (torch.float32, (16, 3, 15, 13)), "scalars": (torch.float32, (16, 20)),
            "ledger": (torch.float32, (16, 27)), "terrain": (torch.float32, (16, 30, 25)),
            "com_rate": (torch.float32, (16, 15, 13))}
    for s in (s0, s1):
        assert set(s) == set(want)
        for k, (dt, shape) in want.items():
            assert s[k].dtype == dt and tuple(s[k].shape) == shape, k
    assert rast.dtype == torch.float32 and tuple(rast.shape) == (16, 15, 120, 100)
    assert asc.dtype == torch.float32 and tuple(asc.shape) == (16, 11)
    r = st.obs_row_of(ids)
    for s, rows in ((s0, r), (s1, r + 1)):
        ref = D.expand_state_np(st.tiles[rows], st.half[rows], st.power_packed[rows], st.eighth[rows], st.scalars[rows],
                                st.ledger[rows], st.terrain[rows], st.com_rate[rows])
        for k in want:
            assert np.array_equal(s[k].numpy(), ref[k]), k
    plan = np.asarray(st.plan[ids])
    assert np.array_equal(rast.numpy(), standin_raster_batch(plan))
    assert np.array_equal(asc.numpy(), np.stack([standin_action_scalars(p) for p in plan]))
    # flags really are the bits: the zone flag is set where the raw word has ZONEBIT
    t = np.asarray(st.tiles[r]).astype(np.int64)
    assert np.array_equal(s0["flags"][:, 0].numpy(), ((t & 0x0400) != 0).astype(np.float32))
    assert np.array_equal(s0["flags"][:, 4].numpy(), ((t & 0x8000) != 0).astype(np.float32))
    seq_a = [it.last_ids.copy()] + [(next(it), it.last_ids.copy())[1] for _ in range(3)]
    it.close()
    # same seed -> same batches, whatever the number of workers
    it0 = D.OneStepBatches(st, idx, 16, seed=3, device="cpu", num_workers=0,
                           raster_fn=standin_raster_batch, scalars_fn=standin_action_scalars)
    seq_b = [(next(it0), it0.last_ids.copy())[1] for _ in range(4)]
    assert all(np.array_equal(a, b) for a, b in zip(seq_a, seq_b))
    assert np.all(np.isin(np.concatenate(seq_b), idx))

    k = 3
    ms = D.MultiStepBatches(st, idx, 4, seed=0, device="cpu", k=k, num_workers=0, stacked=True,
                            raster_fn=standin_raster_batch, scalars_fn=standin_action_scalars)
    s, rr, aa = next(ms)
    assert tuple(s["tile_index"].shape) == (4, k + 1, 120, 100) and tuple(s["flags"].shape) == (4, k + 1, 5, 120, 100)
    assert tuple(s["scalars"].shape) == (4, k + 1, 20) and tuple(s["power"].shape) == (4, k + 1, 120, 100)
    assert tuple(rr.shape) == (4, k, 15, 120, 100) and tuple(aa.shape) == (4, k, 11)
    starts = ms.last_ids
    assert np.all(st.month_of(starts) + k <= st.traj["H"][st.traj_of(starts)])
    for b in range(4):
        rows = st.obs_row_of(starts[b]) + np.arange(k + 1)
        assert np.array_equal(s["scalars"][b].numpy(), np.asarray(st.scalars[rows]).astype(np.float32))
        assert np.array_equal(rr[b].numpy(), standin_raster_batch(np.asarray(st.plan[starts[b] + np.arange(k)])))
    # default format: a list of k one-step tuples, chained (state_t+1 of step t is state_t of step t+1)
    ml = D.MultiStepBatches(st, idx, 4, seed=0, device="cpu", k=k, num_workers=0,
                            raster_fn=standin_raster_batch, scalars_fn=standin_action_scalars)
    win = next(ml)
    assert np.array_equal(ml.last_ids, starts) and len(win) == k
    for t, (a0, r0, c0, a1) in enumerate(win):
        assert set(a0) == set(want) and tuple(a0["flags"].shape) == (4, 5, 120, 100) and tuple(r0.shape) == (4, 15, 120, 100)
        assert tuple(c0.shape) == (4, 11) and np.array_equal(a0["tile_index"].numpy(), s["tile_index"][:, t].numpy())
        assert np.array_equal(a1["scalars"].numpy(), s["scalars"][:, t + 1].numpy())
        if t + 1 < k:
            assert np.array_equal(a1["half"].numpy(), win[t + 1][0]["half"].numpy())


def _make_old(src, dst):
    """A dc-store-1 copy: the store as it was before the ledger (three files and manifest entries removed)."""
    shutil.copytree(src, dst)
    for k in D.LEDGER_FILES:
        (dst / D.ALL_FILES[k][0]).unlink()
    man = json.loads((dst / "manifest.json").read_text())
    for k in D.LEDGER_FILES:
        del man["arrays"][k]
    man["store_format"] = "dc-store-1"
    (dst / "manifest.json").write_text(json.dumps(man))


def _bf_crash_child(path):
    D.backfill_ledger(path, workers=2, compile_plan=standin_compile_plan, chunk=3, log=lambda s: None, crash_after_chunks=1)


def test_backfill_reproduces_generation_and_resumes(ref_store, tmp_path):
    p = tmp_path / "old"
    _make_old(ref_store, p)
    st = D.TrajStore(p)
    assert not st.has_ledger and "ledger" not in st.trajectory(0)
    with pytest.raises(ValueError, match="ledger"):
        D.OneStepBatches(st, st.transition_ids(), 4, 0, "cpu", num_workers=0,
                         raster_fn=standin_raster_batch, scalars_fn=standin_action_scalars)
    old = D.OneStepBatches(st, st.transition_ids(), 4, 0, "cpu", num_workers=0, ledger=False,
                           raster_fn=standin_raster_batch, scalars_fn=standin_action_scalars)
    assert "ledger" not in next(old)[0]
    proc = mp.get_context("fork").Process(target=_bf_crash_child, args=(p,))
    proc.start()
    proc.join(60)
    assert proc.exitcode == 17
    assert len((p / D.BACKFILL_JOURNAL).read_text().splitlines()) == 1
    assert not (p / "ledger.i64").exists() and (p / "ledger.i64.part").exists()
    r = D.backfill_ledger(p, workers=2, compile_plan=standin_compile_plan, chunk=3, log=lambda s: None)
    assert r["published"] and r["checked"] == 8 and r["mismatched"] == 0 and r["chunks_done"] == 3
    assert r["observations_compared"] == st.n_obs
    shas = _shas(ref_store)
    for k in D.LEDGER_FILES:
        f = D.ALL_FILES[k][0]
        assert hashlib.sha256((p / f).read_bytes()).hexdigest() == hashlib.sha256((ref_store / f).read_bytes()).hexdigest()
        assert not (p / (f + ".part")).exists()
    assert all(_shas(p)[f] == shas[f] for f in DATA_FILES)
    st2 = D.TrajStore(p)
    assert st2.manifest["store_format"] == D.STORE_FORMAT and st2.manifest["store_format_at_generation"] == "dc-store-1"
    assert st2.manifest["backfills"][0]["verification"]["mismatched"] == 0
    assert D.check_manifest(st2)["mismatched"] == []
    assert D.verify(st2, compile_plan=standin_compile_plan)["mismatched"] == 0
    assert D.backfill_ledger(p, compile_plan=standin_compile_plan, log=lambda s: None)["already_backfilled"]


def test_backfill_stops_on_mismatch(ref_store, tmp_path):
    p = tmp_path / "old"
    _make_old(ref_store, p)
    st = D.TrajStore(p)
    with open(p / "tiles.u16", "r+b") as f:
        f.seek((st.record(2)["first_obs"] + 1) * D.ROW_BYTES["tiles"] + 999 * 2)
        w = f.read(2)
        f.seek((st.record(2)["first_obs"] + 1) * D.ROW_BYTES["tiles"] + 999 * 2)
        f.write(bytes([w[0] ^ 4, w[1]]))
    man_before = (p / "manifest.json").read_text()
    r = D.backfill_ledger(p, workers=1, compile_plan=standin_compile_plan, chunk=3, log=lambda s: None)
    assert not r["published"] and r["mismatched_ids"] == [2] and r["by_field"] == {"tiles": 1}
    assert not (p / "ledger.i64").exists() and (p / "manifest.json").read_text() == man_before
    with pytest.raises(RuntimeError, match="mismatches"):
        D.backfill_ledger(p, workers=1, compile_plan=standin_compile_plan, chunk=3, log=lambda s: None)


def test_ledger_summary(ref_store):
    st = D.TrajStore(ref_store)
    ls = D.ledger_summary(st, block=3)
    k = np.arange(st.n_trans)
    r = st.obs_row_of(k)
    L = np.asarray(st.ledger)
    d = L[r + 1] - L[r]
    from dc.engine import LEDGER_NAMES
    for i, n in enumerate(LEDGER_NAMES):
        assert ls["ledger"][n]["share_transitions_changed"] == pytest.approx(np.mean(d[:, i] != 0))
        assert ls["ledger"][n]["mean_abs_change"] == pytest.approx(np.mean(np.abs(d[:, i])))
    for name in ("terrain", "com_rate"):
        a = np.asarray(getattr(st, name)).astype(np.int32)
        dd = (a[r + 1] != a[r]).reshape(len(k), -1)
        assert ls[name]["share_cells_changed_mean"] == pytest.approx(dd.mean())
        assert ls[name]["share_transitions_any_cell_changed"] == pytest.approx(dd.any(axis=1).mean())
    assert set(ls["ledger"]) == set(LEDGER_NAMES) and ls["transitions"] == st.n_trans
    # integer sums in float64 are exact, so the block size cannot change the numbers
    assert D.summarise(st, workers=1, raster_fn=False)["ledger_change"] == ls


def test_summary_by_type_and_footprint(ref_store):
    st = D.TrajStore(ref_store)
    s = D.summarise(st, workers=1, raster_fn=standin_raster_batch)
    oc = s["one_month_change"]
    bt = oc["by_behaviour_type"]
    assert sum(v["transitions"] for v in bt.values()) == st.n_trans
    assert sum(v["trajectories"] for v in bt.values()) == st.n_traj
    # recompute the footprint split for every transition directly
    fp_tot = cin_tot = chg_tot = 0
    for k in range(st.n_trans):
        o0, row, o1 = st.transition(k)
        chg = (o0.tiles & 0x3FF) != (o1.tiles & 0x3FF)
        fp = standin_raster_batch(row[None])[0].any(axis=0)
        fp_tot += int(fp.sum())
        cin_tot += int((chg & fp).sum())
        chg_tot += int(chg.sum())
    a = oc["all_transitions"]
    assert a["changed_tiles_mean"] * st.n_trans == pytest.approx(chg_tot)
    assert a["footprint"]["footprint_tiles_mean"] * st.n_trans == pytest.approx(fp_tot)
    assert a["footprint"]["changed_inside_footprint_mean"] * st.n_trans == pytest.approx(cin_tot)
    assert a["footprint"]["changed_outside_footprint_mean"] * st.n_trans == pytest.approx(chg_tot - cin_tot)
    nz = bt["noop"]
    assert nz["footprint"]["footprint_tiles_mean"] == 0 and nz["footprint"]["changed_inside_footprint_mean"] == 0


def test_gen_data_cli(tmp_path):
    root = tmp_path / "data"
    G.main(["all", "--provider", f"{__file__}:STANDIN", "--root", str(root), "--workers", "2",
            "--train-h", "6:10,10:2", "--train-eval-h", "6:3", "--heldout-per-family", "6:2,10:1",
            "--summary-out", str(tmp_path / "summary.json"), "--verify-train-n", "4", "--min-free-gb", "0"])
    s = json.loads((tmp_path / "summary.json").read_text())
    assert s["verify"]["train_full"]["checked"] == 4 and s["verify"]["train_full"]["mismatched"] == 0
    assert s["verify"]["heldout_eval"]["checked"] == 3 and s["verify"]["heldout_eval"]["mismatched"] == 0
    tf = s["splits"]["train_full"]
    assert tf["counts"]["trajectories"] == 12 and tf["counts"]["transitions"] == 80
    assert tf["one_month_change"]["transitions"] == 80
    assert set(tf["one_month_change"]["by_behaviour_type"]) <= {"random_editor", "noop", "budget_sweep"}
    assert "footprint" in tf["one_month_change"]["all_transitions"]
    assert (tmp_path / "verify_train_full.json").exists() and s["generation"]["train_full"]["n"] == 12
    assert s["splits"]["heldout_eval"]["counts"]["by_split"] == {"heldout": {"trajectories": 3, "transitions": 22}}
    assert s["train_small"]["by_H"] == {"6": 1}
    st, idx = D.open_split("train_small", root)
    assert idx.size == 6 and st.path.name == "train_full"
    ev = D.TrajStore(root / "train_eval")
    assert not (set(ev.traj["seed"].tolist()) & set(D.TrajStore(root / "train_full").traj["seed"].tolist()))


# ----------------------------------------------------------------------------------------------
# stand-in generation of a few thousand transitions (not a test)
# ----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["standin"])
    ap.add_argument("--root", required=True)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    G.main(["all", "--provider", f"{__file__}:STANDIN", "--root", a.root, "--workers", str(a.workers),
            "--train-h", "48:50,120:5", "--train-eval-h", "48:10", "--heldout-per-family", "48:4,120:1",
            "--summary-out", str(Path(a.root) / "summary.json"), "--verify-train-n", "500", "--min-free-gb", "0"])
