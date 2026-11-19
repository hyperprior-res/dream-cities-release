"""The README's quick start runs as written and produces a card."""

from __future__ import annotations

import json
import re
from pathlib import Path


def test_readme_quick_start_runs(tmp_path, monkeypatch):
    text = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    section = text.split("## Quick start", 1)[1]
    code = re.search(r"```python\n(.*?)```", section, re.S).group(1)
    monkeypatch.chdir(tmp_path)
    exec(compile(code, "README quick start", "exec"), {"__name__": "readme"})
    card = json.loads((tmp_path / "card.json").read_text())
    assert [e["budget"] for e in card["hackability_curve"]] == [1, 10, 100, 1000]
    assert card["counts"]["instances"] == 12 and card["counts"]["clusters"] == 4
    assert card["counts"]["grader_plan_evaluations"]["attack_search"] == 12 * (1 + 10 + 100 + 1000)
    fl = card["noise_floors"][-1]
    assert fl["matched_floor"] == "residual_surrogate" and "excess" in fl["residual_surrogate"]
    assert card["hackability_curve"][-1]["hackability"]["bca_lo"] is not None or \
        card["hackability_curve"][-1]["hackability"]["method"].startswith("no hacked unit")
