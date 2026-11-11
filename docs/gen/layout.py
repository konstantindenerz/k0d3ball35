# SPDX-License-Identifier: MIT
"""docs/data/layout.json: the layout facts the explorer and the keymap draw from.

Reads hardware/layout/output/points-left.json and points-right.json, hardware/layout/k0d3ball35.yaml,
hardware/trackball-cradle/stack.json (19 mm pocket variant) and hardware/case/stack.json. The case
meshes are not embedded any more: `case_files` names the repo path of each STL and the page fetches
it (raw.githubusercontent.com on the published site, the working tree on localhost).
The right half carries the ball pocket, the left half has no ball; both carry the same battery
bay under the controller.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from . import REPO, case_param

HALVES = ("left", "right")
TEST_PADS = {"left": ["D0", "D1", "D2", "D3", "D9", "D10", "D14", "D15", "D16"], "right": ["D0", "D1", "D2", "D3", "D9"]}
STACK_KEYS = ("ball_centre_z", "ball_top_above_pcb_top", "cup_outer_d", "lowest_plastic_z", "lowest_sensor_board_z",
              "lens_reference_plane_dist", "bearing_contact_z", "rim_z", "floor_z", "sensor_pcb_plane_z",
              "housing_x", "housing_y", "housing_top_z", "footprint_x", "footprint_y", "envelope_d_above_pcb", "notch_apothem")
# STLs the explorer shows per half, in the layout frame (left files are physically mirrored)
CASE_PARTS = {"tray": "tray-{half}", "cap": "box-cap-{half}", "lid": "lid-{half}", "lid_folded": "lid-folded-{half}"}


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


CASE_STACK_KEYS = ("base_z", "floor_z_key", "well_floor_z", "pocket_floor_z", "rim_z", "standoff_h",
                   "box_roof_under_z", "box_top_z", "lid_roof_under_z", "lid_top_z", "lid_lip_depth",
                   "hinge_x", "hinge_axis_z", "hinge_fold_deg", "tent_deg", "foot_dx", "foot_hinge_h", "foot_reach",
                   "case_screw_d", "case_screw_head_d", "case_screw_cs_d", "case_screw_cs_h", "case_screw_head_z")


def half_data(half: str, cfg: dict, stack: dict) -> dict:
    # points-*.json is in the handedness-neutral layout frame; the page mirrors the left half for
    # display (root.scale.x = -1), which matches the mirrored left board files (hardware/left-pcb).
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
        "battery": points["battery"],   # same cell and bay on both halves, under the PCB below the controller
        "stack": {k: stack[k] for k in STACK_KEYS if k in stack} if ball else None,
        "case_stack": case_stack(half),
        "case_files": {k: f"hardware/case/stl/{v.format(half=half)}.stl" for k, v in CASE_PARTS.items()},
    }


def case_stack(half: str) -> dict:
    s = json.loads((REPO / "hardware/case/stack.json").read_text())["variants"][half]
    return {k: s[k] for k in CASE_STACK_KEYS if k in s}


def build() -> dict:
    cfg = yaml.safe_load((REPO / "hardware/layout/k0d3ball35.yaml").read_text())
    stack = json.loads((REPO / "hardware/trackball-cradle/stack.json").read_text())["variants"]["19mm-pocket"]
    right = json.loads((REPO / "hardware/layout/output/points-right.json").read_text())
    return {
        "name": right["name"],
        "revision": right["revision"],
        "keycap": cfg["keycap"],
        "switch_body": cfg["switch_body"],
        "controller": {"x": cfg["controller"]["center"]["x"], "y": cfg["controller"]["center"]["y"],
                       "w": cfg["controller"]["size"]["x"], "l": cfg["controller"]["size"]["y"],
                       "socket": cfg["controller"]["socket_height"]},
        # lid over the controller block: socket + nice!nano PCB + USB-C shell above it + 1.8 mm air and lid clearance
        "controller_lid_z": round(cfg["controller"]["socket_height"] + 1.6 + 1.6 + 1.8, 1),
        "power_switch": cfg["power_switch"]["center"],
        "reset": cfg["reset_button"]["center"],
        "battery_pads": cfg["battery_pads"]["center"],
        "jst": cfg["battery_jst"]["center"],
        "pcb_thickness": 1.6,
        "cap_top_z": case_param("cap_top_z"),   # Choc keycap top over the PCB top
        "halves": {half: half_data(half, cfg, stack) for half in HALVES},
    }
