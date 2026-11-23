# SPDX-License-Identifier: MIT
"""The printed keycaps (hardware/keycaps): inside the envelope the case is checked against, legs
that fit the Choc V1 slider, a fit test with the ladder it claims, and committed STLs that are
what the sources render.

The case, the lid and the interference test treat a keycap as a 17.5 x 16.5 mm prism from
cap_skirt_z to cap_top_z (hardware/case/params.scad). These tests put each printed cap, read back
from the committed STL into the cap's place over the PCB, inside that prism, so every case check
holds for them unchanged.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest
from shapely.geometry import Polygon

from mesh_tools import section

ROOT = Path(__file__).resolve().parents[1]
KEYCAPS = ROOT / "hardware" / "keycaps"
CASE_PARAMS = ROOT / "hardware" / "case" / "params.scad"
CAPS = {"finger": "keycap-1u.stl", "homing": "keycap-1u-homing.stl", "thumb": "keycap-thumb.stl"}

trimesh = pytest.importorskip("trimesh")
np = pytest.importorskip("numpy")


def _num(path: Path, name: str) -> float:
    return float(re.search(rf"^{name}\s*=\s*(-?[\d.]+);", path.read_text(), re.M)[1])


def kp(name: str) -> float:
    return _num(KEYCAPS / "params.scad", name)


def cp(name: str) -> float:
    return _num(CASE_PARAMS, name)


def fit_steps() -> list[float]:
    m = re.search(r"^fit_steps\s*=\s*\[([^\]]+)\];", (KEYCAPS / "params.scad").read_text(), re.M)
    return [float(v) for v in m[1].split(",")]


def over_pcb(path: Path):
    """A committed cap STL (print frame: standing on its back face) in its place over the PCB:
    x across, y away from the user, z up from the PCB top. keycaps.scad: print = (x, cap z,
    cap_d / 2 - cap y)."""
    mesh = trimesh.load(path, force="mesh")
    turn = np.array([[1, 0, 0, 0], [0, 0, -1, kp("cap_d") / 2], [0, 1, 0, kp("plane_z")], [0, 0, 0, 1]], float)
    mesh.apply_transform(turn)
    return mesh


@pytest.mark.parametrize("kind", CAPS)
def test_cap_is_inside_the_case_envelope(kind):
    mesh = over_pcb(KEYCAPS / "stl" / CAPS[kind])
    (x0, y0, z0), (x1, y1, z1) = mesh.bounds
    cap_w, cap_h = map(float, re.search(r"^cap_size\s*=\s*\[([\d.]+),\s*([\d.]+)\];", CASE_PARAMS.read_text(), re.M).groups())
    assert x1 - x0 <= cap_w and y1 - y0 <= cap_h, f"{kind}: {x1 - x0:.2f} x {y1 - y0:.2f} over cap_size"
    assert abs(x0 + x1) < 0.01 and abs(y0 + y1) < 0.01, "not centred on the switch"
    assert z1 <= cp("cap_top_z") + 1e-6, f"{kind}: top at {z1:.2f}, over cap_top_z"
    assert abs(z1 - (kp("plane_z") + kp("top_h"))) < 0.01
    # the skirt: the body without the legs (the legs reach into the switch, below the skirt)
    body = mesh.vertices[(np.abs(mesh.vertices[:, 0]) > kp("cap_w") / 2 - kp("cap_wall"))]
    skirt = body[:, 2].min()
    assert skirt >= cp("cap_skirt_z"), f"{kind}: skirt at {skirt:.2f}, under cap_skirt_z"
    assert abs(skirt - (kp("plane_z") - kp("skirt"))) < 0.01


def test_pressed_cap_clears_the_switch():
    """Pressed through the full travel the skirt stays over the 15 x 15 flange (which the cavity
    does not cover in y), and the cavity clears the upper housing on every side."""
    pressed = kp("plane_z") - kp("skirt") - kp("switch_travel")
    assert pressed >= kp("flange_top_z") + 0.5, f"skirt {pressed:.2f} at full travel"
    assert kp("plane_z") - kp("switch_travel") >= kp("flange_top_z")
    mesh = over_pcb(KEYCAPS / "stl" / CAPS["finger"])
    cut = section(mesh, kp("plane_z") - kp("skirt") / 2)
    cavity = max((Polygon(r) for p in getattr(cut, "geoms", [cut]) for r in p.interiors), key=lambda r: r.area)
    cx0, cy0, cx1, cy1 = cavity.bounds
    for side in (cx1 - cx0, cy1 - cy0):
        assert side >= kp("housing_w") + 2 * 0.3, f"cavity {side:.2f} mm against the {kp('housing_w')} mm housing"


@pytest.mark.parametrize("kind", CAPS)
def test_legs_fit_the_slider(kind):
    mesh = over_pcb(KEYCAPS / "stl" / CAPS[kind])
    cut = section(mesh, kp("plane_z") - 2.0)      # below the skirt: only the two legs
    legs = sorted(getattr(cut, "geoms", [cut]), key=lambda g: g.centroid.x)
    assert len(legs) == 2, f"{kind}: {len(legs)} pieces 2 mm under the plane"
    fit = kp("stem_fit")
    for g in legs:
        x0, y0, x1, y1 = g.bounds
        assert abs((x1 - x0) - (kp("leg_w") - fit)) < 0.02, f"leg width {x1 - x0:.3f}"
        assert abs((y1 - y0) - (kp("leg_l") - fit)) < 0.02, f"leg length {y1 - y0:.3f}"
        assert abs(g.centroid.y) < 0.01
    assert abs(legs[1].centroid.x - legs[0].centroid.x - kp("leg_dx")) < 0.01
    assert abs(mesh.bounds[0][2] - (kp("plane_z") - kp("leg_h"))) < 0.01, "leg length"


def test_homing_bar_only_on_the_homing_cap():
    """The bar stands proud of the dish on the homing cap and nowhere else; the thumb cap has no
    dish."""
    from shapely.geometry import box

    dish = kp("plane_z") + kp("top_h") - kp("dish_depth")
    middle = box(-3, -7, 3, 7)
    over = {k: section(over_pcb(KEYCAPS / "stl" / f), dish + kp("bar_h") - 0.1).intersection(middle) for k, f in CAPS.items()}
    bar = over["homing"]
    assert bar.area > 2.0 and abs(bar.centroid.y - kp("bar_y")) < 0.05 and abs(bar.centroid.x) < 0.05
    assert over["finger"].area < 0.01, "the finger cap has something over its dish"
    assert section(over_pcb(KEYCAPS / "stl" / CAPS["homing"]), dish + kp("bar_h") + 0.01).intersection(middle).area < 0.01
    flat = section(over_pcb(KEYCAPS / "stl" / CAPS["thumb"]), kp("plane_z") + kp("top_h") - 0.01)
    assert flat.contains(box(-4, -4, 4, 4)), "the thumb top is not flat in the middle"


def test_fit_test_ladder():
    """Six tabs, one per stem_fit step, each with the legs of its step; the notches count up."""
    steps = fit_steps()
    assert steps == sorted(steps) and len(steps) == 6 and steps[0] == 0.0
    mesh = trimesh.load(KEYCAPS / "stl" / "keycap-fit-test.stl", force="mesh")
    # print frame: the legs lie along -y below the plate (y 0 .. tab_t)
    v = mesh.vertices
    pitch = kp("tab_pitch")
    for i, fit in enumerate(steps):
        cx = (i - (len(steps) - 1) / 2) * pitch
        leg = v[(v[:, 1] < -1.0) & (np.abs(v[:, 0] - (cx + kp("leg_dx") / 2)) < 1.5)]
        width = leg[:, 0].max() - leg[:, 0].min()
        assert abs(width - (kp("leg_w") - fit)) < 0.02, f"tab {i + 1}: leg {width:.3f}, want {kp('leg_w') - fit:.2f}"
        top = v[(np.abs(v[:, 0] - cx) < kp("tab_w") / 2) & (v[:, 1] > 0.1)]
        assert abs(top[:, 2].max() - kp("tab_d")) < 0.01
    # n notches in the top edge of tab n: count the gaps in a cut just under the top edge
    cut = section(mesh, kp("tab_d") - kp("notch") / 2)
    pieces = sorted(getattr(cut, "geoms", [cut]), key=lambda g: g.centroid.x)
    per_tab = [sum(1 for g in pieces if abs(g.centroid.x - (i - 2.5) * pitch) < kp("tab_w") / 2) for i in range(6)]
    assert per_tab == [n + 1 for n in range(1, 7)], f"pieces per tab under the notches: {per_tab}"


def test_counts_match_the_layout():
    """The README's set is the board's keys: finger, homing and thumb caps per half."""
    import json

    data = json.loads((ROOT / "docs" / "data" / "layout.json").read_text())
    count = {h: {k: sum(1 for key in d["keys"] if key["cap"] == k) for k in CAPS} for h, d in data["halves"].items()}
    assert count == {"left": {"finger": 14, "homing": 1, "thumb": 3}, "right": {"finger": 14, "homing": 1, "thumb": 2}}
    assert all(next(k for k in d["keys"] if k["cap"] == "homing")["ref"] == "SW13" for d in data["halves"].values())


def _openscad():
    exe = shutil.which("openscad") or "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
    return exe if Path(exe).exists() else None


@pytest.mark.skipif(_openscad() is None, reason="openscad not installed")
@pytest.mark.parametrize("part, stl", [("finger", "keycap-1u.stl"), ("homing", "keycap-1u-homing.stl"),
                                       ("thumb", "keycap-thumb.stl"), ("fit_test", "keycap-fit-test.stl")])
def test_committed_stl_is_fresh(tmp_path, part, stl):
    out = tmp_path / stl
    res = subprocess.run([_openscad(), "--backend", "manifold", "-D", f'part="{part}"', "-o", str(out),
                          str(KEYCAPS / "keycaps.scad")], capture_output=True, text=True, timeout=300)
    assert res.returncode == 0, res.stderr
    assert "WARNING" not in res.stderr and "ERROR" not in res.stderr
    new, old = trimesh.load(out, force="mesh"), trimesh.load(KEYCAPS / "stl" / stl, force="mesh")
    assert np.allclose(new.bounds, old.bounds, atol=1e-3) and abs(new.volume - old.volume) < 0.01
