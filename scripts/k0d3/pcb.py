# SPDX-License-Identifier: CERN-OHL-P-2.0
"""KiCad board generator for the k0d3ball36 main PCB (unrouted).

Writes a KiCad 8 format .kicad_pcb with all footprints placed and nets assigned, the
board outline, the trackball cutout, GND pours on both faces and silkscreen. Routing
is done afterwards (scripts/route.py) and the file is round-tripped through pcbnew so
the committed board is in the current KiCad format.
"""
from __future__ import annotations

import json
from pathlib import Path

from .footprints import all_footprints
from .geometry import Layout
from .netlist import HOLE_PIN_LEFT, HOLE_PIN_RIGHT, LIB, Component, net_classes, net_names
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
    nets = net_names(comps)
    net_index = {n: i + 1 for i, n in enumerate(nets)}
    fps = all_footprints(HOLE_PIN_RIGHT, HOLE_PIN_LEFT)
    out = [f"(kicad_pcb (version {PCB_VERSION}) (generator \"k0d3ball36\") (generator_version \"1.0\")",
           "  (general (thickness 1.6) (legacy_teardrops no))", "  (paper \"A3\")",
           f"  (title_block (title {quote(layout.cfg['name'] + ' main PCB')}) (date \"2026-11-05\") (rev {quote(layout.cfg['revision'])}) (company \"k0d3ball36 project\"))",
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
    # board outline
    pts = " ".join(f"(xy {num(ox + x)} {num(oy + y)})" for x, y in list(layout.outline.exterior.coords)[:-1])
    out.append(f"  (gr_poly (pts {pts}) (stroke (width 0.05) (type default)) (fill none) (layer \"Edge.Cuts\") (uuid {quote(uid('edge', 'outline'))}))")
    tb = layout.cfg["trackball"]
    bx, by = ox + layout.ball_center[0], oy + layout.ball_center[1]
    r = tb["pcb_cutout_diameter"] / 2
    out.append(f"  (gr_circle (center {num(bx)} {num(by)}) (end {num(bx + r)} {num(by)}) (stroke (width 0.05) (type default)) (fill none) (layer \"Edge.Cuts\") (uuid {quote(uid('edge', 'ball'))}))")
    # ball / cradle reference on the fab layers
    out.append(f"  (gr_circle (center {num(bx)} {num(by)}) (end {num(bx + tb['ball_diameter'] / 2)} {num(by)}) (stroke (width 0.1) (type dash)) (fill none) (layer \"F.Fab\") (uuid {quote(uid('fab', 'ball'))}))")
    out.append(f"  (gr_circle (center {num(bx)} {num(by)}) (end {num(bx + tb['cradle_diameter'] / 2)} {num(by)}) (stroke (width 0.1) (type dash)) (fill none) (layer \"F.Fab\") (uuid {quote(uid('fab', 'cradle'))}))")
    # silkscreen texts: between the controller footprint and the reset/battery row
    silk = layout.cfg["silkscreen"]
    c = layout.cfg["controller"]
    tx, ty = ox + c["center"]["x"], oy + c["center"]["y"] + 19.3
    for layer, side in (("F.SilkS", "RIGHT"), ("B.SilkS", "LEFT")):
        mirror = " (justify mirror)" if layer.startswith("B.") else ""
        for i, line in enumerate((f"{silk['title']} {silk['revision_text']}  CERN-OHL-P-2.0", f"{side} half - this side up")):
            out.append(f"  (gr_text {quote(line)} (at {num(tx)} {num(ty + i * 1.6)} 0) (layer {quote(layer)}) "
                       f"(uuid {quote(uid('silk', layer, i))}) (effects (font (size 0.8 0.8) (thickness 0.12)){mirror}))")
    # GND pours on both faces
    minx, miny, maxx, maxy = layout.outline.bounds
    zpts = f"(pts (xy {num(ox + minx - 1)} {num(oy + miny - 1)}) (xy {num(ox + maxx + 1)} {num(oy + miny - 1)}) (xy {num(ox + maxx + 1)} {num(oy + maxy + 1)}) (xy {num(ox + minx - 1)} {num(oy + maxy + 1)}))"
    for layer in ("F.Cu", "B.Cu"):
        out.append(f"  (zone (net {net_index['GND']}) (net_name \"GND\") (layer {quote(layer)}) (uuid {quote(uid('zone', layer))}) (name {quote('GND_' + layer)}) (hatch edge 0.5) (priority 0)"
                   f" (connect_pads (clearance 0.3)) (min_thickness 0.25) (filled_areas_thickness no)"
                   f" (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5) (island_removal_mode 1) (island_area_min 10)) (polygon {zpts}))")
    out.append(")")
    return "\n".join(out) + "\n"


def write_library(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, fp in all_footprints(HOLE_PIN_RIGHT, HOLE_PIN_LEFT).items():
        p = out_dir / f"{name}.kicad_mod"
        p.write_text(fp.library_sexpr(LIB))
        written.append(p)
    return written


def project_json(name: str, comps: list[Component]) -> str:
    classes = net_classes()
    power_nets = classes["Power"].pop("nets")
    pro = {
        "board": {
            "design_settings": {
                "defaults": {"board_outline_line_width": 0.05, "copper_line_width": 0.2, "silk_line_width": 0.12, "silk_text_size_h": 1.0, "silk_text_size_v": 1.0, "silk_text_thickness": 0.15},
                "rules": {
                    "min_clearance": 0.2, "min_connection": 0.2, "min_copper_edge_clearance": 0.3, "min_hole_clearance": 0.25,
                    "min_hole_to_hole": 0.25, "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1, "min_resolved_spokes": 2,
                    "min_silk_clearance": 0.0, "min_text_height": 0.6, "min_text_thickness": 0.08, "min_through_hole_diameter": 0.3,
                    "min_track_width": 0.2, "min_via_annular_width": 0.13, "min_via_diameter": 0.5, "solder_mask_clearance": 0.0,
                    "solder_mask_min_width": 0.0, "use_height_for_length_calcs": True,
                },
                "rule_severities": {"lib_footprint_issues": "ignore", "lib_footprint_mismatch": "warning", "silk_overlap": "warning",
                                    "silk_over_copper": "warning", "footprint_type_mismatch": "ignore", "copper_sliver": "warning",
                                    "courtyards_overlap": "warning", "pth_inside_courtyard": "warning", "footprints_on_back": "ignore"},
                "track_widths": [0.25, 0.4], "via_dimensions": [{"diameter": 0.6, "drill": 0.3}, {"diameter": 0.7, "drill": 0.35}],
            },
        },
        "meta": {"filename": f"{name}.kicad_pro", "version": 1},
        "net_settings": {
            "classes": [
                {"name": "Default", "clearance": classes["Default"]["clearance"], "track_width": classes["Default"]["track_width"],
                 "via_diameter": classes["Default"]["via_diameter"], "via_drill": classes["Default"]["via_drill"],
                 "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2, "microvia_diameter": 0.3, "microvia_drill": 0.1,
                 "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "bus_width": 12, "line_style": 0},
                {"name": "Power", "clearance": classes["Power"]["clearance"], "track_width": classes["Power"]["track_width"],
                 "via_diameter": classes["Power"]["via_diameter"], "via_drill": classes["Power"]["via_drill"],
                 "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2, "microvia_diameter": 0.3, "microvia_drill": 0.1,
                 "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "bus_width": 12, "line_style": 0},
            ],
            "meta": {"version": 3},
            "netclass_assignments": {n: "Power" for n in power_nets},
            "netclass_patterns": [{"netclass": "Power", "pattern": n} for n in power_nets],
        },
        "pcbnew": {"page_layout_descr_file": ""},
        "schematic": {"drawing": {"default_line_thickness": 6.0, "default_text_size": 50.0, "pin_symbol_size": 25.0},
                      "legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": [[uid("sheet", "root"), "Root"]],
        "text_variables": {},
    }
    return json.dumps(pro, indent=2) + "\n"
