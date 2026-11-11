# SPDX-License-Identifier: MIT
"""The PCB guard (hardware/case, part "guard"): a 0.8 mm plate lying on the PCB top between the
switches, like the cover plate of the Keyball39. It must not make the half taller, so it lives
in the air under a pressed keycap; it must be one piece without webs too thin to print, and it
must stay clear of everything that sits on the PCB top or has to stay reachable: the switch
housings, the PCB screw heads, the controller box, J1 and the FFC, the cradle opening.

The outline is generated (scripts/gen_case.py guard_polygon) into data.scad; these tests read it
from there and check the exported STL and DXF against it.
"""
from __future__ import annotations

import math
import re

import pytest
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from k0d3.geometry import load_layout
from scad_frame import load_layout_frame, layout_y
from test_case import CASE, DATA, parse_data

PARAMS = (CASE / "params.scad").read_text()
HALVES = ("left", "right")
M2_HEAD_D = 3.5          # PCB screw heads, max diameter (spec/03-bom.md)


def param(name: str) -> float:
    return float(re.search(rf"^{name}\s*=\s*(-?[\d.]+);", PARAMS, re.M)[1])


@pytest.fixture(scope="module")
def data():
    return parse_data(DATA.read_text())


def guard_of(data, half) -> Polygon:
    rings = data["guard"][half]
    return Polygon(rings[0], rings[1:])


def key_square(k, side) -> Polygon:
    x, y, rot = k
    a = math.radians(-rot)
    c, s = math.cos(a), math.sin(a)
    h = side / 2
    return Polygon([(x + px * c - py * s, y + px * s + py * c) for px, py in ((-h, -h), (h, -h), (h, h), (-h, h))])


def test_no_extra_height(stack):
    """The guard fills air that is already there: the keycap top, the rim and the lid stay where
    they were, and a pressed keycap keeps guard_min_air over the guard."""
    for half in HALVES:
        s = stack[half]
        pressed = s["cap_skirt_z"] - s["switch_travel"]
        assert s["guard_top_z"] == pytest.approx(param("guard_t"))
        assert pressed - s["guard_top_z"] >= param("guard_min_air") - 1e-6
        assert s["guard_air"] == pytest.approx(pressed - s["guard_top_z"])
        assert s["guard_top_z"] < s["rim_z"] and s["lid_top_z"] == pytest.approx(17.5)
    # the skirt the guard is measured against is the one the keycap dummy and the rim use
    assert param("cap_skirt_z") == param("rim_z")


@pytest.fixture(scope="module")
def stack():
    import json
    return json.loads((CASE / "stack.json").read_text())["variants"]


@pytest.mark.parametrize("half", HALVES)
def test_one_piece_without_thin_webs(data, half):
    g = guard_of(data, half)
    assert g.is_valid and g.geom_type == "Polygon"
    web = param("guard_min_web")
    # every part of it holds a disc of the minimum web: eroding by a hair less keeps one piece
    core = g.buffer(-(web / 2 - 0.05))
    assert core.geom_type == "Polygon", f"{half}: a web narrower than {web} mm splits the guard"
    assert g.area > 1500, f"{half}: guard area {g.area:.0f} mm2"


@pytest.mark.parametrize("half", HALVES)
def test_stays_on_the_pcb_and_off_the_switches(data, half):
    g = guard_of(data, half)
    layout = load_layout(half)
    assert layout.outline.buffer(0.02).contains(g)      # simplify(0.01) in the generator
    fit = param("guard_fit")
    for k in data["keys"][half]:
        housing = key_square(k, param("switch_lower") + 2 * fit - 0.02)
        assert not g.intersects(housing), f"{half}: guard on the switch housing at {k}"
        # held down by the switch flange: the guard reaches under it on some side of every key
        flange = key_square(k, 15.0)
        assert g.intersects(flange), f"{half}: nothing of the guard under the flange at {k}"


@pytest.mark.parametrize("half", HALVES)
def test_covers_the_webs_between_the_keys(data, half):
    """The point of the part: the PCB between two neighbouring keys of a column is covered."""
    g = guard_of(data, half)
    keys = data["keys"][half]
    pairs = 0
    for a in keys:
        for b in keys:
            if a[2] == 0 and b[2] == 0 and a[0] == b[0] and 16 < b[1] - a[1] < 18:
                mid = Point(a[0], (a[1] + b[1]) / 2)
                if min(Point(h).distance(mid) for h in data["holes"][half]) > param("guard_screw_d"):
                    assert g.contains(mid), f"{half}: web between {a} and {b} not covered"
                    pairs += 1
    assert pairs >= 6


@pytest.mark.parametrize("half", HALVES)
def test_keeps_off_screws_box_j1_and_cradle(data, half):
    g = guard_of(data, half)
    assert param("guard_screw_d") >= M2_HEAD_D + 0.15, "screw head holes too tight for the BOM heads"
    for h in data["holes"][half]:
        assert not g.intersects(Point(h).buffer(M2_HEAD_D / 2 + 0.05)), f"{half}: guard under the screw head at {h}"
    # inside the controller box only under the cap skirt (2 mm wide bands along the key side and
    # the thumb side), never on the controller
    x0, y0, x1, y1 = data["box_rect"][half]
    t = param("box_skirt_t")
    inner = box(x0, y0, x1 - t, y1 - t)
    assert not g.intersects(inner), f"{half}: guard inside the controller box"
    assert not g.intersects(box(*data["ctrl_rect"][half])), f"{half}: guard on the controller"
    assert g.intersects(box(x1 - t, y0, x1, y1)), f"{half}: guard does not run on under the cap skirt"
    if data["has_ball"][half]:
        assert not g.intersects(j1_parts(half)), "guard on J1 or its contacts"
        assert not g.intersects(Polygon(data["cable_corridor"][half])), "guard on the FFC path"
        assert not g.intersects(Point(data["ball_center"][half]).buffer(param("cradle_d") / 2)), "guard over the cradle"


def j1_parts(half):
    """J1 body (F.Fab 8.6 x 4.8) and the contact tails in front of it, checked against the KiCad
    footprint's own pads and fab outline in test_j1_outline_matches_the_footprint."""
    d = parse_data(DATA.read_text())
    return unary_union([Polygon(d["fpc_body"][half]), Polygon(d["fpc_tails"][half])])


def test_j1_outline_matches_the_footprint():
    """fpc_body / fpc_tails in data.scad against J1 on the routed right board: the fab rectangle
    contains no pad of the signal row, the tails rectangle contains all six signal pads."""
    import re as _re
    pcb = (CASE.parents[1] / "hardware" / "right-pcb" / "k0d3ball35-right.kicad_pcb").read_text()
    m = _re.search(r'\(footprint "[^"]*FH12-6S_top"(.*?)\n\t\)', pcb, _re.S)
    assert m, "J1 not on the right board"
    at = _re.search(r"\(at (-?[\d.]+) (-?[\d.]+)(?: (-?[\d.]+))?\)", m.group(1))
    jx, jy, jr = float(at[1]), float(at[2]), float(at[3] or 0)
    pads = [(float(p[1]), float(p[2])) for p in _re.finditer(r'\(pad "[1-6]" smd rect\s*\(at (-?[\d.]+) (-?[\d.]+)', m.group(1))]
    assert len(pads) == 6
    d = parse_data(DATA.read_text())
    body, tails = Polygon(d["fpc_body"]["right"]), Polygon(d["fpc_tails"]["right"])
    lay = load_layout("right").cfg["fpc"]["center"]
    a = math.radians(jr)
    for px, py in pads:
        # KiCad pad offset (y down, rotation counter-clockwise on screen) -> layout frame
        dx, dy = px * math.cos(a) + py * math.sin(a), -px * math.sin(a) + py * math.cos(a)
        p = Point(lay["x"] + dx, lay["y"] + dy)
        assert tails.contains(p) and not body.contains(p), (px, py)


@pytest.mark.parametrize("half", HALVES)
def test_no_bare_pcb_from_above(data, half):
    """Seen from above, the PCB is covered by keycaps, guard, controller box, J1, the screw heads
    and the pocket cover. What may still show is a fit gap (guard_fit at most), never a strip:
    the first guard left 43 mm2 of green beside J1, the thumb screw and the box."""
    pcb = load_layout(half).outline
    caps = unary_union([rot_cap(k) for k in data["keys"][half]])      # 17.5 x 16.5 MBK caps
    x0, y0, x1, y1 = data["box_rect"][half]
    cover = [box(x0, y0, x1, y1), guard_of(data, half)]
    cover += [Point(h).buffer(M2_HEAD_D / 2) for h in data["holes"][half]]
    if data["has_ball"][half]:
        cover += [j1_parts(half), box(*data["cover_rect"][half]), Polygon(data["cable_corridor"][half])]
    bare = pcb.difference(unary_union([caps, *cover]))
    wide = bare.buffer(-(param("guard_fit") / 2 + 0.03))
    assert wide.is_empty, f"{half}: bare PCB visible at {[tuple(round(b, 1) for b in p.bounds) for p in getattr(wide, 'geoms', [wide])]}"


def rot_cap(k) -> Polygon:
    x, y, rot = k
    a = math.radians(-rot)
    c, s = math.cos(a), math.sin(a)
    return Polygon([(x + px * c - py * s, y + px * s + py * c) for px, py in ((-8.75, -8.25), (8.75, -8.25), (8.75, 8.25), (-8.75, 8.25))])


def _need_stl(path):
    if not path.exists():
        pytest.skip(f"{path.name} not built (make -C hardware/case stls)")


@pytest.mark.parametrize("half", HALVES)
def test_stl_matches_the_outline(data, half):
    """Flat 0.8 mm plate on z = 0, the generated outline, the left one mirrored like the board."""
    stl = CASE / "stl" / f"guard-{half}.stl"
    _need_stl(stl)
    mesh = load_layout_frame(stl)
    if half == "left":       # the physical left part is mirrored in x (case.scad mirror_left)
        mesh.vertices[:, 0] *= -1
    assert mesh.is_watertight
    (x0, y0, z0), (x1, y1, z1) = mesh.bounds
    assert z0 == pytest.approx(0, abs=1e-3) and z1 == pytest.approx(param("guard_t"), abs=1e-3)
    gx0, gy0, gx1, gy1 = guard_of(data, half).bounds
    for a, b in ((x0, gx0), (y0, gy0), (x1, gx1), (y1, gy1)):
        assert a == pytest.approx(b, abs=0.05)
    assert abs(mesh.volume) == pytest.approx(guard_of(data, half).area * param("guard_t"), rel=0.01)


@pytest.mark.parametrize("half", HALVES)
def test_dxf_matches_the_outline(data, half):
    ezdxf = pytest.importorskip("ezdxf")
    dxf = CASE / "dxf" / f"guard-{half}.dxf"
    _need_stl(dxf)
    region = None
    for e in ezdxf.readfile(str(dxf)).modelspace():
        assert e.dxftype() == "LWPOLYLINE", e.dxftype()
        ring = Polygon([((-1 if half == "left" else 1) * p[0], layout_y(p[1])) for p in e.get_points()]).buffer(0)
        region = ring if region is None else region.symmetric_difference(ring)
    g = guard_of(data, half)
    assert region.symmetric_difference(g).area < 0.5
