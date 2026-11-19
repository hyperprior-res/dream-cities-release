"""The defence frontier : run settings, or write the frontier from the records.

Resumable: every judge call, preparation, detector fit and record is kept under ``--work``; a re-run computes only what
is missing. One command per setting (``--settings halt95``) or all (``--settings all``, the default); ``--report``
writes ``frontier.md`` / ``frontier.json`` from whatever records exist; ``--cost`` prints the design's emulator
month-steps and exits.

    CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=hpr-dream:code .venv/bin/python \\
        code/scripts/run_defences.py --settings all --device cuda:0 --workers 8 --remote host-b --remote-workers 22
"""

from __future__ import annotations

import argparse
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

from dc import audit as A  # noqa: E402
from dc import defences as D  # noqa: E402

TASKS = REPO / "data" / "tasks_v2_H24.json"
WORK = Path("<cache>/defences/work")
OUT = REPO / "results" / "defences"
REF = {"random": REPO / "results/audit/engine_reference/tasks_v2_H24/B_economy",
       "cem_seeded": REPO / "results/audit/engine_reference/tasks_v2_H24/cem_seeded_B_economy"}
MAIN = {"random": REPO / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24",
        "cem_seeded": REPO / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded"}


def git_state() -> dict:
    rev = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    st = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"], capture_output=True, text=True).stdout
    files = ("code/dc/defences.py", "code/scripts/run_defences.py", "code/dc/audit.py")
    return {"rev": rev, "dirty_files": [l for l in st.splitlines() if l.strip()][:50],
            "file_sha256": {f: A._sha256_file(REPO / f) for f in files}}


def parse(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--settings", default="all", help="'all' or a comma list of " + ", ".join(D.SETTING_BY_NAME))
    p.add_argument("--searches", default=",".join(D.SEARCHES))
    p.add_argument("--members", default=",".join(D.CHECKPOINTS), help="the three checkpoints; member 0 first")
    p.add_argument("--tasks", default=str(TASKS))
    p.add_argument("--work", default=str(WORK))
    p.add_argument("--out", default=str(OUT))
    p.add_argument("--device", default="cuda:0")
    p.add_argument("--chunk", type=int, default=256)
    p.add_argument("--buckets", default="16,64,144,256")
    p.add_argument("--model-src", default="auto")
    p.add_argument("--graphs", action="store_true", help="CUDA graphs for the trunks (off by default: each member's "
                   "graphs keep a private activation pool, and GPU 0 is shared)")
    p.add_argument("--gpu-mem-gb", type=float, default=18.0, help="cap on this process's CUDA allocator (GB)")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--remote", default="", choices=["", "host-b"])
    p.add_argument("--remote-workers", type=int, default=22)
    p.add_argument("--engine-cache", default=str(A.CACHE_ROOT / "engine_cache"))
    p.add_argument("--stage", default="all", choices=["all", "prep"], help="prep: stage 1 only")
    p.add_argument("--shard", default="0/1", help="k/n: this process prepares and searches instances k, k+n, ...; "
                   "the detector fit waits for every instance's preparation")
    p.add_argument("--report", action="store_true", help="write the frontier from the records and exit")
    p.add_argument("--cost", action="store_true", help="print the design's month-steps and exit")
    return p.parse_args(argv)


def settings_of(spec: str):
    if spec == "all":
        return list(D.SETTINGS)
    out = []
    for name in spec.split(","):
        if name not in D.SETTING_BY_NAME:
            raise SystemExit(f"unknown setting {name!r}; choose from {list(D.SETTING_BY_NAME)}")
        out.append(D.SETTING_BY_NAME[name])
    return out


def instances_of(tasks):
    universe = A.load_instances(tasks)
    return universe, A.select_instances(universe, D.N_INSTANCES)


def load_member(ckpt, a, buckets):
    """The audit's emulator judge (``dc.fast``: fused trunk, compiled), with CUDA graphs only under ``--graphs``; the
    judge's description records which (``fast.describe``)."""
    import torch
    if torch.device(a.device).type == "cuda" and a.gpu_mem_gb > 0:
        dev = torch.device(a.device)
        total = torch.cuda.get_device_properties(dev).total_memory
        torch.cuda.set_per_process_memory_fraction(min(1.0, a.gpu_mem_gb * 1e9 / total), dev)
    if a.graphs or torch.device(a.device).type != "cuda":
        return A.EmulatorJudge(ckpt, device=a.device, chunk=a.chunk, buckets=buckets, compile_trunk=True,
                               model_src=a.model_src, H=24, fast=True)
    from dc import fast
    J = A.EmulatorJudge(ckpt, device=a.device, chunk=a.chunk, buckets=buckets, compile_trunk=False,
                        model_src=a.model_src, H=24, fast=False)
    fast.accelerate(J.model, graphs=False)
    J.compiled, J.fast = True, True
    return J


def build(a):
    universe, instances = instances_of(a.tasks)
    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    remote = A.host_b_pool(a.remote_workers, log_path=work / "remote_stderr.log") if a.remote == "host-b" else None
    engine = A.EngineJudge(a.engine_cache, workers=a.workers, H=24, remote=remote, log=lambda s: print(s, flush=True))
    engine._get_pool()                 # the replay processes start before CUDA is initialised
    if remote is not None:             # the two machines must replay identically
        i0 = instances[0]
        rel = str(Path(i0.cty).resolve().relative_to(A.REPO))
        remote.check_files([rel])
        raw = A.Pools(H=24).behaviour(i0.start_id)[:6]
        plans = np.concatenate([A.effective(raw, "grow", 24), A.effective(raw, "recover", 24)])
        jobs = [(i0.cty, plans[j].tobytes(), 24, A.seed_for("remote-check", j)) for j in range(len(plans))]
        same = engine._local(jobs) == remote.map([(rel,) + j[1:] for j in jobs])
        print(f"remote pool on {remote.host}: {remote.workers} workers; identical replays on {len(jobs)} check plans: "
              f"{same}", flush=True)
        if not same:
            raise SystemExit("remote replays differ from local replays")
    buckets = tuple(int(x) for x in a.buckets.split(","))
    members = [load_member(c, a, buckets) for c in a.members.split(",")]
    spec = A.oracle_spec(a.tasks)
    if not spec:
        raise SystemExit("the tasks file has no majority oracle")
    fr = D.Frontier(instances, members, engine, A.Pools(H=24), work, oracle_n=spec["n_seeds"], universe=universe,
                    log=lambda s: print(s, flush=True))
    return fr, engine, universe, instances


def _prep_done(fr, inst) -> bool:
    p = fr._prep_path(inst)
    return p.exists() and A._load_pickle(p).get("tag") == fr.tag_digest


def counters(fr) -> dict:
    js = [*fr.members, *[j for t, j in fr.tempered.items() if t != 1.0]]
    return {"store_month_steps_computed": fr.store.computed_month_steps,
            "judges": [{"describe_digest": fr.store.jd(j), **{k: v for k, v in j.counters().items()}} for j in js]}


def run(a, argv) -> int:
    settings = settings_of(a.settings)
    searches = [s for s in a.searches.split(",") if s]
    for s in searches:
        if s not in D.SEARCHES:
            raise SystemExit(f"unknown search {s}")
    t0 = time.time()
    fr, engine, universe, instances = build(a)
    work = Path(a.work)
    meta = {"argv": [sys.argv[0]] + list(argv or sys.argv[1:]), "tag_digest": fr.tag_digest, "tag": fr.tag,
            "git": git_state(), "instances": [i.key for i in instances], "settings": [s.name for s in settings],
            "searches": searches, "started_utc": dt.datetime.utcnow().isoformat(timespec="seconds")}
    (work / "frontier_tag.json").write_text(json.dumps(meta, indent=1, default=str))
    with open(work / "invocations.jsonl", "a") as f:
        f.write(json.dumps(meta, default=str) + "\n")
    print(f"defences: {len(instances)} instances ({len({i.family_id for i in instances})} families), settings "
          f"{[s.name for s in settings]}, searches {searches}, tag {fr.tag_digest}", flush=True)
    k_sh, n_sh = (int(x) for x in a.shard.split("/"))
    mine = instances[k_sh::n_sh]
    try:
        for k, inst in enumerate(mine):               # stage 1
            fr.prepare(inst)
            print(f"prep {k + 1}/{len(mine)} (shard {a.shard}); {fr.store.computed_month_steps:,} month-steps computed, "
                  f"{time.time() - t0:.0f} s", flush=True)
        if a.stage == "prep":
            return 0
        if any(s.defence == "detector" for s in settings):      # stage 2
            while n_sh > 1 and not all(_prep_done(fr, i) for i in instances):
                time.sleep(30)                         # the other shards' preparations
            det = fr.detectors()
            for f, d in det["folds"].items():
                print(f"detector fitted on fold {f}: " + "; ".join(
                    f"{k}: n {d[k]['model'].n} ({d[k]['model'].n_pos} positive), converged {d[k]['model'].converged}, "
                    f"AUC on the other fold {d[k]['auc_other_fold'].get('value')}" for k in ("search", "verdict")),
                    flush=True)
        for se in searches:                             # stage 3, search by search, instance by instance
            for k, inst in enumerate(mine):
                fr.run_instance(inst, settings, [se])
                print(f"{se}: {k + 1}/{len(mine)} instances (shard {a.shard}); {fr.store.computed_month_steps:,} month-steps "
                      f"computed in this invocation, {time.time() - t0:.0f} s", flush=True)
    finally:
        with open(work / "costs.jsonl", "a") as f:
            f.write(json.dumps({"ended_utc": dt.datetime.utcnow().isoformat(timespec="seconds"),
                                "seconds": time.time() - t0, **counters(fr), "engine": engine.counters()},
                               default=str) + "\n")
        engine.close()
    if n_sh == 1:
        report(a)
    return 0


def _rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(REPO))
    except ValueError:
        return str(p)


def _ref_records(d: Path, method: str, keys: set) -> list:
    if not (d / "records.jsonl.gz").exists():
        return []
    return [r for r in A.read_records(d / "records.jsonl.gz")
            if r["method"] == method and int(r["budget"]) == D.BUDGET and r["instance"] in keys]


def report(a) -> int:
    work, out = Path(a.work), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = json.loads((work / "frontier_tag.json").read_text())
    tag = meta["tag_digest"]
    universe, instances = instances_of(a.tasks)
    keys = [i.key for i in instances]
    recs = []
    for p in sorted((work / "records").glob("*/*/*.json")):
        r = json.loads(p.read_text())
        if r.get("tag") == tag:
            recs.append(r)
    perfect = {se: _ref_records(REF[se], se, set(keys)) for se in D.SEARCHES}
    table = D.frontier_table(recs, perfect, keys)
    # detector and deflation summaries
    det = None
    if (work / "detectors.pkl").exists():
        d = A._load_pickle(work / "detectors.pkl")
        if d.get("tag") == tag:
            det = {"fold_of_family": d["fold_of_family"],
                   "folds": {str(f): {"fit_instances": v["fit_instances"], "test_instances": v["test_instances"],
                                      **{k: {"model": v[k]["model"].as_dict(), "auc_other_fold": v[k]["auc_other_fold"],
                                             "n_test": v[k]["n_test"], "n_test_positive": v[k]["n_test_positive"]}
                                         for k in ("search", "verdict")}}
                             for f, v in d["folds"].items()}}
    if det:     # the verdict detector (of the other fold) on the undefended ensemble's selected plans; label: hacked
        d = A._load_pickle(work / "detectors.pkl")
        fam = {i.key: i.family_id for i in instances}
        det["selected_plans_auc"] = {}
        for se in D.SEARCHES:
            rs = [r for r in recs if r["search"] == se and r["setting"] == "ensemble"]
            if not rs:
                continue
            X = np.array([[r["grader_mean_margin"], r["grader_p"], r["grader_disagreement"], r["grader_monthly_spread"],
                           r["plan_macro_share"]] for r in rs])
            p = np.array([d["folds"][1 - d["fold_of_family"][fam[r["instance"]]]]["verdict"]["model"].prob(X[k:k + 1])[0]
                          for k, r in enumerate(rs)])
            y = np.array([bool(r["grader_accept"]) and not bool(r["oracle_accept"]) for r in rs])
            det["selected_plans_auc"][se] = (
                {**D.hd.auc(p, y, [r["cluster"] for r in rs], bca=True).as_dict(), "n": len(rs), "n_hacked": int(y.sum())}
                if 0 < y.sum() < y.size else {"value": None, "status": "one class", "n": len(rs), "n_hacked": int(y.sum())})
    preps = []
    for i in instances:
        p = work / "prep" / f"{i.file_stem}.pkl"
        if p.exists():
            d = A._load_pickle(p)
            if d.get("tag") == tag:
                preps.append(d)
    defl = {}
    for j in ("member0", "ensemble"):
        al = np.array([d["deflation"][j]["alpha"] for d in preps]) if preps else np.zeros(0)
        mb = np.array([d["deflation"][j]["mu_bar"] for d in preps]) if preps else np.zeros(0)
        defl[j] = {"n_instances": int(al.size),
                   "alpha_quantiles_0_25_50_75_100": np.quantile(al, [0, .25, .5, .75, 1]).tolist() if al.size else None,
                   "mu_bar_quantiles_0_25_50_75_100": np.quantile(mb, [0, .25, .5, .75, 1]).tolist() if mb.size else None,
                   "n_alpha_zero": int((al == 0).sum()), "n_mu_bar_zero": int((mb == 0).sum())}
    halt = {str(q): (np.quantile([d["halt"][q] for d in preps], [0, .5, 1]).tolist() if preps else None)
            for q in D.HALT_PERCENTILES}
    # cross-check: member 0 undefended against the main run's records on the same instances
    cross = {}
    for se in D.SEARCHES:
        main = {r["instance"]: r for r in _ref_records(MAIN[se], se, set(keys))}
        mine = {r["instance"]: r for r in recs if r["search"] == se and r["setting"] == "member0"}
        common = sorted(set(main) & set(mine))
        if common:
            ga_m = np.array([main[k]["grader_p"] >= D.ACCEPT_P for k in common])
            oa_m = np.array([bool(main[k]["oracle_accept"]) for k in common])
            ga = np.array([mine[k]["grader_accept"] for k in common])
            oa = np.array([bool(mine[k]["oracle_accept"]) for k in common])
            cl = [main[k]["cluster"] for k in common]
            cross[se] = {"run": str(MAIN[se]), "n_instances": len(common),
                         "same_selected_plan": int(sum(main[k]["plan_hash"] == mine[k]["plan_hash"] for k in common)),
                         "main_run_hackability": D.hd.hackability(ga_m, oa_m, cl, bca=True).as_dict(),
                         "this_run_hackability": D.hd.hackability(ga, oa, cl, bca=True).as_dict(),
                         "same_judge_verdict": int((ga == ga_m).sum()), "same_oracle_verdict": int((oa == oa_m).sum())}
        else:
            cross[se] = {"status": f"no common records ({MAIN[se]})"}
    costs = [json.loads(l) for l in (work / "costs.jsonl").read_text().splitlines()] if (work / "costs.jsonl").exists() else []
    prep_ms = int(sum(d["costs"]["month_steps_computed"] for d in preps))
    fr_sk = (lambda i: i.forced_key)
    design = D.design_cost(instances, fr_sk)
    js = {"generated_utc": dt.datetime.utcnow().isoformat(timespec="seconds"), "work": str(work), "tag_digest": tag,
          "instances": keys, "n_instances": len(keys), "n_families": len({i.family_id for i in instances}),
          "design": {"budget": D.BUDGET, "searches": list(D.SEARCHES), "k_search_per_member": D.K_SEARCH,
                     "k_verdict_per_member": D.K_VERDICT, "temperatures": list(D.TEMPERATURES),
                     "lambdas": list(D.LAMBDAS), "halt_percentiles": list(D.HALT_PERCENTILES),
                     "detector_thresholds": list(D.DETECTOR_THRESHOLDS), "detector_plans": D.DETECTOR_PLANS,
                     "detector_features": list(D.FEATURES), "disagreement_ddof": D.DDOF,
                     "members": meta["tag"]["ensemble"]["members"] if "ensemble" in meta["tag"] else None,
                     "perfect_emulator": {se: str(REF[se]) for se in D.SEARCHES}},
          "frontier": table, "detector": det, "deflation": defl, "halt_thresholds_min_median_max": halt,
          "cross_check_main_run": cross,
          "costs": {"design_month_steps": design, "prep_month_steps_computed": prep_ms,
                    "invocations": costs, "n_records": len(recs)},
          "policy_aware": D.POLICY_AWARE_SLOT}
    js = D._jsonable(js)
    (out / "frontier.json").write_text(json.dumps(js, indent=1))
    hdr = ["# Defence frontier ", "",
           f"Generated by `code/scripts/run_defences.py --report` at {js['generated_utc']}Z from `{work}` (tag {tag}). "
           f"{len(keys)} instances (`dc.audit.select_instances(all, {D.N_INSTANCES})` on `{_rel(a.tasks)}`, "
           f"{len(keys) // 5} per task family, {js['n_families']} families). Hackability: the judge (with its defence) accepts the selected plan "
           f"and the 32-seed majority oracle rejects it; false rejection: among selected plans the oracle accepts, the "
           f"share the judge rejects; oracle pass share: the mean over instances of the oracle's pass share of the "
           f"selected plan. Cluster bootstrap over families, 2,000 resamples, seed 0, BCa 95 % (`hpr_dream.stats`); "
           f"`*` the percentile interval (BCa undefined), `†` no hacked unit: the exact one-sided bound on clusters. "
           f"The perfect emulator is the engine judging itself on fresh seeds under the same search on the same "
           f"instances (`{_rel(REF['random'])}`, `{_rel(REF['cem_seeded'])}`). Settings, "
           f"formulas and what they assume: `code/dc/defences.py` (module docstring) and "
           f"the working notes. The policy-aware model is a slot (another builder)."]
    md = D.frontier_md(table, hdr)
    if det:
        md += "\n## Detector (logistic regression, two folds by family)\n\n"
        md += "| fitted on fold | features | n fit (positive) | converged | AUC on the other fold's plans (n, positive) |\n"
        md += "|---|---|---|---|---|\n"
        for f, v in det["folds"].items():
            for k in ("search", "verdict"):
                m = v[k]["model"]
                md += (f"| {f} | {k} samples | {m['n']} ({m['n_positive']}) | {m['converged']} | "
                       f"{D._ci(v[k]['auc_other_fold'])} ({v[k]['n_test']}, {v[k]['n_test_positive']}) |\n")
    if det and det.get("selected_plans_auc"):
        md += ("\nThe verdict detector of the other fold on the undefended ensemble's selected plans (label: hacked): " +
               "; ".join(f"{se} {D._ci(v)} (n {v['n']}, hacked {v['n_hacked']})" for se, v in det["selected_plans_auc"].items())
               + ".\n")
    md += "\n## Deflation (Smith and Winkler, eq. 6a-6b), per instance\n\n"
    for j, v in defl.items():
        md += (f"- {j}: alpha quantiles (0, .25, .5, .75, 1) {np.round(v['alpha_quantiles_0_25_50_75_100'], 3).tolist() if v['alpha_quantiles_0_25_50_75_100'] else None}; "
               f"mu_bar quantiles {np.round(v['mu_bar_quantiles_0_25_50_75_100'], 3).tolist() if v['mu_bar_quantiles_0_25_50_75_100'] else None}; "
               f"alpha = 0 on {v['n_alpha_zero']} of {v['n_instances']} instances, mu_bar = 0 on {v['n_mu_bar_zero']}.\n")
    md += "\n## Cost (emulator month-steps)\n\n"
    md += (f"- As designed: {design['total']:,} over {design['instances']} instances and {design['start_share_groups']} "
           f"(start, forced-event) groups (" + ", ".join(f"{k} {v:,}" for k, v in design.items()
                                                         if k not in ("total", "instances", "start_share_groups")) + ").\n"
           f"- Computed: preparation {prep_ms:,}; seeded-search generations " +
           ", ".join(f"{se} {sum(r.get('month_steps', {}).get('search_computed', 0) for r in table[se]['rows']):,}"
                     for se in D.SEARCHES if se in table) +
           f"; every invocation's counter: {sum(c.get('store_month_steps_computed', 0) for c in costs):,}.\n")
    md += "\n## Cross-check: member 0 undefended against the main run's records on these instances\n\n"
    for se, v in cross.items():
        if "n_instances" in v:
            md += (f"- {se}: {v['n_instances']} instances; same selected plan on {v['same_selected_plan']}; same judge "
                   f"verdict on {v['same_judge_verdict']}; hackability here {D._ci(v['this_run_hackability'])}, main run "
                   f"{D._ci(v['main_run_hackability'])}.\n")
        else:
            md += f"- {se}: {v['status']}.\n"
    (out / "frontier.md").write_text(md)
    print(f"wrote {out / 'frontier.md'} and {out / 'frontier.json'} ({len(recs)} records)", flush=True)
    return 0


def main(argv=None) -> int:
    a = parse(argv)
    if a.cost:
        _, instances = instances_of(a.tasks)
        print(json.dumps(D.design_cost(instances, lambda i: i.forced_key), indent=1))
        return 0
    if a.report:
        return report(a)
    return run(a, argv)


if __name__ == "__main__":
    raise SystemExit(main())
