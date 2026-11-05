#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Autoroute the main PCB with freerouting and refill the zones.

Runs with KiCad's bundled Python (needs the pcbnew module):
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 scripts/route.py

Steps: load board -> export Specctra DSN -> freerouting (java) -> import SES -> fill zones -> save in place.
Environment: FREEROUTING_JAR (path to freerouting-2.x.jar), JAVA (java binary, default: java).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pcbnew

REPO = Path(__file__).resolve().parents[1]
PCB = REPO / "hardware" / "main-pcb" / "k0d3ball36.kicad_pcb"
BUILD = REPO / "build"


def main() -> int:
    pcb = Path(sys.argv[1]) if len(sys.argv) > 1 else PCB
    passes = os.environ.get("FREEROUTING_PASSES", "30")
    jar = os.environ.get("FREEROUTING_JAR")
    java = os.environ.get("JAVA", "java")
    if not jar or not Path(jar).exists():
        print("FREEROUTING_JAR not set or missing", file=sys.stderr)
        return 2
    BUILD.mkdir(exist_ok=True)
    dsn, ses = BUILD / (pcb.stem + ".dsn"), BUILD / (pcb.stem + ".ses")
    board = pcbnew.LoadBoard(str(pcb))
    # start from a clean slate: drop existing tracks and vias
    for t in list(board.GetTracks()):
        board.Remove(t)
    ok = pcbnew.ExportSpecctraDSN(board, str(dsn))
    print("DSN export:", ok, dsn)
    cmd = [java, "-jar", jar, "-de", str(dsn), "-do", str(ses), "-mp", passes, "-l", "en", "-dct", "0"]
    print(" ".join(cmd))
    res = subprocess.run(cmd, cwd=BUILD, capture_output=True, text=True, timeout=3600)
    tail = "\n".join(res.stdout.splitlines()[-15:])
    print(tail)
    if not ses.exists():
        print("freerouting produced no session file", file=sys.stderr)
        print(res.stderr[-3000:], file=sys.stderr)
        return 1
    ok = pcbnew.ImportSpecctraSES(board, str(ses))
    print("SES import:", ok)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(pcb), board)
    print("saved", pcb, "tracks:", len(board.GetTracks()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
