"""Heat-map data (figure G2): the engine's own seed-to-seed variation for the plans of figure G1.

For each case of figures/data/gallery_cases.json (the fixed rule of fig_gallery_data.py), replays the plan
on the engine from the instance's start file on oracle seeds 2 to 9 (indices 1..8 of
``dc.tasks.oracle_seeds``) and keeps the month-24 tile map. Seed 1 (index 0) is the map G1 shows and the
reference the error maps are measured against; these eight further seeds give the engine's own floor for
the same measurement (the share of 8 draws whose tile class differs from seed 1's), in the same units as
the emulator's 8 samples. Deterministic (the engine is exact given the seed). CPU only, seconds.

Writes figures/data/heatmap_engine_seeds.npz and figures/data/heatmap_engine_seeds.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "code"), str(REPO / "hpr-dream")]

import numpy as np  # noqa: E402

RUN = REPO / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24"
TASKS = REPO / "data/tasks_v2_H24.json"
OUT = REPO / "figures/data"
N_EXTRA = 8


def main():
    from dc import tasks as T
    from dc.audit import load_instances
    from dc.engine import Engine
    from dc.grammar import compile_plan
    from dc.oracle import replay

    meta = json.loads((OUT / "gallery_cases.json").read_text())
    z = np.load(OUT / "gallery_cases.npz")
    insts = {i.key: i for i in load_instances(TASKS)}
    eng = Engine()
    arrays, rows = {}, []
    for c in meta["cases"]:
        inst = insts[c["instance"]]
        plan = z[f"{c['tag']}_plan"]
        acts, forced = compile_plan(plan)
        seeds = T.oracle_seeds(inst.start_id, inst.task, inst.horizon)
        assert int(seeds[0]) == c["engine_seed_map"]
        tiles, power = [], []
        for s in seeds[1:1 + N_EXTRA]:
            rp = replay(eng, inst.cty, acts, s, forced=forced or None, record="full")
            tiles.append(rp.states[-1].tiles.astype(np.uint16)); power.append(rp.states[-1].power.astype(np.uint8))
        arrays[f"{c['tag']}_eng_seed_tiles"] = np.stack(tiles)
        arrays[f"{c['tag']}_eng_seed_power"] = np.stack(power)
        rows.append({"tag": c["tag"], "instance": c["instance"], "seeds": [int(s) for s in seeds[1:1 + N_EXTRA]]})
    np.savez_compressed(OUT / "heatmap_engine_seeds.npz", **arrays)
    digest = hashlib.sha256(b"".join(np.ascontiguousarray(arrays[k]).tobytes() for k in sorted(arrays))).hexdigest()
    out = {"rule": __doc__.split("\n\n")[1].replace("\n", " "), "n_extra_seeds": N_EXTRA, "cases": rows,
           "inputs": ["figures/data/gallery_cases.json", "figures/data/gallery_cases.npz", str(TASKS.relative_to(REPO))],
           "gallery_arrays_sha256": meta["arrays_sha256"], "arrays_sha256": digest}
    (OUT / "heatmap_engine_seeds.json").write_text(json.dumps(out, indent=1) + "\n")
    print(digest)


if __name__ == "__main__":
    main()
