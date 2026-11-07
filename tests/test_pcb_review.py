# SPDX-License-Identifier: MIT
"""Automated part of the manual board review (issues/hw-main-pcb-review-r1.md).

The two routed boards are parsed as plain s-expressions (no pcbnew needed) and checked
against spec/01-design-spec.md, the layout yaml and the reference geometry of the parts:

* hot-swap socket pads versus the kiswitch CPG135001S30 footprint, back face wired,
* FH12-6S on the right board only, pin 1 and contact side,
* controller holes: nets and pin labels per the spec pin table, USB end at the top edge,
* battery bay outline on the back silkscreen, nothing but U1 inside it,
* mounting holes clear of switch bodies, sockets and copper,
* power switch at the inner edge (actuator direction is a known defect, see the ticket),
* diode orientation, silkscreen texts, test pads, thumb keys,
* copper to edge clearance, the octagonal notch, no cradle holes,
* silkscreen over copper limited to the known cosmetic cases (needs kicad-cli).

Coordinates: the board page offset is (120, 60). The layout frame is handedness-neutral and
the left BOARD is its mirror image (x -> -x, `Layout.to_board`), so frame values are compared
through `_board()` / `_page()`; footprints themselves are not mirrored (local pad positions and
the hole numbering stay as in the part), only their rotation changes sign.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
from dataclasses import dataclass, field

import pytest
from shapely.geometry import LineString, Point, Polygon, box
from shapely import affinity

from k0d3.geometry import HALVES, REPO, load_layout
from k0d3.netlist import FPC_PINS, HOLE_PIN, hole_net, spare_pad_nets

OFFSET = (120.0, 60.0)
BOARDS = {h: REPO / "hardware" / f"{h}-pcb" / f"k0d3ball35-{h}.kicad_pcb" for h in HALVES}
SPEC = REPO / "spec" / "01-design-spec.md"
EDGE_CLEARANCE = 0.3
HOLE_RADIUS = 1.1

# kiswitch SW_Hotswap_Kailh_Choc_V1_1.00u (socket on the back, seen from the front):
# pad 1 at (-3.5, -6.0) and pad 2 at (8.5, -3.8), both 2.55 x 2.5 on B.Cu, boss holes
# 3.05 mm at (0, -5.9) and (5, -3.8). Our pad 1 is 0.45 mm further north and 2.0 mm tall
# so that it clears the mirrored boss hole; pad 2 is identical.
KISWITCH_BOSSES = {(0.0, -5.9), (5.0, -3.8)}
KISWITCH_PADS = {"1": (-3.5, -6.0), "2": (8.5, -3.8)}
SOCKET_BODY = (-4.8, -8.9, 10.2, -2.0)   # CPG135001S30 plastic body, local, seen from the front


# ----- s-expression parsing ------------------------------------------------------------
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


def _parse(text: str):
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


def _s(v) -> str:
    return v[1:-1] if isinstance(v, str) and v.startswith('"') else v


def _kids(node, key):
    return [n for n in node if isinstance(n, list) and n and n[0] == key]


def _kid(node, key, default=None):
    k = _kids(node, key)
    return k[0] if k else default


def _floats(node, key, default=()):
    k = _kid(node, key)
    return tuple(float(v) for v in k[1:]) if k else tuple(default)


@dataclass
class Pad:
    number: str
    kind: str
    shape: str
    x: float          # page coordinates
    y: float
    w: float
    h: float
    rot: float
    layers: tuple[str, ...]
    drill: float | None
    net: str

    def on(self, layer: str) -> bool:
        return layer in self.layers or "*.Cu" in self.layers

    @property
    def copper(self) -> bool:
        return self.kind != "np_thru_hole"

    def poly(self) -> Polygon:
        if self.shape == "circle":
            return Point(self.x, self.y).buffer(self.w / 2, 16)
        b = box(self.x - self.w / 2, self.y - self.h / 2, self.x + self.w / 2, self.y + self.h / 2)
        return affinity.rotate(b, -self.rot, origin=(self.x, self.y)) if self.rot else b


@dataclass
class Graphic:
    kind: str          # line | text
    layer: str
    pts: list[tuple[float, float]]   # page coordinates
    text: str = ""
    size: float = 0.0


@dataclass
class Footprint:
    ref: str
    name: str
    x: float
    y: float
    rot: float
    layer: str
    pads: list[Pad] = field(default_factory=list)
    graphics: list[Graphic] = field(default_factory=list)

    def local(self, px: float, py: float) -> tuple[float, float]:
        """Footprint-local point to page coordinates (KiCad: positive rotation is CCW on screen)."""
        th = math.radians(self.rot)
        return (self.x + px * math.cos(th) + py * math.sin(th), self.y - px * math.sin(th) + py * math.cos(th))

    def local_box(self, x1, y1, x2, y2) -> Polygon:
        return Polygon([self.local(x1, y1), self.local(x2, y1), self.local(x2, y2), self.local(x1, y2)])

    def pad(self, number: str, layer: str) -> Pad:
        for p in self.pads:
            if p.number == number and p.on(layer) and p.copper:
                return p
        raise KeyError((self.ref, number, layer))

    def lines(self, layer: str) -> list[Graphic]:
        return [g for g in self.graphics if g.kind == "line" and g.layer == layer]

    def courtyard(self, layer: str) -> Polygon | None:
        ls = self.lines(layer)
        if not ls:
            return None
        xs = [x for g in ls for x, _ in g.pts]
        ys = [y for g in ls for _, y in g.pts]
        return box(min(xs), min(ys), max(xs), max(ys))

    @property
    def frame(self) -> tuple[float, float]:
        return (round(self.x - OFFSET[0], 3), round(self.y - OFFSET[1], 3))


@dataclass
class Board:
    half: str
    footprints: dict[str, Footprint]
    segments: list[tuple[str, str, float, tuple, tuple]]   # layer, net, width, start, end
    vias: list[tuple[str, float, float, float, float]]      # net, x, y, size, drill
    zones: list[tuple[str, str, list[Polygon]]]             # net, layer, filled polygons
    gr_polys: list[tuple[str, str, Polygon]]                # layer, stroke type, polygon
    gr_texts: list[Graphic]
    outline: Polygon

    def copper(self, layer: str):
        """(description, polygon) of every copper item on one face."""
        for fp in self.footprints.values():
            for p in fp.pads:
                if p.copper and p.on(layer):
                    yield f"{fp.ref} pad {p.number}", p.poly()
        for lay, net, w, a, b in self.segments:
            if lay == layer:
                yield f"track {net}", LineString([a, b]).buffer(w / 2, 8)
        for net, x, y, size, _ in self.vias:
            yield f"via {net}", Point(x, y).buffer(size / 2, 16)
        for net, lay, polys in self.zones:
            if lay == layer:
                for poly in polys:
                    yield f"zone {net} {lay}", poly

    def by_prefix(self, prefix: str) -> list[Footprint]:
        return [fp for ref, fp in sorted(self.footprints.items()) if re.fullmatch(prefix + r"\d+", ref)]


def _load(half: str) -> Board:
    tree = _parse(BOARDS[half].read_text(encoding="utf-8"))
    nets = {n[1]: _s(n[2]) for n in _kids(tree, "net")}

    def net_of(node) -> str:
        """KiCad 10 writes pad nets by name and track nets by number."""
        n = _kid(node, "net")
        if not n:
            return ""
        return _s(n[-1]) if n[-1].startswith('"') else nets[n[1]]
    fps: dict[str, Footprint] = {}
    for node in _kids(tree, "footprint"):
        at = _floats(node, "at")
        ref = ""
        for prop in _kids(node, "property"):
            if _s(prop[1]) == "Reference":
                ref = _s(prop[2])
        fp = Footprint(ref, _s(node[1]).split(":")[-1], at[0], at[1], at[2] if len(at) > 2 else 0.0, _s(_kid(node, "layer")[1]))
        for p in _kids(node, "pad"):
            pat = _floats(p, "at")
            px, py = fp.local(pat[0], pat[1])
            size = _floats(p, "size")
            drill = _floats(p, "drill")
            netn = _kid(p, "net")
            fp.pads.append(Pad(_s(p[1]), p[2], p[3], px, py, size[0], size[1], pat[2] if len(pat) > 2 else 0.0,
                               tuple(_s(l) for l in _kid(p, "layers")[1:]), drill[0] if drill else None,
                               net_of(p)))
        for g in _kids(node, "fp_line"):
            s, e = _floats(g, "start"), _floats(g, "end")
            fp.graphics.append(Graphic("line", _s(_kid(g, "layer")[1]), [fp.local(*s), fp.local(*e)]))
        for g in _kids(node, "fp_text"):
            tat = _floats(g, "at")
            size = _floats(_kid(_kid(g, "effects"), "font"), "size")
            fp.graphics.append(Graphic("text", _s(_kid(g, "layer")[1]), [fp.local(tat[0], tat[1])], _s(g[2]), size[0]))
        for prop in _kids(node, "property"):
            if _kid(prop, "hide") or _kid(prop, "layer") is None:
                continue
            tat = _floats(prop, "at")
            size = _floats(_kid(_kid(prop, "effects"), "font"), "size")
            fp.graphics.append(Graphic("text", _s(_kid(prop, "layer")[1]), [fp.local(tat[0], tat[1])], _s(prop[2]), size[0]))
        fps[ref] = fp
    segments = [(_s(_kid(s, "layer")[1]), net_of(s), _floats(s, "width")[0], _floats(s, "start"), _floats(s, "end"))
                for s in _kids(tree, "segment")]
    vias = [(net_of(v), *_floats(v, "at"), _floats(v, "size")[0], _floats(v, "drill")[0]) for v in _kids(tree, "via")]
    zones = []
    for z in _kids(tree, "zone"):
        if _kid(z, "keepout"):
            continue
        # `(island yes)` would mark a fill area that KiCad drops as unconnected; the pours
        # keep their islands (island_removal_mode 0), so this is only a safety net.
        polys = [Polygon([tuple(float(c) for c in xy[1:]) for xy in _kids(_kid(fpoly, "pts"), "xy")])
                 for fpoly in _kids(z, "filled_polygon") if not _kid(fpoly, "island")]
        zones.append((net_of(z), _s(_kid(z, "layer")[1]), polys))
    gr_polys, outline = [], None
    for g in _kids(tree, "gr_poly"):
        poly = Polygon([tuple(float(c) for c in xy[1:]) for xy in _kids(_kid(g, "pts"), "xy")])
        layer = _s(_kid(g, "layer")[1])
        gr_polys.append((layer, _s(_kid(_kid(g, "stroke"), "type")[1]), poly))
        if layer == "Edge.Cuts":
            outline = poly
    gr_texts = []
    for g in _kids(tree, "gr_text"):
        tat = _floats(g, "at")
        size = _floats(_kid(_kid(g, "effects"), "font"), "size")
        gr_texts.append(Graphic("text", _s(_kid(g, "layer")[1]), [(tat[0], tat[1])], _s(g[1]), size[0]))
    assert outline is not None and outline.is_valid, f"{half}: no Edge.Cuts polygon"
    return Board(half, fps, segments, vias, zones, gr_polys, gr_texts, outline)


@pytest.fixture(scope="module", params=HALVES)
def half(request):
    if not BOARDS[request.param].exists():
        pytest.skip(f"{BOARDS[request.param].relative_to(REPO)} not generated")
    return request.param


@pytest.fixture(scope="module")
def board(half) -> Board:
    return _load(half)


@pytest.fixture(scope="module")
def layout(half):
    return load_layout(half)


def _board(layout, x: float, y: float) -> tuple[float, float]:
    """Layout-frame point -> page coordinates of this half's board (mirrored on the left)."""
    bx, by = layout.to_board(x, y)
    return (round(OFFSET[0] + bx, 3), round(OFFSET[1] + by, 3))


def _page(layout, poly: Polygon) -> Polygon:
    """Layout-frame polygon -> page coordinates of this half's board."""
    return affinity.translate(affinity.scale(poly, xfact=layout.board_sx, yfact=1, origin=(0, 0)), *OFFSET)


def _edge_x(layout, outline: Polygon, y: float, side: str) -> float:
    """x of the board edge crossed by the horizontal line through y, nearest to the inner or outer side
    (inner = -x in the frame, i.e. the left edge of the right board and the right edge of the left board)."""
    minx, _, maxx, _ = outline.bounds
    cut = outline.intersection(LineString([(minx - 1, y), (maxx + 1, y)]))
    xs = [c[0] for c in getattr(cut, "coords", []) or [p for g in getattr(cut, "geoms", []) for p in g.coords]]
    inner = (side == "inner") == (layout.board_sx > 0)
    return min(xs) if inner else max(xs)


def _edge_y_top(outline: Polygon, x: float) -> float:
    _, miny, _, maxy = outline.bounds
    cut = outline.intersection(LineString([(x, miny - 1), (x, maxy + 1)]))
    ys = [c[1] for c in getattr(cut, "coords", []) or [p for g in getattr(cut, "geoms", []) for p in g.coords]]
    return min(ys)


# ----- placement matches the layout --------------------------------------------------
def test_footprints_sit_where_the_layout_says(board, layout):
    for k in layout.keys:
        sw, d = board.footprints[k.ref], board.footprints[k.diode_ref]
        rot = (layout.board_sx * k.rotation) % 360
        assert (sw.x, sw.y) == _board(layout, k.x, k.y) and sw.rot % 360 == rot, k.ref
        # the diode offset (6 mm towards the user, rotated with the key) is mirrored with the key
        assert d.rot % 360 == rot and (round(d.x, 3), round(d.y, 3)) == tuple(round(v, 3) for v in sw.local(0, 6.0)), k.diode_ref
    cfg = layout.cfg
    assert (board.footprints["U1"].x, board.footprints["U1"].y) == _board(layout, cfg["controller"]["center"]["x"], cfg["controller"]["center"]["y"])
    assert (board.footprints["PS1"].x, board.footprints["PS1"].y) == _board(layout, cfg["power_switch"]["center"]["x"], cfg["power_switch"]["center"]["y"])
    assert all(fp.layer == "F.Cu" for fp in board.footprints.values()), "all footprints are placed unflipped; the back face uses the second pad set"


def test_left_board_is_mirror_of_layout(board, layout, half):
    """The frame is handedness-neutral; the left board mirrors x. SW00 (pinky top) sits at
    frame x +36, the controller at -58: on the left board that is board x -36 and +58, the
    controller block at the right edge seen from the top."""
    sx = -1 if half == "left" else 1
    assert layout.board_sx == sx
    sw00, u1 = board.footprints["SW00"], board.footprints["U1"]
    assert (sw00.x, sw00.y) == (OFFSET[0] + sx * 36.0, OFFSET[1] + 10.44)
    assert (u1.x, u1.y) == (OFFSET[0] + sx * -58.0, OFFSET[1] + 11.7)
    minx, miny, maxx, maxy = layout.outline.bounds
    want = (OFFSET[0] + min(sx * minx, sx * maxx), OFFSET[1] + miny, OFFSET[0] + max(sx * minx, sx * maxx), OFFSET[1] + maxy)
    assert all(math.isclose(a, b, abs_tol=1e-3) for a, b in zip(board.outline.bounds, want))
    assert _page(layout, layout.outline).symmetric_difference(board.outline).area < 1e-3
    if half == "left":
        assert u1.x > max(fp.x for fp in board.by_prefix("SW") if fp.ref[2] != "3"), "controller block beyond the finger keys"
        assert board.footprints["SW34"].x > sw00.x, "the inner thumb key is at the controller side"
        assert board.footprints["PS1"].x > u1.x, "power switch between the controller and the inner (right) edge"


def test_key_counts_thumbs_and_test_pads(board, layout, half):
    switches = {fp.ref for fp in board.by_prefix("SW")}
    thumbs = {"left": {"SW32", "SW33", "SW34"}, "right": {"SW33", "SW34"}}[half]
    assert switches == {f"SW{r}{c}" for r in range(3) for c in range(5)} | thumbs
    assert {fp.ref for fp in board.by_prefix("D")} == {"D" + ref[2:] for ref in switches}
    tps = board.by_prefix("TP")
    assert [tp.pad("1", "F.Cu").net for tp in tps] == spare_pad_nets(half)
    assert len(tps) == {"left": 9, "right": 5}[half]
    # the row runs along x on the left half and down y on the right one, where the thumb
    # cluster took the old spot (hardware/layout/k0d3ball35.yaml, halves.<side>.test_pads)
    step = 2.5 * (layout.board_sx if layout.cfg['test_pads']['direction'] == 'x' else 1)
    axis = 'x' if layout.cfg['test_pads']['direction'] == 'x' else 'y'
    assert all(math.isclose(getattr(tps[i + 1], axis) - getattr(tps[i], axis), step, abs_tol=1e-6)
               for i in range(len(tps) - 1))
    assert ("J1" in board.footprints) == (half == "right"), "FPC connector on the right board only"
    assert not any(fp.name.startswith("FPC") for fp in board.footprints.values() if half == "left")


# ----- hot-swap sockets ----------------------------------------------------------------
def test_socket_pads_match_kiswitch_geometry(board):
    """Back-face pad set per switch: pad 1 west of the boss hole at (0, -5.9), pad 2 east of
    the boss hole at (5, -3.8), the same arrangement as the kiswitch CPG135001S30 footprint."""
    for sw in board.by_prefix("SW"):
        holes = [p for p in sw.pads if p.kind == "np_thru_hole" and p.drill == 3.05]
        assert len(holes) == 3, f"{sw.ref}: three 3.05 mm boss holes (one spare for the mirrored set)"
        hole_local = {tuple(round(v, 3) for v in _inv(sw, p.x, p.y)) for p in holes}
        assert KISWITCH_BOSSES <= hole_local, sw.ref
        for number, (kx, ky) in KISWITCH_PADS.items():
            p = sw.pad(number, "B.Cu")
            lx, ly = _inv(sw, p.x, p.y)
            assert math.isclose(lx, kx, abs_tol=1e-6), f"{sw.ref} pad {number}: x {lx} vs kiswitch {kx}"
            assert abs(ly - ky) <= 0.45 + 1e-6, f"{sw.ref} pad {number}: y {ly} vs kiswitch {ky}"
            assert p.kind == "smd" and "B.Paste" in p.layers and math.isclose(p.w, 2.55)
        # the socket body lies on the board and the pads inside its outline
        # the 15 x 6.9 envelope includes the solder legs; on the pinky top key it touches the edge line
        body = sw.local_box(*SOCKET_BODY)
        assert body.within(board.outline.buffer(0.2)), f"{sw.ref}: socket body leaves the board outline"
        for number in ("1", "2"):
            assert sw.pad(number, "B.Cu").poly().buffer(-0.01).within(body.buffer(0.1)), f"{sw.ref} pad {number} outside the socket body"


def _inv(fp: Footprint, x: float, y: float) -> tuple[float, float]:
    """Page coordinates back to footprint-local."""
    th = math.radians(fp.rot)
    dx, dy = x - fp.x, y - fp.y
    return (dx * math.cos(th) - dy * math.sin(th), dx * math.sin(th) + dy * math.cos(th))


def test_socket_back_pads_are_wired(board):
    """The sockets sit on the back: both back pads of every switch must be hit by copper
    (pad 1 by the locked stub to the joiner, pad 2 by a routed track)."""
    ends = [(a, b) for lay, _, _, a, b in board.segments if lay == "B.Cu"]
    for sw in board.by_prefix("SW"):
        for number in ("1", "2"):
            p = sw.pad(number, "B.Cu")
            poly = p.poly()
            hit = any(poly.intersects(Point(e)) for a, b in ends for e in (a, b))
            assert hit, f"{sw.ref}: back pad {number} ({p.net}) is not reached by a B.Cu track"


def test_socket_bodies_do_not_collide(board):
    """Socket plastic bodies versus everything else assembled on the back and the case holes."""
    bodies = {sw.ref: sw.local_box(*SOCKET_BODY) for sw in board.by_prefix("SW")}
    refs = list(bodies)
    for i, a in enumerate(refs):
        for b in refs[i + 1:]:
            assert not bodies[a].intersects(bodies[b]), f"sockets {a} and {b} overlap"
    others = {ref: fp.courtyard("B.CrtYd") for ref, fp in board.footprints.items()
              if ref in ("J1", "J3", "PS1", "RB1") and fp.courtyard("B.CrtYd")}
    for ref, body in bodies.items():
        for oref, cy in others.items():
            assert not body.intersects(cy), f"socket {ref} overlaps the courtyard of {oref}"


# ----- FPC connector (right board) -----------------------------------------------------
def test_fpc_connector_orientation(board, layout, half):
    if half != "right":
        pytest.skip("no FPC connector on the left board")
    j1 = board.footprints["J1"]
    f = layout.cfg["fpc"]
    assert (j1.x, j1.y) == _board(layout, f["center"]["x"], f["center"]["y"]) and j1.rot == f["rotation"]
    # r2.2: J1 lives on the key side so the lock can be reached with the case assembled; the
    # cable climbs the gap beside the cradle cup and folds over the notch edge into the mouth.
    assert j1.name == "FPC_0.5mm_6P_FH12-6S_top"
    assert all("F.Cu" in p.layers and "B.Cu" not in p.layers for p in j1.pads), "front face only"
    contacts = sorted((p for p in j1.pads if p.number), key=lambda p: p.x)
    assert [p.number for p in contacts] == ["1", "2", "3", "4", "5", "6"], "pin 1 at -x: a front-face part is not mirrored"
    assert [p.net for p in sorted(contacts, key=lambda p: int(p.number))] == [FPC_PINS[i] for i in range(1, 7)]
    anchors = [p for p in j1.pads if not p.number]
    # contacts and lock towards the keys (-y), hold-down pads and the cable mouth towards the notch (+y)
    assert all(p.y < j1.y for p in contacts) and all(p.y > j1.y for p in anchors)
    body_top = max(y for g in j1.lines("F.Fab") for _, y in g.pts) - OFFSET[1]
    edge = layout.outline.exterior.distance(Point(f["center"]["x"], body_top))
    assert 0.3 <= edge <= 1.5, f"cable mouth {edge:.2f} mm from the PCB edge: the cable cannot fold into it"
    cap_gap = min(layout.keycap_polygon(k).distance(layout.fpc_box()) for k in layout.keys)
    assert cap_gap >= 0.5, f"J1 only {cap_gap:.2f} mm from a keycap: no room to work the lock"
    assert "1" in {g.text for g in j1.graphics if g.kind == "text" and g.layer == "F.SilkS"}, "pin 1 marker on the front silkscreen"


# ----- controller ------------------------------------------------------------------------
def _spec_pin_rows() -> dict[str, str]:
    """Pro Micro pin -> signal from the single pin table in section 2 of the spec."""
    sec = SPEC.read_text().split("## 2.")[1].split("## 3.")[0]
    out = {}
    for line in sec.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if len(cells) >= 2 and re.fullmatch(r"D\d+|RAW|GND|RST|VCC", cells[1]):
            out[cells[1]] = cells[0]
    return out


def test_controller_hole_nets_follow_the_spec(board, half):
    u1 = board.footprints["U1"]
    pins = _spec_pin_rows()
    assert {"RAW", "GND", "RST", "VCC"} <= set(pins)
    expected = hole_net(half)
    for h in range(1, 25):
        pad = u1.pad(str(h), "F.Cu")
        pin = HOLE_PIN[h]
        assert pad.net == expected[h], f"hole {h} ({pin}) carries {pad.net}, expected {expected[h]}"
        signal = pins.get(pin, "")
        if m := re.match(r"(COL\d|ROW\d)", signal):
            assert pad.net == m.group(1)
        elif m := re.match(r"(TB_\w+)", signal):
            assert pad.net == (m.group(1) if half == "right" else f"TP_{pin}")
        elif pin in ("RAW", "GND", "RST", "VCC"):
            assert pad.net == pin
        else:
            assert pad.net == f"TP_{pin}", f"spare pin {pin} should end on a test pad net"
    # RAW / GND / RST / VCC are the top four holes of the right-hand column (holes 13 to 16);
    # the footprint is not mirrored, so this column is at +x of U1 on both boards
    right_col = sorted((u1.pad(str(h), "F.Cu") for h in range(13, 25)), key=lambda p: p.y)
    assert [p.net for p in right_col[:4]] == ["RAW", "GND", "RST", "VCC"]
    assert all(p.x > u1.x for p in right_col)
    assert u1.pad("1", "F.Cu").shape == "rect", "square pad marks hole 1 (D1)"


def test_controller_pin_labels(board):
    u1 = board.footprints["U1"]
    labels = [g for g in u1.graphics if g.kind == "text" and g.layer == "F.SilkS" and g.text in HOLE_PIN.values()]
    assert len(labels) == 24
    for h in range(1, 25):
        pad = u1.pad(str(h), "F.Cu")
        near = min(labels, key=lambda g: math.dist(g.pts[0], (pad.x, pad.y)))
        assert near.text == HOLE_PIN[h], f"label next to hole {h} reads {near.text}"
        assert math.isclose(near.pts[0][1], pad.y, abs_tol=0.01)
        assert (near.pts[0][0] > pad.x) == (h <= 12), "labels sit inboard of their hole row"
    assert not any(g.kind == "text" and g.layer == "B.SilkS" and g.text in HOLE_PIN.values() for g in u1.graphics)


def test_controller_usb_end_at_the_top_edge(board, layout):
    u1 = board.footprints["U1"]
    assert u1.rot == 0
    body_top = min(y for g in u1.lines("F.Fab") for _, y in g.pts)
    body_bottom = max(y for g in u1.lines("F.Fab") for _, y in g.pts)
    edge_top = _edge_y_top(board.outline, u1.x)
    assert body_top - edge_top < 3.0, "USB end faces the top board edge"
    assert body_bottom < board.outline.bounds[3] - 20, "the other end is deep inside the controller block"
    usb = [g for g in u1.graphics if g.kind == "text" and g.text == "USB" and g.layer == "F.SilkS"]
    assert usb and usb[0].pts[0][1] < u1.y - 10
    assert board.outline.contains(Point(usb[0].pts[0])), "the USB marker is on the board"


def test_controller_usb_overhang_per_spec(board, layout):
    u1 = board.footprints["U1"]
    body_top = min(y for g in u1.lines("F.Fab") for _, y in g.pts)
    edge_top = _edge_y_top(board.outline, u1.x)
    overhang = layout.cfg["controller"]["usb_overhang"]
    # the nice!nano USB-C shell protrudes about 1.3 mm past its PCB: the PCB end must sit outside the edge
    assert edge_top - body_top >= overhang - 1.3 - 0.1, f"controller PCB end is {body_top - edge_top:.2f} mm inside the edge"


# ----- battery bay ---------------------------------------------------------------------
def test_owner_wordmark_on_back_silkscreen(board):
    """The wordmark (spec/images/logo.svg) is a set of filled polygons on B.SilkS under the
    thumb bridge: the same artwork as the case engraving, nowhere near a pad, and with strokes
    a fab can hold. Drawn board-level, so it adds no footprint and no schematic parity item."""
    from shapely.ops import unary_union

    from k0d3.geometry import load_layout
    from k0d3.logo import placed_polygons

    cfg = load_layout(board.half).cfg["silkscreen"]["logo"]
    expected = placed_polygons(cfg["cell"], cfg["rotation"], cfg["layer"].startswith("B."))
    marks = [p for layer, stroke, p in board.gr_polys if layer == "B.SilkS" and stroke != "dash"]
    assert len(marks) == len(expected), f"{board.half}: {len(marks)} wordmark polygons, expected {len(expected)}"
    mark = unary_union(marks)
    assert abs(mark.area - unary_union([Polygon(e) for e in expected]).area) < 0.01, "scaled differently"
    assert board.outline.buffer(-0.5).contains(mark), f"{board.half}: wordmark reaches the board edge"
    assert cfg["cell"] >= 0.2, "silkscreen strokes below what a fab holds"
    # pads are the copper that matters: tracks, vias and the pours are under soldermask, pads
    # are not, and silk on an exposed pad is what the fab and the DRC object to
    for layer in ("B.Cu", "F.Cu"):
        for what, poly in board.copper(layer):
            if " pad " not in what:
                continue
            assert not poly.intersects(mark), f"{board.half}: wordmark over {what}"


def test_battery_bay_on_back_silkscreen(board, layout, half):
    bay = _page(layout, layout.battery_bay())
    dashed = [p for layer, stroke, p in board.gr_polys if layer == "B.SilkS" and stroke == "dash"]
    assert any(p.symmetric_difference(bay).area < 1e-6 for p in dashed), "dashed bay rectangle on B.SilkS"
    assert tuple(round(v, 3) for v in bay.bounds) == {"right": (55.6, 57.0, 76.6, 98.0), "left": (163.4, 57.0, 184.4, 98.0)}[half]
    texts = {g.text for g in board.gr_texts if g.layer == "B.SilkS" and bay.contains(Point(g.pts[0]))}
    assert texts == {"LP552035 cell", "350 mAh", "leads +y"}
    assert bay.within(board.outline.buffer(-layout.cfg["battery"]["edge_clearance"] + 1e-6)), "bay keeps the edge clearance"


# Known defect on the left board (issues/hw-left-bay-inner-sockets.md): the hot-swap socket
# footprint is chiral and reaches 10.2 mm to local +x, which on the mirrored left board is
# towards the controller, so the inner column's sockets (SW04, SW14, SW24) overlap the battery
# bay rectangle by 2.8 mm (body) / 2.4 mm (pad 2). Bounded here until the ticket is resolved.
LEFT_BAY_SOCKET_INTRUSION = 2.85


def test_battery_bay_holds_nothing_but_u1(board, layout, half):
    bay = _page(layout, layout.battery_bay())
    for ref, fp in board.footprints.items():
        if ref == "U1":
            continue
        cy = fp.courtyard("B.CrtYd")
        assert cy is None or not cy.intersects(bay), f"{ref}: back courtyard reaches into the battery bay"
        known = half == "left" and ref in ("SW04", "SW14", "SW24")
        for p in fp.pads:
            if p.kind == "smd" and p.on("B.Cu") and not (known and p.number == "2"):
                assert not p.poly().intersects(bay), f"{ref} pad {p.number}: back SMD pad inside the battery bay"
        if ref.startswith("SW"):
            body = fp.local_box(*SOCKET_BODY)
            if known:
                depth = body.intersection(bay).bounds[2] - bay.bounds[0] if body.intersects(bay) else 0.0
                assert depth <= LEFT_BAY_SOCKET_INTRUSION, f"{ref}: socket body {depth:.2f} mm inside the battery bay"
            else:
                assert not body.intersects(bay), f"{ref}: socket body inside the battery bay"
    u1 = board.footprints["U1"]
    tails = [p for p in u1.pads if bay.contains(Point(p.x, p.y))]
    assert len(tails) >= 12, "the keys-side row of U1 socket tails is the only thing inside the bay (cut flush by hand)"


# ----- mounting holes ------------------------------------------------------------------
def test_mounting_holes(board, layout):
    holes = board.by_prefix("H")
    assert len(holes) == 5
    want = {_board(layout, h["x"], h["y"]) for h in layout.cfg["mounting_holes"]}
    assert {(fp.x, fp.y) for fp in holes} == want
    for h in holes:
        npth = [p for p in h.pads if p.kind == "np_thru_hole"]
        assert len(npth) == 1 and npth[0].drill == 2.2 and len(h.pads) == 1
        centre = Point(h.x, h.y)
        assert board.outline.exterior.distance(centre) >= HOLE_RADIUS + 1.0, f"{h.ref} too close to the edge"
        for sw in board.by_prefix("SW"):
            body = sw.local_box(-6.9, -6.9, 6.9, 6.9)
            assert body.distance(centre) >= HOLE_RADIUS + 0.9, f"{h.ref} hits the switch body of {sw.ref}"
            # H1 passes 1.49 mm from the SW11 socket body: standoffs on the back must stay below 3 mm diameter there
            assert sw.local_box(*SOCKET_BODY).distance(centre) >= HOLE_RADIUS + 0.3, f"{h.ref} hits the socket of {sw.ref}"
        for d in board.by_prefix("D"):
            assert d.courtyard("B.CrtYd").distance(centre) >= HOLE_RADIUS + 0.5, f"{h.ref} hits {d.ref}"
        for layer in ("F.Cu", "B.Cu"):
            for desc, poly in board.copper(layer):
                if desc.startswith("zone"):
                    continue
                assert poly.distance(centre) >= HOLE_RADIUS + 0.25, f"{h.ref}: {desc} on {layer} is {poly.distance(centre) - HOLE_RADIUS:.2f} mm from the hole"
    all_22 = [(fp.ref, p) for fp in board.footprints.values() for p in fp.pads if p.kind == "np_thru_hole" and p.drill == 2.2]
    assert len(all_22) == 5 and all(ref.startswith("H") for ref, _ in all_22), "no cradle holes: the only 2.2 mm holes are the case holes"


# ----- power switch ----------------------------------------------------------------------
def test_power_switch_sits_at_the_inner_edge(board, layout):
    ps1 = board.footprints["PS1"]
    edge = _edge_x(layout, board.outline, ps1.y, "inner")
    assert abs(ps1.x - edge) < 4.0, "switch centre within 4 mm of the inner edge"
    for p in ps1.pads:
        if p.copper and p.on("B.Cu"):
            assert p.poly().distance(board.outline.exterior) >= EDGE_CLEARANCE - 1e-6, f"PS1 pad {p.number} too close to the edge"
    assert ps1.pad("1", "B.Cu").net == "RAW" and ps1.pad("2", "B.Cu").net == "BAT+"


def test_power_switch_actuator_points_through_the_inner_edge(board, layout):
    ps1 = board.footprints["PS1"]
    sx = layout.board_sx                    # inner edge is -x on the right board, +x on the left
    edge = _edge_x(layout, board.outline, ps1.y, "inner")
    tip_x = ps1.local(0.0, 2.9)[0]          # end of the actuator drawing (local +y)
    pads_x = ps1.pad("2", "B.Cu").x
    assert sx * tip_x < sx * ps1.x < sx * pads_x, "actuator towards the inner edge, solder pads inboard"
    assert sx * (tip_x - edge) <= 0.5, f"actuator tip stops {sx * (tip_x - edge):.2f} mm short of the inner edge"


# ----- diodes --------------------------------------------------------------------------
def test_diode_orientation(board, layout):
    for k in layout.keys:
        d = board.footprints[k.diode_ref]
        for layer in ("F.Cu", "B.Cu"):
            assert d.pad("1", layer).net == f"ROW{k.row}", f"{d.ref}: cathode (pad 1) must be on ROW{k.row}"
            assert d.pad("2", layer).net == k.net, f"{d.ref}: anode (pad 2) must be on {k.net}"
        cathode = d.pad("1", "F.Cu")
        bars = [g for g in d.lines("F.SilkS") if math.isclose(math.dist(*g.pts), 1.9, abs_tol=0.01)]
        assert len(bars) == 1, f"{d.ref}: one cathode bar on the front silkscreen"
        bar_mid = ((bars[0].pts[0][0] + bars[0].pts[1][0]) / 2, (bars[0].pts[0][1] + bars[0].pts[1][1]) / 2)
        assert math.dist(bar_mid, (cathode.x, cathode.y)) < math.dist(bar_mid, (d.pad("2", "F.Cu").x, d.pad("2", "F.Cu").y))
        # the diode follows the switch rotation (sign flipped with the mirror on the left) and sits 6 mm towards the user
        assert d.rot % 360 == (layout.board_sx * k.rotation) % 360


# ----- silkscreen ----------------------------------------------------------------------
def test_silkscreen_texts(board, layout, half):
    front = {g.text for g in board.gr_texts if g.layer == "F.SilkS"}
    assert f"{half.upper()} half" in front
    title = [t for t in front if t.startswith("k0d3ball35")]
    assert title and layout.cfg["silkscreen"]["revision_text"] in title[0] and "CERN-OHL-P-2.0" in title[0]
    for g in board.gr_texts:
        if g.layer.endswith("SilkS"):
            assert board.outline.contains(Point(g.pts[0])), f"text {g.text!r} off the board"
    ps1 = board.footprints["PS1"]
    assert [g.layer for g in ps1.graphics if g.kind == "text" and g.text == "ON"] == ["F.SilkS", "B.SilkS"]


def _drc(kicad_cli: str, half: str) -> dict:
    report = REPO / "build" / f"{half}.review.drc.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([kicad_cli, "pcb", "drc", "--severity-all", "--format", "json", "-o", str(report), str(BOARDS[half])],
                   capture_output=True, text=True)
    return json.loads(report.read_text(encoding="utf-8"))


# Silkscreen over exposed copper that was looked at and accepted as cosmetic (clipped by the
# mask, no solder joint affected). Pairs are (first item, second item) regex fragments.
SILK_OVER_COPPER_ACCEPTED = [
    (r"Reference field of TP\d", r"Pad 1 \[TP_D\d+\] of TP\d"),             # TPn label touches the neighbouring test pad
    (r"PCB text 'k0d3ball35 r2", r"(Pad 2 \[SW24\] of SW24 on F.Cu|NPTH pad of SW24)"),  # title under the SW24 keycap
    (r"Polygon on B.Silkscreen", r"PTH pad (1|12|13|24) \[.*\] of U1"),      # dashed bay outline crosses the corner holes of both rows
    (r"Polygon on B.Silkscreen", r"Pad 2 \[SW\d4\] of SW\d4 on B.Cu"),        # left board: inner column sockets reach into the bay (hw-left-bay-inner-sockets)
    # the U1 silkscreen box ends 2 mm above the power switch; its bottom line touches the PS1 pads
    # (clipped by the mask subtraction, no effect on the fab)
    (r"Segment of U1 on [FB].Silkscreen", r"Pad ?(1 \[RAW\]|3 \[<no net>\]|\[<no net>\]) of PS1 on [FB].Cu"),
]


@pytest.mark.kicad
def test_silk_over_copper_only_known_cosmetic(kicad_cli, half):
    data = _drc(kicad_cli, half)
    unexpected = []
    for v in data.get("violations", []):
        if v.get("type") not in ("silk_over_copper", "silk_overlap"):
            continue
        items = [i.get("description", "") for i in v.get("items", [])]
        if v["type"] == "silk_overlap" and any("Polygon on B.Silkscreen" in i for i in items):
            continue  # the bay outline crosses U1's own silkscreen rectangle
        if not any(re.search(a, items[0]) and re.search(b, items[1]) for a, b in SILK_OVER_COPPER_ACCEPTED):
            unexpected.append(f"{v['type']}: {items}")
    assert not unexpected, f"{half}: silkscreen over copper that was not reviewed:\n" + "\n".join(unexpected)
    # nothing silk-related may be an error and no silk over the solder pads of the connectors
    for v in data.get("violations", []):
        if v.get("type", "").startswith("silk"):
            assert v.get("severity") != "error"
            assert not any(re.search(r"of (J1|J3|RB1) ", i.get("description", "")) for i in v.get("items", []))


# ----- copper to edge, notch, holes -------------------------------------------------------
def test_copper_keeps_edge_clearance(board):
    edge = board.outline.exterior
    for layer in ("F.Cu", "B.Cu"):
        for desc, poly in board.copper(layer):
            assert poly.within(board.outline), f"{board.half}: {desc} on {layer} leaves the board"
            d = poly.distance(edge)
            assert d >= EDGE_CLEARANCE - 0.005, f"{board.half}: {desc} on {layer} is {d:.3f} mm from the edge (minimum {EDGE_CLEARANCE})"
    for fp in board.footprints.values():
        for p in fp.pads:
            if p.kind == "np_thru_hole":
                assert Point(p.x, p.y).buffer(p.drill / 2).within(board.outline.buffer(-0.2)), f"{fp.ref}: hole too close to the edge"


def test_zones_are_filled(board):
    for net, layer, polys in board.zones:
        assert net == "GND" and polys, f"{layer} pour is not filled"
        assert sum(p.area for p in polys) > 0.25 * board.outline.area, f"{layer} pour covers too little of the board"


def test_octagonal_notch(board, layout, half):
    if half != "right":
        assert not layout.has_ball
        return
    notch = _page(layout, layout.notch_polygon())
    assert notch.intersection(board.outline).area < 1e-3, "no board material inside the notch"
    # only the part of the octagon that lies inside the un-notched board shows up as edge
    shared = notch.exterior.intersection(board.outline.exterior).length
    assert shared > 5, f"notch edge shares only {shared:.1f} mm with the outline"
    on_octagon = [v for v in board.outline.exterior.coords if notch.exterior.distance(Point(v)) < 1e-3]
    assert len(on_octagon) >= 3, "the outline has vertices on the octagon"
    apothem = layout.cfg["trackball"]["cradle_diameter"] / 2 + layout.cfg["trackball"]["pocket"]["notch_clearance"]
    assert apothem == 15.0
    grown = notch.buffer(EDGE_CLEARANCE - 0.01)
    for layer in ("F.Cu", "B.Cu"):
        for desc, poly in board.copper(layer):
            assert not poly.intersects(grown), f"{desc} on {layer} inside the notch or within {EDGE_CLEARANCE} mm of it"
    for net, x, y, _, _ in board.vias:
        assert not grown.contains(Point(x, y))
    ball = _page(layout, Point(*layout.ball_center).buffer(layout.cfg["trackball"]["ball_diameter"] / 2))
    assert not ball.intersects(board.outline), "the ball itself clears the PCB"


def test_power_tracks_use_the_wide_class(board):
    for layer, net, width, a, b in board.segments:
        if net in ("RAW", "BAT+"):
            assert width >= 0.4 - 1e-6, f"{net} track on {layer} at {a} is only {width} mm wide"
        assert width >= 0.15 - 1e-6


def test_gnd_zones_have_no_slivers(board):
    """Every filled GND polygon is anchored by a GND via or pad, and anything smaller than a
    real pour is only the copper remnant around such an anchor.

    An anchor is a GND pad, via or track: that is also how KiCad decides what counts as an
    island. Dropping islands in the fill settings is not an option, KiCad then reports every
    tagged island as a missing zone connection. Ticket hw-gnd-stitching-review."""
    min_area = 2.0
    max_remnants = 4        # anchored sub-millimetre remnants per face
    anchors = {layer: [] for layer in ("F.Cu", "B.Cu")}
    for net, x, y, _, _ in board.vias:
        if net == "GND":
            for layer in anchors:
                anchors[layer].append(Point(x, y).buffer(0.05))
    for fp in board.footprints.values():
        for pad in fp.pads:
            if pad.net == "GND" and pad.copper:
                for layer in anchors:
                    if pad.on(layer):
                        anchors[layer].append(pad.poly())
    # GND tracks count as a connection too (that is how KiCad decides what is an island)
    for layer, net, width, a, b in board.segments:
        if net == "GND" and layer in anchors:
            anchors[layer].append(LineString([a, b]).buffer(width / 2))
    for net, layer, polys in board.zones:
        if net != "GND" or layer not in anchors:
            continue
        remnants = []
        for raw in polys:
            # KiCad joins holes to the outline with zero-width slits; buffer(0) repairs that
            poly = raw.buffer(0) if not raw.is_valid else raw
            assert not poly.is_empty, f"{board.half} {layer}: unrepairable GND fill polygon"
            grown = poly.buffer(0.05)
            assert any(grown.intersects(a) for a in anchors[layer]), \
                f"{board.half} {layer}: isolated GND island of {poly.area:.1f} mm2 at {poly.centroid.coords[0]}"
            if poly.area < min_area:
                assert poly.area > 0.05, \
                    f"{board.half} {layer}: hairline GND fill of {poly.area:.3f} mm2 at {poly.centroid.coords[0]}"
                remnants.append(round(poly.area, 2))
        assert len(remnants) <= max_remnants, \
            f"{board.half} {layer}: {len(remnants)} GND fill remnants {remnants}, more than {max_remnants}"


def test_drills_keep_the_board_minimum_hole_to_hole(board, half):
    """No two holes closer than the board's `min_hole_to_hole` (0.5 mm), whatever their nets.

    KiCad only reports this between different nets, but a drill that close to another breaks
    whether or not the copper belongs together: the autorouter put a GND via 0.2256 mm from a
    GND stitching via on the right board, and a 0.3 mm via 0.498 mm inside U1's 1.0 mm pad hole
    (see the ticket). The limit is read from the project file, which carries JLCPCB's 0.5 mm
    rather than KiCad's default, so this test follows it. `route.stitch_ground` skips grid points
    that land next to an existing hole, and `route.drop_crowded_ground_vias` removes the ones the
    router placed itself, which no input to freerouting can prevent.
    """
    import json

    limit = json.loads(BOARDS[half].with_suffix(".kicad_pro").read_text())["board"]["design_settings"]["rules"]["min_hole_to_hole"]
    holes = [(x, y, drill / 2, f"via {net}") for net, x, y, _, drill in board.vias]
    for fp in board.footprints.values():
        for pad in fp.pads:
            if pad.drill:
                holes.append((pad.x, pad.y, pad.drill / 2, f"{fp.ref} pad {pad.number}"))
    holes.sort()
    for i, (x1, y1, r1, a) in enumerate(holes):
        for x2, y2, r2, b in holes[i + 1:]:
            if x2 - x1 >= limit + r1 + r2:
                break
            gap = math.dist((x1, y1), (x2, y2)) - r1 - r2
            assert gap >= limit - 1e-6, \
                f"{half}: {a} and {b} are {gap:.4f} mm hole to hole at ({x1 - OFFSET[0]:.2f}, {y1 - OFFSET[1]:.2f})"


def test_no_signal_net_piles_up_vias(board):
    """Step 6 of the review: more than five vias on one signal net means the router took a
    detour worth looking at. SW33 on the left board is at five (a 10 degree thumb key whose
    front and back socket pads sit on either side of the diode); everything else is at three
    or fewer."""
    count = {}
    for net, _, _, _, _ in board.vias:
        if net not in ("GND", ""):
            count[net] = count.get(net, 0) + 1
    worst = sorted(count.items(), key=lambda kv: -kv[1])[:3]
    assert all(n <= 5 for _, n in count.items()), f"{board.half}: via pile-up {worst}"
