"""Tests of the monthly replanning run : the joined margin, the controller on stub engines and
models, the real engine's prefix and continuation, the proposal generator, the job server, the instance order and the
analysis's readings. CPU only."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hpr-dream"))

from dc import audit as A  # noqa: E402
from dc import replan as RP  # noqa: E402
from dc import tasks as T  # noqa: E402
from dc.engine import (SC_COAL, SC_FUNDS, SC_NUCLEAR, SC_POP, SC_POWERED, SC_TAX, SC_TAX_FUND,  # noqa: E402
                       SC_UNPOWERED)
from dc.grammar import N_COLS, compile_plan, random_plan  # noqa: E402
from dc.seeds import seed_for  # noqa: E402

H = 24
CAL = A.CAL_DIR / "H24"


# ----------------------------------------------------------------------------------------------
# The joined margin
# ----------------------------------------------------------------------------------------------
def _inst(task, theta, sd, H=4):
    return A.Instance(f"sX|{task}|H{H}", "sX", "fam-X", task, H, float(theta), float(sd), True, "/nonexistent/sX.cty")


def _rows(n, **cols):
    """(n, 20) rows; each keyword (scalar column name) gives one value per row."""
    idx = {"funds": SC_FUNDS, "tax": SC_TAX, "pop": SC_POP, "tax_fund": SC_TAX_FUND, "powered": SC_POWERED,
           "unpowered": SC_UNPOWERED, "coal": SC_COAL, "nuclear": SC_NUCLEAR}
    r = np.zeros((n, 20))
    for k, v in cols.items():
        r[:, idx[k]] = v
    return r


def test_join_prefix_layout_and_dropped_model_row():
    pre = _rows(3, funds=[1, 2, 3], pop=[10, 20, 30])
    suf = _rows(3, funds=[-99, 4, 5], pop=[-99, 40, 50])[None, None].repeat(2, axis=1)     # (1, 2, 3, 20)
    j = A.join_prefix(pre, suf)
    assert j.shape == (1, 2, 5, 20)
    assert np.array_equal(j[0, 1, :, SC_FUNDS], [1, 2, 3, 4, 5]) and np.array_equal(j[0, 0, :, SC_POP], [10, 20, 30, 40, 50])


# hand-computed cases, H = 4, realised months 0..2 (t = 2) joined to a model's months 3..4. The model's own row 0 (its
# reading of the state at t) carries values that would change the margin if it were used.
def test_joined_margin_grow_hand():
    i = _inst("grow", 2000, 400)
    pre = _rows(3, funds=[10000, 3000, 8000], pop=[1000, 1200, 1500])
    suf = _rows(3, funds=[-500, 6000, 7000], pop=[0, 1800, 2600])
    # min((2600 - 2000) / 400 = 1.5, min funds 3000 / 10000 = 0.3)
    assert A.joined_margin(i, pre, suf) == pytest.approx(0.3, abs=1e-12)


def test_joined_margin_solvent_hand():
    i = _inst("solvent", 2000, 400)
    pre = _rows(3, funds=[10000, 3000, 8000], pop=[1000, 1200, 1500])
    suf = _rows(3, funds=[-500, 6000, 7000], pop=[0, 1800, 2600])
    # min(1.5, (3000 - 0.5 * 10000) / 10000 = -0.2): the realised dip in month 1 binds
    assert A.joined_margin(i, pre, suf) == pytest.approx(-0.2, abs=1e-12)


def test_joined_margin_treasury_hand():
    i = _inst("treasury", 500, 100)
    pre = _rows(3, funds=[10000, 3000, 8000], tax=[7, 7, 9], tax_fund=[0, 0, 0])
    suf = _rows(3, funds=[-500, 6000, 7000], tax=[0, 6, 6], tax_fund=[9999, 100, 800])
    # min((800 - 500) / 100 = 3, 3000 / 10000 = 0.3, (7 - max(7, 9, 6, 6)) / 20 = -0.1): the realised raise binds
    assert A.joined_margin(i, pre, suf) == pytest.approx(-0.1, abs=1e-12)


def test_joined_margin_recover_hand():
    i = _inst("recover", 1.2, 0.1)
    pre = _rows(3, funds=[10000, 9000, 8000], pop=[1000, 600, 800])
    suf = _rows(3, funds=[8000, 8000, 8000], pop=[1, 1000, 1300])
    # (1300 / 1000 - 1.2) / 0.1 = 1.0: the start row is the prefix's (the model's row 0 would give 1300)
    assert A.joined_margin(i, pre, suf) == pytest.approx(1.0, abs=1e-9)


def test_joined_margin_power_hand():
    i = _inst("power", 50, 10)
    pre = _rows(3, funds=[10000] * 3, coal=[0, 1, 1], powered=[10, 20, 30])
    suf = _rows(3, funds=[10000] * 3, coal=[2, 2, 2], powered=[30, 50, 58], unpowered=[0, 2, 2])
    # k = 0 + 0 + 1 from the prefix's start row; at H: zones 60, (60 - 50) / 10 = 1, powered 58 / 60 -> (0.9667 -
    # 0.95) / 0.05 = 0.333, plants 2 -> 1 - 2 = -1 (with the model's row 0 as the start, k would be 3)
    assert A.joined_margin(i, pre, suf) == pytest.approx(-1.0, abs=1e-12)
    suf2 = suf.copy()
    suf2[1:, SC_COAL] = 1          # plants 1 = k: slack 0 binds
    assert A.joined_margin(i, pre, suf2) == pytest.approx(0.0, abs=1e-12)
    suf2[1:, SC_COAL] = 0          # slack 1: the powered share binds, (58 / 60 - 0.95) / 0.05
    assert A.joined_margin(i, pre, suf2) == pytest.approx((58 / 60 - 0.95) / 0.05, abs=1e-12)


@pytest.mark.parametrize("task", T.TASKS)
def test_joined_margin_month0_equals_the_margin_exactly(task):
    """At month 0 (the prefix is the start row) the joined margin is the existing margin, bit for bit; with every month
    realised it is the realised trajectory's margin."""
    rng = np.random.default_rng(7)
    inst = _inst(task, {"grow": 3000, "solvent": 3000, "treasury": 400, "recover": 1.1, "power": 40}[task],
                 {"grow": 500, "solvent": 500, "treasury": 90, "recover": 0.2, "power": 8}[task], H=H)
    S = np.abs(rng.normal(1000, 400, size=(5, 2, H + 1, 20))).round()
    S[..., SC_TAX] = rng.integers(0, 21, size=S.shape[:-1])
    S[..., 0, :] = S[0, 0, 0, :]                                    # one start state
    assert np.array_equal(A.joined_margin(inst, S[0, 0, :1], S), A.task_margin(inst, S))
    assert np.array_equal(A.stats_margin(inst, A.traj_stats(A.join_prefix(S[0, 0, :1], S))),
                          A.stats_margin(inst, A.traj_stats(S)))
    real = S[1, 0]
    assert np.array_equal(A.joined_margin(inst, real, real[-1:][None]), A.task_margin(inst, real[None]))


# ----------------------------------------------------------------------------------------------
# The controller on a stub engine
# ----------------------------------------------------------------------------------------------
class StubWorld:
    """A city whose funds stay at 10,000 and whose population starts at 1,000 and changes each month by
    10 (tax - 7) + round(30 N(0, 1)), the noise drawn from (seed, month); a continued replay draws months < t from the
    realised seed and months >= t from the sample's seed. Proposals: uniform random plans seeded by instance and month."""

    workers = 0

    def __init__(self, noise=30.0, break_prefix=False):
        self.noise, self.break_prefix = noise, break_prefix
        self.cont_calls = []
        self.jobs = {"gen": 0, "cont": 0}
        self.cm = 0

    def _traj(self, eff, seed_of_month):
        Hh = eff.shape[0]
        s = np.zeros((Hh + 1, 20), dtype=np.int64)
        s[:, SC_FUNDS] = 10000
        s[:, SC_TAX] = 7
        s[0, SC_POP] = 1000
        for m in range(Hh):
            z = np.random.default_rng([int(seed_of_month(m)), m]).standard_normal()
            s[m + 1, SC_POP] = s[m, SC_POP] + 10 * (int(eff[m, 0]) - 7) + int(round(self.noise * z))
        return s

    def continued(self, inst, eff_plans, t, seed_real, seeds):
        P = np.asarray(eff_plans).reshape(-1, inst.horizon, N_COLS)
        sd = np.broadcast_to(np.asarray(seeds, dtype=np.int64), (P.shape[0],))
        self.cont_calls.append((int(t), int(seed_real), sd.copy()))
        self.jobs["cont"] += P.shape[0]
        self.cm += P.shape[0] * inst.horizon
        out = np.stack([self._traj(p, (lambda m, s=int(s): int(seed_real) if m < t else s)) for p, s in zip(P, sd)])
        if self.break_prefix and t > 0:
            out[:, 1, SC_POP] += 1
        return out

    def scalars(self, inst, eff_plans, seeds, key_sink=None, store=True):
        return self.continued(inst, eff_plans, 0, 0, seeds)

    def realised(self, inst, eff_prefix, seed_real, want_state=True):
        t = eff_prefix.shape[0]
        full = np.zeros((inst.horizon, N_COLS), dtype=np.int16)
        full[:t] = eff_prefix
        pre = self._traj(full, lambda m: seed_real)[:t + 1]
        return RP.Realised(t, np.asarray(eff_prefix), int(seed_real), pre, int(pre[-1, SC_POP]) if want_state else None,
                           None)

    def proposals(self, inst, eff_prefix, seed_real, n, reserved, seed_stream=None):
        t = eff_prefix.shape[0]
        rng = np.random.default_rng(seed_for(*RP.salted(("stub-gen", inst.key, t), seed_stream)))
        P = np.stack([random_plan(rng, inst.horizon - t) for _ in range(n)]).astype(np.int16)
        P[..., A.FORCED_COL] = 0
        self.jobs["gen"] += n
        return P, ["stub"] * n

    def counters(self):
        return {"jobs": dict(self.jobs), "jobs_remote": 0, "engine_city_months": self.cm, "engine_seconds": 0.0}


class PerfectModel:
    """Knows the realised future: its samples are the world on the realised seed throughout."""

    name = "perfect-stub"

    def __init__(self, world):
        self.world, self.ms = world, 0

    def score_samples(self, inst, eff_full, real, K, stream):
        tr = self.world.continued(inst, eff_full, 0, 0, real.seed_real).astype(np.float64)
        self.ms += eff_full.shape[0] * K * (inst.horizon - real.t)
        return A.join_prefix(real.prefix, np.repeat(tr[:, None, real.t:], K, axis=1))

    def verdict_samples(self, inst, eff_full, K, stream):
        tr = self.world.scalars(inst, eff_full, A.oracle_seed_list(inst, 32)[0]).astype(np.float64)
        self.ms += eff_full.shape[0] * K * inst.horizon
        return np.repeat(tr[:, None], K, axis=1)

    def paired_samples(self, inst, eff_full, real, K):
        return self.score_samples(inst, eff_full, real, K, ())

    def counters(self):
        return {"judge_month_steps": self.ms}

    def describe(self):
        return {"model": self.name}


class StubEmuJudge(A.SamplingJudge):
    """An 'emulator': population from its start state, each month + 10 (tax - 7) + 40 N(0, 1) seeded by the stream;
    its row 0 reads the start state wrongly (funds -10^9), which the join must drop."""

    name = "stub-emulator"

    def __init__(self):
        super().__init__()
        self._override = None
        self.starts = []

    def state0(self, inst):
        return self._override if self._override is not None else {"pop": 1000}

    def state_of(self, obs, ledger_row):
        return {"pop": int(obs)}

    def samples_from(self, inst, P, K, stream, state):
        self._override = state
        try:
            return self.samples(inst, P, K, stream)
        finally:
            self._override = None

    def _samples(self, inst, P, K, stream):
        st = self.state0(inst)
        self.starts.append(st["pop"])
        rng = np.random.default_rng(seed_for("stub-emu", inst.start_id, *stream))
        n, Hh = P.shape[0], P.shape[1]
        s = np.zeros((n, K, Hh + 1, 20))
        s[..., SC_FUNDS] = 10000
        s[..., SC_TAX] = 7
        s[..., 0, SC_FUNDS] = -1e9
        s[..., 0, SC_POP] = st["pop"]
        step = 10 * (P[:, None, :, 0].astype(float) - 7) + 40 * rng.standard_normal((n, K, Hh))
        s[..., 1:, SC_POP] = st["pop"] + np.cumsum(step, axis=-1)
        return s


def _stub_instances(n=3):
    out = []
    for k, (task, theta, sd) in enumerate([("grow", 1100, 100), ("recover", 1.1, 0.1), ("grow", 1000, 100),
                                           ("recover", 1.0, 0.1)][:n]):
        s = f"s{k}"
        out.append(A.Instance(f"{s}|{task}|H{H}", s, f"fam-{s}", task, H, float(theta), float(sd), True,
                              f"/nonexistent/{s}.cty"))
    return out


def _strip(recs):
    return [json.dumps({k: v for k, v in r.items() if k not in ("seconds", "host")}, sort_keys=True) for r in recs]


@pytest.mark.parametrize("version", [1, 2, 3])
def test_perfect_model_realised_outcome_equals_its_prediction(version):
    w = StubWorld()
    for inst in _stub_instances():
        rec = RP.replan_instance(inst, PerfectModel(w), w, n_plans=6, controller_version=version)
        last = rec["months"][-1]
        pred = last["best_score"] if version < 3 else \
            last["pair_challenger_margins" if last["switched"] else "pair_incumbent_margins"][0]
        assert rec["replan"]["margin"] == pred and rec["replan"]["pass"] == (pred >= 0)
        if version == 3:     # the perfect model's paired differences are exact: switch exactly when the challenger is better
            assert all(m["switched"] == (m["pair_d_mean"] > 0) for m in rec["months"][1:])
        assert rec["month0"]["verdict_margins"] == [rec["open_loop"]["margin"]] * 8
        assert rec["accept0"] == rec["open_loop_pass"] and rec["model"] == "perfect-stub"
        assert len(rec["executed"]) == H and rec["n_plans"] == 6


def test_zero_replans_reproduce_the_open_loop_arm():
    w = StubWorld()
    model = RP.EngineModel(w, 32)
    for inst in _stub_instances():
        rec = RP.replan_instance(inst, model, w, n_plans=5, replan_at=(0,))
        assert rec["executed"] == rec["month0"]["plan"]
        assert rec["replan"]["margin"] == rec["open_loop"]["margin"]
        assert rec["replan_pass"] == rec["open_loop_pass"]
        assert [m["best_index"] is None for m in rec["months"]] == [False] + [True] * (H - 1)
        full = RP.replan_instance(inst, model, w, n_plans=5)
        assert full["month0"] == rec["month0"] and full["open_loop"] == rec["open_loop"]


def test_engine_model_continues_from_the_realised_months_on_fresh_seeds():
    w = StubWorld()
    inst = _stub_instances(1)[0]
    rec = RP.replan_instance(inst, RP.EngineModel(w, 32), w, n_plans=4, controller_version=2)
    real = A.oracle_seed_list(inst, 32)[0]
    reserved = A.reserved_seeds(inst.start_id, H, 32)
    scoring = [c for c in w.cont_calls if c[0] > 0]
    assert len(scoring) == H - 1 and all(c[1] == real for c in scoring)
    assert all(not (set(c[2].tolist()) & reserved) for c in scoring)     # never the realised (or any oracle) seed
    assert rec["counts"]["model_month_steps"] == (4 * A.K_SEARCH * H) * H + A.K_VERDICT * H
    with pytest.raises(RuntimeError):
        RP.replan_instance(inst, RP.EngineModel(StubWorld(break_prefix=True), 32), StubWorld(break_prefix=True),
                           n_plans=4)


def test_v3_engine_pairs_share_seeds_disjoint_from_the_screen_and_the_realised_seed():
    w = StubWorld()
    inst = _stub_instances(1)[0]
    rec = RP.replan_instance(inst, RP.EngineModel(w, 32), w, n_plans=4, controller_version=3)
    reserved = A.reserved_seeds(inst.start_id, H, 32)
    later = [c for c in w.cont_calls if c[0] > 0]
    screens, pairs = later[0::2], later[1::2]                 # each month: the screen, then the pair
    assert len(screens) == len(pairs) == H - 1
    for sc, pr in zip(screens, pairs):
        assert len(sc[2]) == 3 * A.K_SEARCH and len(pr[2]) == 2 * RP.PAIRED_SAMPLES
        k = RP.PAIRED_SAMPLES
        assert list(pr[2][:k]) == list(pr[2][k:])            # the same seeds for incumbent and challenger
        assert not (set(pr[2].tolist()) & (set(sc[2].tolist()) | reserved))
    c = rec["counts"]
    assert c["paired_model_month_steps"] == sum(2 * RP.PAIRED_SAMPLES * (H - t) for t in range(1, H))
    assert c["paired_engine_city_months"] == (H - 1) * 2 * RP.PAIRED_SAMPLES * H
    assert c["model_month_steps"] == (4 * A.K_SEARCH * H + (H - 1) * (3 * A.K_SEARCH * H + 2 * RP.PAIRED_SAMPLES * H)
                                      + A.K_VERDICT * H)
    assert rec["incumbent_kept_months"] == sum(1 for m in rec["months"][1:] if not m["switched"])


def test_emulator_model_starts_from_the_real_state_and_drops_its_row0():
    w = StubWorld()
    inst = _stub_instances(1)[0]
    J = StubEmuJudge()
    rec = RP.replan_instance(inst, RP.EmulatorModel(J), w, n_plans=4, controller_version=2)
    # month 0 from state0, month t from the realised population at t (score calls), then the verdict from state0
    pops = [m["realised_pop"] for m in rec["months"]]
    assert J.starts[:H] == pops and J.starts[H] == 1000
    assert all(m["best_score"] > -1000 for m in rec["months"])            # funds -1e9 in row 0 never entered a margin
    assert rec["counts"]["model_month_steps"] == sum(4 * A.K_SEARCH * (H - t) for t in range(H)) + A.K_VERDICT * H


def test_v3_emulator_pairs_draw_common_noise_from_the_real_state():
    """The paired rollouts are two calls of their own with one stream (the same torch seed and batch shape): the stub
    emulator's noise is then common to both plans, so the 8 differences are equal and their standard error is zero;
    the screen's calls are those of a run without pairs. (recover: the margin is linear in the population at H.)"""
    w = StubWorld()
    inst = _stub_instances(2)[1]
    J = StubEmuJudge()
    rec = RP.replan_instance(inst, RP.EmulatorModel(J), w, n_plans=4, controller_version=3)
    pops = [m["realised_pop"] for m in rec["months"]]
    assert J.starts[0] == 1000 and J.starts[1:1 + 3 * (H - 1):3] == pops[1:]        # screen, incumbent, challenger
    assert J.starts[2::3][:H - 1] == pops[1:] and J.starts[3::3][:H - 1] == pops[1:]
    assert all(m["pair_d_se"] < 1e-9 for m in rec["months"][1:])
    assert rec["counts"]["model_month_steps"] == (4 * A.K_SEARCH * H + sum((3 * A.K_SEARCH + 2 * RP.PAIRED_SAMPLES)
                                                                         * (H - t) for t in range(1, H)) + A.K_VERDICT * H)


class TieModel:
    """Every candidate gets the same samples (the realised months, then the state at month t held), so all scores tie;
    ``prefer`` = (month, index): at that month that candidate's population at H is raised, a strict preference (the
    recover margin rises with the population at H)."""

    name = "tie-stub"

    def __init__(self, prefer=None):
        self.prefer, self.ms = prefer, 0

    def score_samples(self, inst, eff_full, real, K, stream):
        n = eff_full.shape[0]
        suf = np.repeat(real.prefix[-1][None].astype(np.float64), inst.horizon - real.t + 1, axis=0)
        S = np.broadcast_to(suf, (n, K) + suf.shape).copy()
        if self.prefer is not None and real.t == self.prefer[0]:
            S[self.prefer[1], :, -1, SC_POP] += 500
        self.ms += n * K * (inst.horizon - real.t)
        return A.join_prefix(real.prefix, S)

    def paired_samples(self, inst, eff_full, real, K):
        """Incumbent (row 0) and challenger (row 1) tie, except that at the preferred month the challenger's population at
        H is raised."""
        suf = np.repeat(real.prefix[-1][None].astype(np.float64), inst.horizon - real.t + 1, axis=0)
        S = np.broadcast_to(suf, (eff_full.shape[0], K) + suf.shape).copy()
        if self.prefer is not None and real.t == self.prefer[0]:
            S[1, :, -1, SC_POP] += 500
        return A.join_prefix(real.prefix, S)

    def verdict_samples(self, inst, eff_full, K, stream):
        s = np.zeros((eff_full.shape[0], K, inst.horizon + 1, 20))
        s[..., SC_FUNDS], s[..., SC_POP] = 10000, 1000
        return s

    def counters(self):
        return {"judge_month_steps": self.ms}

    def describe(self):
        return {"model": self.name}


def test_v2_ties_execute_the_month0_choice_in_full():
    w = StubWorld()
    inst = _stub_instances(2)[1]
    rec = RP.replan_instance(inst, TieModel(), w, n_plans=5, controller_version=2)
    assert rec["controller_version"] == 2
    assert rec["executed"] == rec["month0"]["plan"]
    assert rec["replan"]["margin"] == rec["open_loop"]["margin"] and rec["replan_pass"] == rec["open_loop_pass"]
    assert [m["incumbent_kept"] for m in rec["months"]] == [None] + [True] * (H - 1)
    assert rec["incumbent_kept_months"] == H - 1 and all(m["best_index"] == 0 for m in rec["months"])
    assert [m["label"] for m in rec["months"][1:]] == ["incumbent"] * (H - 1)
    v1 = RP.replan_instance(inst, TieModel(), w, n_plans=5, controller_version=1)
    assert v1["month0"] == rec["month0"] and v1["controller_version"] == 1
    assert all(m["incumbent_kept"] is None for m in v1["months"]) and v1["incumbent_kept_months"] == 0
    assert v1["executed"] != rec["executed"]          # version 1 executes the first month of a new draw each month


def test_v2_switches_at_the_preferred_month_and_carries_the_new_plan():
    w = StubWorld()
    inst = _stub_instances(2)[1]
    k, j, n = 6, 3, 5
    rec = RP.replan_instance(inst, TieModel(prefer=(k, j)), w, n_plans=n, controller_version=2)
    kept = [m["incumbent_kept"] for m in rec["months"]]
    assert kept == [None] + [True] * (k - 1) + [False] + [True] * (H - k - 1)
    assert rec["months"][k]["best_index"] == j and rec["months"][k]["label"] == "stub"
    ex = np.asarray(rec["executed"])
    assert np.array_equal(ex[:k], np.asarray(rec["month0"]["plan"])[:k])
    eff_prefix = A.effective(np.concatenate([ex[:k], np.zeros((H - k, N_COLS), dtype=np.int64)])[None], inst.task, H)[0, :k]
    fresh, _ = StubWorld().proposals(inst, eff_prefix, rec["realised_seed"], n - 1, None)
    assert np.array_equal(ex[k:], fresh[j - 1])        # fresh draw j - 1 sits at index j; its remainder runs to the end
    assert w.jobs["gen"] == n + (n - 1) * (H - 1)       # month 0: n fresh draws; later months: n - 1 and the incumbent


def test_switch_rule():
    sw = RP.switch_rule
    assert RP.PAIRED_SAMPLES == A.K_VERDICT == 8 and RP.SWITCH_STANDARD_ERRORS == 2.0
    assert sw([0.3] * 8) == (True, 0.3, 0.0)                      # equal differences: zero standard error, mean > 0
    assert sw([-0.3] * 8) == (False, -0.3, 0.0)
    assert sw([0.0] * 8)[0] is False                              # ties keep the incumbent
    rng = np.random.default_rng(0)
    assert sw(1.0 + 0.1 * rng.standard_normal(8))[0]              # a clear improvement switches
    d = np.array([1.0, -1.0] * 4)                                 # mean 0: never above two standard errors
    assert sw(d) == (False, 0.0, pytest.approx(float(np.std(d, ddof=1) / np.sqrt(8))))
    d = np.array([0.0] * 7 + [8.0])                               # mean 1, se 1: 1 > 2 fails; the bar is strict
    assert sw(d)[0] is False and sw(d)[2] == pytest.approx(1.0)
    noise = np.random.default_rng(12345).standard_normal((4000, 8))
    rate = np.mean([sw(x)[0] for x in noise])                     # zero true difference: P(t_7 > 2) is about 0.04
    assert rate < 0.06
    with pytest.raises(ValueError):
        sw([1.0])


def test_v3_ties_keep_the_incumbent_and_a_clear_improvement_switches():
    w = StubWorld()
    inst = _stub_instances(2)[1]
    rec = RP.replan_instance(inst, TieModel(), w, n_plans=5, controller_version=3)
    assert rec["executed"] == rec["month0"]["plan"] and rec["replan"]["margin"] == rec["open_loop"]["margin"]
    assert rec["incumbent_kept_months"] == H - 1 and not any(m["switched"] for m in rec["months"][1:])
    assert all(m["label"] == "incumbent" and m["pair_d_se"] == 0.0 for m in rec["months"][1:])
    k, j, n = 6, 2, 5
    rec = RP.replan_instance(inst, TieModel(prefer=(k, j)), w, n_plans=n, controller_version=3)
    assert [m["switched"] for m in rec["months"][1:]] == [False] * (k - 1) + [True] + [False] * (H - k - 1)
    mk = rec["months"][k]
    assert mk["challenger_index"] == j and mk["pair_d_mean"] > 0 and mk["label"] == mk["challenger_label"] == "stub"
    ex = np.asarray(rec["executed"])
    assert np.array_equal(ex[:k], np.asarray(rec["month0"]["plan"])[:k])
    eff_prefix = A.effective(np.concatenate([ex[:k], np.zeros((H - k, N_COLS), dtype=np.int64)])[None], inst.task, H)[0, :k]
    fresh, _ = StubWorld().proposals(inst, eff_prefix, rec["realised_seed"], n - 1, None)
    assert np.array_equal(ex[k:], fresh[j])            # version 3's screen holds fresh draws only: draw j at index j
    assert rec["incumbent_kept_months"] == H - 2


def test_v3_month0_is_version_2s_on_a_dry_run_instance():
    """Month 0 of version 3 is version 2's bit for bit: the version-2 dry run's first record (50 plans) against a
    version-3 run of the same instance (month-0 plan hash, verdict margins, the open-loop arm and its oracle)."""
    import run_replan as R
    d = A.REPO / "results" / "replan" / "dryrun_v2" / "engine"
    if not (d / "records.jsonl.gz").exists():
        pytest.skip("no version-2 dry run")
    r2 = R.read_records(d)[0]
    inst = R.load_order(R.ORDER, R.TASKS)[r2["order_index"]]
    world = RP.EngineWorld(RP.JobPool(0))
    r3 = RP.replan_instance(inst, RP.EngineModel(world, 32), world, n_plans=r2["n_plans"], controller_version=3)
    assert r3["month0"] == r2["month0"] and r3["month0"]["plan_hash"] == r2["month0"]["plan_hash"]
    assert r3["open_loop"] == r2["open_loop"] and r3["accept0"] == r2["accept0"]
    assert r3["months"][0] == {k: v for k, v in r2["months"][0].items()}
    assert r3["controller_version"] == 3 and r2["controller_version"] == 2


def _strip_run(r):
    """A record without the run's clock, host, order position and remote share."""
    d = {k: v for k, v in r.items() if k not in ("seconds", "host", "device_name", "order_index")}
    d["counts"] = {k: v for k, v in r["counts"].items() if k != "engine_jobs_remote"}
    return json.dumps(d, sort_keys=True)


@pytest.mark.skipif(not __import__("os").environ.get("WM2_REPLAN_SLOW"), reason="about 10 minutes on 4 local cores: "
                    "set WM2_REPLAN_SLOW=1")
def test_v3_default_path_reproduces_the_engine_run():
    """Without a seed stream, version 3 reproduces the first two records of results/replan/engine (the host-b run,
    1,000 plans) and of results/replan/dryrun_v3 bit for bit, apart from the clock and the host."""
    import run_replan as R
    ref = {d: R.read_records(A.REPO / "results" / "replan" / d)[:2] for d in ("engine", "dryrun_v3/engine")}
    if any(len(v) < 2 for v in ref.values()):
        pytest.skip("reference records missing")
    order = R.load_order(R.ORDER, R.TASKS)
    pool = RP.JobPool(4)
    world = RP.EngineWorld(pool)
    try:
        for i in range(2):
            r0 = ref["engine"][i]
            rec = RP.replan_instance(order[r0["order_index"]], RP.EngineModel(world, 32), world, n_plans=r0["n_plans"])
            assert "seed_stream" not in rec
            for d, rs in ref.items():
                assert _strip_run(rec) == _strip_run(rs[i]), d
    finally:
        pool.close()


def test_v2_reproduces_its_dry_run_records():
    import run_replan as R
    d = A.REPO / "results" / "replan" / "dryrun_v2" / "engine"
    if not (d / "records.jsonl.gz").exists():
        pytest.skip("no version-2 dry run")
    order = R.load_order(R.ORDER, R.TASKS)
    world = RP.EngineWorld(RP.JobPool(0))
    model = RP.EngineModel(world, 32)
    for r in R.read_records(d):
        rec = RP.replan_instance(order[r["order_index"]], model, world, n_plans=r["n_plans"], controller_version=2)
        assert _strip_run(rec) == _strip_run(r)


def test_seed_stream_keys_and_proposal_seeds():
    key, reserved = "sX|grow|H24", A.reserved_seeds("sX", H, 32)
    assert RP.salted(("a", 1)) == ("a", 1) and RP.salted(("a", 1), "fresh1") == ("a", 1, "seed-stream", "fresh1")
    for t in (0, 7):
        g0, p0 = RP.proposal_seeds(key, t, 6, reserved)          # the default: exactly the seeds of every earlier run
        assert g0 == [A.fresh_seed(("replan-gen", key, t, j), reserved)[0] for j in range(6)]
        assert p0 == [seed_for("replan-policy", key, t, j) for j in range(6)]
        g1, p1 = RP.proposal_seeds(key, t, 6, reserved, "fresh1")
        assert RP.proposal_seeds(key, t, 6, reserved, "fresh1") == (g1, p1)
        assert not set(g1) & set(g0) and not set(p1) & set(p0) and not set(g1) & reserved


def test_seed_stream_run_on_stubs(tmp_path):
    import run_replan as R
    inst = _stub_instances(1)[0]
    real = A.oracle_seed_list(inst, 32)[0]
    reserved = A.reserved_seeds(inst.start_id, H, 32) | {real}
    runs = {}
    for name in ("fresh1", "fresh1-again", None):
        w = StubWorld()
        rec = RP.replan_instance(inst, RP.EngineModel(w, 32), w, n_plans=4,
                                 seed_stream="fresh1" if name else None)
        runs[name] = (rec, w)
    a, wa = runs["fresh1"]
    b, _ = runs["fresh1-again"]
    d, wd = runs[None]
    assert _strip([a]) == _strip([b])                            # the same name: the same run
    assert a["seed_stream"] == "fresh1" and "seed_stream" not in d
    assert a["realised_seed"] == d["realised_seed"] == real
    assert a["month0"]["plan"] != d["month0"]["plan"]
    oracle = set(A.oracle_seed_list(inst, 32))
    derived = [c for c in wa.cont_calls if not set(c[2].tolist()) <= oracle]    # screens, pairs, the verdict
    derived_d = [c for c in wd.cont_calls if not set(c[2].tolist()) <= oracle]
    assert not (set(derived[0][2].tolist()) & set(derived_d[0][2].tolist()))       # month 0's screen seeds
    assert not (set(derived[-1][2].tolist()) & set(derived_d[-1][2].tolist()))     # the verdict's seeds
    assert len(derived) == 1 + 2 * (H - 1) + 1
    assert all(not (set(c[2].tolist()) & reserved) for c in derived)
    for c in wa.cont_calls:
        if set(c[2].tolist()) <= oracle:
            assert c[0] == 0                                     # the realised and oracle replays: plain, default seeds
    out = tmp_path / "s"
    out.mkdir()
    R.run_instances([(0, inst)], RP.EngineModel(StubWorld(), 32), StubWorld(), out, 4, 32, log=lambda s: None,
                    seed_stream="fresh1")
    assert R.read_records(out)[0]["seed_stream"] == "fresh1"
    with pytest.raises(SystemExit):                              # another stream (or none) refuses the directory
        R.run_instances([(1, _stub_instances(2)[1])], RP.EngineModel(StubWorld(), 32), StubWorld(), out, 4, 32,
                        log=lambda s: None)
    (tmp_path / "config.json").write_text(json.dumps({"design": {"seed_stream": "fresh1"}, "invocations": []}))
    R.check_seed_stream(tmp_path, "fresh1")
    with pytest.raises(SystemExit):
        R.check_seed_stream(tmp_path, None)


def test_seed_stream_month0_proposals_differ_on_the_engine():
    inst = _real_instances()[0]
    world = RP.EngineWorld(RP.JobPool(0))
    real = A.oracle_seed_list(inst, 32)[0]
    res = A.reserved_seeds(inst.start_id, H, 32)
    p0, _ = world.proposals(inst, np.zeros((0, N_COLS), np.int16), real, 3, res)
    p1, _ = world.proposals(inst, np.zeros((0, N_COLS), np.int16), real, 3, res, seed_stream="fresh1")
    p1b, _ = world.proposals(inst, np.zeros((0, N_COLS), np.int16), real, 3, res, seed_stream="fresh1")
    assert np.array_equal(p1, p1b) and not np.array_equal(p0, p1)        # (a no-op draw can recur in both)


def _control_recs(rp, ol, tasks):
    out = {}
    for i, (a, b, t) in enumerate(zip(rp, ol, tasks)):
        k = f"c{i // 2}|{t}|H24"
        out[k] = {"instance": k, "cluster": f"c{i // 2}", "task": t, "order_index": i, "replan_pass": bool(a),
                  "open_loop_pass": bool(b), "accept0": False, "controller_version": 3, "incumbent_kept_months": 20}
    return out


def test_replan_control_gate_and_family_bar():
    import replan_control as RC
    tasks = [T.TASKS[i % 5] for i in range(40)]
    g = np.array([t == "grow" for t in tasks])
    # grow wholly below zero (replanning fails where open loop passes), every other family identical
    res = RC.control(_control_recs(~g & (np.arange(40) % 3 == 0), np.ones(40, bool) & (g | (np.arange(40) % 3 == 0)),
                                   tasks), n_boot=400)
    assert res["family_bar_fails"] and res["families_below_zero"] == ["grow"]
    assert res["by_family"]["grow"]["hi"] < 0 and not res["enters_paper_if_complete_and_reviewed"]
    # no family below zero: replanning equals open loop everywhere
    res = RC.control(_control_recs(np.arange(40) % 2 == 0, np.arange(40) % 2 == 0, tasks), n_boot=400)
    assert not res["family_bar_fails"] and not res["gate_fails"] and res["families_below_zero"] == []
    # the pooled gate: replanning fails wherever open loop passes
    res = RC.control(_control_recs(np.zeros(40, bool), np.ones(40, bool), tasks), n_boot=400)
    assert res["gate_fails"] and res["pooled"]["hi"] < 0
    assert "Family bar" in RC.render(res)


def test_controller_version_of_a_directory(tmp_path):
    import run_replan as R
    (tmp_path / "config.json").write_text(json.dumps({"design": {"n_plans": 5}, "invocations": []}))
    R.check_controller_version(tmp_path, 1)             # a directory from before the field existed is version 1
    with pytest.raises(SystemExit):
        R.check_controller_version(tmp_path, 2)
    (tmp_path / "config.json").write_text(json.dumps({"design": {"controller_version": 2}, "invocations": []}))
    R.check_controller_version(tmp_path, 2)
    with pytest.raises(SystemExit):
        R.check_controller_version(tmp_path, 1)


def _v1_strip(r):
    """A record without the fields version 2 added and without the run's clock and host."""
    d = {k: v for k, v in r.items() if k not in ("controller_version", "incumbent_kept_months", "seconds", "host",
                                                "device_name", "order_index")}
    d["months"] = [{k: v for k, v in m.items() if k != "incumbent_kept"} for m in r["months"]]
    d["counts"] = {k: v for k, v in r["counts"].items() if k != "engine_jobs_remote"}
    return json.dumps(d, sort_keys=True)


def test_version1_reproduces_the_dry_run_records():
    """``controller_version=1`` gives the version-1 dry run's engine records (results/replan/dryrun/engine, 50 plans)
    exactly, apart from the new fields."""
    import run_replan as R
    d = A.REPO / "results" / "replan" / "dryrun" / "engine"
    if not (d / "records.jsonl.gz").exists():
        pytest.skip("no version-1 dry run")
    ref = R.read_records(d)
    order = R.load_order(R.ORDER, R.TASKS)
    world = RP.EngineWorld(RP.JobPool(0))
    model = RP.EngineModel(world, 32)
    for r in ref:
        rec = RP.replan_instance(order[r["order_index"]], model, world, n_plans=r["n_plans"], controller_version=1)
        assert _v1_strip(rec) == _v1_strip(r)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_resumption_and_determinism(tmp_path, version):
    import run_replan as R
    insts = _stub_instances(3)
    todo = list(enumerate(insts))

    def run(out, crash_after=None):
        w = StubWorld()
        return R.run_instances(todo, RP.EngineModel(w, 32), w, out, 5, 32, crash_after=crash_after, log=lambda s: None,
                               controller_version=version)

    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    assert run(a) == 3
    with pytest.raises(RuntimeError):
        run(b, crash_after=1)
    assert len(R.read_records(b)) == 1
    assert run(b) == 2                                 # the finished instance is not recomputed
    assert run(b) == 0
    assert _strip(R.read_records(a)) == _strip(R.read_records(b))
    c = tmp_path / "c"
    c.mkdir()
    run(c)
    assert _strip(R.read_records(a)) == _strip(R.read_records(c))
    assert [r["order_index"] for r in R.read_records(a)] == [0, 1, 2]
    assert {r["controller_version"] for r in R.read_records(a)} == {version}
    # a directory holds one controller version: the other version refuses to resume into it
    with pytest.raises(SystemExit):
        R.run_instances(todo, RP.EngineModel(StubWorld(), 32), StubWorld(), a, 5, 32, log=lambda s: None,
                        controller_version=version % 3 + 1)
    p = R.project(a, 50, first=2)
    assert p["records"] == 2 and p["order_positions"] == [0, 1] and p["plans_projected"] == 50
    # 5 plans measured, 50 projected: the replans' rollout month-steps scale by 10, the verdict's do not
    assert version == 3 or p["per_instance"]["model_month_steps"] == pytest.approx(10 * 5 * A.K_SEARCH * sum(H - t for t in range(H))
                                                                   + A.K_VERDICT * H)


# ----------------------------------------------------------------------------------------------
# The real engine
# ----------------------------------------------------------------------------------------------
def _real_instances():
    import run_replan as R
    if not CAL.exists():
        pytest.skip("calibration files not present")
    return R.load_order(R.ORDER, R.TASKS)


def test_prefix_engine_is_the_replay_and_continuation_reseeds():
    from dc.engine import Engine
    from dc.oracle import replay
    inst = [i for i in _real_instances() if i.task == "recover"][0]
    eff = A.effective(A.Pools(H).behaviour(inst.start_id)[:1], inst.task, H)[0]
    acts, forced = compile_plan(eff)
    s, s2, t = seed_for("t-real", 1), seed_for("t-real", 2), 5
    eng = Engine()
    rp = replay(eng, inst.cty, acts, s, forced=forced, want_hash=True)
    e2 = Engine()
    head, rest = RP.split_forced(forced, t)
    assert head == {0: T.RECOVER_DISASTER} and rest == {}
    pe = RP.PrefixEngine(e2, acts[:t], head, s)
    pe.load_start(inst.cty)
    assert np.array_equal(pe.prefix_scalars, rp.scalars[:t + 1])
    assert e2.hash_full() == rp.hashes[t]
    for m in range(t, H):              # without a reseed the engine goes on exactly as the replay (generator included)
        e2.apply(acts[m])
        e2.step_month()
        assert e2.hash_full() == rp.hashes[m + 1]
    c0 = RP.continued(eng, inst.cty, eff, 0, 123, s)
    assert np.array_equal(c0, rp.scalars)
    assert np.frombuffer(A._replay_job((inst.cty, eff.tobytes(), H, s)), dtype="<i8").reshape(H + 1, 20).tolist() == c0.tolist()
    ct = RP.continued(eng, inst.cty, eff, t, s, s2)
    assert np.array_equal(ct[:t + 1], rp.scalars[:t + 1])
    assert np.array_equal(ct, RP.continued(Engine(), inst.cty, eff, t, s, s2))
    assert not np.array_equal(ct, rp.scalars)          # the reseed changes the remaining months of this city


def test_month0_proposals_are_the_logged_plans():
    """The proposal generator at month 0 with the logged plans' seeds reproduces the calibration file's plans."""
    from dc.engine import Engine
    eng = Engine()
    for inst in _real_instances()[:2]:
        beh = A.Pools(H).behaviour(inst.start_id)
        for j in range(2):
            plan, _ = RP.gen_plan(eng, inst.cty, np.zeros((0, N_COLS), np.int16), H, 1,
                                  seed_for("cal-gen", inst.start_id, H, j), seed_for("cal-policy", inst.start_id, H, j))
            assert np.array_equal(plan, beh[j])
    inst = _real_instances()[3]
    eff = A.effective(A.Pools(H).behaviour(inst.start_id)[:1], inst.task, H)[0]
    plan, _ = RP.gen_plan(eng, inst.cty, eff[:7], H, A.oracle_seed_list(inst, 32)[0], 11, 12)
    assert plan.shape == (H - 7, N_COLS) and (plan[:, A.FORCED_COL] == 0).all()


def test_job_server_over_a_pipe_identical():
    import os
    inst = _real_instances()[1]
    cmd = ["env", f"PYTHONPATH={A.REPO / 'code'}", sys.executable, "-m", "dc.replan", "serve", "--workers", "1"]
    remote = A.RemotePool(cmd, 1)
    pool = RP.JobPool(0, remote=remote)
    info = RP.check_remote(pool, inst)
    assert info["identical_jobs"] == 9
    world = RP.EngineWorld(pool)
    s_real = A.oracle_seed_list(inst, 32)[0]
    eff = A.effective(A.Pools(H).behaviour(inst.start_id)[:4], inst.task, H)
    got = world.continued(inst, eff, 3, s_real, [seed_for("p", j) for j in range(4)])
    assert pool.n_remote > 0
    pool.close()
    ref = RP.EngineWorld(RP.JobPool(0))
    assert np.array_equal(got, ref.continued(inst, eff, 3, s_real, [seed_for("p", j) for j in range(4)]))
    assert os.path.isabs(inst.cty)


def test_state_of_month0_equals_the_audits_start_state():
    import torch
    from dc import train as Tr
    inst = _real_instances()[3]
    J = object.__new__(RP._emulator_judge_class())
    J._tr, J.device, J._s0, J._eng = Tr, torch.device("cpu"), {}, None
    s0 = J.state0(inst)
    world = RP.EngineWorld(RP.JobPool(0))
    real = world.realised(inst, np.zeros((0, N_COLS), np.int16), A.oracle_seed_list(inst, 32)[0])
    s = J.state_of(real.obs, real.ledger)
    assert set(s) == set(s0) and all(torch.equal(s[k], s0[k]) for k in s0)
    r5 = world.realised(inst, A.effective(A.Pools(H).behaviour(inst.start_id)[:1], inst.task, H)[0, :5],
                        A.oracle_seed_list(inst, 32)[0])
    s5 = J.state_of(r5.obs, r5.ledger)
    assert torch.equal(s5["scalars"][0].double(), torch.from_numpy(r5.prefix[-1]).double().float().double())


def test_replan_end_to_end_tiny_emulator_cpu(tmp_path):
    """The controller with the real engine and ``ReplanEmulatorJudge`` (a tiny untrained model of the ladder-v2 code
    on CPU, as test_audit's tiny-model test): records complete, the realised trajectory the executed plan's replay."""
    import subprocess
    import importlib
    import torch
    from dc.oracle import replay
    from dc.engine import Engine
    sha = subprocess.run(["git", "-C", str(A.REPO), "rev-parse", "ladder-v2^{commit}"], capture_output=True,
                         text=True).stdout.strip()
    if not sha:
        pytest.skip("tag ladder-v2 not present")
    pkg, _ = A.code_package("ladder-v2")
    M = importlib.import_module(pkg.__name__ + ".model")
    m = M.Emulator(M.SIZES["tiny"])
    ck = tmp_path / "tiny.pt"
    torch.save({"model_config": m.cfg.to_dict(), "model": m.state_dict(), "ema": None, "samples": 0,
                "git": {"commit": sha, "dirty_code_files": []}}, ck)
    J = RP.make_emulator_judge(str(ck), device="cpu", chunk=8, buckets=(8,), compile_trunk=False, model_src="auto")
    inst = [i for i in _real_instances() if i.task == "recover"][0]
    world = RP.EngineWorld(RP.JobPool(0))
    rec = RP.replan_instance(inst, RP.EmulatorModel(J), world, n_plans=2)
    assert rec["model"] == "emulator" and len(rec["executed"]) == H and len(rec["month0"]["verdict_margins"]) == 8
    eff = A.effective(np.asarray(rec["executed"])[None], inst.task, H)[0]
    acts, forced = compile_plan(eff)
    tr = replay(Engine(), inst.cty, acts, rec["realised_seed"], forced=forced).scalars
    assert rec["replan"]["margin"] == float(A.task_margin(inst, tr[None])[0])
    assert rec["counts"]["model_month_steps"] == (2 * A.K_SEARCH * H + sum((A.K_SEARCH + 2 * RP.PAIRED_SAMPLES) * (H - t)
                                                                           for t in range(1, H)) + A.K_VERDICT * H)
    assert rec["counts"]["engine_jobs"]["gen"] == 2 + (2 - 1) * (H - 1)      # versions 2, 3: n - 1 fresh draws from month 1
    assert rec["controller_version"] == 3 and len(rec["months"]) == H
    assert all(len(m["pair_incumbent_margins"]) == RP.PAIRED_SAMPLES for m in rec["months"][1:])


def test_order_file():
    import run_replan as R
    from dc.families import heldout_cty_of
    doc = json.loads(R.ORDER.read_text())
    order = R.load_order(R.ORDER, R.TASKS)
    assert len(order) == 100 and doc["budget_axis_check"]["same_instances"]
    for k in range(1, 21):
        fam = [i.task for i in order[:5 * k]]
        assert all(fam.count(t) == k for t in T.TASKS)
    sel = A.select_instances(A.load_instances(R.TASKS, H, cty_of=heldout_cty_of()), 100)
    assert [i.key for i in R.order_rule(sel)] == [i.key for i in order]
    assert sorted(i.key for i in sel) == sorted(i.key for i in order)


# ----------------------------------------------------------------------------------------------
# The analysis: each reading's three outcomes on synthetic records
# ----------------------------------------------------------------------------------------------
def _recs(acc, rep, ol, orc=None):
    n = len(acc)
    out = {}
    for i in range(n):
        k = f"c{i // 2}|{T.TASKS[i % 5]}|H24"
        out[k] = {"instance": k, "cluster": f"c{i // 2}", "task": T.TASKS[i % 5], "realised_seed": i, "n_plans": 10,
                  "order_index": i, "accept0": bool(acc[i]), "replan_pass": bool(rep[i]), "open_loop_pass": bool(ol[i]),
                  "open_loop": {"oracle_accept": bool(ol[i] if orc is None else orc[i])}}
    return out


N = 40
ONE, ZERO = np.ones(N, bool), np.zeros(N, bool)
ALT = np.array([(i // 2) % 2 == 0 for i in range(N)])          # half the clusters


def _analyse(e, p):
    import replan_axis as RA
    return RA.analyse(_recs(*e), _recs(*p), n_boot=400)["readings"]


@pytest.mark.parametrize("case,expect", [
    # R-a: excess false acceptance under replanning
    (("R-a", (ONE, ZERO, ZERO), (ZERO, ZERO, ZERO)), "above"),
    (("R-a", (ZERO, ZERO, ZERO), (ONE, ZERO, ZERO)), "below"),
    (("R-a", (ALT, ZERO, ZERO), (~ALT, ZERO, ZERO)), "includes_zero"),
    # R-b: replanning excess minus open-loop excess (accept everywhere; replan and open-loop outcomes differ)
    (("R-b", (ONE, ZERO, ONE), (ONE, ONE, ONE)), "above"),
    (("R-b", (ONE, ONE, ZERO), (ONE, ONE, ONE)), "below"),
    (("R-b", (ONE, ALT, ~ALT), (ONE, ONE, ONE)), "includes_zero"),
    # R-c: shortfall in real success under replanning
    (("R-c", (ZERO, ZERO, ZERO), (ZERO, ONE, ZERO)), "above"),
    (("R-c", (ZERO, ONE, ZERO), (ZERO, ZERO, ZERO)), "below"),
    (("R-c", (ZERO, ALT, ZERO), (ZERO, ~ALT, ZERO)), "includes_zero"),
    # R-d: replanning shortfall minus open-loop shortfall
    (("R-d", (ZERO, ZERO, ONE), (ZERO, ONE, ONE)), "above"),
    (("R-d", (ZERO, ONE, ZERO), (ZERO, ONE, ONE)), "below"),
    (("R-d", (ZERO, ALT, ~ALT), (ZERO, ONE, ONE)), "includes_zero"),
])
def test_readings_three_outcomes(case, expect):
    import replan_axis as RA
    r, e, p = case
    d = _analyse(e, p)[r]
    assert d["reading"] == expect
    assert d["wording"] == RA.WORDING[r][expect]
    lo, hi = d["lo"], d["hi"]
    assert (lo > 0) if expect == "above" else ((hi < 0) if expect == "below" else (lo <= 0 <= hi))
    if expect == "includes_zero" and r in ("R-a", "R-c"):
        assert d["interval_width"] == pytest.approx(hi - lo) and "evidence of absence" in d["note"]


def test_wordings_are_decision_88s():
    import replan_axis as RA
    assert RA.WORDING["R-a"]["above"] == "the excess false acceptance survives monthly replanning"
    assert RA.WORDING["R-b"]["below"] == "replanning reduces the excess"
    assert RA.WORDING["R-d"] == {"below": "replanning reduces the shortfall in real success",
                                 "includes_zero": "no change in the shortfall in real success under replanning is established",
                                 "above": "replanning increases the shortfall in real success"}
    # the analysis plan
    assert RA.WORDING["R-c"]["below"] == ("under monthly replanning the emulator's choices truly pass more often than "
                                          "a perfect emulator's") and "R-c" not in RA.WORDING_NOTE


def test_analysis_measures_and_audit_beside():
    import replan_axis as RA
    acc = ALT.copy()
    emu = _recs(acc, ZERO, ONE, orc=ZERO)
    eng = _recs(ZERO, ONE, ONE)
    audit = {"emulator": {(k, 1000): (True, False, True) for k in emu}, "engine": None}
    res = RA.analyse(emu, eng, audit, 1000, n_boot=200)
    P = res["pooled"]
    assert P["emulator"]["replan"]["false_acceptance"]["value"] == pytest.approx(0.5)
    assert P["emulator"]["open_loop"]["false_acceptance"]["value"] == 0.0
    assert P["emulator"]["open_loop_oracle"]["false_acceptance"]["value"] == pytest.approx(0.5)
    assert P["shortfall_real_success"]["replan"]["value"] == 1.0
    assert set(res["by_family"]) == set(T.TASKS) and res["by_family"]["grow"]["n_instances"] == 8
    b = res["open_loop_beside_audit"]
    assert b["emulator"]["audit_stored"]["false_acceptance"]["value"] == 1.0
    assert b["emulator"]["agreement"]["judge_accepts_same"] == int(acc.sum())
    assert b["engine"]["status"] == "no audit records given"
    assert "Readings" in RA.markdown(res, {})
    for r in emu.values():
        r["n_plans"] = 50
    with pytest.raises(SystemExit):
        RA.analyse(emu, eng, n_boot=50)
    assert RA.analyse(emu, eng, n_boot=50, allow_unequal_plans=True)["n_plans"] == {"emulator": [50], "engine": [10]}
    for r in emu.values():
        r["n_plans"], r["controller_version"] = 10, 2
    with pytest.raises(SystemExit):                     # version 2 against records of version 1 (no field)
        RA.analyse(emu, eng, n_boot=50)
    for r in eng.values():
        r["controller_version"] = 2
    assert RA.analyse(emu, eng, n_boot=50)["controller_version"] == 2


def test_analysis_accepts_a_fresh_stream_reference_and_records_both():
    import replan_axis as RA
    emu = _recs(ALT, ZERO, ONE)
    eng = _recs(ZERO, ONE, ONE)
    for r in eng.values():
        r["seed_stream"] = "fresh1"
    res = RA.analyse(emu, eng, n_boot=50)
    assert res["seed_stream"] == {"emulator": None, "engine": "fresh1"}
    assert res["pooled"]["shortfall_real_success"]["replan"]["value"] == 1.0
    next(iter(eng.values()))["seed_stream"] = "fresh2"
    with pytest.raises(SystemExit):                     # one stream per side
        RA.analyse(emu, eng, n_boot=50)


def _without_kept(x, top=True):
    """The analysis output without the keys added after commit 78e9d9b (months kept; prefix, order_index and
    coverage.beyond_prefix)."""
    if isinstance(x, dict):
        out = {k: _without_kept(v, False) for k, v in x.items() if k != "incumbent_kept_months_mean"
               and not (top and k in ("prefix", "order_index"))}
        if top and "coverage" in out:
            out["coverage"] = {k: v for k, v in out["coverage"].items() if k != "beyond_prefix"}
        return out
    if isinstance(x, list):
        return [_without_kept(v, False) for v in x]
    return x


def _old_analysis(tmp_path):
    """replan_axis.py as of commit 78e9d9b (before the months kept and the prefix rule), or None."""
    import importlib.util
    import subprocess
    src = subprocess.run(["git", "-C", str(A.REPO), "show", "78e9d9b:code/scripts/replan_axis.py"], capture_output=True,
                         text=True)
    if src.returncode:
        return None
    f = tmp_path / "replan_axis_78e9d9b.py"
    f.write_text(src.stdout)
    spec = importlib.util.spec_from_file_location("replan_axis_78e9d9b", f)
    OLD = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(OLD)
    return OLD


def _md_core(md):
    """replan.md without the months-kept column and the prefix sentence added after commit 78e9d9b."""
    md = md.replace(" | months the plan in hand was kept (mean, of 23) |", " |").replace(" | n/a |", " |")
    md = md.replace("|---|---|---|---|---|---|---|---|---|", "|---|---|---|---|---|---|---|---|")
    return "\n".join(ln.split(" Analysed:")[0] for ln in md.splitlines())


def test_analysis_months_kept_per_side():
    import replan_axis as RA
    emu, eng = _recs(ALT, ZERO, ONE), _recs(ZERO, ONE, ONE)
    res = RA.analyse(emu, eng, n_boot=50)                       # version 1 records: no field, null on both sides
    assert res["pooled"]["emulator"]["incumbent_kept_months_mean"] is None
    assert all(res["by_family"][f][m]["incumbent_kept_months_mean"] is None for f in T.TASKS for m in RA.MODELS)
    for i, r in enumerate(emu.values()):
        r["incumbent_kept_months"] = i % 24
    for r in eng.values():
        r["incumbent_kept_months"] = 22
    for R_ in (emu, eng):
        for r in R_.values():
            r["controller_version"] = 3
    res = RA.analyse(emu, eng, n_boot=50)
    keys = list(emu)
    assert res["pooled"]["emulator"]["incumbent_kept_months_mean"] == pytest.approx(np.mean([i % 24 for i in range(N)]))
    assert res["pooled"]["engine"]["incumbent_kept_months_mean"] == 22.0
    for f in T.TASKS:
        want = np.mean([i % 24 for i, k in enumerate(keys) if emu[k]["task"] == f])
        assert res["by_family"][f]["emulator"]["incumbent_kept_months_mean"] == pytest.approx(want)
        assert res["by_family"][f]["engine"]["incumbent_kept_months_mean"] == 22.0
    md = RA.markdown(res, {})
    assert "months the plan in hand was kept" in md and "| 22.0 |" in md
    json.dumps(res)                                              # serialisable, null where absent


def test_analysis_existing_fields_unchanged_against_the_committed_script(tmp_path):
    """Every field the analysis wrote before the months-kept field and the prefix rule (commit 78e9d9b) is unchanged on
    the synthetic records the other analysis tests use (complete: every position 0..39 on both sides), with the prefix
    rule (the default) and without it."""
    import replan_axis as RA
    OLD = _old_analysis(tmp_path)
    if OLD is None:
        pytest.skip("commit 78e9d9b not available")
    for e, p in [((ONE, ZERO, ZERO), (ZERO, ZERO, ZERO)), ((ALT, ZERO, ZERO), (~ALT, ZERO, ZERO)),
                 ((ONE, ALT, ~ALT), (ONE, ONE, ONE)), ((ZERO, ALT, ~ALT), (ZERO, ONE, ONE))]:
        emu, eng = _recs(*e), _recs(*p)
        audit = {"emulator": {(k, 1000): (True, False, True) for k in emu}, "engine": None}
        old = json.loads(json.dumps(OLD.analyse(emu, eng, audit, 1000, n_boot=200)))
        for pre in (True, False):
            new = json.loads(json.dumps(RA.analyse(emu, eng, audit, 1000, n_boot=200, prefix=pre)))
            assert _without_kept(new) == old
            assert new["prefix"] is pre and new["order_index"] == list(range(N))
            assert _md_core(RA.markdown(new, {})) == _md_core(OLD.markdown(old, {}))
        assert new["coverage"].get("beyond_prefix") is None


def _recs_n(n, seed=3):
    rng = np.random.default_rng(seed)
    a, b, c = (rng.random(n) < 0.5 for _ in range(3))
    return _recs(a, b, c)


def test_analysis_prefix_complete_100(tmp_path):
    """Both sides hold all 100 positions: the result is the intersection's (and commit 78e9d9b's) apart from the new
    keys; order_index is 0..99 and nothing lies beyond the prefix."""
    import replan_axis as RA
    emu, eng = _recs_n(100, 3), _recs_n(100, 4)
    new = json.loads(json.dumps(RA.analyse(emu, eng, n_boot=200)))
    flat = json.loads(json.dumps(RA.analyse(emu, eng, n_boot=200, prefix=False)))
    assert new["order_index"] == list(range(100)) and new["n_instances"] == 100 and new["prefix"]
    assert new["coverage"]["beyond_prefix"] == [] and _without_kept(new) == _without_kept(flat)
    OLD = _old_analysis(tmp_path)
    if OLD is not None:
        assert _without_kept(new) == json.loads(json.dumps(OLD.analyse(emu, eng, n_boot=200)))


def test_analysis_prefix_with_a_hole_at_position_7(tmp_path):
    import replan_axis as RA
    emu, eng = _recs_n(20, 3), _recs_n(20, 4)
    hole = next(k for k, r in emu.items() if r["order_index"] == 7)
    del emu[hole]
    assert RA.complete_prefix(emu, eng) == 5
    res = json.loads(json.dumps(RA.analyse(emu, eng, n_boot=200)))
    assert res["prefix"] and res["order_index"] == [0, 1, 2, 3, 4] and res["n_instances"] == 5
    assert res["coverage"]["beyond_prefix"] == [5, 6] + list(range(8, 20))
    assert res["coverage"]["engine_only"] == [hole] and res["coverage"]["emulator_only"] == []
    assert res["per_family"] == {t: 1 for t in T.TASKS}
    flat = json.loads(json.dumps(RA.analyse(emu, eng, n_boot=200, prefix=False)))     # --no-prefix: the intersection
    assert not flat["prefix"] and flat["order_index"] == [i for i in range(20) if i != 7]
    assert "beyond_prefix" not in flat["coverage"]
    OLD = _old_analysis(tmp_path)
    if OLD is not None:                                           # --no-prefix reproduces the old output
        assert _without_kept(flat) == json.loads(json.dumps(OLD.analyse(emu, eng, n_boot=200)))
    emu[hole] = dict(eng[hole], order_index=99)                   # one instance at two positions is refused
    with pytest.raises(SystemExit):
        RA.analyse(emu, eng, n_boot=50)
    import replan_axis
    ap_ok = replan_axis.main.__code__.co_consts                   # the CLI flag exists (--prefix / --no-prefix)
    assert any(isinstance(c, str) and "--prefix" in c for c in ap_ok)
