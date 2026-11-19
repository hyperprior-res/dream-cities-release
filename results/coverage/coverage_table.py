"""B20 step 1: how often each tax setting occurs, in months that build (at least one macro) and months that
do not, in (a) train_full, (b) the coverage store when it exists, (c) the selected plans of the main
checkpoint's audit, (d) the frontier plans of the task file. Counts only; no engine, no model.

    PYTHONPATH=code:hpr-dream .venv/bin/python results/coverage/coverage_table.py [--cov-store PATH[,PATH...]]

Writes results/coverage/coverage_table.json and coverage_table.md beside this file.

Definitions. A month is one plan row (25 columns, ``dc.grammar``): column 0 is the tax (0..20), columns
1..3 the road, fire and police funding levels (0..4 = 0, 25, 50, 75, 100 per cent), columns 5, 10, 15, 20
the four macro kinds (0 = no-op). A month *builds* when any macro kind is non-zero (``dc.data._sum_chunk``
uses the same test). *Builder trajectories* are those whose behaviour label starts with ``builder/``.
Selected plans are the ``plans_effective`` rows of every method and budget in the audit file. Frontier
plans are the task file's e32 plans: for each of its 193 instances, the plan of group ``frontier`` in the
oracle stage of ``wm2-cache/tasks_v2/H24/<start>.npz`` (task ``treasury`` is variant ``treasury_rev``).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc import data as D  # noqa: E402

OUT = Path(__file__).resolve().parent
TRAIN_FULL = D.DATA_ROOT / "train_full"
SELECTED = ROOT / "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24/selected_plans.npz"
TASKS = ROOT / "data/tasks_v2_H24.json"
TASK_CACHE = Path("<cache>/tasks_v2/H24")
VARIANT = {"grow": "grow", "solvent": "solvent", "treasury": "treasury_rev", "recover": "recover", "power": "power"}
LOW_TAX = 4


def month_table(P: np.ndarray) -> dict:
    """P (n, 25) plan rows -> counts by tax (0..20) for building and non-building months, and summaries."""
    P = np.asarray(P).reshape(-1, D.PLAN_WIDTH).astype(np.int64)
    tax = P[:, 0]
    builds = (P[:, 5::5] != 0).any(axis=1)
    fund = P[:, 1:4]
    n = len(P)
    nb = int(builds.sum())
    corner = builds & (tax <= LOW_TAX) & (fund == 0).all(axis=1)
    by_build = np.bincount(tax[builds], minlength=21)[:21]
    by_nobuild = np.bincount(tax[~builds], minlength=21)[:21]
    low = tax <= LOW_TAX
    cut_any = (fund < 4).any(axis=1)
    cut_all0 = (fund == 0).all(axis=1)
    return {
        "months": n, "building_months": nb,
        "share_building": nb / n if n else None,
        "tax_counts_building": by_build.tolist(), "tax_counts_not_building": by_nobuild.tolist(),
        "share_building_months_tax_le4": float((builds & low).sum() / nb) if nb else None,
        "share_all_months_tax_le4": float(low.sum() / n) if n else None,
        "share_months_building_and_tax_le4": float((builds & low).sum() / n) if n else None,
        "share_building_months_any_funding_cut": float((builds & cut_any).sum() / nb) if nb else None,
        "share_building_months_all_funding_0": float((builds & cut_all0).sum() / nb) if nb else None,
        "share_building_months_tax_le4_and_any_funding_cut": float((builds & low & cut_any).sum() / nb) if nb else None,
        "building_months_tax_le4": int((builds & low).sum()),
        "building_months_tax_le4_and_any_funding_cut": int((builds & low & cut_any).sum()),
        "building_months_any_funding_cut": int((builds & cut_any).sum()),
        "building_months_all_funding_0": int((builds & cut_all0).sum()),
        "building_months_tax_le4_all_funding_0": int(corner.sum()),
        "share_building_months_tax_le4_all_funding_0": float(corner.sum() / nb) if nb else None,
        "months_tax_le4": int(low.sum()),
    }


def union_table(parts) -> dict:
    """The month table of a union of sources, from the parts' counts."""
    c = lambda k: int(sum(t[k] for t in parts))  # noqa: E731
    n, nb = c("months"), c("building_months")
    by_b = np.sum([t["tax_counts_building"] for t in parts], axis=0)
    by_n = np.sum([t["tax_counts_not_building"] for t in parts], axis=0)
    out = {"months": n, "building_months": nb, "share_building": nb / n,
           "tax_counts_building": by_b.tolist(), "tax_counts_not_building": by_n.tolist()}
    for k in ("building_months_tax_le4", "building_months_tax_le4_and_any_funding_cut", "building_months_any_funding_cut",
              "building_months_all_funding_0", "building_months_tax_le4_all_funding_0", "months_tax_le4"):
        out[k] = c(k)
    out["share_building_months_tax_le4"] = out["building_months_tax_le4"] / nb
    out["share_building_months_tax_le4_and_any_funding_cut"] = out["building_months_tax_le4_and_any_funding_cut"] / nb
    out["share_building_months_any_funding_cut"] = out["building_months_any_funding_cut"] / nb
    out["share_building_months_all_funding_0"] = out["building_months_all_funding_0"] / nb
    out["share_building_months_tax_le4_all_funding_0"] = out["building_months_tax_le4_all_funding_0"] / nb
    out["share_all_months_tax_le4"] = out["months_tax_le4"] / n
    out["share_months_building_and_tax_le4"] = out["building_months_tax_le4"] / n
    return out


def forced_quake_counts(st) -> dict:
    """Transitions at or after a forced earthquake in their trajectory (the month of the event included)."""
    from dc.engine import DISASTER_EARTHQUAKE
    P = np.asarray(st.plan)
    k = np.flatnonzero(P[:, D.PLAN_FORCED_COL] == DISASTER_EARTHQUAKE)
    if k.size == 0:
        return {"trajectories_with_forced_quake": 0, "transitions_from_forced_quake_on": 0,
                "forced_quake_months": 0, "forced_quake_in_month_0": 0}
    j = st.traj_of(k)
    first = {}
    for jj, kk in zip(j.tolist(), k.tolist()):
        first.setdefault(jj, kk)
    js = np.fromiter(first, dtype=np.int64)
    ks = np.fromiter(first.values(), dtype=np.int64)
    end = st.traj["first_trans"][js].astype(np.int64) + st.traj["H"][js].astype(np.int64)
    return {"trajectories_with_forced_quake": int(js.size), "transitions_from_forced_quake_on": int((end - ks).sum()),
            "forced_quake_months": int(k.size), "forced_quake_in_month_0": int(np.count_nonzero(st.month_of(k) == 0))}


def store_tables(path: Path) -> dict:
    st = D.TrajStore(path)
    P = np.asarray(st.plan)
    lab_t = np.repeat(st.traj["label_idx"].astype(np.int64), st.traj["H"].astype(np.int64))
    is_b = np.array([l.startswith("builder/") for l in st.labels], dtype=bool)[lab_t]
    return {"store": str(path), "trajectories": int(st.n_traj), "transitions": int(st.n_trans),
            "all": month_table(P), "builder_trajectories": month_table(P[is_b]),
            "builder_trajectories_months": int(is_b.sum()), "forced_quake": forced_quake_counts(st)}


def selected_tables() -> dict:
    z = np.load(SELECTED)
    ids = [str(s) for s in z["plan_id"]]
    P = z["plans_effective"]
    out = {"file": str(SELECTED.relative_to(ROOT)), "plans": len(ids), "all": month_table(P)}
    meth = np.array(["|".join(s.split("|")[3:5]) for s in ids])
    for m in sorted(set(meth)):
        out[m] = month_table(P[meth == m])
        out[m]["plans"] = int((meth == m).sum())
    return out


def frontier_tables() -> dict:
    t = json.loads(TASKS.read_text())
    plans, keys, by_task = [], [], {}
    for inst in t["instances"]:
        v = VARIANT[inst["task"]]
        with np.load(TASK_CACHE / f"{inst['start_id']}.npz") as z:
            g = z[f"{v}__oracle__group"]
            p = z[f"{v}__oracle__plans"][g == "frontier"]
        if len(p) != 1:
            raise RuntimeError(f"{inst['start_id']} {inst['task']}: {len(p)} frontier plans")
        plans.append(p[0])
        keys.append(inst["task"])
        by_task.setdefault(inst["task"], []).append(p[0])
    P = np.stack(plans)
    out = {"file": str(TASKS.relative_to(ROOT)), "plans": len(plans), "all": month_table(P)}
    for k, v in by_task.items():
        out[k] = month_table(np.stack(v))
        out[k]["plans"] = len(v)
    return out


def fmt(x) -> str:
    return "-" if x is None else f"{x:.3f}"


def markdown(res: dict) -> str:
    cols = [("train_full, all months", res["train_full"]["all"]),
            ("train_full, builder trajectories", res["train_full"]["builder_trajectories"])]
    for k, v in res.get("coverage_stores", {}).items():
        cols += [(f"{k}, all months", v["all"])]
    if "union" in res:
        cols += [(res["union"]["name"], res["union"]["all"])]
    cols += [("selected plans, all methods", res["selected"]["all"]),
             ("selected plans, random B=1000", res["selected"]["random|B1000"]),
             ("frontier plans", res["frontier"]["all"])]
    L = ["# B20 coverage table (counts from the files; no engine, no model)", "",
         "Share of *building* months (at least one macro) at each tax setting, per source. "
         "Last rows: summaries over all months.", "",
         "| tax | " + " | ".join(c for c, _ in cols) + " |", "|---|" + "---|" * len(cols)]
    for tx in range(21):
        row = []
        for _, t in cols:
            nb = t["building_months"]
            row.append(fmt(t["tax_counts_building"][tx] / nb) if nb else "-")
        L.append(f"| {tx} | " + " | ".join(row) + " |")
    L.append("| **building months** | " + " | ".join(f"{t['building_months']:,}" for _, t in cols) + " |")
    L.append("| **all months** | " + " | ".join(f"{t['months']:,}" for _, t in cols) + " |")
    L.append("| share of months that build | " + " | ".join(fmt(t["share_building"]) for _, t in cols) + " |")
    L.append("| building months at tax <= 4 (share of building months) | "
             + " | ".join(fmt(t["share_building_months_tax_le4"]) for _, t in cols) + " |")
    L.append("| building months at tax <= 4 with a funding cut (share of building months) | "
             + " | ".join(fmt(t["share_building_months_tax_le4_and_any_funding_cut"]) for _, t in cols) + " |")
    L.append("| building months with any funding line below 100 % | "
             + " | ".join(fmt(t["share_building_months_any_funding_cut"]) for _, t in cols) + " |")
    L.append("| building months with all funding at 0 | "
             + " | ".join(fmt(t["share_building_months_all_funding_0"]) for _, t in cols) + " |")
    L.append("| building months at tax <= 4 with all funding at 0 (count) | "
             + " | ".join(f"{t['building_months_tax_le4_all_funding_0']:,}" for _, t in cols) + " |")
    L.append("| the same, share of building months | "
             + " | ".join(fmt(t["share_building_months_tax_le4_all_funding_0"]) for _, t in cols) + " |")
    L.append("| all months at tax <= 4 | " + " | ".join(fmt(t["share_all_months_tax_le4"]) for _, t in cols) + " |")
    L += ["", "Forced earthquakes (transitions at or after a forced earthquake in their trajectory, event month included):", ""]
    stores = [("train_full", res["train_full"])] + list(res.get("coverage_stores", {}).items())
    for k, v in stores:
        q = v["forced_quake"]
        L.append(f"- {k}: {q['transitions_from_forced_quake_on']:,} of {v['transitions']:,} transitions; "
                 f"{q['trajectories_with_forced_quake']:,} trajectories with one ({q['forced_quake_in_month_0']:,} in month 0)")
    if "union" in res:
        u = res["union"]
        L.append(f"- {u['name']}: {u['forced_quake_transitions']:,} of {u['transitions']:,} transitions")
    L += ["", "Share of *non-building* months at each tax setting is in the JSON (`tax_counts_not_building`).", "",
          "By method and budget (selected plans): building months at tax <= 4 / share of months that build", ""]
    for k, v in res["selected"].items():
        if isinstance(v, dict) and "|" in k:
            L.append(f"- {k} ({v['plans']} plans): {fmt(v['share_building_months_tax_le4'])} / {fmt(v['share_building'])}")
    L += ["", "By task (frontier plans): building months at tax <= 4 / share of months that build", ""]
    for k, v in res["frontier"].items():
        if isinstance(v, dict) and k != "all":
            L.append(f"- {k} ({v['plans']} plans): {fmt(v['share_building_months_tax_le4'])} / {fmt(v['share_building'])}")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cov-store", default="")
    args = ap.parse_args()
    res = {"definitions": __doc__.split("Definitions.", 1)[1].strip(), "low_tax": LOW_TAX,
           "train_full": store_tables(TRAIN_FULL), "selected": selected_tables(), "frontier": frontier_tables()}
    if args.cov_store:
        res["coverage_stores"] = {Path(p).name: store_tables(Path(p)) for p in args.cov_store.split(",") if p}
        parts = [res["train_full"]] + list(res["coverage_stores"].values())
        res["union"] = {"name": "union " + " + ".join(["train_full"] + list(res["coverage_stores"])),
                        "all": union_table([t["all"] for t in parts]), "transitions": int(sum(t["transitions"] for t in parts)),
                        "forced_quake_transitions": int(sum(t["forced_quake"]["transitions_from_forced_quake_on"] for t in parts))}
    (OUT / "coverage_table.json").write_text(json.dumps(res, indent=1) + "\n")
    md = markdown(res)
    (OUT / "coverage_table.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
