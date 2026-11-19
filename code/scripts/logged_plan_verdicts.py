#!/usr/bin/env python
"""The emulator's verdict on logged plans, by task family .

One command, from the repository root:

    PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/logged_plan_verdicts.py

For every ladder checkpoint (enumerated as ``analyse_ladder.discover_ladder`` does: 24) and the coverage model
(``os_50m_cov`` at 6,000,000 samples), on the 40 cities' random-search audit
(``results/audit/ladder/<run>/samples_<N>/tasks_v2_H24/``), per task family over the first
``behaviour_plans_per_instance`` (100) logged behaviour plans of every instance:

- the share of oracle-accepted plans the emulator rejects (false rejection on logged plans), with its counts;
- the share of oracle-rejected plans the emulator accepts (false acceptance on logged plans), with its counts.

The emulator accepts a plan when its pass share over 8 fresh samples is at least 0.5 (``dc.audit.ACCEPT_P``;
array ``<instance>__behaviour_grader_p`` of ``pools.npz``); the oracle accepts it when the 32-seed majority margin
is at least 0 (array ``<instance>__behaviour_engine_margin``, the rule of ``dc.audit.Audit.flip_rates``; checked
against ``<instance>__behaviour_oracle_share`` >= 0.5). Every rate is recomputed from the arrays and checked
against ``pool_stats.json`` (``flip_rates.by_task``, exact) and the header of ``table.txt`` (to its three printed
decimals). Intervals: cluster bootstrap over city families (the instance's ``family_id``; plans are units), 2,000
resamples, seed 0, BCa with the percentile interval where BCa is undefined (``hpr_dream.stats``; the convention of
the audit's reference tables and of ``analyse_ladder``'s audit measurements).

Outputs: ``results/analysis/logged_plan_verdicts.json`` and ``.md``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(ROOT / "hpr-dream"))
sys.path.insert(0, str(ROOT / "code" / "scripts"))

import numpy as np  # noqa: E402

import analyse_ladder as AL  # noqa: E402  (ladder enumeration, Reader, intervals; nothing is edited)
import hpr_dream.stats as hs  # noqa: E402
from dc import audit as A  # noqa: E402
from dc import tasks as T  # noqa: E402

OUT = ROOT / "results" / "analysis"
FAMILIES = AL.FAMILIES
HEADER_RE = re.compile(r"(\w+) fp ([0-9.]+) fn ([0-9.]+)")
SUFFIX_P, SUFFIX_M, SUFFIX_S = "__behaviour_grader_p", "__behaviour_engine_margin", "__behaviour_oracle_share"


def confusion(grader_p: np.ndarray, margin: np.ndarray) -> dict:
    """Counts and rates of the 8-sample verdict against the oracle's (the rule of ``Audit.flip_rates``)."""
    g = np.asarray(grader_p, float) >= A.ACCEPT_P
    o = np.asarray(margin, float) >= 0
    n_oa, n_or = int(o.sum()), int((~o).sum())
    n_fr, n_fa = int((~g & o).sum()), int((g & ~o).sum())
    return {"n_plans": int(g.size), "n_oracle_accept": n_oa, "n_oracle_reject": n_or,
            "n_emulator_rejects_oracle_accepted": n_fr, "n_emulator_accepts_oracle_rejected": n_fa,
            "false_rejection": n_fr / n_oa if n_oa else float("nan"),
            "false_acceptance": n_fa / n_or if n_or else float("nan"),
            "emulator_accept_rate": float(g.mean()) if g.size else float("nan"),
            "oracle_accept_rate": float(o.mean()) if o.size else float("nan")}


def parse_header(text: str) -> dict:
    """The table header's per-family fp / fn (three decimals) and the plan count."""
    first = text.splitlines()[0] if text else ""
    m = re.search(r"family confusion rates on (\d+) behaviour plans: (.*?); oracle", first)
    if not m:
        return {}
    return {"n_plans": int(m.group(1)),
            "by_task": {t: {"fp": float(fp), "fn": float(fn)} for t, fp, fn in HEADER_RE.findall(m.group(2))}}


def audit_dir(root: Path, entry: dict, stem: str) -> Path:
    return root / "results" / "audit" / "ladder" / entry["run"] / f"samples_{entry['samples']:09d}" / stem


def read_one(entry: dict, tasks: dict, family_of: dict, root: Path, rd: AL.Reader, n_boot: int, seed: int) -> dict:
    d = audit_dir(root, entry, tasks["stem"])
    out = {"checkpoint": entry["checkpoint"], "run": entry["run"], "samples": entry["samples"], "stage": entry["stage"],
           "dir": str(d.relative_to(root)) if d.is_relative_to(root) else str(d), "checks": []}
    if not d.is_dir():
        out["status"] = "not stored: no 40-city random-search audit directory"
        return out
    cfg, ps, z = rd.json(d / "config.json"), rd.json(d / "pool_stats.json"), rd.npz(d / "pools.npz")
    if cfg is None or z is None:
        out["status"] = "not stored: config.json or pools.npz absent or unreadable"
        return out
    if cfg.get("config", {}).get("tasks_sha256") != tasks["sha256"]:
        out["status"] = "not used: the audit ran on another tasks file"
        return out
    fr = (ps or {}).get("flip_rates")
    stems = sorted(k[: -len(SUFFIX_P)] for k in z.files if k.endswith(SUFFIX_P))
    if not fr:
        n_nan = sum(int(np.isnan(np.asarray(z[s + SUFFIX_P], float)).sum()) for s in stems)
        n_all = sum(int(np.asarray(z[s + SUFFIX_P]).size) for s in stems)
        if n_all == 0 or n_nan > 0:
            out["status"] = (f"not stored: a run without floors (config floors {cfg.get('config', {}).get('floors')}); "
                             f"pools.npz holds the oracle's verdicts on the logged plans but no 8-sample emulator "
                             f"verdict ({n_nan} of {n_all} behaviour_grader_p values are NaN)")
            return out
        out["status"] = "not used: emulator verdicts stored without pool_stats.json flip_rates to check them against"
        return out
    n_rows = int(fr["behaviour_plans_per_instance"])
    keys = {s.replace("__", "|") for s in stems}
    expected = set().union(*tasks["instances"].values())
    if keys != expected:
        out["status"] = f"not used: pools.npz holds {len(keys & expected)} of {len(expected)} instances"
        return out
    out["behaviour_plans_per_instance"] = n_rows
    table = (d / "table.txt").read_text() if (d / "table.txt").is_file() else ""
    if table:
        rd.note(d / "table.txt", table.encode())
    hdr = parse_header(table)
    fam_res, share_mismatch = {}, 0
    for f in FAMILIES:
        fs = [s for s in stems if s.split("__")[1] == f]
        gp = [np.asarray(z[s + SUFFIX_P], float)[:n_rows] for s in fs]
        mg = [np.asarray(z[s + SUFFIX_M], float)[:n_rows] for s in fs]
        if any(a.size != n_rows for a in gp + mg):
            out["status"] = f"not used: an instance of {f} holds fewer than {n_rows} behaviour plans"
            return out
        if all(s + SUFFIX_S in z.files for s in fs):
            sh = np.concatenate([np.asarray(z[s + SUFFIX_S], float)[:n_rows] for s in fs])
            share_mismatch += int(((sh >= T.ORACLE_PASS) != (np.concatenate(mg) >= 0)).sum())
        g_all, m_all = np.concatenate(gp), np.concatenate(mg)
        cl = np.repeat([family_of[s.replace("__", "|")] for s in fs], n_rows)
        c = confusion(g_all, m_all)
        c["n_instances"] = len(fs)
        c["n_city_families"] = int(np.unique(cl).size)
        g, o = g_all >= A.ACCEPT_P, m_all >= 0
        c["false_rejection_estimate"] = (hs.conditional_mean((~g).astype(float), o, cl, n_boot=n_boot, seed=seed,
                                                             bca=True) if o.any() else None)
        c["false_acceptance_estimate"] = (hs.conditional_mean(g.astype(float), ~o, cl, n_boot=n_boot, seed=seed,
                                                              bca=True) if (~o).any() else None)
        # checks against the stored rates
        st = fr["by_task"].get(f)
        if st is None:
            out["checks"].append(f"{f}: pool_stats.json has no row")
        else:
            same = (st["n_oracle_accept"] == c["n_oracle_accept"] and st["n_oracle_reject"] == c["n_oracle_reject"]
                    and st["n_behaviour_plans"] == c["n_plans"]
                    and math.isclose(st["fn"], c["false_rejection"] if c["n_oracle_accept"] else 0.0, abs_tol=1e-12)
                    and math.isclose(st["fp"], c["false_acceptance"] if c["n_oracle_reject"] else 0.0, abs_tol=1e-12))
            if not same:
                raise SystemExit(f"{d}: {f}: the arrays disagree with pool_stats.json ({st} against {c})")
        h = hdr.get("by_task", {}).get(f)
        if h is not None:
            ok = (abs(h["fn"] - round(c["false_rejection"], 3)) < 5e-4 + 1e-12 and
                  abs(h["fp"] - round(c["false_acceptance"], 3)) < 5e-4 + 1e-12)
            if not ok:
                raise SystemExit(f"{d}: {f}: the arrays disagree with table.txt's header ({h})")
        fam_res[f] = c
    pooled = confusion(np.concatenate([np.asarray(z[s + SUFFIX_P], float)[:n_rows] for s in stems]),
                       np.concatenate([np.asarray(z[s + SUFFIX_M], float)[:n_rows] for s in stems]))
    if not (pooled["n_oracle_accept"] == fr["n_oracle_accept"] and pooled["n_oracle_reject"] == fr["n_oracle_reject"]):
        raise SystemExit(f"{d}: pooled counts disagree with pool_stats.json")
    out["families"] = fam_res
    out["all_plans_pooled"] = pooled
    out["checks"].append("arrays equal pool_stats.json flip_rates.by_task (counts and rates) in every family")
    out["checks"].append("arrays equal table.txt's header to its three decimals in every family" if hdr.get("by_task")
                         else "table.txt header absent or unparsed: not cross-checked")
    out["checks"].append(f"oracle margin >= 0 agrees with oracle pass share >= {T.ORACLE_PASS} on every plan"
                         if share_mismatch == 0 else
                         f"oracle margin >= 0 and pass share >= {T.ORACLE_PASS} disagree on {share_mismatch} plans")
    out["status"] = "ok"
    return out


def gather(root: Path, ckpt_root: Path, tasks_path: Path, n_boot: int, seed: int) -> dict:
    rd = AL.Reader(root)
    tasks = AL.load_tasks(tasks_path)
    rd.note(tasks_path, Path(tasks_path).read_bytes())
    family_of = {f"{i['start_id']}|{i['task']}|H{int(i['horizon'])}": i["family_id"]
                 for i in json.loads(Path(tasks_path).read_text())["instances"]}
    ladder, notes = AL.discover_ladder(ckpt_root, rd)
    cov = AL.single_entry(ckpt_root, AL.COV_RUN, AL.COV_SAMPLES, rd)
    entries = [dict(e, role="ladder") for e in ladder]
    if cov is not None:
        entries.append(dict(cov, role="coverage model"))
    else:
        notes.append(f"{AL.COV_RUN} at {AL.COV_SAMPLES} samples not found under {ckpt_root}")
    rows = []
    for e in entries:
        r = read_one(e, tasks, family_of, root, rd, n_boot, seed)
        r["role"] = e["role"]
        r["objective"], r["size"], r["data_index"] = e["objective"], e["size"], e["data_index"]
        rows.append(r)
    return {"rows": rows, "ladder_notes": notes, "n_ladder": len(ladder), "tasks": tasks, "manifest": rd.manifest}


def _est(e):
    return e.as_dict() if isinstance(e, hs.Estimate) else e


def fb(e, d: int = 3) -> str:
    return AL.fb(e, d) if isinstance(e, hs.Estimate) else "n/a"


def write_md(path: Path, g: dict, cmd: str, generated: str, n_boot: int):
    rows = g["rows"]
    ok = [r for r in rows if r["status"] == "ok"]
    L = ["# The emulator's verdict on logged behaviour plans, by task family ", "",
         f"Generated {generated} by `{cmd}`. {len(ok)} of {len(rows)} checkpoints ({g['n_ladder']} ladder checkpoints and "
         "the coverage model) have the arrays. 40 cities (`data/tasks_v2_H24.json`), random-search audit, the first 100 "
         "logged behaviour plans of each instance. Emulator accepts: pass share over 8 fresh samples >= 0.5; oracle "
         "accepts: 32-seed majority margin >= 0. False rejection: among oracle-accepted plans, the share the emulator "
         "rejects. False acceptance: among oracle-rejected plans, the share the emulator accepts. Value [95 % BCa; `*` "
         f"percentile where BCa is undefined], cluster bootstrap over city families (plans are units), {n_boot} "
         "resamples, seed 0; counts are emulator-wrong / oracle-class plans.", ""]
    for kind, title in (("false_rejection", "False rejection on logged plans (oracle accepts, emulator rejects)"),
                        ("false_acceptance", "False acceptance on logged plans (oracle rejects, emulator accepts)")):
        L += [f"## {title}", "", "| checkpoint | stage | " + " | ".join(FAMILIES) + " | all plans |",
              "|---|---|" + "---|" * (len(FAMILIES) + 1)]
        nk = "n_emulator_rejects_oracle_accepted" if kind == "false_rejection" else "n_emulator_accepts_oracle_rejected"
        dk = "n_oracle_accept" if kind == "false_rejection" else "n_oracle_reject"
        for r in rows:
            name = r["checkpoint"] + (" (coverage model)" if r["role"] != "ladder" else "")
            if r["status"] != "ok":
                L.append(f"| {name} | {r['stage']} | {r['status']} |" + " |" * len(FAMILIES))
                continue
            cells = []
            for f in FAMILIES:
                c = r["families"][f]
                cells.append(f"{fb(c[kind + '_estimate'])} ({c[nk]}/{c[dk]})")
            p = r["all_plans_pooled"]
            cells.append(f"{AL.fx(p[kind])} ({p[nk]}/{p[dk]})")
            L.append(f"| {name} | {r['stage']} | " + " | ".join(cells) + " |")
        L.append("")
    L += ["## Checks", ""]
    for r in rows:
        if r["status"] == "ok":
            L.append(f"- `{r['checkpoint']}`: " + "; ".join(r["checks"]) + ".")
        else:
            L.append(f"- `{r['checkpoint']}`: {r['status']}.")
    if g["ladder_notes"]:
        L.append("- Ladder enumeration notes: " + "; ".join(g["ladder_notes"]) + ".")
    L.append("")
    Path(path).write_text("\n".join(L))


def _jsonable(o):
    if isinstance(o, hs.Estimate):
        return _jsonable(o.as_dict())
    return AL._jsonable(o)


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--ckpt-root", default=str(AL.CKPT_ROOT))
    ap.add_argument("--tasks", default=str(AL.TASKS_40))
    ap.add_argument("--out", default=None)
    ap.add_argument("--n-boot", type=int, default=hs.N_BOOT)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    root = Path(a.root)
    out = Path(a.out) if a.out else root / "results" / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    g = gather(root, Path(a.ckpt_root), Path(a.tasks), a.n_boot, a.seed)
    args = sys.argv[1:] if argv is None else list(argv)
    cmd = "PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/logged_plan_verdicts.py" + \
        ("" if not args else " " + " ".join(args))
    js = {"generated_utc": generated, "command": cmd,
          "status": "complete" if all(r["status"] == "ok" for r in g["rows"]) and g["n_ladder"] == AL.LADDER_SIZE
          else "partial",
          "definitions": {
              "emulator_accepts": f"pass share over 8 fresh emulator samples >= {A.ACCEPT_P} (behaviour_grader_p)",
              "oracle_accepts": "32-seed majority margin >= 0 (behaviour_engine_margin; dc.audit.Audit.flip_rates)",
              "false_rejection": "emulator-rejected / oracle-accepted logged plans, pooled over the family's plans",
              "false_acceptance": "emulator-accepted / oracle-rejected logged plans, pooled over the family's plans",
              "plans": "the first behaviour_plans_per_instance (100) logged behaviour plans of every instance",
              "interval": f"cluster bootstrap over city families (family_id), plans as units, {a.n_boot} resamples, "
                          f"seed {a.seed}, 95 per cent BCa (percentile where BCa is undefined), "
                          "hpr_dream.stats.conditional_mean"},
          "tasks": {k: v for k, v in g["tasks"].items() if k != "instances"},
          "ladder_notes": g["ladder_notes"], "checkpoints": g["rows"], "inputs": g["manifest"]}
    (out / "logged_plan_verdicts.json").write_text(json.dumps(_jsonable(js), indent=1))
    write_md(out / "logged_plan_verdicts.md", g, cmd, generated, a.n_boot)
    for r in g["rows"]:
        if r["status"] != "ok":
            print(f"{r['checkpoint']}: {r['status']}")
            continue
        print(f"{r['checkpoint']:32s} FR " + " ".join(f"{f[:4]} {r['families'][f]['false_rejection']:.3f}" for f in FAMILIES)
              + " | FA " + " ".join(f"{f[:4]} {r['families'][f]['false_acceptance']:.3f}" for f in FAMILIES))
    print(f"[{js['status'].upper()}] wrote {out}/logged_plan_verdicts.json, .md")
    return js


if __name__ == "__main__":
    main()
