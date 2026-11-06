// k0d3ball35 printed case - tray, controller box cap, test part and dummies

// ---------------------------------------------------------------- tray
module tray_body() {
    translate([0, 0, base_z]) linear_extrude(-pcb_t - base_z + eps) outer_2d();
    translate([0, 0, -pcb_t]) linear_extrude(rim_z + pcb_t) outer_top_2d();
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
        translate([0, 0, -pcb_t]) linear_extrude(box_top_z + 20) pocket_cavity_2d();
        translate([0, 0, pocket_floor_z]) linear_extrude(-pcb_t - pocket_floor_z + eps) ffc_channel_2d();
        for (s = case_screws(half)) {
            translate([s[0], s[1], base_z - 1]) cylinder(d = case_screw_d, h = floor_t + 2);
            translate([s[0], s[1], base_z - 1]) cylinder(d = case_screw_cb_d, h = 1 + case_screw_cb_h);
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
    translate([rs[0], rs[1], base_z - 1]) cylinder(d = reset_hole_d, h = well_floor_z - base_z + 2);
    magnet_pockets_bottom();
    for (f = feet(half))
        translate([f[0], f[1], base_z - 1]) cylinder(d = foot_d, h = 1 + foot_recess);
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
    h = box_roof_under_z - box_skirt_gap + eps;
    difference() {
        union() {
            translate([x0, y0, box_roof_under_z]) cube([x1 - x0, y1 - y0, box_roof_t]);
            translate([x1 - box_skirt_t, ys, box_skirt_gap]) cube([box_skirt_t, y1 - ys, h]);
            translate([xs, y1 - box_skirt_t, box_skirt_gap]) cube([x1 - xs, box_skirt_t, h]);
        }
        for (a = boss_axes())
            translate([a[0], a[1], box_roof_under_z - 1]) cylinder(d = 2.4, h = box_roof_t + 2);
    }
}

// ---------------------------------------------------------------- pocket test print
module pocket_test() {
    c = bc();
    intersection() {
        tray();
        translate([c[0] - 25, c[1] - 25, base_z - 1]) cube([50, 50, rim_z - base_z + 2]);
    }
}

// ---------------------------------------------------------------- dummies for views
module pcb_dummy() color("darkgreen") translate([0, 0, -pcb_t]) linear_extrude(pcb_t) pcb_2d();

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

module cradle_dummy() {
    hb = housing_box(half);
    color("royalblue") {
        translate([bc()[0], bc()[1], -pcb_t - 0.3]) cylinder(d = cradle_cup_d(), h = cradle_rim_z() + pcb_t + 0.3);
        translate([minx(hb), miny(hb), pocket_floor_z]) cube([maxx(hb) - minx(hb), maxy(hb) - miny(hb), -pcb_t - 0.3 - pocket_floor_z]);
    }
}
