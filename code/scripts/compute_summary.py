"""The study's compute in H200-equivalent hours , for the paper.

    CUDA_VISIBLE_DEVICES= .venv/bin/python code/scripts/compute_summary.py

Reads results/analysis/compute_local.json (compute_local.py: local card-hours by card and arm from the run logs),
results/analysis/compute_ledger.json (compute_ledger.py: rented pods from the closed ledger) and the throughput
multiples in code/cloud/compute_multiples.json (internal; fixed on 18 October 2026, before any run, from published card
specifications), and writes results/analysis/compute_summary.{json,md}. The output names no card, pod, price per card
or host and no dollar amount : H200-equivalent hours by arm and in total, the replanning runs'
instance wall-hours, the engine pool's process-hours, the models trained and what is not counted.

H200-equivalent hours = card-hours x (the card's multiple / the H200's). A card without a multiple is left out of every
equivalent total, and the hours left out are counted; no multiple is invented."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARMS = (("emulator training", "training"), ("fidelity evaluation", "fidelity"),
        ("audits, 40 original cities", "audits_original"), ("audits, 80 further cities", "audits_further"),
        ("pool-seeded searches", "pool_seeded"))


def build(local: dict, ledger: dict, mult: dict) -> dict:
    ref = float(mult["multiples"][mult["reference"]])
    names, M = mult["names"], mult["multiples"]

    def factor(card):
        k = names.get(card, card)
        return (float(M[k]) / ref) if k in M else None
    left = {"local_card_hours": 0.0, "rented_card_hours": 0.0, "rented_pods": 0}
    loc = {a: 0.0 for _, a in ARMS}
    for b in local["card_hours_by_card_and_arm"]:
        arm = dict(ARMS).get(b["arm"])
        if arm is None:
            raise SystemExit(f"compute_local.json: unknown arm {b['arm']!r}")
        f = factor(b["card"])
        if f is None:
            left["local_card_hours"] += b["card_hours"]
        else:
            loc[arm] += b["card_hours"] * f
    pods = ledger["pods"]
    if any(p.get("hours") is None for p in pods) or ledger["total"]["n_live"]:
        raise SystemExit("compute_ledger.json: a pod is live or has no hours")
    ok = "its job was fetched and checked"
    is_eval_ok = lambda p: p["stop_reason"] == ok or str(p.get("stop_reason") or "").endswith("completed and verified")
    none_ = [p for p in pods if p["category"].startswith("no run")
             or (p["category"].startswith("evaluation") and not is_eval_ok(p))]
    groups = {"rl": [p for p in pods if p["category"] in ("ladder RL", "other RL")],
              "evaluation": [p for p in pods if p["category"].startswith("evaluation")],
              "extended_training": [p for p in pods if p["category"].startswith("extended training")],
              "no_result": none_, "all": pods}

    def eq(ps):
        h = 0.0
        for p in ps:
            f = factor(p["gpu_type"])
            h += 0.0 if f is None else p["hours"] * f
        return h
    for p in pods:
        if factor(p["gpu_type"]) is None:
            left["rented_card_hours"] += p["hours"]
            left["rented_pods"] += 1
    rp = local["replanning"]["by_side_and_host"].values()
    emu = [v for v in rp if v["side"] == "emulator"]
    perf = [v for v in rp if v["side"] == "perfect emulator"]
    e = local["engine_pool"]
    return {
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit": "H200-equivalent hours",
        "conversion": ("card-hours weighted by throughput multiples fixed before the study from published card "
                       f"specifications (relative to an H200); not measured on our workload; "
                       f"{left['local_card_hours'] + left['rented_card_hours']:.1f} card-hours on cards without a "
                       "multiple left out"),
        "local": {"by_arm": loc, "total": sum(loc.values()), "models_trained": len(local["models_trained"]),
                  "unfinished_jobs_not_counted": len(local["unfinished_jobs_not_counted"]),
                  "worker_log_from": local["inputs"]["worker_log_first"],
                  "card_hours_definition": local["definition"]},
        "total_logged": sum(loc.values()) + eq(pods),
        "rented": {"pods": len(pods), "total": eq(pods),
                   "rl": eq(groups["rl"]), "rl_runs_rented": ledger["runs"]["ladder RL"].get("n_rented"),
                   "evaluation": eq(groups["evaluation"]), "evaluation_pods": len(groups["evaluation"]),
                   "evaluation_pods_with_result": sum(is_eval_ok(p) for p in groups["evaluation"]),
                   "extended_training": eq(groups["extended_training"]),
                   "no_result": eq(none_),
                   "no_result_pods": len(none_),
                   "no_result_rule": ("pods that ran no job, and evaluation pods whose job was not fetched and checked "
                                      "(setup and equivalence-check failures, a refused card, jobs past their planned "
                                      "end, a terminated pod)")},
        "left_out": left,
        "replanning": {"emulator_side_read": local["replanning"]["emulator_side_read"],
                       "emulator_instances": sum(v["instances"] for v in emu),
                       "emulator_instance_wall_hours": sum(v["hours"] for v in emu),
                       "perfect_instances": sum(v["instances"] for v in perf),
                       "perfect_instance_wall_hours": sum(v["hours"] for v in perf)},
        "engine_pool": {"audits": e["audits"], "process_hours": e["process_hours"],
                        "remote_replay_share": e["remote_replays"] / e["replays"] if e["replays"] else None},
        "not_counted": ["local evaluation jobs before the audit worker's log began, whose card no log records",
                        "jobs started and not finished",
                        "reinforcement learning run locally, whose card is not recorded",
                        "the engine time of threshold building and of reinforcement learning's engine-side phases",
                        "the second machine's processor time outside the engine pool",
                        "card-hours on cards without a throughput multiple"],
    }


def write_md(res: dict, path: Path) -> None:
    L, R = res["local"], res["rented"]
    lines = [f"# Compute in H200-equivalent hours\n\nGenerated {res['generated']} by `code/scripts/compute_summary.py`. "
             f"Conversion: {res['conversion']}.\n", "| arm | H200-equivalent hours |", "|---|---|"]
    lines += [f"| local, {a.replace('_', ' ')} | {h:.1f} |" for a, h in L["by_arm"].items()]
    lines += [f"| local, all logged | {L['total']:.1f} |", f"| rented, all {R['pods']} pods | {R['total']:.1f} |",
              f"| logged in total, local and rented | {res['total_logged']:.1f} |",
              f"| rented, reinforcement learning | {R['rl']:.1f} |",
              f"| rented, evaluation jobs ({R['evaluation_pods_with_result']} of {R['evaluation_pods']} pods returned one) | {R['evaluation']:.1f} |",
              *( [f"| rented, extended training | {R['extended_training']:.1f} |"] if R.get("extended_training", 0.0) > 0 else [] ),
              f"| rented, no result ({R['no_result_pods']} pods) | {R['no_result']:.1f} |"]
    rp, e = res["replanning"], res["engine_pool"]
    lines.append(f"\nReplanning, instance wall-hours: emulator side {rp['emulator_instance_wall_hours']:.1f} "
                 f"({rp['emulator_instances']} instances), perfect-emulator sides {rp['perfect_instance_wall_hours']:.1f} "
                 f"({rp['perfect_instances']} instances). Engine pool: {e['process_hours']:.0f} process-hours over "
                 f"{e['audits']} audits. Models trained: {L['models_trained']}. Left out: "
                 f"{res['left_out']['local_card_hours'] + res['left_out']['rented_card_hours']:.1f} card-hours on cards "
                 f"without a multiple ({res['left_out']['rented_pods']} rented pods).")
    lines.append("\nNot counted: " + "; ".join(res["not_counted"]) + ".")
    path.write_text("\n".join(lines) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--local", default=str(REPO / "results/analysis/compute_local.json"))
    ap.add_argument("--ledger", default=str(REPO / "results/analysis/compute_ledger.json"))
    ap.add_argument("--multiples", default=str(REPO / "code/cloud/compute_multiples.json"))
    ap.add_argument("--out", default=str(REPO / "results/analysis/compute_summary"))
    a = ap.parse_args(argv)
    res = build(*(json.loads(Path(x).read_text()) for x in (a.local, a.ledger, a.multiples)))
    Path(a.out + ".json").write_text(json.dumps(res, indent=1) + "\n")
    write_md(res, Path(a.out + ".md"))
    print(f"compute_summary: local {res['local']['total']:.1f}, rented {res['rented']['total']:.1f} H200-equivalent hours")


if __name__ == "__main__":
    main()
