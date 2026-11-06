// k0d3ball35 printed case - removable lid per half (transport cover and foot)
// The skirt stands on the tray rim (rim_z) and follows the outer footprint including the
// pocket block; the roof clears keycaps and ball by lid_clear. A 1 mm lip on the inside of the
// skirt reaches lid_lip_depth into the tray and holds the lid by friction, no magnets on top.
// Under the half (same way up, roof top against the tray underside) four magnets in the roof
// meet four in the tray floor and the lid lifts the half by lid_top_z - rim_z + lid_lip_depth.

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

// magnets in the roof, inserted from the roof underside; magnet_skin stays closed on top
module lid_roof_magnets(under) {
    for (c = foot_magnets(half))
        translate([c[0], c[1], under - 1]) cylinder(d = magnet_d, h = 1 + magnet_h + magnet_pocket_extra);
}

// ---------------------------------------------------------------- lip
lid_lip_chamfer = 0.5;         // lead-in on the lower outer edge of the lip
lid_lip_steps   = 5;

// where the lip must not be: the controller box walls (plus their notch) and the pocket cup
module lip_clear_2d() {
    if (controller_box) offset(delta = pcb_clear + wall + lid_box_clear + 1) box_2d();
    if (has_ball(half)) {
        offset(delta = 1) pocket_cavity_2d();
        fpc_keepout_2d();
    }
}
// ring between the inner wall face minus `inset` and the lip's inner face
module lip_2d(inset) difference() {
    difference() {
        offset(delta = -inset) pcb_cavity_2d();
        offset(delta = -lid_fit - lid_lip_t) pcb_cavity_2d();
    }
    lip_clear_2d();
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

// everything above a plane that rises towards -x (inner edge) by tent_wedge_deg
module tent_cut() {
    xr = maxx(outline(half)) + pcb_clear + wall + 1;
    translate([xr, 0, lid_top_z]) rotate([0, tent_wedge_deg, 0]) translate([-1000, -500, 0]) cube([2000, 1000, 500]);
}

module lid() {
    lid_shell(lid_roof_under_z) {
        if (tent_wedge_deg > 0) difference() { lid_body(lid_top_z + 300); tent_cut(); }
        else lid_body(lid_top_z);
    }
}

// dome variant for the ball half: flat roof at keycap height plus a round turret over the pocket
module lid_dome() {
    under = cap_top_z + lid_clear;
    difference() {
        lid_shell(under) {
            lid_body(under + lid_roof_t);
            if (has_ball(half))
                translate([bc()[0], bc()[1], under]) cylinder(d = cradle_d + 2 * pocket_wall, h = dome_top_z - under);
        }
        if (has_ball(half))
            translate([bc()[0], bc()[1], under - 1]) cylinder(d = cradle_d, h = ball_top_z + lid_clear - under + 1);
    }
}
