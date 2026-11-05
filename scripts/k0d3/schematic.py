# SPDX-License-Identifier: MIT
"""KiCad schematic generator for the k0d3ball36 main PCB.

Produces a single-sheet KiCad 8 format schematic (readable by KiCad 9/10) with all
symbols embedded, so the file needs no external symbol library. Connections are made
with local net labels; the net names are the ones from netlist.py, which the PCB
generator uses as well, so schematic parity in DRC holds by construction.
"""
from __future__ import annotations

from dataclasses import dataclass

from .netlist import LIB, HOLE_PIN_LEFT, HOLE_PIN_RIGHT, Component
from .sexpr import num, quote, uid

SCH_VERSION = "20231120"
G = 2.54  # schematic grid


@dataclass
class Pin:
    number: str
    name: str
    x: float       # connection point in symbol coordinates (y up)
    y: float
    angle: int     # 0 = pin points right (body on the right), 180 = pin points left


@dataclass
class Symbol:
    name: str
    ref_prefix: str
    pins: list[Pin]
    width: float
    height: float
    in_bom: bool = True

    def sexpr(self) -> str:
        out = [f"    (symbol {quote(LIB + ':' + self.name)} (pin_names (offset 0.762)) (exclude_from_sim no) (in_bom {'yes' if self.in_bom else 'no'}) (on_board yes)",
               f"      (property \"Reference\" {quote(self.ref_prefix)} (at 0 {num(self.height / 2 + 1.27)} 0) (effects (font (size 1.27 1.27))))",
               f"      (property \"Value\" {quote(self.name)} (at 0 {num(-self.height / 2 - 1.27)} 0) (effects (font (size 1.27 1.27))))",
               f"      (property \"Footprint\" \"\" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))",
               f"      (property \"Datasheet\" \"\" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))",
               f"      (property \"Description\" \"\" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))",
               f"      (symbol {quote(self.name + '_0_1')}",
               f"        (rectangle (start {num(-self.width / 2)} {num(self.height / 2)}) (end {num(self.width / 2)} {num(-self.height / 2)}) (stroke (width 0.254) (type default)) (fill (type background)))",
               "      )", f"      (symbol {quote(self.name + '_1_1')}"]
        for p in self.pins:
            out.append(f"        (pin passive line (at {num(p.x)} {num(p.y)} {p.angle}) (length 2.54) "
                       f"(name {quote(p.name)} (effects (font (size 1.016 1.016)))) (number {quote(p.number)} (effects (font (size 1.016 1.016)))))")
        out += ["      )", "    )"]
        return "\n".join(out)


def box_symbol(name: str, prefix: str, left: list[tuple[str, str]], right: list[tuple[str, str]], width: float = 10.16) -> Symbol:
    n = max(len(left), len(right), 1)
    height = max(n + 1, 2) * G
    pins = []
    for i, (number, pname) in enumerate(left):
        y = (n - 1) / 2 * G - i * G
        pins.append(Pin(number, pname, -width / 2 - G, y, 0))
    for i, (number, pname) in enumerate(right):
        y = (n - 1) / 2 * G - i * G
        pins.append(Pin(number, pname, width / 2 + G, y, 180))
    return Symbol(name, prefix, pins, width, height)


def symbols() -> dict[str, Symbol]:
    syms = [
        box_symbol("SW_Choc", "SW", [("1", "1")], [("2", "2")], 5.08),
        box_symbol("D_1N4148W", "D", [("2", "A")], [("1", "K")], 5.08),
        box_symbol("nice_nano_v2", "U",
                   [(str(h), f"{h} {HOLE_PIN_RIGHT[h]}/{HOLE_PIN_LEFT[h]}") for h in range(1, 13)],
                   [(str(h), f"{h} {HOLE_PIN_RIGHT[h]}/{HOLE_PIN_LEFT[h]}") for h in range(13, 25)], 30.48),
        box_symbol("SolderJumper_3", "JP", [("1", "1 left hole"), ("2", "2 net"), ("3", "3 right hole")], [], 12.7),
        box_symbol("Conn_FPC_6", "J", [(str(i), f"{i}") for i in range(1, 7)], [], 7.62),
        box_symbol("Conn_Battery", "J", [("1", "B+"), ("2", "B-")], [], 7.62),
        box_symbol("SW_SPDT", "PS", [("1", "1"), ("2", "2 common"), ("3", "3")], [], 7.62),
        box_symbol("SW_Push", "RB", [("1", "1")], [("2", "2")], 5.08),
        box_symbol("TestPoint", "TP", [("1", "1")], [], 5.08),
        Symbol("MountingHole", "H", [], 5.08, 5.08, in_bom=False),
    ]
    return {s.name: s for s in syms}


SYMBOL_FOR_KIND = {"switch": "SW_Choc", "diode": "D_1N4148W", "mcu": "nice_nano_v2", "jumper": "SolderJumper_3", "fpc": "Conn_FPC_6",
                   "battery": "Conn_Battery", "power_switch": "SW_SPDT", "reset": "SW_Push", "testpoint": "TestPoint",
                   "hole": "MountingHole", "cradle_hole": "MountingHole"}


def sym_uuid(ref: str) -> str:
    return uid("sym", ref)


class SchematicWriter:
    def __init__(self, title: str, rev: str, sheet_uuid: str):
        self.title, self.rev, self.sheet_uuid = title, rev, sheet_uuid
        self.syms = symbols()
        self.body: list[str] = []

    # ----- primitives ---------------------------------------------------------------
    def wire(self, x1, y1, x2, y2, owner):
        self.body.append(f"  (wire (pts (xy {num(x1)} {num(y1)}) (xy {num(x2)} {num(y2)})) (stroke (width 0) (type default)) (uuid {quote(uid(owner, 'w', x1, y1, x2, y2))}))")

    def label(self, text, x, y, angle, owner):
        just = "left bottom" if angle == 0 else "right bottom"
        self.body.append(f"  (label {quote(text)} (at {num(x)} {num(y)} {angle}) (effects (font (size 1.27 1.27)) (justify {just})) (uuid {quote(uid(owner, 'lab', text, x, y))}))")

    def no_connect(self, x, y, owner):
        self.body.append(f"  (no_connect (at {num(x)} {num(y)}) (uuid {quote(uid(owner, 'nc', x, y))}))")

    def text(self, text, x, y, size=2.0):
        self.body.append(f"  (text {quote(text)} (exclude_from_sim no) (at {num(x)} {num(y)} 0) (effects (font (size {num(size)} {num(size)})) (justify left bottom)) (uuid {quote(uid('text', text, x, y))}))")

    # ----- symbol placement -----------------------------------------------------------
    def place(self, comp: Component, x: float, y: float, wire_len: float = G) -> None:
        sname = SYMBOL_FOR_KIND[comp.kind]
        sym = self.syms[sname]
        su = sym_uuid(comp.ref)
        lines = [f"  (symbol (lib_id {quote(LIB + ':' + sname)}) (at {num(x)} {num(y)} 0) (unit 1) (exclude_from_sim no) (in_bom {'yes' if sym.in_bom else 'no'}) (on_board yes) (dnp no)",
                 f"    (uuid {quote(su)})",
                 f"    (property \"Reference\" {quote(comp.ref)} (at {num(x)} {num(y - sym.height / 2 - 1.27)} 0) (effects (font (size 1.27 1.27))))",
                 f"    (property \"Value\" {quote(comp.value)} (at {num(x)} {num(y + sym.height / 2 + 1.27)} 0) (effects (font (size 1.27 1.27))))",
                 f"    (property \"Footprint\" {quote(LIB + ':' + comp.footprint)} (at {num(x)} {num(y)} 0) (effects (font (size 1.27 1.27)) hide))",
                 f"    (property \"Datasheet\" \"\" (at {num(x)} {num(y)} 0) (effects (font (size 1.27 1.27)) hide))",
                 f"    (property \"Description\" {quote(comp.description)} (at {num(x)} {num(y)} 0) (effects (font (size 1.27 1.27)) hide))"]
        for p in sym.pins:
            lines.append(f"    (pin {quote(p.number)} (uuid {quote(uid(su, 'pin', p.number))}))")
        lines.append(f"    (instances (project {quote('k0d3ball36')} (path {quote('/' + self.sheet_uuid)} (reference {quote(comp.ref)}) (unit 1))))")
        lines.append("  )")
        self.body.extend(lines)
        # wires + labels for every pin
        for p in sym.pins:
            px, py = x + p.x, y - p.y          # symbol y is up, sheet y is down
            net = comp.pads.get(p.number, "")
            if p.angle == 0:                    # pin on the left, wire goes further left
                ex = px - wire_len
                if net:
                    self.wire(px, py, ex, py, su)
                    self.label(net, ex, py, 180, su)
                else:
                    self.no_connect(px, py, su)
            else:
                ex = px + wire_len
                if net:
                    self.wire(px, py, ex, py, su)
                    self.label(net, ex, py, 0, su)
                else:
                    self.no_connect(px, py, su)

    def place_key_cell(self, sw: Component, d: Component, x: float, y: float) -> None:
        """Switch and diode side by side, wired directly: COL - SW - D(A..K) - ROW."""
        sw_sym, d_sym = self.syms["SW_Choc"], self.syms["D_1N4148W"]
        dx = x + sw_sym.width / 2 + G + G + d_sym.width / 2 + G  # diode centre
        # switch
        self._place_bare(sw, "SW_Choc", x, y)
        self._place_bare(d, "D_1N4148W", dx, y)
        p1 = next(p for p in sw_sym.pins if p.number == "1")
        p2 = next(p for p in sw_sym.pins if p.number == "2")
        pa = next(p for p in d_sym.pins if p.number == "2")
        pk = next(p for p in d_sym.pins if p.number == "1")
        su = sym_uuid(sw.ref)
        # column label on the left
        self.wire(x + p1.x, y - p1.y, x + p1.x - G, y - p1.y, su)
        self.label(sw.pads["1"], x + p1.x - G, y - p1.y, 180, su)
        # switch pin 2 -> diode anode
        self.wire(x + p2.x, y - p2.y, dx + pa.x, y - pa.y, su)
        # diode cathode -> row label
        self.wire(dx + pk.x, y - pk.y, dx + pk.x + G, y - pk.y, su)
        self.label(d.pads["1"], dx + pk.x + G, y - pk.y, 0, su)

    def _place_bare(self, comp: Component, sname: str, x: float, y: float) -> None:
        sym = self.syms[sname]
        su = sym_uuid(comp.ref)
        lines = [f"  (symbol (lib_id {quote(LIB + ':' + sname)}) (at {num(x)} {num(y)} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)",
                 f"    (uuid {quote(su)})",
                 f"    (property \"Reference\" {quote(comp.ref)} (at {num(x)} {num(y - sym.height / 2 - 1.0)} 0) (effects (font (size 1.0 1.0))))",
                 f"    (property \"Value\" {quote(comp.value)} (at {num(x)} {num(y + sym.height / 2 + 1.0)} 0) (effects (font (size 1.0 1.0))))",
                 f"    (property \"Footprint\" {quote(LIB + ':' + comp.footprint)} (at {num(x)} {num(y)} 0) (effects (font (size 1.27 1.27)) hide))",
                 f"    (property \"Datasheet\" \"\" (at {num(x)} {num(y)} 0) (effects (font (size 1.27 1.27)) hide))",
                 f"    (property \"Description\" {quote(comp.description)} (at {num(x)} {num(y)} 0) (effects (font (size 1.27 1.27)) hide))"]
        for p in sym.pins:
            lines.append(f"    (pin {quote(p.number)} (uuid {quote(uid(su, 'pin', p.number))}))")
        lines.append(f"    (instances (project {quote('k0d3ball36')} (path {quote('/' + self.sheet_uuid)} (reference {quote(comp.ref)}) (unit 1))))")
        lines.append("  )")
        self.body.extend(lines)

    # ----- output -----------------------------------------------------------------------
    def render(self) -> str:
        out = [f"(kicad_sch (version {SCH_VERSION}) (generator \"k0d3ball36\") (generator_version \"1.0\")",
               f"  (uuid {quote(self.sheet_uuid)})", "  (paper \"A2\")",
               f"  (title_block (title {quote(self.title)}) (date \"2026-11-05\") (rev {quote(self.rev)}) (company \"k0d3ball36 project\")",
               "    (comment 1 \"Reversible main PCB, right half shown; left half = same board flipped\")",
               "    (comment 2 \"Licensed under CERN-OHL-P-2.0\"))",
               "  (lib_symbols"]
        out += [s.sexpr() for s in self.syms.values()]
        out.append("  )")
        out += self.body
        out.append("  (sheet_instances (path \"/\" (page \"1\")))")
        out.append(")")
        return "\n".join(out) + "\n"


def build_schematic(comps: list[Component], title: str, rev: str) -> str:
    sheet_uuid = uid("sheet", "root")
    w = SchematicWriter(title, rev, sheet_uuid)
    by_ref = {c.ref: c for c in comps}
    # matrix block: columns left to right = matrix col 0..4, rows top to bottom
    x0, y0 = 40.64, 40.64
    col_pitch, row_pitch = 45.72, 20.32
    w.text("Key matrix (COL2ROW: column -> switch -> diode -> row)", x0 - 10, y0 - 12, 2.5)
    for c in comps:
        if c.kind != "switch":
            continue
        d = by_ref[f"D{c.extra['row']}{c.extra['col']}"]
        w.place_key_cell(c, d, x0 + c.extra["col"] * col_pitch, y0 + c.extra["row"] * row_pitch)
    # controller
    w.text("Controller (hole numbers; pin names right half / left half)", x0 - 10, 130, 2.5)
    w.place(by_ref["U1"], x0 + 60, 170, G)
    # jumpers
    w.text("Power-row jumpers: bridge 2-3 on the right half, 1-2 on the left half", x0 + 120, 130, 2.0)
    for i, ref in enumerate(["JP1", "JP2", "JP3"]):
        w.place(by_ref[ref], x0 + 140, 142 + i * 20.32, G)
    # peripherals
    w.text("Power, reset, sensor connector, test pads", x0 + 190, 130, 2.5)
    w.place(by_ref["PS1"], x0 + 210, 145, G)
    w.place(by_ref["J2"], x0 + 210, 165, G)
    w.place(by_ref["J3"], x0 + 210, 182, G)
    w.place(by_ref["RB1"], x0 + 210, 200, G)
    w.place(by_ref["J1"], x0 + 250, 150, G)
    for i, ref in enumerate(["TP1", "TP2", "TP3"]):
        w.place(by_ref[ref], x0 + 250, 180 + i * 12.7, G)
    # holes (no pins)
    holes = [c for c in comps if c.kind in ("hole", "cradle_hole")]
    for i, h in enumerate(holes):
        w.place(h, x0 + 300 + (i % 5) * 15.24, 150 + (i // 5) * 15.24, G)
    return w.render()
