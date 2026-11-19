"""Is the grader's imagined return a function of the plan alone, or also of the batch it is scored in?"""
import sys
from pathlib import Path

ROOT = Path("<repo>")
EXT = Path("<home>/development/wm2-ext")
sys.path.insert(0, str(ROOT / "hpr-dream"))
import numpy as np  # noqa: E402
from hpr_dream.adaptors import tdmpc2 as td  # noqa: E402

task = sys.argv[1] if len(sys.argv) > 1 else "cheetah-run"
st = td.StartState.load(EXT / "states" / f"{task}-00.npz")
with np.load(ROOT / "results/external" / task / "behaviour-00.npz") as d:
    plans = d["plans"][1000:1300]
g = td.Grader(task, EXT / "checkpoints" / f"{task}-1.pt", len(st.obs), st.prefix.shape[1])
ref = g.returns(st, plans)
for bs in (1, 7, 64, 200, 300):
    g.batch_size = bs
    r = g.returns(st, plans)
    print(f"batch_size {bs:>3} vs 128: bitwise equal {int(np.sum(r == ref))}/{len(r)}, max |diff| {np.max(np.abs(r - ref)):.3g}")
g.batch_size = 128
r1 = g.returns(st, plans[:128])
r2 = g.returns(st, plans[1:129])
print("same batch size 128, rows shifted by one position: bitwise equal",
      int(np.sum(r1[1:] == r2[:-1])), "/ 127")
r3 = g.returns(st, plans[:128])
print("same batch repeated: bitwise equal", int(np.sum(r1 == r3)), "/ 128")
