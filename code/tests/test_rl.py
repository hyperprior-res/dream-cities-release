"""Tests of the RL arm (dc.rl, dc.rl_adaptor, scripts/run_rl.py naming and evaluation) on CPU: a stub environment,
the emulator's tiny size loaded with the code of tags ladder-v2 (the default) and ladder-v1 through the adaptor,
and the real engine on a few held-out starts."""

import dataclasses
import importlib
import json
import sys
import types
from pathlib import Path

import numpy as np
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hpr-dream"))

from dc import grammar as G  # noqa: E402
from dc import rl  # noqa: E402
from dc import rl_adaptor as RA  # noqa: E402
from dc import tasks as T  # noqa: E402
from dc.engine import Engine  # noqa: E402
from dc.seeds import seed_for  # noqa: E402

torch.set_num_threads(2)
H = 24


def _small_cfg(**kw):
    base = dict(n_envs=4, rollout_len=6, budget=4 * 6 * 6, snapshots=(72, 144), minibatch=12, save_every=2, epochs=2)
    base.update(kw)
    return rl.RLConfig(**base)


def _stub_trainer(tmp, cfg, task="grow", n_inst=2, key="t"):
    inst = RA.load_family(task)[:n_inst]
    emu = rl.StubEmulator("cpu")
    env = rl.TaskVecEnv(rl.StubEnv(emu, cfg.n_envs), inst, cfg.n_envs, key)
    return rl.Trainer(cfg, env, tmp, key, log=lambda s: None), emu, inst


def _log_lines(path):
    out = []
    for ln in Path(path).read_text().splitlines():
        d = json.loads(ln)
        d.pop("seconds")
        d.pop("snapshot", None)                  # a path inside the run directory
        out.append(d)
    return out


# ----------------------------------------------------------------------------------------------
# budget, snapshots, resume
# ----------------------------------------------------------------------------------------------
def test_month_budget_exact_and_snapshots(tmp_path):
    cfg = _small_cfg()
    tr, emu, _ = _stub_trainer(tmp_path, cfg)
    res = tr.train()
    assert res["months"] == cfg.budget == tr.months
    assert emu.month_steps == cfg.budget                     # environment steps actually taken
    lines = _log_lines(tmp_path / "log.jsonl")
    assert [d["months"] for d in lines] == [cfg.months_per_iter * (k + 1) for k in range(6)]
    snaps = sorted(p.name for p in tmp_path.glob("snap_*.pt"))
    assert snaps == [f"snap_{s:09d}.pt" for s in cfg.snapshots]
    for s in cfg.snapshots:
        ck = torch.load(tmp_path / f"snap_{s:09d}.pt", weights_only=False)
        assert ck["months"] == s
    with pytest.raises(ValueError):
        _small_cfg(budget=100).check()                       # not a multiple of n_envs x rollout_len
    with pytest.raises(ValueError):
        _small_cfg(snapshots=(30, 144)).check()


def test_resumed_run_equals_uninterrupted(tmp_path):
    cfg = _small_cfg()
    a, _, _ = _stub_trainer(tmp_path / "a", cfg)
    a.train()
    b, _, _ = _stub_trainer(tmp_path / "b", cfg)
    r = b.train(stop_after_iters=3)                           # killed after iteration 3; latest.pt is at 2
    assert r["stopped"] and r["iteration"] == 3
    b2, _, _ = _stub_trainer(tmp_path / "b", cfg)             # a new process
    b2.train()
    for k, v in a.policy.state_dict().items():
        assert torch.equal(v, b2.policy.state_dict()[k]), k
    assert _log_lines(tmp_path / "a" / "log.jsonl") == _log_lines(tmp_path / "b" / "log.jsonl")
    for s in cfg.snapshots:
        pa = torch.load(tmp_path / "a" / f"snap_{s:09d}.pt", weights_only=False)["policy"]
        pb = torch.load(tmp_path / "b" / f"snap_{s:09d}.pt", weights_only=False)["policy"]
        assert all(torch.equal(pa[k], pb[k]) for k in pa)


def test_resume_engine_environment(tmp_path):
    """The engine environment is restored by replaying each slot's action log (no state injection)."""
    cfg = _small_cfg(n_envs=2, rollout_len=5, budget=40, snapshots=(40,), minibatch=10, save_every=1, epochs=1)
    inst = RA.load_family("recover")[:2]

    def trainer(d):
        env = rl.TaskVecEnv(rl.EngineEnv(2, workers=0), inst, 2, "eng-resume")
        return rl.Trainer(cfg, env, d, "eng-resume", log=lambda s: None), env
    a, ea = trainer(tmp_path / "a")
    a.train()
    b, eb = trainer(tmp_path / "b")
    b.train(stop_after_iters=2)                              # mid-episode (months 10 of 24)
    b2, eb2 = trainer(tmp_path / "b")
    b2.train()
    assert _log_lines(tmp_path / "a" / "log.jsonl") == _log_lines(tmp_path / "b" / "log.jsonl")
    assert all(torch.equal(v, b2.policy.state_dict()[k]) for k, v in a.policy.state_dict().items())
    for e in (ea, eb, eb2):
        e.b.close()


# ----------------------------------------------------------------------------------------------
# reward, margins, plans, raster; the predicate only through dc.tasks
# ----------------------------------------------------------------------------------------------
@pytest.mark.parametrize("task", ["solvent", "recover"])
def test_reward_telescopes(task):
    inst = RA.load_family(task)[:3]
    emu = rl.StubEmulator("cpu")
    E = 6
    env = rl.TaskVecEnv(rl.StubEnv(emu, E), inst, E, "tele")
    env.reset_all()
    rng = np.random.default_rng(0)
    acc = np.zeros(E)
    sums = []
    torch.manual_seed(0)
    for step in range(2 * H + 5):
        r, d = env.step(G.random_plan(rng, E, p_noop_macro=0.7))
        acc += r
        for e in np.flatnonzero(d):
            sums.append((e, acc[e]))
            acc[e] = 0.0
    fin = env.finished
    assert len(fin) == 2 * E
    for (e, s), f in zip(sums, fin):
        assert f["slot"] == e
        assert abs(s - (f["final_margin"] - f["start_margin"])) < 1e-9


def test_final_margin_is_the_task_margin():
    inst = RA.load_family("power")[:2]
    emu = rl.StubEmulator("cpu")
    env = rl.TaskVecEnv(rl.StubEnv(emu, 2), inst, 2, "fm", auto_reset=False)
    env.reset_all()
    rng = np.random.default_rng(1)
    for t in range(H):
        env.step(G.random_plan(rng, 2, p_noop_macro=0.5))
        for e in range(2):                                     # every month: dc.tasks on the bare trajectory so far
            i = inst[e]
            want = float(T.margin("power", env.traj[e, :t + 2], i.theta, i.stat_sd))
            assert env.margin[e] == pytest.approx(want, abs=0)


def test_prefix_margin_equals_margin_of_prefix():
    """Rows at mixed months in one call (month 0 included), five families: each row gets dc.tasks' margin of its own
    bare prefix; the one-row prefix is dc.tasks' own case (treasury's tax clause has no month yet)."""
    rng = np.random.default_rng(2)
    traj = rng.normal(1000, 300, size=(7, H + 1, 20)).round()
    traj[..., 0] = rng.normal(500, 2000, size=(7, H + 1)).round()       # funds, sometimes negative
    for task in T.TASKS:
        i = dataclasses.replace(RA.load_family(task)[0], theta=900.0, stat_sd=250.0)
        t = np.concatenate([[0, 0], rng.integers(1, H + 1, size=4), [H]])
        got = rl.prefix_margin(i, traj, t)
        want = np.array([T.margin(task, traj[k, :t[k] + 1], 900.0, 250.0) for k in range(7)])
        np.testing.assert_array_equal(got, want)
        assert np.isfinite(got).all()
        assert rl.start_margin(i, traj[0, 0]) == got[0]


def test_task_calls_are_dc_tasks():
    """The adaptor's margin, statistic and feasibility are dc.tasks' on the instance's threshold."""
    rng = np.random.default_rng(6)
    traj = rng.normal(5000, 3000, size=(9, H + 1, 20)).round()
    for task in T.TASKS:
        for i in RA.load_family(task)[:2]:
            np.testing.assert_array_equal(RA.task_margin(i, traj), T.margin(task, traj, i.theta, i.stat_sd))
            np.testing.assert_array_equal(RA.task_statistic(i, traj), T.statistic(task, traj))
            np.testing.assert_array_equal(RA.task_feasible(i, traj), T.feasible(task, traj))
    assert RA.forced_for("recover") == T.forced_for("recover") and RA.forced_for("grow") == {}


def test_effective_rows_match_the_audit():
    rng = np.random.default_rng(3)
    plan = G.random_plan(rng, H)
    plan[:, 4] = rng.integers(0, 7, size=H)
    for task in ("recover", "grow"):
        rows = np.stack([rl.effective_rows(plan[t:t + 1], task, np.array([t]))[0] for t in range(H)])
        np.testing.assert_array_equal(rows, RA.effective(plan[None], task)[0])
    assert RA.effective(plan[None], "recover")[0, 0, 4] == T.forced_for("recover")[0]


def test_raster_on_device_equals_grammar_raster():
    rng = np.random.default_rng(4)
    rows = np.concatenate([G.random_plan(rng, 200), G.random_plan(rng, 100, p_noop_macro=0.5)])
    np.testing.assert_array_equal(rl.raster_torch(rows, "cpu").numpy(), G.raster_batch(rows))


def test_action_heads_and_rows():
    assert rl.N_LOGITS == 21 + 3 * 5 + 4 * (19 + 120 + 100 + 31 + 5)
    torch.manual_seed(0)
    logits = torch.randn(64, rl.N_LOGITS)
    g = torch.Generator().manual_seed(0)
    a = rl.sample_actions(logits, g)
    rows = rl.actions_to_rows(a)
    assert G.is_valid_plan(rows) and (rows[:, 4] == 0).all()
    lp, ent = rl.logp_entropy(logits, a)
    used = rl.used_heads(a)
    lps = rl.head_logps(logits)
    manual = sum(lps[i].gather(1, a[:, i:i + 1]).squeeze(1) * used[:, i] for i in range(rl.N_HEADS))
    torch.testing.assert_close(lp, manual)
    noop = a[:, 4] == 0
    assert not used[noop][:, 5:9].any() and used[~noop][:, 5:7].all()
    gr = rl.sample_actions(logits, None, greedy=True)
    assert torch.equal(gr[:, 0], logits[:, :21].argmax(1))


# ----------------------------------------------------------------------------------------------
# evaluation : stub emulator, real engine through the audit's engine judge
# ----------------------------------------------------------------------------------------------
REC_FIELDS = ["start_margin", "dream_start_margin", "dream_margins", "dream_accepts", "plan_hashes", "dream_macros",
              "engine_open_margins", "engine_open_accepts", "engine_open_shares", "engine_open_majority_margins",
              "engine_open_seed0_margins", "engine_open_seed0_accepts", "plan0_engine_open_margin",
              "plan0_engine_open_accept", "plan0_engine_open_share", "plan0_audit_margins8", "plan0_audit_margin_mean",
              "plan0_audit_margin_4th", "plan0_audit_p", "plan0_audit_accept", "plan0_hacked",
              "engine_closed_margins", "engine_closed_accepts", "closed_seeds", "closed_plan_hashes", "closed_macros",
              "closed_loop_replay_equal", "emu_month_steps_dream", "emu_month_steps_audit", "engine_city_months_open",
              "engine_city_months_closed", "engine_city_months_closed_check", "in_band", "n_oracle_seeds"]
GREEDY_FIELDS = ["greedy_plan_hash", "greedy_macros", "greedy_emulator_margin", "greedy_imagined_margins8",
                 "greedy_imagined_accept", "greedy_engine_open_margin", "greedy_engine_open_accept",
                 "greedy_engine_open_share", "greedy_engine_closed_margin", "greedy_closed_seed",
                 "greedy_closed_loop_replay_equal"]
E8 = rl.EVAL_FROZEN.episodes
S4 = 4                       # oracle seeds in most tests (the first 4 of the instance's 32; the arm uses 32)


def _eval(pol, inst, eng, **kw):
    kw.setdefault("run_key", "evt")
    kw.setdefault("months", 0)
    kw.setdefault("n_oracle", S4)
    return rl.evaluate_snapshot(pol, inst, eng, device="cpu", **kw)


@pytest.fixture(scope="module")
def eng(tmp_path_factory):
    e = RA.engine_judge(workers=0, cache_root=tmp_path_factory.mktemp("ec"), log=lambda s: None)
    yield e
    e.close()


def test_evaluation_records_complete(eng):
    inst = RA.load_family("recover")[:2]
    emu = rl.StubEmulator("cpu")
    torch.manual_seed(1)
    pol = rl.Policy()
    recs, extra = _eval(pol, inst, eng, emu=emu, final=True)
    assert len(recs) == 2 and E8 == 8
    for r, i in zip(recs, inst):
        for f in REC_FIELDS + GREEDY_FIELDS:
            assert f in r, f
        for f in ("dream_margins", "engine_open_margins", "engine_open_shares", "engine_closed_margins", "plan_hashes",
                  "closed_seeds", "closed_loop_replay_equal"):
            assert len(r[f]) == E8, f
        assert len(r["plan0_audit_margins8"]) == 8
        assert r["dream_accepts"] == [m >= 0 for m in r["dream_margins"]]
        assert r["engine_open_accepts"] == [2 * round(s * S4) >= S4 for s in r["engine_open_shares"]]   # majority
        assert r["engine_open_accepts"] == [m >= 0 for m in r["engine_open_majority_margins"]]
        assert r["plan0_engine_open_margin"] == r["engine_open_margins"][0]
        assert r["plan0_audit_accept"] == (np.sort(r["plan0_audit_margins8"])[-4] >= 0)
        assert r["plan0_hacked"] == (r["plan0_audit_accept"] and not r["plan0_engine_open_accept"])
        assert all(r["closed_loop_replay_equal"]) and r["greedy_closed_loop_replay_equal"]
        assert r["start_margin"] == r["dream_start_margin"]       # the emulator starts from the engine's observation
        assert r["emu_month_steps_dream"] == r["emu_month_steps_audit"] == 8 * 24
        assert r["engine_city_months_open"] == E8 * S4 * 24 and r["engine_city_months_closed"] == 8 * 24
        # no closed-loop seed is an oracle seed or a residual seed of the start
        res = RA.reserved_seeds(i.start_id)
        assert not (set(r["closed_seeds"]) | {r["greedy_closed_seed"]}) & res
        assert len(set(r["closed_seeds"])) == E8
    a = extra["arrays"]
    assert a["dream_plans"].shape == (2, E8, H, 25) and a["audit_traj"].shape == (2, 8, H + 1, 20)
    assert a["open_margins"].shape == (2, E8, S4) and a["closed_plans"].shape == (2, E8, H, 25)
    for key in ("dream_plans", "closed_plans", "greedy_emu_plans", "greedy_closed_plans"):
        p = a[key]
        assert (p[..., 0, 4] == T.forced_for("recover")[0]).all() and (p[..., 1:, 4] == 0).all(), key
    assert len({h for r in recs for h in r["plan_hashes"]}) == 2 * E8          # 16 distinct sampled plans
    assert extra["counts"]["emulator_env_month_steps_dream"] == 2 * E8 * H
    assert extra["counts"]["engine_env_city_months_closed"] == 2 * E8 * H
    # the open-loop record of plan j is the oracle's: dc.tasks on the plan's replays on the oracle seeds
    i = inst[1]
    S = T.oracle_seeds(i.start_id, i.task, i.horizon, S4)
    sc = eng.scalars(i, np.repeat(a["dream_plans"][1, 3:4], S4, axis=0), np.asarray(S))
    m = T.margin("recover", sc, i.theta, i.stat_sd)
    assert recs[1]["engine_open_margins"][3] == pytest.approx(float(m.mean()), abs=1e-12)
    assert recs[1]["engine_open_accepts"][3] == bool(T.oracle_verdict("recover", sc, i.theta))
    assert recs[1]["engine_open_shares"][3] == float(T.oracle_share("recover", sc, i.theta))
    assert recs[1]["engine_open_seed0_margins"][3] == float(m[0])
    # the dream verdict is the plan's own trajectory: the dream margin is dc.tasks' margin of the dream trajectory
    assert recs[0]["dream_margins"][5] == float(T.margin("recover", a["dream_traj"][0, 5], inst[0].theta, inst[0].stat_sd))
    s = rl.summarise(recs)
    dm = np.array([m for r in recs for m in r["dream_margins"]])
    om = np.array([m for r in recs for m in r["engine_open_margins"]])
    oa = np.array([m for r in recs for m in r["engine_open_accepts"]])
    assert s["inflation_open"] == pytest.approx(float((dm - om).mean()))
    assert s["verdict_gap_open"] == pytest.approx(float((dm >= 0).mean() - oa.mean()))
    assert s["inflation_closed"] == pytest.approx(s["mean_dream_margin"] - s["mean_engine_closed_margin"])
    assert s["closed_loop_replay_equal"] == f"{2 * E8}/{2 * E8}" and s["greedy_closed_loop_replay_equal"] == "2/2"
    assert s["design_emulator_month_steps"] == 2 * (8 * 24 + 8 * 24 + 24 + 8 * 24)
    # not the final snapshot: no greedy record
    recs2, extra2 = _eval(pol, inst, eng, emu=emu, final=False)
    assert not any(k.startswith("greedy") for k in recs2[0]) and "greedy_closed_plans" not in extra2["arrays"]
    assert [r["dream_margins"] for r in recs2] == [r["dream_margins"] for r in recs]


def test_evaluation_full_oracle_one_instance(eng):
    """With the arm's 32 seeds: one plan per instance's oracle as dc.tasks' majority (16 of 32)."""
    inst = RA.load_family("power")[:1]
    pol = rl.Policy()
    cfg = dataclasses.replace(rl.EVAL_FROZEN, episodes=1, greedy_final=False)
    recs, extra = rl.evaluate_snapshot(pol, inst, eng, run_key="full", months=0, device="cpu", emu=None, cfg=cfg,
                                       n_oracle=T.ORACLE_N)
    i, r = inst[0], recs[0]
    assert T.ORACLE_N == 32 and extra["arrays"]["open_margins"].shape == (1, 1, 32)
    sc = RA.oracle_trajectories(eng, i, extra["arrays"]["closed_plans"][0], 32)
    assert r["engine_open_accepts"][0] == bool(T.oracle_verdict("power", sc, i.theta)[0])
    assert r["engine_city_months_open"] == 32 * 24


def test_evaluation_engine_only(eng):
    """A policy trained on the engine: closed-loop episodes on fresh seeds; their plans are the open-loop plans."""
    inst = RA.load_family("grow")[:2]
    torch.manual_seed(2)
    pol = rl.Policy()
    recs, extra = _eval(pol, inst, eng, emu=None, final=True, months=5)
    for r in recs:
        assert r["open_plans_are_closed_plans"] and r["plan_hashes"] == r["closed_plan_hashes"]
        assert all(r["closed_loop_replay_equal"]) and "dream_margins" not in r
        assert "greedy_engine_closed_margin" in r
    assert "dream_plans" not in extra["arrays"]
    s = rl.summarise(recs)
    assert s["rate_engine_closed_accept"] is not None and "inflation_open" not in s


def test_evaluation_is_seeded(eng):
    """The records are a function of (run, snapshot, policy): two evaluations agree exactly, another snapshot does not."""
    inst = RA.load_family("grow")[:2]
    emu = rl.StubEmulator("cpu")
    pol = rl.Policy()
    r1, x1 = _eval(pol, inst, eng, emu=emu, months=5)
    r2, x2 = _eval(pol, inst, eng, emu=emu, months=5)
    assert r1 == r2
    for k in x1["arrays"]:
        np.testing.assert_array_equal(x1["arrays"][k], x2["arrays"][k])
    r3, _ = _eval(pol, inst, eng, emu=emu, months=10)
    assert [r["plan_hashes"] for r in r3] != [r["plan_hashes"] for r in r1]
    assert [r["closed_seeds"] for r in r3] != [r["closed_seeds"] for r in r1]
    assert (x1["arrays"]["dream_plans"][..., 5::5] > 0).any()              # the untrained policy builds when sampled


def test_evaluation_resumes(eng, tmp_path):
    """Killed after each phase in turn (each time in a fresh call), the evaluation resumes from the saved phases and
    gives the records of an uninterrupted one."""
    inst = RA.load_family("recover")[:2]
    emu = rl.StubEmulator("cpu")
    torch.manual_seed(3)
    pol = rl.Policy()
    ref, xref = _eval(pol, inst, eng, emu=emu, final=True, months=7, out_dir=tmp_path / "ref")
    out = tmp_path / "killed"
    for ph in rl.EMULATOR_PHASES + rl.ENGINE_PHASES:
        with pytest.raises(rl.EvalInterrupted):
            _eval(pol, inst, eng, emu=rl.StubEmulator("cpu"), final=True, months=7, out_dir=out, stop_after=ph)
        assert (out / f"{ph}.npz").exists()
    got, x = _eval(pol, inst, eng, emu=rl.StubEmulator("cpu"), final=True, months=7, out_dir=out)
    assert sorted(x["phases_resumed"]) == sorted(rl.EMULATOR_PHASES + rl.ENGINE_PHASES)
    assert got == ref
    for k in xref["arrays"]:
        np.testing.assert_array_equal(xref["arrays"][k], x["arrays"][k])
    # a phase saved under another tag (here: another policy) is not reused
    pol2 = rl.Policy()
    _, x2 = _eval(pol2, inst, eng, emu=emu, final=True, months=7, out_dir=out)
    assert x2["phases_resumed"] == []


def test_run_script_evaluation_files(tmp_path, monkeypatch):
    """``run_rl.evaluate_run`` on a small stub run: one record file and summary per snapshot, skipped when present."""
    import run_rl
    cfg = _small_cfg()
    tr, emu, inst = _stub_trainer(tmp_path / "cache" / "run", cfg, task="grow", n_inst=2, key="run")
    tr.train()
    orig = RA.engine_judge
    monkeypatch.setattr(RA, "engine_judge", lambda workers=0, log=print: orig(workers=0, cache_root=tmp_path / "ec", log=log))
    args = types.SimpleNamespace(eval_workers=0, env="stub", ckpt="", seed=0)
    digest = RA.tasks_digest(RA.TASKS_JSON)
    rdir = tmp_path / "results" / "run"
    rdir.mkdir(parents=True)
    out = run_rl.evaluate_run(args, cfg, "run", inst, emu, torch.device("cpu"), lambda m: None, digest,
                              tmp_path / "cache" / "run", rdir, S4)
    assert sorted(out) == list(cfg.snapshots)
    for m in cfg.snapshots:
        recs = [json.loads(x) for x in (rdir / f"eval3_{m:09d}.jsonl").read_text().splitlines()]
        assert len(recs) == 2 and all(r["run_key"] == "run" and r["tasks_file"] == digest["tasks_file"] for r in recs)
        s = json.loads((rdir / f"eval3_{m:09d}.summary.json").read_text())
        assert s["months"] == m and s["final_snapshot"] == (m == max(cfg.snapshots))
        assert (s.get("rate_greedy_engine_open_accept") is not None) == s["final_snapshot"]
        assert s["measured_counts"]["engine_env_city_months_closed"] == 2 * E8 * H
    again = run_rl.evaluate_run(args, cfg, "run", inst, emu, torch.device("cpu"), lambda m: None, digest,
                                tmp_path / "cache" / "run", rdir, S4)
    assert again == out


# ----------------------------------------------------------------------------------------------
# run names, tasks file, configuration checks
# ----------------------------------------------------------------------------------------------
def test_tasks_file_in_run_name_and_config(tmp_path, monkeypatch):
    import run_rl
    assert run_rl.DEFAULT_TASKS == "data/tasks_v2_H24.json" and RA.TASKS_JSON.name == "tasks_v2_H24.json"
    t2 = run_rl.tasks_path(run_rl.DEFAULT_TASKS)
    assert run_rl.name_for("emulator", "/x/ladder_v2/os_50m_full/samples_1.pt", "grow", 1, 1_000_000, t2) == \
        "os_50m_full-samples_1__grow__s1__tasks_v2_H24"
    assert run_rl.name_for("engine", "", "power", 0, 300000, Path("/a/tasks_H24.json")) == "engine__power__s0__b300000__tasks_H24"
    assert run_rl.name_for("engine", "", "power", 0, 1_000_000, t2, "stab") == "engine__power__s0__tasks_v2_H24__v-stab"
    # a run made before --tasks existed keeps its untagged name, only for the file it read
    monkeypatch.setattr(run_rl, "RESULTS", tmp_path)
    (tmp_path / "engine__grow__s0__b300000").mkdir()
    (tmp_path / "engine__grow__s0__b300000" / "config.json").write_text(json.dumps({"meta": {"environment": "engine"}}))
    args = types.SimpleNamespace(env="engine", ckpt="", task="grow", seed=0, tasks="data/tasks_H24.json", variant="frozen")
    cfg = dataclasses.replace(rl.FROZEN, budget=300000, snapshots=(300000,))
    assert run_rl.resolve_run_name(args, cfg) == ("engine__grow__s0__b300000", True)
    args.tasks = run_rl.DEFAULT_TASKS
    assert run_rl.resolve_run_name(args, cfg) == ("engine__grow__s0__b300000__tasks_v2_H24", False)
    # the configuration check refuses another tasks file, predicate code, model code, learner or checkpoint
    d = RA.tasks_digest(RA.TASKS_JSON)
    meta = {"environment": "emulator", "task": "grow", "rl_seed": 0, "checkpoint": "c", "model_src": "ladder-v2",
            "init_bias_sha256": "b", **d, "numerics": {"device": "cpu"}}
    c8 = rl.B8_LEARNER.to_dict()
    old = {"cfg": c8, "meta": meta}
    run_rl.check_config(old, {"cfg": c8, "meta": dict(meta)}, "train", False)
    legacy_cfg = {k: v for k, v in c8.items() if k not in ("target_kl", "lr_schedule", "ent_schedule")}
    legacy_cfg["policy"] = {k: v for k, v in c8["policy"].items() if k != "readout"}
    run_rl.check_config({"cfg": legacy_cfg, "meta": meta}, {"cfg": c8, "meta": dict(meta)}, "eval", False)
    for change in ({"tasks_sha256": "0" * 64}, {"tasks_code_sha256": "1" * 64}, {"model_src": "ladder-v1"},
                   {"numerics": {"device": "cuda:0"}}, {"checkpoint": "d"}):
        with pytest.raises(RuntimeError):
            run_rl.check_config(old, {"cfg": c8, "meta": {**meta, **change}}, "train", False)
    with pytest.raises(RuntimeError):
        run_rl.check_config(old, {"cfg": rl.VARIANTS["stab"].to_dict(), "meta": dict(meta)}, "train", False)
    run_rl.check_config(old, {"cfg": c8, "meta": {**meta, "numerics": {"device": "cuda:0"}}}, "eval", False)


# ----------------------------------------------------------------------------------------------
# slot assignment, engine seeds, learner options (round 2, part B)
# ----------------------------------------------------------------------------------------------
def test_slot_assignment_rotates_when_instances_do_not_divide_slots():
    inst = RA.load_family("recover")[:3]
    emu = rl.StubEmulator("cpu")
    E = 4
    env = rl.TaskVecEnv(rl.StubEnv(emu, E), inst, E, "rot")
    env.reset_all()
    rng = np.random.default_rng(0)
    for _ in range(3 * H):                                   # three rounds of episodes
        env.step(G.random_plan(rng, E, p_noop_macro=0.8))
    seen = [(f["episode"], f["slot"], f["instance"]) for f in env.finished]
    assert all(i == (e + k * E) % 3 for k, e, i in seen)
    counts = np.bincount([i for _, _, i in seen], minlength=3)
    assert counts.tolist() == [4, 4, 4]                       # 12 episodes over 3 instances, equal
    assert all(env.theta[e] == inst[env.slot_inst[e]].theta for e in range(E))
    with_40 = rl.TaskVecEnv(rl.StubEnv(emu, 200), RA.load_family("power"), 200, "r40")
    assert (with_40.slot_inst == np.arange(200) % 40).all()  # 40 instances: the assignment


def test_resume_with_rotation(tmp_path):
    cfg = _small_cfg(n_envs=4, rollout_len=6)
    a, _, _ = _stub_trainer(tmp_path / "a", cfg, task="recover", n_inst=3, key="rr")
    a.train()
    b, _, _ = _stub_trainer(tmp_path / "b", cfg, task="recover", n_inst=3, key="rr")
    b.train(stop_after_iters=5)
    b2, _, _ = _stub_trainer(tmp_path / "b", cfg, task="recover", n_inst=3, key="rr")
    b2.train()
    assert _log_lines(tmp_path / "a" / "log.jsonl") == _log_lines(tmp_path / "b" / "log.jsonl")
    assert all(torch.equal(v, b2.policy.state_dict()[k]) for k, v in a.policy.state_dict().items())


def test_training_seeds_are_never_reserved(monkeypatch):
    inst = RA.load_family("power")[:2]
    env = rl.TaskVecEnv(rl.EngineEnv(2, workers=0), inst, 2, "seeds")
    natural = seed_for("rl-engine-train", "seeds", 0, 0)
    seeds = env._seeds(np.array([0, 1]))
    assert seeds[0] == natural                                # unchanged unless reserved
    for s, i in zip(seeds, inst):
        assert s not in RA.reserved_seeds(i.start_id)
    real = RA.reserved_seeds
    monkeypatch.setattr(RA, "reserved_seeds", lambda sid: real(sid) | {natural})
    env2 = rl.TaskVecEnv(rl.EngineEnv(2, workers=0), inst, 2, "seeds")
    s2 = env2._seeds(np.array([0]))[0]
    assert s2 != natural and s2 == RA.fresh_seed(("rl-engine-train", "seeds", 0, 0), real(inst[0].start_id) | {natural})[0]
    env.b.close()
    env2.b.close()


def test_learner_options(tmp_path):
    c = rl.RLConfig(n_envs=4, rollout_len=6, budget=4 * 6 * 4, snapshots=(96,), minibatch=12, lr_schedule="linear",
                    ent_schedule="linear")
    assert c.n_iter == 4 and c.lr_at(0) == c.lr and c.lr_at(2) == pytest.approx(c.lr / 2) and c.ent_at(3) == pytest.approx(c.ent_coef / 4)
    tr, _, _ = _stub_trainer(tmp_path / "s", c)
    tr.train()
    lines = _log_lines(tmp_path / "s" / "log.jsonl")
    assert [d["lr"] for d in lines] == pytest.approx([c.lr_at(k) for k in range(4)])
    assert [d["ent_coef"] for d in lines] == pytest.approx([c.ent_at(k) for k in range(4)])
    # a tiny KL target stops the epoch loop early; the full count is epochs x minibatches
    k = rl.RLConfig(n_envs=4, rollout_len=6, budget=4 * 6 * 3, snapshots=(72,), minibatch=12, epochs=4, target_kl=1e-9)
    tr, _, _ = _stub_trainer(tmp_path / "k", k)
    tr.train()
    lines = _log_lines(tmp_path / "k" / "log.jsonl")
    assert all(d["early_stopped"] and d["minibatch_steps"] < 4 * 2 for d in lines)
    full = _log_lines(tmp_path / "s" / "log.jsonl")
    assert all(d["minibatch_steps"] == 4 * 2 and not d["early_stopped"] for d in full)


def test_update_chunks_accumulate_the_same_gradient(tmp_path):
    cfg = _small_cfg(budget=4 * 6 * 2, snapshots=(48,))
    a, _, _ = _stub_trainer(tmp_path / "a", cfg)
    a.train()
    b, _, _ = _stub_trainer(tmp_path / "b", cfg)
    b.update_chunk = 5                                        # minibatch 12 in chunks of 5, 5, 2
    b.train()
    for key, v in a.policy.state_dict().items():
        torch.testing.assert_close(v, b.policy.state_dict()[key], rtol=1e-4, atol=1e-6)


def test_spatial_readout_starts_as_the_global_policy():
    torch.manual_seed(0)
    pol = rl.Policy(rl.PolicyConfig(readout="spatial"))
    inst = RA.load_family("power")[0]
    ob = rl.pack_state(rl.engine_start_state(inst, "cpu"))
    vec = torch.zeros(1, rl.N_ENV_VEC)
    logits, _ = pol(ob, vec)
    with torch.no_grad():
        pol.pos_out.weight.normal_()                          # the read-out moves the x and y heads only
        logits2, _ = pol(ob, vec)
    d = (logits2 - logits)[0]
    for h in range(rl.N_HEADS):
        sl = slice(rl.HEAD_OFF[h], rl.HEAD_OFF[h + 1])
        if h in rl.X_HEADS or h in rl.Y_HEADS:
            assert d[sl].abs().max() > 0
        else:
            assert d[sl].abs().max() == 0
    pol0 = rl.Policy(rl.PolicyConfig(readout="spatial"))
    add = pol0._position_scores(torch.randn(2, 32, 30, 25), torch.randn(2, 48, 15, 13), torch.randn(2, 256))
    for h in rl.X_HEADS + rl.Y_HEADS:                         # zero-initialised: a constant per head (softmax unchanged)
        sl = add[:, rl.HEAD_OFF[h]:rl.HEAD_OFF[h + 1]]
        assert torch.allclose(sl, sl[:, :1].expand_as(sl))
    assert rl.Policy(rl.PolicyConfig(readout="spatial")).num_parameters() < 3_000_000


# ----------------------------------------------------------------------------------------------
# the emulator through the adaptor (tiny size, code of a tag) and the start states
# ----------------------------------------------------------------------------------------------
_TINY = {}


def _tiny_backend(src, tmp_dir):
    if src not in _TINY:
        pkg, _ = RA.tag_package(src)
        M = importlib.import_module(pkg.__name__ + ".model")           # the tag's own model code writes the weights
        torch.manual_seed(0)
        cfg = dataclasses.replace(M.SIZES["tiny"], bookkeeping=True, bk_width=32, bk_depth=1)
        m = M.Emulator(cfg)
        p = Path(tmp_dir) / f"tiny_{src}.pt"
        torch.save({"model_config": cfg.to_dict(), "model": m.state_dict(), "ema": None, "samples": 0}, p)
        _TINY[src] = RA.EmulatorBackend(p, device="cpu", model_src=src, compile_trunk=False, chunk=8, buckets=(8,))
    return _TINY[src]


@pytest.fixture(scope="module")
def tiny_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("tiny")


@pytest.mark.parametrize("src", ["ladder-v2", "ladder-v1"])
def test_emulator_environment_is_the_judges_process(src, tiny_dir):
    """A fixed plan stepped by the environment equals the audit judge's open-loop rollout under the same seed,
    element for element, and equals the tag's own ``rollout`` at its default decoding."""
    if src == "ladder-v1":
        import subprocess
        if subprocess.run(["git", "-C", str(RA.A.REPO), "rev-parse", "--verify", "ladder-v1^{commit}"],
                          capture_output=True).returncode != 0:
            pytest.skip("historical ladder-v1 tag is not in the single-commit release tree")
    emu = _tiny_backend(src, tiny_dir)
    want = {"ladder-v2": {"temperature": 1.0, "overlay": "sample"}, "ladder-v1": {"temperature": 1.0, "overlay": "mean"}}
    assert emu.decoding == want[src]
    inst = RA.load_family("recover")[0]
    rng = np.random.default_rng(5)
    plans = RA.effective(np.stack([G.random_plan(rng, H, p_noop_macro=0.5) for _ in range(8)]), "recover")
    stream = ("test", 1)
    ref = emu.verdict_samples(inst, plans, 1, stream)[:, 0]                   # (8, H+1, 20)
    torch.manual_seed(seed_for("audit-emu", inst.start_id, *stream))
    env = rl.EmuEnv(emu, 8)
    out = [env.reset(list(range(8)), [inst] * 8, [0] * 8)]
    for h in range(H):
        out.append(env.step(plans[:, h]))
    got = np.stack(out, axis=1)
    np.testing.assert_array_equal(got, ref)
    torch.manual_seed(seed_for("audit-emu", inst.start_id, *stream))
    s0 = {k: v.expand(8, *v.shape[1:]) for k, v in emu.start_state(inst).items()}
    act = torch.from_numpy(G.action_scalars_batch(plans.reshape(-1, 25)).reshape(8, H, -1))
    traj, _ = emu.model.rollout(s0, lambda h: torch.from_numpy(G.raster_batch(plans[:, h])), act, K=1, max_batch=8)
    np.testing.assert_array_equal(got, traj[:, 0].double().numpy())


def test_environment_steps_the_judges_accelerated_model(tiny_dir):
    """The audit judge accelerates its model in place (dc.fast; on a GPU with a compiled trunk). The environment
    steps the same object, so after acceleration (here dc.fast's CPU form, the fused trunk) a fixed plan stepped by
    the environment still equals the judge's rollout element for element."""
    from dc import fast
    _tiny_backend("ladder-v2", tiny_dir)
    p = Path(tiny_dir) / "tiny_ladder-v2.pt"
    emu = RA.EmulatorBackend(p, device="cpu", model_src="ladder-v2", compile_trunk=False, chunk=8, buckets=(8,))
    fast.accelerate(emu.judge.model, compile=False, graphs=False)
    assert emu.model is emu.judge.model and emu.model._fast_levers["fused"]
    inst = RA.load_family("power")[2]
    rng = np.random.default_rng(7)
    plans = RA.effective(np.stack([G.random_plan(rng, H, p_noop_macro=0.5) for _ in range(8)]), "power")
    ref = emu.verdict_samples(inst, plans, 1, ("fast", 1))[:, 0]
    torch.manual_seed(seed_for("audit-emu", inst.start_id, "fast", 1))
    env = rl.EmuEnv(emu, 8)
    out = [env.reset(list(range(8)), [inst] * 8, [0] * 8)]
    for h in range(H):
        out.append(env.step(plans[:, h]))
    np.testing.assert_array_equal(np.stack(out, axis=1), ref)


def test_backend_refuses_a_judge_with_another_decoding(tiny_dir, monkeypatch):
    _tiny_backend("ladder-v2", tiny_dir)
    p = Path(tiny_dir) / "tiny_ladder-v2.pt"
    orig = RA.A.EmulatorJudge.describe
    monkeypatch.setattr(RA.A.EmulatorJudge, "describe",
                        lambda self: {**orig(self), "decoding": {"temperature": 1.0, "overlay": "mean"}})
    with pytest.raises(RuntimeError, match="different processes"):
        RA.EmulatorBackend(p, device="cpu", model_src="ladder-v2", compile_trunk=False, chunk=8, buckets=(8,))


def test_start_states_agree(tiny_dir):
    """The policy sees the same start observation in the emulator, the stub and the engine environment."""
    inst = RA.load_family("grow")[3]
    p_emu = rl.pack_state(_tiny_backend("ladder-v2", tiny_dir).start_state(inst))
    p_eng_state = rl.pack_state(rl.engine_start_state(inst, "cpu"))
    env = rl.EngineEnv(1, workers=0)
    env.reset([0], [inst], [RA.primary_seed(inst)])
    p_env = env.packed()
    env.close()
    for k in rl.PACK_KEYS:
        assert torch.equal(p_emu[k], p_eng_state[k]), k
        assert torch.equal(p_emu[k], p_env[k]), k


def test_engine_environment_follows_the_oracle():
    """A plan played month by month in the engine environment equals ``dc.oracle.replay`` of the same plan."""
    from dc.oracle import replay
    inst = RA.load_family("recover")[1]
    if (RA.A.Pools(H).cal_dir / f"{inst.start_id}.npz").is_file():
        raw = RA.behaviour_plans(inst.start_id, 1)
    else:
        raw = np.stack([G.random_plan(np.random.default_rng(0), H, p_noop_macro=0.3)])
    plan = RA.effective(raw, "recover")[0]
    env = rl.EngineEnv(1, workers=0)
    sc = [env.reset([0], [inst], [77])[0]]
    for h in range(H):
        sc.append(env.step(plan[h:h + 1])[0])
    env.close()
    acts, forced = G.compile_plan(plan)
    e = Engine()
    ref = replay(e, inst.cty, acts, 77, forced=forced).scalars
    e.close()
    np.testing.assert_array_equal(np.stack(sc), ref.astype(np.float64))


def test_policy_size():
    assert rl.Policy().num_parameters() < 3_000_000


# ----------------------------------------------------------------------------------------------
# round 3 : the evaluation split between two machines, the warm start, behaviour cloning
# ----------------------------------------------------------------------------------------------
def test_split_evaluation_equals_the_whole(eng, tmp_path):
    """The emulator side (dream, audit, greedy plan in the emulator) saved on one machine and the engine side run
    from the saved phases with only the emulator's recorded identity give the records of a whole evaluation."""
    inst = RA.load_family("recover")[:2]
    torch.manual_seed(4)
    pol = rl.Policy()
    ref, xref = _eval(pol, inst, eng, emu=rl.StubEmulator("cpu"), final=True, months=9, out_dir=tmp_path / "whole")
    out = tmp_path / "split"
    emu = rl.StubEmulator("cpu")
    recs, x = rl.evaluate_snapshot(pol, inst, None, run_key="evt", months=9, device="cpu", emu=emu, final=True,
                                   out_dir=out, n_oracle=S4, side="emulator")
    assert recs == [] and sorted(p.stem for p in out.glob("*.npz")) == sorted(rl.EMULATOR_PHASES)
    rec_emu = rl.RecordedEmulator(json.loads(json.dumps(emu.describe(), default=str)))
    with pytest.raises(RuntimeError):
        rec_emu.verdict_samples(inst[0], None, 8, ())
    got, x2 = _eval(pol, inst, eng, emu=rec_emu, final=True, months=9, out_dir=out, side="engine")
    assert got == ref and sorted(x2["phases_resumed"]) == sorted(rl.EMULATOR_PHASES)
    for k in xref["arrays"]:
        np.testing.assert_array_equal(xref["arrays"][k], x2["arrays"][k])
    with pytest.raises(RuntimeError, match="emulator phase"):          # the engine side never runs the emulator
        _eval(pol, inst, eng, emu=rec_emu, final=True, months=10, out_dir=tmp_path / "none", side="engine")


def test_month_kl_is_the_kl_of_the_month_distribution():
    """month_kl(p, q) = E_p[log p(month) - log q(month)] with log p as logp_entropy defines it (Monte Carlo over
    200,000 sampled months); 0 for equal policies; the per-head form matches enumeration on one head's change."""
    torch.manual_seed(0)
    lp_ = torch.randn(1, rl.N_LOGITS) * 1.5
    lq_ = lp_ + torch.randn(1, rl.N_LOGITS) * 0.5
    assert float(rl.month_kl(lp_, lp_)) == pytest.approx(0.0, abs=1e-6)
    n = 200_000
    g = torch.Generator().manual_seed(1)
    a = rl.sample_actions(lp_.expand(n, -1), g)
    mc = (rl.logp_entropy(lp_.expand(n, -1), a)[0] - rl.logp_entropy(lq_.expand(n, -1), a)[0])
    se = float(mc.std()) / n ** 0.5
    assert float(rl.month_kl(lp_, lq_)) == pytest.approx(float(mc.mean()), abs=4 * se)


def _bc_demos(tmp_path_factory):
    from dc import data as D
    if not (D.DATA_ROOT / "train_full" / "manifest.json").exists():
        pytest.skip("the offline training store is not on this machine")
    from dc import bc
    root = tmp_path_factory.mktemp("bc")
    bc.extract(root / "demos", limit=2, log=lambda m: None)            # 2 trajectories per split, 144 rows
    return bc, D, root, bc.Demos(root / "demos")


@pytest.fixture(scope="module")
def bc_demos(tmp_path_factory):
    return _bc_demos(tmp_path_factory)


def test_demonstrations_are_packed_as_the_environment_packs_them(bc_demos):
    """Builder trajectories of the training store only (no perturbation, disasters off, training split), split by
    family; month t of a demonstration equals what TaskVecEnv on the engine feeds the policy at month t when it
    plays the stored plan from the stored start and seed (every packed array; the task-free features; the
    task-dependent columns zero); the head values give back the stored row."""
    bc, D, root, demos = bc_demos
    man = demos.manifest
    sel = man["selection"]
    assert sel["kept_months_used"] == 24 * sel["kept_trajectories"]
    assert set(sel["by_style"]) == {s for s in __import__("dc.behaviour", fromlist=["x"]).BUILDER_STYLES}
    assert set(sel["left_out"]) == {"not a builder", "perturbed builder", "random disasters on"}
    assert sum(v["trajectories"] for v in sel["left_out"].values()) + sel["kept_trajectories"] == sel["store_trajectories"]
    fam = {s: set(man["split"]["splits"][s]["family_ids"] or []) for s in ("val", "heldout")}
    assert fam["val"] and fam["heldout"] and not fam["val"] & fam["heldout"]
    t = demos.table
    assert all(l.startswith("builder/") and "+" not in l for l in t["label"])
    for s in ("val", "heldout"):
        assert set(t["family_id"][t["split"] == bc.SPLIT_NAMES.index(s)]) <= fam[s]
    assert not set(t["family_id"][t["split"] == 0]) & (fam["val"] | fam["heldout"])
    st = D.TrajStore(D.DATA_ROOT / "train_full")
    free = [c for c in range(rl.N_ENV_VEC) if c not in rl.TASK_VEC_COLS]
    for k in (0, 5):                                                    # one training, one held-out trajectory
        j = int(t["traj_id"][k])
        rec = st.record(j)
        assert rec["label"] == t["label"][k] and not rec["disasters"] and rec["split"] == "train"
        inst = dataclasses.replace(RA.load_family("grow")[0], start_id=rec["start_id"], cty=rec["cty_path"], key="demo")
        env = rl.TaskVecEnv(rl.EngineEnv(1, workers=0), [inst], 1, "demo", auto_reset=False, slot_seeds=[rec["seed"]])
        env.reset_all()
        b = demos.gather(np.arange(24 * k, 24 * k + 24))
        want = bc.unpack_np(b)
        for m in range(24):
            ob, vec = env.obs()
            for key in rl.PACK_KEYS:
                np.testing.assert_array_equal(ob[key][0].numpy(), want[key][m], err_msg=f"{j} {m} {key}")
            np.testing.assert_array_equal(vec[0, free], b["vec"][m, free])
            assert (b["vec"][m, list(rl.TASK_VEC_COLS)] == 0).all()
            np.testing.assert_array_equal(rl.actions_to_rows(b["actions"][m:m + 1].astype(np.int64))[0], b["rows"][m])
            env.step(b["rows"][m:m + 1])
        env.b.close()


def test_cloning_resumes_keeps_task_inputs_zero_and_loads(bc_demos, tmp_path):
    """Behaviour cloning on CPU (tiny): resumed after one epoch equals uninterrupted; the task-dependent input weights
    are zero after training, so the cloned policy's logits do not depend on the task features; a chunked batch gives
    the same weights to rounding; the saved policy loads for the learner and is refused with another configuration."""
    bc, D, root, demos = bc_demos
    cfg = dataclasses.replace(bc.BC_FROZEN, epochs=2, batch=8, warmup_steps=2, eval_batch=48)
    a = bc.train(demos, 0, tmp_path / "a", device="cpu", cfg=cfg, log=lambda m: None, max_train_rows=32)
    assert bc.train(demos, 0, tmp_path / "b", device="cpu", cfg=cfg, log=lambda m: None, max_train_rows=32,
                    stop_after_epochs=1)["stopped"]
    b = bc.train(demos, 0, tmp_path / "b", device="cpu", cfg=cfg, log=lambda m: None, max_train_rows=32)
    strip = lambda h: [{k: v for k, v in d.items() if k != "seconds"} for d in h]
    assert a["policy_sha256"] == b["policy_sha256"] and strip(a["history"]) == strip(b["history"])
    c = bc.train(demos, 0, tmp_path / "c", device="cpu", cfg=cfg, log=lambda m: None, max_train_rows=32, chunk=3)
    state, meta = bc.load_cloned(tmp_path / "a" / "bc_s0.pt", rl.FROZEN.policy)
    sc, _ = bc.load_cloned(tmp_path / "c" / "bc_s0.pt", rl.FROZEN.policy)
    pa, pc = rl.Policy(rl.FROZEN.policy), rl.Policy(rl.FROZEN.policy)
    pa.load_state_dict(state)
    pc.load_state_dict(sc)
    obc, vecc, _ = bc.Demos.to_device(demos.gather(np.arange(40, 52)), "cpu")
    with torch.no_grad():                    # the policies, not the weights: pos_out.bias shifts a whole head (no
        for x, y in zip(rl.head_logps(pa(obc, vecc)[0]), rl.head_logps(pc(obc, vecc)[0])):   # gradient but rounding)
            torch.testing.assert_close(x, y, rtol=1e-3, atol=1e-3)
    assert meta["meta"]["seed"] == 0 and meta["kept_epoch"] in (1, 2)
    pol = rl.Policy(rl.FROZEN.policy)
    pol.load_state_dict(state)
    assert bc.task_inputs_zero(pol) and not torch.equal(state["vec_fc.weight"], torch.zeros_like(state["vec_fc.weight"]))
    ob, vec, _ = bc.Demos.to_device(demos.gather(np.arange(0, 6)), "cpu")
    with torch.no_grad():
        l0, _ = pol(ob, vec)
        v2 = vec.clone()
        v2[:, list(rl.TASK_VEC_COLS)] = torch.randn(6, len(rl.TASK_VEC_COLS))
        l1, _ = pol(ob, v2)
    assert torch.equal(l0, l1)
    with pytest.raises(RuntimeError):
        bc.load_cloned(tmp_path / "a" / "bc_s0.pt", rl.PolicyConfig(readout="global"))
    assert set(a["heldout"]["per_head"]) == set(bc.HEAD_NAMES) and a["heldout"]["rows"] == 48


def test_warm_start_learner(tmp_path):
    """PPO from a given policy: snapshot 0 is that policy; kl_to_init is 0 in the first iteration; value warm-up
    iterations change the value head only; the KL penalty's coefficient decays linearly to 0 over its share of the
    iterations and the penalty is logged; a resumed warm-started run equals an uninterrupted one."""
    torch.manual_seed(11)
    init = rl.Policy(rl.FROZEN.policy).state_dict()
    cfg = dataclasses.replace(_small_cfg(budget=4 * 6 * 5, snapshots=(0, 48, 120)), policy=rl.FROZEN.policy,
                              value_warmup_iters=2, ref_kl_coef=1.0, ref_kl_frac=0.6)
    assert [cfg.ref_kl_at(k) for k in range(5)] == pytest.approx([1.0, 2 / 3, 1 / 3, 0.0, 0.0])
    with pytest.raises(ValueError):
        _stub_trainer(tmp_path / "x", cfg)                               # needs an initial policy

    def trainer(d):
        inst = RA.load_family("grow")[:2]
        env = rl.TaskVecEnv(rl.StubEnv(rl.StubEmulator("cpu"), cfg.n_envs), inst, cfg.n_envs, "warm")
        return rl.Trainer(cfg, env, d, "warm", log=lambda s: None, init_policy=init)
    a = trainer(tmp_path / "a")
    a.train(stop_after_iters=2)                                          # the two warm-up iterations
    s0 = torch.load(tmp_path / "a" / f"snap_{0:09d}.pt", weights_only=False)["policy"]
    assert all(torch.equal(s0[k], init[k]) for k in init)
    now = a.policy.state_dict()
    changed = {k for k in init if not torch.equal(now[k], init[k])}
    assert changed == {"v.weight", "v.bias"}
    a.train()
    lines = _log_lines(tmp_path / "a" / "log.jsonl")
    assert lines[0]["kl_to_init"] == pytest.approx(0.0, abs=1e-6) and lines[0]["value_warmup"]
    assert [d["value_warmup"] for d in lines] == [True, True, False, False, False]
    assert [d["ref_kl_coef"] for d in lines] == pytest.approx([0.0, 0.0, 1 / 3, 0.0, 0.0])
    assert "ref_kl" in lines[2] and "ref_kl" not in lines[3] and lines[-1]["kl_to_init"] > 0
    b = trainer(tmp_path / "b")
    b.train(stop_after_iters=3)
    trainer(tmp_path / "b").train()
    assert _log_lines(tmp_path / "a" / "log.jsonl") == _log_lines(tmp_path / "b" / "log.jsonl")
    # the gated warm-up: it ends at the first iteration whose explained variance (before the update) reaches the
    # threshold; that iteration is a full update; never with -inf, through the cap with +inf
    for thr, want in ((-np.inf, [False] * 5), (np.inf, [True, True, False, False, False])):
        cfg2 = dataclasses.replace(cfg, value_warmup_ev=thr)
        inst = RA.load_family("grow")[:2]
        env = rl.TaskVecEnv(rl.StubEnv(rl.StubEmulator("cpu"), cfg.n_envs), inst, cfg.n_envs, "warm")
        t = rl.Trainer(cfg2, env, tmp_path / f"g{thr}", "warm", log=lambda s: None, init_policy=init)
        t.train()
        assert [d["value_warmup"] for d in _log_lines(tmp_path / f"g{thr}" / "log.jsonl")] == want
    cfg3 = dataclasses.replace(cfg, value_warmup_ev=0.0)
    env = rl.TaskVecEnv(rl.StubEnv(rl.StubEmulator("cpu"), cfg.n_envs), RA.load_family("grow")[:2], cfg.n_envs, "warm")
    t = rl.Trainer(cfg3, env, tmp_path / "g0", "warm", log=lambda s: None, init_policy=init)
    t.train()
    L = _log_lines(tmp_path / "g0" / "log.jsonl")
    for d in L:                                                          # warm exactly while EV < 0, within the cap
        if d["iteration"] <= 2 and all(x["value_warmup"] for x in L[:d["iteration"] - 1]):
            assert d["value_warmup"] == (d["explained_variance"] < 0)
    assert rl.VARIANTS["bc"].value_warmup_ev == 0.0 and rl.VARIANTS["bc"].value_warmup_iters == rl.BC_VALUE_WARMUP


def test_run_names_and_queue_commands(tmp_path):
    """Warm-started runs: the variant is in the run name, --init-from is required (and refused for other learners);
    the queue passes the cloned policy of the run's seed, the memory options and the evaluation side, and builds the
    engine side's command; the checkpoint is compared by sha256 when both configs record one."""
    import run_rl
    import rl_queue
    t2 = run_rl.tasks_path(run_rl.DEFAULT_TASKS)
    assert run_rl.name_for("engine", "", "power", 0, 1_000_000, t2, "bc_kl") == "engine__power__s0__tasks_v2_H24__v-bc_kl"
    ns = lambda **k: types.SimpleNamespace(**{"cmd": "train", "variant": "bc", "init_from": "", "budget": 0,
                                              "snapshots": "", **k})
    with pytest.raises(SystemExit):
        run_rl.make_cfg(ns())
    with pytest.raises(SystemExit):
        run_rl.make_cfg(ns(variant="frozen", init_from="x.pt"))
    assert run_rl.make_cfg(ns(cmd="eval")).value_warmup_iters == rl.BC_VALUE_WARMUP
    assert run_rl.make_cfg(ns(variant="bc_kl", init_from="x.pt")).ref_kl_coef == 1.0
    run = {"ckpt": "/x/ladder_v2/os_50m_full/samples_006000000.pt", "task": "grow", "seed": 2, "variant": "bc",
           "init_from": "/c/bc_s{seed}.pt", "update_chunk": 250, "buffer": "host", "eval_side": "emulator"}
    cmd = rl_queue.cmd_for(run)
    assert cmd[cmd.index("--init-from") + 1] == "/c/bc_s2.pt" and cmd[cmd.index("--update-chunk") + 1] == "250"
    assert cmd[cmd.index("--buffer") + 1] == "host" and cmd[cmd.index("--eval-side") + 1] == "emulator"
    assert cmd[cmd.index("--variant") + 1] == "bc"
    e = rl_queue.cmd_for(run, "engine")
    assert e[2] == "eval" and e[e.index("--eval-side") + 1] == "engine" and "--init-from" not in e
    assert rl_queue.run_dir(run).name == "os_50m_full-samples_006000000__grow__s2__tasks_v2_H24__v-bc"
    d = RA.tasks_digest(RA.TASKS_JSON)
    meta = {"environment": "emulator", "task": "grow", "rl_seed": 2, "checkpoint": "/rented/a.pt", "checkpoint_sha256": "s",
            "model_src": "ladder-v2", "init_bias_sha256": None, "init_policy_sha256": "p", **d, "numerics": {"device": "cuda:0"}}
    c = rl.VARIANTS["bc"].to_dict()
    run_rl.check_config({"cfg": c, "meta": meta}, {"cfg": c, "meta": {**meta, "checkpoint": "<home>"}}, "eval", False)
    run_rl.check_config({"cfg": c, "meta": meta}, {"cfg": c, "meta": {**meta, "init_policy_sha256": None}}, "eval", False)
    for change in ({"checkpoint_sha256": "t"}, {"init_policy_sha256": "q"}):
        with pytest.raises(RuntimeError):
            run_rl.check_config({"cfg": c, "meta": meta}, {"cfg": c, "meta": {**meta, **change}}, "train", False)


def test_run_script_split_evaluation(tmp_path, monkeypatch):
    """``run_rl.py``'s two sides: the emulator side writes emulator.json, every snapshot's emulator phases and
    DONE_emulator.json (with the files to carry); the engine side, given only those files and the recorded identity,
    writes the records a whole evaluation writes."""
    import run_rl
    cfg = _small_cfg()
    tr, emu, inst = _stub_trainer(tmp_path / "cache" / "run", cfg, task="grow", n_inst=2, key="run")
    tr.train()
    orig = RA.engine_judge
    monkeypatch.setattr(RA, "engine_judge", lambda workers=0, log=print: orig(workers=0, cache_root=tmp_path / "ec", log=log))
    digest = RA.tasks_digest(RA.TASKS_JSON)
    whole = types.SimpleNamespace(eval_workers=0, env="stub", ckpt="", seed=0)
    (tmp_path / "rw").mkdir()
    run_rl.evaluate_run(whole, cfg, "run", inst, emu, torch.device("cpu"), lambda m: None, digest, tmp_path / "cache" / "run",
                        tmp_path / "rw", S4)
    import shutil
    shutil.copytree(tmp_path / "cache" / "run", tmp_path / "split", ignore=shutil.ignore_patterns("eval3_*"))
    rdir = tmp_path / "rs"
    rdir.mkdir()
    (rdir / "config.json").write_text("{}")
    shutil.copy(tmp_path / "cache" / "run" / "log.jsonl", rdir / "log.jsonl")
    side = types.SimpleNamespace(eval_workers=0, env="emulator", ckpt="", seed=0, eval_side="emulator")
    run_rl.evaluate_run(side, cfg, "run", inst, rl.StubEmulator("cpu"), torch.device("cpu"), lambda m: None, digest,
                        tmp_path / "split", rdir, S4)
    done = json.loads((tmp_path / "split" / run_rl.DONE_EMULATOR).read_text())
    assert all(Path(f).exists() for f in done["files"]) and not list(rdir.glob("eval3_*"))
    rec = rl.RecordedEmulator(json.loads((tmp_path / "split" / run_rl.EMULATOR_JSON).read_text()))
    side.eval_side = "engine"
    run_rl.evaluate_run(side, cfg, "run", inst, rec, torch.device("cpu"), lambda m: None, digest, tmp_path / "split", rdir, S4)
    for m in cfg.snapshots:                   # identical records (the checkpoint field names the stub run: null)
        rd = lambda d: [{k: v for k, v in json.loads(x).items() if k != "checkpoint"}
                        for x in (d / f"eval3_{m:09d}.jsonl").read_text().splitlines()]
        assert rd(tmp_path / "rw") == rd(rdir) and len(rd(rdir)) == 2


def test_recorded_identity_gives_the_live_backends_phase_tag(tiny_dir):
    """The engine side finds the emulator side's phases: the tag computed with the live backend equals the tag
    computed with its identity written to JSON and read back (tuples, devices and paths included)."""
    emu = _tiny_backend("ladder-v2", tiny_dir)
    inst = RA.load_family("grow")[:2]
    pol = rl.Policy()
    rec = rl.RecordedEmulator(json.loads(json.dumps(emu.describe(), indent=1, default=str)))
    for final in (False, True):
        live = rl.eval_tag(pol, inst, "k", 250000, "cpu", emu, final, rl.EVAL_FROZEN, 32)
        assert live == rl.eval_tag(pol, inst, "k", 250000, "cpu", rec, final, rl.EVAL_FROZEN, 32)
    assert rl.eval_tag(pol, inst, "k", 250000, "cuda:0", rec, True, rl.EVAL_FROZEN, 32) != live


# ----------------------------------------------------------------------------------------------
# round 4 : the treasury tax cap, the hybrid start
# ----------------------------------------------------------------------------------------------
def _high_tax_bias():
    b = np.zeros(rl.N_LOGITS, dtype=np.float32)
    b[:21] = np.linspace(-3, 3, 21)                                   # the tax head prefers high rates
    return b


def _capped_trainer(tmp, task, mask, key="cap"):
    cfg = dataclasses.replace(_small_cfg(budget=4 * 6 * 4, snapshots=(96,)), mask_treasury_tax=mask)
    inst = RA.load_family(task)[:2]
    env = rl.TaskVecEnv(rl.StubEnv(rl.StubEmulator("cpu"), cfg.n_envs), inst, cfg.n_envs, key)
    seen = []
    step = env.step

    def checked(rows):                                                 # every month a learner sends, with its cap
        seen.append((np.asarray(rows)[:, 0].copy(), env.traj[:, 0, 1].copy()))
        return step(rows)
    env.step = checked
    return rl.Trainer(cfg, env, tmp, key, init_bias=_high_tax_bias(), log=lambda s: None), seen


def test_treasury_tax_cap_masks_training_and_evaluation(eng, tmp_path):
    """In treasury a learner with the mask never sets the tax above the start rate (training months, sampled and
    greedy evaluation, emulator and engine environments), and the engine's trajectories then keep the predicate's tax
    clause; without the mask the same learner does exceed it; other families are untouched by the mask."""
    tr, seen = _capped_trainer(tmp_path / "m", "treasury", True)
    tr.train()
    assert all((t <= c).all() for t, c in seen) and len(seen) == 4 * 6
    un, seen_u = _capped_trainer(tmp_path / "u", "treasury", False)
    un.train()
    assert any((t > c).any() for t, c in seen_u)                      # the test has teeth
    # evaluation: dream (stub emulator), closed loop on the engine, greedy, all capped
    inst = RA.load_family("treasury")[:2]
    recs, x = _eval(tr.policy, inst, eng, emu=rl.StubEmulator("cpu"), final=True, months=96, tax_cap=True)
    start_tax = np.array([rl.engine_start_state(i, "cpu")["scalars"][0, 1].item() for i in inst])
    for key in ("dream_plans", "closed_plans", "greedy_emu_plans", "greedy_closed_plans"):
        p = x["arrays"][key]
        cap = start_tax.reshape(-1, *([1] * (p.ndim - 1)))
        assert (p[..., 0] <= cap[..., 0]).all(), key
    ct = x["arrays"]["closed_traj"]                                    # the engine's own tax column: the clause holds
    assert (ct[..., 1:, 1].max(-1) <= ct[..., 0, 1]).all()
    assert all(r["tax_cap"] for r in recs)
    r0, _ = _eval(tr.policy, inst, eng, emu=rl.StubEmulator("cpu"), final=False, months=96)
    assert any(any(m > 0 for m in r["dream_macros"]) for r in r0)
    # other families: the mask changes nothing (logs and weights identical)
    a, _ = _capped_trainer(tmp_path / "ga", "grow", True, key="g")
    b, _ = _capped_trainer(tmp_path / "gb", "grow", False, key="g")
    a.train()
    b.train()
    assert _log_lines(tmp_path / "ga" / "log.jsonl") == _log_lines(tmp_path / "gb" / "log.jsonl")
    assert all(torch.equal(v, b.policy.state_dict()[k]) for k, v in a.policy.state_dict().items())
    assert rl.FROZEN.mask_treasury_tax and not rl.RLConfig.from_dict(rl.STAB_SPATIAL.to_dict()).mask_treasury_tax
    assert rl.FROZEN == dataclasses.replace(rl.STAB_SPATIAL, mask_treasury_tax=True)


def test_hybrid_start(tmp_path):
    """The hybrid start is the clone except the tax and funding heads' rows of the policy layer, which are exactly
    the fresh policy's of the run (seeded as every run of the family and seed, with its behaviour-marginal biases);
    the task columns of the vector layer stay the clone's zeros."""
    torch.manual_seed(5)
    clone = rl.Policy(rl.FROZEN.policy)
    with torch.no_grad():
        clone.vec_fc.weight[:, list(rl.TASK_VEC_COLS)] = 0.0
        clone.pi.weight.normal_()
        clone.pi.bias.normal_()
    cs = {k: v.clone() for k, v in clone.state_dict().items()}
    cfg = dataclasses.replace(rl.VARIANTS["hybrid"], n_envs=4, rollout_len=6, budget=24, snapshots=(24,), minibatch=12)
    inst = RA.load_family("grow")[:2]
    bias = _high_tax_bias()
    env = rl.TaskVecEnv(rl.StubEnv(rl.StubEmulator("cpu"), 4), inst, 4, "h")
    with pytest.raises(ValueError):
        rl.Trainer(cfg, env, tmp_path / "h", "h", init_key="grow|s0", init_policy=cs, log=lambda s: None)
    t = rl.Trainer(cfg, env, tmp_path / "h", "h", init_key="grow|s0", init_bias=bias, init_policy=cs,
                   log=lambda s: None)
    fresh = rl.Trainer(dataclasses.replace(cfg, value_warmup_iters=0, reinit_budget_heads=False), env, tmp_path / "h",
                       "h", init_key="grow|s0", init_bias=bias, log=lambda s: None).policy.state_dict()
    got = t.policy.state_dict()
    n = int(rl.HEAD_OFF[4])
    assert n == 21 + 3 * 5
    for k in got:
        if k in ("pi.weight", "pi.bias"):
            assert torch.equal(got[k][:n], fresh[k][:n]) and torch.equal(got[k][n:], cs[k][n:])
        else:
            assert torch.equal(got[k], cs[k]), k
    assert torch.equal(t.ref_policy.state_dict()["pi.weight"], got["pi.weight"])
    assert "hybrid" in rl.INIT_VARIANTS and rl.VARIANTS["hybrid"].ref_kl_coef == 0


def test_pooled_seeds_in_the_decision_table(tmp_path, monkeypatch):
    """``run_bc.per_instance`` over runs joined by '+': each instance's mean over the runs (its seeds kept together
    for the bootstrap over instances); runs holding different instances are refused."""
    import run_bc
    monkeypatch.setattr(run_bc, "RL_RESULTS", tmp_path)
    rates = {"a": [1, 0, 0, 0], "b": [1, 1, 0, 0], "c": [0, 0, 0, 0]}
    for run, acc in rates.items():
        (tmp_path / run).mkdir()
        recs = [{"instance": f"i{k}", "engine_open_accepts": [bool(acc[k])] * 4 + [False] * 4} for k in range(4)]
        (tmp_path / run / "eval3_001000000.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
    got = run_bc.per_instance("a+b", 1_000_000)
    assert got == {"i0": 0.5, "i1": 0.25, "i2": 0.0, "i3": 0.0}
    d = run_bc.paired(got, run_bc.per_instance("c+c", 1_000_000))
    assert d["n"] == 4 and d["mean"] == pytest.approx(0.1875) and d["lo"] >= 0
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "eval3_001000000.jsonl").write_text(json.dumps({"instance": "j", "engine_open_accepts": [True]}) + "\n")
    with pytest.raises(ValueError):
        run_bc.per_instance("a+d", 1_000_000)
