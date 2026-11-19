#!/usr/bin/env python
"""Run a queue of emulator training runs on one GPU, in order, then evaluate each run's checkpoints.

    ladder.py --queue code/scripts/ladder_queue.json --gpu 0            # run (resumes, skips finished)
    ladder.py --queue code/scripts/ladder_queue.json --gpu 1 --only os_15m_small,sf_15m_small
    ladder.py --queue code/scripts/ladder_queue.json --gpu 0 --dry-run  # print the commands and the plan

Per run (``runs`` in the queue file; ``defaults`` fill missing fields):
* training: ``train_run.py`` with the run's size, mode, samples, index, seed, save points and, for a
  self-forcing run, ``--init-from`` the final checkpoint of the run named in ``init_from`` (which must
  have finished). ``train_run.py`` resumes from ``<ckpt-root>/<name>/latest.pt`` when it exists, so an
  interrupted run continues where it stopped. On a clean exit the runner writes
  ``<ckpt-root>/<name>/DONE.json`` (final checkpoint, its sha256, samples consumed); a run with
  DONE.json is skipped.
* evaluation: ``eval_fidelity.py`` (decoding a, the trained generative model) on every
  ``samples_*.pt`` of the run on the development selection (monitoring), then the final checkpoint
  on the test selection (the paper's tables) and on train_eval, into
  ``results/fidelity/ladder/<name>/<selection>/``; the baselines and the engine yardstick are cached
  once per selection under ``results/fidelity/ladder/_floor/<selection>`` (and recomputed whenever
  their key, which includes the code, changes). Marked by ``EVAL_DONE.json``.
* micro-batching follows the card: on a GPU with less than 40 GB the 50M runs accumulate micro-batches
  of 64 and the 100M runs of 32 (same 128-sample steps, same schedule).
The runner stops at the first failure. Log: ``<ckpt-root>/ladder_gpu<k>.log``.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
CKPT_ROOT = Path("<cache>/ckpt")
RESULTS = ROOT / "results" / "fidelity" / "ladder"


def log(path: Path, msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    print(line, flush=True)
    with open(path, "a") as f:
        f.write(line + "\n")


def gpu_memory_gb(gpu: int) -> float:
    """Total memory of the card (nvidia-smi); any failure stops the runner rather than guessing."""
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits", "-i", str(gpu)],
                         capture_output=True, text=True, timeout=20, env={**os.environ, "CUDA_DEVICE_ORDER": "PCI_BUS_ID"})
    if out.returncode != 0 or not out.stdout.strip():
        raise RuntimeError(f"nvidia-smi failed for GPU {gpu}: exit {out.returncode}: {out.stderr.strip()}")
    return float(out.stdout.strip().splitlines()[0]) / 1024.0


def micro_batch_for(size: str, mem_gb: float) -> int:
    if mem_gb >= 40:
        return 0
    return {"15m": 0, "50m": 64, "100m": 32}.get(size, 32)


def done_info(ckpt_root: Path, name: str):
    p = ckpt_root / name / "DONE.json"
    return json.loads(p.read_text()) if p.exists() else None


def final_checkpoint(ckpt_root: Path, name: str, samples: int):
    """The last milestone checkpoint whose sample count reached the budget, with a sha256 sidecar."""
    run = ckpt_root / name
    best = None
    for p in sorted(run.glob("samples_*.pt")):
        n = int(p.stem.split("_")[1])
        if n >= samples and (run / (p.name + ".sha256")).exists():
            best = p
    return best


def train_cmd(run: dict, ckpt_root: Path, mem_gb: float, init_path) -> list:
    cmd = [PY, str(ROOT / "code/scripts/train_run.py"), "--run", run["name"], "--size", run["size"], "--mode", run["mode"],
           "--samples", str(run["samples"]), "--index", run["index"], "--seed", str(run.get("seed", 0)),
           "--batch-size", str(run.get("batch_size", 128)), "--lr", str(run["lr"]),
           "--budget-weight", str(run.get("budget_weight", 6.0)), "--table-lr-mult", str(run.get("table_lr_mult", 10.0)),
           "--ckpt-root", str(ckpt_root), "--workers", str(run.get("workers", 6))]
    mb = run.get("micro_batch", micro_batch_for(run["size"], mem_gb))
    if mb:
        cmd += ["--micro-batch", str(mb)]
    if run.get("save_samples"):
        cmd += ["--save-samples", ",".join(str(int(x)) for x in run["save_samples"])]
    if run["mode"] == "selfforce":
        cmd += ["--init-from", str(init_path), "--sf-k", str(run.get("sf_k", 4)), "--sf-tf-ratio", str(run.get("sf_tf_ratio", 0.5))]
    if run.get("model_overrides"):
        cmd += ["--model-overrides", json.dumps(run["model_overrides"])]
    if run.get("bk_updates") is not None:
        cmd += ["--bk-updates", str(run["bk_updates"]), "--bk-batch", str(run.get("bk_batch", 4096))]
    return cmd


EVAL_STAGES = (("dev", "all"), ("test", "final"), ("train_eval", "final"))   # selection, checkpoints
FLOOR_FILES = ("baselines.json", "floor_onestep.json", "floor_rollouts_s1.json")


def eval_cmds(run: dict, ckpt_root: Path, mem_gb: float = 98.0) -> list:
    """[(selection, command)]: every checkpoint on the development selection, the final one on test and
    train_eval (decoding a)."""
    cks = sorted((ckpt_root / run["name"]).glob("samples_*.pt"))
    out = []
    for sel, which in EVAL_STAGES:
        use = cks if which == "all" else cks[-1:]
        out.append((sel, [PY, str(ROOT / "code/scripts/eval_fidelity.py"), "--floor", "--decode", "a", "--workers", "2",
                          "--selection", sel, "--batch-plans", "64" if mem_gb >= 40 else "16",
                          *(["--curves", str(ckpt_root / run["name"])] if sel == "dev" else []),
                          "--out-dir", str(RESULTS / run["name"] / sel), "--ckpt", *map(str, use)]))
    return out


def seed_floor_cache(out_dir: Path, sel: str) -> None:
    """Copy the cached baselines and engine yardstick of a selection into out_dir (eval_fidelity.py checks
    their key and recomputes them when the selection or the code differs)."""
    src = RESULTS / "_floor" / sel
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in FLOOR_FILES:
        if (src / f).exists() and not (out_dir / f).exists():
            shutil.copy(src / f, out_dir / f)


def keep_floor_cache(out_dir: Path, sel: str) -> None:
    src = RESULTS / "_floor" / sel
    src.mkdir(parents=True, exist_ok=True)
    for f in FLOOR_FILES:
        if (out_dir / f).exists():
            shutil.copy(out_dir / f, src / f)


def main() -> None:
    global RESULTS
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--queue", required=True)
    ap.add_argument("--gpu", type=int, required=True)
    ap.add_argument("--only", default="", help="comma-separated run names (default: all, in queue order)")
    ap.add_argument("--ckpt-root", default=str(CKPT_ROOT),
                    help="checkpoint root; a run resumes from <root>/<name>/latest.pt, so a new model needs a fresh root")
    ap.add_argument("--results", default=str(RESULTS), help="evaluation output root (default results/fidelity/ladder)")
    ap.add_argument("--no-eval", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    RESULTS = Path(args.results)
    q = json.loads(Path(args.queue).read_text())
    defaults = q.get("defaults", {})
    runs = [{**defaults, **r} for r in q["runs"]]
    only = [x for x in args.only.split(",") if x]
    if only:
        runs = [r for r in runs if r["name"] in only]
    ckpt_root = Path(args.ckpt_root)
    ckpt_root.mkdir(parents=True, exist_ok=True)
    logp = ckpt_root / f"ladder_gpu{args.gpu}.log"
    mem = gpu_memory_gb(args.gpu)
    env = {**os.environ, "CUDA_DEVICE_ORDER": "PCI_BUS_ID", "CUDA_VISIBLE_DEVICES": str(args.gpu), "OMP_NUM_THREADS": "8"}
    log(logp, f"ladder start: queue {args.queue}, gpu {args.gpu} ({mem:.0f} GB), runs {[r['name'] for r in runs]}")
    for run in runs:
        name = run["name"]
        info = done_info(ckpt_root, name)
        if info is None:
            init_path = None
            if run["mode"] == "selfforce":
                base = done_info(ckpt_root, run["init_from"])
                if base is None and args.dry_run:
                    base = {"final_checkpoint": f"<final checkpoint of {run['init_from']}>"}
                if base is None:
                    log(logp, f"{name}: base run {run['init_from']} has not finished; stopping")
                    sys.exit(2)
                init_path = base["final_checkpoint"]
            cmd = train_cmd(run, ckpt_root, mem, init_path)
            log(logp, f"{name}: train: {' '.join(shlex.quote(c) for c in cmd)}")
            if args.dry_run:
                continue
            (ckpt_root / name).mkdir(parents=True, exist_ok=True)
            with open(ckpt_root / f"{name}.out", "a") as out:
                rc = subprocess.run(cmd, env=env, stdout=out, stderr=subprocess.STDOUT, cwd=str(ROOT)).returncode
            fin = final_checkpoint(ckpt_root, name, run["samples"])
            if rc != 0 or fin is None:
                log(logp, f"{name}: training failed (exit {rc}, final checkpoint {fin}); stopping")
                sys.exit(1)
            sha = (fin.parent / (fin.name + ".sha256")).read_text().split()[0]
            info = {"name": name, "final_checkpoint": str(fin), "sha256": sha, "samples": int(fin.stem.split("_")[1]),
                    "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "gpu": args.gpu, "run": run}
            (ckpt_root / name / "DONE.json").write_text(json.dumps(info, indent=1))
            log(logp, f"{name}: done, {info['samples']} samples, {fin}")
        else:
            log(logp, f"{name}: already finished ({info['final_checkpoint']}), skipping training")
        if args.no_eval:
            continue
        out_dir = RESULTS / name
        if (out_dir / "EVAL_DONE.json").exists():
            log(logp, f"{name}: evaluation already done")
            continue
        failed = False
        for sel, cmd in eval_cmds(run, ckpt_root, mem):
            log(logp, f"{name}: eval {sel}: {' '.join(shlex.quote(c) for c in cmd)}")
            if args.dry_run:
                continue
            seed_floor_cache(out_dir / sel, sel)
            with open(ckpt_root / f"{name}.eval.out", "a") as out:
                rc = subprocess.run(cmd, env=env, stdout=out, stderr=subprocess.STDOUT, cwd=str(ROOT)).returncode
            if rc != 0:
                log(logp, f"{name}: evaluation on {sel} failed (exit {rc}); stopping")
                failed = True
                break
            keep_floor_cache(out_dir / sel, sel)
        if failed:
            sys.exit(1)
        if args.dry_run:
            continue
        (out_dir / "EVAL_DONE.json").write_text(json.dumps({"name": name, "finished": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
        log(logp, f"{name}: evaluation done -> {out_dir}")
    log(logp, "ladder queue finished")


if __name__ == "__main__":
    main()
