"""Oracle patching for one finished audit run (mechanism attribution, study protocol sections 1 and 6).

    PYTHONPATH=code:hpr-dream .venv/bin/python code/scripts/run_patching.py --run-dir <audit output dir> \
        [--device cuda:0] [--workers 4]

Reads the run's ``config.json``, ``records.jsonl.gz`` and ``selected_plans.npz``; writes beside them
``patching.jsonl.gz`` (one row per analysed record and mask), ``patching_summary.md``, ``treasury_identity.md``
and ``patching_costs.json``. Work (one file per patched plan, one per start group of the identity pass) goes to
``<the run's work directory>/patching/<tag>/``; a rerun resumes and recomputes nothing that is there.

Analysed records: the emulator accepts (``grader_p`` >= 0.5, the audit's scored verdict) and the oracle rejects
(``oracle_accept`` False: the 32-seed majority under amendment 3, the primary seed in runs without ``meta.oracle``);
under the majority oracle also, as the secondary set, those that oracle seed 0 alone rejects. Each distinct plan
(start, forced events, effective plan) is patched once with every mask (``dc.patching.run_mask_names``) in one batched
rollout; its records read the verdicts at their own instance's threshold.

Checks made on every patched plan: the full replays' scalar trajectories equal the cached engine judge's on the same
oracle seeds (``dc.audit.oracle_trajectories``); the judge's start state equals the engine's month-0 state; the
record's engine margins are recomputed from those trajectories with this checkout's ``dc.tasks`` (oracle seeds 0..7
under the majority oracle, the primary seed otherwise) and a record whose margins differ is excluded and listed
(the predicate or the thresholds changed since the run).

Specificity controls . ``--symmetric-fire`` adds the
symmetric fire patch and its two controls (``dc.patching.SYMMETRIC_FIRE_MASKS``) to ``--masks all``; ``--family T``
keeps one task family's records; ``--primary-only`` drops the oracle-seed-0 set; ``--true-accept`` analyses instead
the records the emulator and the oracle both accept (``oracle_accept``: the 32-seed majority), of the searches and
budgets that occur in the run's primary set, at most ``--max-records`` of them (a fixed-seed draw balanced over
cities when there are more; the counts go to ``<prefix>_selection.json``); a flip is then the verdict turning from
accept to reject. Each of these needs ``--out-prefix NAME``: the rows, summary, identity report and costs go to
``NAME.jsonl.gz``, ``NAME_summary.md``, ``NAME_treasury_identity.md`` and ``NAME_costs.json`` beside the run, never to
the default files. ``--read-only-cache`` refuses to write to the engine judge's disk cache (a record whose oracle
replays are not cached stops the run before anything is patched).
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
for p in (REPO / "code", REPO / "hpr-dream"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from dc import audit as A                      # noqa: E402
from dc import patching as PT                  # noqa: E402
from dc import tasks as T                      # noqa: E402
from dc.engine import NUM_SCALARS              # noqa: E402
from dc.seeds import seed_for                  # noqa: E402

H = 24
K = PT.K_PATCH


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


# ----------------------------------------------------------------------------------------------
# The run
# ----------------------------------------------------------------------------------------------
class Run:
    def __init__(self, run_dir: Path) -> None:
        self.dir = Path(run_dir)
        self.conf = json.loads((self.dir / "config.json").read_text())
        self.cfg = self.conf.get("config", {})
        self.judge = self.conf.get("judge", {})
        self.H = int(self.cfg.get("H", H))
        if self.H != H:
            raise ValueError(f"horizon {self.H}: only H = {H} is supported")
        self.majority = self.cfg.get("oracle") == "majority"
        self.tasks_file = Path(self.cfg.get("tasks_file") or A.TASKS_JSON)
        self.records = A.read_records(self.dir / "records.jsonl.gz")
        z = np.load(self.dir / "selected_plans.npz")
        self.plan_of = {str(pid): np.asarray(e, dtype=np.int16) for pid, e in zip(z["plan_id"], z["plans_effective"])}
        insts = A.load_instances(self.tasks_file, horizon=self.H)
        self.inst = {i.key: i for i in insts}
        self.work = Path(self.conf.get("work") or (self.dir / "work"))
        self.ckpt = self.judge.get("ckpt")
        self.model_src = self.judge.get("model_src_commit") or self.judge.get("model_src_resolved") or self.judge.get(
            "model_src", "auto")
        self.name = self._name()
        # a v2 run (the amendment-3 tasks: majority oracle, tasks_v2 thresholds) must reproduce every stored margin;
        # an older run's records whose predicate or thresholds changed since are skipped and counted
        self.v2 = bool(self.majority or self.tasks_file.name.startswith("tasks_v2"))

    def _name(self) -> str:
        c = Path(self.ckpt) if self.ckpt else self.dir
        return f"{c.parent.name}/{c.stem}" if self.ckpt else str(self.dir)

    def accepted(self, r) -> bool:
        return float(r["grader_p"]) >= A.ACCEPT_P

    def rejected(self, r) -> bool:
        return not bool(r["oracle_accept"])

    def rejected_seed0(self, r):
        return (not bool(r["oracle_accept_seed0"])) if (self.majority and "oracle_accept_seed0" in r) else None

    def analysed(self):
        out = []
        for r in self.records:
            if not self.accepted(r):
                continue
            prim = self.rejected(r)
            sec = self.rejected_seed0(r)
            if prim or sec:
                out.append((r, bool(prim), sec))
        return out

    def true_accepted(self, family=None):
        """Records the emulator accepts and the oracle accepts (``oracle_accept``), of the (search, budget) pairs that
        occur in the primary set, as (record, False, None) like ``analysed``."""
        pairs = {(r["method"], int(r["budget"])) for r, prim, _ in self.analysed() if prim}
        return [(r, False, None) for r in self.records
                if self.accepted(r) and not self.rejected(r) and (r["method"], int(r["budget"])) in pairs
                and (family is None or self.inst[r["instance"]].task == family)]


def balanced_draw(recs, n: int, seed: int):
    """At most ``n`` records, balanced over cities (``cluster``): records shuffled within each city and cities in a
    shuffled order (one generator, ``seed``), then taken round-robin over cities. All of them if there are n or
    fewer. Returned in input order."""
    if len(recs) <= n:
        return list(recs)
    rng = np.random.default_rng(int(seed))
    by = defaultdict(list)
    for i, r in enumerate(recs):
        by[r[0]["cluster"]].append(i)
    cities = sorted(by)
    for c in cities:
        by[c] = [by[c][j] for j in rng.permutation(len(by[c]))]
    cities = [cities[j] for j in rng.permutation(len(cities))]
    take, depth = [], 0
    while len(take) < n:
        for c in cities:
            if depth < len(by[c]) and len(take) < n:
                take.append(by[c][depth])
        depth += 1
    return [recs[i] for i in sorted(take)]


def plan_key(inst: A.Instance, eff: np.ndarray) -> str:
    return f"{inst.start_id}__{inst.forced_key}__{A.plan_hash(eff)}"


def file_sha(p) -> str:
    return A._sha256_file(p)


# ----------------------------------------------------------------------------------------------
# Engine pool
# ----------------------------------------------------------------------------------------------
class Pool:
    """dc.oracle replays (``dc.patching.replay_job``) in at most ``workers`` processes (0: in this process)."""

    def __init__(self, workers: int) -> None:
        self.workers = int(workers)
        self._p = None
        if self.workers > 0:
            import multiprocessing as mp
            self._p = mp.get_context("spawn").Pool(self.workers)
        self.city_months = 0
        self.seconds = 0.0

    def map_async(self, jobs):
        n = sum(int(j[2]) for j in jobs)
        self.city_months += n
        if self._p is None:
            t0 = time.time()
            res = [PT.replay_job(j) for j in jobs]
            self.seconds += time.time() - t0

            class _R:
                def get(self_inner):
                    return res
            return _R()
        t0 = time.time()
        ar = self._p.map_async(PT.replay_job, jobs, chunksize=1)
        pool = self

        class _W:
            def get(self_inner):
                out = ar.get()
                pool.seconds += time.time() - t0
                return out
        return _W()

    def close(self) -> None:
        if self._p is not None:
            self._p.close()
            self._p.join()
            self._p = None


# ----------------------------------------------------------------------------------------------
# Patching pass
# ----------------------------------------------------------------------------------------------
def patch_tag(run: Run, judge_desc: dict, names) -> dict:
    return {"patching_version": PT.PATCHING_VERSION, "masks": list(names), "masks_digest": PT.masks_digest(names),
            "K": K, "judge": {k: judge_desc.get(k) for k in ("ckpt_sha256", "model_src_commit", "model_py_sha256",
                                                              "decoding", "fast", "device")},
            "patching_py_sha256": file_sha(PT.__file__)}


def patch_plans(run: Run, J, pool: Pool, eng: A.EngineJudge, names, todo, work: Path, tag: dict, device) -> dict:
    """todo: {plan key: (instance, effective plan)}. Returns {plan key: npz path}."""
    out = {}
    keys = sorted(todo)
    pending = {}

    def submit(k):
        inst, eff = todo[k]
        seeds = A.oracle_seed_list(inst, K)
        pending[k] = pool.map_async([(inst.cty, eff.tobytes(), run.H, int(s), "full") for s in seeds])

    need = []
    for k in keys:
        p = work / "plans" / f"{k}.npz"
        if p.exists():
            with np.load(p) as z:
                if str(z["tag"]) == json.dumps(tag, sort_keys=True, default=str):
                    out[k] = p
                    continue
        need.append(k)
    log(f"patching: {len(keys)} distinct plans, {len(keys) - len(need)} done before, {len(need)} to run")
    if need:
        submit(need[0])
    for j, k in enumerate(need):
        inst, eff = todo[k]
        t0 = time.time()
        res = pending.pop(k).get()
        if j + 1 < len(need):
            submit(need[j + 1])                                 # the next plan's replays run beside this rollout
        t_eng = time.time() - t0
        eng_sc = np.stack([r[0] for r in res])
        cached = A.oracle_trajectories(eng, inst, eff[None], K)[0]
        if not np.array_equal(cached, eng_sc):
            raise RuntimeError(f"{k}: full replays differ from the cached engine judge on the oracle seeds")
        E = PT.engine_state_tensors(res, J._tr, device)
        s0 = J.state0(inst)
        for key, v in s0.items():
            if not bool((v[0] == E[key][0, 0].to(v.dtype)).all()):
                raise RuntimeError(f"{k}: the judge's start state differs from the engine's month 0 in {key!r}")
        masks = PT.plan_masks(names, (inst.start_id, inst.forced_key, A.plan_hash(eff)))
        M = len(masks)
        t1 = time.time()
        pr = PT.patched_rollout_batch(J.model, s0, np.repeat(eff[None], M, 0), [E] * M, masks, K,
                                      seed=seed_for("patching-emu", inst.start_id, inst.forced_key, A.plan_hash(eff)))
        if device.type == "cuda":
            import torch
            torch.cuda.synchronize()
        t_emu = time.time() - t1
        cls = list(PT.CLASSES)
        counts = np.stack([np.stack([pr.counts[u][c] for c in cls]) for u in range(M)])       # (M, C, H, K)
        changed = np.stack([np.stack([pr.changed[u][c] for c in cls]) for u in range(M)])     # (M, C, H, K)
        targets = np.stack([np.stack([pr.targets[u][c] for c in cls]) for u in range(M)])     # (M, C, H, K)
        path = work / "plans" / f"{k}.npz"
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.stem + ".tmp.npz")
        np.savez_compressed(
            tmp, tag=json.dumps(tag, sort_keys=True, default=str), masks=np.array([m.name for m in masks]),
            classes=np.array(cls), scalars=pr.scalars, build_cost=pr.build_cost if pr.build_cost is not None else
            np.zeros(0), ledger_none=pr.ledger[names.index("none")] if ("none" in names and pr.ledger is not None)
            else np.zeros(0), counts=counts, changed=changed, targets=targets, scalar_cols=np.stack(pr.scalar_cols),
            eng_scalars=eng_sc, eng_cost=np.stack([r[1] for r in res]), eng_ledger=np.stack([r[2] for r in res]),
            levels=PT.funding_levels(eff), month_steps=pr.month_steps, eng_city_months=K * run.H,
            seconds_emu=t_emu, seconds_eng_wait=t_eng)
        os.replace(tmp, path)
        out[k] = path
        log(f"  [{j + 1}/{len(need)}] {k}: {M} masks x {K} samples, {pr.month_steps} month-steps in {t_emu:.1f} s "
            f"(engine wait {t_eng:.1f} s)")
        del E
    return out


# ----------------------------------------------------------------------------------------------
# Treasury identity pass
# ----------------------------------------------------------------------------------------------
def identity_pass(run: Run, J, pool: Pool, work: Path, tag: dict, n_beh: int, group: int, device,
                  extra_instances=()) -> dict:
    """Emulator rollouts (K = 8, empty mask) and one engine replay each of every distinct selected plan and of the first
    ``n_beh`` behaviour plans of every (start, forced events) group of the run (and of ``extra_instances``). If the
    model revision's sampled state carries no ``build_cost`` (ladder-v1), the emulator side is skipped after the first
    call and only the engine side is kept. -> {group key: npz path}."""
    groups = defaultdict(dict)                    # (start, forced key) -> {plan hash: (kind, effective plan, inst)}
    for r in run.records:
        inst = run.inst.get(r["instance"])
        if inst is None or r["plan_id"] not in run.plan_of:
            continue
        eff = run.plan_of[r["plan_id"]]
        groups[(inst.start_id, inst.forced_key)].setdefault(A.plan_hash(eff), ("selected", eff, inst))
    first_inst = {}
    for inst in extra_instances:
        first_inst.setdefault((inst.start_id, inst.forced_key), inst)
        groups.setdefault((inst.start_id, inst.forced_key), {})
    pools = A.Pools(run.H)
    for (sid, fk), d in list(groups.items()):
        inst = next(v[2] for v in d.values()) if d else first_inst[(sid, fk)]
        if n_beh > 0:
            for e in A.effective(pools.behaviour(sid)[:n_beh], inst.task, run.H):
                h = A.plan_hash(e)
                d[h] = ("selected+behaviour", d[h][1], d[h][2]) if h in d else ("behaviour", e, inst)
    itag = dict(tag, identity={"n_behaviour": n_beh, "group": group})
    itag_s = json.dumps(itag, sort_keys=True, default=str)
    out = {}
    emu_ok = True
    for (sid, fk), d in sorted(groups.items()):
        p = work / "identity" / f"{sid}__{fk}.npz"
        hashes = sorted(d)
        if not hashes:
            continue
        if p.exists():
            with np.load(p) as z:
                if str(z["tag"]) == itag_s and list(z["hashes"]) == hashes:
                    out[(sid, fk)] = p
                    emu_ok = emu_ok and bool(z["emu_available"])
                    continue
        inst = next(v[2] for v in d.values())
        Pe = np.stack([d[h][1] for h in hashes])
        jobs = [(inst.cty, e.tobytes(), run.H, seed_for("patching-identity", sid, fk, h), "scalars")
                for h, e in zip(hashes, Pe)]
        ar = pool.map_async(jobs)
        s0 = J.state0(inst)
        sc, bc, lg = [], [], []
        t0 = time.time()
        ms = 0
        for gi, a in enumerate(range(0, len(hashes), group)):
            if not emu_ok:
                break
            sub = Pe[a:a + group]
            pr = PT.patched_rollout_batch(J.model, s0, sub, [None] * len(sub), [PT.NONE] * len(sub), K,
                                          seed=seed_for("patching-identity-emu", sid, fk, gi), pad_rows=group * K)
            ms += pr.month_steps
            if pr.build_cost is None or pr.ledger is None:
                emu_ok = False
                log("  the model revision's sampled state has no build_cost (or ledger): emulator side of the identity "
                    "skipped, engine side kept")
                break
            sc.append(pr.scalars)
            bc.append(pr.build_cost)
            lg.append(pr.ledger)
        t_emu = time.time() - t0
        res = ar.get()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.stem + ".tmp.npz")
        e0 = np.zeros(0)
        np.savez_compressed(tmp, tag=itag_s, hashes=np.array(hashes), kinds=np.array([d[h][0] for h in hashes]),
                            emu_available=emu_ok, emu_scalars=np.concatenate(sc) if emu_ok else e0,
                            emu_cost=np.concatenate(bc) if emu_ok else e0, emu_ledger=np.concatenate(lg) if emu_ok else e0,
                            levels=np.stack([PT.funding_levels(e) for e in Pe]),
                            eng_scalars=np.stack([r[0] for r in res]), eng_cost=np.stack([r[1] for r in res]),
                            eng_ledger=np.stack([r[2] for r in res]), month_steps=ms, seconds_emu=t_emu)
        os.replace(tmp, p)
        out[(sid, fk)] = p
        log(f"  identity {sid} {fk}: {len(hashes)} plans, {ms} month-steps in {t_emu:.1f} s")
    return out


# ----------------------------------------------------------------------------------------------
# Assembly
# ----------------------------------------------------------------------------------------------
def mask_kind(name: str) -> str:
    if name == "none":
        return "none"
    if name in PT.GLOBAL:
        return "global"
    if name in PT.LOCAL or name in PT.SYMMETRIC or name in PT.OVERLAY_ONLY:
        return "local"
    if name.startswith("random~"):
        return "control, size"
    if name.startswith("changed~"):
        return "control, changed"
    if "+" in name:
        return "pair"
    return "other"


def predicate_check(run: Run, analysed, eng: A.EngineJudge):
    """The record's engine margins recomputed from the cached engine judge's trajectories with this checkout's
    predicate and thresholds: oracle seeds 0..7 under the majority oracle (against ``oracle_margins_seeds``), the
    primary seed otherwise (against ``oracle_margin``). -> (kept [(record, primary, seed0, max |diff|)], excluded)."""
    kept, excluded = [], []
    for r, prim, sec in analysed:
        inst = run.inst[r["instance"]]
        eff = run.plan_of[r["plan_id"]]
        if run.majority:
            tr = A.oracle_trajectories(eng, inst, eff[None], K)[0]
            mine = np.asarray(A.task_margin(inst, tr), dtype=np.float64)
            theirs = np.asarray(r["oracle_margins_seeds"][:K], dtype=np.float64)
        else:
            tr = eng.scalars(inst, eff[None], A.primary_seed(inst))
            mine = np.asarray(A.task_margin(inst, tr), dtype=np.float64).reshape(-1)
            theirs = np.asarray([r["oracle_margin"]], dtype=np.float64)
        dmax = float(np.max(np.abs(mine - theirs)))
        if dmax <= 1e-9:
            kept.append((r, prim, sec, dmax))
        else:
            excluded.append({"plan_id": r["plan_id"], "task": inst.task, "max_abs_margin_difference": dmax})
    return kept, excluded


def assemble(run: Run, kept, plan_files: dict, names, extra=None):
    """``extra``: fields added to every row (only by the specificity-control options)."""
    reads = {t: PT.predicate_reads(t) for t in T.TASKS}
    rows = []
    for r, prim, sec, dmax in kept:
        inst = run.inst[r["instance"]]
        eff = run.plan_of[r["plan_id"]]
        k = plan_key(inst, eff)
        with np.load(plan_files[k]) as z:
            mnames = [str(x) for x in z["masks"]]
            sc = z["scalars"]
            counts = z["counts"]
            changed = z["changed"]
            targets = z["targets"]
            scols = z["scalar_cols"]
            cls = [str(x) for x in z["classes"]]
        base = {"run": run.name, "instance": r["instance"], "cluster": r["cluster"], "start_id": inst.start_id,
                "task": inst.task, "method": r["method"], "scoring": r.get("scoring"), "budget": int(r["budget"]),
                "attacker_seed": int(r.get("attacker_seed", 0)), "plan_id": r["plan_id"], "plan_hash": A.plan_hash(eff),
                "grader_p": float(r["grader_p"]), "grader_p_fresh": r.get("grader_p_fresh"),
                "oracle_accept": bool(r["oracle_accept"]), "oracle_accept_seed0": r.get("oracle_accept_seed0"),
                "oracle_share": r.get("oracle_share"), "primary_set": bool(prim), "seed0_set": sec,
                "oracle_rule": "majority" if run.majority else "primary seed", "predicate_check_max_abs": dmax,
                **(extra or {})}
        for u, mn in enumerate(mnames):
            m = np.asarray(A.task_margin(inst, sc[u]), dtype=np.float64)
            p = float(np.mean(m >= 0))
            cols = set(np.flatnonzero(scols[u]).tolist())
            row = dict(base, mask=mn, kind=mask_kind(mn), direct=bool(cols & reads[inst.task]),
                       margins=[float(x) for x in m], p=p, accept=bool(p >= A.ACCEPT_P), flip=bool(p < A.ACCEPT_P),
                       scalars_overwritten=sorted(int(c) for c in cols))
            for ci, c in enumerate(cls):
                row[f"entries_{c}_mean"] = float(counts[u, ci].mean())
                row[f"changed_{c}_mean"] = float(changed[u, ci].mean())
                row[f"target_{c}_mean"] = float(targets[u, ci].mean())
            row["changed_total_mean"] = float(changed[u].sum(0).mean())
            row["target_total_mean"] = float(targets[u].sum(0).mean())
            rows.append(row)
    return rows


# ----------------------------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------------------------
def _est(flips, clusters):
    from hpr_dream import stats as S
    f = np.asarray(flips, dtype=np.float64)
    if f.size == 0:
        return None
    e = S.conditional_mean(f, None, np.asarray(clusters), n_boot=2000, seed=0, bca=True)
    return e


def _cell(flips, clusters) -> str:
    f = np.asarray(flips, dtype=bool)
    if f.size == 0:
        return "-"
    e = _est(f, clusters)
    iv = (f"[{e.bca_lo:.2f}, {e.bca_hi:.2f}]" if np.isfinite(e.bca_lo) else f"[pct {e.lo:.2f}, {e.hi:.2f}]")
    return f"{int(f.sum())}/{f.size} {e.value:.2f} {iv}"


def summary_tables(rows, set_name: str, names) -> list:
    """Rows of one analysed set -> markdown lines."""
    L = []
    recs = defaultdict(dict)
    for r in rows:
        recs[r["plan_id"]][r["mask"]] = r
    pids = sorted(recs)
    if not pids:
        return [f"No records in this set.", ""]
    meta = {p: next(iter(recs[p].values())) for p in pids}

    def series(mask, sel=None, indirect=False):
        f, c = [], []
        for p in pids:
            if sel is not None and not sel(meta[p]):
                continue
            if mask in ("any global", "any local"):
                group = PT.GLOBAL if mask == "any global" else PT.LOCAL
                ms = [recs[p][g] for g in group if g in recs[p] and (not indirect or not recs[p][g]["direct"])]
                if not ms:
                    continue
                f.append(any(m["flip"] for m in ms))
            else:
                if mask not in recs[p]:
                    continue
                m = recs[p][mask]
                if indirect and m["direct"]:
                    continue
                f.append(m["flip"])
            c.append(meta[p]["cluster"])
        return f, c

    order = [n for n in names] + ["any global", "any local"]
    L += [f"Records: {len(pids)} (distinct plans: {len({meta[p]['plan_hash'] + meta[p]['start_id'] for p in pids})}); "
          f"clusters (held-out families): {len({meta[p]['cluster'] for p in pids})}.", ""]
    L += ["Flip = the patched verdict rejects (fewer than 4 of 8 patched samples satisfy the task). Cells: flips/records, "
          "flip rate, 95 % BCa cluster-bootstrap interval over held-out families (2,000 resamples; 'pct' where BCa is "
          "undefined). Indirect: only the (task, mask) pairs whose predicate reads none of the overwritten entries.", ""]
    L += ["| mask | kind | all plans | indirect only |", "|---|---|---|---|"]
    for n in order:
        fa, ca = series(n)
        fi, ci = series(n, indirect=True)
        L.append(f"| {n} | {mask_kind(n) if n in names else 'derived'} | {_cell(fa, ca)} | {_cell(fi, ci)} |")
    L.append("")
    subjects = [n for n in names if n in PT.SUBSYSTEMS or n in PT.SYMMETRIC or n in PT.OVERLAY_ONLY
                or ("+" in n and mask_kind(n) == "pair")]
    if subjects:
        def mean_changed(mask):
            v = [recs[p][mask]["changed_total_mean"] for p in pids if mask in recs[p]]
            return f"{np.mean(v):.1f}" if v else "-"

        def mean_target(mask):
            v = [recs[p][mask]["target_total_mean"] for p in pids if mask in recs[p]]
            return f"{np.mean(v):.1f}" if v else "-"

        fn, cn = series("none")
        L += ["Each subsystem and pair beside its two controls and the re-drawn rollout ('none', the verdict's own "
              f"noise: {_cell(fn, cn)}). 'chg' = mean entries changed per month and sample (all classes); for the "
              "changed-matched control also its target (the subject's own changed count; fewer are changed only where "
              "fewer entries differ).", ""]
        for indirect in (False, True):
            L += [f"{'Indirect only' if indirect else 'All plans'}:", "",
                  "| subject | patch | chg | matched on size | chg | matched on changed | chg / target |",
                  "|---|---|---|---|---|---|---|"]
            for n in subjects:
                cells = []
                for m in (n, f"random~{n}", f"changed~{n}"):
                    if m in names:
                        f, c = series(m, indirect=indirect)
                        cells.append(_cell(f, c))
                        cells.append(mean_changed(m) + (f" / {mean_target(m)}" if m.startswith("changed~") else ""))
                    else:
                        cells += ["not run", "-"]
                L.append(f"| {n} | " + " | ".join(cells) + " |")
            L.append("")
    for gname, field in (("search method", "method"), ("budget", "budget"), ("task family", "task")):
        vals = sorted({meta[p][field] for p in pids}, key=lambda v: (str(type(v)), v))
        L += [f"By {gname} (all plans; indirect-only counts in the jsonl):", "",
              "| mask | " + " | ".join(str(v) for v in vals) + " |", "|---|" + "---|" * len(vals)]
        for n in order:
            cells = []
            for v in vals:
                f, c = series(n, sel=lambda m, v=v, field=field: m[field] == v)
                cells.append(_cell(f, c))
            L.append(f"| {n} | " + " | ".join(cells) + " |")
        L.append("")
    return L


def decision_inputs(rows) -> list:
    """The inputs of the protocol decision rule, computed mechanically; no label. Since amendment 7 the rule
    reads random search at B = 1,000; the brief's original set (the cross-entropy method) is given beside it."""
    L = []
    for method, title in (("random", "random search, B = 1,000, primary set; the decision set since amendment 7"),
                          ("cem", "cross-entropy method as specified, B = 1,000, primary set; the brief's original set")):
        sel = [r for r in rows if r["primary_set"] and r["method"] == method and r["budget"] == 1000]
        L += [f"## Decision-rule inputs ({title})", ""]
        if not sel:
            L += [f"No {method} B = 1,000 records in this run's primary set.", ""]
            continue
        by = defaultdict(dict)
        for r in sel:
            by[r["plan_id"]][r["mask"]] = r
        pids = sorted(by)
        cl = [next(iter(by[p].values()))["cluster"] for p in pids]
        L += ["| quantity | all plans | indirect only |", "|---|---|---|"]
        for n in ["none"] + list(PT.GLOBAL) + list(PT.LOCAL):
            fa = [by[p][n]["flip"] for p in pids if n in by[p]]
            ca = [c for p, c in zip(pids, cl) if n in by[p]]
            fi = [by[p][n]["flip"] for p in pids if n in by[p] and not by[p][n]["direct"]]
            ci = [c for p, c in zip(pids, cl) if n in by[p] and not by[p][n]["direct"]]
            L.append(f"| {n} | {_cell(fa, ca)} | {_cell(fi, ci)} |")
        for name, group in (("any global", PT.GLOBAL), ("any local", PT.LOCAL)):
            fa = [any(by[p][n]["flip"] for n in group if n in by[p]) for p in pids]
            fi = [any(by[p][n]["flip"] for n in group if n in by[p] and not by[p][n]["direct"]) for p in pids]
            L.append(f"| {name} | {_cell(fa, cl)} | {_cell(fi, cl)} |")
        L += ["", f"Records: {len(pids)}. The protocol decision is made on the main checkpoint over the full "
              "instance set; this table only computes its inputs.", ""]
    return L


def write_summary(run: Run, rows, excluded, names, costs, path: Path, selection=None) -> None:
    """``selection``: None for the default run; otherwise {"title": ..., "lines": [...]} for a run of the
    specificity-control options, whose rows are summarised as one set."""
    L = [f"# Oracle patching: {run.name}", "",
         f"Run directory: `{run.dir}`. Oracle: {'32-seed majority (amendment 3)' if run.majority else 'primary seed (runs without meta.oracle)'}. "
         f"Engine values: oracle seeds 0..{K - 1} (`dc.tasks.oracle_seeds`), patched sample k from seed k. "
         f"Generated by `code/scripts/run_patching.py` (dc.patching v{PT.PATCHING_VERSION}).", ""]
    L += ["## Masks (entries of the emulator's state)", ""] + mask_table_md(rows, names) + [""]
    if selection is not None:
        L += ["## Records", ""] + list(selection["lines"]) + [
            f"Skipped because the record's stored engine margins differ from this checkout's predicate and thresholds: "
            f"{len(excluded)}.", ""]
        L += [f"## {selection['title']}", ""] + summary_tables(rows, "selection", names)
        L += ["## Cost", ""] + [f"- {k}: {v}" for k, v in costs.items()] + [""]
        path.write_text("\n".join(L))
        return
    L += ["## Records", "",
          f"Accepted-but-rejected records analysed: primary set {len({r['plan_id'] for r in rows if r['primary_set']})}"
          + (f", oracle-seed-0 set {len({r['plan_id'] for r in rows if r['seed0_set']})}" if run.majority else "")
          + f". Skipped because the record's stored engine margins differ from this checkout's predicate and thresholds: "
          f"{len(excluded)} (a v2 run stops instead).", ""]
    for e in excluded:
        L.append(f"- excluded `{e['plan_id']}` ({e['task']}): max |margin difference| {e['max_abs_margin_difference']:.6g}")
    L.append("")
    L += [f"## Primary set: emulator accepts, oracle ({'majority' if run.majority else 'primary seed'}) rejects", ""]
    L += summary_tables([r for r in rows if r["primary_set"]], "primary", names)
    if run.majority:
        L += ["## Secondary set: emulator accepts, oracle seed 0 alone rejects", ""]
        L += summary_tables([r for r in rows if r["seed0_set"]], "seed0", names)
    L += decision_inputs(rows)
    L += ["## Goodhart types and matched interventions", "", "Not built yet (study protocol section 6, last item; "
          "`dc.patching.goodhart_type`, `dc.patching.matched_intervention` are placeholders).", ""]
    L += ["## Cost", ""] + [f"- {k}: {v}" for k, v in costs.items()] + [""]
    path.write_text("\n".join(L))


def mask_table_md(rows, names) -> list:
    L = ["Entries per month and sample, means over the analysed records' months 1..24 and 8 samples, as full-resolution "
         "map cells / half-resolution overlay cells / eighth-resolution overlay cells / scalars. Overwritten: entries the "
         "mask sets to the engine's value. Changed: of those, entries whose sampled value differed from the engine's.", "",
         "| mask | kind | entries (state key[channels or columns], cell rule) | overwritten | changed |",
         "|---|---|---|---|---|"]
    for n in names:
        m = PT.plan_masks([n], ("table",))[0]
        if m.like is not None and m.match == "changed":
            desc = (f"random entries among those differing from the engine's, class by class as many as {m.like}'s patch "
                    f"changes that month (seeded per plan)")
        elif m.like is not None:
            desc = f"random entries, class by class the size of {m.like} (seeded per plan)"
        elif m.empty:
            desc = "none (the rollout re-drawn)"
        else:
            parts = []
            for p in m.parts:
                idx = ""
                if p.index is not None:
                    idx = "[" + ",".join(PT.SCALAR_NAMES[i] if p.key == "scalars" else str(i) for i in p.index) + "]"
                cell = f" where engine code in {PT.CELL_RULES[p.cells]}" if p.cells else ""
                parts.append(f"{p.key}{idx}{cell}")
            desc = "; ".join(parts)
        sel = [r for r in rows if r["mask"] == n]
        sz = ch = "-"
        if sel:
            cl = ("full", "half", "eighth", "scalar")
            sz = " / ".join(f"{np.mean([r[f'entries_{c}_mean'] for r in sel]):.0f}" for c in cl)
            ch = " / ".join(f"{np.mean([r[f'changed_{c}_mean'] for r in sel]):.1f}" for c in cl)
        L.append(f"| {n} | {mask_kind(n)} | {desc} | {sz} | {ch} |")
    return L


# ----------------------------------------------------------------------------------------------
# Treasury identity report
# ----------------------------------------------------------------------------------------------
def _resid_stats(rB, bud, unrep, keep_months=None):
    ok = ~unrep if keep_months is None else (~unrep & keep_months)
    r = rB[ok]
    n = int(r.size)
    br = r != 0
    out = {"months": n, "breaches": int(br.sum()), "rate": (float(br.mean()) if n else float("nan"))}
    a = np.abs(r[br])
    out["median_abs"] = float(np.median(a)) if a.size else 0.0
    out["p90_abs"] = float(np.quantile(a, 0.9)) if a.size else 0.0
    return out


def identity_report(run: Run, plan_files: dict, id_files: dict, path: Path) -> dict:
    L = [f"# Treasury identity: {run.name}", "",
         "Form A (protocol): funds[t+1] = funds[t] - build_cost[t] + [budget month t] (tax_fund - road_spend - "
         "fire_spend - police_spend)[t+1]. The budget month is the month whose start city_time is 44 mod 48 (the yearly "
         "collectTax at cityTime % 48 == 0, simulate.cpp:206). Form B (the engine's accounting): in a budget month with "
         "auto-budget on at t+1 the paid amounts sum_i (int)(fund_i x level_i) (ledger road_fund, fire_fund, police_fund "
         "at t+1; the month's funding levels) replace the reported spends (budget.cpp:118-120, 296-306); otherwise A.", ""]
    # engine
    eng_rows = []
    n_patched = n_one = 0
    for p in plan_files.values():
        with np.load(p) as z:
            eng_rows.append((z["eng_scalars"], z["eng_cost"], z["eng_ledger"], np.broadcast_to(z["levels"], (K, H, 3))))
            n_patched += z["eng_scalars"].shape[0]
    for p in id_files.values():
        with np.load(p) as z:
            eng_rows.append((z["eng_scalars"], z["eng_cost"], z["eng_ledger"], z["levels"]))
            n_one += z["eng_scalars"].shape[0]
    out = {}
    if eng_rows:
        sc = np.concatenate([e[0] for e in eng_rows]).astype(np.float64)
        bc = np.concatenate([e[1] for e in eng_rows]).astype(np.float64)
        lg = np.concatenate([e[2] for e in eng_rows]).astype(np.float64)
        lv = np.concatenate([e[3] for e in eng_rows])
        ti = PT.treasury_identity(sc, bc, lg, lv)
        bud, rA, rB = ti["budget"], ti["resid_A"], ti["resid_B"]
        full100 = (lv == 100).all(-1)
        autoon = ti["auto_after"]
        n = rA.size
        L += ["## On engine trajectories", "",
              f"{sc.shape[0]} engine trajectories ({n_patched} of the patched plans on oracle seeds 0..{K - 1}; {n_one} "
              f"selected or behaviour plans of the identity pass on one seed each, `seed_for('patching-identity', start, "
              f"forced events, plan hash)`), {n} months, of which {int(bud.sum())} budget months.", "",
              "| months | n | form A holds | form B holds |", "|---|---|---|---|"]
        for lab, msk in (("all", np.ones_like(bud)), ("not a budget month", ~bud), ("budget month", bud),
                         ("budget, auto-budget on after, all three levels 100", bud & autoon & full100),
                         ("budget, auto-budget on after, some level below 100", bud & autoon & ~full100),
                         ("budget, auto-budget off after", bud & ~autoon)):
            k = int(msk.sum())
            L.append(f"| {lab} | {k} | {int((rA[msk] == 0).sum())} | {int((rB[msk] == 0).sum())} |")
        L.append("")
        out["engine"] = {"months": int(n), "A_holds": int((rA == 0).sum()), "B_holds": int((rB == 0).sum()),
                         "budget_months": int(bud.sum())}
        bad = np.argwhere(rB != 0)
        if bad.size:
            L += [f"Form B fails in {len(bad)} months (first 10: trajectory, month, residual):", ""]
            for i, t in bad[:10]:
                L.append(f"- {i}, {t}, {rB[i, t]:.0f}")
            L.append("")
    # emulator
    L += ["## On the emulator's sampled trajectories (8 samples per plan, empty mask)", "",
          "Breach = residual not 0 (the emulator's scalars are integers in float32; months with |funds| >= 2^24 are left "
          "out and counted). Rates per month; 'any' = share of samples with at least one breach.", ""]
    rec_by_hash = defaultdict(list)
    for r in run.records:
        inst = run.inst.get(r["instance"])
        if inst is None or r["plan_id"] not in run.plan_of:
            continue
        rec_by_hash[(inst.start_id, inst.forced_key, A.plan_hash(run.plan_of[r["plan_id"]]))].append((r, inst))
    groups = defaultdict(lambda: {"rA": [], "rB": [], "bud": [], "unrep": [], "acc": []})
    shares = defaultdict(lambda: {"B": [], "A": [], "ok": [], "cl": []})
    fam_of_start = {i.start_id: i.family_id for i in run.inst.values()}
    n_unavail = 0
    for (sid, fk), p in id_files.items():
        with np.load(p) as z:
            if not bool(z["emu_available"]):
                n_unavail += 1
                continue
            hashes = [str(h) for h in z["hashes"]]
            kinds = [str(k) for k in z["kinds"]]
            ti = PT.treasury_identity(z["emu_scalars"], z["emu_cost"], z["emu_ledger"], z["levels"][:, None])
            sc = z["emu_scalars"]
        shB = PT.created_share(sc, ti["resid_B"])                       # (n, K)
        shA = PT.created_share(sc, ti["resid_A"])
        okm = ~ti["unrepresentable"].any(-1) & np.isfinite(shB)
        for i, (h, kd) in enumerate(zip(hashes, kinds)):
            gk = [("behaviour plans", None)] if "behaviour" in kd else []
            if "selected" in kd:
                for r, inst in rec_by_hash.get((sid, fk, h), []):
                    gk.append((f"selected: {r['method']} B={int(r['budget'])}", (r, inst)))
            for g, ri in gk:
                # behaviour plans belong to no one instance: no predicate, so no "passing" subset
                acc = np.zeros(K, bool) if ri is None else (np.asarray(A.task_margin(ri[1], sc[i])) >= 0)
                G = groups[g]
                G["rA"].append(ti["resid_A"][i]); G["rB"].append(ti["resid_B"][i]); G["bud"].append(ti["budget"][i])
                G["unrep"].append(ti["unrepresentable"][i]); G["acc"].append(acc)
                if ri is None:
                    sk, cl = "behaviour plans", fam_of_start.get(sid, sid)
                else:
                    ok_emu = float(ri[0]["grader_p"]) >= A.ACCEPT_P
                    sk = f"{g}, emulator {'accepts' if ok_emu else 'rejects'}"
                    cl = ri[0]["cluster"]
                S_ = shares[sk]
                S_["B"].append(shB[i]); S_["A"].append(shA[i]); S_["ok"].append(okm[i]); S_["cl"] += [cl] * K
    mat = {}
    if shares:
        lo, mid, hi = PT.MATERIAL_SHARES
        L += ["### The secondary claim's measure (amendment 5): money created as a share of the starting treasury", "",
              "Per trajectory (one of the 8 samples of a plan): the sum over the 24 months of the form-B residual (positive: "
              f"funds rose by more than the accounts allow), divided by the funds at month 0. Breached above {mid:.0%}, "
              f"with {lo:.0%} and {hi:.0%} beside it. Selected plans are split by the audit's verdict on the record "
              "(`grader_p` >= 0.5: the emulator accepts) and counted once per record. Interval: 95 % BCa cluster bootstrap "
              "over held-out families (2,000 resamples). Left out: trajectories with a non-positive starting treasury or a "
              "month with |funds| >= 2^24.", "",
              f"| plans | trajectories | left out | B: > {lo:.0%} | B: > {mid:.0%} | B: > {hi:.0%} | B: mean share | "
              f"A: > {mid:.0%} | A: mean share |", "|---|---|---|---|---|---|---|---|---|"]

        def skey(g):
            if g == "behaviour plans":
                return (0, "", 0, "")
            head, tail = g.split(" B=")
            b, acc = tail.split(", ")
            return (1, head, int(b), acc)

        for g in sorted(shares, key=skey):
            S_ = shares[g]
            B_, A_ = np.concatenate(S_["B"]), np.concatenate(S_["A"])
            ok = np.concatenate(S_["ok"])
            cl = np.asarray(S_["cl"])[ok]
            b, a_ = B_[ok], A_[ok]
            if b.size == 0:
                L.append(f"| {g} | {B_.size} | {int((~ok).sum())} | - | - | - | - | - | - |")
                continue
            cells = [f"{int((b > x).sum())}/{b.size} {np.mean(b > x):.3f}" for x in (lo,)]
            cells.append(_cell(b > mid, cl))
            cells.append(f"{int((b > hi).sum())}/{b.size} {np.mean(b > hi):.3f}")
            L.append(f"| {g} | {B_.size} | {int((~ok).sum())} | " + " | ".join(cells)
                     + f" | {np.mean(b):+.4f} | {int((a_ > mid).sum())}/{a_.size} {np.mean(a_ > mid):.3f} | "
                     f"{np.mean(a_):+.4f} |")
            mat[g] = {"trajectories": int(b.size), "left_out": int((~ok).sum()), "B_gt_1": float(np.mean(b > lo)),
                      "B_gt_5": float(np.mean(b > mid)), "B_gt_10": float(np.mean(b > hi)), "B_mean": float(np.mean(b)),
                      "A_gt_5": float(np.mean(a_ > mid)), "A_mean": float(np.mean(a_))}
        L += ["", "### Per month", ""]
    out["material"] = mat
    L += ["Selected plans are counted once per record (method, search budget); behaviour plans are the first "
          "behaviour-mix plans of each (start, forced events) group.", "",
          "| plans | samples | months | unrepresentable months | A: rate all / yearly-budget / other months | "
          "B: rate all / yearly-budget / other months | B: any | B: median, p90 abs residual | B on samples passing the predicate: rate, any |",
          "|---|---|---|---|---|---|---|---|---|"]
    order = sorted(groups, key=lambda g: (g != "behaviour plans", g.split("B=")[0],
                                         int(g.split("B=")[1]) if "B=" in g else 0))
    emu = {}
    for g in order:
        G = groups[g]
        rA, rB = np.stack(G["rA"]), np.stack(G["rB"])            # (n, K, H)
        bud, unrep, acc = np.stack(G["bud"]), np.stack(G["unrep"]), np.stack(G["acc"])
        sA = [_resid_stats(rA, bud, unrep, m) for m in (None, bud, ~bud)]
        sB = [_resid_stats(rB, bud, unrep, m) for m in (None, bud, ~bud)]
        anyB = float(((rB != 0) & ~unrep).any(-1).mean())
        accm = np.broadcast_to(acc[..., None], rB.shape)
        sBa = _resid_stats(rB, bud, unrep, accm)
        anyBa = float(((rB != 0) & ~unrep).any(-1)[acc].mean()) if acc.any() else float("nan")
        passing = ("n/a (no instance)" if g == "behaviour plans"
                   else f"{sBa['rate']:.3f}, {anyBa:.3f} ({int(acc.sum())} samples)")
        L.append(f"| {g} | {rA.shape[0] * K} | {sB[0]['months']} | {int(unrep.sum())} | "
                 + " / ".join(f"{s['rate']:.3f}" for s in sA) + " | " + " / ".join(f"{s['rate']:.3f}" for s in sB)
                 + f" | {anyB:.3f} | {sB[0]['median_abs']:.0f}, {sB[0]['p90_abs']:.0f} | {passing} |")
        emu[g] = {"samples": int(rA.shape[0] * K), "B_rate": sB[0]["rate"], "A_rate": sA[0]["rate"], "B_any": anyB}
    L.append("")
    if n_unavail:
        L += [f"Not computable on {n_unavail} start groups: the model revision's sampled state carries no build_cost "
              "(ladder-v1 samples the charged cost inside its third stage but does not keep it in the state; ladder-v2 "
              "does), so the identity's build-cost term is unknown on the emulator side.", ""]
    out["emulator"] = emu
    path.write_text("\n".join(L))
    return out


# ----------------------------------------------------------------------------------------------
# Treasury identity on behaviour plans of a checkpoint, without an audit run
# ----------------------------------------------------------------------------------------------
class _BehaviourRun:
    """What ``identity_pass`` / ``identity_report`` read, for behaviour plans only (no records, no audit result)."""

    def __init__(self, ckpt: str, tasks_file: Path, n_inst) -> None:
        self.H = H
        self.records, self.plan_of, self.majority = [], {}, False
        insts = A.load_instances(tasks_file, horizon=H)
        self.inst = {i.key: i for i in insts}
        self.selected = A.select_instances(insts, n_inst)
        c = Path(ckpt)
        self.name = f"{c.parent.name}/{c.stem} (behaviour plans of {len(self.selected)} instances, {tasks_file.name})"


def behaviour_identity(argv) -> None:
    """``--behaviour-identity --checkpoint CKPT --out DIR [--tasks F] [--instances N] [--identity-behaviour n]``: the
    treasury identity on the emulator's and the engine's trajectories of the first n behaviour plans of the
    (start, forced events) groups of ``select_instances(tasks, N)``. Writes DIR/treasury_identity.md."""
    import torch
    ap = argparse.ArgumentParser(description=behaviour_identity.__doc__)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--model-src", default="auto")
    ap.add_argument("--tasks", default=str(REPO / "data" / "tasks_v2_H24.json"))
    ap.add_argument("--instances", type=int, default=10)
    ap.add_argument("--identity-behaviour", type=int, default=25)
    ap.add_argument("--identity-group", type=int, default=16)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", default="")
    a = ap.parse_args(argv)
    dev = torch.device(a.device)
    run = _BehaviourRun(a.checkpoint, Path(a.tasks), a.instances)
    J = A.EmulatorJudge(a.checkpoint, device=a.device, chunk=K, buckets=(K,), compile_trunk=dev.type == "cuda",
                        model_src=a.model_src, fast=True)
    jd = J.describe()
    tag = {"patching_version": PT.PATCHING_VERSION, "mode": "behaviour-identity", "K": K,
           "judge": {k: jd.get(k) for k in ("ckpt_sha256", "model_src_commit", "model_py_sha256", "decoding", "fast")},
           "tasks": str(a.tasks), "instances": [i.key for i in run.selected]}
    digest = hashlib.sha256(json.dumps(tag, sort_keys=True, default=str).encode()).hexdigest()[:10]
    work = Path(a.work) if a.work else A.CACHE_ROOT / "patching_identity" / Path(a.checkpoint).parent.name / digest
    work.mkdir(parents=True, exist_ok=True)
    pool = Pool(a.workers)
    t0 = time.time()
    try:
        files = identity_pass(run, J, pool, work, tag, a.identity_behaviour, a.identity_group, dev,
                              extra_instances=run.selected)
    finally:
        pool.close()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    res = identity_report(run, {}, files, out / "treasury_identity.md")
    ms = 0
    for p in files.values():
        with np.load(p) as z:
            ms += int(z["month_steps"])
    (out / "identity_costs.json").write_text(json.dumps({"identity": res, "emulator_month_steps": ms,
                                                         "seconds": round(time.time() - t0, 1), "work": str(work),
                                                         "tag": tag}, indent=1, default=str))
    log(f"wrote {out / 'treasury_identity.md'} ({ms} emulator month-steps)")


# ----------------------------------------------------------------------------------------------
# Across runs (by checkpoint)
# ----------------------------------------------------------------------------------------------
def aggregate(run_dirs, out: Path) -> None:
    """Flip rates by checkpoint: one column per run directory's ``patching.jsonl.gz`` (primary set, all plans and
    indirect only)."""
    runs = []
    for d in run_dirs:
        p = Path(d) / "patching.jsonl.gz"
        rows = [json.loads(l) for l in gzip.open(p, "rt")]
        runs.append((rows[0]["run"] if rows else str(d), [r for r in rows if r["primary_set"]]))
    names = []
    for _, rows in runs:
        for r in rows:
            if r["mask"] not in names:
                names.append(r["mask"])
    L = ["# Oracle patching by checkpoint (primary sets)", "",
         "Cells: flips/records, flip rate, 95 % BCa cluster-bootstrap interval over held-out families. Runs: "
         + ", ".join(f"`{d}`" for d in run_dirs), ""]
    for indirect in (False, True):
        L += [f"## {'Indirect only' if indirect else 'All plans'}", "",
              "| mask | " + " | ".join(n for n, _ in runs) + " |", "|---|" + "---|" * len(runs)]
        for m in names + ["any global", "any local"]:
            cells = []
            for _, rows in runs:
                by = defaultdict(dict)
                for r in rows:
                    by[r["plan_id"]][r["mask"]] = r
                f, c = [], []
                for pid, d in by.items():
                    if m in ("any global", "any local"):
                        g = [d[x] for x in (PT.GLOBAL if m == "any global" else PT.LOCAL)
                             if x in d and (not indirect or not d[x]["direct"])]
                        if g:
                            f.append(any(x["flip"] for x in g)); c.append(g[0]["cluster"])
                    elif m in d and (not indirect or not d[m]["direct"]):
                        f.append(d[m]["flip"]); c.append(d[m]["cluster"])
                cells.append(_cell(f, c))
            L.append(f"| {m} | " + " | ".join(cells) + " |")
        L.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L))
    log(f"wrote {out}")


# ----------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------
def main(argv=None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == "--aggregate":
        ap = argparse.ArgumentParser(description="flip rates by checkpoint across finished patching runs")
        ap.add_argument("--aggregate", nargs="+", required=True, metavar="RUN_DIR")
        ap.add_argument("--out", default=str(REPO / "results" / "patching" / "by_checkpoint.md"))
        a = ap.parse_args(argv)
        aggregate(a.aggregate, Path(a.out))
        return
    if argv and argv[0] == "--behaviour-identity":
        behaviour_identity(argv[1:])
        return
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--workers", type=int, default=4, help="engine replay processes (at most 4 on the shared machine)")
    ap.add_argument("--masks", default="all", help="comma-separated mask names, or 'all' (dc.patching.run_mask_names)")
    ap.add_argument("--identity-behaviour", type=int, default=25, help="behaviour plans per start group (identity)")
    ap.add_argument("--identity-group", type=int, default=16, help="plans per emulator call in the identity pass")
    ap.add_argument("--no-identity", action="store_true")
    ap.add_argument("--no-fast", action="store_true", help="the compiled trunk without dc.fast (CUDA only)")
    ap.add_argument("--max-plans", type=int, default=0, help="patch at most this many distinct plans (0: all)")
    ap.add_argument("--work", default="", help="default: <the run's work directory>/patching")
    ap.add_argument("--symmetric-fire", action="store_true",
                    help="add the symmetric fire patch and its two controls (dc.patching.SYMMETRIC_FIRE_MASKS)")
    ap.add_argument("--symmetric-zone", action="store_true",
                    help="add the symmetric zone-growth patch and its two controls (dc.patching.SYMMETRIC_ZONE_MASKS)")
    ap.add_argument("--indirect-fire", action="store_true",
                    help="add the overlay-only ('indirect') fire patch and its two controls (dc.patching.INDIRECT_FIRE_MASKS)")
    ap.add_argument("--family", default="", help="analyse these task families' records only (comma-separated)")
    ap.add_argument("--primary-only", action="store_true", help="drop the oracle-seed-0 set (majority oracle runs)")
    ap.add_argument("--true-accept", action="store_true",
                    help="analyse the records the emulator and the oracle both accept (the specificity set)")
    ap.add_argument("--max-records", type=int, default=150, help="--true-accept: at most this many records")
    ap.add_argument("--select-seed", type=int, default=0, help="--true-accept: seed of the balanced draw")
    ap.add_argument("--out-prefix", default="", help="write NAME.jsonl.gz, NAME_summary.md, NAME_costs.json, ...")
    ap.add_argument("--read-only-cache", action="store_true", help="never write to the engine judge's disk cache")
    a = ap.parse_args(argv)
    import torch
    t_start = time.time()
    run = Run(Path(a.run_dir))
    names = list(PT.run_mask_names(a.symmetric_fire, a.symmetric_zone, a.indirect_fire)) if a.masks == "all" else [
        s.strip() for s in a.masks.split(",") if s.strip()]
    if a.symmetric_fire:
        names += [n for n in PT.SYMMETRIC_FIRE_MASKS if n not in names]
    if a.symmetric_zone:
        names += [n for n in PT.SYMMETRIC_ZONE_MASKS if n not in names]
    if a.indirect_fire:
        names += [n for n in PT.INDIRECT_FIRE_MASKS if n not in names]
    PT.plan_masks(names, ("check",))
    opt_names = PT.SYMMETRIC_FIRE_MASKS + PT.SYMMETRIC_ZONE_MASKS + PT.INDIRECT_FIRE_MASKS
    special = bool(a.symmetric_fire or a.symmetric_zone or a.indirect_fire or a.family or a.primary_only or a.true_accept
                   or any(n in opt_names for n in names))
    families = [f.strip() for f in a.family.split(",") if f.strip()]
    pre = a.out_prefix.strip()
    defaults = ("patching.jsonl.gz", "patching_summary.md", "treasury_identity.md", "patching_costs.json")
    outs = ((f"{pre}.jsonl.gz", f"{pre}_summary.md", f"{pre}_treasury_identity.md", f"{pre}_costs.json") if pre
            else defaults)
    if special and not pre:
        raise SystemExit("--symmetric-fire, --symmetric-zone, --indirect-fire, --family, --primary-only and "
                         "--true-accept need --out-prefix (the default output files are never overwritten by them)")
    if pre and (set(outs) & set(defaults) or "/" in pre):
        raise SystemExit(f"--out-prefix {pre!r} would write a default output file or outside the run directory")
    if any(f not in T.TASKS for f in families):
        raise SystemExit(f"unknown task family in {a.family!r}")
    if a.true_accept and len(families) > 1:
        raise SystemExit("--true-accept takes one family")
    dev = torch.device(a.device)
    if dev.type == "cpu":
        torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
    tcode = file_sha(Path(T.__file__))
    if run.cfg.get("tasks_code_sha256") and run.cfg["tasks_code_sha256"] != tcode:
        log(f"note: dc/tasks.py differs from the run's ({run.cfg['tasks_code_sha256'][:8]} -> {tcode[:8]}); every "
            f"record's engine margins are re-checked")
    selection = extra = None
    if a.true_accept:
        pool_ta = run.true_accepted(a.family or None)
        analysed = balanced_draw(pool_ta, a.max_records, seed_for("patching-true-accept", a.select_seed))
        log(f"{run.name}: {len(run.records)} records, {len(pool_ta)} accepted by the emulator and the oracle"
            f"{' (' + a.family + ')' if a.family else ''}; {len(analysed)} analysed")
    else:
        analysed = run.analysed()
        if families:
            analysed = [x for x in analysed if run.inst[x[0]["instance"]].task in families]
        if a.primary_only:
            analysed = [x for x in analysed if x[1]]
        log(f"{run.name}: {len(run.records)} records, {len(analysed)} accepted-but-rejected "
            f"(primary {sum(1 for _, p, _ in analysed if p)}, seed-0 {sum(1 for *_, s in analysed if s)})")
    if special:
        def _counts(xs):
            return {"records": len(xs), "distinct_plans": len({(run.inst[x[0]["instance"]].start_id,
                                                                A.plan_hash(run.plan_of[x[0]["plan_id"]])) for x in xs}),
                    "clusters": len({x[0]["cluster"] for x in xs}),
                    "by_search": dict(sorted(Counter(f"{x[0]['method']} B={int(x[0]['budget'])}"
                                                     for x in xs).items()))}
        kind = "true_accept" if a.true_accept else "accepted_but_rejected"
        extra = {"set": kind}
        sel = {"set": kind, "family": a.family or "all", "primary_only": bool(a.primary_only), "masks": names,
               "analysed": _counts(analysed)}
        if a.true_accept:
            sel.update(existing=_counts(pool_ta), max_records=a.max_records, select_seed=a.select_seed,
                       rule=("emulator accepts (grader_p >= 0.5) and oracle_accept (the run's oracle rule), (method, "
                             "budget) pairs that occur in the primary set; if more than max_records, balanced_draw "
                             "over cities with seed_for('patching-true-accept', select_seed)"))
            sel["note"] = (f"{len(pool_ta)} records exist ({sel['existing']['distinct_plans']} distinct plans, "
                           f"{sel['existing']['clusters']} cities); {len(analysed)} analysed"
                           + (" (all of them)" if len(analysed) == len(pool_ta) else
                              f" (balanced draw of {a.max_records} over cities)") + ".")
            title = (f"True acceptances: emulator accepts, oracle ({'majority' if run.majority else 'primary seed'}) "
                     f"accepts{', ' + a.family if a.family else ''}; flip = accept to reject")
        else:
            sel["note"] = (f"{len(analysed)} accepted-but-rejected records"
                           + (", primary set only" if a.primary_only else "") + (f", {a.family}" if a.family else "")
                           + ".")
            title = (f"Accepted-but-rejected records{', primary set' if a.primary_only else ''}"
                     f"{', ' + a.family if a.family else ''}")
        selection = {"title": title, "lines": [sel["note"], ""], "json": sel}
        (run.dir / f"{pre}_selection.json").write_text(json.dumps(sel, indent=1, default=str))
    for r, _, _ in analysed:
        if A.plan_hash(run.plan_of[r["plan_id"]]) != r.get("plan_hash", A.plan_hash(run.plan_of[r["plan_id"]])):
            raise RuntimeError(f"{r['plan_id']}: stored effective plan does not match the record's plan hash")
    eng = A.EngineJudge(cache_root=run.conf.get("engine_cache") or (A.CACHE_ROOT / "engine_cache"), workers=0)
    if a.read_only_cache:
        def _refuse(*_a, **_k):
            raise RuntimeError("--read-only-cache: an oracle replay missing from the engine judge's disk cache would "
                               "be written; nothing was written")
        eng.cache.put_many = _refuse
    kept, excluded = predicate_check(run, analysed, eng)
    log(f"predicate check: {len(kept)} records kept, {len(excluded)} skipped (stored margin does not match the "
        f"current predicate and thresholds)")
    if excluded and run.v2:
        eng.close()
        raise RuntimeError(
            f"{len(excluded)} record(s) of a v2 run have stored engine margins that the current predicate and "
            f"thresholds do not reproduce; nothing is patched. First: {excluded[:3]}")
    todo = {}
    for r, _, _, _ in kept:
        inst = run.inst[r["instance"]]
        eff = run.plan_of[r["plan_id"]]
        todo.setdefault(plan_key(inst, eff), (inst, eff))
    if a.max_plans:
        keep = sorted(todo)[:a.max_plans]
        todo = {k: todo[k] for k in keep}
        kept = [x for x in kept if plan_key(run.inst[x[0]["instance"]], run.plan_of[x[0]["plan_id"]]) in todo]
    J = A.EmulatorJudge(run.ckpt, device=a.device, chunk=K, buckets=(K,), compile_trunk=dev.type == "cuda",
                        model_src=run.model_src, fast=not a.no_fast)
    jd = J.describe()
    tag = patch_tag(run, jd, names)
    tag_digest = hashlib.sha256(json.dumps(tag, sort_keys=True, default=str).encode()).hexdigest()[:10]
    work = Path(a.work) if a.work else run.work / "patching" / f"v{PT.PATCHING_VERSION}-{tag_digest}"
    work.mkdir(parents=True, exist_ok=True)
    (work / "tag.json").write_text(json.dumps(tag, indent=1, sort_keys=True, default=str))
    log(f"work: {work}; judge {jd.get('model_src_commit', '')[:12]} fast={jd.get('fast')} decoding={jd.get('decoding')}")
    pool = Pool(a.workers)
    try:
        t0 = time.time()
        plan_files = patch_plans(run, J, pool, eng, names, todo, work, tag, dev)
        t_patch = time.time() - t0
        rows = assemble(run, kept, plan_files, names, extra)
        id_files = {}
        t1 = time.time()
        if not a.no_identity:
            id_files = identity_pass(run, J, pool, work, tag, a.identity_behaviour, a.identity_group, dev)
        t_id = time.time() - t1
    finally:
        pool.close()
        ec = eng.counters()
        eng.close()
    # costs from the stored per-plan files (so a resumed run reports the same numbers)
    ms, cm, se = [], [], []
    for p in plan_files.values():
        with np.load(p) as z:
            ms.append(int(z["month_steps"])); cm.append(int(z["eng_city_months"])); se.append(float(z["seconds_emu"]))
    n = len(plan_files)
    costs = {"distinct plans patched": n, "masks per plan": len(names), "samples per mask": K,
             "emulator month-steps per plan": (ms[0] if len(set(ms)) == 1 else f"{np.mean(ms):.0f} (mean)") if ms else 0,
             "engine city-months per plan (full replays)": (cm[0] if cm else 0),
             "emulator seconds per plan (mean, this machine and load)": f"{np.mean(se):.1f}" if se else "-",
             "projection for 100 accepted-but-rejected plans": (
                 f"{100 * int(np.mean(ms)):,} emulator month-steps (about {100 * np.mean(se) / 60:.0f} min at this run's "
                 f"rate) and {100 * (cm[0] if cm else 0):,} engine city-months" if ms else "-"),
             "cached engine judge (cross-checks)": {k: ec[k] for k in ("engine_requests", "engine_cache_hits", "engine_replays")},
             "wall seconds this invocation": {"patching": round(t_patch, 1), "identity": round(t_id, 1),
                                              "total": round(time.time() - t_start, 1)}}
    if special:
        costs["emulator seconds, all plans (sum of the stored per-plan times)"] = round(float(np.sum(se)), 1)
        costs["emulator month-steps, all plans"] = int(np.sum(ms)) if ms else 0
    f_rows, f_sum, f_id, f_cost = (run.dir / o for o in outs)
    out_rows = f_rows
    tmp = out_rows.with_name(out_rows.name + ".tmp")
    with gzip.open(tmp, "wt") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    os.replace(tmp, out_rows)
    write_summary(run, rows, excluded, names, costs, f_sum, selection)
    idout = identity_report(run, plan_files, id_files, f_id) if (plan_files or id_files) else {}
    f_cost.write_text(json.dumps({"costs": costs, "identity": idout, "work": str(work), "tag": tag,
                                  **({"selection": selection["json"]} if selection else {})}, indent=1, default=str))
    log(f"wrote {out_rows} ({len(rows)} rows), {f_sum.name}, {f_id.name}; excluded {len(excluded)}")


if __name__ == "__main__":
    main()
