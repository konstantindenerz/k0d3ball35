#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write a 1:1 measuring sheet per half to build/print/<half>-check-1to1.pdf.

The 1:1 plots of `hw-main-pcb-review-r1` step 2 are meant to be checked with real parts laid
on them. Without parts in hand the same sheet still answers two questions a ruler can settle:
is the print really 1:1, and does the generated geometry carry the numbers the layout promises
(key pitch, controller hole pattern, battery bay, board size, ball pocket).

Everything drawn here comes from `hardware/layout/k0d3ball35.yaml` and the footprint library
through `load_layout` / `nice_nano_tht`, and every dimension label is computed, never typed, so
a stale number cannot survive. What this sheet cannot do is validate a footprint against a real
part: socket, switch, connector and controller pads need the parts and the plot of the board
underside (see the ticket).

Usage: scripts/gen_print_check.py [left|right ...]
"""
from __future__ import annotations

import datetime
import math
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

from k0d3.footprints import nice_nano_tht
from k0d3.geometry import HALVES, REPO, Layout, load_layout, octagon

PAGE = (210.0, 297.0)          # A4 portrait, in millimetres; one SVG user unit is 1 mm
MARGIN_X = 20.0
BOARD_TOP = 36.0
MOUNT_HOLE_D = 2.2             # footprints.mounting_hole, M2 clearance
OUT = REPO / "build" / "print"

C_CAL = "#D62728"              # calibration: everything else depends on it
C_BOARD = "#1F77B4"
C_GRID = "#2CA02C"
C_CTRL = "#E8762E"
C_BATT = "#8E44AD"
C_BALL = "#17A2B8"
INK = "#111111"
GHOST = "#B9B2A4"


@dataclass
class Dim:
    """One line of the legend: what to measure, its nominal value and its colour on the board."""
    name: str
    value: float
    colour: str


# ----------------------------------------------------------------- tiny SVG writer
class Sheet:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def path(self, d: str, stroke: str = INK, width: float = 0.25, fill: str = "none", dash: str = "") -> None:
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{da}/>')

    def poly(self, pts, **kw) -> None:
        self.path("M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in pts) + " Z", **kw)

    def circle(self, x: float, y: float, d: float, stroke: str = INK, width: float = 0.25, fill: str = "none") -> None:
        self.add(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{d / 2:.3f}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{width}"/>')

    def text(self, x: float, y: float, s: str, size: float = 2.8, fill: str = INK,
             anchor: str = "start", weight: str = "normal") -> None:
        self.add(f'<text x="{x:.3f}" y="{y:.3f}" font-family="Helvetica,Arial,sans-serif" '
                 f'font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>')

    def label(self, x: float, y: float, s: str, colour: str, size: float = 2.8, anchor: str = "middle") -> None:
        """Bold text on a white patch, so a dimension stays readable over the drawing."""
        w = len(s) * size * 0.56
        x0 = {"middle": x - w / 2, "end": x - w, "start": x}[anchor]
        self.add(f'<rect x="{x0 - 0.6:.3f}" y="{y - size * 0.82:.3f}" width="{w + 1.2:.3f}" '
                 f'height="{size * 1.12:.3f}" fill="#FFFFFF"/>')
        self.text(x, y, s, size=size, fill=colour, anchor=anchor, weight="bold")

    def render(self) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE[0]}mm" height="{PAGE[1]}mm" '
                f'viewBox="0 0 {PAGE[0]} {PAGE[1]}">\n'
                f'<rect width="{PAGE[0]}" height="{PAGE[1]}" fill="#FFFFFF"/>\n'
                + "\n".join(self.parts) + "\n</svg>\n")


def mm(value: float) -> str:
    return f"{value:.2f} mm".replace(".00 mm", ".0 mm")


def stamp() -> str:
    """Short commit and date for the sheet's corner: a printout on the desk has to say which
    state of the repository it came from. `-dirty` marks uncommitted changes, so a sheet made
    from work in progress can never be mistaken for one made from a commit."""
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                              check=True).stdout.strip()

    try:
        rev = git("rev-parse", "--short", "HEAD")
        if git("status", "--porcelain"):
            rev += "-dirty"
    except (subprocess.CalledProcessError, FileNotFoundError):
        rev = "no commit"
    return f"{rev}  ·  {datetime.date.today().isoformat()}"


def dim_h(s: Sheet, x1: float, x2: float, y: float, label: str, colour: str) -> None:
    """Horizontal dimension line with end ticks; the label sits on the line in a white patch."""
    t = 1.5
    s.path(f"M {x1:.3f},{y - t:.3f} L {x1:.3f},{y + t:.3f} M {x2:.3f},{y - t:.3f} L {x2:.3f},{y + t:.3f} "
           f"M {x1:.3f},{y:.3f} L {x2:.3f},{y:.3f}", stroke=colour, width=0.3)
    s.label((x1 + x2) / 2, y + 1.0, label, colour)


def dim_v(s: Sheet, y1: float, y2: float, x: float, label: str, colour: str, side: int = 1) -> None:
    t = 1.5
    s.path(f"M {x - t:.3f},{y1:.3f} L {x + t:.3f},{y1:.3f} M {x - t:.3f},{y2:.3f} L {x + t:.3f},{y2:.3f} "
           f"M {x:.3f},{y1:.3f} L {x:.3f},{y2:.3f}", stroke=colour, width=0.3)
    s.label(x + 2.2 * side, (y1 + y2) / 2 + 1.0, label, colour, anchor="start" if side > 0 else "end")


# ----------------------------------------------------------------- the sheet
def build(layout: Layout) -> tuple[str, list[Dim]]:
    s = Sheet()
    cfg = layout.cfg
    sx = layout.board_sx
    ring = [(sx * x, y) for x, y in layout.outline.exterior.coords]
    min_x, min_y = min(x for x, _ in ring), min(y for _, y in ring)
    width = max(x for x, _ in ring) - min_x
    height = max(y for _, y in ring) - min_y
    ox, oy = MARGIN_X - min_x, BOARD_TOP - min_y

    def P(x: float, y: float) -> tuple[float, float]:
        """Layout point to page point (board top view; the left half is mirrored in x)."""
        return (ox + sx * x, oy + y)

    dims: list[Dim] = []

    # ---- header
    s.text(MARGIN_X, 14, f"{cfg['name']} {cfg['revision']} - {layout.half} half, 1:1 measuring sheet",
           size=5.0, weight="bold")
    s.text(PAGE[0] - MARGIN_X, 14, stamp(), size=3.0, fill=GHOST, anchor="end")
    s.text(MARGIN_X, 20, "Top view, keys up. Print at 100 %: no “fit to page”, no scaling. Measure the "
                         "red bars first - if they are off, nothing else counts.", size=3.0)
    s.text(MARGIN_X, 24.5, "A steel ruler reads to about 0.5 mm, so the sheet only asks for long distances. "
                           "Every value is generated from the layout file.", size=3.0)

    # ---- the board itself: outline solid, everything a part would cover in grey
    s.poly([P(x, y) for x, y in layout.outline.exterior.coords], stroke=INK, width=0.4)
    kw, kh = layout.keycap
    body = cfg["switch_body"]
    for k in layout.keys:
        th = math.radians(-k.rotation * sx)
        px, py = P(k.x, k.y)
        for w, h in ((kw, kh), (body, body)):
            s.poly([(px + dx * math.cos(th) - dy * math.sin(th), py + dx * math.sin(th) + dy * math.cos(th))
                    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))],
                   stroke=GHOST, width=0.2)
        s.circle(px, py, 3.4, stroke=GHOST, width=0.25)
    holes = cfg["mounting_holes"]
    for h in holes:
        s.circle(*P(h["x"], h["y"]), MOUNT_HOLE_D, stroke=INK, width=0.3)

    # ---- board outline, measured over the bounding box
    dim_h(s, MARGIN_X, MARGIN_X + width, BOARD_TOP - 6, mm(width), C_BOARD)
    dim_v(s, BOARD_TOP, BOARD_TOP + height, MARGIN_X + width + 8, mm(height), C_BOARD)
    dims.append(Dim("Board outline, widest point across", round(width, 2), C_BOARD))
    dims.append(Dim("Board outline, tallest point down", round(height, 2), C_BOARD))

    # ---- key grid: the longest straight runs on the board, measured centre to centre
    row = sorted([k for k in layout.keys if k.kind == "finger" and k.row == 0], key=lambda k: k.x)
    col = sorted([k for k in layout.keys if k.kind == "finger" and k.col == 2], key=lambda k: k.y)
    gx, gy = abs(row[-1].x - row[0].x), abs(col[-1].y - col[0].y)
    dim_h(s, P(row[0].x, 0)[0], P(row[-1].x, 0)[0], P(0, row[0].y)[1],
          f"{mm(gx)} = {len(row) - 1} x {layout.pitch[0]:g}", C_GRID)
    for k in (row[0], row[-1]):   # the keys the line is taken from do not share a y (column stagger)
        px = P(k.x, 0)[0]
        s.path(f"M {px:.3f},{P(0, row[0].y)[1]:.3f} L {px:.3f},{P(0, k.y)[1]:.3f}", stroke=C_GRID,
               width=0.15, dash="1 1")
    dim_v(s, P(0, col[0].y)[1], P(0, col[-1].y)[1], P(col[0].x, 0)[0],
          f"{mm(gy)} = {len(col) - 1} x {layout.pitch[1]:g}", C_GRID)
    dims.append(Dim(f"Row 0, pinky to inner key centre ({len(row) - 1} x {layout.pitch[0]:g} mm pitch)",
                    round(gx, 2), C_GRID))
    dims.append(Dim(f"Middle column, top to bottom key centre ({len(col) - 1} x {layout.pitch[1]:g} mm)",
                    round(gy, 2), C_GRID))

    # ---- controller hole pattern, straight from the footprint the PCB uses
    c = cfg["controller"]
    pads = nice_nano_tht({h: "" for h in range(1, 25)}).pads
    xs = sorted({round(p.x, 3) for p in pads})
    ys = sorted({round(p.y, 3) for p in pads})
    rows, span = xs[-1] - xs[0], ys[-1] - ys[0]
    cx, cy = c["center"]["x"], c["center"]["y"]
    for p in pads:
        s.circle(*P(cx + p.x, cy + p.y), p.drill, stroke=C_CTRL, width=0.25)
    dim_h(s, P(cx + xs[0], 0)[0], P(cx + xs[-1], 0)[0], P(0, cy + ys[0])[1] - 4.0, mm(rows), C_CTRL)
    # the span label goes outside the board: between the hole rows it would sit on the battery bay
    dim_v(s, P(0, cy + ys[0])[1], P(0, cy + ys[-1])[1], P(cx + xs[0], 0)[0], mm(span), C_CTRL, side=-sx)
    dims.append(Dim("Controller hole rows, centre to centre", round(rows, 2), C_CTRL))
    dims.append(Dim(f"Controller row, first to last hole ({len(ys) - 1} x {c['pin_pitch']:g} mm)",
                    round(span, 2), C_CTRL))

    # ---- battery bay (dashed on the back silkscreen; the cell goes under the board here)
    bay = cfg["battery"]["bay"]
    s.poly([P(x, y) for x, y in layout.battery_bay().exterior.coords], stroke=C_BATT, width=0.35, dash="2 1.5")
    bw, bh = bay["size"]["x"], bay["size"]["y"]
    bcx, bcy = bay["center"]["x"], bay["center"]["y"]
    dim_h(s, P(bcx - bw / 2, 0)[0], P(bcx + bw / 2, 0)[0], P(0, bcy + bh / 2)[1] + 4.0, mm(bw), C_BATT)
    dim_v(s, P(0, bcy - bh / 2)[1], P(0, bcy + bh / 2)[1], P(bcx + bw / 2 * sx, 0)[0], mm(bh), C_BATT, side=sx)
    dims.append(Dim(f"Battery bay (dashed), across the {cfg['battery']['cell']}", round(bw, 2), C_BATT))
    dims.append(Dim("Battery bay, along the cell", round(bh, 2), C_BATT))

    # ---- mounting holes: the pair sharing a column is a clean straight run
    h1, h2 = holes[0], holes[1]
    dim_v(s, P(0, h1["y"])[1], P(0, h2["y"])[1], P(h1["x"], 0)[0], mm(abs(h2["y"] - h1["y"])), C_BOARD, side=sx)
    dims.append(Dim("Mounting holes 1 and 2 (same column), centre to centre",
                    round(abs(h2["y"] - h1["y"]), 2), C_BOARD))

    # ---- ball pocket (right half only)
    if layout.has_ball:
        bx, by = layout.ball_center
        tb = cfg["trackball"]
        apothem = tb["cradle_diameter"] / 2 + tb["pocket"]["notch_clearance"]
        ball_d = tb["ball_diameter"]
        s.poly([P(x, y) for x, y in octagon(bx, by, apothem).exterior.coords], stroke=C_BALL, width=0.3)
        s.circle(*P(bx, by), ball_d, stroke=C_BALL, width=0.35)
        dim_h(s, P(bx - apothem, 0)[0], P(bx + apothem, 0)[0], P(0, by + apothem)[1] - 2.0,
              mm(2 * apothem), C_BALL)
        dim_v(s, P(0, by - ball_d / 2)[1], P(0, by + ball_d / 2)[1], P(bx, 0)[0], mm(ball_d), C_BALL)
        dims.append(Dim("Notch octagon, across the flats", round(2 * apothem, 2), C_BALL))
        dims.append(Dim(f"Ball circle ({ball_d:g} mm POM ball)", round(ball_d, 2), C_BALL))

    # ---- calibration bars
    y = BOARD_TOP + height + 16.0
    s.text(MARGIN_X, y, "1  Calibration - measure these two first", size=3.6, weight="bold", fill=C_CAL)
    y += 9
    s.path(f"M {MARGIN_X:.3f},{y:.3f} L {MARGIN_X + 100:.3f},{y:.3f}", stroke=C_CAL, width=0.4)
    for i in range(11):
        x = MARGIN_X + i * 10
        long = i % 5 == 0
        s.path(f"M {x:.3f},{y - (3.2 if long else 1.6):.3f} L {x:.3f},{y:.3f}", stroke=C_CAL,
               width=0.4 if long else 0.25)
        if long:
            s.text(x, y - 4.2, f"{i * 10}", size=2.6, fill=C_CAL, anchor="middle")
    s.text(MARGIN_X + 103, y + 1.0, "100.0 mm", size=3.2, fill=C_CAL, weight="bold")

    # ---- legend, with the vertical calibration bar running beside it
    y += 10
    s.text(MARGIN_X, y, "2  What to measure on the board above", size=3.6, weight="bold")
    y += 6.0
    vbar_top = y - 3
    for d in dims:
        s.add(f'<rect x="{MARGIN_X:.2f}" y="{y - 2.4:.2f}" width="3" height="3" fill="{d.colour}"/>')
        s.text(MARGIN_X + 5, y, d.name, size=3.0)
        s.text(MARGIN_X + 118, y, mm(d.value), size=3.0, anchor="end", weight="bold")
        s.text(MARGIN_X + 122, y, "measured: . . . . . . . . mm", size=3.0, fill=GHOST)
        y += 5.2
    vx = MARGIN_X + 166
    s.path(f"M {vx:.3f},{vbar_top:.3f} L {vx:.3f},{vbar_top + 50:.3f}", stroke=C_CAL, width=0.4)
    for dy in (0, 50):
        s.path(f"M {vx - 2.5:.3f},{vbar_top + dy:.3f} L {vx + 2.5:.3f},{vbar_top + dy:.3f}", stroke=C_CAL, width=0.4)
    s.text(vx, vbar_top - 2.5, "50.0 mm", size=3.2, fill=C_CAL, anchor="middle", weight="bold")

    # ---- what the sheet does not answer
    y += 4
    s.text(MARGIN_X, y, "3  What this sheet cannot tell you", size=3.6, weight="bold")
    y += 5.6
    for para in (
        "Tolerance: a ruler reads to about 0.5 mm. Anything inside that is fine. A systematic error of a "
        "few per cent is a printer scaling problem, not a layout one - fix the print and measure again.",
        "Part footprints are NOT checked here. Pad shapes and hole patterns of the hot-swap socket, the "
        "switch, the FH12-6S and the slide switch need the real parts laid on the plot of the board "
        f"underside, build/print/{layout.half}-bottom-1to1.pdf (step 2 of issues/hw-main-pcb-review-r1.md).",
        f"The grey squares are the keycap ({kw:g} x {kh:g}) and the switch body ({body:g}). Put your hand "
        + ("on the sheet: the thumb should reach the ball circle without the wrist moving. That is the one "
           "judgement worth making before any board is ordered."
           if layout.has_ball else
           "on the sheet and check that every key is within reach; print the right half as well to see "
           "the thumb against the ball circle."),
    ):
        for line in textwrap.wrap(para, 108):
            s.text(MARGIN_X, y, line, size=2.8)
            y += 4.0
        y += 1.2

    return s.render(), dims


def write(half: str) -> Path:
    import cairosvg

    svg, _ = build(load_layout(half))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{half}-check-1to1.svg").write_text(svg)
    pdf = OUT / f"{half}-check-1to1.pdf"
    # dpi=72 makes one SVG user unit one PDF point, so "210mm" on the page really is 210 mm
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(pdf), dpi=72)
    return pdf


def main(argv: list[str]) -> int:
    for half in (argv or list(HALVES)):
        print("wrote", write(half).relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
