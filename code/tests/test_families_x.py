"""The held-out extension : data/families_x.json and its start files beside the 40 held-out ones.

    pytest code/tests/test_families_x.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc.engine import Engine  # noqa: E402
from dc.families import (  # noqa: E402
    FAMILIES_DIR, MANIFEST_X_PATH, POP_BIN_NAMES, heldout_cty_of, load_manifest, pop_bin, regenerate_log,
    regenerate_start, sha256_file, starts,
)

pytestmark = pytest.mark.skipif(not MANIFEST_X_PATH.exists(), reason="data/families_x.json not built")


def _x():
    return load_manifest(MANIFEST_X_PATH)


def test_extension_manifest_shape():
    m, base = _x(), load_manifest()
    assert m["master_seed"] == base["master_seed"] and m["protocol"] == base["protocol"] and not m["failed"]
    fams = m["families"]
    assert [f["id"] for f in fams] == [f"ho-g-{k:02d}" for k in range(40, 120)]
    assert all(f["split"] == "heldout" and f["kind"] == "generated" and len(f["starts"]) == 1 for f in fams)
    # a quarter of the families per population band, each start in its target band
    assert [sum(f["target_band"] == b for f in fams) for b in POP_BIN_NAMES] == [20, 20, 20, 20]
    assert all(POP_BIN_NAMES[pop_bin(f["starts"][0]["summary"]["pop"])] == f["target_band"] for f in fams)
    old = {a["map_seed"] for f in base["families"] for a in f.get("attempts", []) if "map_seed" in a}
    new = {a["map_seed"] for f in fams for a in f["attempts"]}
    assert not old & new
    assert m["extends"]["manifest_sha256"] == sha256_file(ROOT / "data" / "families.json")


def test_extension_files_match_manifest():
    for f in _x()["families"]:
        for v in f["starts"]:
            assert sha256_file(FAMILIES_DIR / v["file"]) == v["sha256"], v["start_id"]
        assert sha256_file(FAMILIES_DIR / f["builder"]["log_file"]) == f["builder"]["log_sha256"]


def test_starts_unchanged_and_union():
    assert len(starts("heldout")) == 40
    cty = heldout_cty_of()
    assert len(cty) == 120 and all(Path(p).exists() for p in cty.values())
    assert {s for s, _f, _p in starts("heldout", _x())} == set(cty) - {s for s, _f, _p in starts("heldout")}


def test_extension_regenerates_bit_for_bit():
    fams = [_x()["families"][0], _x()["families"][-1]]
    eng = Engine()
    try:
        with tempfile.TemporaryDirectory() as td:
            for f in fams:
                v = f["starts"][0]
                assert regenerate_start(f, v, Path(td) / v["file"], eng, td) == v["sha256"], f["id"]
                log = regenerate_log(f, eng, td)
                assert np.array_equal(log[:f["builder"]["log_months"]], np.load(FAMILIES_DIR / f["builder"]["log_file"]))
    finally:
        eng.close()
