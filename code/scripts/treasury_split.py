"""The treasury identity's breach rate, accepted trajectories split by the oracle .

``treasury_identity.md`` of the main checkpoint (``run_patching.py``, ``identity_report``) splits the emulator's
sampled trajectories of the selected plans only by the emulator's verdict on the record (``grader_p`` >= 0.5).
This splits the accepted ones again by the 32-seed majority oracle's verdict on the same record
(``oracle_accept``): *wrongly accepted* (the oracle rejects) against *rightly accepted* (the oracle accepts), with
the rejected ones beside them, per search and budget and pooled over budgets per search.

Inputs, read only: the run's ``records.jsonl.gz``, ``selected_plans.npz``, ``config.json`` and
``patching_costs.json`` (whose ``work`` names the identity pass's per-(start, forced events) files
``<work>/identity/<start>__<forced>.npz``: 8 emulator samples per distinct plan, written by
``run_patching.py identity_pass``; they hold the per-trajectory scalars the breach is computed from). The breach
and its measure are ``identity_report``'s: per trajectory, the 24-month sum of the form-B residual over the funds
at month 0 (``dc.patching.created_share``), breached above 5 per cent; trajectories with a non-positive starting
treasury or a month with |funds| >= 2^24 are left out. Each record counts once (8 trajectories). Intervals: the
same 95 per cent BCa cluster bootstrap over held-out cities (2,000 resamples, seed 0) as ``identity_report``; the
difference wrongly minus rightly accepted by the same bootstrap, both groups on the same city resamples. The
emulator-verdict groups are recomputed and checked against ``patching_costs.json`` (``identity.material``) before
anything is written.

    PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/treasury_split.py [--run DIR]

Writes results/analysis/treasury_identity_split.json and .md.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "scripts"))
import run_patching as RP  # noqa: E402  (Run, the identity report's helpers; no engine or model is loaded)
from hpr_dream import stats as hs  # noqa: E402

A, PT = RP.A, RP.PT
MAIN = ROOT / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24"
GROUPS = ("wrongly accepted", "rightly accepted", "rejected")


def trajectories(run_dir: Path) -> tuple[list, str]:
    """[(record, verdict group, created shares (8,), usable mask (8,))] for every selected record of the run."""
    run = RP.Run(run_dir)
    work = Path(json.loads((run_dir / "patching_costs.json").read_text())["work"]) / "identity"
    rec_by_hash = defaultdict(list)
    for r in run.records:
        inst = run.inst.get(r["instance"])
        if inst is None or r["plan_id"] not in run.plan_of:
            continue
        rec_by_hash[(inst.start_id, inst.forced_key, A.plan_hash(run.plan_of[r["plan_id"]]))].append(r)
    out = []
    for p in sorted(work.glob("*.npz")):
        sid, fk = p.stem.split("__", 1)
        with np.load(p) as z:
            if not bool(z["emu_available"]):
                continue
            hashes = [str(h) for h in z["hashes"]]
            kinds = [str(k) for k in z["kinds"]]
            ti = PT.treasury_identity(z["emu_scalars"], z["emu_cost"], z["emu_ledger"], z["levels"][:, None])
            sc = z["emu_scalars"]
        shB = PT.created_share(sc, ti["resid_B"])
        okm = ~ti["unrepresentable"].any(-1) & np.isfinite(shB)
        for i, (h, kd) in enumerate(zip(hashes, kinds)):
            if "selected" not in kd:
                continue
            for r in rec_by_hash.get((sid, fk, h), []):
                acc = float(r["grader_p"]) >= A.ACCEPT_P
                g = ("rightly accepted" if r["oracle_accept"] else "wrongly accepted") if acc else "rejected"
                out.append((r, g, shB[i], okm[i]))
    return out, str(work)


def _flat(items):
    b = np.concatenate([x[2] for x in items]) if items else np.zeros(0)
    ok = np.concatenate([x[3] for x in items]) if items else np.zeros(0, bool)
    cl = np.repeat([x[0]["cluster"] for x in items], RP.K) if items else np.zeros(0)
    return b, ok, cl


def cell(items, mid: float) -> dict:
    b, ok, cl = _flat(items)
    out = {"records": len(items), "trajectories": int(b.size), "left_out": int((~ok).sum())}
    if not ok.any():
        return {**out, "breached": 0, "rate": None, "bca": None, "n_clusters": 0}
    f = b[ok] > mid
    e = RP._est(f, cl[ok])
    out.update(breached=int(f.sum()), rate=float(e.value), n_clusters=int(e.n_clusters),
               bca=[e.bca_lo, e.bca_hi] if np.isfinite(e.bca_lo) else None, percentile=[e.lo, e.hi],
               mean_share=float(np.mean(b[ok])))
    if not f.any():     # no breach: the BCa interval is degenerate; give the exact one-sided bound on clusters (R1 m16)
        out["zero_event_upper_bound"] = hs.zero_count_upper_bound(e.n_clusters)
    return out


def difference(wrong, right, mid: float, n_boot: int = 2000, seed: int = 0) -> dict | None:
    """Breach rate of the wrongly accepted minus that of the rightly accepted, both on the same cluster resamples."""
    bw, okw, cw = _flat(wrong)
    br, okr, cr = _flat(right)
    if not okw.any() or not okr.any():
        return None
    fw, fr = (bw[okw] > mid).astype(float), (br[okr] > mid).astype(float)
    codes, C = hs._encode(np.concatenate([cw[okw], cr[okr]]))
    kw, kr = codes[:fw.size], codes[fw.size:]
    sw, nw = hs._csum(kw, C, fw), hs._csum(kw, C, np.ones_like(fw))
    sr, nr = hs._csum(kr, C, fr), hs._csum(kr, C, np.ones_like(fr))
    stat = lambda W: hs._div(W @ sw, W @ nw) - hs._div(W @ sr, W @ nr)  # noqa: E731
    e = hs._from_weights(stat, C, fw.size + fr.size, n_boot, seed, hs.LEVEL, True)[0]
    return {"value": e.value, "bca": [e.bca_lo, e.bca_hi] if np.isfinite(e.bca_lo) else None,
            "percentile": [e.lo, e.hi], "n_clusters": int(C), "n_boot_undefined": e.n_boot_undefined}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default=str(MAIN))
    ap.add_argument("--out", default=str(ROOT / "results/analysis"))
    a = ap.parse_args(argv)
    run_dir = Path(a.run)
    items, work = trajectories(run_dir)
    lo, mid, hi = PT.MATERIAL_SHARES
    by = defaultdict(lambda: defaultdict(list))
    for x in items:
        r, g = x[0], x[1]
        by[(r["method"], int(r["budget"]))][g].append(x)
        by[(r["method"], "all budgets")][g].append(x)
    # check: the emulator-verdict groups are identity_report's
    stored = json.loads((run_dir / "patching_costs.json").read_text())["identity"]["material"]
    for (m, B), d in by.items():
        if B == "all budgets":
            continue
        for lab, its in (("accepts", d["wrongly accepted"] + d["rightly accepted"]), ("rejects", d["rejected"])):
            key = f"selected: {m} B={B}, emulator {lab}"
            if not its:
                continue
            c = cell(its, mid)
            s = stored.get(key)
            if s is None or s["trajectories"] != c["trajectories"] - c["left_out"] or s["left_out"] != c["left_out"] \
                    or abs(s["B_gt_5"] - c["rate"]) > 1e-12:
                raise SystemExit(f"{key}: recomputed {c} does not match the stored identity report {s}")
    order = sorted(by, key=lambda k: (k[0], 10 ** 9 if k[1] == "all budgets" else k[1]))
    rows = []
    for k in order:
        d = by[k]
        rows.append({"method": k[0], "budget": k[1], **{g: cell(d[g], mid) for g in GROUPS},
                     "wrong_minus_right": difference(d["wrongly accepted"], d["rightly accepted"], mid)})
    res = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "run": str(run_dir.relative_to(ROOT)) if run_dir.is_relative_to(ROOT) else str(run_dir),
           "identity_files": work, "threshold": mid,
           "definitions": {"breach": f"created money above {mid:.0%} of the starting treasury over 24 months "
                                     "(form B, dc.patching.created_share), per emulator trajectory",
                           "wrongly accepted": "the emulator accepts the record's plan (grader_p >= 0.5) and the 32-seed "
                                               "majority oracle rejects it (oracle_accept false)",
                           "rightly accepted": "the emulator accepts and the oracle accepts",
                           "rejected": "the emulator rejects (as in treasury_identity.md)",
                           "interval": "95 % BCa cluster bootstrap over held-out cities, 2,000 resamples, seed 0 "
                                       "(run_patching._est, as treasury_identity.md); percentile beside it",
                           "wrong_minus_right": "difference of the two rates, both groups on the same city resamples",
                           "zero_event_upper_bound": "a cell with no breach: one-sided 95 % exact binomial upper bound "
                                                     "on its clusters (hpr_dream.stats.zero_count_upper_bound) in place "
                                                     "of the degenerate BCa interval [0, 0]"},
           "check": "emulator accepts / rejects groups recomputed and equal to patching_costs.json identity.material "
                    "(trajectories and the >5 % rate) for every search and budget",
           "rows": rows}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "treasury_identity_split.json").write_text(json.dumps(res, indent=1, default=float))

    def c(x):
        if x["rate"] is None:
            return f"0/{x['trajectories']} -"
        iv = f"[{x['bca'][0]:.2f}, {x['bca'][1]:.2f}]" if x["bca"] else f"[pct {x['percentile'][0]:.2f}, {x['percentile'][1]:.2f}]"
        if "zero_event_upper_bound" in x:
            iv = f"[0, {x['zero_event_upper_bound']:.2f} one-sided]"
        return f"{x['breached']}/{x['trajectories'] - x['left_out']} {x['rate']:.3f} {iv} ({x['records']} records)"

    def dfx(x):
        if x is None:
            return "-"
        iv = f"[{x['bca'][0]:+.3f}, {x['bca'][1]:+.3f}]" if x["bca"] else f"[pct {x['percentile'][0]:+.3f}, {x['percentile'][1]:+.3f}]"
        return f"{x['value']:+.3f} {iv}"

    L = ["# Treasury identity: accepted trajectories split by the oracle", "",
         f"Generated {res['generated']} by `code/scripts/treasury_split.py` on `{res['run']}`, per-trajectory data from "
         f"`{work}`. Breach: {res['definitions']['breach']}. Cells: breached / trajectories, rate, "
         f"{res['definitions']['interval']}. Check: {res['check']}.", "",
         "| search | evaluations | wrongly accepted | rightly accepted | rejected | wrongly minus rightly |",
         "|---|---|---|---|---|---|"]
    for r in rows:
        b = r["budget"] if isinstance(r["budget"], str) else f"{r['budget']:,}"
        L.append(f"| {r['method']} | {b} | {c(r['wrongly accepted'])} | {c(r['rightly accepted'])} | {c(r['rejected'])} | "
                 f"{dfx(r['wrong_minus_right'])} |")
    (out / "treasury_identity_split.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
