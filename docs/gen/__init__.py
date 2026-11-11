# SPDX-License-Identifier: MIT
"""Data generators for the published page. Each module exposes `build() -> dict | None`; the
result is written to docs/data/<module>.json by docs/build.py (None writes nothing yet)."""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

CASE_PARAMS = "hardware/case/params.scad"


def case_param(name: str) -> float:
    """A literal from the case parameters (cap_top_z is not echoed into stack.json)."""
    return float(re.search(rf"^{name}\s*=\s*(-?[\d.]+);", (REPO / CASE_PARAMS).read_text(), flags=re.M)[1])
