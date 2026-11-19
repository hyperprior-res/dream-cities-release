"""Monthly replanning : random search replanned every month from the engine's real
state, for one model at a time (the emulator, or the engine on seeds disjoint from the realised one: the perfect
emulator).

Controller (``replan_instance``), per instance and model. The realised seed is the instance's oracle seed 0. At each
month t = 0..H-1, from the engine's real state at month t (the months executed so far replayed on the realised seed,
``PrefixEngine``):

1. draw ``n_plans`` plans for the remaining H-t months from the audit's proposal generator: a policy drawn from the
   behaviour mix (``dc.behaviour.sample_behaviour``) played closed loop from that state by
   ``dc.behaviour.rollout_behaviour`` on a generation seed of its own, random disasters off, kept as an open-loop plan
   with its forced-disaster column cleared (the procedure that made the logged plans, ``scripts/calibrate_tasks.py``);
   fresh draws seeded by instance, month and draw: policy ``default_rng(seed_for("replan-policy", instance, t, j))``,
   engine ``fresh_seed(("replan-gen", instance, t, j), reserved)``;
2. score each plan with the model as the audit's random search scores a proposal: ``K_SEARCH`` = 2 model samples, the
   mean of ``stats_margin(traj_stats(.))``, every sample being the model's rollout of the remaining months from the
   real state joined to the realised months (``dc.audit.join_prefix``); the candidates are the executed months
   followed by the drawn plan, through ``dc.audit.effective`` (the task's forced events);
3. select with ``hpr_dream.random_shooting`` over all ``n_plans`` (the highest score, the first on ties);
4. execute the selected plan's month t in the engine on the realised seed; next month.

Controller version 2 : from
month 1 on the candidates are the remaining months of the plan chosen the month before, first (the incumbent), then
fresh draws 0..n_plans-2 drawn as in step 1, all scored as in step 2; the first-on-ties rule keeps the incumbent on ties.

The month-0 choice also gets the paper's verdict (``K_VERDICT`` = 8 model samples from the start, accepted when the
4th-largest margin is >= 0, i.e. at least 4 of 8 pass), and is executed in full without replanning on the same seed
(the open-loop arm) and judged by the majority oracle (``dc.audit.oracle_judgement`` over the instance's 32 oracle
seeds; its seed-0 verdict is the open-loop arm's realised verdict, checked).

Models. ``EmulatorModel``: ``ReplanEmulatorJudge`` (``dc.audit.EmulatorJudge``, chunks, padding, seeding and decoding
unchanged) started from the model's state of the real observation at month t (month 0: the audit's own ``state0``);
torch seed ``seed_for("audit-emu", start, "replan-score", task, t)``. ``EngineModel``: ``dc.audit.EngineSeedJudge``
over the engine continued from the real state: the realised months replayed on the realised seed, the generator
reseeded at month t with the judge's own seed (``seed_for("audit-seedcheck", start, "replan-score", task, t, i, k)``,
redrawn while it is one of the nine residual or 32 oracle seeds of any task of the start, so never the realised seed).
At month 0 both are the audit's judges exactly (no prefix).

The engine is only ever positioned by its own loader and month steps (``PrefixEngine``): there is no state injection;
reseeding the generator at a month boundary (``Engine.seed``) is the one call added to ``dc.oracle.replay``'s order.

Workers. Proposal draws and engine replays are jobs (``_job``) for a local process pool and, optionally, a remote
pool (``python -m dc.replan serve`` on host-b over the audit's ssh command, ``host_b_replan_pool``), split by
measured rates like ``dc.audit.EngineJudge``. The remote is used only when the files the jobs run on (``CODE_FILES``)
have the local sha256 there and a few jobs give identical results (``check_remote``). No result is cached on disk.
"""

from __future__ import annotations

import inspect
import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .engine import NUM_SCALARS
from .grammar import N_COLS, compile_plan
from .seeds import seed_for

REPO = Path(__file__).resolve().parents[2]
FORCED_COL = 4
# the files the worker jobs execute: they must be identical on a remote machine (``check_remote``)
CODE_FILES = ("code/dc/replan.py", "code/dc/behaviour.py", "code/dc/oracle.py", "code/dc/engine.py",
              "code/dc/grammar.py", "code/dc/seeds.py")


# ----------------------------------------------------------------------------------------------
# The engine at the real state of month t
# ----------------------------------------------------------------------------------------------
class PrefixEngine:
    """An engine positioned at the real state of month t of a replay. ``load_start`` does what ``dc.oracle.replay``
    does for the first t months of ``actions`` on ``seed``: full reset and the engine's own loader, the disaster
    switch, the observation, the seed, then per month the budget settings and tool calls, the forced disaster, one
    month, the observation. Every other call goes to the wrapped engine, so ``dc.oracle.replay(PrefixEngine(..), cty,
    rest, s)`` continues from the real state with the generator reseeded with ``s`` at month t, and
    ``dc.behaviour.rollout_behaviour(PrefixEngine(..), cty, policy, H - t, s, False, rng)`` plays a policy from it.
    ``prefix_scalars`` (t+1, 20): the scalar rows 0..t of the prefix, as ``replay`` records them."""

    def __init__(self, eng, actions, forced: Optional[Dict[int, int]], seed: int, disasters: bool = False) -> None:
        self.eng = eng
        self.actions = list(actions)
        self.forced = {int(m): int(k) for m, k in (forced or {}).items()}
        if any(m >= len(self.actions) or m < 0 for m in self.forced):
            raise ValueError(f"forced events {self.forced} outside the prefix of {len(self.actions)} months")
        self.seed0 = int(seed)
        self.disasters = bool(disasters)
        self.prefix_scalars: Optional[np.ndarray] = None

    def load_start(self, cty_path) -> None:
        e = self.eng
        e.load_start(cty_path)
        e.set_disasters(self.disasters)
        sc = [e.observe().scalars.copy()]
        e.seed(self.seed0)
        for m, act in enumerate(self.actions):
            e.apply(act)
            if m in self.forced:
                e.force_disaster(self.forced[m])
            e.step_month()
            sc.append(e.scalars())
            e.ledger()
        self.prefix_scalars = np.stack(sc).astype(np.int64)

    def set_disasters(self, on: bool) -> None:
        """The switch belongs before the prefix's first observation; a later call may only confirm it."""
        if bool(on) != self.disasters:
            raise ValueError("PrefixEngine: the disaster switch was set before the prefix")

    def __getattr__(self, name):
        return getattr(self.eng, name)


def salted(key: tuple, seed_stream: Optional[str] = None) -> tuple:
    """A seed key or sample stream in a named seed stream : ``key + ("seed-stream", name)``; with no
    name the key itself, so the default path derives every seed exactly as before the option existed."""
    return tuple(key) + ("seed-stream", str(seed_stream)) if seed_stream else tuple(key)


def proposal_seeds(key: str, t: int, n: int, reserved, seed_stream: Optional[str] = None) -> Tuple[List[int], List[int]]:
    """The proposal draws' seeds at month t: engine ``fresh_seed(salted(("replan-gen", key, t, j)), reserved)`` and
    policy ``seed_for(*salted(("replan-policy", key, t, j)))``, j < n."""
    from .audit import fresh_seed
    return ([fresh_seed(salted(("replan-gen", key, t, j), seed_stream), reserved)[0] for j in range(n)],
            [seed_for(*salted(("replan-policy", key, t, j), seed_stream)) for j in range(n)])


def split_forced(forced: Dict[int, int], t: int) -> Tuple[Dict[int, int], Dict[int, int]]:
    """{month: kind} of a whole plan -> (events of months < t, events of months >= t renumbered from t)."""
    return ({m: k for m, k in forced.items() if m < t}, {m - t: k for m, k in forced.items() if m >= t})


# ----------------------------------------------------------------------------------------------
# Worker jobs
# ----------------------------------------------------------------------------------------------
_ENG = None


def _init() -> None:
    global _ENG
    from .engine import Engine
    _ENG = Engine()


def _engine():
    if _ENG is None:
        _init()
    return _ENG


def _abs(cty: str) -> str:
    return cty if os.path.isabs(cty) else str(REPO / cty)


def gen_plan(eng, cty: str, prefix_eff: np.ndarray, H: int, seed_real: int, gen_seed: int, policy_seed: int):
    """One proposal for months t..H-1 (t = len(prefix_eff)): a behaviour-mix policy played closed loop by
    ``rollout_behaviour`` from the real state at month t (``PrefixEngine`` on ``seed_real``) on ``gen_seed``, random
    disasters off; its action log with the forced-disaster column cleared. Returns (plan (H-t, 25) int16, label)."""
    from .behaviour import rollout_behaviour, sample_behaviour
    t = int(prefix_eff.shape[0])
    acts, forced = compile_plan(prefix_eff) if t else ([], {})
    rng = np.random.default_rng(int(policy_seed))
    policy, label = sample_behaviour(rng)
    plan, _ = rollout_behaviour(PrefixEngine(eng, acts, forced, seed_real), _abs(cty), policy, H - t, int(gen_seed),
                                False, rng, record="scalars")
    plan = np.asarray(plan, dtype=np.int16).copy()
    plan[:, FORCED_COL] = 0                                     # task plans carry no forced disasters of their own
    return plan, label


def continued(eng, cty: str, eff_plan: np.ndarray, t: int, seed_real: int, seed: int) -> np.ndarray:
    """Scalar trajectory (H+1, 20) int64 of an effective plan (H, 25): months 0..t-1 replayed on ``seed_real``, the
    generator reseeded with ``seed`` at month t, months t..H-1 replayed from there. t = 0 is ``dc.oracle.replay`` on
    ``seed`` exactly (what ``dc.audit._replay_job`` computes)."""
    from .oracle import replay
    acts, forced = compile_plan(eff_plan)
    if t == 0:
        return replay(eng, _abs(cty), acts, int(seed), forced=forced or None).scalars.astype(np.int64)
    head, rest = split_forced(forced, t)
    pe = PrefixEngine(eng, acts[:t], head, seed_real)
    rp = replay(pe, _abs(cty), acts[t:], int(seed), forced=rest or None)
    if not np.array_equal(rp.scalars[0], pe.prefix_scalars[t]):
        raise RuntimeError("continued: the observation at month t differs from the prefix's")
    return np.concatenate([pe.prefix_scalars[:t], rp.scalars]).astype(np.int64)


def _job(args):
    """("gen", cty, prefix bytes, t, H, seed_real, gen_seed, policy_seed) -> (plan bytes (H-t, 25) int16, label);
    ("cont", cty, effective plan bytes, H, seed_real, t, seed) -> scalar trajectory bytes (H+1, 20) <i8."""
    kind = args[0]
    if kind == "gen":
        _, cty, pb, t, H, seed_real, gs, ps = args
        prefix = np.frombuffer(pb, dtype=np.int16).reshape(int(t), N_COLS)
        plan, label = gen_plan(_engine(), cty, prefix, int(H), int(seed_real), int(gs), int(ps))
        return plan.tobytes(), label
    if kind == "cont":
        _, cty, pb, H, seed_real, t, seed = args
        P = np.frombuffer(pb, dtype=np.int16).reshape(int(H), N_COLS)
        return continued(_engine(), cty, P, int(t), int(seed_real), int(seed)).astype("<i8").tobytes()
    raise ValueError(f"unknown job {kind!r}")


def _job_months(args) -> int:
    """Engine city-months a job steps: the prefix and the rest, H in both kinds."""
    return int(args[4]) if args[0] == "gen" else int(args[3])


def _ping() -> bool:
    return _ENG is not None


def serve(workers: int) -> None:
    """Job server for a remote machine, ``dc.audit.serve``'s framing and requests ("sha", "map", "quit") with this
    module's jobs."""
    import multiprocessing as mp
    import socket
    from .audit import _recv, _send, _sha256_file
    from .engine import PROTO_VERSION
    inp, out = sys.stdin.buffer, sys.stdout.buffer
    sys.stdout = sys.stderr
    pool = mp.get_context("fork").Pool(int(workers), initializer=_init)
    try:
        pool.apply_async(_ping).get(timeout=120)
    except Exception as e:  # pragma: no cover
        _send(out, ("error", f"replan workers did not start: {e!r}"))
        pool.terminate()
        return
    _send(out, ("ready", PROTO_VERSION, socket.gethostname(), int(workers)))
    while True:
        msg = _recv(inp)
        if msg is None or msg[0] == "quit":
            break
        if msg[0] == "sha":
            _send(out, ("ok", {r: (_sha256_file(REPO / r) if (REPO / r).exists() else None) for r in msg[1]}))
        elif msg[0] == "map":
            jobs = msg[1]
            _send(out, ("ok", pool.map(_job, jobs, chunksize=max(1, len(jobs) // (4 * int(workers))))))
        else:
            _send(out, ("error", f"unknown request {msg[0]!r}"))
    pool.close()
    pool.join()


def host_b_replan_pool(workers: int, root: Optional[str] = None, log_path=None):
    """``dc.audit.RemotePool`` over the audit's ssh command to host-b (``dc.audit.HOST_B_SSH``, root
    ``dc.audit.HOST_B_ROOT``), running this module's ``serve``."""
    from . import audit as A
    root = root or A.HOST_B_ROOT
    cmd = A.HOST_B_SSH + [f"cd {root} && PYTHONPATH=code exec .venv/bin/python -u -m dc.replan serve "
                            f"--workers {int(workers)}"]
    return A.RemotePool(cmd, workers, log_path)


class JobPool:
    """Runs ``_job`` lists on a local process pool (``workers``; 0: in this process) and, when ``remote`` is given and
    a call has enough jobs, partly on the remote pool; the split follows the measured rates of the two (as
    ``dc.audit.EngineJudge._replay``). A failing remote is dropped and its jobs run locally. Counters: jobs by kind,
    jobs run remotely, engine city-months, seconds."""

    def __init__(self, workers: int = 0, remote=None, log=print) -> None:
        self.workers = int(workers)
        self.remote = remote
        self.log = log
        self._pool = None
        self._rate = {"local": 1.0 * max(1, self.workers), "remote": 1.0 * (remote.workers if remote else 0)}
        self.n_jobs: Dict[str, int] = {}
        self.n_remote = 0
        self.city_months = 0
        self.seconds = 0.0

    def _get_pool(self):
        if self._pool is None and self.workers > 0:
            import multiprocessing as mp
            self._pool = mp.get_context("spawn").Pool(self.workers, initializer=_init)
        return self._pool

    def _local(self, jobs):
        pool = self._get_pool()
        if pool is None:
            return [_job(j) for j in jobs]
        return pool.map(_job, jobs, chunksize=max(1, len(jobs) // (4 * self.workers)))

    def map(self, jobs: Sequence[tuple]) -> list:
        jobs = list(jobs)
        if not jobs:
            return []
        t0 = time.time()
        for j in jobs:
            self.n_jobs[j[0]] = self.n_jobs.get(j[0], 0) + 1
            self.city_months += _job_months(j)
        r = self.remote
        if r is None or len(jobs) < 4 * max(1, self.workers):
            out = self._local(jobs)
            self.seconds += time.time() - t0
            return out
        rels = sorted({os.path.relpath(_abs(j[1]), REPO) for j in jobs})
        r.check_files(rels)
        f = self._rate["remote"] / (self._rate["remote"] + self._rate["local"])
        nr = int(round(len(jobs) * f))
        rjobs = [(j[0], os.path.relpath(_abs(j[1]), REPO)) + tuple(j[2:]) for j in jobs[:nr]]
        box: Dict[str, object] = {}

        def run_remote():
            t1 = time.time()
            try:
                box["res"] = r.map(rjobs)
            except Exception as e:  # pragma: no cover - fall back to local jobs
                box["err"] = e
            box["t"] = time.time() - t1

        th = threading.Thread(target=run_remote, daemon=True)
        th.start()
        t1 = time.time()
        loc = self._local(jobs[nr:]) if nr < len(jobs) else []
        tl = time.time() - t1
        th.join()
        if "err" in box:  # pragma: no cover
            self.log(f"  remote jobs failed ({box['err']!r}); running them locally and dropping the remote pool")
            self.remote = None
            out = self._local(jobs[:nr]) + loc
            self.seconds += time.time() - t0
            return out
        for k, n, t in (("remote", nr, box["t"]), ("local", len(jobs) - nr, tl)):
            if n >= 2 * max(1, self.workers) and t > 0:
                self._rate[k] = 0.5 * self._rate[k] + 0.5 * n / t
        self.n_remote += nr
        self.seconds += time.time() - t0
        return list(box["res"]) + loc

    def counters(self) -> dict:
        return {"jobs": dict(self.n_jobs), "jobs_remote": self.n_remote, "engine_city_months": self.city_months,
                "engine_seconds": self.seconds}

    def close(self) -> None:
        if self._pool is not None:
            self._pool.close()
            self._pool.join()
            self._pool = None
        if self.remote is not None:
            self.remote.close()
            self.remote = None


def check_remote(pool: JobPool, inst, H: int = 24) -> dict:
    """Before a remote pool is used: ``CODE_FILES`` and the instance's start file have the local sha256 on the remote
    machine (``RemotePool.check_files`` raises otherwise), and three proposal draws and three continued replays (t = 0
    and t = 5) give identical results there and here. Raises if they differ."""
    from . import audit as A
    r = pool.remote
    r.check_files(list(CODE_FILES) + [os.path.relpath(_abs(inst.cty), REPO)])
    raw = A.Pools(H=H).behaviour(inst.start_id)[:3]
    eff = A.effective(raw, inst.task, H)
    s_real = A.oracle_seed_list(inst, 32)[0]
    rel = os.path.relpath(_abs(inst.cty), REPO)
    jobs = [("gen", rel, eff[0, :5].tobytes(), 5, H, s_real, seed_for("remote-check", j), seed_for("remote-check-p", j))
            for j in range(3)]
    jobs += [("cont", rel, eff[j].tobytes(), H, s_real, t, seed_for("remote-check", j)) for j in range(3) for t in (0, 5)]
    here = [_job(j) for j in jobs]
    there = r.map(jobs)
    same = [tuple(a) == tuple(b) if isinstance(a, tuple) else a == b for a, b in zip(here, there)]
    if not all(same):
        raise RuntimeError(f"remote jobs differ from local jobs on {same.count(False)} of {len(jobs)} checks")
    return {"host": r.host, "workers": r.workers, "checked_files": list(CODE_FILES), "identical_jobs": len(jobs)}


# ----------------------------------------------------------------------------------------------
# The real engine as the controller uses it
# ----------------------------------------------------------------------------------------------
@dataclass
class Realised:
    """The realised months so far: month t, the effective executed rows (t, 25), the realised seed, the scalar rows
    0..t (t+1, 20) and the observation and ledger at month t (for the emulator's start state)."""
    t: int
    eff_prefix: np.ndarray
    seed_real: int
    prefix: np.ndarray
    obs: object = None
    ledger: Optional[np.ndarray] = None


class EngineWorld:
    """The engine: plain replays with the ``dc.audit.EngineJudge.scalars`` interface (so ``EngineSeedJudge`` and
    ``oracle_trajectories`` run on it; nothing is cached), continued replays, proposal draws, and the real state at
    month t (replayed in this process). Counters add this process's prefix months to the pool's."""

    def __init__(self, pool: JobPool, H: int = 24) -> None:
        self.pool = pool
        self.H = int(H)
        self.workers = pool.workers
        self._eng = None
        self.state_months = 0
        self.state_seconds = 0.0

    def scalars(self, inst, eff_plans, seeds, key_sink=None, store=True) -> np.ndarray:
        return self.continued(inst, eff_plans, 0, 0, seeds)

    def continued(self, inst, eff_plans, t: int, seed_real: int, seeds) -> np.ndarray:
        H = self.H
        P = np.ascontiguousarray(eff_plans, dtype=np.int16).reshape(-1, H, N_COLS)
        sd = np.broadcast_to(np.asarray(seeds, dtype=np.int64), (P.shape[0],))
        jobs = [("cont", inst.cty, P[i].tobytes(), H, int(seed_real), int(t), int(sd[i])) for i in range(P.shape[0])]
        out = self.pool.map(jobs)
        return np.stack([np.frombuffer(b, dtype="<i8").reshape(H + 1, NUM_SCALARS) for b in out])

    def proposals(self, inst, eff_prefix: np.ndarray, seed_real: int, n: int, reserved,
                  seed_stream: Optional[str] = None) -> Tuple[np.ndarray, List[str]]:
        """``n`` fresh proposals for months t..H-1 (t = len(eff_prefix)), seeded by instance, month and draw.
        Returns (raw plans (n, H-t, 25) int16, behaviour labels)."""
        from .audit import fresh_seed
        t, H = int(eff_prefix.shape[0]), self.H
        pb = np.ascontiguousarray(eff_prefix, dtype=np.int16).tobytes()
        gs, ps = proposal_seeds(inst.key, t, n, reserved, seed_stream)
        jobs = [("gen", inst.cty, pb, t, H, int(seed_real), gs[j], ps[j]) for j in range(n)]
        out = self.pool.map(jobs)
        if not out:
            return np.zeros((0, H - t, N_COLS), dtype=np.int16), []
        plans = np.stack([np.frombuffer(b, dtype=np.int16).reshape(H - t, N_COLS) for b, _ in out])
        return plans, [lab for _, lab in out]

    def realised(self, inst, eff_prefix: np.ndarray, seed_real: int, want_state: bool = True) -> Realised:
        """The realised months 0..t-1 replayed on ``seed_real`` in this process (``PrefixEngine``)."""
        t0 = time.time()
        t = int(eff_prefix.shape[0])
        if self._eng is None:
            from .engine import Engine
            self._eng = Engine()
        acts, forced = compile_plan(eff_prefix) if t else ([], {})
        pe = PrefixEngine(self._eng, acts, forced, seed_real)
        pe.load_start(_abs(inst.cty))
        obs, led = (self._eng.observe(), self._eng.ledger()) if want_state else (None, None)
        self.state_months += t
        self.state_seconds += time.time() - t0
        return Realised(t, np.asarray(eff_prefix, dtype=np.int16), int(seed_real), pe.prefix_scalars, obs, led)

    def counters(self) -> dict:
        c = self.pool.counters()
        c["engine_city_months"] += self.state_months
        c["engine_seconds"] += self.state_seconds
        c["prefix_months_in_process"] = self.state_months
        return c


# ----------------------------------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------------------------------
def _emulator_judge_class():
    from . import audit as A

    class ReplanEmulatorJudge(A.EmulatorJudge):
        """``dc.audit.EmulatorJudge`` whose rollouts can start from the real state at month t (``samples_from``);
        chunks, padding, buckets, seeding and the model's own decoding are the audit's."""

        _override = None

        def state0(self, inst):
            if self._override is not None:
                return self._override
            return super().state0(inst)

        def state_of(self, obs, ledger_row) -> dict:
            """The model's state of an engine observation, converted as ``state0`` converts the start's: the model
            revision's ``obs_to_numpy`` (with the ledger row read after the disaster switch, when it takes one) and
            ``numpy_to_state``."""
            return state_from_obs(self._tr, obs, ledger_row, self.device)

        def samples_from(self, inst, P, K, stream, state):
            self._override = state
            try:
                return self.samples(inst, P, K, stream)
            finally:
                self._override = None

    return ReplanEmulatorJudge


def state_from_obs(Tr, obs, ledger_row, device) -> dict:
    """``EmulatorJudge.state0``'s conversion of one observation (``Tr``: the model revision's train module)."""
    o2n = Tr.obs_to_numpy
    if ledger_row is not None and "ledger" in inspect.signature(o2n).parameters:
        d = o2n([obs], ledger=np.asarray(ledger_row)[None])
    else:
        d = o2n([obs])
    return Tr.numpy_to_state(d, device)


def make_emulator_judge(ckpt, **kw):
    return _emulator_judge_class()(ckpt, **kw)


class EmulatorModel:
    """The emulator under replanning: at month t its K samples of the remaining months start from its state of the real
    observation (month 0: ``state0``, the audit's start state), joined to the realised months."""

    name = "emulator"

    def __init__(self, judge) -> None:
        self.judge = judge

    def score_samples(self, inst, eff_full: np.ndarray, real: Realised, K: int, stream: tuple) -> np.ndarray:
        from .audit import join_prefix
        t = real.t
        state = self.judge.state0(inst) if t == 0 else self.judge.state_of(real.obs, real.ledger)
        suffix = self.judge.samples_from(inst, np.ascontiguousarray(eff_full[:, t:]), K, stream, state)
        return join_prefix(real.prefix, suffix)

    def verdict_samples(self, inst, eff_full: np.ndarray, K: int, stream: tuple) -> np.ndarray:
        return self.judge.samples(inst, eff_full, K, stream)

    def paired_samples(self, inst, eff_full: np.ndarray, real: Realised, K: int,
                       seed_stream: Optional[str] = None) -> np.ndarray:
        """Version 3's paired comparison: each plan (incumbent, challenger) rolled out K times from the real state at
        month t in a call of its own through the same batched code as the screen (``samples_from``), every call with
        the same stream ("replan-pair", task, t), so the same torch seed and batch shape: both rollouts draw the same
        noise (common random numbers). The screen's calls are made before and are not changed."""
        from .audit import join_prefix
        t = real.t
        state = self.judge.state0(inst) if t == 0 else self.judge.state_of(real.obs, real.ledger)
        stream = salted(("replan-pair", inst.task, t), seed_stream)
        suf = [self.judge.samples_from(inst, np.ascontiguousarray(eff_full[p:p + 1, t:]), K, stream, state)
               for p in range(eff_full.shape[0])]
        return join_prefix(real.prefix, np.concatenate(suf))

    def counters(self) -> dict:
        return self.judge.counters()

    def describe(self) -> dict:
        return {"model": self.name, **self.judge.describe()}


class _Continuation:
    """``EngineJudge.scalars`` for ``EngineSeedJudge``: replays continued from the realised months of ``real`` (the
    generator reseeded with each sample's own seed at month t); no prefix (t = 0) gives plain replays."""

    def __init__(self, world: EngineWorld) -> None:
        self.world = world
        self.real: Optional[Realised] = None
        self.seen: set = set()

    def scalars(self, inst, eff_plans, seeds, key_sink=None, store=True) -> np.ndarray:
        r = self.real
        self.seen.update(int(x) for x in np.asarray(seeds).ravel())
        if r is None or r.t == 0:
            return self.world.continued(inst, eff_plans, 0, 0, seeds)
        return self.world.continued(inst, eff_plans, r.t, r.seed_real, seeds)


class EngineModel:
    """The perfect emulator under replanning: ``dc.audit.EngineSeedJudge`` (its seeds, its redraws of reserved seeds)
    on the engine continued from the real state at month t; samples' rows 0..t are the realised months (checked)."""

    name = "engine"

    def __init__(self, world: EngineWorld, oracle_n: int) -> None:
        from .audit import EngineSeedJudge
        self.cont = _Continuation(world)
        self.judge = EngineSeedJudge(self.cont, oracle_n=oracle_n)
        self.paired_steps = 0          # month-steps of the paired replays, counted as the judge counts its own

    def score_samples(self, inst, eff_full: np.ndarray, real: Realised, K: int, stream: tuple) -> np.ndarray:
        from .audit import join_prefix
        self.cont.real = real
        self.cont.seen = set()
        try:
            tr = self.judge.samples(inst, eff_full, K, stream)
        finally:
            self.cont.real = None
        t = real.t
        if not np.array_equal(tr[..., :t + 1, :], np.broadcast_to(real.prefix, tr.shape[:-2] + real.prefix.shape)):
            raise RuntimeError(f"{inst.key} month {t}: continued replays do not start from the realised months")
        return join_prefix(real.prefix, tr[..., t:, :])

    def verdict_samples(self, inst, eff_full: np.ndarray, K: int, stream: tuple) -> np.ndarray:
        return self.judge.samples(inst, eff_full, K, stream)

    def paired_samples(self, inst, eff_full: np.ndarray, real: Realised, K: int,
                       seed_stream: Optional[str] = None) -> np.ndarray:
        """Version 3's paired comparison: every plan replayed on the same K engine seeds (common random numbers),
        continued from the real state at month t; seed k is ``fresh_seed(("replan-pair", start, task, t, k), avoid)``,
        avoid = the reserved seeds of the start (the nine residual and the oracle's seeds of every task, the realised
        seed among them) and every seed of this month's screen."""
        from .audit import fresh_seed, join_prefix, reserved_seeds
        t, H, n = real.t, inst.horizon, eff_full.shape[0]
        avoid = (frozenset(reserved_seeds(inst.start_id, H, self.judge.oracle_n)) | frozenset(self.cont.seen)
                 | {int(real.seed_real)})
        seeds = [fresh_seed(salted(("replan-pair", inst.start_id, inst.task, t, k), seed_stream), avoid)[0]
                 for k in range(K)]
        tr = self.cont.world.continued(inst, np.repeat(eff_full, K, axis=0), t, real.seed_real, np.tile(seeds, n))
        tr = tr.astype(np.float64).reshape(n, K, H + 1, NUM_SCALARS)
        if not np.array_equal(tr[..., :t + 1, :], np.broadcast_to(real.prefix, tr.shape[:-2] + real.prefix.shape)):
            raise RuntimeError(f"{inst.key} month {t}: paired replays do not start from the realised months")
        self.last_pair_seeds = seeds
        self.paired_steps += n * K * H
        return join_prefix(real.prefix, tr[..., t:, :])

    def counters(self) -> dict:
        c = self.judge.counters()
        c["judge_month_steps"] += self.paired_steps
        return c

    def describe(self) -> dict:
        return {"model": self.name, **self.judge.describe(),
                "continuation": "months 0..t-1 on the realised seed, the generator reseeded at month t with the judge's "
                                "seed (dc.replan.continued)"}


# ----------------------------------------------------------------------------------------------
# The controller
# ----------------------------------------------------------------------------------------------
def _delta(a: dict, b: dict) -> dict:
    out = {}
    for k, v in b.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out[k] = v - a.get(k, 0)
        elif isinstance(v, dict):
            out[k] = {kk: vv - a.get(k, {}).get(kk, 0) for kk, vv in v.items()}
    return out


CONTROLLER_VERSIONS = (1, 2, 3)
CONTROLLER_VERSION = 3          # the analysis plan: the challenger must beat the incumbent on paired samples
PAIRED_SAMPLES = 8              # version 3: the paired comparison's samples per plan, the verdict's sample count (K_VERDICT)
SWITCH_STANDARD_ERRORS = 2.0    # version 3: switch when the paired mean exceeds two standard errors


def switch_rule(d) -> Tuple[bool, float, float]:
    """Version 3's switch : ``d`` = challenger minus incumbent margins on the paired samples. Switch
    exactly when mean(d) > SWITCH_STANDARD_ERRORS * sd(d, ddof=1) / sqrt(len(d)), strictly; when every difference is
    equal the standard error is zero and the rule is mean(d) > 0. Returns (switch, mean, standard error)."""
    d = np.asarray(d, dtype=np.float64)
    if d.ndim != 1 or d.size < 2 or not np.isfinite(d).all():
        raise ValueError(f"switch_rule: {d.size} paired differences (finite, at least 2 needed)")
    mean = float(d.mean())
    se = 0.0 if np.all(d == d[0]) else float(d.std(ddof=1) / np.sqrt(d.size))
    if np.all(d == d[0]):
        mean = float(d[0])
    return bool(mean > SWITCH_STANDARD_ERRORS * se), mean, se


def replan_instance(inst, model, world, *, n_plans: int, oracle_n: int = 32, replan_at: Optional[Sequence[int]] = None,
                    controller_version: int = CONTROLLER_VERSION, seed_stream: Optional[str] = None,
                    log=None) -> dict:
    """The analysis plan's controller on one instance (module docstring). ``replan_at``: the months that replan (default
    every month; a test hook: ``(0,)`` executes the month-0 choice in full, the open-loop arm). Returns the record.

    ``controller_version`` 1 : every replan scores ``n_plans`` fresh proposals (draws 0..n_plans-1).
    Version 2 : month 0 as version 1; at a later replan the candidates are the remaining months
    of the plan chosen at the previous replan, placed first (index 0, label "incumbent"), then the month's fresh draws
    0..n_plans-2 (the same generator and seeding rule; draw n_plans-1 is not drawn), ``n_plans`` in all; every
    candidate, the incumbent included, is scored on the month's fresh model samples, and ``random_shooting``'s first-on-
    ties rule keeps the incumbent on ties. Each month records whether the incumbent was kept (None where none was
    offered)."""
    import hpr_dream as hd
    from . import audit as A
    from . import tasks as T
    if controller_version not in CONTROLLER_VERSIONS:
        raise ValueError(f"controller version {controller_version}: one of {CONTROLLER_VERSIONS}")
    sk = {"seed_stream": seed_stream} if seed_stream else {}     # the default path passes nothing new
    H = int(inst.horizon)
    t_start = time.time()
    sec = {"proposals": 0.0, "scoring": 0.0, "realised_state": 0.0, "verdict_oracle_replays": 0.0}
    if controller_version == 3:
        sec["paired"] = 0.0
    m0, w0 = model.counters(), world.counters()
    seed_real = int(A.oracle_seed_list(inst, oracle_n)[0])
    reserved = A.reserved_seeds(inst.start_id, H, oracle_n)
    executed = np.zeros((0, N_COLS), dtype=np.int16)
    plan_cur = None
    months, choice0, rollout_ms, pair_ms, pair_ecm = [], None, 0, 0, 0
    want_state = model.name == "emulator"
    for t in range(H):
        filler = np.zeros((H - t, N_COLS), dtype=np.int16)
        eff_prefix = A.effective(np.concatenate([executed, filler])[None], inst.task, H)[0, :t]
        t0 = time.time()
        real = world.realised(inst, eff_prefix, seed_real, want_state=want_state)
        sec["realised_state"] += time.time() - t0
        if replan_at is None or t in replan_at:
            incumbent = controller_version == 2 and plan_cur is not None
            paired = controller_version == 3 and plan_cur is not None
            t0 = time.time()
            if paired:          # version 3: the screen holds fresh draws 0..n_plans-2 only, no incumbent
                if not np.array_equal(plan_cur[:t], executed):
                    raise RuntimeError(f"{inst.key} month {t}: the incumbent does not begin with the executed months")
                raw_suffix, labels = world.proposals(inst, eff_prefix, seed_real, n_plans - 1, reserved, **sk)
                raw_suffix, labels = np.asarray(raw_suffix, dtype=np.int16), list(labels)
            elif incumbent:
                if not np.array_equal(plan_cur[:t], executed):
                    raise RuntimeError(f"{inst.key} month {t}: the incumbent does not begin with the executed months")
                fresh, labels = world.proposals(inst, eff_prefix, seed_real, n_plans - 1, reserved, **sk)
                raw_suffix = np.concatenate([plan_cur[None, t:].astype(np.int16), np.asarray(fresh, dtype=np.int16)])
                labels = ["incumbent"] + list(labels)
            else:
                raw_suffix, labels = world.proposals(inst, eff_prefix, seed_real, n_plans, reserved, **sk)
            sec["proposals"] += time.time() - t0
            n_c = n_plans - 1 if paired else n_plans
            if raw_suffix.shape[0] != n_c or len(labels) != n_c:
                raise RuntimeError(f"{inst.key} month {t}: {raw_suffix.shape[0]} candidates, {n_c} wanted")
            cand = np.concatenate([np.broadcast_to(executed, (n_c,) + executed.shape), raw_suffix], axis=1)
            eff = A.effective(cand, inst.task, H)
            if not np.array_equal(eff[:, :t], np.broadcast_to(eff_prefix, (n_c,) + eff_prefix.shape)):
                raise RuntimeError(f"{inst.key} month {t}: candidates do not begin with the executed months")
            t0 = time.time()
            tr = model.score_samples(inst, eff, real, A.K_SEARCH, salted(("replan-score", inst.task, t), seed_stream))
            st = A.traj_stats(tr)
            A.Audit._check_stats([inst], tr, st)
            score = A.stats_margin(inst, st).mean(axis=1)               # the audit's random-search score
            sec["scoring"] += time.time() - t0
            rollout_ms += n_c * A.K_SEARCH * (H - t)
            flat = cand.reshape(n_c, -1).astype(np.int64)
            sel = hd.random_shooting(A._Lookup(flat, score), flat, n_c)
            if int(sel.log["n_scored"]) != n_c:
                raise hd.BudgetError(f"{inst.key} month {t}: scored {sel.log['n_scored']}")
            j = int(sel.log["best_index"])
            if paired:          # version 3: incumbent and challenger on PAIRED_SAMPLES common samples
                t0 = time.time()
                eff2 = A.effective(np.stack([plan_cur, cand[j]]), inst.task, H)
                if not np.array_equal(eff2[:, :t], np.broadcast_to(eff_prefix, (2,) + eff_prefix.shape)):
                    raise RuntimeError(f"{inst.key} month {t}: paired plans do not begin with the executed months")
                tp = model.paired_samples(inst, eff2, real, PAIRED_SAMPLES, **sk)
                stp = A.traj_stats(tp)
                A.Audit._check_stats([inst], tp, stp)
                mp = A.stats_margin(inst, stp)                          # (2, PAIRED_SAMPLES): incumbent, challenger
                d = mp[1] - mp[0]
                switch, dmean, dse = switch_rule(d)
                pair_ms += 2 * PAIRED_SAMPLES * (H - t)
                pair_ecm += 2 * PAIRED_SAMPLES * H if model.name == "engine" else 0
                sec["paired"] += time.time() - t0
                if switch:
                    plan_cur = cand[j].astype(np.int16).copy()
                months.append({"month": t, "best_index": j, "best_score": float(score[j]),
                               "label": labels[j] if switch else "incumbent",
                               "realised_funds": int(real.prefix[-1, 0]), "realised_pop": int(real.prefix[-1, 5]),
                               "challenger_index": j, "challenger_label": labels[j], "challenger_score": float(score[j]),
                               "pair_incumbent_margins": [float(x) for x in mp[0]],
                               "pair_challenger_margins": [float(x) for x in mp[1]],
                               "pair_d_mean": dmean, "pair_d_se": dse, "switched": switch, "incumbent_kept": not switch})
            else:
                plan_cur = cand[j].astype(np.int16).copy()
                months.append({"month": t, "best_index": j, "best_score": float(score[j]), "label": labels[j],
                               "realised_funds": int(real.prefix[-1, 0]), "realised_pop": int(real.prefix[-1, 5]),
                               "incumbent_kept": (j == 0) if incumbent else None})
            if t == 0:
                choice0 = {"plan": plan_cur.copy(), "index": j, "score": float(score[j]), "label": labels[j]}
        else:
            months.append({"month": t, "best_index": None, "best_score": None, "label": None,
                           "realised_funds": int(real.prefix[-1, 0]), "realised_pop": int(real.prefix[-1, 5]),
                           "incumbent_kept": None})
        executed = np.concatenate([executed, plan_cur[t:t + 1]])
        last_real = real
    t0 = time.time()
    eff_exec = A.effective(executed[None], inst.task, H)
    traj = world.scalars(inst, eff_exec, seed_real)[0]
    if not np.array_equal(traj[:H], last_real.prefix):
        raise RuntimeError(f"{inst.key}: the realised trajectory differs from the realised months")
    m_real = float(A.task_margin(inst, traj[None])[0])
    pass_real = bool(T.verdict(inst.task, traj[None], inst.theta)[0])
    if pass_real != (m_real >= 0):
        raise RuntimeError(f"{inst.key}: margin sign disagrees with dc.tasks")
    # the month-0 choice: the paper's verdict, the open-loop arm on the realised seed, the majority oracle
    eff0 = A.effective(choice0["plan"][None], inst.task, H)
    vtr = model.verdict_samples(inst, eff0, A.K_VERDICT, salted(("replan-verdict", inst.task), seed_stream))
    vst = A.traj_stats(vtr)
    A.Audit._check_stats([inst], vtr, vst)
    vm = A.stats_margin(inst, vst)[0]
    p8 = float(np.mean(vm >= 0))
    accept = bool(A._fourth_largest(vm[None])[0] >= 0)
    if accept != (p8 >= A.ACCEPT_P):
        raise RuntimeError(f"{inst.key}: verdict rank and pass share disagree")
    ol = world.scalars(inst, eff0, seed_real)[0]
    m_ol = float(A.task_margin(inst, ol[None])[0])
    pass_ol = bool(T.verdict(inst.task, ol[None], inst.theta)[0])
    oj = A.oracle_judgement(inst, A.oracle_trajectories(world, inst, choice0["plan"][None], oracle_n))
    if float(oj["margin_seed0"][0]) != m_ol or bool(oj["accept_seed0"][0]) != pass_ol:
        raise RuntimeError(f"{inst.key}: the open-loop arm differs from the oracle's seed 0 (the realised seed)")
    sec["verdict_oracle_replays"] += time.time() - t0
    m1, w1 = model.counters(), world.counters()
    dm, dw = _delta(m0, m1), _delta(w0, w1)
    sec["total"] = time.time() - t_start
    rec = {
        "instance": inst.key, "task": inst.task, "cluster": inst.family_id, "start_id": inst.start_id,
        "in_band": bool(inst.in_band), "model": model.name, "realised_seed": seed_real, "n_plans": int(n_plans),
        "controller_version": int(controller_version),
        "incumbent_kept_months": sum(1 for m in months if m["incumbent_kept"]),
        "replan_months": list(range(H)) if replan_at is None else sorted(int(x) for x in replan_at),
        "accept0": accept, "replan_pass": pass_real, "open_loop_pass": pass_ol,
        "month0": {"plan": choice0["plan"].astype(int).tolist(), "plan_hash": A.plan_hash(eff0[0]),
                   "index": choice0["index"], "score": choice0["score"], "label": choice0["label"],
                   "verdict_margins": [float(x) for x in vm], "verdict_p": p8, "verdict_accept": accept},
        "executed": executed.astype(int).tolist(), "executed_plan_hash": A.plan_hash(eff_exec[0]),
        "months": months,
        "replan": {"margin": m_real, "pass": pass_real, "funds_min": int(traj[:, 0].min()), "pop_H": int(traj[-1, 5])},
        "open_loop": {"margin": m_ol, "pass": pass_ol, "oracle_accept": bool(oj["accept"][0]),
                      "oracle_share": float(oj["share"][0]), "oracle_margin": float(oj["margin"][0])},
        "counts": {"model_month_steps": int(dm.get("judge_month_steps", 0)),
                   "model_month_steps_padded": int(dm.get("judge_padded_month_steps", 0)),
                   "model_rollout_month_steps": int(rollout_ms + pair_ms + A.K_VERDICT * H),

                   "engine_city_months": int(dw.get("engine_city_months", 0)),
                   "engine_jobs": dw.get("jobs", {}), "engine_jobs_remote": int(dw.get("jobs_remote", 0))},
        "seconds": {k: float(v) for k, v in sec.items()},
    }
    if seed_stream:                 # the analysis plan; absent on the default path, whose records are unchanged
        rec["seed_stream"] = str(seed_stream)
    if controller_version == 3:     # the paired comparisons' extra work (included in the totals above)
        rec["counts"].update(paired_model_month_steps=int(pair_ms), paired_engine_city_months=int(pair_ecm))
        rec["paired_rule"] = {"samples_per_plan": PAIRED_SAMPLES, "standard_errors": SWITCH_STANDARD_ERRORS}
    return rec


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="job server for a remote replanning pool (dc.replan.host_b_replan_pool)")
    ap.add_argument("cmd", choices=["serve"])
    ap.add_argument("--workers", type=int, default=22)
    a = ap.parse_args()
    serve(a.workers)
