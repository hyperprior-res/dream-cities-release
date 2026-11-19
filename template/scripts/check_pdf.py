"""Reject unembedded/bitmap fonts and unresolved cross-references."""
import argparse
from pathlib import Path
import subprocess
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    fonts = subprocess.check_output(['pdffonts', str(args.pdf)], text=True)
    text = subprocess.check_output(['pdftotext', str(args.pdf), '-'], text=True)
    info = subprocess.check_output(['pdfinfo', str(args.pdf)], text=True)
    issues = []
    for line in fonts.splitlines()[2:]:
        fields = line.split()
        if 'Type 3' in line:
            issues.append('Bitmap Type 3 font: ' + fields[0])
        if len(fields) > 5 and fields[-5] != 'yes':
            issues.append('Unembedded font: ' + fields[0])
    if '??' in text:
        issues.append('Unresolved cross-reference')
    log = args.pdf.with_suffix('.log')
    if log.is_file():
        for line in log.read_text(errors='replace').splitlines():
            if 'Overfull' in line or 'undefined' in line.lower() and 'warning' in line.lower():
                issues.append(line)
    report = {'pdf': args.pdf.name, 'passed': not issues, 'issues': issues, 'font_report': fonts, 'pdf_info': info}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(issues))


if __name__ == '__main__':
    main()
