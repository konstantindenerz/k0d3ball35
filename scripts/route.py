#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Autoroute one main PCB with freerouting and refill the zones.

Runs with KiCad's bundled Python (needs the pcbnew module):
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \
      scripts/route.py [stage] [path/to/board.kicad_pcb]
Default stage is "all", default board is the right half. Build artefacts (DSN, SES, router
copies) are named after the board file in build/, so both halves can be routed in turn.

Stages (each in its own process, the pcbnew Python wrapper misbehaves after a Specctra import):
  prepare  remove unlocked tracks, save; give duplicate pad numbers unique names in a copy and
           export that copy as Specctra DSN (freerouting keeps only one pin per name otherwise)
  route    freerouting (java) -> SES
  import   import the SES into the real board, save
  finish   widen undersized tracks to their net class, fill zones, save
Environment: FREEROUTING_JAR (path to freerouting-2.x.jar), JAVA (java binary), FREEROUTING_PASSES.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pcbnew

REPO = Path(__file__).resolve().parents[1]
PCB = REPO / "hardware" / "right-pcb" / "k0d3ball35-right.kicad_pcb"
BUILD = REPO / "build"


def prepare(pcb: Path) -> None:
    """Remove unlocked tracks from the real board and write the router copy (file level)."""
    import shutil

    board = pcbnew.LoadBoard(str(pcb))
    for t in list(board.GetTracks()):
        if not t.IsLocked():          # keep the generator's stubs and stitching vias
            board.Remove(t)
    pcbnew.SaveBoard(str(pcb), board)
    copy = BUILD / (pcb.stem + "-router.kicad_pcb")
    shutil.copyfile(pcb, copy)
    pro = json.loads(pcb.with_suffix(".kicad_pro").read_text())
    for c in pro["net_settings"]["classes"]:
        # absorb freerouting rounding; the FPC class stays at the pad gap so the 0.5 mm
        # connector is not reported as a pre-existing violation
        c["clearance"] = round(c["clearance"] + 0.05, 3)
    copy.with_suffix(".kicad_pro").write_text(json.dumps(pro, indent=2))
    print("router copy:", copy)


def export_dsn(pcb: Path, dsn: Path) -> None:
    """Separate process: unique pad names + baked rotations in the router copy, then DSN export.

    Freerouting keeps only one pin per name and mis-handles images placed at angles other
    than multiples of 90 degrees, so the copy gets unique pad numbers and pads at absolute
    rotated positions with the footprint itself at 0 degrees. The copy is never saved back.
    """
    copy = BUILD / (pcb.stem + "-router.kicad_pcb")
    board = pcbnew.LoadBoard(str(copy))
    baked = 0
    for fp in board.GetFootprints():
        seen: dict[str, int] = {}
        pads = list(fp.Pads())
        for pad in pads:
            n = pad.GetNumber()
            if n:
                seen[n] = seen.get(n, 0) + 1
                if seen[n] > 1:
                    pad.SetNumber(f"{n}_{seen[n]}")
        if abs(fp.GetOrientationDegrees() % 90.0) > 1e-6:
            absolute = [(pad, pcbnew.VECTOR2I(pad.GetPosition()), pad.GetOrientation()) for pad in pads]
            fp.SetOrientationDegrees(0)
            origin = fp.GetPosition()
            for pad, pos, orient in absolute:
                pad.SetFPRelativePosition(pcbnew.VECTOR2I(pos.x - origin.x, pos.y - origin.y))
                pad.SetOrientation(orient)
                if (pad.GetPosition() - pos).EuclideanNorm() > 10:
                    raise SystemExit(f"bake failed for {fp.GetReference()} pad {pad.GetNumber()}")
            baked += 1
    # Drop the copper pours so GND is routed as a normal net (guaranteed connectivity);
    # the pours are added on top afterwards.
    for z in list(board.Zones()):
        if not z.GetIsRuleArea():
            board.Remove(z)
    ok = pcbnew.ExportSpecctraDSN(board, str(dsn))
    pcbnew.SaveBoard(str(copy.with_name(copy.stem + "-baked.kicad_pcb")), board)   # for inspection only
    print("DSN export:", ok, dsn, "| rotated footprints baked:", baked)


# Tried and rejected (2026-11-07): a `.rules` file with per-layer preferred directions
# (F.Cu horizontal for the rows, B.Cu vertical for the columns, as on the Ferris and the
# Keyball) plus via_costs 200 and fanout off, passed with `-dr`. Freerouting honours the
# file - and then returns an almost empty session: 91 segments on 8 nets instead of 724.
# The rules file sits above the DSN in freerouting's precedence ladder, so it also replaces
# the net class widths and clearances the DSN carries, and the router gives up. Not worth
# re-deriving the whole class table in a second syntax: the board already comes out at
# 51 % horizontal on the front and 47 % vertical on the back, which is the convention the
# matrix geometry produces on its own.
def route(dsn: Path, ses: Path) -> int:
    jar = os.environ.get("FREEROUTING_JAR")
    jar = str(Path(jar).resolve()) if jar else None
    java = os.environ.get("JAVA", "java")
    passes = os.environ.get("FREEROUTING_PASSES", "30")
    if not jar or not Path(jar).exists():
        print("FREEROUTING_JAR not set or missing", file=sys.stderr)
        return 2
    if ses.exists():
        ses.unlink()
    # freerouting picks up a <board>.rules next to the DSN on its own, with a higher
    # priority than the DSN itself: a leftover one silently replaces the net classes and
    # the router then returns an almost empty session, or hangs.
    stale = dsn.with_suffix(".rules")
    if stale.exists():
        stale.unlink()
    cmd = [java, "-jar", jar, "-de", str(dsn), "-do", str(ses), "-mp", passes, "-l", "en", "-dct", "0"]
    res = subprocess.run(cmd, cwd=BUILD, capture_output=True, text=True, timeout=3600)
    print("\n".join(l for l in res.stdout.splitlines() if "Auto-routing stage completed" in l or "pre-existing" in l))
    if not ses.exists():
        print("freerouting produced no session file", file=sys.stderr)
        print(res.stderr[-3000:], file=sys.stderr)
        return 1
    return 0


def strip_placement(ses: Path) -> Path:
    """Drop the (placement ...) block: it carries the router copy's baked 0-degree rotations."""
    text = ses.read_text()
    start = text.find("(placement")
    if start < 0:
        return ses
    depth, i = 0, start
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    out = ses.with_name(ses.stem + "-noplace.ses")
    out.write_text(text[:start] + text[i + 1:])
    return out


def import_ses(pcb: Path, ses: Path) -> None:
    board = pcbnew.LoadBoard(str(pcb))
    ok = pcbnew.ImportSpecctraSES(board, str(strip_placement(ses)))
    print("SES import:", ok)
    pcbnew.SaveBoard(str(pcb), board)


def finish(pcb: Path) -> None:
    board = pcbnew.LoadBoard(str(pcb))
    pro = json.loads(pcb.with_suffix(".kicad_pro").read_text())
    widths = {c["name"]: c["track_width"] for c in pro["net_settings"]["classes"]}
    assignment = {p["pattern"]: p["netclass"] for p in pro["net_settings"].get("netclass_patterns", [])}
    fixed = 0
    for t in board.GetTracks():
        if t.GetClass() == "PCB_TRACK" and not t.IsLocked():
            mm = widths.get(assignment.get(t.GetNetname(), "Default"), widths["Default"])
            want = pcbnew.FromMM(mm)
            if t.GetWidth() < want:
                t.SetWidth(want)
                fixed += 1
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    rules = pro["board"]["design_settings"]["rules"]
    added = stitch_ground(board, hole_gap_mm=rules.get("min_hole_to_hole", 0.25))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(pcb), board)
    print("widened tracks:", fixed, "| GND stitching vias added:", added, "| saved", pcb)


def drop_floating_ground_vias(board) -> int:
    """Remove GND vias whose connected cluster contains no pad (they would only anchor islands)."""
    c = board.GetConnectivity()
    c.Build(board)
    removed = 0
    for v in list(board.GetTracks()):
        if v.GetClass() != "PCB_VIA" or v.GetNetname() != "GND" or v.IsLocked():
            continue
        if len(c.GetConnectedPads(v)) == 0:
            board.Remove(v)
            removed += 1
    return removed


def _point_to_segment(p, a, b) -> float:
    ax, ay, bx, by, px, py = a.x, a.y, b.x, b.y, p.x, p.y
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def stitch_ground(board, grid_mm: float = 6.0, via_mm: float = 0.6, drill_mm: float = 0.3, margin_mm: float = 0.3,
                  hole_gap_mm: float = 0.25) -> int:
    """Add GND vias on a grid wherever both pours have copper around the point.

    The pours already keep their clearance to every other net, so a via that sits fully
    inside both fills is clear of everything else and ties the two pours together. Copper
    clearance says nothing about drills on the same net, though: a router via that landed
    next to a grid point would leave two holes a fraction of a millimetre apart, which DRC
    reports as hole_to_hole and a drill may break. Such grid points are skipped.
    """
    import math

    gnd = board.GetNetsByName()["GND"]
    zones = {}
    for z in board.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != "GND":
            continue
        for layer in z.GetLayerSet().Seq():
            zones[layer] = z.GetFilledPolysList(layer)
    f, b = pcbnew.F_Cu, pcbnew.B_Cu
    if f not in zones or b not in zones:
        return 0
    holes = []
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            holes.append((p.x, p.y, t.GetDrill() / 2))
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            d = max(pad.GetDrillSizeX(), pad.GetDrillSizeY())
            if d > 0:
                p = pad.GetPosition()
                holes.append((p.x, p.y, d / 2))
    # Tracks of other nets: the pour keeps its clearance from them, but a grid point can still
    # land on one where the fill happens to reach around it. Copper to copper is the rule here.
    foreign = []
    for t in board.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        foreign.append((t.GetStart(), t.GetEnd(), t.GetWidth() / 2, t.GetNetname()))
    keep = pcbnew.FromMM(hole_gap_mm + drill_mm / 2)
    via_r = pcbnew.FromMM(via_mm / 2)
    clear = pcbnew.FromMM(0.2)
    bbox = board.GetBoardEdgesBoundingBox()
    r = pcbnew.FromMM(via_mm / 2 + margin_mm)
    step = pcbnew.FromMM(grid_mm)
    ring = [(int(r * math.cos(a)), int(r * math.sin(a))) for a in [k * math.pi / 4 for k in range(8)]]
    added = 0
    y = bbox.GetTop() + step // 2
    while y < bbox.GetBottom():
        x = bbox.GetLeft() + step // 2
        while x < bbox.GetRight():
            ok = all(zones[l].Contains(pcbnew.VECTOR2I(x + dx, y + dy)) for l in (f, b) for dx, dy in ring)
            if ok and any((x - hx) ** 2 + (y - hy) ** 2 < (keep + hr) ** 2 for hx, hy, hr in holes):
                ok = False
            if ok:
                pt = pcbnew.VECTOR2I(x, y)
                for ta, tb, hw, tnet in foreign:        # not a/b: those are the layer pair
                    if tnet == "GND":
                        continue
                    if _point_to_segment(pt, ta, tb) < via_r + hw + clear:
                        ok = False
                        break
            if ok:
                via = pcbnew.PCB_VIA(board)
                via.SetPosition(pcbnew.VECTOR2I(x, y))
                via.SetWidth(pcbnew.FromMM(via_mm))
                via.SetDrill(pcbnew.FromMM(drill_mm))
                via.SetLayerPair(f, b)
                via.SetNet(gnd)
                board.Add(via)
                added += 1
            x += step
        y += step
    return added


def main() -> int:
    args = sys.argv[1:]
    pcb = Path(args[1]) if len(args) > 1 else PCB
    BUILD.mkdir(exist_ok=True)
    dsn, ses = BUILD / (pcb.stem + ".dsn"), BUILD / (pcb.stem + ".ses")
    stage = args[0] if args else "all"
    if stage == "prepare":
        prepare(pcb)
    elif stage == "dsn":
        export_dsn(pcb, dsn)
    elif stage == "import":
        import_ses(pcb, ses)
    elif stage == "finish":
        finish(pcb)
    elif stage == "all":
        for st in ("prepare", "dsn"):
            subprocess.check_call([sys.executable, __file__, st, str(pcb)])
        rc = route(dsn, ses)
        if rc:
            return rc
        for st in ("import", "finish"):
            subprocess.check_call([sys.executable, __file__, st, str(pcb)])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
