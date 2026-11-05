#!/usr/bin/env python3
"""Generate the k0d3ball36 PMW3610 sensor daughterboard (schematic, PCB, libraries).

Run with the Python interpreter bundled with KiCad 10 (it provides the pcbnew module):

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \
        hardware/sensor-pcb/generate.py all

Subcommands
    sym     write hardware/lib/k0d3ball36.kicad_sym (shared symbol library)
    fp      write the PMW3610DM-SUDU footprint into hardware/lib/k0d3ball36.pretty
    sch     write the schematic (.kicad_sch), project (.kicad_pro) and lib tables
    pcb     place footprints and nets into a fresh .kicad_pcb (unrouted)
    route   export Specctra DSN, run freerouting, import the session back
    finish  add copper pours, silkscreen text, refill zones
    all     everything above in order

The schematic is the source of truth for connectivity.  The PCB netlist is derived from the
same NETS table below, and `kicad-cli pcb drc --schematic-parity` is used to prove both agree.
"""
import os
import subprocess
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
LIB = os.path.join(REPO, "hardware", "lib")
PRETTY = os.path.join(LIB, "k0d3ball36.pretty")
PROJECT = "k0d3ball36-sensor"
SCH = os.path.join(HERE, PROJECT + ".kicad_sch")
PCB = os.path.join(HERE, PROJECT + ".kicad_pcb")
PRO = os.path.join(HERE, PROJECT + ".kicad_pro")
KICAD_CLI = os.environ.get(
    "KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
FREEROUTING = os.environ.get("FREEROUTING_JAR", "")
JAVA = os.environ.get("JAVA", "/opt/homebrew/opt/openjdk/bin/java")

REV = "r1"
TITLE = "k0d3ball36 trackball sensor board (PMW3610)"


def uid():
    return str(uuid.uuid4())


# --------------------------------------------------------------------------------------
# Design tables
# --------------------------------------------------------------------------------------

# Sensor-board FPC pin order.  The main PCB uses 1 VCC, 2 GND, 3 SCLK, 4 SDIO, 5 NCS, 6 MOT.
# Both connectors are bottom-contact types mounted on the component side of their boards and
# are joined by a same-side-contact (type A) cable, which mirrors the order: see docs/08.
FPC_PINS = {1: "MOT_J", 2: "NCS", 3: "SDIO", 4: "SCLK", 5: "GND", 6: "VCC", "MP": "GND"}

# Reference, symbol, value, footprint, {pin: net}
PARTS = [
    ("U1", "PMW3610DM-SUDU", "PMW3610DM-SUDU", "PMW3610DM-SUDU", {
        "1": "VCSEL_P", "2": "SDIO", "3": "SCLK", "4": None, "5": "NCS", "6": "VCC",
        "7": "NRESET", "8": "MOT", "9": "VCP", "10": "VCSEL_P", "11": "GND", "12": "CP",
        "13": "CN", "14": "+1V8", "15": "VCSEL_N", "16": "VCSEL_N"}),
    ("U2", "XC6206P182MR", "XC6206P182MR", "SOT-23", {"1": "GND", "2": "+1V8", "3": "VCC"}),
    ("J1", "FPC_6P", "FPC 6P 0.5mm", "FPC_0.5mm_6P_FH12-6S",
     {str(k): v for k, v in FPC_PINS.items()}),
    ("C1", "C", "1u", "C_0603", {"1": "VCC", "2": "GND"}),
    ("C2", "C", "1u", "C_0603", {"1": "+1V8", "2": "GND"}),
    ("C3", "C", "3.3u X7R", "C_0603", {"1": "+1V8", "2": "GND"}),
    ("C4", "C", "100n", "C_0603", {"1": "+1V8", "2": "GND"}),
    ("C5", "C", "100n", "C_0603", {"1": "VCC", "2": "GND"}),
    ("C6", "C", "100n X7R", "C_0603", {"1": "CP", "2": "CN"}),
    ("C7", "C", "10n X7R", "C_0603", {"1": "VCSEL_P", "2": "GND"}),
    ("C8", "C", "10u X7R", "C_0603", {"1": "VCP", "2": "GND"}),
    ("C9", "C", "10n X7R", "C_0603", {"1": "VCP", "2": "GND"}),
    ("R1", "R", "10k", "R_0603", {"1": "VCC", "2": "NRESET"}),
    ("R2", "R", "10k", "R_0603", {"1": "VCC", "2": "NCS"}),
    ("R3", "R", "1k", "R_0603", {"1": "MOT", "2": "MOT_J"}),
    ("TP1", "TestPoint", "VCC", "TestPoint_D1.0mm", {"1": "VCC"}),
    ("TP2", "TestPoint", "1V8", "TestPoint_D1.0mm", {"1": "+1V8"}),
    ("TP3", "TestPoint", "SCLK", "TestPoint_D1.0mm", {"1": "SCLK"}),
    ("TP4", "TestPoint", "SDIO", "TestPoint_D1.0mm", {"1": "SDIO"}),
    ("TP5", "TestPoint", "NCS", "TestPoint_D1.0mm", {"1": "NCS"}),
    ("TP6", "TestPoint", "MOT", "TestPoint_D1.0mm", {"1": "MOT_J"}),
    ("TP7", "TestPoint", "NRESET", "TestPoint_D1.0mm", {"1": "NRESET"}),
    ("H1", "MountingHole", "M2", "MountingHole_M2", {}),
    ("H2", "MountingHole", "M2", "MountingHole_M2", {}),
]

LCSC = {
    "U1": "C42442560", "U2": "C5446", "J1": "C2764370",
    "C1": "C15849", "C2": "C15849", "C3": "C1678", "C4": "C14663", "C5": "C14663",
    "C6": "C14663", "C7": "C57112", "C8": "C19702", "C9": "C57112",
    "R1": "C25804", "R2": "C25804", "R3": "C21190",
}
DESCRIPTIONS = {
    "U1": "PixArt low power laser mouse sensor, 16-pin molded DIP, LM18-LSI lens",
    "U2": "Torex 1.8 V 200 mA LDO, SOT-23",
    "J1": "0.5 mm 6-pos FPC connector, bottom contact, FH12-6S-0.5SH or clone",
    "C1": "1 uF 0603 X5R 10 V, LDO input", "C2": "1 uF 0603 X5R 10 V, 1.8 V rail",
    "C3": "3.3 uF 0603 X7R 16 V, 1.8 V rail bulk", "C4": "100 nF 0603 X7R, VDD decoupling",
    "C5": "100 nF 0603 X7R, VDDIO decoupling", "C6": "100 nF 0603 X7R 16 V, charge pump",
    "C7": "10 nF 0603 X7R 16 V, VCSEL supply", "C8": "10 uF 0603 X7R 16 V, VCP",
    "C9": "10 nF 0603 X7R 16 V, VCP", "R1": "10 k 0603, NRESET pull-up",
    "R2": "10 k 0603, NCS pull-up", "R3": "1 k 0603, MOTION series protection",
}

# Optical centre of the sensor in board coordinates (mm).  Holes sit on the vertical centre
# line 20 mm apart, so the cradle can be symmetric around the ball axis.
OX, OY = 110.0, 110.0
BOARD_W, BOARD_H = 26.0, 25.0
X0, Y0 = OX - BOARD_W / 2, OY - BOARD_H / 2   # top-left corner
X1, Y1 = X0 + BOARD_W, Y0 + BOARD_H

# ref: (x, y, rotation_deg, layer)  -- "B" puts the part on the ball side
PLACEMENT = {
    # U1 is on the ball side; with rotation 180 before the flip its serial pins (2,3,5,8) end up on
    # the bottom row (test point side) and the power pins (9..14) on the top row.
    "U1": (OX, OY, 180, "B"),
    "H1": (OX, OY - 10.0, 0, "F"),
    "H2": (OX, OY + 10.0, 0, "F"),
    "J1": (117.6, 102.45, 180, "F"),
    # top-left: VCP, charge pump and VDD decoupling next to pins 9/12/13/14
    "C9": (98.6, 99.3, 90, "F"),
    "C3": (100.4, 99.3, 90, "F"),
    "C8": (99.1, 102.6, 180, "F"),
    "C6": (102.6, 102.6, 0, "F"),
    "C4": (105.9, 102.6, 180, "F"),
    "TP2": (111.95, 103.0, 0, "F"),
    # bottom-left: pull-ups and VDDIO cap next to pins 5/6/7, regulator with its caps below
    "R2": (99.1, 117.5, 0, "F"),
    "R1": (102.3, 117.5, 0, "F"),
    "C5": (105.5, 117.5, 0, "F"),
    "C1": (98.6, 119.5, 0, "F"),
    "U2": (102.2, 120.2, 0, "F"),
    "C2": (106.2, 119.4, 0, "F"),
    "TP1": (99.1, 121.4, 0, "F"),
    "TP5": (105.3, 121.4, 0, "F"),
    # bottom-right: VCSEL cap next to pin 1, serial test points
    "C7": (113.4, 117.6, 0, "F"),
    "TP7": (113.2, 121.4, 0, "F"),
    "TP4": (115.7, 121.4, 0, "F"),
    "TP3": (118.2, 121.4, 0, "F"),
    "TP6": (120.7, 121.4, 0, "F"),
    # right channel: MOTION series resistor next to the connector
    "R3": (121.3, 108.0, 90, "F"),
}


# --------------------------------------------------------------------------------------
# Symbol library (shared file hardware/lib/k0d3ball36.kicad_sym)
# --------------------------------------------------------------------------------------

F = '(effects (font (size 1.27 1.27)))'
FH = '(effects (font (size 1.27 1.27)) (hide yes))'


def prop(name, value, x, y, hide=False, justify=None):
    j = f" (justify {justify})" if justify else ""
    h = " (hide yes)" if hide else ""
    return f'(property "{name}" "{value}" (at {x} {y} 0) (effects (font (size 1.27 1.27)){j}{h}))'


def pin(etype, x, y, angle, length, name, number, hide=False):
    h = " (hide yes)" if hide else ""
    return (f'(pin {etype} line (at {x} {y} {angle}) (length {length}){h} '
            f'(name "{name}" {F}) (number "{number}" {F}))')


def rect(x0, y0, x1, y1):
    return (f'(rectangle (start {x0} {y0}) (end {x1} {y1}) '
            f'(stroke (width 0.254) (type default)) (fill (type background)))')


def poly(pts, width=0.254, fill="none"):
    p = " ".join(f"(xy {x} {y})" for x, y in pts)
    return f'(polyline (pts {p}) (stroke (width {width}) (type default)) (fill (type {fill})))'


def circle(x, y, r):
    return f'(circle (center {x} {y}) (radius {r}) (stroke (width 0.254) (type default)) (fill (type none)))'


# Each symbol: (name, reference prefix, footprint hint, is_power, graphics, pins, pin_defs)
# pin_defs: list of (etype, x, y, angle, length, name, number)
def symbol_defs():
    S = {}
    # PMW3610: left = serial side, right = power side, GND bottom
    s_pins = [
        ("bidirectional", -17.78, 12.7, 0, 5.08, "SDIO", "2"),
        ("input", -17.78, 10.16, 0, 5.08, "SCLK", "3"),
        ("input", -17.78, 7.62, 0, 5.08, "NCS", "5"),
        ("input", -17.78, 5.08, 0, 5.08, "NRESET", "7"),
        ("output", -17.78, 2.54, 0, 5.08, "MOTION", "8"),
        ("no_connect", -17.78, -7.62, 0, 5.08, "NC", "4"),
        ("power_in", 17.78, 12.7, 180, 5.08, "VDDIO", "6"),
        ("power_in", 17.78, 10.16, 180, 5.08, "VDD", "14"),
        ("passive", 17.78, 5.08, 180, 5.08, "VCP", "9"),
        ("passive", 17.78, 2.54, 180, 5.08, "CP", "12"),
        ("passive", 17.78, 0, 180, 5.08, "CN", "13"),
        ("passive", 17.78, -5.08, 180, 5.08, "+VCSEL", "1"),
        ("passive", 17.78, -7.62, 180, 5.08, "PASS_T", "10"),
        ("passive", 17.78, -12.7, 180, 5.08, "XYLASER", "15"),
        ("passive", 17.78, -15.24, 180, 5.08, "-VCSEL", "16"),
        ("power_in", 0, -22.86, 90, 5.08, "GND", "11"),
    ]
    S["PMW3610DM-SUDU"] = dict(ref="U", power=False, gfx=[rect(-12.7, 17.78, 12.7, -17.78)],
                               pins=s_pins, value="PMW3610DM-SUDU",
                               fp="k0d3ball36:PMW3610DM-SUDU",
                               desc="PixArt PMW3610 low power laser mouse sensor",
                               ds="https://www.pixart.com/products-detail/21/PMW3610DM-SUDU")
    S["XC6206P182MR"] = dict(ref="U", power=False, gfx=[rect(-5.08, 3.81, 5.08, -3.81)],
                             pins=[("power_in", -7.62, 1.27, 0, 2.54, "VIN", "3"),
                                   ("power_out", 7.62, 1.27, 180, 2.54, "VOUT", "2"),
                                   ("power_in", 0, -6.35, 90, 2.54, "GND", "1")],
                             value="XC6206P182MR", fp="k0d3ball36:SOT-23",
                             desc="1.8 V 200 mA LDO regulator, SOT-23",
                             ds="https://www.torexsemi.com/file/xc6206/XC6206.pdf")
    S["FPC_6P"] = dict(ref="J", power=False, gfx=[rect(-2.54, 8.89, 2.54, -8.89)],
                       pins=[("passive", -7.62, 6.35 - 2.54 * i, 0, 5.08, f"Pin_{i+1}", str(i + 1))
                             for i in range(6)] +
                            [("passive", 0, -11.43, 90, 2.54, "MP", "MP")],
                       value="FPC_6P", fp="k0d3ball36:FPC_0.5mm_6P_FH12-6S",
                       desc="6 position 0.5 mm FPC/FFC connector with mounting pads", ds="")
    S["C"] = dict(ref="C", power=False,
                  gfx=[poly([(-2.032, 0.762), (2.032, 0.762)], 0.508),
                       poly([(-2.032, -0.762), (2.032, -0.762)], 0.508)],
                  pins=[("passive", 0, 2.54, 270, 1.778, "~", "1"),
                        ("passive", 0, -2.54, 90, 1.778, "~", "2")],
                  value="C", fp="k0d3ball36:C_0603", desc="Capacitor", ds="", hide_numbers=True)
    S["R"] = dict(ref="R", power=False, gfx=[rect(-1.016, 2.54, 1.016, -2.54)],
                  pins=[("passive", 0, 3.81, 270, 1.27, "~", "1"),
                        ("passive", 0, -3.81, 90, 1.27, "~", "2")],
                  value="R", fp="k0d3ball36:R_0603", desc="Resistor", ds="", hide_numbers=True)
    S["TestPoint"] = dict(ref="TP", power=False, gfx=[circle(0, 0, 0.762)],
                          pins=[("passive", 0, -2.54, 90, 1.778, "1", "1")],
                          value="TestPoint", fp="k0d3ball36:TestPoint_D1.0mm",
                          desc="Test point", ds="", hide_numbers=True, in_bom=False)
    S["MountingHole"] = dict(ref="H", power=False, gfx=[circle(0, 0, 1.27)], pins=[],
                             value="MountingHole", fp="k0d3ball36:MountingHole_M2",
                             desc="Mounting hole", ds="", in_bom=False)
    for name, up in (("GND", False), ("VCC", True), ("+1V8", True)):
        if up:
            gfx = [poly([(0, 0), (0, 1.27)]), poly([(-0.762, 1.27), (0.762, 1.27)])]
            p = ("power_in", 0, 0, 90, 0, name, "1")
        else:
            gfx = [poly([(0, 0), (0, -1.27)]), poly([(-1.27, -1.27), (1.27, -1.27)]),
                   poly([(-0.635, -1.905), (0.635, -1.905)])]
            p = ("power_in", 0, 0, 270, 0, name, "1")
        S[name] = dict(ref="#PWR", power=True, gfx=gfx, pins=[p], value=name, fp="",
                       desc="Power symbol", ds="", in_bom=False)
    S["PWR_FLAG"] = dict(ref="#FLG", power=True,
                         gfx=[poly([(0, 0), (0, 1.27), (-1.016, 1.905), (0, 2.54), (1.016, 1.905),
                                    (0, 1.27)])],
                         pins=[("power_out", 0, 0, 90, 0, "pwr", "1")], value="PWR_FLAG", fp="",
                         desc="Power flag", ds="", in_bom=False)
    return S


def symbol_sexpr(name, d, libname="k0d3ball36"):
    full = f"{libname}:{name}" if libname else name
    out = [f'(symbol "{full}"']
    if d.get("power"):
        out.append("(power)")
    if d.get("hide_numbers"):
        out.append("(pin_numbers (hide yes))")
    out.append("(pin_names (offset 1.016))")
    out.append("(exclude_from_sim no)")
    out.append(f'(in_bom {"no" if d.get("in_bom") is False else "yes"})')
    out.append("(on_board yes)")
    hide_ref = d.get("power")
    out.append(prop("Reference", d["ref"], 0, 2.54 if not d.get("power") else 0, hide=hide_ref))
    out.append(prop("Value", d["value"], 0, -2.54 if not d.get("power") else 3.81))
    out.append(prop("Footprint", d["fp"], 0, 0, hide=True))
    out.append(prop("Datasheet", d["ds"], 0, 0, hide=True))
    out.append(prop("Description", d["desc"], 0, 0, hide=True))
    out.append(f'(symbol "{name}_0_1" ' + " ".join(d["gfx"]) + ")")
    pins = " ".join(pin(*p, hide=(d.get("power") or False)) for p in d["pins"])
    out.append(f'(symbol "{name}_1_1" {pins})')
    out.append("(embedded_fonts no)")
    out.append(")")
    return "\n  ".join(out)


def write_symbol_lib():
    S = symbol_defs()
    body = "\n".join(symbol_sexpr(n, d, libname=None) for n, d in S.items())
    txt = ('(kicad_symbol_lib (version 20241209) (generator "k0d3ball36_generate") '
           '(generator_version "1.0")\n' + body + "\n)\n")
    os.makedirs(LIB, exist_ok=True)
    with open(os.path.join(LIB, "k0d3ball36.kicad_sym"), "w") as f:
        f.write(txt)
    print("wrote", os.path.join(LIB, "k0d3ball36.kicad_sym"))


# --------------------------------------------------------------------------------------
# PMW3610 footprint.  Origin = optical centre.  Pin 1 top right, pins counter-clockwise.
# Dimensions from the PMW3610DM-SUDU datasheet figure 5 (pin pitch 1.78, rows 10.70 apart,
# optical centre 3.18 left of pin 1 and centred between the rows, cutout 16.96 x 8.60).
# --------------------------------------------------------------------------------------

def write_pmw3610_footprint():
    pitch, rows = 1.78, 10.70
    p1x, p1y = 3.18, -rows / 2
    pads = []
    for i in range(8):
        x = p1x - pitch * i
        shape = "rect" if i == 0 else "oval"
        pads.append(f'(pad "{i+1}" thru_hole {shape} (at {x:.3f} {p1y:.3f}) (size 1.3 1.3) '
                    f'(drill 0.8) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{uid()}"))')
    for i in range(8):
        x = p1x - pitch * 7 - 0.89 + pitch * i
        pads.append(f'(pad "{9+i}" thru_hole oval (at {x:.3f} {-p1y:.3f}) (size 1.3 1.3) '
                    f'(drill 0.8) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{uid()}"))')
    # PCB cutout for the package body (relative to pin 1: x -14.18 .. +2.78, y 1.05 .. 9.65)
    cx0, cx1 = p1x - 14.18, p1x + 2.78
    cy0, cy1 = p1y + 1.05, p1y + 9.65
    body_x0, body_x1 = p1x - 7 * pitch - 0.89 - 1.425, p1x + 1.425
    gfx = [
        f'(fp_rect (start {cx0:.3f} {cy0:.3f}) (end {cx1:.3f} {cy1:.3f}) (stroke (width 0.1) (type solid)) (fill no) (layer "Edge.Cuts") (uuid "{uid()}"))',
        f'(fp_rect (start {body_x0:.3f} -5.05) (end {body_x1:.3f} 5.05) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab") (uuid "{uid()}"))',
        f'(fp_rect (start {body_x0-0.5:.3f} -6.6) (end {body_x1+0.5:.3f} 6.6) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "{uid()}"))',
        # lens envelope, approximate, for the cradle designer (verify against the real lens)
        f'(fp_rect (start {p1x-14.18:.3f} -8.5) (end {p1x+2.78:.3f} 8.5) (stroke (width 0.1) (type dash)) (fill no) (layer "Dwgs.User") (uuid "{uid()}"))',
        f'(fp_circle (center 0 0) (end 0.5 0) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab") (uuid "{uid()}"))',
        f'(fp_line (start -1 0) (end 1 0) (stroke (width 0.1) (type solid)) (layer "F.Fab") (uuid "{uid()}"))',
        f'(fp_line (start 0 -1) (end 0 1) (stroke (width 0.1) (type solid)) (layer "F.Fab") (uuid "{uid()}"))',
        # pin 1 marker on silk, outside the pad
        f'(fp_circle (center {p1x+1.2:.3f} {p1y-1.2:.3f}) (end {p1x+1.5:.3f} {p1y-1.2:.3f}) (stroke (width 0.15) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{uid()}"))',
        f'(fp_line (start {body_x0:.3f} -6.2) (end {body_x1:.3f} -6.2) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))',
        f'(fp_line (start {body_x0:.3f} 6.2) (end {body_x1:.3f} 6.2) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uid()}"))',
        f'(fp_text user "optical centre" (at 0 7.4 0) (layer "F.Fab") (uuid "{uid()}") (effects (font (size 0.6 0.6) (thickness 0.1))))',
    ]
    txt = (f'(footprint "PMW3610DM-SUDU" (version 20241229) (generator "k0d3ball36_generate") '
           f'(generator_version "1.0") (layer "F.Cu")\n'
           f'  (descr "PixArt PMW3610DM-SUDU 16-pin molded lead-frame DIP, origin at optical centre, '
           f'includes body cutout")\n  (tags "PMW3610 sensor trackball")\n  (attr through_hole)\n'
           f'  (property "Reference" "REF**" (at 0 -8.9 0) (layer "F.SilkS") (uuid "{uid()}") '
           f'(effects (font (size 1 1) (thickness 0.15))))\n'
           f'  (property "Value" "PMW3610DM-SUDU" (at 0 8.9 0) (layer "F.Fab") (uuid "{uid()}") '
           f'(effects (font (size 1 1) (thickness 0.15))))\n'
           f'  (property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{uid()}") (effects (font (size 1 1) (thickness 0.15))))\n'
           f'  (property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{uid()}") (effects (font (size 1 1) (thickness 0.15))))\n'
           + "\n".join("  " + g for g in gfx) + "\n" + "\n".join("  " + p for p in pads) +
           "\n  (embedded_fonts no)\n)\n")
    os.makedirs(PRETTY, exist_ok=True)
    with open(os.path.join(PRETTY, "PMW3610DM-SUDU.kicad_mod"), "w") as f:
        f.write(txt)
    print("wrote PMW3610DM-SUDU.kicad_mod")


# --------------------------------------------------------------------------------------
# Schematic
# --------------------------------------------------------------------------------------

def write_project_files():
    pro = """{
  "board": {"design_settings": {
      "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "silk_line_width": 0.12,
        "silk_text_size_h": 0.8, "silk_text_size_v": 0.8, "silk_text_thickness": 0.12,
        "fab_text_size_h": 0.8, "fab_text_size_v": 0.8, "fab_text_thickness": 0.12},
      "rules": {"min_clearance": 0.15, "min_connection": 0.0, "min_copper_edge_clearance": 0.2,
        "min_hole_clearance": 0.25, "min_hole_to_hole": 0.25, "min_microvia_diameter": 0.2,
        "min_microvia_drill": 0.1, "min_resolved_spokes": 2, "min_silk_clearance": 0.0,
        "min_text_height": 0.6, "min_text_thickness": 0.08, "min_through_hole_diameter": 0.3,
        "min_track_width": 0.15, "min_via_annular_width": 0.1, "min_via_diameter": 0.5,
        "solder_mask_to_copper_clearance": 0.0, "solder_mask_min_width": 0.1},
      "track_widths": [0.0, 0.2, 0.3], "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.6, "drill": 0.3}]},
    "layer_presets": [], "viewports": []},
  "boards": [],
  "cvpcb": {"equivalence_files": []},
  "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
  "meta": {"filename": "%s.kicad_pro", "version": 3},
  "net_settings": {"classes": [{"name": "Default", "clearance": 0.2, "track_width": 0.2,
    "via_diameter": 0.6, "via_drill": 0.3, "bus_width": 12, "wire_width": 6,
    "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)"}],
    "meta": {"version": 4}},
  "pcbnew": {"page_layout_descr_file": ""},
  "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
  "sheets": [],
  "text_variables": {}
}
""" % PROJECT
    with open(PRO, "w") as f:
        f.write(pro)
    with open(os.path.join(HERE, "sym-lib-table"), "w") as f:
        f.write('(sym_lib_table\n  (version 7)\n  (lib (name "k0d3ball36")(type "KiCad")'
                '(uri "${KIPRJMOD}/../lib/k0d3ball36.kicad_sym")(options "")(descr "project symbols"))\n)\n')
    with open(os.path.join(HERE, "fp-lib-table"), "w") as f:
        f.write('(fp_lib_table\n  (version 7)\n  (lib (name "k0d3ball36")(type "KiCad")'
                '(uri "${KIPRJMOD}/../lib/k0d3ball36.pretty")(options "")(descr "project footprints"))\n)\n')


# Schematic placement of every part (mm, KiCad sheet coordinates, y down).
SCH_POS = {
    "U1": (152.4, 88.9), "U2": (60.96, 50.8), "J1": (40.64, 101.6),
    "C1": (45.72, 60.96), "C5": (81.28, 60.96), "C2": (91.44, 50.8), "C3": (101.6, 50.8), "C4": (111.76, 50.8),
    "C6": (203.2, 88.9), "C7": (203.2, 109.22), "C8": (203.2, 66.04), "C9": (215.9, 66.04),
    "R1": (106.68, 96.52), "R2": (106.68, 111.76), "R3": (106.68, 127.0),
    "TP1": (45.72, 142.24), "TP2": (55.88, 142.24), "TP3": (66.04, 142.24), "TP4": (76.2, 142.24), "TP5": (86.36, 142.24),
    "TP6": (96.52, 142.24), "TP7": (106.68, 142.24), "H1": (231.14, 142.24), "H2": (241.3, 142.24),
}


def write_schematic():
    S = symbol_defs()
    root = uid()
    out = ['(kicad_sch (version 20250114) (generator "k0d3ball36_generate") (generator_version "9.0")',
           f'  (uuid "{root}")', '  (paper "A3")',
           f'  (title_block (title "{TITLE}") (date "2026-11-05") (rev "{REV}") '
           '(company "k0d3ball36 project") (comment 1 "Licensed under CERN-OHL-P-2.0") '
           '(comment 2 "FPC pin order is mirrored relative to the main PCB; see docs/08-trackball-module.md"))',
           '  (lib_symbols']
    for n, d in S.items():
        out.append("    " + symbol_sexpr(n, d).replace("\n", "\n    "))
    out.append("  )")

    wires, labels, syms, nocon = [], [], [], []
    pwr_count = {"#PWR": 0, "#FLG": 0}

    def place(ref, symname, value, x, y, fields=None):
        d = S[symname]
        lines = [f'  (symbol (lib_id "k0d3ball36:{symname}") (at {x} {y} 0) (unit 1) '
                 f'(exclude_from_sim no) (in_bom {"no" if d.get("in_bom") is False else "yes"}) '
                 f'(on_board yes) (dnp no) (fields_autoplaced yes) (uuid "{uid()}")']
        hide_ref = bool(d.get("power"))
        lines.append("    " + prop("Reference", ref, x + 3, y - 3, hide=hide_ref, justify="left"))
        lines.append("    " + prop("Value", value, x + 3, y, justify="left"))
        lines.append("    " + prop("Footprint", d["fp"], x, y, hide=True))
        lines.append("    " + prop("Datasheet", d["ds"], x, y, hide=True))
        lines.append("    " + prop("Description", d["desc"], x, y, hide=True))
        for k, v in (fields or {}).items():
            lines.append("    " + prop(k, v, x, y, hide=True))
        for p in d["pins"]:
            lines.append(f'    (pin "{p[6]}" (uuid "{uid()}"))')
        lines.append(f'    (instances (project "{PROJECT}" (path "/{root}" (reference "{ref}") (unit 1))))')
        lines.append("  )")
        syms.append("\n".join(lines))

    def pin_world(symname, x, y, number):
        for p in S[symname]["pins"]:
            if p[6] == number:
                px, py, ang = p[1], p[2], p[3]
                # outward direction (away from body) in world coordinates
                dx, dy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[ang]
                return x + px, y - py, dx, dy
        raise KeyError(number)

    def connect(symname, x, y, number, net):
        wx, wy, dx, dy = pin_world(symname, x, y, number)
        ex, ey = wx + dx * 2.54, wy + dy * 2.54
        wires.append(f'  (wire (pts (xy {wx:.2f} {wy:.2f}) (xy {ex:.2f} {ey:.2f})) '
                     f'(stroke (width 0) (type default)) (uuid "{uid()}"))')
        if net in ("GND", "VCC", "+1V8"):
            pwr_count["#PWR"] += 1
            # power symbol pin sits at the wire end; GND hangs down, rails point up
            place(f'#PWR0{pwr_count["#PWR"]:02d}', net, net, round(ex, 2), round(ey, 2))
        else:
            rot = 0 if dx >= 0 else 180
            just = "left bottom" if dx >= 0 else "right bottom"
            if dy != 0:
                rot = 90 if dy < 0 else 270
                just = "left bottom"
            labels.append(f'  (global_label "{net}" (shape passive) (at {ex:.2f} {ey:.2f} {rot}) '
                          f'(fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{uid()}")'
                          f' (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {ex:.2f} {ey:.2f} 0) '
                          f'(effects (font (size 1.27 1.27)) (hide yes))))')

    for ref, symname, value, fp, pins in PARTS:
        x, y = SCH_POS[ref]
        fields = {}
        if ref in LCSC:
            fields["LCSC"] = LCSC[ref]
        if ref in DESCRIPTIONS:
            fields["Note"] = DESCRIPTIONS[ref]
        place(ref, symname, value, x, y, fields)
        for number, net in pins.items():
            if net is None:
                wx, wy, _, _ = pin_world(symname, x, y, number)
                nocon.append(f'  (no_connect (at {wx:.2f} {wy:.2f}) (uuid "{uid()}"))')
            else:
                connect(symname, x, y, number, net)

    # PWR_FLAG on VCC (fed by a passive connector pin) and GND
    for i, (net, x, y) in enumerate((("VCC", 30.48, 40.64), ("GND", 40.64, 40.64)), start=1):
        place(f"#FLG0{i}", "PWR_FLAG", "PWR_FLAG", x, y)
        wires.append(f'  (wire (pts (xy {x} {y}) (xy {x} {y+5.08})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
        pwr_count["#PWR"] += 1
        place(f'#PWR0{pwr_count["#PWR"]:02d}', net, net, x, y + 5.08)

    notes = [
        ('  (text "k0d3ball36 trackball sensor board, PMW3610DM-SUDU + LM18-LSI lens.\\n'
         'VDDIO and all logic run at 3.3 V straight from the main PCB (no level shifters).\\n'
         'VDD 1.8 V is generated on board by U2.  MOTION is push-pull; R3 limits current if the\\n'
         'FFC is inserted the wrong way round.  R2 keeps the sensor deselected while the host boots."'
         ' (exclude_from_sim no) (at 30 170 0) (effects (font (size 2 2)) (justify left bottom)) (uuid "%s"))' % uid()),
        ('  (text "FPC pin order on THIS board: 1 MOT, 2 NCS, 3 SDIO, 4 SCLK, 5 GND, 6 VCC.\\n'
         'Main PCB order: 1 VCC, 2 GND, 3 SCLK, 4 SDIO, 5 NCS, 6 MOT.\\n'
         'Both connectors are bottom-contact parts on the component side of their boards and are\\n'
         'joined by a same-side-contact (type A) FFC, which mirrors the pin order end to end."'
         ' (exclude_from_sim no) (at 30 185 0) (effects (font (size 2 2)) (justify left bottom)) (uuid "%s"))' % uid()),
    ]
    out += wires + labels + nocon + syms + notes
    out.append(f'  (sheet_instances (path "/" (page "1")))')
    out.append("  (embedded_fonts no)")
    out.append(")")
    with open(SCH, "w") as f:
        f.write("\n".join(out) + "\n")
    print("wrote", SCH)


# --------------------------------------------------------------------------------------
# PCB (pcbnew API)
# --------------------------------------------------------------------------------------

def mm(v):
    import pcbnew
    return pcbnew.FromMM(v)


def new_board():
    import pcbnew
    board = pcbnew.CreateEmptyBoard()
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.15)
    ds.m_ViasMinSize = mm(0.5)
    ds.m_MinThroughDrill = mm(0.3)
    ds.m_MinClearance = mm(0.15)
    ds.m_CopperEdgeClearance = mm(0.3)
    ds.m_HoleClearance = mm(0.25)
    ds.m_SolderMaskMinWidth = mm(0.1)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetTrackWidth(mm(0.2))
    nc.SetClearance(mm(0.2))
    nc.SetViaDiameter(mm(0.6))
    nc.SetViaDrill(mm(0.3))
    board.SetCopperLayerCount(2)
    # drill/placement origin at the bottom-left board corner (JLCPCB-friendly positive coordinates)
    ds.SetAuxOrigin(pcbnew.VECTOR2I(mm(X0), mm(Y1)))
    ds.SetGridOrigin(pcbnew.VECTOR2I(mm(OX), mm(OY)))
    board.GetTitleBlock().SetTitle(TITLE)
    board.GetTitleBlock().SetRevision(REV)
    board.GetTitleBlock().SetDate("2026-11-05")
    board.GetTitleBlock().SetCompany("k0d3ball36 project")
    return board


def add_outline(board):
    import pcbnew
    r = 2.0
    pts = [(X0 + r, Y0), (X1 - r, Y0), (X1, Y0 + r), (X1, Y1 - r), (X1 - r, Y1), (X0 + r, Y1),
           (X0, Y1 - r), (X0, Y0 + r)]
    # straight segments plus 90 degree arcs for rounded corners
    def seg(a, b):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        board.Add(s)

    def arc(start, mid, end):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetArcGeometry(pcbnew.VECTOR2I(mm(start[0]), mm(start[1])),
                         pcbnew.VECTOR2I(mm(mid[0]), mm(mid[1])),
                         pcbnew.VECTOR2I(mm(end[0]), mm(end[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        board.Add(s)

    k = r * (1 - 0.70710678)
    seg(pts[0], pts[1]); arc(pts[1], (X1 - k, Y0 + k), pts[2])
    seg(pts[2], pts[3]); arc(pts[3], (X1 - k, Y1 - k), pts[4])
    seg(pts[4], pts[5]); arc(pts[5], (X0 + k, Y1 - k), pts[6])
    seg(pts[6], pts[7]); arc(pts[7], (X0 + k, Y0 + k), pts[0])


def add_text(board, text, x, y, layer, size=0.8, rot=0, mirror=False, bold=False):
    import pcbnew
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * 0.15))
    t.SetTextAngleDegrees(rot)
    t.SetMirrored(mirror)
    t.SetBold(bold)
    board.Add(t)
    return t


def set_field(m, name, value):
    import pcbnew
    if m.HasField(name):
        m.GetField(name).SetText(value)
        return
    try:
        m.SetField(name, value)
    except AttributeError:
        fld = pcbnew.PCB_FIELD(m, m.GetNextFieldOrdinal(), name)
        fld.SetText(value)
        fld.SetVisible(False)
        m.AddField(fld)
    if m.HasField(name):
        m.GetField(name).SetVisible(False)


S_PINS = {n: d["pins"] for n, d in symbol_defs().items()}


def build_pcb():
    import pcbnew
    board = new_board()
    add_outline(board)
    nets = {}

    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(board, name)
            board.Add(n)
            nets[name] = n
        return nets[name]

    for ref, symname, value, fp, pins in PARTS:
        m = pcbnew.FootprintLoad(PRETTY, fp)
        if m is None:
            raise SystemExit(f"footprint {fp} not found in {PRETTY}")
        m.SetReference(ref)
        m.SetValue(value)
        m.SetFPIDAsString(f"k0d3ball36:{fp}")
        x, y, rot, layer = PLACEMENT[ref]
        board.Add(m)
        m.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        m.SetOrientationDegrees(rot)
        if layer == "B":
            m.Flip(pcbnew.VECTOR2I(mm(x), mm(y)), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        for pad in m.Pads():
            n = pins.get(pad.GetNumber())
            if n:
                pad.SetNet(net(n))
            elif pad.GetNumber() in pins:   # explicitly unconnected pin, mirror KiCad's naming
                pname = [q[5] for q in S_PINS[symname] if q[6] == pad.GetNumber()][0]
                pad.SetNet(net(f"unconnected-({ref}-{pname}-Pad{pad.GetNumber()})"))
        set_field(m, "Description", symbol_defs()[symname]["desc"])
        set_field(m, "Datasheet", symbol_defs()[symname]["ds"])
        if ref in DESCRIPTIONS:
            set_field(m, "Note", DESCRIPTIONS[ref])
        if layer == "B":
            m.Reference().SetMirrored(True)
            m.Value().SetMirrored(True)
        if ref in LCSC:
            set_field(m, "LCSC", LCSC[ref])
        m.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        m.Reference().SetTextThickness(mm(0.12))
        m.Reference().SetLayer(pcbnew.B_Fab if layer == "B" else pcbnew.F_Fab)
        m.Value().SetVisible(False)
    board.Save(PCB)
    print("wrote", PCB)
    dump_pads(board)
    return board


def dump_pads(board):
    import pcbnew
    for m in board.GetFootprints():
        for p in m.Pads():
            pos = p.GetPosition()
            print(f"{m.GetReference():4s} pad {p.GetNumber():3s} {p.GetNetname():8s} "
                  f"({pcbnew.ToMM(pos.x):7.2f},{pcbnew.ToMM(pos.y):7.2f}) {p.GetLayerName()}")


def route():
    import pcbnew
    board = pcbnew.LoadBoard(PCB)
    dsn = os.path.join(HERE, "build", PROJECT + ".dsn")
    ses = os.path.join(HERE, "build", PROJECT + ".ses")
    os.makedirs(os.path.dirname(dsn), exist_ok=True)
    pcbnew.ExportSpecctraDSN(board, dsn)
    jar = FREEROUTING or os.path.join(HERE, "build", "freerouting.jar")
    cmd = [JAVA, "-jar", jar, "-de", dsn, "-do", ses, "-mp", "200", "-l", "en"]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True, timeout=900)
    ok = pcbnew.ImportSpecctraSES(board, ses)
    print("ses import", ok)
    board.Save(PCB)


# Candidate positions for GND stitching vias (tie the ball-side pour to the component-side pour).
STITCH_VIAS = [(98.4, 98.4), (108.6, 98.6), (111.4, 98.6), (122.2, 99.2), (117.0, 111.0),
               (122.3, 113.5), (108.6, 121.4), (111.4, 121.4), (97.9, 110.0), (122.5, 117.5)]


def _dist_point_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    cx, cy = ax + t * dx, ay + t * dy
    return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5


def add_stitching_vias(board, gnd, via_d=0.6, drill=0.3, clearance=0.25):
    """Drop GND vias at candidate spots that are free of foreign copper (checked geometrically)."""
    import pcbnew
    items = []
    for t in board.GetTracks():
        a, b = t.GetStart(), t.GetEnd()
        w = pcbnew.ToMM(t.GetWidth()) / 2
        items.append((pcbnew.ToMM(a.x), pcbnew.ToMM(a.y), pcbnew.ToMM(b.x), pcbnew.ToMM(b.y), w,
                      t.GetNetname()))
    for m in board.GetFootprints():
        for pad in m.Pads():
            c = pad.GetPosition()
            r = max(pcbnew.ToMM(pad.GetSize().x), pcbnew.ToMM(pad.GetSize().y)) / 2 * 1.42
            items.append((pcbnew.ToMM(c.x), pcbnew.ToMM(c.y), pcbnew.ToMM(c.x), pcbnew.ToMM(c.y), r,
                          pad.GetNetname()))
    placed = 0
    for (x, y) in STITCH_VIAS:
        ok = True
        for (ax, ay, bx, by, w, netname) in items:
            need = via_d / 2 + w + (0.05 if netname == "GND" else clearance)
            if _dist_point_segment(x, y, ax, ay, bx, by) < need:
                ok = False
                break
        if not ok:
            continue
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        v.SetDrill(mm(drill))
        v.SetWidth(mm(via_d))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(gnd)
        board.Add(v)
        placed += 1
    print(f"stitching vias placed: {placed}")


def finish():
    import pcbnew
    board = pcbnew.LoadBoard(PCB)
    # freerouting occasionally emits very short neck-down segments; force the netclass width
    for t in board.GetTracks():
        if t.GetClass() == "PCB_TRACK" and t.GetWidth() < mm(0.2):
            t.SetWidth(mm(0.2))
    gnd = board.FindNet("GND")
    add_stitching_vias(board, gnd)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(gnd)
        z.SetIsFilled(True)
        z.SetMinThickness(mm(0.2))
        z.SetLocalClearance(mm(0.25))
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.3))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetAssignedPriority(0)
        z.SetZoneName(f"GND_{'F' if layer == pcbnew.F_Cu else 'B'}")
        outline = z.Outline()
        outline.NewOutline()
        for (x, y) in ((X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)):
            outline.Append(mm(x), mm(y))
        board.Add(z)
    # silkscreen (component side is cramped, so most text goes on the ball side)
    add_text(board, "6:VCC", 117.5, 106.4, pcbnew.F_SilkS, 0.6)
    add_text(board, "1:MOT", 120.9, 105.3, pcbnew.F_SilkS, 0.6)
    add_text(board, "BALL SIDE", 103.5, 100.4, pcbnew.B_SilkS, 1.2, mirror=True, bold=True)
    add_text(board, "PMW3610 / LM18-LSI", 103.5, 98.6, pcbnew.B_SilkS, 0.7, mirror=True)
    add_text(board, "k0d3ball36 sensor " + REV, 110.0, 117.6, pcbnew.B_SilkS, 0.7, mirror=True)
    add_text(board, "lens + sensor body on this side", 110.0, 121.8, pcbnew.B_SilkS, 0.6, mirror=True)
    for m in board.GetFootprints():
        if m.GetReference() == "U1":
            for item in m.GraphicalItems():
                if isinstance(item, pcbnew.PCB_TEXT) and item.GetLayer() in (pcbnew.B_Fab, pcbnew.B_SilkS):
                    item.SetMirrored(True)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(PCB)
    print("finished", PCB)


def verify():
    """Run ERC and DRC (schematic parity) as hard gates; returns True when both are clean."""
    rpt = os.path.join(HERE, "build")
    os.makedirs(rpt, exist_ok=True)
    erc = subprocess.run([KICAD_CLI, "sch", "erc", "--exit-code-violations", "--severity-error",
                          "--format", "report", "-o", os.path.join(rpt, "erc.rpt"), SCH],
                         capture_output=True, text=True)
    drc = subprocess.run([KICAD_CLI, "pcb", "drc", "--schematic-parity", "--exit-code-violations",
                          "--severity-error", "--format", "report", "-o", os.path.join(rpt, "drc.rpt"), PCB],
                         capture_output=True, text=True)
    print("ERC exit", erc.returncode, "| DRC exit", drc.returncode)
    return erc.returncode == 0 and drc.returncode == 0


def route_until_clean(attempts=4):
    for i in range(attempts):
        build_pcb()
        route()
        finish()
        if verify():
            print(f"clean after attempt {i + 1}")
            return
        print("DRC not clean, re-routing")
    raise SystemExit("could not obtain a DRC-clean route")


def main():
    cmds = sys.argv[1:] or ["all"]
    if "all" in cmds:
        cmds = ["sym", "fp", "sch", "autoroute"]
    for c in cmds:
        {"sym": write_symbol_lib, "fp": write_pmw3610_footprint,
         "sch": lambda: (write_project_files(), write_schematic()),
         "pcb": build_pcb, "route": route, "finish": finish, "verify": verify,
         "autoroute": route_until_clean,
         "dump": lambda: dump_pads(__import__("pcbnew").LoadBoard(PCB))}[c]()


if __name__ == "__main__":
    main()
