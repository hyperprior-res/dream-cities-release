"""Tests of the city audit pipeline (dc.audit) with stub judges, plus small real-engine checks. CPU only."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hpr-dream"))

import hpr_dream as hd  # noqa: E402
from dc import audit as A  # noqa: E402
from dc import tasks as T  # noqa: E402
from dc.engine import DISASTER_EARTHQUAKE, SC_FUNDS, SC_POP  # noqa: E402
from dc.grammar import compile_plan, random_plan  # noqa: E402
from dc.oracle import replay  # noqa: E402
from dc.seeds import seed_for  # noqa: E402

H = 24
CAL = A.CAL_DIR / "H24"


def _traj(pop_h: np.ndarray, H: int = H) -> np.ndarray:
    """Scalar trajectories with population pop_h at H (linear from 1,000) and funds 10,000 throughout."""
    pop_h = np.asarray(pop_h, dtype=np.float64)
    s = np.zeros(pop_h.shape + (H + 1, 20))
    s[..., SC_FUNDS] = 10000.0
    s[..., SC_POP] = 1000.0 + (pop_h[..., None] - 1000.0) * np.linspace(0, 1, H + 1)
    return s


def _value(P: np.ndarray) -> np.ndarray:
    """A deterministic function of an effective plan in [0, 1]: mean tax over the months / 20."""
    return P[..., 0].astype(np.float64).mean(axis=-1) / 20.0


class StubJudge(A.SamplingJudge):
    """Population at H = 1000 + 2000 * value(plan) + 300 * noise (stream-seeded); or always far above."""

    name = "stub"

    def __init__(self, always_accept=False):
        super().__init__()
        self.always_accept = always_accept
        self.seen = []

    def _samples(self, inst, P, K, stream):
        self.seen.append((inst.task, P[:, :, A.FORCED_COL].copy()))
        rng = np.random.default_rng(seed_for("stub-judge", inst.start_id, *stream))
        if self.always_accept:
            pop = np.full((P.shape[0], K), 1e7)
        else:
            pop = 1000.0 + 2000.0 * _value(P)[:, None] + 300.0 * rng.standard_normal((P.shape[0], K))
        return _traj(pop, P.shape[1])


class StubEngine:
    """Population at H = 1000 + 2000 * value(plan) + 100 * N(0, 1) seeded by (plan, seed); or a fixed
    verdict per start (``fixed``: start_id -> True (accept) / False (reject))."""

    workers = 0

    def __init__(self, fixed=None):
        self.fixed = fixed or {}
        self.seen = []
        self.n_requests = self.n_replays = 0

    def scalars(self, inst, eff, seeds, key_sink=None, store=True):
        P = np.asarray(eff).reshape(-1, H, 25)
        sd = np.broadcast_to(np.asarray(seeds, dtype=np.int64), (P.shape[0],))
        if key_sink is not None:
            key_sink.update((inst.start_id, A.plan_hash(p), int(s)) for p, s in zip(P, sd))
        self.seen.append((inst.task, P[:, :, A.FORCED_COL].copy()))
        self.n_requests += P.shape[0]
        self.n_replays += P.shape[0]
        if inst.start_id in self.fixed:
            pop = np.full(P.shape[0], 1e7 if self.fixed[inst.start_id] else 0.0)
        else:
            noise = np.array([np.random.default_rng([int(s), int(A.plan_hash(p)[:8], 16)]).standard_normal()
                              for p, s in zip(P, sd)])
            pop = 1000.0 + 2000.0 * _value(P) + 100.0 * noise
        return np.rint(_traj(pop)).astype(np.int64)

    def counters(self):
        return {"engine_requests": self.n_requests, "engine_replays": self.n_replays, "engine_seconds": 0.0}


def _instances(starts=("sA", "sB", "sC", "sD"), tasks=("grow", "recover")):
    out = []
    for t in tasks:
        for k, s in enumerate(starts):
            theta = 2000.0 if t == "grow" else 1.8      # recover: population ratio to the start (1,000)
            sd = 400.0 if t == "grow" else 0.4
            out.append(A.Instance(f"{s}|{t}|H{H}", s, f"fam-{s}", t, H, theta, sd, True, f"/nonexistent/{s}.cty"))
    return out


def _pools(starts, n=120, seed=0):
    rng = np.random.default_rng(seed)
    arr = {}
    for s in starts:
        arr[("behaviour", s)] = np.stack([random_plan(rng, H, p_noop_macro=0.5) for _ in range(n)])
        arr[("builders", s)] = np.stack([random_plan(rng, H, p_noop_macro=0.3) for _ in range(n)])
    return A.Pools(H, arrays=arr)


CFG = dict(budgets=(1, 10, 100), methods=("cem", "random", "best_of_n", "random_verdict"), search_seeds=(0,),
           floors=("residual", "flip"), pool_verdict_plans=30, residual_pool="family", flip_scope="all")


def _run(work, judge=None, engine=None, crash_after=None, cfg=None, instances=None, pools=None):
    inst = instances or _instances()
    judge = judge or StubJudge()
    engine = engine or StubEngine()
    pools = pools or _pools(sorted({i.start_id for i in inst}))
    au = A.Audit(A.AuditConfig(**(cfg or CFG)), inst, judge, engine, pools, work, log=lambda s: None)
    return au.run(crash_after=crash_after), judge, engine, inst


def _canon(records):
    return [json.dumps(r, sort_keys=True) for r in records]


def test_budget_counts_exact(tmp_path):
    res, judge, engine, inst = _run(tmp_path / "w")
    recs = res["records"]
    assert len(recs) == len(inst) * 4 * 3
    for r in recs:
        assert r["n_scored"] == r["budget"]
        k = A.K_VERDICT if r["method"] == "random_verdict" else A.K_SEARCH
        assert r["emu_month_steps_search"] == r["budget"] * k * H
        assert r["emu_month_steps_verdict"] == A.K_VERDICT * H
        for f in ("residual", "flip"):
            assert isinstance(r[f"{f}_grader_accept"], bool)
    # the judge's own counter equals the design: shared per (start, forced events) + per instance
    n_sf = len({(i.start_id, i.forced_key) for i in inst})
    shared = (100 * 2 + 100 * 8 + 100 * 2 + 30 * 8) * H  # proposals (K=2), pool verdicts (K=8), builders (K=2),
                                                          # builder residual plans (K=8)
    per_inst = 111 * 2 * H                               # CEM 1 + 10 + 100 plans
    sel = sum(d["selected_verdict_rollouts"] for d in res["p1"].values())      # distinct selected plans, 8 samples
    assert 0 < sel <= 12 * len(inst)
    assert judge.month_steps == shared * n_sf + per_inst * len(inst) + sel * 8 * H
    # floor attacks scored exactly B plans against each surrogate
    for d in res["p2"].values():
        for (m, B, s, k), f in d["floors"].items():
            assert f["n_scored"] == B
    # a stated budget without a CEM schedule is refused
    with pytest.raises(ValueError):
        A.AuditConfig(budgets=(7,), methods=("cem",)).check()


def test_resume_after_kill_identical(tmp_path):
    ref, *_ = _run(tmp_path / "ref")
    work = tmp_path / "killed"
    with pytest.raises(A.Crash):
        _run(work, crash_after=("p1", 3))
    assert len(list(work.glob("*/p1/*.pkl"))) == 3
    with pytest.raises(A.Crash):
        _run(work, crash_after=("p2", 5))
    assert len(list(work.glob("*/p2_*/*.pkl"))) == 5
    res, *_ = _run(work)
    assert _canon(res["records"]) == _canon(ref["records"])
    assert np.array_equal(res["plans"], ref["plans"])
    # a different configuration does not reuse the phase files
    res2, judge2, _, _ = _run(work, cfg={**CFG, "budgets": (1, 10)})
    assert judge2.month_steps > 0 and len(res2["records"]) == 8 * 4 * 2


def test_recover_forced_event_in_both_judges(tmp_path):
    res, judge, engine, inst = _run(tmp_path / "w")
    for who in (judge.seen, engine.seen):
        tasks_seen = {t for t, _ in who}
        assert tasks_seen == {"grow", "recover"}
        for t, col in who:
            if t == "recover":
                assert (col[:, 0] == DISASTER_EARTHQUAKE).all() and (col[:, 1:] == 0).all()
            else:
                assert (col == 0).all()
    # the plans the attackers selected keep their own forced column at 0
    assert (res["plans"][:, :, A.FORCED_COL] == 0).all()
    rec = [r for r in res["records"] if r["task"] == "recover"]
    assert rec and all((res["plans_effective"][k][0, A.FORCED_COL] == DISASTER_EARTHQUAKE)
                       for k, r in enumerate(res["records"]) if r["task"] == "recover")


def test_accepted_and_rejected_counting(tmp_path):
    inst = [i for i in _instances(starts=("sA", "sB")) if i.task == "grow"]
    cfg = dict(budgets=(1, 10), methods=("cem", "random"), search_seeds=(0,), floors=("flip",),
               pool_verdict_plans=20, residual_pool="instance")
    engine = StubEngine(fixed={"sA": False, "sB": True})   # the engine rejects every plan on sA, accepts on sB
    res, judge, engine, _ = _run(tmp_path / "w", judge=StubJudge(always_accept=True), engine=engine, cfg=cfg,
                                 instances=inst)
    for r in res["records"]:
        assert r["grader_p"] == 1.0
        assert r["oracle_accept"] == (r["start_id"] == "sB")
    for start, want in (("sA", 1.0), ("sB", 0.0)):
        keep = [i for i in inst if i.start_id == start]
        rec = [r for r in res["records"] if r["start_id"] == start]
        R, beh = A.card_tables(rec, res["p1"], keep, cfg["floors"])
        card = hd.build_card(R, {"audited": "stub", "code_version": "t", "date": "d", "revisit_date": "r"},
                             behaviour=beh)
        assert [e["hackability"]["value"] for e in card["hackability_curve"]] == [want] * 4


def test_space_and_effective():
    sp = A.plan_space(H)
    assert sp.D == H * 25
    frozen = np.flatnonzero(sp.frozen)
    assert list(frozen) == [4 + 25 * m for m in range(H)]
    assert sp.categorical.sum() == 4 * H and (sp.high[sp.categorical] == 18).all()
    X = sp.sample_uniform(np.random.default_rng(0), 50)
    assert (X[:, frozen] == 0).all()
    e = A.effective(X, "recover", H)
    assert e.dtype == np.int16 and (e[:, 0, 4] == DISASTER_EARTHQUAKE).all() and (e[:, 1:, 4] == 0).all()
    assert (A.effective(X, "power", H)[:, :, 4] == 0).all()


def test_instance_selection():
    inst = A.load_instances()
    assert len(inst) == 200
    sel = A.select_instances(inst, 40)
    assert len(sel) == 40 and len({i.start_id for i in sel}) == 40
    assert all(sum(i.task == t for i in sel) == 8 for t in T.TASKS)
    assert A.select_instances(inst, "all") == inst
    with pytest.raises(ValueError):
        A.select_instances(inst, 42)
    # a tasks file with excluded instances (fewer than 40 in some families): still 8 per family on 40 distinct starts
    v2 = A.REPO / "data" / "tasks_v2_H24.json"
    if v2.exists():
        u = A.load_instances(v2)
        sel = A.select_instances(u, 40)
        assert len(sel) == 40 and len({i.start_id for i in sel}) == 40 == len({i.family_id for i in sel})
        assert all(sum(i.task == t for i in sel) == 8 for t in T.TASKS)
        assert A.select_instances(u, len(u)) == u


def _real_start():
    inst = [i for i in A.load_instances() if i.task in ("grow", "recover")]
    sid = inst[0].start_id
    return [i for i in inst if i.start_id == sid]


@pytest.mark.skipif(not CAL.exists(), reason="calibration pool not present")
def test_engine_cache_hit_and_forced(tmp_path):
    grow, recover = _real_start()
    with np.load(CAL / f"{grow.start_id}.npz") as z:
        plans, sp, sr = z["plans"][:3], z["scal_plain"][:3], z["scal_recover"][:3]
    eng = A.EngineJudge(tmp_path / "cache", workers=0)
    seeds = [seed_for("cal-eval", grow.start_id, H, j) for j in range(3)]
    a = eng.scalars(grow, A.effective(plans, "grow", H), seeds)
    assert eng.n_replays == 3 and eng.n_cache_hits == 0
    assert np.array_equal(a, sp)                       # the calibration replays, reproduced
    b = eng.scalars(grow, A.effective(plans, "grow", H), seeds)
    assert eng.n_replays == 3 and eng.n_cache_hits == 3 and np.array_equal(a, b)
    eng.close()
    eng2 = A.EngineJudge(tmp_path / "cache", workers=0)   # a fresh judge on the same disk cache
    c = eng2.scalars(grow, A.effective(plans, "grow", H), seeds)
    assert eng2.n_replays == 0 and eng2.n_cache_hits == 3 and np.array_equal(a, c)
    # recover: the task's earthquake reaches the engine through the effective plan
    r = eng2.scalars(recover, A.effective(plans, "recover", H), seeds)
    assert eng2.n_replays == 3
    assert np.array_equal(r, sr)
    from dc.engine import Engine
    e = Engine()
    acts, forced = compile_plan(plans[0])
    assert forced == {}
    direct = replay(e, recover.cty, acts, seeds[0], forced={0: DISASTER_EARTHQUAKE}).scalars
    assert np.array_equal(r[0], direct) and not np.array_equal(r[0], a[0])
    e.close()
    eng2.close()


@pytest.mark.skipif(not CAL.exists(), reason="calibration pool not present")
def test_identity_judge_small(tmp_path):
    """The engine as its own judge (same seed): nothing is hacked; the flip floor is 0."""
    inst = _real_start()
    eng = A.EngineJudge(tmp_path / "cache", workers=0)
    cfg = dict(budgets=(1, 10), methods=("cem", "random"), search_seeds=(0,), floors=("residual", "flip"),
               pool_verdict_plans=10, residual_pool="instance", flip_scope="all")
    au = A.Audit(A.AuditConfig(**cfg), inst, A.EngineIdentityJudge(eng), eng, A.Pools(H), tmp_path / "w",
                 log=lambda s: None)
    res = au.run()
    assert res["flip_rates"]["fp"] == 0.0 and res["flip_rates"]["fn"] == 0.0
    for r in res["records"]:
        assert r["grader_p"] in (0.0, 1.0)
        assert (r["grader_p"] >= 0.5) == r["oracle_accept"]
        assert not (r["flip_grader_accept"] and not r["flip_oracle_accept"])   # fp = fn = 0
        # the residual floor need not be 0 here (residuals are against the nine-seed mean)
    # residuals are against the nine-seed mean: here both columns equal primary minus that mean
    for key, d in res["p1"].items():
        i = next(x for x in inst if x.key == key)
        m9 = au.engine_margins9(i, A.Pools(H).behaviour(i.start_id)[:10])
        want = m9[:, 0] - m9.mean(axis=1)
        assert np.allclose(d["pools"]["behaviour"][:, 0], want) and np.allclose(d["pools"]["behaviour"][:, 1], want)
    # the residual floor's outcome is the primary-seed verdict of its selected plan
    for r in res["records"]:
        assert r["residual_oracle_accept"] == (r["residual_oracle_margin"] >= 0)
        assert len(r["residual_oracle_accept_seeds"]) == 8
    eng.close()


def test_primary_seed_is_the_protocol_seed():
    i = _instances()[0]
    assert A.primary_seed(i) == seed_for("task", i.start_id, i.task, H)
    assert A.secondary_seeds(i) == [seed_for("task-secondary", i.start_id, i.task, H, k) for k in range(8)]


def test_floor_pools_follow_the_method(tmp_path):
    res, judge, engine, inst = _run(tmp_path / "w")
    for r in res["records"]:
        assert r["residual_pool_source"] == ("builders" if r["method"] == "best_of_n" else "behaviour")
        assert r["residual_oracle_accept"] == (r["residual_oracle_margin"] >= 0)
        assert len(r["residual_oracle_accept_seeds"]) == 8 and len(r["flip_oracle_accept_seeds"]) == 8
    for d in res["p1"].values():
        assert set(d["pools"]) == {"behaviour", "builders"}
        assert not np.array_equal(d["pools"]["behaviour"], d["pools"]["builders"])


def test_surrogate_judged_by_another_oracle():
    """hpr_dream change: score and accept from one oracle function, the outcome from another."""
    X = np.arange(20, dtype=np.int64).reshape(10, 2)
    basis = lambda P: P[:, 0].astype(float)                 # surrogate built on this
    judge = lambda P: -np.ones(len(P))                       # every plan rejected by the judge
    pool = np.zeros((10, 2))
    gr = hd.SurrogateGrader(hd.ResidualSurrogate(pool), hd.OracleCache(basis), np.random.default_rng(0),
                            judge_margin=judge)
    r = hd.attack_surrogate(lambda sc: hd.random_shooting(sc, X, 10), gr, budget=10)
    assert r.surrogate_accept and not r.oracle_accept and r.hacked
    assert r.oracle_margin == -1.0 and r.log["score_basis_margin"] == 18.0
    r2 = hd.attack_surrogate(lambda sc: hd.random_shooting(sc, X, 10), hd.ResidualSurrogate(pool), hd.OracleCache(basis),
                             np.random.default_rng(0), budget=10)
    assert r2.oracle_accept and r2.oracle_margin == 18.0 and "score_basis_margin" not in r2.log


def test_zero_mad_rule():
    a = np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]])       # median 2, MAD 1
    b = np.array([[5.0, 7.0], [5.0, 9.0], [5.0, 11.0]])      # column 0 MAD 0; column 1 median 9, MAD 2
    with pytest.raises(ValueError):
        hd.ResidualFamily([a, b])                             # default unchanged: refuses
    fam = hd.ResidualFamily([a, b], zero_mad="centre")
    assert list(fam.n_zero_mad) == [1, 0] and np.allclose(fam.median_nonzero_mad, [1.0, 1.5])
    ta = hd.pool_family_residuals(a, fam)
    assert np.allclose(ta[:, 0], [1, 2, 3, 2, 2, 2])          # b's column 0 centred, unscaled: 2 + 0
    assert np.allclose(ta[:, 1], [1, 2, 3, 1, 2, 3])          # b's column 1 standardised, rescaled by a's MAD 1
    tb = hd.pool_family_residuals(b, fam)                     # target column 0 has zero MAD: family median 1.0
    assert np.allclose(tb[:, 0], [4, 5, 6, 5, 5, 5])
    assert np.allclose(tb[:, 1], [7, 9, 11, 7, 9, 11])
    d = hd.ResidualSurrogate(b, family_pools=fam).describe()
    assert d["residual_zero_mad_instances"] == [1, 0] and d["residual_target_zero_mad"] == [True, False]


@pytest.mark.skipif(not CAL.exists(), reason="calibration pool not present")
def test_remote_pool_protocol(tmp_path):
    """The replay server over a pipe (as over ssh): identical replays, start files checked."""
    import os
    grow = _real_start()[0]
    with np.load(CAL / f"{grow.start_id}.npz") as z:
        plans = A.effective(z["plans"][:6], "grow", H)
    seeds = [seed_for("t", j) for j in range(6)]
    cmd = ["env", f"PYTHONPATH={A.REPO / 'code'}", sys.executable, "-m", "dc.audit", "serve", "--workers", "2"]
    remote = A.RemotePool(cmd, 2)
    eng = A.EngineJudge(tmp_path / "c1", workers=1, remote=remote)
    a = eng.scalars(grow, plans, seeds)
    assert eng.n_remote > 0 and eng.n_replays == 6
    eng.close()
    ref = A.EngineJudge(tmp_path / "c2", workers=0)
    assert np.array_equal(a, ref.scalars(grow, plans, seeds))
    ref.close()


def test_economy_impute_nearest_and_ties():
    # search residuals of rows 0..5; top=2 keeps rows 4 (0.9) and 5 (0.7); n_random=1 draws one of the rest
    pool = np.array([[0.1, 10.0], [0.3, 11.0], [0.5, 12.0], [0.3, 13.0], [0.9, 14.0], [0.7, 15.0]])
    imp, keep = A.economy_impute(pool, 2, 1, np.random.default_rng(0))
    assert keep[4] and keep[5] and keep.sum() == 3
    kept = np.flatnonzero(keep)
    for i in range(6):
        if keep[i]:
            assert imp[i, 1] == pool[i, 1]
        else:
            d = np.abs(pool[kept, 0] - pool[i, 0])
            assert imp[i, 1] == pool[kept[np.flatnonzero(d == d.min())[0]], 1]   # nearest, lowest index on ties
    assert (imp[:, 0] == pool[:, 0]).all()
    # exact ties (binary-exact values): kept rows 0 and 2 both at 0.5; rows 1 and 3 are equidistant from both,
    # so the kept row with the lower index (row 0) supplies their verdict residual
    p2 = np.array([[0.5, 1.0], [0.25, 2.0], [0.5, 3.0], [0.0, 4.0]])
    imp2, keep2 = A.economy_impute(p2, 2, 0, np.random.default_rng(0))
    assert list(np.flatnonzero(keep2)) == [0, 2] and imp2[1, 1] == 1.0 and imp2[3, 1] == 1.0


def test_shrunk_log_mads():
    rng = np.random.default_rng(1)
    same = [rng.normal(size=(400, 2)) for _ in range(6)]
    sh = A.shrunk_log_mads(same, [np.random.default_rng(k) for k in range(6)])
    # equal true scales: tau2 small against the sampling variance, MADs pulled toward the family mean
    assert all(t < v for t, v in zip(sh["tau2"], sh["v_mean"]))
    raw_sd = np.log(sh["mads"]).std(axis=0)
    assert (np.log(sh["shrunk_mads"]).std(axis=0) < 0.5 * raw_sd).all()
    spread = [rng.normal(size=(400, 2)) * s for s in (0.2, 0.5, 1, 2, 5, 10)]
    sh2 = A.shrunk_log_mads(spread, [np.random.default_rng(k) for k in range(6)])
    # very different true scales and small sampling variance: weights near 1, MADs nearly unchanged
    assert all(w > 0.9 for w in sh2["w_mean"])
    assert np.allclose(sh2["shrunk_mads"], sh2["mads"], rtol=0.1)
    # a zero-MAD pool keeps MAD 0
    z = [np.zeros((50, 2)), rng.normal(size=(50, 2)), rng.normal(size=(50, 2))]
    sh3 = A.shrunk_log_mads(z, [np.random.default_rng(k) for k in range(3)])
    assert (sh3["shrunk_mads"][0] == 0).all() and (sh3["shrunk_mads"][1:] > 0).all()


def test_family_centred_and_shrunk_rules():
    a = np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]])
    b = np.array([[10.0, 10.0], [20.0, 20.0], [30.0, 30.0]])
    cfg = A.AuditConfig(residual_pool="family-centred", pool_verdict_plans=3, budgets=(1,), methods=("random",))
    (sa, sb), _ = A.residual_pool_rule(cfg, [a, b], "grow", "behaviour", ["a", "b"])
    assert np.allclose(sa.effective_pool[:, 0], [1, 2, 3, -8, 2, 12])     # med 2 + (r - own median), unscaled
    assert sa.describe()["residual_pool_kind"] == "family-centred"
    cfg2 = A.AuditConfig(residual_pool="family-shrunk", pool_verdict_plans=3, budgets=(1,), methods=("random",))
    (ta, tb), note = A.residual_pool_rule(cfg2, [a, b], "grow", "behaviour", ["a", "b"])
    assert ta.pool_size == 6 and "tau2" in note
    m = np.median(ta.effective_pool[:, 0])
    assert m == 2.0                                                        # the target's median is kept


def test_rules_share_phase1_and_family_flip_rates(tmp_path):
    work = tmp_path / "w"
    cfg = {**CFG, "pool_verdict_plans": 100}
    res1, judge1, _, inst = _run(work, cfg={**cfg, "residual_pool": "instance"})
    res2, judge2, _, _ = _run(work, cfg={**cfg, "residual_pool": "economy", "economy_top": 20, "economy_random": 5})
    assert judge1.month_steps > 0 and judge2.month_steps == 0            # phase 1 reused, phase 2 per rule
    assert len(list(work.glob("*/p2_instance-*/*.pkl"))) == len(inst) == len(list(work.glob("*/p2_economy-*/*.pkl")))
    assert _canon([{k: r[k] for k in ("plan_id", "grader_p", "oracle_accept")} for r in res1["records"]]) == \
        _canon([{k: r[k] for k in ("plan_id", "grader_p", "oracle_accept")} for r in res2["records"]])
    fr = res2["flip_rates"]
    assert fr["mode"] == "family" and set(fr["by_task"]) == {"grow", "recover"}
    g = np.concatenate([res2["p1"][i.key]["behaviour"]["grader_p"] for i in inst if i.task == "grow"]) >= 0.5
    o = np.concatenate([res2["p1"][i.key]["behaviour"]["oracle_margin"] for i in inst if i.task == "grow"]) >= 0
    assert fr["by_task"]["grow"]["fp"] == float((g & ~o).sum() / (~o).sum())
    for r in res2["records"]:
        assert r["residual_pool_rule"] == "economy"


def _run_audit_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_audit_mod", A.REPO / "code" / "scripts" / "run_audit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_amendment2_plan(tmp_path):
    inst = _instances()                                   # 4 starts x (grow, recover), families fam-sA..fam-sD
    cfg = A.amendment2_config(budgets=(1, 10, 100), pool_verdict_plans=120, economy_top=20, economy_random=5,
                              behaviour_plans=10, subset_n=4, bon_families=2, verdict_cap=10)
    judge, engine = StubJudge(), StubEngine()
    au = A.Audit(cfg, inst, judge, engine, _pools(sorted({i.start_id for i in inst}), n=150), tmp_path / "w",
                 log=lambda s: None, universe=inst)
    res = au.run()
    sub = au._subset
    assert len(sub) == 4 and sum(i.task == "grow" for i in inst if i.key in sub) == 2
    for r in res["records"]:
        i = next(x for x in inst if x.key == r["instance"])
        assert r["n_scored"] == r["budget"]
        if r["method"] == "best_of_n":
            assert i.family_id in ("fam-sA", "fam-sB")
        if r["method"] == "random_verdict" and r["budget"] == 100:
            assert i.key in sub
        assert ("residualA_grader_accept" in r) == (i.key in sub)
        assert r["residual_pool_kind"] == "economy"
    got = {(r["instance"], r["method"]) for r in res["records"]}
    for i in inst:
        assert (i.key, "best_of_n") in got if i.family_id in ("fam-sA", "fam-sB") else (i.key, "best_of_n") not in got
        assert (i.key, "cem") in got and (i.key, "random") in got
    # verdicts only where needed: cross-checked instances have every pool row, the others the prefix + kept rows
    for i in inst:
        pool = res["p1"][i.key]["pools"]["behaviour"]
        n_v = int(np.isfinite(pool[:, 1]).sum())
        if i.key in sub:
            assert n_v == 120
        else:
            assert n_v <= au._verd_prefix(i, "behaviour") + 25 and n_v < 120
    # the plan's design count equals the judge's own counter
    ra = _run_audit_module()
    extra = {k: {**d["extra_verdict_rows"], "selected": d["selected_verdict_rollouts"]} for k, d in res["p1"].items()}
    assert ra.plan_design(au, extra)["total"] == judge.month_steps


def _rand_traj(rng, shape):
    t = np.zeros(shape + (H + 1, 20))
    t[..., :, SC_FUNDS] = rng.integers(-2000, 30000, size=shape + (H + 1,))
    t[..., :, SC_POP] = rng.integers(0, 40000, size=shape + (H + 1,))
    from dc.engine import SC_COAL, SC_NUCLEAR, SC_POWERED, SC_UNPOWERED
    for c, hi in ((SC_POWERED, 300), (SC_UNPOWERED, 40), (SC_COAL, 4), (SC_NUCLEAR, 2)):
        t[..., :, c] = rng.integers(0, hi, size=shape + (H + 1,))
    return t


def test_stats_margins_equal_full_trajectories_and_guard(monkeypatch):
    rng = np.random.default_rng(3)
    full = _rand_traj(rng, (50, 3))
    st = A.traj_stats(full)
    assert st.shape == (50, 3, len(A.STAT_FIELDS))
    for i in _instances(tasks=T.TASKS):
        assert np.array_equal(A.task_margin(i, full), A.stats_margin(i, st))
    # real engine trajectories of the calibration pool, every task of one start
    if CAL.exists():
        insts = [i for i in A.load_instances() if i.start_id == A.load_instances()[0].start_id]
        with np.load(CAL / f"{insts[0].start_id}.npz") as z:
            plain, rec = z["scal_plain"][:200], z["scal_recover"][:200]
        for i in insts:
            sc = rec if i.task == "recover" else plain
            assert np.array_equal(A.task_margin(i, sc), A.stats_margin(i, A.traj_stats(sc)))
    # a predicate reading a quantity the store does not hold is refused, not silently wrong
    from dc.engine import SC_SCORE
    orig = T.margin
    monkeypatch.setattr(T, "margin", lambda task, s, th, sd: orig(task, s, th, sd) + 0 * np.asarray(s)[..., -1, SC_SCORE])
    with pytest.raises(ValueError):
        A.stats_margin(_instances()[0], st)


def test_rescore_rolls_out_only_new_work(tmp_path):
    from dataclasses import replace
    work = tmp_path / "w"
    inst_a = _instances()
    tags_a = dict(tasks_file="a.json", tasks_sha256="a" * 64, tasks_code_sha256="c" * 64)
    tags_b = dict(tasks_file="b.json", tasks_sha256="b" * 64, tasks_code_sha256="c" * 64)
    res_a, judge_a, _, _ = _run(work, cfg={**CFG, **tags_a}, instances=inst_a)
    inst_b = [replace(i, theta=i.theta * 1.15) for i in inst_a]          # new thresholds, same instances
    judge_b = StubJudge()
    res_b, judge_b, _, _ = _run(work, judge=judge_b, cfg={**CFG, **tags_b}, instances=inst_b)
    assert len(list(work.glob("a-*/p1/*.pkl"))) == len(inst_a) == len(list(work.glob("b-*/p1/*.pkl")))
    new_sel = sum(d["selected_verdict_rollouts"] for d in res_b["p1"].values())
    # re-score: cross-entropy search in full plus the verdicts of plans not selected before; nothing else
    assert judge_b.month_steps == (111 * 2 * len(inst_b) + new_sel * 8) * H
    assert new_sel < sum(d["selected_verdict_rollouts"] for d in res_a["p1"].values())
    # and the margins follow the new thresholds
    ra = {r["plan_id"]: r for r in res_a["records"]}
    assert any(r["grader_score"] != ra[r["plan_id"]]["grader_score"] for r in res_b["records"] if r["method"] == "random")


@pytest.mark.skipif(not CAL.exists(), reason="calibration pool not present")
def test_rescore_command(tmp_path):
    """run_audit --rescore: the finished run at another tasks file, recorded with its digest."""
    import copy
    ra = _run_audit_module()
    d = json.loads(A.TASKS_JSON.read_text())
    d2 = copy.deepcopy(d)
    for r in d2["instances"]:
        r["theta"] = r["theta"] * 1.1
    ta, tb = tmp_path / "tasks_a.json", tmp_path / "tasks_b.json"
    ta.write_text(json.dumps(d))
    tb.write_text(json.dumps(d2))
    common = ["--judge", "engine-identity", "--instances", "5", "--budgets", "1,10", "--methods", "random,cem",
              "--floors", "flip", "--pool-verdict-plans", "10", "--residual-pool", "instance", "--workers", "0",
              "--engine-cache", str(tmp_path / "cache"), "--work", str(tmp_path / "w")]
    assert ra.main(common + ["--tasks", str(ta), "--out", str(tmp_path / "out" / "tasks_a")]) == 0
    assert ra.main(["--rescore", str(tmp_path / "out" / "tasks_a"), "--tasks", str(tb)]) == 0
    ca = json.loads((tmp_path / "out" / "tasks_a" / "config.json").read_text())["config"]
    cb = json.loads((tmp_path / "out" / "tasks_b" / "config.json").read_text())["config"]
    assert ca["tasks_sha256"] != cb["tasks_sha256"] and cb["tasks_file"] == str(tb)
    assert (tmp_path / "out" / "tasks_b" / "records.jsonl.gz").exists()


# ----------------------------------------------------------------------------------------------
# The majority oracle (study protocol)
# ----------------------------------------------------------------------------------------------
N_OR = T.ORACLE_N


class SeedRecordingEngine(StubEngine):
    """StubEngine that also records every seed it was asked for."""

    def __init__(self, fixed=None):
        super().__init__(fixed)
        self.seeds = []

    def scalars(self, inst, eff, seeds, key_sink=None, store=True):
        P = np.asarray(eff).reshape(-1, H, 25)
        self.seeds.append((inst.key, np.broadcast_to(np.asarray(seeds, dtype=np.int64), (P.shape[0],)).copy()))
        return super().scalars(inst, eff, seeds, key_sink, store)


def _maj(cfg=None):
    return {**(cfg or CFG), "oracle": "majority", "oracle_seeds": N_OR}


def test_old_configurations_keep_their_digests():
    """Without the majority oracle and with the flip floor everywhere (what every earlier run did), a configuration's
    digests are the ones it had before those fields existed, so phase files of earlier runs stay valid (values
    recorded from the code at commit 2205cf5). The default flip scope ("verdict") is a different configuration."""
    assert A.AuditConfig(**CFG).digest() == "99af3bb801932721" and A.AuditConfig(**CFG).digest_p1() == "6c47a4588dbbf318"
    a2 = A.amendment2_config(budgets=(1, 10, 100), pool_verdict_plans=120, economy_top=20, economy_random=5,
                             behaviour_plans=10, subset_n=4, bon_families=2, verdict_cap=10, flip_scope="all")
    assert a2.digest() == "8367dae11940f070" and a2.digest_p1() == "ee854477a1d78020"
    v = A.AuditConfig(**{**CFG, "flip_scope": "verdict"})
    assert v.digest() != A.AuditConfig(**CFG).digest() and v.digest_p1() == A.AuditConfig(**CFG).digest_p1()
    assert A.AuditConfig().flip_scope == "verdict" and "flip_scope" not in A.AuditConfig(**CFG).to_dict()
    with pytest.raises(ValueError):
        A.AuditConfig(**{**CFG, "flip_scope": "margin"}).check()
    m = A.AuditConfig(**_maj())
    assert m.digest() != A.AuditConfig(**CFG).digest() and m.digest_p1() != A.AuditConfig(**CFG).digest_p1()
    with pytest.raises(ValueError):
        A.AuditConfig(**{**CFG, "oracle": "majority"}).check()          # majority without a seed count
    with pytest.raises(ValueError):
        A.AuditConfig(**{**CFG, "oracle": "mean"}).check()


def test_oracle_spec_seeds_and_reserved(tmp_path):
    d = json.loads(A.TASKS_JSON.read_text())
    p = tmp_path / "t.json"
    p.write_text(json.dumps(d))
    assert A.oracle_spec(p) is None
    for o, ok in (({"rule": "majority", "n_seeds": 32, "seed_name": "task-oracle"}, True),
                  ({"rule": "majority", "n_seeds": 32, "seed_name": "other"}, False),
                  ({"rule": "mean", "n_seeds": 32, "seed_name": "task-oracle"}, False),
                  ({"rule": "majority", "n_seeds": 0, "seed_name": "task-oracle"}, False)):
        p.write_text(json.dumps({**d, "meta": {**d["meta"], "oracle": o}}))
        if ok:
            assert A.oracle_spec(p) == {"rule": "majority", "n_seeds": 32, "seed_name": "task-oracle", "pass_share": 0.5}
        else:
            with pytest.raises(ValueError):
                A.oracle_spec(p)
    # every held-out instance: 32 distinct oracle seeds, none of them a residual seed (primary or secondary)
    for i in A.load_instances():
        A.check_oracle_seeds(i, N_OR)
        assert A.oracle_seed_list(i) == T.oracle_seeds(i.start_id, i.task, H)
    i = _instances()[0]
    res = A.reserved_seeds(i.start_id, H, N_OR)
    for t in T.TASKS:
        j = A.Instance(f"{i.start_id}|{t}|H{H}", i.start_id, i.family_id, t, H, 1.0, 1.0, True, i.cty)
        assert set(A.verdict_seeds(j)) | set(A.oracle_seed_list(j)) <= res
    assert len(res) == 5 * (9 + N_OR)
    keys = ("audit-seedcheck", "sA", "prop", "plain", 0, 3, 1)
    s0, r0 = A.fresh_seed(keys, res)
    assert (s0, r0) == (seed_for(*keys), 0)
    s1, r1 = A.fresh_seed(keys, res | {s0})
    assert r1 >= 1 and s1 != s0 and s1 not in res and s1 == seed_for(*keys, "redraw", r1)


def test_majority_margin_is_the_oracle_verdict():
    rng = np.random.default_rng(5)
    for task in T.TASKS:
        tr = _rand_traj(rng, (40, N_OR))
        i = A.Instance(f"x|{task}|H{H}", "x", "f", task, H, float(np.median(T.statistic(task, tr))),
                       float(np.std(T.statistic(task, tr))) or 1.0, True, "")
        oj = A.oracle_judgement(i, tr)
        assert np.array_equal(oj["accept"], T.oracle_verdict(task, tr, i.theta))
        assert np.array_equal(oj["accept"], oj["margin"] >= 0) and np.array_equal(oj["share"], oj["accept_seeds"].mean(1))
        assert np.array_equal(oj["accept_seed0"], T.verdict(task, tr[:, 0], i.theta))


def test_majority_mode_records_floors_and_tables(tmp_path):
    engine = SeedRecordingEngine()
    res, judge, engine, inst = _run(tmp_path / "w", engine=engine, cfg=_maj())
    by = {i.key: i for i in inst}
    probe = StubEngine()
    for k, r in enumerate(res["records"]):
        i = by[r["instance"]]
        assert r["oracle_rule"] == "majority" and r["oracle_n_seeds"] == N_OR
        assert len(r["oracle_margins_seeds"]) == N_OR == len(r["oracle_accept_seeds"])
        assert r["oracle_share"] == np.mean(r["oracle_accept_seeds"])
        assert r["oracle_accept"] == (r["oracle_share"] >= 0.5) == (r["oracle_margin"] >= 0)
        assert r["oracle_accept_seed0"] == r["oracle_accept_seeds"][0] == (r["oracle_margin_seed0"] >= 0)
        assert len(r["nine_seed_margins"]) == 9 and "oracle_margin_mean9" not in r
        # the record's per-seed margins are the plan replayed on the instance's oracle seeds
        tr = probe.scalars(i, np.repeat(res["plans_effective"][k][None], N_OR, axis=0), A.oracle_seed_list(i))
        assert np.allclose(A.task_margin(i, tr), r["oracle_margins_seeds"])
        assert r["engine_city_months_judge"] == (9 + N_OR) * H
        for f in ("residual", "flip"):        # the floors' selected plans are judged by the majority oracle too
            assert r[f"{f}_oracle_accept"] == (r[f"{f}_oracle_share"] >= 0.5) == (r[f"{f}_oracle_margin"] >= 0)
            assert len(r[f"{f}_oracle_accept_seeds"]) == N_OR
    # the same audit under the primary-seed oracle: identical searches, residual pools (against the nine residual
    # seeds) and surrogate selections; only the judging of selected plans and the behaviour table change
    res0, *_ = _run(tmp_path / "w0")
    assert all("oracle_rule" not in r and len(r["oracle_accept_seeds"]) == 8 for r in res0["records"])
    assert np.array_equal(res0["plans"], res["plans"])
    for key in res["p1"]:
        for kind in ("behaviour", "builders"):
            assert np.array_equal(res0["p1"][key]["pools"][kind], res["p1"][key]["pools"][kind])
    for r0, r in zip(res0["records"], res["records"]):
        assert r0["plan_id"] == r["plan_id"] and r0["grader_p"] == r["grader_p"]
        assert r0["residual_score"] == r["residual_score"] and r0["residual_grader_accept"] == r["residual_grader_accept"]
        assert np.isclose(r0["oracle_margin_mean9"], r["nine_seed_mean"])
    pools = _pools(sorted({i.start_id for i in inst}))
    au = A.Audit(A.AuditConfig(**_maj()), inst, StubJudge(), StubEngine(), pools, tmp_path / "w2", log=lambda s: None)
    for key, d in res["p1"].items():
        oj = au.oracle_judge(by[key], pools.behaviour(by[key].start_id)[:30])
        assert np.array_equal(d["behaviour"]["oracle_margin"], oj["margin"])
        assert np.array_equal(d["behaviour"]["oracle_share"], oj["share"])
    # which seeds the engine replayed: every request is either nine residual seeds or the oracle's seeds
    for key, sd in engine.seeds:
        i = by[key]
        nine, orc = set(A.verdict_seeds(i)), set(A.oracle_seed_list(i))
        assert set(sd.tolist()) <= nine or set(sd.tolist()) <= orc
    fr = res["flip_rates"]
    assert "majority" in fr["verdicts"]
    g = np.concatenate([res["p1"][i.key]["behaviour"]["grader_p"] for i in inst if i.task == "grow"]) >= 0.5
    o = np.concatenate([res["p1"][i.key]["behaviour"]["oracle_share"] for i in inst if i.task == "grow"]) >= 0.5
    assert fr["by_task"]["grow"]["fp"] == float((g & ~o).sum() / (~o).sum())
    # card and tables: no "unlucky" share under the majority rule; the oracle statistics beside the card
    R, beh = A.card_tables(res["records"], res["p1"], inst, ("residual", "flip"))
    assert "oracle_accept_seeds" not in R
    card = hd.build_card(R, {"audited": "stub", "code_version": "t", "date": "d", "revisit_date": "r"}, behaviour=beh)
    assert card["unlucky_share"] == {"status": "not supplied"}
    ra = _run_audit_module()
    os_ = ra.oracle_majority_stats(res["records"], n_boot=200)
    for e in os_:
        rs = [r for r in res["records"] if (r["attacker"], r["scoring"], r["budget"]) == (e["attacker"], e["scoring"], e["budget"])]
        ga = np.array([r["grader_p"] >= 0.5 for r in rs])
        sh = np.array([r["oracle_share"] for r in rs])
        assert np.isclose(e["emulator_share_minus_oracle_share"]["value"], np.mean([r["grader_p"] for r in rs]) - sh.mean())
        if ga.any():
            assert np.isclose(e["oracle_share_given_emulator_accept"]["value"], sh[ga].mean())
        assert np.isclose(e["single_seed_hackability"]["value"],
                          np.mean([r["grader_p"] >= 0.5 and not r["oracle_accept_seed0"] for r in rs]))
    txt = ra.table_majority(card, res["records"], ("residual", "flip"), os_)
    assert "single-seed oracle" in txt and len(txt.splitlines()) == 2 * len(card["hackability_curve"]) + 3


def test_identity_judge_majority_stub(tmp_path):
    """The oracle judging itself under the majority rule: nothing is hacked, the flip floor is 0."""
    eng = StubEngine()
    judge = A.EngineIdentityJudge(eng, oracle_n=N_OR, tasks_sha256="t" * 64)
    res, *_ = _run(tmp_path / "w", judge=judge, engine=eng, cfg=_maj())
    assert res["flip_rates"]["fp"] == 0.0 and res["flip_rates"]["fn"] == 0.0
    for r in res["records"]:
        assert (r["grader_p"] >= 0.5) == r["oracle_accept"]
        assert r["grader_p"] in (0.0, 1.0)
        assert all(m == r["oracle_margin"] for m in r["grader_margins_fresh"])      # the judge's margin is the oracle's
        assert not (r["flip_grader_accept"] and not r["flip_oracle_accept"])
    assert "tasks_sha256" in judge.describe() and judge.describe()["oracle"]["n_seeds"] == N_OR
    with pytest.raises(ValueError):                         # an identity judge of the other oracle is refused
        A.Audit(A.AuditConfig(**CFG), _instances(), judge, eng, _pools(["sA", "sB", "sC", "sD"]), tmp_path / "x",
                log=lambda s: None)
    with pytest.raises(ValueError):
        A.EngineIdentityJudge(eng, oracle_n=N_OR)            # theta-dependent samples need the tasks digest


def test_seed_judge_majority_avoids_reserved(tmp_path, monkeypatch):
    eng = SeedRecordingEngine()
    inst = _instances()[0]
    P = A.effective(_pools([inst.start_id]).behaviour(inst.start_id)[:20], inst.task, H)
    j = A.EngineSeedJudge(eng, oracle_n=N_OR)
    j.samples(inst, P, 8, ("verd", "plain", 0))
    seen = set(eng.seeds[-1][1].tolist())
    assert len(seen) == 160 and not seen & A.reserved_seeds(inst.start_id, H, N_OR) and j.n_redraws == 0
    # a natural draw that is reserved is redrawn, and only that one
    natural = seed_for("audit-seedcheck", inst.start_id, "verd", "plain", 0, 0, 0)
    real = A.reserved_seeds
    monkeypatch.setattr(A, "reserved_seeds", lambda *a, **k: real(*a, **k) | {natural})
    j2 = A.EngineSeedJudge(eng, oracle_n=N_OR)
    j2.samples(inst, P, 8, ("verd", "plain", 0))
    s2 = eng.seeds[-1][1]
    assert j2.n_redraws == 1 and natural not in set(s2.tolist())
    assert (s2[1:] == eng.seeds[-2][1][1:]).all()
    assert "seeds_avoid" in j2.describe() and "seeds_avoid" not in A.EngineSeedJudge(eng).describe()
    assert j2.counters()["judge_seed_redraws"] == 1


@pytest.mark.skipif(not CAL.exists(), reason="calibration pool not present")
def test_oracle_trajectories_real_engine(tmp_path):
    """The RL arm's function: per-seed trajectories on the oracle seeds through the cached judge."""
    grow, recover = _real_start()
    plans = A.Pools(H).behaviour(grow.start_id)[:2]
    eng = A.EngineJudge(tmp_path / "cache", workers=2)
    tr = A.oracle_trajectories(eng, recover, plans)
    assert tr.shape == (2, N_OR, H + 1, 20) and tr.dtype == np.int64 and eng.n_replays == 2 * N_OR
    from dc.engine import Engine
    e = Engine()
    acts, forced = compile_plan(A.effective(plans, "recover", H)[1])
    direct = replay(e, recover.cty, acts, A.oracle_seed_list(recover)[5], forced=forced).scalars
    assert np.array_equal(tr[1, 5], direct) and forced == {0: DISASTER_EARTHQUAKE}
    e.close()
    again = A.oracle_trajectories(eng, recover, A.effective(plans, "recover", H))     # effective plans: same, cached
    assert np.array_equal(again, tr) and eng.n_replays == 2 * N_OR
    oj = A.oracle_judgement(recover, tr)
    assert np.array_equal(oj["accept"], T.oracle_verdict("recover", tr, recover.theta))
    eng.close()


@pytest.mark.skipif(not CAL.exists(), reason="calibration pool not present")
def test_identity_judge_majority_real_small(tmp_path):
    """The real engine judging itself under the majority oracle: hackability and the flip floor exactly 0."""
    grow = _real_start()[0]
    eng = A.EngineJudge(tmp_path / "cache", workers=4)
    cfg = dict(budgets=(1, 10), methods=("cem", "random"), search_seeds=(0,), floors=("residual", "flip"),
               pool_verdict_plans=10, residual_pool="instance", oracle="majority", oracle_seeds=N_OR, flip_scope="all")
    au = A.Audit(A.AuditConfig(**cfg), [grow], A.EngineIdentityJudge(eng, oracle_n=N_OR, tasks_sha256="t" * 64), eng,
                 A.Pools(H), tmp_path / "w", log=lambda s: None)
    res = au.run()
    assert res["flip_rates"]["fp"] == 0.0 and res["flip_rates"]["fn"] == 0.0
    for k, r in enumerate(res["records"]):
        assert (r["grader_p"] >= 0.5) == r["oracle_accept"]
        assert not (r["flip_grader_accept"] and not r["flip_oracle_accept"])
        tr = A.oracle_trajectories(eng, grow, res["plans_effective"][k][None])
        assert r["oracle_accept"] == bool(T.oracle_verdict("grow", tr, grow.theta)[0])
        assert r["oracle_share"] == float(T.oracle_share("grow", tr, grow.theta)[0])
    eng.close()


def test_flip_scope_verdict(tmp_path):
    """Default flip scope: the flip floor's attack runs for random shooting at the budgets of verdict-scored search
    and is reported on verdict-scored records only, identical there to the scope-"all" run; the residual floors and
    the real attacks do not change; verdict-scored records then carry their flip floor's engine replays."""
    res_v, *_ = _run(tmp_path / "v", cfg={**CFG, "flip_scope": "verdict"})
    res_a, _, _, inst = _run(tmp_path / "a", cfg=CFG)
    for rv, ra in zip(res_v["records"], res_a["records"]):
        assert rv["plan_id"] == ra["plan_id"] and rv["residual_score"] == ra["residual_score"]
        assert rv["residual_oracle_accept"] == ra["residual_oracle_accept"]
        if rv["scoring"] == "verdict":
            for k in ("flip_grader_accept", "flip_oracle_accept", "flip_score", "flip_oracle_margin"):
                assert rv[k] == ra[k]
            assert rv["n_floor_oracle_evals"] == rv["flip_engine_replays"] and ra["n_floor_oracle_evals"] == 0
        else:
            assert "flip_grader_accept" not in rv
            assert rv["n_floor_oracle_evals"] == rv["residual_engine_replays"] or rv["method"] != "random"
    for d in res_v["p2"].values():
        assert {(m, B) for (m, B, s, k) in d["floors"] if k == "flip"} == {("random", B) for B in CFG["budgets"]}
    R, beh = A.card_tables(res_v["records"], res_v["p1"], inst, ("residual", "flip"))
    card = hd.build_card(R, {"audited": "stub", "code_version": "t", "date": "d", "revisit_date": "r"}, behaviour=beh)
    for f in card["noise_floors"]:
        if f["scoring"] == "margin":
            assert f["flip_surrogate"]["status"] == "not run for this group" and "excess" in f["residual_surrogate"]
        else:
            assert "excess" in f["flip_surrogate"]
    # amendment 2: verdict-scored search above the cap runs on the subset only, and so does its flip floor
    cfg = A.amendment2_config(budgets=(1, 10, 100), pool_verdict_plans=120, economy_top=20, economy_random=5,
                              behaviour_plans=10, subset_n=4, bon_families=2, verdict_cap=10)
    insts = _instances(starts=("sA", "sB", "sC", "sD", "sE"))
    au = A.Audit(cfg, insts, StubJudge(), StubEngine(), _pools(sorted({i.start_id for i in insts}), n=150),
                 tmp_path / "a2", log=lambda s: None, universe=insts)
    res2 = au.run()
    for key, d in res2["p2"].items():
        want = {1, 10, 100} if key in au._subset else {1, 10}
        assert {B for (m, B, s, k) in d["floors"] if k == "flip"} == want


@pytest.mark.skipif(not CAL.exists(), reason="calibration pool not present")
def test_floor_candidates_kept_out_of_the_cache(tmp_path):
    """Replays asked with store=False stay out of the disk cache (in memory until cleared); a later request with
    store=True writes them; in an audit only pool plans of phase 2 reach the disk, and the records are the same as
    when everything is cached."""
    grow = _real_start()[0]
    plans = A.effective(A.Pools(H).behaviour(grow.start_id)[:3], "grow", H)
    eng = A.EngineJudge(tmp_path / "c", workers=0)
    a = eng.scalars(grow, plans, 7, store=np.array([True, False, False]))
    assert eng.n_replays == 3 and eng.n_put == 1 and eng.n_uncached == 2 and eng.bytes_put > 0
    b = eng.scalars(grow, plans, 7, store=False)                      # all three found (disk and memory)
    assert eng.n_replays == 3 and np.array_equal(a, b)
    eng.scalars(grow, plans[1:2], 7)                                  # store=True: the transient one is written
    assert eng.n_replays == 3 and eng.n_put == 2
    eng.clear_transient()
    eng.scalars(grow, plans, 7, store=False)                          # plan 2 was never written: replayed again
    assert eng.n_replays == 4
    eng.close()
    # an audit: the cross-entropy floor candidates are replayed but not written; identical records either way
    cfg = A.AuditConfig(budgets=(1, 10), methods=("cem", "random"), search_seeds=(0,), floors=("residual", "flip"),
                        pool_verdict_plans=10, residual_pool="instance", flip_scope="all")
    e1 = A.EngineJudge(tmp_path / "c1", workers=0)
    r1 = A.Audit(cfg, [grow], A.EngineIdentityJudge(e1), e1, A.Pools(H), tmp_path / "w1", log=lambda s: None).run()
    assert e1.n_uncached > 0 and e1.n_put == e1.n_replays - e1.n_uncached
    keep_all = A.EngineJudge(tmp_path / "c2", workers=0)
    keep_all.scalars = (lambda f: lambda *x, store=True, **k: f(*x, **k))(keep_all.scalars)   # store everything
    r2 = A.Audit(cfg, [grow], A.EngineIdentityJudge(keep_all), keep_all, A.Pools(H), tmp_path / "w2",
                 log=lambda s: None).run()
    assert keep_all.n_uncached == 0 and _canon(r1["records"]) == _canon(r2["records"])
    e1.close()
    keep_all.close()


def test_truth_seed_floor(tmp_path):
    """Floor basis "truth": phase 1 is the nine-basis run's (its files are reused); the residual pools are against the
    mean over 64 truth seeds; the surrogate selects on truth set A (pool plans) or seeds 0..15 (candidates) and accepts
    on set B plus the drawn verdict residual; the floor never asks the engine for a nine-seed replay."""
    cfg9 = {**_maj(), "residual_pool": "instance", "pool_verdict_plans": 100}
    cfgT = {**cfg9, "floor_basis": "truth"}
    assert A.AuditConfig(**cfgT).digest() != A.AuditConfig(**cfg9).digest()
    assert A.AuditConfig(**cfgT).digest_p1() == A.AuditConfig(**cfg9).digest_p1()
    with pytest.raises(ValueError):
        A.AuditConfig(**{**CFG, "floor_basis": "truth", "residual_pool": "instance"}).check()     # needs the majority
    with pytest.raises(ValueError):
        A.AuditConfig(**{**_maj(), "floor_basis": "truth"}).check()                              # family pooling
    work = tmp_path / "w"
    res9, judge9, _, inst = _run(work, cfg=cfg9)
    engT = SeedRecordingEngine()
    resT, judgeT, _, _ = _run(work, engine=engT, cfg=cfgT)
    assert judge9.month_steps > 0 and judgeT.month_steps == 0                    # phase 1 reused, nothing re-sampled
    by = {i.key: i for i in inst}
    for key, sd in engT.seeds:                                                    # only truth and oracle seeds asked
        i = by[key]
        allowed = set(A.truth_seed_list(i.start_id, i.forced_key, H)) | set(A.oracle_seed_list(i))
        assert set(sd.tolist()) <= allowed
    probe = StubEngine()

    def tmean(i, plan, ks):
        eff = A.effective(plan[None], i.task, H)
        S = A.truth_seed_list(i.start_id, i.forced_key, H)
        return float(A.task_margin(i, probe.scalars(i, np.repeat(eff, len(ks), 0), [S[k] for k in ks])).mean())

    pools = _pools(sorted({i.start_id for i in inst}))
    for r0, r in zip(res9["records"], resT["records"]):
        assert r0["plan_id"] == r["plan_id"] and r0["grader_p"] == r["grader_p"] and r0["oracle_accept"] == r["oracle_accept"]
        i = by[r["instance"]]
        assert "residual_nine_seed_mean" not in r
        assert r["residual_grader_accept"] == (r["residual_truth_accept"] + r["residual_verdict_residual_drawn"] >= 0)
    # the selected plans' truths: set B at accept time; set A (pool plans) or 0..15 (candidates) at search time
    for key, d in resT["p2"].items():
        i = by[key]
        beh = {x.tobytes() for x in pools.behaviour(i.start_id)[:100].reshape(100, -1).astype(np.int64)}
        bon = {x.tobytes() for x in pools.builders(i.start_id)[:100].reshape(100, -1).astype(np.int64)}
        for (m, B, s, k), f in d["floors"].items():
            if k != "residual":
                continue
            plan = f["plan"].astype(np.int64)
            pool_plan = plan.tobytes() in (bon if m == "best_of_n" else beh)
            assert pool_plan == (m != "cem") or m == "cem"
            assert np.isclose(f["truth_accept"], tmean(i, plan, range(32, 64)))
            assert np.isclose(f["truth_search"], tmean(i, plan, range(32) if pool_plan else range(16)))
            assert f["grader_accept"] == (f["truth_accept"] + f["verdict_residual_drawn"] >= 0)
        # pool residuals against the 64-seed truth mean: same judge scores as the nine-basis pools
        for kind in ("behaviour", "builders"):
            raw = (pools.behaviour if kind == "behaviour" else pools.builders)(i.start_id)[:100]
            S = A.truth_seed_list(i.start_id, i.forced_key, H)
            eff = A.effective(raw, i.task, H)
            t64 = A.task_margin(i, probe.scalars(i, np.repeat(eff, 64, 0), np.tile(S, 100))).reshape(100, 64).mean(1)
            nine = A.verdict_seeds(i)
            m9 = A.task_margin(i, probe.scalars(i, np.repeat(eff, 9, 0), np.tile(nine, 100))).reshape(100, 9).mean(1)
            assert np.allclose(d["truth_pools"][kind][:, 0] + t64, res9["p1"][key]["pools"][kind][:, 0] + m9)
    # the search and accept truths recorded for the floors' selections
    for r in resT["records"]:
        i = by[r["instance"]]
        assert np.isfinite(r["residual_truth_search"]) and np.isfinite(r["residual_truth_accept"])


def test_emulator_judge_tiny_v2_cpu(tmp_path):
    """EmulatorJudge end to end on CPU with a tiny untrained model of the ladder-v2 code: auto model source from
    the checkpoint's clean training commit, the model's own decoding, the ledger start state, statistics."""
    import subprocess
    import torch
    sha = subprocess.run(["git", "-C", str(A.REPO), "rev-parse", "ladder-v2^{commit}"], capture_output=True,
                         text=True).stdout.strip()
    if not sha:
        pytest.skip("tag ladder-v2 not present")
    import importlib
    pkg, _ = A.code_package("ladder-v2")
    M = importlib.import_module(pkg.__name__ + ".model")
    m = M.Emulator(M.SIZES["tiny"])
    ck = tmp_path / "tiny.pt"
    torch.save({"model_config": m.cfg.to_dict(), "model": m.state_dict(), "ema": None, "samples": 0,
                "git": {"commit": sha, "dirty_code_files": []}}, ck)
    J = A.EmulatorJudge(str(ck), device="cpu", chunk=8, buckets=(8,), compile_trunk=False, model_src="auto")
    d = J.describe()
    assert d["model_src_resolved"] == sha and d["decoding"]["overlay"] == "sample"
    assert d["decoding"]["default_decoding"] == "a" and d["decoding"]["default_decoding_matches"]
    inst = [i for i in A.load_instances() if i.task == "recover"][0]
    assert {"ledger", "terrain", "com_rate"} <= set(J.state0(inst))
    P = A.effective(A.Pools(H).behaviour(inst.start_id)[:3], inst.task, H)
    tr = J.samples(inst, P, 2, ("smoke", 0))
    assert tr.shape == (3, 2, H + 1, 20) and np.isfinite(tr).all()
    assert np.isfinite(A.stats_margin(inst, A.traj_stats(tr))).all()
    # a checkpoint trained from a dirty tree is refused under auto
    torch.save({"model_config": m.cfg.to_dict(), "model": m.state_dict(), "ema": None, "samples": 0,
                "git": {"commit": sha, "dirty_code_files": [" M code/dc/model.py"]}}, tmp_path / "dirty.pt")
    with pytest.raises(ValueError):
        A.training_commit(tmp_path / "dirty.pt")


def test_volatility_draw_floor(tmp_path):
    """--residual-draw volatility : phase 2 only (phase 1 and its digest unchanged; the plain draw keeps its
    digests); s_j = the sample sd over the 64 truth seeds; a floor-selected plan's s(y) is the sd over its search-truth
    seeds (set A for pool plans, 0..15 for candidates) and its drawn residual row is one of the k pool rows nearest in
    log(s + eps); the real attacks do not change."""
    cfgT = {**_maj(), "residual_pool": "instance", "pool_verdict_plans": 100, "floor_basis": "truth"}
    k = 20
    cfgV = {**cfgT, "residual_draw": "volatility", "residual_draw_k": k}
    assert "residual_draw" not in A.AuditConfig(**cfgT).to_dict()
    assert A.AuditConfig(**cfgV).digest() != A.AuditConfig(**cfgT).digest()
    assert A.AuditConfig(**cfgV).digest_p1() == A.AuditConfig(**cfgT).digest_p1()
    assert A.AuditConfig(**{**cfgV, "residual_draw_k": 100}).digest() != A.AuditConfig(**cfgV).digest()
    for bad in ({**_maj(), "residual_pool": "instance", "residual_draw": "volatility"},       # nine-seed basis
                {**cfgV, "residual_draw": "nearest"}, {**cfgV, "residual_draw_k": 101}, {**cfgV, "truth_cand_seeds": 1}):
        with pytest.raises(ValueError):
            A.AuditConfig(**bad).check()
    work = tmp_path / "w"
    resT, *_ = _run(work, cfg=cfgT)
    resV, judgeV, _, inst = _run(work, cfg=cfgV)
    assert judgeV.month_steps == 0                                                     # phase 1 reused
    by = {i.key: i for i in inst}
    probe = StubEngine()

    def tm(i, plan, ks):
        eff = A.effective(plan[None], i.task, H)
        S = A.truth_seed_list(i.start_id, i.forced_key, H)
        return A.task_margin(i, probe.scalars(i, np.repeat(eff, len(ks), 0), [S[q] for q in ks]))

    pools = _pools(sorted({i.start_id for i in inst}))
    n_cand = 0
    for key, d in resV["p2"].items():
        i = by[key]
        for kind, sd in d["truth_pool_sd"].items():
            raw = (pools.behaviour if kind == "behaviour" else pools.builders)(i.start_id)[:100]
            want = np.array([tm(i, p, range(64)).std(ddof=1) for p in raw])
            assert np.allclose(sd, want)
            assert np.array_equal(d["truth_pools"][kind], resT["p2"][key]["truth_pools"][kind])
            assert d["residual_pools_describe"][kind]["residual_draw"] == "volatility"
        beh = {x.tobytes() for x in pools.behaviour(i.start_id)[:100].reshape(100, -1).astype(np.int64)}
        bon = {x.tobytes() for x in pools.builders(i.start_id)[:100].reshape(100, -1).astype(np.int64)}
        for (m, B, s, kd), f in d["floors"].items():
            if kd != "residual":
                continue
            plan = f["plan"].astype(np.int64)
            pool_plan = plan.tobytes() in (bon if m == "best_of_n" else beh)
            n_cand += not pool_plan
            sy = tm(i, plan, range(32) if pool_plan else range(16)).std(ddof=1)
            assert np.isclose(f["search_sd"], sy)
            kind = A.POOL_OF[m]
            nb = hd.volatility_neighbours(d["truth_pool_sd"][kind], [f["search_sd"]], k, A.VOL_EPS)[0]
            pool = d["truth_pools"][kind]
            assert np.isclose(f["score"] - f["truth_search"], pool[nb, 0]).any()
            assert f["verdict_residual_drawn"] in set(pool[nb, 1].tolist())
            assert f["grader_accept"] == (f["truth_accept"] + f["verdict_residual_drawn"] >= 0)
    assert n_cand > 0
    for r0, r in zip(resT["records"], resV["records"]):
        assert r0["plan_id"] == r["plan_id"] and r0["grader_p"] == r["grader_p"] and r0["oracle_accept"] == r["oracle_accept"]
        assert "residual_search_sd" in r and "residual_search_sd" not in r0


@pytest.mark.skipif(not CAL.exists(), reason="calibration pool not present")
def test_cache_floor_candidates_same_records(tmp_path):
    """Audit.cache_floor_candidates (run_audit --cache-floor-candidates): the floors' candidates go to the disk cache
    too (nothing is kept out), the records are the same, and a second audit of the other draw finds them there."""
    grow = _real_start()[0]
    cfg = A.AuditConfig(budgets=(1, 10), methods=("cem", "random"), search_seeds=(0,), floors=("residual", "flip"),
                        pool_verdict_plans=10, residual_pool="instance", flip_scope="all")
    e1 = A.EngineJudge(tmp_path / "c1", workers=0)
    r1 = A.Audit(cfg, [grow], A.EngineIdentityJudge(e1), e1, A.Pools(H), tmp_path / "w1", log=lambda s: None).run()
    e2 = A.EngineJudge(tmp_path / "c2", workers=0)
    au = A.Audit(cfg, [grow], A.EngineIdentityJudge(e2), e2, A.Pools(H), tmp_path / "w2", log=lambda s: None)
    au.cache_floor_candidates = True
    r2 = au.run()
    assert e1.n_uncached > 0 and e2.n_uncached == 0 and _canon(r1["records"]) == _canon(r2["records"])
    e3 = A.EngineJudge(tmp_path / "c2", workers=0)          # the same cache: phase 2 again replays nothing
    A.Audit(cfg, [grow], A.EngineIdentityJudge(e3), e3, A.Pools(H), tmp_path / "w3", log=lambda s: None).run()
    assert e3.n_replays == 0
    for e in (e1, e2, e3):
        e.close()


def test_cem_seeded_in_the_audit(tmp_path):
    """The seeded cross-entropy search as an audit method: its first generation is the first N behaviour proposals with
    random search's K = 2 scores (no new judge samples), so at B = 1 it selects random search's plan; later generations
    are new judge samples ((B - N) x 2 x H month-steps, the judge's counter agrees); its floors run the same search
    against the surrogates on the behaviour pool; floors of every budget score exactly B plans."""
    cfg = {**_maj(), "methods": ("random", "cem_seeded"), "residual_pool": "instance", "pool_verdict_plans": 100,
           "floor_basis": "truth"}
    res, judge, _, inst = _run(tmp_path / "w", cfg=cfg)
    by = {(r["instance"], r["method"], r["budget"]): r for r in res["records"]}
    k = {r["plan_id"]: n for n, r in enumerate(res["records"])}
    for i in inst:
        r1, s1 = by[(i.key, "random", 1)], by[(i.key, "cem_seeded", 1)]
        assert np.array_equal(res["plans"][k[r1["plan_id"]]], res["plans"][k[s1["plan_id"]]])
        assert r1["grader_score"] == s1["grader_score"] and s1["emu_month_steps_search_new"] == 0
        au = A.Audit(A.AuditConfig(**cfg), inst, StubJudge(), StubEngine(), _pools(sorted({j.start_id for j in inst})),
                     tmp_path / "w", log=lambda s: None)
        beh = au.pools.behaviour(i.start_id)
        prop = au._smargin(i, au._shared("prop", i, 0, A.effective(beh[:100], i.task, H), A.K_SEARCH)).mean(axis=1)
        for B in (10, 100):
            r = by[(i.key, "cem_seeded", B)]
            G, N = hd.cem_schedule(B)
            assert r["best_per_generation"][0] == float(prop[:N].max()) and len(r["best_per_generation"]) == G
            assert r["grader_score"] == max(r["best_per_generation"]) and r["n_scored"] == B
            assert r["emu_month_steps_search_new"] == (B - N) * A.K_SEARCH * H
            assert r["emu_month_steps_search"] == B * A.K_SEARCH * H and r["blocks_replaced"] > 0
            assert np.array_equal(res["plans_effective"][k[r["plan_id"]]],
                                  A.effective(res["plans"][k[r["plan_id"]]][None], i.task, H)[0])
        assert i.key in res["p2"] and all(f["n_scored"] == B for (m, B, s, kd), f in res["p2"][i.key]["floors"].items())
        assert {(m, B) for (m, B, s, kd) in res["p2"][i.key]["floors"] if kd == "residual"} == \
            {(m, B) for m in ("random", "cem_seeded") for B in (1, 10, 100)}
    # the judge's counter: shared proposals and pool verdicts per (start, forced events), the seeded search's later
    # generations per instance, the selected plans' verdicts
    n_sf = len({(i.start_id, i.forced_key) for i in inst})
    shared = (100 * 2 + 100 * 8) * H
    per_inst = ((10 - 5) + (100 - 25)) * 2 * H
    sel = sum(d["selected_verdict_rollouts"] for d in res["p1"].values())
    assert judge.month_steps == shared * n_sf + per_inst * len(inst) + sel * 8 * H
    ra = _run_audit_module()
    au = A.Audit(A.AuditConfig(**cfg), inst, StubJudge(), StubEngine(), _pools(sorted({j.start_id for j in inst})),
                 tmp_path / "w", log=lambda s: None)
    d = ra.plan_design(au, {})
    assert d["components"]["seeded CEM (K=2) beyond its first generation (the shared proposals)"] == per_inst * len(inst)


def test_checkpoint_with_other_methods_needs_its_own_work_dir(tmp_path):
    """A ladder checkpoint run with another method set (e.g. cem_seeded alone) would overwrite the checkpoint's phase-1
    files in the default work directory: refused unless --work and --out are given."""
    ra = _run_audit_module()
    with pytest.raises(SystemExit, match="own --work"):
        ra.main(["--plan", "amendment2", "--checkpoint", str(tmp_path / "x.pt"), "--methods", "cem_seeded"])


def test_calibrated_draw_floor(tmp_path):
    """--residual-draw calibrated : phase 2 only (phase 1 and its digest unchanged; the plain and volatility
    draws keep their digests); m_j and s_j = the mean and sample sd over the 64 truth seeds; a floor-selected plan's
    m(y), s(y) are over its search-truth seeds (set A for pool plans, 0..15 for candidates) and its drawn residual row is
    one of the k pool rows nearest in the pool's ranks of (m, s), its own rows left out; the real attacks do not
    change."""
    cfgT = {**_maj(), "residual_pool": "instance", "pool_verdict_plans": 100, "floor_basis": "truth"}
    k = 20
    cfgC = {**cfgT, "residual_draw": "calibrated", "residual_draw_k": k}
    cfgV = {**cfgT, "residual_draw": "volatility", "residual_draw_k": k}
    dT, dV, dC = (A.AuditConfig(**c).digest() for c in (cfgT, cfgV, cfgC))
    assert len({dT, dV, dC}) == 3 and A.AuditConfig(**cfgC).digest_p1() == A.AuditConfig(**cfgT).digest_p1()
    assert A.AuditConfig(**cfgC).to_dict()["residual_draw"] == "calibrated"
    for bad in ({**_maj(), "residual_pool": "instance", "residual_draw": "calibrated"},       # nine-seed basis
                {**cfgC, "residual_draw_k": 101}, {**cfgC, "truth_cand_seeds": 1}):
        with pytest.raises(ValueError):
            A.AuditConfig(**bad).check()
    work = tmp_path / "w"
    resT, *_ = _run(work, cfg=cfgT)
    resC, judgeC, _, inst = _run(work, cfg=cfgC)
    assert judgeC.month_steps == 0                                                     # phase 1 reused
    by = {i.key: i for i in inst}
    probe = StubEngine()

    def tm(i, plan, ks):
        eff = A.effective(plan[None], i.task, H)
        S = A.truth_seed_list(i.start_id, i.forced_key, H)
        return A.task_margin(i, probe.scalars(i, np.repeat(eff, len(ks), 0), [S[q] for q in ks]))

    pools = _pools(sorted({i.start_id for i in inst}))
    n_cand = n_pool = 0
    for key, d in resC["p2"].items():
        i = by[key]
        raws = {}
        for kind in d["truth_pool_sd"]:
            raw = (pools.behaviour if kind == "behaviour" else pools.builders)(i.start_id)[:100]
            raws[kind] = raw
            t = np.stack([tm(i, p, range(64)) for p in raw])
            assert np.allclose(d["truth_pool_sd"][kind], t.std(axis=1, ddof=1))
            assert np.allclose(d["truth_pool_mean"][kind], t.mean(axis=1))
            assert np.array_equal(d["truth_pools"][kind], resT["p2"][key]["truth_pools"][kind])
            assert d["residual_pools_describe"][kind]["residual_draw"] == "calibrated"
        for (m, B, s, kd), f in d["floors"].items():
            if kd != "residual":
                continue
            kind = A.POOL_OF[m]
            plan = f["plan"].astype(np.int64)
            flat = raws[kind].reshape(100, -1).astype(np.int64)
            own = np.flatnonzero((flat == plan.reshape(1, -1)).all(axis=1))
            pool_plan = plan.tobytes() in {x.tobytes() for x in pools.behaviour(i.start_id)[:100].reshape(100, -1)
                                           .astype(np.int64)} | {x.tobytes() for x in pools.builders(i.start_id)[:100]
                                                                 .reshape(100, -1).astype(np.int64)}
            n_cand += not pool_plan
            n_pool += own.size > 0
            ts = tm(i, plan, range(32) if pool_plan else range(16))
            assert np.isclose(f["truth_search"], ts.mean()) and np.isclose(f["search_sd"], ts.std(ddof=1))
            nb = hd.calibrated_neighbours(d["truth_pool_mean"][kind], d["truth_pool_sd"][kind], [f["truth_search"]],
                                          [f["search_sd"]], k, exclude=[own])[0]
            assert not set(own.tolist()) & set(nb.tolist())
            pool = d["truth_pools"][kind]
            assert np.isclose(f["score"] - f["truth_search"], pool[nb, 0]).any()
            assert f["verdict_residual_drawn"] in set(pool[nb, 1].tolist())
            assert f["grader_accept"] == (f["truth_accept"] + f["verdict_residual_drawn"] >= 0)
    assert n_cand > 0 and n_pool > 0
    for r0, r in zip(resT["records"], resC["records"]):
        assert r0["plan_id"] == r["plan_id"] and r0["grader_p"] == r["grader_p"] and r0["oracle_accept"] == r["oracle_accept"]
        assert "residual_search_sd" in r and "residual_search_sd" not in r0


def test_own_pool_rows_finds_every_copy():
    """The rows the calibrated draw leaves out for a candidate: every row among the first n of the pool holding the
    same plan (a pool may hold one plan many times), none for a plan outside them."""
    rng = np.random.default_rng(3)
    raw = np.stack([random_plan(rng, H, p_noop_macro=0.5) for _ in range(12)])
    raw[7] = raw[2]
    raw[11] = raw[2]                                       # row 11 lies beyond n = 10
    look = A.own_pool_rows(raw, 10)
    flat = raw.reshape(12, -1).astype(np.int64)
    got = look(flat[[2, 7, 3, 11]])
    assert [g.tolist() for g in got] == [[2, 7], [2, 7], [3], [2, 7]]
    other = random_plan(rng, H, p_noop_macro=0.0).reshape(1, -1).astype(np.int64)
    assert look(other)[0].size == 0


class _RefJudge(StubJudge):
    """Another stub judge (smaller noise) standing in for the perfect emulator."""

    name = "stub-ref"

    def _samples(self, inst, P, K, stream):
        rng = np.random.default_rng(seed_for("stub-ref", inst.start_id, *stream))
        return _traj(1000.0 + 2000.0 * _value(P)[:, None] + 100.0 * rng.standard_normal((P.shape[0], K)), P.shape[1])


def test_compare_reference(tmp_path):
    """run_audit --compare-reference: the run paired by instance with the perfect emulator, per method and budget, on
    every instance, per task family and on the well-posed subset; every residual floor that exists for the run (its
    _volatility sibling here) with its excess, and the same draw's floor on the reference with its excess; the numbers
    are the shares recomputed from the records; a sibling whose real attacks differ is refused, an unfinished one is
    left out."""
    ra = _run_audit_module()
    cfgT = {**_maj(), "residual_pool": "instance", "pool_verdict_plans": 100, "floor_basis": "truth"}
    cfgV = {**cfgT, "residual_draw": "volatility", "residual_draw_k": A.VOL_K}
    inst = _instances()
    out_band = {inst[1].key, inst[6].key}

    def write(d, res, cfg):
        d.mkdir(parents=True)
        recs = [{**r, "in_band": r["instance"] not in out_band} for r in res["records"]]
        A.write_records(recs, d / "records.jsonl.gz")
        (d / "config.json").write_text(json.dumps({"config": A.AuditConfig(**cfg).to_dict()}))
        return recs

    run = tmp_path / "out" / "run"
    ref = tmp_path / "out" / "ref"
    recT = write(run, _run(tmp_path / "w", cfg=cfgT)[0], cfgT)
    recV = write(tmp_path / "out" / "run_volatility", _run(tmp_path / "w", cfg=cfgV)[0], cfgV)
    refT = write(ref, _run(tmp_path / "wr", judge=_RefJudge(), cfg=cfgT)[0], cfgT)
    refV = write(tmp_path / "out" / "ref_volatility", _run(tmp_path / "wr", judge=_RefJudge(), cfg=cfgV)[0], cfgV)
    out = ra.compare_reference(run, ref, n_boot=200)
    assert (run / "reference_table.md").exists() and json.loads((run / "reference.json").read_text())["run"] == str(run)
    assert set(out["subsets"]) == {"all", "task:grow", "task:recover", "in_band"}
    assert out["floors_run"]["calibrated"].startswith("not run") and set(out["floors_run"]) == set(A.RESIDUAL_DRAWS)
    key = ra._rkey
    E, V, F, FV = ({key(r): r for r in x} for x in (recT, recV, refT, refV))

    def hk(r, floor=False):
        """Hacked: the judge (or the residual floor's surrogate) accepts, the oracle rejects."""
        if floor:
            return float(r["residual_grader_accept"] and not r["residual_oracle_accept"])
        return float(r["grader_p"] >= 0.5 and not r["oracle_accept"])
    for sname, keep in (("all", lambda r: True), ("task:grow", lambda r: r["task"] == "grow"),
                        ("in_band", lambda r: r["in_band"])):
        s = out["subsets"][sname]
        assert s["n_instances"] == len({r["instance"] for r in recT if keep(r)})
        for g in s["groups"]:
            ks = [k for k, r in E.items() if k[1] == g["method"] and k[2] == g["budget"] and keep(r)]
            assert g["n_paired"] == g["n_run"] == len(ks) > 0
            he = np.array([hk(E[k]) for k in ks])
            hr = np.array([hk(F[k]) for k in ks])
            assert np.isclose(g["emulator"]["hackability"]["value"], he.mean())
            assert np.isclose(g["perfect_emulator"]["hackability"]["value"], hr.mean())
            assert np.isclose(g["difference"]["value"], he.mean() - hr.mean())
            assert np.isclose(g["perfect_emulator"]["oracle_accept"]["value"], np.mean([F[k]["oracle_accept"] for k in ks]))
            ga = np.array([E[k]["grader_p"] >= 0.5 for k in ks])
            oa = np.array([E[k]["oracle_accept"] for k in ks])
            if oa.any():
                assert np.isclose(g["emulator"]["false_rejection"]["value"], np.mean(~ga[oa]))
            if ga.any():
                assert np.isclose(g["emulator"]["oracle_reject_given_judge_accept"]["value"], np.mean(~oa[ga]))
            for draw, (RR, FF) in (("plain", (E, F)), ("volatility", (V, FV))):
                f = g["floors"][draw]
                fe = np.array([hk(RR[k], floor=True) for k in ks])
                fr = np.array([hk(FF[k], floor=True) for k in ks])
                assert np.isclose(f["floor"]["value"], fe.mean()) and np.isclose(f["excess"]["value"], he.mean() - fe.mean())
                assert np.isclose(f["perfect_floor"]["value"], fr.mean())
                assert np.isclose(f["perfect_excess"]["value"], hr.mean() - fr.mean())
            assert "calibrated" not in g["floors"]
    md = (run / "reference_table.md").read_text()
    assert "## every instance" in md and "excess over volatility" in md and "perfect excess over plain" in md
    # an unfinished sibling (fewer records) is left out; one whose real attacks differ is refused
    A.write_records(recV[:-3], tmp_path / "out" / "run_volatility" / "records.jsonl.gz")
    out2 = ra.compare_reference(run, ref, n_boot=50)
    assert out2["floors_run"]["volatility"].startswith("not used") and "volatility" not in out2["subsets"]["all"]["groups"][0]["floors"]
    bad = [dict(r) for r in recV]
    bad[0]["grader_p"] = 1.0 - bad[0]["grader_p"] + 0.125
    A.write_records(bad, tmp_path / "out" / "run_volatility" / "records.jsonl.gz")
    with pytest.raises(SystemExit, match="real attacks differ"):
        ra.compare_reference(run, ref, n_boot=50)
    A.write_records(recV, tmp_path / "out" / "run_volatility" / "records.jsonl.gz")
    assert ra.main(["--compare-reference", str(tmp_path / "out" / "run_volatility"), "--reference", str(ref)]) == 0
    assert (tmp_path / "out" / "run_volatility" / "reference.json").exists()
    assert ra._draw_dirs(tmp_path / "out" / "run_volatility")["plain"] == run
