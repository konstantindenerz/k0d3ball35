#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write the owner wordmark derivatives: hardware/case/logo_data.scad for the case model and
spec/images/logo.svg as the vector master. The grid recovery itself lives in k0d3.logo.

Usage: scripts/gen_logo.py [scad] [svg]
"""
from __future__ import annotations

import sys
from pathlib import Path

from k0d3.logo import (DEFAULT_OUT, DEFAULT_SRC, DEFAULT_SVG, build, polygons, size,  # noqa: F401
                       write_data, write_svg)


def main(argv: list[str]) -> None:
    out = Path(argv[1]) if len(argv) > 1 else DEFAULT_OUT
    svg = Path(argv[2]) if len(argv) > 2 else DEFAULT_SVG
    grid, aspect, rects = build()
    write_data(out)
    write_svg(svg)
    ink = sum(sum(r) for r in grid)
    print("\n".join("".join("#" if v else "." for v in row) for row in grid))
    print(f"{len(grid[0])} x {len(grid)} cells, aspect {aspect:.3f}, {ink} ink, {len(rects)} rects")
    print(f"wrote {out} and {svg}")


if __name__ == "__main__":
    main(sys.argv)
