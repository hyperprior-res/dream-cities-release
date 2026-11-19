"""Tests for code/scripts/defence_baselines.py ."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "scripts"))

import defence_baselines as DB  # noqa: E402


def est(v, lo=None, hi=None):
    return {"value": v, "lo": v if lo is None else lo, "hi": v if hi is None else hi, "n_units": 10, "n_clusters": 5,
            "n_boot": 10, "n_boot_undefined": 0, "level": 0.95, "method": "cluster bootstrap, percentile",
            "bca_lo": None, "bca_hi": None}


def row(setting, judge, defence, param, fa, fr, rs, ja, hme=None):
    r = {"setting": setting, "label": setting, "judge": judge, "defence": defence, "param": param, "derived_from": "",
         "neutral": False, "n": 10, "n_clusters": 5, "hackability": est(fa), "false_rejection": est(fr),
         "oracle_accept": est(rs), "judge_accept": est(ja), "n_hacked": 1, "n_false_rejections": 1,
         "n_oracle_accept": 1, "n_judge_accept": 1, "same_plan_as_ensemble": 3}
    if hme is not None:
        r["hackability_minus_ensemble"] = est(hme, hme - 0.1, hme + 0.1)
    return r


def synthetic():
    rows = [{"setting": "perfect", "label": "perfect", "n": 10, "n_clusters": 5, "hackability": est(0.0),
             "false_rejection": est(0.1), "oracle_accept": est(0.5), "judge_accept": est(0.5)},
            row("member0", "member0", "none", 0.0, 0.2, 0.3, 0.4, 0.4, hme=-0.1),
            row("ensemble", "ensemble", "none", 0.0, 0.3, 0.2, 0.5, 0.6),
            row("temp1.5", "member0", "temperature", 1.5, 0.0, 1.0, 0.3, 0.0, hme=-0.3),
            row("penalty0", "ensemble", "penalty", 0.0, 0.1, 0.6, 0.5, 0.2, hme=-0.2),
            row("penalty1", "ensemble", "penalty", 1.0, 0.05, 0.7, 0.4, 0.1, hme=-0.25),
            {"setting": "policy-aware", "status": "slot"}]
    return {"design": {"budget": 1000, "searches": ["random"]}, "n_instances": 10, "n_families": 5,
            "frontier": {"random": {"rows": rows}}}


def test_own_baseline_and_increments():
    res = DB.build(synthetic())
    sr = res["searches"]["random"]
    by = {e["setting"]: e for e in sr["settings"]}
    assert by["temp1.5"]["baseline"] == "member0"
    c = by["temp1.5"]["against_own_baseline"]
    assert c["false_acceptance"]["difference"] == pytest.approx(-0.2)        # 0.0 - member 0's 0.2, not the ensemble's
    assert c["false_rejection"]["difference"] == pytest.approx(0.7)
    assert c["real_success"]["difference"] == pytest.approx(-0.1)
    assert isinstance(c["false_acceptance"]["difference_interval"], str)     # no paired interval against member 0
    p0 = by["penalty0"]["against_own_baseline"]
    assert p0["false_acceptance"]["difference"] == pytest.approx(-0.2)
    assert p0["false_acceptance"]["difference_interval"]["lo"] == pytest.approx(-0.3)   # the stored paired one
    inc = sr["penalty_increments"]["increments"]["penalty1"]["over_lambda0"]
    assert inc["false_acceptance"]["difference"] == pytest.approx(-0.05)
    assert inc["false_rejection"]["difference"] == pytest.approx(0.1)
    assert inc["real_success"]["difference"] == pytest.approx(-0.1)
    assert sr["not_run"] == [{"setting": "policy-aware", "status": "slot"}]


def test_stored_paired_difference_checked():
    fr = synthetic()
    fr["frontier"]["random"]["rows"][4]["hackability_minus_ensemble"]["value"] = 0.5      # inconsistent with the rates
    with pytest.raises(SystemExit):
        DB.build(fr)


def test_real_frontier(tmp_path):
    js = DB.main(["--out", str(tmp_path)])
    rnd = js["searches"]["random"]
    u = rnd["undefended"]
    assert u["ensemble"]["false_acceptance"]["value"] == pytest.approx(13 / 60)           # 0.217
    assert u["ensemble"]["false_rejection"]["value"] == pytest.approx(7 / 26)             # 0.269
    assert u["member0"]["false_acceptance"]["value"] == pytest.approx(8 / 60)             # 0.133
    p0 = next(e for e in rnd["settings"] if e["setting"] == "penalty0")
    assert p0["against_own_baseline"]["false_acceptance"]["defended"]["value"] == pytest.approx(0.100)
    assert p0["against_own_baseline"]["false_rejection"]["defended"]["value"] == pytest.approx(17 / 26)  # 0.654
    t15 = next(e for e in rnd["settings"] if e["setting"] == "temp1.5")
    assert t15["baseline"] == "member0"
    assert json.loads((tmp_path / "defence_baselines.json").read_text())["searches"]["random"]["settings"]
    assert (tmp_path / "defence_baselines.md").read_text().startswith("# Defences")
