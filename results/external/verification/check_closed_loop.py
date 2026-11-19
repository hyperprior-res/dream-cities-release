"""Positive control: the loaded checkpoint acting through the authors' own environment wrapper.

One episode per task with the authors' make_env and agent.act(eval_mode=True), as in their
online trainer's evaluation. Also: our adaptor's observation() against the wrapper's observation
at every step, one-step predicted reward against the real two-step reward on the agent's own
trajectory, and 50-step imagined against real return of the agent's own actions.
"""
import sys
from pathlib import Path

ROOT = Path("<repo>")
EXT = Path("<home>/development/wm2-ext")
sys.path.insert(0, str(ROOT / "hpr-dream"))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from hpr_dream.adaptors import tdmpc2 as td  # noqa: E402

for task in ("cheetah-run", "walker-walk", "hopper-hop"):
    st = td.capture_start(task, 1000)
    g = td.Grader(task, EXT / "checkpoints" / f"{task}-1.pt", len(st.obs), st.prefix.shape[1])
    from envs import make_env  # authors' code (on sys.path after Grader)
    from common import math as tm
    cfg = g.agent.cfg
    cfg.seed = 1
    env = make_env(cfg)
    torch.manual_seed(1)
    obs, done, t = env.reset(), False, 0
    inner = env.env.env.env._env  # TensorWrapper -> Timeout -> DMControlWrapper -> action_scale -> suite env
    obs_equal, real_r, pred_r, actions, obs_hist = [], [], [], [], []
    while not done:
        obs_equal.append(td.observation(inner).tobytes() == obs.numpy().tobytes())
        obs_hist.append(obs.clone())
        action = g.agent.act(obs, t0=(t == 0), eval_mode=True)
        with torch.no_grad():
            z = g.agent.model.encode(obs.to("cuda:0").unsqueeze(0), None)
            pr = tm.two_hot_inv(g.agent.model.reward(z, action.to("cuda:0").unsqueeze(0), None), cfg)
        pred_r.append(float(pr))
        actions.append(action.clone())
        obs, reward, done, info = env.step(action)
        real_r.append(float(reward))
        t += 1
    real_r, pred_r = np.array(real_r), np.array(pred_r)
    print(f"{task}: steps {t}, episode return (authors' wrapper, eval_mode=True) {real_r.sum():.1f}; "
          f"observation() == wrapper obs at {sum(obs_equal)}/{len(obs_equal)} steps")
    print(f"   one-step predicted vs real 2-step reward on the agent's own trajectory: "
          f"mean pred {pred_r.mean():.4f}, mean real {real_r.mean():.4f}, "
          f"mean |err| {np.abs(pred_r - real_r).mean():.4f}, corr {np.corrcoef(pred_r, real_r)[0, 1]:.4f}")
    # 50-step imagined vs real over the agent's own continuous actions, from steps 100, 200, 300
    for s in (100, 200, 300):
        with torch.no_grad():
            z = g.agent.model.encode(obs_hist[s].to("cuda:0").unsqueeze(0), None)
            tot = 0.0
            for k in range(50):
                a = actions[s + k].to("cuda:0").unsqueeze(0)
                tot += float(tm.two_hot_inv(g.agent.model.reward(z, a, None), cfg))
                z = g.agent.model.next(z, a, None)
        print(f"   from step {s}: imagined 50-step return {tot:.3f}, real {real_r[s:s + 50].sum():.3f}")
    del g
    torch.cuda.empty_cache()
