# SPDX-License-Identifier: MIT
"""docs/data/site.json: what every tab shares (name, revision, repository, the tab list), plus
the few facts, the status line and the document links the overview prints.

The page does not repeat the markdown: the overview names what the keyboard is and links to the
documents in the repository for everything else.

Every fact is read from its source file and names it: the layout points per half, the layout
yaml, the case stack file, the shield, the requirements table of spec/01-design-spec.md. Numbers stay numbers next to the display text so
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
        ("pcbs", "PCBs"), ("keymap", "Keymap"))

POINTS = "hardware/layout/output/points-{half}.json"
LAYOUT = "hardware/layout/k0d3ball35.yaml"
CASE_STACK = "hardware/case/stack.json"
RIGHT_OVERLAY = "firmware/zmk-config/config/boards/shields/k0d3ball35/k0d3ball35_right.overlay"
DESIGN = "spec/01-design-spec.md"
BOM = "spec/03-bom.md"
ORDER_TICKET = "issues/hw-jlcpcb-order-r1.md"

# the documents the overview links to: path, title, what is in it (the page does not repeat them)
DOCS = (
    ("README.md", "README", "What the project is, the repository map, the make targets."),
    ("spec/01-design-spec.md", "Design spec", "Requirements and the decisions behind them."),
    (BOM, "Bill of materials", "Every part with source and price."),
    ("spec/12-order-checklist.md", "Order checklist", "Shop by shop, what is bought and what is not."),
    ("spec/04-build-guide.md", "Build guide", "Tools, soldering order, assembly, checks."),
    ("spec/05-firmware.md", "Firmware", "ZMK build, flashing, pairing, trackball tuning."),
    ("spec/09-roadmap.md", "Roadmap", "What is done and what comes before the first order."),
    ("issues/README.md", "Issues", "Open tickets by priority."),
)


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


def facts() -> list[dict]:
    pts = {h: json.loads((REPO / POINTS.format(half=h)).read_text()) for h in ("left", "right")}
    cfg = yaml.safe_load((REPO / LAYOUT).read_text())
    case = json.loads((REPO / CASE_STACK).read_text())["variants"]
    overlay = (REPO / RIGHT_OVERLAY).read_text()
    req = requirements()

    n = {h: len(p["keys"]) for h, p in pts.items()}
    thumbs = {h: sum(1 for k in p["keys"] if k["kind"] == "thumb") for h, p in pts.items()}
    tb = pts["right"]["trackball"]
    sensor = re.search(r'compatible\s*=\s*"pixart,(\w+)"', overlay)[1].upper()
    cpi = int(re.search(r"res-cpi\s*=\s*<(\d+)>", overlay)[1])
    bat = pts["right"]["battery"]
    b = pts["right"]["bounds"]
    rc = case["right"]
    case_h = rc["box_top_z"] - rc["base_z"]
    switch = req["Switches"]

    return [
        {"id": "keys", "label": "Keys", "value": n["left"] + n["right"], "left": n["left"], "right": n["right"],
         "text": f"{n['left'] + n['right']}: left {n['left']} ({thumbs['left']} thumb), right {n['right']} ({thumbs['right']} thumb), "
                 f"{_num(cfg['pitch']['x'])} x {_num(cfg['pitch']['y'])} mm pitch",
         "pitch": [cfg["pitch"]["x"], cfg["pitch"]["y"]], "source": POINTS.format(half="right")},
        {"id": "switch", "label": "Switches", "text": switch.split(";")[0], "source": DESIGN},
        {"id": "ball", "label": "Trackball", "value": tb["ball_diameter"], "sensor": sensor, "cpi": cpi,
         "text": f"{_num(tb['ball_diameter'])} mm ball on the right half, {sensor} sensor",
         "source": POINTS.format(half="right")},
        {"id": "controller", "label": "Controller",
         "text": f"{req['Wireless'].split(',')[0]}, Bluetooth split, ZMK", "source": DESIGN},
        {"id": "battery", "label": "Battery", "cell": bat["cell"], "value": bat["capacity_mah"],
         "text": f"{bat['capacity_mah']} mAh LiPo per half", "source": POINTS.format(half="right")},
        {"id": "half", "label": "Size per half", "x": round(b["width"], 1), "y": round(b["height"], 1), "z": round(case_h, 1),
         "text": f"{round(b['width'])} x {round(b['height'])} mm, {_num(case_h)} mm high with the case",
         "source": POINTS.format(half="right")},
    ]


def _frontmatter(path: str) -> dict[str, str]:
    head = (REPO / path).read_text().split("---", 2)[1]
    return dict(line.split(": ", 1) for line in head.strip().splitlines() if ": " in line)


def status() -> dict:
    """One line for the overview: built or not. The PCB order ticket decides; the roadmap has the rest."""
    order = _frontmatter(ORDER_TICKET)["status"]
    total = re.search(r"^\| \*\*Total\*\* \| \*\*(.+?)\*\* \|$", (REPO / BOM).read_text(), flags=re.M)[1]
    return {"pcbs_ordered": order == "done", "order_ticket": ORDER_TICKET, "cost": total}


def build() -> dict:
    right = json.loads((REPO / POINTS.format(half="right")).read_text())
    return {
        "name": right["name"],
        "revision": right["revision"],
        "github": GITHUB,
        "ref": "main",
        "tabs": [{"id": i, "title": t} for i, t in TABS],
        "facts": facts(),
        "status": status(),
        "docs": [{"path": p, "title": t, "text": d} for p, t, d in DOCS],
    }
