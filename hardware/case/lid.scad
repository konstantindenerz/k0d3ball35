// k0d3ball35 printed case - hinged lid per half (transport cover and tenting foot)
// The skirt stands on the tray rim (rim_z) and follows the outer footprint including the
// pocket block; the roof clears the keycaps by lid_clear and the ball looks through a window
// smaller than itself. A 1 mm lip on the inside of the skirt reaches lid_lip_depth into the
// tray and holds the lid by friction, no magnets on top. The lid is split along x = hx into
// the outer and the inner plate, joined by a pin hinge whose knuckles are flush with the roof
// top. Under the half the lid is shifted by foot_dx so the hinge sits just outside the inner
// wall: the outer plate lies roof-up under the controller half (four magnets meet four in the
// floor) and the inner plate folds down by hinge_fold_deg as the kickstand; the half rests on
// its outer bottom edge and tilts by tent_deg with the inner edge up. Each plate's cut face
// below the axis leans outward by hinge_stop_deg (half the fold), so the two faces meet flat
// on flat at the fold and carry the load.

// The lid prints roof down, so the roof top is its first layer and gets the same broken edge
// as the tray floor.
module lid_body(top) {
    translate([0, 0, rim_z]) linear_extrude(top - rim_z - edge_chamfer + eps) outer_top_2d();
    chamfer_down(top, edge_chamfer) outer_top_2d();
}

module lid_cavity(top) {
    translate([0, 0, rim_z - 1]) linear_extrude(top - rim_z + 1) {
        pcb_cavity_2d();
        if (has_ball(half)) { pocket_cavity_2d(); translate(bc()) circle(r = clip_ro + 0.5, $fn = 128); }  // room for the clip
    }
}

// the tall controller box walls poke into the lid
module lid_box_notch() {
    if (controller_box) {
        translate([0, 0, rim_z - 1]) linear_extrude(box_top_z + lid_box_clear - rim_z + 1)
            offset(delta = pcb_clear + wall + lid_box_clear) box_2d();
        // the cap's screw heads stand on the box top and reach over its wall, into the skirt
        // (tests/test_assembly_interference.py found the lid resting on them)
        for (a = boss_axes()) translate([a[0], a[1], rim_z - 1])
            cylinder(d = cap_screw_head_d + 2 * lid_screw_clear, h = box_top_z + cap_screw_head_h + lid_box_clear - rim_z + 1, $fn = 48);
    }
}

// magnets in the roof of the outer plate, inserted from the roof underside; magnet_skin stays
// closed on top. foot_magnets is in the board frame (tray pockets), the lid is shifted by
// foot_dx as a foot
module lid_roof_magnets(under) {
    for (c = foot_magnets(half))
        translate([c[0] - foot_dx(half), c[1], under - 1]) cylinder(d = magnet_d, h = 1 + magnet_h + magnet_pocket_extra);
}

// ---------------------------------------------------------------- lip

// where the lip must not be: the controller box walls (plus their notch) and the pocket cup
module lip_clear_2d() {
    // the hinge cut leans by hinge_stop_deg below the axis and would shave a lip that crosses it
    // into a feather edge
    hc = (hinge_axis_z - lip_bottom_z) * tan(hinge_stop_deg) + 1;
    translate([hx - hc, -500]) square([2 * hc, 1000]);
    if (controller_box) offset(delta = pcb_clear + wall + lid_box_clear + 1) box_2d();
    if (has_ball(half)) {
        offset(delta = 1) pocket_cavity_2d();
        fpc_keepout_2d();
    }
}
// Where a lip may stand: the full-width ring minus the keycaps and their clearance. The lip
// goes down past the cap skirts when the lid is put on, so it must stay out of the caps in plan
// at every height. What is left thinner than lid_lip_min is dropped (it would not print).
module lip_zone_2d() offset(delta = lid_lip_min / 2) offset(delta = -lid_lip_min / 2) difference() {
    pcb_cavity_2d();
    offset(delta = -lid_fit - lid_lip_t) pcb_cavity_2d();
    lip_clear_2d();
    offset(delta = lid_cap_clear) caps_2d();
}
// ring between the inner wall face minus `inset` and the lip's inner face
module lip_2d(inset) intersection() {
    difference() {
        offset(delta = -inset) pcb_cavity_2d();
        offset(delta = -lid_fit - lid_lip_t) pcb_cavity_2d();
    }
    lip_zone_2d();
}

module lid_lip(under) {
    z0 = rim_z - lid_lip_depth;
    // inside the skirt the lip is part of the wall (no slit between lip and skirt)
    translate([0, 0, rim_z - eps]) linear_extrude(under - rim_z + 2 * eps) lip_2d(0);
    // below the rim it reaches into the tray with lid_fit to the wall
    translate([0, 0, z0 + lid_lip_chamfer - eps]) linear_extrude(lid_lip_depth - lid_lip_chamfer + 2 * eps) lip_2d(lid_fit);
    // stepped lead-in chamfer on the lower outer edge
    dz = lid_lip_chamfer / lid_lip_steps;
    for (i = [0 : lid_lip_steps - 1])
        translate([0, 0, z0 + i * dz]) linear_extrude(dz + eps)
            lip_2d(lid_fit + lid_lip_chamfer - i * dz);
}

// body (children) minus the cavity and the box notch, plus the lip, minus the roof magnets
module lid_shell(under) {
    difference() {
        union() {
            difference() { children(); lid_cavity(under); lid_box_notch(); }
            lid_lip(under);
        }
        lid_roof_magnets(under);
    }
}

// ---------------------------------------------------------------- hinge
// the roof thickened to hinge_knuckle_d along the hinge line, clipped to the lid footprint
module hinge_strip() {
    translate([0, 0, lid_top_z - hinge_knuckle_d]) linear_extrude(hinge_knuckle_d) intersection() {
        outer_top_2d();
        translate([hx - hinge_strip_w, -500]) square([2 * hinge_strip_w, 1000]);
    }
}

// the one-piece lid before the hinge cut: shell, strip and window
module lid_full() {
    difference() {
        union() { lid_shell(lid_roof_under_z) lid_body(lid_top_z); hinge_strip(); }
    }
}

// a prism along y from an (x, z) polygon
module xz_prism(p) rotate([90, 0, 0]) linear_extrude(1000, center = true) polygon(p);

// what the outer plate keeps: x > hx + hinge_gap / 2 above the axis, below it the face leans
// outward by hinge_stop_deg through the axis line (the stop face)
module keep_outer() {
    g = hinge_gap / 2;
    zt = lid_top_z + 10;
    zb = lip_bottom_z - 10;
    xz_prism([[hx + g, zt], [hx + g, hinge_axis_z - g / tan(hinge_stop_deg)],
              [hx + (hinge_axis_z - zb) * tan(hinge_stop_deg), zb], [hx + 500, zb], [hx + 500, zt]]);
}
module keep_inner() translate([hx, 0, 0]) mirror([1, 0, 0]) translate([-hx, 0, 0]) keep_outer();

// cylinders on the axis over the knuckles owned by `side`, radius r, every knuckle grown by
// `ext` at both ends and the two outermost ones by `end_ext` where they meet the skirt
module hinge_cylinders(side, r, ext = 0, end_ext = 0) {
    n = hinge_segments();
    for (i = [0 : n - 1])
        if (hinge_owner(i) == side) {
            e0 = ext + (i == 0 ? end_ext : 0);
            e1 = ext + (i == n - 1 ? end_ext : 0);
            translate([hx, hinge_seg_y0(i) - e0, hinge_axis_z]) rotate([-90, 0, 0])
                cylinder(r = r, h = hinge_seg() + e0 + e1);
        }
}
// the other plate's knuckles need a round groove plus the strip cleared next to the line, so
// no thin lips remain where the groove meets the strip's top and bottom faces
module hinge_grooves(side) {
    r = hinge_knuckle_d / 2 + hinge_clear;
    dir = side == "outer" ? 1 : -1;
    // the end knuckles run hinge_end_ext into the skirt, so their grooves must too (they used to
    // stop hinge_seg_gap past the span and the plates overlapped by 0.2 mm at both ends)
    n = hinge_segments();
    hinge_cylinders(side, r, hinge_seg_gap, hinge_end_ext);
    for (i = [0 : n - 1])
        if (hinge_owner(i) == side) {
            e0 = hinge_seg_gap + (i == 0 ? hinge_end_ext : 0);
            e1 = hinge_seg_gap + (i == n - 1 ? hinge_end_ext : 0);
            translate([hx + (dir > 0 ? -r : -10), hinge_seg_y0(i) - e0, lid_top_z - hinge_knuckle_d - 1])
                cube([10 + r, hinge_seg() + e0 + e1, hinge_knuckle_d + 2]);
        }
}
module hinge_pin_hole() {
    s = hinge_span();
    translate([hx, s[0] - 1, hinge_axis_z]) rotate([-90, 0, 0])
        cylinder(d = hinge_pin_d + hinge_pin_fit, h = hinge_len() + 1 - hinge_blind);
}
// own knuckles run hinge_end_ext past the span so their end faces never coincide with the skirt
hinge_end_ext = 0.5;
function other(side) = side == "outer" ? "inner" : "outer";

// A plate's footprint without tabs thinner than 0.6 mm. Where a stagger step of the outline
// lies within a knuckle radius of the hinge line, the other plate's end groove would cut such a
// tab loose and leave a stray sliver in the STL.
module plate_footprint_2d(side) offset(delta = 0.3) offset(delta = -0.3) intersection() {
    outer_top_2d();
    g = hinge_gap / 2;
    if (side == "outer") translate([hx + g, -500]) square([500, 1000]);
    else translate([hx - g - 500, -500]) square([500, 1000]);
}

module lid_plate(side) {
    difference() {
        union() {
            difference() {
                intersection() {
                    lid_full();
                    if (side == "outer") keep_outer(); else keep_inner();
                    translate([0, 0, lip_bottom_z - 1]) linear_extrude(lid_top_z - lip_bottom_z + 2) union() {
                        plate_footprint_2d(side);
                        offset(delta = -wall) outer_top_2d();     // everything inside the skirt (lip, roof)
                    }
                }
                hinge_grooves(other(side));
            }
            intersection() {
                hinge_cylinders(side, hinge_knuckle_d / 2, 0, hinge_end_ext);
                translate([0, 0, rim_z]) linear_extrude(lid_top_z - rim_z) outer_top_2d();
            }
        }
        hinge_pin_hole();
    }
}

// both plates closed: the transport cover
module lid() { lid_plate("outer"); lid_plate("inner"); }

// the inner plate rotated about the hinge axis, far end down for fold > 0
module fold_inner(fold) translate([hx, 0, hinge_axis_z]) rotate([0, -fold, 0]) translate([-hx, 0, -hinge_axis_z]) children();
module lid_folded(fold = hinge_fold_deg) { lid_plate("outer"); fold_inner(fold) lid_plate("inner"); }

// foot pose relative to the tray: the folded lid shifted by foot_dx, the outer plate roof-up
// against the tray underside under the controller half
module lid_under_tray() translate([foot_dx(half), 0, base_z - lid_top_z]) lid_folded();
// tray plus folded lid rotated by tent_deg about the tray's outer bottom edge, which stays on
// z = 0 (the desk); the kickstand's lip edge lands on the desk by construction of the fold
module on_desk() {
    px = foot_pivot_x();
    translate([px, 0, 0]) rotate([0, tent_deg, 0]) translate([-px, 0, -base_z]) children();
}

