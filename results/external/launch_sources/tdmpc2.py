"""Inference-only TD-MPC2 / DeepMind Control adaptor.

The optional dependencies live in wm2-ext/venv, never in the instrument's environment.
Actions use the authors' action repeat of two, with summed rewards. All audit returns
are undiscounted sums of 50 model steps (100 simulator steps), without a terminal Q estimate.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys
from dataclasses import dataclass

import numpy as np

from hpr_dream.attack import Space

EXT_ROOT = Path(os.environ.get("WM2_EXT", "<home>/development/wm2-ext"))
HORIZON = 50
ACTION_REPEAT = 2
TASKS = ("cheetah-run", "walker-walk", "hopper-hop")
BEHAVIOUR = "u[0] ~ Uniform(-1,1); u[t] = 0.8*u[t-1] + 0.2*Uniform(-1,1), independently by action dimension; nearest of 21 levels"


def plan_space(action_dim, horizon=HORIZON):
    return Space.integer_columns([0] * (horizon * action_dim), [20] * (horizon * action_dim))


def encode_actions(actions):
    a = np.asarray(actions)
    if not np.isfinite(a).all():
        raise ValueError("actions must be finite")
    return np.clip(np.rint((a + 1) * 10), 0, 20).astype(np.int16)


def decode_plans(plans, action_dim, horizon=HORIZON):
    p = np.asarray(plans)
    if p.ndim != 2 or p.shape[1] != horizon * action_dim:
        raise ValueError("plans must be a matrix of flattened action sequences")
    if not np.issubdtype(p.dtype, np.integer) or np.any((p < 0) | (p > 20)):
        raise ValueError("plan entries must be integers in [0,20]")
    return (p.astype(np.float32) / np.float32(10) - np.float32(1)).reshape(-1, horizon, action_dim)


def pad_rows(x, n):
    """``x`` (m <= n rows) followed by copies of its last row up to exactly ``n`` rows."""
    x = np.asarray(x)
    m = len(x)
    if not 1 <= m <= n:
        raise ValueError(f"cannot pad {m} rows to {n}")
    return x if m == n else np.concatenate([x, np.repeat(x[-1:], n - m, axis=0)])


def behaviour_plans(rng, n, action_dim, horizon=HORIZON):
    u = rng.uniform(-1, 1, (n, horizon, action_dim))
    for t in range(1, horizon):
        u[:, t] = 0.8 * u[:, t - 1] + 0.2 * u[:, t]
    return encode_actions(u).reshape(n, -1)


def observation(env):
    return np.concatenate([np.asarray(v).ravel() for v in env.task.get_observation(env.physics).values()]).astype(np.float32)


def make_env(task, seed=0):
    from dm_control import suite
    domain, name = task.split("-", 1)
    env = suite.load(domain, name, task_kwargs={"random": int(seed)}, visualize_reward=False)
    env.reset()
    spec = env.action_spec()
    if not (np.all(spec.minimum == -1) and np.all(spec.maximum == 1)):
        raise ValueError("adaptor requires the released tasks' [-1,1] action bounds")
    return env


def integration_state(env):
    import mujoco
    spec = mujoco.mjtState.mjSTATE_INTEGRATION
    state = np.empty(mujoco.mj_stateSize(env.physics.model.ptr, spec), np.float64)
    mujoco.mj_getState(env.physics.model.ptr, env.physics.data.ptr, state, spec)
    return state


@dataclass
class StartState:
    task: str
    seed: int
    prefix: np.ndarray
    physics: np.ndarray
    integration: np.ndarray
    obs: np.ndarray
    step_count: int

    def save(self, path):
        np.savez(path, **vars(self))

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as d:
            return cls(str(d["task"]), int(d["seed"]), d["prefix"], d["physics"],
                       d["integration"], d["obs"], int(d["step_count"]))

    @property
    def sha256(self):
        return hashlib.sha256(self.integration.tobytes()).hexdigest()


def capture_start(task, seed, prefix_steps=12):
    env = make_env(task, seed)
    dim = env.action_spec().shape[0]
    prefix = encode_actions(np.random.default_rng(seed + 100000).uniform(-1, 1, (prefix_steps, dim)))
    for action in decode_plans(prefix.reshape(1, -1), dim, prefix_steps)[0]:
        for _ in range(ACTION_REPEAT):
            env.step(action.astype(np.float64))
    state = StartState(task, seed, prefix, env.physics.get_state().copy(), integration_state(env),
                       observation(env), env._step_count)
    env.close()
    return state


def restore(env, state):
    import mujoco
    env.physics.set_state(state.physics)
    mujoco.mj_setState(env.physics.model.ptr, env.physics.data.ptr, state.integration,
                      mujoco.mjtState.mjSTATE_INTEGRATION)
    env.physics.forward()
    mujoco.mj_setState(env.physics.model.ptr, env.physics.data.ptr, state.integration,
                      mujoco.mjtState.mjSTATE_INTEGRATION)
    env._step_count = state.step_count
    env._reset_next_step = False
    if env.physics.get_state().tobytes() != state.physics.tobytes():
        raise RuntimeError("physics state restoration changed bytes")


def replay(env, state, plan, *, trace=False, restore_start=True):
    if restore_start:
        restore(env, state)
    dim = env.action_spec().shape[0]
    actions = decode_plans(np.asarray(plan).reshape(1, -1), dim)[0]
    rewards, states, full = [], [], []
    for action in actions:
        for _ in range(ACTION_REPEAT):
            step = env.step(action.astype(np.float64))
            if step.first():
                raise RuntimeError("unexpected environment reset during oracle replay")
            rewards.append(float(step.reward))
            if trace:
                states.append(env.physics.get_state().copy())
                full.append(integration_state(env))
    if trace:
        return np.asarray(rewards), np.asarray(states), np.asarray(full)
    return float(np.sum(rewards, dtype=np.float64))


_WORKER_ENVS = {}


def oracle_chunk(args):
    state, plans = args
    env = _WORKER_ENVS.get(state.task)
    if env is None:
        env = _WORKER_ENVS[state.task] = make_env(state.task, state.seed)
    return np.asarray([replay(env, state, p) for p in plans])


class Oracle:
    def __init__(self, state, pool=None, workers=1):
        self.state, self.pool, self.workers = state, pool, workers
        self.n_evals = 0

    def __call__(self, plans):
        x = np.asarray(plans)
        if not len(x):
            return np.empty(0)
        chunks = [(self.state, p) for p in np.array_split(x, min(len(x), self.workers * 2)) if len(p)]
        out = list(map(oracle_chunk, chunks)) if self.pool is None else self.pool.map(oracle_chunk, chunks)
        self.n_evals += sum(len(y) for y in out)
        return np.concatenate(out)


class Grader:
    """Authors' world model in eval mode; deterministic reward/dynamics rollout."""
    def __init__(self, task, checkpoint, obs_dim, action_dim, *, batch_size=128, ext_root=EXT_ROOT):
        if os.environ.get("CUDA_DEVICE_ORDER") != "PCI_BUS_ID" or os.environ.get("CUDA_VISIBLE_DEVICES") != "1":
            raise RuntimeError("set CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 before importing torch")
        import torch
        from omegaconf import OmegaConf
        source = Path(ext_root) / "tdmpc2" / "tdmpc2"
        sys.path.insert(0, str(source))
        from common import MODEL_SIZE
        from common.parser import cfg_to_dataclass
        from tdmpc2 import TDMPC2
        from common.math import two_hot_inv
        torch.set_num_threads(1)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        cfg = OmegaConf.load(source / "config.yaml")
        for k, v in MODEL_SIZE[5].items():
            cfg[k] = v
        for k, v in dict(task=task, model_size=5, multitask=False, task_dim=0, obs="state", compile=False,
                         obs_shape={"state": [obs_dim]}, action_dim=action_dim, episode_length=500,
                         bin_size=(cfg.vmax - cfg.vmin) / (cfg.num_bins - 1)).items():
            cfg[k] = v
        self.agent = TDMPC2(cfg_to_dataclass(cfg))
        self.agent.load(str(checkpoint))
        self.agent.model.eval()
        self.torch, self.two_hot_inv = torch, two_hot_inv
        self.batch_size, self.action_dim = int(batch_size), int(action_dim)
        self.n_evals = 0

    def returns(self, state, plans):
        """Imagined 50-step return per plan: the reward head's predictions summed along the latent
        rollout from the encoded start observation (reward(z_t, a_t), then z_t+1 = next(z_t, a_t),
        as in the authors' _estimate_value), undiscounted and without a terminal value.

        Every chunk is padded to exactly ``batch_size`` rows (copies of its last plan), so the
        matrix shapes, hence the floating-point reduction order, never depend on how many plans
        are scored together: the imagined return is a function of the plan alone. Unpadded, the
        chunk size moved returns by up to 1.6e-4 (cheetah-run, 300 plans). Padding rows are
        computed but neither returned nor counted; ``n_evals`` counts the plans scored."""
        torch, model = self.torch, self.agent.model
        actions = decode_plans(plans, self.action_dim)
        bs = self.batch_size
        out = []
        with torch.inference_mode():
            obs = torch.as_tensor(state.obs, device=self.agent.device).unsqueeze(0)
            start = model.encode(obs, None).repeat(bs, 1)
            for i in range(0, len(actions), bs):
                n = len(actions[i:i + bs])
                a = torch.as_tensor(pad_rows(actions[i:i + bs], bs), device=self.agent.device)
                z = start
                total = torch.zeros(bs, device=self.agent.device, dtype=torch.float64)
                for t in range(HORIZON):
                    total += self.two_hot_inv(model.reward(z, a[:, t], None), self.agent.cfg).flatten().double()
                    z = model.next(z, a[:, t], None)
                out.append(total[:n].cpu().numpy())
                self.n_evals += n
        return np.concatenate(out) if out else np.empty(0)

    def margins(self, state, plans, theta, sd, k=1):
        if sd <= 0 or k < 1:
            raise ValueError("positive sd and k required")
        margin = (self.returns(state, plans) - theta) / sd
        return np.repeat(margin[:, None], k, axis=1)

    def native_plan(self, state, seed):
        """Construct 50 actions with the authors' unmodified three-step MPPI.

        Only the encoder entry is redirected after the first call, so subsequent
        calls start at imagined latents. Native settings and value objective are
        preserved. Quantised chosen actions advance that latent. Counts of the
        native short trajectories are separate from 50-step audit plan counts.
        """
        torch, agent, model = self.torch, self.agent, self.agent.model
        torch.manual_seed(int(seed))
        torch.cuda.manual_seed(int(seed))
        counts = {"native_value_calls": 0, "native_trajectories_scored": 0,
                  "native_dynamics_transitions": 0, "native_reward_evaluations": 0,
                  "native_policy_proposal_transitions": 0}
        encode, estimate, next_fn, reward_fn = model.encode, agent._estimate_value, model.next, model.reward
        in_estimate = [False]

        def counted_estimate(z, actions, task):
            counts["native_value_calls"] += 1
            counts["native_trajectories_scored"] += int(actions.shape[1])
            in_estimate[0] = True
            try:
                return estimate(z, actions, task)
            finally:
                in_estimate[0] = False

        def counted_next(z, a, task):
            key = "native_dynamics_transitions" if in_estimate[0] else "native_policy_proposal_transitions"
            counts[key] += int(z.shape[0])
            return next_fn(z, a, task)

        def counted_reward(z, a, task):
            counts["native_reward_evaluations"] += int(z.shape[0])
            return reward_fn(z, a, task)

        plans = []
        with torch.no_grad():
            obs = torch.as_tensor(state.obs, device=agent.device).unsqueeze(0)
            z = encode(obs, None)
            model.encode = lambda ignored, task: z
            agent._estimate_value = counted_estimate
            model.next, model.reward = counted_next, counted_reward
            try:
                for t in range(HORIZON):
                    action = agent._plan(obs, t0=(t == 0), eval_mode=True, task=None)
                    discrete = encode_actions(action.cpu().numpy())
                    plans.append(discrete)
                    quantised = torch.as_tensor(discrete.astype(np.float32) / np.float32(10) - np.float32(1), device=agent.device).unsqueeze(0)
                    z = next_fn(z, quantised, None)
            finally:
                model.encode, agent._estimate_value = encode, estimate
                model.next, model.reward = next_fn, reward_fn
        counts.update(native_horizon=int(agent.cfg.horizon), native_iterations=int(agent.cfg.iterations),
                      native_num_samples=int(agent.cfg.num_samples), native_num_elites=int(agent.cfg.num_elites),
                      native_num_pi_trajs=int(agent.cfg.num_pi_trajs), native_temperature=float(agent.cfg.temperature),
                      native_min_std=float(agent.cfg.min_std), native_max_std=float(agent.cfg.max_std),
                      native_eval_mode=True, action_steps=len(plans),
                      imagined_advance_transitions=len(plans), native_discount=float(agent.discount),
                      audit_candidate_plans=1)
        return np.asarray(plans).reshape(-1), counts
