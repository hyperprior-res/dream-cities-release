#!/usr/bin/env python
"""Behaviour cloning of the RL arm's policy from the offline training store .

    run_bc.py extract                                   # the demonstration extract (one process, gentle reads)
    run_bc.py train --seed 0 --device cuda:0            # one cloned policy per RL seed (0, 1, 2); resumable per epoch
    run_bc.py report                                    # the cloned policies' held-out numbers (markdown)
    run_bc.py table --scratch <runs> --warm <runs>      # warm start against the from-scratch learner (decision rule)

Outputs: ``<cache>/rl/bc/`` (``demos/`` the extract; ``bc_s<seed>.pt`` the cloned
policies, ``bc_s<seed>.latest.pt`` resumption) and ``results/rl/bc/`` (``extract_manifest.json``,
``bc_s<seed>.json`` and ``.log.jsonl``).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "hpr-dream"))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from dc import bc, rl  # noqa: E402

CACHE = Path(os.environ.get("WM2_BC_CACHE", "<cache>/rl/bc"))
RESULTS = Path(os.environ.get("WM2_RL_RESULTS", str(ROOT / "results" / "rl"))) / "bc"
RL_RESULTS = Path(os.environ.get("WM2_RL_RESULTS", str(ROOT / "results" / "rl")))


def log_to(path: Path):
    def f(msg):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
        print(line, flush=True)
        with open(path, "a") as fh:
            fh.write(line + "\n")
    return f


def cmd_extract(args) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    log = log_to(CACHE / "extract.log")
    man = bc.extract(CACHE / "demos", log=log)
    (RESULTS / "extract_manifest.json").write_text(json.dumps(man, indent=1))
    sel = man["selection"]
    log(f"demonstrations: {sel['kept_trajectories']:,} trajectories, {sel['kept_months_used']:,} months used; rows by "
        f"split {man['rows_by_split']}")


def cmd_train(args) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(args.threads)
    dev = torch.device(args.device)
    if dev.type == "cuda":                           # the policy's numerics in every RL run on a card (run_rl.py)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    log = log_to((Path(args.out_dir) if args.out_dir else CACHE) / f"bc_s{args.seed}.log")
    demos = bc.Demos(CACHE / "demos")
    cfg = bc.BC_FROZEN
    if args.config:                                  # a BCConfig other than BC_FROZEN, as JSON (fields to change)
        cfg = bc.BCConfig(**{**cfg.to_dict(), "policy": cfg.policy, **json.loads(args.config)})
    out = Path(args.out_dir) if args.out_dir else CACHE
    out.mkdir(parents=True, exist_ok=True)
    res = bc.train(demos, args.seed, out, device=dev, log=log, stop_after_epochs=args.stop_after_epochs,
                   chunk=args.chunk or None, cfg=cfg)
    if res.get("stopped"):
        return
    rdir = RESULTS / out.relative_to(CACHE) if out != CACHE else RESULTS
    rdir.mkdir(parents=True, exist_ok=True)
    shutil.copy(out / f"bc_s{args.seed}.json", rdir / f"bc_s{args.seed}.json")
    shutil.copy(out / f"bc_s{args.seed}.log.jsonl", rdir / f"bc_s{args.seed}.log.jsonl")
    h = res["heldout"]
    log(f"bc s{args.seed}: kept epoch {res['kept_epoch']}; held-out log-likelihood per month {h['loglik_per_month']:.4f} "
        f"(initial policy {res['heldout_initial_policy']['loglik_per_month']:.4f}); month has a macro: sampled "
        f"{h['month_has_macro_sampled']:.3f}, demonstrated {h['month_has_macro_demo']:.3f}")


def cmd_report(args) -> None:
    rd = RESULTS / (args.out_dir or "cfg2")
    R = {s: json.loads((rd / f"bc_s{s}.json").read_text()) for s in (0, 1, 2) if (rd / f"bc_s{s}.json").exists()}
    if not R:
        print("no cloned policies")
        return
    print(f"cloned policies in {rd} (configuration: {json.dumps({k: v for k, v in next(iter(R.values()))['meta']['cfg'].items() if k != 'policy'})})\n")
    print("| quantity | " + " | ".join(f"seed {s}" for s in R) + " | initial policy (seed 0) |")
    print("|---|" + "---|" * (len(R) + 1))
    first = next(iter(R.values()))
    rows = [("kept epoch (best validation)", lambda r: f"{float(r['kept_epoch']):.3f}", None),
            ("held-out log-likelihood per month (nats)", lambda r: f"{r['heldout']['loglik_per_month']:.3f}",
             lambda r: f"{r['heldout_initial_policy']['loglik_per_month']:.3f}"),
            ("validation log-likelihood per month", lambda r: f"{r['val']['loglik_per_month']:.3f}", None),
            ("held-out: month has a macro, sampled", lambda r: f"{r['heldout']['month_has_macro_sampled']:.3f}",
             lambda r: f"{r['heldout_initial_policy']['month_has_macro_sampled']:.3f}"),
            ("held-out: month has a macro, demonstrated", lambda r: f"{r['heldout']['month_has_macro_demo']:.3f}", None),
            ("held-out: macros per month, sampled", lambda r: f"{r['heldout']['macros_per_month_sampled']:.3f}",
             lambda r: f"{r['heldout_initial_policy']['macros_per_month_sampled']:.3f}"),
            ("held-out: macros per month, demonstrated", lambda r: f"{r['heldout']['macros_per_month_demo']:.3f}", None)]
    for label, f, g in rows:
        print(f"| {label} | " + " | ".join(f(r) for r in R.values()) + f" | {g(first) if g else '-'} |")
    print("\nvalidation log-likelihood per month during training (the kept weights: the highest)\n")
    for sd, r in R.items():
        print(f"seed {sd}: " + ", ".join(f"{h['epoch']:.2f}: {h['val_loglik_per_month']:.2f}" for h in r["history"]))
    print("\nheld-out log-likelihood per head (nats, rows that use the head; arg-max accuracy in brackets)\n")
    print("| head | rows | " + " | ".join(f"seed {s}" for s in R) + " | initial policy (seed 0) |")
    print("|---|---|" + "---|" * (len(R) + 1))
    for h in bc.HEAD_NAMES:
        ph = first["heldout"]["per_head"][h]
        print(f"| {h} | {ph['rows_used']:,} | " + " | ".join(
            f"{r['heldout']['per_head'][h]['loglik']:.3f} ({r['heldout']['per_head'][h]['argmax_accuracy']:.2f})"
            for r in R.values()) + f" | {first['heldout_initial_policy']['per_head'][h]['loglik']:.3f} |")


# ----------------------------------------------------------------------------------------------
# the decision table: warm start against the from-scratch learner, paired over instances
# ----------------------------------------------------------------------------------------------
def per_instance(run: str, months: int, key: str = "engine_open_accepts") -> dict:
    """{instance: mean over its sampled plans of ``key``} from a run's evaluation records at ``months``. ``run`` may
    name several runs joined by '+' (seeds of one learner): then the mean over the runs of each instance's value, so a
    bootstrap over instances keeps an instance's seeds together; every run must hold the same instances."""
    if "+" in run:
        parts = [per_instance(r, months, key) for r in run.split("+")]
        if any(set(q) != set(parts[0]) for q in parts):
            raise ValueError(f"{run}: the runs hold different instances")
        return {k: float(np.mean([q[k] for q in parts])) for k in parts[0]}
    p = RL_RESULTS / run / f"eval3_{months:09d}.jsonl"
    return {r["instance"]: float(np.mean(r[key])) for r in (json.loads(x) for x in p.read_text().splitlines() if x.strip())}


def has_eval(run: str, months: int) -> bool:
    return all((RL_RESULTS / r / f"eval3_{months:09d}.jsonl").exists() for r in run.split("+"))


def paired(a: dict, b: dict, n_boot: int = 2000, seed: int = 0) -> dict:
    """Mean of a - b over the instances both hold, with the 95 per cent percentile interval of 2,000 bootstrap
    resamples of the instances (part B's convention)."""
    keys = sorted(set(a) & set(b))
    d = np.array([a[k] - b[k] for k in keys])
    rng = np.random.default_rng(seed)
    bs = d[rng.integers(0, len(d), size=(n_boot, len(d)))].mean(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"n": len(keys), "mean": float(d.mean()), "lo": float(lo), "hi": float(hi)}


def cmd_table(args) -> None:
    sys.path.insert(0, str(ROOT / "code" / "scripts"))
    import run_rl
    scratch = dict(x.split("=") for x in args.scratch.split(","))      # family=run
    warm = dict(x.split("=") for x in args.warm.split(","))
    tf = run_rl.tasks_path(args.tasks)
    months = [int(m) for m in args.months.split(",")]
    final = max(months)
    out = {"months": months, "families": {}}
    args_scratch_beside = dict(x.split("=") for x in args.beside_scratch.split(",")) if args.beside_scratch else {}
    beside = dict(x.split("=") for x in args.beside.split(",")) if args.beside else {}   # family=run of another learner
    print("| family | instances | seeds | from scratch, 1,000,000 | " + " | ".join(f"{args.label}, {m:,}" for m in months)
          + f" | {args.label} minus scratch at 1,000,000 [95 % interval] | "
          + (f"{args.beside_label}, 1,000,000 | {args.beside_label} minus scratch [95 % interval] | " if beside else "")
          + "behaviour pool | builder pool | source c | search 1,000 (behaviour) | search 1,000 (builders) |")
    print("|---|---|---|---|" + "---|" * len(months) + "---|" + ("---|---|" if beside else "") + "---|---|---|---|---|")
    for fam in warm:
        s = per_instance(scratch[fam], final)
        w = {m: per_instance(warm[fam], m) for m in months if has_eval(warm[fam], m)}
        d = paired(w[final], s) if final in w else None
        y = run_rl.yardsticks(tf, fam)
        out["families"][fam] = {"scratch_run": scratch[fam], "warm_run": warm[fam], "n": len(s),
                                "scratch": float(np.mean(list(s.values()))),
                                "warm": {m: float(np.mean(list(v.values()))) for m, v in w.items()}, "paired": d,
                                "yardsticks": y}
        cells = [f"{np.mean(list(w[m].values())):.3f}" if m in w else "-" for m in months]
        dd = f"{d['mean']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}]" if d else "-"
        bb = ""
        if beside:
            sb = per_instance(args_scratch_beside.get(fam, scratch[fam]), final)
            b = per_instance(beside[fam], final)
            pb = paired(b, sb)
            out["families"][fam]["beside"] = {"run": beside[fam], "scratch_run": args_scratch_beside.get(fam, scratch[fam]),
                                              "rate": float(np.mean(list(b.values()))), "paired": pb}
            bb = f"{np.mean(list(b.values())):.3f} | {pb['mean']:+.3f} [{pb['lo']:+.3f}, {pb['hi']:+.3f}] | "
        ns = len(warm[fam].split("+"))
        if ns != len(scratch[fam].split("+")):
            raise ValueError(f"{fam}: {ns} seeds of the learner, {len(scratch[fam].split('+'))} from scratch")
        out["families"][fam]["seeds"] = ns
        print(f"| {fam} | {len(s)} | {ns} | {np.mean(list(s.values())):.3f} | " + " | ".join(cells) + f" | {dd} | " + bb
              + " | ".join("-" if y[k] is None else f"{y[k]:.3f}" for k, _ in run_rl.YARDSTICKS) + " |")
    ds = [v["paired"] for v in out["families"].values() if v["paired"]]
    above = sum(d["lo"] > 0 for d in ds)
    below = sum(d["hi"] < 0 for d in ds)
    out["rule"] = {"families_compared": len(ds), "interval_above_zero": above, "interval_below_zero": below,
                   "primary": bool(len(ds) == 5 and above >= 3 and below == 0)}
    print(f"\ndecision rule (fixed in the brief): interval above 0 in {above} of {len(ds)} families, below 0 in {below}; "
          + (f"the {args.label} learner becomes primary" if out["rule"]["primary"] else
             "the rule is not met" if len(ds) == 5 else "not all five families yet"))
    if args.out:
        Path(args.out).write_text(json.dumps(out, indent=1))


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["extract", "train", "report", "table"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--stop-after-epochs", type=int, default=None)
    ap.add_argument("--config", default="", help='train: BCConfig fields to change, JSON (e.g. {"epochs": 2})')
    ap.add_argument("--out-dir", default="", help="train: output directory under the cache (default: the cache)")
    ap.add_argument("--chunk", type=int, default=0, help="train: rows per forward/backward pass (0: the whole batch); "
                    "memory on the card only")
    ap.add_argument("--scratch", default="", help="table: family=run of the from-scratch learner, comma-separated")
    ap.add_argument("--warm", default="", help="table: family=run of the warm-started learner, comma-separated")
    ap.add_argument("--months", default="0,250000,500000,1000000")
    ap.add_argument("--label", default="warm start", help="table: name of the --warm learner")
    ap.add_argument("--beside", default="", help="table: family=run of another learner shown beside (1,000,000 months)")
    ap.add_argument("--beside-label", default="clone everything (round 3)")
    ap.add_argument("--beside-scratch", default="", help="table: family=run of the scratch learner the --beside runs "
                    "are compared with, where it differs from --scratch")
    ap.add_argument("--tasks", default="data/tasks_v2_H24.json")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    {"extract": cmd_extract, "train": cmd_train, "report": cmd_report, "table": cmd_table}[args.cmd](args)


if __name__ == "__main__":
    main()
