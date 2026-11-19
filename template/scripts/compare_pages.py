"""Render first pages at the requested density, omitting reference contact details."""
import argparse
from pathlib import Path
import pymupdf as fitz
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--paper', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    reference = fitz.open(args.reference)
    page = reference[0]
    page.add_redact_annot(fitz.Rect(0, 200, 42, 700), fill=(1, 1, 1))
    page.add_redact_annot(fitz.Rect(55, 776, 400, 807), fill=(1, 1, 1))
    page.apply_redactions()
    images = []
    for document in [reference, fitz.open(args.paper)]:
        pixmap = document[0].get_pixmap(dpi=150, alpha=False)
        images.append(Image.frombytes('RGB', [pixmap.width, pixmap.height], pixmap.samples))
    gap, banner = 32, 45
    out = Image.new('RGB', (sum(im.width for im in images)+gap, max(im.height for im in images)+banner), '#e7e7e7')
    draw = ImageDraw.Draw(out)
    draw.text((16, 16), 'REFERENCE / contact details and margin identifier omitted', fill='#242424')
    draw.text((images[0].width+gap+16, 16), 'HYPERPRIOR / first page at the same scale', fill='#242424')
    out.paste(images[0], (0, banner))
    out.paste(images[1], (images[0].width+gap, banner))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.output, dpi=(150, 150))


if __name__ == '__main__':
    main()
