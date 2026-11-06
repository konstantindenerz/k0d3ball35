#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build docs/exploded-view/index.html from template.html and the layout data.

Reads hardware/layout/output/points-left.json and points-right.json,
hardware/layout/k0d3ball35.yaml and hardware/trackball-cradle/stack.json (19 mm pocket
variant), writes layout.json and inlines it into the page so the HTML is self-contained.
The right half carries the ball pocket, the left half has no ball. Run after `make layout`.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
HALVES = ("left", "right")
TEST_PADS = {"left": ["D0", "D1", "D2", "D3", "D9", "D10", "D14", "D15", "D16"], "right": ["D0", "D1", "D2", "D3", "D9"]}
STACK_KEYS = ("ball_centre_z", "ball_top_above_pcb_top", "cup_outer_d", "lowest_plastic_z", "lowest_sensor_board_z",
              "lens_reference_plane_dist", "bearing_contact_z", "rim_z", "floor_z", "sensor_pcb_plane_z",
              "housing_x", "housing_y", "housing_top_z", "footprint_x", "footprint_y", "envelope_d_above_pcb", "notch_apothem")


def _ring(poly) -> list[list[float]]:
    if poly.geom_type != "Polygon":
        poly = max(poly.geoms, key=lambda g: g.area)
    return [[round(x, 2), round(y, 2)] for x, y in list(poly.exterior.coords)[:-1]]


def simplify(points: list[list[float]], tol: float = 0.25) -> list[list[float]]:
    from shapely.geometry import Polygon

    return _ring(Polygon(points).simplify(tol))


def offset(points: list[list[float]], by: float) -> list[list[float]]:
    """Proper polygon offset with mitre joins (a radial offset from the bounding-box centre
    produces self-intersecting rings on the concave outlines, which the page then
    triangulates wrongly)."""
    from shapely.geometry import Polygon

    return _ring(Polygon(points).buffer(by, join_style=2, mitre_limit=3.0).simplify(0.1))


def feet(outline: list[list[float]], inset: float = 7.0) -> list[list[float]]:
    """Four rubber feet: the points of the case floor (inset so a 10 mm foot stays inside) that
    lie closest to the four corners of the bounding box."""
    from shapely.geometry import Point, Polygon
    from shapely.ops import nearest_points

    poly = Polygon(outline).buffer(-inset, join_style=2)
    if poly.geom_type != "Polygon":
        poly = max(poly.geoms, key=lambda g: g.area)
    minx, miny, maxx, maxy = Polygon(outline).bounds
    out = []
    for cx, cy in ((minx, miny), (maxx, miny), (minx, maxy), (maxx, maxy)):
        p = nearest_points(poly, Point(cx, cy))[0]
        out.append([round(p.x, 1), round(p.y, 1)])
    return out


def half_data(half: str, cfg: dict, stack: dict) -> dict:
    points = json.loads((REPO / f"hardware/layout/output/points-{half}.json").read_text())
    tb = points.get("trackball")
    ball = None
    if tb:
        ball = {"d": tb["ball_diameter"], "x": tb["center"]["x"], "y": tb["center"]["y"],
                "cradle_d": tb["cradle_diameter"], "pocket_d": tb["pocket_diameter"],
                "notch": tb["notch"], "sensor_board": tb["sensor_board"],
                "housing_footprint": tb["housing_footprint"], "case_screws": tb["case_screws"]}
    fpc = points.get("fpc")
    return {
        "half": half,
        "keys": [{"ref": f"SW{k['row']}{k['col']}", "x": k["x"], "y": k["y"], "rot": k["rotation"], "kind": k["kind"]} for k in points["keys"]],
        "outline": simplify(points["outline"]),
        "outline_case": offset(points["outline"], 3.0),      # case wall outer edge
        "outline_frame_hole": offset(points["outline"], -2.5),  # top frame opening
        "feet": feet(offset(points["outline"], 3.0)),
        "bounds": points["bounds"],
        "ball": ball,
        "fpc": fpc["center"] if fpc else None,
        "holes": points["mounting_holes"],
        "test_pads": {"start": cfg["test_pads"]["start"], "pitch": cfg["test_pads"]["pitch"], "labels": TEST_PADS[half]},
        "battery": "702025" if ball else "301230",
        "stack": {k: stack[k] for k in STACK_KEYS if k in stack} if ball else None,
    }


def main() -> None:
    cfg = yaml.safe_load((REPO / "hardware/layout/k0d3ball35.yaml").read_text())
    stack = json.loads((REPO / "hardware/trackball-cradle/stack.json").read_text())["variants"]["19mm-pocket"]
    right = json.loads((REPO / "hardware/layout/output/points-right.json").read_text())
    data = {
        "name": right["name"],
        "revision": right["revision"],
        "keycap": cfg["keycap"],
        "switch_body": cfg["switch_body"],
        "controller": {"x": cfg["controller"]["center"]["x"], "y": cfg["controller"]["center"]["y"],
                       "w": cfg["controller"]["size"]["x"], "l": cfg["controller"]["size"]["y"]},
        "power_switch": cfg["power_switch"]["center"],
        "reset": cfg["reset_button"]["center"],
        "battery_pads": cfg["battery_pads"]["center"],
        "jst": cfg["battery_jst"]["center"],
        "pcb_thickness": 1.6,
        "halves": {half: half_data(half, cfg, stack) for half in HALVES},
    }
    (HERE / "layout.json").write_text(json.dumps(data, indent=1) + "\n")
    template = (HERE / "template.html").read_text()
    html = template.replace("/*__LAYOUT_DATA__*/", json.dumps(data, separators=(",", ":")))
    (HERE / "index.html").write_text(html)
    n = {h: len(data["halves"][h]["keys"]) for h in HALVES}
    print(f"wrote index.html ({len(html) // 1024} KiB), keys {n}, ball top +{stack['ball_top_above_pcb_top']:.1f} mm")


if __name__ == "__main__":
    main()
