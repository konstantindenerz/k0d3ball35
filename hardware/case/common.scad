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

// lid heights depend on the half: with lid_mode "flat" the ball half needs the roof above the
// ball; "window" and "dome" keep the roof at keycap height everywhere
lid_roof_under_z = (has_ball(half) && lid_mode == "flat") ? max(cap_top_z, ball_top_z) + lid_clear
                                                         : cap_top_z + lid_clear;
lid_top_z        = lid_roof_under_z + lid_roof_t;
dome_top_z       = ball_top_z + lid_clear + lid_roof_t;
lid_window       = lid_mode == "window" && has_ball(half);

// ---------------------------------------------------------------- lid hinge
hx               = hinge_x(half);                               // hinge line x
hinge_axis_z     = lid_top_z - hinge_knuckle_d / 2;             // knuckles flush with the roof top
lip_bottom_z     = rim_z - lid_lip_depth;
// y range of the PCB outline on the vertical line x = hx (the outline is stepped, so the
// crossing edges are horizontal and the outer skirt simply adds pcb_clear + wall)
function _cross_ys(p, x) = [for (i = [0 : len(p) - 1]) let (a = p[i], b = p[(i + 1) % len(p)])
    if ((a[0] <= x && b[0] > x) || (b[0] <= x && a[0] > x))
        a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])];
function hinge_span() = let (ys = _cross_ys(outline(half), hx), w = pcb_clear + wall)
    [min(ys) - w, max(ys) + w];
function hinge_len() = hinge_span()[1] - hinge_span()[0];
function hinge_segments() = 2 * floor(hinge_len() / (2 * hinge_seg_len)) + 1;
function hinge_seg() = (hinge_len() - (hinge_segments() - 1) * hinge_seg_gap) / hinge_segments();
function hinge_seg_y0(i) = hinge_span()[0] + i * (hinge_seg() + hinge_seg_gap);
// knuckle i belongs to the outer plate when i is even (so both ends are outer)
function hinge_owner(i) = (i % 2 == 0) ? "outer" : "inner";

// ---------------------------------------------------------------- foot pose
// As a foot the lid is shifted by foot_dx (data.scad) so its hinge axis sits foot_overhang
// outside the inner tray wall: the outer plate lies roof-up under the controller half, the
// inner plate folds down beyond the inner edge as the kickstand. The half rotates about its
// outer bottom edge by tent_deg (input); the fold is the angle at which the kickstand's lip
// edge reaches the desk, solved by bisection. The stop faces are cut for exactly that fold.
function _rot2(p, a) = [p[0] * cos(a) + p[1] * sin(a), -p[0] * sin(a) + p[1] * cos(a)];
function _lip_in() = pcb_clear - lid_fit - lid_lip_chamfer;    // lip foot outside the PCB edge (negative: inside)
function foot_pivot_x() = maxx(outline(half)) + pcb_clear + wall;             // tray's outer bottom edge
function foot_axis_x() = hx + foot_dx(half);                                   // hinge axis, board frame
// hinge axis above the desk: the axis is hinge_knuckle_d / 2 under the roof top = tray underside
function foot_hinge_h() = _rot2([foot_axis_x() - foot_pivot_x(), -hinge_knuckle_d / 2], tent_deg)[1];
// the kickstand's contact edge relative to the axis in the lid frame (lip bottom at the inner edge)
function _kick_rel() = [minx(outline(half)) - _lip_in() - hx, lip_bottom_z - hinge_axis_z];
function _kick_gap(f) = foot_hinge_h() + _rot2(_kick_rel(), tent_deg - f)[1];
function _bisect(lo, hi, n) = n == 0 ? (lo + hi) / 2
    : let (m = (lo + hi) / 2) (_kick_gap(m) > 0 ? _bisect(m, hi, n - 1) : _bisect(lo, m, n - 1));
hinge_fold_solved = _bisect(0, 90 + tent_deg, 40);
hinge_fold_deg    = hinge_fold_override > 0 ? hinge_fold_override : hinge_fold_solved;
hinge_stop_deg    = hinge_fold_solved / 2;                     // each cut face leans this far outward
function foot_beta_deg() = hinge_fold_solved - tent_deg;       // kickstand angle below the desk plane... measured from the tray
function foot_reach() = -(foot_axis_x() - foot_pivot_x() + _rot2(_kick_rel(), tent_deg - hinge_fold_solved)[0]
                          + foot_pivot_x() - (minx(outline(half)) - pcb_clear - wall));   // kickstand foot beyond the inner wall
// the outer plate's free end (lip bottom at its outer edge, shifted) above the desk
function foot_free_end_h() = _rot2([maxx(outline(half)) + _lip_in() + foot_dx(half) - foot_pivot_x(),
                                    -(lid_top_z - lip_bottom_z)], tent_deg)[1];
function foot_tilt_deg() = tent_deg;

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

module octagon_2d(c, apothem) translate(c) rotate(22.5) circle(r = apothem / cos(22.5), $fn = 8);
module notch_2d() octagon_2d(bc(), notch_apothem);
module housing_footprint_2d() polygon(housing_footprint(half));
module housing_box_2d() polygon(housing_box(half));
module pocket_well_2d() offset(delta = 0.5) housing_box_2d();
// cavity above the PCB plane: the cradle circle inside the (grown) PCB notch
module pocket_cavity_2d() { translate(bc()) circle(d = cradle_d); offset(delta = pcb_clear) notch_2d(); }
module pocket_ring_2d() { offset(delta = pocket_wall) pocket_cavity_2d(); translate(bc()) circle(d = pocket_d); }

module well_2d() polygon(well(half));
// J1 and the FFC lie on the key side of the PCB since r2.2: nothing of the case may sit on
// them, in particular not the lid lip (docs/08-trackball-module.md).
module fpc_keepout_2d() {
    if (len(fpc_box(half)) > 0) offset(delta = fpc_clear) polygon(fpc_box(half));
    if (len(cable_corridor(half)) > 0) offset(delta = fpc_clear) polygon(cable_corridor(half));
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

// outer footprint below the PCB plane: wall around the cavity, pocket block
module outer_2d() {
    offset(delta = wall) pcb_cavity_2d();
    if (has_ball(half)) housing_footprint_2d();
}
// outer footprint from the PCB plane up: plus the round pocket wall
module outer_top_2d() {
    outer_2d();
    if (has_ball(half)) pocket_ring_2d();
}
