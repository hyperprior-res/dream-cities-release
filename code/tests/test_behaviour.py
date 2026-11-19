"""Behaviour mix (dc.behaviour).

pytest code/tests/test_behaviour.py; run directly for the acceptance printout:

    python code/tests/test_behaviour.py [--workers 16]

(4) 200 behaviour trajectories of 24 months across policies: the replay of the returned action log
reproduces the final full-state hash; (6) tool calls and nominal cost per month and the share of
calls the engine refuses, by policy type, under the behaviour mix; (7) engine throughput in
city-months a second per core on the family start states under the behaviour mix.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))

from dc.behaviour import (  # noqa: E402
    BEHAVIOUR_MIX, BUILDER_STYLES, COVERAGE_STYLES, P_PERTURB, PERTURBATIONS, HeldBudget, LatticeBuilder, Perturbed,
    make_policy, rollout_behaviour, sample_behaviour, sample_coverage_behaviour, sample_listed_behaviour,
)
from dc.engine import Engine  # noqa: E402
from dc.grammar import MACRO_KINDS, compile_plan, is_valid_plan, n_calls_batch, nominal_cost_batch  # noqa: E402
from dc.oracle import replay  # noqa: E402

CITIES = ROOT / "data" / "cities"
ALL_LABELS = [l for l, _ in BEHAVIOUR_MIX] + [l + "+perturb" for l, _ in BEHAVIOUR_MIX]


def _check_replay(eng, cty, label, months, seed, disasters, rng_seed):
    pol = make_policy(label)
    plan, rep = rollout_behaviour(eng, cty, pol, months, seed, disasters, np.random.default_rng(rng_seed),
                                  record="scalars", want_hash=True)
    acts, forced = compile_plan(plan)
    r2 = replay(eng, cty, acts, seed, disasters=disasters, forced=forced, want_hash=True)
    return plan, rep, r2


# ----------------------------------------------------------------------------------------------
def test_mix_table():
    w = np.array([p for _, p in BEHAVIOUR_MIX])
    assert abs(w.sum() - 1) < 1e-9 and (w > 0).all()
    assert sum(1 for l, _ in BEHAVIOUR_MIX if l.startswith("builder/")) >= 5
    for l in ALL_LABELS:
        assert make_policy(l).label == l
    rng = np.random.default_rng(0)
    labels = [sample_behaviour(rng)[1] for _ in range(4000)]
    share = np.mean([l.endswith("+perturb") for l in labels])
    assert abs(share - P_PERTURB) < 0.04
    a = [sample_behaviour(np.random.default_rng(7))[1] for _ in range(3)]
    assert len(set(a)) == 1


def test_every_policy_replays_exactly():
    eng = Engine()
    try:
        for k, label in enumerate(ALL_LABELS):
            cty = CITIES / ["linecity.cty", "med_isle.cty", "scenario_dullsville.cty", "wetcity.cty"][k % 4]
            plan, rep, r2 = _check_replay(eng, cty, label, 12, 100 + k, k % 3 == 0, k)
            assert plan.shape == (12, 25) and plan.dtype == np.int16 and is_valid_plan(plan)
            assert np.array_equal(rep.hashes, r2.hashes), label
            assert np.array_equal(rep.scalars, r2.scalars), label
            assert all(np.array_equal(a, b) for a, b in zip(rep.tool_ok, r2.tool_ok))
    finally:
        eng.close()


def test_full_record_matches_replay_states():
    eng = Engine()
    try:
        cty = CITIES / "bruce.cty"
        plan, rep = rollout_behaviour(eng, cty, make_policy("random/sprinkle+perturb"), 8, 3, False,
                                      np.random.default_rng(3), record="full")
        acts, forced = compile_plan(plan)
        r2 = replay(eng, cty, acts, 3, forced=forced, record="full")
        assert len(rep.states) == 9
        for a, b in zip(rep.states, r2.states):
            assert np.array_equal(a.tiles, b.tiles) and np.array_equal(a.half, b.half)
            assert np.array_equal(a.power, b.power) and np.array_equal(a.eighth, b.eighth)
            assert np.array_equal(a.scalars, b.scalars)
    finally:
        eng.close()


def test_builders_grow_on_generated_terrain():
    """Every builder style grows a city from bare terrain; the fast styles pass 20,000 in ten years."""
    eng = Engine()
    try:
        with tempfile.TemporaryDirectory() as td:
            ter = Path(td) / "t.cty"
            eng.new_terrain(2, 100_000)
            eng.save_city(ter)
            pops = {}
            for style in BUILDER_STYLES:
                plan, rep = rollout_behaviour(eng, ter, LatticeBuilder(BUILDER_STYLES[style]), 120, 1, False,
                                              np.random.default_rng(5), record="scalars")
                pops[style] = int(rep.scalars[-1, 5])
                assert rep.scalars[-1, 15] >= 0.9 * (rep.scalars[-1, 15] + rep.scalars[-1, 16]), style  # powered
                assert (rep.scalars[:, 0] >= 0).all(), style   # never in debt
            assert min(pops.values()) > 2000, pops
            assert pops["boom"] > 20000 and pops["transit"] > 20000, pops
    finally:
        eng.close()


def test_builder_is_deterministic():
    eng = Engine()
    try:
        cty = CITIES / "scenario_dullsville.cty"
        a, _ = rollout_behaviour(eng, cty, make_policy("builder/grid"), 24, 9, False, np.random.default_rng(11))
        b, _ = rollout_behaviour(eng, cty, make_policy("builder/grid"), 24, 9, False, np.random.default_rng(11))
        assert np.array_equal(a, b)
        assert (n_calls_batch(a) > 0).any()
    finally:
        eng.close()


def test_perturbations_fire():
    eng = Engine()
    try:
        seen_bulldoze = seen_disaster = seen_tax = 0
        for s in range(6):
            pol = Perturbed(make_policy("noop"), rate_per_24=(3, 3))
            plan, rep = rollout_behaviour(eng, CITIES / "radial.cty", pol, 24, s, False, np.random.default_rng(s),
                                          record="scalars")
            seen_bulldoze += int((plan[:, 5::5] == MACRO_KINDS["BULLDOZE"]).sum())
            seen_disaster += int((plan[:, 4] > 0).sum())
            seen_tax += int((plan[:, 0] != plan[0, 0]).sum())
        assert seen_bulldoze > 0 and seen_disaster > 0 and seen_tax > 0
        assert set(PERTURBATIONS) == {"cut_wire", "cut_road", "remove_plant", "tax_shock", "funding_cut", "disaster"}
    finally:
        eng.close()


def test_coverage_mix_draws():
    """The coverage mix: seven builder styles uniform, tax uniform on 0..20, each funding level uniform on 0..4,
    drawn independently; deterministic in the generator; no perturbation wrapper."""
    assert COVERAGE_STYLES == tuple(sorted(BUILDER_STYLES)) and len(COVERAGE_STYLES) == 7
    rng = np.random.default_rng(0)
    draws = [sample_coverage_behaviour(rng) for _ in range(7000)]
    styles = np.array([COVERAGE_STYLES.index(p.base.style.name) for p, _ in draws])
    sets = np.array([p.setting for p, _ in draws])
    assert all(isinstance(p, HeldBudget) and isinstance(p.base, LatticeBuilder) for p, _ in draws)
    assert all(l == f"builder/{p.base.style.name}+held" == p.label for p, l in draws)
    assert set(sets[:, 0].tolist()) == set(range(21)) and all(set(sets[:, k].tolist()) == set(range(5)) for k in (1, 2, 3))
    for col, n in ((styles, 7), (sets[:, 0], 21), (sets[:, 1], 5), (sets[:, 2], 5), (sets[:, 3], 5)):
        share = np.bincount(col, minlength=n) / len(col)
        assert np.abs(share - 1.0 / n).max() < 0.02
    a = [(p.setting, l) for p, l in (sample_coverage_behaviour(np.random.default_rng(5)) for _ in range(3))]
    assert len(set(a)) == 1
    for bad in ((21, 4, 4, 4), (0, 5, 0, 0), (0, 0, -1, 0), (1, 2, 3)):
        try:
            HeldBudget(make_policy("noop"), bad)
        except ValueError:
            continue
        raise AssertionError(f"{bad} accepted")


def test_held_budget_builder_replays_and_holds():
    """A builder under a held setting: every month carries the setting, no forced disaster, it still builds,
    and the replay of its action log reproduces the trajectory exactly."""
    eng = Engine()
    try:
        for k, (style, setting) in enumerate((("grid", (0, 0, 0, 0)), ("boom", (20, 4, 0, 2)), ("frugal", (3, 1, 4, 0)))):
            cty = CITIES / ["scenario_dullsville.cty", "linecity.cty", "radial.cty"][k]
            pol = HeldBudget(LatticeBuilder(BUILDER_STYLES[style]), setting)
            plan, rep = rollout_behaviour(eng, cty, pol, 12, 40 + k, False, np.random.default_rng(k), record="scalars",
                                          want_hash=True)
            assert is_valid_plan(plan) and (plan[:, 0:4] == np.array(setting)).all() and (plan[:, 4] == 0).all()
            assert (n_calls_batch(plan) > 0).any(), style
            acts, forced = compile_plan(plan)
            r2 = replay(eng, cty, acts, 40 + k, disasters=False, forced=forced, want_hash=True)
            assert np.array_equal(rep.hashes, r2.hashes) and np.array_equal(rep.scalars, r2.scalars)
            # the engine took the setting: tax rate scalar equals the held tax after month 0
            from dc.engine import SC_TAX
            assert (rep.scalars[1:, SC_TAX] == setting[0]).all()
            # same builder, same generator, no wrapper: the macros of month 0 are the same calls
            plan0, _ = rollout_behaviour(eng, cty, LatticeBuilder(BUILDER_STYLES[style]), 1, 40 + k, False,
                                         np.random.default_rng(k), record="scalars")
            assert np.array_equal(plan0[0, 5:], plan[0, 5:])
    finally:
        eng.close()


# ----------------------------------------------------------------------------------------------
# Acceptance (needs data/families.json from code/scripts/build_families.py)
# ----------------------------------------------------------------------------------------------
def _hash_task(t):
    eng = Engine()
    plan, rep, r2 = _check_replay(eng, t["cty"], t["label"], 24, t["seed"], t["disasters"], t["rng"])
    eng.close()
    return {"label": t["label"], "same": bool(rep.hashes[-1] == r2.hashes[-1]),
            "same_all": bool(np.array_equal(rep.hashes, r2.hashes))}


def _mix_task(t):
    """Behaviour-mix trajectories from training starts: per-month stats plus timing."""
    from dc.families import starts
    rng = np.random.default_rng([20261109, 7, t["k"]])
    st = starts("train")
    fams = sorted({f for _, f, _ in st})
    eng = Engine()
    out = []
    t_roll = t_replay = 0.0
    months_total = 0
    for j in range(t["n"]):
        fam = fams[int(rng.integers(len(fams)))]
        cands = [p for _, f, p in st if f == fam]
        cty = cands[int(rng.integers(len(cands)))]
        pol, label = sample_behaviour(rng)
        disasters = bool(rng.random() < 0.15)
        seed = int(rng.integers(1, 2 ** 31 - 1))
        t0 = time.perf_counter()
        plan, rep = rollout_behaviour(eng, cty, pol, t["months"], seed, disasters, rng, record="full")
        t1 = time.perf_counter()
        acts, forced = compile_plan(plan)
        replay(eng, cty, acts, seed, disasters=disasters, forced=forced, record="scalars")
        t2 = time.perf_counter()
        t_roll += t1 - t0
        t_replay += t2 - t1
        months_total += t["months"]
        ok = rep.tool_ok
        out.append({"label": label, "calls": n_calls_batch(plan).tolist(), "cost": nominal_cost_batch(plan).tolist(),
                    "refused": [int((o != 1).sum()) for o in ok], "charged": rep.build_cost.tolist(),
                    "pop0": int(rep.scalars[0, 5])})
    eng.close()
    return {"traj": out, "months": months_total, "t_roll": t_roll, "t_replay": t_replay}


def acceptance(workers: int) -> None:
    from dc.families import starts
    st = starts("train") + starts("heldout")
    ctx = mp.get_context("spawn")

    print("B1 acceptance 4: 200 behaviour trajectories x 24 months, replay of the returned action log")
    rng = np.random.default_rng(424242)
    tasks = []
    for k in range(200):
        label = ALL_LABELS[k % len(ALL_LABELS)]
        _, _, cty = st[int(rng.integers(len(st)))]
        tasks.append({"cty": str(cty), "label": label, "seed": int(rng.integers(1, 2 ** 31 - 1)),
                      "disasters": bool(k % 4 == 3), "rng": int(rng.integers(1, 2 ** 31 - 1))})
    with ctx.Pool(workers) as pool:
        res = pool.map(_hash_task, tasks)
    same = sum(r["same"] for r in res)
    same_all = sum(r["same_all"] for r in res)
    print(f"policies: {len(ALL_LABELS)} labels x {200 // len(ALL_LABELS)} trajectories; starts drawn from "
          f"{len(st)} family start states; disasters on in {sum(t['disasters'] for t in tasks)}")
    print(f"final full-state hash reproduced: {same} / {len(res)}; identical at every month: {same_all} / {len(res)}")
    print()

    n_traj, months = 800, 48
    per = n_traj // workers
    with ctx.Pool(workers) as pool:
        res = pool.map(_mix_task, [{"k": k, "n": per, "months": months} for k in range(workers)])
    traj = [x for r in res for x in r["traj"]]
    print(f"B1 acceptance 6: behaviour mix on training family starts: {len(traj)} trajectories x {months} months "
          f"(policy by sample_behaviour, start uniform over families then variants, disasters on in 15 per cent)")
    groups = defaultdict(list)
    for x in traj:
        base = x["label"].replace("+perturb", "")
        typ = base.split("/")[0] if base.startswith("builder/") else base
        groups[typ].append(x)
        if base.startswith("builder/"):
            groups[base].append(x)
        groups["(perturbed, any)" if x["label"].endswith("+perturb") else "(unperturbed, any)"].append(x)
        groups["ALL (mix)"].append(x)
    order = ["builder"] + sorted(k for k in groups if k.startswith("builder/")) + \
        ["random/uniform", "random/sprinkle", "noop", "budget_sweep", "(unperturbed, any)", "(perturbed, any)", "ALL (mix)"]
    print(f"{'policy type':22s} {'traj':>5s} {'calls/mo mean':>13s} {'p5':>4s} {'p95':>5s} {'nominal $/mo mean':>17s} "
          f"{'p5':>5s} {'p95':>7s} {'charged $/mo':>12s} {'refused':>8s}")
    for k in order:
        g = groups.get(k, [])
        if not g:
            continue
        calls = np.concatenate([x["calls"] for x in g])
        cost = np.concatenate([x["cost"] for x in g])
        charged = np.concatenate([x["charged"] for x in g])
        ref = np.concatenate([x["refused"] for x in g])
        share = ref.sum() / max(1, calls.sum())
        print(f"{k:22s} {len(g):5d} {calls.mean():13.2f} {np.percentile(calls, 5):4.0f} {np.percentile(calls, 95):5.0f} "
              f"{cost.mean():17.0f} {np.percentile(cost, 5):5.0f} {np.percentile(cost, 95):7.0f} {charged.mean():12.0f} "
              f"{share:8.3f}")
    print()
    m = sum(r["months"] for r in res)
    tr = np.array([r["months"] / r["t_roll"] for r in res])
    tp = np.array([r["months"] / r["t_replay"] for r in res])
    print(f"B1 acceptance 7: throughput per core ({workers} processes at once, one engine each), "
          f"{m:,} city-months on training family starts under the behaviour mix")
    print(f"rollout_behaviour (policy + engine + full observation every month): mean {tr.mean():,.0f} city-months/s per "
          f"core (min {tr.min():,.0f}, max {tr.max():,.0f})")
    print(f"dc.oracle.replay of the same action logs (engine only, scalars): mean {tp.mean():,.0f} city-months/s per core "
          f"(min {tp.min():,.0f}, max {tp.max():,.0f})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=16)
    acceptance(ap.parse_args().workers)


def test_listed_behaviour_and_forced_quake():
    """The second coverage mix: settings only from the given list, uniform; a forced earthquake in month 0 is in the
    plan (and only there), the engine takes it, the builder keeps building, and the log replays exactly."""
    from dc.engine import SC_TAX
    from dc.tasks import forced_for
    lst = [(0, 0, 0, 0), (3, 1, 0, 2), (5, 4, 4, 0)]
    rng = np.random.default_rng(1)
    draws = [sample_listed_behaviour(rng, lst) for _ in range(3000)]
    sets = [p.setting for p, _ in draws]
    assert set(sets) == set(lst) and max(abs(sets.count(x) / 3000 - 1 / 3) for x in lst) < 0.03
    assert all(l == p.label and l.endswith("+held") for p, l in draws)
    for bad in ((), ):
        try:
            sample_listed_behaviour(rng, list(bad))
        except ValueError:
            continue
        raise AssertionError("empty list accepted")
    try:
        HeldBudget(make_policy("noop"), (0, 0, 0, 0), {0: 9})
        raise AssertionError("disaster kind 9 accepted")
    except ValueError:
        pass
    quake = forced_for("recover")
    eng = Engine()
    try:
        cty = CITIES / "linecity.cty"
        pol, label = sample_listed_behaviour(np.random.default_rng(3), [(2, 0, 0, 0)], quake)
        assert label.endswith("+held+forced")
        plan, rep = rollout_behaviour(eng, cty, pol, 12, 77, False, np.random.default_rng(4), record="scalars",
                                      want_hash=True)
        want = np.zeros(12, dtype=np.int64)
        for m, k in quake.items():
            want[m] = k
        assert np.array_equal(plan[:, 4], want) and (plan[:, 0:4] == np.array([2, 0, 0, 0])).all()
        assert (n_calls_batch(plan) > 0).any() and (rep.scalars[1:, SC_TAX] == 2).all()
        acts, forced = compile_plan(plan)
        assert forced == quake
        r2 = replay(eng, cty, acts, 77, disasters=False, forced=forced, want_hash=True)
        assert np.array_equal(rep.hashes, r2.hashes)
        # the earthquake changed the city: the same plan without it ends elsewhere
        r3 = replay(eng, cty, acts, 77, disasters=False, forced=None, want_hash=True)
        assert r3.hashes[-1] != rep.hashes[-1]
    finally:
        eng.close()
