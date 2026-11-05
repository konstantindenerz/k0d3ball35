// k0d3ball36 trackball cradle
//
// A 3D printed holder for a 25 mm (or 34 mm) trackball with three static ceramic
// bearings and a PMW3610 / LM18-LSI sensor daughterboard underneath. The cup drops
// through the 30 mm cutout of the main PCB, the flange sits against the PCB underside
// and is pulled up with three M2 screws from the top.
//
//   part = "cradle"       the printed cup + housing + flange
//   part = "retainer"     the printed claw ring that keeps the ball in
//   part = "assembly"     cradle + retainer + ball + sensor dummy (visual check)
//   part = "cutout2d"     2D outline of the required PCB clearance (export as DXF)
//   part = "sensor_dummy" lens + PCB + pins envelope only
//
// See params.scad for every dimension and README.md for the stack derivation.

include <params.scad>

// ------------------------------------------------------------------ derived values
R      = ball_d / 2;
R_in   = R + ball_gap;                 // cup inner radius
R_out  = R_in + wall;                  // cup outer radius
L_pcb  = R + lens_z + lens_h;          // ball centre -> sensor PCB (lens side) along the axis
L_low  = L_pcb + sensor_pcb_t + sensor_pins_h;   // ball centre -> lowest point of the sensor board
cav_h  = lens_h + 0.4;                 // lens cavity height (lens + 0.4 clearance)
hw     = housing_wall;
hous_x = sensor_pcb_w + 2 * hw;        // housing footprint, local x (tilt plane)
hous_y = sensor_pcb_l + 2 * hw;        // housing footprint, local y (tangential)
th     = sensor_angle;
s = sin(th); c = cos(th);

// lowest point below the ball centre, for the sensor board and for the printed housing
drop_board   = L_low * c + (sensor_pcb_w / 2) * s;
drop_housing = L_pcb * c + (hous_x / 2) * s;
drop         = max(drop_board, drop_housing);

// ball centre height above the main PCB top
zc = -pcb_t - depth_below_pcb + drop;

rim_z        = zc - rim_drop;
bear_dist    = R + bearing_d / 2;      // ball centre -> bearing centre
seat_d       = bearing_d - 2 * bearing_fit;
seat_depth   = bearing_d - ball_gap;   // from cup inner surface to seat bottom
claw_top     = rim_z + retainer_t + claw_h;
claw_r_top   = sqrt(R_in * R_in - pow(claw_top - zc, 2));           // claw inner radius at its top edge
ball_play    = (claw_top - zc) - sqrt(max(0, R * R - claw_r_top * claw_r_top));  // vertical play before the ball is blocked
radial_ext   = L_pcb * s + (hous_x / 2) * c + (th > 0 ? 0 : 0);   // outward reach of the housing (x), tilted case

// ------------------------------------------------------------------ reporting
echo(str("STACK ball_d=", ball_d));
echo(str("STACK sensor_angle=", sensor_angle));
echo(str("STACK ball_centre_z=", zc));
echo(str("STACK ball_top_above_pcb_top=", zc + R));
echo(str("STACK ball_bottom_z=", zc - R));
echo(str("STACK bearing_contact_z=", zc - R * sin(bearing_elev)));
echo(str("STACK rim_z=", rim_z));
echo(str("STACK claw_top_z=", claw_top));
echo(str("STACK retainer_ball_play=", ball_play));
echo(str("STACK lens_reference_plane_dist=", lens_z));
echo(str("STACK sensor_pcb_plane_dist=", L_pcb));
echo(str("STACK lowest_plastic_z=", zc - drop_housing));
echo(str("STACK lowest_sensor_board_z=", zc - drop_board));
echo(str("STACK depth_below_pcb_bottom=", depth_below_pcb));
echo(str("STACK housing_radial_extent_x=", radial_ext));
echo(str("STACK cup_outer_d=", 2 * R_out));
echo(str("STACK pcb_cutout_d=", pcb_cutout_d));

// ------------------------------------------------------------------ helpers
module at_ball() { translate([0, 0, zc]) children(); }

// local sensor frame: origin at the ball centre, -z along the optical axis towards the sensor
module sensor_frame() {
    at_ball() rotate([0, 0, sensor_az]) rotate([0, th, 0]) children();
}

module radial(az, elev) {   // orient children so +z points from the ball centre outwards
    at_ball() rotate([0, 0, az]) rotate([0, 90 + elev, 0]) children();
}

// ------------------------------------------------------------------ cradle solids
module cup_outer() {
    at_ball() sphere(r = R_out);
    translate([0, 0, -pcb_t - flange_t]) cylinder(r = R_out, h = zc + pcb_t + flange_t);
    // bearing bosses
    for (az = bearing_az) radial(az, bearing_elev)
        translate([0, 0, R_in - 0.5]) cylinder(d = seat_d + 3.2, h = seat_depth + 1.4 + 0.5);
}

module housing_outer() {
    sensor_frame() {
        // from the sensor PCB plane up into the cup wall
        translate([-hous_x / 2, -hous_y / 2, -L_pcb]) cube([hous_x, hous_y, L_pcb - R_in + 1.0]);
    }
}

module flange_outer() {
    translate([0, 0, -pcb_t - flange_t]) cylinder(d = flange_d, h = flange_t);
}

module cradle_cuts() {
    // ball cavity
    at_ball() sphere(r = R_in);
    // everything above the rim
    translate([-100, -100, rim_z]) cube([200, 200, 100]);
    // lens aperture + lens cavity + screw pilots, in the sensor frame
    sensor_frame() {
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
        // everything below the sensor PCB plane (keeps the housing face flat for the board)
        translate([-50, -50, -L_pcb - 50]) cube([100, 100, 50]);
    }
    // bearing seats
    for (az = bearing_az) radial(az, bearing_elev)
        translate([0, 0, R_in - 0.01]) cylinder(d = seat_d, h = seat_depth + 0.01);
    // flange pilot holes
    for (az = flange_hole_az) rotate([0, 0, az]) translate([flange_hole_bcd / 2, 0, -pcb_t - flange_t - 1])
        cylinder(d = flange_pilot_d, h = flange_t + 2);
    // retainer peg holes in the rim
    for (az = retainer_claws) rotate([0, 0, az]) translate([(R_in + R_out) / 2, 0, rim_z - peg_h - 0.2])
        cylinder(d = peg_d + 0.1, h = peg_h + 0.3);
    // main PCB keep-out: nothing of the cradle may live inside the PCB slab outside the cutout
    difference() {
        translate([0, 0, -pcb_t]) cylinder(d = 200, h = pcb_t);
        translate([0, 0, -pcb_t - 0.01]) cylinder(d = pcb_cutout_d - 1.0, h = pcb_t + 0.02);
    }
}

module cradle() {
    difference() {
        union() { cup_outer(); housing_outer(); flange_outer(); }
        cradle_cuts();
    }
}

// ------------------------------------------------------------------ retainer
module retainer() {
    difference() {
        union() {
            // base ring on the rim
            translate([0, 0, rim_z]) cylinder(r = R_out, h = retainer_t);
            // claws
            for (az = retainer_claws) rotate([0, 0, az])
                intersection() {
                    translate([0, 0, rim_z]) cylinder(r = R_out, h = retainer_t + claw_h);
                    translate([0, -claw_w / 2, rim_z]) cube([R_out + 1, claw_w, retainer_t + claw_h]);
                }
            // pegs
            for (az = retainer_claws) rotate([0, 0, az]) translate([(R_in + R_out) / 2, 0, rim_z - peg_h])
                cylinder(d = peg_d, h = peg_h + 0.01);
        }
        at_ball() sphere(r = R_in);                       // concentric with the ball, never touches it
        translate([0, 0, rim_z - 1]) cylinder(r = R_in + 0.2, h = retainer_t + 1.01);  // ring bore
        // chamfer the claw tips so the thumb does not catch
        for (az = retainer_claws) rotate([0, 0, az])
            translate([R_out + 0.3, -claw_w, claw_top]) rotate([0, -45, 0]) cube([3, 2 * claw_w, 3]);
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
        translate([0, 0, -pcb_t - 0.1]) cylinder(d = pcb_cutout_d, h = pcb_t + 0.2);
    }
}

// ------------------------------------------------------------------ 2D cutout for the main PCB
module cutout2d() {
    offset(r = 0.5) projection(cut = true) translate([0, 0, pcb_t / 2]) union() { cradle(); }
    for (az = flange_hole_az) rotate([0, 0, az]) translate([flange_hole_bcd / 2, 0]) circle(d = 2.2);
}

// ------------------------------------------------------------------ dispatch
if (part == "cradle")        cradle();
else if (part == "retainer") retainer();
else if (part == "sensor_dummy") sensor_dummy();
else if (part == "cutout2d") cutout2d();
else if (part == "section") {           // half model for section previews
    difference() {
        union() { cradle(); color("orange") retainer(); ball(); sensor_dummy(); main_pcb_dummy(); }
        translate([-100, 0, -100]) cube([200, 100, 200]);
    }
}
else { cradle(); color("orange") retainer(); ball(); sensor_dummy(); main_pcb_dummy(); }
