"""Tests for ``code/scripts/threshold_reread.py``: the margin-structure check on ``dc.tasks`` and,
on the stored main-checkpoint audit, that the re-read at the audit's own threshold reproduces every stored verdict
and that only families whose margin is a uniform shift of theta are computed. CPU only; seconds."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "code" / "scripts", ROOT / "code", ROOT / "hpr-dream"):
    sys.path.insert(0, str(p))

import threshold_reread as tr  # noqa: E402


def test_margin_structure_on_dc_tasks():
    rng = np.random.default_rng(1)
    got = {f: tr.margin_is_a_shift(f, rng) for f in tr.al.FAMILIES}
    assert got["recover"]["uniform_shift"] and got["recover"]["all_feasible"]
    assert got["recover"]["max_deviation_from_uniform_shift"] < 1e-9
    for f in ("grow", "solvent", "treasury", "power"):
        assert not got[f]["uniform_shift"]


@pytest.mark.skipif(not (tr.AUDIT / "records.jsonl.gz").exists(), reason="the main audit is not stored here")
def test_stored_main_audit(tmp_path):
    res = tr.main(["--out", str(tmp_path), "--n-boot", "200"])
    assert res["theta_is_theta32_l50_on_every_instance"] and res["n_instances"] == 193
    rec = res["families"]["recover"]
    assert rec["status"] == "ok" and rec["levels"]["l50"]["reproduces_stored_verdicts"]
    assert rec["selection"]["emulator"]["unchanged"] and rec["selection"]["perfect_emulator"]["unchanged"]
    # a higher bar never adds an oracle acceptance, a lower one never removes one
    c = {lv: rec["levels"][lv]["counts"] for lv in ("l25", "l50", "l75")}
    assert c["l25"]["oracle_accepts"] >= c["l50"]["oracle_accepts"] >= c["l75"]["oracle_accepts"]
    for f in ("grow", "solvent", "treasury", "power"):
        assert res["families"][f]["status"].startswith("not computed") and "levels" not in res["families"][f]
    assert (tmp_path / "threshold_reread.md").read_text().count("| recover |") == 1
