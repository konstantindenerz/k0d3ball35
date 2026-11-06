# SPDX-License-Identifier: MIT
"""The PMW3610 sensor daughterboard (hardware/sensor-pcb) must match the cradle
(hardware/trackball-cradle): same board size, same hole spacing on the same axis, optical
centre on the ball axis, lens and sensor inside the lens cavity, every component on the
floor-facing side and lower than the component gap, FPC connector in front of the cable slot.

Everything is read from the files: the board from ``k0d3ball35-sensor.kicad_pcb`` (board
outline, footprints, pads, courtyards, the sensor body cutout), the cradle from
``params.scad`` and ``stack.json``. The datasheet numbers below are the reference for the
sensor footprint and the lens:

* PMW3610DM-SUDU datasheet PMS0003 R2.4 (2017-09-14), figure 2 (package outline),
  figure 4 (assembly with LM18-LSI, Z stack) and figure 5 (recommended PCB cutout and pin
  spacing): https://trackballs.eu/media/Nakabayashi/Digio2/PMW3610DM-SUDU.pdf
  (mirror: https://www.epsglobal.com/Media-Library/EPSGlobal/Products/files/pixart/PMW3610DM-SUDU.pdf)
* LM18-LSI lens datasheet PMS0039 R1.03 (2024-11-14), figure 1 (lens outline) and the
  mechanical assembly table:
  https://github.com/ufan/pmw3610_breakout/blob/master/datasheet/lens-LM18-LSI.pdf
* Hirose FH12 catalogue (connector height, FH12-06S-0.5SH width 6.1 / 7.1 mm):
  https://media.digikey.com/pdf/Data%20Sheets/Hirose%20PDFs/FH12.pdf
* Cross-check of the optical centre offset against two independent footprints:
  https://github.com/bullwinkle3000/pmw3610-pcb (pin 1 at 6.168, optical centre mark at
  2.988, i.e. 3.18 mm) and https://github.com/ufan/pmw3610_breakout (PMW3610-Ref.kicad_mod).

The OpenSCAD render test is skipped when no OpenSCAD binary is available.
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / "hardware" / "sensor-pcb" / "k0d3ball35-sensor.kicad_pcb"
FOOTPRINT = ROOT / "hardware" / "lib" / "k0d3ball35.pretty" / "PMW3610DM-SUDU.kicad_mod"
CRADLE = ROOT / "hardware" / "trackball-cradle"
SCAD = CRADLE / "cradle.scad"
STL_OUT = ROOT / "build" / "cradle-19mm-pocket.stl"

# ---------------------------------------------------------------- datasheet references (mm)
# PMW3610DM-SUDU figure 5: pin pitch 1.78, rows 10.70 apart, optical centre 3.18 from the
# pin 1 column towards the other pins and centred between the rows (5.35), lower row shifted
# 0.89, cutout 16.96 x 8.60 from 2.78 beyond pin 1 to 14.18 on the far side.
PIN_PITCH = 1.78
ROW_SPACING = 10.70
OPTICAL_FROM_PIN1 = 3.18
ROW2_OFFSET = 0.89
CUTOUT_PIN1_SIDE = 2.78 + OPTICAL_FROM_PIN1          # +5.96 from the optical centre
CUTOUT_FAR_SIDE = 14.18 - OPTICAL_FROM_PIN1          # -11.00 from the optical centre
CUTOUT_HALF_WIDTH = (9.65 - 1.05) / 2                # 4.30
# PMW3610DM-SUDU figure 4 (Z stack, mouse orientation)
LENS_Z_MIN, LENS_Z_TYP, LENS_Z_MAX = 2.2, 2.4, 2.6   # lens reference plane to tracking surface
PCB_TO_BASE_PLATE = 3.40                             # PCB lens-side face to lens reference plane
SENSOR_ABOVE_PCB_COMPONENT_SIDE = 9.05 - 7.40        # 1.65, top of the package on the pin side
SENSOR_BELOW_PCB_LENS_SIDE = 0.7                     # body protrusion on the lens side (docs/08)
# LM18-LSI figure 1: base flange 12.90 x 8.25 (reference surface), upper body 10.29 x 6.55,
# 5.95 tall including the two 0.90 mm guide posts, base 2.12 thick.
LENS_BASE_L, LENS_BASE_W = 12.90, 8.25
LENS_BODY_L, LENS_BODY_W = 10.29, 6.55
LENS_HEIGHT = 5.95
# Hirose FH12 catalogue: standard flip-lock height 2.0 mm; FH12-06S-0.5SH B = 6.1, C = 7.1
FH12_HEIGHT = 2.0
FH12_WIDTH = 7.1

# tallest point of each footprint above its own board face (mm)
HEIGHTS = {
    "FPC_0.5mm_6P_FH12-6S": FH12_HEIGHT,
    "SOT-23": 1.45,                       # JEDEC TO-236 maximum
    "C_0603": 0.95,
    "R_0603": 0.55,
    "TestPoint_D1.0mm": 0.0,
    "MountingHole_M2": 0.0,
    "PMW3610DM-SUDU": SENSOR_ABOVE_PCB_COMPONENT_SIDE,   # on the pin side, opposite to its layer
}
BALL_SIDE = "B.Cu"          # the sensor sits on the back, the "BALL SIDE" silkscreen face
COMPONENT_SIDE = "F.Cu"


# ---------------------------------------------------------------- s-expression reader
def _tokenize(text: str):
    tok, i, n = "", 0, len(text)
    while i < n:
        ch = text[i]
        if ch == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            yield text[i:j + 1]
            i = j + 1
        elif ch in "()":
            if tok:
                yield tok
                tok = ""
            yield ch
            i += 1
        elif ch.isspace():
            if tok:
                yield tok
                tok = ""
            i += 1
        else:
            tok += ch
            i += 1
    if tok:
        yield tok


def parse_sexp(text: str):
    stack = [[]]
    for t in _tokenize(text):
        if t == "(":
            stack.append([])
        elif t == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t)
    return stack[0][0]


def children(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]


def child(node, name, default=None):
    found = children(node, name)
    return found[0] if found else default


def unq(s):
    return s[1:-1] if isinstance(s, str) and s.startswith('"') else s


def xy(node):
    return float(node[1]), float(node[2])


class Footprint:
    def __init__(self, node):
        self.name = unq(node[1]).split(":")[-1]
        self.layer = unq(child(node, "layer")[1])
        at = child(node, "at", ["at", "0", "0"])      # library footprints carry no position
        self.x, self.y = float(at[1]), float(at[2])
        self.rot = float(at[3]) if len(at) > 3 else 0.0
        self.ref = next(unq(p[2]) for p in children(node, "property") if unq(p[1]) == "Reference")
        self.node = node

    def to_board(self, lx, ly):
        """Footprint local -> board coordinates (KiCad: y down, rotation counter-clockwise)."""
        a = math.radians(self.rot)
        return (self.x + lx * math.cos(a) + ly * math.sin(a),
                self.y - lx * math.sin(a) + ly * math.cos(a))

    def pads(self):
        out = {}
        for p in children(self.node, "pad"):
            px, py = xy(child(p, "at"))
            drill = child(p, "drill")
            out[unq(p[1])] = {
                "type": p[2], "shape": p[3], "pos": self.to_board(px, py),
                "size": xy(child(p, "size")), "drill": float(drill[1]) if drill else None,
            }
        return out

    def rects(self, layer):
        """Axis-aligned boxes (x0, x1, y0, y1) of fp_rect items on a layer, in board coordinates."""
        boxes = []
        for r in children(self.node, "fp_rect"):
            if unq(child(r, "layer")[1]) != layer:
                continue
            a = self.to_board(*xy(child(r, "start")))
            b = self.to_board(*xy(child(r, "end")))
            boxes.append((min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1])))
        return boxes


class Board:
    def __init__(self, path: Path):
        self.tree = parse_sexp(path.read_text(encoding="utf-8"))
        self.footprints = {fp.ref: fp for fp in (Footprint(n) for n in children(self.tree, "footprint"))}
        self.thickness = float(child(child(self.tree, "general"), "thickness")[1])

    def outline_bbox(self):
        xs, ys = [], []
        for name in ("gr_line", "gr_arc", "gr_rect", "gr_circle", "gr_poly"):
            for item in children(self.tree, name):
                if unq(child(item, "layer")[1]) != "Edge.Cuts":
                    continue
                for key in ("start", "mid", "end"):
                    pt = child(item, key)
                    if pt:
                        xs.append(float(pt[1]))
                        ys.append(float(pt[2]))
        assert xs, "no board outline on Edge.Cuts"
        return min(xs), max(xs), min(ys), max(ys)


# ---------------------------------------------------------------- cradle parameters
def scad_params(path: Path) -> dict:
    values = {}
    for m in re.finditer(r"^(\w+)\s*=\s*([^;]+);", path.read_text(), re.M):
        name, expr = m.group(1), m.group(2).strip()
        if re.fullmatch(r"[\d.\s+*/()-]+", expr):
            values[name] = float(eval(expr, {"__builtins__": {}}))   # plain arithmetic only
        else:
            values[name] = expr.strip('"')
    return values


@pytest.fixture(scope="module")
def board():
    return Board(PCB)


@pytest.fixture(scope="module")
def params():
    return scad_params(CRADLE / "params.scad")


@pytest.fixture(scope="module")
def stack():
    return json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]


@pytest.fixture(scope="module")
def geometry(board):
    """Board centre, hole positions and the hole axis as derived from the PCB file."""
    x0, x1, y0, y1 = board.outline_bbox()
    holes = [fp for fp in board.footprints.values()
             if any(p["type"] == "np_thru_hole" and p["drill"] and p["drill"] >= 2.0 for p in fp.pads().values())]
    assert len(holes) == 2, [h.ref for h in holes]
    pts = sorted((fp.x, fp.y) for fp in holes)
    return {
        "bbox": (x0, x1, y0, y1),
        "centre": ((x0 + x1) / 2, (y0 + y1) / 2),
        "size": (x1 - x0, y1 - y0),
        "holes": pts,
        "hole_refs": [h.ref for h in holes],
        "hole_d": holes[0].pads()[""]["drill"],
    }


# ---------------------------------------------------------------- tests
def test_board_outline_matches_cradle_board_size(geometry, params, board):
    w, h = geometry["size"]
    # cradle local x (sensor_pcb_w) is the lens / pin-row axis, local y (sensor_pcb_l) the hole axis
    assert abs(w - params["sensor_pcb_w"]) < 0.01, (w, params["sensor_pcb_w"])
    assert abs(h - params["sensor_pcb_l"]) < 0.01, (h, params["sensor_pcb_l"])
    assert abs(board.thickness - params["sensor_pcb_t"]) < 0.01


def test_mounting_holes_match_cradle_posts(geometry, params):
    (ax, ay), (bx, by) = geometry["holes"]
    cx, cy = geometry["centre"]
    # both on the vertical centre line, i.e. along the 25 mm axis (cradle local y)
    assert abs(ax - cx) < 0.01 and abs(bx - cx) < 0.01, geometry["holes"]
    assert abs((by - ay) - params["sensor_hole_sp"]) < 0.01, (by - ay, params["sensor_hole_sp"])
    # symmetric about the board centre
    assert abs((ay + by) / 2 - cy) < 0.01
    # the M2 x 10 case screw and the 1.6 mm pilot both pass the 2.2 mm hole
    assert geometry["hole_d"] >= params["case_screw_d"] + 0.1
    assert geometry["hole_d"] > params["flange_pilot_d"]
    # posts (5 mm columns) stay on the board: hole to board edge
    assert ay - geometry["bbox"][2] >= 2.5 and geometry["bbox"][3] - by >= 2.5


def test_sensor_optical_centre_between_the_holes(board, geometry):
    u1 = board.footprints["U1"]
    assert u1.name == "PMW3610DM-SUDU"
    assert u1.layer == BALL_SIDE
    cx, cy = geometry["centre"]
    assert abs(u1.x - cx) < 0.01 and abs(u1.y - cy) < 0.01, (u1.x, u1.y, cx, cy)
    pads = u1.pads()
    assert set(pads) == {str(i) for i in range(1, 17)}
    p1, p2, p8, p9, p16 = (pads[k]["pos"] for k in ("1", "2", "8", "9", "16"))
    # pin rows run along the lens axis (board x), 10.70 apart and centred on the optical centre
    assert abs(p1[1] - p8[1]) < 0.01 and abs(p9[1] - p16[1]) < 0.01
    assert abs(abs(p1[1] - p9[1]) - ROW_SPACING) < 0.01
    assert abs((p1[1] + p9[1]) / 2 - u1.y) < 0.01
    # optical centre 3.18 from the pin 1 column, towards pin 2 (datasheet figure 5, both references)
    assert abs(abs(p1[0] - u1.x) - OPTICAL_FROM_PIN1) < 0.01, p1
    direction = -1 if p1[0] > u1.x else 1          # pins 2..8 lie towards the optical centre
    assert abs((p2[0] - p1[0]) - direction * PIN_PITCH) < 0.01
    assert abs((p9[0] - p1[0]) - direction * (7 * PIN_PITCH + ROW2_OFFSET)) < 0.01
    # library footprint says the same thing (the board is generated from it)
    lib = Footprint(parse_sexp(FOOTPRINT.read_text()))
    lib.x = lib.y = 0.0
    lp = lib.pads()
    assert abs(lp["1"]["pos"][0] - OPTICAL_FROM_PIN1) < 0.01 and abs(lp["1"]["pos"][1] + ROW_SPACING / 2) < 0.01


def test_sensor_body_cutout_per_datasheet(board, geometry):
    u1 = board.footprints["U1"]
    cut = u1.rects("Edge.Cuts")
    assert len(cut) == 1, cut
    x0, x1, y0, y1 = cut[0]
    assert abs((x1 - x0) - (CUTOUT_PIN1_SIDE + CUTOUT_FAR_SIDE)) < 0.01, (x1 - x0)   # 16.96
    assert abs((y1 - y0) - 2 * CUTOUT_HALF_WIDTH) < 0.01, (y1 - y0)                  # 8.60
    assert abs((y0 + y1) / 2 - u1.y) < 0.01
    p1x = u1.pads()["1"]["pos"][0]
    pin1_side = 1 if p1x > u1.x else -1
    near = x1 if pin1_side > 0 else x0
    far = x0 if pin1_side > 0 else x1
    assert abs(abs(near - u1.x) - CUTOUT_PIN1_SIDE) < 0.01, near
    assert abs(abs(far - u1.x) - CUTOUT_FAR_SIDE) < 0.01, far
    # the cutout stays clear of the mounting holes and the 5 mm post faces around them
    for hx, hy in geometry["holes"]:
        assert min(abs(hy - y0), abs(hy - y1)) >= 2.5 + 0.5, (hy, y0, y1)


def test_lens_and_sensor_fit_the_lens_cavity(board, params, stack):
    """Lens cavity: (sensor_pcb_w - 2) x (sensor_pcb_l - 2) x (lens_h + 0.4) above the board plane,
    minus two 5 mm post columns at (0, +-sensor_hole_sp / 2)."""
    u1 = board.footprints["U1"]
    cav_x = (params["sensor_pcb_w"] - 2) / 2
    cav_y = (params["sensor_pcb_l"] - 2) / 2
    cav_h = params["lens_h"] + 0.4
    post_inner = params["sensor_hole_sp"] / 2 - 2.5
    # Z stack: board plane = ball radius + lens_z + lens_h, lens reference plane per datasheet
    assert LENS_Z_MIN <= params["lens_z"] <= LENS_Z_MAX
    assert abs(params["lens_z"] - LENS_Z_TYP) < 1e-6
    assert abs(params["lens_h"] - PCB_TO_BASE_PLATE) < 1e-6
    assert abs(stack["sensor_pcb_plane_dist"] - (stack["ball_d"] / 2 + params["lens_z"] + params["lens_h"])) < 1e-6
    # the lens hangs on the sensor; the cavity floor sits 0.4 mm below its reference surface
    assert cav_h - params["lens_h"] >= 0.4 - 1e-6
    # sensor body cutout (and with it the sensor body and the lens upper body) inside the cavity
    x0, x1, y0, y1 = u1.rects("Edge.Cuts")[0]
    assert x0 - u1.x >= -cav_x and x1 - u1.x <= cav_x, (x0 - u1.x, x1 - u1.x, cav_x)
    assert y0 - u1.y >= -cav_y and y1 - u1.y <= cav_y
    # LM18-LSI base flange (12.90 x 8.25): wherever it sits along the cutout it stays inside the
    # cavity and clears the post columns (|y| < post_inner) by a margin
    assert LENS_BASE_L <= (x1 - x0), "flange longer than the cutout, position unknown"
    assert LENS_BASE_W / 2 < post_inner - 1.0, (LENS_BASE_W / 2, post_inner)
    assert LENS_BASE_W / 2 < cav_y
    assert max(abs(x0 - u1.x), abs(x1 - u1.x)) + 0.5 < cav_x
    # lens upper body passes the cutout
    assert LENS_BODY_W < 2 * CUTOUT_HALF_WIDTH and LENS_BODY_L < (x1 - x0)
    # the cradle's own lens envelope parameters are also inside the cavity
    assert params["lens_l"] / 2 < cav_x and params["lens_w"] / 2 < post_inner
    # sensor body on the lens side (0.7 mm) is well below the cavity height
    assert SENSOR_BELOW_PCB_LENS_SIDE < cav_h


def test_lens_envelope_on_dwgs_user_matches_datasheet_flange(board, params):
    """The footprint's first dashed Dwgs.User rect is the LM18-LSI base flange (12.90 x 8.25,
    PMS0039 R1.03 figure 1) centred on the optical centre; it clears the cradle post columns.
    The second rect is the upper body (10.29 x 6.55)."""
    u1 = board.footprints["U1"]
    env = u1.rects("Dwgs.User")
    assert len(env) == 2
    x0, x1, y0, y1 = env[0]
    assert abs((x1 - x0) - LENS_BASE_L) < 0.01 and abs((y1 - y0) - LENS_BASE_W) < 0.01, env[0]
    assert abs((x0 + x1) / 2 - u1.x) < 0.01 and abs((y0 + y1) / 2 - u1.y) < 0.01
    post_inner = params["sensor_hole_sp"] / 2 - 2.5
    assert (y1 - y0) / 2 <= post_inner - 1.0, ((y1 - y0) / 2, post_inner)
    bx0, bx1, by0, by1 = env[1]
    assert abs((bx1 - bx0) - LENS_BODY_L) < 0.01 and abs((by1 - by0) - LENS_BODY_W) < 0.01, env[1]


def test_all_components_on_the_floor_side_and_below_the_gap(board, params, stack):
    gap = (stack["sensor_pcb_plane_z"] - params["sensor_pcb_t"]) - stack["floor_z"]
    assert abs(gap - 2.25) < 1e-6, gap
    assert abs(gap - (params["depth_below_pcb"] + params["pcb_t"] - stack["sensor_pcb_plane_dist"]
                      + stack["ball_centre_z"] - params["sensor_pcb_t"])) < 1e-6
    # params.scad budget for the pin side: sensor top + margin
    assert params["sensor_pins_h"] <= gap + 1e-6
    tallest = {}
    for fp in board.footprints.values():
        assert fp.name in HEIGHTS, f"no height budget for footprint {fp.name} ({fp.ref})"
        if fp.ref == "U1":
            continue
        assert fp.layer == COMPONENT_SIDE, f"{fp.ref} is on the ball side"
        tallest[fp.ref] = HEIGHTS[fp.name]
    tallest["U1 (pin side)"] = HEIGHTS["PMW3610DM-SUDU"]
    ref, h = max(tallest.items(), key=lambda kv: kv[1])
    assert h < gap, f"{ref} is {h} mm tall, component gap is {gap} mm"
    assert gap - h >= 0.25 - 1e-6, f"{ref}: only {gap - h:.2f} mm left under the board"


def test_fpc_connector_faces_the_cable_slot(board, geometry, params, stack):
    """The FFC leaves through a slot in the housing wall at one end of the hole axis
    (local -y, key-facing). The connector must sit at such an edge, its mouth towards it,
    and its body inside the slot width."""
    j1 = board.footprints["J1"]
    assert j1.name.startswith("FPC_0.5mm_6P_FH12")
    assert j1.layer == COMPONENT_SIDE
    x0, x1, y0, y1 = geometry["bbox"]
    cx, cy = geometry["centre"]
    slot_w = params["cable_slot_w"] if params["cable_slot_w"] > 0 else stack["housing_x"] - 2 * params["corner_post"]
    assert slot_w == pytest.approx(23.0), slot_w      # 29 mm housing minus the two corner posts
    # the FH12 footprint has its contact leads at local y = -1.85 and the cable mouth at local +y
    mouth = j1.to_board(0, 4.4)
    leads = j1.to_board(0, -1.85)
    d_top, d_bottom = abs(mouth[1] - y0), abs(mouth[1] - y1)
    edge_y = y0 if d_top < d_bottom else y1
    assert min(d_top, d_bottom) < 1.0, "connector mouth must sit at a board edge"
    assert abs(leads[1] - edge_y) > abs(mouth[1] - edge_y), "cable mouth must face the edge"
    # that edge is one of the two ends of the hole axis (a 26 mm side), where the slot is:
    # the holes lie on x = cx, so the hole axis is y and its ends are the y = y0 / y1 edges
    (hx, _), (hx2, _) = geometry["holes"]
    assert abs(hx - cx) < 0.01 and abs(hx2 - cx) < 0.01
    assert edge_y in (y0, y1) and (y1 - y0) == pytest.approx(params["sensor_pcb_l"], abs=0.01)
    # connector body (7.1 mm wide, FH12-06S) inside the slot, with the board centred in the housing
    reach = abs(j1.x - cx) + FH12_WIDTH / 2
    assert reach <= slot_w / 2, (reach, slot_w / 2)
    # courtyard inside the board
    (cx0, cx1, cy0, cy1), = j1.rects("F.CrtYd")
    assert cx0 >= x0 and cx1 <= x1 and cy0 >= y0 and cy1 <= y1, (cx0, cx1, cy0, cy1)
    # the connector and the cable live in the component gap; the slot spans it fully
    assert FH12_HEIGHT < (stack["sensor_pcb_plane_z"] - params["sensor_pcb_t"]) - stack["floor_z"]
    # r2.2: from the board plane up, the cable climbs a narrower channel in the same wall. It
    # must line up with the connector (the cable runs straight) and stay inside the slot.
    ch_x, ch_w = stack["cable_channel_x"], stack["cable_channel_w"]
    assert abs((j1.x - cx) - -ch_x) < 0.5, f"cable channel at {ch_x} does not line up with J1 at {j1.x - cx:+.2f}"
    assert abs(ch_x) + ch_w / 2 <= slot_w / 2 + 1e-6


def test_board_fits_the_housing_cavity(geometry, params, stack):
    w, h = geometry["size"]
    inner_x = stack["housing_x"] - 2 * params["housing_wall_x"]
    inner_y = stack["housing_y"] - 2 * params["housing_wall"]
    assert inner_x == pytest.approx(params["sensor_pcb_w"]) and inner_y == pytest.approx(params["sensor_pcb_l"])
    # the board cavity is the board plus sensor_pcb_gap per side, cut into the walls
    assert w + 2 * params["sensor_pcb_gap"] < stack["housing_x"] - 2 * (params["housing_wall_x"] - params["sensor_pcb_gap"]) + 1e-6
    assert params["housing_wall_x"] - params["sensor_pcb_gap"] >= 1.2, "walls too thin beside the board"
    assert stack["case_screw_sp"] == params["sensor_hole_sp"]


# ---------------------------------------------------------------- OpenSCAD render
def openscad():
    for cand in (shutil.which("openscad"), "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"):
        if cand and Path(cand).exists():
            return cand
    return None


def _section_values(mesh, z, axis):
    """Distinct coordinates (rounded to 0.01 mm) of the mesh's horizontal cross-section at z."""
    import numpy as np
    from trimesh.intersections import mesh_plane
    segs = mesh_plane(mesh, plane_normal=[0, 0, 1], plane_origin=[0, 0, z])
    return sorted(set(float(c) for c in np.round(segs.reshape(-1, 3)[:, axis], 2)))


def _has(values, want, tol=0.02):
    return any(abs(v - want) < tol for v in values)


@pytest.mark.skipif(openscad() is None, reason="openscad not installed")
def test_render_pocket_cradle_and_measure_cavities(board, geometry, params, stack):
    trimesh = pytest.importorskip("trimesh")

    STL_OUT.parent.mkdir(exist_ok=True)
    cmd = [openscad(), "--backend", "manifold", "-D", 'part="cradle"', "-D", "ball_d=19.05",
           "-D", 'mount="pocket"', "-o", str(STL_OUT), str(SCAD)]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    assert res.returncode == 0, res.stderr
    values = {m.group(1): float(m.group(2)) for m in re.finditer(r"STACK (\w+)=(-?[\d.]+)", res.stderr + res.stdout)}
    assert values["sensor_pcb_plane_z"] == stack["sensor_pcb_plane_z"]
    assert values["floor_z"] == stack["floor_z"]

    mesh = trimesh.load(STL_OUT, force="mesh")
    assert mesh.is_watertight
    floor_z, board_z = values["floor_z"], values["sensor_pcb_plane_z"]
    cav_h = params["lens_h"] + 0.4
    w, h = geometry["size"]

    # housing footprint 30 x 29 on the floor
    z = floor_z + 0.1
    xs, ys = _section_values(mesh, z, 0), _section_values(mesh, z, 1)
    assert abs(max(xs) - min(xs) - stack["housing_x"]) < 0.05 and abs(max(ys) - min(ys) - stack["housing_y"]) < 0.05

    # board cavity between floor and board plane: walls at +-(w/2 + gap) and +-(l/2 + gap)
    z = (floor_z + board_z) / 2
    xs, ys = _section_values(mesh, z, 0), _section_values(mesh, z, 1)
    want_x = w / 2 + params["sensor_pcb_gap"]
    want_y = h / 2 + params["sensor_pcb_gap"]
    assert _has(xs, want_x) and _has(xs, -want_x), xs
    assert _has(ys, want_y) and _has(ys, -want_y), ys
    assert w <= 2 * want_x and h <= 2 * want_y
    # cable slot in the -y wall: slot edges at +-slot_w / 2 and nothing of the -y wall inside them
    slot_w = stack["housing_x"] - 2 * params["corner_post"]
    assert _has(xs, slot_w / 2) and _has(xs, -slot_w / 2), xs
    from trimesh.intersections import mesh_plane
    segs = mesh_plane(mesh, plane_normal=[0, 0, 1], plane_origin=[0, 0, z]).reshape(-1, 3)
    in_slot = segs[(abs(segs[:, 0]) < slot_w / 2 - 0.05) & (segs[:, 1] < -want_y + 0.05)]
    assert len(in_slot) == 0, "material in the cable slot"
    # the connector (7.1 mm wide) sits inside the slot width
    j1 = board.footprints["J1"]
    assert abs(j1.x - geometry["centre"][0]) + FH12_WIDTH / 2 <= slot_w / 2

    # lens cavity above the board plane: +-(w/2 - 1) x +-(l/2 - 1), cav_h tall
    z = board_z + cav_h / 2
    xs, ys = _section_values(mesh, z, 0), _section_values(mesh, z, 1)
    assert _has(xs, w / 2 - 1) and _has(xs, -(w / 2 - 1)), xs
    assert _has(ys, h / 2 - 1) and _has(ys, -(h / 2 - 1)), ys
    # cavity ceiling: just above board_z + cav_h the section near the axis is solid except the
    # 9 mm optical hole, just below it is open to the cavity walls
    below = _section_values(mesh, board_z + cav_h - 0.05, 0)
    above = _section_values(mesh, board_z + cav_h + 0.05, 0)
    assert _has(below, w / 2 - 1) and not _has(above, w / 2 - 1), (below, above)
    assert _has(above, 4.5, 0.05) and _has(above, -4.5, 0.05), above
    # post columns (5 mm) at (0, +-hole_sp/2) exist in the cavity: section hits x = +-2.5 there
    segs = mesh_plane(mesh, plane_normal=[0, 0, 1], plane_origin=[0, 0, z]).reshape(-1, 3)
    for sy in (-1, 1):
        near = segs[abs(segs[:, 1] - sy * params["sensor_hole_sp"] / 2) < 0.3]
        assert len(near) and abs(abs(near[:, 0]).max() - 2.5) < 0.05, near
    # the sensor body cutout footprint and the lens flange are inside that cavity
    u1 = board.footprints["U1"]
    x0, x1, y0, y1 = u1.rects("Edge.Cuts")[0]
    assert x0 - u1.x > -(w / 2 - 1) and x1 - u1.x < (w / 2 - 1)
    assert LENS_BASE_W / 2 < params["sensor_hole_sp"] / 2 - 2.5
