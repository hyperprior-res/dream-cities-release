#!/usr/bin/env python
"""The RL point in the audit's unit, the depth of the false acceptances, and the audit's cost in engine terms
. Reads stored files only, except ``replay``.

Commands (``PYTHONPATH=hpr-dream:code``, ``CUDA_VISIBLE_DEVICES=`` empty: nothing here uses a card):

* ``replay [--workers 4]``: the perfect-emulator verdict of every RL run's plan 0. Plan 0 of each instance is the
  first sampled episode's effective action log, read from the run's stored evaluation arrays
  (``<wm2-cache>/rl/<run>/eval3_001000000.npz``, read only; ``dream_plans`` for a policy trained in the emulator,
  ``closed_plans`` for the engine-trained learner, whose open-loop plans are its closed-loop ones). It is replayed
  by the engine on 8 seeds drawn exactly as the audit's perfect emulator draws them (``dc.audit.EngineSeedJudge``
  with the majority oracle's 32 seeds: sample k of the call's row 0 on ``seed_for("audit-seedcheck", start,
  "rl-audit-plan0", run, months, 0, k)``, redrawn past the nine residual seeds and every task's 32 oracle seeds of
  the start; the stream is the one the emulator's own verdict of plan 0 used), and accepted when at least 4 of the 8
  pass (the 4th-largest margin >= 0). Replays go to a local pool of ``--workers`` processes and to no disk cache.
  Checks on every run: the stored plan's hash equals the record's ``plan_hashes[0]``, the plan is effective, the
  emulator's 8 stored verdict margins of plan 0 recompute the record's ``plan0_audit_margins8`` and
  ``plan0_hacked``, and plan 0 of the first instance replayed on the 32 oracle seeds gives the stored per-seed
  oracle margins exactly. Writes ``results/analysis/rl_axis.replays.json``.
* ``analyse``: writes ``results/analysis/rl_axis.{json,md}``, ``false_acceptance_depth.{json,md}`` and
  ``audit_cost.{json,md}``.

Aggregation (the paper's, ``paper/scripts/make_numbers.py`` ``rl_arm``): a run's value is the rate over its
instances; the ladder's value is the mean over runs, with the cluster bootstrap over checkpoints
(``hpr_dream.stats.conditional_mean``, 2,000 resamples, seed 0, percentile and BCa 95 per cent). Every family has
the same number of runs, so the mean over runs is also the mean over families of the mean over runs. The
engine-trained learner is aggregated as ``\\RlEngFull`` is: per family the mean over its seeds, overall the mean
over the five families. Its interval, and the interval of the main checkpoint alone (one checkpoint: no
checkpoint clusters), is the audit's: per instance the mean over the seeds, resampled by city family
(``family_id``), the overall value a ratio estimator whose weights give each task family one fifth.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import math
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "code", ROOT / "hpr-dream"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from dc import audit as A          # noqa: E402
from dc import rl_adaptor as RA    # noqa: E402
from dc import tasks as T          # noqa: E402
from hpr_dream import stats as hs  # noqa: E402

RL_RESULTS = ROOT / "results" / "rl"
RL_CACHE = Path(os.environ.get("WM2_RL_CACHE", "<cache>/rl"))
OUT = ROOT / "results" / "analysis"
REPLAYS = OUT / "rl_axis.replays.json"
DECISION_TABLE = RL_RESULTS / "bc" / "decision_table_pooled.json"
TASKS_FILE = ROOT / "data" / "tasks_v2_H24.json"
TASKS_STEM = "tasks_v2_H24"
MONTHS = 1_000_000                          # the RL arm's final snapshot
H = 24
K = A.K_VERDICT                             # 8 fresh samples
RANK = A.VERDICT_RANK                       # accepted at 4 of 8
FAMILIES = tuple(T.TASKS)                   # grow, solvent, treasury, recover, power
# the 24-checkpoint ladder: the same pattern as analyse_ladder.LADDER_RUN and make_numbers.LADDER_RUN (test-checked)
LADDER_RUN = re.compile(r"(os|sf)_\d+m_(full|small)")
MAIN_CKPT = "os_50m_full-samples_006000000"
N_LADDER_RUNS = 360
N_BOOT = hs.N_BOOT
STREAM = "rl-audit-plan0"                   # the stream of the emulator's verdict of plan 0 (dc.rl.evaluate_snapshot)


# ---------------------------------------------------------------------------------------------------------------
# runs
def ladder_runs(rl_root: Path = RL_RESULTS, months: int = MONTHS) -> list[dict]:
    """The ladder's RL runs exactly as ``make_numbers.rl_runs`` / ``rl_arm`` select them: every
    ``<ckpt>__<family>__s<seed>__tasks_v2_H24`` with a final summary whose checkpoint matches the ladder pattern,
    kept only for checkpoints with all 15 runs (5 families x 3 seeds)."""
    runs = []
    for f in sorted(glob.glob(str(rl_root / f"*__{TASKS_STEM}" / f"eval3_{months:09d}.summary.json"))):
        name = Path(f).parent.name
        if name.startswith("engine"):
            continue
        ck, fam, seed, _ = name.split("__")
        if not LADDER_RUN.fullmatch(ck.split("-samples_")[0]):
            continue
        runs.append({"run": name, "ck": ck, "fam": fam, "seed": int(seed[1:])})
    per = {}
    for r in runs:
        per.setdefault(r["ck"], []).append(r)
    complete = {c for c, rs in per.items() if len(rs) == 15 and {x["fam"] for x in rs} == set(FAMILIES)}
    return [r for r in runs if r["ck"] in complete]


def engine_runs(table: Path = DECISION_TABLE) -> dict:
    """{family: [run, ...]}: the engine-trained learner's runs (``families.<f>.scratch_run``), as ``\\RlEngFull``."""
    d = json.loads(Path(table).read_text())
    return {f: d["families"][f]["scratch_run"].split("+") for f in FAMILIES}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


def read_summary(run: str, months: int = MONTHS) -> dict:
    return json.loads((RL_RESULTS / run / f"eval3_{months:09d}.summary.json").read_text())


# ---------------------------------------------------------------------------------------------------------------
# replay: the perfect emulator's verdict of plan 0
class _Recorder:
    """Stands in for ``dc.audit.EngineJudge`` inside ``EngineSeedJudge``: records the (plan, seed) rows the judge
    asks for and answers from ``table`` (filled by the replays) or with zeros (the recording pass)."""

    def __init__(self) -> None:
        self.asked: list[tuple[bytes, int]] = []
        self.table: dict[tuple[bytes, int], np.ndarray] | None = None

    def scalars(self, inst, eff_plans, seeds, key_sink=None, store=True):
        P = np.ascontiguousarray(eff_plans, dtype=np.int16).reshape(-1, H, A.N_COLS)
        sd = np.broadcast_to(np.asarray(seeds, dtype=np.int64), (P.shape[0],))
        rows = [(P[i].tobytes(), int(sd[i])) for i in range(P.shape[0])]
        if self.table is None:
            self.asked += rows
            return np.zeros((P.shape[0], H + 1, A.NUM_SCALARS), dtype=np.int64)
        return np.stack([self.table[r] for r in rows])


def perfect_seeds(inst, plan: np.ndarray, run: str, months: int = MONTHS) -> list[int]:
    """The 8 engine seeds of the perfect emulator's verdict of ``plan`` (``EngineSeedJudge``, majority oracle)."""
    rec = _Recorder()
    j = A.EngineSeedJudge(rec, oracle_n=T.ORACLE_N)
    j.samples(inst, plan[None], K, (STREAM, run, int(months)))
    return [s for _, s in rec.asked]


def verdict_from_traj(inst, traj: np.ndarray) -> dict:
    """8 sampled trajectories (8, H+1, 20) -> margins, pass count, verdict at 4 of 8."""
    m = np.asarray(A.task_margin(inst, traj), dtype=np.float64)
    return {"margins": m, "n_pass": int((m >= 0).sum()), "accept": bool(RA.fourth_largest(m) >= 0)}


def _plans_of(run: str, months: int = MONTHS) -> tuple[np.ndarray, dict, str]:
    z = np.load(RL_CACHE / run / f"eval3_{months:09d}.npz", allow_pickle=False)
    arrays = {k: z[k] for k in z.files}
    key = "dream_plans" if "dream_plans" in arrays else "closed_plans"
    return arrays[key], arrays, key


def prepare_run(run: str, inst_by_key: dict, months: int = MONTHS) -> dict:
    """Everything the replays of one run need, with the checks of the module docstring (raises on a mismatch)."""
    recs = read_jsonl(RL_RESULTS / run / f"eval3_{months:09d}.jsonl")
    plans, arrays, key = _plans_of(run, months)
    n = len(recs)
    if plans.shape != (n, recs[0]["n_episodes"], H, A.N_COLS):
        raise SystemExit(f"{run}: {key} has shape {plans.shape} for {n} records")
    rows = []
    for k, r in enumerate(recs):
        inst = inst_by_key[r["instance"]]
        p0 = np.ascontiguousarray(plans[k, 0])
        if A.plan_hash(p0) != r["plan_hashes"][0]:
            raise SystemExit(f"{run} {r['instance']}: stored plan 0 does not hash to the record's plan_hashes[0]")
        if not np.array_equal(A.effective(p0[None], inst.task, H)[0], p0):
            raise SystemExit(f"{run} {r['instance']}: stored plan 0 is not effective")
        if bool(arrays["open_accept"][k, 0]) != bool(r["plan0_engine_open_accept"]) or \
                not np.isclose(arrays["open_share"][k, 0], r["plan0_engine_open_share"], rtol=0, atol=1e-12):
            raise SystemExit(f"{run} {r['instance']}: stored oracle verdict of plan 0 differs from the record")
        if "audit_traj" in arrays:              # the emulator's own verdict of plan 0, recomputed
            v = verdict_from_traj(inst, arrays["audit_traj"][k])
            if not np.allclose(v["margins"], r["plan0_audit_margins8"], rtol=0, atol=1e-12) or \
                    v["accept"] != r["plan0_audit_accept"] or \
                    (v["accept"] and not r["plan0_engine_open_accept"]) != r["plan0_hacked"]:
                raise SystemExit(f"{run} {r['instance']}: plan0_hacked does not recompute from the stored samples")
        rows.append({"instance": r["instance"], "inst": inst, "plan": p0, "seeds": perfect_seeds(inst, p0, run, months),
                     "oracle_accept": bool(r["plan0_engine_open_accept"]), "oracle_share": float(r["plan0_engine_open_share"])})
    check_inst = rows[0]["inst"]
    check_seeds = A.oracle_seed_list(check_inst, T.ORACLE_N)
    return {"run": run, "plans_key": key, "rows": rows, "check": {"seeds": check_seeds,
            "stored_margins": np.asarray(arrays["open_margins"][0, 0], dtype=np.float64)}}


def _jobs(prep: dict) -> list[tuple]:
    out = []
    for i, row in enumerate(prep["rows"]):
        for s in row["seeds"]:
            out.append((row["inst"].cty, row["plan"].tobytes(), H, int(s)))
    row = prep["rows"][0]
    for s in prep["check"]["seeds"]:
        out.append((row["inst"].cty, row["plan"].tobytes(), H, int(s)))
    return out


def finish_run(prep: dict, results: list[bytes]) -> dict:
    """Per instance: the perfect emulator's pass count of 8 and verdict; the oracle check of instance 0."""
    it = iter(results)
    out = {"run": prep["run"], "plans_key": prep["plans_key"], "instances": [], "n_pass8": [], "perfect_accept": [],
           "oracle_accept": [], "oracle_share": [], "seeds": []}
    for row in prep["rows"]:
        tr = np.stack([np.frombuffer(next(it), dtype="<i8").reshape(H + 1, A.NUM_SCALARS) for _ in row["seeds"]])
        v = verdict_from_traj(row["inst"], tr)
        out["instances"].append(row["instance"])
        out["n_pass8"].append(v["n_pass"])
        out["perfect_accept"].append(v["accept"])
        out["oracle_accept"].append(row["oracle_accept"])
        out["oracle_share"].append(row["oracle_share"])
        out["seeds"].append([int(s) for s in row["seeds"]])
    tr = np.stack([np.frombuffer(next(it), dtype="<i8").reshape(H + 1, A.NUM_SCALARS) for _ in prep["check"]["seeds"]])
    m = np.asarray(A.task_margin(prep["rows"][0]["inst"], tr), dtype=np.float64)
    err = float(np.max(np.abs(m - prep["check"]["stored_margins"])))
    out["oracle_check"] = {"instance": prep["rows"][0]["instance"], "n_seeds": len(m), "max_abs_margin_error": err}
    if err > 1e-9:
        raise SystemExit(f"{prep['run']}: plan 0 on the oracle seeds gives margins {err} from the stored ones")
    return out


def cmd_replay(a) -> None:
    import multiprocessing as mp
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    insts = {i.key: i for i in A.load_instances(TASKS_FILE, horizon=H)}
    runs = [r["run"] for r in ladder_runs()]
    if len(runs) != N_LADDER_RUNS:
        raise SystemExit(f"{len(runs)} ladder runs, {N_LADDER_RUNS} expected")
    eng = [r for f in FAMILIES for r in engine_runs()[f]]
    todo = runs + eng
    prog = Path(a.progress)
    prog.parent.mkdir(parents=True, exist_ok=True)
    done = {}
    if prog.exists():
        for x in prog.read_text().splitlines():
            if x.strip():
                d = json.loads(x)
                done[d["run"]] = d
    t0, n_rep = time.time(), 0
    with mp.get_context("spawn").Pool(a.workers, initializer=A._worker_init) as pool:
        for j, run in enumerate(todo):
            if run in done:
                continue
            prep = prepare_run(run, insts)
            jobs = _jobs(prep)
            res = pool.map(A._replay_job, jobs, chunksize=max(1, len(jobs) // (4 * a.workers)))
            d = finish_run(prep, res)
            d["engine_replays"] = len(jobs)
            n_rep += len(jobs)
            with prog.open("a") as f:
                f.write(json.dumps(d) + "\n")
            done[run] = d
            el = time.time() - t0
            print(f"[{j + 1}/{len(todo)}] {run}: {sum(d['perfect_accept'])}/{len(d['perfect_accept'])} accepted; "
                  f"{n_rep} replays in {el:.0f} s ({n_rep * H / max(el, 1e-9):.0f} city-months/s)", flush=True)
    out = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "definition": ("perfect-emulator verdict of plan 0 (the first sampled episode's effective action log) of "
                          "every run: the engine on 8 seeds of dc.audit.EngineSeedJudge (oracle_n 32), stream "
                          f"('{STREAM}', run, {MONTHS}), row 0; accepted at 4 of 8. oracle_accept / oracle_share: "
                          "the stored majority verdict and pass share of the same plan over its 32 oracle seeds"),
           "months": MONTHS, "workers": a.workers,
           "engine_replays": int(sum(done[r]["engine_replays"] for r in todo)),
           "engine_city_months": int(sum(done[r]["engine_replays"] for r in todo) * H),
           "runs": {r: done[r] for r in todo}}
    REPLAYS.write_text(json.dumps(out))
    print(f"wrote {REPLAYS}")


# ---------------------------------------------------------------------------------------------------------------
# statistics: one-way and two-way cluster bootstraps of ratio estimators
SNAPSHOTS = (250_000, 500_000, 1_000_000)
SNAP_TAG = {250_000: "Qtr", 500_000: "Half", 1_000_000: "Full"}
CK_SEED, CITY_SEED = 0, 1            # checkpoint draws as make_numbers.rl_arm (seed 0); city draws independent of them


def binom_tail(p: float, n: int = K, k: int = RANK) -> float:
    """P(Binomial(n, p) >= k)."""
    return float(sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1)))


def _clean(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else float(x)


class Arm:
    """Instance rows of a set of runs: per row its checkpoint, city (``family_id``, the audit's cluster), task
    family, run, base weight ``u`` and values. Weights: ``family_mean`` (default) gives each row
    u = 1 / (runs of its task family x instances of its run), so the ratio estimator sum(u v) / sum(u) over one family
    is the mean over the family's runs of the run's mean over its instances, and over several families the mean over
    families of those (with equal runs per family, the mean over runs: ``make_numbers.rl_arm``; with 1 or 3 seeds per
    family, the mean over families of the mean over seeds: ``\\RlEngFull``). ``instance`` gives u = 1 / (runs of the
    task family): every instance once, its seeds averaged."""

    def __init__(self, rows: list[dict], weighting: str = "family_mean") -> None:
        self.rows = rows
        nf = {}
        for r in rows:
            nf.setdefault(r["task"], set()).add(r["run"])
        ni = {}
        for r in rows:
            ni[r["run"]] = ni.get(r["run"], 0) + 1
        self.u = np.array([1.0 / (len(nf[r["task"]]) * (ni[r["run"]] if weighting == "family_mean" else 1)) for r in rows])
        self.weighting = weighting

    def subset(self, fams) -> "Arm":
        return Arm([r for r in self.rows if r["task"] in fams], self.weighting)

    def has(self, key: str) -> bool:
        return bool(self.rows) and all(key in r and r[key] is not None for r in self.rows)


def _mats(arm: Arm, key: str, cks: list, cities: list):
    ci = {c: j for j, c in enumerate(cities)}
    ki = {c: j for j, c in enumerate(cks)}
    M = np.zeros((len(cks), len(cities)))
    D = np.zeros_like(M)
    for r, u in zip(arm.rows, arm.u):
        a, b = ki[r["ck"]], ci[r["cluster"]]
        M[a, b] += u * float(r[key])
        D[a, b] += u
    return M, D


def boot(terms: list, n_boot: int = N_BOOT, level: float = hs.LEVEL) -> dict | None:
    """``terms``: [(sign, Arm, key)]. The statistic is sum of sign x (ratio estimator of key over the arm). Returns the
    point value and three 95 per cent intervals: two-way (checkpoints and cities resampled independently, percentile),
    checkpoint only and city only (percentile and BCa, the jackknife over the resampled clusters). Arms holding the
    same checkpoints share their checkpoint draws; every arm shares the city draws (paired by city)."""
    terms = [(s, a, k) for s, a, k in terms]
    if any(not a.has(k) for _, a, k in terms):
        return None
    cities = sorted({r["cluster"] for _, a, _ in terms for r in a.rows})
    Ck = len(cities)
    Wk = hs._weights(Ck, n_boot, CITY_SEED)
    parts = []
    ck_sets = {}
    for s, a, k in terms:
        cks = sorted({r["ck"] for r in a.rows})
        M, D = _mats(a, k, cks, cities)
        key = tuple(cks)
        if key not in ck_sets:
            ck_sets[key] = hs._weights(len(cks), n_boot, CK_SEED)
        parts.append((s, M, D, key))
    n_ck = max(len(k) for k in ck_sets)

    def stat(wc: dict, wk: np.ndarray) -> np.ndarray:
        out = 0.0
        for s, M, D, key in parts:
            W = wc[key]
            num = np.einsum("bi,ij,bj->b", W, M, wk)
            den = np.einsum("bi,ij,bj->b", W, D, wk)
            with np.errstate(invalid="ignore", divide="ignore"):
                out = out + s * np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)
        return out

    ones_c = {k: np.ones((1, len(k))) for k in ck_sets}
    value = float(stat(ones_c, np.ones((1, Ck)))[0])
    q = [(1 - level) / 2, (1 + level) / 2]

    def pct(b):
        ok = b[np.isfinite(b)]
        return [float(x) for x in np.quantile(ok, q)] if ok.size else [None, None]

    tw = stat(ck_sets, Wk)
    out = {"value": value, "n_rows": int(sum(len(a.rows) for _, a, _ in terms)), "n_cities": Ck,
           "n_checkpoints": n_ck, "n_boot": n_boot, "level": level,
           "twoway": dict(zip(("lo", "hi"), pct(tw)))}
    if n_ck > 1 and len(terms) == 1:
        # one arm: the paper's own computation (hpr_dream.stats.conditional_mean over run values, clusters =
        # checkpoints), so that ties in a discrete bootstrap distribution are broken exactly as there
        s, a, k = terms[0]
        rv, rw, rc = {}, {}, {}
        for r, u in zip(a.rows, a.u):
            rv[r["run"]] = rv.get(r["run"], 0.0) + u * float(r[k])
            rw[r["run"]] = rw.get(r["run"], 0.0) + u
            rc[r["run"]] = r["ck"]
        names = sorted(rv)
        if np.allclose([rw[x] for x in names], rw[names[0]], rtol=1e-12, atol=0):
            v = np.array([rv[x] / rw[x] for x in names])
            e = hs.conditional_mean(s * v, None, np.array([rc[x] for x in names]), n_boot=n_boot, seed=CK_SEED,
                                    level=level, bca=True)
            out["checkpoint_only"] = {"lo": e.lo, "hi": e.hi, "bca_lo": _clean(e.bca_lo), "bca_hi": _clean(e.bca_hi),
                                      "method": "hpr_dream.stats.conditional_mean over run values (make_numbers.rl_arm)"}
    if n_ck > 1 and out.get("checkpoint_only") is None:
        cb = stat(ck_sets, np.ones((n_boot, Ck)))
        jk = {k: (1.0 - np.eye(len(k))) if len(k) == n_ck else np.ones((n_ck, len(k))) for k in ck_sets}
        jack = stat(jk, np.ones((n_ck, Ck)))
        bl, bh = hs._bca(value, cb[np.isfinite(cb)], jack, level)
        out["checkpoint_only"] = {**dict(zip(("lo", "hi"), pct(cb))), "bca_lo": _clean(bl), "bca_hi": _clean(bh)}
    elif n_ck <= 1:
        out["checkpoint_only"] = None          # one checkpoint: the two-way interval is the city interval
    cyb = stat({k: np.ones((n_boot, len(k))) for k in ck_sets}, Wk)
    jack = stat({k: np.ones((Ck, len(k))) for k in ck_sets}, 1.0 - np.eye(Ck))
    bl, bh = hs._bca(value, cyb[np.isfinite(cyb)], jack, level)
    out["city_only"] = {**dict(zip(("lo", "hi"), pct(cyb))), "bca_lo": _clean(bl), "bca_hi": _clean(bh)}
    return out


# ---------------------------------------------------------------------------------------------------------------
# instance rows of the RL runs
def instance_rows(run: str, ck: str, months: int, rep: dict | None = None) -> list[dict]:
    """One row per instance of a run's evaluation at ``months``: rates over the instance's 8 sampled episodes, and
    plan 0 (the first episode's action log) under the audit's verdict rule; the perfect emulator's verdict of plan 0
    from the replays (final snapshot)."""
    recs = read_jsonl(RL_RESULTS / run / f"eval3_{months:09d}.jsonl")
    emu = recs[0].get("environment") == "emulator"
    out = []
    if rep is not None and rep["instances"] != [r["instance"] for r in recs]:
        raise SystemExit(f"{run}: replays and records hold different instances")
    for j, r in enumerate(recs):
        om = float(np.mean(r["engine_open_margins"]))
        d = {"run": run, "ck": ck, "task": r["task"], "instance": r["instance"], "cluster": r["cluster"],
             "oracle": float(np.mean(r["engine_open_accepts"])), "closed": float(np.mean(r["engine_closed_accepts"])),
             "closed_margin_minus_open_margin": float(np.mean(r["engine_closed_margins"])) - om,
             "oracle_accept0": float(r["plan0_engine_open_accept"]),
             "plugin0": 0.0 if r["plan0_engine_open_accept"] else binom_tail(float(r["plan0_engine_open_share"]))}
        d["closed_minus_open"] = d["closed"] - d["oracle"]
        if emu:
            d.update({"dream": float(np.mean(r["dream_accepts"])),
                      "infl": float(np.mean(np.asarray(r["dream_margins"]) - np.asarray(r["engine_open_margins"]))),
                      "fa0": float(r["plan0_hacked"]), "emu_accept0": float(r["plan0_audit_accept"])})
            d["gap"] = d["dream"] - d["oracle"]
        else:                                    # the engine-trained learner: its own environment is the engine
            d.update({"gap_ref": d["closed"] - d["oracle"], "infl_ref": d["closed_margin_minus_open_margin"]})
        if rep is not None:
            if bool(rep["oracle_accept"][j]) != bool(r["plan0_engine_open_accept"]):
                raise SystemExit(f"{run} {r['instance']}: replays and records disagree on the oracle verdict")
            pa = bool(rep["perfect_accept"][j])
            d.update({"perfect_accept0": float(pa), "perfect_fa0": float(pa and not r["plan0_engine_open_accept"])})
            if emu:
                d["excess0"] = d["fa0"] - d["perfect_fa0"]
        out.append(d)
    return out


def summary_check(run: str, months: int, rows: list[dict]) -> None:
    """The rows reproduce the run's summary exactly (rates are means over instances of 8 episodes)."""
    sm = read_summary(run, months)
    pairs = [("rate_engine_open_accept", "oracle"), ("rate_engine_closed_accept", "closed"),
             ("rate_plan0_engine_open_accept", "oracle_accept0")]
    if "dream" in rows[0]:
        pairs += [("rate_dream_accept", "dream"), ("inflation_open", "infl"), ("plan0_hackability", "fa0"),
                  ("rate_plan0_audit_accept", "emu_accept0")]
    for f, k in pairs:
        v = float(np.mean([r[k] for r in rows]))
        if sm.get(f) is None or abs(v - float(sm[f])) > 1e-12:
            raise SystemExit(f"{run} at {months}: {k} from the records {v} against the summary's {f} {sm.get(f)}")


def load_arms(replays: dict | None) -> dict:
    """{snapshot: {"ladder", "main", "coverage", "engine"[, "engine_instance"]}: Arm} from the per-instance records."""
    rr = (replays or {}).get("runs", {})
    lad = ladder_runs()
    if len(lad) != N_LADDER_RUNS:
        raise SystemExit(f"{len(lad)} ladder runs, {N_LADDER_RUNS} expected")
    er = engine_runs()
    cov = sorted(Path(p).parent.name for p in glob.glob(str(RL_RESULTS / f"{COV_CKPT}__*__{TASKS_STEM}"
                                                                         / f"eval3_{MONTHS:09d}.summary.json")))
    out = {}
    for m in SNAPSHOTS:
        rows = {"ladder": [], "main": [], "coverage": [], "engine": []}
        for r in lad:
            x = instance_rows(r["run"], r["ck"], m, rr.get(r["run"]) if m == MONTHS else None)
            summary_check(r["run"], m, x)
            rows["ladder"] += x
            if r["ck"] == MAIN_CKPT:
                rows["main"] += x
        for f in FAMILIES:
            for run in er[f]:
                x = instance_rows(run, "engine", m, rr.get(run) if m == MONTHS else None)
                summary_check(run, m, x)
                rows["engine"] += x
        for run in cov:
            x = instance_rows(run, COV_CKPT, m)
            summary_check(run, m, x)
            rows["coverage"] += x
        out[m] = {k: Arm(v) for k, v in rows.items()}
        out[m]["engine_instance"] = Arm(rows["engine"], "instance")
        out[m]["ladder_instance"] = Arm(rows["ladder"], "instance")
        out[m]["main_instance"] = Arm(rows["main"], "instance")
    return out, {"ladder": [r["run"] for r in lad], "engine": er, "coverage": cov}


COV_CKPT = "os_50m_cov-samples_006000000"
SCOPES = ("all",) + FAMILIES


def scoped(arms: dict, name: str, scope: str) -> Arm:
    a = arms[name]
    return a if scope == "all" else a.subset((scope,))


# ---------------------------------------------------------------------------------------------------------------
# the paper's macros, read back for the reproduction check
FAM_WORD = {"grow": "Grow", "solvent": "Solv", "treasury": "Treas", "recover": "Recov", "power": "Power"}
MACRO_KEYS = {"Dream": "dream", "Oracle": "oracle", "Gap": "gap", "Closed": "closed", "Infl": "infl"}


def read_macros(path: Path = ROOT / "paper" / "numbers.tex") -> dict:
    out = {}
    for m in re.finditer(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", path.read_text()):
        out[m.group(1)] = m.group(2)
    return out


def macro_value(s: str) -> float | None:
    s = s.replace("\\textminus", "-").replace("+", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def macro_interval(s: str):
    m = re.fullmatch(r"\[(.*), (.*)\]", s.strip())
    return (macro_value(m.group(1)), macro_value(m.group(2))) if m else None


def macro_check(res: dict) -> dict:
    """The point estimates and the checkpoint-only BCa intervals against the RL macros of ``paper/numbers.tex``
    (3 decimals as printed)."""
    mac = read_macros()
    rows, bad = [], []

    def cmp(name, v, ci=None):
        if name not in mac:
            return
        p = macro_value(mac[name])
        ok = p is not None and abs(round(v + 0.0, 3) - p) < 1e-9
        rows.append({"macro": name, "printed": mac[name], "recomputed": round(v, 6), "equal": ok})
        if not ok:
            bad.append(name)
        if ci is not None and name + "CI" in mac:
            pi = macro_interval(mac[name + "CI"])
            lo, hi = ci
            oki = pi is not None and lo is not None and abs(round(lo, 3) - pi[0]) < 1e-9 and abs(round(hi, 3) - pi[1]) < 1e-9
            rows.append({"macro": name + "CI", "printed": mac[name + "CI"], "recomputed": [lo, hi], "equal": oki})
            if not oki:
                bad.append(name + "CI")

    for m, tag in SNAP_TAG.items():
        for scope in SCOPES:
            if scope != "all" and m != MONTHS:
                continue
            for word, key in MACRO_KEYS.items():
                e = res["ladder"][m][scope].get(key)
                if e is None:
                    continue
                pre = "Rl" + ("" if tag == "Full" else tag) + (FAM_WORD[scope] if scope != "all" else "")
                co = e.get("checkpoint_only") or {}
                lo, hi = co.get("bca_lo"), co.get("bca_hi")
                if lo is None:
                    lo, hi = co.get("lo"), co.get("hi")
                cmp(pre + word, e["value"], (lo, hi))
        eng = res["engine"][m]["all"]["oracle"]["value"]
        cmp("RlEng" + tag, eng)
        cmp("RlLost" + tag, res["lost"][m]["ladder"]["all"]["open"]["value"])
    for f in FAMILIES:
        cmp("RlEng" + FAM_WORD[f], res["engine"][MONTHS][f]["oracle"]["value"])
    cmp("RlMainDream", res["main"][MONTHS]["all"]["dream"]["value"])
    cmp("RlMainOracle", res["main"][MONTHS]["all"]["oracle"]["value"])
    return {"compared": len(rows), "unequal": bad, "rows": rows}


# ---------------------------------------------------------------------------------------------------------------
# items 1 to 3 and the statistics referee's additions
EMU_KEYS = ("dream", "oracle", "gap", "infl", "closed", "closed_minus_open", "fa0", "emu_accept0", "oracle_accept0",
            "plugin0", "perfect_fa0", "perfect_accept0", "excess0")
ENG_KEYS = ("closed", "oracle", "gap_ref", "infl_ref", "oracle_accept0", "plugin0", "perfect_fa0", "perfect_accept0")


def rl_results(arms: dict) -> dict:
    res = {"ladder": {}, "main": {}, "coverage": {}, "engine": {}, "engine_instance_weighted": {}, "excess": {},
           "lost": {}, "coverage_excess": {}}
    for m in SNAPSHOTS:
        A_ = arms[m]
        for who in ("ladder", "main", "coverage"):
            res[who][m] = {s: {k: boot([(1, scoped(A_, who, s), k)]) for k in EMU_KEYS} for s in SCOPES}
        res["engine"][m] = {s: {k: boot([(1, scoped(A_, "engine", s), k)]) for k in ENG_KEYS} for s in SCOPES}
        res["engine_instance_weighted"][m] = {s: {k: boot([(1, scoped(A_, "engine_instance", s), k)])
                                                  for k in ("gap_ref", "infl_ref", "oracle", "closed")} for s in SCOPES}
        # the emulator-trained gap and inflation minus the engine learner's, paired by city
        res["excess"][m] = {who: {s: {"gap": boot([(1, scoped(A_, who, s), "gap"), (-1, scoped(A_, "engine", s), "gap_ref")]),
                                      "infl": boot([(1, scoped(A_, who, s), "infl"), (-1, scoped(A_, "engine", s), "infl_ref")])}
                                  for s in SCOPES} for who in ("ladder", "main", "coverage")}
        # real success given up: the engine learner minus the emulator-trained policies, open and closed loop
        res["lost"][m] = {}
        for who in ("ladder", "main"):
            res["lost"][m][who] = {s: {"open": boot([(1, scoped(A_, "engine", s), "oracle"), (-1, scoped(A_, who, s), "oracle")]),
                                       "closed": boot([(1, scoped(A_, "engine", s), "closed"), (-1, scoped(A_, who, s), "closed")])}
                                   for s in SCOPES}
            iw = who + "_instance"
            res["lost"][m][who + "_instance_weighted"] = {
                s: {"open": boot([(1, scoped(A_, "engine_instance", s), "oracle"), (-1, scoped(A_, iw, s), "oracle")]),
                    "closed": boot([(1, scoped(A_, "engine_instance", s), "closed"), (-1, scoped(A_, iw, s), "closed")])}
                for s in SCOPES}
        # coverage against the main checkpoint: the difference of their excesses (= the difference of their gaps)
        res["coverage_excess"][m] = {s: {k: boot([(1, scoped(A_, "coverage", s), k), (-1, scoped(A_, "main", s), k)])
                                         for k in ("gap", "infl", "oracle", "closed")} for s in SCOPES}
    return res


def variant_facts() -> dict:
    """How the engine-trained learner's variant was chosen  and its cells."""
    er = engine_runs()
    cfg = {r: json.loads((RL_RESULTS / r / "config.json").read_text()) for f in FAMILIES for r in er[f]}
    vr = json.loads((RL_RESULTS / "bc" / "variant_rule.json").read_text())
    return {"seeds_per_family": {f: len(er[f]) for f in FAMILIES}, "runs": er,
            "variant_of_run": {r: c["meta"].get("variant") for r, c in cfg.items()},
            "mask_treasury_tax_of_run": {r: c["cfg"].get("mask_treasury_tax") for r, c in cfg.items()},
            "instances_of_run": {r: c["meta"].get("n_instances") for r, c in cfg.items()},
            "b8_rule": ("the working notes, section B1, decision rules fixed at 10:23Z before the results they "
                        "read existed: (1) the sixth tuning run is grow with the better of stab and stab_spatial on "
                        "power at 1,000,000 months (stab_spatial, 0.131 against 0.125); (2) the frozen learner is the "
                        "better of b8 and that variant by the mean of the power and grow oracle pass rates at 1,000,000 "
                        "months (stab_spatial, 0.102 against 0.095). The tuning runs are engine-trained, seed 0, judged "
                        "by the 32-seed majority oracle on the 40 evaluation instances of each family (the instances "
                        "every RL number is read on). B8 records that rule 2 decided on a difference the data do not "
                        "resolve (stab_spatial minus b8, paired over instances: +0.022 [-0.016, 0.066] on power, -0.009 "
                        "[-0.047, 0.028] on grow)."),
            "frozen_learner": "dc.rl.FROZEN = stab_spatial with the treasury tax mask ; the mask acts on "
                              "treasury only (MASKED_TAX_TASKS)",
            "variant_rule_json": vr}


# ---------------------------------------------------------------------------------------------------------------
# item 5 helper kept from the first version: binomial plug-in over all 8 episodes (reconciles R2's 0.058)
def plugin_all8(runs: list[str]) -> float:
    v = []
    for run in runs:
        recs = read_jsonl(RL_RESULTS / run / f"eval3_{MONTHS:09d}.jsonl")
        v.append(float(np.mean([0.0 if o else binom_tail(s) for r in recs
                                for o, s in zip(r["engine_open_accepts"], r["engine_open_shares"])])))
    return float(np.mean(v))


# ---------------------------------------------------------------------------------------------------------------
# item 4: depth of the false acceptances
MAIN_AUDIT = ROOT / "results/audit/ladder/os_50m_full/samples_006000000"
DEPTH_SOURCES = {"random": (MAIN_AUDIT / TASKS_STEM, ROOT / "results/audit/engine_reference" / TASKS_STEM / "B_economy"),
                 "cem_seeded": (MAIN_AUDIT / f"{TASKS_STEM}_cem_seeded",
                                ROOT / "results/audit/engine_reference" / TASKS_STEM / "cem_seeded_B_economy")}


def read_records(path: Path) -> list[dict]:
    with gzip.open(path / "records.jsonl.gz", "rt") as f:
        return [json.loads(x) for x in f if x.strip()]


def depth_of(recs: list[dict], method: str, B: int, expected: set) -> dict:
    rs = [r for r in recs if r["method"] == method and int(r["budget"]) == B]
    if {r["instance"] for r in rs} != expected or len(rs) != len(expected):
        return {"status": f"{len({r['instance'] for r in rs} & expected)}/{len(expected)} instances"}
    if any(r.get("oracle_rule") != "majority" or int(r["oracle_n_seeds"]) != T.ORACLE_N for r in rs):
        return {"status": "not judged by the 32-seed majority oracle"}
    fa = [r for r in rs if r["grader_p"] >= A.ACCEPT_P and not r["oracle_accept"]]
    for r in fa:                                    # the share is the oracle's: recompute it from the per-seed verdicts
        if not np.isclose(np.mean(r["oracle_accept_seeds"]), r["oracle_share"], rtol=0, atol=1e-12):
            raise SystemExit(f"{r['plan_id']}: oracle_share differs from its per-seed verdicts")
    sh = np.array([r["oracle_share"] for r in fa], float)
    mm = np.array([r["oracle_margin"] for r in fa], float)
    by = {}
    for f in FAMILIES:
        x = np.array([r["oracle_share"] for r in fa if r["task"] == f], float)
        by[f] = {"n_false_acceptances": int(x.size), "n_share_below_0_1": int((x < 0.1).sum()),
                 "median_share": float(np.median(x)) if x.size else None}
    return {"status": "ok", "n_instances": len(rs), "n_false_acceptances": len(fa),
            "false_acceptance": len(fa) / len(rs),
            "median_oracle_share": float(np.median(sh)) if sh.size else None,
            "n_share_below_0_1": int((sh < 0.1).sum()),
            "n_share_zero": int((sh == 0).sum()),
            "median_majority_margin": float(np.median(mm)) if mm.size else None,
            "shares": sorted(float(x) for x in sh), "by_family": by}


def depth(B: int = 1000) -> dict:
    tasks = json.loads(TASKS_FILE.read_text())
    expected = {f"{r['start_id']}|{r['task']}|H{r['horizon']}" for r in tasks["instances"] if int(r["horizon"]) == H}
    out = {"budget": B, "n_instances_expected": len(expected), "definitions": {
        "false acceptance": "the judge accepts the selected plan (pass share >= 0.5 over its 8 fresh samples: "
                            "grader_p >= 0.5) and the 32-seed majority oracle rejects it (oracle_accept false)",
        "oracle share": "the selected plan's pass share over its 32 oracle seeds (oracle_share, checked against "
                        "oracle_accept_seeds)",
        "majority margin": "oracle_margin: the 16th-largest of the 32 per-seed margins (negative for every false "
                           "acceptance)"},
        "methods": {}}
    for m, (emu_dir, ref_dir) in DEPTH_SOURCES.items():
        out["methods"][m] = {"emulator": {"source": str(emu_dir.relative_to(ROOT)), **depth_of(read_records(emu_dir), m, B, expected)},
                             "perfect_emulator": {"source": str(ref_dir.relative_to(ROOT)),
                                                  **depth_of(read_records(ref_dir), m, B, expected)}}
    return out


# ---------------------------------------------------------------------------------------------------------------
# item 5: cost of the audit in engine terms
LADDER_AUDIT = ROOT / "results/audit/ladder"
CITY_SETS = {"c40": TASKS_STEM, "c80": "tasks_v2x_H24"}


def _record_costs(recs: list[dict], method: str = "random") -> dict:
    """Engine work of a random-search audit's selected plans, per instance, from its records (budgets 1 to 1,000)."""
    rs = [r for r in recs if r["method"] == method]
    by_inst = {}
    for r in rs:
        by_inst.setdefault(r["instance"], []).append(r)
    budgets = sorted({int(r["budget"]) for r in rs})
    per_rec = {int(r["engine_city_months_judge"]) for r in rs}
    n_seeds = {int(r["oracle_n_seeds"]) + len(r.get("nine_seed_margins", [])) for r in rs if "nine_seed_margins" in r}
    distinct = [len({r["plan_hash"] for r in v}) for v in by_inst.values()]
    b1000 = [r for r in rs if int(r["budget"]) == 1000]
    return {"n_instances": len(by_inst), "budgets": budgets, "records": len(rs),
            "engine_city_months_judge_per_record": sorted(per_rec),
            "replays_per_record": sorted(x // H for x in per_rec),
            "engine_city_months_judge_all_budgets": int(sum(int(r["engine_city_months_judge"]) for r in rs)),
            "distinct_selected_plans_per_instance_mean": float(np.mean(distinct)),
            "distinct_selected_plans": int(sum(distinct)),
            "engine_city_months_floor_all_budgets": int(sum(int(r.get("engine_city_months_floor", 0)) for r in rs)),
            "engine_city_months_judge_B1000": int(sum(int(r["engine_city_months_judge"]) for r in b1000)),
            "emu_month_steps_all_budgets": int(sum(int(r["emu_month_steps"]) for r in rs)),
            "emu_month_steps_B1000": int(sum(int(r["emu_month_steps"]) for r in b1000)),
            "oracle_seeds_per_plan": sorted({int(r["oracle_n_seeds"]) for r in rs}),
            "residual_seeds_per_plan": sorted({len(r["nine_seed_margins"]) for r in rs if "nine_seed_margins" in r}),
            "seeds_per_plan_from_records": sorted(n_seeds)}


def audit_cost() -> dict:
    out = {"definitions": {
        "replay": "one 24-month engine run of one plan from a start file on one seed (24 engine city-months)",
        "audit, emulator side": "per checkpoint: random search inside the emulator at budgets 1, 10, 100 and 1,000 "
                                "(the 1,000 candidates are the start's first 1,000 behaviour plans; budgets nest) and the "
                                "engine verdict of each budget's selected plan: engine_city_months_judge per record",
        "perfect-emulator reference": "the same search with the engine as the judge (EngineSeedJudge), run once per "
                                      "city set and shared by every checkpoint: K = 2 engine samples of each candidate, "
                                      "8 of the selected plan, and the selected plan's oracle and residual seeds",
        "floors": "the residual and flip floors (40-city audits only); not needed for false acceptance"},
        "city_sets": {}}
    per_ck = {}
    for cs, stem in CITY_SETS.items():
        rows = {}
        for d in sorted(LADDER_AUDIT.glob(f"*/samples_*/{stem}")):
            run = d.parts[-3]
            if not LADDER_RUN.fullmatch(run) or not (d / "records.jsonl.gz").exists():
                continue
            rows[f"{run}-{d.parts[-2]}"] = _record_costs(read_records(d))
        ref = ROOT / "results/audit/engine_reference" / stem / "B_economy"
        rrec = read_records(ref)
        rr = [r for r in rrec if r["method"] == "random"]
        rb = {B: [r for r in rr if int(r["budget"]) == B] for B in sorted({int(r["budget"]) for r in rr})}
        n_ref = len({r["instance"] for r in rr})
        cj = json.loads((ref / "costs.json").read_text())["summary"]
        ref_d = {"source": str(ref.relative_to(ROOT)), "n_instances": n_ref,
                 "per_instance_B1000": {
                     "engine_city_months_search_samples": float(np.mean([r["emu_month_steps_search"] for r in rb[1000]])),
                     "engine_city_months_verdict_samples": float(np.mean([r["emu_month_steps_verdict"] for r in rb[1000]])),
                     "engine_city_months_oracle_and_residual": float(np.mean([r["engine_city_months_judge"] for r in rb[1000]]))},
                 "whole_run_from_costs_json": {
                     "judge_month_steps_computed (engine-seeds judge: engine city-months)": cj.get("judge_month_steps_computed"),
                     "engine_city_months_replayed (cache misses, every purpose incl. floors)": cj.get("engine_city_months_replayed"),
                     "engine_replays": cj.get("engine_replays")}}
        ref_d["per_instance_B1000"]["total"] = float(sum(ref_d["per_instance_B1000"].values()))
        ref_d["per_instance_B1000"]["replays"] = ref_d["per_instance_B1000"]["total"] / H
        out["city_sets"][cs] = {"tasks": stem, "checkpoints": rows, "perfect_emulator_reference": ref_d}
        for k, v in rows.items():
            per_ck.setdefault(k, {})[cs] = v
    # per checkpoint over all 120 cities, where both city sets are complete
    full = {}
    for k, v in per_ck.items():
        if set(v) == set(CITY_SETS) and all(x["budgets"] == [1, 10, 100, 1000] for x in v.values()):
            n = sum(x["n_instances"] for x in v.values())
            full[k] = {"n_instances": n,
                       "engine_city_months_judge_all_budgets": sum(x["engine_city_months_judge_all_budgets"] for x in v.values()),
                       "engine_city_months_judge_B1000": sum(x["engine_city_months_judge_B1000"] for x in v.values()),
                       "distinct_selected_plans": sum(x["distinct_selected_plans"] for x in v.values())}
    out["c120_per_checkpoint"] = full
    # RL as the paper evaluates it
    runs = ladder_runs()
    tot = {"design_engine_city_months": 0, "open": 0, "closed": 0, "closed_check": 0, "greedy": 0, "instances": 0}
    main = dict(tot)
    for r in runs:
        sm = read_summary(r["run"])
        recs = read_jsonl(RL_RESULTS / r["run"] / f"eval3_{MONTHS:09d}.jsonl")
        parts = {"design_engine_city_months": int(sm["design_engine_city_months"]),
                 "open": sum(int(x["engine_city_months_open"]) for x in recs),
                 "closed": sum(int(x["engine_city_months_closed"]) for x in recs),
                 "closed_check": sum(int(x.get("engine_city_months_closed_check", 0)) for x in recs),
                 "greedy": sum(int(x.get("greedy_engine_city_months", 0)) for x in recs), "instances": len(recs)}
        if parts["open"] + parts["closed"] + parts["closed_check"] + parts["greedy"] != parts["design_engine_city_months"]:
            raise SystemExit(f"{r['run']}: engine months by purpose do not add to design_engine_city_months")
        for k, v in parts.items():
            tot[k] += v
            if r["ck"] == MAIN_CKPT:
                main[k] += v
    er = engine_runs()
    eng_train = {f: [int(read_summary(x)["months"]) for x in er[f]] for f in FAMILIES}
    eng_eval = {f: [int(read_summary(x)["design_engine_city_months"]) for x in er[f]] for f in FAMILIES}
    out["rl"] = {
        "definitions": {
            "open": "open-loop oracle: 8 action logs per instance on 32 oracle seeds (256 replays, 6,144 city-months per "
                    "instance): what the acceptance gap and plan 0's false acceptance need",
            "closed": "the policy acting on the engine, 8 episodes per instance (192 city-months)",
            "closed_check": "the closed-loop logs replayed for the equality check (192 city-months)",
            "greedy": "the greedy plan: 32 oracle seeds plus two 24-month closed-loop runs (816 city-months)",
            "engine-trained learner": "1,000,000 engine months of training per run (the summary's months), plus its "
                                      "evaluation"},
        "ladder_360_runs": {**tot, "n_runs": len(runs), "n_checkpoints": len({r["ck"] for r in runs})},
        "main_checkpoint_15_runs": main,
        "per_checkpoint_mean": {k: v / len({r["ck"] for r in runs}) for k, v in tot.items()},
        "engine_trained_learner": {"runs": er, "training_months": eng_train, "evaluation_city_months": eng_eval,
                                   "n_runs": sum(len(v) for v in er.values()),
                                   "training_months_total": int(sum(sum(v) for v in eng_train.values())),
                                   "evaluation_city_months_total": int(sum(sum(v) for v in eng_eval.values()))}}
    return out


# ---------------------------------------------------------------------------------------------------------------
# outputs
def fe(d, signed=False, digits=3) -> str:
    if d is None or d.get("value") is None:
        return "n/a"
    f = (lambda x: f"{x:+.{digits}f}") if signed else (lambda x: f"{x:.{digits}f}")
    lo, hi = d.get("bca_lo"), d.get("bca_hi")
    if lo is None or hi is None:
        lo, hi = d.get("lo"), d.get("hi")
    return f"{f(d['value'])} [{f(lo)}, {f(hi)}]" if lo is not None and hi is not None else f(d["value"])


def _iv(d, signed):
    f = (lambda x: f"{x:+.3f}") if signed else (lambda x: f"{x:.3f}")
    if not d or d.get("lo") is None:
        return "n/a"
    return f"[{f(d['lo'])}, {f(d['hi'])}]"


def _ivb(d, signed):
    if not d:
        return "n/a"
    if d.get("bca_lo") is not None:
        return _iv({"lo": d["bca_lo"], "hi": d["bca_hi"]}, signed)
    return _iv(d, signed)


def ftw(e, signed=False) -> str:
    """value [two-way percentile interval]"""
    if e is None:
        return "n/a"
    v = f"{e['value']:+.3f}" if signed else f"{e['value']:.3f}"
    return f"{v} {_iv(e['twoway'], signed)}"


def f3way(e, signed=False) -> str:
    if e is None:
        return "n/a | n/a | n/a | n/a"
    v = f"{e['value']:+.3f}" if signed else f"{e['value']:.3f}"
    return " | ".join([v, _iv(e["twoway"], signed), _ivb(e.get("checkpoint_only"), signed) if e.get("checkpoint_only")
                       else "(one checkpoint)", _iv(e["city_only"], signed)])


QLAB = {"dream": "dream acceptance", "oracle": "oracle acceptance (open loop)", "gap": "acceptance gap",
        "infl": "margin inflation", "closed": "closed-loop pass rate on the engine"}


def md_rl_axis(out: dict) -> str:
    R = out["results"]
    F = MONTHS
    vf = out["engine_reference_facts"]
    L = ["# The RL point in the audit's unit and its perfect-emulator reference ", "",
         f"Runs: the {out['runs']['n_ladder']} ladder runs (24 checkpoints x 5 task families x 3 seeds; os_50m_cov "
         f"excluded), the coverage model's {len(out['runs']['coverage'])} runs, and the engine-trained learner's "
         f"{sum(vf['seeds_per_family'].values())} runs of `results/rl/bc/decision_table_pooled.json` (seeds per family: "
         + ", ".join(f"{f} {n}" for f, n in vf["seeds_per_family"].items()) + "). Every number is recomputed from the "
         "per-instance records (`eval3_<months>.jsonl`) and checked against each run's summary.", "",
         "Aggregation: a run's rate is the mean over its instances (8 episodes each); a cell is the mean over task "
         "families of the mean over the family's runs (the ladder: the mean over runs, as the paper; the engine-trained "
         "learner: as `\\RlEngFull`). Intervals, 95 per cent, 2,000 resamples: **two-way** (checkpoints and held-out "
         "cities resampled independently, percentile), **checkpoint only** (BCa, the paper's current intervals), "
         "**city only** (checkpoints fixed, percentile). Cities are the audit's clusters (`family_id`, 40). Differences "
         "between a cell and the engine-trained learner share the city draws (paired by city).", "",
         f"Macro check: {out['macro_check']['compared']} printed RL values and intervals of `paper/numbers.tex` compared; "
         + ("all equal." if not out["macro_check"]["unequal"] else "unequal: " + ", ".join(out["macro_check"]["unequal"]) + "."),
         "", "## 1. What the paper prints, with the three intervals (ladder)", "",
         "| snapshot | scope | quantity | value | two-way | checkpoint only (BCa) | city only |", "|---|---|---|---|---|---|---|"]
    for m in SNAPSHOTS:
        for s in SCOPES:
            if s != "all" and m != F:
                continue
            for k in ("dream", "oracle", "gap", "infl", "closed"):
                L.append(f"| {m:,} | {s} | {QLAB[k]} | {f3way(R['ladder'][m][s][k], k in ('gap', 'infl'))} |")
    L += ["", "## 2. Plan 0 under the audit's verdict rule, beside the perfect emulator (ladder, 1,000,000 months)", "",
          "Plan 0: the first sampled episode's action log of each instance. Emulator: 8 fresh samples, accepted at 4 or "
          "more of 8; perfect emulator: the engine on 8 seeds disjoint from the oracle's (EngineSeedJudge), accepted at "
          "4 of 8; oracle: 32-seed majority. False acceptance = accepted and oracle rejects. Value [two-way].", "",
          "| scope | emulator accepts | perfect emulator accepts | oracle accepts | false acceptance, emulator | false "
          "acceptance, perfect emulator (replayed) | excess | plug-in estimate of the perfect value |",
          "|---|---|---|---|---|---|---|---|"]
    for s in SCOPES:
        x = R["ladder"][F][s]
        L.append(f"| {s} | {ftw(x['emu_accept0'])} | {ftw(x['perfect_accept0'])} | {ftw(x['oracle_accept0'])} | "
                 f"{ftw(x['fa0'])} | {ftw(x['perfect_fa0'])} | {ftw(x['excess0'], True)} | {ftw(x['plugin0'])} |")
    x = R["main"][F]["all"]
    e = R["engine"][F]["all"]
    L += ["", f"Main checkpoint (15 runs; city intervals): false acceptance {ftw(x['fa0'])}, perfect emulator "
              f"{ftw(x['perfect_fa0'])}, excess {ftw(x['excess0'], True)}. Engine-trained learner's own plan 0 under the "
              f"perfect emulator (replayed): false acceptance {ftw(e['perfect_fa0'])} (plug-in {ftw(e['plugin0'])}). "
              f"Plug-in over all 8 episodes' plans (not plan 0 only; R2's computation): emulator-trained "
              f"{out['plugin_all8']['ladder']:.3f}, engine-trained {out['plugin_all8']['engine']:.3f}."]
    if "replays" in out:
        rp = out["replays"]
        L += ["", f"Replays: {rp['engine_replays']:,} engine replays ({rp['engine_city_months']:,} city-months), "
                  f"each run's plan 0 of its first instance also replayed on its 32 oracle seeds: largest margin error "
                  f"against the stored oracle margins {rp['oracle_check_max_abs_margin_error']:.1e}."]
    L += ["", "## 3. The engine-trained learner: the perfect-emulator reference of the gap and the inflation", "",
          "Own-episode pass rate = closed loop on the engine (its own environment); reference gap = own-episode pass rate "
          "minus the oracle's open-loop acceptance of the same action logs; reference inflation = own-episode margin minus "
          "the oracle's mean margin of the same logs. Intervals over cities (value [city percentile]; BCa in the JSON).", "",
          "| snapshot | scope | seeds | own-episode pass rate | oracle acceptance | reference gap | reference inflation |",
          "|---|---|---|---|---|---|---|"]
    for m in SNAPSHOTS:
        for s in SCOPES:
            x = R["engine"][m][s]
            sd = "1 or 3" if s == "all" else str(vf["seeds_per_family"][s])
            L.append(f"| {m:,} | {s} | {sd} | {ftw(x['closed'])} | {ftw(x['oracle'])} | {ftw(x['gap_ref'], True)} | "
                     f"{ftw(x['infl_ref'], True)} |")
    iw = R["engine_instance_weighted"][F]["all"]["gap_ref"]
    L += ["", f"Instance-weighted (every instance once, its seeds averaged): reference gap {iw['value']:+.3f}, city BCa "
              f"{_ivb(iw['city_only'], True)}.", "",
          "## 4. Excess of the emulator-trained gap and inflation over the reference", "",
          "Emulator-trained minus engine-trained, paired by city; ladder two-way, main checkpoint and coverage model city "
          "only (one checkpoint each).", "",
          "| snapshot | scope | gap excess, ladder | gap excess, main checkpoint | inflation excess, ladder | inflation "
          "excess, main checkpoint |", "|---|---|---|---|---|---|"]
    for m in SNAPSHOTS:
        for s in SCOPES:
            if s != "all" and m != F:
                continue
            E = R["excess"][m]
            L.append(f"| {m:,} | {s} | {ftw(E['ladder'][s]['gap'], True)} | {ftw(E['main'][s]['gap'], True)} | "
                     f"{ftw(E['ladder'][s]['infl'], True)} | {ftw(E['main'][s]['infl'], True)} |")
    L += ["", "## 5. Real success given up against the engine-trained learner", "",
          "Engine-trained minus emulator-trained, paired by city: open loop (the oracle's acceptance of each policy's own "
          "logs; `\\RlLost*`) and closed loop (each policy acting on the engine).", "",
          "| snapshot | scope | open loop, ladder | closed loop, ladder | open loop, main checkpoint | closed loop, main "
          "checkpoint | open loop, ladder, instance-weighted |", "|---|---|---|---|---|---|---|"]
    for m in SNAPSHOTS:
        for s in SCOPES:
            if s != "all" and m != F:
                continue
            Lo = R["lost"][m]
            L.append(f"| {m:,} | {s} | {ftw(Lo['ladder'][s]['open'], True)} | {ftw(Lo['ladder'][s]['closed'], True)} | "
                     f"{ftw(Lo['main'][s]['open'], True)} | {ftw(Lo['main'][s]['closed'], True)} | "
                     f"{ftw(Lo['ladder_instance_weighted'][s]['open'], True)} |")
    li = R["lost"][F]["ladder_instance_weighted"]["all"]["open"]
    L += ["", f"Instance-weighted open-loop loss at 1,000,000 months, city BCa: {li['value']:+.3f} {_ivb(li['city_only'], True)}. "
              "Engine-seed variation of the reference is not in any interval (1 or 3 seeds per family).", "",
          "## 6. Coverage: the coverage model and the main checkpoint against the same reference (1,000,000 months)", "",
          "| scope | gap, main | gap, coverage | gap excess, main | gap excess, coverage | coverage minus main (gap) | "
          "inflation excess, main | inflation excess, coverage |", "|---|---|---|---|---|---|---|---|"]
    for s in SCOPES:
        E = R["excess"][F]
        L.append(f"| {s} | {ftw(R['main'][F][s]['gap'], True)} | {ftw(R['coverage'][F][s]['gap'], True)} | "
                 f"{ftw(E['main'][s]['gap'], True)} | {ftw(E['coverage'][s]['gap'], True)} | "
                 f"{ftw(R['coverage_excess'][F][s]['gap'], True)} | {ftw(E['main'][s]['infl'], True)} | "
                 f"{ftw(E['coverage'][s]['infl'], True)} |")
    L += ["", "City intervals only: one coverage model against one main checkpoint, 3 RL seeds each.", "",
          "## 7. How the reference learner was chosen (facts for the paper)", "",
          "The engine-trained learner is the RL arm's frozen learner (`stab_spatial`; for treasury with the tax mask of "
          "the analysis plan, which acts on treasury only) trained on the engine for 1,000,000 months. The variant was chosen by "
          "rule 2 of the working notes: the "
          "better of `b8` and `stab_spatial` by the mean of the power and grow oracle pass rates at 1,000,000 months of "
          "engine-trained seed-0 runs, judged on the same 40 evaluation instances per family on which every RL number is "
          "read (`stab_spatial` 0.102 against 0.095; B8 records that the difference is within instance noise: paired "
          "+0.022 [-0.016, 0.066] on power, -0.009 [-0.047, 0.028] on grow). Two of the runs that made the choice "
          "(`engine__power__s0__tasks_v2_H24__v-stab_spatial`, `engine__grow__s0__tasks_v2_H24__v-stab_spatial`) are "
          "cells of the reference. Seeds per family in the reference: "
          + ", ".join(f"{f} {n}" for f, n in vf["seeds_per_family"].items()) + " (runs: "
          + "; ".join(f"{f}: {', '.join(vf['runs'][f])}" for f in FAMILIES) + "). `results/rl/bc/variant_rule.json` is a "
          f"different rule ({vf['variant_rule_json']['rule']}: chose `{vf['variant_rule_json']['choice']}`) "
          "between the warm-started variants (`bc`, `bc_kl`); the reference runs are trained from scratch and are not "
          "warm-started.", ""]
    return "\n".join(L)


def md_depth(d: dict) -> str:
    L = ["# Depth of the false acceptances ", "",
         f"Main checkpoint (os_50m_full, 6,000,000 samples), {d['n_instances_expected']} instances on the 40 cities, "
         f"budget {d['budget']:,}. Counts, no intervals.", "",
         "| search | judge | instances | false acceptances | median oracle pass share | pass share below 0.1 | pass "
         "share 0 | median majority margin |", "|---|---|---|---|---|---|---|---|"]
    for m, v in d["methods"].items():
        for who, x in v.items():
            if x["status"] != "ok":
                L.append(f"| {m} | {who} | not computed: {x['status']} | | | | | |")
                continue
            L.append(f"| {m} | {who.replace('_', ' ')} | {x['n_instances']} | {x['n_false_acceptances']} | "
                     f"{x['median_oracle_share']:.3f} | {x['n_share_below_0_1']} | {x['n_share_zero']} | "
                     f"{x['median_majority_margin']:.3f} |")
    L += ["", "False acceptance: the judge accepts the selected plan at 4 or more of its 8 fresh samples and the 32-seed "
              "majority oracle rejects it. Pass share: the plan's share of the 32 oracle seeds on which it passes. Sources: "
              + "; ".join(f"{m}: {v['emulator']['source']} and {v['perfect_emulator']['source']}" for m, v in d["methods"].items())
          + ".", ""]
    return "\n".join(L)


def md_cost(c: dict) -> str:
    L = ["# Cost of the audit in engine terms ", "",
         "A replay is one 24-month engine run of one plan on one seed (24 city-months).", "",
         "## Random-search audit, emulator side, per checkpoint (budgets 1, 10, 100, 1,000)", "",
         "| city set | checkpoints | instances | replays per selected plan | engine city-months per checkpoint "
         "(all four budgets) | per instance (replays) | at B = 1,000 only, per checkpoint | distinct selected plans per instance |",
         "|---|---|---|---|---|---|---|---|"]
    for cs, v in c["city_sets"].items():
        rows = list(v["checkpoints"].values())
        if not rows:
            continue
        n = {x["n_instances"] for x in rows}
        cm = [x["engine_city_months_judge_all_budgets"] for x in rows]
        b1 = [x["engine_city_months_judge_B1000"] for x in rows]
        dp = [x["distinct_selected_plans_per_instance_mean"] for x in rows]
        rp = sorted({y for x in rows for y in x["replays_per_record"]})
        L.append(f"| {cs} | {len(rows)} | {'/'.join(map(str, sorted(n)))} | {'/'.join(map(str, rp))} | "
                 f"{int(np.mean(cm)):,} | {np.mean(cm) / np.mean(list(n)):,.0f} ({np.mean(cm) / np.mean(list(n)) / H:,.0f}) | "
                 f"{int(np.mean(b1)):,} | {np.mean(dp):.2f} |")
    full = c["c120_per_checkpoint"]
    if full:
        x = next(iter(full.values()))
        L += ["", f"All 120 cities ({x['n_instances']} instances), on the {len(full)} checkpoints with both city sets "
                  f"complete: {x['engine_city_months_judge_all_budgets']:,} engine city-months per checkpoint "
                  f"({x['engine_city_months_judge_all_budgets'] // H:,} replays) over the four budgets, "
                  f"{x['engine_city_months_judge_B1000']:,} ({x['engine_city_months_judge_B1000'] // H:,} replays) at "
                  f"B = 1,000 alone; with a replay cache (a plan selected at several budgets replayed once) "
                  f"{x['distinct_selected_plans'] * 41:,} replays. Each selected plan: 32 oracle seeds (needed for false "
                  "acceptance) and 9 residual seeds (floors and decision fidelity); the oracle seeds alone at B = 1,000: "
                  f"{x['n_instances'] * 32:,} replays ({x['n_instances'] * 32 * H:,} city-months) per checkpoint."]
    L += ["", "## Perfect-emulator reference (shared by every checkpoint, once per city set)", "",
          "| city set | instances | engine city-months per instance at B = 1,000 (search samples + verdict samples + "
          "oracle and residual) | replays per instance | whole run: engine-seeds judge city-months |", "|---|---|---|---|---|"]
    for cs, v in c["city_sets"].items():
        r = v["perfect_emulator_reference"]
        p = r["per_instance_B1000"]
        L.append(f"| {cs} | {r['n_instances']} | {p['engine_city_months_search_samples']:,.0f} + "
                 f"{p['engine_city_months_verdict_samples']:,.0f} + {p['engine_city_months_oracle_and_residual']:,.0f} = "
                 f"{p['total']:,.0f} | {p['replays']:,.0f} | "
                 f"{r['whole_run_from_costs_json']['judge_month_steps_computed (engine-seeds judge: engine city-months)']:,} |")
    rl = c["rl"]
    m, t = rl["main_checkpoint_15_runs"], rl["ladder_360_runs"]
    e = rl["engine_trained_learner"]
    L += ["", "## RL as the paper evaluates it", "",
          "| scope | runs | instance rows | open-loop oracle | closed loop | closed-loop check | greedy | total engine "
          "city-months |", "|---|---|---|---|---|---|---|---|",
          f"| main checkpoint | 15 | {m['instances']} | {m['open']:,} | {m['closed']:,} | {m['closed_check']:,} | "
          f"{m['greedy']:,} | {m['design_engine_city_months']:,} |",
          f"| ladder | {t['n_runs']} | {t['instances']} | {t['open']:,} | {t['closed']:,} | {t['closed_check']:,} | "
          f"{t['greedy']:,} | {t['design_engine_city_months']:,} |", "",
          f"The engine-trained learner (the RL arm's perfect-emulator reference): {e['n_runs']} runs, "
          f"{e['training_months_total']:,} engine months of training and {e['evaluation_city_months_total']:,} of "
          "evaluation. Per instance and run the RL evaluation replays each of its 8 action logs on the 32 oracle seeds (256 "
          "replays, 6,144 city-months); plan 0's false acceptance alone needs 32 replays (768 city-months), the same as "
          "one selected plan of the audit.", "",
          "Per-instance figures of the reference are the records' design counts at B = 1,000 (the 1,000 candidates' "
          "K = 2 samples are shared by the tasks of a start with the same forced events, and budgets nest); the whole-run "
          "figure is the measured count of the engine-seeds judge, including the behaviour plans' verdicts.", ""]
    return "\n".join(L)


def cmd_analyse(a) -> None:
    rep = json.loads(REPLAYS.read_text()) if REPLAYS.exists() else None
    meta = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "script": "code/scripts/rl_axis.py",
            "argv": sys.argv[1:]}
    arms, runs = load_arms(rep)
    res = rl_results(arms)
    out = {**meta, "runs": {"n_ladder": len(runs["ladder"]), "ladder": runs["ladder"], "engine": runs["engine"],
                            "coverage": runs["coverage"],
                            "selection": "ladder: results/rl/<ckpt>__<family>__s<seed>__tasks_v2_H24, checkpoint matching "
                                         "(os|sf)_<size>m_(full|small) with all 15 runs (make_numbers.rl_arm); engine: "
                                         "decision_table_pooled.json scratch_run; coverage: os_50m_cov-samples_006000000"},
           "definitions": DEFINITIONS, "aggregation": AGGREGATION,
           "perfect_emulator_replayed": rep is not None,
           "results": res, "macro_check": None,
           "plugin_all8": {"ladder": plugin_all8(runs["ladder"]),
                           "engine": float(np.mean([np.mean([plugin_all8([r]) for r in runs["engine"][f]]) for f in FAMILIES]))},
           "engine_reference_facts": variant_facts()}
    out["macro_check"] = macro_check(res)
    if rep is not None:
        rr = rep["runs"]
        out["replays"] = {"file": str(REPLAYS.relative_to(ROOT)), "engine_replays": rep["engine_replays"],
                          "engine_city_months": rep["engine_city_months"], "runs": len(rr),
                          "oracle_check_max_abs_margin_error": max(v["oracle_check"]["max_abs_margin_error"] for v in rr.values())}
    (OUT / "rl_axis.json").write_text(json.dumps(out, indent=1, default=_json_default))
    (OUT / "rl_axis.md").write_text(md_rl_axis(out))
    d = depth()
    (OUT / "false_acceptance_depth.json").write_text(json.dumps({**meta, **d}, indent=1))
    (OUT / "false_acceptance_depth.md").write_text(md_depth(d))
    c = audit_cost()
    (OUT / "audit_cost.json").write_text(json.dumps({**meta, **c}, indent=1))
    (OUT / "audit_cost.md").write_text(md_cost(c))
    print("macro check: " + (f"{out['macro_check']['compared']} compared, all equal" if not out["macro_check"]["unequal"]
                             else "UNEQUAL " + ", ".join(out["macro_check"]["unequal"])))
    print("wrote " + ", ".join(str((OUT / f).relative_to(ROOT)) for f in (
        "rl_axis.json", "rl_axis.md", "false_acceptance_depth.json", "false_acceptance_depth.md", "audit_cost.json",
        "audit_cost.md")))


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    return str(o)


DEFINITIONS = {
    "dream": "rate_dream_accept per instance: share of its 8 sampled episodes in the emulator that pass on their own "
             "trajectory (closed loop in the policy's own environment)",
    "oracle": "rate_engine_open_accept: share of the same 8 action logs the 32-seed majority oracle accepts open loop",
    "gap": "dream minus oracle (the acceptance gap)",
    "infl": "inflation_open: mean over the 8 episodes of the dream margin minus the oracle's mean margin of the same log",
    "closed": "rate_engine_closed_accept: share of 8 episodes of the policy acting closed loop on the engine (fresh "
              "seeds) that pass; for the engine-trained learner its own-episode pass rate",
    "closed_minus_open": "closed minus oracle",
    "gap_ref": "engine-trained learner: closed (own-episode pass rate) minus oracle (its logs open loop): the perfect-"
               "emulator reference of the acceptance gap",
    "infl_ref": "engine-trained learner: mean closed-loop margin minus the oracle's mean margin of the same logs: the "
                "reference of the margin inflation",
    "fa0": "plan0_hackability: the emulator accepts plan 0 (the first sampled episode's action log) on 8 fresh samples "
           "at 4 or more of 8 (4th-largest margin >= 0; dc.rl.evaluate_snapshot audit phase, EmulatorJudge.samples, "
           "stream ('rl-audit-plan0', run, months); the audit's K = 8 and rule) and the 32-seed majority oracle rejects it",
    "emu_accept0": "rate_plan0_audit_accept", "oracle_accept0": "rate_plan0_engine_open_accept",
    "perfect_accept0": "the perfect emulator accepts plan 0: the engine on 8 seeds of dc.audit.EngineSeedJudge with the "
                       "majority oracle's 32 seeds reserved (run_audit.py --judge engine-seeds), stream ('rl-audit-plan0', "
                       "run, 1000000), row 0; at least 4 of 8 pass (rl_axis.replays.json)",
    "perfect_fa0": "perfect_accept0 and the oracle rejects", "excess0": "fa0 minus perfect_fa0, paired by instance",
    "plugin0": "plug-in estimate of perfect_fa0: [oracle rejects plan 0] x P(Binomial(8, oracle pass share) >= 4); an "
               "estimate, beside the replayed value as a check",
    "excess": "emulator-trained gap (or inflation) minus the engine-trained reference, paired by city",
    "lost": "engine-trained minus emulator-trained: oracle (open loop) or closed (closed loop)",
    "coverage_excess": "coverage model minus main checkpoint (equal to the difference of their excesses over the "
                       "same reference)"}
AGGREGATION = ("a run's rate: mean over its instances; a cell: mean over task families of the mean over the family's "
               "runs (ladder: = mean over runs, 72 per family; engine-trained: = mean over families of the mean over "
               "seeds, as \\RlEngFull); *_instance_weighted: every instance once, its runs averaged. Intervals: 95 per "
               "cent, 2,000 resamples; twoway = checkpoints (seed 0, the draws of make_numbers.rl_arm) and cities "
               "(family_id, seed 1) resampled independently, percentile; checkpoint_only = cities fixed (percentile, "
               "BCa; equals make_numbers.rl_arm's interval); city_only = checkpoints fixed (percentile, BCa by the "
               "leave-one-city-out jackknife). Arms of a difference share the city draws (paired by city); an arm on "
               "one checkpoint (main, coverage, engine-trained) has no checkpoint draw")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("replay")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--progress", required=True, help="resumable per-run progress file (JSON lines), outside results/")
    p.set_defaults(fn=cmd_replay)
    p = sub.add_parser("analyse")
    p.set_defaults(fn=cmd_analyse)
    a = ap.parse_args(argv)
    if a.cmd == "replay" and not 1 <= a.workers <= 4:
        raise SystemExit("at most 4 workers")
    a.fn(a)


if __name__ == "__main__":
    main()
