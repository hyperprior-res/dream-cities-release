"""torch.profiler on the tag's sample_next (kernel shares) + FLOP count of the trunk."""
import sys, time, json, collections
import numpy as np
import torch
from torch.profiler import profile, ProfilerActivity
from torch.utils.flop_counter import FlopCounterMode
from dc import audit as A
from dc import rl as R

CK = "<cache>/ckpt/pilot6_censored/samples_000600064.pt"
B = int(sys.argv[1]); overlay = sys.argv[2]; comp = sys.argv[3] == "1"
inst = sorted(A.load_instances(A.TASKS_JSON, horizon=24), key=lambda i: (i.start_id, i.task))
i0 = inst[0]
eff = A.effective(A.Pools(24).behaviour(i0.start_id)[:512], i0.task, 24)
J = A.EmulatorJudge(CK, device="cuda:0", chunk=128, buckets=(16, 64, 128), compile_trunk=comp, model_src="ladder-v2")
m = J.model
s0 = J.state0(i0)
dev = torch.device("cuda:0")
st = {k: v.repeat(B, *([1] * (v.dim() - 1))).clone() for k, v in s0.items()}
idx = np.arange(B) % len(eff)


def step(st, h):
    r = R.raster_torch(eff[idx, h % 24], dev)
    a = R.act_scalars_torch(eff[idx, h % 24], dev)
    return m.sample_next(st, r, a.float(), temperature=1.0, max_batch=B, overlay=overlay)


for h in range(4):
    st = step(st, h)
torch.cuda.synchronize()
# FLOPs of one trunk call (eager trunk, under autocast as in sample_next)
r = R.raster_torch(eff[idx, 0], dev)
a = R.act_scalars_torch(eff[idx, 0], dev).float()
with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
    cond_in = m.cond_input(st, a, r)
    fc = FlopCounterMode(display=False)
    with fc:
        m.trunk(st["tile_index"], st["flags"], st["power"], st["half"], st["eighth"], r,
                m.cond_mlp(torch.cat([cond_in, torch.zeros(B, 32, device=dev)], 1)), st["terrain"], st["com_rate"])
    tf = fc.get_total_flops()
print(f"trunk FLOPs per sample {tf / B / 1e9:.2f} GFLOP (B={B})")
by = collections.Counter()
for k, v in fc.get_flop_counts().get("Global", {}).items():
    by[str(k)] += v
print({k: round(v / B / 1e9, 2) for k, v in by.most_common()})
NS = 6
with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
    torch.cuda.synchronize(); t = time.perf_counter()
    for h in range(NS):
        st = step(st, h)
    torch.cuda.synchronize(); wall = time.perf_counter() - t
ev = prof.key_averages()
cuda_total = sum(e.self_device_time_total for e in ev) / 1e3
print(f"wall {1000 * wall / NS:.1f} ms/step (profiler on); GPU busy (sum of kernel time) {cuda_total / NS:.1f} ms/step = {100 * cuda_total / 1000 / wall:.1f} % of wall")
cat = collections.Counter()
for e in ev:
    if e.self_device_time_total <= 0:
        continue
    n = e.key.lower()
    if "gemm" in n or "cutlass" in n or "sm80_xmma" in n or "sm89" in n or "ampere" in n or "matmul" in n or "mm_" in n or "triton_tem" in n:
        c = "gemm"
    elif "conv" in n or "dgrad" in n or "implicit" in n or "depthwise" in n or "cudnn" in n:
        c = "conv (cudnn)"
    elif "triton" in n:
        c = "triton fused (elementwise/norm)"
    elif "memcpy" in n or "memset" in n:
        c = "memcpy/memset"
    else:
        c = "other aten"
    cat[c] += e.self_device_time_total / 1e3
for c, v in cat.most_common():
    print(f"  {c:32s} {v / NS:8.2f} ms/step  {100 * v / cuda_total:5.1f} %")
print(ev.table(sort_by="self_cuda_time_total", row_limit=30, max_name_column_width=70))
