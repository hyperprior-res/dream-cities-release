#!/usr/bin/env python3
"""Replay Figure 1 and Figure 2 showcase plans across the 6M..36M extended-training milestones.

Evaluates the primary 2-epoch model's Figure 1 coal-plant demolition plan (highest-discrepancy exploited plan from
B = 1,000 random shooting) and Figure 2's 15 representative gallery plans across all six saved milestones
(6,000,000 to 36,000,000 examples) of ``os_50m_full_36m``, alongside a deterministic float32 CPU replay of Figure 1's
plan at 36,000,000 examples under ``fig1_data.py``'s exact torch seed (20261111).

Writes ``results/analysis/showcase_36m.json``.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "code", ROOT / "hpr-dream"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from dc import tasks as T  # noqa: E402
from dc.audit import load_emulator, load_instances  # noqa: E402
from dc.engine import Engine  # noqa: E402
from dc.grammar import action_scalars_batch, raster_batch  # noqa: E402
from dc.oracle import replay  # noqa: E402

FAMILIES = ("grow", "solvent", "treasury", "recover", "power")
MILESTONES = (6_000_000, 12_000_000, 18_000_000, 24_000_000, 30_000_000, 36_000_000)


def main(argv: list[str] | None = None) -> dict:
    ap = argparse.ArgumentParser(description="Replay Figure 1 and Figure 2 plans across 6M..36M milestones.")
    ap.add_argument("--ckpt-dir", default=str(ROOT.parent / "wm2-cache" / "ckpt" / "ladder_v2" / "os_50m_full_36m"))
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--out", default=str(ROOT / "results" / "analysis" / "showcase_36m.json"))
    a = ap.parse_args(argv)

    run_dir = ROOT / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24"
    tasks_path = ROOT / "data/tasks_v2_H24.json"
    inst_list = load_instances(tasks_path)
    inst_map = {i.key: i for i in inst_list}
    order = {i.key: idx for idx, i in enumerate(inst_list)}
    rows = [json.loads(ln) for ln in gzip.open(run_dir / "records.jsonl.gz", "rt")]
    cand = [r for r in rows if r["method"] == "random" and r["budget"] == 1000
            and r["grader_p_fresh"] >= 0.5 and not r["oracle_accept"]]
    z = np.load(run_dir / "selected_plans.npz", allow_pickle=False)

    f1_cand = sorted(cand, key=lambda r: (-(r["grader_p_fresh"] - r["oracle_share"]), r["oracle_margin"]))[0]
    gal = []
    for fam in FAMILIES:
        c = [r for r in cand if r["task"] == fam]
        c.sort(key=lambda r: (-(r["grader_p_fresh"] - r["oracle_share"]), r["oracle_margin"], order[r["instance"]]))
        for rank, r in enumerate(c[:4], 1):
            gal.append((f"{fam}{rank}", r))

    eng = Engine()
    cases = [("fig1", f1_cand, 20261111)] + [(tag, r, 20261113) for tag, r in gal]
    prepped = []
    for tag, r, tseed in cases:
        inst = inst_map[r["instance"]]
        idx = int(np.flatnonzero(z["plan_id"] == r["plan_id"])[0])
        plan = z["plans_effective"][idx].astype(np.int16)
        rp0 = replay(eng, inst.cty, [], 0)
        prepped.append((tag, r, inst, plan, rp0, tseed))

    ck_dir = Path(a.ckpt_dir)
    out = {}
    for m in MILESTONES:
        ck_path = ck_dir / f"samples_{m:09d}.pt"
        model, _, _, Tr = load_emulator(ck_path, a.device, "ladder-v2")
        m_res = {}
        for tag, r, inst, plan, rp0, tseed in prepped:
            d0 = Tr.obs_to_numpy([rp0.obs0], ledger=rp0.ledger[:1])
            s0 = Tr.numpy_to_state(d0, a.device)
            P = plan[None]
            act = torch.from_numpy(action_scalars_batch(P.reshape(-1, P.shape[-1])).reshape(1, P.shape[1], -1)).to(a.device)
            raster = lambda h, P=P: torch.from_numpy(raster_batch(P[:, h])).to(a.device)
            torch.manual_seed(tseed)
            if a.device.startswith("cuda"):
                torch.cuda.manual_seed_all(tseed)
            with torch.no_grad():
                traj, _ = model.rollout(s0, raster, act, K=8, max_batch=8)
            emu_scal = traj[0].detach().cpu().double().numpy()
            passes = T.verdict(inst.task, emu_scal, inst.theta).astype(bool)
            margins = T.margin(inst.task, emu_scal, inst.theta, inst.stat_sd)
            extra = {}
            if tag == "fig1":
                extra["passes_per_sample"] = passes.tolist()
                extra["margins_per_sample"] = [float(x) for x in margins]
                extra["scal_final_mean"] = [float(x) for x in emu_scal[:, -1, :].mean(axis=0)]
            m_res[tag] = {
                "instance": r["instance"],
                "plan_id": r["plan_id"],
                "task": inst.task,
                "orig_6m_audit_pass_share": r["grader_p_fresh"],
                "oracle_share": r["oracle_share"],
                "n_pass_of_8": int(passes.sum()),
                "pass_share": float(passes.mean()),
                "accepted": bool(passes.mean() >= 0.5),
                "mean_margin": float(margins.mean()),
                **extra,
            }
        f1p = m_res["fig1"]["n_pass_of_8"]
        gacc = sum(1 for k, v in m_res.items() if k != "fig1" and v["accepted"])
        by_fam_acc = {fam: sum(1 for k, v in m_res.items() if k != "fig1" and v["task"] == fam and v["accepted"])
                      for fam in FAMILIES}
        out[str(m)] = {
            "fig1_n_pass_of_8": f1p,
            "fig1_accepted": m_res["fig1"]["accepted"],
            "gallery_n_accepted_of_15": gacc,
            "gallery_accepted_by_family": by_fam_acc,
            "cases": m_res,
        }

    torch.set_num_threads(4)
    model_cpu, _, _, Tr_cpu = load_emulator(ck_dir / "samples_036000000.pt", "cpu", "ladder-v2")
    _, r, inst, plan, rp0, _ = prepped[0]
    d0 = Tr_cpu.obs_to_numpy([rp0.obs0], ledger=rp0.ledger[:1])
    s0 = Tr_cpu.numpy_to_state(d0, "cpu")
    P = plan[None]
    act = torch.from_numpy(action_scalars_batch(P.reshape(-1, P.shape[-1])).reshape(1, P.shape[1], -1))
    raster = lambda h, P=P: torch.from_numpy(raster_batch(P[:, h]))
    torch.manual_seed(20261111)
    with torch.no_grad():
        traj, _ = model_cpu.rollout(s0, raster, act, K=8, max_batch=8)
    emu_scal = traj[0].double().numpy()
    passes = T.verdict(inst.task, emu_scal, inst.theta).astype(bool)
    margins = T.margin(inst.task, emu_scal, inst.theta, inst.stat_sd)
    out["fig1_cpu_36m"] = {
        "instance": r["instance"],
        "plan_id": r["plan_id"],
        "torch_seed": 20261111,
        "n_pass_of_8": int(passes.sum()),
        "pass_share": float(passes.mean()),
        "accepted": bool(passes.mean() >= 0.5),
        "passes": passes.tolist(),
        "margins": [float(x) for x in margins],
        "emu_scal_m24_mean": [float(x) for x in emu_scal[:, -1, :].mean(axis=0)],
    }
    Path(a.out).write_text(json.dumps(out, indent=2) + "\n")
    return out


if __name__ == "__main__":
    main()
