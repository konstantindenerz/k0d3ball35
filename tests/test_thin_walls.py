# SPDX-License-Identifier: MIT
"""No skins in the printed parts: walls thinner than a slicer prints.

Numbers alone (watertight, bounding boxes, clearances) did not notice a 0.1 mm x 6.5 mm wall in
tray and lid in r2.4: two cuts that should have met left a skin between them (a stale notch
apothem in the case). A slicer silently drops such a wall. This test sections each part with
OpenSCAD every 0.4 mm and looks for material narrower than SKIN that stands at the same place
in several consecutive sections - a vertical skin. A single thin section is a cut through a
sloped face (chamfer, cone) and is ignored.
"""
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

shapely = pytest.importorskip("shapely")
trimesh = pytest.importorskip("trimesh")
from shapely.geometry import Polygon  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PARTS = [
    "hardware/case/stl/tray-left.stl", "hardware/case/stl/tray-right.stl",
    "hardware/case/stl/lid-left.stl", "hardware/case/stl/lid-right.stl",
    "hardware/case/stl/box-cap-left.stl", "hardware/case/stl/box-cap-right.stl",
    "hardware/case/stl/pocket-cover-right.stl",
    "hardware/trackball-cradle/stl/cradle-19mm-pocket.stl",
    "hardware/case/stl/pocket-clip-right.stl",
]
SKIN = 0.25      # mm: thinner than this does not print
STEP = 0.4       # mm between sections
TALL = 3         # consecutive sections: a skin at least ~1.2 mm tall


def _section(stl: Path, z: float, tmp: Path):
    scad, svg = tmp / "s.scad", tmp / "s.svg"
    scad.write_text(f'projection(cut = true) translate([0, 0, {-z}]) import("{stl}");')
    subprocess.run([shutil.which("openscad"), "--backend=manifold", "-o", str(svg), str(scad)],
                   capture_output=True, timeout=300)
    if not svg.exists():
        return None
    region = None
    for d in re.findall(r'd="([^"]+)"', svg.read_text()):
        for sub in re.split(r"[Zz]", d):
            pts = [tuple(map(float, p)) for p in re.findall(r"(-?[\d.]+),(-?[\d.]+)", sub)]
            if len(pts) >= 3:
                ring = Polygon(pts).buffer(0)
                region = ring if region is None else region.symmetric_difference(ring)
    svg.unlink()
    return region.buffer(0) if region is not None else None


@pytest.mark.skipif(shutil.which("openscad") is None, reason="openscad not installed")
@pytest.mark.parametrize("part", PARTS, ids=lambda p: Path(p).stem)
def test_no_skins(tmp_path, part):
    stl = ROOT / part
    z0, z1 = trimesh.load(stl, force="mesh").bounds[:, 2]
    runs: list[list] = []          # thin spots of the previous section, with their run length
    worst = []
    for z in np.arange(z0 + 0.15, z1 - 0.05, STEP):
        region = _section(stl, z, tmp_path)
        if region is None:
            runs = []
            continue
        thin = region.difference(region.buffer(-SKIN / 2, join_style=2).buffer(SKIN / 2, join_style=2))
        spots = [g for g in getattr(thin, "geoms", [thin]) if g.area > 0.3]
        new = []
        for g in spots:
            n = 1 + max((r for s, r in runs if s.buffer(0.2).intersects(g)), default=0)
            new.append((g, n))
            if n >= TALL:
                worst.append((round(float(z), 2), [round(v, 1) for v in g.bounds]))
        runs = new
    assert not worst, f"skins thinner than {SKIN} mm (z, print-frame bbox): {worst[:5]}"
