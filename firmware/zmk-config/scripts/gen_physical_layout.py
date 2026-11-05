#!/usr/bin/env python3
"""Generate the ZMK physical layout (key_physical_attrs rows) for k0d3ball36.

Geometry follows docs/01-design-spec.md section 5. Until the layout generator in
hardware/layout/ exports exact positions, the approximate values from the spec are
used. Run with --json to emit the keymap-editor layout instead of devicetree.

Units: ZMK physical layouts use centi-keyunits. One keyunit is taken as 18 mm
(the Choc column pitch), so a key is 100 wide and 94 high (17 mm).
"""
from __future__ import annotations

import argparse
import json
import math

MM_PER_UNIT = 18.0
KEY_W_MM, KEY_H_MM = 18.0, 17.0
COL_PITCH_MM, ROW_PITCH_MM = 18.0, 17.0

# column index 0 = pinky ... 4 = inner; y offsets in mm relative to the middle column
STAGGER_MM = [10.44, 4.19, 0.0, 2.23, 4.46]
# thumb keys on the left half: (x, y, rotation_deg) of the key centre in mm,
# x measured from the middle column centre towards the inside of the board,
# y measured from the top row centre downwards.
THUMBS_MM = [
    (22.0, 58.5, 0.0),   # thumb outer   -> matrix (3,2)
    (41.0, 60.5, 10.0),  # thumb middle  -> matrix (3,3)
    (59.5, 65.5, 20.0),  # thumb inner   -> matrix (3,4)
]
HALF_GAP_MM = 36.0  # distance from the inner column centre to the mirror axis


def left_half_centres() -> list[tuple[float, float, float]]:
    """Return (x, y, rot) centres in mm for the left half, in matrix-transform order.

    Order: row 0 pinky..inner, row 1, row 2, then thumbs outer..inner.
    x grows to the right (towards the centre of the keyboard), y grows downwards.
    The middle-column top key centre is the origin.
    """
    keys = []
    for row in range(3):
        for col in range(5):
            x = (col - 2) * COL_PITCH_MM
            y = row * ROW_PITCH_MM + STAGGER_MM[col]
            keys.append((x, y, 0.0))
    for x, y, rot in THUMBS_MM:
        keys.append((x, y, rot))
    return keys


def both_halves() -> list[tuple[float, float, float]]:
    """Centres for all 36 keys in matrix-transform order (rows interleaved L/R)."""
    left = left_half_centres()
    axis = 2 * COL_PITCH_MM + HALF_GAP_MM  # x of the mirror axis
    right = [(2 * axis - x, y, -rot) for (x, y, rot) in left]
    # right half columns are mirrored, so pinky is the right-most key: reverse each row
    ordered: list[tuple[float, float, float]] = []
    for row in range(3):
        ordered += left[row * 5:(row + 1) * 5]
        ordered += right[row * 5:(row + 1) * 5][::-1]
    ordered += left[15:18]
    ordered += right[15:18][::-1]
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
    return {"id": "k0d3ball36", "name": "k0d3ball36", "layouts": {"default_layout": {"layout": layout}}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit keymap-editor JSON")
    args = ap.parse_args()
    keys = both_halves()
    assert len(keys) == 36
    if args.json:
        print(json.dumps(to_json(keys), indent=2))
    else:
        print(to_dts(keys))


if __name__ == "__main__":
    main()
