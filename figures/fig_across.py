"""Figure 7 (fig_across.pdf): Cross-model predictability of RL exploitation across 24 world models.

Follows Google DeepMind / Nature publication aesthetics: generous inter-panel horizontal breathing
room, Liberation Sans / Helvetica Neue typography, outward-offset 0.55 pt black axes, frameless
legends, shared horizontal header baseline, white-grouted correlation tiles, and plain ASCII signs.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

MC = F.REPO / "results/analysis/main_claim.json"
PC = F.REPO / "results/analysis/pairs.csv"
FAMS = ["grow", "solvent", "treasury", "recover", "power"]
MAIN = "os_50m_full-samples_006000000"
FINAL = {"os": 6000000, "sf": 1500032}
STUB = (
    "Across world models. (a) Search audit false acceptance at B = 10^3 vs. PPO margin inflation.",
    "cross-model analysis (main_claim.json complete)",
    "results/analysis/pairs.csv and results/analysis/main_claim.json",
)


def read_pairs():
    rows = []
    with open(PC) as fh:
        for r in csv.DictReader(fh):
            out = {}
            for k, v in r.items():
                try:
                    out[k] = float(v) if v != "" else float("nan")
                except ValueError:
                    out[k] = v
            rows.append(out)
    return rows


def ci_txt(e):
    f = lambda x: ("+" if x >= 0 else "-") + f"{abs(x):.2f}"
    return f"{f(e['value'])} [{f(e['lo'])}, {f(e['hi'])}]"


def corr_matrix(rows):
    """Compute the 7 x 6 Spearman matrix (Pooled, Within-mean, + 5 families x 6 predictors)."""
    predictors = [
        ("Shoot\n$10^3$", "random_c120_hack_1000", +1.0),
        ("CEM\n$10^3$", "cem_seeded_c40_hack_1000", +1.0),
        ("1-plan\nFA", "random_c120_hack_1", +1.0),
        ("1m\nF1", "fid_test_f1_1m", -1.0),
        ("12m\nF1", "fid_test_f1_since_start_12m", -1.0),
        ("Held-out\nNLL", "fid_test_loglik_elbo", +1.0),
    ]
    row_names = ["Pooled", "Within\nmean"] + [F.FAM_LABEL[f] for f in FAMS]
    mat = np.zeros((len(row_names), len(predictors)), dtype=float)
    for j, (_, col, sgn) in enumerate(predictors):
        valid = [r for r in rows if np.isfinite(r[col]) and np.isfinite(r["rl_inflation_1000000"])]
        x_all = sgn * np.array([r[col] for r in valid])
        y_all = np.array([r["rl_inflation_1000000"] for r in valid])
        mat[0, j] = float(spearmanr(x_all, y_all).statistic)
        wf = []
        for i, f in enumerate(FAMS):
            vf = [r for r in valid if r["family"] == f]
            rho_f = float(spearmanr(
                sgn * np.array([r[col] for r in vf]),
                np.array([r["rl_inflation_1000000"] for r in vf]),
            ).statistic)
            mat[2 + i, j] = rho_f
            wf.append(rho_f)
        mat[1, j] = float(np.mean(wf))
    return mat, row_names, [p[0] for p in predictors]


def draw(d, rows, out_dir, watermark=None):
    F.apply()
    res = d["results"]
    blk = res["main"]["c120"]["rl_inflation_1000000"]

    fig = plt.figure(figsize=(F.TEXT_IN, 3.04))
    # Generous inter-panel horizontal margins with shared 1:1 header baseline y_top
    y_top = 0.785
    axa = fig.add_axes([0.066, 0.175, 0.222, y_top - 0.175])
    axb = fig.add_axes([0.390, 0.295, 0.284, 0.430])
    axc = fig.add_axes([0.790, 0.175, 0.198, y_top - 0.175])

    # Panel (a): 120 checkpoint x family scatter coloured by task family + 5 per-family trend lines
    F.decorate_axis(axa, grid="both", wrect=3.0, hrect=3.0)
    use = [r for r in rows if np.isfinite(r["random_c120_hack_1000"]) and np.isfinite(r["rl_inflation_1000000"])]
    axa.axhline(0.0, color="#666666", lw=0.55, ls=(0, (3.0, 1.8)), zorder=2)

    for fam in FAMS:
        uf = [r for r in use if r["family"] == fam]
        xf = np.array([r["random_c120_hack_1000"] for r in uf])
        yf = np.array([r["rl_inflation_1000000"] for r in uf])
        if len(xf) >= 2 and np.ptp(xf) > 1e-6:
            cf = np.polyfit(xf, yf, 1)
            xg_f = np.linspace(xf.min(), xf.max(), 30)
            axa.plot(xg_f, np.polyval(cf, xg_f), color=F.FAM_COL[fam], lw=0.90, ls="-", alpha=0.75, zorder=3)

    for r in use:
        x, y = r["random_c120_hack_1000"], r["rl_inflation_1000000"]
        seeds = [r[f"rl_inflation_1000000_s{s}"] for s in (0, 1, 2)]
        fam = r["family"]
        fcol = F.FAM_COL[fam]
        is_main = r["checkpoint"] == MAIN
        axa.plot([x, x], [min(seeds), max(seeds)], color=fcol, lw=0.50, alpha=0.34, zorder=3)
        axa.scatter(
            [x], [y], marker=F.FAM_MARK[fam], s=22 if is_main else 13,
            facecolor=fcol, edgecolor="#111111" if is_main else "#FFFFFF",
            linewidth=0.85 if is_main else 0.30, alpha=0.95 if is_main else 0.84,
            zorder=5 if is_main else 4,
        )

    wm = blk["within_mean_spearman"]
    ps = blk["pooled_spearman"]
    txt = (
        f"Within-family $\\bar{{\\rho}}$ = {wm['value']:.2f} [{wm['lo']:.2f}, {wm['hi']:.2f}]\n"
        f"Pooled $\\rho$ = {ps['value']:.2f} [{ps['lo']:.2f}, {ps['hi']:.2f}]"
    )
    axa.text(
        0.03, 0.97, txt, transform=axa.transAxes, fontsize=5.55, va="top", ha="left",
        linespacing=1.20, color=F.INK,
        bbox=dict(boxstyle="square,pad=0.05", facecolor="#FFFFFF", edgecolor="none", alpha=0.90),
    )
    axa.set_xlabel("Search false acceptance ($B = 10^3$)", fontsize=6.6)
    axa.set_ylabel("PPO margin inflation ($10^6$ months)", fontsize=6.6, labelpad=2.5)
    axa.tick_params(labelsize=6.2)
    F.panel_header(axa, "a", "Search audit vs. RL exploitation", pad_pt=6.5, letter_dx_pt=-24.0, gap_pt=10.0, fig_y=y_top)

    fam_handles = [
        Line2D([], [], marker=F.FAM_MARK[f], ms=4.0, color=F.FAM_COL[f], markeredgecolor="#FFFFFF",
                markeredgewidth=0.35, ls="none", label=F.FAM_LABEL[f])
        for f in FAMS
    ]
    fam_handles.append(
        Line2D([], [], marker="o", ms=4.0, color="#FFFFFF", markerfacecolor="#E5E7EB",
               markeredgecolor="#111111", markeredgewidth=0.95, ls="none", label="50M primary")
    )
    F.clean_legend(
        fig, fam_handles, loc="upper left", ncol=6, fontsize=6.15,
        bbox_to_anchor=(0.046, 0.992), handletextpad=0.24, columnspacing=0.95,
    )

    # Panel (b): 7 x 6 Annotated Spearman Rank-Correlation Matrix + compact horizontal colourbar
    mat, rnames, cnames = corr_matrix(rows)
    cmap_div = LinearSegmentedColormap.from_list(
        "hpr_div", ["#0B4F8A", "#CFE3F2", "#F7F8FA", "#F4CECE", "#9E1B22"], N=256
    )
    im_b = axb.imshow(mat, cmap=cmap_div, vmin=-0.90, vmax=0.90, aspect="auto")
    for sp in axb.spines.values():
        sp.set_visible(False)

    axb.set_xticks(np.arange(-0.5, mat.shape[1], 1), minor=True)
    axb.set_yticks(np.arange(-0.5, mat.shape[0], 1), minor=True)
    axb.grid(which="minor", color="#FFFFFF", linestyle="-", linewidth=1.35)
    axb.tick_params(which="minor", bottom=False, left=False)
    axb.plot([-0.5, 5.5], [1.5, 1.5], color="#444444", lw=0.60, zorder=4)
    axb.plot([2.5, 2.5], [-0.5, 6.5], color="#444444", lw=0.60, zorder=4)

    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat[i, j]
            tc = "#FFFFFF" if abs(val) >= 0.68 else F.INK
            s_val = f"-{abs(val):.2f}" if val < -0.005 else f"{abs(val):.2f}"
            axb.text(j, i, s_val, ha="center", va="center", fontsize=5.7, color=tc, fontweight="normal")

    axb.set_xticks(np.arange(len(cnames)))
    axb.set_xticklabels(cnames, fontsize=5.55, linespacing=0.98, fontweight="normal", color=F.INK)
    axb.set_yticks(np.arange(len(rnames)))
    axb.set_yticklabels(rnames, fontsize=6.05, linespacing=0.95, fontweight="normal", color=F.INK)
    axb.tick_params(axis="both", length=0, pad=3.0)
    axb.plot([-0.42, 2.40], [-0.66, -0.66], color=F.INK, lw=0.50, clip_on=False)
    axb.plot([2.60, 5.42], [-0.66, -0.66], color=F.INK, lw=0.50, clip_on=False)
    axb.text(1.0, -0.82, "Verdict audits", fontsize=5.8, fontweight="normal", color=F.INK, ha="center", va="bottom", clip_on=False)
    axb.text(4.0, -0.82, "Trajectory error", fontsize=5.8, fontweight="normal", color=F.INK, ha="center", va="bottom", clip_on=False)
    F.panel_header(axb, "b", "Spearman $\\rho$ with PPO inflation", pad_pt=6.5, letter_dx_pt=-22.0, gap_pt=10.0, fig_y=y_top)

    cax_b = fig.add_axes([0.432, 0.132, 0.200, 0.023])
    cb_b = fig.colorbar(im_b, cax=cax_b, orientation="horizontal", ticks=[-0.9, -0.45, 0.0, 0.45, 0.9])
    cb_b.ax.set_xticklabels(["-0.9", "-0.45", "0.0", "+0.45", "+0.9"], fontsize=5.6)
    cb_b.outline.set_linewidth(0.45)
    cb_b.outline.set_edgecolor(F.INK)
    cb_b.ax.tick_params(length=2.0, width=0.45, pad=1.8)
    cax_b.set_xlabel("Spearman $\\rho$", fontsize=6.2, labelpad=1.8)

    # Panel (c): 1-month changed-tile F1 vs false acceptance across 12 final checkpoints
    F.decorate_axis(axc, grid="both", wrect=3.0, hrect=3.0)
    ckl = res["secondary_d79"]["checkpoint_level_beside_existing"]["fid_test_f1_1m|c120"]
    cks = sorted({r["checkpoint"] for r in rows if int(r["checkpoint"].split("-samples_")[1]) == FINAL[r["checkpoint"][:2]]})
    fx_pts, fy_pts = [], []
    for ck in cks:
        rs = [r for r in rows if r["checkpoint"] == ck]
        n = np.array([r["random_c120_n_1000"] for r in rs])
        h = np.array([r["random_c120_hack_1000"] for r in rs])
        fx = rs[0]["fid_test_f1_1m"]
        if not (np.isfinite(fx) and np.all(np.isfinite(h))):
            continue
        y = float((h * n).sum() / n.sum())
        fx_pts.append(fx)
        fy_pts.append(y)
        one = ck.startswith("os_")
        is_main = ck == MAIN
        fc = F.RED_MID if is_main else (F.DARK_NEUTRAL if one else "#FFFFFF")
        ec = "#111111" if is_main else F.DARK_NEUTRAL
        axc.scatter([fx], [y], s=26 if is_main else 20, facecolor=fc, edgecolor=ec,
                    linewidth=0.85, alpha=0.92, zorder=5 if is_main else 4)

    if len(fx_pts) >= 2:
        cf_c = np.polyfit(fx_pts, fy_pts, 1)
        xg_c = np.linspace(min(fx_pts), max(fx_pts), 30)
        axc.plot(xg_c, np.polyval(cf_c, xg_c), color="#666666", lw=0.75, ls=(0, (3.2, 1.8)), zorder=2)

    axc.set_xlim(0.143, 0.184)
    axc.set_ylim(0.068, 0.302)
    axc.set_xticks([0.15, 0.16, 0.17, 0.18])
    axc.set_yticks([0.10, 0.15, 0.20, 0.25, 0.30])
    axc.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter("%.2f"))
    axc.set_xlabel("1-month changed-tile F1", fontsize=6.6)
    axc.set_ylabel("Search false acceptance ($10^3$)", fontsize=6.6, labelpad=2.5)
    axc.tick_params(labelsize=6.2)
    rho_c = ckl["spearman"]["value"]
    rho_c_str = f"-{abs(rho_c):.2f}" if rho_c < 0 else f"{abs(rho_c):.2f}"
    axc.text(
        0.96, 0.96,
        f"12 final models ($\\rho$ = {rho_c_str})",
        transform=axc.transAxes, fontsize=5.8, va="top", ha="right", color=F.INK,
        bbox=dict(boxstyle="square,pad=0.06", facecolor="#FFFFFF", edgecolor="none", alpha=0.90),
    )
    hc = [
        Line2D([], [], marker="o", ms=3.8, color=F.DARK_NEUTRAL, ls="none", label="One-step"),
        Line2D([], [], marker="o", ms=3.8, color=F.DARK_NEUTRAL, mfc="#FFFFFF", mew=0.90, ls="none", label="Pushforward"),
    ]
    F.clean_legend(axc, hc, loc="lower left", fontsize=5.95, handletextpad=0.25, labelspacing=0.22)
    F.panel_header(axc, "c", "Fidelity vs. exploitability", pad_pt=6.5, letter_dx_pt=-28.0, gap_pt=10.0, fig_y=y_top)

    if watermark:
        fig.text(0.5, 0.5, watermark, fontsize=20, color="#cc0000", alpha=0.35, ha="center", va="center", rotation=12)
    if out_dir is None:
        return F.save(
            fig, "fig_across.pdf",
            {"inputs": [str(MC.relative_to(F.REPO)), str(PC.relative_to(F.REPO))], "status": d["status"], "pairs": len(use)},
        )
    p = Path(out_dir) / "fig_across_LAYOUT_TEST.pdf"
    fig.savefig(p)
    plt.close(fig)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout-test", default=None)
    a = ap.parse_args()
    d = json.loads(MC.read_text())
    done = d["status"] == "complete" and d["results"]["status"] == "complete"
    if a.layout_test:
        if Path(a.layout_test).resolve().is_relative_to(F.REPO / "paper"):
            raise SystemExit("--layout-test must not write under paper/")
        print(draw(d, read_pairs(), a.layout_test, None if done else "LAYOUT TEST"))
        return
    if not done:
        from fig_slots import stub
        stub("fig_across.pdf", *STUB)
        return
    draw(d, read_pairs(), None)


if __name__ == "__main__":
    main()
