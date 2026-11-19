"""Audit (b), (e): an independent few-line dm_control loop against the audit's oracle numbers.

No adaptor code is used for the simulator: each start state is reached from its seed by reset and
the stored integer prefix (no state restoration), then the plan's actions are stepped twice each
and the task's own rewards summed. Compared bitwise with (1) the start states stored by the audit,
(2) stored behaviour-plan oracle returns, (3) every selected plan's oracle margin and every
noise-floor plan's oracle verdict in the instance records, (4) the adaptor's restoring oracle and
the authors' own TD-MPC2 environment wrapper on fixed action sequences.
Usage: python check_oracle.py TASK [RESULTS_ROOT [STATES_DIR]]
"""
import json
import sys
from pathlib import Path

import numpy as np
from dm_control import suite

ROOT = Path("<repo>")
EXT = Path("<home>/development/wm2-ext")
task = sys.argv[1]
domain, name = task.split("-", 1)
RES = (Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results/external") / task
STATES = Path(sys.argv[3]) if len(sys.argv) > 3 else EXT / "states"


def decode(idx, dim):
    """Integer level k in 0..20 -> action k/10 - 1, computed in float32 (the audit's convention)."""
    return np.asarray(idx, dtype=np.float32).reshape(-1, dim) / np.float32(10) - np.float32(1)


def my_returns(seed, prefix, plans, dim, check_ctrl=False):
    out, start = [], None
    for plan in plans:
        # a fresh environment per plan: a second reset() of one environment draws a new start
        env = suite.load(domain, name, task_kwargs={"random": int(seed)}, visualize_reward=False)
        env.reset()
        for a in decode(prefix, dim):
            for _ in range(2):
                env.step(a.astype(np.float64))
        if start is None:
            start = env.physics.get_state().copy()
        total, n = 0.0, 0
        rewards = []
        for a in decode(plan, dim):
            for _ in range(2):
                ts = env.step(a.astype(np.float64))
                if check_ctrl:
                    assert env.physics.data.ctrl.tobytes() == a.astype(np.float64).tobytes()
                rewards.append(ts.reward)
                n += 1
        out.append(np.sum(np.asarray(rewards, dtype=np.float64)))
        assert n == 100
    return np.asarray(out), start


instances = sorted(RES.glob("instance-*.json"))
n_beh = n_beh_eq = n_sel = n_sel_eq = n_floor = n_floor_eq = n_state_eq = 0
worst = 0.0
for path in instances:
    rec = json.loads(path.read_text())
    i = rec["instance"]
    st = np.load(STATES / f"{task}-{i:02d}.npz")
    seed, prefix = int(st["seed"]), st["prefix"]
    dim = prefix.shape[1]
    theta, sd = rec["theta"], rec["sd"]
    # (2) behaviour plans
    with np.load(RES / f"behaviour-{i:02d}.npz") as d:
        idx = [0, 1, 2, 599, 600, 999, 1000, 1500, 1999]
        plans, stored = d["plans"][idx], d["oracle_returns"][idx]
    mine, start = my_returns(seed, prefix, plans, dim, check_ctrl=(i == 0))
    n_state_eq += int(start.tobytes() == st["physics"].tobytes())
    n_beh += len(idx)
    n_beh_eq += int(np.sum([a.tobytes() == b.tobytes() for a, b in zip(mine, stored)]))
    worst = max(worst, float(np.max(np.abs(mine - stored))))
    # (3) selected plans: margins must equal the records bitwise
    with np.load(RES / f"selected-{i:02d}.npz") as d:
        sel = np.concatenate([d["plans"], d["native_plans"]])
    rows = rec["records"] + rec["native_records"]
    assert len(rows) == len(sel)
    mine, _ = my_returns(seed, prefix, sel, dim)
    for r, R in zip(rows, mine):
        m = float((R - theta) / sd)
        n_sel += 1
        n_sel_eq += int(m == r["oracle_margin"] and (m >= 0) == r["oracle_accept"])
    # noise-floor plans: oracle verdicts
    fplans, fverd = [], []
    for r in rec["records"]:
        for nm in ("flip", "residual"):
            f = RES / f"floor-{i:02d}-{r['attacker_seed']}-{r['attacker']}-{r['scoring']}-{r['budget']}-{nm}.npy"
            fplans.append(np.load(f).astype(np.int64))
            fverd.append(r[f"{nm}_oracle_accept"])
    mine, _ = my_returns(seed, prefix, np.asarray(fplans), dim)
    v = (mine - theta) / sd >= 0
    n_floor += len(v)
    n_floor_eq += int(np.sum(v == np.asarray(fverd)))
print(f"{task}: starts {len(instances)}; stored start states reproduced bitwise from seed+prefix: {n_state_eq}/{len(instances)}")
print(f"   behaviour-plan oracle returns equal bitwise: {n_beh_eq}/{n_beh} (max abs diff {worst:g})")
print(f"   selected-plan oracle margins (and verdicts) equal bitwise: {n_sel_eq}/{n_sel}")
print(f"   noise-floor selected-plan oracle verdicts equal: {n_floor_eq}/{n_floor}")

# (4) fixed action sequences: independent loop vs adaptor oracle (restoring) vs authors' wrapper
sys.path.insert(0, str(ROOT / "hpr-dream"))
from hpr_dream.adaptors import tdmpc2 as td  # noqa: E402

st0 = td.StartState.load(STATES / f"{task}-00.npz")
dim = st0.prefix.shape[1]
fixed = {"all_zero_action(k=10)": np.full(50 * dim, 10), "all_plus_one(k=20)": np.full(50 * dim, 20),
         "all_minus_one(k=0)": np.full(50 * dim, 0),
         "alternating_-1/+1": np.tile(np.repeat([0, 20], dim), 25),
         "ramp_k=t%21": np.repeat(np.arange(50) % 21, dim)}
P = np.stack(list(fixed.values())).astype(np.int64)
mine, _ = my_returns(st0.seed, st0.prefix, P, dim)
adaptor = td.Oracle(st0)(P)

sys.path.insert(0, str(EXT / "tdmpc2/tdmpc2"))
from envs.dmcontrol import make_env as authors_make_env  # noqa: E402
from types import SimpleNamespace  # noqa: E402

authors = []
for plan in P:
    env = authors_make_env(SimpleNamespace(task=task, obs="state", seed=st0.seed))  # Timeout(DMControlWrapper(action_scale(suite)))
    env.reset()
    for a in decode(st0.prefix, dim):
        env.step(a)
    tot = []
    for a in decode(plan, dim):
        _, r, _, _ = env.step(a)
        tot.append(r)
    authors.append(float(np.sum(np.asarray(tot, dtype=np.float64))))
print(f"   fixed sequences from start 00 (seed {st0.seed}):")
print("   sequence | independent loop | adaptor oracle (restored state) | authors' TD-MPC2 wrapper")
for (k, _), a, b, c in zip(fixed.items(), mine, adaptor, authors):
    print(f"   {k} | {a!r} | {b!r} | {c!r} | loop==adaptor {a.tobytes() == b.tobytes()} |loop-authors| {abs(a - c):.3g}")
