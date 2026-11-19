#!/usr/bin/env python
"""Defences against their own undefended model .

One command, from the repository root:

    PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/defence_baselines.py

Reads ``results/defences/frontier.json`` only (no new runs, no other file). For each search (random search and
the pool-seeded search, B = 1,000, the frontier's 60 instances) and each defence setting it reports false
acceptance (``hackability``: the defended judge accepts the selected plan and the 32-seed majority oracle rejects
it), false rejection (among selected plans the oracle accepts, the share the defended judge rejects) and real
success (``oracle_accept``: the oracle accepts the selected plan) beside the setting's own undefended model: member
0 for a setting whose judge is member 0 (temperatures, member-0 deflation), the three-member ensemble for a
setting whose judge is the ensemble (disagreement penalty, halting, detector, ensemble deflation). The baseline is
read from the row's ``judge`` field. The disagreement penalty's settings are also given as increments over its
lambda = 0 row (the verdict's added mean-margin condition with no disagreement term).

Intervals: each rate carries the interval frontier.json stores (cluster bootstrap over city families, 2,000
resamples, seed 0; printed as BCa, the percentile interval where BCa is undefined, as ``frontier.md`` does). A
difference is a point value (the difference of the two rates on the same 60 instances), except the one paired
interval frontier.json stores: false acceptance minus the undefended ensemble's (``hackability_minus_ensemble``),
which is carried for ensemble-judged settings. frontier.json holds no per-instance outcomes, so no other paired
interval can be computed from it; the output says so where it applies.

Outputs: ``results/analysis/defence_baselines.json`` and ``.md``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTIER = ROOT / "results" / "defences" / "frontier.json"
OUT = ROOT / "results" / "analysis"

# (output name, frontier.json field, description)
STATS = (("false_acceptance", "hackability", "false acceptance: the defended judge accepts the selected plan and "
                                             "the 32-seed majority oracle rejects it, over instances"),
         ("false_rejection", "false_rejection", "false rejection: among selected plans the oracle accepts, the "
                                                "share the defended judge rejects"),
         ("real_success", "oracle_accept", "real success: the oracle accepts the selected plan, over instances"),
         ("emulator_accepts", "judge_accept", "the defended judge accepts the selected plan, over instances"))
COUNTS = ("n_hacked", "n_false_rejections", "n_oracle_accept", "n_judge_accept")
BASELINES = ("member0", "ensemble")           # the undefended rows, named by the judge they use
PENALTY = "penalty"
NO_PAIRED = ("not computable from frontier.json: it stores no per-instance outcomes, only each rate's interval "
             "and, for false acceptance, the paired difference from the undefended ensemble")
SEARCH_NAMES = {"random": "random search", "cem_seeded": "pool-seeded search"}
TOL = 1e-9


def _num(x):
    return float("nan") if x is None else float(x)


def interval(e: dict) -> tuple[float, float, str]:
    """BCa where frontier.json stores it, else the percentile interval (``analyse_ladder.interval``)."""
    lo, hi = _num(e.get("bca_lo")), _num(e.get("bca_hi"))
    if math.isfinite(lo) and math.isfinite(hi):
        return lo, hi, "BCa"
    return _num(e.get("lo")), _num(e.get("hi")), "percentile"


def is_estimate(e) -> bool:
    return isinstance(e, dict) and "value" in e and "n_units" in e


def baseline_of(row: dict) -> str | None:
    j = row.get("judge")
    return j if j in BASELINES else None


def compare(row: dict, base: dict) -> dict:
    """The row's rates, its baseline's and the point differences."""
    out = {}
    for name, field, _ in STATS:
        a, b = row.get(field), base.get(field)
        va = _num(a["value"]) if is_estimate(a) else float("nan")
        vb = _num(b["value"]) if is_estimate(b) else float("nan")
        out[name] = {"defended": a, "undefended": b,
                     "difference": va - vb if math.isfinite(va) and math.isfinite(vb) else None,
                     "difference_interval": NO_PAIRED}
    return out


def build(fr: dict) -> dict:
    """Every setting of every search beside its own undefended model, and the penalty's increments over lambda 0."""
    res = {"design": {"budget": fr["design"]["budget"], "n_instances": fr["n_instances"],
                      "n_city_families": fr["n_families"], "searches": fr["design"]["searches"]},
           "searches": {}, "checks": []}
    for search, blk in fr["frontier"].items():
        rows = {r["setting"]: r for r in blk["rows"]}
        missing = [b for b in BASELINES if b not in rows or not is_estimate(rows[b].get("hackability"))]
        if missing:
            raise SystemExit(f"{search}: undefended row(s) {missing} absent from frontier.json")
        n_set = {rows[b]["n"] for b in BASELINES}
        sr = {"perfect_emulator": {k: rows["perfect"].get(f) for k, f, _ in STATS} if "perfect" in rows else None,
              "undefended": {b: {"label": rows[b]["label"], "n": rows[b]["n"], "n_clusters": rows[b]["n_clusters"],
                                 **{k: rows[b].get(f) for k, f, _ in STATS}, **{c: rows[b].get(c) for c in COUNTS}}
                             for b in BASELINES},
              "settings": [], "not_run": [], "penalty_increments": {}}
        for name, r in rows.items():
            if name == "perfect" or name in BASELINES:
                continue
            if "judge" not in r:
                sr["not_run"].append({"setting": name, "status": r.get("status", "no values")})
                continue
            b = baseline_of(r)
            if b is None:
                raise SystemExit(f"{search} {name}: judge {r.get('judge')!r} is neither member 0 nor the ensemble")
            if r["n"] not in n_set:
                raise SystemExit(f"{search} {name}: {r['n']} instances, the undefended rows {sorted(n_set)}")
            e = {"setting": name, "label": r["label"], "judge": r["judge"], "defence": r["defence"],
                 "param": r["param"], "derived_from": r.get("derived_from") or None, "neutral": bool(r.get("neutral")),
                 "n": r["n"], "n_clusters": r["n_clusters"], "baseline": b,
                 "same_plan_as_ensemble": r.get("same_plan_as_ensemble"),
                 "counts": {c: r.get(c) for c in COUNTS}, "baseline_counts": {c: rows[b].get(c) for c in COUNTS},
                 "against_own_baseline": compare(r, rows[b])}
            hm = r.get("hackability_minus_ensemble")
            if is_estimate(hm):
                # check: the stored paired difference's point equals the difference of the two stored rates
                d = _num(r["hackability"]["value"]) - _num(rows["ensemble"]["hackability"]["value"])
                ok = abs(_num(hm["value"]) - d) <= TOL
                res["checks"].append(f"{search} {name}: stored hackability_minus_ensemble {_num(hm['value']):+.6f} "
                                     f"{'equals' if ok else 'differs from'} the rates' difference {d:+.6f}")
                if not ok:
                    raise SystemExit(res["checks"][-1])
                e["false_acceptance_minus_ensemble_paired"] = hm
                if b == "ensemble":
                    e["against_own_baseline"]["false_acceptance"]["difference_interval"] = hm
            sr["settings"].append(e)
        # the disagreement penalty: increments over its lambda = 0 row
        pens = sorted((r for r in rows.values() if r.get("defence") == PENALTY), key=lambda r: float(r["param"]))
        zero = next((r for r in pens if float(r["param"]) == 0.0), None)
        if zero is None:
            sr["penalty_increments"] = {"status": "not computed: no lambda = 0 row in frontier.json"}
        else:
            inc = {"lambda0_setting": zero["setting"], "lambda0_label": zero["label"],
                   "lambda0_same_plan_as_ensemble": zero.get("same_plan_as_ensemble"),
                   "lambda0_against_ensemble": compare(zero, rows["ensemble"]), "increments": {}}
            if is_estimate(zero.get("hackability_minus_ensemble")):
                inc["lambda0_against_ensemble"]["false_acceptance"]["difference_interval"] = \
                    zero["hackability_minus_ensemble"]
            for r in pens:
                if r is zero:
                    continue
                c = compare(r, zero)
                for v in c.values():
                    v["difference_interval"] = ("not computable from frontier.json: it stores each penalty setting's "
                                                "paired difference from the undefended ensemble, not from lambda 0, "
                                                "and no per-instance outcomes")
                inc["increments"][r["setting"]] = {"lambda": float(r["param"]), "label": r["label"],
                                                   "same_plan_as_ensemble": r.get("same_plan_as_ensemble"),
                                                   "over_lambda0": c}
            sr["penalty_increments"] = inc
        res["searches"][search] = sr
    return res


# ---------------------------------------------------------------------------------------------------------------
# markdown


def fb(e, d: int = 3) -> str:
    if not is_estimate(e) or e.get("value") is None:
        return "n/a"
    lo, hi, kind = interval(e)
    v = _num(e["value"])
    if not (math.isfinite(lo) and math.isfinite(hi)):
        return f"{v:.{d}f} [n/a]"
    mark = "†" if str(e.get("method", "")).startswith("no hacked unit") else ("*" if kind == "percentile" else "")
    return f"{v:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]{mark}"


def fd(v, d: int = 3) -> str:
    return "n/a" if v is None or not math.isfinite(v) else f"{v:+.{d}f}"


def fdi(e, d: int = 3) -> str:
    if not is_estimate(e):
        return "point only"
    lo, hi, kind = interval(e)
    return f"[{lo:+.{d}f}, {hi:+.{d}f}]{'*' if kind == 'percentile' else ''}"


def write_md(path: Path, res: dict, cmd: str, generated: str, src_sha: str):
    L = ["# Defences beside their own undefended model ", "",
         f"Generated {generated} by `{cmd}` from `results/defences/frontier.json` only (sha256 {src_sha[:16]}). "
         f"B = {res['design']['budget']:,}; {res['design']['n_instances']} instances in "
         f"{res['design']['n_city_families']} city families. Each setting beside its own undefended model, read from "
         "its `judge` field: member 0 for member-0 settings, the ensemble for ensemble settings. Rates: value [95 % "
         "BCa] as stored (cluster bootstrap over city families, 2,000 resamples, seed 0; `*` percentile where BCa is "
         "undefined; `†` no hacked unit, the exact one-sided bound on clusters). Differences are point values on the "
         "same 60 instances; the only paired interval frontier.json stores is false acceptance minus the undefended "
         "ensemble's, shown for ensemble settings. Real success: the oracle accepts the selected plan.", ""]
    for search, sr in res["searches"].items():
        u = sr["undefended"]
        L += [f"## {SEARCH_NAMES.get(search, search)}", "",
              "Undefended: " + "; ".join(
                  f"{'member 0' if b == 'member0' else 'ensemble'}: false acceptance {fb(u[b]['false_acceptance'])}, "
                  f"false rejection {fb(u[b]['false_rejection'])}, real success {fb(u[b]['real_success'])}"
                  for b in BASELINES) + "."]
        if sr["perfect_emulator"]:
            p = sr["perfect_emulator"]
            L.append(f"Perfect emulator: false acceptance {fb(p['false_acceptance'])}, false rejection "
                     f"{fb(p['false_rejection'])}, real success {fb(p['real_success'])}.")
        L += ["", "| setting | own baseline | false acceptance | minus baseline | paired interval | false rejection | "
              "minus baseline | real success | minus baseline | hacked / false rejections / oracle accepts (baseline) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for e in sr["settings"]:
            c = e["against_own_baseline"]
            fa, fr_, rs = c["false_acceptance"], c["false_rejection"], c["real_success"]
            k, kb = e["counts"], e["baseline_counts"]
            L.append(f"| {e['label']} | {'member 0' if e['baseline'] == 'member0' else 'ensemble'} | "
                     f"{fb(fa['defended'])} | {fd(fa['difference'])} | {fdi(fa['difference_interval'])} | "
                     f"{fb(fr_['defended'])} | {fd(fr_['difference'])} | {fb(rs['defended'])} | {fd(rs['difference'])} | "
                     f"{k['n_hacked']} / {k['n_false_rejections']} / {k['n_oracle_accept']} "
                     f"({kb['n_hacked']} / {kb['n_false_rejections']} / {kb['n_oracle_accept']}) |")
        for nr in sr["not_run"]:
            L.append(f"| {nr['setting']} | - | {nr['status']} | | | | | | | |")
        L.append("")
        inc = sr["penalty_increments"]
        if "increments" not in inc:
            L += [f"Disagreement penalty: {inc.get('status')}.", ""]
            continue
        z = inc["lambda0_against_ensemble"]
        L += ["### Disagreement penalty as increments over lambda = 0", "",
              f"lambda = 0 ({inc['lambda0_label']}) selects the same plan as the undefended ensemble on "
              f"{inc['lambda0_same_plan_as_ensemble']} of {res['design']['n_instances']} instances; against the ensemble "
              f"it changes false acceptance by {fd(z['false_acceptance']['difference'])} "
              f"{fdi(z['false_acceptance']['difference_interval'])} (paired, stored), false rejection by "
              f"{fd(z['false_rejection']['difference'])} and real success by {fd(z['real_success']['difference'])} "
              "(points).", "",
              "| lambda | same plan as ensemble | false acceptance | minus lambda 0 | false rejection | minus lambda 0 | "
              "real success | minus lambda 0 |", "|---|---|---|---|---|---|---|---|"]
        for s, v in inc["increments"].items():
            c = v["over_lambda0"]
            L.append(f"| {v['lambda']:g} | {v['same_plan_as_ensemble']} | {fb(c['false_acceptance']['defended'])} | "
                     f"{fd(c['false_acceptance']['difference'])} | {fb(c['false_rejection']['defended'])} | "
                     f"{fd(c['false_rejection']['difference'])} | {fb(c['real_success']['defended'])} | "
                     f"{fd(c['real_success']['difference'])} |")
        L += ["", "Increments are point values: frontier.json stores each penalty setting's paired difference from "
              "the undefended ensemble, not from lambda 0, and no per-instance outcomes.", ""]
    L += ["## Checks", ""] + [f"- {c}." for c in res["checks"]] + [""]
    Path(path).write_text("\n".join(L))


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    return o


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--frontier", default=str(FRONTIER))
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    src = Path(a.frontier)
    data = src.read_bytes()
    fr = json.loads(data)
    res = build(fr)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cmd = "PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/defence_baselines.py" + \
        ("" if not (sys.argv[1:] if argv is None else argv) else " " + " ".join(sys.argv[1:] if argv is None else argv))
    sha = hashlib.sha256(data).hexdigest()
    js = {"generated_utc": generated, "command": cmd,
          "inputs": {str(src.relative_to(ROOT)) if src.is_relative_to(ROOT) else str(src): sha},
          "definitions": {n: d for n, _, d in STATS} | {
              "baseline": "the setting's own undefended model, from its judge field: member 0 or the ensemble",
              "difference": "defended rate minus the baseline's rate on the same instances (point value)",
              "intervals": "as stored in frontier.json: cluster bootstrap over city families, 2,000 resamples, seed "
                           "0, 95 per cent; BCa with the percentile interval where BCa is undefined",
              "penalty_increments": "a penalty setting's rate minus the lambda = 0 row's (point value)"},
          **res}
    (out / "defence_baselines.json").write_text(json.dumps(_jsonable(js), indent=1))
    write_md(out / "defence_baselines.md", res, cmd, generated, sha)
    for search, sr in res["searches"].items():
        for e in sr["settings"]:
            c = e["against_own_baseline"]
            print(f"{search:10s} {e['setting']:20s} vs {e['baseline']:8s}: FA {fd(c['false_acceptance']['difference'])} "
                  f"FR {fd(c['false_rejection']['difference'])} RS {fd(c['real_success']['difference'])}")
    print(f"wrote {out}/defence_baselines.json, .md")
    return js


if __name__ == "__main__":
    main()
