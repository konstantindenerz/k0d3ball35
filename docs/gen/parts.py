# SPDX-License-Identifier: MIT
"""docs/data/parts.json: every STL of the printed case and the trackball cradle, for the Case and
Trackball tabs.

Reads hardware/case/stl/*.stl and hardware/trackball-cradle/stl/*.stl (measured with trimesh:
bounding box, triangles, watertightness), hardware/trackball-cradle/stack.json and
retention.json, and names the preview renders in hardware/case/preview and
hardware/trackball-cradle/preview. Each part gets a name and one line; how to print and fit it
stays in hardware/case/README.md and hardware/trackball-cradle/README.md, which the page links.

Every STL in the two folders has an entry in PARTS or in EXCLUDED (with the reason), otherwise
build() fails, so a new part cannot silently stay off the page.
"""
from __future__ import annotations

import json

from . import REPO

CASE_STL = "hardware/case/stl"
CRADLE_STL = "hardware/trackball-cradle/stl"
CASE_PREVIEW = "hardware/case/preview"
CRADLE_PREVIEW = "hardware/trackball-cradle/preview"

GROUPS = (
    ("right", "Right half"),
    ("left", "Left half"),
    ("test", "Test prints"),
    ("cradle", "Trackball cradle"),
    ("retainer", "Ball retainer"),
)

# where the details live: the page names a part, the README says how to print and fit it
DOCS = {"right": "hardware/case/README.md", "left": "hardware/case/README.md", "test": "hardware/case/README.md",
        "cradle": "hardware/trackball-cradle/README.md", "retainer": "hardware/case/README.md"}

# stem -> group, name, one line on what it is, printed (True = a part to print, False = display only)
PARTS: dict[str, tuple[str, str, str, bool]] = {}


def _half(half: str) -> None:
    PARTS[f"tray-{half}"] = (half, f"Tray, {half}", "The case body the PCB sits in"
                             + (", with the pocket for the trackball cradle." if half == "right" else "."), True)
    PARTS[f"guard-{half}"] = (half, f"PCB guard, {half}", "0.8 mm plate on the PCB between the switches, under the keycaps. Adds no height.", True)
    PARTS[f"box-cap-{half}"] = (half, f"Controller box cap, {half}", "Screwed roof over the controller, with the engraved wordmark.", True)
    PARTS[f"lid-outer-{half}"] = (half, f"Lid, outer plate, {half}", "Pinky-side half of the hinged lid.", True)
    PARTS[f"lid-inner-{half}"] = (half, f"Lid, inner plate, {half}", "Thumb-side half of the hinged lid.", True)
    PARTS[f"lid-{half}"] = (half, f"Lid, closed, {half}", "Both lid plates closed over the keys for transport.", False)
    PARTS[f"lid-folded-{half}"] = (half, f"Lid, folded as foot, {half}", "Both lid plates folded under the half as a tenting foot.", False)


for _h in ("right", "left"):
    _half(_h)

PARTS["pocket-cover-right"] = ("right", "Pocket cover, right", "Flush plate over the cradle opening, with the funnel down to the ball. Two M2 x 6 countersunk screws.", True)
PARTS["pocket-test-right"] = ("test", "Pocket test, right", "The corner of the right tray around the ball pocket, to test the cradle fit.", True)
PARTS["cradle-19mm-pocket"] = ("cradle", "Cradle, 19.05 mm ball", "Cup on three ceramic bearings, with the tilted sensor module sleeve beside it. The only variant since r2.4.", True)
PARTS["pocket-clip-right"] = ("retainer", "Retainer clip, right", "Optional clip on the pocket cover that keeps the ball in when the half is turned over.", True)

# STLs in the two folders that the page does not list, with the reason
EXCLUDED: dict[str, str] = {}
# not a print part and not in the part list: the bought sensor module's envelope where it sits
SENSOR_REF = "hardware/trackball-cradle/ref/sensor-module.stl"

# preview renders: path -> (caption, parts it shows)
PREVIEWS = {
    f"{CASE_PREVIEW}/assembly-right.png": ("Right half assembled", ("tray-right", "box-cap-right", "pocket-cover-right")),
    f"{CASE_PREVIEW}/assembly-left.png": ("Left half assembled", ("tray-left", "box-cap-left")),
    f"{CASE_PREVIEW}/section-right.png": ("Section through the ball, right half", ("tray-right", "pocket-test-right")),
    f"{CASE_PREVIEW}/tray-bottom-right.png": ("Tray from below, right", ("tray-right",)),
    f"{CASE_PREVIEW}/box-right.png": ("Controller box close-up, right", ("box-cap-right", "tray-right")),
    f"{CASE_PREVIEW}/cap-logo-right.png": ("Cap with the engraved wordmark", ("box-cap-right", "box-cap-left")),
    f"{CASE_PREVIEW}/clip-right.png": ("Retainer clip on the pocket cover", ("pocket-clip-right", "pocket-cover-right")),
    f"{CASE_PREVIEW}/lid-on-right.png": ("Lid on for transport, right", ("lid-right", "lid-outer-right", "lid-inner-right")),
    f"{CASE_PREVIEW}/lid-hinge-right.png": ("Lid hinge close-up, right", ("lid-right", "lid-outer-right", "lid-inner-right")),
    f"{CASE_PREVIEW}/lid-folded-right.png": ("Lid folded, right", ("lid-folded-right",)),
    f"{CASE_PREVIEW}/lid-foot-right.png": ("Lid as tenting foot, right", ("lid-folded-right",)),
    f"{CRADLE_PREVIEW}/assembly-19mm-pocket.png": ("Cradle assembled, 19.05 mm ball", ("cradle-19mm-pocket",)),
    f"{CRADLE_PREVIEW}/section-19mm-pocket.png": ("Section, 19.05 mm ball, pocket", ("cradle-19mm-pocket",)),
}

VARIANTS = (
    ("19mm-pocket", "19 mm pocket", "pocket-clip-right"),
)
STACK_KEYS = ("ball_d", "ball_centre_z", "ball_top_above_pcb_top", "ball_bottom_z", "bearing_contact_z", "rim_z",
              "rim_below_equator", "lens_reference_plane_dist", "sensor_pcb_plane_z", "lowest_plastic_z", "floor_z",
              "cup_outer_d", "envelope_d_above_pcb", "notch_apothem", "housing_x", "housing_y", "footprint_x",
              "footprint_y")
RETENTION_KEYS = ("trapped", "without_clip_trapped", "guaranteed_margin", "ball_lift_play", "rest_gap",
                  "pull_off_min_gap", "open_sector_deg", "pin_cradle_clearance", "clip_top_z", "clip_outer_r")


def _r(v, n=2):
    return None if v is None else round(float(v), n)


def measure(path) -> dict:
    import trimesh

    m = trimesh.load(path, force="mesh")
    lo, hi = m.bounds
    import numpy as np

    _, uses = np.unique(m.edges_sorted, axis=0, return_counts=True)
    return {
        "bbox_min": [_r(v) for v in lo],
        "bbox_max": [_r(v) for v in hi],
        "size": [_r(b - a) for a, b in zip(lo, hi)],
        "triangles": int(len(m.faces)),
        "watertight": bool(m.is_watertight),
        # edges shared by more than two faces: two surfaces touching along a line (closed, but not
        # strictly manifold); slicers take that, the volume stays valid
        "non_manifold_edges": int((uses > 2).sum()),
    }


def _stls() -> list[str]:
    return sorted(str(p.relative_to(REPO)) for d in (CASE_STL, CRADLE_STL) for p in (REPO / d).glob("*.stl"))


def build() -> dict:
    files = _stls()
    stems = {p.rsplit("/", 1)[1][:-4]: p for p in files}
    unknown = sorted(set(stems) - set(PARTS) - set(EXCLUDED))
    missing = sorted(set(PARTS) - set(stems))
    if unknown or missing:
        raise SystemExit(f"parts.py: STLs without an entry {unknown}, entries without an STL {missing}")
    group_order = [g for g, _ in GROUPS]
    parts = []
    for stem in sorted(PARTS, key=lambda s: (group_order.index(PARTS[s][0]), list(PARTS).index(s))):
        group, name, role, printed = PARTS[stem]
        parts.append({
            "id": stem, "path": stems[stem], "group": group, "name": name, "role": role,
            "printed": printed, "doc": DOCS[group],
            "previews": sorted(p for p, (_, shows) in PREVIEWS.items() if stem in shows),
            **measure(REPO / stems[stem]),
        })
    stack = json.loads((REPO / "hardware/trackball-cradle/stack.json").read_text())["variants"]
    retention = json.loads((REPO / "hardware/case/retention.json").read_text())["variants"]
    variants = []
    for vid, label, retainer in VARIANTS:
        s, r = stack[vid], retention.get(vid, {})
        previews = sorted(p for p in PREVIEWS if p.startswith(CRADLE_PREVIEW) and p.rsplit("/", 1)[1].endswith(f"{vid}.png"))
        variants.append({
            "id": vid, "label": label, "cradle": f"cradle-{vid}",
            "retainer": retainer if retainer in PARTS else None,
            "sensor": SENSOR_REF,
            "mount": "pocket" if s.get("mount_pocket") else "cutout",
            "stack": {k: _r(s[k], 3) for k in STACK_KEYS if k in s},
            "retention": {k: (_r(r[k], 3) if isinstance(r.get(k), float) else r.get(k)) for k in RETENTION_KEYS if k in r},
            "previews": previews,
        })
    return {
        "groups": [{"id": g, "label": label} for g, label in GROUPS],
        "parts": parts,
        "excluded": dict(sorted(EXCLUDED.items())),
        "previews": [{"path": p, "caption": c, "parts": sorted(s)} for p, (c, s) in sorted(PREVIEWS.items())],
        "trackball": {
            "default": VARIANTS[0][0],
            "variants": variants,
        },
    }
