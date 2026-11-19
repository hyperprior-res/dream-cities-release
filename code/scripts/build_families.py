"""Build the start-state families: data/families/*.cty, data/families.json, results/families/.

    python code/scripts/build_families.py [--workers 16] [--master-seed 20261109]

Deterministic given the master seed: every family's random choices come from
``numpy.random.default_rng([master_seed, split_code, family_index, map_attempt])``, so the output does
not depend on the number of workers. See ``dc.families`` for the recipe a start file follows.

Training split: bundled cities with a real city in them (population at load >= 2,000 and the start
bar met), the first 20 by file name, plus generated families to make 60. Held-out split: 40 generated
families, map seeds disjoint from training. Each generated family is given a target population
band; its builder style and warm-up treasury are drawn from that band's recipe, the builder runs
360 months, and the warm-up length W (60..360) is drawn among the months whose population lies in
the band. The builder seed (with style and treasury) is re-rolled until the start bar is met; every
attempt is recorded.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc.behaviour import BUILDER_STYLES, LatticeBuilder, rollout_behaviour  # noqa: E402
from dc.engine import PROTO_VERSION, Engine  # noqa: E402
from dc.families import (  # noqa: E402
    CITIES_DIR, FAMILIES_DIR, FUNDS_CHOICES, LOGS_DIR, MANIFEST_PATH, POP_BIN_NAMES, POP_BINS, RESULTS_DIR,
    check_bar, contact_sheet, make_terrain, pop_bin, save_variant, sha256_file,
)

N_TRAIN, N_HELDOUT, MAX_BUNDLED = 60, 40, 20
LOG_MONTHS = 360                 # builder rollout length; W is chosen inside [W_MIN, W_MAX]
W_MIN, W_MAX = 60, 360
BUNDLED_MONTHS = (24, 60, 120)   # extra months of a scripted builder for bundled variants
MAX_ATTEMPTS = 10                # builder re-rolls per map seed
MAP_TRIES = 3                    # map seeds per generated family
MAP_BASE = {"train": 10_000, "heldout": 20_000}
MAP_STRIDE = 1_000               # map seed of family k, try m: base + k + m * stride
SPLIT_CODE = {"train": 1, "heldout": 2}
BIN_TOP = 250_000                # upper end of the >80k band when drawing a target

# per population band: builder styles and warm-up treasuries (funds at the terrain's creation)
RECIPES = {
    0: {"styles": ["frugal", "satellite", "corridor", "industry", "grid"], "funds0": [20000]},
    1: {"styles": ["grid", "corridor", "satellite", "industry", "frugal", "boom", "transit"], "funds0": [20000, 50000]},
    2: {"styles": ["grid", "corridor", "industry", "boom", "transit"], "funds0": [50000, 100000]},
    3: {"styles": ["boom", "transit"], "funds0": [100000, 150000]},
}


def _rng(master, split, k, m=0):
    return np.random.default_rng([int(master), SPLIT_CODE[split], int(k), int(m)])


# ----------------------------------------------------------------------------------------------
# Workers
# ----------------------------------------------------------------------------------------------
def build_generated(task: dict) -> dict:
    fid, split, k, target_bin, master = task["id"], task["split"], task["k"], task["bin"], task["master"]
    n_var = 4 if split == "train" else 1
    eng = Engine()
    attempts = []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for m in range(MAP_TRIES):
            map_seed = MAP_BASE[split] + k + m * MAP_STRIDE
            rng = _rng(master, split, k, m)
            for a in range(MAX_ATTEMPTS):
                rec = RECIPES[target_bin]
                style = str(rng.choice(rec["styles"]))
                funds0 = int(rng.choice(rec["funds0"]))
                builder_seed = int(rng.integers(1, 2 ** 31 - 1))
                engine_seed = int(rng.integers(1, 2 ** 31 - 1))
                funds_final = int(rng.choice(FUNDS_CHOICES))
                att = {"map_seed": map_seed, "style": style, "funds0": funds0, "builder_seed": builder_seed,
                       "engine_seed": engine_seed, "funds_final": funds_final}
                terrain = td / f"{fid}_terrain.cty"
                tsha = make_terrain(eng, map_seed, funds0, terrain)
                pol = LatticeBuilder(BUILDER_STYLES[style])
                plan, rep = rollout_behaviour(eng, terrain, pol, LOG_MONTHS, engine_seed, False,
                                              np.random.default_rng(builder_seed), record="scalars")
                pops = rep.scalars[:, 5]
                lo, hi = POP_BINS[target_bin]
                cand = [w for w in range(W_MIN, W_MAX + 1) if lo <= pops[w] < hi]
                att["max_pop"] = int(pops.max())
                if not cand:
                    att["result"] = "population never in band"
                    attempts.append(att)
                    continue
                # up to three warm-up lengths from the months in band, at random
                order = [cand[int(i)] for i in rng.permutation(len(cand))[:3]]
                done = None
                for W in order:
                    out = FAMILIES_DIR / f"{fid}-v{n_var - 1}.cty"
                    sha = save_variant(eng, terrain, plan, W, engine_seed, funds_final, out)
                    ok, info = check_bar(eng, out)
                    if pop_bin(info["pop"]) != target_bin:
                        ok = False
                        info["fails"] = info["fails"] + ["band"]
                    if ok:
                        done = (W, sha, info)
                        break
                    att.setdefault("tried_W", []).append({"W": W, "fails": info["fails"], "pop": info["pop"]})
                if done is None:
                    att["result"] = "start bar not met"
                    attempts.append(att)
                    continue
                W, sha_top, info_top = done
                att["result"] = "ok"
                att["W"] = W
                attempts.append(att)
                variants = []
                months_list = [W] if n_var == 1 else [int(round(W * q)) for q in (0.25, 0.5, 0.75)] + [W]
                for v, mo in enumerate(months_list):
                    out = FAMILIES_DIR / f"{fid}-v{v}.cty"
                    if mo == W and v == n_var - 1:
                        sha, ok, info = sha_top, True, info_top
                    else:
                        sha = save_variant(eng, terrain, plan, mo, engine_seed, funds_final, out)
                        ok, info = check_bar(eng, out)
                    variants.append({"months": mo, "file": out.name, "sha256": sha, "ok": ok, "summary": info})
                kept = []
                for v in variants:
                    if v["ok"]:
                        kept.append(v)
                    else:
                        os.remove(FAMILIES_DIR / v["file"])
                # renumber kept variants v0..
                starts = []
                for i, v in enumerate(kept):
                    name = f"{fid}-v{i}.cty"
                    if v["file"] != name:
                        os.replace(FAMILIES_DIR / v["file"], FAMILIES_DIR / name)
                    s = {k2: v[k2] for k2 in ("months", "sha256")}
                    s["start_id"] = f"{fid}-v{i}"
                    s["file"] = name
                    s["summary"] = {k2: v["summary"][k2] for k2 in v["summary"] if k2 != "fails"}
                    starts.append(s)
                dropped = [{"months": v["months"], "fails": v["summary"]["fails"], "pop": v["summary"]["pop"]}
                           for v in variants if not v["ok"]]
                log_file = f"logs/{fid}.npy"
                np.save(FAMILIES_DIR / log_file, plan[:W].astype(np.int16))
                eng.close()
                return {
                    "id": fid, "split": split, "kind": "generated", "source": f"new_terrain(map_seed={map_seed})",
                    "target_band": POP_BIN_NAMES[target_bin],
                    "builder": {"style": style, "builder_seed": builder_seed, "engine_seed": engine_seed,
                                "map_seed": map_seed, "funds0": funds0, "terrain_sha256": tsha,
                                "warmup_months": W, "funds_final": funds_final, "log_file": log_file,
                                "log_months": W, "log_sha256": sha256_file(FAMILIES_DIR / log_file),
                                "rng": "numpy.random.default_rng(builder_seed)", "disasters": False},
                    "attempts": attempts, "dropped_variants": dropped, "starts": starts,
                }
    eng.close()
    for f in FAMILIES_DIR.glob(f"{fid}-v*.cty"):
        f.unlink()
    return {"id": fid, "split": split, "kind": "generated", "failed": True, "attempts": attempts,
            "target_band": POP_BIN_NAMES[target_bin]}


def build_bundled(task: dict) -> dict:
    fid, k, master, src = task["id"], task["k"], task["master"], Path(task["source"])
    eng = Engine()
    rng = _rng(master, "train", 100 + k)
    v0 = FAMILIES_DIR / f"{fid}-v0.cty"
    shutil.copyfile(src, v0)
    ok0, info0 = check_bar(eng, v0)
    attempts = []
    best = None
    for a in range(MAX_ATTEMPTS):
        style = str(rng.choice(sorted(BUILDER_STYLES)))
        builder_seed = int(rng.integers(1, 2 ** 31 - 1))
        engine_seed = int(rng.integers(1, 2 ** 31 - 1))
        funds_final = int(rng.choice(FUNDS_CHOICES))
        att = {"style": style, "builder_seed": builder_seed, "engine_seed": engine_seed, "funds_final": funds_final}
        pol = LatticeBuilder(BUILDER_STYLES[style])
        plan, rep = rollout_behaviour(eng, src, pol, max(BUNDLED_MONTHS), engine_seed, False,
                                      np.random.default_rng(builder_seed), record="scalars")
        res = []
        with tempfile.TemporaryDirectory() as td:
            for i, mo in enumerate(BUNDLED_MONTHS):
                out = Path(td) / f"v{i + 1}.cty"
                sha = save_variant(eng, src, plan, mo, engine_seed, funds_final, out)
                ok, info = check_bar(eng, out)
                res.append((mo, sha, ok, info, out.read_bytes()))
        att["passed"] = [mo for mo, _, ok, _, _ in res if ok]
        att["result"] = "ok" if len(att["passed"]) == len(BUNDLED_MONTHS) else "start bar not met"
        attempts.append(att)
        if best is None or len(att["passed"]) > len(best[1]["passed"]):
            best = (plan, att, res)
        if att["result"] == "ok":
            break
    plan, att, res = best
    starts = [{"start_id": f"{fid}-v0", "file": v0.name, "months": 0, "sha256": sha256_file(v0),
               "summary": {k2: info0[k2] for k2 in info0 if k2 != "fails"}}]
    i = 1
    for mo, sha, ok, info, data in res:
        if not ok:
            continue
        name = f"{fid}-v{i}.cty"
        (FAMILIES_DIR / name).write_bytes(data)
        starts.append({"start_id": f"{fid}-v{i}", "file": name, "months": mo, "sha256": sha,
                       "summary": {k2: info[k2] for k2 in info if k2 != "fails"}})
        i += 1
    log_file = f"logs/{fid}.npy"
    np.save(FAMILIES_DIR / log_file, plan.astype(np.int16))
    eng.close()
    return {
        "id": fid, "split": "train", "kind": "bundled", "source": str(src.relative_to(ROOT)),
        "builder": {"style": att["style"], "builder_seed": att["builder_seed"], "engine_seed": att["engine_seed"],
                    "funds_final": att["funds_final"], "warmup_months": 0, "log_file": log_file,
                    "log_months": int(plan.shape[0]), "log_sha256": sha256_file(FAMILIES_DIR / log_file),
                    "rng": "numpy.random.default_rng(builder_seed)", "disasters": False,
                    "variant_months": list(BUNDLED_MONTHS)},
        "attempts": attempts, "starts": starts,
    }


def screen_bundled(path: str) -> dict:
    eng = Engine()
    ok, info = check_bar(eng, path)
    eng.close()
    return {"source": path, "ok": ok, "info": info}


# ----------------------------------------------------------------------------------------------
# Reports
# ----------------------------------------------------------------------------------------------
def write_reports(manifest: dict, screen: list, elapsed: float, cmd: str) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fams = manifest["families"]
    lines = ["# Start-state families", "",
             f"Built by `{cmd}` in {elapsed:.0f} s. Protocol `{PROTO_VERSION}`. "
             f"{len(fams)} families, {sum(len(f['starts']) for f in fams)} start files.", ""]
    lines += ["## Bundled cities screened", "",
              "Rule: population at load at least 2,000 and the start bar met; first 20 by file name.", "",
              "| file | pop | zones | powered | no-op min/start | bar | taken |", "|---|---|---|---|---|---|---|"]
    taken = {f["source"] for f in fams if f["kind"] == "bundled"}
    for s in screen:
        i = s["info"]
        lines.append(f"| {Path(s['source']).name} | {i['pop']:,} | {i['zones']} | {i['powered_fraction']:.2f} | "
                     f"{i['noop_min_pop_ratio']:.2f} | {'met' if s['ok'] else 'fails: ' + ','.join(i['fails'])} | "
                     f"{'yes' if str(Path(s['source']).relative_to(ROOT)) in taken else ''} |")
    lines += ["", "## Families", "",
              "Population, funds, zones and powered fraction are of the family's reference start at load: the "
              "full warm-up for a generated family, the bundled file itself for a bundled one. funds0: treasury of "
              "the generated terrain during the warm-up. W: warm-up months. F: funds set before saving (bundled: "
              "variants 1.. only; variant 0 is the file as distributed). style: the warm-up builder (bundled: the "
              "builder that made variants 1..). Attempts: builder re-rolls until the bar was met.", "",
              "| family | split | kind | style | funds0 | W | F | pop | funds | zones | powered | variants | attempts |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for f in fams:
        b = f["builder"]
        s = f["starts"][-1]["summary"] if f["kind"] == "generated" else f["starts"][0]["summary"]
        lines.append(f"| {f['id']} | {f['split']} | {f['kind']} | {b['style']} | {b.get('funds0', '-')} | "
                     f"{b['warmup_months']} | {b['funds_final']} | {s['pop']:,} | {s['funds']:,} | {s['zones']} | "
                     f"{s['powered_fraction']:.2f} | {len(f['starts'])} | {len(f['attempts'])} |")
    lines += ["", "## Population histogram by split (families; reference variant)", "",
              "| split | " + " | ".join(POP_BIN_NAMES) + " |", "|---|" + "---|" * len(POP_BIN_NAMES)]
    for split in ("train", "heldout"):
        h = [0] * len(POP_BINS)
        for f in fams:
            if f["split"] != split:
                continue
            s = f["starts"][-1]["summary"] if f["kind"] == "generated" else f["starts"][0]["summary"]
            h[pop_bin(s["pop"])] += 1
        lines.append(f"| {split} | " + " | ".join(str(v) for v in h) + " |")
    lines += ["", "## Population histogram by split (all start variants)", "",
              "| split | " + " | ".join(POP_BIN_NAMES) + " |", "|---|" + "---|" * len(POP_BIN_NAMES)]
    for split in ("train", "heldout"):
        h = [0] * len(POP_BINS)
        for f in fams:
            if f["split"] == split:
                for s in f["starts"]:
                    h[pop_bin(s["summary"]["pop"])] += 1
        lines.append(f"| {split} | " + " | ".join(str(v) for v in h) + " |")
    lines += ["", "Contact sheet: `results/families/contact_sheet.png`.", ""]
    (RESULTS_DIR / "summary.md").write_text("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--master-seed", type=int, default=20261109)
    args = ap.parse_args()
    cmd = "python code/scripts/build_families.py " + " ".join(sys.argv[1:])
    t0 = time.time()
    if FAMILIES_DIR.exists():
        shutil.rmtree(FAMILIES_DIR)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ctx = mp.get_context("spawn")
    with ctx.Pool(args.workers) as pool:
        screen = pool.map(screen_bundled, [str(p) for p in sorted(CITIES_DIR.glob("*.cty"))])
        bundled = [s["source"] for s in screen if s["ok"] and s["info"]["pop"] >= 2000][:MAX_BUNDLED]
        bund_bins = [pop_bin(s["info"]["pop"]) for s in screen if s["source"] in bundled]
        # generated training quotas: bring the training split towards a quarter per band
        want = [N_TRAIN // 4] * 4
        quota = [max(0, want[b] - bund_bins.count(b)) for b in range(4)]
        n_gen_train = N_TRAIN - len(bundled)
        while sum(quota) > n_gen_train:
            quota[int(np.argmax(quota))] -= 1
        while sum(quota) < n_gen_train:
            quota[int(np.argmin(quota))] += 1
        tasks_b = [{"id": f"tr-b-{Path(s).stem}", "k": i, "master": args.master_seed, "source": s}
                   for i, s in enumerate(bundled)]
        tasks_g = []
        bins_tr = [b for b in range(4) for _ in range(quota[b])]
        for i, b in enumerate(bins_tr):
            tasks_g.append({"id": f"tr-g-{i:02d}", "split": "train", "k": i, "bin": b, "master": args.master_seed})
        bins_ho = [b for b in range(4) for _ in range(N_HELDOUT // 4)]
        for i, b in enumerate(bins_ho):
            tasks_g.append({"id": f"ho-g-{i:02d}", "split": "heldout", "k": i, "bin": b, "master": args.master_seed})
        res_b = pool.map(build_bundled, tasks_b)
        res_g = pool.map(build_generated, tasks_g, chunksize=1)
    failed = [r for r in res_g if r.get("failed")]
    fams = res_b + [r for r in res_g if not r.get("failed")]
    manifest = {
        "protocol": PROTO_VERSION, "master_seed": args.master_seed, "command": cmd,
        "bar": {"pop": 2000, "zones": 20, "powered_fraction": 0.5, "noop_months": 24, "noop_seed": 1, "noop_keep": 0.3},
        "pop_bands": POP_BIN_NAMES, "generated_training_quota": quota,
        "families": fams, "failed": failed,
    }
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=1)
    elapsed = time.time() - t0
    write_reports(manifest, screen, elapsed, cmd)
    # contact sheet of all start cities
    eng = Engine()
    items = []
    for fam in fams:
        for s in fam["starts"]:
            eng.load_start(FAMILIES_DIR / s["file"])
            items.append((f"{s['start_id']} {s['summary']['pop'] // 1000}k", eng.observe().tiles))
    eng.close()
    contact_sheet(items, RESULTS_DIR / "contact_sheet.png", cols=16)
    print(f"families: {len(fams)} ({len(res_b)} bundled), failed {len(failed)}, starts "
          f"{sum(len(f['starts']) for f in fams)}, {elapsed:.0f} s")


if __name__ == "__main__":
    main()
