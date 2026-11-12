// k0d3ball35 printed case - entry point
// Usage: openscad --backend manifold -D half=\"right\" -D part=\"tray\" -o tray-right.stl case.scad
// Parts: tray | box_cap | pocket_cover | pocket_clip | guard | guard2d | lid | lid_outer | lid_inner | lid_folded | pocket_test | assembly | section | floor2d
// Previews: lid_on | lid_foot (tilted on the desk) | lid_foot_flat
// Layout facts come from data.scad (scripts/gen_case.py), dimensions from params.scad.

include <params.scad>
include <data.scad>
include <logo_data.scad>
include <common.scad>
include <logo.scad>
include <tray.scad>
include <lid.scad>

ob = outline(half);
echo(str("STACK floor_z_key=", floor_z_key));
echo(str("STACK well_floor_z=", well_floor_z));
echo(str("STACK pocket_floor_z=", pocket_floor_z));
echo(str("STACK base_z=", base_z));
echo(str("STACK desk_z=", base_z - (foot_h - foot_recess)));   // the table under the feet
echo(str("STACK rim_z=", rim_z));
echo(str("STACK cap_w=", cap_size[0]));
echo(str("STACK cap_h=", cap_size[1]));
echo(str("STACK cap_top_z=", cap_top_z));
echo(str("STACK standoff_h=", standoff_h));
echo(str("STACK standoff_d=", standoff_d));
echo(str("STACK insert_hole_d=", insert_hole_d));
echo(str("STACK insert_depth=", insert_depth));
echo(str("STACK pcb_hole_depth=", pcb_hole_depth));
echo(str("STACK boss_hole_depth=", screw_hole_depth));
echo(str("STACK box_roof_t=", box_roof_t));
echo(str("STACK reset_plunger_z=", reset_plunger_z));
echo(str("STACK usb_w=", usb_cut[0]));
echo(str("STACK usb_z0=", usb_z0));
echo(str("STACK usb_z1=", usb_z1));
echo(str("STACK usb_x=", usb_x()));
echo(str("STACK usb_wall_y=", box_y_in() - wall));
echo(str("STACK usb_face_y=", ctrl_rect(half)[1] - usb_face_in));
echo(str("STACK ctrl_top_z=", ctrl_top_z));
echo(str("STACK usb_shell_h=", usb_shell_h));
echo(str("STACK box_roof_under_z=", box_roof_under_z));
echo(str("STACK box_top_z=", box_top_z));
echo(str("STACK lid_roof_under_z=", lid_roof_under_z));
echo(str("STACK lid_top_z=", lid_top_z));
echo(str("STACK lid_roof_t=", lid_roof_t));
echo(str("STACK edge_chamfer=", edge_chamfer));
echo(str("STACK rim_chamfer=", rim_chamfer));
echo(str("STACK lid_lip_depth=", lid_lip_depth));
echo(str("STACK hinge_x=", hx));
echo(str("STACK hinge_axis_z=", hinge_axis_z));
echo(str("STACK hinge_knuckle_d=", hinge_knuckle_d));
echo(str("STACK hinge_pin_d=", hinge_pin_d));
echo(str("STACK hinge_pin_len=", hinge_len() - hinge_blind));
echo(str("STACK hinge_y0=", hinge_span()[0]));
echo(str("STACK hinge_y1=", hinge_span()[1]));
echo(str("STACK hinge_segments=", hinge_segments()));
echo(str("STACK hinge_seg=", hinge_seg()));
echo(str("STACK tent_deg=", tent_deg));
echo(str("STACK hinge_fold_deg=", hinge_fold_solved));
echo(str("STACK hinge_stop_deg=", hinge_stop_deg));
echo(str("STACK foot_dx=", foot_dx(half)));
echo(str("STACK foot_tilt_deg=", foot_tilt_deg()));
echo(str("STACK foot_beta_deg=", foot_beta_deg()));
echo(str("STACK foot_hinge_h=", foot_hinge_h()));
echo(str("STACK foot_reach=", foot_reach()));
echo(str("STACK foot_free_end_h=", foot_free_end_h()));
echo(str("STACK has_ball=", has_ball(half) ? 1 : 0));
echo(str("STACK ball_top_z=", ball_top_z));
echo(str("STACK cradle_rim_z=", cradle_rim_z()));
echo(str("STACK pocket_rim_z=", pocket_rim_z()));
echo(str("STACK housing_x=", has_ball(half) ? maxx(housing_box(half)) - minx(housing_box(half)) : 0));
echo(str("STACK housing_y=", has_ball(half) ? maxy(housing_box(half)) - miny(housing_box(half)) : 0));
echo(str("STACK case_screw_sp=", has_ball(half) ? norm(case_screws(half)[1] - case_screws(half)[0]) : 0));
echo(str("STACK case_screw_d=", case_screw_d));
echo(str("STACK cover_z0=", has_ball(half) ? cover_z0 : 0));
echo(str("STACK cover_hole_d=", cover_hole_d));
echo(str("STACK cover_t=", cover_t));
echo(str("STACK clip_top_z=", clip_top_z()));
echo(str("STACK clip_ro=", clip_ro));
echo(str("STACK clip_ri=", clip_ri));
echo(str("STACK clip_pin_r=", clip_pin_r));
echo(str("STACK clip_pin_az=", clip_pin_az));
echo(str("STACK clip_open_az=", clip_open_az));
echo(str("STACK clip_claw_az=", clip_claw_az));
echo(str("STACK clip_barb_bottom_z=", barb_z_bot()));
echo(str("STACK case_screw_head_d=", case_screw_head_d));
echo(str("STACK case_screw_cs_d=", case_screw_cs_d));
echo(str("STACK case_screw_cs_h=", case_screw_cs_h));
echo(str("STACK case_screw_head_z=", base_z + (case_screw_cs_d - case_screw_head_d) / 2));
echo(str("STACK case_screw_floor_left=", (pocket_floor_z - base_z) - case_screw_cs_h));
echo(str("STACK guard_t=", guard_t));
echo(str("STACK guard_top_z=", guard_top_z));
echo(str("STACK guard_air=", guard_air));
echo(str("STACK cap_skirt_z=", cap_skirt_z));
echo(str("STACK switch_travel=", switch_travel));
echo(str("STACK bbox_min_x=", minx(ob)));
echo(str("STACK bbox_min_y=", miny(ob)));
echo(str("STACK bbox_max_x=", maxx(ob)));
echo(str("STACK bbox_max_y=", maxy(ob)));
echo(str("STACK box_x0=", box_r()[0]));
echo(str("STACK box_y0=", box_r()[1]));
echo(str("STACK box_x1=", box_inner_x));
echo(str("STACK box_y1=", box_r()[3]));
echo(str("STACK foot_magnets=", len(foot_magnets(half))));
echo(str("STACK logo_on_cap=", logo_on_cap ? 1 : 0));
echo(str("STACK logo_on_floor=", logo_on_floor ? 1 : 0));
echo(str("STACK logo_depth=", logo_depth));
echo(str("STACK logo_line_w=", min(logo_cell, logo_floor_cell)));
echo(str("STACK logo_cap_x=", logo_size(logo_cell)[0]));
echo(str("STACK logo_cap_y=", logo_size(logo_cell)[1]));
echo(str("STACK logo_cap_area=", logo_on_cap ? logo_area(logo_cell) : 0));
echo(str("STACK logo_floor_area=", logo_on_floor ? logo_area(logo_floor_cell) : 0));

module assembly() {
    tray();
    pcb_dummy();
    keys_dummy();
    controller_dummy();
    battery_dummy();
    if (guard) color("dimgray") guard();
    if (controller_box) color("tan") box_cap();
    if (has_ball(half)) { ball_dummy(); cradle_dummy(); color("tan") pocket_cover(); }
}

module section() {
    c = bc();
    difference() {
        assembly();
        translate([-500, c[1], -100]) cube([1000, 1000, 300]);
    }
}

// floor plan for the DXF: outer footprint, every hole, the wells drawn as thin outline rings
module ring_2d() difference() { children(); offset(delta = -0.1) children(); }
module floor2d() {
    difference() {
        outer_2d();
        for (hp = holes(half)) translate(hp) circle(d = 2.2);
        if (has_ball(half)) {
            ring_2d() pocket_well_2d();
            for (s = case_screws(half)) translate(s) circle(d = case_screw_d);
        }
        ring_2d() well_2d();
        translate(reset(half)) circle(d = reset_hole_d);
    }
}

module dispatch() {
    if (part == "tray") tray();
    else if (part == "box_cap") box_cap();
    else if (part == "pocket_cover") pocket_cover();
    else if (part == "pocket_clip") pocket_clip();                       // ball-centred, like the cradle STL
    else if (part == "clip_placed") translate([bc()[0], bc()[1], 0]) pocket_clip();
    else if (part == "clip_clash") intersection() {                      // must be empty (tests)
        translate([bc()[0], bc()[1], 0]) pocket_clip();
        union() { pocket_cover(); tray(); cradle_dummy(); }
    }
    else if (part == "assembly_clip") { assembly(); color("darkorange") translate([bc()[0], bc()[1], 0]) pocket_clip(); }

    else if (part == "guard") guard();
    else if (part == "guard2d") guard_2d();
    else if (part == "lid") lid();
    else if (part == "lid_outer") lid_plate("outer");
    else if (part == "lid_inner") lid_plate("inner");
    else if (part == "lid_folded") lid_folded();
    else if (part == "pocket_test") pocket_test();
    else if (part == "assembly") assembly();
    else if (part == "section") section();
    else if (part == "floor2d") floor2d();
    else if (part == "lid_on") { tray(); if (controller_box) box_cap(); if (has_ball(half)) pocket_cover(); color("tan", 0.6) lid(); }
    else if (part == "lid_foot") on_desk() { tray(); if (controller_box) box_cap(); if (has_ball(half)) pocket_cover(); color("tan") lid_under_tray(); }
    else if (part == "lid_foot_flat") { tray(); if (controller_box) box_cap(); color("tan") lid_under_tray(); }
    else assert(false, str("unknown part ", part));
}

// The sources work in the layout frame: x outward, y towards the user, z up. That frame is
// left-handed, and STL and DXF are always read right-handed, so exporting it as it is would give
// the mirror image of the real part (issues/mech-case-stl-mirrored.md). The export flips y once
// here: the files are in the print frame, x outward, y away from the user, z up - what a slicer
// shows from above with the user at the front of the bed. The echoed STACK numbers stay in the
// layout frame.
module print_frame() mirror([0, 1, 0]) children();

print_frame()
    if (half == "left" && mirror_left) mirror([1, 0, 0]) dispatch();
    else dispatch();
