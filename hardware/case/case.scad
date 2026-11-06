// k0d3ball35 printed case - entry point
// Usage: openscad --backend manifold -D half=\"right\" -D part=\"tray\" -o tray-right.stl case.scad
// Parts: tray | box_cap | lid | lid_outer | lid_inner | lid_folded | lid_dome | pocket_test | assembly | section | floor2d
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
echo(str("STACK rim_z=", rim_z));
echo(str("STACK standoff_h=", standoff_h));
echo(str("STACK standoff_d=", standoff_d));
echo(str("STACK insert_hole_d=", insert_hole_d));
echo(str("STACK insert_depth=", insert_depth));
echo(str("STACK box_roof_under_z=", box_roof_under_z));
echo(str("STACK box_top_z=", box_top_z));
echo(str("STACK lid_roof_under_z=", lid_roof_under_z));
echo(str("STACK lid_top_z=", lid_top_z));
echo(str("STACK lid_roof_t=", lid_roof_t));
echo(str("STACK lid_lip_depth=", lid_lip_depth));
echo(str("STACK lid_window=", lid_window ? 1 : 0));
echo(str("STACK ball_window_d=", ball_window_d));
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
echo(str("STACK housing_x=", has_ball(half) ? maxx(housing_box(half)) - minx(housing_box(half)) : 0));
echo(str("STACK housing_y=", has_ball(half) ? maxy(housing_box(half)) - miny(housing_box(half)) : 0));
echo(str("STACK case_screw_sp=", has_ball(half) ? case_screws(half)[1][1] - case_screws(half)[0][1] : 0));
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
    if (controller_box) color("tan") box_cap();
    if (has_ball(half)) { ball_dummy(); cradle_dummy(); }
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
    else if (part == "lid") lid();
    else if (part == "lid_outer") lid_plate("outer");
    else if (part == "lid_inner") lid_plate("inner");
    else if (part == "lid_folded") lid_folded();
    else if (part == "lid_dome") lid_dome();
    else if (part == "pocket_test") pocket_test();
    else if (part == "assembly") assembly();
    else if (part == "section") section();
    else if (part == "floor2d") floor2d();
    else if (part == "lid_on") { tray(); if (controller_box) box_cap(); color("tan", 0.6) lid(); }
    else if (part == "lid_foot") on_desk() { tray(); if (controller_box) box_cap(); color("tan") lid_under_tray(); }
    else if (part == "lid_foot_flat") { tray(); if (controller_box) box_cap(); color("tan") lid_under_tray(); }
    else assert(false, str("unknown part ", part));
}

if (half == "left" && mirror_left) mirror([1, 0, 0]) dispatch();
else dispatch();
