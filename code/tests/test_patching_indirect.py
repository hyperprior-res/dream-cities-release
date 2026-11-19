"""CPU unit tests for the overlay-only ('indirect') fire-patching mask ``fire_overlay`` and its controls."""

import dataclasses
import gzip
import importlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from dc import audit as A
from dc import patching as PT
from dc import tasks as T

H = 24
K = PT.K_PATCH
TASKS_V2 = A.REPO / "data" / "tasks_v2_H24.json"


def _ladder_v2_sha() -> str:
    return subprocess.run(["git", "-C", str(A.REPO), "rev-parse", "ladder-v2^{commit}"], capture_output=True,
                          text=True).stdout.strip()


@pytest.fixture(scope="module")
def setup(tmp_path_factory):
    sha = _ladder_v2_sha()
    if not sha:
        pytest.skip("tag ladder-v2 not present")
    torch.set_num_threads(2)
    pkg, _ = A.code_package("ladder-v2")
    M = importlib.import_module(pkg.__name__ + ".model")
    cfg = dataclasses.replace(M.SIZES["tiny"], bookkeeping=True, bk_width=32, bk_depth=2)
    torch.manual_seed(0)
    m = M.Emulator(cfg)
    d = tmp_path_factory.mktemp("patch_indirect")
    ck = d / "tinybk.pt"
    torch.save({"model_config": m.cfg.to_dict(), "model": m.state_dict(), "ema": None, "samples": 0,
                "git": {"commit": sha, "dirty_code_files": []}}, ck)
    J = A.EmulatorJudge(str(ck), device="cpu", chunk=16, buckets=(16,), compile_trunk=False, model_src="auto")
    insts = A.load_instances(TASKS_V2)
    inst = [i for i in insts if i.task == "recover"][0]
    beh = A.Pools(H).behaviour(inst.start_id)
    P = A.effective(beh[:2], inst.task, H)
    seeds = A.oracle_seed_list(inst, K)
    res = [PT.replay_job((inst.cty, P[0].tobytes(), H, s, "full")) for s in seeds]
    E = PT.engine_state_tensors(res, J._tr, "cpu")
    return {"J": J, "inst": inst, "P": P, "E": E, "res": res, "ck": ck, "dir": d, "sha": sha}


def test_default_digest_and_mask_wiring():
    base = PT.run_mask_names()
    assert len(base) == 37 and not any("fire_overlay" in n for n in base)
    assert PT.masks_digest(base) == "2847153cc569"
    assert PT.run_mask_names(indirect_fire=True) == base + PT.INDIRECT_FIRE_MASKS
    assert PT.run_mask_names(True, False, True) == base + PT.SYMMETRIC_FIRE_MASKS + PT.INDIRECT_FIRE_MASKS
    m = PT.named_mask("fire_overlay")
    assert not m.reads_rollout and m.parts == (PT.Part("eighth", (1,)),)


def test_fire_overlay_leaves_all_non_fire_cover_entries_untouched(setup):
    """``fire_overlay`` modifies ONLY ``eighth[:, 1]`` (fire coverage) and leaves ``eighth[:, 0]``, ``eighth[:, 2]``,
    ``tile_index`` (even on burning/fire cells!), ``flags``, ``power``, ``half``, ``scalars``, ``ledger``,
    ``terrain``, ``com_rate``, and ``build_cost`` 100% untouched."""
    J, inst, P, E = setup["J"], setup["inst"], setup["P"], setup["E"]
    t = 5
    Et = PT.engine_at(E, t)

    # Construct a state where EVERY key/channel differs from Et, including burning fire tiles on both sides
    cur = {}
    for k, v in Et.items():
        if k == "tile_index":
            cur[k] = (v + 7) % 900
            cur[k][:, 0, :4] = 58                     # synthetic emulator burning tiles
        elif v.dtype == torch.bool:
            cur[k] = ~v
        elif v.is_floating_point():
            cur[k] = v + 13.5
        else:
            cur[k] = v + 3

    rs = PT.Resolver(PT.named_mask("fire_overlay"), "cpu", K)
    sel = rs.at(Et)
    assert set(sel) == {"eighth"}
    assert bool(sel["eighth"][:, 1].all())
    assert not bool(sel["eighth"][:, 0].any()) and not bool(sel["eighth"][:, 2].any())

    masks = PT.plan_masks(["none", "fire_overlay", "random~fire_overlay", "changed~fire_overlay"],
                          (inst.start_id, "ind"))
    U = len(masks)
    s_in = {k: v.repeat(U, *([1] * (v.dim() - 1))).clone() for k, v in cur.items()}
    cnt = [{c: np.zeros((H, K), dtype=np.int64) for c in PT.CLASSES} for _ in range(U)]
    chg = [{c: np.zeros((H, K), dtype=np.int64) for c in PT.CLASSES} for _ in range(U)]
    tgt = [{c: np.zeros((H, K), dtype=np.int64) for c in PT.CLASSES} for _ in range(U)]
    scl = [np.zeros(20, dtype=bool) for _ in range(U)]
    out = PT._apply(s_in, t, [E] * U, [PT.Resolver(m, "cpu", K) for m in masks], cnt, scl, K, chg, tgt)

    # Unit 1 is fire_overlay: rows K..2K
    u = 1
    sl = slice(u * K, (u + 1) * K)
    for k, v in cur.items():
        got = out[k][sl]
        if k == "eighth":
            assert torch.equal(got[:, 1], Et["eighth"][:, 1].to(got.dtype))
            assert torch.equal(got[:, 0], v[:, 0])
            assert torch.equal(got[:, 2], v[:, 2])
        else:
            assert torch.equal(got, v), f"fire_overlay modified {k!r}"

    # Verify counts/changed/targets across all classes for fire_overlay and its matched controls
    n_cells = PT.WORLD_W_8 * PT.WORLD_H_8
    for uu in (1, 2, 3):
        assert not scl[uu].any()
        for c in ("scalar", "full", "half"):
            assert (cnt[uu][c][t - 1] == 0).all()
            assert (chg[uu][c][t - 1] == 0).all()
            assert (tgt[uu][c][t - 1] == 0).all()
    assert (cnt[1]["eighth"][t - 1] == n_cells).all()
    assert (chg[1]["eighth"][t - 1] == n_cells).all()
    assert np.array_equal(cnt[2]["eighth"][t - 1], cnt[1]["eighth"][t - 1])
    assert np.array_equal(tgt[3]["eighth"][t - 1], chg[1]["eighth"][t - 1])
    assert np.array_equal(chg[3]["eighth"][t - 1], tgt[3]["eighth"][t - 1])

    # Controls of fire_overlay also leave tile_index, flags, power, half, scalars 100% untouched
    for uu in (2, 3):
        sl_c = slice(uu * K, (uu + 1) * K)
        for k in ("tile_index", "flags", "power", "half", "scalars", "ledger", "terrain", "com_rate", "build_cost"):
            if k in cur:
                assert torch.equal(out[k][sl_c], cur[k]), (masks[uu].name, k)

    # Full rollout check
    ro = PT.patched_rollout_batch(J.model, J.state0(inst), np.repeat(P[:1], U, 0), [E] * U, masks, K, seed=11,
                                  keep_states=True)
    by, bc, bt = (dict(zip([m.name for m in masks], x)) for x in (ro.counts, ro.changed, ro.targets))
    for name in PT.INDIRECT_FIRE_MASKS:
        for c in ("scalar", "full", "half"):
            assert (by[name][c] == 0).all() and (bc[name][c] == 0).all()
    assert (by["fire_overlay"]["eighth"] == n_cells).all()
    assert np.array_equal(by["random~fire_overlay"]["eighth"], by["fire_overlay"]["eighth"])
    assert np.array_equal(bt["changed~fire_overlay"]["eighth"], bc["fire_overlay"]["eighth"])
    for m_step in range(1, H + 1):
        eg = ro.states[m_step]["eighth"][K:2 * K, 1]
        assert torch.equal(eg, PT.engine_at(E, m_step)["eighth"][:, 1].to(eg.dtype))


def test_run_patching_indirect_fire_cli(setup, tmp_path):
    """``run_patching.py --indirect-fire`` enforces ``--out-prefix`` and produces ABR and true-accept files without
    touching default outputs."""
    sys.path.insert(0, str(A.REPO / "code" / "scripts"))
    import run_patching as RP

    inst, P = setup["inst"], setup["P"]
    eng = A.EngineJudge(cache_root=tmp_path / "cache", workers=0)
    tr = A.oracle_trajectories(eng, inst, P, T.ORACLE_N)
    oj = A.oracle_judgement(inst, tr)
    eng.close()
    recs = []
    for r in range(2):
        rec = {"instance": inst.key, "cluster": inst.family_id, "start_id": inst.start_id, "task": inst.task,
               "method": "cem", "scoring": "margin", "budget": 1, "attacker_seed": r,
               "plan_id": f"{inst.key}|cem|B1|s{r}", "grader_p": 1.0, "grader_p_fresh": 1.0,
               "plan_hash": A.plan_hash(P[r])}
        rec.update(A._oracle_fields(oj, r))
        rec["oracle_accept"] = (r == 1)                # r=0 is ABR, r=1 is true_accept
        recs.append(rec)
    run = tmp_path / "run"
    run.mkdir()
    A.write_records(recs, run / "records.jsonl.gz")
    np.savez_compressed(run / "selected_plans.npz", plan_id=np.array([r["plan_id"] for r in recs]),
                        plans=P.astype(np.int16), plans_effective=P.astype(np.int16))
    cfg = {"config": {"tasks_file": str(TASKS_V2), "oracle": "majority", "oracle_seeds": T.ORACLE_N, "H": H},
           "judge": {"ckpt": str(setup["ck"]), "model_src": "auto", "model_src_commit": setup["sha"]},
           "work": str(tmp_path / "work"), "engine_cache": str(tmp_path / "cache")}
    (run / "config.json").write_text(json.dumps(cfg))

    with pytest.raises(SystemExit):
        RP.main(["--run-dir", str(run), "--device", "cpu", "--workers", "0", "--masks", "none", "--indirect-fire"])

    RP.main(["--run-dir", str(run), "--device", "cpu", "--workers", "0", "--masks", "none", "--indirect-fire",
             "--family", "recover", "--primary-only", "--no-identity",
             "--out-prefix", "patching_controls_indirect_recover"])
    RP.main(["--run-dir", str(run), "--device", "cpu", "--workers", "0", "--masks", "none", "--indirect-fire",
             "--true-accept", "--family", "recover", "--no-identity",
             "--out-prefix", "patching_controls_indirect_true_accept_recover"])

    assert not (run / "patching.jsonl.gz").exists()
    for pre, expected_set, expected_pid in (
        ("patching_controls_indirect_recover", "accepted_but_rejected", recs[0]["plan_id"]),
        ("patching_controls_indirect_true_accept_recover", "true_accept", recs[1]["plan_id"]),
    ):
        rows = [json.loads(l) for l in gzip.open(run / f"{pre}.jsonl.gz", "rt")]
        assert [r["mask"] for r in rows] == ["none"] + list(PT.INDIRECT_FIRE_MASKS)
        assert {r["plan_id"] for r in rows} == {expected_pid}
        assert all(r["set"] == expected_set for r in rows)
        fo = [r for r in rows if r["mask"] == "fire_overlay"][0]
        assert fo["kind"] == "local" and fo["direct"] is False
        assert fo["entries_full_mean"] == 0.0 and fo["entries_half_mean"] == 0.0 and fo["entries_scalar_mean"] == 0.0
        assert fo["entries_eighth_mean"] == float(PT.WORLD_W_8 * PT.WORLD_H_8)
        assert "fire_overlay" in (run / f"{pre}_summary.md").read_text()
