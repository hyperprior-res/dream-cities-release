"""Oracle patching (dc.patching): CPU, a tiny untrained model of the ladder-v2 code with the third stage, the real
engine. The two identity tests of the brief: an empty mask reproduces the audit judge's rollout element for element
under the same seed; the full mask makes every month's state the engine's."""

import dataclasses
import gzip
import importlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from dc import audit as A
from dc import patching as PT
from dc import tasks as T
from dc.engine import SC_FUNDS, SC_POP, SC_TAX, SC_TAX_FUND, SC_POWERED, SC_UNPOWERED, SC_COAL, SC_NUCLEAR
from dc.seeds import seed_for

H = 24
K = PT.K_PATCH
TASKS_V2 = A.REPO / "data" / "tasks_v2_H24.json"


def _ladder_v2_sha():
    return subprocess.run(["git", "-C", str(A.REPO), "rev-parse", "ladder-v2^{commit}"], capture_output=True,
                          text=True).stdout.strip()


@pytest.fixture(scope="module")
def setup(tmp_path_factory):
    sha = _ladder_v2_sha()
    if not sha:
        pytest.skip("tag ladder-v2 not present")
    torch.set_num_threads(4)
    pkg, _ = A.code_package("ladder-v2")
    M = importlib.import_module(pkg.__name__ + ".model")
    cfg = dataclasses.replace(M.SIZES["tiny"], bookkeeping=True, bk_width=32, bk_depth=2)
    torch.manual_seed(0)
    m = M.Emulator(cfg)
    d = tmp_path_factory.mktemp("patch")
    ck = d / "tinybk.pt"
    torch.save({"model_config": m.cfg.to_dict(), "model": m.state_dict(), "ema": None, "samples": 0,
                "git": {"commit": sha, "dirty_code_files": []}}, ck)
    J = A.EmulatorJudge(str(ck), device="cpu", chunk=16, buckets=(16,), compile_trunk=False, model_src="auto")
    insts = A.load_instances(TASKS_V2)
    inst = [i for i in insts if i.task == "recover"][0]          # forced earthquake in month 0
    beh = A.Pools(H).behaviour(inst.start_id)
    P = A.effective(beh[:2], inst.task, H)
    seeds = A.oracle_seed_list(inst, K)
    res = [PT.replay_job((inst.cty, P[0].tobytes(), H, s, "full")) for s in seeds]
    E = PT.engine_state_tensors(res, J._tr, "cpu")
    return {"J": J, "inst": inst, "P": P, "E": E, "res": res, "ck": ck, "dir": d, "sha": sha, "insts": insts}


def test_empty_mask_reproduces_audit_judge(setup):
    """With an empty mask the patched rollout is the audit judge's rollout, element for element, under the judge's
    seed and batch layout: one plan (padded to the judge's 16-row bucket) and two plans (16 rows)."""
    J, inst, P = setup["J"], setup["inst"], setup["P"]
    s0 = J.state0(inst)
    for n, stream in ((1, ("sel", "x", "t1")), (2, ("sel", "x", "t2"))):
        tr = J.samples(inst, P[:n], K, stream)
        seed = seed_for("audit-emu", inst.start_id, *stream)
        out = PT.patched_rollout_batch(J.model, s0, P[:n], [None] * n, [PT.NONE] * n, K, seed=seed, pad_rows=16)
        assert out.scalars.shape == tr.shape
        assert np.array_equal(out.scalars, tr)
        assert out.build_cost is not None and np.isfinite(out.build_cost).all()
    # a different seed gives a different rollout (the comparison above is not vacuous)
    other = PT.patched_rollout(J.model, s0, P[0], None, PT.NONE, K, seed=seed + 1, pad_rows=16)
    assert not np.array_equal(other.scalars[0], tr[0])


def test_full_mask_every_month_is_the_engine(setup):
    J, inst, P, E = setup["J"], setup["inst"], setup["P"], setup["E"]
    out = PT.patched_rollout(J.model, J.state0(inst), P[0], E, PT.FULL, K, seed=1, keep_states=True)
    assert len(out.states) == H + 1
    for t, st in enumerate(out.states):
        Et = PT.engine_at(E, t)
        assert set(st) <= set(Et) and (t == 0 or "build_cost" in st)
        for k, v in st.items():
            assert torch.equal(v, Et[k].to(v.dtype)), (t, k)
    # the recorded trajectory is the engine's scalar trajectory on oracle seeds 0..7
    eng = np.stack([r[0] for r in setup["res"]]).astype(np.float64)
    assert np.array_equal(out.scalars[0], eng)
    assert np.array_equal(out.build_cost[0], np.stack([r[1] for r in setup["res"]]).astype(np.float64))


def test_subsystem_entries_and_controls(setup):
    """Every subsystem overwrites exactly its entries with the engine's at every month; each control overwrites the
    same number of entries per class, month and sample as its subsystem."""
    J, inst, P, E = setup["J"], setup["inst"], setup["P"], setup["E"]
    names = ["power", "treasury", "zone_growth", "traffic", "fire", "power+valves",
             "random~power", "random~traffic", "random~treasury", "random~power+valves",
             "changed~power", "changed~traffic", "changed~treasury", "changed~power+valves"]
    masks = PT.plan_masks(names, (inst.start_id, "test"))
    out = PT.patched_rollout_batch(J.model, J.state0(inst), np.repeat(P[:1], len(masks), 0), [E] * len(masks),
                                   masks, K, seed=2, keep_states=True)
    # changed-matched controls: every overwritten entry differed, and as many changed as the subject's patch changed
    for u, m in enumerate(masks):
        if m.match != "changed":
            continue
        subj = names.index(m.like)
        for c in PT.CLASSES:
            assert np.array_equal(out.changed[u][c], out.counts[u][c]), (m.name, c)
            assert np.array_equal(out.targets[u][c], out.changed[subj][c]), (m.name, c)
            assert np.array_equal(out.changed[u][c], out.targets[u][c]), (m.name, c)
        assert sum(out.changed[u][c].sum() for c in PT.CLASSES) > 0, m.name
    with pytest.raises(ValueError):          # a changed-matched control needs its subject in the same call
        PT.patched_rollout(J.model, J.state0(inst), P[0], E, PT.plan_masks(["changed~power"], ("x",))[0], K)
    for u, m in enumerate(masks):
        if m.match == "changed":
            continue
        r = PT.Resolver(m, "cpu", K)
        for t in range(1, H + 1):
            Et = PT.engine_at(E, t)
            sel = r.at(Et)
            st = {k: v[u * K:(u + 1) * K] for k, v in out.states[t].items()}
            assert sel, m.name
            for k, s in sel.items():
                assert torch.equal(st[k][s], Et[k].to(st[k].dtype)[s]), (m.name, t, k)
            if m.name == "treasury":
                assert set(sel) == {"scalars"} and int(sel["scalars"][0].sum()) == 5
            if m.name == "power":
                assert int(sel["flags"][0].sum()) == 12000 and int(sel["power"][0].sum()) == 12000
            if m.name == "zone_growth":
                code = Et["tile_index"]
                assert torch.equal(sel["tile_index"], (code >= 240) & (code <= 692))
    for u in range(len(masks)):
        for c in PT.CLASSES:
            assert (out.changed[u][c] <= out.counts[u][c]).all()
    assert dict(zip(names, out.changed))["traffic"]["half"].sum() > 0
    by = dict(zip(names, out.counts))
    for s in ("power", "traffic", "treasury", "power+valves"):
        for c in PT.CLASSES:
            assert np.array_equal(by[f"random~{s}"][c], by[s][c]), (s, c)
    assert by["traffic"]["full"].min() > 0 and by["traffic"]["half"].min() == 3000
    assert by["power"]["full"].min() == 24000 and by["power"]["scalar"].min() == 2
    assert dict(zip(names, out.scalar_cols))["treasury"].sum() == 5
    # controls are seeded: the same seed keys give the same draw, other keys another
    a = PT.Resolver(PT.plan_masks(["random~power"], ("a",))[0], "cpu", K).at(PT.engine_at(E, 3))
    b = PT.Resolver(PT.plan_masks(["random~power"], ("a",))[0], "cpu", K).at(PT.engine_at(E, 3))
    c = PT.Resolver(PT.plan_masks(["random~power"], ("b",))[0], "cpu", K).at(PT.engine_at(E, 3))
    assert all(torch.equal(a[k], b[k]) for k in a) and not all(torch.equal(a[k], c[k]) for k in a if k in c)


def test_symmetric_fire_option(setup):
    """The symmetric fire rule (option, off by default): the default masks and their digest are unchanged; fire_sym
    overwrites the union of the engine's and the unit's own fire cells with the engine's tiles (so after the patch the
    state's fire cells are the engine's); its size-matched control takes fire_sym's own counts; its changed-matched
    control changes as many entries as fire_sym changed."""
    J, inst, P, E = setup["J"], setup["inst"], setup["P"], setup["E"]
    base = PT.run_mask_names()
    assert len(base) == 37 and not any("fire_sym" in n for n in base)
    assert PT.masks_digest(base) == "2847153cc569"          # the main checkpoint's stored run tag
    assert PT.run_mask_names(symmetric_fire=True) == base + PT.SYMMETRIC_FIRE_MASKS
    assert not PT.SUBSYSTEMS["fire"].reads_rollout and PT.SYMMETRIC["fire_sym"].reads_rollout
    lo, hi = PT.FIRE_CODES
    # the cell rule on a hand-made state: emulator fire where the engine has none, and engine fire where it has none
    t = 5
    Et = PT.engine_at(E, t)
    cur = {k: v.clone() for k, v in Et.items()}
    eng_fire = (Et["tile_index"] >= lo) & (Et["tile_index"] <= hi)
    free = (~eng_fire.any(0)).nonzero()[:7]
    for x, y in free.tolist():
        cur["tile_index"][:, x, y] = 57
    ef = eng_fire.nonzero()
    if ef.shape[0]:
        k, x, y = ef[0].tolist()
        cur["tile_index"][k, x, y] = 0
    own_fire = (cur["tile_index"] >= lo) & (cur["tile_index"] <= hi)
    rs = PT.Resolver(PT.named_mask("fire_sym"), "cpu", K)
    sel = rs.at(Et, cur)
    assert torch.equal(sel["tile_index"], eng_fire | own_fire)
    assert torch.equal(PT.Resolver(PT.named_mask("fire"), "cpu", K).at(Et)["tile_index"], eng_fire)
    assert bool(sel["eighth"][:, 1].all()) and not bool(sel["eighth"][:, 0].any())
    with pytest.raises(ValueError):
        rs.at(Et)                                                  # the symmetric rule needs the unit's own state
    masks = PT.plan_masks(["fire", "fire_sym", "random~fire_sym", "changed~fire_sym"], (inst.start_id, "sym"))
    U = len(masks)
    s = {k: v.repeat(U, *([1] * (v.dim() - 1))) for k, v in cur.items()}
    cnt = [{c: np.zeros((H, K), dtype=np.int64) for c in PT.CLASSES} for _ in range(U)]
    chg = [{c: np.zeros((H, K), dtype=np.int64) for c in PT.CLASSES} for _ in range(U)]
    tgt = [{c: np.zeros((H, K), dtype=np.int64) for c in PT.CLASSES} for _ in range(U)]
    scl = [np.zeros(20, dtype=bool) for _ in range(U)]
    res = [PT.Resolver(m, "cpu", K) for m in masks]
    out = PT._apply(s, t, [E] * U, res, cnt, scl, K, chg, tgt)
    tile = {n: out["tile_index"][u * K:(u + 1) * K] for u, n in enumerate(["fire", "sym", "rnd", "chg"])}
    assert torch.equal(tile["sym"][eng_fire | own_fire], Et["tile_index"][eng_fire | own_fire])
    assert torch.equal((tile["sym"] >= lo) & (tile["sym"] <= hi), eng_fire)          # no emulator fire remains
    assert bool(((tile["fire"] >= lo) & (tile["fire"] <= hi) & ~eng_fire).any())     # the one-sided rule keeps it
    for c in PT.CLASSES:
        assert np.array_equal(cnt[2][c][t - 1], cnt[1][c][t - 1]), c                   # size from fire_sym's unit
        assert np.array_equal(tgt[3][c][t - 1], chg[1][c][t - 1]), c                   # changed target
    assert np.array_equal(cnt[1]["full"][t - 1], (eng_fire | own_fire).reshape(K, -1).sum(1).numpy())
    assert (chg[1]["full"][t - 1] >= len(free)).all()
    # a size-matched control of fire_sym needs fire_sym in the same call
    with pytest.raises(ValueError):
        PT.patched_rollout(J.model, J.state0(inst), P[0], E, PT.plan_masks(["random~fire_sym"], ("x",))[0], K)
    # in a rollout: after every month's patch the fire_sym unit's fire cells are exactly the engine's; the controls
    # overwrite as many entries per class, month and sample as fire_sym (size) and change as many as it changed
    names = ["none", "fire", "random~fire", "changed~fire"] + list(PT.SYMMETRIC_FIRE_MASKS)
    masks = PT.plan_masks(names, (inst.start_id, "sym2"))
    ro = PT.patched_rollout_batch(J.model, J.state0(inst), np.repeat(P[:1], len(masks), 0), [E] * len(masks), masks,
                                  K, seed=3, keep_states=True)
    u = names.index("fire_sym")
    for t in range(1, H + 1):
        code = ro.states[t]["tile_index"][u * K:(u + 1) * K]
        ec = PT.engine_at(E, t)["tile_index"]
        assert torch.equal((code >= lo) & (code <= hi), (ec >= lo) & (ec <= hi)), t
    by = dict(zip(names, ro.counts))
    bc = dict(zip(names, ro.changed))
    bt = dict(zip(names, ro.targets))
    for c in PT.CLASSES:
        assert np.array_equal(by["random~fire_sym"][c], by["fire_sym"][c]), c
        assert np.array_equal(bt["changed~fire_sym"][c], bc["fire_sym"][c]), c
    assert by["fire_sym"]["eighth"].min() == by["fire"]["eighth"].min() == PT.WORLD_W_8 * PT.WORLD_H_8


def test_symmetric_zone_option(setup):
    """zone_growth_sym (option, off by default): the union of the engine's and the unit's own zone cells, written with
    the engine's tiles, so after every month's patch the state's zone cells are the engine's; its size control takes
    its own unit's counts and its changed control changes as many entries as it changed; defaults unchanged."""
    J, inst, P, E = setup["J"], setup["inst"], setup["P"], setup["E"]
    base = PT.run_mask_names()
    assert PT.masks_digest(base) == "2847153cc569"
    assert PT.run_mask_names(symmetric_zone=True) == base + PT.SYMMETRIC_ZONE_MASKS
    assert PT.run_mask_names(True, True) == base + PT.SYMMETRIC_FIRE_MASKS + PT.SYMMETRIC_ZONE_MASKS
    assert PT.SYMMETRIC["zone_growth_sym"].reads_rollout and not PT.SUBSYSTEMS["zone_growth"].reads_rollout
    lo, hi = PT.ZONE_CODES
    t = 4
    Et = PT.engine_at(E, t)
    cur = {k: v.clone() for k, v in Et.items()}
    eng_zone = (Et["tile_index"] >= lo) & (Et["tile_index"] <= hi)
    free = (~eng_zone.any(0)).nonzero()[:9]
    for x, y in free.tolist():
        cur["tile_index"][:, x, y] = 250                             # an emulator zone tile where the engine has none
    own = (cur["tile_index"] >= lo) & (cur["tile_index"] <= hi)
    sel = PT.Resolver(PT.named_mask("zone_growth_sym"), "cpu", K).at(Et, cur)
    assert set(sel) == {"tile_index"} and torch.equal(sel["tile_index"], eng_zone | own)
    masks = PT.plan_masks(["zone_growth", "zone_growth_sym", "random~zone_growth_sym", "changed~zone_growth_sym"],
                          (inst.start_id, "zsym"))
    U = len(masks)
    s = {k: v.repeat(U, *([1] * (v.dim() - 1))) for k, v in cur.items()}
    cnt = [{c: np.zeros((H, K), dtype=np.int64) for c in PT.CLASSES} for _ in range(U)]
    chg = [{c: np.zeros((H, K), dtype=np.int64) for c in PT.CLASSES} for _ in range(U)]
    tgt = [{c: np.zeros((H, K), dtype=np.int64) for c in PT.CLASSES} for _ in range(U)]
    out = PT._apply(s, t, [E] * U, [PT.Resolver(m, "cpu", K) for m in masks], cnt,
                    [np.zeros(20, dtype=bool) for _ in range(U)], K, chg, tgt)
    one, sym = (out["tile_index"][u * K:(u + 1) * K] for u in (0, 1))
    assert torch.equal((sym >= lo) & (sym <= hi), eng_zone)
    assert bool(((one >= lo) & (one <= hi) & ~eng_zone).any())             # the one-sided rule keeps them
    assert np.array_equal(cnt[1]["full"][t - 1], (eng_zone | own).reshape(K, -1).sum(1).numpy())
    assert (chg[1]["full"][t - 1] >= len(free)).all()
    for c in PT.CLASSES:
        assert np.array_equal(cnt[2][c][t - 1], cnt[1][c][t - 1]) and np.array_equal(tgt[3][c][t - 1], chg[1][c][t - 1])
    with pytest.raises(ValueError):
        PT.patched_rollout(J.model, J.state0(inst), P[0], E, PT.plan_masks(["changed~zone_growth_sym"], ("x",))[0], K)
    names = ["none", "zone_growth"] + list(PT.SYMMETRIC_ZONE_MASKS)
    masks = PT.plan_masks(names, (inst.start_id, "zsym2"))
    ro = PT.patched_rollout_batch(J.model, J.state0(inst), np.repeat(P[:1], len(masks), 0), [E] * len(masks), masks,
                                  K, seed=4, keep_states=True)
    u = names.index("zone_growth_sym")
    for t in range(1, H + 1):
        code = ro.states[t]["tile_index"][u * K:(u + 1) * K]
        ec = PT.engine_at(E, t)["tile_index"]
        assert torch.equal((code >= lo) & (code <= hi), (ec >= lo) & (ec <= hi)), t
    by, bc, bt = (dict(zip(names, x)) for x in (ro.counts, ro.changed, ro.targets))
    for c in PT.CLASSES:
        assert np.array_equal(by["random~zone_growth_sym"][c], by["zone_growth_sym"][c]), c
        assert np.array_equal(bt["changed~zone_growth_sym"][c], bc["zone_growth_sym"][c]), c


def test_balanced_draw_and_true_accept_command(setup, tmp_path):
    """The specificity set's selection (balanced over cities, fixed seed) and a --true-accept --symmetric-fire run
    writing only to its prefix."""
    sys.path.insert(0, str(A.REPO / "code" / "scripts"))
    import run_patching as RP
    recs = [({"cluster": f"c{i % 4}", "plan_id": str(i)}, False, None) for i in range(4 * 10 + 3)]
    d = RP.balanced_draw(recs, 10, 7)
    assert len(d) == 10 and d == RP.balanced_draw(recs, 10, 7) and d != RP.balanced_draw(recs, 10, 8)
    per = Counter(r[0]["cluster"] for r in d)
    assert max(per.values()) - min(per.values()) <= 1 and len(per) == 4
    assert RP.balanced_draw(recs[:5], 10, 7) == recs[:5]
    run = _stub_run(setup, tmp_path)
    recs = A.read_records(run / "records.jsonl.gz")
    recs[1].update(grader_p=1.0, oracle_accept=True, method="cem", budget=1)     # a true acceptance of a primary search
    A.write_records(recs, run / "records.jsonl.gz")
    with pytest.raises(SystemExit):                     # never without a prefix: the default files stay untouched
        RP.main(["--run-dir", str(run), "--device", "cpu", "--workers", "0", "--true-accept", "--masks", "none"])
    with pytest.raises(SystemExit):
        RP.main(["--run-dir", str(run), "--device", "cpu", "--workers", "0", "--true-accept", "--masks", "none",
                 "--out-prefix", "patching"])
    argv = ["--run-dir", str(run), "--device", "cpu", "--workers", "0", "--masks", "none,fire", "--symmetric-fire",
            "--true-accept", "--family", "recover", "--no-identity", "--read-only-cache", "--out-prefix", "ta"]
    RP.main(argv)
    assert not (run / "patching.jsonl.gz").exists() and not (run / "patching_summary.md").exists()
    rows = [json.loads(l) for l in gzip.open(run / "ta.jsonl.gz", "rt")]
    assert {r["mask"] for r in rows} == {"none", "fire"} | set(PT.SYMMETRIC_FIRE_MASKS)
    assert {r["plan_id"] for r in rows} == {recs[1]["plan_id"]} and all(r["set"] == "true_accept" for r in rows)
    assert all(r["flip"] == (r["p"] < 0.5) and not r["primary_set"] for r in rows)
    sel = json.loads((run / "ta_selection.json").read_text())
    assert sel["existing"]["records"] == 1 and sel["analysed"]["records"] == 1
    assert "fire_sym" in (run / "ta_summary.md").read_text()
    # the accepted-but-rejected primary set of one family, under the symmetric masks only
    RP.main(["--run-dir", str(run), "--device", "cpu", "--workers", "0", "--masks", "none", "--symmetric-fire",
             "--symmetric-zone", "--family", "grow,recover", "--primary-only", "--no-identity", "--out-prefix", "abr"])
    rows = [json.loads(l) for l in gzip.open(run / "abr.jsonl.gz", "rt")]
    assert {r["plan_id"] for r in rows} == {recs[0]["plan_id"]} and all(r["set"] == "accepted_but_rejected" for r in rows)
    assert [r["mask"] for r in rows] == ["none"] + list(PT.SYMMETRIC_FIRE_MASKS) + list(PT.SYMMETRIC_ZONE_MASKS)
    assert all(r["kind"] == "local" for r in rows if r["mask"] in PT.SYMMETRIC)
    with pytest.raises(SystemExit):
        RP.main(["--run-dir", str(run), "--device", "cpu", "--workers", "0", "--masks", "none", "--symmetric-zone",
                 "--family", "recover,town", "--out-prefix", "bad"])


def test_predicate_reads():
    exp = {"grow": {SC_POP, SC_FUNDS}, "solvent": {SC_POP, SC_FUNDS}, "treasury": {SC_TAX_FUND, SC_FUNDS, SC_TAX},
           "recover": {SC_POP}, "power": {SC_POWERED, SC_UNPOWERED, SC_COAL, SC_NUCLEAR}}
    for t in T.TASKS:
        assert PT.predicate_reads(t) == exp[t], t


def test_treasury_identity_on_engine(setup):
    """Form B holds at every month of the engine's replays; form A at every month without the yearly budget."""
    res, P = setup["res"], setup["P"]
    sc = np.stack([r[0] for r in res])
    cost = np.stack([r[1] for r in res])
    led = np.stack([r[2] for r in res])
    ti = PT.treasury_identity(sc, cost, led, PT.funding_levels(P[0]))
    assert ti["budget"].any() and (~ti["budget"]).any()
    assert np.all(ti["resid_B"] == 0)
    assert np.all(ti["resid_A"][~ti["budget"]] == 0)
    assert np.all(PT.created_share(sc, ti["resid_B"]) == 0)
    # money created: +500 in one month of a 10,000 treasury is a share of 0.05; destroyed money is negative
    s = np.zeros((2, H + 1, 20))
    s[:, 0, SC_FUNDS] = 10000.0
    r = np.zeros((2, H))
    r[0, 3], r[1, 5] = 500.0, -700.0
    assert np.allclose(PT.created_share(s, r), [0.05, -0.07])


def _stub_run(setup, tmp: Path) -> Path:
    """A finished-run directory with one accepted-but-rejected record (majority oracle) and one other record."""
    inst, P, J = setup["inst"], setup["P"], setup["J"]
    eng = A.EngineJudge(cache_root=tmp / "cache", workers=0)
    tr = A.oracle_trajectories(eng, inst, P, T.ORACLE_N)
    oj = A.oracle_judgement(inst, tr)
    eng.close()
    recs = []
    for r in range(2):
        rec = {"instance": inst.key, "cluster": inst.family_id, "start_id": inst.start_id, "task": inst.task,
               "method": "cem", "scoring": "margin", "budget": 10 ** r, "attacker_seed": 0,
               "plan_id": f"{inst.key}|cem|B{10 ** r}|s0", "grader_p": 1.0 if r == 0 else 0.0,
               "grader_p_fresh": 1.0 if r == 0 else 0.0, "plan_hash": A.plan_hash(P[r])}
        rec.update(A._oracle_fields(oj, r))
        rec["oracle_accept"] = False if r == 0 else rec["oracle_accept"]   # the stub's first plan counts as rejected
        recs.append(rec)
    run = tmp / "run"
    run.mkdir()
    A.write_records(recs, run / "records.jsonl.gz")
    np.savez_compressed(run / "selected_plans.npz", plan_id=np.array([r["plan_id"] for r in recs]),
                        plans=P.astype(np.int16), plans_effective=P.astype(np.int16))
    cfg = {"config": {"tasks_file": str(TASKS_V2), "oracle": "majority", "oracle_seeds": T.ORACLE_N, "H": H},
           "judge": {"ckpt": str(setup["ck"]), "model_src": "auto", "model_src_commit": setup["sha"]},
           "work": str(tmp / "work"), "engine_cache": str(tmp / "cache")}
    (run / "config.json").write_text(json.dumps(cfg))
    return run


def test_skipped_records_and_v2_stop(setup, tmp_path):
    """A record whose stored engine margin the current predicate does not reproduce stops a v2 run before anything is
    patched, and is skipped (and counted) in an older run."""
    sys.path.insert(0, str(A.REPO / "code" / "scripts"))
    import run_patching as RP
    run = _stub_run(setup, tmp_path)
    recs = A.read_records(run / "records.jsonl.gz")
    recs[0]["oracle_margins_seeds"][0] += 1.0
    A.write_records(recs, run / "records.jsonl.gz")
    with pytest.raises(RuntimeError, match="v2 run"):
        RP.main(["--run-dir", str(run), "--device", "cpu", "--workers", "0", "--masks", "none"])
    assert not (run / "patching.jsonl.gz").exists()
    # an older run: the primary-seed oracle and the first thresholds
    cfg = json.loads((run / "config.json").read_text())
    cfg["config"] = {"tasks_file": str(A.TASKS_JSON), "H": H}
    (run / "config.json").write_text(json.dumps(cfg))
    R = RP.Run(run)
    assert not R.v2 and not R.majority
    inst = R.inst[recs[0]["instance"]]
    eng = A.EngineJudge(cache_root=tmp_path / "cache", workers=0)
    good = float(A.task_margin(inst, eng.scalars(inst, setup["P"][:1], A.primary_seed(inst)))[0])
    recs[0].update(oracle_margin=good, oracle_accept=False)
    recs[1].update(grader_p=1.0, oracle_accept=False, oracle_margin=1e6)       # not the plan's margin
    A.write_records(recs, run / "records.jsonl.gz")
    R = RP.Run(run)
    kept, skipped = RP.predicate_check(R, R.analysed(), eng)
    eng.close()
    assert [k[0]["plan_id"] for k in kept] == [recs[0]["plan_id"]]
    assert [s["plan_id"] for s in skipped] == [recs[1]["plan_id"]]


def test_run_patching_command(setup, tmp_path):
    sys.path.insert(0, str(A.REPO / "code" / "scripts"))
    import run_patching as RP
    run = _stub_run(setup, tmp_path)
    argv = ["--run-dir", str(run), "--device", "cpu", "--workers", "0", "--masks",
            "none,treasury,random~treasury,changed~treasury", "--identity-behaviour", "1", "--identity-group", "1"]
    RP.main(argv)
    rows = [json.loads(l) for l in gzip.open(run / "patching.jsonl.gz", "rt")]
    assert len(rows) == 4 and {r["mask"] for r in rows} == {"none", "treasury", "random~treasury", "changed~treasury"}
    ch = [r for r in rows if r["mask"] == "changed~treasury"][0]
    assert ch["target_total_mean"] == [r for r in rows if r["mask"] == "treasury"][0]["changed_total_mean"]
    assert "money created as a share of the starting treasury" in (run / "treasury_identity.md").read_text()
    assert "matched on changed" in (run / "patching_summary.md").read_text()
    tre = [r for r in rows if r["mask"] == "treasury"][0]
    assert tre["direct"] is False            # recover reads population only
    assert len(tre["margins"]) == K and tre["flip"] == (tre["p"] < 0.5)
    assert ch["changed_total_mean"] <= ch["target_total_mean"]
    assert tre["predicate_check_max_abs"] == 0.0
    for f in ("patching_summary.md", "treasury_identity.md"):
        assert (run / f).stat().st_size > 0
    # resumable: a second run recomputes nothing and writes the same rows
    RP.main(argv)
    rows2 = [json.loads(l) for l in gzip.open(run / "patching.jsonl.gz", "rt")]
    assert rows2 == rows
    # by checkpoint, across run directories
    RP.main(["--aggregate", str(run), str(run), "--out", str(tmp_path / "by_checkpoint.md")])
    txt = (tmp_path / "by_checkpoint.md").read_text()
    assert "| treasury |" in txt and "any global" in txt
