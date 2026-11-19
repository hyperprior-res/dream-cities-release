"""Check the proposed union patch (scratch copy of tag ladder-v2 + patch) on the real stores, CPU only.

usage: python union_check.py <patched code dir> <scratch root>
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

code, root = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(code))
sys.path.insert(0, str(code / "scripts"))
from dc import data as D  # noqa: E402

DATA = Path("<cache>/data")
out = {}
u_path = root / "data" / "train_full_cov"
if not (u_path / D.UNION_FILE).exists():
    D.make_union(u_path, [DATA / "train_full", DATA / "train_cov"], name="train_full_cov")
st, idx = D.open_split("train_full_cov", root / "data")
a, b = D.TrajStore(DATA / "train_full"), D.TrajStore(DATA / "train_cov")
out["union"] = {"n_traj": st.n_traj, "n_trans": st.n_trans, "n_obs": st.n_obs, "index_len": int(len(idx)),
                "complete": st.complete, "has_ledger": st.has_ledger, "labels": len(st.labels), "starts": len(st.starts)}
assert st.n_trans == a.n_trans + b.n_trans == len(idx) and st.n_obs == a.n_obs + b.n_obs

# records: every trajectory's record equals its part's
rng = np.random.default_rng(0)
for j in rng.choice(st.n_traj, 300, replace=False):
    r = st.record(int(j))
    part, jj = (a, int(j)) if j < a.n_traj else (b, int(j) - a.n_traj)
    q = part.record(jj)
    for k in ("start_id", "family_id", "split", "label", "seed", "disasters", "H", "final_hash", "cty_sha256"):
        assert r[k] == q[k], (j, k)
out["records_checked"] = 300

# rows through the loader's batch source: union ids vs part ids
src_u = D._BatchSource(st.path, 1, None, None, True)
src_a = D._BatchSource(a.path, 1, None, None, True)
src_b = D._BatchSource(b.path, 1, None, None, True)
ids = np.concatenate([rng.integers(0, a.n_trans, 200), a.n_trans + rng.integers(0, b.n_trans, 200)])
rng.shuffle(ids)
bu = src_u[ids]
ia, ib = ids < a.n_trans, ids >= a.n_trans
ba, bb = src_a[ids[ia]], src_b[ids[ib] - a.n_trans]
for k in bu:
    if k == "ids":
        continue
    assert np.array_equal(bu[k][ia], ba[k]) and np.array_equal(bu[k][ib], bb[k]), k
out["batch_rows_checked"] = int(ids.size)
assert np.array_equal(st.build_cost[ids][ia], np.asarray(a.build_cost)[ids[ia]])
assert np.array_equal(st.build_cost[ids][ib], np.asarray(b.build_cost)[ids[ib] - a.n_trans])

# the loader itself, with worker processes (fork) reopening the union by path
import torch  # noqa: E402
it = D.OneStepBatches(st, idx, 64, seed=5, device="cpu", num_workers=2)
s0, r, asc, s1 = next(it)
rows = st.obs_row_of(it.last_ids)
ref = D.expand_state_np(st.tiles[rows], st.half[rows], st.power_packed[rows], st.eighth[rows], st.scalars[rows],
                        st.ledger[rows], st.terrain[rows], st.com_rate[rows])
for k in ref:
    assert np.array_equal(s0[k].numpy(), ref[k]), k
draw = np.concatenate([it.last_ids] + [(next(it), it.last_ids.copy())[1] for _ in range(40)])
it.close()
out["loader_batches"] = 41
out["loader_share_from_cov"] = float(np.mean(draw >= a.n_trans))

# BookData.from_cache over the union: rows equal the per-part caches
from dc.train import BookData  # noqa: E402
cache = root / "bk_cache"
sel = np.sort(np.concatenate([rng.integers(0, a.n_trans, 5000), a.n_trans + rng.integers(0, b.n_trans, 5000)]))
t0 = time.time()
bk = BookData.from_cache(st, sel, "cpu", seed=0, cache=cache)
bk_a = BookData.from_cache(a, sel[sel < a.n_trans], "cpu", seed=0, cache=cache)
n_a = int((sel < a.n_trans).sum())
assert torch.equal(bk.raw[:n_a], bk_a.raw) and torch.equal(bk.d[:n_a], bk_a.d) and torch.equal(bk.act[:n_a], bk_a.act)
zc = np.load(cache / "train_cov.npz")
ib_ = sel[sel >= a.n_trans] - a.n_trans
assert np.array_equal(bk.ct[n_a:].numpy(), zc["sc0"][ib_][:, 9].astype(np.float64))
out["bookdata"] = {"rows": int(bk.n), "source": bk.info["source"], "seconds": round(time.time() - t0, 1)}
print(json.dumps(out, indent=1))
