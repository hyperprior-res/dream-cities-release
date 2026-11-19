"""Parameter counts of the ladder's final one-step checkpoints, read from the saved weights (EMA)."""
import hashlib, json, sys
from pathlib import Path
import torch
ROOT = Path("<cache>/ckpt/ladder_v2")
OUT = Path(__file__).resolve().parents[1] / "data" / "param_counts.json"
res = {}
for size in ("15m", "50m", "100m"):
    p = ROOT / f"os_{size}_full" / "samples_006000000.pt"
    ck = torch.load(p, map_location="cpu", weights_only=False, mmap=True)
    sd = ck["ema"] if ck.get("ema") is not None else ck["model"]
    n = sum(v.numel() for k, v in sd.items() if torch.is_tensor(v) and v.is_floating_point() and "norm_stats" not in k and not k.endswith(("_mean", "_std", "_scale")))
    n_all = sum(v.numel() for v in sd.values() if torch.is_tensor(v))
    res[size] = {"checkpoint": str(p), "sha256_file": (p.with_suffix(".pt.sha256").read_text().split()[0] if p.with_suffix(".pt.sha256").exists() else None),
                 "tensors": len(sd), "elements_all": int(n_all), "elements_float_excl_norm_buffers": int(n),
                 "model_config_size": ck.get("model_config", {}).get("size")}
OUT.write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps(res, indent=1))
