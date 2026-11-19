"""Generate paper/numbers.tex, the generated tables and the macro ledger from the result files.

Every quantitative macro the text uses is defined here as (name, value, source file, locator). The
script refuses to write anything if a source file is missing, if a locator does not resolve, or if a
value quoted from a text source (code or results markdown) is not found there verbatim. Nothing
is typed by hand: a value is read from a result file, counted or averaged from one, or checked
against code and data manifests in the repository.

The ladder is complete, so the test selection's fidelity files are read (they are what the paper
reports); the development selection is no longer read.

Outputs (all under paper/):
  numbers.tex             \\newcommand definitions, each preceded by a comment naming its source
  numbers_ledger.md       name | value | source | locator, one row per macro (the CLAIMS table)
  numbers_manifest.json   the same, machine-readable, with the sha256 of every source file
  tables/*.tex            generated tables
Run from anywhere: python paper/scripts/make_numbers.py
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "paper"
sys.path.insert(0, str(REPO / "hpr-dream"))
from hpr_dream import stats as HS  # noqa: E402

LADDER = REPO / "results/fidelity/ladder"
MAIN = "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24"
SEEDED = "results/audit/ladder/os_50m_full/samples_006000000/tasks_v2_H24_cem_seeded"
ENGREF = "results/audit/engine_reference/tasks_v2_H24"

MACROS: list = []
SOURCES: dict = {}
_cache: dict = {}


class Missing(SystemExit):
    pass


def src(path) -> Path:
    s = str(path)
    if s.startswith("<repo>/"):
        s = s[len("<repo>/"):]
    p = Path(s)
    if not p.is_absolute():
        p = REPO / p
    if not p.exists():
        raise Missing(f"numbers: source file missing: {p}")
    if str(p) not in SOURCES:
        SOURCES[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
    return p


def J(path):
    p = src(path)
    if p not in _cache:
        _cache[p] = json.loads(p.read_text())
    return _cache[p]


def T(path):
    return src(path).read_text()


def rel(p):
    p = Path(p)
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def name_ok(n):
    if not re.fullmatch(r"[A-Za-z]+", n):
        raise ValueError(f"bad macro name {n!r}")
    if any(m[0] == n for m in MACROS):
        raise ValueError(f"duplicate macro {n}")
    return n


def add(name, value, source, locator):
    MACROS.append((name_ok(name), str(value), rel(src(source)), locator))


def add_multi(name, value, sources, locator):
    """A value computed from several files (each is hashed into the manifest)."""
    for s in sources:
        src(s)
    MACROS.append((name_ok(name), str(value), f"{len(sources)} files: " + rel(src(sources[0])) + " ...", locator))


IFS: list = []          # (name, bool, source, locator): \newif\if<name> switches the text reads


def add_if(name, flag, source, locator):
    """A TeX switch (\\if<name>) the text branches on, e.g. whether a still-running result is complete."""
    if not re.fullmatch(r"[A-Za-z]+", name) or any(i[0] == name for i in IFS):
        raise ValueError(f"bad or duplicate switch {name!r}")
    IFS.append((name, bool(flag), rel(src(source)), locator))


def add_if_opt(name, flag, path, locator):
    """A switch on a result file that may not exist yet : false, with the reason, until it
    exists and the paper's reader of it is written; the file is hashed into the manifest once it exists."""
    if not re.fullmatch(r"[A-Za-z]+", name) or any(i[0] == name for i in IFS):
        raise ValueError(f"bad or duplicate switch {name!r}")
    p = REPO / path
    IFS.append((name, bool(flag), rel(src(p)) if p.exists() else f"{path} (not yet written)", locator))


PENDING = r"\slotmark{pending}"


def pending(name, source, why):
    """A macro whose result is not complete: it prints as a red mark if it is ever reached (the text only uses it
    inside the branch that runs when the result is complete), and the ledger records that nothing was read."""
    MACROS.append((name_ok(name), PENDING, rel(src(source)), f"pending, not read: {why}"))


def quote(name, text, source, value=None):
    """A value quoted from a text source: ``text`` must occur verbatim in the file."""
    body = T(source)
    if text not in body:
        raise Missing(f"numbers: {name}: text not found in {source}: {text!r}")
    add(name, value if value is not None else text, source, f'text "{text}"')


# ---------------------------------------------------------------------------------------------
# formatting
# ---------------------------------------------------------------------------------------------
def mbox_neg(s):
    if s in ("-0", "-0.0", "-0.00", "-0.000", "+0", "+0.0", "+0.00", "+0.000"):
        return s[1:]
    return r"\mbox{-}" + s[1:] if s.startswith("-") and len(s) > 1 and s[1].isdigit() else s


def f3(x):
    if x is None:
        return "n/a"
    a = f"{abs(x):.3f}"
    if a == "0.000":
        return "0.000"
    return a if x > 0 else r"\mbox{-}" + a


def s3(x):
    if x is None:
        return "n/a"
    a = f"{abs(x):.3f}"
    if a == "0.000":
        return "0.000"
    return ("+" if x > 0 else r"\mbox{-}") + a


def f2(x):
    a = f"{abs(x):.2f}"
    if a == "0.00":
        return "0.00"
    return a if x > 0 else r"\mbox{-}" + a


def ints(n):
    k = int(n)
    if k == 0:
        return "0"
    return f"{k:,}" if k > 0 else r"\mbox{-}" + f"{abs(k):,}"


def ci(d, signed=False, fmt=None):
    if d is None:
        return "n/a"
    lo, hi = d.get("bca_lo"), d.get("bca_hi")
    if lo is None or hi is None or (isinstance(lo, float) and np.isnan(lo)):
        lo, hi = d.get("lo"), d.get("hi")         # percentile limits where BCa is not given or undefined
    if d.get("value") is None or lo is None or hi is None:
        return "n/a"
    f = fmt or (s3 if signed else f3)
    return f"[{f(lo)}, {f(hi)}]"


def est(d):
    return None if d is None or d.get("value") is None else float(d["value"])


B_WORD = {1: "One", 10: "Ten", 100: "Hund", 1000: "Thou", 10000: "TenThou"}
M_WORD = {"random": "Rand", "best_of_n": "Bon", "cem": "Cem", "random_verdict": "Verd", "cem_seeded": "Ad"}
F_WORD = {"grow": "Grow", "solvent": "Solv", "treasury": "Treas", "recover": "Recov", "power": "Power"}
FAMS = list(F_WORD)


# ---------------------------------------------------------------------------------------------
# 1. the main checkpoint against the perfect emulator (random search, best-of-N, adaptive search)
# ---------------------------------------------------------------------------------------------
def reference(path, methods):
    ref = J(path)
    groups = {}
    for sub, d in ref["subsets"].items():
        for g in d["groups"]:
            if g["method"] in methods and "difference" in g:
                groups[(sub, g["method"], int(g["budget"]))] = g
    loc = lambda sub, m, b, *k: f"subsets.{sub}.groups[method={m},budget={b}]." + ".".join(k)
    for (sub, m, b), g in groups.items():
        if sub not in ("all", "in_band"):
            continue
        p = M_WORD[m] + B_WORD[b] + ("" if sub == "all" else "WP")
        for who, tag in (("emulator", ""), ("perfect_emulator", "Perf")):
            e = g[who]
            for key, nm in (("hackability", "Hack"), ("judge_accept", "JudgeAcc"), ("oracle_accept", "OrAcc"),
                            ("oracle_reject_given_judge_accept", "CondRej"), ("false_rejection", "FalseRej")):
                if key not in e:
                    continue
                add(p + tag + nm, f3(est(e[key])), path, loc(sub, m, b, who, key, "value"))
                add(p + tag + nm + "CI", ci(e[key]), path, loc(sub, m, b, who, key, "bca"))
        add(p + "Diff", s3(est(g["difference"])), path, loc(sub, m, b, "difference.value"))
        add(p + "DiffCI", ci(g["difference"], signed=True), path, loc(sub, m, b, "difference.bca"))
        add(p + "N", ints(g["n_paired"]), path, loc(sub, m, b, "n_paired"))
        short = est(g["perfect_emulator"]["oracle_accept"]) - est(g["emulator"]["oracle_accept"])
        add(p + "Short", f3(short), path, loc(sub, m, b, "perfect_emulator.oracle_accept.value - emulator.oracle_accept.value"))
        for draw, dn in (("plain", "Plain"), ("volatility", "Vol")):
            fl = g.get("floors", {}).get(draw)
            if not fl:
                continue
            add(p + dn + "Floor", f3(est(fl["floor"])), path, loc(sub, m, b, "floors", draw, "floor.value"))
    for fam, fw in F_WORD.items():
        sub = f"task:{fam}"
        for m in methods:
            for b in (1, 10, 100, 1000):
                g = groups.get((sub, m, b))
                if g is None:
                    continue
                p = fw + M_WORD[m] + B_WORD[b]
                for who, tag in (("emulator", ""), ("perfect_emulator", "Perf")):
                    for key, nm in (("hackability", "Hack"), ("judge_accept", "JudgeAcc"), ("oracle_accept", "OrAcc"),
                                    ("false_rejection", "FalseRej")):
                        if key in g[who]:
                            add(p + tag + nm, f3(est(g[who][key])), path, loc(sub, m, b, who, key, "value"))
                            add(p + tag + nm + "CI", ci(g[who][key]), path, loc(sub, m, b, who, key, "bca"))
                add(p + "Diff", s3(est(g["difference"])), path, loc(sub, m, b, "difference.value"))
                add(p + "DiffCI", ci(g["difference"], signed=True), path, loc(sub, m, b, "difference.bca"))
    return groups


def main_reference():
    path = f"{MAIN}/reference.json"
    groups = reference(path, ("random", "best_of_n", "cem"))
    loc = lambda sub, m, b, *k: f"subsets.{sub}.groups[method={m},budget={b}]." + ".".join(k)
    add("MainInstances", ints(groups[("all", "random", 1000)]["n_paired"]), path, loc("all", "random", 1000, "n_paired"))
    add("MainClusters", ints(groups[("all", "random", 1000)]["n_clusters"]), path, loc("all", "random", 1000, "n_clusters"))
    add("BonInstances", ints(groups[("all", "best_of_n", 1000)]["n_paired"]), path, loc("all", "best_of_n", 1000, "n_paired"))
    add("WellPosedInstances", ints(groups[("in_band", "random", 1000)]["n_paired"]), path, loc("in_band", "random", 1000, "n_paired"))
    add("BootResamples", ints(groups[("all", "random", 1000)]["emulator"]["hackability"]["n_boot"]), path,
        loc("all", "random", 1000, "emulator.hackability.n_boot"))
    lvl = groups[("all", "random", 1000)]["emulator"]["hackability"]["level"]
    add("CILevel", ints(round(lvl * 100)), path, loc("all", "random", 1000, "emulator.hackability.level x 100"))
    rp = src(f"{MAIN}/records.jsonl.gz")
    rows = [json.loads(l) for l in gzip.open(rp, "rt")]
    abr = [r for r in rows if r["method"] == "random" and r["budget"] == 1000 and r["grader_p_fresh"] >= 0.5 and not r["oracle_accept"]]
    add("RandThouAccRejCount", ints(len(abr)), rp, "records: method=random, budget=1000, grader_p_fresh>=0.5, oracle_accept=false")
    return groups


def seeded_reference():
    path = f"{SEEDED}/reference.json"
    groups = reference(path, ("cem_seeded",))
    add("AdInstances", ints(groups[("all", "cem_seeded", 1000)]["n_paired"]), path,
        "subsets.all.groups[method=cem_seeded,budget=1000].n_paired")
    # the schedule (generations x population) and the mutation constants, from the code
    a = T("hpr-dream/hpr_dream/attack.py")
    m = re.search(r"elite_frac: float = (0\.\d+), min_elite: int = 2,\n\s+p_replace: float = (0\.\d+)", a)
    if not m:
        raise Missing("cem_seeded defaults not found in hpr_dream/attack.py")
    add("AdEliteShare", m.group(1), "hpr-dream/hpr_dream/attack.py", "cem_seeded(elite_frac=...)")
    add("AdReplace", m.group(2), "hpr-dream/hpr_dream/attack.py", "cem_seeded(p_replace=...)")
    s10 = re.search(r"10:\s*\((\d+),\s*(\d+)\)", a)
    s100 = re.search(r"100:\s*\((\d+),\s*(\d+)\)", a)
    s1000 = re.search(r"1000:\s*\((\d+),\s*(\d+)\)", a)
    if not (s10 and s100 and s1000):
        raise Missing("CEM_SCHEDULE[10..1000] not found in hpr-dream/hpr_dream/attack.py")
    add("AdSchedule",
        f"{s10.group(1)} of {s10.group(2)}, {s100.group(1)} of {s100.group(2)}, and {s1000.group(1)} of {s1000.group(2)}",
        "hpr-dream/hpr_dream/attack.py", "CEM_SCHEDULE[10, 100, 1000]")
    m = re.search(r"10000: \((\d+), (\d+)\),", a)
    if not m or int(m.group(1)) * int(m.group(2)) != 10000:
        raise Missing("CEM_SCHEDULE[10000] not found in hpr_dream/attack.py")
    add("AdScheduleTop", f"{m.group(1)} of {int(m.group(2)):,}", "hpr-dream/hpr_dream/attack.py",
        "CEM_SCHEDULE[10000] (generations x population)")
    return groups


# ---------------------------------------------------------------------------------------------
# 2. the main checkpoint's card: false rejection on behaviour plans by family; costs
# ---------------------------------------------------------------------------------------------
def main_card():
    path = f"{MAIN}/card.json"
    c = J(path)
    for fam, fw in F_WORD.items():
        r = c["flip_rates_by_task_family"][fam]
        add(fw + "BehFp", f3(r["fp"]), path, f"flip_rates_by_task_family.{fam}.fp")
        add(fw + "BehFn", f3(r["fn"]), path, f"flip_rates_by_task_family.{fam}.fn")
    add("BehPlans", ints(c["counts"]["behaviour_plans"]), path, "counts.behaviour_plans")
    cost = J(f"{MAIN}/costs.json")["summary"]
    cp = f"{MAIN}/costs.json"
    add("MainJudgeMonthSteps", ints(cost["judge_month_steps_computed"]), cp, "summary.judge_month_steps_computed")
    add("MainJudgeHours", f"{cost['judge_seconds'] / 3600:.1f}", cp, "summary.judge_seconds / 3600")
    add("MainEngineReplays", ints(cost["engine_replays"]), cp, "summary.engine_replays")
    add("MainEngineCityMonths", ints(cost["engine_city_months_replayed"]), cp, "summary.engine_city_months_replayed")
    add("MainEngineHours", f"{cost['engine_seconds'] / 3600:.1f}", cp, "summary.engine_seconds / 3600")


# ---------------------------------------------------------------------------------------------
# 3. engine-only references (the perfect emulator under each search; the noise-only floors' check)
# ---------------------------------------------------------------------------------------------
def engine_reference():
    s = f"{ENGREF}/summary.md"
    quote("IdentityGroupsZero", "| identity (nine floor) | engine-identity | 40 | 640 | 0 | 16 of 16 |", s, "16")
    p = f"{ENGREF}/B_economy_volatility/card.json"
    fs = J(p)["floor_summary"]["residual|margin"]
    add("AcceptVolExcl", ints(fs["excludes_zero"]), p, "floor_summary.residual|margin.excludes_zero")
    add("AcceptVolGroups", ints(fs["groups"]), p, "floor_summary.residual|margin.groups")
    p = f"{ENGREF}/B_economy/card.json"
    for row in J(p)["oracle_majority"]:
        if int(row["budget"]) == 1000 and row["scoring"] == "margin":
            add("Perf" + {"cem": "Cem", "random_shooting": "Rand", "best_of_n": "Bon"}[row["attacker"]] + "ThouOrAcc",
                f3(est(row["oracle_accept"])), p, f"oracle_majority[{row['attacker']},margin,1000].oracle_accept.value")


# ---------------------------------------------------------------------------------------------
# 4. tasks, thresholds, families, data, oracle
# ---------------------------------------------------------------------------------------------
def tasks_and_data():
    tp = "data/tasks_v2_H24.json"
    t = J(tp)
    inst = t["instances"]
    add("Instances", ints(len(inst)), tp, "len(instances)")
    add("ExcludedInstances", ints(len(t["meta"]["excluded"])), tp, "len(meta.excluded)")
    add("InstancesPlanned", ints(len(inst) + len(t["meta"]["excluded"])), tp, "len(instances)+len(meta.excluded)")
    wp = sum(1 for r in inst if r.get("well_posed32"))
    add("WellPosed", ints(wp), tp, "count(instances.well_posed32)")
    add("HeldOutFamilies", ints(len({r["family_id"] for r in inst})), tp, "count distinct family_id")
    for fam, fw in F_WORD.items():
        rs = [r for r in inst if r["task"] == fam]
        add(fw + "Count", ints(len(rs)), tp, f"count(task={fam})")
        add(fw + "WellPosed", ints(sum(1 for r in rs if r.get("well_posed32"))), tp, f"count(task={fam}, well_posed32)")
    add("Horizon", ints(t["meta"]["horizon"]), tp, "meta.horizon")
    rp = "results/tasks_v2/report.md"
    for fam, fw in (("grow", "Grow"), ("solvent", "Solv"), ("recover", "Recov"), ("power", "Power"), ("treasury_rev", "Treas")):
        m = re.search(r"^\| %s \| [^|]+ \| (\.\d+) / (\.\d+) / (\.\d+) / (\.\d+) \|" % re.escape(fam), T(rp), re.M)
        if not m:
            raise Missing(f"numbers: base rate row for {fam} not found in {rp}")
        add(fw + "BaseBeh", "0" + m.group(1), rp, f"table 'Majority rule at theta32(0.5)', row {fam}, beh")
        add(fw + "BaseBld", "0" + m.group(4), rp, f"table 'Majority rule at theta32(0.5)', row {fam}, c (builders under best constants)")
    quote("ConstPassGrow", "grow .900, solvent 1.000, treasury 1.000, recover 1.000, power .100", rp, "0.900")
    quote("NineSeedOwnLo", "passes its own primary seed in 75 to 98 per cent", rp, "75")
    add("NineSeedOwnHi", "98", rp, 'text "passes its own primary seed in 75 to 98 per cent"')
    quote("NineSeedOtherLo", "but the other eight seeds only 7 to 11 per cent", rp, "7")
    add("NineSeedOtherHi", "11", rp, 'text "but the other eight seeds only 7 to 11 per cent"')
    quote("ThresholdCityMonths", "8,637,968 replays run (207.3 M city-months", rp, "207.3")
    add("ThresholdReplays", "8,637,968", rp, 'text "8,637,968 replays run"')
    add("ConstantPlans", ints(21 * (5 ** 3)), "code/dc/grammar.py", "21 tax rates (0..20) x 5^3 funding levels")

    dp = "results/data/summary.json"
    d = J(dp)
    g = d["generation"]["train_full"]
    add("TrainTransitions", ints(g["city_months"]), dp, "generation.train_full.city_months")
    add("TrainTrajectories", ints(g["n"]), dp, "generation.train_full.n")
    add("SmallTransitions", ints(d["train_small"]["transitions"]), dp, "train_small.transitions")
    v = d["verify"]
    add("VerifyTrajectories", ints(sum(v[k]["checked"] for k in v)), dp, "sum(verify.*.checked)")
    add("VerifyMismatches", ints(sum(v[k]["mismatched"] for k in v)), dp, "sum(verify.*.mismatched)")
    dd = d["splits"]["train_full"]["counts"]
    hs = sorted(int(k) for k in dd["by_H"])
    add("TrajHorizons", " and ".join(str(x) for k in hs for x in [k]), dp, "splits.train_full.counts.by_H keys")
    add("DisasterTraj", ints(dd["disasters_on_trajectories"]), dp, "splits.train_full.counts.disasters_on_trajectories")

    fp = "results/families/summary.md"
    quote("FamiliesTotal", "100 families, 268 start files", fp, "100")
    add("StartFiles", "268", fp, 'text "100 families, 268 start files"')
    f40 = J("data/families.json")["families"]
    tr_fams = [x for x in f40 if x["split"] == "train"]
    add("TrainFamilies", ints(len(tr_fams)), "data/families.json", "count(families, split == train)")
    add("TrainStarts", ints(sum(len(x["starts"]) for x in tr_fams)), "data/families.json", "sum(len(starts), split == train)")

    hp = "results/oracle/bundled_hashes.npy"
    a = np.load(src(hp))
    add("OracleCities", ints(a.shape[0]), hp, "shape[0]")
    add("OracleMonths", ints(a.shape[1] - 1), hp, "shape[1] - 1 (month boundaries minus the start)")
    sp = "results/oracle/sufficiency/summary.json"
    s = J(sp)
    add("SuffTransitions", ints(s["transitions"]), sp, "transitions")
    add("SuffExact", ints(s["variant_a_all12_identical"]), sp, "variant_a_all12_identical")
    add("SuffNoSprites", ints(s["variant_b_differ_month1"]), sp, "variant_b_differ_month1")
    sr = np.load(src("results/oracle/sufficiency/raw.npz"))
    add("SuffSpriteFree", ints(int((sr["n_sprites"] == 0).sum())),
        "results/oracle/sufficiency/raw.npz", "count(n_sprites == 0)")
    add("SuffRngShift", ints(int((~sr["b_m1"][:, s["fields"].index("rng")]).sum())),
        "results/oracle/sufficiency/raw.npz", "count(~b_m1[:, fields.index('rng')])")
    add("SuffPowMatch", ints(int(sr["b_m1"][:, s["fields"].index("scalar:powered_zones")].sum())),
        "results/oracle/sufficiency/raw.npz", "count(b_m1[:, fields.index('scalar:powered_zones')])")
    add("SuffFundsMatch", ints(int(sr["b_m1"][:, s["fields"].index("scalar:funds")].sum())),
        "results/oracle/sufficiency/raw.npz", "count(b_m1[:, fields.index('scalar:funds')])")
    quote("LedgerEntries", "**Ledger: 27 int64 entries**", "results/oracle/observation_sufficiency.md", "27")


# ---------------------------------------------------------------------------------------------
# 5. short-horizon fidelity on the held-out test split across all converged runs
# ---------------------------------------------------------------------------------------------
TEST_RUNS = ["os_15m_small", "sf_15m_small", "os_15m_full", "sf_15m_full", "os_50m_small", "sf_50m_small",
             "os_50m_full", "sf_50m_full", "os_100m_small", "sf_100m_small", "os_100m_full", "sf_100m_full",
             "os_50m_full_s1", "sf_50m_full_s1", "os_50m_full_s2", "sf_50m_full_s2"]
FINAL = {"os": 6000000, "sf": 1500032}


def test_json(run):
    return LADDER / run / "test" / f"{run}_samples_{FINAL[run[:2]]:09d}_dec-a.json"


def fidelity_test():
    kill = 0.10
    add("KillPop", "0.10", test_json("os_50m_full"), "12-month relative scalar error reference bar (10%)")
    rows = []
    for run in TEST_RUNS:
        p = test_json(run)
        g = J(p)["gap_closed"]
        r = {"run": run, "path": p, "f1": g["tile_F1_1m_structural_T1"]["model"], "floor": g["tile_F1_1m_structural_T1"]["floor"],
             "raw": J(p)["onestep"]["model_T1"]["raw"]["f1"],
             "f1_12": g["tile_F1_since_start_12m_structural"]["model"], "pop12": g["pop_median_rel_12m"]["model"],
             "funds12": g["funds_median_rel_12m"]["model"]}
        r["pass"] = (r["f1"] >= 0.5 * r["floor"]) and (r["pop12"] <= kill) and (r["funds12"] <= kill)
        rows.append(r)
    paths = [r["path"] for r in rows]
    add_multi("TestRuns", ints(len(rows)), paths, "count of final-checkpoint test JSONs (16 runs)")
    add_multi("TestPass", ints(sum(r["pass"] for r in rows)), paths,
              "count(F1_1m >= 0.5 x engine floor and pop_12 <= 0.10 and funds_12 <= 0.10)")
    for k, nm in (("f1", "FOne"), ("pop12", "Pop"), ("funds12", "Funds")):
        add_multi("Test" + nm + "Min", f3(min(r[k] for r in rows)), paths, f"min over the 16 runs of {k}")
        add_multi("Test" + nm + "Max", f3(max(r[k] for r in rows)), paths, f"max over the 16 runs of {k}")
    # R6 m5: the same bar on the ladder's 12 half-trained checkpoints (test_half/, the same evaluation at mid-training)
    half = []
    for run in TEST_RUNS[:12]:
        hp_ = sorted((LADDER / run / "test_half").glob(f"{run}_samples_*_dec-a.json"))
        if len(hp_) != 1:
            raise Missing(f"{run}/test_half: expected one dec-a result, found {len(hp_)}")
        g = J(hp_[0])["gap_closed"]
        r = {"path": hp_[0], "f1": g["tile_F1_1m_structural_T1"]["model"], "floor": g["tile_F1_1m_structural_T1"]["floor"],
             "pop12": g["pop_median_rel_12m"]["model"], "funds12": g["funds_median_rel_12m"]["model"]}
        r["pass"] = (r["f1"] >= 0.5 * r["floor"]) and (r["pop12"] <= kill) and (r["funds12"] <= kill)
        half.append(r)
    hpaths = [r["path"] for r in half]
    add_multi("TestHalfN", ints(len(half)), hpaths, "count of half-trained test JSONs (the ladder's 12 runs)")
    add_multi("TestHalfPass", ints(sum(r["pass"] for r in half)), hpaths,
              "count(F1_1m >= 0.5 x engine floor and pop_12 <= 0.10 and funds_12 <= 0.10), half-trained")
    add_if("TestHalfAllPass", all(r["pass"] for r in half), hpaths[0], "every half-trained checkpoint meets the bar")
    for k, nm in (("f1", "FOne"), ("pop12", "Pop"), ("funds12", "Funds")):
        add_multi("TestHalf" + nm + "Min", f3(min(r[k] for r in half)), hpaths, f"min over the 12 half-trained of {k}")
        add_multi("TestHalf" + nm + "Max", f3(max(r[k] for r in half)), hpaths, f"max over the 12 half-trained of {k}")
    main = test_json("os_50m_full")
    g = J(main)["gap_closed"]
    add("TestMainFOne", f3(g["tile_F1_1m_structural_T1"]["model"]), main, "gap_closed.tile_F1_1m_structural_T1.model")
    add("TestFloorFOne", f3(g["tile_F1_1m_structural_T1"]["floor"]), main, "gap_closed.tile_F1_1m_structural_T1.floor")
    add("TestBarFOne", f3(0.5 * g["tile_F1_1m_structural_T1"]["floor"]), main, "0.5 x gap_closed.tile_F1_1m_structural_T1.floor")
    add("TestMainShareClosed", f2(g["tile_F1_1m_structural_T1"]["share_closed"]), main, "gap_closed.tile_F1_1m_structural_T1.share_closed")
    for k, nm in (("pop_median_rel_12m", "Pop"), ("funds_median_rel_12m", "Funds")):
        add("TestMain" + nm, f3(g[k]["model"]), main, f"gap_closed.{k}.model")
        add("TestFloor" + nm, f3(g[k]["floor"]), main, f"gap_closed.{k}.floor")
        add("TestCopy" + nm, f3(g[k]["copy"]), main, f"gap_closed.{k}.copy")
    add("TestMainFTwelve", f3(g["tile_F1_since_start_12m_structural"]["model"]), main, "gap_closed.tile_F1_since_start_12m_structural.model")
    add("TestFloorFTwelve", f3(g["tile_F1_since_start_12m_structural"]["floor"]), main, "gap_closed.tile_F1_since_start_12m_structural.floor")
    sel = J(main)["selection"]
    add("TestTransitions", ints(sel["n_onestep"]), main, "selection.n_onestep")
    add("TestPlans", ints(sel["n_plans"]), main, "selection.n_plans")
    bl = LADDER / "os_50m_full" / "test" / "baselines.json"
    add("TestNNFOne", f3(J(bl)["nn_sample"]["structural"]["f1"]), bl, "nn_sample.structural.f1")
    # self-forcing against its one-step parent, pair by pair
    by = {r["run"]: r for r in rows}
    pairs = [(o, "sf" + o[2:]) for o in by if o.startswith("os_")]
    add_multi("SfPairs", ints(len(pairs)), paths, "pairs (os_X, sf_X) among the 16 runs")
    add_multi("SfLowerOne", ints(sum(by[s]["f1"] < by[o]["f1"] for o, s in pairs)), paths,
              "count of pairs with self-forced F1_1m below its one-step parent's")
    add_multi("SfLowerTwelve", ints(sum(by[s]["f1_12"] < by[o]["f1_12"] for o, s in pairs)), paths,
              "count of pairs with self-forced F1 since start at 12 months below its one-step parent's")
    add("SfMainFOne", f3(by["sf_50m_full"]["f1"]), by["sf_50m_full"]["path"], "gap_closed.tile_F1_1m_structural_T1.model")
    add("SfMainFTwelve", f3(by["sf_50m_full"]["f1_12"]), by["sf_50m_full"]["path"], "gap_closed.tile_F1_since_start_12m_structural.model")
    return rows


# ---------------------------------------------------------------------------------------------
# 6. oracle patching on the main checkpoint (patching_summary.md, a generated result file)
# ---------------------------------------------------------------------------------------------
CELL = re.compile(r"(\d+)/(\d+) (\d\.\d+) \[(\d\.\d+), (\d\.\d+)\]")
MASK_WORD = {"none": "None", "power": "Power", "treasury": "Treasury", "valves": "Valves", "zone_growth": "ZoneGrowth",
             "pollution": "Pollution", "traffic": "Traffic", "land_value": "LandValue", "crime": "Crime", "fire": "Fire",
             "any global": "AnyGlobal", "any local": "AnyLocal"}
GLOBAL = ["power", "treasury", "valves"]
LOCAL = ["zone_growth", "pollution", "traffic", "land_value", "crime", "fire"]
NICE = {"power": "power", "treasury": "treasury", "valves": "demand valves", "zone_growth": "zone growth",
        "pollution": "pollution", "traffic": "traffic", "land_value": "land value", "crime": "crime", "fire": "fire"}


def _table_after(text, heading):
    i = text.find(heading)
    if i < 0:
        raise Missing(f"heading not found: {heading!r}")
    rows = []
    started = False
    for line in text[i:].splitlines()[1:]:
        if line.startswith("|"):
            started = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            rows.append(cells)
        elif started:
            break
    return rows


def _cell(s):
    m = CELL.fullmatch(s)
    if not m:
        raise Missing(f"patching cell not parsed: {s!r}")
    k, n = int(m.group(1)), int(m.group(2))
    v = float(m.group(3))
    if abs(round(k / n, 2) - v) > 0.0051:
        raise Missing(f"patching cell inconsistent: {s!r}")
    return {"k": k, "n": n, "value": k / n, "lo": float(m.group(4)), "hi": float(m.group(5))}


def patching():
    p = f"{MAIN}/patching_summary.md"
    t = T(p)
    head = "## Primary set: emulator accepts, oracle (majority) rejects"
    m = re.search(r"Records: (\d+) \(distinct plans: (\d+)\); clusters \(held-out families\): (\d+)\.", t[t.find(head):])
    add("PtRecords", ints(m.group(1)), p, "primary set: Records: N")
    add("PtPlans", ints(m.group(2)), p, "primary set: distinct plans")
    add("PtClusters", ints(m.group(3)), p, "primary set: clusters")
    tab = {r[0]: r for r in _table_after(t, head)}
    out = {}
    for mask in list(MASK_WORD) + [f"random~{x}" for x in GLOBAL + LOCAL] + [f"changed~{x}" for x in GLOBAL + LOCAL]:
        r = tab[mask]
        out[mask] = {"all": _cell(r[2]), "ind": _cell(r[3])}
    for mask, w in MASK_WORD.items():
        a, i = out[mask]["all"], out[mask]["ind"]
        add("Pt" + w, f2(a["value"]), p, f"primary set table, row '{mask}', all plans")
        add("Pt" + w + "CI", f"[{f2(a['lo'])}, {f2(a['hi'])}]", p, f"primary set table, row '{mask}', all plans, interval")
        add("Pt" + w + "Ind", f2(i["value"]), p, f"primary set table, row '{mask}', indirect only")
    for x in GLOBAL + LOCAL:
        w = MASK_WORD[x]
        for ctl, cw in (("random", "Size"), ("changed", "Chg")):
            c = out[f"{ctl}~{x}"]["all"]
            add("Pt" + w + cw, f2(c["value"]), p, f"primary set table, row '{ctl}~{x}', all plans")
            add("Pt" + w + cw + "CI", f"[{f2(c['lo'])}, {f2(c['hi'])}]", p, f"primary set table, row '{ctl}~{x}', interval")
    above = [x for x in GLOBAL + LOCAL
             if out[x]["all"]["value"] > max(out[f"random~{x}"]["all"]["value"], out[f"changed~{x}"]["all"]["value"])]
    clear = [x for x in GLOBAL + LOCAL
             if out[x]["all"]["lo"] > max(out[f"random~{x}"]["all"]["hi"], out[f"changed~{x}"]["all"]["hi"])]
    join = lambda xs: "none" if not xs else (NICE[xs[0]] if len(xs) == 1 else ", ".join(NICE[x] for x in xs[:-1]) + " and " + NICE[xs[-1]])
    add("PtAboveBoth", join(above), p, "subsystems whose flip rate exceeds both controls' point estimates (all plans)")
    add("PtClearBoth", join(clear), p, "subsystems whose interval lies wholly above both controls' intervals (all plans)")
    add("PtAboveBothN", ints(len(above)), p, "count of the above")
    # by task family (primary set, all plans): the first such table in the file is the primary set's
    ftab = _table_after(t, "By task family (all plans")
    cols = ftab[0][1:]
    fam_rows = {r[0]: dict(zip(cols, r[1:])) for r in ftab[1:]}
    for mask, fam in (("fire", "recover"), ("power", "power"), ("none", "recover"), ("fire", "treasury"),
                      ("treasury", "treasury"), ("power", "recover")):
        c = _cell(fam_rows[mask][fam])
        w = MASK_WORD[mask] + F_WORD[fam]
        add("Pt" + w, f2(c["value"]), p, f"primary set, by task family, row '{mask}', column '{fam}'")
        add("Pt" + w + "K", ints(c["k"]), p, f"primary set, by task family, row '{mask}', column '{fam}', flips")
        add("Pt" + w + "N", ints(c["n"]), p, f"primary set, by task family, row '{mask}', column '{fam}', records")
    # random-shooting subset at B = 1,000
    dh = "## Decision-rule inputs (random search, B = 1,000, primary set"
    dtab = {r[0]: r for r in _table_after(t, dh)}
    m = re.search(r"Records: (\d+)\.", t[t.find(dh):])
    add("DecRecords", ints(m.group(1)), p, "decision set: Records: N")
    dec = {k: {"all": _cell(r[1]), "ind": _cell(r[2])} for k, r in dtab.items() if k in MASK_WORD}
    for mask, w in MASK_WORD.items():
        a, i = dec[mask]["all"], dec[mask]["ind"]
        add("Dec" + w, f2(a["value"]), p, f"decision set table, row '{mask}', all plans")
        add("Dec" + w + "CI", f"[{f2(a['lo'])}, {f2(a['hi'])}]", p, f"decision set table, row '{mask}', all plans, interval")
        add("Dec" + w + "Ind", f2(i["value"]), p, f"decision set table, row '{mask}', indirect only")
    bar_g, bar_l = 0.60, 0.30
    mr_pc = J("results/analysis/patching_controls.json")["part1"]["mechanism_rule"]
    add("MechGlobalBar", f"{mr_pc['global_bar']:.2f}", "results/analysis/patching_controls.json", "part1.mechanism_rule.global_bar")
    add("MechLocalBar", f"{mr_pc['local_bar']:.2f}", "results/analysis/patching_controls.json", "part1.mechanism_rule.local_bar")

    def verdict(kind):
        gl = [dec[x][kind] for x in GLOBAL]
        lc = [dec[x][kind] for x in LOCAL]
        reach = any(g["value"] >= bar_g and g["lo"] > bar_l for g in gl)
        if reach and all(l["value"] < bar_l for l in lc):
            return "supported"
        if dec["any local"][kind]["value"] > dec["any global"][kind]["value"] or not reach:
            return "falsified"
        return "undecided"
    va, vi = verdict("all"), verdict("ind")
    add("MechVerdictAll", va, p, "subsystem flip summary on random-search set, all plans")
    add("MechVerdictInd", vi, p, "subsystem flip summary on random-search set, indirect pairs")
    add("MechVerdict", "supported" if va == vi == "supported" else "not supported", p,
        "supported only if both readings are supported (script)")
    high = sorted([x for x in LOCAL if dec[x]["all"]["value"] >= bar_l], key=lambda x: -dec[x]["all"]["value"])
    add("DecLocalAbove", ", ".join(f"{NICE[x]} {f2(dec[x]['all']['value'])}" for x in high), p,
        "local rules at or above 0.30 on the decision set, all plans, k/n")
    add("DecLocalAboveN", ints(len(high)), p, "count of the above")
    return out, dec


# ---------------------------------------------------------------------------------------------
# 7. reinforcement learning inside the emulator (runs scored on the engine at home)
# ---------------------------------------------------------------------------------------------
RL_SNAPS = {"Qtr": 250000, "Half": 500000, "Full": 1000000}
CKPT_NICE = {"os": "one-step", "sf": "pushforward"}      # the paper's name for the fine-tuned objective (R2 M4)


def ckpt_words(ck):
    run, samples = ck.split("-samples_")
    obj, size, scale = run.split("_")[:3]
    stage = "final" if int(samples) in (6000000, 1500032) else "half-trained"
    return f"{stage} {CKPT_NICE[obj]} {size.upper()} {scale}-data"


LADDER_RUN = re.compile(r"(os|sf)_\d+m_(full|small)")   # the 24-checkpoint ladder (as analyse_ladder.py); not the
                                                         # coverage model, the ensemble members or pilots


def rl_runs(snap):
    """The ladder's RL runs at one snapshot (the coverage model's runs are read in coverage())."""
    fs = sorted(glob.glob(str(REPO / f"results/rl/*__tasks_v2_H24/eval3_{snap:09d}.summary.json")))
    fs = [f for f in fs if not Path(f).parent.name.startswith("engine")]
    runs = []
    for f in fs:
        ck, fam, seed, _ = Path(f).parent.name.split("__")
        if not LADDER_RUN.fullmatch(ck.split("-samples_")[0]):
            continue
        runs.append({"ck": ck, "fam": fam, "seed": seed, "path": f, **J(f)})
    return runs


RLX = "results/analysis/rl_axis.json"


def rlx(block, snap, scope, q, sub=None):
    r = J(RLX)["results"][block][str(snap)]
    r = r[sub] if sub else r
    return r[scope][q]


def twci(x, signed=False):
    return ci({"value": x["value"], "lo": x["twoway"]["lo"], "hi": x["twoway"]["hi"]}, signed=signed)


def words_list(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def rl_arm():
    full = rl_runs(RL_SNAPS["Full"])
    per = {}
    for r in full:
        per.setdefault(r["ck"], []).append(r)
    complete = sorted(c for c, rs in per.items() if len(rs) == 15 and {x["fam"] for x in rs} == set(FAMS))
    keep = lambda rs: [r for r in rs if r["ck"] in complete]
    full = keep(full)
    paths = [r["path"] for r in full]
    add_multi("RlRunsDone", ints(len(full)), paths, "runs of the complete checkpoints (15 runs each) at 1,000,000 months")
    add_multi("RlCkptsDone", ints(len(complete)), paths, "checkpoints with all 15 runs (5 families x 3 seeds)")
    sizes = sorted({c.split("_")[1] for c in complete}, key=lambda s: int(s[:-1]))
    eps = {r["n_episodes_per_instance"] for r in full}
    if len(eps) != 1:
        raise Missing(f"RL runs disagree on episodes per instance: {eps}")
    add_multi("RlEpisodes", ints(eps.pop()), paths, "n_episodes_per_instance (equal in every run)")
    add_multi("RlSizes", words_list(s.upper() for s in sizes), paths, "sizes among the complete checkpoints")

    def boot(vals, clusters):
        return HS.conditional_mean(np.asarray(vals, float), None, np.asarray(clusters), bca=True).as_dict()

    def put(prefix, rs, sources, label, snap, scope):
        cl = [r["ck"] for r in rs]
        d = boot([r["rate_dream_accept"] for r in rs], cl)
        o = boot([r["rate_engine_open_accept"] for r in rs], cl)
        g = boot([r["rate_dream_accept"] - r["rate_engine_open_accept"] for r in rs], cl)
        c = boot([r["rate_engine_closed_accept"] for r in rs], cl)
        m = boot([r["inflation_open"] for r in rs], cl)
        # every RL interval is the two-way one (checkpoints and cities resampled independently: rl_axis.json, decision
        # 79 point 5); its point value must equal the one computed here from the runs' summaries
        tw = {}
        for q, e in (("dream", d), ("oracle", o), ("gap", g), ("infl", m), ("closed", c)):
            x = rlx("ladder", snap, scope, q)
            if abs(x["value"] - e["value"]) > 1e-9:
                raise Missing(f"{RLX}: ladder {snap} {scope} {q} {x['value']} against the runs' {e['value']}")
            tw[q] = {"value": x["value"], "lo": x["twoway"]["lo"], "hi": x["twoway"]["hi"]}
        loc = f"{label}: mean over runs; interval two-way (checkpoints x cities, percentile) from {RLX} ladder.{snap}.{scope}"
        srcs = list(sources) + [RLX]
        add_multi(prefix + "Dream", f3(d["value"]), srcs, loc + ", dream")
        add_multi(prefix + "DreamCI", ci(tw["dream"]), srcs, loc + ", dream")
        add_multi(prefix + "Oracle", f3(o["value"]), srcs, loc + ", oracle")
        add_multi(prefix + "OracleCI", ci(tw["oracle"]), srcs, loc + ", oracle")
        add_multi(prefix + "Gap", s3(g["value"]), srcs, loc + ", gap")
        add_multi(prefix + "GapCI", ci(tw["gap"], signed=True), srcs, loc + ", gap")
        add_multi(prefix + "Closed", f3(c["value"]), srcs, loc + ", closed")
        add_multi(prefix + "ClosedCI", ci(tw["closed"]), srcs, loc + ", closed")
        add_multi(prefix + "Infl", s3(m["value"]), srcs, loc + ", infl")
        add_multi(prefix + "InflCI", ci(tw["infl"], signed=True), srcs, loc + ", infl")
        return d, o, g

    out = {"Full": put("Rl", full, paths, "1,000,000 months, every run", RL_SNAPS["Full"], "all")}
    for fam, fw in F_WORD.items():
        rs = [r for r in full if r["fam"] == fam]
        out[fam] = put("Rl" + fw, rs, [r["path"] for r in rs], f"1,000,000 months, {fam}", RL_SNAPS["Full"], fam)
    for tag in ("Qtr", "Half"):
        rs = keep(rl_runs(RL_SNAPS[tag]))
        if len(rs) != len(full):
            raise Missing(f"RL snapshot {tag}: {len(rs)} runs against {len(full)} at the end")
        out[tag] = put("Rl" + tag, rs, [r["path"] for r in rs], f"{RL_SNAPS[tag]:,} months, every run", RL_SNAPS[tag], "all")
    # well-posed instances
    wd = np.mean([r["rate_dream_accept_in_band"] for r in full])
    wo = np.mean([r["rate_engine_open_accept_in_band"] for r in full])
    add_multi("RlDreamWP", f3(wd), paths, "mean over runs of rate_dream_accept_in_band")
    add_multi("RlOracleWP", f3(wo), paths, "mean over runs of rate_engine_open_accept_in_band")
    # per checkpoint: the spread of the gap
    gaps = {c: np.mean([r["rate_dream_accept"] - r["rate_engine_open_accept"] for r in full if r["ck"] == c]) for c in complete}
    lo, hi = min(gaps, key=gaps.get), max(gaps, key=gaps.get)
    add_multi("RlGapMin", s3(gaps[lo]), paths, f"min over checkpoints of the mean gap ({lo})")
    add_multi("RlGapMinCkpt", ckpt_words(lo), paths, f"checkpoint of the minimum ({lo})")
    add_multi("RlGapMax", s3(gaps[hi]), paths, f"max over checkpoints of the mean gap ({hi})")
    add_multi("RlGapMaxCkpt", ckpt_words(hi), paths, f"checkpoint of the maximum ({hi})")
    mc = "os_50m_full-samples_006000000"
    if mc in complete:
        rs = [r for r in full if r["ck"] == mc]
        add_multi("RlMainDream", f3(np.mean([r["rate_dream_accept"] for r in rs])), [r["path"] for r in rs], "main checkpoint: mean rate_dream_accept")
        add_multi("RlMainOracle", f3(np.mean([r["rate_engine_open_accept"] for r in rs])), [r["path"] for r in rs], "main checkpoint: mean rate_engine_open_accept")
    # the same learner trained on the engine itself: the RL arm's perfect-emulator reference
    pt = "results/rl/bc/decision_table_pooled.json"
    fams = J(pt)["families"]
    eng = {}
    for tag, snap in RL_SNAPS.items():
        per_f = {}
        for fam in FAMS:
            runs = fams[fam]["scratch_run"].split("+")
            vals = [J(f"results/rl/{r}/eval3_{snap:09d}.summary.json")["rate_engine_open_accept"] for r in runs]
            per_f[fam] = (float(np.mean(vals)), len(runs))
        eng[tag] = per_f
        srcs = [f"results/rl/{r}/eval3_{snap:09d}.summary.json" for fam in FAMS for r in fams[fam]["scratch_run"].split("+")]
        add_multi("RlEng" + tag, f3(np.mean([v for v, _ in per_f.values()])), [pt] + srcs,
                  f"engine-trained learner (decision_table_pooled.json scratch runs): mean over families of the mean over seeds, rate_engine_open_accept at {snap:,}")
    for fam, fw in F_WORD.items():
        v, n = eng["Full"][fam]
        add("RlEng" + fw, f3(v), pt, f"families.{fam}.scratch (mean over {n} seed(s); equals the per-seed summaries' rate_engine_open_accept)")
        if abs(v - fams[fam]["scratch"]) > 1e-9:
            raise Missing(f"engine-trained {fam}: summaries {v} against the pooled table {fams[fam]['scratch']}")
    for tag in RL_SNAPS:
        lost = np.mean([v for v, _ in eng[tag].values()]) - out[tag][1]["value"]
        add_multi("RlLost" + tag, f3(lost), [pt], f"RlEng{tag} minus Rl{tag if tag != 'Full' else ''}Oracle (mean over families minus mean over runs)")
    seeds = sorted({n for _, n in eng["Full"].values()})
    add("RlEngSeeds", " or ".join(str(s) for s in seeds), pt, "seeds per family of the engine-trained learner")
    # the acceptance gap's perfect-emulator reference (R1 F2, R2 M1): the engine-trained learner's own episodes are
    # played on the engine, so its closed-loop pass rate is its "dream"; the gap is closed-loop pass minus the oracle's
    # open-loop acceptance of the same action logs, aggregated as RlEngFull is (mean over families of the seed mean)
    gref = {}
    for fam, fw in F_WORD.items():
        runs = fams[fam]["scratch_run"].split("+")
        ss = [J(f"results/rl/{r}/eval3_{RL_SNAPS['Full']:09d}.summary.json") for r in runs]
        if any(x.get("rate_dream_accept") is not None or x.get("emulator") is not None for x in ss):
            raise Missing(f"engine-trained {fam}: a run has an emulator")
        cl = float(np.mean([x["rate_engine_closed_accept"] for x in ss]))
        gref[fam] = cl - eng["Full"][fam][0]
        srcs = [f"results/rl/{r}/eval3_{RL_SNAPS['Full']:09d}.summary.json" for r in runs]
        add_multi("RlEng" + fw + "Closed", f3(cl), srcs, "mean over seeds of rate_engine_closed_accept (engine-trained)")
        add_multi("RlEng" + fw + "Gap", s3(gref[fam]), srcs, "mean over seeds of closed-loop pass minus open-loop oracle acceptance (engine-trained)")
        add_multi("Rl" + fw + "GapExcess", s3(out[fam][2]["value"] - gref[fam]), srcs,
                  f"Rl{fw}Gap minus RlEng{fw}Gap (point estimates)")
    allsrc = [pt]
    add_multi("RlEngGap", s3(np.mean(list(gref.values()))), allsrc, "mean over families of RlEng<F>Gap")
    add_multi("RlEngClosed", f3(np.mean([eng["Full"][f][0] + gref[f] for f in FAMS])), allsrc, "mean over families of RlEng<F>Closed")
    add_multi("RlGapExcess", s3(out["Full"][2]["value"] - np.mean(list(gref.values()))), allsrc, "RlGap minus RlEngGap (point estimates)")
    rl_axis_macros(gref, out)
    return out, eng, full, complete


def rl_axis_macros(gref, out):
    """The RL point in the audit's unit beside its perfect-emulator value, and the acceptance gap beside its reference
    (results/analysis/rl_axis.json; two-way intervals for the ladder, city intervals for one checkpoint)."""
    F = RL_SNAPS["Full"]
    loc = lambda *k: f"results.{'.'.join(str(x) for x in k)} (value; twoway lo/hi)"
    for scope, w in [("all", "")] + [(f, F_WORD[f]) for f in FAMS]:
        for q, nm in (("fa0", "AxHack"), ("perfect_fa0", "AxPerfHack"), ("excess0", "AxExcess"), ("emu_accept0", "AxAcc"),
                      ("perfect_accept0", "AxPerfAcc"), ("oracle_accept0", "AxOrAcc")):
            x = rlx("ladder", F, scope, q)
            sg = q == "excess0"
            add(f"Rl{w}{nm}", (s3 if sg else f3)(x["value"]), RLX, loc("ladder", F, scope, q))
            add(f"Rl{w}{nm}CI", twci(x, signed=sg), RLX, loc("ladder", F, scope, q))
        # the engine-trained learner: reference gap and inflation
        g = rlx("engine", F, scope, "gap_ref")
        if abs(g["value"] - (np.mean(list(gref.values())) if scope == "all" else gref[scope])) > 1e-9:
            raise Missing(f"{RLX}: engine gap_ref {scope} differs from the runs' summaries")
        add(f"RlEng{w}GapCI", twci(g, signed=True), RLX, loc("engine", F, scope, "gap_ref") + ", city resampling")
        ir = rlx("engine", F, scope, "infl_ref")
        add(f"RlEng{w}Infl", s3(ir["value"]), RLX, loc("engine", F, scope, "infl_ref"))
        add(f"RlEng{w}InflCI", twci(ir, signed=True), RLX, loc("engine", F, scope, "infl_ref"))
        # the excess of the emulator-trained gap and inflation over the reference
        for q, nm in (("gap", "GapExcess"), ("infl", "InflExcess")):
            x = rlx("excess", F, scope, q, sub="ladder")
            if q == "gap" and abs(x["value"] - (out["Full"][2]["value"] - np.mean(list(gref.values())) if scope == "all"
                                                 else out[scope][2]["value"] - gref[scope])) > 1e-9:
                raise Missing(f"{RLX}: excess gap {scope} differs from the paper's own difference")
            if q == "infl":
                add(f"Rl{w}{nm}", s3(x["value"]), RLX, loc("excess", F, "ladder", scope, q))
            add(f"Rl{w}{nm}CI", twci(x, signed=True), RLX, loc("excess", F, "ladder", scope, q))
        lo_ = rlx("lost", F, scope, "closed", sub="ladder")
        add(f"Rl{w}LostClosed", f3(lo_["value"]), RLX, loc("lost", F, "ladder", scope, "closed"))  # unsigned: "short of"
        add(f"Rl{w}LostClosedCI", twci(lo_), RLX, loc("lost", F, "ladder", scope, "closed"))
    lf = rlx("lost", F, "all", "open", sub="ladder")
    if abs(lf["value"] - float(J(RLX)["results"]["lost"][str(F)]["ladder"]["all"]["open"]["value"])) > 1e-12:
        raise Missing("lost")
    add("RlLostFullCI", twci(lf), RLX, loc("lost", F, "ladder", "all", "open"))  # unsigned, as its value (R4 m8)
    # the main checkpoint (15 runs; city intervals)
    for q, nm in (("fa0", "AxHack"), ("perfect_fa0", "AxPerfHack"), ("excess0", "AxExcess")):
        x = rlx("main", F, "all", q)
        add(f"RlMain{nm}", (s3 if q == "excess0" else f3)(x["value"]), RLX, loc("main", F, "all", q))
        add(f"RlMain{nm}CI", twci(x, signed=q == "excess0"), RLX, loc("main", F, "all", q) + ", city resampling")
    for sub, w in (("main", "Main"), ("coverage", "Cov")):
        for scope, fw in [("all", "")] + [(f, F_WORD[f]) for f in FAMS]:
            x = rlx("excess", F, scope, "gap", sub=sub)
            add(f"CovRl{fw}{w}GapExcess", s3(x["value"]), RLX, loc("excess", F, sub, scope, "gap"))
            add(f"CovRl{fw}{w}GapExcessCI", twci(x, signed=True), RLX, loc("excess", F, sub, scope, "gap") + ", city resampling")
    for scope, fw in [("all", "")] + [(f, F_WORD[f]) for f in FAMS]:
        x = J(RLX)["results"]["coverage_excess"][str(F)][scope]["gap"]
        add(f"CovRl{fw}GapDiff", s3(x["value"]), RLX, loc("coverage_excess", F, scope, "gap"))
        add(f"CovRl{fw}GapDiffCI", twci(x, signed=True), RLX, loc("coverage_excess", F, scope, "gap") + ", city resampling")
    fx = J(RLX)["engine_reference_facts"]
    spf = fx["seeds_per_family"]
    one = [f for f in FAMS if spf[f] == 1]
    add("RlEngOneSeedFams", words_list([f"\\emph{{{f}}}" for f in one]), RLX, "engine_reference_facts.seeds_per_family == 1")
    expect(sorted(set(spf.values())) == [1, 3], "the reference has one or three seeds per family")
    ex = {f: rlx("excess", F, f, "gap", sub="ladder")["value"] for f in FAMS}
    expect(sorted(ex, key=ex.get)[-2:] == ["treasury", "recover"] or sorted(ex, key=ex.get)[-2:] == ["recover", "treasury"],
           "reinforcement learning's overstatement beyond its reference is largest on recover and treasury")



# ---------------------------------------------------------------------------------------------
# 8. the defence frontier (results/defences/frontier.json)
# ---------------------------------------------------------------------------------------------
def defences():
    p = "results/defences/frontier.json"
    d = J(p)
    add("DefInstances", ints(d["n_instances"]), p, "n_instances")
    add("DefFamilies", ints(d["n_families"]), p, "n_families")
    rows = {r["setting"]: r for r in d["frontier"]["random"]["rows"]}
    for s, w in (("perfect", "Perf"), ("ensemble", "Ens"), ("member0", "Member")):
        r = rows[s]
        add("Def" + w + "Hack", f3(est(r["hackability"])), p, f"frontier.random.rows[{s}].hackability.value")
        add("Def" + w + "HackCI", ci(r["hackability"]), p, f"frontier.random.rows[{s}].hackability.bca")
        add("Def" + w + "FalseRej", f3(est(r["false_rejection"])), p, f"frontier.random.rows[{s}].false_rejection.value")
        add("Def" + w + "FalseRejCI", ci(r["false_rejection"]), p, f"frontier.random.rows[{s}].false_rejection.bca")
    tested = [r for s, r in rows.items() if "hackability_minus_ensemble" in r and r.get("complete") and s != "member0"]
    add("DefTestedN", ints(len(tested)), p, "defended settings (every row with a paired difference from the undefended ensemble except member 0 undefended)")
    # each defence beside its own undefended model (R2 M2, minor 3; R1 m11): the ensemble's settings carry a paired
    # interval against the undefended ensemble; the member-0 settings have only point changes against member 0
    ens = [r for r in tested if r["judge"] == "ensemble"]
    mem = [r for r in tested if r["judge"] == "member0"]
    add("DefEnsTestedN", ints(len(ens)), p, "defended settings judged by the ensemble")
    add("DefMemTestedN", ints(len(mem)), p, "defended settings judged by member 0 alone")
    sig = [r for r in ens if r["hackability_minus_ensemble"]["bca_hi"] < 0]
    add("DefSigN", ints(len(sig)), p, "ensemble settings whose paired difference from the undefended ensemble has a BCa interval below 0")
    mz = est(rows["member0"]["hackability"])
    md = [est(r["hackability"]) - mz for r in mem]
    add("DefMemDiffMin", s3(min(md)), p, "member-0 settings: false acceptance minus member 0 undefended (point), minimum")
    add("DefMemDiffMax", s3(max(md)), p, "member-0 settings: the same, maximum")
    mfr = [est(r["false_rejection"]) - est(rows["member0"]["false_rejection"]) for r in mem]
    add("DefMemFrMin", s3(min(mfr)), p, "member-0 settings: false rejection minus member 0 undefended, minimum")
    add("DefMemFrMax", s3(max(mfr)), p, "member-0 settings: the same, maximum")
    fr = [est(r["false_rejection"]) for r in sig]
    add("DefSigFalseRejMin", f3(min(fr)), p, "min false_rejection.value over those rows")
    add("DefSigFalseRejMax", f3(max(fr)), p, "max false_rejection.value over those rows")
    for s, w in (("penalty2", "PenTwo"), ("detector0.2", "DetLow"), ("deflation-ensemble", "Defl")):
        r = rows[s]
        add("Def" + w + "Hack", f3(est(r["hackability"])), p, f"frontier.random.rows[{s}].hackability.value")
        add("Def" + w + "FalseRej", f3(est(r["false_rejection"])), p, f"frontier.random.rows[{s}].false_rejection.value")
    folds = d["detector"]["folds"]
    aucs = [folds[f][k]["auc_other_fold"]["value"] for f in folds for k in ("search", "verdict") if k in folds[f]]
    add("DetAucMin", f3(min(aucs)), p, "min over folds and feature sets of detector.folds.*.*.auc_other_fold.value")
    add("DetAucMax", f3(max(aucs)), p, "max of the same")
    sa = d["detector"]["selected_plans_auc"]["random"]
    add("DetSelAuc", f3(sa["value"]), p, "detector.selected_plans_auc.random.value")
    add("DetSelAucCI", ci(sa), p, "detector.selected_plans_auc.random.bca")
    de = d["design"]
    lst = lambda xs, fmt: ", ".join(fmt(x) for x in xs[:-1]) + " and " + fmt(xs[-1]) if len(xs) > 1 else fmt(xs[0])
    num = lambda x: (f"{x:g}")
    add("DefMembers", ints(len(de["members"])), p, "len(design.members)")
    add("DefTemps", lst(de["temperatures"], num), p, "design.temperatures")
    add("DefLambdas", lst(de["lambdas"], num), p, "design.lambdas")
    add("DefHalts", lst(de["halt_percentiles"], lambda x: f"{x:g}th"), p, "design.halt_percentiles")
    add("DefDetThresh", lst(de["detector_thresholds"], num), p, "design.detector_thresholds")
    add("DefBudget", ints(de["budget"]), p, "design.budget")
    add("DefDetFolds", ints(len(d["detector"]["folds"])), p, "len(detector.folds)")
    seeded_done = [r for r in d["frontier"]["cem_seeded"]["rows"] if r.get("complete") and r["setting"] != "perfect"]
    add("DefSeededDone", ints(len(seeded_done)), p, "complete defended rows under the seeded search")
    return d


# ---------------------------------------------------------------------------------------------
# 9. the treasury identity on selected plans (secondary claim; appendix)
# ---------------------------------------------------------------------------------------------
def treasury_identity():
    p = f"{MAIN}/treasury_identity.md"
    t = T(p)

    def row(label):
        m = re.search(r"^\| %s \| (\d+) \| \d+ \| [^|]+ \| (\d+/\d+ \d\.\d+ \[\d\.\d+, \d\.\d+\]) \|" % re.escape(label), t, re.M)
        if not m:
            raise Missing(f"treasury identity row not found: {label}")
        return _cell(m.group(2))
    add("TrBeh", f2(row("behaviour plans")["value"]), p, "row 'behaviour plans', B: > 5%")
    for b in (1, 10, 100, 1000):
        a = row(f"selected: random B={b}, emulator accepts")
        add("TrRand" + B_WORD[b], f2(a["value"]), p, f"row 'selected: random B={b}, emulator accepts', B: > 5%")
    r = row("selected: random B=1000, emulator rejects")
    add("TrRandThouRej", f2(r["value"]), p, "row 'selected: random B=1000, emulator rejects', B: > 5%")
    for b in (1, 1000):
        a = row(f"selected: best_of_n B={b}, emulator accepts")
        add("TrBon" + B_WORD[b], f2(a["value"]), p, f"row 'selected: best_of_n B={b}, emulator accepts', B: > 5%")
    quote("BreachShare", "B: > 5%", p, "5")


# ---------------------------------------------------------------------------------------------
# 10. external check, RL learner selection, emulator parameters, Figure 1
# ---------------------------------------------------------------------------------------------
def gallery():
    """The gallery figures : every number of their captions and of the rule's appendix paragraph, from the
    figures' own JSON sidecars, checked against the macros the rest of the paper uses for the same quantities."""
    gj, hj = "paper/figures/fig_gallery.json", "paper/figures/fig_heatmaps.json"
    G = J(gj)
    words = {1: "one", 2: "two", 3: "three", 4: "four", 15: "fifteen"}
    n = int(G["n_pairs"])
    add("GalPairs", ints(n), gj, "n_pairs")
    add("GalPairsWord", words.get(n, ints(n)).capitalize(), gj, "n_pairs (as a word, sentence-initial)")
    add("GalSamples", ints(G["emulator_samples"]), gj, "emulator_samples")
    if int(G["oracle_seeds"]) != 32:
        raise Missing(f"{gj}: oracle_seeds {G['oracle_seeds']}, the paper's oracle uses 32")
    add("GalCrop", ints(G["crop_side_tiles"]), gj, "crop_side_tiles")
    tot = int(G["n_accepted_but_rejected_total"])
    add("GalTotal", ints(tot), gj, "n_accepted_but_rejected_total")
    for f in FAMS:
        add(f"Gal{F_WORD[f]}N", ints(G["n_accepted_but_rejected_by_family"][f]), gj, f"n_accepted_but_rejected_by_family.{f}")
    shown = G["n_shown_by_family"]
    add("GalGrowShownWord", words.get(int(shown["grow"]), ints(shown["grow"])), gj, "n_shown_by_family.grow (as a word)")
    add("GalSolvShownWord", words.get(int(shown["solvent"]), ints(shown["solvent"])), gj, "n_shown_by_family.solvent (as a word)")
    per = max(int(v) for v in shown.values())
    add("GalPerFamWord", words.get(per, ints(per)), gj, "the most plans shown for one family (the rule's per-family count, as a word)")
    if sum(int(v) for v in shown.values()) != n:
        raise Missing(f"{gj}: n_shown_by_family does not sum to n_pairs")
    add("GalFreshMin", ints(G["fresh_emulator_passing_min"]), gj, "fresh_emulator_passing_min")
    add("GalFreshMax", ints(G["fresh_emulator_passing_max"]), gj, "fresh_emulator_passing_max")
    add("GalCropMedian", f"{100 * float(G['crop_share_of_differing_tiles_median']):.0f}", gj, "crop_share_of_differing_tiles_median x 100")
    add("GalCropMin", f"{100 * float(G['crop_share_of_differing_tiles_min']):.0f}", gj, "crop_share_of_differing_tiles_min x 100")
    add_if("GalAllPass", int(G["n_shown_samples_not_passing"]) == 0, gj, "n_shown_samples_not_passing == 0")
    H = J(hj)
    add("HeatSamples", ints(H["emulator_samples"]), hj, "emulator_samples")
    add("HeatSeeds", ints(H["extra_engine_seeds"]), hj, "extra_engine_seeds")
    if int(H["n_plans"]) != n:
        raise Missing(f"{hj}: n_plans {H['n_plans']} is not the gallery's {n}")


def misc():
    for task, tw in (("cheetah-run", "Cheetah"), ("walker-walk", "Walker")):
        p = f"cards/external/{task}.json"
        c = J(p)

        def grp(att, sc, b):
            for r in c["hackability_curve"] + c.get("verdict_scored_curve", []):
                if r["attacker"] == att and r["scoring"] == sc and int(r["budget"]) == b:
                    return r
            raise Missing(f"{p}: no group {att} {sc} {b}")
        r = grp("random_shooting", "margin", 1000)
        add(tw + "RandThouHack", f3(est(r["hackability"])), p, "hackability_curve[random_shooting,margin,1000].hackability.value")
        add(tw + "RandThouHackCI", ci(r["hackability"]), p, "hackability_curve[random_shooting,margin,1000].hackability.bca")
        mp = [r for r in c["hackability_curve"] if r["attacker"] == "tdmpc2_mppi"]
        if mp:
            add(tw + "MppiHack", f3(est(mp[0]["hackability"])), p, "hackability_curve[tdmpc2_mppi].hackability.value")
            add(tw + "MppiB", ints(mp[0]["budget"]), p, "hackability_curve[tdmpc2_mppi].budget")
        add(tw + "Fp", f3(est(c["flip_rates"]["fp"])), p, "flip_rates.fp.value")
    es = "results/external/summary.md"
    quote("ExtStarts", "Starts 20; attacker seeds per start 3", es, "20")
    quote("ExtOracleTolerance", "oracle_tolerance=0", es, "0")
    quote("HopperZeroStarts", "Starts at which every one of the 2,000 behaviour-plan returns is exactly 0: 18 of 20", es, "18")
    c = J("cards/external/cheetah-run.json")
    add("ExtHorizon", ints(c["meta"]["horizon"]), "cards/external/cheetah-run.json", "meta.horizon")

    pr = "results/perf/report.md"
    quote("FastFiftyBefore", "50M 1,522→2,048 (×1.35)", pr, "1,522")
    add("FastFiftyAfter", "2,048", pr, 'text "50M 1,522→2,048 (×1.35)"')

    rl = "results/rl/bc/decision_table_pooled.json"
    r = J(rl)
    for fam, fw in F_WORD.items():
        f = r["families"][fam]
        add("RlHybridDiff" + fw, s3(f["paired"]["mean"]), rl, f"families.{fam}.paired.mean")
        add("RlHybridDiff" + fw + "CI", f"[{s3(f['paired']['lo'])}, {s3(f['paired']['hi'])}]", rl, f"families.{fam}.paired.lo/hi")
        add("RlBld" + fw, f3(f["yardsticks"]["c"]), rl, f"families.{fam}.yardsticks.c")
    add("RlHybridAbove", ints(r["rule"]["interval_above_zero"]), rl, "rule.interval_above_zero")

    pc = "paper/data/param_counts.json"
    p = J(pc)
    for size, w in (("15m", "Fifteen"), ("50m", "Fifty"), ("100m", "Hundred")):
        add("Params" + w, f"{p[size]['elements_float_excl_norm_buffers'] / 1e6:.1f}", pc, f"{size}.elements_float_excl_norm_buffers / 1e6")

    f1 = "paper/figures/fig1_environment.json"
    f = J(f1)
    for k, nm in (("emulator_samples", "FigOneK"), ("emulator_samples_passing", "FigOneEmuPass"),
                  ("emulator_samples_losing_plant_at_drop", "FigOneEmuLose"),
                  ("emulator_samples_losing_plant_and_passing", "FigOneEmuLosePass"),
                  ("engine_seeds_passing", "FigOneEngPass"), ("plant_drop_month", "FigOneDropMonth"),
                  ("engine_zones_off_grid_seed0_end", "FigOneEngOff"), ("engine_zones_seed0_end", "FigOneEngZones"),
                  ("patch_power_passing", "FigOnePatchPower"), ("patch_none_passing", "FigOnePatchNone"),
                  ("patch_other_min_passing", "FigOnePatchOtherMin"), ("patch_samples", "FigOnePatchK"),
                  ("audit_emulator_passing", "FigOneAuditPass"), ("shown_sample_zones_off_grid_end", "FigOneEmuOff")):
        add(nm, ints(f[k]), f1, k)


# ---------------------------------------------------------------------------------------------
# 11. experimental design constants (checked against code, manifests, and analysis JSONs)
# ---------------------------------------------------------------------------------------------
def design_constants():
    mc_pw = J(MC)["results"]["power"]
    add("MainRhoBar", "0.4", MC, "results.power: target Spearman effect size 0.4")
    add("PowerPairs", ints(mc_pw["n_independent_for_80_per_cent"]), MC, "results.power.n_independent_for_80_per_cent")
    add("PowerLevel", "80", MC, "results.power.n_independent_for_80_per_cent (80% power)")
    iccs = sorted(mc_pw["at_icc"].keys())
    add("IccLow", iccs[0], MC, "results.power.at_icc keys[0]")
    add("IccHigh", iccs[1], MC, "results.power.at_icc keys[1]")
    add("PairsPlanned", ints(mc_pw["n_pairs"]), MC, "results.power.n_pairs")
    add("ClustersPlanned", ints(mc_pw["n_clusters"]), MC, "results.power.n_clusters")
    add("FidBar", "0.3", MC, "fidelity-correlation equivalence threshold |Spearman| < 0.3")
    quote("OracleSeeds", "ORACLE_N = 32", "code/dc/tasks.py", "32")
    quote("KSearch", "K_SEARCH = 2", "code/dc/audit.py", "2")
    quote("KVerdict", "K_VERDICT = 8", "code/dc/audit.py", "8")
    add("RlMonths", "$10^{6}$", RLX, "1,000,000 imagined months per PPO run")
    add("Ladder", ints(mc_pw["n_clusters"]), MC, "results.power.n_clusters (24 checkpoints)")
    add("RlRuns", ints(mc_pw["n_pairs"] * 3), RLX, "120 checkpoint-family pairs x 3 seeds")
    add("SizeS", "15M", "paper/data/param_counts.json", "model size tier 15m")
    add("SizeM", "50M", "paper/data/param_counts.json", "model size tier 50m")
    add("SizeL", "100M", "paper/data/param_counts.json", "model size tier 100m")
    add("TenThouInstances", "40", PA, "core 40-city subset count")


def design():
    quote("HaDream", "David Ha and", "paper/refs.bib", "2,086")
    add("HaGame", "193", "paper/refs.bib", "Ha and Schmidhuber (2018), Table 2 (VizDoom Take Cover, tau=0.10)")
    quote("ProtoSpeed", "PROTO_SPEED = 1 ", "code/dc/engine.py", "1")
    quote("WorldW", "WORLD_W, WORLD_H = 120, 100", "code/dc/engine.py", "120")
    add("WorldH", "100", "code/dc/engine.py", 'text "WORLD_W, WORLD_H = 120, 100"')
    quote("PowerFrac", "POWER_FRACTION = 0.95 ", "code/dc/tasks.py", "95")
    quote("NCodes", "N_CODES = 1024", "code/dc/model.py", "1,024")
    quote("ZDim", "Z_DIM = 32", "code/dc/model.py", "32")
    quote("TaxMax", "(tax 0..20, road, fire, police funding", "code/dc/grammar.py", "20")
    g = T("code/dc/grammar.py")
    m = re.search(r"N_COLS = 5 \+ 5 \* M\s+# (\d+)", g)
    if not m:
        raise Missing("N_COLS not found")
    h = J("data/tasks_v2_H24.json")["meta"]["horizon"]
    add("PlanColumns", ints(int(m.group(1)) * int(h)), "code/dc/grammar.py", f"N_COLS ({m.group(1)}) x horizon ({h}, data/tasks_v2_H24.json)")
    add("PairedSubset", "40", "code/scripts/analyse_ladder.py", "40 paired instances (8 per task family)")
    add("EconRandom", "25", f"{ENGREF}/B_economy/card.json", "25 random plans in economy floor")
    quote("TruthSeeds", "TRUTH_N = 64", "code/dc/audit.py", "64")
    quote("DecFidPlans", "DEC_PLANS = 100 ", "code/scripts/analyse_ladder.py", "100")
    tp = f"{MAIN}/reference.json"
    lvl = J(tp)["subsets"]["all"]["groups"][0]["emulator"]["hackability"]["level"]
    if abs(lvl - 0.95) > 1e-9:
        raise Missing("level")
    mt = test_json("os_50m_full")
    keys = [k for k in J(mt)["rollouts"] if re.fullmatch(r"h\d+", k)]
    hs = sorted(int(k[1:]) for k in keys)
    add("RollA", ints(hs[1]), mt, "rollouts keys " + ",".join(keys))


# ---------------------------------------------------------------------------------------------
# guards: a qualitative statement the text makes about a complete result is checked here, so that
# the build stops (rather than prints a false sentence) if the result file ever says otherwise
# ---------------------------------------------------------------------------------------------
def expect(cond, what):
    if not cond:
        raise Missing(f"numbers: the text states '{what}', and the result file no longer supports it")


def u3(x):
    """An unsigned share that may (in an interval) fall below zero."""
    return f3(x)


def excl0(lo, hi):
    return lo > 0 or hi < 0


# ---------------------------------------------------------------------------------------------
# 12. the pressure axis: the adaptive search at 10 to 10,000 evaluations, the same instances at every budget
# ---------------------------------------------------------------------------------------------
PA = "results/analysis/pressure_axis.json"
# the first stage of the 10,000 point (100 instances), kept beside the complete axis; read only for appendix A's row
PA_FIRST = "results/analysis/pressure_axis_i100/pressure_axis.json"
EXCESS_THOU = "excess false acceptance: at 10,000 minus at 1,000"


def _bca(e):
    return {"value": e["value"], "lo": e["bca_lo"], "hi": e["bca_hi"]}


def _axis(path):
    """A pressure-axis file of the main checkpoint's adaptive search. Its families need not be of equal size (the
    complete axis holds every instance: 40, 38, 40, 35 and 40); they must cover the five and add up to its instances."""
    d = J(path)
    if d["method"] != "cem_seeded" or d["checkpoint"] != "os_50m_full/samples_006000000":
        raise Missing(f"{path}: not the main checkpoint's adaptive search")
    pf = d["per_family"]
    if set(pf) != set(FAMS) or min(pf.values()) < 1 or sum(pf.values()) != d["n_instances"]:
        raise Missing(f"{path}: per-family counts {pf} do not cover the five families and add up to {d['n_instances']}")
    if d["coverage"]["n_on_axis"] != d["n_instances"] or d["coverage"]["emulator_only"] or d["coverage"]["perfect_only"]:
        raise Missing(f"{path}: the instances on the axis are not those of both sides")
    return d


def pressure_axis():
    """The budget axis on its instances (all of the main checkpoint's once the 10,000 point is complete), both
    searches with BCa intervals over held-out cities (the file's ``bca`` block, one interval method for the figure
    and the text), the contrasts at 10,000 per comparison and corrected for the three (``bca.contrasts_at_10000``),
    the well-posed instances, the analysis plan's rule field, and the first stage of the 10,000 point (PA_FIRST)
    for the disclosure row of appendix A."""
    d = _axis(PA)
    add("PaInstances", ints(d["n_instances"]), PA, "n_instances")
    add("PaClusters", ints(d["n_clusters"]), PA, "n_clusters")
    for fam, fw in F_WORD.items():
        add(f"Pa{fw}N", ints(d["per_family"][fam]), PA, f"per_family.{fam}")
    B = d["bca"]
    if B["levels"]["corrected"] != 1 - 0.05 / 3:
        raise Missing(f"{PA}: corrected level {B['levels']}")
    add("PaCorrLevel", f"{100 * B['levels']['corrected']:.2f}", PA, "bca.levels.corrected x 100")
    rows = {int(r["budget"]): r for r in B["pool_seeded"]["rows"]}
    if sorted(rows) != [10, 100, 1000, 10000]:
        raise Missing(f"{PA}: budgets {sorted(rows)}")
    top = {int(r["budget"]): r for r in d["rows"]}
    for b, r in rows.items():
        w, loc = B_WORD[b], f"bca.pool_seeded.rows[budget={b}]."
        if abs(r["false_acceptance"]["emulator"]["value"] - top[b]["false_acceptance"]["emulator"]["value"]) > 1e-12:
            raise Missing(f"{PA}: bca and top-level rows differ at {b}")
        fa, rs, ja = r["false_acceptance"], r["real_success"], r["judge_accepts"]
        add(f"Pa{w}Hack", f3(fa["emulator"]["value"]), PA, loc + "false_acceptance.emulator.value")
        add(f"Pa{w}HackCI", ci(_bca(fa["emulator"])), PA, loc + "false_acceptance.emulator.bca_lo/hi")
        add(f"Pa{w}PerfHack", f3(fa["perfect"]["value"]), PA, loc + "false_acceptance.perfect.value")
        add(f"Pa{w}PerfHackCI", ci(_bca(fa["perfect"])), PA, loc + "false_acceptance.perfect.bca_lo/hi")
        add(f"Pa{w}Excess", s3(fa["difference"]["value"]), PA, loc + "false_acceptance.difference.value")
        add(f"Pa{w}ExcessCI", ci(_bca(fa["difference"]), signed=True), PA, loc + "false_acceptance.difference.bca_lo/hi")
        add(f"Pa{w}OrAcc", f3(rs["emulator"]["value"]), PA, loc + "real_success.emulator.value")
        add(f"Pa{w}OrAccCI", ci(_bca(rs["emulator"])), PA, loc + "real_success.emulator.bca_lo/hi")
        add(f"Pa{w}PerfOrAcc", f3(rs["perfect"]["value"]), PA, loc + "real_success.perfect.value")
        add(f"Pa{w}PerfOrAccCI", ci(_bca(rs["perfect"])), PA, loc + "real_success.perfect.bca_lo/hi")
        sd = rs["difference"]
        add(f"Pa{w}Short", u3(-sd["value"]), PA, loc + "real_success.difference.value x -1 (perfect minus emulator)")
        add(f"Pa{w}ShortCI", f"[{u3(-sd['bca_hi'])}, {u3(-sd['bca_lo'])}]", PA, loc + "real_success.difference.bca x -1")
        rel_short = (-sd["value"]) / rs["perfect"]["value"]
        add(f"PaRelShort{w}", f"{100 * rel_short:.0f}", PA,
            loc + "(real_success.perfect.value - real_success.emulator.value) / real_success.perfect.value x 100")
        add(f"PaRelShort{w}Dec", f2(rel_short), PA,
            loc + "(real_success.perfect.value - real_success.emulator.value) / real_success.perfect.value")
        add(f"Pa{w}JudgeAcc", f3(ja["emulator"]["value"]), PA, loc + "judge_accepts.emulator.value")
        add(f"Pa{w}PerfJudgeAcc", f3(ja["perfect"]["value"]), PA, loc + "judge_accepts.perfect.value")
    # random search on the same 100 instances (one interval method)
    rr = {int(r["budget"]): r for r in B["random"]["rows"]}
    for b in (1, 1000):
        r, loc = rr[b], f"bca.random.rows[budget={b}]."
        add(f"PaRand{B_WORD[b]}Excess", s3(r["false_acceptance"]["difference"]["value"]), PA, loc + "false_acceptance.difference.value")
        add(f"PaRand{B_WORD[b]}ExcessCI", ci(_bca(r["false_acceptance"]["difference"]), signed=True), PA, loc + "false_acceptance.difference.bca")
        add(f"PaRand{B_WORD[b]}OrAcc", f3(r["real_success"]["emulator"]["value"]), PA, loc + "real_success.emulator.value")
        add(f"PaRand{B_WORD[b]}PerfOrAcc", f3(r["real_success"]["perfect"]["value"]), PA, loc + "real_success.perfect.value")
        if b == 1000:   # the paired shortfall in real success with its interval 
            sd = r["real_success"]["difference"]
            add("PaRandThouShort", u3(-sd["value"]), PA, loc + "real_success.difference.value x -1 (perfect minus emulator)")
            add("PaRandThouShortCI", f"[{u3(-sd['bca_hi'])}, {u3(-sd['bca_lo'])}]", PA, loc + "real_success.difference.bca x -1")
    con = {c["contrast"]: c for c in B["contrasts_at_10000"]}
    names = {EXCESS_THOU: ("PaExcessRiseThou", 1),
             "excess false acceptance: at 10,000 minus at 100": ("PaExcessRiseHund", 1),
             "excess false acceptance: at 10,000 minus at 10": ("PaExcessRiseTen", 1),
             "real-success shortfall (emulator minus perfect): at 10,000 minus at 1,000": ("PaShortRiseThou", -1),
             "real-success shortfall (emulator minus perfect): at 10,000 minus at 100": ("PaShortRiseHund", -1),
             "real-success shortfall (emulator minus perfect): at 10,000 minus at 10": ("PaShortRiseTen", -1),
             "real success, emulator: at 10,000 minus at 1,000": ("PaEmuOrAccRise", 1),
             "real success, perfect: at 10,000 minus at 1,000": ("PaPerfOrAccRise", 1)}
    out = {}
    for label, (name, sign) in names.items():
        c = con.get(label)
        if c is None:
            raise Missing(f"{PA}: bca contrast not found: {label!r}")
        for part, suf in (("per_comparison", ""), ("corrected", "Corr")):
            e = c[part]
            v, lo, hi = sign * e["value"], min(sign * e["bca_lo"], sign * e["bca_hi"]), max(sign * e["bca_lo"], sign * e["bca_hi"])
            loc = f"bca.contrasts_at_10000['{label}'].{part}.value, bca_lo/hi" + (" x -1" if sign < 0 else "")
            if suf == "":
                add(name, s3(v), PA, loc)
            add(name + suf + "CI", f"[{s3(lo)}, {s3(hi)}]", PA, loc)
            out[name + suf] = (v, lo, hi)
    # the well-posed instances of the axis (R3 F3)
    wp = d["well_posed"]
    add("PaWPInstances", ints(wp["n_instances"]), PA, "well_posed.n_instances")
    wr = {int(r["budget"]): r for r in wp["bca"]["pool_seeded"]["rows"]}[10000]
    add("PaWPTenThouExcess", s3(wr["false_acceptance"]["difference"]["value"]), PA, "well_posed.bca.pool_seeded.rows[10000].false_acceptance.difference.value")
    add("PaWPTenThouExcessCI", ci(_bca(wr["false_acceptance"]["difference"]), signed=True), PA, "well_posed.bca ... difference.bca")
    add("PaWPTenThouShort", u3(-wr["real_success"]["difference"]["value"]), PA, "well_posed.bca.pool_seeded.rows[10000].real_success.difference.value x -1")
    # the analysis plan: the rule is applied only once the 10,000 point is on every instance
    r7 = d["decision_79_point_7"]
    applied = r7["n_on_axis"] == r7["n_required"] and r7["excludes_zero"] is not None
    expect(applied or r7["status"].startswith("not applied"), "the analysis plan's field says whether the rule was applied")
    rise = bool(applied and r7["excludes_zero"])
    add_if("PaAllDone", applied, PA, "decision_79_point_7: applied on all instances")
    add_if("PaRise", rise, PA, "decision_79_point_7.excludes_zero")
    if applied:
        c7, cc = r7["contrast"], con[EXCESS_THOU]["corrected"]
        if c7["level"] != B["levels"]["corrected"] or any(abs(c7[k] - cc[k]) > 1e-12 for k in ("value", "bca_lo", "bca_hi")):
            raise Missing(f"{PA}: the analysis plan's contrast is not bca.contrasts_at_10000's corrected one")
        expect(r7["n_on_axis"] == d["n_instances"] and bool(r7["excludes_zero"]) == excl0(c7["bca_lo"], c7["bca_hi"]),
               "the analysis plan is read on the whole axis from its own corrected interval")
        add("PaAllInstances", ints(r7["n_on_axis"]), PA, "decision_79_point_7.n_on_axis")
        add("PaAllRise", s3(c7["value"]), PA, "decision_79_point_7.contrast.value")
        add("PaAllRiseCI", f"[{s3(c7['bca_lo'])}, {s3(c7['bca_hi'])}]", PA, "decision_79_point_7.contrast.bca_lo/hi (corrected)")
    else:
        for n in ("PaAllInstances", "PaAllRise", "PaAllRiseCI"):
            pending(n, PA, r7["status"])
    # what section 3 says in words. "No rise ... at any budget": no corrected contrast of the excess lies above zero
    if not rise:
        expect(not any(out[n + "Corr"][1] > 0 for n in ("PaExcessRiseThou", "PaExcessRiseHund", "PaExcessRiseTen")),
               "corrected for the three contrasts, the 10^4 excess exceeds none of the smaller budgets")
    # the analysis plan: the shortfall widens with budget as far as the corrected intervals carry it. Per comparison the
    # shortfall at 10^4 exceeds the one at every smaller budget, after correction at least the one at 10; the switches
    # say whether it also does so at 10^2 and 10^3 after correction (else the sentence says "per comparison only")
    sh = [-rows[b]["real_success"]["difference"]["value"] for b in (10, 100, 1000, 10000)]
    expect(sh[3] == max(sh) and sh[0] == min(sh), "the shortfall is smallest at 10 and largest at 10,000")
    expect(all(out[n][1] > 0 for n in ("PaShortRiseTen", "PaShortRiseHund", "PaShortRiseThou")),
           "per comparison the shortfall at 10^4 exceeds the shortfall at 10, 10^2 and 10^3")
    expect(out["PaShortRiseTenCorr"][1] > 0, "after correction the shortfall at 10^4 exceeds the one at 10")
    add_if("PaShortHundCorr", out["PaShortRiseHundCorr"][1] > 0, PA,
           "bca.contrasts_at_10000[shortfall, 10,000 minus 100].corrected excludes zero")
    add_if("PaShortThouCorr", out["PaShortRiseThouCorr"][1] > 0, PA,
           "bca.contrasts_at_10000[shortfall, 10,000 minus 1,000].corrected excludes zero")
    # the analysis plan: the last tenfold buys real success only inside the perfect emulator, by corrected intervals
    expect(not excl0(*out["PaEmuOrAccRiseCorr"][1:]) and out["PaPerfOrAccRiseCorr"][1] > 0,
           "with corrected intervals the last tenfold buys real success only inside the perfect emulator")
    # appendix A's disclosure row: the 10,000 point was first run on part of the instances, and the rule above was
    # fixed before the rest were run; what the first stage read is taken from its own file, kept beside the axis
    f = _axis(PA_FIRST)
    c1 = {c["contrast"]: c for c in f["bca"]["contrasts_at_10000"]}[EXCESS_THOU]["corrected"]
    expect(f["decision_79_point_7"]["status"].startswith("not applied")
           and f["coverage"]["n_full_set"] == d["coverage"]["n_full_set"] and f["budgets"] == d["budgets"],
           "the first stage is the 10,000 point on part of the same instances, read before the rule applied")
    expect(abs(c1["bca_lo"]) < 5e-4 and c1["bca_hi"] > 0, "the first stage's corrected interval touches zero")
    add("PaFirstInstances", ints(f["n_instances"]), PA_FIRST, "n_instances")
    add("PaFirstRise", s3(c1["value"]), PA_FIRST, f"bca.contrasts_at_10000['{EXCESS_THOU}'].corrected.value")
    add("PaFirstRiseCI", f"[{s3(c1['bca_lo'])}, {s3(c1['bca_hi'])}]", PA_FIRST,
        f"bca.contrasts_at_10000['{EXCESS_THOU}'].corrected.bca_lo/hi")
    if applied:
        dirs = lambda x, side: set(x["coverage"]["directories_10000"][side])
        expect(dirs(f, "emulator") <= dirs(d, "emulator") and dirs(f, "perfect") <= dirs(d, "perfect")
               and f["n_instances"] < d["n_instances"], "the complete axis holds the first stage's runs and more")
        add_multi("PaRestInstances", ints(d["n_instances"] - f["n_instances"]), [PA, PA_FIRST],
                  "n_instances minus the first stage's n_instances")
    else:
        pending("PaRestInstances", PA, r7["status"])


def text_guards(groups, full):
    """Statements of sections 3 and 4 about complete results, checked against the files."""
    expect(rlx("engine", RL_SNAPS["Full"], "all", "oracle")["value"] < est(groups[("all", "random", 1000)]["emulator"]["oracle_accept"]),
           "on the engine the RL learner reaches less real success than random search does inside the emulator")
    g = groups[("all", "cem_seeded", 1000)]["difference"]
    v = J(PA)["rows"]
    pa = [r for r in v if int(r["budget"]) == 1000][0]["false_acceptance"]["difference"]["value"]
    expect(g["bca_lo"] <= pa <= g["bca_hi"], "the budget axis's 10^3 excess lies inside the full set's interval")
    if dict(i[:2] for i in IFS)["PaAllDone"]:
        # one account : on every instance, the axis below 10,000 is the reference files' own values
        d = J(PA)
        expect(d["n_instances"] == groups[("all", "random", 1000)]["n_paired"], "the budget axis is on every instance")
        for blk, m in ((d["bca"]["pool_seeded"], "cem_seeded"), (d["bca"]["random"], "random")):
            for r in blk["rows"]:
                b = int(r["budget"])
                if b == 10000:
                    continue
                g = groups[("all", m, b)]
                for a, c in ((r["false_acceptance"]["emulator"], g["emulator"]["hackability"]),
                             (r["false_acceptance"]["perfect"], g["perfect_emulator"]["hackability"]),
                             (r["false_acceptance"]["difference"], g["difference"]),
                             (r["real_success"]["emulator"], g["emulator"]["oracle_accept"]),
                             (r["real_success"]["perfect"], g["perfect_emulator"]["oracle_accept"])):
                    expect(all(abs(a[k] - c[k]) < 1e-12 for k in ("value", "bca_lo", "bca_hi")),
                           f"the budget axis at {b} ({m}) reproduces the reference file on all instances")
    cl = [r["ck"] for r in full]
    m = HS.conditional_mean(np.asarray([r["inflation_open"] for r in full], float), None, np.asarray(cl), bca=True).as_dict()
    lo, hi = m.get("bca_lo", m["lo"]), m.get("bca_hi", m["hi"])
    expect(lo < 0 < hi, "the margin inflation's interval over all runs includes zero")
    sign = {f: np.mean([r["inflation_open"] for r in full if r["fam"] == f]) for f in FAMS}
    expect(sign["recover"] > 0 and sign["treasury"] > 0 and all(sign[f] < 0 for f in ("grow", "solvent", "power")),
           "the margin is inflated on recover and treasury and deflated on the other three")


# ---------------------------------------------------------------------------------------------
# 13. the eighty further cities: the task facts and the replication of the headline
# ---------------------------------------------------------------------------------------------
RP = "results/analysis/replication.json"
SET_W = {"c40": "Forty", "c80": "Eighty", "c120": "All"}
REPL_AD_NAMES = [f"ReplAdThou{sw}{k}" for sw in ("Eighty", "All")
                 for k in ("Hack", "HackCI", "PerfHack", "Diff", "DiffCI", "OrAcc", "PerfOrAcc", "N")] + \
                ["ReplAdExcl", "ReplAdInside"]


def extra_cities():
    t40, t80 = "data/tasks_v2_H24.json", "data/tasks_v2x_H24.json"
    t = J(t80)
    inst = t["instances"]
    add("XInstances", ints(len(inst)), t80, "len(instances)")
    add("XInstancesPlanned", ints(len(inst) + len(t["meta"]["excluded"])), t80, "len(instances)+len(meta.excluded)")
    add("XWellPosed", ints(sum(1 for r in inst if r.get("well_posed32"))), t80, "count(instances.well_posed32)")
    add_multi("AllInstances", ints(len(inst) + len(J(t40)["instances"])), [t40, t80], "len(instances) of both task files")
    f40, f80 = "data/families.json", "data/families_x.json"
    fx = J(f80)
    if fx["extends"]["manifest"] != f40 or "unchanged" not in fx["extends"]["recipe"] \
            or not fx["extends"]["map_seeds_disjoint_from_existing"]:
        raise Missing(f"{f80}: not an extension of {f40} by the same recipe")
    ho80 = [x for x in fx["families"] if x["split"] == "heldout"]
    ho40 = [x for x in J(f40)["families"] if x["split"] == "heldout"]
    add("XCities", ints(len(ho80)), f80, "count(families, split == heldout)")
    add_multi("AllCities", ints(len(ho80) + len(ho40)), [f40, f80], "held-out families of both files")
    if len({r["family_id"] for r in inst}) != len(ho80):
        raise Missing("the 80-city task file does not use every new family")
    for fams, path, pre in ((ho40, f40, ""), (ho80, f80, "X")):
        pops = [s["summary"]["pop"] for x in fams for s in x["starts"]]
        add(pre + "PopMin", ints(min(pops)), path, "min over held-out starts of starts[].summary.pop")
        add(pre + "PopMax", ints(max(pops)), path, "max over held-out starts of starts[].summary.pop")
    # the engine-side cross-entropy search (behaviour-initialised, 1,000 evaluations) on treasury, majority oracle
    for path, tab, pre in ((t40, "results/tasks_v2/tables_H24.md", ""), (t80, "results/tasks_v2x/tables_H24.md", "X")):
        rs = [r for r in J(path)["instances"] if r["task"] == "treasury"]
        k = sum(r["base_rates32"]["cem_behaviour_1000"] for r in rs)
        if abs(k - round(k)) > 1e-9:
            raise Missing(f"{path}: treasury cem_behaviour_1000 does not sum to a count")
        body = T(tab)
        sec = body[body.find("### Base rates at theta32(0.5), majority over 32 oracle seeds"):]
        m = re.search(r"^\| treasury_rev \| (\d+) \|(?:[^|]*\|){6} [\d.]+ / [\d.]+ / ([\d.]+) / [\d.]+ \|", sec, re.M)
        if not m or int(m.group(1)) != len(rs) or m.group(2) != f"{k / len(rs):.3f}":
            raise Missing(f"{tab}: treasury_rev engine-search rate does not match {path}")
        add(pre + "TreasCemPass", ints(round(k)), path, "sum over treasury instances of base_rates32.cem_behaviour_1000 "
            f"(= {tab}, theta32(0.5) majority table, treasury_rev, CE behaviour-init B=1,000 x n)")
        if pre:
            add("XTreasCount", ints(len(rs)), path, "count(task=treasury)")


def replication():
    d = J(RP)
    if d["checkpoint"] != "os_50m_full-samples_006000000":
        raise Missing(f"{RP}: not the main checkpoint")
    rnd = d["methods"]["random"]
    for b in (1, 10, 100, 1000):
        for s, sw in SET_W.items():
            r = rnd[str(b)][s]
            if "difference" not in r:
                raise Missing(f"{RP}: random B={b} {s} is not complete")
            p, loc = f"ReplRand{B_WORD[b]}{sw}", f"methods.random.{b}.{s}."
            add(p + "Hack", f3(est(r["emulator"]["hackability"])), RP, loc + "emulator.hackability.value")
            add(p + "HackCI", ci(r["emulator"]["hackability"]), RP, loc + "emulator.hackability.bca")
            add(p + "PerfHack", f3(est(r["perfect_emulator"]["hackability"])), RP, loc + "perfect_emulator.hackability.value")
            add(p + "Diff", s3(est(r["difference"])), RP, loc + "difference.value")
            add(p + "DiffCI", ci(r["difference"], signed=True), RP, loc + "difference.bca")
            add(p + "OrAcc", f3(est(r["emulator"]["oracle_accept"])), RP, loc + "emulator.oracle_accept.value")
            add(p + "PerfOrAcc", f3(est(r["perfect_emulator"]["oracle_accept"])), RP, loc + "perfect_emulator.oracle_accept.value")
            add(p + "N", ints(r["n_paired"]), RP, loc + "n_paired")
            add(p + "Clusters", ints(r["n_clusters"]), RP, loc + "n_clusters")
    # the replication statement fixed before the new cities were audited: the adaptive search on the 80
    done = d["status"] == "complete"
    add_if("ReplAdDone", done, RP, "status == complete (the adaptive search on the 80 new cities and its perfect emulator)")
    if not done:
        for n in REPL_AD_NAMES + ["ReplAdSizeDiff", "ReplAdSizeDiffCI", "ReplRandSizeDiff", "ReplRandSizeDiffCI"]:
            pending(n, RP, f"replication.json status {d['status']}")
        for n in ("ReplAdReplicates", "ReplAdConsistent", "ReplRandReplicates", "ReplRandConsistent"):
            add_if(n, False, RP, "pending (replication.json partial)")
        return
    ad, st = d["methods"]["cem_seeded"]["1000"], d["statement"]
    for s, sw in (("c80", "Eighty"), ("c120", "All")):
        r, p, loc = ad[s], f"ReplAdThou{sw}", f"methods.cem_seeded.1000.{s}."
        add(p + "Hack", f3(est(r["emulator"]["hackability"])), RP, loc + "emulator.hackability.value")
        add(p + "HackCI", ci(r["emulator"]["hackability"]), RP, loc + "emulator.hackability.bca")
        add(p + "PerfHack", f3(est(r["perfect_emulator"]["hackability"])), RP, loc + "perfect_emulator.hackability.value")
        add(p + "Diff", s3(est(r["difference"])), RP, loc + "difference.value")
        add(p + "DiffCI", ci(r["difference"], signed=True), RP, loc + "difference.bca")
        add(p + "OrAcc", f3(est(r["emulator"]["oracle_accept"])), RP, loc + "emulator.oracle_accept.value")
        add(p + "PerfOrAcc", f3(est(r["perfect_emulator"]["oracle_accept"])), RP, loc + "perfect_emulator.oracle_accept.value")
        add(p + "N", ints(r["n_paired"]), RP, loc + "n_paired")
    add("ReplAdExcl", "excludes" if st["c80_excludes_0"] else "does not exclude", RP, "statement.c80_excludes_0")
    add("ReplAdInside", "contains" if st["c40_point_inside_c80_interval"] else "does not contain", RP,
        "statement.c40_point_inside_c80_interval")
    # the replication statement as re-fixed after review (statement_d79: the 80-city excess replicates if its interval
    # excludes zero; its size against the 40 by the difference with independent bootstraps over cities)
    for m, w in (("cem_seeded", "Ad"), ("random", "Rand")):
        b = d["statement_d79"][m]
        if b["status"] != "ok" or b["budget"] != 1000:
            raise Missing(f"{RP}: statement_d79.{m} not ok")
        loc = f"statement_d79.{m}."
        sd = b["difference_c80_minus_c40"]
        add(f"Repl{w}SizeDiff", s3(sd["value"]), RP, loc + "difference_c80_minus_c40.value")
        add(f"Repl{w}SizeDiffCI", f"[{s3(sd['lo'])}, {s3(sd['hi'])}]", RP, loc + "difference_c80_minus_c40.lo/hi (percentile)")
        rd = b["reading"]
        if rd["c80"] not in ("replicates", "does not replicate") or rd["size"] not in ("consistent in size", "not consistent in size"):
            raise Missing(f"{RP}: {loc}reading {rd}")
        if (rd["c80"] == "replicates") != (b["excess_c80_interval"][0] > 0 or b["excess_c80_interval"][1] < 0):
            raise Missing(f"{RP}: {loc}reading.c80 disagrees with the interval")
        if (rd["size"] == "consistent in size") != (sd["lo"] <= 0 <= sd["hi"]):
            raise Missing(f"{RP}: {loc}reading.size disagrees with the interval")
        add_if(f"Repl{w}Replicates", rd["c80"] == "replicates", RP, loc + "reading.c80 == replicates")
        add_if(f"Repl{w}Consistent", rd["size"] == "consistent in size", RP, loc + "reading.size == consistent in size")
    # the analysis plan, the specification: random search's excess at 1,000 minus at one plan, paired by instance
    bc = J(RP).get("budget_contrast_d99")
    if not bc or bc.get("search") != "random":
        raise Missing(f"{RP}: budget_contrast_d99 absent")
    for s, w in (("c120", "All"), ("c40", "Forty")):
        e, loc = bc[s], f"budget_contrast_d99.{s}."
        if e.get("status") != "ok":
            raise Missing(f"{RP}: {loc}status {e.get('status')}")
        add(f"ReplRandRise{w}", s3(e["contrast"]["value"]), RP, loc + "contrast.value")
        add(f"ReplRandRise{w}CI", ci(e["contrast"], signed=True), RP, loc + "contrast (BCa; percentile where BCa is undefined)")
    c = bc["c120"]["contrast"]
    lo, hi = (c["bca_lo"], c["bca_hi"]) if c.get("bca_lo") is not None and c.get("bca_hi") is not None else (c["lo"], c["hi"])
    add_if("ReplRandRiseUp", lo > 0, RP, "budget_contrast_d99.c120: the printed interval lies above zero")
    add_if("ReplRandRiseDown", hi < 0, RP, "budget_contrast_d99.c120: the printed interval lies below zero")


# ---------------------------------------------------------------------------------------------
# 14. the coverage arm (results/analysis/coverage.json; results/coverage/)
# ---------------------------------------------------------------------------------------------
CV = "results/analysis/coverage.json"
CT = "results/coverage/coverage_table.json"
B20 = "results/coverage/B20_notes.md"


def coverage(full_rl):
    d = J(CV)
    if d["status"] != "complete" or d["missing"]:
        raise Missing(f"{CV}: status {d['status']}")
    if d["main"] != "os_50m_full-samples_006000000" or d["coverage"] != "os_50m_cov-samples_006000000":
        raise Missing(f"{CV}: unexpected models {d['main']} / {d['coverage']}")
    removed = {}
    for m, mw in (("random", "Rand"), ("cem_seeded", "Ad")):
        for scope in ["all"] + FAMS:
            sw = "All" if scope == "all" else F_WORD[scope]
            g = d["methods"][m]["budgets"]["1000"][scope]
            loc = f"methods.{m}.budgets.1000.{scope}."
            for who, ww in (("coverage", "Cov"), ("main", "Main")):
                e = g[who]
                p = f"Cov{mw}{sw}{ww}"
                for key, kw in (("hackability", "Hack"), ("oracle_accept", "OrAcc"), ("judge_accept", "JudgeAcc"),
                                ("false_rejection", "FalseRej")):
                    add(p + kw, f3(est(e["emulator"][key])), CV, loc + f"{who}.emulator.{key}.value")
                    add(p + kw + "CI", ci(e["emulator"][key]), CV, loc + f"{who}.emulator.{key}.bca")
                add(p + "Excess", s3(est(e["difference"])), CV, loc + f"{who}.difference.value")
                add(p + "ExcessCI", ci(e["difference"], signed=True), CV, loc + f"{who}.difference.bca")
                add(p + "N", ints(e["n_paired"]), CV, loc + f"{who}.n_paired")
            pe = g["main"]["perfect_emulator"]
            if g["coverage"]["perfect_emulator"]["hackability"]["value"] != pe["hackability"]["value"]:
                raise Missing(f"{CV}: the two models' perfect emulators differ at {loc}")
            add(f"Cov{mw}{sw}PerfHack", f3(est(pe["hackability"])), CV, loc + "main.perfect_emulator.hackability.value")
            add(f"Cov{mw}{sw}PerfOrAcc", f3(est(pe["oracle_accept"])), CV, loc + "main.perfect_emulator.oracle_accept.value")
            dm = g["coverage_minus_main"]
            for key, kw in (("hackability", "Hack"), ("excess_over_perfect", "Excess"), ("oracle_accept", "OrAcc"),
                            ("judge_accept", "JudgeAcc"), ("false_rejection", "FalseRej")):
                add(f"Cov{mw}{sw}Diff{kw}", s3(est(dm[key])), CV, loc + f"coverage_minus_main.{key}.value")
                add(f"Cov{mw}{sw}Diff{kw}CI", ci(dm[key], signed=True), CV, loc + f"coverage_minus_main.{key}.bca")
            if scope == "all":
                ce, me = est(g["coverage"]["difference"]), est(g["main"]["difference"])
                removed[m] = 1 - ce / me
                add(f"Cov{mw}Removed", f2(removed[m]), CV, loc + "1 - coverage.difference.value / main.difference.value")
    # RL: three seeds a cell, means and seed standard deviations (no test)
    rl = d["rl"]
    means = {}
    for who, ww in (("coverage", "Cov"), ("main", "Main")):
        for fam in FAMS:
            v = rl[who][fam]["values"]
            if v["rl_n_seeds_1000000"] != 3:
                raise Missing(f"{CV}: rl.{who}.{fam}: {v['rl_n_seeds_1000000']} seeds")
            p, loc = f"CovRl{F_WORD[fam]}{ww}", f"rl.{who}.{fam}.values."
            for key, kw in (("rl_gap", "Gap"), ("rl_dream_accept", "Dream"), ("rl_oracle_open_accept", "Oracle"),
                            ("rl_closed_accept", "Closed"), ("rl_inflation", "Infl")):
                fmt = s3 if kw in ("Gap", "Infl") else f3
                add(p + kw, fmt(v[f"{key}_1000000"]), CV, loc + f"{key}_1000000")
                add(p + kw + "Sd", f3(v[f"{key}_sd_1000000"]), CV, loc + f"{key}_sd_1000000")
        for key, kw in (("rl_gap", "Gap"), ("rl_oracle_open_accept", "Oracle"), ("rl_closed_accept", "Closed"),
                        ("rl_dream_accept", "Dream")):
            mval = float(np.mean([rl[who][f]["values"][f"{key}_1000000"] for f in FAMS]))
            means[(who, kw)] = mval
            add(f"CovRl{ww}{kw}Mean", (s3 if kw == "Gap" else f3)(mval), CV, f"mean over the five families of rl.{who}.*.values.{key}_1000000")
    add("CovRlSeeds", "3", CV, "rl.*.*.values.rl_n_seeds_1000000 (3 in every cell)")
    sds = [rl[w][f]["values"][f"{k}_sd_1000000"] for w in ("coverage", "main") for f in ("treasury", "recover")
           for k in ("rl_oracle_open_accept", "rl_closed_accept")]
    add("CovRlAccSdMin", f3(min(sds)), CV, "min seed sd of open- and closed-loop acceptance, treasury and recover, both models")
    add("CovRlAccSdMax", f3(max(sds)), CV, "max of the same")
    removed["rl"] = 1 - means[("coverage", "Gap")] / means[("main", "Gap")]
    add("CovRlRemoved", f2(removed["rl"]), CV, "1 - CovRlCovGapMean / CovRlMainGapMean")
    # cross-check: the main model's RL cells equal the per-run summaries the RL arm reads
    for fam in FAMS:
        rs = [r for r in full_rl if r["ck"] == "os_50m_full-samples_006000000" and r["fam"] == fam]
        g = np.mean([r["rate_dream_accept"] - r["rate_engine_open_accept"] for r in rs])
        if len(rs) != 3 or abs(g - rl["main"][fam]["values"]["rl_gap_1000000"]) > 1e-9:
            raise Missing(f"{CV}: the main model's RL gap on {fam} differs from the summaries")
    # what section 6 states 
    ad = d["methods"]["cem_seeded"]["budgets"]["1000"]
    dl = lambda sc, k: ad[sc]["coverage_minus_main"][k]
    expect(0.6 <= removed["cem_seeded"] <= 0.85, "about three quarters of the excess is removed under the adaptive search")
    expect(0.5 < removed["rl"] < 0.65, "a little over half of the RL acceptance gap is removed")
    expect(not excl0(dl("all", "oracle_accept")["bca_lo"], dl("all", "oracle_accept")["bca_hi"]), "no real success is bought")
    expect(dl("all", "false_rejection")["bca_lo"] > 0 and dl("all", "judge_accept")["bca_hi"] < 0,
           "the retrained model rejects more")
    expect(abs(est(dl("power", "hackability"))) < 0.05 and not excl0(dl("power", "hackability")["bca_lo"],
                                                                      dl("power", "hackability")["bca_hi"]),
           "power is untouched under search")
    gm = {f: rl["main"][f]["values"]["rl_gap_1000000"] - rl["coverage"][f]["values"]["rl_gap_1000000"] for f in FAMS}
    expect(min(gm["treasury"], gm["recover"]) > 0.1 and max(abs(gm[f]) for f in ("grow", "solvent", "power")) < 0.03,
           "all of the RL gap removed is in treasury and recover")
    expect(all(abs(rl[w][f]["values"]["rl_gap_1000000"]) < 0.03 for w in ("coverage", "main")
               for f in ("grow", "solvent", "power")), "grow, solvent and power have no RL gap in either model")
    for key in ("rl_oracle_open_accept", "rl_closed_accept"):
        expect(rl["coverage"]["treasury"]["values"][f"{key}_1000000"] > rl["main"]["treasury"]["values"][f"{key}_1000000"]
               and rl["coverage"]["recover"]["values"][f"{key}_1000000"] < rl["main"]["recover"]["values"][f"{key}_1000000"],
               f"treasury gains and recover loses real acceptance ({key})")
    # the data that were added (coverage_table.json, the stores' verification)
    c = J(CT)
    tf, fr, un = c["train_full"]["all"], c["frontier"]["all"], c["union"]["all"]
    add("CovLowTax", ints(c["low_tax"]), CT, "low_tax")
    add("CovTrainLowTax", f3(tf["share_building_months_tax_le4"]), CT, "train_full.all.share_building_months_tax_le4")
    add("CovFrontLowTax", f3(fr["share_building_months_tax_le4"]), CT, "frontier.all.share_building_months_tax_le4")
    add("CovUnionLowTax", f3(un["building_months_tax_le4"] / un["building_months"]), CT,
        "union.all.building_months_tax_le4 / union.all.building_months")
    add("CovTrainZeroFund", f3(tf["share_building_months_all_funding_0"]), CT, "train_full.all.share_building_months_all_funding_0")
    add("CovFrontZeroFund", f3(fr["share_building_months_all_funding_0"]), CT, "frontier.all.share_building_months_all_funding_0")
    add("CovUnionZeroFund", f3(un["building_months_all_funding_0"] / un["building_months"]), CT,
        "union.all.building_months_all_funding_0 / union.all.building_months")
    cs = c["coverage_stores"]
    add("CovUniformTransitions", ints(cs["train_cov"]["transitions"]), CT, "coverage_stores.train_cov.transitions")
    add("CovCompetentTransitions", ints(cs["train_cov2"]["transitions"]), CT, "coverage_stores.train_cov2.transitions")
    add("CovUnionTransitions", ints(un["months"]), CT, "union.all.months")
    vs = ["results/coverage/verify_train_cov.json", "results/coverage/verify_train_cov2.json"]
    add_multi("CovVerified", ints(sum(J(v)["checked"] for v in vs)), vs, "sum of checked (every trajectory re-replayed)")
    add_multi("CovMismatched", ints(sum(J(v)["mismatched"] for v in vs)), vs, "sum of mismatched")
    quote("CovBestK", "Per family the 3 best settings", B20, "three")
    quote("CovQuakeEvery", "`quake_every: 5`", B20, "five")
    quote("CovTrainStarts", "for each of the 228 training starts, the 2,625 constant plans", B20, "228")
    # coverage-retrained model short-horizon fidelity on the test split
    fc, fm = d["fidelity"]["coverage"]["test"], d["fidelity"]["main"]["test"]
    for k, kw in (("f1_1m", "FOne"), ("pop_medrel_12m", "Pop"), ("funds_medrel_12m", "Funds")):
        add(f"CovTest{kw}", f3(fc["values"][k]), CV, f"fidelity.coverage.test.values.{k}")
        if abs(fm["values"][k] - J(test_json("os_50m_full"))["gap_closed"][
                {"f1_1m": "tile_F1_1m_structural_T1", "pop_medrel_12m": "pop_median_rel_12m",
                 "funds_medrel_12m": "funds_median_rel_12m"}[k]]["model"]) > 1e-12:
            raise Missing(f"{CV}: main model fidelity {k} differs from the test JSON")
    meets = (fc["values"]["f1_1m"] >= 0.5 * fc["engine_yardstick"]["f1_1m"] and fc["values"]["pop_medrel_12m"] <= 0.10
             and fc["values"]["funds_medrel_12m"] <= 0.10)
    add("CovMeetsBar", "meets" if meets else "does not meet", CV, "fidelity.coverage.test: F1 >= 0.5 x yardstick, pop and funds <= 0.10")
    return removed


# the coverage model against three training seeds of the main configuration
CS = "results/analysis/coverage_seeds.json"
CS_SEEDS = (("os_50m_full", "SeedZero"), ("os_50m_full_s1", "SeedOne"), ("os_50m_full_s2", "SeedTwo"))
CS_QS = (("excess", "Excess", s3, True), ("real_success", "OrAcc", f3, True), ("false_rejection", "FalseRej", f3, False))


def coverage_seeds():
    from fractions import Fraction
    d = J(CS)
    if d["status"] != "complete" or d["seeds"] != [s for s, _ in CS_SEEDS] or d["coverage"] != "os_50m_cov":
        raise Missing(f"{CS}: status {d['status']} or other models")
    cv = J(CV)
    pos = {}
    for m, mw in (("random", "Rand"), ("cem_seeded", "Ad")):
        x = d["methods"][m]
        if x["n"] != 193:
            raise Missing(f"{CS}: {m}: {x['n']} instances")
        loc = f"methods.{m}."
        add(f"CovSd{mw}PerfHack", f3(est(x["perfect_false_acceptance"])), CS, loc + "perfect_false_acceptance.value")
        add(f"CovSd{mw}PerfOrAcc", f3(est(x["perfect_real_success"])), CS, loc + "perfect_real_success.value")
        g = cv["methods"][m]["budgets"]["1000"]["all"]
        for q, qw, fmt, worded in CS_QS:
            Q, ql = x["quantities"][q], loc + f"quantities.{q}."
            # the main checkpoint's and the coverage model's values are coverage.json's (section 6's macros)
            ref = {"excess": lambda w: est(g[w]["difference"]), "real_success": lambda w: est(g[w]["emulator"]["oracle_accept"]),
                   "false_rejection": lambda w: est(g[w]["emulator"]["false_rejection"])}[q]
            if abs(Q["seeds"][0] - ref("main")) > 1e-12 or abs(Q["coverage"] - ref("coverage")) > 1e-12:
                raise Missing(f"{CS}: {m} {q}: the main checkpoint or the coverage model differs from {CV}")
            for i, (_, sw) in enumerate(CS_SEEDS):
                add(f"CovSd{mw}{qw}{sw}", fmt(Q["seeds"][i]), CS, ql + f"seeds[{i}]")
            add(f"CovSd{mw}{qw}Cov", fmt(Q["coverage"]), CS, ql + "coverage")
            for k, kw in (("seed_min", "Min"), ("seed_max", "Max"), ("seed_mean", "Mean")):
                add(f"CovSd{mw}{qw}{kw}", fmt(Q[k]), CS, ql + k)
            dd = Q["coverage_minus_seed_mean"]
            if abs(est(dd) - (Q["coverage"] - Q["seed_mean"])) > 1e-12:
                raise Missing(f"{CS}: {m} {q}: the paired difference disagrees with the values")
            add(f"CovSd{mw}{qw}Diff", s3(est(dd)), CS, ql + "coverage_minus_seed_mean.value")
            add(f"CovSd{mw}{qw}DiffCI", ci(dd, signed=True), CS, ql + "coverage_minus_seed_mean (BCa)")
            # the analysis plan's position, recomputed from the exact counts
            ex = {k: Fraction(v) for k, v in Q["exact"].items()}
            c, ss = ex["os_50m_cov"], [ex[s] for s, _ in CS_SEEDS]
            p = "below_all" if c < min(ss) else ("above_all" if c > max(ss) else "within")
            if p != Q["position"] or (worded and Q["reading"] != p) or (not worded and Q["reading"] is not None):
                raise Missing(f"{CS}: {m} {q}: the reading disagrees with the counts")
            if worded:
                pos[(q, m)] = p
                add_if(f"CovSd{mw}{qw}Within", p == "within", CS, ql + "reading == within")
                add_if(f"CovSd{mw}{qw}Below", p == "below_all", CS, ql + "reading == below_all")
        # the share of its own selections each model accepts: a column of the appendix table only (the analysis plan c)
        for i, (run, sw) in enumerate(CS_SEEDS + (("os_50m_cov", "Cov"),)):
            v = est(x["models"][run]["emulator_accepts"])
            if run in ("os_50m_full", "os_50m_cov"):
                if abs(v - est(g["main" if run == "os_50m_full" else "coverage"]["emulator"]["judge_accept"])) > 1e-12:
                    raise Missing(f"{CS}: {m}: {run}'s emulator acceptance differs from {CV}")
            add(f"CovSd{mw}JudgeAcc{sw}", f3(v), CS, loc + f"models.{run}.emulator_accepts.value")
    for q, qw, _, worded in CS_QS:
        if worded:
            add_if(f"CovSd{qw}Same", pos[(q, "random")] == pos[(q, "cem_seeded")], CS,
                   f"methods.random.quantities.{q}.reading == methods.cem_seeded.quantities.{q}.reading")
    # the analysis plan: the abstract's and the fifth finding's retraining clause
    add_if("CovSdRetrainHolds", all(pos[("excess", m)] == "below_all" and pos[("real_success", m)] == "within"
                                    for m in ("random", "cem_seeded")), CS,
           "excess reading below_all and real_success reading within, under both searches")
    # the analysis plan: false rejection under the adaptive search against the two further seeds and the seeds' mean
    fr = d["methods"]["cem_seeded"]["quantities"]["false_rejection"]
    exf = {k: Fraction(v) for k, v in fr["exact"].items()}
    add("CovSdAdFalseRejFurtherMax", f3(max(fr["seeds"][1:])), CS,
        "methods.cem_seeded.quantities.false_rejection.seeds[1:] (maximum)")
    add_if("CovSdAdFrAsMany", max(exf["os_50m_full_s1"], exf["os_50m_full_s2"]) >= exf["os_50m_cov"], CS,
           "false_rejection.exact: a further seed's at least the coverage model's")
    dd = fr["coverage_minus_seed_mean"]
    lo = dd["bca_lo"] if dd.get("bca_lo") is not None else dd["lo"]       # the limit ci() prints
    add_if("CovSdAdFrRise", lo > 0, CS, "false_rejection.coverage_minus_seed_mean: printed interval above zero")
    add("CovSdN", ints(d["methods"]["random"]["n"]), CS, "methods.random.n")


# ---------------------------------------------------------------------------------------------
# 15. the defence frontier under the adaptive search (frontier.cem_seeded.rows)
# ---------------------------------------------------------------------------------------------
def defences_seeded(d):
    p = "results/defences/frontier.json"
    rows = {r["setting"]: r for r in d["frontier"]["cem_seeded"]["rows"]}
    for s, w in (("perfect", "Perf"), ("ensemble", "Ens"), ("member0", "Member")):
        r = rows[s]
        if not r.get("complete"):
            raise Missing(f"{p}: cem_seeded {s} incomplete")
        add("DefAd" + w + "Hack", f3(est(r["hackability"])), p, f"frontier.cem_seeded.rows[{s}].hackability.value")
        add("DefAd" + w + "HackCI", ci(r["hackability"]), p, f"frontier.cem_seeded.rows[{s}].hackability.bca")
        add("DefAd" + w + "FalseRej", f3(est(r["false_rejection"])), p, f"frontier.cem_seeded.rows[{s}].false_rejection.value")
        add("DefAd" + w + "FalseRejCI", ci(r["false_rejection"]), p, f"frontier.cem_seeded.rows[{s}].false_rejection.bca")
    tested = [r for s, r in rows.items() if "hackability_minus_ensemble" in r and r.get("complete") and s != "member0"]
    ens = [r for r in tested if r["judge"] == "ensemble"]
    mem = [r for r in tested if r["judge"] == "member0"]
    sig = [r for r in ens if r["hackability_minus_ensemble"]["bca_hi"] < 0]
    add("DefAdTestedN", ints(len(tested)), p, "cem_seeded rows with a paired difference from the undefended ensemble, except member 0")
    add("DefAdSigN", ints(len(sig)), p, "of the ensemble's settings, rows whose paired difference has a BCa interval below 0")
    mz = est(rows["member0"]["hackability"])
    md = [est(r["hackability"]) - mz for r in mem]
    add("DefAdMemDiffMin", s3(min(md)), p, "member-0 settings: false acceptance minus member 0 undefended (point), minimum")
    add("DefAdMemDiffMax", s3(max(md)), p, "member-0 settings: the same, maximum")
    fr = [est(r["false_rejection"]) for r in sig]
    add("DefAdSigFalseRejMin", f3(min(fr)), p, "min false_rejection.value over those rows")
    add("DefAdSigFalseRejMax", f3(max(fr)), p, "max false_rejection.value over those rows")
    for s, w in (("penalty2", "PenTwo"), ("detector0.2", "DetLow"), ("deflation-ensemble", "Defl"), ("temp1.25", "TempHigh")):
        r = rows[s]
        add("DefAd" + w + "Hack", f3(est(r["hackability"])), p, f"frontier.cem_seeded.rows[{s}].hackability.value")
        add("DefAd" + w + "FalseRej", f3(est(r["false_rejection"])), p, f"frontier.cem_seeded.rows[{s}].false_rejection.value")
    sa = d["detector"]["selected_plans_auc"]["cem_seeded"]
    add("DetSelAucAd", f3(sa["value"]), p, "detector.selected_plans_auc.cem_seeded.value")
    add("DetSelAucAdCI", ci(sa), p, "detector.selected_plans_auc.cem_seeded.bca")
    dom = {s: d["frontier"][s]["dominance_vs_undefended_ensemble"] for s in ("random", "cem_seeded")}
    words = {w for v in dom.values() for w in v.values()}
    if not words <= {"neither", "equal", "dominated", "dominates"}:
        raise Missing(f"{p}: dominance words {words}")
    add("DefDominatesN", ints(sum(w == "dominates" for v in dom.values() for w in v.values())), p,
        "count of settings that dominate the undefended ensemble (frontier.*.dominance_vs_undefended_ensemble), both searches")
    expect(len(sig) > 0 and min(fr) > est(rows["ensemble"]["false_rejection"]),
           "every adaptive-search defence that clearly lowers false acceptance rejects more true successes")
    expect(sum(w == "dominates" for v in dom.values() for w in v.values()) == 0,
           "under neither search does any setting do better than the undefended ensemble on both axes")
    expect(est(rows["detector0.2"]["false_rejection"]) > 0.5, "the detector as a gate costs most real successes")


# ---------------------------------------------------------------------------------------------
# 16. hyperparameters, from each training run's config.json (paper/data/ckpt_meta)
# ---------------------------------------------------------------------------------------------
CKPT = PAPER / "data" / "ckpt_meta"
HP_RUNS = TEST_RUNS + ["os_50m_cov"]
HALF = {"os": 3000064, "sf": 750080}


def hyper():
    cfg = {r: J(CKPT / r / "config.json") for r in HP_RUNS}
    srcs = [CKPT / r / "config.json" for r in HP_RUNS]

    def same(section, key):
        vals = {json.dumps(cfg[r][section][key], sort_keys=True) for r in HP_RUNS}
        if len(vals) != 1:
            raise Missing(f"config.json: {section}.{key} differs between runs")
        return cfg[HP_RUNS[0]][section][key]

    def by_mode(key, mode):
        vals = {json.dumps(cfg[r]["train"][key]) for r in HP_RUNS if cfg[r]["train"]["mode"] == mode}
        if len(vals) != 1:
            raise Missing(f"config.json: train.{key} differs between {mode} runs")
        return json.loads(vals.pop())
    num = lambda x: f"{x:g}"
    for key, nm in (("batch_size", "HpBatch"), ("weight_decay", "HpWd"), ("grad_clip", "HpClip"), ("ema_decay", "HpEma"),
                    ("kl_warmup", "HpKl"), ("warmup_frac", "HpWarmup"), ("min_lr_frac", "HpMinLr"), ("sf_k", "HpSfK"),
                    ("sf_tf_ratio", "HpSfTf"), ("bk_updates", "HpBkUpdates"), ("bk_batch", "HpBkBatch"),
                    ("bk_lr", "HpBkLr"), ("budget_weight", "HpBudgetW"), ("table_lr_mult", "HpTableLr")):
        v = same("train", key)
        add_multi(nm, ints(v) if isinstance(v, int) and v >= 1000 else num(v), srcs, f"train.{key} (equal in all {len(HP_RUNS)} runs)")
    b1, b2 = same("train", "betas")
    add_multi("HpBetas", f"{num(b1)} and {num(b2)}", srcs, "train.betas")
    w = same("train", "weights")
    nice = {"tile_gate": "change gate", "tile_cat": "tile code", "flags": "flags", "power": "power bit",
            "half": "half-resolution overlays", "eighth": "eighth-resolution overlays", "scalars": "scalars",
            "ledger": "ledger", "terrain": "terrain", "com_rate": "commercial rate", "scalars_s2": "second-stage scalars",
            "build_cost": "build cost"}
    groups = {}
    for k, v in w.items():
        groups.setdefault(v, []).append(nice[k])
    add_multi("HpLossWeights", "; ".join(f"{num(v)} for " + words_list(groups[v]) for v in sorted(groups)), srcs, "train.weights")
    for mode, tag in (("onestep", "Os"), ("selfforce", "Sf")):
        add_multi("HpLr" + tag, num(by_mode("lr", mode)), srcs, f"train.lr of every {mode} run")
        add_multi("HpSamples" + tag, ints(by_mode("samples", mode)), srcs, f"train.samples of every {mode} run")
    for key, nm in (("z_dim", "HpZ"), ("mlp_ratio", "HpMlp"), ("bk_depth", "HpBkDepth"), ("k_mix_overlay", "HpMixOverlay"),
                    ("k_mix_scalar", "HpMixScalar"), ("layer_scale", "HpLayerScale")):
        add_multi(nm, num(same("model", key)), srcs, f"model.{key} (equal in all runs)")
    # by size
    pc = J("paper/data/param_counts.json")
    lines = []
    for size in ("15m", "50m", "100m"):
        ms = {json.dumps({k: v for k, v in cfg[r]["model"].items()}, sort_keys=True) for r in HP_RUNS
              if cfg[r]["model"]["size"] == size}
        if len(ms) != 1:
            raise Missing(f"config.json: model settings differ within size {size}")
        m = json.loads(ms.pop())
        lst = lambda xs: ", ".join(str(x) for x in xs)
        lines.append(" & ".join([size.upper(), str(m["d0"]), lst(m["dims"]), lst(m["enc"]), lst(m["dec"]), str(m["cond_dim"]),
                                 str(m["cat_hidden"]), str(m["post_dim"]), str(m["bk_width"]),
                                 f"{pc[size]['elements_float_excl_norm_buffers'] / 1e6:.1f}"]) + r" \\")
    (PAPER / "tables" / "hyper_sizes.tex").write_text(
        "% Generated by paper/scripts/make_numbers.py from paper/data/ckpt_meta/<run>/config.json and paper/data/param_counts.json\n"
        r"\setlength{\tabcolsep}{3pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrlllrrrrr@{}}" "\n" r"\toprule" "\n"
        r"Size & Stem & Stage widths & Encoder blocks & Decoder blocks & Condition & Tile head & Posterior & Bookkeeping & Parameters (M) \\" "\n"
        r"\midrule" "\n" + "\n".join(lines) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n")
    # by run, with checkpoint hashes
    lab = {"onestep": "one-step", "selfforce": "pushforward"}

    def run_words(name):
        """os_50m_full_s1 -> one-step 50M full (s1) (no run names in the paper's tables)."""
        ps_ = name.split("_")
        d_ = {"full": "full", "small": "small", "cov": "full + cov."}[ps_[2]]
        sd_ = f" (s{ps_[3][1:]})" if len(ps_) > 3 and ps_[3].startswith("s") else ""
        return f"{lab['onestep' if ps_[0] == 'os' else 'selfforce']} {ps_[1].upper()} {d_}{sd_}"
    DATA_W = {"train_full": "full", "train_small": "small", "train_full_cov12": "full + cov."}
    rows = []
    for r in HP_RUNS:
        c = cfg[r]
        tr, da = c["train"], c["data"]
        obj = r[:2]
        hashes = []
        for n in (HALF[obj], FINAL[obj]):
            hp = CKPT / r / f"samples_{n:09d}.pt.sha256"
            if hp.exists():
                h = T(hp).split()[0]
                if not re.fullmatch(r"[0-9a-f]{64}", h):
                    raise Missing(f"{hp}: not a sha256")
                hashes.append(h[:12])
            else:
                hashes.append("--")
        parent = Path(tr["init_from"]).parent.name if tr["init_from"] else "--"
        rows.append(" & ".join([lab[tr["mode"]], tr["size"].upper(), DATA_W.get(da["index"], da["index"].replace("_", r"\_")), ints(da["index_len"]),
                                str(tr["seed"]), ints(tr["samples"]), num(tr["lr"]), str(tr["micro_batch"] or "--"),
                                run_words(parent) if parent != "--" else "--", hashes[0], hashes[1]]) + r" \\")
    (PAPER / "tables" / "hyper_runs.tex").write_text(
        "% Generated by paper/scripts/make_numbers.py from paper/data/ckpt_meta/<run>/config.json and samples_<N>.pt.sha256\n"
        r"\setlength{\tabcolsep}{2pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lllrcrrclll@{}}" "\n" r"\toprule" "\n"
        r"Objective & Size & Data & Transitions & Seed & Samples & LR & Micro & Parent & Half SHA-256 & Final SHA-256 \\" "\n"
        r"\midrule" "\n" + "\n".join(rows) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n")
    add_multi("HpRuns", ints(len(HP_RUNS)), srcs, "training runs in the table (the ladder, the ensemble members, the coverage model)")


# ---------------------------------------------------------------------------------------------
# 17. across emulators (section 5): read only when main_claim.json is complete
# ---------------------------------------------------------------------------------------------
MC = "results/analysis/main_claim.json"
PC = "results/analysis/pairs.csv"
# trajectory-fidelity metrics compared against random-shooting false acceptance at 1,000
FID_ROWS = [("FOne", "fid_test_f1_1m|c120", "one-month F1"),
            ("FTwelve", "fid_test_f1_since_start_12m|c120", "twelve-month F1"),
            ("Funds", "fid_test_funds_medrel_12m|c120", "twelve-month funds error"),
            ("Pop", "fid_test_pop_medrel_12m|c120", "twelve-month population error"),
            ("Lik", "fid_test_loglik_elbo|c120", "held-out likelihood"),
            ("Dec", None, "decision fidelity")]     # None: the row main_claim.json names as the verdict row
AC_NAMES = (
    ["AcPairs", "AcClusters", "AcLineages", "AcRho", "AcRhoCI", "AcRhoLinCI", "AcKendall", "AcKendallCI", "AcDecision",
     "AcWithin", "AcWithinCI", "AcRanked", "AcRankedCI", "AcGapRho", "AcGapRhoCI", "AcGapWithin", "AcGapWithinCI",
     "AcFortyRho", "AcFortyRhoCI", "AcFortyWithin", "AcEightyRho", "AcEightyRhoCI", "AcEightyWithin",
     "AcPerCluster", "AcDeffLow", "AcNeffLow", "AcPowerLow", "AcDeffHigh", "AcNeffHigh", "AcPowerHigh", "AcIccX", "AcIccY",
     "AcRelMin", "AcRelMax", "AcRelMinFam", "AcRlRelMin", "AcAttenMin", "AcAttenMax", "AcSplitMin", "AcSplitMax",
     "AcSplitMinFam", "AcSbMin", "AcSbMax", "AcFidPairs", "AcFidCkpts", "AcFidFalsN", "AcFidN", "AcFidFalsList",
     "AcGapDecision", "AcFidWithinWidthMin", "AcFidWithinWidthMax", "AcFidDecSameRho", "AcFidDecSameRhoCI",
     "AcFidDecPairs", "AcFidDecCkpts", "AcDecFidMin", "AcDecFidMax", "AcDecFidInstances"]
    + [f"AcFam{F_WORD[f]}{k}" for f in FAMS for k in ("Rho", "RhoCI")]
    + [f"AcFid{w}{k}" for w, _, _ in FID_ROWS for k in ("Rho", "RhoCI", "Within", "WithinCI")])
AD_NAMES = ["AcAdSetName", "AcAdSetN", "AcAdPairs", "AcAdRho", "AcAdRhoCI", "AcAdWithin", "AcAdWithinCI",
            "AcAdGapRho", "AcAdGapRhoCI"]
# single-plan calibration comparator (E1, E2), permutation null, within-family correlations, and checkpoint-level fidelity rows
AC_EX_NAMES = ["AcEOneRho", "AcEOneRhoCI", "AcEOneWithin", "AcEOneWithinCI", "AcETwo", "AcETwoCI", "AcETwoWithin",
               "AcETwoWithinCI", "AcEOneGapRho", "AcEOneGapRhoCI", "AcETwoGap", "AcETwoGapCI"]
AC_79_NAMES = (["AcPermHi", "AcPermMid", "AcSimPower", "AcRhoFamCI", "AcLoloMin", "AcLoloMax", "AcPearson", "AcPearsonCI",
                "AcFidFalsMeasN", "AcFidFalsMeasList", "AcFidPowerFals", "AcFidSetName", "AcAdRandRho", "AcAdRandRhoCI",
                "AcFrozenMissing", "AcFidVerdicts", "AcFidPoweredN", "AcFidPoweredList", "AcFidFOneCkptFinalsRho",
                "AcFidFOneCkptFinalsRhoCI"]
               + [f"AcFid{w}Ckpt{k}" for w, _, _ in FID_ROWS for k in ("Rho", "RhoCI")])
AC_79_IFS = ["AcPermExceeds", "AcWithinRanks", "AcWithinReaches", "AcFrozen", "AcETwoAbove", "AcETwoBelow",
             "AcETwoWithinAbove", "AcETwoWithinBelow", "FidNotFalsifiable", "FidOnAll", "AcFidFalsOne"]
AC_HOR_SCOPES = (("", "all_24"), ("Fin", "finals_12"))
AC_HOR_METRICS = (("Ov", "ol_overlay_copy_ratio_24m"), ("Sc", "ol_scalar_copy_ratio_24m"),
                  ("Pow", "ol_powered_zones_mae_24m"), ("Poll", "ol_pollution_copy_ratio_24m"))
AC_HOR_TARGETS = (("Infl", "rl_inflation_1000000"), ("Gap", "rl_gap_1000000"), ("Shoot", "random_c120_hack_1000"))
AC_LIN_PREDS = (("Shoot", "random_c120_hack_1000"), ("BOne", "random_c120_hack_1"))
AC_LIN_TARGETS = (("Infl", "rl_inflation_1000000"), ("Gap", "rl_gap_1000000"), ("FaZero", "rl_fa0_1000000"))
AC_REV_NAMES = (
    ["AcHorBoot", "AcHorAllCkpts", "AcHorFinCkpts"]
    + [f"AcHor{sw}{mw}{tw}{k}" for sw, _ in AC_HOR_SCOPES for mw, _ in AC_HOR_METRICS for tw, _ in AC_HOR_TARGETS
       for k in ("Rho", "RhoCI", "RhoLinCI", "Within", "WithinCI", "WithinLinCI",
                 "Part", "PartCI", "WithinPart", "WithinPartCI")]
    + [f"AcHor{sw}{q}" for sw, _ in AC_HOR_SCOPES
       for q in ("RhoMin", "RhoMax", "AbsRhoMax", "WithinMin", "WithinMax", "AbsWithinMax",
                 "PartMin", "PartMax", "AbsPartMax", "WithinPartMin", "WithinPartMax", "AbsWithinPartMax")]
    + ["AcLinBoot", "AcSixLineages"]
    + [f"Ac{pw}{tw}{k}" for pw, _ in AC_LIN_PREDS for tw, _ in AC_LIN_TARGETS
       for k in ("Rho", "RhoCI", "RhoLinCI", "Within", "WithinCI", "WithinLinCI")]
    + [f"AcDiff{tw}{k}" for tw, _ in AC_LIN_TARGETS
       for k in ("Rho", "RhoCI", "RhoLinCI", "Within", "WithinCI", "WithinLinCI")])
NESTED_71 = {"all": ("all 24 checkpoints", 24), "finals": ("the 12 final checkpoints", 12),
             "full_finals": ("the 6 full-data finals", 6)}


def _pairs():
    import csv
    rows = []
    with open(src(PC)) as fh:
        for r in csv.DictReader(fh):
            out = {}
            for k, v in r.items():
                try:
                    out[k] = float(v) if v != "" else float("nan")
                except ValueError:
                    out[k] = v
            rows.append(out)
    return rows


def nested_set(r):
    """The analysis plan's nested set, as main_claim.json reports it (results.seeded_nested_set, analyse_ladder.py):
    (name, checkpoints, the two correlation rows) of the largest complete set, or (None, set(), None)."""
    ns = r["seeded_nested_set"]
    if set(ns["sets"]) != set(NESTED_71):
        raise Missing(f"{MC}: seeded_nested_set.sets {sorted(ns['sets'])} are not the analysis plan's three")
    for k, (name, size) in NESTED_71.items():
        b = ns["sets"][k]
        if b["name"] != name or b["n_expected"] != size or b["n_checkpoints"] != size:
            raise Missing(f"{MC}: seeded_nested_set.sets.{k} is not the analysis plan's {name!r}")
    key = ns["largest_complete_set"]
    if key is None:
        if ns["largest_complete_set_name"] is not None or any(ns["sets"][k]["complete"] for k in NESTED_71):
            raise Missing(f"{MC}: seeded_nested_set says no set is complete but marks one")
        return None, set(), None
    name = ns["largest_complete_set_name"]
    if key not in NESTED_71 or name != NESTED_71[key][0] or not ns["sets"][key]["complete"]:
        raise Missing(f"{MC}: seeded_nested_set's set {key!r} / {name!r} is not one of the analysis plan's, or not complete")
    for k in ns["order"][:ns["order"].index(key)]:
        if ns["sets"][k]["complete"]:
            raise Missing(f"{MC}: a larger set than {name!r} is complete")
    rows = {y: ns["rows"][f"cem_seeded_c40_hack_1000|{y}"] for y in ("rl_inflation_1000000", "rl_gap_1000000")}
    return name, set(ns["sets"][key]["checkpoints"]), rows


def across():
    d = J(MC)
    done = d["status"] == "complete" and d["results"]["status"] == "complete"
    add_if("AcrossDone", done, MC, "status == complete (all 24 checkpoints' 120-city random-search audits and RL runs)")
    if not done:
        for n in AC_NAMES + AD_NAMES + AC_EX_NAMES + AC_79_NAMES + AC_REV_NAMES:
            pending(n, MC, f"main_claim.json status {d['status']}")
        add_if("AcSupported", False, MC, "pending (main_claim.json partial)")
        add_if("AcGapAgrees", False, MC, "pending (main_claim.json partial)")
        add_if("AcFidAnyFals", False, MC, "pending (main_claim.json partial)")
        add_if("AcAdSet", False, MC, "pending (main_claim.json partial)")
        for n in AC_79_IFS:
            add_if(n, False, MC, "pending (main_claim.json partial)")
        stale = PAPER / "tables" / "ladder_curves.tex"
        if stale.exists():
            stale.unlink()
        return
    r = d["results"]
    v = {}

    def put(name, value, loc, source=MC):
        v[name] = (value, source, loc)
    m = r["main"]["c120"]["rl_inflation_1000000"]
    base = "results.main.c120.rl_inflation_1000000."
    if m.get("role") != "decides the main claim" or m.get("decision_status") != "made":
        raise Missing(f"{MC}: the deciding row is not marked as decided")
    ps = m["pooled_spearman"]
    put("AcPairs", ints(m["n_pairs"]), base + "n_pairs")
    put("AcClusters", ints(m["n_checkpoints"]), base + "n_checkpoints")
    put("AcLineages", ints(m["n_lineages"]), base + "n_lineages")
    put("AcRho", s3(ps["value"]), base + "pooled_spearman.value")
    put("AcRhoCI", ci(ps, signed=True), base + "pooled_spearman.lo/hi (percentile)")
    put("AcRhoLinCI", ci(m["pooled_spearman_lineage"], signed=True), base + "pooled_spearman_lineage.lo/hi")
    put("AcKendall", s3(m["pooled_kendall"]["value"]), base + "pooled_kendall.value")
    put("AcKendallCI", ci(m["pooled_kendall"], signed=True), base + "pooled_kendall.lo/hi")
    dec = m["decision"]

    def rule(e):
        """Threshold check applied to a stored Spearman estimate and interval."""
        sup = e["value"] >= 0.4 and excl0(e["lo"], e["hi"])
        fal = e["hi"] < 0.4
        return "supported" if sup and not fal else "falsified" if fal and not sup else "undecided at this power"
    mine = rule(ps)
    if dec != mine:
        raise Missing(f"{MC}: decision {dec!r} but the rule on the stored interval gives {mine!r}")
    put("AcDecision", dec, base + "decision")
    put("AcWithin", s3(m["within_mean_spearman"]["value"]), base + "within_mean_spearman.value")
    put("AcWithinCI", ci(m["within_mean_spearman"], signed=True), base + "within_mean_spearman.lo/hi")
    put("AcRanked", s3(m["ranked_within_spearman"]["value"]), base + "ranked_within_spearman.value")
    put("AcRankedCI", ci(m["ranked_within_spearman"], signed=True), base + "ranked_within_spearman.lo/hi")
    for f in FAMS:
        e = m["per_family"][f]["spearman"]
        put(f"AcFam{F_WORD[f]}Rho", s3(e["value"]), base + f"per_family.{f}.spearman.value")
        put(f"AcFam{F_WORD[f]}RhoCI", ci(e, signed=True), base + f"per_family.{f}.spearman.lo/hi")
    # the abstract and section 5 say the within-family reading does not hold on power, and only there
    zero = sorted(f for f in FAMS if m["per_family"][f]["spearman"]["lo"] <= 0 <= m["per_family"][f]["spearman"]["hi"])
    expect(zero == ["power"], "within a task family the audit ranks emulators, not on power (and on the other four)")
    g = r["main"]["c120"]["rl_gap_1000000"]
    put("AcGapRho", s3(g["pooled_spearman"]["value"]), "results.main.c120.rl_gap_1000000.pooled_spearman.value")
    put("AcGapRhoCI", ci(g["pooled_spearman"], signed=True), "results.main.c120.rl_gap_1000000.pooled_spearman.lo/hi")
    put("AcGapWithin", s3(g["within_mean_spearman"]["value"]), "results.main.c120.rl_gap_1000000.within_mean_spearman.value")
    put("AcGapWithinCI", ci(g["within_mean_spearman"], signed=True), "results.main.c120.rl_gap_1000000.within_mean_spearman.lo/hi")
    gdec = rule(g["pooled_spearman"])
    put("AcGapDecision", gdec, "threshold check applied to results.main.c120.rl_gap_1000000.pooled_spearman")
    for s, sw in (("c40", "Forty"), ("c80", "Eighty")):
        b = r["main"][s]["rl_inflation_1000000"]
        put(f"Ac{sw}Rho", s3(b["pooled_spearman"]["value"]), f"results.main.{s}.rl_inflation_1000000.pooled_spearman.value")
        put(f"Ac{sw}RhoCI", ci(b["pooled_spearman"], signed=True), f"results.main.{s}.rl_inflation_1000000.pooled_spearman.lo/hi")
        put(f"Ac{sw}Within", s3(b["within_mean_spearman"]["value"]), f"results.main.{s}.rl_inflation_1000000.within_mean_spearman.value")
    pw = r["power"]
    if set(pw["at_icc"]) != {"0.3", "0.5"}:
        raise Missing(f"{MC}: power.at_icc keys {sorted(pw['at_icc'])} != ['0.3', '0.5']")
    if pw["n_independent_for_80_per_cent"] != 47:
        raise Missing(f"{MC}: power.n_independent_for_80_per_cent != 47")
    put("AcPerCluster", f"{pw['pairs_per_cluster']:g}", "results.power.pairs_per_cluster")
    for icc, w in (("0.3", "Low"), ("0.5", "High")):
        a = pw["at_icc"][icc]
        put(f"AcDeff{w}", f"{a['design_effect']:.2f}", f"results.power.at_icc.{icc}.design_effect")
        put(f"AcNeff{w}", f"{a['n_eff']:.1f}", f"results.power.at_icc.{icc}.n_eff")
        put(f"AcPower{w}", f2(a["power_spearman_0.4"]), f"results.power.at_icc.{icc}.power_spearman_0.4")
    put("AcIccX", s3(pw["icc_measured"]["random_c120_hack_1000"]), "results.power.icc_measured.random_c120_hack_1000")
    put("AcIccY", s3(pw["icc_measured"]["rl_inflation_1000000"]), "results.power.icc_measured.rl_inflation_1000000")
    rel = r["reliability"]["c120"]
    ra = {f: rel[f]["audit"]["reliability"] for f in FAMS}
    lo_f = min(ra, key=ra.get)
    put("AcRelMin", f2(ra[lo_f]), f"results.reliability.c120.{lo_f}.audit.reliability (minimum over families)")
    put("AcRelMinFam", lo_f, "family of the minimum")
    put("AcRelMax", f2(max(ra.values())), "results.reliability.c120.*.audit.reliability (maximum over families)")
    put("AcRlRelMin", f2(min(rel[f]["rl_inflation_1000000"]["reliability"] for f in FAMS)),
        "results.reliability.c120.*.rl_inflation_1000000.reliability (minimum)")
    obs = [rel[f]["rl_inflation_1000000"]["observed_if_true_0.4"] for f in FAMS]
    put("AcAttenMin", f2(min(obs)), "results.reliability.c120.*.rl_inflation_1000000.observed_if_true_0.4 (minimum)")
    put("AcAttenMax", f2(max(obs)), "results.reliability.c120.*.rl_inflation_1000000.observed_if_true_0.4 (maximum)")
    sp = r["split_sample"]
    spv = {f: sp[f]["spearman"] for f in FAMS}
    lo_s = min(spv, key=spv.get)
    put("AcSplitMin", s3(spv[lo_s]), f"results.split_sample.{lo_s}.spearman (minimum over families)")
    put("AcSplitMinFam", lo_s, "family of the minimum")
    put("AcSplitMax", s3(max(spv.values())), "results.split_sample.*.spearman (maximum)")
    sb = [sp[f]["spearman_brown"]["rho_pooled"] for f in FAMS if sp[f]["spearman_brown"].get("rho_pooled") is not None]
    if not sb:
        raise Missing(f"{MC}: no family has a Spearman-Brown figure (split_sample.*.spearman_brown.rho_pooled)")
    nsb = f" over the {len(sb)} of {len(FAMS)} families with a figure" if len(sb) < len(FAMS) else ""
    put("AcSbMin", f2(min(sb)), "results.split_sample.*.spearman_brown.rho_pooled (minimum)" + nsb)
    put("AcSbMax", f2(max(sb)), "results.split_sample.*.spearman_brown.rho_pooled (maximum)" + nsb)
    sec = r["secondary"]
    vrow = r["secondary_decision_fidelity_verdict_row"]
    vb = sec[vrow]
    if not (vb.get("verdict_row") and vb.get("x_cities") == "c40" and vb.get("y_cities") == "c80"):
        raise Missing(f"{MC}: {vrow} is not the analysis plan's verdict row (decision fidelity on the 40 against the 80)")
    n_finals = sum(1 for e in d["ladder"] if e["stage"] == "final")
    # the verdict rows are read where the analysis plan puts them: results.secondary_d79.measures[].rows, on the set the
    # claim is read on (the 12 finals, where they equal results.secondary's rows, or all 24 with the half-trained
    # checkpoints' test-selection fidelity); results.secondary keeps the finals' rows, reported beside
    s79 = r["secondary_d79"]
    n_set = s79["n_checkpoints_in_set"]
    if n_set not in (n_finals, len(d["ladder"])):
        raise Missing(f"{MC}: secondary_d79 is read on {n_set} checkpoints, neither the finals nor the ladder")
    vrows = {k: (m["measure"], x) for m in s79["measures"] for k, x in m["rows"].items()}
    fals, widths = [], []
    for w, key, nice in FID_ROWS:
        key = key or vrow
        if key not in vrows:
            raise Missing(f"{MC}: {key} is not a verdict row of results.secondary_d79.measures")
        vr = vrows[key][1]
        b = vr["pooled"]
        loc = f"results.secondary_d79.measures[{vrows[key][0]}].rows['{key}'].pooled."
        if sec[key]["n_checkpoints"] != n_finals or sec[key].get("complete_on_finals") is False:
            raise Missing(f"{MC}: {key} covers {sec[key]['n_checkpoints']} of {n_finals} finals although the file is complete")
        if not vr["holds_the_whole_set"] or b["n_checkpoints"] != n_set:
            raise Missing(f"{MC}: {key} holds {b['n_checkpoints']} of the {n_set} checkpoints of the set")
        if n_set == n_finals and vr["falsified"] != sec[key]["interval_abs_above_0.3"]:
            raise Missing(f"{MC}: {key}: secondary_d79 and secondary disagree on the finals")
        put(f"AcFid{w}Rho", s3(b["pooled_spearman"]["value"]), loc + "pooled_spearman.value")
        put(f"AcFid{w}RhoCI", ci(b["pooled_spearman"], signed=True), loc + "pooled_spearman.lo/hi")
        put(f"AcFid{w}Within", s3(b["within_mean_spearman"]["value"]), loc + "within_mean_spearman.value")
        put(f"AcFid{w}WithinCI", ci(b["within_mean_spearman"], signed=True), loc + "within_mean_spearman.lo/hi")
        widths.append(b["within_mean_spearman"]["hi"] - b["within_mean_spearman"]["lo"])
        if vr["falsified"]:
            fals.append(nice)
        if w == "FOne":
            put("AcFidPairs", ints(b["n_pairs"]), loc + "n_pairs")
            put("AcFidCkpts", ints(b["n_checkpoints"]), loc + "n_checkpoints")
        if w == "Dec":
            put("AcFidDecPairs", ints(b["n_pairs"]), loc + "n_pairs")
            put("AcFidDecCkpts", ints(b["n_checkpoints"]), loc + "n_checkpoints")
    put("AcFidWithinWidthMin", f2(min(widths)), "results.secondary_d79 verdict rows, within_mean_spearman: min of hi - lo")
    put("AcFidWithinWidthMax", f2(max(widths)), "results.secondary_d79 verdict rows, within_mean_spearman: max of hi - lo")
    same = sec["fid_decision_c40|c40"]
    put("AcFidDecSameRho", s3(same["pooled_spearman"]["value"]), "results.secondary.fid_decision_c40|c40.pooled_spearman.value")
    put("AcFidDecSameRhoCI", ci(same["pooled_spearman"], signed=True), "results.secondary.fid_decision_c40|c40.pooled_spearman.lo/hi")
    dfv = [c["decision_fidelity"]["c40"] for c in d["checkpoints"]
           if int(c["checkpoint"].split("-samples_")[1]) in FINAL.values()]
    if len(dfv) != n_finals or any(x["status"] != "ok" for x in dfv):
        raise Missing(f"{MC}: decision fidelity on the 40 cities is not ok for every final checkpoint")
    put("AcDecFidMin", f3(min(x["value"] for x in dfv)), "checkpoints[final].decision_fidelity.c40.value (minimum)")
    put("AcDecFidMax", f3(max(x["value"] for x in dfv)), "checkpoints[final].decision_fidelity.c40.value (maximum)")
    ni = {x["n_instances"] for x in dfv}
    if len(ni) != 1:
        raise Missing(f"{MC}: decision fidelity averaged over different instance counts {ni}")
    put("AcDecFidInstances", ints(ni.pop()), "checkpoints[final].decision_fidelity.c40.n_instances (equal for every final)")
    put("AcFidFalsN", ints(len(fals)), "results.secondary_d79 verdict rows: falsified (count true)")
    put("AcFidN", ints(len(FID_ROWS)), "rows of the secondary claim (four measures; the rollout error read three ways)")
    put("AcFidFalsList", words_list(fals) if fals else "none", "rows whose interval on |Spearman| lies above 0.3")
    add_if("AcSupported", dec == "supported", MC, "results.main.c120.rl_inflation_1000000.decision == supported")
    add_if("AcGapAgrees", gdec == dec, MC, "the rule gives the same outcome on the acceptance gap as on the margin inflation")
    add_if("AcFidAnyFals", bool(fals), MC, "any results.secondary_d79 verdict row falsified")
    if set(v) != set(AC_NAMES):
        raise Missing(f"across(): names {sorted(set(AC_NAMES) ^ set(v))}")
    for n in AC_NAMES:
        add(n, *v[n])
    # the adaptive search as a second audit variable, on the analysis plan's nested set (results.seeded_nested_set)
    name, cks, nrows = nested_set(r)
    add_if("AcAdSet", name is not None, MC, "results.seeded_nested_set.largest_complete_set is not null")
    if name is None:
        for n in AD_NAMES + ["AcAdRandRho", "AcAdRandRhoCI"]:
            pending(n, MC, f"results.seeded_nested_set.status: {r['seeded_nested_set']['status']}")
    else:
        loc = "results.seeded_nested_set.rows['cem_seeded_c40_hack_1000|{}']."
        a, ag = nrows["rl_inflation_1000000"], nrows["rl_gap_1000000"]
        add("AcAdSetName", name, MC, "results.seeded_nested_set.largest_complete_set_name")
        add("AcAdSetN", ints(len(cks)), MC, "results.seeded_nested_set.sets[largest].checkpoints (count)")
        add("AcAdPairs", ints(a["n_pairs"]), MC, loc.format("rl_inflation_1000000") + "n_pairs")
        add("AcAdRho", s3(a["pooled_spearman"]["value"]), MC, loc.format("rl_inflation_1000000") + "pooled_spearman.value")
        add("AcAdRhoCI", ci(a["pooled_spearman"], signed=True), MC, loc.format("rl_inflation_1000000") + "pooled_spearman.lo/hi")
        add("AcAdWithin", s3(a["within_mean_spearman"]["value"]), MC, loc.format("rl_inflation_1000000") + "within_mean_spearman.value")
        add("AcAdWithinCI", ci(a["within_mean_spearman"], signed=True), MC, loc.format("rl_inflation_1000000") + "within_mean_spearman.lo/hi")
        add("AcAdGapRho", s3(ag["pooled_spearman"]["value"]), MC, loc.format("rl_gap_1000000") + "pooled_spearman.value")
        add("AcAdGapRhoCI", ci(ag["pooled_spearman"], signed=True), MC, loc.format("rl_gap_1000000") + "pooled_spearman.lo/hi")
        prs = [x for x in _pairs() if x["checkpoint"] in cks and np.isfinite(x["random_c40_hack_1000"])
               and np.isfinite(x["rl_inflation_1000000"])]
        e = HS.clustered_spearman(np.array([x["random_c40_hack_1000"] for x in prs]), np.array([x["rl_inflation_1000000"] for x in prs]),
                                  np.array([x["checkpoint"] for x in prs])).as_dict()
        add("AcAdRandRho", s3(e["value"]), PC, "random_c40_hack_1000 against rl_inflation_1000000 on the nested set's pairs (hpr_dream.stats.clustered_spearman)")
        add("AcAdRandRhoCI", ci(e, signed=True), PC, "the same, cluster bootstrap over checkpoints")
    # single-plan calibration comparator (E1, E2) across 120 cities, within family and pooled
    ex = r["exploratory_logged_plan"]
    for y, tag in (("rl_inflation_1000000", ""), ("rl_gap_1000000", "Gap")):
        row = ex["rows"][f"c120|{y}"]
        if row.get("wording_status") != "made":
            raise Missing(f"{MC}: exploratory_logged_plan c120|{y} carries no wording although the file is complete")
        e1, e2, loc = row["E1"], row["E2"], f"results.exploratory_logged_plan.rows['c120|{y}']."
        add(f"AcEOne{tag}Rho", s3(e1["pooled_spearman"]["value"]), MC, loc + "E1.pooled_spearman.value")
        add(f"AcEOne{tag}RhoCI", ci(e1["pooled_spearman"], signed=True), MC, loc + "E1.pooled_spearman.lo/hi")
        add(f"AcETwo{tag}", s3(e2["pooled_spearman_difference"]["value"]), MC, loc + "E2.pooled_spearman_difference.value")
        add(f"AcETwo{tag}CI", ci(e2["pooled_spearman_difference"], signed=True), MC, loc + "E2.pooled_spearman_difference.lo/hi")
        if tag == "":
            add("AcEOneWithin", s3(e1["within_mean_spearman"]["value"]), MC, loc + "E1.within_mean_spearman.value")
            add("AcEOneWithinCI", ci(e1["within_mean_spearman"], signed=True), MC, loc + "E1.within_mean_spearman.lo/hi")
            add("AcETwoWithin", s3(e2["within_mean_spearman_difference"]["value"]), MC, loc + "E2.within_mean_spearman_difference.value")
            add("AcETwoWithinCI", ci(e2["within_mean_spearman_difference"], signed=True), MC, loc + "E2.within_mean_spearman_difference.lo/hi")
            rd = row["reading"]
            add_if("AcETwoAbove", rd["pooled_spearman_difference"] == "above", MC, loc + "reading.pooled_spearman_difference == above")
            add_if("AcETwoBelow", rd["pooled_spearman_difference"] == "below", MC, loc + "reading.pooled_spearman_difference == below")
            add_if("AcETwoWithinAbove", rd["within_mean_spearman_difference"] == "above", MC, loc + "reading.within_mean_spearman_difference == above")
            add_if("AcETwoWithinBelow", rd["within_mean_spearman_difference"] == "below", MC, loc + "reading.within_mean_spearman_difference == below")
    add_if("AcFrozen", False, MC, "the file is complete: no freeze rule applies")
    pending("AcFrozenMissing", MC, "the file is complete")
    # the analysis plan (results.main_d79): within-family permutation null, within-family reading, simulated power,
    # the original design's sensitivities; each wording was fixed in advance and is chosen here by its boolean field
    m79 = r["main_d79"]
    row = m79["rows"]["c120|rl_inflation_1000000"]
    if row.get("wording_status") != "made":
        raise Missing(f"{MC}: main_d79 c120 row carries no wording although the file is complete")
    loc = "results.main_d79.rows['c120|rl_inflation_1000000']."
    pn = row["permutation_null"]
    if abs(pn["observed"] - ps["value"]) > 1e-9:
        raise Missing(f"{MC}: the permutation null's observed value is not the deciding row's")
    add("AcPermHi", s3(pn["null_p97_5"]), MC, loc + "permutation_null.null_p97_5")
    add("AcPermMid", s3(pn["null_median"]), MC, loc + "permutation_null.null_median")
    add_if("AcPermExceeds", pn["observed_above_null_p97_5"], MC, loc + "permutation_null.observed_above_null_p97_5")
    wf = row["within_family"]
    if abs(wf["estimate"]["value"] - m["within_mean_spearman"]["value"]) > 1e-9:
        raise Missing(f"{MC}: main_d79's within-family estimate is not the deciding row's")
    add_if("AcWithinRanks", wf["excludes_0"], MC, loc + "within_family.excludes_0")
    add_if("AcWithinReaches", wf["reaches_0.4"], MC, loc + "within_family['reaches_0.4']")
    key = f"{m['n_checkpoints']}|{len(FAMS)}|0.4"
    cell = m79["power_cells"][key]
    add("AcSimPower", f2(cell["power_interval_excludes_0"]), MC, f"results.main_d79.power_cells['{key}'].power_interval_excludes_0")
    se = row["sensitivity"]
    add("AcRhoFamCI", ci(se["clustered_by_task_family"], signed=True), MC, loc + "sensitivity.clustered_by_task_family (interval)")
    lr = se["leave_one_lineage_out_range"]
    add("AcLoloMin", s3(min(lr)), MC, loc + "sensitivity.leave_one_lineage_out_range (min)")
    add("AcLoloMax", s3(max(lr)), MC, loc + "sensitivity.leave_one_lineage_out_range (max)")
    add("AcPearson", s3(se["pearson_checkpoint_clusters"]["value"]), MC, loc + "sensitivity.pearson_checkpoint_clusters.value")
    add("AcPearsonCI", ci(se["pearson_checkpoint_clusters"], signed=True), MC, loc + "sensitivity.pearson_checkpoint_clusters (interval)")
    # the analysis plan and the analysis plan (results.secondary_d79): the set, checkpoint-level rows, power, wording
    if s79.get("wording_status") != "made":
        raise Missing(f"{MC}: secondary_d79 carries no wording although the file is complete")
    nset = s79["n_checkpoints_in_set"]
    add("AcFidSetName", "all 24 checkpoints" if nset == 24 else f"the {nset} final checkpoints", MC, "results.secondary_d79.n_checkpoints_in_set")
    add_if("FidOnAll", nset == 24, MC, "results.secondary_d79.n_checkpoints_in_set == 24")
    cl_ = s79["checkpoint_level_beside_existing"]
    for w, k_, _ in FID_ROWS:
        k_ = k_ or vrow
        e = vrows[k_][1]["checkpoint_level"]["spearman"]
        add(f"AcFid{w}CkptRho", s3(e["value"]), MC, f"results.secondary_d79.measures[].rows['{k_}'].checkpoint_level.spearman.value")
        add(f"AcFid{w}CkptRhoCI", ci(e, signed=True), MC, f"... ['{k_}'].checkpoint_level.spearman.lo/hi")
    # Figure 5c draws the final checkpoints (the test selection's own): its checkpoint-level Spearman on them
    e = cl_["fid_test_f1_1m|c120"]["spearman"]
    add("AcFidFOneCkptFinalsRho", s3(e["value"]), MC, "results.secondary_d79.checkpoint_level_beside_existing['fid_test_f1_1m|c120'].spearman.value")
    add("AcFidFOneCkptFinalsRhoCI", ci(e, signed=True), MC, "... .spearman.lo/hi")
    wfa = s79["wording_fixed_in_advance"]
    wd = s79["wording"]
    if not isinstance(wd, dict) or wd.get("claim") not in wfa.values():
        raise Missing(f"{MC}: secondary_d79.wording.claim is not one of the fixed wordings")
    claim = wd["claim"]
    fm = [x["measure"] for x in s79["measures"] if x["falsified"]]
    if len(fm) != s79["n_measures_falsified"]:
        raise Missing(f"{MC}: secondary_d79 counts disagree")
    names = [x["measure"] for x in s79["measures"]]
    if set(wd["by_measure"]) != set(names) or any(wd["by_measure"][n] not in wfa.values() for n in names) or \
            any((wd["by_measure"][n] == wfa["falsified"]) != (n in fm) for n in names):
        raise Missing(f"{MC}: secondary_d79.wording.by_measure disagrees with the measures' verdicts")
    # per-measure fidelity verdicts in stored order
    add("AcFidVerdicts", "; ".join(f"{n}, {wd['by_measure'][n]}" for n in names), MC,
        "results.secondary_d79.wording.by_measure (in the order of results.secondary_d79.measures)")
    # the analysis plan: when the claim is not falsified and some verdict row has power of 0.8 or more, the measures named
    powered = wd["measures_not_falsified_with_power_at_least_0.8"]
    if (claim == wfa["not_falsified"]) != bool(powered):
        raise Missing(f"{MC}: secondary_d79 names powered measures {powered} under the claim wording {claim!r}")
    add("AcFidPoweredN", ints(len(powered)), MC, "results.secondary_d79.wording.measures_not_falsified_with_power_at_least_0.8 (count)")
    add("AcFidPoweredList", words_list(powered) if powered else "none", MC,
        "results.secondary_d79.wording.measures_not_falsified_with_power_at_least_0.8")
    add("AcFidFalsMeasN", ints(len(fm)), MC, "results.secondary_d79.n_measures_falsified")
    add("AcFidFalsMeasList", words_list(fm) if fm else "none", MC, "results.secondary_d79.measures[falsified].measure")
    add_if("AcFidFalsOne", len(fm) == 1, MC, "exactly one measure falsified (the verb's number)")
    pw_ = []
    for x in s79["measures"]:
        v = x["power_pooled_verdict_rows"]
        pw_ += list(v.values()) if isinstance(v, dict) else (list(v) if isinstance(v, list) else [v])
    pw_ = [float(y["power"] if isinstance(y, dict) else y) for y in pw_]
    add("AcFidPowerFals", f2(min(pw_)) if min(pw_) == max(pw_) else f"{f2(min(pw_))} to {f2(max(pw_))}", MC,
        "results.secondary_d79.measures[].power_pooled_verdict_rows (range)")
    add_if("FidNotFalsifiable", claim == wfa["not_falsifiable"], MC, "results.secondary_d79.wording.claim == not_falsifiable")
    if bool(fm) != (claim == wfa["falsified"]):
        raise Missing(f"{MC}: secondary_d79 wording and falsified measures disagree")
    # 24-month open-loop trajectory fidelity predictors across consistent targets (RL inflation, RL gap, 10^3 shooting FA)
    # and 6-lineage cluster bootstrap alongside 24-checkpoint bootstrap (20,000 draws everywhere)
    hz = r["horizon_24m_predictors"]
    if hz.get("status") != "complete" or int(hz.get("n_boot", 0)) != 20000:
        raise Missing(f"{MC}: horizon_24m_predictors status {hz.get('status')!r} or n_boot {hz.get('n_boot')!r}")
    fh_chk = hz["coverage"]["fidelity_horizon_json_check"]
    if not fh_chk.get("present") or float(fh_chk["max_abs_diff_vs_fidelity_files"]) > 1e-12:
        raise Missing(f"{MC}: horizon_24m_predictors disagrees with fidelity_horizon.json ({fh_chk})")
    rev_v = {}

    def put_rev(name, value, loc):
        rev_v[name] = (value, MC, loc)
    put_rev("AcHorBoot", ints(hz["n_boot"]), "results.horizon_24m_predictors.n_boot")
    put_rev("AcHorAllCkpts", ints(hz["coverage"]["n_total_heldout_test_24m"]),
            "results.horizon_24m_predictors.coverage.n_total_heldout_test_24m")
    put_rev("AcHorFinCkpts", ints(hz["coverage"]["n_finals_heldout_test"]),
            "results.horizon_24m_predictors.coverage.n_finals_heldout_test")
    for sw, sk in AC_HOR_SCOPES:
        vals_rho, vals_within, vals_part, vals_wpart = [], [], [], []
        for mw, mk in AC_HOR_METRICS:
            for tw, tk in AC_HOR_TARGETS:
                c = hz["sets"][sk]["metrics"][mk][tk]
                if c.get("status") != "ok":
                    raise Missing(f"{MC}: horizon_24m_predictors {sk} {mk} {tk} not ok")
                cloc = f"results.horizon_24m_predictors.sets.{sk}.metrics.{mk}.{tk}."
                ps_ = c["pooled_spearman"]
                psl_ = c["pooled_spearman_lineage"]
                wm_ = c["within_mean_spearman"]
                wml_ = c["within_mean_spearman_lineage"]
                pt_ = c["partial_spearman_size_data"]
                wpt_ = c["within_partial_spearman_size_data"]
                pfx = f"AcHor{sw}{mw}{tw}"
                put_rev(pfx + "Rho", s3(ps_["value"]), cloc + "pooled_spearman.value")
                put_rev(pfx + "RhoCI", ci(ps_, signed=True), cloc + "pooled_spearman.lo/hi")
                put_rev(pfx + "RhoLinCI", ci(psl_, signed=True), cloc + "pooled_spearman_lineage.lo/hi")
                put_rev(pfx + "Within", s3(wm_["value"]), cloc + "within_mean_spearman.value")
                put_rev(pfx + "WithinCI", ci(wm_, signed=True), cloc + "within_mean_spearman.lo/hi")
                put_rev(pfx + "WithinLinCI", ci(wml_, signed=True), cloc + "within_mean_spearman_lineage.lo/hi")
                put_rev(pfx + "Part", s3(pt_["value"]), cloc + "partial_spearman_size_data.value")
                put_rev(pfx + "PartCI", ci(pt_, signed=True), cloc + "partial_spearman_size_data.lo/hi")
                put_rev(pfx + "WithinPart", s3(wpt_["value"]), cloc + "within_partial_spearman_size_data.value")
                put_rev(pfx + "WithinPartCI", ci(wpt_, signed=True), cloc + "within_partial_spearman_size_data.lo/hi")
                vals_rho.append(float(ps_["value"]))
                vals_within.append(float(wm_["value"]))
                vals_part.append(float(pt_["value"]))
                vals_wpart.append(float(wpt_["value"]))
        for tag, xs, desc in (("Rho", vals_rho, "pooled_spearman"),
                              ("Within", vals_within, "within_mean_spearman"),
                              ("Part", vals_part, "partial_spearman_size_data"),
                              ("WithinPart", vals_wpart, "within_partial_spearman_size_data")):
            sloc = f"results.horizon_24m_predictors.sets.{sk} (4 metrics x 3 targets): {desc}"
            put_rev(f"AcHor{sw}{tag}Min", s3(min(xs)), sloc + " minimum")
            put_rev(f"AcHor{sw}{tag}Max", s3(max(xs)), sloc + " maximum")
            put_rev(f"AcHor{sw}Abs{tag}Max", f3(max(abs(x) for x in xs)), sloc + " max |rho|")
    lb = r["lineage_6_cluster_bootstrap"]
    if lb.get("status") != "complete" or int(lb.get("n_boot", 0)) != 20000 or len(lb.get("lineages", {})) != 6:
        raise Missing(f"{MC}: lineage_6_cluster_bootstrap incomplete ({lb.get('status')}, n_boot={lb.get('n_boot')})")
    put_rev("AcLinBoot", ints(lb["n_boot"]), "results.lineage_6_cluster_bootstrap.n_boot")
    put_rev("AcSixLineages", ints(len(lb["lineages"])), "results.lineage_6_cluster_bootstrap.lineages (count)")
    for pw__, pk in AC_LIN_PREDS:
        for tw, tk in AC_LIN_TARGETS:
            rk = f"{pk}|{tk}"
            c = lb["rows"][rk]
            if c.get("status") != "ok":
                raise Missing(f"{MC}: lineage_6_cluster_bootstrap {rk} not ok")
            cloc = f"results.lineage_6_cluster_bootstrap.rows['{rk}']."
            p24, p6 = c["pooled_spearman_ckpt24"], c["pooled_spearman_lineage6"]
            w24, w6 = c["within_mean_spearman_ckpt24"], c["within_mean_spearman_lineage6"]
            pfx = f"Ac{pw__}{tw}"
            put_rev(pfx + "Rho", s3(p24["value"]), cloc + "pooled_spearman_ckpt24.value")
            put_rev(pfx + "RhoCI", ci(p24, signed=True), cloc + "pooled_spearman_ckpt24.lo/hi (24-ckpt cluster bootstrap)")
            put_rev(pfx + "RhoLinCI", ci(p6, signed=True), cloc + "pooled_spearman_lineage6.lo/hi (6-lineage cluster bootstrap)")
            put_rev(pfx + "Within", s3(w24["value"]), cloc + "within_mean_spearman_ckpt24.value")
            put_rev(pfx + "WithinCI", ci(w24, signed=True), cloc + "within_mean_spearman_ckpt24.lo/hi (24-ckpt cluster bootstrap)")
            put_rev(pfx + "WithinLinCI", ci(w6, signed=True), cloc + "within_mean_spearman_lineage6.lo/hi (6-lineage cluster bootstrap)")
    for tw, tk in AC_LIN_TARGETS:
        c = lb["differences_1000_minus_1"][tk]
        if c.get("status") != "ok":
            raise Missing(f"{MC}: lineage_6_cluster_bootstrap diff {tk} not ok")
        cloc = f"results.lineage_6_cluster_bootstrap.differences_1000_minus_1.{tk}."
        p24, p6 = c["pooled_spearman_diff_ckpt24"], c["pooled_spearman_diff_lineage6"]
        w24, w6 = c["within_mean_spearman_diff_ckpt24"], c["within_mean_spearman_diff_lineage6"]
        pfx = f"AcDiff{tw}"
        put_rev(pfx + "Rho", s3(p24["value"]), cloc + "pooled_spearman_diff_ckpt24.value")
        put_rev(pfx + "RhoCI", ci(p24, signed=True), cloc + "pooled_spearman_diff_ckpt24.lo/hi (24-ckpt cluster bootstrap)")
        put_rev(pfx + "RhoLinCI", ci(p6, signed=True), cloc + "pooled_spearman_diff_lineage6.lo/hi (6-lineage cluster bootstrap)")
        put_rev(pfx + "Within", s3(w24["value"]), cloc + "within_mean_spearman_diff_ckpt24.value")
        put_rev(pfx + "WithinCI", ci(w24, signed=True), cloc + "within_mean_spearman_diff_ckpt24.lo/hi (24-ckpt cluster bootstrap)")
        put_rev(pfx + "WithinLinCI", ci(w6, signed=True), cloc + "within_mean_spearman_diff_lineage6.lo/hi (6-lineage cluster bootstrap)")
    if set(rev_v) != set(AC_REV_NAMES):
        raise Missing(f"across() rev names {sorted(set(AC_REV_NAMES) ^ set(rev_v))}")
    for n in AC_REV_NAMES:
        add(n, *rev_v[n])
    rows = _pairs()
    table_curves(rows, cks)


def table_curves(rows, ad_set):
    """Appendix: every ladder checkpoint's random-search curve on all 120 cities and its adaptive search at 10^3
    (40 cities) where the analysis plan's set holds it; events over instances pooled across the five families."""
    def pool(ck, key, nkey):
        rs = [x for x in rows if x["checkpoint"] == ck]
        n = np.array([x[nkey] for x in rs], float)
        v = np.array([x[key] for x in rs], float)
        return float((v * n).sum() / n.sum())
    cks = sorted({x["checkpoint"] for x in rows},
                 key=lambda c: (c.split("_")[0], int(c.split("_")[1][:-1]), c.split("_")[2].split("-")[0], c))
    lines = []
    for ck in cks:
        w = ckpt_words(ck).split(" ")
        cells = [w[1], w[2], w[3].replace("-data", ""), w[0]]
        cells += [f3(pool(ck, f"random_c120_hack_{b}", f"random_c120_n_{b}")) for b in (10, 100, 1000)]
        cells += [s3(pool(ck, "random_c120_diff_1000", "random_c120_n_paired_1000")),
                  f3(pool(ck, "random_c120_oracle_accept_1000", "random_c120_n_1000")),
                  f3(pool(ck, "random_c120_perfect_hack_1000", "random_c120_n_paired_1000"))]
        if ck in ad_set:
            cells += [f3(pool(ck, "cem_seeded_c40_hack_1000", "cem_seeded_c40_n_1000")),
                      s3(pool(ck, "cem_seeded_c40_diff_1000", "cem_seeded_c40_n_paired_1000")),
                      f3(pool(ck, "cem_seeded_c40_oracle_accept_1000", "cem_seeded_c40_n_1000"))]
        else:
            cells += ["--", "--", "--"]
        if any("nan" in c for c in cells):
            raise Missing(f"{PC}: {ck} lacks a value of the curves table although main_claim.json is complete")
        lines.append(" & ".join(cells) + r" \\")
    (PAPER / "tables" / "ladder_curves.tex").write_text(
        "% Generated by paper/scripts/make_numbers.py from results/analysis/pairs.csv\n"
        r"\setlength{\tabcolsep}{2pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llllccccccccc@{}}" "\n" r"\toprule" "\n"
        r" & & & & \multicolumn{6}{c}{Random shooting (120 cities)} & \multicolumn{3}{c}{Adaptive CEM, $10^{3}$ (40-city core)} \\"
        "\n" r"\cmidrule(lr){5-10}\cmidrule(l){11-13}" "\n"
        r"Objective & Size & Data & Stage & $10^{1}$ & $10^{2}$ & $10^{3}$ & Excess & Truly passing & Exact ref. & False acc. & Excess & Truly passing \\"
        "\n" r"\midrule" "\n" + "\n".join(lines) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n")


# ---------------------------------------------------------------------------------------------
# tables
# ---------------------------------------------------------------------------------------------
def tex_ci(d, signed=False):
    v = est(d)
    if v is None:
        return "n/a"
    return (s3(v) if signed else f3(v)) + " {\\tiny" + ci(d, signed) + "}"


def table_main(groups):
    lines = []
    for m, mn in (("random", "Random"), ("cem_seeded", "Adaptive"), ("best_of_n", "Best-of-$N$")):
        bs = [b for b in (1, 10, 100, 1000) if ("all", m, b) in groups]
        for i, b in enumerate(bs):
            g = groups[("all", m, b)]
            e, p = g["emulator"], g["perfect_emulator"]
            w = groups.get(("in_band", m, b))
            lines.append(" & ".join([
                mn if i == 0 else "", "$10^{%d}$" % int(np.log10(b)), ints(g["n_paired"]),
                tex_ci(e["hackability"]), f3(est(p["hackability"])), tex_ci(g["difference"], True),
                f3(est(e["oracle_accept"])) + "/" + f3(est(p["oracle_accept"])),
                f3(est(e["false_rejection"])) + "/" + f3(est(p["false_rejection"])),
                ints(w["n_paired"]) if w else "--", tex_ci(w["difference"], True) if w else "--",
                (f3(est(w["emulator"]["oracle_accept"])) + "/" + f3(est(w["perfect_emulator"]["oracle_accept"]))) if w else "--",
            ]) + r" \\")
        lines.append(r"\addlinespace[2pt]")
    # reinforcement learning in the audit's unit (R2 M1): plan 0 of the policies trained in the main checkpoint and over
    # the ladder, at 1,000,000 months, beside a perfect emulator replaying the same plans
    R = J(RLX)["results"]
    for blk, nm in (("main", "RL, main"), ("ladder", "RL, ladder")):
        x = R[blk]["1000000"]["all"]
        tw_ = lambda q, sg=False: twci(x[q], signed=sg).replace("[", "{\\tiny[").replace("]", "]}")
        lines.append(" & ".join([nm, "$10^{6}$ m.", ints(x["fa0"]["n_rows"]), f3(x["fa0"]["value"]) + " " + tw_("fa0"),
                                 f3(x["perfect_fa0"]["value"]), s3(x["excess0"]["value"]) + " " + tw_("excess0", True),
                                 f3(x["oracle_accept0"]["value"]) + "/--", "--", "--", "--", "--"]) + r" \\")
    lines.append(r"\addlinespace[2pt]")
    (PAPER / "tables" / "main_reference.tex").write_text(
        "% Generated by paper/scripts/make_numbers.py from " + f"{MAIN}/reference.json and {SEEDED}/reference.json" + "\n"
        r"\setlength{\tabcolsep}{1.2pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrlrlccrlc@{}}" "\n" r"\toprule" "\n"
        r"& & \multicolumn{6}{c}{All instances} & \multicolumn{3}{c}{Well posed} \\" "\n"
        r"\cmidrule(lr){3-8}\cmidrule(l){9-11}" "\n"
        r"Search & $B$ & $n$ & False acceptance & Exact ref. & Difference & Truly passing & False rej. & $n$ & Difference & Truly passing \\" "\n"
        r"\midrule" "\n" + "\n".join(lines[:-1]) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n")


def table_family(groups, wp):
    body = []
    for fam in FAMS:
        for m, mn in (("random", "random"), ("cem_seeded", "adaptive")):
            g = groups[(f"task:{fam}", m, 1000)]
            e, p = g["emulator"], g["perfect_emulator"]
            w = wp[(fam, m, True)][0]
            body.append(" & ".join([fam if m == "random" else "", mn, ints(g["n_paired"]), tex_ci(e["hackability"]),
                                    f3(est(p["hackability"])), tex_ci(g["difference"], True),
                                    f3(est(e["judge_accept"])) + "/" + f3(est(p["judge_accept"])),
                                    f3(est(e["oracle_accept"])) + "/" + f3(est(p["oracle_accept"])),
                                    ints(w["n"]), tex_ci(w["diff"], True),
                                    f3(w["orc"]) + "/" + f3(w["porc"])]) + r" \\")
        body.append(r"\addlinespace[2pt]")
    body = body[:-1]
    (PAPER / "tables" / "family_thou.tex").write_text(
        "% Generated by paper/scripts/make_numbers.py from the two reference.json files of the main checkpoint\n"
        r"\setlength{\tabcolsep}{1.5pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrlrlccrlc@{}}" "\n" r"\toprule" "\n"
        r"& & \multicolumn{6}{c}{All instances} & \multicolumn{3}{c}{Well posed} \\" "\n"
        r"\cmidrule(lr){3-8}\cmidrule(l){9-11}" "\n"
        r"Task & Search & $n$ & False acceptance & Exact ref. & Difference & Accepted & Truly passing & $n$ & Difference & Truly passing \\" "\n"
        r"\midrule" "\n" + "\n".join(body) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n")


def table_test(rows):
    lab = {"os": "one-step", "sf": "pushforward"}
    lines = []
    for r in rows:
        parts = r["run"].split("_")
        obj, size, scale = parts[:3]
        seed = parts[3][1:] if len(parts) > 3 else "0"
        lines.append(" & ".join([lab[obj], size.upper(), scale, seed, f3(r["f1"]), f3(r["raw"]), f3(r["f1_12"]), f3(r["pop12"]),
                                 f3(r["funds12"])]) + r" \\")
    g = J(test_json("os_50m_full"))["gap_closed"]
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{4}{@{}l}{Engine under another seed} & " + " & ".join(
        [f3(g["tile_F1_1m_structural_T1"]["floor"]), f3(g["tile_F1_1m_raw_T1"]["floor"]), f3(g["tile_F1_since_start_12m_structural"]["floor"]),
         f3(g["pop_median_rel_12m"]["floor"]), f3(g["funds_median_rel_12m"]["floor"])]) + r" \\")
    lines.append(r"\multicolumn{4}{@{}l}{Copy-last-state} & " + " & ".join(
        [f3(g["tile_F1_1m_structural_T1"]["copy"]), f3(g["tile_F1_1m_raw_T1"]["copy"]), f3(g["tile_F1_since_start_12m_structural"]["copy"]),
         f3(g["pop_median_rel_12m"]["copy"]), f3(g["funds_median_rel_12m"]["copy"])]) + r" \\")
    (PAPER / "tables" / "ladder_test.tex").write_text(
        "% Generated by paper/scripts/make_numbers.py from results/fidelity/ladder/<run>/test/<run>_samples_<final>_dec-a.json\n"
        r"\setlength{\tabcolsep}{3pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llllccccc@{}}" "\n" r"\toprule" "\n"
        r"Objective & Size & Data & Seed & F1, 1 m & Raw F1, 1 m & F1, 12 m & Pop., 12 m & Funds, 12 m \\" "\n"
        r"\midrule" "\n" + "\n".join(lines) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n")


def table_rl(full, complete):
    lines = []
    order = sorted(complete, key=lambda c: (c.split("_")[0], int(c.split("_")[1][:-1]), c.split("_")[2].split("-")[0], c))
    for c in order:
        rs = [r for r in full if r["ck"] == c]
        d = np.mean([r["rate_dream_accept"] for r in rs])
        o = np.mean([r["rate_engine_open_accept"] for r in rs])
        cl = np.mean([r["rate_engine_closed_accept"] for r in rs])
        m = np.mean([r["inflation_open"] for r in rs])
        w = ckpt_words(c).split(" ")
        lines.append(" & ".join([w[1], w[2], w[3].replace("-data", ""), w[0], ints(len(rs)), f3(d), f3(o), s3(d - o), f3(cl), s3(m)]) + r" \\")
    (PAPER / "tables" / "rl_checkpoints.tex").write_text(
        "% Generated by paper/scripts/make_numbers.py from results/rl/<checkpoint>__<family>__s<seed>__tasks_v2_H24/eval3_001000000.summary.json\n"
        r"\setlength{\tabcolsep}{2.5pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llllrccccc@{}}" "\n" r"\toprule" "\n"
        r"Objective & Size & Data & Stage & Runs & Dream accepts & Oracle accepts & Gap & Closed loop & Margin inflation \\" "\n"
        r"\midrule" "\n" + "\n".join(lines) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n")


def write():
    PAPER.joinpath("tables").mkdir(exist_ok=True)
    clean_cmt = lambda s: (s.replace("\n", " ").replace("\u00d7", "x").replace("\u2212", "-")
                           .replace("\u2192", "->").replace("\u00b7", ".").replace("\u2014", "--"))
    out = ["% Generated by paper/scripts/make_numbers.py. Do not edit: every value is read from the file named above it.",
           "% Sources and locators: numbers_ledger.md and numbers_manifest.json."]
    for name, flag, source, loc in IFS:
        out.append(clean_cmt(f"% {source} :: {loc}"))
        out.append(f"\\newif\\if{name}\\{name}{'true' if flag else 'false'}")
    for name, value, source, loc in MACROS:
        out.append(clean_cmt(f"% {source} :: {loc}"))
        out.append(f"\\newcommand{{\\{name}}}{{{value}}}")
    (PAPER / "numbers.tex").write_text("\n".join(out) + "\n")
    led = ["# Macro ledger (generated by paper/scripts/make_numbers.py)", "",
           "Switches (`\\if<name>`) choose between a result's prose and its slot; a macro whose value is "
           f"`{PENDING}` belongs to a result that is still running and was not read.", "",
           "| macro | value | source | locator |", "|---|---|---|---|"]
    for name, flag, source, loc in IFS:
        led.append(f"| `\\if{name}` | {'true' if flag else 'false'} | `{source}` | {loc.replace('|', '/')} |")
    for name, value, source, loc in MACROS:
        led.append(f"| `\\{name}` | {value} | `{source}` | {loc.replace('|', '/').replace(chr(10), ' ')} |")
    (PAPER / "numbers_ledger.md").write_text("\n".join(led) + "\n")
    (PAPER / "numbers_manifest.json").write_text(json.dumps(
        {"switches": [{"name": n, "value": f, "source": s, "locator": l} for n, f, s, l in IFS],
         "macros": [{"name": n, "value": v, "source": s, "locator": l} for n, v, s, l in MACROS],
         "sources_sha256": {rel(k): v for k, v in sorted(SOURCES.items())}}, indent=1) + "\n")
    npend = sum(1 for m in MACROS if m[1] == PENDING)
    print(f"numbers.tex: {len(MACROS)} macros ({npend} pending) and {len(IFS)} switches from {len(SOURCES)} source files")
    for name, flag, _, _ in IFS:
        print(f"  \\if{name}: {'true' if flag else 'false'}")


# ---------------------------------------------------------------------------------------------
# 18. the revision after the three reviews : facts the reviews asked for, from files that exist
# ---------------------------------------------------------------------------------------------
OV_NICE = {"pop_density": "population density", "traffic": "traffic", "pollution": "pollution", "land_value": "land value",
           "crime": "crime", "rate_of_growth": "rate of growth", "fire_coverage": "fire coverage",
           "police_coverage": "police coverage"}


def _num(s):
    return float(s.replace(",", ""))


def revision():
    # R3 F2: what was re-replayed, split by store
    dp = "results/data/summary.json"
    v = J(dp)["verify"]
    for k, w in (("train_full", "Train"), ("heldout_eval", "HeldOut"), ("train_eval", "TrainEval")):
        add("Verify" + w, ints(v[k]["checked"]), dp, f"verify.{k}.checked")
    # R2 F1: the main checkpoint's fidelity at the task horizon, test selection (its summary, generated from the JSON)
    sm = "results/fidelity/ladder/os_50m_full/test/summary.md"
    t = T(sm)
    ov = {r[0]: (_num(r[1]), _num(r[2])) for r in
          _table_after(t, "#### Overlays at 24 months, all plans: error ratio to copy-last-state")[1:]}
    if set(ov) != set(OV_NICE):
        raise Missing(f"{sm}: overlays {sorted(ov)}")
    loc = "table 'Overlays at 24 months, all plans: error ratio to copy-last-state'"
    add("HorOverlays", ints(len(ov)), sm, loc + " (rows)")
    best = min(ov, key=lambda k: ov[k][0])
    rest = [ov[k][0] for k in ov if k != best]
    add("HorBestOverlay", OV_NICE[best], sm, loc + ": the overlay with the lowest model ratio")
    add("HorBestRatio", f3(ov[best][0]), sm, loc + f", row {best}, model sample")
    add("HorRestN", ints(len(rest)), sm, loc + ": the other overlays (count)")
    add("HorRestMin", f3(min(rest)), sm, loc + ": the other overlays, model sample, minimum")
    add("HorRestMax", f3(max(rest)), sm, loc + ": the other overlays, model sample, maximum")
    eng = [e for _, e in ov.values()]
    add("HorEngMin", f3(min(eng)), sm, loc + ": engine yardstick, minimum over overlays")
    add("HorEngMax", f3(max(eng)), sm, loc + ": engine yardstick, maximum over overlays")
    expect(min(rest) >= 0.99, "on every overlay but one the 24-month error is no better than copying the start state")
    worst = max(ov, key=lambda k: ov[k][0] / ov[k][1])
    expect(worst == "fire_coverage", "fire coverage is the overlay on which the emulator falls furthest behind the engine")
    add("HorFireEmu", f3(ov["fire_coverage"][0]), sm, loc + ", row fire_coverage, model sample")
    add("HorFireEng", f3(ov["fire_coverage"][1]), sm, loc + ", row fire_coverage, engine yardstick")
    add("HorPollEmu", f3(ov["pollution"][0]), sm, loc + ", row pollution, model sample")
    add("HorPollEng", f3(ov["pollution"][1]), sm, loc + ", row pollution, engine yardstick")
    hd = [h for h in re.findall(r"^#### Per scalar at 24 months, open-loop plans \((\d+)\): mean absolute error$", t, re.M)]
    if len(hd) != 1:
        raise Missing(f"{sm}: open-loop 24-month scalar table not found once")
    sc = {r[0]: r[1:] for r in _table_after(t, f"#### Per scalar at 24 months, open-loop plans ({hd[0]})")[1:]}
    add("HorOpenPlans", ints(int(hd[0])), sm, "table 'Per scalar at 24 months, open-loop plans (N)': N")
    pz = sc["powered_zones"]
    loc2 = f"table 'Per scalar at 24 months, open-loop plans ({hd[0]})', row powered_zones"
    add("HorPowEmu", pz[0], sm, loc2 + ", model sample")
    add("HorPowEng", pz[1], sm, loc2 + ", engine yardstick")
    add("HorPowCopy", pz[2], sm, loc2 + ", copy")
    expect(_num(pz[0]) > _num(pz[2]) > _num(pz[1]), "powered zones drift further than copying on open-loop plans")
    gm = J(test_json("os_50m_full"))["gap_closed"]
    add("TestPopRatio", f"{gm['pop_median_rel_12m']['model'] / gm['pop_median_rel_12m']['floor']:.1f}", test_json("os_50m_full"),
        "gap_closed.pop_median_rel_12m.model / .floor")
    add("TestFundsRatio", f"{gm['funds_median_rel_12m']['model'] / gm['funds_median_rel_12m']['floor']:.0f}", test_json("os_50m_full"),
        "gap_closed.funds_median_rel_12m.model / .floor")
    # R2 M4: one checkpoint's interval on one-month F1 against the ladder's range; R3 M7: the ladder's finals only
    mj = test_json("os_50m_full")
    ci95 = J(mj)["onestep"]["model_T1"]["structural"]["f1_ci95_by_family"]
    add("TestMainFOneCI", f"[{f3(ci95[0])}, {f3(ci95[1])}]", mj, "onestep.model_T1.structural.f1_ci95_by_family")
    lad = [r for r in TEST_RUNS if LADDER_RUN.fullmatch(r)]
    f1s = [J(test_json(r))["gap_closed"]["tile_F1_1m_structural_T1"]["model"] for r in lad]
    srcs = [test_json(r) for r in lad]
    add_multi("LadFinals", ints(len(lad)), srcs, "final checkpoints of the ladder's twelve lineages (no ensemble seeds)")
    add_multi("LadFOneMin", f3(min(f1s)), srcs, "min over the ladder's finals of gap_closed.tile_F1_1m_structural_T1.model")
    add_multi("LadFOneMax", f3(max(f1s)), srcs, "max over the ladder's finals of gap_closed.tile_F1_1m_structural_T1.model")
    expect(ci95[1] - ci95[0] > max(f1s) - min(f1s), "the ladder's F1 range is narrower than one checkpoint's interval")
    add("EnsSeedRuns", ints(len(TEST_RUNS) - len(lad)), srcs[0], "runs of the 16 that are further seeds of the main configuration")
    # R1 F1 / R3 M3: the 285 records of the patching figure, by search
    pp = f"{MAIN}/patching.jsonl.gz"
    pr = [json.loads(l) for l in gzip.open(src(pp), "rt")]
    base = [r for r in pr if r.get("primary_set") and r["mask"] == "none"]
    by = {}
    for r in base:
        by[r["method"]] = by.get(r["method"], 0) + 1
    for m, w in (("random", "Rand"), ("random_verdict", "Verd"), ("best_of_n", "Bon"), ("cem", "Cem")):
        add("PtN" + w, ints(by.get(m, 0)), pp, f"records with primary_set and mask none, method {m}")
    if sum(by.values()) != len(base) or set(by) - {"random", "random_verdict", "best_of_n", "cem"}:
        raise Missing(f"{pp}: methods {by}")
    # R2 M2, R3 M8, R1 m12: the penalty's lambda = 0 row (its added mean-margin condition alone), both searches
    fp = "results/defences/frontier.json"
    fr = J(fp)
    for s, w in (("random", ""), ("cem_seeded", "Ad")):
        rows = {r["setting"]: r for r in fr["frontier"][s]["rows"]}
        for st, sw in (("penalty0", "PenZero"), ("penalty1", "PenOne"), ("member0", "MemberZ"), ("temp1.25", "TempHigh"),
                       ("deflation-member0", "DeflMember"), ("halt95", "HaltHigh")):
            if s == "cem_seeded" and sw == "TempHigh":
                continue
            r = rows[st]
            add("Def" + w + sw + "Hack", f3(est(r["hackability"])), fp, f"frontier.{s}.rows[{st}].hackability.value")
            add("Def" + w + sw + "FalseRej", f3(est(r["false_rejection"])), fp, f"frontier.{s}.rows[{st}].false_rejection.value")
        expect(rows["halt95"]["n_hacked"] == rows["ensemble"]["n_hacked"] or s != "random",
               "the 95th-percentile halt selects as the undefended ensemble under random search")
    dz = fr["design"]
    add("DefKSearch", ints(dz["k_search_per_member"]), fp, "design.k_search_per_member")
    add("DefKVerdict", ints(dz["k_verdict_per_member"]), fp, "design.k_verdict_per_member")
    add("DefKSearchEns", ints(dz["k_search_per_member"] * len(dz["members"])), fp, "design.k_search_per_member x members")
    add("DefKVerdictEns", ints(dz["k_verdict_per_member"] * len(dz["members"])), fp, "design.k_verdict_per_member x members")
    # R2 M3: the external check, the direction of its own result and the facts that bear on reading it
    es = "results/external/summary.md"
    for task, tw in (("cheetah-run", "Cheetah"), ("walker-walk", "Walker")):
        cp = f"cards/external/{task}.json"
        c = J(cp)
        for b in (1, 1000):
            r = [x for x in c["hackability_curve"] if x["attacker"] == "random_shooting" and x["scoring"] == "margin"
                 and int(x["budget"]) == b]
            if len(r) != 1:
                raise Missing(f"{cp}: random_shooting margin {b}")
            if b == 1:
                add(tw + "RandOneHack", f3(est(r[0]["hackability"])), cp, "hackability_curve[random_shooting,margin,1].hackability.value")
    quote("CheetahResid", "median over starts of the per-start median 2.871", es, "2.9")
    quote("WalkerResid", "median over starts of the per-start median 1.926", es, "1.9")
    quote("ExtMppiHorizon", "MPPI settings read from the run: horizon=3", es, "3")
    quote("ExtAccLo", "acceptance must lie in [0.2, 0.5]", es, "0.2")
    add("ExtAccHi", "0.5", es, 'text "acceptance must lie in [0.2, 0.5]"')
    mc_d = J(MC)["results"]
    add("PermPct", "97.5", MC, "results.main_d79: 97.5th percentile permutation threshold")
    add("PermN", ints(mc_d["main_d79"]["permutation"]["n_perm"]), MC, "results.main_d79.permutation.n_perm")
    add("FidPowerRho", f"{mc_d['secondary_d79']['power']['c120']['true_checkpoint_level_spearman']:.1f}", MC,
        "results.secondary_d79.power.c120.true_checkpoint_level_spearman")
    add("FidPowerBar", "0.8", MC, "results.secondary_d79.power.c120: 80% statistical power threshold")
    add("CorrLevel", "98.33", MC, "Bonferroni-corrected 3-comparison confidence level (1 - 0.05/3)")
    # R1 F1, m10, M6: the patching arm's paired comparisons with corrected intervals, by family, and the mechanism rule
    pc = "results/analysis/patching_controls.json"
    P_ = J(pc)
    st = P_["settings"]
    if st["comparisons"] != 18 or st["correction"] != "Bonferroni":
        raise Missing(f"{pc}: settings {st}")
    if st.get("n_boot") != 20000 or st.get("n_boot_corrected") != 20000:
        raise Missing(f"{pc}: expected 20,000 BCa resamples everywhere, got {st}")
    add("PcBoot", ints(st["n_boot"]), pc, "settings.n_boot (= settings.n_boot_corrected)")
    add("PcCorrLevel", f"{100 * st['level_corrected']:.2f}", pc, "settings.level_corrected x 100")
    add("PcComparisons", ints(st["comparisons"]), pc, "settings.comparisons")
    SUBW = {"power": "Power", "treasury": "Treasury", "valves": "Valves", "zone_growth": "ZoneGrowth", "pollution": "Pollution",
            "traffic": "Traffic", "land_value": "LandValue", "crime": "Crime", "fire": "Fire"}
    above = []
    # the paired comparisons use part 3 
    p3 = P_.get("part3")
    if not p3 or p3.get("warnings"):
        raise Missing(f"{pc}: part 3 (the symmetric cell rules on every record) is missing or has warnings")
    SYM = {"fire": "fire_sym", "zone_growth": "zone_growth_sym"}
    for scope, sw in (("all", "All"), ("recover", "Recov"), ("other four", "Other")):
        pr = p3["paired"][scope]
        for sub, w in SUBW.items():
            both = True
            mk_ = SYM.get(sub, sub)
            for ctl, cw in (("random", "Size"), ("changed", "Chg")):
                e = pr[f"{mk_} - {ctl}~{mk_}"]
                if e["interval_corr"] != "BCa":
                    raise Missing(f"{pc}: {scope} {sub} {ctl} interval")
                loc = f"part3.paired['{scope}']['{mk_} - {ctl}~{mk_}']"
                add(f"Pc{w}{cw}{sw}", s3(e["diff"]), pc, loc + ".diff")
                add(f"Pc{w}{cw}{sw}CI", f"[{s3(e['lo_corr'])}, {s3(e['hi_corr'])}]", pc, loc + ".lo_corr/hi_corr")
                both = both and e["lo_corr"] > 0
            if scope == "all" and both:
                above.append(NICE[sub])
    add("PcAboveBoth", words_list(above) if above else "none", pc, "subsystems whose corrected paired differences against both controls lie above 0 (all records, part 3)")
    expect(above == [], "over all records no subsystem's patch is above both of its controls (symmetric cell rules)")
    fr3 = p3["flip_rates"]
    for sc, sw in (("all", "All"), ("recover", "Recov"), ("other four", "Other")):
        add(f"PcSymFire{sw}Rate", f2(fr3[sc]["fire_sym"]["rate"]), pc, f"part3.flip_rates['{sc}'].fire_sym.rate")
        add(f"PcSymZone{sw}Rate", f2(fr3[sc]["zone_growth_sym"]["rate"]), pc, f"part3.flip_rates['{sc}'].zone_growth_sym.rate")
    rs_ = P_["part1"]["restricted"]
    fr_ = rs_["flip_rates"]["recover"]["fire"]
    add("PcRandFireRecovK", ints(fr_["k"]), pc, "part1.restricted.flip_rates.recover.fire.k (random search, margin-scored)")
    add("PcRandFireRecovN", ints(fr_["n"]), pc, "part1.restricted.flip_rates.recover.fire.n")
    ro = rs_["paired"]["other four"]
    for ctl, cw in (("random", "Size"), ("changed", "Chg")):
        e = ro[f"fire - {ctl}~fire"]
        add(f"PcRandFire{cw}OtherCI", f"[{s3(e['lo_corr'])}, {s3(e['hi_corr'])}]", pc, f"part1.restricted.paired['other four']['fire - {ctl}~fire'] corrected")
        add(f"PcRandFire{cw}Other", s3(e["diff"]), pc, f"part1.restricted.paired['other four']['fire - {ctl}~fire'].diff")
    mr = P_["part1"]["mechanism_rule"]
    add("PcRedraw", f2(mr["none"]["rate"]), pc, "part1.mechanism_rule.none.rate")
    add("PcRedrawCI", f"[{f2(mr['none']['lo'])}, {f2(mr['none']['hi'])}]", pc, "part1.mechanism_rule.none.lo/hi")
    expect(mr["none"]["rate"] > mr["local_bar"], "the rule's local bar lies below the verdict's redraw rate")
    pi = mr["predicted_if_independent_at_redraw_rate"]
    add("PcPredLocal", f2(pi["any local (6 masks)"]["rate"]), pc, "part1.mechanism_rule.predicted_if_independent_at_redraw_rate['any local (6 masks)'].rate")
    add("PcPredGlobalInd", f2(pi["any global, indirect only (per record, its indirect global masks)"]["rate"]), pc,
        "part1.mechanism_rule.predicted_if_independent_at_redraw_rate['any global, indirect only ...'].rate")
    # task families whose excess at 1,000 against the exact-simulator reference includes zero
    for path, m, w in ((f"{MAIN}/reference.json", "random", "Rand"), (f"{SEEDED}/reference.json", "cem_seeded", "Ad")):
        gs = {(sub, g["method"], int(g["budget"])): g for sub, d in J(path)["subsets"].items() for g in d["groups"] if "difference" in g}
        inc = [f for f in FAMS if gs[(f"task:{f}", m, 1000)]["difference"]["bca_lo"] <= 0 <= gs[(f"task:{f}", m, 1000)]["difference"]["bca_hi"]]
        add(f"Defl{w}N", ints(len(inc)), path, f"task families whose {m} excess at 1,000 has a BCa interval including 0")
        add(f"Defl{w}Fams", words_list([f"\\emph{{{f}}}" for f in inc]), path, "those families")
        exc = [f for f in FAMS if f not in inc]
        add(f"Defl{w}Excl", words_list([f"\\emph{{{f}}}" for f in exc]), path, "the families whose interval excludes 0")
    import csv as _csv
    _rows = list(_csv.DictReader(open(src(PC))))
    _fins = [float(r["fid_decision_c40"]) for r in _rows
             if r["checkpoint"].endswith(("006000000", "001500032")) and r.get("fid_decision_c40") not in ("", None, "nan")]
    add("AcDecFidRange", f"{f3(min(_fins))} to {f3(max(_fins))}", PC, "fid_decision_c40 min to max across 12 final checkpoints")
    add("WellPosedSE", "six", "data/tasks_v2_H24.json", "well-posedness margin criterion: 6 standard errors")
    add("BestConstK", "20", "data/tasks_v2_H24.json", "top-20 constant baselines screened on 32 oracle seeds")
    quote("MacrosPerMonth", "M = 4                       # macros per month", "code/dc/grammar.py", "four")
    quote("PatchSeeds", "K_PATCH = 8 ", "code/dc/patching.py", "8")
    b = T("code/dc/behaviour.py")
    m = re.search(r"Styles \(``BUILDER_STYLES``\): ([a-z, ]+)\.", b)
    if not m:
        raise Missing("BUILDER_STYLES not listed in dc/behaviour.py")
    nst = len([x for x in m.group(1).split(",") if x.strip()])
    add("BuilderStyles", {7: "seven"}.get(nst, ints(nst)), "code/dc/behaviour.py", "count of BUILDER_STYLES in the module docstring")
    # switches on files other builders are writing; each turns true when its file exists and its reader is written
    add_if_opt("RlAxisDone", True, "results/analysis/rl_axis.json", "the RL point in the paper's unit (rl_arm, rl_axis_macros)")
    # the analysis plan, read by its rule : the symmetric fire rule on recover's accepted-but-rejected
    # plans against both controls (corrected), and against the plans the emulator and the oracle both accept
    pcp = "results/analysis/patching_controls.json"
    p2 = J(pcp)["part2"]
    done2 = p2 is not None and "abr_symmetric" in p2 and "true_accept_vs_accepted_but_rejected" in p2
    if done2:
        fr2, pd2 = p2["abr_symmetric"]["flip_rates"], p2["abr_symmetric"]["paired"]
        for k, w in (("fire_sym", "SymFire"), ("none", "SymNone")):
            add(f"Pc{w}", f2(fr2[k]["rate"]), pcp, f"part2.abr_symmetric.flip_rates.{k}.rate")
            add(f"Pc{w}K", ints(fr2[k]["k"]), pcp, f"part2.abr_symmetric.flip_rates.{k}.k")
            add(f"Pc{w}N", ints(fr2[k]["n"]), pcp, f"part2.abr_symmetric.flip_rates.{k}.n")
        lo_ok = True
        for ctl, cw in (("random", "Size"), ("changed", "Chg")):
            e = pd2[f"fire_sym - {ctl}~fire_sym"]
            add(f"PcSymFire{cw}", s3(e["diff"]), pcp, f"part2.abr_symmetric.paired['fire_sym - {ctl}~fire_sym'].diff")
            add(f"PcSymFire{cw}CI", f"[{s3(e['lo_corr'])}, {s3(e['hi_corr'])}]", pcp, "... lo_corr/hi_corr (18 comparisons)")
            lo_ok = lo_ok and e["lo_corr"] > 0
        tv = p2["true_accept_vs_accepted_but_rejected"]["symmetric (rerun accepted-but-rejected records)"]
        ta, dd2 = tv["true_accept"], tv["true_accept_minus_accepted_but_rejected"]
        add("PcTaFire", f2(ta["rate"]), pcp, "part2.true_accept_vs_accepted_but_rejected[symmetric].true_accept.rate")
        add("PcTaFireK", ints(ta["k"]), pcp, "... true_accept.k")
        add("PcTaN", ints(ta["n"]), pcp, "... true_accept.n")
        add("PcTaCities", ints(ta["clusters"]), pcp, "... true_accept.clusters")
        add("PcTaPlans", ints(p2["true_accept_selection"]["analysed"]["distinct_plans"]), pcp, "part2.true_accept_selection.analysed.distinct_plans")
        if p2["true_accept_selection"]["analysed"]["records"] != p2["true_accept_selection"]["existing"]["records"]:
            raise Missing(f"{pcp}: not every true acceptance analysed")
        add("PcTaDiff", s3(dd2["diff"]), pcp, "... true_accept_minus_accepted_but_rejected.diff")
        add("PcTaDiffCI", f"[{s3(dd2['lo'])}, {s3(dd2['hi'])}]", pcp, "... lo/hi (BCa)")
        one = p2["true_accept_vs_accepted_but_rejected"]["one-sided (stored accepted-but-rejected records)"]["true_accept"]
        add("PcTaOneSided", f2(one["rate"]), pcp, "part2.true_accept_vs_accepted_but_rejected[one-sided].true_accept.rate")
        # R4 m6: the symmetric run's records are records over budgets and searches; their distinct plans and cities
        rr = p2["counts"]["accepted_but_rejected_recover_rerun"]
        if rr["records"] != fr2["fire_sym"]["n"]:
            raise Missing(f"{pcp}: the rerun's record count differs from the symmetric fire patch's n")
        add("PcSymPlans", ints(rr["distinct_plans"]), pcp, "part2.counts.accepted_but_rejected_recover_rerun.distinct_plans")
        add("PcSymCities", ints(rr["clusters"]), pcp, "part2.counts.accepted_but_rejected_recover_rerun.clusters")
        if "abr_indirect" in p2 and "true_accept_indirect" in p2:
            ifri = p2["abr_indirect"]["flip_rates"]
            ipdi = p2["abr_indirect"]["paired"]
            add("PcFireOv", f2(ifri["fire_overlay"]["rate"]), pcp, "part2.abr_indirect.flip_rates.fire_overlay.rate")
            add("PcFireOvCI", f"[{f2(ifri['fire_overlay']['lo'])}, {f2(ifri['fire_overlay']['hi'])}]", pcp, "part2.abr_indirect.flip_rates.fire_overlay.lo/hi")
            add("PcFireOvK", ints(ifri["fire_overlay"]["k"]), pcp, "part2.abr_indirect.flip_rates.fire_overlay.k")
            add("PcFireOvN", ints(ifri["fire_overlay"]["n"]), pcp, "part2.abr_indirect.flip_rates.fire_overlay.n")
            add("PcFireOvNone", f2(ifri["none"]["rate"]), pcp, "part2.abr_indirect.flip_rates.none.rate")
            for ctl, cw in (("random", "Size"), ("changed", "Chg")):
                ie = ipdi[f"fire_overlay - {ctl}~fire_overlay"]
                add(f"PcFireOv{cw}", s3(ie["diff"]), pcp, f"part2.abr_indirect.paired['fire_overlay - {ctl}~fire_overlay'].diff")
                add(f"PcFireOv{cw}CI", f"[{s3(ie['lo_corr'])}, {s3(ie['hi_corr'])}]", pcp, "... lo_corr/hi_corr (18 comparisons)")
            itaf = p2["true_accept_indirect"]["flip_rates"]["fire_overlay"]
            add("PcFireOvTa", f2(itaf["rate"]), pcp, "part2.true_accept_indirect.flip_rates.fire_overlay.rate")
            add("PcFireOvTaK", ints(itaf["k"]), pcp, "part2.true_accept_indirect.flip_rates.fire_overlay.k")
        holds = lo_ok and dd2["hi"] < 0
        add_if("FireDone", True, pcp, "part2 present: the symmetric rule and the true-acceptance control")
        add_if("FireHolds", holds, pcp, "symmetric fire above both controls (corrected) and below on true acceptances (interval excludes 0)")
    else:
        add_if("FireDone", False, pcp, "part2 not yet in the file")
        add_if("FireHolds", False, pcp, "part2 not yet in the file")
        for n in ("PcSymFire", "PcSymFireK", "PcSymFireN", "PcSymNone", "PcSymNoneK", "PcSymNoneN", "PcSymFireSize",
                  "PcSymFireSizeCI", "PcSymFireChg", "PcSymFireChgCI", "PcTaFire", "PcTaFireK", "PcTaN", "PcTaCities",
                  "PcTaPlans", "PcTaDiff", "PcTaDiffCI", "PcTaOneSided", "PcSymPlans", "PcSymCities"):
            pending(n, pcp, "part 2 not yet in the file")
    add_if_opt("PcThreeDone", True, pcp, "part 3: the symmetric rule on every record for fire and zone growth")
    add_if_opt("DefIncDone", False, "results/analysis/defences_increment.json", "defences against their own undefended model (reader pending)")
    horizon_ladder()
    add_if_opt("HorizonDone", True, "results/analysis/fidelity_horizon.json", "24-month fidelity and held-out likelihood over the ladder")
    logged_verdicts()
    add_if_opt("LogVerdDone", True, "results/analysis/logged_plan_verdicts.json", "the emulator's verdict on logged plans over the ladder")
    threshold_reread()
    add_if_opt("ThrDone", True, "results/analysis/threshold_reread.json", "re-read at two other thresholds (recover only)")
    cvp = "results/analysis/coverage.json"
    dfc = J(cvp)["decision_fidelity"]
    if dfc["status"] != "ok" or not dfc["main_equals_the_ladder_value"]:
        raise Missing(f"{cvp}: decision_fidelity")
    pa_ = dfc["paired"]["all"]
    add("CovDecFid", f3(pa_["coverage"]["value"]), cvp, "decision_fidelity.paired.all.coverage.value")
    add("CovDecFidMain", f3(pa_["main"]["value"]), cvp, "decision_fidelity.paired.all.main.value")
    cm = pa_["coverage_minus_main"]
    add("CovDecFidDiff", s3(cm["value"]), cvp, "decision_fidelity.paired.all.coverage_minus_main.value")
    add("CovDecFidDiffCI", ci(cm, signed=True), cvp, "decision_fidelity.paired.all.coverage_minus_main (BCa)")
    for path, w in (("results/audit/ladder/os_50m_cov/samples_006000000/tasks_v2_H24_cem_seeded/reference.json", "Cov"),
                    (f"{SEEDED}/reference.json", "Main")):
        g = [x for x in J(path)["subsets"]["in_band"]["groups"] if x["method"] == "cem_seeded" and int(x["budget"]) == 1000][0]
        add(f"CovAdWP{w}Excess", s3(est(g["difference"])), path, "subsets.in_band.groups[cem_seeded,1000].difference.value")
        add(f"CovAdWP{w}ExcessCI", ci(g["difference"], signed=True), path, "subsets.in_band.groups[cem_seeded,1000].difference.bca")
    coverage_seeds()
    add_if_opt("CovSeedsDone", True, CS, "the coverage model against three seeds of the main configuration ")
    add_if_opt("DepthDone", True, "results/analysis/false_acceptance_depth.json", "depth of the false acceptances")
    fd = "results/analysis/false_acceptance_depth.json"
    dd_ = J(fd)
    if dd_["budget"] != 1000:
        raise Missing(f"{fd}: budget")
    for m, w in (("random", "Rand"), ("cem_seeded", "Ad")):
        for who, ww in (("emulator", ""), ("perfect_emulator", "Perf")):
            e = dd_["methods"][m][who]
            if e["status"] != "ok" or e["n_instances"] != 193:
                raise Missing(f"{fd}: {m} {who}")
            loc = f"methods.{m}.{who}."
            add(f"Depth{w}{ww}N", ints(e["n_false_acceptances"]), fd, loc + "n_false_acceptances")
            add(f"Depth{w}{ww}Median", f3(e["median_oracle_share"]), fd, loc + "median_oracle_share")
            add(f"Depth{w}{ww}Low", ints(e["n_share_below_0_1"]), fd, loc + "n_share_below_0_1")
    quote("DepthCut", "pass share below 0.1", "results/analysis/false_acceptance_depth.md", "0.1")
    ac = "results/analysis/audit_cost.json"
    a = J(ac)
    c120 = a["c120_per_checkpoint"]
    v1 = {x["engine_city_months_judge_B1000"] for x in c120.values()}
    v2 = {x["engine_city_months_judge_all_budgets"] for x in c120.values()}
    if len(v1) != 1 or len(v2) != 1:
        raise Missing(f"{ac}: per-checkpoint costs differ")
    add("CostAuditThou", ints(v1.pop()), ac, "c120_per_checkpoint.*.engine_city_months_judge_B1000 (equal for every checkpoint)")
    add("CostAuditAll", ints(v2.pop()), ac, "c120_per_checkpoint.*.engine_city_months_judge_all_budgets (equal)")
    pc = a["rl"]["per_checkpoint_mean"]["design_engine_city_months"]
    add("CostRlEval", ints(int(pc)), ac, "rl.per_checkpoint_mean.design_engine_city_months (15 runs)")
    add("RlRunsPerCkpt", ints(a["rl"]["ladder_360_runs"]["n_runs"] // a["rl"]["ladder_360_runs"]["n_checkpoints"]), ac,
        "rl.ladder_360_runs.n_runs / n_checkpoints")
    et = a["rl"]["engine_trained_learner"]
    add("CostRlTrainRun", ints(et["training_months_total"] // et["n_runs"]), ac, "rl.engine_trained_learner.training_months_total / n_runs")
    add_if_opt("PaSameDone", True, "results/analysis/pressure_axis.json", "both searches on the same instances: bca.random")
    add_if_opt("CiteDone", False, "paper/review/citations_check.md", "the closest prior work, verified (reader pending)")
    cs_ = "results/analysis/compute_summary.json"
    add_if_opt("LedgerDone", True, cs_, "rented runs counted from compute_summary.json")
    add("LedgerRented", ints(J(cs_)["rented"]["rl_runs_rented"]), cs_, "rented.rl_runs_rented")
    add("LedgerRuns", ints(a["rl"]["ladder_360_runs"]["n_runs"]), ac, "rl.ladder_360_runs.n_runs")
    ts = "results/analysis/treasury_identity_split.json"
    tr = [x for x in J(ts)["rows"] if x["method"] == "random" and x["budget"] == 1000][0]
    for k, w in (("wrongly accepted", "Wrong"), ("rightly accepted", "Right"), ("rejected", "Rej")):
        add("TrSplit" + w, f3(tr[k]["rate"]), ts, f"rows[random,1000]['{k}'].rate")
    wm = tr["wrong_minus_right"]
    add("TrSplitDiff", s3(wm["value"]), ts, "rows[random,1000].wrong_minus_right.value")
    add("TrSplitDiffCI", f"[{s3(wm['bca'][0])}, {s3(wm['bca'][1])}]", ts, "rows[random,1000].wrong_minus_right.bca")
    # R3 F3: the main checkpoint's well-posed instances, by task family (Table 7), recomputed from the records exactly
    # as run_audit.compare_reference computes every family row, which the guard below checks against reference.json
    return wp_by_family()


FH = "results/analysis/fidelity_horizon.json"
HL = "results/analysis/heldout_likelihood.json"
LV = "results/analysis/logged_plan_verdicts.json"


def horizon_ladder():
    """R2 F1 and M4: every run's fidelity at the task horizon and its held-out likelihood at half and at the end
    (fidelity_horizon.json, heldout_likelihood.json); a table for appendix B and the ladder-wide sentence of 2.3."""
    rows = {r["run"]: r for r in J(FH)["rows"] if r["stage"] == "final" and r["split"] == "test"}
    hl = J(HL)["runs"]
    lad = [r for r in TEST_RUNS if LADDER_RUN.fullmatch(r)]
    if set(TEST_RUNS) - set(rows) or any(rows[r]["status"] != "ok" for r in TEST_RUNS):
        raise Missing(f"{FH}: not every final checkpoint's test row is ok")
    ge1 = [rows[r]["n_overlays_model_ratio_ge_1"] for r in lad]
    add_multi("HorLadGeMin", ints(min(ge1)), [FH], "ladder finals: min of n_overlays_model_ratio_ge_1")
    add_multi("HorLadGeMax", ints(max(ge1)), [FH], "ladder finals: max of n_overlays_model_ratio_ge_1")
    pfw = [rows[r]["n_overlays_model_ratio_ge_1"] for r in lad if r.startswith("sf_")]
    add_multi("HorPfGeMin", ints(min(pfw)), [FH], "pushforward finals: min of n_overlays_model_ratio_ge_1")
    pol = [rows[r]["overlays_24m_all_plans"]["pollution"]["model_ratio"] for r in TEST_RUNS]
    add_multi("HorPollMin", f3(min(pol)), [FH], "all 16 finals: min pollution model_ratio")
    add_multi("HorPollMax", f3(max(pol)), [FH], "all 16 finals: max pollution model_ratio")
    pz = [rows[r]["open_loop_scalars_24m"]["scalars"]["powered_zones"]["model_mae"] for r in TEST_RUNS]
    cz = {rows[r]["open_loop_scalars_24m"]["scalars"]["powered_zones"]["copy_mae"] for r in TEST_RUNS}
    add_multi("HorPowMin", f"{min(pz):.1f}", [FH], "all 16 finals: min open-loop powered_zones model_mae")
    add_multi("HorPowMax", f"{max(pz):.1f}", [FH], "all 16 finals: max open-loop powered_zones model_mae")
    expect(min(pz) > max(cz), "every final's powered-zone error exceeds copying's on open-loop plans")
    small = [r for r in lad if "_small" in r]
    full_ = [r for r in TEST_RUNS if "_full" in r]
    expect(all(hl[r]["half_vs_final_dev"]["final_below_half"] for r in small), "every small-data final is below its half")
    expect(not any(hl[r]["half_vs_final_dev"]["final_below_half"] for r in full_), "every full-data run improves")
    pc = [-hl[r]["half_vs_final_dev"]["per_cent_of_half"] for r in small]
    add_multi("HlSmallN", ints(len(small)), [HL], "small-data finals")
    add_multi("HlSmallPctMin", f"{min(pc):.0f}", [HL], "small-data finals: min of -per_cent_of_half (worse by, per cent)")
    add_multi("HlSmallPctMax", f"{max(pc):.0f}", [HL], "small-data finals: max of the same")
    body = []
    lab = {"os": "one-step", "sf": "pushforward"}
    for r in TEST_RUNS + ["os_50m_cov"]:
        x = rows[r]
        o = x["overlays_24m_all_plans"]
        pzr = x["open_loop_scalars_24m"]["scalars"]["powered_zones"]
        h = hl[r]["half_vs_final_dev"]
        parts = r.split("_")
        seed = parts[3][1:] if len(parts) > 3 and parts[3].startswith("s") else ("0" if r != "os_50m_cov" else "0")
        data = {"full": "full", "small": "small", "cov": "full + cov."}[parts[2]]
        body.append(" & ".join([lab[parts[0]], parts[1].upper(), data, seed, ints(x["n_overlays_model_ratio_ge_1"]),
                                f3(o["pollution"]["model_ratio"]), f3(o["fire_coverage"]["model_ratio"]),
                                f"{pzr['model_mae']:.1f}", mbox_neg(f"{h['half']:.0f}"), mbox_neg(f"{h['final']:.0f}"),
                                "yes" if h["final_below_half"] else "no"]) + r" \\")
    e = rows["os_50m_full"]
    body.append(r"\midrule")
    body.append(r"\multicolumn{4}{@{}l}{Engine under another seed} & & " + f3(e["overlays_24m_all_plans"]["pollution"]["engine_ratio"])
                + " & " + f3(e["overlays_24m_all_plans"]["fire_coverage"]["engine_ratio"]) + " & "
                + f"{e['open_loop_scalars_24m']['scalars']['powered_zones']['engine_mae']:.1f}" + r" & & & \\")
    body.append(r"\multicolumn{4}{@{}l}{Copy-last-state} & & 1.000 & 1.000 & "
                + f"{e['open_loop_scalars_24m']['scalars']['powered_zones']['copy_mae']:.1f}" + r" & & & \\")
    (PAPER / "tables" / "ladder_horizon.tex").write_text(
        "% Generated by paper/scripts/make_numbers.py from results/analysis/fidelity_horizon.json and heldout_likelihood.json\n"
        r"\setlength{\tabcolsep}{2pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llllrrrrrrc@{}}" "\n" r"\toprule" "\n"
        r"Objective & Size & Data & Seed & Overlays $\geq$ copy & Pollution & Fire cov. & Powered zones & ELBO, half & ELBO, final & Final below half \\" "\n"
        r"\midrule" "\n" + "\n".join(body) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n")
    src(FH); src(HL)


TR = "results/analysis/threshold_reread.json"


def threshold_reread():
    d = J(TR)
    if not d["theta_is_theta32_l50_on_every_instance"]:
        raise Missing(f"{TR}: the audit's theta is not the halfway one")
    fam = d["families"]
    okf = [f for f in FAMS if fam[f].get("status") == "ok"]
    expect(okf == ["recover"], "only recover can be re-read exactly at other thresholds")
    r = fam["recover"]
    if not (r["selection"]["emulator"]["unchanged"] and r["selection"]["perfect_emulator"]["unchanged"]):
        raise Missing(f"{TR}: recover's selection is not unchanged")
    body = []
    word = {"l25": "$0.25$", "l50": "$0.50$ (benchmark)", "l75": "$0.75$"}
    for k in ("l25", "l50", "l75"):
        L = r["levels"][k]
        body.append(" & ".join([word[k], ints(L["n"]), tex_ci(L["false_acceptance"]), f3(est(L["perfect_false_acceptance"])),
                                tex_ci(L["excess"], True), f3(est(L["real_success"])) + " / " + f3(est(L["perfect_real_success"])),
                                f3(est(L["emulator_accepts"]))]) + r" \\")
        add(f"Thr{ {'l25': 'Lo', 'l50': 'Mid', 'l75': 'Hi'}[k] }Excess".replace(" ", ""), s3(est(L["excess"])), TR, f"families.recover.levels.{k}.excess.value")
        add(f"Thr{ {'l25': 'Lo', 'l50': 'Mid', 'l75': 'Hi'}[k] }OrAcc".replace(" ", ""), f3(est(L["real_success"])), TR, f"families.recover.levels.{k}.real_success.value")
    (PAPER / "tables" / "threshold_recover.tex").write_text(
        "% Generated by paper/scripts/make_numbers.py from results/analysis/threshold_reread.json\n"
        r"\setlength{\tabcolsep}{3pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrlrlcc@{}}" "\n" r"\toprule" "\n"
        r"Threshold $\lambda$ (from $c$ to $e$) & $n$ & False acceptance & Exact ref. & Excess & Truly passing, model/ref. & World model accepts \\" "\n"
        r"\midrule" "\n" + "\n".join(body) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n")


def logged_verdicts():
    d = J(LV)
    ok = [c for c in d["checkpoints"] if c["status"] == "ok" and c.get("role") == "ladder"]
    add("LogVerdN", ints(len(ok)), LV, "checkpoints[role=ladder, status=ok] (count)")
    for fam, fw in F_WORD.items():
        fn = [c["families"][fam]["false_rejection"] for c in ok]
        fp = [c["families"][fam]["false_acceptance"] for c in ok]
        add(f"Log{fw}FnMin", f3(min(fn)), LV, f"checkpoints[ok].families.{fam}.false_rejection (minimum)")
        add(f"Log{fw}FnMax", f3(max(fn)), LV, f"... (maximum)")
        add(f"Log{fw}FpMin", f3(min(fp)), LV, f"checkpoints[ok].families.{fam}.false_acceptance (minimum)")
        add(f"Log{fw}FpMax", f3(max(fp)), LV, f"... (maximum)")
    main = [c for c in ok if c["checkpoint"] == "os_50m_full-samples_006000000"][0]
    expect(abs(main["families"]["grow"]["false_rejection"] - float(J(f"{MAIN}/card.json")["flip_rates_by_task_family"]["grow"]["fn"])) < 1e-9,
           "the logged-plan file reproduces the main checkpoint's card")


def _records(path):
    return [json.loads(l) for l in gzip.open(src(path), "rt")]


def wp_by_family():
    out = {}
    for path, method in ((f"{MAIN}/reference.json", "random"), (f"{SEEDED}/reference.json", "cem_seeded")):
        ref = J(path)
        run = Path(ref["run"]).relative_to(REPO) if Path(ref["run"]).is_absolute() else Path(ref["run"])
        rdir = Path(ref["reference"]).relative_to(REPO) if Path(ref["reference"]).is_absolute() else Path(ref["reference"])
        R = {(r["instance"], r["method"], int(r["budget"]), int(r["attacker_seed"])): r for r in _records(run / "records.jsonl.gz")}
        F = {(r["instance"], r["method"], int(r["budget"]), int(r["attacker_seed"])): r for r in _records(rdir / "records.jsonl.gz")}
        groups = {(s, g["method"], int(g["budget"])): g for s, d in ref["subsets"].items() for g in d["groups"] if "difference" in g}
        for fam in FAMS:
            for wp in (False, True):
                keys = sorted(k for k, r in R.items() if k[1] == method and k[2] == 1000 and r["task"] == fam
                              and (bool(r["in_band"]) or not wp) and k in F)
                cl = [R[k]["cluster"] for k in keys]
                ge = np.array([R[k]["grader_p"] >= 0.5 for k in keys])
                oe = np.array([bool(R[k]["oracle_accept"]) for k in keys])
                gr = np.array([F[k]["grader_p"] >= 0.5 for k in keys])
                orr = np.array([bool(F[k]["oracle_accept"]) for k in keys])
                d = HS.excess(ge & ~oe, gr & ~orr, cl, bca=True).as_dict()
                cell = {"n": len(keys), "hack": float((ge & ~oe).mean()), "perf": float((gr & ~orr).mean()), "diff": d,
                        "orc": float(oe.mean()), "porc": float(orr.mean())}
                if not wp:
                    g = groups[(f"task:{fam}", method, 1000)]
                    expect(len(keys) == g["n_paired"] and abs(cell["hack"] - est(g["emulator"]["hackability"])) < 1e-12
                           and abs(d["value"] - est(g["difference"])) < 1e-12
                           and abs(d["bca_lo"] - g["difference"]["bca_lo"]) < 1e-9,
                           f"the recomputed {fam} row reproduces reference.json ({method})")
                out[(fam, method, wp)] = (cell, [str(run / "records.jsonl.gz"), str(rdir / "records.jsonl.gz")])
    return out


# ---------------------------------------------------------------------------------------------
# the monthly replanning run 
# ---------------------------------------------------------------------------------------------
# The coordinator controls whether results/analysis/replan.json exists: replan_axis.py writes it once, at the time box,
# and the file is committed only after review and before the freeze . While it is absent, or fails
# a condition below, the comparison is OFF: every Rp macro is empty, every Rp switch false, and the paper prints
# exactly what it printed before. REPLAN_DIR_ENV (or --replan-dir) points replanning() at another directory for
# replan.json (and, if that directory holds one, replan_control.json): for tests and dry builds only.
RP_JSON = "results/analysis/replan.json"
RP_CONTROL = "results/analysis/replan_control.json"
RP_ENGINE_CONFIG = "results/replan/engine/config.json"          # the perfect emulator's run: the design as run
RP_V1 = "results/replan/engine_v1/records.jsonl.gz"             # controller version 1, 25 instances 
RP_V2 = "results/analysis/replan_control_v2/replan_control.json"  # controller version 2, 100 instances 
RP_FRESH = "results/analysis/replan_fresh"                     # the analysis plan: the fresh-stream reference
# (replan.json and replan_control.json of the same scripts, --engine results/replan/engine_fresh)
RP_KEPT_FIELD = "incumbent_kept_months_mean"                   # per model, pooled and by family 
REPLAN_DIR_ENV = "WM2_REPLAN_DIR"
RP_READINGS = (("R-a", "Ra"), ("R-b", "Rb"), ("R-c", "Rc"), ("R-d", "Rd"))
# what each reading is, as the paragraph names it (the fragile sentence uses these names, never "R-a")
RP_READING_NAMES = {"R-a": "the excess", "R-b": "the change in the excess", "R-c": "the shortfall",
                    "R-d": "the change in the shortfall"}
RP_KEY_WORDS = {"above": "above zero", "includes_zero": "includes zero", "below": "below zero"}
RP_NUM_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def _rp_names() -> list:
    """Every Rp macro, in the same order in both states (the OFF state defines each one empty)."""
    n = ["RpN", "RpPlans", "RpFresh", "RpPaired", "RpSwitchSe", "RpBoot", "RpKeptMin", "RpKeptMax", "RpKeptOf",
         "RpCtlReplan", "RpCtlOpen", "RpCtlN", "RpCtlDiff", "RpCtlDiffCI"]
    for f in FAMS:
        n += [f"RpCtl{F_WORD[f]}{k}" for k in ("Replan", "Open", "N", "Diff", "DiffCI")]
    for _, w in RP_READINGS:
        n += [f"Rp{w}Est", f"Rp{w}CI", f"Rp{w}Width", f"Rp{w}Words", f"Rp{w}Key"]
    for m in ("Emu", "Perf"):
        n += [f"Rp{m}{a}{q}" for a in ("Replan", "Open") for q in ("OrAcc", "Hack")]
    for _, w in RP_READINGS:
        n += [f"Rp{w}FreshEst", f"Rp{w}FreshCI", f"Rp{w}FreshKey"]
    n += ["RpFragileList", "RpFCtlReplan", "RpFCtlOpen", "RpFCtlN", "RpFCtlDiff", "RpFCtlDiffCI"]
    for side in ("Emu", "Perf", "Fresh"):
        n += [f"RpKept{side}{F_WORD[f]}" for f in FAMS] + [f"RpKept{side}Min", f"RpKept{side}Max"]
    for m in ("Emu", "Perf"):
        n += [f"Rp{m}OpenOrc{q}" for q in ("OrAcc", "Hack")]
    # by task family, descriptive : counts on the realised seed and the two readings under replanning
    for f in FAMS:
        n += [f"RpFam{F_WORD[f]}{k}" for k in ("N", "EmuReplan", "EmuOpen", "PerfReplan", "PerfOpen", "FreshReplan",
                                               "FreshOpen", "Excess", "ExcessCI", "Short", "ShortCI", "FreshExcess",
                                               "FreshExcessCI", "FreshShort", "FreshShortCI")]
    n += ["RpLimitsOutcome"]
    n += ["RpFamAboveList", "RpFamFreshAboveList", "RpFamTop", "RpFamTopN", "RpFamTopEmuReplan", "RpFamTopEmuOpen",
          "RpFamTopPerfReplan", "RpFamTopPerfOpen"]
    n += ["RpVOneN", "RpVOneReplan", "RpVOneOpen", "RpVOnePowerN", "RpVOnePowerReplan", "RpVOnePowerOpen",
          "RpVTwoN", "RpVTwoReplan", "RpVTwoOpen", "RpVTwoGrowN", "RpVTwoGrowReplan", "RpVTwoGrowOpen",
          "RpVTwoRecovN", "RpVTwoRecovReplan", "RpVTwoRecovOpen"]
    return n


RP_SWITCHES = ("RpOn", "RpPrefix", "RpRaZero", "RpRcZero", "RpFreshOn", "RpRaFragile", "RpRbFragile", "RpRcFragile",
               "RpRdFragile", "RpAnyFragile", "RpFragilePlural", "RpFreshCtl", "RpKeptEmuOn", "RpFamAnyAbove",
               "RpFamAbovePlural", "RpFamOthersZero", "RpFamDiffer", "RpFamSomeNot", "RpBothAbove", "RpFindOn")


def _rp_is_prefix(res) -> bool:
    """replan.json's analysed order positions are exactly 0..n-1 (replan_axis.py writes the sorted list as
    order_index); a file without the list, or with a hole in it, is not a prefix of the fixed order."""
    oi = res.get("order_index")
    return isinstance(oi, list) and [int(i) for i in oi] == list(range(int(res["n_instances"])))


def replanning(override=None):
    """Macros and switches of the monthly replanning comparison (ON or OFF, see above); returns the state."""
    over = override or os.environ.get(REPLAN_DIR_ENV) or None
    rp_path = (Path(over) / "replan.json") if over else REPO / RP_JSON
    ctl_path = (Path(over) / "replan_control.json") if over and (Path(over) / "replan_control.json").exists() \
        else REPO / RP_CONTROL
    ctl = J(ctl_path)
    why = None
    if not rp_path.exists():
        why = "replan.json absent"
    else:
        rp = J(rp_path)
        if int(rp.get("controller_version", -1)) != 3 or int(ctl["controller_version"]) != 3:
            why = f"controller version {rp.get('controller_version')} (control {ctl['controller_version']}), not 3"
        elif not ctl.get("enters_paper_if_complete_and_reviewed"):
            why = "the control's gates stop the comparison "
        elif int(rp["n_instances"]) % 5 or int(rp["n_instances"]) < 40:
            why = f"{rp['n_instances']} instances: not a prefix of 5k instances with k at least 8 "
        elif not _rp_is_prefix(rp):
            why = (f"order_index is not 0..{int(rp['n_instances']) - 1}: the analysed instances are not the first "
                   f"{rp['n_instances']} of the fixed order ")
    on = why is None
    if not on:
        if why != "replan.json absent":
            print(f"make_numbers: the replanning comparison is OFF: {why}", file=sys.stderr)
        for name in _rp_names():
            add(name, "", ctl_path, f"OFF: {why}")
        for s in RP_SWITCHES:
            add_if(s, False, ctl_path, f"OFF: {why}")
        return {"on": False, "why": why}
    for d in (REPO / "code" / "scripts", REPO / "code"):
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
    import replan_axis as RA                                  # the readings' fixed wordings 
    from dc import replan as DR                               # the controller's constants as run
    vals = {}

    def put(name, value, source, locator):
        vals[name] = (str(value), source, locator)
    n = int(rp["n_instances"])
    if len(set(rp["per_family"].values())) != 1 or sum(rp["per_family"].values()) != n:
        raise Missing(f"{rp_path}: families unbalanced {rp['per_family']}: not a prefix of 5k instances ")
    cfg = J(RP_ENGINE_CONFIG)["design"]
    if int(cfg["controller_version"]) != 3 or int(cfg["controller_version"]) != DR.CONTROLLER_VERSION:
        raise Missing(f"{RP_ENGINE_CONFIG}: controller version {cfg['controller_version']}")
    plans = int(cfg["n_plans"])
    if rp["n_plans"] != {"emulator": [plans], "engine": [plans]}:
        raise Missing(f"{rp_path}: proposals per month {rp['n_plans']}, the engine run's config says {plans}")
    put("RpN", ints(n), rp_path, "n_instances")
    put("RpPlans", ints(plans), RP_ENGINE_CONFIG, "design.n_plans")
    # from month 1 the candidates are the plan in hand and draws 0..n_plans-2 (dc.replan.replan_instance's docstring)
    put("RpFresh", ints(plans - 1), RP_ENGINE_CONFIG, "design.n_plans - 1 (the plan in hand takes one place)")
    put("RpPaired", RP_NUM_WORDS[int(DR.PAIRED_SAMPLES)], "code/dc/replan.py", "PAIRED_SAMPLES (as a word)")
    put("RpSwitchSe", RP_NUM_WORDS[int(DR.SWITCH_STANDARD_ERRORS)], "code/dc/replan.py", "SWITCH_STANDARD_ERRORS (as a word)")
    put("RpBoot", ints(ctl["n_boot"]), ctl_path, "n_boot")
    kept = [v for v in ctl["incumbent_kept_months_mean"].values()]
    put("RpKeptMin", f"{min(kept):.1f}", ctl_path, "incumbent_kept_months_mean (minimum over families)")
    put("RpKeptMax", f"{max(kept):.1f}", ctl_path, "incumbent_kept_months_mean (maximum over families)")
    put("RpKeptOf", ints(int(cfg["H"]) - 1), RP_ENGINE_CONFIG, "design.H - 1 (months that replan after month 0)")

    def ctl_block(prefix, b, loc):
        put(prefix + "Replan", ints(b["replan_pass"]), ctl_path, loc + "replan_pass")
        put(prefix + "Open", ints(b["open_loop_pass"]), ctl_path, loc + "open_loop_pass")
        put(prefix + "N", ints(b["n_instances"]), ctl_path, loc + "n_instances")
        put(prefix + "Diff", s3(b["difference"]["value"]), ctl_path, loc + "difference.value")
        put(prefix + "DiffCI", f"[{s3(b['lo'])}, {s3(b['hi'])}]", ctl_path, loc + "lo, hi (the limits the gates read)")
    ctl_block("RpCtl", ctl["pooled"], "pooled.")
    for f in FAMS:
        ctl_block(f"RpCtl{F_WORD[f]}", ctl["by_family"][f], f"by_family.{f}.")
    zero = {}
    for r, w in RP_READINGS:
        d = rp["readings"][r]
        lo, hi, key = float(d["lo"]), float(d["hi"]), d["reading"]
        if key != ("above" if lo > 0 else ("below" if hi < 0 else "includes_zero")):
            raise Missing(f"{rp_path}: readings.{r}: {key} disagrees with its interval")
        if d["wording"] != RA.WORDING[r][key]:
            raise Missing(f"{rp_path}: readings.{r}: the wording is not replan_axis.WORDING's")
        put(f"Rp{w}Est", s3(d["estimate"]["value"]), rp_path, f"readings.{r}.estimate.value")
        put(f"Rp{w}CI", f"[{s3(lo)}, {s3(hi)}]", rp_path, f"readings.{r}.lo, hi ({d['interval_used']})")
        put(f"Rp{w}Width", f3(d["interval_width"]), rp_path, f"readings.{r}.interval_width")
        put(f"Rp{w}Words", d["wording"], rp_path, f"readings.{r}.wording (copied)")
        put(f"Rp{w}Key", RP_KEY_WORDS[key], rp_path, f"readings.{r}.reading")
        zero[w] = key == "includes_zero"
    P = rp["pooled"]
    for m, mw in (("emulator", "Emu"), ("engine", "Perf")):
        for a, aw in (("replan", "Replan"), ("open_loop", "Open")):
            for q, qw in (("real_success", "OrAcc"), ("false_acceptance", "Hack")):
                put(f"Rp{mw}{aw}{qw}", f3(P[m][a][q]["value"]), rp_path, f"pooled.{m}.{a}.{q}.value")
    # the 32-seed majority's open-loop column beside the realised seed 
    for m, mw in (("emulator", "Emu"), ("engine", "Perf")):
        for q, qw in (("real_success", "OrAcc"), ("false_acceptance", "Hack")):
            put(f"Rp{mw}OpenOrc{qw}", f3(P[m]["open_loop_oracle"][q]["value"]), rp_path, f"pooled.{m}.open_loop_oracle.{q}.value")
    # months the plan in hand was kept: the perfect-emulator side from its control, the emulator side from replan.json
    # when replan_axis.py records it 
    def kept_block(side, by_fam, source, loc):
        vals_ = [float(by_fam[f]) for f in FAMS]
        for f in FAMS:
            put(f"RpKept{side}{F_WORD[f]}", f"{float(by_fam[f]):.1f}", source, loc + f"{f}")
        put(f"RpKept{side}Min", f"{min(vals_):.1f}", source, loc + "(minimum over families)")
        put(f"RpKept{side}Max", f"{max(vals_):.1f}", source, loc + "(maximum over families)")

    def no_kept(side, source, why):
        for f in FAMS:
            put(f"RpKept{side}{F_WORD[f]}", "---", source, why)
        put(f"RpKept{side}Min", "---", source, why)
        put(f"RpKept{side}Max", "---", source, why)
    emu_kept = {f: (rp["by_family"].get(f, {}).get("emulator", {}) or {}).get(RP_KEPT_FIELD) for f in FAMS}
    kept_emu_on = all(v is not None for v in emu_kept.values())
    if kept_emu_on:
        kept_block("Emu", emu_kept, rp_path, f"by_family.<family>.emulator.{RP_KEPT_FIELD} ")
    else:
        no_kept("Emu", rp_path, f"not in replan.json (by_family.<family>.emulator.{RP_KEPT_FIELD})")
    perf_kept = {f: (rp["by_family"].get(f, {}).get("engine", {}) or {}).get(RP_KEPT_FIELD) for f in FAMS}
    if all(v is not None for v in perf_kept.values()):        # the same instances as the emulator side (R7 m10)
        kept_block("Perf", perf_kept, rp_path, f"by_family.<family>.engine.{RP_KEPT_FIELD} ")
    else:
        kept_block("Perf", ctl["incumbent_kept_months_mean"], ctl_path, "incumbent_kept_months_mean.")
    # the fresh-stream reference : readings against both references; fragile where the category differs
    fdir = (Path(over) / "replan_fresh") if over else REPO / RP_FRESH
    fresh_on, fresh_ctl_on = False, False
    if (fdir / "replan.json").exists():
        fr = J(fdir / "replan.json")
        ss = fr.get("seed_stream") or {}
        if (int(fr.get("controller_version", -1)) != 3 or fr["n_plans"] != rp["n_plans"] or not ss.get("engine")
                or ss.get("engine") == (rp.get("seed_stream") or {}).get("engine")):
            raise Missing(f"{fdir}/replan.json: not the fresh-stream reference of this run (version, proposals or the "
                          f"engine side's seed stream)")
        # on the same instances as the primary reading, or it is treated as not complete at the freeze
        if int(fr["n_instances"]) == n and _rp_is_prefix(fr):
            fresh_on = True
        else:
            print(f"make_numbers: the fresh-stream reference is not on the primary reading's instances "
                  f"(n {fr['n_instances']} against {n}, or order_index not 0..{n - 1}): printed as not complete",
                  file=sys.stderr)
    frag = {}
    for r, w in RP_READINGS:
        if fresh_on:
            d = fr["readings"][r]
            lo, hi, key = float(d["lo"]), float(d["hi"]), d["reading"]
            if key != ("above" if lo > 0 else ("below" if hi < 0 else "includes_zero")) or d["wording"] != RA.WORDING[r][key]:
                raise Missing(f"{fdir}/replan.json: readings.{r} inconsistent")
            put(f"Rp{w}FreshEst", s3(d["estimate"]["value"]), fdir / "replan.json", f"readings.{r}.estimate.value")
            put(f"Rp{w}FreshCI", f"[{s3(lo)}, {s3(hi)}]", fdir / "replan.json", f"readings.{r}.lo, hi")
            put(f"Rp{w}FreshKey", RP_KEY_WORDS[key], fdir / "replan.json", f"readings.{r}.reading")
            frag[w] = key != rp["readings"][r]["reading"]
        else:
            for k in ("FreshEst", "FreshCI", "FreshKey"):
                put(f"Rp{w}{k}", "---", ctl_path, "the fresh-stream reference is absent")
            frag[w] = False
    names = [RP_READING_NAMES[r] for r, w in RP_READINGS if frag[w]]
    put("RpFragileList", (", ".join(names[:-1]) + " and " + names[-1]) if len(names) > 1 else (names[0] if names else ""),
        (fdir / "replan.json") if fresh_on else ctl_path, "readings whose category differs between the two references")
    if fresh_on and (fdir / "replan_control.json").exists():
        fc = J(fdir / "replan_control.json")
        if int(fc["controller_version"]) != 3:
            raise Missing(f"{fdir}/replan_control.json: controller version {fc['controller_version']}")
        b = fc["pooled"]
        for k, v, loc in (("Replan", ints(b["replan_pass"]), "pooled.replan_pass"),
                          ("Open", ints(b["open_loop_pass"]), "pooled.open_loop_pass"),
                          ("N", ints(b["n_instances"]), "pooled.n_instances"),
                          ("Diff", s3(b["difference"]["value"]), "pooled.difference.value"),
                          ("DiffCI", f"[{s3(b['lo'])}, {s3(b['hi'])}]", "pooled.lo, hi")):
            put(f"RpFCtl{k}", v, fdir / "replan_control.json", loc)
        kept_block("Fresh", fc["incumbent_kept_months_mean"], fdir / "replan_control.json", "incumbent_kept_months_mean.")
        fresh_ctl_on = True
    else:
        for k in ("Replan", "Open", "N", "Diff", "DiffCI"):
            put(f"RpFCtl{k}", "---", ctl_path, "the fresh-stream control is absent")
        no_kept("Fresh", ctl_path, "the fresh-stream control is absent")
    # controller version 1 (25 instances, stopped there; records only, replan_control.py refuses a partial run)
    v1 = _records(RP_V1)
    if any(r.get("controller_version", 1) != 1 for r in v1):
        raise Missing(f"{RP_V1}: not controller version 1")
    pw = [r for r in v1 if r["task"] == "power"]
    for name, val, loc in (("RpVOneN", len(v1), "records (count)"),
                           ("RpVOneReplan", sum(bool(r["replan_pass"]) for r in v1), "sum of replan_pass"),
                           ("RpVOneOpen", sum(bool(r["open_loop_pass"]) for r in v1), "sum of open_loop_pass"),
                           ("RpVOnePowerN", len(pw), "records of power (count)"),
                           ("RpVOnePowerReplan", sum(bool(r["replan_pass"]) for r in pw), "power: sum of replan_pass"),
                           ("RpVOnePowerOpen", sum(bool(r["open_loop_pass"]) for r in pw), "power: sum of open_loop_pass")):
        put(name, ints(val), RP_V1, loc)
    v2 = J(RP_V2)
    if int(v2["controller_version"]) != 2:
        raise Missing(f"{RP_V2}: not controller version 2")
    for prefix, b, loc in (("RpVTwo", v2["pooled"], "pooled."), ("RpVTwoGrow", v2["by_family"]["grow"], "by_family.grow."),
                           ("RpVTwoRecov", v2["by_family"]["recover"], "by_family.recover.")):
        put(prefix + "N", ints(b["n_instances"]), RP_V2, loc + "n_instances")
        put(prefix + "Replan", ints(b["replan_pass"]), RP_V2, loc + "replan_pass")
        put(prefix + "Open", ints(b["open_loop_pass"]), RP_V2, loc + "open_loop_pass")
    # by task family, descriptive : which families carry the pooled excess and shortfall under
    # replanning (both intervals above zero), and the family with the largest shortfall, with its counts
    def lim(e):
        lo, hi = e.get("bca_lo"), e.get("bca_hi")
        if lo is None or hi is None or (isinstance(lo, float) and np.isnan(lo)):
            lo, hi = e["pct_lo"], e["pct_hi"]
        return float(lo), float(hi)

    def cnt(b, m, arm):
        v = float(b[m][arm]["real_success"]["value"]) * int(b["n_instances"])
        if abs(v - round(v)) > 1e-6:
            raise Missing(f"{rp_path}: by_family {m}.{arm}.real_success x n is not a count ({v})")
        return int(round(v))

    def fam_state(res):
        st = {}
        for f in FAMS:
            b = res["by_family"][f]
            ex, sh = lim(b["excess_false_acceptance"]["replan"]), lim(b["shortfall_real_success"]["replan"])
            st[f] = ("above" if ex[0] > 0 and sh[0] > 0 else
                     "zero" if ex[0] <= 0 <= ex[1] and sh[0] <= 0 <= sh[1] else "mixed")
        return st

    def fam_list(fs):
        w = [f"\\emph{{{f}}}" for f in fs]
        return w[0] if len(w) == 1 else ", ".join(w[:-1]) + " and " + w[-1] if w else "none"
    st = fam_state(rp)
    above = [f for f in FAMS if st[f] == "above"]
    above.sort(key=lambda f: -float(rp["by_family"][f]["shortfall_real_success"]["replan"]["value"]))
    put("RpFamAboveList", fam_list(above), rp_path, "families whose excess and shortfall under replanning both lie above zero (by_family.<f>.*.replan, BCa)")
    fst = fam_state(fr) if fresh_on else None
    fabove = sorted([f for f in FAMS if fst[f] == "above"], key=lambda f: -float(fr["by_family"][f]["shortfall_real_success"]["replan"]["value"])) if fresh_on else []
    put("RpFamFreshAboveList", fam_list(fabove) if fresh_on else "---", (fdir / "replan.json") if fresh_on else ctl_path,
        "the same list against the fresh-stream reference")
    top = max(FAMS, key=lambda f: float(rp["by_family"][f]["shortfall_real_success"]["replan"]["value"]))
    bt = rp["by_family"][top]
    put("RpFamTop", f"\\emph{{{top}}}", rp_path, "the family with the largest shortfall under replanning")
    put("RpFamTopN", ints(int(bt["n_instances"])), rp_path, f"by_family.{top}.n_instances")
    put("RpFamTopEmuReplan", ints(cnt(bt, "emulator", "replan")), rp_path, f"by_family.{top}.emulator.replan.real_success x n")
    put("RpFamTopEmuOpen", ints(cnt(bt, "emulator", "open_loop")), rp_path, f"by_family.{top}.emulator.open_loop.real_success x n")
    put("RpFamTopPerfReplan", ints(cnt(bt, "engine", "replan")), rp_path, f"by_family.{top}.engine.replan.real_success x n")
    put("RpFamTopPerfOpen", ints(cnt(bt, "engine", "open_loop")), rp_path, f"by_family.{top}.engine.open_loop.real_success x n")
    for f in FAMS:
        b, W = rp["by_family"][f], f"RpFam{F_WORD[f]}"
        put(W + "N", ints(int(b["n_instances"])), rp_path, f"by_family.{f}.n_instances")
        for m, mw in (("emulator", "Emu"), ("engine", "Perf")):
            for arm, aw in (("replan", "Replan"), ("open_loop", "Open")):
                put(f"{W}{mw}{aw}", ints(cnt(b, m, arm)), rp_path, f"by_family.{f}.{m}.{arm}.real_success x n")
        for q, qw in (("excess_false_acceptance", "Excess"), ("shortfall_real_success", "Short")):
            e = b[q]["replan"]
            put(W + qw, s3(e["value"]), rp_path, f"by_family.{f}.{q}.replan.value")
            put(W + qw + "CI", "[{}, {}]".format(*(s3(x) for x in lim(e))), rp_path, f"by_family.{f}.{q}.replan (BCa)")
            if fresh_on:
                e2 = fr["by_family"][f][q]["replan"]
                put(W + "Fresh" + qw, s3(e2["value"]), fdir / "replan.json", f"by_family.{f}.{q}.replan.value")
                put(W + "Fresh" + qw + "CI", "[{}, {}]".format(*(s3(x) for x in lim(e2))), fdir / "replan.json", f"by_family.{f}.{q}.replan (BCa)")
            else:
                put(W + "Fresh" + qw, "---", ctl_path, "the fresh-stream reference is absent")
                put(W + "Fresh" + qw + "CI", "", ctl_path, "the fresh-stream reference is absent")
        if fresh_on:
            fb = fr["by_family"][f]
            put(W + "FreshReplan", ints(cnt(fb, "engine", "replan")), fdir / "replan.json", f"by_family.{f}.engine.replan.real_success x n")
            put(W + "FreshOpen", ints(cnt(fb, "engine", "open_loop")), fdir / "replan.json", f"by_family.{f}.engine.open_loop.real_success x n")
        else:
            put(W + "FreshReplan", "---", ctl_path, "the fresh-stream reference is absent")
            put(W + "FreshOpen", "---", ctl_path, "the fresh-stream reference is absent")
    # the gate's own criterion in each control run: no task family's interval wholly below zero (R7 r2)
    for name_, c_ in (("control", ctl), ("fresh control", fc if fresh_ctl_on else None)):
        if c_ is not None:
            low = [f for f in FAMS if float(c_["by_family"][f]["hi"]) < 0]
            if low:
                raise Missing(f"{name_}: task families with an interval wholly below zero: {low}")
    # the Limits clause's outcome (R7 r3), built from the categories of R-a and R-c against the primary reference
    ka, kc = rp["readings"]["R-a"]["reading"], rp["readings"]["R-c"]["reading"]
    if ka == kc == "above":
        outc = "the excess and the shortfall survived"
    elif ka == kc == "includes_zero":
        outc = "no excess and no shortfall were established"
    elif ka == kc == "below":
        outc = "the excess and the shortfall lay below zero"
    else:
        outc = ({"above": "the excess survived", "includes_zero": "no excess was established",
                 "below": "the excess lay below zero"}[ka] + " and " +
                {"above": "the shortfall survived", "includes_zero": "no shortfall was established",
                 "below": "the shortfall lay below zero"}[kc])
    put("RpLimitsOutcome", outc, rp_path, "readings.R-a.reading and readings.R-c.reading (categories)")
    both_above = ka == kc == "above"
    fam_flags = {"RpFamAnyAbove": bool(above), "RpFamAbovePlural": len(above) > 1,
                 "RpFamOthersZero": all(st[f] == "zero" for f in FAMS if f not in above),
                 "RpFamDiffer": bool(fresh_on and fabove != above), "RpFamSomeNot": len(above) < len(FAMS),
                 "RpBothAbove": both_above, "RpFindOn": both_above and not frag["Ra"] and not frag["Rc"]}
    if set(vals) != set(_rp_names()) or len(vals) != len(_rp_names()):
        raise ValueError(f"replanning(): macros {sorted(set(vals) ^ set(_rp_names()))} differ from _rp_names()")
    for name in _rp_names():
        add(name, *vals[name])
    add_if("RpOn", True, rp_path, "replan.json present, controller version 3 as the control's, the control's gates "
           "hold, n_instances a multiple of 5 and at least 40")
    add_if("RpPrefix", n < int(ctl["pooled"]["n_instances"]), rp_path, "n_instances below the control's (a prefix)")
    add_if("RpRaZero", zero["Ra"], rp_path, "readings.R-a.reading == includes_zero")
    add_if("RpRcZero", zero["Rc"], rp_path, "readings.R-c.reading == includes_zero")
    fsrc = (fdir / "replan.json") if fresh_on else rp_path
    add_if("RpFreshOn", fresh_on, fsrc, "the fresh-stream reference's replan.json present and consistent")
    for _, w in RP_READINGS:
        add_if(f"Rp{w}Fragile", frag[w], fsrc, f"category of {w} differs between the two references")
    add_if("RpAnyFragile", any(frag.values()), fsrc, "any reading fragile")
    add_if("RpFragilePlural", sum(frag.values()) > 1, fsrc, "more than one reading fragile")
    add_if("RpFreshCtl", fresh_ctl_on, fsrc, "the fresh-stream control present")
    add_if("RpKeptEmuOn", kept_emu_on, rp_path, f"replan.json carries by_family.<family>.emulator.{RP_KEPT_FIELD}")
    for k, v in fam_flags.items():
        add_if(k, v, rp_path, {"RpFamAnyAbove": "some family has both by-family intervals above zero",
                               "RpFamAbovePlural": "more than one such family",
                               "RpFamOthersZero": "every other family has both intervals including zero",
                               "RpFamDiffer": "the fresh-stream reference gives a different list",
                               "RpFamSomeNot": "some family is not in the list",
                               "RpBothAbove": "R-a and R-c both above zero (primary reference)",
                               "RpFindOn": "R-a and R-c above zero against the primary reference and neither fragile"}[k])
    return {"on": True, "why": None}


def section5_b38():
    """the specification (the analysis plan, (d), (e)): the inflation's sign by family (pairs.csv), the single logged plan shared
    by every checkpoint (the audits' budget-1 records), and the cause of "not falsifiable at this size"
    (main_claim.json, results.secondary_d79.power.c120)."""
    import csv
    rows = list(csv.DictReader(open(src(PC))))
    fam = {}
    for r in rows:
        v = r.get("rl_inflation_1000000", "")
        if v not in ("", "nan"):
            fam.setdefault(r["family"], []).append(float(v))
    means = {f: float(np.mean(v)) for f, v in fam.items()}
    neg = sorted(v for v in means.values() if v < 0)
    add("AcInflNegN", RP_NUM_WORDS.get(len(neg), str(len(neg))), PC, "families whose mean rl_inflation_1000000 is below zero (count, as a word)")
    add("AcInflNegMin", s3(min(neg)), PC, "the lowest family mean of rl_inflation_1000000")
    add("AcInflNegMax", s3(max(neg)), PC, "the highest family mean below zero")
    d = J(MC)
    pw = d["results"]["secondary_d79"]["power"]["c120"]
    add("AcFidShareBetween", f"{100 * pw['decomposition']['share_between_families']:.0f}", MC,
        "results.secondary_d79.power.c120.decomposition.share_between_families x 100")
    add("AcFidPowerCkpt", f2(pw["power_checkpoint_level"]), MC, "results.secondary_d79.power.c120.power_checkpoint_level")
    add("AcFidPowerCkptRho", f"{pw['true_checkpoint_level_spearman']:.1f}", MC,
        "results.secondary_d79.power.c120.true_checkpoint_level_spearman")
    # the single logged plan (random search at budget 1) is the same plan, with the same engine verdict, on every
    # checkpoint: counted from the audits' own records
    plans, verdict, cks = {}, {}, set()
    paths = []
    for d_ in sorted(glob.glob(str(REPO / "results/audit/ladder/*/samples_*/tasks_v2_H24")))                  + sorted(glob.glob(str(REPO / "results/audit/ladder/*/samples_*/tasks_v2x_H24"))):
        if not LADDER_RUN.fullmatch(Path(d_).parent.parent.name):
            continue
        ck = Path(d_).parent.parent.name + "/" + Path(d_).parent.name
        cks.add(ck)
        paths.append(str(Path(d_) / "records.jsonl.gz"))
        for r in _records(Path(d_) / "records.jsonl.gz"):
            if r["method"] == "random" and int(r["budget"]) == 1:
                plans.setdefault(r["instance"], {})[ck] = r["plan_hash"]
                verdict.setdefault(r["instance"], {})[ck] = bool(r["oracle_accept"])
    if len(cks) != 24:
        raise Missing(f"single logged plan: {len(cks)} checkpoints with audits, not 24")
    same = [k for k in plans if len(plans[k]) == len(cks) and len(set(plans[k].values())) == 1
            and len(set(verdict[k].values())) == 1]
    add_multi("AcBOneSameN", ints(len(same)), paths, "instances whose budget-1 plan_hash and oracle verdict are identical on all 24 checkpoints")
    add_multi("AcBOneN", ints(len(plans)), paths, "instances with a budget-1 random-search record")


def compute_statement():
    """the specification : the compute statement in H200-equivalent hours, from
    results/analysis/compute_summary.json only (compute_summary.py: no card, pod, price or host name)."""
    cs = "results/analysis/compute_summary.json"
    S = J(cs)
    L, R, rp, e = S["local"], S["rented"], S["replanning"], S["engine_pool"]
    for k, w in (("training", "Train"), ("fidelity", "Fid"), ("audits_original", "Forty"),
                 ("audits_further", "Eighty"), ("pool_seeded", "Seed")):
        add(f"CompEq{w}", f"{L['by_arm'][k]:.1f}", cs, f"local.by_arm.{k} (H200-equivalent hours)")
    add("CompEqLocal", f"{L['total']:.0f}", cs, "local.total (H200-equivalent hours)")
    add("CompEqLocalOne", f"{L['total']:.1f}", cs, "local.total (H200-equivalent hours, one decimal)")
    add("CompModels", ints(L["models_trained"]), cs, "local.models_trained")
    add("CompUnfinished", ints(L["unfinished_jobs_not_counted"]), cs, "local.unfinished_jobs_not_counted")
    w0 = L["worker_log_from"]
    add("CompWorkerFrom", w0[:10] + " " + w0[11:16] + "Z", cs, "local.worker_log_from (date and time)")
    add("CompRentPods", ints(R["pods"]), cs, "rented.pods")
    add("CompEqRent", f"{R['total']:.0f}", cs, "rented.total (H200-equivalent hours)")
    add("CompEqTotalTen", ints(int(round(S["total_logged"] / 10.0)) * 10), cs,
        "total_logged (local and rented, H200-equivalent hours), rounded to the nearest ten")
    add("CompEqRentOne", f"{R['total']:.1f}", cs, "rented.total (one decimal)")
    add("CompEqRentRl", f"{R['rl']:.1f}", cs, "rented.rl (H200-equivalent hours)")
    add("CompEqRentEval", f"{R['evaluation']:.1f}", cs, "rented.evaluation (H200-equivalent hours)")
    add("CompRentEvalN", ints(R["evaluation_pods"]), cs, "rented.evaluation_pods")
    add("CompRentEvalOk", ints(R["evaluation_pods_with_result"]), cs, "rented.evaluation_pods_with_result")
    add("CompEqRentTrain", f"{R.get('extended_training', 0.0):.1f}", cs, "rented.extended_training (H200-equivalent hours)")
    add("CompEqRentNone", f"{R['no_result']:.1f}", cs, "rented.no_result (H200-equivalent hours)")
    add("CompRentNonePods", ints(R["no_result_pods"]), cs, "rented.no_result_pods")
    lo = S["left_out"]
    add("CompLeftOutHours", f"{lo['local_card_hours'] + lo['rented_card_hours']:.1f}", cs,
        "left_out.local_card_hours + left_out.rented_card_hours")
    add("CompLeftOutPods", ints(lo["rented_pods"]), cs, "left_out.rented_pods")
    add("CompEngineAudits", ints(e["audits"]), cs, "engine_pool.audits")
    add("CompEnginePH", ints(round(e["process_hours"])), cs, "engine_pool.process_hours")
    add("CompEngineRemoteShare", f2(e["remote_replay_share"]), cs, "engine_pool.remote_replay_share")
    add("CompReplanPerfN", ints(rp["perfect_instances"]), cs, "replanning.perfect_instances")
    add("CompReplanPerfHours", f"{rp['perfect_instance_wall_hours']:.1f}", cs, "replanning.perfect_instance_wall_hours")
    add_if("CompReplanEmuRead", bool(rp["emulator_side_read"]), cs, "replanning.emulator_side_read")
    add("CompReplanEmuN", ints(rp["emulator_instances"]) if rp["emulator_side_read"] else "---", cs,
        "replanning.emulator_instances")
    add("CompReplanEmuHours", f"{rp['emulator_instance_wall_hours']:.1f}" if rp["emulator_side_read"] else "---", cs,
        "replanning.emulator_instance_wall_hours")


def extended_training():
    """Sixfold extended one-step training control (os_50m_full_36m: 36,000,000 examples / 12 epochs)
    from results/analysis/extended_training.json and paper/data/ckpt_meta/os_50m_full_36m/."""
    et = "results/analysis/extended_training.json"
    d = J(et)
    if d.get("status") != "complete":
        raise Missing(f"{et}: status {d.get('status')!r}")
    sha_path = "paper/data/ckpt_meta/os_50m_full_36m/samples_036000000.pt.sha256"
    sha_hex = T(sha_path).split()[0]
    add("ExtTrSamples", ints(d["samples"]), et, "samples")
    add("ExtTrEpochs", ints(d["epochs_over_3m_store"]), et, "epochs_over_3m_store")
    add("ExtTrEpochsWord", "twelve", et, "epochs_over_3m_store (as word)")
    add("ExtTrSha", sha_hex[:12], sha_path, "first 12 hex digits of SHA-256")

    fid = d["fidelity"]
    t36 = fid["milestones_36m"]["test"]["36000000"]
    t06_ext = fid["milestones_36m"]["test"]["6000000"]
    t06 = fid["baseline_6m"]["test"]
    dl = fid["deltas_test_36m_minus_baseline_6m"]
    add("ExtTrTestElbo", mbox_neg(f"{t36['elbo']:.1f}"), et, "fidelity.milestones_36m.test.36000000.elbo")
    add("ExtTrBaseTestElbo", mbox_neg(f"{t06['elbo']:.1f}"), et, "fidelity.baseline_6m.test.elbo")
    add("ExtTrTestElboGain", f"{dl['elbo_nats']:.1f}", et, "fidelity.deltas_test_36m_minus_baseline_6m.elbo_nats")
    add("ExtTrDevElbo", mbox_neg(f"{fid['milestones_36m']['dev']['36000000']['elbo']:.1f}"), et,
        "fidelity.milestones_36m.dev.36000000.elbo")
    slope_pct = 100.0 * float(fid["last_tenth_slopes"]["terms"]["loss"]["relative_per_100k"])
    add("ExtTrLossSlopePct", mbox_neg(f"{slope_pct:.3f}"), et,
        "fidelity.last_tenth_slopes.terms.loss.relative_per_100k x 100")
    add("ExtTrTestFOne", f3(t36["f1_struct_1m"]), et, "fidelity.milestones_36m.test.36000000.f1_struct_1m")
    add("ExtTrTestFOneCI", f"[{f3(t36['f1_struct_1m_ci95'][0])}, {f3(t36['f1_struct_1m_ci95'][1])}]", et,
        "fidelity.milestones_36m.test.36000000.f1_struct_1m_ci95")
    add("ExtTrTestFunds", f3(t36["funds_medrel_12m"]), et, "fidelity.milestones_36m.test.36000000.funds_medrel_12m")
    add("ExtTrFirstFunds", f3(t06_ext["funds_medrel_12m"]), et, "fidelity.milestones_36m.test.6000000.funds_medrel_12m")
    add("ExtTrTestPop", f3(t36["pop_medrel_12m"]), et, "fidelity.milestones_36m.test.36000000.pop_medrel_12m")
    add("ExtTrMeanOv", f3(t36["mean_overlay_ratio_24m"]), et, "fidelity.milestones_36m.test.36000000.mean_overlay_ratio_24m")
    add("ExtTrBaseMeanOv", f3(t06["mean_overlay_ratio_24m"]), et, "fidelity.baseline_6m.test.mean_overlay_ratio_24m")
    add("ExtTrFirstMeanOv", f3(t06_ext["mean_overlay_ratio_24m"]), et, "fidelity.milestones_36m.test.6000000.mean_overlay_ratio_24m")
    add("ExtTrGeCopy", ints(t36["n_overlays_ge_1"]), et, "fidelity.milestones_36m.test.36000000.n_overlays_ge_1")
    add("ExtTrPowMae", f"{t36['open_loop_powered_zones_mae_24m']:.1f}", et,
        "fidelity.milestones_36m.test.36000000.open_loop_powered_zones_mae_24m")
    add("ExtTrTrainPowBase", f"{fid['baseline_6m']['train_eval']['open_loop_powered_zones_mae_24m']:.1f}", et,
        "fidelity.baseline_6m.train_eval.open_loop_powered_zones_mae_24m")
    add("ExtTrTrainPow", f"{fid['milestones_36m']['train_eval']['36000000']['open_loop_powered_zones_mae_24m']:.1f}", et,
        "fidelity.milestones_36m.train_eval.36000000.open_loop_powered_zones_mae_24m")
    add("ExtTrKlStart", f"{t06['kl']:.1f}", et, "fidelity.baseline_6m.test.kl")
    add("ExtTrKlEnd", f"{t36['kl']:.1f}", et, "fidelity.milestones_36m.test.36000000.kl")
    t30 = fid["milestones_36m"]["test"]["30000000"]
    add("ExtTrLastTwoElboGain", f"{t36['elbo'] - t30['elbo']:.1f}", et,
        "fidelity.milestones_36m.test.36000000.elbo minus 30000000.elbo")
    b3s = list(fid["baseline_3seed_test"].values())
    add("ExtTrSeedGeMin", ints(min(x["n_overlays_ge_1"] for x in b3s)), et, "min n_overlays_ge_1 across 3 baseline 50M seeds")
    add("ExtTrSeedGeMax", ints(max(x["n_overlays_ge_1"] for x in b3s)), et, "max n_overlays_ge_1 across 3 baseline 50M seeds")
    add("ExtTrSeedPowMin", f"{min(x['open_loop_powered_zones_mae_24m'] for x in b3s):.1f}", et,
        "min open_loop_powered_zones_mae_24m across 3 baseline 50M seeds")
    add("ExtTrSeedPowMax", f"{max(x['open_loop_powered_zones_mae_24m'] for x in b3s):.1f}", et,
        "max open_loop_powered_zones_mae_24m across 3 baseline 50M seeds")

    # Milestone B=1 single-plan trajectory across 120 cities (6M..36M) and showcase replays
    mb1 = d["milestones_b1_120"]
    b1_main = d["audit_120_cities"]["random"]["1"]["c120"]["all"]["main_6m"]
    add("ExtTrMainRandOneAllHack", f3(est(b1_main["false_acceptance"])), et, "audit_120_cities.random.1.c120.all.main_6m.false_acceptance.value")
    add("ExtTrMainRandOneAllExcess", s3(est(b1_main["excess"])), et, "audit_120_cities.random.1.c120.all.main_6m.excess.value")
    add("ExtTrMainRandOneAllFalseRej", f3(est(b1_main["false_rejection"])), et, "audit_120_cities.random.1.c120.all.main_6m.false_rejection.value")
    add("ExtTrMainRandOneAllJudgeAcc", f3(est(b1_main["judge_accept"])), et, "audit_120_cities.random.1.c120.all.main_6m.judge_accept.value")
    mb_06 = mb1["6000000"]["all"]["ext_36m"]
    mb_24 = mb1["24000000"]["all"]["ext_36m"]
    mb_30 = mb1["30000000"]["all"]["ext_36m"]
    add("ExtTrMileTwoJudgeAcc", f3(est(mb_06["judge_accept"])), et, "milestones_b1_120.6000000.all.ext_36m.judge_accept.value")
    add("ExtTrMileTwoFalseRej", f3(est(mb_06["false_rejection"])), et, "milestones_b1_120.6000000.all.ext_36m.false_rejection.value")
    add("ExtTrMileEightEpochs", "8", et, "24,000,000 / 3,000,000 epochs")
    add("ExtTrMileEightSamples", ints(24_000_000), et, "milestones_b1_120: 24,000,000 examples")
    add("ExtTrMileEightExcess", s3(est(mb_24["excess"])), et, "milestones_b1_120.24000000.all.ext_36m.excess.value")
    add("ExtTrMileEightExcessCI", ci(mb_24["excess"], signed=True), et, "milestones_b1_120.24000000.all.ext_36m.excess.bca")
    add("ExtTrMileTenEpochs", "10", et, "30,000,000 / 3,000,000 epochs")
    add("ExtTrMileTenSamples", ints(30_000_000), et, "milestones_b1_120: 30,000,000 examples")
    add("ExtTrMileTenExcess", s3(est(mb_30["excess"])), et, "milestones_b1_120.30000000.all.ext_36m.excess.value")
    add("ExtTrMileTenExcessCI", ci(mb_30["excess"], signed=True), et, "milestones_b1_120.30000000.all.ext_36m.excess.bca")
    add("ExtTrMileTenFalseRej", f3(est(mb_30["false_rejection"])), et, "milestones_b1_120.30000000.all.ext_36m.false_rejection.value")

    sh36 = d["showcase_36m"]
    add("ExtTrFigOnePass", ints(sh36["fig1_cpu_36m"]["n_pass_of_8"]), et, "showcase_36m.fig1_cpu_36m.n_pass_of_8")
    add("ExtTrGalStartAcc", ints(sh36["milestones"]["6000000"]["gallery_n_accepted_of_15"]), et,
        "showcase_36m.milestones.6000000.gallery_n_accepted_of_15")
    add("ExtTrGalEndAcc", ints(sh36["milestones"]["36000000"]["gallery_n_accepted_of_15"]), et,
        "showcase_36m.milestones.36000000.gallery_n_accepted_of_15")

    # 120-city (574-instance) planning audits and 193-instance B=10,000 adaptive CEM
    aud120 = d["audit_120_cities"]
    for m, B, tag in (("random", "1", "RandOneAll"), ("random", "1000", "RandThouAll"), ("cem_seeded", "1000", "AdThouAll")):
        blk = aud120[m][B]["c120"]["all"]
        loc = f"audit_120_cities.{m}.{B}.c120.all."
        e36, df = blk["ext_36m"], blk["diff_36m_minus_6m"]
        for k, kw in (("false_acceptance", "Hack"), ("oracle_accept", "OrAcc"), ("false_rejection", "FalseRej"), ("judge_accept", "JudgeAcc")):
            add(f"ExtTr{tag}{kw}", f3(est(e36[k])), et, loc + f"ext_36m.{k}.value")
            add(f"ExtTr{tag}{kw}CI", ci(e36[k]), et, loc + f"ext_36m.{k}.bca")
        add(f"ExtTr{tag}Excess", s3(est(e36["excess"])), et, loc + "ext_36m.excess.value")
        add(f"ExtTr{tag}ExcessCI", ci(e36["excess"], signed=True), et, loc + "ext_36m.excess.bca")
        add(f"ExtTr{tag}OrDiff", s3(est(df["oracle_accept"])), et, loc + "diff_36m_minus_6m.oracle_accept.value")
        add(f"ExtTr{tag}OrDiffCI", ci(df["oracle_accept"], signed=True), et, loc + "diff_36m_minus_6m.oracle_accept.bca")

    c40_ad3 = aud120["cem_seeded"]["1000"]["c40"]["all"]["ext_36m"]
    add("ExtTrAdThouCoreOrAcc", f3(est(c40_ad3["oracle_accept"])), et, "audit_120_cities.cem_seeded.1000.c40.all.ext_36m.oracle_accept.value")
    add("ExtTrAdThouCoreOrAccCI", ci(c40_ad3["oracle_accept"]), et, "audit_120_cities.cem_seeded.1000.c40.all.ext_36m.oracle_accept.bca")
    add("ExtTrAdThouCoreExcess", s3(est(c40_ad3["excess"])), et, "audit_120_cities.cem_seeded.1000.c40.all.ext_36m.excess.value")
    add("ExtTrAdThouCoreExcessCI", ci(c40_ad3["excess"], signed=True), et, "audit_120_cities.cem_seeded.1000.c40.all.ext_36m.excess.bca")
    add("ExtTrAdThouCoreFalseRej", f3(est(c40_ad3["false_rejection"])), et, "audit_120_cities.cem_seeded.1000.c40.all.ext_36m.false_rejection.value")

    b1_tr = aud120["random"]["1"]["c120"]["by_family"]["treasury"]["ext_36m"]
    add("ExtTrRandOneAllTreasExcess", s3(est(b1_tr["excess"])), et, "audit_120_cities.random.1.c120.by_family.treasury.ext_36m.excess.value")
    add("ExtTrRandOneAllTreasExcessCI", ci(b1_tr["excess"], signed=True), et, "audit_120_cities.random.1.c120.by_family.treasury.ext_36m.excess.bca")
    add("ExtTrRandOneAllTreasFalseRej", f3(est(b1_tr["false_rejection"])), et, "audit_120_cities.random.1.c120.by_family.treasury.ext_36m.false_rejection.value")

    for fam_k, fam_tag in (("treasury", "Treas"), ("power", "Power"), ("recover", "Recov")):
        fb = aud120["cem_seeded"]["1000"]["c120"]["by_family"][fam_k]["diff_36m_minus_6m"]["oracle_accept"]
        add(f"ExtTrAdThouAll{fam_tag}OrDiff", s3(est(fb)), et,
            f"audit_120_cities.cem_seeded.1000.c120.by_family.{fam_k}.diff_36m_minus_6m.oracle_accept.value")
        add(f"ExtTrAdThouAll{fam_tag}OrDiffCI", ci(fb, signed=True), et,
            f"audit_120_cities.cem_seeded.1000.c120.by_family.{fam_k}.diff_36m_minus_6m.oracle_accept.bca")

    a1e4 = d["audit_1e4"]["all"]
    e1e4, m1e4, p1e4, d1e4 = a1e4["ext_36m"], a1e4["main_6m"], a1e4["perfect"], a1e4["diff_36m_minus_6m"]
    for k, kw in (("false_acceptance", "Hack"), ("oracle_accept", "OrAcc"), ("false_rejection", "FalseRej"), ("judge_accept", "JudgeAcc")):
        add(f"ExtTrTenThou{kw}", f3(est(e1e4[k])), et, f"audit_1e4.all.ext_36m.{k}.value")
        add(f"ExtTrTenThou{kw}CI", ci(e1e4[k]), et, f"audit_1e4.all.ext_36m.{k}.bca")
    add("ExtTrMainTenThouFalseRej", f3(est(m1e4["false_rejection"])), et, "audit_1e4.all.main_6m.false_rejection.value")
    add("ExtTrPerfTenThouFalseRej", f3(est(p1e4["false_rejection"])), et, "audit_1e4.all.perfect.false_rejection.value")
    add("ExtTrTenThouExcess", s3(est(e1e4["excess"])), et, "audit_1e4.all.ext_36m.excess.value")
    add("ExtTrTenThouExcessCI", ci(e1e4["excess"], signed=True), et, "audit_1e4.all.ext_36m.excess.bca")
    sh = e1e4["shortfall"]
    add("ExtTrTenThouShort", u3(-sh["value"]), et, "audit_1e4.all.ext_36m.shortfall.value x -1 (perfect minus emulator)")
    add("ExtTrTenThouShortCI", f"[{u3(-sh['bca_hi'])}, {u3(-sh['bca_lo'])}]", et, "audit_1e4.all.ext_36m.shortfall.bca x -1")
    add("ExtTrTenThouOrDiff", s3(est(d1e4["oracle_accept"])), et, "audit_1e4.all.diff_36m_minus_6m.oracle_accept.value")
    add("ExtTrTenThouOrDiffCI", ci(d1e4["oracle_accept"], signed=True), et, "audit_1e4.all.diff_36m_minus_6m.oracle_accept.bca")
    con36 = {c["contrast"]: c for c in d["pressure_axis_36m"]["bca"]["contrasts_at_10000"]}
    cr_emu = con36["real success, emulator: at 10,000 minus at 1,000"]["per_comparison"]
    add("ExtTrEmuOrAccRise", s3(cr_emu["value"]), et, "pressure_axis_36m.bca.contrasts_at_10000[real success, emulator: 10,000 - 1,000].per_comparison.value")
    add("ExtTrEmuOrAccRiseCI", ci(cr_emu, signed=True), et, "pressure_axis_36m.bca.contrasts_at_10000[real success, emulator: 10,000 - 1,000].per_comparison.bca")

    fams_1e4 = d["audit_1e4"]["by_family"]
    n_zero_acc = sum(1 for fk in ("grow", "solvent", "treasury", "recover", "power")
                     if fams_1e4[fk]["ext_36m"]["judge_accept"]["value"] == 0.0)
    add("ExtTrZeroAccFams", ints(n_zero_acc), et, "count of families with 0.000 self-acceptance at B=10,000 on 12-epoch model")

    pw1e4 = fams_1e4["power"]
    add("ExtTrMainPowerTenThouExcess", s3(est(pw1e4["main_6m"]["excess"])), et, "audit_1e4.by_family.power.main_6m.excess.value")
    add("ExtTrPowerTenThouExcess", s3(est(pw1e4["ext_36m"]["excess"])), et, "audit_1e4.by_family.power.ext_36m.excess.value")
    add("ExtTrPowerTenThouExcessCI", ci(pw1e4["ext_36m"]["excess"], signed=True), et, "audit_1e4.by_family.power.ext_36m.excess.bca")
    add("ExtTrPowerTenThouOrAcc", f3(est(pw1e4["ext_36m"]["oracle_accept"])), et, "audit_1e4.by_family.power.ext_36m.oracle_accept.value")
    add("ExtTrMainPowerTenThouOrAcc", f3(est(pw1e4["main_6m"]["oracle_accept"])), et, "audit_1e4.by_family.power.main_6m.oracle_accept.value")
    add("ExtTrPowerTenThouOrDiff", s3(est(pw1e4["diff_36m_minus_6m"]["oracle_accept"])), et,
        "audit_1e4.by_family.power.diff_36m_minus_6m.oracle_accept.value")
    add("ExtTrPowerTenThouOrDiffCI", ci(pw1e4["diff_36m_minus_6m"]["oracle_accept"], signed=True), et,
        "audit_1e4.by_family.power.diff_36m_minus_6m.oracle_accept.bca")

    rc1e4 = fams_1e4["recover"]
    add("ExtTrMainRecovTenThouJudgeAcc", f3(est(rc1e4["main_6m"]["judge_accept"])), et, "audit_1e4.by_family.recover.main_6m.judge_accept.value")
    add("ExtTrRecovTenThouJudgeAcc", f3(est(rc1e4["ext_36m"]["judge_accept"])), et, "audit_1e4.by_family.recover.ext_36m.judge_accept.value")
    add("ExtTrRecovTenThouExcess", s3(est(rc1e4["ext_36m"]["excess"])), et, "audit_1e4.by_family.recover.ext_36m.excess.value")
    add("ExtTrMainRecovTenThouOrAcc", f3(est(rc1e4["main_6m"]["oracle_accept"])), et, "audit_1e4.by_family.recover.main_6m.oracle_accept.value")
    add("ExtTrRecovTenThouOrAcc", f3(est(rc1e4["ext_36m"]["oracle_accept"])), et, "audit_1e4.by_family.recover.ext_36m.oracle_accept.value")

    tr1e4 = fams_1e4["treasury"]
    add("ExtTrMainTreasTenThouExcess", s3(est(tr1e4["main_6m"]["excess"])), et, "audit_1e4.by_family.treasury.main_6m.excess.value")
    add("ExtTrTreasTenThouExcess", s3(est(tr1e4["ext_36m"]["excess"])), et, "audit_1e4.by_family.treasury.ext_36m.excess.value")
    add("ExtTrTreasTenThouFalseRej", f3(est(tr1e4["ext_36m"]["false_rejection"])), et, "audit_1e4.by_family.treasury.ext_36m.false_rejection.value")

    # PPO at 1,000,000 steps (15 runs = 5 families x 3 seeds)
    def _rl_est_dict(x):
        return {"value": x["value"], **x["city_only"]}

    rl = d["rl"]
    add("ExtTrRlRuns", "15", et, "rl: 5 task families x 3 seeds")
    add("ExtTrRlSpatialRuns", "12", et, "rl.spatial4: 4 spatial task families x 3 seeds")
    for sc, sw in (("all", ""), ("treasury", "Treas"), ("spatial4", "Spat")):
        blk = rl[sc]
        loc = f"rl.{sc}."
        for k, kw, sgn in (("dream", "Dream", False), ("oracle", "Oracle", False), ("closed", "Closed", False),
                           ("gap", "Gap", True), ("excess0", "AxExcess", True)):
            fmt = s3 if sgn else f3
            e36 = _rl_est_dict(blk["ext_36m"][k])
            m06 = _rl_est_dict(blk["main_6m"][k])
            df = _rl_est_dict(blk["diff_36m_minus_6m"][k])
            add(f"ExtTrRl{sw}{kw}", fmt(est(e36)), et, loc + f"ext_36m.{k}.value")
            add(f"ExtTrRl{sw}{kw}CI", ci(e36, signed=sgn), et, loc + f"ext_36m.{k}.city_only.bca")
            add(f"ExtTrMainRl{sw}{kw}", fmt(est(m06)), et, loc + f"main_6m.{k}.value")
            add(f"ExtTrRl{sw}{kw}Diff", s3(est(df)), et, loc + f"diff_36m_minus_6m.{k}.value")
            add(f"ExtTrRl{sw}{kw}DiffCI", ci(df, signed=True), et, loc + f"diff_36m_minus_6m.{k}.city_only.bca")

    # Out-of-sample cross-model calibration (25 checkpoints, 125 pairs)
    ac = d["across_25_checkpoints"]
    add("ExtTrOosCkpts", ints(ac["n_checkpoints"]), et, "across_25_checkpoints.n_checkpoints")
    add("ExtTrOosPairs", ints(ac["n_pairs"]), et, "across_25_checkpoints.n_pairs")
    b1 = ac["b1_vs_inflation_same_lineage"]
    add("ExtTrOosBOneWithin", s3(est(b1["within_mean_spearman"])), et, "across_25_checkpoints.b1_vs_inflation_same_lineage.within_mean_spearman.value")
    add("ExtTrOosBOneWithinCI", ci(b1["within_mean_spearman"], signed=True), et, "across_25_checkpoints.b1_vs_inflation_same_lineage.within_mean_spearman.lo/hi")
    add("ExtTrOosBOneWithinLinCI", ci(b1["within_mean_spearman_lineage"], signed=True), et,
        "across_25_checkpoints.b1_vs_inflation_same_lineage.within_mean_spearman_lineage.lo/hi")
    add("ExtTrOosBOneRho", s3(est(b1["pooled_spearman"])), et, "across_25_checkpoints.b1_vs_inflation_same_lineage.pooled_spearman.value")
    add("ExtTrOosBOneRhoCI", ci(b1["pooled_spearman"], signed=True), et, "across_25_checkpoints.b1_vs_inflation_same_lineage.pooled_spearman.lo/hi")
    add("ExtTrOosBOneRhoLinCI", ci(b1["pooled_spearman_lineage"], signed=True), et,
        "across_25_checkpoints.b1_vs_inflation_same_lineage.pooled_spearman_lineage.lo/hi")
    b1g = ac["b1_vs_gap_same_lineage"]
    add("ExtTrOosBOneGapRho", s3(est(b1g["pooled_spearman"])), et, "across_25_checkpoints.b1_vs_gap_same_lineage.pooled_spearman.value")
    add("ExtTrOosBOneGapRhoCI", ci(b1g["pooled_spearman"], signed=True), et, "across_25_checkpoints.b1_vs_gap_same_lineage.pooled_spearman.lo/hi")
    b3 = ac["b1000_vs_inflation_same_lineage"]
    add("ExtTrOosShootWithin", s3(est(b3["within_mean_spearman"])), et, "across_25_checkpoints.b1000_vs_inflation_same_lineage.within_mean_spearman.value")
    add("ExtTrOosShootWithinCI", ci(b3["within_mean_spearman"], signed=True), et, "across_25_checkpoints.b1000_vs_inflation_same_lineage.within_mean_spearman.lo/hi")
    add("ExtTrOosShootRho", s3(est(b3["pooled_spearman"])), et, "across_25_checkpoints.b1000_vs_inflation_same_lineage.pooled_spearman.value")
    add("ExtTrOosShootRhoCI", ci(b3["pooled_spearman"], signed=True), et, "across_25_checkpoints.b1000_vs_inflation_same_lineage.pooled_spearman.lo/hi")
    elb = ac["elbo_vs_b1000_finals_13"]
    add("ExtTrOosFinals", ints(elb["pooled_spearman"]["n_clusters"]), et, "across_25_checkpoints.elbo_vs_b1000_finals_13.pooled_spearman.n_clusters")
    add("ExtTrOosElboRho", s3(est(elb["pooled_spearman"])), et, "across_25_checkpoints.elbo_vs_b1000_finals_13.pooled_spearman.value")
    add("ExtTrOosElboRhoCI", ci(elb["pooled_spearman"], signed=True), et, "across_25_checkpoints.elbo_vs_b1000_finals_13.pooled_spearman.lo/hi")
    f1c = ac["f1_1m_vs_b1000_finals_13"]
    add("ExtTrOosFOneRho", s3(est(f1c["pooled_spearman"])), et, "across_25_checkpoints.f1_1m_vs_b1000_finals_13.pooled_spearman.value")
    add("ExtTrOosFOneRhoCI", ci(f1c["pooled_spearman"], signed=True), et, "across_25_checkpoints.f1_1m_vs_b1000_finals_13.pooled_spearman.lo/hi")

    # Write paper/tables/extended_36m.tex (four compact panels)
    p1 = []
    p1.append(" & ".join([
        "Primary (50M)", ints(6_000_000), "2",
        mbox_neg(f"{t06['elbo']:.1f}"), f3(t06["f1_struct_1m"]), f3(t06["pop_medrel_12m"]), f3(t06["funds_medrel_12m"]),
        f"{f3(t06['mean_overlay_ratio_24m'])} ({t06['n_overlays_ge_1']}/8)", f"{t06['open_loop_powered_zones_mae_24m']:.1f}",
        tex_ci(b1_main["excess"], True),
        f"{f3(est(b1_main['false_rejection']))}/{f3(est(b1_main['judge_accept']))}",
        T("paper/data/ckpt_meta/os_50m_full/samples_006000000.pt.sha256").split()[0][:10],
    ]) + r" \\")
    p1.append(r"\midrule")
    for m_step in (6_000_000, 12_000_000, 18_000_000, 24_000_000, 30_000_000, 36_000_000):
        row = fid["milestones_36m"]["test"][str(m_step)]
        mb_arm = mb1[str(m_step)]["all"]["ext_36m"]
        m_sha = T(f"paper/data/ckpt_meta/os_50m_full_36m/samples_{m_step:09d}.pt.sha256").split()[0][:10]
        p1.append(" & ".join([
            "Extended (50M)" if m_step == 6_000_000 else "",
            ints(m_step), str(m_step // 3_000_000),
            mbox_neg(f"{row['elbo']:.1f}"), f3(row["f1_struct_1m"]), f3(row["pop_medrel_12m"]), f3(row["funds_medrel_12m"]),
            f"{f3(row['mean_overlay_ratio_24m'])} ({row['n_overlays_ge_1']}/8)", f"{row['open_loop_powered_zones_mae_24m']:.1f}",
            tex_ci(mb_arm["excess"], True),
            f"{f3(est(mb_arm['false_rejection']))}/{f3(est(mb_arm['judge_accept']))}",
            m_sha,
        ]) + r" \\")

    p2 = []
    plan_specs = [
        (r"Single plan ($10^{0}$, 120 cities)", aud120["random"]["1"]["c120"]["all"]),
        (r"Random ($10^{3}$, 120 cities)", aud120["random"]["1000"]["c120"]["all"]),
        (r"Adaptive CEM ($10^{3}$, 120 cities)", aud120["cem_seeded"]["1000"]["c120"]["all"]),
        (r"Adaptive CEM ($10^{4}$, 40-city core)", a1e4),
    ]
    for idx, (label, blk) in enumerate(plan_specs):
        if idx > 0:
            p2.append(r"\midrule")
        pf = blk["perfect"]
        for who_lbl, arm in (("Primary (2 ep.)", blk["main_6m"]), ("Extended (12 ep.)", blk["ext_36m"])):
            lead = label if who_lbl.startswith("Primary") else ""
            p2.append(" & ".join([
                lead, who_lbl,
                tex_ci(arm["false_acceptance"]), f3(est(pf["false_acceptance"])),
                tex_ci(arm["excess"], True),
                tex_ci(arm["oracle_accept"]), f3(est(pf["oracle_accept"])),
                f"{f3(est(arm['false_rejection']))} / {f3(est(arm['judge_accept']))}",
            ]) + r" \\")

    p2b = []
    for fk in ("grow", "solvent", "treasury", "recover", "power"):
        fb = fams_1e4[fk]
        m6, e3, pf, df = fb["main_6m"], fb["ext_36m"], fb["perfect"], fb["diff_36m_minus_6m"]
        p2b.append(" & ".join([
            rf"\emph{{{fk}}} ({fb['n']})",
            f"{f3(est(m6['judge_accept']))}/{f3(est(e3['judge_accept']))}",
            tex_ci(m6["excess"], True),
            tex_ci(e3["excess"], True),
            f"{f3(est(m6['oracle_accept']))}/{f3(est(e3['oracle_accept']))}/{f3(est(pf['oracle_accept']))}",
            tex_ci(df["oracle_accept"], True),
            f"{f3(est(m6['false_rejection']))}/{f3(est(e3['false_rejection']))}",
        ]) + r" \\")

    p3 = []
    rl_specs = [
        (r"\emph{treasury} (3 seeds)", rl["treasury"]),
        ("Spatial families (12 seeds)", rl["spatial4"]),
        ("All five families (15 seeds)", rl["all"]),
    ]
    for idx, (label, blk) in enumerate(rl_specs):
        if idx > 0:
            p3.append(r"\midrule")
        for who_lbl, key in (("Primary (2 ep.)", "main_6m"), ("Extended (12 ep.)", "ext_36m")):
            lead = label if key == "main_6m" else ""
            arm = blk[key]
            diff_cell = "" if key == "main_6m" else tex_ci(_rl_est_dict(blk["diff_36m_minus_6m"]["oracle"]), True)
            p3.append(" & ".join([
                lead, who_lbl,
                f3(est(_rl_est_dict(arm["dream"]))),
                tex_ci(_rl_est_dict(arm["oracle"])),
                tex_ci(_rl_est_dict(arm["gap"]), True),
                tex_ci(_rl_est_dict(arm["closed"])),
                diff_cell,
            ]) + r" \\")

    tab_tex = (
        "% Generated by paper/scripts/make_numbers.py from results/analysis/extended_training.json\n"
        r"\setlength{\tabcolsep}{1.5pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrlrrcclcr@{}}" "\n"
        r"\toprule" "\n"
        r"Run & Examples & Ep. & ELBO & 1m F1 & 12m pop & 12m funds & 24m ov.\ ($\ge$ copy) & 24m pow. & $10^{0}$ excess & $10^{0}$ rej./acc. & SHA-256 \\" "\n"
        r"\midrule" "\n" + "\n".join(p1) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n\n"
        r"\vspace{4pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llllllll@{}}" "\n"
        r"\toprule" "\n"
        r"Planning regime & Model & False acceptance & Ref. & Excess & Truly passing & Ref. & False rej.\,/\,acc. \\" "\n"
        r"\midrule" "\n" + "\n".join(p2) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n\n"
        r"\vspace{4pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcllclc@{}}" "\n"
        r"\toprule" "\n"
        r"Family ($10^{4}$ CEM) & Acc.\ (2/12) & Excess (2 ep.) & Excess (12 ep.) & Oracle (2/12/ref.) & Oracle diff. & Rej.\ (2/12) \\" "\n"
        r"\midrule" "\n" + "\n".join(p2b) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n\n"
        r"\vspace{4pt}" "\n"
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lllllll@{}}" "\n"
        r"\toprule" "\n"
        r"PPO scope ($10^{6}$ steps) & Model & Dream & Oracle pass & Optimism gap & Closed loop & Oracle diff. \\" "\n"
        r"\midrule" "\n" + "\n".join(p3) + "\n" r"\bottomrule" "\n" r"\end{tabular*}" "\n"
    )
    (PAPER / "tables" / "extended_36m.tex").write_text(tab_tex)


def main():
    groups = main_reference()
    groups.update(seeded_reference())
    main_card()
    engine_reference()
    tasks_and_data()
    test_rows = fidelity_test()
    patching()
    _, _, full, complete = rl_arm()
    defences_seeded(defences())
    treasury_identity()
    pressure_axis()
    text_guards(groups, full)
    extra_cities()
    replication()
    coverage(full)
    hyper()
    across()
    section5_b38()
    gallery()
    misc()
    design_constants()
    design()
    wp = revision()
    table_main(groups)
    table_family(groups, wp)
    table_test(test_rows)
    table_rl(full, complete)
    replanning()
    compute_statement()
    extended_training()
    sys.path.insert(0, str(PAPER / "scripts"))
    import protocols                                        # appendix B's protocols, generated from the code
    protocols.protocols(sys.modules[__name__])
    write()


if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser(description="Generate paper/numbers.tex, the generated tables and the macro ledger.")
    _ap.add_argument("--replan-dir", default=None,
                     help="tests and dry builds only: read replan.json (and replan_control.json, if there) from this "
                          f"directory instead of results/analysis/ (also the environment variable {REPLAN_DIR_ENV}); "
                          "never write a stand-in to results/analysis/replan.json")
    _a = _ap.parse_args()
    if _a.replan_dir:
        os.environ[REPLAN_DIR_ENV] = _a.replan_dir
    main()
