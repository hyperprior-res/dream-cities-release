#!/usr/bin/env python3
"""Run the city audit (``dc.audit``): every (instance, method, budget, search seed), then the floors,
then the records, the selected plans, the pool statistics, the costs and the grader card.

Usage (from the repository root, PYTHONPATH=hpr-dream:code or as below):
  python code/scripts/run_audit.py --ckpt PATH --out results/audit/NAME [--instances all|N]
      [--budgets 1,10,100,1000] [--methods cem,random,best_of_n,random_verdict] [--search-seeds 0]
      [--floors residual,flip] [--pool-verdict-plans 50] [--residual-pool family|instance]
      [--device cuda:0] [--judge emulator|engine-identity|engine-seeds] [--workers 12]

The oracle comes from the tasks file: with ``meta.oracle`` (``{"rule": "majority", "n_seeds": 32, "seed_name":
"task-oracle"}``) every selected plan is judged by the majority over the instance's oracle seeds and the table and
card report the majority statistics (``table_majority``, ``oracle_majority_stats``) with the single-seed oracle
(oracle seed 0) as secondary rows; without it, by the primary seed as before.

``--out`` holds the small outputs; large intermediates go to ``--work`` (default
<cache>/audit/work/<name of --out>), and engine replays to the shared
engine cache (default <cache>/audit/engine_cache). Rerunning the same
command resumes per instance.
"""

from __future__ import annotations

import argparse
from typing import Dict, Tuple
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO / "hpr-dream"))

import hpr_dream as hd  # noqa: E402
from dc import audit as A  # noqa: E402
from dc import tasks as T  # noqa: E402
from dc.families import heldout_cty_of  # noqa: E402


NO_FLOORS = "none"


class NoFloorAudit(A.Audit):
    """``--floors none`` (no floor, so no floor cross-check either): phase 2 has nothing to compute. With ``--floors
    ""`` ``dc.audit.Audit`` still builds every instance's truth-seed residual pools in phase 2 (1,000 pool plans x 64
    truth seeds per start and forced events), which only the floors read; ``none`` skips them, and under the
    amendment-2 plan turns the floor cross-check off. Records, cards and tables are phase 1's alone. ``--floors ""``
    keeps its behaviour, so no existing run changes. Phase 1 also leaves out the economy rule's extra verdict rows (the
    100 pool rows with the largest search residual plus 25 at random, 8 judge samples each, per instance and pool),
    which only the residual floor reads; the shared verdict prefix (verdict-scored search, the behaviour table) is
    sampled as in ``dc.audit.Audit``, and the selected plans' verdicts are unchanged."""

    def _verdicts(self, inst, kind, eff, search_resid, s0):
        R = self.cfg.pool_verdict_plans
        n_pref = self._verd_prefix(inst, kind)
        mv = np.full((max(R, n_pref), A.K_VERDICT), np.nan)
        if n_pref:
            mv[:n_pref] = self._smargin(inst, self._shared("verd" if kind == "behaviour" else "bverd", inst, s0,
                                                           eff[:n_pref], A.K_VERDICT))
        return mv, 0

    @staticmethod
    def _pool(search, fourth, p8, m9, oracle_margin=None):
        """``dc.audit.Audit._pool``; where no pool row has 8-sample verdicts (random search alone, no floor), the
        verdict column is NaN and its summaries are None (the residual pools are written but no floor reads them)."""
        if np.isfinite(np.asarray(fourth, dtype=np.float64)).any():
            return A.Audit._pool(search, fourth, p8, m9, oracle_margin)
        mean9 = m9.mean(axis=1)
        pool = np.stack([search - mean9, np.full(len(search), np.nan)], axis=1)
        info = {"n_plans": int(len(search)), "n_verdict_rows": 0,
                "residual_against": f"mean engine margin over {m9.shape[1]} seeds",
                "residual_search": A._summ(pool[:, 0]), "residual_verdict": None,
                "engine_margin_seed_sd_mean": float(np.mean(m9.std(axis=1))),
                "engine_accept_rate_primary": float(np.mean(m9[:, 0] >= 0)),
                "engine_accept_rate_mean9": float(np.mean(mean9 >= 0)),
                "note": "no pool row has 8-sample verdicts (no floor reads them): no verdict residuals, no confusion counts"}
        if oracle_margin is not None:
            om = np.asarray(oracle_margin, dtype=np.float64)
            info["engine_accept_rate_oracle"] = float(np.mean(om[np.isfinite(om)] >= 0)) if np.isfinite(om).any() else None
        return pool, info

    def phase2(self, inst, p1i, resid_surr, flips, cross_surr=None) -> dict:
        if self.cfg.floors or self.cross_checked(inst):
            raise RuntimeError("NoFloorAudit runs only configurations without floors and without the floor cross-check")
        ec, jc = self.engine.counters(), self.judge.counters()
        costs = {"seconds": 0.0, "timing": {}, **A._delta(ec, ec), "engine_workers": getattr(self.engine, "workers", 0),
                 "oracle_distinct_replays": 0, "note": "no floors: phase 2 computes nothing"}
        out = {"tag": self.tag, "floors": {}, "oracle_cache": {"mean9_evals": 0, "primary_evals": 0}, "costs": costs}
        if self.cfg.floor_basis == "truth":
            costs.update(A._delta(jc, jc))
            out.update(truth_pools={}, truth_pool_info={}, truth_extra_verdict_rows={}, residual_pools_describe={})
        if self.cfg.majority:
            costs["oracle_distinct_replays_by_purpose"] = {}
            out["oracle_cache"] = {"mean9_evals": 0, "oracle_evals": 0, "by_method": {}}
        return out


def _ints(s: str):
    return tuple(int(x) for x in s.split(",") if x != "")


def _strs(s: str):
    return tuple(x for x in s.split(",") if x != "")


def git_state() -> dict:
    def run(*a):
        return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()
    mine = ["code/dc/audit.py", "code/scripts/run_audit.py", "code/scripts/gen_builder_pool.py"]
    return {"rev": run("rev-parse", "HEAD"), "dirty_files": run("status", "--porcelain").splitlines(),
            "file_sha256": {f: A._sha256_file(REPO / f) for f in mine}}


def make_judge(a, engine, oracle=None, tasks_sha256: str = ""):
    """The judge of ``--judge``. ``oracle``: the tasks file's majority oracle (``A.oracle_spec``) or None; the engine
    judges then use the oracle's seeds (identity) or stay off them (seeds)."""
    n = oracle["n_seeds"] if oracle else 0
    if a.judge == "emulator":
        if not a.ckpt:
            raise SystemExit("--ckpt is required for --judge emulator")
        return A.EmulatorJudge(a.ckpt, device=a.device, chunk=a.chunk, buckets=_ints(a.buckets),
                               compile_trunk=not a.no_compile, model_src=a.model_src, H=a.horizon,
                               fast=not a.no_fast)
    if a.judge == "engine-identity":
        return A.EngineIdentityJudge(engine, oracle_n=n, tasks_sha256=tasks_sha256 if n else "")
    if a.judge == "engine-seeds":
        return A.EngineSeedJudge(engine, oracle_n=n)
    raise SystemExit(f"unknown judge {a.judge}")


# ----------------------------------------------------------------------------------------------
# table, costs, projection
# ----------------------------------------------------------------------------------------------
def _e(est, bca=True) -> str:
    if not isinstance(est, dict) or "value" not in est:
        return "n/a"
    lo, hi = (est.get("bca_lo"), est.get("bca_hi")) if bca else (est["lo"], est["hi"])
    if lo is None or hi is None or (isinstance(lo, float) and np.isnan(lo)):
        lo, hi = est["lo"], est["hi"]
    return f"{est['value']:.3f} [{lo:.3f},{hi:.3f}]"


def table(card: dict, records, floors) -> str:
    fl = {(f["attacker"], f["scoring"], f["budget"]): f for f in card["noise_floors"]}
    un = {(u["attacker"], u["scoring"], u["budget"]): u for u in card["unlucky_share"]} \
        if isinstance(card["unlucky_share"], list) else {}
    L = ["method (scoring)       B     n  hackability [BCa]      judge acc  eng acc  unlucky  "
         + "".join(f"{k} floor [BCa]          excess over {k} [BCa]   " for k in floors)
         + "emu steps/row  eng months/row"]
    for e in card["hackability_curve"]:
        k = (e["attacker"], e["scoring"], e["budget"])
        rs = [r for r in records if (r["attacker"], r["scoring"], r["budget"]) == k]
        ga = np.mean([r["grader_p"] >= A.ACCEPT_P for r in rs])
        oa = np.mean([r["oracle_accept"] for r in rs])
        u = un.get(k, {}).get("unlucky_share", {})
        uv = u.get("value") if isinstance(u, dict) else None
        us = f"{uv:.3f}" if uv is not None and np.isfinite(uv) else "-"
        line = f"{rs[0]['method'] + ' (' + e['scoring'] + ')':20s} {e['budget']:5d} {e['n_rows']:5d}  {_e(e['hackability']):21s}  " \
               f"{ga:8.3f}  {oa:7.3f}  {us:>7s}  "
        for f in floors:
            s = fl[k].get(f"{f}_surrogate", {})
            line += f"{_e(s.get('hackability')):21s}  {_e(s.get('excess')):24s}  "
        line += f"{np.mean([r['emu_month_steps'] for r in rs]):13,.0f}  {np.mean([r['engine_city_months'] for r in rs]):14,.0f}"
        L.append(line)
    return "\n".join(L)


def oracle_majority_stats(records, n_boot: int = 2000, seed: int = 0) -> list:
    """Per (attacker, scoring, budget) group of records judged by the majority oracle, with the instrument's
    estimators (cluster bootstrap over the records' clusters, BCa, the card's seed): the emulator's and the
    oracle's acceptance rates, the mean oracle pass share of the plans the emulator accepted, the mean of
    (emulator pass share - oracle pass share) over the selected plans, and the secondary single-seed oracle (oracle
    seed 0): its acceptance rate and the hackability under it."""
    kw = dict(n_boot=n_boot, seed=seed, bca=True)
    out = []
    for k in sorted({(r["attacker"], r["scoring"], r["budget"]) for r in records}):
        rs = [r for r in records if (r["attacker"], r["scoring"], r["budget"]) == k]
        cl = [r["cluster"] for r in rs]
        gp = np.array([r["grader_p"] for r in rs], dtype=np.float64)
        ga = gp >= A.ACCEPT_P
        oa = np.array([r["oracle_accept"] for r in rs], dtype=bool)
        sh = np.array([r["oracle_share"] for r in rs], dtype=np.float64)
        o0 = np.array([r["oracle_accept_seed0"] for r in rs], dtype=bool)
        e = {"attacker": k[0], "scoring": k[1], "budget": int(k[2]), "n_rows": len(rs),
             "emulator_accept": hd.conditional_mean(ga, None, cl, **kw).as_dict(),
             "oracle_accept": hd.conditional_mean(oa, None, cl, **kw).as_dict(),
             "oracle_share_given_emulator_accept": (hd.conditional_mean(sh, ga, cl, **kw).as_dict() if ga.any()
                                                    else {"status": "the emulator accepted no selected plan"}),
             "emulator_share_minus_oracle_share": hd.excess(gp, sh, cl, **kw).as_dict(),
             "single_seed_oracle_accept": hd.conditional_mean(o0, None, cl, **kw).as_dict(),
             "single_seed_hackability": hd.hackability(ga, o0, cl, **kw).as_dict(),
             "definitions": {"emulator_share": "grader_p, the emulator's pass share of 8 samples (verdict-scored search: "
                                               "the verdict it selected on)",
                             "oracle_share": "pass share over the oracle's seeds", "single_seed": "oracle seed 0 alone"}}
        out.append(e)
    return out


def table_majority(card: dict, records, floors, ostats=None) -> str:
    """The run's table under the majority oracle: per group hackability, the acceptance rates, the oracle's pass
    share where the emulator accepts, the emulator-minus-oracle pass share, both floors and the excess over each;
    then the single-seed oracle (seed 0) as secondary rows."""
    ostats = ostats if ostats is not None else oracle_majority_stats(records)
    os_ = {(o["attacker"], o["scoring"], o["budget"]): o for o in ostats}
    fl = {(f["attacker"], f["scoring"], f["budget"]): f for f in card["noise_floors"]}
    L = ["method (scoring)          B     n  hackability [BCa]      emu acc  orc acc  orc share | emu acc [BCa]  "
         "emu - orc share [BCa]     "
         + "".join(f"{k} floor [BCa]         excess over {k} [BCa]  " for k in floors)
         + "emu steps/row  eng months/row"]
    for e in card["hackability_curve"]:
        k = (e["attacker"], e["scoring"], e["budget"])
        rs = [r for r in records if (r["attacker"], r["scoring"], r["budget"]) == k]
        o = os_[k]
        line = (f"{rs[0]['method'] + ' (' + e['scoring'] + ')':24s} {e['budget']:5d} {e['n_rows']:5d}  "
                f"{_e(e['hackability']):21s}  {o['emulator_accept']['value']:7.3f}  {o['oracle_accept']['value']:7.3f}  "
                f"{_e(o['oracle_share_given_emulator_accept']):28s}  {_e(o['emulator_share_minus_oracle_share']):24s}  ")
        for f in floors:
            s = fl[k].get(f"{f}_surrogate", {})
            line += f"{_e(s.get('hackability')):21s}  {_e(s.get('excess')):24s}  "
        line += f"{np.mean([r['emu_month_steps'] for r in rs]):13,.0f}  {np.mean([r['engine_city_months'] for r in rs]):14,.0f}"
        L.append(line)
    L.append("secondary: the single-seed oracle (oracle seed 0 alone)")
    L.append("method (scoring)          B     n  hackability [BCa]      orc acc")
    for e in card["hackability_curve"]:
        k = (e["attacker"], e["scoring"], e["budget"])
        o = os_[k]
        rs = [r for r in records if (r["attacker"], r["scoring"], r["budget"]) == k]
        L.append(f"{rs[0]['method'] + ' (' + e['scoring'] + ')':24s} {e['budget']:5d} {e['n_rows']:5d}  "
                 f"{_e(o['single_seed_hackability']):21s}  {o['single_seed_oracle_accept']['value']:7.3f}")
    return "\n".join(L)


def _excludes_zero(e: dict) -> bool:
    lo, hi = e.get("bca_lo"), e.get("bca_hi")
    if lo is None or hi is None or not np.isfinite(lo) or not np.isfinite(hi):
        lo, hi = e["lo"], e["hi"]
    return bool(lo > 0 or hi < 0)


def floor_summary(card: dict) -> dict:
    """Per floor and scoring: groups whose excess interval (BCa) excludes 0, mean excess, largest |excess|."""
    out = {}
    for floor, scoring in (("residual", "margin"), ("flip", "verdict"), ("flip", "margin"), ("residual", "verdict")):
        ex = [(f["attacker"], f["budget"], f[f"{floor}_surrogate"]["excess"]) for f in card["noise_floors"]
              if f["scoring"] == scoring and "excess" in f.get(f"{floor}_surrogate", {})]
        if not ex:
            continue
        v = np.array([e["value"] for _, _, e in ex])
        j = int(np.argmax(np.abs(v)))
        out[f"{floor}|{scoring}"] = {
            "groups": len(ex), "excludes_zero": int(sum(_excludes_zero(e) for _, _, e in ex)),
            "excluding_groups": [f"{a} B={b} {e['value']:+.3f}" for a, b, e in ex if _excludes_zero(e)],
            "mean_excess": float(v.mean()), "largest_abs_excess": float(v[j]),
            "largest_at": f"{ex[j][0]} B={ex[j][1]}"}
    return out


def flip_closed_form_family(records, p1, instances, flips, n_beh) -> list:
    """Flip closed form for verdict-scored random shooting with the per-instance base rate (the oracle's verdicts of
    the instance's behaviour plans: the primary seed's, or the majority oracle's) and confusion rates pooled within
    the task family."""
    by = {i.key: i for i in instances}
    out = []
    vs = [r for r in records if r["attacker"] == "random_shooting" and r["scoring"] == "verdict"]
    for B in sorted({r["budget"] for r in vs}):
        rs = [r for r in vs if r["budget"] == B]
        fl, hk, cl = [], [], []
        for r in rs:
            i = by[r["instance"]]
            pi = float(np.mean(np.asarray(p1[i.key]["behaviour"]["oracle_margin"][:n_beh]) >= 0))
            fr = flips["by_task"][i.task]
            fl.append(hd.noise_floor_flip(pi, fr["fp"], fr["fn"], B))
            hk.append(float(r["grader_p"] >= A.ACCEPT_P and not r["oracle_accept"]))
            cl.append(r["cluster"])
        out.append({"attacker": "random_shooting", "scoring": "verdict", "budget": int(B),
                    "floor": hd.excess(fl, np.zeros(len(fl)), cl, bca=True).as_dict(),
                    "excess": hd.excess(hk, fl, cl, bca=True).as_dict(),
                    "definition": "mean over instances of (1-(1-a)^B)(1-pi_i)fp_f/a, a = pi_i(1-fn_f)+(1-pi_i)fp_f; "
                                  "pi_i per instance, fp_f and fn_f pooled within the instance's task family"})
    return out


def side_by_side(ce: dict, ca: dict) -> str:
    fe = {(f["attacker"], f["scoring"], f["budget"]): f for f in ce["noise_floors"]}
    fa = {(f["attacker"], f["scoring"], f["budget"]): f for f in ca["noise_floors"]}
    L = ["method (scoring)          B     n  hackability [BCa]      economy floor [BCa]    excess [BCa]             "
         "paired floor [BCa]     excess [BCa]"]
    for e in ce["hackability_curve"]:
        k = (e["attacker"], e["scoring"], e["budget"])
        re_, ra = fe[k]["residual_surrogate"], fa[k]["residual_surrogate"]
        L.append(f"{e['attacker'] + ' (' + e['scoring'] + ')':24s} {e['budget']:5d} {e['n_rows']:5d}  {_e(e['hackability']):21s}  "
                 f"{_e(re_.get('hackability')):21s}  {_e(re_.get('excess')):24s} {_e(ra.get('hackability')):21s}  "
                 f"{_e(ra.get('excess'))}")
    return "\n".join(L)


def plan_design(audit: A.Audit, extra: Dict[str, Dict[str, int]], H: int = 24) -> dict:
    """Exact judge month-steps of an audit's plan by component, given the economy verdict rows each instance
    samples beyond its group's shared prefix (``extra[key][kind]``)."""
    c = audit.cfg
    S = len(c.search_seeds)
    comp = {"random-search proposals (K=2)": 0, "shared 8-sample verdicts, behaviour plans": 0,
            "best-of-n proposals (K=2)": 0, "shared 8-sample verdicts, builder plans": 0, "CEM (K=2)": 0,
            "economy verdict rows, behaviour plans": 0, "economy verdict rows, builder plans": 0,
            "selected-plan verdicts (8 samples)": 0}
    if any("cem_seeded" in audit.inst_plan(i) for i in audit.instances):
        comp["seeded CEM (K=2) beyond its first generation (the shared proposals)"] = 0
    seen = set()
    R = c.pool_verdict_plans
    for i in audit.instances:
        plan = audit.inst_plan(i)
        g = (i.start_id, audit._share_key(i))
        if g not in seen:
            seen.add(g)
            grp = [j for j in audit.instances if (j.start_id, audit._share_key(j)) == g]
            comp["random-search proposals (K=2)"] += max(audit._need_props(j) for j in grp) * A.K_SEARCH * S * H
            comp["shared 8-sample verdicts, behaviour plans"] += audit._verd_prefix(i, "behaviour") * A.K_VERDICT * H
            bon = [j for j in grp if "best_of_n" in audit.inst_plan(j)]
            if bon:
                nb = max(max(max(audit.inst_plan(j)["best_of_n"]) for j in bon), R)
                comp["best-of-n proposals (K=2)"] += nb * A.K_SEARCH * S * H
            comp["shared 8-sample verdicts, builder plans"] += audit._verd_prefix(i, "builders") * A.K_VERDICT * H
        if "cem" in plan:
            comp["CEM (K=2)"] += sum(plan["cem"]) * A.K_SEARCH * S * H
        if "cem_seeded" in plan:
            comp["seeded CEM (K=2) beyond its first generation (the shared proposals)"] += sum(
                B - A.cem_seeded_first(B) for B in plan["cem_seeded"]) * A.K_SEARCH * S * H
        e = extra.get(i.key, {})
        comp["economy verdict rows, behaviour plans"] += e.get("behaviour", 0) * A.K_VERDICT * H
        comp["economy verdict rows, builder plans"] += e.get("builders", 0) * A.K_VERDICT * H
        n_sel = e.get("selected", sum(len(b) for b in plan.values()) * S)     # measured rollouts, else rows
        comp["selected-plan verdicts (8 samples)"] += n_sel * A.K_VERDICT * H
    return {"components": comp, "total": int(sum(comp.values()))}


def plan_design_report(audit, res, universe, judge, engine, work, costs) -> dict:
    """The design count of this run (checked against the judge's counter) and of a full checkpoint (every instance of the tasks file)
    under the same plan with the default pool sizes; for the full checkpoint every non-cross-checked instance is
    charged the economy rule's 125 verdict rows per pool, an upper bound (rows already in the shared prefix are
    not sampled again)."""
    extra = {k: {**d["extra_verdict_rows"], "selected": d.get("selected_verdict_rollouts", 0)} for k, d in res["p1"].items()}
    for k, d2 in res["p2"].items():          # verdict rows sampled for the truth-seed pools (economy rule), phase 2
        for kind, v in d2.get("truth_extra_verdict_rows", {}).items():
            extra[k][kind] = extra[k].get(kind, 0) + v
    this = plan_design(audit, extra)
    # what this invocation's instances rolled out: the shared pool samples they computed (none when re-read from
    # the sample store, e.g. on a re-score) plus their own (CEM, economy rows, selected plans)
    shared_lines = ("random-search proposals (K=2)", "shared 8-sample verdicts, behaviour plans", "best-of-n proposals (K=2)", "shared 8-sample verdicts, builder plans")
    computed = sum(d["costs"].get("shared_month_steps_computed", 0) for d in res["p1"].values())
    this["rolled_out"] = int(sum(v for k, v in this["components"].items() if k not in shared_lines) + computed)
    this["shared_computed"] = int(computed)
    full_cfg = A.amendment2_config(search_seeds=audit.cfg.search_seeds, H=audit.cfg.H, oracle=audit.cfg.oracle,
                                   oracle_seeds=audit.cfg.oracle_seeds)
    full = A.Audit(full_cfg, universe, judge, engine, audit.pools, Path(work) / "_design_only", log=lambda s: None,
                   universe=universe)
    n_ec, R = full_cfg.economy_top + full_cfg.economy_random, full_cfg.pool_verdict_plans
    ub = {i.key: {"behaviour": 0 if full._verd_prefix(i, "behaviour") >= R else n_ec,
                  "builders": 0 if ("best_of_n" not in full.inst_plan(i) or full._verd_prefix(i, "builders") >= R)
                  else n_ec} for i in universe}
    fc = plan_design(full, ub)
    rate = costs.get("judge_month_steps_per_s") if judge.name == "emulator" else None
    if rate:
        fc["rate"] = rate
        fc["hours_at_this_run_rate"] = fc["total"] / rate / 3600
    fc["assumption"] = ("economy verdict rows charged 125 per pool to every instance whose (start, forced events) group "
                        "has no 1,000-row verdict prefix (an upper bound: kept rows already inside a shorter prefix are "
                        "not sampled again); instances in a group with a cross-checked member need none")
    fc["instances_charged_economy_rows"] = {k: sum(1 for v in ub.values() if v[k]) for k in ("behaviour", "builders")}
    return {"this_run": this, "full_checkpoint": fc}


RATE_REF = A.REPO / "results" / "audit" / "engine_reference" / "r3_A_instance" / "costs.json"   # 16 local + 22 host-b


def engine_costs_majority(res: dict, cfg: A.AuditConfig, instances, universe, audit) -> dict:
    """Engine work under the majority oracle.

    ``this_run_by_purpose``: the distinct (plan, seed) replays each instance requested, cached or not, attributed to
    the purpose that asked first, summed over instances and the two phases (a pair requested in both phases counts
    twice, as in ``oracle_distinct_replays``).

    ``full_checkpoint``: the replays of one ladder checkpoint under the amendment-2 plan (every instance of the tasks
    file), in city-months, for each flip scope, split into the part every checkpoint needs anew and the part that
    depends only on the pools, the instances and the seeds (computed once, then read from the engine cache):
      per checkpoint: the real attacks' selected plans on the oracle and the nine seeds (rows x (n + 9), an upper
        bound: equal plans are replayed once); the residual floors' cross-entropy candidates on the nine seeds (every
        instance, and those of the fully paired cross-check); the floors' selected plans on the oracle seeds; under
        flip scope "all" the flip floor's cross-entropy candidates on the oracle seeds (the flip surrogate flips the
        oracle's verdict of every candidate) and their selections' nine-seed margins (a diagnostic);
      shared: the residual pools' first 1,000 behaviour and builder plans on the nine seeds; on the oracle seeds the
        behaviour plans the flip floor's random shooting scores (up to the largest budget of verdict-scored search on
        the instance under scope "verdict", of any random shooting under "all"; at least the behaviour table's rows)
        and, under "all", the best-of-n instances' first 1,000 builder plans.
    Cross-entropy candidates per instance: this run's measured distinct counts where its budgets are the plan's (the
    flip floor's only from a run with scope "all"), otherwise the upper bound (every candidate distinct)."""
    H, n = cfg.H, cfg.oracle_seeds
    by: Dict[str, int] = {}
    for c in res["costs"]:
        for ph in ("phase1", "phase2"):
            for k, v in c[ph].get("oracle_distinct_replays_by_purpose", {}).items():
                by[k] = by.get(k, 0) + int(v)
    out = {"this_run_by_purpose": dict(sorted(by.items())), "this_run_total": int(sum(by.values()))}
    cem9, cemo = [], []
    for i in instances:
        bm = res["p2"][i.key].get("oracle_cache", {}).get("by_method", {})
        e = bm.get(f"cem_s{cfg.search_seeds[0]}")
        if e is None:
            continue
        n_res = ("residual" in cfg.floors) + audit.cross_checked(i)
        if n_res:
            cem9.append(e.get("truth_search_evals", e.get("nine_seed_mean_evals", 0)) / n_res)
        if "flip" in cfg.floors and cfg.flip_scope == "all":
            cemo.append(e["oracle_evals"])
    S_ = len(cfg.search_seeds)
    full_cfg = A.amendment2_config(search_seeds=cfg.search_seeds, H=H, oracle="majority", oracle_seeds=n)
    full = A.Audit(full_cfg, universe, audit.judge, audit.engine, audit.pools, Path(audit.work) / "_design_only",
                   log=lambda s: None, universe=universe)
    plans = {i.key: full.inst_plan(i) for i in universe}
    rows = sum(len(b) for pl in plans.values() for b in pl.values()) * S_
    n_cem = sum("cem" in pl for pl in plans.values())
    n_x = sum(full.cross_checked(i) for i in universe)
    n_bon = sum("best_of_n" in pl for pl in plans.values())
    n_res_graders = sum(1 + full.cross_checked(i) for i in universe)          # residual floor (+ cross-check) per instance
    R, Bmax, nB = full_cfg.pool_verdict_plans, max(full_cfg.budgets), len(full_cfg.budgets)
    sum_b = sum(full_cfg.budgets)
    if tuple(cfg.budgets) != tuple(full_cfg.budgets):       # measured counts of other budgets do not transfer
        cem9, cemo = [], []
    m9 = float(np.mean(cem9)) if cem9 else float(sum_b)       # else the upper bound: every candidate distinct
    mo = float(np.mean(cemo)) if cemo else float(sum_b + 2 * nB)
    truth = cfg.floor_basis == "truth"
    common = {"real selected plans, oracle + nine seeds (upper bound)": int(rows * (n + 9) * H),
              "residual floors' selected plans, oracle seeds (upper bound)": int(n_res_graders * 3 * nB * S_ * n * H)}
    if truth:
        common[f"residual floors' CEM candidates, truth seeds 0..{cfg.truth_cand_seeds - 1}"] = int(
            round((n_cem + n_x) * m9 * cfg.truth_cand_seeds * H))
        common[f"residual floors' CEM selections, truth seeds {A.TRUTH_A}..{A.TRUTH_N - 1} (upper bound)"] = int(
            (n_cem + n_x) * nB * S_ * (A.TRUTH_N - A.TRUTH_A) * H)
    else:
        common["residual floors' CEM candidates, nine seeds"] = int(round((n_cem + n_x) * m9 * 9 * H))
    pool9 = {"pool rows, nine seeds (behaviour 1,000 per instance; builders 1,000 on best-of-n instances; upper bound)":
             int((len(universe) + n_bon) * R * 9 * H)}
    if truth:      # truth seeds belong to (start, forced events): one replay serves the tasks of a start
        groups: Dict[tuple, bool] = {}
        for i in universe:
            g = (i.start_id, i.forced_key)
            groups[g] = groups.get(g, False) or "best_of_n" in plans[i.key]
        pool9[f"pool rows, {A.TRUTH_N} truth seeds per (start, forced events) (behaviour 1,000; builders 1,000 where "
              f"best-of-n runs; upper bound)"] = int(sum(R * (1 + b) for b in groups.values()) * A.TRUTH_N * H)
    rv_max = sum(max(max(pl.get("random_verdict", (0,))), full_cfg.beh_rows) for pl in plans.values())
    scopes = {
        "verdict": {"per_checkpoint": dict(common), "shared": {
            **pool9, "behaviour plans up to the largest verdict-scored budget, oracle seeds (upper bound)":
            int(rv_max * n * H)}},
        "all": {"per_checkpoint": {
            **common, "flip floor's CEM candidates and floors' CEM selections, oracle seeds": int(round(n_cem * mo * n * H)),
            "flip floor's selected CEM plans, nine seeds (diagnostic)": int(n_cem * nB * S_ * 9 * H)}, "shared": {
            **pool9, "behaviour plans 1..1,000, oracle seeds (upper bound)": int(len(universe) * max(Bmax, full_cfg.beh_rows) * n * H),
            "builder plans 1..1,000 on best-of-n instances, oracle seeds (upper bound)": int(n_bon * Bmax * n * H)}}}
    rate = None
    if RATE_REF.exists():
        rate = json.loads(RATE_REF.read_text())["summary"].get("engine_city_months_per_s")
    for sc in scopes.values():
        sc["per_checkpoint_city_months"] = int(sum(sc["per_checkpoint"].values()))
        sc["shared_city_months"] = int(sum(sc["shared"].values()))
        if rate:
            sc["hours_per_checkpoint_at_reference_rate"] = sc["per_checkpoint_city_months"] / rate / 3600
            sc["hours_shared_once_at_reference_rate"] = sc["shared_city_months"] / rate / 3600
    fc = {"by_flip_scope": scopes, "this_run_flip_scope": cfg.flip_scope,
          "basis": {"instances": len(universe), "rows": rows, "cem_instances": n_cem, "cross_check_instances": n_x,
                    "best_of_n_instances": n_bon, "oracle_seeds": n,
                    "cem_distinct_candidates_per_residual_grader": m9, "cem_distinct_oracle_evals_per_instance": mo,
                    "cem_counts": ("measured on this run's instances" if cem9 else "upper bound (sum of budgets)")
                                  + ("; flip floor's measured" if cemo else "; flip floor's upper bound")}}
    if rate:
        fc["rate_reference"] = {"file": str(RATE_REF.relative_to(A.REPO)), "city_months_per_s": rate,
                                "workers": "16 local + 22 host-b (that run's configuration)"}
    out["full_checkpoint"] = fc
    return out


def costs_summary(res: dict, cfg: A.AuditConfig, instances, judge, engine, universe=None) -> dict:
    """Costs of the run from its phase files, and (uniform plans) projections to every instance of the tasks file
    (``universe``: its instances; default this run's)."""
    universe = list(universe) if universe is not None else list(instances)
    n_all, n_sf_all = len(universe), len({(i.start_id, i.forced_key) for i in universe})
    H = cfg.H
    p1c = [c["phase1"] for c in res["costs"]]
    p2c = [c["phase2"] for c in res["costs"]]
    jm = sum(c.get("judge_month_steps", 0) for c in p1c + p2c)          # phase 2: verdict rows of truth-seed pools
    js = sum(c.get("judge_seconds", 0.0) for c in p1c + p2c)
    pad = sum(c.get("judge_padded_month_steps", 0) for c in p1c + p2c)
    er = sum(c.get("engine_replays", 0) for c in p1c + p2c)
    er_remote = sum(c.get("engine_replays_remote", 0) for c in p1c + p2c)
    es = sum(c.get("engine_seconds", 0.0) for c in p1c + p2c)
    t1 = [c["seconds"] for c in p1c]
    t2 = [c["seconds"] for c in p2c]
    timing = {}
    for c in p1c + p2c:
        for k, v in c["timing"].items():
            timing.setdefault(k, []).append(v)
    out = {
        "instances_in_this_invocation_phase_files": len(instances),
        "judge": judge.describe(),
        "judge_month_steps_computed": int(jm), "judge_padded_month_steps": int(pad), "judge_seconds": js,
        "judge_month_steps_per_s": jm / js if js > 0 else None,
        "engine_replays": int(er), "engine_replays_remote": int(er_remote),
        "engine_city_months_replayed": int(er * H), "engine_seconds": es,
        "engine_city_months_per_s": er * H / es if es > 0 else None,
        "engine_workers": sorted({c.get("engine_workers", -1) for c in p1c + p2c}),
        "seconds_phase1_per_instance_mean": float(np.mean(t1)), "seconds_phase2_per_instance_mean": float(np.mean(t2)),
        "seconds_per_instance_by_step_mean": {k: float(np.mean(v)) for k, v in sorted(timing.items())},
        "note": "computed from the per-instance phase files: counts and seconds of the invocation that computed "
                "each instance (a resumed run keeps the original instances' costs; shared per-start samples computed "
                "by a killed invocation and reused are in no phase file); engine replays are disk-cache misses",
    }
    # wall clock per instance per method (mean over instances): the method's search, its floor attacks,
    # its share (by rows) of the selected-plan verdicts, and the per-start scores it needs (random
    # shooting: the K = 2 proposal scores; verdict-scored: the 8-sample pool verdicts; best-of-n: the
    # builder scores). The pool statistics (8-sample verdicts and engine margins of the residual plans)
    # are listed separately.
    n_rows = len(cfg.methods) * len(cfg.budgets) * len(cfg.search_seeds)
    per_m = {}
    for m in cfg.methods:
        own = {"random": ["proposals"], "random_verdict": ["pool_verdicts"], "best_of_n": ["builder_scores"]}.get(m, [])
        vals = []
        for c1, c2 in zip(p1c, p2c):
            t = sum(v for k, v in c1["timing"].items() if k.startswith(f"attack_{m}_"))
            t += sum(c1["timing"].get(k, 0.0) for k in own)
            t += (c1["timing"].get("verdict_selected", 0.0) + c1["timing"].get("engine_selected", 0.0)) \
                * len(cfg.budgets) * len(cfg.search_seeds) / n_rows
            if A.FLOOR_METHOD[m] == m:
                t += sum(v for k, v in c2["timing"].items() if k.startswith(f"floors_{m}_"))
            vals.append(t)
        per_m[m] = float(np.mean(vals))
    out["wall_seconds_per_instance_by_method"] = per_m
    out["wall_seconds_per_instance_pool_statistics"] = float(np.mean(
        [c["timing"].get("pool_verdicts", 0.0) * ("random_verdict" not in cfg.methods) + c["timing"].get("pool_engine", 0.0)
         for c in p1c]))
    # exact judge month-steps of this run's design (checked against the counter) and projections
    starts_forced = {(i.start_id, i.forced_key) for i in instances}
    S = len(cfg.search_seeds)
    Bmax, sumB = max(cfg.budgets), sum(cfg.budgets)

    def design(methods, pvp):
        n_prop = max(pvp, Bmax if {"random", "random_verdict"} & set(methods) else 0,
                     max(A.cem_seeded_first(B) for B in cfg.budgets) if "cem_seeded" in methods else 0)
        n_v = max(pvp, Bmax if "random_verdict" in methods else 0)
        bon = "best_of_n" in methods
        shared = (n_prop * A.K_SEARCH * S + n_v * A.K_VERDICT
                  + ((max(Bmax, pvp) * A.K_SEARCH * S + pvp * A.K_VERDICT) if bon else 0)) * H
        rows = len(methods) * len(cfg.budgets) * S
        seeded = sum(B - A.cem_seeded_first(B) for B in cfg.budgets) * A.K_SEARCH * S if "cem_seeded" in methods else 0
        per_inst = ((sumB * A.K_SEARCH * S if "cem" in methods else 0) + seeded + rows * A.K_VERDICT) * H
        return shared, per_inst, rows

    od0 = [c1.get("oracle_distinct_replays", 0) + c2.get("oracle_distinct_replays", 0) for c1, c2 in zip(p1c, p2c)]
    out["oracle_distinct_replays_per_instance_mean"] = float(np.mean(od0))
    if cfg.plan != "uniform" or cfg.verdict_rows != "all":      # per-instance plans: see plan_design
        out["judge_month_steps_design_this_run"] = None
        out["judge_month_steps_design_matches_counter"] = None
        out["projection_full"] = {}
        return out
    shared, per_inst, rows_i = design(cfg.methods, cfg.pool_verdict_plans)
    sel = sum(res["p1"][i.key].get("selected_verdict_rollouts", rows_i) for i in instances)   # measured: plans
    shc = [res["p1"][i.key]["costs"].get("shared_month_steps_computed") for i in instances]
    sh_run = sum(shc) if all(x is not None for x in shc) else shared * len(starts_forced)    # re-read when re-scoring
    d_run = sh_run + (per_inst - rows_i * A.K_VERDICT * H) * len(instances) + sel * A.K_VERDICT * H
    out["judge_month_steps_design_this_run"] = int(d_run)
    out["judge_month_steps_design_matches_counter"] = bool(d_run == jm) if len(res["costs"]) == len(instances) else None
    # engine work of the oracle side (verdicts, residual plans, floors), measured: distinct (plan, seed)
    # replays requested per instance, whether or not the disk cache already held them
    od = [c1.get("oracle_distinct_replays", 0) + c2.get("oracle_distinct_replays", 0) for c1, c2 in zip(p1c, p2c)]
    out["oracle_distinct_replays_per_instance_mean"] = float(np.mean(od))
    rate_j = out["judge_month_steps_per_s"] if judge.name == "emulator" else None
    rate_e = out["engine_city_months_per_s"]
    proj = {}
    variants = [("this_run_methods", tuple(cfg.methods))]
    four = ("cem", "random", "best_of_n", "random_verdict")         # the protocol methods (not cem_seeded)
    if set(cfg.methods) != set(four):
        variants.append(("all_four_methods", four))
    for label, methods in variants:
        sh, pi, rows = design(methods, cfg.pool_verdict_plans)
        jm_full = sh * n_sf_all + pi * n_all
        p = {"methods": list(methods), "budgets": list(cfg.budgets), "pool_verdict_plans": cfg.pool_verdict_plans,
             "judge_month_steps": int(jm_full),
             "instances": n_all, "judge_formula": f"per (start, forced events) {sh:,} x {n_sf_all} + per instance {pi:,} x {n_all}"}
        if tuple(methods) == tuple(cfg.methods):
            em_full = float(np.mean(od)) * H * n_all
            p["engine_city_months_oracle_side_no_cache"] = int(em_full)
            p["engine_formula"] = f"this run's mean distinct oracle-side replays per instance x {H} x {n_all}"
            if rate_e:
                p["engine_hours_at_measured_rate"] = em_full / rate_e / 3600
        if rate_j:
            p["judge_hours_at_measured_rate"] = jm_full / rate_j / 3600
        proj[label] = p
    out["projection_full"] = proj
    return out


RULE_TEXT = {
    "family": "family pool (hpr_dream ResidualFamily, per-instance median and MAD, zero-MAD rule), first {rows} rows",
    "instance": "per-instance pool, fully paired, first {rows} rows",
    "economy": "economy per-instance pool: search residual on {rows} rows, verdict residual on {top} rows with the "
               "largest search residual plus {rnd} at random, the rest imputed from the nearest kept row",
    "family-shrunk": "family pool with each log-MAD shrunk toward the family mean log-MAD, first {rows} rows",
    "family-centred": "family pool centred per instance, not rescaled, first {rows} rows",
}


def residual_pool_cost(cfg: dict, H: int = 24, n_sf: int = 80, n_inst: int = 200) -> dict:
    """Residual-pool cost of a rule for a real emulator, per checkpoint: emulator month-steps for the 8-sample
    verdicts of the pool rows (per start and forced events; the K = 2 search scores of the first 1,000 behaviour
    and builder rows exist anyway where random search and best-of-n run) and engine city-months for the nine-seed
    means of the pool rows (per instance: the seeds belong to the task)."""
    cfg = {**A.AuditConfig().to_dict(), **cfg}
    rule, rows = cfg["residual_pool"], cfg["residual_rows"] or cfg["pool_verdict_plans"]
    v_rows = cfg["economy_top"] + cfg["economy_random"] if rule == "economy" else rows
    kinds = len({A.POOL_OF[m] for m in cfg["methods"]})
    emu = v_rows * kinds * A.K_VERDICT * H * n_sf
    eng = rows * kinds * (1 + cfg["n_secondary"]) * H * n_inst
    return {"verdict_rows_per_pool": v_rows, "rows_per_pool": rows, "pools": kinds,
            "emulator_month_steps": int(emu), "engine_city_months": int(eng)}


def summarise(specs: str, out_md: str) -> None:
    rate_emu = None
    pilot = A.REPO / "results" / "audit" / "pilot2_small" / "costs.json"
    if pilot.exists():
        rate_emu = json.loads(pilot.read_text())["summary"].get("judge_month_steps_per_s")
    first = json.loads((Path(specs.split(",")[0].split("=", 1)[1]) / "card.json").read_text())["counts"]
    L = [f"# Engine reference: the engine judging itself on fresh seeds, {first['instances']} instances", "",
         "Generated by `code/scripts/run_audit.py --summarise` from the run directories listed per section. "
         f"Excess = measured hackability minus the floor, paired cluster bootstrap over the {first['clusters']} families, BCa 95 % "
         "interval; 'excludes 0' uses the BCa limits. The real attacks (hackability columns) are identical across "
         "rules; only the residual floor changes. Flip floor in every run: per-instance base rate, confusion rates "
         "pooled within the task family (first 125 behaviour plans per instance).", ""]
    summ_rows = []
    sections = []
    for spec in specs.split(","):
        label, d = spec.split("=", 1)
        d = Path(d)
        card = json.loads((d / "card.json").read_text())
        rc = json.loads((d / "config.json").read_text())
        cfg = {**A.AuditConfig().to_dict(), **rc["config"]}
        fs = card.get("floor_summary") or floor_summary(card)
        rm = fs["residual|margin"]
        fv = fs.get("flip|verdict")
        keys = [k.split("|") for k in rc["instances"]]                 # start|task|H of every instance of the run
        n_inst, n_sf = len(keys), len({(k[0], bool(T.forced_for(k[1]))) for k in keys})
        cost = residual_pool_cost(cfg, n_sf=n_sf, n_inst=n_inst)
        summ_rows.append(f"| {label} | {rm['excludes_zero']} of {rm['groups']} | {rm['mean_excess']:+.4f} | "
                         f"{rm['largest_abs_excess']:+.3f} ({rm['largest_at']}) | "
                         + (f"{fv['excludes_zero']} of {fv['groups']}, mean {fv['mean_excess']:+.4f}" if fv else "-")
                         + f" | {cost['emulator_month_steps'] / 1e6:.2f} M | {cost['engine_city_months'] / 1e6:.1f} M |")
        txt = (d / "table.txt").read_text().splitlines()
        main_tab = []
        for ln in txt:
            if ln.startswith("in-band subset"):
                break
            main_tab.append(ln)
        hours = (f", {cost['emulator_month_steps'] / rate_emu / 3600:.2f} h on the gpu-b at the pilot's measured "
                 f"{rate_emu:,.0f} month-steps/s" if rate_emu else "")
        sections += [f"## {label}: " + RULE_TEXT.get(cfg["residual_pool"], cfg["residual_pool"]).format(
                         rows=cost["rows_per_pool"], top=cfg["economy_top"], rnd=cfg["economy_random"]),
                     f"Run directory `{d}`.", "",
                     "Groups whose residual excess excludes 0: " + (", ".join(rm["excluding_groups"]) or "none") + ".", "",
                     f"Cost for a real emulator, per checkpoint ({n_inst} instances), residual pools only: "
                     f"{cost['verdict_rows_per_pool']} verdict rows x {cost['pools']} pools x 8 samples x 24 months x "
                     f"{n_sf} (start, forced events) = {cost['emulator_month_steps']:,} emulator month-steps{hours}; "
                     f"plus {cost['rows_per_pool']} rows x {cost['pools']} pools x 9 engine seeds x 24 x {n_inst} instances = "
                     f"{cost['engine_city_months']:,} engine city-months.", "", "```", *main_tab, "```", ""]
    L += ["| rule | residual floor: margin-scored groups excluding 0 | mean excess | largest excess | flip floor: "
          "verdict-scored groups excluding 0 | emulator month-steps for the pools | engine city-months for the pools |",
          "|---|---|---|---|---|---|---|", *summ_rows, ""] + sections
    Path(out_md).write_text("\n".join(L) + "\n")
    print(f"wrote {out_md}")


def summarise_majority(out_dir, labels, out_md: str) -> None:
    """summary.md of the engine-only acceptance under the majority oracle: the identity run's checks (hackability and
    flip floor exactly 0 in every group, counted from the records), the engine-seeds runs' floor summaries, and
    every run's table verbatim."""
    out_dir = Path(out_dir)
    L = ["# Engine reference under the majority oracle", "",
         "Generated by `code/scripts/run_audit.py --plan engine-reference` from the run directories below. The oracle "
         "is the predicate's pass share over the instance's oracle seeds, accepted at one half (`dc.tasks.oracle_verdict`); "
         "residuals and surrogates use seeds disjoint from the oracle's: the truth seeds (floor basis 'truth', amendment 3 "
         "point 7) or the nine old seeds ('nine'), as each run's row says. Excess = measured "
         "hackability minus the floor, paired cluster bootstrap over the families, BCa 95 % interval; 'excludes 0' "
         "uses the BCa limits.", ""]
    rows, sections = [], []
    for lab in labels:
        d = out_dir / lab
        card = json.loads((d / "card.json").read_text())
        cfgd = json.loads((d / "config.json").read_text())
        recs = A.read_records(d / "records.jsonl.gz")
        fs = card.get("floor_summary") or floor_summary(card)
        rm, fv = fs.get("residual|margin"), fs.get("flip|verdict")
        hack = sum(1 for r in recs if r["grader_p"] >= A.ACCEPT_P and not r["oracle_accept"])
        flip_h = sum(1 for r in recs if r.get("flip_grader_accept") and not r.get("flip_oracle_accept"))
        res_h = sum(1 for r in recs if r.get("residual_grader_accept") and not r.get("residual_oracle_accept"))
        groups = card["hackability_curve"]
        zero_g = sum(1 for e in groups if e["hackability"]["value"] == 0.0)
        rows.append(f"| {lab} ({cfgd['config'].get('floor_basis', 'nine')} floor) | {cfgd['judge'].get('judge')} | "
                    f"{card['counts']['instances']} | {len(recs)} | {hack} | "
                    f"{zero_g} of {len(groups)} | {flip_h} | {res_h} | "
                    + (f"{rm['excludes_zero']} of {rm['groups']}, mean {rm['mean_excess']:+.4f}, largest "
                       f"{rm['largest_abs_excess']:+.3f} ({rm['largest_at']})" if rm else "-") + " | "
                    + (f"{fv['excludes_zero']} of {fv['groups']}, mean {fv['mean_excess']:+.4f}" if fv else "-") + " |")
        txt = (d / "table.txt").read_text().rstrip("\n")
        jd = cfgd["judge"]
        basis = cfgd["config"].get("floor_basis", "nine")
        over = []
        if jd.get("judge") == "engine-seeds":      # the flip floor is the brief's baseline: its overshoot, measured
            fl = {(f["attacker"], f["scoring"], f["budget"]): f for f in card["noise_floors"]}
            for e in card["hackability_curve"]:
                fs_ = fl[(e["attacker"], e["scoring"], e["budget"])].get("flip_surrogate", {})
                if e["scoring"] == "verdict" and "excess" in fs_:
                    x = fs_["excess"]
                    lo, hi = (x.get("bca_lo"), x.get("bca_hi")) if x.get("bca_lo") is not None else (x["lo"], x["hi"])
                    over.append(f"B={e['budget']}: flip floor {fs_['hackability']['value']:.3f}, perfect emulator "
                                f"{e['hackability']['value']:.3f}, overshoot {-x['value']:+.3f} [{-hi:+.3f},{-lo:+.3f}]")
        sections += [f"## {lab}", f"Run directory `{d}`; judge {jd.get('judge')} (seeds: {jd.get('seeds', '-')}"
                     + (f"; {jd['seeds_avoid']}" if jd.get("seeds_avoid") else "") + f"); residual pool rule "
                     f"{cfgd['config']['residual_pool']}; residual floor basis: "
                     + ("truth seeds" if basis == "truth" else "the nine old seeds") + ".", ""]
        if over:
            sections += ["Flip floor (the brief's baseline) beside verdict-scored search, measured overshoot on the perfect "
                         "emulator (floor minus hackability, BCa): " + "; ".join(over) + ". Its excess on an emulator is "
                         "not exact; read it beside this overshoot.", ""]
        sections += ["```", txt, "```", ""]
    L += ["| run | judge | instances | records | records hacked (emulator accepts, oracle rejects) | groups with "
          "hackability exactly 0 | flip-floor records hacked | residual-floor records hacked | residual floor, "
          "margin-scored groups whose excess excludes 0 | flip floor, verdict-scored groups whose excess excludes 0 |",
          "|---|---|---|---|---|---|---|---|---|---|", *rows, ""] + sections
    Path(out_md).write_text("\n".join(L) + "\n")
    print(f"wrote {out_md}")


def cache_keep_keys(tasks: str, H: int = 24, rows: int = 1000, n_secondary: int = A.N_SECONDARY):
    """The engine-cache entries later runs on ``tasks`` read, by start: every instance's first ``rows`` behaviour and
    builder plans (the residual pools, random shooting's and best-of-n's candidates, the behaviour table) on the nine
    residual seeds and, under the majority oracle, on the oracle's seeds and on the residual floor's truth seeds of
    their (start, forced events). Everything else in the cache (judge samples
    of engine-only runs, cross-entropy candidates, selected plans, replays of superseded tasks files and of other
    arms) is read by no later audit of a checkpoint; dropping it only costs replaying it again if it is ever needed.
    Returns ({start_id: set of keys}, {start_id: an instance of that start}) ."""
    universe = A.load_instances(tasks, H, cty_of=heldout_cty_of())
    spec = A.oracle_spec(tasks)
    pools = A.Pools(H=H)
    eng = A.EngineJudge(workers=0, H=H)          # for its key function only; nothing is replayed
    keep: Dict[str, set] = {}
    rep = {}
    groups = set()
    for i in universe:
        seeds = A.verdict_seeds(i, n_secondary) + (A.oracle_seed_list(i, spec["n_seeds"]) if spec else [])
        if spec and (i.start_id, i.forced_key) not in groups:      # the residual floor's truth seeds, once per group
            groups.add((i.start_id, i.forced_key))
            seeds = seeds + A.truth_seed_list(i.start_id, i.forced_key, H, A.TRUTH_N)
        k = keep.setdefault(i.start_id, set())
        rep.setdefault(i.start_id, i)
        for P in (pools.behaviour(i.start_id)[:rows], pools.builders(i.start_id)[:rows]):
            for e in {x.tobytes(): x for x in A.effective(P, i.task, H)}.values():
                k.update(eng.key(i, e, s) for s in seeds)
    eng.close()
    return keep, rep


def cache_compact(tasks: str, cache_root: str, to: str = "") -> dict:
    """Dry run (default): how much of the engine cache ``cache_keep_keys`` keeps. With ``to``: copy the kept entries
    into new per-start sqlite files under ``to`` (which must not exist yet); the existing cache is never modified.
    Swapping the directories afterwards is left to the operator."""
    import sqlite3
    keep, rep = cache_keep_keys(tasks)
    root = Path(cache_root)
    out_root = Path(to) if to else None
    if out_root is not None:
        if out_root.exists():
            raise SystemExit(f"{out_root} exists; give a new directory")
        out_root.mkdir(parents=True)
    tot = {"rows": 0, "value_bytes": 0, "kept_rows": 0, "kept_value_bytes": 0, "keep_keys": 0, "keep_keys_missing": 0}
    files = sorted(root.glob("*.sqlite"))
    for f in files:
        sid = f.stem
        con = sqlite3.connect(f"file:{f}?mode=ro", uri=True, timeout=120)
        n, b = con.execute("SELECT count(*), coalesce(sum(length(v)), 0) FROM c").fetchone()
        tot["rows"] += n
        tot["value_bytes"] += b
        ks = list(keep.get(sid, ()))
        tot["keep_keys"] += len(ks)
        dst = None
        if out_root is not None and ks:
            dst = sqlite3.connect(str(out_root / f.name))
            dst.execute("PRAGMA journal_mode=WAL")
            dst.execute("CREATE TABLE IF NOT EXISTS c (k BLOB PRIMARY KEY, v BLOB NOT NULL)")
        found = 0
        for a in range(0, len(ks), 500):
            part = ks[a:a + 500]
            got = con.execute("SELECT k, v FROM c WHERE k IN (%s)" % ",".join("?" * len(part)), part).fetchall()
            found += len(got)
            tot["kept_value_bytes"] += sum(len(v) for _, v in got)
            if dst is not None:
                dst.executemany("INSERT OR IGNORE INTO c (k, v) VALUES (?, ?)", got)
        tot["kept_rows"] += found
        tot["keep_keys_missing"] += len(ks) - found
        if dst is not None:
            dst.commit()
            dst.close()
        con.close()
    tot["files"] = len(files)
    tot["bytes_on_disk"] = int(sum(p.stat().st_size for p in root.iterdir() if p.is_file()))
    tot["tasks"] = tasks
    tot["written_to"] = str(out_root) if out_root else None
    return tot


def cache_size(root) -> int:
    """Bytes on disk of the engine cache directory (sqlite files with their WAL and shared-memory files)."""
    root = Path(root)
    return int(sum(p.stat().st_size for p in root.iterdir() if p.is_file())) if root.exists() else 0


def rescore(old_out: str, tasks: str, new_out: str, argv: list) -> int:
    """Re-score a finished run at another tasks file: the same command (checkpoint, model code, plan, pool and
    engine settings, work directory) with ``--tasks`` replaced. Every stored judge sample is re-read through
    ``dc.tasks``; what is rolled out again is listed in the dc.audit module docstring ('Re-scoring')."""
    old = json.loads((Path(old_out) / "config.json").read_text())
    prev = list(old["argv"][1:])
    keep, i = [], 0
    while i < len(prev):
        x = prev[i]
        name = x.split("=")[0]
        if name in ("--tasks", "--tasks-json", "--out", "--rescore"):
            i += 1 if "=" in x else 2
            continue
        keep.append(x)
        i += 1
    if "--work" not in {x.split("=")[0] for x in keep}:
        keep += ["--work", old["work"]]
    if "--flip-scope" not in {x.split("=")[0] for x in keep}:     # a run before the option existed ran it everywhere
        keep += ["--flip-scope", old["config"].get("flip_scope", "all")]
    out = new_out or str(Path(old_out).parent / Path(tasks).stem)
    print(f"re-scoring {old_out} at {tasks} -> {out} (work {old['work']})", flush=True)
    return main(keep + ["--tasks", tasks, "--out", out])


# ----------------------------------------------------------------------------------------------
# comparison with the perfect emulator 
# ----------------------------------------------------------------------------------------------
CMP_METHOD_ORDER = ("random", "best_of_n", "cem", "cem_seeded", "random_verdict")


def _draw_dirs(d) -> Dict[str, Path]:
    """The run directories of one run under each residual draw: the plain run's directory and its siblings with the
    suffixes ``_volatility`` and ``_calibrated`` (``draw_suffix`` at the rule's k). ``d`` may be any of them."""
    d = Path(d)
    base = d
    for draw in A.RESIDUAL_DRAWS[1:]:
        if d.name.endswith("_" + draw):
            base = d.with_name(d.name[:-len(draw) - 1])
    return {draw: (base if draw == "plain" else base.with_name(f"{base.name}_{draw}")) for draw in A.RESIDUAL_DRAWS}


def _rkey(r: dict) -> tuple:
    return (r["instance"], r["method"], int(r["budget"]), int(r["attacker_seed"]))


def _floor_runs(d, records: list) -> Tuple[Dict[str, dict], Dict[str, str]]:
    """Per residual draw that exists for the run of ``records`` (directory ``d`` or a sibling, ``_draw_dirs``): its
    residual floor per record, {record key: (floor grader accepts, floor oracle accepts)}; and a note per draw (the
    directory used, or why there is none). A sibling counts only if it is finished (records.jsonl.gz), was run with
    that draw at the rule's k, holds exactly the run's records, and its real attacks are the run's (same selected plan,
    judge pass share and oracle verdict on every record; otherwise the comparison is refused)."""
    base = {_rkey(r): r for r in records}
    out, notes = {}, {}
    for draw, p in _draw_dirs(d).items():
        if not (p / "records.jsonl.gz").exists():
            notes[draw] = f"not run ({p} has no records.jsonl.gz)"
            continue
        cfg = json.loads((p / "config.json").read_text())["config"]
        got, k = cfg.get("residual_draw", "plain"), int(cfg.get("residual_draw_k", A.VOL_K))
        if got != draw or (draw != "plain" and k != A.VOL_K):
            notes[draw] = f"not used: {p} was run with draw {got}, k {k}"
            continue
        recs = {_rkey(r): r for r in A.read_records(p / "records.jsonl.gz")}
        if set(recs) != set(base):
            notes[draw] = (f"not used: {p} holds {len(recs)} records, {len(set(recs) & set(base))} of them among the "
                           f"run's {len(base)} (unfinished or another plan)")
            continue
        bad = [key for key, r in recs.items() if (r["plan_hash"], r["grader_p"], r["oracle_accept"]) !=
               (base[key]["plan_hash"], base[key]["grader_p"], base[key]["oracle_accept"])]
        if bad:
            raise SystemExit(f"{p}: the real attacks differ from {d} on {len(bad)} records (e.g. {bad[0]}): not the same run")
        if any(r.get("residual_grader_accept") is None or r.get("residual_oracle_accept") is None for r in recs.values()):
            notes[draw] = f"not used: {p} has records without a residual floor"
            continue
        out[draw] = {key: (bool(r["residual_grader_accept"]), bool(r["residual_oracle_accept"])) for key, r in recs.items()}
        notes[draw] = f"{p} (residual pool rule {cfg.get('residual_pool')}, floor basis {cfg.get('floor_basis', 'nine')})"
    return out, notes


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return float(x) if np.isfinite(x) else None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def _ci(e, signed: bool = False) -> str:
    """'value [lo, hi]' with the BCa limits; '*' marks the percentile interval where BCa is undefined, '†' the exact
    bound of a hackability with no hacked unit; 'n/a' where the statistic is undefined."""
    if not isinstance(e, dict) or "value" not in e or e["value"] is None or not np.isfinite(e["value"]):
        return "n/a"
    f = "{:+.3f}" if signed else "{:.3f}"
    lo, hi, mark = e.get("bca_lo"), e.get("bca_hi"), ""
    if lo is None or hi is None or not (np.isfinite(lo) and np.isfinite(hi)):
        lo, hi, mark = e["lo"], e["hi"], "*"
    if e.get("method") == hd.stats.ZERO_BOUND_METHOD:
        mark = "†"
    if lo is None or hi is None or not (np.isfinite(lo) and np.isfinite(hi)):
        return f.format(e["value"]) + " [n/a]"
    return f"{f.format(e['value'])} [{f.format(lo)}, {f.format(hi)}]{mark}"


def _arm_stats(ga: np.ndarray, oa: np.ndarray, cl: list, kw: dict) -> dict:
    """One arm's statistics on paired units: hackability, judge and oracle acceptance, P(oracle rejects | judge
    accepts), and the false-rejection rate P(judge rejects | oracle accepts)."""
    out = {"hackability": hd.hackability(ga, oa, cl, **kw).as_dict(),
           "judge_accept": hd.conditional_mean(ga, None, cl, **kw).as_dict(),
           "oracle_accept": hd.conditional_mean(oa, None, cl, **kw).as_dict(),
           "n_judge_accept": int(ga.sum()), "n_oracle_accept": int(oa.sum())}
    out["oracle_reject_given_judge_accept"] = (hd.conditional_reject(ga, oa, cl, **kw).as_dict() if ga.any() else
                                               {"value": None, "status": "the judge accepted no selected plan"})
    out["false_rejection"] = (hd.false_rejection(ga[oa], [c for c, o in zip(cl, oa) if o], **kw).as_dict() if oa.any()
                              else {"value": None, "status": "the oracle accepted no selected plan"})
    return out


def compare_reference(run_dir, ref_dir, n_boot: int = hd.stats.N_BOOT, seed: int = 0) -> dict:
    """The run beside the perfect emulator (the engine judging itself on fresh seeds, ``ref_dir``), paired by instance,
    per method and budget, on every instance, per task family and on the well-posed subset (``in_band``); every
    residual floor that exists for the run (plain, volatility, calibrated: ``_floor_runs``) with the run's excess over
    it, and the same floor's excess on the perfect emulator in the same group (the reference's run with that draw).
    Cluster bootstrap over families, BCa, ``n_boot`` resamples, ``hpr_dream.stats``. Writes reference_table.md and
    reference.json in ``run_dir`` and returns the json's content."""
    run_dir, ref_dir = Path(run_dir), Path(ref_dir)
    rec = A.read_records(run_dir / "records.jsonl.gz")
    ref = A.read_records(ref_dir / "records.jsonl.gz")
    for name, rs in (("run", rec), ("reference", ref)):
        if any(r.get("oracle_rule") != "majority" for r in rs):
            raise SystemExit(f"the {name} is not judged by the majority oracle: no comparison")
        if len({_rkey(r) for r in rs}) != len(rs):
            raise SystemExit(f"the {name} has duplicate records")
    rcfg = json.loads((run_dir / "config.json").read_text())
    fcfg = json.loads((ref_dir / "config.json").read_text())
    if Path(rcfg["config"].get("tasks_file", "")).name != Path(fcfg["config"].get("tasks_file", "")).name or \
            rcfg["config"].get("tasks_sha256") != fcfg["config"].get("tasks_sha256"):
        raise SystemExit("the run and the reference use different tasks files")
    floors_run, notes_run = _floor_runs(run_dir, rec)
    floors_ref, notes_ref = _floor_runs(ref_dir, ref)
    R = {_rkey(r): r for r in rec}
    F = {_rkey(r): r for r in ref}
    kw = dict(n_boot=n_boot, seed=seed, bca=True)
    tasks = [t for t in T.TASKS if any(r["task"] == t for r in rec)]
    subsets = [("all", "every instance", lambda r: True)]
    subsets += [(f"task:{t}", f"task family {t}", (lambda t: lambda r: r["task"] == t)(t)) for t in tasks]
    subsets += [("in_band", "well-posed instances (in_band)", lambda r: bool(r["in_band"]))]
    methods = sorted({r["method"] for r in rec}, key=lambda m: (CMP_METHOD_ORDER.index(m) if m in CMP_METHOD_ORDER
                                                                  else len(CMP_METHOD_ORDER), m))
    card = json.loads((run_dir / "card.json").read_text()) if (run_dir / "card.json").exists() else None
    card_h = {(e["attacker"], e["scoring"], e["budget"]): e["hackability"]["value"] for e in card["hackability_curve"]} \
        if card else {}
    out = {"run": str(run_dir), "reference": str(ref_dir),
           "generated_utc": dt.datetime.utcnow().isoformat(timespec="seconds"),
           "statistics": f"paired by instance (record keys instance, method, budget, attacker seed present in both); "
                         f"cluster bootstrap over families, {n_boot} resamples, seed {seed}, BCa 95 % (hpr_dream.stats)",
           "definitions": {
               "hackability": "share of instances where the judge accepts the selected plan (pass share >= 0.5 over its "
                              "8 samples) and the majority oracle rejects it",
               "judge_accept": "share of instances where the judge accepts the selected plan",
               "oracle_accept": "share of instances where the majority oracle accepts the selected plan",
               "oracle_reject_given_judge_accept": "among instances whose selected plan the judge accepts, the share the "
                                                   "oracle rejects (hackability / judge_accept)",
               "false_rejection": "among instances whose selected plan the oracle accepts, the share the judge rejects",
               "difference": "emulator hackability minus perfect-emulator hackability, paired by instance",
               "floor": "the residual floor's hackability (its surrogate accepts, the oracle rejects its selected plan)",
               "excess": "hackability minus the floor's, paired by instance (the run's, or the perfect emulator's over the "
                         "same draw's floor of the reference)"},
           "floors_run": notes_run, "floors_reference": notes_ref, "subsets": {}, "card_check": None}
    n_card = 0
    for sname, sdesc, keep in subsets:
        groups = []
        for m in methods:
            for B in sorted({int(r["budget"]) for r in rec if r["method"] == m}):
                keys = sorted(k for k, r in R.items() if k[1] == m and k[2] == B and keep(r))
                paired = [k for k in keys if k in F]
                g = {"method": m, "attacker": R[keys[0]]["attacker"] if keys else None,
                     "scoring": R[keys[0]]["scoring"] if keys else None, "budget": B,
                     "n_run": len(keys), "n_paired": len(paired)}
                if not paired:
                    g["status"] = "no instance of the run's group is in the reference"
                    groups.append(g)
                    continue
                for k in paired:
                    if F[k]["cluster"] != R[k]["cluster"] or bool(F[k]["in_band"]) != bool(R[k]["in_band"]) or \
                            F[k]["task"] != R[k]["task"]:
                        raise SystemExit(f"{k}: the run and the reference disagree on the instance's family, task or band")
                cl = [R[k]["cluster"] for k in paired]
                g["n_clusters"] = len(set(cl))
                ga_e = np.array([R[k]["grader_p"] >= A.ACCEPT_P for k in paired])
                oa_e = np.array([bool(R[k]["oracle_accept"]) for k in paired])
                ga_r = np.array([F[k]["grader_p"] >= A.ACCEPT_P for k in paired])
                oa_r = np.array([bool(F[k]["oracle_accept"]) for k in paired])
                he, hr = ga_e & ~oa_e, ga_r & ~oa_r
                g["emulator"] = _arm_stats(ga_e, oa_e, cl, kw)
                g["perfect_emulator"] = _arm_stats(ga_r, oa_r, cl, kw)
                g["difference"] = hd.excess(he, hr, cl, **kw).as_dict()
                fl = {}
                for draw in A.RESIDUAL_DRAWS:
                    if draw not in floors_run:
                        continue
                    fe = np.array([floors_run[draw][k][0] and not floors_run[draw][k][1] for k in paired])
                    e = {"floor": hd.hackability([floors_run[draw][k][0] for k in paired],
                                                 [floors_run[draw][k][1] for k in paired], cl, **kw).as_dict(),
                         "excess": hd.excess(he, fe, cl, **kw).as_dict()}
                    if draw in floors_ref:
                        fr = np.array([floors_ref[draw][k][0] and not floors_ref[draw][k][1] for k in paired])
                        e["perfect_floor"] = hd.hackability([floors_ref[draw][k][0] for k in paired],
                                                            [floors_ref[draw][k][1] for k in paired], cl, **kw).as_dict()
                        e["perfect_excess"] = hd.excess(hr, fr, cl, **kw).as_dict()
                    else:
                        e["perfect_status"] = notes_ref.get(draw, "not run")
                    fl[draw] = e
                g["floors"] = fl
                if sname == "all" and card_h and len(paired) == len(keys):
                    cv = card_h.get((g["attacker"], g["scoring"], B))
                    if cv is not None:
                        if not np.isclose(cv, g["emulator"]["hackability"]["value"]):
                            raise SystemExit(f"{m} B={B}: hackability {g['emulator']['hackability']['value']} differs from "
                                             f"the run's card ({cv})")
                        n_card += 1
                groups.append(g)
        out["subsets"][sname] = {"description": sdesc, "groups": groups,
                                 "n_instances": len({k[0] for k, r in R.items() if keep(r)})}
    out["card_check"] = (f"emulator hackability equals the run's card.json in {n_card} groups (every instance)" if card
                         else "the run has no card.json")
    out = _jsonable(out)
    (run_dir / "reference.json").write_text(json.dumps(out, indent=1))
    (run_dir / "reference_table.md").write_text(reference_table_md(out))
    return out


def reference_table_md(out: dict) -> str:
    """reference_table.md from ``compare_reference``'s content: per subset, the comparison with the perfect emulator,
    then every residual floor of the run with its excess and the same floor's excess on the perfect emulator."""
    draws = [d for d in A.RESIDUAL_DRAWS if not out["floors_run"].get(d, "").startswith("not ")]
    L = ["# The run beside the perfect emulator", "",
         f"Run `{out['run']}`; perfect emulator (the engine judging itself on fresh seeds) `{out['reference']}`. "
         f"Generated by `code/scripts/run_audit.py --compare-reference` at {out['generated_utc']}Z. Statistics: "
         f"{out['statistics']}. `*`: the percentile interval (BCa undefined); `†`: no hacked unit, the exact one-sided "
         f"bound on clusters; a rate whose group has no event, or only events, has a zero-width bootstrap interval. "
         f"{out['card_check']}.", "",
         "Definitions: " + "; ".join(f"**{k}**: {v}" for k, v in out["definitions"].items()) + ".", "",
         "Residual floors of the run: " + "; ".join(f"{d}: {n}" for d, n in out["floors_run"].items()) + ".", "",
         "Residual floors of the perfect emulator: " + "; ".join(f"{d}: {n}" for d, n in out["floors_reference"].items())
         + ".", ""]
    for sname, s in out["subsets"].items():
        L += [f"## {s['description']} ({s['n_instances']} instances)", "",
              "| method | B | n | hackability, emulator | hackability, perfect | difference | judge accepts, emulator | "
              "judge accepts, perfect | oracle accepts, emulator | oracle accepts, perfect | oracle rejects given judge "
              "accepts, emulator | the same, perfect | false rejection, emulator | false rejection, perfect |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for g in s["groups"]:
            if "emulator" not in g:
                L.append(f"| {g['method']} | {g['budget']} | 0 of {g['n_run']} | {g.get('status', '')} |" + " |" * 10)
                continue
            e, p = g["emulator"], g["perfect_emulator"]
            n = f"{g['n_paired']}" + ("" if g["n_paired"] == g["n_run"] else f" of {g['n_run']}")
            L.append(f"| {g['method']} | {g['budget']} | {n} | {_ci(e['hackability'])} | {_ci(p['hackability'])} | "
                     f"{_ci(g['difference'], True)} | {_ci(e['judge_accept'])} | {_ci(p['judge_accept'])} | "
                     f"{_ci(e['oracle_accept'])} | {_ci(p['oracle_accept'])} | "
                     f"{_ci(e['oracle_reject_given_judge_accept'])} | {_ci(p['oracle_reject_given_judge_accept'])} | "
                     f"{_ci(e['false_rejection'])} | {_ci(p['false_rejection'])} |")
        if draws:
            hdr = "| method | B | n | hackability, emulator | hackability, perfect | " + " | ".join(
                f"{d} floor | excess over {d} | {d} floor, perfect | perfect excess over {d}" for d in draws) + " |"
            L += ["", hdr, "|" + "---|" * (5 + 4 * len(draws))]
            for g in s["groups"]:
                if "emulator" not in g:
                    continue
                n = f"{g['n_paired']}" + ("" if g["n_paired"] == g["n_run"] else f" of {g['n_run']}")
                row = (f"| {g['method']} | {g['budget']} | {n} | {_ci(g['emulator']['hackability'])} | "
                       f"{_ci(g['perfect_emulator']['hackability'])} | ")
                cells = []
                for d in draws:
                    f = g["floors"].get(d, {})
                    cells += [_ci(f.get("floor")), _ci(f.get("excess"), True),
                              _ci(f.get("perfect_floor")) if "perfect_floor" in f else "not run",
                              _ci(f.get("perfect_excess"), True) if "perfect_excess" in f else "not run"]
                L.append(row + " | ".join(cells) + " |")
        L.append("")
    return "\n".join(L) + "\n"


def filter_instance_keys(instances, path: str):
    """``--instance-keys FILE``: keep, in their selected order, only the selected instances whose key (``start|task|H<h>``)
    is listed in the file (one per line; blank lines and lines starting with # are skipped). Every listed key must be
    among the selected instances, and none may be listed twice."""
    want = [x.strip() for x in Path(path).read_text().splitlines() if x.strip() and not x.strip().startswith("#")]
    if len(set(want)) != len(want):
        raise SystemExit(f"--instance-keys {path}: a key is listed twice")
    have = {i.key for i in instances}
    missing = [k for k in want if k not in have]
    if missing:
        raise SystemExit(f"--instance-keys {path}: {len(missing)} keys are not among the selected instances, e.g. {missing[:3]}")
    keep = set(want)
    return [i for i in instances if i.key in keep]


def draw_suffix(a) -> str:
    """Run-directory suffix of a residual draw other than the plain one ("" for plain; "_volatility" or "_calibrated",
    or "_volatility_k<k>" / "_calibrated_k<k>" for a diagnostic neighbour count)."""
    if a.residual_draw == "plain":
        return ""
    return f"_{a.residual_draw}" + ("" if a.residual_draw_k == A.VOL_K else f"_k{a.residual_draw_k}")


def engine_reference(a, argv: list) -> int:
    """The engine-only acceptance of the residual floor (study protocol): the engine judging itself on
    fresh seeds, every instance of --tasks, four methods, budgets 1 to 1,000, with the fully paired per-instance pool
    (rule A, 1,000 rows) and the economy pool (rule B), sharing phase 1; then summary.md. When the tasks file carries
    ``meta.oracle`` (the majority oracle), the identity run comes first: the oracle judging itself (economy pools),
    whose hackability must be exactly 0 in every group, as must its flip floor; the engine-seeds judge then uses seeds
    that are neither the nine residual seeds nor the oracle's, and summary.md reads both (``summarise_majority``)."""
    out = Path(a.out or (A.REPO / "results" / "audit" / "engine_reference" / Path(a.tasks).stem))
    work = a.work or str(A.CACHE_ROOT / "work" / "engine_reference" / Path(a.tasks).stem)
    base = ["--judge", "engine-seeds", "--instances", a.instances, "--budgets", "1,10,100,1000",
            "--methods", "cem,random,best_of_n,random_verdict", "--floors", "residual,flip",
            "--pool-verdict-plans", "1000", "--behaviour-plans", "125", "--flip-rates", "family",
            "--tasks", a.tasks, "--work", work, "--workers", str(a.workers), "--flip-scope", a.flip_scope,
            "--truth-cand-seeds", str(a.truth_cand_seeds)]
    given = {x.split("=")[0] for x in argv if x.startswith("--")}
    for flag in ("--methods", "--floors"):     # a reference restricted to some methods or floors, when asked for
        if flag in given:
            base[base.index(flag) + 1] = getattr(a, flag[2:])
    sfx = draw_suffix(a)          # another residual draw: its own run directories and summary beside the plain ones
    if sfx:
        base += ["--residual-draw", a.residual_draw, "--residual-draw-k", str(a.residual_draw_k)]
    if a.cache_floor_candidates:
        base += ["--cache-floor-candidates"]
    if a.remote != "none":
        base += ["--remote", a.remote, "--remote-workers", str(a.remote_workers)]
    runs = [("A_instance", ["--residual-pool", "instance", "--residual-rows", "1000"]),
            ("B_economy", ["--residual-pool", "economy", "--residual-rows", "1000", "--economy-top", "100",
                           "--economy-random", "25"])]
    if A.oracle_spec(a.tasks):
        # majority oracle (amendment 3): first the oracle judging itself (identity judge on the oracle's seeds; its
        # samples depend on the thresholds, so its own work directory), economy pools as on a checkpoint
        ident = list(base)
        ident[ident.index("engine-seeds")] = "engine-identity"
        if a.identity_instances:          # the identity run is a plumbing check: a subset may be enough
            ident[ident.index("--instances") + 1] = a.identity_instances
        ident[ident.index("--work") + 1] = str(Path(work) / "identity")
        order = [x for x in a.reference_runs.split(",") if x] or ["identity", "A_instance", "B_economy"]
        bad = set(order) - {"identity", "A_instance", "B_economy"}
        if bad:
            raise SystemExit(f"--reference-runs: unknown runs {sorted(bad)}")
        extra_of = dict(runs)
        for label in order:
            if label == "identity":
                rc = main(ident + ["--residual-pool", "economy", "--residual-rows", "1000", "--economy-top", "100",
                                   "--economy-random", "25", "--out", str(out / ("identity" + sfx))])
            else:
                rc = main(base + extra_of[label] + ["--out", str(out / (label + sfx))])
            if rc:
                return rc
        summarise_majority(out, [lab + sfx for lab in ("identity", "A_instance", "B_economy")
                                 if (out / (lab + sfx) / "card.json").exists()], str(out / f"summary{sfx}.md"))
        return 0
    for label, extra in runs:
        rc = main(base + extra + ["--out", str(out / label)])
        if rc:
            return rc
    summarise(",".join(f"{lab}={out / lab}" for lab, _ in runs), str(out / "summary.md"))
    return 0


def _card(R, meta, beh):
    """``hpr_dream.card.build_card`` with the behaviour sections left out (and the meta saying so) when the method set
    sampled no behaviour verdicts, so that their pass shares are missing: a run must not fail after every phase."""
    bp = np.asarray((beh or {}).get("grader_p", []), dtype=np.float64)
    if beh is not None and (bp.size == 0 or not np.isfinite(bp).all() or (bp < 0).any() or (bp > 1).any()):
        meta = {**meta, "behaviour_table": f"not supplied ({int((~np.isfinite(bp)).sum())} of {bp.size} behaviour pass "
                                           "shares are not finite for this method set)"}
        beh = None
    return hd.build_card(R, meta, behaviour=beh, bca=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ckpt", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--summarise", default="", help="label=run_dir,label=run_dir,...: write --summary-out and exit")
    ap.add_argument("--summary-out", default="")
    ap.add_argument("--work", default="")
    ap.add_argument("--instances", default="all")
    ap.add_argument("--budgets", default="1,10,100,1000")
    ap.add_argument("--methods", default="cem,random,best_of_n,random_verdict")
    ap.add_argument("--search-seeds", default="0")
    ap.add_argument("--floors", default="residual,flip", help="comma-separated floors (residual, flip); 'none': no "
                    "floor and nothing in phase 2 (NoFloorAudit; under --plan amendment2 also no floor cross-check)")
    ap.add_argument("--pool-verdict-plans", type=int, default=50)
    ap.add_argument("--residual-pool", default="family", choices=A.RESIDUAL_RULES)
    ap.add_argument("--residual-rows", type=int, default=0, help="first rows of each pool the rule uses (0: all)")
    ap.add_argument("--behaviour-plans", type=int, default=0, help="behaviour rows for the behaviour table (0: all)")
    ap.add_argument("--economy-top", type=int, default=100)
    ap.add_argument("--economy-random", type=int, default=25)
    ap.add_argument("--flip-rates", default="family", choices=("family", "all"))
    ap.add_argument("--flip-scope", default="verdict", choices=A.FLIP_SCOPES,
                    help="verdict (default): the flip floor beside verdict-scored random search only, its matched use; "
                         "all: beside every method (the main checkpoint)")
    ap.add_argument("--plan", default="uniform", choices=("uniform", "amendment2", "engine-reference"),
                    help="amendment2: the per-checkpoint plan of study protocol (its defaults replace "
                         "--methods, --budgets, --pool-verdict-plans, --residual-pool, --behaviour-plans unless given)")
    ap.add_argument("--checkpoint", default="", help="ladder checkpoint .pt: sets --ckpt, and --out "
                    "results/audit/ladder/<run>/<checkpoint>/ and --work .../work/ladder/<run>/<checkpoint>/ if not given")
    ap.add_argument("--reference-runs", default="", help="engine-reference under the majority oracle: which runs and in "
                    "what order (identity,A_instance,B_economy; default all three in that order)")
    ap.add_argument("--truth-cand-seeds", type=int, default=A.TRUTH_CAND, help="majority oracle: truth seeds of a "
                    "cross-entropy candidate's search truth in the residual floor (0..n-1)")
    ap.add_argument("--residual-draw", default="plain", choices=A.RESIDUAL_DRAWS, help="majority oracle: how the residual "
                    "floor draws a candidate's residual: plain (uniform over the pool), volatility (uniform over the "
                    f"{A.VOL_K} pool plans nearest in log seed standard deviation) or calibrated (uniform over the "
                    f"{A.VOL_K} pool plans nearest in the pool's ranks of mean and seed standard deviation, the candidate's "
                    "own plan left out; dc.audit RESIDUAL_DRAWS)")
    ap.add_argument("--residual-draw-k", type=int, default=A.VOL_K, help=f"volatility and calibrated draws: neighbours "
                    f"(the rule is {A.VOL_K}; other values are diagnostics)")
    ap.add_argument("--cache-floor-candidates", action="store_true", help="also write the floors' search candidates and "
                    "selections to the engine cache (default: pool plans only). For engine-only runs whose next run "
                    "replays the same candidates (the other pool rule draws the same search residuals); results do not "
                    "depend on it; --cache-compact drops the entries later")
    ap.add_argument("--identity-instances", default="", help="engine-reference under the majority oracle: instances of "
                    "the identity run (all or N, selected as --instances; default: as --instances)")
    ap.add_argument("--instance-keys", default="", help="file of instance keys (start|task|H<h>, one per line): keep only "
                    "these of the instances --instances selected (applied after it; every key must be among them)")
    ap.add_argument("--subset-n", type=int, default=40)
    ap.add_argument("--bon-families", type=int, default=20)
    ap.add_argument("--verdict-cap", type=int, default=100)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--judge", default="emulator", choices=("emulator", "engine-identity", "engine-seeds"))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--chunk", type=int, default=256, help="emulator rows (plans x K) per rollout call")
    ap.add_argument("--buckets", default="16,64,144,256", help="padded batch shapes of the emulator (144 + 256 "
                    "holds a 400-row cross-entropy generation without padding)")
    ap.add_argument("--no-compile", action="store_true")
    ap.add_argument("--no-fast", action="store_true", help="the tag's compiled trunk instead of dc.fast")
    ap.add_argument("--model-src", default="", help="'auto' (the checkpoint's training commit, refused if its tree "
                    "was dirty), 'worktree', or a git revision or tag; default auto with --checkpoint, else worktree")
    ap.add_argument("--engine-cache", default=str(A.CACHE_ROOT / "engine_cache"))
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--tasks", "--tasks-json", dest="tasks", default=str(A.TASKS_JSON),
                    help="tasks file (instances, thresholds); recorded with its sha256 and dc/tasks.py's in the digests")
    ap.add_argument("--rescore", default="",
                    help="finished run directory: rerun it at --tasks with the same checkpoint, plan and work directory, "
                         "re-reading every stored sample (see dc.audit module docstring, 'Re-scoring')")
    ap.add_argument("--remote", default="none", choices=("none", "host-b"),
                    help="add a remote replay pool (python -m dc.audit serve over ssh)")
    ap.add_argument("--remote-workers", type=int, default=22)
    ap.add_argument("--remote-root", default=A.HOST_B_ROOT)
    ap.add_argument("--cache-compact", action="store_true", help="report how much of --engine-cache the entries later "
                    "runs on --tasks read (cache_keep_keys) take, and exit; nothing is modified")
    ap.add_argument("--cache-compact-to", default="", help="with --cache-compact: copy those entries into this new "
                    "directory (the existing cache is left as it is)")
    ap.add_argument("--compare-reference", default="", help="finished run directory: write reference_table.md and "
                    "reference.json there, the run beside the perfect emulator (--reference) paired by instance, with "
                    "every residual floor that exists for the run (its _volatility and _calibrated siblings), and exit")
    ap.add_argument("--reference", default="", help="with --compare-reference: the perfect emulator's run directory "
                    "(default results/audit/engine_reference/<tasks stem>/B_economy; its _volatility and _calibrated "
                    "siblings give the floors' own excess)")
    argv = list(sys.argv[1:] if argv is None else argv)
    a = ap.parse_args(argv)
    if a.cache_compact:
        r = cache_compact(a.tasks, a.engine_cache, a.cache_compact_to)
        print(json.dumps(r, indent=1))
        return 0
    if a.summarise:
        summarise(a.summarise, a.summary_out)
        return 0
    if a.compare_reference:
        run_dir = Path(a.compare_reference)
        ref = a.reference or str(A.REPO / "results" / "audit" / "engine_reference" / Path(json.loads(
            (run_dir / "config.json").read_text())["config"]["tasks_file"]).stem / "B_economy")
        res = compare_reference(run_dir, ref)
        print(f"wrote {run_dir / 'reference_table.md'} and {run_dir / 'reference.json'} (reference {ref}); floors of the "
              f"run: " + "; ".join(f"{d}: {n}" for d, n in res["floors_run"].items()), flush=True)
        return 0
    if a.rescore:
        return rescore(a.rescore, a.tasks, a.out, argv)
    if a.plan == "engine-reference":
        return engine_reference(a, argv)
    given = {x.split("=")[0] for x in argv if x.startswith("--")}
    if a.checkpoint and "--methods" in given and set(_strs(a.methods)) != {"cem", "random", "best_of_n", "random_verdict"} \
            and not ({"--work", "--out"} <= given):
        # another method set changes the phase-1 digest; phase-1 files have one path per instance, so the checkpoint's
        # default work directory would be overwritten 
        raise SystemExit("--checkpoint with other --methods needs its own --work and --out ")
    if a.checkpoint:
        ck = Path(a.checkpoint).resolve()
        a.ckpt = str(ck)
        if not a.out:      # another residual draw is another run beside the plain one (phase 1 shared via --work)
            a.out = str(A.REPO / "results" / "audit" / "ladder" / ck.parent.name / ck.stem
                        / (Path(a.tasks).stem + draw_suffix(a)))
        if not a.work:
            a.work = str(A.CACHE_ROOT / "work" / "ladder" / ck.parent.name / ck.stem)
        if not a.model_src:
            a.model_src = "auto"
    if not a.model_src:
        a.model_src = "worktree"
    if not a.out:
        raise SystemExit("--out is required")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(a.work) if a.work else A.CACHE_ROOT / "work" / out.name
    work.mkdir(parents=True, exist_ok=True)
    tdig = A.tasks_digest(a.tasks)
    ospec = A.oracle_spec(a.tasks)               # None: the primary-seed oracle; else the majority oracle (amendment 3)
    if ospec:      # the majority oracle: the residual floor on truth seeds (the nine seeds stay for older files only)
        tdig = {**tdig, "oracle": "majority", "oracle_seeds": ospec["n_seeds"], "floor_basis": "truth",
                "truth_cand_seeds": a.truth_cand_seeds, "residual_draw": a.residual_draw,
                "residual_draw_k": a.residual_draw_k}
    elif a.residual_draw != "plain":
        raise SystemExit(f"--residual-draw {a.residual_draw} needs a tasks file with the majority oracle (truth-seed floor)")
    no_floors = a.floors.strip() == NO_FLOORS              # ``NoFloorAudit``: no floor, nothing in phase 2
    floors = () if no_floors else _strs(a.floors)
    if a.plan == "amendment2":
        kw = dict(**tdig, search_seeds=_ints(a.search_seeds), floors=floors, flip_rates=a.flip_rates,
                  flip_scope=a.flip_scope,
                  subset_n=a.subset_n, bon_families=a.bon_families, verdict_cap=a.verdict_cap,
                  economy_top=a.economy_top, economy_random=a.economy_random, H=a.horizon)
        for flag, key, val in (("--budgets", "budgets", _ints(a.budgets)), ("--methods", "methods", _strs(a.methods)),
                               ("--pool-verdict-plans", "pool_verdict_plans", a.pool_verdict_plans),
                               ("--behaviour-plans", "behaviour_plans", a.behaviour_plans)):
            if flag in given:
                kw[key] = val
        if no_floors:          # no floor, so no cross-check of the residual floor (``NoFloorAudit``)
            kw["cross_check"] = ""
        cfg = A.amendment2_config(**kw)
    else:
        cfg = A.AuditConfig(H=a.horizon, budgets=_ints(a.budgets), methods=_strs(a.methods),
                            search_seeds=_ints(a.search_seeds), floors=floors,
                            pool_verdict_plans=a.pool_verdict_plans, residual_pool=a.residual_pool,
                            residual_rows=a.residual_rows, behaviour_plans=a.behaviour_plans, economy_top=a.economy_top,
                            economy_random=a.economy_random, flip_rates=a.flip_rates, flip_scope=a.flip_scope, **tdig)
    cfg.check()
    # start files of data/families.json and, when it exists, of data/families_x.json (the held-out extension)
    universe = A.load_instances(a.tasks, a.horizon, cty_of=heldout_cty_of())
    instances = A.select_instances(universe, "all" if a.instances == "all" else int(a.instances))
    if a.instance_keys:
        instances = filter_instance_keys(instances, a.instance_keys)
    t0 = time.time()
    cache_bytes0 = cache_size(a.engine_cache)
    remote = None
    if a.remote == "host-b":
        remote = A.host_b_pool(a.remote_workers, a.remote_root, log_path=work / "remote_stderr.log")
    engine = A.EngineJudge(a.engine_cache, workers=a.workers, H=a.horizon, remote=remote,
                           log=lambda s: print(s, flush=True))
    engine._get_pool()          # start the replay processes before CUDA is initialised
    if remote is not None:      # the two machines must replay identically: compare on a few plans
        i0 = instances[0]
        rel = str(Path(i0.cty).resolve().relative_to(A.REPO))
        remote.check_files([rel])
        raw = A.Pools(H=a.horizon).behaviour(i0.start_id)[:6]
        plans = np.concatenate([A.effective(raw, "grow", a.horizon), A.effective(raw, "recover", a.horizon)])
        jobs = [(i0.cty, plans[j].tobytes(), a.horizon, A.seed_for("remote-check", j)) for j in range(len(plans))]
        same = engine._local(jobs) == remote.map([(rel,) + j[1:] for j in jobs])
        print(f"remote pool on {remote.host}: {remote.workers} workers; identical replays on {len(jobs)} check plans "
              f"(6 plain, 6 with the recover earthquake): {same}", flush=True)
        if not same:
            raise SystemExit("remote replays differ from local replays")
    judge = make_judge(a, engine, ospec, tdig["tasks_sha256"])
    pools = A.Pools(H=a.horizon)
    audit_cls = NoFloorAudit if no_floors else A.Audit
    audit = audit_cls(cfg, instances, judge, engine, pools, work, log=lambda s: print(s, flush=True), universe=universe)
    audit.cache_floor_candidates = bool(a.cache_floor_candidates)
    run_meta = {"argv": [sys.argv[0]] + argv, "config": cfg.to_dict(), "judge": judge.describe(), "pools": pools.describe(),
                "engine_cache": a.engine_cache, "work": str(work), "git": git_state(),
                "instances": [i.key for i in instances], "started_utc": dt.datetime.utcnow().isoformat(timespec="seconds")}
    prev_cfg = json.loads((out / "config.json").read_text()).get("config") if (out / "config.json").exists() else None
    if prev_cfg != json.loads(json.dumps(run_meta["config"], default=str)):
        # the first invocation of this configuration (a changed one, e.g. a new floor, replaces it); all are appended below
        (out / "config.json").write_text(json.dumps(run_meta, indent=1, default=str))
    with open(out / "invocations.jsonl", "a") as f:
        f.write(json.dumps(run_meta, default=str) + "\n")
    print(f"audit: {len(instances)} instances ({len({i.start_id for i in instances})} starts, "
          f"{len({i.family_id for i in instances})} families), methods {cfg.methods}, budgets {cfg.budgets}, "
          f"seeds {cfg.search_seeds}, floors {cfg.floors}, judge {judge.name}, work {work}"
          + (f", oracle: majority over {cfg.oracle_seeds} seeds" if cfg.majority else ""), flush=True)
    try:
        res = audit.run()
    finally:
        engine.close()
    records = res["records"]
    for r in records:
        assert r["n_scored"] == r["budget"], r["plan_id"]

    # outputs
    A.write_records(records, out / "records.jsonl.gz")
    np.savez_compressed(out / "selected_plans.npz", plan_id=np.array([r["plan_id"] for r in records]),
                        plans=res["plans"], plans_effective=res["plans_effective"])
    pools_npz = {}
    for i in instances:
        d = res["p1"][i.key]
        for kind, pool in d["pools"].items():
            pools_npz[f"{i.file_stem}__residual_pool_{kind}"] = pool
        pools_npz[f"{i.file_stem}__behaviour_grader_p"] = d["behaviour"]["grader_p"]
        pools_npz[f"{i.file_stem}__behaviour_engine_margin"] = d["behaviour"]["oracle_margin"]
        if cfg.majority:
            pools_npz[f"{i.file_stem}__behaviour_oracle_share"] = d["behaviour"]["oracle_share"]
        for kind, pool in res["p2"][i.key].get("truth_pools", {}).items():
            pools_npz[f"{i.file_stem}__truth_residual_pool_{kind}"] = pool
        for kind, sd in res["p2"][i.key].get("truth_pool_sd", {}).items():          # volatility and calibrated draws
            pools_npz[f"{i.file_stem}__truth_pool_sd_{kind}"] = sd
        for kind, mu in res["p2"][i.key].get("truth_pool_mean", {}).items():        # calibrated draw only
            pools_npz[f"{i.file_stem}__truth_pool_mean_{kind}"] = mu
    np.savez_compressed(out / "pools.npz", **pools_npz)
    pool_stats = {"flip_rates": res["flip_rates"], "residual_pool_mode": cfg.residual_pool,
                  "residual_surrogates": res["residual_pools"],
                  "per_instance": {i.key: res["p1"][i.key]["pool_info"] for i in instances},
                  "truth_pools_per_instance": {i.key: res["p2"][i.key].get("truth_pool_info") for i in instances}
                  if cfg.floor_basis == "truth" else None}
    (out / "pool_stats.json").write_text(json.dumps(pool_stats, indent=1))
    costs = costs_summary(res, cfg, instances, judge, engine, universe)
    if cfg.plan == "amendment2":
        costs["design_amendment2"] = plan_design_report(audit, res, universe, judge, engine, work, costs)
    if cfg.majority:
        costs["engine_majority"] = engine_costs_majority(res, cfg, instances, universe, audit)
    costs["wall_seconds_this_invocation"] = time.time() - t0
    (out / "costs.json").write_text(json.dumps({"summary": costs, "per_instance": res["costs"]}, indent=1, default=float))

    meta = {"audited": f"{judge.name}: {judge.describe().get('ckpt', judge.name)}",
            "code_version": run_meta["git"]["rev"] + ("+dirty" if run_meta["git"]["dirty_files"] else ""),
            "date": dt.date.today().isoformat(),
            "revisit_date": (dt.date.today() + dt.timedelta(days=182)).isoformat(),
            "judge": judge.describe(), "config": cfg.to_dict(), "instances": len(instances),
            "engine_seeds": "primary seed_for('task', start, task, H); secondary seed_for('task-secondary', start, task, H, k), k=0..7",
            "residual_definition": "judge margin minus the engine's mean margin over the nine verdict seeds; floor outcome on the primary seed",
            "residual_pool": cfg.residual_pool, "residual_rows": cfg.rows,
            "flip_floor": ("flip surrogate and flip_closed_form_family_rates use confusion rates pooled within the task "
                           "family and the per-instance base rate; the instrument's built-in flip_closed_form pools "
                           "confusion rates over every behaviour plan" if cfg.flip_rates == "family" else
                           "confusion rates pooled over every behaviour plan")}
    if cfg.majority:
        meta.update({
            "oracle": {**ospec, "seeds": f"seed_for('{ospec['seed_name']}', start, task, H, k), k=0..{ospec['n_seeds'] - 1}",
                       "verdict": f"dc.tasks.oracle_verdict: pass share over the {ospec['n_seeds']} seeds >= "
                                  f"{ospec['pass_share']}", "single_seed_record": "oracle seed 0 alone (k = 0)"},
            "engine_seeds": (f"oracle: the majority over the {ospec['n_seeds']} oracle seeds above; residual seeds (pools and "
                             "surrogates only, disjoint from the oracle's): primary seed_for('task', start, task, H), "
                             "secondary seed_for('task-secondary', start, task, H, k), k=0..7"),
            "residual_definition": (
                f"truth seeds seed_for('task-truth', start, forced key, H, k), k < {A.TRUTH_N}, shared by the tasks of a start, "
                f"disjoint from every residual and oracle seed; residual of a pool plan = judge score minus its mean margin "
                f"over all {A.TRUTH_N}; the surrogate selects on a pool plan's mean over truth seeds 0..{A.TRUTH_A - 1} (a "
                f"cross-entropy candidate's over 0..{cfg.truth_cand_seeds - 1}) plus a drawn search residual and accepts on "
                f"the selected plan's mean over {A.TRUTH_A}..{A.TRUTH_N - 1} plus the paired verdict residual; the floor's "
                f"selected plan is judged by the majority oracle; the nine old seeds are not used by the floor"
                if cfg.floor_basis == "truth" else
                "judge margin minus the engine's mean margin over the nine residual seeds; the floor's selected plan is "
                "judged by the majority oracle")
            + ((f"; residual draw 'volatility': the candidate's paired residual is drawn uniformly from the "
                f"{cfg.residual_draw_k} pool plans nearest in log(s + {A.VOL_EPS}), s = the sample standard deviation of "
                f"the margin over all {A.TRUTH_N} truth seeds (pool plans) or over the candidate's search-truth seeds; "
                f"ties by pool order; a pool without spread in s draws uniformly") if cfg.residual_draw == "volatility" else "")
            + ((f"; residual draw 'calibrated': the candidate's paired residual is drawn uniformly from the "
                f"{cfg.residual_draw_k} pool plans nearest in the plane of the pool's own ranks (u_m, u_s), u_m(x) = share "
                f"of pool plans whose mean margin over all {A.TRUTH_N} truth seeds is below x, u_s likewise for the sample "
                f"standard deviation; the candidate's m and s over its search-truth seeds; Euclidean distance, ties by pool "
                f"order, every pool row holding the candidate's own plan left out") if cfg.residual_draw == "calibrated" else ""),
            "oracle_accept": "the majority oracle's verdict (hackability = emulator accepts and the majority rejects)"})
    R, beh = A.card_tables(records, res["p1"], instances, cfg.floors, n_beh=cfg.beh_rows)
    card = _card(R, meta, beh)
    if res["flip_rates"]:
        card["flip_rates_by_task_family"] = res["flip_rates"]["by_task"]
        card["flip_closed_form_family_rates"] = flip_closed_form_family(records, res["p1"], instances,
                                                                        res["flip_rates"], cfg.beh_rows)
    card["floor_summary"] = floor_summary(card)
    ostats = None
    if cfg.majority:
        ostats = oracle_majority_stats(records)
        card["oracle_majority"] = ostats
    hd.write_card(card, out / "card.json")
    fr = res["flip_rates"]
    frs = "n/a"
    if fr:
        frs = (f"{fr['mode']} confusion rates on {fr['n_behaviour_plans']} behaviour plans: " +
               ("; ".join(f"{t} fp {v['fp']:.3f} fn {v['fn']:.3f}" for t, v in fr["by_task"].items())
                if fr["mode"] == "family" else f"fp {fr['fp']:.3f}, fn {fr['fn']:.3f}"))
    tab = (lambda cd, rc, os_=None: table_majority(cd, rc, cfg.floors, os_)) if cfg.majority else \
        (lambda cd, rc, os_=None: table(cd, rc, cfg.floors))
    lines = [f"judge {judge.name}; {len(instances)} instances in {len({i.family_id for i in instances})} clusters; "
             f"residual pool rule {cfg.residual_pool} ({cfg.rows} rows per pool); {frs}"
             + (f"; oracle: majority over {cfg.oracle_seeds} seeds (pass share >= {T.ORACLE_PASS})" if cfg.majority else ""),
             tab(card, records, ostats)]
    for k, v in card["floor_summary"].items():
        if k in ("residual|margin", "flip|verdict"):
            lines.append(f"summary {k.replace('|', ' floor, ')}-scored groups: excess excludes 0 (BCa) in "
                         f"{v['excludes_zero']} of {v['groups']}; mean excess {v['mean_excess']:+.4f}; largest |excess| "
                         f"{v['largest_abs_excess']:+.3f} ({v['largest_at']})")
    inband = [i for i in instances if i.in_band]
    if 0 < len(inband) < len(instances):
        keep = {i.key for i in inband}
        rec_b = [r for r in records if r["instance"] in keep]
        Rb, bb = A.card_tables(rec_b, res["p1"], inband, cfg.floors, n_beh=cfg.beh_rows)
        band = (json.loads(Path(a.tasks).read_text()).get("meta") or {}).get("in_band")   # the file's definition, if any
        card_b = _card(Rb, {**meta, "subset": "instances flagged in_band: " + (
            band if isinstance(band, str) else "validation base rate in [0.2, 0.5]")}, bb)
        os_b = None
        if cfg.majority:
            os_b = card_b["oracle_majority"] = oracle_majority_stats(rec_b)
        hd.write_card(card_b, out / "card_in_band.json")
        lines += [f"in-band subset: {len(inband)} instances ({card_b['meta']['subset']})", tab(card_b, rec_b, os_b)]
    xkeys = sorted({r["instance"] for r in records if "residualA_grader_accept" in r})
    if xkeys:
        xinst = [i for i in instances if i.key in xkeys]
        rec_x = [r for r in records if r["instance"] in set(xkeys)]
        Rx, bx = A.card_tables(rec_x, res["p1"], xinst, cfg.floors, n_beh=cfg.beh_rows)
        card_xe = _card(Rx, {**meta, "subset": "cross-check subset, economy per-instance pool"}, bx)
        rec_xa = [{**r, "residual_grader_accept": r["residualA_grader_accept"],
                   "residual_oracle_accept": r["residualA_oracle_accept"]} for r in rec_x]
        Rxa, _ = A.card_tables(rec_xa, res["p1"], xinst, cfg.floors, n_beh=cfg.beh_rows)
        card_xa = _card(Rxa, {**meta, "subset": "cross-check subset, fully paired per-instance pool"}, bx)
        hd.write_card(card_xe, out / "card_subset_economy.json")
        hd.write_card(card_xa, out / "card_subset_paired.json")
        lines += [f"cross-check subset: {len(xinst)} instances; residual floor by the economy pool and by the fully "
                  f"paired pool, side by side", side_by_side(card_xe, card_xa)]
    c = costs
    lines.append(
        f"costs: judge {c['judge_month_steps_computed']:,} month-steps in {c['judge_seconds']:.0f} s"
        + (f" ({c['judge_month_steps_per_s']:,.0f}/s)" if c["judge_month_steps_per_s"] else "")
        + f", padding {c['judge_padded_month_steps']:,}; engine {c['engine_city_months_replayed']:,} city-months replayed "
        f"in {c['engine_seconds']:.0f} s" + (f" ({c['engine_city_months_per_s']:,.0f}/s, local workers {c['engine_workers']}, "
                                              f"{c['engine_replays_remote']:,} replays remote)"
                                              if c["engine_city_months_per_s"] else "")
        + f"; per instance phase 1 {c['seconds_phase1_per_instance_mean']:.1f} s, phase 2 "
        f"{c['seconds_phase2_per_instance_mean']:.1f} s; design month-steps match counter: "
        f"{c['judge_month_steps_design_matches_counter']}")
    lines.append("wall clock per instance (s): " + ", ".join(f"{m} {v:.1f}" for m, v in c["wall_seconds_per_instance_by_method"].items())
                 + f", pool statistics {c['wall_seconds_per_instance_pool_statistics']:.1f}")
    if "design_amendment2" in c:
        d2 = c["design_amendment2"]
        tr = d2["this_run"]
        lines.append(f"design check (this run): rolled out by plan {tr['rolled_out']:,} (shared pool samples computed "
                     f"{tr['shared_computed']:,} of the plan's {tr['total'] - tr['rolled_out'] + tr['shared_computed']:,}), "
                     f"judge counter {c['judge_month_steps_computed']:,}: "
                     f"{'match' if tr['rolled_out'] == c['judge_month_steps_computed'] else 'DIFFER'}")
        fc = d2["full_checkpoint"]
        lines.append(f"full checkpoint ({len(universe)} instances, amendment 2), emulator month-steps: " +
                     "; ".join(f"{k} {v:,}" for k, v in fc["components"].items()) + f"; total {fc['total']:,}" +
                     (f" = {fc['hours_at_this_run_rate']:.2f} h at this run's {fc['rate']:,.0f}/s" if fc.get("rate") else ""))
    if "engine_majority" in c:
        em = c["engine_majority"]
        lines.append("engine replays requested by this run (distinct plan-seed pairs, cached or not), by purpose: "
                     + "; ".join(f"{k} {v:,}" for k, v in em["this_run_by_purpose"].items())
                     + f"; total {em['this_run_total']:,} = {em['this_run_total'] * cfg.H:,} city-months")
        fc = em["full_checkpoint"]
        rr = fc.get("rate_reference")
        for scope, sc in fc["by_flip_scope"].items():
            lines.append(
                f"full checkpoint ({fc['basis']['instances']} instances, amendment 2, majority oracle, flip scope {scope}"
                f"{' (this run)' if scope == fc['this_run_flip_scope'] else ''}; CEM candidates {fc['basis']['cem_counts']}), "
                f"engine city-months: per checkpoint {sc['per_checkpoint_city_months']:,} "
                f"({'; '.join(f'{k} {v:,}' for k, v in sc['per_checkpoint'].items())}); once for every checkpoint "
                f"{sc['shared_city_months']:,} ({'; '.join(f'{k} {v:,}' for k, v in sc['shared'].items())})"
                + (f"; at {rr['city_months_per_s']:,.0f} city-months/s ({rr['workers']}, {rr['file']}): "
                   f"{sc['hours_per_checkpoint_at_reference_rate']:.2f} h per checkpoint, "
                   f"{sc['hours_shared_once_at_reference_rate']:.2f} h once" if rr else ""))
    for label, p in c["projection_full"].items():
        bits = []
        if "judge_hours_at_measured_rate" in p:
            bits.append(f"judge {p['judge_month_steps']:,} month-steps = {p['judge_hours_at_measured_rate']:.2f} h")
        if "engine_hours_at_measured_rate" in p:
            bits.append(f"engine (oracle side) {p['engine_city_months_oracle_side_no_cache']:,} city-months = "
                        f"{p['engine_hours_at_measured_rate']:.2f} h")
        if bits:
            lines.append(f"projection, {p['instances']} instances, {','.join(p['methods'])} at B {p['budgets']}: " + "; ".join(bits))
    ec = engine.counters()
    cache_bytes1 = cache_size(a.engine_cache)
    costs["engine_cache"] = {"root": a.engine_cache, "bytes_on_disk_start": cache_bytes0, "bytes_on_disk_end": cache_bytes1,
                             "entries_written_by_this_run": ec.get("engine_rows_put"),
                             "value_bytes_written_by_this_run": ec.get("engine_bytes_put"),
                             "replays_kept_out_of_the_cache": ec.get("engine_replays_uncached"),
                             "note": "the size difference includes whatever other processes wrote meanwhile"}
    (out / "costs.json").write_text(json.dumps({"summary": costs, "per_instance": res["costs"]}, indent=1, default=float))
    lines.append(f"engine cache {a.engine_cache}: {cache_bytes1 / 1e9:.2f} GB on disk ({(cache_bytes1 - cache_bytes0) / 1e9:+.2f} GB "
                 f"since this invocation started, other writers included); this run wrote {ec.get('engine_rows_put', 0):,} "
                 f"entries ({ec.get('engine_bytes_put', 0) / 1e9:.2f} GB of values) and kept "
                 f"{ec.get('engine_replays_uncached', 0):,} replays (search candidates of the floors) out of it")
    txt = "\n".join(lines)
    (out / "table.txt").write_text(txt + "\n")
    print(txt, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
