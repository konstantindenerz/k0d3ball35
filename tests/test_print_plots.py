# SPDX-License-Identifier: MIT
"""The 1:1 part-check plots (scripts/gen_print_plots.py).

A plot you lay a real connector on is worth nothing unless it is exactly 1:1 on a page the
printer will not rescale, so that is what is checked here: the KiCad SVG really is cropped to
the board, the A4 wrapper keeps the board at its true size, and the PDF page box comes out A4.
The header parser gets its own pure tests - it is the part that rots when KiCad changes its
output, and it runs where there is no kicad-cli.
"""
from __future__ import annotations

import re
import zlib

import pytest

from gen_print_plots import LAYERS, build, part_points, svg_box, svg_body, write
from gen_print_check import PAGE
from k0d3.geometry import REPO, load_layout

MAKEFILE = (REPO / "Makefile").read_text()


def header(width: str, height: str, box: str) -> str:
    return f'<svg\n  version="1.1"\n  width="{width}" height="{height}" viewBox="{box}">\n</svg>\n'


def test_svg_box_reads_millimetres():
    assert svg_box(header("120.9548mm", "86.6902mm", "0.0000 0.0000 120.9548 86.6902")) == \
        (120.9548, 86.6902)


@pytest.mark.parametrize("width, height, box, why", [
    ("4.76in", "3.41in", "0 0 4.76 3.41", "inches would silently scale the board by 25.4"),
    ("120.9548", "86.6902", "0 0 120.9548 86.6902", "a bare number has no scale at all"),
    ("120.9548mm", "86.6902mm", "0 0 241.9 173.4", "a viewBox at twice the page halves the board"),
])
def test_svg_box_refuses_anything_but_a_one_to_one_millimetre_page(width, height, box, why):
    with pytest.raises(ValueError):
        svg_box(header(width, height, box))
    assert why                                   # the parametrisation documents the failure


def test_svg_box_refuses_a_header_it_does_not_recognise():
    with pytest.raises(ValueError):
        svg_box('<svg version="1.1">\n</svg>\n')


def test_svg_body_drops_the_wrapper_and_keeps_the_drawing():
    body = svg_body(header("1mm", "1mm", "0 0 1 1").replace("</svg>", "<path d='M 0,0'/></svg>"))
    assert "<svg" not in body and "</svg>" not in body
    assert "<path d='M 0,0'/>" in body


@pytest.mark.parametrize("half", ["left", "right"])
def test_a_part_is_only_labelled_on_the_face_it_sits_on(half):
    """J1 moved to the key side in r2.2; a ring over bare laminate would send the reader wrong."""
    layout = load_layout(half)
    back = {ref for ref, _, _ in part_points(layout, "bottom")}
    front = {ref for ref, _, _ in part_points(layout, "top")}
    assert "PS1" in back and "PS1" not in front, "the slide switch is a back-side part"
    assert "U1" in back and "U1" in front, "the controller is through-hole, it shows on both"
    assert {k.ref for k in layout.thumbs} <= back, "the thumb sockets are checked on the back"
    if layout.cfg.get("fpc"):
        assert ("J1" in front) == (layout.fpc_side == "top")
        assert ("J1" in back) == (layout.fpc_side == "bottom")
    else:
        assert "J1" not in back | front, "no FPC connector on this half"


def test_the_layer_sets_are_the_fab_layers_of_their_own_face():
    """A B.Cu plot floods the page with the GND pour; the fab layers sketch the pads instead."""
    assert "B.Fab" in LAYERS["bottom"] and "F.Fab" not in LAYERS["bottom"]
    assert "F.Fab" in LAYERS["top"] and "B.Fab" not in LAYERS["top"]
    assert all(v.endswith("Edge.Cuts") and "Cu," not in v for v in LAYERS.values())


def test_the_makefile_offers_the_plots_as_a_target():
    """The ticket used to carry a copy-paste kicad-cli snippet that produced A3 pages."""
    for target in ("print", "print-check", "print-plots"):
        assert re.search(rf"^{target}:.*## ", MAKEFILE, re.M), f"no documented {target} target"
    phony = re.search(r"^\.PHONY:(.*)$", MAKEFILE, re.M).group(1).split()
    assert {"print", "print-check", "print-plots"} <= set(phony)


# ----------------------------------------------------------------- needs kicad-cli
@pytest.mark.kicad
@pytest.mark.parametrize("face", ["bottom", "top"])
def test_the_plot_is_the_board_on_an_a4_page_at_one_to_one(tmp_path, face, monkeypatch, kicad_cli):
    pytest.importorskip("cairosvg")
    import gen_print_plots

    monkeypatch.setattr(gen_print_plots, "OUT", tmp_path)
    monkeypatch.setattr(gen_print_plots, "KICAD_CLI", kicad_cli)
    pdf = write("right", face)
    layout = load_layout("right")

    plot = (tmp_path / f"right-{face}-plot.svg").read_text()
    w, h = svg_box(plot)
    bounds = layout.outline.bounds
    assert abs(w - (bounds[2] - bounds[0])) < 1.0, "the plot page is not the board's own extent"
    assert abs(h - (bounds[3] - bounds[1])) < 1.0

    svg = (tmp_path / f"right-{face}-1to1.svg").read_text()
    assert f'width="{PAGE[0]}mm" height="{PAGE[1]}mm"' in svg
    assert f"{w:.2f} mm" in svg and f"{h:.2f} mm" in svg, "the cross-check dimensions are missing"

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
        assert abs((box[2] - box[0]) * 25.4 / 72 - PAGE[0]) < 0.05
        assert abs((box[3] - box[1]) * 25.4 / 72 - PAGE[1]) < 0.05


@pytest.mark.kicad
@pytest.mark.parametrize("half", ["left", "right"])
def test_the_page_holds_the_board_its_labels_and_the_calibration_bar(tmp_path, monkeypatch,
                                                                     kicad_cli, half):
    """Nothing may fall off A4: the page is the one thing the printer must not have to resize.

    The KiCad drawing sits in a translated group and carries its own board-relative coordinates,
    so scanning the finished page would measure those instead of the wrapper. The wrapper is
    rebuilt here around an empty plot of the same size, which leaves only our own elements to
    scan, and the board box is checked separately from the plot's declared extent.
    """
    import gen_print_plots

    monkeypatch.setattr(gen_print_plots, "KICAD_CLI", kicad_cli)
    gen_print_plots.export_svg(
        REPO / "hardware" / f"{half}-pcb" / f"k0d3ball35-{half}.kicad_pcb",
        "bottom", tmp_path / "plot.svg")
    plot = (tmp_path / "plot.svg").read_text()
    w, h = svg_box(plot)
    layout = load_layout(half)

    assert gen_print_plots.MARGIN_X + w <= PAGE[0] - 5, (half, "the board is wider than A4 allows")
    assert gen_print_plots.BOARD_TOP + h <= PAGE[1] - 40, (half, "no room left for the bar below")

    bare = build(layout, "bottom", header(f"{w}mm", f"{h}mm", f"0 0 {w} {h}"))
    xs = [float(v) for v in re.findall(r'(?:\sx|cx)="(-?[\d.]+)"', bare)]
    ys = [float(v) for v in re.findall(r'(?:\sy|cy)="(-?[\d.]+)"', bare)]
    assert 0 <= min(xs) and max(xs) <= PAGE[0], (half, min(xs), max(xs))
    assert 0 <= min(ys) and max(ys) <= PAGE[1], (half, min(ys), max(ys))
