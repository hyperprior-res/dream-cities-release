"""Tests for code/scripts/logged_plan_verdicts.py ."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "scripts"))

import logged_plan_verdicts as LV  # noqa: E402

MAIN = ROOT / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000" / "tasks_v2_H24"


def test_confusion_counts():
    gp = np.array([1.0, 0.5, 0.375, 0.0, 0.625, 0.125])     # emulator accepts at >= 0.5: T T F F T F
    mg = np.array([0.2, -0.1, 0.0, -2.0, -0.3, 1.0])       # oracle accepts at >= 0:   T F T F F T
    c = LV.confusion(gp, mg)
    assert (c["n_oracle_accept"], c["n_oracle_reject"]) == (3, 3)
    assert c["n_emulator_rejects_oracle_accepted"] == 2         # plans 2 and 5
    assert c["n_emulator_accepts_oracle_rejected"] == 2         # plans 1 and 4
    assert c["false_rejection"] == pytest.approx(2 / 3)
    assert c["false_acceptance"] == pytest.approx(2 / 3)


def test_parse_header():
    h = LV.parse_header("judge emulator; 193 instances in 40 clusters; residual pool rule economy (1000 rows per pool); "
                        "family confusion rates on 19300 behaviour plans: grow fp 0.006 fn 0.750; solvent fp 0.006 fn "
                        "0.903; oracle: majority over 32 seeds (pass share >= 0.5)\nrest")
    assert h["n_plans"] == 19300
    assert h["by_task"]["grow"] == {"fp": 0.006, "fn": 0.75}
    assert h["by_task"]["solvent"]["fn"] == 0.903
    assert LV.parse_header("judge emulator; n/a; oracle") == {}


@pytest.mark.skipif(not (MAIN / "pools.npz").is_file(), reason="main audit not present")
def test_main_checkpoint_matches_review(tmp_path):
    js = LV.main(["--out", str(tmp_path), "--n-boot", "50"])
    row = next(r for r in js["checkpoints"] if r["checkpoint"] == "os_50m_full-samples_006000000")
    assert row["status"] == "ok"
    f = row["families"]
    assert f["grow"]["false_rejection"] == pytest.approx(0.750)            # R2 F1.3: 0.750 (grow)
    assert f["grow"]["n_oracle_accept"] == 204 and f["grow"]["n_emulator_rejects_oracle_accepted"] == 153
    assert f["solvent"]["false_rejection"] == pytest.approx(28 / 31)       # 0.903
    assert round(f["treasury"]["false_acceptance"], 3) == 0.130
    assert round(f["recover"]["false_acceptance"], 3) == 0.173
    assert row["all_plans_pooled"]["n_plans"] == 19300
    # a run without floors is reported as not stored, not computed
    nf = next(r for r in js["checkpoints"] if r["checkpoint"] == "os_100m_full-samples_006000000")
    assert nf["status"].startswith("not stored")
    assert json.loads((tmp_path / "logged_plan_verdicts.json").read_text())["checkpoints"]
