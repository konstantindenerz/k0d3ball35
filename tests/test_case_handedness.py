# SPDX-License-Identifier: MIT
"""The exported case and cradle files are the real parts, not their mirror images.

The SCAD sources model in the layout frame (x outward, y towards the user, z up), which is
left-handed; the export flips y once (issues/mech-case-stl-mirrored.md). The other tests undo
that flip and compare with the layout. This file does not: it reads the committed STLs as a
slicer does (right-handed, z up) and compares them with the KiCad boards seen from above, the
other source of truth. KiCad's y points down the screen, towards the user, so a board point
(kx, ky) lies at (kx - 120, 60 - ky) in the print frame (KiCad = layout + (120, 60), left board
mirrored in x like the left case). A y-mirrored export puts the controller box, the ball pocket
and the cradle's cable slot on the wrong side and fails here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "hardware" / "case"
CRADLE = ROOT / "hardware" / "trackball-cradle"
OFFSET = (120.0, 60.0)
PCB_T = 1.6

trimesh = pytest.importorskip("trimesh")
np = pytest.importorskip("numpy")


def to_print(kx: float, ky: float) -> tuple[float, float]:
    return kx - OFFSET[0], OFFSET[1] - ky


def board(half: str) -> dict:
    """Footprint positions and the Edge.Cuts outline of a main board, in the print frame."""
    text = (ROOT / "hardware" / f"{half}-pcb" / f"k0d3ball35-{half}.kicad_pcb").read_text()
    refs = {}
    for m in re.finditer(r'\(footprint "[^"]+"(.*?)\(property "Reference" "([^"]+)"', text, flags=re.S):
        at = re.search(r"\(at ([-\d.]+) ([-\d.]+)", m[1])
        refs[m[2]] = to_print(float(at[1]), float(at[2]))
    edge = text.index('(layer "Edge.Cuts")')
    poly = text[text.rindex("(gr_poly", 0, edge):edge]
    outline = [to_print(float(x), float(y)) for x, y in re.findall(r"\(xy ([-\d.]+) ([-\d.]+)\)", poly)]
    return {"refs": refs, "outline": np.array(outline)}


def stack(half: str) -> dict:
    return json.loads((CASE / "stack.json").read_text())["variants"][half]


@pytest.mark.parametrize("half", ["left", "right"])
def test_tray_lies_on_the_board_not_on_its_mirror_image(half):
    b = board(half)
    v = trimesh.load(CASE / "stl" / f"tray-{half}.stl", force="mesh").vertices
    lo, hi = b["outline"].min(axis=0), b["outline"].max(axis=0)
    # the tray encloses the board outline with its wall (a few mm), on both axes
    for axis in (0, 1):
        assert 0 < lo[axis] - v[:, axis].min() < 8, (half, axis, lo[axis], v[:, axis].min())
        assert 0 < v[:, axis].max() - hi[axis] < 8, (half, axis, hi[axis], v[:, axis].max())
    # the controller box (the highest walls) stands over the controller U1
    top = v[v[:, 2] > stack(half)["box_top_z"] - 0.3][:, :2].mean(axis=0)
    u1 = np.array(b["refs"]["U1"])
    assert np.hypot(*(top - u1)) < 10, (half, top, u1)
    assert np.hypot(*(top - u1 * [1, -1])) > 20, "the box would also fit the mirrored board"


def test_ball_pocket_sits_in_the_board_notch():
    b = board("right")
    right = json.loads((ROOT / "hardware/layout/output/points-right.json").read_text())
    tb = right["trackball"]["center"]
    ball = np.array(to_print(tb["x"] + OFFSET[0], tb["y"] + OFFSET[1]))
    # the KiCad outline has its octagonal notch around that point (apothem 15)
    d = np.hypot(*(b["outline"] - ball).T)
    assert 14.9 < d.min() < 16.5, d.min()
    v = trimesh.load(CASE / "stl" / "tray-right.stl", force="mesh").vertices
    above = v[v[:, 2] > -PCB_T + 0.05]
    r = np.hypot(above[:, 0] - ball[0], above[:, 1] - ball[1])
    assert r.min() >= 14.0, "nothing of the tray in the cradle circle"
    assert ((r > 14.0) & (r < 20.0)).sum() > 50, "the pocket wall rings the ball"


def test_cradle_cable_slot_faces_the_keys():
    """J1 and the cable lie on the key side of the ball, so the slot in the housing wall must face
    the switches of the right board: +y in the print frame."""
    b = board("right")
    right = json.loads((ROOT / "hardware/layout/output/points-right.json").read_text())
    ball_y = OFFSET[1] - (right["trackball"]["center"]["y"] + OFFSET[1])
    keys_y = np.mean([p[1] for ref, p in b["refs"].items() if re.fullmatch(r"SW\d+", ref)])
    assert keys_y > ball_y
    s = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]
    v = trimesh.load(CRADLE / "stl" / "cradle-19mm-pocket.stl", force="mesh").vertices
    half_y = s["housing_y"] / 2

    def slot_edges(face_y):
        face = v[np.abs(v[:, 1] - face_y) < 0.05]
        return [len(face[np.abs(face[:, 0] - (s["cable_channel_x"] + sx * s["cable_channel_w"] / 2)) < 0.05])
                for sx in (-1, 1)]

    assert all(n > 0 for n in slot_edges(+half_y)), "slot in the key-side wall"
    assert slot_edges(-half_y) == [0, 0], "no slot in the wall facing the user"
