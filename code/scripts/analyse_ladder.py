#!/usr/bin/env python
"""Across emulators: does the cheap audit predict what reinforcement learning overstates?

One command, re-runnable as results land (from the repository root):

    PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/analyse_ladder.py

For every ladder checkpoint and task family (a *pair*) it gathers whatever exists:

- **audit**, on three city sets: the 40 cities (``data/tasks_v2_H24.json``; run directories
  ``results/audit/ladder/<run>/samples_<N>/tasks_v2_H24[_cem_seeded]``), the 80 new cities
  (``data/tasks_v2x_H24.json``; ``.../tasks_v2x_H24[_cem_seeded]``) and all 120 pooled (the instances of both
  files; a rate is events over instances, the excess over the perfect emulator is paired by instance against the
  reference of the instance's own file; the analysis plan). Per search (``random``, ``cem_seeded``) and budget (10, 100,
  1,000) on the pair's instances: the false acceptance (the judge accepts the selected plan, pass share >= 0.5 of
  its 8 samples, and the 32-seed majority oracle rejects it), the judge's and the oracle's acceptance, the false
  rejection of the selected plans (among those the oracle accepts, the share the judge rejects), and the excess
  over the perfect emulator (the engine judging itself on fresh seeds, ``results/audit/engine_reference/<tasks>/
  {B_economy, cem_seeded_B_economy}``; paired by instance, method, budget and attacker seed, as
  ``run_audit.py --compare-reference``); on the behaviour plans of the 40 cities (``pool_stats.json``, rates
  within the task family, where the run has floors), the judge's false rejection and false acceptance;
- **RL** (``results/rl/<checkpoint>__<family>__s<seed>__tasks_v2_H24/eval3_<months>.summary.json``, the frozen
  learner) at 250,000, 500,000 and 1,000,000 months: the margin inflation (``inflation_open``: dream margin minus
  the open-loop engine margin of the same plan; the protocol variable, on which the main claim is decided,
  the analysis plan), the dream acceptance, the oracle's open-loop acceptance of the same plans, their gap (reported
  beside it), the closed-loop acceptance; mean, standard deviation and count over the RL seeds;
- **fidelity** (``results/fidelity/ladder/<run>/{dev,test}/<run>_samples_<N>_dec-*.json``, ``gap_closed``, one
  model sample): structural changed-tile F1 at one month, structural changed-since-start F1 at 12 months, the
  median relative error of funds and of population at 12 months; and, for the finals , the
  held-out likelihood (``onestep.loglik_nats_per_transition.elbo`` of the test selection, nats per transition) and
  the fixed-candidate decision fidelity on each city file (per instance, Spearman between the emulator's two-sample
  mean margin and the engine's margin over the first 100 behaviour plans, from the random-search audit's
  ``pools.npz``; the mean over instances; see ``decision_fidelity``);
- the checkpoint's size, data scale, objective, training stage and lineage, from its training config.

``main_claim.json`` also holds ``results.seeded_nested_set``: the pool-seeded search's cross-emulator row on the
largest complete nested set of the analysis plan (``seeded_nested_set``).

Added by the specification, after every earlier field (each of which is unchanged): ``results.exploratory_logged_plan``,
the analysis plan's exploratory comparator (E1: the main claim's statistics with random search's false acceptance at budget
1, one logged plan per instance, as the predictor; E2: Spearman at 1,000 minus Spearman at 1 on the same cluster
resamples; the 120-city rows carry the analysis plan's wording only when the main claim's inputs are complete), with the
budget-1 columns in ``pairs.csv``; and in ``coverage.json`` the coverage model's fixed-candidate decision fidelity
beside the main checkpoint's, paired by instance (``coverage_decision_fidelity``).

Added by the specification, after every earlier field (each of which is unchanged): ``budget_contrast_d99`` in
``replication.json``, the analysis plan's contrast for random search, the excess over the perfect emulator at 1,000 minus
at budget 1, paired by instance, on all 120 cities and on the 40 (``budget_contrast_d99``).

Outputs in ``results/analysis/``: ``pairs.csv`` (one row per pair; ``missing`` lists what is absent),
``main_claim.md`` / ``.json``, ``replication.md`` / ``.json`` (the main checkpoint's headline on the 40, the 80
and the 120 cities), ``coverage.md`` / ``.json`` (the coverage model against the main model), ``fig5_*.csv`` (the
data the section-5 figures need) and ``inputs_manifest.json`` (every file read, with its sha256). Every output
says whether it is *partial* or *complete*.

The statistics are fixed by the specification, its round 2, the study protocol (section 1; amendments 3, 4, 7) and
the analysis plan. Correlations: ``hpr_dream.stats`` estimators, cluster bootstrap, 2,000 resamples, seed 0,
percentile intervals (the within-family statistics resample with the same draws,
``hpr_dream.stats.cluster_draws``). Audit measurements (replication, coverage): the same estimators with BCa
intervals and the percentile interval where BCa is undefined, the convention of the audit's reference tables
(protocol).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import multiprocessing as mp
import re
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "hpr-dream"))

import numpy as np  # noqa: E402
from scipy import stats as sps  # noqa: E402
from scipy.special import ndtr, ndtri  # noqa: E402

import hpr_dream.stats as hs  # noqa: E402
from dc import audit as A  # noqa: E402  (ACCEPT_P, read_records; no engine is loaded)
from dc import tasks as T  # noqa: E402  (TASKS)

_DEFAULT_CKPT_ROOT = Path("<cache>/ckpt/ladder_v2")
CKPT_ROOT = _DEFAULT_CKPT_ROOT if _DEFAULT_CKPT_ROOT.is_dir() else ROOT / "paper" / "data" / "ckpt_meta"
TASKS_40 = ROOT / "data" / "tasks_v2_H24.json"
TASKS_80 = ROOT / "data" / "tasks_v2x_H24.json"
ENGINE_REF = ROOT / "results" / "audit" / "engine_reference"
COV_FIDELITY_FALLBACK = Path("<home>/development/wm2-ladder-v2-cov")   # the coverage model's checkout
COV_RL_FALLBACK = Path("<home>/development/wm2-fleet")                # where its RL runs are produced

FAMILIES = tuple(T.TASKS)                      # grow, solvent, treasury, recover, power
METHODS = ("random", "cem_seeded")             # the audit's searches 
COVERAGE_METHODS = ("random", "best_of_n", "cem_seeded")
METHOD_DIR_SUFFIX = {"random": "", "best_of_n": "", "cem_seeded": "_cem_seeded"}
REF_NAME = {"random": "B_economy", "best_of_n": "B_economy", "cem_seeded": "cem_seeded_B_economy"}
SETS = ("c40", "c80")                          # the two city files
POOLED = "c120"                                # both pooled
ALL_SETS = (POOLED,) + SETS                    # the primary first 
SET_DESC = {"c40": "the 40 cities", "c80": "the 80 new cities", "c120": "all 120 cities"}
BUDGETS = (10, 100, 1000)
SNAPSHOTS = (250_000, 500_000, 1_000_000)     # the RL arm's evaluations (protocol)
RL_SEEDS = (0, 1, 2)                           # three RL seeds per pair (protocol)
RL_VARIANT = "frozen"                          # the RL arm's primary learner 
LADDER_SIZE = 24                               # protocol
MAIN_RUN, MAIN_SAMPLES = "os_50m_full", 6_000_000   # the main checkpoint (amendment 4)
COV_RUN, COV_SAMPLES = "os_50m_cov", 6_000_000      # the coverage model 
THRESHOLD = 0.4                                # the main claim's decision value (protocol)
SECONDARY_ABS = 0.3                            # the secondary claim's |Spearman| bound (protocol)
POWER_ICCS = (0.3, 0.5)                        # the intra-checkpoint correlations of the protocol's power statement
MIN_FAMILY_PAIRS = 3                           # a family enters a within-family statistic with at least 3 pairs
LADDER_RUN = re.compile(r"(os|sf)_\d+m_(full|small)")   # one-step and self-forced runs; ensemble members excluded
FIDELITY_METRICS = (
    ("f1_1m", "tile_F1_1m_structural_T1", "structural changed-tile F1, one month"),
    ("f1_since_start_12m", "tile_F1_since_start_12m_structural", "structural changed-since-start tile F1, 12 months"),
    ("funds_medrel_12m", "funds_median_rel_12m", "funds, median relative error, 12 months"),
    ("pop_medrel_12m", "pop_median_rel_12m", "population, median relative error, 12 months"),
)
RL_FIELDS = (
    ("inflation", "inflation_open"),
    ("gap", "verdict_gap_open"),
    ("dream_accept", "rate_dream_accept"),
    ("oracle_open_accept", "rate_engine_open_accept"),
    ("closed_accept", "rate_engine_closed_accept"),
)
AUDIT_STATS = ("hack", "judge_accept", "oracle_accept", "false_rejection", "perfect_hack", "diff")
NAN = float("nan")
# The secondary claim's two further fidelity measures .
HELDOUT_X = "fid_test_loglik_elbo"             # onestep.loglik_nats_per_transition.elbo of the test-selection file
HELDOUT_DESC = ("fidelity, test selection (finals only): held-out likelihood, the total bound (ELBO), nats per "
                "transition")
DEC_PLANS = 100                                # the first 100 logged behaviour plans of each instance (the study brief)
DEC_TIE_TOL = 1e-9                             # recovered margins closer than this are one value (see dec_margins)
DEC_X = {s: f"fid_decision_{s}" for s in ALL_SETS}
DEC_DESC = {s: f"fixed-candidate decision fidelity on {SET_DESC[s]} (finals only): mean over instances of the Spearman "
               f"correlation between the emulator's two-sample mean margin and the engine's margin, first {DEC_PLANS} "
               f"behaviour plans" for s in ALL_SETS}
# (cities of the measure, cities of the audit variable, role): random search selects on the same emulator scores, so the
# verdict is read on disjoint cities 
DEC_ROWS = (("c40", "c80", "carries this measure's verdict: fidelity on the 40 cities, false acceptance on the 80 new "
                           "cities "),
            ("c80", "c40", "beside it: the reverse, fidelity on the 80 new cities, false acceptance on the 40"),
            ("c120", "c120", "beside it: the same cities, as the other measures"),
            ("c40", "c40", "beside it: the same cities, as the other measures"),
            ("c80", "c80", "beside it: the same cities, as the other measures"))
DEC_VERDICT_ROW = f"{DEC_X['c40']}|c80"
# The analysis plan: the pool-seeded search's cross-emulator row on the largest complete nested set of checkpoints.
NESTED_SETS = (("all", "all 24 checkpoints", LADDER_SIZE), ("finals", "the 12 final checkpoints", LADDER_SIZE // 2),
               ("full_finals", "the 6 full-data finals", LADDER_SIZE // 4))
SEEDED_X = "cem_seeded_c40_hack_1000"
# The analysis plan : an exploratory comparator, supplementary. E1: the main claim's statistics with random
# search's false acceptance at budget 1 (one logged plan per instance, no search) in place of budget 1,000; E2: the
# paired difference, the statistic at 1,000 minus the statistic at 1 on the same pairs, both on each cluster resample.
E_BUDGET = 1
E_X = {s: f"random_{s}_hack_{E_BUDGET}" for s in ALL_SETS}
E_SEARCH_X = {s: f"random_{s}_hack_1000" for s in ALL_SETS}
E_DESC = {s: f"random search: false acceptance at budget {E_BUDGET} (one logged plan per instance, no search), "
             f"{SET_DESC[s]}" for s in ALL_SETS}
E_WORDING = {   # fixed in the analysis plan, before any 120-city input was complete; read on E2's interval
    "above": "the search adds predictive value beyond a check on logged plans",
    "includes": "the prediction does not need the search: one logged plan per instance, judged by the emulator and "
                "the engine, predicts as well, so the audit cannot be told from a calibration check on logged plans",
    "below": "one logged plan predicts better than the search audit"}
E_SCOPES = (("pooled_spearman_difference", "pooled"), ("within_mean_spearman_difference", "mean of the within-family values"),
            ("ranked_within_spearman_difference", "pooled after ranking within family"))
# The analysis plan : fixed before the 120-city inputs are complete.
D79_N_PERM, D79_PERM_SEED = 2000, 0            # the within-family permutation null of the pooled Spearman
D79_SIM, D79_SIM_BOOT, D79_SIM_SEED = 500, 1000, 0   # power by simulation: simulations per cell, resamples per interval
D79_RHOS = (0.2, 0.3, 0.4, 0.5)                # true within-family Spearman for the within-family reading's power
D79_FALSIFY_RHO, D79_POWER_BAR = 0.5, 0.8      # the secondary claim's power to falsify 
D79_MAIN_WORDING = {"null_above": "exceeds what the differences between task families alone produce",
                    "null_not_above": "is no more than the differences between task families produce",
                    "within_excludes": "within a task family the audit ranks emulators",
                    "within_includes": "does not rank emulators within a task family"}
D79_SEC_WORDING = {"falsified": "falsified", "not_falsified": "not falsified",
                   "not_falsifiable": "not falsified, and not falsifiable at this size"}
# the analysis plan: the four protocol measures and their pooled verdict rows (the twelve-month error has three readings)
D78_MEASURES = (("one-month F1", ("fid_test_f1_1m|c120",)),
                ("twelve-month rollout error", ("fid_test_f1_since_start_12m|c120", "fid_test_funds_medrel_12m|c120",
                                                "fid_test_pop_medrel_12m|c120")),
                ("held-out likelihood", (f"{HELDOUT_X}|c120",)),
                ("fixed-candidate decision fidelity", (DEC_VERDICT_ROW,)))
# Section 5 24-month open-loop trajectory fidelity predictors and 6-lineage cluster bootstrap (20,000 draws).
N_BOOT_CLUSTER_20K = 20_000
HORIZON_24M_METRICS = (
    ("ol_overlay_copy_ratio_24m", "mean 24m spatial overlay copy-ratio (open-loop plans)"),
    ("ol_scalar_copy_ratio_24m", "mean 24m scalar copy-ratio (open-loop plans)"),
    ("ol_powered_zones_mae_24m", "24m open-loop powered-zone count error (MAE)"),
    ("ol_pollution_copy_ratio_24m", "24m open-loop pollution copy-ratio"),
    ("all_overlay_copy_ratio_24m", "mean 24m spatial overlay copy-ratio (all 500 plans, Table 16 scope)"),
    ("all_pollution_copy_ratio_24m", "24m pollution copy-ratio (all 500 plans, Table 16 column)"),
)
HORIZON_24M_TARGETS = (
    ("rl_inflation_1000000", "PPO continuous margin inflation (1,000,000 imagined months)"),
    ("rl_gap_1000000", "PPO pass-rate optimism (1,000,000 imagined months)"),
    ("random_c120_hack_1000", "10^3 random-shooting false acceptance (all 120 cities)"),
)
LINEAGE_6_PREDICTORS = (
    ("random_c120_hack_1000", "10^3 random-shooting false acceptance (all 120 cities)"),
    ("random_c120_hack_1", "single-logged-plan false acceptance (B = 1, all 120 cities)"),
)
LINEAGE_6_TARGETS = (
    ("rl_inflation_1000000", "PPO continuous margin inflation (1,000,000 imagined months)"),
    ("rl_gap_1000000", "PPO pass-rate optimism (1,000,000 imagined months)"),
    ("rl_fa0_1000000", "PPO initial-plan false acceptance (plan0_hackability, 1,000,000 imagined months)"),
)


# ---------------------------------------------------------------------------------------------------------------
# reading


class Reader:
    """Reads JSON / records defensively and keeps a manifest of every file read (path, sha256)."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.manifest: dict[str, str] = {}

    def note(self, path: Path, data: bytes):
        p = Path(path)
        try:
            key = str(p.resolve().relative_to(self.root.resolve()))
        except ValueError:
            key = str(p)
        self.manifest[key] = hashlib.sha256(data).hexdigest()

    def json(self, path: Path):
        """The parsed file, or None if it is absent or cannot be parsed (a file being written)."""
        p = Path(path)
        if not p.is_file():
            return None
        try:
            data = p.read_bytes()
            out = json.loads(data.decode("utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            return None
        self.note(p, data)
        return out

    def records(self, path: Path):
        p = Path(path)
        if not p.is_file():
            return None
        try:
            data = p.read_bytes()
            rows = A.read_records(p)
        except (OSError, EOFError, ValueError):
            return None
        self.note(p, data)
        return rows

    def npz(self, path: Path):
        """The arrays of a ``.npz`` file (read lazily from memory), or None if it is absent or unreadable."""
        p = Path(path)
        if not p.is_file():
            return None
        try:
            data = p.read_bytes()
            z = np.load(io.BytesIO(data), allow_pickle=False)
        except (OSError, ValueError, zipfile.BadZipFile):
            return None
        self.note(p, data)
        return z


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_tasks(path: Path) -> dict:
    t = json.loads(Path(path).read_text())
    fam: dict[str, set] = {}
    for i in t["instances"]:
        fam.setdefault(i["task"], set()).add(f"{i['start_id']}|{i['task']}|H{int(i['horizon'])}")
    if set(fam) != set(FAMILIES):
        raise SystemExit(f"{path}: task families {sorted(fam)} differ from dc.tasks.TASKS {FAMILIES}")
    return {"path": str(path), "stem": Path(path).stem, "sha256": sha256_file(path), "instances": fam,
            "n": {f: len(fam[f]) for f in FAMILIES}}


def make_entry(d: Path, cfg: dict, n: int, path: Path, stage: str) -> dict:
    tr, data = cfg["train"], cfg.get("data", {})
    shaf = path.with_name(path.name + ".sha256")
    sha = shaf.read_text().split()[0] if shaf.is_file() else None
    mode = tr["mode"]
    lineage = d.name if mode == "onestep" else Path(tr.get("init_from", "")).parent.name
    return {"checkpoint": f"{d.name}-samples_{n:09d}", "run": d.name, "samples": n, "path": str(path),
            "sha256": sha, "objective": mode, "size": tr["size"], "data_index": data.get("index"),
            "data_transitions": int(data["index_len"]) if "index_len" in data else None,
            "budget_samples": int(tr["samples"]), "stage": stage, "lineage": lineage or None}


def _saved(d: Path) -> dict:
    files = {}
    for p in d.glob("samples_*.pt"):
        m = re.fullmatch(r"samples_(\d+)\.pt", p.name)
        if m:
            files[int(m.group(1))] = p
    for p in d.glob("samples_*.pt.sha256"):
        m = re.fullmatch(r"samples_(\d+)\.pt\.sha256", p.name)
        if m and int(m.group(1)) not in files:
            files[int(m.group(1))] = d / f"samples_{m.group(1)}.pt"
    return files


def discover_ladder(ckpt_root: Path, rd: Reader) -> tuple[list[dict], list[str]]:
    """The ladder's checkpoints from the training runs' configs: every seed-0 one-step or self-forced run, one
    checkpoint per save fraction (the first file saved at or past fraction x budget and before the next one)."""
    entries, notes = [], []
    if not Path(ckpt_root).is_dir():
        raise SystemExit(f"checkpoint root {ckpt_root} not found: the ladder cannot be enumerated")
    for d in sorted(Path(ckpt_root).iterdir()):
        if not d.is_dir() or not LADDER_RUN.fullmatch(d.name):
            continue
        cfg = rd.json(d / "config.json")
        if cfg is None:
            notes.append(f"{d.name}: no readable config.json")
            continue
        tr = cfg["train"]
        if int(tr.get("seed", 0)) != 0:
            notes.append(f"{d.name}: training seed {tr.get('seed')} (not a ladder rung)")
            continue
        files = _saved(d)
        budget = int(tr["samples"])
        fracs = sorted(float(f) for f in tr.get("save_fracs", []))
        for k, frac in enumerate(fracs):
            hi = fracs[k + 1] * budget if k + 1 < len(fracs) else math.inf
            cands = sorted(n for n in files if frac * budget <= n < hi)
            stage = {0.5: "half", 1.0: "final"}.get(frac, f"{frac:g}")
            if not cands:
                notes.append(f"{d.name}: no checkpoint saved at {frac:g} of {budget} samples")
                continue
            entries.append(make_entry(d, cfg, cands[0], files[cands[0]], stage))
    return entries, notes


def single_entry(ckpt_root: Path, run: str, samples: int, rd: Reader):
    d = Path(ckpt_root) / run
    cfg = rd.json(d / "config.json")
    p = d / f"samples_{samples:09d}.pt"
    if cfg is None or not p.is_file():
        return None
    stage = "final" if samples >= int(cfg["train"]["samples"]) else f"{samples / int(cfg['train']['samples']):g}"
    return make_entry(d, cfg, samples, p, stage)


# ---------------------------------------------------------------------------------------------------------------
# audit


def _rkey(r: dict) -> tuple:
    return (r["instance"], r["method"], int(r["budget"]), int(r["attacker_seed"]))


def _ref_records(path: Path, rd: Reader, cache: dict):
    path = Path(path)
    if path not in cache:
        rows = rd.records(path / "records.jsonl.gz")
        cfg = rd.json(path / "config.json")
        cache[path] = None if rows is None else ({_rkey(r): r for r in rows}, cfg)
    return cache[path]


def read_audit(entry: dict, method: str, tasks: dict, root: Path, ref_root: Path, rd: Reader, ref_cache: dict) -> dict:
    """One checkpoint's audit for one search on one city file: per family and budget the selected plans' verdicts
    as per-instance arrays (``units``), paired with the perfect emulator where it exists, or a status."""
    d = (root / "results" / "audit" / "ladder" / entry["run"] / f"samples_{entry['samples']:09d}"
         / f"{tasks['stem']}{METHOD_DIR_SUFFIX[method]}")
    out = {"dir": str(d.relative_to(root)) if d.is_relative_to(root) else str(d), "status": None, "notes": [],
           "families": {}, "behaviour": {}}
    if not d.is_dir():
        out["status"] = "absent"
        return out
    card = rd.json(d / "card.json")
    recs = rd.records(d / "records.jsonl.gz")
    cfg = rd.json(d / "config.json")
    if card is None or recs is None or cfg is None:
        out["status"] = "incomplete"
        out["notes"].append("no readable card.json, records.jsonl.gz or config.json (a run in progress)")
        return out
    if cfg.get("config", {}).get("tasks_sha256") != tasks["sha256"]:
        out["status"] = "other tasks file"
        return out
    judge_sha = (card.get("meta") or {}).get("judge", {}).get("ckpt_sha256")
    if entry["sha256"] and judge_sha and judge_sha != entry["sha256"]:
        out["status"] = "checkpoint sha256 differs"
        return out
    if any(r.get("oracle_rule") != "majority" for r in recs):
        out["status"] = "not judged by the majority oracle"
        return out
    R = {_rkey(r): r for r in recs}
    if len(R) != len(recs):
        out["status"] = "duplicate records"
        return out
    mine = [r for r in recs if r["method"] == method]
    if not mine:
        out["status"] = f"no {method} records"
        return out
    # the card's all-instance false acceptance must equal the records' (what compare_reference checks)
    card_h = {(e["attacker"], e["scoring"], int(e["budget"])): e["hackability"]["value"]
              for e in card.get("hackability_curve", []) or []}
    budgets = sorted({int(r["budget"]) for r in mine})
    for B in budgets:
        rs = [r for r in mine if int(r["budget"]) == B]
        h = float(np.mean([r["grader_p"] >= A.ACCEPT_P and not r["oracle_accept"] for r in rs]))
        cv = card_h.get((rs[0]["attacker"], rs[0]["scoring"], B))
        if cv is not None and not np.isclose(cv, h, rtol=0, atol=1e-12):
            out["status"] = f"records disagree with card.json at B={B}"
            return out
    # the perfect emulator: the reference the run was compared with, else the default for this file and search
    refj = rd.json(d / "reference.json")
    ref_dir = Path(refj["reference"]) if refj and refj.get("reference") else Path(ref_root) / tasks["stem"] / REF_NAME[method]
    if str(ref_dir).startswith("<repo>/"):
        ref_dir = root / str(ref_dir)[len("<repo>/"):]
    elif not ref_dir.is_absolute():
        ref_dir = root / ref_dir
    ref = _ref_records(ref_dir, rd, ref_cache)
    ref_ok = ref is not None and (ref[1] or {}).get("config", {}).get("tasks_sha256") == tasks["sha256"]
    out["reference"] = str(ref_dir)
    if not ref_ok:
        out["notes"].append(f"perfect-emulator reference {ref_dir} absent, unreadable or on another tasks file")
    F = ref[0] if ref_ok else {}
    for f in FAMILIES:
        expected = tasks["instances"][f]
        fam = {}
        for B in budgets:
            rs = sorted((r for r in mine if r["task"] == f and int(r["budget"]) == B), key=_rkey)
            got = {r["instance"] for r in rs}
            if got != expected or len({int(r["attacker_seed"]) for r in rs}) != 1:
                fam[B] = {"status": f"{len(got & expected)}/{len(expected)} instances", "n": len(rs)}
                continue
            keys = [_rkey(r) for r in rs]
            u = {"status": "ok", "n": len(rs), "keys": keys, "cl": [r["cluster"] for r in rs],
                 "ga": np.array([r["grader_p"] >= A.ACCEPT_P for r in rs]),
                 "oa": np.array([bool(r["oracle_accept"]) for r in rs]), "gr": None, "orr": None,
                 "n_paired": sum(1 for k in keys if k in F)}
            if u["n_paired"] == len(keys):
                for k in keys:
                    if F[k]["task"] != R[k]["task"] or F[k]["cluster"] != R[k]["cluster"]:
                        raise SystemExit(f"{d}: {k}: the run and the reference disagree on the instance")
                u["gr"] = np.array([F[k]["grader_p"] >= A.ACCEPT_P for k in keys])
                u["orr"] = np.array([bool(F[k]["oracle_accept"]) for k in keys])
            fam[B] = u
        out["families"][f] = fam
    # cross-check against the run's reference.json where it exists
    if refj:
        agree, differ = 0, []
        for f in FAMILIES:
            for g in refj.get("subsets", {}).get(f"task:{f}", {}).get("groups", []):
                if g.get("method") != method or "emulator" not in g:
                    continue
                u = out["families"][f].get(int(g["budget"]), {})
                if u.get("status") != "ok" or g.get("n_paired") != u["n"]:
                    continue
                v = summarise(u)
                pairs = [("hack", g["emulator"]["hackability"]["value"]),
                         ("judge_accept", g["emulator"]["judge_accept"]["value"]),
                         ("oracle_accept", g["emulator"]["oracle_accept"]["value"]),
                         ("perfect_hack", g["perfect_emulator"]["hackability"]["value"]),
                         ("diff", g["difference"]["value"])]
                for name, val in pairs:
                    if np.isfinite(v.get(name, NAN)) and np.isclose(v[name], val, rtol=0, atol=1e-12):
                        agree += 1
                    else:
                        differ.append(f"{f} B={g['budget']} {name}: {v.get(name)} vs {val}")
        out["reference_json_check"] = {"agree": agree, "differ": differ}
        if differ:
            out["notes"].append(f"reference.json disagrees with the records in {len(differ)} values")
    # behaviour plans: rates within the family (pool_stats.json of a run with floors)
    ps = rd.json(d / "pool_stats.json")
    bt = ((ps or {}).get("flip_rates") or {}).get("by_task") or {}
    for f in FAMILIES:
        if f in bt:
            b = bt[f]
            out["behaviour"][f] = {"false_rejection": float(b["fn"]), "false_acceptance": float(b["fp"]),
                                   "n_oracle_accept": int(b["n_oracle_accept"]),
                                   "n_oracle_reject": int(b["n_oracle_reject"])}
    out["status"] = "ok"
    return out


def summarise(u: dict) -> dict:
    """A unit set's audit values: rates over its instances; the excess where every instance is paired."""
    ga, oa = u["ga"], u["oa"]
    v = {"n": int(ga.size), "n_paired": int(u["n_paired"]), "hack": float(np.mean(ga & ~oa)),
         "judge_accept": float(ga.mean()), "oracle_accept": float(oa.mean()), "n_oracle_accept": int(oa.sum()),
         "false_rejection": float(np.mean(~ga[oa])) if oa.any() else NAN, "perfect_hack": NAN, "diff": NAN}
    if u.get("gr") is not None:
        hr = u["gr"] & ~u["orr"]
        v["perfect_hack"] = float(hr.mean())
        v["diff"] = float(np.mean((ga & ~oa).astype(float) - hr.astype(float)))
    return v


def pool_units(units: list) -> dict | None:
    """Instances of several unit sets taken together (None unless every set is complete); paired only if every
    set is paired."""
    if not units or any(u is None or u.get("status") != "ok" for u in units):
        return None
    paired = all(u.get("gr") is not None for u in units)
    return {"status": "ok", "n": sum(u["n"] for u in units), "keys": [k for u in units for k in u["keys"]],
            "cl": [c for u in units for c in u["cl"]], "ga": np.concatenate([u["ga"] for u in units]),
            "oa": np.concatenate([u["oa"] for u in units]),
            "gr": np.concatenate([u["gr"] for u in units]) if paired else None,
            "orr": np.concatenate([u["orr"] for u in units]) if paired else None,
            "n_paired": sum(u["n_paired"] for u in units)}


def ref_budgets(aud: dict, method: str, ref_cache: dict) -> set:
    """The budgets the run's perfect-emulator reference holds for ``method`` (the seeded reference has no B = 1 by
    design: an unpaired budget there is not a missing input)."""
    ref = ref_cache.get(Path(aud["reference"])) if aud.get("reference") else None
    return {k[2] for k in ref[0] if k[1] == method} if ref else set()


NOT_RUN_AT_B = "the perfect emulator was not run at this budget"


def pairing_status(B: int, budget_sets: list) -> str:
    """Why units are not paired with the perfect emulator: its run is absent (a missing input), it holds no run at
    this budget (by design), or it lacks some of the run's instances (a missing input)."""
    if any(not b for b in budget_sets):
        return "perfect-emulator reference absent"
    if any(B not in b for b in budget_sets):
        return NOT_RUN_AT_B
    return "not paired with the perfect emulator on every instance"


def units_all_families(aud: dict, B: int) -> dict | None:
    """One budget's units over every family of a run (None if any family is incomplete)."""
    if aud is None or aud.get("status") != "ok":
        return None
    return pool_units([aud["families"].get(f, {}).get(B) for f in FAMILIES])


# ---------------------------------------------------------------------------------------------------------------
# RL and fidelity


def read_rl(entry: dict, family: str, roots: list, tasks: dict, rd: Reader) -> dict:
    """The pair's RL runs: per snapshot, the values of each seed with a valid summary. ``roots``: trees searched in
    order for ``results/rl/<run>`` (the first holding the run directory is used)."""
    out = {"seeds": {m: {} for m in SNAPSHOTS}, "fa0_seeds": {m: {} for m in SNAPSHOTS}, "notes": [], "source": {}}
    for s in RL_SEEDS:
        name = f"{entry['checkpoint']}__{family}__s{s}__{tasks['stem']}"
        d = next((Path(r) / "results" / "rl" / name for r in roots if (Path(r) / "results" / "rl" / name).is_dir()), None)
        if d is None:
            continue
        cfg = rd.json(d / "config.json")
        meta = (cfg or {}).get("meta", {})
        bad = []
        if meta.get("environment") != "emulator":
            bad.append("environment")
        if meta.get("task") != family or int(meta.get("rl_seed", -1)) != s:
            bad.append("task or seed")
        if meta.get("checkpoint") != entry["path"]:
            bad.append("checkpoint path")
        if entry["sha256"] and meta.get("checkpoint_sha256") != entry["sha256"]:
            bad.append("checkpoint sha256")
        if meta.get("variant") != RL_VARIANT:
            bad.append(f"variant {meta.get('variant')}")
        if meta.get("tasks_sha256") != tasks["sha256"]:
            bad.append("tasks file")
        if set(meta.get("instances", [])) != tasks["instances"][family]:
            bad.append("instances")
        if bad:
            out["notes"].append(f"{name}: config differs ({', '.join(bad)}); not used")
            continue
        out["source"][s] = str(d.parents[2])
        for m in SNAPSHOTS:
            sm = rd.json(d / f"eval3_{m:09d}.summary.json")
            if sm is None:
                continue
            if int(sm.get("eval_version", -1)) != 3 or int(sm.get("months", -1)) != m or \
                    int(sm.get("n_instances", -1)) != tasks["n"][family]:
                out["notes"].append(f"{name}: eval3_{m:09d} summary has another version, month count or instance count")
                continue
            vals = {key: (NAN if sm.get(field) is None else float(sm[field])) for key, field in RL_FIELDS}
            if not np.isclose(vals["gap"], vals["dream_accept"] - vals["oracle_open_accept"], rtol=0, atol=1e-9):
                out["notes"].append(f"{name}: eval3_{m:09d} gap differs from dream minus oracle acceptance")
                continue
            out["seeds"][m][s] = vals
            fa0 = sm.get("plan0_hackability")
            if fa0 is not None and np.isfinite(float(fa0)):
                out["fa0_seeds"][m][s] = float(fa0)
    return out


def rl_aggregate(rl: dict) -> dict:
    out = {}
    for mo in SNAPSHOTS:
        got = rl["seeds"][mo]
        out[f"rl_n_seeds_{mo}"] = len(got)
        out[f"rl_seeds_{mo}"] = ";".join(str(s) for s in sorted(got))
        for key, _ in RL_FIELDS:
            vals = np.array([got[s][key] for s in sorted(got)], dtype=float)
            out[f"rl_{key}_{mo}"] = float(vals.mean()) if vals.size else NAN
            out[f"rl_{key}_sd_{mo}"] = float(vals.std(ddof=1)) if vals.size >= 2 else NAN
    return out


def read_fidelity(entry: dict, split: str, roots: list, rd: Reader) -> dict:
    """``roots``: trees searched in order for ``results/fidelity/ladder/<run>/<split>``."""
    for r in roots:
        d = Path(r) / "results" / "fidelity" / "ladder" / entry["run"] / split
        files = sorted(d.glob(f"{entry['run']}_samples_{entry['samples']:09d}_dec-*.json")) if d.is_dir() else []
        files = [p for p in files if re.fullmatch(rf"{re.escape(entry['run'])}_samples_\d+_dec-[A-Za-z0-9]+\.json", p.name)]
        if files:
            break
    else:
        return {"status": "absent"}
    if len(files) > 1:
        return {"status": f"{len(files)} decodings ({', '.join(p.name for p in files)})"}
    j = rd.json(files[0])
    if j is None:
        return {"status": "unreadable"}
    if int(j.get("samples", -1)) != entry["samples"]:
        return {"status": "sample count differs"}
    if entry["sha256"] and j.get("checkpoint_sha256") and j["checkpoint_sha256"] != entry["sha256"]:
        return {"status": "checkpoint sha256 differs"}
    gc = j.get("gap_closed", {})
    vals, floor = {}, {}
    for key, field, _ in FIDELITY_METRICS:
        v = gc.get(field, {})
        vals[key] = NAN if v.get("model") is None else float(v["model"])
        floor[key] = NAN if v.get("floor") is None else float(v["floor"])
    return {"status": "ok", "file": str(files[0]), "values": vals, "engine_yardstick": floor}


def read_heldout_loglik(fid_test: dict, rd: Reader) -> tuple[float, str]:
    """Held-out likelihood : the total bound in nats per transition, ``onestep.loglik_nats_per_transition``
    field ``elbo`` (``dc.model``: reconstruction minus KL), of the test-selection file ``read_fidelity`` accepted."""
    if fid_test.get("status") != "ok":
        return NAN, f"test selection {fid_test.get('status')}"
    j = rd.json(Path(fid_test["file"]))
    v = (((j or {}).get("onestep") or {}).get("loglik_nats_per_transition") or {}).get("elbo")
    if v is None or not np.isfinite(float(v)):
        return NAN, "no onestep.loglik_nats_per_transition.elbo in the test-selection file"
    return float(v), "ok"


# Fixed-candidate decision fidelity . What an audit stores (``run_audit.py`` writing ``pools.npz``;
# ``dc.audit.Audit.phase1`` and ``_pool``): ``<instance>__residual_pool_behaviour`` (R = 1,000 rows, the instance's
# first R behaviour plans), column 0 = the emulator's mean margin over its K = 2 search samples (``prop_score``, the
# scores random search selects on) minus the engine's mean margin over the instance's nine residual seeds (primary and
# eight secondary, ``engine_margins9``); ``<instance>__behaviour_engine_margin`` (the first 100 plans) = the majority
# oracle's margin (``majority_margin`` over the oracle seeds). The nine-seed mean is not stored by the audit itself, but
# it is the engine's alone (the plan, the instance's seeds; no emulator): every run with the calibrated residual draw
# stores, on the same rows, the truth-seed pool mean m (``__truth_pool_mean_behaviour``) and the truth residual
# (``__truth_residual_pool_behaviour``, column 0 = the same K = 2 score minus m), so the nine-seed mean is
# m + truth residual - residual. The engine-reference runs on a city file that store m give it; the emulator's
# two-sample margin of a ladder audit is its residual plus that mean, checked on every random-search record (the
# recovered margin of the selected row equals the record's ``grader_score``).
DEC_RES, DEC_ENG, DEC_GP = "__residual_pool_behaviour", "__behaviour_engine_margin", "__behaviour_grader_p"
DEC_TMEAN, DEC_TRES = "__truth_pool_mean_behaviour", "__truth_residual_pool_behaviour"
DEC_CHECK_TOL = 1e-9


def nine_seed_means(ref_root: Path, tasks: dict, rd: Reader) -> dict:
    """The engine's nine-seed mean margin of every instance's first R behaviour plans on one city file, from the
    engine-reference runs that store the truth-seed pool mean (the first in name order; every other one must agree)."""
    base = Path(ref_root) / tasks["stem"]
    found, notes = [], []
    for d in sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []:
        f = d / "pools.npz"
        try:
            with zipfile.ZipFile(f) as zf:
                if not any(n.endswith(DEC_TMEAN + ".npy") for n in zf.namelist()):
                    continue
        except (OSError, zipfile.BadZipFile):
            continue
        cfg = rd.json(d / "config.json")
        if (cfg or {}).get("config", {}).get("tasks_sha256") != tasks["sha256"]:
            notes.append(f"{d.name}: another tasks file")
            continue
        z = rd.npz(f)
        if z is None:
            notes.append(f"{d.name}: pools.npz unreadable")
            continue
        m9, bad = {}, []
        for k in sorted(set().union(*tasks["instances"].values())):
            st = k.replace("|", "__")
            if st + DEC_TMEAN not in z.files:
                bad.append(k)
                continue
            m9[k] = z[st + DEC_TMEAN] + z[st + DEC_TRES][:, 0] - z[st + DEC_RES][:, 0]
        if bad:
            notes.append(f"{d.name}: {len(bad)} instances without the truth-seed pool mean")
            continue
        found.append((d, m9))
    if not found:
        return {"status": f"no run under {base} stores the truth-seed pool mean ({DEC_TMEAN.strip('_')}) of every "
                          f"instance, from which the engine's nine-seed mean follows: the emulator's two-sample margins "
                          f"cannot be recovered from the audits' residuals", "notes": notes}
    d0, m0 = found[0]
    diff = max((float(np.max(np.abs(m[k] - m0[k]))) for _, m in found[1:] for k in m0), default=0.0)
    out = {"status": "ok", "source": str(d0), "cross_checked_with": [str(d) for d, _ in found[1:]],
           "max_abs_difference_between_sources": diff, "notes": notes, "m9": m0}
    if diff > DEC_CHECK_TOL:
        out["status"] = f"the runs storing the truth-seed pool mean disagree on the nine-seed mean (up to {diff:.3g})"
    return out


def dec_margins(v: np.ndarray, tol: float = DEC_TIE_TOL) -> tuple[np.ndarray, float, float]:
    """Recovered margins with the recovery's floating-point error removed from the ranking: sorted values closer than
    ``tol`` to their predecessor take its group's first value (the emulator's own margins tie exactly where two plans
    give the same scores; the residual plus the nine-seed mean reproduces them only to a few ulp). Returns (values, the
    largest gap merged, the smallest gap kept)."""
    v = np.asarray(v, float)
    order = np.argsort(v, kind="mergesort")
    s = v[order]
    d = np.diff(s)
    new = np.r_[True, d > tol]
    out = np.empty_like(v)
    out[order] = s[new][np.cumsum(new) - 1]
    merged = d[(d > 0) & (d <= tol)]
    kept = d[d > tol]
    return out, float(merged.max()) if merged.size else 0.0, float(kept.min()) if kept.size else math.inf


def _auc(a: np.ndarray, b: np.ndarray) -> float:
    """P(a value of ``a`` exceeds one of ``b``), ties counted half (Mann-Whitney)."""
    r = midrank(np.concatenate([a, b]))
    return float((r[:a.size].sum() - a.size * (a.size + 1) / 2) / (a.size * b.size))


def decision_fidelity(aud: dict, tasks: dict, root: Path, rd: Reader, m9src: dict) -> dict:
    """One checkpoint's fixed-candidate decision fidelity on one city file : per instance, Spearman's
    rho between the emulator's mean margin over its two search samples and the engine's (majority oracle's) margin on
    the instance's first ``DEC_PLANS`` behaviour plans; the mean over the instances where neither side is constant.
    Read from the random-search audit's ``pools.npz``; the recovery is checked on every random-search record."""
    out = {"status": None, "cities": tasks["stem"]}
    if m9src.get("status") != "ok":
        out["status"] = f"not computable: {m9src.get('status')}"
        return out
    if aud.get("status") != "ok":
        out["status"] = f"random-search audit {aud.get('status')}"
        return out
    d = Path(root) / aud["dir"]
    z = rd.npz(d / "pools.npz")
    recs = rd.records(d / "records.jsonl.gz")
    cfg = rd.json(d / "config.json")
    if z is None or recs is None or cfg is None:
        out["status"] = "pools.npz, records.jsonl.gz or config.json absent or unreadable"
        return out
    out["file"] = str((d / "pools.npz").relative_to(root)) if (d / "pools.npz").is_relative_to(root) else str(d)
    m9 = m9src["m9"]
    rho, per_f, merged, kept = {}, {}, 0.0, math.inf
    n_const = {"emulator": 0, "engine": 0, "both": 0}
    second = {"acc": [], "rej": [], "auc": []}
    for f in FAMILIES:
        vals = []
        for k in sorted(tasks["instances"][f]):
            st = k.replace("|", "__")
            if st + DEC_RES not in z.files or st + DEC_ENG not in z.files or k not in m9:
                out["status"] = f"{k}: pools.npz holds no residual pool or engine margin"
                return out
            res, eng = z[st + DEC_RES], z[st + DEC_ENG]
            if res.shape[0] < DEC_PLANS or eng.shape[0] < DEC_PLANS or m9[k].shape[0] < DEC_PLANS:
                out["status"] = f"{k}: fewer than {DEC_PLANS} behaviour plans stored"
                return out
            emu = res[:DEC_PLANS, 0] + m9[k][:DEC_PLANS]
            e = np.asarray(eng[:DEC_PLANS], float)
            if not (np.all(np.isfinite(emu)) and np.all(np.isfinite(e))):
                out["status"] = f"{k}: non-finite margins among the first {DEC_PLANS} plans"
                return out
            emu, mg, kp = dec_margins(emu)
            merged, kept = max(merged, mg), min(kept, kp)
            ce, cg = np.ptp(emu) == 0, np.ptp(e) == 0
            if ce or cg:
                n_const["both" if ce and cg else ("emulator" if ce else "engine")] += 1
                rho[k] = None
            else:
                rho[k] = spearman(emu, e)
                vals.append(rho[k])
            if st + DEC_GP in z.files:          # the audit's second reading of the same plans: 8 fresh samples
                gp = np.asarray(z[st + DEC_GP][:DEC_PLANS], float)
                if gp.size == DEC_PLANS and np.all(np.isfinite(gp)):
                    acc = gp >= A.ACCEPT_P
                    second["acc"] += list(emu[acc])
                    second["rej"] += list(emu[~acc])
                    if acc.any() and (~acc).any():
                        second["auc"].append(_auc(emu[acc], emu[~acc]))
        per_f[f] = {"value": float(np.mean(vals)) if vals else NAN, "n_defined": len(vals),
                    "n_left_out": len(tasks["instances"][f]) - len(vals)}
    # the recovery on every random-search record: the selected row's recovered margin is the record's grader_score
    s0 = int((cfg.get("config") or {}).get("search_seeds", [0])[0])
    errs = []
    for r in recs:
        if r.get("method") != "random" or int(r["attacker_seed"]) != s0:
            continue
        k, j, gs = r["instance"], r.get("best_index"), r.get("grader_score")
        st = k.replace("|", "__")
        if j is None or gs is None or k not in m9 or st + DEC_RES not in z.files or int(j) >= z[st + DEC_RES].shape[0]:
            errs.append(math.inf)
            continue
        errs.append(abs(float(z[st + DEC_RES][int(j), 0] + m9[k][int(j)]) - float(gs)))
    out["recovery_check"] = {"n_records": len(errs), "max_abs_error": max(errs) if errs else NAN,
                             "tolerance": DEC_CHECK_TOL, "source": m9src["source"],
                             "description": "random-search records (every budget): the selected row's residual plus "
                                            "the nine-seed mean against the record's grader_score"}
    out["ties"] = {"tolerance": DEC_TIE_TOL, "largest_gap_merged": merged, "smallest_gap_kept": kept}
    if not errs or max(errs) > DEC_CHECK_TOL:
        out["status"] = (f"recovery check failed on {sum(e > DEC_CHECK_TOL for e in errs)} of {len(errs)} random-search "
                         f"records" if errs else "no random-search record to check the recovery on")
        return out
    if second["auc"]:
        out["second_reading_check"] = {
            "description": f"instances whose first {DEC_PLANS} plans have the audit's 8-sample pass share "
                           f"(behaviour_grader_p): the recovered margin of plans the emulator accepts (share >= "
                           f"{A.ACCEPT_P}) against those it rejects",
            "n_plans_accepted": len(second["acc"]), "n_plans_rejected": len(second["rej"]),
            "mean_margin_accepted": float(np.mean(second["acc"])), "mean_margin_rejected": float(np.mean(second["rej"])),
            "n_instances_with_both": len(second["auc"]), "mean_auc": float(np.mean(second["auc"])),
            "n_instances_auc_above_half": int(sum(a > 0.5 for a in second["auc"]))}
    defined = [v for v in rho.values() if v is not None]
    out.update({"status": "ok", "value": float(np.mean(defined)) if defined else NAN, "n_instances": len(rho),
                "n_defined": len(defined), "n_left_out": len(rho) - len(defined), "left_out_constant": n_const,
                "per_family": per_f, "_rho": rho})
    return out


def pool_decision(parts: list) -> dict:
    """The decision fidelity of several city files taken together: the mean over the instances of both."""
    if any(p.get("status") != "ok" for p in parts):
        return {"status": "; ".join(f"{p.get('cities')}: {p.get('status')}" for p in parts if p.get("status") != "ok")}
    rho = {k: v for p in parts for k, v in p["_rho"].items()}
    defined = [v for v in rho.values() if v is not None]
    return {"status": "ok", "value": float(np.mean(defined)) if defined else NAN, "n_instances": len(rho),
            "n_defined": len(defined), "n_left_out": len(rho) - len(defined),
            "left_out_constant": {k: sum(p["left_out_constant"][k] for p in parts) for k in ("emulator", "engine", "both")}}


# ---------------------------------------------------------------------------------------------------------------
# pairs


def _f(x):
    return NAN if x is None else float(x)


def gather(root: Path, ckpt_root: Path, tasks_paths: dict, ref_root: Path):
    """Every pair's row, the ladder, the per-checkpoint audits (kept for the replication), the reading notes and
    the manifest."""
    root = Path(root)
    rd = Reader(root)
    tasks = {s: load_tasks(tasks_paths[s]) for s in SETS}
    for s in SETS:
        rd.note(Path(tasks_paths[s]), Path(tasks_paths[s]).read_bytes())
    for f in FAMILIES:
        if tasks["c40"]["instances"][f] & tasks["c80"]["instances"][f]:
            raise SystemExit(f"the two city files share instances of {f}: they cannot be pooled")
    ladder, notes = discover_ladder(ckpt_root, rd)
    ref_cache: dict = {}
    rows, per_ckpt, audits = [], [], {}
    rl_fa0_1000000: dict[str, float] = {}
    m9src = {s: nine_seed_means(ref_root, tasks[s], rd) for s in SETS}
    for e in ladder:
        aud = {(m, s): read_audit(e, m, tasks[s], root, ref_root, rd, ref_cache) for m in METHODS for s in SETS}
        audits[e["checkpoint"]] = aud
        fid = {sp: read_fidelity(e, sp, [root], rd) for sp in ("dev", "test")}
        # the secondary claim's further measures , on the finals only 
        if e["stage"] == "final":
            ll, ll_status = read_heldout_loglik(fid["test"], rd)
            dec = {s: decision_fidelity(aud[("random", s)], tasks[s], root, rd, m9src[s]) for s in SETS}
            dec[POOLED] = pool_decision([dec["c40"], dec["c80"]])
        else:
            ll, ll_status = NAN, "not entered: the test selection holds finals only"
            dec = {s: {"status": "not entered: finals only "} for s in ALL_SETS}
        ck = {"checkpoint": e["checkpoint"], "audit": {f"{m}_{s}": aud[(m, s)]["status"] for m in METHODS for s in SETS},
              "audit_notes": {f"{m}_{s}": aud[(m, s)]["notes"] for m in METHODS for s in SETS if aud[(m, s)]["notes"]},
              "reference_json_check": {f"{m}_{s}": aud[(m, s)]["reference_json_check"] for m in METHODS for s in SETS
                                       if aud[(m, s)].get("reference_json_check")},
              "fidelity": {sp: fid[sp]["status"] for sp in fid}, "rl_runs_complete": 0, "rl_notes": []}
        for f in FAMILIES:
            row = {k: e[k] for k in ("checkpoint", "run", "objective", "size", "data_index", "data_transitions",
                                     "stage", "samples", "budget_samples", "lineage")}
            row["family"] = f
            row["n_instances_c40"] = tasks["c40"]["n"][f]
            row["n_instances_c80"] = tasks["c80"]["n"][f]
            missing = []
            for m in METHODS:
                for s in SETS:
                    a = aud[(m, s)]
                    if a["status"] != "ok":
                        missing.append(f"audit_{m}_{s}:{a['status']}")
                for B in BUDGETS:
                    us = {s: aud[(m, s)]["families"].get(f, {}).get(B) for s in SETS}
                    us[POOLED] = pool_units([us["c40"], us["c80"]])
                    for s in ALL_SETS:
                        u = us[s]
                        ok = u is not None and u.get("status") == "ok"
                        v = summarise(u) if ok else {}
                        for k in AUDIT_STATS:
                            row[f"{m}_{s}_{k}_{B}"] = _f(v.get(k)) if ok else NAN
                        for k in ("n_oracle_accept", "n", "n_paired"):
                            row[f"{m}_{s}_{k}_{B}"] = v.get(k) if ok else None
                        if s in SETS and aud[(m, s)]["status"] == "ok":
                            if not ok:
                                missing.append(f"audit_{m}_{s}@{B}:{(u or {}).get('status', 'absent')}")
                            elif u["gr"] is None:
                                missing.append(f"excess_{m}_{s}@{B}:{u['n_paired']}/{u['n']} paired")
            b = aud[("random", "c40")]["behaviour"].get(f)
            row["behaviour_false_rejection"] = _f(b["false_rejection"]) if b else NAN
            row["behaviour_n_oracle_accept"] = b["n_oracle_accept"] if b else None
            row["behaviour_false_acceptance"] = _f(b["false_acceptance"]) if b else NAN
            row["behaviour_n_oracle_reject"] = b["n_oracle_reject"] if b else None
            if aud[("random", "c40")]["status"] == "ok" and not b:
                missing.append("behaviour_rates:the run has no floors")
            rl = read_rl(e, f, [root], tasks["c40"], rd)
            ck["rl_notes"] += rl["notes"]
            row["ckpt_sha256"] = e["sha256"]
            row.update(rl_aggregate(rl))
            fa0_got = rl["fa0_seeds"][SNAPSHOTS[-1]]
            rl_fa0_1000000[f"{e['checkpoint']}|{f}"] = (
                float(np.mean([fa0_got[s] for s in sorted(fa0_got)])) if len(fa0_got) == len(RL_SEEDS) else NAN)
            for mo in SNAPSHOTS:
                if len(rl["seeds"][mo]) < len(RL_SEEDS):
                    missing.append(f"rl@{mo}:{len(rl['seeds'][mo])}/{len(RL_SEEDS)} seeds")
            for s in RL_SEEDS:
                v = rl["seeds"][SNAPSHOTS[-1]].get(s)
                row[f"rl_inflation_{SNAPSHOTS[-1]}_s{s}"] = v["inflation"] if v else NAN
                row[f"rl_gap_{SNAPSHOTS[-1]}_s{s}"] = v["gap"] if v else NAN
            ck["rl_runs_complete"] += sum(1 for s in RL_SEEDS if all(s in rl["seeds"][mo] for mo in SNAPSHOTS))
            for sp in ("dev", "test"):
                fv = fid[sp]
                for key, _, _ in FIDELITY_METRICS:
                    row[f"fid_{sp}_{key}"] = fv["values"][key] if fv["status"] == "ok" else NAN
                # the test selection evaluates finals only ; a non-final has nothing missing there
                if fv["status"] != "ok" and (sp == "dev" or e["stage"] == "final"):
                    missing.append(f"fidelity_{sp}:{fv['status']}")
            row["missing"] = ";".join(missing)
            # new columns after every existing one : constant across the checkpoint's families
            row[HELDOUT_X] = ll
            for s in ALL_SETS:
                ok = dec[s].get("status") == "ok"
                row[DEC_X[s]] = dec[s]["value"] if ok else NAN
                row[f"{DEC_X[s]}_n_defined"] = dec[s]["n_defined"] if ok else None
                row[f"{DEC_X[s]}_n_left_out"] = dec[s]["n_left_out"] if ok else None
            # the analysis plan : random search at budget 1, after every existing column; its own missing list
            # (the existing ``missing`` column is left as it was)
            b1_missing = []
            us = {s: aud[("random", s)]["families"].get(f, {}).get(E_BUDGET) for s in SETS}
            us[POOLED] = pool_units([us["c40"], us["c80"]])
            for s in ALL_SETS:
                u = us[s]
                ok = u is not None and u.get("status") == "ok"
                v = summarise(u) if ok else {}
                for k in AUDIT_STATS:
                    row[f"random_{s}_{k}_{E_BUDGET}"] = _f(v.get(k)) if ok else NAN
                for k in ("n_oracle_accept", "n", "n_paired"):
                    row[f"random_{s}_{k}_{E_BUDGET}"] = v.get(k) if ok else None
                if s in SETS:
                    if aud[("random", s)]["status"] != "ok":
                        b1_missing.append(f"audit_random_{s}:{aud[('random', s)]['status']}")
                    elif not ok:
                        b1_missing.append(f"audit_random_{s}@{E_BUDGET}:{(u or {}).get('status', 'absent')}")
                    elif u["gr"] is None:
                        b1_missing.append(f"excess_random_{s}@{E_BUDGET}:{u['n_paired']}/{u['n']} paired")
            row[f"missing_budget_{E_BUDGET}"] = ";".join(b1_missing)
            rows.append(row)
        ck["heldout_loglik"] = ll_status
        ck["decision_fidelity"] = {s: {k: v for k, v in dec[s].items() if k != "_rho"} for s in ALL_SETS}
        per_ckpt.append(ck)
    sources = {s: {k: v for k, v in m9src[s].items() if k != "m9"} for s in SETS}
    return {"rows": rows, "ladder": ladder, "ladder_notes": notes, "checkpoints": per_ckpt, "tasks": tasks,
            "audits": audits, "reader": rd, "ref_cache": ref_cache, "nine_seed_mean_sources": sources, "m9src": m9src,
            "rl_fa0_1000000": rl_fa0_1000000}


# ---------------------------------------------------------------------------------------------------------------
# statistics


def midrank(a: np.ndarray) -> np.ndarray:
    """Ranks 1..n with ties at their mean rank (``scipy.stats.rankdata(method="average")``, without its
    per-call overhead)."""
    a = np.asarray(a, float)
    n = a.size
    order = np.argsort(a, kind="mergesort")
    s = a[order]
    new = np.r_[True, s[1:] != s[:-1]]
    dense = np.cumsum(new)
    start = np.r_[np.flatnonzero(new), n]
    out = np.empty(n)
    out[order] = 0.5 * (start[dense - 1] + start[dense] - 1) + 1
    return out


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman's rho (mid-ranks): Pearson's r of the ranks; NaN when either ranking is constant (as
    ``hpr_dream.stats.clustered_spearman``)."""
    if x.size < 2 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return NAN
    rx, ry = midrank(x), midrank(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    return float(rx @ ry / math.sqrt((rx @ rx) * (ry @ ry)))


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return NAN
    xc, yc = x - x.mean(), y - y.mean()
    return float(xc @ yc / math.sqrt((xc @ xc) * (yc @ yc)))


def kendall(x: np.ndarray, y: np.ndarray) -> float:
    """Kendall's tau-b (as ``scipy.stats.kendalltau``); NaN when either ranking is constant."""
    if x.size < 2 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return NAN
    iu = np.triu_indices(x.size, 1)
    dx = np.sign(x[:, None] - x[None, :])[iu]
    dy = np.sign(y[:, None] - y[None, :])[iu]
    n0 = dx.size
    den = math.sqrt((n0 - np.count_nonzero(dx == 0)) * (n0 - np.count_nonzero(dy == 0)))
    return float((dx * dy).sum() / den) if den > 0 else NAN


def _encode(clusters) -> tuple[np.ndarray, int]:
    _, codes = np.unique(np.asarray(clusters), return_inverse=True)
    return codes.reshape(-1), int(codes.max()) + 1


def cluster_boot(stat, clusters, n_boot: int, seed: int) -> hs.Estimate:
    """``stat(index array)`` on the units, and on each cluster resample (``hpr_dream.stats.cluster_draws``: the
    same draws as the package's estimators for the same clusters and seed); percentile interval."""
    codes, C = _encode(clusters)
    order = np.argsort(codes, kind="stable")
    bounds = np.concatenate([[0], np.cumsum(np.bincount(codes, minlength=C))])
    mem = [order[bounds[c]:bounds[c + 1]] for c in range(C)]
    value = stat(np.arange(codes.size))
    boot = np.array([stat(np.concatenate([mem[c] for c in d])) for d in hs.cluster_draws(C, n_boot, seed)])
    ok = np.isfinite(boot)
    if ok.any() and np.isfinite(value):
        lo, hi = np.quantile(boot[ok], [(1 - hs.LEVEL) / 2, (1 + hs.LEVEL) / 2])
    else:
        lo = hi = NAN
    return hs.Estimate(float(value), float(lo), float(hi), int(codes.size), int(C), int(n_boot), int((~ok).sum()))


def within_family_mean(x, y, fam, fams_used, fn):
    def stat(ix):
        vals = []
        for f in fams_used:
            sel = ix[fam[ix] == f]
            vals.append(fn(x[sel], y[sel]))
        return float(np.mean(vals)) if vals and np.all(np.isfinite(vals)) else NAN
    return stat


def ranked_within(x, y, fam):
    """Spearman over all units of the within-family percentile ranks (mid-rank - 0.5) / n_family, the ranks
    recomputed on every resample."""
    def stat(ix):
        u, v = [], []
        for f in np.unique(fam[ix]):
            sel = ix[fam[ix] == f]
            u.append((midrank(x[sel]) - 0.5) / sel.size)
            v.append((midrank(y[sel]) - 0.5) / sel.size)
        return spearman(np.concatenate(u), np.concatenate(v)) if u else NAN
    return stat


def excludes_zero(e: hs.Estimate) -> bool | None:
    if e.n_clusters < 2 or not (np.isfinite(e.lo) and np.isfinite(e.hi)):
        return None
    return bool(e.lo > 0 or e.hi < 0)


def corr_block(x, y, family, ckpt, lineage, n_boot: int, seed: int) -> dict:
    """Pooled (checkpoint clusters; lineage clusters as a sensitivity), per family (one point per checkpoint),
    the mean of the within-family values (bootstrap over checkpoints) and the pooled Spearman of within-family
    ranks; Kendall beside Spearman."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    family, ckpt, lineage = np.asarray(family), np.asarray(ckpt), np.asarray(lineage)
    out = {"n_pairs": int(x.size), "n_checkpoints": int(np.unique(ckpt).size) if x.size else 0,
           "n_lineages": int(np.unique(lineage).size) if x.size else 0,
           "n_families": int(np.unique(family).size) if x.size else 0}
    if x.size < 3:
        out["status"] = "fewer than 3 pairs"
        return out
    out["pooled_spearman"] = hs.clustered_spearman(x, y, ckpt, n_boot=n_boot, seed=seed)
    out["pooled_kendall"] = hs.clustered_kendall(x, y, ckpt, n_boot=n_boot, seed=seed)
    out["pooled_spearman_lineage"] = hs.clustered_spearman(x, y, lineage, n_boot=n_boot, seed=seed)
    fam_codes = np.array([FAMILIES.index(f) for f in family])
    per = {}
    for i, f in enumerate(FAMILIES):
        sel = np.flatnonzero(fam_codes == i)
        if sel.size < MIN_FAMILY_PAIRS:
            per[f] = {"n": int(sel.size), "status": f"fewer than {MIN_FAMILY_PAIRS} pairs"}
            continue
        xs, ys, cs = x[sel], y[sel], ckpt[sel]
        per[f] = {"n": int(sel.size),
                  "spearman": cluster_boot(lambda ix: spearman(xs[ix], ys[ix]), cs, n_boot, seed),
                  "kendall": cluster_boot(lambda ix: kendall(xs[ix], ys[ix]), cs, n_boot, seed)}
    out["per_family"] = per
    used = [FAMILIES.index(f) for f in FAMILIES if "spearman" in per[f]]
    out["families_in_mean"] = [FAMILIES[i] for i in used]
    if used:
        out["within_mean_spearman"] = cluster_boot(within_family_mean(x, y, fam_codes, used, spearman), ckpt,
                                                   n_boot, seed)
        out["within_mean_kendall"] = cluster_boot(within_family_mean(x, y, fam_codes, used, kendall), ckpt,
                                                  n_boot, seed)
        out["within_mean_spearman_lineage"] = cluster_boot(within_family_mean(x, y, fam_codes, used, spearman),
                                                           lineage, n_boot, seed)
    out["ranked_within_spearman"] = cluster_boot(ranked_within(x, y, fam_codes), ckpt, n_boot, seed)
    out["ranked_within_spearman_lineage"] = cluster_boot(ranked_within(x, y, fam_codes), lineage, n_boot, seed)
    return out


def decide(e: hs.Estimate) -> str:
    """protocol: supported if the estimate is at least 0.4 and the interval excludes 0; falsified if
    the interval lies below 0.4; otherwise undecided at this power."""
    if e.n_clusters < 2 or not (np.isfinite(e.value) and np.isfinite(e.lo) and np.isfinite(e.hi)):
        return "not computable"
    sup = e.value >= THRESHOLD and (e.lo > 0 or e.hi < 0)
    fal = e.hi < THRESHOLD
    if sup and not fal:
        return "supported"
    if fal and not sup:
        return "falsified"
    return "undecided at this power"


def fisher_power(r: float, n_eff: float, alpha: float = 0.05) -> float:
    """Two-sided power to detect a correlation r with n_eff independent pairs (Fisher z, variance 1 / (n - 3)),
    the approximation behind the protocol's "about 47 independent pairs detect Spearman 0.4 at 80 per cent"."""
    if not np.isfinite(n_eff) or n_eff <= 3:
        return NAN
    z = math.atanh(r) * math.sqrt(n_eff - 3)
    c = float(ndtri(1 - alpha / 2))
    return float(ndtr(z - c) + ndtr(-z - c))


def icc1(values, groups) -> float:
    """One-way random-effects intraclass correlation ICC(1) of ``values`` within ``groups`` (ANOVA estimator,
    unbalanced groups through n0)."""
    v = np.asarray(values, float)
    codes, k = _encode(groups)
    N = v.size
    if k < 2 or N - k < 1:
        return NAN
    n_i = np.bincount(codes, minlength=k).astype(float)
    means = np.bincount(codes, weights=v, minlength=k) / n_i
    msb = float((n_i * (means - v.mean()) ** 2).sum()) / (k - 1)
    msw = float(((v - means[codes]) ** 2).sum()) / (N - k)
    n0 = (N - (n_i ** 2).sum() / N) / (k - 1)
    den = msb + (n0 - 1) * msw
    return float((msb - msw) / den) if den > 0 else NAN


def power_block(n_pairs: int, n_clusters: int) -> dict:
    m = n_pairs / n_clusters if n_clusters else NAN
    out = {"n_pairs": n_pairs, "n_clusters": n_clusters, "pairs_per_cluster": m, "at_icc": {}}
    for icc in POWER_ICCS:
        n_eff = n_pairs / (1 + (m - 1) * icc) if n_clusters else NAN
        out["at_icc"][str(icc)] = {"design_effect": 1 + (m - 1) * icc, "n_eff": n_eff,
                                   "power_spearman_0.4": fisher_power(THRESHOLD, n_eff)}
    out["n_independent_for_80_per_cent"] = math.ceil(((ndtri(0.975) + ndtri(0.8)) / math.atanh(THRESHOLD)) ** 2 + 3)
    return out


def reliability(rows: list[dict], xkey: str, nkey: str, ykeys: list[str]) -> dict:
    """Per family, over the pairs given: the audit variable's binomial standard error per pair (``nkey``: the
    pair's instance count) against its spread across checkpoints, the RL variable's seed standard error (of the
    mean of the seeds) against the same; reliability lambda = 1 - mean(SE^2) / variance across checkpoints; the
    classical attenuation of a correlation, r_observed = r_true x sqrt(lambda_x lambda_y)."""
    out = {}
    for f in FAMILIES:
        fr = [r for r in rows if r["family"] == f]
        e = {"n": len(fr)}
        if len(fr) < 2:
            e["status"] = "fewer than 2 pairs"
            out[f] = e
            continue
        p = np.array([r[xkey] for r in fr], float)
        n = np.array([r[nkey] for r in fr], float)
        se2 = p * (1 - p) / n
        vb = float(np.var(p, ddof=1))
        e["audit"] = {"rms_se": float(math.sqrt(se2.mean())), "sd_between": math.sqrt(vb),
                      "reliability": float(1 - se2.mean() / vb) if vb > 0 else NAN}
        for yk in ykeys:
            mo = SNAPSHOTS[-1]
            base = yk.rsplit(f"_{mo}", 1)[0]
            ybar = np.array([r[yk] for r in fr], float)
            sd = np.array([r[f"{base}_sd_{mo}"] for r in fr], float)
            k = np.array([r[f"rl_n_seeds_{mo}"] for r in fr], float)
            s2 = sd ** 2 / k
            vy = float(np.var(ybar, ddof=1))
            lam_y = float(1 - s2.mean() / vy) if vy > 0 else NAN
            lam_x = e["audit"]["reliability"]
            fac = math.sqrt(max(lam_x, 0.0) * max(lam_y, 0.0)) if np.isfinite(lam_x) and np.isfinite(lam_y) else NAN
            e[yk] = {"rms_seed_se_of_mean": float(math.sqrt(s2.mean())), "rms_seed_sd": float(math.sqrt((sd ** 2).mean())),
                     "sd_between": math.sqrt(vy), "reliability": lam_y, "attenuation_factor": fac,
                     "observed_if_true_0.4": THRESHOLD * fac if np.isfinite(fac) else NAN}
        out[f] = e
    return out


def sb(rho_u: float, k: float) -> float:
    """Spearman-Brown: reliability of a measure of k units of per-unit reliability rho_u."""
    return k * rho_u / (1 + (k - 1) * rho_u)


def sb_from_split(r: float, k1: float, k2: float) -> dict:
    """Parallel forms of unequal length (k1, k2 instances): the correlation of their values across checkpoints is
    r = sqrt(rho(k1) rho(k2)), rho(k) = Spearman-Brown of the per-instance reliability; solved for that (bisection;
    r^2 increases with it), it gives the reliability of each form and of both pooled (k1 + k2)."""
    if not np.isfinite(r) or r <= 0:
        return {"rho_instance": NAN, "rho_k1": NAN, "rho_k2": NAN, "rho_pooled": NAN,
                "status": "correlation <= 0 or undefined: no Spearman-Brown figure"}
    target = min(r, 1.0) ** 2
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if sb(mid, k1) * sb(mid, k2) < target:
            lo = mid
        else:
            hi = mid
    ru = 0.5 * (lo + hi)
    return {"rho_instance": ru, "rho_k1": sb(ru, k1), "rho_k2": sb(ru, k2), "rho_pooled": sb(ru, k1 + k2)}


def binomial_reliability(p: np.ndarray, n: np.ndarray) -> float:
    if p.size < 2:
        return NAN
    vb = float(np.var(p, ddof=1))
    return float(1 - np.mean(p * (1 - p) / n) / vb) if vb > 0 else NAN


def split_sample(rows: list[dict], method: str = "random", B: int = 1000) -> dict:
    """Per family, across the checkpoints with both city files: Spearman and Pearson between a pair's 40-city and
    80-city values; the Spearman-Brown reliability of the 40, the 80 and the pooled 120 from Pearson's r; beside it
    the binomial-formula reliability of each on the same checkpoints."""
    out = {}
    for f in FAMILIES:
        fr = [r for r in rows if r["family"] == f and np.isfinite(r[f"{method}_c40_hack_{B}"])
              and np.isfinite(r[f"{method}_c80_hack_{B}"])]
        e = {"n_checkpoints": len(fr)}
        if len(fr) < MIN_FAMILY_PAIRS:
            e["status"] = f"fewer than {MIN_FAMILY_PAIRS} checkpoints with both city files"
            out[f] = e
            continue
        a = np.array([r[f"{method}_c40_hack_{B}"] for r in fr], float)
        b = np.array([r[f"{method}_c80_hack_{B}"] for r in fr], float)
        n1 = np.array([r[f"{method}_c40_n_{B}"] for r in fr], float)
        n2 = np.array([r[f"{method}_c80_n_{B}"] for r in fr], float)
        p = np.array([r[f"{method}_c120_hack_{B}"] for r in fr], float)
        e["spearman"], e["pearson"] = spearman(a, b), pearson(a, b)
        e["k_c40"], e["k_c80"] = float(np.median(n1)), float(np.median(n2))
        e["spearman_brown"] = sb_from_split(e["pearson"], e["k_c40"], e["k_c80"])
        e["binomial"] = {"c40": binomial_reliability(a, n1), "c80": binomial_reliability(b, n2),
                         "c120": binomial_reliability(p, n1 + n2)}
        out[f] = e
    return out


def _x_vars():
    xs = []
    for m, md in (("random", "random search"), ("cem_seeded", "pool-seeded search")):
        for s in ALL_SETS:
            xs.append((f"{m}_{s}_hack_1000", f"{md}: false acceptance at 1,000, {SET_DESC[s]}"))
    for m, md in (("random", "random search"), ("cem_seeded", "pool-seeded search")):
        for s in ALL_SETS:
            xs.append((f"{m}_{s}_diff_1000", f"{md}: excess over the perfect emulator at 1,000 (paired), {SET_DESC[s]}"))
    xs += [(f"fid_dev_{k}", f"fidelity, development selection: {d}") for k, _, d in FIDELITY_METRICS]
    xs += [(f"fid_test_{k}", f"fidelity, test selection (finals only): {d}") for k, _, d in FIDELITY_METRICS]
    return xs


X_VARS = _x_vars()
PRIMARY_X = f"random_{POOLED}_hack_1000"       # the analysis plan
FID_X = [k for k, _ in X_VARS if k.startswith("fid_")]
Y_VARS = [
    ("rl_inflation_1000000", "RL margin inflation: dream margin minus open-loop engine margin of the same plans at "
                             "1,000,000 months, mean of three seeds (protocol; the main claim is decided on it, "
                             "the analysis plan)"),
    ("rl_gap_1000000", "RL acceptance gap: dream acceptance minus the oracle's open-loop acceptance of the same plans "
                       "at 1,000,000 months, mean of three seeds (reported beside it)"),
]
PRIMARY_Y = Y_VARS[0][0]


def _usable(r: dict, k: str) -> bool:
    """A pair's value enters a statistic when it exists; an RL value only as the mean of all three seeds."""
    if k.startswith("rl_"):
        return r[f"rl_n_seeds_{SNAPSHOTS[-1]}"] == len(RL_SEEDS) and np.isfinite(r[k])
    return np.isfinite(r.get(k, NAN))


_ROWS: list = []


def _block(xk: str, yk: str, n_boot: int, seed: int, rows=None) -> dict:
    rs = [r for r in (_ROWS if rows is None else rows) if _usable(r, xk) and _usable(r, yk)]
    return corr_block([r[xk] for r in rs], [r[yk] for r in rs], [r["family"] for r in rs],
                      [r["checkpoint"] for r in rs], [r["lineage"] for r in rs], n_boot, seed)


def _block_job(args):
    return args[:2], _block(*args)


def compute_blocks(rows: list[dict], wanted: list[tuple], n_boot: int, seed: int, workers: int) -> dict:
    """Every (x, y) correlation block; in ``workers`` processes (fork) when more than one."""
    global _ROWS
    wanted = list(dict.fromkeys(wanted))
    if workers <= 1 or len(wanted) < 2:
        return {(x, y): _block(x, y, n_boot, seed, rows) for x, y in wanted}
    _ROWS = rows
    with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("fork")) as ex:
        out = dict(ex.map(_block_job, [(x, y, n_boot, seed) for x, y in wanted]))
    _ROWS = []
    return out


def analyse(rows: list[dict], n_boot: int = hs.N_BOOT, seed: int = 0, workers: int = 1) -> dict:
    """The fixed statistics of the specification (and its round 2) on the pairs given."""
    prim = [r for r in rows if _usable(r, PRIMARY_X) and _usable(r, PRIMARY_Y)]
    n_ladder = len({r["checkpoint"] for r in rows})
    out = {"n_rows": len(rows), "n_checkpoints_in_rows": n_ladder, "n_boot": n_boot, "seed": seed,
           "primary_x": PRIMARY_X, "primary_y": PRIMARY_Y,
           "n_pairs_primary": len(prim), "n_checkpoints_primary": len({r["checkpoint"] for r in prim})}
    out["status"] = "complete" if (len(prim) == LADDER_SIZE * len(FAMILIES) and n_ladder == LADDER_SIZE) else "partial"
    main_xy = [(f"random_{s}_hack_1000", y) for s in ALL_SETS for y, _ in Y_VARS]
    alt_xy = [(x, y) for x, _ in X_VARS for y, _ in Y_VARS]
    sec_xy = [(x, f"random_{s}_hack_1000") for x in FID_X for s in ALL_SETS]
    sec2_xy = [(HELDOUT_X, f"random_{s}_hack_1000") for s in ALL_SETS] + \
        [(DEC_X[sx], f"random_{sy}_hack_1000") for sx, sy, _ in DEC_ROWS]
    e1_xy = [(E_X[s], y) for s in ALL_SETS for y, _ in Y_VARS]
    blocks = compute_blocks(rows, main_xy + alt_xy + sec_xy + sec2_xy + e1_xy, n_boot, seed, workers)
    # 1. the protocol test (as amended): decided on (120 cities, margin inflation) when the ladder is complete
    main = {}
    for s in ALL_SETS:
        main[s] = {}
        for yk, ydesc in Y_VARS:
            b = dict(blocks[(f"random_{s}_hack_1000", yk)])
            b["y_description"] = ydesc
            primary = s == POOLED and yk == PRIMARY_Y
            b["role"] = "decides the main claim" if primary else "reported beside it"
            if primary and "pooled_spearman" in b:
                b["decision"] = decide(b["pooled_spearman"]) if out["status"] == "complete" else None
                b["decision_status"] = "made" if out["status"] == "complete" else "not made: partial inputs"
            main[s][yk] = b
    out["main"] = main
    pw = power_block(len(prim), len({r["checkpoint"] for r in prim}))
    if prim:
        pw["icc_measured"] = {PRIMARY_X: icc1([r[PRIMARY_X] for r in prim], [r["checkpoint"] for r in prim])}
        for yk, _ in Y_VARS:
            pw["icc_measured"][yk] = icc1([r[yk] for r in prim], [r["checkpoint"] for r in prim])
    out["power"] = pw
    # 3. reliability, on the pairs of the main test for each city set; split-sample on every checkpoint with both
    out["reliability"] = {}
    for s in ALL_SETS:
        xk = f"random_{s}_hack_1000"
        ps = [r for r in rows if _usable(r, xk) and _usable(r, PRIMARY_Y)]
        out["reliability"][s] = reliability(ps, xk, f"random_{s}_n_1000", [y for y, _ in Y_VARS])
    out["split_sample"] = split_sample(rows)
    # 4. alternatives: every x against both RL variables
    alt = {}
    for xk, xdesc in X_VARS:
        for yk, _ in Y_VARS:
            b = dict(blocks[(xk, yk)])
            b["x_description"] = xdesc
            if xk.startswith("fid_") and "pooled_spearman" in b:
                b["abs_below_0.3"] = bool(abs(b["pooled_spearman"].value) < SECONDARY_ABS)
            alt[f"{xk}|{yk}"] = b
    out["alternatives"] = alt
    # the secondary claim as protocol: fidelity against random search's false acceptance at 1,000
    sec = {}
    xdesc = dict(X_VARS)
    for s in ALL_SETS:
        for xk in FID_X:
            b = dict(blocks[(xk, f"random_{s}_hack_1000")])
            b["x_description"] = xdesc[xk]
            if "pooled_spearman" in b:
                e = b["pooled_spearman"]
                b["abs_below_0.3"] = bool(abs(e.value) < SECONDARY_ABS)
                b["interval_abs_above_0.3"] = (None if e.n_clusters < 2 or not np.isfinite(e.lo)
                                               else bool(e.lo > SECONDARY_ABS or e.hi < -SECONDARY_ABS))
            sec[f"{xk}|{s}"] = b
    # the two further protocol measures , the same statistics and rule
    new = [(HELDOUT_X, HELDOUT_DESC, s, s, None) for s in ALL_SETS] + \
        [(DEC_X[sx], DEC_DESC[sx], sx, sy, role) for sx, sy, role in DEC_ROWS]
    for xk, desc, sx, sy, role in new:
        b = dict(blocks[(xk, f"random_{sy}_hack_1000")])
        b["x_description"] = desc
        if role is not None:
            b["x_cities"], b["y_cities"], b["role"] = sx, sy, role
            b["verdict_row"] = f"{xk}|{sy}" == DEC_VERDICT_ROW
        if "pooled_spearman" in b:
            e = b["pooled_spearman"]
            b["abs_below_0.3"] = bool(abs(e.value) < SECONDARY_ABS)
            b["interval_abs_above_0.3"] = (None if e.n_clusters < 2 or not np.isfinite(e.lo)
                                           else bool(e.lo > SECONDARY_ABS or e.hi < -SECONDARY_ABS))
        sec[f"{xk}|{sy}"] = b
    out["secondary"] = sec
    out["secondary_decision_fidelity_verdict_row"] = DEC_VERDICT_ROW
    out["exploratory_logged_plan"] = exploratory(rows, blocks, out["status"], n_boot, seed)
    return out


def e2_block(rows: list[dict], s: str, yk: str, n_boot: int, seed: int) -> dict:
    """The analysis plan, E2: on the pairs holding random search's false acceptance at 1,000 and at budget 1 and the RL
    variable, Spearman at 1,000 minus Spearman at 1, both recomputed on every cluster resample (the same draws:
    clusters = checkpoints; lineage clusters as a sensitivity); pooled, per family, the mean of the within-family
    values and the pooled Spearman of within-family ranks (each as ``corr_block`` computes it)."""
    xa, xb = E_SEARCH_X[s], E_X[s]
    rs = [r for r in rows if _usable(r, xa) and _usable(r, xb) and _usable(r, yk)]
    a = np.array([r[xa] for r in rs], float)
    b = np.array([r[xb] for r in rs], float)
    y = np.array([r[yk] for r in rs], float)
    ck = np.array([r["checkpoint"] for r in rs])
    lin = np.array([r["lineage"] for r in rs])
    out = {"x_search": xa, "x_logged_plan": xb, "y": yk, "n_pairs": len(rs),
           "n_checkpoints": int(np.unique(ck).size) if rs else 0, "n_lineages": int(np.unique(lin).size) if rs else 0,
           "statistic": "Spearman with x at 1,000 minus Spearman with x at budget 1, on the same pairs and the same "
                        "cluster resamples (clusters = checkpoints)"}
    if len(rs) < 3:
        out["status"] = "fewer than 3 pairs"
        return out
    fam = np.array([FAMILIES.index(r["family"]) for r in rs])

    def diff(fa, fb):
        return lambda ix: fa(ix) - fb(ix)
    sp_a = lambda ix: spearman(a[ix], y[ix])     # noqa: E731
    sp_b = lambda ix: spearman(b[ix], y[ix])     # noqa: E731
    out["pooled_spearman_search"] = cluster_boot(sp_a, ck, n_boot, seed)
    out["pooled_spearman_logged_plan"] = cluster_boot(sp_b, ck, n_boot, seed)
    out["pooled_spearman_difference"] = cluster_boot(diff(sp_a, sp_b), ck, n_boot, seed)
    out["pooled_spearman_difference_lineage"] = cluster_boot(diff(sp_a, sp_b), lin, n_boot, seed)
    per = {}
    for i, f in enumerate(FAMILIES):
        sel = np.flatnonzero(fam == i)
        if sel.size < MIN_FAMILY_PAIRS:
            per[f] = {"n": int(sel.size), "status": f"fewer than {MIN_FAMILY_PAIRS} pairs"}
            continue
        aa, bb, yy, cc = a[sel], b[sel], y[sel], ck[sel]
        per[f] = {"n": int(sel.size),
                  "spearman_difference": cluster_boot(lambda ix: spearman(aa[ix], yy[ix]) - spearman(bb[ix], yy[ix]),
                                                      cc, n_boot, seed)}
    out["per_family"] = per
    used = [FAMILIES.index(f) for f in FAMILIES if "spearman_difference" in per[f]]
    out["families_in_mean"] = [FAMILIES[i] for i in used]
    if used:
        out["within_mean_spearman_difference"] = cluster_boot(
            diff(within_family_mean(a, y, fam, used, spearman), within_family_mean(b, y, fam, used, spearman)),
            ck, n_boot, seed)
    out["ranked_within_spearman_difference"] = cluster_boot(diff(ranked_within(a, y, fam), ranked_within(b, y, fam)),
                                                            ck, n_boot, seed)
    return out


def e2_reading(e) -> str | None:
    """The analysis plan's three readings of E2's interval (None where there is no interval)."""
    if not isinstance(e, hs.Estimate) or e.n_clusters < 2 or not (np.isfinite(e.lo) and np.isfinite(e.hi)):
        return None
    return "above" if e.lo > 0 else ("below" if e.hi < 0 else "includes")


def exploratory(rows: list[dict], blocks: dict, status: str, n_boot: int, seed: int) -> dict:
    """The analysis plan's exploratory comparator (supplementary): E1 and E2 for every city set and both RL variables.
    The 120-city rows carry the wording; while the main claim's inputs are partial they carry none ("not made: partial
    inputs", as the main claim's decision); the 40- and 80-city rows are reported beside them."""
    full = LADDER_SIZE * len(FAMILIES)
    out = {"label": "single-plan comparator : defined before any 120-city input was complete",
           "status": status, "budget": E_BUDGET, "wording_fixed_in_advance": E_WORDING,
           "wording_scopes": dict(E_SCOPES), "rows": {}}
    for s in ALL_SETS:
        for yk, ydesc in Y_VARS:
            e1 = dict(blocks[(E_X[s], yk)])
            e1["x"], e1["x_description"], e1["y_description"] = E_X[s], E_DESC[s], ydesc
            e2 = e2_block(rows, s, yk, n_boot, seed)
            row = {"cities": s, "y": yk, "E1": e1, "E2": e2,
                   "role": "carries the wording " if s == POOLED else "reported beside it"}
            if s == POOLED:
                made = status == "complete" and e2["n_pairs"] == full
                row["wording_status"] = "made" if made else "not made: partial inputs"
                if made:
                    row["reading"] = {k: e2_reading(e2.get(k)) for k, _ in E_SCOPES}
                    row["wording"] = {k: (E_WORDING[v] if v else None) for k, v in row["reading"].items()}
                else:
                    row["reading"] = row["wording"] = None
            out["rows"][f"{s}|{yk}"] = row
    return out


# ---------------------------------------------------------------------------------------------------------------
# the analysis plan : the main claim's permutation null, sensitivities and within-family power; the
# secondary claim's checkpoint-level rows, power to falsify, the 24-checkpoint reading and the analysis plan's rule


def _row_ranks(a: np.ndarray) -> np.ndarray:
    """Mid-ranks along the last axis (``scipy.stats.rankdata(method="average")``)."""
    return sps.rankdata(a, axis=-1)


def _rowwise_spearman(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Spearman of each row of X with the same row of Y; NaN where a row is constant."""
    rx, ry = _row_ranks(X), _row_ranks(Y)
    rx = rx - rx.mean(axis=-1, keepdims=True)
    ry = ry - ry.mean(axis=-1, keepdims=True)
    den = np.sqrt((rx * rx).sum(-1) * (ry * ry).sum(-1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, (rx * ry).sum(-1) / np.where(den > 0, den, 1), np.nan)


def perm_null(x, y, fam, n_perm: int = D79_N_PERM, seed: int = D79_PERM_SEED) -> dict:
    """The analysis plan (1a): the pooled Spearman under the within-family permutation null: y permuted among the pairs
    (checkpoints) of each task family, every within-family relation destroyed and the family structure kept."""
    x, y, fam = np.asarray(x, float), np.asarray(y, float), np.asarray(fam)
    out = {"n_pairs": int(x.size), "n_perm": n_perm, "seed": seed,
           "description": "y (the RL variable) permuted among checkpoints within each task family; pooled Spearman"}
    if x.size < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        out["status"] = "not computable: fewer than 3 pairs or a constant variable"
        return out
    rx, ry = midrank(x), midrank(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    den = math.sqrt((rx @ rx) * (ry @ ry))
    rng = np.random.default_rng(seed)
    idx = np.tile(np.arange(x.size), (n_perm, 1))
    for f in np.unique(fam):
        g = np.flatnonzero(fam == f)
        idx[:, g] = rng.permuted(np.tile(g, (n_perm, 1)), axis=1)
    null = (ry[idx] @ rx) / den
    obs = float(rx @ ry / den)
    p = np.percentile(null, [2.5, 50, 97.5])
    out.update({"status": "ok", "observed": obs, "null_p2_5": float(p[0]), "null_median": float(p[1]),
                "null_p97_5": float(p[2]), "observed_above_null_p97_5": bool(obs > p[2]),
                "share_of_null_at_or_above_observed": float(np.mean(null >= obs - 1e-12))})
    return out


def sim_within_power(C: int, F: int, rho: float, n_sim: int = D79_SIM, n_boot: int = D79_SIM_BOOT,
                     seed: int = D79_SIM_SEED) -> dict:
    """The analysis plan (1): power of the within-family reading by simulation. Model: in each of F families, C checkpoints
    with (x, y) bivariate normal of Spearman ``rho`` (Pearson 2 sin(pi rho / 6)); families and checkpoints independent
    (no checkpoint effect shared across families; no ties). Statistic as the analysis computes it: the mean over the
    families of the within-family Spearman, cluster bootstrap over checkpoints (``hpr_dream.stats.cluster_draws``,
    percentile, ``n_boot`` resamples). Power: the share of simulations whose interval excludes zero."""
    r = 2 * math.sin(math.pi * rho / 6)
    rng = np.random.default_rng([seed, C, F, int(round(rho * 1000))])
    D = hs.cluster_draws(C, n_boot, seed)
    excl = lo_pos = ge = 0
    for _ in range(n_sim):
        bs, est = np.zeros(n_boot), 0.0
        for _f in range(F):
            z1 = rng.normal(size=C)
            z2 = r * z1 + math.sqrt(1 - r * r) * rng.normal(size=C)
            est += spearman(z1, z2)
            bs += _rowwise_spearman(z1[D], z2[D])
        est, bs = est / F, bs / F
        ok = np.isfinite(bs)
        lo, hi = np.quantile(bs[ok], [(1 - hs.LEVEL) / 2, (1 + hs.LEVEL) / 2])
        excl += bool(lo > 0 or hi < 0)
        lo_pos += bool(lo > 0)
        ge += bool(est >= THRESHOLD)
    return {"n_checkpoints": C, "n_families": F, "true_within_family_spearman": rho, "n_sim": n_sim, "n_boot": n_boot,
            "power_interval_excludes_0": excl / n_sim, "power_interval_above_0": lo_pos / n_sim,
            "share_estimate_at_least_0.4": ge / n_sim,
            "monte_carlo_se_at_most": 0.5 / math.sqrt(n_sim)}


def _sim_within_job(args):
    return args, sim_within_power(*args, n_sim=D79_SIM, n_boot=D79_SIM_BOOT, seed=D79_SIM_SEED)


SIM_WITHIN_ASSUMPTIONS = (
    "In each task family, the checkpoints' (audit, RL) values are bivariate normal with the stated true Spearman "
    "(Pearson 2 sin(pi rho / 6)); families and checkpoints independent (no checkpoint effect shared across families, "
    "which the measured intra-checkpoint correlations, near zero and negative, do not contradict); continuous values (no "
    "ties); the row's numbers of checkpoints and families; the statistic and interval as computed here (mean of the "
    f"within-family Spearman, cluster bootstrap over checkpoints, percentile), with {D79_SIM_BOOT} resamples in place "
    f"of 2,000; {D79_SIM} simulations per cell; power = the share whose 95 per cent interval excludes zero.")


def main_d79(rows: list[dict], res: dict, n_boot: int, seed: int, workers: int) -> dict:
    """The analysis plan on every main row (three city sets, both RL variables): the within-family permutation
    null of the pooled Spearman, the sensitivities of the original design (clustered by task family; leave one
    lineage out; Pearson), the within-family reading and its power by simulation. Wording on the 120-city rows only
    when the main claim's inputs are complete."""
    status = res["status"]
    out = {"status": status, "rule": "the analysis plan", "wording_fixed_in_advance": D79_MAIN_WORDING,
           "permutation": {"n_perm": D79_N_PERM, "seed": D79_PERM_SEED},
           "power_assumptions": SIM_WITHIN_ASSUMPTIONS, "rows": {}, "power_cells": {}}
    cells = set()
    for s in ALL_SETS:
        xk = f"random_{s}_hack_1000"
        for yk, _ in Y_VARS:
            rs = [r for r in rows if _usable(r, xk) and _usable(r, yk)]
            x = np.array([r[xk] for r in rs], float)
            y = np.array([r[yk] for r in rs], float)
            fam = np.array([r["family"] for r in rs])
            ck = np.array([r["checkpoint"] for r in rs])
            lin = np.array([r["lineage"] for r in rs])
            b = res["main"][s][yk]
            row = {"cities": s, "y": yk, "n_pairs": len(rs), "n_checkpoints": int(np.unique(ck).size) if rs else 0,
                   "role": ("carries the wording " if s == POOLED else
                            ("the check on audit data unseen when every rule was fixed " if s == "c80"
                             else "reported beside it"))}
            row["permutation_null"] = perm_null(x, y, fam)
            if len(rs) >= 3:
                row["sensitivity"] = {
                    "clustered_by_task_family": hs.clustered_spearman(x, y, fam, n_boot=n_boot, seed=seed),
                    "pearson_checkpoint_clusters": cluster_boot(lambda ix: pearson(x[ix], y[ix]), ck, n_boot, seed),
                    "leave_one_lineage_out": {}}
                for L in sorted(set(lin)):
                    sel = lin != L
                    if sel.sum() < 3:
                        continue
                    row["sensitivity"]["leave_one_lineage_out"][str(L)] = {
                        "n_pairs": int(sel.sum()), "n_checkpoints": int(np.unique(ck[sel]).size),
                        "spearman": hs.clustered_spearman(x[sel], y[sel], ck[sel], n_boot=n_boot, seed=seed)}
                lo = [v["spearman"].value for v in row["sensitivity"]["leave_one_lineage_out"].values()]
                row["sensitivity"]["leave_one_lineage_out_range"] = [float(min(lo)), float(max(lo))] if lo else None
            w = b.get("within_mean_spearman")
            nf = len(b.get("families_in_mean", []))
            if isinstance(w, hs.Estimate):
                row["within_family"] = {"estimate": w, "excludes_0": excludes_zero(w),
                                        "reaches_0.4": bool(w.value >= THRESHOLD) if np.isfinite(w.value) else None,
                                        "n_families": nf}
            C = row["n_checkpoints"]
            row["power_cells"] = []
            for Cc in sorted({C, LADDER_SIZE}):
                if Cc >= 3 and nf:
                    for rho in D79_RHOS:
                        cells.add((Cc, nf, rho))
                        row["power_cells"].append(f"{Cc}|{nf}|{rho}")
            if s == POOLED:
                made = status == "complete"
                row["wording_status"] = "made" if made else "not made: partial inputs"
                row["wording"] = None
                if made:
                    pn = row["permutation_null"]
                    wf = row.get("within_family", {})
                    row["wording"] = {
                        "permutation_null": (None if pn.get("status") != "ok" else D79_MAIN_WORDING[
                            "null_above" if pn["observed_above_null_p97_5"] else "null_not_above"]),
                        "within_family": (None if wf.get("excludes_0") is None else D79_MAIN_WORDING[
                            "within_excludes" if wf["excludes_0"] else "within_includes"])}
            out["rows"][f"{s}|{yk}"] = row
    cells = sorted(cells)
    if workers > 1 and len(cells) > 1:
        with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("fork")) as ex:
            got = dict(ex.map(_sim_within_job, cells))
    else:
        got = dict(_sim_within_job(c) for c in cells)
    out["power_cells"] = {f"{C}|{F}|{rho}": got[(C, F, rho)] for C, F, rho in cells}
    return out


def _decompose(Y: np.ndarray) -> dict:
    """Two-way additive decomposition of a checkpoints-by-families table: family means, the SD of the checkpoint
    means (families removed) and the residual SD."""
    C, F = Y.shape
    gm = Y.mean()
    fm = Y.mean(axis=0) - gm
    cm = Y.mean(axis=1) - gm
    e = Y - gm - fm[None, :] - cm[:, None]
    return {"grand_mean": float(gm), "family_effects": fm.tolist(), "sd_checkpoint": float(np.std(cm, ddof=1)),
            "sd_residual": float(math.sqrt((e ** 2).sum() / max((C - 1) * (F - 1), 1))),
            "share_between_families": float((C * (fm ** 2).sum()) / max(((Y - gm) ** 2).sum(), 1e-300))}


def sim_falsify_power(dec: dict, C: int, F: int, rho: float = D79_FALSIFY_RHO, n_sim: int = D79_SIM,
                      n_boot: int = D79_SIM_BOOT, seed: int = D79_SIM_SEED) -> dict:
    """The analysis plan: the power to falsify (the interval on |Spearman| lies above 0.3) at a true checkpoint-
    level Spearman of ``rho`` between a fidelity measure and the checkpoint's mean false acceptance over the families.
    Model: x and the checkpoint component u bivariate normal (Spearman ``rho``); a pair's value = grand mean + the
    observed family effect + sd_checkpoint u + a normal residual of the observed residual SD centred within the
    checkpoint (so the checkpoint mean is a monotone function of u); x constant across the checkpoint's families.
    Pooled row: Spearman over the C x F pairs, cluster bootstrap over checkpoints; checkpoint-level row: Spearman over
    the C checkpoints, bootstrap over checkpoints; percentile intervals, ``n_boot`` resamples."""
    r = 2 * math.sin(math.pi * rho / 6)
    rng = np.random.default_rng([seed, C, F, 79])
    D = hs.cluster_draws(C, n_boot, seed)
    fe_ = np.asarray(dec["family_effects"], float)
    if fe_.size != F:
        raise ValueError("family effects and F differ")
    sc = math.sqrt(F / (F - 1)) if F > 1 else 1.0
    cols = (D[:, :, None] * F + np.arange(F)[None, None, :]).reshape(n_boot, C * F)   # the drawn checkpoints' pairs
    hit = {"pooled": 0, "checkpoint_level": 0}
    for _ in range(n_sim):
        x = rng.normal(size=C)
        u = r * x + math.sqrt(1 - r * r) * rng.normal(size=C)
        z = rng.normal(size=(C, F))
        e = dec["sd_residual"] * sc * (z - z.mean(axis=1, keepdims=True))
        Y = dec["grand_mean"] + fe_[None, :] + dec["sd_checkpoint"] * u[:, None] + e
        xp, yp = np.repeat(x, F), Y.reshape(-1)
        for name, bs in (("pooled", _rowwise_spearman(xp[cols], yp[cols])),
                         ("checkpoint_level", _rowwise_spearman(x[D], Y.mean(axis=1)[D]))):
            ok = np.isfinite(bs)
            lo, hi = np.quantile(bs[ok], [(1 - hs.LEVEL) / 2, (1 + hs.LEVEL) / 2])
            hit[name] += bool(lo > SECONDARY_ABS or hi < -SECONDARY_ABS)
    return {"n_checkpoints": C, "n_families": F, "true_checkpoint_level_spearman": rho, "n_sim": n_sim,
            "n_boot": n_boot, "power_pooled": hit["pooled"] / n_sim,
            "power_checkpoint_level": hit["checkpoint_level"] / n_sim, "monte_carlo_se_at_most": 0.5 / math.sqrt(n_sim),
            "decomposition": dec}


SIM_FALSIFY_ASSUMPTIONS = (
    f"A true Spearman of {D79_FALSIFY_RHO} (either sign) between the fidelity measure and the checkpoint's mean false "
    "acceptance over the five families; the measure constant across a checkpoint's families; a pair's false acceptance "
    "= the observed grand mean + the observed family effect + (the observed SD of checkpoint means) x the checkpoint "
    "component + a normal residual of the observed residual SD (two-way additive fit on the row's own checkpoints), "
    "centred within the checkpoint; normal, continuous values (the observed rates are discrete); the row's checkpoints; "
    f"the statistics and intervals as computed here, {D79_SIM_BOOT} resamples in place of 2,000; {D79_SIM} simulations; "
    f"power = the share whose interval on |Spearman| lies above {SECONDARY_ABS} (the analysis plan's rule).")


def _ckpt_level(rs: list[dict], xk: str, yk_base: str, n_boot: int, seed: int) -> dict:
    """One point per checkpoint: x (constant across the checkpoint's families) against the mean over the five
    families of ``yk_base`` (a checkpoint enters with all five families); bootstrap over checkpoints."""
    by = {}
    for r in rs:
        by.setdefault(r["checkpoint"], []).append(r)
    xs, ys, cks, bad = [], [], [], []
    for c, rr in by.items():
        if len(rr) != len(FAMILIES) or not all(_usable(r, yk_base) for r in rr) or not all(_usable(r, xk) for r in rr):
            continue
        xv = {r[xk] for r in rr}
        if len(xv) != 1:
            bad.append(c)
            continue
        xs.append(rr[0][xk])
        ys.append(float(np.mean([r[yk_base] for r in rr])))
        cks.append(c)
    out = {"x": xk, "y": f"mean over the {len(FAMILIES)} families of {yk_base}", "n_checkpoints": len(xs)}
    if bad:
        out["status"] = f"x differs across the families of {len(bad)} checkpoints"
        return out
    if len(xs) < 3:
        out["status"] = "fewer than 3 checkpoints"
        return out
    x, y, ck = np.array(xs), np.array(ys), np.array(cks)
    e = cluster_boot(lambda ix: spearman(x[ix], y[ix]), ck, n_boot, seed)
    out.update({"status": "ok", "spearman": e, "abs_below_0.3": bool(abs(e.value) < SECONDARY_ABS) if np.isfinite(e.value)
                else None, "interval_abs_above_0.3": (None if not (np.isfinite(e.lo) and np.isfinite(e.hi))
                                                       else bool(e.lo > SECONDARY_ABS or e.hi < -SECONDARY_ABS)),
                "checkpoints": cks})
    return out


def secondary_d79(g: dict, rows: list[dict], res: dict, n_boot: int, seed: int) -> dict:
    """The analysis plan with the analysis plan's rule: the checkpoint set (all 24 if test-selection fidelity of every
    half-trained checkpoint exists under ``results/fidelity/ladder/<run>/test_half/``, else the 12 finals), the pooled
    verdict rows and their checkpoint-level rows on that set, checkpoint-level rows beside every existing secondary
    row, the power to falsify at a true |Spearman| of 0.5 by simulation, and the analysis plan's verdict. Wording only when
    every verdict row holds the whole set and the main claim's inputs are complete (``main_claim.json`` complete)."""
    rd, root = g["reader"], Path(g["reader"].root)
    halves = [e for e in g["ladder"] if e["stage"] != "final"]
    finals = [e for e in g["ladder"] if e["stage"] == "final"]
    th = {e["checkpoint"]: read_fidelity(e, "test_half", [root], rd) for e in halves}
    n_half_ok = sum(1 for v in th.values() if v["status"] == "ok")
    # every half-trained checkpoint (12 on the full ladder) has its test-selection file: the claim is read on all
    use24 = bool(halves) and len(halves) == len(finals) and n_half_ok == len(halves)
    out = {"rule": "the analysis plan and the analysis plan", "wording_fixed_in_advance": D79_SEC_WORDING,
           "half_test_selection": {c: v["status"] for c, v in th.items()}, "n_half_with_test_half": n_half_ok,
           "checkpoint_set": (f"all {len(g['ladder'])} checkpoints (test selection: finals from test/, half-trained "
                              "checkpoints from test_half/)" if use24 else
                              f"the {len(finals)} final checkpoints (test-selection fidelity of the half-trained "
                              f"checkpoints under test_half/: {n_half_ok} of {len(halves)} present)"),
           "n_checkpoints_in_set": len(g["ladder"]) if use24 else len(finals),
           "departure": None if use24 else ("read on the final checkpoints instead of the protocol 24 (the analysis plan "
                                            "point 4): test-selection fidelity of the half-trained checkpoints is not "
                                            "complete"),
           "power_assumptions": SIM_FALSIFY_ASSUMPTIONS}
    # the rows of the set: as gathered, with the half-trained checkpoints' test-selection measures when the set is 24
    if use24:
        extra = {}
        for e in halves:
            fv = th[e["checkpoint"]]
            ll, _ = read_heldout_loglik(fv, rd)
            dec = {s: decision_fidelity(g["audits"][e["checkpoint"]][("random", s)], g["tasks"][s], root, rd,
                                        g["m9src"][s]) for s in SETS}
            dec[POOLED] = pool_decision([dec["c40"], dec["c80"]])
            extra[e["checkpoint"]] = {**{f"fid_test_{k}": fv["values"][k] for k, _, _ in FIDELITY_METRICS},
                                      HELDOUT_X: ll, **{DEC_X[s]: (dec[s]["value"] if dec[s].get("status") == "ok"
                                                                   else NAN) for s in ALL_SETS}}
            out.setdefault("half_decision_fidelity", {})[e["checkpoint"]] = {s: dec[s].get("status") for s in ALL_SETS}
        srows = [{**r, **extra.get(r["checkpoint"], {})} for r in rows]
    else:
        fset = {e["checkpoint"] for e in finals}
        srows = [r for r in rows if r["checkpoint"] in fset]
    # checkpoint-level rows beside every existing pooled secondary row (on that row's own pairs)
    out["checkpoint_level_beside_existing"] = {}
    for key, b in res["secondary"].items():
        xk, sy = key.split("|")
        rs = [r for r in rows if _usable(r, xk) and _usable(r, f"random_{sy}_hack_1000")]
        out["checkpoint_level_beside_existing"][key] = _ckpt_level(rs, xk, f"random_{sy}_hack_1000", n_boot, seed)
    # the verdict rows on the set, pooled and checkpoint level, with the power to falsify
    n_set = out["n_checkpoints_in_set"]
    power = {}
    measures, complete = [], True
    for name, keys in D78_MEASURES:
        m = {"measure": name, "rows": {}}
        for key in keys:
            xk, sy = key.split("|")
            yk = f"random_{sy}_hack_1000"
            rs = [r for r in srows if _usable(r, xk) and _usable(r, yk)]
            pb = _block(xk, yk, n_boot, seed, rs) if use24 else dict(res["secondary"][key])
            cl = _ckpt_level(rs, xk, yk, n_boot, seed)
            if sy not in power:
                ys = [r for r in srows if _usable(r, yk)]
                by = {}
                for r in ys:
                    by.setdefault(r["checkpoint"], {})[r["family"]] = r[yk]
                full = [c for c, v in by.items() if len(v) == len(FAMILIES)]
                if len(full) >= 3:
                    Y = np.array([[by[c][f] for f in FAMILIES] for c in full])
                    power[sy] = sim_falsify_power(_decompose(Y), len(full), len(FAMILIES), D79_FALSIFY_RHO, D79_SIM,
                                                  D79_SIM_BOOT, D79_SIM_SEED)
                    power[sy]["checkpoints_in_decomposition"] = len(full)
                    power[sy]["n_checkpoints_simulated"] = len(full)
                else:
                    power[sy] = {"status": "fewer than 3 checkpoints with all five families"}
            e = pb.get("pooled_spearman")
            fals = (None if not isinstance(e, hs.Estimate) or e.n_clusters < 2 or not np.isfinite(e.lo)
                    else bool(e.lo > SECONDARY_ABS or e.hi < -SECONDARY_ABS))
            whole = pb.get("n_checkpoints") == n_set and pb.get("n_pairs") == n_set * len(FAMILIES)
            complete &= bool(whole)
            m["rows"][key] = {"pooled": pb, "checkpoint_level": cl, "falsified": fals, "holds_the_whole_set": whole,
                              "power_pooled": power[sy].get("power_pooled"),
                              "power_checkpoint_level": power[sy].get("power_checkpoint_level")}
        fl = [v["falsified"] for v in m["rows"].values()]
        m["falsified"] = None if any(v is None for v in fl) else any(fl)
        m["power_pooled_verdict_rows"] = [v["power_pooled"] for v in m["rows"].values()]
        measures.append(m)
    out["power"] = power
    out["measures"] = measures
    # the same machinery as the main claim: no wording until main_claim.json is complete (the analysis plan: read at the freeze)
    out["verdict_rows_hold_the_set"] = bool(complete)
    complete = bool(complete) and res["status"] == "complete"
    out["status"] = "complete" if complete else "partial"
    out["n_measures_falsified"] = (None if any(m["falsified"] is None for m in measures)
                                   else sum(bool(m["falsified"]) for m in measures))
    # the analysis plan: the measures not falsified whose verdict rows include one with power to falsify of at least 0.8 (when
    # any exists the claim, if not falsified, is "not falsified", and the output names them)
    out["measures_not_falsified_with_power_at_least_0.8"] = [
        {"measure": m["measure"], "verdict_rows": [k for k, v in m["rows"].items() if v["power_pooled"] is not None
                                                   and v["power_pooled"] >= D79_POWER_BAR]}
        for m in measures if m["falsified"] is False
        and any(p is not None and p >= D79_POWER_BAR for p in m["power_pooled_verdict_rows"])]
    out["wording_status"] = "made" if complete else "not made: partial inputs"
    out["wording"] = None
    if complete and out["n_measures_falsified"] is not None:
        per = {}
        for m in measures:
            pw = [p for p in m["power_pooled_verdict_rows"] if p is not None]
            if m["falsified"]:
                per[m["measure"]] = D79_SEC_WORDING["falsified"]
            elif pw and max(pw) < D79_POWER_BAR:
                per[m["measure"]] = D79_SEC_WORDING["not_falsifiable"]
            else:
                per[m["measure"]] = D79_SEC_WORDING["not_falsified"]
        allp = [p for m in measures for p in m["power_pooled_verdict_rows"] if p is not None]
        claim = (D79_SEC_WORDING["falsified"] if out["n_measures_falsified"] else
                 (D79_SEC_WORDING["not_falsifiable"] if allp and max(allp) < D79_POWER_BAR
                  else D79_SEC_WORDING["not_falsified"]))
        named = [m["measure"] for m in out["measures_not_falsified_with_power_at_least_0.8"]]
        out["wording"] = {"claim": claim, "by_measure": per,
                          "measures_not_falsified_with_power_at_least_0.8": (named if claim == D79_SEC_WORDING[
                              "not_falsified"] else []),
                          "claim_rule": "falsified if any measure is ; otherwise 'not falsifiable at this "
                                        f"size' if the power to falsify of every verdict row is below {D79_POWER_BAR}, "
                                        f"else 'not falsified', naming the measures with a verdict row of power at "
                                        f"least {D79_POWER_BAR}"}
    return out


def _design_matrix(levels_list: list[np.ndarray]) -> np.ndarray:
    """Intercept plus indicator columns for every categorical factor's levels past its first."""
    n = levels_list[0].size
    cols = [np.ones(n, dtype=float)]
    for arr in levels_list:
        uniq = np.unique(arr)
        for u in uniq[1:]:
            cols.append((arr == u).astype(float))
    return np.column_stack(cols)


def _partial_spearman_xy(x: np.ndarray, y: np.ndarray, Z: np.ndarray) -> float:
    """Partial Spearman correlation: Pearson r between OLS residuals of mid-ranks of x and y regressed on Z."""
    if x.size < Z.shape[1] + 2 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return NAN
    R = np.column_stack([midrank(x), midrank(y)])
    coef, _, _, _ = np.linalg.lstsq(Z, R, rcond=None)
    res = R - Z @ coef
    rx, ry = res[:, 0], res[:, 1]
    if np.ptp(rx) < 1e-12 or np.ptp(ry) < 1e-12:
        return NAN
    return pearson(rx, ry)


def _within_partial_spearman(x: np.ndarray, y: np.ndarray, fam_codes: np.ndarray, fams_used: list[int],
                             Z_sd: np.ndarray):
    """Mean across task families of within-family partial Spearman controlling model size and data scale."""
    def stat(ix):
        vals = []
        for f in fams_used:
            sel = ix[fam_codes[ix] == f]
            vals.append(_partial_spearman_xy(x[sel], y[sel], Z_sd[sel]))
        return float(np.mean(vals)) if vals and np.all(np.isfinite(vals)) else NAN
    return stat


def read_fidelity_24m(fid_rec: dict, rd: Reader) -> dict:
    """Extract 24-month open-loop (and all-plan Table-16) trajectory rollout metrics from a verified fidelity JSON."""
    if fid_rec.get("status") != "ok":
        return {"status": fid_rec.get("status", "absent")}
    j = rd.json(Path(fid_rec["file"]))
    if j is None:
        return {"status": "unreadable"}
    ro = j.get("rollouts") or {}
    h24 = ro.get("h24") or {}
    ol24 = ((ro.get("by_subset") or {}).get("open_loop") or {}).get("h24") or {}
    if not h24 or not ol24:
        return {"status": "no_h24_rollouts"}
    vals = {
        "ol_overlay_copy_ratio_24m": ol24.get("mean_ratio_overlays"),
        "ol_scalar_copy_ratio_24m": ol24.get("mean_ratio_sample"),
        "ol_powered_zones_mae_24m": ((ol24.get("scalars") or {}).get("powered_zones") or {}).get("mae_sample"),
        "ol_pollution_copy_ratio_24m": ((ol24.get("half") or {}).get("pollution") or {}).get("ratio_sample"),
        "all_overlay_copy_ratio_24m": h24.get("mean_ratio_overlays"),
        "all_pollution_copy_ratio_24m": ((h24.get("half") or {}).get("pollution") or {}).get("ratio_sample"),
    }
    clean = {}
    for k, v in vals.items():
        if v is None or not np.isfinite(float(v)):
            return {"status": f"missing_{k}"}
        clean[k] = float(v)
    return {"status": "ok", "file": fid_rec["file"], "values": clean}


def _h24_cell_job(args):
    key, x, y, fam, ck, lin, sz, da, n_boot, seed = args
    n_pairs = int(x.size)
    n_ck = int(np.unique(ck).size) if n_pairs else 0
    n_lin = int(np.unique(lin).size) if n_pairs else 0
    if n_pairs < 6 or n_ck < 3:
        return key, {"status": "insufficient_pairs", "n_pairs": n_pairs, "n_checkpoints": n_ck, "n_lineages": n_lin}
    fam_codes = np.array([FAMILIES.index(f) for f in fam])
    used = [i for i in range(len(FAMILIES)) if np.count_nonzero(fam_codes == i) >= MIN_FAMILY_PAIRS]
    Z_sd = _design_matrix([sz, da])
    Z_fsd = _design_matrix([fam, sz, da])
    out = {
        "status": "ok",
        "n_pairs": n_pairs,
        "n_checkpoints": n_ck,
        "n_lineages": n_lin,
        "pooled_spearman": hs.clustered_spearman(x, y, ck, n_boot=n_boot, seed=seed),
        "pooled_spearman_lineage": hs.clustered_spearman(x, y, lin, n_boot=n_boot, seed=seed),
        "partial_spearman_size_data": cluster_boot(lambda ix: _partial_spearman_xy(x[ix], y[ix], Z_sd[ix]),
                                                   ck, n_boot, seed),
        "partial_spearman_family_size_data": cluster_boot(lambda ix: _partial_spearman_xy(x[ix], y[ix], Z_fsd[ix]),
                                                          ck, n_boot, seed),
    }
    if used:
        out["within_mean_spearman"] = cluster_boot(within_family_mean(x, y, fam_codes, used, spearman),
                                                   ck, n_boot, seed)
        out["within_mean_spearman_lineage"] = cluster_boot(within_family_mean(x, y, fam_codes, used, spearman),
                                                           lin, n_boot, seed)
        out["within_partial_spearman_size_data"] = cluster_boot(
            _within_partial_spearman(x, y, fam_codes, used, Z_sd), ck, n_boot, seed)
    return key, out


def horizon_24m_predictors(g: dict, rows: list[dict], n_boot: int, seed: int, workers: int) -> dict:
    """Section 5 24-month trajectory-fidelity rank correlations (pooled, within-family, and partial Spearman
    controlling model size and data scale) against consistent targets: PPO margin inflation, PPO pass-rate optimism,
    and 10^3 random-shooting false acceptance across both all 24 checkpoints (test + test_half) and the 12 finals."""
    rd, root = g["reader"], Path(g["reader"].root)
    ck_meta = {}
    for e in g["ladder"]:
        sp = "test" if e["stage"] == "final" else "test_half"
        fv = read_fidelity(e, sp, [root], rd)
        h24 = read_fidelity_24m(fv, rd)
        fv_dev = read_fidelity(e, "dev", [root], rd)
        h24_dev = read_fidelity_24m(fv_dev, rd)
        ck_meta[e["checkpoint"]] = {"stage": e["stage"], "run": e["run"], "test_split": sp,
                                    "test": h24, "dev": h24_dev}
    fh_path = root / "results" / "analysis" / "fidelity_horizon.json"
    fh_check = {"present": False}
    if fh_path.is_file():
        fh = rd.json(fh_path) or {}
        lad_runs = {e["run"] for e in g["ladder"]}
        fh_test = {r["run"]: r for r in fh.get("rows", [])
                   if r.get("split") == "test" and r.get("stage") == "final" and r.get("run") in lad_runs}
        fh_dev = {(r["run"], r["stage"]): r for r in fh.get("rows", [])
                  if r.get("split") == "dev" and r.get("run") in lad_runs}
        max_diff = 0.0
        for e in g["ladder"]:
            if e["stage"] == "final" and e["run"] in fh_test and ck_meta[e["checkpoint"]]["test"]["status"] == "ok":
                v = ck_meta[e["checkpoint"]]["test"]["values"]
                fr = fh_test[e["run"]]
                max_diff = max(
                    max_diff,
                    abs(v["ol_scalar_copy_ratio_24m"] - float(fr["open_loop_scalars_24m"]["mean_ratio_to_copy_model"])),
                    abs(v["ol_powered_zones_mae_24m"] - float(fr["open_loop_scalars_24m"]["scalars"]["powered_zones"]["model_mae"])),
                    abs(v["all_pollution_copy_ratio_24m"] - float(fr["overlays_24m_all_plans"]["pollution"]["model_ratio"])),
                )
        fh_check = {"present": True, "n_ladder_finals_test": len(fh_test), "n_ladder_checkpoints_dev": len(fh_dev),
                    "max_abs_diff_vs_fidelity_files": float(max_diff)}
    n_test_finals = sum(1 for v in ck_meta.values() if v["stage"] == "final" and v["test"]["status"] == "ok")
    n_test_halves = sum(1 for v in ck_meta.values() if v["stage"] != "final" and v["test"]["status"] == "ok")
    n_dev_all = sum(1 for v in ck_meta.values() if v["dev"]["status"] == "ok")
    jobs = []
    subsets = (
        ("all_24", "all 24 ladder checkpoints (held-out test: 12 finals in test/, 12 half-trained in test_half/)",
         lambda r: ck_meta.get(r["checkpoint"], {}).get("test", {}).get("status") == "ok"),
        ("finals_12", "the 12 converged final ladder checkpoints (held-out test/, Table 16 scope)",
         lambda r: r["stage"] == "final" and ck_meta.get(r["checkpoint"], {}).get("test", {}).get("status") == "ok"),
    )
    for s_key, _, pred in subsets:
        for m_key, _ in HORIZON_24M_METRICS:
            for y_key, _ in HORIZON_24M_TARGETS:
                rs = [r for r in rows if pred(r) and _usable(r, y_key)]
                x = np.array([ck_meta[r["checkpoint"]]["test"]["values"][m_key] for r in rs], dtype=float)
                y = np.array([float(r[y_key]) for r in rs], dtype=float)
                fam = np.array([r["family"] for r in rs])
                ck = np.array([r["checkpoint"] for r in rs])
                lin = np.array([f"{r['size']}_{'full' if 'full' in str(r['data_index']) else 'small'}" for r in rs])
                sz = np.array([str(r["size"]) for r in rs])
                da = np.array([str(r["data_index"]) for r in rs])
                jobs.append(((s_key, m_key, y_key), x, y, fam, ck, lin, sz, da, n_boot, seed))
    if workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("fork")) as ex:
            done = dict(ex.map(_h24_cell_job, jobs))
    else:
        done = dict(_h24_cell_job(j) for j in jobs)
    by_set = {}
    for s_key, s_desc, _ in subsets:
        cells = {}
        for m_key, _ in HORIZON_24M_METRICS:
            cells[m_key] = {y_key: done[(s_key, m_key, y_key)] for y_key, _ in HORIZON_24M_TARGETS}
        by_set[s_key] = {"description": s_desc, "metrics": cells}
    complete = (n_test_finals == LADDER_SIZE // 2 and n_test_halves == LADDER_SIZE // 2
                and all(v.get("status") == "ok" and v.get("n_pairs") == LADDER_SIZE * len(FAMILIES)
                        for (sk, _, _), v in done.items() if sk == "all_24"))
    return {
        "status": "complete" if complete else "partial",
        "n_boot": int(n_boot),
        "seed": int(seed),
        "coverage": {
            "n_ladder_total": len(g["ladder"]),
            "n_finals_heldout_test": n_test_finals,
            "n_halves_heldout_test_half": n_test_halves,
            "n_total_heldout_test_24m": n_test_finals + n_test_halves,
            "n_total_dev_24m": n_dev_all,
            "fidelity_horizon_json_check": fh_check,
        },
        "metrics": dict(HORIZON_24M_METRICS),
        "targets": dict(HORIZON_24M_TARGETS),
        "sets": by_set,
    }


def _lin6_pair_job(args):
    key, x, y, fam, ck, lin6, n_boot, seed = args
    n_pairs = int(x.size)
    n_ck = int(np.unique(ck).size) if n_pairs else 0
    n_lin = int(np.unique(lin6).size) if n_pairs else 0
    if n_pairs < 3 or n_ck < 2 or n_lin < 2:
        return key, {"status": "insufficient_pairs", "n_pairs": n_pairs, "n_checkpoints": n_ck, "n_lineages": n_lin}
    fam_codes = np.array([FAMILIES.index(f) for f in fam])
    used = [i for i in range(len(FAMILIES)) if np.count_nonzero(fam_codes == i) >= MIN_FAMILY_PAIRS]
    out = {
        "status": "ok",
        "n_pairs": n_pairs,
        "n_checkpoints": n_ck,
        "n_lineages": n_lin,
        "pooled_spearman_ckpt24": hs.clustered_spearman(x, y, ck, n_boot=n_boot, seed=seed),
        "pooled_spearman_lineage6": hs.clustered_spearman(x, y, lin6, n_boot=n_boot, seed=seed),
        "ranked_within_spearman_ckpt24": cluster_boot(ranked_within(x, y, fam_codes), ck, n_boot, seed),
        "ranked_within_spearman_lineage6": cluster_boot(ranked_within(x, y, fam_codes), lin6, n_boot, seed),
    }
    if used:
        out["within_mean_spearman_ckpt24"] = cluster_boot(within_family_mean(x, y, fam_codes, used, spearman),
                                                          ck, n_boot, seed)
        out["within_mean_spearman_lineage6"] = cluster_boot(within_family_mean(x, y, fam_codes, used, spearman),
                                                            lin6, n_boot, seed)
    return key, out


def _lin6_diff_job(args):
    yk, xs, x1, y, fam, ck, lin6, n_boot, seed = args
    n_pairs = int(y.size)
    n_ck = int(np.unique(ck).size) if n_pairs else 0
    n_lin = int(np.unique(lin6).size) if n_pairs else 0
    if n_pairs < 3 or n_ck < 2 or n_lin < 2:
        return yk, {"status": "insufficient_pairs", "n_pairs": n_pairs, "n_checkpoints": n_ck, "n_lineages": n_lin}
    fam_codes = np.array([FAMILIES.index(f) for f in fam])
    used = [i for i in range(len(FAMILIES)) if np.count_nonzero(fam_codes == i) >= MIN_FAMILY_PAIRS]
    sp_s = lambda ix: spearman(xs[ix], y[ix])
    sp_1 = lambda ix: spearman(x1[ix], y[ix])
    diff = lambda a, b: lambda ix: a(ix) - b(ix)
    out = {
        "status": "ok",
        "n_pairs": n_pairs,
        "n_checkpoints": n_ck,
        "n_lineages": n_lin,
        "pooled_spearman_diff_ckpt24": cluster_boot(diff(sp_s, sp_1), ck, n_boot, seed),
        "pooled_spearman_diff_lineage6": cluster_boot(diff(sp_s, sp_1), lin6, n_boot, seed),
    }
    if used:
        wm_s = within_family_mean(xs, y, fam_codes, used, spearman)
        wm_1 = within_family_mean(x1, y, fam_codes, used, spearman)
        out["within_mean_spearman_diff_ckpt24"] = cluster_boot(diff(wm_s, wm_1), ck, n_boot, seed)
        out["within_mean_spearman_diff_lineage6"] = cluster_boot(diff(wm_s, wm_1), lin6, n_boot, seed)
    return yk, out


def lineage_6_cluster_bootstrap(g: dict, rows: list[dict], n_boot: int, seed: int, workers: int) -> dict:
    """6-lineage ({15m, 50m, 100m} x {small, full}, 4 checkpoints per lineage) and 24-checkpoint cluster bootstraps
    (20,000 draws) for Section 5 verdict-audit predictors (10^3 shooting FA and single-logged-plan FA) against PPO
    margin inflation, PPO pass-rate optimism, and PPO initial-plan FA."""
    fa0_map = g.get("rl_fa0_1000000", {})

    def y_val(r: dict, yk: str) -> float:
        if yk == "rl_fa0_1000000":
            return float(fa0_map.get(f"{r['checkpoint']}|{r['family']}", NAN))
        v = r.get(yk, NAN)
        return float(v) if v is not None else NAN

    def lin6_label(r: dict) -> str:
        scale = "full" if "full" in str(r.get("data_index", "")) else "small"
        return f"{r['size']}_{scale}"

    pair_jobs, diff_jobs = [], []
    for xk, _ in LINEAGE_6_PREDICTORS:
        for yk, _ in LINEAGE_6_TARGETS:
            rs = [r for r in rows if _usable(r, xk) and np.isfinite(y_val(r, yk))]
            x = np.array([float(r[xk]) for r in rs], dtype=float)
            y = np.array([y_val(r, yk) for r in rs], dtype=float)
            fam = np.array([r["family"] for r in rs])
            ck = np.array([r["checkpoint"] for r in rs])
            lin6 = np.array([lin6_label(r) for r in rs])
            pair_jobs.append(((xk, yk), x, y, fam, ck, lin6, n_boot, seed))
    for yk, _ in LINEAGE_6_TARGETS:
        rs = [r for r in rows if _usable(r, "random_c120_hack_1000") and _usable(r, "random_c120_hack_1")
              and np.isfinite(y_val(r, yk))]
        xs = np.array([float(r["random_c120_hack_1000"]) for r in rs], dtype=float)
        x1 = np.array([float(r["random_c120_hack_1"]) for r in rs], dtype=float)
        y = np.array([y_val(r, yk) for r in rs], dtype=float)
        fam = np.array([r["family"] for r in rs])
        ck = np.array([r["checkpoint"] for r in rs])
        lin6 = np.array([lin6_label(r) for r in rs])
        diff_jobs.append((yk, xs, x1, y, fam, ck, lin6, n_boot, seed))
    if workers > 1 and len(pair_jobs) + len(diff_jobs) > 1:
        with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context("fork")) as ex:
            p_done = dict(ex.map(_lin6_pair_job, pair_jobs))
            d_done = dict(ex.map(_lin6_diff_job, diff_jobs))
    else:
        p_done = dict(_lin6_pair_job(j) for j in pair_jobs)
        d_done = dict(_lin6_diff_job(j) for j in diff_jobs)
    lineages_members: dict[str, list[str]] = {}
    for e in g["ladder"]:
        scale = "full" if "full" in str(e.get("data_index", "")) else "small"
        lineages_members.setdefault(f"{e['size']}_{scale}", []).append(e["checkpoint"])
    rows_out = {f"{xk}|{yk}": p_done[(xk, yk)] for xk, _ in LINEAGE_6_PREDICTORS for yk, _ in LINEAGE_6_TARGETS}
    complete = (len(lineages_members) == 6 and all(len(v) == 4 for v in lineages_members.values())
                and all(v.get("status") == "ok" and v.get("n_pairs") == LADDER_SIZE * len(FAMILIES)
                        and v.get("n_checkpoints") == LADDER_SIZE and v.get("n_lineages") == 6
                        for v in rows_out.values()))
    return {
        "status": "complete" if complete else "partial",
        "n_boot": int(n_boot),
        "seed": int(seed),
        "lineage_definition": "{15m, 50m, 100m} x {small, full}: 6 four-checkpoint lineages (one-step half, one-step final, pushforward half, pushforward final)",
        "lineages": {k: sorted(v) for k, v in sorted(lineages_members.items())},
        "predictors": dict(LINEAGE_6_PREDICTORS),
        "targets": dict(LINEAGE_6_TARGETS),
        "rows": rows_out,
        "differences_1000_minus_1": d_done,
    }


def annotate_secondary(res: dict, g: dict) -> None:
    """The further measures' rows: how many finals hold the measure, by reading status, and (where no pair has it) the
    reason it was not computed."""
    finals = [c for c, e in zip(g["checkpoints"], g["ladder"]) if e["stage"] == "final"]

    def statuses(xk):
        if xk == HELDOUT_X:
            st = [c["heldout_loglik"] for c in finals]
        else:
            s = next(k for k, v in DEC_X.items() if v == xk)
            st = [c["decision_fidelity"][s]["status"] for c in finals]
        out = {}
        for v in st:
            out[v] = out.get(v, 0) + 1
        return out
    for key, b in res["secondary"].items():
        xk = key.split("|")[0]
        if xk != HELDOUT_X and xk not in DEC_X.values():
            continue
        b["x_status_finals"] = statuses(xk)
        b["n_finals"] = len(finals)
        b["complete_on_finals"] = bool(len(finals) and b["n_checkpoints"] == len(finals)
                                       and b["n_pairs"] == len(FAMILIES) * len(finals))
        if "pooled_spearman" not in b:
            bad = {k: v for k, v in b["x_status_finals"].items() if k != "ok"}
            b["not_computed"] = ("; ".join(f"{v} of {len(finals)} finals: {k}" for k, v in bad.items())
                                 if bad else b.get("status", "no pair with both variables"))


def seeded_done(g: dict) -> dict:
    """The analysis plan's test of one checkpoint: its pool-seeded search on the 40 cities counts as done when the run's
    ``reference.json`` exists and the audit is complete by this script's own reading (``read_audit`` status ok; every
    family's instances at every budget with nothing missing and the excess paired with the perfect emulator; the
    records reproduce reference.json's per-family values)."""
    root = Path(g["reader"].root)
    byck = {c["checkpoint"]: c for c in g["checkpoints"]}
    out = {}
    for e in g["ladder"]:
        ck = e["checkpoint"]
        a = g["audits"][ck][("cem_seeded", "c40")]
        has_ref = (root / a["dir"] / "reference.json").is_file()
        why = [] if has_ref else ["no reference.json"]
        if a["status"] != "ok":
            why.append(f"audit {a['status']}")
        else:
            prs = [r for r in g["rows"] if r["checkpoint"] == ck]
            tags = sorted({t for r in prs for t in r["missing"].split(";")
                           if t.startswith(("audit_cem_seeded_c40", "excess_cem_seeded_c40"))})
            if len(prs) != len(FAMILIES):
                why.append(f"{len(prs)} of {len(FAMILIES)} families")
            if tags:
                why.append("incomplete: " + "; ".join(tags))
            chk = byck[ck]["reference_json_check"].get("cem_seeded_c40")
            if has_ref and chk is None:
                why.append("reference.json unreadable")
            elif chk is not None and chk["differ"]:
                why.append(f"reference.json disagrees with the records in {len(chk['differ'])} values")
            elif chk is not None and not chk["agree"]:
                why.append("reference.json holds no per-family value the records reproduce")
        out[ck] = {"done": not why, "why_not": why}
    return out


def seeded_nested_set(g: dict, rows: list[dict], n_boot: int, seed: int, workers: int) -> dict:
    """The analysis plan: the pool-seeded search's false acceptance at 1,000 on the 40 cities against both RL variables
    (pooled and within family, ``corr_block``, as the random-search rows) on the largest complete nested set: all 24
    checkpoints, the 12 finals, the 6 full-data finals; beside it random search on the same checkpoints."""
    done = seeded_done(g)
    lad = g["ladder"]
    members = {"all": [e["checkpoint"] for e in lad],
               "finals": [e["checkpoint"] for e in lad if e["stage"] == "final"],
               "full_finals": [e["checkpoint"] for e in lad
                               if e["stage"] == "final" and LADDER_RUN.fullmatch(e["run"]).group(2) == "full"]}
    sets = {}
    for key, name, size in NESTED_SETS:
        cks = members[key]
        sets[key] = {"name": name, "n_expected": size, "n_checkpoints": len(cks),
                     "n_done": sum(done[c]["done"] for c in cks),
                     "complete": len(cks) == size and all(done[c]["done"] for c in cks),
                     "checkpoints": cks, "not_done": [c for c in cks if not done[c]["done"]]}
    largest = next((k for k, _, _ in NESTED_SETS if sets[k]["complete"]), None)
    out = {"description": "the analysis plan: the pool-seeded search's cross-emulator row on the largest complete nested set "
                          "(all 24 checkpoints, the 12 finals, the 6 full-data finals)",
           "x": SEEDED_X, "y": [y for y, _ in Y_VARS],
           "done_test": "tasks_v2_H24_cem_seeded/reference.json exists; the audit reads with status ok; every family's "
                        "instances at 10, 100 and 1,000 are complete and paired with the perfect emulator; the records "
                        "reproduce reference.json's per-family values",
           "order": [k for k, _, _ in NESTED_SETS], "sets": sets, "checkpoints": done,
           "largest_complete_set": largest, "largest_complete_set_name": sets[largest]["name"] if largest else None,
           "status": f"computed on {sets[largest]['name']}" if largest else "no set is complete", "rows": {}}
    if largest:
        keep = set(sets[largest]["checkpoints"])
        sel = [r for r in rows if r["checkpoint"] in keep]
        xy = [(SEEDED_X, y) for y, _ in Y_VARS] + [(f"random_{s}_hack_1000", y) for s in (POOLED, "c40") for y, _ in Y_VARS]
        blocks = compute_blocks(sel, xy, n_boot, seed, workers)
        for x, y in xy:
            b = dict(blocks[(x, y)])
            b["role"] = "the row " if x == SEEDED_X else "beside it: random search on the same checkpoints"
            b["n_pairs_expected"] = len(FAMILIES) * len(keep)
            out["rows"][f"{x}|{y}"] = b
    return out


# ---------------------------------------------------------------------------------------------------------------
# audit measurements: arms, paired differences (replication, coverage)


def arm(u: dict, n_boot: int, seed: int) -> dict:
    """One arm's audit statistics on a unit set, BCa (``run_audit._arm_stats``'s estimators): false acceptance,
    the judge's and the oracle's acceptance, false rejection; the perfect emulator's arm and the paired
    difference where the units are paired."""
    kw = dict(n_boot=n_boot, seed=seed, bca=True)
    ga, oa, cl = u["ga"], u["oa"], list(u["cl"])
    out = {"n": int(ga.size), "n_clusters": len(set(cl)), "n_paired": int(u["n_paired"]),
           "emulator": _arm(ga, oa, cl, kw)}
    if u.get("gr") is not None:
        out["perfect_emulator"] = _arm(u["gr"], u["orr"], cl, kw)
        out["difference"] = hs.excess(ga & ~oa, u["gr"] & ~u["orr"], cl, **kw)
    return out


def _arm(ga, oa, cl, kw) -> dict:
    out = {"hackability": hs.hackability(ga, oa, cl, **kw), "judge_accept": hs.conditional_mean(ga, None, cl, **kw),
           "oracle_accept": hs.conditional_mean(oa, None, cl, **kw), "n_judge_accept": int(ga.sum()),
           "n_oracle_accept": int(oa.sum())}
    out["false_rejection"] = (hs.false_rejection(ga[oa], [c for c, o in zip(cl, oa) if o], **kw) if oa.any()
                              else None)
    return out


def _ratio_difference(num_a, den_a, num_b, den_b, cl, n_boot, seed) -> hs.Estimate:
    """sum(num_a)/sum(den_a) - sum(num_b)/sum(den_b) over the same units, both on each cluster resample (the
    package's weights, percentile and BCa intervals)."""
    codes, C = _encode(cl)
    s = [np.bincount(codes, weights=np.asarray(v, float), minlength=C) for v in (num_a, den_a, num_b, den_b)]

    def stat(W):
        with np.errstate(invalid="ignore", divide="ignore"):
            a = np.where(W @ s[1] > 0, (W @ s[0]) / np.where(W @ s[1] > 0, W @ s[1], 1), np.nan)
            b = np.where(W @ s[3] > 0, (W @ s[2]) / np.where(W @ s[3] > 0, W @ s[3], 1), np.nan)
        return a - b
    return hs._from_weights(stat, C, codes.size, n_boot, seed, hs.LEVEL, True)[0]


def model_difference(ua: dict, ub: dict, ref_ok: bool, n_boot: int, seed: int) -> dict:
    """Model a minus model b on the instances both hold (paired by instance key): false acceptance, its excess over
    the perfect emulator (on instances paired with the reference too), real success, the emulator's acceptance
    (means of per-instance differences, ``hpr_dream.stats.excess``) and false rejection (a difference of ratios)."""
    kw = dict(n_boot=n_boot, seed=seed, bca=True)
    ia = {k[0]: i for i, k in enumerate(ua["keys"])}
    ib = {k[0]: i for i, k in enumerate(ub["keys"])}
    common = [k for k in ia if k in ib]
    if not common:
        return {"n": 0, "status": "no common instance"}
    a = np.array([ia[k] for k in common])
    b = np.array([ib[k] for k in common])
    cl = [ua["cl"][i] for i in a]
    ga, oa, gb, ob = ua["ga"][a], ua["oa"][a], ub["ga"][b], ub["oa"][b]
    out = {"n": len(common), "n_clusters": len(set(cl)),
           "hackability": hs.excess(ga & ~oa, gb & ~ob, cl, **kw),
           "oracle_accept": hs.excess(oa, ob, cl, **kw),
           "judge_accept": hs.excess(ga, gb, cl, **kw),
           "false_rejection": (_ratio_difference(oa & ~ga, oa, ob & ~gb, ob, cl, n_boot, seed)
                               if oa.any() and ob.any() else None)}
    if ref_ok and ua.get("gr") is not None and ub.get("gr") is not None:
        hr = ua["gr"][a] & ~ua["orr"][a]
        out["excess_over_perfect"] = hs.excess((ga & ~oa).astype(float) - hr, (gb & ~ob).astype(float) - hr, cl, **kw)
    return out


# ---------------------------------------------------------------------------------------------------------------
# replication of the main checkpoint's headline


def replication(g: dict, n_boot: int, seed: int) -> dict:
    tag = f"{MAIN_RUN}-samples_{MAIN_SAMPLES:09d}"
    aud = g["audits"].get(tag)
    out = {"checkpoint": tag, "methods": {}, "missing": [], "checks": []}
    if aud is None:
        out["missing"].append(f"{tag} is not in the ladder")
        out["status"] = "partial"
        return out
    for m in METHODS:
        out["methods"][m] = {}
        budgets = sorted(set().union(*[set(b for f in FAMILIES for b in aud[(m, s)]["families"].get(f, {}))
                                       for s in SETS]))
        for s in SETS:
            if aud[(m, s)]["status"] != "ok":
                out["missing"].append(f"{m}, {SET_DESC[s]}: {aud[(m, s)]['status']}")
        rb = {s: ref_budgets(aud[(m, s)], m, g["ref_cache"]) for s in SETS}
        for B in budgets:
            us = {s: units_all_families(aud[(m, s)], B) for s in SETS}
            us[POOLED] = pool_units([us["c40"], us["c80"]])
            row = {}
            for s in ALL_SETS:
                if us[s] is None:
                    row[s] = {"status": "absent or incomplete"}
                    continue
                row[s] = arm(us[s], n_boot, seed)
                if "difference" not in row[s]:
                    row[s]["perfect_status"] = pairing_status(B, [rb[x] for x in (SETS if s == POOLED else (s,))])
                    if row[s]["perfect_status"] != NOT_RUN_AT_B:
                        out["missing"].append(f"{m} B={B}, {SET_DESC[s]}: {row[s]['perfect_status']}")
            out["methods"][m][B] = row
        # the 40-city arm must reproduce the run's reference.json (every instance)
        d = Path(g["reader"].root) / aud[(m, "c40")]["dir"]
        refj = g["reader"].json(d / "reference.json") if aud[(m, "c40")]["status"] == "ok" else None
        if refj:
            ok, bad = 0, []
            for grp in refj.get("subsets", {}).get("all", {}).get("groups", []):
                if grp.get("method") != m or "difference" not in grp:
                    continue
                v = out["methods"][m].get(int(grp["budget"]), {}).get("c40", {})
                if "difference" not in v:
                    continue
                for name, mine, theirs in (("difference", v["difference"], grp["difference"]),
                                           ("hackability", v["emulator"]["hackability"], grp["emulator"]["hackability"]),
                                           ("perfect", v["perfect_emulator"]["hackability"],
                                            grp["perfect_emulator"]["hackability"])):
                    for fld in ("value", "bca_lo", "bca_hi", "lo", "hi"):
                        x, y = getattr(mine, fld), theirs.get(fld)
                        if y is None and not np.isfinite(x) or y is not None and np.isclose(x, y, rtol=0, atol=1e-9):
                            ok += 1
                        else:
                            bad.append(f"B={grp['budget']} {name} {fld}: {x} vs {y}")
            out["checks"].append(f"{m}, 40 cities: equals the run's reference.json in {ok} values"
                                 + (f"; differs in {len(bad)}: {'; '.join(bad[:4])}" if bad else ""))
    # the replication statement (fixed in round 2)
    st = {}
    v80 = out["methods"].get("cem_seeded", {}).get(1000, {}).get("c80", {})
    v40 = out["methods"].get("cem_seeded", {}).get(1000, {}).get("c40", {})
    if "difference" in v80:
        lo, hi, kind = interval(v80["difference"])
        st["c80_interval"] = [lo, hi]
        st["c80_interval_kind"] = kind
        st["c80_excludes_0"] = bool(lo > 0 or hi < 0)
        if "difference" in v40:
            st["c40_point"] = v40["difference"].value
            st["c40_point_inside_c80_interval"] = bool(lo <= v40["difference"].value <= hi)
    out["statement"] = st
    out["status"] = "complete" if not out["missing"] and "c40_point_inside_c80_interval" in st else "partial"
    # the analysis plan , after every earlier field
    out["statement_d79"] = {m: replication_d79(aud, m, n_boot, seed) for m in METHODS}
    # the analysis plan, after every earlier field
    out["budget_contrast_d99"] = budget_contrast_d99(aud, out["methods"].get(D99_SEARCH, {}), n_boot, seed)
    return out


D79_B = 1000
D79_WORDING = {"replicates": "replicates", "not_replicated": "does not replicate", "consistent": "consistent in size",
               "not_consistent": "not consistent in size"}


def _excess_draws(u: dict, n_boot: int, seed: int) -> tuple[float, np.ndarray]:
    """The excess over the perfect emulator of a paired unit set (mean over instances of hacked minus perfect-emulator
    hacked) and its cluster-bootstrap replicates (``hpr_dream.stats`` weights: the draws of ``hs.excess`` for the same
    clusters and seed)."""
    d = (u["ga"] & ~u["oa"]).astype(float) - (u["gr"] & ~u["orr"]).astype(float)
    codes, C = _encode(u["cl"])
    sn = np.bincount(codes, weights=d, minlength=C)
    sd = np.bincount(codes, minlength=C).astype(float)
    W = hs._weights(C, n_boot, seed)
    return float(d.mean()), (W @ sn) / (W @ sd)


def replication_d79(aud: dict, method: str, n_boot: int, seed: int) -> dict:
    """The analysis plan: the search's excess over the perfect emulator at 1,000 on the 80 new cities and on the
    original 40, each with its interval (BCa, the percentile interval where BCa is undefined, as the table), and the
    80-minus-40 difference with an interval from independent cluster bootstraps over the two sets of cities (start-
    state families; seed ``seed`` for the 40, ``seed + 1`` for the 80, so the two sets' draws are independent;
    percentile interval of the differences of the replicates). "Replicates" if the 80-city interval excludes zero;
    "consistent in size" if the difference's interval includes zero."""
    out = {"search": method, "budget": D79_B, "rule": "the analysis plan: replicates if the interval of the 80-city "
           "excess excludes zero; consistent in size if the interval of the 80-minus-40 difference includes zero",
           "difference_interval": f"independent cluster bootstraps over the two sets of cities (start-state families), "
                                  f"{n_boot} resamples each, seeds {seed} (40 cities) and {seed + 1} (80 cities), "
                                  f"percentile 95 per cent interval of the replicate differences"}
    us = {s: units_all_families(aud.get((method, s)), D79_B) if aud.get((method, s)) else None for s in SETS}
    for s in SETS:
        u = us[s]
        if u is None or u.get("gr") is None:
            out["status"] = (f"not computable: {SET_DESC[s]}: "
                             + ("absent or incomplete" if u is None else "not paired with the perfect emulator"))
            return out
    kw = dict(n_boot=n_boot, seed=seed, bca=True)
    for s in SETS:
        u = us[s]
        e = hs.excess(u["ga"] & ~u["oa"], u["gr"] & ~u["orr"], list(u["cl"]), **kw)
        lo, hi, kind = interval(e)
        out[f"excess_{s}"] = e
        out[f"excess_{s}_interval"] = [lo, hi]
        out[f"excess_{s}_interval_kind"] = kind
        out[f"n_{s}"], out[f"n_clusters_{s}"] = int(u["n"]), len(set(u["cl"]))
    v40, b40 = _excess_draws(us["c40"], n_boot, seed)
    v80, b80 = _excess_draws(us["c80"], n_boot, seed + 1)
    if not (np.isclose(v40, out["excess_c40"].value, rtol=0, atol=1e-12)
            and np.isclose(v80, out["excess_c80"].value, rtol=0, atol=1e-12)):
        raise SystemExit("replication_d79: the excess disagrees with hpr_dream.stats.excess")
    diff = b80 - b40
    ok = np.isfinite(diff)
    lo, hi = np.quantile(diff[ok], [(1 - hs.LEVEL) / 2, (1 + hs.LEVEL) / 2])
    out["difference_c80_minus_c40"] = {"value": v80 - v40, "lo": float(lo), "hi": float(hi), "n_boot": n_boot,
                                       "n_boot_undefined": int((~ok).sum())}
    lo80, hi80 = out["excess_c80_interval"]
    out["c80_excess_interval_excludes_0"] = bool(lo80 > 0 or hi80 < 0)
    out["difference_interval_includes_0"] = bool(lo <= 0 <= hi)
    out["reading"] = {"c80": D79_WORDING["replicates" if out["c80_excess_interval_excludes_0"] else "not_replicated"],
                      "size": D79_WORDING["consistent" if out["difference_interval_includes_0"] else "not_consistent"]}
    out["status"] = "ok"
    return out


D99_SEARCH, D99_BUDGETS = "random", (1000, 1)   # the analysis plan: the excess at 1,000 minus at one logged plan


def _excess_units(u: dict) -> np.ndarray:
    """Per instance of a paired unit set: emulator falsely accepts minus perfect emulator falsely accepts."""
    return (u["ga"] & ~u["oa"]).astype(float) - (u["gr"] & ~u["orr"]).astype(float)


def budget_contrast(ua: dict, ub: dict, n_boot: int, seed: int, names: tuple = ("a", "b")) -> dict:
    """The excess over the perfect emulator on unit set ``ua`` minus that on ``ub``, paired by instance (both must hold
    the same instances, each once, with the same clusters): the mean over instances of the per-instance contrasts, with
    ``hpr_dream.stats.excess`` of the contrasts against zero (cluster bootstrap, BCa; ``interval`` names the interval
    read); each set's own excess as ``excess_<name>``."""
    ka, kb = [k[0] for k in ua["keys"]], [k[0] for k in ub["keys"]]
    if len(set(ka)) != len(ka) or len(set(kb)) != len(kb) or set(ka) != set(kb):
        raise SystemExit("budget_contrast: the two budgets do not hold the same instances once each")
    ib = {k: i for i, k in enumerate(kb)}
    b = np.array([ib[k] for k in ka])
    cl = list(ua["cl"])
    if [ub["cl"][i] for i in b] != cl:
        raise SystemExit("budget_contrast: the two budgets put an instance in different clusters")
    ea, eb = _excess_units(ua), _excess_units(ub)[b]
    d = ea - eb
    e = hs.excess(d, np.zeros(d.size), cl, n_boot=n_boot, seed=seed, bca=True)
    lo, hi, kind = interval(e)
    return {"status": "ok", "n": int(d.size), "n_clusters": len(set(cl)), f"excess_{names[0]}": float(ea.mean()),
            f"excess_{names[1]}": float(eb.mean()), "contrast": e, "interval": [lo, hi], "interval_kind": kind}


def budget_contrast_d99(aud: dict, rows: dict, n_boot: int, seed: int) -> dict:
    """The analysis plan: random search's excess false acceptance over the perfect emulator at
    1,000 evaluations minus its excess at budget 1 (one logged plan), paired by instance, on all 120 cities (the two
    files' instances pooled, as the replication's arms) and on the 40. Each budget's excess must equal the
    replication's ``difference`` at that budget (``rows``: ``replication()``'s rows of the search)."""
    hi_b, lo_b = D99_BUDGETS
    out = {"search": D99_SEARCH, "budgets": [hi_b, lo_b],
           "definition": f"per instance, (emulator falsely accepts minus the perfect emulator falsely accepts) at "
                         f"{hi_b:,} evaluations minus the same at budget {lo_b} (one logged plan), on the same instance "
                         f"(paired by instance key; same instances and clusters at both budgets); the mean over "
                         f"instances (contrast); excess_at_{hi_b} and excess_at_{lo_b}: the excess at each budget",
           "interval": f"hpr_dream.stats.excess of the per-instance contrasts against zero: cluster bootstrap over "
                       f"start-state families, {n_boot} resamples, seed {seed}; BCa where defined, else percentile "
                       f"(interval_kind); contrast holds both (lo/hi percentile, bca_lo/bca_hi BCa)"}
    us = {}
    for B in D99_BUDGETS:
        u = {s: units_all_families(aud.get((D99_SEARCH, s)), B) if aud.get((D99_SEARCH, s)) else None for s in SETS}
        us[B] = {POOLED: pool_units([u["c40"], u["c80"]]), "c40": u["c40"]}
    for s in (POOLED, "c40"):
        ua, ub = us[hi_b][s], us[lo_b][s]
        if ua is None or ub is None or ua.get("gr") is None or ub.get("gr") is None:
            out[s] = {"status": f"not computable: {SET_DESC[s]}: a budget's units are absent, incomplete or not paired "
                                f"with the perfect emulator"}
            continue
        out[s] = budget_contrast(ua, ub, n_boot, seed, names=(f"at_{hi_b}", f"at_{lo_b}"))
        for B in D99_BUDGETS:
            ref = rows.get(B, {}).get(s, {}).get("difference")
            if ref is None or not np.isclose(out[s][f"excess_at_{B}"], ref.value, rtol=0, atol=1e-12):
                raise SystemExit(f"budget_contrast_d99: {s} B={B}: the excess disagrees with the replication's")
    out["status"] = "ok" if all(out[s]["status"] == "ok" for s in (POOLED, "c40")) else "partial"
    return out


def interval(e: hs.Estimate) -> tuple[float, float, str]:
    """BCa where defined, else the percentile interval (the convention of the audit's reference tables)."""
    if np.isfinite(e.bca_lo) and np.isfinite(e.bca_hi):
        return e.bca_lo, e.bca_hi, "BCa"
    return e.lo, e.hi, "percentile"


# ---------------------------------------------------------------------------------------------------------------
# coverage arm


def coverage(g: dict, root: Path, ckpt_root: Path, ref_root: Path, fid_fallback: Path, rl_fallback: Path,
             n_boot: int, seed: int) -> dict:
    rd, tasks = g["reader"], g["tasks"]["c40"]
    main = next((e for e in g["ladder"] if e["run"] == MAIN_RUN and e["samples"] == MAIN_SAMPLES), None)
    cov = single_entry(ckpt_root, COV_RUN, COV_SAMPLES, rd)
    out = {"main": main["checkpoint"] if main else None, "coverage": cov["checkpoint"] if cov else None,
           "missing": [], "methods": {}, "rl": {}, "fidelity": {}}
    if main is None or cov is None:
        out["missing"].append("the main or the coverage checkpoint is not found")
        out["status"] = "partial"
        return out
    out["coverage_entry"] = cov
    rand = None
    for m in COVERAGE_METHODS:
        am = read_audit(main, m, tasks, root, ref_root, rd, g["ref_cache"])
        ac = read_audit(cov, m, tasks, root, ref_root, rd, g["ref_cache"])
        if m == "random":
            rand = (am, ac)
        st = {"main": am["status"], "coverage": ac["status"]}
        out["methods"][m] = {"status": st, "budgets": {}}
        for who, a in (("main", am), ("coverage", ac)):
            if a["status"] != "ok":
                out["missing"].append(f"{m}, {who} model: {a['status']}")
        if am["status"] != "ok" or ac["status"] != "ok":
            continue
        budgets = sorted(set(b for f in FAMILIES for b in am["families"].get(f, {}))
                         & set(b for f in FAMILIES for b in ac["families"].get(f, {})))
        rb = ref_budgets(am, m, g["ref_cache"])
        for B in budgets:
            res = {}
            for scope in ("all",) + FAMILIES:
                fams = FAMILIES if scope == "all" else (scope,)
                ua = pool_units([ac["families"].get(f, {}).get(B) for f in fams])
                ub = pool_units([am["families"].get(f, {}).get(B) for f in fams])
                if ua is None or ub is None:
                    res[scope] = {"status": "incomplete"}
                    continue
                res[scope] = {"coverage": arm(ua, n_boot, seed), "main": arm(ub, n_boot, seed),
                              "coverage_minus_main": model_difference(ua, ub, True, n_boot, seed)}
                if scope == "all" and ("difference" not in res[scope]["coverage"]
                                       or "difference" not in res[scope]["main"]):
                    ps = pairing_status(B, [rb])
                    res[scope]["perfect_status"] = ps
                    if ps != NOT_RUN_AT_B:
                        out["missing"].append(f"{m} B={B}: {ps}")
            out["methods"][m]["budgets"][B] = res
    # RL: the coverage model's 15 runs beside the main model's 15
    for who, e, roots in (("main", main, [root]), ("coverage", cov, [root, rl_fallback])):
        out["rl"][who] = {}
        for f in FAMILIES:
            rl = read_rl(e, f, roots, tasks, rd)
            out["rl"][who][f] = {"values": rl_aggregate(rl), "notes": rl["notes"],
                                 "source": sorted(set(rl["source"].values()))}
            if len(rl["seeds"][SNAPSHOTS[-1]]) < len(RL_SEEDS):
                out["missing"].append(f"RL, {who} model, {f}: {len(rl['seeds'][SNAPSHOTS[-1]])}/{len(RL_SEEDS)} seeds "
                                      f"at {SNAPSHOTS[-1]:,} months")
    # fidelity of both
    for who, e, roots in (("main", main, [root]), ("coverage", cov, [root, fid_fallback])):
        out["fidelity"][who] = {sp: read_fidelity(e, sp, roots, rd) for sp in ("dev", "test")}
        for sp, v in out["fidelity"][who].items():
            if v["status"] != "ok":
                out["missing"].append(f"fidelity, {who} model, {sp}: {v['status']}")
    out["status"] = "complete" if not out["missing"] else "partial"
    # minor 1 of : after the status, which it does not enter (every earlier field unchanged)
    out["decision_fidelity"] = coverage_decision_fidelity(g, root, main, rand, n_boot, seed)
    return out


def coverage_decision_fidelity(g: dict, root: Path, main: dict, rand, n_boot: int, seed: int) -> dict:
    """The coverage model's fixed-candidate decision fidelity on the 40 cities, computed exactly as the analysis plan
    computes it for the finals (``decision_fidelity`` on the random-search audit's ``pools.npz``, the engine's
    nine-seed mean from the 40 cities' engine reference), beside the main checkpoint's; coverage minus main paired by
    instance on the instances where both rank correlations are defined (``hpr_dream.stats.excess``), overall and by
    family; BCa cluster bootstrap over start-state families, the percentile interval where BCa is undefined (the
    convention of the audit's tables)."""
    tasks, rd = g["tasks"]["c40"], g["reader"]
    out = {"cities": "c40", "definition": DEC_DESC["c40"], "status": None,
           "interval": f"cluster bootstrap over start-state families, {n_boot} resamples, seed {seed}, BCa (percentile "
                       f"where BCa is undefined)"}
    if rand is None:
        out["status"] = "not computable: no random-search audit read"
        return out
    am, ac = rand
    dm = decision_fidelity(am, tasks, root, rd, g["m9src"]["c40"])
    dc = decision_fidelity(ac, tasks, root, rd, g["m9src"]["c40"])
    out["main"] = {k: v for k, v in dm.items() if k != "_rho"}
    out["coverage"] = {k: v for k, v in dc.items() if k != "_rho"}
    gm = next((c["decision_fidelity"]["c40"] for c in g["checkpoints"] if c["checkpoint"] == main["checkpoint"]), {})
    if gm.get("status") == "ok" and dm.get("status") == "ok":
        out["main_equals_the_ladder_value"] = bool(gm["value"] == dm["value"])
    if dm.get("status") != "ok" or dc.get("status") != "ok":
        out["status"] = f"not computable: main model {dm.get('status')}; coverage model {dc.get('status')}"
        return out
    # each instance's start-state family, from the audits' own records (the two must agree)
    clus = {}
    for a in (am, ac):
        for f in FAMILIES:
            for u in a["families"].get(f, {}).values():
                for k, c in zip(u.get("keys", []), u.get("cl", [])):
                    if clus.setdefault(k[0], c) != c:
                        out["status"] = f"not computable: {k[0]} has two start-state families in the records"
                        return out
    fam_of = {k: f for f in FAMILIES for k in tasks["instances"][f]}
    common = sorted(k for k, v in dm["_rho"].items() if v is not None and dc["_rho"].get(k) is not None)
    if any(k not in clus for k in common):
        out["status"] = "not computable: an instance without a start-state family in the records"
        return out
    out["n_instances"] = len(dm["_rho"])
    out["n_defined_both"] = len(common)
    out["n_defined_main_only"] = sum(1 for k, v in dm["_rho"].items() if v is not None and dc["_rho"].get(k) is None)
    out["n_defined_coverage_only"] = sum(1 for k, v in dc["_rho"].items() if v is not None and dm["_rho"].get(k) is None)
    kw = dict(n_boot=n_boot, seed=seed, bca=True)
    paired = {}
    for scope in ("all",) + FAMILIES:
        ks = [k for k in common if scope == "all" or fam_of[k] == scope]
        if not ks:
            paired[scope] = {"n_instances": 0, "status": "no instance with both defined"}
            continue
        rc = np.array([dc["_rho"][k] for k in ks], float)
        rm = np.array([dm["_rho"][k] for k in ks], float)
        cl = [clus[k] for k in ks]
        paired[scope] = {"n_instances": len(ks), "n_clusters": len(set(cl)),
                         "coverage": hs.conditional_mean(rc, None, cl, **kw), "main": hs.conditional_mean(rm, None, cl, **kw),
                         "coverage_minus_main": hs.excess(rc, rm, cl, **kw),
                         "n_instances_coverage_higher": int((rc > rm).sum()), "n_instances_main_higher": int((rm > rc).sum())}
    out["paired"] = paired
    out["status"] = "ok"
    return out


# ---------------------------------------------------------------------------------------------------------------
# outputs


def _jsonable(o):
    if isinstance(o, hs.Estimate):
        return _jsonable(o.as_dict())
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [_jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return _jsonable(o.tolist())
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def _cell(v):
    if v is None:
        return ""
    if isinstance(v, (float, np.floating)):
        return "" if not np.isfinite(v) else repr(float(v))
    return str(v)


def write_csv(path: Path, rows: list[dict], cols: list[str] | None = None):
    cols = cols or (list(rows[0].keys()) if rows else [])
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([_cell(r.get(c)) for c in cols])


def fe(e, d: int = 3) -> str:
    """Estimate [interval]; an interval from fewer than 2 clusters is not an interval and is not shown."""
    if not isinstance(e, hs.Estimate) or not np.isfinite(e.value):
        return "n/a"
    if e.n_clusters < 2:
        return f"{e.value:+.{d}f} [{e.n_clusters} cluster: no interval]"
    if not (np.isfinite(e.lo) and np.isfinite(e.hi)):
        return f"{e.value:+.{d}f} [n/a]"
    return f"{e.value:+.{d}f} [{e.lo:+.{d}f}, {e.hi:+.{d}f}]"


def fb(e, d: int = 3) -> str:
    """Audit measurement: value [BCa], or [percentile]* where BCa is undefined, as the reference tables."""
    if not isinstance(e, hs.Estimate) or not np.isfinite(e.value):
        return "n/a"
    lo, hi, kind = interval(e)
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return f"{e.value:.{d}f} [n/a]"
    mark = "†" if e.method == hs.ZERO_BOUND_METHOD else ("*" if kind == "percentile" else "")
    return f"{e.value:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]{mark}"


def fbs(e, d: int = 3) -> str:
    """As ``fb`` with a sign (differences)."""
    if not isinstance(e, hs.Estimate) or not np.isfinite(e.value):
        return "n/a"
    lo, hi, kind = interval(e)
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return f"{e.value:+.{d}f} [n/a]"
    return f"{e.value:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]{'*' if kind == 'percentile' else ''}"


def fx(v, d: int = 3) -> str:
    return "n/a" if v is None or not np.isfinite(v) else f"{v:.{d}f}"


def decision_text(b: dict, status: str) -> str:
    if "pooled_spearman" not in b:
        return f"no estimate ({b.get('status', 'n/a')})"
    if "decision_status" not in b:
        return "reported beside (no decision)"
    if status != "complete":
        return "no decision: partial inputs (the rule is applied to the complete ladder)"
    return f"decision: {b['decision']}"


def ez(e) -> str:
    z = excludes_zero(e) if isinstance(e, hs.Estimate) else None
    return "n/a" if z is None else ("yes" if z else "no")


def correlation_rows(res: dict) -> list[dict]:
    """Long table of every correlation estimate (fig5_correlations.csv)."""
    out = []

    def add(test, xk, yk, scope, statistic, clusters, e, b):
        out.append({"test": test, "x": xk, "y": yk, "scope": scope, "statistic": statistic, "clusters": clusters,
                    "value": e.value, "lo": e.lo, "hi": e.hi, "n_units": e.n_units, "n_clusters": e.n_clusters,
                    "n_boot": e.n_boot, "n_boot_undefined": e.n_boot_undefined, "excludes_zero": excludes_zero(e),
                    "n_pairs": b["n_pairs"], "n_checkpoints": b["n_checkpoints"], "status": res["status"]})

    def blocks():
        for s, d in res["main"].items():
            for yk, b in d.items():
                yield ("main" if (s == POOLED and yk == PRIMARY_Y) else "main_beside"), f"random_{s}_hack_1000", yk, b
        for key, b in res["alternatives"].items():
            xk, yk = key.split("|")
            yield "alternative", xk, yk, b
        for key, b in res["secondary"].items():
            xk, s = key.split("|")
            yield "secondary", xk, f"random_{s}_hack_1000", b

    for test, xk, yk, b in blocks():
        if "pooled_spearman" not in b:
            continue
        add(test, xk, yk, "pooled", "spearman", "checkpoint", b["pooled_spearman"], b)
        add(test, xk, yk, "pooled", "kendall", "checkpoint", b["pooled_kendall"], b)
        add(test, xk, yk, "pooled", "spearman", "lineage", b["pooled_spearman_lineage"], b)
        for f, v in b["per_family"].items():
            if "spearman" in v:
                add(test, xk, yk, f"family:{f}", "spearman", "checkpoint", v["spearman"], b)
                add(test, xk, yk, f"family:{f}", "kendall", "checkpoint", v["kendall"], b)
        if "within_mean_spearman" in b:
            add(test, xk, yk, "within_family_mean", "spearman", "checkpoint", b["within_mean_spearman"], b)
            add(test, xk, yk, "within_family_mean", "kendall", "checkpoint", b["within_mean_kendall"], b)
            add(test, xk, yk, "within_family_mean", "spearman", "lineage", b["within_mean_spearman_lineage"], b)
        add(test, xk, yk, "ranked_within_family", "spearman", "checkpoint", b["ranked_within_spearman"], b)
        add(test, xk, yk, "ranked_within_family", "spearman", "lineage", b["ranked_within_spearman_lineage"], b)
    return out


def _yn(v) -> str:
    return "n/a" if v is None else ("yes" if v else "no")


def secondary_more_md(g: dict, res: dict) -> list[str]:
    """Section 6, continued: held-out likelihood and fixed-candidate decision fidelity ."""
    L = ["### The two further protocol measures: held-out likelihood, fixed-candidate decision fidelity", "",
         "Definitions fixed in the analysis plan before any of these correlations was computed; the same pairs, statistics "
         "and rule as the rows above. Held-out likelihood: the total bound (ELBO) in nats per transition of the "
         "test-selection file (`onestep.loglik_nats_per_transition.elbo`), components not tested separately. Fixed-"
         f"candidate decision fidelity (the study brief, K = 2): per instance, Spearman's rho between the emulator's "
         f"mean margin over its two search samples and the engine's margin (the majority oracle's) on the instance's "
         f"first {DEC_PLANS} logged behaviour plans; the mean over instances, leaving out those where either side is "
         "constant. Both on the final checkpoints. Random search selects on the same emulator scores, so this measure's "
         "verdict is read on disjoint cities: the measure on the 40 cities against false acceptance on the 80 new ones "
         "(the row marked **verdict**); the reverse and the same-city rows beside it.", "",
         "| x | x: cities | false acceptance at 1,000: cities | pairs | checkpoints | pooled Spearman | within-family "
         "mean Spearman | abs < 0.3 | interval on abs above 0.3 | row |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    order = [f"{HELDOUT_X}|{s}" for s in ALL_SETS] + [f"{DEC_X[sx]}|{sy}" for sx, sy, _ in DEC_ROWS]
    for key in order:
        b = res["secondary"][key]
        xk, sy = key.split("|")
        sx = b.get("x_cities", "test selection")
        sxd = sx[1:] if sx in SET_DESC else sx
        role = "**verdict**" if b.get("verdict_row") else ("beside" if "role" in b else "")
        nck = f"{b['n_checkpoints']} of {b.get('n_finals', '?')} finals"
        if "pooled_spearman" not in b:
            L.append(f"| {b['x_description']} | {sxd} | {sy[1:]} | {b['n_pairs']} | {nck} | not computed | | | | {role} |")
            continue
        L.append(f"| {b['x_description']} | {sxd} | {sy[1:]} | {b['n_pairs']} | {nck} | "
                 f"{fe(b['pooled_spearman'])} | {fe(b.get('within_mean_spearman'))} | {_yn(b['abs_below_0.3'])} | "
                 f"{_yn(b['interval_abs_above_0.3'])} | {role} |")
    L.append("")
    for key in order:
        b = res["secondary"][key]
        if "not_computed" in b:
            L.append(f"- `{key}` not computed: {b['not_computed']}.")
    L.append("")
    L += ["Per final checkpoint. Decision fidelity: the mean over instances [instances with a rank correlation; left "
          "out: emulator constant / engine constant / both]; the recovery check (random-search records whose selected "
          "row's recovered margin equals the record's `grader_score`, and the largest error); the second reading (where "
          f"the audit stores the 8-sample pass share of the first {DEC_PLANS} plans: the mean, over instances with both, "
          "of the probability that a plan the emulator accepts has the higher recovered margin than one it rejects).", "",
          "| checkpoint | held-out likelihood (nats / transition) | decision fidelity, 40 | recovery check, 40 | second "
          "reading, 40 | decision fidelity, 80 |",
          "|---|---|---|---|---|---|"]
    for c, e in zip(g["checkpoints"], g["ladder"]):
        if e["stage"] != "final":
            continue
        ll = next((r[HELDOUT_X] for r in g["rows"] if r["checkpoint"] == c["checkpoint"]), NAN)

        def dv(d):
            if d.get("status") != "ok":
                st = d.get("status", "n/a")
                return "not computable (below)" if st.startswith("not computable") else st
            lo = d["left_out_constant"]
            return (f"{fx(d['value'])} [{d['n_defined']}; {lo['emulator']} / {lo['engine']} / {lo['both']}]")
        d40, d80 = c["decision_fidelity"]["c40"], c["decision_fidelity"]["c80"]
        rc = d40.get("recovery_check")
        rcs = f"{rc['n_records']} records, max error {rc['max_abs_error']:.1e}" if rc else "n/a"
        sr = d40.get("second_reading_check")
        srs = f"{fx(sr['mean_auc'])} ({sr['n_instances_with_both']} instances)" if sr else "not stored"
        L.append(f"| {c['checkpoint']} | {fx(ll, 2) if np.isfinite(ll) else c['heldout_loglik']} | {dv(d40)} | {rcs} | "
                 f"{srs} | {dv(d80)} |")
    L.append("")
    for s, src in g["nine_seed_mean_sources"].items():
        if src["status"] == "ok":
            L.append(f"- Nine-seed engine mean, {SET_DESC[s]}: from `{src['source']}` (truth-seed pool mean plus truth "
                     f"residual minus residual); cross-checked with {len(src['cross_checked_with'])} other run(s), largest "
                     f"difference {src['max_abs_difference_between_sources']:.1e}.")
        else:
            L.append(f"- Nine-seed engine mean, {SET_DESC[s]}: {src['status']}.")
    L.append(f"- Recovered margins closer than {DEC_TIE_TOL:g} are ranked as one value (the recovery reproduces the "
             "emulator's tied scores only to a few ulp); the largest gap merged and the smallest gap kept are in "
             "`checkpoints[].decision_fidelity.<cities>.ties`.")
    L.append("")
    return L


def nested_md(res: dict) -> list[str]:
    ns = res.get("seeded_nested_set")
    if not ns:
        return []
    L = ["## The pool-seeded search on the analysis plan's nested set", "",
         f"x: `{ns['x']}`. A checkpoint is done when {ns['done_test']}. The row is computed on the largest complete set "
         "(the same statistics as section 2); random search on the same checkpoints beside it.", "",
         "| set | checkpoints (expected) | done | complete |", "|---|---|---|---|"]
    for k in ns["order"]:
        s = ns["sets"][k]
        L.append(f"| {s['name']} | {s['n_checkpoints']} ({s['n_expected']}) | {s['n_done']} | {_yn(s['complete'])} |")
    L += ["", f"**{ns['status']}.**", ""]
    if ns["rows"]:
        L += ["| x | y | role | pairs (expected) | checkpoints | pooled Spearman | Kendall | within-family mean Spearman "
              "| ranked within family |", "|---|---|---|---|---|---|---|---|---|"]
        for key, b in ns["rows"].items():
            x, y = key.split("|")
            if "pooled_spearman" not in b:
                L.append(f"| `{x}` | `{y}` | {b['role']} | {b['n_pairs']} ({b['n_pairs_expected']}) | "
                         f"{b['n_checkpoints']} | n/a ({b.get('status')}) | | | |")
                continue
            L.append(f"| `{x}` | `{y}` | {b['role']} | {b['n_pairs']} ({b['n_pairs_expected']}) | {b['n_checkpoints']} | "
                     f"{fe(b['pooled_spearman'])} | {fe(b['pooled_kendall'])} | {fe(b.get('within_mean_spearman'))} | "
                     f"{fe(b['ranked_within_spearman'])} |")
        L.append("")
    done = [c for c, v in ns["checkpoints"].items() if v["done"]]
    L.append(f"- Done: {', '.join(done) if done else 'none'}.")
    L.append("")
    return L


def exploratory_md(res: dict) -> list[str]:
    """The analysis plan's exploratory comparator ."""
    ex = res.get("exploratory_logged_plan")
    if not ex:
        return []
    P = ex["status"].upper()
    L = [f"## Single-plan comparator: one logged plan per instance against the search  ({P})", "",
         f"Added after's review (M7) and defined in the analysis plan before any 120-city input was complete. E1: the "
         f"statistics of sections 2 and 3 with random search's false acceptance at budget {E_BUDGET} (one logged plan per "
         "instance, judged by the emulator on 8 fresh samples and by the 32-seed oracle; no search) in place of budget "
         "1,000. E2: Spearman at 1,000 minus Spearman at budget 1 on the pairs that hold both, both recomputed on every "
         "cluster resample (clusters = checkpoints; percentile intervals). The 120-city rows carry the wording fixed in "
         "advance; the 40- and 80-city rows are reported beside them. The protocol deciding row and rule (section 2) "
         "do not change.", "",
         "Wording, read on E2's interval: above zero: \"" + E_WORDING["above"] + "\"; includes zero: \"" +
         E_WORDING["includes"] + "\"; below zero: \"" + E_WORDING["below"] + "\".", ""]
    if ex["status"] != "complete":
        L += [f"**{P}.** Every number below is computed on the inputs that existed when this file was written and is "
              "partial; the 120-city rows carry no wording until the main claim's inputs are complete.", ""]
    L += ["### E1: false acceptance at budget 1 as the predictor", "",
          "| x: cities | y | pairs | checkpoints | Spearman [95 %] | Kendall [95 %] | Spearman, lineage clusters | "
          "mean of the within-family Spearman | ranked within family | role |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for key, row in ex["rows"].items():
        b = row["E1"]
        if "pooled_spearman" not in b:
            L.append(f"| {SET_DESC[row['cities']]} | `{row['y']}` | {b['n_pairs']} | {b['n_checkpoints']} | n/a "
                     f"({b.get('status')}) | | | | | {row['role']} |")
            continue
        L.append(f"| {SET_DESC[row['cities']]} | `{row['y']}` | {b['n_pairs']} | {b['n_checkpoints']} | "
                 f"{fe(b['pooled_spearman'])} | {fe(b['pooled_kendall'])} | {fe(b['pooled_spearman_lineage'])} | "
                 f"{fe(b.get('within_mean_spearman'))} | {fe(b['ranked_within_spearman'])} | {row['role']} |")
    L += ["", "Per family (one point per checkpoint), E1:", "",
          "| x: cities | y | " + " | ".join(FAMILIES) + " |", "|---|---|" + "---|" * len(FAMILIES)]
    for key, row in ex["rows"].items():
        per = row["E1"].get("per_family", {})
        L.append(f"| {SET_DESC[row['cities']]} | `{row['y']}` | " + " | ".join(
            (fe(per[f]["spearman"]) + f" ({per[f]['n']})") if "spearman" in per.get(f, {}) else
            f"n/a ({per.get(f, {}).get('n', 0)})" for f in FAMILIES) + " |")
    L += ["", "### E2: Spearman at 1,000 minus Spearman at budget 1 (same pairs, same resamples)", "",
          "| x: cities | y | pairs | checkpoints | Spearman at 1,000 | Spearman at 1 | difference, pooled | difference, "
          "lineage clusters | difference, mean of the within-family values | difference, ranked within family | wording |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for key, row in ex["rows"].items():
        b = row["E2"]
        if row["cities"] != POOLED:
            w = "reported beside (no wording)"
        elif row["wording_status"] != "made":
            w = "no wording: partial inputs (applied when the main claim's inputs are complete)"
        else:
            w = "; ".join(f"{dict(E_SCOPES)[k]}: \"{v}\"" if v else f"{dict(E_SCOPES)[k]}: no interval"
                          for k, v in row["wording"].items())
        if "pooled_spearman_difference" not in b:
            L.append(f"| {SET_DESC[row['cities']]} | `{row['y']}` | {b['n_pairs']} | {b['n_checkpoints']} | n/a "
                     f"({b.get('status')}) | | | | | | {w} |")
            continue
        L.append(f"| {SET_DESC[row['cities']]} | `{row['y']}` | {b['n_pairs']} | {b['n_checkpoints']} | "
                 f"{fe(b['pooled_spearman_search'])} | {fe(b['pooled_spearman_logged_plan'])} | "
                 f"{fe(b['pooled_spearman_difference'])} | {fe(b['pooled_spearman_difference_lineage'])} | "
                 f"{fe(b.get('within_mean_spearman_difference'))} | {fe(b['ranked_within_spearman_difference'])} | {w} |")
    L += ["", "Per family, E2 (difference [95 %] (pairs)):", "",
          "| x: cities | y | " + " | ".join(FAMILIES) + " |", "|---|---|" + "---|" * len(FAMILIES)]
    for key, row in ex["rows"].items():
        per = row["E2"].get("per_family", {})
        L.append(f"| {SET_DESC[row['cities']]} | `{row['y']}` | " + " | ".join(
            (fe(per[f]["spearman_difference"]) + f" ({per[f]['n']})") if "spearman_difference" in per.get(f, {}) else
            f"n/a ({per.get(f, {}).get('n', 0)})" for f in FAMILIES) + " |")
    L += ["", f"- Per-pair values at budget {E_BUDGET}: `pairs.csv`, columns `random_<cities>_<statistic>_{E_BUDGET}` "
          f"(after every earlier column) and `missing_budget_{E_BUDGET}`.", ""]
    return L


def main_d79_md(res: dict) -> list[str]:
    d = res.get("main_d79")
    if not d:
        return []
    P = d["status"].upper()
    L = [f"## The analysis plan: the main claim's permutation null, sensitivities and within-family power ({P})", "",
         "The verdict stays on the protocol row and rule (section 2). Beside it: (a) the pooled Spearman under a "
         f"within-family permutation null (the RL variable permuted among checkpoints within each task family, "
         f"{d['permutation']['n_perm']} permutations, seed {d['permutation']['seed']}): the pooled value \""
         + D79_MAIN_WORDING["null_above"] + "\" if it lies above the null's 97.5th percentile, \""
         + D79_MAIN_WORDING["null_not_above"] + "\" otherwise; (b) the within-family Spearman (mean of the family values, "
         "section 3) as the reading for ranking emulators: \"" + D79_MAIN_WORDING["within_excludes"] + "\" if its interval "
         "excludes zero (with the estimate and whether it reaches 0.4), \"" + D79_MAIN_WORDING["within_includes"] + "\" if "
         "it includes zero. The 120-city rows carry the wording; the 80-city row is the check on audit data unseen when "
         "every rule was fixed.", ""]
    if d["status"] != "complete":
        L += [f"**{P}.** Every number below is partial; the 120-city rows carry no wording until the main claim's inputs "
              "are complete.", ""]
    L += ["| x: cities | y | pairs | observed pooled Spearman | null 2.5 / 50 / 97.5 percentiles | above the 97.5th | "
          "within-family Spearman [95 %] | excludes 0 | reaches 0.4 | role | wording |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for key, row in d["rows"].items():
        pn, wf = row["permutation_null"], row.get("within_family", {})
        if row["cities"] == POOLED:
            w = ("no wording: partial inputs" if row["wording_status"] != "made" else
                 "; ".join(f"{k}: \"{v}\"" for k, v in row["wording"].items() if v))
        else:
            w = "reported beside (no wording)"
        nul = (f"{pn['null_p2_5']:+.3f} / {pn['null_median']:+.3f} / {pn['null_p97_5']:+.3f}" if pn.get("status") == "ok"
               else pn.get("status", "n/a"))
        L.append(f"| {SET_DESC[row['cities']]} | `{row['y']}` | {row['n_pairs']} | "
                 f"{fx(pn.get('observed')) if pn.get('status') == 'ok' else 'n/a'} | {nul} | "
                 f"{_yn(pn.get('observed_above_null_p97_5'))} | {fe(wf.get('estimate'))} | {_yn(wf.get('excludes_0'))} | "
                 f"{_yn(wf.get('reaches_0.4'))} | {row['role']} | {w} |")
    L += ["", "### Sensitivities of the original design (appendix)", "",
          "| x: cities | y | Spearman, clustered by task family [95 %] | Pearson, checkpoint clusters [95 %] | leave one "
          "lineage out: range of the pooled Spearman | lineages |", "|---|---|---|---|---|---|"]
    for key, row in d["rows"].items():
        sv = row.get("sensitivity")
        if not sv:
            L.append(f"| {SET_DESC[row['cities']]} | `{row['y']}` | n/a | | | |")
            continue
        rg = sv["leave_one_lineage_out_range"]
        L.append(f"| {SET_DESC[row['cities']]} | `{row['y']}` | {fe(sv['clustered_by_task_family'])} | "
                 f"{fe(sv['pearson_checkpoint_clusters'])} | {'n/a' if not rg else f'{rg[0]:+.3f} to {rg[1]:+.3f}'} | "
                 f"{len(sv['leave_one_lineage_out'])} |")
    L += ["", "Leave one lineage out, each lineage (pooled Spearman, checkpoint clusters):", ""]
    for key, row in d["rows"].items():
        sv = row.get("sensitivity")
        if sv:
            L.append(f"- {SET_DESC[row['cities']]}, `{row['y']}`: " + "; ".join(
                f"without {k}: {fe(v['spearman'])} ({v['n_pairs']} pairs)" for k, v in sv["leave_one_lineage_out"].items())
                + ".")
    L += ["", "### Power of the within-family reading, by simulation", "", d["power_assumptions"], "",
          "| checkpoints | families | true within-family Spearman | power (interval excludes 0) | interval above 0 | "
          "estimate at least 0.4 |", "|---|---|---|---|---|---|"]
    for k, c in d["power_cells"].items():
        L.append(f"| {c['n_checkpoints']} | {c['n_families']} | {c['true_within_family_spearman']:.1f} | "
                 f"{c['power_interval_excludes_0']:.2f} | {c['power_interval_above_0']:.2f} | "
                 f"{c['share_estimate_at_least_0.4']:.2f} |")
    L += ["", f"- Monte Carlo standard error of each power: at most {0.5 / math.sqrt(D79_SIM):.3f}. A row's own cells: "
          "its checkpoints now, and the protocol 24.", ""]
    return L


def secondary_d79_md(res: dict) -> list[str]:
    d = res.get("secondary_d79")
    if not d:
        return []
    P = d["status"].upper()
    L = [f"## The analysis plan: the secondary claim on its checkpoint set, the analysis plan's rule ({P})", "",
         f"Checkpoint set: {d['checkpoint_set']}." + (f" Departure: {d['departure']}." if d["departure"] else ""), "",
         "The analysis plan: a measure is falsified if the interval on |Spearman| of its pooled verdict row lies above 0.3; the "
         "twelve-month rollout error (three readings) is falsified if any reading is; the claim is falsified if any "
         "measure is. The analysis plan: if it is not falsified and the power to falsify at a true |Spearman| of 0.5 is below "
         "0.8, the wording is \"" + D79_SEC_WORDING["not_falsifiable"] + "\". Checkpoint-level rows (one point per "
         "checkpoint: the measure against the mean over the five families of the false acceptance) beside the pooled "
         "rows; they are not part of the rule.", ""]
    if d["status"] != "complete":
        L += [f"**{P}.** No wording until the main claim's inputs are complete and every verdict row holds the whole set "
              f"(verdict rows hold the set now: {_yn(d.get('verdict_rows_hold_the_set'))}); the numbers below are partial.",
              ""]
    L += ["| measure | verdict row | pairs | checkpoints | pooled Spearman [95 %] | interval on abs above 0.3 | power to "
          "falsify, pooled | checkpoint-level Spearman [95 %] (checkpoints) | power, checkpoint level |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m in d["measures"]:
        for key, v in m["rows"].items():
            pb, cl = v["pooled"], v["checkpoint_level"]
            L.append(f"| {m['measure']} | `{key}` | {pb.get('n_pairs')} | {pb.get('n_checkpoints')} | "
                     f"{fe(pb.get('pooled_spearman'))} | {_yn(v['falsified'])} | {fx(v['power_pooled'], 2)} | "
                     f"{fe(cl.get('spearman'))} ({cl.get('n_checkpoints')}) | {fx(v['power_checkpoint_level'], 2)} |")
    L += [""]
    if d["wording_status"] == "made":
        L += [f"**Verdict : {d['n_measures_falsified']} of {len(d['measures'])} measures falsified; the claim: "
              f"\"{d['wording']['claim']}\".** By measure: " + "; ".join(f"{k}: \"{v}\"" for k, v in
                                                                      d["wording"]["by_measure"].items()) + "."
              + (" Not falsified, with a verdict row of power at least 0.8: "
                 + ", ".join(d["wording"]["measures_not_falsified_with_power_at_least_0.8"]) + "."
                 if d["wording"]["measures_not_falsified_with_power_at_least_0.8"] else ""), ""]
    else:
        L += ["No wording: partial inputs.", ""]
    L += ["### Power to falsify, by simulation", "", d["power_assumptions"], "",
          "| false acceptance: cities | checkpoints | share of variance between families | power, pooled row | power, "
          "checkpoint-level row |", "|---|---|---|---|---|"]
    for sy, p in d["power"].items():
        if "power_pooled" not in p:
            L.append(f"| {sy[1:]} | n/a ({p.get('status')}) | | | |")
            continue
        L.append(f"| {sy[1:]} | {p['n_checkpoints']} | {p['decomposition']['share_between_families']:.2f} | "
                 f"{p['power_pooled']:.2f} | {p['power_checkpoint_level']:.2f} |")
    L += ["", "### Checkpoint-level rows beside every pooled secondary row (on that row's own checkpoints)", "",
          "| pooled row | checkpoints | checkpoint-level Spearman [95 %] | abs < 0.3 | interval on abs above 0.3 |",
          "|---|---|---|---|---|"]
    for key, cl in d["checkpoint_level_beside_existing"].items():
        if cl.get("status") != "ok":
            L.append(f"| `{key}` | {cl['n_checkpoints']} | n/a ({cl.get('status')}) | | |")
            continue
        L.append(f"| `{key}` | {cl['n_checkpoints']} | {fe(cl['spearman'])} | {_yn(cl['abs_below_0.3'])} | "
                 f"{_yn(cl['interval_abs_above_0.3'])} |")
    L.append("")
    return L


def horizon_24m_md(res: dict) -> list[str]:
    d = res.get("horizon_24m_predictors")
    if not d:
        return []
    P = d["status"].upper()
    cov = d["coverage"]
    L = [f"## 24-month trajectory-fidelity predictors against consistent exploitation targets ({P})", "",
         f"Held-out 24-month rollout records: {cov['n_finals_heldout_test']} finals in `test/` and "
         f"{cov['n_halves_heldout_test_half']} half-trained checkpoints in `test_half/` "
         f"({cov['n_total_heldout_test_24m']} of {cov['n_ladder_total']} ladder checkpoints; "
         f"{cov['n_total_dev_24m']} on `dev/`). Bootstrap resamples: {d['n_boot']:,} (seed {d['seed']}).", ""]
    for sk, sb in d["sets"].items():
        L += [f"### {sb['description']}", "",
              "| 24m metric | target | pairs | ckpts | pooled Spearman [95 %] | within-family Spearman [95 %] | "
              "partial Spearman (size + data) [95 %] | within-family partial (size + data) [95 %] |",
              "|---|---|---|---|---|---|---|---|"]
        for mk, mdesc in HORIZON_24M_METRICS:
            for yk, _ in HORIZON_24M_TARGETS:
                c = sb["metrics"][mk][yk]
                if c.get("status") != "ok":
                    L.append(f"| {mdesc} | `{yk}` | {c.get('n_pairs', 0)} | {c.get('n_checkpoints', 0)} | n/a | n/a | n/a | n/a |")
                    continue
                L.append(f"| {mdesc} | `{yk}` | {c['n_pairs']} | {c['n_checkpoints']} | "
                         f"{fe(c['pooled_spearman'])} | {fe(c.get('within_mean_spearman'))} | "
                         f"{fe(c['partial_spearman_size_data'])} | {fe(c.get('within_partial_spearman_size_data'))} |")
        L.append("")
    return L


def lineage_6_md(res: dict) -> list[str]:
    d = res.get("lineage_6_cluster_bootstrap")
    if not d:
        return []
    P = d["status"].upper()
    L = [f"## 6-lineage cluster bootstrap alongside 24-checkpoint bootstrap ({P})", "",
         f"Lineages: {d['lineage_definition']}. Bootstrap resamples: {d['n_boot']:,} (seed {d['seed']}).", "",
         "| predictor | target | pairs | pooled Spearman (24 ckpts) | pooled Spearman (6 lineages) | "
         "within-family Spearman (24 ckpts) | within-family Spearman (6 lineages) |",
         "|---|---|---|---|---|---|---|"]
    for key, c in d["rows"].items():
        xk, yk = key.split("|")
        if c.get("status") != "ok":
            L.append(f"| `{xk}` | `{yk}` | {c.get('n_pairs', 0)} | n/a | n/a | n/a | n/a |")
            continue
        L.append(f"| `{xk}` | `{yk}` | {c['n_pairs']} | {fe(c['pooled_spearman_ckpt24'])} | "
                 f"{fe(c['pooled_spearman_lineage6'])} | {fe(c.get('within_mean_spearman_ckpt24'))} | "
                 f"{fe(c.get('within_mean_spearman_lineage6'))} |")
    L.append("")
    return L


def write_markdown(path: Path, g: dict, res: dict, argv: list[str], generated: str):
    rows, status = g["rows"], res["status"]
    P = status.upper()
    nfam = len(FAMILIES)
    L = [f"# Across emulators: does the cheap audit predict what reinforcement learning overstates? ({P})", ""]
    if status == "partial":
        L.append(f"**{P}.** {res['n_pairs_primary']} of {LADDER_SIZE * nfam} checkpoint-by-family pairs "
                 f"({res['n_checkpoints_primary']} of {LADDER_SIZE} checkpoints) have both variables of the main test "
                 f"(random search's false acceptance at 1,000 on {SET_DESC[POOLED]}, and the margin inflation of all "
                 f"three RL seeds). Every number below is computed on the inputs that existed when this file was "
                 f"written and is partial.")
    else:
        L.append(f"**{P}.** All {LADDER_SIZE * nfam} pairs have both variables of the main test.")
    L += ["", f"Generated {generated} by `{' '.join(argv)}`. Statistics fixed in the specification (and its round 2), the "
          f"study protocol (section 1; amendments 3, 4, 7) and the analysis plan. Cluster bootstrap, {res['n_boot']} "
          f"resamples, seed {res['seed']}, 95 per cent percentile intervals (`hpr_dream.stats`). Per-pair values: "
          f"`pairs.csv`; figure data: `fig5_*.csv`; the main checkpoint on three city sets: `replication.md`; the "
          f"coverage model: `coverage.md`.", "",
          f"City sets: {SET_DESC['c40']} (`{Path(g['tasks']['c40']['path']).name}`, "
          f"{sum(g['tasks']['c40']['n'].values())} instances), {SET_DESC['c80']} (`{Path(g['tasks']['c80']['path']).name}`, "
          f"{sum(g['tasks']['c80']['n'].values())} instances) and {SET_DESC['c120']} (both pooled: a pair's rate is "
          f"events over the instances of both, its excess paired by instance against each file's perfect emulator). The "
          f"main claim's audit variable is the 120-city value ; the 40 and the 80 are reported beside it.", ""]

    # 1. inputs
    L += ["## 1. Inputs", "",
          f"Ladder checkpoints found: {len(g['ladder'])} (protocol: {LADDER_SIZE}); task families: "
          f"{', '.join(FAMILIES)} (40 cities: {', '.join(str(g['tasks']['c40']['n'][f]) for f in FAMILIES)} instances; "
          f"80 cities: {', '.join(str(g['tasks']['c80']['n'][f]) for f in FAMILIES)}).", "",
          "| checkpoint | objective | size | data (transitions) | stage | lineage | random, 40 | random, 80 | seeded, 40 "
          "| seeded, 80 | RL runs with all 3 snapshots (of 15) | fidelity dev | fidelity test | pairs with both main variables |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    lad = {e["checkpoint"]: e for e in g["ladder"]}
    for ck in g["checkpoints"]:
        e = lad[ck["checkpoint"]]
        nboth = sum(1 for r in rows if r["checkpoint"] == ck["checkpoint"] and _usable(r, PRIMARY_X) and _usable(r, PRIMARY_Y))
        dtr = f"{e['data_transitions']:,}" if e["data_transitions"] is not None else "n/a"
        a = ck["audit"]
        L.append(f"| {e['checkpoint']} | {e['objective']} | {e['size']} | {e['data_index']} ({dtr}) | {e['stage']} | "
                 f"{e['lineage']} | {a['random_c40']} | {a['random_c80']} | {a['cem_seeded_c40']} | {a['cem_seeded_c80']} | "
                 f"{ck['rl_runs_complete']} | {ck['fidelity']['dev']} | {ck['fidelity']['test']} | {nboth} |")
    L.append("")

    # 2. the main test
    L += ["## 2. The protocol test, as amended", "",
          "x: random search's false acceptance at 1,000 on the pair's instances. y: the RL variable, mean of three RL "
          "seeds of the frozen learner. Spearman over all pairs; cluster bootstrap by checkpoint. Decision rule (protocol "
          f"section 1): supported if the estimate is at least {THRESHOLD} and the interval excludes 0; falsified if the "
          f"interval lies below {THRESHOLD}; otherwise undecided at this power. It is applied to one row: "
          f"{SET_DESC[POOLED]} against the margin inflation .", "",
          "| x: cities | y | pairs | clusters (checkpoints) | Spearman [95 %] | Kendall [95 %] | lineages | Spearman, "
          "lineage clusters [95 %] | decision |",
          "|---|---|---|---|---|---|---|---|---|"]
    for s in ALL_SETS:
        for yk, _ in Y_VARS:
            b = res["main"][s][yk]
            L.append(f"| {SET_DESC[s]} | `{yk}` | {b['n_pairs']} | {b['n_checkpoints']} | {fe(b.get('pooled_spearman'))} | "
                     f"{fe(b.get('pooled_kendall'))} | {b['n_lineages']} | {fe(b.get('pooled_spearman_lineage'))} | "
                     f"{decision_text(b, status)} |")
    pw = res["power"]
    L += ["", f"Achieved, for the deciding row: {pw['n_pairs']} pairs in {pw['n_clusters']} clusters "
          f"({fx(pw['pairs_per_cluster'], 2)} pairs per cluster). Independent pairs needed for 80 per cent power at "
          f"Spearman {THRESHOLD} (two-sided, 5 per cent, Fisher z): {pw['n_independent_for_80_per_cent']}."]
    for icc, v in pw["at_icc"].items():
        L.append(f"- At intra-checkpoint correlation {icc} (the protocol's design effect 1 + (m - 1) rho): design effect "
                 f"{fx(v['design_effect'], 2)}, effective pairs {fx(v['n_eff'], 1)}, power to detect {THRESHOLD}: "
                 f"{fx(v['power_spearman_0.4'], 2)}.")
    if "icc_measured" in pw:
        L.append("- Measured ICC(1) by checkpoint on these pairs: " + "; ".join(
            f"`{k}` {fx(v, 3)}" for k, v in pw["icc_measured"].items()) + ".")
    L.append("")

    # 3. within family
    L += ["## 3. Within task family", "",
          "Spearman inside each family, one point per checkpoint (bootstrap over checkpoints); the mean of the family "
          f"values (families with at least {MIN_FAMILY_PAIRS} pairs; bootstrap over checkpoints, every family recomputed "
          "on each resample); the pooled Spearman of within-family percentile ranks, (rank - 0.5) / n, recomputed on "
          "each resample. Columns: the three city sets of the audit variable.", ""]
    for yk, _ in Y_VARS:
        L += [f"### y: `{yk}`", "",
              "| scope | pairs (120 / 40 / 80) | Spearman, 120 | Kendall, 120 | Spearman, 40 | Kendall, 40 | Spearman, 80 | Kendall, 80 |",
              "|---|---|---|---|---|---|---|---|"]
        bs = {s: res["main"][s][yk] for s in ALL_SETS}

        def cells(get):
            out = []
            for s in ALL_SETS:
                sp, kd = get(bs[s])
                out += [fe(sp), fe(kd)]
            return " | ".join(out)

        def npairs(get_n):
            return " / ".join(str(get_n(bs[s])) for s in ALL_SETS)

        L.append(f"| pooled | {npairs(lambda b: b['n_pairs'])} | "
                 f"{cells(lambda b: (b.get('pooled_spearman'), b.get('pooled_kendall')))} |")
        for f in FAMILIES:
            L.append(f"| {f} | {npairs(lambda b: b.get('per_family', {}).get(f, {}).get('n', 0))} | "
                     f"{cells(lambda b: (b.get('per_family', {}).get(f, {}).get('spearman'), b.get('per_family', {}).get(f, {}).get('kendall')))} |")
        L.append(f"| mean of families | {npairs(lambda b: b['n_pairs'])} | "
                 f"{cells(lambda b: (b.get('within_mean_spearman'), b.get('within_mean_kendall')))} |")
        L.append(f"| pooled, ranked within family | {npairs(lambda b: b['n_pairs'])} | "
                 f"{cells(lambda b: (b.get('ranked_within_spearman'), None))} |")
        L.append("")
        for s in ALL_SETS:
            b = bs[s]
            if "pooled_spearman" not in b:
                L.append(f"- {SET_DESC[s]}: no estimate ({b.get('status')}).")
                continue
            ex, inc = [], []
            items = [("pooled", b["pooled_spearman"])] + [(f, b["per_family"][f]["spearman"]) for f in FAMILIES
                                                          if "spearman" in b["per_family"][f]]
            if "within_mean_spearman" in b:
                items.append(("mean of families", b["within_mean_spearman"]))
            items.append(("pooled after ranking within family", b["ranked_within_spearman"]))
            for name, e in items:
                z = excludes_zero(e)
                (ex if z else inc).append(name if z is not None else f"{name} (no interval)")
            L.append(f"- {SET_DESC[s]} ({status}): Spearman intervals that exclude 0: {', '.join(ex) if ex else 'none'}. "
                     f"Intervals that include 0: {', '.join(inc) if inc else 'none'}.")
        L.append("")

    # 4. reliability
    L += ["## 4. Reliability", "",
          "Per family, over the pairs of the main test (each city set's own pairs). Audit: the binomial standard error "
          "of each pair's false acceptance, sqrt(p (1 - p) / n) with n the pair's instances, against the standard "
          "deviation of the pair values across checkpoints. RL: the standard error of each pair's three-seed mean, (seed "
          "standard deviation) / sqrt(3), against the standard deviation of the means across checkpoints. Reliability "
          "lambda = 1 - mean(SE^2) / variance across checkpoints. Attenuation (classical formula, for a linear "
          "correlation): r_observed = r_true x sqrt(lambda_audit x lambda_RL), a lambda at or below 0 entering as 0.", ""]
    for yk, _ in Y_VARS:
        L += [f"### y: `{yk}`", "",
              "| family | cities | pairs | audit RMS SE | audit SD across checkpoints | lambda audit | RL seed SD (RMS) | "
              "RL SE of the mean (RMS) | RL SD across checkpoints | lambda RL | attenuation factor | observed value of a true 0.4 |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for f in FAMILIES:
            for s in ALL_SETS:
                e = res["reliability"][s][f]
                if "audit" not in e:
                    L.append(f"| {f} | {s[1:]} | {e['n']} | n/a ({e.get('status')}) | | | | | | | | |")
                    continue
                a, y = e["audit"], e[yk]
                L.append(f"| {f} | {s[1:]} | {e['n']} | {fx(a['rms_se'])} | {fx(a['sd_between'])} | {fx(a['reliability'], 2)} | "
                         f"{fx(y['rms_seed_sd'])} | {fx(y['rms_seed_se_of_mean'])} | {fx(y['sd_between'])} | "
                         f"{fx(y['reliability'], 2)} | {fx(y['attenuation_factor'], 2)} | {fx(y['observed_if_true_0.4'], 2)} |")
        L.append("")
    L += ["### Split-sample reliability of the audit variable", "",
          "Per family, across every checkpoint audited on both city files (no RL variable needed): Spearman and Pearson "
          "between a pair's 40-city and 80-city false acceptance at 1,000 (random search). Spearman-Brown for forms of "
          "unequal length: with k1 and k2 the instance counts, r = sqrt(rho(k1) rho(k2)) and rho(k) = k rho_1 / (1 + (k - 1) "
          "rho_1); solved for the per-instance rho_1 from Pearson's r, it gives the reliability of the 40, the 80 and the "
          "pooled 120. Beside it, the binomial-formula reliability of each on the same checkpoints.", "",
          "| family | checkpoints with both | Spearman 40 vs 80 | Pearson 40 vs 80 | Spearman-Brown: 40 | 80 | pooled 120 | "
          "binomial: 40 | 80 | pooled 120 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for f in FAMILIES:
        e = res["split_sample"][f]
        if "pearson" not in e:
            L.append(f"| {f} | {e['n_checkpoints']} | n/a ({e['status']}) | | | | | | | |")
            continue
        sbv, bi = e["spearman_brown"], e["binomial"]
        L.append(f"| {f} | {e['n_checkpoints']} | {fx(e['spearman'])} | {fx(e['pearson'])} | {fx(sbv['rho_k1'], 2)} | "
                 f"{fx(sbv['rho_k2'], 2)} | {fx(sbv['rho_pooled'], 2)} | {fx(bi['c40'], 2)} | {fx(bi['c80'], 2)} | "
                 f"{fx(bi['c120'], 2)} |")
    L.append("")

    # 5. alternatives
    L += ["## 5. Alternatives (a fixed table, not a search)", "",
          "The same pooled and within-family statistics with the audit variable replaced. Fidelity numbers are per "
          "checkpoint (constant across its five families); the test selection holds finals only. For fidelity rows, "
          f"the secondary claim's question: is |pooled Spearman| below {SECONDARY_ABS}?", ""]
    for yk, _ in Y_VARS:
        L += [f"### y: `{yk}`", "",
              "| x | pairs | checkpoints | lineages | pooled Spearman | pooled Kendall | pooled Spearman, lineage clusters | "
              "within-family mean Spearman | within-family mean Kendall | ranked within family | abs < 0.3 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for xk, xdesc in X_VARS:
            b = res["alternatives"][f"{xk}|{yk}"]
            if "pooled_spearman" not in b:
                L.append(f"| {xdesc} | {b['n_pairs']} | {b['n_checkpoints']} | {b['n_lineages']} | n/a | n/a | n/a | "
                         f"n/a | n/a | n/a | |")
                continue
            ab = b.get("abs_below_0.3")
            L.append(f"| {xdesc} | {b['n_pairs']} | {b['n_checkpoints']} | {b['n_lineages']} | {fe(b['pooled_spearman'])} | "
                     f"{fe(b['pooled_kendall'])} | {fe(b['pooled_spearman_lineage'])} | {fe(b.get('within_mean_spearman'))} | "
                     f"{fe(b.get('within_mean_kendall'))} | {fe(b['ranked_within_spearman'])} | "
                     f"{'' if ab is None else ('yes' if ab else 'no')} |")
        L.append("")

    # 6. secondary claim
    L += ["## 6. The secondary claim as protocol (fidelity against random search's false acceptance at 1,000)",
          "", "protocol: static fidelity correlates with false acceptance at 1,000 across the ladder at "
          f"|Spearman| under {SECONDARY_ABS}; falsified if the interval on |Spearman| lies above {SECONDARY_ABS} (here: the "
          f"interval lies wholly above {SECONDARY_ABS} or wholly below -{SECONDARY_ABS}). Pairs with the audit variable; "
          "no RL variable needed. The 120-city audit variable first, the 40 and the 80 beside it.", "",
          "| x | cities | pairs | checkpoints | pooled Spearman | within-family mean Spearman | abs < 0.3 | interval on abs above 0.3 |",
          "|---|---|---|---|---|---|---|---|"]
    xdesc = dict(X_VARS)
    for s in ALL_SETS:
        for xk in FID_X:
            b = res["secondary"][f"{xk}|{s}"]
            if "pooled_spearman" not in b:
                L.append(f"| {xdesc[xk]} | {s[1:]} | {b['n_pairs']} | {b['n_checkpoints']} | n/a | n/a | | |")
                continue
            ia = b["interval_abs_above_0.3"]
            L.append(f"| {xdesc[xk]} | {s[1:]} | {b['n_pairs']} | {b['n_checkpoints']} | {fe(b['pooled_spearman'])} | "
                     f"{fe(b.get('within_mean_spearman'))} | {'yes' if b['abs_below_0.3'] else 'no'} | "
                     f"{'n/a' if ia is None else ('yes' if ia else 'no')} |")
    L.append("")
    L += secondary_more_md(g, res)
    L += nested_md(res)
    L += exploratory_md(res)
    L += main_d79_md(res)
    L += secondary_d79_md(res)
    L += horizon_24m_md(res)
    L += lineage_6_md(res)

    # 7. missing
    L += ["## 7. What is missing", ""]
    for m in METHODS:
        for s in SETS:
            bad = [c["checkpoint"] + f" ({c['audit'][f'{m}_{s}']})" for c in g["checkpoints"] if c["audit"][f"{m}_{s}"] != "ok"]
            L.append(f"- Audit, {m}, {SET_DESC[s]}: missing or unusable for {len(bad)} of {len(g['ladder'])} checkpoints"
                     + (f": {', '.join(bad)}." if bad else "."))
    rl_short = [f"{c['checkpoint']} ({c['rl_runs_complete']}/15)" for c in g["checkpoints"]
                if c["rl_runs_complete"] < len(RL_SEEDS) * nfam]
    fid_dev = [c["checkpoint"] for c in g["checkpoints"] if c["fidelity"]["dev"] != "ok"]
    fid_test = [c["checkpoint"] for c in g["checkpoints"]
                if c["fidelity"]["test"] != "ok" and lad[c["checkpoint"]]["stage"] == "final"]
    excess = sorted({r["checkpoint"] for r in rows if any(t.startswith("excess_") for t in r["missing"].split(";") if t)})
    L += [f"- RL runs (family x seed) with all three evaluation summaries short of 15 for {len(rl_short)} checkpoints"
          + (f": {', '.join(rl_short)}." if rl_short else "."),
          f"- Excess over the perfect emulator not computable (records not all paired) for: {', '.join(excess) if excess else 'none'}.",
          f"- Fidelity, development selection, missing for: {', '.join(fid_dev) if fid_dev else 'none'}; test selection "
          f"(finals) missing for: {', '.join(fid_test) if fid_test else 'none'}."]
    if g["ladder_notes"]:
        L.append("- Ladder enumeration notes: " + "; ".join(g["ladder_notes"]) + ".")
    L.append("")
    L += ["## Checks made while reading", "",
          "- Audit: the run's tasks sha256 equals its city file's; the card's judge checkpoint sha256 equals the "
          "checkpoint's; every record judged by the majority oracle; no duplicate record keys; the card's all-instance "
          "false acceptance equals the records' at every budget; every family's instances are exactly the city file's; "
          "the two city files share no instance; the perfect emulator paired on every record (else the excess is left "
          "empty); where a run has reference.json, the records reproduce its per-family values.",
          "- RL: environment emulator, the frozen learner, the checkpoint path and sha256, the tasks file sha256 and the "
          "instance list as expected; each summary is evaluation version 3 at the month count of its file name with the "
          "family's instance count; the gap equals dream minus oracle acceptance.",
          "- Fidelity: one decoding per checkpoint and split; the sample count and checkpoint sha256 as expected."]
    for c in g["checkpoints"]:
        for m, chk in c["reference_json_check"].items():
            L.append(f"- `{c['checkpoint']}` {m}: reference.json agrees with the records in {chk['agree']} values"
                     + (f", differs in {len(chk['differ'])}: {'; '.join(chk['differ'][:5])}" if chk["differ"] else "") + ".")
        for m, ns in c["audit_notes"].items():
            L.append(f"- `{c['checkpoint']}` {m}: {'; '.join(ns)}.")
        if c["rl_notes"]:
            L.append(f"- `{c['checkpoint']}` RL: {'; '.join(c['rl_notes'][:5])}"
                     + (f" (and {len(c['rl_notes']) - 5} more)" if len(c["rl_notes"]) > 5 else "") + ".")
    L.append("")
    Path(path).write_text("\n".join(L))


def write_replication_md(path: Path, rep: dict, argv: list[str], generated: str, n_boot: int):
    P = rep["status"].upper()
    L = [f"# The main checkpoint's headline on three city sets ({P})", "",
         f"Checkpoint `{rep['checkpoint']}`. Random search and the pool-seeded search at each budget, on {SET_DESC['c40']}, "
         f"{SET_DESC['c80']} and {SET_DESC['c120']}, each beside the same search in a perfect emulator (the engine judging "
         f"itself on fresh seeds) on the same instances. Cluster bootstrap over start-state families, {n_boot} resamples, "
         "seed 0, BCa 95 per cent intervals (`hpr_dream.stats`, as the audit's reference tables); `*` the percentile "
         "interval where BCa is undefined; `†` no event, the exact one-sided bound on clusters. Generated "
         f"{generated} by `{' '.join(argv)}`.", ""]
    if rep["status"] != "complete":
        L += [f"**{P}.** Missing: " + ("; ".join(rep["missing"]) if rep["missing"] else "the 80-city pool-seeded run") + ".", ""]
    st = rep.get("statement", {})
    if "c80_excludes_0" in st:
        lo, hi = st["c80_interval"]
        line = (f"**Statement ({rep['status']}).** Pool-seeded search at 1,000, 80 new cities: the difference from the "
                f"perfect emulator's {st['c80_interval_kind']} interval [{lo:+.3f}, {hi:+.3f}] "
                f"{'excludes' if st['c80_excludes_0'] else 'includes'} 0.")
        if "c40_point" in st:
            line += (f" The 40-city point estimate {st['c40_point']:+.3f} lies "
                     f"{'inside' if st['c40_point_inside_c80_interval'] else 'outside'} the 80-city interval.")
        L += [line, ""]
    else:
        L += [f"**Statement.** Not computable: the pool-seeded search on the 80 new cities, paired with its perfect "
              f"emulator, does not exist yet ({rep['status']}).", ""]
    names = {"random": "Random search", "cem_seeded": "Pool-seeded search"}
    for m, by_b in rep["methods"].items():
        L += [f"## {names.get(m, m)}", "",
              "| B | cities | n | false acceptance, emulator | false acceptance, perfect | difference | real success, "
              "emulator | real success, perfect | false rejection, emulator | false rejection, perfect |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for B, row in by_b.items():
            for s in ALL_SETS:
                v = row[s]
                if "emulator" not in v:
                    L.append(f"| {B} | {s[1:]} | n/a | {v['status']} | | | | | | |")
                    continue
                em, pe = v["emulator"], v.get("perfect_emulator", {})
                dif = fbs(v["difference"]) if "difference" in v else v.get("perfect_status", "n/a")
                L.append(f"| {B} | {s[1:]} | {v['n']} | {fb(em['hackability'])} | {fb(pe.get('hackability'))} | "
                         f"{dif} | {fb(em['oracle_accept'])} | {fb(pe.get('oracle_accept'))} | "
                         f"{fb(em['false_rejection'])} | {fb(pe.get('false_rejection'))} |")
        L.append("")
    if rep["checks"]:
        L += ["## Checks", ""] + [f"- {c}." for c in rep["checks"]] + [""]
    L += replication_d79_md(rep.get("statement_d79"))
    bc = rep.get("budget_contrast_d99")
    if bc:
        L += [f"- The analysis plan: random search's excess over the perfect emulator at "
              f"{bc['budgets'][0]:,} minus at budget {bc['budgets'][1]} (one logged plan), paired by instance: "
              + "; ".join(f"{SET_DESC[s]} {fbs(bc[s]['contrast'])} ({bc[s]['n']} instances)" if bc[s]["status"] == "ok"
                          else f"{SET_DESC[s]} {bc[s]['status']}" for s in (POOLED, "c40"))
              + " (BCa; `*` percentile where BCa is undefined).", ""]
    Path(path).write_text("\n".join(L))


def replication_d79_md(sd: dict | None) -> list[str]:
    if not sd:
        return []
    names = {"random": "Random search", "cem_seeded": "Pool-seeded search"}
    L = [f"## The analysis plan's replication statement , at {D79_B:,} evaluations", "",
         "\"Replicates\" if the interval of the excess over the perfect emulator on the 80 new cities excludes zero; "
         "\"consistent in size\" if the interval of the 80-minus-40 difference includes zero. Excess intervals as the "
         "tables above (BCa; `*` percentile where BCa is undefined); the difference: independent cluster bootstraps over "
         "the two sets of cities, percentile interval of the replicate differences.", "",
         "| search | excess, 40 cities (n) | excess, 80 cities (n) | 80 minus 40 [95 %] | 80-city interval excludes 0 | "
         "difference's interval includes 0 | reading |", "|---|---|---|---|---|---|---|"]
    for m, v in sd.items():
        if v.get("status") != "ok":
            L.append(f"| {names.get(m, m)} | {v.get('status')} | | | | | |")
            continue
        d = v["difference_c80_minus_c40"]
        L.append(f"| {names.get(m, m)} | {fbs(v['excess_c40'])} ({v['n_c40']}) | {fbs(v['excess_c80'])} ({v['n_c80']}) | "
                 f"{d['value']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}] | {_yn(v['c80_excess_interval_excludes_0'])} | "
                 f"{_yn(v['difference_interval_includes_0'])} | {v['reading']['c80']}; {v['reading']['size']} |")
    L += ["", f"- Difference interval: {next(iter(sd.values()))['difference_interval']}.", ""]
    return L


def write_coverage_md(path: Path, cov: dict, argv: list[str], generated: str, n_boot: int):
    P = cov["status"].upper()
    L = [f"# Coverage arm: the coverage model against the main model ({P})", "",
         f"Coverage model `{cov['coverage']}`, main model `{cov['main']}`, on {SET_DESC['c40']}, paired by instance. Each "
         "model beside the perfect emulator; the difference is coverage minus main on the instances both hold. Cluster "
         f"bootstrap over start-state families, {n_boot} resamples, seed 0, BCa 95 per cent intervals (`*` percentile "
         f"where BCa is undefined; `†` no event, the exact one-sided bound). Generated {generated} by `{' '.join(argv)}`.", ""]
    if cov["missing"]:
        L += [f"**{P}.** Missing: " + "; ".join(cov["missing"]) + ".", ""]
    names = {"random": "Random search", "best_of_n": "Best-of-N", "cem_seeded": "Pool-seeded search"}
    for m, mv in cov["methods"].items():
        L += [f"## {names[m]}", ""]
        if not mv["budgets"]:
            L += [f"Not computable: main model {mv['status']['main']}, coverage model {mv['status']['coverage']}.", ""]
            continue
        L += ["| B | scope | n | false acceptance: coverage / main | excess over perfect: coverage / main | real success: "
              "coverage / main | false rejection: coverage / main | emulator accepts: coverage / main | coverage minus "
              "main: false acceptance | excess | real success | false rejection | emulator accepts |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for B, res in mv["budgets"].items():
            for scope, v in res.items():
                if "coverage" not in v:
                    L.append(f"| {B} | {scope} | n/a | {v['status']} | | | | | | | | | |")
                    continue
                c, mn, d = v["coverage"], v["main"], v["coverage_minus_main"]
                L.append(f"| {B} | {scope} | {d['n']} | {fb(c['emulator']['hackability'])} / {fb(mn['emulator']['hackability'])} | "
                         f"{fbs(c.get('difference'))} / {fbs(mn.get('difference'))} | "
                         f"{fb(c['emulator']['oracle_accept'])} / {fb(mn['emulator']['oracle_accept'])} | "
                         f"{fb(c['emulator']['false_rejection'])} / {fb(mn['emulator']['false_rejection'])} | "
                         f"{fb(c['emulator']['judge_accept'])} / {fb(mn['emulator']['judge_accept'])} | "
                         f"{fbs(d.get('hackability'))} | {fbs(d.get('excess_over_perfect'))} | {fbs(d.get('oracle_accept'))} | "
                         f"{fbs(d.get('false_rejection'))} | {fbs(d.get('judge_accept'))} |")
        L.append("")
    mo = SNAPSHOTS[-1]
    L += [f"## RL at {mo:,} months (mean over seeds [standard deviation], seeds)", "",
          "| family | margin inflation: coverage | main | acceptance gap: coverage | main | closed-loop acceptance: coverage | main |",
          "|---|---|---|---|---|---|---|"]
    for f in FAMILIES:
        c, mn = cov["rl"]["coverage"][f]["values"], cov["rl"]["main"][f]["values"]

        def rv(v, k):
            n = v[f"rl_n_seeds_{mo}"]
            return "n/a (0 seeds)" if n == 0 else f"{fx(v[f'rl_{k}_{mo}'])} [{fx(v[f'rl_{k}_sd_{mo}'])}], {n}"
        L.append(f"| {f} | {rv(c, 'inflation')} | {rv(mn, 'inflation')} | {rv(c, 'gap')} | {rv(mn, 'gap')} | "
                 f"{rv(c, 'closed_accept')} | {rv(mn, 'closed_accept')} |")
    srcs = sorted({s for f in FAMILIES for s in cov["rl"]["coverage"][f]["source"]})
    L += ["", f"Coverage model's RL runs read from: {', '.join(srcs) if srcs else 'none found'}.", "",
          "## Fidelity (one model sample; engine under another seed as the yardstick)", "",
          "| split | metric | coverage | main | engine yardstick |", "|---|---|---|---|---|"]
    for sp in ("dev", "test"):
        c, mn = cov["fidelity"]["coverage"][sp], cov["fidelity"]["main"][sp]
        for key, _, desc in FIDELITY_METRICS:
            L.append(f"| {sp} | {desc} | {fx(c['values'][key]) if c['status'] == 'ok' else c['status']} | "
                     f"{fx(mn['values'][key]) if mn['status'] == 'ok' else mn['status']} | "
                     f"{fx(mn['engine_yardstick'][key]) if mn['status'] == 'ok' else 'n/a'} |")
    files = [cov["fidelity"][w][sp].get("file") for w in ("coverage", "main") for sp in ("dev", "test")]
    L += ["", "Fidelity files: " + "; ".join(f"`{p}`" for p in files if p) + ".", ""]
    L += coverage_decision_md(cov.get("decision_fidelity"))
    Path(path).write_text("\n".join(L))


def coverage_decision_md(d: dict | None) -> list[str]:
    """Minor 1 of : the coverage model's fixed-candidate decision fidelity beside the main's."""
    if not d:
        return []
    L = ["## Fixed-candidate decision fidelity, 40 cities ", "",
         f"Computed exactly as the analysis plan computes it for the finals: {d['definition']}; read from each model's "
         "random-search audit (`pools.npz`), the engine's nine-seed mean from the 40 cities' engine reference. The "
         "paired rows: instances where both models' rank correlations are defined, coverage minus main per instance, "
         f"{d['interval']}.", ""]
    if d["status"] != "ok":
        return L + [f"Not computed: {d['status']}.", ""]

    def one(v):
        rc = v.get("recovery_check") or {}
        return (f"{fx(v['value'])} over {v['n_defined']} of {v['n_instances']} instances (left out, constant: emulator "
                f"{v['left_out_constant']['emulator']}, engine {v['left_out_constant']['engine']}, both "
                f"{v['left_out_constant']['both']}); recovery check on {rc.get('n_records')} records, largest error "
                f"{rc.get('max_abs_error', NAN):.1e}")
    L += [f"- Coverage model: {one(d['coverage'])}.", f"- Main model: {one(d['main'])}"
          + (f"; equals the value in `main_claim.json`: {_yn(d.get('main_equals_the_ladder_value'))}." ), "",
          "| scope | instances (both defined) | clusters | coverage | main | coverage minus main | instances: coverage "
          "higher / main higher |", "|---|---|---|---|---|---|---|"]
    for scope, v in d["paired"].items():
        if "coverage" not in v:
            L.append(f"| {scope} | 0 | | n/a ({v['status']}) | | | |")
            continue
        L.append(f"| {scope} | {v['n_instances']} | {v['n_clusters']} | {fb(v['coverage'])} | {fb(v['main'])} | "
                 f"{fbs(v['coverage_minus_main'])} | {v['n_instances_coverage_higher']} / {v['n_instances_main_higher']} |")
    L += ["", f"- Instances with the measure defined for the main model only: {d['n_defined_main_only']}; for the "
          f"coverage model only: {d['n_defined_coverage_only']}.", ""]
    return L


def summary_lines(res: dict, rep: dict, cov: dict) -> list[str]:
    st = res["status"].upper()
    out = [f"[{st}] pairs with both main variables ({PRIMARY_X} x {PRIMARY_Y}): {res['n_pairs_primary']} of "
           f"{LADDER_SIZE * len(FAMILIES)} ({res['n_checkpoints_primary']} checkpoints)"]
    for s in ALL_SETS:
        for yk, _ in Y_VARS:
            b = res["main"][s][yk]
            if "pooled_spearman" not in b:
                out.append(f"[{st}] x={s} y={yk}: {b.get('status')}")
                continue
            out.append(f"[{st}] x={s} y={yk}: pairs {b['n_pairs']}, clusters {b['n_checkpoints']}, Spearman "
                       f"{fe(b['pooled_spearman'])}, Kendall {fe(b['pooled_kendall'])}; {decision_text(b, res['status'])}")
    pw = res["power"]
    out.append(f"[{st}] deciding row: pairs {pw['n_pairs']}, clusters {pw['n_clusters']}; power at ICC 0.3 / 0.5: "
               + " / ".join(fx(v["power_spearman_0.4"], 2) for v in pw["at_icc"].values()))
    ss = res["split_sample"]
    n_both = max(e["n_checkpoints"] for e in ss.values())
    out.append(f"[{st}] split-sample reliability: at most {n_both} checkpoints with both city files per family"
               + ("" if n_both >= MIN_FAMILY_PAIRS else f" (needs {MIN_FAMILY_PAIRS}): not computed"))
    for f, e in ss.items():
        if "pearson" in e:
            out.append(f"[{st}]   {f}: Pearson {fx(e['pearson'])}, Spearman {fx(e['spearman'])}; SB 40/80/120 "
                       f"{fx(e['spearman_brown']['rho_k1'], 2)}/{fx(e['spearman_brown']['rho_k2'], 2)}/"
                       f"{fx(e['spearman_brown']['rho_pooled'], 2)}; binomial {fx(e['binomial']['c40'], 2)}/"
                       f"{fx(e['binomial']['c80'], 2)}/{fx(e['binomial']['c120'], 2)}")
    out.append(f"[{rep['status'].upper()}] replication: {rep.get('statement') or 'statement not computable'}")
    out.append(f"[{cov['status'].upper()}] coverage: {len(cov['missing'])} inputs missing")
    # the secondary claim's further measures  and the analysis plan's nested set
    for key in [f"{HELDOUT_X}|{s}" for s in ALL_SETS] + [f"{DEC_X[sx]}|{sy}" for sx, sy, _ in DEC_ROWS]:
        b = res["secondary"].get(key)
        if b is None:
            continue
        tag = " (verdict row)" if b.get("verdict_row") else ""
        if "pooled_spearman" not in b:
            out.append(f"[{st}] secondary {key}{tag}: not computed ({b.get('not_computed', b.get('status'))})")
            continue
        out.append(f"[{st}] secondary {key}{tag}: pairs {b['n_pairs']}, checkpoints {b['n_checkpoints']}, Spearman "
                   f"{fe(b['pooled_spearman'])}; abs < 0.3: {_yn(b['abs_below_0.3'])}; interval on abs above 0.3: "
                   f"{_yn(b['interval_abs_above_0.3'])}")
    ns = res.get("seeded_nested_set")
    if ns:
        out.append(f"[{st}] seeded search, the analysis plan's nested set: {ns['status']} ("
                   + "; ".join(f"{ns['sets'][k]['name']}: {ns['sets'][k]['n_done']} of {ns['sets'][k]['n_expected']} done"
                               for k in ns["order"]) + ")")
    # the analysis plan: pairs and wording status only (the values are in main_claim.json / .md, marked as the main claim's)
    ex = res.get("exploratory_logged_plan")
    if ex:
        for key, row in ex["rows"].items():
            w = row.get("wording_status", "reported beside (no wording)")
            out.append(f"[{st}] exploratory  {key}: E1 pairs {row['E1']['n_pairs']}, E2 pairs "
                       f"{row['E2']['n_pairs']} ({row['E2']['n_checkpoints']} checkpoints); wording: {w}")
    if res.get("main_d79"):
        md = res["main_d79"]
        out.append(f"[{st}] the analysis plan (values in main_claim.json / .md): rows "
                   + "; ".join(f"{k} pairs {v['n_pairs']}" for k, v in md["rows"].items())
                   + f"; power cells {len(md['power_cells'])}; 120-city wording: "
                   + md["rows"][f"{POOLED}|{PRIMARY_Y}"]["wording_status"])
    if res.get("secondary_d79"):
        sd = res["secondary_d79"]
        out.append(f"[{sd['status'].upper()}] the analysis plan: set {sd['n_checkpoints_in_set']} checkpoints "
                   f"(test_half present for {sd['n_half_with_test_half']}); wording: {sd['wording_status']}")
    if rep.get("statement_d79"):
        out.append(f"[{rep['status'].upper()}] replication, the analysis plan (values in replication.json / .md): "
                   + "; ".join(f"{m} {v.get('status')}" for m, v in rep["statement_d79"].items()))
    if cov.get("decision_fidelity"):
        out.append(f"[{cov['status'].upper()}] coverage, fixed-candidate decision fidelity: "
                   f"{cov['decision_fidelity']['status']}")
    return out


def main(argv: list[str] | None = None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(ROOT), help="repository root (results are read under <root>/results)")
    ap.add_argument("--ckpt-root", default=str(CKPT_ROOT), help="the ladder's training runs")
    ap.add_argument("--tasks", default=str(TASKS_40), help="the 40 cities' tasks file")
    ap.add_argument("--tasks-x", default=str(TASKS_80), help="the 80 new cities' tasks file")
    ap.add_argument("--engine-reference", default=str(ENGINE_REF),
                    help="perfect-emulator runs, <dir>/<tasks stem>/{B_economy,cem_seeded_B_economy}, used when a run "
                         "has no reference.json")
    ap.add_argument("--cov-fidelity-fallback", default=str(COV_FIDELITY_FALLBACK),
                    help="tree read for the coverage model's fidelity when the main tree has none")
    ap.add_argument("--cov-rl-fallback", default=str(COV_RL_FALLBACK),
                    help="tree read for the coverage model's RL runs when the main tree has none")
    ap.add_argument("--out", default=None, help="output directory (default <root>/results/analysis)")
    ap.add_argument("--n-boot", type=int, default=hs.N_BOOT)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4, help="processes for the correlation blocks (CPU)")
    a = ap.parse_args(argv)
    root = Path(a.root)
    out = Path(a.out) if a.out else root / "results" / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    g = gather(root, Path(a.ckpt_root), {"c40": Path(a.tasks), "c80": Path(a.tasks_x)}, Path(a.engine_reference))
    res = analyse(g["rows"], n_boot=a.n_boot, seed=a.seed, workers=a.workers)
    annotate_secondary(res, g)
    res["seeded_nested_set"] = seeded_nested_set(g, g["rows"], a.n_boot, a.seed, a.workers)
    # the analysis plan , after every earlier result
    res["main_d79"] = main_d79(g["rows"], res, a.n_boot, a.seed, a.workers)
    res["secondary_d79"] = secondary_d79(g, g["rows"], res, a.n_boot, a.seed)
    n_boot_20k = N_BOOT_CLUSTER_20K if a.n_boot >= hs.N_BOOT else a.n_boot
    res["horizon_24m_predictors"] = horizon_24m_predictors(g, g["rows"], n_boot_20k, a.seed, a.workers)
    res["lineage_6_cluster_bootstrap"] = lineage_6_cluster_bootstrap(g, g["rows"], n_boot_20k, a.seed, a.workers)
    rep = replication(g, a.n_boot, a.seed)
    cov = coverage(g, root, Path(a.ckpt_root), Path(a.engine_reference), Path(a.cov_fidelity_fallback),
                   Path(a.cov_rl_fallback), a.n_boot, a.seed)
    cmd = ["PYTHONPATH=hpr-dream:code", ".venv/bin/python", "code/scripts/analyse_ladder.py"] + \
        (sys.argv[1:] if argv is None else list(argv))
    rows = g["rows"]
    write_csv(out / "pairs.csv", rows)
    scat_cols = ["checkpoint", "family", "lineage", "objective", "size", "data_index", "stage"] + \
        [f"random_{s}_{k}_1000" for s in ALL_SETS for k in ("hack", "n")] + \
        ["rl_inflation_1000000", "rl_inflation_sd_1000000", "rl_gap_1000000", "rl_gap_sd_1000000",
         "rl_dream_accept_1000000", "rl_oracle_open_accept_1000000", "rl_closed_accept_1000000", "rl_n_seeds_1000000"]
    scat = [r for r in rows if any(_usable(r, f"random_{s}_hack_1000") for s in ALL_SETS) and _usable(r, PRIMARY_Y)]
    write_csv(out / "fig5_scatter.csv", [{**r, "status": res["status"]} for r in scat], scat_cols + ["status"])
    write_csv(out / "fig5_correlations.csv", correlation_rows(res))
    rel_rows = []
    for s in ALL_SETS:
        for f, e in res["reliability"][s].items():
            if "audit" not in e:
                continue
            for yk, _ in Y_VARS:
                rel_rows.append({"cities": s, "family": f, "y": yk, "n_pairs": e["n"], "audit_rms_se": e["audit"]["rms_se"],
                                 "audit_sd_between": e["audit"]["sd_between"],
                                 "audit_reliability": e["audit"]["reliability"],
                                 **{f"rl_{k}": v for k, v in e[yk].items()}, "status": res["status"]})
    write_csv(out / "fig5_reliability.csv", rel_rows)
    ss_rows = [{"family": f, "n_checkpoints": e["n_checkpoints"], "spearman": e.get("spearman"),
                "pearson": e.get("pearson"), "sb_c40": e.get("spearman_brown", {}).get("rho_k1"),
                "sb_c80": e.get("spearman_brown", {}).get("rho_k2"), "sb_c120": e.get("spearman_brown", {}).get("rho_pooled"),
                "binomial_c40": e.get("binomial", {}).get("c40"), "binomial_c80": e.get("binomial", {}).get("c80"),
                "binomial_c120": e.get("binomial", {}).get("c120"), "status": res["status"]}
               for f, e in res["split_sample"].items()]
    write_csv(out / "fig5_split_sample.csv", ss_rows)
    definitions = {"x": dict(X_VARS), "y": dict(Y_VARS), "primary_x": PRIMARY_X, "primary_y": PRIMARY_Y,
                   "city_sets": SET_DESC,
                   "decision_rule": f"supported if Spearman >= {THRESHOLD} and its 95 % cluster-bootstrap interval "
                                    f"(clusters = checkpoints) excludes 0; falsified if the interval lies below "
                                    f"{THRESHOLD}; otherwise undecided at this power; applied to {PRIMARY_X} x {PRIMARY_Y} "
                                    f"on the complete ladder",
                   "bootstrap": f"{a.n_boot} resamples, seed {a.seed}, percentile, hpr_dream.stats.cluster_draws",
                   "families": list(FAMILIES), "budgets": list(BUDGETS), "snapshots": list(SNAPSHOTS),
                   "rl_seeds": list(RL_SEEDS), "rl_variant": RL_VARIANT, "min_family_pairs": MIN_FAMILY_PAIRS,
                   "lineage": "the one-step run a checkpoint descends from (itself for one-step checkpoints, the run of "
                              "init_from for self-forced ones)",
                   "secondary_further_x": {HELDOUT_X: HELDOUT_DESC, **{DEC_X[s]: DEC_DESC[s] for s in ALL_SETS}},
                   "secondary_decision_fidelity_rows": {f"{DEC_X[sx]}|{sy}": role for sx, sy, role in DEC_ROWS},
                   "nine_seed_mean_sources": g["nine_seed_mean_sources"],
                   "exploratory_logged_plan": {
                       "decision": 77, "label": "single-plan comparator",
                       "x": E_DESC, "x_search": {s: E_SEARCH_X[s] for s in ALL_SETS},
                       "E1": f"the main claim's statistics (pooled, per family, mean of the within-family values, ranked "
                             f"within family) with x = random search's false acceptance at budget {E_BUDGET}",
                       "E2": f"Spearman with x at 1,000 minus Spearman with x at budget {E_BUDGET}, on the pairs holding "
                             "both, the same clusters resampled jointly",
                       "wording": E_WORDING, "wording_rows": f"{POOLED} (both RL variables); the 40- and 80-city rows "
                                                             "are reported beside them",
                       "pairs_csv_columns": [f"random_<cities>_<statistic>_{E_BUDGET}", f"missing_budget_{E_BUDGET}"]},
                   "decision_79": {
                       "main": "results.main_d79: within-family permutation null of the pooled Spearman "
                               f"({D79_N_PERM} permutations, seed {D79_PERM_SEED}); sensitivities (clustered by task "
                               "family; leave one lineage out; Pearson); the within-family reading; its power by "
                               "simulation", "main_wording": D79_MAIN_WORDING, "main_power_assumptions": SIM_WITHIN_ASSUMPTIONS,
                       "secondary": "results.secondary_d79: the analysis plan's verdict on the checkpoint set (24 if every "
                                    "half-trained checkpoint has test_half/ fidelity, else the 12 finals), checkpoint-level "
                                    "rows, power to falsify at a true |Spearman| of 0.5 by simulation",
                       "secondary_wording": D79_SEC_WORDING, "secondary_power_assumptions": SIM_FALSIFY_ASSUMPTIONS,
                       "measures": {n: list(k) for n, k in D78_MEASURES}}}
    js = {"status": res["status"], "generated_utc": generated, "command": " ".join(cmd), "definitions": definitions,
          "ladder": g["ladder"], "ladder_notes": g["ladder_notes"], "checkpoints": g["checkpoints"],
          "tasks": {s: {k: v for k, v in g["tasks"][s].items() if k != "instances"} for s in SETS}, "results": res}
    (out / "main_claim.json").write_text(json.dumps(_jsonable(js), indent=1))
    (out / "replication.json").write_text(json.dumps(_jsonable({"generated_utc": generated, "command": " ".join(cmd),
                                                                **rep}), indent=1))
    (out / "coverage.json").write_text(json.dumps(_jsonable({"generated_utc": generated, "command": " ".join(cmd),
                                                             **cov}), indent=1))
    write_markdown(out / "main_claim.md", g, res, cmd, generated)
    write_replication_md(out / "replication.md", rep, cmd, generated, a.n_boot)
    write_coverage_md(out / "coverage.md", cov, cmd, generated, a.n_boot)
    (out / "inputs_manifest.json").write_text(json.dumps({"generated_utc": generated, "files": g["reader"].manifest},
                                                          indent=1, sort_keys=True))
    for line in summary_lines(res, rep, cov):
        print(line)
    print(f"wrote {out}/pairs.csv ({len(rows)} rows), main_claim.md/.json, replication.md/.json, coverage.md/.json, "
          f"fig5_*.csv, inputs_manifest.json")
    return {"gather": g, "results": res, "replication": rep, "coverage": cov}


if __name__ == "__main__":
    main()
