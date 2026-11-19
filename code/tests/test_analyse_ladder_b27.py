"""Tests for the additions to ``code/scripts/analyse_ladder.py``: the analysis plan's exploratory comparator (E1, E2,
the budget-1 columns of ``pairs.csv``, no wording while the inputs are partial), the coverage model's fixed-candidate
decision fidelity paired by instance , and the analysis plan's replication statement (80-minus-40
difference from independent bootstraps). The small trees are those of ``test_analyse_ladder.py``. CPU only; seconds."""

from __future__ import annotations

import gzip
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats as sps
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "code" / "tests", ROOT / "code" / "scripts", ROOT / "code", ROOT / "hpr-dream"):
    sys.path.insert(0, str(p))

import analyse_ladder as al  # noqa: E402
import hpr_dream.stats as hs  # noqa: E402
from test_analyse_ladder import _npz, _wjson, _wrecords, blank_row, build_tree  # noqa: E402

FAM = al.FAMILIES
NB = 200
NAN = float("nan")


@pytest.fixture(autouse=True)
def few_simulations(monkeypatch):
    """The power simulations at test size (the analysis reads these at call time)."""
    monkeypatch.setattr(al, "D79_SIM", 40)
    monkeypatch.setattr(al, "D79_SIM_BOOT", 100)


def run_main(t, tmp_path):
    out = tmp_path / "out"
    r = al.main(["--root", str(t["root"]), "--ckpt-root", str(t["ckpt"]), "--tasks", str(t["tasks"]["c40"]),
                 "--tasks-x", str(t["tasks"]["c80"]), "--engine-reference", str(t["eref"]),
                 "--cov-fidelity-fallback", str(t["covtree"]), "--cov-rl-fallback", str(tmp_path / "nofleet"),
                 "--out", str(out), "--n-boot", "50", "--workers", "1"])
    return r, out


def e_rows(n_ckpt: int, x1_of, seed: int = 0) -> list[dict]:
    """Pairs with random search's false acceptance at 1,000 and at budget 1 on all three city sets; ``x1_of(rng, z,
    x1000)`` gives the budget-1 value."""
    rng = np.random.default_rng(seed)
    rows = []
    for c in range(n_ckpt):
        for f in FAM:
            z = rng.normal()
            r = blank_row(f"ck{c:03d}", f, f"lin{c % 6}")
            x = float(ndtr(z + 0.3 * rng.normal()))
            x1 = float(x1_of(rng, z, x))
            for s in al.ALL_SETS:
                r[al.E_SEARCH_X[s]], r[al.E_X[s]] = x, x1
            r["rl_inflation_1000000"] = r["rl_gap_1000000"] = z + 0.3 * rng.normal()
            r["rl_gap_sd_1000000"] = r["rl_inflation_sd_1000000"] = 0.01
            rows.append(r)
    return rows


# --------------------------------------------------------------------------------------------------------------


def test_e2_is_the_paired_difference_and_reads_decision_77s_wording_only_when_complete():
    rows = e_rows(24, lambda rng, z, x: rng.uniform())         # one logged plan carries no signal
    res = al.analyse(rows, n_boot=NB, seed=0)
    assert res["status"] == "complete"
    ex = res["exploratory_logged_plan"]
    row = ex["rows"][f"{al.POOLED}|{al.PRIMARY_Y}"]
    e1, e2 = row["E1"], row["E2"]
    xs = np.array([r[al.E_SEARCH_X["c120"]] for r in rows])
    x1 = np.array([r[al.E_X["c120"]] for r in rows])
    y = np.array([r[al.PRIMARY_Y] for r in rows])
    # E1 is the main claim's block with x at budget 1; E2's pooled value is the difference of the two Spearmans
    assert e1["pooled_spearman"].value == pytest.approx(sps.spearmanr(x1, y).statistic)
    assert e2["pooled_spearman_search"].value == pytest.approx(res["main"]["c120"][al.PRIMARY_Y]["pooled_spearman"].value)
    assert e2["pooled_spearman_difference"].value == pytest.approx(sps.spearmanr(xs, y).statistic
                                                                   - sps.spearmanr(x1, y).statistic)
    assert e2["n_pairs"] == 120 and e2["pooled_spearman_difference"].n_clusters == 24
    assert e2["pooled_spearman_difference_lineage"].n_clusters == 6
    # joint resampling: the difference's replicates are the replicates' differences (same draws as cluster_boot)
    ck = np.array([r["checkpoint"] for r in rows])
    a = al.cluster_boot(lambda ix: al.spearman(xs[ix], y[ix]), ck, NB, 0)
    assert e2["pooled_spearman_search"].lo == pytest.approx(a.lo)
    assert e2["pooled_spearman_difference"].lo > 0
    assert row["wording_status"] == "made" and row["reading"]["pooled_spearman_difference"] == "above"
    assert row["wording"]["pooled_spearman_difference"] == al.E_WORDING["above"]
    assert all(per["n"] == 24 for per in e2["per_family"].values())
    # the 40- and 80-city rows are reported beside, with no wording
    for s in al.SETS:
        r = ex["rows"][f"{s}|{al.PRIMARY_Y}"]
        assert r["role"] == "reported beside it" and "wording" not in r and "wording_status" not in r
    # identical predictors: the difference is zero on every resample and its interval includes zero
    same = e_rows(24, lambda rng, z, x: x, seed=1)
    r2 = al.analyse(same, n_boot=NB, seed=0)["exploratory_logged_plan"]["rows"][f"{al.POOLED}|{al.PRIMARY_Y}"]
    d = r2["E2"]["pooled_spearman_difference"]
    assert d.value == 0 and d.lo == 0 and d.hi == 0
    assert r2["reading"]["pooled_spearman_difference"] == "includes"
    assert r2["wording"]["within_mean_spearman_difference"] == al.E_WORDING["includes"]
    # partial inputs (fewer checkpoints than the ladder): values, no wording
    part = al.analyse(e_rows(10, lambda rng, z, x: rng.uniform()), n_boot=NB, seed=0)
    rp = part["exploratory_logged_plan"]["rows"][f"{al.POOLED}|{al.PRIMARY_Y}"]
    assert part["status"] == "partial" and rp["wording_status"] == "not made: partial inputs"
    assert rp["wording"] is None and rp["reading"] is None and "pooled_spearman_difference" in rp["E2"]
    assert al.e2_reading(hs.Estimate(-0.2, -0.3, -0.1, 10, 5, 10, 0)) == "below"
    assert al.e2_reading(hs.Estimate(0.1, NAN, NAN, 10, 5, 10, 0)) is None


def test_budget_one_columns_and_rows_on_the_small_tree(tmp_path):
    t = build_tree(tmp_path)
    r, out = run_main(t, tmp_path)
    g, res = r["gather"], r["results"]
    rows = {(x["checkpoint"], x["family"]): x for x in g["rows"]}
    for fi, f in enumerate(FAM):
        x = rows[(t["tag"], f)]
        # the tree's random search: the judge accepts instance j < h[f] (oracle rejects) at every budget
        assert x["random_c40_hack_1"] == pytest.approx(t["h40"][f] / 4)
        assert x["random_c80_hack_1"] == pytest.approx(t["h80"][f] / 2)
        assert x["random_c120_hack_1"] == pytest.approx((t["h40"][f] + t["h80"][f]) / 6)
        assert x["random_c120_n_1"] == 6 and x["random_c40_perfect_hack_1"] == 0.0
        assert x["random_c40_diff_1"] == pytest.approx(t["h40"][f] / 4)
        assert x["missing_budget_1"] == ""
        assert not any(m.split(":")[0].endswith("@1") for m in x["missing"].split(";"))   # the old column as it was
        sf = rows[("sf_50m_full-samples_001500032", f)]
        assert math.isnan(sf["random_c40_hack_1"]) and sf["missing_budget_1"].startswith("audit_random_c40:absent")
    header = (out / "pairs.csv").read_text().splitlines()[0].split(",")
    # the new columns come after every earlier one
    assert header.index("random_c120_hack_1") > header.index("fid_decision_c80_n_left_out")
    assert header[-1] == "missing_budget_1"
    ex = res["exploratory_logged_plan"]
    assert ex["status"] == "partial" and set(ex["rows"]) == {f"{s}|{y}" for s in al.ALL_SETS for y, _ in al.Y_VARS}
    assert ex["rows"][f"c120|{al.PRIMARY_Y}"]["wording"] is None
    js = json.loads((out / "main_claim.json").read_text())
    assert js["results"]["exploratory_logged_plan"]["wording_fixed_in_advance"] == al.E_WORDING
    assert js["definitions"]["exploratory_logged_plan"]["decision"] == 77
    md = (out / "main_claim.md").read_text()
    assert "the analysis plan" in md and "no wording: partial inputs" in md
    assert md.index("## 7. What is missing") > md.index("## Single-plan comparator")


def test_replication_d79_difference_from_independent_bootstraps(tmp_path):
    t = build_tree(tmp_path)
    r, out = run_main(t, tmp_path)
    rep = r["replication"]
    sd = rep["statement_d79"]
    assert set(sd) == set(al.METHODS)
    for m in al.METHODS:
        v = sd[m]
        assert v["status"] == "ok"
        # the perfect emulator is never fooled in the tree: the excess is the false acceptance
        h40 = np.mean([t["h40"][f] / 4 for f in FAM])
        h80 = np.mean([t["h80"][f] / 2 for f in FAM])
        assert v["excess_c40"].value == pytest.approx(h40) and v["excess_c80"].value == pytest.approx(h80)
        assert v["excess_c80"].value == pytest.approx(rep["methods"][m][1000]["c80"]["difference"].value)
        d = v["difference_c80_minus_c40"]
        assert d["value"] == pytest.approx(h80 - h40) and d["lo"] <= d["value"] <= d["hi"]
        assert v["difference_interval_includes_0"] == bool(d["lo"] <= 0 <= d["hi"])
        lo, hi = v["excess_c80_interval"]
        assert v["c80_excess_interval_excludes_0"] == bool(lo > 0 or hi < 0)
        assert v["reading"]["c80"] in ("replicates", "does not replicate")
    # the replicates are independent: the 80 drawn with seed + 1, the 40 with seed
    u40 = al.units_all_families(g_aud(r, t, "random", "c40"), 1000)
    u80 = al.units_all_families(g_aud(r, t, "random", "c80"), 1000)
    _, b40 = al._excess_draws(u40, 50, 0)
    _, b80 = al._excess_draws(u80, 50, 1)
    q = np.quantile(b80 - b40, [0.025, 0.975])
    assert sd["random"]["difference_c80_minus_c40"]["lo"] == pytest.approx(q[0])
    assert "The analysis plan's replication statement" in (out / "replication.md").read_text()
    js = json.loads((out / "replication.json").read_text())
    assert js["statement_d79"]["cem_seeded"]["status"] == "ok"


def g_aud(r, t, m, s):
    return r["gather"]["audits"][t["tag"]][(m, s)]


def test_coverage_decision_fidelity_is_decision_74s_measure_paired_by_instance(tmp_path):
    t = build_tree(tmp_path)
    tasks = al.load_tasks(t["tasks"]["c40"])
    keys = sorted(set().union(*tasks["instances"].values()))
    rng = np.random.default_rng(5)
    R = al.DEC_PLANS
    lad = t["root"] / "results" / "audit" / "ladder"
    runs = {"main": lad / "os_50m_full" / "samples_006000000" / "tasks",
            "coverage": lad / "os_50m_cov" / "samples_006000000" / "tasks"}
    ref, emu, eng, pools = {}, {"main": {}, "coverage": {}}, {}, {"main": {}, "coverage": {}}
    for k in keys:
        st = k.replace("|", "__")
        m9, t64, s_ref = (rng.normal(size=R) for _ in range(3))
        eng[k] = rng.normal(size=R)
        ref[st + al.DEC_RES] = np.stack([s_ref - m9, s_ref], axis=1)
        ref[st + al.DEC_TRES] = np.stack([s_ref - t64, s_ref], axis=1)
        ref[st + al.DEC_TMEAN] = t64
        for who, noise in (("main", 0.5), ("coverage", 1.5)):
            emu[who][k] = eng[k] + noise * rng.normal(size=R)
            pools[who][st + al.DEC_RES] = np.stack([emu[who][k] - m9, emu[who][k]], axis=1)
            pools[who][st + al.DEC_ENG] = eng[k]
    _npz(t["eref"] / tasks["stem"] / "B_economy_calibrated" / "pools.npz", **ref)
    _wjson(t["eref"] / tasks["stem"] / "B_economy_calibrated" / "config.json", {"config": {"tasks_sha256": tasks["sha256"]}})
    for who, run in runs.items():
        _npz(run / "pools.npz", **pools[who])
        recs = [json.loads(x) for x in gzip.open(run / "records.jsonl.gz", "rt")]
        for x in recs:
            if x["method"] == "random":
                j = int(np.argmax(emu[who][x["instance"]][:min(x["budget"], R)]))
                x["best_index"], x["grader_score"] = j, float(emu[who][x["instance"]][j])
        _wrecords(run / "records.jsonl.gz", recs)
    r, out = run_main(t, tmp_path)
    d = r["coverage"]["decision_fidelity"]
    assert d["status"] == "ok" and d["n_defined_both"] == len(keys)
    rho = {who: {k: sps.spearmanr(emu[who][k], eng[k]).correlation for k in keys} for who in runs}
    assert d["main"]["value"] == pytest.approx(np.mean(list(rho["main"].values())), abs=1e-12)
    assert d["coverage"]["value"] == pytest.approx(np.mean(list(rho["coverage"].values())), abs=1e-12)
    p = d["paired"]["all"]
    assert p["coverage_minus_main"].value == pytest.approx(np.mean([rho["coverage"][k] - rho["main"][k] for k in keys]))
    assert p["n_clusters"] == 4 and p["coverage_minus_main"].value < 0
    assert p["n_instances_coverage_higher"] + p["n_instances_main_higher"] == len(keys)
    assert all(d["paired"][f]["n_instances"] == 4 for f in FAM)
    # the main checkpoint's value is the one the ladder rows carry
    assert d["main_equals_the_ladder_value"] is True
    # every field the coverage report had before is unchanged in kind: its status does not depend on this block
    assert r["coverage"]["status"] == "partial" and not any("decision" in m for m in r["coverage"]["missing"])
    assert "Fixed-candidate decision fidelity, 40 cities" in (out / "coverage.md").read_text()
    js = json.loads((out / "coverage.json").read_text())
    assert js["decision_fidelity"]["paired"]["all"]["n_instances"] == len(keys)


# --------------------------------------------------------------------------------------------------------------
# the analysis plan


def fam_rows(n_ckpt: int, within: float, seed: int = 0) -> list[dict]:
    """x and y share a family offset; inside a family y follows x with weight ``within``."""
    rng = np.random.default_rng(seed)
    rows = []
    for c in range(n_ckpt):
        for fi, f in enumerate(FAM):
            z = rng.normal()
            r = blank_row(f"ck{c:03d}", f, f"lin{c % 6}")
            for s in al.ALL_SETS:
                r[f"random_{s}_hack_1000"] = float(ndtr(fi - 2 + 0.3 * z))
            r["rl_inflation_1000000"] = r["rl_gap_1000000"] = 3.0 * fi + within * z + rng.normal()
            r["rl_gap_sd_1000000"] = r["rl_inflation_sd_1000000"] = 0.01
            rows.append(r)
    return rows


def test_permutation_null_keeps_the_family_structure():
    rows = fam_rows(24, within=0.0)
    x = np.array([r["random_c120_hack_1000"] for r in rows])
    y = np.array([r["rl_inflation_1000000"] for r in rows])
    fam = np.array([r["family"] for r in rows])
    p = al.perm_null(x, y, fam, n_perm=500, seed=0)
    # families alone carry a high pooled value, and the null reproduces it
    assert p["status"] == "ok" and p["observed"] == pytest.approx(sps.spearmanr(x, y).statistic)
    assert p["null_median"] > 0.7 and p["null_p2_5"] < p["observed"] < p["null_p97_5"]
    assert not p["observed_above_null_p97_5"]
    rows2 = fam_rows(24, within=3.0)
    y2 = np.array([r["rl_inflation_1000000"] for r in rows2])
    x2 = np.array([r["random_c120_hack_1000"] for r in rows2])
    p2 = al.perm_null(x2, y2, fam, n_perm=500, seed=0)
    assert p2["observed_above_null_p97_5"] and p2["share_of_null_at_or_above_observed"] < 0.025
    # the permutation stays inside each family: y's within-family multiset is unchanged, so the null of a statistic of
    # family means only is a point
    fm = np.array([y[fam == f].mean() for f in FAM])
    assert np.ptp(fm) > 0


def test_main_d79_rows_wording_only_when_complete_and_power_by_simulation():
    rows = fam_rows(24, within=3.0)
    res = al.analyse(rows, n_boot=NB, seed=0)
    d = al.main_d79(rows, res, NB, 0, 1)
    row = d["rows"][f"c120|{al.PRIMARY_Y}"]
    assert d["status"] == "complete" and row["wording_status"] == "made"
    assert row["wording"]["permutation_null"] == al.D79_MAIN_WORDING["null_above"]
    assert row["wording"]["within_family"] == al.D79_MAIN_WORDING["within_excludes"]
    assert row["within_family"]["estimate"].value == res["main"]["c120"][al.PRIMARY_Y]["within_mean_spearman"].value
    sv = row["sensitivity"]
    assert sv["clustered_by_task_family"].n_clusters == 5
    assert sv["pearson_checkpoint_clusters"].value == pytest.approx(sps.pearsonr(
        [r["random_c120_hack_1000"] for r in rows], [r[al.PRIMARY_Y] for r in rows]).statistic)
    assert len(sv["leave_one_lineage_out"]) == 6 and all(v["n_pairs"] == 100 for v in sv["leave_one_lineage_out"].values())
    assert d["rows"][f"c80|{al.PRIMARY_Y}"]["role"].startswith("the check on audit data unseen")
    assert "wording" not in d["rows"][f"c40|{al.PRIMARY_Y}"]
    assert set(d["power_cells"]) == {f"24|5|{rho}" for rho in al.D79_RHOS}
    part = fam_rows(10, within=3.0)
    rp = al.main_d79(part, al.analyse(part, n_boot=NB, seed=0), NB, 0, 1)["rows"][f"c120|{al.PRIMARY_Y}"]
    assert rp["wording_status"] == "not made: partial inputs" and rp["wording"] is None
    assert "permutation_null" in rp and "sensitivity" in rp


def test_simulated_powers_behave():
    lo = al.sim_within_power(24, 5, 0.0, n_sim=150, n_boot=200)
    hi = al.sim_within_power(24, 5, 0.7, n_sim=60, n_boot=200)
    assert lo["power_interval_excludes_0"] < 0.15 and hi["power_interval_excludes_0"] > 0.9
    flat = {"grand_mean": 0.2, "family_effects": [0.0] * 5, "sd_checkpoint": 0.05, "sd_residual": 0.0}
    a = al.sim_falsify_power(flat, 24, 5, rho=0.95, n_sim=60, n_boot=200)
    assert a["power_checkpoint_level"] > 0.9 and a["power_pooled"] > 0.9   # no dilution without family effects
    fam = {"grand_mean": 0.2, "family_effects": [-0.3, -0.15, 0.0, 0.15, 0.3], "sd_checkpoint": 0.02,
           "sd_residual": 0.02}
    b = al.sim_falsify_power(fam, 24, 5, rho=0.95, n_sim=60, n_boot=200)
    assert b["power_checkpoint_level"] > 0.9 and b["power_pooled"] < 0.1       # the pooled row is diluted
    Y = np.add.outer(np.arange(4.0), np.array([0.0, 1, 2, 3, 4])) + 0.0
    dec = al._decompose(Y)
    assert dec["sd_residual"] == pytest.approx(0) and dec["family_effects"] == pytest.approx([-2, -1, 0, 1, 2])


def test_secondary_d79_on_the_small_tree_reads_the_finals_then_all_with_test_half(tmp_path):
    t = build_tree(tmp_path)
    r, out = run_main(t, tmp_path)
    d = r["results"]["secondary_d79"]
    assert d["n_checkpoints_in_set"] == 2 and d["departure"] and d["status"] == "partial" and d["wording"] is None
    assert r["results"]["status"] == "partial"        # no wording while the main claim's inputs are partial
    assert [m["measure"] for m in d["measures"]] == [n for n, _ in al.D78_MEASURES]
    assert set(d["checkpoint_level_beside_existing"]) == set(r["results"]["secondary"])
    # test-selection files for both half-trained checkpoints: the claim is read on all four
    gc = {m: {"model": 0.3, "floor": 0.5} for _, m, _ in al.FIDELITY_METRICS}
    for run, n in (("os_50m_full", 3_000_064), ("sf_50m_full", 750_080)):
        _wjson(t["root"] / "results" / "fidelity" / "ladder" / run / "test_half" / f"{run}_samples_{n:09d}_dec-a.json",
               {"samples": n, "gap_closed": gc, "onestep": {"loglik_nats_per_transition": {"elbo": -2700.0}}})
    r2, out2 = run_main(t, tmp_path)
    d2 = r2["results"]["secondary_d79"]
    assert d2["n_checkpoints_in_set"] == 4 and d2["departure"] is None and d2["n_half_with_test_half"] == 2
    assert d2["checkpoint_set"].startswith("all 4 checkpoints")
    js = json.loads((out2 / "main_claim.json").read_text())
    assert js["results"]["secondary_d79"]["checkpoint_set"].startswith("all 4")
    assert js["definitions"]["decision_79"]["measures"]["held-out likelihood"] == [f"{al.HELDOUT_X}|c120"]
    md = (out2 / "main_claim.md").read_text()
    assert "The analysis plan" in md and "The analysis plan" in md


def test_checkpoint_level_row_is_one_point_per_checkpoint():
    rows = []
    for c in range(8):
        for fi, f in enumerate(FAM):
            r = blank_row(f"ck{c}", f, "l")
            r["fid_test_f1_1m"] = float(c)
            r["random_c120_hack_1000"] = 0.1 * c + 0.01 * fi
            rows.append(r)
    cl = al._ckpt_level(rows, "fid_test_f1_1m", "random_c120_hack_1000", NB, 0)
    assert cl["status"] == "ok" and cl["n_checkpoints"] == 8 and cl["spearman"].value == pytest.approx(1.0)
    rows[3]["fid_test_f1_1m"] = 99.0          # x must be constant across a checkpoint's families
    assert al._ckpt_level(rows, "fid_test_f1_1m", "random_c120_hack_1000", NB, 0)["status"].startswith("x differs")


def test_secondary_d79_applies_decision_78s_rule_when_complete(tmp_path):
    rng = np.random.default_rng(11)
    rows, ladder = [], []
    for c in range(24):
        ck = f"ck{c:03d}"
        ladder.append({"checkpoint": ck, "run": f"r{c}", "samples": 1, "stage": "final", "sha256": None})
        fid = {k: rng.normal() for k in ("f1_1m", "f1_since_start_12m", "funds_medrel_12m", "pop_medrel_12m")}
        ll, dec = rng.normal(), rng.normal()
        for fi, f in enumerate(FAM):
            r = blank_row(ck, f, f"lin{c % 6}")
            for k, v in fid.items():
                r[f"fid_test_{k}"] = v
            r[al.HELDOUT_X], r[al.DEC_X["c40"]] = ll, dec
            for s in al.ALL_SETS:
                # false acceptance follows one-month F1 strongly inside every family: that measure is falsified
                r[f"random_{s}_hack_1000"] = float(ndtr(0.5 * fi - 1 + 2.0 * fid["f1_1m"] + 0.1 * rng.normal()))
            r["rl_inflation_1000000"] = r["rl_gap_1000000"] = rng.normal()
            r["rl_gap_sd_1000000"] = r["rl_inflation_sd_1000000"] = 0.01
            rows.append(r)
    res = al.analyse(rows, n_boot=NB, seed=0)
    assert res["status"] == "complete"
    g = {"reader": al.Reader(tmp_path), "ladder": ladder}
    d = al.secondary_d79(g, rows, res, NB, 0)
    assert d["n_checkpoints_in_set"] == 24 and d["status"] == "complete" and d["wording_status"] == "made"
    m = {x["measure"]: x for x in d["measures"]}
    assert m["one-month F1"]["falsified"] is True and d["n_measures_falsified"] >= 1
    assert d["wording"]["claim"] == al.D79_SEC_WORDING["falsified"]
    assert d["wording"]["by_measure"]["one-month F1"] == al.D79_SEC_WORDING["falsified"]
    cl = m["one-month F1"]["rows"]["fid_test_f1_1m|c120"]["checkpoint_level"]
    assert cl["n_checkpoints"] == 24 and cl["spearman"].value > 0.9
    assert set(d["power"]) == {"c120", "c80"} and 0 <= d["power"]["c120"]["power_pooled"] <= 1
    assert d["wording"]["measures_not_falsified_with_power_at_least_0.8"] == []     # the claim is falsified
    assert "one-month F1" not in [x["measure"] for x in d["measures_not_falsified_with_power_at_least_0.8"]]


def sec_rows(rng, signal: float):
    rows, ladder = [], []
    for c in range(24):
        ck = f"ck{c:03d}"
        ladder.append({"checkpoint": ck, "run": f"r{c}", "samples": 1, "stage": "final", "sha256": None})
        fid = {k: rng.normal() for k in ("f1_1m", "f1_since_start_12m", "funds_medrel_12m", "pop_medrel_12m")}
        ll, dec = rng.normal(), rng.normal()
        for fi, f in enumerate(FAM):
            r = blank_row(ck, f, f"lin{c % 6}")
            for k, v in fid.items():
                r[f"fid_test_{k}"] = v
            r[al.HELDOUT_X], r[al.DEC_X["c40"]] = ll, dec
            for s_ in al.ALL_SETS:
                r[f"random_{s_}_hack_1000"] = float(ndtr(0.5 * fi - 1 + signal * fid["f1_1m"] + 0.3 * rng.normal()))
            r["rl_inflation_1000000"] = r["rl_gap_1000000"] = rng.normal()
            r["rl_gap_sd_1000000"] = r["rl_inflation_sd_1000000"] = 0.01
            rows.append(r)
    return rows, ladder


@pytest.mark.parametrize("power,claim", [(0.9, "not_falsified"), (0.5, "not_falsifiable")])
def test_decision_81_names_the_powered_measures_when_not_falsified(tmp_path, monkeypatch, power, claim):
    rows, ladder = sec_rows(np.random.default_rng(4), signal=0.0)     # no measure related to false acceptance
    res = al.analyse(rows, n_boot=NB, seed=0)
    fake = lambda dec, C, F, *a, **k: {"power_pooled": power, "power_checkpoint_level": power}   # noqa: E731
    monkeypatch.setattr(al, "sim_falsify_power", fake)
    d = al.secondary_d79({"reader": al.Reader(tmp_path), "ladder": ladder}, rows, res, NB, 0)
    assert d["n_measures_falsified"] == 0 and d["wording"]["claim"] == al.D79_SEC_WORDING[claim]
    named = [m["measure"] for m in d["measures_not_falsified_with_power_at_least_0.8"]]
    if power >= 0.8:
        assert named == [n for n, _ in al.D78_MEASURES]
        assert d["wording"]["measures_not_falsified_with_power_at_least_0.8"] == named
        assert all(d["wording"]["by_measure"][n] == al.D79_SEC_WORDING["not_falsified"] for n in named)
    else:
        assert named == [] and d["wording"]["measures_not_falsified_with_power_at_least_0.8"] == []
