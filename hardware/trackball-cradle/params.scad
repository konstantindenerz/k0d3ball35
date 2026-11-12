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
bearing_az      = [60, 180, 300];  // azimuths (deg, layout frame). The sensor window sits at 0 (+x), so
                                   // the bosses stay 60 degrees either side of it and one sits
                                   // straight on the thumb side. STACK window_az echoes the window's
                                   // real azimuth so nothing has to re-derive it from sensor_az.

// ---------------------------------------------------------------- sensor stack (PAW3222 module)
// Since r2.4 the sensor is the ready-made PAW3222 module (sekigon-gonnoc / nogikes-ya, the one
// torabo-tsuki LP uses), tilted beside the ball instead of straight under it.
// Why the tilt needs this module and not our old PMW3610 board: the module's extent in the TILT
// PLANE is what decides. Tilted, one edge of the board swings down and the other swings UP; the
// upper edge has to stay under the cup rim. The PMW3610 is a 16-pin moulded package through a
// 16.96 x 8.60 mm board cutout, so it cannot get narrower than about 13 mm in that plane, and at
// 13 mm the largest legal tilt is 38 deg - which buys 0.06 mm of ball height over no tilt at all.
// The module's 7.4 mm clear it at 65 deg. See spec/08-trackball-module.md.
//
// Module outline from the maker's drawing (github.com/sekigon-gonnoc/small-mouse-sensor-module,
// img/size.png, and the photo img/image.png). Until r2.4b this file carried an unsourced
// "14 x 8 mm with the connector on the back"; the real part differs in every point that matters
// (issues/mech-cradle-real-module.md):
//   - board 13.4 x 7.4 mm; the 7.4 lies in the tilt plane (local x), the 13.4 is tangential
//     (local y, horizontal in the world)
//   - lens body 9.06 x 7.4 mm on the LENS side, the full board width, flush with one short end;
//     the optical centre is 6.79 mm from that end
//   - Hirose FH19C 6-pin 0.5 mm connector on the LENS side too, in the 4.34 mm at the other end;
//     the cable enters it in the board plane through that short end (2.3 mm insertion)
//
// MEASURE THESE. PixArt publishes no assembly drawing for the PAW3222 + PNSR-015-RB3 pair, so
// lens_z, lens_h and the board thickness below are nominal values to be confirmed on the real
// part with the feeler gauge (README, "Test-fit checklist"). The ball height does NOT depend on
// them: at 65 deg the cup floor is the binding term, not the module (STACK drop_cup vs
// drop_board), which tests/test_cradle.py asserts. They only decide whether the module fits.
lens_z          = 2.4;     // ball surface to lens reference plane (the lens face; nominal, PixArt family)
// Correction for the printed stack, in mm. The lens face rests on the floor of its cavity, so the
// printed terms that set the lens distance are that floor and the three bearing seats that hold
// the ball. The seats are the sensitive ones, because they sit 35 degrees below the equator: a
// radial seat error d moves the ball centre by d * cot(35) = 1.43 d. Measure, then reprint with
// lens_shim set: POSITIVE moves the module away from the ball and increases the distance,
// NEGATIVE decreases it. With the tilted module a shim moves it along the optical axis and does
// NOT raise the ball.
lens_shim       = 0;       // measured correction to lens_z; 0 = nominal
lens_h          = 2.5;     // lens face to module board (lens side), nominal
lens_l          = 7.4;     // lens body across the board, local x (maker drawing: the full board width)
lens_w          = 9.06;    // lens body along the board, local y (maker drawing)
lens_far        = 6.79;    // optical centre to the board end the lens body is flush with (maker drawing)
optical_d       = 4.0;     // the window through the CUP WALL, local x (the tilt plane). Sized on the
                           // aperture, not on the lens body: it subtends asin(optical_d/2 / R_in)
                           // either side of the axis, and at 65 deg a wider one reaches the rim.
optical_l       = 8.0;     // and along local y: the lens has two apertures (domes) 0.64 and 3.12 mm from
optical_shift   = 2.0;     // the optical centre towards the lens end (photo img/image.png), so the
                           // window is a slot of optical_d circles optical_l long, its middle shifted
                           // optical_shift towards the lens end: +2 .. -6 mm, the window of the maker's
                           // own case (trackball-module-case/case-12mm-1-Body.step). A centred 6 mm
                           // slot blocked a third of the outer aperture. tests/test_cradle.py traces
                           // rays from both apertures to the ball and checks rim and bearings.
lens_apertures  = [0.64, 3.12];   // aperture centres from the optical centre towards the lens end
aperture_d      = 2.2;     // aperture (dome) diameter, photo
sensor_pcb_l    = 13.4;    // module board along y, tangential (maker drawing)
sensor_pcb_w    = 7.4;     // module board in the tilt plane - the dimension the tilt is limited by
sensor_pcb_t    = 1.0;     // module board thickness, nominal
sensor_pcb_gap  = 0.2;     // clearance per side between the module and the sleeve walls
sensor_pins_h   = 1.2;     // allowance for parts on the back of the board (none known), nominal
conn_zone       = 4.34;    // board end beside the lens body that carries the connector (13.4 - 9.06)
conn_h          = 0.9;     // Hirose FH19C height over the board, nominal
conn_end        = 1;       // +1: connector at local +y, which is layout -y (the key side) for
                           // sensor_az 180, so the cable leaves straight towards J1
ffc_w           = 3.5;     // 6-way 0.5 mm FFC width; the exit in the sleeve wall gets +0.5
sensor_angle    = 65;      // tilt from vertical, towards +x. Largest angle whose optical window
                           // clears the cup rim (6 deg below the equator) and whose upper board
                           // edge stays under the rim. 0 = straight below the ball.
sensor_az       = 180;     // turn of the sensor frame about z. The frame tilts about its local y axis,
                           // which points the optical axis (and the module) at sensor_az + 180, so
                           // 180 leans the module towards layout +x, under the middle-finger column.
                           // There the PCB already ends at y 42.8, 16 mm above the module, so the
                           // sleeve costs no board area; leaning towards +y (r2.4 first cut, 270)
                           // made the case 5 mm deeper. -x is the PCB thumb bridge, -y the keys and J1.

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
housing_wall    = 2.0;     // sleeve wall either side of the 13.4 mm module: sets the width of the body's
                           // tab, 13.4 + 2 x 2 = 17.4 mm (cradle.scad tab_w)
housing_wall_x  = 1.5;     // sleeve wall across the tilt; only the derived sleeve envelope (drop_housing,
                           // sleeve_top_z, housing_radial_extent_x) uses it, the body is cut at the rim
// FFC exit: the cable leaves the module's connector in the board plane, out of the board's
// short end, so the exit is a slot in the sleeve's end wall on the key side (conn_end), open
// towards the rear like the module slot, so the module slides in with the cable plugged. From
// there the cable runs round the cup as a band and lies down on the PCB into J1.

// ---------------------------------------------------------------- rendering
$fn             = 96;
part            = "assembly";  // cradle | assembly | section | floor2d | sensor_dummy | insert_path
