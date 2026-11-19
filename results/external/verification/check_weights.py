"""Audit (a) (check_weights.out was produced on the first builder's run layout, before its outputs
were archived; the behaviour-plan part now reads the reported run).

Audit (a): released checkpoint bytes, keys and values actually loaded into the grader.

Run with wm2-ext/venv, CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path("<repo>")
EXT = Path("<home>/development/wm2-ext")
sys.path.insert(0, str(ROOT / "hpr-dream"))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from hpr_dream.adaptors import tdmpc2 as td  # noqa: E402

NAME_MAP = ["weight", "bias", "ln.weight", "ln.bias"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


prov = json.loads((EXT / "provenance.json").read_text())
print("== sha256 against provenance.json")
for c in prov["checkpoints"]:
    p = EXT / "checkpoints" / c["file"]
    h = sha(p)
    print(c["task"], c["file"], h, "match" if h == c["sha256"] else "MISMATCH",
          "bytes", p.stat().st_size, "match" if p.stat().st_size == c["bytes"] else "MISMATCH")

for task in ("cheetah-run", "walker-walk", "hopper-hop"):
    print(f"\n== {task}")
    path = EXT / "checkpoints" / f"{task}-1.pt"
    st = td.capture_start(task, 1000)
    obs_dim, act_dim = len(st.obs), st.prefix.shape[1]
    raw_file = torch.load(path, map_location="cpu", weights_only=False)
    print("file top-level keys", sorted(raw_file.keys()), "metadata", raw_file.get("metadata"))
    raw = {k: v.detach().clone() for k, v in raw_file["model"].items()}
    raw_numel = sum(v.numel() for v in raw.values())
    g = td.Grader(task, path, obs_dim, act_dim)
    model = g.agent.model
    sd = {k: v for k, v in model.state_dict().items()}

    def targets(k):
        if k.startswith("_Qs.params."):
            n = int(k.rsplit(".", 1)[1])
            sub = f"{n // 4}.{NAME_MAP[n % 4]}"
            return [f"_Qs.params.{sub}", f"_detach_Qs_params.{sub}"]
        if k.startswith("_target_Qs.params."):
            n = int(k.rsplit(".", 1)[1])
            return [f"_target_Qs_params.{n // 4}.{NAME_MAP[n % 4]}"]
        return [k]

    covered, absent, unequal = set(), [], []
    for k, v in raw.items():
        for t in targets(k):
            if t not in sd:
                absent.append((k, t))
                continue
            covered.add(t)
            if not torch.equal(sd[t].detach().cpu(), v):
                unequal.append(t)
    not_from_file = sorted(k for k in sd if k not in covered)
    print(f"file tensors {len(raw)}, file numel {raw_numel:,}; model state-dict entries {len(sd)}")
    print("file keys with no model entry:", absent)
    print("model entries whose value differs from the file:", unequal)
    print("model entries not supplied by the file:", not_from_file)
    for k in not_from_file:
        v = sd[k]
        print("   ", k, (v.detach().cpu().tolist() if hasattr(v, "numel") and v.numel() < 5 else type(v)))

    # strict-load report on a fresh agent, using the authors' own conversion
    from common.layers import api_model_conversion
    from tdmpc2 import TDMPC2
    fresh = TDMPC2(g.agent.cfg)
    conv = api_model_conversion(fresh.model.state_dict(), {k: v.clone() for k, v in raw.items()})
    res = fresh.model.load_state_dict(conv, strict=False)
    print("load_state_dict(strict=False) on the converted file: missing", res.missing_keys,
          "unexpected", res.unexpected_keys)

    # a freshly initialised (never loaded) model for contrast
    from common.world_model import WorldModel
    init_model = WorldModel(g.agent.cfg).to("cuda:0")
    grader_mods = ("_encoder", "_dynamics", "_reward")
    n_grader = sum(p.numel() for m in grader_mods for p in getattr(model, m).parameters())
    print(f"learnable parameters (authors' total_params) {model.total_params:,}; "
          f"encoder+dynamics+reward {n_grader:,}")
    same_as_file = all(torch.equal(p.detach().cpu(), raw[f"{m}.{n}"]) for m in grader_mods
                       for n, p in getattr(model, m).named_parameters())
    same_as_init = [f"{m}.{n}" for m in grader_mods for n, p in getattr(model, m).named_parameters()
                    if torch.equal(p.detach(), dict(getattr(init_model, m).named_parameters())[n].detach())]
    print("every encoder/dynamics/reward parameter equals the file tensor:", same_as_file)
    print("grader parameters equal to a fresh initialisation:", same_as_init)
    print("reward output layer |W|: loaded", float(model._reward[-1].weight.abs().sum()),
          "fresh init", float(init_model._reward[-1].weight.abs().sum()))
    print("model.training", model.training, "dropout modules in grader path:",
          [n for m in grader_mods for n, x in getattr(model, m).named_modules() if isinstance(x, torch.nn.Dropout)])

    # functional contrast on the audit's own behaviour plans (start 0): loaded vs fresh init
    beh = ROOT / "results/external" / task / "behaviour-00.npz"
    if beh.exists():
        state = td.StartState.load(EXT / "states" / f"{task}-00.npz")
        with np.load(beh) as d:
            plans, real = d["plans"][1000:], d["oracle_returns"][1000:]
            if "pool_grader_returns" in d:  # layout of the first builder's run
                stored = d["pool_grader_returns"]
            else:  # layout of the reported run
                with np.load(beh.parent / "pool-00.npz") as q:
                    stored = q["grader_returns"]
        imag = g.returns(state, plans)
        from scipy.stats import spearmanr
        print("start 00, 1,000 pool plans: recomputed imagined == stored (bitwise)",
              imag.tobytes() == stored.tobytes(), "max abs diff", float(np.max(np.abs(imag - stored))))
        print("   spearman(imagined, real)", round(float(spearmanr(imag, real)[0]), 4),
              "imagined mean/sd", round(float(imag.mean()), 4), round(float(imag.std()), 4),
              "real mean/sd", round(float(real.mean()), 4), round(float(real.std()), 4))
        g.agent.model = init_model
        g_init_returns = None
        model_saved = g.agent.model
        imag0 = td.Grader.returns(g, state, plans[:200])
        print("   fresh-init model on the same plans: imagined min/max", float(imag0.min()), float(imag0.max()))
        g.agent.model = model
    del g, fresh, init_model
    torch.cuda.empty_cache()
