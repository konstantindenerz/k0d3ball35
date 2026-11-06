# SPDX-License-Identifier: MIT
"""Independent check of the exported gerber zips (ticket test-fab-gerber-viewer).

Parses every layer with gerbonara, compares the drill files with the KiCad boards, checks the
outline, the octagonal notch, the battery bay silkscreen and renders each board to
build/gerber-check/<board>-<side>.png for a visual pass. Skipped cleanly when gerbonara (or the
raster helpers cairosvg, Pillow, numpy) are not installed.
"""
from __future__ import annotations

import io
import math
import re
import warnings
import zipfile
from collections import Counter
from pathlib import Path

import pytest

gerbonara = pytest.importorskip("gerbonara")
from gerbonara import LayerStack  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "build" / "gerber-check"
DPMM = 20  # raster resolution for the pixel checks, px per mm

BOARDS = {
    "left": {
        "zip": "hardware/left-pcb/k0d3ball35-left-gerbers.zip",
        "pcb": "hardware/left-pcb/k0d3ball35-left.kicad_pcb",
        "prefix": "k0d3ball35-left-",
        "size": (121.0, 86.7),
        "keys": 18,
        "protel": False,
        "outlines": 1,
    },
    "right": {
        "zip": "hardware/right-pcb/k0d3ball35-right-gerbers.zip",
        "pcb": "hardware/right-pcb/k0d3ball35-right.kicad_pcb",
        "prefix": "k0d3ball35-right-",
        "size": (117.8, 80.4),
        "keys": 17,
        "protel": False,
        "outlines": 1,
    },
    "sensor": {
        "zip": "hardware/sensor-pcb/fab/k0d3ball35-sensor-r1-gerbers.zip",
        "pcb": "hardware/sensor-pcb/k0d3ball35-sensor.kicad_pcb",
        "prefix": "k0d3ball35-sensor-",
        "size": (26.0, 25.0),
        "keys": 0,
        "protel": False,  # hardware/sensor-pcb/export.sh passes --no-protel-ext like the main boards
        "outlines": 2,  # outer outline plus the sensor window
    },
}
MAIN = ("left", "right")

LAYER_FILES = {
    "F_Cu": {".gbr", ".gtl"},
    "B_Cu": {".gbr", ".gbl"},
    "F_Mask": {".gbr", ".gts"},
    "B_Mask": {".gbr", ".gbs"},
    "F_Paste": {".gbr", ".gtp"},
    "B_Paste": {".gbr", ".gbp"},
    "F_Silkscreen": {".gbr", ".gto"},
    "B_Silkscreen": {".gbr", ".gbo"},
    "Edge_Cuts": {".gbr", ".gm1"},
    "PTH": {".drl"},
    "NPTH": {".drl"},
    "PTH-drl_map": {".gbr"},
    "NPTH-drl_map": {".gbr"},
    "job": {".gbrjob"},
}
GRAPHIC_LAYERS = {
    ("top", "copper"), ("bottom", "copper"), ("top", "mask"), ("bottom", "mask"),
    ("top", "paste"), ("bottom", "paste"), ("top", "silk"), ("bottom", "silk"),
    ("mechanical", "outline"),
}

# KiCad coordinates of the battery bay (layout bay centre (-53.9, 17.5), 21 x 41 mm, offset 120/60)
BAY_KICAD = (55.6, 57.0, 76.6, 98.0)
BAY_TEXTS = ("LP552035 cell", "350 mAh", "leads +y")
# controller footprint area in KiCad coordinates (centre (62, 74), 18 x 33.5 mm)
CONTROLLER_KICAD = (53.0, 57.25, 71.0, 90.75)
NOTCH_APOTHEM = 15.0  # cradle radius 14 + 1 mm clearance
NOTCH_SIDE = 2 * NOTCH_APOTHEM * math.tan(math.radians(22.5))


def _zip(board: str) -> Path:
    path = REPO / BOARDS[board]["zip"]
    if not path.exists():
        pytest.skip(f"{path.relative_to(REPO)} not exported yet")
    return path


_STACKS: dict[str, LayerStack] = {}


def _stack(board: str) -> LayerStack:
    if board not in _STACKS:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _STACKS[board] = LayerStack.open(_zip(board))
    return _STACKS[board]


def _outline_width(stack: LayerStack) -> float:
    widths = {round(o.aperture.diameter, 3) for o in stack.outline.objects if getattr(o, "aperture", None)}
    return max(widths) if widths else 0.0


def _outline_segments(stack: LayerStack, index: int = 0) -> list[tuple[float, float, float, float]]:
    polys = list(stack.outline_polygons())
    return [(s.x1, s.y1, s.x2, s.y2) for s in polys[index]]


def _drill_hits(text: str) -> Counter:
    """Hits per tool diameter of an Excellon file, parsed independently of gerbonara."""
    tools: dict[str, float] = {}
    hits: Counter = Counter()
    current = None
    for line in text.splitlines():
        if m := re.match(r"T(\d+)C([\d.]+)", line):
            tools[m.group(1)] = float(m.group(2))
        elif m := re.match(r"T(\d+)$", line):
            current = m.group(1)
        elif current and re.match(r"X-?[\d.]+Y-?[\d.]+", line):
            hits[tools[current]] += 1
    return hits


def _pcb_drills(board: str) -> tuple[Counter, Counter]:
    """(PTH, NPTH) drill diameters of the KiCad board: pads with a drill plus vias."""
    text = (REPO / BOARDS[board]["pcb"]).read_text(encoding="utf-8")
    pth: Counter = Counter()
    npth: Counter = Counter()
    pad_re = re.compile(r'\(pad\s+"[^"]*"\s+(thru_hole|np_thru_hole)\s+\w+(?:[^()]|\([^()]*\))*?\(drill\s+([\d.]+)')
    for kind, drill in pad_re.findall(text):
        (pth if kind == "thru_hole" else npth)[float(drill)] += 1
    for drill in re.findall(r"\(via\s(?:[^()]|\([^()]*\))*?\(drill\s+([\d.]+)\)", text):
        pth[float(drill)] += 1
    return pth, npth


# ---------------------------------------------------------------- archive and layer set


@pytest.mark.parametrize("board", sorted(BOARDS))
def test_zip_contains_exactly_the_fab_files(board: str):
    cfg = BOARDS[board]
    with zipfile.ZipFile(_zip(board)) as zf:
        names = zf.namelist()
    assert all("/" not in n for n in names), f"{board}: zip must be flat, got {names}"
    assert all(n.startswith(cfg["prefix"]) for n in names), f"{board}: unexpected file names {names}"
    seen = {}
    for name in names:
        stem = name[len(cfg["prefix"]):]
        layer, dot, ext = stem.partition(".")
        assert layer in LAYER_FILES, f"{board}: unexpected file {name}"
        assert dot + ext in LAYER_FILES[layer], f"{board}: unexpected extension on {name}"
        if not cfg["protel"]:
            assert ext in {"gbr", "drl", "gbrjob"}, f"{board}: protel extension on {name}"
        seen[layer] = name
    missing = set(LAYER_FILES) - set(seen)
    assert not missing, f"{board}: missing fab files {sorted(missing)}"
    assert len(names) == len(LAYER_FILES)


@pytest.mark.parametrize("board", sorted(BOARDS))
def test_all_layers_parse(board: str):
    stack = _stack(board)
    assert set(stack.graphic_layers) == GRAPHIC_LAYERS
    for key, layer in stack.graphic_layers.items():
        if key[1] == "paste" and board == "sensor" and key[0] == "bottom":
            continue  # the sensor board has no bottom SMD parts
        assert len(layer.objects) > 0, f"{board}: layer {key} is empty"
    drills = {p.original_path.name.split("-")[-1].split(".")[0]: p for p in stack.drill_layers}
    assert set(drills) == {"PTH", "NPTH"}, f"{board}: drill files {sorted(drills)}"
    for name, layer in drills.items():
        assert len(layer.objects) > 0, f"{board}: {name} drill file is empty"


@pytest.mark.parametrize("board", sorted(BOARDS))
def test_drill_files_are_metric_with_explicit_units(board: str):
    with zipfile.ZipFile(_zip(board)) as zf:
        for name in zf.namelist():
            if name.endswith(".drl"):
                head = zf.read(name).decode("ascii", "replace")[:600]
                assert "METRIC" in head, f"{board}: {name} is not metric"
                assert "FMAT,2" in head, f"{board}: {name} lacks the Excellon format header"


# ---------------------------------------------------------------- outline


@pytest.mark.parametrize("board", sorted(BOARDS))
def test_board_extents_match_pcb_outline(board: str):
    stack = _stack(board)
    (x0, y0), (x1, y1) = stack.board_bounds()
    width = _outline_width(stack)
    size = (x1 - x0 - width, y1 - y0 - width)
    want = BOARDS[board]["size"]
    assert abs(size[0] - want[0]) < 0.15 and abs(size[1] - want[1]) < 0.15, (
        f"{board}: gerber extents {size[0]:.2f} x {size[1]:.2f} mm, expected {want[0]} x {want[1]} mm"
    )


@pytest.mark.parametrize("board", sorted(BOARDS))
def test_outline_is_closed(board: str):
    stack = _stack(board)
    polys = list(stack.outline_polygons())
    assert len(polys) == BOARDS[board]["outlines"], f"{board}: {len(polys)} outline polygons"
    # every Edge.Cuts vertex belongs to exactly two segments: closed loops, no dangling ends
    degree: Counter = Counter()
    for seg in stack.outline.objects:
        degree[(round(seg.x1, 3), round(seg.y1, 3))] += 1
        degree[(round(seg.x2, 3), round(seg.y2, 3))] += 1
    open_ends = [v for v, n in degree.items() if n != 2]
    assert not open_ends, f"{board}: outline not closed at {open_ends}"


@pytest.mark.parametrize("board", MAIN)
def test_main_board_outline_is_angular_without_cutout(board: str):
    """Only 90 degree steps plus the rotated thumb edges; the right board adds one 45 degree notch side."""
    segs = _outline_segments(_stack(board))
    angles = Counter()
    for x1, y1, x2, y2 in segs:
        ang = round(math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180, 1)
        angles[ang] += 1
    allowed = {0.0, 90.0, 10.0, 20.0, 100.0, 110.0}
    if board == "right":
        allowed.add(45.0)
    assert set(angles) <= allowed, f"{board}: unexpected outline directions {dict(angles)}"


def test_right_board_has_octagonal_notch_left_board_none():
    """The notch is the 45 degree side of a regular octagon (apothem 15 mm) plus its axis-aligned neighbours."""
    right = _outline_segments(_stack("right"))
    diagonals = [s for s in right if abs((math.degrees(math.atan2(s[3] - s[1], s[2] - s[0])) % 180) - 45) < 0.5]
    assert len(diagonals) == 1, f"right: expected one 45 degree notch side, got {diagonals}"
    x1, y1, x2, y2 = diagonals[0]
    assert abs(math.hypot(x2 - x1, y2 - y1) - NOTCH_SIDE) < 0.05
    idx = right.index(diagonals[0])
    before, after = right[idx - 1], right[(idx + 1) % len(right)]
    # the neighbours are the horizontal and vertical octagon sides (clipped by the board edge)
    horizontal = before if abs(before[1] - before[3]) < 1e-6 else after
    vertical = after if horizontal is before else before
    assert abs(horizontal[1] - horizontal[3]) < 1e-6 and abs(vertical[0] - vertical[2]) < 1e-6
    centre = (vertical[0] + NOTCH_APOTHEM, horizontal[1] - NOTCH_APOTHEM)
    # layout pocket centre (5, 64) is KiCad (125, 124), gerber y is negated
    assert abs(centre[0] - 125.0) < 0.05 and abs(centre[1] - -124.0) < 0.05, f"notch centre {centre}"
    # and the 45 degree side really is at apothem distance from that centre
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    assert abs(math.hypot(mx - centre[0], my - centre[1]) - NOTCH_APOTHEM) < 0.05

    left = _outline_segments(_stack("left"))
    assert not [s for s in left if abs((math.degrees(math.atan2(s[3] - s[1], s[2] - s[0])) % 180) - 45) < 0.5]


# ---------------------------------------------------------------- drills


@pytest.mark.parametrize("board", sorted(BOARDS))
def test_drill_hits_match_kicad_board(board: str):
    with zipfile.ZipFile(_zip(board)) as zf:
        pth = _drill_hits(zf.read(BOARDS[board]["prefix"] + "PTH.drl").decode())
        npth = _drill_hits(zf.read(BOARDS[board]["prefix"] + "NPTH.drl").decode())
    want_pth, want_npth = _pcb_drills(board)
    assert dict(pth) == dict(want_pth), f"{board}: PTH gerber {dict(pth)} vs board {dict(want_pth)}"
    assert dict(npth) == dict(want_npth), f"{board}: NPTH gerber {dict(npth)} vs board {dict(want_npth)}"
    # gerbonara sees the same hits
    stack = _stack(board)
    for layer in stack.drill_layers:
        hits = Counter(round(o.aperture.diameter, 3) for o in layer.objects)
        want = pth if layer.original_path.name.endswith("-PTH.drl") else npth
        assert dict(hits) == dict(want), f"{board}: gerbonara {dict(hits)} vs raw {dict(want)}"


@pytest.mark.parametrize("board", MAIN)
def test_main_board_drill_table(board: str):
    keys = BOARDS[board]["keys"]
    with zipfile.ZipFile(_zip(board)) as zf:
        pth = _drill_hits(zf.read(BOARDS[board]["prefix"] + "PTH.drl").decode())
        npth = _drill_hits(zf.read(BOARDS[board]["prefix"] + "NPTH.drl").decode())
    # the reversible Choc footprint carries three 3.05 mm socket boss holes per key
    assert npth[3.4] == keys, f"{board}: {npth[3.4]} switch centre holes for {keys} keys"
    assert npth[1.7] == 2 * keys, f"{board}: {npth[1.7]} switch post holes"
    assert npth[3.05] == 3 * keys, f"{board}: {npth[3.05]} socket boss holes"
    assert npth[2.2] == 5, f"{board}: {npth[2.2]} case holes, expected five and no cradle holes"
    assert npth[0.85] == 2, f"{board}: {npth[0.85]} power switch pegs"
    assert set(npth) == {3.4, 1.7, 3.05, 2.2, 0.85}, f"{board}: unexpected NPTH tools {sorted(npth)}"
    assert pth[1.0] == 26, f"{board}: {pth[1.0]} controller and battery pads"
    assert pth[0.4] == 3 * keys, f"{board}: {pth[0.4]} diode joiner holes"
    assert pth[0.3] > 0 and set(pth) == {1.0, 0.4, 0.3}, f"{board}: unexpected PTH tools {sorted(pth)}"


# ---------------------------------------------------------------- silkscreen


@pytest.mark.parametrize("board", MAIN)
def test_battery_bay_marking_on_back_silkscreen(board: str):
    pcb = (REPO / BOARDS[board]["pcb"]).read_text(encoding="utf-8")
    for text in BAY_TEXTS:
        m = re.search(r'\(gr_text "' + re.escape(text) + r'"\s*\(at ([\d.-]+) ([\d.-]+)[^)]*\)\s*\(layer "([^"]+)"\)', pcb)
        assert m, f"{board}: text {text!r} missing"
        x, y, layer = float(m.group(1)), float(m.group(2)), m.group(3)
        assert layer == "B.SilkS", f"{board}: {text!r} on {layer}"
        block = pcb[m.end():m.end() + 300]
        assert "(justify mirror)" in block.split("(gr_", 1)[0], f"{board}: {text!r} not mirrored"
        assert BAY_KICAD[0] < x < BAY_KICAD[2] and BAY_KICAD[1] < y < BAY_KICAD[3], f"{board}: {text!r} at {x},{y} outside the bay"
        # the label sits in the lower part of the bay, below the controller's hole rows
        assert CONTROLLER_KICAD[0] < x < CONTROLLER_KICAD[2] + 4 and y > CONTROLLER_KICAD[1]
    # the dashed rectangle is the only dashed item on B.SilkS
    dashed = re.findall(r"\(gr_poly\s*\(pts\s*((?:\(xy [\d. -]+\)\s*)+)\)\s*\(stroke\s*\(width [\d.]+\)\s*\(type dash\)\s*\)\s*\(fill no\)\s*\(layer \"B\.SilkS\"\)", pcb)
    assert len(dashed) == 1, f"{board}: {len(dashed)} dashed polygons on B.SilkS"
    pts = [tuple(map(float, xy.split())) for xy in re.findall(r"\(xy ([\d. -]+)\)", dashed[0])]
    xs, ys = sorted({p[0] for p in pts}), sorted({p[1] for p in pts})
    assert (xs[0], ys[0], xs[-1], ys[-1]) == BAY_KICAD, f"{board}: dashed bay rectangle at {xs}, {ys}"
    # and the gerber carries the strokes: text and dashes inside the bay rectangle on the bottom silk
    silk = _stack(board).graphic_layers[("bottom", "silk")]
    inside = 0
    for obj in silk.objects:
        (ox0, ox1), (oy0, oy1) = obj.bounding_box()
        if BAY_KICAD[0] - 0.3 <= ox0 and ox1 <= BAY_KICAD[2] + 0.3 and -BAY_KICAD[3] - 0.3 <= oy0 and oy1 <= -BAY_KICAD[1] + 0.3:
            inside += 1
    assert inside >= 80, f"{board}: only {inside} bottom silk strokes inside the battery bay"


@pytest.mark.parametrize("board", MAIN)
def test_half_label_on_front_silkscreen(board: str):
    pcb = (REPO / BOARDS[board]["pcb"]).read_text(encoding="utf-8")
    m = re.search(r'\(gr_text "(LEFT|RIGHT) half"\s*\(at [^)]*\)\s*\(layer "([^"]+)"\)', pcb)
    assert m and m.group(1) == board.upper() and m.group(2) == "F.SilkS", f"{board}: half label {m and m.groups()}"


# ---------------------------------------------------------------- raster checks and renders


@pytest.fixture(scope="module")
def raster_tools():
    np = pytest.importorskip("numpy")
    cairosvg = pytest.importorskip("cairosvg")
    pil = pytest.importorskip("PIL.Image")
    return np, cairosvg, pil


_RASTERS: dict[str, dict] = {}


def _rasters(board: str, tools) -> dict:
    """Binary pixel masks per layer plus the filled board area, all on one grid; renders the PNGs."""
    if board in _RASTERS:
        return _RASTERS[board]
    np, cairosvg, Image = tools
    stack = _stack(board)
    (x0, y0), (x1, y1) = stack.board_bounds()
    w, h = int(round((x1 - x0) * DPMM)), int(round((y1 - y0) * DPMM))
    bounds = ((x0, y0), (x1, y1))

    def raster(svg: str):
        png = cairosvg.svg2png(bytestring=svg.encode(), output_width=w, output_height=h, background_color="white")
        return np.array(Image.open(io.BytesIO(png)).convert("L")) < 128

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        layers = {k: raster(str(l.to_svg(force_bounds=bounds, fg="black", bg="white"))) for k, l in stack.graphic_layers.items()}
        drill = np.zeros((h, w), bool)
        for d in stack.drill_layers:
            drill |= raster(str(d.to_svg(force_bounds=bounds, fg="black", bg="white")))
        path = stack.outline_svg_d()
    board_svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x0} {-y1} {x1 - x0} {y1 - y0}">'
        f'<g transform="scale(1,-1)"><path d="{path}" fill="black" fill-rule="evenodd"/></g></svg>'
    )
    board_px = raster(board_svg)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for side in ("top", "bottom"):
        img = np.full((h, w, 3), 255, np.uint8)
        img[board_px] = (20, 70, 40)
        cu, mk, sk = layers[(side, "copper")], layers[(side, "mask")], layers[(side, "silk")]
        img[cu & board_px] = (40, 110, 60)
        img[mk] = (170, 140, 90)
        img[mk & cu] = (212, 175, 55)
        img[sk] = (245, 245, 245)
        img[drill] = (0, 0, 0)
        img[layers[("mechanical", "outline")]] = (255, 40, 40)
        if side == "bottom":
            img = img[:, ::-1]  # seen from below, so the mirrored silkscreen reads normally
        Image.fromarray(img).save(OUT_DIR / f"{board}-{side}.png")
    _RASTERS[board] = {"layers": layers, "board": board_px, "drill": drill, "origin": (x0, y1), "size": (w, h)}
    return _RASTERS[board]


@pytest.mark.parametrize("board", sorted(BOARDS))
def test_renders_written(board: str, raster_tools):
    _rasters(board, raster_tools)
    for side in ("top", "bottom"):
        png = OUT_DIR / f"{board}-{side}.png"
        assert png.exists() and png.stat().st_size > 1000


@pytest.mark.parametrize("board", sorted(BOARDS))
@pytest.mark.parametrize("side", ("top", "bottom"))
def test_no_silkscreen_over_mask_openings(board: str, side: str, raster_tools):
    r = _rasters(board, raster_tools)
    silk, mask = r["layers"][(side, "silk")], r["layers"][(side, "mask")]
    overlap = int((silk & mask).sum())
    assert overlap == 0, f"{board} {side}: {overlap} silkscreen pixels on exposed pads ({overlap / DPMM**2:.2f} mm2)"


@pytest.mark.parametrize("board", sorted(BOARDS))
@pytest.mark.parametrize("side", ("top", "bottom"))
def test_copper_stays_inside_outline(board: str, side: str, raster_tools):
    r = _rasters(board, raster_tools)
    outside = int((r["layers"][(side, "copper")] & ~r["board"]).sum())
    assert outside <= 0.1 * DPMM**2, f"{board} {side}: {outside / DPMM**2:.2f} mm2 copper outside the outline"


def test_no_copper_inside_the_right_notch(raster_tools):
    np = raster_tools[0]
    r = _rasters("right", raster_tools)
    x0, y1 = r["origin"]
    w, h = r["size"]
    cx, cy = 125.0, -124.0
    ys, xs = np.mgrid[0:h, 0:w]
    px, py = x0 + xs / DPMM, y1 - ys / DPMM
    inset = NOTCH_APOTHEM - 0.3
    octagon = (np.abs(px - cx) <= inset) & (np.abs(py - cy) <= inset) & (np.abs(px - cx) + np.abs(py - cy) <= inset * math.sqrt(2))
    assert octagon.sum() > 0
    assert int((octagon & r["board"]).sum()) == 0, "board material inside the pocket octagon"
    for side in ("top", "bottom"):
        inside = int((octagon & r["layers"][(side, "copper")]).sum())
        assert inside == 0, f"{side}: {inside} copper pixels inside the notch"
