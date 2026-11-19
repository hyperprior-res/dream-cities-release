"""Tests for the addition to ``code/scripts/analyse_ladder.py``: the analysis plan's contrast ,
random search's excess over the perfect emulator at 1,000 minus at budget 1, paired by instance, on all 120 cities
and on the 40, in ``replication.json``'s ``budget_contrast_d99`` after every earlier field. The small tree is
``test_analyse_ladder.py``'s, with verdicts changed at one budget so that the contrast is known by hand. CPU only;
seconds."""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "code" / "tests", ROOT / "code" / "scripts", ROOT / "code", ROOT / "hpr-dream"):
    sys.path.insert(0, str(p))

import analyse_ladder as al  # noqa: E402
import hpr_dream.stats as hs  # noqa: E402
from test_analyse_ladder import _wrecords, build_tree, write_run  # noqa: E402

FAM = al.FAMILIES
NB = 50                                            # the resamples run_main asks for
STARTS = {"c40": ["s-a", "s-b", "s-c", "s-d"], "c80": ["s-e", "s-f"]}   # build_tree's start states (the clusters)

# The tree's random search falsely accepts, at every budget, instance j < h[f] of family f (h40 = 0, 1, 2, 3, 3 of 4;
# h80 = 0, 1, 0, 1, 0 of 2), and its perfect emulator never does. Changed here, one budget each:
#   (a) emulator, B = 1, 40 cities: `recover` instances 0, 1, 2 rejected by the judge   -> contrast +1 on each
#   (b) emulator, B = 1, 80 cities: `treasury` instance 0 accepted, the oracle rejects  -> contrast -1
#   (c) perfect emulator, B = 1,000, 40 cities: `power` instance 0 falsely accepted     -> contrast -1
CHANGES = {("emulator", "c40", 1, "recover"): ({"s-a", "s-b", "s-c"}, 0.0),
           ("emulator", "c80", 1, "treasury"): ({"s-e"}, 1.0),
           ("perfect", "c40", 1000, "power"): ({"s-a"}, 1.0)}


def _read(path: Path) -> list[dict]:
    with gzip.open(path, "rt") as f:
        return [json.loads(x) for x in f]


def _change(recs: list[dict], who: str, s: str) -> list[dict]:
    for r in recs:
        for (w, cs, B, f), (clusters, gp) in CHANGES.items():
            if (w, cs) == (who, s) and r["method"] == "random" and r["budget"] == B and r["task"] == f \
                    and r["cluster"] in clusters:
                assert not r["oracle_accept"]
                r["grader_p"] = gp
    return recs


def changed_tree(tmp: Path) -> dict:
    t = build_tree(tmp)
    run = t["root"] / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000"
    for s, stem in (("c40", "tasks"), ("c80", "tasksx")):
        d = run / stem
        tsha = json.loads((d / "config.json").read_text())["config"]["tasks_sha256"]
        jsha = json.loads((d / "card.json").read_text())["meta"]["judge"]["ckpt_sha256"]
        write_run(d, _change(_read(d / "records.jsonl.gz"), "emulator", s), tsha, jsha,
                  pool_stats=(d / "pool_stats.json").exists())          # card.json follows the changed records
        ref = t["eref"] / t["tasks"][s].stem / "B_economy" / "records.jsonl.gz"
        _wrecords(ref, _change(_read(ref), "perfect", s))
    return t


def hand_contrast(s: str) -> tuple[np.ndarray, list]:
    """Per instance of city set ``s`` (in any order): the contrast and the start state, from the verdicts above."""
    sets = ("c40", "c80") if s == "c120" else (s,)
    vals, cl = [], []
    for cs in sets:
        h = build_h(cs)
        for f in FAM:
            for j, st in enumerate(STARTS[cs]):
                def falsely(who, B):
                    base = who == "emulator" and j < h[f]
                    ch = CHANGES.get((who, cs, B, f))
                    return float(ch[1] >= 0.5) if ch and st in ch[0] else float(base)
                vals.append((falsely("emulator", 1000) - falsely("perfect", 1000))
                            - (falsely("emulator", 1) - falsely("perfect", 1)))
                cl.append(st)
    return np.array(vals), cl


def build_h(cs: str) -> dict:
    return {f: (min(i, 3) if cs == "c40" else i % 2) for i, f in enumerate(FAM)}


def same(a: hs.Estimate, b: hs.Estimate) -> bool:
    """Every field equal, NaN equal to NaN (an undefined BCa limit)."""
    return all(x == y or (isinstance(x, float) and np.isnan(x) and np.isnan(y))
               for x, y in zip(a.as_dict().values(), b.as_dict().values()))


@pytest.fixture(scope="module")
def ran(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("bc")
    t = changed_tree(tmp)
    out = tmp / "out"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(al, "D79_SIM", 40)
        mp.setattr(al, "D79_SIM_BOOT", 100)
        r = al.main(["--root", str(t["root"]), "--ckpt-root", str(t["ckpt"]), "--tasks", str(t["tasks"]["c40"]),
                     "--tasks-x", str(t["tasks"]["c80"]), "--engine-reference", str(t["eref"]),
                     "--cov-fidelity-fallback", str(t["covtree"]), "--cov-rl-fallback", str(tmp / "nofleet"),
                     "--out", str(out), "--n-boot", str(NB), "--workers", "1"])
    return t, r, out


def test_contrast_equals_the_hand_computation_and_the_package_interval(ran):
    t, r, out = ran
    rep = r["replication"]
    bc = rep["budget_contrast_d99"]
    assert bc["search"] == "random" and bc["budgets"] == [1000, 1] and bc["status"] == "ok"
    # by hand: 40 cities (+3 - 1) / 20; 120 cities (+3 - 1 - 1) / 30; the excess at each budget
    want = {"c40": (2 / 20, 8 / 20, 6 / 20, 20, 4), "c120": (1 / 30, 10 / 30, 9 / 30, 30, 6)}
    for s, (c, e1000, e1, n, C) in want.items():
        v = bc[s]
        assert v["status"] == "ok" and v["n"] == n and v["n_clusters"] == C
        assert v["contrast"].value == pytest.approx(c, abs=1e-12)
        assert v["excess_at_1000"] == pytest.approx(e1000, abs=1e-12) and v["excess_at_1"] == pytest.approx(e1, abs=1e-12)
        # each budget's excess is the replication's difference at that budget
        for B in (1000, 1):
            assert v[f"excess_at_{B}"] == pytest.approx(rep["methods"]["random"][B][s]["difference"].value, abs=1e-12)
        # the interval is the package's: hpr_dream.stats.excess on the hand-built contrasts, same clusters and seed
        vals, cl = hand_contrast(s)
        assert vals.sum() == pytest.approx(c * n)
        e = hs.excess(vals, np.zeros(vals.size), cl, n_boot=NB, seed=0, bca=True)
        for fld in ("value", "lo", "hi", "n_units", "n_clusters", "n_boot", "n_boot_undefined"):
            assert getattr(v["contrast"], fld) == pytest.approx(getattr(e, fld), abs=1e-12), fld
        for fld in ("bca_lo", "bca_hi"):
            assert np.isfinite(getattr(e, fld)) == np.isfinite(getattr(v["contrast"], fld))
            if np.isfinite(getattr(e, fld)):
                assert getattr(v["contrast"], fld) == pytest.approx(getattr(e, fld), abs=1e-12), fld
        lo, hi, kind = al.interval(e)
        assert v["interval_kind"] == kind and v["interval"] == pytest.approx([lo, hi], abs=1e-12)
    # the 80 cities alone are not part of the statistic
    assert "c80" not in bc


def test_new_field_comes_after_every_earlier_one(ran):
    t, r, out = ran
    js = json.loads((out / "replication.json").read_text())
    keys = list(js)
    assert keys[-1] == "budget_contrast_d99" and keys[-2] == "statement_d79"
    assert keys[:-1] == ["generated_utc", "command", "checkpoint", "methods", "missing", "checks", "statement", "status",
                         "statement_d79"]
    b = js["budget_contrast_d99"]
    assert list(b) == ["search", "budgets", "definition", "interval", "c120", "c40", "status"]
    assert b["c120"]["contrast"]["value"] == pytest.approx(1 / 30) and b["c40"]["interval_kind"] in ("BCa", "percentile")
    assert {"lo", "hi", "bca_lo", "bca_hi", "n_boot"} <= set(b["c120"]["contrast"])
    md = (out / "replication.md").read_text()
    assert md.index("random search's excess over the perfect emulator") > md.index("replication statement")
    assert f"all 120 cities {al.fbs(r['replication']['budget_contrast_d99']['c120']['contrast'])} (30 instances)" in md


def test_pairing_is_by_instance_key_and_mismatches_are_refused(ran):
    t, r, out = ran
    aud = r["gather"]["audits"][t["tag"]][("random", "c40")]
    ua, ub = al.units_all_families(aud, 1000), al.units_all_families(aud, 1)
    base = al.budget_contrast(ua, ub, NB, 0)
    # the same instances in another order give the same contrast and interval
    perm = np.random.default_rng(0).permutation(ub["n"])
    shuffled = {**ub, "keys": [ub["keys"][i] for i in perm], "cl": [ub["cl"][i] for i in perm],
                **{k: ub[k][perm] for k in ("ga", "oa", "gr", "orr")}}
    again = al.budget_contrast(ua, shuffled, NB, 0)
    assert same(again["contrast"], base["contrast"]) and again["excess_b"] == base["excess_b"]
    # a set against itself: zero on every resample
    z = al.budget_contrast(ua, ua, NB, 0)["contrast"]
    assert z.value == 0 and z.lo == 0 and z.hi == 0
    # another instance set, or an instance in another cluster, is refused
    fewer = {**ub, "keys": ub["keys"][1:], "cl": ub["cl"][1:], **{k: ub[k][1:] for k in ("ga", "oa", "gr", "orr")}}
    with pytest.raises(SystemExit, match="same instances"):
        al.budget_contrast(ua, fewer, NB, 0)
    moved = {**ub, "cl": ["elsewhere"] + list(ub["cl"][1:])}
    with pytest.raises(SystemExit, match="different clusters"):
        al.budget_contrast(ua, moved, NB, 0)
    # without the perfect emulator at a budget the contrast is not computable, and said so
    unpaired = dict(r["gather"]["audits"][t["tag"]])
    fam = {f: dict(b) for f, b in unpaired[("random", "c40")]["families"].items()}
    for f in FAM:
        fam[f][1] = {**fam[f][1], "gr": None, "orr": None}
    unpaired[("random", "c40")] = {**unpaired[("random", "c40")], "families": fam}
    d = al.budget_contrast_d99(unpaired, r["replication"]["methods"]["random"], NB, 0)
    assert d["status"] == "partial" and d["c40"]["status"].startswith("not computable")
    assert d["c120"]["status"].startswith("not computable")
