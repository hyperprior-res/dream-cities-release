"""Tests for monthly closed-loop replanning macro generation in ``paper/scripts/make_numbers.py``
and conditional prose expansion in ``paper/sections/switched.tex``.

Synthetic inputs only: ``replan.json`` is built from synthetic records via ``replan_axis.analyse`` and read through
an override directory; nothing under ``results/replan/emulator`` is read and nothing is written to
``results/analysis/``. Stored exact-simulator control files are read directly on CPU."""
from __future__ import annotations

import itertools
import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "paper" / "scripts", ROOT / "code" / "scripts", ROOT / "code", ROOT / "hpr-dream"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import make_numbers as MN  # noqa: E402
import replan_axis as RA  # noqa: E402

FAMS = RA.FAMILIES
READS = ("R-a", "R-b", "R-c", "R-d")
STATES = ("above", "includes_zero", "below")
NEEDED = [ROOT / MN.RP_CONTROL, ROOT / MN.RP_ENGINE_CONFIG, ROOT / MN.RP_V1, ROOT / MN.RP_V2]
pytestmark = pytest.mark.skipif(not all(p.exists() for p in NEEDED), reason="control files not present")


def synthetic(n=100, seed=0, version=3, n_plans=1000, engine_stream=None) -> dict:
    """replan_axis.analyse on synthetic records: n instances in fixed benchmark family pattern, random verdicts."""
    rng = np.random.default_rng(seed)
    runs = []
    for _ in range(2):
        R = {}
        for i in range(n):
            k = f"s{i // 3:02d}|{FAMS[i % 5]}|H24"
            acc, rp, ol = (bool(x) for x in rng.random(3) < (0.5, 0.4, 0.4))
            R[k] = {"instance": k, "cluster": f"s{i // 3:02d}", "task": FAMS[i % 5], "realised_seed": i,
                    "n_plans": n_plans, "order_index": i, "controller_version": version, "accept0": acc,
                    "replan_pass": rp, "open_loop_pass": ol, "open_loop": {"oracle_accept": ol}}
            if engine_stream and len(runs) == 1:
                R[k]["seed_stream"] = engine_stream
        runs.append(R)
    res = json.loads(json.dumps(RA.analyse(runs[0], runs[1], n_boot=200)))
    res.setdefault("order_index", list(range(n)))
    res.setdefault("prefix", True)
    return res


def force(res: dict, states: dict) -> dict:
    """Set each reading to a state with a consistent interval and wording (as replan_axis writes it)."""
    lims = {"above": (0.012, 0.094), "includes_zero": (-0.041, 0.057), "below": (-0.088, -0.006)}
    for r, s in states.items():
        lo, hi = lims[s]
        d = res["readings"][r]
        d.update(lo=lo, hi=hi, reading=s, wording=RA.WORDING[r][s], interval_width=hi - lo, interval_used="bca")
        d["estimate"]["value"] = (lo + hi) / 2
    return res


def reset():
    MN.MACROS.clear()
    MN.IFS.clear()
    MN.SOURCES.clear()
    MN._cache.clear()


def run(tmp: Path, res: dict | None, control: dict | None = None) -> tuple[dict, dict, dict]:
    tmp.mkdir(parents=True, exist_ok=True)
    if res is not None:
        (tmp / "replan.json").write_text(json.dumps(res))
    if control is not None:
        (tmp / "replan_control.json").write_text(json.dumps(control))
    reset()
    state = MN.replanning(override=str(tmp))
    macros = {m[0]: m[1] for m in MN.MACROS}
    flags = {i[0]: i[1] for i in MN.IFS}
    return state, macros, flags


def test_off_while_the_file_is_absent(tmp_path):
    state, macros, flags = run(tmp_path, None)
    assert not state["on"] and state["why"] == "replan.json absent"
    assert list(macros) == MN._rp_names() and all(v == "" for v in macros.values())
    assert set(flags) == set(MN.RP_SWITCHES) and not any(flags.values())
    assert all(n.startswith("Rp") and re.fullmatch(r"[A-Za-z]+", n) for n in macros)


@pytest.mark.parametrize("change", ["version 2", "35 instances", "failed control", "control of version 2"])
def test_off_conditions(tmp_path, change):
    res = synthetic(n=35 if change == "35 instances" else 40, version=2 if change == "version 2" else 3)
    ctl = None
    if change in ("failed control", "control of version 2"):
        ctl = json.loads((ROOT / MN.RP_CONTROL).read_text())
        if change == "failed control":
            ctl["enters_paper_if_complete_and_reviewed"] = False
        else:
            ctl["controller_version"] = 2
    state, macros, flags = run(tmp_path, res, ctl)
    assert not state["on"], state
    assert all(v == "" for v in macros.values()) and not any(flags.values())


@pytest.mark.parametrize("s", STATES)
def test_on_carries_the_fixed_wordings(tmp_path, s):
    res = force(synthetic(n=40), {r: s for r in READS})
    state, macros, flags = run(tmp_path, res)
    assert state["on"] and flags["RpOn"] and flags["RpPrefix"]
    for r, w in MN.RP_READINGS:
        assert macros[f"Rp{w}Words"] == RA.WORDING[r][s]
        assert macros[f"Rp{w}Key"] == MN.RP_KEY_WORDS[s]
    assert flags["RpRaZero"] == flags["RpRcZero"] == (s == "includes_zero")
    assert macros["RpN"] == "40" and macros["RpPlans"] == "1,000" and macros["RpFresh"] == "999"
    assert macros["RpPaired"] == "eight" and macros["RpSwitchSe"] == "two"
    ctl = json.loads((ROOT / MN.RP_CONTROL).read_text())
    assert macros["RpCtlReplan"] == str(ctl["pooled"]["replan_pass"])
    assert macros["RpVOneN"] == "25" and macros["RpVTwoN"] == "100"
    assert all(macros[n] != "" for n in MN._rp_names()
               if n != "RpFragileList" and not n.endswith(("FreshExcessCI", "FreshShortCI")))


def test_on_refuses_a_wording_that_is_not_replan_axis(tmp_path):
    res = force(synthetic(n=40), {r: "above" for r in READS})
    res["readings"]["R-b"]["wording"] = "replanning lowers the excess"
    with pytest.raises(SystemExit):
        run(tmp_path, res)
    res = force(synthetic(n=40), {r: "above" for r in READS})
    res["readings"]["R-a"]["lo"] = -0.01
    with pytest.raises(SystemExit):
        run(tmp_path, res)


# --------------------------------------------------------------------------------------------------------------
# Conditional text expansion across all combinations of the four readings
# --------------------------------------------------------------------------------------------------------------
def tex_defs() -> dict:
    text = (ROOT / "paper" / "sections" / "switched.tex").read_text()
    text = re.sub(r"(?<!\\)%.*", "", text)
    out = {}
    for m in re.finditer(r"\\newcommand\{\\([A-Za-z]+)\}\{", text):
        i, depth = m.end(), 1
        while depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        out[m.group(1)] = text[m.end():i - 1]
    return out


TOK = re.compile(r"\\if([A-Za-z]+)|\\else(?![A-Za-z])|\\fi(?![A-Za-z])|\\([A-Za-z]+)(?:\{\})?|~|[^\\~]+|\\.")


def expand_text(name: str, defs: dict, values: dict, flags: dict) -> str:
    """Resolve TeX conditionals by recursive parse, then substitute macro expansions."""
    body = defs[name]
    body = re.sub(r"\\(?:paragraph|subsection)\{([^{}]*)\}", "\u00a7" + r"\1 ", body)
    body = re.sub(r"\\label\{[^{}]*\}", "", body)
    body = re.sub(r"\\ref\{[^{}]*\}", "N", body)
    body = re.sub(r"\\ci\{(\\[A-Za-z]+)\}", r"\1", body)
    toks = [m.group(0) for m in TOK.finditer(body)]

    def parse(i, until_else=False):
        out = []
        while i < len(toks):
            s = toks[i]
            m = re.fullmatch(r"\\if([A-Za-z]+)", s)
            if m:
                yes, i = parse(i + 1, True)
                no = []
                if toks[i].startswith("\\else"):
                    no, i = parse(i + 1, True)
                assert toks[i].startswith("\\fi")
                out.append((m.group(1), yes, no))
                i += 1
                continue
            if until_else and (s.startswith("\\else") or s.startswith("\\fi")):
                return out, i
            out.append(s)
            i += 1
        return out, i

    def render(tree) -> str:
        out = []
        for x in tree:
            if isinstance(x, tuple):
                out.append(render(x[1] if flags[x[0]] else x[2]))
                continue
            mm = re.fullmatch(r"\\([A-Za-z]+)(?:\{\})?", x)
            if mm:
                n = mm.group(1)
                out.append(expand_text(n, defs, values, flags) if n in defs else values[n])
            else:
                out.append(" " if x == "~" else x)
        return "".join(out)
    tree, _ = parse(0)
    return re.sub(r"\s+", " ", render(tree).replace("\u00a7", "")).strip()


NUMS = {"RpFCtlReplan": "72", "RpFCtlOpen": "63", "RpKeptEmuMin": "8.2", "RpKeptEmuMax": "15.0", "RpKeptOf": "23",
        "RpKeptPerfMin": "21.3", "RpKeptPerfMax": "22.3", "RpFragileList": "the excess", "OracleSeeds": "32",
        "Horizon": "24", "RpN": "40", "RpFresh": "999", "RpPaired": "eight", "RpSwitchSe": "two", "RpCtlReplan": "70",
        "RpCtlN": "100", "RpCtlOpen": "49", "RpFamAboveList": "\\emph{power} and \\emph{treasury}",
        "RpFamTop": "\\emph{power}", "RpFamTopEmuReplan": "4", "RpFamTopN": "20", "RpFamTopEmuOpen": "16",
        "RpFamTopPerfReplan": "20", "RpFamTopPerfOpen": "20"}
FAMFLAGS = {"RpFamAnyAbove": True, "RpFamAbovePlural": True, "RpFamOthersZero": True, "RpFamDiffer": False,
            "RpFamSomeNot": True}
for _w, _v in (("Ra", "+0.050"), ("Rb", "\u22120.020"), ("Rc", "+0.110"), ("Rd", "+0.010")):
    NUMS.update({f"Rp{_w}Est": _v, f"Rp{_w}CI": "[\u22120.040, +0.060]", f"Rp{_w}Width": "0.100",
                 f"Rp{_w}FreshEst": _v, f"Rp{_w}FreshCI": "[\u22120.030, +0.070]"})


def words(s: str) -> int:
    return sum(1 for w in s.split() if re.search(r"[A-Za-z0-9]", w))


def test_every_combination_of_the_four_readings_reads_with_its_wording():
    defs = tex_defs()
    counts = []
    for combo in itertools.product(STATES, repeat=4):
        for prefix in (False, True):
            st = dict(zip(READS, combo))
            values = dict(NUMS)
            values.update({f"Rp{w}Words": RA.WORDING[r][st[r]] for r, w in MN.RP_READINGS})
            flags = {"RpOn": True, "RpPrefix": prefix, "RpFreshCtl": False, "RpRaZero": st["R-a"] == "includes_zero",
                     "RpRcZero": st["R-c"] == "includes_zero", "RpFreshOn": True, "RpAnyFragile": False,
                     "RpFragilePlural": False, "RpKeptEmuOn": True, **FAMFLAGS}
            txt = expand_text("ReplanParagraph", defs, values, flags)
            assert txt.startswith("Monthly Closed-Loop Replanning Does observing the true city state")
            for r in READS:
                assert RA.WORDING[r][st[r]] in txt
            assert txt.count("not evidence of absence") == (st["R-a"] == "includes_zero") + (st["R-c"] == "includes_zero")
            assert ("On the first 40 of 100 instances in fixed benchmark order (balanced" in txt) == prefix
            assert ("On 40 benchmark instances (balanced" in txt) == (not prefix)
            assert "\\" not in txt.replace("\\emph", "") and "  " not in txt and " ," not in txt
            assert "keep their categories. Across task families" in txt and txt.endswith("passes 20 and 20.")
            assert "unadjusted" in txt and "shrinking-horizon" in txt and "on the realised engine trajectory" in txt
            assert txt.count("width 0.100") == 4 and "all readings keep their categories" in txt
            counts.append(words(txt) - words("Monthly Closed-Loop Replanning"))
    assert len(counts) == 162


def test_off_prints_nothing_and_the_limits_sentence_stays():
    defs = tex_defs()
    off = {"RpOn": False, "RpPrefix": False, "RpRaZero": False, "RpRcZero": False}
    assert expand_text("ReplanParagraph", defs, {}, off) == ""
    assert expand_text("RpLimitsText", defs, {}, off) == "we do not evaluate receding-horizon planning"
    on = dict(off, RpOn=True)
    assert expand_text("RpLimitsText", defs, {"RpN": "100", "RpLimitsOutcome": "the excess and the shortfall survived"},
                       on) == ("we evaluated one hysteresis-gated shrinking-horizon replanner on 100 instances "
                               "(Section N), under which the excess and the shortfall survived")
    assert expand_text("RpOpenLoopLead", defs, {}, off) == "all planners commit open loop"
    assert expand_text("RpOpenLoopLead", defs, {}, on) == "all planners outside Section N commit open loop"
    rel = (ROOT / "paper" / "sections" / "related.tex").read_text()
    assert "and \\RpLimitsText," in rel


def on_dir(tmp: Path, primary: dict, fresh: dict | None, kept=True, fresh_ctl=True) -> Path:
    """Override directory containing replan.json (primary) and replan_fresh/{replan.json, replan_control.json}."""
    res = force(synthetic(n=40), primary)
    if kept:
        for f in FAMS:
            res["by_family"][f]["emulator"][MN.RP_KEPT_FIELD] = 10.0 + FAMS.index(f)
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "replan.json").write_text(json.dumps(res))
    if fresh is not None:
        fd = tmp / "replan_fresh"
        fd.mkdir()
        fr = force(synthetic(n=40, seed=1, engine_stream="fresh1"), fresh)
        (fd / "replan.json").write_text(json.dumps(fr))
        if fresh_ctl:
            ctl = json.loads((ROOT / MN.RP_CONTROL).read_text())
            (fd / "replan_control.json").write_text(json.dumps(ctl))
    return tmp


def on_run(d: Path):
    reset()
    state = MN.replanning(override=str(d))
    return state, {m[0]: m[1] for m in MN.MACROS}, {i[0]: i[1] for i in MN.IFS}


def test_fresh_absent(tmp_path):
    state, macros, flags = on_run(on_dir(tmp_path, {r: "above" for r in READS}, None))
    assert state["on"] and not flags["RpFreshOn"] and not flags["RpAnyFragile"] and not flags["RpFreshCtl"]
    assert macros["RpRaFreshEst"] == "---" and macros["RpFCtlReplan"] == "---" and macros["RpFragileList"] == ""
    defs = tex_defs()
    txt = expand_text("RpFreshText", defs, macros, flags)
    assert txt == "An independent exact-simulator rerun on fresh proposal and evaluation seeds was not available."


def test_fresh_same_category_is_not_fragile(tmp_path):
    st = {"R-a": "above", "R-b": "includes_zero", "R-c": "below", "R-d": "includes_zero"}
    state, macros, flags = on_run(on_dir(tmp_path, st, st))
    assert flags["RpFreshOn"] and flags["RpFreshCtl"] and not flags["RpAnyFragile"]
    assert not any(flags[f"Rp{w}Fragile"] for _, w in MN.RP_READINGS)
    txt = expand_text("RpFreshText", tex_defs(), macros, flags)
    assert txt.startswith("Paired against an independent exact-simulator control run on fresh proposal and evaluation "
                          "seeds, the four quantities read ")
    assert txt.endswith("all readings keep their categories.")


@pytest.mark.parametrize("which", [("R-a",), ("R-a", "R-c")])
def test_a_fragile_reading_is_named(tmp_path, which):
    st = {r: "includes_zero" for r in READS}
    fr = dict(st, **{r: "above" for r in which})
    state, macros, flags = on_run(on_dir(tmp_path, st, fr))
    for r, w in MN.RP_READINGS:
        assert flags[f"Rp{w}Fragile"] == (r in which)
    assert flags["RpAnyFragile"] and flags["RpFragilePlural"] == (len(which) > 1)
    txt = expand_text("RpFreshText", tex_defs(), macros, flags)
    want = "the excess is seed-sensitive, its interval category differing" if len(which) == 1 else \
        "the excess and the shortfall are seed-sensitive, their categories differing".replace(
            "their categories", "their interval categories")
    assert want in txt and txt.endswith("between the two references.") and "R-" not in txt
    assert macros["RpFragileList"] == " and ".join(MN.RP_READING_NAMES[r] for r in which)


def test_months_kept_and_the_majority_column(tmp_path):
    state, macros, flags = on_run(on_dir(tmp_path, {r: "above" for r in READS}, None))
    assert flags["RpKeptEmuOn"] and macros["RpKeptEmuGrow"] == "10.0" and macros["RpKeptEmuMax"] == "14.0"
    ctl = json.loads((ROOT / MN.RP_CONTROL).read_text())
    assert macros["RpKeptPerfGrow"] == f"{ctl['incumbent_kept_months_mean']['grow']:.1f}"
    for m in ("Emu", "Perf"):
        assert re.fullmatch(r"\d\.\d{3}", macros[f"Rp{m}OpenOrcOrAcc"]) and re.fullmatch(r"\d\.\d{3}", macros[f"Rp{m}OpenOrcHack"])
    state, macros, flags = on_run(on_dir(tmp_path / "b", {r: "above" for r in READS}, None, kept=False))
    assert not flags["RpKeptEmuOn"] and macros["RpKeptEmuGrow"] == "---"
    vals = dict(NUMS, **{f"Rp{w}Words": RA.WORDING[r]["above"] for r, w in MN.RP_READINGS})
    para = expand_text("ReplanParagraph", tex_defs(), vals, flags)
    assert "alongside incumbent retention horizons" not in para
    assert "alongside incumbent retention horizons" in expand_text(
        "ReplanParagraph", tex_defs(), vals, dict(flags, RpKeptEmuOn=True))


def test_a_fresh_file_of_the_same_stream_is_refused(tmp_path):
    d = on_dir(tmp_path, {r: "above" for r in READS}, {r: "above" for r in READS})
    fr = json.loads((d / "replan_fresh" / "replan.json").read_text())
    fr["seed_stream"]["engine"] = None
    (d / "replan_fresh" / "replan.json").write_text(json.dumps(fr))
    with pytest.raises(SystemExit):
        on_run(d)


def test_paragraph_word_range_over_the_new_branches():
    defs = tex_defs()
    counts = []
    for combo in itertools.product(STATES, repeat=4):
        st = dict(zip(READS, combo))
        for prefix, fresh, nfrag, kept in itertools.product((False, True), (False, True), (0, 1, 2), (False, True)):
            if not fresh and nfrag:
                continue
            values = dict(NUMS, RpFragileList={0: "", 1: "the change in the excess",
                                               2: "the change in the excess and the change in the shortfall"}[nfrag])
            values.update({f"Rp{w}Words": RA.WORDING[r][st[r]] for r, w in MN.RP_READINGS})
            flags = {"RpOn": True, "RpPrefix": prefix, "RpFreshCtl": fresh, "RpRaZero": st["R-a"] == "includes_zero",
                     "RpRcZero": st["R-c"] == "includes_zero", "RpFreshOn": fresh, "RpAnyFragile": nfrag > 0,
                     "RpFragilePlural": nfrag > 1, "RpKeptEmuOn": kept, **FAMFLAGS}
            txt = expand_text("ReplanParagraph", defs, values, flags)
            assert "\\" not in txt.replace("\\emph", "") and "  " not in txt and " ." not in txt
            counts.append(words(txt) - words("Monthly Closed-Loop Replanning"))
    assert max(counts) <= 365


def test_budget_clause_branches():
    defs = tex_defs()
    vals = {"ReplRandRiseAll": "+0.016", "ReplRandRiseAllCI": "[−0.019, +0.050]", "Bp": "10^"}
    none = expand_text("ReplBudgetClause", defs, vals, {"ReplRandRiseUp": False, "ReplRandRiseDown": False})
    up = expand_text("ReplBudgetClause", defs, vals, {"ReplRandRiseUp": True, "ReplRandRiseDown": False})
    down = expand_text("ReplBudgetClause", defs, vals, {"ReplRandRiseUp": False, "ReplRandRiseDown": True})
    assert none == "no increase with random-shooting budget is established ("
    assert up.startswith("it rises with random-shooting budget (by +0.016") and up.endswith(";")
    assert down.startswith("it falls with random-shooting budget (by +0.016") and down.endswith(";")


@pytest.mark.parametrize("oi", ["missing", "hole", "shifted"])
def test_off_unless_the_instances_are_a_prefix(tmp_path, oi):
    res = force(synthetic(n=40), {r: "above" for r in READS})
    if oi == "missing":
        res.pop("order_index")
    elif oi == "hole":
        res["order_index"] = list(range(39)) + [41]
    else:
        res["order_index"] = list(range(1, 41))
    state, macros, flags = run(tmp_path, res)
    assert not state["on"] and "order_index" in state["why"]
    assert all(v == "" for v in macros.values()) and not any(flags.values())


def test_on_with_the_prefix_written(tmp_path):
    res = force(synthetic(n=40), {r: "above" for r in READS})
    assert res["order_index"] == list(range(40))
    state, macros, flags = run(tmp_path, res)
    assert state["on"]


@pytest.mark.parametrize("bad", ["hole", "fewer"])
def test_a_fresh_file_off_the_primary_instances_is_not_complete(tmp_path, bad):
    st = {r: "includes_zero" for r in READS}
    d = on_dir(tmp_path, st, dict(st, **{"R-a": "above"}))
    fr = json.loads((d / "replan_fresh" / "replan.json").read_text())
    if bad == "hole":
        fr["order_index"] = list(range(39)) + [40]
    else:
        fr["n_instances"] = 35
        fr["order_index"] = list(range(35))
    (d / "replan_fresh" / "replan.json").write_text(json.dumps(fr))
    state, macros, flags = on_run(d)
    assert state["on"] and not flags["RpFreshOn"] and not flags["RpAnyFragile"] and macros["RpFragileList"] == ""
    txt = expand_text("RpFreshText", tex_defs(), macros, flags)
    assert txt == "An independent exact-simulator rerun on fresh proposal and evaluation seeds was not available."


def test_the_readings_are_named_as_the_fragile_sentence_names_them():
    defs = tex_defs()
    for r, w in MN.RP_READINGS:
        assert defs[f"Rp{w}Paren"].startswith(MN.RP_READING_NAMES[r] + ", ")


def set_family(res, fam, excess, short):
    """Force one family's excess and shortfall under replanning to (value, lo, hi)."""
    for q, (v, lo, hi) in (("excess_false_acceptance", excess), ("shortfall_real_success", short)):
        e = res["by_family"][fam][q]["replan"]
        e.update(value=v, bca_lo=lo, bca_hi=hi, pct_lo=lo, pct_hi=hi)
    return res


ABOVE, ZERO, MIXED = (0.5, 0.2, 0.8), (0.0, -0.2, 0.2), (0.3, 0.1, 0.5)


def fam_run(tmp, primary_above, fresh_above=None, others=ZERO):
    st = {r: "above" for r in READS}
    d = on_dir(tmp, st, st if fresh_above is not None else None)
    for path, above in ((d / "replan.json", primary_above), (d / "replan_fresh" / "replan.json", fresh_above)):
        if above is None:
            continue
        res = json.loads(path.read_text())
        for i, f in enumerate(FAMS):
            if f in above:
                set_family(res, f, ABOVE, (0.5 + 0.1 * i, 0.3, 0.9))
            else:
                set_family(res, f, ZERO, (0.0, -0.2, 0.2) if others is ZERO else (0.2, 0.05, 0.4))
        path.write_text(json.dumps(res))
    return on_run(d)


def fam_text(macros, flags):
    return expand_text("RpFamText", tex_defs(), macros, flags)


def test_by_family_two_families_above(tmp_path):
    state, macros, flags = fam_run(tmp_path, ["treasury", "power"], ["treasury", "power"])
    assert flags["RpFamAnyAbove"] and flags["RpFamOthersZero"] and not flags["RpFamDiffer"]
    assert macros["RpFamAboveList"] == "\\emph{power} and \\emph{treasury}" and macros["RpFamTop"] == "\\emph{power}"
    txt = fam_text(macros, flags)
    assert txt.startswith("Across task families, paired against the run's exact-simulator control, both excess false "
                          "acceptance and real-success shortfall under replanning lie above zero on "
                          "\\emph{power} and \\emph{treasury} and include zero on the others; on \\emph{power} the "
                          "world-model replanner")
    res = json.loads((tmp_path / "replan.json").read_text())
    b = res["by_family"]["power"]
    n = b["n_instances"]
    assert macros["RpFamTopEmuReplan"] == str(round(b["emulator"]["replan"]["real_success"]["value"] * n))
    assert macros["RpFamTopPerfOpen"] == str(round(b["engine"]["open_loop"]["real_success"]["value"] * n))


def test_by_family_none_above(tmp_path):
    state, macros, flags = fam_run(tmp_path, [])
    assert not flags["RpFamAnyAbove"] and macros["RpFamAboveList"] == "none"
    assert fam_text(macros, flags).startswith("Across task families, paired against the run's exact-simulator control, "
                                              "on no single family do both excess and shortfall lie strictly above "
                                              "zero; on ")


def test_by_family_others_not_all_zero(tmp_path):
    state, macros, flags = fam_run(tmp_path, ["power"], others=MIXED)
    assert flags["RpFamAnyAbove"] and not flags["RpFamOthersZero"]
    assert "lie above zero on \\emph{power} and do not both lie above zero on the others;" in fam_text(macros, flags)


def test_by_family_the_references_disagree(tmp_path):
    state, macros, flags = fam_run(tmp_path, ["power"], ["power", "treasury"])
    assert flags["RpFamDiffer"] and macros["RpFamAboveList"] == "\\emph{power}"
    assert macros["RpFamFreshAboveList"] == "\\emph{power} and \\emph{treasury}"
    assert "above zero on \\emph{power} and include zero" in fam_text(macros, flags)
    tex = (ROOT / "paper" / "sections" / "app_results.tex").read_text()
    assert "\\ifRpFamDiffer" in tex and "Against the rerun on fresh seeds" in tex


def test_the_control_clause_names_both_runs_and_the_check_stops_the_build(tmp_path):
    st = {r: "above" for r in READS}
    state, macros, flags = on_run(on_dir(tmp_path / "a", st, st))
    assert flags["RpFreshCtl"]
    vals = dict(NUMS, **{f"Rp{w}Words": RA.WORDING[r]["above"] for r, w in MN.RP_READINGS},
                RpFCtlReplan="72", RpFCtlOpen="63")
    txt = expand_text("ReplanParagraph", tex_defs(), vals, dict(flags, **FAMFLAGS))
    assert "with no task family's interval lying wholly below zero in either run (Appendix Table N" in txt
    txt = expand_text("ReplanParagraph", tex_defs(), vals, dict(flags, RpFreshCtl=False, **FAMFLAGS))
    assert "without degrading any task family (Appendix Table N" in txt
    d = on_dir(tmp_path / "b", st, st)
    ctl = json.loads((d / "replan_fresh" / "replan_control.json").read_text())
    ctl["by_family"]["recover"]["hi"] = -0.01
    (d / "replan_fresh" / "replan_control.json").write_text(json.dumps(ctl))
    with pytest.raises(SystemExit):
        on_run(d)


@pytest.mark.parametrize("ka,kc,want", [
    ("above", "above", "the excess and the shortfall survived"),
    ("includes_zero", "includes_zero", "no excess and no shortfall were established"),
    ("above", "includes_zero", "the excess survived and no shortfall was established"),
    ("includes_zero", "below", "no excess was established and the shortfall lay below zero")])
def test_the_limits_outcome_is_built_from_the_categories(tmp_path, ka, kc, want):
    st = {"R-a": ka, "R-b": "above", "R-c": kc, "R-d": "above"}
    state, macros, flags = on_run(on_dir(tmp_path, st, st))
    assert macros["RpLimitsOutcome"] == want
    assert flags["RpBothAbove"] == (ka == kc == "above")
    sees = expand_text("RpSees", tex_defs(), macros, flags)
    assert sees == ("may encounter" if ka == kc == "above" else "encounters")
    assert expand_text("RpSees", tex_defs(), macros, dict(flags, RpOn=False)) == "encounters"


@pytest.mark.parametrize("fresh,want", [({}, True), ({"R-a": "includes_zero"}, False), ({"R-c": "includes_zero"}, False),
                                        ({"R-d": "includes_zero"}, True)])
def test_the_finding_and_what_to_do_clauses(tmp_path, fresh, want):
    st = {r: "above" for r in READS}
    state, macros, flags = on_run(on_dir(tmp_path, st, dict(st, **fresh)))
    assert flags["RpFindOn"] == want
    find = expand_text("RpFindClause", tex_defs(), macros, flags)
    what = expand_text("RpWhatClause", tex_defs(), macros, flags)
    if want:
        assert find == ("; both excess false acceptance and ground-truth shortfall also persist under monthly "
                        "closed-loop replanning from true simulator states (Section N)")
        assert what == ", and both effects persist even under monthly closed-loop replanning from true states"
    else:
        assert find == "" and what == ""
    intro = (ROOT / "paper" / "sections" / "intro.tex").read_text()
    assert (
        "Section~\\ref{sec:pressure})\\RpFindClause{}" in intro
        or "\\RpFindClause{} (Section" in intro
    ) and "\\RpWhatClause," in (ROOT / "paper" / "sections" / "related.tex").read_text()
