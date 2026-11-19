"""Every slot in the text (\\slot{ID}{...}) and every stub figure must be listed in TODO.md.

The text branches on switches that make_numbers.py writes into numbers.tex (\\newif\\if<Name> with its state):
a result that is still running prints its slot in the \\else branch and its prose in the other. This check reads
the switches, works out which branch prints, and reports the slots that print now separately from those that sit
in a branch that does not print (prepared: they print, or vanish, when their result file changes). Both kinds must
be in TODO.md.
"""
import json, re, sys
from pathlib import Path
P = Path(__file__).resolve().parents[1]
text = "\n".join(f.read_text() for f in [P / "main.tex"] + sorted((P / "sections").glob("*.tex")))
text = re.sub(r"(?<!\\)%.*", "", text)
flags = {m.group(1): m.group(2) == "true"
         for m in re.finditer(r"\\newif\\if([A-Za-z]+)\\\1(true|false)", (P / "numbers.tex").read_text())}
tok = re.compile(r"\\if(%s)(?![A-Za-z])|\\else(?![A-Za-z])|\\fi(?![A-Za-z])" % "|".join(map(re.escape, flags)) if flags
                 else r"(?!x)x")
live, stack, pos = [], [], 0
for m in tok.finditer(text):
    if all((flags[n] and not e) or (not flags[n] and e) for n, e in stack):
        live.append(text[pos:m.start()])
    t = m.group(0)
    if t.startswith("\\if"):
        stack.append([m.group(1), False])
    elif t == "\\else":
        if not stack:
            sys.exit("check_slots: \\else outside a known switch")
        stack[-1][1] = True
    else:
        if not stack:
            sys.exit("check_slots: \\fi outside a known switch")
        stack.pop()
    pos = m.end()
if stack:
    sys.exit(f"check_slots: unclosed switch {stack}")
live.append(text[pos:])
order = lambda s: (s[0], int(s[1:]))
ids = sorted(set(re.findall(r"\\slot\{([A-Z]\d+)\}", text)), key=order)
printing = sorted(set(re.findall(r"\\slot\{([A-Z]\d+)\}", "".join(live))), key=order)
prepared = [i for i in ids if i not in printing]
stubs = sorted(p.name.replace(".json", ".pdf") for p in (P / "figures").glob("*.json")
               if json.loads(p.read_text()).get("stub"))
if (P / "TODO.md").exists():
    todo = (P / "TODO.md").read_text()
    missing = [i for i in ids if f"| {i} |" not in todo] + [s for s in stubs if s not in todo]
else:
    missing = []
print(f"switches: {', '.join(f'{k}={str(v).lower()}' for k, v in flags.items()) or 'none'}")
print(f"slots that print: {len(printing)} ({', '.join(printing)}); in branches that do not print: "
      f"{len(prepared)} ({', '.join(prepared) or 'none'}); stub figures: {len(stubs)} ({', '.join(stubs) or 'none'})")
for m in missing:
    print("not in TODO.md:", m)
sys.exit(1 if (missing or (not (P / "TODO.md").exists() and (printing or stubs))) else 0)
