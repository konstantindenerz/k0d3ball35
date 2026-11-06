// k0d3ball35 printed case - 2D building blocks and derived heights
// Everything here works in the layout frame of the selected `half`; the data arrays come
// from data.scad (generated), the offsets and heights from params.scad.

// ---------------------------------------------------------------- helpers
function minx(p) = min([for (q = p) q[0]]);
function maxx(p) = max([for (q = p) q[0]]);
function miny(p) = min([for (q = p) q[1]]);
function maxy(p) = max([for (q = p) q[1]]);
function bc() = ball_center(half);
function ball_centre_z() = ball_top_z - ball_d / 2;
function cradle_rim_z() = ball_centre_z() - 1.0;              // cradle rim_drop
function cradle_cup_d() = ball_d + 2 * 0.4 + 2 * 1.6;          // ball_gap and cup wall of the cradle
function magnet_offset() = pcb_clear + wall + pad_size[1] - magnet_skin - magnet_d / 2;
function magnet_center(p) = [p[0] + p[2] * magnet_offset(), p[1] + p[3] * magnet_offset()];
function mark_center(p) = [p[0] + p[2] * (pcb_clear + wall / 2), p[1] + p[3] * (pcb_clear + wall / 2)];

// lid heights depend on the half: the ball half needs the roof above the ball
lid_roof_under_z = (has_ball(half) && lid_mode == "flat") ? max(cap_top_z, ball_top_z) + lid_clear
                                                         : cap_top_z + lid_clear;
lid_top_z        = lid_roof_under_z + lid_roof_t;
dome_top_z       = ball_top_z + lid_clear + lid_roof_t;

// controller box: inner wall faces and boss axes
function box_r() = box_rect(half);
function box_x_in() = box_r()[0] - pcb_clear;                  // inner face of the outer (-x) wall
function box_y_in() = box_r()[1] - pcb_clear;                  // inner face of the top (-y) wall
function boss_half() = insert_hole_d / 2 + boss_skin;          // 3.0: half of the boss square
function boss_axes() = [[box_x_in() + boss_in, box_y_in() + boss_in],
                        [box_x_in() + boss_in, box_r()[3] - boss_half()]];
function boss_x_end() = box_x_in() + boss_in + boss_half();    // how far the bosses reach into the box
function usb_x() = (ctrl_rect(half)[0] + ctrl_rect(half)[2]) / 2;

// ---------------------------------------------------------------- 2D regions
module pcb_2d() polygon(outline(half));
module pcb_cavity_2d() offset(delta = pcb_clear) pcb_2d();

module pad_2d(p) {
    a = atan2(p[3], p[2]);
    depth = pcb_clear + wall + pad_size[1];
    translate([p[0], p[1]]) rotate(a) translate([-0.5, -pad_size[0] / 2]) square([depth + 0.5, pad_size[0]]);
}
module pads_2d() for (p = magnet_pads(half)) pad_2d(p);

module octagon_2d(c, apothem) translate(c) rotate(22.5) circle(r = apothem / cos(22.5), $fn = 8);
module notch_2d() octagon_2d(bc(), notch_apothem);
module housing_footprint_2d() polygon(housing_footprint(half));
module housing_box_2d() polygon(housing_box(half));
module pocket_well_2d() offset(delta = 0.5) housing_box_2d();
// cavity above the PCB plane: the cradle circle inside the (grown) PCB notch
module pocket_cavity_2d() { translate(bc()) circle(d = cradle_d); offset(delta = pcb_clear) notch_2d(); }
module pocket_ring_2d() { offset(delta = pocket_wall) pocket_cavity_2d(); translate(bc()) circle(d = pocket_d); }

module well_2d() polygon(well(half));
module ffc_channel_2d() {
    fb = fpc_box(half);
    hb = housing_box(half);
    cx = (minx(fb) + maxx(fb)) / 2;
    y0 = miny(fb);
    y1 = miny(hb) + 1.0;
    translate([cx - ffc_channel_w / 2, y0]) square([ffc_channel_w, y1 - y0]);
}

module box_2d() {
    r = box_r();
    translate([r[0], r[1]]) square([box_inner_x - r[0], r[3] - r[1]]);
}
// the tall walls of the controller box: only where the tray has a wall anyway
module box_walls_2d() intersection() {
    difference() { offset(delta = pcb_clear + wall) box_2d(); box_2d(); }
    difference() { outer_2d(); pcb_cavity_2d(); }
}

// outer footprint below the PCB plane: wall around the cavity, magnet pads, pocket block
module outer_2d() {
    offset(delta = wall) pcb_cavity_2d();
    pads_2d();
    if (has_ball(half)) housing_footprint_2d();
}
// outer footprint from the PCB plane up: plus the round pocket wall
module outer_top_2d() {
    outer_2d();
    if (has_ball(half)) pocket_ring_2d();
}
