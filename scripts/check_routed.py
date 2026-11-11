#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Refuse a main PCB that is not routed: scripts/check_routed.py <board.kicad_pcb> <drc.json>

r2.4 once committed both boards with only the hand routes and no GND pour: the autorouter had
been skipped because java was not on the PATH, and the gerbers were exported from that board.
This runs after routing (build_board.sh) and before every export (export.sh).
"""
import json
import re
import sys
from pathlib import Path

MIN_SEGMENTS = 300      # a routed half has about 700; the hand routes alone are about 100


def problems(board: Path, drc: Path) -> list[str]:
    text = board.read_text()
    out = []
    segments = len(re.findall(r"\(segment\b", text))
    if segments < MIN_SEGMENTS:
        out.append(f"only {segments} track segments (routed boards have ~700): was the autorouter skipped?")
    if "filled_polygon" not in text:
        out.append("no filled copper zone: the GND pour is missing")
    report = json.loads(drc.read_text())
    if report.get("unconnected_items"):
        out.append(f"{len(report['unconnected_items'])} unconnected items in the DRC")
    return out


if __name__ == "__main__":
    board, drc = Path(sys.argv[1]), Path(sys.argv[2])
    found = problems(board, drc)
    for p in found:
        print(f"{board.name}: {p}", file=sys.stderr)
    sys.exit(1 if found else 0)
