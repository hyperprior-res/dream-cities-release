"""``run_audit.py --floors none``: ``NoFloorAudit`` computes nothing in phase 2 and no economy verdict
rows in phase 1, and its real attacks are those of ``dc.audit.Audit`` with ``floors=()``. Stub judges, CPU only.

    pytest code/tests/test_no_floor_audit.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "scripts"))
sys.path.insert(0, str(ROOT / "code" / "tests"))
sys.path.insert(0, str(ROOT / "hpr-dream"))

from dc import audit as A  # noqa: E402
import run_audit as RA  # noqa: E402
from test_audit import StubEngine, StubJudge, _instances, _pools  # noqa: E402

KEYS = ("instance", "method", "budget", "best_index", "best_score", "grader_score", "plan_hash", "oracle_accept",
        "oracle_share", "oracle_margin")


def _cfg(**kw):
    d = dict(budgets=(1, 10, 100), methods=("random",), floors=(), pool_verdict_plans=100, behaviour_plans=50,
             residual_pool="economy", economy_top=10, economy_random=5, verdict_cap=100, subset_n=0,
             oracle="majority", oracle_seeds=32, floor_basis="truth")
    d.update(kw)
    return A.amendment2_config(**d)


def test_no_floor_audit_skips_floor_work_and_keeps_the_attacks(tmp_path):
    inst = _instances(starts=("sA", "sB"))
    pools = _pools(["sA", "sB"])
    runs = {}
    for name, cls, cfg in (("base", A.Audit, _cfg(cross_check="instance")), ("none", RA.NoFloorAudit, _cfg(cross_check=""))):
        judge, engine = StubJudge(), StubEngine()
        au = cls(cfg, inst, judge, engine, pools, tmp_path / name, log=lambda s: None)
        runs[name] = (au.run(), judge, engine)
    base, none = runs["base"][0], runs["none"][0]
    rb = {r["plan_id"]: r for r in base["records"]}
    rn = {r["plan_id"]: r for r in none["records"]}
    assert set(rb) == set(rn) and len(rn) == len(inst) * 3
    for k in rn:
        assert all(rn[k][f] == rb[k][f] for f in KEYS), k
    # phase 2: nothing; phase 1: no economy verdict rows
    for c in none["costs"]:
        assert c["phase2"]["oracle_distinct_replays"] == 0 and c["phase2"]["engine_requests"] == 0
    assert all(d["extra_verdict_rows"]["behaviour"] == 0 for d in none["p1"].values())
    assert any(d["extra_verdict_rows"]["behaviour"] > 0 for d in base["p1"].values())
    assert runs["none"][1].month_steps < runs["base"][1].month_steps
    assert all("truth_pools" not in d or not d["truth_pools"] for d in none["p2"].values())


def test_no_floor_audit_refuses_floors(tmp_path):
    inst = _instances(starts=("sA",))
    au = RA.NoFloorAudit(_cfg(floors=("flip",), cross_check=""), inst, StubJudge(), StubEngine(), _pools(["sA"]),
                         tmp_path, log=lambda s: None)
    try:
        au.run()
    except RuntimeError as e:
        assert "without floors" in str(e)
    else:
        raise AssertionError("NoFloorAudit ran a configuration with a floor")
