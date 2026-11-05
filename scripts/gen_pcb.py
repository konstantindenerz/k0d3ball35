#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the unrouted main PCB (hardware/main-pcb/k0d3ball36.kicad_pcb) and the footprint library."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from k0d3.geometry import REPO, check_layout, load_layout  # noqa: E402
from k0d3.netlist import build_components  # noqa: E402
from k0d3.pcb import build_pcb, write_library  # noqa: E402

OUT = REPO / "hardware" / "main-pcb"
LIB_DIR = REPO / "hardware" / "lib" / "k0d3ball36.pretty"


def main() -> int:
    layout = load_layout()
    problems = check_layout(layout)
    if problems:
        print("layout problems:\n  " + "\n  ".join(problems))
        return 1
    comps = build_components(layout)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "k0d3ball36.kicad_pcb").write_text(build_pcb(layout, comps, "k0d3ball36.kicad_sch"))
    files = write_library(LIB_DIR)
    print(f"wrote {OUT / 'k0d3ball36.kicad_pcb'} ({len(comps)} footprints) and {len(files)} library footprints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
