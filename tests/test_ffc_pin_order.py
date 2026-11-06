# SPDX-License-Identifier: MIT
"""Desk verification of the 6-pin FFC between the right PCB (J1) and the sensor PCB (J1).

Both connectors are Hirose FH12-6S-0.5SH bottom-contact parts.  Since r2.2 the keyboard-side
one sits on the KEY side of the right PCB: the cable climbs the gap between the cradle cup and
the PCB notch, folds over the board edge and goes into the mouth from +y, so the lock can be
worked with everything assembled.  The test reads the pads of both connectors straight from the
board files, places both boards in one world frame the way they are mounted in the ball pocket
(docs/08-trackball-module.md sections 2.2 and 3.2) and pairs the pads that a straight, untwisted
cable joins.  The nets on paired pads must match.

World frame: X and Y are the right PCB's board axes (KiCad, +Y towards the user), Z up.

* Right PCB J1 sits on the key side (pads on F.Cu); a front-face footprint is not mirrored, so
  its pad coordinates are the connector's own drawing.  Bottom contact on the top face: the
  cable's contact face points DOWN.
* The sensor board lies on the case floor with the component side (and its J1) facing down, its
  cable edge towards the keys.  Turning the board over about the axis that runs along the cable
  (Y) keeps board y and negates board x.  Bottom contact under a board that is above the cable:
  the cable's contact face points UP there.
* Opposite faces at the two ends is exactly what a **type B** FFC provides (type A has its
  contacts on the same face at both ends and will NOT work here).  A type B cable carries each
  conductor straight through, so pads at the same world X are joined -- and because the
  keyboard-side pad set is no longer mirrored, the pin numbers now run 1 to 1.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RIGHT_PCB = REPO_ROOT / "hardware" / "right-pcb" / "k0d3ball35-right.kicad_pcb"
SENSOR_PCB = REPO_ROOT / "hardware" / "sensor-pcb" / "k0d3ball35-sensor.kicad_pcb"

# Net names differ between the two projects; this is the intended signal pairing.
RIGHT_TO_SENSOR_NET = {
    "VCC": "VCC",
    "GND": "GND",
    "TB_SCLK": "SCLK",
    "TB_SDIO": "SDIO",
    "TB_NCS": "NCS",
    "TB_MOT": "MOT_J",   # MOT_J is the connector side of R3 (1 k) on the sensor board
}
PITCH = 0.5


# -- minimal s-expression reader -------------------------------------------------------------

def _parse(text: str) -> list:
    tokens = re.findall(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()]+', text)
    stack: list[list] = [[]]
    for tok in tokens:
        if tok == "(":
            stack.append([])
        elif tok == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(tok[1:-1] if tok.startswith('"') else tok)
    return stack[0][0]


def _children(node: list, key: str) -> list[list]:
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def _first(node: list, key: str) -> list | None:
    found = _children(node, key)
    return found[0] if found else None


def _rotate(x: float, y: float, deg: float) -> tuple[float, float]:
    # KiCad: positive footprint rotation is counter-clockwise on screen (y axis points down)
    a = math.radians(deg)
    return x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a)


def ffc_connector(pcb: Path, reference: str = "J1") -> dict:
    """Return the FFC footprint's placement and its numbered pads in board coordinates."""
    board = _parse(pcb.read_text())
    for fp in _children(board, "footprint"):
        props = {p[1]: p[2] for p in _children(fp, "property") if len(p) > 2}
        if props.get("Reference") != reference:
            continue
        at = _first(fp, "at")
        fx, fy = float(at[1]), float(at[2])
        rot = float(at[3]) if len(at) > 3 else 0.0
        layer = _first(fp, "layer")[1]
        pads = {}
        for pad in _children(fp, "pad"):
            if not pad[1].isdigit():
                continue
            pat = _first(pad, "at")
            lx, ly = float(pat[1]), float(pat[2])
            dx, dy = _rotate(lx, ly, rot)
            net = _first(pad, "net")
            pads[int(pad[1])] = {
                "x": round(fx + dx, 3),
                "y": round(fy + dy, 3),
                "copper": [l for l in _first(pad, "layers")[1:] if l.endswith(".Cu")],
                "net": net[-1] if net else None,
            }
        mp = [_first(p, "at") for p in _children(fp, "pad") if not p[1].isdigit()]
        mp_y = [fy + _rotate(float(a[1]), float(a[2]), rot)[1] for a in mp]
        return {"name": fp[1], "x": fx, "y": fy, "rot": rot, "layer": layer, "pads": pads,
                "mount_pad_y": mp_y}
    raise AssertionError(f"{reference} not found in {pcb}")


@pytest.fixture(scope="module")
def right() -> dict:
    return ffc_connector(RIGHT_PCB)


@pytest.fixture(scope="module")
def sensor() -> dict:
    return ffc_connector(SENSOR_PCB)


# -- step 1: nets on pads 1..6 ------------------------------------------------------------------

def test_right_j1_pin_order_is_the_spec_order(right):
    assert {p: d["net"] for p, d in right["pads"].items()} == {
        1: "VCC", 2: "GND", 3: "TB_SCLK", 4: "TB_SDIO", 5: "TB_NCS", 6: "TB_MOT"}


def test_sensor_j1_pin_order_is_straight_through(sensor):
    assert {p: d["net"] for p, d in sensor["pads"].items()} == {
        1: "VCC", 2: "GND", 3: "SCLK", 4: "SDIO", 5: "NCS", 6: "MOT_J"}


# -- step 2: faces, pad 1 positions, cable entry sides -----------------------------------------

def test_faces_and_footprints(right, sensor):
    # Right J1: front-face footprint variant, copper on the key side only (r2.2).
    assert right["name"].endswith("FPC_0.5mm_6P_FH12-6S_top")
    assert right["layer"] == "F.Cu" and right["rot"] == 0.0
    assert all(d["copper"] == ["F.Cu"] for d in right["pads"].values())
    # Sensor J1: front-face variant on the component side, rotated 180 degrees.
    assert sensor["name"].endswith("FPC_0.5mm_6P_FH12-6S")
    assert sensor["layer"] == "F.Cu" and sensor["rot"] == 180.0
    assert all(d["copper"] == ["F.Cu"] for d in sensor["pads"].values())


def test_pad_rows_are_straight_and_pin1_sides(right, sensor):
    for conn, step in ((right, PITCH), (sensor, -PITCH)):
        ys = {d["y"] for d in conn["pads"].values()}
        assert len(ys) == 1, "contact row must be parallel to the board x axis"
        xs = [conn["pads"][i]["x"] for i in range(1, 7)]
        steps = {round(b - a, 3) for a, b in zip(xs, xs[1:])}
        assert steps == {step}, f"expected 0.5 mm pitch with step {step}, got {xs}"
    # The keyboard side is a front-face part (pad 1 at -x), the sensor side a flipped one
    # (pad 1 at +x in its own frame); turning the sensor board over makes the two agree.
    assert right["pads"][1]["x"] < right["pads"][6]["x"]
    assert sensor["pads"][1]["x"] > sensor["pads"][6]["x"]


def test_cable_entry_sides_face_each_other(right, sensor):
    """Contacts sit at the rear of an FH12; the metal-fitting pads are towards the cable side.

    Right J1 takes the cable from +y (the notch edge, where it folds over); the sensor connector
    takes it from its board -y (the edge that faces the keys once the board lies in the pocket).
    """
    right_contact_y = right["pads"][1]["y"]
    sensor_contact_y = sensor["pads"][1]["y"]
    assert all(right_contact_y < y for y in right["mount_pad_y"]), "right J1 cable entry must be +y"
    assert all(sensor_contact_y > y for y in sensor["mount_pad_y"]), "sensor J1 cable entry must be -y"


# -- step 3 and 4: model the cable and compare the nets ----------------------------------------

def cable_pairs(right: dict, sensor: dict) -> list[tuple[int, int]]:
    """Pairs (right pin, sensor pin) joined by a straight, untwisted type B FFC.

    World X of a right-board pad is its board x (the right PCB is not turned over).
    The sensor board is turned over about the cable axis, so world X of its pads is the
    negated board x.  Both connector centres sit on the cable axis; a conductor keeps its
    lateral offset from that axis along the whole cable.
    """
    r_off = {p: d["x"] - right["x"] for p, d in right["pads"].items()}
    s_off = {p: -(d["x"] - sensor["x"]) for p, d in sensor["pads"].items()}
    pairs = []
    for rp, rx in r_off.items():
        match = [sp for sp, sx in s_off.items() if abs(sx - rx) < PITCH / 4]
        assert len(match) == 1, f"right pin {rp} at X={rx:+.2f} meets {match} on the sensor side"
        pairs.append((rp, match[0]))
    return sorted(pairs)


def test_type_b_cable_keeps_the_pin_numbers(right, sensor):
    assert cable_pairs(right, sensor) == [(i, i) for i in range(1, 7)]


def test_nets_match_across_the_cable(right, sensor):
    """The load-bearing check: every right-side signal lands on its sensor-side net."""
    got = {right["pads"][rp]["net"]: sensor["pads"][sp]["net"] for rp, sp in cable_pairs(right, sensor)}
    assert got == RIGHT_TO_SENSOR_NET, f"cross-connection is {got}"


def test_power_pins_are_at_opposite_edges(right, sensor):
    """A cable inserted one position off or mirrored must not put VCC on GND or MOT on VCC
    without the series/pull-up resistors in the path; the design relies on VCC and MOT being
    at opposite cable edges on both boards."""
    for conn, vcc, mot in ((right, "VCC", "TB_MOT"), (sensor, "VCC", "MOT_J")):
        nets = [conn["pads"][i]["net"] for i in range(1, 7)]
        assert {nets[0], nets[-1]} == {vcc, mot}
