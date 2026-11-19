#!/usr/bin/env python
"""Fidelity at the task horizon, and held-out likelihood at half and final .

One command, from the repository root:

    PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/fidelity_horizon.py

Reads the JSON files that ``code/scripts/eval_fidelity.py`` writes and renders into each ``summary.md``:
``results/fidelity/ladder/<run>/<split>/<run>_samples_<N>_dec-a.json`` (the model: one sample at T = 1, K = 8
samples per plan, decoding a) and ``floor_rollouts_s1.json`` in the same directory (the engine replaying the same
plans under one other seed: the yardstick). No markdown is parsed. The 16 training runs of the paper's fidelity
table (``paper/scripts/make_numbers.py`` ``TEST_RUNS``) and, beside them, the coverage model ``os_50m_cov``.

Item 3 (``fidelity_horizon.{json,md}``), per checkpoint and selection:

- at 24 months, all plans: each overlay's mean absolute error as a ratio to copy-last-state's (``rollouts.h24.half``
  and ``.eighth``, ``ratio_sample``: mean over plans, K samples and cells of |sample - true|, divided by the mean
  over plans and cells of |start - true|), for the model and for the engine under another seed;
- at 24 months, open-loop plans: the mean absolute error of every scalar (powered zones among them) for the model
  sample, the engine under another seed and copy-last-state, with the number of plans;
- at 12 months, all plans: the median relative error of population and of funds, |x - true| / max(|true|, 1)
  (median over plans and samples), for the model, the engine and copy, beside the protocol bar of 0.10
  (protocol (ii) and (iii)).

Rows: the final checkpoints on the test selection (the paper's table); the half checkpoints, which have fidelity
files on the development selection only (the test selection evaluates finals only), with each run's final on the
development selection beside them.

Item 4 (``heldout_likelihood.{json,md}``): the held-out likelihood, the total bound (ELBO) in nats per transition
(``onestep.loglik_nats_per_transition.elbo``, the field ``analyse_ladder.py`` reads), at every stored checkpoint of
every run on the development selection, and at the final on the test selection. For each run: final minus half on
the development selection (the only selection holding both), and whether the final is below the half (past its
held-out optimum among the stored checkpoints). The model's and the engine's files are checked to carry the same
selection key; a row whose files disagree is not computed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FID = ROOT / "results" / "fidelity" / "ladder"
OUT = ROOT / "results" / "analysis"
RUNS = ["os_15m_small", "sf_15m_small", "os_15m_full", "sf_15m_full", "os_50m_small", "sf_50m_small",
        "os_50m_full", "sf_50m_full", "os_100m_small", "sf_100m_small", "os_100m_full", "sf_100m_full",
        "os_50m_full_s1", "sf_50m_full_s1", "os_50m_full_s2", "sf_50m_full_s2"]   # make_numbers.TEST_RUNS
BESIDE = ["os_50m_cov"]
MAIN_RUN = "os_50m_full"
DECODING = "a"
FLOOR_FILE = "floor_rollouts_s1.json"
BAR = 0.10              # protocol (ii), (iii): median relative error at 12 months at most 10 per cent
OVERLAYS = (("half", "pop_density"), ("half", "traffic"), ("half", "pollution"), ("half", "land_value"),
            ("half", "crime"), ("eighth", "rate_of_growth"), ("eighth", "fire_coverage"), ("eighth", "police_coverage"))
MD_SCALARS = ("powered_zones", "unpowered_zones", "coal_plants", "pop", "funds", "road_total")
NAME_RE = re.compile(r"(?P<run>.+)_samples_(?P<n>\d{9})_dec-(?P<dec>[a-z])\.json")


def _f(x):
    return float("nan") if x is None else float(x)


def model_files(run_dir: Path, split: str) -> dict[int, Path]:
    """Sample count -> the model's evaluation JSON (decoding a, no eval seed) in ``<run>/<split>``."""
    out = {}
    d = run_dir / split
    if not d.is_dir():
        return out
    for p in d.iterdir():
        m = NAME_RE.fullmatch(p.name)
        if m and m["run"] == run_dir.name and m["dec"] == DECODING:
            out[int(m["n"])] = p
    return out


class Reader:
    def __init__(self, root: Path):
        self.root, self.manifest, self._cache = Path(root), {}, {}

    def json(self, p: Path):
        p = Path(p)
        if p in self._cache:
            return self._cache[p]
        if not p.is_file():
            return None
        data = p.read_bytes()
        try:
            key = str(p.resolve().relative_to(self.root.resolve()))
        except ValueError:
            key = str(p)
        self.manifest[key] = hashlib.sha256(data).hexdigest()
        self._cache[p] = json.loads(data)
        return self._cache[p]


def horizon_row(model: dict, floor: dict | None) -> dict:
    """Item 3's numbers from one model JSON and the engine yardstick of the same selection."""
    ro = model["rollouts"]
    fl_ok = floor is not None and floor.get("selection_key") == model.get("selection_key")
    out = {"samples": model["samples"], "selection_key": model.get("selection_key"),
           "selection_name": (model.get("selection") or {}).get("name"),
           "n_plans": ro["n_plans"], "K": ro["K"], "decoding": model["decoding"],
           "engine_yardstick": "ok" if fl_ok else ("absent" if floor is None else "selection key differs: not used")}
    h24, f24 = ro["h24"], (floor["h24"] if fl_ok else None)
    out["overlays_24m_all_plans"] = {
        name: {"model_ratio": _f(h24[tag][name]["ratio_sample"]),
               "engine_ratio": _f(f24[tag][name]["ratio_sample"]) if f24 else None,
               "model_mae": _f(h24[tag][name]["mae_sample"]), "engine_mae": _f(f24[tag][name]["mae_sample"]) if f24 else None,
               "copy_mae": _f(h24[tag][name]["mae_copy"]), "n_plans": ro["n_plans"]}
        for tag, name in OVERLAYS}
    ol = ro["by_subset"].get("open_loop")
    fol = floor["by_subset"].get("open_loop") if fl_ok else None
    if ol and "h24" in ol:
        out["open_loop_scalars_24m"] = {
            "n_plans": ol["n_plans"],
            "scalars": {n: {"model_mae": _f(v["mae_sample"]), "engine_mae": _f(fol["h24"]["scalars"][n]["mae_sample"])
                            if fol else None, "copy_mae": _f(v["mae_copy"])}
                        for n, v in ol["h24"]["scalars"].items()},
            "mean_ratio_to_copy_model": _f(ol["h24"]["mean_ratio_sample"]),
            "mean_ratio_to_copy_engine": _f(fol["h24"]["mean_ratio_sample"]) if fol else None}
        if fol and fol["n_plans"] != ol["n_plans"]:
            raise SystemExit("open-loop plan counts of the model and the engine differ")
    else:
        out["open_loop_scalars_24m"] = {"status": "no open-loop plans in this selection"}
    h12, f12 = ro["h12"], (floor["h12"] if fl_ok else None)
    gc = model.get("gap_closed", {})
    out["twelve_months_all_plans"] = {}
    for q in ("pop", "funds"):
        m, c = _f(h12[f"median_rel_{q}"]["sample"]), _f(h12[f"median_rel_{q}"]["copy"])
        e = _f(f12[f"median_rel_{q}"]["sample"]) if f12 else None
        g = gc.get(f"{q}_median_rel_12m")
        if g is not None and not (math.isclose(g["model"], m, abs_tol=1e-12) and math.isclose(g["copy"], c, abs_tol=1e-12)):
            raise SystemExit(f"{q}: gap_closed and rollouts.h12 disagree")
        out["twelve_months_all_plans"][q] = {
            "model": m, "engine": e, "copy": c, "bar": BAR, "model_within_bar": bool(m <= BAR),
            "copy_within_bar": bool(c <= BAR), "model_over_engine": m / e if e else None, "model_over_copy": m / c if c else None,
            "n_plans": ro["n_plans"]}
    out["mean_ratio_to_copy_24m_all_plans"] = {"model": _f(h24["mean_ratio_sample"]),
                                               "engine": _f(f24["mean_ratio_sample"]) if f24 else None}
    out["n_overlays_model_ratio_ge_1"] = sum(1 for v in out["overlays_24m_all_plans"].values() if v["model_ratio"] >= 1)
    return out


def elbo_of(model: dict):
    ll = (model.get("onestep") or {}).get("loglik_nats_per_transition") or {}
    return None if ll.get("elbo") is None else float(ll["elbo"])


def gather(fid_root: Path, root: Path) -> dict:
    rd = Reader(root)
    horizon, heldout, notes = [], {}, []
    for run in RUNS + BESIDE:
        rdir = fid_root / run
        role = "ladder run" if run in RUNS else "beside: the coverage model (its own selections)"
        files = {sp: model_files(rdir, sp) for sp in ("dev", "test")}
        if not files["test"]:
            notes.append(f"{run}: no test-selection model JSON")
        final = max(files["test"]) if files["test"] else (max(files["dev"]) if files["dev"] else None)
        dev_n = sorted(files["dev"])
        half = next((n for n in dev_n if 0.5 * final <= n < final), None) if final else None
        floors = {sp: rd.json(rdir / sp / FLOOR_FILE) for sp in ("dev", "test")}
        # item 3 rows
        for stage, split, n in (("final", "test", final), ("half", "dev", half), ("final", "dev", final)):
            if n is None or n not in files[split]:
                horizon.append({"run": run, "role": role, "stage": stage, "split": split,
                                "status": f"no {split}-selection model JSON at this stage"})
                continue
            m = rd.json(files[split][n])
            if m["decoding"]["name"] != DECODING or int(m["samples"]) != n:
                raise SystemExit(f"{files[split][n]}: decoding or sample count differs from its file name")
            row = {"run": run, "role": role, "stage": stage, "split": split, "status": "ok",
                   "file": str(files[split][n].relative_to(root)), **horizon_row(m, floors[split])}
            horizon.append(row)
        # item 4
        h = {"run": run, "role": role, "final_samples": final, "half_samples": half, "dev": {}, "test": {}}
        for sp in ("dev", "test"):
            for n in sorted(files[sp]):
                m = rd.json(files[sp][n])
                h[sp][str(n)] = {"elbo": elbo_of(m), "selection_key": m.get("selection_key"),
                                 "n_transitions": len(m["onestep"]["funds_items"]["pairs"])}
        d = h["dev"]
        if half is not None and str(half) in d and str(final) in d and d[str(half)]["elbo"] is not None \
                and d[str(final)]["elbo"] is not None:
            if d[str(half)]["selection_key"] != d[str(final)]["selection_key"]:
                h["half_vs_final_dev"] = {"status": "not computed: half and final were scored on different selections"}
            else:
                a, b = d[str(half)]["elbo"], d[str(final)]["elbo"]
                best = max(d, key=lambda k: d[k]["elbo"] if d[k]["elbo"] is not None else -math.inf)
                h["half_vs_final_dev"] = {"half": a, "final": b, "final_minus_half": b - a,
                                          "per_cent_of_half": 100.0 * (b - a) / abs(a),
                                          "final_below_half": bool(b < a),
                                          "best_stored_checkpoint_samples": int(best),
                                          "n_stored_checkpoints": len(d),
                                          "n_transitions": d[str(final)]["n_transitions"]}
        else:
            h["half_vs_final_dev"] = {"status": "not computed: the half or the final has no development-selection file"}
        heldout[run] = h
    # the beside rows: is the selection the ladder's apart from its key (which also hashes the nearest-neighbour fit
    # and the code fingerprint, eval_fidelity.selection_key)?
    for run in BESIDE:
        for sp in ("dev", "test"):
            a, b = rd.json(fid_root / run / sp / "selection.json"), rd.json(fid_root / MAIN_RUN / sp / "selection.json")
            if a is None or b is None:
                notes.append(f"{run} {sp}: selection.json absent; not compared with {MAIN_RUN}'s")
                continue
            same = {k: v for k, v in a.items() if k != "key"} == {k: v for k, v in b.items() if k != "key"}
            notes.append(f"{run} {sp}: selection.json {'equals' if same else 'differs from'} {MAIN_RUN}'s apart from "
                         f"the key ({a.get('key')} against {b.get('key')})")
    return {"horizon": horizon, "heldout": heldout, "notes": notes, "manifest": rd.manifest}


# ---------------------------------------------------------------------------------------------------------------
# markdown


def fx(v, d: int = 3) -> str:
    return "n/a" if v is None or (isinstance(v, float) and not math.isfinite(v)) else f"{v:.{d}f}"


def horizon_md(path: Path, g: dict, cmd: str, generated: str):
    rows = g["horizon"]
    L = ["# Fidelity at the task horizon ", "",
         f"Generated {generated} by `{cmd}` from the evaluation JSONs behind each `summary.md` "
         "(`results/fidelity/ladder/<run>/<split>/<run>_samples_<N>_dec-a.json`; the engine yardstick "
         f"`{FLOOR_FILE}` of the same directory, used only when its selection key equals the model's). Model: one "
         "sample at T = 1, mean over K = 8 samples per plan; engine: the same plans replayed under one other seed. "
         "Ratios below 1 beat copy-last-state.", ""]
    groups = (("Final checkpoints, test selection (the paper's fidelity table)", "final", "test"),
              ("Half checkpoints, development selection (the test selection evaluates finals only)", "half", "dev"),
              ("Final checkpoints, development selection (beside the half rows)", "final", "dev"))
    for title, stage, split in groups:
        sel = [r for r in rows if r["stage"] == stage and r["split"] == split]
        ok = [r for r in sel if r["status"] == "ok"]
        L += [f"## {title}", "", f"{len(ok)} of {len(sel)} checkpoints.", "",
              "### Overlays at 24 months, all plans: error ratio to copy-last-state, model / engine", "",
              "| run | samples | plans | " + " | ".join(n for _, n in OVERLAYS) + " | overlays with model ratio >= 1 |",
              "|---|---|---|" + "---|" * (len(OVERLAYS) + 1)]
        for r in sel:
            if r["status"] != "ok":
                L.append(f"| {r['run']} | {r['status']} |" + " |" * (len(OVERLAYS) + 2))
                continue
            ov = r["overlays_24m_all_plans"]
            L.append(f"| {r['run']} | {r['samples']:,} | {r['n_plans']} | " +
                     " | ".join(f"{fx(ov[n]['model_ratio'])} / {fx(ov[n]['engine_ratio'])}" for _, n in OVERLAYS) +
                     f" | {r['n_overlays_model_ratio_ge_1']} of {len(OVERLAYS)} |")
        L += ["", "### Open-loop plans at 24 months: mean absolute error, model / engine / copy (all 20 scalars in the "
              "JSON)", "",
              "| run | open-loop plans | " + " | ".join(MD_SCALARS) + " | mean ratio to copy, model / engine |",
              "|---|---|" + "---|" * (len(MD_SCALARS) + 1)]
        for r in ok:
            o = r["open_loop_scalars_24m"]
            if "scalars" not in o:
                L.append(f"| {r['run']} | {o['status']} |" + " |" * (len(MD_SCALARS) + 1))
                continue
            s = o["scalars"]
            L.append(f"| {r['run']} | {o['n_plans']} | " + " | ".join(
                f"{fx(s[n]['model_mae'], 1)} / {fx(s[n]['engine_mae'], 1)} / {fx(s[n]['copy_mae'], 1)}" for n in MD_SCALARS)
                + f" | {fx(o['mean_ratio_to_copy_model'])} / {fx(o['mean_ratio_to_copy_engine'])} |")
        L += ["", f"### 12 months, all plans: median relative error, model / engine / copy, against the bar {BAR:.2f}", "",
              "| run | plans | population | model within bar | model / engine | funds | model within bar | model / engine |",
              "|---|---|---|---|---|---|---|---|"]
        for r in ok:
            t = r["twelve_months_all_plans"]
            p, f = t["pop"], t["funds"]
            L.append(f"| {r['run']} | {r['n_plans']} | {fx(p['model'])} / {fx(p['engine'])} / {fx(p['copy'])} | "
                     f"{'yes' if p['model_within_bar'] else 'no'} | {fx(p['model_over_engine'], 1)} | "
                     f"{fx(f['model'])} / {fx(f['engine'])} / {fx(f['copy'])} | {'yes' if f['model_within_bar'] else 'no'} | "
                     f"{fx(f['model_over_engine'], 1)} |")
        L.append("")
    keys = sorted({r.get("selection_key") for r in rows if r["status"] == "ok"} - {None})
    L += ["## Notes", "",
          f"- Selection keys seen: {', '.join(keys)}. The coverage model (`os_50m_cov`) carries other keys; the "
          "comparison of its `selection.json` with the main run's is below.",
          "- Half checkpoints: the half of each run is the first stored checkpoint at or past half its final sample "
          "count; every one of the 16 runs (12 ladder rungs and the 4 seed replicas of the 50M full-data runs) has one "
          "on the development selection only."]
    L += [f"- {n}" for n in g["notes"]]
    L.append("")
    Path(path).write_text("\n".join(L))


def heldout_md(path: Path, g: dict, cmd: str, generated: str):
    H = g["heldout"]
    L = ["# Held-out likelihood at half and final ", "",
         f"Generated {generated} by `{cmd}`. Held-out likelihood: the total bound (ELBO) in nats per transition "
         "(`onestep.loglik_nats_per_transition.elbo`; higher is better) on the development selection (2,000 held-out "
         "transitions, every stored checkpoint) and the test selection (finals only). Final below half: the final's "
         "ELBO is lower than the half's on the development selection, the only selection holding both.", "",
         "| run | half (samples) | final (samples) | dev ELBO, half | dev ELBO, final | final minus half | per cent of half "
         "| final below half | best stored (dev) | test ELBO, final |", "|---|---|---|---|---|---|---|---|---|---|"]
    n_below, n_rows = 0, 0
    for run, h in H.items():
        hv = h["half_vs_final_dev"]
        te = h["test"].get(str(h["final_samples"]), {}).get("elbo") if h["final_samples"] else None
        name = run + (" (beside)" if run in BESIDE else "")
        if "final" not in hv:
            L.append(f"| {name} | {h['half_samples']} | {h['final_samples']} | {hv['status']} | | | | | | {fx(te, 1)} |")
            continue
        if run in RUNS:
            n_rows += 1
            n_below += hv["final_below_half"]
        L.append(f"| {name} | {h['half_samples']:,} | {h['final_samples']:,} | {fx(hv['half'], 1)} | {fx(hv['final'], 1)} | "
                 f"{hv['final_minus_half']:+.1f} | {hv['per_cent_of_half']:+.1f} | {'yes' if hv['final_below_half'] else 'no'} | "
                 f"{hv['best_stored_checkpoint_samples']:,} (of {hv['n_stored_checkpoints']} stored) | {fx(te, 1)} |")
    L += ["", f"Of the {n_rows} training runs with both (the 12 seed-0 runs and 4 seed replicas), {n_below} have a "
          "final below their half on the development selection.", ""]
    for run in (MAIN_RUN, "os_50m_cov"):
        h = H.get(run)
        if h and len(h["dev"]) > 2:
            L.append(f"- `{run}`, development selection, every stored checkpoint: " + "; ".join(
                f"{int(n):,}: {fx(v['elbo'], 1)}" for n, v in sorted(h["dev"].items(), key=lambda kv: int(kv[0]))) + ".")
    L.append("")
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
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--fidelity", default=None, help="default <root>/results/fidelity/ladder")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root)
    fid = Path(a.fidelity) if a.fidelity else root / "results" / "fidelity" / "ladder"
    out = Path(a.out) if a.out else root / "results" / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    args = sys.argv[1:] if argv is None else list(argv)
    cmd = "PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/fidelity_horizon.py" + ("" if not args else " " + " ".join(args))
    g = gather(fid, root)
    defs = {"overlay_ratio": "rollouts.h24.<half|eighth>.<overlay>.ratio_sample: mean over plans, K = 8 samples and "
                             "cells of |sample - true| / mean over plans and cells of |start - true|; engine: the same "
                             "with one other engine seed (K = 1)",
            "open_loop_scalar_mae": "rollouts.by_subset.open_loop.h24.scalars.<name>: mean over open-loop plans (and K "
                                    "samples) of |x - true|; copy: |start - true|",
            "median_rel_12m": "rollouts.h12.median_rel_<pop|funds>: median over plans and samples of |x - true| / "
                              "max(|true|, 1)", "bar": f"{BAR} (protocol (ii) and (iii))",
            "elbo": "onestep.loglik_nats_per_transition.elbo, nats per transition, higher is better"}
    common = {"generated_utc": generated, "command": cmd, "definitions": defs, "inputs": g["manifest"]}
    (out / "fidelity_horizon.json").write_text(json.dumps(_jsonable({**common, "rows": g["horizon"],
                                                                     "notes": g["notes"]}), indent=1))
    (out / "heldout_likelihood.json").write_text(json.dumps(_jsonable({**common, "runs": g["heldout"]}), indent=1))
    horizon_md(out / "fidelity_horizon.md", g, cmd, generated)
    heldout_md(out / "heldout_likelihood.md", g, cmd, generated)
    for r in g["horizon"]:
        if r["status"] == "ok" and r["stage"] == "final" and r["split"] == "test":
            ov = r["overlays_24m_all_plans"]
            print(f"{r['run']:16s} pollution {ov['pollution']['model_ratio']:.3f}/{ov['pollution']['engine_ratio']:.3f} "
                  f"fire {ov['fire_coverage']['model_ratio']:.3f}/{ov['fire_coverage']['engine_ratio']:.3f} "
                  f"overlays>=1 {r['n_overlays_model_ratio_ge_1']}")
    for run, h in g["heldout"].items():
        hv = h["half_vs_final_dev"]
        if "final" in hv:
            print(f"{run:16s} dev ELBO half {hv['half']:.1f} final {hv['final']:.1f} ({hv['per_cent_of_half']:+.1f}%)")
    print(f"wrote {out}/fidelity_horizon.json/.md, heldout_likelihood.json/.md")
    return g


if __name__ == "__main__":
    main()
