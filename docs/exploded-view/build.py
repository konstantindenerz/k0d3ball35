#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build docs/exploded-view/index.html from template.html and the layout data.

Reads hardware/layout/output/points.json, hardware/layout/k0d3ball36.yaml and
hardware/trackball-cradle/stack.json, writes layout.json and inlines it into the page so
the HTML is self-contained. Run after `make layout`.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def simplify(points: list[list[float]], tol: float = 0.25) -> list[list[float]]:
    try:
        from shapely.geometry import Polygon

        poly = Polygon(points).simplify(tol)
        return [[round(x, 2), round(y, 2)] for x, y in list(poly.exterior.coords)[:-1]]
    except Exception:  # shapely missing: keep every point
        return [[round(x, 2), round(y, 2)] for x, y in points]


def main() -> None:
    points = json.loads((REPO / "hardware/layout/output/points.json").read_text())
    cfg = yaml.safe_load((REPO / "hardware/layout/k0d3ball36.yaml").read_text())
    stack = json.loads((REPO / "hardware/trackball-cradle/stack.json").read_text())["variants"]["25mm"]
    data = {
        "name": points["name"],
        "revision": points["revision"],
        "outline": simplify(points["outline"]),
        "bounds": points["bounds"],
        "keys": [{"ref": f"SW{k['row']}{k['col']}", "x": k["x"], "y": k["y"], "rot": k["rotation"], "kind": k["kind"]} for k in points["keys"]],
        "keycap": cfg["keycap"],
        "switch_body": cfg["switch_body"],
        "ball": {"d": cfg["trackball"]["ball_diameter"], "x": cfg["trackball"]["center"]["x"], "y": cfg["trackball"]["center"]["y"],
                 "cutout_d": cfg["trackball"]["pcb_cutout_diameter"], "cradle_d": cfg["trackball"]["cradle_diameter"],
                 "flange_circle": cfg["trackball"]["flange_hole_circle"], "flange_angles": cfg["trackball"]["flange_hole_angles"]},
        "controller": {"x": cfg["controller"]["center"]["x"], "y": cfg["controller"]["center"]["y"],
                       "w": cfg["controller"]["size"]["x"], "l": cfg["controller"]["size"]["y"]},
        "fpc": cfg["fpc"]["center"],
        "power_switch": cfg["power_switch"]["center"],
        "reset": cfg["reset_button"]["center"],
        "battery_pads": cfg["battery_pads"]["center"],
        "jst": cfg["battery_jst"]["center"],
        "jumpers": cfg["jumpers"],
        "test_pads": cfg["test_pads"],
        "holes": cfg["mounting_holes"],
        "stack": {"ball_centre_z": stack["ball_centre_z"], "ball_top": stack["ball_top_above_pcb_top"],
                  "cup_outer_d": stack["cup_outer_d"], "lowest_plastic_z": stack["lowest_plastic_z"],
                  "lowest_sensor_board_z": stack["lowest_sensor_board_z"], "lens_gap": stack["lens_reference_plane_dist"],
                  "bearing_contact_z": stack["bearing_contact_z"], "rim_z": stack["rim_z"]},
        "pcb_thickness": 1.6,
    }
    (HERE / "layout.json").write_text(json.dumps(data, indent=1) + "\n")
    template = (HERE / "template.html").read_text()
    html = template.replace("/*__LAYOUT_DATA__*/", json.dumps(data, separators=(",", ":")))
    (HERE / "index.html").write_text(html)
    print(f"wrote index.html ({len(html) // 1024} KiB), {len(data['outline'])} outline points")


if __name__ == "__main__":
    main()
