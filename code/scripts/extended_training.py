#!/usr/bin/env python3
"""Sixfold extended one-step training control (os_50m_full_36m: 36,000,000 examples, 12 epochs).

Computes reproducible CPU-only summaries and city-clustered BCa 95 per cent intervals comparing the
12-epoch (36M-example) full-data 50M one-step world model against the 2-epoch (6M-example) primary
os_50m_full checkpoint and the exact-simulator reference across:
  1. Trajectory fidelity and held-out variational ELBO from 6M to 36M examples (dev, test, train_eval);
  2. Adaptive CEM at B = 10,000 across all 193 held-out core instances (and B = 10..10,000 scaling);
  3. Random shooting (B = 1..1,000) and adaptive CEM (B = 1,000) across all 120 held-out cities (574 instances);
  4. In-imagination PPO (15 runs: 5 task families x 3 seeds at 1,000,000 steps) and initial-plan reference verdicts;
  5. Out-of-sample cross-model correlation when adding os_50m_full_36m to the 24-checkpoint ladder (25 checkpoints,
     125 checkpoint-by-task pairs).

Usage:
    CUDA_VISIBLE_DEVICES="" PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/extended_training.py
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "code", ROOT / "hpr-dream"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import numpy as np  # noqa: E402

from hpr_dream import stats as hs  # noqa: E402
from scripts import analyse_ladder as AL  # noqa: E402
from scripts import pressure_axis as PA  # noqa: E402
from scripts import rl_axis as RX  # noqa: E402

FAMILIES = ("grow", "solvent", "treasury", "recover", "power")
SPATIAL_FAMILIES = ("grow", "solvent", "recover", "power")
MILESTONES = (6_000_000, 12_000_000, 18_000_000, 24_000_000, 30_000_000, 36_000_000)
CKPT_6M = "os_50m_full-samples_006000000"
CKPT_36M = "os_50m_full_36m-samples_036000000"
N_BOOT = 2000
SEED = 0


def _val(x) -> float:
    if isinstance(x, (int, float)):
        return float(x)
    for k in ("sample", "model", "model_mae", "mae", "median"):
        if k in x:
            return float(x[k])
    return float(next(iter(x.values())))


def _clean_est(e: hs.Estimate) -> dict:
    d = e.as_dict()
    for k in ("lo", "hi", "bca_lo", "bca_hi"):
        v = d.get(k)
        if v is not None and isinstance(v, float) and not math.isfinite(v):
            d[k] = None
    return d


def bca_mean(vals: np.ndarray, clusters: np.ndarray, rate: bool = False) -> dict:
    return PA.bca_est(np.asarray(vals, dtype=float), np.asarray(clusters), N_BOOT, SEED, PA.LEVEL, rate=rate)


def bca_ratio(num: np.ndarray, den: np.ndarray, clusters: np.ndarray) -> dict:
    """Conditional rate sum(num) / sum(den) (e.g. false rejection among oracle-passing plans) with BCa cluster CI."""
    num = np.asarray(num, dtype=float)
    den = np.asarray(den, dtype=float)
    sel = den > 0.5
    if not sel.any():
        return {"value": None, "lo": None, "hi": None, "bca_lo": None, "bca_hi": None, "n_units": 0, "n_clusters": 0}
    return bca_mean(num[sel], np.asarray(clusters)[sel], rate=True)


# ---------------------------------------------------------------------------------------------------------------------
# 1. Trajectory fidelity and held-out likelihood (6M..36M vs 6M baseline)
# ---------------------------------------------------------------------------------------------------------------------
def summarise_fidelity_file(path: Path) -> dict:
    d = json.loads(path.read_text())
    ll = d["onestep"]["loglik_nats_per_transition"]
    st = d["onestep"]["model_T1"]["structural"]
    rw = d["onestep"]["model_T1"]["raw"]
    gc = d.get("gap_closed", {})
    h12 = d["rollouts"]["h12"]
    h24 = d["rollouts"]["h24"]
    ov = {}
    for grp in ("half", "eighth"):
        for k, v in h24[grp].items():
            ov[k] = float(v["ratio_sample"])
    ol = d["rollouts"]["by_subset"]["open_loop"]["h24"]["scalars"]
    f12_s = gc.get("tile_F1_since_start_12m_structural", {}).get("model")
    return {
        "file": str(path.relative_to(ROOT)),
        "elbo": float(ll["elbo"]),
        "kl": float(ll["kl"]),
        "f1_struct_1m": float(st["f1"]),
        "f1_struct_1m_ci95": [float(x) for x in st["f1_ci95_by_family"]],
        "f1_raw_1m": float(rw["f1"]),
        "f1_since_start_12m_struct": None if f12_s is None else float(f12_s),
        "pop_medrel_12m": _val(h12["median_rel_pop"]),
        "funds_medrel_12m": _val(h12["median_rel_funds"]),
        "overlays_24m": ov,
        "mean_overlay_ratio_24m": float(sum(ov.values()) / len(ov)),
        "n_overlays_ge_1": int(sum(1 for v in ov.values() if v >= 1.0)),
        "open_loop_powered_zones_mae_24m": _val(ol["powered_zones"]),
        "open_loop_funds_mae_24m": _val(ol["funds"]),
        "open_loop_pop_mae_24m": _val(ol["pop"]),
    }


def fidelity_section() -> dict:
    r36 = ROOT / "results" / "fidelity" / "ladder" / "os_50m_full_36m"
    r06 = ROOT / "results" / "fidelity" / "ladder" / "os_50m_full"
    fh = json.loads((ROOT / "results" / "analysis" / "fidelity_horizon.json").read_text())
    orig_test_row = next(r for r in fh["rows"] if r["run"] == "os_50m_full" and r["stage"] == "final" and r["split"] == "test")
    copy_pow = float(orig_test_row["open_loop_scalars_24m"]["scalars"]["powered_zones"]["copy_mae"])
    eng_pow = float(orig_test_row["open_loop_scalars_24m"]["scalars"]["powered_zones"]["engine_mae"])

    base = {}
    for sp in ("dev", "test", "train_eval"):
        p = r06 / sp / "os_50m_full_samples_006000000_dec-a.json"
        if not p.exists() and sp == "train_eval":
            p = ROOT / "results" / "fidelity" / "ladder" / "train_eval" / "os_50m_full_samples_006000000_dec-a.json"
        if p.exists():
            base[sp] = summarise_fidelity_file(p)

    miles = {sp: {} for sp in ("dev", "test", "train_eval")}
    for sp in ("dev", "test", "train_eval"):
        for m in MILESTONES:
            p = r36 / sp / f"os_50m_full_36m_samples_{m:09d}_dec-a.json"
            if p.exists():
                miles[sp][str(m)] = summarise_fidelity_file(p)

    slopes_path = r36 / "last_tenth_slopes.json"
    slopes = json.loads(slopes_path.read_text())["os_50m_full_36m"] if slopes_path.exists() else None
    t36 = miles["test"]["36000000"]
    t06 = base["test"]
    seeds_test = {}
    for rn in ("os_50m_full", "os_50m_full_s1", "os_50m_full_s2"):
        sp_path = ROOT / "results" / "fidelity" / "ladder" / rn / "test" / f"{rn}_samples_006000000_dec-a.json"
        if sp_path.is_file():
            seeds_test[rn] = summarise_fidelity_file(sp_path)
    return {
        "baseline_6m": base,
        "baseline_3seed_test": seeds_test,
        "milestones_36m": miles,
        "reference_yardsticks_test": {
            "open_loop_powered_zones_copy_mae_24m": copy_pow,
            "open_loop_powered_zones_engine_mae_24m": eng_pow,
        },
        "deltas_test_36m_minus_baseline_6m": {
            "elbo_nats": float(t36["elbo"] - t06["elbo"]),
            "f1_struct_1m": float(t36["f1_struct_1m"] - t06["f1_struct_1m"]),
            "funds_medrel_12m": float(t36["funds_medrel_12m"] - t06["funds_medrel_12m"]),
            "pop_medrel_12m": float(t36["pop_medrel_12m"] - t06["pop_medrel_12m"]),
            "mean_overlay_ratio_24m": float(t36["mean_overlay_ratio_24m"] - t06["mean_overlay_ratio_24m"]),
            "open_loop_powered_zones_mae_24m": float(
                t36["open_loop_powered_zones_mae_24m"] - t06["open_loop_powered_zones_mae_24m"]
            ),
        },
        "last_tenth_slopes": slopes,
    }


# ---------------------------------------------------------------------------------------------------------------------
# 2. Paired audit records helper (works for B=1..1,000 on 40/80/120 cities and B=10,000 on 193 core instances)
# ---------------------------------------------------------------------------------------------------------------------
def load_records(dirs: list[Path], method: str, budget: int) -> dict[str, dict]:
    out = {}
    for d in dirs:
        gz = d / "records.jsonl.gz"
        with gzip.open(gz, "rt") as fh:
            for ln in fh:
                r = json.loads(ln)
                if r["method"] != method or int(r["budget"]) != budget:
                    continue
                k = r["instance"]
                if k in out:
                    raise SystemExit(f"duplicate ({k}, {method}, {budget}) in {d}")
                acc = bool(r["grader_p_fresh"] >= 0.5)
                orc = bool(r["oracle_accept"])
                out[k] = {
                    "instance": k,
                    "cluster": r["cluster"],
                    "task": r["task"],
                    "in_band": bool(r["in_band"]),
                    "judge_accept": float(acc),
                    "oracle_accept": float(orc),
                    "false_acceptance": float(acc and not orc),
                    "false_reject_event": float((not acc) and orc),
                }
    return out


def paired_audit_cell(emu36: dict[str, dict], perf: dict[str, dict], emu06: dict[str, dict]) -> dict:
    keys = sorted(set(emu36) & set(perf) & set(emu06))
    if not (len(keys) == len(emu36) == len(perf) == len(emu06)):
        raise SystemExit(f"instance mismatch: 36m={len(emu36)}, perf={len(perf)}, 6m={len(emu06)}, common={len(keys)}")

    def block(ks: list[str]) -> dict:
        cl = np.array([emu36[k]["cluster"] for k in ks])
        fa36 = np.array([emu36[k]["false_acceptance"] for k in ks])
        fap = np.array([perf[k]["false_acceptance"] for k in ks])
        fa06 = np.array([emu06[k]["false_acceptance"] for k in ks])
        ja36 = np.array([emu36[k]["judge_accept"] for k in ks])
        jap = np.array([perf[k]["judge_accept"] for k in ks])
        ja06 = np.array([emu06[k]["judge_accept"] for k in ks])
        oa36 = np.array([emu36[k]["oracle_accept"] for k in ks])
        oap = np.array([perf[k]["oracle_accept"] for k in ks])
        oa06 = np.array([emu06[k]["oracle_accept"] for k in ks])
        fr36_ev = np.array([emu36[k]["false_reject_event"] for k in ks])
        frp_ev = np.array([perf[k]["false_reject_event"] for k in ks])
        fr06_ev = np.array([emu06[k]["false_reject_event"] for k in ks])

        ex36 = fa36 - fap
        ex06 = fa06 - fap
        sh36 = oa36 - oap
        sh06 = oa06 - oap
        return {
            "n": len(ks),
            "n_clusters": int(len(set(cl))),
            "ext_36m": {
                "false_acceptance": bca_mean(fa36, cl, rate=True),
                "judge_accept": bca_mean(ja36, cl, rate=True),
                "oracle_accept": bca_mean(oa36, cl, rate=True),
                "false_rejection": bca_ratio(fr36_ev, oa36, cl),
                "excess": bca_mean(ex36, cl),
                "shortfall": bca_mean(sh36, cl),
            },
            "main_6m": {
                "false_acceptance": bca_mean(fa06, cl, rate=True),
                "judge_accept": bca_mean(ja06, cl, rate=True),
                "oracle_accept": bca_mean(oa06, cl, rate=True),
                "false_rejection": bca_ratio(fr06_ev, oa06, cl),
                "excess": bca_mean(ex06, cl),
                "shortfall": bca_mean(sh06, cl),
            },
            "perfect": {
                "false_acceptance": bca_mean(fap, cl, rate=True),
                "judge_accept": bca_mean(jap, cl, rate=True),
                "oracle_accept": bca_mean(oap, cl, rate=True),
                "false_rejection": bca_ratio(frp_ev, oap, cl),
            },
            "diff_36m_minus_6m": {
                "excess": bca_mean(ex36 - ex06, cl),
                "oracle_accept": bca_mean(oa36 - oa06, cl),
                "judge_accept": bca_mean(ja36 - ja06, cl),
            },
        }

    wp_keys = [k for k in keys if emu36[k]["in_band"]]
    by_fam = {}
    for f in FAMILIES:
        fk = [k for k in keys if emu36[k]["task"] == f]
        by_fam[f] = block(fk)
    return {"all": block(keys), "well_posed": block(wp_keys), "by_family": by_fam}


def audit_1e4_section() -> dict:
    d36 = [ROOT / "results" / "audit_36m" / "seed1e4" / "tasks_v2_H24_cem_seeded_1e4"]
    dp = [
        ROOT / "results" / "audit" / "engine_reference" / "tasks_v2_H24" / "cem_seeded_1e4_i100",
        ROOT / "results" / "audit" / "engine_reference" / "tasks_v2_H24" / "cem_seeded_1e4_rest93",
    ]
    pa_orig = json.loads((ROOT / "results" / "analysis" / "pressure_axis.json").read_text())
    hi06 = pa_orig["inputs"]["emulator"]["high"]
    d06 = [ROOT / p for p in (hi06 if isinstance(hi06, list) else [hi06])]
    return paired_audit_cell(
        load_records(d36, "cem_seeded", 10000),
        load_records(dp, "cem_seeded", 10000),
        load_records(d06, "cem_seeded", 10000),
    )


def audit_120_and_pressure_section() -> tuple[dict | None, dict | None]:
    c_rand36 = ROOT / "results" / "audit_36m" / "core" / "tasks_v2_H24"
    c_cem36 = ROOT / "results" / "audit_36m" / "core" / "tasks_v2_H24_cem_seeded"
    x_rand36 = ROOT / "results" / "audit_36m" / "x80" / "tasks_v2x_H24"
    x_cem36 = ROOT / "results" / "audit_36m" / "x80" / "tasks_v2x_H24_cem_seeded"
    needed = (c_rand36, c_cem36, x_rand36, x_cem36)
    if not all((p / "records.jsonl.gz").is_file() for p in needed):
        return None, None

    c_rand06 = ROOT / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000" / "tasks_v2_H24"
    c_cem06 = ROOT / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000" / "tasks_v2_H24_cem_seeded"
    x_rand06 = ROOT / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000" / "tasks_v2x_H24"
    x_cem06 = ROOT / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000" / "tasks_v2x_H24_cem_seeded"

    c_rand_p = ROOT / "results" / "audit" / "engine_reference" / "tasks_v2_H24" / "B_economy"
    c_cem_p = ROOT / "results" / "audit" / "engine_reference" / "tasks_v2_H24" / "cem_seeded_B_economy"
    x_rand_p = ROOT / "results" / "audit" / "engine_reference" / "tasks_v2x_H24" / "B_economy"
    x_cem_p = ROOT / "results" / "audit" / "engine_reference" / "tasks_v2x_H24" / "cem_seeded_B_economy"

    aud = {"random": {}, "cem_seeded": {}}
    for B in (1, 10, 100, 1000):
        aud["random"][str(B)] = {
            "c40": paired_audit_cell(load_records([c_rand36], "random", B), load_records([c_rand_p], "random", B), load_records([c_rand06], "random", B)),
            "c80": paired_audit_cell(load_records([x_rand36], "random", B), load_records([x_rand_p], "random", B), load_records([x_rand06], "random", B)),
            "c120": paired_audit_cell(
                load_records([c_rand36, x_rand36], "random", B),
                load_records([c_rand_p, x_rand_p], "random", B),
                load_records([c_rand06, x_rand06], "random", B),
            ),
        }
    for B in (10, 100):
        aud["cem_seeded"][str(B)] = {
            "c40": paired_audit_cell(load_records([c_cem36], "cem_seeded", B), load_records([c_cem_p], "cem_seeded", B), load_records([c_cem06], "cem_seeded", B)),
        }
    aud["cem_seeded"]["1000"] = {
        "c40": paired_audit_cell(load_records([c_cem36], "cem_seeded", 1000), load_records([c_cem_p], "cem_seeded", 1000), load_records([c_cem06], "cem_seeded", 1000)),
        "c80": paired_audit_cell(load_records([x_cem36], "cem_seeded", 1000), load_records([x_cem_p], "cem_seeded", 1000), load_records([x_cem06], "cem_seeded", 1000)),
        "c120": paired_audit_cell(
            load_records([c_cem36, x_cem36], "cem_seeded", 1000),
            load_records([c_cem_p, x_cem_p], "cem_seeded", 1000),
            load_records([c_cem06, x_cem06], "cem_seeded", 1000),
        ),
    }

    # Pressure axis (B = 10..10,000 CEM + B = 1..1,000 random on the 193 core instances)
    d36_hi = [ROOT / "results" / "audit_36m" / "seed1e4" / "tasks_v2_H24_cem_seeded_1e4"]
    dp_hi = [
        ROOT / "results" / "audit" / "engine_reference" / "tasks_v2_H24" / "cem_seeded_1e4_i100",
        ROOT / "results" / "audit" / "engine_reference" / "tasks_v2_H24" / "cem_seeded_1e4_rest93",
    ]
    D = {
        "emulator": {**PA.load(c_cem36), **PA.load_many(d36_hi)},
        "perfect": {**PA.load(c_cem_p), **PA.load_many(dp_hi)},
    }
    R = {"emulator": PA.load(c_rand36, "random"), "perfect": PA.load(c_rand_p, "random")}
    inst = sorted({i for i, b in D["emulator"] if b == 10000} & {i for i, b in D["perfect"] if b == 10000})
    cluster = np.array([D["emulator"][(i, 10)][3] for i in inst])
    task = np.array([D["emulator"][(i, 10)][4] for i in inst])
    Xc = {side: {nm: np.array([[float(D[side][(i, B)][k]) for i in inst] for B in PA.CEM_BUDGETS]) for k, nm in enumerate(PA.NAMES)} for side in D}
    Xr = {side: {nm: np.array([[float(R[side][(i, B)][k]) for i in inst] for B in PA.RANDOM_BUDGETS]) for k, nm in enumerate(PA.NAMES)} for side in R}
    pa_bca = PA.bca_block(Xc, Xr, cluster, task, N_BOOT, SEED)
    pa_full = PA.axis(Xc, cluster, task, PA.CEM_BUDGETS, N_BOOT, SEED)
    return aud, {"n_instances": len(inst), "n_clusters": int(pa_full["n_clusters"]), "rows": pa_full["rows"], "bca": pa_bca}


# ---------------------------------------------------------------------------------------------------------------------
# 3. In-imagination PPO (15 runs of os_50m_full_36m vs os_50m_full and engine PPO)
# ---------------------------------------------------------------------------------------------------------------------
def rl_section() -> dict:
    rep36 = json.loads((ROOT / "results" / "analysis" / "extended_training.replays.json").read_text())["runs"]
    rep06 = json.loads((ROOT / "results" / "analysis" / "rl_axis.replays.json").read_text())["runs"]
    eng_map = RX.engine_runs()

    rows36, rows06, rows_eng = [], [], []
    for fam in FAMILIES:
        for s in (0, 1, 2):
            r36 = f"{CKPT_36M}__{fam}__s{s}__tasks_v2_H24"
            r06 = f"{CKPT_6M}__{fam}__s{s}__tasks_v2_H24"
            ir36 = RX.instance_rows(r36, CKPT_36M, RX.MONTHS, rep36[r36])
            ir06 = RX.instance_rows(r06, CKPT_6M, RX.MONTHS, rep06[r06])
            RX.summary_check(r36, RX.MONTHS, ir36)
            RX.summary_check(r06, RX.MONTHS, ir06)
            rows36 += ir36
            rows06 += ir06
        for reng in eng_map[fam]:
            ire = RX.instance_rows(reng, "engine", RX.MONTHS, rep06[reng])
            RX.summary_check(reng, RX.MONTHS, ire)
            rows_eng += ire

    arm36 = RX.Arm(rows36)
    arm06 = RX.Arm(rows06)
    arm_eng = RX.Arm(rows_eng)

    scopes = [("all", FAMILIES), ("spatial4", SPATIAL_FAMILIES)] + [(f, (f,)) for f in FAMILIES]
    out = {}
    for sc_name, fams in scopes:
        a36 = arm36.subset(fams)
        a06 = arm06.subset(fams)
        aen = arm_eng.subset(fams)
        cell = {"ext_36m": {}, "main_6m": {}, "engine": {}, "diff_36m_minus_6m": {}, "ext_36m_vs_engine": {}}
        for q in ("dream", "oracle", "gap", "closed", "infl", "fa0", "perfect_fa0", "excess0", "emu_accept0", "perfect_accept0", "oracle_accept0"):
            cell["ext_36m"][q] = RX.boot([(+1, a36, q)])
            cell["main_6m"][q] = RX.boot([(+1, a06, q)])
            if q in ("dream", "oracle", "gap", "closed", "infl", "excess0", "fa0"):
                cell["diff_36m_minus_6m"][q] = RX.boot([(+1, a36, q), (-1, a06, q)])
        for q in ("oracle", "closed", "gap_ref", "infl_ref"):
            cell["engine"][q] = RX.boot([(+1, aen, q)])
        cell["ext_36m_vs_engine"]["gap_excess"] = RX.boot([(+1, a36, "gap"), (-1, aen, "gap_ref")])
        cell["ext_36m_vs_engine"]["oracle_diff"] = RX.boot([(+1, a36, "oracle"), (-1, aen, "oracle")])
        cell["ext_36m_vs_engine"]["closed_diff"] = RX.boot([(+1, a36, "closed"), (-1, aen, "closed")])
        out[sc_name] = cell
    return out


# ---------------------------------------------------------------------------------------------------------------------
# 4. Out-of-sample cross-model correlation (24 ladder checkpoints + os_50m_full_36m = 25 checkpoints, 125 pairs)
# ---------------------------------------------------------------------------------------------------------------------
def across_oos_section(aud120: dict | None, fid: dict) -> dict | None:
    if aud120 is None:
        return None
    ladder_rows = list(csv.DictReader((ROOT / "results" / "analysis" / "pairs.csv").open()))
    if len(ladder_rows) != 120:
        raise SystemExit(f"expected 120 rows in pairs.csv, got {len(ladder_rows)}")

    # Gather 5 rows for os_50m_full_36m-samples_036000000
    ext_rows = []
    for fam in FAMILIES:
        s_list = [
            json.loads((ROOT / "results" / "rl" / f"{CKPT_36M}__{fam}__s{s}__tasks_v2_H24" / "eval3_001000000.summary.json").read_text())
            for s in (0, 1, 2)
        ]
        ext_rows.append({
            "checkpoint": CKPT_36M,
            "lineage_same": "os_50m_full",
            "lineage_sep": "os_50m_full_36m",
            "family": fam,
            "random_c120_hack_1": float(aud120["random"]["1"]["c120"]["by_family"][fam]["ext_36m"]["false_acceptance"]["value"]),
            "random_c120_hack_1000": float(aud120["random"]["1000"]["c120"]["by_family"][fam]["ext_36m"]["false_acceptance"]["value"]),
            "cem_seeded_c120_hack_1000": float(aud120["cem_seeded"]["1000"]["c120"]["by_family"][fam]["ext_36m"]["false_acceptance"]["value"]),
            "rl_inflation_1000000": float(np.mean([s["inflation_open"] for s in s_list])),
            "rl_gap_1000000": float(np.mean([s["verdict_gap_open"] for s in s_list])),
            "fid_test_f1_1m": float(fid["milestones_36m"]["test"]["36000000"]["f1_struct_1m"]),
            "fid_test_loglik_elbo": float(fid["milestones_36m"]["test"]["36000000"]["elbo"]),
        })

    def serialise_corr(cb: dict) -> dict:
        res = {}
        for k, v in cb.items():
            if isinstance(v, hs.Estimate):
                res[k] = _clean_est(v)
            elif isinstance(v, dict):
                res[k] = {
                    fk: ({sk: _clean_est(sv) if isinstance(sv, hs.Estimate) else sv for sk, sv in fv.items()} if isinstance(fv, dict) else fv)
                    for fk, fv in v.items()
                }
            else:
                res[k] = v
        return res

    all_rows = []
    for r in ladder_rows:
        all_rows.append({
            "checkpoint": r["checkpoint"],
            "lineage_same": r["lineage"],
            "lineage_sep": r["lineage"],
            "family": r["family"],
            "random_c120_hack_1": float(r["random_c120_hack_1"]),
            "random_c120_hack_1000": float(r["random_c120_hack_1000"]),
            "rl_inflation_1000000": float(r["rl_inflation_1000000"]),
            "rl_gap_1000000": float(r["rl_gap_1000000"]),
            "fid_test_f1_1m": float(r["fid_test_f1_1m"]) if r["fid_test_f1_1m"] != "" else None,
            "fid_test_loglik_elbo": float(r["fid_test_loglik_elbo"]) if r["fid_test_loglik_elbo"] != "" else None,
        })
    all_rows += ext_rows

    def run_pair(x_key: str, y_key: str, lin_key: str = "lineage_same") -> dict:
        sub = [r for r in all_rows if r.get(x_key) is not None and r.get(y_key) is not None]
        x = np.array([r[x_key] for r in sub], float)
        y = np.array([r[y_key] for r in sub], float)
        fam = np.array([r["family"] for r in sub])
        ck = np.array([r["checkpoint"] for r in sub])
        lin = np.array([r[lin_key] for r in sub])
        return serialise_corr(AL.corr_block(x, y, fam, ck, lin, N_BOOT, SEED))

    # Out-of-sample linear calibration fit on the 24 ladder checkpoints predicting os_50m_full_36m's 5 pairs
    oos_fit = {}
    for fam in FAMILIES:
        l_sub = [r for r in ladder_rows if r["family"] == fam]
        lx = np.array([float(r["random_c120_hack_1"]) for r in l_sub])
        ly_inf = np.array([float(r["rl_inflation_1000000"]) for r in l_sub])
        ly_gap = np.array([float(r["rl_gap_1000000"]) for r in l_sub])
        er = next(r for r in ext_rows if r["family"] == fam)
        # Rank of 36m among all 25 checkpoints on both X and Y
        x25 = np.append(lx, er["random_c120_hack_1"])
        y25_inf = np.append(ly_inf, er["rl_inflation_1000000"])
        y25_gap = np.append(ly_gap, er["rl_gap_1000000"])
        oos_fit[fam] = {
            "x_b1_false_acceptance": er["random_c120_hack_1"],
            "x_b1000_false_acceptance": er["random_c120_hack_1000"],
            "y_rl_inflation": er["rl_inflation_1000000"],
            "y_rl_gap": er["rl_gap_1000000"],
            "ladder_x_min_max": [float(lx.min()), float(lx.max())],
            "ladder_y_inf_min_max": [float(ly_inf.min()), float(ly_inf.max())],
            "rank_x_b1_of_25": int((x25 <= er["random_c120_hack_1"]).sum()),
            "rank_y_inf_of_25": int((y25_inf <= er["rl_inflation_1000000"]).sum()),
            "rank_y_gap_of_25": int((y25_gap <= er["rl_gap_1000000"]).sum()),
        }

    return {
        "n_checkpoints": 25,
        "n_pairs": 125,
        "ext_36m_pairs": ext_rows,
        "per_family_rank_placement": oos_fit,
        "b1_vs_inflation_same_lineage": run_pair("random_c120_hack_1", "rl_inflation_1000000", "lineage_same"),
        "b1_vs_inflation_separate_lineage": run_pair("random_c120_hack_1", "rl_inflation_1000000", "lineage_sep"),
        "b1_vs_gap_same_lineage": run_pair("random_c120_hack_1", "rl_gap_1000000", "lineage_same"),
        "b1000_vs_inflation_same_lineage": run_pair("random_c120_hack_1000", "rl_inflation_1000000", "lineage_same"),
        "b1000_vs_gap_same_lineage": run_pair("random_c120_hack_1000", "rl_gap_1000000", "lineage_same"),
        "elbo_vs_b1000_finals_13": run_pair("fid_test_loglik_elbo", "random_c120_hack_1000", "lineage_same"),
        "f1_1m_vs_b1000_finals_13": run_pair("fid_test_f1_1m", "random_c120_hack_1000", "lineage_same"),
    }


def write_markdown(res: dict, path: Path) -> None:
    fid = res["fidelity"]
    a1e4 = res["audit_1e4"]["all"]
    rl_all = res["rl"]["all"]
    rl_tr = res["rl"]["treasury"]
    rl_sp = res["rl"]["spatial4"]
    L = [
        "# Sixfold Extended One-Step Training Control (`os_50m_full_36m`, 36M examples / 12 epochs)",
        "",
        f"Status: **{res['status']}** (generated `{res['generated_utc']}` on CPU).",
        "",
        "## 1. Held-out test fidelity and likelihood across milestones",
        "",
        "| Checkpoint | Examples | Test ELBO | 1m struct F1 | 12m pop err | 12m funds err | 24m overlay ratio (ge 1) | 24m powered-zone MAE |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    b0 = fid["baseline_6m"]["test"]
    L.append(
        f"| `os_50m_full` (2 ep) | 6,000,000 | {b0['elbo']:.1f} | {b0['f1_struct_1m']:.3f} | "
        f"{b0['pop_medrel_12m']:.3f} | {b0['funds_medrel_12m']:.3f} | "
        f"{b0['mean_overlay_ratio_24m']:.3f} ({b0['n_overlays_ge_1']}/8) | {b0['open_loop_powered_zones_mae_24m']:.2f} |"
    )
    for m in MILESTONES:
        r = fid["milestones_36m"]["test"][str(m)]
        ep = m // 3_000_000
        L.append(
            f"| `os_50m_full_36m` ({ep} ep) | {m:,} | {r['elbo']:.1f} | {r['f1_struct_1m']:.3f} | "
            f"{r['pop_medrel_12m']:.3f} | {r['funds_medrel_12m']:.3f} | "
            f"{r['mean_overlay_ratio_24m']:.3f} ({r['n_overlays_ge_1']}/8) | {r['open_loop_powered_zones_mae_24m']:.2f} |"
        )
    L += [
        "",
        "## 2. Adaptive CEM at B = 10,000 (193 core instances)",
        "",
        f"- `os_50m_full` (6M): false acceptance `{a1e4['main_6m']['false_acceptance']['value']:.3f}`, "
        f"excess `{a1e4['main_6m']['excess']['value']:+.3f}`, false rejection `{a1e4['main_6m']['false_rejection']['value']:.3f}`, "
        f"oracle pass `{a1e4['main_6m']['oracle_accept']['value']:.3f}`, shortfall `{a1e4['main_6m']['shortfall']['value']:+.3f}`.",
        f"- `os_50m_full_36m` (36M): false acceptance `{a1e4['ext_36m']['false_acceptance']['value']:.3f}`, "
        f"excess `{a1e4['ext_36m']['excess']['value']:+.3f}`, false rejection `{a1e4['ext_36m']['false_rejection']['value']:.3f}`, "
        f"oracle pass `{a1e4['ext_36m']['oracle_accept']['value']:.3f}`, shortfall `{a1e4['ext_36m']['shortfall']['value']:+.3f}`.",
        f"- Exact simulator: false acceptance `{a1e4['perfect']['false_acceptance']['value']:.3f}`, "
        f"false rejection `{a1e4['perfect']['false_rejection']['value']:.3f}`, oracle pass `{a1e4['perfect']['oracle_accept']['value']:.3f}`.",
        "",
        "## 3. In-imagination PPO at 1,000,000 steps (15 runs)",
        "",
        f"- All 5 families: dream `{rl_all['ext_36m']['dream']['value']:.3f}` (6M `{rl_all['main_6m']['dream']['value']:.3f}`), "
        f"oracle `{rl_all['ext_36m']['oracle']['value']:.3f}` (6M `{rl_all['main_6m']['oracle']['value']:.3f}`), "
        f"closed `{rl_all['ext_36m']['closed']['value']:.3f}` (6M `{rl_all['main_6m']['closed']['value']:.3f}`), "
        f"initial-plan excess `{rl_all['ext_36m']['excess0']['value']:+.3f}` (6M `{rl_all['main_6m']['excess0']['value']:+.3f}`).",
        f"- Treasury (3 seeds): dream `{rl_tr['ext_36m']['dream']['value']:.3f}` -> oracle `{rl_tr['ext_36m']['oracle']['value']:.3f}` "
        f"(6M `{rl_tr['main_6m']['dream']['value']:.3f}` -> `{rl_tr['main_6m']['oracle']['value']:.3f}`, diff `{rl_tr['diff_36m_minus_6m']['oracle']['value']:+.3f}`).",
        f"- Four spatial/grid families (12 seeds): dream `{rl_sp['ext_36m']['dream']['value']:.3f}` -> closed `{rl_sp['ext_36m']['closed']['value']:.3f}` "
        f"(6M `{rl_sp['main_6m']['dream']['value']:.3f}` -> `{rl_sp['main_6m']['closed']['value']:.3f}`).",
    ]
    if res["audit_120_cities"] is not None:
        r1 = res["audit_120_cities"]["random"]["1"]["c120"]["all"]
        r3 = res["audit_120_cities"]["random"]["1000"]["c120"]["all"]
        c3 = res["audit_120_cities"]["cem_seeded"]["1000"]["c120"]["all"]
        L += [
            "",
            "## 4. All 120 held-out cities (574 instances)",
            "",
            f"- Single-plan (`B = 1`): false acceptance `{r1['ext_36m']['false_acceptance']['value']:.3f}` "
            f"(6M `{r1['main_6m']['false_acceptance']['value']:.3f}`, ref `{r1['perfect']['false_acceptance']['value']:.3f}`, "
            f"excess `{r1['ext_36m']['excess']['value']:+.3f}`).",
            f"- Random shooting (`B = 1,000`): false acceptance `{r3['ext_36m']['false_acceptance']['value']:.3f}`, "
            f"excess `{r3['ext_36m']['excess']['value']:+.3f}`, false rejection `{r3['ext_36m']['false_rejection']['value']:.3f}`, "
            f"oracle pass `{r3['ext_36m']['oracle_accept']['value']:.3f}` (6M `{r3['main_6m']['oracle_accept']['value']:.3f}`, ref `{r3['perfect']['oracle_accept']['value']:.3f}`).",
            f"- Adaptive CEM (`B = 1,000`): false acceptance `{c3['ext_36m']['false_acceptance']['value']:.3f}`, "
            f"excess `{c3['ext_36m']['excess']['value']:+.3f}`, false rejection `{c3['ext_36m']['false_rejection']['value']:.3f}`, "
            f"oracle pass `{c3['ext_36m']['oracle_accept']['value']:.3f}` (6M `{c3['main_6m']['oracle_accept']['value']:.3f}`, ref `{c3['perfect']['oracle_accept']['value']:.3f}`).",
        ]
    if res["across_25_checkpoints"] is not None:
        ac = res["across_25_checkpoints"]["b1_vs_inflation_same_lineage"]
        L += [
            "",
            "## 5. Out-of-sample cross-model calibration (25 checkpoints, 125 pairs)",
            "",
            f"- Single-plan (`B = 1`) vs PPO margin inflation: within-family Spearman `{ac['within_mean_spearman']['value']:.3f}` "
            f"[{ac['within_mean_spearman']['lo']:.3f}, {ac['within_mean_spearman']['hi']:.3f}], "
            f"pooled `{ac['pooled_spearman']['value']:.3f}` [{ac['pooled_spearman']['lo']:.3f}, {ac['pooled_spearman']['hi']:.3f}].",
        ]
    path.write_text("\n".join(L) + "\n")


def milestones_b1_section() -> dict | None:
    mb_root = ROOT / "results" / "audit_36m" / "milestones_b1"
    c_rand06 = ROOT / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000" / "tasks_v2_H24"
    x_rand06 = ROOT / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000" / "tasks_v2x_H24"
    c_rand_p = ROOT / "results" / "audit" / "engine_reference" / "tasks_v2_H24" / "B_economy"
    x_rand_p = ROOT / "results" / "audit" / "engine_reference" / "tasks_v2x_H24" / "B_economy"
    perf = load_records([c_rand_p, x_rand_p], "random", 1)
    emu06 = load_records([c_rand06, x_rand06], "random", 1)
    out = {}
    for m in MILESTONES:
        if m < 36_000_000:
            d = [mb_root / f"samples_{m:09d}" / "tasks_v2_H24", mb_root / f"samples_{m:09d}" / "tasks_v2x_H24"]
        else:
            d = [ROOT / "results" / "audit_36m" / "core" / "tasks_v2_H24",
                 ROOT / "results" / "audit_36m" / "x80" / "tasks_v2x_H24"]
        if not all((p / "records.jsonl.gz").is_file() for p in d):
            return None
        out[str(m)] = paired_audit_cell(load_records(d, "random", 1), perf, emu06)
    return out


def showcase_section() -> dict | None:
    p = ROOT / "results" / "analysis" / "showcase_36m.json"
    if not p.is_file():
        return None
    d = json.loads(p.read_text())
    return {
        "milestones": {
            str(m): {
                "fig1_n_pass_of_8": int(d[str(m)]["fig1_n_pass_of_8"]),
                "fig1_accepted": bool(d[str(m)]["fig1_accepted"]),
                "gallery_n_accepted_of_15": int(d[str(m)]["gallery_n_accepted_of_15"]),
                "gallery_accepted_by_family": dict(d[str(m)]["gallery_accepted_by_family"]),
            }
            for m in MILESTONES
        },
        "fig1_cpu_36m": d["fig1_cpu_36m"],
    }


def main(argv: list[str] | None = None) -> dict:
    ap = argparse.ArgumentParser(description="Analyse the 36M-example (12-epoch) extended-training control.")
    ap.add_argument("--out", default=str(ROOT / "results" / "analysis"), help="Output directory")
    a = ap.parse_args(argv)

    fid = fidelity_section()
    a1e4 = audit_1e4_section()
    aud120, pa36 = audit_120_and_pressure_section()
    mb1 = milestones_b1_section()
    sh36 = showcase_section()
    rl = rl_section()
    oos = across_oos_section(aud120, fid)

    complete = aud120 is not None and pa36 is not None and oos is not None and mb1 is not None and sh36 is not None
    res = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "complete" if complete else "partial",
        "checkpoint": CKPT_36M,
        "baseline_checkpoint": CKPT_6M,
        "samples": 36_000_000,
        "epochs_over_3m_store": 12,
        "bootstrap": f"BCa cluster bootstrap over held-out city families, {N_BOOT} resamples, seed {SEED}",
        "fidelity": fid,
        "milestones_b1_120": mb1,
        "showcase_36m": sh36,
        "audit_1e4": a1e4,
        "audit_120_cities": aud120,
        "pressure_axis_36m": pa36,
        "rl": rl,
        "across_25_checkpoints": oos,
    }
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "extended_training.json").write_text(json.dumps(res, indent=1))
    write_markdown(res, out_dir / "extended_training.md")
    print(f"wrote {out_dir / 'extended_training.json'} (status={res['status']})")
    return res


if __name__ == "__main__":
    main()
