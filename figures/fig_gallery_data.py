"""Gallery data (figures G1 and G2): accepted-but-rejected plans of the main checkpoint, as the emulator
imagines them and as the engine replays them, month 24.

Selection rule (fixed in this file before any map was drawn; Figure 1 used the same rule for its one
plan): per task family, among the plans that random search selected at B = 1,000 evaluations on the 40
original cities that the emulator accepts (pass share >= 0.5 over its 8 re-scored samples) and the
32-seed majority oracle rejects, the four with the largest emulator pass share minus oracle pass share;
ties go to the most negative oracle margin, then to the lower instance index (order of the task file).
A family with fewer than four such plans contributes what it has.

Engine side: ``dc.oracle.replay`` of the plan from the instance's start file with every observation on
the oracle's first seed (the map), and the scalar trajectory on all 32 oracle seeds (to recompute the
oracle's pass share as a check against the audit record).

Emulator side: the audit's checkpoint and training-commit code (``dc.audit.load_emulator``, model source
"auto"), K = 8 fresh samples per plan on the CPU in float32 with 4 torch threads (as Figure 1), torch seed
20261113 set before each plan's rollout (so a plan's samples do not depend on the others). A GPU rollout was
tried first and does not repeat bit for bit from run to run, so the CPU is used. The audit's
own GPU samples do not reproduce bit-for-bit across devices, so these are fresh CPU draws from the same
model; the pass counts printed under each pair are the audit's (the counts the selection used), and the
fresh draws' counts are stored beside them. The sample shown is the first fresh sample on which the task
predicate passes (else the one with the largest margin, flagged).

Writes figures/data/gallery_cases.npz and figures/data/gallery_cases.json. CPU only, six worker processes.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""          # CPU only: the GPU draws do not repeat bit for bit
REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "code"), str(REPO / "hpr-dream")]

import numpy as np  # noqa: E402

RUN = REPO / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24"
CKPT = REPO.parent / "wm2-cache" / "ckpt/ladder_v2/os_50m_full/samples_006000000.pt"   # read-only
TASKS = REPO / "data/tasks_v2_H24.json"
OUT = REPO / "figures/data"
FAMILIES = ["grow", "solvent", "treasury", "recover", "power"]
PER_FAMILY = 4
TORCH_SEED = 20261113
K = 8
THREADS = 4
WORKERS = 6


def select(rows, order):
    """The fixed rule: {family: [record, ...]} (at most PER_FAMILY each) and the candidate counts."""
    cand = [r for r in rows if r["method"] == "random" and r["budget"] == 1000
            and r["grader_p_fresh"] >= 0.5 and not r["oracle_accept"]]
    out, counts = {}, {}
    for fam in FAMILIES:
        c = [r for r in cand if r["task"] == fam]
        c.sort(key=lambda r: (-(r["grader_p_fresh"] - r["oracle_share"]), r["oracle_margin"], order[r["instance"]]))
        out[fam], counts[fam] = c[:PER_FAMILY], len(c)
    return out, counts, len(cand)


def run_case(job):
    """One plan: engine replay (map on the oracle's first seed, scalars on all 32) and K emulator samples
    on the CPU (float32, THREADS torch threads, torch seed TORCH_SEED set before the rollout)."""
    fam, rank, rec, order_idx = job
    import torch
    torch.set_num_threads(THREADS)
    from dc import tasks as T
    from dc.audit import load_emulator, load_instances, effective
    from dc.engine import Engine
    from dc.grammar import action_scalars_batch, compile_plan, raster_batch
    from dc.oracle import replay

    inst = {i.key: i for i in load_instances(TASKS)}[rec["instance"]]
    z = np.load(RUN / "selected_plans.npz", allow_pickle=False)
    idx = int(np.flatnonzero(z["plan_id"] == rec["plan_id"])[0])
    plan = z["plans_effective"][idx].astype(np.int16)
    assert np.array_equal(plan, effective(plan[None], inst.task, inst.horizon)[0])
    eng = Engine()
    acts, forced = compile_plan(plan)
    seeds = T.oracle_seeds(inst.start_id, inst.task, inst.horizon)
    full = replay(eng, inst.cty, acts, seeds[0], forced=forced or None, record="full")
    eng_scal = np.stack([replay(eng, inst.cty, acts, s, forced=forced or None).scalars for s in seeds])
    share = float(T.oracle_share(inst.task, eng_scal, inst.theta))
    assert abs(share - rec["oracle_share"]) < 1e-9, (share, rec["oracle_share"])

    model, ck, desc, Tr = load_emulator(CKPT, "cpu", "auto")
    rp0 = replay(eng, inst.cty, [], 0)
    d0 = Tr.obs_to_numpy([rp0.obs0], ledger=rp0.ledger[:1])
    s0 = Tr.numpy_to_state(d0, "cpu")
    P = plan[None]
    act = torch.from_numpy(action_scalars_batch(P.reshape(-1, P.shape[-1])).reshape(1, P.shape[1], -1))
    raster = lambda h: torch.from_numpy(raster_batch(P[:, h]))
    torch.manual_seed(TORCH_SEED)
    with torch.no_grad():
        traj, sK = model.rollout(s0, raster, act, K=K, max_batch=K)
    emu_scal = traj[0].double().numpy()
    passes = T.verdict(inst.task, emu_scal, inst.theta).astype(bool)
    margins = T.margin(inst.task, emu_scal, inst.theta, inst.stat_sd)
    shown = int(np.flatnonzero(passes)[0]) if passes.any() else int(np.argmax(margins))
    footprint = (raster_batch(plan) != 0).any(axis=(0, 1))                          # (120, 100)
    tag = f"{fam}{rank}"
    arrays = {
        f"{tag}_start_tiles": rp0.obs0.tiles.astype(np.uint16),
        f"{tag}_eng_tiles": full.states[-1].tiles.astype(np.uint16),
        f"{tag}_eng_power": full.states[-1].power.astype(np.uint8),
        f"{tag}_emu_tile_index": sK["tile_index"].numpy().astype(np.int16),
        f"{tag}_emu_power": sK["power"].numpy().astype(np.uint8),
        f"{tag}_footprint": footprint, f"{tag}_plan": plan,
    }
    case = {
        "tag": tag, "family": fam, "rank": rank, "instance": rec["instance"], "instance_index": order_idx,
        "plan_id": rec["plan_id"], "start_id": inst.start_id,
        "audit_emulator_pass_share": rec["grader_p_fresh"],
        "audit_emulator_passing": int(round(rec["grader_p_fresh"] * K)),
        "audit_oracle_share": rec["oracle_share"], "audit_oracle_passing": int(round(rec["oracle_share"] * 32)),
        "audit_oracle_margin": rec["oracle_margin"], "gap": rec["grader_p_fresh"] - rec["oracle_share"],
        "engine_oracle_share_recomputed": share, "engine_seed_map": int(seeds[0]),
        "fresh_emulator_passes": passes.tolist(), "fresh_emulator_passing": int(passes.sum()),
        "fresh_emulator_margins": [round(float(m), 6) for m in margins],
        "shown_sample": shown, "shown_sample_passes": bool(passes[shown]),
        "footprint_tiles": int(footprint.sum()),
    }
    emu_desc = {k: desc[k] for k in ("ckpt_sha256", "model_src_commit", "samples") if k in desc}
    return case, arrays, emu_desc


def main():
    import multiprocessing as mp
    from dc.audit import load_instances
    insts = load_instances(TASKS)
    order = {i.key: n for n, i in enumerate(insts)}
    rows = [json.loads(l) for l in gzip.open(RUN / "records.jsonl.gz", "rt")]
    sel, counts, n_all = select(rows, order)
    jobs = [(fam, rank, rec, order[rec["instance"]]) for fam in FAMILIES for rank, rec in enumerate(sel[fam])]
    t_start = time.time()
    with mp.get_context("spawn").Pool(WORKERS) as pool:
        res = pool.map(run_case, jobs, chunksize=1)
    t_all = time.time() - t_start
    cases, arrays = [], {}
    for case, arr, emu_desc in res:
        cases.append(case); arrays.update(arr)
        print(case["tag"], case["instance"], "audit %d/8 vs %d/32" % (case["audit_emulator_passing"],
              case["audit_oracle_passing"]), "fresh %d/8" % case["fresh_emulator_passing"], flush=True)
    desc = res[0][2]

    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / "gallery_cases.npz", **arrays)
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001
        commit = None
    digest = hashlib.sha256(b"".join(np.ascontiguousarray(arrays[k]).tobytes() for k in sorted(arrays))).hexdigest()
    meta = {
        "selection_rule": __doc__.split("\n\n")[1].replace("\n", " "),
        "families": FAMILIES, "per_family": PER_FAMILY,
        "n_accepted_but_rejected_total": n_all, "n_accepted_but_rejected_by_family": counts,
        "n_shown_by_family": {f: len(sel[f]) for f in FAMILIES},
        "cases": cases,
        "inputs": [str((RUN / "records.jsonl.gz").relative_to(REPO)), str((RUN / "selected_plans.npz").relative_to(REPO)),
                   str(TASKS.relative_to(REPO)), "checkpoint ladder_v2/os_50m_full/samples_006000000.pt (read-only cache)"],
        "emulator": {k: desc[k] for k in ("ckpt_sha256", "model_src_commit", "samples") if k in desc},
        "emulator_device": f"cpu float32, torch threads {THREADS}", "torch_seed": TORCH_SEED, "K": K,
        "arrays_sha256": digest, "code_commit": commit,
        "shown_rule": "first fresh sample on which the predicate passes (else the largest margin, flagged)",
    }
    (OUT / "gallery_cases.json").write_text(json.dumps(meta, indent=1) + "\n")
    print("seconds %.1f" % t_all)
    print(json.dumps({k: meta[k] for k in ("n_accepted_but_rejected_by_family", "n_shown_by_family", "arrays_sha256")}, indent=1))


if __name__ == "__main__":
    main()
