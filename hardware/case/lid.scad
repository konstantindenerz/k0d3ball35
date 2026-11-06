// k0d3ball35 printed case - removable lid per half (transport cover and foot)
// The skirt stands on the tray rim (rim_z) and follows the outer footprint including the
// magnet pads and the pocket block; the roof clears keycaps and ball by lid_clear. Flipped
// over and stuck under the half with the same magnets it lifts the half by lid_top_z - rim_z.

module lid_body(top) translate([0, 0, rim_z]) linear_extrude(top - rim_z) outer_top_2d();

module lid_cavity(top) {
    translate([0, 0, rim_z - 1]) linear_extrude(top - rim_z + 1) {
        pcb_cavity_2d();
        if (has_ball(half)) pocket_cavity_2d();
    }
}

// the tall controller box walls poke into the lid
module lid_box_notch() {
    if (controller_box)
        translate([0, 0, rim_z - 1]) linear_extrude(box_top_z + lid_box_clear - rim_z + 1)
            offset(delta = pcb_clear + wall + lid_box_clear) box_2d();
}

module lid_magnets() {
    for (p = magnet_pads(half)) {
        c = magnet_center(p);
        translate([c[0], c[1], rim_z - 1]) cylinder(d = magnet_d, h = 1 + magnet_h + magnet_pocket_extra);
    }
}

// everything above a plane that rises towards -x (inner edge) by tent_wedge_deg
module tent_cut() {
    xr = maxx(outline(half)) + wall + pad_size[1] + 1;
    translate([xr, 0, lid_top_z]) rotate([0, tent_wedge_deg, 0]) translate([-1000, -500, 0]) cube([2000, 1000, 500]);
}

module lid() {
    difference() {
        if (tent_wedge_deg > 0) difference() { lid_body(lid_top_z + 300); tent_cut(); }
        else lid_body(lid_top_z);
        lid_cavity(lid_roof_under_z);
        lid_box_notch();
        lid_magnets();
    }
}

// dome variant for the ball half: flat roof at keycap height plus a round turret over the pocket
module lid_dome() {
    under = cap_top_z + lid_clear;
    difference() {
        union() {
            lid_body(under + lid_roof_t);
            if (has_ball(half))
                translate([bc()[0], bc()[1], under]) cylinder(d = cradle_d + 2 * pocket_wall, h = dome_top_z - under);
        }
        lid_cavity(under);
        if (has_ball(half))
            translate([bc()[0], bc()[1], under - 1]) cylinder(d = cradle_d, h = ball_top_z + lid_clear - under + 1);
        lid_box_notch();
        lid_magnets();
    }
}
