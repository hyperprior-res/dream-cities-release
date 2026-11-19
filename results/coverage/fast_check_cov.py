"""B20: the audit's model loading and ``dc.fast`` accept a checkpoint trained at tag ladder-v2-cov (CPU, tiny model).

    # 1. a tiny untrained checkpoint written by the cov checkout's own Trainer (so its git record is that checkout's)
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python results/coverage/fast_check_cov.py make <out.pt>
    # 2. load it as run_audit.py does (model source "auto" = the checkpoint's training commit) and accelerate it
    PYTHONPATH=code:hpr-dream .venv/bin/python results/coverage/fast_check_cov.py check <out.pt>
"""

import json
import sys
from pathlib import Path

COV = Path("<home>/development/wm2-ladder-v2-cov")
MAIN = Path(__file__).resolve().parents[2]


def make(out: Path) -> None:
    sys.path.insert(0, str(COV / "code"))
    import torch
    from dc.model import SIZES, Emulator
    from dc.train import TrainConfig, Trainer
    m0 = Emulator(SIZES["tiny"])           # its own initial buffers serve as (untrained) normalisation statistics
    stats = {k: getattr(m0, k).clone() for k in ("cond_mean", "cond_std", "delta_scale", "ledger_mean", "ledger_std",
                                                 "ledger_delta_scale") if hasattr(m0, k)}
    stats["n"] = torch.tensor(1)
    tr = Trainer(TrainConfig(size="tiny", samples=0, compile=False), out.parent / "tiny_run", "cpu", norm_stats=stats)
    tr.checkpoint(out, full=False)
    ck = torch.load(out, map_location="cpu", weights_only=False)
    print(json.dumps({"made": str(out), "git": ck["git"], "trainer_module": tr.__class__.__module__,
                      "train_py": str(sys.modules["dc.train"].__file__)}))


def check(path: Path) -> None:
    sys.path.insert(0, str(MAIN / "code"))
    import hashlib
    import subprocess
    import torch
    from dc import audit as A
    from dc import fast
    sha_cov = subprocess.run(["git", "-C", str(MAIN), "rev-parse", "ladder-v2-cov^{commit}"], capture_output=True, text=True,
                             check=True).stdout.strip()
    out = {"ladder-v2-cov": sha_cov, "training_commit": A.training_commit(path)}
    assert out["training_commit"] == sha_cov
    pk_cov, _ = A.code_package("ladder-v2-cov")
    pk_v2, _ = A.code_package("ladder-v2")
    mp = lambda pk: hashlib.sha256((Path(pk.__file__).parent / "model.py").read_bytes()).hexdigest()  # noqa: E731
    out["model_py_identical"] = mp(pk_cov) == mp(pk_v2)
    model, ck, desc, _ = A.load_emulator(path, "cpu", "auto")
    out["load_emulator"] = {k: desc[k] for k in ("model_src", "model_src_resolved", "model_src_commit", "model_py_sha256")}
    out["source_sha_matches_reference"] = fast._source_sha(model) == fast.LADDER_V2_SOURCE_SHA
    import inspect
    mod = sys.modules[type(model).__module__]
    out["scalar_stage_matches_reference"] = (hashlib.sha256(inspect.getsource(mod.ScalarStage.forward).encode()).hexdigest()
                                             == fast.SCALAR_STAGE_SOURCE_SHA)
    plain = model.trunk
    fused = fast.make_fused_trunk(model)
    fast.accelerate(model)                      # on CPU: the fused restatement only (no compile, no graphs)
    out["describe"] = fast.describe(model)
    g = torch.Generator().manual_seed(0)
    B = 3
    cond_dim = model.trunk.enc1[0].film.in_features      # the conditioning width the trunk's FiLM layers take
    args = (torch.randint(0, 1024, (B, 120, 100), generator=g), torch.rand(B, 5, 120, 100, generator=g).round(),
            torch.rand(B, 120, 100, generator=g).round(), 255 * torch.rand(B, 5, 60, 50, generator=g),
            100 * torch.rand(B, 3, 15, 13, generator=g), torch.rand(B, 15, 120, 100, generator=g).round(),
            torch.randn(B, cond_dim, generator=g))
    kw = {"terrain": (255 * torch.rand(B, 30, 25, generator=g)), "com_rate": 64 * torch.rand(B, 15, 13, generator=g)}
    with torch.no_grad():
        a = plain(*args, **kw)
        b = fused(*args, **kw)
        c = model._trunk_fn(*args, **kw)
    diffs = [float((x - y).abs().max()) for x, y in zip(a, b) if x is not None]
    same_obj = all((x is None and y is None) or torch.equal(x, y) for x, y in zip(b, c))
    out["fused_vs_tag_trunk_max_abs_diff"] = max(diffs)
    out["accelerated_equals_fused"] = bool(same_obj)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"make": make, "check": check}[sys.argv[1]](Path(sys.argv[2]))
