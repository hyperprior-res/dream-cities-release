"""Training: one-step likelihood and self-forcing fine-tune, budgets in samples, resumable.

A *sample* is one transition (one-step) or one starting transition of a short rollout on the
model's own predictions (self-forcing). Every count written anywhere is the count that ran: the
trainer adds the batch size of each optimiser step it actually took.

Objective (one-step): the negative evidence lower bound per transition,
    sum_term w_term * (-log p_term(s_t+1 | s_t, a_t, z)) + beta * KL(q(z | s_t, a_t, s_t+1) || N(0, I)),
z drawn from the posterior, divided by the number of tiles (12,000) so the loss is in nats per tile.
The weights only shift trunk capacity between heads; every head stays a proper distribution, and
evaluation reports the unweighted terms. beta ramps linearly from 0 to 1 over ``kl_warmup`` of the
budget.

Self-forcing (pushforward): for each optimiser step draw j = 0 with probability ``sf_tf_ratio``
(teacher forcing), else j uniform in 1..k-1. The model rolls j months forward from the engine's
state with no gradient, decoding each month at the posterior z given the engine's next state and
taking the mode (temperature 0), so the drift it accumulates is model error rather than a different
random realisation; the loss is then the one-step objective of the engine's s_t+j+1 given the
model's own state.

Also here: a development stand-in for the trajectory store (``EnginePool``): real engine
observations from bundled cities under random tool calls, in exactly the loader's batch format.
It exists for tests and throughput measurement before the store lands; it is not training data.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

import numpy as np
import torch

from .engine import (
    ANIMBIT, BULLBIT, BURNBIT, CONDBIT, LOMASK, PWRBIT, TOOL_SIZES, WORLD_H, WORLD_W, ZONEBIT,
    Engine, MonthAction, Obs,
)
from .engine import SC_TIME
from .model import Emulator, ModelConfig, SIZES, State, build, compute_norm_stats, set_numerics

REPO = Path(__file__).resolve().parents[2]
N_TILES = WORLD_W * WORLD_H
FLAG_BITS = (ZONEBIT, BULLBIT, BURNBIT, CONDBIT, PWRBIT)
# raster channel order : res, com, ind, fire, police, wire, bulldoze, rail, road,
# stadium, park, seaport, coal, nuclear, airport = engine tool ids 0..15 without 5 (query)
TOOL_TO_CHANNEL = {t: c for c, t in enumerate([0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])}


# ----------------------------------------------------------------------------------------------
# Loader-format conversion and the development stand-in
# ----------------------------------------------------------------------------------------------
def obs_to_numpy(obs: Sequence[Obs], ledger: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
    """Compact numpy rows. ``ledger``: the oracle's ``Replay.ledger`` (H+1, 27), whose row 0 carries the
    trajectory's disaster switch (``obs0`` is read before the switch is set)."""
    tiles = np.stack([o.tiles for o in obs])
    out = {
        "tile_index": (tiles & LOMASK).astype(np.int16),
        "flags": np.stack([(tiles & b) > 0 for b in FLAG_BITS], axis=1),
        "power": np.stack([o.power for o in obs]).astype(np.uint8),
        "half": np.stack([o.half for o in obs]),
        "eighth": np.stack([o.eighth for o in obs]),
        "scalars": np.stack([o.scalars for o in obs]),
    }
    if obs[0].ledger is not None:
        out["ledger"] = np.asarray(ledger) if ledger is not None else np.stack([o.ledger for o in obs])
        out["terrain"] = np.stack([o.terrain for o in obs])
        out["com_rate"] = np.stack([o.com_rate for o in obs])
    return out


def numpy_to_state(d: Dict[str, np.ndarray], device) -> State:
    """Compact numpy rows -> the loader's state format (dtypes of section 4.3)."""
    t = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(device)
    out = {
        "tile_index": t(d["tile_index"]).long(),
        "flags": t(d["flags"]).float(),
        "power": t(d["power"]).float(),
        "half": t(d["half"]).float(),
        "eighth": t(d["eighth"]).float(),
        "scalars": t(d["scalars"]).double().float(),
    }
    if "ledger" in d:
        out["ledger"] = t(d["ledger"]).double().float()
        out["terrain"] = t(d["terrain"]).float()
        out["com_rate"] = t(d["com_rate"]).float()
    return out


def obs_to_state(obs: Sequence[Obs], device="cpu") -> State:
    return numpy_to_state(obs_to_numpy(obs), device)


def stand_in_raster(act: MonthAction) -> np.ndarray:
    """Development stand-in for the ``raster``: footprint of every attempted call set to 1.

    Footprints from ``dc.engine.TOOL_SIZES`` and its anchor note (3x3 centred; 4x4 and 6x6 anchored
    one tile up-left of the centre). the measured footprints replace this when ``dc.grammar`` lands.
    """
    r = np.zeros((15, WORLD_W, WORLD_H), dtype=np.float32)
    for tool, x, y in act.tools.tolist():
        if tool not in TOOL_TO_CHANNEL:
            continue
        n = TOOL_SIZES.get(tool, 1)
        x0 = x - 1 if n >= 3 else x
        y0 = y - 1 if n >= 3 else y
        r[TOOL_TO_CHANNEL[tool], max(0, x0):max(0, x0 + n), max(0, y0):max(0, y0 + n)] = 1.0
    return r


def stand_in_action_scalars(act: MonthAction, forced_kind: int = 0) -> np.ndarray:
    v = np.zeros(11, dtype=np.float32)
    v[:4] = [act.tax / 20.0, act.road / 100.0, act.fire / 100.0, act.police / 100.0]
    v[4 + int(forced_kind)] = 1.0
    return v


def random_month(rng: np.random.Generator, n_max: int = 12) -> Tuple[MonthAction, int]:
    """Random budget settings and tool calls (roads and zones most often), rare forced disaster."""
    n = int(rng.integers(0, n_max + 1))
    tools = rng.choice([0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], size=n,
                       p=np.array([12, 10, 8, 1, 1, 8, 6, 3, 20, .5, 4, .5, 1, .5, .5]) / 76.0)
    xs, ys = rng.integers(0, WORLD_W, n), rng.integers(0, WORLD_H, n)
    act = MonthAction(int(rng.integers(0, 21)), *(int(v) for v in rng.choice([0, 25, 50, 75, 100], 3)),
                      tools=np.stack([tools, xs, ys], 1).astype(np.int16))
    forced = int(rng.integers(1, 7)) if rng.random() < 0.01 else 0
    return act, forced


class EnginePool:
    """Real engine transitions held on one device, served as loader-format batches.

    ``EnginePool.generate(cities, trajs_per_city, months, seed)`` replays each bundled city with
    random months through ``dc.oracle.replay`` (record="full"). Development stand-in only.
    """

    def __init__(self, obs: Dict[str, np.ndarray], raster: np.ndarray, act: np.ndarray, src: np.ndarray,
                 traj_start: np.ndarray, months: int, device) -> None:
        self.device = torch.device(device)
        self.obs = numpy_to_state(obs, device)
        self.raster = torch.from_numpy(raster).to(device)          # (T,15,X,Y) uint8
        self.act = torch.from_numpy(act).to(device)                # (T,11)
        self.src = torch.from_numpy(src).to(device)                # (T,) observation row of s_t
        self.traj_start = traj_start                               # first transition id per trajectory
        self.months = months
        self.n = int(self.src.shape[0])

    @staticmethod
    def generate(cities: Sequence[Path], trajs_per_city: int = 2, months: int = 48, seed: int = 0,
                 device="cpu") -> "EnginePool":
        from .oracle import replay
        rng = np.random.default_rng(seed)
        eng = Engine()
        obs_rows, rasters, acts, src, starts, costs = [], [], [], [], [], []
        n_obs = 0
        for c in cities:
            for _ in range(trajs_per_city):
                months_l = [random_month(rng) for _ in range(months)]
                actions = [m[0] for m in months_l]
                forced = {i: k for i, (_, k) in enumerate(months_l) if k}
                rp = replay(eng, c, actions, seed=int(rng.integers(1, 2**31 - 1)),
                            disasters=bool(rng.random() < 0.15), forced=forced, record="full")
                starts.append(len(src))
                obs_rows.append(obs_to_numpy(rp.states, rp.ledger))
                costs.extend(rp.build_cost.tolist())
                for i, (a, k) in enumerate(months_l):
                    rasters.append(stand_in_raster(a).astype(np.uint8))
                    acts.append(stand_in_action_scalars(a, k))
                    src.append(n_obs + i)
                n_obs += months + 1
        eng.close()
        obs = {k: np.concatenate([o[k] for o in obs_rows]) for k in obs_rows[0]}
        pool = EnginePool(obs, np.stack(rasters), np.stack(acts), np.asarray(src, dtype=np.int64),
                          np.asarray(starts, dtype=np.int64), months, device)
        pool.cost = torch.tensor(costs, dtype=torch.float32, device=pool.device)
        return pool

    def _state(self, rows: torch.Tensor) -> State:
        return {k: v.index_select(0, rows) for k, v in self.obs.items()}

    def transition(self, ids: torch.Tensor):
        rows = self.src.index_select(0, ids)
        s1 = self._state(rows + 1)
        if getattr(self, "cost", None) is not None:
            s1["build_cost"] = self.cost.index_select(0, ids)
        return (self._state(rows), self.raster.index_select(0, ids).float(), self.act.index_select(0, ids), s1)

    def batches(self, batch_size: int, seed: int, ids: Optional[torch.Tensor] = None) -> Iterator:
        """Uniform with replacement over ``ids`` (default all transitions), forever."""
        g = torch.Generator(device="cpu").manual_seed(seed)
        pool = torch.arange(self.n) if ids is None else ids.cpu()
        while True:
            pick = pool[torch.randint(len(pool), (batch_size,), generator=g)].to(self.device)
            yield self.transition(pick)

    def multistep_batches(self, batch_size: int, k: int, seed: int) -> Iterator:
        """Lists of k consecutive transitions of one trajectory per batch element."""
        g = torch.Generator(device="cpu").manual_seed(seed)
        n_traj = len(self.traj_start)
        while True:
            tj = torch.randint(n_traj, (batch_size,), generator=g)
            off = torch.randint(self.months - k + 1, (batch_size,), generator=g)
            first = torch.from_numpy(self.traj_start)[tj] + off
            yield [self.transition((first + i).to(self.device)) for i in range(k)]

    def all_batches(self, batch_size: int) -> Iterator:
        for a in range(0, self.n, batch_size):
            yield self.transition(torch.arange(a, min(self.n, a + batch_size), device=self.device))


# ----------------------------------------------------------------------------------------------
# Configuration and schedule
# ----------------------------------------------------------------------------------------------
DEFAULT_WEIGHTS = {"tile_gate": 1.0, "tile_cat": 1.0, "flags": 1.0, "power": 1.0, "half": 0.25,
                   "eighth": 1.0, "scalars": 4.0, "ledger": 4.0, "terrain": 0.25, "com_rate": 1.0,
                   "scalars_s2": 4.0, "build_cost": 4.0}


@dataclass
class TrainConfig:
    size: str = "50m"
    mode: str = "onestep"                # "onestep" | "selfforce"
    samples: int = 6_000_000             # budget in samples
    batch_size: int = 256
    lr: float = 8e-4
    min_lr_frac: float = 0.05
    warmup_frac: float = 0.03
    weight_decay: float = 0.05
    betas: Tuple[float, float] = (0.9, 0.98)
    grad_clip: float = 1.0
    ema_decay: float = 0.999
    kl_warmup: float = 0.05              # fraction of the budget over which beta goes 0 -> 1
    weights: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    save_fracs: Tuple[float, ...] = (0.5, 1.0)
    save_samples: Tuple[int, ...] = ()   # extra milestones in samples (e.g. pilot evaluations)
    sf_k: int = 4                        # self-forcing: rollout length (transitions per window)
    sf_tf_ratio: float = 0.5             # self-forcing: share of steps that are teacher-forced
    compile: bool = True
    seed: int = 0
    log_every: int = 20
    resume_every_s: float = 600.0        # wall-clock interval of the resumable checkpoint
    init_from: str = ""                  # self-forcing: path of the one-step checkpoint
    budget_weight: float = 1.0           # weight of the scalar terms on transitions whose month contains the
                                         # yearly budget (city_time mod 48 >= 44; 1 transition in 12)
    table_lr_mult: float = 1.0           # learning-rate multiplier of the second stage's changed-tile tables
    model_overrides: Dict[str, object] = field(default_factory=dict)   # ModelConfig fields to change
    micro_batch: int = 0                 # >0: each optimiser step accumulates batch_size / micro_batch micro-batches
    bk_updates: int = 10                 # third stage: scalar-only updates per trunk step (its own schedule)
    bk_batch: int = 4096
    bk_lr: float = 1e-3

    def to_dict(self) -> dict:
        d = asdict(self)
        d["betas"] = list(self.betas)
        d["save_fracs"], d["save_samples"] = list(self.save_fracs), list(self.save_samples)
        d["model_overrides"] = dict(self.model_overrides)
        return d


def budget_window(city_time: torch.Tensor) -> torch.Tensor:
    """True where the coming month contains the yearly budget: the engine collects tax when city_time is a
    multiple of 48 and a month advances city_time by 4, so the month starting at c contains it iff
    c mod 48 >= 44 (measured: every budget landing in heldout_eval follows c mod 48 = 44)."""
    return torch.remainder(city_time.round().long(), 48) >= 44


def lr_at(cfg: TrainConfig, samples: int) -> float:
    """Linear warm-up over warmup_frac of the budget, then cosine to min_lr_frac at the budget."""
    w = max(1, int(cfg.warmup_frac * cfg.samples))
    if samples < w:
        return cfg.lr * (samples + cfg.batch_size) / w
    p = min(1.0, (samples - w) / max(1, cfg.samples - w))
    return cfg.lr * (cfg.min_lr_frac + (1 - cfg.min_lr_frac) * 0.5 * (1 + math.cos(math.pi * p)))


def beta_at(cfg: TrainConfig, samples: int) -> float:
    if cfg.mode != "onestep":
        return 1.0
    w = cfg.kl_warmup * cfg.samples
    return 1.0 if w <= 0 else min(1.0, samples / w)


def milestones(cfg: TrainConfig) -> List[int]:
    m = {int(round(f * cfg.samples)) for f in cfg.save_fracs} | {int(s) for s in cfg.save_samples}
    return sorted(x for x in m if 0 < x <= cfg.samples)


# ----------------------------------------------------------------------------------------------
# Provenance helpers
# ----------------------------------------------------------------------------------------------
def git_state() -> Dict[str, object]:
    """Commit and uncommitted code files of the checkout (a failing git stops the run: provenance is required)."""
    if not (REPO / ".git").exists():
        return {"commit": "release-tree", "dirty_code_files": []}
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10,
                          check=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--", "code"], capture_output=True,
                           text=True, timeout=10, check=True).stdout.strip().splitlines()
    return {"commit": head, "dirty_code_files": dirty}


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def state_dict_sha256(sd: Dict[str, torch.Tensor]) -> str:
    h = hashlib.sha256()
    for k in sorted(sd):
        h.update(k.encode())
        h.update(sd[k].detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()
                 if sd[k].dim() > 0 else sd[k].detach().cpu().reshape(1).view(torch.uint8).numpy().tobytes())
    return h.hexdigest()


def atomic_torch_save(obj, path: Path) -> str:
    """Save atomically, write ``<path>.sha256``, return the file's sha256."""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    torch.save(obj, tmp)
    os.replace(tmp, path)
    digest = sha256_file(path)
    (path.parent / (path.name + ".sha256")).write_text(f"{digest}  {path.name}\n")
    return digest


def load_checkpoint(path, device="cpu", use_ema: bool = True) -> Tuple[Emulator, dict]:
    """Load a checkpoint for evaluation, with the numerics training used (``dc.model.set_numerics``)."""
    if torch.device(device).type == "cuda":
        set_numerics()
    ck = torch.load(path, map_location="cpu", weights_only=False)
    m = Emulator(ModelConfig.from_dict(ck["model_config"]))
    # which weights were actually loaded (a checkpoint without an EMA falls back to the raw weights)
    ck["loaded_weights"] = "ema" if (use_ema and ck.get("ema") is not None) else "model"
    m.load_state_dict(ck["ema"] if ck["loaded_weights"] == "ema" else ck["model"])
    m = m.to(device)
    if torch.device(device).type == "cuda":
        m = m.to(memory_format=torch.channels_last)
    return m.eval(), ck


# ----------------------------------------------------------------------------------------------
# Trainer
# ----------------------------------------------------------------------------------------------
class Trainer:
    def __init__(self, cfg: TrainConfig, run_dir: Path, device="cuda", data_info: Optional[dict] = None,
                 norm_stats: Optional[Dict[str, torch.Tensor]] = None, book_data: Optional["BookData"] = None) -> None:
        self.cfg = cfg
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.device = torch.device(device)
        self.data_info = data_info or {}
        torch.manual_seed(cfg.seed)
        if self.device.type == "cuda":
            set_numerics()
        init_ck = None
        if cfg.init_from:
            self.model, init_ck = load_checkpoint(cfg.init_from, self.device, use_ema=True)
            self.model.train()
        else:
            import dataclasses
            mcfg = dataclasses.replace(SIZES[cfg.size], **{k: (tuple(v) if isinstance(v, list) else v)
                                                           for k, v in cfg.model_overrides.items()})
            self.model = Emulator(mcfg).to(self.device)
            if self.device.type == "cuda":
                self.model = self.model.to(memory_format=torch.channels_last)
        if norm_stats is not None and not cfg.init_from:
            self.model.set_norm_stats(norm_stats)
        assert self.model.norm_ready, "normalisation statistics must be set (compute_norm_stats)"
        self.ema = [p.detach().clone() for p in self.model.parameters()]
        self.book = book_data
        self.bk_samples = 0
        self.bk_opt = None
        if self.model.cfg.bookkeeping:
            if book_data is None:
                raise ValueError("a third-stage model needs its scalar-only data (BookData)")
            if not cfg.init_from:
                self.model.set_bk_stats(book_data.stats)
            self.bk_opt = torch.optim.AdamW(self.model.bk.parameters(), lr=cfg.bk_lr, betas=(0.9, 0.98), weight_decay=0.0)
        decay, no_decay, tables = [], [], []
        for n, p in self.model.named_parameters():
            if n.startswith("bk."):
                continue
            if n.startswith("scalar_stage.delta_"):
                tables.append(p)
            elif p.dim() < 2 or "emb" in n or "norm" in n or ".level." in n:
                no_decay.append(p)
            else:
                decay.append(p)
        groups = [{"params": decay, "weight_decay": cfg.weight_decay, "lr_mult": 1.0},
                  {"params": no_decay, "weight_decay": 0.0, "lr_mult": 1.0}]
        if tables:
            groups.append({"params": tables, "weight_decay": 0.0, "lr_mult": cfg.table_lr_mult})
        self.opt = torch.optim.AdamW(groups, lr=cfg.lr, betas=tuple(cfg.betas), fused=self.device.type == "cuda")
        self.samples = 0
        self.step = 0
        self.wall = 0.0
        self.init_info = None if init_ck is None else {
            "path": str(cfg.init_from), "samples": init_ck["samples"], "sha256": sha256_file(cfg.init_from)}
        self.log_path = self.run_dir / "log.jsonl"
        self.saved = []
        if cfg.compile and self.device.type == "cuda":
            self.model.compile_trunk(dynamic=False, mode=os.environ.get("DC_COMPILE_MODE") or None)

    # -- checkpoints -------------------------------------------------------------------------------
    def _ema_state(self) -> Dict[str, torch.Tensor]:
        sd = self.model.state_dict()
        names = [n for n, _ in self.model.named_parameters()]
        out = {k: v.detach().cpu().clone() for k, v in sd.items()}
        for n, e in zip(names, self.ema):
            out[n] = e.detach().cpu().clone()
        return out

    def checkpoint(self, path: Path, full: bool) -> str:
        model_sd = {k: v.detach().cpu() for k, v in self.model.state_dict().items()}
        ema_sd = self._ema_state()
        ck = {
            "kind": "dc-emulator-checkpoint-1",
            "model_config": self.model.cfg.to_dict(),
            "train_config": self.cfg.to_dict(),
            "samples": self.samples,
            "bk_samples": self.bk_samples,
            "steps": self.step,
            "wall_seconds": self.wall,
            "data": self.data_info,
            "init_from": self.init_info,
            "git": git_state(),
            "model": model_sd,
            "ema": ema_sd,
            "weights_sha256": {"model": state_dict_sha256(model_sd), "ema": state_dict_sha256(ema_sd)},
            "norm_stats": {"cond_mean": self.model.cond_mean.cpu(), "cond_std": self.model.cond_std.cpu(),
                           "delta_scale": self.model.delta_scale.cpu(), "n": int(self.model.norm_n)},
        }
        if full:
            ck["optimizer"] = self.opt.state_dict()
            if self.bk_opt is not None:
                ck["bk_optimizer"] = self.bk_opt.state_dict()
            ck["rng"] = {"torch": torch.get_rng_state(),
                         "cuda": torch.cuda.get_rng_state_all() if self.device.type == "cuda" else None}
        return atomic_torch_save(ck, path)

    def resume(self, path: Path) -> bool:
        path = Path(path)
        if not path.exists():
            return False
        ck = torch.load(path, map_location="cpu", weights_only=False)
        free = ("micro_batch", "resume_every_s", "log_every", "compile")    # do not change the mathematics
        a = {k: v for k, v in ck["train_config"].items() if k not in free}
        b = {k: v for k, v in self.cfg.to_dict().items() if k not in free}
        if a != b:
            raise ValueError("resume: training configuration differs from the checkpoint's")
        self.model.load_state_dict(ck["model"])
        names = [n for n, _ in self.model.named_parameters()]
        for n, e in zip(names, self.ema):
            e.copy_(ck["ema"][n].to(e.device))
        self.opt.load_state_dict(ck["optimizer"])
        if self.bk_opt is not None and "bk_optimizer" in ck:
            self.bk_opt.load_state_dict(ck["bk_optimizer"])
        self.bk_samples = int(ck.get("bk_samples", 0))
        self.samples, self.step, self.wall = ck["samples"], ck["steps"], ck["wall_seconds"]
        torch.set_rng_state(ck["rng"]["torch"])
        if ck["rng"]["cuda"] is not None and self.device.type == "cuda":
            torch.cuda.set_rng_state_all(ck["rng"]["cuda"])
        self.init_info = ck.get("init_from")
        self._log({"event": "resume", "samples": self.samples, "steps": self.step})
        return True

    def _log(self, rec: dict) -> None:
        rec = {"t": time.time(), **rec}
        with open(self.log_path, "a") as f:
            f.write(json.dumps(rec) + "\n")

    # -- steps -------------------------------------------------------------------------------------
    def _objective(self, s0, r, a, s1) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        out = self.model.loss_terms(s0, r, a, s1)
        w = self.cfg.weights
        nll = {k: -out[k].mean() for k in self.model.train_terms}
        kl = out["kl"].mean()
        beta = beta_at(self.cfg, self.samples)
        terms = dict(nll)
        budget = budget_window(s0["scalars"][:, SC_TIME])
        if self.cfg.budget_weight != 1.0:
            bw = torch.where(budget, self.cfg.budget_weight, 1.0)
            for k in ("scalars", "ledger"):
                if k in terms:
                    terms[k] = -(out[k] * bw).mean()
        loss = (sum(w.get(k, DEFAULT_WEIGHTS.get(k, 1.0)) * terms[k] for k in terms) + beta * kl) / N_TILES
        stats = {**{"nll_" + k: v.detach() for k, v in nll.items()}, "kl": kl.detach(),
                 "n_changed": out["n_changed"].mean().detach()}
        if budget.any():
            stats["nll_scalars_budget"] = -out["scalars"][budget].mean().detach()
        if (~budget).any():
            stats["nll_scalars_other"] = -out["scalars"][~budget].mean().detach()
        stats["nll_sc_funds"] = -out["sc_funds"].mean().detach()
        if "bk" in out:
            stats["nll_bk_teacher"] = -out["bk"].mean().detach()
        stats["loss_total"] = loss.detach()
        return loss, stats

    @torch.no_grad()
    def _posterior_mode_step(self, s: State, r, a, s_true: State) -> State:
        m = self.model
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=self.device.type == "cuda"):
            cond_in = m.cond_input(s, a, r)
            mu, _ = m.posterior(s, s_true, m.scalar_delta_feats(s, s_true), cond_in)
            dense = m._dense(s, r, cond_in, mu)
        return m._sample_from_dense(dense, s, a, 0.0, "sample", r)

    def train_step(self, batch) -> Dict[str, float]:
        cfg = self.cfg
        lr = lr_at(cfg, self.samples)
        for g in self.opt.param_groups:
            g["lr"] = lr * g.get("lr_mult", 1.0)
        self.model.train()
        if cfg.mode == "onestep":
            s0, r, a, s1 = batch
            B = s0["tile_index"].shape[0]
            j = 0
        else:
            window = batch                       # list of k transitions
            B = window[0][0]["tile_index"].shape[0]
            g = np.random.default_rng((cfg.seed, self.step))
            j = 0 if g.random() < cfg.sf_tf_ratio else int(g.integers(1, len(window)))
            s = window[0][0]
            for i in range(j):
                s = self._posterior_mode_step(s, window[i][1], window[i][2], window[i][3])
            _, r, a, s1 = window[j]
            s0 = s
        self.opt.zero_grad(set_to_none=True)
        mb = cfg.micro_batch if 0 < cfg.micro_batch < B else B
        n_mb = (B + mb - 1) // mb
        acc_stats: Dict[str, torch.Tensor] = {}
        for q in range(n_mb):
            sl = slice(q * mb, min(B, (q + 1) * mb))
            sub = lambda st: {k: v[sl] for k, v in st.items()}
            loss, stats = self._objective(sub(s0), r[sl], a[sl], sub(s1))
            (loss * ((sl.stop - sl.start) / B)).backward()
            for k, v in stats.items():
                acc_stats[k] = acc_stats.get(k, 0) + v * ((sl.stop - sl.start) / B)
        stats = acc_stats
        loss = stats["loss_total"] if "loss_total" in stats else loss
        gn = torch.nn.utils.clip_grad_norm_([p for n, p in self.model.named_parameters() if not n.startswith("bk.")],
                                            cfg.grad_clip)
        self.opt.step()
        if self.bk_opt is not None:
            stats["nll_bk"] = self._bk_updates()
        d = min(cfg.ema_decay, (1 + self.step) / (10 + self.step))
        torch._foreach_lerp_(self.ema, [p.detach() for p in self.model.parameters()], 1.0 - d)
        self.samples += B
        self.step += 1
        stats.update({"loss": stats.pop("loss_total"), "grad_norm": gn.detach()})
        stats["lr"] = lr
        stats["sf_unroll"] = j
        return stats

    def _bk_updates(self) -> torch.Tensor:
        """The third stage's own schedule: cfg.bk_updates scalar-only updates on true next-month census."""
        cfg = self.cfg
        total = max(1, int(cfg.samples / cfg.batch_size) * cfg.bk_updates * cfg.bk_batch)
        lr = cfg.bk_lr * (0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * min(1.0, self.bk_samples / total))))
        for g in self.bk_opt.param_groups:
            g["lr"] = lr
        acc = 0.0
        for _ in range(cfg.bk_updates):
            raw, act, ct, d = self.book.sample(cfg.bk_batch)
            lp = self.model.bk_logp(raw, act, ct, d)
            w = torch.where(budget_window(ct), cfg.budget_weight, 1.0).unsqueeze(1)
            loss = -(lp * w).mean()
            self.bk_opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.bk.parameters(), 1.0)
            self.bk_opt.step()
            self.bk_samples += cfg.bk_batch
            acc = acc + (-lp.sum(1).mean()).detach()
        return acc / cfg.bk_updates

    # -- loop --------------------------------------------------------------------------------------
    def run(self, batches: Iterator, on_milestone=None, max_seconds: Optional[float] = None) -> List[dict]:
        cfg = self.cfg
        todo = [m for m in milestones(cfg) if m > self.samples]
        t_last_resume = time.time()
        t0 = time.time()
        wall0 = self.wall
        acc: Dict[str, List[torch.Tensor]] = {}
        n_acc, t_acc, s_acc = 0, time.time(), self.samples
        while self.samples < cfg.samples:
            batch = next(batches)
            st = self.train_step(batch)
            for k, v in st.items():
                acc.setdefault(k, []).append(v if torch.is_tensor(v) else torch.tensor(float(v)))
            n_acc += 1
            self.wall = wall0 + (time.time() - t0)
            if self.step % cfg.log_every == 0:
                if self.device.type == "cuda":
                    torch.cuda.synchronize()
                dt = time.time() - t_acc
                rec = {k: float(torch.stack([x.float().cpu() for x in v]).mean()) for k, v in acc.items()}
                rec.update({"samples": self.samples, "bk_samples": self.bk_samples, "steps": self.step,
                            "samples_per_s": (self.samples - s_acc) / dt,
                            "wall_s": self.wall,
                            "gpu_mem_gb": torch.cuda.max_memory_allocated() / 2**30 if self.device.type == "cuda" else 0})
                self._log(rec)
                acc, n_acc, t_acc, s_acc = {}, 0, time.time(), self.samples
            while todo and self.samples >= todo[0]:
                name = f"samples_{self.samples:09d}.pt"
                digest = self.checkpoint(self.run_dir / name, full=False)
                info = {"event": "milestone", "milestone": todo[0], "samples": self.samples, "steps": self.step,
                        "path": str(self.run_dir / name), "sha256": digest}
                self._log(info)
                self.saved.append(info)
                todo.pop(0)
                if on_milestone is not None:
                    on_milestone(self, info)
            if time.time() - t_last_resume > cfg.resume_every_s:
                self.checkpoint(self.run_dir / "latest.pt", full=True)
                t_last_resume = time.time()
            if max_seconds is not None and time.time() - t0 > max_seconds:
                break
        self.checkpoint(self.run_dir / "latest.pt", full=True)
        return self.saved


# ----------------------------------------------------------------------------------------------
# Third-stage data: scalar-only rows of the run's own training index
# ----------------------------------------------------------------------------------------------
BOOK_CACHE = Path("<cache>/ckpt/bookkeeping_cache")


def union_tiles_from_plan(plan: np.ndarray) -> np.ndarray:
    """(N, 25) plan rows -> (N, 15) action-raster tile counts per channel: the union area of each channel's
    macro footprints (equals the raster sum; checked on 20,000 train_full rows, 20,000 equal)."""
    import itertools
    from . import grammar
    r = grammar.clip_plan(np.asarray(plan).astype(np.int64))
    ch, x0, x1, y0, y1, n, _ = grammar._macro_geometry(r)
    N, M = ch.shape
    ok = (ch >= 0) & (n > 0)
    out = np.zeros((N, 15), dtype=np.int64)
    for k in range(1, M + 1):
        for comb in itertools.combinations(range(M), k):
            c0 = ch[:, comb[0]]
            same = np.all([ch[:, j] == c0 for j in comb], axis=0) & np.all([ok[:, j] for j in comb], axis=0)
            ix0 = np.max([x0[:, j] for j in comb], axis=0)
            ix1 = np.min([x1[:, j] for j in comb], axis=0)
            iy0 = np.max([y0[:, j] for j in comb], axis=0)
            iy1 = np.min([y1[:, j] for j in comb], axis=0)
            area = np.maximum(0, ix1 - ix0) * np.maximum(0, iy1 - iy0) * same
            sel = area > 0
            np.add.at(out, (np.flatnonzero(sel), c0[sel]), ((-1) ** (k + 1)) * area[sel])
    return out


class BookData:
    """Third-stage rows (raw inputs as ``dc.model.bk_raw``, action scalars, city time, target changes) on a
    device, sampled uniformly with replacement. ``from_cache`` reads the scalar feature cache built by
    code/scripts/bookkeeping_diag.py for the run's own index (so a train_small lineage stays small-data);
    ``from_pool`` computes the same rows from engine transitions through the model's own feature code."""

    def __init__(self, raw: torch.Tensor, act: torch.Tensor, ct: torch.Tensor, d: torch.Tensor, info: dict, seed: int = 0) -> None:
        self.raw, self.act, self.ct, self.d, self.info = raw, act, ct, d, info
        self.n = raw.shape[0]
        self.g = torch.Generator(device=raw.device).manual_seed(seed)
        r = raw.double()
        sl = torch.sign(r) * torch.log1p(r.abs())
        self.stats = {"bk_mean_l": sl.mean(0).cpu(), "bk_std_l": sl.std(0).cpu() + 1e-6,
                      "bk_mean_r": r.mean(0).cpu(), "bk_std_r": r.std(0).cpu() + 1e-6}

    def sample(self, b: int):
        ix = torch.randint(self.n, (b,), device=self.raw.device, generator=self.g)
        return self.raw[ix], self.act[ix], self.ct[ix], self.d[ix]

    @staticmethod
    def from_cache(store, index: np.ndarray, device, seed: int = 0, cache: Path = BOOK_CACHE) -> "BookData":
        from .engine import SC_TIME
        from .model import BK_CENSUS, LEARNED_LEDGER, STAGE3_SCALARS, spend_cost_per_tile
        z = np.load(cache / "train_full.npz")
        idx = np.asarray(index, dtype=np.int64)
        if len(z["cost"]) != store.n_trans:
            raise ValueError("bookkeeping cache does not match the store")
        sc0, sc1, lg0, lg1 = z["sc0"][idx], z["sc1"][idx], z["lg0"][idx], z["lg1"][idx]
        spend = union_tiles_from_plan(np.asarray(store.plan[idx])) * spend_cost_per_tile().double().numpy()
        raw = np.concatenate([sc0, lg0, sc1[:, list(BK_CENSUS)], z["nxt"][idx], z["cost"][idx][:, None], spend,
                              spend.sum(1, keepdims=True)], axis=1)
        d = np.concatenate([sc1[:, list(STAGE3_SCALARS)] - sc0[:, list(STAGE3_SCALARS)],
                            lg1[:, list(LEARNED_LEDGER)] - lg0[:, list(LEARNED_LEDGER)]], axis=1)
        t = lambda a, dt: torch.tensor(np.ascontiguousarray(a), dtype=dt, device=device)
        info = {"source": str(cache / "train_full.npz"), "rows": int(len(idx)),
                "index_sha256": hashlib.sha256(idx.tobytes()).hexdigest()}
        return BookData(t(raw, torch.float32), t(z["act"][idx], torch.float32), t(sc0[:, SC_TIME], torch.float64),
                        t(d, torch.float32), info, seed)

    @staticmethod
    def from_pool(pool: "EnginePool", model: Emulator, seed: int = 0) -> "BookData":
        from .engine import SC_TIME
        from .model import bk_raw
        ids = torch.arange(pool.n, device=pool.device)
        s0, r, a, s1 = pool.transition(ids)
        raw = bk_raw(s0, s1, s1["build_cost"], r.float().sum(dim=(2, 3)).double() * model.spend_cost.double().to(r.device))
        return BookData(raw.float(), a, s0["scalars"][:, SC_TIME].double(), model.bk_targets(s0, s1),
                        {"source": "EnginePool", "rows": pool.n}, seed)
