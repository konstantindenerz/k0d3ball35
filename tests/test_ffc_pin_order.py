# SPDX-License-Identifier: MIT
"""Desk verification of the 6-pin FFC between the right PCB (J1) and the trackball sensor module.

Since r2.4 the sensor is not a board of ours any more: it is the bought 14 x 8 mm PixArt PAW3222
module (sekigon-gonnoc / nogikes-ya, the one torabo-tsuki LP uses), so its FFC pinout is given by
its vendor and J1 has to follow it. There is no second `.kicad_pcb` left to read the far end from,
so the module side enters this test as the declared constant `MODULE_PINS` below and the pairing is
*derived* from the two mounting faces instead of measured off two pad fields.

What decides the pairing is the cable type, and the cable type follows from the mounting:

* An FH12-style bottom-contact connector only mates with the face of the cable that carries the
  contact window, and that face has to point at the board the connector is soldered to.
* Right PCB J1 sits on the KEY side with the cable lying on top of the board
  (`issues/hw-j1-top-side.md`), so at that end the cable's contact window points DOWN.
* The module is tilted beside the ball with its optics towards the ball and its FPC connector on
  the back face, so the cable runs along the back of the module and its contact window points at
  that back face, i.e. away from the ball and with an upward component
  (`spec/08-trackball-module.md`, `hardware/trackball-cradle/params.scad`).
* Contact windows on opposite faces at the two ends is exactly what a **type B** FFC provides. A
  type A cable (windows on the same face at both ends, the usual default) presents insulation to
  the contacts at one end and connects nothing.

Pin numbering across the cable. For one cable end write `m` for the direction the cable leaves the
mouth and `c` for the normal from the connector's contacts towards the cable. Pin 1 and pin 6 sit
at the two ends of the contact row, and for a given connector family the direction from pin 1 to
pin 6 has a fixed handedness with respect to those two vectors: `p = m x c`. Put the cable in its
own frame, `u` from the keyboard end to the module end and `n` normal to the cable:

| | keyboard end | module end |
|---|---|---|
| cable leaves the mouth along | `m = +u` | `m = -u` |
| its board lies on the | `-n` side | `+n` side (type B: the other face) |
| contacts point at the cable along | `c = +n` | `c = -n` |
| pin 1 -> pin 6 therefore runs along | `p = u x n` | `p = (-u) x (-n) = u x n` |

Both ends number their pins in the SAME lateral direction, and an untwisted cable that is not
folded back on itself keeps every conductor on its own side, so **pin i meets pin i**. With a
type A cable the module end would keep `c = +n`, `p` would flip and the mapping would reverse to
`i + j = 7`. Both signs are checked below, and the type A branch is cross-checked against a
published design: torabo-tsuki LP puts both connectors on the undersides of its two boards, uses a
type A cable, and therefore wires its keyboard side in the exact reverse of this same module's
order (`spec/08-trackball-module.md` section 2.2).

Assumption this rests on, and the reason `issues/hw-ffc-pin-order-verification.md` keeps a bench
step open: `p = m x c` needs the SAME sign at both ends, i.e. the module's connector has to call
the same end of its contact row "1" as the Hirose part does. Two identical footprints made that
free in r2.2; a bought module does not. It is a continuity test on the first physical cable, and
it is cheap. Everything else here is checked against files in this repository.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

from k0d3.netlist import FPC_PINS

REPO_ROOT = Path(__file__).resolve().parents[1]
RIGHT_PCB = REPO_ROOT / "hardware" / "right-pcb" / "k0d3ball35-right.kicad_pcb"

# The bought module's 6-pin 0.5 mm FFC pinout, looking at the module's own connector.
# Source: sekigon-gonnoc / nogikes-ya PAW3222 trackball module as shipped in torabo-tsuki LP. The
# same six signals in the same order are quoted in spec/08-trackball-module.md section 2.2 as the
# module side of that keyboard's cable, which is where the cross-check below gets its second
# data point. Confirm on the physical part before the PCB order: this is the one value in this
# file that nothing in this repository can verify (issues/hw-ffc-pin-order-verification.md).
MODULE_PINS = {1: "3.3V", 2: "CS", 3: "MOTION", 4: "SDIO", 5: "SCLK", 6: "GND"}

# Our net names against the module's signal names. Same six signals, different vocabulary.
NET_TO_MODULE_SIGNAL = {
    "VCC": "3.3V",
    "GND": "GND",
    "TB_SCLK": "SCLK",
    "TB_SDIO": "SDIO",
    "TB_NCS": "CS",
    "TB_MOT": "MOTION",
}

# torabo-tsuki LP's keyboard-side pin order, quoted in spec/08-trackball-module.md section 2.2.
# Same module, but both connectors on board undersides, hence a type A cable and the reversed
# mapping. An independent check that the handedness argument in the docstring has the right sign.
TORABO_TSUKI_KEYBOARD_TYPE_A = {1: "GND", 2: "SCLK", 3: "SDIO", 4: "MOTION", 5: "CS", 6: "3.3V"}

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


# -- step 1: the cable ------------------------------------------------------------------------

def cable_pairs(cable_type: str, pins: int = 6) -> dict[int, int]:
    """{keyboard pin: module pin} joined by a straight, untwisted FFC of the given type.

    Type B puts the two boards on opposite faces of the cable, so both connectors number their
    pins in the same lateral direction and the cable runs straight through. Type A keeps both
    boards on the same face, which flips the far end's numbering direction and reverses the
    mapping. The derivation is in the module docstring.
    """
    if cable_type == "B":
        return {i: i for i in range(1, pins + 1)}
    if cable_type == "A":
        return {i: pins + 1 - i for i in range(1, pins + 1)}
    raise ValueError(f"unknown FFC type {cable_type!r}: this design uses type B")


def test_type_b_is_straight_through_and_type_a_reverses():
    assert cable_pairs("B") == {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}
    assert cable_pairs("A") == {1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
    with pytest.raises(ValueError):
        cable_pairs("D")


def test_torabo_tsuki_confirms_the_type_a_sign():
    """Same module, both connectors under their boards, type A cable: the published keyboard-side
    order must come out of the reversed mapping. If it did not, the handedness argument in the
    docstring would have the wrong sign and our type B conclusion would be reversed too."""
    derived = {kb: MODULE_PINS[mod] for kb, mod in cable_pairs("A").items()}
    assert derived == TORABO_TSUKI_KEYBOARD_TYPE_A, (
        f"type A mapping gives {derived}, torabo-tsuki LP publishes {TORABO_TSUKI_KEYBOARD_TYPE_A}")


# -- step 2: J1 against the module's declared pinout -------------------------------------------

def test_j1_model_carries_the_module_pin_order():
    """The load-bearing check: every J1 signal lands on the module pin that carries it.

    With the type B cable the mapping is pin for pin, so J1's order is the module's own order
    translated into our net names.
    """
    got = {kb: NET_TO_MODULE_SIGNAL[FPC_PINS[kb]] for kb in sorted(FPC_PINS)}
    want = {kb: MODULE_PINS[mod] for kb, mod in cable_pairs("B").items()}
    assert got == want, f"J1 reaches {got}, the module offers {want}"


def test_every_module_signal_is_wired_exactly_once():
    assert sorted(NET_TO_MODULE_SIGNAL.values()) == sorted(MODULE_PINS.values())
    assert sorted(FPC_PINS.values()) == sorted(NET_TO_MODULE_SIGNAL)


def test_right_j1_copper_matches_the_model(right):
    """The generated copper has to carry the nets the model assigns. Fails until `make pcb` (or
    `make route`) has regenerated the right board after a pin reorder."""
    assert {p: d["net"] for p, d in right["pads"].items()} == dict(FPC_PINS), (
        "hardware/right-pcb/k0d3ball35-right.kicad_pcb predates the current FPC_PINS; "
        "re-run `make pcb` / `make route`")


# -- step 3: the premises the derivation rests on, read off the right board ---------------------

def test_right_j1_is_the_unmirrored_key_side_part(right):
    """J1 on the key side (r2.2): a front-face footprint variant, copper on F.Cu only, so its pad
    coordinates are the connector's own drawing and the cable's contact window points down."""
    assert right["name"].endswith("FPC_0.5mm_6P_FH12-6S_top")
    assert right["layer"] == "F.Cu" and right["rot"] == 0.0
    assert all(d["copper"] == ["F.Cu"] for d in right["pads"].values())


def test_right_pad_row_is_straight_at_the_connector_pitch(right):
    ys = {d["y"] for d in right["pads"].values()}
    assert len(ys) == 1, "contact row must be parallel to the board x axis"
    xs = [right["pads"][i]["x"] for i in range(1, 7)]
    steps = {round(b - a, 3) for a, b in zip(xs, xs[1:])}
    assert steps == {PITCH}, f"expected 0.5 mm pitch rising with the pin number, got {xs}"


def test_right_cable_entry_is_towards_the_notch(right):
    """Contacts sit at the rear of an FH12, the metal-fitting pads are towards the cable side.
    J1 takes the cable from +y, the notch edge where it folds over the board (spec/01 section 3)."""
    contact_y = right["pads"][1]["y"]
    assert all(contact_y < y for y in right["mount_pad_y"]), "right J1 cable entry must be +y"


# -- step 4: what the module's fixed order costs us --------------------------------------------

def test_power_pins_sit_at_opposite_cable_edges(right):
    """The module puts 3.3V on pin 1 and GND on pin 6, so our J1 does too, and the two supply
    pins end up at opposite edges of the cable.

    This is worth writing down because it is a regression against r2.3. Then VCC faced MOT across
    the cable and a laterally reversed cable was current-limited by the series resistor on our own
    sensor board; the bought module's pinout is not ours to choose and that resistor went with the
    board. The failure mode a type B cable protects against is the common one (a type A cable, a
    cable swapped end for end or inserted upside down all present insulation and connect nothing),
    but a cable whose contact window is on the wrong face at one end would now short VCC to GND.
    Hence the continuity test before power in issues/hw-ffc-pin-order-verification.md, and the
    palindromic-pinout idea parked in spec/08-trackball-module.md section 6.
    """
    nets = [FPC_PINS[i] for i in range(1, 7)]
    assert {nets[0], nets[-1]} == {"VCC", "GND"}
    assert MODULE_PINS[1] == "3.3V" and MODULE_PINS[6] == "GND"
    # and the copper agrees about which end of the row is pin 1
    assert right["pads"][1]["x"] < right["pads"][6]["x"]
