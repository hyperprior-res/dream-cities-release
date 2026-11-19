"""The ensemble judge and the defence frontier .

For each defence setting: how often the defended emulator is fooled (hackability under the 32-seed majority oracle)
against how often it rejects a selected plan the oracle accepts (false rejection), on 60 instances (twelve per task
family, ``dc.audit.select_instances(all, 60)``), under random search over the behaviour pool and the pool-seeded
search ``cem_seeded``, both at B = 1,000. Every setting below is fixed by the brief; nothing here is tuned.

Judges.
- *Member 0* is the main checkpoint (``dc.audit.EmulatorJudge``, the audit's own settings).
- *Ensemble judge* (``EnsembleJudge``): the three one-step 50M full-data finals. A call with K samples per member draws
  K from each member, each member on its own random stream: member 0 on the call's stream, member m >= 1 on the
  stream extended by ("member", m) (``member_stream``), so an ensemble of one member is the single-model judge exactly
  and an ensemble of three copies of one model is the single-model judge at 3K samples in distribution. Samples come
  back as (n, M K, H+1, 20), member m in columns [m K, (m+1) K). K = 2 per member while searching, 8 per member for a
  verdict. Search score = mean margin over all samples; verdict = pass share over all samples >= 1/2; disagreement of
  a plan = the standard deviation (ddof 1) across members of each member's mean margin (``summarise``).
- *Tempered member 0* (``TemperedJudge``): every sampled head at temperature T, the model's own
  ``rollout(temperature=T)`` (z ~ N(0, T^2 I); gate, categorical and Bernoulli logits divided by T; logistic scales
  multiplied by T). At T = 1 it is member 0 itself.

Defences (``SETTINGS``; score = what the search maximises, verdict = what accepts the selected plan; the defence is
part of both):
- temperature T in {0.75, 1.25, 1.5} (member 0): the tempered judge, undefended score and verdict;
- disagreement penalty lambda in {1, 2} (ensemble): score = mean margin - lambda * disagreement; accepted when that is
  >= 0 and the pass share is >= 1/2;
- halt (ensemble): a plan whose disagreement exceeds the instance's threshold is rejected and scores -inf in search;
  thresholds = the 95th and 80th percentiles (numpy's linear rule) of the disagreement of the instance's 1,000
  behaviour plans under their search samples (K = 2 per member);
- detector (ensemble): logistic regression (``fit_logistic``) for "accepted by the undefended ensemble and rejected by
  the oracle" from five features of the plan's ensemble rollout (``FEATURES``), fitted on the first
  ``DETECTOR_PLANS`` behaviour plans of the instances of half of the 40 held-out families and applied to the
  instances of the other half (two folds: families sorted by id, alternate), both ways; a plan is rejected (and scores
  -inf in search) when the predicted probability exceeds 0.5 or 0.2. Two fits per fold of the same model: one on the
  features of the search samples (applied while searching), one on the features of the verdict samples (applied to
  the verdict);
- deflation (post hoc, member 0 and ensemble): Smith and Winkler's Bayesian adjustment (``deflation_prior``,
  ``deflate``) of the selected plan's verdict pass share towards the instance's behaviour-pool acceptance rate,
  accepted when the adjusted share is >= 1/2.
Neutral settings are the identity (tests): T = 1; halt threshold +inf; detector threshold >= 1; deflation alpha = 1.
The penalty at lambda = 0 has the undefended search score, and its verdict adds "mean margin >= 0" to the undefended
verdict (as the brief writes the rule); it is reported as ``penalty0``, derived from the undefended ensemble's
selections.

Seeds and streams (common random numbers across settings): proposals ("prop", share key, 0), the audit's own stream;
seeded search generation g ("cem_seeded", task, B, 0, g), the audit's; its random generator
``seed_for("audit-cem-seeded", instance, B, 0)``, the audit's; detector training verdicts ("def-detector", share key,
0); selected plans' verdicts ("def-verdict", share key, tag of the set of plans sampled in that call), stored per plan
so a plan selected under several settings has one verdict per member. Every judge call is stored on disk
(``SampleStore``) keyed by the judge's description, the plans and the stream, so identical calls of different settings
are computed once and a killed run resumes.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import audit as A
from . import tasks as T
from .engine import NUM_SCALARS, SC_POP, SC_POWERED, SC_TAX_FUND, SC_UNPOWERED
from .grammar import N_COLS, PLAN_COLUMNS, action_scalars_batch, clip_plan, raster_batch
from .seeds import seed_for

hd = A.hd

# ----------------------------------------------------------------------------------------------
# The fixed design 
# ----------------------------------------------------------------------------------------------
N_INSTANCES = 60
BUDGET = 1000
SEARCHES = ("random", "cem_seeded")
K_SEARCH = A.K_SEARCH            # per member while searching
K_VERDICT = A.K_VERDICT          # per member for a verdict
ACCEPT_P = A.ACCEPT_P
TEMPERATURES = (0.75, 1.25, 1.5)
LAMBDAS = (1.0, 2.0)
HALT_PERCENTILES = (95.0, 80.0)
DETECTOR_THRESHOLDS = (0.5, 0.2)
DETECTOR_PLANS = 125             # the behaviour plans per instance whose oracle verdicts the engine reference holds
DDOF = 1                         # standard deviation across members
FEATURES = ("mean_margin", "pass_share", "disagreement", "monthly_spread", "macro_share")
MONTH_COLS = (SC_POP, SC_TAX_FUND, SC_POWERED, SC_UNPOWERED)   # every task's statistic reads only these
KIND_COLS = tuple(j for j, (name, _, _) in enumerate(PLAN_COLUMNS) if name.endswith("_kind"))
MEMBER_STREAMS = "member 0: the call's stream; member m >= 1: the stream extended by ('member', m)"
CHECKPOINTS = tuple(f"<cache>/ckpt/ladder_v2/{r}/samples_006000000.pt"
                    for r in ("os_50m_full", "os_50m_full_s1", "os_50m_full_s2"))
DEFENCES_VERSION = 1


@dataclass(frozen=True)
class Setting:
    name: str
    judge: str                   # "member0" or "ensemble"
    defence: str                 # "none", "temperature", "penalty", "halt", "detector", "deflation"
    param: float = 0.0           # temperature, lambda, percentile or probability threshold
    derived_from: str = ""       # post hoc settings: the setting whose selected plans they re-judge
    neutral: bool = False        # a defence's neutral point, reported beside the design's settings

    @property
    def temperature(self) -> float:
        return self.param if self.defence == "temperature" else 1.0


SETTINGS: Tuple[Setting, ...] = (
    Setting("member0", "member0", "none"),
    *(Setting(f"temp{t:g}", "member0", "temperature", t) for t in TEMPERATURES),
    Setting("ensemble", "ensemble", "none"),
    *(Setting(f"penalty{l:g}", "ensemble", "penalty", l) for l in LAMBDAS),
    *(Setting(f"halt{q:g}", "ensemble", "halt", q) for q in HALT_PERCENTILES),
    *(Setting(f"detector{c:g}", "ensemble", "detector", c) for c in DETECTOR_THRESHOLDS),
    Setting("deflation-member0", "member0", "deflation", derived_from="member0"),
    Setting("deflation-ensemble", "ensemble", "deflation", derived_from="ensemble"),
    Setting("penalty0", "ensemble", "penalty", 0.0, derived_from="ensemble", neutral=True),
)
SETTING_BY_NAME = {s.name: s for s in SETTINGS}


def member_stream(stream: Sequence, m: int) -> tuple:
    return tuple(stream) if m == 0 else tuple(stream) + ("member", int(m))


def _digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------
# Judges
# ----------------------------------------------------------------------------------------------
class EnsembleJudge(A.SamplingJudge):
    """Equal numbers of samples from each member, each member on its own stream (module docstring)."""

    name = "ensemble"

    def __init__(self, members: Sequence[A.SamplingJudge]) -> None:
        super().__init__()
        if not members:
            raise ValueError("an ensemble needs at least one member")
        self.members = list(members)

    @property
    def task_independent(self) -> bool:      # type: ignore[override]
        return all(m.task_independent for m in self.members)

    @property
    def M(self) -> int:
        return len(self.members)

    def describe(self) -> dict:
        return {"judge": self.name, "members": [m.describe() for m in self.members], "member_streams": MEMBER_STREAMS}

    def samples(self, inst, eff_plans, K: int, stream: tuple) -> np.ndarray:
        t0 = time.time()
        P = np.ascontiguousarray(eff_plans, dtype=np.int16)
        out = np.concatenate([m.samples(inst, P, int(K), member_stream(stream, j)) for j, m in enumerate(self.members)],
                             axis=1)
        n, H = P.shape[0], P.shape[1]
        if out.shape != (n, self.M * int(K), H + 1, NUM_SCALARS):
            raise ValueError(f"ensemble samples of shape {out.shape}")
        self.month_steps += n * self.M * int(K) * H
        self.n_calls += 1
        self.seconds += time.time() - t0
        return out

    def counters(self) -> dict:
        d = super().counters()
        d["members"] = [m.counters() for m in self.members]
        return d


def tempered_rollout(model, state0: dict, plans: np.ndarray, K: int, device, max_batch: int,
                     temperature: float) -> np.ndarray:
    """``dc.audit.emulator_rollout`` with ``model.rollout(..., temperature=T)``: the same inputs (raster built on the
    card when on a GPU, as the audit does), the same call, one argument more. -> (B, K, H+1, 20) float64."""
    import torch
    B, H = plans.shape[0], plans.shape[1]
    act = torch.from_numpy(action_scalars_batch(plans.reshape(-1, N_COLS)).reshape(B, H, -1)).to(device)
    on_card = torch.device(device).type == "cuda"
    P = np.ascontiguousarray(plans)

    def raster(h):
        if on_card:
            from . import fast
            return fast.raster_rows(P[:, h], device)
        return torch.from_numpy(raster_batch(plans[:, h])).to(device, non_blocking=True)

    s0 = {k: v.expand(B, *v.shape[1:]) for k, v in state0.items()}
    traj, _ = model.rollout(s0, raster, act, K=K, max_batch=max_batch, temperature=float(temperature))
    return traj.double().cpu().numpy()


class TemperedJudge(A.SamplingJudge):
    """An ``EmulatorJudge``'s model with every sampled head at temperature T (Ha and Schmidhuber's knob), the base
    judge's chunks, buckets, start states and stream seeding. At T = 1 it calls the base judge (identical samples and
    description); ``force_tempered_path`` runs the tempered code at any T (a test of that path at T = 1)."""

    name = "emulator"

    def __init__(self, base, temperature: float, force_tempered_path: bool = False) -> None:
        super().__init__()
        if not float(temperature) > 0:
            raise ValueError("temperature must be positive")
        self.base = base
        self.temperature = float(temperature)
        self.force = bool(force_tempered_path)

    @property
    def task_independent(self) -> bool:      # type: ignore[override]
        return self.base.task_independent

    def describe(self) -> dict:
        d = dict(self.base.describe())
        if self.temperature != 1.0:
            d["temperature"] = self.temperature
        return d

    def _samples(self, inst, P, K, stream):
        if self.temperature == 1.0 and not self.force:
            return self.base._samples(inst, P, K, stream)
        b = self.base
        if b.chunk % K or any(x % K for x in b.buckets):
            raise ValueError(f"chunk {b.chunk} and buckets {b.buckets} must be multiples of K = {K}")
        b.torch.manual_seed(seed_for("audit-emu", inst.start_id, *stream))
        s0 = b.state0(inst)
        n, H = P.shape[0], P.shape[1]
        G = b.chunk // K
        out = np.empty((n, K, H + 1, NUM_SCALARS), dtype=np.float64)
        for a in range(0, n, G):
            sub = P[a:a + G]
            g = sub.shape[0]
            rows = next(x for x in b.buckets if x >= g * K)
            gp = rows // K
            if gp > g:
                sub = np.concatenate([sub, np.repeat(sub[-1:], gp - g, axis=0)])
                self.padded_month_steps += (gp - g) * K * H
            out[a:a + g] = tempered_rollout(b.model, s0, sub, K, b.device, rows, self.temperature)[:g]
        return out


# ----------------------------------------------------------------------------------------------
# Features of a rollout
# ----------------------------------------------------------------------------------------------
def monthly_statistic(task: str, month: np.ndarray) -> np.ndarray:
    """The task's statistic (``dc.tasks.statistic``) at every month 1..H from the stored columns ``MONTH_COLS``:
    (..., H+1, len(MONTH_COLS)) -> (..., H). Month h is ``statistic`` of the trajectory's prefix up to row h."""
    mo = np.asarray(month, dtype=np.float64)
    pseudo = np.full(mo.shape[:-1] + (NUM_SCALARS,), np.nan)
    for j, c in enumerate(MONTH_COLS):
        pseudo[..., c] = mo[..., j]
    H = mo.shape[-2] - 1
    out = np.stack([T.statistic(task, pseudo[..., :h + 1, :]) for h in range(1, H + 1)], axis=-1)
    if not np.isfinite(out).all():
        raise ValueError(f"the statistic of {task} reads a column outside MONTH_COLS")
    return out


def macro_share(eff: np.ndarray) -> np.ndarray:
    """Share of the plan's months with at least one macro that is not NOOP: (n, H, 25) -> (n,)."""
    k = np.asarray(eff)[..., list(KIND_COLS)]
    return (k != 0).any(axis=-1).mean(axis=-1).astype(np.float64)


def summarise(inst, stats: np.ndarray, month: np.ndarray, eff: np.ndarray) -> Dict[str, np.ndarray]:
    """A judge's samples of n plans -> per-plan quantities. ``stats`` (n, M, K, len(STAT_FIELDS)), ``month``
    (n, M, K, H+1, len(MONTH_COLS)), ``eff`` (n, H, 25). Margins by ``dc.audit.stats_margin`` (the audit's one call
    into ``dc.tasks``). mean_margin and pass_share over all M K samples; disagreement = sd (ddof 1) across members of
    each member's mean margin (0 for one member); monthly_spread = mean over months 1..H of the sd (ddof 1) across
    members of each member's mean statistic at that month, divided by the instance's stat_sd (0 for one member);
    macro_share of the plan."""
    st = np.asarray(stats, dtype=np.float64)
    n, M, K = st.shape[:3]
    m = A.stats_margin(inst, st)                                   # (n, M, K)
    mm = m.mean(axis=2)
    if M > 1:
        dis = mm.std(axis=1, ddof=DDOF)
        sm = monthly_statistic(inst.task, month).mean(axis=2)      # (n, M, H)
        spread = sm.std(axis=1, ddof=DDOF).mean(axis=-1) / max(float(inst.stat_sd), 1e-9)
    else:
        dis = np.zeros(n)
        spread = np.zeros(n)
    return {"mean_margin": m.mean(axis=(1, 2)), "pass_share": (m >= 0).mean(axis=(1, 2)), "disagreement": dis,
            "monthly_spread": spread, "macro_share": macro_share(eff), "margins": m}


def feature_matrix(S: Dict[str, np.ndarray]) -> np.ndarray:
    return np.stack([np.asarray(S[f], dtype=np.float64) for f in FEATURES], axis=1)


def _take(S: Dict[str, np.ndarray], idx) -> Dict[str, np.ndarray]:
    return {k: np.asarray(v)[idx] for k, v in S.items()}


# ----------------------------------------------------------------------------------------------
# Detector: logistic regression by maximum likelihood
# ----------------------------------------------------------------------------------------------
@dataclass
class Logistic:
    """P(y = 1 | x) = sigmoid(w0 + sum_j w_j (x_j - mu_j) / sd_j)."""
    mu: np.ndarray
    sd: np.ndarray
    w: np.ndarray
    iterations: int
    converged: bool
    loglik: float
    n: int
    n_pos: int

    def prob(self, X) -> np.ndarray:
        Z = (np.asarray(X, dtype=np.float64) - self.mu) / self.sd
        eta = self.w[0] + Z @ self.w[1:]
        return 1.0 / (1.0 + np.exp(-eta))

    def as_dict(self) -> dict:
        return {"features": list(FEATURES), "mean": self.mu.tolist(), "sd": self.sd.tolist(), "coef": self.w.tolist(),
                "iterations": self.iterations, "converged": self.converged, "loglik": self.loglik, "n": self.n,
                "n_positive": self.n_pos}


def _loglik(Z, y, w) -> float:
    eta = Z @ w
    return float(np.sum(y * eta - np.logaddexp(0.0, eta)))


def fit_logistic(X, y, max_iter: int = 100, tol: float = 1e-8) -> Logistic:
    """Unpenalised maximum likelihood with an intercept, features standardised on the fitting data (sd ddof 0; a
    constant feature keeps sd 1), Newton-Raphson with step halving until the log-likelihood does not fall;
    converged when the largest step is below ``tol``. Refused when the data hold only one class."""
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=bool).astype(np.float64)
    if y.min() == y.max():
        raise ValueError("the detector's fitting data hold only one class")
    mu, sd = X.mean(axis=0), X.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    Z = np.column_stack([np.ones(len(X)), (X - mu) / sd])
    w = np.zeros(Z.shape[1])
    w[0] = math.log(y.mean() / (1 - y.mean()))
    ll = _loglik(Z, y, w)
    converged, it = False, 0
    for it in range(1, max_iter + 1):
        p = 1.0 / (1.0 + np.exp(-(Z @ w)))
        g = Z.T @ (y - p)
        Hm = (Z * (p * (1 - p))[:, None]).T @ Z
        step = np.linalg.lstsq(Hm, g, rcond=None)[0]
        t = 1.0
        while True:
            w_new = w + t * step
            ll_new = _loglik(Z, y, w_new)
            if ll_new >= ll - 1e-12 or t < 1e-10:
                break
            t *= 0.5
        w, ll = w_new, ll_new
        if np.max(np.abs(t * step)) < tol:
            converged = True
            break
    return Logistic(mu, sd, w, it, converged, ll, int(len(y)), int(y.sum()))


def family_folds(families: Sequence[str]) -> Dict[str, int]:
    """Two folds of the held-out families: sorted by id, alternate (index mod 2)."""
    return {f: k % 2 for k, f in enumerate(sorted(set(families)))}


# ----------------------------------------------------------------------------------------------
# Deflation (Smith and Winkler 2006, section 3.2, eqs. 6a-6b)
# ----------------------------------------------------------------------------------------------
def deflation_prior(oracle_share, oracle_accept, judge_pass) -> dict:
    """The instance's prior and the judge's error from its behaviour plans with oracle verdicts: mu_bar = the oracle's
    acceptance rate on them; var_mu = the variance (ddof 1) of their oracle pass shares (the prior variance of the true
    value); var_v = the mean squared difference between the judge's verdict pass share and the oracle pass share (the
    variance of the estimate given the true value, with any bias in it); alpha = 1 / (1 + var_v / var_mu) (0 when
    var_mu = 0: the prior is a point)."""
    q = np.asarray(oracle_share, dtype=np.float64)
    a = np.asarray(oracle_accept, dtype=bool)
    v = np.asarray(judge_pass, dtype=np.float64)
    mu_bar = float(a.mean())
    var_mu = float(q.var(ddof=1)) if q.size > 1 else 0.0
    var_v = float(np.mean((v - q) ** 2))
    alpha = var_mu / (var_mu + var_v) if var_mu > 0 else 0.0
    return {"mu_bar": mu_bar, "var_mu": var_mu, "var_v": var_v, "alpha": float(alpha), "n_plans": int(q.size)}


def deflate(p, mu_bar: float, alpha: float) -> np.ndarray:
    """Posterior mean alpha p + (1 - alpha) mu_bar (S&W eq. 6b) of the selected plan's pass share p."""
    return float(alpha) * np.asarray(p, dtype=np.float64) + (1.0 - float(alpha)) * float(mu_bar)


# ----------------------------------------------------------------------------------------------
# Scores and verdicts of a setting
# ----------------------------------------------------------------------------------------------
def defended_score(st: Setting, S: Dict[str, np.ndarray], ctx: dict) -> np.ndarray:
    """What the search maximises under setting ``st`` (search samples' summary ``S``; ``ctx``: the instance's halt
    thresholds and search detector)."""
    mean = np.asarray(S["mean_margin"], dtype=np.float64)
    if st.defence in ("none", "temperature", "deflation"):
        return mean.copy()
    if st.defence == "penalty":
        return mean - st.param * np.asarray(S["disagreement"])
    if st.defence == "halt":
        return np.where(np.asarray(S["disagreement"]) > ctx["halt"][st.param], -np.inf, mean)
    if st.defence == "detector":
        return np.where(ctx["detector_search"].prob(feature_matrix(S)) > st.param, -np.inf, mean)
    raise ValueError(st.defence)


def defended_verdict(st: Setting, S: Dict[str, np.ndarray], ctx: dict) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """(accept, extra fields) of plans' verdict samples' summary ``S`` under setting ``st``."""
    p = np.asarray(S["pass_share"], dtype=np.float64)
    base = p >= ACCEPT_P
    if st.defence in ("none", "temperature"):
        return base, {}
    if st.defence == "penalty":
        am = np.asarray(S["mean_margin"]) - st.param * np.asarray(S["disagreement"])
        return base & (am >= 0), {"acceptance_margin": am}
    if st.defence == "halt":
        thr = ctx["halt"][st.param]
        return base & ~(np.asarray(S["disagreement"]) > thr), {"halt_threshold": np.full(p.shape, thr)}
    if st.defence == "detector":
        q = ctx["detector_verdict"].prob(feature_matrix(S))
        return base & ~(q > st.param), {"detector_p": q}
    if st.defence == "deflation":
        d = ctx["deflation"][st.judge]
        s = deflate(p, d["mu_bar"], d["alpha"])
        return s >= ACCEPT_P, {"shrunk_share": s, "deflation_alpha": np.full(p.shape, d["alpha"]),
                               "deflation_mu_bar": np.full(p.shape, d["mu_bar"])}
    raise ValueError(st.defence)


# ----------------------------------------------------------------------------------------------
# Sample store
# ----------------------------------------------------------------------------------------------
class SampleStore:
    """Judge samples on disk as the audit's per-sample statistics (``STAT_FIELDS``) plus the columns ``MONTH_COLS`` at
    every month. ``call``: one judge call, keyed by (judge description, start, share key, purpose, stream, plans, K).
    ``plan_verdicts``: K_VERDICT samples per plan, kept per plan; missing plans are sampled in one call whose stream
    names their set. New samples are checked: the margins from the statistics equal those from the full trajectories,
    and every task's monthly statistic from the stored columns equals that of the full trajectories."""

    def __init__(self, root) -> None:
        self.root = Path(root)
        self._jd: Dict[int, str] = {}
        self._pv: Dict[Path, dict] = {}
        self.computed_month_steps = 0

    def jd(self, judge) -> str:
        k = id(judge)
        if k not in self._jd:
            self._jd[k] = _digest(judge.describe())
        return self._jd[k]

    @staticmethod
    def _check(inst, tr: np.ndarray, st: np.ndarray, mo: np.ndarray) -> None:
        if not np.array_equal(np.asarray(A.task_margin(inst, tr), dtype=np.float64), A.stats_margin(inst, st)):
            raise ValueError(f"{inst.key}: margins from the statistics differ from the trajectories'")
        tr1, mo1 = tr[:2], mo[:2]          # which columns a statistic reads does not depend on the values
        for task in T.TASKS:
            full = np.stack([T.statistic(task, tr1[..., :h + 1, :]) for h in range(1, tr1.shape[-2])], axis=-1)
            if not np.array_equal(full, monthly_statistic(task, mo1)):
                raise ValueError(f"{task}: the monthly statistic from MONTH_COLS differs from the trajectories'")

    def _sample(self, judge, inst, eff, K, stream):
        tr = judge.samples(inst, eff, K, stream)
        st = A.traj_stats(tr)
        mo = np.ascontiguousarray(tr[..., list(MONTH_COLS)])
        self._check(inst, tr, st, mo)
        self.computed_month_steps += int(eff.shape[0]) * int(K) * int(eff.shape[1])
        return st, mo

    def call(self, judge, inst, sk: str, purpose: str, eff: np.ndarray, K: int, stream: tuple):
        eff = np.ascontiguousarray(eff, dtype=np.int16)
        key = _digest([self.jd(judge), inst.start_id, sk, purpose, list(map(str, stream)), A.plan_hash(eff), int(K)])
        p = self.root / "calls" / inst.start_id / f"{purpose}__{key}.npz"
        if p.exists():
            with np.load(p) as z:
                if str(z["plan_hash"]) == A.plan_hash(eff) and str(z["judge"]) == self.jd(judge):
                    return z["stats"], z["month"]
        st, mo = self._sample(judge, inst, eff, K, stream)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.stem + f".tmp{os.getpid()}.npz")
        np.savez(tmp, stats=st, month=mo, plan_hash=A.plan_hash(eff), judge=self.jd(judge), stream=repr(stream))
        os.replace(tmp, p)
        return st, mo

    def plan_verdicts(self, judge, inst, sk: str, eff: np.ndarray, member: int = 0):
        """(n, K_VERDICT, F) statistics and (n, K_VERDICT, H+1, 4) columns of each plan's verdict samples."""
        eff = np.ascontiguousarray(eff, dtype=np.int16)
        p = self.root / "verdicts" / inst.start_id / f"{sk}__{self.jd(judge)}.npz"
        keys = [A.plan_hash(e) for e in eff]
        store = self._pv.get(p)
        if store is None or any(k not in store for k in keys):
            store = self._load_pv(p)
        miss = sorted({k for k in keys if k not in store})
        if miss:
            first = {k: i for i, k in reversed(list(enumerate(keys)))}
            idx = [first[k] for k in miss]
            tag = hashlib.sha256("".join(miss).encode()).hexdigest()[:16]
            st, mo = self._sample(judge, inst, eff[idx], K_VERDICT, member_stream(("def-verdict", sk, tag), member))
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(str(p) + ".lock", "w") as lk:
                fcntl.flock(lk, fcntl.LOCK_EX)
                store = self._load_pv(p)
                for k, s, m in zip(miss, st, mo):
                    store.setdefault(k, (s, m))
                ks = sorted(store)
                tmp = p.with_name(p.stem + f".tmp{os.getpid()}.npz")
                np.savez(tmp, keys=np.array(ks), stats=np.stack([store[k][0] for k in ks]),
                         month=np.stack([store[k][1] for k in ks]), judge=self.jd(judge))
                os.replace(tmp, p)
            self._pv[p] = store
        return np.stack([store[k][0] for k in keys]), np.stack([store[k][1] for k in keys])

    def _load_pv(self, p: Path) -> dict:
        store = {}
        if p.exists():
            with np.load(p) as z:
                store = {str(k): (s, m) for k, s, m in zip(z["keys"], z["stats"], z["month"])}
        self._pv[p] = store
        return store


# ----------------------------------------------------------------------------------------------
# The frontier
# ----------------------------------------------------------------------------------------------
def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return [_jsonable(v) for v in x.tolist()]
    if isinstance(x, (float, np.floating)):
        return float(x) if np.isfinite(x) else None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


class Frontier:
    """Runs the defence settings on ``instances``: preparation per instance (``prepare``), the detectors
    (``detectors``), the searches and verdicts per instance (``run_instance``), records per (search, setting,
    instance) under ``<work>/records``."""

    def __init__(self, instances, members: Sequence[A.SamplingJudge], engine, pools, work, oracle_n: int,
                 universe=None, budget: int = BUDGET, temperatures=TEMPERATURES, log: Callable[[str], None] = print,
                 detector_plans: int = DETECTOR_PLANS) -> None:
        self.instances = list(instances)
        self.universe = list(universe) if universe is not None else self.instances
        self.members = list(members)
        if len(self.members) != 3:
            raise ValueError("the ensemble of the design has three members")
        self.ens = EnsembleJudge(self.members)
        self.m0 = self.members[0]
        self.tempered = {1.0: self.m0, **{float(t): TemperedJudge(self.m0, t) for t in temperatures if t != 1.0}}
        self.engine, self.pools = engine, pools
        self.work = Path(work)
        self.oracle_n = int(oracle_n)
        self.budget = int(budget)
        self.log = log
        self.H = self.instances[0].horizon
        self.space = A.plan_space(self.H)
        self.store = SampleStore(self.work / "samples")
        self.folds = family_folds([i.family_id for i in self.universe])
        self.detector_plans = int(detector_plans)
        self._det = None
        self.tag = {"defences_version": DEFENCES_VERSION, "ensemble": self.ens.describe(),
                    "tempered": {str(t): j.describe() for t, j in self.tempered.items()}, "budget": self.budget,
                    "oracle_n": self.oracle_n, "detector_plans": self.detector_plans}
        self.tag_digest = _digest(self.tag)

    # -- judges and samples ------------------------------------------------------------------
    def sk(self, inst) -> str:
        return inst.forced_key if self.ens.task_independent else inst.task

    def kind_members(self, st: Setting) -> List[A.SamplingJudge]:
        return self.members if st.judge == "ensemble" else [self.tempered[st.temperature]]

    def rollouts(self, st: Setting, inst, purpose: str, eff: np.ndarray, K: int, stream: tuple):
        """Stats (n, M, K, F) and month columns (n, M, K, H+1, 4) of the setting's judge, member m on
        ``member_stream(stream, m)``."""
        out = [self.store.call(j, inst, self.sk(inst), purpose, eff, K, member_stream(stream, m))
               for m, j in enumerate(self.kind_members(st))]
        return np.stack([o[0] for o in out], axis=1), np.stack([o[1] for o in out], axis=1)

    def verdict_samples(self, st: Setting, inst, eff: np.ndarray):
        out = [self.store.plan_verdicts(j, inst, self.sk(inst), eff, member=m)
               for m, j in enumerate(self.kind_members(st))]
        return np.stack([o[0] for o in out], axis=1), np.stack([o[1] for o in out], axis=1)

    def oracle(self, inst, raw_plans) -> dict:
        tr = A.oracle_trajectories(self.engine, inst, raw_plans, self.oracle_n)
        return A.oracle_judgement(inst, tr)

    def behaviour(self, inst):
        beh = self.pools.behaviour(inst.start_id)
        if beh.shape[0] < self.budget:
            raise ValueError(f"{inst.start_id}: {beh.shape[0]} behaviour plans, {self.budget} needed")
        return beh, beh.reshape(beh.shape[0], -1).astype(np.int64)

    # -- paths -----------------------------------------------------------------------------------
    def _prep_path(self, inst) -> Path:
        return self.work / "prep" / f"{inst.file_stem}.pkl"

    def _rec_path(self, search: str, setting: str, inst) -> Path:
        return self.work / "records" / search / setting / f"{inst.file_stem}.json"

    def record(self, search: str, setting: str, inst) -> Optional[dict]:
        p = self._rec_path(search, setting, inst)
        if not p.exists():
            return None
        r = json.loads(p.read_text())
        return r if r.get("tag") == self.tag_digest else None

    # -- stage 1: per-instance preparation ----------------------------------------------------------
    def prepare(self, inst) -> dict:
        p = self._prep_path(inst)
        if p.exists():
            d = A._load_pickle(p)
            if d.get("tag") == self.tag_digest:
                return d
        t0 = time.time()
        ms0 = self.store.computed_month_steps
        H, sk, B, nd = self.H, self.sk(inst), self.budget, self.detector_plans
        beh, flat = self.behaviour(inst)
        eff = A.effective(beh[:B], inst.task, H)
        stream = ("prop", sk, 0)
        prop = {}
        ens = SETTING_BY_NAME["ensemble"]
        s, m = self.rollouts(ens, inst, "prop", eff, K_SEARCH, stream)
        prop["ensemble"] = _drop_margins(summarise(inst, s, m, eff))
        prop["member0"] = _drop_margins(summarise(inst, s[:, :1], m[:, :1], eff))     # member 0's block: T = 1
        for t, j in self.tempered.items():
            if t == 1.0:
                continue
            st = Setting(f"temp{t:g}", "member0", "temperature", t)
            s1, m1 = self.rollouts(st, inst, "prop", eff, K_SEARCH, stream)
            prop[f"temp{t:g}"] = _drop_margins(summarise(inst, s1, m1, eff))
        # detector training plans: the first nd behaviour plans, verdict samples of every member, oracle verdicts
        dv_s, dv_m = self.rollouts(ens, inst, "def-detector", eff[:nd], K_VERDICT, ("def-detector", sk, 0))
        dv = summarise(inst, dv_s, dv_m, eff[:nd])
        dv0 = summarise(inst, dv_s[:, :1], dv_m[:, :1], eff[:nd])
        oj = self.oracle(inst, beh[:nd])
        label = (dv["pass_share"] >= ACCEPT_P) & ~oj["accept"]
        halt = {q: float(np.percentile(prop["ensemble"]["disagreement"], q)) for q in HALT_PERCENTILES}
        defl = {"ensemble": deflation_prior(oj["share"], oj["accept"], dv["pass_share"]),
                "member0": deflation_prior(oj["share"], oj["accept"], dv0["pass_share"])}
        d = {"tag": self.tag_digest, "instance": asdict(inst), "fold": self.folds[inst.family_id], "prop": prop,
             "det_search_X": feature_matrix(prop["ensemble"])[:nd], "det_verdict_X": feature_matrix(dv),
             "det_label": label, "det_oracle_share": oj["share"], "det_oracle_accept": oj["accept"],
             "det_pass_ensemble": dv["pass_share"], "det_pass_member0": dv0["pass_share"],
             "halt": halt, "deflation": defl,
             "costs": {"seconds": time.time() - t0, "month_steps_computed": self.store.computed_month_steps - ms0}}
        A._atomic_pickle(d, p)
        self.log(f"  prep {inst.key}: {d['costs']['month_steps_computed']:,} month-steps computed, "
                 f"{d['costs']['seconds']:.0f} s; halt thresholds {halt}; detector positives {int(label.sum())}/{nd}")
        return d

    # -- stage 2: detectors -------------------------------------------------------------------------
    def detectors(self) -> dict:
        """Per fold f: the search-feature and verdict-feature detectors fitted on the preparation of the instances
        whose family is in fold f (applied to the other fold), and their AUC on the other fold's plans."""
        if self._det is not None:
            return self._det
        p = self.work / "detectors.pkl"
        if p.exists():
            d = A._load_pickle(p)
            if d.get("tag") == self.tag_digest:
                self._det = d
                return d
        preps = [self.prepare(i) for i in self.instances]
        out = {"folds": {}, "fold_of_family": self.folds}
        for f in (0, 1):
            tr = [d for d in preps if d["fold"] == f]
            te = [d for d in preps if d["fold"] != f]
            fold = {"fit_instances": len(tr), "test_instances": len(te)}
            for kind in ("search", "verdict"):
                X = np.concatenate([d[f"det_{kind}_X"] for d in tr])
                y = np.concatenate([d["det_label"] for d in tr])
                model = fit_logistic(X, y)
                Xt = np.concatenate([d[f"det_{kind}_X"] for d in te])
                yt = np.concatenate([d["det_label"] for d in te])
                cl = np.concatenate([[d["instance"]["family_id"]] * len(d["det_label"]) for d in te])
                auc = (hd.auc(model.prob(Xt), yt, cl, bca=True).as_dict() if 0 < yt.sum() < yt.size
                       else {"value": None, "status": "one class in the test fold"})
                fold[kind] = {"model": model, "auc_other_fold": auc, "n_test": int(yt.size), "n_test_positive": int(yt.sum())}
            out["folds"][f] = fold
        out["tag"] = self.tag_digest
        A._atomic_pickle(out, p)
        self._det = out
        return out

    def context(self, inst, prep: dict, need_detector: bool) -> dict:
        ctx = {"halt": prep["halt"], "deflation": prep["deflation"]}
        if need_detector:
            other = 1 - prep["fold"]
            det = self.detectors()["folds"][other]
            ctx["detector_search"] = det["search"]["model"]
            ctx["detector_verdict"] = det["verdict"]["model"]
            ctx["detector_fold"] = other
        return ctx

    # -- stage 3: searches, verdicts, oracle ----------------------------------------------------------
    def _search(self, st: Setting, search: str, inst, prep: dict, ctx: dict, flat: np.ndarray):
        B, H = self.budget, self.H
        Sp = prep["prop"][st.name if st.defence == "temperature" else st.judge]
        scores = defended_score(st, Sp, ctx)
        if search == "random":
            sel = hd.random_shooting(A._Lookup(flat, scores), flat[:B], B)
        elif search == "cem_seeded":
            calls = [0]
            look = A._Lookup(flat, scores)

            def score(X):
                calls[0] += 1
                if calls[0] == 1:          # generation 0: the first N proposals, scored from their search samples
                    return look(X)
                eff = A.effective(X, inst.task, H)
                s, m = self.rollouts(st, inst, "cem_seeded", eff, K_SEARCH, ("cem_seeded", inst.task, B, 0, calls[0] - 1))
                return defended_score(st, summarise(inst, s, m, eff), ctx)

            init = hd.fit_marginals(self.space, flat)
            sel = hd.cem_seeded(score, self.space, B, np.random.default_rng(seed_for("audit-cem-seeded", inst.key, B, 0)),
                                flat[:B], init, block=N_COLS, repair=self._repair)
        else:
            raise ValueError(search)
        if int(sel.log["n_scored"]) != B:
            raise hd.BudgetError(f"{inst.key} {search} {st.name}: scored {sel.log['n_scored']}")
        return sel

    def _repair(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X)
        return clip_plan(X.reshape(X.shape[0], self.H, N_COLS)).reshape(X.shape[0], -1).astype(np.int64)

    def run_instance(self, inst, settings: Sequence[Setting], searches: Sequence[str]) -> List[dict]:
        """Every (search, setting) of the instance whose record is missing: searches, then the selected plans'
        verdicts (batched per judge), the oracle, the derived settings; records written per (search, setting)."""
        H = self.H
        prep = self.prepare(inst)
        need_det = any(s.defence == "detector" for s in settings)
        ctx = self.context(inst, prep, need_det)
        beh, flat = self.behaviour(inst)
        def src_of(s: Setting) -> Setting:
            return SETTING_BY_NAME[s.derived_from] if s.derived_from else s

        all_settings = list(settings) + [src_of(s) for s in settings if s.derived_from and src_of(s) not in settings]
        todo = [(se, s) for se in searches for s in all_settings if self.record(se, s.name, inst) is None]
        if not todo:
            return []
        need: List[Tuple[str, Setting]] = []
        for se, s in todo:
            if (se, src_of(s)) not in need:
                need.append((se, src_of(s)))
        ms0 = self.store.computed_month_steps
        t0 = time.time()
        sels = {}
        for se, s in need:
            ts = time.time()
            m0 = self.store.computed_month_steps
            sel = self._search(s, se, inst, prep, ctx, flat)
            raw = np.asarray(sel.plan, dtype=np.int64).reshape(H, N_COLS)
            old = self.record(se, s.name, inst)
            if old is not None and old["plan_hash"] != A.plan_hash(A.effective(raw[None], inst.task, H)[0]):
                raise RuntimeError(f"{inst.key} {se} {s.name}: the search re-run selected another plan than its record")
            sels[(se, s.name)] = (sel, raw, self.store.computed_month_steps - m0, time.time() - ts)
        # verdicts, batched per judge
        verd = {}
        for jkey in sorted({(s.judge, s.temperature) for _, s in need}):
            pairs = [(se, s) for se, s in need if (s.judge, s.temperature) == jkey]
            effs = A.effective(np.stack([sels[(se, s.name)][1] for se, s in pairs]), inst.task, H)
            vs, vm = self.verdict_samples(pairs[0][1], inst, effs)
            for k, (se, s) in enumerate(pairs):
                verd[(se, s.name)] = (vs[k:k + 1], vm[k:k + 1], effs[k:k + 1])
        # the oracle, one call for every selected plan
        keys = list(sels)
        oj = self.oracle(inst, np.stack([sels[k][1] for k in keys]))
        orow = {k: r for r, k in enumerate(keys)}
        out = []
        for se, s in todo:
            src = src_of(s)
            sel, raw, ms_new, sec = sels[(se, src.name)]
            vs, vm, eff = verd[(se, src.name)]
            S = summarise(inst, vs, vm, eff)
            acc, extra = defended_verdict(s, S, ctx)
            if s.derived_from:      # a post hoc setting re-judges the source's selection; its search score is the source's
                if s.defence == "penalty":
                    Sp = prep["prop"][src.judge]
                    if not np.array_equal(defended_score(s, Sp, ctx), defended_score(src, Sp, ctx)):
                        raise RuntimeError("penalty0's search score differs from the undefended ensemble's")
            r = orow[(se, src.name)]
            M = len(self.kind_members(src))
            bs = float(sel.log["best_score"])
            rec = {"tag": self.tag_digest, "instance": inst.key, "cluster": inst.family_id, "start_id": inst.start_id,
                   "task": inst.task, "in_band": inst.in_band, "setting": s.name, "judge": s.judge,
                   "defence": s.defence, "param": s.param, "derived_from": s.derived_from, "neutral": s.neutral,
                   "search": se, "budget": int(sel.log["n_scored"]), "members": M,
                   "plan_hash": A.plan_hash(eff[0]), "best_index": int(sel.log["best_index"]),
                   "best_score": bs if np.isfinite(bs) else None, "best_score_is_minus_inf": bool(bs == -np.inf),
                   "grader_p": float(S["pass_share"][0]), "grader_mean_margin": float(S["mean_margin"][0]),
                   "grader_disagreement": float(S["disagreement"][0]), "grader_monthly_spread": float(S["monthly_spread"][0]),
                   "plan_macro_share": float(S["macro_share"][0]),
                   "grader_accept_undefended": bool(S["pass_share"][0] >= ACCEPT_P), "grader_accept": bool(acc[0]),
                   **{k: float(np.asarray(v)[0]) for k, v in extra.items()},
                   **A._oracle_fields(oj, r),
                   "emu_month_steps_search": int(sel.log["n_scored"]) * K_SEARCH * M * H,
                   "emu_month_steps_verdict": K_VERDICT * M * H,
                   "emu_month_steps_search_computed": int(ms_new) if not s.derived_from else 0,
                   "search_seconds": sec if not s.derived_from else 0.0,
                   "fold_of_detector": ctx.get("detector_fold") if s.defence == "detector" else None}
            if se == "cem_seeded":
                rec["best_per_generation"] = [float(x) if np.isfinite(x) else None for x in sel.log["best_per_generation"]]
            p = self._rec_path(se, s.name, inst)
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_name(p.name + f".tmp{os.getpid()}")
            tmp.write_text(json.dumps(_jsonable(rec), sort_keys=True))
            os.replace(tmp, p)
            out.append(rec)
        self.log(f"  {inst.key}: {len(todo)} records; {self.store.computed_month_steps - ms0:,} month-steps computed, "
                 f"{time.time() - t0:.0f} s")
        return out

    def records(self, searches=SEARCHES, settings=SETTINGS) -> List[dict]:
        out = []
        for se in searches:
            for s in settings:
                for i in self.instances:
                    r = self.record(se, s.name, i)
                    if r is not None:
                        out.append(r)
        return out


def _drop_margins(S: dict) -> dict:
    return {k: v for k, v in S.items() if k != "margins"}


# ----------------------------------------------------------------------------------------------
# Statistics of the frontier
# ----------------------------------------------------------------------------------------------
def arm_stats(ga, oa, share, cl, n_boot: int = 2000, seed: int = 0) -> dict:
    """One arm on its units: hackability, judge and oracle acceptance, the oracle's mean pass share of the selected
    plans, P(oracle rejects | judge accepts), false rejection = P(judge rejects | oracle accepts); cluster bootstrap
    over families, BCa (``hpr_dream.stats``)."""
    ga, oa = np.asarray(ga, dtype=bool), np.asarray(oa, dtype=bool)
    cl = np.asarray(cl)
    kw = dict(n_boot=n_boot, seed=seed, bca=True)
    out = {"n": int(ga.size), "n_clusters": int(len(set(cl.tolist()))),
           "hackability": hd.hackability(ga, oa, cl, **kw).as_dict(),
           "judge_accept": hd.conditional_mean(ga, None, cl, **kw).as_dict(),
           "oracle_accept": hd.conditional_mean(oa, None, cl, **kw).as_dict(),
           "oracle_share": hd.conditional_mean(np.asarray(share, dtype=np.float64), None, cl, **kw).as_dict(),
           "n_judge_accept": int(ga.sum()), "n_oracle_accept": int(oa.sum()), "n_hacked": int((ga & ~oa).sum()),
           "n_false_rejections": int((~ga & oa).sum())}
    out["oracle_reject_given_judge_accept"] = (hd.conditional_reject(ga, oa, cl, **kw).as_dict() if ga.any() else
                                               {"value": None, "status": "the judge accepted no selected plan"})
    out["false_rejection"] = (hd.false_rejection(ga[oa], cl[oa], **kw).as_dict() if oa.any() else
                              {"value": None, "status": "the oracle accepted no selected plan"})
    return out


def design_cost(instances, sk_of: Callable, budget: int = BUDGET, H: int = 24, n_ens_cem: int = 7,
                n_m0_cem: int = 4, temperatures=TEMPERATURES, detector_plans: int = DETECTOR_PLANS) -> dict:
    """Emulator month-steps of the whole frontier as designed (before any sharing between settings' seeded searches
    and before verdicts): proposals and detector verdicts once per (start, share key); seeded search per instance and
    setting (generations after the first; the first reuses the proposals' samples)."""
    groups = sorted({(i.start_id, sk_of(i)) for i in instances})
    G, N = hd.cem_schedule(budget)
    new = budget - N
    c = {"start_share_groups": len(groups), "instances": len(instances),
         "proposals_ensemble": len(groups) * budget * 3 * K_SEARCH * H,
         "proposals_tempered": len(groups) * len(temperatures) * budget * K_SEARCH * H,
         "detector_verdicts": len(groups) * detector_plans * 3 * K_VERDICT * H,
         "cem_seeded_ensemble": len(instances) * n_ens_cem * new * 3 * K_SEARCH * H,
         "cem_seeded_member0": len(instances) * n_m0_cem * new * K_SEARCH * H,
         "verdicts_upper_bound": len(instances) * 2 * (n_ens_cem * 3 + n_m0_cem) * K_VERDICT * H}
    c["total"] = int(sum(v for k, v in c.items() if k not in ("start_share_groups", "instances")))
    return c


# ----------------------------------------------------------------------------------------------
# The frontier table
# ----------------------------------------------------------------------------------------------
POLICY_AWARE_SLOT = {"setting": "policy-aware", "label": "policy-aware model (Dann, Mansour and Mohri), 50M",
                     "status": "slot: trained and attacked by another builder; not run here"}
LABELS = {"member0": "member 0, undefended", "ensemble": "ensemble, undefended",
          "temp0.75": "member 0, temperature 0.75", "temp1.25": "member 0, temperature 1.25",
          "temp1.5": "member 0, temperature 1.5", "penalty1": "ensemble, disagreement penalty lambda 1",
          "penalty2": "ensemble, disagreement penalty lambda 2", "halt95": "ensemble, halt above 95th percentile",
          "halt80": "ensemble, halt above 80th percentile", "detector0.5": "ensemble, detector p > 0.5",
          "detector0.2": "ensemble, detector p > 0.2", "deflation-member0": "member 0, deflation (Smith-Winkler)",
          "deflation-ensemble": "ensemble, deflation (Smith-Winkler)",
          "penalty0": "ensemble, penalty lambda 0 (neutral point: the verdict's added mean-margin condition)"}


def _hacked(r: dict, accept_key: str = "grader_accept") -> bool:
    return bool(r[accept_key]) and not bool(r["oracle_accept"])


def frontier_table(recs: Sequence[dict], perfect: Dict[str, Sequence[dict]], instances: Sequence[str],
                   n_boot: int = 2000, seed: int = 0) -> dict:
    """Per search: the perfect emulator, every setting of ``SETTINGS`` and the policy-aware slot, each with
    ``arm_stats`` over the instances it has records for; each setting's hackability minus the undefended ensemble's,
    paired by instance; dominance against the undefended ensemble by point estimates (hackability and false
    rejection both no higher, one lower: dominates; both no lower, one higher: dominated)."""
    out = {}
    inst = list(instances)
    for se in SEARCHES:
        R = {(r["setting"], r["instance"]): r for r in recs if r["search"] == se}
        rows = []
        pf = [r for r in perfect.get(se, []) if r["instance"] in set(inst)]
        if pf:
            ga = np.array([r["grader_p"] >= ACCEPT_P for r in pf])
            row = {"setting": "perfect", "label": "perfect emulator (engine on fresh seeds)", "n_instances": len(pf),
                   "complete": len(pf) == len(inst),
                   **arm_stats(ga, [bool(r["oracle_accept"]) for r in pf], [r["oracle_share"] for r in pf],
                               [r["cluster"] for r in pf], n_boot, seed)}
            rows.append(row)
        else:
            rows.append({"setting": "perfect", "label": "perfect emulator", "status": "no reference records"})
        for s in SETTINGS:
            rs = [R[(s.name, i)] for i in inst if (s.name, i) in R]
            meta = {"setting": s.name, "label": LABELS.get(s.name, s.name), "judge": s.judge, "defence": s.defence,
                    "param": s.param, "derived_from": s.derived_from, "neutral": s.neutral}
            if not rs:
                rows.append({**meta, "status": "not run"})
                continue
            cl = [r["cluster"] for r in rs]
            row = {**meta, "n_instances": len(rs), "complete": len(rs) == len(inst),
                   **arm_stats([r["grader_accept"] for r in rs], [r["oracle_accept"] for r in rs],
                               [r["oracle_share"] for r in rs], cl, n_boot, seed),
                   "budget": sorted({int(r["budget"]) for r in rs}),
                   "month_steps": {"search_as_designed": int(sum(r["emu_month_steps_search"] for r in rs)),
                                   "search_computed": int(sum(r["emu_month_steps_search_computed"] for r in rs)),
                                   "verdict_as_designed": int(sum(r["emu_month_steps_verdict"] for r in rs))},
                   "n_best_score_minus_inf": int(sum(bool(r.get("best_score_is_minus_inf")) for r in rs))}
            common = [i for i in inst if (s.name, i) in R and ("ensemble", i) in R]
            if s.name != "ensemble" and common:
                row["hackability_minus_ensemble"] = hd.excess(
                    [_hacked(R[(s.name, i)]) for i in common], [_hacked(R[("ensemble", i)]) for i in common],
                    [R[("ensemble", i)]["cluster"] for i in common], n_boot=n_boot, seed=seed, bca=True).as_dict()
                row["hackability_minus_ensemble"]["n_paired"] = len(common)
                row["same_plan_as_ensemble"] = int(sum(R[(s.name, i)]["plan_hash"] == R[("ensemble", i)]["plan_hash"]
                                                       for i in common))
            rows.append(row)
        rows.append(dict(POLICY_AWARE_SLOT))
        ens = next((r for r in rows if r.get("setting") == "ensemble" and "hackability" in r), None)
        dom = {}
        if ens is not None and ens["complete"]:
            h0 = ens["hackability"]["value"]
            f0 = ens["false_rejection"].get("value")
            for r in rows:
                if r.get("setting") in ("ensemble", "perfect") or "hackability" not in r:
                    continue
                if not r["complete"]:
                    dom[r["setting"]] = "incomplete"
                    continue
                h, f = r["hackability"]["value"], r["false_rejection"].get("value")
                if f is None or f0 is None:
                    dom[r["setting"]] = "undefined (no oracle-accepted selected plan)"
                elif h <= h0 and f <= f0 and (h < h0 or f < f0):
                    dom[r["setting"]] = "dominates"
                elif h >= h0 and f >= f0 and (h > h0 or f > f0):
                    dom[r["setting"]] = "dominated"
                elif h == h0 and f == f0:
                    dom[r["setting"]] = "equal"
                else:
                    dom[r["setting"]] = "neither"
        out[se] = {"rows": rows, "dominance_vs_undefended_ensemble": dom, "n_instances_design": len(inst)}
    return _jsonable(out)


def _ci(e, signed: bool = False) -> str:
    """'value [lo, hi]' with the BCa limits; '*': the percentile interval (BCa undefined); '†': the exact bound of a
    hackability with no hacked unit; 'n/a' where the statistic is undefined (as ``run_audit._ci``)."""
    if not isinstance(e, dict) or e.get("value") is None or not np.isfinite(e["value"]):
        return "n/a"
    f = "{:+.3f}" if signed else "{:.3f}"
    lo, hi, mark = e.get("bca_lo"), e.get("bca_hi"), ""
    if lo is None or hi is None or not (np.isfinite(lo) and np.isfinite(hi)):
        lo, hi, mark = e.get("lo"), e.get("hi"), "*"
    if e.get("method") == hd.stats.ZERO_BOUND_METHOD:
        mark = "†"
    if lo is None or hi is None:
        return f.format(e["value"]) + " [n/a]"
    return f"{f.format(e['value'])} [{f.format(lo)}, {f.format(hi)}]{mark}"


def frontier_md(table: dict, header: Sequence[str]) -> str:
    L = list(header)
    for se in SEARCHES:
        t = table.get(se)
        if not t:
            continue
        L += ["", f"## {se} search, B = {BUDGET:,}", "",
              "| setting | n | hackability | false rejection | judge accepts | oracle accepts | oracle pass share of "
              "selected plans | oracle rejects given judge accepts | hackability minus undefended ensemble (paired) | "
              "hacked / false rejections / oracle accepts (counts) | emulator month-steps computed (search) |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in t["rows"]:
            if "hackability" not in r:
                L.append(f"| {r.get('label', r['setting'])} | - | {r.get('status', '')} |" + " |" * 8)
                continue
            n = f"{r['n_instances']}" + ("" if r["complete"] else f" of {t['n_instances_design']} (partial)")
            ms = r.get("month_steps", {}).get("search_computed")
            L.append(f"| {r['label']} | {n} | {_ci(r['hackability'])} | {_ci(r['false_rejection'])} | "
                     f"{_ci(r['judge_accept'])} | {_ci(r['oracle_accept'])} | {_ci(r['oracle_share'])} | "
                     f"{_ci(r['oracle_reject_given_judge_accept'])} | "
                     f"{_ci(r.get('hackability_minus_ensemble'), True) if 'hackability_minus_ensemble' in r else '-'} | "
                     f"{r['n_hacked']} / {r['n_false_rejections']} / {r['n_oracle_accept']} | "
                     f"{'-' if ms is None else f'{ms:,}'} |")
        dom = t.get("dominance_vs_undefended_ensemble") or {}
        if dom:
            L += ["", "Against the undefended ensemble (point estimates of hackability and false rejection): "
                  + "; ".join(f"{LABELS.get(k, k)}: {v}" for k, v in dom.items()) + "."]
    return "\n".join(L) + "\n"
