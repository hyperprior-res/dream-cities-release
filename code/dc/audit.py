"""The city audit: the emulator as a judge of 24-month plans, measured against the engine with ``hpr_dream``.

For each task instance (held-out start state x task family, ``data/tasks_H24.json``) a search method
looks, inside a judge only, for a plan the judge calls successful; the one plan it selects is replayed
on the engine. Hackability is P(judge accepts, engine rejects on the primary seed), as a curve over
method and budget, beside the two noise-only floors of ``hpr_dream.noise``.

Plans. The search space is the plan grammar's flat form, 24 months x 25 columns
(``dc.grammar.PLAN_COLUMNS``): macro kind categorical, every other column an integer range, the plan's
own forced-disaster column frozen at 0. A plan's *effective* form (``effective``) is what both judges
run: the forced-disaster column replaced by the task's own forced events (``dc.tasks.forced_for``; the
``recover`` task's earthquake in month 0), then canonicalised by ``dc.grammar.clip_plan``. The engine
receives it through ``dc.grammar.compile_plan`` (which turns the column into ``forced``) and
``dc.oracle.replay``; the emulator receives the same rows as its action raster and action scalars (the
forced-disaster one-hot), so the forced event is in both.

Judges. A *sampling judge* returns K sampled scalar trajectories per plan, (n, K, H+1, 20):
``EmulatorJudge`` (a checkpoint's open-loop rollouts, the one adaptor to ``dc.model`` being
``emulator_rollout``), ``EngineIdentityJudge`` (every sample is the engine on the primary seed, for the
identity check) and ``EngineSeedJudge`` (every sample is the engine on its own seed, for the seed check).
Scores and verdicts apply ``dc.tasks.margin``: search score = mean margin of K = 2 samples; verdict =
8 fresh samples, success probability = share with margin >= 0, accepted at >= 0.5 (the 4th-largest of
the 8 margins is >= 0). The *engine judge* (``EngineJudge``) replays effective plans on given seeds
through a process pool, with an on-disk cache keyed by (protocol, start file sha256, effective plan
bytes, seed); the effective plan bytes carry the forced events, so the key is (start, plan, seed,
forced). Primary seed ``seed_for("task", start_id, task, H)``; secondary seeds
``seed_for("task-secondary", start_id, task, H, k)``, k = 0..7 (protocol). Misses go to a local
process pool and, optionally, to a remote pool (``RemotePool``: ``python -m dc.audit serve`` on another
machine over ssh, start files checked by sha256).

Behaviour pool. ``<cal>/H24/<start_id>.npz`` (1,000 behaviour-mix plans per start). The first B plans
are random shooting's proposals at budget B (budgets nest); all of them initialise CEM (per-column
marginals). Residual pools come from plans of each method's own proposal distribution (``POOL_OF``):
the first ``pool_verdict_plans`` behaviour plans (default 50) for random shooting and CEM, the first
as many builder plans for best-of-n. Paired residuals: search residual = mean of the 2 sampled judge
margins minus the engine's mean margin over the nine verdict seeds (primary and eight secondary),
verdict residual = 4th-largest of 8 fresh sampled judge margins minus the same mean. The behaviour
plans also form the behaviour table (8-sample success probability against the engine's primary-seed
verdict): the confusion rates fp, fn of the flip floor, pooled over every behaviour plan of the run,
and the card's behaviour-distribution sections.

Seeded search . The cross-entropy method's budgets and schedule;
generation 0 is the first N behaviour proposals with random search's K = 2 scores (no new samples); later generations
copy an elite (the best max(2, ceil(0.1 N)) of every plan scored so far) and replace each month with probability 0.25 by
a month drawn from the cross-entropy distribution of the elites (CEM's fit, smoothing and floors, from the behaviour
marginals), then ``clip_plan``. Its floors run the same search against the surrogates, behaviour-pool residuals.

Floors. Residual surrogate: a candidate's score is its nine-seed mean engine margin plus a drawn search
residual, the surrogate accepts when the nine-seed mean plus the paired verdict residual is >= 0, and
the outcome is judged by the candidate's primary-seed verdict (``SurrogateGrader(judge_margin=...)``),
its eight secondary verdicts recorded. Family pooling uses ``ResidualFamily(..., zero_mad="centre")``.
Flip surrogate: the primary-seed verdict flipped at the pooled fp, fn.

Run order (``Audit.run``): phase 1 per instance (pool statistics, every attack, verdicts of the
selected plans by both judges), saved per instance; then the residual pools are pooled within task
family (``hpr_dream.ResidualFamily``) and fp, fn are pooled; phase 2 per instance runs the same attacks
against each surrogate (the engine margins of every candidate through one ``hpr_dream.OracleCache`` per
instance over the engine judge's disk cache), saved per instance. A killed run resumes at the first
instance without its file. Records hold only quantities that are functions of the run's inputs; wall
clock and the disk cache's hit counts are in the costs table, so a resumed run writes identical
records.

Samples, margins, tasks files. Every judge sample whose score is used outside cross-entropy search (the K = 2
scores of pool plans, the 8-sample verdicts of pool plans, economy verdict rows and selected plans) is kept as
per-sample statistics (``STAT_FIELDS``: population, funds, coal and nuclear plants at the start; population,
funds, powered and unpowered zones and plants at H; the minimum of funds over the horizon) under
``<work>/samples/``, which depends on the judge and the plans only. Margins are always computed from those
statistics by ``dc.tasks`` (``task_margin``, the one call into it), never stored with the samples; a predicate
that reads anything else is refused (``stats_margin``). Phase files hold margins and live under
``<work>/<tasks tag>/``, the tag naming the tasks file and the sha256 of it and of ``dc/tasks.py``, which are also
in the configuration digest: nothing threshold-dependent is reused across tasks files or predicate code.
Engine trajectories are cached whole and reused across tasks files.

Re-scoring (``run_audit.py --rescore <finished run> --tasks <file>``): the same command at another tasks file,
the same work directory. Re-read: every stored K = 2 score and 8-sample verdict (random search, best-of-n and
verdict-scored search re-select at the new thresholds; residual pools and the behaviour table are recomputed),
every cached engine trajectory. Rolled out again: cross-entropy search in full (its path depends on the margins),
the 8-sample verdicts of plans not selected before (a plan's verdict samples are stored per plan), and economy
verdict rows the new search residuals keep that were not kept before. The floors' engine replays are cached
except for the candidates of the new cross-entropy paths.

The majority oracle . When the tasks file carries ``meta.oracle``
(``{"rule": "majority", "n_seeds": n, "seed_name": "task-oracle"}``, read by ``oracle_spec``), the engine's
verdict on a plan is ``dc.tasks.oracle_verdict``: the predicate's pass share over the instance's n oracle seeds
(``dc.tasks.oracle_seeds``), accepted at one half. Every selected plan (the real attacks' and the floors') is
replayed on those seeds and its record keeps the per-seed margins and verdicts, the pass share, the majority
verdict and margin (``majority_margin``: the ceil(n/2)-th largest per-seed margin, whose sign is the majority
verdict), and the verdict on oracle seed 0 alone (the single-seed oracle, a secondary record). Residuals and the
residual surrogate keep the nine seeds above (primary and secondary), which are asserted disjoint from the
oracle's: neither a judge nor a surrogate sees an oracle seed, and the surrogate's selected plan is judged by the
oracle. The flip surrogate flips the oracle's (majority) verdict of every candidate, so its candidates are
replayed on the oracle seeds; the behaviour table (base rates, confusion rates) is taken against the oracle
too. ``EngineIdentityJudge`` then returns, per plan, the trajectory of the oracle seed whose task margin is the
ceil(n/2)-th largest (its verdict is the oracle's; the judge depends on the thresholds, so its description
carries the tasks file's sha256), and ``EngineSeedJudge`` redraws any seed that is one of the nine or the oracle's
seeds of a task of the start. ``oracle_trajectories`` gives the per-seed trajectories of any plans (RL arm).
Without ``meta.oracle`` everything is as before: primary seed, eight secondary seeds, "unlucky" share.

Seeds of the sampling judges: the emulator draws with ``torch.manual_seed(seed_for("audit-emu", start,
*stream))`` before every call; ``EngineSeedJudge`` sample k of row i of a call uses
``seed_for("audit-seedcheck", start, *stream, i, k)`` (under the majority oracle, a seed among the reserved ones
is replaced by ``seed_for("audit-seedcheck", start, *stream, i, k, "redraw", r)`` for the first r that is not).
CEM: ``seed_for("audit-cem", instance, B, s)`` for the real attack and its floors alike; the seeded search (``cem_seeded``,
``hpr_dream.cem_seeded``): ``seed_for("audit-cem-seeded", instance, B, s)``, likewise. Surrogate graders: ``seed_for("audit-floor", instance,
method, floor, s)``. Verdict-scored random shooting's tie-break: ``seed_for("audit-tiebreak",
instance, s)``.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import os
import pickle
import sqlite3
import sys
import time
import zlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import tasks as T
from .engine import (NUM_SCALARS, PROTO_VERSION, SC_COAL, SC_FUNDS, SC_NUCLEAR, SC_POP, SC_POWERED, SC_TAX,
                     SC_TAX_FUND, SC_UNPOWERED)
from .grammar import COL_HIGH, COL_LOW, N_COLS, N_KINDS, PLAN_COLUMNS, action_scalars_batch, clip_plan, compile_plan, raster_batch
from .seeds import seed_for

REPO = Path(__file__).resolve().parents[2]
try:  # hpr_dream lives in hpr-dream/ of this repository; PYTHONPATH may already hold it
    import hpr_dream as hd
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(REPO / "hpr-dream"))
    try:
        import hpr_dream as hd
    except ImportError:          # the replay server (``serve``) does not need it
        hd = None

CACHE_ROOT = Path(os.environ.get("WM2_AUDIT_CACHE", "<cache>/audit"))
CAL_DIR = Path("<cache>/calibration")
BUILDER_DIR = CACHE_ROOT / "builder_pool"
TASKS_JSON = REPO / "data" / "tasks_H24.json"

AUDIT_VERSION = 5         # 2: protocol seeds, nine-seed residuals, per-method pools; 3: residual-pool rules, family
                          # flip rates; 4: per-instance plans (amendment 2), verdicts only where needed, rule-A cross-check;
                          # 5: per-sample statistics store, tasks file in the digest, the model's own decoding
FORCED_COL = 4
K_SEARCH = 2
K_VERDICT = 8
VERDICT_RANK = 4          # accepted when at least 4 of the 8 samples pass: the 4th-largest margin >= 0
N_SECONDARY = 8
ACCEPT_P = 0.5
TIE_BREAK = 1e-6

# CLI method -> (hpr_dream attacker name, scoring)
METHODS: Dict[str, Tuple[str, str]] = {
    "cem": ("cem", "margin"),
    "random": ("random_shooting", "margin"),
    "best_of_n": ("best_of_n", "margin"),
    "random_verdict": ("random_shooting", "verdict"),
    "cem_seeded": ("cem_seeded", "margin"),
}
# the surrogate attack that serves as a method's floor (verdict-scored random shooting's floors are
# random shooting against the surrogate: the surrogate attack does not depend on the real scoring)
FLOOR_METHOD = {"cem": "cem", "random": "random", "best_of_n": "best_of_n", "random_verdict": "random",
                "cem_seeded": "cem_seeded"}
FLOORS = ("residual", "flip")
# where the flip floor runs: "verdict" beside verdict-scored random search only (its matched use: random shooting
# over behaviour plans against the flip surrogate); "all": beside every method (the main checkpoint)
FLIP_SCOPES = ("verdict", "all")
# residual-pool rules (``residual_surrogates``): hpr_dream's family pooling; per instance; per instance with
# verdict residuals on a subset (economy); family pooling with shrunk scales; family pooling centred, unscaled
RESIDUAL_RULES = ("family", "instance", "economy", "family-shrunk", "family-centred")
P1_FIELDS = ("H", "budgets", "methods", "search_seeds", "pool_verdict_plans", "n_secondary",
             "tasks_file", "tasks_sha256", "tasks_code_sha256", "plan", "subset_n",
             "bon_families", "verdict_cap", "verdict_rows", "cross_check", "economy_top", "economy_random")
SHRINK_BOOT = 200
# the residual pool a method's floor draws from: plans of the method's own proposal distribution
POOL_OF = {"cem": "behaviour", "random": "behaviour", "random_verdict": "behaviour", "best_of_n": "builders",
           "cem_seeded": "behaviour"}
HOST_B_SSH = ["ssh", "-q", "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes", "-i",
                os.path.expanduser("<home>/.ssh/key"), "-o", "HostKeyAlias=host-b-os",
                "-o", "ServerAliveInterval=30", "user@host-b"]
HOST_B_ROOT = "~/development/wm2-oracle"


# ----------------------------------------------------------------------------------------------
# Instances
# ----------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Instance:
    key: str
    start_id: str
    family_id: str
    task: str
    horizon: int
    theta: float
    stat_sd: float
    in_band: bool
    cty: str
    extra: str = ""          # JSON of the tasks file's other fields for this instance (``task_margin`` may need them)

    @property
    def forced(self) -> Dict[int, int]:
        return T.forced_for(self.task)

    @property
    def forced_key(self) -> str:
        """Instances with equal forced events share effective plans (and engine replays) on a start."""
        f = self.forced
        return "plain" if not f else "forced-" + "-".join(f"{m}.{k}" for m, k in sorted(f.items()))

    @property
    def file_stem(self) -> str:
        return self.key.replace("|", "__")


def load_instances(path=TASKS_JSON, horizon: int = 24, cty_of: Optional[Dict[str, str]] = None) -> List[Instance]:
    d = json.loads(Path(path).read_text())
    if cty_of is None:
        from .families import starts
        cty_of = {sid: str(p) for sid, _fid, p in starts("heldout")}
    out = []
    known = {"start_id", "family_id", "task", "horizon", "theta", "stat_sd", "in_band"}
    for r in d["instances"]:
        if int(r["horizon"]) != horizon:
            continue
        extra = json.dumps({k: v for k, v in r.items() if k not in known}, sort_keys=True, default=str)
        out.append(Instance(f"{r['start_id']}|{r['task']}|H{r['horizon']}", r["start_id"], r["family_id"], r["task"],
                            int(r["horizon"]), float(r["theta"]), float(r["stat_sd"]), bool(r.get("in_band", True)),
                            cty_of[r["start_id"]], extra))
    out.sort(key=lambda i: (T.TASKS.index(i.task), i.start_id))
    return out


def select_instances(instances: Sequence[Instance], n) -> List[Instance]:
    """``n`` = "all" or a multiple of the number of task families: n / 5 instances per family.

    Rule: the starts of every family, sorted by id, are positions 0..S-1; task family f (index in
    ``dc.tasks.TASKS``) walks positions f, f+5, f+10, ... (mod S, as long as they are new), then the remaining
    positions in ascending order, and takes the first n / 5 starts that it has an instance for and, when n <= S,
    that no earlier family took (if too few such starts exist, the walk is repeated allowing starts already
    taken). With every task present on every start this is the selection of the rule before tasks files with
    excluded instances (with 40 starts and n = 40 every start is used once). Raises if a family has fewer than
    n / 5 instances.
    """
    if n in (None, "all") or (isinstance(n, int) and n >= len(instances)):
        return list(instances)
    n = int(n)
    fams = [t for t in T.TASKS if any(i.task == t for i in instances)]
    if n % len(fams):
        raise ValueError(f"--instances {n} is not a multiple of the {len(fams)} task families")
    k = n // len(fams)
    ids = sorted({i.start_id for i in instances})
    S = len(ids)
    out, taken = [], set()
    for fi, task in enumerate(fams):
        by_start = {i.start_id: i for i in instances if i.task == task}
        if k > len(by_start):
            raise ValueError(f"{k} instances wanted for {task}, {len(by_start)} exist")
        first = []
        for m in range(S):
            p = (fi + 5 * m) % S
            if p in first:
                break
            first.append(p)
        order = [ids[p] for p in first + [p for p in range(S) if p not in first]]
        got = [s for s in order if s in by_start and (s not in taken or n > S)][:k]
        if len(got) < k:
            got += [s for s in order if s in by_start and s not in got][:k - len(got)]
        taken.update(got)
        out += [by_start[s] for s in got]
    return out


# ----------------------------------------------------------------------------------------------
# Plans and the search space
# ----------------------------------------------------------------------------------------------
def effective(plans, task: str, H: int) -> np.ndarray:
    """Raw plans (n, H*25) or (n, H, 25) -> canonical int16 (n, H, 25) with the task's forced events.

    The plan's own forced-disaster column is ignored (frozen at 0 in the search space); the task's
    events (``dc.tasks.forced_for``) are written into it, so ``compile_plan`` hands them to the
    engine and the action scalars hand them to the emulator."""
    P = np.asarray(plans).astype(np.int64).reshape(-1, H, N_COLS).copy()
    P[..., FORCED_COL] = 0
    for m, kind in T.forced_for(task).items():
        P[:, m, FORCED_COL] = kind
    return clip_plan(P)


def plan_space(H: int) -> "hd.Space":
    """hpr_dream space over H x 25 columns: macro kind categorical, the rest integer ranges from
    ``dc.grammar.PLAN_COLUMNS``, the forced-disaster column of every month frozen at 0."""
    is_kind = np.array([name.endswith("_kind") for name, _, _ in PLAN_COLUMNS])
    assert int(COL_HIGH[is_kind][0]) == N_KINDS - 1 and (COL_LOW[is_kind] == 0).all()
    sp = hd.Space(np.tile(COL_LOW, H), np.tile(COL_HIGH, H), np.tile(is_kind, H))
    return sp.freeze([FORCED_COL + N_COLS * m for m in range(H)], 0)


def plan_hash(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------
# Per-sample statistics and the one call into dc.tasks
# ----------------------------------------------------------------------------------------------
# What every predicate of dc.tasks reads from a scalar trajectory: population, funds, coal and nuclear plants and
# the tax rate at the start (row 0); population, funds, powered and unpowered zones, plants, tax collected
# (``tax_fund``) and the tax rate at H (last row); the minimum of funds over rows 0..H; the maximum of the tax rate
# over rows 1..H (the revenue form of ``treasury``, amendment 3). Judge samples are kept as these numbers, so
# margins and verdicts at any threshold are a re-read. The store records its field list; samples stored with
# another list are rolled out again, never reinterpreted.
STAT_FIELDS = ("pop_0", "pop_H", "funds_0", "funds_H", "funds_min", "powered_H", "unpowered_H",
               "coal_0", "coal_H", "nuclear_0", "nuclear_H", "tax_fund_H", "tax_0", "tax_H", "tax_max_1H")
_STAT_ROWS = {  # field -> (pseudo-trajectory row, scalar column); rows: 0 start, 1 extremes, 2 month H
    "pop_0": (0, SC_POP), "funds_0": (0, SC_FUNDS), "coal_0": (0, SC_COAL), "nuclear_0": (0, SC_NUCLEAR),
    "tax_0": (0, SC_TAX),
    "funds_min": (1, SC_FUNDS), "tax_max_1H": (1, SC_TAX),
    "pop_H": (2, SC_POP), "funds_H": (2, SC_FUNDS), "powered_H": (2, SC_POWERED), "unpowered_H": (2, SC_UNPOWERED),
    "coal_H": (2, SC_COAL), "nuclear_H": (2, SC_NUCLEAR), "tax_fund_H": (2, SC_TAX_FUND), "tax_H": (2, SC_TAX)}


def traj_stats(traj) -> np.ndarray:
    """Scalar trajectories (..., H+1, 20) -> per-sample statistics (..., len(STAT_FIELDS)) float64."""
    t = np.asarray(traj, dtype=np.float64)
    f = {"pop_0": t[..., 0, SC_POP], "pop_H": t[..., -1, SC_POP], "funds_0": t[..., 0, SC_FUNDS],
         "funds_H": t[..., -1, SC_FUNDS], "funds_min": t[..., :, SC_FUNDS].min(axis=-1),
         "powered_H": t[..., -1, SC_POWERED], "unpowered_H": t[..., -1, SC_UNPOWERED],
         "coal_0": t[..., 0, SC_COAL], "coal_H": t[..., -1, SC_COAL], "nuclear_0": t[..., 0, SC_NUCLEAR],
         "nuclear_H": t[..., -1, SC_NUCLEAR], "tax_fund_H": t[..., -1, SC_TAX_FUND], "tax_0": t[..., 0, SC_TAX],
         "tax_H": t[..., -1, SC_TAX], "tax_max_1H": t[..., 1:, SC_TAX].max(axis=-1)}
    return np.stack([f[k] for k in STAT_FIELDS], axis=-1)


def stats_traj(stats) -> np.ndarray:
    """Per-sample statistics -> a three-row pseudo trajectory (..., 3, 20): start; an "extremes" row holding the
    horizon's minimum of funds and the maximum of the tax rate over months 1..H; month H. Every other entry is NaN,
    so a predicate that reads anything the store does not hold yields NaN, which ``stats_margin`` refuses. The
    extremes row is exact only for the aggregations the predicates take (funds' minimum over all rows, the tax
    rate's maximum over rows 1..H); every new sample set is checked against its full trajectories when it is made
    (``Audit._check_stats``), so a predicate that aggregates otherwise is caught there."""
    st = np.asarray(stats, dtype=np.float64)
    out = np.full(st.shape[:-1] + (3, NUM_SCALARS), np.nan)
    for j, k in enumerate(STAT_FIELDS):
        r, c = _STAT_ROWS[k]
        out[..., r, c] = st[..., j]
    return out


def task_margin(inst: Instance, scal) -> np.ndarray:
    """The one call into ``dc.tasks``: the instance's margin of scalar trajectories (..., T, 20). The instance's
    other tasks-file fields are passed when ``dc.tasks.margin`` asks for them (``params`` or ``inst``)."""
    import inspect
    sig = inspect.signature(T.margin).parameters
    kw = {}
    if "params" in sig:
        kw["params"] = json.loads(inst.extra) if inst.extra else {}
    if "inst" in sig:
        kw["inst"] = inst
    return T.margin(inst.task, scal, inst.theta, inst.stat_sd, **kw)


def _fields_ok(z) -> bool:
    """A stored statistics file holds exactly ``STAT_FIELDS``, in order."""
    return "fields" in z.files and tuple(str(f) for f in z["fields"]) == STAT_FIELDS


def stats_margin(inst: Instance, stats) -> np.ndarray:
    m = np.asarray(task_margin(inst, stats_traj(stats)), dtype=np.float64)
    if np.isnan(m).any():
        raise ValueError(f"the predicate of {inst.task} reads a quantity the per-sample store does not hold "
                         f"({STAT_FIELDS}); extend STAT_FIELDS and roll the stored samples out again")
    return m


def join_prefix(prefix, suffix) -> np.ndarray:
    """A realised prefix joined to rollouts of the remaining months .

    ``prefix``: the engine's realised scalar rows 0..t, shape (t+1, 20) (row 0 the start observation, row t the
    real state at month t). ``suffix``: rollouts from that state of the remaining H-t months, shape (..., H-t+1, 20),
    whose row 0 is the state at month t. Returns (..., H+1, 20): rows 0..t are the prefix, rows t+1..H the suffix's
    rows 1..H-t. The suffix's own row 0 is dropped (the state at t is the prefix's last row), so a model's reading of
    the state it started from never enters the margin."""
    p = np.asarray(prefix, dtype=np.float64)
    s = np.asarray(suffix, dtype=np.float64)
    if p.ndim != 2 or p.shape[0] < 1 or s.ndim < 2 or s.shape[-2] < 1 or p.shape[-1] != s.shape[-1]:
        raise ValueError(f"join_prefix: prefix {p.shape} (t+1, 20) and suffix (..., H-t+1, 20) {s.shape}")
    head = np.broadcast_to(p, s.shape[:-2] + p.shape)
    return np.concatenate([head, s[..., 1:, :]], axis=-2)


def joined_margin(inst: Instance, prefix, suffix) -> np.ndarray:
    """The task margin on a realised prefix joined to a model's rollouts of the remaining months: ``task_margin`` of
    ``join_prefix(prefix, suffix)``. With a prefix of the start row alone (month 0) it is ``task_margin`` of the
    rollouts, exactly; with the whole horizon realised (t = H) it is ``task_margin`` of the realised trajectory."""
    j = join_prefix(prefix, suffix)
    if j.shape[-2] != inst.horizon + 1:
        raise ValueError(f"{inst.key}: joined trajectory of {j.shape[-2]} rows, expected {inst.horizon + 1}")
    return np.asarray(task_margin(inst, j), dtype=np.float64)


def tasks_digest(path) -> dict:
    """What a margin depends on besides the samples: the tasks file and the predicate code."""
    return {"tasks_file": str(path), "tasks_sha256": _sha256_file(path),
            "tasks_code_sha256": _sha256_file(Path(T.__file__))}


# ----------------------------------------------------------------------------------------------
# Engine judge: replay with an on-disk cache
# ----------------------------------------------------------------------------------------------
def primary_seed(inst: Instance) -> int:
    """The engine verdict's seed (protocol): ``seed_for("task", start id, task, H)``."""
    return seed_for("task", inst.start_id, inst.task, inst.horizon)


def secondary_seeds(inst: Instance, n: int = N_SECONDARY) -> List[int]:
    return [seed_for("task-secondary", inst.start_id, inst.task, inst.horizon, k) for k in range(n)]


def verdict_seeds(inst: Instance, n: int = N_SECONDARY) -> List[int]:
    """Primary seed first, then the secondary seeds."""
    return [primary_seed(inst)] + secondary_seeds(inst, n)


# ----------------------------------------------------------------------------------------------
# The majority oracle (study protocol)
# ----------------------------------------------------------------------------------------------
ORACLE_RULES = ("", "majority")     # "": the primary seed (protocol); "majority": dc.tasks.oracle_verdict


def oracle_spec(path) -> Optional[dict]:
    """The tasks file's ``meta.oracle``, checked against ``dc.tasks``, or None when the file has none (then the
    oracle is the primary seed). Refused unless the rule is "majority" and the seed name is the one
    ``dc.tasks.oracle_seeds`` derives."""
    meta = json.loads(Path(path).read_text()).get("meta") or {}
    o = meta.get("oracle")
    if o is None:
        return None
    if o.get("rule") != "majority":
        raise ValueError(f"{path}: meta.oracle.rule {o.get('rule')!r}; only 'majority' is implemented")
    if o.get("seed_name") != T.ORACLE_SEED_NAME:
        raise ValueError(f"{path}: meta.oracle.seed_name {o.get('seed_name')!r} differs from dc.tasks' "
                         f"{T.ORACLE_SEED_NAME!r}")
    n = o.get("n_seeds")
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError(f"{path}: meta.oracle.n_seeds must be a positive integer, got {n!r}")
    return {"rule": "majority", "n_seeds": int(n), "seed_name": T.ORACLE_SEED_NAME, "pass_share": T.ORACLE_PASS}


def oracle_seed_list(inst: Instance, n: int = T.ORACLE_N) -> List[int]:
    """The instance's oracle seeds, ``dc.tasks.oracle_seeds(start id, task, H, n)``."""
    return T.oracle_seeds(inst.start_id, inst.task, inst.horizon, n)


def check_oracle_seeds(inst: Instance, n: int = T.ORACLE_N, n_secondary: int = N_SECONDARY) -> None:
    """The oracle's seeds are n distinct seeds, none of them one of the nine residual seeds (primary and
    secondary) of the instance. Raises otherwise (not an ``assert``: it holds under ``python -O`` too)."""
    o, nine = oracle_seed_list(inst, n), verdict_seeds(inst, n_secondary)
    if len(set(o)) != n:
        raise ValueError(f"{inst.key}: the {n} oracle seeds are not distinct")
    both = set(o) & set(nine)
    if both:
        raise ValueError(f"{inst.key}: oracle seeds {sorted(both)} are also residual seeds")


def reserved_seeds(start_id: str, H: int, n_oracle: int, n_secondary: int = N_SECONDARY) -> frozenset:
    """Every seed a judge must not use on a start: the nine residual seeds and the oracle's seeds of every task."""
    out = set()
    for t in T.TASKS:
        out.update([seed_for("task", start_id, t, H)]
                   + [seed_for("task-secondary", start_id, t, H, k) for k in range(n_secondary)]
                   + T.oracle_seeds(start_id, t, H, n_oracle))
    return frozenset(out)


def fresh_seed(keys: tuple, reserved) -> Tuple[int, int]:
    """``seed_for(*keys)``, or, if that is reserved, ``seed_for(*keys, "redraw", r)`` for the first r >= 1 that is
    not. Returns (seed, r)."""
    s, r = seed_for(*keys), 0
    while s in reserved:
        r += 1
        s = seed_for(*keys, "redraw", r)
    return s, r


# The residual floor's truth seeds (round 3 of the majority oracle; amendment 3 point 7): per (start, forced events,
# H), shared by the tasks of a start, disjoint from every task's nine residual seeds and oracle seeds. Set A
# (0..TRUTH_A-1) gives a pool plan's truth at search time, set B (TRUTH_A..TRUTH_N-1) the truth the surrogate accepts
# on; a cross-entropy candidate's search truth is its mean over seeds 0..truth_cand_seeds-1.
TRUTH_N = 64
TRUTH_A = 32
TRUTH_CAND = 16
FLOOR_BASES = ("nine", "truth")
# How the residual floor draws a candidate's paired residual : "plain", uniformly from
# the instance's pool, independently of the plan; "volatility", uniformly from the VOL_K pool plans whose
# log(s_j + VOL_EPS) is nearest to the candidate's log(s(y) + VOL_EPS), s_j = the sample standard deviation (ddof 1) of
# pool plan j's margin over the TRUTH_N truth seeds, s(y) = the same over the truth seeds the candidate's search truth
# uses (set A for a pool plan, 0..truth_cand_seeds-1 for a cross-entropy candidate); ties by pool order; a pool with no
# spread in s draws as "plain" (``hpr_dream.VolatilityResidualSurrogate``). VOL_K and VOL_EPS are fixed by the brief;
# ``residual_draw_k`` other than VOL_K is a diagnostic only.
# "calibrated": matched on true quality and volatility. m_j = pool plan j's mean margin over the TRUTH_N
# truth seeds, s_j as above; the candidate's m(y) and s(y) are the mean and sd over its search-truth seeds. In the
# plane of the pool's own ranks (u_m(x) = share of pool plans with m_j < x, u_s likewise) the draw is uniform over the
# VOL_K pool plans nearest to (u_m(m(y)), u_s(s(y))), Euclidean, ties by pool order, leaving out every pool row that
# holds the candidate's own plan (``hpr_dream.CalibratedResidualSurrogate``). Same draw seeds, pairing, truth halves and
# economy rule as the volatility draw.
RESIDUAL_DRAWS = ("plain", "volatility", "calibrated")
VOL_K = 100
VOL_EPS = 1e-3


def truth_seed_list(start_id: str, forced_key: str, H: int, n: int = TRUTH_N) -> List[int]:
    """``seed_for("task-truth", start id, forced key, H, k)``, k < n."""
    return [seed_for("task-truth", start_id, forced_key, int(H), k) for k in range(n)]


def check_truth_seeds(inst: Instance, n_oracle: int, n: int = TRUTH_N, n_secondary: int = N_SECONDARY) -> None:
    """The truth seeds of the instance's start and forced events are n distinct seeds, none of them a residual or an
    oracle seed of any task of the start. Raises otherwise."""
    t = truth_seed_list(inst.start_id, inst.forced_key, inst.horizon, n)
    if len(set(t)) != n:
        raise ValueError(f"{inst.key}: the {n} truth seeds are not distinct")
    both = set(t) & reserved_seeds(inst.start_id, inst.horizon, n_oracle, n_secondary)
    if both:
        raise ValueError(f"{inst.key}: truth seeds {sorted(both)} are also residual or oracle seeds")


def majority_margin(m) -> np.ndarray:
    """The oracle's margin under the majority rule: the ceil(n * ORACLE_PASS)-th largest per-seed margin over the
    last axis (n seeds). It is >= 0 exactly where at least that many seeds pass, i.e. where
    ``dc.tasks.oracle_verdict`` is True (a seed passes exactly where its margin is >= 0)."""
    m = np.asarray(m, dtype=np.float64)
    k = int(math.ceil(m.shape[-1] * T.ORACLE_PASS))
    return -np.sort(-m, axis=-1)[..., k - 1]


def oracle_trajectories(engine: "EngineJudge", inst: Instance, plans, n_seeds: int = T.ORACLE_N,
                        key_sink=None, store=True) -> np.ndarray:
    """Per-seed engine trajectories of plans on the instance's oracle seeds, through the cached engine judge.

    ``plans``: raw plans (n, H*25) or (n, H, 25) (the task's forced events are written in by ``effective``, so
    effective plans give the same result). Returns int64 (n, n_seeds, H+1, 20); entry [i, k] is plan i replayed
    on ``dc.tasks.oracle_seeds(start, task, H)[k]``. The verdicts are ``dc.tasks.oracle_verdict(inst.task,
    out, inst.theta)``. Replays are read from / written to the engine judge's disk cache (``store``: per plan or
    one for all; False keeps new replays out of it, as for the floors' search candidates)."""
    H = int(inst.horizon)
    eff = effective(plans, inst.task, H)
    S = oracle_seed_list(inst, n_seeds)
    n, k = eff.shape[0], len(S)
    stk = np.repeat(np.broadcast_to(np.asarray(store, dtype=bool), (n,)), k)
    sc = engine.scalars(inst, np.repeat(eff, k, axis=0), np.tile(np.asarray(S, dtype=np.int64), n), key_sink=key_sink,
                        **({} if stk.all() else {"store": stk}))
    return np.asarray(sc).reshape(n, k, H + 1, NUM_SCALARS)


def oracle_judgement(inst: Instance, traj) -> dict:
    """The oracle's judgement of plans from their trajectories on the oracle seeds (n, S, H+1, 20): per-seed
    margins (``task_margin``) and verdicts, the pass share (``dc.tasks.oracle_share``), the majority verdict
    (``dc.tasks.oracle_verdict``) and margin (``majority_margin``), and oracle seed 0's verdict and margin. The
    margins' signs are checked against ``dc.tasks`` (per seed and for the majority)."""
    tr = np.asarray(traj)
    m = np.asarray(task_margin(inst, tr), dtype=np.float64)                    # (n, S)
    v_seed = np.asarray(T.verdict(inst.task, tr, inst.theta), dtype=bool)        # (n, S)
    share = np.asarray(T.oracle_share(inst.task, tr, inst.theta), dtype=np.float64)
    verdict = np.asarray(T.oracle_verdict(inst.task, tr, inst.theta), dtype=bool)
    mm = majority_margin(m)
    if not np.array_equal(m >= 0, v_seed) or not np.array_equal(mm >= 0, verdict):
        raise ValueError(f"{inst.key}: margin signs disagree with dc.tasks' verdicts")
    return {"margins": m, "accept_seeds": v_seed, "share": share, "accept": verdict, "margin": mm,
            "accept_seed0": v_seed[:, 0].copy(), "margin_seed0": m[:, 0].copy()}


_W_ENG = None


def _worker_init() -> None:
    global _W_ENG
    from .engine import Engine
    _W_ENG = Engine()


def _replay_job(args) -> bytes:
    """(cty, effective plan bytes, H, seed) -> scalar trajectory bytes (H+1, 20) int64."""
    global _W_ENG
    from .oracle import replay
    if _W_ENG is None:
        _worker_init()
    cty, pb, H, seed = args
    if not os.path.isabs(cty):
        cty = str(REPO / cty)
    plan = np.frombuffer(pb, dtype=np.int16).reshape(H, N_COLS)
    acts, forced = compile_plan(plan)
    return replay(_W_ENG, cty, acts, int(seed), forced=forced or None).scalars.astype("<i8").tobytes()


def _sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class EngineCache:
    """sqlite file per start: key (16 bytes) -> zlib-compressed int64 scalar trajectory."""

    def __init__(self, root) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._con: Dict[str, sqlite3.Connection] = {}

    def _db(self, start_id: str) -> sqlite3.Connection:
        c = self._con.get(start_id)
        if c is None:
            c = sqlite3.connect(str(self.root / f"{start_id}.sqlite"), timeout=120)
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("CREATE TABLE IF NOT EXISTS c (k BLOB PRIMARY KEY, v BLOB NOT NULL)")
            self._con[start_id] = c
        return c

    def get_many(self, start_id: str, keys: Sequence[bytes]) -> Dict[bytes, bytes]:
        db, out = self._db(start_id), {}
        ks = list(dict.fromkeys(keys))
        for a in range(0, len(ks), 500):
            part = ks[a:a + 500]
            q = "SELECT k, v FROM c WHERE k IN (%s)" % ",".join("?" * len(part))
            for k, v in db.execute(q, part):
                out[bytes(k)] = zlib.decompress(v)
        return out

    def put_many(self, start_id: str, items: Dict[bytes, bytes]) -> Tuple[int, int]:
        """Insert (or ignore, if present) entries; returns (rows inserted, value bytes of the rows given)."""
        if not items:
            return 0, 0
        db = self._db(start_id)
        rows = [(k, zlib.compress(v, 6)) for k, v in items.items()]
        n0 = db.total_changes
        db.executemany("INSERT OR IGNORE INTO c (k, v) VALUES (?, ?)", rows)
        db.commit()
        return db.total_changes - n0, sum(len(v) for _, v in rows)

    def close(self) -> None:
        for c in self._con.values():
            c.close()
        self._con = {}


def _send(f, obj) -> None:
    b = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    f.write(len(b).to_bytes(8, "little"))
    f.write(b)
    f.flush()


def _recv(f):
    h = f.read(8)
    if len(h) < 8:
        return None
    n = int.from_bytes(h, "little")
    b = f.read(n)
    if len(b) < n:
        return None
    return pickle.loads(b)


def _ping() -> bool:
    return _W_ENG is not None


def serve(workers: int) -> None:
    """Replay server for a remote machine: framed pickled requests on stdin, replies on stdout.

    Requests: ("sha", [paths relative to the repository]) -> {path: sha256 or None};
    ("map", [(relative cty, effective plan bytes, H, seed), ...]) -> ("ok", [scalar bytes]); ("quit",)."""
    import multiprocessing as mp
    import socket
    inp, out = sys.stdin.buffer, sys.stdout.buffer
    sys.stdout = sys.stderr
    pool = mp.get_context("fork").Pool(int(workers), initializer=_worker_init)
    try:                        # a worker that cannot start its engine would make every map hang
        pool.apply_async(_ping).get(timeout=120)
    except Exception as e:
        _send(out, ("error", f"replay workers did not start: {e!r}"))
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
            _send(out, ("ok", pool.map(_replay_job, jobs, chunksize=max(1, len(jobs) // (4 * int(workers))))))
        else:
            _send(out, ("error", f"unknown request {msg[0]!r}"))
    pool.close()
    pool.join()


class RemotePool:
    """Replays on another machine through ``serve`` over one ssh connection (or any command whose
    stdin / stdout reach a ``serve`` process). Start files are named relative to the repository root
    and checked by sha256 against the local files before use."""

    def __init__(self, command: Sequence[str], workers: int, log_path=None) -> None:
        import subprocess
        self.workers = int(workers)
        self.command = list(command)
        err = open(log_path, "ab") if log_path else subprocess.DEVNULL
        self.proc = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err)
        msg = _recv(self.proc.stdout)
        if not msg or msg[0] != "ready":
            raise RuntimeError(f"remote replay server did not start: {msg!r}")
        if msg[1] != PROTO_VERSION:
            raise RuntimeError(f"remote protocol {msg[1]} differs from local {PROTO_VERSION}")
        self.host = msg[2]
        self._sha_ok: set = set()

    def check_files(self, rel_paths: Sequence[str]) -> None:
        need = [r for r in rel_paths if r not in self._sha_ok]
        if not need:
            return
        _send(self.proc.stdin, ("sha", need))
        st, got = _recv(self.proc.stdout)
        for r in need:
            if got.get(r) != _sha256_file(REPO / r):
                raise RuntimeError(f"start file {r} differs on {self.host} (remote sha256 {got.get(r)})")
            self._sha_ok.add(r)

    def map(self, jobs: Sequence[tuple]) -> List[bytes]:
        _send(self.proc.stdin, ("map", list(jobs)))
        msg = _recv(self.proc.stdout)
        if not msg or msg[0] != "ok":
            raise RuntimeError(f"remote replay failed: {msg!r}")
        return msg[1]

    def close(self) -> None:
        try:
            _send(self.proc.stdin, ("quit",))
            self.proc.stdin.close()
            self.proc.wait(timeout=60)
        except Exception:  # pragma: no cover
            self.proc.kill()


def host_b_pool(workers: int = 22, root: str = HOST_B_ROOT, log_path=None) -> RemotePool:
    cmd = HOST_B_SSH + [f"cd {root} && PYTHONPATH=code exec .venv/bin/python -u -m dc.audit serve --workers {int(workers)}"]
    return RemotePool(cmd, workers, log_path)


class EngineJudge:
    """The engine through ``dc.grammar.compile_plan`` + ``dc.oracle.replay``, cached on disk.

    ``scalars(inst, eff_plans, seeds)``: effective plans (n, H, 25) int16 and one seed per plan (or
    one for all) -> (n, H+1, 20) int64. Misses are replayed by a local process pool of ``workers``
    processes (0: in this process) and, when ``remote`` is given and a call has enough misses, partly
    by the remote pool; the split follows the measured rates of the two. ``store`` (per row, or one for all): False
    keeps a replay out of the disk cache, in a transient in-memory table that ``clear_transient`` empties (the
    floors' search candidates, which no later run looks up). Counters: ``n_requests``, ``n_cache_hits``,
    ``n_replays`` (rows sent to an engine; ``n_remote`` of them remote; ``n_uncached`` of them kept out of the disk
    cache), ``n_put`` / ``bytes_put`` (entries written to the disk cache and their compressed bytes), ``seconds``
    (wall time of the replays)."""

    def __init__(self, cache_root=CACHE_ROOT / "engine_cache", workers: int = 12, H: int = 24,
                 remote: Optional[RemotePool] = None, log: Callable[[str], None] = print) -> None:
        self.cache = EngineCache(cache_root)
        self.workers = int(workers)
        self.H = H
        self.remote = remote
        self.log = log
        self._pool = None
        self._start_sha: Dict[str, str] = {}
        self.n_requests = self.n_cache_hits = self.n_replays = self.n_remote = 0
        self.n_uncached = self.n_put = self.bytes_put = 0
        self._transient: Dict[bytes, bytes] = {}
        self.seconds = 0.0
        self._rate = {"local": 1.0 * max(1, self.workers), "remote": 1.0 * (remote.workers if remote else 0)}

    def _get_pool(self):
        if self._pool is None and self.workers > 0:
            import multiprocessing as mp
            self._pool = mp.get_context("spawn").Pool(self.workers, initializer=_worker_init)
        return self._pool

    def close(self) -> None:
        if self._pool is not None:
            self._pool.close()
            self._pool.join()
            self._pool = None
        if self.remote is not None:
            self.remote.close()
            self.remote = None
        self.cache.close()

    def start_sha(self, inst: Instance) -> str:
        s = self._start_sha.get(inst.cty)
        if s is None:
            s = self._start_sha[inst.cty] = _sha256_file(inst.cty)
        return s

    def key(self, inst: Instance, eff_row: np.ndarray, seed: int) -> bytes:
        head = f"{PROTO_VERSION}|{self.start_sha(inst)}|{self.H}|{int(seed)}|".encode()
        return hashlib.sha256(head + np.ascontiguousarray(eff_row, dtype=np.int16).tobytes()).digest()[:16]

    def _local(self, jobs):
        pool = self._get_pool()
        if pool is None:
            return [_replay_job(j) for j in jobs]
        return pool.map(_replay_job, jobs, chunksize=max(1, len(jobs) // (4 * self.workers)))

    def _replay(self, inst: Instance, jobs: List[tuple]) -> List[bytes]:
        r = self.remote
        if r is None or len(jobs) < 4 * max(1, self.workers):
            return self._local(jobs)
        import threading
        rel = os.path.relpath(inst.cty, REPO)
        r.check_files([rel])
        f = self._rate["remote"] / (self._rate["remote"] + self._rate["local"])
        nr = int(round(len(jobs) * f))
        rjobs = [(rel,) + tuple(j[1:]) for j in jobs[:nr]]
        box: Dict[str, object] = {}

        def run_remote():
            t0 = time.time()
            try:
                box["res"] = r.map(rjobs)
            except Exception as e:  # pragma: no cover - fall back to local replays
                box["err"] = e
            box["t"] = time.time() - t0

        th = threading.Thread(target=run_remote, daemon=True)
        th.start()
        t0 = time.time()
        loc = self._local(jobs[nr:]) if nr < len(jobs) else []
        tl = time.time() - t0
        th.join()
        if "err" in box:
            self.log(f"  remote replays failed ({box['err']!r}); replaying locally and dropping the remote pool")
            self.remote = None
            return self._local(jobs[:nr]) + loc
        for k, n, t in (("remote", nr, box["t"]), ("local", len(jobs) - nr, tl)):
            if n >= 2 * max(1, self.workers) and t > 0:
                self._rate[k] = 0.5 * self._rate[k] + 0.5 * n / t
        self.n_remote += nr
        return list(box["res"]) + loc

    def clear_transient(self) -> None:
        self._transient = {}

    def scalars(self, inst: Instance, eff_plans: np.ndarray, seeds, key_sink: Optional[set] = None,
                store=True) -> np.ndarray:
        P = np.ascontiguousarray(eff_plans, dtype=np.int16).reshape(-1, self.H, N_COLS)
        n = P.shape[0]
        sd = np.broadcast_to(np.asarray(seeds, dtype=np.int64), (n,))
        st = np.broadcast_to(np.asarray(store, dtype=bool), (n,))
        keys = [self.key(inst, P[i], int(sd[i])) for i in range(n)]
        if key_sink is not None:
            key_sink.update(keys)
        have = self.cache.get_many(inst.start_id, keys)
        want: Dict[bytes, bool] = {}                 # key -> whether some row asking for it wants it on disk
        for i, k in enumerate(keys):
            want[k] = want.get(k, False) or bool(st[i])
        promote = {}
        for k in want:
            if k not in have and k in self._transient:
                have[k] = self._transient[k]
                if want[k]:
                    promote[k] = self._transient.pop(k)
        miss: Dict[bytes, int] = {}
        for i, k in enumerate(keys):
            if k not in have and k not in miss:
                miss[k] = i
        self.n_requests += n
        self.n_cache_hits += sum(1 for k in keys if k in have)
        new: Dict[bytes, bytes] = {}
        if miss:
            t0 = time.time()
            jobs = [(inst.cty, P[i].tobytes(), self.H, int(sd[i])) for i in miss.values()]
            new = dict(zip(miss.keys(), self._replay(inst, jobs)))
            have.update(new)
            self.n_replays += len(jobs)
            self.seconds += time.time() - t0
        put = {**promote, **{k: v for k, v in new.items() if want[k]}}
        for k, v in new.items():
            if not want[k]:
                self._transient[k] = v
                self.n_uncached += 1
        if put:
            r, b = self.cache.put_many(inst.start_id, put)
            self.n_put += r
            self.bytes_put += b
        return np.stack([np.frombuffer(have[k], dtype="<i8").reshape(self.H + 1, NUM_SCALARS) for k in keys])

    def counters(self) -> dict:
        return {"engine_requests": self.n_requests, "engine_cache_hits": self.n_cache_hits,
                "engine_replays": self.n_replays, "engine_replays_remote": self.n_remote,
                "engine_replays_uncached": self.n_uncached, "engine_rows_put": self.n_put,
                "engine_bytes_put": self.bytes_put,
                "engine_city_months_replayed": self.n_replays * self.H, "engine_seconds": self.seconds}


# ----------------------------------------------------------------------------------------------
# Sampling judges
# ----------------------------------------------------------------------------------------------
class SamplingJudge:
    """Interface: ``samples(inst, eff_plans (n, H, 25), K, stream) -> (n, K, H+1, 20) float64``.

    ``stream`` is a tuple naming the call (deterministic); counters: ``month_steps`` (n K H of every
    call), ``seconds``."""

    name = "abstract"
    task_independent = True      # samples depend on the start and the forced events, not on the task

    def __init__(self) -> None:
        self.month_steps = 0
        self.padded_month_steps = 0
        self.seconds = 0.0
        self.n_calls = 0

    def samples(self, inst: Instance, eff_plans: np.ndarray, K: int, stream: tuple) -> np.ndarray:
        t0 = time.time()
        P = np.ascontiguousarray(eff_plans, dtype=np.int16)
        out = self._samples(inst, P, int(K), tuple(stream))
        n, H = P.shape[0], P.shape[1]
        if out.shape != (n, K, H + 1, NUM_SCALARS):
            raise ValueError(f"{self.name}: samples of shape {out.shape}, expected {(n, K, H + 1, NUM_SCALARS)}")
        self.month_steps += n * K * H
        self.n_calls += 1
        self.seconds += time.time() - t0
        return out

    def _samples(self, inst, P, K, stream):  # pragma: no cover - interface
        raise NotImplementedError

    def describe(self) -> dict:
        d = {"judge": self.name}
        if self.name.startswith("engine"):
            d["seeds"] = ("primary seed_for('task', start, task, H)" if self.name == "engine-identity"
                          else "seed_for('audit-seedcheck', start, *stream, row, sample)")
        return d

    def counters(self) -> dict:
        return {"judge_month_steps": self.month_steps, "judge_padded_month_steps": self.padded_month_steps,
                "judge_seconds": self.seconds, "judge_calls": self.n_calls}


class EngineIdentityJudge(SamplingJudge):
    """The oracle judging itself. Without ``oracle_n``: every sample is the engine's own trajectory on the primary
    seed (the engine judge's seed). With ``oracle_n`` (the majority oracle over that many seeds): every sample of
    a plan is the plan's trajectory on the oracle seed whose task margin is the ceil(n/2)-th largest (ties: the
    lower seed index), so the judge's margin is the oracle's majority margin and its verdict the oracle's. That
    choice depends on the thresholds: ``tasks_sha256`` (the tasks file's) goes into the description, so its
    samples are never reused across tasks files."""

    name = "engine-identity"
    task_independent = False     # the primary seed (or the oracle's seeds) belong to the task

    def __init__(self, engine: EngineJudge, oracle_n: int = 0, tasks_sha256: str = "") -> None:
        super().__init__()
        self.engine = engine
        self.oracle_n = int(oracle_n)
        self.tasks_sha256 = tasks_sha256
        if self.oracle_n and not tasks_sha256:
            raise ValueError("the majority identity judge depends on the thresholds: pass tasks_sha256")

    def describe(self) -> dict:
        d = super().describe()
        if self.oracle_n:
            d["seeds"] = (f"oracle seeds seed_for('task-oracle', start, task, H, k), k < {self.oracle_n}: per plan the "
                          f"seed whose task margin is the ceil(n/2)-th largest (lower index on ties)")
            d["oracle"] = {"rule": "majority", "n_seeds": self.oracle_n}
            d["tasks_sha256"] = self.tasks_sha256
        return d

    def _samples(self, inst, P, K, stream):
        if not self.oracle_n:
            s = self.engine.scalars(inst, P, primary_seed(inst)).astype(np.float64)
            return np.repeat(s[:, None], K, axis=1)
        tr = oracle_trajectories(self.engine, inst, P, self.oracle_n)                 # (n, S, H+1, 20)
        m = np.asarray(task_margin(inst, tr), dtype=np.float64)
        k = int(math.ceil(self.oracle_n * T.ORACLE_PASS))
        j = np.argsort(-m, axis=1, kind="stable")[:, k - 1]                            # the k-th largest margin
        s = tr[np.arange(tr.shape[0]), j].astype(np.float64)
        return np.repeat(s[:, None], K, axis=1)


class EngineSeedJudge(SamplingJudge):
    """Every sample is the engine on a seed of its own: sample k of row i of a call with stream S is
    seeded ``seed_for("audit-seedcheck", start, *S, i, k)``. With ``oracle_n`` (the majority oracle), a seed that is
    one of the nine residual seeds or the ``oracle_n`` oracle seeds of any task of the start is redrawn
    (``fresh_seed``; counted in ``n_redraws``), so the judge never replays on a seed the oracle or a residual uses."""

    name = "engine-seeds"

    def __init__(self, engine: EngineJudge, oracle_n: int = 0) -> None:
        super().__init__()
        self.engine = engine
        self.oracle_n = int(oracle_n)
        self.n_redraws = 0
        self._reserved: Dict[str, frozenset] = {}

    def describe(self) -> dict:
        d = super().describe()
        if self.oracle_n:
            d["seeds_avoid"] = (f"the nine residual seeds and the {self.oracle_n} oracle seeds of every task of the start; "
                                f"a reserved draw is replaced by seed_for('audit-seedcheck', start, *stream, row, sample, "
                                f"'redraw', r)")
        return d

    def _samples(self, inst, P, K, stream):
        n = P.shape[0]
        if not self.oracle_n:
            seeds = np.array([[seed_for("audit-seedcheck", inst.start_id, *stream, i, k) for k in range(K)]
                              for i in range(n)], dtype=np.int64)
        else:
            res = self._reserved.get(inst.start_id)
            if res is None:
                res = self._reserved[inst.start_id] = reserved_seeds(inst.start_id, P.shape[1], self.oracle_n)
            seeds = np.empty((n, K), dtype=np.int64)
            for i in range(n):
                for k in range(K):
                    seeds[i, k], r = fresh_seed(("audit-seedcheck", inst.start_id, *stream, i, k), res)
                    self.n_redraws += r > 0
            if set(seeds.reshape(-1).tolist()) & res:      # by construction; checked because the brief requires it
                raise RuntimeError("a judge seed is a reserved seed")
        s = self.engine.scalars(inst, np.repeat(P, K, axis=0), seeds.reshape(-1)).astype(np.float64)
        return s.reshape(n, K, P.shape[1] + 1, NUM_SCALARS)

    def counters(self) -> dict:
        d = super().counters()
        if self.oracle_n:
            d["judge_seed_redraws"] = self.n_redraws
        return d


LADDER_V2_COMMIT = "2cbd5c2252e9f3b5578edb0057e4b770069fa8f9"


def code_package(rev: str):
    """The ``dc`` package as of a git revision, imported under a private name (``dcsrc_<sha12>``) beside this
    process's own ``dc``: ``git archive <rev> code/dc`` is extracted under the audit cache once. The package's
    modules import each other relatively, so model, train, engine constants and grammar all come from the
    revision; the engine library itself is never loaded from it (this process replays with its own ``dc``).
    In a single-commit release checkout where historical git tags are absent, ``ladder-v2`` resolves to the
    shipped ``code/dc`` tree (whose model, train, engine, and grammar modules are identical to ``ladder-v2``).
    Returns (package, full commit sha)."""
    import importlib
    import importlib.util
    import subprocess
    import tarfile
    import io
    r = subprocess.run(["git", "-C", str(REPO), "rev-parse", f"{rev}^{{commit}}"], capture_output=True, text=True)
    if r.returncode != 0:
        if rev in ("ladder-v2", LADDER_V2_COMMIT):
            sha = LADDER_V2_COMMIT
            name = f"dcsrc_{sha[:12]}"
            if name in sys.modules:
                return sys.modules[name], sha
            init = REPO / "code" / "dc" / "__init__.py"
            spec = importlib.util.spec_from_file_location(name, init, submodule_search_locations=[str(init.parent)])
            pkg = importlib.util.module_from_spec(spec)
            sys.modules[name] = pkg
            spec.loader.exec_module(pkg)
            return pkg, sha
        raise subprocess.CalledProcessError(r.returncode, r.args, output=r.stdout, stderr=r.stderr)
    sha = r.stdout.strip()
    name = f"dcsrc_{sha[:12]}"
    if name in sys.modules:
        return sys.modules[name], sha
    d = CACHE_ROOT / "model_src" / sha[:12]
    init = d / "code" / "dc" / "__init__.py"
    if not init.exists():
        tar = subprocess.run(["git", "-C", str(REPO), "archive", "--format=tar", sha, "code/dc"], check=True,
                             capture_output=True).stdout
        tmp = d.with_name(d.name + ".tmp")
        tmp.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
            tf.extractall(tmp)
        os.replace(tmp, d)
    spec = importlib.util.spec_from_file_location(name, init, submodule_search_locations=[str(init.parent)])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules[name] = pkg
    spec.loader.exec_module(pkg)
    return pkg, sha


def training_commit(ckpt) -> str:
    """The commit a checkpoint was trained at (its ``git`` record), refused if the training tree had uncommitted
    code changes: then the code that made it is not in the repository and ``--model-src`` must be given."""
    import torch
    try:
        ck = torch.load(ckpt, map_location="cpu", weights_only=False, mmap=True)
    except Exception:
        ck = torch.load(ckpt, map_location="cpu", weights_only=False)
    g = ck.get("git") or {}
    dirty = [f for f in (g.get("dirty_code_files") or []) if f.strip()]
    if not g.get("commit"):
        raise ValueError(f"{ckpt}: no training commit recorded; pass --model-src")
    if dirty:
        raise ValueError(f"{ckpt}: trained with uncommitted code changes {dirty[:5]}; pass --model-src explicitly")
    return str(g["commit"])


def load_emulator(ckpt, device, model_src: str = "worktree"):
    """(model, checkpoint dict, description, train module). ``model_src``: "worktree" (this checkout's
    ``dc.train.load_checkpoint``) or a git revision or tag: the revision's whole ``dc`` package
    (``code_package``) loads the checkpoint with its own ``train.load_checkpoint`` (which applies that code's
    numerics) and supplies the state conversion (``obs_to_numpy``, ``numpy_to_state``) for the start state."""
    import importlib
    desc = {"ckpt": str(ckpt), "model_src": model_src}
    if model_src == "auto":
        model_src = training_commit(ckpt)
        desc["model_src_resolved"] = model_src
    if model_src == "worktree":
        from . import train as Tr
        desc["model_py_sha256"] = _sha256_file(REPO / "code" / "dc" / "model.py")
    else:
        pkg, sha = code_package(model_src)
        Tr = importlib.import_module(f"{pkg.__name__}.train")
        desc["model_src_commit"] = sha
        desc["model_py_sha256"] = _sha256_file(Path(pkg.__file__).parent / "model.py")
    model, ck = Tr.load_checkpoint(ckpt, device)
    desc["samples"] = int(ck.get("samples", -1))
    desc["ckpt_sha256"] = _sha256_file(ckpt)
    desc["ckpt_trained_at"] = (ck.get("git") or {}).get("commit")
    cfgd = ck.get("model_config", {})
    desc["model_config"] = {k: cfgd.get(k) for k in ("size", "scalar_stage", "ledger", "bookkeeping") if k in cfgd}
    return model, ck, desc, Tr


def emulator_rollout(model, state0: dict, plans: np.ndarray, K: int, device, max_batch: int) -> np.ndarray:
    """The one adaptor to ``dc.model``: open-loop rollouts of effective plans (B, H, 25) from a
    one-row start state, K samples each, the model's default decoding. -> (B, K, H+1, 20) float64."""
    import torch
    B, H = plans.shape[0], plans.shape[1]
    act = torch.from_numpy(action_scalars_batch(plans.reshape(-1, N_COLS)).reshape(B, H, -1)).to(device)

    on_card = torch.device(device).type == "cuda"
    P = np.ascontiguousarray(plans)

    def raster(h):
        if on_card:                      # built on the card; exactly equal to raster_batch (code/tests/test_fast.py)
            from . import fast
            return fast.raster_rows(P[:, h], device)
        return torch.from_numpy(raster_batch(plans[:, h])).to(device, non_blocking=True)

    s0 = {k: v.expand(B, *v.shape[1:]) for k, v in state0.items()}
    traj, _ = model.rollout(s0, raster, act, K=K, max_batch=max_batch)      # the model's own default decoding
    return traj.double().cpu().numpy()


class EmulatorJudge(SamplingJudge):
    """A checkpoint's sampled open-loop rollouts. Plans go through the model in groups of at most
    ``chunk`` rows (plans x K), each padded with copies of its last plan to the smallest of
    ``buckets`` that holds it, so a compiled trunk sees a fixed set of batch shapes."""

    name = "emulator"

    def __init__(self, ckpt, device: str = "cuda:0", chunk: int = 128, buckets: Sequence[int] = (16, 64, 128),
                 compile_trunk: bool = True, model_src: str = "worktree", H: int = 24, fast: bool = True) -> None:
        super().__init__()
        import torch
        self.torch = torch
        self.device = torch.device(device)
        if self.device.type == "cuda":
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
        self.model, ck, self.desc, self._tr = load_emulator(ckpt, self.device, model_src)
        self.chunk = int(chunk)
        self.buckets = tuple(sorted(int(b) for b in buckets if int(b) <= self.chunk)) or (self.chunk,)
        if self.buckets[-1] != self.chunk:
            self.buckets = self.buckets + (self.chunk,)
        self.compiled = bool(compile_trunk and self.device.type == "cuda")
        self.fast = bool(fast and self.compiled)
        if self.fast:
            # dc.fast: the tag's trunk with fc1 + GELU as one GEMM, compiled, replayed as CUDA graphs; the
            # sampling and everything else are the tag's own code (equivalence: results/perf/report.md)
            from . import fast as _fast
            _fast.accelerate(self.model)
        elif self.compiled:
            self.model.compile_trunk(dynamic=False)
        self.H = H
        self._s0: Dict[str, dict] = {}
        self._eng = None

    def describe(self) -> dict:
        return {"judge": self.name, **self.desc, "device": str(self.device), "chunk": self.chunk,
                "buckets": list(self.buckets), "compiled_trunk": self.compiled,
                "fast": self._fast_describe(), "decoding": self.decoding()}

    def _fast_describe(self) -> dict:
        from . import fast as _fast
        return _fast.describe(self.model)

    def decoding(self) -> dict:
        """The decoding the rollouts use: ``model.rollout``'s own defaults (the audit passes none), and the name
        the revision's ``fidelity.DEFAULT_DECODING`` gives it."""
        import importlib
        import inspect
        prm = inspect.signature(self.model.rollout).parameters
        d = {k: prm[k].default for k in ("temperature", "overlay") if k in prm}
        d["source"] = "model.rollout defaults"
        try:
            fid = importlib.import_module(self._tr.__name__.rsplit(".", 1)[0] + ".fidelity")
            d["default_decoding"] = fid.DEFAULT_DECODING
            d["default_decoding_matches"] = tuple(fid.DECODINGS[fid.DEFAULT_DECODING]) == (d.get("temperature"), d.get("overlay"))
        except Exception as e:  # pragma: no cover
            d["default_decoding"] = f"unavailable ({type(e).__name__})"
        return d

    def state0(self, inst: Instance) -> dict:
        s = self._s0.get(inst.start_id)
        if s is None:
            import inspect
            from .engine import Engine
            from .oracle import replay
            if self._eng is None:
                self._eng = Engine()
            rp = replay(self._eng, inst.cty, [], 0)
            o2n = self._tr.obs_to_numpy
            led = getattr(rp, "ledger", None)
            d = (o2n([rp.obs0], ledger=led[:1]) if led is not None and "ledger" in inspect.signature(o2n).parameters
                 else o2n([rp.obs0]))
            s = self._s0[inst.start_id] = self._tr.numpy_to_state(d, self.device)
        return s

    def _samples(self, inst, P, K, stream):
        torch = self.torch
        if self.chunk % K or any(b % K for b in self.buckets):
            raise ValueError(f"chunk {self.chunk} and buckets {self.buckets} must be multiples of K = {K}")
        torch.manual_seed(seed_for("audit-emu", inst.start_id, *stream))
        s0 = self.state0(inst)
        n, H = P.shape[0], P.shape[1]
        G = self.chunk // K
        out = np.empty((n, K, H + 1, NUM_SCALARS), dtype=np.float64)
        for a in range(0, n, G):
            sub = P[a:a + G]
            g = sub.shape[0]
            rows = next(b for b in self.buckets if b >= g * K)
            gp = rows // K
            if gp > g:
                sub = np.concatenate([sub, np.repeat(sub[-1:], gp - g, axis=0)])
                self.padded_month_steps += (gp - g) * K * H
            out[a:a + g] = emulator_rollout(self.model, s0, sub, K, self.device, max_batch=rows)[:g]
        return out


# ----------------------------------------------------------------------------------------------
# Pools
# ----------------------------------------------------------------------------------------------
class Pools:
    """Behaviour-mix plans (calibration files) and builder plans per start, forced column cleared."""

    def __init__(self, H: int = 24, cal_dir=CAL_DIR, builder_dir=BUILDER_DIR, arrays: Optional[dict] = None) -> None:
        self.H = H
        self.cal_dir = Path(cal_dir) / f"H{H}"
        self.builder_dir = Path(builder_dir) / f"H{H}"
        self._arrays = arrays or {}
        self._cache: Dict[Tuple[str, str], np.ndarray] = {}

    def _load(self, kind: str, start_id: str) -> np.ndarray:
        k = (kind, start_id)
        if k not in self._cache:
            if k in self._arrays:
                p = np.asarray(self._arrays[k])
            else:
                d = self.cal_dir if kind == "behaviour" else self.builder_dir
                with np.load(d / f"{start_id}.npz") as z:
                    p = z["plans"]
            p = np.asarray(p, dtype=np.int16).reshape(-1, self.H, N_COLS).copy()
            p[..., FORCED_COL] = 0
            p.flags.writeable = False
            self._cache[k] = p
        return self._cache[k]

    def behaviour(self, start_id: str) -> np.ndarray:
        return self._load("behaviour", start_id)

    def builders(self, start_id: str) -> np.ndarray:
        return self._load("builders", start_id)

    def describe(self) -> dict:
        return {"behaviour": str(self.cal_dir), "builders": str(self.builder_dir), "in_memory": bool(self._arrays)}


# ----------------------------------------------------------------------------------------------
# Scoring helpers
# ----------------------------------------------------------------------------------------------
class _Lookup:
    """Precomputed scores of a plan list, served to an attacker in order (random shooting and
    best-of-n score the first B rows of their proposal list)."""

    def __init__(self, plans: np.ndarray, scores: np.ndarray) -> None:
        self.plans, self.scores, self.off = plans, np.asarray(scores, dtype=np.float64), 0

    def __call__(self, X: np.ndarray) -> np.ndarray:
        n = X.shape[0]
        sl = slice(self.off, self.off + n)
        if self.off + n > self.plans.shape[0] or not np.array_equal(X, self.plans[sl]):
            raise RuntimeError("precomputed scores requested for plans out of order")
        self.off += n
        return self.scores[sl].copy()


def _fourth_largest(m: np.ndarray) -> np.ndarray:
    return np.sort(m, axis=-1)[..., -VERDICT_RANK]


@dataclass
class AuditConfig:
    H: int = 24
    budgets: Tuple[int, ...] = (1, 10, 100, 1000)
    methods: Tuple[str, ...] = ("cem", "random", "best_of_n", "random_verdict")
    search_seeds: Tuple[int, ...] = (0,)
    floors: Tuple[str, ...] = FLOORS
    pool_verdict_plans: int = 50           # rows of each residual pool computed in phase 1
    residual_pool: str = "family"          # one of RESIDUAL_RULES
    n_secondary: int = N_SECONDARY
    residual_rows: int = 0                 # first rows of each pool the rule uses (0: all computed rows)
    behaviour_plans: int = 0               # first behaviour rows of the behaviour table and flip rates (0: all)
    economy_top: int = 100                 # economy rule: verdict residuals on the rows with the largest search
    economy_random: int = 25               # residual, plus this many drawn at random from the rest
    flip_rates: str = "family"             # confusion rates pooled within the task family, or over "all" plans
    plan: str = "uniform"                  # "uniform": every method and budget on every instance; "amendment2": below
    subset_n: int = 40                     # amendment2: the fixed cross-check subset, select_instances(all, subset_n)
    bon_families: int = 20                 # amendment2: best-of-n on the instances of the first this many families
    verdict_cap: int = 100                 # amendment2: verdict-scored random search above this budget on the subset only
    verdict_rows: str = "all"              # "all": 8-sample verdicts on every pool row; "economy": only where needed
    cross_check: str = ""                  # "instance": the fully paired per-instance pool as well, on the subset
    tasks_file: str = ""                   # the tasks file the instances and thresholds come from
    tasks_sha256: str = ""                 # its sha256 and that of dc/tasks.py: margins depend on both, samples on
    tasks_code_sha256: str = ""            # neither (``tasks_digest``)
    oracle: str = ""                       # "": the primary seed; "majority": the tasks file's meta.oracle (amendment 3)
    oracle_seeds: int = 0                  # the majority oracle's number of seeds
    flip_scope: str = "verdict"            # flip floor beside verdict-scored random search only, or "all" methods
    floor_basis: str = "nine"              # residual floor's truth: "nine" (old seeds; files without meta.oracle) or
    truth_cand_seeds: int = TRUTH_CAND     # "truth" (truth seeds); a candidate's search truth over this many of them
    residual_draw: str = "plain"           # residual floor's draw: "plain", "volatility" or "calibrated" (RESIDUAL_DRAWS)
    residual_draw_k: int = VOL_K           # neighbours drawn from (VOL_K; other values are diagnostics)

    @property
    def majority(self) -> bool:
        return self.oracle == "majority"

    @property
    def rows(self) -> int:
        return self.residual_rows or self.pool_verdict_plans

    @property
    def beh_rows(self) -> int:
        return self.behaviour_plans or self.pool_verdict_plans

    def check(self) -> None:
        bad = [m for m in self.methods if m not in METHODS]
        if bad:
            raise ValueError(f"unknown methods {bad}; choose from {sorted(METHODS)}")
        bad = [f for f in self.floors if f not in FLOORS]
        if bad:
            raise ValueError(f"unknown floors {bad}; choose from {FLOORS}")
        if self.residual_pool not in RESIDUAL_RULES:
            raise ValueError(f"residual_pool must be one of {RESIDUAL_RULES}")
        if self.flip_rates not in ("family", "all"):
            raise ValueError("flip_rates must be 'family' or 'all'")
        if self.rows > self.pool_verdict_plans or self.beh_rows > self.pool_verdict_plans:
            raise ValueError("residual_rows and behaviour_plans cannot exceed pool_verdict_plans")
        if self.residual_pool == "economy" and self.economy_top + self.economy_random > self.rows:
            raise ValueError("economy_top + economy_random exceeds the pool rows")
        if self.plan not in ("uniform", "amendment2"):
            raise ValueError("plan must be 'uniform' or 'amendment2'")
        if self.verdict_rows not in ("all", "economy") or self.cross_check not in ("", "instance"):
            raise ValueError("verdict_rows must be 'all' or 'economy'; cross_check '' or 'instance'")
        if self.verdict_rows == "economy" and self.residual_pool not in ("economy",):
            raise ValueError("verdict_rows='economy' leaves pool rows without verdicts: only the economy rule can use it")
        if self.residual_rows and self.residual_rows != self.pool_verdict_plans and self.verdict_rows == "economy":
            raise ValueError("with verdict_rows='economy' the rule uses every computed pool row")
        if "cem" in self.methods or "cem_seeded" in self.methods:
            for B in self.budgets:
                hd.cem_schedule(B)
        if not self.budgets or min(self.budgets) < 1:
            raise ValueError("budgets must be positive")
        if self.oracle not in ORACLE_RULES:
            raise ValueError(f"oracle must be one of {ORACLE_RULES}")
        if (self.oracle_seeds >= 1) != self.majority:
            raise ValueError("oracle_seeds must be >= 1 exactly when oracle is 'majority'")
        if self.flip_scope not in FLIP_SCOPES:
            raise ValueError(f"flip_scope must be one of {FLIP_SCOPES}")
        if self.floor_basis not in FLOOR_BASES:
            raise ValueError(f"floor_basis must be one of {FLOOR_BASES}")
        if self.floor_basis == "truth":
            if not self.majority:
                raise ValueError("the truth-seed floor belongs to the majority oracle")
            if self.residual_pool not in ("instance", "economy"):
                raise ValueError("the truth-seed floor uses per-instance residual pools (instance or economy)")
            if not 1 <= self.truth_cand_seeds <= TRUTH_A:
                raise ValueError(f"truth_cand_seeds must lie in 1..{TRUTH_A}")
        if self.residual_draw not in RESIDUAL_DRAWS:
            raise ValueError(f"residual_draw must be one of {RESIDUAL_DRAWS}")
        if self.residual_draw in ("volatility", "calibrated"):
            if self.floor_basis != "truth":
                raise ValueError(f"the {self.residual_draw} draw needs the truth-seed floor (its means and standard deviations)")
            if self.truth_cand_seeds < 2:
                raise ValueError(f"the {self.residual_draw} draw needs at least 2 truth seeds per candidate")
            if not 1 <= self.residual_draw_k <= self.rows:
                raise ValueError(f"residual_draw_k must lie in 1..{self.rows} (the pool rows)")

    def to_dict(self) -> dict:
        """Every field; the oracle fields only under the majority oracle, the flip scope only when it is not "all",
        the floor basis only when it is "truth" and the residual draw only when it is not "plain" (what every run did
        before those fields existed), so that a configuration of an earlier round has the digests it had then (its
        phase files stay valid). Of these only the oracle fields enter the phase-1 digest: the others change the
        floors only."""
        d = asdict(self)
        if not d["oracle"] and not d["oracle_seeds"]:
            del d["oracle"], d["oracle_seeds"]
        if d["flip_scope"] == "all":
            del d["flip_scope"]
        if d["floor_basis"] == "nine":            # the floor of every run before the truth seeds existed
            del d["floor_basis"], d["truth_cand_seeds"]
        if d["residual_draw"] == "plain":         # the draw of every run before the volatility draw existed
            del d["residual_draw"], d["residual_draw_k"]
        return {k: list(v) if isinstance(v, tuple) else v for k, v in d.items()}

    def digest(self) -> str:
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()[:16]

    def digest_p1(self) -> str:
        """Digest of what phase 1 depends on. A uniform plan with verdicts on every row depends on the first six
        fields only (so rules share phase 1, as in round 3); per-instance plans and sparse verdicts add theirs;
        the majority oracle adds its two fields."""
        base = P1_FIELDS[:9] + ("oracle", "oracle_seeds")
        extra = () if (self.plan == "uniform" and self.verdict_rows == "all" and not self.cross_check) else P1_FIELDS[9:]
        d = {k: v for k, v in self.to_dict().items() if k in base + extra}
        return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()[:16]

    def rule_tag(self) -> str:
        return f"{self.residual_pool}-{self.digest()[:8]}"

    def tasks_tag(self) -> str:
        if not self.tasks_sha256:
            return "tasks-unrecorded"
        return f"{Path(self.tasks_file).stem}-{self.tasks_sha256[:8]}-{self.tasks_code_sha256[:6]}"


def cem_seeded_first(B: int) -> int:
    """Generation 0 of the seeded search at budget B: the first N behaviour proposals (N = the CEM population)."""
    return int(hd.cem_schedule(B)[1])


def amendment2_config(**kw) -> "AuditConfig":
    """The per-checkpoint plan of study protocol: cem, random and verdict-scored random search on
    every instance, best-of-n on the first 20 families, budgets 1 to 1,000; verdict-scored random search above
    B = 100 only on the fixed 40-instance subset; economy per-instance residual pools (1,000 rows, verdict
    residuals on the 100 largest search residuals plus 25 at random) everywhere, and the fully paired
    per-instance pool on the subset as a cross-check; flip rates pooled within task family from the first 100
    behaviour plans per instance (the plans verdict-scored search scores anyway)."""
    d = dict(plan="amendment2", methods=("cem", "random", "best_of_n", "random_verdict"), budgets=(1, 10, 100, 1000),
             floors=FLOORS, pool_verdict_plans=1000, residual_pool="economy", residual_rows=0, economy_top=100,
             economy_random=25, behaviour_plans=100, flip_rates="family", subset_n=40, bon_families=20, verdict_cap=100,
             verdict_rows="economy", cross_check="instance")
    d.update(kw)
    return AuditConfig(**d)


def _atomic_pickle(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _load_pickle(path: Path):
    with open(path, "rb") as f:
        return pickle.load(f)


class ArraySurrogate(hd.ResidualSurrogate if hd is not None else object):
    """A residual surrogate over a pool array built by ``residual_pool_rule`` (the rules other than hpr_dream's
    own family pooling); ``describe`` reports the rule."""

    def describe(self) -> dict:
        d = super().describe()
        info = getattr(self, "info", {})
        d.update(info)
        if "residual_pool_rule" in info:
            d["residual_pool_kind"] = info["residual_pool_rule"]
        return d


class VolatilityArraySurrogate(hd.VolatilityResidualSurrogate if hd is not None else object):
    """The volatility draw (``RESIDUAL_DRAWS``) over a pool array built by ``residual_pool_rule``; ``describe`` reports
    the rule and the draw."""

    def describe(self) -> dict:
        d = super().describe()
        info = getattr(self, "info", {})
        d.update(info)
        if "residual_pool_rule" in info:
            d["residual_pool_kind"] = info["residual_pool_rule"]
        return d


def volatility_surrogate(sg, pool_sd: np.ndarray, k: int) -> "VolatilityArraySurrogate":
    """The surrogate ``sg`` of ``residual_pool_rule`` (its effective pool rows, in pool order) with the volatility draw:
    ``pool_sd`` = s_j of the same rows, k neighbours, eps VOL_EPS."""
    v = VolatilityArraySurrogate(sg.effective_pool, np.asarray(pool_sd, dtype=np.float64)[:sg.pool_size], k=int(k),
                                 eps=VOL_EPS)
    v.info = dict(getattr(sg, "info", {}))
    return v


class CalibratedArraySurrogate(hd.CalibratedResidualSurrogate if hd is not None else object):
    """The calibrated draw (``RESIDUAL_DRAWS``) over a pool array built by ``residual_pool_rule``; ``describe`` reports
    the rule and the draw."""

    def describe(self) -> dict:
        d = super().describe()
        info = getattr(self, "info", {})
        d.update(info)
        if "residual_pool_rule" in info:
            d["residual_pool_kind"] = info["residual_pool_rule"]
        return d


def calibrated_surrogate(sg, pool_m: np.ndarray, pool_sd: np.ndarray, k: int) -> "CalibratedArraySurrogate":
    """The surrogate ``sg`` of ``residual_pool_rule`` (its effective pool rows, in pool order) with the calibrated draw:
    ``pool_m`` = m_j and ``pool_sd`` = s_j of the same rows, k neighbours."""
    n = sg.pool_size
    v = CalibratedArraySurrogate(sg.effective_pool, np.asarray(pool_m, dtype=np.float64)[:n],
                                 np.asarray(pool_sd, dtype=np.float64)[:n], k=int(k))
    v.info = dict(getattr(sg, "info", {}))
    return v


def own_pool_rows(raw_pool: np.ndarray, n: int) -> Callable:
    """plans -> for each plan the rows among the first ``n`` of ``raw_pool`` (raw plans, in pool order) that hold the
    same plan (an empty array for a plan outside them): the rows the calibrated draw leaves out for that candidate."""
    rows: Dict[bytes, List[int]] = {}
    flat = np.ascontiguousarray(raw_pool[:n], dtype=np.int64).reshape(min(n, len(raw_pool)), -1)
    for j, x in enumerate(flat):
        rows.setdefault(x.tobytes(), []).append(j)
    empty = np.zeros(0, dtype=np.int64)
    table = {key: np.array(v, dtype=np.int64) for key, v in rows.items()}

    def lookup(X) -> List[np.ndarray]:
        X = np.ascontiguousarray(X, dtype=np.int64).reshape(len(X), -1)
        return [table.get(x.tobytes(), empty) for x in X]
    return lookup


def _med_mad(a: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    med = np.median(a, axis=0)
    return med, np.median(np.abs(a - med), axis=0)


def economy_keep(search: np.ndarray, top: int, n_random: int, rng: np.random.Generator) -> np.ndarray:
    """Rows the economy rule keeps verdict residuals on: the ``top`` largest search residuals (ties: lower row
    index first) plus ``n_random`` drawn uniformly without replacement from the rest."""
    order = np.argsort(-np.asarray(search), kind="stable")
    keep = np.zeros(len(search), dtype=bool)
    keep[order[:top]] = True
    keep[rng.choice(np.flatnonzero(~keep), size=n_random, replace=False)] = True
    return keep


def economy_impute(pool: np.ndarray, top: int, n_random: int, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Economy rule. Verdict residuals are kept on ``top`` rows with the largest search residual (ties: lower
    row index first) plus ``n_random`` rows drawn uniformly without replacement from the rest; every other row
    takes the verdict residual of the kept row nearest in search residual (smallest absolute difference; ties:
    the kept row with the lower index). Returns (pool with imputed verdict column, mask of kept rows)."""
    s = pool[:, 0]
    keep = economy_keep(s, top, n_random, rng)
    if not np.isfinite(pool[keep, 1]).all():
        raise ValueError("economy rule: a kept row has no verdict residual")
    kept = np.flatnonzero(keep)                      # ascending row index
    out = pool.copy()
    for i in np.flatnonzero(~keep):
        out[i, 1] = pool[kept[int(np.argmin(np.abs(s[kept] - s[i])))], 1]   # argmin: first, i.e. lowest index
    return out, keep


def shrunk_log_mads(pools: Sequence[np.ndarray], rngs: Sequence[np.random.Generator], n_boot: int = SHRINK_BOOT) -> dict:
    """Per column c, for the instances with MAD > 0: l_i = log MAD_i, v_i = bootstrap variance of log MAD_i
    (``n_boot`` row resamples), l_bar = mean_i l_i, tau2 = max(0, var_i(l_i) - mean_i(v_i)) (between-instance
    variance of the true log-MADs, moment estimate), w_i = tau2 / (tau2 + v_i), shrunk MAD_i = exp(w_i l_i +
    (1 - w_i) l_bar): each log-MAD pulled toward the family mean by the share v_i / (tau2 + v_i). Zero-MAD
    instances keep MAD 0 (the zero-MAD rule applies to them)."""
    k, C = len(pools), pools[0].shape[1]
    mads = np.stack([_med_mad(p)[1] for p in pools])
    shr = np.zeros_like(mads)
    out = {"tau2": [], "l_bar": [], "w_mean": [], "v_mean": []}
    for c in range(C):
        nz = np.flatnonzero(mads[:, c] > 0)
        if nz.size == 0:
            for key in out:
                out[key].append(float("nan"))
            continue
        ell = np.log(mads[nz, c])
        v = np.empty(nz.size)
        for j, i in enumerate(nz):
            p = pools[i][:, c]
            idx = rngs[i].integers(0, len(p), size=(n_boot, len(p)))
            b = p[idx]
            mb = np.median(np.abs(b - np.median(b, axis=1, keepdims=True)), axis=1)
            mb = mb[mb > 0]
            v[j] = float(np.var(np.log(mb), ddof=1)) if mb.size > 1 else float("inf")
        lbar = float(ell.mean())
        fin = np.isfinite(v)
        tau2 = max(0.0, float(np.var(ell, ddof=1)) - float(v[fin].mean())) if nz.size > 1 and fin.any() else 0.0
        w = np.where(np.isfinite(v), tau2 / (tau2 + v) if tau2 > 0 else 0.0, 0.0)
        shr[nz, c] = np.exp(w * ell + (1.0 - w) * lbar)
        for key, val in (("tau2", tau2), ("l_bar", lbar), ("w_mean", float(w.mean())), ("v_mean", float(v[fin].mean()) if fin.any() else float("nan"))):
            out[key].append(val)
    out["mads"], out["shrunk_mads"] = mads, shr
    return out


def residual_pool_rule(cfg, pools: Sequence[np.ndarray], task: str, kind: str, keys: Sequence[str]):
    """(surrogates for the instances of one task family, note) under ``cfg.residual_pool``:

    family          hpr_dream ``ResidualFamily(zero_mad="centre")``: each instance's rows centred and scaled by
                    its own median and MAD, mapped back with the target's (zero-MAD rule for MAD 0)
    instance        the instance's own rows
    economy         the instance's own rows, verdict residuals kept on a subset and imputed (``economy_impute``)
    family-shrunk   as family, with every MAD replaced by its shrunk value (``shrunk_log_mads``); zero-MAD rule
                    unchanged (a target with MAD 0 takes the family's median non-zero raw MAD)
    family-centred  every instance's rows centred by its own median and added to the target's median, unscaled
    """
    rule = cfg.residual_pool
    if rule == "family":
        fam = hd.ResidualFamily(list(pools), zero_mad="centre")
        note = (f"zero-MAD rule for {[int(x) for x in fam.n_zero_mad]} of {len(pools)} instances (search, verdict)"
                if fam.n_zero_mad.any() else "")
        return [hd.ResidualSurrogate(p, family_pools=fam) for p in pools], note
    out = []
    if rule == "instance":
        for p in pools:
            sg = ArraySurrogate(p)
            sg.info = {"residual_pool_rule": rule}
            out.append(sg)
        return out, ""
    if rule == "economy":
        n_kept = []
        for p, key in zip(pools, keys):
            imp, keep = economy_impute(p, cfg.economy_top, cfg.economy_random,
                                       np.random.default_rng(seed_for("audit-economy", key, kind)))
            sg = ArraySurrogate(imp)
            sg.info = {"residual_pool_rule": rule, "residual_verdict_rows": int(keep.sum())}
            n_kept.append(int(keep.sum()))
            out.append(sg)
        return out, f"economy: verdict residuals kept on {sorted(set(n_kept))} of {len(pools[0])} rows"
    med = [_med_mad(p)[0] for p in pools]
    if rule == "family-centred":
        cen = np.concatenate([p - m for p, m in zip(pools, med)])
        for p, m in zip(pools, med):
            sg = ArraySurrogate(m + cen)
            sg.info = {"residual_pool_rule": rule, "residual_pooled_instances": len(pools)}
            out.append(sg)
        return out, ""
    if rule == "family-shrunk":
        sh = shrunk_log_mads(pools, [np.random.default_rng(seed_for("audit-shrink", key, kind)) for key in keys])
        mads, smad = sh["mads"], sh["shrunk_mads"]
        nz_raw = [np.median(mads[mads[:, c] > 0, c]) if (mads[:, c] > 0).any() else 0.0 for c in range(mads.shape[1])]
        z = []
        for p, m, s_ in zip(pools, med, smad):
            sc = s_ > 0
            z.append(np.where(sc, (p - m) / np.where(sc, s_, 1.0), 0.0))
        Z = np.concatenate(z)
        D = np.concatenate([np.where(s_ > 0, 0.0, p - m) for p, m, s_ in zip(pools, med, smad)])
        SC = np.concatenate([np.broadcast_to(s_ > 0, p.shape) for p, s_ in zip(pools, smad)])
        for p, m, s_ in zip(pools, med, smad):
            scale = np.where(s_ > 0, s_, nz_raw)
            sg = ArraySurrogate(m + np.where(SC, scale * Z, D))
            sg.info = {"residual_pool_rule": rule, "residual_pooled_instances": len(pools),
                       "residual_zero_mad_instances": [int(x) for x in (mads == 0).sum(axis=0)]}
            out.append(sg)
        note = (f"shrunk scales: tau2 {['%.4f' % x for x in sh['tau2']]}, mean weight on own log-MAD "
                f"{['%.3f' % x for x in sh['w_mean']]}, mean sampling variance {['%.4f' % x for x in sh['v_mean']]}")
        return out, note
    raise ValueError(rule)


class Crash(RuntimeError):
    """Raised by the test hook ``crash_after`` (simulated kill)."""


class _KeySink:
    """The distinct (plan, seed) engine replays an instance requested (a set of cache keys, ``len`` = count), each
    attributed to the purpose that requested it first (``by_purpose``; set ``purpose`` before a request)."""

    def __init__(self) -> None:
        self.keys: set = set()
        self.by_purpose: Dict[str, int] = {}
        self.purpose = "other"

    def update(self, keys) -> None:
        for k in keys:
            if k not in self.keys:
                self.keys.add(k)
                self.by_purpose[self.purpose] = self.by_purpose.get(self.purpose, 0) + 1

    def __len__(self) -> int:
        return len(self.keys)


# ----------------------------------------------------------------------------------------------
# The audit
# ----------------------------------------------------------------------------------------------
class Audit:
    """Runs phase 1 and phase 2 over ``instances`` and assembles the outputs (module docstring)."""

    def __init__(self, cfg: AuditConfig, instances: Sequence[Instance], judge: SamplingJudge, engine: EngineJudge,
                 pools: Pools, work_dir, log: Callable[[str], None] = print,
                 universe: Optional[Sequence[Instance]] = None) -> None:
        """``universe``: every instance of the task file (default ``instances``); the amendment-2 subset and the
        best-of-n families are fixed on it, whatever subset of it this run audits."""
        cfg.check()
        self.cfg = cfg
        self.instances = list(instances)
        if len({i.key for i in self.instances}) != len(self.instances):
            raise ValueError("duplicate instances")
        uni = list(universe) if universe is not None else self.instances
        self._subset = {i.key for i in select_instances(uni, cfg.subset_n)} if cfg.plan == "amendment2" else set()
        fams = sorted({i.family_id for i in uni})
        self._bon_families = set(fams[:cfg.bon_families]) if cfg.plan == "amendment2" else set(fams)
        self.judge, self.engine, self.pools = judge, engine, pools
        self.work = Path(work_dir)
        self.log = log
        self.H = cfg.H
        self.space = plan_space(cfg.H)
        self.D = self.space.D
        jd = json.dumps(judge.describe(), sort_keys=True, default=str)
        self.tag = {"config": cfg.digest(), "judge": jd, "audit_version": AUDIT_VERSION}
        self.tag_p1 = {"config_p1": cfg.digest_p1(), "judge": jd, "audit_version": AUDIT_VERSION}
        jn = getattr(judge, "oracle_n", None)
        if cfg.majority:
            for i in self.instances:
                check_oracle_seeds(i, cfg.oracle_seeds, cfg.n_secondary)
                if cfg.floor_basis == "truth":
                    check_truth_seeds(i, cfg.oracle_seeds, TRUTH_N, cfg.n_secondary)
            if jn is not None and jn != cfg.oracle_seeds:
                raise ValueError(f"judge {judge.name} is set up for oracle_n={jn}, the oracle has {cfg.oracle_seeds} seeds")
        elif jn:
            raise ValueError(f"judge {judge.name} is set up for the majority oracle; the tasks file has none")
        self._oracle_keys = _KeySink()
        self.cache_floor_candidates = False       # phase 2: also write the floors' search candidates to the disk cache
        self._vstore: Dict[Path, dict] = {}
        self._last_plan_rollouts = 0
        self._shared_ms = 0
        self._check_pool_sizes()

    # -- paths and resume -------------------------------------------------------------------
    def _p(self, phase: str, inst: Instance) -> Path:
        d = "p1" if phase == "p1" else f"p2_{self.cfg.rule_tag()}"
        return self.work / self.cfg.tasks_tag() / d / f"{inst.file_stem}.pkl"

    def _done(self, phase: str, inst: Instance):
        p = self._p(phase, inst)
        if not p.exists():
            return None
        d = _load_pickle(p)
        if d.get("tag") != (self.tag_p1 if phase == "p1" else self.tag):
            self.log(f"  {p.name}: written by a different configuration or judge, recomputing")
            return None
        return d

    def _repair(self, X: np.ndarray) -> np.ndarray:
        """The seeded search's children in the grammar's canonical form (``clip_plan``), flat (n, H*25) int64."""
        X = np.asarray(X)
        return clip_plan(X.reshape(X.shape[0], self.H, N_COLS)).reshape(X.shape[0], -1).astype(np.int64)

    # -- per-instance plan and sizes ----------------------------------------------------------
    def inst_plan(self, inst: Instance) -> Dict[str, Tuple[int, ...]]:
        """{method: budgets} this instance runs (amendment 2: best-of-n on the first families only, verdict-scored
        random search above ``verdict_cap`` on the subset only)."""
        c = self.cfg
        out = {}
        for m in c.methods:
            b = tuple(c.budgets)
            if c.plan == "amendment2":
                if m == "best_of_n" and inst.family_id not in self._bon_families:
                    continue
                if m == "random_verdict" and inst.key not in self._subset:
                    b = tuple(x for x in b if x <= c.verdict_cap)
            if b:
                out[m] = b
        return out

    def cross_checked(self, inst: Instance) -> bool:
        return self.cfg.cross_check == "instance" and inst.key in self._subset

    def _mx(self, inst: Instance, methods) -> int:
        pl = self.inst_plan(inst)
        return max([max(pl[m]) for m in methods if m in pl] or [0])

    def _need_props(self, inst: Instance) -> int:
        """Behaviour proposals with K = 2 scores: the pool rows, random search's budgets and the seeded search's first
        generation (``cem_seeded_first``)."""
        n = max(self.cfg.pool_verdict_plans, self._mx(inst, ("random", "random_verdict")))
        pl = self.inst_plan(inst)
        if "cem_seeded" in pl:
            n = max(n, max(cem_seeded_first(B) for B in pl["cem_seeded"]))
        return n

    def _verd_need(self, inst: Instance, kind: str) -> int:
        """Leading pool rows that need 8-sample verdicts for this instance alone."""
        c, R = self.cfg, self.cfg.pool_verdict_plans
        if kind == "builders":
            if "best_of_n" not in self.inst_plan(inst):
                return 0
            return R if (c.verdict_rows == "all" or self.cross_checked(inst)) else 0
        own = self._mx(inst, ("random_verdict",))
        if c.verdict_rows == "all" or self.cross_checked(inst):
            own = max(own, R)
        return own

    def _verd_prefix(self, inst: Instance, kind: str) -> int:
        """Shared verdict prefix of the instance's (start, forced events) group: the largest need among the
        instances that share its judge samples, so no sample is computed twice."""
        sk = self._share_key(inst)
        return max(self._verd_need(j, kind) for j in self.instances
                   if j.start_id == inst.start_id and self._share_key(j) == sk)

    def _need_props_any(self) -> int:
        return max(self._need_props(i) for i in self.instances)

    def _check_pool_sizes(self) -> None:
        c = self.cfg
        Bmax = max(c.budgets)
        if c.plan == "amendment2" and c.beh_rows > min(c.verdict_cap, max(c.budgets)):
            raise ValueError("behaviour_plans must lie within the verdict prefix every instance computes "
                             f"(<= {min(c.verdict_cap, max(c.budgets))})")
        if "residual" in c.floors:
            if c.residual_pool in ("instance", "economy") and c.rows < Bmax:
                raise hd.PoolTooSmall(f"per-instance residual pools of {c.rows} rows are fewer than the "
                                      f"largest budget {Bmax}: raise --pool-verdict-plans or use a family pool")
            if c.residual_pool.startswith("family"):
                for task in T.TASKS:
                    k = sum(1 for i in self.instances if i.task == task)
                    if k and k * c.rows < Bmax:
                        raise hd.PoolTooSmall(
                            f"family residual pool for {task}: {k} instances x {c.rows} plans = "
                            f"{k * c.rows} rows, fewer than the largest budget {Bmax}: raise "
                            f"--pool-verdict-plans to at least {math.ceil(Bmax / k)}")

    # -- shared per-start computations ------------------------------------------------------
    def _share_key(self, inst: Instance) -> str:
        return inst.forced_key if self.judge.task_independent else inst.task

    def _shared(self, purpose: str, inst: Instance, seed: int, eff: np.ndarray, K: int) -> np.ndarray:
        """Per-sample statistics (n, K, len(STAT_FIELDS)) of judge samples of a per-start plan list, shared by the
        instances with the same forced events when the judge's samples do not depend on the task. Kept on disk
        under ``<work>/samples/``, which depends on the judge and the plans only (no threshold), so resumed runs,
        the other tasks of the start and re-scoring at another tasks file reuse them."""
        sk = self._share_key(inst)
        p = self.work / "samples" / "shared" / f"{inst.start_id}__{sk}__{purpose}__s{seed}__K{K}.npz"
        h = plan_hash(eff)
        if p.exists():
            with np.load(p) as z:
                if str(z["plan_hash"]) == h and str(z["tag"]) == self.tag["judge"]:
                    if "traj" in z.files:                      # whole trajectories (round 4): the statistics are exact
                        return traj_stats(z["traj"])
                    if _fields_ok(z):                          # statistics of another field list: rolled out again
                        return z["stats"]
        tr = self.judge.samples(inst, eff, K, (purpose, sk, seed))
        st = traj_stats(tr)
        self._check_stats([j for j in self.instances if j.start_id == inst.start_id and self._share_key(j) == sk], tr, st)
        self._shared_ms += int(eff.shape[0]) * K * self.H
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.stem + ".tmp.npz")
        np.savez(tmp, stats=st, fields=np.array(STAT_FIELDS), plan_hash=h, tag=self.tag["judge"])
        os.replace(tmp, p)
        return st

    def _plan_verdicts(self, inst: Instance, eff: np.ndarray, purpose: str) -> np.ndarray:
        """8-sample verdict statistics (m, 8, len(STAT_FIELDS)) of individual plans (economy verdict rows,
        selected plans), stored per plan under ``<work>/samples/plans/``: a plan whose verdict samples exist
        (from this run, another task of the start, or a run at another tasks file) is not rolled out again.
        Missing plans are sampled in one call whose stream names the set of plans."""
        sk = self._share_key(inst)
        p = self.work / "samples" / "plans" / f"{inst.start_id}__{sk}.npz"
        store = self._vstore.get(p)
        if store is None:
            store = {}
            if p.exists():
                with np.load(p) as z:
                    if str(z["tag"]) == self.tag["judge"] and _fields_ok(z):
                        store = {str(k): v for k, v in zip(z["keys"], z["stats"])}
            self._vstore[p] = store
        keys = [plan_hash(e) for e in eff]
        miss = sorted({k for k in keys if k not in store})
        if miss:
            first = {k: i for i, k in reversed(list(enumerate(keys)))}
            idx = [first[k] for k in miss]
            tag = hashlib.sha256("".join(miss).encode()).hexdigest()[:16]
            tr = self.judge.samples(inst, eff[idx], K_VERDICT, (purpose, sk, tag))
            st = traj_stats(tr)
            self._check_stats([j for j in self.instances if j.start_id == inst.start_id and self._share_key(j) == sk],
                              tr, st)
            for k, v in zip(miss, st):
                store[k] = v
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_name(p.stem + ".tmp.npz")
            ks = sorted(store)
            np.savez(tmp, keys=np.array(ks), stats=np.stack([store[k] for k in ks]), fields=np.array(STAT_FIELDS),
                     tag=self.tag["judge"])
            os.replace(tmp, p)
        self._last_plan_rollouts = len(miss)
        return np.stack([store[k] for k in keys])

    @staticmethod
    def _check_stats(insts: Sequence[Instance], tr: np.ndarray, st: np.ndarray) -> None:
        """New samples: the margins from the per-sample statistics equal those from the full trajectories, exactly,
        for every instance that will read them (the store's representation is checked where it is made)."""
        for j in insts:
            if not np.array_equal(np.asarray(task_margin(j, tr), dtype=np.float64), stats_margin(j, st)):
                raise ValueError(f"{j.key}: margins from the per-sample statistics differ from the trajectories'; the "
                                 f"predicate aggregates a quantity the store ({STAT_FIELDS}) does not represent")

    def _margin(self, inst: Instance, scal) -> np.ndarray:
        """Margins of full scalar trajectories (the engine's)."""
        return task_margin(inst, scal)

    def _smargin(self, inst: Instance, stats) -> np.ndarray:
        """Margins of judge samples, from their per-sample statistics."""
        return stats_margin(inst, stats)

    def engine_margins(self, inst: Instance, raw_plans, seeds, store=True) -> np.ndarray:
        eff = effective(raw_plans, inst.task, self.H)
        st = np.broadcast_to(np.asarray(store, dtype=bool), (eff.shape[0],))
        return self._margin(inst, self.engine.scalars(inst, eff, seeds, key_sink=self._oracle_keys,
                                                      **({} if st.all() else {"store": st})))

    def engine_margins9(self, inst: Instance, raw_plans, purpose: Optional[str] = None, store=True) -> np.ndarray:
        """(n, 1 + n_secondary) engine margins: the primary seed, then the secondary seeds. ``store``: per plan or one
        for all; False keeps new replays out of the disk cache (``EngineJudge.scalars``)."""
        if purpose:
            self._oracle_keys.purpose = purpose
        eff = effective(raw_plans, inst.task, self.H)
        S = verdict_seeds(inst, self.cfg.n_secondary)
        n, k = eff.shape[0], len(S)
        stk = np.repeat(np.broadcast_to(np.asarray(store, dtype=bool), (n,)), k)
        sc = self.engine.scalars(inst, np.repeat(eff, k, axis=0), np.tile(S, n), key_sink=self._oracle_keys,
                                 **({} if stk.all() else {"store": stk}))
        return self._margin(inst, sc).reshape(n, k)

    def oracle_judge(self, inst: Instance, raw_plans, purpose: Optional[str] = None, store=True) -> dict:
        """The majority oracle's judgement of plans (``oracle_judgement`` of their trajectories on the instance's
        ``cfg.oracle_seeds`` oracle seeds, replayed through the engine judge's cache; ``store`` as in
        ``engine_margins9``)."""
        if purpose:
            self._oracle_keys.purpose = purpose
        tr = oracle_trajectories(self.engine, inst, raw_plans, self.cfg.oracle_seeds, key_sink=self._oracle_keys,
                                 store=store)
        return oracle_judgement(inst, tr)

    def truth_margins(self, inst: Instance, raw_plans, ks, store=True, purpose: Optional[str] = None) -> np.ndarray:
        """(n, len(ks)) engine margins of plans on truth seeds ``ks`` (indices into ``truth_seed_list``)."""
        if purpose:
            self._oracle_keys.purpose = purpose
        eff = effective(raw_plans, inst.task, self.H)
        S = truth_seed_list(inst.start_id, inst.forced_key, self.H, TRUTH_N)
        seeds = np.array([S[k] for k in ks], dtype=np.int64)
        n, k = eff.shape[0], len(seeds)
        stk = np.repeat(np.broadcast_to(np.asarray(store, dtype=bool), (n,)), k)
        sc = self.engine.scalars(inst, np.repeat(eff, k, axis=0), np.tile(seeds, n), key_sink=self._oracle_keys,
                                 **({} if stk.all() else {"store": stk}))
        return self._margin(inst, sc).reshape(n, k)

    def truth_pool(self, inst: Instance, kind: str) -> Tuple[np.ndarray, dict, int, np.ndarray, np.ndarray]:
        """The truth-seed residual pool of one pool kind (floor basis "truth"): for the first R pool plans, search
        residual = the judge's K = 2 score minus the plan's mean margin over all TRUTH_N truth seeds, verdict residual
        = the 4th-largest of 8 judge margins minus the same mean (NaN where no verdict exists). The judge's scores
        and verdicts are re-read from the sample store (phase 1 computed them; nothing of phase 1 changes); under the
        economy rule the verdict rows the new search residuals keep and the store lacks are sampled here. Returns
        (pool, summary, verdict rows sampled here, s_j = each plan's sample standard deviation (ddof 1) of the margin
        over the TRUTH_N truth seeds, which the volatility and calibrated draws use, m_j = each plan's mean margin over
        them, which the calibrated draw uses)."""
        c, H, R, s0 = self.cfg, self.H, self.cfg.pool_verdict_plans, self.cfg.search_seeds[0]
        sk = self._share_key(inst)
        if kind == "behaviour":
            beh = self.pools.behaviour(inst.start_id)
            n_sh = max(self._need_props(j) for j in self.instances
                       if j.start_id == inst.start_id and self._share_key(j) == sk)
            search = self._smargin(inst, self._shared("prop", inst, s0, effective(beh[:n_sh], inst.task, H),
                                                      K_SEARCH)).mean(axis=1)[:R]
            n_eff = max(self._need_props(inst), self._verd_prefix(inst, "behaviour"), R)
            eff, raw = effective(beh[:n_eff], inst.task, H), beh[:R]
        else:
            bon = self.pools.builders(inst.start_id)
            n_b = max(max(self.inst_plan(inst)["best_of_n"]), R)
            eff, raw = effective(bon[:n_b], inst.task, H), bon[:R]
            search = self._smargin(inst, self._shared("bon", inst, s0, eff, K_SEARCH)).mean(axis=1)[:R]
        t = self.truth_margins(inst, raw, range(TRUTH_N), store=True, purpose="pool rows, truth seeds")
        t64 = t.mean(axis=1)
        mv, extra = self._verdicts(inst, kind, eff, search - t64, s0)
        pool = np.stack([search - t64, _fourth_largest(mv[:R]) - t64], axis=1)
        hv = np.isfinite(pool[:, 1])
        info = {"n_plans": int(R), "n_verdict_rows": int(hv.sum()), "verdict_rows_sampled_for_the_floor": int(extra),
                "residual_against": f"mean engine margin over {TRUTH_N} truth seeds",
                "residual_search": _summ(pool[:, 0]), "residual_verdict": _summ(pool[hv, 1]),
                "truth_margin_seed_sd_mean": float(np.mean(t.std(axis=1))),
                "truth_set_a_minus_b_sd": float(np.std(t[:, :TRUTH_A].mean(axis=1) - t[:, TRUTH_A:].mean(axis=1)))}
        return pool, info, int(extra), t.std(axis=1, ddof=1), t64

    @staticmethod
    def _pool(search: np.ndarray, fourth: np.ndarray, p8: np.ndarray, m9: np.ndarray,
              oracle_margin: Optional[np.ndarray] = None) -> Tuple[np.ndarray, dict]:
        """Paired residuals against the engine's mean margin over the verdict seeds (verdict column NaN on rows
        without 8-sample verdicts), and their summary. ``oracle_margin`` (majority oracle; NaN on rows without
        it): the confusion counts are taken against it on the rows that have it, instead of the primary seed."""
        mean9 = m9.mean(axis=1)
        pool = np.stack([search - mean9, fourth - mean9], axis=1)
        hv = np.isfinite(pool[:, 1])
        mad = [float(np.median(np.abs(c - np.median(c)))) for c in (pool[:, 0], pool[hv, 1])]
        prim = m9[:, 0]
        info = {
            "n_plans": int(len(search)), "n_verdict_rows": int(hv.sum()),
            "residual_against": f"mean engine margin over {m9.shape[1]} seeds",
            "residual_search": _summ(pool[:, 0]), "residual_verdict": _summ(pool[hv, 1]),
            "share_zero_residual": [float(np.mean(pool[:, 0] == 0)), float(np.mean(pool[hv, 1] == 0))],
            "zero_mad": [m == 0 for m in mad],
            "engine_margin_seed_sd_mean": float(np.mean(m9.std(axis=1))),
            "judge_accept_rate": float(np.mean(p8[hv] >= ACCEPT_P)), "engine_accept_rate_primary": float(np.mean(prim >= 0)),
            "engine_accept_rate_mean9": float(np.mean(mean9 >= 0)),
        }
        ref, rows = prim, hv
        if oracle_margin is not None:
            om = np.full(len(search), np.nan)
            om[:len(oracle_margin)] = np.asarray(oracle_margin, dtype=np.float64)[:len(search)]
            ref, rows = om, hv & np.isfinite(om)
            info["confusion_against"] = f"majority oracle, on the {int(rows.sum())} rows with both verdicts"
            info["engine_accept_rate_oracle"] = float(np.mean(om[np.isfinite(om)] >= 0)) if np.isfinite(om).any() else None
        info.update({
            "fp_count": int(np.sum((p8[rows] >= ACCEPT_P) & (ref[rows] < 0))), "fp_den": int(np.sum(ref[rows] < 0)),
            "fn_count": int(np.sum((p8[rows] < ACCEPT_P) & (ref[rows] >= 0))), "fn_den": int(np.sum(ref[rows] >= 0))})
        return pool, info

    def _verdicts(self, inst: Instance, kind: str, eff: np.ndarray, search_resid: np.ndarray, s0: int):
        """8-sample verdict margins (R, 8) of the pool rows, NaN where none are needed: the shared prefix of the
        instance's group, plus (economy verdict rows) the rows the economy rule keeps that the prefix misses.
        Returns (margins, number of rows sampled for this instance alone)."""
        c, R = self.cfg, self.cfg.pool_verdict_plans
        n_pref = self._verd_prefix(inst, kind)
        mv = np.full((max(R, n_pref), K_VERDICT), np.nan)
        if n_pref:
            mv[:n_pref] = self._smargin(inst, self._shared("verd" if kind == "behaviour" else "bverd", inst, s0,
                                                           eff[:n_pref], K_VERDICT))
        extra = 0
        if c.verdict_rows == "economy" and c.residual_pool == "economy":
            keep = economy_keep(search_resid, c.economy_top, c.economy_random,
                                np.random.default_rng(seed_for("audit-economy", inst.key, kind)))
            miss = np.flatnonzero(keep & ~np.isfinite(mv[:R, 0]))
            if miss.size:
                mv[miss] = self._smargin(inst, self._plan_verdicts(inst, eff[miss], "verdrows"))
                extra = int(self._last_plan_rollouts)
        return mv, extra

    # -- phase 1 -----------------------------------------------------------------------------
    def phase1(self, inst: Instance) -> dict:
        c, H = self.cfg, self.H
        t_start = time.time()
        timing: Dict[str, float] = {}
        self._oracle_keys = _KeySink()
        jc0, ec0 = self.judge.counters(), self.engine.counters()
        sh0 = self._shared_ms
        plan = self.inst_plan(inst)
        R = c.pool_verdict_plans
        s0 = c.search_seeds[0]
        n_pref0 = self._verd_prefix(inst, "behaviour")
        nb = min(c.beh_rows, n_pref0) if n_pref0 else c.beh_rows       # behaviour-table rows (<= R)

        beh = self.pools.behaviour(inst.start_id)
        flat_beh = beh.reshape(beh.shape[0], -1).astype(np.int64)
        n_prop = self._need_props(inst)
        n_pref = self._verd_prefix(inst, "behaviour")
        n_eff = max(n_prop, n_pref, R)
        if beh.shape[0] < n_eff:
            raise ValueError(f"{inst.start_id}: behaviour pool has {beh.shape[0]} plans, {n_eff} needed")
        eff_beh = effective(beh[:n_eff], inst.task, H)
        sk = self._share_key(inst)
        n_prop_sh = max(self._need_props(j) for j in self.instances
                        if j.start_id == inst.start_id and self._share_key(j) == sk)

        # search scores (K = 2) of the proposals, one sample stream per search seed (shared prefix of the group)
        t0 = time.time()
        prop_score = {}
        for s in c.search_seeds:
            tr = self._shared("prop", inst, s, effective(beh[:n_prop_sh], inst.task, H), K_SEARCH)
            prop_score[s] = self._smargin(inst, tr).mean(axis=1)[:n_prop]
        timing["proposals"] = time.time() - t0
        # engine margins of the pool rows on the primary and secondary seeds (search residuals need all rows)
        t0 = time.time()
        m9 = self.engine_margins9(inst, beh[:R], purpose="pool rows, nine seeds")
        ob = None
        if c.majority:      # the behaviour table's plans on the oracle's seeds (base rates, confusion rates)
            ob = self.oracle_judge(inst, beh[:nb], purpose="behaviour table, oracle seeds")
        timing["pool_engine"] = time.time() - t0
        # 8-sample verdicts where needed
        t0 = time.time()
        mv, extra_b = self._verdicts(inst, "behaviour", eff_beh, prop_score[s0][:R] - m9.mean(axis=1), s0)
        p8 = (mv >= 0).mean(axis=1)
        p8[~np.isfinite(mv[:, 0])] = np.nan
        timing["pool_verdicts"] = time.time() - t0
        pools, pool_info = {}, {}
        pools["behaviour"], pool_info["behaviour"] = self._pool(prop_score[s0][:R], _fourth_largest(mv[:R]), p8[:R], m9,
                                                                None if ob is None else ob["margin"])
        pool_info["behaviour"]["verdict_rows_sampled_for_this_instance"] = extra_b
        pool_info["behaviour"]["verdict_prefix"] = n_pref

        # builder pool: best-of-n proposals and their own residual pool
        bon_score, flat_bon, extra_d = {}, None, 0
        if "best_of_n" in plan:
            t0 = time.time()
            bon = self.pools.builders(inst.start_id)
            Bb = max(plan["best_of_n"])
            n_b = max(Bb, R)
            if bon.shape[0] < n_b:
                raise ValueError(f"{inst.start_id}: builder pool has {bon.shape[0]} plans, {n_b} needed")
            flat_bon = bon.reshape(bon.shape[0], -1).astype(np.int64)[:Bb]
            eff_bon = effective(bon[:n_b], inst.task, H)
            for s in c.search_seeds:
                bon_score[s] = self._smargin(inst, self._shared("bon", inst, s, eff_bon, K_SEARCH)).mean(axis=1)
            m9b = self.engine_margins9(inst, bon[:R], purpose="pool rows, nine seeds")
            mvb, extra_d = self._verdicts(inst, "builders", eff_bon, bon_score[s0][:R] - m9b.mean(axis=1), s0)
            p8b = (mvb >= 0).mean(axis=1)
            p8b[~np.isfinite(mvb[:, 0])] = np.nan
            pools["builders"], pool_info["builders"] = self._pool(bon_score[s0][:R], _fourth_largest(mvb[:R]), p8b[:R], m9b)
            if c.majority:
                pool_info["builders"]["confusion_against"] = "primary seed (diagnostic only; not the oracle)"
            pool_info["builders"]["verdict_rows_sampled_for_this_instance"] = extra_d
            pool_info["builders"]["verdict_prefix"] = self._verd_prefix(inst, "builders")
            timing["builder_scores"] = time.time() - t0

        init = hd.fit_marginals(self.space, flat_beh) if ("cem" in plan or "cem_seeded" in plan) else None
        rows, sel_plans = [], []
        for s in c.search_seeds:
            n_rv = max(plan.get("random_verdict", (0,)))
            tie = np.random.default_rng(seed_for("audit-tiebreak", inst.key, s)).random(max(n_rv, 1))
            for method, budgets in plan.items():
                attacker, scoring = METHODS[method]
                t_m = time.time()
                for B in budgets:
                    ms0 = self.judge.month_steps
                    if method == "random":
                        sel = hd.random_shooting(_Lookup(flat_beh, prop_score[s]), flat_beh[:n_prop], B)
                        ms_search = sel.log["n_scored"] * K_SEARCH * H
                    elif method == "random_verdict":
                        vs = (p8[:n_rv] >= ACCEPT_P).astype(np.float64) + TIE_BREAK * tie[:n_rv]
                        sel = hd.random_shooting(_Lookup(flat_beh, vs), flat_beh[:n_rv], B)
                        ms_search = sel.log["n_scored"] * K_VERDICT * H
                    elif method == "best_of_n":
                        sel = hd.best_of_n(_Lookup(flat_bon, bon_score[s]), flat_bon, B)
                        ms_search = sel.log["n_scored"] * K_SEARCH * H
                    elif method == "cem_seeded":
                        calls = [0]
                        look = _Lookup(flat_beh, prop_score[s])

                        def score(X, B=B, s=s, calls=calls, look=look):
                            calls[0] += 1
                            if calls[0] == 1:      # generation 0: the first N proposals, random search's K = 2 scores
                                return look(X)
                            tr = self.judge.samples(inst, effective(X, inst.task, H), K_SEARCH,
                                                    ("cem_seeded", inst.task, B, s, calls[0] - 1))
                            st = traj_stats(tr)
                            self._check_stats([inst], tr, st)
                            return self._smargin(inst, st).mean(axis=1)

                        sel = hd.cem_seeded(score, self.space, B, np.random.default_rng(seed_for("audit-cem-seeded", inst.key, B, s)),
                                            flat_beh[:n_prop], init, block=N_COLS, repair=self._repair)
                        ms_search = sel.log["n_scored"] * K_SEARCH * H
                        ms_new = self.judge.month_steps - ms0
                        assert ms_new == (B - cem_seeded_first(B)) * K_SEARCH * H
                    else:
                        calls = [0]

                        def score(X, B=B, s=s, calls=calls):
                            tr = self.judge.samples(inst, effective(X, inst.task, H), K_SEARCH,
                                                    ("cem", inst.task, B, s, calls[0]))
                            calls[0] += 1
                            st = traj_stats(tr)
                            self._check_stats([inst], tr, st)
                            return self._smargin(inst, st).mean(axis=1)

                        sel = hd.cem(score, self.space, B, np.random.default_rng(seed_for("audit-cem", inst.key, B, s)), init)
                        ms_search = self.judge.month_steps - ms0
                        assert ms_search == sel.log["n_scored"] * K_SEARCH * H
                    n_scored = int(sel.log["n_scored"])
                    if n_scored != B:
                        raise hd.BudgetError(f"{inst.key} {method} B={B}: scored {n_scored}")
                    j = int(sel.log["best_index"])
                    row = {
                        "instance": inst.key, "cluster": inst.family_id, "start_id": inst.start_id, "task": inst.task,
                        "in_band": inst.in_band, "method": method, "attacker": attacker, "scoring": scoring,
                        "budget": n_scored, "attacker_seed": int(s),
                        "plan_id": f"{inst.key}|{method}|B{n_scored}|s{s}", "n_scored": n_scored,
                        "best_index": j, "best_score": float(sel.log["best_score"]),
                        "emu_month_steps_search": int(ms_search), "emu_month_steps_verdict": K_VERDICT * H,
                        "subset": inst.key in self._subset,
                    }
                    if method == "cem_seeded":
                        row["emu_month_steps_search_new"] = int(ms_new)      # beyond the shared proposal samples
                        row["best_per_generation"] = [float(x) for x in sel.log["best_per_generation"]]
                        row["blocks_replaced"] = int(sel.log["blocks_replaced"])
                    if method == "random_verdict":
                        row["grader_p_selection"] = float(p8[j])
                        row["grader_score"] = float(prop_score[s][j])
                    elif method == "random":
                        row["grader_score"] = float(prop_score[s][j])
                    elif method == "best_of_n":
                        row["grader_score"] = float(bon_score[s][j])
                    else:
                        row["grader_score"] = float(sel.log["best_score"])
                    rows.append(row)
                    sel_plans.append(np.asarray(sel.plan, dtype=np.int64).reshape(H, N_COLS))
                timing[f"attack_{method}_s{s}"] = time.time() - t_m

        # verdicts of every selected plan: 8 fresh judge samples, engine on the primary and secondary seeds
        t0 = time.time()
        SP = np.stack(sel_plans)
        eff_sel = effective(SP, inst.task, H)
        mf = self._smargin(inst, self._plan_verdicts(inst, eff_sel, "sel"))                          # (r, 8)
        sel_rollouts = int(self._last_plan_rollouts)
        timing["verdict_selected"] = time.time() - t0
        t0 = time.time()
        me = self.engine_margins9(inst, SP, purpose="selected plans, nine seeds")
        S1 = me.shape[1]
        oj = self.oracle_judge(inst, SP, purpose="selected plans, oracle seeds") if c.majority else None
        timing["engine_selected"] = time.time() - t0
        for r, row in enumerate(rows):
            p_fresh = float(np.mean(mf[r] >= 0))
            row["grader_p_fresh"] = p_fresh
            row["grader_p"] = row["grader_p_selection"] if row["scoring"] == "verdict" else p_fresh
            row["grader_margins_fresh"] = [float(x) for x in mf[r]]
            if oj is None:
                row["oracle_margin"] = float(me[r, 0])
                row["oracle_accept"] = bool(me[r, 0] >= 0)
                row["oracle_margins_seeds"] = [float(x) for x in me[r, 1:]]
                row["oracle_accept_seeds"] = [bool(x >= 0) for x in me[r, 1:]]
                row["oracle_margin_mean9"] = float(me[r].mean())
                row["engine_city_months_judge"] = S1 * H
            else:
                row.update(_oracle_fields(oj, r))
                row["nine_seed_margins"] = [float(x) for x in me[r]]     # primary + secondary: the residual seeds
                row["nine_seed_mean"] = float(me[r].mean())
                row["engine_city_months_judge"] = (S1 + c.oracle_seeds) * H
            row["plan_hash"] = plan_hash(eff_sel[r])
        jc1, ec1 = self.judge.counters(), self.engine.counters()
        if ob is None:
            behaviour = {"grader_p": p8[:nb].copy(), "oracle_margin": m9[:nb, 0].copy()}     # nb <= R
        else:
            behaviour = {"grader_p": p8[:nb].copy(), "oracle_margin": ob["margin"].copy(), "oracle_share": ob["share"].copy(),
                         "oracle_margin_seed0": ob["margin_seed0"].copy(), "primary_margin": m9[:nb, 0].copy()}
        costs = {"seconds": time.time() - t_start, "timing": timing, **_delta(jc0, jc1), **_delta(ec0, ec1),
                 "engine_workers": getattr(self.engine, "workers", 0),
                 "oracle_distinct_replays": len(self._oracle_keys),
                 "shared_month_steps_computed": self._shared_ms - sh0}
        if c.majority:
            costs["oracle_distinct_replays_by_purpose"] = dict(self._oracle_keys.by_purpose)
        return {
            "tag": self.tag_p1, "instance": asdict(inst), "plan": {m: list(b) for m, b in plan.items()},
            "rows": rows, "selected_plans": SP.astype(np.int16),
            "selected_effective": eff_sel, "pools": pools, "pool_info": pool_info,
            "behaviour": behaviour,
            "extra_verdict_rows": {"behaviour": extra_b, "builders": extra_d},
            "selected_verdict_rollouts": sel_rollouts,
            "costs": costs,
        }

    # -- floors -------------------------------------------------------------------------------
    def residual_surrogates(self, p1: Dict[str, dict], rule: Optional[str] = None,
                            only: Optional[set] = None) -> Dict[str, Dict[str, object]]:
        """instance key -> {pool kind -> residual surrogate} under ``rule`` (default ``cfg.residual_pool``) for the
        pool kinds each instance's plan uses; ``only``: restrict to these instance keys (the cross-check)."""
        c = self.cfg
        rule = rule or c.residual_pool
        cfg = c if rule == c.residual_pool else AuditConfig(**{**c.to_dict(), "residual_pool": rule,
                                                               "budgets": tuple(c.budgets), "methods": tuple(c.methods),
                                                               "search_seeds": tuple(c.search_seeds),
                                                               "floors": tuple(c.floors), "verdict_rows": "all"})
        insts = [i for i in self.instances if only is None or i.key in only]
        out: Dict[str, Dict[str, object]] = {i.key: {} for i in insts}
        for kind in ("behaviour", "builders"):
            for task in T.TASKS:
                mem = [i for i in insts if i.task == task and kind in {POOL_OF[m] for m in self.inst_plan(i)}]
                if not mem:
                    continue
                pools = [np.asarray(p1[i.key]["pools"][kind])[:c.rows] for i in mem]
                if rule != "economy" and any(not np.isfinite(p).all() for p in pools):
                    raise ValueError(f"rule {rule} needs verdict residuals on every pool row ({kind}, {task})")
                surr, note = residual_pool_rule(cfg, pools, task, kind, [i.key for i in mem])
                if note:
                    self.log(f"  {rule} {kind} residual pools of {task}: {note}")
                for i, sg in zip(mem, surr):
                    out[i.key][kind] = sg
        return out

    def flip_rates(self, p1: Dict[str, dict]) -> dict:
        """Confusion rates of the 8-sample verdict against the oracle's verdict (the primary seed's, or the
        majority oracle's) on the first ``cfg.beh_rows`` behaviour plans of each instance: pooled within each
        task family and over all."""
        n = self.cfg.beh_rows

        def rates(insts):
            g = np.concatenate([p1[i.key]["behaviour"]["grader_p"][:n] for i in insts]) >= ACCEPT_P
            o = np.concatenate([p1[i.key]["behaviour"]["oracle_margin"][:n] for i in insts]) >= 0
            return {"fp": float((g & ~o).sum() / (~o).sum()) if (~o).any() else 0.0,
                    "fn": float((~g & o).sum() / o.sum()) if o.any() else 0.0,
                    "n_behaviour_plans": int(g.size), "n_oracle_reject": int((~o).sum()), "n_oracle_accept": int(o.sum())}

        by_task = {t: rates([i for i in self.instances if i.task == t]) for t in T.TASKS
                   if any(i.task == t for i in self.instances)}
        out = {"mode": self.cfg.flip_rates, "by_task": by_task, **rates(self.instances),
               "pooled_over": "task family" if self.cfg.flip_rates == "family" else "every behaviour plan of the run",
               "verdicts": "8-sample judge verdict against the primary-seed engine verdict",
               "behaviour_plans_per_instance": n}
        if self.cfg.majority:
            out["verdicts"] = (f"8-sample judge verdict against the majority oracle's verdict ({self.cfg.oracle_seeds} "
                               f"oracle seeds, accepted at a pass share >= {T.ORACLE_PASS})")
        return out

    def flip_runs(self, floor_method: str, B: int, plan: Dict[str, Tuple[int, ...]]) -> bool:
        """Whether the flip floor's attack runs for this floor method and budget: always under ``flip_scope`` "all";
        under "verdict" only where verdict-scored random search runs (its floor attack is random shooting)."""
        if self.cfg.flip_scope == "all":
            return True
        return floor_method == FLOOR_METHOD["random_verdict"] and B in plan.get("random_verdict", ())

    def attaches(self, scoring: str, kind: str) -> bool:
        """Whether a record of this scoring carries the floor ``kind`` (the flip floor: every record under
        ``flip_scope`` "all", verdict-scored records only under "verdict")."""
        return kind != "flip" or self.cfg.flip_scope == "all" or scoring == "verdict"

    def _flip_for(self, flips: dict, inst: Instance) -> Tuple[float, float]:
        r = flips["by_task"][inst.task] if flips["mode"] == "family" else flips
        return r["fp"], r["fn"]

    def phase2(self, inst: Instance, p1i: dict, resid_surr: Dict[str, object], flips: dict,
               cross_surr: Optional[Dict[str, object]] = None) -> dict:
        """Floors. Residual surrogate: score = nine-seed mean engine margin + drawn search residual, accept when
        nine-seed mean + paired verdict residual >= 0, outcome judged by the oracle. Flip surrogate: the oracle's
        verdict flipped at fp, fn. The oracle is the primary seed (the selected plan's secondary verdicts are
        recorded) or, under the majority oracle, ``oracle_judge`` (the selected plan's per-seed oracle margins and
        verdicts, pass share, seed-0 verdict and nine-seed margins are recorded; every flip candidate is replayed
        on the oracle's seeds, because the flip surrogate flips the oracle's verdict)."""
        c, H = self.cfg, self.H
        t_start = time.time()
        self._oracle_keys = _KeySink()
        ec0 = self.engine.counters()
        beh = self.pools.behaviour(inst.start_id)
        flat_beh = beh.reshape(beh.shape[0], -1).astype(np.int64)
        plan = self.inst_plan(inst)
        flat_bon = None
        if "best_of_n" in plan:
            flat_bon = self.pools.builders(inst.start_id).reshape(-1, self.D).astype(np.int64)[:max(plan["best_of_n"])]
        init = hd.fit_marginals(self.space, flat_beh) if ("cem" in plan or "cem_seeded" in plan) else None
        pseed = primary_seed(inst)
        cur = {"method": ""}
        # what goes to the engine's disk cache: pool plans only (behaviour and builder plans, which every checkpoint
        # and the residual pools look up again); the floors' cross-entropy candidates and their selections are
        # replayed for this instance alone and kept in memory until it is done (a killed instance is recomputed)
        if hasattr(self.engine, "clear_transient"):
            self.engine.clear_transient()
        nkeep = max(c.pool_verdict_plans, max(c.budgets))
        poolrows = {np.ascontiguousarray(x, dtype=np.int64).tobytes()
                    for x in self.pools.behaviour(inst.start_id)[:nkeep].reshape(-1, self.D)}
        if "best_of_n" in plan:
            poolrows |= {np.ascontiguousarray(x, dtype=np.int64).tobytes()
                         for x in self.pools.builders(inst.start_id)[:nkeep].reshape(-1, self.D)}

        def keep(X) -> np.ndarray:
            X = np.ascontiguousarray(X, dtype=np.int64).reshape(-1, self.D)
            return np.array([x.tobytes() in poolrows for x in X], dtype=bool)

        def store(X) -> np.ndarray:
            """What goes to the disk cache: pool plans; everything when ``cache_floor_candidates`` is set (an engine-only
            run whose next run replays the same candidates, e.g. the other pool rule; records do not depend on it)."""
            return np.ones(len(np.asarray(X).reshape(-1, self.D)), dtype=bool) if self.cache_floor_candidates else keep(X)

        truth = c.floor_basis == "truth"
        vol = c.residual_draw == "volatility"
        cal = c.residual_draw == "calibrated"
        need_sd = vol or cal                     # the draws that read s(y)
        jc0 = self.judge.counters()
        tpools, tinfo, textra, tdesc, tsd, tmean, own_rows = {}, {}, {}, {}, {}, {}, {}
        search_sd: Dict[bytes, float] = {}       # volatility and calibrated draws: s(y) of every plan the search truth saw
        if truth:
            # truth-seed residual pools of this instance, and its surrogates (per-instance rules only)
            for kind in sorted({POOL_OF[m] for m in plan}):
                tpools[kind], tinfo[kind], textra[kind], tsd[kind], tmean[kind] = self.truth_pool(inst, kind)
            resid_surr, cross_surr = {}, ({} if self.cross_checked(inst) else None)
            cfg_a = AuditConfig(**{**c.to_dict(), "residual_pool": "instance", "budgets": tuple(c.budgets),
                                   "methods": tuple(c.methods), "search_seeds": tuple(c.search_seeds),
                                   "floors": tuple(c.floors), "verdict_rows": "all"})
            for kind, pool in tpools.items():
                if "residual" in c.floors:
                    resid_surr[kind] = residual_pool_rule(c, [pool], inst.task, kind, [inst.key])[0][0]
                    if vol:
                        resid_surr[kind] = volatility_surrogate(resid_surr[kind], tsd[kind], c.residual_draw_k)
                    if cal:
                        resid_surr[kind] = calibrated_surrogate(resid_surr[kind], tmean[kind], tsd[kind],
                                                                c.residual_draw_k)
                    tdesc[kind] = resid_surr[kind].describe()
                if cross_surr is not None:
                    cross_surr[kind] = residual_pool_rule(cfg_a, [pool], inst.task, kind, [inst.key])[0][0]
                    if vol:
                        cross_surr[kind] = volatility_surrogate(cross_surr[kind], tsd[kind], c.residual_draw_k)
                    if cal:
                        cross_surr[kind] = calibrated_surrogate(cross_surr[kind], tmean[kind], tsd[kind],
                                                                c.residual_draw_k)
                if cal:            # the rows of this pool that hold a candidate's own plan, left out of its draw
                    raw = self.pools.behaviour(inst.start_id) if kind == "behaviour" else self.pools.builders(inst.start_id)
                    own_rows[kind] = own_pool_rows(raw, len(pool))

            def truth_search(X):
                """Search-time truth: a pool plan's mean over truth set A, a candidate's over seeds 0..cand-1 (under the
                volatility and calibrated draws the standard deviation over the same seeds is kept for ``truth_sd``)."""
                X = np.ascontiguousarray(X, dtype=np.int64).reshape(-1, self.D)
                kp, out = keep(X), np.empty(X.shape[0])
                sd = np.empty(X.shape[0])
                if kp.any():
                    t = self.truth_margins(inst, X[kp], range(TRUTH_A), True, f"floors {cur['method']}: truth seeds")
                    out[kp] = t.mean(axis=1)
                    if need_sd:
                        sd[kp] = t.std(axis=1, ddof=1)
                if (~kp).any():
                    t = self.truth_margins(inst, X[~kp], range(c.truth_cand_seeds), self.cache_floor_candidates,
                                           f"floors {cur['method']}: truth seeds")
                    out[~kp] = t.mean(axis=1)
                    if need_sd:
                        sd[~kp] = t.std(axis=1, ddof=1)
                if need_sd:
                    for x, v in zip(X, sd):
                        search_sd[x.tobytes()] = float(v)
                return out

            def truth_sd(X):
                """s(y) of plans the search truth has seen (the grader asks for the margin first)."""
                X = np.ascontiguousarray(X, dtype=np.int64).reshape(-1, self.D)
                return np.array([search_sd[x.tobytes()] for x in X], dtype=np.float64)

            def truth_accept(X):
                """Accept-time truth of a selected plan: its mean over truth set B (never used to select)."""
                X = np.ascontiguousarray(X, dtype=np.int64).reshape(-1, self.D)
                return self.truth_margins(inst, X, range(TRUTH_A, TRUTH_N), store(X),
                                          f"floors {cur['method']}: truth seeds").mean(axis=1)

            basis, accept_basis = hd.OracleCache(truth_search), hd.OracleCache(truth_accept)
            mean9 = basis
        else:
            mean9 = hd.OracleCache(lambda X: self.engine_margins9(inst, X, purpose=f"floors {cur['method']}: nine seeds",
                                                                  store=store(X)).mean(axis=1))
            accept_basis = None
        if c.majority:
            primary = hd.OracleCache(lambda X: self.oracle_judge(
                inst, X, purpose=f"floors {cur['method']}: oracle seeds", store=store(X))["margin"])
        else:
            primary = hd.OracleCache(lambda X: self.engine_margins(inst, X, pseed, store=store(X)))
        n_prop = self._need_props(inst)
        evals_by_method: Dict[str, dict] = {}

        def attack(method, B, s):
            if method == "random":
                return lambda sc: hd.random_shooting(sc, flat_beh[:n_prop], B)
            if method == "best_of_n":
                return lambda sc: hd.best_of_n(sc, flat_bon, B)
            if method == "cem_seeded":
                return lambda sc: hd.cem_seeded(sc, self.space, B, np.random.default_rng(seed_for("audit-cem-seeded", inst.key, B, s)),
                                                flat_beh[:n_prop], init, block=N_COLS, repair=self._repair)
            return lambda sc: hd.cem(sc, self.space, B, np.random.default_rng(seed_for("audit-cem", inst.key, B, s)), init)

        res, timing = {}, {}
        fbudgets: Dict[str, set] = {}
        for m, bs in plan.items():
            fbudgets.setdefault(FLOOR_METHOD[m], set()).update(bs)
        for s in c.search_seeds:
            for method in sorted(fbudgets):
                t_m = time.time()
                cur["method"] = method
                n9_0, no_0 = mean9.n_evals, primary.n_evals
                graders = {}
                vkw = {"volatility": truth_sd} if vol else {}
                if cal:
                    vkw = {"volatility": truth_sd, "pool_rows": own_rows[POOL_OF[method]]}
                if cross_surr is not None:
                    graders["residualA"] = hd.SurrogateGrader(
                        cross_surr[POOL_OF[method]], mean9,
                        np.random.default_rng(seed_for("audit-floor", inst.key, method, "residualA", s)), judge_margin=primary,
                        accept_margin=accept_basis, **vkw)
                if "residual" in c.floors:
                    graders["residual"] = hd.SurrogateGrader(
                        resid_surr[POOL_OF[method]], mean9,
                        np.random.default_rng(seed_for("audit-floor", inst.key, method, "residual", s)), judge_margin=primary,
                        accept_margin=accept_basis, **vkw)
                if "flip" in c.floors:
                    graders["flip"] = hd.SurrogateGrader(
                        hd.FlipSurrogate(*self._flip_for(flips, inst)), primary,
                        np.random.default_rng(seed_for("audit-floor", inst.key, method, "flip", s)))
                for B in sorted(fbudgets[method]):
                    for k, gr in graders.items():
                        if k == "flip" and not self.flip_runs(method, B, plan):
                            continue
                        n0 = len(self._oracle_keys)
                        r = hd.attack_surrogate(attack(method, B, s), gr, budget=B)
                        kp = store(r.plan[None])
                        m9 = None if truth else self.engine_margins9(
                            inst, r.plan[None], purpose=f"floors {method}: selected plans, nine seeds", store=kp)[0]
                        if c.majority:
                            oj = self.oracle_judge(inst, r.plan[None], purpose=f"floors {method}: oracle seeds", store=kp)
                            if float(oj["margin"][0]) != r.oracle_margin or bool(oj["accept"][0]) != r.oracle_accept:
                                raise RuntimeError(f"{inst.key} {method} B={B} {k}: the floor's verdict is not the oracle's")
                            ent = {"grader_accept": bool(r.surrogate_accept), **_oracle_fields(oj, 0),
                                   "score": float(r.surrogate_score)}
                            if m9 is not None:
                                ent.update(nine_seed_margins=[float(x) for x in m9], nine_seed_mean=float(m9.mean()))
                            if "accept_basis_margin" in r.log:
                                ent.update(truth_search=r.log["search_basis_margin"], truth_accept=r.log["accept_basis_margin"],
                                           accept_at_search=r.log["accept_at_search"],
                                           verdict_residual_drawn=r.log["verdict_residual_drawn"])
                            if need_sd and k.startswith("residual"):
                                ent["search_sd"] = float(truth_sd(r.plan[None])[0])
                        else:
                            assert float(m9[0]) == r.oracle_margin
                            ent = {
                                "grader_accept": bool(r.surrogate_accept), "oracle_accept": bool(r.oracle_accept),
                                "oracle_accept_seeds": [bool(x >= 0) for x in m9[1:]],
                                "oracle_margins_seeds": [float(x) for x in m9[1:]],
                                "score": float(r.surrogate_score), "oracle_margin": float(r.oracle_margin),
                                "oracle_margin_mean9": float(m9.mean())}
                        ent.update({
                            "plan": np.asarray(r.plan, dtype=np.int16),          # the floor's selected plan (raw)
                            "n_scored": int(r.log["surrogate_n_scored"]),
                            "engine_replays": len(self._oracle_keys) - n0,
                            "pool_kind": r.log.get("residual_pool_kind"), "pool_size": r.log.get("residual_pool_size"),
                            "pool_rule": r.log.get("residual_pool_rule"),
                            "pool_source": POOL_OF[method] if k.startswith("residual") else None,
                            "zero_mad_instances": r.log.get("residual_zero_mad_instances"),
                            "target_zero_mad": r.log.get("residual_target_zero_mad"),
                        })
                        res[(method, B, s, k)] = ent
                timing[f"floors_{method}_s{s}"] = time.time() - t_m
                evals_by_method[f"{method}_s{s}"] = {("truth_search_evals" if truth else "nine_seed_mean_evals"):
                                                     mean9.n_evals - n9_0, "oracle_evals": primary.n_evals - no_0}
        if hasattr(self.engine, "clear_transient"):
            self.engine.clear_transient()
        costs = {"seconds": time.time() - t_start, "timing": timing, **_delta(ec0, self.engine.counters()),
                 "engine_workers": getattr(self.engine, "workers", 0),
                 "oracle_distinct_replays": len(self._oracle_keys)}
        if truth:     # judge rollouts of verdict rows the truth-seed pools keep (economy rule) happen here
            costs.update(_delta(jc0, self.judge.counters()))
        out = {"tag": self.tag, "floors": res,
               "oracle_cache": {"mean9_evals": mean9.n_evals, "primary_evals": primary.n_evals}, "costs": costs}
        if truth:
            out.update(truth_pools=tpools, truth_pool_info=tinfo, truth_extra_verdict_rows=textra,
                       residual_pools_describe=tdesc)
            if vol:
                out["truth_pool_sd"] = tsd
            if cal:
                out["truth_pool_sd"], out["truth_pool_mean"] = tsd, tmean
        if c.majority:
            costs["oracle_distinct_replays_by_purpose"] = dict(self._oracle_keys.by_purpose)
            out["oracle_cache"] = {"mean9_evals": mean9.n_evals, "oracle_evals": primary.n_evals,
                                   "by_method": evals_by_method}
        return out

    # -- run -----------------------------------------------------------------------------------
    def run(self, crash_after: Optional[Tuple[str, int]] = None) -> dict:
        c = self.cfg
        p1: Dict[str, dict] = {}
        t_run = time.time()
        for n_done, inst in enumerate(self.instances):
            d = self._done("p1", inst)
            if d is None:
                if crash_after and crash_after[0] == "p1" and n_done >= crash_after[1]:
                    raise Crash(f"simulated kill before phase 1 of instance {n_done}")
                t0 = time.time()
                d = self.phase1(inst)
                _atomic_pickle(d, self._p("p1", inst))
                self.log(f"[p1 {n_done + 1}/{len(self.instances)}] {inst.key}: {time.time() - t0:.1f} s; "
                         f"judge month-steps {d['costs'].get('judge_month_steps', 0):,}, "
                         f"engine replays {d['costs'].get('engine_replays', 0):,}")
            p1[inst.key] = d
        p2: Dict[str, dict] = {}
        flips = self.flip_rates(p1) if "flip" in c.floors else None
        truth = c.floor_basis == "truth"         # truth-seed pools are made per instance inside phase 2
        rs = self.residual_surrogates(p1) if ("residual" in c.floors and not truth) else {}
        xs = {}
        if c.cross_check == "instance" and not truth:
            xs = self.residual_surrogates(p1, rule="instance", only={i.key for i in self.instances if self.cross_checked(i)})
        for n_done, inst in enumerate(self.instances):
            d = self._done("p2", inst)
            if d is None:
                if crash_after and crash_after[0] == "p2" and n_done >= crash_after[1]:
                    raise Crash(f"simulated kill before phase 2 of instance {n_done}")
                t0 = time.time()
                d = self.phase2(inst, p1[inst.key], rs.get(inst.key, {}), flips, xs.get(inst.key))
                _atomic_pickle(d, self._p("p2", inst))
                self.log(f"[p2 {n_done + 1}/{len(self.instances)}] {inst.key}: {time.time() - t0:.1f} s; "
                         f"engine replays {d['costs'].get('engine_replays', 0):,} "
                         f"(remote {d['costs'].get('engine_replays_remote', 0):,})")
            p2[inst.key] = d
        out = self.assemble(p1, p2, flips, rs, time.time() - t_run)
        out["cross_check_pools"] = {k: {kind: v.describe() for kind, v in d.items()} for k, d in xs.items()}
        return out

    # -- outputs -------------------------------------------------------------------------------
    def assemble(self, p1, p2, flips, rs, seconds) -> dict:
        c = self.cfg
        records, plans, plans_eff, costs = [], [], [], []
        for inst in self.instances:
            d1, d2 = p1[inst.key], p2[inst.key]
            for r, row in enumerate(d1["rows"]):
                row = dict(row)
                fm = FLOOR_METHOD[row["method"]]
                n_floor = 0
                kinds = list(c.floors) + (["residualA"] if self.cross_checked(inst) else [])
                names = (("grader_accept", "oracle_accept", "oracle_share", "oracle_accept_seed0", "oracle_margin_seed0",
                          "oracle_accept_seeds", "oracle_margins_seeds", "score", "oracle_margin", "nine_seed_mean",
                          "truth_search", "truth_accept", "accept_at_search", "verdict_residual_drawn", "search_sd",
                          "engine_replays")
                         if c.majority else
                         ("grader_accept", "oracle_accept", "oracle_accept_seeds", "oracle_margins_seeds", "score",
                          "oracle_margin", "oracle_margin_mean9", "engine_replays"))
                pl = self.inst_plan(inst)
                fm_row = fm in pl and row["budget"] in pl[fm]          # a record of the floor's own method exists
                for k in kinds:
                    if not self.attaches(row["scoring"], k):
                        continue
                    f = d2["floors"][(fm, row["budget"], row["attacker_seed"], k)]
                    for name in names:
                        if name in f:
                            row[f"{k}_{name}"] = f[name]
                    # a floor attack shared with the record of the floor's own method is counted on that record
                    if row["method"] == fm or not (fm_row and self.attaches(METHODS[fm][1], k)):
                        n_floor += f["engine_replays"]
                    if k.startswith("residual"):
                        row[f"{k}_pool_kind"] = f["pool_kind"]
                        row[f"{k}_pool_size"] = f["pool_size"]
                    if k == "residual":
                        row["residual_pool_kind"] = f["pool_kind"]
                        row["residual_pool_rule"] = f.get("pool_rule")
                        row["residual_pool_size"] = f["pool_size"]
                        row["residual_pool_source"] = f["pool_source"]
                        row["residual_zero_mad_instances"] = f["zero_mad_instances"]
                        row["residual_target_zero_mad"] = f["target_zero_mad"]
                row["n_floor_oracle_evals"] = n_floor
                row["engine_city_months_floor"] = n_floor * self.H
                row["emu_month_steps"] = row["emu_month_steps_search"] + row["emu_month_steps_verdict"]
                row["engine_city_months"] = row["engine_city_months_judge"] + row["engine_city_months_floor"]
                records.append(row)
                plans.append(d1["selected_plans"][r])
                plans_eff.append(d1["selected_effective"][r])
            costs.append({"instance": inst.key, "phase1": d1["costs"], "phase2": d2["costs"]})
        if c.floor_basis == "truth":
            rp = {i.key: p2[i.key].get("residual_pools_describe", {}) for i in self.instances}
        else:
            rp = {k: {kind: v.describe() for kind, v in d.items()} for k, d in rs.items()} if rs else {}
        return {"records": records, "plans": np.stack(plans), "plans_effective": np.stack(plans_eff), "costs": costs,
                "flip_rates": flips, "p1": p1, "p2": p2, "seconds": seconds, "residual_pools": rp}


def _oracle_fields(oj: dict, r: int, prefix: str = "") -> dict:
    """The record fields of plan ``r`` of a majority-oracle judgement (``oracle_judgement``)."""
    return {f"{prefix}oracle_rule": "majority", f"{prefix}oracle_n_seeds": int(oj["margins"].shape[1]),
            f"{prefix}oracle_margin": float(oj["margin"][r]), f"{prefix}oracle_accept": bool(oj["accept"][r]),
            f"{prefix}oracle_share": float(oj["share"][r]),
            f"{prefix}oracle_margins_seeds": [float(x) for x in oj["margins"][r]],
            f"{prefix}oracle_accept_seeds": [bool(x) for x in oj["accept_seeds"][r]],
            f"{prefix}oracle_accept_seed0": bool(oj["accept_seed0"][r]),
            f"{prefix}oracle_margin_seed0": float(oj["margin_seed0"][r])}


def _summ(x: np.ndarray) -> dict:
    x = np.asarray(x, dtype=np.float64)
    med = float(np.median(x))
    return {"mean": float(x.mean()), "sd": float(x.std()), "median": med, "mad": float(np.median(np.abs(x - med))),
            "min": float(x.min()), "max": float(x.max())}


def _delta(a: dict, b: dict) -> dict:
    return {k: b[k] - a[k] for k in b}


# ----------------------------------------------------------------------------------------------
# Card inputs
# ----------------------------------------------------------------------------------------------
CARD_COLUMNS = ("instance", "cluster", "attacker", "scoring", "budget", "attacker_seed", "plan_id", "grader_p",
                "oracle_accept", "n_scored", "grader_score", "oracle_margin")


def card_tables(records: Sequence[dict], p1: Dict[str, dict], instances: Sequence[Instance], floors,
                n_beh: Optional[int] = None) -> Tuple[dict, dict]:
    """(records table, behaviour table) in the column form ``hpr_dream.build_card`` takes. ``oracle_accept`` is the
    records' oracle verdict: the primary seed's, or the majority oracle's. Under the majority oracle the other
    seeds' verdicts are not passed (the card's "unlucky" share, a majority of other seeds overturning a one-seed
    rejection, has no meaning when the verdict already is the majority); the single-seed oracle and the pass shares
    are reported beside the card (``run_audit.oracle_majority_stats``)."""
    R = {k: [r[k] for r in records] for k in CARD_COLUMNS}
    if not any(r.get("oracle_rule") == "majority" for r in records):
        R["oracle_accept_seeds"] = np.array([r["oracle_accept_seeds"] for r in records], dtype=bool)
    elif not all(r.get("oracle_rule") == "majority" for r in records):
        raise ValueError("records mix oracle rules")
    for k in floors:      # None where the floor is not run for the record's group (the flip floor's scope)
        R[f"{k}_grader_accept"] = [r.get(f"{k}_grader_accept") for r in records]
        R[f"{k}_oracle_accept"] = [r.get(f"{k}_oracle_accept") for r in records]
    R["n_floor_oracle_evals"] = [r["n_floor_oracle_evals"] for r in records]
    keys = {r["instance"] for r in records}
    beh = {"instance": [], "cluster": [], "grader_p": [], "oracle_accept": []}
    for inst in instances:
        if inst.key not in keys:
            continue
        b = p1[inst.key]["behaviour"]
        n = len(b["grader_p"]) if n_beh is None else min(int(n_beh), len(b["grader_p"]))
        beh["instance"] += [inst.key] * n
        beh["cluster"] += [inst.family_id] * n
        beh["grader_p"] += [float(x) for x in b["grader_p"][:n]]
        beh["oracle_accept"] += [bool(x >= 0) for x in b["oracle_margin"][:n]]
    return R, beh


def write_records(records: Sequence[dict], path) -> None:
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    os.replace(tmp, path)


def read_records(path) -> List[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="replay server for a remote engine pool (dc.audit.RemotePool)")
    ap.add_argument("cmd", choices=["serve"])
    ap.add_argument("--workers", type=int, default=22)
    a = ap.parse_args()
    serve(a.workers)
