"""Figure 9 (fig_defences.pdf): Inference-time defence trade-off across false acceptance, false rejection, and ground-truth discovery.

Follows Google DeepMind (SIMA Figs 9-11) and Nature (AlphaTensor Fig. 5) bar-chart conventions:
three aligned solid horizontal bar panels anchored on crisp 0.55 pt black zero spines with capless
black 95% bootstrap confidence-interval whiskers under both Adaptive CEM and Random shooting.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

SRC = F.REPO / "results/defences/frontier.json"

ROWS = [
    ("perfect", "Exact simulator", "sim"),
    ("member0", "Single world model", "undef"),
    ("ensemble", "Undefended ensemble (3)", "undef"),
    ("temp0.75", "Temperature 0.75", "def"),
    ("halt80", "Uncertainty halt 80%", "def"),
    ("detector0.5", "Latent OOD gate 0.5", "def"),
    ("penalty1", "Variance penalty 1", "def"),
    ("penalty0", "Mean-margin filter", "def"),
    ("deflation-ensemble", "Emp.-Bayes shrink (3)", "def"),
    ("deflation-member0", "Emp.-Bayes shrink (1)", "def"),
    ("temp1.25", "Temperature 1.25", "def"),
    ("detector0.2", "Latent OOD gate 0.2", "def"),
    ("penalty2", "Variance penalty 2", "def"),
    ("temp1.5", "Temperature 1.5", "def"),
]


def d_rows(d, search):
    return {r["setting"]: r for r in d["frontier"][search]["rows"] if r.get("complete")}


def val(d):
    lo = d.get("bca_lo", d["lo"])
    hi = d.get("bca_hi", d["hi"])
    return float(d["value"]), float(lo), float(hi)


def role_colors(role: str):
    if role == "sim":
        return F.BLUE, F.BLUE_LIGHT
    if role == "undef":
        return F.RED_MID, F.RED_LIGHT
    return F.PETROL, F.PETROL_LIGHT


def main():
    d = json.loads(SRC.read_text())
    F.apply()

    rr = d_rows(d, "random")
    rc = d_rows(d, "cem_seeded")

    fig, axes = plt.subplots(
        1, 3, figsize=(F.TEXT_IN, 3.74), sharey=True,
        gridspec_kw=dict(left=0.205, right=0.988, top=0.820, bottom=0.115, wspace=0.105),
    )

    n_rows = len(ROWS)
    ys = np.arange(n_rows)[::-1].astype(float) * 0.94
    ys[:3] += 0.30
    sep_y = 0.5 * (ys[2] + ys[3])

    ih = 0.24
    dy = 0.14
    drawn = []

    panels = [
        (axes[0], "hackability", "False acceptance", "a", (0.0, 0.44), [0.0, 0.1, 0.2, 0.3, 0.4], "Exploited plans accepted"),
        (axes[1], "false_rejection", "False rejection", "b", (0.0, 1.04), [0.0, 0.25, 0.5, 0.75, 1.0], "Truly passing plans rejected"),
        (axes[2], "oracle_accept", "Ground-truth pass rate", "c", (0.0, 0.76), [0.0, 0.2, 0.4, 0.6], "Oracle pass rate (32 seeds)"),
    ]

    for ax, key, title, letter, xlim, xticks, xlabel in panels:
        F.decorate_bar_axis(ax, zero_spine=True, wrect=3.2)
        ax.axhline(sep_y, color="#CCCCCC", lw=0.55, zorder=1)

        ref_setting = "perfect" if key == "oracle_accept" else "ensemble"
        ref_v = val(rc[ref_setting][key])[0]
        ref_lbl = "Exact sim." if key == "oracle_accept" else "Undefended ens."
        ax.plot([ref_v, ref_v], [ys.min() - 0.50, ys.max() + 0.42], color="#555555", lw=0.55, ls=(0, (3.0, 2.0)), zorder=2)
        ha_ref = "left" if key == "false_rejection" else "center"
        x_ref_txt = max(ref_v - 0.015, 0.01) if key == "false_rejection" else ref_v
        ax.text(
            x_ref_txt, ys.max() + 0.48, f"{ref_lbl} ({ref_v:.2f})",
            fontsize=5.6, color="#444444", ha=ha_ref, va="bottom",
        )

        for idx, (setting, _label, role) in enumerate(ROWS):
            y = ys[idx]
            c_cem, c_rnd = role_colors(role)
            if setting in rc:
                vc, loc, hic = val(rc[setting][key])
                F.draw_hbar_ci(
                    ax, y + dy, vc, loc, hic,
                    color=c_cem, height=ih, zorder=4,
                )
                if letter == "a":
                    drawn.append(("cem_seeded", setting))
            if setting in rr:
                vr, lor, hir = val(rr[setting][key])
                F.draw_hbar_ci(
                    ax, y - dy, vr, lor, hir,
                    color=c_rnd, height=ih, zorder=3,
                )
                if letter == "a":
                    drawn.append(("random", setting))

        ax.set_xlim(*xlim)
        ax.set_xticks(xticks)
        ax.tick_params(axis="x", labelsize=6.4)
        ax.set_xlabel(xlabel, fontsize=6.7)
        F.panel_header(ax, letter, title, pad_pt=7.5, letter_dx_pt=-9.5, gap_pt=9.5)

    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([lab for _, lab, _ in ROWS], fontsize=6.4, fontweight="normal", color=F.INK)
    axes[0].set_ylim(ys.min() - 0.50, ys.max() + 0.90)
    axes[0].tick_params(axis="y", length=0, pad=4.0)

    leg_handles = [
        F.bar_legend_handle(F.RED_MID, label="Undefended model (Adaptive CEM)"),
        F.bar_legend_handle(F.PETROL, label="Defended model (Adaptive CEM)"),
        F.bar_legend_handle(F.BLUE, label="Exact simulator (Adaptive CEM)"),
        F.bar_legend_handle(F.RED_LIGHT, label="Undefended model (Random shooting)"),
        F.bar_legend_handle(F.PETROL_LIGHT, label="Defended model (Random shooting)"),
        F.bar_legend_handle(F.BLUE_LIGHT, label="Exact simulator (Random shooting)"),
    ]
    F.clean_legend(
        fig, leg_handles, loc="upper left", ncol=3, fontsize=6.15,
        bbox_to_anchor=(0.060, 0.992), columnspacing=0.95, labelspacing=0.26, handlelength=1.35,
    )

    F.save(
        fig, "fig_defences.pdf",
        {"inputs": [str(SRC.relative_to(F.REPO))], "drawn": drawn, "seeded_half_drawn": any(s == "cem_seeded" for s, _ in drawn)},
    )


if __name__ == "__main__":
    main()
