#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write a 1:1 part-check plot per half and face to build/print/<half>-{bottom,top}-1to1.pdf.

This is step 2b of `issues/hw-main-pcb-review-r1.md`: the sheet you lay a real hot-swap socket,
slide switch or FFC connector on to see whether its legs land on their pads. The companion
measuring sheet (`gen_print_check.py`) answers the ruler questions and deliberately draws no
footprints; this one draws nothing but footprints.

Why a script and not `kicad-cli pcb export pdf` on its own, as the ticket used to suggest: the
generated boards carry `(paper "A3")`, so every exported PDF is 420 x 297 mm and an A4 printer
either scales it - which destroys the one property the sheet needs - or clips it. Only the SVG
exporter has `--page-size-mode 2` ("board area only"), so the board is plotted bare and re-paged
onto A4 here, at 1:1, with the calibration bar and the commit stamp the other sheet already uses.
`--sketch-pads-on-fab-layers` is what makes the plot usable: pads come out as outlines with their
numbers instead of the solid copper flood a `B.Cu` plot puts over the whole board.

Reference designators live on F.Fab in this project, so on the mirrored back plot KiCad would
print them in mirror writing. They are drawn here from the layout instead - the same source the
rest of the sheet family uses - for the handful of parts the review step actually sends you
hunting for.

Usage: scripts/gen_print_plots.py [left|right ...]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from gen_print_check import C_CAL, GHOST, INK, MARGIN_X, OUT, PAGE, Sheet, mm, stamp
from k0d3.geometry import HALVES, LAYOUT_FILE, REPO, Layout, load_layout

BOARD_TOP = 30.0               # below the header, above the calibration bar
KICAD_CLI = os.environ.get("KICAD_CLI", "kicad-cli")

LAYERS = {"bottom": "B.Fab,B.SilkS,Edge.Cuts", "top": "F.Fab,F.SilkS,Edge.Cuts"}


def export_svg(pcb: Path, face: str, dest: Path) -> None:
    """Plot one face of the board, bare, at 1:1, with the page cropped to the board."""
    cmd = [KICAD_CLI, "pcb", "export", "svg", "--layers", LAYERS[face],
           "--sketch-pads-on-fab-layers", "--black-and-white", "--page-size-mode", "2",
           "--exclude-drawing-sheet", "--drill-shape-opt", "2", "--mode-single", "--scale", "1",
           "-o", str(dest), str(pcb)]
    if face == "bottom":
        cmd.insert(-3, "--mirror")
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def svg_box(svg: str) -> tuple[float, float]:
    """Width and height of a KiCad SVG in millimetres.

    The whole sheet is 1:1 or it is worthless, so a unit that is not millimetres, a viewBox that
    disagrees with the declared size, or a missing header is an error rather than a guess.
    """
    m = re.search(r'width="([\d.]+)(\w*)"\s+height="([\d.]+)(\w*)"\s+viewBox="([-\d.\s]+)"', svg)
    if not m:
        raise ValueError("no width/height/viewBox in the SVG header")
    w, wu, h, hu, box = float(m.group(1)), m.group(2), float(m.group(3)), m.group(4), m.group(5)
    if (wu, hu) != ("mm", "mm"):
        raise ValueError(f"expected millimetres in the SVG header, got {wu!r} and {hu!r}")
    vb = [float(v) for v in box.split()]
    if len(vb) != 4 or abs(vb[2] - w) > 1e-3 or abs(vb[3] - h) > 1e-3:
        raise ValueError(f"viewBox {vb} does not match the {w} x {h} mm page: the plot is not 1:1")
    return w, h


def svg_body(svg: str) -> str:
    """The KiCad drawing without its own <svg> wrapper, ready to be placed in a group."""
    start = svg.index(">", svg.index("<svg")) + 1
    return svg[start:svg.rindex("</svg>")]


def part_points(layout: Layout, face: str) -> list[tuple[str, float, float]]:
    """Board-frame points for the parts this face sends the reader looking for.

    A label on a face the part is not mounted on would be worse than none: J1 moved to the key
    side in r2.2, so on the back plot there is nothing under a `J1` ring but bare laminate. The
    hot-swap sockets and PS1 sit on the back; U1 is through-hole and shows on both.
    """
    cfg = layout.cfg
    pts: list[tuple[str, float, float]] = [
        ("U1", cfg["controller"]["center"]["x"], cfg["controller"]["center"]["y"])]
    if face == "bottom":
        pts += [(k.ref, k.x, k.y) for k in layout.thumbs]
        corner = min(layout.keys, key=lambda k: (k.row, k.col))
        pts.append((corner.ref, corner.x, corner.y))
        pts.append(("PS1", cfg["power_switch"]["center"]["x"], cfg["power_switch"]["center"]["y"]))
    if cfg.get("fpc") and layout.fpc_side == face:
        pts.append(("J1", cfg["fpc"]["center"]["x"], cfg["fpc"]["center"]["y"]))
    return [(ref, *layout.to_board(x, y)) for ref, x, y in pts]


def build(layout: Layout, face: str, plot: str) -> str:
    """Wrap one KiCad plot in an A4 page: header, stamp, the board at 1:1, calibration bar."""
    w, h = svg_box(plot)
    ring = [layout.to_board(x, y) for x, y in layout.outline.exterior.coords]
    min_bx, min_by = min(x for x, _ in ring), min(y for _, y in ring)
    ox, oy = MARGIN_X, BOARD_TOP

    def P(bx: float, by: float) -> tuple[float, float]:
        """Board point to page point. The back plot is mirrored, so x runs the other way."""
        x = (w - (bx - min_bx)) if face == "bottom" else (bx - min_bx)
        return (ox + x, oy + by - min_by)

    s = Sheet()
    cfg = layout.cfg
    side = "back, as seen from behind the board" if face == "bottom" else "front"
    s.text(MARGIN_X, 14, f"{cfg['name']} {cfg['revision']} - {layout.half} half, {face} side, "
           "1:1 part check", size=5.0, weight="bold")
    s.text(PAGE[0] - MARGIN_X, 14, stamp(), size=3.0, fill=GHOST, anchor="end")
    s.text(MARGIN_X, 20, f"{LAYERS[face]}, {side}. Print at 100 %: no “fit to page”, no scaling.",
           size=3.0)
    s.text(MARGIN_X, 24.5, "Measure the bar below, then lay the real part on its pads. Pads are "
           "outlines with their numbers, filled circles are drill holes.", size=3.0, fill=GHOST)

    # the plot's own origin is already the board's bounding-box corner (--page-size-mode 2), so it
    # only needs the page offset; P() adds min_bx/min_by because it starts from board coordinates
    s.add(f'<g transform="translate({ox:.4f},{oy:.4f})">{svg_body(plot)}</g>')

    for ref, bx, by in part_points(layout, face):
        px, py = P(bx, by)
        s.circle(px, py, 7.0, stroke=C_CAL, width=0.3)
        s.label(px, py - 4.6, ref, C_CAL, size=3.0)

    y = BOARD_TOP + h + 14.0
    s.text(MARGIN_X, y, "Calibration - measure this before anything else", size=3.6,
           weight="bold", fill=C_CAL)
    y += 9
    s.path(f"M {MARGIN_X:.3f},{y:.3f} L {MARGIN_X + 100:.3f},{y:.3f}", stroke=C_CAL, width=0.4)
    for i in range(11):
        x = MARGIN_X + i * 10
        long = i % 5 == 0
        s.path(f"M {x:.3f},{y - (3.2 if long else 1.6):.3f} L {x:.3f},{y:.3f}", stroke=C_CAL,
               width=0.4 if long else 0.25)
    s.text(MARGIN_X + 103, y + 1.0, "100.0 mm", size=3.2, fill=C_CAL, weight="bold")
    y += 7
    s.text(MARGIN_X, y, f"Cross-check: the board measures {mm(w)} across and {mm(h)} down, the "
           f"same as the measuring sheet ({layout.half}-check-1to1.pdf).", size=3.0, fill=INK)
    return s.render()


def write(half: str, face: str, source: Path = LAYOUT_FILE) -> Path:
    layout = load_layout(half, source)
    pcb = REPO / "hardware" / f"{half}-pcb" / f"k0d3ball35-{half}.kicad_pcb"
    OUT.mkdir(parents=True, exist_ok=True)
    raw = OUT / f"{half}-{face}-plot.svg"
    export_svg(pcb, face, raw)
    svg = build(layout, face, raw.read_text())
    (OUT / f"{half}-{face}-1to1.svg").write_text(svg)
    pdf = OUT / f"{half}-{face}-1to1.pdf"
    import cairosvg                       # optional dependency, like the measuring sheet

    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(pdf), dpi=72)
    return pdf


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("halves", nargs="*", default=list(HALVES), choices=list(HALVES))
    ap.add_argument("--layout", type=Path, default=LAYOUT_FILE,
                    help="read another layout yaml instead of the committed one")
    args = ap.parse_args(argv)
    for half in args.halves or HALVES:
        for face in ("bottom", "top"):
            print("wrote", write(half, face, args.layout).relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
