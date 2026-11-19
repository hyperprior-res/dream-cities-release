"""Tests for ``code/scripts/analyse_ladder.py``: the rank statistics against scipy
and ``hpr_dream.stats``, synthetic pairs with a known correlation on the pooled 120-city variable, a family
confound, reliability under known measurement noise, split-sample reliability and Spearman-Brown for forms of
unequal length, the protocol's power statement, the decision rule, the parallel path, and the reading of a small tree
of result files (two city files, a run in progress, a missing RL seed, the replication and the coverage reports).
CPU only; well under a minute."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats as sps
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "code" / "scripts", ROOT / "code", ROOT / "hpr-dream"):
    sys.path.insert(0, str(p))

import analyse_ladder as al  # noqa: E402
import hpr_dream.stats as hs  # noqa: E402

FAM = al.FAMILIES
NB = 300
NAN = float("nan")


def blank_row(ckpt: str, family: str, lineage: str) -> dict:
    r = {"checkpoint": ckpt, "family": family, "lineage": lineage, f"rl_n_seeds_{al.SNAPSHOTS[-1]}": 3,
         "random_c40_n_1000": 40, "random_c80_n_1000": 80, "random_c120_n_1000": 120}
    for k, _ in al.X_VARS + al.Y_VARS:
        r[k] = NAN
    for k, _ in al.Y_VARS:
        r[k.replace("_1000000", "_sd_1000000")] = NAN
    return r


def synthetic(n_ckpt: int, x_of, y_of, seed: int = 0, n_lineages: int = 6) -> list[dict]:
    """``x_of(rng, f_index, z)`` / ``y_of(...)``: the pair's primary audit value and RL value from a shared latent
    z ~ N(0, 1)."""
    rng = np.random.default_rng(seed)
    rows = []
    for c in range(n_ckpt):
        for fi, f in enumerate(FAM):
            z = rng.normal()
            r = blank_row(f"ck{c:03d}", f, f"lin{c % n_lineages}")
            r[al.PRIMARY_X] = float(x_of(rng, fi, z))
            r["rl_inflation_1000000"] = float(y_of(rng, fi, z))
            r["rl_gap_1000000"] = r["rl_inflation_1000000"]
            r["rl_gap_sd_1000000"] = r["rl_inflation_sd_1000000"] = 0.01
            rows.append(r)
    return rows


def primary(res):
    return res["main"][al.POOLED][al.PRIMARY_Y]


# --------------------------------------------------------------------------------------------------------------


def test_rank_statistics_match_scipy():
    rng = np.random.default_rng(1)
    for n in (2, 3, 7, 24, 120):
        for _ in range(20):
            x = rng.integers(0, 5, n).astype(float)
            y = rng.integers(0, 4, n).astype(float) + 0.1 * x
            assert np.array_equal(al.midrank(x), sps.rankdata(x))
            if np.ptp(x) == 0 or np.ptp(y) == 0:
                assert math.isnan(al.spearman(x, y)) and math.isnan(al.kendall(x, y))
                continue
            assert al.spearman(x, y) == pytest.approx(sps.spearmanr(x, y).statistic, abs=1e-12)
            assert al.kendall(x, y) == pytest.approx(sps.kendalltau(x, y).statistic, abs=1e-12)
            assert al.pearson(x, y) == pytest.approx(sps.pearsonr(x, y).statistic, abs=1e-12)
    assert math.isnan(al.spearman(np.ones(5), np.arange(5.0)))


def test_cluster_bootstrap_equals_the_package_estimator():
    rng = np.random.default_rng(2)
    x, y = rng.normal(size=60), rng.normal(size=60)
    cl = np.repeat([f"c{i}" for i in range(12)], 5)
    mine = al.cluster_boot(lambda ix: al.spearman(x[ix], y[ix]), cl, NB, 0)
    ref = hs.clustered_spearman(x, y, cl, n_boot=NB, seed=0)
    assert (mine.value, mine.n_units, mine.n_clusters, mine.n_boot_undefined) == \
        pytest.approx((ref.value, ref.n_units, ref.n_clusters, ref.n_boot_undefined), abs=1e-12)
    assert mine.lo == pytest.approx(ref.lo, abs=1e-12) and mine.hi == pytest.approx(ref.hi, abs=1e-12)
    mk = al.cluster_boot(lambda ix: al.kendall(x[ix], y[ix]), cl, NB, 0)
    rk = hs.clustered_kendall(x, y, cl, n_boot=NB, seed=0)
    assert (mk.value, mk.lo, mk.hi) == pytest.approx((rk.value, rk.lo, rk.hi), abs=1e-12)


def test_known_correlation_on_the_pooled_variable_is_recovered_and_supported():
    # the 40- and 80-city rates are binomial draws around a latent rate; the pooled 120 is their instance-weighted
    # mean; the RL variable shares the latent. The test reads only the pooled variable for the decision.
    rng = np.random.default_rng(7)
    rows = []
    for c in range(24):
        for f in FAM:
            z = rng.normal()
            p = ndtr(0.6 * z - 0.6)
            h40, h80 = rng.binomial(40, p), rng.binomial(80, p)
            r = blank_row(f"ck{c:03d}", f, f"lin{c % 6}")
            r["random_c40_hack_1000"], r["random_c80_hack_1000"] = h40 / 40, h80 / 80
            r["random_c120_hack_1000"] = (h40 + h80) / 120
            r["rl_inflation_1000000"] = r["rl_gap_1000000"] = z + 0.3 * rng.normal()
            r["rl_inflation_sd_1000000"] = r["rl_gap_sd_1000000"] = 0.01
            rows.append(r)
    res = al.analyse(rows, n_boot=NB, seed=0)
    assert res["status"] == "complete" and res["n_pairs_primary"] == 120
    b = primary(res)
    assert b["role"] == "decides the main claim" and b["decision"] == "supported" and b["decision_status"] == "made"
    # the deciding statistic is the pooled variable's Spearman, and the 40 and the 80 are reported beside it
    xs = [r["random_c120_hack_1000"] for r in rows]
    ys = [r["rl_inflation_1000000"] for r in rows]
    assert b["pooled_spearman"].value == pytest.approx(sps.spearmanr(xs, ys).statistic)
    for s in al.SETS:
        assert "decision" not in res["main"][s][al.PRIMARY_Y]
        assert res["main"][s][al.PRIMARY_Y]["role"] == "reported beside it"
    assert "decision" not in res["main"][al.POOLED]["rl_gap_1000000"]
    # more cities, less attenuation: the pooled variable correlates at least as well as the 40 alone here
    assert b["pooled_spearman"].value > res["main"]["c40"][al.PRIMARY_Y]["pooled_spearman"].value
    assert all(b["per_family"][f]["n"] == 24 for f in FAM)
    assert b["pooled_spearman_lineage"].n_clusters == 6 and b["pooled_spearman"].n_clusters == 24
    assert b["pooled_kendall"].value == pytest.approx(sps.kendalltau(xs, ys).statistic)


def test_known_correlation_is_recovered():
    # Pearson 0.8 between x and y (shared latent, independent noise of sd 0.5); Spearman 6/pi asin(0.4) = 0.786.
    truth = 6 / math.pi * math.asin(0.8 / 2)
    rows = synthetic(24, lambda rng, fi, z: ndtr(z + 0.5 * rng.normal()), lambda rng, fi, z: z + 0.5 * rng.normal())
    b = primary(al.analyse(rows, n_boot=NB, seed=0))
    e = b["pooled_spearman"]
    assert abs(e.value - truth) < 0.08 and e.lo < truth < e.hi
    assert abs(b["within_mean_spearman"].value - truth) < 0.12
    assert abs(b["ranked_within_spearman"].value - truth) < 0.1


def test_null_is_falsified_and_partial_inputs_get_no_decision():
    rows = synthetic(100, lambda rng, fi, z: ndtr(rng.normal()), lambda rng, fi, z: rng.normal(), seed=3)
    res = al.analyse(rows, n_boot=200, seed=0)
    b = primary(res)
    assert abs(b["pooled_spearman"].value) < 0.1 and b["pooled_spearman"].hi < al.THRESHOLD
    assert al.decide(b["pooled_spearman"]) == "falsified"
    assert res["status"] == "partial" and b["decision"] is None   # 100 checkpoints is not the protocol ladder
    assert b["decision_status"] == "not made: partial inputs"
    assert "no decision" in al.decision_text(b, res["status"])


def test_within_family_statistics_remove_a_family_confound():
    # inside every family y rises with x; across families the offsets run the other way
    rows = synthetic(24, lambda rng, fi, z: 0.1 * fi + 0.02 * ndtr(z), lambda rng, fi, z: -10.0 * fi + ndtr(z))
    res = al.analyse(rows, n_boot=NB, seed=0)
    b = primary(res)
    assert b["pooled_spearman"].value < -0.5
    assert res["status"] == "complete" and b["decision"] == "falsified"
    for f in FAM:
        assert b["per_family"][f]["spearman"].value == pytest.approx(1.0)
        assert b["per_family"][f]["kendall"].value == pytest.approx(1.0)
    assert b["within_mean_spearman"].value == pytest.approx(1.0) and b["within_mean_spearman"].lo == pytest.approx(1.0)
    assert b["ranked_within_spearman"].value == pytest.approx(1.0)


def test_parallel_blocks_equal_serial():
    rows = synthetic(10, lambda rng, fi, z: ndtr(z + rng.normal()), lambda rng, fi, z: z + rng.normal(), seed=9)
    want = [(al.PRIMARY_X, al.PRIMARY_Y), (al.PRIMARY_X, "rl_gap_1000000")]
    a = al.compute_blocks(rows, want, 100, 0, 1)
    b = al.compute_blocks(rows, want, 100, 0, 2)
    def fields(e):
        return (e.value, e.lo, e.hi, e.n_units, e.n_clusters, e.n_boot_undefined)

    for k in want:
        for stat in ("pooled_spearman", "pooled_kendall", "within_mean_spearman", "ranked_within_spearman"):
            assert fields(a[k][stat]) == fields(b[k][stat])


def test_reliability_under_known_measurement_noise():
    rng = np.random.default_rng(4)
    n_ck, n_inst, seed_sd, k = 3000, 40, 0.1, 3
    rows = []
    for c in range(n_ck):
        for f in FAM:
            p = rng.uniform(0.1, 0.5)                    # variance 0.4^2 / 12 across checkpoints
            mu = rng.normal(0, 0.1)
            seeds = mu + seed_sd * rng.normal(size=k)
            r = blank_row(f"ck{c}", f, "lin")
            r["random_c40_hack_1000"] = rng.binomial(n_inst, p) / n_inst
            r["rl_gap_1000000"] = r["rl_inflation_1000000"] = float(seeds.mean())
            r["rl_gap_sd_1000000"] = r["rl_inflation_sd_1000000"] = float(seeds.std(ddof=1))
            rows.append(r)
    rel = al.reliability(rows, "random_c40_hack_1000", "random_c40_n_1000", ["rl_gap_1000000"])
    vp = 0.4 ** 2 / 12
    noise = (0.3 - (0.09 + vp)) / n_inst                 # E[p (1 - p)] / n
    lam_x = vp / (vp + noise)
    lam_y = 0.01 / (0.01 + seed_sd ** 2 / k)
    for f in FAM:
        e = rel[f]
        assert e["audit"]["reliability"] == pytest.approx(lam_x, abs=0.04)
        assert e["rl_gap_1000000"]["reliability"] == pytest.approx(lam_y, abs=0.04)
        fac = math.sqrt(e["audit"]["reliability"] * e["rl_gap_1000000"]["reliability"])
        assert e["rl_gap_1000000"]["attenuation_factor"] == pytest.approx(fac)
        assert e["rl_gap_1000000"]["observed_if_true_0.4"] == pytest.approx(0.4 * fac)


def test_spearman_brown_for_forms_of_unequal_length_inverts_exactly():
    for ru, k1, k2 in ((0.01, 40, 80), (0.05, 38, 75), (0.2, 35, 70)):
        r = math.sqrt(al.sb(ru, k1) * al.sb(ru, k2))
        out = al.sb_from_split(r, k1, k2)
        assert out["rho_instance"] == pytest.approx(ru, abs=1e-9)
        assert out["rho_pooled"] == pytest.approx(al.sb(ru, k1 + k2), abs=1e-9)
    assert al.sb(0.75 / (3 - 2 * 0.75), 3) == pytest.approx(0.75)          # tripling 1/3 of a 0.75 measure
    assert math.isnan(al.sb_from_split(-0.1, 40, 80)["rho_pooled"])


def test_split_sample_reliability_matches_known_noise():
    # true rate per checkpoint and family; the 40 and the 80 cities are independent binomial draws around it
    rng = np.random.default_rng(6)
    rows = []
    n1, n2 = 40, 80
    for c in range(3000):
        for f in FAM:
            p = rng.uniform(0.1, 0.5)
            h1, h2 = rng.binomial(n1, p), rng.binomial(n2, p)
            r = blank_row(f"ck{c}", f, "lin")
            r.update({"random_c40_hack_1000": h1 / n1, "random_c80_hack_1000": h2 / n2,
                      "random_c120_hack_1000": (h1 + h2) / (n1 + n2), "random_c40_n_1000": n1, "random_c80_n_1000": n2})
            rows.append(r)
    ss = al.split_sample(rows)
    vp = 0.4 ** 2 / 12
    ep = 0.3 - (0.09 + vp)
    lam = {k: vp / (vp + ep / k) for k in (n1, n2, n1 + n2)}
    for f in FAM:
        e = ss[f]
        assert e["n_checkpoints"] == 3000
        assert e["pearson"] == pytest.approx(math.sqrt(lam[n1] * lam[n2]), abs=0.03)
        assert e["spearman_brown"]["rho_k1"] == pytest.approx(lam[n1], abs=0.04)
        assert e["spearman_brown"]["rho_k2"] == pytest.approx(lam[n2], abs=0.04)
        assert e["spearman_brown"]["rho_pooled"] == pytest.approx(lam[n1 + n2], abs=0.04)
        assert e["binomial"]["c120"] == pytest.approx(lam[n1 + n2], abs=0.04)
    few = al.split_sample(rows[:10])                                         # 2 checkpoints per family
    assert all("status" in few[f] for f in FAM)


def test_power_reproduces_the_protocol_statement():
    assert al.fisher_power(0.4, 47) == pytest.approx(0.80, abs=0.01)
    pw = al.power_block(120, 24)
    assert pw["n_independent_for_80_per_cent"] == 47
    assert pw["at_icc"]["0.3"]["n_eff"] == pytest.approx(120 / 2.2)       # protocol: "about 55"
    assert pw["at_icc"]["0.5"]["n_eff"] == pytest.approx(40.0)            # protocol: "40 at 0.5"
    rng = np.random.default_rng(5)
    g = np.repeat(np.arange(400), 5)
    v = rng.normal(size=400)[g] + rng.normal(size=g.size)                 # ICC 0.5
    assert al.icc1(v, g) == pytest.approx(0.5, abs=0.06)


def test_decision_rule():
    E = lambda v, lo, hi, c=24: hs.Estimate(v, lo, hi, 120, c, 2000, 0)  # noqa: E731
    assert al.decide(E(0.5, 0.1, 0.8)) == "supported"
    assert al.decide(E(0.1, -0.2, 0.35)) == "falsified"
    assert al.decide(E(0.3, -0.1, 0.6)) == "undecided at this power"
    assert al.decide(E(0.45, -0.05, 0.8)) == "undecided at this power"     # interval includes 0
    assert al.decide(E(0.35, 0.05, 0.6)) == "undecided at this power"      # estimate below 0.4
    assert al.decide(E(0.9, 0.9, 0.9, c=1)) == "not computable"            # one cluster is no interval


# --------------------------------------------------------------------------------------------------------------
# a small tree of result files


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _wjson(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))


def _wrecords(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


ATTACKER = {"random": "random_shooting", "best_of_n": "best_of_n", "cem_seeded": "cem_seeded"}


def recs_for(inst, starts, method, budgets, hacked, accepted):
    """Records: in family f, instance j is accepted by the judge when j < hacked[f] (oracle rejects) or
    j in accepted (oracle accepts)."""
    out = []
    for f in FAM:
        for j, iid in enumerate(inst[f]):
            for B in budgets:
                out.append({"instance": iid, "method": method, "attacker": ATTACKER[method], "scoring": "margin",
                            "budget": B, "attacker_seed": 0, "task": f, "cluster": starts[j], "in_band": True,
                            "oracle_rule": "majority", "grader_p": 1.0 if (j < hacked[f] or j in accepted) else 0.0,
                            "oracle_accept": j in accepted})
    return out


def write_run(d: Path, recs, tasks_sha, judge_sha, pool_stats=True):
    _wrecords(d / "records.jsonl.gz", recs)
    curve = {}
    for r in recs:
        curve.setdefault((r["attacker"], r["budget"]), []).append(r["grader_p"] >= 0.5 and not r["oracle_accept"])
    _wjson(d / "card.json", {"meta": {"judge": {"ckpt_sha256": judge_sha}}, "hackability_curve": [
        {"attacker": a, "scoring": "margin", "budget": B, "hackability": {"value": float(np.mean(v))}}
        for (a, B), v in curve.items()]})
    _wjson(d / "config.json", {"config": {"tasks_sha256": tasks_sha}})
    if pool_stats:
        _wjson(d / "pool_stats.json", {"flip_rates": {"by_task": {f: {"fp": 0.1, "fn": 0.2, "n_oracle_accept": 10,
                                                                      "n_oracle_reject": 90, "n_behaviour_plans": 100}
                                                                  for f in FAM}}})


def ckpt_run(ck: Path, run: str, cfg: dict, ns) -> dict:
    _wjson(ck / run / "config.json", cfg)
    shas = {}
    for n in ns:
        p = ck / run / f"samples_{n:09d}.pt"
        p.write_bytes(f"{run}{n}".encode())
        shas[n] = _sha(p.read_bytes())
        (ck / run / f"samples_{n:09d}.pt.sha256").write_text(f"{shas[n]}  {p.name}\n")
    return shas


def build_tree(tmp: Path) -> dict:
    root, ck, covtree = tmp / "repo", tmp / "ckpt", tmp / "covtree"
    starts40, starts80 = ["s-a", "s-b", "s-c", "s-d"], ["s-e", "s-f"]
    tf = {}
    for s, starts, name in (("c40", starts40, "tasks.json"), ("c80", starts80, "tasksx.json")):
        tf[s] = root / "data" / name
        _wjson(tf[s], {"meta": {}, "instances": [{"family_id": st, "start_id": f"{st}-v0", "task": f, "horizon": "24"}
                                                for f in FAM for st in starts]})
    tsha = {s: _sha(tf[s].read_bytes()) for s in tf}
    inst = {s: {f: [f"{st}-v0|{f}|H24" for st in starts] for f in FAM}
            for s, starts in (("c40", starts40), ("c80", starts80))}
    data = {"index": "train_full", "index_len": 3000}
    os_sha = ckpt_run(ck, "os_50m_full", {"train": {"size": "50m", "mode": "onestep", "samples": 6_000_000, "seed": 0,
                                                    "save_fracs": [0.5, 1.0], "init_from": ""}, "data": data},
                      (3_000_064, 6_000_000))
    sf_sha = ckpt_run(ck, "sf_50m_full", {"train": {"size": "50m", "mode": "selfforce", "samples": 1_500_000, "seed": 0,
                                                    "save_fracs": [0.5, 1.0],
                                                    "init_from": str(ck / "os_50m_full" / "samples_006000000.pt")},
                                          "data": data}, (750_080, 1_500_032))
    ckpt_run(ck, "os_50m_full_s1", {"train": {"size": "50m", "mode": "onestep", "samples": 6_000_000, "seed": 1,
                                              "save_fracs": [0.5, 1.0]}, "data": data}, (3_000_064, 6_000_000))
    cov_sha = ckpt_run(ck, "os_50m_cov", {"train": {"size": "50m", "mode": "onestep", "samples": 6_000_000, "seed": 0,
                                                    "save_fracs": [0.5, 1.0], "init_from": ""},
                                          "data": {"index": "train_full_cov12", "index_len": 4200}}, (6_000_000,))
    fin, fin_sha = str(ck / "os_50m_full" / "samples_006000000.pt"), os_sha[6_000_000]
    tag = "os_50m_full-samples_006000000"
    lad = root / "results" / "audit" / "ladder"
    eref = root / "results" / "audit" / "engine_reference"
    h40 = {f: min(i, 3) for i, f in enumerate(FAM)}               # of 4; instance 3 is accepted by both
    h80 = {f: i % 2 for i, f in enumerate(FAM)}                   # of 2; none accepted by the oracle
    allB = (1, 10, 100, 1000)
    # the main final: random and best-of-N on the 40 (with floors), random on the 80 (no floors); seeded on both
    write_run(lad / "os_50m_full" / "samples_006000000" / "tasks",
              recs_for(inst["c40"], starts40, "random", allB, h40, {3})
              + recs_for(inst["c40"], starts40, "best_of_n", allB, h40, {3}), tsha["c40"], fin_sha)
    write_run(lad / "os_50m_full" / "samples_006000000" / "tasksx",
              recs_for(inst["c80"], starts80, "random", allB, h80, set()), tsha["c80"], fin_sha, pool_stats=False)
    write_run(lad / "os_50m_full" / "samples_006000000" / "tasks_cem_seeded",
              recs_for(inst["c40"], starts40, "cem_seeded", (1, 10, 100, 1000), h40, {3}), tsha["c40"], fin_sha)
    write_run(lad / "os_50m_full" / "samples_006000000" / "tasksx_cem_seeded",
              recs_for(inst["c80"], starts80, "cem_seeded", (1, 10, 100, 1000), h80, set()), tsha["c80"], fin_sha,
              pool_stats=False)
    # the half: a run in progress (config only)
    _wjson(lad / "os_50m_full" / "samples_003000064" / "tasks" / "config.json", {"config": {"tasks_sha256": tsha["c40"]}})
    # the perfect emulator: never fooled; accepts instance 3 of the 40
    zero = {f: 0 for f in FAM}
    for s, starts, acc in (("c40", starts40, {3}), ("c80", starts80, set())):
        stem = tf[s].stem
        _wrecords(eref / stem / "B_economy" / "records.jsonl.gz",
                  recs_for(inst[s], starts, "random", allB, zero, acc) + recs_for(inst[s], starts, "best_of_n", allB, zero, acc))
        _wjson(eref / stem / "B_economy" / "config.json", {"config": {"tasks_sha256": tsha[s]}})
        _wrecords(eref / stem / "cem_seeded_B_economy" / "records.jsonl.gz",
                  recs_for(inst[s], starts, "cem_seeded", (10, 100, 1000), zero, acc))
        _wjson(eref / stem / "cem_seeded_B_economy" / "config.json", {"config": {"tasks_sha256": tsha[s]}})
    # the coverage model: never fooled, accepts instance 3; random and best-of-N only (seeded missing)
    cov_tag_dir = lad / "os_50m_cov" / "samples_006000000" / "tasks"
    write_run(cov_tag_dir, recs_for(inst["c40"], starts40, "random", allB, zero, {3})
              + recs_for(inst["c40"], starts40, "best_of_n", allB, zero, {3}), tsha["c40"], cov_sha[6_000_000])
    # RL on the main final: 3 seeds, except power seed 2 whose last evaluation is missing
    for fi, f in enumerate(FAM):
        for s in (0, 1, 2):
            d = root / "results" / "rl" / f"{tag}__{f}__s{s}__tasks"
            _wjson(d / "config.json", {"meta": {"environment": "emulator", "task": f, "rl_seed": s, "checkpoint": fin,
                                                "checkpoint_sha256": fin_sha, "variant": "frozen",
                                                "tasks_sha256": tsha["c40"], "instances": inst["c40"][f]}})
            for mo in al.SNAPSHOTS:
                if f == "power" and s == 2 and mo == al.SNAPSHOTS[-1]:
                    continue
                da, oa = 0.1 * s + 0.01 * fi, 0.05
                _wjson(d / f"eval3_{mo:09d}.summary.json",
                       {"eval_version": 3, "months": mo, "n_instances": 4, "rate_dream_accept": da,
                        "rate_engine_open_accept": oa, "verdict_gap_open": da - oa, "inflation_open": 0.2 + 0.1 * s,
                        "rate_engine_closed_accept": 0.3})
    # an RL run of another learner on the self-forced final: read, refused
    _wjson(root / "results" / "rl" / "sf_50m_full-samples_001500032__grow__s0__tasks" / "config.json",
           {"meta": {"environment": "emulator", "task": "grow", "rl_seed": 0,
                     "checkpoint": str(ck / "sf_50m_full" / "samples_001500032.pt"),
                     "checkpoint_sha256": sf_sha[1_500_032], "variant": "bc", "tasks_sha256": tsha["c40"],
                     "instances": inst["c40"]["grow"]}})
    # fidelity: the main final in the main tree; the coverage model only in its own checkout
    gc = {m: {"model": 0.1 * (i + 1), "floor": 0.5} for i, (_, m, _) in enumerate(al.FIDELITY_METRICS)}
    _wjson(root / "results" / "fidelity" / "ladder" / "os_50m_full" / "dev" / "os_50m_full_samples_006000000_dec-a.json",
           {"samples": 6_000_000, "checkpoint_sha256": fin_sha, "gap_closed": gc})
    _wjson(covtree / "results" / "fidelity" / "ladder" / "os_50m_cov" / "dev" / "os_50m_cov_samples_006000000_dec-a.json",
           {"samples": 6_000_000, "checkpoint_sha256": cov_sha[6_000_000], "gap_closed": gc})
    return {"root": root, "ckpt": ck, "tasks": tf, "eref": eref, "covtree": covtree, "h40": h40, "h80": h80, "tag": tag}


def test_reading_a_small_tree_end_to_end(tmp_path):
    t = build_tree(tmp_path)
    out = tmp_path / "out"
    r = al.main(["--root", str(t["root"]), "--ckpt-root", str(t["ckpt"]), "--tasks", str(t["tasks"]["c40"]),
                 "--tasks-x", str(t["tasks"]["c80"]), "--engine-reference", str(t["eref"]),
                 "--cov-fidelity-fallback", str(t["covtree"]), "--cov-rl-fallback", str(tmp_path / "nofleet"),
                 "--out", str(out), "--n-boot", "50", "--workers", "1"])
    g, res, rep, cov = r["gather"], r["results"], r["replication"], r["coverage"]
    assert [e["checkpoint"] for e in g["ladder"]] == ["os_50m_full-samples_003000064", "os_50m_full-samples_006000000",
                                                     "sf_50m_full-samples_000750080", "sf_50m_full-samples_001500032"]
    assert [e["lineage"] for e in g["ladder"]] == ["os_50m_full"] * 4
    assert [e["stage"] for e in g["ladder"]] == ["half", "final", "half", "final"]
    rows = {(x["checkpoint"], x["family"]): x for x in g["rows"]}
    assert len(rows) == 4 * len(FAM)
    for fi, f in enumerate(FAM):
        x = rows[(t["tag"], f)]
        a, b = t["h40"][f], t["h80"][f]
        assert x["random_c40_hack_1000"] == pytest.approx(a / 4)
        assert x["random_c40_judge_accept_1000"] == pytest.approx((a + 1) / 4)
        assert x["random_c40_false_rejection_1000"] == 0.0
        assert x["random_c40_perfect_hack_1000"] == 0.0 and x["random_c40_diff_1000"] == pytest.approx(a / 4)
        assert x["random_c80_hack_1000"] == pytest.approx(b / 2) and x["random_c80_diff_1000"] == pytest.approx(b / 2)
        # pooled: events over the instances of both files, the excess paired by instance against each reference
        assert x["random_c120_hack_1000"] == pytest.approx((a + b) / 6) and x["random_c120_n_1000"] == 6
        assert x["random_c120_diff_1000"] == pytest.approx((a + b) / 6)
        assert x["random_c120_oracle_accept_1000"] == pytest.approx(1 / 6)
        assert x["cem_seeded_c120_hack_1000"] == pytest.approx((a + b) / 6)
        assert x["behaviour_false_rejection"] == 0.2
        assert x["fid_dev_f1_1m"] == pytest.approx(0.1) and math.isnan(x["fid_test_f1_1m"])
        assert "fidelity_test:absent" in x["missing"]
        gaps = np.array([0.1 * s + 0.01 * fi - 0.05 for s in (0, 1, 2)])
        if f == "power":
            assert x["rl_n_seeds_1000000"] == 2 and "rl@1000000:2/3 seeds" in x["missing"]
            assert x["rl_gap_1000000"] == pytest.approx(gaps[:2].mean())
        else:
            assert x["rl_n_seeds_1000000"] == 3 and "rl@" not in x["missing"]
            assert x["rl_gap_1000000"] == pytest.approx(gaps.mean())
            assert x["rl_gap_sd_1000000"] == pytest.approx(gaps.std(ddof=1))
            assert x["rl_inflation_1000000"] == pytest.approx(0.3)
    half = rows[("os_50m_full-samples_003000064", "grow")]
    assert "audit_random_c40:incomplete" in half["missing"] and "audit_random_c80:absent" in half["missing"]
    assert math.isnan(half["random_c120_hack_1000"]) and "fidelity_test" not in half["missing"]
    assert rows[("sf_50m_full-samples_001500032", "grow")]["rl_n_seeds_1000000"] == 0
    assert any("config differs (variant bc)" in n for c in g["checkpoints"] for n in c["rl_notes"])
    # the main test: four families of one checkpoint with all three seeds, pooled variable; partial, no decision
    assert res["status"] == "partial" and res["n_pairs_primary"] == 4 and res["n_checkpoints_primary"] == 1
    assert primary(res)["decision"] is None
    assert res["split_sample"]["grow"]["n_checkpoints"] == 1 and "status" in res["split_sample"]["grow"]
    # replication of the main checkpoint: arms and differences on the 40, the 80 and pooled
    v = rep["methods"]["cem_seeded"][1000]
    assert v["c40"]["n"] == 20 and v["c80"]["n"] == 10 and v["c120"]["n"] == 30
    assert v["c40"]["difference"].value == pytest.approx(sum(t["h40"].values()) / 20)
    assert v["c120"]["difference"].value == pytest.approx((sum(t["h40"].values()) + sum(t["h80"].values())) / 30)
    assert v["c120"]["perfect_emulator"]["oracle_accept"].value == pytest.approx(5 / 30)
    assert v["c120"]["emulator"]["false_rejection"].value == 0.0
    st = rep["statement"]
    assert st["c40_point"] == pytest.approx(v["c40"]["difference"].value)
    assert st["c80_excludes_0"] == bool(st["c80_interval"][0] > 0 or st["c80_interval"][1] < 0)
    assert rep["methods"]["cem_seeded"][1]["c40"].get("difference") is None   # no reference at B = 1
    # coverage: coverage minus main on the 40, paired by instance; the seeded search and RL missing; fidelity read
    # from the coverage model's own checkout
    c = cov["methods"]["random"]["budgets"][1000]
    assert c["all"]["coverage_minus_main"]["n"] == 20
    assert c["all"]["coverage_minus_main"]["hackability"].value == pytest.approx(-sum(t["h40"].values()) / 20)
    assert c["all"]["coverage_minus_main"]["excess_over_perfect"].value == pytest.approx(-sum(t["h40"].values()) / 20)
    assert c["all"]["coverage_minus_main"]["oracle_accept"].value == 0.0
    assert c["treasury"]["coverage_minus_main"]["hackability"].value == pytest.approx(-0.5)
    assert cov["methods"]["best_of_n"]["budgets"][10]["all"]["coverage"]["emulator"]["hackability"].value == 0.0
    assert cov["methods"]["cem_seeded"]["status"]["coverage"] == "absent"
    assert cov["fidelity"]["coverage"]["dev"]["status"] == "ok" and str(t["covtree"]) in cov["fidelity"]["coverage"]["dev"]["file"]
    assert cov["status"] == "partial" and any("RL, coverage model" in m for m in cov["missing"])
    md = (out / "main_claim.md").read_text()
    assert md.startswith("# Across emulators") and "(PARTIAL)" in md and "no decision: partial inputs" in md
    assert "reported beside (no decision)" in md
    # the tree holds every input of the replication (the seeded reference has no B = 1, by design): complete
    assert rep["status"] == "complete" and not rep["missing"]
    assert rep["methods"]["cem_seeded"][1]["c40"]["perfect_status"] == al.NOT_RUN_AT_B
    assert "(COMPLETE)" in (out / "replication.md").read_text() and "(PARTIAL)" in (out / "coverage.md").read_text()
    js = json.loads((out / "main_claim.json").read_text())
    assert js["status"] == "partial" and js["results"]["n_pairs_primary"] == 4
    assert json.loads((out / "replication.json").read_text())["checkpoint"] == t["tag"]
    lines = (out / "pairs.csv").read_text().splitlines()
    assert len(lines) == 1 + 4 * len(FAM) and lines[0].split(",")[0] == "checkpoint"
    man = json.loads((out / "inputs_manifest.json").read_text())["files"]
    assert any(k.endswith("samples_006000000/tasksx/records.jsonl.gz") for k in man)
    for name in ("fig5_scatter.csv", "fig5_correlations.csv", "fig5_reliability.csv", "fig5_split_sample.csv"):
        assert (out / name).is_file()


# --------------------------------------------------------------------------------------------------------------
# held-out likelihood, fixed-candidate decision fidelity, the analysis plan's nested set


def _npz(path: Path, **arrays):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays)


def dec_tree(tmp: Path, starts=("s-a", "s-b", "s-c"), R: int = 120, seed: int = 0):
    """A city file; an engine-reference run storing the truth-seed pool mean (with its own search scores); one audit's
    pools.npz and random-search records whose emulator two-sample margins are known. The margins are rounded to
    0.25 (exact ties), and the stored residuals carry a recovery error of a few ulp, as real ones do. Instance 0 of
    ``grow`` has a constant engine margin, instance 1 a constant emulator margin."""
    rng = np.random.default_rng(seed)
    root = tmp / "repo"
    tf = root / "data" / "tasks.json"
    _wjson(tf, {"meta": {}, "instances": [{"family_id": st, "start_id": f"{st}-v0", "task": f, "horizon": "24"}
                                          for f in FAM for st in starts]})
    tasks = al.load_tasks(tf)
    keys = sorted(set().union(*tasks["instances"].values()))
    eref = root / "results" / "audit" / "engine_reference"
    run = root / "results" / "audit" / "ladder" / "r" / "samples_000000001" / "tasks"
    ref, aud, truth = {}, {}, {}
    for k in keys:
        st = k.replace("|", "__")
        m9, t64, s_ref = rng.normal(size=R), rng.normal(size=R), rng.normal(size=R)
        eng = rng.normal(size=R)
        emu = np.round((eng + 0.7 * rng.normal(size=R)) * 4) / 4          # ties at multiples of 0.25
        if k == f"{starts[0]}-v0|grow|H24":
            eng[:] = -1.0
        if k == f"{starts[1]}-v0|grow|H24":
            emu[:] = 0.5
        ref[st + al.DEC_RES] = np.stack([s_ref - m9, np.full(R, np.nan)], axis=1)
        ref[st + al.DEC_TRES] = np.stack([s_ref - t64, np.full(R, np.nan)], axis=1)
        ref[st + al.DEC_TMEAN] = t64
        ulp = rng.uniform(-4e-15, 4e-15, size=R)
        aud[st + al.DEC_RES] = np.stack([emu - m9 + ulp, np.full(R, np.nan)], axis=1)
        aud[st + al.DEC_ENG] = eng[:al.DEC_PLANS]
        aud[st + al.DEC_GP] = (emu[:al.DEC_PLANS] > np.median(emu[:al.DEC_PLANS])).astype(float)
        truth[k] = {"emu": emu, "eng": eng, "m9": m9}
    for name in ("A_instance_calibrated", "B_economy_calibrated"):
        _npz(eref / tasks["stem"] / name / "pools.npz", **ref)
        _wjson(eref / tasks["stem"] / name / "config.json", {"config": {"tasks_sha256": tasks["sha256"]}})
    _npz(run / "pools.npz", **aud)
    recs = []
    for k in keys:
        for B in (1, 10, 100, 1000):
            j = int(np.argmax(truth[k]["emu"][:min(B, R)]))
            recs.append({"instance": k, "method": "random", "budget": B, "attacker_seed": 0, "best_index": j,
                         "grader_score": float(truth[k]["emu"][j])})
    _wrecords(run / "records.jsonl.gz", recs)
    _wjson(run / "config.json", {"config": {"tasks_sha256": tasks["sha256"], "search_seeds": [0]}})
    return {"root": root, "tasks": tasks, "eref": eref, "run": run, "truth": truth, "keys": keys, "recs": recs}


def test_decision_fidelity_recovers_the_two_sample_margins(tmp_path):
    t = dec_tree(tmp_path)
    rd = al.Reader(t["root"])
    src = al.nine_seed_means(t["eref"], t["tasks"], rd)
    assert src["status"] == "ok" and src["source"].endswith("A_instance_calibrated")
    assert len(src["cross_checked_with"]) == 1 and src["max_abs_difference_between_sources"] == 0.0
    for k in t["keys"]:
        assert np.allclose(src["m9"][k], t["truth"][k]["m9"], rtol=0, atol=1e-12)
    d = al.decision_fidelity({"status": "ok", "dir": str(t["run"])}, t["tasks"], t["root"], rd, src)
    assert d["status"] == "ok"
    # expected: scipy's Spearman on the exact margins, the two constant instances left out, the mean of the rest
    want, naive_differs = [], 0
    for k in t["keys"]:
        emu, eng = t["truth"][k]["emu"][:al.DEC_PLANS], t["truth"][k]["eng"][:al.DEC_PLANS]
        if np.ptp(emu) == 0 or np.ptp(eng) == 0:
            continue
        want.append(sps.spearmanr(emu, eng).correlation)
        st = k.replace("|", "__")
        z = np.load(t["run"] / "pools.npz")
        rec = z[st + al.DEC_RES][:al.DEC_PLANS, 0] + src["m9"][k][:al.DEC_PLANS]
        naive_differs += al.spearman(rec, eng) != pytest.approx(want[-1], abs=1e-12)
    assert naive_differs > 0                       # the ulp of the recovery would break the exact ties
    assert d["value"] == pytest.approx(np.mean(want), abs=1e-12)
    assert d["n_instances"] == len(t["keys"]) and d["n_defined"] == len(t["keys"]) - 2 and d["n_left_out"] == 2
    assert d["left_out_constant"] == {"emulator": 1, "engine": 1, "both": 0}
    assert d["per_family"]["grow"]["n_left_out"] == 2 and d["per_family"]["power"]["n_left_out"] == 0
    assert d["ties"]["largest_gap_merged"] < 1e-13 and d["ties"]["smallest_gap_kept"] >= 0.25 - 1e-9
    assert d["recovery_check"]["n_records"] == 4 * len(t["keys"]) and d["recovery_check"]["max_abs_error"] < 1e-13
    # the second reading: the plans the stored pass share accepts are exactly the higher-margin half
    assert d["second_reading_check"]["mean_auc"] == pytest.approx(1.0)
    assert "_rho" in d and set(d["_rho"]) == set(t["keys"])
    # two city files pooled: the mean over the instances of both
    p = al.pool_decision([d, d])
    assert p["status"] == "ok" and p["value"] == pytest.approx(d["value"]) and p["n_left_out"] == 2
    q = al.pool_decision([d, {"status": "not computable: x", "cities": "tasksx"}])
    assert q["status"] == "tasksx: not computable: x" and "value" not in q


def test_decision_fidelity_refuses_what_it_cannot_recover(tmp_path):
    t = dec_tree(tmp_path)
    rd = al.Reader(t["root"])
    src = al.nine_seed_means(t["eref"], t["tasks"], rd)
    aud = {"status": "ok", "dir": str(t["run"])}
    # a record whose grader_score the recovered margin does not reproduce
    bad = [dict(r) for r in t["recs"]]
    bad[5]["grader_score"] += 1e-6
    _wrecords(t["run"] / "records.jsonl.gz", bad)
    d = al.decision_fidelity(aud, t["tasks"], t["root"], al.Reader(t["root"]), src)
    assert d["status"].startswith("recovery check failed on 1 of") and "value" not in d
    _wrecords(t["run"] / "records.jsonl.gz", t["recs"])
    # no run on the city file stores the truth-seed pool mean: not computable, and said why
    none = al.nine_seed_means(tmp_path / "nowhere", t["tasks"], rd)
    assert none["status"].startswith("no run under")
    d = al.decision_fidelity(aud, t["tasks"], t["root"], rd, none)
    assert d["status"].startswith("not computable: no run under") and "value" not in d
    # sources that disagree are refused
    z = dict(np.load(t["eref"] / t["tasks"]["stem"] / "B_economy_calibrated" / "pools.npz"))
    k0 = t["keys"][0].replace("|", "__") + al.DEC_TMEAN
    z[k0] = z[k0] + 1e-3
    _npz(t["eref"] / t["tasks"]["stem"] / "B_economy_calibrated" / "pools.npz", **z)
    assert al.nine_seed_means(t["eref"], t["tasks"], al.Reader(t["root"]))["status"].startswith("the runs storing")
    # an audit that is not complete is not read
    assert al.decision_fidelity({"status": "incomplete", "dir": str(t["run"])}, t["tasks"], t["root"], rd,
                                src)["status"] == "random-search audit incomplete"


def test_heldout_likelihood_reads_the_total_bound(tmp_path):
    rd = al.Reader(tmp_path)
    f = tmp_path / "t.json"
    _wjson(f, {"onestep": {"loglik_nats_per_transition": {"elbo": -2500.5, "kl": -3.0, "tile_gate": -200.0}}})
    assert al.read_heldout_loglik({"status": "ok", "file": str(f)}, rd) == (-2500.5, "ok")
    _wjson(f, {"onestep": {"loglik_nats_per_transition": {"kl": -3.0}}})
    v, st = al.read_heldout_loglik({"status": "ok", "file": str(f)}, rd)
    assert math.isnan(v) and "elbo" in st
    v, st = al.read_heldout_loglik({"status": "absent"}, rd)
    assert math.isnan(v) and st == "test selection absent"


def test_secondary_further_rows_use_the_same_statistics_and_mark_the_verdict_row():
    rng = np.random.default_rng(4)
    rows = []
    for c in range(12):
        z = rng.normal()
        for f in FAM:
            r = blank_row(f"ck{c:03d}", f, f"lin{c % 6}")
            r[al.HELDOUT_X] = -2600.0 + 50 * z
            r[al.DEC_X["c40"]] = 0.65 + 0.03 * z
            for s in al.ALL_SETS:
                r[f"random_{s}_hack_1000"] = float(0.1 + 0.05 * z + 0.05 * rng.normal())
            rows.append(r)
    res = al.analyse(rows, n_boot=NB, seed=0)
    sec = res["secondary"]
    assert res["secondary_decision_fidelity_verdict_row"] == al.DEC_VERDICT_ROW == "fid_decision_c40|c80"
    assert [k for k, b in sec.items() if b.get("verdict_row")] == ["fid_decision_c40|c80"]
    for key, xk, yk in (("fid_test_loglik_elbo|c120", al.HELDOUT_X, "random_c120_hack_1000"),
                        ("fid_decision_c40|c80", al.DEC_X["c40"], "random_c80_hack_1000"),
                        ("fid_decision_c40|c40", al.DEC_X["c40"], "random_c40_hack_1000")):
        b, ref = sec[key], al._block(xk, yk, NB, 0, rows)
        assert b["n_pairs"] == 60 and b["n_checkpoints"] == 12
        assert b["pooled_spearman"].value == ref["pooled_spearman"].value and b["pooled_spearman"].lo == ref["pooled_spearman"].lo
        e = b["pooled_spearman"]
        assert b["abs_below_0.3"] == (abs(e.value) < 0.3)
        assert b["interval_abs_above_0.3"] == (e.lo > 0.3 or e.hi < -0.3)
    # no pair holds the measure on the 80 cities: no estimate
    assert "pooled_spearman" not in sec["fid_decision_c80|c40"] and sec["fid_decision_c80|c40"]["n_pairs"] == 0
    assert sec["fid_decision_c80|c40"]["x_cities"] == "c80" and sec["fid_decision_c80|c40"]["y_cities"] == "c40"
    # the rows that existed before are untouched by the new ones
    assert all(k in sec for k in (f"{x}|{s}" for x in al.FID_X for s in al.ALL_SETS))


def nested_g(tmp: Path, done: set, bad_excess=(), bad_ref=()):
    """A ladder of 24 (12 runs x half and final) with the seeded search done on ``done``."""
    root = tmp / "repo"
    ladder, cks, rows, audits = [], [], [], {}
    rng = np.random.default_rng(2)
    for o in ("os", "sf"):
        for sz in (15, 50, 100):
            for dsc in ("full", "small"):
                run = f"{o}_{sz}m_{dsc}"
                for stage in ("half", "final"):
                    ck = f"{run}-{stage}"
                    ladder.append({"checkpoint": ck, "run": run, "stage": stage})
                    d = f"results/audit/ladder/{run}/{stage}/tasks_v2_H24_cem_seeded"
                    ok = ck in done or ck in bad_excess or ck in bad_ref
                    if ok:
                        (root / d).mkdir(parents=True, exist_ok=True)
                        (root / d / "reference.json").write_text("{}")
                    audits[ck] = {("cem_seeded", "c40"): {"status": "ok" if ok else "absent", "dir": d}}
                    chk = {"cem_seeded_c40": {"agree": 15, "differ": ["x"] if ck in bad_ref else []}} if ok else {}
                    cks.append({"checkpoint": ck, "reference_json_check": chk})
                    z = rng.normal()
                    for f in FAM:
                        r = blank_row(ck, f, run)
                        r[al.SEEDED_X] = float(0.1 + 0.05 * z + 0.02 * rng.normal()) if ok else NAN
                        r["random_c120_hack_1000"] = r["random_c40_hack_1000"] = float(0.1 + 0.05 * z)
                        r["rl_inflation_1000000"] = r["rl_gap_1000000"] = float(z + 0.3 * rng.normal())
                        r["missing"] = "excess_cem_seeded_c40@1000:0/40 paired" if ck in bad_excess else ""
                        rows.append(r)
    return {"ladder": ladder, "checkpoints": cks, "rows": rows, "audits": audits, "reader": al.Reader(root)}


def test_nested_set_takes_the_largest_complete_set(tmp_path):
    lad = nested_g(tmp_path / "x", set())["ladder"]
    full = {e["checkpoint"] for e in lad if e["stage"] == "final" and "_full" in e["run"]}
    finals = {e["checkpoint"] for e in lad if e["stage"] == "final"}
    allc = {e["checkpoint"] for e in lad}
    assert len(full) == 6 and len(finals) == 12 and len(allc) == 24
    some = set(sorted(full)[:3])
    for i, (done, kw, want) in enumerate([
            (some, {}, None),
            (full, {}, "full_finals"),
            (full - {sorted(full)[0]}, {"bad_ref": {sorted(full)[0]}}, None),       # reference.json disagrees
            (finals - {sorted(finals - full)[0]}, {"bad_excess": {sorted(finals - full)[0]}}, "full_finals"),
            (finals, {}, "finals"),
            (allc, {}, "all")]):
        g = nested_g(tmp_path / f"t{i}", done, **kw)
        ns = al.seeded_nested_set(g, g["rows"], NB, 0, 1)
        assert ns["largest_complete_set"] == want, (i, ns["status"])
        assert [ns["sets"][k]["n_done"] for k in ns["order"]] == [len(done), len(done & finals), len(done & full)]
        if want is None:
            assert ns["status"] == "no set is complete" and ns["rows"] == {} and ns["largest_complete_set_name"] is None
            continue
        keep = set(ns["sets"][want]["checkpoints"])
        assert ns["largest_complete_set_name"] == dict((k, n) for k, n, _ in al.NESTED_SETS)[want]
        sel = [r for r in g["rows"] if r["checkpoint"] in keep]
        for y in ("rl_inflation_1000000", "rl_gap_1000000"):
            b, ref = ns["rows"][f"{al.SEEDED_X}|{y}"], al._block(al.SEEDED_X, y, NB, 0, sel)
            assert b["n_checkpoints"] == len(keep) and b["n_pairs"] == b["n_pairs_expected"] == 5 * len(keep)
            assert b["pooled_spearman"].value == ref["pooled_spearman"].value
            assert b["within_mean_spearman"].value == ref["within_mean_spearman"].value
            assert "per_family" in b and ns["rows"][f"random_c120_hack_1000|{y}"]["n_checkpoints"] == len(keep)
    g = nested_g(tmp_path / "why", set(), bad_excess={sorted(full)[0]}, bad_ref={sorted(full)[1]})
    why = al.seeded_done(g)
    assert any("incomplete: excess_cem_seeded_c40@1000" in w for w in why[sorted(full)[0]]["why_not"])
    assert any("reference.json disagrees" in w for w in why[sorted(full)[1]]["why_not"])
    assert why[sorted(full)[2]]["why_not"] == ["no reference.json", "audit absent"]


def test_the_small_tree_with_stored_margins_end_to_end(tmp_path):
    """The tree of the end-to-end test, with the 40 cities' truth-seed pool mean in the engine reference and the
    main final's pools.npz: the further measures and the nested-set block reach the outputs."""
    t = build_tree(tmp_path)
    tasks = al.load_tasks(t["tasks"]["c40"])
    keys = sorted(set().union(*tasks["instances"].values()))
    rng = np.random.default_rng(3)
    R = al.DEC_PLANS
    run = t["root"] / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000" / "tasks"
    ref, aud, emu = {}, {}, {}
    for k in keys:
        st = k.replace("|", "__")
        m9, t64, s_ref, eng = (rng.normal(size=R) for _ in range(4))
        emu[k] = eng + 0.5 * rng.normal(size=R)
        ref[st + al.DEC_RES] = np.stack([s_ref - m9, s_ref], axis=1)
        ref[st + al.DEC_TRES] = np.stack([s_ref - t64, s_ref], axis=1)
        ref[st + al.DEC_TMEAN] = t64
        aud[st + al.DEC_RES] = np.stack([emu[k] - m9, emu[k]], axis=1)
        aud[st + al.DEC_ENG] = eng
    _npz(t["eref"] / tasks["stem"] / "B_economy_calibrated" / "pools.npz", **ref)
    _wjson(t["eref"] / tasks["stem"] / "B_economy_calibrated" / "config.json", {"config": {"tasks_sha256": tasks["sha256"]}})
    _npz(run / "pools.npz", **aud)
    recs = [json.loads(x) for x in gzip.open(run / "records.jsonl.gz", "rt")]
    for r in recs:
        if r["method"] == "random":
            j = int(np.argmax(emu[r["instance"]][:min(r["budget"], R)]))
            r["best_index"], r["grader_score"] = j, float(emu[r["instance"]][j])
    _wrecords(run / "records.jsonl.gz", recs)
    fit = t["root"] / "results" / "fidelity" / "ladder" / "os_50m_full" / "test" / "os_50m_full_samples_006000000_dec-a.json"
    gc = {m: {"model": 0.2, "floor": 0.5} for _, m, _ in al.FIDELITY_METRICS}
    fin_sha = json.loads((run / "card.json").read_text())["meta"]["judge"]["ckpt_sha256"]
    _wjson(fit, {"samples": 6_000_000, "checkpoint_sha256": fin_sha, "gap_closed": gc,
                 "onestep": {"loglik_nats_per_transition": {"elbo": -2610.25}}})
    out = tmp_path / "out"
    r = al.main(["--root", str(t["root"]), "--ckpt-root", str(t["ckpt"]), "--tasks", str(t["tasks"]["c40"]),
                 "--tasks-x", str(t["tasks"]["c80"]), "--engine-reference", str(t["eref"]),
                 "--cov-fidelity-fallback", str(t["covtree"]), "--cov-rl-fallback", str(tmp_path / "nofleet"),
                 "--out", str(out), "--n-boot", "50", "--workers", "1"])
    g, res = r["gather"], r["results"]
    want = np.mean([sps.spearmanr(emu[k], aud[k.replace("|", "__") + al.DEC_ENG]).correlation for k in keys])
    rows = {(x["checkpoint"], x["family"]): x for x in g["rows"]}
    for f in FAM:
        x = rows[(t["tag"], f)]
        assert x[al.HELDOUT_X] == -2610.25 and x[al.DEC_X["c40"]] == pytest.approx(want, abs=1e-12)
        assert x[f"{al.DEC_X['c40']}_n_defined"] == len(keys) and math.isnan(x[al.DEC_X["c80"]])
        assert math.isnan(rows[("os_50m_full-samples_003000064", f)][al.DEC_X["c40"]])     # finals only
    ck = {c["checkpoint"]: c for c in g["checkpoints"]}
    assert ck[t["tag"]]["decision_fidelity"]["c80"]["status"].startswith("not computable: no run under")
    assert ck["sf_50m_full-samples_001500032"]["decision_fidelity"]["c40"]["status"] == "random-search audit absent"
    assert ck["os_50m_full-samples_003000064"]["heldout_loglik"].startswith("not entered")
    assert "not_computed" in res["secondary"]["fid_decision_c80|c40"]
    ns = res["seeded_nested_set"]
    assert ns["status"] == "no set is complete" and [ns["sets"][k]["n_checkpoints"] for k in ns["order"]] == [4, 2, 2]
    js = json.loads((out / "main_claim.json").read_text())
    assert js["results"]["seeded_nested_set"]["largest_complete_set"] is None
    assert js["results"]["secondary_decision_fidelity_verdict_row"] == "fid_decision_c40|c80"
    assert "fid_decision_c40" in (out / "pairs.csv").read_text().splitlines()[0].split(",")
    md = (out / "main_claim.md").read_text()
    assert "**verdict**" in md and "the analysis plan's nested set" in md and "no set is complete" in md
