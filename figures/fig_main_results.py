"""Figure 4 (fig_family.pdf): Task-family heterogeneity across search and reinforcement learning.

Follows Google DeepMind (SIMA Figs 9-10) and Nature (AlphaTensor Fig. 5) bar-chart conventions:
solid horizontal bars anchored on a crisp 0.55 pt black zero baseline with capless black 95%
bootstrap confidence-interval whiskers and frameless panel-aligned legends.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

BASE = F.REPO / "results/audit/ladder/os_50m_full/samples_006000000"
RUNS = {
    "random": BASE / "tasks_v2_H24/reference.json",
    "cem_seeded": BASE / "tasks_v2_H24_cem_seeded/reference.json",
}
FAM = ["grow", "solvent", "treasury", "recover", "power"]


def group(ref, fam, method, b=1000):
    return [x for x in ref["subsets"][f"task:{fam}"]["groups"] if x["method"] == method and x["budget"] == b][0]


def fig_family():
    refs = {m: json.loads(p.read_text()) for m, p in RUNS.items()}
    F.apply()
    fig, axes = plt.subplots(
        1, 3, figsize=(F.TEXT_IN, 2.86), sharey=True,
        gridspec_kw=dict(left=0.090, right=0.988, top=0.775, bottom=0.165, wspace=0.115),
    )
    row_step = 1.24
    ys = np.arange(len(FAM))[::-1].astype(float) * row_step

    # Four solid borderless bar tracks per family: Adaptive CEM pair (top), Random shooting pair (bottom)
    tracks = [
        ("cem_seeded", "emulator", +0.285, F.RED_MID),
        ("cem_seeded", "perfect_emulator", +0.095, F.BLUE),
        ("random", "emulator", -0.095, F.RED_LIGHT),
        ("random", "perfect_emulator", -0.285, F.BLUE_LIGHT),
    ]
    ih = 0.175

    for ax, key, title, letter, xlim, xticks in (
        (axes[0], "hackability", "False acceptance ($B = 10^3$)", "a", (0.0, 0.62), [0.0, 0.2, 0.4, 0.6]),
        (axes[1], "oracle_accept", "Ground-truth pass rate ($B = 10^3$)", "b", (0.0, 1.05), [0.0, 0.25, 0.5, 0.75, 1.0]),
    ):
        F.decorate_bar_axis(ax, zero_spine=True, wrect=3.2)
        for i, fam in enumerate(FAM):
            for m, who, dy, col in tracks:
                g = group(refs[m], fam, m)
                v, lo, hi = F.interval(g[who][key])
                F.draw_hbar_ci(
                    ax, ys[i] + dy, v, lo, hi,
                    color=col, height=ih, zorder=3,
                )
        ax.set_xlim(*xlim)
        ax.set_xticks(xticks)
        ax.tick_params(axis="x", labelsize=6.4)
        ax.set_xlabel("Share of task instances", fontsize=6.7)
        F.panel_header(ax, letter, title, pad_pt=6.5, letter_dx_pt=-9.5, gap_pt=9.5)

    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([F.FAM_LABEL[f] for f in FAM], fontsize=6.5, fontweight="normal", color=F.INK)
    axes[0].set_ylim(ys.min() - 0.56, ys.max() + 0.56)
    axes[0].tick_params(axis="y", length=0, pad=4.0)

    search_leg = [
        F.bar_legend_handle(F.RED_MID, label="Adaptive CEM (world model)"),
        F.bar_legend_handle(F.BLUE, label="Adaptive CEM (exact simulator)"),
        F.bar_legend_handle(F.RED_LIGHT, label="Random shooting (world model)"),
        F.bar_legend_handle(F.BLUE_LIGHT, label="Random shooting (exact simulator)"),
    ]
    F.clean_legend(
        fig, search_leg, loc="upper left", ncol=2, fontsize=6.3,
        bbox_to_anchor=(0.088, 0.992), columnspacing=1.20, labelspacing=0.25,
    )

    # Panel (c): PPO optimism gap across 24 world models vs Engine PPO (two-way 95% CIs)
    R = json.loads((F.REPO / "results/analysis/rl_axis.json").read_text())["results"]
    ax = axes[2]
    F.decorate_bar_axis(ax, zero_spine=False, wrect=3.2)

    for i, fam in enumerate(FAM):
        xw = R["ladder"]["1000000"][fam]["gap"]
        vw, low, hiw = float(xw["value"]), float(xw["twoway"]["lo"]), float(xw["twoway"]["hi"])
        F.draw_hbar_ci(
            ax, ys[i] + 0.125, vw, low, hiw,
            color=F.RED_MID, height=0.22, zorder=3,
        )

        xe = R["engine"]["1000000"][fam]["gap_ref"]
        ve, loe, hie = float(xe["value"]), float(xe["twoway"]["lo"]), float(xe["twoway"]["hi"])
        F.draw_hbar_ci(
            ax, ys[i] - 0.125, ve, loe, hie,
            color=F.BLUE, height=0.22, zorder=3,
        )

    ax.set_xlim(-0.08, 0.66)
    ax.set_xticks([0.0, 0.2, 0.4, 0.6])
    ax.tick_params(axis="x", labelsize=6.4)
    ax.set_xlabel("Dream pass minus oracle pass", fontsize=6.7)
    F.panel_header(ax, "c", "PPO optimism gap ($10^6$ months)", pad_pt=6.5, letter_dx_pt=-9.5, gap_pt=9.5)

    rl_leg = [
        F.bar_legend_handle(F.RED_MID, label="Dream PPO (24 models)"),
        F.bar_legend_handle(F.BLUE, label="Engine PPO"),
    ]
    F.clean_legend(
        fig, rl_leg, loc="upper right", ncol=1, fontsize=6.4,
        bbox_to_anchor=(0.988, 0.992), labelspacing=0.26,
    )

    F.save(
        fig, "fig_family.pdf",
        {"inputs": [str(p.relative_to(F.REPO)) for p in RUNS.values()] + ["results/analysis/rl_axis.json"]},
    )


if __name__ == "__main__":
    fig_family()
