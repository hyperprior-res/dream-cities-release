#!/usr/bin/env python3
"""Thresholds v2: engine-only do-nothing and engine-search frontiers per task instance .

One command per horizon; resumable (every stage of every instance is saved as it completes and skipped
when its file exists). Engine only: every trajectory comes from ``dc.oracle.replay`` through
``dc.audit.EngineJudge`` (on-disk cache, local process pool, optionally host-b's pool), except the
closed-loop builder rollouts of source c, which are ``dc.behaviour.rollout_behaviour`` on a local
``dc.engine.Engine`` exactly as ``code/scripts/gen_builder_pool.py`` produces the builder pool.

Stages per instance (start, variant; ``dc.frontier.VARIANTS``):

  const      the 2,625 constant plans on the primary seed; the 20 best by J on the eight secondary seeds
  pools      source a: the behaviour pool (1,000) and the builder pool (1,000, H = 24 only) on the primary seed
  overwrite  source b: the same plans with their tax and funding columns set to each of the three best
             constant settings (constant plans ranked by J on the primary seed)
  closed     source c (H = 24 only): scripted builders played closed loop under each of the two best
             constant settings, 500 plans per setting, then replayed on the primary seed
  cem        source d: the cross-entropy method on the engine (primary seed, score J), one run initialised
             from the behaviour pool's column marginals and one from the builder pool's (H = 24), tax and
             funding columns centred on the best constant setting; the large run (10 x 1,000 at H = 24,
             5 x 1,000 otherwise) plus runs at budgets 10, 100, 1,000 for the budget table; each run's
             selected plan replayed on the eight secondary seeds
  final      the 50 best by J of each source, replayed on the eight secondary seeds; the rule
  constfull  (optional) the whole constant grid on the eight secondary seeds

Usage:
  python code/scripts/task_frontier.py run --horizon 24 --shard 0/3 --workers 4 --remote host-b --remote-workers 8
  python code/scripts/task_frontier.py assemble --horizon 24
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "hpr-dream"))

import hpr_dream as hd  # noqa: E402
from dc import audit as A  # noqa: E402
from dc import frontier as F  # noqa: E402
from dc import tasks as T  # noqa: E402
from dc.engine import PROTO_VERSION  # noqa: E402
from dc.families import heldout_cty_of  # noqa: E402
from dc.grammar import N_COLS  # noqa: E402
from dc.seeds import seed_for  # noqa: E402

CACHE = Path(os.environ.get("WM2_TASKS_V2_CACHE", "<cache>/tasks_v2"))
STAGES = ("const", "pools", "overwrite", "closed", "cem", "final")
OPTIONAL_STAGES = ("constfull", "oracle")
N_ORACLE_SUBSET = 100            # plans per source (behaviour, builders, b, c) replayed on the oracle seeds
N_OVERWRITE = 3
N_CLOSED_SETTINGS = 2
N_CLOSED_PER_SETTING = 500
SMALL_BUDGETS = (10, 100, 1000)


def big_schedule(H: int):
    return (10, 1000) if H == 24 else (5, 1000)


def utc() -> str:
    return dt.datetime.utcnow().strftime("%H:%M:%SZ")


def work_dir(H: int) -> Path:
    return CACHE / f"H{H}" / "work"


def inst_dir(H: int, inst: A.Instance, variant: str) -> Path:
    return work_dir(H) / f"{inst.start_id}__{variant}"


def save_npz(path: Path, **arrays) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.stem + ".tmp.npz")
    np.savez_compressed(tmp, **arrays)
    os.replace(tmp, path)


def load_npz(path: Path) -> Dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def jdump(obj) -> np.ndarray:
    return np.array(json.dumps(obj, default=float))


def jload(a) -> dict:
    return json.loads(str(a))


class Counts:
    """Judge counter deltas of one stage."""

    def __init__(self, judge: A.EngineJudge) -> None:
        self.judge = judge
        self.c0 = dict(judge.counters())
        self.t0 = time.time()

    def done(self, **extra) -> dict:
        c1 = self.judge.counters()
        d = {k: c1[k] - self.c0[k] for k in c1}
        d["wall_seconds"] = round(time.time() - self.t0, 2)
        d.update(extra)
        return d


def stat_feas_J(variant: str, scal: np.ndarray):
    """(statistic, feasible, J, slack) of trajectories (..., H+1, 20)."""
    return F.statistic(variant, scal), F.feasible(variant, scal), F.J(variant, scal), F.slack(variant, scal)


def pool_plans(pools: A.Pools, start_id: str, H: int):
    """Raw plans of source a: behaviour pool, then builder pool where one exists (H = 24)."""
    beh = np.asarray(pools.behaviour(start_id))
    try:
        bld = np.asarray(pools.builders(start_id))
    except FileNotFoundError:
        bld = np.zeros((0, H, N_COLS), dtype=np.int16)
    return beh, bld


# ----------------------------------------------------------------------------------------------
# Stages
# ----------------------------------------------------------------------------------------------
class Runner:
    def __init__(self, H: int, judge: A.EngineJudge, pools: A.Pools, local_workers: int, log) -> None:
        self.H, self.judge, self.pools, self.log = H, judge, pools, log
        self.local_workers = local_workers
        self._cl_pool = None
        self.space = A.plan_space(H)

    def close(self):
        if self._cl_pool is not None:
            self._cl_pool.close()
            self._cl_pool.join()
            self._cl_pool = None

    def cl_pool(self):
        if self._cl_pool is None:
            self._cl_pool = mp.get_context("spawn").Pool(max(1, self.local_workers))
        return self._cl_pool

    # -- helpers --------------------------------------------------------------------------------
    def replay(self, inst, raw, seeds) -> np.ndarray:
        eff = A.effective(raw, inst.task, self.H)
        return self.judge.scalars(inst, eff, seeds)

    def const_ranking(self, inst, variant) -> np.ndarray:
        d = load_npz(inst_dir(self.H, inst, variant) / "const.npz")
        return d["top"]

    # -- const ------------------------------------------------------------------------------------
    def stage_const(self, inst, variant, path):
        cnt = Counts(self.judge)
        H = self.H
        P = F.constant_plans(H)
        scal = self.replay(inst, P, A.primary_seed(inst))
        st, ok, Jp, sl = stat_feas_J(variant, scal)
        top = F.top_k(Jp, F.N_CONST_TOP, sl)
        sec = A.secondary_seeds(inst)
        s2 = self.replay(inst, np.repeat(P[top], len(sec), axis=0), np.tile(sec, len(top)))
        s2 = s2.reshape(len(top), len(sec), H + 1, -1)
        save_npz(path, scal=scal, J=Jp, slack=sl, top=top, sec_scal=s2, grid=F.GRID,
                 counts=jdump(cnt.done(plans=int(P.shape[0]), secondary_replays=int(len(top) * len(sec)))))

    # -- a ----------------------------------------------------------------------------------------
    def stage_pools(self, inst, variant, path):
        cnt = Counts(self.judge)
        beh, bld = pool_plans(self.pools, inst.start_id, self.H)
        raw = np.concatenate([beh, bld])
        scal = self.replay(inst, raw, A.primary_seed(inst))
        st, ok, Jp, sl = stat_feas_J(variant, scal)
        save_npz(path, stat=st, feas=ok, J=Jp, slack=sl, n_beh=np.int64(len(beh)), n_bld=np.int64(len(bld)),
                 counts=jdump(cnt.done(plans=int(len(raw)))))

    # -- b ----------------------------------------------------------------------------------------
    def stage_overwrite(self, inst, variant, path):
        cnt = Counts(self.judge)
        beh, bld = pool_plans(self.pools, inst.start_id, self.H)
        raw = np.concatenate([beh, bld])
        top = self.const_ranking(inst, variant)[:N_OVERWRITE]
        settings = F.GRID[top]
        sts, oks, Js, sls = [], [], [], []
        for s in settings:
            scal = self.replay(inst, F.overwrite_budget(raw, s), A.primary_seed(inst))
            st, ok, Jp, sl = stat_feas_J(variant, scal)
            sts.append(st), oks.append(ok), Js.append(Jp), sls.append(sl)
        save_npz(path, settings=settings, stat=np.stack(sts), feas=np.stack(oks), J=np.stack(Js), slack=np.stack(sls),
                 n_beh=np.int64(len(beh)), n_bld=np.int64(len(bld)),
                 counts=jdump(cnt.done(plans=int(len(raw) * len(settings)))))

    # -- c ----------------------------------------------------------------------------------------
    def closed_plans(self, inst, setting) -> tuple:
        """Source c's plans for (start, forced events, setting), shared by tasks with equal forced events."""
        H = self.H
        s = "-".join(str(int(v)) for v in setting)
        p = work_dir(H) / "closed" / f"{inst.start_id}__{inst.forced_key}__{s}.npz"
        if p.exists():
            d = load_npz(p)
            return d["plans"].astype(np.int16), d["labels"], 0
        jobs = [(inst.start_id, inst.cty, H, tuple(int(v) for v in setting), dict(inst.forced), inst.forced_key, j)
                for j in range(N_CLOSED_PER_SETTING)]
        res = self.cl_pool().map(F.closed_loop_job, jobs, chunksize=max(1, len(jobs) // (4 * max(1, self.local_workers))))
        plans = np.stack([np.frombuffer(b, dtype=np.int16).reshape(H, N_COLS) for b, _ in res])
        labels = np.array([l for _, l in res])
        save_npz(p, plans=plans.astype(np.uint8), labels=labels, setting=np.asarray(setting),
                 seeds=jdump({"policy": "seed_for('tv2-c-policy', start, H, forced_key, 't-r-f-p', j)",
                              "closed_loop": "seed_for('tv2-c-gen', start, H, forced_key, 't-r-f-p', j)"}))
        return plans, labels, len(jobs)

    def stage_closed(self, inst, variant, path):
        cnt = Counts(self.judge)
        top = self.const_ranking(inst, variant)[:N_CLOSED_SETTINGS]
        settings = F.GRID[top]
        allp, labs, sts, oks, Js, sls, n_roll = [], [], [], [], [], [], 0
        for s in settings:
            plans, labels, n_new = self.closed_plans(inst, s)
            n_roll += n_new
            scal = self.replay(inst, plans, A.primary_seed(inst))
            st, ok, Jp, sl = stat_feas_J(variant, scal)
            allp.append(plans), labs.append(labels), sts.append(st), oks.append(ok), Js.append(Jp), sls.append(sl)
        save_npz(path, settings=settings, plans=np.stack(allp).astype(np.uint8), labels=np.stack(labs),
                 stat=np.stack(sts), feas=np.stack(oks), J=np.stack(Js), slack=np.stack(sls),
                 counts=jdump(cnt.done(plans=int(sum(len(p) for p in allp)), closed_loop_rollouts_run=n_roll)))

    # -- d ----------------------------------------------------------------------------------------
    def stage_cem(self, inst, variant, path):
        cnt = Counts(self.judge)
        H = self.H
        beh, bld = pool_plans(self.pools, inst.start_id, H)
        setting = F.GRID[self.const_ranking(inst, variant)[0]]
        inits = [("behaviour", beh)] + ([("builders", bld)] if len(bld) else [])
        G, N = big_schedule(H)
        budgets = list(SMALL_BUDGETS) + [G * N]
        prim, sec = A.primary_seed(inst), A.secondary_seeds(inst)
        logs = {}
        sel_plans = np.zeros((len(inits), len(budgets), H, N_COLS), dtype=np.int16)
        sel_J = np.zeros((len(inits), len(budgets)))
        big_plans = np.zeros((len(inits), G * N, H * N_COLS), dtype=np.uint8)
        big_J = np.zeros((len(inits), G * N))
        big_stat = np.zeros((len(inits), G * N))
        big_feas = np.zeros((len(inits), G * N), dtype=bool)
        big_slack = np.zeros((len(inits), G * N))
        for ii, (name, pool) in enumerate(inits):
            init = F.centred_init(self.space, pool.reshape(len(pool), -1).astype(np.int64), setting, H)
            for bi, B in enumerate(budgets):
                rec = {"X": [], "J": [], "stat": [], "feas": [], "slack": []}

                def score(X, rec=rec):
                    scal = self.replay(inst, X, prim)
                    st, ok, Jp, sl = stat_feas_J(variant, scal)
                    rec["X"].append(np.asarray(X).astype(np.uint8)), rec["J"].append(Jp)
                    rec["stat"].append(st), rec["feas"].append(ok), rec["slack"].append(sl)
                    return Jp

                rng = np.random.default_rng(seed_for("tv2-cem", inst.start_id, variant, H, name, B))
                sched = (G, N) if B == G * N else None
                sel = hd.cem(score, self.space, B, rng, init, schedule=sched)
                assert sel.log["n_scored"] == B
                sel_plans[ii, bi] = A.effective(sel.plan, inst.task, H)[0]
                sel_J[ii, bi] = sel.log["best_score"]
                logs[f"{name}/{B}"] = sel.log
                if B == G * N:
                    big_plans[ii] = np.concatenate(rec["X"])
                    big_J[ii] = np.concatenate(rec["J"])
                    big_stat[ii] = np.concatenate(rec["stat"])
                    big_feas[ii] = np.concatenate(rec["feas"])
                    big_slack[ii] = np.concatenate(rec["slack"])
        # selected plans on the eight secondary seeds
        flat = sel_plans.reshape(-1, H, N_COLS)
        s2 = self.judge.scalars(inst, np.repeat(flat, len(sec), axis=0), np.tile(sec, len(flat)))
        s2 = s2.reshape(len(inits), len(budgets), len(sec), H + 1, -1)
        s1 = self.judge.scalars(inst, flat, prim).reshape(len(inits), len(budgets), H + 1, -1)
        save_npz(path, inits=np.array([n for n, _ in inits]), budgets=np.array(budgets), setting=setting,
                 sel_plans=sel_plans, sel_J=sel_J, sel_scal_primary=s1, sel_scal_secondary=s2,
                 big_plans=big_plans, big_J=big_J, big_stat=big_stat, big_feas=big_feas, big_slack=big_slack,
                 logs=jdump(logs),
                 counts=jdump(cnt.done(plans_scored=int(len(inits) * sum(budgets)),
                                       schedule_big=[G, N], budgets=budgets)))

    # -- finalists and the rule -------------------------------------------------------------------
    def candidates(self, inst, variant):
        """(source name, raw plans (n, H, 25), J (n,), slack (n,)) for the four sources (a..d) present."""
        H = self.H
        d = inst_dir(H, inst, variant)
        beh, bld = pool_plans(self.pools, inst.start_id, H)
        raw_a = np.concatenate([beh, bld])
        po = load_npz(d / "pools.npz")
        out = [("a", raw_a, po["J"], po["slack"])]
        ov = load_npz(d / "overwrite.npz")
        raw_b = np.concatenate([F.overwrite_budget(raw_a, s) for s in ov["settings"]])
        out.append(("b", raw_b, ov["J"].reshape(-1), ov["slack"].reshape(-1)))
        if (d / "closed.npz").exists():
            cl = load_npz(d / "closed.npz")
            out.append(("c", cl["plans"].astype(np.int16).reshape(-1, H, N_COLS), cl["J"].reshape(-1), cl["slack"].reshape(-1)))
        cm = load_npz(d / "cem.npz")
        out.append(("d", cm["big_plans"].astype(np.int16).reshape(-1, H, N_COLS), cm["big_J"].reshape(-1),
                    cm["big_slack"].reshape(-1)))
        return out

    def stage_final(self, inst, variant, path):
        cnt = Counts(self.judge)
        H = self.H
        seeds9 = A.verdict_seeds(inst)
        rows, src_bits, src_first, Jp_list, keys = [], [], [], [], {}
        names = []
        for si, (name, raw, Jv, slv) in enumerate(self.candidates(inst, variant)):
            names.append(name)
            idx = F.top_k(Jv, F.N_FINALISTS, slv)
            eff = A.effective(raw[idx], inst.task, H)
            for r, j in zip(eff, idx):
                k = r.tobytes()
                if k in keys:
                    src_bits[keys[k]] |= 1 << si
                    continue
                keys[k] = len(rows)
                rows.append(r)
                src_bits.append(1 << si)
                src_first.append(si)
                Jp_list.append(float(Jv[j]))
        eff = np.stack(rows)
        n = len(eff)
        scal9 = self.judge.scalars(inst, np.repeat(eff, 9, axis=0), np.tile(seeds9, n)).reshape(n, 9, H + 1, -1)
        assert np.allclose(F.J(variant, scal9[:, 0]), np.array(Jp_list)), "primary-seed J of a finalist changed"
        const = load_npz(inst_dir(H, inst, variant) / "const.npz")
        res = F.rule(variant, const["scal"], const["top"], const["sec_scal"], scal9, inst.stat_sd)
        if res["frontier_index"] >= 0:
            fi = res["frontier_index"]
            res["frontier_source"] = names[src_first[fi]]
            res["frontier_sources_all"] = [names[s] for s in range(len(names)) if src_bits[fi] >> s & 1]
            res["frontier_plan"] = F.describe_plan(eff[fi])
        save_npz(path, plans=eff, source_first=np.array(src_first), source_bits=np.array(src_bits),
                 source_names=np.array(names), J_primary=np.array(Jp_list), scal9=scal9, seeds9=np.array(seeds9),
                 rule=jdump(res), counts=jdump(cnt.done(finalists=n, replays_requested=int(9 * n))))

    # -- optional: the whole constant grid on the eight secondary seeds ---------------------------
    def stage_constfull(self, inst, variant, path):
        cnt = Counts(self.judge)
        H = self.H
        P = F.constant_plans(H)
        sec = A.secondary_seeds(inst)
        sts, oks = [], []
        for s in sec:
            scal = self.replay(inst, P, s)
            sts.append(F.statistic(variant, scal)), oks.append(F.feasible(variant, scal))
        save_npz(path, stat=np.stack(sts, 1), feas=np.stack(oks, 1), seeds=np.array(sec),
                 counts=jdump(cnt.done(plans=int(P.shape[0]), seeds=len(sec))))

    # -- the majority rule: 32 fresh oracle seeds -------------------------------------------------
    def stage_oracle(self, inst, variant, path):
        """The 20 best constants, the nine-seed rule's frontier plan, 100 plans each (seeded subsets) of the
        behaviour pool, the builder pool, source b and source c, and the cross-entropy runs' selected plans, on the
        32 oracle seeds ``dc.tasks.oracle_seeds`` (used for nothing else)."""
        cnt = Counts(self.judge)
        H = self.H
        d = inst_dir(H, inst, variant)
        const, fin, cm = load_npz(d / "const.npz"), load_npz(d / "final.npz"), load_npz(d / "cem.npz")
        eff = lambda raw: A.effective(raw, inst.task, H)
        groups, src_idx = [], []

        def add(name, plans, idx):
            groups.append((name, np.asarray(plans, dtype=np.int16).reshape(-1, H, N_COLS)))
            src_idx.append(np.asarray(idx, dtype=np.int64))

        def subset(n_total, *key):
            rng = np.random.default_rng(seed_for("tv2-oracle-subset", *key))
            return np.sort(rng.choice(n_total, size=min(N_ORACLE_SUBSET, n_total), replace=False))

        add("const20", eff(F.constant_plans(H)[const["top"]]), const["top"])
        fi = F.frontier_e(variant, fin["scal9"])["frontier_index"]
        add("frontier", fin["plans"][fi:fi + 1] if fi >= 0 else np.zeros((0, H, N_COLS), np.int16), [fi] if fi >= 0 else [])
        beh, bld = pool_plans(self.pools, inst.start_id, H)
        ib = subset(len(beh), inst.start_id, H, "behaviour")
        add("behaviour", eff(beh[ib]), ib)
        if len(bld):
            iu = subset(len(bld), inst.start_id, H, "builders")
            add("builders", eff(bld[iu]), iu)
        ov = load_npz(d / "overwrite.npz")
        raw_a = np.concatenate([beh, bld])
        raw_b = np.concatenate([F.overwrite_budget(raw_a, st) for st in ov["settings"]])
        i_b = subset(len(raw_b), inst.start_id, variant, H, "b")
        add("b", eff(raw_b[i_b]), i_b)
        if (d / "closed.npz").exists():
            cl = load_npz(d / "closed.npz")["plans"].astype(np.int16).reshape(-1, H, N_COLS)
            i_c = subset(len(cl), inst.start_id, variant, H, "c")
            add("c", eff(cl[i_c]), i_c)
        add("cem_sel", cm["sel_plans"].reshape(-1, H, N_COLS), np.arange(cm["sel_plans"].shape[0] * cm["sel_plans"].shape[1]))
        names = np.concatenate([np.full(len(g), nm) for nm, g in groups])
        allp = np.concatenate([g for _, g in groups])
        seeds = T.oracle_seeds(inst.start_id, inst.task, H, F.N_ORACLE)
        assert seeds == [seed_for("task-oracle", inst.start_id, inst.task, H, k) for k in range(F.N_ORACLE)]
        n = len(allp)
        scal = self.judge.scalars(inst, np.repeat(allp, len(seeds), axis=0), np.tile(seeds, n))
        scal = scal.reshape(n, len(seeds), H + 1, -1)
        keep = np.isin(names, ("const20", "frontier"))
        save_npz(path, plans=allp, group=names, src_index=np.concatenate(src_idx), seeds=np.array(seeds),
                 stat32=F.statistic(variant, scal), feas32=F.feasible(variant, scal),
                 scal32_const_frontier=scal[keep], group_const_frontier=names[keep],
                 cem_inits=cm["inits"], cem_budgets=cm["budgets"],
                 counts=jdump(cnt.done(plans=int(n), seeds=len(seeds), replays_requested=int(n * len(seeds)))))

    def run_instance(self, inst, variant, stages: Sequence[str]) -> None:
        d = inst_dir(self.H, inst, variant)
        for st in stages:
            if st == "closed" and self.H != 24:
                continue
            p = d / f"{st}.npz"
            if p.exists():
                continue
            t0 = time.time()
            getattr(self, f"stage_{st}")(inst, variant, p)
            c = jload(load_npz(p)["counts"])
            self.log(f"{utc()} {inst.start_id} {variant:11s} {st:9s} {time.time() - t0:7.1f} s  requests {c['engine_requests']:,} "
                     f"hits {c['engine_cache_hits']:,} replays {c['engine_replays']:,} (remote {c['engine_replays_remote']:,})")


# ----------------------------------------------------------------------------------------------
# run
# ----------------------------------------------------------------------------------------------
def tasks_v1_path(H: int, given: str = "") -> Path:
    """The first-thresholds tasks file the instances (and stat_sd, theta_v1) come from: data/tasks_H<H>.json, or
    ``--tasks-v1`` (data/tasks_x_H24.json for the held-out extension)."""
    return Path(given) if given else ROOT / "data" / f"tasks_H{H}.json"


def instances_for(H: int, n_inst, tasks_v1: str = ""):
    # start files of data/families.json and, when it exists, of data/families_x.json (start ids are disjoint)
    universe = A.load_instances(tasks_v1_path(H, tasks_v1), H, cty_of=heldout_cty_of())
    sel = A.select_instances(universe, n_inst)
    return universe, sel


def remote_check(judge: A.EngineJudge, remote, inst, H: int, log) -> None:
    rel = str(Path(inst.cty).resolve().relative_to(A.REPO))
    remote.check_files([rel])
    raw = A.Pools(H=H).behaviour(inst.start_id)[:6]
    plans = np.concatenate([A.effective(raw, "grow", H), A.effective(raw, "recover", H)])
    jobs = [(inst.cty, plans[j].tobytes(), H, A.seed_for("remote-check", j)) for j in range(len(plans))]
    same = judge._local(jobs) == remote.map([(rel,) + j[1:] for j in jobs])
    log(f"remote pool on {remote.host}: {remote.workers} workers; identical replays on {len(jobs)} check plans "
        f"(6 plain, 6 with the recover earthquake): {same}")
    if not same:
        raise SystemExit("remote replays differ from local replays")


def cmd_run(a) -> int:
    H = a.horizon
    log_path = CACHE / f"H{H}" / "logs" / f"run_shard{a.shard.replace('/', 'of')}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logf = open(log_path, "a")

    def log(s):
        print(s, flush=True)
        logf.write(s + "\n")
        logf.flush()

    k, n = (int(v) for v in a.shard.split("/"))
    universe, sel = instances_for(H, "all" if a.instances == "all" else int(a.instances), a.tasks_v1)
    variants = [v for v in a.variants.split(",") if v]
    stages = [s for s in a.stages.split(",") if s]
    for s in stages:
        if s not in STAGES + OPTIONAL_STAGES:
            raise SystemExit(f"unknown stage {s}")
    starts = sorted({i.start_id for i in sel})
    if a.starts:
        starts = [s for s in starts if s in set(a.starts.split(","))]
    mine = [sid for j, sid in enumerate(starts) if j % n == k]
    by_key = {(i.start_id, i.task): i for i in sel}
    todo = [(by_key[(sid, F.base_task(v))], v) for sid in mine for v in variants if (sid, F.base_task(v)) in by_key]
    remote = None
    if a.remote == "host-b":
        remote = A.host_b_pool(a.remote_workers, A.HOST_B_ROOT, log_path=log_path.with_suffix(".remote_stderr.log"))
    judge = A.EngineJudge(A.CACHE_ROOT / "engine_cache", workers=a.workers, H=H, remote=remote, log=log)
    if remote is not None:
        remote_check(judge, remote, todo[0][0], H, log)
    pools = A.Pools(H=H)
    runner = Runner(H, judge, pools, a.workers, log)
    meta = {"argv": sys.argv, "started_utc": dt.datetime.utcnow().isoformat(timespec="seconds"), "shard": a.shard,
            "instances": len(todo), "variants": variants, "stages": stages, "protocol": PROTO_VERSION,
            "engine_cache": str(A.CACHE_ROOT / "engine_cache"), "local_workers": a.workers,
            "remote": a.remote, "remote_workers": a.remote_workers if remote else 0}
    with open(CACHE / f"H{H}" / "logs" / "invocations.jsonl", "a") as f:
        f.write(json.dumps(meta) + "\n")
    log(f"{utc()} shard {a.shard}: {len(todo)} instance-variants on {len(mine)} starts, stages {stages}, pid {os.getpid()}")
    t0 = time.time()
    try:
        for j, (inst, v) in enumerate(todo):
            runner.run_instance(inst, v, stages)
            log(f"{utc()} done {j + 1}/{len(todo)} ({inst.start_id} {v}); {time.time() - t0:.0f} s elapsed; "
                f"judge {judge.counters()}")
    finally:
        runner.close()
        judge.close()
    log(f"{utc()} shard {a.shard} finished in {time.time() - t0:.0f} s")
    return 0


# ----------------------------------------------------------------------------------------------
# assemble
# ----------------------------------------------------------------------------------------------
def pass_share(stat, feas, theta) -> float:
    stat, feas = np.asarray(stat), np.asarray(feas)
    if stat.size == 0 or not np.isfinite(theta):
        return float("nan")
    return float(np.mean(feas & (stat >= theta)))


def instance_record(H: int, inst: A.Instance, variant: str, v1: dict, cal_dir: Path) -> Optional[dict]:
    d = inst_dir(H, inst, variant)
    need = ["const", "pools", "overwrite", "cem", "final"] + (["closed"] if H == 24 else [])
    if not all((d / f"{s}.npz").exists() for s in need):
        return None
    const = load_npz(d / "const.npz")
    fin = load_npz(d / "final.npz")
    # the rule is recomputed here from the stored replays (the copy saved by the run is kept in final.npz)
    stat_sd, theta_v1 = inst.stat_sd, inst.theta
    if F.VARIANTS[variant][1] == "rev":
        # a new statistic: no v1 threshold; stat_sd by the v1 definition (sd of the feasible statistic over the
        # behaviour-mix calibration trajectories)
        with np.load(cal_dir / f"{inst.start_id}.npz") as z:
            scc = z["scal_plain"]
        okc, stc = F.feasible(variant, scc), F.statistic(variant, scc)
        stat_sd = float(np.std(stc[okc])) if okc.sum() > 1 else float(np.std(stc))
        stat_sd = stat_sd if stat_sd > 0 else 1.0
        theta_v1 = float("nan")
        inst = A.Instance(inst.key, inst.start_id, inst.family_id, inst.task, inst.horizon, theta_v1, stat_sd,
                          inst.in_band, inst.cty)
    res = F.rule(variant, const["scal"], const["top"], const["sec_scal"], fin["scal9"], stat_sd)
    if res["frontier_index"] >= 0:
        fi = res["frontier_index"]
        names = [str(x) for x in fin["source_names"]]
        res["frontier_source"] = names[int(fin["source_first"][fi])]
        res["frontier_sources_all"] = [names[k] for k in range(len(names)) if int(fin["source_bits"][fi]) >> k & 1]
        res["frontier_plan"] = F.describe_plan(fin["plans"][fi])
    pools = load_npz(d / "pools.npz")
    ov = load_npz(d / "overwrite.npz")
    cm = load_npz(d / "cem.npz")
    cl = load_npz(d / "closed.npz") if (d / "closed.npz").exists() else None
    cf = load_npz(d / "constfull.npz") if (d / "constfull.npz").exists() else None
    nb = int(pools["n_beh"])
    st_c, ok_c = F.statistic(variant, const["scal"]), F.feasible(variant, const["scal"])
    st_cs, ok_cs = F.statistic(variant, const["sec_scal"]), F.feasible(variant, const["sec_scal"])
    rec = {"key": inst.key, "variant": variant, "task": inst.task, "start_id": inst.start_id, "family_id": inst.family_id,
           "theta_v1": inst.theta, "stat_sd": inst.stat_sd, **{k: res[k] for k in res if k not in ("frontier_plan",)}}
    rec["frontier_plan"] = res.get("frontier_plan")
    rec["best_settings"] = [[int(x) for x in F.GRID[i]] for i in const["top"][:3]]
    # the v1 threshold: constant plans (and pools) at the current theta
    th1 = inst.theta
    rec["v1_const_pass_primary"] = bool((ok_c & (st_c >= th1)).any())
    rec["v1_const_pass_any9_top20"] = bool(rec["v1_const_pass_primary"] or (ok_cs & (st_cs >= th1)).any())
    rec["v1_default_pass_primary"] = bool(ok_c[F.GRID.tolist().index(list(F.DEFAULT_SETTING))]
                                          and st_c[F.GRID.tolist().index(list(F.DEFAULT_SETTING))] >= th1)
    sub567 = np.isin(F.GRID[:, 1:], (0, 2, 4)).all(axis=1)      # the main 567-plan grid (levels 0, 50, 100 %)
    rec["v1_const567_pass_primary"] = bool((ok_c & (st_c >= th1))[sub567].any())
    if cf is not None:
        rec["v1_const_pass_any9_full"] = bool(rec["v1_const_pass_primary"] or (cf["feas"] & (cf["stat"] >= th1)).any())
    rec["v1_beh_pass_primary"] = pass_share(pools["stat"][:nb], pools["feas"][:nb], th1)
    if not np.isfinite(th1):            # no v1 threshold for this variant
        for k in [k for k in rec if k.startswith("v1_")]:
            rec[k] = float("nan")
    # diagnostics (not the rule): like-for-like do-nothing frontiers and how the bar separates the two frontier plans
    e, sd = res["e"], res["seed_sd"]
    fin_ok = np.isfinite(e)
    rec["diag_e_minus_cmean9_seed_sd"] = float((e - res["c_mean9"]) / sd) if (fin_ok and sd > 0 and np.isfinite(res["c_mean9"])) else float("nan")
    rec["diag_wp_cmean9_4sd"] = bool(fin_ok and np.isfinite(res["c_mean9"]) and e - res["c_mean9"] >= 4 * sd)
    rec["diag_wp_cmean9_2sd"] = bool(fin_ok and np.isfinite(res["c_mean9"]) and e - res["c_mean9"] >= 2 * sd)
    rec["diag_wp_c_2sd"] = bool(fin_ok and e - res["c"] >= 2 * sd)
    if cf is not None:
        st9 = np.concatenate([st_c[:, None], cf["stat"]], axis=1)          # (2625, 9), primary first
        ok9 = np.concatenate([ok_c[:, None], cf["feas"]], axis=1)
        any_ok = ok9.any()
        rec["diag_c_full9_any"] = float(np.max(np.where(ok9, st9, -np.inf))) if any_ok else float(np.max(st9))
        m9 = st9.mean(axis=1)
        allok = ok9.all(axis=1)
        rec["diag_c_full9_mean"] = float(np.max(np.where(allok, m9, -np.inf))) if allok.any() else float("nan")
        rec["diag_wp_cfull9mean_4sd"] = bool(fin_ok and allok.any() and e - rec["diag_c_full9_mean"] >= 4 * sd)
    for lam in F.LAMBDAS:
        tag = f"l{int(round(100 * lam))}"
        th = res[f"theta_{tag}"]
        if res.get("frontier_stats") is not None and np.isfinite(th):
            rec[f"diag_frontier_pass9_{tag}"] = float(np.mean(np.array(res["frontier_stats"]) >= th))
        if res.get("c_mean9_stats") is not None and np.isfinite(th):
            rec[f"diag_cmean9_pass9_{tag}"] = float(np.mean(np.array(res["c_mean9_stats"]) >= th))
    # base rates at the v2 thresholds
    G, N = big_schedule(H)
    for lam in F.LAMBDAS:
        tag = f"l{int(round(100 * lam))}"
        th = res[f"theta_{tag}"]
        r = {}
        r["const_primary"] = pass_share(st_c, ok_c, th)
        r["const_top20_secondary"] = pass_share(st_cs, ok_cs, th)
        if cf is not None:
            r["const_full_secondary"] = pass_share(cf["stat"], cf["feas"], th)
        r["behaviour"] = pass_share(pools["stat"][:nb], pools["feas"][:nb], th)
        r["builders"] = pass_share(pools["stat"][nb:], pools["feas"][nb:], th) if int(pools["n_bld"]) else float("nan")
        r["b_overwrite"] = pass_share(ov["stat"], ov["feas"], th)
        r["c_closed"] = pass_share(cl["stat"], cl["feas"], th) if cl is not None else float("nan")
        for ii, name in enumerate(cm["inits"]):
            for bi, B in enumerate(cm["budgets"]):
                p1 = F.verdict(variant, cm["sel_scal_primary"][ii, bi], th) if np.isfinite(th) else False
                p8 = F.verdict(variant, cm["sel_scal_secondary"][ii, bi], th).mean() if np.isfinite(th) else float("nan")
                r[f"cem_{name}_{int(B)}_primary"] = float(p1)
                r[f"cem_{name}_{int(B)}_secondary"] = float(p8)
        rec[f"pass_{tag}"] = r
    # behaviour-mix base rate on the calibration trajectories (the v1 definition: fit = first 600, val = last 400)
    with np.load(cal_dir / f"{inst.start_id}.npz") as z:
        sc = z["scal_recover" if inst.task == "recover" else "scal_plain"]
    th = res["theta"]
    rec["cal_base_rate_fit"] = float(np.mean(F.verdict(variant, sc[:600], th))) if np.isfinite(th) else float("nan")
    rec["cal_base_rate_val"] = float(np.mean(F.verdict(variant, sc[600:], th))) if np.isfinite(th) else float("nan")
    rec["cal_feasible_rate"] = float(np.mean(F.feasible(variant, sc)))
    rec["_cal_scal"] = sc            # used below for the majority-rule theta, dropped before writing
    # where e - c <= 0 or e undefined, the rule fails on this instance
    rec["rule_fails"] = (not np.isfinite(res["e"])) or (res["e"] <= res["c"])
    orc = load_npz(d / "oracle.npz") if (d / "oracle.npz").exists() else None
    if orc is not None:
        oracle_record(rec, variant, inst, orc)
        th32 = rec["theta32_l50"]
        sc = rec["_cal_scal"]
        rec["cal_base_rate32_fit"] = float(np.mean(F.verdict(variant, sc[:600], th32))) if np.isfinite(th32) else float("nan")
        rec["cal_base_rate32_val"] = float(np.mean(F.verdict(variant, sc[600:], th32))) if np.isfinite(th32) else float("nan")
    rec.pop("_cal_scal", None)
    counts = {}
    for s in need + (["constfull"] if cf is not None else []) + (["oracle"] if orc is not None else []):
        c = jload(load_npz(d / f"{s}.npz")["counts"])
        counts[s] = c
    rec["counts"] = counts
    rec["cem_logs"] = {k: {kk: vv for kk, vv in v.items() if kk in ("n_scored", "generations", "population", "best_score",
                                                                      "best_per_generation")}
                       for k, v in jload(cm["logs"]).items()}
    rec["source_best_J"] = {}
    for nm, arr in (("a_behaviour", pools["J"][:nb]), ("a_builders", pools["J"][nb:]), ("b", ov["J"]),
                    ("c", cl["J"] if cl is not None else np.zeros(0)), ("d", cm["big_J"])):
        rec["source_best_J"][nm] = float(np.max(arr)) if np.size(arr) else None
    return rec


def oracle_record(rec: dict, variant: str, inst: A.Instance, orc: Dict[str, np.ndarray]) -> None:
    """The majority rule on the 32 oracle seeds: c32, e32, theta32, well-posedness, base rates by source under
    the majority rule and on oracle seed 0 alone, and the cross-check against ``dc.tasks.oracle_value``."""
    g, st, fe = orc["group"], orc["stat32"], orc["feas32"]
    c, f = g == "const20", g == "frontier"
    r32 = F.rule32(st[c], fe[c], st[f][0] if f.any() else None, fe[f][0] if f.any() else None)
    rec.update(r32)
    m = F.majority_value(st, fe)
    rec["oracle_n_seeds"] = int(st.shape[1])
    # the two ways of counting the majority agree (16 of 32 passes) on every plan at every theta32
    for lam in F.LAMBDAS:
        th = r32[f"theta32_l{int(round(100 * lam))}"]
        if np.isfinite(th):
            assert np.array_equal(m >= th, F.majority_pass(st, fe, th))
    # cross-check with dc.tasks (the reference oracle) on the stored 32-seed trajectories
    sc = orc["scal32_const_frontier"]
    task = F.base_task(variant)
    if variant in ("treasury_v1", "treasury_v2"):
        rec["oracle_crosscheck"] = "n/a (a funds form of treasury, dropped; dc.tasks holds the revenue form)"
    else:                                              # treasury_rev is dc.tasks' treasury since amendment 3
        same = bool(np.array_equal(T.oracle_value(task, sc), F.majority_value(F.statistic(variant, sc), F.feasible(variant, sc))))
        rec["oracle_crosscheck"] = "equal" if same else "DIFFERENT"
    inits, budgets = [str(x) for x in orc["cem_inits"]], [int(x) for x in orc["cem_budgets"]]
    for lam in F.LAMBDAS:
        tag = f"l{int(round(100 * lam))}"
        th = r32[f"theta32_{tag}"]
        maj, one = {}, {}
        for grp in ("const20", "frontier", "behaviour", "builders", "b", "c"):
            sel = g == grp
            if not sel.any() or not np.isfinite(th):
                maj[grp] = one[grp] = float("nan")
                continue
            maj[grp] = float(np.mean(m[sel] >= th))
            one[grp] = float(np.mean(fe[sel, 0] & (st[sel, 0] >= th)))
        sel = np.flatnonzero(g == "cem_sel")
        for k, row in enumerate(sel):
            name = f"cem_{inits[k // len(budgets)]}_{budgets[k % len(budgets)]}"
            maj[name] = float(m[row] >= th) if np.isfinite(th) else float("nan")
            one[name] = float(fe[row, 0] & (st[row, 0] >= th)) if np.isfinite(th) else float("nan")
        rec[f"pass32_{tag}"] = maj
        rec[f"pass_seed0_{tag}"] = one
    rec["rule32_fails"] = not (np.isfinite(r32["headroom32"]) and r32["headroom32"] > 0)


def q(x, p):
    """Quantile over the non-NaN values; +inf (headroom over a zero seed sd) is kept and printed as inf."""
    x = np.asarray([v for v in x if v is not None and not np.isnan(v)], dtype=np.float64)
    if not x.size:
        return float("nan")
    v = float(np.quantile(np.minimum(x, 1e12), p))
    return float("inf") if v >= 1e11 else v


def fmt(v, nd=3):
    if isinstance(v, float) and v == float("inf"):
        return "inf"
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "-"
    if isinstance(v, (bool, np.bool_)):
        return str(bool(v))
    if isinstance(v, (int, np.integer)):
        return f"{int(v):,}"
    return f"{v:.{nd}f}"


def tables(H: int, recs: List[dict], variants: Sequence[str]) -> str:
    G, N = big_schedule(H)
    bigB = G * N
    out = []
    groups = [(v, [r for r in recs if r["variant"] == v]) for v in variants]
    prop = [r for r in recs if r["variant"] in F.PROPOSAL_VARIANTS]
    groups_all = groups + [("overall (proposal)", prop)]
    inits0 = ["behaviour", "builders"] if H == 24 else ["behaviour"]
    budgets0 = list(SMALL_BUDGETS) + [bigB]
    out.append(f"## H = {H}: headline at theta(0.5)\n")
    out.append("v1 = the current thresholds (`data/tasks_H%d.json`); a constant plan passes if some replay of it passes "
               "(primary grid plus the 20 best on the eight secondary seeds; full grid on nine seeds where the constfull "
               "stage ran). Pass rates at theta(0.5): pools, b, c on the primary seed; CE = the plan selected on the primary "
               "seed, share of the eight secondary seeds on which it passes (B = 10 / 100 / 1,000 / %s).\n" % (H, f"{bigB:,}"))
    hdr = ["variant", "n", "v1: some constant passes", "v1: full grid, 9 seeds", "e > c", "well posed", "behaviour pool",
           "builder pool", "b", "c"] + [f"CE {nm}-init" for nm in inits0]
    out.append("| " + " | ".join(hdr) + " |")
    out.append("|" + "---|" * len(hdr))
    for v, rs in groups + [("overall (proposal)", prop)]:
        if not rs:
            continue
        full = [r["v1_const_pass_any9_full"] for r in rs if "v1_const_pass_any9_full" in r]
        m = lambda k: fmt(np.nanmean([r["pass_l50"].get(k, float("nan")) for r in rs]))
        cells = [v, str(len(rs)), fmt(np.mean([r["v1_const_pass_any9_top20"] for r in rs])),
                 (fmt(np.mean(full)) if len(full) == len(rs) else ("-" if not full else fmt(np.mean(full)) + f" ({len(full)})")),
                 fmt(np.mean([bool(np.isfinite(r["e"]) and r["e"] > r["c"]) for r in rs])),
                 fmt(np.mean([r["well_posed"] for r in rs])), m("behaviour"), m("builders"), m("b_overwrite"), m("c_closed")]
        for nm in inits0:
            cells.append(" / ".join(m(f"cem_{nm}_{B}_secondary") for B in budgets0))
        out.append("| " + " | ".join(cells) + " |")
    out.append("")
    out.append(f"## H = {H}: instances per variant\n")
    out.append("| variant | instances complete |\n|---|---|")
    for v, rs in groups:
        out.append(f"| {v} | {len(rs)} |")
    out.append("")
    out.append("### Constant plans at the current (v1) thresholds\n")
    out.append("| variant | n | default (tax 7, 100%) passes, primary | some constant of the 567-plan grid passes, primary | some constant passes, primary | some constant passes, any of 9 seeds (primary grid + top-20 on 8 secondary) | some constant passes, any of 9 seeds (full grid on all 9) | behaviour pool pass share at v1, primary |")
    out.append("|---|---|---|---|---|---|---|---|")
    for v, rs in groups_all:
        if not rs:
            continue
        full = [r["v1_const_pass_any9_full"] for r in rs if "v1_const_pass_any9_full" in r]
        out.append(f"| {v} | {len(rs)} | {fmt(np.mean([r['v1_default_pass_primary'] for r in rs]))} | "
                   f"{fmt(np.mean([r['v1_const567_pass_primary'] for r in rs]))} | "
                   f"{fmt(np.mean([r['v1_const_pass_primary'] for r in rs]))} | {fmt(np.mean([r['v1_const_pass_any9_top20'] for r in rs]))} | "
                   f"{fmt(np.mean(full)) if len(full) == len(rs) else ('-' if not full else fmt(np.mean(full)) + f' ({len(full)} inst.)')} | "
                   f"{fmt(np.mean([r['v1_beh_pass_primary'] for r in rs]))} |")
    out.append("")
    out.append("### Frontiers and headroom\n")
    out.append("Headroom = e - c. Quartiles are (25 %, median, 75 %) over instances. c and e are also given relative to the "
               "v1 threshold, in units of stat_sd.\n")
    out.append("| variant | n | c feasible | e defined | e > c | well posed (e - c >= 4 seed sd) | headroom / seed sd | headroom / stat_sd | seed sd / stat_sd | (c - theta_v1) / stat_sd | (e - theta_v1) / stat_sd | diagnostic: e > c_mean9 | diagnostic: (e - c_mean9) / seed sd |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for v, rs in groups_all:
        if not rs:
            continue
        hs = [r["headroom_seed_sd"] for r in rs]
        hst = [r["headroom_stat_sd"] for r in rs]
        ss = [r["seed_sd"] / r["stat_sd"] if np.isfinite(r["seed_sd"]) else float("nan") for r in rs]
        cr = [(r["c"] - r["theta_v1"]) / r["stat_sd"] for r in rs]
        er = [(r["e"] - r["theta_v1"]) / r["stat_sd"] if np.isfinite(r["e"]) else float("nan") for r in rs]
        f3 = lambda x: f"{fmt(q(x, .25), 2)}, {fmt(q(x, .5), 2)}, {fmt(q(x, .75), 2)}"
        out.append(f"| {v} | {len(rs)} | {fmt(np.mean([r['c_feasible'] for r in rs]))} | {fmt(np.mean([np.isfinite(r['e']) for r in rs]))} | "
                   f"{fmt(np.mean([np.isfinite(r['e']) and r['e'] > r['c'] for r in rs]))} | {fmt(np.mean([r['well_posed'] for r in rs]))} | "
                   f"{f3(hs)} | {f3(hst)} | {f3(ss)} | {f3(cr)} | {f3(er)} | "
                   f"{fmt(np.mean([np.isfinite(r['e']) and np.isfinite(r['c_mean9']) and r['e'] > r['c_mean9'] for r in rs]))} | "
                   f"{f3([(r['e'] - r['c_mean9']) / r['seed_sd'] if (np.isfinite(r['e']) and r['seed_sd'] > 0) else float('nan') for r in rs])} |")
    out.append("")
    out.append("### Diagnostics, not the rule: like-for-like do-nothing frontiers\n")
    out.append("c_mean9 = the largest nine-seed mean statistic among the 20 constant plans replayed on nine seeds (feasible "
               "on all nine); c_full9_mean = the same over the whole grid on nine seeds (where the constfull stage ran). "
               "Pass9 = share of the nine seeds on which the plan's statistic reaches theta(0.5) (feasibility aside).\n")
    out.append("| variant | n | e - c >= 2 seed sd | e - c_mean9 >= 4 seed sd | e - c_mean9 >= 2 seed sd | e - c_full9_mean >= 4 seed sd | (e - c_mean9) / seed sd (quartiles) | frontier plan pass9 at theta(0.5) | best constant (c_mean9) pass9 at theta(0.5) |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for v, rs in groups_all:
        if not rs:
            continue
        cf_ = [r["diag_wp_cfull9mean_4sd"] for r in rs if "diag_wp_cfull9mean_4sd" in r]
        x = [r["diag_e_minus_cmean9_seed_sd"] for r in rs]
        out.append(f"| {v} | {len(rs)} | {fmt(np.mean([r['diag_wp_c_2sd'] for r in rs]))} | {fmt(np.mean([r['diag_wp_cmean9_4sd'] for r in rs]))} | "
                   f"{fmt(np.mean([r['diag_wp_cmean9_2sd'] for r in rs]))} | {fmt(np.mean(cf_)) + ('' if len(cf_) == len(rs) else f' ({len(cf_)} inst.)') if cf_ else '-'} | "
                   f"{fmt(q(x, .25), 2)}, {fmt(q(x, .5), 2)}, {fmt(q(x, .75), 2)} | "
                   f"{fmt(np.nanmean([r.get('diag_frontier_pass9_l50', float('nan')) for r in rs]))} | "
                   f"{fmt(np.nanmean([r.get('diag_cmean9_pass9_l50', float('nan')) for r in rs]))} |")
    out.append("")
    out.append("### Which source supplied the frontier plan (share of instances with e defined; a plan found by several sources counts for the first in a, b, c, d order)\n")
    out.append("| variant | a (pools) | b (pools, budget overwritten) | c (closed-loop builders) | d (cross-entropy search) | also found by another source |")
    out.append("|---|---|---|---|---|---|")
    for v, rs in groups_all:
        rs2 = [r for r in rs if r.get("frontier_source")]
        if not rs2:
            continue
        sh = lambda s: fmt(np.mean([r["frontier_source"] == s for r in rs2]))
        out.append(f"| {v} | {sh('a')} | {sh('b')} | {sh('c')} | {sh('d')} | {fmt(np.mean([len(r['frontier_sources_all']) > 1 for r in rs2]))} |")
    out.append("")
    out.append("### What the frontier plans do (means over instances)\n")
    out.append("| variant | macros / month | builds nothing | constant budget | tax mean | tax min..max (median over instances) | road % | fire % | police % | macro kinds per month (mean over instances, top 6) |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for v, rs in groups_all:
        fp = [r["frontier_plan"] for r in rs if r.get("frontier_plan")]
        if not fp:
            continue
        kinds = {}
        for p in fp:
            for kk, vv in p["by_kind_per_month"].items():
                kinds[kk] = kinds.get(kk, 0.0) + vv / len(fp)
        ks = ", ".join(f"{kk} {vv:.2f}" for kk, vv in sorted(kinds.items(), key=lambda x: -x[1])[:6])
        out.append(f"| {v} | {fmt(np.mean([p['macros_per_month'] for p in fp]), 2)} | {fmt(np.mean([p['builds_nothing'] for p in fp]))} | "
                   f"{fmt(np.mean([p['constant_budget'] for p in fp]))} | {fmt(np.mean([p['tax_mean'] for p in fp]), 1)} | "
                   f"{int(np.median([p['tax_min'] for p in fp]))}..{int(np.median([p['tax_max'] for p in fp]))} | "
                   f"{fmt(np.mean([p['road_pct_mean'] for p in fp]), 0)} | {fmt(np.mean([p['fire_pct_mean'] for p in fp]), 0)} | "
                   f"{fmt(np.mean([p['police_pct_mean'] for p in fp]), 0)} | {ks} |")
    out.append("")
    inits = ["behaviour", "builders"] if H == 24 else ["behaviour"]
    budgets = list(SMALL_BUDGETS) + [bigB]
    for lam in F.LAMBDAS:
        tag = f"l{int(round(100 * lam))}"
        out.append(f"### Pass rates at theta({lam})\n")
        out.append("Pools, b, c and constants: share of plans passing on the primary seed, mean over instances. Cross-entropy "
                   "search: the plan selected on the primary seed, its pass share on the eight secondary seeds, mean over "
                   "instances (its primary-seed pass share in brackets).\n")
        hdr = ["variant", "n", "constants (primary)", "constants top-20 (8 secondary)", "constants full grid (8 secondary)",
               "behaviour pool", "builder pool", "b", "c"]
        for name in inits:
            for B in budgets:
                hdr.append(f"CE {name}-init B={B:,}")
        out.append("| " + " | ".join(hdr) + " |")
        out.append("|" + "---|" * len(hdr))
        for v, rs in groups_all:
            if not rs:
                continue
            m = lambda k: fmt(np.nanmean([r[f"pass_{tag}"].get(k, float("nan")) for r in rs]))
            cells = [v, str(len(rs)), m("const_primary"), m("const_top20_secondary"),
                     m("const_full_secondary") if all("const_full_secondary" in r[f"pass_{tag}"] for r in rs) else "-",
                     m("behaviour"), m("builders"), m("b_overwrite"), m("c_closed")]
            for name in inits:
                for B in budgets:
                    cells.append(f"{m(f'cem_{name}_{B}_secondary')} ({m(f'cem_{name}_{B}_primary')})")
            out.append("| " + " | ".join(cells) + " |")
        out.append("")
    fails = [r for r in recs if r["rule_fails"] or not r["well_posed"]]
    out.append(f"### Instances where the rule fails or is not well posed ({len(fails)} of {len(recs)})\n")
    out.append("| instance | variant | c | c from seed (0 = primary) | c_mean9 | e | seed sd | e - c | headroom / seed sd | frontier source | finalists feasible on 9 seeds |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in fails:
        out.append(f"| {r['start_id']} | {r['variant']} | {fmt(r['c'], 4)}{'' if r['c_feasible'] else ' (infeasible)'} | {r['c_seed_index']} | {fmt(r['c_mean9'], 4)} | {fmt(r['e'], 4)} | {fmt(r['seed_sd'], 4)} | "
                   f"{fmt(r['headroom'], 4)} | {fmt(r['headroom_seed_sd'], 2)} | {r.get('frontier_source', '-')} | "
                   f"{r['n_feasible_all_seeds']}/{r['n_finalists']} |")
    out.append("")
    return "\n".join(out)


def oracle_tables(H: int, recs: List[dict], variants: Sequence[str]) -> str:
    G, N = big_schedule(H)
    budgets = list(SMALL_BUDGETS) + [G * N]
    inits = ["behaviour", "builders"] if H == 24 else ["behaviour"]
    rs_all = [r for r in recs if "c32" in r]
    groups = [(v, [r for r in rs_all if r["variant"] == v]) for v in variants]
    groups += [("overall (proposal)", [r for r in rs_all if r["variant"] in F.PROPOSAL_VARIANTS])]
    out = [f"## H = {H}: the majority rule on {F.N_ORACLE} oracle seeds\n",
           "m32 = the 16th largest of the 32 per-seed feasible statistics (upper median; minus infinity where infeasible), so "
           "m32 >= theta exactly when at least 16 of 32 seeds pass (an exact 16 passes). c32 = the largest m32 among the 20 "
           "best constant plans; e32 = m32 of the nine-seed rule's frontier plan (not re-selected); theta32(lambda) = c32 + "
           "lambda (e32 - c32); well posed when e32 - c32 >= 6 x 1.2533 seed_sd32 / sqrt(32) (seed_sd32 = sd of the frontier "
           "plan's statistic over the 32 seeds), or > 0 where seed_sd32 = 0. Base rates: share of plans whose m32 >= theta32 "
           "(100-plan seeded subsets of each source; the 20 constants; the cross-entropy runs' selected plans, selected on the "
           "primary seed as run). 'seed 0' = the same plans judged on oracle seed 0 alone.\n"]
    out.append("| variant | n | e32 > c32 | well posed32 | (e32 - c32) / SE quartiles | (e32 - c32) / stat_sd quartiles | seed_sd32 / stat_sd median | frontier plan feasible on all 32 seeds | dc.tasks cross-check |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for v, rs in groups:
        if not rs:
            continue
        hse = [r["headroom32_se"] for r in rs]
        hst = [r["headroom32"] / r["stat_sd"] for r in rs]
        f3 = lambda x: f"{fmt(q(x, .25), 2)}, {fmt(q(x, .5), 2)}, {fmt(q(x, .75), 2)}"
        cc = [r.get("oracle_crosscheck", "") for r in rs]
        out.append(f"| {v} | {len(rs)} | {fmt(np.mean([np.isfinite(r['headroom32']) and r['headroom32'] > 0 for r in rs]))} | "
                   f"{fmt(np.mean([r['well_posed32'] for r in rs]))} | {f3(hse)} | {f3(hst)} | "
                   f"{fmt(q([r['seed_sd32'] / r['stat_sd'] for r in rs], .5), 3)} | "
                   f"{fmt(np.mean([r['front_feasible_seeds32'] == r['oracle_n_seeds'] for r in rs]))} | "
                   f"{sum(c == 'equal' for c in cc)} equal, {sum(c == 'DIFFERENT' for c in cc)} different, {sum(c.startswith('n/a') for c in cc)} n/a |")
    out.append("")
    for lam in F.LAMBDAS:
        tag = f"l{int(round(100 * lam))}"
        for rule, key in (("majority over 32 oracle seeds", "pass32"), ("oracle seed 0 alone", "pass_seed0")):
            out.append(f"### Base rates at theta32({lam}), {rule}\n")
            hdr = ["variant", "n", "constants (20)", "frontier plan", "behaviour", "builders", "b", "c"]
            hdr += [f"CE {nm}-init B=" + " / ".join(f"{B:,}" for B in budgets) for nm in inits]
            out.append("| " + " | ".join(hdr) + " |")
            out.append("|" + "---|" * len(hdr))
            for v, rs in groups:
                if not rs:
                    continue
                m = lambda k: fmt(np.nanmean([r[f"{key}_{tag}"].get(k, float("nan")) for r in rs]))
                cells = [v, str(len(rs)), m("const20"), m("frontier"), m("behaviour"), m("builders"), m("b"), m("c")]
                for nm in inits:
                    cells.append(" / ".join(m(f"cem_{nm}_{B}") for B in budgets))
                out.append("| " + " | ".join(cells) + " |")
            out.append("")
    bad = [r for r in rs_all if r["rule32_fails"]]
    out.append(f"### Instances with e32 - c32 <= 0 or undefined ({len(bad)} of {len(rs_all)})\n")
    out.append("| instance | variant | c32 | e32 | seed_sd32 | e32 - c32 | nine-seed c | nine-seed e | frontier feasible seeds of 32 |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for r in bad:
        out.append(f"| {r['start_id']} | {r['variant']} | {fmt(r['c32'], 4)} | {fmt(r['e32'], 4)} | {fmt(r['seed_sd32'], 4)} | "
                   f"{fmt(r['headroom32'], 4)} | {fmt(r['c'], 4)} | {fmt(r['e'], 4)} | {r['front_feasible_seeds32']} |")
    nwp = [r for r in rs_all if not r["rule32_fails"] and not r["well_posed32"]]
    out.append("")
    out.append(f"### Instances with e32 > c32 but not well posed ({len(nwp)} of {len(rs_all)})\n")
    out.append("| instance | variant | c32 | e32 | seed_sd32 | (e32 - c32) / SE |")
    out.append("|---|---|---|---|---|---|")
    for r in nwp:
        out.append(f"| {r['start_id']} | {r['variant']} | {fmt(r['c32'], 4)} | {fmt(r['e32'], 4)} | {fmt(r['seed_sd32'], 4)} | {fmt(r['headroom32_se'], 2)} |")
    out.append("")
    return "\n".join(out)


def cmd_assemble(a) -> int:
    H = a.horizon
    universe, sel = instances_for(H, "all" if a.instances == "all" else int(a.instances), a.tasks_v1)
    variants = [v for v in a.variants.split(",") if v]
    cal_dir = A.CAL_DIR / f"H{H}"
    recs = []
    missing = []
    for inst in sel:
        for v in variants:
            if F.base_task(v) != inst.task:
                continue
            r = instance_record(H, inst, v, {}, cal_dir)
            if r is None:
                missing.append(f"{inst.start_id}|{v}")
            else:
                recs.append(r)
    md = (oracle_tables(H, recs, variants) + "\n") if any("c32" in r for r in recs) else ""
    md += tables(H, recs, variants)
    out_dir = Path(a.results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"tables_H{H}.md").write_text(md)
    (out_dir / f"instances_H{H}.json").write_text(json.dumps(recs, indent=0, default=float))
    print(md)
    print(f"{len(recs)} instance-variants complete, {len(missing)} missing")
    if missing:
        print("missing:", ", ".join(missing[:20]), "..." if len(missing) > 20 else "")
    # proposal JSON
    if a.write_json:
        v1 = json.loads(tasks_v1_path(H, a.tasks_v1).read_text())
        by = {(r["start_id"], r["variant"]): r for r in recs}
        out_inst = []
        excluded = []
        for d in v1["instances"]:
            if d["task"] not in [F.base_task(v) for v in F.PROPOSAL_VARIANTS]:
                continue
            v = [x for x in F.PROPOSAL_VARIANTS if F.base_task(x) == d["task"]][0]
            r = by.get((d["start_id"], v))
            if r is None:
                continue
            nd = dict(d)
            th = r["theta"]
            same_stat = F.VARIANTS[v][1] != "rev"          # the revenue form has another statistic than v1's funds
            nd.update(stat_sd=float(r["stat_sd"]))
            nd.update(theta=(float(th) if np.isfinite(th) else None), theta_v1=(d["theta"] if same_stat else None),
                      c=r["c"], c_feasible=r["c_feasible"],
                      e=(r["e"] if np.isfinite(r["e"]) else None),
                      seed_sd=(r["seed_sd"] if np.isfinite(r["seed_sd"]) else None), well_posed=bool(r["well_posed"]),
                      theta_l25=(r["theta_l25"] if np.isfinite(r["theta_l25"]) else None),
                      theta_l75=(r["theta_l75"] if np.isfinite(r["theta_l75"]) else None),
                      predicate=F.PREDICATES[v], frontier_source=r.get("frontier_source"),
                      base_rate_fit=r["cal_base_rate_fit"], base_rate_val=r["cal_base_rate_val"],
                      feasible_rate=r["cal_feasible_rate"],
                      in_band=bool(np.isfinite(r["cal_base_rate_val"]) and T.BAND[0] <= r["cal_base_rate_val"] <= T.BAND[1]),
                      base_rates={k: (vv if np.isfinite(vv) else None) for k, vv in r["pass_l50"].items()},
                      note=("rule undefined: no finalist feasible on all nine seeds" if not np.isfinite(r["e"]) else
                            ("rule fails: e <= c" if r["e"] <= r["c"] else ("not well posed" if not r["well_posed"] else ""))))
            if a.oracle:
                if "c32" not in r:
                    raise SystemExit(f"--oracle: {d['start_id']} {v} has no oracle stage")
                fz = lambda x: float(x) if np.isfinite(x) else None
                nd.update(theta=fz(r["theta32_l50"]), theta_l50=fz(r["theta"]),
                          c32=fz(r["c32"]), e32=fz(r["e32"]), seed_sd32=fz(r["seed_sd32"]), well_posed32=bool(r["well_posed32"]),
                          theta32_l25=fz(r["theta32_l25"]), theta32_l50=fz(r["theta32_l50"]), theta32_l75=fz(r["theta32_l75"]),
                          base_rate_fit=r["cal_base_rate32_fit"], base_rate_val=r["cal_base_rate32_val"],
                          in_band=bool(np.isfinite(r["cal_base_rate32_val"]) and T.BAND[0] <= r["cal_base_rate32_val"] <= T.BAND[1]),
                          base_rates32={k: fz(vv) for k, vv in r["pass32_l50"].items()},
                          base_rates_seed0={k: fz(vv) for k, vv in r["pass_seed0_l50"].items()},
                          note32=("rule fails: e32 <= c32 or undefined" if r["rule32_fails"] else
                                  ("not well posed" if not r["well_posed32"] else "")))
                # adopted file: in_band carries the v2 notion (well posed under the majority rule), which is what
                # the pipeline's subset reporting reads; the v1 band flag is kept beside it
                nd.update(in_band_v1def=nd["in_band"], in_band=bool(r["well_posed32"]))
                if r["rule32_fails"]:                      # no bar exists above doing nothing: left out, listed in meta
                    excluded.append({"start_id": d["start_id"], "task": d["task"], "c32": nd["c32"], "e32": nd["e32"],
                                     "reason": "e32 <= c32 or undefined: no plan found beats the best constant plan"})
                    continue
            out_inst.append(nd)
        tot = {}
        for r in recs:
            if r["variant"] not in F.PROPOSAL_VARIANTS:
                continue
            for s, c in r["counts"].items():
                for kk, vv in c.items():
                    if isinstance(vv, (int, float)) and kk.startswith(("engine_", "closed_loop")):
                        tot[kk] = tot.get(kk, 0) + vv
        G, N = big_schedule(H)
        meta = dict(v1["meta"])
        meta.update({
            "version": "tasks v2, adopted by study protocol ",
            "excluded": excluded,
            "in_band": "in v2 files in_band = well_posed32; the v1 band flag at the v2 theta is in_band_v1def",
            "rule": {
                "c": "largest statistic of a feasible trajectory among the 2,625 constant plans (tax 0..20 x five funding "
                     "levels of road, fire, police; no macro) on the primary seed and the 20 best by J also on the eight "
                     "secondary seeds; if none feasible, the largest statistic regardless (c_feasible false)",
                "J": "statistic if feasible, else -1e9 + slack of the violated clause (dc.frontier.J)",
                "e": "largest nine-seed mean statistic among finalists feasible on all nine seeds; finalists = the 50 best by "
                     "J on the primary seed from each source: a pools, b pools with budget columns overwritten by the three "
                     "best constant settings, c closed-loop scripted builders under the two best settings (500 each; H = 24 "
                     f"only), d cross-entropy search on the engine ({G} generations of {N}, behaviour-pool init"
                     + (" and builder-pool init" if H == 24 else "") + ", tax and funding centred on the best constant setting)",
                "theta": "c + 0.5 (e - c); theta_l25, theta_l75 likewise",
                "well_posed": "e - c >= 4 x seed_sd (sd of the frontier plan's statistic over the nine seeds, ddof 1)",
                "best constant settings": "constant plans ranked by J on the primary seed; ties broken by the "
                                          "feasibility slack (larger first), then by grid order",
                "finalist ties": "the 50 best by J of a source, ties broken by the feasibility slack, then by position",
                "c_mean9 (diagnostic, not the rule)": "largest nine-seed mean statistic among the 20 constant plans "
                                                      "replayed on nine seeds that are feasible on all nine",
                "closed-loop seeds": "source c's builders play under a closed-loop seed of their own (as the builder pool "
                                     "does) with the task's forced events applied, then are replayed on the primary seed",
                "treasury": F.PREDICATES["treasury_rev"],
                "stat_sd": "spread of the statistic under the behaviour mix, as in tasks_H%d.json; recomputed for "
                           "treasury, whose statistic changed" % H,
                "base_rate_fit / base_rate_val / in_band": "the v1 definitions (behaviour-mix calibration trajectories, "
                     "first 600 / last 400 plans, band 0.2..0.5) at the v2 theta; the band is not part of the v2 rule",
                "base_rates": "pass shares at theta (primary seed for pools, b, c, constants; cross-entropy selected plan: "
                              "primary verdict and share of the eight secondary seeds)",
            },
            "seeds": {"primary": "seed_for('task', start_id, task, H)",
                      "secondary": "seed_for('task-secondary', start_id, task, H, k), k = 0..7",
                      "cem": "seed_for('tv2-cem', start_id, variant, H, init, B)",
                      "closed_loop": "seed_for('tv2-c-policy' | 'tv2-c-gen', start_id, H, forced_key, setting, j)"},
            "counts": tot, "instances_written": len(out_inst), "instances_missing": missing,
            **({"oracle": {"rule": "majority", "n_seeds": F.N_ORACLE, "seed_name": "task-oracle",
                           "value": "m32 = 16th largest of the 32 per-seed feasible statistics (minus infinity where "
                                    "infeasible); passes at theta exactly when >= 16 of 32 seeds pass (an exact 16 passes)",
                           "c32": "largest m32 among the 20 best constant plans (those replayed on the nine seeds)",
                           "e32": "m32 of the nine-seed rule's frontier plan (not re-selected on the oracle seeds)",
                           "theta": "theta = theta32(0.5) = c32 + 0.5 (e32 - c32); theta32_l25, theta32_l75 likewise; "
                                    "the nine-seed rule's fields keep their names (c, e, seed_sd, well_posed, theta_l25, "
                                    "theta_l50, theta_l75)",
                           "well_posed32": "e32 - c32 >= 6 x 1.2533 x seed_sd32 / sqrt(32), or e32 - c32 > 0 where seed_sd32 = 0",
                           "base_rate_fit / base_rate_val / in_band": "v1 definitions (calibration trajectories, single "
                                                                     "replays) at theta32(0.5)",
                           "base_rates32": "pass shares under the majority rule at theta32(0.5) (100-plan seeded subsets "
                                           "of each source; constants; cross-entropy selected plans)",
                           "base_rates_seed0": "the same plans on oracle seed 0 alone"}} if a.oracle else {}),
            "assembled_utc": dt.datetime.utcnow().isoformat(timespec="seconds"),
        })
        if a.tasks_v1:          # another first-thresholds file (the held-out extension): named, with the stage cache
            meta.update(tasks_v1_file=str(a.tasks_v1), stage_cache=str(CACHE / f"H{H}"))
        out_json = Path(a.json_out) if a.json_out else ROOT / "data" / f"tasks_v2_H{H}.json"
        out_json.write_text(json.dumps({"meta": meta, "instances": out_inst}, indent=1, default=float))
        print(f"wrote {out_json} ({len(out_inst)} instances)")
    if a.write_npz:
        for sid in sorted({i.start_id for i in sel}):
            arrays = {}
            for v in variants:
                d = work_dir(H) / f"{sid}__{v}"
                if not d.exists():
                    continue
                for s in STAGES + OPTIONAL_STAGES:
                    p = d / f"{s}.npz"
                    if p.exists():
                        for k2, arr in load_npz(p).items():
                            arrays[f"{v}__{s}__{k2}"] = arr
            if arrays:
                save_npz(CACHE / f"H{H}" / f"{sid}.npz", **arrays)
        print(f"wrote per-start npz files to {CACHE / f'H{H}'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--horizon", type=int, default=24)
    r.add_argument("--instances", default="all", help="'all' or a multiple of 5 (dc.audit.select_instances)")
    r.add_argument("--variants", default=",".join(F.PROPOSAL_VARIANTS))
    r.add_argument("--stages", default=",".join(STAGES))
    r.add_argument("--shard", default="0/1")
    r.add_argument("--starts", default="", help="comma-separated start ids (default: every start of the selection)")
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--remote", default="none", choices=("none", "host-b"))
    r.add_argument("--remote-workers", type=int, default=7)
    r.add_argument("--tasks-v1", default="", help="first-thresholds tasks file of the instances (default "
                   "data/tasks_H<H>.json; data/tasks_x_H24.json for the held-out extension, with WM2_TASKS_V2_CACHE "
                   "pointing at its own stage cache)")
    s = sub.add_parser("assemble")
    s.add_argument("--tasks-v1", default="", help="as for run")
    s.add_argument("--horizon", type=int, default=24)
    s.add_argument("--instances", default="all")
    s.add_argument("--variants", default=",".join(F.PROPOSAL_VARIANTS))
    s.add_argument("--write-json", action="store_true")
    s.add_argument("--write-npz", action="store_true")
    s.add_argument("--results-dir", default=str(ROOT / "results" / "tasks_v2"))
    s.add_argument("--json-out", default="")
    s.add_argument("--oracle", action="store_true", help="theta = theta32(0.5) (the majority rule); needs the oracle stage")
    a = ap.parse_args()
    if a.cmd == "run":
        return cmd_run(a)
    return cmd_assemble(a)


if __name__ == "__main__":
    sys.exit(main())
