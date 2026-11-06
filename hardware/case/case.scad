// k0d3ball35 printed case - entry point
// Usage: openscad --backend manifold -D half=\"right\" -D part=\"tray\" -o tray-right.stl case.scad
// Parts: tray | box_cap | lid | lid_dome | pocket_test | assembly | section | floor2d
// Layout facts come from data.scad (scripts/gen_case.py), dimensions from params.scad.

include <params.scad>
include <data.scad>
include <common.scad>
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
echo(str("STACK lid_lift=", lid_top_z - rim_z + lid_lip_depth));
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
    else if (part == "lid_dome") lid_dome();
    else if (part == "pocket_test") pocket_test();
    else if (part == "assembly") assembly();
    else if (part == "section") section();
    else if (part == "floor2d") floor2d();
    else if (part == "lid_on") { tray(); if (controller_box) box_cap(); color("tan", 0.6) lid(); }
    else if (part == "lid_foot") { tray(); if (controller_box) box_cap(); color("tan") lid_as_foot(); }
    else assert(false, str("unknown part ", part));
}

// the lid the same way up with its roof top against the tray underside (foot position); the
// four roof magnets meet the four floor magnets
module lid_as_foot() translate([0, 0, base_z - lid_top_z]) lid();

if (half == "left" && mirror_left) mirror([1, 0, 0]) dispatch();
else dispatch();
