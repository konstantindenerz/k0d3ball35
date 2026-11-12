// k0d3ball35 trackball cradle
//
// A 3D printed holder for a 19.05 mm trackball on three static ceramic bearings, with a
// bought PAW3222 sensor module tilted 65 degrees into a sleeve beside the cup. The cup rim
// stays below the ball equator: the ball rests in the cup by gravity. The optional clip that keeps
// it in when the half is turned over sits on the case's pocket cover (hardware/case, pocket_clip,
// issues/mech-ball-retainer-clip.md); otherwise the case lid covers the ball (issues/mech-case-lid.md).
//
// The module stands on the case floor in a pocket beside the main PCB; the PCB edge has
// an octagonal notch around the cup. 19.05 mm ball only (r2.4 dropped the 25 mm ball and
// the r1 cutout mount).
//
//   part = "cradle"       the printed body: cup and sensor sleeve in one piece
//   part = "assembly"     cradle + ball + sensor dummy + PCB / floor dummies
//   part = "section"      half model for section previews
//   part = "floor2d"      2D footprint of the module on the case floor (export as DXF)
//   part = "sensor_dummy" lens + PCB + pins envelope only
//
// See params.scad for every dimension and README.md for the stack derivation.

include <params.scad>

// ------------------------------------------------------------------ derived values
floor_t_assumed = 2.0;                 // case floor the case screw passes before the skirt
R      = ball_d / 2;
R_in   = R + ball_gap;                 // cup inner radius
R_out  = R_in + wall;                  // cup outer radius
lens_zz = lens_z + lens_shim;          // effective ball surface -> lens reference plane
L_pcb  = R + lens_zz + lens_h;         // ball centre -> sensor PCB (lens side) along the axis
L_low  = L_pcb + sensor_pcb_t + sensor_pins_h;   // ball centre -> lowest point of the sensor board
// Module layout along local y (maker drawing): the optical centre is on the axis (y = 0), the lens
// body is flush with the board end on the -conn_end side, the connector zone fills the other end.
gap    = sensor_pcb_gap;
y_lens_end = -conn_end * lens_far;                         // board end the lens body is flush with
y_conn_end = y_lens_end + conn_end * sensor_pcb_l;          // board end with the connector (cable mouth)
y_split    = y_lens_end + conn_end * lens_w;                // lens body / connector zone boundary
function span(a, b) = [min(a, b), max(a, b)];
board_y = span(y_lens_end, y_conn_end);
lens_y  = span(y_lens_end, y_split);
conn_y  = span(y_split, y_conn_end);
lens_face = L_pcb - lens_h;                                // = R + lens_zz: where the lens face seats
hw     = housing_wall;
hwx    = housing_wall_x;
hous_x = sensor_pcb_w + 2 * hwx;       // sleeve, local x (tilt plane)
hous_y = sensor_pcb_l + 2 * hw;        // sleeve, local y (tangential)
th     = sensor_angle;                 // tilt of the sensor module from vertical
s = sin(th); c = cos(th);

// lowest point below the ball centre, for the sensor board and for the printed housing
drop_board   = L_low * c + (sensor_pcb_w / 2) * s;
drop_housing = L_pcb * c + (hous_x / 2) * s;
drop_cup     = R + cup_floor_t;        // the cup itself needs this much above the floor
drop         = max(drop_board, drop_housing, drop_cup);

// case floor the module stands on
floor_z = -pcb_t - depth_below_pcb;
// ball centre height above the main PCB top
zc = floor_z + drop;

rim_z        = zc - rim_drop;
bear_dist    = R + bearing_d / 2;      // ball centre -> bearing centre
seat_d       = bearing_d - 2 * bearing_fit;
seat_depth   = bearing_d - ball_gap;   // from cup inner surface to seat bottom
radial_ext   = L_pcb * s + (hous_x / 2) * c;                        // outward reach of the housing (x), tilted case
board_z      = zc - L_pcb * c;   // module plane under the ball centre, only meaningful at th = 0
// Upper edge of the module and of the sleeve, in global z. Tilted, one edge swings down
// (drop_board) and the other swings up - and THAT is what limits the angle.
board_top_z  = zc - (L_pcb * c - (sensor_pcb_w / 2) * s);
sleeve_top_z = zc - (L_pcb * c - (hous_x / 2) * s);
// radial reach of the module itself above the main PCB plane: must stay inside the notch
// Three different reaches, and mixing them up is easy. board_reach is the near face's corner.
// module_reach is the absolute far corner including the board thickness - it sits ABOVE the PCB
// slab, so it is not the notch constraint even though it is the biggest number.
// module_slab_reach is the one that matters: how far the module gets while it is inside the PCB
// slab (z from -pcb_t to 0), the only band where it can foul the board.
board_reach  = L_pcb * s + (sensor_pcb_w / 2) * c;
module_reach = (L_pcb + sensor_pcb_t) * s + (sensor_pcb_w / 2) * c;
slab_x_hi    = min(sensor_pcb_w / 2, max(-sensor_pcb_w / 2, ((L_pcb + sensor_pcb_t) * c - zc) / s));
module_slab_reach = (L_pcb + sensor_pcb_t) * s + slab_x_hi * c;
// The sleeve sits BESIDE the cup, not under it, so it may rise to the cup rim.
hous_top     = rim_z;
// Plan of the printed body: the cup circle and a tab as wide as the sleeve (hous_y) towards the
// window, one outline extruded from the floor to the rim. The tab ends at the PCB keep-out (notch
// apothem minus pcb_clear), with the notch octagon's own 45 degree corners, so nothing has to be
// trimmed off afterwards and the body is the same shape above and below the PCB plane.
tab_w        = hous_y;
tab_back     = notch_apothem - pcb_clear;
skirt_z      = floor_z;                                             // bottom of the cylindrical cup skirt
screw_depth  = min(case_screw_len - floor_t_assumed, rim_z - floor_z - 1.0);   // thread length in the skirt
// largest diameter of the cup above the PCB underside: must stay inside the layout's cradle
// clearance circle (trackball.cradle_diameter). The bearing seats end at R_out along their axis,
// 35 degrees below the equator, so they sit inside the cup skirt and need no bosses of their own.
envelope_d   = 2 * R_out;
rim_ch       = rim_chamfer;                         // 45 degree edge break along the top


// ------------------------------------------------------------------ reporting
echo(str("STACK ball_d=", ball_d));
echo(str("STACK sensor_angle=", th));
// The window's real layout azimuth. sensor_frame() turns by sensor_az and then tilts about the
// LOCAL y axis, which tips the optical axis towards local -x: the window lands at sensor_az + 180,
// not at sensor_az. (Until r2.4b this read -sensor_az, which agrees only at 90 and 270.)
// Echoed so tests and the layout do not each re-derive the sign and get it wrong.
win_az = (sensor_az + 180) % 360;
echo(str("STACK window_az=", win_az));
echo(str("STACK ball_centre_z=", zc));
echo(str("STACK ball_top_above_pcb_top=", zc + R));
echo(str("STACK ball_bottom_z=", zc - R));
echo(str("STACK bearing_contact_z=", zc - R * sin(bearing_elev)));
echo(str("STACK rim_z=", rim_z));
echo(str("STACK rim_below_equator=", zc - rim_z));
echo(str("STACK lens_reference_plane_dist=", lens_zz));
echo(str("STACK sensor_pcb_plane_dist=", L_pcb));
echo(str("STACK sensor_pcb_plane_z=", board_z));
echo(str("STACK board_top_z=", board_top_z));
echo(str("STACK sleeve_top_z=", sleeve_top_z));
echo(str("STACK board_reach=", board_reach));
echo(str("STACK module_reach=", module_reach));
echo(str("STACK module_slab_reach=", module_slab_reach));
echo(str("STACK drop_board=", drop_board));
echo(str("STACK drop_housing=", drop_housing));
echo(str("STACK drop_cup=", drop_cup));
echo(str("STACK lowest_plastic_z=", floor_z));
echo(str("STACK lowest_sensor_board_z=", zc - drop_board));
echo(str("STACK floor_z=", floor_z));
echo(str("STACK depth_below_pcb_bottom=", depth_below_pcb));
echo(str("STACK housing_radial_extent_x=", radial_ext));
echo(str("STACK housing_x=", hous_x));
echo(str("STACK housing_y=", hous_y));
echo(str("STACK housing_top_z=", hous_top));
// the real floor footprint (bounding box of plan_2d), across and along the lean
echo(str("STACK footprint_x=", 2 * R_out));
echo(str("STACK footprint_y=", R_out + tab_back));
echo(str("STACK body_back_reach=", tab_back));
echo(str("STACK case_screw_sp=", case_screw_sp));   // case screws, local y axis
echo(str("STACK cup_outer_d=", 2 * R_out));
echo(str("STACK envelope_d_above_pcb=", envelope_d));
echo(str("STACK notch_apothem=", notch_apothem));
echo(str("STACK pcb_cutout_d=", 2 * notch_apothem));

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
// One body, built from one plan (plan_2d): vertical walls from the case floor to the rim and the
// same 45 degree chamfer, rim_ch wide, along the whole top edge, an edge break on cup and tab. Each of
// the two convex pieces gets its chamfer by a hull, and their union leaves a clean valley where
// the tab meets the cup. Both pieces run 1 mm past the floor and the rim and body() cuts them
// flat at both: two solids ending on a shared plane each would leave the exported floor and rim
// T-junctioned where their faceting differs. Everything the module needs is cut in afterwards.
module tab_2d() {
    intersection() {
        rotate([0, 0, win_az]) translate([0, -tab_w / 2]) square([tab_back + 1, tab_w]);
        octagon(tab_back);
    }
}

module plan_2d() { circle(r = R_out); tab_2d(); }

module cup_outer() {
    rotate_extrude($fn = $fn) polygon([[0, floor_z - 1], [R_out, floor_z - 1], [R_out, rim_z - rim_ch],
                                       [R_out - rim_ch - 1, rim_z + 1], [0, rim_z + 1]]);
}

module tab_outer() {
    hull() {
        translate([0, 0, floor_z - 1]) linear_extrude(rim_z - rim_ch - floor_z + 1) tab_2d();
        translate([0, 0, rim_z + 1 - 0.01]) linear_extrude(0.01) offset(delta = -rim_ch - 1) tab_2d();
    }
}

module body() {
    intersection() {
        union() { cup_outer(); tab_outer(); }
        translate([-50, -50, floor_z]) cube([100, 100, rim_z - floor_z]);
    }
}

// Everything the module needs, in the sensor frame: the slot it slides into, the cavity for
// the lens and the chip, the optical path to the ball, and the exit for the FFC.
module sensor_pocket_cuts() {
    bw = sensor_pcb_w + 2 * gap;
    // Optical window through the cup wall, along local -z from the ball centre to the lens face:
    // a slot of optical_d circles, optical_l long along y, so both lens apertures see the ball.
    // Sized on the apertures, not on the lens body: wider in x it would reach the cup rim.
    // (Until r2.4b it was a round hole cut along +z, away from the sensor; tests/test_cradle.py
    // casts rays through the mesh.)
    translate([0, -conn_end * optical_shift, -lens_face - 0.01]) hull()
        for (sy = [-1, 1]) translate([0, sy * (optical_l - optical_d) / 2, 0])
            cylinder(d = optical_d, h = lens_face + 0.02);
    // Lens body cavity, exactly lens_h deep: the lens face rests on its floor, which sets the lens
    // distance directly (the lens is as wide as the board, so there is no shoulder to seat the
    // board on).
    translate([-bw / 2, lens_y[0] - gap, -L_pcb - 0.01])
        cube([bw, lens_y[1] - lens_y[0] + 2 * gap, lens_h + 0.01]);
    // Connector zone: the FH19C stands conn_h on the lens side, 0.3 mm clear of the floor.
    translate([-bw / 2, conn_y[0] - gap, -L_pcb - 0.01])
        cube([bw, conn_y[1] - conn_y[0] + 2 * gap, conn_h + 0.3 + 0.01]);
    // The module slot, open at the back (-z): the module slides in along its axis until the lens
    // face meets the cavity floor. A strip of tape over the opening keeps it there (build guide).
    translate([-bw / 2, board_y[0] - gap, -L_low - 20])
        cube([bw, board_y[1] - board_y[0] + 2 * gap, L_low + 20 - L_pcb + 0.01]);
    // FFC exit: the cable leaves the connector in the board plane out of the board's short end,
    // so the exit is a slot through the sleeve's end wall on the conn_end side, as high as the
    // connector and open to the back, so the module slides in with its cable already plugged.
    ew = ffc_w + 0.5;
    translate([-ew / 2, conn_end > 0 ? y_conn_end - 0.01 : y_conn_end - 20, -L_low - 20])
        cube([ew, 20.01, L_low + 20 - L_pcb + conn_h + 0.3]);
}

module cradle_cuts() {
    // ball cavity
    at_ball() sphere(r = R_in);
    sensor_frame() sensor_pocket_cuts();
    // Case screws: straight up from the floor into the cup skirt.
    // No posts and no holes in the module since r2.4 - the sleeve holds the module.
    for (sy = [-1, 1]) translate([0, sy * case_screw_sp / 2, floor_z - 1])
        cylinder(d = screw_pocket_d, h = 1 + screw_depth);
    // bearing seats
    for (az = bearing_az) radial(az, bearing_elev)
        translate([0, 0, R_in - 0.01]) cylinder(d = seat_d, h = seat_depth + 0.01);
}

module cradle() {
    difference() {
        body();
        cradle_cuts();
    }
}


// ------------------------------------------------------------------ test ball
// Half a ball to print twice and glue, flat face on the bed, until the bought ball is there.
// A piece of 1.75 mm filament in the centre hole lines the halves up. It shows fit, gap and
// retention; the sensor does not track a printed surface like the real ball.
ball_pin_d = 1.9;
ball_pin_depth = 4.0;
module ball_test_half() {
    difference() {
        intersection() { sphere(r = R); translate([-R, -R, 0]) cube([2 * R, 2 * R, R]); }
        translate([0, 0, -0.01]) cylinder(d = ball_pin_d, h = ball_pin_depth + 0.01, $fn = 32);
    }
}

// ------------------------------------------------------------------ dummies for the assembly view
module ball() { at_ball() color("ivory") sphere(r = R); }

module sensor_dummy(ffc = true) {
    sensor_frame() {
        color("gray", 0.6) translate([-lens_l / 2, lens_y[0], -L_pcb]) cube([lens_l, lens_y[1] - lens_y[0], lens_h]);     // lens body
        color("green", 0.7) translate([-sensor_pcb_w / 2, board_y[0], -L_pcb - sensor_pcb_t])
            cube([sensor_pcb_w, board_y[1] - board_y[0], sensor_pcb_t]);                                            // module board
        color("black", 0.7) translate([-3.0, conn_y[0] + 0.2, -L_pcb]) cube([6.0, conn_y[1] - conn_y[0] - 0.2, conn_h]);  // FH19C
        if (ffc) color("white", 0.8) translate([-ffc_w / 2, conn_end > 0 ? y_conn_end - 2.3 : y_conn_end - 3.7, -L_pcb + 0.35])
            cube([ffc_w, 6.0, 0.15]);                                                                               // FFC stub
    }
}

module main_pcb_dummy() {
    color("darkgreen", 0.3) difference() {
        translate([0, 0, -pcb_t]) cylinder(d = 70, h = pcb_t);
        translate([0, 0, -pcb_t - 0.1]) linear_extrude(pcb_t + 0.2) octagon(notch_apothem);
    }
}

module case_floor_dummy() {   // the case floor the module stands on
    color("burlywood", 0.3) translate([-35, -35, floor_z - 1.5]) cube([70, 70, 1.5]);
}

// ------------------------------------------------------------------ 2D exports
// Footprint on the case floor with 0.5 mm clearance: the body's plan (cup plus tab), and the
// two case screw holes. It is the same plan the body is extruded from, so the two cannot
// disagree. No mirror of its own: the print-frame mirror at the bottom of this file applies to it
// like to everything else. A second mirror here cancelled it once in r2.4 and put the sleeve on
// the KEY side of the DXF while the STL had it on the back edge (tests/test_cradle.py compares
// the two).
module floor2d() {
    difference() {
        offset(r = 0.5) plan_2d();
        for (sy = [-1, 1]) translate([0, sy * case_screw_sp / 2]) circle(d = case_screw_d + 0.2);
    }
}

// ------------------------------------------------------------------ dispatch

// The sources work in the layout frame (+x outward, +y towards the user, z up), which is
// left-handed; STL and DXF are read right-handed. The export flips y once so the files are the
// real part, in the print frame: x outward, y away from the user, z up
// (issues/mech-case-stl-mirrored.md). The echoed STACK numbers stay in the layout frame.
module dispatch() {
    if (part == "cradle")        cradle();
    else if (part == "ball_test_half") ball_test_half();
    else if (part == "sensor_dummy") sensor_dummy();
    else if (part == "sensor_module") sensor_dummy(ffc = false);   // ref/sensor-module.stl: the bought module in its place
    else if (part == "floor2d")  floor2d();
    else if (part == "insert_path") {     // must be empty (tests): the module's way in along -z
        intersection() {
            cradle();
            // one hull per box, so the step between lens body and connector is not filled in
            sensor_frame() {
                hull() for (tt = [0, 40]) translate([-sensor_pcb_w / 2, lens_y[0], -L_pcb - sensor_pcb_t - tt])
                    cube([sensor_pcb_w, lens_y[1] - lens_y[0], lens_h + sensor_pcb_t]);
                hull() for (tt = [0, 40]) translate([-sensor_pcb_w / 2, conn_y[0], -L_pcb - sensor_pcb_t - tt])
                    cube([sensor_pcb_w, conn_y[1] - conn_y[0], conn_h + sensor_pcb_t]);
                hull() for (tt = [0, 40]) translate([-ffc_w / 2, conn_end > 0 ? y_conn_end - 2.3 : y_conn_end - 3.7, -L_pcb + 0.35 - tt])
                    cube([ffc_w, 6, 0.15]);
            }
        }
    }
    else if (part == "section") {           // half model for section previews: the y = 0 plane cuts
        difference() {                      // along the tilt plane, the key side (-y) half is removed
            union() { cradle(); ball(); sensor_dummy(); main_pcb_dummy(); case_floor_dummy(); }
            translate([-100, -200, -100]) cube([200, 200, 200]);
        }
    }
    else { cradle(); ball(); sensor_dummy(); main_pcb_dummy(); case_floor_dummy(); }
}

mirror([0, 1, 0]) dispatch();
