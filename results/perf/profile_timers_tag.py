"""Per-part synchronised timers on the tag's sample_next (profiling only: wrappers on the instance)."""
import sys, time, json, collections
import numpy as np
import torch
from dc import audit as A
from dc import rl as R
from dc.grammar import raster_batch, action_scalars_batch, N_COLS

CK = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".pt") else "<cache>/ckpt/pilot6_censored/samples_000600064.pt"
B = int(sys.argv[2]); overlay = sys.argv[3]; comp = sys.argv[4] == "1"
inst = sorted(A.load_instances(A.TASKS_JSON, horizon=24), key=lambda i: (i.start_id, i.task))
i0 = inst[0]
eff = A.effective(A.Pools(24).behaviour(i0.start_id)[:512], i0.task, 24)
J = A.EmulatorJudge(CK, device="cuda:0", chunk=128, buckets=(16, 64, 128), compile_trunk=comp, model_src="ladder-v2")
m = J.model
mod = sys.modules[type(m).__module__]
s0 = J.state0(i0)
dev = torch.device("cuda:0")
T = collections.defaultdict(float)
ON = [False]


def timed(fn, name):
    def w(*a, **k):
        if not ON[0]:
            return fn(*a, **k)
        torch.cuda.synchronize(); t = time.perf_counter()
        out = fn(*a, **k)
        torch.cuda.synchronize(); T[name] += time.perf_counter() - t
        return out
    return w


for name in ("cond_input", "_dense", "_sample_from_dense", "_sample_overlay", "_scalar_dist", "_sample_bk",
             "bk_dist_from_raw", "_cat_logits", "_new_flag_logits", "_bern"):
    setattr(m, name, timed(getattr(m, name), name))
object.__setattr__(m, "_trunk_fn", timed(m._trunk_fn, "trunk"))
m.cond_mlp.forward = timed(m.cond_mlp.forward, "cond_mlp")
for name in ("next_map_summary", "bk_raw", "censor_limits", "censored_next", "dlogistic_mix_sample", "scalar_keys"):
    setattr(mod, name, timed(getattr(mod, name), name))

st = {k: v.repeat(B, *([1] * (v.dim() - 1))).clone() for k, v in s0.items()}
idx = np.arange(B) % len(eff)


def step(st, h, host_raster):
    torch.cuda.synchronize(); t = time.perf_counter()
    if host_raster:
        r = torch.from_numpy(raster_batch(eff[idx, h % 24])).to(dev, non_blocking=True)
        a = torch.from_numpy(action_scalars_batch(eff[idx, h % 24])).to(dev)
    else:
        r = R.raster_torch(eff[idx, h % 24], dev)
        a = R.act_scalars_torch(eff[idx, h % 24], dev)
    torch.cuda.synchronize()
    if ON[0]:
        T["raster_host" if host_raster else "raster_gpu"] += time.perf_counter() - t
    t = time.perf_counter()
    out = m.sample_next(st, r, a.float(), temperature=1.0, max_batch=B, overlay=overlay)
    torch.cuda.synchronize()
    if ON[0]:
        T["sample_next"] += time.perf_counter() - t
    return out


for h in range(3):
    st = step(st, h, True)
NS = 12
for host in (True, False):
    T.clear(); ON[0] = True
    for h in range(NS):
        st = step(st, h, host)
    ON[0] = False
    tot = T["sample_next"]
    print(f"B={B} overlay={overlay} compiled={comp} host_raster={host}: sample_next {1000 * tot / NS:.1f} ms/step (timers on)")
    for k, v in sorted(T.items(), key=lambda kv: -kv[1]):
        print(f"  {k:22s} {1000 * v / NS:8.2f} ms  {100 * v / tot:6.1f} %")
# timers off, whole step
for host in (True, False):
    torch.cuda.synchronize(); t = time.perf_counter()
    for h in range(NS):
        st = step(st, h, host)
    torch.cuda.synchronize(); dt = time.perf_counter() - t
    print(f"timers off host_raster={host}: {1000 * dt / NS:.1f} ms/step = {B * NS / dt:.0f} month-steps/s")
