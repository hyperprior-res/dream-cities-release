"""Tests for ``code/scripts/rl_axis.py``: the binomial plug-in, the one-way and two-way bootstraps of
ratio estimators (point values, the paper's checkpoint interval, pairing by city), the perfect emulator's seed
scheme, the 4-of-8 verdict, the depth counts, and, where the stored files exist, one RL run end to end (records
against summary; plan 0 replayed on its 32 oracle seeds against the stored margins). CPU only; well under a minute."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "code" / "scripts", ROOT / "code", ROOT / "hpr-dream"):
    sys.path.insert(0, str(p))

import rl_axis as X  # noqa: E402
import hpr_dream.stats as hs  # noqa: E402
from dc import audit as A  # noqa: E402
from dc import tasks as T  # noqa: E402

MAIN_RUN = "os_50m_full-samples_006000000__grow__s0__tasks_v2_H24"


def test_ladder_pattern_is_the_papers():
    for f in ("paper/scripts/make_numbers.py", "code/scripts/analyse_ladder.py"):
        m = re.search(r'LADDER_RUN = re\.compile\(r"([^"]+)"\)', (ROOT / f).read_text())
        assert m and m.group(1) == X.LADDER_RUN.pattern, f


def test_binomial_tail():
    assert X.binom_tail(0.0) == 0.0
    assert X.binom_tail(1.0) == pytest.approx(1.0)
    assert X.binom_tail(0.5) == pytest.approx(163 / 256)
    p = 0.3
    assert X.binom_tail(p) == pytest.approx(sum(math.comb(8, j) * p ** j * (1 - p) ** (8 - j) for j in range(4, 9)))


def _rows(rng, cks, fams, cities, n_inst, key="v", shift=0.0):
    rows = []
    for ck in cks:
        for f in fams:
            for s in range(2):
                run = f"{ck}__{f}__s{s}"
                for i in range(n_inst[f]):
                    rows.append({"run": run, "ck": ck, "task": f, "instance": f"{f}{i}", "cluster": cities[i % len(cities)],
                                 key: float(rng.random() + shift)})
    return rows


def test_family_mean_weighting_and_paper_interval():
    rng = np.random.default_rng(0)
    cks = [f"c{j}" for j in range(6)]
    n_inst = {"a": 5, "b": 3}
    rows = _rows(rng, cks, ["a", "b"], [f"city{j}" for j in range(5)], n_inst)
    arm = X.Arm(rows)
    e = X.boot([(1, arm, "v")], n_boot=400)
    runs = sorted({r["run"] for r in rows})
    rv = {u: np.mean([r["v"] for r in rows if r["run"] == u]) for u in runs}
    fam_mean = np.mean([np.mean([rv[u] for u in runs if f"__{f}__" in u]) for f in ("a", "b")])
    assert e["value"] == pytest.approx(fam_mean)
    assert e["value"] == pytest.approx(np.mean(list(rv.values())))        # equal runs per family: mean over runs
    ref = hs.conditional_mean(np.array([rv[u] for u in runs]), None, np.array([u.split("__")[0] for u in runs]),
                              n_boot=400, seed=X.CK_SEED, bca=True)
    assert e["checkpoint_only"]["lo"] == ref.lo and e["checkpoint_only"]["hi"] == ref.hi
    assert e["checkpoint_only"]["bca_lo"] == pytest.approx(ref.bca_lo)
    # two-way intervals are at least as wide as the city-only ones here (both sources of variation)
    tw, cy = e["twoway"], e["city_only"]
    assert tw["hi"] - tw["lo"] >= 0.9 * (cy["hi"] - cy["lo"])
    iw = X.boot([(1, X.Arm(rows, "instance"), "v")], n_boot=50)
    assert iw["value"] == pytest.approx(np.mean([r["v"] for r in rows]))


def test_difference_pairs_by_city():
    rng = np.random.default_rng(1)
    cities = [f"city{j}" for j in range(8)]
    rows = _rows(rng, ["c0"], ["a"], cities, {"a": 8})
    same = X.boot([(1, X.Arm(rows), "v"), (-1, X.Arm([dict(r) for r in rows]), "v")], n_boot=200)
    assert same["value"] == pytest.approx(0.0)
    assert same["city_only"]["lo"] == pytest.approx(0.0) and same["city_only"]["hi"] == pytest.approx(0.0)
    assert same["checkpoint_only"] is None                               # one checkpoint
    eng = [dict(r, ck="engine", run="eng", v=r["v"] - 0.25) for r in rows if r["run"].endswith("s0")]
    d = X.boot([(1, X.Arm(rows), "v"), (-1, X.Arm(eng), "v")], n_boot=200)
    s1 = np.mean([r["v"] for r in rows if r["run"].endswith("s1")])
    s0 = np.mean([r["v"] for r in rows if r["run"].endswith("s0")])
    assert d["value"] == pytest.approx((s0 + s1) / 2 - (s0 - 0.25))
    assert d["twoway"] == {k: d["city_only"][k] for k in ("lo", "hi")}  # no checkpoint draw: two-way = city only


def test_boot_refuses_missing_values():
    rows = [{"run": "r", "ck": "c", "task": "a", "instance": "i", "cluster": "k", "v": 1.0}]
    assert X.boot([(1, X.Arm(rows), "w")]) is None


def test_perfect_seeds_follow_the_engine_seed_judge():
    inst = A.load_instances(X.TASKS_FILE, horizon=X.H)[0]
    plan = np.zeros((X.H, A.N_COLS), dtype=np.int16)
    s = X.perfect_seeds(inst, A.effective(plan[None], inst.task, X.H)[0], "some-run")
    res = A.reserved_seeds(inst.start_id, X.H, T.ORACLE_N)
    want = [A.fresh_seed(("audit-seedcheck", inst.start_id, X.STREAM, "some-run", X.MONTHS, 0, k), res)[0]
            for k in range(8)]
    assert s == want and len(set(s)) == 8
    assert not set(s) & res and not set(s) & set(A.oracle_seed_list(inst, T.ORACLE_N))


def test_verdict_is_four_of_eight(monkeypatch):
    for m, acc in (([0.0, 0.1, 0.2, 0.0, -1, -1, -1, -1], True), ([0.0, 0.1, 0.2, -0.01, -1, -1, -1, -1], False)):
        monkeypatch.setattr(X.A, "task_margin", lambda inst, traj, m=m: np.array(m))
        v = X.verdict_from_traj(None, None)
        assert v["accept"] is acc and v["n_pass"] == (4 if acc else 3)


def test_depth_counts():
    def rec(i, gp, oa, share, task="grow"):
        n = int(round(share * 32))
        return {"method": "random", "budget": 1000, "instance": f"i{i}", "task": task, "grader_p": gp,
                "oracle_accept": oa, "oracle_share": share, "oracle_margin": -0.1 * (i + 1), "oracle_rule": "majority",
                "oracle_n_seeds": 32, "oracle_accept_seeds": [True] * n + [False] * (32 - n), "plan_id": f"p{i}"}
    recs = [rec(0, 0.5, False, 0.0), rec(1, 0.75, False, 2 / 32), rec(2, 0.625, False, 0.4375), rec(3, 0.25, False, 0.0),
            rec(4, 1.0, True, 0.75)]
    d = X.depth_of(recs, "random", 1000, {f"i{i}" for i in range(5)})
    assert d["n_false_acceptances"] == 3 and d["n_share_below_0_1"] == 2 and d["n_share_zero"] == 1
    assert d["median_oracle_share"] == pytest.approx(2 / 32)
    assert X.depth_of(recs, "random", 1000, {f"i{i}" for i in range(6)})["status"] != "ok"


def test_macro_parsing():
    assert X.macro_value("\\textminus0.331") == pytest.approx(-0.331)
    assert X.macro_value("+0.178") == pytest.approx(0.178)
    assert X.macro_interval("[\\textminus0.042, +0.092]") == (pytest.approx(-0.042), pytest.approx(0.092))


@pytest.mark.skipif(not (X.RL_RESULTS / MAIN_RUN).is_dir() or not (X.RL_CACHE / MAIN_RUN).is_dir(),
                    reason="stored RL run not present")
def test_stored_run_end_to_end():
    rows = X.instance_rows(MAIN_RUN, "os_50m_full-samples_006000000", X.MONTHS)
    X.summary_check(MAIN_RUN, X.MONTHS, rows)
    insts = {i.key: i for i in A.load_instances(X.TASKS_FILE, horizon=X.H)}
    prep = X.prepare_run(MAIN_RUN, insts)
    jobs = X._jobs(prep)
    check = jobs[-T.ORACLE_N:]                                # plan 0 of the first instance on its oracle seeds
    res = [b"\0" * (X.H + 1) * A.NUM_SCALARS * 8] * (len(jobs) - len(check)) + [A._replay_job(j) for j in check]
    out = X.finish_run(prep, res)
    assert out["oracle_check"]["max_abs_margin_error"] <= 1e-9
    assert len(out["perfect_accept"]) == len(rows)
