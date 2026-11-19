#!/usr/bin/env python3
"""More held-out start-state families : ``ho-g-40`` .. ``ho-g-119``, one start each.

    python code/scripts/build_families_x.py verify [--workers 16]       # the 40 held-out families, rebuilt in a scratch
                                                                        # directory by today's code, against the manifest
    python code/scripts/build_families_x.py build [--workers 16]        # the new families -> data/families/, data/families_x.json
    python code/scripts/build_families_x.py builder-pool [--workers 16] # their builder pools (gen_builder_pool's recipe)

Then (the behaviour pools and first thresholds, the thresholds rule, the perfect-emulator reference):

    python code/scripts/calibrate_tasks.py --horizon 24 --workers 16 --out-dir <cache>/calibration \
        --manifest data/families_x.json --tasks-out data/tasks_x_H24.json
    WM2_TASKS_V2_CACHE=<cache>/tasks_v2x python code/scripts/task_frontier.py run \
        --tasks-v1 data/tasks_x_H24.json --stages const,pools,overwrite,closed,cem,final,oracle ...   (and assemble)

The new families are made by ``build_families.build_generated`` itself, unchanged: the same generator
(``Engine.new_terrain``), the same per-band recipes (builder styles, warm-up treasuries, warm-up length drawn
among the months in band, start treasury from ``FUNDS_CHOICES``), the same start bar and re-roll rule, and the same
random streams ``numpy.random.default_rng([master_seed, 2, k, m])`` (split code 2 = held out) with the family index
k continuing from 40. Map seeds follow the same rule, 20,000 + k + 1,000 m, so they are 20,040 .. 20,119 (21,040 ..
and 22,040 .. on re-tries), disjoint from every existing family's (10,000 .. 12,039 training, 20,000 .. 22,039
held out). Target bands: a quarter of the families per band, as for the 40 (k 40..59 2k-10k, 60..79 10k-30k,
80..99 30k-80k, 100..119 >80k).

Nothing existing is written: the start files and warm-up logs get new names beside the old ones, and the manifest
of the new families is its own file (``data/families_x.json``, the schema of ``data/families.json``), so
``dc.families.load_manifest()`` and everything that reads it are unchanged.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "scripts"))

import build_families as BF  # noqa: E402
from dc.engine import PROTO_VERSION  # noqa: E402
from dc.families import FAMILIES_DIR, MANIFEST_PATH, POP_BIN_NAMES, load_manifest, pop_bin, sha256_file  # noqa: E402

MANIFEST_X = ROOT / "data" / "families_x.json"
FIRST, N_NEW = 40, 80                          # family indices k = 40 .. 119
MASTER = 20261109                              # data/families.json master_seed


def _build(task: dict) -> dict:
    """``build_generated`` with its output directory pointed at ``task['dir']`` (the module global it writes to)."""
    BF.FAMILIES_DIR = Path(task["dir"])
    return BF.build_generated({k: task[k] for k in ("id", "split", "k", "bin", "master")})


def tasks_for(ks, d: Path, master: int):
    out = []
    for k in ks:
        b = k // 10 if k < 40 else (k - FIRST) // (N_NEW // 4)
        out.append({"id": f"ho-g-{k:02d}", "split": "heldout", "k": k, "bin": b, "master": master, "dir": str(d)})
    return out


def run_pool(tasks, workers):
    ctx = mp.get_context("spawn")
    with ctx.Pool(workers) as pool:
        return pool.map(_build, tasks, chunksize=1)


def cmd_verify(a) -> int:
    m = load_manifest()
    if m["master_seed"] != MASTER:
        raise SystemExit("master seed differs")
    ho = {f["id"]: f for f in m["families"] if f["split"] == "heldout"}
    ks = [int(x) for x in a.ks.split(",")] if a.ks else list(range(40))
    t0 = time.time()
    with tempfile.TemporaryDirectory(dir=a.scratch or None) as td:
        (Path(td) / "logs").mkdir()
        res = run_pool(tasks_for(ks, Path(td), MASTER), a.workers)
        bad = 0
        for r in res:
            f = ho[r["id"]]
            same_rec = (r.get("builder") == f["builder"] and r.get("attempts") == f["attempts"]
                        and r.get("target_band") == f["target_band"] and r.get("source") == f["source"])
            same_files = [s["sha256"] == sha256_file(Path(td) / s["file"]) for s in f["starts"]]
            same_starts = r.get("starts") == f["starts"]
            log_same = sha256_file(Path(td) / f["builder"]["log_file"]) == f["builder"]["log_sha256"]
            ok = same_rec and all(same_files) and same_starts and log_same
            bad += not ok
            print(f"{r['id']}: record {same_rec}, start files {all(same_files)}, start records {same_starts}, "
                  f"warm-up log {log_same}", flush=True)
    print(f"verify: {len(res) - bad} of {len(res)} held-out families rebuilt bit for bit by today's code "
          f"({time.time() - t0:.0f} s)")
    return 1 if bad else 0


def cmd_build(a) -> int:
    if MANIFEST_X.exists() and not a.force:
        raise SystemExit(f"{MANIFEST_X} exists (--force rebuilds it)")
    ks = list(range(FIRST, FIRST + N_NEW))
    existing = {v["file"] for f in load_manifest()["families"] for v in f["starts"]}
    for k in ks:                               # never overwrite a file of the existing families
        if f"ho-g-{k:02d}-v0.cty" in existing:
            raise SystemExit(f"ho-g-{k:02d} is in data/families.json")
    old_seeds = set()
    for f in load_manifest()["families"]:
        for at in f.get("attempts", []):
            if "map_seed" in at:
                old_seeds.add(int(at["map_seed"]))
    new_seeds = {BF.MAP_BASE["heldout"] + k + m * BF.MAP_STRIDE for k in ks for m in range(BF.MAP_TRIES)}
    if old_seeds & new_seeds:
        raise SystemExit(f"map seeds overlap the existing families: {sorted(old_seeds & new_seeds)[:10]}")
    cmd = "python code/scripts/build_families_x.py " + " ".join(sys.argv[1:])
    t0 = time.time()
    res = run_pool(tasks_for(ks, FAMILIES_DIR, MASTER), a.workers)
    failed = [r for r in res if r.get("failed")]
    fams = [r for r in res if not r.get("failed")]
    used = {int(at["map_seed"]) for r in res for at in r["attempts"]}
    manifest = {
        "protocol": PROTO_VERSION, "master_seed": MASTER, "command": cmd,
        "bar": {"pop": 2000, "zones": 20, "powered_fraction": 0.5, "noop_months": 24, "noop_seed": 1, "noop_keep": 0.3},
        "pop_bands": POP_BIN_NAMES,
        "extends": {"manifest": "data/families.json", "manifest_sha256": sha256_file(MANIFEST_PATH),
                    "recipe": "build_families.build_generated, unchanged; family index k continues from 40; target band "
                              "(k - 40) // 20; map seed 20000 + k + 1000 m",
                    "map_seeds_used": sorted(used), "map_seeds_disjoint_from_existing": not (used & old_seeds)},
        "families": fams, "failed": failed, "seconds": round(time.time() - t0, 1),
    }
    MANIFEST_X.write_text(json.dumps(manifest, indent=1))
    hist = [0] * 4
    for f in fams:
        hist[pop_bin(f["starts"][-1]["summary"]["pop"])] += 1
    print(f"families: {len(fams)} built, {len(failed)} failed, {time.time() - t0:.0f} s; reference variants by band "
          + ", ".join(f"{n} {h}" for n, h in zip(POP_BIN_NAMES, hist)) + f" -> {MANIFEST_X}")
    return 0 if not failed else 2


def cmd_builder_pool(a) -> int:
    """The builder pool (best-of-N's proposals; sources a and c of the thresholds rule read it) for the new starts:
    ``gen_builder_pool._one_start``, unchanged (seeds ``bon-policy``, ``bon-gen``, ``bon-eval`` per start, H and plan),
    into the existing directory beside the 40 starts' files (new names; a file that exists with n plans is skipped).
    Its counts go to ``meta_x.json`` there; ``meta.json`` (the 40's run) is not touched. ``gen_builder_pool.py`` itself
    lists the starts of data/families.json only, hence this driver."""
    import gen_builder_pool as GB
    from dc.families import starts
    H, n = a.horizon, a.n
    out_dir = Path(a.out_dir) / f"H{H}"
    out_dir.mkdir(parents=True, exist_ok=True)
    old = {sid for sid, _f, _p in starts("heldout")}
    jobs = [(sid, str(p), H, n, str(out_dir)) for sid, _f, p in starts("heldout", load_manifest(MANIFEST_X))]
    assert not old & {j[0] for j in jobs}
    t0 = time.time()
    months, skipped = 0, 0
    with mp.get_context("fork").Pool(max(1, min(a.workers, len(jobs)))) as pool:
        for k, (sid, m, sec, skip) in enumerate(pool.imap_unordered(GB._one_start, jobs), 1):
            months += m
            skipped += int(skip)
            print(f"{k}/{len(jobs)} {sid} {'skipped (exists)' if skip else f'{m:,} city-months in {sec:.1f} s'}", flush=True)
    sec = time.time() - t0
    meta = {"protocol": PROTO_VERSION, "horizon": H, "n_per_start": n, "split": "heldout",
            "manifest": "data/families_x.json", "styles": list(GB.STYLES), "starts": len(jobs), "starts_skipped": skipped,
            "engine_city_months_this_run": months, "seconds_this_run": round(sec, 1), "workers": a.workers,
            "made_by": "code/scripts/build_families_x.py builder-pool (gen_builder_pool._one_start)",
            "seeds": {"policy": "seed_for('bon-policy', start, H, j)", "closed_loop": "seed_for('bon-gen', start, H, j)",
                      "eval": "seed_for('bon-eval', start, H, j)"}}
    (out_dir / "meta_x.json").write_text(json.dumps(meta, indent=1))
    print(f"builder pool: {len(jobs)} starts ({skipped} already present), {n} plans each, H={H}, "
          f"{months:,} engine city-months in {sec:.1f} s -> {out_dir}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("builder-pool")
    p.add_argument("--horizon", type=int, default=24)
    p.add_argument("--n", type=int, default=1000)
    p.add_argument("--workers", type=int, default=16)
    p.add_argument("--out-dir", default="<cache>/audit/builder_pool")
    v = sub.add_parser("verify")
    v.add_argument("--workers", type=int, default=16)
    v.add_argument("--ks", default="", help="comma-separated family indices of the 40 (default all)")
    v.add_argument("--scratch", default="")
    b = sub.add_parser("build")
    b.add_argument("--workers", type=int, default=16)
    b.add_argument("--force", action="store_true")
    a = ap.parse_args()
    return {"verify": cmd_verify, "build": cmd_build, "builder-pool": cmd_builder_pool}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
