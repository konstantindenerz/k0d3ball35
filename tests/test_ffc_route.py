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

from k0d3.ffc_route import SLACK_Z, SLACK_ZONE, route, slack_capacity
from k0d3.geometry import load_layout

ROOT = Path(__file__).resolve().parents[1]
DOCS = ["spec/03-bom.md", "spec/04-build-guide.md", "spec/08-trackball-module.md", "spec/12-order-checklist.md"]


def _layout():
    return load_layout("right")


def test_route_is_short_and_the_cable_has_room():
    lay = _layout()
    r = route(lay)
    length = lay.cfg["fpc"]["cable_length"]
    assert 25.0 < r.total < 45.0, f"route {r.total:.1f} mm"
    slack = length - r.total
    assert slack >= 3.0, f"{length} mm cable leaves only {slack:.1f} mm to plug it in"
    cap = slack_capacity()
    assert slack <= cap, f"{slack:.1f} mm of slack, the S-fold zone holds {cap:.1f}"


def test_slack_zone_is_free():
    """The S-fold zone beside J1 must be empty: outside the cradle (mesh), off the PCB, inside the
    pocket opening (open from the PCB underside up), under the pocket cover, clear of the case
    screw and of the clip pins (which only reach down to z 3.3, above the band)."""
    import numpy as np
    import trimesh  # noqa: F401
    from scad_frame import load_layout_frame
    from shapely.geometry import box as sbox
    import gen_case
    lay = _layout()
    bx, by = lay.ball_center
    x0, y0, x1, y1 = SLACK_ZONE
    zone = sbox(bx + x0, by + y0, bx + x1, by + y1)
    assert zone.within(sbox(*gen_case.pocket_opening(lay).bounds)), "zone leaves the pocket opening"
    assert zone.distance(lay.outline) > 0.0 and not zone.intersects(lay.outline), "zone is over the PCB"
    for sx, sy in lay.case_screws():
        assert zone.distance(sbox(sx - 1.1, sy - 1.1, sx + 1.1, sy + 1.1)) > 0.3
    case = json.loads((ROOT / "hardware/case/stack.json").read_text())["variants"]["right"]
    assert SLACK_Z[1] < case["clip_barb_bottom_z"] - 0.5
    mesh = load_layout_frame(ROOT / "hardware/trackball-cradle/stl/cradle-19mm-pocket.stl")
    xs, ys, zs = (np.linspace(a, b, 12) for a, b in ((x0, x1), (y0, y1), SLACK_Z))
    pts = np.array([(x, y, z) for x in xs for y in ys for z in zs])
    s = json.loads((ROOT / "hardware/trackball-cradle/stack.json").read_text())["variants"]["19mm-pocket"]
    outside_cup = np.hypot(pts[:, 0], pts[:, 1]) > s["cup_outer_d"] / 2 + 0.3
    hit = mesh.contains(pts[outside_cup])
    assert not hit.any(), f"cradle plastic in the slack zone at {pts[outside_cup][hit][:3]}"


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
