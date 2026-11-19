"""Behaviour cloning of the RL arm's policy from the emulator's own offline training data .

Demonstrations (``select_demonstrations``). The offline training store ``train_full`` only (``dc.data``; the 60
training families): the trajectories played by the scripted builder styles (labels ``builder/<style>``) with the
engine's random disasters off. Left out, each with its count and reason in the extract's manifest:

* random editors, no-op months and budget sweeps (``random/*``, ``noop``, ``budget_sweep``): not builders;
* builder trajectories with perturbations mixed in (``builder/<style>+perturb``): their months carry tax shocks,
  funding cuts, bulldozed wires, roads and plants and forced disasters that are not the builder's choices, and the
  store does not mark which months carry them;
* builder trajectories with random disasters on: the RL environments always run with disasters off, and the
  switch is a ledger entry the policy reads, so these observations are packed differently from any the
  environment produces.

Nothing from the held-out start cities, the tasks files or new engine rollouts enters. Of each kept trajectory the
first 24 months form one demonstration episode: a stored trajectory starts at a loaded start state, as an RL
episode does, and an episode is 24 months, so month t of the demonstration (t = 0..23) is packed exactly as month
t of an environment episode on that start (``dc.rl.pack_engine_obs`` of the observation; ``dc.rl`` environment
features from the scalar trajectory so far, tested equal to ``TaskVecEnv`` playing the stored plan on the engine).
The months after 24 are left out (the month one-hot stops at month 23, and the change since the start would leave
the range of a 24-month episode).

The stored data carries no task, so the task-dependent environment features (``dc.rl.TASK_VEC_COLS``: the task
one-hot, the margin, the statistic's slack, the feasibility clause and theta) are zero in every demonstration,
and their input weights in the policy's vector layer start at zero and stay there (zero input, zero gradient,
checked after training). At the start of PPO the policy therefore acts as the cloned policy whatever the task.

Split, by family (``family_split``): a seeded permutation of the families; held-out families until they hold at
least 5 per cent of the demonstration trajectories (reported only), then validation families likewise (used only
to choose the epoch whose weights are kept), the rest for training. One split for every seed.

Cloning (``train``): the policy network and action factorisation of the frozen learner (``dc.rl.Policy``,
``dc.rl.FROZEN.policy``); the loss is minus the log-probability of the demonstrated month as ``dc.rl.logp_entropy``
defines it (the sum over the heads the month uses of the log-probability of the demonstrated head value; a
canonical plan row's head values are its columns ``dc.rl.HEAD_COLS``). The value head is not trained. Initial
policy-head biases: the head marginals of the training split's demonstrations (``dc.rl.behaviour_head_bias``, mix
0.9). Seeds: initialisation ``seed_for("bc-init", seed)``, data order ``seed_for("bc-order", seed, epoch)``.

The cloned policy is saved as ``bc_s<seed>.pt`` (policy configuration, weights, metadata), which ``run_rl.py
--init-from`` loads (``load_cloned``).
"""

from __future__ import annotations

import hashlib
import json
import os
import queue
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch

from . import data as D
from . import grammar as G
from . import rl
from .engine import LOMASK, NUM_LEDGER, NUM_SCALARS, WORLD_H, WORLD_W
from .seeds import seed_for

BC_VERSION = "bc-1"
EPISODE = rl.H                                   # months per demonstration episode (the RL episode)
SPLIT_NAMES = ("train", "val", "heldout")
HELDOUT_FRAC = 0.05
VAL_FRAC = 0.05
STORE_NAME = "train_full"

# extract arrays: name -> (file, dtype, row shape)
EXTRACT_FILES: Dict[str, Tuple[str, str, Tuple[int, ...]]] = {
    "tiles16": ("tiles16.i16", "<i2", (WORLD_W, WORLD_H)),
    "power": ("power.u1", "|u1", (D.POWER_BYTES,)),          # bit-packed 0/1 (dc.data.pack_power)
    "half": ("half.u8", "|u1", D.OBS_FILES["half"][2]),
    "eighth": ("eighth.i16", "<i2", D.OBS_FILES["eighth"][2]),
    "terrain": ("terrain.u8", "|u1", D.OBS_FILES["terrain"][2]),
    "com_rate": ("com_rate.i16", "<i2", D.OBS_FILES["com_rate"][2]),
    "scalars": ("scalars.f32", "<f4", (NUM_SCALARS,)),        # as dc.rl.pack_engine_obs: int64 -> float64 -> float32
    "ledger": ("ledger.f32", "<f4", (NUM_LEDGER,)),
    "vec": ("vec.f32", "<f4", (rl.N_ENV_VEC,)),              # environment features, task-dependent columns zero
    "actions": ("actions.i16", "<i2", (rl.N_HEADS,)),         # head values of the demonstrated month
    "rows": ("rows.i16", "<i2", (G.N_COLS,)),                 # the stored canonical plan row
}


# ----------------------------------------------------------------------------------------------
# Demonstrations
# ----------------------------------------------------------------------------------------------
def style_of(label: str) -> Optional[str]:
    """'builder/grid' -> 'grid'; anything else (perturbed builders included) -> None."""
    if label.startswith("builder/") and "+" not in label:
        return label.split("/", 1)[1]
    return None


def select_demonstrations(store: D.TrajStore) -> Tuple[np.ndarray, dict]:
    """Trajectory ids of the demonstrations (sorted) and a report: counts by style (trajectories, stored months,
    months used) and what was left out, by label, with the reason."""
    rec = store.traj
    labels = np.array(store.labels)[rec["label_idx"]]
    split = np.array(D.SPLITS)[rec["split"]]
    dis = rec["disasters"].astype(bool)
    Hs = rec["H"].astype(np.int64)
    style = np.array([style_of(l) or "" for l in labels])
    keep = (style != "") & ~dis & (split == "train") & (Hs >= EPISODE)
    reasons = {
        "not a builder": "random editors, no-op months and budget sweeps (random/*, noop, budget_sweep): not builders",
        "perturbed builder": "builder/<style>+perturb: tax shocks, funding cuts, bulldozed wires, roads and plants and "
                             "forced disasters mixed into the months, not the builder's choices, in months the store "
                             "does not mark",
        "random disasters on": "the RL environments run with disasters off; the switch is a ledger entry the policy reads",
        "not the training split": "the store's split is not 'train'",
        "shorter than an episode": f"fewer than {EPISODE} months",
    }
    why = np.full(len(rec), "", dtype=object)
    for j in range(len(rec)):
        if keep[j]:
            continue
        if split[j] != "train":
            why[j] = "not the training split"
        elif labels[j].startswith("builder/") and "+perturb" in labels[j]:
            why[j] = "perturbed builder"
        elif not labels[j].startswith("builder/"):
            why[j] = "not a builder"
        elif dis[j]:
            why[j] = "random disasters on"
        else:
            why[j] = "shorter than an episode"
    by_style = {}
    for s in sorted(set(style[keep].tolist())):
        sel = keep & (style == s)
        by_style[s] = {"trajectories": int(sel.sum()), "months_stored": int(Hs[sel].sum()),
                       "months_used": int(sel.sum()) * EPISODE,
                       "months_left_out_after_24": int(Hs[sel].sum()) - int(sel.sum()) * EPISODE}
    left = {}
    for r in reasons:
        sel = why == r
        if not sel.any():
            continue
        lab = {}
        for l in sorted(set(labels[sel].tolist())):
            s2 = sel & (labels == l)
            lab[l] = {"trajectories": int(s2.sum()), "months": int(Hs[s2].sum())}
        left[r] = {"reason": reasons[r], "trajectories": int(sel.sum()), "months": int(Hs[sel].sum()), "by_label": lab}
    ids = np.flatnonzero(keep).astype(np.int64)
    report = {"store": str(store.path), "store_trajectories": int(len(rec)), "store_months": int(Hs.sum()),
              "kept_trajectories": int(keep.sum()), "kept_months_stored": int(Hs[keep].sum()),
              "kept_months_used": int(keep.sum()) * EPISODE, "episode_months": EPISODE, "by_style": by_style,
              "left_out": left,
              "months_after_24_left_out": "the RL episode is 24 months from a loaded start; month t of a stored "
                                          "trajectory is month t of an episode only for t < 24"}
    return ids, report


def family_split(store: D.TrajStore, traj_ids: np.ndarray, heldout_frac: float = HELDOUT_FRAC,
                 val_frac: float = VAL_FRAC) -> Tuple[Dict[str, np.ndarray], dict]:
    """By family: a permutation of the families (``seed_for("bc-split")``); in that order, families go to the
    held-out split while adding one brings its share of the trajectories nearer to ``heldout_frac``, then to the
    validation split likewise (``val_frac``), the rest to training. Returns {split: sorted trajectory ids} and a
    report."""
    fam_idx = store.traj["family_idx"][traj_ids].astype(np.int64)
    fams = np.unique(fam_idx)
    rng = np.random.default_rng(seed_for("bc-split"))
    order = [int(f) for f in fams[rng.permutation(len(fams))]]
    n = len(traj_ids)
    counts = {int(f): int((fam_idx == f).sum()) for f in fams}
    assign: Dict[int, str] = {}
    pos = 0
    for split, frac in (("heldout", heldout_frac), ("val", val_frac)):
        tot = 0
        while pos < len(order) and abs(tot + counts[order[pos]] - frac * n) < abs(tot - frac * n):
            assign[order[pos]] = split
            tot += counts[order[pos]]
            pos += 1
    for f in order[pos:]:
        assign[f] = "train"
    out = {}
    rep = {"rule": f"seeded permutation of the families (seed_for('bc-split')); in that order, families go to the "
                   f"held-out split while adding one brings its share nearer to {heldout_frac:.0%} of the "
                   f"trajectories, then to validation likewise ({val_frac:.0%}), the rest to training",
           "splits": {}}
    for s in SPLIT_NAMES:
        fs = sorted(f for f, a in assign.items() if a == s)
        sel = np.isin(fam_idx, fs)
        out[s] = np.sort(traj_ids[sel])
        rep["splits"][s] = {"families": len(fs), "family_ids": [store.families[f] for f in fs] if s != "train" else None,
                            "trajectories": int(sel.sum()), "share": float(sel.sum() / n),
                            "months": int(sel.sum()) * EPISODE}
    return out, rep


def demo_features(scal: np.ndarray) -> np.ndarray:
    """(24, 20) float64 scalar rows of months 0..23 of one trajectory -> (24, 74) float32 environment features of
    months 0..23, task-dependent columns zero (``dc.rl.taskfree_features``, the function ``TaskVecEnv.vec`` uses)."""
    T_ = scal.shape[0]
    traj = np.broadcast_to(scal[None], (T_, T_, NUM_SCALARS))
    return rl.taskfree_features(np.ascontiguousarray(traj), np.arange(T_))


def pack_rows(tiles: np.ndarray, power_packed: np.ndarray, half, eighth, terrain, com_rate, scalars, ledger) -> dict:
    """Stored observation rows -> the extract's rows: exactly ``dc.rl.pack_engine_obs``'s values (tiles16 = tile code
    | the five flags at bits 10..14; power 0/1, kept bit-packed; scalars and ledger int64 -> float64 -> float32)."""
    t = np.asarray(tiles).astype(np.int64)
    t16 = t & LOMASK
    for i, b in enumerate(rl.ENGINE_FLAG_BITS):
        t16 |= ((t & b) > 0).astype(np.int64) << (rl.FLAG_SHIFT + i)
    return {"tiles16": t16.astype(np.int16), "power": np.asarray(power_packed, dtype=np.uint8),
            "half": np.asarray(half, dtype=np.uint8), "eighth": np.asarray(eighth, dtype=np.int16),
            "terrain": np.asarray(terrain, dtype=np.uint8), "com_rate": np.asarray(com_rate, dtype=np.int16),
            "scalars": np.asarray(scalars).astype(np.float64).astype(np.float32),
            "ledger": np.asarray(ledger).astype(np.float64).astype(np.float32)}


def head_values(rows: np.ndarray) -> np.ndarray:
    """Canonical plan rows (n, 25) -> the policy's head values (n, 24): the columns ``dc.rl.HEAD_COLS``."""
    r = np.asarray(rows).astype(np.int64)
    if not np.array_equal(G.clip_plan(r).astype(np.int64), r):
        raise ValueError("demonstrated rows are not canonical plan rows")
    return r[:, rl.HEAD_COLS].astype(np.int16)


def _sha256(path, buf: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(buf), b""):
            h.update(b)
    return h.hexdigest()


def extract(out_dir, store_path=None, chunk: int = 64, log=print, limit: Optional[int] = None) -> dict:
    """Write the demonstration extract to ``out_dir`` (rows in the order: split train, val, heldout; within a split by
    trajectory id; 24 rows per trajectory). Written under ``<out_dir>.tmp`` and renamed when complete; an existing
    complete extract is returned as it is. One process, contiguous reads of 24 rows per trajectory.
    ``limit``: the first n demonstration trajectories of each split only (tests)."""
    out_dir = Path(out_dir)
    if (out_dir / "manifest.json").exists():
        return json.loads((out_dir / "manifest.json").read_text())
    store = D.TrajStore(store_path or (D.DATA_ROOT / STORE_NAME))
    if not store.complete or not store.has_ledger:
        raise RuntimeError(f"{store.path}: not a complete store with the ledger arrays")
    ids, sel_rep = select_demonstrations(store)
    splits, split_rep = family_split(store, ids)
    if limit is not None:
        splits = {s: v[:limit] for s, v in splits.items()}
    order = np.concatenate([splits[s] for s in SPLIT_NAMES])
    split_of = np.concatenate([np.full(len(splits[s]), k, dtype=np.int8) for k, s in enumerate(SPLIT_NAMES)])
    N = len(order) * EPISODE
    tmp = out_dir.with_name(out_dir.name + ".tmp")
    tmp.mkdir(parents=True, exist_ok=True)
    mm = {}
    for k, (f, dt, shape) in EXTRACT_FILES.items():
        mm[k] = np.lib.format.open_memmap(tmp / (f + ".npy"), mode="w+", dtype=np.dtype(dt), shape=(N, *shape))
    m = store._maps()
    t0 = time.time()
    rec = store.traj
    for c0 in range(0, len(order), chunk):
        js = order[c0:c0 + chunk]
        for k, j in enumerate(js):
            r0 = (c0 + k) * EPISODE
            o, t = int(rec["first_obs"][j]), int(rec["first_trans"][j])
            p = pack_rows(m["tiles"][o:o + EPISODE], m["power"][o:o + EPISODE], m["half"][o:o + EPISODE],
                          m["eighth"][o:o + EPISODE], m["terrain"][o:o + EPISODE], m["com_rate"][o:o + EPISODE],
                          m["scalars"][o:o + EPISODE], m["ledger"][o:o + EPISODE])
            rows = np.asarray(m["plan"][t:t + EPISODE])
            if (rows[:, rl.FORCED_COL] != 0).any():
                raise RuntimeError(f"trajectory {j}: a forced disaster in the month")
            for key, v in p.items():
                mm[key][r0:r0 + EPISODE] = v
            mm["vec"][r0:r0 + EPISODE] = demo_features(np.asarray(m["scalars"][o:o + EPISODE]).astype(np.float64))
            mm["rows"][r0:r0 + EPISODE] = rows
            mm["actions"][r0:r0 + EPISODE] = head_values(rows)
        if (c0 // chunk) % 25 == 0:
            log(f"extract: {c0 + len(js)} / {len(order)} trajectories, {time.time() - t0:.0f} s")
    for v in mm.values():
        v.flush()
    del mm
    st = store.traj[order]
    table = {"traj_id": order, "split": split_of, "family_idx": st["family_idx"].astype(np.int32),
             "start_idx": st["start_idx"].astype(np.int32), "seed": st["seed"].astype(np.int64),
             "label": np.array(store.labels)[st["label_idx"]].astype(str),
             "family_id": np.array(store.families)[st["family_idx"]].astype(str),
             "start_id": np.array([store.starts[int(s)]["start_id"] for s in st["start_idx"]]).astype(str),
             "cty_path": np.array([store.starts[int(s)]["path"] for s in st["start_idx"]]).astype(str)}
    np.savez(tmp / "trajectories.npz", **table)
    files = {k: {"file": f + ".npy", "sha256": _sha256(tmp / (f + ".npy"))} for k, (f, _, _) in EXTRACT_FILES.items()}
    files["trajectories"] = {"file": "trajectories.npz", "sha256": _sha256(tmp / "trajectories.npz")}
    man = {"version": BC_VERSION, "store": str(store.path), "store_manifest_sha256": _sha256(store.path / "manifest.json"),
           "store_traj_rec_sha256": store.manifest["traj_rec"]["sha256"], "rows": int(N),
           "rows_by_split": {s: int(len(splits[s]) * EPISODE) for s in SPLIT_NAMES},
           "trajectories_by_split": {s: int(len(splits[s])) for s in SPLIT_NAMES},
           "selection": sel_rep, "split": split_rep, "limit": limit, "task_vec_cols": list(rl.TASK_VEC_COLS),
           "files": files, "seconds": time.time() - t0,
           "code_sha256": {"dc/bc.py": _sha256(Path(__file__)), "dc/rl.py": _sha256(Path(rl.__file__))}}
    (tmp / "manifest.json").write_text(json.dumps(man, indent=1))
    os.replace(tmp, out_dir)
    log(f"extract: {N:,} rows in {time.time() - t0:.0f} s -> {out_dir}")
    return man


class Demos:
    """The extract, memory-mapped; ``rows_of(split)`` the row indices of a split; ``batch(idx, device)`` the
    policy's inputs and the demonstrated head values."""

    def __init__(self, path) -> None:
        self.path = Path(path)
        self.manifest = json.loads((self.path / "manifest.json").read_text())
        self.mm = {k: np.load(self.path / (f + ".npy"), mmap_mode="r") for k, (f, _, _) in EXTRACT_FILES.items()}
        with np.load(self.path / "trajectories.npz") as z:
            self.table = {k: z[k] for k in z.files}
        self.split_of_row = np.repeat(self.table["split"], EPISODE)
        self.month_of_row = np.tile(np.arange(EPISODE), len(self.table["split"]))
        self.n = int(self.manifest["rows"])

    def rows_of(self, split: str) -> np.ndarray:
        return np.flatnonzero(self.split_of_row == SPLIT_NAMES.index(split)).astype(np.int64)

    def gather(self, idx: np.ndarray) -> Dict[str, np.ndarray]:
        idx = np.sort(np.asarray(idx, dtype=np.int64))
        return {k: np.asarray(v[idx]) for k, v in self.mm.items()}

    @staticmethod
    def to_device(b: Dict[str, np.ndarray], device) -> Tuple[Dict[str, torch.Tensor], torch.Tensor, torch.Tensor]:
        dev = torch.device(device)
        nb = dev.type == "cuda"
        t = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(dev, non_blocking=nb)
        ob = {"tiles16": t(b["tiles16"]), "half": t(b["half"]), "eighth": t(b["eighth"]), "terrain": t(b["terrain"]),
              "com_rate": t(b["com_rate"]), "scalars": t(b["scalars"]), "ledger": t(b["ledger"])}
        ob["power"] = D._torch_unpack(t(b["power"]), D.N_TILES, (WORLD_W, WORLD_H)).to(torch.uint8)
        return ob, t(b["vec"]), t(b["actions"]).long()


def unpack_np(b: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Extract rows -> ``dc.rl.pack_engine_obs``'s format (numpy; power unpacked; overlays as float32)."""
    return {"tiles16": b["tiles16"], "power": D.unpack_power(b["power"]), "half": b["half"].astype(np.float32),
            "eighth": b["eighth"].astype(np.float32), "terrain": b["terrain"].astype(np.float32),
            "com_rate": b["com_rate"].astype(np.float32), "scalars": b["scalars"], "ledger": b["ledger"]}


# ----------------------------------------------------------------------------------------------
# Cloning
# ----------------------------------------------------------------------------------------------
@dataclass
class BCConfig:
    epochs: int = 8                 # passes over the training split; the epoch with the best validation likelihood is kept
    batch: int = 512
    lr: float = 5e-4                # Adam; linear warm-up, then cosine decay to zero at the last epoch
    warmup_steps: int = 300
    adam_eps: float = 1e-8
    weight_decay: float = 0.0       # > 0: AdamW (decoupled decay; a zero weight stays zero)
    max_grad_norm: float = 1.0
    init_mix: float = 0.9           # policy-head biases: log(mix x training-split marginal + (1 - mix) x uniform)
    eval_batch: int = 1024
    evals_per_epoch: int = 1        # validations per epoch (the kept weights are the best validation's)
    policy: rl.PolicyConfig = field(default_factory=lambda: rl.FROZEN.policy)

    def to_dict(self) -> dict:
        return asdict(self)


# The cloning configuration, chosen on the validation families only (held-out families unread for the choice): the
# first configuration (8 epochs, validation once per epoch) kept epoch 1 at -18.52 nats per month; this one (2 epochs,
# validation every quarter epoch, decoupled weight decay 0.05) kept half an epoch at -15.97 (initial policy -20.36).
BC_FIRST = BCConfig()
BC_FROZEN = BCConfig(epochs=2, evals_per_epoch=4, weight_decay=0.05)


def zero_task_inputs(policy: rl.Policy) -> None:
    with torch.no_grad():
        policy.vec_fc.weight[:, list(rl.TASK_VEC_COLS)] = 0.0


def task_inputs_zero(policy: rl.Policy) -> bool:
    return bool((policy.vec_fc.weight[:, list(rl.TASK_VEC_COLS)] == 0).all())


def head_loglik(logits: torch.Tensor, actions: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Per row and head: log-probability of the demonstrated head value (B, 24), and the used mask (B, 24)."""
    lps = rl.head_logps(logits)
    lp = torch.stack([lps[i].gather(1, actions[:, i:i + 1]).squeeze(1) for i in range(rl.N_HEADS)], dim=1)
    return lp, rl.used_heads(actions)


HEAD_NAMES = ["tax", "road", "fire", "police"] + [f"m{j}_{f}" for j in range(G.M) for f in ("kind", "x", "y", "a", "b")]


def evaluate(policy: rl.Policy, demos: Demos, rows: np.ndarray, device, cfg: BCConfig, sample_seed: int) -> dict:
    """On the given demonstration rows: mean log-likelihood per month (the loss's quantity), per head over the rows
    that use it, arg-max accuracy per head, and the share of months containing a macro, for the demonstrations and
    for one month sampled from the policy at each row (generator seeded ``sample_seed``)."""
    policy.eval()
    s_lp = np.zeros(rl.N_HEADS)
    s_n = np.zeros(rl.N_HEADS)
    s_acc = np.zeros(rl.N_HEADS)
    tot = 0.0
    n = 0
    mac_demo = mac_samp = nmac_demo = nmac_samp = 0.0
    gen = torch.Generator(device=device)
    gen.manual_seed(int(sample_seed))
    with torch.no_grad():
        for c0 in range(0, len(rows), cfg.eval_batch):
            ob, vec, act = Demos.to_device(demos.gather(rows[c0:c0 + cfg.eval_batch]), device)
            logits, _ = policy(ob, vec)
            lp, used = head_loglik(logits, act)
            u = used.float()
            s_lp += (lp * u).sum(0).double().cpu().numpy()
            s_n += u.sum(0).double().cpu().numpy()
            am = rl.sample_actions(logits, None, greedy=True)
            s_acc += ((am == act).float() * u).sum(0).double().cpu().numpy()
            tot += float((lp * u).sum())
            n += act.shape[0]
            samp = rl.sample_actions(logits, gen)
            kd = act[:, rl.KIND_HEADS] > 0
            ks = samp[:, rl.KIND_HEADS] > 0
            mac_demo += float(kd.any(1).float().sum())
            mac_samp += float(ks.any(1).float().sum())
            nmac_demo += float(kd.float().sum())
            nmac_samp += float(ks.float().sum())
    per_head = {HEAD_NAMES[i]: {"loglik": float(s_lp[i] / max(s_n[i], 1)), "rows_used": int(s_n[i]),
                                "argmax_accuracy": float(s_acc[i] / max(s_n[i], 1))} for i in range(rl.N_HEADS)}
    return {"rows": int(n), "loglik_per_month": tot / max(n, 1), "per_head": per_head,
            "month_has_macro_demo": mac_demo / max(n, 1), "month_has_macro_sampled": mac_samp / max(n, 1),
            "macros_per_month_demo": nmac_demo / max(n, 1), "macros_per_month_sampled": nmac_samp / max(n, 1)}


class _Prefetch:
    """Batches gathered by one background thread (numpy from the memory map), ``depth`` ahead."""

    def __init__(self, demos: Demos, batches: List[np.ndarray], depth: int = 3) -> None:
        self.q: "queue.Queue" = queue.Queue(maxsize=depth)
        self.demos, self.batches = demos, batches
        self.th = threading.Thread(target=self._run, daemon=True)
        self.th.start()

    def _run(self) -> None:
        for b in self.batches:
            self.q.put(self.demos.gather(b))
        self.q.put(None)

    def __iter__(self):
        while True:
            b = self.q.get()
            if b is None:
                return
            yield b


def _lr_at(cfg: BCConfig, step: int, total: int) -> float:
    if step < cfg.warmup_steps:
        return cfg.lr * (step + 1) / cfg.warmup_steps
    p = (step - cfg.warmup_steps) / max(1, total - cfg.warmup_steps)
    return cfg.lr * 0.5 * (1.0 + np.cos(np.pi * min(1.0, p)))


def train(demos: Demos, seed: int, out_dir, device="cuda:0", cfg: BCConfig = BC_FROZEN, log=print,
          stop_after_epochs: Optional[int] = None, max_train_rows: Optional[int] = None,
          chunk: Optional[int] = None) -> dict:
    """Behaviour cloning of one policy (``seed``). Resumable at epoch boundaries (``<out_dir>/bc_s<seed>.latest.pt``).
    Writes ``bc_s<seed>.pt`` (the kept epoch's weights), ``bc_s<seed>.log.jsonl`` and returns the summary.
    ``max_train_rows``: use only the first n training rows (tests). ``chunk``: rows per forward / backward pass (the
    batch's gradient accumulated; memory on the card only, numbers equal but for rounding)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dev = torch.device(device)
    tr_rows = demos.rows_of("train")
    if max_train_rows is not None:
        tr_rows = tr_rows[:max_train_rows]
    va_rows, ho_rows = demos.rows_of("val"), demos.rows_of("heldout")
    torch.manual_seed(seed_for("bc-init", seed))
    pol = rl.Policy(cfg.policy).to(dev)
    tr_act = np.asarray(demos.mm["rows"][np.sort(tr_rows)])
    bias = rl.behaviour_head_bias(tr_act, cfg.init_mix)
    pol.set_head_bias(bias)
    zero_task_inputs(pol)
    if cfg.weight_decay > 0:
        opt = torch.optim.AdamW(pol.parameters(), lr=cfg.lr, eps=cfg.adam_eps, weight_decay=cfg.weight_decay)
    else:
        opt = torch.optim.Adam(pol.parameters(), lr=cfg.lr, eps=cfg.adam_eps)
    steps_per_epoch = len(tr_rows) // cfg.batch
    total = steps_per_epoch * cfg.epochs
    latest = out_dir / f"bc_s{seed}.latest.pt"
    logp = out_dir / f"bc_s{seed}.log.jsonl"
    meta = {"version": BC_VERSION, "seed": int(seed), "cfg": cfg.to_dict(), "extract": str(demos.path),
            "extract_manifest_sha256": _sha256(demos.path / "manifest.json"), "train_rows": int(len(tr_rows)),
            "val_rows": int(len(va_rows)), "heldout_rows": int(len(ho_rows)), "steps_per_epoch": steps_per_epoch,
            "init_bias_sha256": hashlib.sha256(bias.tobytes()).hexdigest()[:16], "device": str(dev),
            "task_vec_cols": list(rl.TASK_VEC_COLS), "max_train_rows": max_train_rows}
    epoch, step, best = 0, 0, None
    hist: List[dict] = []
    if latest.exists():
        ck = torch.load(latest, map_location="cpu", weights_only=False)
        if ck["meta"] != meta:
            raise RuntimeError(f"{latest} was written under another configuration")
        pol.load_state_dict(ck["policy"])
        opt.load_state_dict(ck["opt"])
        epoch, step, best, hist = ck["epoch"], ck["step"], ck["best"], ck["hist"]
        log(f"bc s{seed}: resumed at epoch {epoch}")
    else:
        logp.write_text("")
        e0 = evaluate(pol, demos, va_rows, dev, cfg, seed_for("bc-sample", seed, "val", 0))
        rec = {"epoch": 0, "step": 0, "val_loglik_per_month": e0["loglik_per_month"], "train_loss": None}
        hist.append(rec)
        with open(logp, "a") as f:
            f.write(json.dumps(rec) + "\n")
    done_now = 0
    t_start = time.time()

    def _validate(ep, st_, train_loss, t0, best):
        if not task_inputs_zero(pol):
            raise RuntimeError("task-dependent input weights moved off zero")
        ev = evaluate(pol, demos, va_rows, dev, cfg, seed_for("bc-sample", seed, "val", ep))
        rec = {"epoch": ep, "step": st_, "train_loss": train_loss, "val_loglik_per_month": ev["loglik_per_month"],
               "val_month_has_macro_sampled": ev["month_has_macro_sampled"], "seconds": time.time() - t0}
        hist.append(rec)
        with open(logp, "a") as f:
            f.write(json.dumps(rec) + "\n")
        log(f"bc s{seed}: epoch {ep}: train loss {train_loss:.4f}, validation log-likelihood per month "
            f"{ev['loglik_per_month']:.4f} ({rec['seconds']:.0f} s)")
        if best is None or ev["loglik_per_month"] > best["val_loglik_per_month"]:
            best = {"epoch": ep, "val_loglik_per_month": ev["loglik_per_month"],
                    "policy": {k: v.detach().cpu().clone() for k, v in pol.state_dict().items()}}
        return best
    while epoch < cfg.epochs:
        if stop_after_epochs is not None and done_now >= stop_after_epochs:
            return {"stopped": True, "epoch": epoch}
        perm = tr_rows[np.random.default_rng(seed_for("bc-order", seed, epoch)).permutation(len(tr_rows))]
        batches = [perm[i * cfg.batch:(i + 1) * cfg.batch] for i in range(steps_per_epoch)]
        pol.train()
        t0 = time.time()
        run_loss, run_n = 0.0, 0
        for b in _Prefetch(demos, batches):
            ob, vec, act = Demos.to_device(b, dev)
            for g in opt.param_groups:
                g["lr"] = _lr_at(cfg, step, total)
            opt.zero_grad(set_to_none=True)
            B = act.shape[0]
            cs = min(chunk or B, B)
            bl = 0.0
            for c0 in range(0, B, cs):
                sl = slice(c0, c0 + cs)
                logits, _ = pol({k: v[sl] for k, v in ob.items()}, vec[sl])
                lp, used = head_loglik(logits, act[sl])
                loss = -(lp * used.float()).sum(1).sum() / B          # the batch mean, accumulated over chunks
                loss.backward()
                bl += float(loss.detach())
            torch.nn.utils.clip_grad_norm_(pol.parameters(), cfg.max_grad_norm)
            opt.step()
            step += 1
            run_loss += bl
            run_n += 1
            if step % 200 == 0:
                log(f"bc s{seed}: epoch {epoch + 1} step {step}/{total} loss {run_loss / run_n:.4f} "
                    f"({(time.time() - t0) / run_n:.3f} s/step)")
            if cfg.evals_per_epoch > 1 and run_n < steps_per_epoch and run_n % (steps_per_epoch // cfg.evals_per_epoch) == 0:
                best = _validate(epoch + run_n / steps_per_epoch, step, run_loss / run_n, t0, best)
                pol.train()
        epoch += 1
        done_now += 1
        best = _validate(float(epoch) if cfg.evals_per_epoch > 1 else epoch, step, run_loss / max(run_n, 1), t0, best)
        tmp = latest.with_name(latest.name + ".tmp")
        torch.save({"meta": meta, "policy": pol.state_dict(), "opt": opt.state_dict(), "epoch": epoch, "step": step,
                    "best": best, "hist": hist}, tmp)
        os.replace(tmp, latest)
    # the kept weights: the epoch with the best validation likelihood
    pol.load_state_dict(best["policy"])
    if not task_inputs_zero(pol):
        raise RuntimeError("task-dependent input weights are not zero")
    torch.manual_seed(seed_for("bc-init", seed))                  # the initial policy, as a yardstick
    init = rl.Policy(cfg.policy).to(dev)
    init.set_head_bias(bias)
    zero_task_inputs(init)
    res = {"meta": meta, "kept_epoch": best["epoch"], "history": hist,
           "heldout": evaluate(pol, demos, ho_rows, dev, cfg, seed_for("bc-sample", seed, "heldout")),
           "heldout_initial_policy": evaluate(init, demos, ho_rows, dev, cfg, seed_for("bc-sample", seed, "heldout")),
           "val": evaluate(pol, demos, va_rows, dev, cfg, seed_for("bc-sample", seed, "val", "final")),
           "policy_sha256": rl.policy_sha256(pol), "policy_parameters": pol.num_parameters(),
           "train_seconds_this_invocation": time.time() - t_start}
    torch.save({"version": BC_VERSION, "policy_cfg": asdict(cfg.policy), "policy": pol.state_dict(),
                "meta": {k: v for k, v in res.items() if k not in ("history",)}}, out_dir / f"bc_s{seed}.pt")
    (out_dir / f"bc_s{seed}.json").write_text(json.dumps(res, indent=1, default=str))
    return res


def load_cloned(path, policy_cfg: rl.PolicyConfig) -> Tuple[Dict[str, torch.Tensor], dict]:
    """A cloned policy's weights (CPU) and metadata; refuses another policy configuration or task-dependent input
    weights that are not zero."""
    ck = torch.load(path, map_location="cpu", weights_only=False)
    if ck.get("version") != BC_VERSION:
        raise RuntimeError(f"{path}: not a cloned policy of version {BC_VERSION}")
    if rl.PolicyConfig(**ck["policy_cfg"]) != policy_cfg:
        raise RuntimeError(f"{path}: policy configuration {ck['policy_cfg']} is not the learner's {asdict(policy_cfg)}")
    pol = rl.Policy(policy_cfg)
    pol.load_state_dict(ck["policy"])
    if not task_inputs_zero(pol):
        raise RuntimeError(f"{path}: task-dependent input weights are not zero")
    return ck["policy"], ck["meta"]
