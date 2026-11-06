# SPDX-License-Identifier: CERN-OHL-P-2.0
"""KiCad board generator for the k0d3ball35 main PCBs (unrouted, one per half).

Writes a KiCad 8 format .kicad_pcb with all footprints placed and nets assigned, the
board outline (with the ball pocket notch on the right), GND pours on both faces and
silkscreen. Components arrive in board coordinates (netlist.build_components); every
value taken from the layout frame directly (outline, silkscreen, keep-out, vias, hand
routes) goes through `layout.to_board`, which mirrors x on the left half. The case pocket
and the ball are drawn on User.Comments for reference. Routing is done afterwards (scripts/route.py) and the file is round-tripped through pcbnew so
the committed board is in the current KiCad format.
"""
from __future__ import annotations

import json
from pathlib import Path

from .footprints import all_footprints
from .geometry import Layout
from .netlist import HOLE_PIN, LIB, Component, net_classes, net_names
from .schematic import sym_uuid
from .sexpr import num, quote, uid

PCB_VERSION = "20240108"
OFFSET = (120.0, 60.0)   # sheet position of the layout origin

LAYERS = [(0, "F.Cu", "signal"), (31, "B.Cu", "signal"), (32, "B.Adhes", "user", "B.Adhesive"), (33, "F.Adhes", "user", "F.Adhesive"),
          (34, "B.Paste", "user"), (35, "F.Paste", "user"), (36, "B.SilkS", "user", "B.Silkscreen"), (37, "F.SilkS", "user", "F.Silkscreen"),
          (38, "B.Mask", "user"), (39, "F.Mask", "user"), (40, "Dwgs.User", "user", "User.Drawings"), (41, "Cmts.User", "user", "User.Comments"),
          (42, "Eco1.User", "user", "User.Eco1"), (43, "Eco2.User", "user", "User.Eco2"), (44, "Edge.Cuts", "user"), (45, "Margin", "user"),
          (46, "B.CrtYd", "user", "B.Courtyard"), (47, "F.CrtYd", "user", "F.Courtyard"), (48, "B.Fab", "user"), (49, "F.Fab", "user")]


def build_pcb(layout: Layout, comps: list[Component], sheetfile: str) -> str:
    ox, oy = OFFSET

    def P(x: float, y: float) -> tuple[float, float]:
        """Layout-frame point -> page coordinates (mirrored on the left, plus the page offset)."""
        bx, by = layout.to_board(x, y)
        return (ox + bx, oy + by)

    def pts_sexpr(coords) -> str:
        return " ".join("(xy {} {})".format(*map(num, P(x, y))) for x, y in coords)
    nets = net_names(comps)
    net_index = {n: i + 1 for i, n in enumerate(nets)}
    fps = all_footprints(HOLE_PIN)
    out = [f"(kicad_pcb (version {PCB_VERSION}) (generator \"k0d3ball35\") (generator_version \"1.0\")",
           "  (general (thickness 1.6) (legacy_teardrops no))", "  (paper \"A3\")",
           f"  (title_block (title {quote(layout.cfg['name'] + ' ' + layout.half + ' half')}) (date \"2026-11-06\") (rev {quote(layout.cfg['revision'])}) (company \"k0d3ball35 project\"))",
           "  (layers"]
    for l in LAYERS:
        extra = f" {quote(l[3])}" if len(l) > 3 else ""
        out.append(f"    ({l[0]} {quote(l[1])} {l[2]}{extra})")
    out += ["  )",
            "  (setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no)",
            "    (pcbplotparams (layerselection 0x00010fc_ffffffff) (plot_on_all_layers_selection 0x0000000_00000000) (disableapertmacros no) (usegerberextensions yes)",
            "      (usegerberattributes yes) (usegerberadvancedattributes yes) (creategerberjobfile yes) (dashed_line_dash_ratio 12) (dashed_line_gap_ratio 3)",
            "      (svgprecision 4) (plotframeref no) (viasonmask no) (mode 1) (useauxorigin no) (hpglpennumber 1) (hpglpenspeed 20) (hpglpendiameter 15)",
            "      (pdf_front_fp_property_popups yes) (pdf_back_fp_property_popups yes) (dxfpolygonmode yes) (dxfimperialunits yes) (dxfusepcbnewfont yes)",
            "      (psnegative no) (psa4output no) (plotreference yes) (plotvalue yes) (plotfptext yes) (plotinvisibletext no) (sketchpadsonfab no)",
            "      (subtractmaskfromsilk yes) (outputformat 1) (mirror no) (drillshape 0) (scaleselection 1) (outputdirectory \"gerbers/\"))",
            "  )",
            "  (net 0 \"\")"]
    out += [f"  (net {i} {quote(n)})" for n, i in net_index.items()]
    # footprints
    for c in comps:
        fp = fps[c.footprint]
        padnets = {pad: (net_index[n], n) for pad, n in c.pads.items() if n}
        out.append(fp.board_sexpr(LIB, c.ref, c.value, ox + c.x, oy + c.y, c.rotation, padnets, sym_uuid(c.ref), sheetfile, c.description))
    # Fixed stubs: front and back socket pad of pin 1 -> plated joiner pad (per switch)
    import math as _m
    for c in comps:
        if c.kind != "switch":
            continue
        th = _m.radians(c.rotation)
        def rot(px, py):
            return (ox + c.x + px * _m.cos(th) + py * _m.sin(th), oy + c.y - px * _m.sin(th) + py * _m.cos(th))
        joiner = rot(-2.2, -8.0)
        n = net_index[c.pads["1"]]
        def seg(a, b, layer):
            out.append(f"  (segment (locked yes) (start {num(a[0])} {num(a[1])}) (end {num(b[0])} {num(b[1])}) (width 0.25) (layer {quote(layer)}) (net {n}) (uuid {quote(uid('stub', c.ref, layer, a, b))}))")
        # back pad touches the joiner; front pad goes up and across above the boss hole
        seg(rot(-3.5, -6.45), joiner, "B.Cu")
        seg(rot(3.5, -6.45), rot(3.5, -8.0), "F.Cu")
        seg(rot(3.5, -8.0), joiner, "F.Cu")
    # Column buses on the back: a straight locked track through the joiner pads of the three
    # finger rows of each column (x - 2.6 keeps 0.37 mm from the diode pads and the holes).
    by_col = {}
    for c in comps:
        if c.kind == "switch" and c.extra["row"] < 3:
            by_col.setdefault(c.extra["col"], []).append(c)
    for col, keys in by_col.items():
        keys.sort(key=lambda k: k.y)
        x = ox + keys[0].x - 2.6
        y1, y2 = oy + keys[0].y - 8.0, oy + keys[-1].y - 8.0
        n = net_index[f"COL{col}"]
        out.append(f"  (segment (locked yes) (start {num(x)} {num(y1)}) (end {num(x)} {num(y2)}) (width 0.25) (layer \"B.Cu\") (net {n}) (uuid {quote(uid('bus', col))}))")
    # FPC connector: the 0.3 mm GND pad cannot be reached by the pour (its neighbours are
    # 0.2 mm away), so give pad 2 a short locked stub to a GND via. The front-face variant
    # is not mirrored, so its pad 2 sits at -x instead of +x.
    for c in comps:
        if c.kind != "fpc":
            continue
        th = _m.radians(c.rotation)
        def frot(px, py):
            return (ox + c.x + px * _m.cos(th) + py * _m.sin(th), oy + c.y - px * _m.sin(th) + py * _m.cos(th))
        g = net_index["GND"]
        top = c.extra.get("side") == "top"
        for layer, sign in ((("F.Cu", -1),) if top else (("B.Cu", 1),)):
            a, b = frot(sign * 0.75, -1.85), frot(sign * 0.75, -3.9)
            out.append(f"  (segment (locked yes) (start {num(a[0])} {num(a[1])}) (end {num(b[0])} {num(b[1])}) (width 0.25) (layer {quote(layer)}) (net {g}) (uuid {quote(uid('fpcgnd', c.ref, layer))}))")
            out.append(f"  (via (locked yes) (at {num(b[0])} {num(b[1])}) (size 0.6) (drill 0.3) (layers \"F.Cu\" \"B.Cu\") (net {g}) (uuid {quote(uid('fpcvia', c.ref, layer))}))")
    # Test pads have a copper disc on both faces; a via through the centre ties them together
    # so the router only has to reach one face.
    for c in comps:
        if c.kind == "testpoint":
            out.append(f"  (via (locked yes) (at {num(ox + c.x)} {num(oy + c.y)}) (size 0.6) (drill 0.3) (layers \"F.Cu\" \"B.Cu\") (net {net_index[c.pads['1']]}) (uuid {quote(uid('tpvia', c.ref))}))")
    # Hand-placed locked tracks from the layout file (thumb cluster)
    by_ref = {c.ref: c for c in comps}
    def resolve(pt):
        if not isinstance(pt, str):
            return P(pt[0], pt[1])
        ref, what = pt.split(":")
        c = by_ref[ref]
        th = _m.radians(c.rotation)
        def r(px, py):
            return (ox + c.x + px * _m.cos(th) + py * _m.sin(th), oy + c.y - px * _m.sin(th) + py * _m.cos(th))
        if what == "joiner":
            return r(-2.2, -8.0)
        if what == "pad2":                     # hot-swap socket pad 2, back face copy
            return r(8.5, -3.8)
        if what == "pad2f":                    # hot-swap socket pad 2, front face copy
            return r(-8.5, -3.8)
        if c.kind == "mcu":                    # controller hole number
            h = int(what)
            return r(-7.62 if h <= 12 else 7.62, -13.97 + ((h - 1) % 12) * 2.54)
        if what == "bus":                      # bottom end of the column bus at this key
            return (ox + c.x - 2.6, oy + c.y - 8.0)
        if c.kind == "diode":
            return r(-1.65 if what == "1" else 1.65, 0)
        raise ValueError(pt)
    for i, route in enumerate(layout.cfg.get("manual_routes", [])):
        pts = [resolve(p) for p in route["points"]]
        n = net_index[route["net"]]
        for key, pt in (("via_start", pts[0]), ("via_end", pts[-1])):
            if route.get(key):
                out.append(f"  (via (locked yes) (at {num(pt[0])} {num(pt[1])}) (size 0.6) (drill 0.3) (layers \"F.Cu\" \"B.Cu\") (net {n}) (uuid {quote(uid('manualvia', i, key))}))")
        for j, (a, b) in enumerate(zip(pts, pts[1:])):
            out.append(f"  (segment (locked yes) (start {num(a[0])} {num(a[1])}) (end {num(b[0])} {num(b[1])}) (width {num(route.get('width', 0.25))}) (layer {quote(route['layer'])}) (net {n}) (uuid {quote(uid('manual', i, j))}))")
    # board outline
    pts = pts_sexpr(list(layout.outline.exterior.coords)[:-1])
    out.append(f"  (gr_poly (pts {pts}) (stroke (width 0.05) (type default)) (fill none) (layer \"Edge.Cuts\") (uuid {quote(uid('edge', 'outline'))}))")
    # ball pocket reference (case wall and ball) on User.Comments; the PCB itself only has the notch
    if layout.has_ball:
        tb = layout.cfg["trackball"]
        bx, by = P(*layout.ball_center)
        out.append(f"  (gr_circle (center {num(bx)} {num(by)}) (end {num(bx + tb['ball_diameter'] / 2)} {num(by)}) (stroke (width 0.1) (type dash)) (fill none) (layer \"Cmts.User\") (uuid {quote(uid('cmts', 'ball'))}))")
        ppts = pts_sexpr(list(layout.pocket_polygon().exterior.coords)[:-1])
        out.append(f"  (gr_poly (pts {ppts}) (stroke (width 0.1) (type dash)) (fill none) (layer \"Cmts.User\") (uuid {quote(uid('cmts', 'pocket'))}))")
        out.append(f"  (gr_text \"ball pocket (case)\" (at {num(bx)} {num(by + tb['cradle_diameter'] / 2 + 3.5)} 0) (layer \"Cmts.User\") "
                   f"(uuid {quote(uid('cmts', 'label'))}) (effects (font (size 1.0 1.0) (thickness 0.15))))")
    # battery bay on the back silkscreen: the cell lies under the PCB here, in the case well
    bat = layout.cfg["battery"]
    bay = layout.battery_bay()
    bpts = pts_sexpr(list(bay.exterior.coords)[:-1])
    out.append(f"  (gr_poly (pts {bpts}) (stroke (width 0.15) (type dash)) (fill none) (layer \"B.SilkS\") (uuid {quote(uid('silk', 'bay'))}))")
    bminx, bminy, bmaxx, bmaxy = bay.bounds
    for i, line in enumerate((f"{bat['cell']} cell", f"{bat['capacity_mah']} mAh", f"leads {bat['leads']}")):   # short lines: they sit between the two hole rows
        btx, bty = P((bminx + bmaxx) / 2, bmaxy - 4.5 + i * 1.5)
        out.append(f"  (gr_text {quote(line)} (at {num(btx)} {num(bty)} 0) (layer \"B.SilkS\") "
                   f"(uuid {quote(uid('silk', 'B.SilkS', 'bay', i))}) (effects (font (size 0.8 0.8) (thickness 0.12)) (justify mirror)))")
    # silkscreen texts (front only): between the controller footprint and the reset/battery row
    silk = layout.cfg["silkscreen"]
    c = layout.cfg["controller"]
    tx, ty = P(c["center"]["x"] + 6.0, c["center"]["y"] + 19.0)   # inboard of the controller, above the reset/battery row
    for i, line in enumerate((f"{silk['title']} {silk['revision_text']}  CERN-OHL-P-2.0", f"{layout.half.upper()} half")):
        out.append(f"  (gr_text {quote(line)} (at {num(tx)} {num(ty + i * 1.6)} 0) (layer \"F.SilkS\") "
                   f"(uuid {quote(uid('silk', 'F.SilkS', i))}) (effects (font (size 0.8 0.8) (thickness 0.12))))")
    # Track/via keep-out ring along the board edge (including the pocket notch), so the
    # autorouter respects the 0.3 mm copper-to-edge clearance. A ring with a hole is written
    # as one simple polygon with a hairline slit (KiCad normalises it).
    def ring_polygon(outer, inner):
        ext = list(outer.exterior.coords)[:-1]
        inn = list(inner.exterior.coords)[:-1]
        # start the slit at the exterior vertex closest to an interior vertex
        best = min(((i, j, (ext[i][0]-inn[j][0])**2 + (ext[i][1]-inn[j][1])**2) for i in range(0, len(ext), max(1, len(ext)//60)) for j in range(0, len(inn), max(1, len(inn)//60))), key=lambda t: t[2])
        i, j = best[0], best[1]
        path = ext[i:] + ext[:i] + [ext[i]] + [inn[j]] + list(reversed(inn[:j] + [inn[j]] if False else (inn[j:] + inn[:j])))[::1][::-1][::-1]
        # ensure the interior is traversed in the opposite winding
        inner_path = inn[j:] + inn[:j]
        inner_path = inner_path[::-1]
        inner_path = inner_path[-1:] + inner_path[:-1]  # start at inn[j]
        path = ext[i:] + ext[:i] + [ext[i], inn[j]] + inner_path[1:] + [inn[j]]
        return path
    edge_ring = ring_polygon(layout.outline, layout.outline.buffer(-0.35, join_style=2))
    for name, poly in (("edge_keepout", edge_ring),):
        kpts = pts_sexpr(poly)
        out.append(f"  (zone (net 0) (net_name \"\") (layers \"F&B.Cu\") (uuid {quote(uid('zone', name))}) (name {quote(name)}) (hatch edge 0.5) (priority 10)"
                   f" (connect_pads (clearance 0)) (min_thickness 0.25) (filled_areas_thickness no)"
                   f" (keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour allowed) (footprints allowed))"
                   f" (fill (thermal_gap 0.5) (thermal_bridge_width 0.5)) (polygon (pts {kpts})))")
    # GND stitching vias so the two pours are tied together everywhere
    for i, (vx, vy) in enumerate(layout.cfg.get("stitching_vias", [])):
        vx, vy = P(vx, vy)
        out.append(f"  (via (locked yes) (at {num(vx)} {num(vy)}) (size 0.6) (drill 0.3) (layers \"F.Cu\" \"B.Cu\") (net {net_index['GND']}) (uuid {quote(uid('via', i))}))")
    # GND pours on both faces
    minx, miny, maxx, maxy = layout.outline.bounds
    zpts = "(pts " + pts_sexpr([(minx - 1, miny - 1), (maxx + 1, miny - 1), (maxx + 1, maxy + 1), (minx - 1, maxy + 1)]) + ")"
    for layer in ("F.Cu", "B.Cu"):
        out.append(f"  (zone (net {net_index['GND']}) (net_name \"GND\") (layer {quote(layer)}) (uuid {quote(uid('zone', layer))}) (name {quote('GND_' + layer)}) (hatch edge 0.5) (priority 0)"
                   f" (connect_pads (clearance 0.3)) (min_thickness 0.25) (filled_areas_thickness no)"
                   f" (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5) (island_removal_mode 0)) (polygon {zpts}))")
    out.append(")")
    return "\n".join(out) + "\n"


def write_library(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, fp in all_footprints(HOLE_PIN).items():
        p = out_dir / f"{name}.kicad_mod"
        p.write_text(fp.library_sexpr(LIB))
        written.append(p)
    return written


def project_json(name: str, comps: list[Component], half: str) -> str:
    classes = net_classes()
    assignments = {}
    class_list = []
    for name, c in classes.items():
        for n in c.get("nets", []):
            assignments[n] = name
        class_list.append({"name": name, "clearance": c["clearance"], "track_width": c["track_width"],
                           "via_diameter": c["via_diameter"], "via_drill": c["via_drill"],
                           "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2, "microvia_diameter": 0.3, "microvia_drill": 0.1,
                           "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "bus_width": 12, "line_style": 0})
    pro = {
        "board": {
            "design_settings": {
                "defaults": {"board_outline_line_width": 0.05, "copper_line_width": 0.2, "silk_line_width": 0.12, "silk_text_size_h": 1.0, "silk_text_size_v": 1.0, "silk_text_thickness": 0.15},
                "rules": {
                    "min_clearance": 0.127, "min_connection": 0.127, "min_copper_edge_clearance": 0.3, "min_hole_clearance": 0.25,
                    "min_hole_to_hole": 0.25, "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1, "min_resolved_spokes": 2,
                    "min_silk_clearance": 0.0, "min_text_height": 0.6, "min_text_thickness": 0.08, "min_through_hole_diameter": 0.3,
                    "min_track_width": 0.15, "min_via_annular_width": 0.1, "min_via_diameter": 0.5, "solder_mask_clearance": 0.0,
                    "solder_mask_min_width": 0.0, "use_height_for_length_calcs": True,
                },
                "rule_severities": {"lib_footprint_issues": "ignore", "lib_footprint_mismatch": "warning", "silk_overlap": "warning",
                                    "silk_over_copper": "warning", "footprint_type_mismatch": "ignore", "copper_sliver": "warning",
                                    "courtyards_overlap": "warning", "pth_inside_courtyard": "warning", "footprints_on_back": "ignore"},
                "track_widths": [0.15, 0.25, 0.4], "via_dimensions": [{"diameter": 0.6, "drill": 0.3}],
            },
        },
        "meta": {"filename": f"{name}.kicad_pro", "version": 1},
        "net_settings": {
            "classes": class_list,
            "meta": {"version": 3},
            "netclass_assignments": assignments,
            "netclass_patterns": [{"netclass": cls, "pattern": n} for n, cls in assignments.items()],
        },
        "pcbnew": {"page_layout_descr_file": ""},
        "schematic": {"drawing": {"default_line_thickness": 6.0, "default_text_size": 50.0, "pin_symbol_size": 25.0},
                      "legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": [[uid("sheet", "root", half), "Root"]],
        "text_variables": {},
    }
    return json.dumps(pro, indent=2) + "\n"
