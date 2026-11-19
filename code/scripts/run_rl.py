#!/usr/bin/env python
"""One PPO run of the RL arm (``dc.rl``): train, snapshot, evaluate every snapshot against the engine.

    # inside an emulator checkpoint (the arm's runs; GPU)
    run_rl.py train --env emulator --ckpt <ckpt.pt> --model-src ladder-v2 --task grow --seed 0 --device cuda:0
    # PPO with the real engine as the environment (engine on CPU worker processes; policy and update on --device)
    run_rl.py train --env engine --task power --seed 0 --budget 1000000 --workers 8 --device cuda:0
    # evaluate snapshots that have no records yet (also runs after ``train`` unless --no-eval)
    run_rl.py eval --env emulator --ckpt <ckpt.pt> --task grow --seed 0 --device cuda:0

Settings: ``dc.rl.FROZEN`` (n_envs, rollout length, PPO, policy). ``--budget`` and ``--snapshots`` may be set
(small runs); a budget other than the frozen one is part of the run's name. Everything else is frozen.

Tasks file: ``--tasks`` (default ``data/tasks_v2_H24.json``, amendment 3). Its stem is part of the run's name, and the run's
config records its path and sha256 and the sha256 of ``dc/tasks.py``; a run is never resumed or evaluated after
either changed. Runs made before ``--tasks`` existed (their config records no tasks file; they read
``data/tasks_H24.json``, the only file then) keep their untagged names and are found under them.

Model code: ``--model-src`` (default ``ladder-v2``); a run is evaluated only with the model code it trained with.

Learner: ``--variant`` (default ``frozen``, ``dc.rl.FROZEN``; otherwise a name in ``dc.rl.VARIANTS``, part of the
run name). Engine runs on a GPU: ``--device cuda:0 --buffer host --update-chunk 250`` keeps the card's footprint
under 2 GB without changing any number but rounding.

Evaluation: the analysis plan under amendment 3 (``dc.rl.evaluate_snapshot``): per instance 8 sampled dream episodes,
their plans judged by the oracle (majority over 32 dedicated seeds), the audit's verdict on plan 0, 8 sampled
closed-loop episodes on fresh seeds, the greedy plan at the final snapshot. Records
``results/rl/<run>/eval3_<months>.jsonl`` and ``.summary.json``; arrays and the saved phases (an interrupted
evaluation resumes from them) under the cache directory. Earlier records (``eval2_*``: round 2 part A, single
seed; ``eval_*``: the rules) are left as they are; ``report`` prints them separately.

``compare --runs a,b,...``: the tuning table (oracle pass rate, mean margin, closed-loop pass share at each
snapshot; entropy and approximate KL over training) beside the family's yardsticks from the tasks file
(``base_rates32``).

``--profile`` synchronises the per-part timers with the GPU (otherwise no synchronisation is added; no number of
a run depends on it).

Outputs: ``<cache>/rl/<run>/`` (latest.pt, snap_*.pt, log.jsonl, eval3_*/ phases,
eval3_*.npz, DONE.json once every snapshot is evaluated) and ``results/rl/<run>/`` (config.json, log.jsonl,
eval3_<months>.jsonl records and summaries, summary_eval3.json).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "hpr-dream"))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from dc import rl, rl_adaptor as RA  # noqa: E402

CACHE = Path(os.environ.get("WM2_RL_CACHE", "<cache>/rl"))
RESULTS = Path(os.environ.get("WM2_RL_RESULTS", str(ROOT / "results" / "rl")))
DEFAULT_TASKS = "data/tasks_v2_H24.json"           # amendment 3
LEGACY_TASKS = ROOT / "data" / "tasks_H24.json"    # the tasks file of every run made before --tasks existed


def ckpt_tag(ckpt: str) -> str:
    p = Path(ckpt)
    return f"{p.parent.name}-{p.stem}"


def tasks_path(tasks: str) -> Path:
    p = Path(tasks)
    return (p if p.is_absolute() else ROOT / p).resolve()


def name_for(env: str, ckpt: str, task: str, seed: int, budget: int, tasks, variant: str = "frozen") -> str:
    """A run's name: environment or checkpoint, family, RL seed, the budget when it is not the frozen one, the
    tasks file's stem (``tasks`` None: the untagged name of a run made before ``--tasks`` existed) and the learner
    variant when it is not the frozen one."""
    if env == "engine":
        base = f"engine__{task}__s{seed}"
    elif env == "stub":
        base = f"stub__{task}__s{seed}"
    else:
        base = f"{ckpt_tag(ckpt)}__{task}__s{seed}"
    if int(budget) != rl.FROZEN.budget:
        base += f"__b{int(budget)}"
    if tasks is not None:
        base += f"__{Path(tasks).stem}"
    if variant != "frozen":
        base += f"__v-{variant}"
    return base


def run_name(args, cfg: rl.RLConfig) -> str:
    return name_for(args.env, args.ckpt, args.task, args.seed, cfg.budget, tasks_path(args.tasks), args.variant)


def resolve_run_name(args, cfg: rl.RLConfig):
    """(name, legacy): the tagged name, or the untagged name of a run made before ``--tasks`` existed when that run
    exists, its config records no tasks file and ``--tasks`` is the file it read."""
    name = run_name(args, cfg)
    legacy = name_for(args.env, args.ckpt, args.task, args.seed, cfg.budget, None)
    if args.variant != "frozen" or (RESULTS / name / "config.json").exists() or not (RESULTS / legacy / "config.json").exists():
        return name, False
    old = json.loads((RESULTS / legacy / "config.json").read_text())
    if "tasks_sha256" in old.get("meta", {}) or tasks_path(args.tasks) != LEGACY_TASKS.resolve():
        return name, False
    return legacy, True


def check_config(old: dict, new: dict, cmd: str, legacy: bool) -> None:
    """Refuse to resume or evaluate a run under another configuration, tasks file, predicate code, checkpoint or
    model code (and, for training, on another kind of device)."""
    o, m = old["meta"], new["meta"]
    errs = []
    if not rl.RLConfig.from_dict(old["cfg"]).same_learner(rl.RLConfig.from_dict(new["cfg"])):
        errs.append("PPO / policy configuration")
    if o.get("init_bias_sha256") != m.get("init_bias_sha256"):
        errs.append("initial head biases")
    if (cmd == "train" or m.get("init_policy_sha256") is not None) and o.get("init_policy_sha256") != m.get("init_policy_sha256"):
        errs.append(f"initial policy (the run: {o.get('init_policy_sha256')}, now: {m.get('init_policy_sha256')})")
    if legacy:
        if m["tasks_file"] != os.path.relpath(LEGACY_TASKS, ROOT):
            errs.append(f"tasks file (the run read {os.path.relpath(LEGACY_TASKS, ROOT)})")
    else:
        for k in ("tasks_sha256", "tasks_code_sha256"):
            if o.get(k) != m.get(k):
                errs.append(f"{k} (the run: {o.get(k)}, now: {m.get(k)})")
    for k in ("environment", "task", "rl_seed"):
        if o.get(k) != m.get(k):
            errs.append(f"{k} (the run: {o.get(k)}, now: {m.get(k)})")
    # the checkpoint by its sha256 when both record one (a run trained on another machine), else by its path
    ck = "checkpoint_sha256" if o.get("checkpoint_sha256") and m.get("checkpoint_sha256") else "checkpoint"
    if o.get(ck) != m.get(ck):
        errs.append(f"{ck} (the run: {o.get(ck)}, now: {m.get(ck)})")
    if m["environment"] == "emulator" and o.get("model_src") != m.get("model_src"):
        errs.append(f"model code (the run trained with {o.get('model_src')}, --model-src is {m.get('model_src')})")
    if cmd == "train" and "numerics" in o:
        if torch.device(o["numerics"]["device"]).type != torch.device(m["numerics"]["device"]).type:
            errs.append(f"device kind (the run: {o['numerics']['device']}, now: {m['numerics']['device']})")
    if errs:
        raise RuntimeError("this run was made under another " + "; ".join(errs))


def make_cfg(args) -> rl.RLConfig:
    if args.variant != "frozen" and args.variant not in rl.VARIANTS:
        raise SystemExit(f"--variant {args.variant!r}: one of frozen, {', '.join(rl.VARIANTS)}")
    init_from = bool(getattr(args, "init_from", ""))
    if init_from and args.variant not in rl.INIT_VARIANTS:
        raise SystemExit(f"--init-from is for --variant {', '.join(rl.INIT_VARIANTS)} only")
    if args.cmd == "train" and args.variant in rl.INIT_VARIANTS and not init_from:
        raise SystemExit(f"--variant {args.variant} trains from a cloned policy: --init-from is required")
    cfg = rl.FROZEN if args.variant == "frozen" else rl.VARIANTS[args.variant]
    if args.budget:
        cfg = replace(cfg, budget=int(args.budget))
    if args.snapshots:
        cfg = replace(cfg, snapshots=tuple(int(x) for x in args.snapshots.split(",")))
    elif args.budget:
        cfg = replace(cfg, snapshots=(int(args.budget),))
    cfg.check()
    return cfg


def init_bias(instances, cfg: rl.RLConfig) -> tuple:
    plans = np.concatenate([RA.behaviour_plans(i.start_id, cfg.init_plans).reshape(-1, rl.N_COLS)
                            for i in sorted({i.start_id: i for i in instances}.values(), key=lambda i: i.start_id)])
    b = rl.behaviour_head_bias(plans, cfg.init_mix)
    import hashlib
    return b, {"init_rows": int(plans.shape[0]), "init_bias_sha256": hashlib.sha256(b.tobytes()).hexdigest()[:16]}


def init_policy(args, cfg: rl.RLConfig) -> tuple:
    """The cloned policy of ``--init-from`` (``dc.bc.load_cloned``: same policy configuration, task-dependent input
    weights zero), cloned with the run's RL seed; its weights and what the run's config records about it."""
    from dc import bc
    state, bmeta = bc.load_cloned(args.init_from, cfg.policy)
    if int(bmeta["meta"]["seed"]) != int(args.seed):
        raise SystemExit(f"--init-from {args.init_from}: cloned with seed {bmeta['meta']['seed']}, the RL seed is {args.seed}")
    pol = rl.Policy(cfg.policy)
    pol.load_state_dict(state)
    ho = bmeta.get("heldout", {})
    return state, {"init_from": str(Path(args.init_from).resolve()), "init_policy_sha256": rl.policy_sha256(pol),
                   "init_from_bc": {"seed": int(bmeta["meta"]["seed"]), "kept_epoch": bmeta.get("kept_epoch"),
                                    "extract_manifest_sha256": bmeta["meta"]["extract_manifest_sha256"],
                                    "heldout_loglik_per_month": ho.get("loglik_per_month")}}


def policy_numerics_on(device: torch.device) -> None:
    """The policy's numerics on a GPU without an emulator: TF32 for matmuls and convolutions, as the audit judge
    sets them in every emulator run (the policy shares the process). cuDNN autotuning stays off."""
    if device.type == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True


def numerics(device) -> dict:
    return {"device": str(device), "torch": torch.__version__,
            "tf32_matmul": bool(torch.backends.cuda.matmul.allow_tf32), "tf32_cudnn": bool(torch.backends.cudnn.allow_tf32),
            "cudnn_benchmark": bool(torch.backends.cudnn.benchmark)}


def make_emulator(args, cdir: Path = None):
    """The emulator backend (or the stub's), or None for the engine environment; and the policy's device. On the
    engine side of a split evaluation (``--eval-side engine``) the emulator is the identity recorded by the emulator
    side (``<cache>/<run>/emulator.json``), and the checkpoint file need not exist."""
    if args.env == "engine":
        dev = torch.device(args.device or "cpu")
        policy_numerics_on(dev)
        return None, dev
    if args.env == "stub":
        return rl.StubEmulator("cpu"), torch.device("cpu")
    if getattr(args, "eval_side", "both") == "engine":
        p = cdir / EMULATOR_JSON
        if not p.exists():
            raise SystemExit(f"{p}: missing (the emulator side writes it)")
        dev = torch.device(args.device or "cuda:0")
        policy_numerics_on(dev)
        return rl.RecordedEmulator(json.loads(p.read_text())), dev
    emu = RA.EmulatorBackend(args.ckpt, device=args.device or "cuda:0", model_src=args.model_src,
                             compile_trunk=args.compile)
    return emu, emu.device


def make_train_backend(args, emu, n: int, device):
    if args.env == "engine":
        return rl.EngineEnv(n, workers=args.workers, device="cpu")     # packed on the host; the trainer moves them
    if args.env == "stub":
        return rl.StubEnv(emu, n)
    return rl.EmuEnv(emu, n, profile=args.profile)


def log_to(path: Path):
    def f(msg):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
        print(line, flush=True)
        with open(path, "a") as fh:
            fh.write(line + "\n")
    return f


EVAL_PREFIX = f"eval{rl.EVAL_VERSION}_"
EMULATOR_JSON = "emulator.json"            # the emulator's identity, written by the emulator side of a split evaluation
DONE_EMULATOR = "DONE_emulator.json"       # the emulator side of every snapshot is saved (with the files to carry home)


def emulator_side_files(cdir: Path, rdir: Path, cfg) -> list:
    """What the engine side of a split evaluation reads: the run's config and log, the snapshots, the emulator's
    identity and every saved emulator phase (the dream episodes and their plans, the audit's samples of plan 0, the
    greedy plan in the emulator)."""
    fs = [rdir / "config.json", rdir / "log.jsonl", cdir / EMULATOR_JSON]
    fs += [cdir / f"snap_{m:09d}.pt" for m in sorted(cfg.snapshots)]
    for m in sorted(cfg.snapshots):
        fs += sorted((cdir / f"{EVAL_PREFIX}{m:09d}").glob("*.npz"))
    return fs


def evaluate_run(args, cfg, name, instances, emu, device, log, digest, cdir: Path, rdir: Path, n_oracle: int) -> dict:
    side = getattr(args, "eval_side", "both")
    if side == "emulator":
        return evaluate_emulator_side(args, cfg, name, instances, emu, device, log, cdir, rdir, n_oracle)
    engine = RA.engine_judge(workers=args.eval_workers, log=log)
    final = max(cfg.snapshots)
    out = {}
    try:
        for months in sorted(cfg.snapshots):
            tag = f"{EVAL_PREFIX}{months:09d}"
            rec_path = rdir / f"{tag}.jsonl"
            if rec_path.exists():
                out[months] = json.loads((rdir / f"{tag}.summary.json").read_text())
                continue
            snap = cdir / f"snap_{months:09d}.pt"
            if not snap.exists():
                raise FileNotFoundError(snap)
            pol, ck = rl.load_snapshot(snap, device)
            assert ck["months"] == months, (ck["months"], months)
            ec0 = engine.counters()
            jc0 = emu.judge_counters() if hasattr(emu, "judge_counters") else {}
            t0 = time.time()
            recs, extra = rl.evaluate_snapshot(pol, instances, engine, run_key=ck["run_key"], months=months,
                                               device=device, emu=emu, final=(months == final), out_dir=cdir / tag,
                                               closed_workers=args.eval_workers, n_oracle=n_oracle,
                                               side="engine" if side == "engine" else "both",
                                               tax_cap=bool(cfg.mask_treasury_tax))
            ec1 = engine.counters()
            jc1 = emu.judge_counters() if hasattr(emu, "judge_counters") else {}
            for r in recs:
                r.update({"run": name, "checkpoint": args.ckpt if args.env == "emulator" else None,
                          "rl_seed": int(args.seed), "tasks_file": digest["tasks_file"]})
            np.savez_compressed(cdir / f"{tag}.npz", **extra["arrays"])
            summ = rl.summarise(recs)
            summ.update({"months": months, "final_snapshot": months == final, "run_key": ck["run_key"],
                         "eval_cfg": rl.EVAL_FROZEN.to_dict(), "eval_tag": extra["tag"],
                         "phases_resumed": extra["phases_resumed"], "seconds": extra["seconds"],
                         "wall_s_this_invocation": time.time() - t0, "measured_counts": extra["counts"],
                         "engine_counters": {k: ec1[k] - ec0.get(k, 0) for k in ec1},
                         "emulator_judge_counters": {k: jc1[k] - jc0.get(k, 0) for k in jc1},
                         "tasks": digest, "numerics": numerics(device),
                         "emulator": emu.describe() if emu is not None else None})
            tmp = rec_path.with_name(rec_path.name + ".tmp")
            tmp.write_text("".join(json.dumps(r) + "\n" for r in recs))
            (rdir / f"{tag}.summary.json").write_text(json.dumps(summ, indent=1, default=str))
            os.replace(tmp, rec_path)
            out[months] = summ
            log(f"eval {months}: " + json.dumps({k: summ.get(k) for k in (
                "rate_dream_accept", "rate_engine_open_accept", "mean_engine_open_share", "rate_engine_closed_accept",
                "mean_dream_margin", "mean_engine_open_margin", "mean_engine_closed_margin", "inflation_open",
                "plan0_hackability", "closed_loop_replay_equal")}))
    finally:
        engine.close()
    return out


def evaluate_emulator_side(args, cfg, name, instances, emu, device, log, cdir: Path, rdir: Path, n_oracle: int) -> dict:
    """The emulator side of a split evaluation (a rented card): every snapshot's emulator phases saved under
    ``<cache>/<run>/eval3_<months>/``, the emulator's identity in ``emulator.json``, and ``DONE_emulator.json`` listing
    the files the engine side reads with their sha256. No engine replay."""
    if args.env != "emulator":
        raise SystemExit("--eval-side emulator is for runs in the emulator")
    (cdir / EMULATOR_JSON).write_text(json.dumps(emu.describe(), indent=1, default=str))
    final = max(cfg.snapshots)
    secs = {}
    for months in sorted(cfg.snapshots):
        tag = f"{EVAL_PREFIX}{months:09d}"
        pol, ck = rl.load_snapshot(cdir / f"snap_{months:09d}.pt", device)
        assert ck["months"] == months, (ck["months"], months)
        t0 = time.time()
        _, extra = rl.evaluate_snapshot(pol, instances, None, run_key=ck["run_key"], months=months, device=device,
                                        emu=emu, final=(months == final), out_dir=cdir / tag, n_oracle=n_oracle,
                                        side="emulator", tax_cap=bool(cfg.mask_treasury_tax))
        secs[months] = {"phases": extra["seconds"], "resumed": extra["phases_resumed"], "wall_s": time.time() - t0}
        log(f"eval {months} (emulator side): phases saved {sorted(extra['seconds'])}, resumed {extra['phases_resumed']}")
    files = emulator_side_files(cdir, rdir, cfg)
    missing = [str(f) for f in files if not f.exists()]
    if missing:
        raise RuntimeError(f"emulator side incomplete: {missing}")
    import hashlib
    sha = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    (cdir / DONE_EMULATOR).write_text(json.dumps({"run": name, "eval_version": rl.EVAL_VERSION, "seconds": secs,
                                                  "files": sha, "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                                                 indent=1))
    return {}


EVAL3_ROWS = [
    ("rate_dream_accept", "dream accept (own trajectory)"),
    ("rate_engine_open_accept", "oracle accept, open loop (same plans; 16 of 32 seeds)"),
    ("mean_engine_open_share", "oracle pass share, open loop"),
    ("mean_engine_open_margin", "engine margin open (mean over oracle seeds)"),
    ("rate_engine_open_seed0_accept", "oracle seed 0 alone: accept"),
    ("rate_engine_closed_accept", "closed loop: pass share (fresh seeds)"),
    ("mean_engine_closed_margin", "closed loop: margin"),
    ("mean_dream_margin", "dream margin"),
    ("mean_start_margin", "start margin"),
    ("inflation_open", "inflation open"),
    ("verdict_gap_open", "verdict gap open"),
    ("inflation_closed", "inflation closed"),
    ("verdict_gap_closed", "verdict gap closed"),
    ("rate_plan0_audit_accept", "plan 0: audit accept (4 of 8 samples)"),
    ("mean_plan0_audit_margin", "plan 0: audit margin (mean of 8)"),
    ("rate_plan0_engine_open_accept", "plan 0: oracle accept"),
    ("plan0_hackability", "plan 0: audit accepts, oracle rejects"),
    ("rate_engine_open_accept_in_band", "oracle accept, in-band (well-posed) instances"),
    ("dream_macros_per_month", "macros per month, dream plans"),
    ("closed_macros_per_month", "macros per month, closed-loop plans"),
    ("closed_loop_replay_equal", "closed loop = replay"),
    ("rate_greedy_imagined_accept", "greedy: emu accept (8 samples)"),
    ("rate_greedy_engine_open_accept", "greedy: oracle accept"),
    ("mean_greedy_engine_open_margin", "greedy: engine margin (mean over oracle seeds)"),
    ("rate_greedy_engine_closed_accept", "greedy: closed loop accept"),
    ("greedy_inflation_open", "greedy: inflation open"),
    ("greedy_macros_per_month", "greedy: macros per month"),
    ("greedy_closed_loop_replay_equal", "greedy: closed loop = replay"),
]
EVAL2_ROWS = [
    ("rate_dream_accept", "dream accept (own trajectory)"),
    ("rate_engine_open_accept", "engine accept open, primary (same plans)"),
    ("rate_engine_closed_accept", "engine accept closed"),
    ("mean_engine_open_margin", "engine margin open"),
    ("mean_engine_closed_margin", "engine margin closed"),
    ("mean_start_margin", "start margin"),
    ("inflation_open", "inflation open"),
    ("rate_plan0_engine_open_accept", "plan 0: engine accept, primary"),
    ("rate_plan0_engine_secondary_accept", "plan 0: engine accept, 8 secondary"),
    ("closed_macros_per_month", "macros per month, closed-loop plans"),
    ("closed_loop_replay_equal", "closed loop = replay"),
    ("rate_greedy_engine_open_accept", "greedy: engine accept open, primary"),
]
LEGACY_ROWS = [
    ("rate_imagined_accept", "emu accept (8 samples)"), ("rate_engine_open_accept", "engine accept open, primary"),
    ("rate_engine_open_accept_secondary", "engine accept open, 8 secondary"),
    ("rate_engine_closed_accept", "engine accept closed"), ("mean_imagined_margin", "imagined margin"),
    ("mean_engine_open_margin", "engine margin open"), ("mean_engine_closed_margin", "engine margin closed"),
    ("mean_start_margin", "start margin"), ("inflation_open", "inflation open"),
    ("verdict_gap_open", "verdict gap open"), ("inflation_closed", "inflation closed"),
    ("closed_loop_replay_equal", "closed loop = replay")]


def _table(S, rows) -> None:
    print("\n| quantity | " + " | ".join(f"{d['months']:,} months" for d in S) + " |")
    print("|---|" + "---|" * len(S))
    for k, label in rows:
        vals = [d.get(k) for d in S]
        if all(v is None for v in vals):
            continue
        print(f"| {label} | " + " | ".join("-" if v is None else (v if isinstance(v, str) else f"{v:.3f}") for v in vals) + " |")


def report(rdir: Path) -> None:
    """Markdown tables of a run: training curve (about 12 rows), every snapshot's decision-34 evaluation, and any
    legacy evaluations of the rules."""
    lines = [json.loads(x) for x in (rdir / "log.jsonl").read_text().splitlines() if x.strip()]
    print(f"run {rdir.name}: {len(lines)} iterations, {lines[-1]['months'] if lines else 0} months")
    print("\n| iteration | months | episodes | in-loop accept (sampled policy) | mean final margin | entropy | approx KL |")
    print("|---|---|---|---|---|---|---|")
    step = max(1, len(lines) // 12)
    for d in lines[step - 1::step]:
        fmt = lambda v: "-" if v is None else f"{v:.3f}"
        print(f"| {d['iteration']} | {d['months']:,} | {d['episodes_total']:,} | {fmt(d['accept_rate_in_loop'])} | "
              f"{fmt(d['final_margin_mean'])} | {d['entropy']:.2f} | {d['approx_kl']:.4f} |")
    if lines:
        sec = {k: sum(d["seconds"][k] for d in lines) for k in lines[0]["seconds"]}
        tot = sum(sec.values())
        syn = all(d.get("timers_synchronised", True) for d in lines)
        print("\ntraining seconds" + ("" if syn else " (timers not synchronised with the GPU)") + ": "
              + ", ".join(f"{k} {v:.1f} ({100 * v / tot:.0f} %)" for k, v in sec.items())
              + f"; total {tot:.1f}; months/s {lines[-1]['months'] / tot:.1f}")
    S = [json.loads(p.read_text()) for p in sorted(rdir.glob("eval3_*.summary.json"))]
    print("\nsnapshot evaluations ")
    if S:
        _table(S, EVAL3_ROWS)
    S2 = [json.loads(p.read_text()) for p in sorted(rdir.glob("eval2_*.summary.json"))]
    if S2:
        print("\nearlier evaluations (the analysis plan under the single-seed verdict, round 2 part A)")
        _table(S2, EVAL2_ROWS)
    for rule, pick in (("greedy", lambda p: p.name.count(".") == 2), ("sample", lambda p: ".sample." in p.name)):
        L = [json.loads(p.read_text()) for p in sorted(rdir.glob("eval_*.summary.json")) if pick(p)]
        if L:
            print(f"\nlegacy evaluations , plan rule: {rule}")
            _table(L, LEGACY_ROWS)


YARDSTICKS = (("behaviour", "behaviour pool"), ("builders", "builder pool"),
              ("c", "scripted builders under the best constant settings (source c)"),
              ("cem_behaviour_1000", "engine-side search, 1,000 evaluations (behaviour-pool start)"),
              ("cem_builders_1000", "engine-side search, 1,000 evaluations (builder-pool start)"))


def yardsticks(tasks_file: Path, task: str) -> dict:
    """Mean over the family's instances of the tasks file's ``base_rates32`` (pass shares under the oracle)."""
    d = json.loads(tasks_file.read_text())
    I = [r for r in d["instances"] if r["task"] == task and int(r["horizon"]) == 24]
    out = {"n_instances": len(I)}
    for k, _ in YARDSTICKS:
        v = [r["base_rates32"][k] for r in I if "base_rates32" in r and k in r["base_rates32"]]
        out[k] = float(np.mean(v)) if v else None
    return out


def compare(runs, tasks_file: Path) -> None:
    """The tuning table of a list of runs (results/rl/<run>/): per snapshot the sampled policy's oracle pass rate,
    mean margin over the oracle seeds and closed-loop pass share; entropy and approximate KL over training; the
    families' yardsticks."""
    print("| run | variant | family | months | oracle pass rate | engine margin (mean over 32 seeds) | closed-loop pass "
          "share | closed-loop margin | entropy | approx KL | minibatch steps |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    fams = []
    for run in runs:
        rdir = RESULTS / run
        conf = json.loads((rdir / "config.json").read_text())
        task, variant = conf["meta"]["task"], conf["meta"].get("variant", "frozen")
        fams.append(task)
        lp = rdir / "log.jsonl" if (rdir / "log.jsonl").exists() else CACHE / run / "log.jsonl"   # during training
        L = {d["months"]: d for d in (json.loads(x) for x in lp.read_text().splitlines() if x.strip())}
        for p in sorted(rdir.glob("eval3_*.summary.json")):
            s = json.loads(p.read_text())
            m = s["months"]
            win = [L[k] for k in L if m - 25000 < k <= m]            # the five iterations up to the snapshot
            ent = np.mean([d["entropy"] for d in win]) if win else float("nan")
            kl = np.mean([d["approx_kl"] for d in win]) if win else float("nan")
            mb = np.mean([d.get("minibatch_steps", 20) for d in win]) if win else float("nan")
            print(f"| {run} | {variant} | {task} | {m:,} | {s['rate_engine_open_accept']:.3f} | "
                  f"{s['mean_engine_open_margin']:.3f} | {s['rate_engine_closed_accept']:.3f} | "
                  f"{s['mean_engine_closed_margin']:.3f} | {ent:.2f} | {kl:.4f} | {mb:.1f} |")
    print("\nyardsticks (tasks file base_rates32: pass shares under the oracle, mean over the family's instances)\n")
    print("| family | instances | " + " | ".join(lbl for _, lbl in YARDSTICKS) + " |")
    print("|---|---|" + "---|" * len(YARDSTICKS))
    for task in dict.fromkeys(fams):
        y = yardsticks(tasks_file, task)
        print(f"| {task} | {y['n_instances']} | " + " | ".join("-" if y[k] is None else f"{y[k]:.3f}" for k, _ in YARDSTICKS) + " |")


def baseline(args) -> None:
    """Engine acceptance of constant do-nothing plans (no macro, funding 100 per cent, tax fixed) on a family's
    instances, primary seed and the eight secondary seeds, beside the behaviour mix's validation base rate when
    the tasks file has one."""
    from dc import grammar as G
    tp = tasks_path(args.tasks)
    eng = RA.engine_judge(workers=0, log=lambda m: None)
    d = json.loads(tp.read_text())
    try:
        for task in args.task.split(","):
            br = [r["base_rate_val"] for r in d["instances"] if r["task"] == task and int(r["horizon"]) == 24
                  and r.get("base_rate_val") is not None]
            print(f"\n{task} ({os.path.relpath(tp, ROOT)}): behaviour-mix base rate (validation, mean over "
                  f"{len(br)}) " + (f"{np.mean(br):.3f}" if br else "not in the tasks file"))
            print("| tax | accept, primary seed | accept, 8 secondary seeds | mean margin, primary |")
            print("|---|---|---|---|")
            for tax in (0, 2, 4, 5, 6, 7, 9):
                acc, acc8, mg = [], [], []
                for i in RA.load_family(task, tp):
                    eff = RA.effective(np.tile(G.noop_row(tax=tax), (24, 1))[None], task)
                    S = RA.verdict_seeds(i)
                    m = RA.task_margin(i, eng.scalars(i, np.repeat(eff, len(S), axis=0), np.asarray(S)))
                    acc.append(m[0] >= 0), acc8.append(np.mean(m[1:] >= 0)), mg.append(m[0])
                print(f"| {tax} | {np.mean(acc):.3f} | {np.mean(acc8):.3f} | {np.mean(mg):.3f} |")
        print("\n" + json.dumps(eng.counters()))
    finally:
        eng.close()


def cost(rdir: Path, pmon: Path, pid: int) -> None:
    """Projected GPU-hours of the 360 runs from a measured emulator run (acceptance item 4; reads that
    run's legacy evaluation summaries). Every input is read from a file; the assumptions are printed."""
    L = [json.loads(x) for x in (rdir / "log.jsonl").read_text().splitlines() if x.strip()]
    steady = L[1:]                                        # iteration 1 includes the compilation of the trunk
    sec = {k: sum(d["seconds"][k] for d in steady) for k in steady[0]["seconds"]}
    tot = sum(sec.values())
    months = sum(d["months"] - p["months"] for p, d in zip(L[:-1], L[1:]))
    rate_shared = months / tot
    warm = sum(L[0]["seconds"].values()) - (L[0]["months"] / rate_shared)
    S = [json.loads(p.read_text()) for p in sorted(rdir.glob("eval_*.summary.json")) if p.name.count(".") == 2]
    ev_first = S[0]["seconds"]["greedy_emulator"] + S[0]["seconds"]["verdict_emulator"]
    ev_steady = S[-1]["seconds"]["greedy_emulator"] + S[-1]["seconds"]["verdict_emulator"]
    sm, n = {}, 0
    for ln in pmon.read_text().splitlines():
        p = ln.split()
        if ln.startswith("#") or len(p) < 4 or p[0] != "0" or p[2] != "C":
            continue
        sm.setdefault(int(p[1]), []).append(0.0 if p[3] == "-" else float(p[3]))
    n = max(len(v) for v in sm.values())
    mine = sum(sm.get(pid, [])) / n
    busy = sum(sum(v) for v in sm.values()) / n
    inf = {(r["size"], r["batch"]): r["city_months_per_s"] for r in json.loads((ROOT / "results/fidelity/bench_infer.json").read_text())}
    rel = {s: inf[(s, 256)] / inf[("50m", 256)] for s in ("15m", "50m", "100m")}
    share = mine / busy
    emu_frac = sec["env_step"] / tot
    budget, snaps, n_runs = rl.FROZEN.budget, len(rl.FROZEN.snapshots), 120
    print(f"measured (50M, GPU 0 shared): {months:,} months in {tot:.1f} s of steady-state iterations = {rate_shared:.1f} "
          f"months/s with the policy in the loop; split " + ", ".join(f"{k} {100 * v / tot:.1f} %" for k, v in sec.items()))
    print(f"first iteration's extra time (trunk compilation) {warm:.1f} s; evaluation of a snapshot (emulator part) "
          f"{ev_first:.1f} s with compilation, {ev_steady:.1f} s after; engine part about 1-3 s")
    print(f"GPU 0 while it trained (nvidia-smi pmon, {n} samples of 1 s): this process {mine:.1f} % SM busy, all compute "
          f"processes {busy:.1f} %; share {share:.3f}")
    print(f"alone estimate: rate x (all-process busy / own busy) = {rate_shared / share:.0f} months/s (assumes the process "
          f"is GPU-bound and would use the busy time the others used; an upper estimate)")
    print(f"size scaling: emulator step only, from the inference bench of the pilot-1 model (batch 256, compiled, alone): "
          + ", ".join(f"{k} {v:.2f}" for k, v in rel.items()) + " of 50M's speed; policy forward and update do not scale with size")
    print("\n| size | runs | months/s alone (est.) | GPU-h per run alone | GPU-h alone, 120 runs | GPU-h at the measured share |")
    print("|---|---|---|---|---|---|")
    total_alone = total_shared = 0.0
    for size in ("15m", "50m", "100m"):
        per_month_alone = share / rate_shared * (emu_frac / rel[size] + (1 - emu_frac))
        train_s = budget * per_month_alone
        eval_s = snaps * ev_steady * share / rel[size] + (ev_first - ev_steady) * share / rel[size] + warm * share
        h = (train_s + eval_s) / 3600
        total_alone += n_runs * h
        total_shared += n_runs * h / share
        print(f"| {size} | {n_runs} | {1 / per_month_alone:.0f} | {h:.3f} | {n_runs * h:.1f} | {n_runs * h / share:.1f} |")
    print(f"| all | {3 * n_runs} | | | {total_alone:.1f} | {total_shared:.1f} |")


GPU_LOGS = Path("<cache>/ckpt")


def other_gpu_job_rate(since: float, until: float = float("inf")) -> dict:
    """Mean samples/s that the ladder's training runs logged in [since, until) (unix time), per run."""
    out = {}
    for lp in GPU_LOGS.glob("*/log.jsonl"):
        if lp.stat().st_mtime < since:
            continue
        rates = []
        with open(lp) as f:
            for ln in f:
                try:
                    d = json.loads(ln)
                except ValueError:
                    continue
                if since <= d.get("t", 0) < until and "samples_per_s" in d:
                    rates.append(d["samples_per_s"])
        if rates:
            out[lp.parent.name] = {"n": len(rates), "mean_samples_per_s": float(np.mean(rates))}
    return out


def bench(args) -> dict:
    """Throughput of the emulator environment on a GPU: emulator steps alone, and full PPO iterations with the
    policy in the loop (``dc.rl.Trainer.iterate``: 25 steps of every environment plus the update), per batch size.
    The per-part timers are synchronised (profile mode)."""
    instances = RA.load_family(args.task, tasks_path(args.tasks))
    cfg0 = rl.FROZEN
    dev_name = args.device or "cuda:0"
    res = {"ckpt": args.ckpt, "device": dev_name, "compile_trunk": bool(args.compile), "task": args.task, "runs": []}
    t_start = time.time()
    emu = RA.EmulatorBackend(args.ckpt, device=dev_name, model_src=args.model_src, compile_trunk=args.compile)
    res["load_s"] = time.time() - t_start
    res["emulator"] = emu.describe()
    dev = emu.device
    for E in [int(x) for x in args.bench_envs.split(",")]:
        cfg = replace(cfg0, n_envs=E, budget=E * cfg0.rollout_len * 1000, snapshots=(), minibatch=E * cfg0.rollout_len // 5)
        env = rl.TaskVecEnv(rl.EmuEnv(emu, E, profile=True), instances, E, run_key=f"bench{E}")
        env.reset_all()
        rng = np.random.default_rng(0)
        rows = G_random(rng, E)
        t0 = time.time()
        for _ in range(3):                          # warm-up (compilation for this shape)
            env.b.step(rows)
        torch.cuda.synchronize(dev)
        warm = time.time() - t0
        n = 20
        t0 = time.time()
        for _ in range(n):
            env.b.step(rows)
        torch.cuda.synchronize(dev)
        alone = n * E / (time.time() - t0)
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tr = rl.Trainer(cfg, env, td, run_key=f"bench{E}", device=dev, log=lambda m: None, profile=True)
            env.reset_all()
            tr.iterate()                            # first iteration: policy kernels autotune
            env.b.t_raster = env.b.t_model = 0.0
            torch.cuda.synchronize(dev)
            t0 = time.time()
            rec = tr.iterate()
            torch.cuda.synchronize(dev)
            it_s = time.time() - t0
        r = {"n_envs": E, "warmup_s": warm, "emulator_step_alone_months_per_s": alone,
             "ppo_iteration_months": E * cfg.rollout_len, "ppo_iteration_s": it_s,
             "months_per_s_policy_in_loop": E * cfg.rollout_len / it_s, "breakdown_s": rec["seconds"],
             "emulator_split_s": {"raster": env.b.t_raster, "model": env.b.t_model},
             "peak_mem_gb": torch.cuda.max_memory_allocated(dev) / 2**30}
        res["runs"].append(r)
        print(json.dumps(r), flush=True)
    res["wall_s"] = time.time() - t_start
    res["other_gpu_jobs_during"] = other_gpu_job_rate(t_start)
    res["other_gpu_jobs_before"] = other_gpu_job_rate(t_start - 600, t_start)
    if args.bench_out:
        Path(args.bench_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.bench_out).write_text(json.dumps(res, indent=1, default=str))
    return res


def G_random(rng, E):
    from dc import grammar as G
    return G.random_plan(rng, E, p_noop_macro=0.6)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["train", "eval", "bench", "report", "cost", "baseline", "compare"])
    ap.add_argument("--env", choices=["emulator", "engine", "stub"], required=True)
    ap.add_argument("--ckpt", default="")
    ap.add_argument("--model-src", default=RA.DEFAULT_MODEL_SRC)
    ap.add_argument("--task", required=True, help="task family (baseline: comma-separated families)")
    ap.add_argument("--tasks", default=DEFAULT_TASKS, help="tasks file: instances and thresholds (part of the run name)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--budget", type=int, default=0)
    ap.add_argument("--snapshots", default="")
    ap.add_argument("--device", default=None,
                    help="policy and PPO update (and the emulator); default cuda:0 for --env emulator, cpu otherwise")
    ap.add_argument("--compile", action="store_true", help="torch.compile the emulator trunk (fixed batch shapes)")
    ap.add_argument("--workers", type=int, default=8, help="engine environment processes (--env engine, training)")
    ap.add_argument("--eval-workers", type=int, default=8, help="engine processes for evaluation (judge and closed loop)")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--profile", action="store_true", help="synchronise the per-part timers with the GPU")
    ap.add_argument("--variant", default="frozen", help="learner: frozen (dc.rl.FROZEN) or a name in dc.rl.VARIANTS "
                    "(part of the run name)")
    ap.add_argument("--buffer", choices=["device", "host"], default="device",
                    help="train: keep the iteration's observations on the policy's device or on the host")
    ap.add_argument("--update-chunk", type=int, default=0,
                    help="train: rows per forward/backward pass in the update (0: the whole minibatch); the gradient "
                         "of the minibatch is accumulated, so only memory changes")
    ap.add_argument("--init-from", default="", help="train: the cloned policy (dc.bc, bc_s<seed>.pt) the learner starts "
                    "from; required with --variant " + ", ".join(rl.INIT_VARIANTS))
    ap.add_argument("--eval-side", choices=["both", "emulator", "engine"], default="both",
                    help="emulator runs: 'emulator' saves the snapshots' emulator phases and emulator.json (a rented "
                         "card, no engine replay); 'engine' (eval) reads them and runs the engine phases and records "
                         "(at home; --ckpt names the run and need not exist); 'both' does all")
    ap.add_argument("--no-eval", action="store_true")
    ap.add_argument("--stop-after-iters", type=int, default=None, help="testing: stop after this many iterations")
    ap.add_argument("--bench-envs", default="200", help="bench: comma-separated batch sizes (environments)")
    ap.add_argument("--bench-out", default="", help="bench: JSON output path")
    ap.add_argument("--run", default="", help="report, cost: run name (directory under results/rl)")
    ap.add_argument("--runs", default="", help="compare: comma-separated run names")
    ap.add_argument("--pmon", default="", help="cost: nvidia-smi pmon log recorded while the run trained")
    ap.add_argument("--pmon-pid", default="0", help="cost: the run's process id in the pmon log")
    args = ap.parse_args(argv)
    if args.cmd == "bench":
        return bench(args)
    if args.cmd == "report":
        return report(RESULTS / args.run)
    if args.cmd == "baseline":
        return baseline(args)
    if args.cmd == "cost":
        return cost(RESULTS / args.run, Path(args.pmon), int(args.pmon_pid))
    if args.cmd == "compare":
        return compare([r for r in args.runs.split(",") if r], tasks_path(args.tasks))
    torch.set_num_threads(args.threads)
    if args.env == "emulator" and not args.ckpt:
        ap.error("--ckpt is required with --env emulator")
    tp = tasks_path(args.tasks)
    digest = RA.tasks_digest(tp)
    cfg = make_cfg(args)
    name, legacy = resolve_run_name(args, cfg)
    cdir, rdir = CACHE / name, RESULTS / name
    cdir.mkdir(parents=True, exist_ok=True)
    rdir.mkdir(parents=True, exist_ok=True)
    log = log_to(cdir / "run.log")
    if legacy:
        log(f"{name}: a run made before --tasks existed (its config records no tasks file; it read {DEFAULT_TASKS})")
    instances = RA.load_family(args.task, tp)
    if not instances:
        raise RuntimeError(f"{args.task}: no instances in {tp}")
    n_oracle = RA.oracle_n(tp)
    cpath = rdir / "config.json"
    if args.cmd == "eval" and cpath.exists():
        # a finished run is evaluated with its own configuration (FROZEN may have moved on since it trained)
        cfg = rl.RLConfig.from_dict(json.loads(cpath.read_text())["cfg"])
    if args.eval_side != "both" and args.env != "emulator":
        ap.error("--eval-side emulator / engine is for runs in the emulator")
    if args.eval_side == "engine" and args.cmd == "train":
        ap.error("--eval-side engine evaluates a trained run: use the eval command")
    emu, device = make_emulator(args, cdir)
    backend = None
    try:
        init_state, iinfo = None, {}
        if args.variant in rl.INIT_VARIANTS:            # warm start: the cloned policy's biases, not the behaviour's
            if cfg.reinit_budget_heads:                 # hybrid: the budget heads' biases are the fresh policy's
                bias, binfo = init_bias(instances, cfg)
            else:
                bias, binfo = None, {"init_rows": None, "init_bias_sha256": None}
            if args.init_from:
                init_state, iinfo = init_policy(args, cfg)
        else:
            bias, binfo = init_bias(instances, cfg)
        meta = {"run": name, "environment": args.env, "task": args.task, "rl_seed": args.seed, "checkpoint": args.ckpt or None,
                "model_src": args.model_src if args.env == "emulator" else None, "compile_trunk": bool(args.compile),
                "instances": [i.key for i in instances], "n_instances": len(instances), "variant": args.variant,
                "n_oracle_seeds": n_oracle, **binfo, **iinfo, **digest, "numerics": numerics(device),
                "buffer": args.buffer, "update_chunk": args.update_chunk or None}
        if emu is not None and hasattr(emu, "describe"):
            meta["emulator"] = emu.describe()
            if meta["emulator"].get("ckpt_sha256"):
                meta["checkpoint_sha256"] = meta["emulator"]["ckpt_sha256"]
        meta["policy_parameters"] = rl.Policy(cfg.policy).num_parameters()
        conf = {"cfg": cfg.to_dict(), "meta": meta, "argv": sys.argv if argv is None else argv, "rl_version": rl.RL_VERSION}
        if cpath.exists():
            check_config(json.loads(cpath.read_text()), conf, args.cmd, legacy)
        else:
            cpath.write_text(json.dumps(conf, indent=1, default=str))
        log(f"{args.cmd} {name}: {cfg.months_per_iter} months per iteration, budget {cfg.budget}, snapshots "
            f"{list(cfg.snapshots)}, policy {meta['policy_parameters']:,} parameters, device {device}, tasks "
            f"{digest['tasks_file']} ({digest['tasks_sha256'][:12]})")
        if args.cmd == "train":
            backend = make_train_backend(args, emu, cfg.n_envs, device)
            env = rl.TaskVecEnv(backend, instances, cfg.n_envs, run_key=name)
            tr = rl.Trainer(cfg, env, cdir, run_key=name, device=device, init_bias=bias, meta=meta,
                            init_key=f"{args.task}|s{args.seed}", log=log, profile=args.profile,
                            buffer_device="cpu" if args.buffer == "host" else None,
                            update_chunk=args.update_chunk or None, init_policy=init_state)
            t0 = time.time()
            res = tr.train(stop_after_iters=args.stop_after_iters)
            res["wall_s_this_invocation"] = time.time() - t0
            res["timing_this_invocation"] = tr.timing
            log(f"train: {json.dumps(res)}")
            shutil.copy(cdir / "log.jsonl", rdir / "log.jsonl")
            if hasattr(backend, "close"):
                backend.close()
            if res["stopped"]:
                return
        if not args.no_eval:
            ev = evaluate_run(args, cfg, name, instances, emu, device, log, digest, cdir, rdir, n_oracle)
            if args.eval_side == "emulator":
                log(f"{name}: emulator side saved ({DONE_EMULATOR}); the engine side runs `eval --eval-side engine`")
                return
            summ = {"run": name, "snapshots": {str(k): v for k, v in ev.items()}}
            lp = rdir / "log.jsonl"
            if lp.exists():
                lines = [json.loads(x) for x in lp.read_text().splitlines() if x.strip()]
                summ["training_months"] = lines[-1]["months"] if lines else 0
                summ["training_seconds"] = {k: float(sum(x["seconds"][k] for x in lines)) for k in lines[0]["seconds"]} if lines else {}
            (rdir / f"summary_eval{rl.EVAL_VERSION}.json").write_text(json.dumps(summ, indent=1, default=str))
            (cdir / "DONE.json").write_text(json.dumps({"run": name, "eval_version": rl.EVAL_VERSION,
                                                        "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}))
    finally:
        if backend is not None and hasattr(backend, "close"):
            backend.close()


if __name__ == "__main__":
    main()
