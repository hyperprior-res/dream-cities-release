"""Gate 2 (numbers): every digit in the paper's prose must come from a macro of numbers.tex,
and every point estimate paired with a confidence interval must satisfy lo - 1e-3 <= est <= hi + 1e-3.

Scans main.tex and sections/*.tex for hand-typed digits (generated tables are written by make_numbers.py
and are exempt from the raw-digit scan), strips comments, cross-reference and citation arguments, file
names and environment names, and reports any remaining digit. Checks that every capitalised macro the text
uses is defined in numbers.tex, main.tex or sections/switched.tex.

Also enforces two automated interval-consistency gates:
  (a) In numbers.tex / numbers_manifest.json, every numeric macro <Name> with a companion <Name>CI macro
      [lo, hi] (including multiplicity-adjusted <Name>CorrCI companions) satisfies lo - 1e-3 <= est <= hi + 1e-3.
  (b) Across paper/main.tex, paper/sections/*.tex, and paper/tables/*.tex, every point-estimate macro
      immediately paired with a CI macro on the same cell/clause, adjacent table column, or stacked
      continuation row (as well as literal est [lo, hi] cells in generated tables) satisfies
      lo - 1e-3 <= est <= hi + 1e-3.
Exit status 1 if anything is found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1]
FILES = [P / "main.tex"] + sorted((P / "sections").glob("*.tex"))
TABLE_FILES = sorted((P / "tables").glob("*.tex"))
TOL = 1e-3

WHITELIST = [
    r"TD-MPC2", r"GPL-3\.0", r"GPL-3", r"Apache-2\.0", r"CC BY 4\.0", r"Dreamer~?4", r"DreamerV3",
    r"PROWL-1", r"StarCraft~II", r"1989", r"SHA-256", r"\\Bp\{\d\}", r"10\^\{?\d\}?", r"\\\\\[\d+pt\]",
    r"\d+(\.\d+)?(pt|em|ex|mm|cm|in)\b", r"0\.\d+\\textwidth", r"\{\d+\}\{\d+\}", r"p\{0\.\d+",
    r"\$h\(\\mathcal", r"F1\b", r"\bF\d\b", r"\b[A-Z]\d+\b", r"\\slot\{[A-Z]\d+\}", r"bd6e12e",
    r"hpr-dream", r"WoVR\+", r"Agora-1", r"x\d+",
    r"\[1\]\{#1\}", r"\^2", r"\(1-\\alpha\)", r"2\\,tp", r"\\lambda=0",
    r"\\multicolumn\{\d+\}", r"\\cmidrule(\([a-z]*\))?\{\d+-\d+\}",
]
STRIP = [
    r"%.*",
    r"\\mbox\{-?\}",
    r"\\(label|ref|cite[tp]?|citep|citet|citealp|input|include|includegraphics|bibliography|wordmarkpath|hypersetup|begin|end|url|eqref)(\[[^\]]*\])?\{[^}]*\}",
    r"\\(setcounter|renewcommand|newcommand|setlength|usepackage)\{[^}]*\}(\{[^}]*\})*",
    r"\\documentclass\{[^}]*\}",
    r"\\[A-Za-z]+",
]

SAME_CLAUSE_PAIR_RE = re.compile(
    r"\\([A-Z][A-Za-z]*?)(?:\{\}|(?=\s))\s*(?:\(\s*(?:corrected\s+)?)?"
    r"(?:\\ci\{\\([A-Z][A-Za-z]*CI)(?:\{\})?\}"
    r"|\{\\(?:tiny|scriptsize|footnotesize)\s*\\([A-Z][A-Za-z]*CI)(?:\{\})?\s*\}"
    r"|\\([A-Z][A-Za-z]*CI)(?:\{\}|\b))"
)
SINGLE_EST_CELL_RE = re.compile(r"^\\([A-Z][A-Za-z]*)(?:\{\})?$")
SINGLE_CI_CELL_RE = re.compile(
    r"^(?:\\ci\{\\([A-Z][A-Za-z]*CI)(?:\{\})?\}"
    r"|\{\\(?:tiny|scriptsize|footnotesize)\s*\\([A-Z][A-Za-z]*CI)(?:\{\})?\s*\}"
    r"|\\([A-Z][A-Za-z]*CI)(?:\{\})?)(?:\s*\\if[A-Za-z]+.*)?$"
)
LITERAL_EST_CI_RE = re.compile(
    r"([+-]?\d+\.\d+)\s*(?:\{\\(?:scriptsize|tiny|footnotesize)\s*)?"
    r"\[\s*([+-]?\d+\.\d+)\s*,\s*([+-]?\d+\.\d+)\s*\]"
)


def parse_newcommands(text: str) -> dict[str, str]:
    """Extract \\newcommand{\\Name}{body} with balanced braces (handles \\mbox{-} etc.)."""
    out: dict[str, str] = {}
    for m in re.finditer(r"\\newcommand\{\\([A-Za-z]+)\}\{", text):
        i, depth = m.end(), 1
        while i < len(text) and depth > 0:
            if text[i] == "\\" and i + 1 < len(text):
                i += 2
                continue
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        if depth == 0:
            out[m.group(1)] = text[m.end():i - 1]
    return out


def norm_minus(s: str) -> str:
    """Normalise LaTeX / Unicode minus representations (including \\mbox{-}) to ASCII '-'."""
    s = s.replace(r"\mbox{-}", "-")
    s = re.sub(r"\\textminus(?:\{\}|\s+|$)", "-", s)
    s = s.replace("\u2212", "-")
    return s


def parse_est(raw: str) -> float | None:
    s = norm_minus(raw.strip())
    s = re.sub(r"(?<=\d),(?=\d)", "", s)
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", s):
        return float(s)
    return None


def parse_ci(raw: str) -> tuple[float, float] | None:
    s = raw.strip()
    m_wrap = re.fullmatch(r"\{\\(?:scriptsize|tiny|footnotesize)\s*(.*)\}", s)
    if m_wrap:
        s = m_wrap.group(1).strip()
    s = norm_minus(s)
    m = re.fullmatch(r"\[\s*([+-]?[\d,]+(?:\.\d+)?)\s*,\s*([+-]?[\d,]+(?:\.\d+)?)\s*\]", s)
    if not m:
        return None
    lo = float(re.sub(r"(?<=\d),(?=\d)", "", m.group(1)))
    hi = float(re.sub(r"(?<=\d),(?=\d)", "", m.group(2)))
    return lo, hi


def _verify_pair(where: str, est_label: str, est: float | None, ci_label: str,
                 bounds: tuple[float, float] | None, bad: list[str],
                 macros: dict[str, str] | None = None) -> None:
    if macros is not None and est_label.startswith("\\") and ci_label.startswith("\\"):
        en, cn_ = est_label[1:], ci_label[1:]
        if (en + "CI") in macros and not cn_.startswith(en):
            bad.append(f"{where}: mismatched CI macro {ci_label} paired with {est_label} (expected \\{en}CI)")
    if est is None or bounds is None:
        return
    lo, hi = bounds
    if lo > hi + 1e-9:
        bad.append(f"{where}: inverted interval {ci_label}=[{lo}, {hi}]")
    elif not (lo - TOL <= est <= hi + TOL):
        bad.append(f"{where}: point estimate {est_label}={est} outside {ci_label}=[{lo}, {hi}]")


def check_numbers_and_manifest_cis(macros: dict[str, str], manifest_path: Path, bad: list[str]) -> None:
    """Gate (a): every <Name> with companion <Name>CI in numbers.tex / numbers_manifest.json satisfies lo <= est <= hi."""
    if manifest_path.is_file():
        mf = json.loads(manifest_path.read_text())
        mf_macros = {entry["name"]: str(entry["value"]) for entry in mf.get("macros", [])}
        for k, v in mf_macros.items():
            if k in macros and macros[k] != v:
                bad.append(f"numbers_manifest.json: macro \\{k}={v!r} disagrees with numbers.tex {macros[k]!r}")
    for ci_name, ci_raw in macros.items():
        if not ci_name.endswith("CI"):
            continue
        bounds = parse_ci(ci_raw)
        if bounds is None:
            continue
        lo, hi = bounds
        if lo > hi + 1e-9:
            bad.append(f"numbers.tex: inverted interval \\{ci_name}=[{lo}, {hi}]")
            continue
        companions: list[str] = []
        base = ci_name[:-2]
        if base in macros:
            companions.append(base)
        elif ci_name.endswith("CorrCI") and ci_name[:-6] in macros:
            companions.append(ci_name[:-6])
        elif ci_name.endswith("LinCI") and ci_name[:-5] in macros:
            companions.append(ci_name[:-5])
        elif ci_name.endswith("FamCI") and ci_name[:-5] in macros:
            companions.append(ci_name[:-5])
        for est_name in companions:
            est = parse_est(macros[est_name])
            _verify_pair("numbers.tex", f"\\{est_name}", est, f"\\{ci_name}", bounds, bad)


def _strip_row_end(s: str) -> str:
    return re.sub(r"\\\\(?:\s*\[[^\]]*\])?\s*$", "", s).strip()


def check_tex_est_ci_pairs(tex_files: list[Path], macros: dict[str, str], bad: list[str]) -> None:
    """Gate (b): verify every point estimate + CI pairing across main.tex, sections/*.tex, and tables/*.tex."""
    for f in tex_files:
        rel_name = f.name if f.parent == P or f.parent.name == "sections" else f"{f.parent.name}/{f.name}"
        prev_row: tuple[int, list[str]] | None = None
        for n, raw_line in enumerate(f.read_text().splitlines(), 1):
            line = re.sub(r"(?<!\\)%.*", "", raw_line)
            where = f"{rel_name}:{n}"

            # B1: \Foo{} immediately followed on the same cell/clause by \ci{\BarCI} or \BarCI{}
            for m in SAME_CLAUSE_PAIR_RE.finditer(line):
                est_name = m.group(1)
                ci_name = m.group(2) or m.group(3) or m.group(4)
                if est_name.endswith("CI") or est_name not in macros or ci_name not in macros:
                    continue
                _verify_pair(where, f"\\{est_name}", parse_est(macros[est_name]),
                             f"\\{ci_name}", parse_ci(macros[ci_name]), bad, macros)

            # B4: literal point estimate + [lo, hi] in generated tables
            if f.parent.name == "tables":
                norm_line = norm_minus(line)
                for m in LITERAL_EST_CI_RE.finditer(norm_line):
                    est = float(m.group(1))
                    lo, hi = float(m.group(2)), float(m.group(3))
                    _verify_pair(where, m.group(1), est, f"[{m.group(2)}, {m.group(3)}]", (lo, hi), bad)

            # Table row tracking for B2 (adjacent cells) and B3 (two-row stacked CI continuation rows)
            stripped = line.strip()
            if any(tok in stripped for tok in (r"\toprule", r"\midrule", r"\bottomrule", r"\end{tabular")):
                prev_row = None
                continue
            if "&" not in stripped or r"\\" not in stripped:
                continue
            row_body = _strip_row_end(stripped)
            cells = [c.strip() for c in row_body.split("&")]

            # B2: adjacent cells & \Foo{} & \BarCI{}
            for j in range(len(cells) - 1):
                me = SINGLE_EST_CELL_RE.fullmatch(cells[j])
                mc = SINGLE_CI_CELL_RE.fullmatch(cells[j + 1])
                if me and mc:
                    est_name = me.group(1)
                    ci_name = mc.group(1) or mc.group(2) or mc.group(3)
                    if not est_name.endswith("CI") and est_name in macros and ci_name in macros:
                        _verify_pair(where, f"\\{est_name}", parse_est(macros[est_name]),
                                     f"\\{ci_name}", parse_ci(macros[ci_name]), bad, macros)

            # B3: stacked continuation row (empty col 0, CI-only cells in cols 1..k under est-only cells)
            if prev_row is not None:
                prev_n, prev_cells = prev_row
                if len(cells) == len(prev_cells) >= 2 and cells[0] == "" and prev_cells[0] != "":
                    is_ci_continuation = False
                    for j in range(1, len(cells)):
                        prev_all = [x for x in re.findall(r"\\([A-Z][A-Za-z]*)", prev_cells[j]) if x in macros]
                        curr_all = [x for x in re.findall(r"\\([A-Z][A-Za-z]*)", cells[j]) if x in macros]
                        est_prev = [x for x in prev_all if not x.endswith("CI")]
                        ci_prev = [x for x in prev_all if x.endswith("CI")]
                        est_curr = [x for x in curr_all if not x.endswith("CI")]
                        ci_curr = [x for x in curr_all if x.endswith("CI")]
                        if len(est_prev) == 1 and not ci_prev and not est_curr and len(ci_curr) == 1:
                            is_ci_continuation = True
                            _verify_pair(f"{rel_name}:{prev_n}-{n}(col {j + 1})",
                                         f"\\{est_prev[0]}", parse_est(macros[est_prev[0]]),
                                         f"\\{ci_curr[0]}", parse_ci(macros[ci_curr[0]]), bad, macros)
                    if is_ci_continuation:
                        prev_row = None
                        continue

            prev_row = (n, cells)


def main() -> None:
    bad: list[str] = []
    num_text = (P / "numbers.tex").read_text()
    macros = parse_newcommands(num_text)
    defined = set(macros)
    defined |= set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", (P / "main.tex").read_text()))
    defined |= set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", (P / "sections" / "switched.tex").read_text()))
    for f in FILES:
        text = f.read_text()
        if f.name == "main.tex":
            text = text.split("\\begin{abstract}", 1)[1]
        for n, line in enumerate(text.splitlines(), 1):
            for m in re.findall(r"\\([A-Z][A-Za-z]+)", line):
                if m not in defined and m not in ("Pr",):
                    bad.append(f"{f.name}:{n}: undefined macro \\{m}")
            s = line
            for w in WHITELIST:
                s = re.sub(w, " ", s)
            for st in STRIP:
                s = re.sub(st, " ", s)
            for d in re.finditer(r"\d[\d,.]*", s):
                bad.append(f"{f.name}:{n}: hand-typed number '{d.group(0)}' in: {line.strip()[:110]}")

    check_numbers_and_manifest_cis(macros, P / "numbers_manifest.json", bad)
    check_tex_est_ci_pairs(FILES + TABLE_FILES, macros, bad)

    for b in bad:
        print(b)
    print(f"check_numbers: {len(bad)} finding(s) in {len(FILES)} prose files + {len(TABLE_FILES)} generated tables")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
