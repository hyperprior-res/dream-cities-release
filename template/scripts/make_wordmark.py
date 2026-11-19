"""Outline the house wordmark; retain no font or live text in the output."""
import argparse
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from reportlab.pdfgen import canvas


class OutlineCanvas(canvas.Canvas):
    def _make_preamble(self):
        self._preamble = '1 0 0 1 0 0 cm'


class PdfPen(BasePen):
    def __init__(self, glyphs, path):
        super().__init__(glyphs)
        self.path = path

    def _moveTo(self, p):
        self.path.moveTo(*p)

    def _lineTo(self, p):
        self.path.lineTo(*p)

    def _curveToOne(self, p1, p2, p3):
        self.path.curveTo(*p1, *p2, *p3)

    def _qCurveToOne(self, p1, p2):
        p0 = self._getCurrentPoint()
        q1 = tuple(p0[i] + 2 * (p1[i] - p0[i]) / 3 for i in (0, 1))
        q2 = tuple(p2[i] + 2 * (p1[i] - p2[i]) / 3 for i in (0, 1))
        self.path.curveTo(*q1, *q2, *p2)

    def _closePath(self):
        self.path.close()

    def _endPath(self):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    font = TTFont(args.font)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    tracking = -0.055 * font['head'].unitsPerEm
    positions = []
    x = 0
    bounds = BoundsPen(glyphs)
    for char in 'HYPERPRIOR':
        name = cmap[ord(char)]
        positions.append((name, x))
        glyphs[name].draw(TransformPen(bounds, (1, 0, 0, 1, x, 0)))
        x += glyphs[name].width + tracking
    xmin, ymin, xmax, ymax = bounds.bounds
    height = 18 * 72 / 72.27
    scale = height / (ymax - ymin)
    width = (xmax - xmin) * scale
    paths = []
    for name, x in positions:
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, (x-xmin)*scale, ymax*scale)))
        paths.append(pen.getCommands())
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="%.6fpt" height="%.6fpt" viewBox="0 0 %.6f %.6f"><title>HyperPrior</title><g fill="#8E1B1E">%s</g></svg>\n' % (width, height, width, height, ''.join('<path d="' + d + '"/>' for d in paths))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'wordmark.svg').write_text(svg)
    pdf = OutlineCanvas(str(args.output / 'wordmark.pdf'), pagesize=(width, height), pageCompression=1, invariant=1)
    pdf.setTitle('HyperPrior wordmark')
    pdf.setAuthor('HyperPrior Research')
    pdf.setCreator('HyperPrior outline generator')
    pdf.setFillColorRGB(142/255, 27/255, 30/255)
    path = pdf.beginPath()
    for name, x in positions:
        pen = PdfPen(glyphs, path)
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, scale, (x-xmin)*scale, -ymin*scale)))
    pdf.drawPath(path, fill=1, stroke=0)
    pdf.showPage()
    pdf.save()
    (args.output / 'wordmark-provenance.json').write_text(json.dumps({
        'source': 'www repository, origin/main, fonts/austin-regular.woff2',
        'font_sha256': hashlib.sha256(args.font.read_bytes()).hexdigest(),
        'text': 'HYPERPRIOR', 'tracking_em': -0.055, 'colour': '#8E1B1E',
        'width_pdf_pt': width, 'height_pdf_pt': height,
        'font_embedded': False, 'output': 'outlined paths only'
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
