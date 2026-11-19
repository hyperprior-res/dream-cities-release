"""Figure 3 (fig_pressure.pdf): Scaling optimisation pressure across open-loop search and in-imagination PPO.

Follows Google DeepMind and Nature empirical plotting conventions: pure white canvases, outward-offset
axes, piecewise-linear scaling trajectories across discrete decade budgets with vertical 95% bootstrap
confidence intervals, unsmoothed 200-step (5k-month) PPO learning trajectories across all 360 world-model
runs and engine reference runs, and an explicit panel for initial-plan verdict false acceptance.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

AXIS = F.REPO / "results/analysis/pressure_axis.json"
RLX = F.REPO / "results/analysis/rl_axis.json"
SNAPS = [250_000, 500_000, 1_000_000]


def bca_series(block):
    out = {}
    for r in block["rows"]:
        g = {}
        for who, src in (("emulator", "emulator"), ("perfect_emulator", "perfect")):
            g[who] = {
                "hackability": F.interval(r["false_acceptance"][src]),
                "oracle_accept": F.interval(r["real_success"][src]),
            }
        out[int(r["budget"])] = g
    return out


def tw(x):
    return float(x["value"]), float(x["twoway"]["lo"]), float(x["twoway"]["hi"])


def load_ppo_200step(rlx_doc: dict):
    """Load unsmoothed 200-step (5k..1M months) in-loop pass-rate trajectories for 24 world models and engine PPO."""
    by_ckpt_fam: dict[tuple[str, str], list[np.ndarray]] = {}
    months = None
    for run_name in rlx_doc["runs"]["ladder"]:
        ck, fam, _seed, _ = run_name.split("__")
        p = F.REPO / "results/rl" / run_name / "log.jsonl"
        rows = [json.loads(line) for line in p.read_text().splitlines()]
        if months is None:
            months = np.array([r["months"] for r in rows], dtype=float) / 1e6
        arr = np.array([r["accept_rate_in_loop"] for r in rows], dtype=float)
        by_ckpt_fam.setdefault((ck, fam), []).append(arr)

    ckpts = sorted({ck for ck, _ in by_ckpt_fam})
    fams = ["grow", "solvent", "treasury", "recover", "power"]
    ckpt_curves = []
    for ck in ckpts:
        fam_means = [np.mean(by_ckpt_fam[(ck, f)], axis=0) for f in fams]
        ckpt_curves.append(np.mean(fam_means, axis=0))
    ckpt_curves_arr = np.asarray(ckpt_curves)  # (24, 200)

    eng_fam_means = []
    for f in fams:
        s_runs = []
        for run_name in rlx_doc["runs"]["engine"][f]:
            p = F.REPO / "results/rl" / run_name / "log.jsonl"
            s_runs.append(np.array([json.loads(line)["accept_rate_in_loop"] for line in p.read_text().splitlines()], dtype=float))
        eng_fam_means.append(np.mean(s_runs, axis=0))
    eng_curve = np.mean(eng_fam_means, axis=0)

    mean_lad = ckpt_curves_arr.mean(axis=0)
    se_lad = ckpt_curves_arr.std(axis=0, ddof=1) / np.sqrt(len(ckpts))
    lo_lad = np.clip(mean_lad - 1.96 * se_lad, 0.0, 1.0)
    hi_lad = np.clip(mean_lad + 1.96 * se_lad, 0.0, 1.0)
    return months, ckpt_curves_arr, mean_lad, lo_lad, hi_lad, eng_curve


def draw_discrete_budget(
    ax, xs, vals, color: str, ls, marker: str, mfc: str, lw: float, ms: float, zorder: int, ci_from: int = 0
):
    """Straight segments connecting discrete budgets with crisp vertical 95% CI error bars."""
    xs = np.asarray(xs, dtype=float)
    ys = vals[:, 0]
    los = vals[:, 1]
    his = vals[:, 2]
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=zorder)
    for idx in range(ci_from, len(xs)):
        if his[idx] - los[idx] > 1e-6:
            ax.plot([xs[idx], xs[idx]], [los[idx], his[idx]], color=color, lw=0.65, solid_capstyle="butt", zorder=zorder)
            ax.plot(
                [xs[idx], xs[idx]], [los[idx], his[idx]],
                linestyle="none", marker="_", markersize=2.5, markeredgewidth=0.65, color=color, zorder=zorder,
            )
    ax.plot(
        xs[ci_from:], ys[ci_from:], color=color, lw=0, ls="none", marker=marker, ms=ms,
        mfc=mfc, mec=color, mew=0.85, zorder=zorder + 1,
    )


def main():
    F.apply()
    d = json.loads(AXIS.read_text())
    if d["method"] != "cem_seeded" or d["checkpoint"] != "os_50m_full/samples_006000000":
        raise SystemExit(f"{AXIS}: not the main checkpoint's adaptive search")
    G = {"random": bca_series(d["bca"]["random"]), "cem_seeded": bca_series(d["bca"]["pool_seeded"])}

    fig = plt.figure(figsize=(F.TEXT_IN, 2.86))
    axes = [
        fig.add_axes([0.054, 0.195, 0.180, 0.560]),
        fig.add_axes([0.302, 0.195, 0.180, 0.560]),
        fig.add_axes([0.554, 0.195, 0.172, 0.560]),
        fig.add_axes([0.810, 0.195, 0.132, 0.560]),
    ]
    style = {"random": ("o", "Random shooting"), "cem_seeded": ("s", "Adaptive CEM")}

    for ax, key, title, letter in (
        (axes[0], "hackability", "Search false acceptance", "a"),
        (axes[1], "oracle_accept", "Ground-truth pass rate", "b"),
    ):
        F.decorate_axis(ax, grid="both", wrect=3.0, hrect=3.0)
        for m, (mk, _) in style.items():
            if m == "cem_seeded":
                bs_eval = sorted(G[m])
                xs_perf = [1.0 * (10.0 ** -0.024)] + [b * (10.0 ** -0.068) for b in bs_eval]
                xs_emu = [1.0 * (10.0 ** +0.024)] + [b * (10.0 ** +0.068) for b in bs_eval]
                emu = np.array([G["random"][1]["emulator"][key]] + [G[m][b]["emulator"][key] for b in bs_eval])
                perf = np.array([G["random"][1]["perfect_emulator"][key]] + [G[m][b]["perfect_emulator"][key] for b in bs_eval])
                ci_start = 1
            else:
                bs_all = sorted(G[m])
                xs_perf = [b * (10.0 ** -0.024) for b in bs_all]
                xs_emu = [b * (10.0 ** +0.024) for b in bs_all]
                emu = np.array([G[m][b]["emulator"][key] for b in bs_all])
                perf = np.array([G[m][b]["perfect_emulator"][key] for b in bs_all])
                ci_start = 0

            ce, cp = (F.RED_MID, F.BLUE) if m == "cem_seeded" else (F.RED_LIGHT, F.BLUE_LIGHT)
            lw = 1.40 if m == "cem_seeded" else 1.10
            draw_discrete_budget(ax, xs_perf, perf, cp, (0, (3.2, 1.6)), mk, "#FFFFFF", lw * 0.92, 3.1, 4, ci_from=ci_start)
            draw_discrete_budget(ax, xs_emu, emu, ce, "-", mk, ce, lw, 3.3, 5, ci_from=ci_start)

        F.log_budget_axis(ax, 1, 10_000)
        ax.set_xlabel("Search budget $B$ (plans)", fontsize=6.6)
        F.panel_header(ax, letter, title, pad_pt=6.5, letter_dx_pt=-12.0, gap_pt=9.2)

        if key == "hackability":
            ax.set_ylim(0.0, 0.40)
            ax.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4])
            ax.set_ylabel("Share of core instances", fontsize=6.6, labelpad=2.0)
        else:
            ax.set_ylim(0.0, 0.80)
            ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8])
            ax.set_ylabel("Oracle pass rate (32 seeds)", fontsize=6.6, labelpad=2.0)

    search_handles = [
        Line2D([], [], color=F.RED_MID, marker="s", ms=3.3, mfc=F.RED_MID, lw=1.40, ls="-", label="Adaptive CEM (world model)"),
        Line2D([], [], color=F.BLUE, marker="s", ms=3.2, mfc="#FFFFFF", mec=F.BLUE, mew=0.85, lw=1.25, ls=(0, (3.2, 1.6)), label="Adaptive CEM (exact simulator)"),
        Line2D([], [], color=F.RED_LIGHT, marker="o", ms=3.2, mfc=F.RED_LIGHT, lw=1.10, ls="-", label="Random shooting (world model)"),
        Line2D([], [], color=F.BLUE_LIGHT, marker="o", ms=3.1, mfc="#FFFFFF", mec=F.BLUE_LIGHT, mew=0.85, lw=1.00, ls=(0, (3.2, 1.6)), label="Random shooting (exact simulator)"),
    ]
    F.clean_legend(
        fig, search_handles, loc="upper left", ncol=2, fontsize=6.05,
        bbox_to_anchor=(0.052, 0.992), columnspacing=0.95, labelspacing=0.24,
    )

    # Panel (c): Unsmoothed 200-step PPO curves (Dream vs Oracle vs Engine PPO)
    ax = axes[2]
    F.decorate_axis(ax, grid="both", wrect=3.0, hrect=3.0)
    rlx_doc = json.loads(RLX.read_text())
    R = rlx_doc["results"]
    months_m, ckpt_curves, mean_lad, lo_lad, hi_lad, eng_curve = load_ppo_200step(rlx_doc)

    for ck_c in ckpt_curves:
        ax.plot(months_m, ck_c, color=F.RED_MID, lw=0.35, alpha=0.11, zorder=2)

    ax.fill_between(months_m, lo_lad, hi_lad, color=F.RED_MID, alpha=0.18, lw=0, zorder=4)
    ax.plot(months_m, mean_lad, color=F.RED_MID, lw=1.30, ls="-", zorder=5)
    x_snaps = np.array([0.25, 0.50, 1.00], dtype=float)
    dream_snaps = np.array([tw(R["ladder"][str(s)]["all"]["dream"])[0] for s in SNAPS])
    ax.plot(x_snaps, dream_snaps, color=F.RED_MID, ls="none", marker="o", ms=3.1, mfc=F.RED_MID, zorder=6)

    ax.plot(months_m, eng_curve, color=F.BLUE, lw=1.15, ls="-", alpha=0.95, zorder=4)

    or_t0 = G["random"][1]["emulator"]["oracle_accept"][0]
    x_or = np.array([0.005, 0.25, 0.50, 1.00], dtype=float)
    or_vals = np.array([[or_t0, or_t0, or_t0]] + [list(tw(R["ladder"][str(s)]["all"]["oracle"])) for s in SNAPS])
    draw_discrete_budget(ax, x_or, or_vals, F.RED_MID, (0, (3.2, 1.6)), "o", "#FFFFFF", 1.20, 3.0, 5, ci_from=1)

    gap = np.array([tw(R["ladder"][str(s)]["all"]["gap"]) for s in SNAPS])
    ref = np.array([tw(R["engine"][str(s)]["all"]["gap_ref"]) for s in SNAPS])

    ax.set_xlim(-0.02, 1.04)
    ax.set_xticks([0.0, 0.50, 1.00])
    ax.set_xticklabels(["0", "0.5M", "1M"], fontsize=6.3)
    ax.set_ylim(0.0, 0.60)
    ax.set_yticks([0.0, 0.2, 0.4, 0.6])
    ax.set_xlabel("Training months", fontsize=6.6)
    ax.set_ylabel("Task pass rate", fontsize=6.6, labelpad=2.0)
    F.panel_header(ax, "c", "In-imagination PPO", pad_pt=6.5, letter_dx_pt=-12.0, gap_pt=9.2)

    # Panel (d): Separate vertical bar panel with explicit y-axis for 1M initial-plan false acceptance
    axd = axes[3]
    F.decorate_axis(axd, grid="y", wrect=3.0, hrect=3.0)
    fa = tw(R["ladder"][str(SNAPS[-1])]["all"]["fa0"])
    pf = tw(R["ladder"][str(SNAPS[-1])]["all"]["perfect_fa0"])
    F.draw_vbar_ci(axd, 0.0, fa[0], fa[1], fa[2], color=F.RED_MID, width=0.48)
    F.draw_vbar_ci(axd, 1.0, pf[0], pf[1], pf[2], color=F.BLUE, width=0.48)
    axd.set_xlim(-0.55, 1.55)
    axd.set_xticks([0.0, 1.0])
    axd.set_xticklabels(["World\nmodel", "Exact\nsim."], fontsize=5.9, linespacing=1.02)
    axd.set_ylim(0.0, 0.35)
    axd.set_yticks([0.0, 0.1, 0.2, 0.3])
    axd.set_ylabel("False acceptance rate", fontsize=6.6, labelpad=2.2)
    axd.set_xlabel("1M policy", fontsize=6.6)
    F.panel_header(axd, "d", "Initial-plan false acceptance", pad_pt=6.5, letter_dx_pt=-12.0, gap_pt=9.2, title_size=6.65)

    hs = [
        Line2D([], [], color=F.RED_MID, marker="o", ms=3.0, mfc=F.RED_MID, lw=1.35, label="Dream PPO (imagined)"),
        Line2D([], [], color=F.RED_MID, ls=(0, (3.2, 1.6)), marker="o", ms=2.9, mfc="#FFFFFF", mec=F.RED_MID, mew=0.85, lw=1.15, label="Dream PPO (oracle)"),
        Line2D([], [], color=F.BLUE, lw=1.20, ls="-", label="Engine PPO"),
    ]
    F.clean_legend(
        fig, hs, loc="upper left", ncol=2, fontsize=6.05,
        bbox_to_anchor=(0.538, 0.992), columnspacing=0.90, labelspacing=0.24, handlelength=1.35,
    )

    prov = {
        "inputs": [str(AXIS.relative_to(F.REPO)), str(RLX.relative_to(F.REPO)), "results/rl/*__tasks_v2_H24/log.jsonl"],
        "axis_instances": d["n_instances"],
        "axis_budgets": d["budgets"],
        "interval": d["bca"]["interval"],
        "random_budgets": sorted(G["random"]),
        "adaptive_budgets": sorted(G["cem_seeded"]),
        "rl_ppo_curve_steps": int(len(months_m)),
        "rl_gap": [list(r) for r in gap],
        "rl_gap_reference": [list(r) for r in ref],
        "rl_plan0_false_acceptance": fa,
        "rl_plan0_perfect": pf,
        "n_checkpoint_fan_lines": int(len(ckpt_curves)),
    }
    F.save(fig, "fig_pressure.pdf", prov)


if __name__ == "__main__":
    main()
