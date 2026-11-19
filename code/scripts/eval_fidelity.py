#!/usr/bin/env python
"""Fidelity of emulator checkpoints on held-out trajectories, beside copy-last-state, the
nearest-neighbour baseline and the engine's own seed-against-seed floor.

Examples
  eval_fidelity.py --ckpt <run>/samples_000150016.pt <run>/samples_000300032.pt \
      --heldout heldout_eval --train-index train_full --floor --out-dir results/fidelity/pilot_50m
  eval_fidelity.py --curves <cache>/ckpt/pilot_50m --out-dir results/fidelity/pilot_50m
  eval_fidelity.py --synthetic --ckpt <ckpt> --floor --out-dir <dir>      # development stand-in

Selections (--selection, ``dc.fidelity.selection``): dev (seed 20261109: --n-onestep transitions
drawn uniformly without replacement from all held-out transitions, --n-plans trajectories of at least
--H months, whose first H months are the plans; the ladder is monitored on it), test (a fresh seed on
the held-out plans and transitions the development selection does not contain: the paper's tables)
and train_eval (the unused split). Several comma-separated selections go to subdirectories of
--out-dir. The engine yardstick and the baselines are cached per selection, keyed also on the code
that computes them and on the nearest-neighbour fit.

Headline rows are one model sample (T=1, decoding a) against the stored run, beside copy-last-state
and the engine under another seed (a sample-against-sample yardstick, not a bound); mean-of-K and
mode (T=0) rows are in the appendix. Every rollout table is split by plan source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc import fidelity as fd  # noqa: E402
from dc.train import EnginePool, load_checkpoint, sha256_file  # noqa: E402

CITIES = sorted((ROOT / "data" / "cities").glob("*.cty"))


def heldout_trajectories(args, split: str):
    if args.synthetic:
        # development stand-in: half of the bundled cities, random months, disasters off
        return fd.trajectories_from_engine(CITIES[1::2], per_city=args.synthetic_per_city, months=args.H, seed=12345)
    from dc import data
    store, _ = data.open_split(split, args.data_root or None)
    return fd.trajectories_from_store(store, store.traj_ids().tolist())


def nn_baseline(args, device, out_dir: Path):
    # the count table is 270 MB: it lives in the cache, not in results/
    cache = Path(args.cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    import inspect
    code = hashlib.sha256(inspect.getsource(fd.TileNN).encode()).hexdigest()[:10]
    path = cache / f"tilenn_{args.train_index}_{args.nn_fit}_{code}{'_synthetic' if args.synthetic else ''}.pt"
    if path.exists():
        return fd.TileNN.from_state_dict(torch.load(path, weights_only=False), device)
    if args.synthetic:
        pool = EnginePool.generate(CITIES[0::2], trajs_per_city=4, months=48, seed=99, device=device)
        it = pool.batches(256, seed=5)
    else:
        from dc import data
        store, idx = data.open_split(args.train_index, args.data_root or None)
        it = iter(data.OneStepBatches(store, idx, 256, 4242, device, num_workers=args.workers))
    nn = fd.TileNN(device).fit(it, args.nn_fit)
    torch.save(nn.state_dict(), path)
    return nn


def code_fingerprint() -> str:
    """sha256 over the code that computes the cached baselines and engine yardstick: dc.fidelity,
    dc.oracle, dc.engine, dc.grammar and the engine library."""
    h = hashlib.sha256()
    for f in (ROOT / "code/dc/fidelity.py", ROOT / "code/dc/oracle.py", ROOT / "code/dc/engine.py",
              ROOT / "code/dc/grammar.py", ROOT / "engine/libmicropolis.so"):
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def selection_key(trajs, pairs, plans, args) -> str:
    """Keys the cached baselines and yardstick: the trajectories, the selected pairs and plans, the
    horizon, the nearest-neighbour fit (training split and size) and the code fingerprint."""
    h = hashlib.sha256()
    for tr in trajs:
        h.update(f"{tr.traj_id}:{tr.seed}:{tr.H}:{tr.start_path}".encode())
    h.update(json.dumps([list(map(int, p)) for p in pairs]).encode())
    h.update(json.dumps(list(map(int, plans))).encode())
    h.update(f"H={args.H}:nn={args.train_index}:{args.nn_fit}:floor_seeds={args.floor_seeds}:code={code_fingerprint()}".encode())
    return h.hexdigest()[:16]


def cached(path: Path, key: str, fn):
    if path.exists():
        d = json.loads(path.read_text())
        if d.get("selection_key") == key:
            return d
        print(f"{path.name}: cached for another selection or code version, recomputing", flush=True)
    t = time.time()
    d = fn()
    d["selection_key"] = key
    d["seconds"] = round(time.time() - t, 1)
    fd.to_json(d, path)
    return d


def fmt(x, nd=3):
    return "n/a" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}f}"


def gap_closed(res, base, floor_1, floor_r) -> Dict[str, Dict[str, float]]:
    """Share of the gap between copy-last-state and the engine yardstick that one model sample (T=1)
    closes: (model - copy) / (engine - copy) for F1, (copy - model) / (copy - engine) for errors. Errors
    are mean absolute errors of one model sample against the stored run, beside one engine run under
    another seed against the stored run (sample against sample). Only sampled rows enter this table."""
    out: Dict[str, Dict[str, float]] = {}

    def put(name, m, c, f, higher_better):
        d = (m - c) / (f - c) if higher_better else (c - m) / (c - f)
        out[name] = {"model": m, "copy": c, "floor": f, "share_closed": d if np.isfinite(d) else float("nan")}

    if floor_1:
        for kind in ("structural", "raw"):
            put(f"tile_F1_1m_{kind}_T1", res["onestep"]["model_T1"][kind]["f1"], base["copy"][kind]["f1"],
                floor_1["tile"][kind]["f1"], True)
    if floor_r:
        for h in (12, 24):
            k = f"h{h}"
            if k not in res["rollouts"]:
                continue
            for sc in ("pop", "funds", "res_valve", "com_valve", "ind_valve"):
                m = res["rollouts"][k]["scalars"][sc]
                put(f"{sc}_mae_{h}m", m["mae_sample"], m["mae_copy"], floor_r[k]["scalars"][sc]["mae_sample"], False)
            for sc in ("pop", "funds"):
                m = res["rollouts"][k][f"median_rel_{sc}"]
                put(f"{sc}_median_rel_{h}m", m["sample"], m["copy"], floor_r[k][f"median_rel_{sc}"]["sample"], False)
            for kind in ("structural", "raw"):
                put(f"tile_F1_since_start_{h}m_{kind}", res["rollouts"][k]["tile_since_start"][kind]["f1"], 0.0,
                    floor_r[k]["tile_since_start"][kind]["f1"], True)
    return out


YARD = "engine, other seed (yardstick)"
YARD_NOTE = ("The engine row replays the same month or plan under another seed: a sample-against-sample yardstick "
             "for one model sample against the stored run, not a bound. Mean-of-K and mode rows (appendix) are not "
             "comparable with it.")
SUBSET_NAMES = {"all": "all plans", "state_reading": "state-reading plans", "open_loop": "open-loop plans",
                "untouched": "plans with no development transition in months 0..H-1"}


def _sub(rep, name):
    return rep if name == "all" else rep.get("by_subset", {}).get(name)


def summary_md(name, res, base, floor_1, floor_r, sel_desc) -> str:
    on, ro = res["onestep"], res["rollouts"]
    dec = res.get("decoding", {})
    L = [f"## {name}", "", f"samples consumed: {res.get('samples')}; weights loaded: {res.get('weights')}; "
         f"decoding {dec.get('name')} (T={dec.get('temperature')}, overlays {dec.get('overlay')})", "",
         f"selection: {json.dumps(sel_desc)}", ""]
    if dec.get("name") != fd.DEFAULT_DECODING:
        L += [f"**Appendix decoding ({dec.get('name')}): not a headline result.**", ""]
    L += ["### Headline: one model sample (T=1) against the stored run", "", YARD_NOTE, "",
          "#### One month, changed tiles (pooled over tiles; 95% interval by family bootstrap)", "",
          "| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |",
          "|---|---|---|---|---|---|---|---|---|---|"]

    def tile_row(sub, n, r):
        if not r:
            return
        cells = []
        for kind in ("raw", "structural"):
            q = r[kind]
            ci = q.get("f1_ci95_by_family", [None, None])
            cells.append(f"{fmt(q['precision'])} | {fmt(q['recall'])} | {fmt(q['f1'])} | {fmt(ci[0])} to {fmt(ci[1])}")
        L.append(f"| {sub} | {n} | " + " | ".join(cells) + " |")

    for sname in ("all", "state_reading", "open_loop"):
        o = on if sname == "all" else on.get("by_subset", {}).get(sname)
        b = base if sname == "all" else base.get("by_subset", {}).get(sname, {})
        f = floor_1 if sname == "all" else (floor_1 or {}).get("by_subset", {}).get(sname)
        if not o:
            continue
        lab = f"{sname.replace('_', '-')} ({o.get('n_transitions', len(on['funds_items']['pairs']))})" if sname != "all" else f"all ({len(on['funds_items']['pairs'])})"
        tile_row(lab, "model T=1 (one sample)", o["model_T1"])
        tile_row(lab, "copy-last-state", b.get("copy"))
        tile_row(lab, "nearest neighbour (sampled)", b.get("nn_sample"))
        tile_row(lab, YARD, f.get("tile") if f else None)
    L += ["", "#### Open-loop rollouts by plan source: error relative to copy-last-state (mean over scalars; <1 beats copy)", "",
          "| plans | n | horizon | model sample | engine yardstick | funds med. rel. model / engine / copy | "
          "pop med. rel. model / engine / copy | changed-since-start structural F1 model / engine |",
          "|---|---|---|---|---|---|---|---|"]
    for sname in ("all", "state_reading", "open_loop", "untouched"):
        m_all, f_all = _sub(ro, sname), (_sub(floor_r, sname) if floor_r else None)
        if not m_all or not m_all.get("n_plans"):
            continue
        for h in fd.HORIZONS:
            k = f"h{h}"
            if k not in m_all:
                continue
            m, f = m_all[k], (f_all.get(k) if f_all else None)
            L.append(f"| {SUBSET_NAMES[sname]} | {m_all['n_plans']} | {h} | {fmt(m['mean_ratio_sample'])} | "
                     f"{fmt(f['mean_ratio_sample']) if f else 'n/a'} | "
                     f"{fmt(m['median_rel_funds']['sample'])} / {fmt(f['median_rel_funds']['sample']) if f else 'n/a'} / {fmt(m['median_rel_funds']['copy'])} | "
                     f"{fmt(m['median_rel_pop']['sample'])} / {fmt(f['median_rel_pop']['sample']) if f else 'n/a'} / {fmt(m['median_rel_pop']['copy'])} | "
                     f"{fmt(m['tile_since_start']['structural']['f1'])} / {fmt(f['tile_since_start']['structural']['f1']) if f else 'n/a'} |")
    L += ["", "(means over the 18 scalars other than tax and city_time, which are bookkeeping identities; copy-last-state "
          "has changed-since-start F1 0)"]
    gc = res.get("gap_closed", {})
    if gc:
        L += ["", "#### Share of the copy-to-yardstick gap closed by one model sample (all plans and transitions)", "",
              "| metric | copy | engine yardstick | model T=1 | share closed |", "|---|---|---|---|---|"]
        for n, v in gc.items():
            L.append(f"| {n} | {fmt(v['copy'], 4)} | {fmt(v['floor'], 4)} | {fmt(v['model'], 4)} | {fmt(v['share_closed'])} |")
    for sname in ("all", "state_reading", "open_loop"):
        m_all, f_all = _sub(ro, sname), (_sub(floor_r, sname) if floor_r else None)
        if not m_all or "h24" not in m_all:
            continue
        L += ["", f"#### Per scalar at 24 months, {SUBSET_NAMES[sname]} ({m_all['n_plans']}): mean absolute error", "",
              "| scalar | model sample | engine yardstick | copy |", "|---|---|---|---|"]
        for n, v in m_all["h24"]["scalars"].items():
            fv = f_all["h24"]["scalars"][n]["mae_sample"] if f_all else None
            L.append(f"| {n} | {fmt(v['mae_sample'], 1)} | {fmt(fv, 1)} | {fmt(v['mae_copy'], 1)} |")
    if "h24" in ro:
        L += ["", "#### Overlays at 24 months, all plans: error ratio to copy-last-state", "",
              "| overlay | model sample | engine yardstick |", "|---|---|---|"]
        for tag in ("half", "eighth"):
            for n, v in ro["h24"].get(tag, {}).items():
                fv = floor_r["h24"][tag][n]["ratio_sample"] if floor_r else None
                L.append(f"| {n} | {fmt(v['ratio_sample'])} | {fmt(fv)} |")
    # appendix
    L += ["", "### Appendix: the mode (T=0) and the mean of K samples (not comparable with the engine yardstick)", "",
          "| transitions | predictor | raw P | raw R | raw F1 | raw F1 95% | structural P | structural R | structural F1 | structural F1 95% |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    tile_row(f"all ({len(on['funds_items']['pairs'])})", "model T=0 (mode)", on["model_T0"])
    tile_row(f"all ({len(on['funds_items']['pairs'])})", "nearest neighbour (mode)", base.get("nn_mode"))
    L += ["", "| plans | horizon | model mean of K: mean ratio | funds med. rel. | pop med. rel. |", "|---|---|---|---|---|"]
    for sname in ("all", "state_reading", "open_loop"):
        m_all = _sub(ro, sname)
        if not m_all or not m_all.get("n_plans"):
            continue
        for h in fd.HORIZONS:
            m = m_all.get(f"h{h}")
            if m:
                L.append(f"| {SUBSET_NAMES[sname]} | {h} | {fmt(m['mean_ratio_mean'])} | {fmt(m['median_rel_funds']['mean'])} | "
                         f"{fmt(m['median_rel_pop']['mean'])} |")
    L += ["", "### Held-out log-likelihood (nats per transition)", "", "| term | value |", "|---|---|"]
    for k, v in on["loglik_nats_per_transition"].items():
        if k in ("n_changed", "derived_viol"):
            continue
        L.append(f"| {k} | {fmt(v, 2)} |")
    return "\n".join(L) + "\n"


def bound_shares_md(name, res) -> str:
    """Share of values at each bound: model samples against the engine's own months."""
    one, ro = res["onestep"].get("bound_shares"), res["rollouts"].get("bound_shares")
    L = [f"# Shares at the engine's bounds: {name}", "",
         "Share of values exactly at the lower / upper bound (dc.model.BOUND_SOURCES; censored likelihood). "
         "One month: model sample T=1 against the engine's next month on the held-out transitions. Rollouts: "
         "model samples (K per plan) against the engine's stored months, pooled over months 1..H of the plans. "
         "'beyond' counts values outside the bounds (model / engine).", "",
         "| entry | bounds | one month: model at lower | engine at lower | model at upper | engine at upper | "
         "rollouts: model at lower | engine at lower | model at upper | engine at upper | beyond (model / engine) |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    pct = lambda x: "n/a" if x is None else f"{100 * x:.2f}%"
    for n, r in (ro or one or {}).items():
        o = (one or {}).get(n, {})
        q = (ro or {}).get(n, {})
        om, oe = o.get("model_T1", {}), o.get("engine", {})
        rm, re_ = q.get("model", {}), q.get("engine", {})
        lo, hi = r["lower"], r["upper"]
        bnd = f"[{'-inf' if lo is None else int(lo)}, {'inf' if hi is None else int(hi)}]"
        L.append(f"| {n} | {bnd} | {pct(om.get('share_at_lower'))} | {pct(oe.get('share_at_lower'))} | "
                 f"{pct(om.get('share_at_upper'))} | {pct(oe.get('share_at_upper'))} | {pct(rm.get('share_at_lower'))} | "
                 f"{pct(re_.get('share_at_lower'))} | {pct(rm.get('share_at_upper'))} | {pct(re_.get('share_at_upper'))} | "
                 f"{(om.get('beyond_bounds') or 0) + (rm.get('beyond_bounds') or 0)} / {(oe.get('beyond_bounds') or 0) + (re_.get('beyond_bounds') or 0)} |")
    return "\n".join(L) + "\n"


def plot_curves(run_dir: Path, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker
    recs = [json.loads(l) for l in (run_dir / "log.jsonl").read_text().splitlines() if l.strip()]
    recs = [r for r in recs if "nll_tile_gate" in r]
    if not recs:
        return
    s = np.array([r["samples"] for r in recs])
    want = ["nll_tile_gate", "nll_tile_cat", "nll_flags", "nll_power", "nll_half", "nll_eighth", "nll_scalars",
            "nll_scalars_s2", "nll_ledger", "nll_build_cost", "nll_bk", "kl"]
    keys = [k for k in want if all(k in r for r in recs)][:11]
    fig, axes = plt.subplots(3, 4, figsize=(17, 10))
    for ax, k in zip(axes.flat, keys + ["loss"]):
        ax.plot(s, [r[k] for r in recs], lw=0.8)
        ax.set_title(k + (" (nats / transition)" if k != "loss" else " (weighted, nats / tile)"), fontsize=9)
        ax.set_xlabel("samples (thousands)")
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:g}"))
        ax.grid(alpha=0.3)
    fig.suptitle(f"training curves: {run_dir.name}")
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / "training_curves.png", dpi=110)
    print("wrote", out_dir / "training_curves.png")


def funds_split_md(name, split) -> str:
    L = [f"# Funds error split: {name}", "",
         "Median relative error |x - true| / max(|true|, 1) (mean absolute error in brackets); n = items.", "",
         "## One month (held-out one-step transitions), by behaviour type and budget month", "",
         "| group | n | model T=1 | model T=0 | copy | engine floor |", "|---|---|---|---|---|---|"]
    for g, v in split["one_month"].items():
        if v["copy"] is None:
            continue
        cell = lambda k: (f"{v[k]['median_rel']:.4f} ({v[k]['mae']:.0f})" if v.get(k) else "n/a")
        L.append(f"| {g} | {v['copy']['n']} | {cell('model_T1')} | {cell('model_T0')} | {cell('copy')} | {cell('engine_floor')} |")
    L += ["", "## Twelve months (open-loop from the plans' start states; every window holds one budget month)", "",
          "| behaviour | n plans | model sample | copy | engine floor |", "|---|---|---|---|---|"]
    for g, v in split["twelve_months"].items():
        cell = lambda q: (f"{q['median_rel']:.4f} ({q['mae']:.0f})" if q else "n/a")
        L.append(f"| {g} | {v['model_sample']['n']} | {cell(v['model_sample'])} | {cell(v['copy'])} | {cell(v['engine_floor'])} |")
    return "\n".join(L) + "\n"


def one_month_md(name, res, floor_1, floor_r) -> str:
    """Per-entry one-month table for the valves, the score and every learned ledger entry: from the
    plans' start states (rollout month 1: model sample, model mean of K, engine other seed, copy) and on
    random held-out transitions (model sample T=1, mode T=0, copy, engine re-seeded at month t)."""
    from dc.model import LEARNED_LEDGER
    from dc.engine import LEDGER_NAMES
    h1 = dict(res["rollouts"]["h1"], n_plans=res["rollouts"]["n_plans"])
    fr = floor_r["h1"] if floor_r else None
    on = res["onestep"]
    L = [f"# One-month errors per entry: {name}", "",
         f"Mean absolute error. Start states: the first month of the {h1.get('n_plans', res['rollouts']['n_plans'])} "
         f"plans (K = {res['rollouts']['K']} model samples; 'mean of K' is an appendix row, not comparable with the "
         "engine yardstick). Random transitions: the "
         f"{len(on['funds_items']['pairs'])} one-step transitions (engine yardstick re-seeded at month t).", "",
         "| entry | start: model sample | start: mean of K | start: engine floor | start: copy | ratio sample/copy | "
         "random: T=1 | random: T=0 | random: engine floor | random: copy |", "|---|---|---|---|---|---|---|---|---|---|"]
    rows = [("scalar", n) for n in ("res_valve", "com_valve", "ind_valve", "score")]
    rows += [("ledger", LEDGER_NAMES[i]) for i in LEARNED_LEDGER]
    for kind, n in rows:
        if kind == "scalar":
            m, f = h1["scalars"][n], (fr["scalars"][n] if fr else None)
            o, fo = on["scalar_mae_1m"][n], (floor_1["scalar_mae_1m"][n] if floor_1 else None)
        else:
            if "ledger" not in h1:
                continue
            m, f = h1["ledger"][n], (fr["ledger"][n] if fr and "ledger" in fr else None)
            o = on.get("ledger_mae_1m", {}).get(n)
            fo = floor_1.get("ledger_mae_1m", {}).get(n) if floor_1 else None
        L.append(f"| {n} | {fmt(m['mae_sample'], 2)} | {fmt(m['mae_mean'], 2)} | {fmt(f['mae_sample'], 2) if f else 'n/a'} | "
                 f"{fmt(m['mae_copy'], 2)} | {fmt(m['ratio_sample'])} | {fmt(o['T1'], 2) if o else 'n/a'} | "
                 f"{fmt(o['T0'], 2) if o else 'n/a'} | {fmt(fo, 2) if fo is not None else 'n/a'} | {fmt(o['copy'], 2) if o else 'n/a'} |")
    return "\n".join(L) + "\n"


def compare_md(paths, labels) -> str:
    """Gap-closed table across evaluation JSONs, plus the 12-month median relative errors."""
    R = [json.loads(Path(p).read_text()) for p in paths]
    L = ["| metric | copy | engine floor | " + " | ".join(f"{lab}: model | share" for lab in labels) + " |",
         "|---|---|---|" + "---|---|" * len(R)]
    for k in R[0]["gap_closed"]:
        g = [r["gap_closed"].get(k) for r in R]
        L.append(f"| {k} | {fmt(g[0]['copy'], 4)} | {fmt(g[0]['floor'], 4)} | " +
                 " | ".join(f"{fmt(x['model'], 4)} | {fmt(x['share_closed'])}" if x else "n/a | n/a" for x in g) + " |")
    L += ["", "Median relative error at 12 months (sampled model; the line is 0.10):", "",
          "| run | population | funds |", "|---|---|---|"]
    for lab, r in zip(labels, R):
        h = r["rollouts"]["h12"]
        L.append(f"| {lab} | {fmt(h['median_rel_pop']['sample'])} | {fmt(h['median_rel_funds']['sample'])} |")
    L += ["", "Funds at 1, 12 and 24 months: mean absolute error (sample) / median relative error (sample):", "",
          "| run | 1 month | 12 months | 24 months |", "|---|---|---|---|"]
    for lab, r in zip(labels, R):
        cells = [f"{fmt(r['rollouts'][f'h{h}']['scalars']['funds']['mae_sample'], 1)} / "
                 f"{fmt(r['rollouts'][f'h{h}']['median_rel_funds']['sample'], 4)}" for h in fd.HORIZONS]
        L.append(f"| {lab} | " + " | ".join(cells) + " |")
    return "\n".join(L) + "\n"


def last_tenth_slopes(run_dir: Path) -> dict:
    """Least-squares slope of every logged loss term over the last tenth of the samples, in nats per
    transition per 100,000 samples, and relative to the term's mean over that window."""
    recs = [json.loads(l) for l in (run_dir / "log.jsonl").read_text().splitlines() if l.strip()]
    recs = [r for r in recs if "nll_tile_gate" in r]
    s = np.array([r["samples"] for r in recs], dtype=np.float64)
    lo = s.max() - 0.1 * (s.max() - 0.0)
    sel = s >= lo
    out = {"window_samples": [float(s[sel].min()), float(s[sel].max())], "points": int(sel.sum()), "terms": {}}
    for k in [k for k in recs[0] if k.startswith("nll_") or k in ("kl", "loss")]:
        y = np.array([r[k] for r in recs], dtype=np.float64)[sel]
        b = np.polyfit(s[sel] / 1e5, y, 1)[0]
        out["terms"][k] = {"slope_per_100k": float(b), "window_mean": float(y.mean()),
                           "relative_per_100k": float(b / abs(y.mean())) if y.mean() != 0 else float("nan")}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ckpt", nargs="*", default=[])
    ap.add_argument("--data-root", default="", help="root of the stores (default dc.data.DATA_ROOT)")
    ap.add_argument("--selection", default="dev", help="comma-separated subset of dev, test, train_eval (dc.fidelity.selection)")
    ap.add_argument("--heldout", default="", help="override the split (default: heldout_eval; train_eval for that selection)")
    ap.add_argument("--train-index", default="train_full", help="training split for the nearest-neighbour fit")
    ap.add_argument("--workers", type=int, default=2, help="loader workers for the nearest-neighbour fit")
    ap.add_argument("--batch-plans", type=int, default=64, help="plans per rollout batch (x K samples); 16 on a 24 GB card")
    ap.add_argument("--n-onestep", type=int, default=fd.DEV_N_ONESTEP)
    ap.add_argument("--n-plans", type=int, default=0, help="0: 500 (dev, train_eval) or every eligible plan (test)")
    ap.add_argument("--H", type=int, default=fd.DEV_H)
    ap.add_argument("--K", type=int, default=8)
    ap.add_argument("--floor-seeds", type=int, default=1)
    ap.add_argument("--nn-fit", type=int, default=20000)
    ap.add_argument("--select-seed", type=int, default=None, help="override the selection's seed (default: its own)")
    ap.add_argument("--eval-seed", type=int, default=0, help="noise seed of the model's samples (an evaluation-noise check)")
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--no-ema", action="store_true")
    ap.add_argument("--k-iw", type=int, default=1)
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--synthetic-per-city", type=int, default=2)
    ap.add_argument("--curves", default="")
    ap.add_argument("--compare", nargs="*", default=[], help="evaluation JSONs to tabulate side by side")
    ap.add_argument("--labels", default="", help="comma-separated labels for --compare")
    ap.add_argument("--slopes", nargs="*", default=[], help="run directories: last-tenth slope of each loss term")
    ap.add_argument("--decode", default=fd.DEFAULT_DECODING,
                    help="rollout decodings, comma-separated subset of a,b,c (dc.fidelity.DECODINGS); a is the model, b and c are appendix comparisons")
    ap.add_argument("--cache-dir", default="<cache>/ckpt/eval_cache")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out_root = Path(args.out_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    if args.compare:
        labels = args.labels.split(",") if args.labels else [Path(p).stem for p in args.compare]
        (out_root / "comparison.md").write_text(compare_md(args.compare, labels))
        print("wrote", out_root / "comparison.md")
        return
    if args.slopes:
        res = {Path(d).name: last_tenth_slopes(Path(d)) for d in args.slopes}
        fd.to_json(res, out_root / "last_tenth_slopes.json")
        for run, r in res.items():
            print(run, "window", r["window_samples"], "points", r["points"])
            for k, v in r["terms"].items():
                print(f"  {k:16s} slope {v['slope_per_100k']:+10.3f} per 100k  mean {v['window_mean']:10.3f}  relative {100 * v['relative_per_100k']:+6.2f}% per 100k")
        return
    if args.curves:
        plot_curves(Path(args.curves), out_root)
        if not args.ckpt and not args.floor:
            return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        from dc.model import set_numerics
        set_numerics()
    sels = [x for x in args.selection.split(",") if x]
    decodes = [d for d in args.decode.split(",") if d]
    for sel in sels:
        out_dir = out_root / sel if len(sels) > 1 else out_root
        out_dir.mkdir(parents=True, exist_ok=True)
        t = time.time()
        split = args.heldout or ("train_eval" if sel == "train_eval" else "heldout_eval")
        trajs = heldout_trajectories(args, split)
        n_plans = args.n_plans or (10**9 if sel == "test" else fd.DEV_N_PLANS)
        pairs, plans, sel_desc = fd.selection(trajs, sel, args.n_onestep, n_plans, args.H, args.select_seed)
        extra = None
        if sel == "test":
            dev_pairs = fd.pick_transitions(trajs, fd.DEV_N_ONESTEP, fd.DEV_SEED)
            touched = {i for i, t_ in dev_pairs if t_ < args.H}
            extra = {"untouched": [i not in touched for i in plans]}
            sel_desc["plans_with_no_development_transition_in_window"] = int(sum(extra["untouched"]))
        key = selection_key(trajs, pairs, plans, args)
        sel_desc.update(key=key, split=split if not args.synthetic else "synthetic")
        fd.to_json(sel_desc, out_dir / "selection.json")
        print(f"{sel}: {len(trajs)} trajectories, {len(pairs)} transitions, {len(plans)} plans of {args.H} months "
              f"(loaded in {time.time() - t:.1f}s), key {key}, {json.dumps(sel_desc)}", flush=True)
        base = cached(out_dir / "baselines.json", key,
                      lambda: fd.eval_baselines_onestep(trajs, pairs, nn_baseline(args, device, out_dir), device))
        print("baselines F1 raw / structural", json.dumps({k: [round(v["raw"]["f1"], 4), round(v["structural"]["f1"], 4)]
                                                           for k, v in base.items() if isinstance(v, dict) and "raw" in v}), flush=True)
        floor_1 = floor_r = None
        if args.floor:
            floor_1 = cached(out_dir / "floor_onestep.json", key, lambda: fd.engine_floor_onestep(trajs, pairs))
            floor_r = cached(out_dir / f"floor_rollouts_s{args.floor_seeds}.json", key,
                             lambda: fd.engine_floor_rollouts(trajs, plans, H=args.H, n_seeds=args.floor_seeds,
                                                              extra_subsets=extra))
            print("yardstick one-month F1 raw", fmt(floor_1["tile"]["raw"]["f1"]), "structural",
                  fmt(floor_1["tile"]["structural"]["f1"]), "prefix mismatches", floor_1["prefix_mismatches"], flush=True)
        md = []
        for ck_path in args.ckpt:
            model, ck = load_checkpoint(ck_path, device, use_ema=not args.no_ema)
            t = time.time()
            onestep = fd.eval_model_onestep(model, trajs, pairs, device, k_iw=args.k_iw, seed=args.eval_seed)
            t_one = time.time() - t
            for dec in decodes:
                t = time.time()
                T, ov = fd.DECODINGS[dec]
                res = {"checkpoint": str(ck_path), "checkpoint_sha256": sha256_file(ck_path), "samples": ck["samples"],
                       "weights": ck["loaded_weights"], "selection": sel_desc, "selection_key": key, "eval_seed": args.eval_seed,
                       "decoding": {"name": dec, "temperature": T, "overlay": ov},
                       "onestep": onestep,
                       "rollouts": fd.eval_model_rollouts(model, trajs, plans, device, H=args.H, K=args.K,
                                                          temperature=T, overlay=ov, batch_plans=args.batch_plans,
                                                          extra_subsets=extra, seed=args.eval_seed)}
                res["seconds"] = round(time.time() - t + t_one, 1)
                res["gap_closed"] = gap_closed(res, base, floor_1, floor_r)
                name = Path(ck_path).parent.name + "_" + Path(ck_path).stem + f"_dec-{dec}" + (
                    f"_seed{args.eval_seed}" if args.eval_seed else "")
                split = fd.funds_split(trajs, pairs, plans, res["onestep"], res["rollouts"], floor_1, floor_r)
                fd.to_json(split, out_dir / f"funds_split_{name}.json")
                (out_dir / f"funds_split_{name}.md").write_text(funds_split_md(name, split))
                (out_dir / f"one_month_{name}.md").write_text(one_month_md(name, res, floor_1, floor_r))
                (out_dir / f"bound_shares_{name}.md").write_text(bound_shares_md(name, res))
                fd.to_json(res, out_dir / f"{name}.json")
                md.append(summary_md(name, res, base, floor_1, floor_r, sel_desc))
                h24 = res["rollouts"].get("h24", {})
                print(f"{name} [{sel}]: decoding {dec} h24 mean ratio scalars {fmt(h24.get('mean_ratio_sample'))} overlays "
                      f"{fmt(h24.get('mean_ratio_overlays'))} both {fmt(h24.get('mean_ratio_scalars_and_overlays'))}", flush=True)
                print(f"{name} [{sel}]: F1 raw T1 {fmt(res['onestep']['model_T1']['raw']['f1'])}, structural T1 "
                      f"{fmt(res['onestep']['model_T1']['structural']['f1'])}, rollout ratio h24 "
                      f"{fmt(res['rollouts'].get('h24', {}).get('mean_ratio_sample'))} ({res['seconds']}s)", flush=True)
            del model
            if device.type == "cuda":
                torch.cuda.empty_cache()
        if md:
            (out_dir / "summary.md").write_text("\n".join(md))
            print("wrote", out_dir / "summary.md")


if __name__ == "__main__":
    main()
