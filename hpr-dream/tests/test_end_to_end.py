"""End-to-end checks (specification 6.5 as amended by the coordinator) on synthetic graders with
known truth, in two grader settings (A: per-plan error + per-sample noise; B: all K samples equal).

Each check prints its table (visible with ``pytest -s``).
Check 1: (i) verdict-scored random shooting matches the flip closed form within its interval at
every B; (ii) margin-scored random shooting has zero excess over the residual surrogate within
interval at every B. Check 2: CEM finds the hole (hackability rises with B; excess over both
floors positive at B = 1,000). Check 3: budget accounting. Pool diagnostic: unbiased grader with
per-plan error sd 2.0 at B = 1,000, residual floor from a 1,000-row per-instance pool and from the
pooled option over 100-row pools; a 100-row per-instance pool is refused.
"""

from __future__ import annotations

import functools

import pytest

import e2e_checks as E


@functools.lru_cache(maxsize=None)
def check1(setting):
    text, res = E.run_check1(setting=setting)
    print("\n" + text)
    return res


@functools.lru_cache(maxsize=None)
def check2(setting):
    text, res = E.run_check2(setting=setting, build_card=setting == "A")
    print("\n" + text)
    return res


@pytest.mark.parametrize("setting", ["A", "B"])
def test_check1_verdict_scored_random_shooting_matches_closed_form(setting):
    res = check1(setting)
    for B, v in res["verdicts"].items():
        assert v["verdict_closed_form_in_ci"], B
    assert res["crit_i"]


@pytest.mark.parametrize("setting", ["A", "B"])
def test_check1_margin_scored_excess_over_residual_is_zero(setting):
    res = check1(setting)
    for B, v in res["verdicts"].items():
        assert v["excess_over_residual_ci_has_zero"], B
    assert res["crit_ii"]


@pytest.mark.parametrize("setting", ["A", "B"])
def test_check1_flip_surrogate_attack_matches_closed_form(setting):
    for B, v in check1(setting)["verdicts"].items():
        assert v["flip_surrogate_matches_closed_form"], B


@pytest.mark.parametrize("setting", ["A", "B"])
def test_check2_cem_finds_the_hole(setting):
    res = check2(setting)
    assert res["rises"]
    assert res["pos_r"]
    assert res["pos_f"]


def test_check2_card_matches_the_tables():
    res = check2("A")
    card = res["card"]
    for (a, sc, B), o in res["out"].items():
        e = next(x for x in card["hackability_curve"] if (x["attacker"], x["scoring"], x["budget"]) == (a, sc, B))
        assert e["hackability"]["value"] == o["h"].value
        assert (e["hackability"]["lo"], e["hackability"]["hi"]) == (o["h"].lo, o["h"].hi)
        if sc == "verdict":
            v = next(x for x in card["verdict_scored_curve"] if x["budget"] == B)
            assert v["flip_closed_form"]["floor"]["value"] == o["ff"].floor.value
    assert card["counts"]["records"] == 3 * 4 * 200


def test_check3_budget_accounting():
    text, res = E.run_check3()
    print("\n" + text)
    assert res["ok"]
    assert len(res["results"]) == 30


def test_pool_diagnostic():
    text, res = E.run_pool_diagnostic()
    print("\n" + text)
    for sample_sd in (0.0, 0.5):
        assert res[(sample_sd, "per-instance, 1000 rows")]["zero_in_ci"]
        assert res[(sample_sd, "pooled, 200 instances x 100 rows")]["zero_in_ci"]
        assert res[(sample_sd, "per-instance, 100 rows")]["refused"] == 200
