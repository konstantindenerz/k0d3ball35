# SPDX-License-Identifier: MIT
"""docs/data/parts.json: every STL of the printed case and the trackball cradle, for the Case and
Trackball tabs.

Reads hardware/case/stl/*.stl and hardware/trackball-cradle/stl/*.stl (measured with trimesh:
bounding box, triangles, volume, watertightness), hardware/trackball-cradle/stack.json and
retention.json, and names the preview renders in hardware/case/preview and
hardware/trackball-cradle/preview. Names, roles and print notes are short summaries of
hardware/case/README.md, spec/11-case.md and hardware/trackball-cradle/README.md.

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
PLA_DENSITY = 1.24   # g/cm3

GROUPS = (
    ("right", "Right half"),
    ("left", "Left half"),
    ("test", "Test prints"),
    ("cradle", "Trackball cradle"),
    ("retainer", "Ball retainer"),
)

CASE_PRINT = "PETG or PLA, 0.2 mm layers, 3 perimeters, 20 % infill, no supports."
CRADLE_PRINT = "PETG or PLA, 0.12 mm layers, 3 perimeters, 30 % infill, no supports."

# stem -> group, name, role, printed (True = a part to print, False = display only), print notes
PARTS: dict[str, tuple[str, str, str, bool, str]] = {}


def _half(half: str) -> None:
    ball = " Carries the pocket for the trackball cradle." if half == "right" else ""
    window = " Carries the 16 mm ball window," if half == "right" else " Carries"
    PARTS[f"tray-{half}"] = (
        half, f"Tray, {half}",
        "The case body: angular walls on the stepped PCB outline, key floor 3 mm under the PCB, battery "
        "well, controller box walls, five standoffs for M2 heat-set inserts, four foot magnet pockets "
        f"from below.{ball}",
        True, f"{CASE_PRINT} Flat on the bed, cavities open upwards; the only bridges are the USB "
        "opening (11 mm), the switch slot, the LED window and the magnet pockets.")
    PARTS[f"box-cap-{half}"] = (
        half, f"Controller box cap, {half}",
        "Roof of the controller box: a 2 mm plate in the rebate plus an L-shaped skirt towards the keys "
        "and the thumb keys, held by two M2 screws in the corner bosses. The wordmark is engraved 0.6 mm "
        "into the plate.",
        True, f"{CASE_PRINT} Roof down (plate on the bed). A filament change at 0.6 mm gives a "
        "two-colour wordmark.")
    PARTS[f"lid-outer-{half}"] = (
        half, f"Lid, outer plate, {half}",
        f"The pinky-side half of the transport cover.{window} the four roof magnets and the even "
        "hinge knuckles; folded, it lies under the half as the tenting foot.",
        True, f"{CASE_PRINT} Roof down; the magnet pockets print as plain holes on a 0.6 mm skin. "
        "Joined to the inner plate by a 2 mm steel pin.")
    PARTS[f"lid-inner-{half}"] = (
        half, f"Lid, inner plate, {half}",
        "The controller and thumb-side half of the transport cover with the odd hinge knuckles; folded "
        "down beyond the inner edge it is the kickstand of the tenting foot.",
        True, f"{CASE_PRINT} Roof down. Joined to the outer plate by a 2 mm steel pin.")
    PARTS[f"lid-{half}"] = (
        half, f"Lid, closed pair, {half}",
        "Both lid plates closed on the tray, as held on top by the inner lip. One mesh of the two plates "
        "for the assembled and exploded views.",
        False, "Display only, do not print: print lid-outer and lid-inner instead.")
    PARTS[f"lid-folded-{half}"] = (
        half, f"Lid, folded as foot, {half}",
        "Both lid plates in the folded position under the tray, tilting the half by 18 degrees as a "
        "tenting foot.",
        False, "Display only, do not print: print lid-outer and lid-inner instead.")


for _h in ("right", "left"):
    _half(_h)

PARTS["pocket-test-right"] = (
    "test", "Pocket test, right",
    "The 50 x 50 mm corner of the right tray around the ball pocket, to check the fit of the cradle "
    "and the PCB notch before printing the whole tray.",
    True, "0.12 mm layers, otherwise as the tray. Print it with the cradle and a scrap PCB with the notch "
    "before the full tray.")

_CRADLE_NOTE = (f"{CRADLE_PRINT} Upright, housing down, open side on the bed. Press in three 2 mm ZrO2 "
                "bearing balls and deburr the rim.")
PARTS["cradle-19mm-pocket"] = (
    "cradle", "Cradle, 19.05 mm ball, pocket",
    "The r2 default: cup with three static ceramic bearings for a 19.05 mm ball and the housing for the "
    "PMW3610 sensor board, standing on the case floor in the pocket beside the right PCB.",
    True, _CRADLE_NOTE)
PARTS["cradle-25mm-pocket"] = (
    "cradle", "Cradle, 25 mm ball, pocket",
    "Fallback for a 25 mm ball in the same pocket. Needs a PCB notch apothem of 16.5 mm and a 35 mm "
    "pocket, i.e. a different PCB.",
    True, _CRADLE_NOTE)
PARTS["cradle-25mm-cutout"] = (
    "cradle", "Cradle, 25 mm ball, PCB cutout (r1)",
    "The r1 design: sits in a 30 mm round cutout of the PCB with a 40 mm flange under the board. Kept "
    "for reference.",
    True, _CRADLE_NOTE)
_RET_NOTE = ("PETG (the snap fingers bend 2.3 %, which PLA only just takes), 0.12 mm layers, upright as "
             "exported, no supports.")
PARTS["retainer-19mm"] = (
    "retainer", "Retainer, 19.05 mm ball",
    "Optional clip-on ring with two claws over the ball's shoulders, away from the thumb, so the ball "
    "stays in when the half is turned over. Snaps onto the cup rim and comes off by hand.",
    True, _RET_NOTE)
PARTS["retainer-25mm"] = (
    "retainer", "Retainer, 25 mm ball",
    "The same clip-on ring for the 25 mm cups (pocket and cutout variant).",
    True, _RET_NOTE)

# STLs in the two folders that the page does not list, with the reason
EXCLUDED: dict[str, str] = {}

# preview renders: path -> (caption, parts it shows)
PREVIEWS = {
    f"{CASE_PREVIEW}/assembly-right.png": ("Right half assembled", ("tray-right", "box-cap-right")),
    f"{CASE_PREVIEW}/assembly-left.png": ("Left half assembled", ("tray-left", "box-cap-left")),
    f"{CASE_PREVIEW}/section-right.png": ("Section through the ball, right half", ("tray-right", "pocket-test-right")),
    f"{CASE_PREVIEW}/tray-bottom-right.png": ("Tray from below, right", ("tray-right",)),
    f"{CASE_PREVIEW}/box-right.png": ("Controller box close-up, right", ("box-cap-right", "tray-right")),
    f"{CASE_PREVIEW}/cap-logo-right.png": ("Cap with the engraved wordmark", ("box-cap-right", "box-cap-left")),
    f"{CASE_PREVIEW}/lid-on-right.png": ("Lid on for transport, right", ("lid-right", "lid-outer-right", "lid-inner-right")),
    f"{CASE_PREVIEW}/lid-hinge-right.png": ("Lid hinge close-up, right", ("lid-right", "lid-outer-right", "lid-inner-right")),
    f"{CASE_PREVIEW}/lid-folded-right.png": ("Lid folded, right", ("lid-folded-right",)),
    f"{CASE_PREVIEW}/lid-foot-right.png": ("Lid as tenting foot, right", ("lid-folded-right",)),
    f"{CRADLE_PREVIEW}/assembly-19mm-pocket.png": ("Cradle assembled, 19.05 mm ball", ("cradle-19mm-pocket", "retainer-19mm")),
    f"{CRADLE_PREVIEW}/assembly-25mm-pocket.png": ("Cradle assembled, 25 mm ball", ("cradle-25mm-pocket", "retainer-25mm")),
    f"{CRADLE_PREVIEW}/section-19mm-pocket.png": ("Section, 19.05 mm ball, pocket", ("cradle-19mm-pocket",)),
    f"{CRADLE_PREVIEW}/section-25mm-cutout.png": ("Section, 25 mm ball, PCB cutout", ("cradle-25mm-cutout",)),
}

VARIANTS = (
    ("19mm-pocket", "19 mm pocket", "retainer-19mm"),
    ("25mm-pocket", "25 mm pocket", "retainer-25mm"),
    ("25mm-cutout", "25 mm cutout", "retainer-25mm"),
)
STACK_KEYS = ("ball_d", "ball_centre_z", "ball_top_above_pcb_top", "ball_bottom_z", "bearing_contact_z", "rim_z",
              "rim_below_equator", "lens_reference_plane_dist", "sensor_pcb_plane_z", "lowest_plastic_z", "floor_z",
              "cup_outer_d", "envelope_d_above_pcb", "notch_apothem", "housing_x", "housing_y", "footprint_x",
              "footprint_y", "retainer_top_z", "retainer_outer_d")
RETENTION_KEYS = ("trapped", "without_retainer_trapped", "guaranteed_margin", "ball_lift_play", "rest_gap",
                  "pull_off_min_gap", "open_sector_deg", "boss_clearance")


def _r(v, n=2):
    return None if v is None else round(float(v), n)


def measure(path) -> dict:
    import trimesh

    m = trimesh.load(path, force="mesh")
    lo, hi = m.bounds
    vol = abs(m.volume) / 1000.0
    import numpy as np

    _, uses = np.unique(m.edges_sorted, axis=0, return_counts=True)
    return {
        "bbox_min": [_r(v) for v in lo],
        "bbox_max": [_r(v) for v in hi],
        "size": [_r(b - a) for a, b in zip(lo, hi)],
        "triangles": int(len(m.faces)),
        "volume_cm3": _r(vol),
        "mass_g_solid": _r(vol * PLA_DENSITY, 1),
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
        group, name, role, printed, notes = PARTS[stem]
        parts.append({
            "id": stem, "path": stems[stem], "group": group, "name": name, "role": role,
            "printed": printed, "print_notes": notes,
            "previews": sorted(p for p, (_, shows) in PREVIEWS.items() if stem in shows),
            **measure(REPO / stems[stem]),
        })
    stack = json.loads((REPO / "hardware/trackball-cradle/stack.json").read_text())["variants"]
    retention = json.loads((REPO / "hardware/trackball-cradle/retention.json").read_text())["variants"]
    variants = []
    for vid, label, retainer in VARIANTS:
        s, r = stack[vid], retention.get(vid, {})
        previews = sorted(p for p in PREVIEWS if p.startswith(CRADLE_PREVIEW) and p.rsplit("/", 1)[1].endswith(f"{vid}.png"))
        variants.append({
            "id": vid, "label": label, "cradle": f"cradle-{vid}",
            "retainer": retainer if retainer in PARTS else None,
            "mount": "pocket" if s.get("mount_pocket") else "cutout",
            "stack": {k: _r(s[k], 3) for k in STACK_KEYS if k in s},
            "retention": {k: (_r(r[k], 3) if isinstance(r.get(k), float) else r.get(k)) for k in RETENTION_KEYS if k in r},
            "previews": previews,
        })
    return {
        "density_pla_g_cm3": PLA_DENSITY,
        "mass_note": "Mass of the solid mesh in PLA (1.24 g/cm3): an upper bound, a print with 20 to 30 % "
                     "infill weighs much less.",
        "groups": [{"id": g, "label": label} for g, label in GROUPS],
        "parts": parts,
        "excluded": dict(sorted(EXCLUDED.items())),
        "previews": [{"path": p, "caption": c, "parts": sorted(s)} for p, (c, s) in sorted(PREVIEWS.items())],
        "trackball": {
            "default": VARIANTS[0][0],
            "variants": variants,
        },
    }
