"""The end-to-end checks of the specification (6.5, as amended by the coordinator), plus diagnostics.

Run directly to print the tables:
    PYTHONPATH=hpr-dream python hpr-dream/tests/e2e_checks.py [--diagnostics] [--coverage]
The pytest wrappers are in test_end_to_end.py. Problem seeds are fixed here (check 1: 11,
check 2: 12) and were fixed before the first run.

Two grader settings (tests/synthetic.py):
  A  per-plan error sd 0.5 + per-sample noise sd 0.5: the attacker scores the mean of 2 samples,
     the verdict re-scores on 8 fresh samples (accept when at least 4 pass); probabilities are
     fractional.
  B  all K samples equal (per-plan error sd 0.5 only): the setting of the first report.

Matched floors: margin-scored attackers against the residual surrogate (paired pool: search
residual, verdict residual; pooled over the 200 instances of the task family, since 100 rows per
instance is fewer than B = 1,000); verdict-scored random shooting against the flip closed form.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from synthetic import Problem  # noqa: E402

import hpr_dream as hd  # noqa: E402
from hpr_dream import stats as S  # noqa: E402

SEED_CHECK1 = 11
SEED_CHECK2 = 12
BUDGETS = (1, 10, 100, 1000)
N_CAL = 100  # behaviour plans per instance: fp, fn, base rates, residual pools
N_BOOT = 2000
SETTINGS = {
    "A": dict(noise_sd=0.5, sample_sd=0.5, label="per-plan error sd 0.5 + per-sample noise sd 0.5 (K=2 search, 8 fresh for the verdict)"),
    "B": dict(noise_sd=0.5, sample_sd=0.0, label="all K samples equal, per-plan error sd 0.5"),
}
KW = dict(n_boot=N_BOOT, seed=0)


@dataclass
class Arm:
    grader_accept: list = field(default_factory=list)
    oracle_accept: list = field(default_factory=list)
    gap: list = field(default_factory=list)
    grader_p: list = field(default_factory=list)
    in_hole: list = field(default_factory=list)
    n_scored: int = 0

    def add(self, ga, oa, gap=np.nan, p=np.nan, in_hole=False, n_scored=0):
        self.grader_accept.append(bool(ga))
        self.oracle_accept.append(bool(oa))
        self.gap.append(float(gap))
        self.grader_p.append(float(p))
        self.in_hole.append(bool(in_hole))
        self.n_scored += int(n_scored)

    @property
    def hacked(self) -> np.ndarray:
        return np.array(self.grader_accept) & ~np.array(self.oracle_accept)

    def hack(self, cl) -> S.Estimate:
        return S.hackability(self.grader_accept, self.oracle_accept, cl, **KW)


@dataclass
class Cal:
    g: np.ndarray
    o: np.ndarray
    inst: np.ndarray
    p: np.ndarray
    pools: list
    fp: float
    fn: float


def _calibration(P: Problem, ss: np.random.SeedSequence, n_cal: int = N_CAL) -> Cal:
    """n_cal behaviour plans per instance, scored by grader (K = 2 search score, 8-sample verdict)
    and oracle. Pool rows: (search residual, verdict residual)."""
    g, o, inst, p, pools = [], [], [], [], []
    for i, s in enumerate(ss.spawn(P.n)):
        rng = np.random.default_rng(s)
        X = P.behaviour(rng, n_cal)
        m = P.oracle_margin(i, X)
        r_search = P.search_score(i, X, rng) - m
        p8, fourth = P.verdict(i, X, rng)
        pools.append(np.stack([r_search, fourth - m], axis=1))
        g.append(p8 >= 0.5)
        o.append(m >= 0)
        inst.append(np.full(n_cal, i))
        p.append(p8)
    g, o, inst, p = (np.concatenate(v) for v in (g, o, inst, p))
    fp = float((g & ~o).sum() / (~o).sum())
    fn = float((~g & o).sum() / o.sum())
    return Cal(g, o, inst, p, pools, fp, fn)


def _est(x: S.Estimate) -> str:
    mark = "u" if x.method == S.ZERO_BOUND_METHOD else " "
    return f"{x.value:6.3f} [{x.lo:6.3f},{x.hi:6.3f}]{mark}"


def _yn(b: bool) -> str:
    return "yes" if b else "NO"


LEGEND = "      u = no hacked instance: interval is [0, exact one-sided binomial upper bound on the 40 clusters]"


def _verdict_attack(P, i, props, B, rng_vs, rng_fresh):
    """Verdict-scored random shooting: each candidate scored by its 8-sample verdict + tie-break.
    Returns (plan, log, p of the selected plan at selection, p on a fresh 8-sample re-score)."""
    box = {}

    def vscore(X):
        p8, _ = P.verdict(i, X, rng_vs)
        box["p"] = p8
        return (p8 >= 0.5) + 1e-6 * P.tie_break(i, X)

    plan, log = hd.random_shooting(vscore, props, B)
    p_fresh, _ = P.verdict(i, plan[None], rng_fresh)
    return plan, log, float(box["p"][log["best_index"]]), float(p_fresh[0])


# ------------------------------------------------------------------------------------------
# check 1


def run_check1(seed: int = SEED_CHECK1, setting: str = "A", n_cal: int = N_CAL):
    t0 = time.time()
    st = SETTINGS[setting]
    P = Problem(seed, hole=False, noise_sd=st["noise_sd"], sample_sd=st["sample_sd"])
    root = np.random.SeedSequence([seed, 1])
    s_cal, s_prop, s_flip, s_res, s_search, s_verd, s_vs = root.spawn(7)
    cal = _calibration(P, s_cal, n_cal)
    fam = hd.ResidualFamily(cal.pools)
    arms = {k: {B: Arm() for B in BUDGETS} for k in ("margin", "verdict", "verdict_fresh", "flip", "resid")}
    ev = {B: [0, 0] for B in BUDGETS}  # oracle requests (both surrogates), evaluations (shared cache)
    seeds = [x.spawn(P.n) for x in (s_prop, s_flip, s_res, s_search, s_verd, s_vs)]
    pool_info = None
    for i in range(P.n):
        sp_, sf_, sr_, ss_, sv_, svs_ = (x[i] for x in seeds)
        props = P.behaviour(np.random.default_rng(sp_), max(BUDGETS))
        rng_search, rng_verd, rng_vs = (np.random.default_rng(x) for x in (ss_, sv_, svs_))
        oracle = hd.OracleCache(lambda X, i=i: P.oracle_margin(i, X))
        flip_g = hd.SurrogateGrader(hd.FlipSurrogate(cal.fp, cal.fn), oracle, np.random.default_rng(sf_))
        res_g = hd.SurrogateGrader(hd.ResidualSurrogate(cal.pools[i], family_pools=fam), oracle,
                                   np.random.default_rng(sr_))
        for B in BUDGETS:
            plan, log = hd.random_shooting(lambda X: P.search_score(i, X, rng_search), props, B)
            assert log["n_scored"] == B
            p8 = P.verdict(i, plan[None], rng_verd)[0][0]
            m_sel = P.oracle_margin(i, plan[None])[0]
            arms["margin"][B].add(p8 >= 0.5, m_sel >= 0, log["best_score"] - m_sel, p8, n_scored=log["n_scored"])
            plan, log, p_sel, p_fresh = _verdict_attack(P, i, props, B, rng_vs, rng_verd)
            m_sel = P.oracle_margin(i, plan[None])[0]
            arms["verdict"][B].add(p_sel >= 0.5, m_sel >= 0, p=p_sel, n_scored=log["n_scored"])
            arms["verdict_fresh"][B].add(p_fresh >= 0.5, m_sel >= 0, p=p_fresh)
            before = oracle.n_evals
            for k, gr in (("flip", flip_g), ("resid", res_g)):
                r = hd.attack_surrogate(lambda s, B=B: hd.random_shooting(s, props, B), gr, budget=B)
                arms[k][B].add(r.surrogate_accept, r.oracle_accept, r.surrogate_score - r.oracle_margin,
                               n_scored=r.log["n_scored"])
                ev[B][0] += r.log["n_oracle_requests"]
                if k == "resid":
                    pool_info = (r.log["residual_pool_kind"], r.log["residual_pool_size"], r.log["residual_pool_paired"])
            ev[B][1] += oracle.n_evals - before
    cl = P.cluster
    rows, verdicts = [], {}
    for B in BUDGETS:
        A = {k: arms[k][B] for k in arms}
        r = dict(B=B, n_scored=A["margin"].n_scored, n_scored_v=A["verdict"].n_scored, ev=ev[B])
        r["hv"] = A["verdict"].hack(cl)
        r["ffv"] = S.flip_floor(B, cal.g, cal.o, cal.inst, cl, hacked=A["verdict"].hacked, **KW)
        r["hvf"] = A["verdict_fresh"].hack(cl)
        r["hf"] = A["flip"].hack(cl)
        r["hm"] = A["margin"].hack(cl)
        r["hr"] = A["resid"].hack(cl)
        r["ex_r"] = S.excess(A["margin"].hacked, A["resid"].hacked, cl, **KW)
        r["ffm"] = S.flip_floor(B, cal.g, cal.o, cal.inst, cl, hacked=A["margin"].hacked, **KW)
        r["gap"] = S.excess(A["margin"].gap, np.zeros(P.n), cl, **KW)
        r["gap_r"] = S.excess(A["resid"].gap, np.zeros(P.n), cl, **KW)
        rows.append(r)
        verdicts[B] = dict(
            verdict_closed_form_in_ci=r["hv"].contains(r["ffv"].floor.value),
            verdict_excess_ci_has_zero=r["ffv"].excess.contains(0.0),
            flip_surrogate_matches_closed_form=r["hf"].contains(r["ffv"].floor.value),
            excess_over_residual_ci_has_zero=r["ex_r"].contains(0.0),
            margin_closed_form_in_ci=r["hm"].contains(r["ffv"].floor.value),
        )
    pi = np.bincount(cal.inst, weights=cal.o.astype(float)) / n_cal
    L = [
        f"CHECK 1 [setting {setting}]  unbiased noisy grader: {st['label']}; random shooting",
        f"  instances {P.n}, clusters {len(np.unique(cl))}, behaviour plans {cal.g.size} ({n_cal} per instance), "
        f"bootstrap {N_BOOT} cluster resamples, seed 0",
        f"  measured on behaviour plans (8-sample verdict): fp = {cal.fp:.4f}, fn = {cal.fn:.4f}, pooled base rate = "
        f"{cal.o.mean():.4f}, per-instance base rate min/median/max = {pi.min():.2f}/{np.median(pi):.2f}/{pi.max():.2f}",
        f"  residual pool: {pool_info[0]}, {pool_info[1]} rows, paired = {pool_info[2]}",
        "",
        "  (a) verdict-scored random shooting (score = 8-sample accept + uniform tie-break) vs its matched floor, the flip closed form",
        "      selection verdict = the verdict the attacker selected on; fresh re-score = the selected plan re-scored on 8 new samples",
        f"  {'B':>5} {'plans scored':>12} {'verdict-scored hack':>25} {'closed form [95% CI]':>25} {'pooled-pi':>9} {'in CI':>5} "
        f"{'excess over closed form':>25} {'0 in CI':>7} {'flip surrogate attack':>25} {'fresh re-score hack':>25}",
    ]
    for r in rows:
        v = verdicts[r["B"]]
        L.append(f"  {r['B']:>5} {r['n_scored_v']:>12} {_est(r['hv']):>25} {_est(r['ffv'].floor):>25} "
                 f"{r['ffv'].floor_pooled_base_rate.value:>9.3f} {_yn(v['verdict_closed_form_in_ci']):>5} "
                 f"{_est(r['ffv'].excess):>25} {_yn(v['verdict_excess_ci_has_zero']):>7} {_est(r['hf']):>25} {_est(r['hvf']):>25}")
    L += [
        "",
        "  (b) margin-scored random shooting (score = mean of 2 sampled margins) vs its matched floor, the residual surrogate",
        "      gap = attacker's score minus oracle margin of the selected plan (behaviour-sd units); oracle requests by the two",
        "      surrogate attacks / evaluations through the shared oracle cache, summed over instances",
        f"  {'B':>5} {'plans scored':>12} {'hackability':>25} {'residual floor':>25} {'excess over residual':>25} {'0 in CI':>7} "
        f"{'gap, real grader':>25} {'gap, residual surr.':>25} {'oracle req/evals':>17}",
    ]
    for r in rows:
        L.append(f"  {r['B']:>5} {r['n_scored']:>12} {_est(r['hm']):>25} {_est(r['hr']):>25} {_est(r['ex_r']):>25} "
                 f"{_yn(verdicts[r['B']]['excess_over_residual_ci_has_zero']):>7} {_est(r['gap']):>25} {_est(r['gap_r']):>25} "
                 f"{r['ev'][0]:>8}/{r['ev'][1]:<8}")
    L += [
        "",
        "  (c) mismatched pairing, for reference: margin-scored random shooting against the flip closed form",
        f"  {'B':>5} {'margin-scored hack':>25} {'closed form':>11} {'excess over closed form':>25}",
    ]
    for r in rows:
        L.append(f"  {r['B']:>5} {_est(r['hm']):>25} {r['ffv'].floor.value:>11.3f} {_est(r['ffm'].excess):>25}")
    crit_i = all(v["verdict_closed_form_in_ci"] for v in verdicts.values())
    crit_ii = all(v["excess_over_residual_ci_has_zero"] for v in verdicts.values())
    L += [
        LEGEND,
        "",
        f"  criterion (i)  verdict-scored random shooting: closed form inside its hackability CI at every B: {'PASS' if crit_i else 'FAIL'}",
        f"  criterion (ii) margin-scored random shooting: excess over residual surrogate has 0 in CI at every B: {'PASS' if crit_ii else 'FAIL'}",
        f"  wall time {time.time() - t0:.1f} s",
    ]
    return "\n".join(L), dict(rows=rows, verdicts=verdicts, crit_i=crit_i, crit_ii=crit_ii, fp=cal.fp, fn=cal.fn)


# ------------------------------------------------------------------------------------------
# check 2


def run_check2(seed: int = SEED_CHECK2, setting: str = "A", build_card: bool = False):
    t0 = time.time()
    st = SETTINGS[setting]
    P = Problem(seed, hole=True, noise_sd=st["noise_sd"], sample_sd=st["sample_sd"])
    root = np.random.SeedSequence([seed, 2])
    s_cal, s_prop, s_init, s_cem, s_flip, s_res, s_search, s_verd, s_vs = root.spawn(9)
    cal = _calibration(P, s_cal)
    fam = hd.ResidualFamily(cal.pools)
    init = hd.fit_marginals(P.space, P.behaviour(np.random.default_rng(s_init), 2000))
    keys = [("random_shooting", "margin"), ("cem", "margin"), ("random_shooting", "verdict")]
    arms = {(a, sc, k): {B: Arm() for B in BUDGETS} for a, sc in keys for k in ("real", "flip", "resid")}
    fresh = {B: Arm() for B in BUDGETS}
    seeds = [x.spawn(P.n) for x in (s_prop, s_cem, s_flip, s_res, s_search, s_verd, s_vs)]
    n_floor_oracle = {(a, sc): {B: np.zeros(P.n, int) for B in BUDGETS} for a, sc in keys}
    for i in range(P.n):
        sp_, sc_, sf_, sr_, ss_, sv_, svs_ = (x[i] for x in seeds)
        props = P.behaviour(np.random.default_rng(sp_), max(BUDGETS))
        rng_search, rng_verd, rng_vs = (np.random.default_rng(x) for x in (ss_, sv_, svs_))
        oracle = hd.OracleCache(lambda X, i=i: P.oracle_margin(i, X))
        cem_seeds = sc_.spawn(len(BUDGETS))
        graders = {}
        for a, ff_seed, rr_seed in (("random_shooting", *sf_.spawn(1), *sr_.spawn(1)),
                                    ("cem", *sf_.spawn(1), *sr_.spawn(1))):
            graders[a] = {
                "flip": hd.SurrogateGrader(hd.FlipSurrogate(cal.fp, cal.fn), oracle, np.random.default_rng(ff_seed)),
                "resid": hd.SurrogateGrader(hd.ResidualSurrogate(cal.pools[i], family_pools=fam), oracle,
                                            np.random.default_rng(rr_seed)),
            }
        for bi, B in enumerate(BUDGETS):
            for a in ("random_shooting", "cem"):
                if a == "random_shooting":
                    attack = lambda s, B=B: hd.random_shooting(s, props, B)
                else:
                    attack = lambda s, B=B, bi=bi: hd.cem(s, P.space, B, np.random.default_rng(cem_seeds[bi]), init)
                plan, log = attack(lambda X: P.search_score(i, X, rng_search))
                assert log["n_scored"] == B
                x = plan[None]
                p8 = P.verdict(i, x, rng_verd)[0][0]
                m_sel = P.oracle_margin(i, x)[0]
                arms[(a, "margin", "real")][B].add(p8 >= 0.5, m_sel >= 0, log["best_score"] - m_sel, p8,
                                                    P.in_hole(x)[0], log["n_scored"])
                for k, gr in graders[a].items():
                    before = oracle.n_evals
                    r = hd.attack_surrogate(attack, gr, budget=B)
                    n_floor_oracle[(a, "margin")][B][i] += oracle.n_evals - before
                    arms[(a, "margin", k)][B].add(r.surrogate_accept, r.oracle_accept, in_hole=P.in_hole(r.plan[None])[0],
                                                   n_scored=r.log["n_scored"])
                    if a == "random_shooting":  # the surrogate attacks do not depend on how the real attacker scores
                        arms[("random_shooting", "verdict", k)][B].add(r.surrogate_accept, r.oracle_accept,
                                                                        in_hole=P.in_hole(r.plan[None])[0])
            plan, log, p_sel, p_fresh = _verdict_attack(P, i, props, B, rng_vs, rng_verd)
            x = plan[None]
            m_sel = P.oracle_margin(i, x)[0]
            arms[("random_shooting", "verdict", "real")][B].add(p_sel >= 0.5, m_sel >= 0, p=p_sel, in_hole=P.in_hole(x)[0],
                                                                 n_scored=log["n_scored"])
            fresh[B].add(p_fresh >= 0.5, m_sel >= 0, p=p_fresh)
    cl = P.cluster
    out = {}
    L = [
        f"CHECK 2 [setting {setting}]  grader with a plan-dependent hole (R = {{x0=2, x1=3, x2=4}}, 0.8 % of behaviour; "
        f"grader +3, oracle margin -1); {st['label']}",
        f"  instances {P.n}, clusters {len(np.unique(cl))}, behaviour plans {cal.g.size} ({N_CAL} per instance), "
        f"CEM init fitted to 2000 behaviour plans, bootstrap {N_BOOT} cluster resamples, seed 0",
        f"  measured on behaviour plans (8-sample verdict): fp = {cal.fp:.4f}, fn = {cal.fn:.4f}, pooled base rate = "
        f"{cal.o.mean():.4f}; residual pool pooled over {P.n} instances ({P.n * N_CAL} paired rows)",
    ]
    for a in ("random_shooting", "cem"):
        L += [
            "",
            f"  {a}, margin-scored: matched floor = residual surrogate; flip surrogate shown with its role (verdict-scored floor)",
            "  plans scored summed over instances; sel. in R = share of selected plans inside the hole",
            f"  {'B':>5} {'plans scored':>12} {'hackability':>25} {'sel. in R':>9} {'residual floor':>25} "
            f"{'excess over residual':>25} {'flip surrogate':>25} {'excess over flip surr.':>25}",
        ]
        for B in BUDGETS:
            real, fl, rs = (arms[(a, "margin", k)][B] for k in ("real", "flip", "resid"))
            o = dict(h=real.hack(cl), hf=fl.hack(cl), hr=rs.hack(cl), exf=S.excess(real.hacked, fl.hacked, cl, **KW),
                     exr=S.excess(real.hacked, rs.hacked, cl, **KW), hacked=real.hacked, in_r=float(np.mean(real.in_hole)))
            out[(a, "margin", B)] = o
            L.append(f"  {B:>5} {real.n_scored:>12} {_est(o['h']):>25} {o['in_r']:>9.3f} {_est(o['hr']):>25} {_est(o['exr']):>25} "
                     f"{_est(o['hf']):>25} {_est(o['exf']):>25}")
    L += [
        "",
        "  random_shooting, verdict-scored (8-sample accept + tie-break): matched floor = flip closed form",
        f"  {'B':>5} {'plans scored':>12} {'hackability':>25} {'sel. in R':>9} {'closed form':>25} {'excess over closed form':>25} "
        f"{'flip surrogate':>25} {'fresh re-score hack':>25}",
    ]
    for B in BUDGETS:
        real = arms[("random_shooting", "verdict", "real")][B]
        ff = S.flip_floor(B, cal.g, cal.o, cal.inst, cl, hacked=real.hacked, **KW)
        o = dict(h=real.hack(cl), ff=ff, hf=arms[("random_shooting", "verdict", "flip")][B].hack(cl), hvf=fresh[B].hack(cl))
        out[("random_shooting", "verdict", B)] = o
        L.append(f"  {B:>5} {real.n_scored:>12} {_est(o['h']):>25} {np.mean(real.in_hole):>9.3f} {_est(ff.floor):>25} "
                 f"{_est(ff.excess):>25} {_est(o['hf']):>25} {_est(o['hvf']):>25}")
    c = [out[("cem", "margin", B)]["h"].value for B in BUDGETS]
    rises = all(b > a_ for a_, b in zip(c, c[1:]))
    d = S.excess(out[("cem", "margin", 1000)]["hacked"], out[("cem", "margin", 1)]["hacked"], cl, **KW)
    o = out[("cem", "margin", 1000)]
    pos_f, pos_r = o["exf"].lo > 0, o["exr"].lo > 0
    L += [
        LEGEND,
        "",
        f"  CEM hackability(B=1000) - hackability(B=1), paired: {_est(d)}",
        f"  criterion (i)   CEM hackability rises with B (point estimates {', '.join(f'{v:.3f}' for v in c)}): {'PASS' if rises else 'FAIL'}",
        f"  criterion (ii)  CEM B=1000 excess over the residual surrogate floor (matched), CI above 0: {'PASS' if pos_r else 'FAIL'}",
        f"  criterion (iii) CEM B=1000 excess over the flip surrogate floor, CI above 0: {'PASS' if pos_f else 'FAIL'}",
    ]
    res = dict(out=out, rises=rises, pos_f=pos_f, pos_r=pos_r, diff=d)
    if build_card:
        rec = {k: [] for k in ("instance", "cluster", "attacker", "scoring", "budget", "attacker_seed", "plan_id", "grader_p",
                               "oracle_accept", "flip_grader_accept", "flip_oracle_accept", "residual_grader_accept",
                               "residual_oracle_accept", "n_scored", "n_floor_oracle_evals")}
        for a, sc in keys:
            for B in BUDGETS:
                real, fl, rs = (arms[(a, sc, k)][B] for k in ("real", "flip", "resid"))
                for i in range(P.n):
                    rec["instance"].append(i)
                    rec["cluster"].append(int(cl[i]))
                    rec["attacker"].append(a)
                    rec["scoring"].append(sc)
                    rec["budget"].append(B)
                    rec["attacker_seed"].append(0)
                    rec["plan_id"].append(f"{a}-{sc}-{B}-{i}")
                    rec["grader_p"].append(real.grader_p[i])
                    rec["oracle_accept"].append(real.oracle_accept[i])
                    rec["flip_grader_accept"].append(fl.grader_accept[i])
                    rec["flip_oracle_accept"].append(fl.oracle_accept[i])
                    rec["residual_grader_accept"].append(rs.grader_accept[i])
                    rec["residual_oracle_accept"].append(rs.oracle_accept[i])
                    rec["n_scored"].append(B)
                    # verdict-scored rows reuse the random-shooting floors, already counted on the margin rows
                    rec["n_floor_oracle_evals"].append(int(n_floor_oracle[(a, sc)][B][i]) if sc == "margin" else 0)
        beh = {"instance": cal.inst, "cluster": cl[cal.inst], "grader_p": cal.p, "oracle_accept": cal.o}
        meta = {"audited": f"synthetic hole grader, setting {setting}", "code_version": "e2e_checks", "date": "2026-11-09",
                "revisit_date": "2027-05-09"}
        card = hd.build_card({k: np.array(v) for k, v in rec.items()}, meta, behaviour=beh, bca=True)
        cc = next(e for e in card["hackability_curve"] if (e["attacker"], e["scoring"], e["budget"]) == ("cem", "margin", 1000))
        vc = next(e for e in card["verdict_scored_curve"] if e["budget"] == 1000)
        res["card"] = card
        L += [
            "",
            f"  card (bca=True) from these records: {card['counts']['records']} records, {card['counts']['groups']} groups, "
            f"{card['counts']['behaviour_plans']} behaviour plans, noise-floor oracle evaluations "
            f"{card['counts']['oracle_plan_evaluations']['noise_floor_attacks']}",
            f"    cem margin B=1000 hackability {cc['hackability']['value']:.3f} percentile [{cc['hackability']['lo']:.3f}, "
            f"{cc['hackability']['hi']:.3f}] BCa [{cc['hackability']['bca_lo']:.3f}, {cc['hackability']['bca_hi']:.3f}]",
            f"    verdict-scored random shooting B=1000: hackability {vc['hackability']['value']:.3f}, flip closed form "
            f"{vc['flip_closed_form']['floor']['value']:.3f}",
        ]
    L.append(f"  wall time {time.time() - t0:.1f} s")
    return "\n".join(L), res


# ------------------------------------------------------------------------------------------
# check 3


def run_check3():
    t0 = time.time()
    space = hd.Space.concat(hd.Space.categorical_columns([4, 7, 2, 30]), hd.Space.integer_columns([-5, 0], [5, 100]),
                            hd.Space.categorical_columns([3]).freeze([0], [2]))
    rng = np.random.default_rng(3)
    w = rng.normal(size=space.D)
    pool = space.sample_uniform(rng, 10000)
    budgets = (1, 10, 100, 1000, 10000)
    lines = [
        "CHECK 3  budget accounting: plans handed to score, counted outside the attacker (external) and inside (log)",
        f"  {'attacker':<26} {'B':>6} {'schedule':>10} {'external':>9} {'log n_scored':>12} {'calls':>6} {'max batch':>9} {'ok':>3}",
    ]
    ok_all = True
    results = []

    def counted():
        box = {"n": 0, "calls": 0}

        def score(X):
            box["n"] += X.shape[0]
            box["calls"] += 1
            return X @ w
        return score, box

    def row(name, B, sched, box, log):
        nonlocal ok_all
        ok = box["n"] == B and log["n_scored"] == B and box["calls"] == log["n_score_calls"]
        ok_all &= ok
        results.append((name, B, box["n"], log["n_scored"], ok))
        lines.append(f"  {name:<26} {B:>6} {sched:>10} {box['n']:>9} {log['n_scored']:>12} {log['n_score_calls']:>6} "
                     f"{log['max_batch']:>9} {'yes' if ok else 'NO':>3}")

    for B in budgets:
        s, box = counted()
        _, log = hd.random_shooting(s, pool, B)
        row("random_shooting", B, "1 call", box, log)
    for B in budgets:
        s, box = counted()
        _, log = hd.best_of_n(s, pool, B)
        row("best_of_n", B, "1 call", box, log)
    for B in budgets:
        for init_name, init in (("uniform", None), ("fitted", hd.fit_marginals(space, pool[:500]))):
            s, box = counted()
            _, log = hd.cem(s, space, B, np.random.default_rng(B), init)
            row(f"cem ({init_name} init)", B, f"{log['generations']} x {log['population']}", box, log)
    for B in budgets:
        s, box = counted()
        _, log = hd.random_shooting(s, pool, B, batch_size=64)
        row("random_shooting batch 64", B, f"{-(-B // 64)} calls", box, log)
    for B in budgets:
        s, box = counted()
        oracle = lambda X: X @ w - 1.0
        r = hd.attack_surrogate(lambda sc, B=B: hd.cem(sc, space, B, np.random.default_rng(B)), hd.FlipSurrogate(0.1, 0.2),
                                oracle, np.random.default_rng(0), budget=B)
        box["n"] = r.log["surrogate_n_scored"]
        box["calls"] = r.log["n_score_calls"]
        row("cem vs flip surrogate", B, f"{r.log['generations']} x {r.log['population']}", box, r.log)
    lines += ["", f"  spec 6.5.3: every attacker scored exactly B plans at every B: {'PASS' if ok_all else 'FAIL'}",
              f"  wall time {time.time() - t0:.1f} s"]
    return "\n".join(lines), dict(ok=ok_all, results=results)


# ------------------------------------------------------------------------------------------
# residual pool diagnostic


def run_pool_diagnostic(seed: int = SEED_CHECK1, B: int = 1000):
    """Unbiased grader with per-plan error sd 2.0; margin-scored random shooting at B against the
    residual surrogate built three ways."""
    t0 = time.time()
    L = [f"POOL DIAGNOSTIC  unbiased grader, per-plan error sd 2.0, margin-scored random shooting at B = {B}, check 1 problem",
         f"  {'grader':<40} {'residual pool':<34} {'refused':>7} {'hackability':>25} {'residual floor':>25} "
         f"{'excess over residual':>25} {'0 in CI':>7}"]
    res = {}
    for sample_sd in (0.0, 0.5):
        P = Problem(seed, hole=False, noise_sd=2.0, sample_sd=sample_sd)
        root = np.random.SeedSequence([seed, 3, int(sample_sd * 10)])
        s_cal, s_prop, s_search, s_verd, s_res = root.spawn(5)
        cal = _calibration(P, s_cal, 1000)
        p1000 = cal.pools
        p100 = [p[:100] for p in p1000]
        fam100 = hd.ResidualFamily(p100)
        configs = [("per-instance, 1000 rows", lambda i: hd.ResidualSurrogate(p1000[i])),
                   ("pooled, 200 instances x 100 rows", lambda i: hd.ResidualSurrogate(p100[i], family_pools=fam100)),
                   ("per-instance, 100 rows", lambda i: hd.ResidualSurrogate(p100[i]))]
        real = Arm()
        floors = {name: Arm() for name, _ in configs}
        refused = {name: 0 for name, _ in configs}
        seeds = [x.spawn(P.n) for x in (s_prop, s_search, s_verd, s_res)]
        for i in range(P.n):
            sp_, ss_, sv_, sr_ = (x[i] for x in seeds)
            props = P.behaviour(np.random.default_rng(sp_), B)
            rng_search, rng_verd = np.random.default_rng(ss_), np.random.default_rng(sv_)
            plan, log = hd.random_shooting(lambda X: P.search_score(i, X, rng_search), props, B)
            p8 = P.verdict(i, plan[None], rng_verd)[0][0]
            real.add(p8 >= 0.5, P.oracle_margin(i, plan[None])[0] >= 0)
            oracle = hd.OracleCache(lambda X, i=i: P.oracle_margin(i, X))
            for j, (name, make) in enumerate(configs):
                rng = np.random.default_rng(sr_.spawn(1)[0])
                try:
                    r = hd.attack_surrogate(lambda s: hd.random_shooting(s, props, B), make(i), oracle, rng, budget=B)
                except hd.PoolTooSmall:
                    refused[name] += 1
                    continue
                floors[name].add(r.surrogate_accept, r.oracle_accept)
        cl = P.cluster
        hk = real.hack(cl)
        glabel = f"per-plan 2.0, per-sample {sample_sd}" + (" (all K equal)" if sample_sd == 0 else "")
        for name, _ in configs:
            if refused[name]:
                L.append(f"  {glabel:<40} {name:<34} {refused[name]:>7} {_est(hk):>25} {'-':>25} {'-':>25} {'-':>7}")
                res[(sample_sd, name)] = dict(refused=refused[name])
                continue
            fl = floors[name]
            hf = fl.hack(cl)
            ex = S.excess(real.hacked, fl.hacked, cl, **KW)
            res[(sample_sd, name)] = dict(refused=0, floor=hf, excess=ex, zero_in_ci=ex.contains(0.0))
            L.append(f"  {glabel:<40} {name:<34} {0:>7} {_est(hk):>25} {_est(hf):>25} {_est(ex):>25} {_yn(ex.contains(0.0)):>7}")
    L += ["  refused = instances whose attack the surrogate refused (pool rows < B)", f"  wall time {time.time() - t0:.1f} s"]
    return "\n".join(L), res


# ------------------------------------------------------------------------------------------
# coverage of the intervals


def run_coverage(reps: int = 1000, seed: int = 0):
    """Coverage of the 95 per cent intervals for hackability: 200 instances in 40 clusters of 5,
    instance hack probability expit(logit(q) + u_c), u_c ~ N(0, 1) per cluster; the true mean is
    computed from 2,000,000 draws of u."""
    from scipy.special import expit, logit
    t0 = time.time()
    rng = np.random.default_rng(seed)
    cl = np.repeat(np.arange(40), 5)
    L = [f"COVERAGE  95 % intervals for hackability, 200 instances in 40 clusters, {reps} replications per row, "
         f"{N_BOOT} resamples each",
         f"  {'q':>6} {'true mean':>9} {'zero-hack reps':>14} {'percentile cover':>16} {'mean width':>10} "
         f"{'BCa cover':>9} {'mean width':>10} {'BCa undefined':>13}"]
    out = []
    for q in (0.005, 0.02, 0.05, 0.2, 0.5):
        mu = float(np.mean(expit(logit(q) + rng.normal(size=2_000_000))))
        cp = cb = zero = und = 0
        wp = wb = 0.0
        for r in range(reps):
            u = rng.normal(size=40)[cl]
            y = rng.random(200) < expit(logit(q) + u)
            e = S.hackability(y, np.zeros(200, bool), cl, n_boot=N_BOOT, seed=r, bca=True)
            zero += e.method == S.ZERO_BOUND_METHOD
            cp += e.lo <= mu <= e.hi
            wp += e.hi - e.lo
            if np.isfinite(e.bca_lo):
                cb += e.bca_lo <= mu <= e.bca_hi
                wb += e.bca_hi - e.bca_lo
            else:
                und += 1
        nb = reps - und
        out.append(dict(q=q, mu=mu, zero=zero, pct=cp / reps, bca=cb / max(nb, 1), und=und))
        L.append(f"  {q:>6} {mu:>9.4f} {zero:>14} {cp / reps:>16.3f} {wp / reps:>10.3f} {cb / max(nb, 1):>9.3f} "
                 f"{wb / max(nb, 1):>10.3f} {und:>13}")
    L += ["  zero-hack replications use [0, 1 - 0.05^(1/40)] = [0, 0.072] for both columns",
          f"  wall time {time.time() - t0:.1f} s"]
    return "\n".join(L), out


if __name__ == "__main__":
    for setting in ("A", "B"):
        print(run_check1(setting=setting)[0], end="\n\n")
    for setting in ("A", "B"):
        print(run_check2(setting=setting, build_card=setting == "A")[0], end="\n\n")
    print(run_check3()[0], end="\n\n")
    if "--diagnostics" in sys.argv:
        print(run_pool_diagnostic()[0], end="\n\n")
    if "--coverage" in sys.argv:
        print(run_coverage()[0])
