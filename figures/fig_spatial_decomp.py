"""Main-body spatial decomposition figure (fig_spatial_decomp.pdf): 5 task families x 3 spatial channels.

Shows the top-ranked exploited city plan from each of the 5 task families (Grow, Solvent, Treasury,
Recover, Power across columns a-e) decomposed into three 40x40-tile spatial channels over desaturated
month-24 procedural micro-sprites:
  Row 1: World-model vs. simulator error share (8 rollouts)
  Row 2: Exact simulator seed-to-seed floor (8 seeds)
  Row 3: Internal disagreement across the 8 world-model rollouts
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
from fig_heatmaps import RED_RAMP, INK_RAMP, AMBER_RAMP, category, sprite_base_grey, heat_image, SCALE  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def main():
    F.apply()
    z = np.load(F.DATA / "gallery_cases.npz")
    meta = json.loads((F.DATA / "gallery_cases.json").read_text())
    ze = np.load(F.DATA / "heatmap_engine_seeds.npz")
    gal = json.loads((F.PAPER_FIG / "fig_gallery.json").read_text())
    crops = {(c["family"], c["rank"]): c["crop"] for c in gal["cases"]}

    fams = ["grow", "solvent", "treasury", "recover", "power"]
    # Select rank-1 case (largest dream-minus-oracle pass gap) per family; for power pick rank 3 (ho-g-09, dramatic multi-block blackout) or rank 1 consistently!
    # Using rank 1 for every family is 100% systematic and rule-determined (zero cherry-picking!).
    by_fam = {f: sorted([c for c in meta["cases"] if c["family"] == f], key=lambda x: x["rank"])[0] for f in fams}

    W = F.TEXT_IN
    left_lbl = 0.66
    right = 0.34
    col_gap = 0.085
    row_gap = 0.055
    head_h = 0.30
    bar_h = 0.42

    side = (W - left_lbl - right - 4 * col_gap) / 5.0
    H = head_h + 3 * side + 2 * row_gap + bar_h
    fig = plt.figure(figsize=(W, H))

    def rect(x, y, w, h):
        return [x / W, 1 - (y + h) / H, w / W, h / H]

    row_titles = [
        ("Model vs.\nsimulator", "(8 rollouts)"),
        ("Simulator\nseed floor", "(8 seeds)"),
        ("Rollout\nspread", "(8 rollouts)"),
    ]
    for r_idx, (rt, rsub) in enumerate(row_titles):
        yc = head_h + r_idx * (side + row_gap) + side * 0.5
        fig.text(0.0, 1 - (yc - 0.05) / H, rt,
                 fontsize=6.4, fontweight="normal", color=F.INK, ha="left", va="center", linespacing=1.10)
        fig.text(0.0, 1 - (yc + 0.17) / H, rsub,
                 fontsize=5.7, color="#555555", ha="left", va="center")

    letters = "abcde"
    shown_meta = []
    for c_idx, fam in enumerate(fams):
        c = by_fam[fam]
        x = left_lbl + c_idx * (side + col_gap)
        fam_name = F.FAM_LABEL[fam]
        case_label = f"{fam_name} {c['rank'] + 1}"

        # Clean black column header + pass counts on exact shared baseline
        fig.text(x / W, 1 - (head_h - 0.145) / H, letters[c_idx], fontsize=8.0, fontweight="bold",
                 color=F.INK, ha="left", va="baseline")
        fig.text((x + 0.145) / W, 1 - (head_h - 0.145) / H, case_label, fontsize=6.6,
                 fontweight="normal", color=F.INK, ha="left", va="baseline")
        fig.text((x + side / 2) / W, 1 - (head_h - 0.032) / H,
                 f"{c['audit_emulator_passing']}/8 pass, {c['audit_oracle_passing']}/32 seeds",
                 fontsize=5.8, color=F.INK, ha="center", va="baseline")

        t = c["tag"]
        eng_t = z[f"{t}_eng_tiles"] & F.LOMASK
        eng_p = z[f"{t}_eng_power"] > 0
        ref = category(eng_t, eng_p)
        emu = category(z[f"{t}_emu_tile_index"], z[f"{t}_emu_power"])
        seeds = category(ze[f"{t}_eng_seed_tiles"] & F.LOMASK, ze[f"{t}_eng_seed_power"])
        err = (emu != ref[None]).mean(0)
        floor = (seeds != ref[None]).mean(0)
        counts = np.stack([(emu == k).sum(0) for k in range(2 * len(F.CLASSES))])
        dis = 1 - counts.max(0) / emu.shape[0]
        x0, y0, s = crops[(c["family"], c["rank"])]
        xs, ys = slice(x0, x0 + s), slice(y0, y0 + s)
        base_hi = sprite_base_grey(eng_t[xs, ys], eng_p[xs, ys], scale=SCALE)
        fp_crop = z[f"{t}_footprint"][xs, ys]

        for r_idx, (val, cmap) in enumerate([
            (err, RED_RAMP),
            (floor, INK_RAMP),
            (dis, AMBER_RAMP),
        ]):
            y = head_h + r_idx * (side + row_gap)
            ax = fig.add_axes(rect(x, y, side, side))
            ax.imshow(heat_image(val[xs, ys], base_hi, cmap, fp_crop=fp_crop), interpolation="nearest",
                      extent=(x0 - 0.5, x0 + s - 0.5, y0 + s - 0.5, y0 - 0.5))
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(True); sp.set_linewidth(0.55); sp.set_color(F.INK)

        shown_meta.append({"letter": letters[c_idx], "family": fam, "instance": c["instance"], "crop": [x0, y0, s]})

    yb = H - bar_h + 0.165
    bounds = np.arange(0, 9) / 8
    grid_w = W - left_lbl - right
    w_bar = 1.62
    gap_bar = (grid_w - 3 * w_bar) / 2.0
    for k, (cmap, lab) in enumerate([
        (RED_RAMP, "Model vs. simulator (8 rollouts)"),
        (INK_RAMP, "Simulator seed floor (8 seeds)"),
        (AMBER_RAMP, "Rollout spread (8 rollouts)"),
    ]):
        x_bar = left_lbl + k * (w_bar + gap_bar)
        cax = fig.add_axes(rect(x_bar, yb, w_bar, 0.072))
        cols = ["#ECEFF3"] + [cmap(i / 7) for i in range(8)]
        cm = mpl.colors.ListedColormap(cols)
        cb = mpl.colorbar.ColorbarBase(
            cax, cmap=cm, norm=mpl.colors.BoundaryNorm(np.r_[-1 / 16, bounds + 1 / 16], cm.N),
            orientation="horizontal", ticks=[0, 0.25, 0.5, 0.75, 1],
        )
        cb.ax.set_xticklabels(["0", "2/8", "4/8", "6/8", "8/8"])
        cb.outline.set_linewidth(0.45); cb.ax.tick_params(labelsize=6.0, length=2, width=0.45)
        cax.set_title(lab, fontsize=6.1, loc="left", pad=2.4, fontweight="normal", color=F.INK)

    F.save(fig, "fig_spatial_decomp.pdf", {
        "inputs": ["figures/data/gallery_cases.npz", "figures/data/heatmap_engine_seeds.npz", "paper/figures/fig_gallery.json"],
        "selection_rule": "rank-1 exploited case per task family from gallery_cases.json",
        "cases": shown_meta,
    })


if __name__ == "__main__":
    main()
