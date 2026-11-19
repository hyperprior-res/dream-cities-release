"""The RL arm's one adaptor to the audit pipeline (``dc.audit``) and its calls into ``dc.tasks``.

Everything the policies-in-the-emulator arm (``dc.rl``) takes from the audit goes through this module, so
a change in ``dc.audit`` is absorbed here: task instances (from a given tasks file), effective plans (the task's
forced events written into the plan), the protocol verdict seeds, the engine judge with its on-disk cache,
the emulator loaded with the model code of a tagged revision, its start states and its K-sample verdicts.

Task predicate. The margin, the statistic and the feasibility clause of an instance are read only through
``dc.tasks`` (``task_margin``, ``task_statistic``, ``task_feasible``). ``task_margin`` is the audit's own
``dc.audit.task_margin`` when that exists, so both arms compute a margin by the same call; the instance's other
tasks-file fields are passed when a ``dc.tasks`` function asks for them (``params`` or ``inst``), the audit's
convention. Nothing in ``dc.rl`` restates a clause or a threshold.

Decoding. The environment and the judge both use the tag's default decoding: the defaults of the tag's
``Emulator.rollout`` (temperature, overlay; at ``ladder-v2`` temperature 1 and everything sampled). The backend
refuses to start when the judge reports another decoding in ``describe()["decoding"]``, and the test
``test_emulator_environment_is_the_judges_process`` checks that a fixed plan stepped by the environment equals
the judge's rollout under the same torch seed, element for element.

The emulator is used in two ways:

* as the RL environment, one month at a time (``EmulatorBackend.step``: the one call site of the single-step
  sampler; the model object is the judge's, accelerated in place by ``dc.fast`` when the judge is);
* as the judge of a finished plan (``EmulatorBackend.verdict_samples``): exactly ``EmulatorJudge.samples``.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np

from . import audit as A
from . import tasks as T

H = 24
K_VERDICT = A.K_VERDICT            # 8 fresh samples for a plan's emulator verdict
VERDICT_RANK = A.VERDICT_RANK      # accepted when the 4th-largest of the 8 margins is >= 0
ACCEPT_P = A.ACCEPT_P
N_SECONDARY = A.N_SECONDARY
FORCED_COL = A.FORCED_COL
Instance = A.Instance
CACHE_ROOT = A.CACHE_ROOT
REPO = A.REPO
TASKS_JSON = REPO / "data" / "tasks_v2_H24.json"   # the default tasks file (``run_rl.py --tasks``; amendment 3)
TASKS_JSON_V1 = REPO / "data" / "tasks_H24.json"  # the first thresholds 
DEFAULT_MODEL_SRC = "ladder-v2"


# ----------------------------------------------------------------------------------------------
# Instances and tasks files
# ----------------------------------------------------------------------------------------------
def load_family(task: str, path=None) -> List[Instance]:
    """The held-out instances of one task family at H = 24 in tasks file ``path``, sorted by start id."""
    inst = [i for i in A.load_instances(Path(path) if path else TASKS_JSON, horizon=H) if i.task == task]
    return sorted(inst, key=lambda i: i.start_id)


def _sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tasks_code_sha256() -> str:
    return _sha256(Path(T.__file__))


def tasks_digest(path) -> dict:
    """What a margin depends on besides the trajectory: the tasks file (path relative to the repository when it
    lies inside it) and its sha256, and the sha256 of ``dc/tasks.py``."""
    p = Path(path).resolve()
    try:
        rel = str(p.relative_to(REPO))
    except ValueError:
        rel = str(p)
    return {"tasks_file": rel, "tasks_sha256": _sha256(p), "tasks_code_sha256": tasks_code_sha256()}


# ----------------------------------------------------------------------------------------------
# The predicate, only through dc.tasks
# ----------------------------------------------------------------------------------------------
def _task_kwargs(fn, inst: Instance) -> dict:
    sig = inspect.signature(fn).parameters
    kw = {}
    if "params" in sig:
        extra = getattr(inst, "extra", "")
        kw["params"] = json.loads(extra) if extra else {}
    if "inst" in sig:
        kw["inst"] = inst
    return kw


def task_margin(inst: Instance, scal) -> np.ndarray:
    """``dc.tasks.margin`` of the instance on scalar trajectories (..., T, 20), T = months so far + 1."""
    f = getattr(A, "task_margin", None)
    if f is not None:
        return np.asarray(f(inst, scal), dtype=np.float64)
    return np.asarray(T.margin(inst.task, scal, inst.theta, inst.stat_sd, **_task_kwargs(T.margin, inst)),
                      dtype=np.float64)


def task_statistic(inst: Instance, scal) -> np.ndarray:
    return np.asarray(T.statistic(inst.task, scal, **_task_kwargs(T.statistic, inst)), dtype=np.float64)


def task_feasible(inst: Instance, scal) -> np.ndarray:
    return np.asarray(T.feasible(inst.task, scal, **_task_kwargs(T.feasible, inst)), dtype=bool)


def forced_for(task: str) -> Dict[int, int]:
    return T.forced_for(task)


def effective(plans, task: str) -> np.ndarray:
    """Raw plans (n, H, 25) -> canonical int16 (n, H, 25) with the task's forced events (``dc.audit.effective``)."""
    return A.effective(plans, task, H)


def primary_seed(inst: Instance) -> int:
    return A.primary_seed(inst)


def verdict_seeds(inst: Instance) -> List[int]:
    """Primary seed first, then the eight secondary seeds (protocol)."""
    return A.verdict_seeds(inst, N_SECONDARY)


def plan_hash(a: np.ndarray) -> str:
    return A.plan_hash(a)


# ----------------------------------------------------------------------------------------------
# Seeds the RL arm must not use, and the seed-majority oracle (amendment 3)
# ----------------------------------------------------------------------------------------------
def reserved_seeds(start_id: str) -> frozenset:
    """Every seed a judge or a policy must not use on a start: the nine residual seeds and the oracle's seeds of
    every task (``dc.audit.reserved_seeds``)."""
    return A.reserved_seeds(start_id, H, T.ORACLE_N, N_SECONDARY)


def fresh_seed(keys: tuple, reserved) -> tuple:
    """``seed_for(*keys)``, redrawn past the reserved seeds (``dc.audit.fresh_seed``): (seed, redraws)."""
    return A.fresh_seed(tuple(keys), reserved)


def oracle_n(tasks_path) -> int:
    """Seeds of the oracle: the tasks file's ``meta.oracle.n_seeds`` (checked by ``dc.audit.oracle_spec``), else
    ``dc.tasks.ORACLE_N`` (a tasks file of the first thresholds names no oracle; amendment 3 applies to all)."""
    spec = A.oracle_spec(tasks_path)
    return int(spec["n_seeds"]) if spec else int(T.ORACLE_N)


def oracle_trajectories(engine, inst: Instance, plans, n_seeds: int) -> np.ndarray:
    """(n, n_seeds, H+1, 20) engine trajectories of plans on the instance's oracle seeds (``dc.audit``, cached)."""
    A.check_oracle_seeds(inst, n_seeds, N_SECONDARY)
    return A.oracle_trajectories(engine, inst, plans, n_seeds=n_seeds)


def oracle_judgement(inst: Instance, traj) -> dict:
    """``dc.audit.oracle_judgement``: per-seed margins and verdicts, pass share, majority verdict and margin, seed 0."""
    return A.oracle_judgement(inst, traj)


def fourth_largest(m: np.ndarray) -> np.ndarray:
    return np.sort(m, axis=-1)[..., -VERDICT_RANK]


def engine_judge(workers: int = 8, cache_root=None, log=print):
    """the cached engine judge (``dc.audit.EngineJudge``); ``cache_root`` defaults to the audit's cache."""
    root = Path(cache_root) if cache_root is not None else A.CACHE_ROOT / "engine_cache"
    return A.EngineJudge(root, workers=int(workers), H=H, log=log)


def behaviour_plans(start_id: str, n: int) -> np.ndarray:
    """The first n behaviour-mix plans of a start (forced column cleared), int16 (n, H, 25)."""
    return np.asarray(A.Pools(H).behaviour(start_id)[:n])


def tag_package(model_src: str):
    """The ``dc`` package of a git revision (``dc.audit.code_package``): (package, commit sha)."""
    return A.code_package(model_src)


# ----------------------------------------------------------------------------------------------
# The emulator
# ----------------------------------------------------------------------------------------------
def tag_decoding(model) -> dict:
    """The tag's default decoding: the defaults of its ``Emulator.rollout`` (temperature, overlay)."""
    prm = inspect.signature(model.rollout).parameters
    return {"temperature": float(prm["temperature"].default), "overlay": str(prm["overlay"].default)}


class EmulatorBackend:
    """A checkpoint loaded by ``dc.audit.EmulatorJudge`` with the model code of ``model_src``."""

    def __init__(self, ckpt, device: str = "cuda:0", model_src: str = DEFAULT_MODEL_SRC, compile_trunk: bool = False,
                 chunk: int = 128, buckets: Sequence[int] = (16, 64, 128), fast: bool = True) -> None:
        import torch
        self.torch = torch
        self.judge = A.EmulatorJudge(ckpt, device=device, chunk=chunk, buckets=buckets, compile_trunk=compile_trunk,
                                     model_src=model_src, H=H, fast=fast)
        self.model = self.judge.model        # the judge's own model object: accelerated in place when the judge is
        self.device = self.judge.device
        self.decoding = tag_decoding(self.model)
        jd = self.judge.describe().get("decoding", {}) or {}
        try:
            judge_dec = (float(jd["temperature"]), str(jd["overlay"]))
        except (KeyError, TypeError, ValueError):
            raise RuntimeError(f"dc.audit.EmulatorJudge.describe() reports no decoding the environment can match: {jd!r}")
        if judge_dec != (self.decoding["temperature"], self.decoding["overlay"]):
            raise RuntimeError(f"the audit judge rolls out with decoding {judge_dec}, the tag's default is "
                               f"{self.decoding}: the environment and the judge would be different processes")
        self.temperature = self.decoding["temperature"]
        self.overlay = self.decoding["overlay"]
        self.month_steps = 0          # environment month-steps taken through ``step``

    def describe(self) -> dict:
        return {**self.judge.describe(), "environment_decoding": dict(self.decoding)}

    def start_state(self, inst: Instance) -> Dict[str, "object"]:
        """One-row start state on the device (the judge's own: the engine's observation after the load)."""
        return self.judge.state0(inst)

    def step(self, state: dict, raster, act):
        """One month for every row under the tag's default decoding."""
        B = state["tile_index"].shape[0]
        # ---- B10 FAST PATH: the one call site of the emulator's single-step sampler in the RL arm; nothing else in
        # ---- dc.rl calls sample_next. The audit judge accelerates its model in place (dc.fast, the analysis plan: on a
        # ---- GPU with a compiled trunk, ``fast=True``), and this is the same object, so environment and judge run
        # ---- the same trunk.
        if self.model is not self.judge.model:
            raise RuntimeError("the environment must step the judge's own model object")
        out = self.model.sample_next(state, raster.to(state["flags"].dtype), act.float(), temperature=self.temperature,
                                     max_batch=B, overlay=self.overlay)
        self.month_steps += B
        return out

    def verdict_samples(self, inst: Instance, eff_plans: np.ndarray, K: int, stream: tuple) -> np.ndarray:
        """(n, K, H+1, 20) sampled scalar trajectories of effective plans (``EmulatorJudge.samples``)."""
        return self.judge.samples(inst, eff_plans, K, stream)

    def judge_counters(self) -> dict:
        return self.judge.counters()
