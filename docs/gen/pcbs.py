# SPDX-License-Identifier: MIT
"""docs/data/pcbs.json: the two main boards for the PCBs tab.

Per board: the repo paths of the KiCad file, the GLB and the layer SVGs written by `make pcb-3d`
(scripts/export_site_pcbs.py), the PNG renders, STEP and gerber zip written by `make gerbers`,
the shared viewBox of the layer SVGs, and facts read from the board
file (copper layers, thickness, footprints, tracks, vias), from the outline SVG (size), from
hardware/layout/output/points-<half>.json (keys, ball notch) and from spec/03-bom.md (finish, the
notes column). Nothing here is measured in a browser, so the file is deterministic.

Since r2.4 the trackball sensor is a bought PAW3222 module, not a board of ours, so the tab shows
the left and right halves only (issues/hw-paw3222-variant.md).
"""
from __future__ import annotations

import json
import re

from . import REPO

# id, name, folder, file stem, PNG renders, STEP, gerber zip, the parts worth naming (ref -> role)
BOARDS = (
    ("left", "Left PCB", "hardware/left-pcb", "k0d3ball35-left",
     ("renders/left-pcb-top.png", "renders/left-pcb-bottom.png"), "k0d3ball35-left.step", "k0d3ball35-left-gerbers.zip",
     {"U1": "Controller", "J3": "Battery connector", "J2": "Battery pads", "PS1": "Power switch", "RB1": "Reset button"}),
    ("right", "Right PCB", "hardware/right-pcb", "k0d3ball35-right",
     ("renders/right-pcb-top.png", "renders/right-pcb-bottom.png"), "k0d3ball35-right.step", "k0d3ball35-right-gerbers.zip",
     {"U1": "Controller", "J1": "Sensor cable connector", "J3": "Battery connector", "J2": "Battery pads",
      "PS1": "Power switch", "RB1": "Reset button"}),
)
# layer file -> label, side, kind, colour on the plot. Order: drawn first to last when seen from the front.
LAYERS = (
    ("B.Silkscreen", "Back silkscreen", "back", "silk", "#ECE8DA"),
    ("B.Mask", "Back solder mask", "back", "mask", "#1E5A3E"),
    ("B.Cu", "Back copper", "back", "copper", "#C27C45"),
    ("F.Cu", "Front copper", "front", "copper", "#D9A843"),
    ("F.Mask", "Front solder mask", "front", "mask", "#1E5A3E"),
    ("F.Silkscreen", "Front silkscreen", "front", "silk", "#F6F3E8"),
    ("Edge.Cuts", "Board edge", "both", "edge", None),
)
SIDE = {"F.Cu": "front", "B.Cu": "back"}
# what each face is in use
FACE = {"left": {"F.Cu": "front (key side)"}, "right": {"F.Cu": "front (key side)"}}


def _footprints(text: str) -> list[dict]:
    out = []
    for blk in text.split("\n\t(footprint ")[1:]:
        out.append({
            "ref": re.search(r'\(property "Reference" "([^"]*)"', blk).group(1),
            "value": re.search(r'\(property "Value" "([^"]*)"', blk).group(1),
            "footprint": blk.split('"')[1].split(":")[-1],
            "layer": re.search(r'\n\t\t\(layer "([^"]+)"', blk).group(1),
        })
    return out


def _bom_rows() -> dict[str, list[str]]:
    rows = {}
    for line in (REPO / "spec/03-bom.md").read_text().splitlines():
        m = re.search(r"PCB `(k0d3ball35-\w+)`", line)
        if m and line.startswith("|"):
            rows[m.group(1)] = [c.strip() for c in line.strip("|").split("|")]
    return rows


def _viewbox(svg: str) -> list[float]:
    return [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]


def _outline_size(svg: str) -> tuple[float, float]:
    d = re.search(r' d="([^"]+)"', svg).group(1)
    pts = [tuple(map(float, p.split(","))) for p in re.findall(r"-?[\d.]+,-?[\d.]+", d)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return max(xs) - min(xs), max(ys) - min(ys)


def board(spec: tuple, bom: dict) -> dict:
    bid, name, folder, stem, pngs, step, zip_, roles = spec
    pcb = REPO / folder / f"{stem}.kicad_pcb"
    text = pcb.read_text()
    layers_dir = f"{folder}/renders/layers"
    outline_svg = (REPO / layers_dir / "outline.svg").read_text()
    view = _viewbox(outline_svg)
    for lid, *_ in LAYERS:
        assert _viewbox((REPO / layers_dir / f"{lid}.svg").read_text()) == view, f"{bid} {lid}: viewBox differs, run make pcb-3d"
    w, h = _outline_size(outline_svg)
    copper = len(re.findall(r'^\t\t\(\d+ "[^"]+\.Cu" signal\)', text, re.M))
    thickness = float(re.search(r"\(general\s*\(thickness ([\d.]+)\)", text).group(1))
    fps = _footprints(text)
    by_ref = {f["ref"]: f for f in fps}
    row = bom.get(stem, [])
    spec_col = row[2] if len(row) > 2 else ""
    finish = next((f for f in ("ENIG", "HASL") if f in spec_col), None)
    copper_weight = (re.search(r"(\d+ oz)", spec_col) or [None, None])[1] if spec_col else None
    keys = notch = None
    points = REPO / f"hardware/layout/output/points-{bid}.json"
    if points.exists():
        p = json.loads(points.read_text())
        keys = len(p["keys"])
        if bid == "right":
            n = p["trackball"]["notch"]
            notch = round((max(x for x, _ in n) - min(x for x, _ in n)) / 2, 2)
    facts = [["Outline", f"{w:.1f} x {h:.1f} mm"], ["Thickness", f"{thickness:g} mm"], ["Copper layers", str(copper)]]
    if copper_weight:
        facts.append(["Copper weight", copper_weight])
    if finish:
        facts.append(["Surface finish", finish])
    if keys:
        facts.append(["Key positions", str(keys)])
    if notch:
        facts.append(["Ball pocket notch", f"octagon, apothem {notch:g} mm"])
    facts += [["Footprints", str(len(fps))],
              ["Track segments", str(len(re.findall(r"^\t\(segment\b", text, re.M)))],
              ["Vias", str(len(re.findall(r"^\t\(via\b", text, re.M)))]]
    parts = [{"ref": r, "role": role, "value": by_ref[r]["value"], "footprint": by_ref[r]["footprint"],
              "side": FACE[bid].get(by_ref[r]["layer"], SIDE.get(by_ref[r]["layer"], by_ref[r]["layer"]))} for r, role in roles.items() if r in by_ref]
    files = {
        "kicad_pcb": f"{folder}/{stem}.kicad_pcb",
        "glb": f"{folder}/renders/{stem}.glb",
        "outline": f"{layers_dir}/outline.svg",
        "render_top": f"{folder}/{pngs[0]}",
        "render_bottom": f"{folder}/{pngs[1]}",
        "step": f"{folder}/{step}",
        "gerbers": f"{folder}/{zip_}",
    }
    for k, v in files.items():
        assert (REPO / v).is_file(), f"{bid}: {v} missing"
    return {
        "id": bid,
        "name": name,
        "stem": stem,
        "folder": folder,
        "files": files,
        "sizes": {k: (REPO / v).stat().st_size for k, v in files.items()},
        "layers": [{"id": lid, "label": label, "side": side, "kind": kind, "color": color, "path": f"{layers_dir}/{lid}.svg"}
                   for lid, label, side, kind, color in LAYERS],
        "viewbox": view,
        "size_mm": [round(w, 2), round(h, 2)],
        "thickness_mm": thickness,
        "copper_layers": copper,
        "finish": finish,
        "keys": keys,
        "notes": row[5] if len(row) > 5 and "cart" not in row[5] else "",
        "facts": facts,
        "parts": parts,
    }


def build() -> dict:
    bom = _bom_rows()
    return {
        "source": "make pcb-3d (scripts/export_site_pcbs.py), make gerbers",
        "glb_frame": "glTF as KiCad writes it: Y up, metres, KiCad board coordinates (x right, -y up)",
        "boards": [board(b, bom) for b in BOARDS],
    }
