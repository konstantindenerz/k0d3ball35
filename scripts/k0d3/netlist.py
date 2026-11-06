# SPDX-License-Identifier: MIT
"""Electrical description of the k0d3ball35 main PCBs (left and right half).

The same component/net model feeds the schematic generator, the PCB generator and the
tests, so the three can never disagree. Everything follows docs/01-design-spec.md.

Since r2 the two halves are separate, non-reversible PCBs with identical controller pin
use. Controller holes are numbered like the physical Pro Micro footprint seen from the
top with the USB connector up: 1-12 down the left column, 13-24 down the right column.
The only difference between the halves is what hangs on the four sensor pins: the SPI
lines of the trackball sensor on the right, test pads on the left.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .geometry import Layout

LIB = "k0d3ball35"

# Pro Micro / nice!nano pin names per hole (top view, USB up), identical on both halves.
HOLE_PIN = {
    1: "D1", 2: "D0", 3: "GND", 4: "GND", 5: "D2", 6: "D3", 7: "D4", 8: "D5", 9: "D6", 10: "D7", 11: "D8", 12: "D9",
    13: "RAW", 14: "GND", 15: "RST", 16: "VCC", 17: "D21", 18: "D20", 19: "D19", 20: "D18", 21: "D15", 22: "D14", 23: "D16", 24: "D10",
}

# Net connected to each controller hole, shared part (matrix, power, spare pins).
_HOLE_NET_COMMON = {
    1: "TP_D1", 2: "TP_D0",
    3: "GND", 4: "GND", 14: "GND",
    5: "TP_D2", 6: "TP_D3", 12: "TP_D9",
    7: "COL0", 8: "COL1", 9: "COL2", 10: "COL3", 11: "COL4",
    13: "RAW", 15: "RST", 16: "VCC",
    17: "ROW0", 18: "ROW1", 19: "ROW2", 20: "ROW3",
}
# Sensor pins: SPI to the trackball daughterboard on the right, test pads on the left.
_SENSOR_HOLES = {21: "TB_SCLK", 22: "TB_MOT", 23: "TB_SDIO", 24: "TB_NCS"}


def hole_net(half: str) -> dict[int, str]:
    """Controller hole -> net name for one half."""
    nets = dict(_HOLE_NET_COMMON)
    for h, net in _SENSOR_HOLES.items():
        nets[h] = net if half == "right" else f"TP_{HOLE_PIN[h]}"
    return dict(sorted(nets.items()))


def spare_pad_nets(half: str) -> list[str]:
    """Test pad nets in placement order (TP1..TPn)."""
    nets = ["TP_D0", "TP_D1", "TP_D2", "TP_D3", "TP_D9"]
    if half == "left":
        nets += [f"TP_{HOLE_PIN[h]}" for h in sorted(_SENSOR_HOLES)]   # D15, D14, D16, D10
    return nets


FPC_PINS = {1: "VCC", 2: "GND", 3: "TB_SCLK", 4: "TB_SDIO", 5: "TB_NCS", 6: "TB_MOT"}


@dataclass
class Component:
    ref: str
    value: str
    footprint: str          # footprint name inside the project library
    pads: dict[str, str]    # pad number -> net name ("" = unconnected)
    kind: str               # switch | diode | mcu | fpc | battery | power_switch | reset | testpoint | hole
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    description: str = ""
    extra: dict = field(default_factory=dict)


def build_components(layout: Layout) -> list[Component]:
    """Components of one half in board coordinates (top view, before the page offset).

    Positions are layout-frame values passed through `layout.to_board`; on the left half this
    mirrors x. Footprints themselves are never mirrored (the parts are chiral and the nets hang
    on the pads), only their rotation flips sign: an x mirror maps a direction angle a to -a for
    y-directed parts and to 180 - a for x-directed ones, and for the 0/90/270 degree parts of
    this design both rules agree with `-rotation`.
    """
    cfg = layout.cfg
    half = layout.half
    sx = layout.board_sx
    B = layout.to_board

    def place(x: float, y: float, rotation: float) -> tuple[float, float, float]:
        bx, by = B(x, y)
        return (bx, by, (sx * rotation) % 360)

    comps: list[Component] = []
    for k in layout.keys:
        comps.append(Component(k.ref, "Choc V1", "SW_Choc_V1_HS_reversible",
                               {"1": f"COL{k.col}", "2": k.net}, "switch", *place(k.x, k.y, k.rotation),
                               "Kailh Choc V1 switch, hot-swap socket on the back",
                               {"row": k.row, "col": k.col, "name": k.name}))
        # Diode sits in the free south band of the switch (6 mm below the centre, rotated with
        # the key), cathode (pad 1) towards the row line. Offset in the frame, then mirrored.
        th = math.radians(k.rotation)
        dx, dy = round(k.x + 6.0 * math.sin(th), 3), round(k.y + 6.0 * math.cos(th), 3)
        comps.append(Component(k.diode_ref, "1N4148W", "D_SOD-123_reversible",
                               {"1": f"ROW{k.row}", "2": k.net}, "diode", *place(dx, dy, k.rotation),
                               "1N4148W SOD-123, pads on both sides", {"row": k.row, "col": k.col}))
    c = cfg["controller"]
    nets = hole_net(half)
    comps.append(Component("U1", "nice!nano v2", "nice_nano_v2_THT",
                           {str(h): nets[h] for h in nets}, "mcu",
                           *place(c["center"]["x"], c["center"]["y"], c["rotation"]),
                           "nice!nano v2 / SuperMini nRF52840 on 1.27 mm sockets, component side up, USB at the top"))
    f = cfg.get("fpc")
    if f:
        comps.append(Component("J1", "FH12-6S-0.5SH", "FPC_0.5mm_6P_FH12-6S_bottom",
                               {str(p): n for p, n in FPC_PINS.items()}, "fpc",
                               *place(f["center"]["x"], f["center"]["y"], f["rotation"]),
                               "Sensor daughterboard, 6-pin 0.5 mm FPC, bottom side"))
    b = cfg["battery_pads"]
    comps.append(Component("J2", "BAT", "BatteryPads_2x1.8mm_P2.0mm",
                           {"1": "BAT+", "2": "GND"}, "battery", *place(b["center"]["x"], b["center"]["y"], b["rotation"]),
                           "Battery solder pads, B+ / B-"))
    bj = cfg["battery_jst"]
    comps.append(Component("J3", "S2B-PH-SM4-TB", "JST_PH_S2B-PH-SM4-TB_reversible",
                           {"1": "BAT+", "2": "GND"}, "battery", *place(bj["center"]["x"], bj["center"]["y"], bj["rotation"]),
                           "Optional JST-PH 2.0 battery connector, bottom side"))
    ps = cfg["power_switch"]
    comps.append(Component("PS1", "MSK12C02", "SW_SPDT_MSK12C02_reversible",
                           {"1": "RAW", "2": "BAT+", "3": ""}, "power_switch",
                           *place(ps["center"]["x"], ps["center"]["y"], ps["rotation"]),
                           "Power slide switch in the battery positive line, bottom side"))
    rb = cfg["reset_button"]
    comps.append(Component("RB1", "EVQ-P7A01P", "SW_SPST_EVQP7A_reversible",
                           {"1": "RST", "2": "GND"}, "reset",
                           *place(rb["center"]["x"], rb["center"]["y"], rb["rotation"]),
                           "Reset button, bottom side"))
    tp = cfg["test_pads"]
    along_x = tp.get("direction", "y") == "x"
    for i, net in enumerate(spare_pad_nets(half)):
        comps.append(Component(f"TP{i + 1}", net, "TestPad_1.5mm", {"1": net}, "testpoint",
                               *place(tp["start"]["x"] + (i * tp["pitch"] if along_x else 0),
                                      tp["start"]["y"] + (0 if along_x else i * tp["pitch"]), 0),
                               f"Spare controller pin {net[3:]}"))
    for i, h in enumerate(cfg["mounting_holes"]):
        comps.append(Component(f"H{i + 1}", "M2", "MountingHole_2.2mm", {}, "hole", *place(h["x"], h["y"], 0), "Case mounting hole M2"))
    return comps


def net_names(comps: list[Component]) -> list[str]:
    nets: set[str] = set()
    for c in comps:
        nets.update(n for n in c.pads.values() if n)
    order = ["GND", "VCC", "RAW", "BAT+", "RST"]
    rest = sorted(n for n in nets if n not in order)
    return [n for n in order if n in nets] + rest


def net_classes() -> dict[str, dict]:
    return {
        "Default": {"clearance": 0.2, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3},
        "Power": {"clearance": 0.2, "track_width": 0.4, "via_diameter": 0.6, "via_drill": 0.3,
                  "nets": ["RAW", "BAT+"]},   # GND is pour-fed, stays in Default
        # thin tracks for the 0.5 mm pitch FPC connector (0.3 mm pads, 0.2 mm gaps)
        "FPC": {"clearance": 0.2, "track_width": 0.15, "via_diameter": 0.6, "via_drill": 0.3,
                "nets": ["TB_SCLK", "TB_SDIO", "TB_NCS", "TB_MOT", "VCC"]},
    }
