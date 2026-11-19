#!/usr/bin/env python
"""Train an emulator (one-step or self-forcing), or measure training / inference throughput.

Examples
  # the pilot: 50M, one-step, 600,000 samples, milestones at 150k and 300k (and the end)
  train_run.py --size 50m --samples 600000 --save-samples 150000,300000 --run pilot_50m --index train_full
  # self-forcing fine-tune from a one-step final
  train_run.py --mode selfforce --samples 1500000 --init-from <ckpt> --run sf_50m --index train_full
  # throughput
  train_run.py --bench-train 15m,50m,100m
  train_run.py --bench-infer 15m,50m,100m --batches 256,1024,4096

A run lives in <ckpt-root>/<run>/: log.jsonl, samples_*.pt milestones with .sha256 sidecars, and
latest.pt (resumable, rewritten every --resume-every seconds and at the end). Re-running the same
command resumes from latest.pt. --synthetic trains on the development stand-in (real engine
transitions from bundled cities under random tool calls), for testing only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc.model import SIZES, ModelConfig, build, compute_norm_stats  # noqa: E402
from dc.train import EnginePool, TrainConfig, Trainer, sha256_file  # noqa: E402

CKPT_ROOT = Path("<cache>/ckpt")
CITIES = sorted((ROOT / "data" / "cities").glob("*.cty"))


# ----------------------------------------------------------------------------------------------
# Data 
# ----------------------------------------------------------------------------------------------
def open_split(args):
    """(dc.data module, store, transition index) of the named split through the ``open_split``."""
    from dc import data
    store, idx = data.open_split(args.index, args.data_root or None)
    return data, store, np.asarray(idx, dtype=np.int64)


def data_info(store_path, index_name: str, idx: np.ndarray, seed: int, loader: str) -> dict:
    man = Path(store_path) / "manifest.json"
    return {"store": str(store_path), "manifest_sha256": sha256_file(man) if man.exists() else None,
            "index": index_name, "index_len": int(len(idx)),
            "index_sha256": hashlib.sha256(np.ascontiguousarray(idx.astype(np.int64)).tobytes()).hexdigest(),
            "loader": loader, "seed": seed}


def with_cost(loader, store, device, k: int = 1):
    """Attach the engine's charged build cost of each transition (store accounting) to state_t+1."""
    cost = store.build_cost
    for b in loader:
        ids = np.asarray(loader.last_ids, dtype=np.int64)
        if k == 1:
            s0, r, a, s1 = b
            s1["build_cost"] = torch.from_numpy(np.asarray(cost[ids]).astype(np.float32)).to(device)
            yield s0, r, a, s1
        else:
            for i, step in enumerate(b):
                step[3]["build_cost"] = torch.from_numpy(np.asarray(cost[ids + i]).astype(np.float32)).to(device)
            yield b


def make_batches(args, cfg: TrainConfig, samples_done: int, device):
    """(iterator, data_info, norm-stat iterator factory). The iterator's seed depends on the samples
    already consumed, so a resumed run continues with a fresh, recorded stream."""
    seed = (cfg.seed * 1_000_003 + samples_done) % (2**31 - 1)
    if args.synthetic:
        pool = EnginePool.generate(CITIES, trajs_per_city=args.synthetic_trajs, months=48, seed=cfg.seed, device=device)
        info = {"store": "synthetic EnginePool (bundled cities, random tool calls)", "index": "all",
                "index_len": pool.n, "loader": "EnginePool", "seed": seed}
        if cfg.mode == "onestep":
            it = pool.batches(cfg.batch_size, seed)
        else:
            it = pool.multistep_batches(cfg.batch_size, cfg.sf_k, seed)
        return it, info, (lambda: pool.batches(256, cfg.seed + 17))
    data, store, idx = open_split(args)
    nw = args.workers
    if cfg.mode == "onestep":
        it = with_cost(data.OneStepBatches(store, idx, cfg.batch_size, seed, device, num_workers=nw), store, device)
        loader = f"OneStepBatches(num_workers={nw})"
    else:
        it = with_cost(data.MultiStepBatches(store, idx, cfg.batch_size, seed, device, cfg.sf_k, num_workers=nw),
                       store, device, cfg.sf_k)
        loader = f"MultiStepBatches(k={cfg.sf_k}, num_workers={nw})"
    info = data_info(store.path, args.index, idx, seed, loader)
    info["store_complete"] = bool(store.complete)
    info["store_transitions"] = int(store.n_trans)
    args._store, args._idx = store, idx
    return it, info, (lambda: with_cost(data.OneStepBatches(store, idx, 256, cfg.seed + 17, device, num_workers=nw), store, device))


def main_train(args) -> None:
    device = torch.device("cuda")
    weights = json.loads(args.weights) if args.weights else None
    cfg = TrainConfig(size=args.size, mode=args.mode, samples=args.samples, batch_size=args.batch_size,
                      lr=args.lr, seed=args.seed, compile=not args.no_compile, init_from=args.init_from or "",
                      save_samples=tuple(int(s) for s in args.save_samples.split(",") if s),
                      sf_k=args.sf_k, sf_tf_ratio=args.sf_tf_ratio, resume_every_s=args.resume_every,
                      budget_weight=args.budget_weight, table_lr_mult=args.table_lr_mult, micro_batch=args.micro_batch,
                      model_overrides=json.loads(args.model_overrides) if args.model_overrides else {},
                      bk_updates=args.bk_updates, bk_batch=args.bk_batch)
    if weights:
        cfg.weights.update(weights)
    run_dir = Path(args.ckpt_root) / args.run
    latest = run_dir / "latest.pt"
    resumed_samples = 0
    if latest.exists():
        resumed_samples = int(torch.load(latest, map_location="cpu", weights_only=False)["samples"])
    it, info, norm_iter = make_batches(args, cfg, resumed_samples, device)
    stats = None
    if not latest.exists() and not cfg.init_from:
        t = time.time()
        stats = compute_norm_stats(norm_iter(), args.norm_batches)
        print(f"normalisation statistics from {int(stats['n'])} transitions in {time.time() - t:.1f}s", flush=True)
    book = None
    import dataclasses
    from dc.model import SIZES as _S
    mcfg = dataclasses.replace(_S[cfg.size], **{k: (tuple(v) if isinstance(v, list) else v) for k, v in cfg.model_overrides.items()})
    if cfg.init_from:
        mcfg = ModelConfig.from_dict(torch.load(cfg.init_from, map_location="cpu", weights_only=False)["model_config"])
    if mcfg.bookkeeping:
        from dc.train import BookData
        t = time.time()
        book = BookData.from_cache(args._store, args._idx, device, seed=cfg.seed)
        info["bookkeeping_data"] = book.info
        print(f"third-stage data: {book.n:,} rows of the run's index in {time.time() - t:.1f}s", flush=True)
    tr = Trainer(cfg, run_dir, device, data_info=info, norm_stats=stats if stats is not None else _stub_stats(),
                 book_data=book)
    if latest.exists():
        tr.resume(latest)
        tr.data_info = {**info, "resumed_at_samples": resumed_samples}
    print(f"run {args.run}: {cfg.size} {cfg.mode}, params {tr.model.num_parameters():,}, samples {tr.samples:,}"
          f" of {cfg.samples:,}, batch {cfg.batch_size}", flush=True)
    (run_dir / "config.json").write_text(json.dumps({"train": cfg.to_dict(), "model": tr.model.cfg.to_dict(),
                                                     "data": info, "argv": sys.argv}, indent=1))
    t0 = time.time()
    saved = tr.run(it)
    print(json.dumps({"done_samples": tr.samples, "steps": tr.step, "wall_s": round(time.time() - t0, 1),
                      "milestones": saved}, indent=1), flush=True)


def _stub_stats():
    """Placeholder statistics that let the Trainer build before resume() loads the real buffers."""
    from dc.engine import NUM_SCALARS
    return {"cond_mean": torch.zeros(NUM_SCALARS, dtype=torch.float64),
            "cond_std": torch.ones(NUM_SCALARS, dtype=torch.float64),
            "delta_scale": torch.ones(NUM_SCALARS, dtype=torch.float64), "n": torch.tensor(1)}


# ----------------------------------------------------------------------------------------------
# Throughput
# ----------------------------------------------------------------------------------------------
def _pool(device, trajs=1):
    pool = EnginePool.generate(CITIES, trajs_per_city=trajs, months=24, seed=0, device=device)
    return pool, compute_norm_stats(pool.all_batches(256), 100)


def bench_train(sizes, batch_size, steps, compile_, out, micro_batch: int = 0, mode: str = "onestep") -> None:
    device = torch.device("cuda")
    pool, stats = _pool(device)
    rows = []
    for size in sizes:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        cfg = TrainConfig(size=size, samples=10**12, batch_size=batch_size, compile=compile_, log_every=10**9,
                          resume_every_s=1e12, micro_batch=micro_batch, mode=mode, budget_weight=6.0,
                          table_lr_mult=10.0)
        tmp = tempfile.TemporaryDirectory(prefix="dc_bench_")
        tr = Trainer(cfg, Path(tmp.name), device, norm_stats=stats)
        it = pool.batches(batch_size, seed=1) if mode == "onestep" else pool.multistep_batches(batch_size, cfg.sf_k, seed=1)
        t = time.time()
        for _ in range(3):
            tr.train_step(next(it))
        torch.cuda.synchronize()
        warm = time.time() - t
        t = time.time()
        for _ in range(steps):
            tr.train_step(next(it))
        torch.cuda.synchronize()
        dt = time.time() - t
        sps = steps * batch_size / dt
        row = {"size": size, "mode": mode, "micro_batch": micro_batch, "params": tr.model.num_parameters(),
               "batch": batch_size, "compile": compile_,
               "steps_timed": steps, "samples_per_s": round(sps, 1), "hours_per_6M": round(6e6 / sps / 3600, 2),
               "warmup_s": round(warm, 1), "peak_mem_gb": round(torch.cuda.max_memory_allocated() / 2**30, 1)}
        print(json.dumps(row), flush=True)
        rows.append(row)
        del tr
        tmp.cleanup()
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps(rows, indent=1))


@torch.no_grad()
def bench_infer(sizes, batches, reps, compile_, max_batch, out) -> None:
    device = torch.device("cuda")
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    pool, stats = _pool(device)
    rows = []
    for size in sizes:
        m = build(size, device).eval()
        m.set_norm_stats(stats)
        if compile_:
            m.compile_trunk(dynamic=False)
        for B in batches:
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            s0, r, a, _ = pool.transition(torch.randint(pool.n, (B,), device=device))
            mb = min(B, max_batch) if max_batch else None
            while True:
                try:
                    t = time.time()
                    s = m.sample_next(s0, r, a, max_batch=mb)
                    s = m.sample_next(s, r, a, max_batch=mb)
                    torch.cuda.synchronize()
                    break
                except torch.OutOfMemoryError:
                    s = None
                    torch.cuda.empty_cache()
                    mb = (mb or B) // 2
                    print(f"out of memory at {size} batch {B}; chunking by {mb}", flush=True)
            warm = time.time() - t
            t = time.time()
            for _ in range(reps):
                s = m.sample_next(s, r, a, max_batch=mb)
            torch.cuda.synchronize()
            dt = time.time() - t
            row = {"size": size, "batch": B, "chunk": min(mb or B, m.safe_batch), "compile": compile_, "month_steps_timed": reps * B,
                   "city_months_per_s": round(reps * B / dt, 1), "warmup_s": round(warm, 1),
                   "peak_mem_gb": round(torch.cuda.max_memory_allocated() / 2**30, 1),
                   "changed_frac_last_step": round(float((s["tile_index"] != s0["tile_index"]).float().mean()), 4)}
            print(json.dumps(row), flush=True)
            rows.append(row)
        del m
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps(rows, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", default="50m", choices=[s for s in SIZES if s != "tiny"] + ["tiny"])
    ap.add_argument("--mode", default="onestep", choices=["onestep", "selfforce"])
    ap.add_argument("--samples", type=int, default=6_000_000)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--lr", type=float, default=8e-4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--run", default="")
    ap.add_argument("--ckpt-root", default=str(CKPT_ROOT))
    ap.add_argument("--data-root", default="", help="root of the stores (default dc.data.DATA_ROOT)")
    ap.add_argument("--index", default="train_full", help="split name for dc.data.open_split")
    ap.add_argument("--workers", type=int, default=6, help="loader worker processes")
    ap.add_argument("--save-samples", default="")
    ap.add_argument("--init-from", default="")
    ap.add_argument("--sf-k", type=int, default=4)
    ap.add_argument("--sf-tf-ratio", type=float, default=0.5)
    ap.add_argument("--weights", default="", help="JSON overrides of the loss weights")
    ap.add_argument("--micro-batch", type=int, default=0, help="accumulate each step in micro-batches of this size")
    ap.add_argument("--bk-updates", type=int, default=10, help="third stage: scalar-only updates per trunk step")
    ap.add_argument("--bk-batch", type=int, default=4096, help="third stage: rows per scalar-only update")
    ap.add_argument("--budget-weight", type=float, default=1.0, help="scalar-loss weight on budget-month transitions")
    ap.add_argument("--table-lr-mult", type=float, default=1.0, help="lr multiplier of the second stage's tables")
    ap.add_argument("--model-overrides", default="", help="JSON of ModelConfig fields to change")
    ap.add_argument("--norm-batches", type=int, default=200)
    ap.add_argument("--resume-every", type=float, default=600.0)
    ap.add_argument("--no-compile", action="store_true")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--synthetic-trajs", type=int, default=2)
    ap.add_argument("--bench-train", default="")
    ap.add_argument("--bench-infer", default="")
    ap.add_argument("--batches", default="256,1024,4096")
    ap.add_argument("--bench-steps", type=int, default=20)
    ap.add_argument("--max-batch", type=int, default=0, help="inference chunk size (0 = whole batch)")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    if args.bench_train:
        bench_train(args.bench_train.split(","), args.batch_size, args.bench_steps, not args.no_compile, args.out,
                    args.micro_batch, args.mode)
    elif args.bench_infer:
        bench_infer(args.bench_infer.split(","), [int(b) for b in args.batches.split(",")], args.bench_steps,
                    not args.no_compile, args.max_batch, args.out)
    else:
        if not args.run:
            ap.error("--run is required for training")
        main_train(args)


if __name__ == "__main__":
    main()
