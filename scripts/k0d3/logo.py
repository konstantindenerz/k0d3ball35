# SPDX-License-Identifier: MIT
"""Owner wordmark as a cell grid.

The `kode` wordmark in docs/images/logo.png is drawn on a strict rectangular grid: every
stroke is one cell wide, every gap one cell. This script recovers that grid from the
bitmap, turns the ink cells into a short list of axis-aligned rectangles and writes them as
cell coordinates. All millimetres live in the SCAD sources, so `-D logo_cell=0.8` stays live.

The grid is not hard-coded: the cell counts are the smallest ones for which every cell
samples as unambiguously ink or background. The raster rounds cell edges by up to a pixel,
so cells are sampled in their middle, never at their borders.

The supplied artwork is cropped: it ends mid-frame at the top while the bottom carries the
full `bar / stub / stub / bar-with-gaps` foot. The missing rows are mirrored in from the
bottom so the frame closes.

Writes two things from the same rectangles: hardware/case/logo_data.scad for the case model
and docs/images/logo.svg as the vector master everything else can start from.

The CLI lives in scripts/gen_logo.py; scripts/k0d3/pcb.py uses polygons() for the
silkscreen.
"""
from __future__ import annotations

import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SRC = REPO / "docs" / "images" / "logo.png"
DEFAULT_OUT = REPO / "hardware" / "case" / "logo_data.scad"
DEFAULT_SVG = REPO / "docs" / "images" / "logo.svg"

THRESHOLD = 120     # grey level above which a pixel counts as ink (the artwork is two-tone)
CORE = 0.6          # fraction of a cell sampled in its middle; the rest absorbs edge rounding
AMBIGUOUS = 0.25    # a sampled cell this far from 0 or 1 means the grid does not fit;
                    # one stroke of the artwork is rendered 5 px wide instead of 7 (0.8 ink)
MAX_CELLS = 120   # upper bound for the cell count search
EDGE_TOL = 0.9    # px a grid line may sit off its cell boundary (the raster rounds edges)
EDGE_SHARE = 0.9  # share of the edge weight a cell size must explain to be the grid
SPECK = 0.01      # ink fraction below which a band of rows is crop debris, not artwork
SPECKLE = 2       # px that must change before a line counts as a grid line at all
FOOT_ROWS = 2     # stub + bar-with-gaps: the frame foot, mirrored in at the cropped top

Grid = list[list[int]]


def fmt(v: float) -> str:
    v = round(float(v), 3)
    if v == 0:
        v = 0.0
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def load_ink(src: Path):
    from PIL import Image

    import numpy as np

    img = Image.open(src).convert("L")
    return (np.array(img) > THRESHOLD).astype(int)


def content_box(ink):
    """Bounding box of the artwork. Rows of ink form bands separated by blank rows; bands
    carrying almost no ink are specks left over from the crop and are dropped, while the
    gaps designed into the frame keep their bands."""
    import numpy as np

    rows = ink.sum(1) > 0
    bands, start = [], None
    for y, on in enumerate(list(rows) + [False]):
        if on and start is None:
            start = y
        elif not on and start is not None:
            bands.append((start, y))
            start = None
    if not bands:
        raise SystemExit("logo: no ink found, is the threshold right?")
    keep = [b for b in bands if int(ink[b[0]:b[1]].sum()) >= SPECK * int(ink.sum())]
    y0, y1 = keep[0][0], keep[-1][1]
    cols = np.where(ink[y0:y1].sum(0) > 0)[0]
    return y0, y1, int(cols.min()), int(cols.max()) + 1


def sample(ink, box, nx, ny):
    """Ink fraction of the middle of every cell, as a list of rows."""
    y0, y1, x0, x1 = box
    cx, cy = (x1 - x0) / nx, (y1 - y0) / ny
    pad_x, pad_y = cx * (1 - CORE) / 2, cy * (1 - CORE) / 2
    out = []
    for j in range(ny):
        ya, yb = round(y0 + j * cy + pad_y), round(y0 + (j + 1) * cy - pad_y)
        row = []
        for i in range(nx):
            xa, xb = round(x0 + i * cx + pad_x), round(x0 + (i + 1) * cx - pad_x)
            row.append(float(ink[ya:max(yb, ya + 1), xa:max(xb, xa + 1)].mean()))
        out.append(row)
    return out


def edges(lines) -> list[tuple[int, int]]:
    """Grid lines as (index, weight): positions where the artwork changes from one line to
    the next, weighted by how much of the line changes. A pixel or two is anti-aliasing."""
    out = []
    for i in range(1, len(lines)):
        w = int((lines[i] != lines[i - 1]).sum())
        if w > SPECKLE:
            out.append((i, w))
    return out


def fit_count(span: int, marks: list[tuple[int, int]], axis: str) -> int:
    """Smallest cell count whose boundaries explain the grid lines. A majority rather than
    all of them: the artwork is a raster and one of its strokes is rendered two pixels
    narrow, which would otherwise force an absurdly fine grid."""
    total = sum(w for _, w in marks)
    for n in range(1, min(MAX_CELLS, span) + 1):
        cell = span / n
        if cell < 2:
            break
        hit = sum(w for m, w in marks if abs(m - round(m / cell) * cell) <= EDGE_TOL)
        if hit >= EDGE_SHARE * total:
            return n
    raise SystemExit(f"logo: no cell grid fits the artwork in {axis}, has it been redrawn?")


def fit_counts(ink, box) -> tuple[int, int]:
    y0, y1, x0, x1 = box
    crop = ink[y0:y1, x0:x1]
    nx = fit_count(x1 - x0, edges(crop.T), "x")
    ny = fit_count(y1 - y0, edges(crop), "y")
    grid = sample(ink, box, nx, ny)
    bad = [(i, j, f) for j, row in enumerate(grid) for i, f in enumerate(row)
           if AMBIGUOUS < f < 1 - AMBIGUOUS]
    if bad:
        i, j, f = bad[0]
        raise SystemExit(f"logo: {len(bad)} cells are neither ink nor background, e.g. ({i}, {j}) at {f:.2f}")
    return nx, ny


def read_grid(src: Path) -> tuple[Grid, float]:
    """Sample the artwork into cells. Returns the grid and the cell aspect (height / width)."""
    ink = load_ink(src)
    box = content_box(ink)
    nx, ny = fit_counts(ink, box)
    grid = [[1 if f >= 0.5 else 0 for f in row] for row in sample(ink, box, nx, ny)]
    y0, y1, x0, x1 = box
    return grid, ((y1 - y0) / ny) / ((x1 - x0) / nx)


def close_frame(grid: Grid) -> Grid:
    """Mirror the frame foot in at the top, where the artwork is cropped."""
    if grid[0] != grid[-FOOT_ROWS - 1]:
        raise SystemExit("logo: the top does not start on the frame bar, has the crop changed?")
    head = [list(r) for r in reversed(grid[-FOOT_ROWS:])]
    return head + [list(r) for r in grid]


def rectangles(grid: Grid) -> list[tuple[int, int, int, int]]:
    """Greedy cover of the ink cells with axis-aligned rectangles (x, y, w, h)."""
    ny, nx = len(grid), len(grid[0])
    todo = [list(r) for r in grid]
    out: list[tuple[int, int, int, int]] = []
    for y in range(ny):
        for x in range(nx):
            if not todo[y][x]:
                continue
            w = 0
            while x + w < nx and todo[y][x + w]:
                w += 1
            h = 1
            while y + h < ny and all(todo[y + h][x + i] for i in range(w)):
                h += 1
            for j in range(y, y + h):
                for i in range(x, x + w):
                    todo[j][i] = 0
            out.append((x, y, w, h))
    return out


def render(grid: Grid, aspect: float, rects: list[tuple[int, int, int, int]], src: Path) -> str:
    ny, nx = len(grid), len(grid[0])
    ink = sum(sum(r) for r in grid)
    body = ", ".join(f"[{x}, {y}, {w}, {h}]" for x, y, w, h in rects)
    return "\n".join([
        "// generated by scripts/gen_logo.py, do not edit",
        f"// The owner wordmark from {src.relative_to(REPO)}, measured off its own grid: one cell is",
        "// one stroke width. Coordinates are cell indices, y counted from the top of the artwork,",
        "// the origin in its top left corner. The millimetre scale lives in params.scad",
        "// (logo_cell and logo_stretch).",
        "",
        f"logo_grid = [{nx}, {ny}];",
        f"logo_aspect = {fmt(aspect)};      // cell height / cell width in the source artwork",
        f"logo_ink_cells = {ink};",
        f"logo_rects = [{body}];",
        "",
    ])


def render_svg(grid: Grid, aspect: float, rects: list[tuple[int, int, int, int]], src: Path) -> str:
    """The same rectangles as a vector file: one cell wide and `aspect` cells tall, y down, so
    the SVG user units are the cell grid itself. Everything downstream of the artwork - the case
    engraving, a KiCad silkscreen footprint, the web - can start from this instead of the raster."""
    ny, nx = len(grid), len(grid[0])
    w, h = nx, round(ny * aspect, 3)
    body = "".join(f'M{x} {fmt(y * aspect)}h{dx}v{fmt(dy * aspect)}h-{dx}z'
                   for x, y, dx, dy in rects)
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<!-- generated by scripts/gen_logo.py from {src.relative_to(REPO)}, do not edit -->',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(w)} {fmt(h)}"',
        f'     width="{fmt(w)}" height="{fmt(h)}" fill="currentColor" role="img"',
        '     aria-label="kode">',
        f'  <path d="{body}"/>',
        '</svg>',
        "",
    ])


def polygons(cell: float, src: Path = DEFAULT_SRC) -> list[list[tuple[float, float]]]:
    """The wordmark as closed rectangles in millimetres, centred on (0, 0), y counted downward
    like the artwork and like KiCad. `cell` is the stroke width, which is also the smallest
    feature a fab has to hold."""
    grid, aspect, rects = build(src)
    nx, ny = len(grid[0]), len(grid)
    cy = cell * aspect
    ox, oy = nx * cell / 2, ny * cy / 2
    out = []
    for x, y, w, h in rects:
        x0, y0 = round(x * cell - ox, 4), round(y * cy - oy, 4)
        x1, y1 = round(x0 + w * cell, 4), round(y0 + h * cy, 4)
        out.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    return out


def size(cell: float, src: Path = DEFAULT_SRC) -> tuple[float, float]:
    """(width, height) in millimetres of the whole wordmark at this stroke width."""
    grid, aspect, _ = build(src)
    return round(len(grid[0]) * cell, 4), round(len(grid) * cell * aspect, 4)


def placed_polygons(cell: float, rotation: float = 0.0, mirror: bool = False,
                    src: Path = DEFAULT_SRC) -> list[list[tuple[float, float]]]:
    """polygons() turned by `rotation` degrees counter-clockwise on the page and, for the back
    face, mirrored in x so the wordmark reads the right way round when the board is flipped."""
    a = math.radians(rotation)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for poly in polygons(cell, src):
        pts = [(x * ca + y * sa, -x * sa + y * ca) for x, y in poly]
        if mirror:
            pts = [(-x, y) for x, y in pts][::-1]
        out.append([(round(x, 4), round(y, 4)) for x, y in pts])
    return out


def build(src: Path = DEFAULT_SRC) -> tuple[Grid, float, list[tuple[int, int, int, int]]]:
    grid, aspect = read_grid(Path(src))
    grid = close_frame(grid)
    return grid, aspect, rectangles(grid)


def write_data(path: Path = DEFAULT_OUT, src: Path = DEFAULT_SRC) -> Path:
    path = Path(path)
    grid, aspect, rects = build(src)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(grid, aspect, rects, Path(src)))
    return path


def write_svg(path: Path = DEFAULT_SVG, src: Path = DEFAULT_SRC) -> Path:
    path = Path(path)
    grid, aspect, rects = build(src)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_svg(grid, aspect, rects, Path(src)))
    return path
