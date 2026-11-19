"""Figure 1 data: one accepted-but-rejected plan of the main checkpoint, as the emulator imagines it
and as the engine replays it.

Selection rule (fixed in this file before any map was drawn): among the main checkpoint's
random-search selections at B = 1,000 that the emulator accepts (pass share >= 0.5 over its 8
re-scored samples) and the 32-seed majority oracle rejects, take the plan with the largest emulator
pass share minus oracle pass share; ties go to the most negative oracle margin.

Engine side: ``dc.oracle.replay`` of the plan from the instance's start file, full record, on oracle
seed k = 0 (the map), and the scalar trajectory on all 32 oracle seeds (the band; these are the
seeds the oracle's verdict is defined on).

Emulator side: the same checkpoint and training-commit code as the audit (``dc.audit.load_emulator``,
model source "auto"), run on the CPU in float32 with 4 threads, K = 8 fresh samples under torch seed
20261111. Because CUDA kernel reductions do not reproduce bit-for-bit across architectures, these are fresh CPU draws
from the same model, not the audit's own samples; the figure says so and shows the first sample
(lowest index) on which the shared predicate passes.

Writes figures/data/fig1_case.npz and figures/data/fig1_case.json. CPU only.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "code"), str(REPO / "hpr-dream")]

import numpy as np  # noqa: E402

RUN = REPO / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24"
CKPT = Path("<cache>/ckpt/ladder_v2/os_50m_full/samples_006000000.pt")
TASKS = REPO / "data/tasks_v2_H24.json"
OUT = REPO / "figures/data"
TORCH_SEED = 20261111
K = 8


def choose_case():
    rows = [json.loads(l) for l in gzip.open(RUN / "records.jsonl.gz", "rt")]
    cand = [r for r in rows if r["method"] == "random" and r["budget"] == 1000
            and r["grader_p_fresh"] >= 0.5 and not r["oracle_accept"]]
    cand.sort(key=lambda r: (-(r["grader_p_fresh"] - r["oracle_share"]), r["oracle_margin"]))
    return cand[0], len(cand)


def main():
    import torch
    torch.set_num_threads(4)
    from dc import tasks as T
    from dc.audit import load_emulator, load_instances, effective
    from dc.engine import Engine
    from dc.grammar import action_scalars_batch, compile_plan, raster_batch
    from dc.oracle import replay

    rec, n_cand = choose_case()
    inst = {i.key: i for i in load_instances(TASKS)}[rec["instance"]]
    z = np.load(RUN / "selected_plans.npz", allow_pickle=False)
    idx = int(np.flatnonzero(z["plan_id"] == rec["plan_id"])[0])
    plan = z["plans_effective"][idx].astype(np.int16)
    assert np.array_equal(plan, effective(plan[None], inst.task, inst.horizon)[0])

    # engine: 32 oracle seeds, scalars; seed k = 0 with every observation
    eng = Engine()
    acts, forced = compile_plan(plan)
    seeds = T.oracle_seeds(inst.start_id, inst.task, inst.horizon)
    t0 = time.time()
    full = replay(eng, inst.cty, acts, seeds[0], forced=forced or None, record="full")
    eng_scal = np.stack([replay(eng, inst.cty, acts, s, forced=forced or None).scalars for s in seeds])
    t_engine = time.time() - t0
    share = float(T.oracle_share(inst.task, eng_scal, inst.theta))
    assert abs(share - rec["oracle_share"]) < 1e-9, (share, rec["oracle_share"])
    eng_tiles = np.stack([o.tiles for o in full.states]).astype(np.uint16)      # (H+1, 120, 100)
    eng_power = np.stack([o.power for o in full.states]).astype(np.uint8)

    # emulator: K fresh CPU samples of the same checkpoint
    model, ck, desc, Tr = load_emulator(CKPT, "cpu", "auto")
    rp0 = replay(eng, inst.cty, [], 0)
    d0 = Tr.obs_to_numpy([rp0.obs0], ledger=rp0.ledger[:1])
    s0 = Tr.numpy_to_state(d0, "cpu")
    P = plan[None]
    act = torch.from_numpy(action_scalars_batch(P.reshape(-1, P.shape[-1])).reshape(1, P.shape[1], -1))
    raster = lambda h: torch.from_numpy(raster_batch(P[:, h]))
    torch.manual_seed(TORCH_SEED)
    t1 = time.time()
    with torch.no_grad():
        traj, sK = model.rollout(s0, raster, act, K=K, max_batch=K)
    t_emu = time.time() - t1
    emu_scal = traj[0].double().numpy()                                          # (K, H+1, 20)
    passes = T.verdict(inst.task, emu_scal, inst.theta).astype(bool)
    margins = T.margin(inst.task, emu_scal, inst.theta, inst.stat_sd)
    shown = int(np.flatnonzero(passes)[0]) if passes.any() else int(np.argmax(margins))
    emu_tile_index = sK["tile_index"].cpu().numpy().astype(np.int16)              # (K, 120, 100)
    emu_flags = (sK["flags"].cpu().numpy() > 0.5)                                 # (K, 5, 120, 100)
    emu_power = sK["power"].cpu().numpy().astype(np.uint8)

    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / "fig1_case.npz", plan=plan, eng_tiles=eng_tiles, eng_power=eng_power,
                        eng_scal=eng_scal, eng_scal_seed0=full.scalars, emu_scal=emu_scal,
                        emu_tile_index=emu_tile_index, emu_flags=emu_flags, emu_power=emu_power,
                        emu_passes=passes, emu_margins=margins, start_tiles=rp0.obs0.tiles.astype(np.uint16))
    meta = {
        "selection_rule": __doc__.split("\n\n")[1].replace("\n", " "),
        "n_accepted_but_rejected": n_cand, "instance": rec["instance"], "plan_id": rec["plan_id"],
        "start_id": inst.start_id, "task": inst.task, "theta": inst.theta, "stat_sd": inst.stat_sd,
        "audit_emulator_pass_share": rec["grader_p_fresh"], "audit_oracle_share": rec["oracle_share"],
        "audit_oracle_margin": rec["oracle_margin"], "engine_seed_map": int(seeds[0]),
        "engine_oracle_share_recomputed": share, "engine_seconds": t_engine,
        "emulator": {k: desc[k] for k in ("ckpt", "ckpt_sha256", "model_src_commit", "samples") if k in desc},
        "emulator_device": "cpu float32, torch threads 4", "torch_seed": TORCH_SEED, "K": K,
        "emulator_passes": passes.tolist(), "emulator_pass_share_fresh_cpu": float(passes.mean()),
        "emulator_margins": [float(m) for m in margins], "shown_sample": shown,
        "shown_rule": "first sample on which the predicate passes (else the largest margin)",
        "emulator_seconds": t_emu, "written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (OUT / "fig1_case.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
