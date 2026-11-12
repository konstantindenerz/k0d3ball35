// k0d3ball35 printed case - parameters
// All dimensions in mm. Frame: x outward (towards the pinky), y towards the user, origin at
// the middle-column top key, z up with z = 0 the TOP surface of the main PCB (1.6 thick).
// The frame is handedness-neutral; the left half is mirrored once in case.scad.
//
// Override on the command line, e.g.
//   openscad --backend manifold -D half=\"left\" -D part=\"tray\" -o tray-left.stl case.scad
// Every z value below is derived here, nothing is hard-coded in the modules.

// ---------------------------------------------------------------- selection
half            = "right";     // "left" | "right"
part            = "assembly";  // tray | box_cap | lid | lid_outer | lid_inner | lid_folded | pocket_test | assembly | section | floor2d
mirror_left     = true;        // mirror x once at the top level for the left half (physical part)

// ---------------------------------------------------------------- PCB and walls
pcb_t           = 1.6;
pcb_clear       = 0.2;         // gap between the PCB edge and the cavity wall
// Broken edges. Both halves print with their large flat face on the bed - the tray floor down,
// the lid roof down - and that first layer squashes out by a tenth or two (elephant's foot).
// A 45 degree taper there keeps the part sitting flat and takes the sharp edge off the one that
// rides on the desk. The rim gets a smaller one: it is what the hand touches when the lid is off
// and what meets the lid skirt when it is on, where it reads as a shadow line instead of a seam.
// The vertical corners stay sharp: the nozzle rounds them to about 0.2 mm anyway and the angular
// outline is the point (corner_radius 0 in the layout file).
edge_chamfer    = 0.5;         // tray bottom and lid roof, the two first layers
rim_chamfer     = 0.3;         // top outer edge of the tray rim
chamfer_step    = 0.1;         // a taper is stepped this finely, well under one print layer
wall            = 3.0;         // case wall outside the PCB cavity
under_pcb_clear = 2.1;         // cavity under the key area: hot-swap sockets 1.85 + 0.25 air. The floor
                               // is the anvil under the sockets: the switches go in with the PCB
                               // already screwed down (the guard lies under their flanges), so no
                               // finger can support a socket from below. With 3.0 mm the solder
                               // joints took the whole insertion force.
rim_z           = 5.0;         // top of the tray walls (flush with the Choc keycap skirts)
pocket_rim_drop = 0.5;         // the pocket wall stops this far below the cup rim, so the thumb
                               // reaches the ball at its equator instead of over a lip. Since r2.4
                               // the ball sits low enough that rim_z would otherwise be above it.

// ---------------------------------------------------------------- floors
well_floor_z    = -8.1;        // battery well floor: 6.5 under the PCB underside. Socket solder joints
                               // 0.4 + Kapton 0.1 + LP552035 5.7 mm (datasheet maximum) + 0.3 for the
                               // cell to breathe. Was 6.0, which the old sum (0.1 + 0.25 + 5.7 + 0.1 =
                               // 6.15) already overran; a pouch cell must never be clamped.
pocket_floor_z  = -7.1;        // cradle floor, cradle stack.json floor_z. Since r2.4 the sensor is
                               // tilted beside the ball, so the pocket no longer sets the case depth.
floor_t         = 2.0;         // floor under the pocket; the underside is flat everywhere
well_floor_t    = 1.5;         // floor under the battery well. Thinner than floor_t so the deeper well
                               // adds no height; the two foot recesses under it keep 0.7 mm of skin.
floor_z_key     = -pcb_t - under_pcb_clear;          // -3.7
// One flat underside for the whole half: the deepest well sets it. The battery well reaches
// -8.1 over a 1.5 mm floor and the pocket -7.1 over 2.5 mm, which is what the countersunk
// cradle screws need (case_screw_floor_left in case.scad).
base_z          = min(well_floor_z - well_floor_t, pocket_floor_z - floor_t);   // -9.6

// ---------------------------------------------------------------- PCB fastening
// Default: M2 heat-set inserts (brass, M2 x 3 mm, OD about 3.5) in the standoffs and the cap
// bosses, M2 x 5 machine screws from the top (head max 3.5 mm, under the keycaps). M2 x 6
// bottoms out in the cap bosses, so the build uses one length everywhere: x 5.
// "pilot": 1.6 mm pilots for M2 self-tapping screws instead.
pcb_screws      = "insert";    // "insert" | "pilot"
insert_hole_d   = 3.2;
insert_depth    = 4.0;         // cap bosses: deeper would break through the boss chamfer
standoff_hole_depth = 4.8;     // PCB standoffs: M2 x 5 ends at -5.0, the hole at -6.4 (it runs on into the floor)
standoff_d      = 5.6;         // 1.2 mm around the insert hole; 6.0 touched the switch pegs and sockets (geometry.py STANDOFF_D)
standoff_pilot_d = 1.6;        // only used for pcb_screws == "pilot"
standoff_h      = -pcb_t - floor_z_key;              // 2.1: most of the insert sits in the solid floor
screw_hole_d    = (pcb_screws == "insert") ? insert_hole_d : standoff_pilot_d;
screw_hole_depth = (pcb_screws == "insert") ? insert_depth : 6.0;          // cap bosses
pcb_hole_depth   = (pcb_screws == "insert") ? standoff_hole_depth : 6.0;   // PCB standoffs
min_floor_under_insert = 1.5;

// ---------------------------------------------------------------- controller box
controller_box  = true;
ctrl_top_z      = 5.7;         // 2.5 mm sockets + 1.6 mm PCB + 1.6 mm USB-C shell
box_clear       = 1.0;         // roof clearance over the controller
box_roof_t      = 2.0;
box_roof_under_z = ctrl_top_z + box_clear;           // 6.7
box_top_z       = box_roof_under_z + box_roof_t;     // 8.7
box_inner_x     = -45.5;       // key-side wall of the box (the inner column caps end at -44.75)
box_skirt_t     = 2.0;         // cap skirt walls (key side and thumb side), inside the box rectangle
box_skirt_gap   = 0.3;         // skirt stops this above the PCB top, or above the PCB guard (common.scad box_skirt_z)
box_rebate      = 2.0;         // inner part of the tall walls lowered to box_roof_under_z for the cap plate
box_fit         = 0.15;        // clearance between the cap plate and the rebate
boss_in         = 0.5;         // boss screw axis this far inside the wall's inner face
boss_skin       = 1.4;         // material around the insert hole
// The receptacle (8.94 x 3.26) sits 1.7 mm behind the outer wall face, so the plug's overmold has
// to enter the opening or the plug does not seat. USB Type-C allows an overmold of 12.35 x 6.5 mm;
// the opening is that plus 0.3 mm all round, centred on the receptacle. It used to end at the cap
// plate (5.8 tall, off-centre), which admitted overmolds up to 5.3 mm only.
usb_shell_h     = 3.26;        // receptacle shell height; its top is ctrl_top_z
usb_cut         = [13.0, 7.1]; // width, height of the opening
usb_z0          = ctrl_top_z - usb_shell_h / 2 - usb_cut[1] / 2;   // 0.52
usb_z1          = usb_z0 + usb_cut[1];                             // 7.62, above the cap plate underside
usb_face_in     = 0.6;         // receptacle face this far outside the controller rectangle (controller_dummy)
switch_slot     = [7, 3.0];    // slide switch lever: width along the wall, height under the PCB
reset_hole_d    = 2.0;         // pin hole through the inner wall onto the reset button's side plunger
reset_plunger_z = -pcb_t - 0.7; // plunger axis: half of the 1.35 mm EVQ-P7A body below the PCB underside
led_window      = [3, 3];      // width along the wall, height; in the inner (-x) wall
led_offset_y    = 8.0;         // from the controller board's USB end
led_z           = 3.5;         // bottom of the window

// ---------------------------------------------------------------- owner wordmark
// Grid and rectangles in logo_data.scad (scripts/gen_logo.py). The relief is engraved, not
// raised: the box cap prints with the engraved face on the bed (so would the tray floor if
// logo_on_floor is set). Grooves are one cell wide, so nothing bridges further than logo_cell.
logo_on_cap     = true;
logo_on_floor   = false;      // the floor stays plain (2026-11-07); true engraves it like the cap
logo_invert     = false;      // true: engrave the field instead, leaving the lines proud of it
logo_depth      = 0.6;        // 3 layers at 0.2
logo_cell       = 1.0;        // stroke width on the cap; the min printable feature
logo_stretch    = 1.5;        // cell height / cell width (1.524 in the artwork)
logo_cap_pos    = [-59.525, 21.9];   // centre of the cap plate
logo_floor_cell = 0.9;        // stroke width on the case floor
logo_floor_pos  = [0, 25.5];  // flat floor between the feet, under the key area
logo_floor_rot  = 90;         // the wordmark lies along the board on the floor

// ---------------------------------------------------------------- magnets and feet
// Magnets only hold the lid-as-foot: four in the tray floor (from below) and four in the roof
// of the outer lid plate (from the roof underside, closed by magnet_skin on top). The lid on
// top holds by its lip.
magnet_d        = 6.2;         // 6 x 2 mm neodymium discs
magnet_h        = 2.2;
magnet_skin     = 0.6;         // roof left above the lid magnets (lid_roof_t - magnet_h - magnet_pocket_extra)
magnet_pocket_extra = 0.2;     // pocket depth = magnet_h + this (glue film)
foot_d          = 10.5;        // rubber feet recess
foot_h          = 1.0;         // rubber foot thickness (spec/03-bom.md)
foot_recess     = 0.8;         // 1 mm feet stand 0.2 mm proud: flush would not grip (r2.4)

// ---------------------------------------------------------------- lid
// Two plates per half joined by a pin hinge along x = hinge_x (data.scad): the outer plate
// (pinky side, carries the ball window and the four roof magnets) and the inner plate
// (controller and thumb side). Closed it is the transport cover; folded it goes under the half
// shifted by foot_dx, the outer plate roof-up under the controller half on the floor magnets
// and the inner plate as the kickstand beyond the inner edge. See spec/11-case.md section 7.
cap_top_z       = 11.0;        // Choc V1 keycap top
lid_clear       = 3.5;         // roof underside over the caps; also room for the hinge strip. Since
                               // r2.4 the ball top (13.95) sits UNDER the roof underside (14.5), so
                               // there is no ball window any more and both halves get the same lid.
lid_roof_t      = 3.0;         // takes the 2.4 mm magnet pockets plus the 0.6 mm skin
lid_lip_t       = 1.0;         // inner lip that holds the lid on the tray by friction
lid_lip_depth   = 3.0;         // how far the lip reaches into the tray below the rim
lid_fit         = 0.15;        // clearance between the lip and the inner wall face
lid_lip_chamfer = 0.5;         // lead-in on the lower outer edge of the lip
lid_lip_steps   = 5;
lid_box_clear   = 0.3;         // lid skirt around the controller box walls
cap_size        = [17.5, 16.5]; // Choc 1u keycap footprint (layout yaml `keycap`)
lid_cap_clear   = 0.5;         // the lip keeps this far from every keycap. Along the rows the caps
                               // end only 0.5 mm inside the PCB edge (0.7 from the wall face), so
                               // no lip fits there: it stands on the column sides, the step faces
                               // and the outer edge, where the caps are 1.6 mm inside.
lid_lip_min     = 0.8;         // lip pieces thinner than two perimeters are dropped

// ---------------------------------------------------------------- lid hinge and tenting foot
tent_deg        = 18;          // tilt of the half on the folded lid. 15 no longer solves on the
                               // right half since r2.3: the pocket pushes the hinge line to -31,
                               // the kickstand gets shorter and needs a steeper fold, which drops
                               // the outer plate's free end below the desk. 18 clears it by 2.3 mm
                               // on the right and 7.8 on the left.
hinge_fold_override = -1;      // > 0: fold shown by lid_folded instead of the solved one (collision test)
foot_overhang   = 3.0;         // as a foot the hinge axis sits this far outside the inner tray wall (gen_case FOOT_OVERHANG)
hinge_knuckle_d = 5.0;         // knuckle diameter = thickness of the hinge strip, flush with the roof top
hinge_strip_w   = 6.0;         // the roof is thickened to hinge_knuckle_d this far on both sides of the line
hinge_seg_len   = 10.0;        // target knuckle length; the count is odd so the outer plate owns both ends
hinge_seg_gap   = 0.3;         // between neighbouring knuckles along the pin
hinge_clear     = 0.3;         // radial clearance of a knuckle in the other plate's groove
hinge_gap       = 0.2;         // between the two plates' vertical cut faces above the axis
hinge_pin_d     = 2.0;         // steel rod; 1.75 for a piece of filament
hinge_pin_fit   = 0.2;         // hole = pin + this
hinge_blind     = 1.5;         // the pin hole stops this short of the y-max end (towards the user)

// ---------------------------------------------------------------- trackball pocket
ball_d          = 19.05;       // the only supported size since r2.4
pocket_d        = 32.0;        // round pocket wall above the PCB plane (cradle 28 + 2 x 2 wall)
pocket_wall     = 2.0;
cradle_d        = 28.0;        // cradle clearance circle above the PCB plane
ball_top_z      = 13.95;        // cradle stack.json ball_top_above_pcb_top (19.05 mm ball)
// Backstop for the sensor module. It slides into the cradle's sleeve from the open back and only
// a strip of tape keeps it against the lens seat; the cable pulls on it. A rib on the pocket wall
// stands module_stop_gap behind the module's rear corner, so it cannot back out of focus (the
// wall itself is 1.15 mm away, which would let the lens distance grow from 2.4 to 3.7 mm).
module_reach    = 16.40;       // cradle stack.json module_reach: rear upper board corner from the ball axis, towards +x
module_stop_gap = 0.3;         // the cradle (0.5 mm loose in its pocket, module fitted) still drops in
module_stop_w   = 8.0;         // along y, on the lens half of the board, clear of the cable exit (key side)
module_stop_dy  = 1.5;         // rib centre from the ball centre, away from the keys
module_stop_top_z = 1.6;       // above the module's rear corner (z 0.86)
// Flush cover over the cradle opening (tray.scad pocket_cover): it sits in a rebate on a ledge,
// flush with rim_z, and reaches over the cup rim as a bezel to cover_ball_gap from the ball, so
// the cup is out of sight. Until this bezel the hole was 26.5 mm (the old clip had to pass) with
// a funnel through the whole plate: a 5 mm ring round the ball.
cover_t         = 1.2;         // rim_z - cover_t = 3.8: 0.375 over the cradle top (cup rim 3.425),
                               // more than a print layer, so the cover never sits on the cup
cover_fit       = 0.15;        // all round in the rebate
cover_ball_gap  = 0.75;        // hole edge to the ball (radius <= 9.508 under the cover top): the
                               // cradle (+-0.1 on its screws) and the cover (+-0.15 in the rebate)
                               // may be off by 0.25 and the bezel still clears the ball by 0.5
cover_hole_d    = ball_d + 2 * cover_ball_gap;   // 20.55; the ball still lifts out through it
cover_chamfer   = 0.4;         // top edge of the hole
cover_screw_pilot_d = 1.6;     // M2 x 6 countersunk, self-tapping into the tray under the ledge
cover_screw_depth   = 6.0;
cover_screw_d   = 2.2;
cover_screw_head_d  = 3.8;     // DIN 7991 M2

// Optional retainer clip on top of the cover (tray.scad pocket_clip), for carrying the half
// turned over. A flat C-ring on the cover round the hole, open towards the thumb, with two claws
// over the ball's shoulders, held by two split snap pins in two holes in the cover. The claws
// keep the shape the old cup-mounted clip proved in retention.py (issues/mech-ball-retainer-clip.md).
clip_ball_gap   = 0.4;         // claw inner face to the ball: the cradle's ball_gap (cup inner wall)
clip_claw_az    = 80;          // claws at +- this azimuth from +x (layout frame); the thumb comes from -x
clip_claw_w     = 6.0;         // claw width between its parallel side faces
clip_claw_h     = 0.525 * ball_d / 2;   // claw top above the ball centre (5.0)
clip_claw_t     = 1.2;         // claw shell
clip_open_az    = 102;         // nothing of the clip beyond +- this azimuth: 156 degrees open to the thumb
clip_ring_t     = 1.2;         // C-ring on the cover top
clip_ring_w     = 4.8;         // radial width from the hole edge: carries the pins with 1.2 mm round them
clip_pin_r      = 13.0;        // pin axis from the ball axis: the pin keeps 0.375 to the cup (r 11.525)
clip_pin_az     = 56;          // pins at +- this azimuth, between the sensor tab (+x, 18 mm wide: 0.68 mm
                               // from the pin to its side face) and the claws at +-80 (0.97 mm)
clip_pin_d      = 2.2;         // in a cover_pin_hole_d hole
cover_pin_hole_d = 2.4;
clip_pin_slit   = 0.9;         // radial slit: two 0.65 mm prongs that spring towards each other
clip_pin_barb   = 0.22;        // barb per side beyond the pin: 0.12 undercut in the 2.4 hole (strain 2.2 %)
clip_pin_barb_h = 0.6;         // barb height under the cover
clip_release    = 30;          // barb top face, degrees from horizontal: pulls out straight up
case_screw_d      = 2.2;       // clearance holes for the M2 x 8 case screws from below
case_screw_head_d = 4.4;       // widest countersunk M2 head: DIN 7982 ST2.2 is 4.4, DIN 7991/965 M2 is 3.8
case_screw_cs_d   = case_screw_head_d + 0.4;              // 90 degree countersink mouth in the flat underside
case_screw_cs_h   = (case_screw_cs_d - case_screw_d) / 2; // 1.3 mm deep, 1.2 mm of floor left at the bore
fpc_clear       = 0.5;         // clearance around J1 and the FFC corridor on the key side

// ---------------------------------------------------------------- PCB guard
// A thin plate lying on the PCB top between the switches (like the Keyball39 cover plate). It
// adds no height: it fills the air under the keycaps, which bottom out at cap_skirt_z -
// switch_travel. The lower switch housings pass through square cut-outs, and the upper housing
// flanges hold it down, so it needs no screws. It stays clear of the PCB screw heads (they keep
// sitting on the PCB), the inside of the controller box, J1 and the FFC, and the cradle. It runs
// on under the box cap's skirt, which then stands on the guard: no PCB shows anywhere from above.
guard           = true;
cap_skirt_z     = 5.0;         // keycap skirt bottom at rest (the keycap dummy and rim_z)
switch_travel   = 3.0;         // Choc V1 total travel: the skirt bottoms out at +2.0
switch_lower    = 13.8;        // Choc V1 lower housing, the square under the flange
guard_t         = 0.8;         // 4 layers at 0.2
guard_min_air   = 0.8;         // at least this much air between the guard and a pressed keycap
guard_fit       = 0.2;         // around every switch housing, to the cavity wall and the box
guard_min_web   = 1.0;         // narrower strips are dropped from the outline; 1.0 = 2 perimeters of a 0.4 nozzle
guard_screw_d   = 3.7;         // PCB screw heads are max 3.5 (BOM): 0.1 all round, so no PCB shows round a head

// ---------------------------------------------------------------- rendering
$fn             = 64;
eps             = 0.01;
