"""Verification tests for the sixfold extended one-step training control (``os_50m_full_36m``: 36,000,000 examples,
12 epochs over the 3,000,000-transition full training store). Runs strictly on CPU in milliseconds."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _check_ci(est: dict, bca: bool = True) -> None:
    v = float(est["value"])
    lo = est.get("bca_lo") if bca and est.get("bca_lo") is not None else est.get("lo")
    hi = est.get("bca_hi") if bca and est.get("bca_hi") is not None else est.get("hi")
    assert lo is not None and hi is not None, est
    assert math.isfinite(v) and math.isfinite(lo) and math.isfinite(hi), est
    assert lo - 1e-6 <= v <= hi + 1e-6, (lo, v, hi)


def test_ckpt_meta_and_replays_complete():
    meta_dir = ROOT / "paper" / "data" / "ckpt_meta" / "os_50m_full_36m"
    assert (meta_dir / "config.json").is_file()
    cfg = json.loads((meta_dir / "config.json").read_text())
    assert int(cfg["train"]["samples"]) == 36_000_000
    for m in (6_000_000, 12_000_000, 18_000_000, 24_000_000, 30_000_000, 36_000_000):
        sha = (meta_dir / f"samples_{m:09d}.pt.sha256").read_text().split()[0]
        assert len(sha) == 64 and all(c in "0123456789abcdef" for c in sha)

    rep = json.loads((ROOT / "results" / "analysis" / "extended_training.replays.json").read_text())
    assert len(rep["runs"]) == 15
    for run_name, insts in rep["runs"].items():
        assert run_name.startswith("os_50m_full_36m-samples_036000000__")
        assert len(insts["instances"]) in (35, 38, 40)


def test_extended_training_analysis_invariants():
    d = json.loads((ROOT / "results" / "analysis" / "extended_training.json").read_text())
    assert d["status"] == "complete"
    assert d["samples"] == 36_000_000 and d["epochs_over_3m_store"] == 12

    # 1. Fidelity milestones (monotonic test ELBO gain alongside rising 24-month spatial drift)
    fid = d["fidelity"]
    miles = fid["milestones_36m"]["test"]
    elbos = [miles[str(m)]["elbo"] for m in (6_000_000, 12_000_000, 18_000_000, 24_000_000, 30_000_000, 36_000_000)]
    assert all(elbos[i] < elbos[i + 1] for i in range(len(elbos) - 1)), elbos
    ratios = [miles[str(m)]["mean_overlay_ratio_24m"] for m in (6_000_000, 12_000_000, 18_000_000, 24_000_000, 30_000_000, 36_000_000)]
    assert all(ratios[i] < ratios[i + 1] for i in range(len(ratios) - 1)), ratios
    assert fid["deltas_test_36m_minus_baseline_6m"]["elbo_nats"] > 200.0
    assert fid["deltas_test_36m_minus_baseline_6m"]["funds_medrel_12m"] < 0.0
    assert fid["deltas_test_36m_minus_baseline_6m"]["open_loop_powered_zones_mae_24m"] > 4.0
    # Training-city 24m drift also worsens (ruling out held-out overfitting)
    tr_miles = fid["milestones_36m"]["train_eval"]
    assert tr_miles["36000000"]["open_loop_powered_zones_mae_24m"] > fid["baseline_6m"]["train_eval"]["open_loop_powered_zones_mae_24m"]

    # 2. B = 10,000 adaptive CEM matches pressure_axis.json on baseline 6M and satisfies CI invariants
    pa = json.loads((ROOT / "results" / "analysis" / "pressure_axis.json").read_text())
    pa_1e4 = next(r for r in pa["rows"] if int(r["budget"]) == 10000)
    a1e4 = d["audit_1e4"]["all"]
    assert a1e4["n"] == 193 and a1e4["n_clusters"] == 40
    assert abs(a1e4["main_6m"]["false_acceptance"]["value"] - pa_1e4["false_acceptance"]["emulator"]["value"]) < 1e-12
    assert abs(a1e4["main_6m"]["oracle_accept"]["value"] - pa_1e4["real_success"]["emulator"]["value"]) < 1e-12
    assert abs(a1e4["perfect"]["oracle_accept"]["value"] - pa_1e4["real_success"]["perfect"]["value"]) < 1e-12
    for arm in ("ext_36m", "main_6m", "perfect"):
        for k in ("false_acceptance", "judge_accept", "oracle_accept", "false_rejection"):
            _check_ci(a1e4[arm][k])
    for k in ("excess", "shortfall"):
        _check_ci(a1e4["ext_36m"][k])
        _check_ci(a1e4["main_6m"][k])

    # 3. Full 120-city (574-instance) search audits
    aud120 = d["audit_120_cities"]
    for m, B in (("random", "1"), ("random", "1000"), ("cem_seeded", "1000")):
        blk = aud120[m][B]["c120"]["all"]
        assert blk["n"] == 574 and blk["n_clusters"] == 120
        _check_ci(blk["ext_36m"]["excess"])
        _check_ci(blk["ext_36m"]["oracle_accept"])

    # 4. PPO mechanistic split (treasury gains ground-truth success; spatial families lose closed-loop success)
    rl = d["rl"]
    tr_diff = rl["treasury"]["diff_36m_minus_6m"]["oracle"]
    assert tr_diff["value"] > 0.05 and tr_diff["city_only"]["bca_lo"] > 0.0
    sp_diff = rl["spatial4"]["diff_36m_minus_6m"]["closed"]
    assert sp_diff["value"] < -0.04 and sp_diff["city_only"]["bca_hi"] < 0.0

    # 5. Out-of-sample cross-model correlation across 25 checkpoints (125 pairs)
    ac = d["across_25_checkpoints"]
    assert ac["n_checkpoints"] == 25 and ac["n_pairs"] == 125
    b1 = ac["b1_vs_inflation_same_lineage"]
    _check_ci(b1["within_mean_spearman"], bca=False)
    _check_ci(b1["pooled_spearman"], bca=False)
    assert b1["within_mean_spearman"]["value"] > 0.65 and b1["pooled_spearman"]["value"] > 0.85

    # 6. Milestone B=1 single-plan verdict trajectory across 120 cities (6M..36M) and showcase replays
    mb1 = d["milestones_b1_120"]
    assert set(mb1.keys()) == {str(m) for m in (6_000_000, 12_000_000, 18_000_000, 24_000_000, 30_000_000, 36_000_000)}
    # Excess stays statistically positive through 24M (8 epochs), then includes zero at 30M..36M as self-acceptance collapses
    for m in (6_000_000, 12_000_000, 18_000_000, 24_000_000):
        ex = mb1[str(m)]["all"]["ext_36m"]["excess"]
        _check_ci(ex)
        assert ex["bca_lo"] > 0.0, (m, ex)
    for m in (30_000_000, 36_000_000):
        ex = mb1[str(m)]["all"]["ext_36m"]["excess"]
        _check_ci(ex)
        assert ex["bca_lo"] <= 0.0 <= ex["bca_hi"], (m, ex)
    assert mb1["36000000"]["all"]["ext_36m"]["false_rejection"]["value"] > 0.80

    # Three-seed baseline 24m drift band vs 12-epoch drift
    b3 = fid["baseline_3seed_test"]
    assert len(b3) == 3
    pow_3s = [v["open_loop_powered_zones_mae_24m"] for v in b3.values()]
    assert max(pow_3s) < miles["36000000"]["open_loop_powered_zones_mae_24m"]

    # Showcase Figure 1 & Figure 2 replays
    sh = d["showcase_36m"]
    assert sh["fig1_cpu_36m"]["n_pass_of_8"] == 7 and sh["fig1_cpu_36m"]["accepted"] is True
    assert sh["milestones"]["6000000"]["gallery_n_accepted_of_15"] > sh["milestones"]["36000000"]["gallery_n_accepted_of_15"]
    assert sh["milestones"]["36000000"]["gallery_accepted_by_family"]["recover"] == 0
