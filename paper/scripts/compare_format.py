"""Format gate (brief section 8 "Check it" and section 11 gate 4) for this paper.

1. Renders page 1 of the reference and of main.pdf at 150 dpi and writes them side by side, with the
   reference's contact line and arXiv margin identifier painted out (the same two regions the group's
   template script redacts; pymupdf is not installed here, so pdftoppm and PIL do the work).
2. Measures both first pages the way the template was measured: page size (pdfinfo), fonts (pdffonts),
   and the ink positions of the title, the date, the byline and the abstract (pdftotext -bbox-layout).
3. Runs the template's check_pdf.py on main.pdf (embedded fonts, no Type 3, no ??, overfull boxes).
Outputs under paper/review/format/. No text of the reference is retained.
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[1]
REF = Path("<repo>/ext/reference/2602.11865.pdf")
OUT = P / "review" / "format"
DPI = 150


def render(pdf, page=1):
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(page), "-l", str(page), "-png", str(pdf), f"{d}/p"], check=True)
        f = sorted(Path(d).glob("p*.png"))[0]
        return Image.open(f).convert("RGB")


def words(pdf):
    xml = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    lines = re.findall(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>', xml, re.S)
    out = []
    for x0, y0, x1, y1, body in lines:
        n = len(re.findall(r"<word ", body))
        out.append({"x0": float(x0), "y0": float(y0), "x1": float(x1), "y1": float(y1), "words": n})
    return out


def info(pdf):
    t = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    size = re.search(r"Page size:\s+(.*)", t).group(1)
    fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    names = sorted({re.sub(r"^[A-Z]{6}\+", "", l.split()[0]) for l in fonts if l.strip()})
    t3 = [l.split()[0] for l in fonts if "Type 3" in l]
    unemb = [l.split()[0] for l in fonts if len(l.split()) > 5 and l.split()[-5] != "yes"]
    return {"page_size": size, "fonts": names, "type3": t3, "unembedded": unemb}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ref, paper = render(REF), render(P / "main.pdf")
    s = DPI / 72.0
    d = ImageDraw.Draw(ref)
    d.rectangle([0, 200 * s, 42 * s, 700 * s], fill="white")          # arXiv margin identifier
    d.rectangle([55 * s, 776 * s, 400 * s, 807 * s], fill="white")    # contact line
    gap, banner = 32, 45
    out = Image.new("RGB", (ref.width + paper.width + gap, max(ref.height, paper.height) + banner), "#e7e7e7")
    dd = ImageDraw.Draw(out)
    dd.text((16, 16), "REFERENCE / contact details and margin identifier omitted", fill="#242424")
    dd.text((ref.width + gap + 16, 16), "HYPERPRIOR / Dream cities, first page at the same scale", fill="#242424")
    out.paste(ref, (0, banner)); out.paste(paper, (ref.width + gap, banner))
    out.save(OUT / "page1-comparison.png", dpi=(DPI, DPI))
    # measurements: first-page ink of the top lines
    def top(lines, n=8):
        return [{k: round(v, 1) if isinstance(v, float) else v for k, v in l.items()} for l in sorted(lines, key=lambda l: l["y0"])[:n]]
    rw, pw = words(REF), words(P / "main.pdf")
    rep = {"reference": {**info(REF), "text_left_edge_pt": round(min(l["x0"] for l in rw if l["y0"] > 80), 1),
                         "first_lines": top(rw)},
           "paper": {**info(P / "main.pdf"), "text_left_edge_pt": round(min(l["x0"] for l in pw if l["y0"] > 80), 1),
                     "first_lines": top(pw)},
           "image": "page1-comparison.png", "dpi": DPI}
    (OUT / "format-check.json").write_text(json.dumps(rep, indent=1) + "\n")
    chk = subprocess.run(["python3", "<repo>/template/scripts/check_pdf.py", str(P / "main.pdf"),
                          "--output", str(OUT / "main-pdf-check.json")], capture_output=True, text=True)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "first_lines"} for k, v in rep.items() if isinstance(v, dict)}, indent=1))
    print("check_pdf passed:", chk.returncode == 0)
    if chk.returncode:
        print(chk.stdout[-3000:])


if __name__ == "__main__":
    main()
