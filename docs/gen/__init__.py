# SPDX-License-Identifier: MIT
"""Data generators for the published page. Each module exposes `build() -> dict | None`; the
result is written to docs/data/<module>.json by docs/build.py (None writes nothing yet)."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
