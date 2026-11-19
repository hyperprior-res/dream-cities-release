"""refs.bib (the verified bibliography, kept as exported from each source) -> refs_tex.bib for the
TeX build: non-ASCII characters become LaTeX accents, noisy export metadata (ISSN fields, redundant
URLs on entries that already carry a DOI, and raw OpenReview ID suffixes) is stripped, underscores
outside url, doi, eprint and howpublished \\url{} fields are escaped, and title words the style
would wrongly lower-case are brace-protected."""
import re
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1]
in_path = Path(sys.argv[1]) if len(sys.argv) > 1 else (P / "refs.bib")
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else (P / "refs_tex.bib")

# Map non-ASCII characters to clean LaTeX equivalents (avoiding raw banned symbols and em-dashes).
MAP = {
    "\u0161": r"{\v{s}}",
    "\u00fc": r'{\"u}',
    "\u00e4": r'{\"a}',
    "\u00f6": r'{\"o}',
    "\u2019": "'",
    "\u2018": "`",
    "\u2013": "--",
    "\u2014": "--",
    "\u00f3": r"{\'o}",
    "\u00e7": r"{\c{c}}",
    "\u00ed": r"{\'i}",
    "\u00e9": r"{\'e}",
    "\u00e1": r"{\'a}",
    "\u00f1": r"{\~n}",
    "\u00e8": r"{\`e}",
    "\u0142": r"{\l}",
    "\u201c": "``",
    "\u201d": "''",
    "\u00d7": r"$\times$",
    "\u00b1": r"$\pm$",
}


def strip_field_from_entry(entry: str, field: str) -> str:
    """Remove balanced-brace ``field = {...}`` (and trailing comma/whitespace) from a BibTeX entry."""
    pat = re.compile(r"(?:,\s*|\n[ \t]*)\b" + field + r"\s*=\s*\{", re.I)
    while True:
        m = pat.search(entry)
        if not m:
            break
        j, depth = m.end(), 1
        while j < len(entry) and depth:
            depth += {"{": 1, "}": -1}.get(entry[j], 0)
            j += 1
        prefix = entry[m.start():m.end()]
        if prefix.lstrip().startswith(","):
            # Inline field preceded by ', ': drop ', field = {...}' cleanly
            entry = entry[:m.start()] + entry[j:]
        else:
            # Line-leading field: also consume optional trailing comma and spaces on that line
            k = j
            while k < len(entry) and entry[k] in " \t":
                k += 1
            if k < len(entry) and entry[k] == ",":
                k += 1
            entry = entry[:m.start()] + entry[k:]
    return entry


def clean_entries(text: str) -> str:
    """Strip ISSN clutter, strip redundant URLs when DOI is present, canonicalise DOI prefixes,
    and drop trailing 'OpenReview id ...' suffixes in notes."""
    chunks = re.split(r"(?m)^(?=@)", text)
    cleaned = []
    doi_pat = re.compile(r"\bdoi\s*=\s*\{", re.I)
    for chunk in chunks:
        if not chunk.lstrip().startswith("@"):
            cleaned.append(chunk)
            continue
        chunk = strip_field_from_entry(chunk, "issn")
        if doi_pat.search(chunk):
            chunk = strip_field_from_entry(chunk, "url")
            chunk = re.sub(
                r"(\bdoi\s*=\s*\{)https?://(?:dx\.)?doi\.org/",
                r"\1",
                chunk,
                flags=re.I,
            )
        chunk = re.sub(r"\.\s*OpenReview id [A-Za-z0-9_\-]+", "", chunk)
        cleaned.append(chunk)
    return "".join(cleaned)


src = clean_entries(in_path.read_text(encoding="utf-8"))
out = []
for line in src.splitlines():
    for k, v in MAP.items():
        line = line.replace(k, v)
    bad = [ch for ch in line if ord(ch) > 127]
    if bad:
        raise SystemExit(f"bib_for_tex: unmapped characters {set(bad)} in: {line}")
    m = re.match(r"(\s*)([A-Za-z]+)(\s*=\s*)(.*)$", line)
    if m and m.group(2).lower() not in ("url", "doi", "eprint", "howpublished", "note"):
        line = m.group(1) + m.group(2) + m.group(3) + re.sub(r"(?<!\\)_", r"\\_", m.group(4))
    elif m and m.group(2).lower() in ("howpublished", "note"):
        parts = re.split(r"(\\url\{[^}]*\})", m.group(4))
        parts = [p if p.startswith("\\url{") else re.sub(r"(?<!\\)_", r"\\_", p) for p in parts]
        line = m.group(1) + m.group(2) + m.group(3) + "".join(parts)
    out.append(line)
text = "\n".join(out) + "\n"


def escape_field(text, field):
    """Escape underscores inside every balanced-brace value of ``field`` (one-line exports included)."""
    res, i = [], 0
    pat = re.compile(r"\b" + field + r"\s*=\s*\{", re.I)
    while True:
        m = pat.search(text, i)
        if not m:
            res.append(text[i:])
            break
        j, depth = m.end(), 1
        while depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        res.append(text[i:m.end()])
        res.append(re.sub(r"(?<!\\)_", r"\\_", text[m.end():j - 1]))
        res.append("}")
        i = j
    return "".join(res)


# Title capitals the style would lower-case (R6 m20): a word with a capital after its first letter (SimCity, TD-MPC2,
# MOReL, RL, StarCraft, II) or a proper name below is wrapped in braces, at brace depth 0 of the title only.
PROPER = {"Conway's", "Atari", "Gemini", "Veo", "Goodhart's", "Micropolis", "DeepMind", "Ctrl-World", "SimCity"}


def capital(w):
    """A word the style must not lower-case: a listed name, or a hyphen part with a capital after its first letter
    (TD-MPC2, MOReL, RL, StarCraft) or a one-letter capital part (U-Net)."""
    parts = w.split("-")
    return (
        w in PROPER
        or any(any(ch.isupper() for ch in q[1:]) for q in parts)
        or (len(parts) > 1 and any(len(q) == 1 and q.isupper() for q in parts))
    )


def protect_titles(text):
    res, i = [], 0
    pat = re.compile(r"\btitle\s*=\s*\{", re.I)
    tok = re.compile(r"[A-Za-z][A-Za-z0-9+'\-]*")
    while True:
        m = pat.search(text, i)
        if not m:
            res.append(text[i:])
            break
        j, depth, out = m.end(), 1, []
        e, d = j, 1
        while d:
            d += {"{": 1, "}": -1}.get(text[e], 0)
            e += 1
        body = text[j:e - 1]
        shout = body.upper() == body          # an all-capitals export is left for the style to set
        while depth:
            c = text[j]
            if c in "{}" or depth > 1 or text[j - 1] == "\\":
                depth += {"{": 1, "}": -1}.get(c, 0)
                out.append(c if depth else "")
                j += 1
                continue
            t = tok.match(text, j)
            if t and not text[j - 1].isalnum():
                w = t.group(0)
                out.append("{" + w + "}" if capital(w) and not shout else w)
                j = t.end()
                continue
            out.append(c)
            j += 1
        res.append(text[i:m.end()])
        res.append("".join(out))
        res.append("}")
        i = j
    return "".join(res)


text = text.replace("Gemini Robotics Team and", "{Gemini Robotics Team} and")
text = protect_titles(text)
for f in ("title", "journal", "booktitle"):
    text = escape_field(text, f)
out_path.write_text(text, encoding="utf-8")
print(f"{out_path.name} written")
