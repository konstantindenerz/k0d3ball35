#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the unrouted PCB of one or both halves and the footprint library.

    scripts/gen_pcb.py [left|right ...]      (default: both)

Writes hardware/<half>-pcb/k0d3ball35-<half>.kicad_pcb and regenerates
hardware/lib/k0d3ball35.pretty.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen_schematic import board_dir, board_name  # noqa: E402
from k0d3.geometry import HALVES, REPO, check_layout, load_layout  # noqa: E402
from k0d3.netlist import LIB, build_components  # noqa: E402
from k0d3.pcb import build_pcb, write_library  # noqa: E402

LIB_DIR = REPO / "hardware" / "lib" / f"{LIB}.pretty"


def generate(half: str) -> int:
    layout = load_layout(half)
    problems = check_layout(layout)
    if problems:
        print(f"layout problems ({half}):\n  " + "\n  ".join(problems))
        return 1
    comps = build_components(layout)
    out = board_dir(half)
    out.mkdir(parents=True, exist_ok=True)
    name = board_name(half)
    (out / f"{name}.kicad_pcb").write_text(build_pcb(layout, comps, f"{name}.kicad_sch"))
    print(f"wrote {out / (name + '.kicad_pcb')} ({len(comps)} footprints)")
    return 0


def main(argv: list[str]) -> int:
    halves = argv or list(HALVES)
    bad = [h for h in halves if h not in HALVES]
    if bad:
        print(f"unknown half {bad}, expected one of {HALVES}", file=sys.stderr)
        return 2
    files = write_library(LIB_DIR)
    print(f"wrote {len(files)} library footprints to {LIB_DIR}")
    return max(generate(h) for h in halves)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
