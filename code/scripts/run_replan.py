#!/usr/bin/env python3
"""The monthly replanning run of the analysis plan , one model per invocation.

Random search at ``--plans`` (1,000) proposals, replanned every month from the engine's real state, the month-0 choice
judged by the paper's verdict and also executed open loop on the same seed; ``dc.replan`` holds the controller and its
seeds. ``--model emulator --checkpoint CKPT`` is the emulator (the audit's ``EmulatorJudge``, ``--model-src auto``);
``--model engine`` is the perfect emulator (the engine on seeds disjoint from the realised one).

``--controller-version`` 3 : from month 1 the best of the fresh proposals challenges the
incumbent on 8 paired samples; 2  offers the incumbent plan first in the screen; 1 is the analysis plan's
controller (``dc.replan.replan_instance``). A directory holds one controller version.

Instances: the order of ``data/replan_order_v1.json`` (``--write-order`` writes it by ``order_rule``); ``--instances N``
takes its first N, ``--shard k/n`` the positions p < N with p mod n = k - 1 (several processes split the order).

Outputs under ``--out``: ``records.jsonl.gz`` (one record per instance, ``dc.replan.replan_instance``, plus
``order_index``, ``device_name`` and ``host``), appended atomically under a lock (``.records.lock``) so shards share a
directory; ``config.json`` (the design, checked on every invocation, and every invocation's command line). Resumable per
instance: an instance already in the records is never recomputed; an interrupted instance restarts at month 0.

``--project DIR``: read a finished (dry) run's records and print the projected cost of 100 and 40 instances at
``--plans`` proposals from the measured seconds (scaled by plans; see ``project``).

Usage (from the repository root):
  PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/run_replan.py --model engine --out DIR [--instances 100]
      [--shard 1/1] [--plans 1000] [--workers 8] [--remote host-b --remote-workers 22]
  PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/run_replan.py --model emulator --checkpoint CKPT --out DIR
      [--device cuda:0] [--workers 4] ...
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import gzip
import json
import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO / "hpr-dream"))

from dc import audit as A  # noqa: E402
from dc import replan as RP  # noqa: E402
from dc import tasks as T  # noqa: E402
from dc.families import heldout_cty_of  # noqa: E402

ORDER = REPO / "data" / "replan_order_v1.json"
TASKS = REPO / "data" / "tasks_v2_H24.json"
N_AXIS = 100                    # the instances of the budget axis (20 a family)
AXIS_RUN = REPO / "results" / "audit" / "engine_reference" / "tasks_v2_H24" / "cem_seeded_1e4_i100"
ORDER_RULE = ("the 100 instances of the budget axis, dc.audit.select_instances(load_instances(tasks, 24, "
              "heldout_cty_of()), 100) (20 a task family), interleaved round robin over the task families in "
              "dc.tasks.TASKS order: position 5r + f holds family f's r-th instance in the selection's own order, so "
              "every prefix of 5k instances holds k per family")


def order_rule(instances) -> list:
    """``ORDER_RULE`` on the selected instances (each family the same count)."""
    by = {t: [i for i in instances if i.task == t] for t in T.TASKS}
    sizes = {len(v) for v in by.values()}
    if len(sizes) != 1:
        raise ValueError(f"families of unequal size: { {t: len(v) for t, v in by.items()} }")
    return [by[t][r] for r in range(sizes.pop()) for t in T.TASKS]


def _rel(p) -> str:
    p = Path(p).resolve()
    return str(p.relative_to(REPO)) if p.is_relative_to(REPO) else str(p)


def write_order(tasks, path) -> dict:
    universe = A.load_instances(tasks, 24, cty_of=heldout_cty_of())
    order = order_rule(A.select_instances(universe, N_AXIS))
    check = None
    if (AXIS_RUN / "config.json").exists():
        axis = json.loads((AXIS_RUN / "config.json").read_text())["instances"]
        check = {"run": _rel(AXIS_RUN), "same_instances": sorted(axis) == sorted(i.key for i in order)}
        if not check["same_instances"]:
            raise SystemExit(f"the selection differs from the budget axis's instances in {AXIS_RUN}")
    doc = {"decision": 88, "rule": ORDER_RULE, "tasks_file": _rel(tasks), "tasks_sha256": A._sha256_file(tasks),
           "n": len(order), "per_family": {t: sum(1 for i in order if i.task == t) for t in T.TASKS},
           "budget_axis_check": check,
           "instances": [{"index": k, "key": i.key, "task": i.task, "start_id": i.start_id, "cluster": i.family_id}
                         for k, i in enumerate(order)]}
    Path(path).write_text(json.dumps(doc, indent=1) + "\n")
    return doc


def load_order(path, tasks) -> list:
    doc = json.loads(Path(path).read_text())
    if doc["tasks_sha256"] != A._sha256_file(tasks):
        raise SystemExit(f"{path} was written for another tasks file (sha256 {doc['tasks_sha256'][:12]})")
    by = {i.key: i for i in A.load_instances(tasks, 24, cty_of=heldout_cty_of())}
    return [by[e["key"]] for e in doc["instances"]]


def shard_of(spec: str):
    k, n = (int(x) for x in spec.split("/"))
    if not 1 <= k <= n:
        raise SystemExit(f"--shard {spec}: need 1 <= k <= n")
    return k, n


@contextmanager
def locked(path: Path):
    with open(path, "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def read_records(out: Path) -> list:
    p = out / "records.jsonl.gz"
    return A.read_records(p) if p.exists() else []


def append_record(out: Path, rec: dict) -> bool:
    """Add one record under the lock: re-read, skip if the instance is there (another process), write a temporary
    file, fsync, rename. Returns whether it was added."""
    with locked(out / ".records.lock"):
        recs = read_records(out)
        if any(r["instance"] == rec["instance"] for r in recs):
            return False
        recs.append(rec)
        recs.sort(key=lambda r: r["order_index"])
        tmp = out / "records.jsonl.gz.tmp"
        with gzip.open(tmp, "wt", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        with open(tmp, "rb") as f:
            os.fsync(f.fileno())
        os.replace(tmp, out / "records.jsonl.gz")
    return True


def git_state() -> dict:
    def run(*a):
        return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()
    mine = ["code/dc/replan.py", "code/dc/audit.py", "code/scripts/run_replan.py", "code/dc/behaviour.py",
            "code/dc/tasks.py"]
    return {"rev": run("rev-parse", "HEAD"), "dirty_files": run("status", "--porcelain").splitlines(),
            "file_sha256": {f: A._sha256_file(REPO / f) for f in mine}}


def design_of(a, model, tasks, order_path, oracle_n) -> dict:
    """What every record of the directory depends on (checked on each invocation)."""
    d = model.describe()
    keep = {k: d.get(k) for k in ("model", "judge", "ckpt_sha256", "model_src_commit", "model_config", "chunk",
                                  "buckets", "compiled_trunk", "fast", "decoding", "seeds", "seeds_avoid",
                                  "continuation")}
    return {"decision": 88, "model": keep, "tasks_file": _rel(tasks), "tasks_sha256": A._sha256_file(tasks),
            "tasks_code_sha256": A._sha256_file(Path(T.__file__)), "order_file": _rel(order_path),
            "order_sha256": A._sha256_file(order_path), "n_plans": int(a.plans), "H": 24, "oracle_seeds": int(oracle_n),
            "K_search": A.K_SEARCH, "K_verdict": A.K_VERDICT, "verdict_rank": A.VERDICT_RANK,
            "replan_code_sha256": A._sha256_file(REPO / "code" / "dc" / "replan.py"),
            "controller_version": int(a.controller_version),
            **({"seed_stream": a.seed_stream} if a.seed_stream else {})}


def check_seed_stream(out: Path, stream) -> None:
    """Refuse an output directory whose config or records were written with another seed stream (none: the default
    seeds; a directory from before the option existed has none)."""
    cp = out / "config.json"
    have = set()
    if cp.exists():
        have.add(json.loads(cp.read_text())["design"].get("seed_stream") or None)
    have |= {r.get("seed_stream") or None for r in read_records(out)}
    if have - {stream or None}:
        raise SystemExit(f"{out} holds seed stream {sorted(map(str, have))}; this run is {stream or None}: use another --out")


def check_controller_version(out: Path, version: int) -> None:
    """Refuse an output directory whose config or records were written by another controller version (a directory
    from before the field existed is version 1)."""
    cp = out / "config.json"
    have = set()
    if cp.exists():
        have.add(int(json.loads(cp.read_text())["design"].get("controller_version", 1)))
    have |= {int(r.get("controller_version", 1)) for r in read_records(out)}
    if have - {int(version)}:
        raise SystemExit(f"{out} holds controller version {sorted(have)}; this run is version {version}: use another --out")


def project(out: Path, plans: int, n_list=(100, 40), first: int = 0) -> dict:
    """Projected cost from a run's records (``first``: only the records at order positions < first, e.g. the cost
    valve's first five). Per instance, the seconds of the proposal draws and of the scoring scale with the number of
    plans, the rest (realised states, verdict, open loop, oracle) does not; the model's month-steps and the engine's
    city-months likewise. Rates are this run's (its workers, its card and cap). ``hours``: wall hours of one process;
    ``scoring_hours``: the model's share (the emulator's card-hours); ``proposal_hours``: the proposal draws on the
    engine workers."""
    recs = [r for r in read_records(out) if not first or r["order_index"] < first]
    if not recs:
        raise SystemExit(f"{out}: no records")
    f = plans / recs[0]["n_plans"]
    per = []
    for r in recs:
        s = r["seconds"]
        fixed = s["realised_state"] + s["verdict_oracle_replays"] + s.get("paired", 0.0)
        pm, pe = r["counts"].get("paired_model_month_steps", 0), r["counts"].get("paired_engine_city_months", 0)
        per.append({"seconds": fixed + f * (s["proposals"] + s["scoring"]), "proposals": f * s["proposals"],
                    "scoring": f * s["scoring"], "paired": s.get("paired", 0.0), "fixed": fixed,
                    "model_month_steps": (r["counts"]["model_rollout_month_steps"] - A.K_VERDICT * 24 - pm) * f
                    + A.K_VERDICT * 24 + pm,
                    "engine_city_months": (r["counts"]["engine_city_months"] - pe) * f + pe})
    mean = {k: float(np.mean([p[k] for p in per])) for k in per[0]}
    return {"run": str(out), "records": len(recs), "plans_measured": recs[0]["n_plans"], "plans_projected": plans,
            "model": recs[0]["model"], "per_instance": mean, "order_positions": sorted(r["order_index"] for r in recs),
            "hours": {str(n): mean["seconds"] * n / 3600 for n in n_list},
            "scoring_hours": {str(n): mean["scoring"] * n / 3600 for n in n_list},
            "proposal_hours": {str(n): mean["proposals"] * n / 3600 for n in n_list},
            "measured": {"seconds_per_instance": float(np.mean([r["seconds"]["total"] for r in recs])),
                         "model_month_steps_per_scoring_second": float(
                             sum(r["counts"]["model_month_steps"] for r in recs) /
                             max(1e-9, sum(r["seconds"]["scoring"] for r in recs))),
                         "engine_city_months_per_second_of_proposals_and_scoring": float(
                             sum(r["counts"]["engine_city_months"] for r in recs) /
                             max(1e-9, sum(r["seconds"]["proposals"] + r["seconds"]["scoring"] for r in recs)))}}


def _ints(s: str):
    return tuple(int(x) for x in s.split(",") if x)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", choices=("emulator", "engine"))
    ap.add_argument("--checkpoint", default="", help="the emulator's checkpoint (.pt)")
    ap.add_argument("--tasks", default=str(TASKS))
    ap.add_argument("--order", default=str(ORDER))
    ap.add_argument("--write-order", action="store_true", help="write --order by order_rule and exit")
    ap.add_argument("--instances", type=int, default=0, help="the first N of the order (0: all)")
    ap.add_argument("--shard", default="1/1", help="k/n: positions p < N with p mod n = k - 1")
    ap.add_argument("--plans", type=int, default=1000, help="proposals per replan (the analysis plan: 1,000)")
    ap.add_argument("--out", default="")
    ap.add_argument("--project", default="", help="records directory: print the projected cost at --plans and exit")
    ap.add_argument("--project-first", type=int, default=0, help="with --project: only order positions below this "
                    "(the cost valve reads the first 5)")
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--buckets", default="16,64,144,256")
    ap.add_argument("--no-compile", action="store_true")
    ap.add_argument("--no-fast", action="store_true")
    ap.add_argument("--model-src", default="auto")
    ap.add_argument("--workers", type=int, default=2, help="local engine processes (proposal draws, replays)")
    ap.add_argument("--remote", default="none", choices=("none", "host-b"))
    ap.add_argument("--remote-workers", type=int, default=22)
    ap.add_argument("--remote-root", default=A.HOST_B_ROOT)
    ap.add_argument("--seed-stream", default="", help="the analysis plan: salt every seed the controller derives (the "
                    "proposals, the screen's, the verdict's and the paired samples) with this name; default none: the "
                    "seeds of every earlier run. The realised seed, the order and the oracle's seeds are unchanged")
    ap.add_argument("--controller-version", type=int, default=RP.CONTROLLER_VERSION, choices=RP.CONTROLLER_VERSIONS,
                    help="3 : from month 1 the screen's best fresh proposal must beat the incumbent "
                         "on 8 paired samples by two standard errors; 2 : the incumbent is offered first in "
                         "the screen; 1: the analysis plan's controller (fresh proposals only)")
    argv = list(sys.argv[1:] if argv is None else argv)
    a = ap.parse_args(argv)
    if a.write_order:
        doc = write_order(a.tasks, a.order)
        print(f"wrote {a.order}: {doc['n']} instances, {doc['per_family']}; budget axis check {doc['budget_axis_check']}")
        return 0
    if a.project:
        print(json.dumps(project(Path(a.project), a.plans, first=a.project_first), indent=1))
        return 0
    if not a.model or not a.out:
        raise SystemExit("--model and --out are required")
    if a.model == "emulator" and not a.checkpoint:
        raise SystemExit("--model emulator needs --checkpoint")
    spec = A.oracle_spec(a.tasks)
    if not spec:
        raise SystemExit("the tasks file has no majority oracle (meta.oracle)")
    oracle_n = spec["n_seeds"]
    order = load_order(a.order, a.tasks)
    N = a.instances or len(order)
    k, n_sh = shard_of(a.shard)
    mine = [(p, i) for p, i in enumerate(order[:N]) if p % n_sh == k - 1]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    check_controller_version(out, a.controller_version)
    check_seed_stream(out, a.seed_stream or None)
    done = {r["instance"] for r in read_records(out)}
    todo = [(p, i) for p, i in mine if i.key not in done]
    print(f"replan {a.model} (controller version {a.controller_version}"
          + (f", seed stream {a.seed_stream}" if a.seed_stream else "") + f"): {len(mine)} instances in shard {a.shard} of the first {N}; {len(mine) - len(todo)} done",
          flush=True)
    if not todo:
        return 0
    remote = remote_info = None
    if a.remote == "host-b":
        remote = RP.host_b_replan_pool(a.remote_workers, a.remote_root, log_path=out / "remote_stderr.log")
    pool = RP.JobPool(a.workers, remote=remote, log=lambda s: print(s, flush=True))
    if remote is not None:
        remote_info = RP.check_remote(pool, todo[0][1])
        print(f"remote pool: {remote_info}", flush=True)
    pool._get_pool()                       # the engine processes start before CUDA is initialised
    world = RP.EngineWorld(pool)
    if a.model == "emulator":
        ck = str(Path(a.checkpoint).resolve())
        judge = RP.make_emulator_judge(ck, device=a.device, chunk=a.chunk, buckets=_ints(a.buckets),
                                       compile_trunk=not a.no_compile, model_src=a.model_src, H=24, fast=not a.no_fast)
        model = RP.EmulatorModel(judge)
    else:
        model = RP.EngineModel(world, oracle_n)
    design = design_of(a, model, a.tasks, a.order, oracle_n)
    inv = {"argv": [sys.argv[0]] + argv, "started_utc": dt.datetime.utcnow().isoformat(timespec="seconds"),
           "host": socket.gethostname(), "git": git_state(), "remote": remote_info, "workers": a.workers,
           "describe": json.loads(json.dumps(model.describe(), default=str))}
    with locked(out / ".records.lock"):
        cp = out / "config.json"
        cfg = json.loads(cp.read_text()) if cp.exists() else {"design": json.loads(json.dumps(design, default=str)),
                                                               "invocations": []}
        if cfg["design"] != json.loads(json.dumps(design, default=str)):
            diff = sorted(k for k in design if cfg["design"].get(k) != json.loads(json.dumps(design[k], default=str)))
            raise SystemExit(f"{cp}: written by another design (differs in {diff}); use another --out")
        cfg["invocations"].append(inv)
        tmp = cp.with_name(cp.name + ".tmp")
        tmp.write_text(json.dumps(cfg, indent=1, default=str))
        os.replace(tmp, cp)
    dev_name = None
    if a.model == "emulator" and str(a.device).startswith("cuda"):
        import torch
        dev_name = torch.cuda.get_device_name(torch.device(a.device))
    try:
        run_instances(todo, model, world, out, a.plans, oracle_n, dev_name, controller_version=a.controller_version,
                      seed_stream=a.seed_stream or None)
    finally:
        pool.close()
    if dev_name is not None:
        import torch
        print(f"card memory peak: allocated {torch.cuda.max_memory_allocated() / 2**30:.2f} GiB, reserved "
              f"{torch.cuda.max_memory_reserved() / 2**30:.2f} GiB", flush=True)
    return 0


def _say(s: str) -> None:
    print(s, flush=True)


def run_instances(todo, model, world, out: Path, plans: int, oracle_n: int, dev_name=None, crash_after=None,
                  log=_say, controller_version: int = RP.CONTROLLER_VERSION, seed_stream=None) -> int:
    """The controller over (order position, instance) pairs, skipping instances already in ``out``'s records; each
    finished instance is appended at once. ``crash_after``: raise after that many new records (resumption tests).
    Refuses a directory written by another controller version."""
    check_controller_version(out, controller_version)
    check_seed_stream(out, seed_stream)
    n_new = 0
    for p, inst in todo:
        if inst.key in {r["instance"] for r in read_records(out)}:
            continue                        # finished by an earlier invocation or another process
        t0 = time.time()
        rec = RP.replan_instance(inst, model, world, n_plans=plans, oracle_n=oracle_n,
                                 controller_version=controller_version,
                                 **({"seed_stream": seed_stream} if seed_stream else {}))
        rec.update(order_index=p, device_name=dev_name, host=socket.gethostname())
        added = append_record(out, rec)
        n_new += added
        c = rec["counts"]
        log(f"{p:3d} {inst.key}: accept0 {rec['accept0']}, replan pass {rec['replan_pass']} "
            f"(margin {rec['replan']['margin']:+.3f}), open loop pass {rec['open_loop_pass']} "
            f"(margin {rec['open_loop']['margin']:+.3f}, oracle {rec['open_loop']['oracle_accept']}); "
            f"{time.time() - t0:.0f} s (proposals {rec['seconds']['proposals']:.0f}, scoring "
            f"{rec['seconds']['scoring']:.0f}); model {c['model_month_steps']:,} month-steps, engine "
            f"{c['engine_city_months']:,} city-months; incumbent kept {rec['incumbent_kept_months']} of {len(rec['months']) - 1} "
            f"months{'' if added else ' (already written by another process)'}")
        if crash_after is not None and n_new >= crash_after:
            raise RuntimeError("crash_after")
    return n_new


if __name__ == "__main__":
    sys.exit(main())
