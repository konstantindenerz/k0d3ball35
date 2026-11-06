// k0d3ball35 trackball cradle
//
// A 3D printed holder for a 19.05 mm (or 25 mm) trackball with three static ceramic
// bearings and a PMW3610 / LM18-LSI sensor daughterboard underneath. The cup rim stays
// below the ball equator and there is no retainer: the ball rests in the cup by gravity,
// a removable case lid covers it in transport (issues/mech-case-lid.md).
//
// Two ways to mount it (params.scad, `mount`):
//   "pocket" (r2 default): the module stands on the case floor in a pocket beside the main
//            PCB. The sensor board sits inside the housing and is screwed to two M2 posts
//            from below; the same two screws (M2 x 10) come up through the case floor, so the
//            posts double as the case fastening. The housing walls reach the floor and the
//            PCB edge only has an octagonal notch around the cup.
//   "cutout" (r1): the cup drops through a round cutout of the main PCB and a round flange
//            under the PCB is pulled up with three M2 screws from the top.
//
//   part = "cradle"       the printed cup + housing (+ flange in the cutout mount)
//   part = "assembly"     cradle + ball + sensor dummy + PCB / floor dummies
//   part = "section"      half model for section previews
//   part = "cutout2d"     2D outline of the required PCB clearance, cutout mount (export as DXF)
//   part = "floor2d"      2D footprint of the module on the case floor, pocket mount (export as DXF)
//   part = "sensor_dummy" lens + PCB + pins envelope only
//
// See params.scad for every dimension and README.md for the stack derivation.

include <params.scad>

// ------------------------------------------------------------------ derived values
pocket = (mount == "pocket");
R      = ball_d / 2;
R_in   = R + ball_gap;                 // cup inner radius
R_out  = R_in + wall;                  // cup outer radius
L_pcb  = R + lens_z + lens_h;          // ball centre -> sensor PCB (lens side) along the axis
L_low  = L_pcb + sensor_pcb_t + sensor_pins_h;   // ball centre -> lowest point of the sensor board
cav_h  = lens_h + 0.4;                 // lens cavity height (lens + 0.4 clearance)
hw     = housing_wall;
hwx    = pocket ? housing_wall_x : hw;
hous_x = sensor_pcb_w + 2 * hwx;       // housing footprint, local x (tilt plane)
hous_y = sensor_pcb_l + 2 * hw;        // housing footprint, local y (tangential)
th     = pocket ? 0 : sensor_angle;    // the pocket housing is always straight
s = sin(th); c = cos(th);

// lowest point below the ball centre, for the sensor board and for the printed housing
drop_board   = L_low * c + (sensor_pcb_w / 2) * s;
drop_housing = L_pcb * c + (hous_x / 2) * s;
drop         = max(drop_board, drop_housing);

// case floor (pocket mount) / lowest allowed point (cutout mount)
floor_z = -pcb_t - depth_below_pcb;
// ball centre height above the main PCB top
zc = floor_z + drop;

rim_z        = zc - rim_drop;
bear_dist    = R + bearing_d / 2;      // ball centre -> bearing centre
seat_d       = bearing_d - 2 * bearing_fit;
seat_depth   = bearing_d - ball_gap;   // from cup inner surface to seat bottom
boss_len     = seat_depth + 1.4 + 0.5; // bearing boss length along its axis (starts at R_in - 0.5)
boss_r       = (seat_d + 3.2) / 2;
radial_ext   = L_pcb * s + (hous_x / 2) * c;                        // outward reach of the housing (x), tilted case
board_z      = zc - L_pcb;                                          // sensor PCB plane (lens side)
hous_top     = pocket ? min(zc - R_in + 1.0, -pcb_t - pcb_clear) : zc - R_in + 1.0;
skirt_z      = pocket ? floor_z : -pcb_t - flange_t;                // bottom of the cylindrical cup skirt
slot_w       = cable_slot_w > 0 ? cable_slot_w : hous_x - 2 * corner_post;
// largest diameter of anything above the PCB underside (cup, bearing bosses):
// must stay inside the layout's cradle clearance circle (trackball.cradle_diameter)
boss_reach   = (R_in - 0.5 + boss_len) * cos(bearing_elev) + boss_r * sin(bearing_elev);
envelope_d   = 2 * max(R_out, boss_reach);

// ------------------------------------------------------------------ reporting
echo(str("STACK mount_pocket=", pocket ? 1 : 0));
echo(str("STACK ball_d=", ball_d));
echo(str("STACK sensor_angle=", th));
echo(str("STACK ball_centre_z=", zc));
echo(str("STACK ball_top_above_pcb_top=", zc + R));
echo(str("STACK ball_bottom_z=", zc - R));
echo(str("STACK bearing_contact_z=", zc - R * sin(bearing_elev)));
echo(str("STACK rim_z=", rim_z));
echo(str("STACK rim_below_equator=", zc - rim_z));
echo(str("STACK lens_reference_plane_dist=", lens_z));
echo(str("STACK sensor_pcb_plane_dist=", L_pcb));
echo(str("STACK sensor_pcb_plane_z=", board_z));
echo(str("STACK lowest_plastic_z=", pocket ? floor_z : zc - drop_housing));
echo(str("STACK lowest_sensor_board_z=", zc - drop_board));
echo(str("STACK floor_z=", floor_z));
echo(str("STACK depth_below_pcb_bottom=", depth_below_pcb));
echo(str("STACK housing_radial_extent_x=", radial_ext));
echo(str("STACK housing_x=", hous_x));
if (pocket) echo(str("STACK cable_channel_x=", cable_ch_x));
if (pocket) echo(str("STACK cable_channel_w=", cable_ch_w));
echo(str("STACK housing_y=", hous_y));
echo(str("STACK housing_top_z=", hous_top));
echo(str("STACK footprint_x=", pocket ? hous_x : flange_d));
echo(str("STACK footprint_y=", pocket ? hous_y : flange_d));
if (pocket) echo(str("STACK case_screw_sp=", sensor_hole_sp));   // case screws through the sensor posts, local y axis
echo(str("STACK cup_outer_d=", 2 * R_out));
echo(str("STACK envelope_d_above_pcb=", envelope_d));
echo(str("STACK notch_apothem=", notch_apothem));
echo(str("STACK pcb_cutout_d=", pocket ? 2 * notch_apothem : pcb_cutout_d));

// ------------------------------------------------------------------ helpers
module at_ball() { translate([0, 0, zc]) children(); }

// local sensor frame: origin at the ball centre, -z along the optical axis towards the sensor
module sensor_frame() {
    at_ball() rotate([0, 0, sensor_az]) rotate([0, th, 0]) children();
}

module radial(az, elev) {   // orient children so +z points from the ball centre outwards
    at_ball() rotate([0, 0, az]) rotate([0, 90 + elev, 0]) children();
}

module octagon(apothem) { rotate([0, 0, 22.5]) circle(r = apothem / cos(22.5), $fn = 8); }

// ------------------------------------------------------------------ cradle solids
module cup_outer() {
    at_ball() sphere(r = R_out);
    translate([0, 0, skirt_z]) cylinder(r = R_out, h = zc - skirt_z);
    // bearing bosses
    for (az = bearing_az) radial(az, bearing_elev)
        translate([0, 0, R_in - 0.5]) cylinder(r = boss_r, h = boss_len);
}

module housing_outer() {
    if (pocket) {
        // walls around the sensor board, from the case floor up to just under the PCB;
        // nothing else touches the floor, the case screws go into the sensor posts
        translate([-hous_x / 2, -hous_y / 2, floor_z]) cube([hous_x, hous_y, hous_top - floor_z]);
    } else {
        sensor_frame() {
            // from the sensor PCB plane up into the cup wall
            translate([-hous_x / 2, -hous_y / 2, -L_pcb]) cube([hous_x, hous_y, L_pcb - R_in + 1.0]);
        }
    }
}

module flange_outer() {
    if (!pocket) translate([0, 0, -pcb_t - flange_t]) cylinder(d = flange_d, h = flange_t);
}

module sensor_pocket_cuts() {   // lens cavity, optical path and the two M2 posts, in the sensor frame
    cylinder(d = 9, h = L_pcb + 1);                                  // optical path (both directions)
    translate([0, 0, -R_in - 2]) cylinder(d = 9, h = R_in + 3);       // through the cup floor
    translate([-(sensor_pcb_w - 2) / 2, -(sensor_pcb_l - 2) / 2, -L_pcb - 0.01])
        difference() {
            cube([sensor_pcb_w - 2, sensor_pcb_l - 2, cav_h + 0.01]);
            for (sy = [-1, 1]) translate([(sensor_pcb_w - 2) / 2, (sensor_pcb_l - 2) / 2 + sy * sensor_hole_sp / 2, 0])
                cylinder(d = 5, h = cav_h + 0.02);                   // boss columns stay
        }
    for (sy = [-1, 1]) translate([0, sy * sensor_hole_sp / 2, -L_pcb - 0.01])
        cylinder(d = flange_pilot_d, h = cav_h + 3);                 // M2 pilots in the boss columns
}

module cradle_cuts() {
    // ball cavity
    at_ball() sphere(r = R_in);
    // everything above the rim
    translate([-100, -100, rim_z]) cube([200, 200, 100]);
    sensor_frame() {
        sensor_pocket_cuts();
        if (!pocket)   // everything below the sensor PCB plane (keeps the housing face flat for the board)
            translate([-50, -50, -L_pcb - 50]) cube([100, 100, 50]);
    }
    if (pocket) {
        // board cavity: the sensor board slides in from below and screws to the posts
        bw = sensor_pcb_w + 2 * sensor_pcb_gap;
        bl = sensor_pcb_l + 2 * sensor_pcb_gap;
        translate([-bw / 2, -bl / 2, floor_z - 1]) cube([bw, bl, board_z - floor_z + 1.01]);
        // FFC slot through the key-facing (-y) wall, from the floor up to the board plane
        translate([-slot_w / 2, -hous_y / 2 - 1, floor_z - 1]) cube([slot_w, hw + 2, board_z - floor_z + 1.01]);
        // and on from the board plane to the top of the housing: the cable turns up here and
        // climbs past the PCB plane in the gap between the cup and the notch (r2.2)
        translate([cable_ch_x - cable_ch_w / 2, -hous_y / 2 - 1, board_z - 0.01])
            cube([cable_ch_w, hw + 2, hous_top - board_z + 0.02]);
        // case screw path: the post pilot holes continue straight down to the housing underside, so
        // the M2 x 10 screws pass the case floor, the component gap and the board into the posts
        for (sy = [-1, 1]) translate([0, sy * sensor_hole_sp / 2, floor_z - 1])
            cylinder(d = flange_pilot_d, h = board_z - floor_z + 1.5);
        // PCB keep-out: nothing above the PCB underside outside the notch (with clearance)
        difference() {
            translate([0, 0, -pcb_t - pcb_clear]) cylinder(d = 200, h = 100);
            translate([0, 0, -pcb_t - pcb_clear - 0.01]) linear_extrude(100.02) octagon(notch_apothem - pcb_clear);
        }
    }
    // bearing seats
    for (az = bearing_az) radial(az, bearing_elev)
        translate([0, 0, R_in - 0.01]) cylinder(d = seat_d, h = seat_depth + 0.01);
    if (!pocket) {
        // flange pilot holes
        for (az = flange_hole_az) rotate([0, 0, az]) translate([flange_hole_bcd / 2, 0, -pcb_t - flange_t - 1])
            cylinder(d = flange_pilot_d, h = flange_t + 2);
        // main PCB keep-out: nothing of the cradle may live inside the PCB slab outside the cutout
        difference() {
            translate([0, 0, -pcb_t]) cylinder(d = 200, h = pcb_t);
            translate([0, 0, -pcb_t - 0.01]) cylinder(d = pcb_cutout_d - 1.0, h = pcb_t + 0.02);
        }
    }
}

module cradle() {
    difference() {
        union() { cup_outer(); housing_outer(); flange_outer(); }
        cradle_cuts();
    }
}

// ------------------------------------------------------------------ dummies for the assembly view
module ball() { at_ball() color("ivory") sphere(r = R); }

module sensor_dummy() {
    sensor_frame() {
        color("gray", 0.6) translate([-lens_l / 2, -lens_w / 2, -L_pcb]) cube([lens_l, lens_w, lens_h]);   // lens body
        color("green", 0.7) translate([-sensor_pcb_w / 2, -sensor_pcb_l / 2, -L_pcb - sensor_pcb_t])
            cube([sensor_pcb_w, sensor_pcb_l, sensor_pcb_t]);                                             // sensor PCB
        color("black", 0.7) translate([-5.05, -8.1, -L_low]) cube([10.1, 16.2, sensor_pins_h]);           // package + solder
    }
}

module main_pcb_dummy() {
    color("darkgreen", 0.3) difference() {
        translate([0, 0, -pcb_t]) cylinder(d = 70, h = pcb_t);
        if (pocket) translate([0, 0, -pcb_t - 0.1]) linear_extrude(pcb_t + 0.2) octagon(notch_apothem);
        else        translate([0, 0, -pcb_t - 0.1]) cylinder(d = pcb_cutout_d, h = pcb_t + 0.2);
    }
}

module case_floor_dummy() {   // pocket mount: the case floor the module stands on
    if (pocket) color("burlywood", 0.3) translate([-35, -35, floor_z - 1.5]) cube([70, 70, 1.5]);
}

// ------------------------------------------------------------------ 2D exports
module cutout2d() {   // cutout mount: PCB clearance incl. the flange holes
    offset(r = 0.5) projection(cut = true) translate([0, 0, pcb_t / 2]) union() { cradle(); }
    for (az = flange_hole_az) rotate([0, 0, az]) translate([flange_hole_bcd / 2, 0]) circle(d = 2.2);
}

module floor2d() {    // pocket mount: housing outline on the case floor with 0.5 mm clearance and the two case screw holes
    difference() {
        offset(r = 0.5) square([hous_x, hous_y], center = true);
        for (sy = [-1, 1]) translate([0, sy * sensor_hole_sp / 2]) circle(d = case_screw_d + 0.2);
    }
}

// ------------------------------------------------------------------ dispatch
if (part == "cradle")        cradle();
else if (part == "sensor_dummy") sensor_dummy();
else if (part == "cutout2d") cutout2d();
else if (part == "floor2d")  floor2d();
else if (part == "section") {           // half model for section previews
    difference() {
        union() { cradle(); ball(); sensor_dummy(); main_pcb_dummy(); case_floor_dummy(); }
        translate([-100, 0, -100]) cube([200, 100, 200]);
    }
}
else { cradle(); ball(); sensor_dummy(); main_pcb_dummy(); case_floor_dummy(); }
