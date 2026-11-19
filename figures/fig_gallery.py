"""Figure 2 (fig_gallery.pdf): Procedural micro-sprite gallery of 15 exploited city plans at month 24.

Reads figures/data/gallery_cases.{npz,json}; writes paper/figures/fig_gallery.pdf and its JSON sidecar.
Each pair renders the 40x40-tile region of peak world-model/engine divergence using hpr_fig.render_city
at 8x8 subpixels per tile, pairing the world model's imagined city beside the exact simulator's state
under the identical 24-month plan, with neutral academic typography and zero coloured badges.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

REPO = F.REPO
FAMILIES = ["grow", "solvent", "treasury", "recover", "power"]
PER_FAMILY = 4
CROP = 40
SCALE = 10
WMAP, HMAP = 120, 100


def crop_box(footprint, differ, side=CROP):
    def window_sums(m):
        c = np.zeros((WMAP + 1, HMAP + 1))
        c[1:, 1:] = np.cumsum(np.cumsum(m.astype(float), 0), 1)
        return c[side:, side:] - c[:-side, side:] - c[side:, :-side] + c[:-side, :-side]

    d, f = window_sums(differ), window_sums(footprint)
    xs, ys = np.meshgrid(np.arange(d.shape[0]), np.arange(d.shape[1]), indexing="ij")
    order = np.lexsort((ys.ravel(), xs.ravel(), -f.ravel(), -d.ravel()))
    x0, y0 = int(xs.ravel()[order[0]]), int(ys.ravel()[order[0]])
    return x0, y0, side


def drawn_differently(emu_t, emu_p, eng_t, eng_p):
    ce, cg = F.tile_class(emu_t), F.tile_class(eng_t)
    needs = np.isin(ce, [F.CLASSES.index(n) for n in F.NEEDS_POWER])
    return (ce != cg) | (needs & (emu_p != eng_p))


def load():
    z = np.load(F.DATA / "gallery_cases.npz")
    meta = json.loads((F.DATA / "gallery_cases.json").read_text())
    return z, meta


def pair_maps(z, c):
    t, k = c["tag"], c["shown_sample"]
    emu_t, emu_p = z[f"{t}_emu_tile_index"][k], z[f"{t}_emu_power"][k] > 0
    eng_t, eng_p = z[f"{t}_eng_tiles"] & F.LOMASK, z[f"{t}_eng_power"] > 0
    differ = drawn_differently(emu_t, emu_p, eng_t, eng_p)
    box = crop_box(z[f"{t}_footprint"], differ)
    return (emu_t, emu_p), (eng_t, eng_p), box, differ


def _zone_dev_state(tiles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Classify each tile into (tile_class, zone_development_stage) for divergence highlighting."""
    ti = np.asarray(tiles) & F.LOMASK
    cls = F.tile_class(ti).astype(np.int16)
    dev = np.zeros_like(cls)
    r = cls == F.CLASSES.index("residential")
    dev[r & (ti >= 240) & (ti <= 248)] = 1
    dev[r & (ti >= 249) & (ti <= 260)] = 2
    dev[r & ~((ti >= 240) & (ti <= 260))] = 3
    c = cls == F.CLASSES.index("commercial")
    dev[c & (ti >= 423) & (ti <= 431)] = 1
    dev[c & ~((ti >= 423) & (ti <= 431))] = 3
    ind = cls == F.CLASSES.index("industrial")
    dev[ind & (ti >= 612) & (ti <= 620)] = 1
    dev[ind & ~((ti >= 612) & (ti <= 620))] = 3
    return cls, dev


def visual_divergence(emu_t: np.ndarray, emu_p: np.ndarray, eng_t: np.ndarray, eng_p: np.ndarray) -> np.ndarray:
    """Boolean mask of tiles diverging in tile class, zone development level, or power status."""
    ce, de = _zone_dev_state(emu_t)
    cg, dg = _zone_dev_state(eng_t)
    need_ids = [F.CLASSES.index(n) for n in F.NEEDS_POWER]
    pw_diff = (np.isin(ce, need_ids) | np.isin(cg, need_ids)) & (emu_p != eng_p)
    return (ce != cg) | (de != dg) | pw_diff


def _shift_bool(m: np.ndarray, dy: int, dx: int) -> np.ndarray:
    out = np.zeros_like(m, dtype=bool)
    h, w = m.shape
    y0, y1 = max(0, dy), min(h, h + dy)
    x0, x1 = max(0, dx), min(w, w + dx)
    out[y0:y1, x0:x1] = m[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
    return out


def draw_map(ax, tiles, power, box, div_mask=None):
    x0, y0, s = box
    img = F.render_city(tiles[x0:x0 + s, y0:y0 + s], power[x0:x0 + s, y0:y0 + s], scale=SCALE)
    if div_mask is not None:
        dc = div_mask[x0:x0 + s, y0:y0 + s]
        if dc.any():
            m_up = np.repeat(np.repeat(dc.T.astype(bool), SCALE, axis=0), SCALE, axis=1)
            eroded = (
                m_up
                & _shift_bool(m_up, -1, 0) & _shift_bool(m_up, 1, 0)
                & _shift_bool(m_up, 0, -1) & _shift_bool(m_up, 0, 1)
            )
            dilated = (
                m_up
                | _shift_bool(m_up, -1, 0) | _shift_bool(m_up, 1, 0)
                | _shift_bool(m_up, 0, -1) | _shift_bool(m_up, 0, 1)
            )
            halo = dilated & ~m_up
            stroke = m_up & ~eroded
            img = img.copy()
            img[halo] = 0.58 * np.ones(3, dtype=np.float32) + 0.42 * img[halo]
            img[stroke] = np.array([0.769, 0.231, 0.259], dtype=np.float32)  # F.RED_MID
    ax.imshow(img, interpolation="nearest", extent=(x0 - 0.5, x0 + s - 0.5, y0 + s - 0.5, y0 - 0.5))
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.55); sp.set_color(F.INK)


def off_grid_counts(z, c):
    t, k = c["tag"], c["shown_sample"]
    need = [F.CLASSES.index(n) for n in F.NEEDS_POWER]
    ec, ep = F.tile_class(z[f"{t}_emu_tile_index"]), z[f"{t}_emu_power"] > 0
    gc, gp = F.tile_class(z[f"{t}_eng_tiles"] & F.LOMASK), z[f"{t}_eng_power"] > 0
    off_e = (np.isin(ec, need) & ~ep).sum((1, 2))
    return int(off_e[k]), round(float(off_e.mean()), 2), int((np.isin(gc, need) & ~gp).sum())


def classes_present(z, meta):
    seen = set()
    for c in meta["cases"]:
        (et, ep), (gt, gp), (x0, y0, s), _ = pair_maps(z, c)
        for t in (et, gt):
            seen |= set(np.unique(F.tile_class(t[x0:x0 + s, y0:y0 + s])).tolist())
    return {F.CLASSES[i] for i in seen}


def _swatch(code: int, powered: bool = True, plant: bool = False) -> np.ndarray:
    t = np.full((2, 2), code, dtype=np.int16)
    if plant:
        t = np.array([[745, 746], [753, 754]], dtype=np.int16)
    elif code == 66:
        t = np.array([[66, 150], [76, 66]], dtype=np.int16)
    elif code == 827:
        t = np.array([[440, 827], [442, 445]], dtype=np.int16)
    return F.render_city(t, np.full((2, 2), powered, dtype=bool), scale=8)


def main():
    F.apply()
    z, meta = load()
    by_fam = {f: [c for c in meta["cases"] if c["family"] == f] for f in FAMILIES}

    cases = [c for f in FAMILIES for c in by_fam[f]]
    NC = 4
    n_cells = len(cases) + 1
    NR = int(np.ceil(n_cells / NC))
    W = F.TEXT_IN
    left, right = 0.01, 0.01
    pair_gap, in_gap, head_h, fam_h, under_h, row_gap = 0.15, 0.038, 0.19, 0.165, 0.140, 0.052
    side = (W - left - right - (NC - 1) * pair_gap - NC * in_gap) / (2 * NC)
    row_h = fam_h + side + under_h + row_gap
    H = head_h + NR * row_h - row_gap
    fig = plt.figure(figsize=(W, H))

    def rect(x, y, w, h):
        return [x / W, 1 - (y + h) / H, w / W, h / H]

    for j in range(NC):
        x = left + j * (2 * side + in_gap + pair_gap)
        fig.text((x + side / 2) / W, 1 - (head_h - 0.042) / H, "World model", color=F.INK, fontsize=6.8,
                 fontweight="normal", ha="center", va="bottom")
        fig.text((x + side + in_gap + side / 2) / W, 1 - (head_h - 0.042) / H, "Exact simulator", color=F.INK, fontsize=6.8,
                 fontweight="normal", ha="center", va="bottom")
        # Crisp hairline spanner under each pair's column titles
        hl_ax = fig.add_axes([x / W, 1 - (head_h - 0.014) / H, (2 * side + in_gap) / W, 0.002])
        hl_ax.axis("off")
        hl_ax.axhline(0.5, color="#CCCCCC", lw=0.55)

    crops, differ_in = {}, {}
    letters = "abcdefghijklmnopqrstuvwxyz"
    for n, c in enumerate(cases):
        i, j = divmod(n, NC)
        x = left + j * (2 * side + in_gap + pair_gap)
        y = head_h + i * row_h
        fam_name = F.FAM_LABEL.get(c["family"], c["family"].capitalize())
        case_label = f"{fam_name} {c['rank'] + 1}"

        emu, eng, box, differ = pair_maps(z, c)
        div_mask = visual_divergence(*emu, *eng)
        crops[c["tag"]] = list(map(int, box))
        x0, y0, sd = box
        differ_in[c["tag"]] = (int(differ[x0:x0 + sd, y0:y0 + sd].sum()), int(differ.sum()))
        n_vis_diff = int(div_mask[x0:x0 + sd, y0:y0 + sd].sum())

        yb_txt = 1 - (y + fam_h - 0.050) / H
        fig.text(x / W, yb_txt, letters[n], fontsize=8.0, fontweight="bold", color=F.INK,
                 ha="left", va="baseline")
        fig.text((x + 0.145) / W, yb_txt, case_label, fontsize=6.5,
                 fontweight="normal", color=F.INK, ha="left", va="baseline")
        fig.text((x + 2 * side + in_gap) / W, yb_txt, f"{n_vis_diff} tiles differ",
                 fontsize=5.6, color="#555555", ha="right", va="baseline")

        ax_e = fig.add_axes(rect(x, y + fam_h, side, side))
        draw_map(ax_e, *emu, box, div_mask=div_mask)
        ax_g = fig.add_axes(rect(x + side + in_gap, y + fam_h, side, side))
        draw_map(ax_g, *eng, box, div_mask=div_mask)
        dag = "" if c["shown_sample_passes"] else "$^\\dagger$"
        ax_e.text(0.5, -0.048, f"{c['audit_emulator_passing']}/8 pass{dag}", transform=ax_e.transAxes,
                  ha="center", va="top", fontsize=6.3, color=F.INK)
        ax_g.text(0.5, -0.048, f"{c['audit_oracle_passing']}/32 seeds", transform=ax_g.transAxes,
                  ha="center", va="top", fontsize=6.3, color=F.INK)

    # Cell 16: Two-column Procedural Micro-Sprite Key (unified 1:1 with Fig. 1)
    present = classes_present(z, meta)
    i, j = divmod(len(cases), NC)
    x = left + j * (2 * side + in_gap + pair_gap)
    y = head_h + i * row_h
    leg_ax = fig.add_axes(rect(x, y + fam_h - 0.045, 2 * side + in_gap, side + under_h + 0.045))
    leg_ax.set_xlim(0, 1); leg_ax.set_ylim(0, 1); leg_ax.axis("off")
    leg_ax.text(0.0, 0.99, "Tile key (40 by 40 tile crops)", fontsize=6.8, fontweight="normal", color=F.INK, va="top")

    key_entries = [
        (_swatch(274, True), "Residential"),
        (_swatch(445, True), "Commercial"),
        (_swatch(634, True), "Industrial"),
        (_swatch(765, True), "Civic"),
        (_swatch(745, True, plant=True), "Power plant"),
        (_swatch(66, True), "Road / traffic"),
        (_swatch(208, True), "Power line"),
        (_swatch(226, True), "Rail"),
        (_swatch(4, True), "Water"),
        (_swatch(29, True), "Trees"),
        (_swatch(58, True), "Fire"),
        (_swatch(827, False), "Blackout"),
    ]
    for idx_k, (sw, lbl) in enumerate(key_entries):
        col_i = idx_k // 6
        row_i = idx_k % 6
        xc = 0.01 + col_i * 0.50
        yc = 0.82 - row_i * 0.125
        ins = leg_ax.inset_axes([xc, yc - 0.045, 0.105, 0.098])
        ins.imshow(sw, interpolation="nearest")
        ins.set_xticks([]); ins.set_yticks([])
        for sp in ins.spines.values():
            sp.set_linewidth(0.45); sp.set_color("#2B303A")
        leg_ax.text(xc + 0.13, yc + 0.004, lbl, fontsize=5.95, color=F.INK, va="center")

    # Divergence outline swatch at bottom of Cell 16
    from matplotlib.patches import Rectangle
    leg_ax.add_patch(Rectangle((0.01, 0.015), 0.105, 0.075, facecolor="#EFECE2", edgecolor=F.RED_MID, lw=0.95))
    leg_ax.text(0.14, 0.052, "Diverging zone or power state", fontsize=5.85, color=F.INK, va="center")

    crop_rule_txt = (
        "per pair, the 40 x 40-tile window of the 120 x 100 map that holds the most tiles drawn differently "
        "in the two maps shown; ties go to larger action footprint, then smaller x, then y."
    )
    share_in = [a / b for a, b in differ_in.values() if b > 0]
    off = {c["tag"]: off_grid_counts(z, c) for c in meta["cases"]}
    prov = {
        "inputs": ["figures/data/gallery_cases.npz", "figures/data/gallery_cases.json"],
        "selection_rule": meta["selection_rule"],
        "crop_rule": crop_rule_txt,
        "crop_side_tiles": CROP,
        "n_accepted_but_rejected_total": meta["n_accepted_but_rejected_total"],
        "n_accepted_but_rejected_by_family": meta["n_accepted_but_rejected_by_family"],
        "n_shown_by_family": meta["n_shown_by_family"],
        "n_pairs": len(meta["cases"]),
        "layout": "4 x 4 grid of micro-sprite pairs, sprite key in cell 16",
        "panel_letters": {letters[n]: c["tag"] for n, c in enumerate(cases)},
        "families_with_fewer_than_four": [f for f in FAMILIES if meta["n_shown_by_family"][f] < PER_FAMILY],
        "cases": [
            {
                k: c[k]
                for k in (
                    "family", "rank", "instance", "plan_id", "audit_emulator_passing",
                    "audit_oracle_passing", "audit_oracle_margin", "fresh_emulator_passing",
                    "shown_sample", "shown_sample_passes",
                )
            }
            | {
                "crop": crops[c["tag"]],
                "tiles_drawn_differently_in_crop": differ_in[c["tag"]][0],
                "tiles_drawn_differently_on_map": differ_in[c["tag"]][1],
                "off_grid_tiles_sample_shown": off[c["tag"]][0],
                "off_grid_tiles_sample_mean": off[c["tag"]][1],
                "off_grid_tiles_engine": off[c["tag"]][2],
            }
            for c in meta["cases"]
        ],
        "crop_share_of_differing_tiles_median": round(float(np.median(share_in)), 3),
        "crop_share_of_differing_tiles_min": round(float(np.min(share_in)), 3),
        "fresh_emulator_passing_min": int(min(c["fresh_emulator_passing"] for c in meta["cases"])),
        "fresh_emulator_passing_max": int(max(c["fresh_emulator_passing"] for c in meta["cases"])),
        "n_fresh_emulator_accepts": int(sum(c["fresh_emulator_passing"] >= meta["K"] / 2 for c in meta["cases"])),
        "n_shown_samples_not_passing": int(sum(not c["shown_sample_passes"] for c in meta["cases"])),
        "emulator_samples": meta["K"],
        "oracle_seeds": 32,
        "torch_seed": meta["torch_seed"],
        "tile_classes_in_legend": sorted(present),
        "arrays_sha256": meta["arrays_sha256"],
        "data_code_commit": meta["code_commit"],
        "figure_size_in": [round(W, 3), round(H, 3)],
        "map_side_in": round(side, 3),
    }
    F.save(fig, "fig_gallery.pdf", prov)


if __name__ == "__main__":
    main()
