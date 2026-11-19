"""Tests for code/scripts/fidelity_horizon.py ."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "scripts"))

import fidelity_horizon as FH  # noqa: E402

FID = ROOT / "results" / "fidelity" / "ladder"


def _h(ratio, mae=1.0, pop=(0.05, 0.1), funds=(0.03, 0.4)):
    ov = {"half": {n: {"mae_sample": mae * ratio, "mae_copy": mae, "ratio_sample": ratio}
                   for t, n in FH.OVERLAYS if t == "half"},
          "eighth": {n: {"mae_sample": mae * ratio, "mae_copy": mae, "ratio_sample": ratio}
                     for t, n in FH.OVERLAYS if t == "eighth"}}
    sc = {"powered_zones": {"mae_sample": 6.0 * ratio, "mae_copy": 0.5, "ratio_sample": 12.0 * ratio}}
    return {"scalars": sc, "mean_ratio_sample": ratio, "median_rel_pop": {"sample": pop[0], "copy": pop[1]},
            "median_rel_funds": {"sample": funds[0], "copy": funds[1]}, **ov}


def synthetic(ratio, key="k"):
    h = _h(ratio)
    return {"samples": 100, "selection_key": key, "selection": {"name": "test"}, "decoding": {"name": "a"},
            "rollouts": {"n_plans": 7, "K": 8, "h12": h, "h24": h,
                         "by_subset": {"open_loop": {"n_plans": 3, "h24": h}}},
            "gap_closed": {"pop_median_rel_12m": {"model": h["median_rel_pop"]["sample"], "copy": 0.1},
                           "funds_median_rel_12m": {"model": h["median_rel_funds"]["sample"], "copy": 0.4}}}


def floor(ratio, key="k"):
    """The engine yardstick's file holds the rollout blocks at its top level."""
    return {**synthetic(ratio)["rollouts"], "selection_key": key}


def test_horizon_row_synthetic():
    m, f = synthetic(1.5), floor(0.5)
    r = FH.horizon_row(m, f)
    assert r["engine_yardstick"] == "ok"
    assert r["overlays_24m_all_plans"]["pollution"]["model_ratio"] == 1.5
    assert r["overlays_24m_all_plans"]["fire_coverage"]["engine_ratio"] == 0.5
    assert r["n_overlays_model_ratio_ge_1"] == len(FH.OVERLAYS)
    assert r["open_loop_scalars_24m"]["n_plans"] == 3
    assert r["open_loop_scalars_24m"]["scalars"]["powered_zones"]["copy_mae"] == 0.5
    t = r["twelve_months_all_plans"]
    assert t["pop"]["model_within_bar"] and not t["funds"]["copy_within_bar"] and t["pop"]["bar"] == 0.10
    # an engine file of another selection is not used
    r2 = FH.horizon_row(m, floor(0.5, key="other"))
    assert r2["engine_yardstick"].startswith("selection key differs")
    assert r2["overlays_24m_all_plans"]["pollution"]["engine_ratio"] is None


def test_horizon_row_checks_gap_closed():
    m = synthetic(1.0)
    m["gap_closed"]["pop_median_rel_12m"]["model"] = 0.9
    with pytest.raises(SystemExit):
        FH.horizon_row(m, None)


@pytest.mark.skipif(not (FID / "os_50m_full" / "test").is_dir(), reason="fidelity files not present")
def test_real_files_match_review(tmp_path):
    g = FH.main(["--out", str(tmp_path)])
    rows = {(r["run"], r["stage"], r["split"]): r for r in g["horizon"]}
    m = rows[("os_50m_full", "final", "test")]
    ov = m["overlays_24m_all_plans"]
    assert round(ov["pollution"]["model_ratio"], 3) == 1.520 and round(ov["pollution"]["engine_ratio"], 3) == 0.703
    assert round(ov["fire_coverage"]["model_ratio"], 3) == 1.127 and round(ov["land_value"]["model_ratio"], 3) == 0.652
    pz = m["open_loop_scalars_24m"]["scalars"]["powered_zones"]
    assert m["open_loop_scalars_24m"]["n_plans"] == 173
    assert (round(pz["model_mae"], 1), round(pz["engine_mae"], 1), round(pz["copy_mae"], 1)) == (6.1, 0.0, 0.5)
    t = m["twelve_months_all_plans"]
    assert round(t["pop"]["copy"], 3) == 0.112 and round(t["funds"]["model"], 3) == 0.035
    assert sum(1 for k in rows if k[1:] == ("final", "test") and rows[k]["status"] == "ok") == 17
    assert sum(1 for k in rows if k[1:] == ("half", "dev") and rows[k]["status"] == "ok") == 17
    h = g["heldout"]["os_15m_small"]["half_vs_final_dev"]                  # R2 M4: -2,948 to -3,061
    assert round(h["half"]) == -2948 and round(h["final"]) == -3061 and h["final_below_half"]
    assert not g["heldout"]["os_50m_full"]["half_vs_final_dev"]["final_below_half"]
    assert json.loads((tmp_path / "heldout_likelihood.json").read_text())["runs"]
