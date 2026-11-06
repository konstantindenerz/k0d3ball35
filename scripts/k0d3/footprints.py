# SPDX-License-Identifier: CERN-OHL-P-2.0
"""Footprints for the k0d3ball35 main PCBs.

All footprints are described in the board frame with x outward, y towards the user and
the component side = F (switches on top, sockets and small parts on the back). The
footprints were designed for the reversible r1 board and keep their pads on both faces:

* parts whose pin order is handed (hot-swap socket, slide switch, JST)
  have a mirrored pad set on the back (x -> -x, same pad numbers);
* symmetric parts (diode, test pads, reset button) have the same pad positions on both
  faces.

Since r2 the two halves are separate boards, so only one face of each pad set is used;
the second copy is harmless (same net on both faces) and keeps the freedom to mount a
socket on either face. The FPC connector is the exception (back face only). Pad geometry comes from the KiCad standard library, kiswitch and
marbastlib (all permissive licences, see NOTICE).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .sexpr import num, quote, uid

VERSION = "20240108"  # KiCad 8 file format; KiCad 10 reads and upgrades it

F_SMD = ("F.Cu", "F.Paste", "F.Mask")
B_SMD = ("B.Cu", "B.Paste", "B.Mask")
THT = ("*.Cu", "*.Mask")


@dataclass
class Pad:
    number: str
    kind: str                  # smd | thru_hole | np_thru_hole
    shape: str                 # circle | rect | roundrect | oval
    x: float
    y: float
    w: float
    h: float
    layers: tuple[str, ...]
    drill: float | None = None
    rratio: float | None = None
    rot: float = 0.0
    zone_connect: int | None = None   # 2 = solid connection to copper pours

    def mirrored(self) -> "Pad":
        layers = tuple(l.replace("F.", "B.") if l.startswith("F.") else l for l in self.layers)
        return Pad(self.number, self.kind, self.shape, -self.x, self.y, self.w, self.h, layers, self.drill, self.rratio, -self.rot, self.zone_connect)

    def flipped_layers(self) -> "Pad":
        layers = tuple(l.replace("F.", "B.") if l.startswith("F.") else l for l in self.layers)
        return Pad(self.number, self.kind, self.shape, self.x, self.y, self.w, self.h, layers, self.drill, self.rratio, self.rot, self.zone_connect)


@dataclass
class Line:
    x1: float
    y1: float
    x2: float
    y2: float
    layer: str
    width: float = 0.12


@dataclass
class Circle:
    cx: float
    cy: float
    r: float
    layer: str
    width: float = 0.12


@dataclass
class Text:
    text: str
    x: float
    y: float
    layer: str
    size: float = 0.8
    rot: float = 0.0


@dataclass
class Footprint:
    name: str
    descr: str
    attr: str                  # smd | through_hole
    pads: list[Pad] = field(default_factory=list)
    graphics: list = field(default_factory=list)
    ref_layer: str = "F.Fab"
    ref_offset: tuple[float, float] = (0.0, 0.0)

    # ----- emitters ---------------------------------------------------------------
    def _graphic_sexpr(self, g, owner: str) -> str:
        if isinstance(g, Line):
            return (f"    (fp_line (start {num(g.x1)} {num(g.y1)}) (end {num(g.x2)} {num(g.y2)}) "
                    f"(stroke (width {num(g.width)}) (type default)) (layer {quote(g.layer)}) (uuid {quote(uid(owner, 'l', g.x1, g.y1, g.x2, g.y2, g.layer))}))")
        if isinstance(g, Circle):
            return (f"    (fp_circle (center {num(g.cx)} {num(g.cy)}) (end {num(g.cx + g.r)} {num(g.cy)}) "
                    f"(stroke (width {num(g.width)}) (type default)) (fill none) (layer {quote(g.layer)}) (uuid {quote(uid(owner, 'c', g.cx, g.cy, g.r, g.layer))}))")
        if isinstance(g, Text):
            mirror = " (justify mirror)" if g.layer.startswith("B.") else ""
            return (f"    (fp_text user {quote(g.text)} (at {num(g.x)} {num(g.y)} {num(g.rot)}) (layer {quote(g.layer)}) "
                    f"(uuid {quote(uid(owner, 't', g.text, g.x, g.y, g.layer))}) "
                    f"(effects (font (size {num(g.size)} {num(g.size)}) (thickness {num(g.size * 0.15)})){mirror}))")
        raise TypeError(g)

    def _pad_sexpr(self, p: Pad, owner: str, net: tuple[int, str] | None, fp_rot: float) -> str:
        layers = " ".join(quote(l) for l in p.layers)
        rot = fp_rot + p.rot
        at = f"(at {num(p.x)} {num(p.y)}" + (f" {num(rot)})" if abs(rot) > 1e-9 else ")")
        parts = [f"    (pad {quote(p.number)} {p.kind} {p.shape} {at} (size {num(p.w)} {num(p.h)})"]
        if p.drill is not None:
            parts.append(f"(drill {num(p.drill)})")
        parts.append(f"(layers {layers})")
        if p.kind == "thru_hole":
            parts.append("(remove_unused_layers no)")
        if p.shape == "roundrect":
            parts.append(f"(roundrect_rratio {num(p.rratio or 0.25)})")
        if p.zone_connect is not None:
            parts.append(f"(zone_connect {p.zone_connect})")
        if net is not None and p.number:
            parts.append(f"(net {net[0]} {quote(net[1])})")
        parts.append(f"(uuid {quote(uid(owner, 'p', p.number, p.x, p.y, p.layers[0]))}))")
        return " ".join(parts)

    def library_sexpr(self, lib: str) -> str:
        out = [f"(footprint {quote(self.name)} (version {VERSION}) (generator {quote('k0d3ball35')}) (generator_version {quote('1.0')})",
               f"  (layer \"F.Cu\")", f"  (descr {quote(self.descr)})", f"  (tags {quote('k0d3ball35')})",
               f"  (property \"Reference\" \"REF**\" (at {num(self.ref_offset[0])} {num(self.ref_offset[1])} 0) (layer {quote(self.ref_layer)}) (uuid {quote(uid(self.name, 'ref'))}) (effects (font (size 1 1) (thickness 0.15))))",
               f"  (property \"Value\" {quote(self.name)} (at 0 2 0) (layer \"F.Fab\") (uuid {quote(uid(self.name, 'val'))}) (effects (font (size 1 1) (thickness 0.15))))",
               f"  (property \"Footprint\" {quote(lib + ':' + self.name)} (at 0 0 0) (layer \"F.Fab\") (hide yes) (uuid {quote(uid(self.name, 'fp'))}) (effects (font (size 1.27 1.27))))",
               f"  (property \"Datasheet\" \"\" (at 0 0 0) (layer \"F.Fab\") (hide yes) (uuid {quote(uid(self.name, 'ds'))}) (effects (font (size 1.27 1.27))))",
               f"  (property \"Description\" {quote(self.descr)} (at 0 0 0) (layer \"F.Fab\") (hide yes) (uuid {quote(uid(self.name, 'de'))}) (effects (font (size 1.27 1.27))))",
               f"  (attr {self.attr})"]
        out += [self._graphic_sexpr(g, self.name) for g in self.graphics]
        out += [self._pad_sexpr(p, self.name, None, 0.0) for p in self.pads]
        out.append(")")
        return "\n".join(out) + "\n"

    def board_sexpr(self, lib: str, ref: str, value: str, x: float, y: float, rot: float,
                    nets: dict[str, tuple[int, str]], path_uuid: str, sheetfile: str, descr: str = "") -> str:
        fid = uid("fp", ref)
        at = f"(at {num(x)} {num(y)}" + (f" {num(rot)})" if abs(rot) > 1e-9 else ")")
        out = [f"  (footprint {quote(lib + ':' + self.name)} (layer \"F.Cu\") (uuid {quote(fid)}) {at}",
               f"    (descr {quote(descr or self.descr)})", f"    (tags {quote('k0d3ball35')})",
               f"    (property \"Reference\" {quote(ref)} (at {num(self.ref_offset[0])} {num(self.ref_offset[1])} {num(rot)}) (layer {quote(self.ref_layer)}) (uuid {quote(uid(fid, 'ref'))}) (effects (font (size 0.8 0.8) (thickness 0.12))))",
               f"    (property \"Value\" {quote(value)} (at 0 2 {num(rot)}) (layer \"F.Fab\") (uuid {quote(uid(fid, 'val'))}) (effects (font (size 0.8 0.8) (thickness 0.12))))",
               f"    (property \"Footprint\" {quote(lib + ':' + self.name)} (at 0 0 {num(rot)}) (layer \"F.Fab\") (hide yes) (uuid {quote(uid(fid, 'fp'))}) (effects (font (size 1.27 1.27))))",
               f"    (property \"Datasheet\" \"\" (at 0 0 {num(rot)}) (layer \"F.Fab\") (hide yes) (uuid {quote(uid(fid, 'ds'))}) (effects (font (size 1.27 1.27))))",
               f"    (property \"Description\" {quote(descr or self.descr)} (at 0 0 {num(rot)}) (layer \"F.Fab\") (hide yes) (uuid {quote(uid(fid, 'de'))}) (effects (font (size 1.27 1.27))))",
               f"    (path {quote('/' + path_uuid)})", f"    (sheetname \"/\")", f"    (sheetfile {quote(sheetfile)})",
               f"    (attr {self.attr})"]
        out += [self._graphic_sexpr(g, fid) for g in self.graphics]
        out += [self._pad_sexpr(p, fid, nets.get(p.number) if p.number else None, rot) for p in self.pads]
        out.append("  )")
        return "\n".join(out)


# ----- helpers ----------------------------------------------------------------------
def rect_lines(cx: float, cy: float, w: float, h: float, layer: str, width: float = 0.1) -> list[Line]:
    x1, y1, x2, y2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    return [Line(x1, y1, x2, y1, layer, width), Line(x2, y1, x2, y2, layer, width),
            Line(x2, y2, x1, y2, layer, width), Line(x1, y2, x1, y1, layer, width)]


def both_faces(pads: list[Pad], mirror: bool) -> list[Pad]:
    """Return F pads plus their B counterparts (mirrored or not)."""
    back = [p.mirrored() if mirror else p.flipped_layers() for p in pads]
    return pads + back


def both_face_graphics(gfx: list, mirror: bool) -> list:
    out = list(gfx)
    for g in gfx:
        if isinstance(g, Line):
            out.append(Line(-g.x1 if mirror else g.x1, g.y1, -g.x2 if mirror else g.x2, g.y2, g.layer.replace("F.", "B."), g.width))
        elif isinstance(g, Circle):
            out.append(Circle(-g.cx if mirror else g.cx, g.cy, g.r, g.layer.replace("F.", "B."), g.width))
        elif isinstance(g, Text):
            out.append(Text(g.text, -g.x if mirror else g.x, g.y, g.layer.replace("F.", "B."), g.size, -g.rot if mirror else g.rot))
    return out


# ----- footprint definitions ---------------------------------------------------------
def choc_v1_hotswap_reversible() -> Footprint:
    """Kailh Choc V1 with hot-swap socket, reversible.

    Right half: switch from the top (F), socket on the back (B) with the kiswitch pad
    geometry (pins north, at (0,-5.9) and (5,-3.8)). Left half: the board is flipped,
    the socket sits on F with mirrored pads and uses the hole at (-5,-3.8). All three
    pin holes are 3.05 mm non-plated holes for the socket bosses, so the board is
    hot-swap only (like the Keyball). The pad next to the centre pin is shifted 0.45 mm
    north and made a 2.0 mm pill so that it clears the mirrored boss hole by >= 0.25 mm.
    """
    pads = [
        Pad("", "np_thru_hole", "circle", 0, 0, 3.4, 3.4, THT, 3.4),
        Pad("", "np_thru_hole", "circle", -5.5, 0, 1.7, 1.7, THT, 1.7),
        Pad("", "np_thru_hole", "circle", 5.5, 0, 1.7, 1.7, THT, 1.7),
        Pad("", "np_thru_hole", "circle", 0, -5.9, 3.05, 3.05, THT, 3.05),
        Pad("", "np_thru_hole", "circle", 5.0, -3.8, 3.05, 3.05, THT, 3.05),
        Pad("", "np_thru_hole", "circle", -5.0, -3.8, 3.05, 3.05, THT, 3.05),
    ]
    # Plated joiner pad for pin 1: ties the front and back socket pads of pin 1 together so
    # the column line only needs to reach one of them (the PCB generator adds the stubs).
    pads.append(Pad("1", "thru_hole", "circle", -2.2, -8.0, 0.8, 0.8, THT, 0.4))
    back = [
        Pad("1", "smd", "roundrect", -3.5, -6.45, 2.55, 2.0, B_SMD, rratio=0.5),
        Pad("2", "smd", "roundrect", 8.5, -3.8, 2.55, 2.5, B_SMD, rratio=0.1),
    ]
    front = [Pad(p.number, p.kind, p.shape, -p.x, p.y, p.w, p.h,
                 tuple(l.replace("B.", "F.") for l in p.layers), p.drill, p.rratio) for p in back]
    gfx = rect_lines(0, 0, 13.8, 13.8, "F.Fab", 0.1) + rect_lines(0, 0, 13.8, 13.8, "B.Fab", 0.1)
    gfx += rect_lines(0, 0, 14.4, 14.4, "F.CrtYd", 0.05) + rect_lines(0, 0, 14.4, 14.4, "B.CrtYd", 0.05)
    sock = [Line(-4.8, -8.9, 10.2, -8.9, "B.Fab"), Line(10.2, -8.9, 10.2, -2.0, "B.Fab"),
            Line(10.2, -2.0, -4.8, -2.0, "B.Fab"), Line(-4.8, -2.0, -4.8, -8.9, "B.Fab")]
    gfx += sock + [Line(-l.x1, l.y1, -l.x2, l.y2, "F.Fab") for l in sock]
    return Footprint("SW_Choc_V1_HS_reversible",
                     "Kailh Choc V1 (PG1350) with CPG135001S30 hot-swap socket on either face, hot-swap only",
                     "through_hole", pads + back + front, gfx, "F.Fab", (0, 0))


def sod123_reversible() -> Footprint:
    pads_f = [Pad("1", "smd", "roundrect", -1.65, 0, 0.9, 1.2, F_SMD, rratio=0.25),
              Pad("2", "smd", "roundrect", 1.65, 0, 0.9, 1.2, F_SMD, rratio=0.25)]
    pads = both_faces(pads_f, mirror=False)
    pads += [Pad("1", "thru_hole", "circle", -1.65, 0, 0.9, 0.9, THT, 0.4),
             Pad("2", "thru_hole", "circle", 1.65, 0, 0.9, 0.9, THT, 0.4)]
    gfx_f = [Line(-2.35, -0.95, 1.35, -0.95, "F.SilkS"), Line(-2.35, 0.95, 1.35, 0.95, "F.SilkS"),
             Line(-2.35, -0.95, -2.35, 0.95, "F.SilkS", 0.2)] + rect_lines(0, 0, 2.8, 1.8, "F.Fab", 0.1) + rect_lines(0, 0, 4.6, 1.9, "F.CrtYd", 0.05)
    gfx = both_face_graphics(gfx_f, mirror=False)
    return Footprint("D_SOD-123_reversible", "1N4148W in SOD-123, pads on both faces joined by small plated holes, cathode = pad 1",
                     "smd", pads, gfx, "F.Fab", (0, -1.6))


def nice_nano_tht(hole_pin: dict[int, str]) -> Footprint:
    pads = []
    for h in range(1, 25):
        col = -7.62 if h <= 12 else 7.62
        row = (h - 1) % 12
        y = -13.97 + row * 2.54
        shape = "rect" if h == 1 else "circle"
        pads.append(Pad(str(h), "thru_hole", shape, col, y, 1.7, 1.7, THT, 1.0, zone_connect=2 if h in (2, 14) else None))
    gfx = rect_lines(0, -0.6, 18.0, 33.5, "F.Fab", 0.1) + rect_lines(0, -0.6, 18.0, 33.5, "B.Fab", 0.1)
    gfx += rect_lines(0, -0.6, 19.0, 36.0, "F.CrtYd", 0.05) + rect_lines(0, -0.6, 19.0, 36.0, "B.CrtYd", 0.05)
    gfx += rect_lines(0, -0.6, 18.0, 33.5, "F.SilkS", 0.12) + rect_lines(0, -0.6, 18.0, 33.5, "B.SilkS", 0.12)
    gfx += [Text("USB", 0, -15.8, "F.SilkS", 0.8), Text("USB", 0, -15.8, "B.SilkS", 0.8)]
    for h in range(1, 25):
        col = -7.62 if h <= 12 else 7.62
        y = -13.97 + ((h - 1) % 12) * 2.54
        tx = col + (2.3 if h <= 12 else -2.3)
        gfx.append(Text(hole_pin[h], tx, y, "F.SilkS", 0.6))
    return Footprint("nice_nano_v2_THT", "nice!nano v2 / SuperMini nRF52840, 2x12 2.54 mm through holes, USB at the top, component side up",
                     "through_hole", pads, gfx, "F.SilkS", (0, -18.6))


def fpc_fh12_6_bottom() -> Footprint:
    """Hirose FH12-6S-0.5SH on the back face only (the sensor cable enters from the pocket).

    Pad geometry as seen from the front, so the pad set is the mirror image of the
    connector's own drawing: pad 1 at +x. The 0.5 mm pitch leaves no room for a second
    pad set on the front, which is why this is the one part without a two-face footprint.
    """
    pads_f = [Pad(str(i + 1), "smd", "rect", -1.25 + i * 0.5, -1.85, 0.3, 1.3, F_SMD, zone_connect=2) for i in range(6)]
    pads_f += [Pad("", "smd", "rect", -3.15, 1.4, 1.8, 2.2, F_SMD), Pad("", "smd", "rect", 3.15, 1.4, 1.8, 2.2, F_SMD)]
    pads = [p.mirrored() for p in pads_f]
    gfx_f = rect_lines(0, 0.6, 8.6, 4.8, "F.Fab", 0.1) + rect_lines(0, 0.6, 9.2, 5.6, "F.CrtYd", 0.05)
    gfx_f += [Line(-4.3, -1.8, -4.3, -2.6, "F.SilkS"), Line(-4.3, -2.6, -2.0, -2.6, "F.SilkS"), Text("1", -2.0, -3.3, "F.SilkS", 0.6)]
    gfx = [g for g in both_face_graphics(gfx_f, mirror=True) if g.layer.startswith("B.")]
    return Footprint("FPC_0.5mm_6P_FH12-6S_bottom", "Hirose FH12-6S-0.5SH (0.5 mm, 6 contacts, bottom contact), back face only",
                     "smd", pads, gfx, "B.Fab", (0, 4.2))


def battery_pads() -> Footprint:
    pads = [Pad("1", "thru_hole", "rect", -1.27, 0, 1.7, 1.7, THT, 1.0, zone_connect=2), Pad("2", "thru_hole", "circle", 1.27, 0, 1.7, 1.7, THT, 1.0, zone_connect=2)]
    gfx = [Text("+", -1.27, -1.8, "F.SilkS", 0.8), Text("-", 1.27, -1.8, "F.SilkS", 0.8),
           Text("+", -1.27, -1.8, "B.SilkS", 0.8), Text("-", 1.27, -1.8, "B.SilkS", 0.8)]
    gfx += rect_lines(0, 0, 4.6, 2.6, "F.CrtYd", 0.05) + rect_lines(0, 0, 4.6, 2.6, "B.CrtYd", 0.05)
    return Footprint("BatteryPads_2x1.8mm_P2.0mm", "Battery solder pads, B+ square pad, 2.54 mm pitch", "through_hole", pads, gfx, "F.SilkS", (0, 1.9))


def jst_ph_sm4_reversible() -> Footprint:
    pads_f = [Pad("1", "smd", "roundrect", -1.0, -2.85, 1.0, 3.5, F_SMD, rratio=0.25),
              Pad("2", "smd", "roundrect", 1.0, -2.85, 1.0, 3.5, F_SMD, rratio=0.25),
              Pad("", "smd", "roundrect", -3.35, 2.9, 1.5, 3.4, F_SMD, rratio=0.17),
              Pad("", "smd", "roundrect", 3.35, 2.9, 1.5, 3.4, F_SMD, rratio=0.17)]
    pads = both_faces(pads_f, mirror=True)
    gfx_f = rect_lines(0, 0.5, 8.0, 6.0, "F.Fab", 0.1) + rect_lines(0, 0.3, 9.4, 8.4, "F.CrtYd", 0.05) + [Text("1", -1.0, -5.4, "F.SilkS", 0.6)]
    gfx = both_face_graphics(gfx_f, mirror=True)
    return Footprint("JST_PH_S2B-PH-SM4-TB_reversible", "JST PH 2.0 mm S2B-PH-SM4-TB, side entry, pad sets on both faces (optional, 6 mm tall)",
                     "smd", pads, gfx, "F.Fab", (0, 5.6))


def msk12c02_reversible() -> Footprint:
    pads_f = [Pad("1", "smd", "roundrect", -2.25, -1.95, 0.6, 1.3, F_SMD, rratio=0.25),
              Pad("2", "smd", "roundrect", 0.75, -1.95, 0.6, 1.3, F_SMD, rratio=0.25),
              Pad("3", "smd", "roundrect", 2.25, -1.95, 0.6, 1.3, F_SMD, rratio=0.25),
              Pad("", "smd", "roundrect", -3.675, -1.1, 1.05, 0.7, F_SMD, rratio=0.25),
              Pad("", "smd", "roundrect", -3.675, 1.1, 1.05, 0.7, F_SMD, rratio=0.25),
              Pad("", "smd", "roundrect", 3.675, -1.1, 1.05, 0.7, F_SMD, rratio=0.25),
              Pad("", "smd", "roundrect", 3.675, 1.1, 1.05, 0.7, F_SMD, rratio=0.25)]
    pads = both_faces(pads_f, mirror=True)
    pads += [Pad("", "np_thru_hole", "circle", -1.5, 0, 0.85, 0.85, ("*.Mask",), 0.85),
             Pad("", "np_thru_hole", "circle", 1.5, 0, 0.85, 0.85, ("*.Mask",), 0.85)]
    gfx_f = rect_lines(0, 0, 7.0, 3.0, "F.Fab", 0.1) + rect_lines(0, 0.6, 8.4, 5.4, "F.CrtYd", 0.05)
    gfx_f += [Line(-1.0, 1.5, -1.0, 2.9, "F.Fab"), Line(1.0, 1.5, 1.0, 2.9, "F.Fab"), Line(-1.0, 2.9, 1.0, 2.9, "F.Fab"),
              Text("ON", -3.0, 3.4, "F.SilkS", 0.6)]
    gfx = both_face_graphics(gfx_f, mirror=True)
    return Footprint("SW_SPDT_MSK12C02_reversible", "MSK-12C02 SPDT slide switch, actuator towards +y, pad sets on both faces",
                     "smd", pads, gfx, "F.Fab", (0, -3.2))


def evqp7a_reversible() -> Footprint:
    pads_f = [Pad("1", "smd", "roundrect", -1.8, -0.72, 1.4, 1.05, F_SMD, rratio=0.24),
              Pad("1", "smd", "roundrect", 1.8, -0.72, 1.4, 1.05, F_SMD, rratio=0.24),
              Pad("2", "smd", "roundrect", -1.8, 0.72, 1.4, 1.05, F_SMD, rratio=0.24),
              Pad("2", "smd", "roundrect", 1.8, 0.72, 1.4, 1.05, F_SMD, rratio=0.24)]
    pads = both_faces(pads_f, mirror=False)
    gfx_f = rect_lines(0, 0, 3.5, 2.9, "F.Fab", 0.1) + rect_lines(0, 0, 5.4, 3.5, "F.CrtYd", 0.05) + [Circle(0, 0, 0.6, "F.SilkS")]
    gfx = both_face_graphics(gfx_f, mirror=False)
    return Footprint("SW_SPST_EVQP7A_reversible", "Panasonic EVQ-P7A 3.5x2.9 mm tactile switch, pads on both faces", "smd", pads, gfx, "F.Fab", (0, -2.4))


def test_pad() -> Footprint:
    pads = both_faces([Pad("1", "smd", "circle", 0, 0, 1.5, 1.5, ("F.Cu", "F.Mask"))], mirror=False)
    gfx = [Circle(0, 0, 1.0, "F.CrtYd", 0.05), Circle(0, 0, 1.0, "B.CrtYd", 0.05)]
    return Footprint("TestPad_1.5mm", "1.5 mm round test pad on both faces", "smd", pads, gfx, "F.SilkS", (2.2, 0))


def mounting_hole() -> Footprint:
    pads = [Pad("", "np_thru_hole", "circle", 0, 0, 2.2, 2.2, THT, 2.2)]
    gfx = [Circle(0, 0, 2.2, "F.CrtYd", 0.05), Circle(0, 0, 2.2, "B.CrtYd", 0.05), Circle(0, 0, 1.6, "F.Fab", 0.1)]
    return Footprint("MountingHole_2.2mm", "M2 mounting hole, 2.2 mm, no copper, 4.4 mm keep-out", "through_hole exclude_from_pos_files exclude_from_bom", pads, gfx, "F.Fab", (0, -3.0))


def all_footprints(hole_pin: dict[int, str]) -> dict[str, Footprint]:
    fps = [choc_v1_hotswap_reversible(), sod123_reversible(), nice_nano_tht(hole_pin),
           fpc_fh12_6_bottom(), battery_pads(), jst_ph_sm4_reversible(), msk12c02_reversible(), evqp7a_reversible(),
           test_pad(), mounting_hole()]
    return {f.name: f for f in fps}
