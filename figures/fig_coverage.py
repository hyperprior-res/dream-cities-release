"""Figure 8 (fig_coverage.pdf): Retraining with fiscal-regime rollout coverage vs. seed variance.

Follows Google DeepMind (SIMA Figs 9-10) and Nature (AlphaTensor Fig. 5) bar-chart conventions:
solid horizontal bars anchored on crisp 0.55 pt black zero baselines with capless black 95%
bootstrap CI and 3-seed min-max whiskers, zero circle-dot scatter overlays, and frameless legends.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

SRC = F.REPO / "results/analysis/coverage.json"
CS = F.REPO / "results/analysis/coverage_seeds.json"
RL = F.REPO / "results/rl"
FAMS = ["grow", "solvent", "treasury", "recover", "power"]
MAIN, COV = "os_50m_full-samples_006000000", "os_50m_cov-samples_006000000"


def rl_gaps(ck, fam):
    out = []
    for s in (0, 1, 2):
        p = RL / f"{ck}__{fam}__s{s}__tasks_v2_H24" / "eval3_001000000.summary.json"
        d = json.loads(p.read_text())
        out.append(float(d["rate_dream_accept"]) - float(d["rate_engine_open_accept"]))
    return out


def main():
    d = json.loads(SRC.read_text())
    cs = json.loads(CS.read_text())
    if d["status"] != "complete":
        raise SystemExit(f"{SRC}: status {d['status']}")
    F.apply()

    fig, (axa, axb) = plt.subplots(
        1, 2, figsize=(F.TEXT_IN, 2.90), sharey=True,
        gridspec_kw=dict(left=0.115, right=0.985, top=0.780, bottom=0.160, wspace=0.105),
    )
    rows = ["all"] + FAMS
    ys = np.arange(len(rows))[::-1].astype(float) * 1.14
    ys[0] += 0.30
    sep_y = 0.5 * (ys[0] + ys[1])

    # Panel (a): Adaptive CEM false acceptance at B = 1,000 (uniform 3 solid bars per row)
    F.decorate_bar_axis(axa, zero_spine=True, wrect=3.2)
    axa.axhline(sep_y, color="#CCCCCC", lw=0.55, zorder=1)

    g = d["methods"]["cem_seeded"]["budgets"]["1000"]
    _ = cs["methods"]["cem_seeded"]["quantities"]["false_acceptance"]["seeds"]
    ih = 0.21
    tracks_a = [
        ("main", "emulator", +0.23, F.RED_MID),
        ("coverage", "emulator", 0.00, F.PETROL),
        ("main", "perfect_emulator", -0.23, F.BLUE),
    ]
    for who, arm, dy, col in tracks_a:
        for y, sc in zip(ys, rows):
            v, lo, hi = F.interval(g[sc][who][arm]["hackability"])
            F.draw_hbar_ci(axa, y + dy, v, lo, hi, color=col, height=ih, zorder=3)

    axa.set_yticks(ys)
    axa.set_yticklabels(["All tasks"] + [F.FAM_LABEL[f] for f in FAMS], fontsize=6.5, fontweight="normal", color=F.INK)
    axa.tick_params(axis="y", length=0, pad=4.0)
    axa.set_xlim(0.0, 0.60)
    axa.set_xticks([0.0, 0.2, 0.4, 0.6])
    axa.tick_params(axis="x", labelsize=6.4)
    axa.set_ylim(ys[-1] - 0.54, ys[0] + 0.54)
    axa.set_xlabel("False acceptance (Adaptive CEM, $B = 10^3$)", fontsize=6.7)
    F.panel_header(axa, "a", "Open-loop search exploitation", pad_pt=6.5, letter_dx_pt=-9.5, gap_pt=9.5)

    leg_a = [
        F.bar_legend_handle(F.RED_MID, label="Baseline 50M (95% CI)"),
        F.bar_legend_handle(F.PETROL, label="Fiscal-coverage 50M (95% CI)"),
        F.bar_legend_handle(F.BLUE, label="Exact simulator (95% CI)"),
    ]
    F.clean_legend(
        fig, leg_a, loc="upper left", ncol=2, fontsize=6.10,
        bbox_to_anchor=(0.095, 0.992), columnspacing=0.85, labelspacing=0.25,
    )

    # Panel (b): PPO optimism gap at 1M imagined months (uniform 3 solid bars per row)
    F.decorate_bar_axis(axb, zero_spine=False, wrect=3.2)
    axb.axhline(sep_y, color="#CCCCCC", lw=0.55, zorder=1)

    means = {}
    for ck, who, col, dy in (
        (MAIN, "main", F.RED_MID, +0.23),
        (COV, "coverage", F.PETROL, 0.00),
    ):
        per_seed_all = np.zeros(3, dtype=float)
        for y, fam in zip(ys[1:], FAMS):
            gs = rl_gaps(ck, fam)
            per_seed_all += np.asarray(gs) / len(FAMS)
            m = float(np.mean(gs))
            ref = d["rl"][who][fam]["values"]["rl_gap_1000000"]
            if abs(m - ref) > 1e-9:
                raise SystemExit(f"{who} {fam}: mismatch {m} vs {ref}")
            means[(who, fam)] = m
            F.draw_hbar_ci(
                axb, y + dy, m, float(min(gs)), float(max(gs)),
                color=col, height=ih, zorder=3,
            )

        mm = float(np.mean([means[(who, f)] for f in FAMS]))
        means[(who, "all")] = mm
        F.draw_hbar_ci(
            axb, ys[0] + dy, mm, float(per_seed_all.min()), float(per_seed_all.max()),
            color=col, height=ih, zorder=3,
        )

    R_eng = json.loads((F.REPO / "results/analysis/rl_axis.json").read_text())["results"]["engine"]["1000000"]
    for y, fam in zip(ys, ["all"] + FAMS):
        xe = R_eng[fam]["gap_ref"]
        ve, loe, hie = float(xe["value"]), float(xe["twoway"]["lo"]), float(xe["twoway"]["hi"])
        F.draw_hbar_ci(
            axb, y - 0.23, ve, loe, hie,
            color=F.BLUE, height=ih, zorder=3,
        )

    axb.set_xlim(-0.09, 0.50)
    axb.set_xticks([0.0, 0.2, 0.4])
    axb.tick_params(axis="x", labelsize=6.4)
    axb.set_xlabel("PPO optimism gap at $10^6$ months (dream minus oracle)", fontsize=6.7)
    F.panel_header(axb, "b", "In-imagination PPO exploitation (3 seeds/task)", pad_pt=6.5, letter_dx_pt=-9.5, gap_pt=9.5)

    leg_b = [
        F.bar_legend_handle(F.RED_MID, label="Baseline 50M (3-seed range)"),
        F.bar_legend_handle(F.PETROL, label="Fiscal-coverage 50M (3-seed range)"),
        F.bar_legend_handle(F.BLUE, label="Engine PPO (95% CI)"),
    ]
    F.clean_legend(
        fig, leg_b, loc="upper right", ncol=2, fontsize=6.10,
        bbox_to_anchor=(0.992, 0.992), columnspacing=0.80, labelspacing=0.25,
    )

    F.save(
        fig, "fig_coverage.pdf",
        {
            "inputs": [
                str(SRC.relative_to(F.REPO)),
                str(CS.relative_to(F.REPO)),
                "results/rl/{os_50m_full,os_50m_cov}-samples_006000000__*__tasks_v2_H24/eval3_001000000.summary.json",
            ],
            "rl_gap_means": {f"{w}|{f}": v for (w, f), v in means.items()},
        },
    )


if __name__ == "__main__":
    main()
