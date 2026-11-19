# External TD-MPC2 adaptor

`hpr_dream.adaptors.tdmpc2` runs the instrument on a world model we did not train: a released
TD-MPC2 single-task checkpoint is the grader and the DeepMind Control simulator is the oracle.
Inference only. The adaptor imports torch, dm_control and the TD-MPC2 code lazily, inside the
functions that need them, so importing `hpr_dream` or the adaptor needs numpy only.

## Running the adaptor

The dependencies live in an isolated environment, `<home>/development/wm2-ext/venv`
(recreate it with `<home>/development/wm2-ext/INSTALL.md`; nothing is installed into the
project's `.venv`). From the wm2 root:

```bash
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 MUJOCO_GL=disable
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
PY=<home>/development/wm2-ext/venv/bin/python
# 1. oracle replay check (must report oracle_tolerance=0 before an audit will start)
taskset -c 16-23 $PY code/scripts/external_tdmpc2.py determinism --tasks cheetah-run walker-walk hopper-hop
# 2. the audit (resumable; detach it and redirect to a log); writes results/external/<task>/
taskset -c 16-23 $PY -u code/scripts/external_tdmpc2.py audit --tasks cheetah-run walker-walk hopper-hop \
    --instances 20 --attacker-seeds 3 --workers 7 > results/external/audit.log 2>&1
# 3. cards (cards/external/<task>.json) and results/external/summary.md from the saved results
$PY code/scripts/external_tdmpc2.py report --tasks cheetah-run walker-walk hopper-hop
# tests (project venv; the simulator parts run in wm2-ext/venv and skip if it is absent)
PYTHONPATH=hpr-dream .venv/bin/python -m pytest hpr-dream/tests/test_adaptor_tdmpc2.py -q
```

The grader refuses to start unless only physical GPU 1 is visible. One coordinator process holds
the model on the GPU; up to seven worker processes replay plans in the simulator. A resumed run
must use the same tasks, number of starts and attacker seeds.

## What the adaptor does

- **Plan**: 50 actions, flattened; each action dimension is an integer level 0..20 decoded as
  float32 `level / 10 - 1` (`decode_plans`; `encode_actions` is its inverse on the grid). Grader
  and oracle receive the same values: the simulator's control equals the float64 copy of the
  float32 action at every step (tested).
- **Start state** (`capture_start`, `StartState`, `restore`): seed `s`, environment reset, then 12
  uniform random actions on the grid, each repeated twice. Saved: physics state, the MuJoCo
  integration state (time, positions, velocities, warm start, controls), the observation the
  continuation produced, and the step count. `restore` sets these exactly. The replay after a
  restore equals the original continuation bit for bit (physics, integration state and rewards at
  every step; within a process, after re-creating the environment and in a separate process).
  The observation recomputed after a restore can differ for hopper (touch sensors recomputed by
  `forward()`; 3 of 20 audit starts); the grader always encodes the stored observation.
- **Oracle** (`Oracle`, `replay`): each action is applied for two simulator steps (the authors'
  action repeat) and the 100 rewards of the task are summed, undiscounted. It matches a few-line
  dm_control loop that reaches the start from its seed and prefix without any restoration, bit for
  bit (tested), and the authors' own TD-MPC2 environment wrapper.
- **Grader** (`Grader`): the authors' `TDMPC2` agent built from their `config.yaml` with the
  released single-task size (`MODEL_SIZE[5]`), loaded with their `load` (strict; no missing or
  unexpected keys), in evaluation mode. `returns` encodes the start observation and sums
  `two_hot_inv(reward(z_t, a_t))` for t = 0..49 with `z_t+1 = next(z_t, a_t)`, undiscounted, no
  terminal value: the same 50 steps and convention as the oracle. It is deterministic, so K
  samples are copies and success probabilities are 0 or 1. Every chunk is padded to a fixed
  batch shape so a plan's imagined return does not depend on the plans scored with it (without
  padding, batch size moved returns by up to 1.6e-4). `n_evals` counts plans scored.
- **Behaviour plans** (`behaviour_plans`): `u[0] ~ Uniform(-1, 1)`,
  `u[t] = 0.8 u[t-1] + 0.2 Uniform(-1, 1)`, independently per action dimension, rounded to the grid.
- **TD-MPC2's own planner** (`Grader.native_plan`): the authors' `_plan` (MPPI, released settings:
  horizon 3, 6 iterations, 512 samples, 64 elites, 24 policy trajectories, temperature 0.5,
  eval_mode=True) is called at 50 successive imagined latents starting from the encoded start
  observation; each selected action is quantised to the grid and advances the latent. The result
  is one 50-step plan, graded and replayed like any other. The planner's latent rollouts
  (horizon 3 plus a terminal Q) are counted while it runs (50 x 6 x 512 = 153,600 per plan) and
  that count is its budget label. It optimises the authors' discounted return plus terminal Q,
  not the 50-step audit score, and has no score callback over 50-step plans, so the surrogate noise
  floors are not run against it.

## The audit script (`code/scripts/external_tdmpc2.py`)

Per checkpoint: 20 starts (seeds 1000..1019; cluster = start). Per start: 2,000 behaviour plans
replayed on the oracle; theta = the 0.65 quantile of the first 600 oracle returns, checked on the
next 400 (acceptance must lie in [0.2, 0.5], else the checkpoint is excluded and reported); sd =
the sample sd of those 1,000 returns; the last 1,000 plans are scored by the grader too and give
the per-start residual pool (grader margin minus oracle margin), the flip rates (pooled within
the task) and false rejection. Attackers at exact budgets 1, 10, 100 and 1,000, three attacker
seeds each: margin-scored random shooting (proposals from the behaviour distribution), CEM
(initialised from behaviour marginals) and verdict-scored random shooting; each is also run
against the flip and the residual surrogate (`hpr_dream.noise`), with one oracle cache per start.
Every selected plan is re-scored by the grader and replayed on the oracle. Every random stream
has its own seed (start, attacker, budget, attacker seed, purpose). Budgets in the records are the
attackers' counted `n_scored`.

Checkpoints whose behaviour-plan oracle returns cannot be calibrated are not audited. For
hopper-hop, at 18 of the 20 starts every one of the 2,000 behaviour-plan returns is exactly 0
(98.2 and 99.5 per cent at the other two), so theta = 0 and the checked acceptance is 1.0 at every
start (`results/external/summary.md`, `results/external/hopper-hop/calibration-*.json`).

Checks of the adaptor against independent code (scripts and outputs in
`results/external/verification/`): the checkpoint bytes equal the release's published sha256; all
60 file tensors load into the agent unchanged (no missing or unexpected keys); the loaded agent,
acting through the authors' own environment wrapper, scores 875.2 (cheetah-run), 993.9
(walker-walk) and 570.0 (hopper-hop) in one evaluation episode each; every selected plan's oracle
margin is reproduced bit for bit by a few-line dm_control loop without state restoration; every
selected plan's grader margin is reproduced bit for bit by `Grader.returns` in a new process.
