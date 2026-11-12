# SPDX-License-Identifier: MIT
"""The FFC from the sensor module to J1: its route, and the length the docs tell people to buy.

Until r2.4b the docs said 30 to 40 mm without a calculation, while the cradle was drawn for a
module with its connector on the back; that route would have needed about 49 mm. With the real
module (connector on the lens side, cable out of the short end) the route is computed in
scripts/k0d3/ffc_route.py from the cradle and the layout, and this file holds the documented
length against it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from k0d3.ffc_route import route
from k0d3.geometry import load_layout

ROOT = Path(__file__).resolve().parents[1]
DOCS = ["spec/03-bom.md", "spec/04-build-guide.md", "spec/08-trackball-module.md", "spec/12-order-checklist.md"]


def _layout():
    return load_layout("right")


def test_route_is_short_and_the_cable_has_room():
    lay = _layout()
    r = route(lay)
    length = lay.cfg["fpc"]["cable_length"]
    assert 25.0 < r.total < 40.0, f"route {r.total:.1f} mm"
    slack = length - r.total
    assert 5.0 <= slack <= 15.0, f"{length} mm cable leaves {slack:.1f} mm: too tight or it bows in the pocket"


def test_route_leaves_towards_the_keys_and_takes_the_short_way():
    r = route(_layout())
    assert r.module_mouth[1] < -6.0, "the module's cable mouth is not on the key side (layout -y)"
    assert r.sweep_deg < 100.0, f"the cable runs {r.sweep_deg:.0f} deg round the cup"


def test_band_stays_under_the_clip_pins_and_the_cover():
    """Round the cup the cable stands upright; its top edge must pass under the retainer clip's
    snap pins (they hang down through the cover) and under the cover itself."""
    case = json.loads((ROOT / "hardware/case/stack.json").read_text())
    right = case["variants"]["right"]
    r = route(_layout())
    assert r.band_top_z < right["clip_barb_bottom_z"] - 0.5, (r.band_top_z, right["clip_barb_bottom_z"])


def test_docs_give_the_computed_cable_length():
    length = _layout().cfg["fpc"]["cable_length"]
    for doc in DOCS:
        text = (ROOT / doc).read_text()
        assert "30 to 40 mm" not in text, f"{doc} still gives the old guess"
        assert re.search(rf"\b{length} mm\b", text), f"{doc} does not give the {length} mm cable"
