"""Policies trained with PPO wholly inside the emulator, judged by the real engine (the main claim's second arm).

Environment. ``TaskVecEnv`` holds ``n_envs`` slots; slot e belongs to task instance ``e mod 40`` of the pair (one
environment per (instance, episode)). An episode starts at the instance's start observation, takes 24 monthly
steps and ends; the slot then resets to the same instance (auto-reset). The month's action is one grammar
month; the plan's forced-disaster column is 0 and the task's own forced events (``dc.tasks.forced_for``: the
``recover`` task's earthquake in month 0) are written into it, exactly as ``dc.audit.effective`` does for a whole
plan (tested equal). Three backends give the next state of every slot:

* ``EmuEnv``: the emulator (``dc.rl_adaptor.EmulatorBackend.step``: the checkpoint's ``sample_next`` under the
  tag's default decoding, which the audit judge must report too; one noise sample per slot per month; no engine
  call anywhere in training);
* ``EngineEnv``: the real engine through ``dc.engine.Engine`` (load, seed, then the month order of
  ``dc.oracle.replay``), in worker processes; used for PPO with the engine as environment (the policy and the
  update may sit on a GPU) and for closed-loop evaluation;
* ``StubEnv``: a cheap toy dynamics with the emulator's state format, for tests only.

Observation. The policy sees the state the emulator consumes (tile codes, five flags, power map, five
half-resolution and three eighth-resolution overlays, terrain density and commercial-rate maps, 20 scalars, 27
ledger entries) and, from the environment, the task family (one-hot), the month index, the instance's start
scalars, the change since the start, and the instance's threshold expressed as the task's own quantities on the
trajectory so far (margin, statistic slack in units of the behaviour spread, minimum funds over the start funds,
the feasibility clause, theta).

Action. A factorised categorical over the plan grammar's columns (``dc.grammar.PLAN_COLUMNS``) except the
forced-disaster column: tax (21), road, fire, police (5 each), and per macro kind (19), x (120), y (100), a (31),
b (5): 24 heads, 1,136 logits. The log-probability of an action sums the heads the month's canonical form uses
(x and y unless the kind is NOOP; a and b where the kind's range is not (0, 0)); the plan row is
``dc.grammar.clip_plan`` of the sampled values. Greedy = arg-max of every head.

Reward. Potential-based on the task margin: r_t = margin(trajectory up to month t+1) - margin(trajectory up to
month t), so an episode's undiscounted return is its final margin minus its start margin (tested). The margin of
a prefix is ``dc.tasks``' margin of the bare prefix (months 0..t). The margin, the statistic and the feasibility
clause are read only through ``dc.tasks`` by way of ``dc.rl_adaptor`` (``task_margin``, ``task_statistic``,
``task_feasible``), so a change of the tasks file or of ``dc/tasks.py`` needs no change here.

Budget. A PPO iteration steps every slot ``rollout_len`` times; months are counted from the steps taken
(``n_envs x rollout_len`` per iteration, summed and asserted against the budget and every snapshot count).
Episodes cross iteration boundaries (bootstrapped values at the cut).

Seeds. Iteration k seeds the torch generator with ``seed_for("rl-env", run_key, k)`` (emulator noise), samples
actions from a generator seeded ``seed_for("rl-act", run_key, k)`` and shuffles minibatches with
``seed_for("rl-perm", run_key, k, epoch)``; engine training episodes use ``seed_for("rl-engine-train", run_key,
slot, episode)``. A resumed run reloads the state at an iteration boundary and is then identical to an
uninterrupted one (tested on CPU).

Timing. The per-part timers (environment step, policy forward, update, host) are synchronised with the GPU only
when ``profile`` is set; otherwise no synchronisation is added (the numbers a run produces are the same either
way, and the timers then measure when the host got there, not when the card finished).

Instances. A pair holds the family's instances in the tasks file (40, 38, 40, 35 and 40 under amendment 3). Slot e
plays instance (e + k E) mod n in its k-th episode, so instances get equal shares when n does not divide E. Engine
seeds in training are redrawn past every reserved seed of the start (the oracle's 32 and the nine residual seeds of
each task), and that is asserted.

Evaluation of a snapshot (the analysis plan under amendment 3, ``evaluate_snapshot``): the policy's plan is a sampled
episode of the policy. Per instance, 8 dream episodes (actions sampled from the policy, 24 months, one noise sample
per step), each action log a plan judged by its own trajectory; every plan judged by the oracle (its majority over
the instance's 32 dedicated seeds; engine margin = mean margin over those seeds), plan 0 also through the audit's
8-sample verdict; 8 sampled closed-loop episodes on the engine on fresh seeds of their own; the greedy plan as a
secondary record at the final snapshot. The phases are saved as they finish, so a killed evaluation resumes at the
first unfinished phase with identical records.

Learner options (round 2, part B; ``RLConfig``, ``VARIANTS``): a KL target with early stopping of the epoch loop, a
linear learning-rate decay, an entropy coefficient annealed linearly to zero, and a spatial read-out for the
position heads (``PolicyConfig.readout``). Their defaults are the learner, so the configurations and
snapshots load as they are. Memory options that change no number but rounding: the iteration's observations kept
on the host (``Trainer(buffer_device="cpu")``) and the minibatch's gradient accumulated over chunks
(``update_chunk``).

Round 4 . In ``MASKED_TAX_TASKS`` (``treasury``) the tax head's values above the episode's start rate
are masked for every learner with ``RLConfig.mask_treasury_tax`` (``FROZEN`` and "hybrid"): training rows, sampled
and greedy evaluation, emulator and engine environments (``cap_tax``, ``TaskVecEnv.tax_cap``); the predicate is
unchanged. The hybrid start (``RLConfig.reinit_budget_heads``, ``hybrid_state``): the cloned policy with the tax and
funding heads of the policy layer as the run's fresh policy initialises them.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from . import grammar as G
from . import rl_adaptor as RA
from . import tasks as T
from .engine import (BULLBIT, BURNBIT, CONDBIT, LOMASK, NUM_LEDGER, NUM_SCALARS, PWRBIT, SC_COAL, SC_FUNDS, SC_POP,
                     SC_RES_POP, SC_TAX, SC_TIME, SC_UNPOWERED, WORLD_H, WORLD_W, ZONEBIT, TOOL_COSTS)
from .seeds import seed_for

H = 24
N_COLS = G.N_COLS
FORCED_COL = 4
RL_VERSION = 1               # training: unchanged (snapshots of RL_VERSION 1 load as they are)
EVAL_VERSION = 3             # 2: the analysis plan (sampled episodes; dream, open loop, audit verdict of plan 0, closed loop);
                             # 3: amendment 3 (the 32-seed majority oracle; closed loop on fresh unreserved seeds)

# ----------------------------------------------------------------------------------------------
# Action space
# ----------------------------------------------------------------------------------------------
HEAD_COLS: List[int] = [0, 1, 2, 3] + [5 + 5 * j + k for j in range(G.M) for k in range(5)]   # 24 plan columns
HEAD_SIZES: List[int] = [int(G.COL_HIGH[c] - G.COL_LOW[c] + 1) for c in HEAD_COLS]
assert all(int(G.COL_LOW[c]) == 0 for c in HEAD_COLS)
N_HEADS = len(HEAD_COLS)                     # 24
N_LOGITS = int(sum(HEAD_SIZES))              # 1,136
HEAD_OFF = np.concatenate([[0], np.cumsum(HEAD_SIZES)]).astype(np.int64)
KIND_HEADS = [4 + 5 * j for j in range(G.M)]
_fam = np.array([G.MACRO_SPEC[k][1] for k in range(G.N_KINDS)])
KIND_USES_XY = torch.tensor(_fam != G.F_NONE)
KIND_USES_A = torch.tensor([G.MACRO_SPEC[k][2] != (0, 0) for k in range(G.N_KINDS)])
KIND_USES_B = torch.tensor([G.MACRO_SPEC[k][3] != (0, 0) for k in range(G.N_KINDS)])
_HCOL_T = torch.tensor(HEAD_COLS)


def used_heads(actions: torch.Tensor) -> torch.Tensor:
    """(B, 24) raw head values -> (B, 24) bool: the heads the month's canonical form depends on."""
    B = actions.shape[0]
    m = torch.ones(B, N_HEADS, dtype=torch.bool, device=actions.device)
    for j in range(G.M):
        k = actions[:, 4 + 5 * j].long()
        xy = KIND_USES_XY.to(actions.device)[k]
        m[:, 5 + 5 * j] = xy
        m[:, 6 + 5 * j] = xy
        m[:, 7 + 5 * j] = KIND_USES_A.to(actions.device)[k]
        m[:, 8 + 5 * j] = KIND_USES_B.to(actions.device)[k]
    return m


def actions_to_rows(actions) -> np.ndarray:
    """(B, 24) raw head values -> canonical plan rows (B, 25) int16, forced-disaster column 0."""
    a = np.asarray(actions.cpu() if torch.is_tensor(actions) else actions).astype(np.int64)
    rows = np.zeros((a.shape[0], N_COLS), dtype=np.int64)
    rows[:, HEAD_COLS] = a
    return G.clip_plan(rows)


def effective_rows(rows: np.ndarray, task: str, months: np.ndarray) -> np.ndarray:
    """Rows of month ``months[i]`` -> effective rows: the task's forced event of that month in column 4."""
    r = np.asarray(rows).astype(np.int64).copy()
    r[:, FORCED_COL] = 0
    for m, kind in RA.forced_for(task).items():
        r[np.asarray(months) == m, FORCED_COL] = kind
    return G.clip_plan(r)


def head_logps(logits: torch.Tensor) -> List[torch.Tensor]:
    return [F.log_softmax(logits[:, HEAD_OFF[i]:HEAD_OFF[i + 1]].float(), dim=-1) for i in range(N_HEADS)]


def sample_actions(logits: torch.Tensor, gen: Optional[torch.Generator], greedy: bool = False) -> torch.Tensor:
    """(B, 1136) logits -> (B, 24) int64 head values (Gumbel-max with ``gen``, or arg-max)."""
    out = []
    for i in range(N_HEADS):
        lg = logits[:, HEAD_OFF[i]:HEAD_OFF[i + 1]].float()
        if greedy:
            out.append(lg.argmax(-1))
        else:
            u = torch.rand(lg.shape, generator=gen, device=lg.device, dtype=torch.float32).clamp_(1e-12, 1 - 1e-7)
            out.append((lg - torch.log(-torch.log(u))).argmax(-1))
    return torch.stack(out, dim=1)


def logp_entropy(logits: torch.Tensor, actions: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Log-probability and entropy of the used heads of ``actions`` (B, 24)."""
    lps = head_logps(logits)
    used = used_heads(actions).float()
    lp = torch.stack([lps[i].gather(1, actions[:, i:i + 1].long()).squeeze(1) for i in range(N_HEADS)], dim=1)
    ent = torch.stack([-(lps[i].exp() * lps[i]).sum(-1) for i in range(N_HEADS)], dim=1)
    return (lp * used).sum(1), (ent * used).sum(1)


def month_kl(logits_p: torch.Tensor, logits_q: torch.Tensor) -> torch.Tensor:
    """(B,) KL(p || q) between two policies' month distributions as ``logp_entropy`` defines them (the product over
    the heads the month uses): the budget and kind heads count fully, macro j's x and y heads weighted by
    p(kind j uses x and y), its a and b heads by p(kind j uses a) and p(kind j uses b) (the heads are independent
    under p, and an unused head's value does not enter the month)."""
    lp, lq = head_logps(logits_p), head_logps(logits_q)
    kl = [(lp[i].exp() * (lp[i] - lq[i])).sum(-1) for i in range(N_HEADS)]
    out = kl[0] + kl[1] + kl[2] + kl[3]
    for j in range(G.M):
        pk = lp[4 + 5 * j].exp()
        dev = pk.device
        p_xy = (pk * KIND_USES_XY.to(dev).float()).sum(-1)
        p_a = (pk * KIND_USES_A.to(dev).float()).sum(-1)
        p_b = (pk * KIND_USES_B.to(dev).float()).sum(-1)
        out = out + kl[4 + 5 * j] + p_xy * (kl[5 + 5 * j] + kl[6 + 5 * j]) + p_a * kl[7 + 5 * j] + p_b * kl[8 + 5 * j]
    return out


MASKED_TAX_TASKS = ("treasury",)                 # tasks whose plans may not set the tax above the start rate
BUDGET_HEADS = (0, 1, 2, 3)                      # tax, road, fire, police: logits HEAD_OFF[0]:HEAD_OFF[4]


def cap_tax(logits: torch.Tensor, cap: Optional[torch.Tensor]) -> torch.Tensor:
    """``logits`` with the tax head's values above ``cap`` (B,) set to -1e9 (probability 0 to float precision; never
    sampled, never the arg-max); ``cap`` None: unchanged."""
    if cap is None:
        return logits
    n = HEAD_SIZES[0]
    over = torch.arange(n, device=logits.device)[None, :] > cap.to(logits.device).long()[:, None]
    out = logits.clone()
    out[:, :n] = out[:, :n].masked_fill(over, -1e9)
    return out


def hybrid_state(clone: Dict[str, torch.Tensor], fresh: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
    """The hybrid start: every weight of the cloned policy except the tax and funding heads' rows of the policy layer
    (``pi.weight`` and ``pi.bias``, logits HEAD_OFF[0]:HEAD_OFF[4]), which are the fresh policy's. The task features
    enter the network only through the shared vector layer, whose weights (the task columns zero) stay the clone's."""
    rows = slice(int(HEAD_OFF[BUDGET_HEADS[0]]), int(HEAD_OFF[BUDGET_HEADS[-1] + 1]))
    out = {k: v.detach().clone() for k, v in clone.items()}
    for k in ("pi.weight", "pi.bias"):
        out[k][rows] = fresh[k][rows].to(out[k].device, out[k].dtype)
    return out


# ----------------------------------------------------------------------------------------------
# Raster on the device (exact: the same rectangles as dc.grammar.raster_batch)
# ----------------------------------------------------------------------------------------------
_XS = {}


def raster_torch(rows: np.ndarray, device) -> torch.Tensor:
    """Canonical rows (B, 25) -> float32 (B, 15, 120, 100) on ``device``; equal to ``dc.grammar.raster_batch``."""
    r = G.clip_plan(np.asarray(rows).reshape(-1, N_COLS))
    ch, x0, x1, y0, y1, n, _ = G._macro_geometry(r)
    dev = torch.device(device)
    key = str(dev)
    if key not in _XS:
        _XS[key] = (torch.arange(WORLD_W, device=dev), torch.arange(WORLD_H, device=dev))
    xs, ys = _XS[key]
    t = lambda a: torch.from_numpy(np.ascontiguousarray(a, dtype=np.int64)).to(dev)
    x0, x1, y0, y1, n, ch = t(x0), t(x1), t(y0), t(y1), t(n), t(ch)
    mx = (xs >= x0[..., None]) & (xs < x1[..., None])                      # (B, M, 120)
    my = (ys >= y0[..., None]) & (ys < y1[..., None])                      # (B, M, 100)
    valid = (n > 0) & (ch >= 0)
    oh = F.one_hot(ch.clamp(min=0), G.N_CHANNELS).float() * valid[..., None].float()    # (B, M, 15)
    rect = (mx[..., :, None] & my[..., None, :]).float()                   # (B, M, 120, 100)
    return (torch.einsum("bmc,bmxy->bcxy", oh, rect) > 0).float()


def act_scalars_torch(rows: np.ndarray, device) -> torch.Tensor:
    return torch.from_numpy(G.action_scalars_batch(rows)).to(device)


# ----------------------------------------------------------------------------------------------
# Observations: one compact format for the emulator's state and the engine's observation
# ----------------------------------------------------------------------------------------------
PACK_KEYS = ("tiles16", "power", "half", "eighth", "terrain", "com_rate", "scalars", "ledger")
FLAG_SHIFT = 10                     # tiles16 = tile code | flag i << (10 + i), flags in the loader's order
ENGINE_FLAG_BITS = (ZONEBIT, BULLBIT, BURNBIT, CONDBIT, PWRBIT)


def pack_state(state: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
    """Emulator state (loader format) -> compact tensors (lossless: flags and power are 0/1, codes < 1,024)."""
    t16 = state["tile_index"].long()
    for i in range(5):
        t16 = t16 | (state["flags"][:, i] > 0.5).long() << (FLAG_SHIFT + i)
    return {"tiles16": t16.to(torch.int16), "power": (state["power"] > 0.5).to(torch.uint8),
            "half": state["half"].float(), "eighth": state["eighth"].float(), "terrain": state["terrain"].float(),
            "com_rate": state["com_rate"].float(), "scalars": state["scalars"].float(),
            "ledger": state["ledger"].float()}


def pack_engine_obs(obs, ledger: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
    """``dc.engine.Obs`` -> the compact format of ``pack_state`` (numpy, one row)."""
    tiles = obs.tiles.astype(np.int64)
    t16 = tiles & LOMASK
    for i, b in enumerate(ENGINE_FLAG_BITS):
        t16 |= ((tiles & b) > 0).astype(np.int64) << (FLAG_SHIFT + i)
    led = obs.ledger if ledger is None else ledger
    return {"tiles16": t16.astype(np.int16), "power": (obs.power > 0).astype(np.uint8),
            "half": obs.half.astype(np.float32), "eighth": obs.eighth.astype(np.float32),
            "terrain": obs.terrain.astype(np.float32), "com_rate": obs.com_rate.astype(np.float32),
            "scalars": obs.scalars.astype(np.float64).astype(np.float32),
            "ledger": np.asarray(led).astype(np.float64).astype(np.float32),
            "scal64": obs.scalars.astype(np.float64)}       # exact engine scalars for the task margins


def stack_packed(rows: Sequence[Dict[str, np.ndarray]], device) -> Dict[str, torch.Tensor]:
    return {k: torch.from_numpy(np.stack([r[k] for r in rows])).to(device) for k in PACK_KEYS}


def symlog_np(x):
    return np.sign(x) * np.log1p(np.abs(x))


def symlog_t(x: torch.Tensor) -> torch.Tensor:
    return torch.sign(x) * torch.log1p(x.abs())


# ----------------------------------------------------------------------------------------------
# Policy
# ----------------------------------------------------------------------------------------------
N_ENV_VEC = len(T.TASKS) + H + NUM_SCALARS + NUM_SCALARS + 5     # 74
_VEC_TAIL = len(T.TASKS) + H + 2 * NUM_SCALARS                    # 69: margin, statistic slack, minimum funds,
                                                                  # feasibility, theta
# Columns of the environment features that depend on the task family or the instance's threshold: the task
# one-hot, the margin, the statistic's slack, the feasibility clause and theta (the cloned policy's inputs there
# are zero; ``dc.bc``). The month one-hot, the start scalars, the change since the start and the minimum funds
# over the start funds are read from the scalar trajectory alone.
TASK_VEC_COLS: Tuple[int, ...] = tuple(range(len(T.TASKS))) + (_VEC_TAIL + 0, _VEC_TAIL + 1, _VEC_TAIL + 3,
                                                                 _VEC_TAIL + 4)


def taskfree_features(traj: np.ndarray, t: np.ndarray) -> np.ndarray:
    """(E, 74) float32 environment features with the task-dependent columns (``TASK_VEC_COLS``) zero: month one-hot,
    start scalars, change since the start (symlog / 10) and the minimum funds so far over the start funds.
    ``traj`` (E, >= t + 1, 20) float64 scalar trajectories, ``t`` (E,) months so far."""
    traj = np.asarray(traj)
    t = np.asarray(t, dtype=np.int64)
    E = traj.shape[0]
    v = np.zeros((E, N_ENV_VEC), dtype=np.float32)
    o = len(T.TASKS)
    v[np.arange(E), o + np.minimum(t, H - 1)] = 1.0
    o += H
    s0 = traj[:, 0]
    cur = traj[np.arange(E), t]
    v[:, o:o + NUM_SCALARS] = symlog_np(s0) / 10.0
    o += NUM_SCALARS
    v[:, o:o + NUM_SCALARS] = symlog_np(cur - s0) / 10.0
    fmin = np.minimum.accumulate(traj[:, :, SC_FUNDS], axis=1)[np.arange(E), t]
    fmin = fmin / np.maximum(np.abs(s0[:, SC_FUNDS]), 1.0)
    v[:, _VEC_TAIL + 2] = np.clip(fmin, -10, 10)
    return v


@dataclass
class PolicyConfig:
    tile_emb: int = 8
    c1: int = 32                  # 30 x 25 after a 4 x 4 patchify convolution
    c2: int = 48                  # 15 x 13 and 8 x 7
    spatial_out: int = 256
    vec_hidden: int = 256
    hidden: int = 256
    readout: str = "global"       # "global": every head from the trunk vector ; "spatial": the x and y heads
                                  # also read a 30 x 25 map (``Policy`` docstring)


X_HEADS = [5 + 5 * j for j in range(G.M)]           # head index of macro j's x (120) and y (100) heads
Y_HEADS = [6 + 5 * j for j in range(G.M)]
READ_CELL = 4                                        # tiles per cell of the spatial read-out (30 x 25 cells)


class Policy(nn.Module):
    """Shared trunk: a small convolutional encoder of the maps and an MLP of the vectors; 1,136 action logits
    and a value.

    Read-out "spatial": for each macro slot a map of joint position scores over the 30 x 25 cells of 4 x 4 tiles,
    from the 30 x 25 features (first convolution) and the 15 x 13 features (third convolution, up-sampled), shifted
    per channel by the trunk vector; the x head adds log-sum-exp over the map's rows (the marginal of the cell
    scores, each cell's score repeated over its 4 columns), the y head likewise over columns. The final 1 x 1
    convolution starts at zero, so the initial action distribution is the global read-out's."""

    def __init__(self, cfg: PolicyConfig = PolicyConfig()) -> None:
        super().__init__()
        self.cfg = cfg
        c = cfg
        self.tile_emb = nn.Embedding(1024, c.tile_emb)
        self.conv1 = nn.Conv2d(c.tile_emb + 5 + 1, c.c1, kernel_size=4, stride=4)                 # 120x100 -> 30x25
        self.conv2 = nn.Conv2d(c.c1 + 1 + 5, c.c2, kernel_size=3, stride=2, padding=1)            # -> 15x13
        self.conv3 = nn.Conv2d(c.c2 + 3 + 1, c.c2, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(c.c2, c.c2, kernel_size=3, stride=2, padding=1)                    # -> 8x7
        self.sp_fc = nn.Linear(c.c2 * 8 * 7, c.spatial_out)
        self.sp_ln = nn.LayerNorm(c.spatial_out)
        self.vec_fc = nn.Linear(N_ENV_VEC + NUM_SCALARS + NUM_LEDGER, c.vec_hidden)
        self.vec_ln = nn.LayerNorm(c.vec_hidden)
        self.fc1 = nn.Linear(c.spatial_out + c.vec_hidden, c.hidden)
        self.fc2 = nn.Linear(c.hidden, c.hidden)
        self.pi = nn.Linear(c.hidden, N_LOGITS)
        self.v = nn.Linear(c.hidden, 1)
        if c.readout not in ("global", "spatial"):
            raise ValueError(f"readout {c.readout!r}")
        if c.readout == "spatial":
            ch = c.c1 + c.c2
            self.pos_film = nn.Linear(c.hidden, ch)
            self.pos_conv = nn.Conv2d(ch, ch, kernel_size=3, padding=1)
            self.pos_out = nn.Conv2d(ch, 2 * G.M, kernel_size=1)
        for m in self.modules():
            if isinstance(m, (nn.Linear, nn.Conv2d)):
                nn.init.orthogonal_(m.weight, gain=math.sqrt(2))
                nn.init.zeros_(m.bias)
        nn.init.orthogonal_(self.pi.weight, gain=0.01)
        nn.init.zeros_(self.pi.bias)
        nn.init.orthogonal_(self.v.weight, gain=1.0)
        nn.init.zeros_(self.v.bias)
        if c.readout == "spatial":
            nn.init.zeros_(self.pos_out.weight)
            nn.init.zeros_(self.pos_out.bias)

    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def set_head_bias(self, bias: np.ndarray) -> None:
        with torch.no_grad():
            self.pi.bias.copy_(torch.as_tensor(bias, dtype=torch.float32))

    def _stem(self, tiles16: torch.Tensor, power: torch.Tensor) -> torch.Tensor:
        t16 = tiles16.long()
        idx = t16 & LOMASK
        flags = torch.stack([((t16 >> (FLAG_SHIFT + i)) & 1) for i in range(5)], dim=1).float()
        x = torch.cat([self.tile_emb(idx).permute(0, 3, 1, 2), flags, power.float().unsqueeze(1)], dim=1)
        return F.gelu(self.conv1(x))

    def forward(self, ob: Dict[str, torch.Tensor], vec: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        x = self._stem(ob["tiles16"], ob["power"])
        f30 = x                                                                  # (B, c1, 30, 25)
        half = F.avg_pool2d(ob["half"].float() / 255.0, 2)
        x = torch.cat([x, (ob["terrain"].float() / 128.0).unsqueeze(1), half], dim=1)
        x = F.gelu(self.conv2(x))
        e = ob["eighth"].float()
        e = torch.stack([e[:, 0] / 200.0, e[:, 1] / 256.0, e[:, 2] / 256.0], dim=1)
        x = torch.cat([x, e, (ob["com_rate"].float() / 64.0).unsqueeze(1)], dim=1)
        x = F.gelu(self.conv3(x))
        f15 = x                                                                  # (B, c2, 15, 13)
        x = F.gelu(self.conv4(x))
        sp = F.gelu(self.sp_ln(self.sp_fc(x.flatten(1))))
        v = torch.cat([vec.float(), symlog_t(ob["scalars"].float()) / 10.0, symlog_t(ob["ledger"].float()) / 10.0], dim=1)
        v = F.gelu(self.vec_ln(self.vec_fc(v)))
        h = F.gelu(self.fc1(torch.cat([sp, v], dim=1)))
        h = F.gelu(self.fc2(h))
        logits = self.pi(h)
        if self.cfg.readout == "spatial":
            logits = logits + self._position_scores(f30, f15, h)
        return logits, self.v(h).squeeze(1)

    def _position_scores(self, f30: torch.Tensor, f15: torch.Tensor, h: torch.Tensor) -> torch.Tensor:
        """(B, 1136) additions to the x and y heads' logits (zero elsewhere) from the spatial read-out."""
        up = F.interpolate(f15, size=f30.shape[-2:], mode="nearest")[..., :f30.shape[-2], :f30.shape[-1]]
        z = torch.cat([f30, up], dim=1) + self.pos_film(h)[:, :, None, None]
        z = self.pos_out(F.gelu(self.pos_conv(F.gelu(z))))                     # (B, 2M, 30, 25)
        B = z.shape[0]
        add = torch.zeros(B, N_LOGITS, dtype=z.dtype, device=z.device)
        for j in range(G.M):
            sx = torch.logsumexp(z[:, 2 * j], dim=2).repeat_interleave(READ_CELL, dim=1)[:, :WORLD_W]       # (B, 120)
            sy = torch.logsumexp(z[:, 2 * j + 1], dim=1).repeat_interleave(READ_CELL, dim=1)[:, :WORLD_H]   # (B, 100)
            hx, hy = X_HEADS[j], Y_HEADS[j]
            add[:, HEAD_OFF[hx]:HEAD_OFF[hx + 1]] = sx
            add[:, HEAD_OFF[hy]:HEAD_OFF[hy + 1]] = sy
        return add


def behaviour_head_bias(plans: np.ndarray, mix: float) -> np.ndarray:
    """Initial logits: log(mix * marginal of the head over behaviour plans + (1 - mix) * uniform), where a macro
    head's marginal counts only rows whose kind uses that head. ``plans``: (n, 25) canonical rows."""
    rows = G.clip_plan(np.asarray(plans).reshape(-1, N_COLS)).astype(np.int64)
    a = torch.from_numpy(rows[:, HEAD_COLS])
    used = used_heads(a).numpy()
    out = np.zeros(N_LOGITS, dtype=np.float64)
    for i, size in enumerate(HEAD_SIZES):
        v = rows[used[:, i], HEAD_COLS[i]]
        p = np.bincount(v, minlength=size)[:size].astype(np.float64)
        p = p / p.sum() if p.sum() > 0 else np.full(size, 1.0 / size)
        out[HEAD_OFF[i]:HEAD_OFF[i + 1]] = np.log(mix * p + (1.0 - mix) / size)
    return out.astype(np.float32)


# ----------------------------------------------------------------------------------------------
# Backends (batches of slots)
# ----------------------------------------------------------------------------------------------
class EmuEnv:
    """A batch of emulator states on the backend's device."""

    kind = "emulator"

    def __init__(self, emu, n: int, profile: bool = False) -> None:
        self.emu, self.n, self.device = emu, int(n), emu.device
        self.profile = bool(profile)          # synchronise the raster / model timers with the GPU
        self.state: Optional[Dict[str, torch.Tensor]] = None
        self._s0: Dict[str, Dict[str, torch.Tensor]] = {}
        self.t_raster = self.t_model = 0.0

    def _start(self, inst) -> Dict[str, torch.Tensor]:
        if inst.start_id not in self._s0:
            self._s0[inst.start_id] = self.emu.start_state(inst)
        return self._s0[inst.start_id]

    def reset(self, slots: Sequence[int], insts: Sequence, seeds: Sequence[int]) -> np.ndarray:
        if self.state is None:
            s0 = self._start(insts[0])
            self.state = {k: v.repeat(self.n, *([1] * (v.dim() - 1))).clone() for k, v in s0.items()}
        for e, inst in zip(slots, insts):
            for k, v in self._start(inst).items():
                self.state[k][e] = v[0]
        return self.scalars()[np.asarray(slots, dtype=np.int64)]

    def scalars(self) -> np.ndarray:
        return self.state["scalars"].double().cpu().numpy()

    def step(self, rows: np.ndarray) -> np.ndarray:
        dev = self.device
        sync = self.profile and dev.type == "cuda"
        t0 = time.perf_counter()
        r = raster_torch(rows, dev)
        a = act_scalars_torch(rows, dev)
        if sync:
            torch.cuda.synchronize(dev)
        t1 = time.perf_counter()
        self.state = self.emu.step(self.state, r, a)
        if sync:
            torch.cuda.synchronize(dev)
        self.t_raster += t1 - t0
        self.t_model += time.perf_counter() - t1
        return self.scalars()

    def packed(self) -> Dict[str, torch.Tensor]:
        return pack_state(self.state)

    def get_state(self) -> dict:
        return {"state": {k: v.cpu() for k, v in self.state.items()}}

    def set_state(self, d: dict) -> None:
        self.state = {k: v.to(self.device) for k, v in d["state"].items()}

    def month_steps(self) -> int:
        return self.emu.month_steps


class StubEmulator:
    """A toy stochastic dynamics with the emulator's state format, for tests (not a model of the engine).
    Start states are the engine's own start observations."""

    def __init__(self, device="cpu") -> None:
        self.device = torch.device(device)
        self.month_steps = 0
        self._s0: Dict[str, Dict[str, torch.Tensor]] = {}
        self.cost = torch.tensor([TOOL_COSTS[t] / float(G.FOOTPRINTS[t][2] * G.FOOTPRINTS[t][3]) for t in G.RASTER_TOOLS],
                                 dtype=torch.float64)

    def describe(self) -> dict:
        return {"judge": "stub"}

    def start_state(self, inst) -> Dict[str, torch.Tensor]:
        if inst.start_id not in self._s0:
            self._s0[inst.start_id] = engine_start_state(inst, self.device)
        return self._s0[inst.start_id]

    def step(self, state, raster, act):
        B = state["tile_index"].shape[0]
        s = {k: v.clone() for k, v in state.items()}
        sc = s["scalars"].double()
        r = raster.double()
        zones = r[:, 0:3].sum(dim=(2, 3)) / 9.0                                   # res, com, ind zones attempted
        spend = (r.sum(dim=(2, 3)) * self.cost.to(r.device)).sum(1)
        tax = act[:, 0].double() * 20.0
        fund = act[:, 1:4].double().mean(1)
        noise = torch.randn(B, 2, dtype=torch.float64, device=r.device)
        pop = sc[:, SC_POP]
        growth = 1.0 + 0.01 * (7.0 - tax) / 7.0 + 0.004 * fund + 0.01 * noise[:, 0]
        newpop = (pop * growth + 60.0 * zones.sum(1)).clamp(min=0)
        funds = sc[:, SC_FUNDS] + tax * pop / 400.0 - spend - 200.0 * fund + 300.0 * noise[:, 1]
        sc[:, SC_POP] = newpop.round()
        sc[:, SC_RES_POP] = (newpop / 20.0).round()
        sc[:, SC_FUNDS] = funds.round()
        sc[:, SC_TAX] = tax.round()
        sc[:, SC_TIME] = sc[:, SC_TIME] + 4
        sc[:, SC_UNPOWERED] = sc[:, SC_UNPOWERED] + zones.sum(1).round()
        sc[:, SC_COAL] = sc[:, SC_COAL] + (r[:, 12].sum(dim=(1, 2)) / 16.0).round()
        s["scalars"] = sc.to(state["scalars"].dtype)
        built = r[:, 0:3].amax(1) > 0
        s["tile_index"] = torch.where(built, torch.full_like(s["tile_index"], 244), s["tile_index"])
        s["flags"][:, 0] = torch.where(built, torch.ones_like(s["flags"][:, 0]), s["flags"][:, 0])
        s["half"] = (s["half"] * 0.95 + 5.0 * torch.rand_like(s["half"])).clamp(0, 255)
        self.month_steps += B
        return s

    def verdict_samples(self, inst, eff_plans: np.ndarray, K: int, stream: tuple) -> np.ndarray:
        torch.manual_seed(seed_for("rl-stub-verdict", inst.start_id, *stream))
        steps0 = self.month_steps
        P = np.asarray(eff_plans).reshape(-1, H, N_COLS)
        n = P.shape[0]
        s0 = self.start_state(inst)
        s = {k: v.repeat(n * K, *([1] * (v.dim() - 1))) for k, v in s0.items()}
        out = np.empty((n * K, H + 1, NUM_SCALARS))
        out[:, 0] = s["scalars"].double().numpy()
        for h in range(H):
            rows = np.repeat(P[:, h], K, axis=0)
            s = self.step(s, raster_torch(rows, self.device), act_scalars_torch(rows, self.device))
            out[:, h + 1] = s["scalars"].double().numpy()
        self.month_steps = steps0                 # verdict samples are not environment steps
        return out.reshape(n, K, H + 1, NUM_SCALARS)


def engine_start_state(inst, device) -> Dict[str, torch.Tensor]:
    """The start state in the loader's format, read from the engine as ``dc.oracle.replay`` reads it."""
    from .engine import Engine
    from .oracle import replay
    from .train import numpy_to_state, obs_to_numpy
    eng = Engine()
    try:
        rp = replay(eng, inst.cty, [], 0)
    finally:
        eng.close()
    return numpy_to_state(obs_to_numpy([rp.obs0], ledger=rp.ledger[:1]), device)


# -- the engine as an environment ---------------------------------------------------------------
class _EngineSlots:
    """Engine instances keyed by slot, driven in ``dc.oracle.replay``'s month order."""

    def __init__(self) -> None:
        self.eng: Dict[int, object] = {}

    def _get(self, slot: int):
        from .engine import Engine
        if slot not in self.eng:
            self.eng[slot] = Engine()
        return self.eng[slot]

    def reset(self, slot: int, cty: str, seed: int):
        e = self._get(slot)
        e.load_start(cty)
        e.set_disasters(False)
        obs = e.observe()
        e.seed(int(seed))
        return pack_engine_obs(obs, ledger=e.ledger())

    def step(self, slot: int, row: np.ndarray):
        e = self.eng[slot]
        act, dis = G.compile_month(row)
        e.apply(act)
        if dis:
            e.force_disaster(dis)
        e.step_month()
        return pack_engine_obs(e.observe())

    def handle(self, msg):
        cmd = msg[0]
        if cmd == "reset":
            return {s: self.reset(s, c, sd) for s, c, sd in msg[1]}
        if cmd == "step":
            return {s: self.step(s, r) for s, r in msg[1].items()}
        if cmd == "restore":
            out = {}
            for s, c, sd, rows in msg[1]:
                out[s] = self.reset(s, c, sd)
                for r in rows:
                    out[s] = self.step(s, r)
            return out
        raise ValueError(cmd)

    def close(self) -> None:
        for e in self.eng.values():
            e.close()
        self.eng = {}


def _engine_worker(conn) -> None:
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    torch.set_num_threads(1)
    slots = _EngineSlots()
    while True:
        msg = conn.recv()
        if msg[0] == "close":
            slots.close()
            conn.close()
            return
        try:
            conn.send(("ok", slots.handle(msg)))
        except Exception as ex:  # pragma: no cover
            conn.send(("error", repr(ex)))


class EngineEnv:
    """Slots on real engines (``dc.engine.Engine``), spread over ``workers`` processes (0: this process).
    Each slot keeps its seed and its action log since the last reset, so ``get_state`` / ``set_state``
    restore a slot by replaying it from the start (there is no state injection)."""

    kind = "engine"

    def __init__(self, n: int, workers: int = 0, device="cpu") -> None:
        self.n, self.workers, self.device = int(n), int(workers), torch.device(device)
        self.cty: List[str] = [""] * self.n
        self.seed: List[int] = [0] * self.n
        self.rows: List[List[np.ndarray]] = [[] for _ in range(self.n)]
        self.obs: List[Optional[Dict[str, np.ndarray]]] = [None] * self.n
        self.city_months = 0
        self.t_engine = 0.0
        if self.workers > 0:
            import multiprocessing as mp
            ctx = mp.get_context("spawn")
            self.conns, self.procs = [], []
            for _ in range(self.workers):
                a, b = ctx.Pipe()
                p = ctx.Process(target=_engine_worker, args=(b,), daemon=True)
                p.start()
                self.conns.append(a)
                self.procs.append(p)
        else:
            self.local = _EngineSlots()

    def _owner(self, slot: int) -> int:
        return slot % self.workers

    def _call(self, cmd: str, per_slot: Dict[int, object]) -> Dict[int, dict]:
        t0 = time.perf_counter()
        if self.workers == 0:
            payload = per_slot if cmd == "step" else list(per_slot.values())
            out = self.local.handle((cmd, payload))
        else:
            parts: Dict[int, Dict[int, object]] = {}
            for s, v in per_slot.items():
                parts.setdefault(self._owner(s), {})[s] = v
            for w, d in parts.items():
                self.conns[w].send((cmd, d if cmd == "step" else list(d.values())))
            out = {}
            for w in parts:
                st, res = self.conns[w].recv()
                if st != "ok":
                    raise RuntimeError(f"engine worker {w}: {res}")
                out.update(res)
        self.t_engine += time.perf_counter() - t0
        return out

    def reset(self, slots: Sequence[int], insts: Sequence, seeds: Sequence[int]) -> np.ndarray:
        req = {}
        for e, inst, sd in zip(slots, insts, seeds):
            self.cty[e], self.seed[e], self.rows[e] = str(inst.cty), int(sd), []
            req[e] = (e, str(inst.cty), int(sd))
        for e, ob in self._call("reset", req).items():
            self.obs[e] = ob
        return np.stack([self.obs[e]["scal64"] for e in slots]) if len(slots) else np.zeros((0, NUM_SCALARS))

    def scalars(self) -> np.ndarray:
        raise NotImplementedError("engine scalars are int64; use the values returned by step / reset")

    def step(self, rows: np.ndarray) -> np.ndarray:
        rows = np.asarray(rows, dtype=np.int16)
        req = {e: rows[e] for e in range(self.n)}
        for e in range(self.n):
            self.rows[e].append(rows[e].copy())
        for e, ob in self._call("step", req).items():
            self.obs[e] = ob
        self.city_months += self.n
        return self.last_scalars()

    def last_scalars(self) -> np.ndarray:
        return np.stack([self.obs[e]["scal64"] for e in range(self.n)])

    def packed(self) -> Dict[str, torch.Tensor]:
        return stack_packed(self.obs, self.device)

    def get_state(self) -> dict:
        return {"cty": list(self.cty), "seed": list(self.seed), "rows": [np.array(r, dtype=np.int16).reshape(-1, N_COLS)
                                                                          for r in self.rows]}

    def set_state(self, d: dict) -> None:
        req = {}
        for e in range(self.n):
            self.cty[e], self.seed[e] = d["cty"][e], int(d["seed"][e])
            self.rows[e] = [r.copy() for r in np.asarray(d["rows"][e]).reshape(-1, N_COLS)]
            req[e] = (e, self.cty[e], self.seed[e], self.rows[e])
        for e, ob in self._call("restore", req).items():
            self.obs[e] = ob

    def month_steps(self) -> int:
        return self.city_months

    def close(self) -> None:
        if self.workers > 0:
            for c in self.conns:
                try:
                    c.send(("close",))
                except Exception:  # pragma: no cover
                    pass
            for p in self.procs:
                p.join(timeout=30)
                if p.is_alive():  # pragma: no cover
                    p.kill()
            self.workers = 0
            self.local = _EngineSlots()
        else:
            self.local.close()


class StubEnv(EmuEnv):
    kind = "stub"


# ----------------------------------------------------------------------------------------------
# The task environment
# ----------------------------------------------------------------------------------------------
def _by_month(t: np.ndarray):
    """(month, row indices) for each distinct month in ``t``."""
    t = np.asarray(t)
    for tt in np.unique(t):
        yield int(tt), np.flatnonzero(t == tt)


def prefix_margin(inst, traj: np.ndarray, t: np.ndarray) -> np.ndarray:
    """The instance's task margin (``dc.tasks`` through ``dc.rl_adaptor.task_margin``) of each row's trajectory so
    far: the bare prefix of months 0..t[row] (at t = 0 the start row alone, which ``dc.tasks`` defines)."""
    out = np.zeros(traj.shape[0])
    for tt, sel in _by_month(t):
        out[sel] = RA.task_margin(inst, traj[sel, :tt + 1])
    return out


def start_margin(inst, row0: np.ndarray) -> float:
    """The margin of a trajectory that has only its start row."""
    return float(RA.task_margin(inst, np.asarray(row0, dtype=np.float64).reshape(1, 1, -1))[0])


class TaskVecEnv:
    """``n_envs`` slots of one task family over its n instances. Slot e plays instance (e + k E) mod n in its k-th
    episode (E = n_envs): every round of episodes covers E consecutive instance indices, so instances get equal
    shares when n does not divide E (with n dividing E it is instance e mod n throughout)."""

    def __init__(self, backend, instances: Sequence, n_envs: int, run_key: str, auto_reset: bool = True,
                 slot_seeds: Optional[Sequence[int]] = None) -> None:
        self.b = backend
        self.inst = list(instances)
        self.task = self.inst[0].task
        assert all(i.task == self.task for i in self.inst), "one task family per environment"
        self.n_inst = len(self.inst)
        self.E = int(n_envs)
        self.run_key = run_key
        self.auto_reset = auto_reset
        self.slot_seeds = None if slot_seeds is None else [int(s) for s in slot_seeds]
        if self.slot_seeds is not None and len(self.slot_seeds) != self.E:
            raise ValueError("slot_seeds: one seed per slot")
        self.traj = np.zeros((self.E, H + 1, NUM_SCALARS))
        self.plans = np.zeros((self.E, H, N_COLS), dtype=np.int16)
        self.t = np.zeros(self.E, dtype=np.int64)
        self.episode = np.zeros(self.E, dtype=np.int64)
        self.margin = np.zeros(self.E)
        self.start_margin = np.zeros(self.E)
        self._assign(np.arange(self.E))
        self.finished: List[dict] = []
        self.t_host = 0.0
        self._reserved: Dict[str, frozenset] = {}

    def _assign(self, slots: np.ndarray) -> None:
        if not hasattr(self, "slot_inst"):
            self.slot_inst = np.zeros(self.E, dtype=np.int64)
            self.theta = np.zeros(self.E)
            self.stat_sd = np.zeros(self.E)
        self.slot_inst[slots] = (slots + self.episode[slots] * self.E) % self.n_inst
        self.theta[slots] = [self.inst[i].theta for i in self.slot_inst[slots]]
        self.stat_sd[slots] = [self.inst[i].stat_sd for i in self.slot_inst[slots]]

    def _groups(self, slots: np.ndarray):
        """(instance, the given slots on it) for each instance among ``slots``."""
        si = self.slot_inst[slots]
        for g in np.unique(si):
            yield self.inst[int(g)], slots[si == g]

    def _seeds(self, slots) -> List[int]:
        """Engine seeds: the given per-slot seeds, or ``seed_for("rl-engine-train", run, slot, episode)`` redrawn
        past every reserved seed of the start (the oracle's and the nine residual seeds of all its tasks); asserted."""
        if self.slot_seeds is not None:
            return [self.slot_seeds[e] for e in slots]
        if getattr(self.b, "kind", "") != "engine":
            return [0] * len(slots)                      # the emulator and the stub take no seed
        out = []
        for e in slots:
            sid = self.inst[self.slot_inst[e]].start_id
            if sid not in self._reserved:
                self._reserved[sid] = RA.reserved_seeds(sid)
            s, _ = RA.fresh_seed(("rl-engine-train", self.run_key, int(e), int(self.episode[e])), self._reserved[sid])
            if s in self._reserved[sid]:
                raise RuntimeError(f"training seed {s} is reserved on {sid}")
            out.append(s)
        return out

    def _margins(self, slots: np.ndarray) -> np.ndarray:
        out = np.zeros(self.E)
        for inst, sel in self._groups(np.asarray(slots)):
            out[sel] = prefix_margin(inst, self.traj[sel], self.t[sel])
        return out[np.asarray(slots)]

    def _reset_slots(self, slots: np.ndarray) -> None:
        if slots.size == 0:
            return
        self._assign(slots)
        sc = self.b.reset([int(e) for e in slots], [self.inst[self.slot_inst[e]] for e in slots], self._seeds(slots))
        self.traj[slots] = 0.0
        self.traj[slots, 0] = sc
        self.plans[slots] = 0
        self.t[slots] = 0
        m = self._margins(slots)
        self.margin[slots] = m
        self.start_margin[slots] = m

    def reset_all(self) -> None:
        self._reset_slots(np.arange(self.E))

    def vec(self) -> np.ndarray:
        """(E, 74) environment features (module docstring): ``taskfree_features`` plus the task-dependent columns."""
        E = self.E
        v = taskfree_features(self.traj, self.t)
        v[:, T.TASKS.index(self.task)] = 1.0
        o = _VEC_TAIL
        stat = np.zeros(E)
        feas = np.zeros(E)
        for inst, members in self._groups(np.arange(E)):
            for tt, k in _by_month(self.t[members]):
                sel = members[k]
                pre = self.traj[sel, :tt + 1]                          # the bare trajectory so far
                stat[sel] = (RA.task_statistic(inst, pre) - inst.theta) / max(inst.stat_sd, 1e-9)
                feas[sel] = RA.task_feasible(inst, pre)
        v[:, o + 0] = np.clip(self.margin, -10, 10)
        v[:, o + 1] = np.clip(stat, -10, 10)
        v[:, o + 3] = feas
        v[:, o + 4] = symlog_np(self.theta) / 10.0
        return v

    def obs(self):
        return self.b.packed(), self.vec()

    def tax_cap(self) -> Optional[np.ndarray]:
        """(E,) the start rate of every slot's episode (scalar ``tax`` of its start row) in ``MASKED_TAX_TASKS``; None
        elsewhere."""
        if self.task not in MASKED_TAX_TASKS:
            return None
        return self.traj[:, 0, SC_TAX].astype(np.int64)

    def step(self, rows: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Advance every slot one month with canonical rows (E, 25). Returns (rewards, dones)."""
        eff = effective_rows(rows, self.task, self.t)
        sc = self.b.step(eff)
        t0 = time.perf_counter()
        E = np.arange(self.E)
        self.plans[E, self.t] = eff
        self.t += 1
        self.traj[E, self.t] = sc
        m = self._margins(E)
        rew = m - self.margin
        self.margin = m
        done = self.t == H
        dslots = np.flatnonzero(done)
        for e in dslots:
            self.finished.append({"slot": int(e), "instance": int(self.slot_inst[e]), "episode": int(self.episode[e]),
                                  "final_margin": float(self.margin[e]), "start_margin": float(self.start_margin[e])})
        self.t_host += time.perf_counter() - t0
        if self.auto_reset and dslots.size:
            self.episode[dslots] += 1
            self._reset_slots(dslots)
        return rew, done

    def get_state(self) -> dict:
        return {"traj": self.traj.copy(), "plans": self.plans.copy(), "t": self.t.copy(), "episode": self.episode.copy(),
                "margin": self.margin.copy(), "start_margin": self.start_margin.copy(), "backend": self.b.get_state()}

    def set_state(self, d: dict) -> None:
        for k in ("traj", "plans", "t", "episode", "margin", "start_margin"):
            setattr(self, k, np.array(d[k]))
        self._assign(np.arange(self.E))
        self.b.set_state(d["backend"])


# ----------------------------------------------------------------------------------------------
# PPO
# ----------------------------------------------------------------------------------------------
@dataclass
class RLConfig:
    n_envs: int = 200
    rollout_len: int = 25
    budget: int = 1_000_000
    snapshots: Tuple[int, ...] = (250_000, 500_000, 1_000_000)
    lr: float = 3e-4
    adam_eps: float = 1e-5
    epochs: int = 4
    minibatch: int = 1000
    clip: float = 0.2
    gamma: float = 1.0
    gae_lambda: float = 0.95
    ent_coef: float = 0.003
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5
    init_mix: float = 0.9                 # head biases: log(mix * behaviour marginal + (1 - mix) * uniform)
    init_plans: int = 200                 # behaviour plans per start for the marginals
    save_every: int = 10                  # iterations between resumable checkpoints
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    # learner options of round 2 (part B); the defaults are the learner
    target_kl: Optional[float] = None     # stop the iteration's epoch loop at the first minibatch whose approximate
                                          # KL (before its step) exceeds 1.5 x target_kl
    lr_schedule: str = "constant"         # "linear": lr x (1 - k / n_iter) in iteration k (0-based)
    ent_schedule: str = "constant"        # "linear": ent_coef x (1 - k / n_iter) in iteration k
    # options of the warm start . Both need the
    # run to start from an initial policy (``Trainer(init_policy=...)``, the cloned policy of ``dc.bc``).
    value_warmup_iters: int = 0           # iterations 0..n-1 update the value head's own weights only (the policy and
                                          # the shared trunk are not changed); their months count in the budget
    value_warmup_ev: Optional[float] = None   # set: the warm-up ends at the first iteration whose explained variance
                                          # (value head before the update, on that iteration's data) reaches this
                                          # value; that iteration and all later ones are full PPO updates
    ref_kl_coef: float = 0.0              # penalty on KL(policy || initial policy) of the month distribution
                                          # (``month_kl``), mean over the minibatch, in the loss beside the PPO terms
    ref_kl_frac: float = 0.0              # the penalty's coefficient decays linearly to 0 over this share of iterations
    # round 4 : the hybrid start and the treasury tax cap
    reinit_budget_heads: bool = False     # the initial policy's tax and funding heads (``BUDGET_HEADS``) re-initialised
                                          # exactly as a fresh policy of the run initialises them (``hybrid_state``)
    mask_treasury_tax: bool = False       # in ``MASKED_TAX_TASKS`` the tax head's values above the start rate are
                                          # masked (training, sampled and greedy evaluation; ``cap_tax``)

    @property
    def months_per_iter(self) -> int:
        return self.n_envs * self.rollout_len

    def check(self) -> None:
        per = self.months_per_iter
        if self.budget % per:
            raise ValueError(f"budget {self.budget} is not a multiple of n_envs x rollout_len = {per}")
        for s in self.snapshots:
            if s % per or s > self.budget or s < 0:
                raise ValueError(f"snapshot {s} is not a multiple of {per} within the budget {self.budget}")
        if self.months_per_iter % self.minibatch:
            raise ValueError("minibatch must divide n_envs x rollout_len")
        if self.lr_schedule not in ("constant", "linear") or self.ent_schedule not in ("constant", "linear"):
            raise ValueError("schedules: constant or linear")
        if self.target_kl is not None and not self.target_kl > 0:
            raise ValueError("target_kl must be positive")
        if self.value_warmup_iters < 0 or self.ref_kl_coef < 0:
            raise ValueError("value_warmup_iters and ref_kl_coef must not be negative")
        if self.ref_kl_coef > 0 and not 0 < self.ref_kl_frac <= 1:
            raise ValueError("ref_kl_frac must lie in (0, 1] when ref_kl_coef is set")

    @property
    def n_iter(self) -> int:
        return self.budget // self.months_per_iter

    @property
    def needs_init(self) -> bool:
        """The learner starts from a given policy (warm start options set)."""
        return self.value_warmup_iters > 0 or self.ref_kl_coef > 0 or self.reinit_budget_heads

    def lr_at(self, k: int) -> float:
        return self.lr * (1.0 - k / self.n_iter) if self.lr_schedule == "linear" else self.lr

    def ent_at(self, k: int) -> float:
        return self.ent_coef * (1.0 - k / self.n_iter) if self.ent_schedule == "linear" else self.ent_coef

    def ref_kl_at(self, k: int) -> float:
        """ref_kl_coef x (1 - k / (ref_kl_frac x n_iter)), not below 0."""
        if self.ref_kl_coef <= 0:
            return 0.0
        return self.ref_kl_coef * max(0.0, 1.0 - k / (self.ref_kl_frac * self.n_iter))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["snapshots"] = list(self.snapshots)
        return d

    @staticmethod
    def from_dict(d: dict) -> "RLConfig":
        """Also reads the configurations, which lack the round-2 fields ."""
        d = dict(d)
        d["policy"] = PolicyConfig(**d.get("policy", {}))
        d["snapshots"] = tuple(d["snapshots"])
        return RLConfig(**d)

    def same_learner(self, other: "RLConfig") -> bool:
        """Equal, counting a field the configurations lack as its default."""
        return RLConfig.from_dict(self.to_dict()).to_dict() == RLConfig.from_dict(other.to_dict()).to_dict()


B8_LEARNER = RLConfig()
# Learner variants tried in round 2, part B (engine only; ``run_rl.py --variant``). Each is the learner with
# the changes named; "frozen" is the one every run of the arm uses (``FROZEN``).
VARIANTS: Dict[str, RLConfig] = {
    "b8": B8_LEARNER,
    "stab": replace(B8_LEARNER, target_kl=0.02, lr_schedule="linear", ent_schedule="linear"),
    "spatial": replace(B8_LEARNER, policy=PolicyConfig(readout="spatial")),
    "stab_spatial": replace(B8_LEARNER, target_kl=0.02, lr_schedule="linear", ent_schedule="linear",
                            policy=PolicyConfig(readout="spatial")),
}
# Frozen at 11:49Z on 2026-11-10 (round 2, part B) by the rule fixed at 10:23Z: of "b8" and the sixth tuning run's
# variant, the higher mean oracle pass rate at 1,000,000 months over power and grow (the working notes).
STAB_SPATIAL = VARIANTS["stab_spatial"]
FROZEN = STAB_SPATIAL                            # until the analysis plan
# Warm start : PPO from the cloned policy of ``dc.bc`` (``run_rl.py --init-from``) with the
# frozen settings unchanged ("bc"), and the same with a penalty on KL(policy || cloned policy) of the month
# distribution whose coefficient decays linearly from 1 (per month, in nats) to 0 over the first 20 per cent of the
# iterations ("bc_kl"). The value head starts untrained in both, and a value-only warm-up runs first: iterations that
# update the value head's own weights alone until the head explains a non-negative share of the iteration's return
# variance (measured before the update), at most ``BC_VALUE_WARMUP`` iterations. Decided on the engine, plain variant,
# `power`, seed 0 : without it the first iteration's explained variance was -4.74 and every update stopped
# after one minibatch step; two fixed warm-up iterations left it at -1.51.
BC_VALUE_WARMUP = 10
VARIANTS["bc"] = replace(STAB_SPATIAL, value_warmup_iters=BC_VALUE_WARMUP, value_warmup_ev=0.0)
VARIANTS["bc_kl"] = replace(STAB_SPATIAL, value_warmup_iters=BC_VALUE_WARMUP, value_warmup_ev=0.0, ref_kl_coef=1.0,
                            ref_kl_frac=0.2)
# Round 4 . The treasury task's tax cap (never above the start rate) is an action constraint for every
# learner: the frozen learner is "stab_spatial" with the mask (it changes nothing outside ``MASKED_TAX_TASKS``). The
# hybrid start ("hybrid"): the cloned policy with its tax and funding heads re-initialised as the run's fresh policy
# initialises them (``hybrid_state``); PPO plain, with the value warm-up of "bc".
FROZEN = replace(STAB_SPATIAL, mask_treasury_tax=True)
VARIANTS["hybrid"] = replace(STAB_SPATIAL, value_warmup_iters=BC_VALUE_WARMUP, value_warmup_ev=0.0,
                             reinit_budget_heads=True, mask_treasury_tax=True)
INIT_VARIANTS = ("bc", "bc_kl", "hybrid")        # learners that start from a given policy


def _atomic_save(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    torch.save(obj, tmp)
    os.replace(tmp, path)


class Trainer:
    """PPO over a ``TaskVecEnv``. ``run_dir`` holds ``latest.pt`` (resumable), ``snap_<months>.pt`` and
    ``log.jsonl``. ``train(stop_after_iters=None)`` resumes from ``latest.pt`` when it exists."""

    def __init__(self, cfg: RLConfig, env: TaskVecEnv, run_dir, run_key: str, device="cpu", init_bias=None,
                 meta: Optional[dict] = None, init_key: Optional[str] = None, log=print, profile: bool = False,
                 buffer_device=None, update_chunk: Optional[int] = None,
                 init_policy: Optional[Dict[str, torch.Tensor]] = None) -> None:
        """``init_policy``: the weights the policy starts from (the cloned policy; then ``init_bias`` is not used) and
        the reference of ``kl_to_init`` in the log and of the ``ref_kl_coef`` penalty."""
        cfg.check()
        if cfg.needs_init and init_policy is None:
            raise ValueError("value_warmup_iters / ref_kl_coef need an initial policy")
        self.cfg, self.env, self.run_dir, self.run_key = cfg, env, Path(run_dir), run_key
        self.device = torch.device(device)
        # where the iteration's observations are kept for the update (the policy's device, or the host to keep the
        # card's memory small; the same tensors either way)
        self.buf_device = torch.device(buffer_device) if buffer_device is not None else self.device
        # rows per forward / backward pass in the update (None: the whole minibatch); smaller chunks accumulate the
        # same gradient with less memory on the card
        self.update_chunk = int(update_chunk) if update_chunk else None
        self.meta = meta or {}
        self.log = log
        self.profile = bool(profile)             # synchronise the timers with the GPU (no effect on any number)
        torch.manual_seed(seed_for("rl-init", init_key or run_key))   # same initial policy for a (task, seed) on every checkpoint
        self.policy = Policy(cfg.policy).to(self.device)
        self.ref_policy: Optional[Policy] = None
        if init_policy is not None:
            if cfg.reinit_budget_heads:              # the hybrid start: the budget heads as this run's fresh policy's
                if init_bias is None:
                    raise ValueError("reinit_budget_heads needs the fresh policy's head biases (init_bias)")
                self.policy.set_head_bias(init_bias)
                init_policy = hybrid_state(init_policy, self.policy.state_dict())
            self.policy.load_state_dict(init_policy)
            self.ref_policy = Policy(cfg.policy).to(self.device)
            self.ref_policy.load_state_dict(init_policy)
            self.ref_policy.eval()
            for p in self.ref_policy.parameters():
                p.requires_grad_(False)
        elif init_bias is not None:
            self.policy.set_head_bias(init_bias)
        self.opt = torch.optim.Adam(self.policy.parameters(), lr=cfg.lr, eps=cfg.adam_eps)
        self.iteration = 0
        self.warmup_over = False              # the value warm-up has ended (``RLConfig.value_warmup_ev``)
        self.tax_mask = bool(cfg.mask_treasury_tax and env.task in MASKED_TAX_TASKS)
        self.months = 0
        self.episodes = 0
        self.timing = {"env_step": 0.0, "policy_forward": 0.0, "update": 0.0, "host": 0.0}
        self.run_dir.mkdir(parents=True, exist_ok=True)

    # -- persistence ---------------------------------------------------------------------------
    def _ckpt(self) -> dict:
        return {"version": RL_VERSION, "cfg": self.cfg.to_dict(), "run_key": self.run_key, "iteration": self.iteration,
                "months": self.months, "episodes": self.episodes, "warmup_over": self.warmup_over,
                "policy": self.policy.state_dict(),
                "opt": self.opt.state_dict(), "env": self.env.get_state(), "meta": self.meta}

    def save_latest(self) -> None:
        _atomic_save(self._ckpt(), self.run_dir / "latest.pt")

    def resume(self) -> bool:
        p = self.run_dir / "latest.pt"
        if not p.exists():
            return False
        ck = torch.load(p, map_location="cpu", weights_only=False)
        if ck["cfg"] != self.cfg.to_dict() or ck["run_key"] != self.run_key:
            raise RuntimeError(f"{p} was written by another configuration or run")
        self.policy.load_state_dict(ck["policy"])
        self.opt.load_state_dict(ck["opt"])
        self.env.set_state(ck["env"])
        self.iteration, self.months, self.episodes = ck["iteration"], ck["months"], ck["episodes"]
        self.warmup_over = bool(ck.get("warmup_over", False))
        lp = self.run_dir / "log.jsonl"          # drop log lines of iterations after the resumed state
        if lp.exists():
            keep = [ln for ln in lp.read_text().splitlines() if ln.strip() and json.loads(ln)["iteration"] <= self.iteration]
            lp.write_text("".join(ln + "\n" for ln in keep))
        return True

    def snapshot_path(self, months: int) -> Path:
        return self.run_dir / f"snap_{months:09d}.pt"

    def save_snapshot(self) -> None:
        _atomic_save({"version": RL_VERSION, "cfg": self.cfg.to_dict(), "run_key": self.run_key, "months": self.months,
                      "iteration": self.iteration, "episodes": self.episodes, "policy": self.policy.state_dict(),
                      "meta": self.meta}, self.snapshot_path(self.months))

    def _log(self, rec: dict) -> None:
        with open(self.run_dir / "log.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")

    # -- one iteration -------------------------------------------------------------------------
    def _sync(self) -> None:
        if self.profile and self.device.type == "cuda":
            torch.cuda.synchronize(self.device)

    def iterate(self) -> dict:
        cfg, env, k = self.cfg, self.env, self.iteration
        E, L = env.E, cfg.rollout_len
        torch.manual_seed(seed_for("rl-env", self.run_key, k))
        gen = torch.Generator(device=self.device)
        gen.manual_seed(seed_for("rl-act", self.run_key, k))
        tim = {"env_step": 0.0, "policy_forward": 0.0, "update": 0.0, "host": 0.0}
        buf_ob: Dict[str, List[torch.Tensor]] = {key: [] for key in PACK_KEYS}
        buf_vec, buf_a, buf_lp, buf_v, buf_r, buf_d = [], [], [], [], [], []
        n_fin0 = len(env.finished)
        steps_before = env.b.month_steps()
        self.policy.eval()
        kl_init = []                                 # KL(policy || initial policy) on the iteration's states
        buf_cap: List[torch.Tensor] = []             # the tax cap of every row (masked tasks)
        for _ in range(L):
            t0 = time.perf_counter()
            ob, vec = env.obs()
            ob_d = {key: x.to(self.device) for key, x in ob.items()}
            vec_t = torch.from_numpy(vec).to(self.device)
            self._sync()
            t1 = time.perf_counter()
            cap = torch.from_numpy(env.tax_cap()).to(self.device) if self.tax_mask else None
            with torch.no_grad():
                logits, value = self.policy(ob_d, vec_t)
                logits = cap_tax(logits, cap)
                a = sample_actions(logits, gen)
                lp, _ = logp_entropy(logits, a)
                if self.ref_policy is not None:
                    kl_init.append(month_kl(logits, cap_tax(self.ref_policy(ob_d, vec_t)[0], cap)).mean())
            if cap is not None:
                buf_cap.append(cap)
            self._sync()
            t2 = time.perf_counter()
            rows = actions_to_rows(a)
            for key in PACK_KEYS:
                buf_ob[key].append(ob[key].to(self.buf_device))
            buf_vec.append(vec_t.to(self.buf_device))
            buf_a.append(a)
            buf_lp.append(lp)
            buf_v.append(value)
            t3 = time.perf_counter()
            r, d = env.step(rows)
            t4 = time.perf_counter()
            buf_r.append(torch.from_numpy(r).to(self.device, torch.float32))
            buf_d.append(torch.from_numpy(d.astype(np.float32)).to(self.device))
            tim["policy_forward"] += t2 - t1
            tim["env_step"] += t4 - t3
            tim["host"] += (t1 - t0) + (t3 - t2) + (time.perf_counter() - t4)
        n_steps = env.b.month_steps() - steps_before
        if n_steps != E * L:
            raise RuntimeError(f"iteration {k}: {n_steps} month-steps taken, {E * L} expected")
        ob, vec = env.obs()
        with torch.no_grad():
            _, v_last = self.policy({key: x.to(self.device) for key, x in ob.items()}, torch.from_numpy(vec).to(self.device))
        R = torch.stack(buf_r)
        D = torch.stack(buf_d)
        V = torch.stack(buf_v)
        adv = torch.zeros_like(R)
        last = torch.zeros(E, device=self.device)
        for t in reversed(range(L)):
            nv = v_last if t == L - 1 else V[t + 1]
            delta = R[t] + cfg.gamma * (1 - D[t]) * nv - V[t]
            last = delta + cfg.gamma * cfg.gae_lambda * (1 - D[t]) * last
            adv[t] = last
        ret = adv + V
        with torch.no_grad():                        # the value head's explained variance before the update (logged in
            r64, v64 = ret.double(), V.double()      # warm-started runs)
            ev_before = float(1.0 - (r64 - v64).var() / r64.var().clamp(min=1e-12))
        N = E * L
        obs_flat = {key: torch.stack(v).reshape(N, *v[0].shape[1:]) for key, v in buf_ob.items()}
        vec_flat = torch.stack(buf_vec).reshape(N, -1)
        a_flat = torch.stack(buf_a).reshape(N, -1)
        lp_flat = torch.stack(buf_lp).reshape(N)
        cap_flat = torch.stack(buf_cap).reshape(N) if buf_cap else None
        adv_flat = adv.reshape(N)
        ret_flat = ret.reshape(N)
        # update
        self._sync()
        t0 = time.perf_counter()
        self.policy.train()
        lr_k, ent_k = cfg.lr_at(k), cfg.ent_at(k)
        warm = k < cfg.value_warmup_iters and not self.warmup_over   # value warm-up: only the value head's weights
        if warm and cfg.value_warmup_ev is not None and ev_before >= cfg.value_warmup_ev:  # take steps
            warm = False
        if not warm and cfg.value_warmup_iters > 0:
            self.warmup_over = True
        kl_k = cfg.ref_kl_at(k) if self.ref_policy is not None and not warm else 0.0
        if warm:
            vparams = {id(p) for p in self.policy.v.parameters()}
            for p in self.policy.parameters():
                p.requires_grad_(id(p) in vparams)
        for pg_ in self.opt.param_groups:
            pg_["lr"] = lr_k
        stats = {"pg_loss": 0.0, "v_loss": 0.0, "entropy": 0.0, "approx_kl": 0.0, "clip_frac": 0.0}
        if kl_k > 0:
            stats["ref_kl"] = 0.0
        n_mb = 0
        stopped = False
        for ep in range(cfg.epochs):
            g = torch.Generator()
            g.manual_seed(seed_for("rl-perm", self.run_key, k, ep))
            perm = torch.randperm(N, generator=g)
            for s in range(0, N, cfg.minibatch):
                idx = perm[s:s + cfg.minibatch]
                M = int(idx.numel())
                ad_all = adv_flat[idx.to(self.device)]
                mu, sd = ad_all.mean(), ad_all.std()             # advantages normalised over the whole minibatch
                chunk = min(self.update_chunk or M, M)
                self.opt.zero_grad(set_to_none=True)
                acc = {key: 0.0 for key in stats}
                for c0 in range(0, M, chunk):                    # one chunk unless update_chunk < minibatch: the
                    ic = idx[c0:c0 + chunk]                      # gradient of the minibatch's loss, accumulated
                    w = ic.numel() / M
                    ic_b, ic_d = ic.to(self.buf_device), ic.to(self.device)
                    mb_ob = {key: x[ic_b].to(self.device, non_blocking=True) for key, x in obs_flat.items()}
                    mb_vec = vec_flat[ic_b].to(self.device)
                    logits, v = self.policy(mb_ob, mb_vec)
                    mb_cap = cap_flat[ic_d] if cap_flat is not None else None
                    logits = cap_tax(logits, mb_cap)
                    lp, ent = logp_entropy(logits, a_flat[ic_d])
                    ratio = torch.exp(lp - lp_flat[ic_d])
                    ad = (adv_flat[ic_d] - mu) / (sd + 1e-8)
                    pg = -torch.min(ratio * ad, ratio.clamp(1 - cfg.clip, 1 + cfg.clip) * ad).mean()
                    vl = 0.5 * (v - ret_flat[ic_d]).pow(2).mean()
                    if warm:
                        loss = cfg.vf_coef * vl * w
                    else:
                        loss = (pg + cfg.vf_coef * vl - ent_k * ent.mean()) * w
                    if kl_k > 0:
                        with torch.no_grad():
                            ref_logits = cap_tax(self.ref_policy(mb_ob, mb_vec)[0], mb_cap)
                        rk = month_kl(logits, ref_logits).mean()
                        loss = loss + kl_k * rk * w
                        acc["ref_kl"] += float(rk.detach()) * w
                    loss.backward()
                    with torch.no_grad():
                        acc["pg_loss"] += float(pg) * w
                        acc["v_loss"] += float(vl) * w
                        acc["entropy"] += float(ent.mean()) * w
                        acc["approx_kl"] += float(((ratio - 1) - torch.log(ratio)).mean()) * w
                        acc["clip_frac"] += float(((ratio - 1).abs() > cfg.clip).float().mean()) * w
                if cfg.target_kl is not None and acc["approx_kl"] > 1.5 * cfg.target_kl:
                    self.opt.zero_grad(set_to_none=True)
                    stopped = True                       # this minibatch takes no step; the iteration's update ends
                    break
                nn.utils.clip_grad_norm_(self.policy.parameters(), cfg.max_grad_norm)   # (warm-up: the value head's)
                self.opt.step()
                for key in stats:
                    stats[key] += acc[key]
                n_mb += 1
            if stopped:
                break
        if warm:
            for p in self.policy.parameters():
                p.requires_grad_(True)
        self._sync()
        tim["update"] = time.perf_counter() - t0
        self.iteration += 1
        self.months += n_steps
        fin = env.finished[n_fin0:]
        env.finished = env.finished[:n_fin0]          # keep memory flat; the log holds the summary
        self.episodes += len(fin)
        fm = np.array([f["final_margin"] for f in fin]) if fin else np.zeros(0)
        rec = {"iteration": self.iteration, "months": self.months, "episodes_finished": len(fin),
               "episodes_total": self.episodes,
               "final_margin_mean": float(fm.mean()) if fm.size else None,
               "accept_rate_in_loop": float((fm >= 0).mean()) if fm.size else None,
               "return_mean": float(np.mean([f["final_margin"] - f["start_margin"] for f in fin])) if fin else None,
               **{key: v / max(n_mb, 1) for key, v in stats.items()},
               "minibatch_steps": n_mb, "early_stopped": stopped, "lr": lr_k, "ent_coef": ent_k,
               "seconds": {key: round(v, 4) for key, v in tim.items()},
               "timers_synchronised": bool(self.profile or self.device.type != "cuda")}
        if self.ref_policy is not None:                # warm start (round 3): only in runs with an initial policy
            rec.update({"kl_to_init": float(torch.stack(kl_init).mean()), "value_warmup": bool(warm),
                        "ref_kl_coef": kl_k, "explained_variance": ev_before})
        for key in tim:
            self.timing[key] += tim[key]
        return rec

    def train(self, stop_after_iters: Optional[int] = None) -> dict:
        cfg = self.cfg
        if not self.resume():
            self.env.reset_all()
            if 0 in cfg.snapshots:                 # the initial policy, for a learning curve
                self.save_snapshot()
        n_iter = cfg.budget // cfg.months_per_iter
        done_now = 0
        while self.iteration < n_iter:
            if stop_after_iters is not None and done_now >= stop_after_iters:
                return {"stopped": True, "months": self.months, "iteration": self.iteration}
            rec = self.iterate()
            done_now += 1
            snap = self.months in cfg.snapshots
            if snap:
                self.save_snapshot()
                rec["snapshot"] = str(self.snapshot_path(self.months))
            self._log(rec)
            self.log(json.dumps({k: rec[k] for k in ("iteration", "months", "accept_rate_in_loop", "final_margin_mean",
                                                    "entropy", "approx_kl")}))
            if snap or self.iteration % cfg.save_every == 0 or self.iteration == n_iter:
                self.save_latest()
        assert self.months == cfg.budget, (self.months, cfg.budget)
        missing = [s for s in cfg.snapshots if not self.snapshot_path(s).exists()]
        if missing:
            raise RuntimeError(f"snapshots missing: {missing}")
        return {"stopped": False, "months": self.months, "iteration": self.iteration}


def load_snapshot(path, device="cpu") -> Tuple[Policy, dict]:
    ck = torch.load(path, map_location="cpu", weights_only=False)
    cfg = RLConfig.from_dict(ck["cfg"])
    pol = Policy(cfg.policy)
    pol.load_state_dict(ck["policy"])
    return pol.to(device).eval(), ck




# ----------------------------------------------------------------------------------------------
# Evaluation of a snapshot 
# ----------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class EvalConfig:
    episodes: int = 8               # sampled episodes per instance, in the dream and in the closed loop
    audit_k: int = 8                # fresh emulator samples of plan 0 for the audit's verdict (accepted at 4 of 8)
    greedy_final: bool = True       # the greedy plan as a secondary record at the final snapshot
    verify_closed: bool = True      # every closed-loop action log replayed by the engine judge and compared

    def to_dict(self) -> dict:
        return asdict(self)


EVAL_FROZEN = EvalConfig()


class EvalInterrupted(RuntimeError):
    """Raised by ``evaluate_snapshot(stop_after=phase)`` once that phase is saved (tests of resumption)."""


EMULATOR_PHASES = ("dream", "audit", "greedy_emu")    # need the emulator (a card); the others need the engine
ENGINE_PHASES = ("closed", "open", "greedy")


class RecordedEmulator:
    """The emulator's identity on the engine side of a split evaluation (``evaluate_snapshot(side="engine")``):
    ``describe()`` as recorded where the emulator side ran (``emulator.json``), so the phase tags match and the saved
    emulator phases are read; nothing that needs the model can be called."""

    kind = "recorded"

    def __init__(self, describe: dict) -> None:
        self._describe = dict(describe)
        self.month_steps = 0

    def describe(self) -> dict:
        return dict(self._describe)

    def _refuse(self, *a, **k):
        raise RuntimeError("the emulator is not loaded on the engine side of a split evaluation")

    step = start_state = verdict_samples = _refuse

    def judge_counters(self) -> dict:
        return {}


def play_episodes(policy: Policy, env: TaskVecEnv, device, greedy: bool = False,
                  seed: Optional[int] = None, tax_cap: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """One 24-month episode in every slot of ``env`` (no auto-reset): actions drawn from the policy with a
    generator seeded ``seed``, or the arg-max of every head (``greedy``). ``tax_cap``: the learner masks the tax above
    the start rate (``RLConfig.mask_treasury_tax``; effective in ``MASKED_TAX_TASKS``). Returns (effective plans
    (E, H, 25), trajectories (E, H+1, 20))."""
    env.auto_reset = False
    env.reset_all()
    policy.eval()
    gen = None
    if not greedy:
        gen = torch.Generator(device=device)
        gen.manual_seed(int(seed))
    for _ in range(H):
        ob, vec = env.obs()
        with torch.no_grad():
            logits, _ = policy({k: x.to(device) for k, x in ob.items()}, torch.from_numpy(vec).to(device))
            cap = env.tax_cap() if tax_cap else None
            logits = cap_tax(logits, None if cap is None else torch.from_numpy(cap))
            a = sample_actions(logits, gen, greedy=greedy)
        env.step(actions_to_rows(a))
    assert (env.t == H).all()
    return env.plans.copy(), env.traj.copy()


def policy_sha256(policy: nn.Module) -> str:
    h = hashlib.sha256()
    for k, v in policy.state_dict().items():
        h.update(k.encode())
        h.update(v.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def _emu_env(emu, n: int):
    return StubEnv(emu, n) if isinstance(emu, StubEmulator) else EmuEnv(emu, n)


def _emu_identity(emu) -> Optional[dict]:
    if emu is None:
        return None
    d = emu.describe()
    keys = ("judge", "ckpt_sha256", "model_src_commit", "model_py_sha256", "compiled_trunk", "fast", "chunk", "buckets",
            "decoding", "environment_decoding", "device")
    return {k: d[k] for k in keys if k in d}


def eval_tag(policy: nn.Module, instances: Sequence, run_key: str, months: int, device, emu, final: bool,
             cfg: EvalConfig, n_oracle: int, tax_cap: bool = False) -> str:
    """Everything a snapshot's evaluation arrays depend on, hashed: phases saved under another tag are not reused."""
    d = {"eval_version": EVAL_VERSION, "cfg": cfg.to_dict(), "run_key": run_key, "months": int(months),
         "final": bool(final), "policy_sha256": policy_sha256(policy), "policy_device": str(torch.device(device)),
         "instances": [[i.key, float(i.theta), float(i.stat_sd), getattr(i, "extra", "")] for i in instances],
         "tasks_code_sha256": RA.tasks_code_sha256(), "emulator": _emu_identity(emu), "n_oracle": int(n_oracle)}
    if tax_cap:                                  # only when set, so earlier tags are unchanged
        d["tax_cap"] = True
    return hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:24]


class PhaseStore:
    """Finished phases of one snapshot's evaluation: ``<root>/<phase>.npz`` each (``root`` None: memory only),
    valid for one tag; a file under another tag is recomputed and overwritten."""

    def __init__(self, root, tag: str) -> None:
        self.root = Path(root) if root is not None else None
        self.tag = tag
        self.mem: Dict[str, Dict[str, np.ndarray]] = {}
        self.loaded: List[str] = []

    def get(self, name: str) -> Optional[Dict[str, np.ndarray]]:
        if name in self.mem:
            return self.mem[name]
        if self.root is None or not (self.root / f"{name}.npz").exists():
            return None
        with np.load(self.root / f"{name}.npz", allow_pickle=False) as z:
            if str(z["_tag"]) != self.tag:
                return None
            d = {k: z[k] for k in z.files if k != "_tag"}
        self.mem[name] = d
        self.loaded.append(name)
        return d

    def put(self, name: str, arrays: Dict[str, np.ndarray]) -> None:
        arrays = {k: np.asarray(v) for k, v in arrays.items()}
        self.mem[name] = arrays
        if self.root is None:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        tmp = self.root / f"{name}.tmp.npz"
        np.savez(tmp, _tag=np.array(self.tag), **arrays)
        os.replace(tmp, self.root / f"{name}.npz")


def macros_per_plan(plans: np.ndarray) -> np.ndarray:
    """Number of non-NOOP macros in each plan (..., H, 25)."""
    return (np.asarray(plans)[..., 5::5] > 0).sum(axis=(-1, -2))


ORACLE_KEYS = ("margins", "accept_seeds", "share", "accept", "margin")


def _oracle(engine, inst, plans: np.ndarray, n_oracle: int) -> Dict[str, np.ndarray]:
    """The oracle's judgement of plans (m, H, 25): per-seed margins (m, S) and verdicts, pass share, majority
    verdict, majority margin (``dc.audit.oracle_judgement``; verdicts from ``dc.tasks``)."""
    oj = RA.oracle_judgement(inst, RA.oracle_trajectories(engine, inst, plans, n_oracle))
    return {k: np.asarray(oj[k]) for k in ORACLE_KEYS}


def evaluate_snapshot(policy: Policy, instances: Sequence, engine, *, run_key: str, months: int, device,
                      emu=None, final: bool = False, cfg: EvalConfig = EVAL_FROZEN, out_dir=None,
                      closed_workers: int = 0, stop_after: Optional[str] = None,
                      n_oracle: int = T.ORACLE_N, side: str = "both", tax_cap: bool = False) -> Tuple[List[dict], dict]:
    """Records (one per instance) and arrays of one snapshot under the analysis plan and amendment 3.

    ``emu``: the emulator backend (``dc.rl_adaptor.EmulatorBackend`` or ``StubEmulator``), or None for a policy
    trained on the engine (then only the engine phases run, and the open-loop plans are the closed-loop ones).
    ``engine``: ``dc.rl_adaptor.engine_judge``. ``final``: the run's last snapshot (the greedy record is added
    there). ``out_dir``: where finished phases are saved (resumption). ``n_oracle``: the oracle's seeds.

    ``side`` splits the evaluation between two machines (round 3): "emulator" runs only the phases that need the
    emulator (``EMULATOR_PHASES``: the dream episodes and their plans, the audit's verdict of plan 0, the greedy plan
    in the emulator), saves them in ``out_dir`` and returns no records (``engine`` may be None); "engine" reads those
    saved phases (``emu`` may be a ``RecordedEmulator``: the phases' tag holds the emulator's identity), runs the
    engine phases and returns the records; "both" runs everything. The records do not depend on the split.

    The engine's verdict on a plan is the oracle's: the predicate's majority over the instance's ``n_oracle``
    dedicated seeds (``dc.tasks.oracle_seeds``); its engine margin is the mean margin over those seeds (beside it
    the pass share, the majority margin and oracle seed 0's margin and verdict). No phase uses an oracle seed or
    one of the nine residual seeds for anything but the oracle's replays.

    Phases, slot e of a batch being episode e // n of instance e mod n (n instances, E episodes each):
    * dream (emulator): N = n E slots, 24 months; emulator noise ``torch.manual_seed(seed_for("rl-eval-sample",
      run, months, "emulator"))``, actions from a generator seeded ``seed_for("rl-eval-sample", run, months,
      "policy")``; each episode's effective action log is a plan, its own trajectory gives the imagined margin
      and the dream verdict (margin >= 0);
    * audit (emulator): plan 0 of each instance through ``EmulatorJudge.samples`` (K = 8, stream
      ("rl-audit-plan0", run, months)), accepted when the 4th-largest of the 8 margins is >= 0;
    * closed (engine): N slots, actions from a generator seeded ``seed_for("rl-eval-closed", run, months,
      "policy")``; episode j of an instance on the engine seed ``seed_for("rl-eval-closed-seed", run, months,
      instance, j)`` redrawn past the start's reserved seeds; every closed-loop action log replayed by the engine
      judge on its seed and compared;
    * open (engine judge): the E plans of each instance on the oracle's seeds;
    * greedy (final snapshot only): the arg-max plan in the emulator (the seeds: torch ``seed_for("rl-eval-greedy",
      run, months)``, verdict stream ("rl-verdict", run, months)) judged by the oracle, and the greedy policy closed
      loop on the seed ``seed_for("rl-eval-greedy-seed", run, months, instance)`` (redrawn past reserved seeds).
    """
    inst = list(instances)
    n, E = len(inst), int(cfg.episodes)
    N = n * E
    if emu is not None and cfg.audit_k != RA.K_VERDICT:
        raise ValueError(f"audit_k {cfg.audit_k} is not the audit's K = {RA.K_VERDICT}")
    if side not in ("both", "emulator", "engine"):
        raise ValueError(f"side {side!r}")
    if side != "both" and emu is None:
        raise ValueError("a split evaluation is for policies trained in the emulator")
    if side == "emulator" and isinstance(emu, RecordedEmulator):
        raise ValueError("the emulator side needs the emulator")
    store = PhaseStore(out_dir, eval_tag(policy, inst, run_key, months, device, emu, final, cfg, n_oracle, tax_cap))
    seconds: Dict[str, float] = {}
    reserved = {i.start_id: RA.reserved_seeds(i.start_id) for i in inst}

    def by_instance(a: np.ndarray) -> np.ndarray:            # slot e = j * n + i  ->  [i, j]
        return np.ascontiguousarray(np.asarray(a).reshape(E, n, *a.shape[1:]).swapaxes(0, 1))

    def fresh(keys, sid) -> int:
        s, _ = RA.fresh_seed(keys, reserved[sid])
        if s in reserved[sid]:
            raise RuntimeError(f"seed {s} is reserved on {sid}")
        return int(s)

    def phase(name, fn):
        d = store.get(name)
        if d is None and side == "engine" and name in EMULATOR_PHASES:
            raise RuntimeError(f"emulator phase {name!r} of snapshot {months} is not in {out_dir} under this tag: run "
                               "the emulator side first (same policy device, emulator identity and instances)")
        if d is None:
            t0 = time.perf_counter()
            d = fn()
            store.put(name, d)
            d = store.mem[name]
            seconds[name] = time.perf_counter() - t0
            if stop_after == name:
                raise EvalInterrupted(name)
        return d

    def closed_loop(n_slots, seeds, greedy, gseed):
        eenv = EngineEnv(n_slots, workers=closed_workers, device="cpu")
        try:
            env = TaskVecEnv(eenv, inst, n_slots, run_key, auto_reset=False, slot_seeds=seeds)
            plans, traj = play_episodes(policy, env, device, greedy=greedy, seed=gseed, tax_cap=tax_cap)
            cm = eenv.city_months
        finally:
            eenv.close()
        if cm != n_slots * H:
            raise RuntimeError(f"closed loop: {cm} engine city-months, {n_slots * H} expected")
        eq = np.zeros(n_slots, dtype=bool)
        if cfg.verify_closed:
            for k, i in enumerate(inst):                         # slots k, k + n, k + 2n, ... play instance k
                sl = np.arange(k, n_slots, n)
                rep = engine.scalars(i, plans[sl], np.asarray(seeds)[sl]).astype(np.float64)
                eq[sl] = [np.array_equal(rep[j], traj[e]) for j, e in enumerate(sl)]
        return plans, traj, eq, cm

    def dream():
        torch.manual_seed(seed_for("rl-eval-sample", run_key, months, "emulator"))
        env = TaskVecEnv(_emu_env(emu, N), inst, N, run_key, auto_reset=False)
        s0 = emu.month_steps
        plans, traj = play_episodes(policy, env, device, seed=seed_for("rl-eval-sample", run_key, months, "policy"),
                                    tax_cap=tax_cap)
        steps = emu.month_steps - s0
        if steps != N * H:
            raise RuntimeError(f"dream: {steps} emulator month-steps taken, {N * H} expected")
        return {"plans": by_instance(plans), "traj": by_instance(traj), "month_steps": steps}

    def audit():
        p = D["plans"]
        ver = np.stack([emu.verdict_samples(i, p[k, :1], cfg.audit_k, ("rl-audit-plan0", run_key, months))[0]
                        for k, i in enumerate(inst)])                              # (n, 8, H+1, 20)
        return {"traj": ver}

    def closed():
        seeds = [fresh(("rl-eval-closed-seed", run_key, months, inst[e % n].key, e // n), inst[e % n].start_id)
                 for e in range(N)]
        plans, traj, eq, cm = closed_loop(N, seeds, False, seed_for("rl-eval-closed", run_key, months, "policy"))
        out = {"plans": by_instance(plans), "traj": by_instance(traj), "seeds": by_instance(np.asarray(seeds)),
               "city_months": cm}
        if cfg.verify_closed:
            out["replay_equal"] = by_instance(eq)
        return out

    def open_loop():
        P = D["plans"] if emu is not None else C["plans"]
        res = [_oracle(engine, i, P[k], n_oracle) for k, i in enumerate(inst)]
        return {k: np.stack([r[k] for r in res]) for k in ORACLE_KEYS}                # (n, E, ...)

    def greedy_emu():                                        # the greedy plan in the emulator and its verdict samples
        torch.manual_seed(seed_for("rl-eval-greedy", run_key, months))
        env = TaskVecEnv(_emu_env(emu, n), inst, n, run_key, auto_reset=False)
        gp, gt = play_episodes(policy, env, device, greedy=True, tax_cap=tax_cap)
        vt = np.stack([emu.verdict_samples(i, gp[k:k + 1], RA.K_VERDICT, ("rl-verdict", run_key, months))[0]
                       for k, i in enumerate(inst)])
        return {"emu_plans": gp, "emu_traj": gt, "verdict_traj": vt}

    def greedy():                                            # the greedy policy closed loop; the oracle's judgement
        out = {}
        seeds = [fresh(("rl-eval-greedy-seed", run_key, months, i.key), i.start_id) for i in inst]
        cp, ct, eq, _ = closed_loop(n, seeds, True, None)
        op = GE["emu_plans"] if emu is not None else cp
        res = [_oracle(engine, i, op[k:k + 1], n_oracle) for k, i in enumerate(inst)]
        out.update({f"oracle_{k}": np.stack([r[k][0] for r in res]) for k in ORACLE_KEYS})
        out.update({"closed_plans": cp, "closed_traj": ct, "closed_seeds": np.asarray(seeds), "closed_replay_equal": eq})
        return out

    D = A8 = Gd = GE = None
    want_greedy = final and cfg.greedy_final
    if emu is not None:
        D = phase("dream", dream)
        A8 = phase("audit", audit)
        if want_greedy:
            GE = phase("greedy_emu", greedy_emu)
    if side == "emulator":
        arrays = {f"{name}_{k}": v for name, d in (("dream", D), ("audit", A8), ("greedy", GE)) if d is not None
                  for k, v in d.items()}
        return [], {"arrays": arrays, "seconds": seconds, "counts": {"emulator_env_month_steps_dream": int(D["month_steps"])},
                    "phases_resumed": list(store.loaded), "tag": store.tag, "side": side}
    C = phase("closed", closed)
    O = phase("open", open_loop)
    if want_greedy:
        Gd = {**(GE or {}), **phase("greedy", greedy)}

    recs = []
    K = RA.K_VERDICT
    for k, i in enumerate(inst):
        r = {"run_key": run_key, "snapshot_months": int(months), "eval_version": EVAL_VERSION,
             "plan_rule": "sampled episodes ", "oracle": f"majority of {n_oracle} seeds (amendment 3)",
             "environment": "emulator" if emu is not None else "engine",
             "instance": i.key, "start_id": i.start_id, "cluster": i.family_id, "task": i.task,
             "in_band": bool(i.in_band), "theta": float(i.theta), "stat_sd": float(i.stat_sd), "n_episodes": E,
             "n_oracle_seeds": int(n_oracle)}
        if tax_cap and i.task in MASKED_TAX_TASKS:
            r["tax_cap"] = "the tax head masked above the start rate "
        ct = C["traj"][k]
        cm = RA.task_margin(i, ct)
        r["start_margin"] = start_margin(i, ct[0, 0])
        r.update({"engine_closed_margins": [float(x) for x in cm], "engine_closed_accepts": [bool(x >= 0) for x in cm],
                  "closed_seeds": [int(x) for x in C["seeds"][k]],
                  "closed_plan_hashes": [RA.plan_hash(C["plans"][k, j]) for j in range(E)],
                  "closed_macros": [int(x) for x in macros_per_plan(C["plans"][k])],
                  "engine_city_months_closed": E * H})
        if "replay_equal" in C:
            r["closed_loop_replay_equal"] = [bool(x) for x in C["replay_equal"][k]]
            r["engine_city_months_closed_check"] = E * H
        om = O["margins"][k]                                                        # (E, S) per-seed margins
        r.update({"engine_open_margins": [float(x) for x in om.mean(axis=1)],
                  "engine_open_accepts": [bool(x) for x in O["accept"][k]],
                  "engine_open_shares": [float(x) for x in O["share"][k]],
                  "engine_open_majority_margins": [float(x) for x in O["margin"][k]],
                  "engine_open_seed0_margins": [float(x) for x in om[:, 0]],
                  "engine_open_seed0_accepts": [bool(x) for x in O["accept_seeds"][k][:, 0]],
                  "engine_city_months_open": E * n_oracle * H})
        r.update({"plan0_engine_open_margin": r["engine_open_margins"][0],
                  "plan0_engine_open_accept": r["engine_open_accepts"][0],
                  "plan0_engine_open_share": r["engine_open_shares"][0]})
        if emu is not None:
            dt = D["traj"][k]
            dm = RA.task_margin(i, dt)
            am = RA.task_margin(i, A8["traj"][k])
            a4 = float(RA.fourth_largest(am))
            r.update({"dream_start_margin": start_margin(i, dt[0, 0]),
                      "dream_margins": [float(x) for x in dm], "dream_accepts": [bool(x >= 0) for x in dm],
                      "plan_hashes": [RA.plan_hash(D["plans"][k, j]) for j in range(E)],
                      "dream_macros": [int(x) for x in macros_per_plan(D["plans"][k])],
                      "plan0_audit_margins8": [float(x) for x in am], "plan0_audit_margin_mean": float(am.mean()),
                      "plan0_audit_margin_4th": a4, "plan0_audit_p": float((am >= 0).mean()),
                      "plan0_audit_accept": bool(a4 >= 0),
                      "plan0_hacked": bool(a4 >= 0 and not r["plan0_engine_open_accept"]),
                      "emu_month_steps_dream": E * H, "emu_month_steps_audit": K * H})
        else:
            r["open_plans_are_closed_plans"] = True
            r["plan_hashes"] = list(r["closed_plan_hashes"])
        if Gd is not None:
            gmc = float(RA.task_margin(i, Gd["closed_traj"][k]))
            gplan = Gd["emu_plans"][k] if emu is not None else Gd["closed_plans"][k]
            r.update({"greedy_plan_hash": RA.plan_hash(gplan), "greedy_macros": int(macros_per_plan(gplan)),
                      "greedy_engine_open_margin": float(Gd["oracle_margins"][k].mean()),
                      "greedy_engine_open_accept": bool(Gd["oracle_accept"][k]),
                      "greedy_engine_open_share": float(Gd["oracle_share"][k]),
                      "greedy_engine_open_seed0_accept": bool(Gd["oracle_accept_seeds"][k][0]),
                      "greedy_engine_closed_margin": gmc, "greedy_engine_closed_accept": bool(gmc >= 0),
                      "greedy_closed_seed": int(Gd["closed_seeds"][k]),
                      "greedy_closed_plan_hash": RA.plan_hash(Gd["closed_plans"][k]),
                      "greedy_closed_loop_replay_equal": bool(Gd["closed_replay_equal"][k]),
                      "greedy_engine_city_months": n_oracle * H + 2 * H})
            if emu is not None:
                gml = float(RA.task_margin(i, Gd["emu_traj"][k]))
                g8 = RA.task_margin(i, Gd["verdict_traj"][k])
                r.update({"greedy_emulator_margin": gml, "greedy_emulator_accept": bool(gml >= 0),
                          "greedy_imagined_margins8": [float(x) for x in g8], "greedy_imagined_margin": float(g8.mean()),
                          "greedy_imagined_p": float((g8 >= 0).mean()),
                          "greedy_imagined_accept": bool(RA.fourth_largest(g8) >= 0),
                          "greedy_emu_month_steps": H + K * H})
        recs.append(r)
    arrays = {f"{name}_{k}": v for name, d in (("dream", D), ("audit", A8), ("closed", C), ("open", O), ("greedy", Gd))
              if d is not None for k, v in d.items()}
    counts = {"emulator_env_month_steps_dream": int(D["month_steps"]) if D is not None else 0,
              "engine_env_city_months_closed": int(C["city_months"])}
    return recs, {"arrays": arrays, "seconds": seconds, "counts": counts, "phases_resumed": list(store.loaded),
                  "tag": store.tag, "side": side}


def _flat(recs: Sequence[dict], key: str) -> np.ndarray:
    v = []
    for r in recs:
        if key in r:
            v += list(r[key]) if isinstance(r[key], list) else [r[key]]
    return np.asarray(v, dtype=np.float64)


def summarise(recs: Sequence[dict]) -> dict:
    """Pair-level numbers of one snapshot : inflation = mean over instances and episodes
    of the dream margin minus the oracle's mean margin of the same plan; verdict gap = dream acceptance rate minus
    the oracle's acceptance rate of the same plans; the closed-loop versions; plan 0 under the audit's rule; the
    greedy record. ``*_in_band`` repeats the main rates on the instances whose tasks-file flag ``in_band`` is set
    (in the v2 tasks files: well posed, amendment 3)."""
    def mean(key, rs=recs):
        v = _flat(rs, key)
        return float(v.mean()) if v.size else None

    out = {"eval_version": EVAL_VERSION, "n_instances": len(recs), "n_episodes_per_instance": recs[0]["n_episodes"],
           "n_oracle_seeds": recs[0].get("n_oracle_seeds"), "n_in_band": int(sum(r.get("in_band", True) for r in recs))}
    names = {"start_margin": "mean_start_margin",
             "dream_margins": "mean_dream_margin", "dream_accepts": "rate_dream_accept",
             "engine_open_margins": "mean_engine_open_margin", "engine_open_accepts": "rate_engine_open_accept",
             "engine_open_shares": "mean_engine_open_share",
             "engine_open_majority_margins": "mean_engine_open_majority_margin",
             "engine_open_seed0_accepts": "rate_engine_open_seed0_accept",
             "engine_open_seed0_margins": "mean_engine_open_seed0_margin",
             "plan0_engine_open_margin": "mean_plan0_engine_open_margin",
             "plan0_engine_open_accept": "rate_plan0_engine_open_accept",
             "plan0_audit_margin_mean": "mean_plan0_audit_margin", "plan0_audit_margin_4th": "mean_plan0_audit_margin_4th",
             "plan0_audit_accept": "rate_plan0_audit_accept", "plan0_hacked": "plan0_hackability",
             "engine_closed_margins": "mean_engine_closed_margin", "engine_closed_accepts": "rate_engine_closed_accept",
             "greedy_emulator_margin": "mean_greedy_emulator_margin", "greedy_imagined_margin": "mean_greedy_imagined_margin",
             "greedy_imagined_accept": "rate_greedy_imagined_accept",
             "greedy_engine_open_margin": "mean_greedy_engine_open_margin",
             "greedy_engine_open_accept": "rate_greedy_engine_open_accept",
             "greedy_engine_open_seed0_accept": "rate_greedy_engine_open_seed0_accept",
             "greedy_engine_closed_margin": "mean_greedy_engine_closed_margin",
             "greedy_engine_closed_accept": "rate_greedy_engine_closed_accept"}
    for key, name in names.items():
        out[name] = mean(key)
    wp = [r for r in recs if r.get("in_band", True)]
    for key in ("engine_open_accepts", "engine_open_margins", "engine_closed_accepts", "dream_accepts"):
        out[names[key] + "_in_band"] = mean(key, wp) if wp else None
    for key in ("dream_macros", "closed_macros", "greedy_macros"):
        v = mean(key)
        out[f"{key}_per_month"] = None if v is None else v / H
    dm, om = _flat(recs, "dream_margins"), _flat(recs, "engine_open_margins")
    if dm.size:
        out["inflation_open"] = float((dm - om).mean())
        out["verdict_gap_open"] = out["rate_dream_accept"] - out["rate_engine_open_accept"]
        out["inflation_closed"] = out["mean_dream_margin"] - out["mean_engine_closed_margin"]
        out["verdict_gap_closed"] = out["rate_dream_accept"] - out["rate_engine_closed_accept"]
        out["plan0_inflation_audit"] = float((_flat(recs, "plan0_audit_margin_mean")
                                              - _flat(recs, "plan0_engine_open_margin")).mean())
        out["plan0_verdict_gap_audit"] = out["rate_plan0_audit_accept"] - out["rate_plan0_engine_open_accept"]
    if out["mean_greedy_imagined_margin"] is not None:
        out["greedy_inflation_open"] = out["mean_greedy_imagined_margin"] - out["mean_greedy_engine_open_margin"]
        out["greedy_verdict_gap_open"] = out["rate_greedy_imagined_accept"] - out["rate_greedy_engine_open_accept"]
    for key in ("closed_loop_replay_equal", "greedy_closed_loop_replay_equal"):
        v = _flat(recs, key)
        if v.size:
            out[key] = f"{int(v.sum())}/{v.size}"
    out["design_emulator_month_steps"] = int(sum(r.get("emu_month_steps_dream", 0) + r.get("emu_month_steps_audit", 0)
                                                 + r.get("greedy_emu_month_steps", 0) for r in recs))
    out["design_engine_city_months"] = int(sum(r.get("engine_city_months_open", 0) + r.get("engine_city_months_closed", 0)
                                               + r.get("engine_city_months_closed_check", 0)
                                               + r.get("greedy_engine_city_months", 0) for r in recs))
    return out
