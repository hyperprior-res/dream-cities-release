"""Figure 6 (fig_mechanism.pdf): Counterfactual subsystem patching across all 285 exploited plan records.

Follows Google DeepMind (SIMA Figs 9-10) and Nature (AlphaTensor Fig. 5) bar-chart conventions:
solid horizontal bars anchored at zero with capless black bootstrap confidence-interval whiskers,
cleanly separating raw boundary sensitivity (a) from perturbation-controlled causal excess (b).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

SRC = F.REPO / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24/patching_summary.md"
PC = F.REPO / "results/analysis/patching_controls.json"
CELL = re.compile(r"(\d+)/(\d+) (\d\.\d+) \[(\d\.\d+), (\d\.\d+)\]")
ORDER = [
    ("power", "Power grid"),
    ("treasury", "Treasury"),
    ("valves", "Demand valves"),
    ("zone_growth", "Zone growth"),
    ("pollution", "Pollution"),
    ("traffic", "Traffic"),
    ("land_value", "Land value"),
    ("crime", "Crime"),
    ("fire", "Fire spread"),
]
SYM_KEY = {"fire": "fire_sym", "zone_growth": "zone_growth_sym"}


def table():
    t = SRC.read_text()
    i = t.find("## Primary set: emulator accepts, oracle (majority) rejects")
    rows, started = {}, False
    for line in t[i:].splitlines()[1:]:
        if line.startswith("|"):
            started = True
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            m = CELL.fullmatch(c[2]) if len(c) > 2 else None
            if m:
                k, n = int(m.group(1)), int(m.group(2))
                rows[c[0]] = (k / n, float(m.group(4)), float(m.group(5)), n)
        elif started:
            break
    return rows


def symmetric(R, P):
    fr = P["part3"]["flip_rates"]["all"]
    for m in ("fire", "zone_growth"):
        for pre in ("", "random~", "changed~"):
            e = fr[pre + m + "_sym"]
            R[pre + m] = (e["k"] / e["n"], e["lo"], e["hi"], e["n"])
    return R


def main():
    P = json.loads(PC.read_text())
    R = symmetric(table(), P)
    F.apply()

    fig, (axa, axb) = plt.subplots(
        1, 2, figsize=(F.TEXT_IN, 3.16), sharey=True,
        gridspec_kw=dict(left=0.158, right=0.985, top=0.760, bottom=0.150, wspace=0.095, width_ratios=[1.05, 1.0]),
    )
    ys = np.arange(len(ORDER))[::-1].astype(float) * 1.08
    ys[3:] -= 0.34
    sep_y = 0.5 * (ys[2] + ys[3])

    # Panel (a): Raw flip share under subsystem patch vs matched controls
    F.decorate_bar_axis(axa, zero_spine=True, wrect=3.2)
    none = R["none"]
    axa.axvspan(none[1], none[2], ymax=0.935, color="#E6E8EB", lw=0, zorder=1)
    axa.plot([none[0], none[0]], [ys.min() - 0.54, ys.max() + 0.42], color="#444444", lw=0.60, ls=(0, (3.0, 1.8)), zorder=5)
    axa.text(
        none[0], ys.max() + 0.47, f"Unpatched redraw ({none[0]:.2f})",
        fontsize=5.75, color="#444444", fontweight="normal", ha="center", va="bottom",
    )
    axa.axhline(sep_y, color="#CCCCCC", lw=0.55, ls="-", zorder=1)

    ih = 0.215
    dy = 0.225
    for (m, _), y in zip(ORDER, ys):
        v, lo, hi, _ = R[m]
        cv_chg, clo_c, chi_c, _ = R["changed~" + m]
        cv_sz, clo_s, chi_s, _ = R["random~" + m]

        F.draw_hbar_ci(axa, y + dy, v, lo, hi, color=F.PETROL, height=ih, zorder=4)
        F.draw_hbar_ci(axa, y, cv_chg, clo_c, chi_c, color="#6E7781", height=ih, zorder=3)
        F.draw_hbar_ci(axa, y - dy, cv_sz, clo_s, chi_s, color="#AFB8C1", height=ih, zorder=3)

    axa.set_yticks(ys)
    axa.set_yticklabels([lab for _, lab in ORDER], fontsize=6.4, fontweight="normal", color=F.INK)
    axa.tick_params(axis="y", length=0, pad=4.0)
    axa.set_xlim(0.0, 0.84)
    axa.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8])
    axa.tick_params(axis="x", labelsize=6.4)
    axa.set_ylim(ys.min() - 0.54, ys.max() + 0.86)
    axa.set_xlabel(f"Share of exploited plans flipping to rejection ($n = {R['power'][3]}$)", fontsize=6.7)
    F.panel_header(axa, "a", "Verdict flip share under subsystem splice", pad_pt=7.5, letter_dx_pt=-9.5, gap_pt=9.5)

    leg_a = [
        F.bar_legend_handle(F.PETROL, label="Engine splice"),
        F.bar_legend_handle("#6E7781", label="Change-matched"),
        F.bar_legend_handle("#AFB8C1", label="Size-matched"),
        F.band_line_legend_handle("#E6E8EB", "#444444", label="Unpatched redraw (95% CI)"),
    ]
    F.clean_legend(
        fig, leg_a, loc="upper left", ncol=2, fontsize=6.15,
        bbox_to_anchor=(0.155, 0.990), columnspacing=0.95, labelspacing=0.25,
    )

    # Panel (b): Paired excess over matched change-count control (All tasks vs Recover)
    F.decorate_bar_axis(axb, zero_spine=False, wrect=3.2)
    axb.axhline(sep_y, color="#CCCCCC", lw=0.55, ls="-", zorder=1)

    paired_all = P["part3"]["paired"]["all"]
    paired_rec = P["part3"]["paired"]["recover"]
    for (m, _), y in zip(ORDER, ys):
        mk = SYM_KEY.get(m, m)
        ea = paired_all[f"{mk} - changed~{mk}"]
        er = paired_rec[f"{mk} - changed~{mk}"]

        F.draw_hbar_ci(
            axb, y + 0.13, ea["diff"], ea["lo_corr"], ea["hi_corr"],
            color=F.DARK_NEUTRAL, height=0.22, zorder=3,
        )
        F.draw_hbar_ci(
            axb, y - 0.13, er["diff"], er["lo_corr"], er["hi_corr"],
            color=F.VERMILION, height=0.22, zorder=3,
        )

    axb.set_xlim(-0.60, 0.46)
    axb.set_xticks([-0.6, -0.4, -0.2, 0.0, 0.2, 0.4])
    axb.tick_params(axis="x", labelsize=6.4)
    axb.set_xlabel("Paired excess flip rate over change-matched control", fontsize=6.7)
    F.panel_header(axb, "b", "Causal excess over control (99.7% BCa CI)", pad_pt=7.5, letter_dx_pt=-9.5, gap_pt=9.5)

    leg_b = [
        F.bar_legend_handle(F.DARK_NEUTRAL, label="All 5 task families"),
        F.bar_legend_handle(F.VERMILION, label="Post-quake recovery (recover)"),
    ]
    F.clean_legend(
        fig, leg_b, loc="upper right", ncol=1, fontsize=6.20,
        bbox_to_anchor=(0.985, 0.990), labelspacing=0.25,
    )

    F.save(
        fig, "fig_mechanism.pdf",
        {"inputs": [str(SRC.relative_to(F.REPO)), str(PC.relative_to(F.REPO))], "records": R["power"][3]},
    )


if __name__ == "__main__":
    main()
