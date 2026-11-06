#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the ZMK physical layout (key_physical_attrs rows) for k0d3ball35.

Key centres come from the layout generator's exact output,
hardware/layout/output/points-left.json and points-right.json (run
`scripts/gen_layout.py` to refresh them). Both files use the same frame: x grows
outward towards the pinky, y grows downward, origin = centre of the middle
column's top key. The left half is mirrored for display, the right half is used
as is, and the two halves are placed HALF_GAP_MM apart (inner column centre to
the mirror axis).

Keys are emitted in matrix-transform order (k0d3ball35.dtsi): three finger rows,
each left pinky..inner then right inner..pinky, followed by the thumb keys (left
outer, middle, inner, then right middle, outer). 35 keys in total.

Run with --json to emit the keymap-editor layout instead of devicetree.

Units: ZMK physical layouts use centi-keyunits. One keyunit is taken as 18 mm
(the Choc column pitch), so a key is 100 wide and 94 high (17 mm).
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
POINTS = ROOT / "hardware" / "layout" / "output"

MM_PER_UNIT = 18.0
KEY_W_MM, KEY_H_MM = 18.0, 17.0
HALF_GAP_MM = 36.0  # distance from the inner column centre to the mirror axis
EXPECTED_KEYS = 35


def load_points(half: str) -> dict:
    path = POINTS / f"points-{half}.json"
    if not path.exists():
        raise SystemExit(f"{path} missing; run `.venv/bin/python scripts/gen_layout.py` first")
    return json.loads(path.read_text())


def display_keys(half: str) -> dict[tuple[int, int], tuple[float, float, float]]:
    """Return {(row, col): (x, y, rot)} in the display frame (x to the right, y down).

    Display x = 0 is the mirror axis between the halves. Rotation is clockwise
    positive (ZMK convention); the layout files use KiCad's counter-clockwise
    convention, so the right half flips the sign and the mirrored left half keeps it.
    """
    data = load_points(half)
    inner_x = min(k["x"] for k in data["keys"] if k["kind"] == "finger")
    shift = -inner_x + HALF_GAP_MM  # moves the inner column to HALF_GAP_MM from the axis
    keys = {}
    for k in data["keys"]:
        x_out = k["x"] + shift  # distance from the axis, positive outward
        if half == "left":
            keys[(k["row"], k["col"])] = (-x_out, k["y"], float(k["rotation"]))
        else:
            keys[(k["row"], k["col"])] = (x_out, k["y"], -float(k["rotation"]))
    return keys


def both_halves() -> list[tuple[float, float, float]]:
    """Centres for all keys in matrix-transform order."""
    left = display_keys("left")
    right = display_keys("right")
    ordered: list[tuple[float, float, float]] = []
    for row in range(3):
        ordered += [left[(row, c)] for c in range(5)]
        ordered += [right[(row, c)] for c in range(4, -1, -1)]
    thumbs_left = sorted((rc for rc in left if rc[0] == 3), key=lambda rc: rc[1])
    thumbs_right = sorted((rc for rc in right if rc[0] == 3), key=lambda rc: -rc[1])
    ordered += [left[rc] for rc in thumbs_left]
    ordered += [right[rc] for rc in thumbs_right]
    return ordered


def to_dts(keys) -> str:
    min_x = min(x - KEY_W_MM / 2 for x, _, _ in keys)
    min_y = min(y - KEY_H_MM / 2 for _, y, _ in keys)
    w = round(KEY_W_MM / MM_PER_UNIT * 100)
    h = round(KEY_H_MM / MM_PER_UNIT * 100)
    lines = []
    for i, (cx, cy, rot) in enumerate(keys):
        x = round((cx - KEY_W_MM / 2 - min_x) / MM_PER_UNIT * 100)
        y = round((cy - KEY_H_MM / 2 - min_y) / MM_PER_UNIT * 100)
        r = round(rot * 100)
        rx = round((cx - min_x) / MM_PER_UNIT * 100) if r else 0
        ry = round((cy - min_y) / MM_PER_UNIT * 100) if r else 0
        r_txt = f"({r})" if r < 0 else str(r)
        sep = "=" if i == 0 else ","
        lines.append(f"            {sep} <&key_physical_attrs {w:4d} {h:4d} {x:5d} {y:5d} {r_txt:>7} {rx:5d} {ry:5d}>")
    return "\n".join(lines) + "\n            ;"


def to_json(keys) -> dict:
    min_x = min(x - KEY_W_MM / 2 for x, _, _ in keys)
    min_y = min(y - KEY_H_MM / 2 for _, y, _ in keys)
    layout = []
    for cx, cy, rot in keys:
        entry = {
            "x": round((cx - KEY_W_MM / 2 - min_x) / MM_PER_UNIT, 3),
            "y": round((cy - KEY_H_MM / 2 - min_y) / MM_PER_UNIT, 3),
            "w": 1,
            "h": round(KEY_H_MM / KEY_W_MM, 3),
        }
        if rot:
            entry["r"] = rot
            entry["rx"] = round((cx - min_x) / MM_PER_UNIT, 3)
            entry["ry"] = round((cy - min_y) / MM_PER_UNIT, 3)
        layout.append(entry)
    return {"id": "k0d3ball35", "name": "k0d3ball35", "layouts": {"default_layout": {"layout": layout}}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit keymap-editor JSON")
    args = ap.parse_args()
    keys = both_halves()
    assert len(keys) == EXPECTED_KEYS, f"expected {EXPECTED_KEYS} keys, got {len(keys)}"
    if args.json:
        print(json.dumps(to_json(keys), indent=2))
    else:
        print(to_dts(keys))


if __name__ == "__main__":
    main()
