"""The card: every number equals the statistic computed directly; inputs are validated; JSON is clean."""

from __future__ import annotations

import json
import math

import numpy as np
import pytest

from hpr_dream import stats as S
from hpr_dream.card import CARD_SCHEMA, ROLE_FLIP, ROLE_RESIDUAL, build_card, write_card

META = {"audited": "synthetic grader", "code_version": "test", "date": "2026-11-09", "revisit_date": "2027-05-09"}
GROUPS = (("random_shooting", "margin"), ("cem", "margin"), ("random_shooting", "verdict"))


def make_tables(seed=0, n_inst=24, seeds=2):
    rng = np.random.default_rng(seed)
    cl_of = np.repeat(np.arange(8), 3)
    rec = {k: [] for k in ("instance", "cluster", "attacker", "scoring", "budget", "attacker_seed", "plan_id", "grader_p",
                           "oracle_accept", "oracle_accept_seeds", "flip_grader_accept", "flip_oracle_accept",
                           "residual_grader_accept", "residual_oracle_accept", "n_scored", "n_floor_oracle_evals",
                           "grader_score", "oracle_margin")}
    for a, sc in GROUPS:
        for B in (1, 10):
            for i in range(n_inst):
                for s in range(seeds):
                    rec["instance"].append(i)
                    rec["cluster"].append(f"fam{cl_of[i]}")
                    rec["attacker"].append(a)
                    rec["scoring"].append(sc)
                    rec["budget"].append(B)
                    rec["attacker_seed"].append(s)
                    rec["plan_id"].append(f"{a}-{sc}-{B}-{i}-{s}")
                    rec["grader_p"].append(rng.integers(0, 9) / 8)
                    rec["oracle_accept"].append(bool(rng.random() < 0.5))
                    rec["oracle_accept_seeds"].append(rng.random(3) < 0.5)
                    for k in ("flip_grader_accept", "flip_oracle_accept", "residual_grader_accept", "residual_oracle_accept"):
                        rec[k].append(bool(rng.random() < 0.5))
                    rec["n_scored"].append(B)
                    rec["n_floor_oracle_evals"].append(2 * B)
                    rec["grader_score"].append(rng.normal())
                    rec["oracle_margin"].append(rng.normal())
    rec = {k: np.array(v) for k, v in rec.items()}
    beh_inst = np.repeat(np.arange(n_inst), 10)
    beh = {"instance": beh_inst, "cluster": np.array([f"fam{c}" for c in cl_of[beh_inst]]),
           "grader_p": rng.integers(0, 9, size=beh_inst.size) / 8, "oracle_accept": rng.random(beh_inst.size) < 0.4}
    cand = {"cluster": np.array([f"fam{c}" for c in cl_of]), "grader_scores": rng.normal(size=(n_inst, 6)),
            "oracle_scores": rng.normal(size=(n_inst, 6))}
    det = {"cluster": rec["cluster"], "score": rng.normal(size=rec["cluster"].size),
           "label": rng.random(rec["cluster"].size) < 0.3}
    return rec, beh, cand, det


def pick(entries, a, sc, b):
    return next(e for e in entries if (e["attacker"], e["scoring"], e["budget"]) == (a, sc, b))


def test_card_numbers_equal_direct_statistics(tmp_path):
    rec, beh, cand, det = make_tables()
    card = build_card(rec, META, behaviour=beh, candidates=cand, detector=det)
    assert card["schema"] == CARD_SCHEMA and card["meta"] == META
    m = (rec["attacker"] == "cem") & (rec["budget"] == 10)
    g, o, cl = rec["grader_p"][m] >= 0.5, rec["oracle_accept"][m], rec["cluster"][m]
    entry = pick(card["hackability_curve"], "cem", "margin", 10)
    assert entry["hackability"] == S.hackability(g, o, cl).as_dict()
    assert entry["n_instances"] == 24 and entry["n_rows"] == 48 and entry["seeds_per_instance"] == 2
    assert pick(card["conditional_reject"], "cem", "margin", 10)["conditional_reject"] == S.conditional_reject(g, o, cl).as_dict()
    un = pick(card["unlucky_share"], "cem", "margin", 10)
    assert un["unlucky_share"] == S.unlucky_share(g, o, rec["oracle_accept_seeds"][m], cl).as_dict()
    fl = pick(card["noise_floors"], "cem", "margin", 10)
    assert fl["matched_floor"] == "residual_surrogate"
    assert fl["residual_surrogate"]["role"] == ROLE_RESIDUAL and fl["flip_surrogate"]["role"] == ROLE_FLIP
    fh = rec["flip_grader_accept"][m] & ~rec["flip_oracle_accept"][m]
    assert fl["flip_surrogate"]["excess"] == S.excess((g & ~o).astype(float), fh.astype(float), cl).as_dict()
    rh = rec["residual_grader_accept"][m] & ~rec["residual_oracle_accept"][m]
    assert fl["residual_surrogate"]["excess"] == S.excess((g & ~o).astype(float), rh.astype(float), cl).as_dict()
    assert "status" in fl["flip_closed_form"]  # closed form only beside verdict-scored random shooting
    assert "status" in pick(card["noise_floors"], "random_shooting", "margin", 10)["flip_closed_form"]
    sel = pick(card["calibration"]["selected"], "cem", "margin", 10)
    assert sel["brier"]["brier"] == S.brier_decomposition(rec["grader_p"][m], o, cl).brier.as_dict()
    assert sel["log_score_bits"] == S.log_score(rec["grader_p"][m], o, cl, 8).as_dict()
    bo = beh["oracle_accept"]
    assert card["false_rejection"]["false_rejection"] == S.false_rejection(
        (beh["grader_p"] >= 0.5)[bo], beh["cluster"][bo]).as_dict()
    assert card["dream_overfit_probability"]["dream_overfit_probability"] == S.dream_overfit_probability(
        cand["grader_scores"], cand["oracle_scores"], cand["cluster"]).as_dict()
    assert card["detector_auc"][0]["auc"] == S.auc(det["score"], det["label"], det["cluster"]).as_dict()
    c = card["counts"]
    assert c["records"] == 288 and c["instances"] == 24 and c["clusters"] == 8 and c["groups"] == 6
    assert c["scorings"] == ["margin", "verdict"]
    assert c["grader_plan_evaluations"]["attack_search"] == 3 * 24 * 2 * (1 + 10)
    assert c["oracle_plan_evaluations"]["selected_other_seeds"] == 288 * 3
    assert c["oracle_plan_evaluations"]["noise_floor_attacks"] == 3 * 24 * 2 * (2 + 20)
    path = write_card(card, tmp_path / "card.json")
    back = json.loads(open(path).read())
    assert back["counts"]["records"] == 288


def test_verdict_scored_curve_carries_the_closed_form():
    rec, beh, _, _ = make_tables(seeds=1)
    card = build_card(rec, META, behaviour=beh)
    m = (rec["attacker"] == "random_shooting") & (rec["scoring"] == "verdict") & (rec["budget"] == 10)
    hacked = ((rec["grader_p"][m] >= 0.5) & ~rec["oracle_accept"][m]).astype(float)
    cl_inst = np.array([f"fam{c}" for c in np.repeat(np.arange(8), 3)])
    ff = S.flip_floor(10, beh["grader_p"] >= 0.5, beh["oracle_accept"], beh["instance"], cl_inst, hacked=hacked)
    vc = next(e for e in card["verdict_scored_curve"] if e["budget"] == 10)
    assert vc["flip_closed_form"]["floor"] == ff.floor.as_dict()
    assert vc["flip_closed_form"]["excess"] == ff.excess.as_dict()
    fl = pick(card["noise_floors"], "random_shooting", "verdict", 10)
    assert fl["matched_floor"] == "flip" and fl["flip_closed_form"]["floor"] == ff.floor.as_dict()
    assert fl["flip_closed_form"]["role"] == ROLE_FLIP
    # without verdict-scored rows the curve is marked as not supplied
    keep = rec["scoring"] == "margin"
    card2 = build_card({k: v[keep] for k, v in rec.items()}, META, behaviour=beh)
    assert card2["verdict_scored_curve"] == {"status": "not supplied"}


def test_card_bca_option():
    rec, beh, _, _ = make_tables(seeds=1)
    a = build_card(rec, META, behaviour=beh)
    b = build_card(rec, META, behaviour=beh, bca=True)
    ea, eb = pick(a["hackability_curve"], "cem", "margin", 10)["hackability"], pick(b["hackability_curve"], "cem", "margin", 10)["hackability"]
    assert (ea["lo"], ea["hi"]) == (eb["lo"], eb["hi"])
    assert math.isnan(ea["bca_lo"]) and math.isfinite(eb["bca_lo"]) and math.isfinite(eb["bca_hi"])
    assert "BCa" in b["instrument"]["bootstrap"]["method"]


def test_card_marks_missing_sections_and_validates():
    rec, _, _, _ = make_tables()
    minimal = {k: rec[k] for k in ("instance", "cluster", "attacker", "budget", "attacker_seed", "plan_id",
                                   "grader_p", "oracle_accept")}
    minimal = {k: v[rec["scoring"] == "margin"] for k, v in minimal.items()}  # no scoring column: all margin
    card = build_card(minimal, META)
    for k in ("unlucky_share", "false_rejection", "dream_overfit_probability", "detector_auc", "flip_rates", "optimism",
              "verdict_scored_curve"):
        assert card[k] == {"status": "not supplied"}, k
    assert card["noise_floors"][0]["flip_surrogate"]["status"] == "not supplied"
    assert card["counts"]["grader_plan_evaluations"]["attack_search"] is None
    with pytest.raises(ValueError):
        build_card(minimal, {"audited": "x"})
    bad = dict(minimal)
    bad["cluster"] = minimal["cluster"].copy()
    bad["cluster"][0] = "elsewhere"
    with pytest.raises(ValueError):
        build_card(bad, META)  # an instance in two clusters
    drop = {k: v[1:] for k, v in minimal.items()}
    with pytest.raises(ValueError):
        build_card(drop, META)  # unequal attacker seeds per instance
    with pytest.raises(ValueError):
        build_card({k: v for k, v in minimal.items() if k != "grader_p"}, META)
    with pytest.raises(ValueError):
        build_card({**minimal, "scoring": np.full(len(minimal["instance"]), "logit")}, META)


def test_floor_not_run_for_some_groups():
    """A floor column holding None on every row of a group: that group's floor is 'not run'; the others are as if
    the column had only their rows; None on part of a group is refused."""
    rec, beh, _, _ = make_tables()
    full = build_card(rec, META, behaviour=beh)
    part = dict(rec)
    margin = rec["scoring"] == "margin"
    for k in ("flip_grader_accept", "flip_oracle_accept"):
        part[k] = np.array([None if m else bool(x) for m, x in zip(margin, rec[k])], dtype=object)
    card = build_card(part, META, behaviour=beh)
    for f, g in zip(card["noise_floors"], full["noise_floors"]):
        if f["scoring"] == "margin":
            assert f["flip_surrogate"] == {"status": "not run for this group", "role": ROLE_FLIP}
        else:
            assert f["flip_surrogate"] == g["flip_surrogate"]
        assert f["residual_surrogate"] == g["residual_surrogate"]
    bad = dict(part)
    bad["flip_grader_accept"] = part["flip_grader_accept"].copy()
    bad["flip_grader_accept"][np.flatnonzero(~margin)[0]] = None
    with pytest.raises(ValueError):
        build_card(bad, META, behaviour=beh)


def test_write_card_turns_nan_into_null(tmp_path):
    p = write_card({"x": float("nan"), "y": np.float64(1.5), "z": np.arange(3), "w": (np.bool_(True),)}, tmp_path / "c.json")
    assert json.loads(open(p).read()) == {"x": None, "y": 1.5, "z": [0, 1, 2], "w": [True]}
