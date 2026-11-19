"""Specificity controls for the oracle-patching arm .

    PYTHONPATH=hpr-dream:code .venv/bin/python code/scripts/patching_controls.py \
        [--run-dir results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24] \
        [--out results/analysis/patching_controls]

Part 1 re-reads the stored records of the patching arm (``patching.jsonl.gz``, primary set: the emulator accepts, the
32-seed oracle majority rejects); no rollout is run. Part 2 reads the reruns of ``run_patching.py`` on ``recover``
(``--family recover``) when their files exist beside the stored ones:

- ``patching_controls_abr_recover.jsonl.gz``: the primary set's accepted-but-rejected ``recover`` records under the
  symmetric fire patch (``fire_sym``: the fire cells of either the engine or the emulator), its two controls and the
  no-patch redraw;
- ``patching_controls_true_accept_recover.jsonl.gz``: the ``recover`` records of the same searches and budgets that
  the emulator and the 32-seed oracle both accept (the specificity set), under the one-sided fire patch, the
  symmetric one, their controls and the no-patch redraw. A flip is the emulator's verdict turning from accept to
  reject, as on the accepted-but-rejected records.

Statistics. A record is one audit record (instance, search, budget); records that share a plan share its patched
rollouts, as in ``patching_summary.md``. Flip rates and differences carry BCa intervals from the cluster bootstrap
over held-out cities (the record's ``cluster``, as ``patching_summary.md`` clusters; ``hpr_dream.stats``, seed 0):
per comparison at 95 per cent from 20,000 resamples, and corrected for the 18
comparisons of the nine subsystems by their two controls by Bonferroni, at 1 - 0.05/18 = 99.72 per cent from 20,000
resamples. A patch against a control is the
mean over the same records of flip(patch) - flip(control). The fire patch on true acceptances against the fire patch
on accepted-but-rejected plans is a difference of two rates on different records; its interval resamples cities
once for both sets (a resample in which a set has no record is undefined and dropped). 'pct' marks a percentile
interval where BCa is undefined. No conclusion is written here.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
for p in (REPO / "code", REPO / "hpr-dream"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from hpr_dream import stats as S                 # noqa: E402

RUN = REPO / "results" / "audit" / "ladder" / "os_50m_full" / "samples_006000000" / "tasks_v2_H24"
OUT = REPO / "results" / "analysis" / "patching_controls"
ABR_FILE = "patching_controls_abr_recover.jsonl.gz"
TA_FILE = "patching_controls_true_accept_recover.jsonl.gz"
IND_ABR_FILE = "patching_controls_indirect_recover.jsonl.gz"
IND_TA_FILE = "patching_controls_indirect_true_accept_recover.jsonl.gz"
OTHER4_FILE = "patching_controls_abr_other4.jsonl.gz"            # fire_sym and zone_growth_sym, four other families
RZONE_FILE = "patching_controls_abr_recover_zone.jsonl.gz"       # zone_growth_sym, recover

GLOBAL = ("power", "treasury", "valves")
LOCAL = ("zone_growth", "pollution", "traffic", "land_value", "crime", "fire")
SUBSYSTEMS = GLOBAL + LOCAL
PAIRS = ("power+treasury", "power+valves", "treasury+valves")
SYM_OF = {"fire": "fire_sym", "zone_growth": "zone_growth_sym"}  # part 3: the cell rules made symmetric
SYM_SUBSYSTEMS = tuple(SYM_OF.get(s, s) for s in SUBSYSTEMS)
FAMILIES = ("grow", "power", "recover", "solvent", "treasury")
N_COMPARISONS = 18                                 # nine subsystems by two controls
LEVEL = 0.95
LEVEL_CORR = 1.0 - (1.0 - LEVEL) / N_COMPARISONS
N_BOOT = 20000
N_BOOT_CORR = 20000
SEED = 0
LOCAL_BAR = 0.30                                   # protocol: every local rule's point estimate below 0.30
GLOBAL_BAR = 0.60                                  # some global subsystem at least 0.60, its interval above 0.30


def subject_masks(subjects=SUBSYSTEMS + PAIRS):
    return ["none"] + [m for s in subjects for m in (s, f"random~{s}", f"changed~{s}")]


# ----------------------------------------------------------------------------------------------
# Records
# ----------------------------------------------------------------------------------------------
def read_rows(path: Path) -> list:
    with gzip.open(path, "rt") as f:
        return [json.loads(l) for l in f]


def by_record(rows, sel=lambda r: True) -> dict:
    """{record id: {mask: row}}; the record id is the audit record's ``plan_id`` (instance, search, budget, seed)."""
    out = defaultdict(dict)
    for r in rows:
        if sel(r):
            out[r["plan_id"]][r["mask"]] = r
    return dict(out)


def meta(recs: dict) -> dict:
    return {p: next(iter(d.values())) for p, d in recs.items()}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ----------------------------------------------------------------------------------------------
# Statistics
# ----------------------------------------------------------------------------------------------
def _iv(e: S.Estimate) -> dict:
    if np.isfinite(e.bca_lo) and np.isfinite(e.bca_hi):
        return {"lo": e.bca_lo, "hi": e.bca_hi, "interval": "BCa"}
    return {"lo": e.lo, "hi": e.hi, "interval": "pct"}


def rate(flags, clusters) -> dict | None:
    f = np.asarray(flags, dtype=bool)
    if f.size == 0:
        return None
    e = S.conditional_mean(f.astype(np.float64), None, np.asarray(clusters), n_boot=N_BOOT, seed=SEED, level=LEVEL,
                           bca=True)
    return {"k": int(f.sum()), "n": int(f.size), "clusters": e.n_clusters, "rate": e.value, **_iv(e)}


def paired(a, b, clusters) -> dict | None:
    """mean(a - b) over the same records, per comparison (95 %) and corrected (Bonferroni over 18)."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size == 0:
        return None
    c = np.asarray(clusters)
    e = S.excess(a, b, c, n_boot=N_BOOT, seed=SEED, level=LEVEL, bca=True)
    ec = S.excess(a, b, c, n_boot=N_BOOT_CORR, seed=SEED, level=LEVEL_CORR, bca=True)
    i, ic = _iv(e), _iv(ec)
    return {"n": int(a.size), "clusters": e.n_clusters, "patch": float(a.mean()), "control": float(b.mean()),
            "diff": e.value, "lo": i["lo"], "hi": i["hi"], "interval": i["interval"],
            "lo_corr": ic["lo"], "hi_corr": ic["hi"], "interval_corr": ic["interval"],
            "level": LEVEL, "level_corr": LEVEL_CORR}


def two_sample(fa, ca, fb, cb, level=LEVEL, n_boot=N_BOOT) -> dict | None:
    """rate(a) - rate(b) for two record sets on shared cities: one cluster resample for both sets."""
    fa, fb = np.asarray(fa, dtype=np.float64), np.asarray(fb, dtype=np.float64)
    if fa.size == 0 or fb.size == 0:
        return None
    lab = np.concatenate([np.asarray(ca, dtype=object), np.asarray(cb, dtype=object)]).astype(str)
    codes, C = S._encode(lab)
    xa, xb = codes[:fa.size], codes[fa.size:]
    sa, na = S._csum(xa, C, fa), S._csum(xa, C, np.ones(fa.size))
    sb, nb = S._csum(xb, C, fb), S._csum(xb, C, np.ones(fb.size))

    def stat(W):
        return S._div(W @ sa, W @ na) - S._div(W @ sb, W @ nb)

    e = S._from_weights(stat, C, fa.size + fb.size, n_boot, SEED, level, True)[0]
    i = _iv(e)
    return {"a": float(fa.mean()), "n_a": int(fa.size), "clusters_a": int(len(set(ca))), "b": float(fb.mean()),
            "n_b": int(fb.size), "clusters_b": int(len(set(cb))), "clusters_union": int(C), "diff": e.value,
            "lo": i["lo"], "hi": i["hi"], "interval": i["interval"], "level": level,
            "resamples_undefined": e.n_boot_undefined}


# ----------------------------------------------------------------------------------------------
# Tables on one set of records
# ----------------------------------------------------------------------------------------------
def groups_of(m: dict) -> dict:
    """Column groups: all records, each family, and the four families other than recover together."""
    g = {"all": list(m)}
    for fam in FAMILIES:
        g[fam] = [p for p in m if m[p]["task"] == fam]
    g["other four"] = [p for p in m if m[p]["task"] != "recover"]
    return g


def flip_table(recs: dict, masks, groups: dict) -> dict:
    m = meta(recs)
    out = {}
    for gname, pids in groups.items():
        out[gname] = {}
        for mk in masks:
            ps = [p for p in pids if mk in recs[p]]
            out[gname][mk] = rate([recs[p][mk]["flip"] for p in ps], [m[p]["cluster"] for p in ps])
    return out


def paired_table(recs: dict, groups: dict, subjects=SUBSYSTEMS) -> dict:
    m = meta(recs)
    out = {}
    for gname, pids in groups.items():
        out[gname] = {}
        for s in subjects:
            for ctl in (f"random~{s}", f"changed~{s}"):
                ps = [p for p in pids if s in recs[p] and ctl in recs[p]]
                out[gname][f"{s} - {ctl}"] = paired([recs[p][s]["flip"] for p in ps],
                                                    [recs[p][ctl]["flip"] for p in ps],
                                                    [m[p]["cluster"] for p in ps])
    return out


def mechanism_rule(rows) -> dict:
    """The decision set (primary set, random search at B = 1,000; amendment 7): the no-patch redraw rate beside the
    rule's bars, and the unions if every mask flipped independently at the redraw rate."""
    recs = by_record(rows, lambda r: r["primary_set"] and r["method"] == "random" and int(r["budget"]) == 1000)
    m = meta(recs)
    pids = sorted(recs)
    cl = [m[p]["cluster"] for p in pids]
    none = rate([recs[p]["none"]["flip"] for p in pids], cl)
    r, lo, hi = none["rate"], none["lo"], none["hi"]

    def union(x, n):
        return 1.0 - (1.0 - x) ** n

    n_ind_global = [sum(1 for g in GLOBAL if not recs[p][g]["direct"]) for p in pids]
    obs = {
        "any local, all plans": rate([any(recs[p][x]["flip"] for x in LOCAL) for p in pids], cl),
        "any global, all plans": rate([any(recs[p][x]["flip"] for x in GLOBAL) for p in pids], cl),
        "any local, indirect only": rate([any(recs[p][x]["flip"] for x in LOCAL if not recs[p][x]["direct"])
                                          for p in pids], cl),
        "any global, indirect only": rate([any(recs[p][x]["flip"] for x in GLOBAL if not recs[p][x]["direct"])
                                           for p in pids], cl),
    }
    pred = {
        "any local (6 masks)": {"rate": union(r, 6), "lo": union(lo, 6), "hi": union(hi, 6)},
        "any global (3 masks)": {"rate": union(r, 3), "lo": union(lo, 3), "hi": union(hi, 3)},
        "any global, indirect only (per record, its indirect global masks)": {
            "rate": float(np.mean([union(r, n) for n in n_ind_global])),
            "lo": float(np.mean([union(lo, n) for n in n_ind_global])),
            "hi": float(np.mean([union(hi, n) for n in n_ind_global])),
            "indirect_global_masks_per_record": dict(Counter(n_ind_global))},
    }
    per_mask = {x: rate([recs[p][x]["flip"] for p in pids], cl) for x in GLOBAL + LOCAL}
    return {"records": len(pids), "clusters": len(set(cl)), "none": none, "local_bar": LOCAL_BAR,
            "global_bar": GLOBAL_BAR, "predicted_if_independent_at_redraw_rate": pred, "observed": obs,
            "per_mask": per_mask,
            "note": "predicted intervals map the redraw rate's interval endpoints through 1 - (1 - x)^n"}


# ----------------------------------------------------------------------------------------------
# Part 2: the reruns
# ----------------------------------------------------------------------------------------------
def reruns(run_dir: Path, stored_rows) -> dict | None:
    pa, pt = run_dir / ABR_FILE, run_dir / TA_FILE
    if not pa.exists() and not pt.exists():
        return None
    out = {"files": {}}
    stored_abr = by_record(stored_rows, lambda r: r["primary_set"] and r["task"] == "recover")
    abr = ta = None
    if pa.exists():
        rows = read_rows(pa)
        out["files"]["abr"] = {"path": str(pa.relative_to(REPO)), "sha256": sha256(pa), "rows": len(rows)}
        abr = by_record(rows, lambda r: r["primary_set"] and r["task"] == "recover")
    if pt.exists():
        rows = read_rows(pt)
        out["files"]["true_accept"] = {"path": str(pt.relative_to(REPO)), "sha256": sha256(pt), "rows": len(rows)}
        ta = by_record(rows, lambda r: r.get("set") == "true_accept" and r["task"] == "recover")
    sel = run_dir / "patching_controls_true_accept_recover_selection.json"
    if sel.exists():
        out["true_accept_selection"] = json.loads(sel.read_text())

    def counts(recs):
        m = meta(recs)
        return {"records": len(recs), "distinct_plans": len({(m[p]["start_id"], m[p]["plan_hash"]) for p in recs}),
                "clusters": len({m[p]["cluster"] for p in recs}),
                "by_search": dict(Counter(f"{m[p]['method']} B={m[p]['budget']}" for p in recs))}

    out["counts"] = {"accepted_but_rejected_recover_stored": counts(stored_abr)}
    if abr is not None:
        out["counts"]["accepted_but_rejected_recover_rerun"] = counts(abr)
        if set(abr) != set(stored_abr):
            out["counts"]["warning"] = "the rerun's accepted-but-rejected records differ from the stored primary set's"
        masks = subject_masks(("fire_sym",))
        m = meta(abr)
        all_p = sorted(abr)
        out["abr_symmetric"] = {
            "flip_rates": flip_table(abr, masks, {"recover": all_p})["recover"],
            "paired": paired_table(abr, {"recover": all_p}, ("fire_sym",))["recover"],
        }
    if ta is not None:
        out["counts"]["true_accept_recover"] = counts(ta)
        masks = subject_masks(("fire", "fire_sym"))
        all_p = sorted(ta)
        out["true_accept"] = {
            "flip_rates": flip_table(ta, masks, {"recover": all_p})["recover"],
            "paired": paired_table(ta, {"recover": all_p}, ("fire", "fire_sym"))["recover"],
        }
    # the fire patch on true acceptances against the fire patch on accepted-but-rejected plans, both mask rules
    diffs = {}
    if ta is not None:
        mt = meta(ta)
        tp = sorted(ta)
        for rule, mk, src in (("one-sided (stored accepted-but-rejected records)", "fire", stored_abr),
                              ("symmetric (rerun accepted-but-rejected records)", "fire_sym", abr)):
            if src is None:
                diffs[rule] = None
                continue
            ms = meta(src)
            sp = sorted(p for p in src if mk in src[p])
            ft = [ta[p][mk]["flip"] for p in tp if mk in ta[p]]
            ct = [mt[p]["cluster"] for p in tp if mk in ta[p]]
            fa = [src[p][mk]["flip"] for p in sp]
            ca = [ms[p]["cluster"] for p in sp]
            diffs[rule] = {"mask": mk, "true_accept": rate(ft, ct), "accepted_but_rejected": rate(fa, ca),
                           "true_accept_minus_accepted_but_rejected": two_sample(ft, ct, fa, ca)}
        # the same contrast for the controls and the redraw, beside it
        for mk in ("none", "random~fire", "changed~fire", "random~fire_sym", "changed~fire_sym"):
            src = stored_abr if mk in ("random~fire", "changed~fire") else abr
            if mk == "none":
                src = abr if abr is not None else stored_abr
            if src is None:
                continue
            ms = meta(src)
            sp = sorted(p for p in src if mk in src[p])
            ft = [ta[p][mk]["flip"] for p in tp if mk in ta[p]]
            ct = [mt[p]["cluster"] for p in tp if mk in ta[p]]
            if not sp or not ft:
                continue
            diffs[f"beside: {mk}"] = {"mask": mk, "accepted_but_rejected_source": (
                "stored" if src is stored_abr else "rerun"),
                "true_accept": rate(ft, ct),
                "accepted_but_rejected": rate([src[p][mk]["flip"] for p in sp], [ms[p]["cluster"] for p in sp]),
                "true_accept_minus_accepted_but_rejected": two_sample(
                    ft, ct, [src[p][mk]["flip"] for p in sp], [ms[p]["cluster"] for p in sp])}
    out["true_accept_vs_accepted_but_rejected"] = diffs
    # mask sizes: entries overwritten and changed per month and sample, means over each set's records
    sizes = {}
    for sname, recs in (("accepted-but-rejected, stored", stored_abr), ("accepted-but-rejected, rerun", abr),
                        ("true acceptances, rerun", ta)):
        if recs is None:
            continue
        mks = sorted({mk for d in recs.values() for mk in d}, key=lambda x: (x.split("~")[-1], x))
        sizes[sname] = {mk: {f: float(np.mean([d[mk][f] for d in recs.values() if mk in d]))
                             for f in ("entries_full_mean", "entries_eighth_mean", "changed_full_mean",
                                       "changed_eighth_mean", "changed_total_mean")}
                        for mk in mks if "fire" in mk}
    out["mask_sizes"] = sizes
    ind_abr_p, ind_ta_p = run_dir / IND_ABR_FILE, run_dir / IND_TA_FILE
    if ind_abr_p.exists():
        irows = read_rows(ind_abr_p)
        out["files"]["abr_indirect"] = {"path": str(ind_abr_p.relative_to(REPO)), "sha256": sha256(ind_abr_p), "rows": len(irows)}
        iabr = by_record(irows, lambda r: r["primary_set"] and r["task"] == "recover")
        imasks = subject_masks(("fire_overlay",))
        ip = sorted(iabr)
        out["abr_indirect"] = {
            "counts": counts(iabr),
            "flip_rates": flip_table(iabr, imasks, {"recover": ip})["recover"],
            "paired": paired_table(iabr, {"recover": ip}, ("fire_overlay",))["recover"],
        }
    if ind_ta_p.exists():
        itrows = read_rows(ind_ta_p)
        out["files"]["true_accept_indirect"] = {"path": str(ind_ta_p.relative_to(REPO)), "sha256": sha256(ind_ta_p), "rows": len(itrows)}
        ita = by_record(itrows, lambda r: r.get("set") == "true_accept" and r["task"] == "recover")
        imasks = subject_masks(("fire_overlay",))
        itp = sorted(ita)
        out["true_accept_indirect"] = {
            "counts": counts(ita),
            "flip_rates": flip_table(ita, imasks, {"recover": itp})["recover"],
            "paired": paired_table(ita, {"recover": itp}, ("fire_overlay",))["recover"],
        }
    return out


# ----------------------------------------------------------------------------------------------
# Part 3: the primary set with both cell rules symmetric
# ----------------------------------------------------------------------------------------------
def part3(run_dir: Path, stored_rows) -> dict | None:
    """Section 1b's table with fire and zone_growth replaced by fire_sym and zone_growth_sym: the stored records of
    the other seven subsystems, the symmetric masks (and their controls) from the reruns, joined on the record."""
    files = [(f, run_dir / f) for f in (ABR_FILE, OTHER4_FILE, RZONE_FILE)]
    if not any(p.exists() for _, p in files):
        return None
    merged = by_record(stored_rows, lambda r: r["primary_set"])
    sym_masks = {m for s in SYM_OF.values() for m in (s, f"random~{s}", f"changed~{s}")}
    out = {"files": {}, "redraws": {}, "warnings": []}
    for f, p in files:
        if not p.exists():
            out["warnings"].append(f"{f} missing")
            continue
        rows = read_rows(p)
        out["files"][f] = {"path": str(p.relative_to(REPO)), "sha256": sha256(p), "rows": len(rows)}
        recs = by_record(rows, lambda r: r["primary_set"])
        for pid, d in recs.items():
            if pid not in merged:
                out["warnings"].append(f"{f}: record {pid} is not in the stored primary set")
                continue
            for mk, row in d.items():
                if mk in sym_masks:
                    if mk in merged[pid]:
                        out["warnings"].append(f"{f}: {pid} {mk} given twice")
                    merged[pid][mk] = row
        m = meta(recs)
        g = groups_of(m)
        out["redraws"][f] = {k: rate([recs[q]["none"]["flip"] for q in v if "none" in recs[q]],
                                     [m[q]["cluster"] for q in v if "none" in recs[q]]) for k, v in g.items()}
    m = meta(merged)
    out["coverage"] = {mk: {"records": sum(1 for d in merged.values() if mk in d),
                            "of": len(merged)} for mk in sorted(sym_masks)}
    g = groups_of(m)
    out["flip_rates"] = flip_table(merged, [mk for s in ("zone_growth_sym", "fire_sym")
                                            for mk in (s, f"random~{s}", f"changed~{s}")], g)
    out["paired"] = paired_table(merged, {k: g[k] for k in ("all", "recover", "other four")}, SYM_SUBSYSTEMS)
    return out


# ----------------------------------------------------------------------------------------------
# Markdown
# ----------------------------------------------------------------------------------------------
def f_rate(c) -> str:
    if not c:
        return "-"
    tag = "" if c["interval"] == "BCa" else " pct"
    return f"{c['k']}/{c['n']} {c['rate']:.2f} [{c['lo']:.2f}, {c['hi']:.2f}]{tag}"


def f_diff(c, corr=False) -> str:
    if not c:
        return "-"
    lo, hi, it = (c["lo_corr"], c["hi_corr"], c["interval_corr"]) if corr else (c["lo"], c["hi"], c["interval"])
    tag = "" if it == "BCa" else " pct"
    return f"{c['diff']:+.3f} [{lo:+.3f}, {hi:+.3f}]{tag}"


def md_flip_table(tab: dict, masks, cols) -> list:
    L = ["| mask | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for mk in masks:
        L.append(f"| {mk} | " + " | ".join(f_rate(tab[c].get(mk)) for c in cols) + " |")
    return L + [""]


def md_paired_table(tab: dict, cols) -> list:
    L = ["| patch - control | " + " | ".join(f"{c}: 95 % | {c}: corrected" for c in cols) + " |",
         "|---|" + "---|---|" * len(cols)]
    keys = list(next(iter(tab.values())).keys())
    for k in keys:
        L.append(f"| {k} | " + " | ".join(f"{f_diff(tab[c][k])} | {f_diff(tab[c][k], True)}" for c in cols) + " |")
    return L + [""]


def write_md(res: dict, path: Path) -> None:
    P1 = res["part1"]
    L = ["# Patching arm: specificity controls ", "",
         f"Generated by `code/scripts/patching_controls.py` at {res['generated']}. Stored records: "
         f"`{res['inputs']['patching']['path']}` (sha256 {res['inputs']['patching']['sha256'][:12]}), primary set "
         "(the emulator accepts at 4 of 8 samples, the 32-seed oracle majority rejects). Main checkpoint "
         "`os_50m_full/samples_006000000`.", "",
         "Flip = the patched verdict rejects (fewer than 4 of 8 patched samples satisfy the task). Cells: flips/records, "
         "rate, interval. Intervals: BCa cluster bootstrap over held-out cities (the record's `cluster`), seed 0; "
         f"95 % from {N_BOOT:,} resamples; 'corrected' = Bonferroni over the {N_COMPARISONS} comparisons (nine "
         f"subsystems by two controls), {LEVEL_CORR * 100:.2f} % from {N_BOOT_CORR:,} resamples, within each column "
         "group. 'pct': percentile interval where BCa is undefined. A patch against a control is the mean over the same "
         "records of flip(patch) - flip(control). All plans (local masks never touch a predicate input, so their "
         "indirect-only rows equal these; the global rows over all plans include direct reads).", ""]
    L += ["## Part 1. Re-read of the stored records (no new rollouts)", ""]
    c = P1["counts"]
    L += [f"Primary set: {c['records']} records, {c['distinct_plans']} distinct plans, {c['clusters']} cities. By task "
          "family: " + ", ".join(f"{k} {v}" for k, v in c["by_family"].items()) + ".", ""]
    L += ["### 1a. Flip rates by task family (primary set)", ""]
    cols = ["all"] + list(FAMILIES) + ["other four"]
    L += md_flip_table(P1["flip_rates"], subject_masks(), cols)
    L += ["### 1b. Each subsystem against its two controls, paired on the same records (primary set)", ""]
    L += md_paired_table(P1["paired"], ["all", "recover", "other four"])
    R = P1["restricted"]
    L += ["### 1c. Restricted to the searches the paper describes (margin-scored random search, pool-seeded search)", "",
          "Primary-set records by the search that produced them:", "",
          "| search (method, scoring) | records | of which recover |", "|---|---|---|"]
    for k, v in R["records_by_search"].items():
        L.append(f"| {k} | {v['records']} | {v['recover']} |")
    L += ["", R["note"], "",
          f"Restricted set: {R['counts']['records']} records, {R['counts']['distinct_plans']} distinct plans, "
          f"{R['counts']['clusters']} cities; by family "
          + ", ".join(f"{k} {v}" for k, v in R["counts"]["by_family"].items()) + ".", ""]
    L += md_flip_table(R["flip_rates"], subject_masks(SUBSYSTEMS), ["all", "recover", "other four"])
    L += md_paired_table(R["paired"], ["all", "recover", "other four"])
    M = P1["mechanism_rule"]
    L += ["### 1d. The protocol mechanism rule (protocol; amendment 7 decision set)", "",
          f"Decision set: primary set, random search at B = 1,000: {M['records']} records, {M['clusters']} cities.", "",
          "| quantity | value |", "|---|---|",
          f"| no-patch redraw flip rate | {f_rate(M['none'])} |",
          f"| rule's bar for every local rule (point estimate below) | {M['local_bar']:.2f} |",
          f"| rule's bar for some global subsystem (at least, interval above {M['local_bar']:.2f}) | {M['global_bar']:.2f} |",
          ""]
    L += ["Unions if every mask flipped independently at the redraw rate (1 - (1 - r)^n; interval: the redraw rate's "
          "interval endpoints mapped through the same function), beside the observed unions:", "",
          "| union | if independent at the redraw rate | observed |", "|---|---|---|"]
    pr, ob = M["predicted_if_independent_at_redraw_rate"], M["observed"]
    L.append(f"| any local, 6 masks (all plans = indirect only) | {pr['any local (6 masks)']['rate']:.2f} "
             f"[{pr['any local (6 masks)']['lo']:.2f}, {pr['any local (6 masks)']['hi']:.2f}] | "
             f"{f_rate(ob['any local, all plans'])} |")
    L.append(f"| any global, 3 masks, all plans | {pr['any global (3 masks)']['rate']:.2f} "
             f"[{pr['any global (3 masks)']['lo']:.2f}, {pr['any global (3 masks)']['hi']:.2f}] | "
             f"{f_rate(ob['any global, all plans'])} |")
    q = pr["any global, indirect only (per record, its indirect global masks)"]
    L.append(f"| any global, indirect only (per record, its {dict(sorted(q['indirect_global_masks_per_record'].items()))} "
             f"indirect global masks: count of masks -> records) | {q['rate']:.2f} [{q['lo']:.2f}, {q['hi']:.2f}] | "
             f"{f_rate(ob['any global, indirect only'])} |")
    L.append(f"| any global, indirect only, 3 masks for every record (R1's form) | {pr['any global (3 masks)']['rate']:.2f} "
             f"[{pr['any global (3 masks)']['lo']:.2f}, {pr['any global (3 masks)']['hi']:.2f}] | "
             f"{f_rate(ob['any global, indirect only'])} |")
    L += ["", "Per-mask flip rates on the decision set: " + "; ".join(
        f"{k} {f_rate(v)}" for k, v in M["per_mask"].items()) + ".", ""]
    P2 = res.get("part2")
    L += ["## Part 2. Reruns on `recover` (symmetric fire rule; true acceptances)", ""]
    if not P2:
        L += ["Not run yet: no rerun files beside the stored records.", ""]
    else:
        L += md_part2(P2)
    P3 = res.get("part3")
    L += ["## Part 3. The primary set with both cell rules symmetric (`fire_sym`, `zone_growth_sym`)", ""]
    if not P3:
        L += ["Not run yet.", ""]
    else:
        L += md_part3(P3)
    path.write_text("\n".join(L))


def md_part3(P3: dict) -> list:
    L = ["Section 1b's table with `fire` and `zone_growth` replaced by their symmetric versions (cells of either the "
         "engine or the emulator, written with the engine's tile; controls drawn for the symmetric mask by the same "
         "rules). The other seven subsystems' rows are the stored records, as in 1b. The symmetric masks come from the "
         "reruns, joined to the stored records on the record: `fire_sym` on `recover` from part 2's rerun, on the other "
         "four families from `patching_controls_abr_other4`; `zone_growth_sym` on `recover` from "
         "`patching_controls_abr_recover_zone`, on the other four from `patching_controls_abr_other4`. Same samples "
         f"(8) and verdict rule (4 of 8); corrected = Bonferroni over the {N_COMPARISONS} comparisons.", ""]
    for k, v in P3["files"].items():
        L.append(f"- `{v['path']}` ({v['rows']} rows, sha256 {v['sha256'][:12]})")
    L.append("")
    L.append("Records carrying each symmetric mask: " + "; ".join(
        f"{k} {v['records']}/{v['of']}" for k, v in P3["coverage"].items()) + ".")
    if P3["warnings"]:
        L += ["", "Warnings: " + "; ".join(P3["warnings"][:10])]
    L += ["", "### 3a. Each subsystem against its two controls, paired on the same records (primary set)", ""]
    L += md_paired_table(P3["paired"], ["all", "recover", "other four"])
    L += ["### 3b. Flip rates by task family of the two symmetric masks and their controls (primary set)", ""]
    cols = ["all"] + list(FAMILIES) + ["other four"]
    L += md_flip_table(P3["flip_rates"], list(next(iter(P3["flip_rates"].values())).keys()), cols)
    L += ["The no-patch redraw of each rerun file, by family (each file redraws only its own records):", "",
          "| file | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for f, d in P3["redraws"].items():
        L.append(f"| {f} | " + " | ".join(f_rate(d.get(c)) for c in cols) + " |")
    return L + [""]


def md_part2(P2: dict) -> list:
    L = []
    for k, v in P2["files"].items():
        L.append(f"- {k}: `{v['path']}` ({v['rows']} rows, sha256 {v['sha256'][:12]})")
    L.append("")
    if "true_accept_selection" in P2:
        s = P2["true_accept_selection"]
        L += [f"Specificity set (true acceptances): {s.get('note', '')}", ""]
    L += ["| set | records | distinct plans | cities | by search |", "|---|---|---|---|---|"]
    for k, v in P2["counts"].items():
        if isinstance(v, dict):
            L.append(f"| {k} | {v['records']} | {v['distinct_plans']} | {v['clusters']} | "
                     + ", ".join(f"{a} {b}" for a, b in sorted(v["by_search"].items())) + " |")
    if "warning" in P2["counts"]:
        L += ["", f"Warning: {P2['counts']['warning']}"]
    L.append("")
    if "abr_symmetric" in P2:
        A = P2["abr_symmetric"]
        L += ["### 2a. Symmetric fire against its controls on the accepted-but-rejected `recover` records (rerun)", "",
              "| mask | flips |", "|---|---|"]
        for k, v in A["flip_rates"].items():
            L.append(f"| {k} | {f_rate(v)} |")
        L += ["", "| patch - control | 95 % | corrected (18) |", "|---|---|---|"]
        for k, v in A["paired"].items():
            L.append(f"| {k} | {f_diff(v)} | {f_diff(v, True)} |")
        L.append("")
    if "true_accept" in P2:
        T = P2["true_accept"]
        L += ["### 2b. True acceptances on `recover` (the emulator and the 32-seed oracle accept): flip = accept to reject",
              "", "| mask | flips |", "|---|---|"]
        for k, v in T["flip_rates"].items():
            L.append(f"| {k} | {f_rate(v)} |")
        L += ["", "| patch - control | 95 % | corrected (18) |", "|---|---|---|"]
        for k, v in T["paired"].items():
            L.append(f"| {k} | {f_diff(v)} | {f_diff(v, True)} |")
        L.append("")
    D = P2.get("true_accept_vs_accepted_but_rejected") or {}
    if D:
        L += ["### 2c. Flip rate on true acceptances against flip rate on accepted-but-rejected plans", "",
              "Difference = true acceptances minus accepted-but-rejected, 95 % BCa interval from one cluster resample of "
              "cities for both sets.", "",
              "| rule / mask | true acceptances | accepted-but-rejected | difference [95 %] |", "|---|---|---|---|"]
        for k, v in D.items():
            if not v:
                L.append(f"| {k} | - | - | - |")
                continue
            d = v["true_accept_minus_accepted_but_rejected"]
            tag = "" if d["interval"] == "BCa" else " pct"
            L.append(f"| {k} | {f_rate(v['true_accept'])} | {f_rate(v['accepted_but_rejected'])} | "
                     f"{d['diff']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}]{tag} |")
        L.append("")
    Z = P2.get("mask_sizes") or {}
    if Z:
        L += ["### 2d. Fire masks' sizes", "",
              "Entries per month and sample, means over the set's records: overwritten full-resolution cells / eighth "
              "cells; changed (overwritten entries whose sampled value differed from the engine's) full / eighth / all.",
              "", "| set | mask | overwritten full / eighth | changed full / eighth / all |", "|---|---|---|---|"]
        for sname, d in Z.items():
            for mk, v in d.items():
                L.append(f"| {sname} | {mk} | {v['entries_full_mean']:.1f} / {v['entries_eighth_mean']:.1f} | "
                         f"{v['changed_full_mean']:.1f} / {v['changed_eighth_mean']:.1f} / {v['changed_total_mean']:.1f} |")
        L.append("")
    return L


# ----------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------
def part1(rows) -> dict:
    prim = by_record(rows, lambda r: r["primary_set"])
    m = meta(prim)
    counts = {"records": len(prim), "distinct_plans": len({(m[p]["start_id"], m[p]["plan_hash"]) for p in prim}),
              "clusters": len({m[p]["cluster"] for p in prim}),
              "by_family": {f: sum(1 for p in prim if m[p]["task"] == f) for f in FAMILIES}}
    g = groups_of(m)
    out = {"counts": counts, "flip_rates": flip_table(prim, subject_masks(), g),
           "paired": paired_table(prim, {k: g[k] for k in ("all", "recover", "other four")})}
    # restricted to the searches the paper describes
    srch = Counter()
    rec_srch = Counter()
    for p in prim:
        k = f"{m[p]['method']} ({m[p]['scoring']})"
        srch[k] += 1
        rec_srch[k] += m[p]["task"] == "recover"
    by_search = {k: {"records": srch[k], "recover": rec_srch[k]} for k in sorted(srch)}
    by_search.setdefault("cem_seeded (margin), the pool-seeded search", {"records": 0, "recover": 0})
    keep = {p: d for p, d in prim.items() if m[p]["method"] == "random" and m[p]["scoring"] == "margin"}
    mk = meta(keep)
    gk = groups_of(mk)
    out["restricted"] = {
        "records_by_search": by_search,
        "note": ("The pool-seeded search (`cem_seeded`) has no record in the patching arm: it ran as a separate audit "
                 "(`tasks_v2_H24_cem_seeded`), which was not patched. The restricted set is therefore margin-scored "
                 "random search alone (method `random`, scoring `margin`)."),
        "counts": {"records": len(keep), "distinct_plans": len({(mk[p]["start_id"], mk[p]["plan_hash"]) for p in keep}),
                   "clusters": len({mk[p]["cluster"] for p in keep}),
                   "by_family": {f: sum(1 for p in keep if mk[p]["task"] == f) for f in FAMILIES}},
        "flip_rates": flip_table(keep, subject_masks(SUBSYSTEMS), {k: gk[k] for k in ("all", "recover", "other four")}),
        "paired": paired_table(keep, {k: gk[k] for k in ("all", "recover", "other four")}),
    }
    out["mechanism_rule"] = mechanism_rule(rows)
    return out


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-dir", default=str(RUN))
    ap.add_argument("--out", default=str(OUT), help="output path without extension (.json and .md are written)")
    a = ap.parse_args(argv)
    run_dir = Path(a.run_dir).resolve()
    src = run_dir / "patching.jsonl.gz"
    rows = read_rows(src)
    res = {"generated": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
           "inputs": {"patching": {"path": str(src.relative_to(REPO)), "sha256": sha256(src), "rows": len(rows)}},
           "settings": {"level": LEVEL, "level_corrected": LEVEL_CORR, "comparisons": N_COMPARISONS,
                        "n_boot": N_BOOT, "n_boot_corrected": N_BOOT_CORR, "seed": SEED,
                        "clusters": "record's cluster (held-out city)", "correction": "Bonferroni"},
           "part1": part1(rows), "part2": reruns(run_dir, rows), "part3": part3(run_dir, rows)}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(res, indent=1, default=float))
    write_md(res, out.with_suffix(".md"))
    print(f"wrote {out.with_suffix('.json')} and {out.with_suffix('.md')}")


if __name__ == "__main__":
    main()
