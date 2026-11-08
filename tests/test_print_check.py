# SPDX-License-Identifier: MIT
"""The 1:1 measuring sheet (scripts/gen_print_check.py) is only worth printing if it is really
1:1 and if its printed numbers are the layout's numbers. Both are checked here: the page is A4
in millimetres, the PDF page box comes out as A4 in points, every legend value is recomputed
from the layout, and nothing is drawn off the page."""
from __future__ import annotations

import json
import math
import re
import zlib

import pytest

from gen_print_check import PAGE, ball_top_above_pcb, build, stamp
from k0d3.footprints import nice_nano_tht
from k0d3.geometry import HALVES, REPO, load_layout


@pytest.fixture(scope="module", params=HALVES)
def half(request) -> str:
    return request.param


@pytest.fixture(scope="module")
def sheet(half):
    layout = load_layout(half)
    svg, dims = build(layout)
    return layout, svg, {d.name: d.value for d in dims}


def _prose(svg: str) -> str:
    """The sheet's running text, re-joined: textwrap splits a paragraph over several <text>
    elements, so a phrase like "make print-plots" is not findable in the raw markup."""
    return " ".join(re.findall(r"<text[^>]*>([^<]*)</text>", svg))


def test_page_is_a4_in_millimetres(sheet):
    _, svg, _ = sheet
    assert f'width="{PAGE[0]}mm" height="{PAGE[1]}mm"' in svg
    assert f'viewBox="0 0 {PAGE[0]} {PAGE[1]}"' in svg
    assert PAGE == (210.0, 297.0)


def test_sheet_carries_the_commit_it_was_made_from(sheet):
    """A printout on the desk has to say which state of the repository it came from."""
    import subprocess

    _, svg, _ = sheet
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                             capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                                    capture_output=True, text=True, check=True).stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("not a git checkout")
    assert f">{rev}" in svg, "the sheet does not name the commit"
    assert (f"{rev}-dirty" in svg) == dirty, "the dirty marker does not match the working tree"
    assert stamp() in svg


def test_dimensions_are_the_layout_values(sheet):
    layout, _, dims = sheet
    px, py = layout.pitch
    bounds = layout.outline.bounds
    assert dims["Board outline, widest point across"] == round(bounds[2] - bounds[0], 2)
    assert dims["Board outline, tallest point down"] == round(bounds[3] - bounds[1], 2)
    assert dims[f"Row 0, pinky to inner key centre (4 x {px:g} mm pitch)"] == round(4 * px, 2)
    assert dims[f"Middle column, top to bottom key centre (2 x {py:g} mm)"] == round(2 * py, 2)

    pads = nice_nano_tht({h: "" for h in range(1, 25)}).pads
    xs = sorted({round(p.x, 3) for p in pads})
    ys = sorted({round(p.y, 3) for p in pads})
    assert dims["Controller hole rows, centre to centre"] == round(xs[-1] - xs[0], 2) == 15.24
    assert dims["Controller row, first to last hole (11 x 2.54 mm)"] == round(ys[-1] - ys[0], 2) == 27.94

    bay = layout.cfg["battery"]["bay"]
    cell = layout.cfg["battery"]["cell"]
    assert dims[f"Battery bay (dashed), across the {cell}"] == bay["size"]["x"]
    assert dims["Battery bay, along the cell"] == bay["size"]["y"]

    holes = layout.cfg["mounting_holes"]
    assert dims["Mounting holes 1 and 2 (same column), centre to centre"] == \
        round(abs(holes[1]["y"] - holes[0]["y"]), 2)

    if layout.has_ball:
        tb = layout.cfg["trackball"]
        assert dims["Notch octagon, across the flats"] == \
            round(tb["cradle_diameter"] + 2 * tb["pocket"]["notch_clearance"], 2)
        assert dims[f"Ball circle ({tb['ball_diameter']:g} mm POM ball)"] == tb["ball_diameter"]
    else:
        assert not [k for k in dims if "Ball" in k or "Notch" in k], "no pocket on the left half"


# The two ball-surface reaches are marked on the drawing by a tick where the travel line crosses
# the ball circle, not by a number: a fourth figure in that corner would sit on the octagon.
TICK_ONLY = ", what the thumb covers"


def test_every_legend_value_is_printed_on_the_board(sheet):
    """A legend line without its dimension on the drawing would send the user hunting.

    The legend prints the value itself, so presence in the markup proves nothing - what counts is
    a second occurrence, the one on the drawing.
    """
    _, svg, dims = sheet
    for name, value in dims.items():
        text = f"{value:.2f} mm".replace(".00 mm", ".0 mm")
        drawn = svg.count(f">{text}<") + svg.count(f">{text} =") - 1      # minus the legend line
        if name.endswith(TICK_ONLY):
            assert drawn == 0, f"{name}: marked by a tick, a number there would crowd the pocket"
        else:
            assert drawn >= 1, f"{name} ({text}) is in the legend but not on the drawing"


def test_nothing_is_drawn_off_the_page(sheet):
    _, svg, _ = sheet
    xs = [float(v) for v in re.findall(r'(?:\sx|cx)="(-?[\d.]+)"', svg)]
    ys = [float(v) for v in re.findall(r'(?:\sy|cy)="(-?[\d.]+)"', svg)]
    path_pts = [(float(a), float(b)) for a, b in re.findall(r"(-?[\d.]+),(-?[\d.]+)", svg)]
    assert min(xs) >= 0 and max(xs) <= PAGE[0], (min(xs), max(xs))
    assert min(ys) >= 0 and max(ys) <= PAGE[1] - 8, (min(ys), max(ys))
    assert all(0 <= x <= PAGE[0] and 0 <= y <= PAGE[1] for x, y in path_pts)


def test_pdf_page_box_is_a4_at_one_to_one(tmp_path, half):
    """cairosvg converts mm to px at its `dpi`; at anything but 72 the PDF comes out scaled."""
    pytest.importorskip("cairosvg")
    import cairosvg

    svg, _ = build(load_layout(half))
    pdf = tmp_path / f"{half}.pdf"
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(pdf), dpi=72)
    data = pdf.read_bytes()
    boxes = []
    for m in re.finditer(rb"stream\r?\n", data):
        try:
            raw = zlib.decompress(data[m.end():data.find(b"endstream", m.end())])
        except zlib.error:
            continue
        boxes += [[float(v) for v in b.group(1).split()]
                  for b in re.finditer(rb"/MediaBox\s*\[([^\]]*)\]", raw)]
    assert boxes, "no MediaBox found in the PDF"
    for box in boxes:
        width_mm = (box[2] - box[0]) * 25.4 / 72
        height_mm = (box[3] - box[1]) * 25.4 / 72
        assert abs(width_mm - PAGE[0]) < 0.05 and abs(height_mm - PAGE[1]) < 0.05, (width_mm, height_mm)


def test_thumb_reach_is_measured_to_the_ball_surface(sheet):
    """The thumb touches the ball's near surface, not its centre.

    `issues/mech-thumb-arc-tuning.md` is the only open finding whose fix would be a layout change,
    and this sheet is its test method, so the sheet has to print the distance the thumb actually
    covers. The centre distance alone reads as reachable when it is not.
    """
    layout, _, dims = sheet
    if not layout.has_ball:
        assert not [k for k in dims if "surface" in k], "no ball, no surface reach on the left half"
        return
    bx, by = layout.ball_center
    r = layout.cfg["trackball"]["ball_diameter"] / 2
    thumbs = sorted((k for k in layout.keys if k.kind == "thumb"), key=lambda k: -k.x)
    assert len(thumbs) == 2
    for i, k in enumerate(thumbs):
        d = math.dist((bx, by), (k.x, k.y))
        near = "near" if i == 0 else "far"
        assert dims[f"Ball centre to thumb key {k.ref} ({near})"] == round(d, 2)
        assert dims[f"Ball surface to thumb key {k.ref} ({near}), what the thumb covers"] == \
            round(d - r, 2)


def test_stack_height_for_the_motion_test_comes_from_the_cradle(sheet):
    """The sheet asks the reader to stand something as tall as the ball on the circle and swipe.

    That height has to follow the cradle rather than be typed into the generator, so choosing the
    25 mm fallback (issues/hw-25mm-cradle-fallback.md) updates the paper by itself.
    """
    layout, svg, _ = sheet
    if not layout.has_ball:
        assert "tall on the ball circle" not in _prose(svg)
        return
    ball_d = layout.cfg["trackball"]["ball_diameter"]
    variants = json.loads((REPO / "hardware" / "trackball-cradle" / "stack.json").read_text())["variants"]
    expected = next(v["ball_top_above_pcb_top"] for v in variants.values()
                    if math.isclose(v["ball_d"], ball_d, abs_tol=1e-6))
    assert ball_top_above_pcb(ball_d) == expected
    assert f"{expected:.1f} mm" in _prose(svg), "the stack height is not printed on the sheet"


def test_the_sheet_points_at_the_plot_target_for_footprints(sheet):
    """Footprints are checked on the part-check plots, which are a make target, not a snippet."""
    layout, svg, _ = sheet
    prose = _prose(svg)
    assert "make print-plots" in prose
    assert f"build/print/{layout.half}-bottom-1to1.pdf" in prose
