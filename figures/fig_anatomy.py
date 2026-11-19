"""Appendix Figure 10 (fig_anatomy.pdf): Simulator anatomy of one Micropolis city-month (speed 1).

Verifies every engine constant against the patched C++ sources before drawing, and renders a
Nature / DeepMind (AlphaDev Fig. 2 / AlphaTensor Fig. 2) architectural schematic:
  (a) Five-stage deterministic phase pipeline inside the 4-cycle monthly execution loop,
  (b) Three-stage square-pixel procedural micro-sprite progression of budgeted DFS power routing,
  (c) Three-track 24-month timing diagram of capital outlays, demand-valve lag, and annual taxes.
Zero barcode register grids, zero rounded boxes, zero banned Unicode symbols.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

SRC = F.REPO / "engine" / "src"


def check_sources():
    sim = (SRC / "simulate.cpp").read_text()
    pw = (SRC / "power.cpp").read_text()
    mh = (SRC / "micropolis.h").read_text()
    facts = {
        "coal": re.search(r"COAL_POWER_STRENGTH = (\d+)L", pw).group(1),
        "nuclear": re.search(r"NUCLEAR_POWER_STRENGTH = (\d+)L", pw).group(1),
        "census": re.search(r"CENSUS_FREQUENCY_10 = (\d+);", sim).group(1),
        "tax": re.search(r"TAX_FREQUENCY = (\d+);", sim).group(1),
        "power_period": re.search(r"speedPowerScan\[3\] =\s*\{\s*(\d+),", sim).group(1),
        "poll_period": re.search(r"SpeedPollutionTerrainLandValueScan\[3\] =\s*\{\s*(\d+),", sim).group(1),
        "stack": re.search(r"POWER_STACK_SIZE = \(WORLD_W \* WORLD_H\) / (\d+);", mh).group(1),
    }
    assert facts["coal"] == "700" and facts["nuclear"] == "2000", facts
    assert facts["census"] == "4" and facts["tax"] == "48", facts
    assert facts["power_period"] == "2" and facts["poll_period"] == "2", facts
    assert facts["stack"] == "4", facts
    assert "if (!(simCycle & 1))" in sim and "setValves();" in sim
    return facts


def _arrow(ax, x1: float, y1: float, x2: float, y2: float, lw: float = 0.55, color: str = "#000000") -> None:
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_width=0.95,head_length=1.10",
        lw=lw, color=color, shrinkA=0, shrinkB=0, zorder=5,
    ))


def _stage_box(ax, x: float, y: float, w: float, h: float, title: str, sub: str, fc: str = "#FFFFFF", ec: str = "#1A1A1A") -> None:
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, lw=0.55, zorder=2))
    ax.text(x + w / 2, y + h * 0.69, title, fontsize=6.2, fontweight="bold", color=F.INK, ha="center", va="center", zorder=4)
    ax.text(x + w / 2, y + h * 0.30, sub, fontsize=5.7, fontweight="normal", color="#333333",
            ha="center", va="center", linespacing=1.14, zorder=4)


def _sprite_card(mode: str) -> np.ndarray:
    """Build a 6 x 5 tile procedural micro-sprite vignette for each DFS stage."""
    t = np.zeros((6, 5), dtype=np.int16)
    p = np.zeros((6, 5), dtype=bool)
    if mode == "root":
        for px in range(4):
            for py in range(4):
                t[px, py] = 745 + py * 4 + px
                p[px, py] = True
        t[4:6, 1:3] = 208
        p[4:6, 1:3] = True
        t[:, 4] = 66
    elif mode == "active":
        t[0:6, 2] = 208
        p[0:6, 2] = True
        for zx in range(3):
            for zy in range(2):
                t[zx, zy] = 270 + zy * 3 + zx
                p[zx, zy] = True
                t[3 + zx, zy] = 441 + zy * 3 + zx
                p[3 + zx, zy] = True
        for zx in range(6):
            t[zx, 3] = 66
            t[zx, 4] = 29
    else:
        t[0:2, 2] = 208
        p[0:2, 2] = True
        t[2:6, 2] = 208
        p[2:6, 2] = False
        for zx in range(3):
            for zy in range(2):
                t[zx, zy] = 827 if (zx == 1 and zy == 0) else (630 + zy * 3 + zx)
                p[zx, zy] = False
                t[3 + zx, zy] = 827 if (zx == 1 and zy == 1) else (441 + zy * 3 + zx)
                p[3 + zx, zy] = False
        for zx in range(6):
            t[zx, 3] = 66
            t[zx, 4] = 4
    return F.render_city(t, p, scale=10)


def main():
    facts = check_sources()
    F.apply()
    W, Hh = F.TEXT_IN, 2.58
    fig = plt.figure(figsize=(W, Hh), facecolor="#FFFFFF")
    ax = fig.add_axes([0, 0, 1, 1], facecolor="#FFFFFF")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 44)
    ax.axis("off")

    # =========================================================================
    # Panel a: Five-stage monthly execution pipeline inside 4-cycle loop frame
    # =========================================================================
    ax.text(0.6, 41.2, "a", color=F.INK, fontsize=8.0, fontweight="bold", va="baseline")
    ax.text(2.6, 41.2, "Monthly simulator step (four simulation cycles per month, sixteen phases per cycle)",
            fontsize=7.0, fontweight="normal", color=F.INK, va="baseline")

    yb_box, hb_box = 28.8, 7.6
    # Clean dashed cycle container on pure white canvas (zero grey card fill)
    loop_x, loop_w = 14.0, 72.0
    ax.add_patch(Rectangle((loop_x, 24.4), loop_w, 14.6, facecolor="none", edgecolor="#666666",
                           lw=0.55, ls=(0, (3.2, 2.0)), zorder=1))
    ax.text(loop_x + 1.0, 37.8,
            f"4 cycles per month (odd cycles skip Phases 0, 11, and 12; period = {facts['power_period']} cycles)",
            fontsize=5.8, fontweight="normal", color="#333333", va="center", ha="left")

    # Input & output endpoint blocks
    _stage_box(ax, 0.6, yb_box, 11.4, hb_box, "Policy action", "Tax, 3 budgets,\nup to 4 builds", "#F5F5F5", "#1A1A1A")
    _arrow(ax, 12.15, yb_box + hb_box / 2, 15.15, yb_box + hb_box / 2)

    stages = [
        ("Phase 0", "Demand valves\n(even cycles)"),
        ("Phases 1 to 8", "1/8 map zone\nscan (each cyc.)"),
        ("Phases 9 to 10", "Census, taxes,\ntraffic decay"),
        ("Phases 11 to 12", "DFS power, land\nval. (even cyc.)"),
        ("Phases 13 to 15", "Crime, fire, and\ndisasters (each)"),
    ]
    sx0, sw, sgap = 15.35, 12.25, 1.98
    for idx, (st_tit, st_sub) in enumerate(stages):
        sx = sx0 + idx * (sw + sgap)
        _stage_box(ax, sx, yb_box, sw, hb_box, st_tit, st_sub, "#FFFFFF", "#1A1A1A")
        if idx < len(stages) - 1:
            _arrow(ax, sx + sw + 0.14, yb_box + hb_box / 2, sx + sw + sgap - 0.14, yb_box + hb_box / 2)

    last_right = sx0 + (len(stages) - 1) * (sw + sgap) + sw
    _arrow(ax, last_right + 0.15, yb_box + hb_box / 2, 87.85, yb_box + hb_box / 2)
    _stage_box(ax, 88.0, yb_box, 11.4, hb_box, "Month state", "120 by 100 map,\noverlays, ledger", "#F5F5F5", "#1A1A1A")

    # Unbroken cycle-return feedback line beneath the 5 stages with label positioned cleanly below
    y_ret = 26.85
    ax.plot([last_right - 2.2, last_right - 2.2, sx0 + 2.2], [yb_box, y_ret, y_ret], color="#333333", lw=0.55, zorder=3)
    _arrow(ax, sx0 + 2.2, y_ret, sx0 + 2.2, yb_box - 0.08, lw=0.55, color="#333333")
    ax.text(0.5 * (sx0 + last_right), y_ret - 0.55, "Repeat cycles 1 to 4",
            fontsize=5.65, color="#333333", ha="center", va="top")

    # =========================================================================
    # Panel b: Three-stage procedural micro-sprite flow for budgeted DFS power
    # =========================================================================
    by = 20.0
    ax.text(0.6, by, "b", color=F.INK, fontsize=8.0, fontweight="bold", va="baseline")
    ax.text(2.6, by, "Budgeted depth-first power routing (Phase 11)", fontsize=7.0, fontweight="normal", color=F.INK, va="baseline")

    stack_cap = 120 * 100 // int(facts["stack"])
    cards = [
        ("root", "1. Plant root", f"Coal ({int(facts['coal']):,}) or\nnuclear ({int(facts['nuclear']):,})"),
        ("active", "2. DFS flood-fill", "Connected zones\nreceive power"),
        ("cutoff", "3. Cap reached", f"{stack_cap:,}-node cap;\nrest unpowered"),
    ]
    w_card_frac = 0.112
    h_card_frac = (w_card_frac * W * (5.0 / 6.0)) / Hh
    y_card_frac = 0.125
    x_cards_frac = [0.012, 0.172, 0.332]

    for idx_c, (mode, c_head, c_sub) in enumerate(cards):
        xf = x_cards_frac[idx_c]
        ins = ax.inset_axes([xf, y_card_frac, w_card_frac, h_card_frac])
        ins.imshow(_sprite_card(mode), interpolation="nearest")
        ins.set_xticks([])
        ins.set_yticks([])
        for sp in ins.spines.values():
            sp.set_linewidth(0.55)
            sp.set_color(F.INK)
        xc_data = (xf + w_card_frac / 2.0) * 100.0
        ax.text(xc_data, (y_card_frac + h_card_frac) * 44.0 + 0.65, c_head,
                fontsize=6.0, fontweight="normal", color=F.INK, ha="center", va="bottom")
        ax.text(xc_data, y_card_frac * 44.0 - 0.65, c_sub,
                fontsize=5.65, color="#333333", ha="center", va="top", linespacing=1.12)
        if idx_c < 2:
            x1_d = (xf + w_card_frac + 0.008) * 100.0
            x2_d = (x_cards_frac[idx_c + 1] - 0.008) * 100.0
            yc_d = (y_card_frac + h_card_frac / 2.0) * 44.0
            _arrow(ax, x1_d, yc_d, x2_d, yc_d, lw=0.55, color=F.INK)

    # =========================================================================
    # Panel c: Conformant 24-month event-timing axis (0.55pt left & bottom spines)
    # =========================================================================
    ax.text(50.5, by, "c", color=F.INK, fontsize=8.0, fontweight="bold", va="baseline")
    ax.text(52.5, by, "Multi-rate fiscal and demand horizon", fontsize=7.0, fontweight="normal", color=F.INK, va="baseline")

    ins_c = ax.inset_axes([0.642, 0.132, 0.348, 0.285])
    F.decorate_axis(ins_c, grid="x", wrect=2.2, hrect=2.2)

    y_tracks = [2.0, 1.0, 0.0]
    for yt in y_tracks:
        ins_c.plot([0, 24], [yt, yt], color="#D4D4D4", lw=0.45, zorder=1)

    # Track 1 (top): Monthly capital outlays at m = 1..24
    ms_all = np.arange(1, 25)
    ins_c.vlines(ms_all, y_tracks[0] - 0.20, y_tracks[0] + 0.20, color="#222222", linewidth=0.75, zorder=3)
    ins_c.text(12.2, y_tracks[0] + 0.21, "Monthly deductions", fontsize=5.45, color=F.INK, ha="center", va="bottom")

    # Track 2 (middle): 16-month census demand-valve lag window (0 to 16)
    ins_c.plot([0, 16], [y_tracks[1], y_tracks[1]], color=F.BLUE, lw=2.2, solid_capstyle="butt", alpha=0.28, zorder=2)
    ins_c.vlines([16], y_tracks[1] - 0.22, y_tracks[1] + 0.22, color=F.BLUE, linewidth=1.45, zorder=4)
    ins_c.text(8.0, y_tracks[1] + 0.21, "16-month census lag", fontsize=5.45, color=F.INK, ha="center", va="bottom")

    # Track 3 (bottom): Annual 12-month tax & budget settlements at m = 12 and m = 24
    ins_c.plot([0, 24], [y_tracks[2], y_tracks[2]], color=F.PETROL, lw=2.2, solid_capstyle="butt", alpha=0.24, zorder=2)
    ins_c.vlines([12, 24], y_tracks[2] - 0.22, y_tracks[2] + 0.22, color=F.PETROL, linewidth=1.45, zorder=4)
    ins_c.text(6.0, y_tracks[2] + 0.21, "12-month settlement", fontsize=5.45, color=F.INK, ha="center", va="bottom")

    ins_c.set_xlim(0.0, 24.5)
    ins_c.set_ylim(-0.42, 2.55)
    ins_c.set_xticks([0, 4, 8, 12, 16, 20, 24])
    ins_c.tick_params(axis="x", labelsize=5.9, length=2.2, width=0.55, pad=2.0)
    ins_c.set_yticks(y_tracks)
    ins_c.set_yticklabels(["Capital outlays", "Demand valves", "Taxes and budgets"],
                          fontsize=5.85, color=F.INK, linespacing=1.05)
    ins_c.tick_params(axis="y", length=2.0, width=0.55, pad=3.0)
    ins_c.set_xlabel("Simulation month", fontsize=6.2, labelpad=2.0)

    F.save(fig, "fig_anatomy.pdf", {"engine_facts_checked": facts, "kind": "designed diagram with procedural sprites"})


if __name__ == "__main__":
    main()
