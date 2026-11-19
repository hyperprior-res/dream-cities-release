#!/usr/bin/env python
"""Run a queue of RL-arm runs (checkpoint x task family x RL seed) on one GPU, in order; resumable.

    rl_queue.py --queue results/rl/queue_gpu0.json --gpu 0              # run (resumes, skips finished runs)
    rl_queue.py --queue results/rl/queue_gpu0.json --gpu 0 --dry-run    # print the commands
    rl_queue.py --make --ckpts <list file> --tasks grow,solvent,treasury,recover,power --seeds 0,1,2 \
                --tasks-file data/tasks_v2_H24.json --out results/rl/queue_all.json   # write a queue
    # warm start from the cloned policies (dc.bc), memory options, evaluation split between two machines:
    rl_queue.py --make ... --variant bc --init-from /path/bc_s{seed}.pt --update-chunk 250 --buffer host \
                --eval-side emulator --out queue_rented.json
    rl_queue.py --queue queue_rented.json --gpu 0                       # on the rented card: train + emulator side
    rl_queue.py --queue queue_rented.json --gpu 0 --side engine         # at home: the engine side of every run

Queue file: {"defaults": {...run_rl.py options...}, "runs": [{"ckpt": ..., "task": ..., "seed": ...}, ...]};
options: model_src (default ladder-v2), tasks_file (default data/tasks_v2_H24.json), compile, budget, snapshots,
eval_workers, threads, variant (default frozen), init_from (a path; ``{seed}`` is replaced by the run's RL seed),
update_chunk, buffer (device | host), eval_side (both | emulator).

Each run is ``run_rl.py train`` (which trains, resumes from its ``latest.pt``, snapshots and evaluates every snapshot).
With ``eval_side: emulator`` the evaluation saves only the emulator phases (the dream episodes and their plans, the
audit's samples of plan 0, the greedy plan in the emulator) and ``emulator.json``, and writes ``DONE_emulator.json``
listing, with sha256, every file the engine side reads: the run's ``results/rl/<run>/config.json`` and ``log.jsonl``,
and under the cache directory the snapshots, ``emulator.json`` and ``eval3_<months>/*.npz``. Carried home (same
relative paths under the results and cache roots), ``--side engine`` runs ``run_rl.py eval --eval-side engine`` for
each run: the engine phases and the records, with no emulator loaded (the checkpoint path names the run and need not
exist at home). A run counts as done with a ``DONE.json`` (or, for the emulator side, a ``DONE_emulator.json``) of
the current evaluation version and is skipped. The runner stops at the first failure. Log:
``<cache>/rl/rl_queue_gpu<k>[_engine].log``.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
CACHE = Path(os.environ.get("WM2_RL_CACHE", "<cache>/rl"))
sys.path.insert(0, str(ROOT / "code" / "scripts"))
DEFAULT_MODEL_SRC = "ladder-v2"
DEFAULT_TASKS_FILE = "data/tasks_v2_H24.json"   # amendment 3
DONE_EMULATOR = "DONE_emulator.json"           # run_rl.DONE_EMULATOR


def log(path: Path, msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    print(line, flush=True)
    with open(path, "a") as f:
        f.write(line + "\n")


def run_dir(run: dict) -> Path:
    """The run's cache directory, named exactly as ``run_rl.py`` names it."""
    import run_rl
    budget = int(run.get("budget") or run_rl.rl.FROZEN.budget)
    tasks = run_rl.tasks_path(run.get("tasks_file", DEFAULT_TASKS_FILE))
    return CACHE / run_rl.name_for("emulator", run["ckpt"], run["task"], int(run["seed"]), budget, tasks,
                                   run.get("variant", "frozen"))


def is_done(d: Path, side: str = "both") -> bool:
    """``side`` "emulator": the emulator side is saved (``DONE_emulator.json``); otherwise the run is evaluated."""
    import run_rl
    p = d / (DONE_EMULATOR if side == "emulator" else "DONE.json")
    return p.exists() and json.loads(p.read_text()).get("eval_version") == run_rl.rl.EVAL_VERSION


def init_from(run: dict) -> str:
    return str(run["init_from"]).replace("{seed}", str(int(run["seed"]))) if run.get("init_from") else ""


def cmd_for(run: dict, side: str = "train") -> list:
    """``side`` "train": ``run_rl.py train`` (with the run's evaluation side); "engine": ``run_rl.py eval --eval-side
    engine`` (the engine side of a split evaluation)."""
    common = ["--env", "emulator", "--ckpt", run["ckpt"], "--model-src", run.get("model_src", DEFAULT_MODEL_SRC),
              "--task", run["task"], "--seed", str(run["seed"]), "--tasks", run.get("tasks_file", DEFAULT_TASKS_FILE),
              "--device", "cuda:0", "--eval-workers", str(run.get("eval_workers", 8)), "--threads", str(run.get("threads", 8))]
    if run.get("variant", "frozen") != "frozen":
        common += ["--variant", run["variant"]]
    if run.get("budget"):
        common += ["--budget", str(run["budget"])]
    if run.get("snapshots"):
        common += ["--snapshots", ",".join(str(int(x)) for x in run["snapshots"])]
    if side == "engine":
        return [PY, str(ROOT / "code/scripts/run_rl.py"), "eval", *common, "--eval-side", "engine"]
    cmd = [PY, str(ROOT / "code/scripts/run_rl.py"), "train", *common]
    if run.get("compile"):
        cmd.append("--compile")
    if init_from(run):
        cmd += ["--init-from", init_from(run)]
    if run.get("update_chunk"):
        cmd += ["--update-chunk", str(int(run["update_chunk"]))]
    if run.get("buffer"):
        cmd += ["--buffer", run["buffer"]]
    if run.get("eval_side", "both") != "both":
        cmd += ["--eval-side", run["eval_side"]]
    return cmd


def make_queue(args) -> None:
    ckpts = [x.strip() for x in Path(args.ckpts).read_text().splitlines() if x.strip() and not x.startswith("#")]
    runs = [{"ckpt": c, "task": t, "seed": int(s)} for c in ckpts for t in args.tasks.split(",") for s in args.seeds.split(",")]
    dflt = {"model_src": args.model_src, "tasks_file": args.tasks_file, "compile": True}
    if args.variant != "frozen":
        dflt["variant"] = args.variant
    if args.init_from:
        dflt["init_from"] = args.init_from
    if args.update_chunk:
        dflt["update_chunk"] = args.update_chunk
    if args.buffer:
        dflt["buffer"] = args.buffer
    if args.eval_side != "both":
        dflt["eval_side"] = args.eval_side
    q = {"defaults": dflt, "runs": runs}
    Path(args.out).write_text(json.dumps(q, indent=1))
    print(f"{len(runs)} runs -> {args.out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--queue")
    ap.add_argument("--gpu", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--side", choices=["train", "engine"], default="train",
                    help="train: run_rl.py train for each run; engine: the engine side of a split evaluation")
    ap.add_argument("--make", action="store_true")
    ap.add_argument("--ckpts")
    ap.add_argument("--tasks", default="grow,solvent,treasury,recover,power", help="--make: task families")
    ap.add_argument("--tasks-file", default=DEFAULT_TASKS_FILE, help="--make: the tasks file (thresholds)")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--model-src", default=DEFAULT_MODEL_SRC)
    ap.add_argument("--variant", default="frozen", help="--make: learner (run_rl.py --variant)")
    ap.add_argument("--init-from", default="", help="--make: cloned policy path; {seed} is replaced by the RL seed")
    ap.add_argument("--update-chunk", type=int, default=0, help="--make: run_rl.py --update-chunk")
    ap.add_argument("--buffer", choices=["", "device", "host"], default="", help="--make: run_rl.py --buffer")
    ap.add_argument("--eval-side", choices=["both", "emulator"], default="both", help="--make: run_rl.py --eval-side")
    ap.add_argument("--out")
    args = ap.parse_args()
    if args.make:
        return make_queue(args)
    if args.queue is None or args.gpu is None:
        ap.error("--queue and --gpu are required")
    q = json.loads(Path(args.queue).read_text())
    runs = [{**q.get("defaults", {}), **r} for r in q["runs"]]
    CACHE.mkdir(parents=True, exist_ok=True)
    logp = CACHE / (f"rl_queue_gpu{args.gpu}" + ("_engine" if args.side == "engine" else "") + ".log")
    env = {**os.environ, "CUDA_DEVICE_ORDER": "PCI_BUS_ID", "CUDA_VISIBLE_DEVICES": str(args.gpu), "OMP_NUM_THREADS": "8",
           "PYTHONPATH": f"{ROOT / 'code'}:{ROOT / 'hpr-dream'}"}
    log(logp, f"rl queue start: {args.queue}, gpu {args.gpu}, side {args.side}, {len(runs)} runs")
    for run in runs:
        d = run_dir(run)
        side = "both" if args.side == "engine" else run.get("eval_side", "both")
        if is_done(d, side):
            log(logp, f"{d.name}: done, skipping")
            continue
        if args.side == "engine" and not is_done(d, "emulator"):
            log(logp, f"{d.name}: the emulator side is not saved ({DONE_EMULATOR} missing); stopping")
            sys.exit(1)
        cmd = cmd_for(run, args.side)
        log(logp, f"{d.name}: {' '.join(shlex.quote(c) for c in cmd)}")
        if args.dry_run:
            continue
        d.mkdir(parents=True, exist_ok=True)
        with open(d.with_suffix(".out"), "a") as out:
            rc = subprocess.run(cmd, env=env, stdout=out, stderr=subprocess.STDOUT, cwd=str(ROOT)).returncode
        if rc != 0 or not is_done(d, side):
            log(logp, f"{d.name}: failed (exit {rc}); stopping")
            sys.exit(1)
        log(logp, f"{d.name}: finished")
    log(logp, "rl queue finished")


if __name__ == "__main__":
    main()
