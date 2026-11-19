"""Audit (a), (d), (e) on the run's own records.

For every selected plan of every start: (1) the adaptor's Grader.returns recomputed in a fresh
process must give the recorded grader margin bit for bit; (2) an independent latent loop written
here from the checkpoint's submodules (encoder, dynamics MLP, reward MLP, two-hot decoding), one
plan at a time, must agree within float32 batch-shape noise; (3) the recorded counts must equal
the counts implied by the design. Usage: python check_grader_records.py TASK
"""
import json
import sys
from pathlib import Path

ROOT = Path("<repo>")
EXT = Path("<home>/development/wm2-ext")
sys.path.insert(0, str(ROOT / "hpr-dream"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
from hpr_dream.adaptors import tdmpc2 as td  # noqa: E402

task = sys.argv[1]
RES = ROOT / "results/external" / task
insts = [json.loads(p.read_text()) for p in sorted(RES.glob("instance-*.json"))]
st0 = td.StartState.load(insts[0]["state"])
g = td.Grader(task, EXT / "checkpoints" / f"{task}-1.pt", len(st0.obs), st0.prefix.shape[1])
model, cfg = g.agent.model, g.agent.cfg
bins = torch.linspace(cfg.vmin, cfg.vmax, cfg.num_bins, device="cuda:0")


def independent(obs, actions):
    """sum_t symexp(softmax(reward_mlp([z_t, a_t])) . bins); z_{t+1} = dynamics_mlp([z_t, a_t])."""
    with torch.no_grad():
        z = model._encoder["state"](torch.as_tensor(obs, device="cuda:0")[None])
        tot = 0.0
        for a in torch.as_tensor(actions, device="cuda:0"):
            za = torch.cat([z, a[None]], -1)
            x = (torch.softmax(model._reward(za), -1) * bins).sum(-1)
            tot += float(torch.sign(x) * (torch.exp(torch.abs(x)) - 1))
            z = model._dynamics(za)
    return tot


n_rows = n_bit = n_flip = 0
worst = 0.0
diffs = []
count_ok = 0
dim = st0.prefix.shape[1]
for x in insts:
    i = x["instance"]
    state = td.StartState.load(x["state"])
    theta, sd = x["theta"], x["sd"]
    with np.load(RES / f"selected-{i:02d}.npz") as d:
        sel = np.concatenate([d["plans"], d["native_plans"]])
    rows = x["records"] + x["native_records"]
    marg = (g.returns(state, sel) - theta) / sd
    for r, m, p in zip(rows, marg, sel):
        n_rows += 1
        n_bit += int(float(m) == r["grader_score"] and (r["grader_p"] == float(m >= 0)))
        ind = (independent(state.obs, td.decode_plans(p[None], dim)[0]) - theta) / sd
        worst = max(worst, abs(ind - r["grader_score"]))
        diffs.append(abs(ind - r["grader_score"]))
        n_flip += int((ind >= 0) != (r["grader_score"] >= 0))
    # design counts per start: pool + search + rescoring of selected plans
    search = sum(r["n_scored"] for r in x["records"])
    exp_search = len(x["native_records"]) * 3 * sum((1, 10, 100, 1000))
    ok = (x["grader_plan_evaluations_pool"] == 1000 and search == exp_search
          and x["grader_plan_evaluations_attacks"] == search + len(x["records"]) + len(x["native_records"])
          and all(r["budget"] == r["n_scored"] for r in rows)
          and x["oracle_plan_evaluations"] == 2000
          and x["oracle_plan_evaluations_attacks"] == len(rows) + x["floor_oracle_unique_evaluations"]
          and all(r["budget"] == l["native_trajectories_scored"] == 50 * l["native_iterations"] * l["native_num_samples"]
                  for r, l in zip(x["native_records"], x["native_logs"])))
    count_ok += int(ok)
print(f"{task}: selected plans {n_rows}; recomputed grader margin and verdict equal to the record bitwise: {n_bit}/{n_rows}; "
      f"independent one-plan latent loop |margin diff| max {worst:.3g}, 99th pct {np.quantile(diffs, 0.99):.3g}, median {np.median(diffs):.3g}, "
      f"verdict disagreements {n_flip}/{n_rows}; starts whose counts match the design: {count_ok}/{len(insts)}")
