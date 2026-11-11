// k0d3ball35 trackball cradle
//
// A 3D printed holder for a 19.05 mm (or 25 mm) trackball with three static ceramic
// bearings and a PMW3610 / LM18-LSI sensor daughterboard underneath. The cup rim stays
// below the ball equator and the cup has nothing above it: the ball rests in the cup by
// gravity. An optional clip-on retainer (part = "retainer") puts two claws over the ball's
// shoulders, away from the thumb, so the ball stays in when the half is turned over; it
// snaps onto a chamfer and four pockets on the cup (issues/mech-ball-retainer-clip.md).
// Without it the case lid covers the ball in transport (issues/mech-case-lid.md).
//
// The module stands on the case floor in a pocket beside the main PCB; the PCB edge has
// an octagonal notch around the cup. 19.05 mm ball only (r2.4 dropped the 25 mm ball and
// the r1 cutout mount).
//
//   part = "cradle"       the printed cup + housing
//   part = "retainer"     the optional clip-on ring with the two claws
//   part = "assembly"     cradle + retainer + ball + sensor dummy + PCB / floor dummies
//   part = "section"      half model for section previews
//   part = "floor2d"      2D footprint of the module on the case floor (export as DXF)
//   part = "sensor_dummy" lens + PCB + pins envelope only
//
// See params.scad for every dimension and README.md for the stack derivation.

include <params.scad>

// ------------------------------------------------------------------ derived values
floor_t_assumed = 2.0;                 // case floor the M2 x 10 passes before the skirt
R      = ball_d / 2;
R_in   = R + ball_gap;                 // cup inner radius
R_out  = R_in + wall;                  // cup outer radius
lens_zz = lens_z + lens_shim;          // effective ball surface -> lens reference plane
L_pcb  = R + lens_zz + lens_h;         // ball centre -> sensor PCB (lens side) along the axis
L_low  = L_pcb + sensor_pcb_t + sensor_pins_h;   // ball centre -> lowest point of the sensor board
cav_h  = lens_h + 0.4;                 // lens cavity height (lens + 0.4 clearance)
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
boss_len     = seat_depth + 1.4 + 0.5; // bearing boss length along its axis (starts at R_in - 0.5)
boss_r       = (seat_d + 3.2) / 2;
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
// The sleeve sits BESIDE the cup, not under it, so it may rise to the cup rim; the
// "everything above the rim" cut and the PCB keep-out below trim whatever pokes out.
hous_top     = rim_z;
skirt_z      = floor_z;                                             // bottom of the cylindrical cup skirt
screw_depth  = min(10.0 - floor_t_assumed, rim_z - floor_z - 1.0);   // thread length in the skirt
// largest diameter of anything above the PCB underside (cup, bearing bosses):
// must stay inside the layout's cradle clearance circle (trackball.cradle_diameter)
boss_reach   = (R_in - 0.5 + boss_len) * cos(bearing_elev) + boss_r * sin(bearing_elev);
envelope_d   = 2 * max(R_out, boss_reach);
boss_top_z   = zc - (R_in - 0.5 + boss_len) * sin(bearing_elev) + boss_r * cos(bearing_elev);

// retainer (optional clip-on ring), see params.scad
ret_ch       = retainer_chamfer;
ret_fi       = R_out + retainer_fit;                 // inner face of the skirt and the fingers
ret_ro       = ret_fi + retainer_skirt_t;            // outer radius of the ring
ret_top      = zc + retainer_claw_h;                 // claw tops
ret_zb       = retainer_tip_clear;                   // finger tips = skirt bottom = print bed
// The ring, the nubs and the cuts are all modelled 1 mm past the tips and one flat cut at ret_zb
// makes the bottom. Letting each solid end on ret_zb instead left the nub's foot and the skirt's
// with coplanar faces of different extent, which the exported mesh T-junctioned on; the cut also
// guarantees what tests/test_retainer.py asks of the first layer - one plane, nothing below it.
ret_zb_x     = ret_zb - 1;
ret_sd       = 0.05 * sqrt(2);                       // seat cone standoff, see retainer_ring()
ret_cone_z   = rim_z - ret_ch - (ret_fi - R_out - ret_sd);   // where the ring's bore leaves ret_fi
ret_coll     = rim_z + retainer_collar_h;            // top of the collar above the rim
ret_slit_top = ret_coll - 0.8;                       // fingers are free below this: the slits stop
                                                     // 0.8 mm under the collar's top edge, which is
                                                     // the band that roots them
ret_nub_rel  = retainer_nub / tan(retainer_release); // height of the release face
ret_nub_top  = ret_zb + retainer_nub + retainer_nub_flat + ret_nub_rel;
ret_tip_r    = sqrt(R_in * R_in - pow(retainer_claw_h, 2));     // claw inner radius at its top edge
// vertical play of the ball before it touches the claw tips (ball centred)
ret_play     = retainer_claw_h - sqrt(max(0, R * R - ret_tip_r * ret_tip_r));
// claw corner furthest round towards the thumb (side face at the tip radius), in degrees
ret_claw_reach = retainer_claw_az + asin((retainer_claw_w / 2) / ret_tip_r);
// furthest round towards the thumb that ANYTHING of the ring rises above the rim: the claw corner
// or the end of the collar, whichever reaches further. This is what the open sector is measured on.
ret_above_reach = max(ret_claw_reach, retainer_open_az);
// The tilted sensor sleeve stands beside the cup and is clipped flat at the rim plane (hous_top),
// so it fills the ring's annulus over a sector of azimuths and the skirt has to be relieved there.
// Which azimuth: sensor_frame() turns by sensor_az about z and then tilts about the LOCAL y axis,
// which puts the optical axis - and the sleeve - at layout azimuth -sensor_az. The sleeve is
// hous_y / 2 either side of the vertical plane through that axis, so a ring point at radius r is
// clear of it only beyond asin((hous_y / 2 + clearance) / r), worst at the ring's inner face.
ret_sleeve_az   = -sensor_az;
ret_sleeve_half = asin((hous_y / 2 + retainer_sleeve_clear) / ret_fi);

// ------------------------------------------------------------------ reporting
echo(str("STACK ball_d=", ball_d));
echo(str("STACK sensor_angle=", th));
// The window's real layout azimuth. sensor_frame() turns by sensor_az and then tilts about the
// LOCAL y axis, which lands the optical axis at -sensor_az - not at sensor_az, as one would read
// off the parameter. Echoed so tests and the layout do not each re-derive the sign and get it wrong.
echo(str("STACK window_az=", (360 - sensor_az) % 360));
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
echo(str("STACK cable_channel_x=", cable_ch_x));
echo(str("STACK cable_channel_w=", cable_ch_w));
echo(str("STACK housing_y=", hous_y));
echo(str("STACK housing_top_z=", hous_top));
echo(str("STACK footprint_x=", hous_x));
echo(str("STACK footprint_y=", hous_y));
echo(str("STACK case_screw_sp=", case_screw_sp));   // case screws, local y axis
echo(str("STACK cup_outer_d=", 2 * R_out));
echo(str("STACK envelope_d_above_pcb=", envelope_d));
echo(str("STACK notch_apothem=", notch_apothem));
echo(str("STACK pcb_cutout_d=", 2 * notch_apothem));
echo(str("STACK bearing_boss_top_z=", boss_top_z));
echo(str("STACK retainer_claw_az=", retainer_claw_az));
echo(str("STACK retainer_top_z=", ret_top));
echo(str("STACK retainer_top_above_rim=", ret_top - rim_z));
echo(str("STACK retainer_outer_d=", 2 * ret_ro));
echo(str("STACK retainer_bottom_z=", ret_zb));
echo(str("STACK retainer_ball_gap=", ball_gap));
echo(str("STACK retainer_ball_play=", ret_play));
echo(str("STACK retainer_claw_tip_r=", ret_tip_r));
echo(str("STACK retainer_open_deg=", 360 - 2 * ret_above_reach));
echo(str("STACK retainer_collar_top_z=", ret_coll));
echo(str("STACK retainer_sleeve_relief_deg=", 2 * ret_sleeve_half));
echo(str("STACK retainer_snap_undercut=", retainer_nub - retainer_fit));
// bending strain of a snap finger while its nub rides over the cup wall: 1.5 t y / L^2
// (cantilever with a point load at the nub; PETG takes about 4 %, PLA about 2.5 %). L runs from
// the root - the top of the slits, up in the collar - down to the middle of the nub's flat, so
// the collar is what makes the finger long enough to bend at all (params.scad, retainer_collar_h).
echo(str("STACK retainer_finger_strain=",
         1.5 * retainer_finger_t * (retainer_nub - retainer_fit)
         / pow(ret_slit_top - (ret_zb + retainer_nub + retainer_nub_flat / 2), 2)));

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

// Tilted sleeve around the module, clipped flat at the case floor and at the cup rim. The
// clip is what makes the tilt printable: the sleeve stands on the floor on its cut face.
module housing_outer() {
    intersection() {
        sensor_frame()
            translate([-hous_x / 2, -hous_y / 2, -L_low - sleeve_back])
                cube([hous_x, hous_y, L_low + sleeve_back - R_in + 1.0]);
        translate([-200, -200, floor_z]) cube([400, 400, hous_top - floor_z]);
    }
}

// Everything the module needs, in the sensor frame: the slot it slides into, the cavity for
// the lens and the chip, the optical path to the ball, and the exit for the FFC.
module sensor_pocket_cuts() {
    bw = sensor_pcb_w + 2 * sensor_pcb_gap;
    bl = sensor_pcb_l + 2 * sensor_pcb_gap;
    // Optical path through the cup wall: sized on the aperture (optical_d), not on the lens body.
    // The window it opens in the cup subtends asin(optical_d/2 / R_in) around the axis, and with
    // the lens-body width it would reach above the cup rim at this tilt.
    cylinder(d = optical_d, h = L_pcb + 0.01);
    // lens + chip cavity between the module and the cup
    translate([-(lens_l + 1.0) / 2, -(lens_w + 1.0) / 2, -L_pcb - 0.01])
        cube([lens_l + 1.0, lens_w + 1.0, cav_h + 0.01]);
    // the module slot and the room its back-side parts need, open towards -z so it slides in
    translate([-bw / 2, -bl / 2, -L_low - 0.01]) cube([bw, bl, L_low - L_pcb + 0.02]);
    // FFC exit: a notch in the sleeve's local +x wall, which rotate([0,0,sensor_az]) puts on the
    // KEY side (layout -y) for sensor_az = 270 - mind the frame, the STL export flips y again.
    // From the notch the cable climbs the 2.95 mm annular gap between the cup envelope (r 12.05)
    // and the PCB notch (r 15.0) round to J1: the r2.2 mechanism, so the main PCB keeps J1 where
    // it is. The bearing bosses are inside r 12.05, so the gap is clear all the way round.
    translate([bw / 2 - 0.01, -cable_ch_w / 2, -L_low - 0.01])
        cube([hwx + 1.01, cable_ch_w, L_low - L_pcb - sensor_pcb_t + 0.02]);
}

module cradle_cuts() {
    // ball cavity
    at_ball() sphere(r = R_in);
    // everything above the rim
    translate([-100, -100, rim_z]) cube([200, 200, 100]);
    sensor_frame() sensor_pocket_cuts();
    // Case screws: straight up from the floor into the cup skirt, clear of the bearing bosses.
    // No posts and no holes in the module since r2.4 - the sleeve holds the module.
    for (sy = [-1, 1]) translate([0, sy * case_screw_sp / 2, floor_z - 1])
        cylinder(d = screw_pocket_d, h = 1 + screw_depth);
    // FFC channel on from the module towards the keys: the cable turns up outside the sleeve and
    // climbs past the PCB plane in the gap between the cup and the notch (r2.2)
    translate([cable_ch_x - cable_ch_w / 2, -hous_y / 2 - 1, floor_z - 0.01])
        cube([cable_ch_w, hw + 2, hous_top - floor_z + 0.02]);
    // PCB keep-out: nothing above the PCB underside outside the notch (with clearance)
    difference() {
        translate([0, 0, -pcb_t - pcb_clear]) cylinder(d = 200, h = 100);
        translate([0, 0, -pcb_t - pcb_clear - 0.01]) linear_extrude(100.02) octagon(notch_apothem - pcb_clear);
    }
    // bearing seats
    for (az = bearing_az) radial(az, bearing_elev)
        translate([0, 0, R_in - 0.01]) cylinder(d = seat_d, h = seat_depth + 0.01);
    // retainer seat: a 45 degree chamfer on the outer edge of the rim, which the ring sits
    // on and centres itself by, and one pocket per snap finger in the outer wall. Both stay
    // outside the ball side of the rim, so the cup works the same without the retainer.
    rotate_extrude($fn = $fn)
        polygon([[R_out - ret_ch, rim_z + 0.01], [R_out + 1, rim_z + 0.01], [R_out + 1, rim_z - ret_ch - 1]]);
    for (f = retainer_fingers) finger_arc(f[0], f[1] + 2 * 0.3, R_out)
        offset(delta = retainer_pocket_clear) nub_profile(R_out + 1);
}

module cradle() {
    difference() {
        union() { cup_outer(); housing_outer(); }
        cradle_cuts();
    }
}

// ------------------------------------------------------------------ retainer (optional clip)
// r-z profile of a snap nub on the inner face of a finger: 45 degree lead-in from the tip
// (it slides down the rim chamfer and the cup wall), a short flat, then the release face at
// retainer_release degrees from vertical that pulls out of the pocket when the ring is lifted.
// It runs down to ret_zb_x, past the tip, and retainer()'s flat cut takes the tail off again.
module nub_profile(r_back) {
    polygon([[r_back, ret_zb_x], [ret_fi, ret_zb_x], [ret_fi, ret_zb],
             [ret_fi - retainer_nub, ret_zb + retainer_nub],
             [ret_fi - retainer_nub, ret_zb + retainer_nub + retainer_nub_flat],
             [ret_fi, ret_nub_top], [r_back, ret_nub_top]]);
}

// children (an r-z profile) swept over the arc of a finger `width` wide at radius r_ref
module finger_arc(az, width, r_ref) {
    half = (width / 2) / r_ref * 180 / PI;
    rotate([0, 0, az - half]) rotate_extrude(angle = 2 * half, $fn = $fn) children();
}

module retainer_claw(az) {
    w = retainer_claw_w;
    intersection() {
        difference() {
            union() {
                at_ball() sphere(r = R_in + retainer_claw_t);
                // Back of the claw: a wall up the inside of the collar, then a 45 degree taper in
                // to the ball so the claw prints without support. The wall is what ties the claw
                // into the collar, and on the sensor side that is the ONLY thing holding it -
                // there is no skirt under that claw (params.scad). It runs 0.3 mm inside the
                // ring's outer face and breaks into the taper 0.5 mm below the collar's top edge:
                // either surface laid exactly in one of the ring's own would leave the exported
                // mesh with T-junctions.
                translate([0, 0, rim_z]) cylinder(h = ret_coll - 0.5 - rim_z, r = ret_ro - 0.3);
                translate([0, 0, ret_coll - 0.5]) cylinder(h = ret_ro - 0.3 - R_in, r1 = ret_ro - 0.3, r2 = R_in);
            }
            // The cup's inner surface, carried on DOWNWARDS as a cylinder below the ball's equator
            // instead of following the sphere back in. A face that leans in under the equator moves
            // towards the ball as the ring is lifted straight up and would brush it on the way off,
            // dragging the ball out of the cup with the ring; against the cylinder every point of
            // the claw only ever moves away (retention.py pull_off_min_gap,
            // issues/mech-ball-retainer-clip.md). Hulled rather than unioned: the cylinder's top
            // rim lies exactly on the sphere, and a boolean between tangent surfaces comes out
            // degenerate - the hull of the two convex solids is the same shape and is clean.
            hull() {
                at_ball() sphere(r = R_in);
                translate([0, 0, zc - 20]) cylinder(r = R_in, h = 20);
            }
            // Underside: the rim's 45 degree chamfer carried on inwards and upwards as one cone,
            // which leaves the claw 0.2 mm clear of the chamfer and of the flat of the rim all the
            // way in. One cone and not a flat plus a cone: the flat used to end 0.03 mm outside
            // the collar's bore, and that sliver of a face came out of the exporter degenerate.
            cone_r = R_out - ret_ch + 0.1;
            translate([0, 0, rim_z + 0.2 - 30]) cylinder(h = 30 + cone_r, r1 = cone_r + 30, r2 = 0);
        }
        rotate([0, 0, az]) translate([0, -w / 2, rim_z]) cube([ret_ro + 1, w, ret_top - rim_z]);
    }
}

// The arc above the rim that the collar is taken BACK from, so the thumb's approach stays open
// (params.scad, retainer_open_az). It is one cut on the swept ring rather than the ring being
// swept as two arcs: a partial sweep meets a full one on faces whose facet corners do not line
// up, and the exported mesh then comes out with T-junctions. The sector spans
// 360 - 2 * retainer_open_az, which is under 180 degrees, so it is the intersection of two half
// spaces. Its floor sits 0.01 mm under the rim so that it does not land exactly in the plane of
// the ring's own top edge, which would be a degenerate boolean; all that costs is 0.01 mm off the
// seat cone on the thumb side.
module retainer_open_sector() {
    intersection() {
        translate([0, 0, rim_z - 0.01])
            cylinder(r = ret_ro + 2, h = ret_coll - rim_z + 2, $fn = $fn);
        rotate([0, 0, retainer_open_az])  translate([-100, 0, -100])    cube([200, 200, 200]);
        rotate([0, 0, -retainer_open_az]) translate([-100, -200, -100]) cube([200, 200, 200]);
    }
}

// The ring, in one sweep: the skirt down the cup's outer wall to the finger tips, the seat cone
// that drops onto the rim chamfer, and the collar carried on above the rim - its inner face flush
// with the cone's top edge, so the ring has no ledge sitting over the rim and its bore still
// clears the ball. The cone stands 0.05 mm off the chamfer along its normal so the two facetted
// surfaces do not overlap in the model; the real ring settles onto the chamfer.
module retainer_ring() {
    difference() {
        rotate_extrude($fn = $fn) polygon([
            [R_out - ret_ch + ret_sd, rim_z], [R_out - ret_ch + ret_sd, ret_coll], [ret_ro, ret_coll],
            [ret_ro, ret_zb_x], [ret_fi, ret_zb_x],
            [ret_fi, ret_cone_z], [R_out + ret_sd, rim_z - ret_ch]]);
        retainer_open_sector();
    }
}

module retainer() {
    // One flat cut makes the bottom; see ret_zb_x for why the solids all run past it.
    intersection() {
        translate([-100, -100, ret_zb]) cube([200, 200, 200]);
        union() {
            difference() {
                union() {
                    retainer_ring();
                    for (s = [-1, 1]) retainer_claw(s * retainer_claw_az);
                }
                for (f = retainer_fingers) {
                    a = f[0]; w = f[1];
                    // two slits free the finger up to ret_slit_top ...
                    for (s = [-1, 1]) rotate([0, 0, a + s * ((w + retainer_slit) / 2) / ret_fi * 180 / PI])
                        translate([ret_fi - 1, -retainer_slit / 2, ret_zb_x - 1])
                            cube([retainer_skirt_t + 2, retainer_slit, ret_slit_top - ret_zb_x + 1]);
                    // ... and it is thinner than the skirt, so it flexes outwards
                    finger_arc(a, w + 0.02, ret_fi)
                        translate([ret_fi + retainer_finger_t, ret_zb_x - 1])
                            square([retainer_skirt_t, ret_slit_top - ret_zb_x + 1]);
                    // The seat cone and the collar's inner shoulder are cleared off the finger:
                    // left in, they would stiffen its free length by about a factor of ten and
                    // ride on the rim chamfer as it flexes out, so a finger's inner face is the
                    // plain cylinder ret_fi over its whole length and the strain echoed above
                    // means what it says. The rest of the arc keeps the cone, and that is what
                    // seats and centres the ring. The cut starts half a millimetre below
                    // ret_cone_z, where the ring's bore leaves ret_fi: taken any lower it would
                    // run its own wall down the bore as far as the flat cut, and there the two
                    // surfaces come out of different sweeps whose facet corners miss each other.
                    finger_arc(a, w + 0.02, ret_fi)
                        translate([ret_fi - 2, ret_cone_z - 0.5])
                            square([2, ret_slit_top - ret_cone_z + 0.5]);
                }
                // Relief for the tilted sensor sleeve: over its sector the sleeve fills the whole
                // annulus the skirt would want, right up to the rim plane, so the ring is simply
                // absent below rim_z + retainer_sleeve_clear there and the collar crosses the gap.
                rotate([0, 0, ret_sleeve_az - ret_sleeve_half])
                    rotate_extrude(angle = 2 * ret_sleeve_half, $fn = $fn)
                        polygon([[ret_fi - 1, ret_zb_x - 1], [ret_ro + 1, ret_zb_x - 1],
                                 [ret_ro + 1, rim_z + retainer_sleeve_clear],
                                 [ret_fi - 1, rim_z + retainer_sleeve_clear]]);
            }
            // snap nubs on the fingers
            for (f = retainer_fingers) finger_arc(f[0], f[1], ret_fi) nub_profile(ret_fi + retainer_finger_t / 2);
        }
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
        translate([0, 0, -pcb_t - 0.1]) linear_extrude(pcb_t + 0.2) octagon(notch_apothem);
    }
}

module case_floor_dummy() {   // the case floor the module stands on
    color("burlywood", 0.3) translate([-35, -35, floor_z - 1.5]) cube([70, 70, 1.5]);
}

// ------------------------------------------------------------------ 2D exports
// Footprint on the case floor with 0.5 mm clearance: the cup skirt plus the tilted sleeve
// where it meets the floor, and the two case screw holes.
module floor2d() {
    difference() {
        offset(r = 0.5) union() {
            circle(r = R_out);
            // The sleeve's footprint is taken from the 3D part by sectioning it just above the
            // floor, not from a formula. Writing it out by hand got it wrong twice in r2.4: once
            // by ignoring sensor_az, and once by using the UNCLIPPED sleeve, which reached 21.4 mm
            // from the axis instead of the real 14.3 and so blew up the case's pocket well.
            // No mirror of its own: the print-frame mirror at the bottom of this file applies to
            // the projection like to everything else. A second mirror here cancelled it once in
            // r2.4 and put the sleeve on the KEY side of the DXF while the STL had it on the
            // back edge (tests/test_cradle.py compares the two).
            projection(cut = true) translate([0, 0, -floor_z - 0.05]) housing_outer();
        }
        for (sy = [-1, 1]) translate([0, sy * case_screw_sp / 2]) circle(d = case_screw_d + 0.2);
    }
}

// ------------------------------------------------------------------ dispatch
module retainer_view() { if (with_retainer) color("darkorange") retainer(); }

// The sources work in the layout frame (+x outward, +y towards the user, z up), which is
// left-handed; STL and DXF are read right-handed. The export flips y once so the files are the
// real part, in the print frame: x outward, y away from the user, z up
// (issues/mech-case-stl-mirrored.md). The echoed STACK numbers stay in the layout frame.
module dispatch() {
    if (part == "cradle")        cradle();
    else if (part == "retainer") retainer();
    else if (part == "clash")    intersection() { cradle(); retainer(); }   // must be empty (tests)
    else if (part == "sensor_dummy") sensor_dummy();
    else if (part == "floor2d")  floor2d();
    else if (part == "section") {           // half model for section previews: the x = 0 plane cuts
        difference() {                      // through both claws, the thumb (-x) half is removed
            union() { cradle(); retainer_view(); ball(); sensor_dummy(); main_pcb_dummy(); case_floor_dummy(); }
            translate([-200, -100, -100]) cube([200, 200, 200]);
        }
    }
    else { cradle(); retainer_view(); ball(); sensor_dummy(); main_pcb_dummy(); case_floor_dummy(); }
}

mirror([0, 1, 0]) dispatch();
