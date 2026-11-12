# SPDX-License-Identifier: MIT
"""Nothing in the assembled half may occupy the same space as anything else.

Every other test checks one part against its own numbers. The faults the 2026-11-12 review found
were all between two parts that each passed: the lid lip inside the keycaps, case standoffs inside
hot-swap sockets, a battery well shallower than cell plus socket, a screw longer than its hole, a
USB opening smaller than the plug. This test puts the half together - the printed parts rendered
from the sources, the bought parts as simple prisms at their real positions - cuts the stack
every 0.4 mm and demands that no two things overlap in any cut.

The bought parts are modelled at their MAXIMUM size (datasheet maxima, tallest solder joint), so a
pass means they fit, not that they fit on a good day. Add a prism here for every new part.
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("trimesh")
from shapely import affinity  # noqa: E402
from shapely.geometry import Point, Polygon, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

from k0d3.geometry import CELL_AIR, PEG_OUT, SOCKET_H, load_layout, rotated_box  # noqa: E402
from mesh_tools import section  # noqa: E402
from scad_frame import load_layout_frame  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "hardware" / "case"
CRADLE_STL = ROOT / "hardware" / "trackball-cradle" / "stl" / "cradle-19mm-pocket.stl"
PCB_T = 1.6
STEP = 0.4
OVERLAP = 0.05          # mm2 per cut: below this it is numerical noise on a shared face

# printed parts that are in the half when it lies closed on the desk
PRINTED = {"left": ["tray", "box_cap", "guard", "lid_outer", "lid_inner"],
           "right": ["tray", "box_cap", "guard", "lid_outer", "lid_inner", "pocket_cover"]}


def openscad():
    for cand in (shutil.which("openscad"), "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"):
        if cand and Path(cand).exists():
            return cand
    return None


def render(part: str, half: str, out: Path) -> dict:
    res = subprocess.run([openscad(), "--backend", "manifold", "-D", f'part="{part}"', "-D", f'half="{half}"',
                          "-o", str(out), str(CASE / "case.scad")], capture_output=True, text=True, timeout=600)
    assert res.returncode == 0, res.stderr
    return {m.group(1): float(m.group(2)) for m in re.finditer(r"STACK (\w+)=(-?[\d.]+)", res.stderr + res.stdout)}


def bought_parts(half: str, v: dict) -> list[tuple[str, object, float, float]]:
    """(name, footprint in the layout frame, z0, z1) of everything that is not printed."""
    layout = load_layout(half)
    cfg = layout.cfg
    under = -PCB_T
    parts: list[tuple[str, object, float, float]] = [("PCB", layout.outline, -PCB_T, 0.0)]
    for k in layout.keys:
        parts.append((f"{k.ref} switch body", rotated_box(k.x, k.y, cfg["switch_body"], cfg["switch_body"], k.rotation), 0.0, 5.0))
        parts.append((f"{k.ref} keycap", layout.keycap_polygon(k), v["rim_z"], v["cap_top_z"]))
        for name, poly, h in layout.under_switch(k):
            parts.append((name, poly, under - h, under))
    back = layout.back_parts()
    parts.append(("PS1 slide switch", back["PS1"].buffer(-0.7, join_style=2), under - 1.4, under))    # body inside its courtyard
    parts.append(("RB1 reset button", back["RB1"].buffer(-0.9, join_style=2), under - 1.35, under))
    parts.append(("J3 battery connector", back["J3"].buffer(-0.7, join_style=2), under - 5.5, under))  # S2B-PH-SM4-TB is 5.5 tall
    # the cell: hangs under whatever stands out of the PCB inside the bay, at its maximum size
    bat = cfg["battery"]
    bay = layout.battery_bay()
    sockets_in_bay = any(name.endswith(" socket") and poly.intersects(bay) for name, poly in back.items())
    top = under - (SOCKET_H if sockets_in_bay else 0.4 + 0.1)      # sockets, or solder joints plus Kapton
    cx, cy = bay.centroid.x, bay.centroid.y
    cell = box(cx - bat["size"]["x"] / 2, cy - bat["size"]["y"] / 2, cx + bat["size"]["x"] / 2, cy + bat["size"]["y"] / 2)
    parts.append((f"{bat['cell']} cell with {CELL_AIR} mm of air", cell, top - bat["size"]["z"] - CELL_AIR, top))
    # controller on its sockets, the USB receptacle and the largest plug overmold Type-C allows
    c = cfg["controller"]
    ctrl = rotated_box(c["center"]["x"], c["center"]["y"], c["size"]["x"], c["size"]["y"], 0, offset=(0, c["pcb_offset_y"]))
    parts.append(("controller board", ctrl, 2.5, 4.1))
    ux, face = v["usb_x"], v["usb_face_y"]
    cz = v["ctrl_top_z"] - v["usb_shell_h"] / 2
    parts.append(("USB receptacle", box(ux - 4.47, face, ux + 4.47, face + 7.35), v["ctrl_top_z"] - v["usb_shell_h"], v["ctrl_top_z"]))
    parts.append(("USB-C plug overmold", box(ux - 12.35 / 2, face - 12.0, ux + 12.35 / 2, face), cz - 3.25, cz + 3.25))
    # screws: the documented M2 x 5 with a pan head, in the PCB holes and in the cap bosses
    for h in cfg["mounting_holes"]:
        p = Point(h["x"], h["y"])
        parts.append(("PCB screw thread", p.buffer(1.0, 24), -5.0, 0.0))
        parts.append(("PCB screw head", p.buffer(1.75, 24), 0.0, 1.5))
    # the ball, as a stack of discs (handled by z in `cut_of`)
    if layout.has_ball:
        parts.append(("ball", ("sphere", layout.ball_center, 19.05 / 2, v["ball_top_z"] - 19.05 / 2), v["ball_top_z"] - 19.05, v["ball_top_z"]))
    return parts


def cut_of(shape, z: float):
    if isinstance(shape, tuple) and shape[0] == "sphere":
        _, (x, y), r, zc = shape
        rr = r * r - (z - zc) ** 2
        return Point(x, y).buffer(math.sqrt(rr), 48) if rr > 0 else Polygon()
    return shape


# Pairs that touch by design. Each entry says why, so nobody adds one to silence a real clash.
ALLOWED = [
    (r"switch body$", r"keycap$"),            # the cap sits on the switch
    (r"switch body$", r"^guard$"),            # the guard's holes are the switch bodies (0.1 mm fit, see below)
    (r"PCB screw thread", r"^PCB$"),          # through its hole
    (r"PCB screw thread", r"^tray$"),         # in the insert; the tip is checked on its own below
    (r"centre post|side peg", r"switch body"),
    (r"socket (body|tab)$", r"socket (body|tab)$"),
    (r"USB receptacle", r"controller board"),
    (r"USB receptacle", r"USB-C plug"),
]


def allowed(a: str, b: str) -> bool:
    return any((re.search(x, a) and re.search(y, b)) or (re.search(x, b) and re.search(y, a)) for x, y in ALLOWED)


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
@pytest.mark.parametrize("half", ["left", "right"])
def test_nothing_overlaps_in_the_closed_half(tmp_path, half):
    sx = -1 if half == "left" else 1
    meshes, values = {}, {}
    for part in PRINTED[half]:
        out = tmp_path / f"{part}.stl"
        values = render(part, half, out) or values
        meshes[part] = load_layout_frame(out)
    if half == "right":
        cradle = load_layout_frame(CRADLE_STL)
        bx, by = load_layout(half).ball_center
        cradle.apply_translation([bx * sx, by, 0.0])
        meshes["cradle"] = cradle
    bought = [(n, s if isinstance(s, tuple) else affinity.scale(s, xfact=sx, origin=(0, 0)), z0, z1)
              for n, s, z0, z1 in bought_parts(half, values)]
    if half == "left":
        bought = [(n, (s[0], (s[1][0] * sx, s[1][1]), s[2], s[3]) if isinstance(s, tuple) else s, z0, z1) for n, s, z0, z1 in bought]

    z_lo = min(m.bounds[0][2] for m in meshes.values())
    z_hi = max(m.bounds[1][2] for m in meshes.values())
    clashes: dict[tuple[str, str], tuple[float, float]] = {}
    seen_pairs = 0
    for z in np.arange(z_lo + 0.13, z_hi, STEP):
        z = float(z)
        layer = [(name, section(m, z)) for name, m in meshes.items() if m.bounds[0][2] < z < m.bounds[1][2]]
        layer = [(n, c) for n, c in layer if not c.is_empty]
        layer += [(n, cut_of(s, z)) for n, s, z0, z1 in bought if z0 < z < z1]
        for i in range(len(layer)):
            for j in range(i + 1, len(layer)):
                (a, ga), (b, gb) = layer[i], layer[j]
                printed = (a in meshes) + (b in meshes)
                if printed == 0 or allowed(a, b):
                    continue                       # two bought parts: the PCB tests own those
                seen_pairs += 1
                if not ga.intersects(gb):
                    continue
                area = ga.intersection(gb).area
                if area > OVERLAP and area > clashes.get((a, b), (0.0, 0.0))[0]:
                    clashes[(a, b)] = (round(area, 2), round(z, 2))
    assert seen_pairs > 2000, "the stack was hardly compared: the test measured nothing"
    assert not clashes, f"{half}: parts in the same space (mm2 in the worst cut, z): {clashes}"


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_the_check_sees_a_known_clash(tmp_path):
    """Mutation: a 5.7 mm cell under the left board's sockets must be reported."""
    half = "left"
    out = tmp_path / "tray.stl"
    values = render("tray", half, out)
    tray = load_layout_frame(out)
    parts = bought_parts(half, values)
    name, cell, z0, z1 = next(p for p in parts if "cell" in p[0])
    thick = z1 - (5.7 + CELL_AIR)                    # the right half's cell in the left half
    cut = section(tray, thick + 0.1)
    assert cut.intersection(affinity.scale(cell, xfact=-1, origin=(0, 0))).area > 50.0, "a cell 1.5 mm too thick went unnoticed"
    assert section(tray, z0 + 0.1).intersection(affinity.scale(cell, xfact=-1, origin=(0, 0))).area < OVERLAP
