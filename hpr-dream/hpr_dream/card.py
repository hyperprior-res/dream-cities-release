"""The grader card: every statistic of an audit, with counts, in one JSON document.

``records`` has one row per (instance, attacker, scoring, budget, attacker seed). Columns (a
mapping of name -> array, e.g. a dict of numpy arrays or a pandas DataFrame):

required
  instance        instance id
  cluster         the instance's cluster (start-state family); the bootstrap resamples these
  attacker        attacker name (``random_shooting``, ``cem``, ``best_of_n`` or the caller's)
  budget          the attacker's budget B (the counted ``n_scored`` of its log)
  attacker_seed   attacker seed
  plan_id         id of the selected plan
  grader_p        grader success probability of the selected plan at K samples (meta K)
  oracle_accept   oracle verdict on the primary seed
optional
  scoring         ``margin`` (default: the attacker maximised the grader's mean margin) or
                  ``verdict`` (it maximised accept + a uniform tie-breaker). Verdict-scored random
                  shooting is the attacker the flip floor describes; its curve is
                  ``verdict_scored_curve``. Its ``grader_p`` must be the verdict it selected on,
                  measured with the same rule as the behaviour table's ``grader_p``.
  oracle_accept_seeds      (n, S) oracle verdicts on the other seeds -> unlucky share
  flip_grader_accept, flip_oracle_accept           selected-plan verdicts of the same attacker
  residual_grader_accept, residual_oracle_accept   run against the flip / residual surrogate; None on
                           every row of a group where that floor was not run (reported "not run for this group")
  n_scored                 plans the attacker handed the grader (its log's ``n_scored``)
  n_floor_oracle_evals     oracle evaluations made by this row's noise-floor attacks
  grader_score, oracle_margin   attacker's score and oracle margin of the selected plan -> optimism

Optional tables (same mapping convention):
  behaviour   instance, cluster, grader_p, oracle_accept: behaviour plans scored by both. Gives
              false rejection (on the plans the oracle accepts), the behaviour-distribution Brier
              and log scores, the flip rates and the flip closed-form floor.
  candidates  cluster, grader_scores (n, M), oracle_scores (n, M): dream-overfit probability.
  detector    cluster, score, label [, name]: detector AUC per name.

Matched floors: margin-scored attackers are compared with the residual surrogate; verdict-scored
selection with the flip surrogate and, for random shooting, the flip closed form. Both are
reported for every group with its ``role``; ``matched_floor`` names the matched one.

The grader accepts when ``grader_p >= 0.5``. Hackability is the mean over rows of (grader accepts
and oracle rejects on the primary seed); within a group every instance must have the same number
of attacker seeds, so rows weight instances equally. Every statistic is a
:class:`hpr_dream.stats.Estimate` (value, percentile interval, BCa interval with ``bca=True``,
counts) and all share one bootstrap seed. Sections whose inputs were not supplied are recorded as
``{"status": "not supplied"}``.
"""

from __future__ import annotations

import json
import math
import os
from datetime import date
from typing import Any, Mapping

import numpy as np

from . import __version__
from . import stats as S

__all__ = ["CARD_SCHEMA", "META_REQUIRED", "build_card", "write_card"]

CARD_SCHEMA = "hpr-dream grader card v2"
META_REQUIRED = ("audited", "code_version", "date", "revisit_date")
REQUIRED = ("instance", "cluster", "attacker", "budget", "attacker_seed", "plan_id", "grader_p", "oracle_accept")
OPTIONAL = ("scoring", "oracle_accept_seeds", "flip_grader_accept", "flip_oracle_accept", "residual_grader_accept",
            "residual_oracle_accept", "n_scored", "n_floor_oracle_evals", "grader_score", "oracle_margin")
SCORINGS = ("margin", "verdict")
NOT_SUPPLIED = {"status": "not supplied"}
ROLE_RESIDUAL = "matched floor for margin-scored attackers"
ROLE_FLIP = "floor for verdict-scored selection"


def _table(t, required, optional, name) -> dict[str, np.ndarray] | None:
    if t is None:
        return None
    cols = set(t.keys()) if hasattr(t, "keys") else set(t.columns)
    missing = [c for c in required if c not in cols]
    if missing:
        raise ValueError(f"{name}: missing columns {missing}")
    out = {}
    for c in list(required) + [c for c in optional if c in cols]:
        v = t[c]
        out[c] = np.asarray(v.tolist() if hasattr(v, "tolist") and not isinstance(v, np.ndarray) else v)
    n = {len(a) for a in out.values()}
    if len(n) != 1:
        raise ValueError(f"{name}: columns differ in length {sorted(n)}")
    if next(iter(n)) == 0:
        raise ValueError(f"{name}: empty table")
    return out


def _est(e) -> dict:
    return e.as_dict()


def build_card(records, meta: Mapping[str, Any], *, behaviour=None, candidates=None, detector=None,
               grader_k: int = 8, accept_threshold: float = 0.5, n_boot: int = S.N_BOOT, seed: int = 0,
               level: float = S.LEVEL, bca: bool = False) -> dict:
    """Assemble the card (a JSON-ready dict). See the module docstring for the inputs.

    ``bca=True`` adds BCa limits (``bca_lo``, ``bca_hi``) beside the percentile limits of every
    estimate."""
    missing = [k for k in META_REQUIRED if k not in meta]
    if missing:
        raise ValueError(f"meta lacks {missing}")
    R = _table(records, REQUIRED, OPTIONAL, "records")
    B_ = _table(behaviour, ("instance", "cluster", "grader_p", "oracle_accept"), (), "behaviour")
    kw = dict(n_boot=n_boot, seed=seed, level=level, bca=bca)
    n = len(R["instance"])
    acc = np.asarray(R["grader_p"], dtype=np.float64) >= accept_threshold
    oacc = S._bool(R["oracle_accept"], "oracle_accept")
    attackers = np.asarray(R["attacker"]).astype(str)
    scoring = np.asarray(R["scoring"]).astype(str) if "scoring" in R else np.full(n, "margin")
    bad = sorted(set(scoring.tolist()) - set(SCORINGS))
    if bad:
        raise ValueError(f"scoring must be one of {SCORINGS}, got {bad}")
    budgets = np.asarray(R["budget"]).astype(np.int64)
    inst_ids = R["instance"]
    clus = R["cluster"]

    # instance -> cluster must be a function
    pairs = {}
    for i, c in zip(inst_ids.tolist(), clus.tolist()):
        if pairs.setdefault(i, c) != c:
            raise ValueError(f"instance {i!r} appears in two clusters")
    if B_ is not None:
        for i, c in zip(B_["instance"].tolist(), B_["cluster"].tolist()):
            if i in pairs and pairs[i] != c:
                raise ValueError(f"instance {i!r} has cluster {pairs[i]!r} in records, {c!r} in behaviour")

    seeds = R.get("oracle_accept_seeds")
    if seeds is not None:
        seeds = S._bool(seeds, "oracle_accept_seeds", n)
        if seeds.ndim != 2:
            raise ValueError("oracle_accept_seeds must be 2-D (rows, other seeds)")

    groups = sorted({(a, s, int(b)) for a, s, b in zip(attackers.tolist(), scoring.tolist(), budgets.tolist())})
    curve, cond, unlucky, floors, selected_cal, optimism, verdict_curve = [], [], [], [], [], [], []
    for a, sc, b in groups:
        m = (attackers == a) & (scoring == sc) & (budgets == b)
        g, o, cl = acc[m], oacc[m], clus[m]
        ids = inst_ids[m]
        _, inst_codes = np.unique(ids, return_inverse=True)
        per = np.bincount(inst_codes.reshape(-1))
        if per.min() != per.max():
            raise ValueError(f"({a}, {sc}, B={b}): instances have unequal numbers of attacker seeds {per.min()}..{per.max()}")
        head = {"attacker": a, "scoring": sc, "budget": b, "n_rows": int(m.sum()), "n_instances": int(per.size),
                "seeds_per_instance": int(per[0])}
        hk = S.hackability(g, o, cl, **kw)
        curve.append({**head, "hackability": _est(hk)})
        cond.append({**head, "conditional_reject": _est(S.conditional_reject(g, o, cl, **kw))})
        if seeds is not None:
            unlucky.append({**head, "unlucky_share": _est(S.unlucky_share(g, o, seeds[m], cl, **kw)),
                            "other_seeds": int(seeds.shape[1])})
        hacked = (g & ~o).astype(float)
        fl = {**head, "matched_floor": "residual_surrogate" if sc == "margin" else "flip"}
        for nm, role in (("residual", ROLE_RESIDUAL), ("flip", ROLE_FLIP)):
            ga, oa = R.get(f"{nm}_grader_accept"), R.get(f"{nm}_oracle_accept")
            if ga is None or oa is None:
                fl[f"{nm}_surrogate"] = {**NOT_SUPPLIED, "role": role}
                continue
            gm, om = ga[m], oa[m]
            if gm.dtype == object or om.dtype == object:     # None marks rows whose floor was not run
                none = np.array([x is None for x in gm.tolist()]) | np.array([x is None for x in om.tolist()])
                if none.all():
                    fl[f"{nm}_surrogate"] = {"status": "not run for this group", "role": role}
                    continue
                if none.any():
                    raise ValueError(f"({a}, {sc}, B={b}): the {nm} floor is missing on {int(none.sum())} of "
                                     f"{none.size} rows")
                gm, om = np.array(gm.tolist()), np.array(om.tolist())
            sg, so = S._bool(gm, nm), S._bool(om, nm)
            fl[f"{nm}_surrogate"] = {"role": role, "hackability": _est(S.hackability(sg, so, cl, **kw)),
                                     "excess": _est(S.excess(hacked, (sg & ~so).astype(float), cl, **kw))}
        if a == "random_shooting" and sc == "verdict":
            cf = (_closed_form(b, ids, cl, hacked, B_, accept_threshold, kw) if B_ is not None
                  else {"status": "needs the behaviour table"})
            fl["flip_closed_form"] = {"role": ROLE_FLIP, **cf}
            verdict_curve.append({**head, "hackability": _est(hk), "flip_closed_form": cf})
        else:
            fl["flip_closed_form"] = {"status": "computed beside verdict-scored random shooting only", "role": ROLE_FLIP}
        floors.append(fl)
        p_sel = np.asarray(R["grader_p"], dtype=np.float64)[m]
        selected_cal.append({**head, "brier": S.brier_decomposition(p_sel, o, cl, **kw).as_dict(),
                             "log_score_bits": _est(S.log_score(p_sel, o, cl, grader_k, **kw))})
        if "grader_score" in R and "oracle_margin" in R:
            optimism.append({**head, "mean_grader_score_minus_oracle_margin": _est(
                S.excess(np.asarray(R["grader_score"], float)[m], np.asarray(R["oracle_margin"], float)[m], cl, **kw))})

    card: dict[str, Any] = {
        "schema": CARD_SCHEMA,
        "meta": dict(meta),
        "instrument": {
            "package": "hpr_dream", "version": __version__,
            "bootstrap": {"method": "cluster bootstrap, percentile interval" + (" and BCa" if bca else ""),
                          "n_boot": int(n_boot), "level": float(level), "seed": int(seed),
                          "zero_hacked": S.ZERO_BOUND_METHOD},
            "grader_k": int(grader_k), "accept_threshold": float(accept_threshold),
            "unit": "the attacker's selected plan per (instance, attacker, scoring, budget, attacker seed)",
            "matched_floors": {"margin": "residual_surrogate", "verdict": "flip (surrogate; closed form for random shooting)"},
        },
        "hackability_curve": curve,
        "verdict_scored_curve": verdict_curve if verdict_curve else NOT_SUPPLIED,
        "conditional_reject": cond,
        "unlucky_share": unlucky if seeds is not None else NOT_SUPPLIED,
        "noise_floors": floors,
        "optimism": optimism if optimism else NOT_SUPPLIED,
        "calibration": {"selected": selected_cal},
    }

    # behaviour-distribution sections
    if B_ is not None:
        bp = np.asarray(B_["grader_p"], dtype=np.float64)
        bg = bp >= accept_threshold
        bo = S._bool(B_["oracle_accept"], "behaviour oracle_accept")
        bc = B_["cluster"]
        card["false_rejection"] = {
            "on": "behaviour plans the oracle accepts", "n_plans": int(bo.sum()),
            "false_rejection": _est(S.false_rejection(bg[bo], bc[bo], **kw)) if bo.any() else NOT_SUPPLIED}
        card["calibration"]["behaviour"] = {
            "brier": S.brier_decomposition(bp, bo, bc, **kw).as_dict(),
            "log_score_bits": _est(S.log_score(bp, bo, bc, grader_k, **kw))}
        card["flip_rates"] = {
            "fp": _est(S._ratio(bg & ~bo, ~bo, bc, n_boot, seed, level, bca)),
            "fn": _est(S._ratio(~bg & bo, bo, bc, n_boot, seed, level, bca)),
            "base_rate": _est(S._ratio(bo, np.ones(bo.size), bc, n_boot, seed, level, bca)),
            "on": "behaviour plans, pooled"}
    else:
        card["false_rejection"] = NOT_SUPPLIED
        card["calibration"]["behaviour"] = NOT_SUPPLIED
        card["flip_rates"] = NOT_SUPPLIED

    C_ = _table(candidates, ("cluster", "grader_scores", "oracle_scores"), (), "candidates")
    card["dream_overfit_probability"] = (
        {"dream_overfit_probability": _est(S.dream_overfit_probability(C_["grader_scores"], C_["oracle_scores"], C_["cluster"], **kw)),
         "n_instances": int(len(C_["cluster"]))} if C_ is not None else NOT_SUPPLIED)

    D_ = _table(detector, ("cluster", "score", "label"), ("name",), "detector")
    if D_ is not None:
        names = D_["name"].astype(str) if "name" in D_ else np.full(len(D_["score"]), "detector")
        card["detector_auc"] = [
            {"name": nm, "n": int((names == nm).sum()),
             "auc": _est(S.auc(D_["score"][names == nm], D_["label"][names == nm], D_["cluster"][names == nm], **kw))}
            for nm in sorted(set(names.tolist()))]
    else:
        card["detector_auc"] = NOT_SUPPLIED

    # counts: only what the inputs show
    n_seeds_other = int(seeds.shape[1]) if seeds is not None else 0
    n_beh = int(len(B_["instance"])) if B_ is not None else 0
    n_cand = int(sum(np.asarray(x).size for x in C_["grader_scores"])) if C_ is not None else 0
    card["counts"] = {
        "records": int(n),
        "instances": int(len(np.unique(inst_ids))),
        "clusters": int(len(np.unique(clus))),
        "attackers": sorted(set(attackers.tolist())),
        "scorings": sorted(set(scoring.tolist())),
        "budgets": sorted(set(int(x) for x in budgets.tolist())),
        "groups": len(groups),
        "behaviour_plans": n_beh,
        "behaviour_instances": int(len(np.unique(B_["instance"]))) if B_ is not None else 0,
        "candidate_plans": n_cand,
        "grader_plan_evaluations": {
            "attack_search": int(np.sum(R["n_scored"])) if "n_scored" in R else None,
            "selected_plans_rescored": int(n),
            "behaviour_plans": n_beh,
            "candidate_plans": n_cand,
        },
        "oracle_plan_evaluations": {
            "selected_primary_seed": int(n),
            "selected_other_seeds": int(n * n_seeds_other),
            "noise_floor_attacks": int(np.sum(R["n_floor_oracle_evals"])) if "n_floor_oracle_evals" in R else None,
            "behaviour_plans": n_beh,
            "candidate_plans": n_cand,
        },
    }
    return card


def _closed_form(B, ids, cl, hacked, Bt, thr, kw) -> dict:
    """Flip closed-form floor and paired excess for one verdict-scored random-shooting group."""
    uniq, codes = np.unique(ids, return_inverse=True)
    codes = codes.reshape(-1)
    h_inst = np.bincount(codes, weights=hacked) / np.bincount(codes)
    cl_inst = np.empty(uniq.size, dtype=object)
    cl_inst[codes] = list(cl)
    beh_ids = Bt["instance"]
    pos = np.clip(np.searchsorted(uniq, beh_ids), 0, uniq.size - 1)
    keep = uniq[pos] == beh_ids
    if not keep.any():
        return {"status": "no behaviour plans for these instances"}
    have = np.bincount(pos[keep], minlength=uniq.size)
    if (have == 0).any():
        return {"status": f"{int((have == 0).sum())} instances lack behaviour plans"}
    bg = np.asarray(Bt["grader_p"], dtype=np.float64)[keep] >= thr
    bo = S._bool(Bt["oracle_accept"], "behaviour oracle_accept")[keep]
    ff = S.flip_floor(B, bg, bo, pos[keep], np.asarray(cl_inst.tolist()), hacked=h_inst, **kw)
    return {"floor": _est(ff.floor), "floor_pooled_base_rate": _est(ff.floor_pooled_base_rate),
            "excess": _est(ff.excess), "fp": _est(ff.fp), "fn": _est(ff.fn), "base_rate": _est(ff.base_rate),
            "n_behaviour_plans": ff.n_behaviour_plans,
            "definition": "mean over instances of (1-(1-a)^B)(1-pi_i)fp/a, a = pi_i(1-fn)+(1-pi_i)fp; "
                          "fp, fn pooled over behaviour plans, pi_i per instance"}


def _clean(x):
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, np.ndarray):
        return [_clean(v) for v in x.tolist()]
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        x = float(x)
        return x if math.isfinite(x) else None
    if isinstance(x, date):
        return x.isoformat()
    return x


def write_card(card: dict, path) -> str:
    """Write the card as JSON (NaN and infinities become null). Returns the path written."""
    path = os.fspath(path)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(_clean(card), f, indent=2, allow_nan=False, sort_keys=False)
        f.write("\n")
    os.replace(tmp, path)
    return path
