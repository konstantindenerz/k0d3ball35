#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate key positions, PCB outlines and previews from hardware/layout/k0d3ball35.yaml.

Outputs (hardware/layout/output/), one set per half:
  points-<half>.json    key positions, outline polygon, ball pocket and controller data
  outline-<half>.dxf    PCB outline, pocket circles, holes, switch bodies (for the case design)
  preview-<half>.png    top view (the left half drawn mirrored, as on the desk)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from k0d3.geometry import HALVES, REPO, check_layout, load_layout, write_outline_dxf, write_points, write_preview  # noqa: E402


def main() -> int:
    halves = [h for h in sys.argv[1:] if h in HALVES] or list(HALVES)
    out = REPO / "hardware" / "layout" / "output"
    rc = 0
    for half in halves:
        layout = load_layout(half)
        problems = check_layout(layout)
        write_points(layout, out / f"points-{half}.json")
        write_outline_dxf(layout, out / f"outline-{half}.dxf")
        write_preview(layout, out / f"preview-{half}.png")
        b = layout.to_dict()["bounds"]
        print(f"{half}: {len(layout.keys)} keys, PCB {b['width']:.1f} x {b['height']:.1f} mm"
              + (f", ball at {layout.ball_center}" if layout.has_ball else ""))
        for k in layout.keys:
            print(f"  {k.ref:5} {k.name:13} x={k.x:8.2f} y={k.y:7.2f} rot={k.rotation:5.1f}")
        if problems:
            print("PROBLEMS:")
            for p in problems:
                print("  -", p)
            rc = 1
        else:
            print(f"  layout checks passed ({half})")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
