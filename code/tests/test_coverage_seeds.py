"""Tests for ``code/scripts/coverage_seeds.py``: the analysis plan's position rule, the quantities
and the paired difference against the mean of three seeds on a small tree whose verdicts are known (each value
recomputed here from the verdict arrays with numpy, not with the script's readers), the refusals (an incomplete audit,
a card naming another checkpoint, a reference.json or an analysis file that disagrees), and, where the stored audits
exist, the run on them (the main checkpoint's numbers equal ``results/analysis/coverage.json``). CPU only; seconds."""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "code" / "scripts", ROOT / "code", ROOT / "hpr-dream"):
    sys.path.insert(0, str(p))

import coverage_seeds as cs  # noqa: E402
import hpr_dream.stats as hs  # noqa: E402

al = cs.al
FAM = al.FAMILIES
STARTS = ("s-a", "s-b", "s-c", "s-d", "s-e", "s-f")
NB = 200


def _wjson(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(al._jsonable(obj)))


def _wrecords(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _recs(inst: list, method: str, g: np.ndarray, o: np.ndarray, budgets=(10, 1000)) -> list:
    out = []
    for B in budgets:
        for (iid, f, st), gi, oi in zip(inst, g, o):
            out.append({"instance": iid, "method": method, "attacker": method, "scoring": "margin", "budget": B,
                        "attacker_seed": 0, "task": f, "cluster": st, "oracle_rule": "majority",
                        "grader_p": 0.75 if gi else 0.25, "oracle_accept": bool(oi)})
    return out


def small_tree(tmp: Path, seed: int = 0, drop=None, wrong_card=None):
    """Four models x two searches on 30 instances (6 start states x 5 families) with random verdicts, one perfect
    emulator per search; returns the paths and the verdict arrays (instance order of the tasks file)."""
    root = tmp / "repo"
    tasks = root / "data" / "tasks_v2_H24.json"
    _wjson(tasks, {"meta": {}, "instances": [{"start_id": f"{st}-v0", "task": f, "horizon": 24}
                                            for f in FAM for st in STARTS]})
    tsha = hashlib.sha256(tasks.read_bytes()).hexdigest()
    inst = [(f"{st}-v0|{f}|H24", f, st) for f in FAM for st in STARTS]
    rng = np.random.default_rng(seed)
    n = len(inst)
    eref = root / "results" / "audit" / "engine_reference"
    v = {}
    for m in cs.METHODS:
        gr, orr = rng.random(n) < 0.4, rng.random(n) < 0.5
        d = eref / "tasks_v2_H24" / al.REF_NAME[m]
        _wrecords(d / "records.jsonl.gz", _recs(inst, m, gr, orr))
        _wjson(d / "config.json", {"config": {"tasks_sha256": tsha}})
        v[(m, "ref")] = (gr, orr)
        for k, run in enumerate(cs.MODELS):
            g, o = rng.random(n) < 0.3 + 0.1 * k, rng.random(n) < 0.5
            o[0] = True                                          # every model has a selected plan that truly passes
            v[(m, run)] = (g, o)
            rows = _recs(inst, m, g, o)
            if drop and drop == (m, run):
                rows = [r for r in rows if r["instance"] != inst[3][0]]
            d = root / "results" / "audit" / "ladder" / run / "samples_006000000" / f"tasks_v2_H24{al.METHOD_DIR_SUFFIX[m]}"
            _wrecords(d / "records.jsonl.gz", rows)
            ck = wrong_card if wrong_card and wrong_card[0] == (m, run) else None
            judge = {"ckpt": f"/x/ckpt/{ck[1] if ck else run}/samples_006000000.pt",
                     "ckpt_sha256": hashlib.sha256((ck[1] if ck else run).encode()).hexdigest()}
            _wjson(d / "card.json", {"meta": {"judge": judge}, "hackability_curve": []})
            _wjson(d / "config.json", {"config": {"tasks_sha256": tsha}})
    return {"root": root, "tasks": tasks, "eref": eref, "inst": inst, "v": v}


def expected_analysis(t: dict) -> dict:
    """``coverage.json``'s main and coverage arms and their difference, built with ``analyse_ladder``'s own functions
    straight from ``read_audit`` (no alignment, no script code)."""
    rd = al.Reader(t["root"])
    tasks = al.load_tasks(t["tasks"])
    cache = {}
    out = {"main": "os_50m_full-samples_006000000", "coverage": "os_50m_cov-samples_006000000", "methods": {}}
    for m in cs.METHODS:
        u = {run: al.units_all_families(al.read_audit(cs.entry(run), m, tasks, t["root"], t["eref"], rd, cache), 1000)
             for run in ("os_50m_full", "os_50m_cov")}
        out["methods"][m] = {"budgets": {"1000": {"all": {
            "main": al.arm(u["os_50m_full"], NB, 0), "coverage": al.arm(u["os_50m_cov"], NB, 0),
            "coverage_minus_main": al.model_difference(u["os_50m_cov"], u["os_50m_full"], True, NB, 0)}}}}
    return json.loads(json.dumps(al._jsonable(out)))


def run(t: dict, tmp: Path, analysis: dict | None = None, extra=()):
    cov = tmp / "coverage.json"
    cov.write_text(json.dumps(analysis if analysis is not None else expected_analysis(t)))
    return cs.main(["--root", str(t["root"]), "--tasks", str(t["tasks"]), "--engine-reference", str(t["eref"]),
                    "--coverage-json", str(cov), "--replication-json", str(tmp / "absent.json"),
                    "--out", str(tmp / "out"), "--n-boot", str(NB), *extra])


def test_decision_87_position_rule():
    F = cs.Fraction
    assert cs.position(F(1, 10), [F(2, 10), F(3, 10), F(4, 10)]) == "below_all"
    assert cs.position(F(5, 10), [F(2, 10), F(3, 10), F(4, 10)]) == "above_all"
    assert cs.position(F(3, 10), [F(2, 10), F(3, 10), F(4, 10)]) == "within"
    assert cs.position(F(2, 10), [F(2, 10), F(3, 10), F(4, 10)]) == "within"      # a tie with the lowest seed
    assert cs.position(F(4, 10), [F(2, 10), F(3, 10), F(4, 10)]) == "within"      # and with the highest
    assert cs.position(None, [F(1, 2)] * 3) is None
    # exact counts: two false-rejection ratios that print alike are still ordered
    assert cs.position(F(1, 3), [F(333, 1000), F(1, 2), F(2, 3)]) == "within"
    assert cs.position(F(333, 1000), [F(1, 3), F(1, 2), F(2, 3)]) == "below_all"
    assert set(cs.WORDING) == {"below_all", "above_all", "within"}
    assert "cannot be told from seed-to-seed variation" in cs.WORDING["within"]


def test_quantities_and_paired_difference_on_a_known_tree(tmp_path):
    t = small_tree(tmp_path)
    res = run(t, tmp_path)
    assert res["status"] == "complete" and res["notes"] == [f"{r}, {m}: no reference.json" for m in cs.METHODS
                                                            for r in cs.MODELS]
    cl = [st for _, _, st in t["inst"]]
    for m in cs.METHODS:
        gr, orr = t["v"][(m, "ref")]
        rh = (gr & ~orr).astype(float)
        exc = {r: float(np.mean((t["v"][(m, r)][0] & ~t["v"][(m, r)][1]) - rh)) for r in cs.MODELS}
        rs = {r: float(np.mean(t["v"][(m, r)][1])) for r in cs.MODELS}
        fr = {r: float(np.mean(~t["v"][(m, r)][0][t["v"][(m, r)][1]])) for r in cs.MODELS}
        x = res["methods"][m]
        assert x["n"] == 30 and x["n_clusters"] == 6
        assert x["perfect_false_acceptance"].value == pytest.approx(rh.mean())
        for q, want in (("excess", exc), ("real_success", rs), ("false_rejection", fr)):
            got = x["quantities"][q]
            assert got["coverage"] == pytest.approx(want[cs.COV])
            assert got["seeds"] == pytest.approx([want[s] for s in cs.SEEDS])
            assert got["seed_min"] == pytest.approx(min(want[s] for s in cs.SEEDS))
            assert got["seed_max"] == pytest.approx(max(want[s] for s in cs.SEEDS))
            assert got["seed_mean"] == pytest.approx(np.mean([want[s] for s in cs.SEEDS]))
            d = got["coverage_minus_seed_mean"]
            assert d.value == pytest.approx(want[cs.COV] - np.mean([want[s] for s in cs.SEEDS]))
            assert d.n_boot == NB and d.n_clusters == 6
            pos = "below_all" if want[cs.COV] < min(want[s] for s in cs.SEEDS) - 1e-12 else (
                "above_all" if want[cs.COV] > max(want[s] for s in cs.SEEDS) + 1e-12 else "within")
            assert got["position"] == pos
            assert got["reading"] == (pos if q != "false_rejection" else None)
            assert got["wording"] == (cs.WORDING[pos] if q != "false_rejection" else None)
        # the interval of (i): hpr_dream.stats.excess on the arrays built here, BCa, each arm net of the reference as
        # analyse_ladder.model_difference writes it (with few clusters many replicates tie with the point, and BCa's
        # bias term counts ties, so the algebraically equal form without the reference can differ in the last bit)
        mean_h = np.mean([(t["v"][(m, s)][0] & ~t["v"][(m, s)][1]).astype(float) for s in cs.SEEDS], axis=0)
        e = hs.excess((t["v"][(m, cs.COV)][0] & ~t["v"][(m, cs.COV)][1]).astype(float) - rh, mean_h - rh, cl,
                      n_boot=NB, seed=0, bca=True)
        assert x["quantities"]["excess"]["coverage_minus_seed_mean"].bca_lo == pytest.approx(e.bca_lo)
        assert x["quantities"]["excess"]["coverage_minus_seed_mean"].hi == pytest.approx(e.hi)
        # (iii): the same resamples as the package's ratio for the coverage model alone
        g, o = t["v"][(m, cs.COV)]
        codes, C = al._encode(cl)
        W = hs._weights(C, NB, 0)
        sub = lambda gg, oo: (W @ np.bincount(codes, (oo & ~gg).astype(float), C)) / (W @ np.bincount(codes, oo.astype(float), C))
        with np.errstate(invalid="ignore", divide="ignore"):
            boot = sub(g, o) - np.mean([sub(*t["v"][(m, s)]) for s in cs.SEEDS], axis=0)
        ok = np.isfinite(boot)
        frd = x["quantities"]["false_rejection"]["coverage_minus_seed_mean"]
        assert frd.lo == pytest.approx(np.quantile(boot[ok], 0.025)) and frd.n_boot_undefined == int((~ok).sum())
    js = json.loads((tmp_path / "out" / "coverage_seeds.json").read_text())
    assert js["status"] == "complete" and js["methods"]["random"]["quantities"]["excess"]["position"] in cs.WORDING
    md = (tmp_path / "out" / "coverage_seeds.md").read_text()
    assert md.count("| coverage model |") == 2 and md.count("| seed 1 |") == 2


def test_refusals(tmp_path):
    t = small_tree(tmp_path / "a", drop=("cem_seeded", "os_50m_full_s2"))
    with pytest.raises(SystemExit):
        cs.build(t["root"], t["tasks"], t["eref"], tmp_path / "none.json", None, NB, 0)
    t = small_tree(tmp_path / "b", wrong_card=(("random", "os_50m_full_s1"), "os_50m_full_s2"))
    with pytest.raises(SystemExit, match="card"):
        run(t, tmp_path / "b")
    # an analysis file that disagrees with the records stops the run
    t = small_tree(tmp_path / "c")
    a = expected_analysis(t)
    a["methods"]["cem_seeded"]["budgets"]["1000"]["all"]["main"]["difference"]["value"] += 0.01
    with pytest.raises(SystemExit, match="coverage.json"):
        run(t, tmp_path / "c", analysis=a)
    a = expected_analysis(t)
    a["methods"]["random"]["budgets"]["1000"]["all"]["coverage_minus_main"]["false_rejection"]["bca_lo"] = 0.5
    with pytest.raises(SystemExit, match="coverage_minus_main"):
        run(t, tmp_path / "c", analysis=a)
    # a reference.json whose value differs from the records stops the run; one that agrees is checked silently
    d = t["root"] / "results" / "audit" / "ladder" / "os_50m_full_s1" / "samples_006000000" / "tasks_v2_H24"
    rd, tasks = al.Reader(t["root"]), al.load_tasks(t["tasks"])
    u = al.units_all_families(al.read_audit(cs.entry("os_50m_full_s1"), "random", tasks, t["root"], t["eref"], rd, {}),
                              1000)
    a1 = al.arm(u, NB, 0)
    grp = {"method": "random", "budget": 1000, "n_paired": 30, "difference": a1["difference"],
           "emulator": {"hackability": a1["emulator"]["hackability"]},
           "perfect_emulator": {"hackability": a1["perfect_emulator"]["hackability"]}}
    _wjson(d / "reference.json", {"subsets": {"all": {"groups": [grp]}}})
    res = run(t, tmp_path / "c")
    assert "os_50m_full_s1, random: no reference.json" not in res["notes"]
    assert res["methods"]["random"]["models"]["os_50m_full_s1"]["reference_json"]["status"] == "ok"
    grp["difference"] = dict(json.loads(json.dumps(al._jsonable(a1["difference"]))), value=0.9)
    _wjson(d / "reference.json", {"subsets": {"all": {"groups": [grp]}}})
    with pytest.raises(SystemExit, match="reference.json"):
        run(t, tmp_path / "c")


STORED = [ROOT / "results" / "audit" / "ladder" / r / "samples_006000000" / f"tasks_v2_H24{s}" / "records.jsonl.gz"
          for r in cs.MODELS for s in ("", "_cem_seeded")]


@pytest.mark.skipif(not all(p.is_file() for p in STORED) or not (ROOT / "results/analysis/coverage.json").is_file(),
                    reason="the stored audits are not here")
def test_stored_audits(tmp_path):
    res = cs.main(["--out", str(tmp_path)])           # 2,000 resamples: the analysis files' intervals must match
    assert res["status"] == "complete"
    for m in cs.METHODS:
        x = res["methods"][m]
        assert x["n"] == 193 and x["n_clusters"] == 40
        assert any(c.startswith(f"{m}: the main checkpoint's and the coverage model's") for c in res["checks"])
        for q, _, worded in cs.QUANTITIES:
            assert x["quantities"][q]["position"] in cs.WORDING
            assert (x["quantities"][q]["reading"] is not None) == worded
    assert (tmp_path / "coverage_seeds.md").read_text().count("| coverage model |") == 2
