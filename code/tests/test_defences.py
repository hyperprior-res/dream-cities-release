"""Tests of the ensemble judge and the defence frontier . CPU only: a tiny untrained model of the
ladder-v2 code for the judges, stub judges and a stub engine for the pipeline."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hpr-dream"))

import hpr_dream as hd  # noqa: E402
from dc import audit as A  # noqa: E402
from dc import defences as D  # noqa: E402
from dc import tasks as T  # noqa: E402
from dc.engine import SC_FUNDS, SC_POP  # noqa: E402
from dc.grammar import random_plan  # noqa: E402
from dc.seeds import seed_for  # noqa: E402

H = 24


# ----------------------------------------------------------------------------------------------
# A tiny model of the ladder-v2 code
# ----------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    import importlib
    import subprocess
    import torch
    sha = subprocess.run(["git", "-C", str(A.REPO), "rev-parse", "ladder-v2^{commit}"], capture_output=True,
                         text=True).stdout.strip()
    if not sha:
        pytest.skip("tag ladder-v2 not present")
    pkg, _ = A.code_package("ladder-v2")
    M = importlib.import_module(pkg.__name__ + ".model")
    torch.manual_seed(0)
    m = M.Emulator(M.SIZES["tiny"])
    ck = tmp_path_factory.mktemp("tiny") / "tiny.pt"
    torch.save({"model_config": m.cfg.to_dict(), "model": m.state_dict(), "ema": None, "samples": 0,
                "git": {"commit": sha, "dirty_code_files": []}}, ck)
    J = A.EmulatorJudge(str(ck), device="cpu", chunk=24, buckets=(24,), compile_trunk=False, model_src="auto")
    inst = [i for i in A.load_instances(A.REPO / "data" / "tasks_v2_H24.json") if i.task == "grow"][0]
    P = A.effective(A.Pools(H).behaviour(inst.start_id)[:8], inst.task, H)[:, :3]     # three months: fast on CPU
    return J, inst, P


def test_ensemble_of_three_copies_is_the_single_model_judge(tiny):
    """Member m of an ensemble of three copies draws exactly the single-model judge's samples on the member's stream;
    an ensemble of one member is the single-model judge; pooled, the three copies' samples follow the single-model
    judge's distribution at 3K samples (two-sample KS on every scalar the predicates read, at month 3)."""
    from scipy.stats import ks_2samp
    J, inst, P = tiny
    ens = D.EnsembleJudge([J, J, J])
    E = ens.samples(inst, P, 2, ("t", 0))
    assert E.shape == (8, 6, 4, 20)
    for m in range(3):
        assert np.array_equal(E[:, 2 * m:2 * m + 2], J.samples(inst, P, 2, D.member_stream(("t", 0), m)))
    assert np.array_equal(D.EnsembleJudge([J]).samples(inst, P, 2, ("t", 0)), J.samples(inst, P, 2, ("t", 0)))
    assert ens.month_steps == 8 * 6 * 3
    S = J.samples(inst, P, 6, ("t", 1))
    for c in (SC_POP, SC_FUNDS):
        a, b = E[:, :, -1, c].ravel(), S[:, :, -1, c].ravel()
        if np.ptp(np.concatenate([a, b])) > 0:
            assert ks_2samp(a, b).pvalue > 0.01
    d = ens.describe()
    assert d["judge"] == "ensemble" and len(d["members"]) == 3 and d["members"][0] == J.describe()


def test_temperature_one_is_the_identity(tiny):
    J, inst, P = tiny
    ref = J.samples(inst, P, 2, ("t", 2))
    t1 = D.TemperedJudge(J, 1.0)
    assert t1.describe() == J.describe()
    assert np.array_equal(t1.samples(inst, P, 2, ("t", 2)), ref)
    # the tempered code path itself at T = 1 draws the identical samples
    assert np.array_equal(D.TemperedJudge(J, 1.0, force_tempered_path=True).samples(inst, P, 2, ("t", 2)), ref)
    t15 = D.TemperedJudge(J, 1.5)
    assert t15.describe()["temperature"] == 1.5
    assert not np.array_equal(t15.samples(inst, P, 2, ("t", 2)), ref)


# ----------------------------------------------------------------------------------------------
# Features, detector, deflation
# ----------------------------------------------------------------------------------------------
def _traj(pop_h, H=H):
    pop_h = np.asarray(pop_h, dtype=np.float64)
    s = np.zeros(pop_h.shape + (H + 1, 20))
    s[..., SC_FUNDS] = 10000.0
    s[..., SC_POP] = 1000.0 + (pop_h[..., None] - 1000.0) * np.linspace(0, 1, H + 1)
    return s


def _inst(start="sA", task="grow", fam=None):
    theta, sd = (2000.0, 400.0) if task == "grow" else (1.8, 0.4)
    return A.Instance(f"{start}|{task}|H{H}", start, fam or f"fam-{start}", task, H, theta, sd, True, f"/nonexistent/{start}.cty")


def test_summarise_by_hand():
    inst = _inst()
    pops = np.array([[[2400.0, 2000.0], [1600.0, 1800.0], [3000.0, 2200.0]]])      # (1 plan, 3 members, 2 samples)
    tr = _traj(pops)
    st = A.traj_stats(tr)
    mo = tr[..., list(D.MONTH_COLS)]
    eff = np.zeros((1, H, 25), dtype=np.int16)
    eff[0, :6, D.KIND_COLS[0]] = 1
    eff[0, 3, D.KIND_COLS[2]] = 4
    S = D.summarise(inst, st, mo, eff)
    margins = np.minimum((pops - 2000.0) / 400.0, 1.0)          # grow: the funds clause (funds / starting funds) caps it
    assert np.allclose(S["margins"], margins)
    assert np.isclose(S["mean_margin"][0], margins.mean())
    assert np.isclose(S["pass_share"][0], 4 / 6)
    assert np.isclose(S["disagreement"][0], np.std(margins.mean(axis=2)[0], ddof=1))
    mean_pop = 1000.0 + (pops.mean(axis=2)[0][:, None] - 1000.0) * np.linspace(0, 1, H + 1)[None, 1:]   # (3, H)
    assert np.isclose(S["monthly_spread"][0], np.std(mean_pop, axis=0, ddof=1).mean() / 400.0)
    assert np.isclose(S["macro_share"][0], 6 / 24)
    one = D.summarise(inst, st[:, :1], mo[:, :1], eff)
    assert one["disagreement"][0] == 0 and one["monthly_spread"][0] == 0
    # the recover statistic month by month is the population ratio to the start
    r = D.monthly_statistic("recover", mo)
    assert np.allclose(r[0, 0, 0], tr[0, 0, 0, 1:, SC_POP] / 1000.0)


def test_logistic_recovers_coefficients_and_refuses_one_class():
    rng = np.random.default_rng(0)
    X = rng.standard_normal((4000, 3))
    w = np.array([-1.0, 2.0, 0.0, -0.5])
    y = rng.random(4000) < 1 / (1 + np.exp(-(w[0] + X @ w[1:])))
    m = D.fit_logistic(X, y)
    assert m.converged
    coef = m.w[1:] / m.sd                       # back on the raw scale
    assert np.allclose(coef, w[1:], atol=0.15)
    assert np.allclose(m.prob(X).mean(), y.mean(), atol=1e-6)      # the MLE with an intercept matches the mean
    with pytest.raises(ValueError):
        D.fit_logistic(X, np.zeros(4000, bool))


def test_deflation_by_hand():
    q = np.array([0.0, 0.1, 0.6, 0.0])
    acc = q >= 0.5
    v = np.array([0.125, 0.0, 0.875, 0.25])
    d = D.deflation_prior(q, acc, v)
    var_mu, var_v = np.var(q, ddof=1), np.mean((v - q) ** 2)
    assert np.isclose(d["mu_bar"], 0.25) and np.isclose(d["var_mu"], var_mu) and np.isclose(d["var_v"], var_v)
    assert np.isclose(d["alpha"], 1 / (1 + var_v / var_mu))
    assert np.isclose(D.deflate(0.75, d["mu_bar"], d["alpha"]), d["alpha"] * 0.75 + (1 - d["alpha"]) * 0.25)
    assert D.deflation_prior(np.zeros(4), np.zeros(4, bool), v)["alpha"] == 0.0     # a point prior
    assert np.allclose(D.deflate(np.array([0.3, 0.9]), 0.1, 1.0), [0.3, 0.9])          # alpha = 1: the identity


def _random_summary(n=200, seed=0):
    rng = np.random.default_rng(seed)
    return {"mean_margin": rng.standard_normal(n), "pass_share": rng.integers(0, 25, n) / 24,
            "disagreement": rng.random(n), "monthly_spread": rng.random(n), "macro_share": rng.random(n)}


def test_every_defence_is_the_identity_at_its_neutral_setting():
    S = _random_summary()
    rng = np.random.default_rng(1)
    det = D.fit_logistic(D.feature_matrix(S), rng.random(200) < 0.3)
    ctx = {"halt": {np.inf: np.inf}, "detector_search": det, "detector_verdict": det,
           "deflation": {"ensemble": {"mu_bar": 0.1, "alpha": 1.0}, "member0": {"mu_bar": 0.0, "alpha": 1.0}}}
    und = D.SETTING_BY_NAME["ensemble"]
    s0, v0 = D.defended_score(und, S, ctx), D.defended_verdict(und, S, ctx)[0]
    for st in (D.Setting("h", "ensemble", "halt", np.inf), D.Setting("d", "ensemble", "detector", 1.0),
               D.Setting("f", "ensemble", "deflation"), D.Setting("f0", "member0", "deflation"),
               D.Setting("t", "member0", "temperature", 1.0)):
        assert np.array_equal(D.defended_score(st, S, ctx), s0), st
        assert np.array_equal(D.defended_verdict(st, S, ctx)[0], v0), st
    # the penalty at lambda = 0: the undefended score; its verdict adds "mean margin >= 0", as the brief writes it
    p0 = D.SETTING_BY_NAME["penalty0"]
    assert np.array_equal(D.defended_score(p0, S, ctx), s0)
    assert np.array_equal(D.defended_verdict(p0, S, ctx)[0], v0 & (S["mean_margin"] >= 0))
    # the design's settings do act
    ctx["halt"][95.0] = float(np.percentile(S["disagreement"], 95))
    h = D.defended_score(D.SETTING_BY_NAME["halt95"], S, ctx)
    assert np.isneginf(h).sum() == int((S["disagreement"] > ctx["halt"][95.0]).sum()) > 0
    pen = D.defended_score(D.SETTING_BY_NAME["penalty2"], S, ctx)
    assert np.allclose(pen, S["mean_margin"] - 2 * S["disagreement"])


def test_family_folds_alternate():
    f = D.family_folds(["ho-03", "ho-01", "ho-02", "ho-00", "ho-01"])
    assert f == {"ho-00": 0, "ho-01": 1, "ho-02": 0, "ho-03": 1}


# ----------------------------------------------------------------------------------------------
# The pipeline with stub judges and a stub engine
# ----------------------------------------------------------------------------------------------
def _value(P):
    return P[..., 0].astype(np.float64).mean(axis=-1) / 20.0


class StubMember(A.SamplingJudge):
    """Population at H = 1000 + 2000 value(plan) + offset + 300 noise (stream-seeded); the noise is scaled by the
    temperature of a ``StubTempered`` wrapper."""

    name = "stub"

    def __init__(self, offset, tag):
        super().__init__()
        self.offset, self.tag = float(offset), tag

    def describe(self):
        return {"judge": "stub", "offset": self.offset, "tag": self.tag}

    def draw(self, inst, P, K, stream, scale=1.0):
        rng = np.random.default_rng(seed_for("stub-member", inst.start_id, *stream))
        pop = 1000.0 + 2000.0 * _value(P)[:, None] + self.offset + 300.0 * scale * rng.standard_normal((P.shape[0], K))
        return _traj(pop, P.shape[1])

    def _samples(self, inst, P, K, stream):
        return self.draw(inst, P, K, stream)


class StubTempered(A.SamplingJudge):
    name = "stub"

    def __init__(self, base, temperature, force_tempered_path=False):
        super().__init__()
        self.base, self.temperature = base, float(temperature)

    def describe(self):
        d = dict(self.base.describe())
        if self.temperature != 1.0:
            d["temperature"] = self.temperature
        return d

    def _samples(self, inst, P, K, stream):
        return self.base.draw(inst, P, K, stream, self.temperature)


class StubEngine:
    workers = 0

    def __init__(self):
        self.n = 0

    def scalars(self, inst, eff, seeds, key_sink=None, store=True):
        P = np.asarray(eff).reshape(-1, H, 25)
        sd = np.broadcast_to(np.asarray(seeds, dtype=np.int64), (P.shape[0],))
        self.n += P.shape[0]
        noise = np.array([np.random.default_rng([int(s), int(A.plan_hash(p)[:8], 16)]).standard_normal()
                          for p, s in zip(P, sd)])
        return np.rint(_traj(1000.0 + 2000.0 * _value(P) + 200.0 * noise)).astype(np.int64)

    def counters(self):
        return {"engine_replays": self.n}


def _frontier(tmp_path, monkeypatch, starts=("sA", "sB", "sC", "sD")):
    monkeypatch.setattr(D, "TemperedJudge", StubTempered)
    inst = [_inst(s, t) for t in ("grow", "recover") for s in starts]
    rng = np.random.default_rng(0)
    arr = {("behaviour", s): np.stack([random_plan(rng, H, p_noop_macro=0.5) for _ in range(1000)]) for s in starts}
    members = [StubMember(0.0, "m0"), StubMember(250.0, "m1"), StubMember(-100.0, "m2")]
    fr = D.Frontier(inst, members, StubEngine(), A.Pools(H, arrays=arr), tmp_path / "work", oracle_n=32,
                    log=lambda s: None)
    return fr, inst


def test_frontier_end_to_end_stub(tmp_path, monkeypatch):
    fr, inst = _frontier(tmp_path, monkeypatch)
    det = fr.detectors()
    for f in (0, 1):
        for k in ("search", "verdict"):
            assert det["folds"][f][k]["model"].n == 4 * D.DETECTOR_PLANS      # two starts x two tasks per fold
    recs = []
    for i in inst:
        recs += fr.run_instance(i, D.SETTINGS, D.SEARCHES)
    assert len(recs) == len(inst) * len(D.SETTINGS) * len(D.SEARCHES)
    for r in recs:
        assert r["budget"] == D.BUDGET
        assert r["emu_month_steps_search"] == D.BUDGET * D.K_SEARCH * r["members"] * H
        if r["defence"] == "detector":
            i = next(j for j in inst if j.key == r["instance"])
            assert r["fold_of_detector"] == 1 - fr.folds[i.family_id]      # never its own family's fold
    R = {(r["search"], r["setting"], r["instance"]): r for r in recs}
    for se in D.SEARCHES:
        for i in inst:
            e = R[(se, "ensemble", i.key)]
            # post hoc settings re-judge the undefended selections
            for name in ("deflation-ensemble", "penalty0"):
                assert R[(se, name, i.key)]["plan_hash"] == e["plan_hash"]
            assert R[(se, "deflation-member0", i.key)]["plan_hash"] == R[(se, "member0", i.key)]["plan_hash"]
            assert R[(se, "penalty0", i.key)]["grader_accept"] == (e["grader_accept"] and e["grader_mean_margin"] >= 0)
    # resume: nothing is recomputed, and a deleted record comes back identical (timings aside)
    n0 = fr.store.computed_month_steps
    assert all(fr.run_instance(i, D.SETTINGS, D.SEARCHES) == [] for i in inst)
    p = fr._rec_path("cem_seeded", "halt80", inst[0])
    old = json.loads(p.read_text())
    p.unlink()
    new = fr.run_instance(inst[0], D.SETTINGS, D.SEARCHES)
    assert len(new) == 1 and fr.store.computed_month_steps == n0
    strip = lambda r: {k: v for k, v in r.items() if k not in ("search_seconds", "emu_month_steps_search_computed")}
    assert strip(json.loads(p.read_text())) == strip(old)
    # the frontier table: every setting complete, the perfect emulator and the policy-aware slot present
    perfect = {se: [{"instance": i.key, "grader_p": 0.5, "oracle_accept": True, "oracle_share": 0.6, "cluster": i.family_id}
                    for i in inst] for se in D.SEARCHES}
    tab = D.frontier_table(fr.records(), perfect, [i.key for i in inst], n_boot=200)
    for se in D.SEARCHES:
        rows = {r["setting"]: r for r in tab[se]["rows"]}
        assert rows["policy-aware"]["status"].startswith("slot")
        assert rows["perfect"]["false_rejection"]["value"] == 0.0
        for s in D.SETTINGS:
            assert rows[s.name]["complete"] and rows[s.name]["n"] == len(inst)
        assert set(tab[se]["dominance_vs_undefended_ensemble"]) == {s.name for s in D.SETTINGS if s.name != "ensemble"}
    md = D.frontier_md(tab, ["# t"])
    assert "policy-aware" in md and "halt above 80th" in md


def test_search_is_the_identity_at_neutral_settings(tmp_path, monkeypatch):
    fr, inst = _frontier(tmp_path, monkeypatch, starts=("sA", "sB"))
    i = inst[0]
    prep = fr.prepare(i)
    beh, flat = fr.behaviour(i)
    ctx = {"halt": {np.inf: np.inf}, "deflation": prep["deflation"],
           "detector_search": D.fit_logistic(prep["det_search_X"], np.arange(D.DETECTOR_PLANS) % 3 == 0)}
    und = D.SETTING_BY_NAME["ensemble"]
    for se in D.SEARCHES:
        ref = fr._search(und, se, i, prep, ctx, flat)
        for st in (D.Setting("h", "ensemble", "halt", np.inf), D.Setting("d", "ensemble", "detector", 1.0),
                   D.SETTING_BY_NAME["penalty0"]):
            sel = fr._search(st, se, i, prep, ctx, flat)
            assert np.array_equal(sel.plan, ref.plan) and sel.log["best_index"] == ref.log["best_index"], (se, st)
    # the seeded search's first generation is the first N proposals, as in the audit
    G, N = hd.cem_schedule(D.BUDGET)
    assert (G, N) == (5, 200)
