"""Shared visual system and procedural Micropolis micro-sprite renderer for Dream Cities.

Empirical figure primitives follow Nature and Google DeepMind house conventions (AlphaTensor,
AlphaDev, SIMA, and DreamerV3): pure white canvases, subtle hairline reference grids, crisp
0.55 pt black axes, solid borderless bar charts anchored at zero with capped black confidence-interval
error bars, frameless legends, metric-matched sans-serif figure typography (Liberation Sans, with
automatic priority hooks for commercial Helvetica Neue LT Std or Google Sans Text), and a
vectorized procedural pixel-art city renderer driven directly by the engine's 10-bit tile codes
(0..1023) and boolean power-grid overlay.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAPER_FIG = REPO / "paper" / "figures"
DATA = REPO / "figures" / "data"
os.environ.setdefault("MPLCONFIGDIR", str(REPO / ".build-cache" / "matplotlib"))
os.environ.setdefault("MPLBACKEND", "Agg")
sys.path.insert(0, str(REPO / "template"))

import numpy as np  # noqa: E402
import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from figure_style import apply as _apply, save as _save, COLUMN_IN, TEXT_IN, RED, BLUE, INK, GREY, PALE  # noqa: E402,F401

# Core role colours and Okabe-Ito / rliable colorblind-safe scientific palette
INK = "#000000"
RED = "#8E1B1E"
RED_MID = "#C43B42"
RED_PALE = "#F2D5D7"
RED_LIGHT = "#E39498"
BLUE = "#4C72B0"
BLUE_MID = "#4C72B0"
BLUE_PALE = "#DCE6F4"
BLUE_LIGHT = "#8CA8D4"
PETROL = "#264653"
PETROL_MID = "#3D6B7D"
PETROL_LIGHT = "#6E95A4"
DARK_NEUTRAL = "#3B4252"
GREY_PALE = "#E6E6E6"
SLATE = "#444444"
MUTED = "#666666"
RULE = "#D0D0D0"
GRID = "#EBEBEB"
CANVAS = "#FFFFFF"
CANVAS_AGG = "#F7F7F7"
LEARNER = "#7C6F5B"
TEAL = "#009E73"
AMBER = "#E69F00"
GOLD = "#F5C518"
PLUM = "#CC79A7"
VERMILION = "#D55E00"

# Colourblind-safe 5-task-family palette, shapes, and display names (reserved strictly for task families)
FAM_COL = {
    "grow": "#009E73",
    "solvent": "#CC79A7",
    "treasury": "#56B4E9",
    "recover": "#D55E00",
    "power": "#E69F00",
}
FAM_MARK = {
    "grow": "o",
    "solvent": "s",
    "treasury": "D",
    "recover": "^",
    "power": "P",
}
FAM_LABEL = {
    "grow": "Grow",
    "solvent": "Solvent",
    "treasury": "Treasury",
    "recover": "Recover",
    "power": "Power",
}


def _register_sans() -> str:
    """Register commercial Helvetica Neue / Google Sans Text if present in figures/fonts/ or ext/fonts/, else Liberation Sans."""
    import logging
    from matplotlib import font_manager
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

    font_dirs = [REPO / "figures" / "fonts", REPO / "ext" / "fonts"]
    candidates = []
    for local_dir in font_dirs:
        candidates.extend([
            ("Helvetica Neue LT Std", [
                (local_dir / "HelveticaNeueLTStd-Roman.ttf", "normal", 400),
                (local_dir / "HelveticaNeueLTStd-Bd.ttf", "normal", 700),
                (local_dir / "HelveticaNeueLTStd-It.ttf", "italic", 400),
                (local_dir / "HelveticaNeueLTStd-BdIt.ttf", "italic", 700),
            ]),
            ("Google Sans Text", [
                (local_dir / "GoogleSansText-Regular.ttf", "normal", 400),
                (local_dir / "GoogleSansText-Bold.ttf", "normal", 700),
                (local_dir / "GoogleSansText-Italic.ttf", "italic", 400),
                (local_dir / "GoogleSansText-BoldItalic.ttf", "italic", 700),
            ]),
        ])
    candidates.append(
        ("Liberation Sans", [
            (Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"), "normal", 400),
            (Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"), "normal", 700),
            (Path("/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"), "italic", 400),
            (Path("/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"), "italic", 700),
        ]),
    )
    for fam_name, faces in candidates:
        if all(p.exists() for p, _, _ in faces):
            font_manager.fontManager.ttflist = [
                f for f in font_manager.fontManager.ttflist if f.name != fam_name
            ]
            for fpath, style, weight in faces:
                font_manager.fontManager.addfont(str(fpath))
                font_manager.fontManager.ttflist.insert(
                    0, font_manager.FontEntry(fname=str(fpath), name=fam_name, style=style, weight=weight)
                )
            if hasattr(font_manager.fontManager, "_findfont_cached"):
                font_manager.fontManager._findfont_cached.cache_clear()
            return fam_name
    return "DejaVu Sans"


def apply():
    _apply()
    sans = _register_sans()
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["ps.fonttype"] = 42
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["svg.hashsalt"] = "hyperprior-dream-cities"
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.sans-serif"] = [sans, "Liberation Sans", "DejaVu Sans"]
    mpl.rcParams["font.size"] = 6.7
    mpl.rcParams["text.color"] = INK
    mpl.rcParams["mathtext.fontset"] = "custom"
    mpl.rcParams["mathtext.rm"] = sans
    mpl.rcParams["mathtext.it"] = f"{sans}:italic"
    mpl.rcParams["mathtext.bf"] = f"{sans}:bold"
    mpl.rcParams["mathtext.sf"] = sans
    mpl.rcParams["mathtext.cal"] = f"{sans}:italic"
    mpl.rcParams["mathtext.tt"] = sans
    mpl.rcParams["mathtext.fallback"] = "stixsans"
    mpl.rcParams["axes.facecolor"] = CANVAS
    mpl.rcParams["axes.titlelocation"] = "left"
    mpl.rcParams["axes.titleweight"] = "normal"
    mpl.rcParams["axes.titlesize"] = 7.0
    mpl.rcParams["axes.labelsize"] = 6.7
    mpl.rcParams["axes.labelcolor"] = INK
    mpl.rcParams["axes.titlepad"] = 5.5
    mpl.rcParams["axes.edgecolor"] = INK
    mpl.rcParams["axes.linewidth"] = 0.55
    mpl.rcParams["xtick.labelsize"] = 6.3
    mpl.rcParams["ytick.labelsize"] = 6.3
    mpl.rcParams["xtick.color"] = INK
    mpl.rcParams["ytick.color"] = INK
    mpl.rcParams["xtick.major.size"] = 2.4
    mpl.rcParams["ytick.major.size"] = 2.4
    mpl.rcParams["xtick.major.width"] = 0.55
    mpl.rcParams["ytick.major.width"] = 0.55
    mpl.rcParams["xtick.major.pad"] = 2.3
    mpl.rcParams["ytick.major.pad"] = 2.3
    mpl.rcParams["legend.fontsize"] = 6.3
    mpl.rcParams["legend.frameon"] = False


def decorate_axis(ax, grid: str = "both", wrect: float = 3.0, hrect: float = 3.0, darker: bool = False):
    """Nature / rliable axis decoration: open top/right spines, crisp 0.55pt black spines, subtle hairline grid."""
    ax.set_facecolor(CANVAS_AGG if darker else CANVAS)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["bottom"].set_visible(True)
    ax.spines["left"].set_color(INK)
    ax.spines["bottom"].set_color(INK)
    ax.spines["left"].set_linewidth(0.55)
    ax.spines["bottom"].set_linewidth(0.55)
    if hrect:
        ax.spines["left"].set_position(("outward", hrect))
    if wrect:
        ax.spines["bottom"].set_position(("outward", wrect))
    ax.grid(False)
    gcol = "#DFDFDF" if darker else GRID
    if grid in ("both", "x"):
        ax.xaxis.grid(True, color=gcol, linewidth=0.45, linestyle="-", zorder=0)
    if grid in ("both", "y"):
        ax.yaxis.grid(True, color=gcol, linewidth=0.45, linestyle="-", zorder=0)
    ax.set_axisbelow(True)
    return ax


def decorate_interval_axis(ax, wrect: float = 3.5, darker: bool = False):
    """rliable.plot_interval_estimates axis decoration: no left/top/right spine, crisp 0.55pt black bottom spine."""
    ax.set_facecolor(CANVAS_AGG if darker else CANVAS)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_linewidth(0.55)
    if wrect:
        ax.spines["bottom"].set_position(("outward", wrect))
    ax.grid(False)
    gcol = "#DFDFDF" if darker else "#EBEBEB"
    ax.xaxis.grid(True, color=gcol, linewidth=0.45, linestyle="-", zorder=0)
    ax.tick_params(axis="y", length=0)
    ax.set_axisbelow(True)
    return ax


def style_panel(ax, grid: str = "both", canvas: str = CANVAS, wrect: float = 3.0, hrect: float = 3.0):
    """Backward-compatible wrapper delegating to DeepMind / rliable axis decoration."""
    if grid == "x":
        return decorate_interval_axis(ax, wrect=wrect, darker=(canvas != CANVAS))
    return decorate_axis(ax, grid=grid, wrect=wrect, hrect=hrect, darker=(canvas != CANVAS))


def draw_interval_bar(
    ax,
    y: float,
    est: float,
    lo: float,
    hi: float,
    color: str,
    height: float = 0.22,
    alpha: float = 0.72,
    tick_color: str | None = None,
    tick_lw: float = 1.35,
    min_span: float = 0.008,
    outline: bool = False,
    zorder: int = 3,
):
    """rliable.plot_interval_estimates primitive: floating [lo, hi] bootstrap interval bar + vertical point-estimate tick."""
    span = max(float(hi) - float(lo), min_span)
    left = float(lo) if (float(hi) - float(lo)) >= min_span else float(est) - 0.5 * min_span
    ax.barh(
        y=y,
        width=span,
        height=height,
        left=left,
        color=color,
        alpha=alpha,
        edgecolor=color if outline else "none",
        linewidth=0.65 if outline else 0.0,
        zorder=zorder,
    )
    tcol = tick_color if tick_color is not None else "#14171D"
    ax.vlines(
        x=float(est),
        ymin=y - height * 0.50,
        ymax=y + height * 0.50,
        color=tcol,
        linewidth=tick_lw,
        zorder=zorder + 2,
    )


def draw_curve(
    ax,
    xs,
    ys,
    lo=None,
    hi=None,
    color: str = RED,
    alpha: float = 0.17,
    ls: str | tuple = "-",
    marker: str | None = "o",
    mfc: str | None = None,
    lw: float = 1.55,
    ms: float = 3.6,
    zorder: int = 4,
    label: str | None = None,
):
    """DreamerV3.curve + rliable.plot_sample_efficiency_curve: borderless CI ribbon + crisp trajectory + clean markers."""
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if lo is not None and hi is not None:
        ax.fill_between(xs, np.asarray(lo, float), np.asarray(hi, float), color=color, alpha=alpha, lw=0, zorder=zorder - 1)
    ax.plot(
        xs, ys, color=color, lw=lw, ls=ls, marker=marker, ms=ms,
        mfc=mfc if mfc is not None else color, mec=color, mew=0.85,
        zorder=zorder, label=label,
    )


class _IntervalPill:
    def __init__(self, color: str, alpha: float, tick_color: str, outline: bool, label: str):
        self.color = color
        self.alpha = alpha
        self.tick_color = tick_color
        self.outline = outline
        self._label = label

    def get_label(self) -> str:
        return self._label


class _IntervalPillHandler(mpl.legend_handler.HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        from matplotlib.patches import Rectangle
        from matplotlib.lines import Line2D
        bh = height * 0.68
        y0 = ydescent + 0.5 * (height - bh)
        rect = Rectangle(
            (xdescent, y0), width, bh,
            facecolor=mpl.colors.to_rgba(orig_handle.color, orig_handle.alpha),
            edgecolor=orig_handle.color if orig_handle.outline else "none",
            linewidth=0.6 if orig_handle.outline else 0.0,
            transform=trans,
        )
        xc = xdescent + 0.5 * width
        tick = Line2D(
            [xc, xc], [y0 - 0.16 * bh, y0 + 1.16 * bh],
            color=orig_handle.tick_color, linewidth=1.25, transform=trans,
        )
        return [rect, tick]


def decorate_bar_axis(ax, zero_spine: bool = True, wrect: float = 3.2, darker: bool = False):
    """Nature / SIMA solid-bar axis: crisp 0.55pt black zero baseline, outward bottom spine, subtle grid."""
    ax.set_facecolor(CANVAS_AGG if darker else CANVAS)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_linewidth(0.55)
    if wrect:
        ax.spines["bottom"].set_position(("outward", wrect))
    if zero_spine:
        ax.spines["left"].set_visible(True)
        ax.spines["left"].set_color(INK)
        ax.spines["left"].set_linewidth(0.55)
        ax.spines["left"].set_position(("data", 0.0))
    else:
        ax.spines["left"].set_visible(False)
        ax.axvline(0.0, color=INK, lw=0.55, zorder=4)
    ax.grid(False)
    gcol = "#DFDFDF" if darker else "#EBEBEB"
    ax.xaxis.grid(True, color=gcol, linewidth=0.45, linestyle="-", zorder=0)
    ax.tick_params(axis="y", length=0)
    ax.set_axisbelow(True)
    return ax


def draw_hbar_ci(
    ax,
    y: float,
    est: float,
    lo: float | None = None,
    hi: float | None = None,
    color: str = RED_MID,
    height: float = 0.20,
    alpha: float = 1.0,
    edgecolor: str = "none",
    edge_lw: float = 0.0,
    ci_color: str = "#1A1A1A",
    ci_lw: float = 0.55,
    cap_pt: float = 2.5,
    zorder: int = 3,
):
    """Nature / Google DeepMind solid borderless horizontal bar + crisp capped CI error bar."""
    v = float(est)
    if abs(v) > 1e-6:
        ax.barh(
            y=y,
            width=v,
            height=height,
            left=0.0,
            color=color,
            alpha=alpha,
            edgecolor="none",
            linewidth=0.0,
            zorder=zorder,
        )
    elif lo is not None and hi is not None and (float(hi) - float(lo)) > 1e-6:
        # Subtle zero-baseline colour stub so zero-valued series remain identifiable
        ax.plot([0.0, 0.0], [y - 0.42 * height, y + 0.42 * height], color=color, lw=1.35, solid_capstyle="butt", zorder=zorder + 1)
    if lo is not None and hi is not None and (float(hi) - float(lo)) > 1e-6:
        lo_v, hi_v = float(lo), float(hi)
        ax.plot(
            [lo_v, hi_v],
            [y, y],
            color=ci_color,
            linewidth=ci_lw,
            solid_capstyle="butt",
            zorder=zorder + 2,
        )
        caps = [c for c in (lo_v, hi_v) if abs(c) > 1e-6 or abs(v) > 1e-6]
        if caps:
            ax.plot(
                caps,
                [y] * len(caps),
                linestyle="none",
                marker="|",
                markersize=cap_pt,
                markeredgewidth=ci_lw,
                color=ci_color,
                zorder=zorder + 2,
            )


def draw_vbar_ci(
    ax,
    x: float,
    est: float,
    lo: float | None = None,
    hi: float | None = None,
    color: str = RED_MID,
    width: float = 0.068,
    alpha: float = 1.0,
    edgecolor: str = "none",
    edge_lw: float = 0.0,
    ci_color: str = "#1A1A1A",
    ci_lw: float = 0.55,
    cap_pt: float = 2.5,
    zorder: int = 4,
):
    """Nature / Google DeepMind solid borderless vertical bar + crisp capped CI error bar."""
    v = float(est)
    if abs(v) > 1e-6:
        ax.bar(
            x=x,
            height=v,
            bottom=0.0,
            width=width,
            color=color,
            alpha=alpha,
            edgecolor="none",
            linewidth=0.0,
            zorder=zorder,
        )
    if lo is not None and hi is not None and (float(hi) - float(lo)) > 1e-6:
        lo_v, hi_v = float(lo), float(hi)
        ax.plot(
            [x, x],
            [lo_v, hi_v],
            color=ci_color,
            linewidth=ci_lw,
            solid_capstyle="butt",
            zorder=zorder + 2,
        )
        caps = [c for c in (lo_v, hi_v) if abs(c) > 1e-6 or abs(v) > 1e-6]
        if caps:
            ax.plot(
                [x] * len(caps),
                caps,
                linestyle="none",
                marker="_",
                markersize=cap_pt,
                markeredgewidth=ci_lw,
                color=ci_color,
                zorder=zorder + 2,
            )


class _BarSwatch:
    def __init__(self, color: str, edgecolor: str = "none", edge_lw: float = 0.0, label: str = ""):
        self.color = color
        self.edgecolor = edgecolor
        self.edge_lw = edge_lw
        self._label = label

    def get_label(self) -> str:
        return self._label


class _BarSwatchHandler(mpl.legend_handler.HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        from matplotlib.patches import Rectangle
        bh = height * 0.68
        bw = width * 0.86
        x0 = xdescent + 0.5 * (width - bw)
        y0 = ydescent + 0.5 * (height - bh)
        rect = Rectangle(
            (x0, y0), bw, bh,
            facecolor=orig_handle.color,
            edgecolor=orig_handle.edgecolor,
            linewidth=orig_handle.edge_lw,
            transform=trans,
        )
        return [rect]


def bar_legend_handle(color: str, edgecolor: str = "none", edge_lw: float = 0.0, label: str = ""):
    """Crisp rectangular swatch legend proxy matching solid Nature / DeepMind bar charts."""
    return _BarSwatch(color=color, edgecolor=edgecolor, edge_lw=edge_lw, label=label)


class _BandLineSwatch:
    def __init__(self, band_color: str = "#E6E8EB", line_color: str = "#444444", label: str = ""):
        self.band_color = band_color
        self.line_color = line_color
        self._label = label

    def get_label(self) -> str:
        return self._label


class _BandLineSwatchHandler(mpl.legend_handler.HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        from matplotlib.patches import Rectangle
        from matplotlib.lines import Line2D
        bh = height * 0.72
        bw = width * 0.86
        x0 = xdescent + 0.5 * (width - bw)
        y0 = ydescent + 0.5 * (height - bh)
        rect = Rectangle(
            (x0, y0), bw, bh,
            facecolor=orig_handle.band_color,
            edgecolor="none",
            linewidth=0.0,
            transform=trans,
        )
        xc = x0 + 0.5 * bw
        line = Line2D(
            [xc, xc], [y0 - 0.12 * bh, y0 + 1.12 * bh],
            color=orig_handle.line_color, linewidth=0.65, linestyle=(0, (2.2, 1.4)), transform=trans,
        )
        return [rect, line]


def band_line_legend_handle(band_color: str = "#E6E8EB", line_color: str = "#444444", label: str = ""):
    """Legend proxy matching a vertical CI band bisected by a dashed reference line."""
    return _BandLineSwatch(band_color=band_color, line_color=line_color, label=label)


def clean_legend(target, handles, labels=None, **kwargs):
    """Frameless publication legend supporting solid BarSwatch and legacy IntervalPill handles."""
    hmap = dict(kwargs.pop("handler_map", {}) or {})
    hmap[_IntervalPill] = _IntervalPillHandler()
    hmap[_BarSwatch] = _BarSwatchHandler()
    hmap[_BandLineSwatch] = _BandLineSwatchHandler()
    opts = dict(
        frameon=False, handlelength=1.35, handletextpad=0.40,
        columnspacing=1.05, borderaxespad=0.0, handler_map=hmap,
    )
    opts.update(kwargs)
    if labels is not None:
        return target.legend(handles, labels, **opts)
    return target.legend(handles=handles, **opts)


def interval_legend_handle(
    color: str, alpha: float = 0.72, tick_color: str = "#14171D", outline: bool = False, label: str = ""
):
    """Legend proxy matching rliable's translucent interval pill + vertical point-estimate tick."""
    return _IntervalPill(color=color, alpha=alpha, tick_color=tick_color, outline=outline, label=label)


def save(fig, name: str, provenance: dict | None = None):
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    path = PAPER_FIG / name
    _save(fig, path)
    if provenance is not None:
        provenance = dict(provenance)
        provenance["figure"] = name
        path.with_suffix(".json").write_text(json.dumps(provenance, indent=1, sort_keys=True) + "\n")
    plt.close(fig)
    return path


def panel_label(ax, letter, x=-0.03, y=1.035, **kw):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=8.0, fontweight="bold", color=INK,
            ha="right", va="bottom", **kw)


def panel_header(
    ax,
    letter: str,
    title: str,
    pad_pt: float = 6.0,
    letter_dx_pt: float = -10.5,
    gap_pt: float = 11.2,
    fig_y: float | None = None,
    title_size: float = 7.0,
    letter_size: float = 8.0,
):
    """Nature house standard: 8 pt bold lowercase panel letter + 7 pt regular panel title on shared baseline."""
    fig = ax.figure
    if fig_y is not None:
        pos = ax.get_position()
        y_ax = (fig_y - pos.y0) / pos.height
    else:
        y_ax = 1.0
    t_let = ax.transAxes + mpl.transforms.ScaledTranslation(letter_dx_pt / 72.0, pad_pt / 72.0, fig.dpi_scale_trans)
    t_tit = ax.transAxes + mpl.transforms.ScaledTranslation((letter_dx_pt + gap_pt) / 72.0, pad_pt / 72.0, fig.dpi_scale_trans)
    ax.text(0.0, y_ax, letter, transform=t_let, fontsize=letter_size, fontweight="bold",
            color=INK, ha="left", va="baseline", clip_on=False)
    ax.text(0.0, y_ax, title, transform=t_tit, fontsize=title_size, fontweight="normal",
            color=INK, ha="left", va="baseline", clip_on=False)


def log_budget_axis(ax, lo=1, hi=10_000):
    ax.set_xscale("log")
    ax.set_xlim(lo / 1.45, hi * 1.45)
    ticks = [b for b in (1, 10, 100, 1000, 10_000) if lo <= b <= hi]
    ax.set_xticks(ticks)
    ax.set_xticklabels([r"$10^{%d}$" % int(round(np.log10(t))) for t in ticks])
    ax.xaxis.set_minor_locator(mpl.ticker.NullLocator())


def interval(d: dict):
    """(value, lo, hi) of an hpr_dream estimate: BCa limits where defined, else stored limits."""
    lo = d.get("bca_lo", d.get("lo"))
    hi = d.get("bca_hi", d.get("hi"))
    return float(d["value"]), float(lo), float(hi)


# ------------------------------------------------------------------------------------------------
# Procedural Micro-Sprite City Renderer (driven by 10-bit Micropolis tile codes)
# ------------------------------------------------------------------------------------------------
LOMASK = 0x03FF
CLASSES = [
    "land", "water", "trees", "road", "rail", "wire",
    "residential", "commercial", "industrial", "civic", "plant", "rubble", "fire",
]
LIT = {
    "land": "#EFECE2",
    "water": "#6FA8DC",
    "trees": "#4E8C57",
    "road": "#4A4F58",
    "rail": "#5A4A3A",
    "wire": "#C87D28",
    "residential": "#D97B59",
    "commercial": "#357ABD",
    "industrial": "#C68B2C",
    "civic": "#7D669E",
    "plant": "#1C2026",
    "rubble": "#959A9E",
    "fire": "#E65518",
}
UNLIT = {
    "residential": "#525A68",
    "commercial": "#434B59",
    "industrial": "#4C5360",
    "civic": "#3F4652",
}
NEEDS_POWER = ("residential", "commercial", "industrial", "civic")


def tile_class(idx: np.ndarray) -> np.ndarray:
    """Engine tile index (0..1023) -> integer class (position in CLASSES)."""
    i = np.asarray(idx) & LOMASK
    c = np.zeros(i.shape, dtype=np.int8)

    def put(lo, hi, name):
        c[(i >= lo) & (i <= hi)] = CLASSES.index(name)

    put(2, 20, "water"); put(48, 51, "water")
    put(21, 43, "trees"); put(840, 843, "trees")
    put(44, 47, "rubble"); put(52, 55, "rubble"); put(860, 867, "rubble")
    put(56, 63, "fire")
    put(64, 206, "road"); put(828, 831, "road"); put(948, 951, "road")
    put(207, 222, "wire")
    put(223, 238, "rail")
    put(240, 422, "residential"); put(956, 1023, "residential")
    put(423, 611, "commercial")
    put(612, 692, "industrial"); put(844, 859, "industrial"); put(868, 915, "industrial")
    put(693, 744, "civic"); put(761, 810, "civic"); put(832, 839, "civic"); put(932, 947, "civic")
    put(745, 760, "plant"); put(811, 826, "plant"); put(916, 931, "plant"); put(952, 955, "plant")
    put(827, 827, "residential")
    return c


def _rgb(hexcol: str) -> np.ndarray:
    return np.array(mpl.colors.to_rgb(hexcol), dtype=np.float32)


def _shift_mask(m: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """Boolean neighbor mask shifted by (dy, dx) with edge replication."""
    out = np.zeros_like(m, dtype=bool)
    H, W = m.shape
    y0, y1 = max(0, dy), min(H, H + dy)
    x0, x1 = max(0, dx), min(W, W + dx)
    out[y0:y1, x0:x1] = m[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
    return out


def render_city(tile_index: np.ndarray, powered: np.ndarray, scale: int = 8) -> np.ndarray:
    """Synthesize a crisp procedural pixel-art city map from (W, H) tile indices and power grid.

    Uses at least 8x8 subpixels per tile so road carriageways, twin rails, copper power pylons,
    pitched residential roofs, glass commercial towers, sawtooth factories, 4x4 coal/nuclear
    plants, active fires, and amber blackout lightning-bolt badges resolve cleanly in print.
    """
    S = max(8, int(scale))
    ti = (np.asarray(tile_index) & LOMASK).T   # (H, W): rows = y, cols = x
    cls = tile_class(tile_index).T             # (H, W)
    pw = np.asarray(powered).astype(bool).T    # (H, W)
    H, W = cls.shape

    # Upsampled coordinate grids: ty, tx = tile indices; uy, ux = subpixel 0..S-1 inside tile
    yy, xx = np.mgrid[0:H * S, 0:W * S]
    ty, tx = yy // S, xx // S
    uy, ux = yy % S, xx % S

    T_cls = cls[ty, tx]
    T_idx = ti[ty, tx]
    T_pw = pw[ty, tx]

    def cid(name: str) -> int:
        return CLASSES.index(name)

    img = np.empty((H * S, W * S, 3), dtype=np.float32)
    # 1. Base parchment-turf terrain with subtle organic stipple
    img[:] = _rgb("#F1EFE6")
    stipple = ((ty * 7 + tx * 13 + uy * 3 + ux * 5) % 17 == 0) & (uy > 0) & (ux > 0)
    img[stipple] = _rgb("#E5E1D4")

    # 2. Water with coastal sand bank & wave crests
    m_water = cls == cid("water")
    coast = m_water & (~_shift_mask(m_water, -1, 0) | ~_shift_mask(m_water, 1, 0)
                       | ~_shift_mask(m_water, 0, -1) | ~_shift_mask(m_water, 0, 1))
    W_water = T_cls == cid("water")
    img[W_water] = _rgb("#6BAED6")
    deep = W_water & ~coast[ty, tx] & (((uy + ty * S) % 4) < 2)
    img[deep] = _rgb("#5398C6")
    wave = W_water & ((uy == S // 3) & ((ux + tx * 2) % 5 < 3))
    img[wave] = _rgb("#B5D8EE")
    bank = W_water & coast[ty, tx] & ((uy == 0) | (uy == S - 1) | (ux == 0) | (ux == S - 1))
    img[bank] = _rgb("#D8CCA8")

    # 3. Woods / park canopy sprites
    W_tree = T_cls == cid("trees")
    img[W_tree] = _rgb("#DDE8D3")
    cx, cy = S / 2.0 - 0.5, S / 2.0 - 0.5
    r2 = (ux - cx) ** 2 + (uy - cy) ** 2
    crown = W_tree & (r2 <= (0.37 * S) ** 2)
    crown_hi = W_tree & ((ux - cx + 0.8) ** 2 + (uy - cy + 0.8) ** 2 <= (0.22 * S) ** 2)
    trunk = W_tree & (np.abs(ux - cx) <= 0.7) & (uy >= S - 2)
    img[crown] = _rgb("#3B7A4B")
    img[crown_hi] = _rgb("#589E67")
    img[trunk] = _rgb("#5A422E")

    # 4. Connected Road network + lane markings + live traffic specks
    m_road = (cls == cid("road")) | (ti == 237) | (ti == 238)
    rn = _shift_mask(m_road, -1, 0)[ty, tx]
    rs = _shift_mask(m_road, 1, 0)[ty, tx]
    rw = _shift_mask(m_road, 0, -1)[ty, tx]
    re_ = _shift_mask(m_road, 0, 1)[ty, tx]
    lo_b, hi_b = S // 5, S - 1 - S // 5
    mid = S // 2
    W_road = T_cls == cid("road")
    in_c = (ux >= lo_b) & (ux <= hi_b) & (uy >= lo_b) & (uy <= hi_b)
    arm_n = rn & (ux >= lo_b) & (ux <= hi_b) & (uy < lo_b)
    arm_s = rs & (ux >= lo_b) & (ux <= hi_b) & (uy > hi_b)
    arm_w = rw & (uy >= lo_b) & (uy <= hi_b) & (ux < lo_b)
    arm_e = re_ & (uy >= lo_b) & (uy <= hi_b) & (ux > hi_b)
    iso = ~(rn | rs | rw | re_) & ((ux >= lo_b) & (ux <= hi_b) | (uy >= lo_b) & (uy <= hi_b))
    pave = W_road & (in_c | arm_n | arm_s | arm_w | arm_e | iso)
    img[W_road] = _rgb("#D7D5CC")
    img[pave] = _rgb("#454A54")
    dash_v = pave & (rn | rs) & (ux == mid) & (uy % 3 == 1)
    dash_h = pave & (rw | re_) & (uy == mid) & (ux % 3 == 1)
    img[dash_v | dash_h] = _rgb("#E9D778")
    # Traffic vehicles on low/high traffic tiles (80..206)
    trf = pave & (T_idx >= 80) & (T_idx <= 206)
    car1 = trf & (ux == mid - 1) & (uy == mid - 1)
    car2 = trf & (T_idx >= 144) & (ux == mid + 1) & (uy == mid + 1)
    img[car1] = _rgb("#F5B041")
    img[car2] = _rgb("#EC7063")

    # 5. Connected Twin-Rail network
    m_rail = cls == cid("rail")
    qn = _shift_mask(m_rail, -1, 0)[ty, tx]
    qs = _shift_mask(m_rail, 1, 0)[ty, tx]
    qw = _shift_mask(m_rail, 0, -1)[ty, tx]
    qe = _shift_mask(m_rail, 0, 1)[ty, tx]
    W_rail = T_cls == cid("rail")
    img[W_rail] = _rgb("#CFCBC0")
    bed_v = W_rail & (qn | qs | ~(qw | qe)) & (ux >= lo_b) & (ux <= hi_b)
    bed_h = W_rail & (qw | qe) & (uy >= lo_b) & (uy <= hi_b)
    img[bed_v | bed_h] = _rgb("#6E5B49")
    rails_v = bed_v & ((ux == lo_b + 1) | (ux == hi_b - 1))
    rails_h = bed_h & ((uy == lo_b + 1) | (uy == hi_b - 1))
    img[rails_v | rails_h] = _rgb("#D5D8DC")

    # 6. Connected Power Transmission Lines + Pylons
    m_wire = (cls == cid("wire")) | (cls == cid("plant")) | np.isin(cls, [cid(n) for n in NEEDS_POWER])
    wn = _shift_mask(m_wire, -1, 0)[ty, tx]
    ws = _shift_mask(m_wire, 1, 0)[ty, tx]
    ww = _shift_mask(m_wire, 0, -1)[ty, tx]
    we = _shift_mask(m_wire, 0, 1)[ty, tx]
    W_wire = T_cls == cid("wire")
    w_v = W_wire & (wn | ws | ~(ww | we)) & ((ux == mid - 1) | (ux == mid)) & ((wn & (uy <= mid)) | (ws & (uy >= mid)) | ~(wn | ws))
    w_h = W_wire & (ww | we) & ((uy == mid - 1) | (uy == mid)) & ((ww & (ux <= mid)) | (we & (ux >= mid)) | ~(ww | we))
    pylon = W_wire & (ux >= mid - 1) & (ux <= mid + 1) & (uy >= mid - 1) & (uy <= mid + 1)
    img[w_v | w_h] = np.where(T_pw[w_v | w_h, None], _rgb("#D68910"), _rgb("#7F8C8D"))
    img[pylon] = np.where(T_pw[pylon, None], _rgb("#F5B041"), _rgb("#4D5656"))

    # 7. Zones: Empty surveyed lots vs. Developed architectural rooftops
    edge_tile = (ux == 0) | (ux == S - 1) | (uy == 0) | (uy == S - 1)
    inner_box = (ux >= 1) & (ux <= S - 2) & (uy >= 1) & (uy <= S - 2)
    win_grid = ((ux % 3 == 2) & (uy % 3 == 2)) & inner_box

    # 7a. Residential (empty 240..248, cottages 249..260, 3x3 apartment blocks 261+)
    W_res = T_cls == cid("residential")
    res_empty = W_res & (T_idx >= 240) & (T_idx <= 248)
    res_house = W_res & (T_idx >= 249) & (T_idx <= 260)
    res_apt = W_res & ~res_empty & ~res_house

    # Empty residential lot: green parcel with dashed white lot boundary
    img[res_empty] = np.where(T_pw[res_empty, None], _rgb("#DCEAD6"), _rgb("#68707D"))
    lot_b = res_empty & edge_tile & (((ux + uy) % 2) == 0)
    img[lot_b] = np.where(T_pw[lot_b, None], _rgb("#82A878"), _rgb("#3E444F"))

    # Single-tile houses: garden + terracotta pitched roof
    img[res_house] = np.where(T_pw[res_house, None], _rgb("#D5E5CE"), _rgb("#5A6270"))
    h_roof = res_house & (ux >= 1) & (ux <= S - 2) & (uy >= 2) & (uy <= S - 2)
    h_ridge = res_house & (ux >= 2) & (ux <= S - 3) & (uy == S // 2)
    img[h_roof] = np.where(T_pw[h_roof, None], _rgb("#CC6B49"), _rgb("#484F5C"))
    img[h_ridge] = np.where(T_pw[h_ridge, None], _rgb("#E59866"), _rgb("#656D7A"))
    h_win = h_roof & T_pw & (ux == S // 2) & (uy == S - 2)
    img[h_win] = _rgb("#FFF3A1")

    # Developed 3x3 residential apartment blocks
    img[res_apt] = np.where(T_pw[res_apt, None], _rgb("#E8D8BE"), _rgb("#565E6C"))
    apt_roof = res_apt & inner_box
    apt_eave = res_apt & ((ux == 1) | (uy == 1)) & inner_box
    apt_court = res_apt & (((T_idx - 261) % 9) == 4) & (ux >= 2) & (ux <= S - 3) & (uy >= 2) & (uy <= S - 3)
    img[apt_roof] = np.where(T_pw[apt_roof, None], _rgb("#C96A4B"), _rgb("#454C59"))
    img[apt_eave] = np.where(T_pw[apt_eave, None], _rgb("#E28E6E"), _rgb("#5E6675"))
    img[apt_court] = np.where(T_pw[apt_court, None], _rgb("#7FB374"), _rgb("#39404B"))
    img[apt_roof & T_pw & win_grid & ~apt_court] = _rgb("#FFE89C")

    # 7b. Commercial (empty 423..431, developed glass office towers 432+)
    W_com = T_cls == cid("commercial")
    com_empty = W_com & (T_idx >= 423) & (T_idx <= 431)
    com_dev = W_com & ~com_empty
    img[com_empty] = np.where(T_pw[com_empty, None], _rgb("#D6E4F0"), _rgb("#5E6673"))
    c_lot_b = com_empty & edge_tile & (((ux + uy) % 2) == 0)
    img[c_lot_b] = np.where(T_pw[c_lot_b, None], _rgb("#6C9BC2"), _rgb("#3A404A"))

    img[com_dev] = np.where(T_pw[com_dev, None], _rgb("#C5D6E6"), _rgb("#4B5362"))
    com_tower = com_dev & inner_box
    com_roof = com_dev & (ux >= 2) & (ux <= S - 3) & (uy >= 2) & (uy <= 3)
    img[com_tower] = np.where(T_pw[com_tower, None], _rgb("#28689C"), _rgb("#383F4C"))
    img[com_roof] = np.where(T_pw[com_roof, None], _rgb("#7FB8E6"), _rgb("#525B6B"))
    img[com_tower & T_pw & win_grid] = _rgb("#BEE9FF")

    # 7c. Industrial (empty 612..620, developed sawtooth factories & smokestacks 621+)
    W_ind = T_cls == cid("industrial")
    ind_empty = W_ind & (T_idx >= 612) & (T_idx <= 620)
    ind_dev = W_ind & ~ind_empty
    img[ind_empty] = np.where(T_pw[ind_empty, None], _rgb("#EAE0C8"), _rgb("#5D6470"))
    i_lot_b = ind_empty & edge_tile & (((ux + uy) % 2) == 0)
    img[i_lot_b] = np.where(T_pw[i_lot_b, None], _rgb("#B28F46"), _rgb("#3B414B"))

    img[ind_dev] = np.where(T_pw[ind_dev, None], _rgb("#D4C4A8"), _rgb("#4D5461"))
    ind_shed = ind_dev & inner_box
    sawtooth = ind_shed & ((uy % 3) == 1)
    stack = ind_dev & (ux >= S - 3) & (ux <= S - 2) & (uy >= 1) & (uy <= 3)
    img[ind_shed] = np.where(T_pw[ind_shed, None], _rgb("#A8701A"), _rgb("#3E4450"))
    img[sawtooth] = np.where(T_pw[sawtooth, None], _rgb("#D49B38"), _rgb("#535B69"))
    img[stack] = _rgb("#282C34")
    smoke = ind_dev & T_pw & (ux == S - 2) & (uy == 0)
    img[smoke] = _rgb("#F2F4F4")

    # 7d. Civic (port, airport, fire/police stations, stadium)
    W_civ = T_cls == cid("civic")
    img[W_civ] = np.where(T_pw[W_civ, None], _rgb("#DED6EA"), _rgb("#505764"))
    civ_b = W_civ & inner_box
    civ_cross = W_civ & (((ux == mid) & (uy >= 2) & (uy <= S - 3)) | ((uy == mid) & (ux >= 2) & (ux <= S - 3)))
    img[civ_b] = np.where(T_pw[civ_b, None], _rgb("#6D5691"), _rgb("#3B414D"))
    img[civ_cross] = np.where(T_pw[civ_cross, None], _rgb("#F4ECF7"), _rgb("#6A7382"))

    # 8. 4x4 Coal / Nuclear Power Plants (heavy dark-iron complex + red/white stacks + boiler glow)
    W_plt = T_cls == cid("plant")
    img[W_plt] = _rgb("#2C313A")
    plt_hall = W_plt & ((ux > 0) & (uy > 0))
    img[plt_hall] = _rgb("#191D24")
    # Sub-tile coordinates inside 4x4 coal (745..760) or nuclear (811..826) complex
    is_coal = W_plt & (T_idx >= 745) & (T_idx <= 760)
    is_nuc = W_plt & (T_idx >= 811) & (T_idx <= 826)
    sub16 = np.where(is_coal, T_idx - 745, np.where(is_nuc, T_idx - 811, 0))
    pr, pc_ = sub16 // 4, sub16 % 4
    # Twin striped smokestacks on upper rows, glowing turbine/boiler cores on lower rows
    chimney = W_plt & ((pc_ == 1) | (pc_ == 2)) & (pr <= 1) & (ux >= 2) & (ux <= S - 3)
    stripe = chimney & ((uy % 3) == 0)
    boiler = W_plt & (pr >= 2) & (pc_ >= 1) & (pc_ <= 2) & (ux >= 2) & (ux <= S - 3) & (uy >= 2) & (uy <= S - 3)
    busbar = W_plt & ((ux == 0) | (uy == 0))
    img[chimney] = _rgb("#B03A2E")
    img[stripe] = _rgb("#F8F9F9")
    img[boiler] = _rgb("#F39C12")
    img[busbar] = _rgb("#5D6D7E")

    # 9. Rubble & Active Fire Sprites
    W_rub = T_cls == cid("rubble")
    img[W_rub] = _rgb("#C5C2B8")
    debris = W_rub & (((ux * 3 + uy * 5 + tx + ty) % 4) == 0)
    debris_dark = W_rub & (((ux * 7 + uy * 2 + tx) % 7) == 0)
    img[debris] = _rgb("#85898E")
    img[debris_dark] = _rgb("#4A4E54")

    W_fire = T_cls == cid("fire")
    img[W_fire] = _rgb("#5B2C22")
    fl_outer = W_fire & (ux >= 1) & (ux <= S - 2) & (uy >= 1) & (uy <= S - 2) & ((ux + uy) >= 3)
    fl_mid = W_fire & (ux >= 2) & (ux <= S - 3) & (uy >= 2) & (uy <= S - 2)
    fl_core = W_fire & (ux >= mid - 1) & (ux <= mid) & (uy >= mid) & (uy <= S - 2)
    img[fl_outer] = _rgb("#C0392B")
    img[fl_mid] = _rgb("#F39C12")
    img[fl_core] = _rgb("#FFF59D")

    # 10. High-contrast Amber Lightning-Bolt Blackout Badges on Unpowered Zone Centres
    need_tile = np.isin(cls, [cid(n) for n in NEEDS_POWER]) & ~pw
    # Identify 3x3 zone centres: explicit LIGHTNINGBOLT (827), known empty/developed 3x3 centres, or local 3x3 interior
    is_center_code = (
        (ti == 827) | (ti == 244) | (ti == 427) | (ti == 616) | (ti == 698) | (ti == 716) | (ti == 765) | (ti == 774) | (ti == 784)
        | ((ti >= 261) & (ti <= 422) & (((ti - 261) % 9) == 4))
        | ((ti >= 432) & (ti <= 611) & (((ti - 432) % 9) == 4))
        | ((ti >= 621) & (ti <= 692) & (((ti - 621) % 9) == 4))
    )
    interior_unlit = (
        need_tile & _shift_mask(need_tile, -1, 0) & _shift_mask(need_tile, 1, 0)
        & _shift_mask(need_tile, 0, -1) & _shift_mask(need_tile, 0, 1)
        & ((np.arange(H)[:, None] % 3 == 1) & (np.arange(W)[None, :] % 3 == 1))
    )
    bolt_tile = need_tile & (is_center_code | interior_unlit)
    B_tile = bolt_tile[ty, tx]

    # Subtle cool blackout frame around unpowered zone blocks
    unlit_px = np.isin(T_cls, [cid(n) for n in NEEDS_POWER]) & ~T_pw
    unlit_border = unlit_px & ((ux == 0) | (uy == 0))
    img[unlit_border] = _rgb("#232832")

    # Crisp 8x8 normalized lightning-bolt glyph inside dark badge on each unpowered zone centre
    bx = (ux * 8) // S
    by = (uy * 8) // S
    shield = B_tile & (bx >= 1) & (bx <= 6) & (by >= 1) & (by <= 6)
    bolt = B_tile & (
        ((by == 1) & ((bx == 4) | (bx == 5)))
        | ((by == 2) & ((bx == 3) | (bx == 4)))
        | ((by == 3) & (bx >= 2) & (bx <= 5))
        | ((by == 4) & (bx >= 2) & (bx <= 5))
        | ((by == 5) & ((bx == 3) | (bx == 4)))
        | ((by == 6) & ((bx == 2) | (bx == 3)))
    )
    img[shield] = _rgb("#171A21")
    img[bolt] = _rgb("#FFD43B")

    return img


def legend_handles(only=None):
    from matplotlib.patches import Patch
    items = [
        ("residential", LIT["residential"], "#8F422B", None),
        ("commercial", LIT["commercial"], "#1E4C7A", None),
        ("industrial", LIT["industrial"], "#7E5614", None),
        ("civic", LIT["civic"], "#4A3966", None),
        ("power plant (4x4)", LIT["plant"], "#B03A2E", None),
        ("road / traffic", LIT["road"], "#2B303A", None),
        ("power line", LIT["wire"], "#875212", None),
        ("water", LIT["water"], "#437BA8", None),
        ("trees", LIT["trees"], "#2A5C36", None),
        ("rubble", LIT["rubble"], "#5D636A", None),
        ("fire", LIT["fire"], "#9E1B22", None),
        ("unpowered (blackout)", UNLIT["commercial"], "#FFD43B", None),
    ]
    key_map = {
        "power plant (4x4)": "plant",
        "road / traffic": "road",
        "power line": "wire",
        "unpowered (blackout)": "off",
    }
    hs = []
    for label, col, edge, hatch in items:
        raw_name = key_map.get(label, label)
        if only is not None and raw_name != "off" and raw_name not in only:
            continue
        lw = 0.9 if raw_name == "off" else 0.45
        p = Patch(facecolor=col, edgecolor=edge, hatch=hatch, linewidth=lw, label=label)
        hs.append(p)
    return hs


def stub(name: str, title: str, waits_for: str, source: str, width=COLUMN_IN, height=1.9):
    """A labelled placeholder that says, in the PDF, which result it waits for. No data is drawn."""
    import textwrap
    apply()
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((0.02, 0.04), 0.96, 0.92, boxstyle="round,pad=0,rounding_size=0.02",
                                facecolor="#F6F6F4", edgecolor="#B5B5B5", linewidth=0.6, linestyle=(0, (3, 2))))
    cpl = int(width / COLUMN_IN * 53)
    fix = lambda t: t.replace("10^3", "$10^3$").replace("10^4", "$10^4$")
    t = "\n".join(textwrap.wrap(fix(title), cpl))
    w = "\n".join(textwrap.wrap("Waits for: " + fix(waits_for), int(cpl * 1.08)))
    sname = "\n".join(textwrap.wrap("Source: " + source, int(cpl * 1.15), break_on_hyphens=False))
    ax.text(0.06, 0.88, "SLOT", color=RED, fontsize=8, fontweight="bold", va="top")
    ax.text(0.06, 0.76, t, color=INK, fontsize=7.5, va="top", linespacing=1.25)
    ax.text(0.06, 0.38, w, color=MUTED, fontsize=6.8, va="top", linespacing=1.2)
    ax.text(0.06, 0.17, sname, color=MUTED, fontsize=6.3, va="top", linespacing=1.2)
    return save(fig, name, {"stub": True, "waits_for": waits_for, "source": source})
