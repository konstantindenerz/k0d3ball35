#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate key positions, PCB outline and previews from hardware/layout/k0d3ball36.yaml.

Outputs (hardware/layout/output/):
  points.json          all key positions, outline polygon, ball and controller data
  outline.dxf          PCB outline, cutout, holes and switch bodies (for the case design)
  preview-right.png    top view of the right half
  preview-left.png     top view of the left (mirrored) half
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from k0d3.geometry import REPO, check_layout, load_layout, write_outline_dxf, write_points, write_preview  # noqa: E402


def main() -> int:
    layout = load_layout()
    problems = check_layout(layout)
    out = REPO / "hardware" / "layout" / "output"
    write_points(layout, out / "points.json")
    write_outline_dxf(layout, out / "outline.dxf")
    write_preview(layout, out / "preview-right.png")
    write_preview(layout, out / "preview-left.png", mirror=True)
    b = layout.to_dict()["bounds"]
    print(f"{len(layout.keys)} keys, outline {b['width']:.1f} x {b['height']:.1f} mm")
    for k in layout.keys:
        print(f"  {k.ref:5} {k.name:13} x={k.x:8.2f} y={k.y:7.2f} rot={k.rotation:5.1f}")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  -", p)
        return 1
    print("layout checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
