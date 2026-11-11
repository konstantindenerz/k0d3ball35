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
sleeve_back     = 1.2;     // printed material behind the module
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
// plastic (the cup skirt runs down to the floor). The two M2 x 10 screws come up from below
// through the case floor straight into that skirt - no posts, no holes in the module, and the
// spacing is unchanged, so the main PCB keeps its case holes. Clear of the bearing bosses.
case_screw_d    = 2.0;     // case screw diameter (M2); the floor DXF gets d + 0.2 clearance holes
case_screw_sp   = 20;      // spacing on the local y axis (layout trackball.case_screw_spacing)
screw_pocket_d  = 1.6;     // pilot for the M2 self-tapping screw in the cup skirt
cable_slot_w    = -1;      // width of the FFC slot in the key-facing (-y) wall; -1 = wall width minus 2 corner posts
corner_post     = 3.0;     // material left at the two -y corners beside the cable slot
post_pilot_d    = 1.6;     // pilot hole for M2 self-tapping screws (use 3.2 for heat-set inserts)

// ---------------------------------------------------------------- cup
// The cup itself has nothing above its rim: the rim stays below the equator all round and
// the ball rests on the bearings by gravity. Keeping it in when the half is lifted or turned
// over is the job of the optional clip-on retainer below, or of the case lid in transport.
wall            = 1.6;     // cup wall thickness
cup_floor_t     = 2.0;     // material under the ball bottom. Since r2.4 the sensor is tilted, so
                           // the sensor stack no longer sets the ball height - this does.
rim_drop        = 1.0;     // cup rim this far below the equator (finger clearance, ball lifts out freely)

// ---------------------------------------------------------------- retainer (optional clip)
// A separate ring that clips onto the cup and carries two claws over the ball's shoulders,
// one on each side of the thumb's approach (issues/mech-ball-retainer-clip.md). The thumb
// comes from -x (layout frame: thumb keys at -171 and 180 degrees from the ball), so the
// claws sit at +-retainer_claw_az measured from +x and nothing of the ring rises above the
// cup rim on the thumb side. Remove it by pinching the two claws and pulling straight up;
// the ball then lifts out as before.
//
// Retention was checked by a configuration-space flood fill of the ball centre against the
// cup and the claws (retention.py, retention.json): with these values the ball stays
// trapped until ball, cup and claws are together about 1 mm looser than nominal. A claw on
// the far (+x) side adds nothing; two claws close to +-90 degrees are what holds.
//
// r2.4 rebuilt the ring around two things the flatter stack took away:
//
//  * the ball dropped 3.15 mm, so the cup's outer wall only stands 3.4 mm above the main PCB
//    top. The old 5.6 mm skirt would have reached 2.2 mm BELOW the board plane, into the
//    annular gap the FFC climbs in, and a skirt short enough to stay above the board is far
//    too short to bend a snap finger in. So the ring grew a collar ABOVE the rim and the
//    fingers are rooted in that instead: the finger is as long as skirt + collar, the tips
//    still stop clear of the board (retainer_tip_clear).
//  * the sensor is a sleeve tilted in BESIDE the cup whose flat top is the rim plane, so it
//    fills the ring's annulus over a sector either side of its azimuth. The skirt is relieved
//    over that sector and the collar carries the claw on that side across it - which is why
//    the collar, not the skirt, is what the +retainer_claw_az claw hangs from. The relieved
//    stretch of the collar is a ~15 mm unsupported ledge, so print the clip with supports
//    under it (it is an optional part; the cradle and the cup need none).
//
// The bearing bosses stopped mattering in the same move: they now top out 1.9 mm below the
// skirt's bottom edge, so the arches the skirt used to need over them (retainer_boss_clear) are
// gone. retention.json still reports the clearance under the name boss_clearance, but the thing
// it measures is the sleeve.
retainer_claw_az   = 80;     // claws at +- this azimuth (deg from +x); the thumb sector stays open
retainer_claw_w    = 6.0;    // claw width between its parallel side faces
retainer_claw_h    = 0.525 * ball_d / 2;  // claw top above the ball centre: 5.0 for the 19.05 mm ball
                             // (about 1.6 mm above the Choc caps), scales with the ball
retainer_claw_t    = 1.2;    // claw shell thickness; its inner face is the cup sphere, ball_gap from the ball
retainer_chamfer   = 0.8;    // 45 degree seat: outer chamfer on the cup rim and the matching cone in the ring
retainer_fit       = 0.2;    // radial clearance between the ring's skirt and the cup's outer wall
retainer_skirt_t   = 1.2;    // skirt wall around the cup, below the rim (and the collar above it)
retainer_tip_clear = 1.0;    // finger tips / skirt bottom this far above the main PCB top (z = 0).
                             // Below the board plane the ring would sit in the 3.5 mm annular gap
                             // between the cup and the PCB notch, which is the FFC's way round to J1.
retainer_collar_h  = 3.0;    // ring wall above the cup rim. Two jobs: it roots the snap fingers high
                             // enough that bending them over the nub stays under 2.5 % strain (the
                             // 2.4 mm of skirt left above the board cannot), and it bridges the sensor
                             // sleeve to carry the +retainer_claw_az claw. Keep it below the claw tops.
retainer_open_az   = 102;    // nothing of the ring above the rim beyond +- this azimuth, so the open
                             // sector is 360 - 2 * 102 = 156 deg, centred on the thumb. The lower bound
                             // is the first snap finger's slits (they need collar on both sides); the
                             // upper bound is the thumb keys, at 171 and 180 deg from the ball.
retainer_sleeve_clear = 0.8; // gap from the ring to the tilted sensor sleeve, radially and above its
                             // top face. Sets both the relieved sector and the collar's ride height
                             // there (retention.json boss_clearance).
retainer_fingers   = [[270, 2.0], [300, 3.0], [330, 3.0], [0, 2.0]];  // [azimuth, width]: snap fingers.
                             // All four live in the arc that has both skirt below the rim and collar
                             // above it; the sleeve's sector has neither. The two wide ones sit in the
                             // middle of that arc, the narrow ones at its ends where there is less room
                             // for their slits. The two widths key the ring, as the positions already do.
                             // THESE FOLLOW sensor_az: the usable arc is whatever the sleeve's sector
                             // leaves, so move them if the sensor's azimuth ever moves. Everything
                             // else about the relief is derived (cradle.scad, ret_sleeve_half).
retainer_finger_t  = 0.8;    // finger thickness (radial), thinner than the skirt so it flexes
retainer_slit      = 0.6;    // slit on each side of a finger
retainer_nub       = 0.45;   // nub height towards the cup; the snap undercut is nub - fit = 0.25
retainer_nub_flat  = 0.3;    // flat tip of the nub
retainer_release   = 30;     // nub top face, degrees from vertical: smaller pulls off easier
retainer_pocket_clear = 0.1; // clearance of the nub in its pocket in the cup wall
with_retainer      = true;   // show the retainer in the assembly and section views
housing_wall    = 2.0;     // walls around the sensor board / lens cavity (y, the key-facing side)
housing_wall_x  = 1.5;     // same on x: 29 mm total, 1 mm narrower than the notch across flats, so
                           // the housing clears the PCB edge when the module is lowered into the pocket
// FFC channel : the cable leaves the sensor connector under the board, turns up
// inside the key-facing wall and climbs past the PCB plane in the gap between the cup and the
// notch, where it folds over the board edge into J1 on the key side of the main PCB.
// cable_ch_x is the local x of the cable, i.e. (J1 x in the layout frame) - (ball centre x).
cable_ch_x      = -7.6;
cable_ch_w      = 6.0;

// ---------------------------------------------------------------- rendering
$fn             = 96;
part            = "assembly";  // cradle | retainer | assembly | section | floor2d | sensor_dummy
