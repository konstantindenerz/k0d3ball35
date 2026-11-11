// k0d3ball35 printed case - tray, controller box cap, test part and dummies

// ---------------------------------------------------------------- tray
module tray_body() {
    // bottom: the first print layer, so its outer edge is broken (params.scad edge_chamfer)
    translate([0, 0, base_z + edge_chamfer - eps]) linear_extrude(-pcb_t - base_z - edge_chamfer + 2 * eps) outer_2d();
    chamfer_up(base_z, edge_chamfer) outer_2d();
    // rim: the edge the hand touches and the lid skirt meets. Not under the controller box,
    // whose walls stand on the rim - a chamfer there would undercut them.
    translate([0, 0, -pcb_t]) linear_extrude(rim_z + pcb_t - rim_chamfer + eps) outer_top_2d();
    // the pocket wall stops at the cup rim, not at the general rim, so the thumb reaches the ball
    // at its equator. It is CUT here rather than built lower, because the wall is not the pocket
    // block: it is what `offset(delta = wall) pcb_cavity_2d()` leaves when it grows into the PCB
    // notch, and that reaches r 12.3 around the ball whatever the block does (r2.4).
    chamfer_down(rim_z, rim_chamfer) difference() {
        outer_top_2d();
        if (controller_box) offset(delta = pcb_clear + wall) box_2d();
    }
    if (controller_box)
        translate([0, 0, rim_z - rim_chamfer - eps]) linear_extrude(rim_chamfer + eps) intersection() {
            outer_top_2d();
            offset(delta = pcb_clear + wall) box_2d();
        }
    if (controller_box)
        translate([0, 0, rim_z - eps]) linear_extrude(box_top_z - rim_z + eps) box_walls_2d();
}

module standoffs() {
    for (hp = holes(half))
        translate([hp[0], hp[1], floor_z_key - eps]) cylinder(d = standoff_d, h = standoff_h + eps);
}

module screw_holes() {
    for (hp = holes(half))
        translate([hp[0], hp[1], -pcb_t - screw_hole_depth]) cylinder(d = screw_hole_d, h = screw_hole_depth + 1);
}

// foot magnets: pockets from below in the thick floor under the key area, north pole down
module magnet_pockets_bottom() {
    for (c = foot_magnets(half))
        translate([c[0], c[1], base_z - 1]) cylinder(d = magnet_d, h = 1 + magnet_h + magnet_pocket_extra);
}

module tray_cuts() {
    // cavity under the key area (hot-swap sockets and diodes) and the PCB itself
    translate([0, 0, floor_z_key]) linear_extrude(-pcb_t - floor_z_key + eps) pcb_cavity_2d();
    translate([0, 0, -pcb_t]) linear_extrude(rim_z + 1 + pcb_t) pcb_cavity_2d();
    // battery well: bay plus J3 and RB1 courtyards
    translate([0, 0, well_floor_z]) linear_extrude(-pcb_t - well_floor_z + eps) well_2d();
    if (has_ball(half)) {
        translate([0, 0, pocket_floor_z]) linear_extrude(-pcb_t - pocket_floor_z + eps) pocket_well_2d();
        // open over the cradle up to the cover, then the rebate the cover sits in
        translate([0, 0, -pcb_t - eps]) linear_extrude(cover_z0 + pcb_t + 2 * eps) pocket_opening_2d();
        translate([0, 0, cover_z0]) linear_extrude(rim_z - cover_z0 + 1) cover_rebate_2d();
        for (s = cover_screws(half))
            translate([s[0], s[1], cover_z0 - cover_screw_depth]) cylinder(d = cover_screw_pilot_d, h = cover_screw_depth + 1);
        // through hole plus a 90 degree countersink, so the flat-head screws sit below the underside
        for (s = case_screws(half)) {
            translate([s[0], s[1], base_z - 1]) cylinder(d = case_screw_d, h = (pocket_floor_z - base_z) + 2);
            translate([s[0], s[1], base_z - eps])
                cylinder(d1 = case_screw_cs_d + 2 * eps, d2 = case_screw_d, h = case_screw_cs_h + eps);
        }
    }
    screw_holes();
    if (controller_box) {
        r = box_r();
        cr = ctrl_rect(half);
        // USB-C opening in the top (-y) wall, up to the cap plate
        translate([usb_x() - usb_cut[0] / 2, box_y_in() - wall - 1, box_roof_under_z - usb_cut[1]])
            cube([usb_cut[0], wall + 2, usb_cut[1]]);
        // rebate for the cap plate on the tall walls
        translate([box_x_in() - box_rebate, box_y_in() - box_rebate, box_roof_under_z])
            cube([box_inner_x - box_x_in() + box_rebate + 1, r[3] - box_y_in() + box_rebate + 1, box_roof_t + 1]);
        // LED window in the inner (-x) wall near the USB end of the controller
        translate([box_x_in() - wall - 1, cr[1] + led_offset_y - led_window[0] / 2, led_z])
            cube([wall + 2, led_window[0], led_window[1]]);
    }
    // slide switch lever through the outer wall, directly under the PCB
    sw = switch(half);
    translate([box_x_in() - wall - 1, sw[1] - switch_slot[0] / 2, -pcb_t - switch_slot[1]])
        cube([wall + 2, switch_slot[0], switch_slot[1] + eps]);
    // reset pin hole through the floor of the well
    rs = reset(half);
    translate([rs[0], rs[1], base_z - 1]) cylinder(d = reset_hole_d, h = (well_floor_z - base_z) + 2);
    magnet_pockets_bottom();
    for (f = feet(half))
        translate([f[0], f[1], base_z - 1]) cylinder(d = foot_d, h = 1 + foot_recess);
    // wordmark engraved into the flat underside, cut upward so the grooves open to the bed
    if (logo_on_floor)
        logo_cut(logo_floor_pos, logo_floor_rot, logo_floor_cell, base_z + logo_depth, logo_depth);
}

// corner bosses for the cap screws: half in the wall, 3.5 mm into the box, 45 degree underside
module boss(axis, corner) {
    bh = boss_half();
    x0 = box_x_in() - wall;
    x1 = axis[0] + bh;
    y0 = corner ? box_y_in() - wall : axis[1] - bh;
    y1 = axis[1] + bh;
    z0 = box_skirt_gap;
    in = 0.5;                       // the chamfer starts inside the wall so the faces meet cleanly
    rise = x1 - box_x_in() + in;
    hull() {
        // the part inside the wall goes all the way down
        if (corner) translate([x0, y0, z0]) cube([box_x_in() - in - x0, box_y_in() - in - y0, eps]);
        else translate([x0, y0, z0]) cube([box_x_in() - in - x0, y1 - y0, eps]);
        translate([x0, y0, z0 + rise]) cube([x1 - x0, y1 - y0, box_roof_under_z - z0 - rise]);
    }
}

module bosses() {
    if (controller_box) {
        a = boss_axes();
        boss(a[0], true);
        boss(a[1], false);
    }
}

module boss_holes() {
    if (controller_box)
        for (a = boss_axes())
            translate([a[0], a[1], box_roof_under_z - screw_hole_depth]) cylinder(d = screw_hole_d, h = screw_hole_depth + 1);
}

// standoffs and bosses are added after the cavity cuts (they stand inside the cavities),
// then the screw holes are drilled
module tray() {
    difference() {
        union() {
            difference() { tray_body(); tray_cuts(); }
            standoffs();
            bosses();
        }
        screw_holes();
        boss_holes();
    }
}

// ---------------------------------------------------------------- controller box cap
// Roof plate in the rebate plus an L-shaped skirt (key side and thumb side) that stands on the
// PCB. Two M2 machine screws into the bosses. Prints roof-down.
module box_cap() {
    r = box_r();
    x0 = box_x_in() - box_rebate + box_fit;
    y0 = box_y_in() - box_rebate + box_fit;
    x1 = box_inner_x;
    y1 = r[3];
    ys = box_y_in() + box_fit;
    xs = boss_x_end() + box_fit;
    h = box_roof_under_z - box_skirt_z + eps;
    difference() {
        union() {
            translate([x0, y0, box_roof_under_z]) cube([x1 - x0, y1 - y0, box_roof_t]);
            translate([x1 - box_skirt_t, ys, box_skirt_z]) cube([box_skirt_t, y1 - ys, h]);
            translate([xs, y1 - box_skirt_t, box_skirt_z]) cube([x1 - xs, box_skirt_t, h]);
        }
        for (a = boss_axes())
            translate([a[0], a[1], box_roof_under_z - 1]) cylinder(d = 2.4, h = box_roof_t + 2);
        if (logo_on_cap) logo_cut(logo_cap_pos, 0, logo_cell, box_top_z, logo_depth);
    }
}

// ---------------------------------------------------------------- pocket cover
// Flush plate over the cradle opening: same top as the rim, reaching over the cup rim as a bezel
// that ends cover_ball_gap from the ball, two countersunk M2 at the user-side corners, two small
// holes for the optional clip's pins. Prints top down.
module pocket_cover() {
    c = bc();
    difference() {
        translate([0, 0, cover_z0]) linear_extrude(cover_t) cover_2d();
        translate([c[0], c[1], cover_z0 - eps]) {
            cylinder(d = cover_hole_d, h = cover_t + 2 * eps, $fn = 128);
            translate([0, 0, cover_t - cover_chamfer + eps])
                cylinder(d1 = cover_hole_d, d2 = cover_hole_d + 2 * cover_chamfer + 2 * eps, h = cover_chamfer + eps, $fn = 128);
        }
        // the two holes the optional clip's snap pins go through
        for (p = clip_pins()) translate([c[0] + p[0], c[1] + p[1], cover_z0 - 1]) cylinder(d = cover_pin_hole_d, h = cover_t + 2, $fn = 32);
        for (s = cover_screws(half)) {
            translate([s[0], s[1], cover_z0 - 1]) cylinder(d = cover_screw_d, h = cover_t + 2);
            translate([s[0], s[1], rim_z - (cover_screw_head_d - cover_screw_d) / 2 + eps])
                cylinder(d1 = cover_screw_d, d2 = cover_screw_head_d + 2 * eps, h = (cover_screw_head_d - cover_screw_d) / 2, $fn = 32);
        }
    }
}

// ---------------------------------------------------------------- retainer clip (optional)
// Ball-centred frame (the STL is exported like the cradle's, centred on the ball); the assembly
// places it with translate(bc()). See params.scad clip_* for what each part is for.

// the arc beyond +-clip_open_az, cut off so the thumb's approach stays open (less than 180 degrees
// wide, so the intersection of two half spaces)
module clip_open_sector() {
    intersection() {
        translate([0, 0, -50]) cylinder(r = clip_ro + 5, h = 100);
        rotate([0, 0, clip_open_az])  translate([-100, 0, -100])    cube([200, 200, 200]);
        rotate([0, 0, -clip_open_az]) translate([-100, -200, -100]) cube([200, 200, 200]);
    }
}

// A claw over the ball's shoulder: a shell whose inner face is the cup's sphere (clip_ball_gap
// from the ball), backed by a 45 degree taper from the ring's outer edge so it prints without
// support. Below the equator the inner face would continue as a cylinder (hull), so lifting the
// clip straight up only ever moves the claw away from the ball.
module clip_claw(az) {
    zc = ball_centre_z();
    intersection() {
        difference() {
            union() {
                translate([0, 0, zc]) sphere(r = clip_rin + clip_claw_t, $fn = 96);
                translate([0, 0, clip_z1 - eps])
                    cylinder(h = clip_ro - 0.3 - clip_rin, r1 = clip_ro - 0.3, r2 = clip_rin, $fn = 96);
            }
            hull() {
                translate([0, 0, zc]) sphere(r = clip_rin, $fn = 96);
                translate([0, 0, zc - 20]) cylinder(r = clip_rin, h = 20, $fn = 96);
            }
        }
        rotate([0, 0, az]) translate([0, -clip_claw_w / 2, clip_z0]) cube([clip_ro + 1, clip_claw_w, clip_top_z() - clip_z0]);
    }
}

// A pin's barb, as a wedge on one prong in the y-z plane (y outward from the slit): 45 degree
// lead-in at the tip, a short flat, the release face at clip_release degrees from horizontal up to
// the catch 0.05 mm under the cover. Its inner face runs well inside the pin and its tip starts
// 0.05 above the pin's, so none of its faces lies in one of the pin's.
function barb_z_top() = cover_z0 - 0.05;
function barb_z_bot() = barb_z_top() - clip_pin_barb * tan(clip_release) - 0.1 - clip_pin_barb;
module barb() {
    r0 = clip_pin_d / 2; r1 = r0 + clip_pin_barb; zb = barb_z_bot() + 0.05; yi = 0.6;
    rotate([90, 0, 90]) linear_extrude(height = 1.2, center = true)
        polygon([[yi, zb], [r0, zb], [r1, zb + clip_pin_barb],
                 [r1, barb_z_top() - clip_pin_barb * tan(clip_release)],
                 [r0, barb_z_top()], [yi, barb_z_top()]]);
}

// A split snap pin at the origin, local x radial: the slit lies in the x-z plane, so the two
// prongs spring towards each other tangentially and the barbs sit on the faces they move with.
module clip_pin() {
    difference() {
        union() {
            translate([0, 0, barb_z_bot()]) cylinder(d = clip_pin_d, h = clip_z0 - barb_z_bot() + eps, $fn = 32);
            barb();
            mirror([0, 1, 0]) barb();
        }
        // the slit runs up into the ring to 0.4 under its top, which is what makes the prongs long
        translate([-5, -clip_pin_slit / 2, barb_z_bot() - 1]) cube([10, clip_pin_slit, clip_z1 - 0.4 - barb_z_bot() + 1]);
    }
}

module pocket_clip() {
    difference() {
        union() {
            translate([0, 0, clip_z0]) difference() {
                cylinder(r = clip_ro, h = clip_ring_t, $fn = 128);
                translate([0, 0, -1]) cylinder(r = clip_ri, h = clip_ring_t + 2, $fn = 128);
            }
            for (s = [-1, 1]) clip_claw(s * clip_claw_az);
        }
        clip_open_sector();
        for (p = clip_pins()) translate([p[0], p[1], 0]) rotate([0, 0, atan2(p[1], p[0])])
            translate([-5, -clip_pin_slit / 2, barb_z_bot() - 1]) cube([10, clip_pin_slit, clip_z1 - 0.4 - barb_z_bot() + 1]);
    }
    for (p = clip_pins()) translate([p[0], p[1], 0]) rotate([0, 0, atan2(p[1], p[0])]) clip_pin();
}

// ---------------------------------------------------------------- PCB guard
// Lies on the PCB top between the switches, held down by the switch flanges (common.scad
// guard_2d). Prints flat; the DXF (part guard2d) is the same outline for a laser-cut sheet.
module guard() linear_extrude(guard_t) guard_2d();

// ---------------------------------------------------------------- pocket test print
module pocket_test() {
    c = bc();
    intersection() {
        tray();
        translate([c[0] - 25, c[1] - 25, base_z - 1]) cube([50, 50, rim_z - base_z + 2]);
    }
}

// ---------------------------------------------------------------- dummies for views
module pcb_dummy() {
    color("darkgreen") translate([0, 0, -pcb_t]) linear_extrude(pcb_t) pcb_2d();
    // what sits on the PCB top besides the switches: the five M2 heads (BOM max 3.5 mm) and J1
    color("silver") for (hp = holes(half)) translate([hp[0], hp[1], 0]) cylinder(d = 3.5, h = 1.3);
    if (has_ball(half)) {
        color("black") polygon_box(fpc_body(half), 2.0);
        color("gold") polygon_box(fpc_tails(half), 0.15);
    }
}
module polygon_box(p, h) linear_extrude(h) polygon(p);

module keys_dummy() {
    for (k = keys(half)) translate([k[0], k[1], 0]) rotate(-k[2]) {
        color("dimgray") translate([-6.9, -6.9, 0]) cube([13.8, 13.8, 5]);
        color("ivory") translate([-8.75, -8.25, 5]) cube([17.5, 16.5, cap_top_z - 5]);
    }
}

module controller_dummy() {
    cr = ctrl_rect(half);
    sh = 2.5;
    color("steelblue") translate([cr[0], cr[1], sh]) cube([cr[2] - cr[0], cr[3] - cr[1], 1.6]);
    color("silver") translate([usb_x() - 4.5, cr[1] - 0.6, ctrl_top_z - 3.26]) cube([9, 7.35, 3.26]);
}

module battery_dummy() {
    b = bay(half);
    color("gold") translate([(minx(b) + maxx(b)) / 2 - 10.25, (miny(b) + maxy(b)) / 2 - 18.75, well_floor_z]) cube([20.5, 37.5, 5.7]);
}

module ball_dummy() color("white") translate([bc()[0], bc()[1], ball_centre_z()]) sphere(d = ball_d);

// The printed cradle itself in the assembly views (its STL is in the print frame and centred on
// the ball: mirror y back to the layout frame and move it to the ball). Until the r2.4 fix this was
// a stand-in drawn from copied numbers, which drifted away from the real part.
module cradle_dummy()
    color("royalblue") translate([bc()[0], bc()[1], 0]) mirror([0, 1, 0])
        import("../trackball-cradle/stl/cradle-19mm-pocket.stl");
