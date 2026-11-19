"""B20: checks of a coverage store beyond the re-replay (counts from the store files; no engine).

    PYTHONPATH=code .venv/bin/python results/coverage/store_checks.py train_cov2

Engine seeds against every other store; training starts only; disasters flag off; budget columns held within every
trajectory; for a ``listed`` store, each trajectory's setting in its start's list (the recover list for every fifth,
which carries the earthquake in month 0 and no other forced event); style and setting draws; manifest sha256.
Writes results/coverage/store_checks_<name>.json.
"""

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "code" / "scripts"))
from dc import data as D  # noqa: E402
import gen_data as G  # noqa: E402

name = sys.argv[1]
R = D.DATA_ROOT
st = D.TrajStore(R / name)
spec = json.loads((st.path / "gen_config.json").read_text())["spec"]
out = {"store": str(st.path), "trajectories": st.n_traj, "transitions": st.n_trans, "complete": st.complete}
cs = st.traj["seed"].astype(np.int64)
out["seeds_distinct"] = int(len(set(cs.tolist())))
others = [n for n in ("train_full", "train_eval", "heldout_eval", "train_cov", "train_cov2") if n != name and (R / n / "traj.rec").exists()]
out["seed_overlap"] = {n: int(len(set(cs.tolist()) & set(D.TrajStore(R / n).traj["seed"].tolist()))) for n in others}
out["splits"] = sorted(set(np.array(D.SPLITS)[st.traj["split"]].tolist()))
out["heldout_starts_in_table"] = int(sum(s["split"] != "train" for s in st.starts))
out["families"] = int(len(set(st.traj["family_idx"].tolist())))
out["starts_used"] = int(len(set(st.traj["start_idx"].tolist())))
out["disasters_on"] = int(st.traj["disasters"].sum())
H = st.traj["H"].astype(np.int64)
P = np.asarray(st.plan)
held = all((P[a:a + h, 0:4] == P[a, 0:4]).all() for a, h in zip(st.traj["first_trans"].astype(np.int64), H))
out["budget_held_every_trajectory"] = bool(held)
out["labels"] = dict(Counter(st.labels[i] for i in st.traj["label_idx"]))
if spec.get("behaviour") == "listed":
    tab = json.loads(D.resolve_path(spec["settings_file"]).read_text())["starts"]
    quake = G.RealProvider().recover_forced()
    k_every = int(spec["quake_every"])
    bad_setting = bad_forced = 0
    n_quake = 0
    draws = Counter()
    for j in range(st.n_traj):
        a, h = int(st.traj["first_trans"][j]), int(H[j])
        sid = st.starts[int(st.traj["start_idx"][j])]["start_id"]
        q = j % k_every == k_every - 1
        n_quake += q
        s = [int(v) for v in P[a, 0:4]]
        lst = tab[sid]["recover" if q else "settings"]
        bad_setting += s not in lst
        draws[(sid, q, lst.index(s) if s in lst else -1, len(lst))] += 1
        want = np.zeros(h, dtype=np.int64)
        if q:
            for m, kind in quake.items():
                want[m] = kind
        bad_forced += not np.array_equal(P[a:a + h, D.PLAN_FORCED_COL].astype(np.int64), want)
    out["listed"] = {"trajectories_with_forced_quake": int(n_quake), "setting_not_in_start_list": int(bad_setting),
                     "forced_column_wrong": int(bad_forced), "forced": {str(m): k for m, k in quake.items()}}
    # uniformity of the setting draw: position in the list, pooled over starts with lists of the same length
    pos = Counter()
    for (sid, q, i, n), c in draws.items():
        pos[(n, i)] += c
    out["listed"]["setting_position_counts_by_list_length"] = {str(n): [pos[(n, i)] for i in range(n)]
                                                               for n in sorted({n for n, _ in pos})}
    sty = Counter(l.split("/")[1].split("+")[0] for l in (st.labels[i] for i in st.traj["label_idx"]))
    out["listed"]["styles"] = dict(sty)
out["manifest_check"] = D.check_manifest(st, hash_threads=8)
(Path(__file__).resolve().parent / f"store_checks_{name}.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
