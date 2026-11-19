"""Appendix Figure (fig_heatmaps.pdf): Spatial error, engine seed floor, and sample disagreement.

For each of the 15 gallery cases (40x40-tile crops at month 24), overlays:
  (i)   World model vs. simulator error share (across 8 rollouts),
  (ii)  Exact simulator seed-to-seed floor (8 further seeds vs. primary seed),
  (iii) Internal disagreement among the 8 world-model rollouts,
over a desaturated procedural micro-sprite terrain underlay, with active construction
footprints outlined in gold and pure neutral black typography.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

PER_ROW = 3
SCALE = 8


def ramp(pale, col):
    return LinearSegmentedColormap.from_list("r", [pale, col], N=8)


RED_RAMP = ramp("#F4D0D2", F.RED)
INK_RAMP = ramp("#CFD5DF", F.INK)
AMBER_RAMP = ramp("#F7E2B8", "#B85D19")
NEED = [F.CLASSES.index(n) for n in F.NEEDS_POWER]


def category(tiles, power):
    c = F.tile_class(tiles).astype(np.int16)
    off = np.isin(c, NEED) & ~(np.asarray(power) > 0)
    return c + len(F.CLASSES) * off


def sprite_base_grey(tiles, power, scale=SCALE):
    """Desaturated high-key micro-sprite city underlay (rows = y, cols = x, scale px/tile)."""
    rgb = F.render_city(tiles, power, scale=scale)
    lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    return 0.78 + 0.20 * lum


def heat_image(value, base_hi, cmap, fp_crop=None, scale=SCALE):
    """Blend 8-step tile heatmap over high-key micro-sprite underlay + gold footprint border."""
    v = np.repeat(np.repeat(value.T, scale, axis=0), scale, axis=1)
    col = cmap(np.clip((v - 1 / 16) / (1 - 1 / 16), 0, 1))[..., :3]
    base_rgb = base_hi[..., None] * np.ones(3, dtype=np.float32)
    blended = 0.82 * col + 0.18 * base_rgb
    img = np.where((v > 0)[..., None], blended, base_rgb)
    if fp_crop is not None and fp_crop.any():
        f_up = np.repeat(np.repeat(fp_crop.T.astype(bool), scale, axis=0), scale, axis=1)
        eroded = (
            f_up
            & np.roll(f_up, 1, 0) & np.roll(f_up, -1, 0)
            & np.roll(f_up, 1, 1) & np.roll(f_up, -1, 1)
        )
        outline = f_up & ~eroded
        img[outline] = np.array(mpl.colors.to_rgb("#E09F1F"), dtype=np.float32)
    return img


def main():
    F.apply()
    z = np.load(F.DATA / "gallery_cases.npz")
    meta = json.loads((F.DATA / "gallery_cases.json").read_text())
    ze = np.load(F.DATA / "heatmap_engine_seeds.npz")
    me = json.loads((F.DATA / "heatmap_engine_seeds.json").read_text())
    assert me["gallery_arrays_sha256"] == meta["arrays_sha256"]
    gal = json.loads((F.PAPER_FIG / "fig_gallery.json").read_text())
    crops = {(c["family"], c["rank"]): c["crop"] for c in gal["cases"]}
    fams = ["grow", "solvent", "treasury", "recover", "power"]
    cases = sorted(meta["cases"], key=lambda c: (fams.index(c["family"]), c["rank"]))
    n_rows = int(np.ceil(len(cases) / PER_ROW))

    W = F.TEXT_IN
    left, right, in_gap, plan_gap = 0.02, 0.02, 0.032, 0.16
    head_h, label_h, row_gap, bar_h = 0.29, 0.172, 0.058, 0.44
    side = (W - left - right - (PER_ROW - 1) * plan_gap - PER_ROW * 2 * in_gap) / (3 * PER_ROW)
    row_h = label_h + side + row_gap
    H = head_h + n_rows * row_h + bar_h
    fig = plt.figure(figsize=(W, H))

    def rect(x, y, w, h):
        return [x / W, 1 - (y + h) / H, w / W, h / H]

    heads = [
        "(i) Model vs.\nsimulator",
        "(ii) Simulator\nseed floor",
        "(iii) Rollout\nspread",
    ]
    for j in range(PER_ROW):
        x = left + j * (3 * side + 2 * in_gap + plan_gap)
        for m, title_txt in enumerate(heads):
            fig.text((x + m * (side + in_gap) + side / 2) / W, 1 - (head_h - 0.042) / H, title_txt,
                     color=F.INK, fontsize=6.3, fontweight="normal", ha="center", va="bottom", linespacing=1.10)
        hl_ax = fig.add_axes([x / W, 1 - (head_h - 0.014) / H, (3 * side + 2 * in_gap) / W, 0.002])
        hl_ax.axis("off")
        hl_ax.axhline(0.5, color="#CCCCCC", lw=0.55)

    stats = []
    letters = "abcdefghijklmnopqrstuvwxyz"
    for n, c in enumerate(cases):
        r, j = divmod(n, PER_ROW)
        x = left + j * (3 * side + 2 * in_gap + plan_gap)
        y = head_h + r * row_h
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
        fp = z[f"{t}_footprint"]
        fp_crop = fp[xs, ys]

        for m, (val, cmap) in enumerate([
            (err, RED_RAMP),
            (floor, INK_RAMP),
            (dis, AMBER_RAMP),
        ]):
            ax = fig.add_axes(rect(x + m * (side + in_gap), y + label_h, side, side))
            ax.imshow(heat_image(val[xs, ys], base_hi, cmap, fp_crop=fp_crop), interpolation="nearest",
                      extent=(x0 - 0.5, x0 + s - 0.5, y0 + s - 0.5, y0 - 0.5))
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(True); sp.set_linewidth(0.55); sp.set_color(F.INK)

        fam_name = F.FAM_LABEL.get(c["family"], c["family"].capitalize())
        case_label = f"{fam_name} {c['rank'] + 1}"
        yb_txt = 1 - (y + label_h - 0.050) / H
        fig.text(x / W, yb_txt, letters[n], fontsize=8.0, fontweight="bold", color=F.INK,
                 ha="left", va="baseline")
        fig.text((x + 0.145) / W, yb_txt, case_label, fontsize=6.4,
                 fontweight="normal", color=F.INK, ha="left", va="baseline")
        fig.text((x + 3 * side + 2 * in_gap) / W, yb_txt,
                 f"{c['audit_emulator_passing']}/8 pass, {c['audit_oracle_passing']}/32 seeds",
                 fontsize=5.8, color=F.INK, ha="right", va="baseline")

        whole = lambda a: float(a.mean())
        onfp = lambda a: round(float(a[fp].mean()), 4) if fp.any() else None
        stats.append({
            "family": c["family"], "rank": c["rank"], "instance": c["instance"], "letter": letters[n],
            "error_mean_map": round(whole(err), 4), "floor_mean_map": round(whole(floor), 4),
            "disagree_mean_map": round(whole(dis), 4),
            "error_mean_footprint": onfp(err), "floor_mean_footprint": onfp(floor),
            "disagree_mean_footprint": onfp(dis),
            "error_mean_crop": round(float(err[xs, ys].mean()), 4),
            "floor_mean_crop": round(float(floor[xs, ys].mean()), 4),
            "disagree_mean_crop": round(float(dis[xs, ys].mean()), 4),
            "footprint_tiles": int(fp.sum()), "crop": [x0, y0, s],
        })

    yb = H - bar_h + 0.17
    bounds = np.arange(0, 9) / 8
    w_bar = 1.95
    gap_bar = (W - left - right - 3 * w_bar) / 2.0
    for k, (cmap, lab) in enumerate([
        (RED_RAMP, "(i) Model vs. simulator (8 rollouts)"),
        (INK_RAMP, "(ii) Simulator seed floor (8 seeds)"),
        (AMBER_RAMP, "(iii) Rollout spread (8 rollouts)"),
    ]):
        x_bar = left + k * (w_bar + gap_bar)
        cax = fig.add_axes(rect(x_bar, yb, w_bar, 0.08))
        cols = ["#ECEFF3"] + [cmap(i / 7) for i in range(8)]
        cm = mpl.colors.ListedColormap(cols)
        cb = mpl.colorbar.ColorbarBase(
            cax, cmap=cm, norm=mpl.colors.BoundaryNorm(np.r_[-1 / 16, bounds + 1 / 16], cm.N),
            orientation="horizontal", ticks=[0, 0.25, 0.5, 0.75, 1],
        )
        cb.ax.set_xticklabels(["0", "2/8", "4/8", "6/8", "8/8"])
        cb.outline.set_linewidth(0.45); cb.ax.tick_params(labelsize=6.1, length=2, width=0.45)
        cax.set_title(lab, fontsize=6.1, loc="left", pad=2.5, fontweight="normal", color=F.INK)

    agg = lambda key: round(float(np.mean([s[key] for s in stats if s[key] is not None])), 4)
    prov = {
        "inputs": [
            "figures/data/gallery_cases.npz", "figures/data/gallery_cases.json",
            "figures/data/heatmap_engine_seeds.npz", "figures/data/heatmap_engine_seeds.json",
            "paper/figures/fig_gallery.json",
        ],
        "option": "b",
        "option_reason": "Spatial error, engine stochasticity floor, and rollout disagreement over 40x40 crops.",
        "maps": "Per plan, three spatial heatmaps in eighths over desaturated micro-sprite underlay + footprint border.",
        "selection_rule": meta["selection_rule"], "n_plans": len(cases), "cases": stats,
        "mean_over_plans": {
            k: agg(k) for k in (
                "error_mean_map", "floor_mean_map", "disagree_mean_map",
                "error_mean_footprint", "floor_mean_footprint", "disagree_mean_footprint",
                "error_mean_crop", "floor_mean_crop", "disagree_mean_crop",
            )
        },
        "n_plans_with_footprint": int(sum(s["footprint_tiles"] > 0 for s in stats)),
        "n_plans_error_above_floor_footprint": int(
            sum(s["error_mean_footprint"] > s["floor_mean_footprint"] for s in stats if s["footprint_tiles"] > 0)
        ),
        "n_plans_error_above_floor_crop": int(sum(s["error_mean_crop"] > s["floor_mean_crop"] for s in stats)),
        "n_plans_error_above_floor_map": int(sum(s["error_mean_map"] > s["floor_mean_map"] for s in stats)),
        "emulator_samples": meta["K"], "extra_engine_seeds": me["n_extra_seeds"],
        "arrays_sha256": meta["arrays_sha256"], "engine_seeds_sha256": me["arrays_sha256"],
        "figure_size_in": [round(W, 3), round(H, 3)], "map_side_in": round(side, 3),
    }
    F.save(fig, "fig_heatmaps.pdf", prov)


if __name__ == "__main__":
    main()
