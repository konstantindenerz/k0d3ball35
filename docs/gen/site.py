# SPDX-License-Identifier: MIT
"""docs/data/site.json: what every tab shares (name, revision, repository, the tab list), plus
the key facts and licences the overview prints.

Every fact is read from its source file and names it: the layout points per half, the layout
yaml, the cradle and case stack files, the shield, the west manifest, the requirements table of
spec/01-design-spec.md and the LICENSE files. Numbers stay numbers next to the display text so
the tests can compare them with the sources.
"""
from __future__ import annotations

import json
import re

import yaml

from . import REPO

GITHUB = "konstantindenerz/k0d3ball35"
# id, title in the tab bar; the order is the order of the sheets in the title block
TABS = (("overview", "Overview"), ("explorer", "Explorer"), ("case", "Case"), ("trackball", "Trackball"),
        ("pcbs", "PCBs"), ("keymap", "Keymap"), ("build", "Build & BOM"))

POINTS = "hardware/layout/output/points-{half}.json"
LAYOUT = "hardware/layout/k0d3ball35.yaml"
CRADLE_STACK = "hardware/trackball-cradle/stack.json"
CASE_STACK = "hardware/case/stack.json"
RIGHT_OVERLAY = "firmware/zmk-config/config/boards/shields/k0d3ball35/k0d3ball35_right.overlay"
ZMK_YML = "firmware/zmk-config/config/boards/shields/k0d3ball35/k0d3ball35.zmk.yml"
WEST = "firmware/zmk-config/config/west.yml"
DESIGN = "spec/01-design-spec.md"
BOM = "spec/03-bom.md"


def _num(v: float) -> str:
    """19.05 -> '19.05', 18.0 -> '18', 120.978 -> '121.0' (one decimal above 100)."""
    v = round(v, 2)
    return f"{v:g}"


def requirements() -> dict[str, str]:
    """| R2 | Switches | ... | rows of the design spec's requirements table, keyed by name."""
    text = (REPO / DESIGN).read_text()
    out = {}
    for m in re.finditer(r"^\| R\d+ \| ([^|]+) \| ([^|]+) \|$", text, flags=re.M):
        out[m[1].strip()] = m[2].strip().replace("`", "")
    return out


def licences() -> list[dict]:
    out = []
    for path, scope in (("LICENSE", "firmware, scripts, documentation"), ("LICENSE-HARDWARE", "hardware")):
        first = next(line.strip() for line in (REPO / path).read_text().splitlines() if line.strip())
        spdx = {"MIT License": "MIT", "CERN Open Hardware Licence Version 2 - Permissive": "CERN-OHL-P-2.0"}.get(first, first)
        out.append({"id": spdx, "name": first, "scope": scope, "path": path})
    return out


def facts() -> list[dict]:
    pts = {h: json.loads((REPO / POINTS.format(half=h)).read_text()) for h in ("left", "right")}
    cfg = yaml.safe_load((REPO / LAYOUT).read_text())
    cradle = json.loads((REPO / CRADLE_STACK).read_text())["variants"]["19mm-pocket"]
    case = json.loads((REPO / CASE_STACK).read_text())["variants"]
    overlay = (REPO / RIGHT_OVERLAY).read_text()
    zmk = yaml.safe_load((REPO / ZMK_YML).read_text())
    west = yaml.safe_load((REPO / WEST).read_text())
    req = requirements()

    n = {h: len(p["keys"]) for h, p in pts.items()}
    thumbs = {h: sum(1 for k in p["keys"] if k["kind"] == "thumb") for h, p in pts.items()}
    tb = pts["right"]["trackball"]
    sensor = re.search(r'compatible\s*=\s*"pixart,(\w+)"', overlay)[1].upper()
    cpi = int(re.search(r"res-cpi\s*=\s*<(\d+)>", overlay)[1])
    bat = pts["right"]["battery"]
    b = pts["right"]["bounds"]
    zmk_rev = next(p["revision"] for p in west["manifest"]["projects"] if p["name"] == "zmk")
    rc = case["right"]
    case_h = rc["box_top_z"] - rc["base_z"]
    switch = req["Switches"]
    from .bom import cost, parse_sections
    price = cost(parse_sections((REPO / BOM).read_text())[1])

    return [
        {"id": "keys", "label": "Keys", "value": n["left"] + n["right"], "left": n["left"], "right": n["right"],
         "text": f"{n['left'] + n['right']}: left {n['left']} ({n['left'] - thumbs['left']} + {thumbs['left']} thumb), "
                 f"right {n['right']} ({n['right'] - thumbs['right']} + {thumbs['right']} thumb)",
         "source": POINTS.format(half="right")},
        {"id": "switch", "label": "Switches", "text": switch, "source": DESIGN},
        {"id": "pitch", "label": "Key pitch", "x": cfg["pitch"]["x"], "y": cfg["pitch"]["y"],
         "text": f"{_num(cfg['pitch']['x'])} x {_num(cfg['pitch']['y'])} mm, Keyball39 column stagger and thumb arc",
         "source": LAYOUT},
        {"id": "ball", "label": "Trackball", "value": tb["ball_diameter"], "sensor": sensor, "cpi": cpi,
         "text": f"{_num(tb['ball_diameter'])} mm POM ball on the right half, {sensor} sensor at {cpi} CPI on a daughterboard",
         "source": POINTS.format(half="right")},
        {"id": "ball_top", "label": "Ball top above PCB", "value": cradle["ball_top_above_pcb_top"],
         "text": f"{_num(cradle['ball_top_above_pcb_top'])} mm", "source": CRADLE_STACK},
        {"id": "controller", "label": "Controller", "text": req["Wireless"], "source": DESIGN},
        {"id": "firmware", "label": "Firmware", "revision": zmk_rev, "features": zmk["features"],
         "text": f"ZMK, pinned to {zmk_rev[:7]}; keys, pointer, ZMK Studio" if "studio" in zmk["features"]
                 else f"ZMK, pinned to {zmk_rev[:7]}",
         "source": WEST},
        {"id": "battery", "label": "Battery", "cell": bat["cell"], "value": bat["capacity_mah"],
         "text": f"{bat['cell']} LiPo, {bat['capacity_mah']} mAh, one per half in a bay under the PCB",
         "source": POINTS.format(half="right")},
        {"id": "half", "label": "PCB per half", "x": round(b["width"], 1), "y": round(b["height"], 1),
         "text": f"{round(b['width'], 1)} x {round(b['height'], 1)} mm, two different boards (left, right) and a sensor board",
         "source": POINTS.format(half="right")},
        {"id": "case_height", "label": "Case height", "value": round(case_h, 1),
         "text": f"{_num(case_h)} mm from the tray bottom to the controller cap", "source": CASE_STACK},
        {"id": "cost", "label": "Parts cost", "value": price["total"],
         "text": f"{price['total_text']} for one keyboard, PCBs in batches of five included", "source": BOM},
    ]


def build() -> dict:
    right = json.loads((REPO / POINTS.format(half="right")).read_text())
    return {
        "name": right["name"],
        "revision": right["revision"],
        "github": GITHUB,
        "ref": "main",
        "tabs": [{"id": i, "title": t} for i, t in TABS],
        "facts": facts(),
        "licences": licences(),
    }
