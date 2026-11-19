"""Start-state families: the city files every replay starts from.

A family is a terrain or bundled city plus the scripted builder that developed it; families are the
unit of the train / held-out split. Each family has one or more start variants, each a ``.cty`` file
in ``data/families/``. ``data/families.json`` (the manifest) records, for every family, how its files
were made (bit for bit) and, for every start variant, the file's sha256 and the observation at load.

Generated family recipe (``regenerate_start`` follows it):

1. ``Engine.new_terrain(map_seed, funds0)`` then ``save_city`` -> the terrain file (sha256 recorded);
2. the warm-up: ``dc.behaviour.rollout_behaviour`` of ``LatticeBuilder(style)`` from the terrain file,
   generator ``numpy.random.default_rng(builder_seed)``, engine seed ``engine_seed``, disasters off;
   its action log is stored in ``data/families/logs/<family>.npy``;
3. a start variant saved after ``months`` months of that log: ``dc.oracle.replay`` of the first
   ``months`` rows from the terrain file, then ``Engine.set_funds(F)``, then ``save_city``.

Bundled family: variant 0 is the bundled file itself (byte copy); variants 1.. are the same recipe
with the bundled file in place of the terrain file (no ``new_terrain`` step).
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from .engine import REPO_ROOT, Engine, Obs
from .grammar import NOOP_ROW, compile_month, compile_plan
from .oracle import replay

FAMILIES_DIR = REPO_ROOT / "data" / "families"
LOGS_DIR = FAMILIES_DIR / "logs"
MANIFEST_PATH = REPO_ROOT / "data" / "families.json"
# more held-out families : their own manifest, so
# ``load_manifest()`` and ``starts()`` (data/families.json) are unchanged; ``heldout_cty_of`` reads both
MANIFEST_X_PATH = REPO_ROOT / "data" / "families_x.json"
RESULTS_DIR = REPO_ROOT / "results" / "families"
CITIES_DIR = REPO_ROOT / "data" / "cities"

# acceptance bar for a start state (REBUILD_SPEC 3.3)
BAR_POP = 2000
BAR_ZONES = 20
BAR_POWERED = 0.5
BAR_NOOP_MONTHS = 24
BAR_NOOP_SEED = 1
BAR_NOOP_KEEP = 0.30

POP_BINS = [(2000, 10000), (10000, 30000), (30000, 80000), (80000, 10 ** 9)]
POP_BIN_NAMES = ["2k-10k", "10k-30k", "30k-80k", ">80k"]
FUNDS_CHOICES = (5000, 10000, 20000, 40000)


def pop_bin(pop: int) -> int:
    for k, (lo, hi) in enumerate(POP_BINS):
        if lo <= pop < hi:
            return k
    return -1


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def obs_summary(obs: Obs) -> dict:
    sc = obs.scalars
    return {
        "pop": int(obs.pop), "funds": int(obs.funds), "zones": int(obs.zones),
        "powered_fraction": round(float(obs.powered_fraction), 4), "plants": int(obs.plants),
        "city_time": int(sc[9]), "res_pop": int(sc[6]), "com_pop": int(sc[7]), "ind_pop": int(sc[8]),
        "tax": int(sc[1]),
    }


def noop_actions(months: int):
    act, _ = compile_month(NOOP_ROW)
    return [act] * months


def check_bar(eng: Engine, cty_path) -> Tuple[bool, dict]:
    """The start-state acceptance bar, checked by loading the saved file with ``load_start``.

    Population >= 2,000; zones >= 20; powered fraction >= 0.5; and under 24 no-op months (the
    grammar's no-op month: tax 7, full funding, nothing built; seed 1, disasters off) the population
    stays above 30 per cent of its start at every month.
    """
    eng.load_start(cty_path)
    o = eng.observe()
    s = obs_summary(o)
    r = replay(eng, cty_path, noop_actions(BAR_NOOP_MONTHS), BAR_NOOP_SEED)
    pops = r.scalars[1:, 5]
    min_ratio = float(pops.min() / max(1, s["pop"]))
    info = dict(s)
    info["noop_min_pop_ratio"] = round(min_ratio, 4)
    info["noop_final_pop"] = int(pops[-1])
    reasons = []
    if s["pop"] < BAR_POP:
        reasons.append("pop")
    if s["zones"] < BAR_ZONES:
        reasons.append("zones")
    if s["powered_fraction"] < BAR_POWERED:
        reasons.append("powered")
    if not min_ratio > BAR_NOOP_KEEP:
        reasons.append("noop_collapse")
    info["fails"] = reasons
    return not reasons, info


# ----------------------------------------------------------------------------------------------
# Manifest access
# ----------------------------------------------------------------------------------------------
def load_manifest(path=MANIFEST_PATH) -> dict:
    with open(path) as f:
        return json.load(f)


def starts(split: str, manifest: Optional[dict] = None) -> List[Tuple[str, str, Path]]:
    """[(start_id, family_id, cty_path)] of every start variant of the split ('train' or 'heldout')."""
    m = manifest or load_manifest()
    out = []
    for fam in m["families"]:
        if fam["split"] != split:
            continue
        for v in fam["starts"]:
            out.append((v["start_id"], fam["id"], FAMILIES_DIR / v["file"]))
    return out


def families(split: Optional[str] = None, manifest: Optional[dict] = None) -> List[dict]:
    m = manifest or load_manifest()
    return [f for f in m["families"] if split is None or f["split"] == split]


def heldout_cty_of() -> Dict[str, str]:
    """start id -> start file (str) of every held-out start of ``data/families.json`` and, when it exists, of
    ``data/families_x.json``. A tasks file names its starts by id; this resolves either set. Raises if a start id is
    in both manifests."""
    out = {sid: str(p) for sid, _f, p in starts("heldout")}
    if MANIFEST_X_PATH.exists():
        for sid, _f, p in starts("heldout", load_manifest(MANIFEST_X_PATH)):
            if sid in out:
                raise ValueError(f"start {sid} is in both {MANIFEST_PATH.name} and {MANIFEST_X_PATH.name}")
            out[sid] = str(p)
    return out


# ----------------------------------------------------------------------------------------------
# Making and regenerating start files
# ----------------------------------------------------------------------------------------------
def make_terrain(eng: Engine, map_seed: int, funds0: int, path) -> str:
    eng.new_terrain(int(map_seed), int(funds0))
    eng.save_city(path)
    return sha256_file(path)


def save_variant(eng: Engine, base_cty, plan: np.ndarray, months: int, engine_seed: int, funds: int, out_path) -> str:
    """Replay the first ``months`` rows of ``plan`` from ``base_cty``, set the funds, save."""
    acts, forced = compile_plan(plan[:months])
    replay(eng, base_cty, acts, int(engine_seed), disasters=False, forced=forced)
    eng.set_funds(int(funds))
    eng.save_city(out_path)
    return sha256_file(out_path)


def regenerate_start(fam: dict, variant: dict, out_path, eng: Engine, work_dir) -> str:
    """Rebuild one start file from the manifest record alone; returns its sha256."""
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    b = fam["builder"]
    if fam["kind"] == "bundled" and variant["months"] == 0:
        shutil.copyfile(REPO_ROOT / fam["source"], out_path)
        return sha256_file(out_path)
    if fam["kind"] == "generated":
        base = work_dir / f"{fam['id']}_terrain.cty"
        tsha = make_terrain(eng, b["map_seed"], b["funds0"], base)
        if tsha != b["terrain_sha256"]:
            raise RuntimeError(f"terrain of {fam['id']} does not regenerate")
    else:
        base = REPO_ROOT / fam["source"]
    plan = np.load(FAMILIES_DIR / b["log_file"])
    return save_variant(eng, base, plan, variant["months"], b["engine_seed"], b["funds_final"], out_path)


def regenerate_log(fam: dict, eng: Engine, work_dir) -> np.ndarray:
    """Re-run the family's builder policy from its seeds; returns the action log it produces."""
    from .behaviour import BUILDER_STYLES, LatticeBuilder, rollout_behaviour
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    b = fam["builder"]
    if fam["kind"] == "generated":
        base = work_dir / f"{fam['id']}_terrain.cty"
        make_terrain(eng, b["map_seed"], b["funds0"], base)
    else:
        base = REPO_ROOT / fam["source"]
    pol = LatticeBuilder(BUILDER_STYLES[b["style"]])
    plan, _ = rollout_behaviour(eng, base, pol, b["log_months"], b["engine_seed"], False,
                                np.random.default_rng(b["builder_seed"]), record="scalars")
    return plan


# ----------------------------------------------------------------------------------------------
# Pictures
# ----------------------------------------------------------------------------------------------
def tile_colours(tiles: np.ndarray) -> np.ndarray:
    """Tile map (120, 100) raw words -> RGB float (100, 120, 3) in a plain palette (no game art).

    Clear land sand, water blue, trees and parks muted green, rubble grey-brown, fire and flood
    red, road dark grey, power line yellow, rail brown, residential bright green, commercial pink,
    industrial ochre, plants / ports / airports / stations / stadiums purple. Unpowered zones are
    drawn at half brightness.
    """
    i = (tiles & 0x3FF).astype(np.int32)
    pw = (tiles & 0x8000) != 0
    c = np.zeros(i.shape + (3,), np.float32) + np.array([0.86, 0.81, 0.66], np.float32)
    table = [
        ((2, 20), (0.27, 0.47, 0.84)), ((21, 43), (0.48, 0.62, 0.42)), ((44, 47), (0.52, 0.47, 0.42)),
        ((48, 63), (0.92, 0.12, 0.08)), ((64, 206), (0.30, 0.30, 0.30)), ((208, 222), (0.92, 0.85, 0.20)),
        ((224, 238), (0.50, 0.32, 0.22)), ((240, 422), (0.20, 0.78, 0.25)), ((423, 611), (0.93, 0.45, 0.62)),
        ((612, 692), (0.85, 0.62, 0.12)), ((693, 860), (0.55, 0.22, 0.65)),
    ]
    for (lo, hi), col in table:
        c[(i >= lo) & (i <= hi)] = col
    zone = (i >= 240) & (i <= 692)
    c[zone & ~pw] *= 0.5
    return c.transpose(1, 0, 2)


def contact_sheet(items: List[Tuple[str, np.ndarray]], path, cols: int = 12, scale: int = 2) -> None:
    """items: [(label, tiles (120, 100))] -> one PNG with a labelled thumbnail per city."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(items)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.25 * scale, rows * 1.2 * scale))
    axes = np.atleast_2d(axes)
    for k in range(rows * cols):
        ax = axes[k // cols, k % cols]
        ax.axis("off")
        if k < n:
            lab, t = items[k]
            ax.imshow(tile_colours(t), interpolation="nearest")
            ax.set_title(lab, fontsize=5 * scale ** 0.5)
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=100)
    plt.close(fig)
