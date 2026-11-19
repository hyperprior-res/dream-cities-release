"""Figures whose data do not exist yet: each writes a labelled stub that says in the PDF what it waits for.

A real drawing function is registered for a slot only once its input format is known and fixed (the
cross-emulator analysis and the coverage arm are being built by other builders); until then the stub is
written. Stubs never contain data.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpr_fig as F  # noqa: E402

SLOTS = [
    # (output, title, waits for, source file, width). Empty since draft 3: fig_coverage.pdf has its drawing function
    # (fig_coverage.py), and fig_across.py writes its own stub until main_claim.json is complete.
]


def main():
    for name, title, waits, source, width in SLOTS:
        F.stub(name, title, waits, source, width=width, height=1.75 if width == F.COLUMN_IN else 1.5)
    print(f"{len(SLOTS)} slot figures written")


if __name__ == "__main__":
    main()
