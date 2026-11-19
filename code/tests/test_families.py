"""Start-state families (dc.families, data/families.json, data/families/).

pytest code/tests/test_families.py; run directly for the acceptance printout (families table,
population histogram by split, regeneration sha256 check on 10 families):

    python code/tests/test_families.py [--n-regen 10]
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc.engine import Engine  # noqa: E402
from dc.families import (  # noqa: E402
    BAR_POP, BAR_POWERED, BAR_ZONES, FAMILIES_DIR, FUNDS_CHOICES, POP_BIN_NAMES, POP_BINS, check_bar, families,
    load_manifest, pop_bin, regenerate_log, regenerate_start, sha256_file, starts, tile_colours,
)
from dc.grammar import is_valid_plan  # noqa: E402


def _ref(f):
    """The family's reference start: the full warm-up (generated) or the bundled file itself."""
    return f["starts"][-1] if f["kind"] == "generated" else f["starts"][0]


def regen_check(fams, eng) -> list:
    out = []
    with tempfile.TemporaryDirectory() as td:
        for f in fams:
            for v in f["starts"]:
                p = Path(td) / v["file"]
                sha = regenerate_start(f, v, p, eng, td)
                out.append((f["id"], v["start_id"], v["months"], sha == v["sha256"]))
    return out


# ----------------------------------------------------------------------------------------------
def test_manifest_shape():
    m = load_manifest()
    tr, ho = families("train", m), families("heldout", m)
    assert len(tr) == 60 and len(ho) == 40 and not m["failed"]
    assert all(f["kind"] == "generated" for f in ho)
    assert all(len(f["starts"]) == 1 for f in ho)
    assert all(1 <= len(f["starts"]) <= 4 for f in tr)
    bundled = [f for f in tr if f["kind"] == "bundled"]
    assert len(bundled) <= 20 and [f["source"] for f in bundled] == sorted(f["source"] for f in bundled)
    seeds_tr = {f["builder"]["map_seed"] for f in tr if f["kind"] == "generated"}
    seeds_ho = {f["builder"]["map_seed"] for f in ho}
    assert not seeds_tr & seeds_ho
    ids = [v["start_id"] for f in m["families"] for v in f["starts"]]
    assert len(ids) == len(set(ids))
    for f in m["families"]:
        assert f["builder"]["funds_final"] in FUNDS_CHOICES
        if f["kind"] == "generated":
            assert 60 <= f["builder"]["warmup_months"] <= 360


def test_files_match_manifest():
    m = load_manifest()
    for f in m["families"]:
        for v in f["starts"]:
            assert sha256_file(FAMILIES_DIR / v["file"]) == v["sha256"], v["start_id"]
        log = np.load(FAMILIES_DIR / f["builder"]["log_file"])
        assert sha256_file(FAMILIES_DIR / f["builder"]["log_file"]) == f["builder"]["log_sha256"]
        assert log.shape == (f["builder"]["log_months"], 25) and is_valid_plan(log)
    on_disk = {p.name for p in FAMILIES_DIR.glob("*.cty")}
    expected = {v["file"] for f in m["families"] for v in f["starts"]}
    ext = FAMILIES_DIR.parent / "families_x.json"       # the extension's 80 held-out cities, their own manifest
    if ext.exists():
        import json
        expected |= {v["file"] for f in json.loads(ext.read_text())["families"] for v in f["starts"]}
    assert on_disk == expected


def test_starts_listing():
    tr, ho = starts("train"), starts("heldout")
    assert len(ho) == 40 and len(tr) >= 60
    assert all(p.exists() for _, _, p in tr + ho)


def test_bar_holds_on_sample():
    eng = Engine()
    try:
        m = load_manifest()
        allv = [(f, v) for f in m["families"] for v in f["starts"]]
        rng = np.random.default_rng(0)
        for k in rng.choice(len(allv), 12, replace=False):
            f, v = allv[int(k)]
            ok, info = check_bar(eng, FAMILIES_DIR / v["file"])
            assert ok, (v["start_id"], info)
            assert info["pop"] == v["summary"]["pop"] and info["pop"] >= BAR_POP
            assert info["zones"] >= BAR_ZONES and info["powered_fraction"] >= BAR_POWERED
    finally:
        eng.close()


def test_bar_rejects_empty_terrain():
    eng = Engine()
    try:
        ok, info = check_bar(eng, ROOT / "data" / "cities" / "about.cty")
        assert not ok and "pop" in info["fails"]
    finally:
        eng.close()


def test_regeneration_bit_for_bit():
    m = load_manifest()
    gen = [f for f in families("train", m) if f["kind"] == "generated"]
    fams = [gen[0], families("heldout", m)[-1], [f for f in m["families"] if f["kind"] == "bundled"][0]]
    eng = Engine()
    try:
        res = regen_check(fams, eng)
        assert all(r[3] for r in res), res
        with tempfile.TemporaryDirectory() as td:
            for f in fams[:2]:
                log = regenerate_log(f, eng, td)
                assert np.array_equal(log, np.load(FAMILIES_DIR / f["builder"]["log_file"])), f["id"]
    finally:
        eng.close()


def test_palette():
    eng = Engine()
    try:
        eng.load_start(ROOT / "data" / "cities" / "linecity.cty")
        rgb = tile_colours(eng.observe().tiles)
        assert rgb.shape == (100, 120, 3) and rgb.min() >= 0 and rgb.max() <= 1
    finally:
        eng.close()


# ----------------------------------------------------------------------------------------------
def acceptance(n_regen: int) -> None:
    m = load_manifest()
    fams = m["families"]
    print("B1 acceptance 5: families (reference start at load: generated = full warm-up, bundled = the file)")
    print(f"{'family':30s} {'split':7s} {'kind':9s} {'style':9s} {'funds0':>6s} {'W':>3s} {'pop':>8s} {'funds':>9s} "
          f"{'zones':>5s} {'powered':>7s} {'variants':>8s} {'attempts':>8s}")
    for f in fams:
        b, s = f["builder"], _ref(f)["summary"]
        print(f"{f['id']:30s} {f['split']:7s} {f['kind']:9s} {b['style']:9s} {str(b.get('funds0', '-')):>6s} "
              f"{b['warmup_months']:3d} {s['pop']:8,d} {s['funds']:9,d} {s['zones']:5d} {s['powered_fraction']:7.2f} "
              f"{len(f['starts']):8d} {len(f['attempts']):8d}")
    print()
    print("population histogram by split (families, reference start):")
    print(f"{'split':8s} " + " ".join(f"{n:>8s}" for n in POP_BIN_NAMES))
    for split in ("train", "heldout"):
        h = [0] * len(POP_BINS)
        for f in families(split, m):
            h[pop_bin(_ref(f)["summary"]["pop"])] += 1
        print(f"{split:8s} " + " ".join(f"{v:8d}" for v in h))
    print("population histogram by split (every start variant):")
    for split in ("train", "heldout"):
        h = [0] * len(POP_BINS)
        n = 0
        for f in families(split, m):
            for v in f["starts"]:
                h[pop_bin(v["summary"]["pop"])] += 1
                n += 1
        print(f"{split:8s} " + " ".join(f"{v:8d}" for v in h) + f"   ({n} starts)")
    print()
    rng = np.random.default_rng(10)
    gen = [f for f in fams if f["kind"] == "generated"]
    bun = [f for f in fams if f["kind"] == "bundled"]
    pick = [gen[int(k)] for k in rng.choice(len(gen), n_regen - 2, replace=False)] + \
        [bun[int(k)] for k in rng.choice(len(bun), 2, replace=False)]
    eng = Engine()
    res = regen_check(pick, eng)
    with tempfile.TemporaryDirectory() as td:
        logs_same = sum(np.array_equal(regenerate_log(f, eng, td), np.load(FAMILIES_DIR / f["builder"]["log_file"]))
                        for f in pick)
    eng.close()
    print(f"regeneration from the manifest record alone, {len(pick)} families ({n_regen - 2} generated, 2 bundled):")
    for fid, sid, mo, same in res:
        print(f"  {sid:34s} months {mo:3d}  sha256 {'identical' if same else 'DIFFERENT'}")
    print(f"start files identical: {sum(r[3] for r in res)} / {len(res)}; builder policy re-run from its seeds "
          f"reproduces the stored warm-up log: {logs_same} / {len(pick)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-regen", type=int, default=10)
    acceptance(ap.parse_args().n_regen)
