# SPDX-License-Identifier: MIT
"""docs/data/site.json: what every tab shares (name, revision, repository, the tab list)."""
from __future__ import annotations

import json

from . import REPO

GITHUB = "konstantindenerz/k0d3ball35"
# id, title in the tab bar; the order is the order of the sheets in the title block
TABS = (("overview", "Overview"), ("explorer", "Explorer"), ("case", "Case"), ("trackball", "Trackball"),
        ("pcbs", "PCBs"), ("keymap", "Keymap"), ("build", "Build & BOM"))


def build() -> dict:
    right = json.loads((REPO / "hardware/layout/output/points-right.json").read_text())
    return {
        "name": right["name"],
        "revision": right["revision"],
        "github": GITHUB,
        "ref": "main",
        "tabs": [{"id": i, "title": t} for i, t in TABS],
    }
