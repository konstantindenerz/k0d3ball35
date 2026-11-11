// k0d3ball35 trackball cradle - parameters
// All dimensions in mm. Coordinate system: z up, z = 0 is the TOP surface of the
// main PCB, the ball centre is on the z axis. +x points outward (towards the pinky
// side of the right half), +y points towards the user.
//
// Override on the command line, e.g.
//   openscad -D part=\"cradle\" -o cradle-19mm-pocket.stl cradle.scad

// ---------------------------------------------------------------- mounting
// One mount, one ball size. The module stands on the case floor in a pocket BESIDE the PCB
// (the PCB edge has an octagonal notch around it). The housing walls reach down to the floor,
// the case screws come up through the floor into the housing bosses; the PCB is not touched.
// The r1 cutout mount (cup through a round PCB cutout, flange under the board) and the 25 mm
// ball were dropped in r2.4 - the project supports 19.05 mm only.

// ---------------------------------------------------------------- ball & bearings
ball_d          = 19.05;   // trackball diameter, 3/4 inch POM. The only supported size.
ball_gap        = 0.4;     // radial clearance between ball and cup wall
bearing_d       = 2.0;     // ZrO2 / Si3N4 ceramic ball diameter
bearing_fit     = 0.05;    // press-fit interference per side (seat = bearing_d - 2*fit)
bearing_depth   = 0.6;     // how far the bearing centre sits behind the cup inner surface
bearing_elev    = 35;      // degrees below the equator where the bearings touch the ball
bearing_az      = [30, 150, 270];  // azimuths (deg). Rotated 30 deg in r2.4 so the sensor window is
                                   // free of bearing bosses. CAREFUL with the sign: sensor_frame()
                                   // turns by sensor_az and then tilts about the LOCAL y axis, so
                                   // the window ends up at layout azimuth -sensor_az = 90, not at
                                   // sensor_az. A first attempt put the bosses at [90, 210, 330]
                                   // and dropped a bearing seat straight into the window; STACK
                                   // window_az echoes the real value so nothing has to re-derive it.

// ---------------------------------------------------------------- sensor stack (PAW3222 module)
// Since r2.4 the sensor is the ready-made 14 x 8 mm PAW3222 module (sekigon-gonnoc /
// nogikes-ya, as used in torabo-tsuki LP), tilted beside the ball instead of straight under it.
// Why the tilt needs this module and not our old PMW3610 board: the module's extent in the TILT
// PLANE is what decides. Tilted, one edge of the board swings down and the other swings UP; the
// upper edge has to stay under the cup rim. The PMW3610 is a 16-pin moulded package through a
// 16.96 x 8.60 mm board cutout, so it cannot get narrower than about 13 mm in that plane, and at
// 13 mm the largest legal tilt is 38 deg - which buys 0.06 mm of ball height over no tilt at all.
// The module's 8 mm clear it at 65 deg. See spec/08-trackball-module.md.
//
// MEASURE THESE. PixArt publishes no assembly drawing for the PAW3222 + PNSR-015-RB3 pair, so
// lens_z, lens_h and the module thickness below are nominal values to be confirmed on the real
// part with the feeler gauge (README, "Test-fit checklist"). The ball height does NOT depend on
// them: at 65 deg the cup floor is the binding term, not the module (STACK drop_cup vs
// drop_board), which tests/test_cradle.py asserts. They only decide whether the module fits.
lens_z          = 2.4;     // ball surface to lens reference plane (nominal, PixArt family)
// Correction for the printed stack, in mm. Every term that sets the lens distance is printed: the
// housing face the lens seats on, and the three bearing seats that hold the ball. The seats are
// the sensitive ones, because they sit 35 degrees below the equator: a radial seat error d moves
// the ball centre by d * cot(35) = 1.43 d. Measure, then reprint with lens_shim set: POSITIVE
// moves the module away from the ball and increases the distance, NEGATIVE decreases it.
// With the tilted module a shim moves it along the optical axis and does NOT raise the ball
// (with the old vertical sensor it did, because the module stood under the ball on the floor).
lens_shim       = 0;       // measured correction to lens_z; 0 = nominal
lens_h          = 2.5;     // lens reference plane to module board (lens side), nominal
lens_l          = 6.0;     // PNSR-015-RB3 body length (cavity gets +1.0 clearance), nominal
optical_d       = 4.0;     // the hole through the CUP WALL, sized on the optical aperture and not
                           // on the lens body: the window subtends asin(optical_d/2 / R_in) either
                           // side of the axis, and at 65 deg the lens-body width would reach above
                           // the cup rim. tests/test_cradle.py checks it against rim and bearings.
lens_w          = 5.0;     // PNSR-015-RB3 body width, nominal
sensor_pcb_l    = 14;      // module length, tangential to the tilt (the 14 of 14 x 8)
sensor_pcb_w    = 8;       // module width, IN the tilt plane - the dimension the tilt is limited by
sensor_pcb_t    = 1.0;     // module board thickness, nominal
sensor_pcb_gap  = 0.2;     // clearance per side between the module and the sleeve walls
sensor_pins_h   = 1.2;     // tallest part on the back: the 6-pin 0.5 mm FPC connector, nominal
sensor_angle    = 65;      // tilt from vertical, towards +x. Largest angle whose optical window
                           // clears the cup rim (6 deg below the equator) and whose upper board
                           // edge stays under the rim. 0 = straight below the ball.
sensor_az       = 270;     // azimuth of the tilt direction: the module leans towards +y, the back edge.
                           // NOTE the frame: STACK values and bearing_az are layout frame, but the STL
                           // export flips y (cradle.scad bottom), so +y here is -y in the printed part.
                           // -x is blocked by the PCB thumb bridge, +x and -y by the keys and J1, and
                           // the other azimuths by a bearing boss. bearing_az keeps 270 free.

// ---------------------------------------------------------------- main PCB and case interface
pcb_t           = 1.6;     // main PCB thickness
depth_below_pcb = 5.5;    // case floor below the main PCB underside. Set by the battery well, not by the sensor (r2.4)
pcb_clear       = 0.3;     // nothing of the module closer than this to the PCB underside
notch_apothem   = 15.5;    // PCB notch, regular octagon apothem
                           // (layout trackball.cradle_diameter / 2 + notch_clearance)
// Case screws: since r2.4 the module sits beside the ball, so the floor under the ball is free
// plastic (the cup skirt runs down to the floor). The two M2 x 8 screws come up from below
// through the case floor straight into that skirt - no posts, no holes in the module, and the
// spacing is unchanged, so the main PCB keeps its case holes. Clear of the bearing bosses.
case_screw_d    = 2.0;     // case screw diameter (M2); the floor DXF gets d + 0.2 clearance holes
case_screw_len  = 8;       // M2 x 8: a 10 mm screw ended 0.9 mm over the PCB plane, where the
                           // cup is only 9.28 mm in radius, and its thread broke into the cup
case_screw_sp   = 20;      // spacing on the local y axis (layout trackball.case_screw_spacing)
screw_pocket_d  = 1.6;     // pilot for the M2 self-tapping screw in the cup skirt
cable_slot_w    = -1;      // width of the FFC slot in the key-facing (-y) wall; -1 = wall width minus 2 corner posts
corner_post     = 3.0;     // material left at the two -y corners beside the cable slot
post_pilot_d    = 1.6;     // pilot hole for M2 self-tapping screws (use 3.2 for heat-set inserts)

// ---------------------------------------------------------------- cup
// The cup itself has nothing above its rim: the rim stays below the equator all round and
// the ball rests on the bearings by gravity. Keeping it in when the half is lifted or turned
// over is the job of the optional clip on the case's pocket cover, or of the case lid in transport.
wall            = 1.6;     // cup wall thickness
cup_floor_t     = 2.0;     // material under the ball bottom. Since r2.4 the sensor is tilted, so
                           // the sensor stack no longer sets the ball height - this does.
rim_drop        = 1.0;     // cup rim this far below the equator (finger clearance, ball lifts out freely)

// Keeping the ball in when the half is turned over is the job of the optional clip on the case's
// pocket cover (hardware/case, pocket_clip) or of the lid in transport; the cradle has nothing for it.
rim_chamfer     = 0.8;     // 45 degree edge break along the top of cup and tab
housing_wall    = 2.0;     // sleeve wall either side of the 14 mm module: sets the width of the body's
                           // tab, 14 + 2 x 2 = 18 mm (cradle.scad tab_w)
housing_wall_x  = 1.5;     // sleeve wall across the tilt; only the derived sleeve envelope (drop_housing,
                           // sleeve_top_z, housing_radial_extent_x) uses it, the body is cut at the rim
// FFC exit: a notch in the sleeve wall under the module's connector. From there the cable
// climbs past the PCB plane in the gap between the cup and the notch, runs round the cup and
// folds over the board edge into J1 on the key side of the main PCB.
ffc_exit_w      = 6.0;

// ---------------------------------------------------------------- rendering
$fn             = 96;
part            = "assembly";  // cradle | assembly | section | floor2d | sensor_dummy | insert_path
