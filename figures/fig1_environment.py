"""Figure 1: One action plan, two cities, and causal localization of the world model's error.

Reads figures/data/fig1_case.{npz,json} and the primary world model's counterfactual patching
records (results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24/patching.jsonl.gz).
Renders procedural micro-sprite 24-month maps (a, b), unified power-grid telemetry over the
24-month rollout (c), and a solid horizontal subsystem-patching bar chart (d).
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO = F.REPO
sys.path.insert(0, str(REPO / "code"))
from dc.engine import SCALAR_NAMES  # noqa: E402

RUN = REPO / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24"
PATCH = RUN / "patching.jsonl.gz"
S = {n: i for i, n in enumerate(SCALAR_NAMES)}
SUBSYSTEMS = [
    ("none", "Unpatched redraw"),
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


def powered_share(sc):
    p, u = sc[..., S["powered_zones"]], sc[..., S["unpowered_zones"]]
    return np.where(p + u > 0, p / np.maximum(p + u, 1), np.nan)


def plants(sc):
    return sc[..., S["coal_plants"]] + sc[..., S["nuclear_plants"]]


def _mini_swatch(tile_code: int, powered: bool = True, plant_block: bool = False) -> np.ndarray:
    """Render a tiny 2x2 tile micro-sprite swatch for the legend."""
    t = np.full((2, 2), tile_code, dtype=np.int16)
    if plant_block:
        t = np.array([[745, 746], [753, 754]], dtype=np.int16)
    elif tile_code == 66:
        t = np.array([[66, 150], [76, 66]], dtype=np.int16)
    elif tile_code == 208:
        t = np.array([[208, 208], [209, 208]], dtype=np.int16)
    elif tile_code == 827:
        t = np.array([[440, 827], [442, 445]], dtype=np.int16)
    p = np.full((2, 2), powered, dtype=bool)
    return F.render_city(t, p, scale=8)


def main():
    F.apply()
    z = np.load(F.DATA / "fig1_case.npz")
    meta = json.loads((F.DATA / "fig1_case.json").read_text())
    k = int(meta["shown_sample"])
    H = z["eng_tiles"].shape[0] - 1

    recs = [json.loads(l) for l in gzip.open(PATCH, "rt")]
    recs = [r for r in recs if r["plan_id"] == meta["plan_id"] and r["primary_set"]]
    by_mask = {r["mask"]: r for r in recs}
    Kp = int(meta["K"])
    passing = {m: int(round(by_mask[m]["p"] * Kp)) for m, _ in SUBSYSTEMS}
    flips = {m: bool(by_mask[m]["flip"]) for m, _ in SUBSYSTEMS}

    s_cls = F.tile_class(z["start_tiles"])
    e_cls = F.tile_class(z["eng_tiles"][-1])
    ch = np.argwhere(e_cls != s_cls)
    x0, x1 = max(0, ch[:, 0].min() - 3), min(119, ch[:, 0].max() + 3)
    y0, y1 = max(0, ch[:, 1].min() - 4), min(99, ch[:, 1].max() + 3)
    side = max(x1 - x0, y1 - y0) + 1
    x0 = max(0, min(x0, 120 - side))
    y0 = max(0, min(y0, 100 - side))
    xs, ys = slice(x0, x0 + side), slice(y0, y0 + side)

    eng_img = F.render_city(z["eng_tiles"][-1][xs, ys] & F.LOMASK, z["eng_power"][-1][xs, ys] > 0, scale=10)

    eng_pl = plants(z["eng_scal_seed0"])
    drop = int(np.flatnonzero(np.diff(eng_pl) < 0)[0]) + 1 if (np.diff(eng_pl) < 0).any() else None
    plant_cls = F.CLASSES.index("plant")
    lost = (F.tile_class(z["eng_tiles"][drop - 1]) == plant_cls) & (F.tile_class(z["eng_tiles"][drop]) != plant_cls)
    lost_xy = np.argwhere(lost)
    lx, ly = lost_xy.mean(axis=0)
    px0, py0 = lost_xy.min(axis=0) - 0.5
    pw_box, ph_box = (lost_xy.max(axis=0) - lost_xy.min(axis=0) + 1)

    emu_pl = plants(z["emu_scal"])
    emu_lose = (emu_pl[:, drop] < emu_pl[:, drop - 1]) if drop is not None else np.zeros(len(emu_pl), bool)
    emu_pass = np.asarray(meta["emulator_passes"], bool)
    rep = np.flatnonzero(emu_lose & emu_pass)
    shown_rule = (
        "first sample that loses a plant at the engine's drop month and passes" if rep.size else meta["shown_rule"]
    )
    k = int(rep[0]) if rep.size else k
    emu_img = F.render_city(z["emu_tile_index"][k][xs, ys], z["emu_power"][k][xs, ys] > 0, scale=10)
    emu_keeps = bool((F.tile_class(z["emu_tile_index"][k])[lost] == plant_cls).mean() > 0.5)

    fig_w, fig_h = F.TEXT_IN, 4.32
    fig = plt.figure(figsize=(fig_w, fig_h))

    # Shared vertical alignment grid: Col 1 (a, c) at x_col1; Col 2 (b, d) at x_col2
    x_col1 = 0.074
    x_col2 = 0.506
    s_in = 2.02
    w_map = s_in / fig_w
    h_map = s_in / fig_h
    y_map = 0.470

    def draw_city_card(ax, img, title, letter, summary_txt):
        ax.imshow(img, interpolation="nearest", extent=(x0 - 0.5, x0 + side - 0.5, y0 + side - 0.5, y0 - 0.5))
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(True); sp.set_linewidth(0.55); sp.set_color(F.INK)
        F.panel_header(ax, letter, title, pad_pt=5.8, letter_dx_pt=0.0, gap_pt=10.8)
        ax.text(
            0.0, -0.036, summary_txt,
            transform=ax.transAxes, fontsize=5.95, fontweight="normal", va="top", color=F.INK,
        )

    ax_e = fig.add_axes([x_col1, y_map, w_map, h_map])
    ax_g = fig.add_axes([x_col2, y_map, w_map, h_map])
    n_emu = int(np.sum(meta["emulator_passes"]))
    n_or = int(round(meta["engine_oracle_share_recomputed"] * 32))
    p_e = int(z["emu_scal"][k, -1, S["powered_zones"]])
    u_e = int(z["emu_scal"][k, -1, S["unpowered_zones"]])
    p_g = int(z["eng_scal_seed0"][-1, S["powered_zones"]])
    u_g = int(z["eng_scal_seed0"][-1, S["unpowered_zones"]])

    draw_city_card(
        ax_e, emu_img, f"World-model rollout (month {H})", "a",
        f"{p_e}/{p_e + u_e} zones powered, {n_emu}/{meta['K']} pass (first passing rollout)",
    )
    draw_city_card(
        ax_g, eng_img, f"Exact simulator (month {H})", "b",
        f"{p_g}/{p_g + u_g} surviving zones powered, {n_or}/32 seeds pass",
    )

    if drop is not None:
        for ax_m, txt in (
            (ax_e, "Plant cleared,\nzones stay lit"),
            (ax_g, f"Coal plant retired (m = {drop}),\ngrid blackout"),
        ):
            ax_m.add_patch(Rectangle((px0, py0), pw_box, ph_box, fill=False, edgecolor="#FFFFFF", lw=1.45, ls="-"))
            ax_m.add_patch(Rectangle((px0, py0), pw_box, ph_box, fill=False, edgecolor=F.INK, lw=0.80, ls=(0, (3, 2))))
            ax_m.annotate(
                txt, xy=(lx + 1.6, ly), xytext=(lx + 0.23 * side, ly + 0.05 * side),
                fontsize=5.9, fontweight="normal", color=F.INK, linespacing=1.18,
                bbox=dict(
                    boxstyle="round,pad=0.24,rounding_size=0.14",
                    facecolor="#FFFFFF", edgecolor="#555555", lw=0.45, alpha=0.95,
                ),
                arrowprops=dict(
                    arrowstyle="-|>,head_width=0.14,head_length=0.24",
                    lw=0.55, color="#222222", shrinkA=0, shrinkB=2,
                ),
                va="center",
            )

    # Top-right: Procedural Micro-Sprite Key (unified 1:1 with Fig. 2)
    ax_l = fig.add_axes([0.834, y_map, 0.160, h_map])
    ax_l.set_xlim(0, 1); ax_l.set_ylim(0, 1); ax_l.axis("off")
    ax_l.text(0.02, 1.0, "Tile key", fontsize=7.0, fontweight="normal", color=F.INK,
              va="baseline", transform=ax_l.transAxes + plt.matplotlib.transforms.ScaledTranslation(0, 5.8 / 72.0, fig.dpi_scale_trans))
    swatches = [
        (_mini_swatch(274, True), "Residential"),
        (_mini_swatch(445, True), "Commercial"),
        (_mini_swatch(634, True), "Industrial"),
        (_mini_swatch(765, True), "Civic"),
        (_mini_swatch(745, True, plant_block=True), "Power plant"),
        (_mini_swatch(66, True), "Road / traffic"),
        (_mini_swatch(208, True), "Power line"),
        (_mini_swatch(4, True), "Water"),
        (_mini_swatch(29, True), "Trees"),
        (_mini_swatch(827, False), "Blackout"),
    ]
    y_top = 0.945
    step_y = 0.095
    for idx_s, (sw_img, label) in enumerate(swatches):
        yc = y_top - idx_s * step_y
        ins = ax_l.inset_axes([0.02, yc - 0.055, 0.175, 0.068])
        ins.imshow(sw_img, interpolation="nearest")
        ins.set_xticks([]); ins.set_yticks([])
        for sp in ins.spines.values():
            sp.set_linewidth(0.45); sp.set_color(F.INK)
        ax_l.text(0.24, yc - 0.021, label, fontsize=6.15, fontweight="normal", color=F.INK, va="center")

    # Bottom row: Two equal-height axes whose visible left spines and letters align 1:1 with (a) and (b)
    hrect_pt = 2.8
    hrect_fig = hrect_pt / (72.0 * fig_w)
    y_bot, h_bot = 0.084, 0.262
    ax_pw = fig.add_axes([x_col1 + hrect_fig, y_bot, w_map - hrect_fig, h_bot])
    ax_s = fig.add_axes([x_col2, y_bot, 0.468, h_bot])

    # Panel (c): Unified power-grid telemetry across 8 world-model rollouts vs 32 simulator seeds
    months = np.arange(H + 1)
    F.decorate_axis(ax_pw, grid="y", wrect=2.8, hrect=hrect_pt)

    es = powered_share(z["eng_scal"])
    ax_pw.fill_between(months, np.nanmin(es, 0), np.nanmax(es, 0), color=F.BLUE, alpha=0.12, lw=0, zorder=1)
    for s_idx in range(es.shape[0]):
        ax_pw.plot(months, es[s_idx], color=F.BLUE, lw=0.40, alpha=0.20, zorder=2)
    ax_pw.plot(months, powered_share(z["eng_scal_seed0"]), color=F.BLUE, lw=1.40, ls="-", zorder=4)

    for j in range(z["emu_scal"].shape[0]):
        ax_pw.plot(
            months, powered_share(z["emu_scal"][j]),
            color=F.RED if j == k else F.RED_MID,
            lw=1.45 if j == k else 0.55,
            alpha=1.0 if j == k else 0.30,
            zorder=5 if j == k else 3,
        )

    ax_pw.axhline(0.95, color="#666666", lw=0.55, ls=(0, (1.2, 1.5)), zorder=2)
    ax_pw.annotate(
        "Pass threshold\n(0.95)",
        xy=(1.9, 0.95), xytext=(0.45, 0.892),
        fontsize=5.8, color="#444444", ha="left", va="top", linespacing=1.10,
        arrowprops=dict(arrowstyle="-", lw=0.45, color="#777777", shrinkA=0, shrinkB=1),
    )

    if drop is not None:
        p_pre = int(eng_pl[drop - 1])
        p_post = int(eng_pl[drop])
        ax_pw.axvline(drop, color="#666666", lw=0.55, ls=(0, (3.0, 1.8)), zorder=2)
        ax_pw.text(
            drop + 0.50, 0.865,
            f"Plant retired (m = {drop}, {p_pre} to {p_post})",
            fontsize=5.8, color="#222222", ha="left", va="center",
            bbox=dict(boxstyle="square,pad=0.06", facecolor="#FFFFFF", edgecolor="none", alpha=0.88),
        )

    ax_pw.set_ylim(0.44, 1.04)
    ax_pw.set_yticks([0.50, 0.75, 1.00])
    ax_pw.set_xlim(0, H)
    ax_pw.set_xticks([0, 6, 12, 18, 24])
    ax_pw.tick_params(axis="both", labelsize=6.2)
    ax_pw.set_ylabel("Powered-zone share", fontsize=6.7)
    ax_pw.set_xlabel("Simulation month", fontsize=6.7)

    c_handles = [
        Line2D([], [], color=F.RED, lw=1.45, label=f"World model ({meta['K']} rollouts, {n_emu}/{meta['K']} pass)"),
        Line2D([], [], color=F.BLUE, lw=1.40, label=f"Exact simulator (32 seeds, {n_or}/32 pass)"),
    ]
    F.clean_legend(
        ax_pw, c_handles, loc="lower right", bbox_to_anchor=(0.995, 0.020),
        fontsize=5.85, handlelength=1.25, labelspacing=0.22,
    )
    F.panel_header(ax_pw, "c", "Power-grid telemetry across rollout", pad_pt=13.5, letter_dx_pt=-hrect_pt, gap_pt=10.8)

    # Panel (d): Nature / DeepMind horizontal count plot anchored on 0.55pt zero spine
    F.decorate_bar_axis(ax_s, zero_spine=True, wrect=2.8)

    yy = np.arange(len(SUBSYSTEMS))[::-1].astype(float)
    yy[0] += 0.45
    sep_y = 0.5 * (yy[0] + yy[1])
    ax_s.plot([0.0, float(Kp)], [sep_y, sep_y], color="#D0D4D9", lw=0.50, ls="-", zorder=1)

    y_lo, y_hi = yy.min() - 0.60, yy.max() + 0.85
    ax_s.plot([Kp / 2.0, Kp / 2.0], [y_lo, yy[0] + 0.36], color="#555555", lw=0.55, ls=(0, (3.0, 1.8)), zorder=2)
    ax_s.text(
        Kp / 2.0, yy[0] + 0.46, f"Majority pass ({Kp // 2}/{Kp})",
        fontsize=5.8, color="#444444", ha="center", va="bottom", clip_on=False,
    )

    for (m, _lab), y in zip(SUBSYSTEMS, yy):
        n = passing[m]
        is_flip = flips[m]
        lcol = "#6E7781" if m == "none" else F.PETROL
        if n > 0:
            ax_s.plot([0.0, float(n)], [y, y], color=lcol, lw=1.15, solid_capstyle="butt", zorder=3)
        if is_flip:
            ax_s.plot(
                [float(n)], [y], marker="o", markersize=5.4,
                markerfacecolor="#FFFFFF", markeredgecolor="none",
                linestyle="none", zorder=5, clip_on=False,
            )
            ax_s.plot(
                [float(n)], [y], marker="o", markersize=4.1,
                markerfacecolor="#FFFFFF", markeredgecolor=F.RED, markeredgewidth=1.15,
                linestyle="none", zorder=6, clip_on=False,
            )
            ax_s.text(
                0.28, y, f"{n}/{Kp} (flips to reject)",
                va="center", ha="left", fontsize=5.85, fontweight="normal", color=F.RED, zorder=6,
                bbox=dict(boxstyle="square,pad=0.06", facecolor="#FFFFFF", edgecolor="none", alpha=0.92),
            )
        else:
            ax_s.plot(
                [float(n)], [y],
                marker="o", markersize=3.8,
                markerfacecolor=F.PETROL if m != "none" else "#6E7781",
                markeredgecolor="#FFFFFF", markeredgewidth=0.55,
                linestyle="none", zorder=5, clip_on=False,
            )

    ax_s.set_yticks(yy)
    ax_s.set_yticklabels([lab for _, lab in SUBSYSTEMS], fontsize=6.15, fontweight="normal", color=F.INK)
    ax_s.set_xlim(0.0, float(Kp) + 0.30)
    ax_s.spines["bottom"].set_bounds(0, Kp)
    ax_s.set_xticks(list(range(0, Kp + 1)))
    ax_s.tick_params(axis="x", labelsize=6.2)
    ax_s.set_ylim(y_lo, y_hi)
    ax_s.set_xlabel(f"Rollouts passing out of {Kp} after splice", fontsize=6.7)
    ax_s.tick_params(axis="y", length=0, pad=4.8)
    F.panel_header(ax_s, "d", "Counterfactual subsystem patching", pad_pt=13.5, letter_dx_pt=0.0, gap_pt=10.8)

    other = [passing[m] for m, _ in SUBSYSTEMS if m not in ("none", "power")]
    prov = {
        "inputs": [
            str(F.DATA.relative_to(REPO) / "fig1_case.npz"),
            str(F.DATA.relative_to(REPO) / "fig1_case.json"),
            str(PATCH.relative_to(REPO)),
        ],
        "case": {k2: meta[k2] for k2 in ("instance", "plan_id", "torch_seed", "engine_seed_map")},
        "shown_sample": k,
        "shown_rule": shown_rule,
        "audit_emulator_passing": int(round(meta["audit_emulator_pass_share"] * meta["K"])),
        "crop_tiles": [int(x0), int(y0), int(side)],
        "plant_drop_month": drop,
        "emulator_keeps_plant": emu_keeps,
        "emulator_samples": int(len(emu_pass)),
        "emulator_samples_passing": int(emu_pass.sum()),
        "emulator_samples_losing_plant_at_drop": int(emu_lose.sum()),
        "emulator_samples_losing_plant_and_passing": int((emu_lose & emu_pass).sum()),
        "engine_seeds_passing": int(round(meta["engine_oracle_share_recomputed"] * 32)),
        "engine_zones_off_grid_seed0_end": int(z["eng_scal_seed0"][-1, S["unpowered_zones"]]),
        "engine_zones_seed0_end": int(
            z["eng_scal_seed0"][-1, S["unpowered_zones"]] + z["eng_scal_seed0"][-1, S["powered_zones"]]
        ),
        "shown_sample_zones_off_grid_end": int(z["emu_scal"][k, -1, S["unpowered_zones"]]),
        "n_accepted_but_rejected": int(meta["n_accepted_but_rejected"]),
        "patch_samples": Kp,
        "patch_passing": passing,
        "patch_flips": flips,
        "patch_power_passing": passing["power"],
        "patch_none_passing": passing["none"],
        "patch_other_min_passing": int(min(other)),
    }
    F.save(fig, "fig1_environment.pdf", prov)


if __name__ == "__main__":
    main()
