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
part            = "assembly";  // tray | box_cap | lid | lid_outer | lid_inner | lid_folded | lid_dome | pocket_test | assembly | section | floor2d
mirror_left     = true;        // mirror x once at the top level for the left half (physical part)

// ---------------------------------------------------------------- PCB and walls
pcb_t           = 1.6;
pcb_clear       = 0.2;         // gap between the PCB edge and the cavity wall
wall            = 3.0;         // case wall outside the PCB cavity
under_pcb_clear = 3.0;         // cavity under the key area: hot-swap sockets 1.8 + diodes 1.1 + air
rim_z           = 5.0;         // top of the tray walls (flush with the Choc keycap skirts)

// ---------------------------------------------------------------- floors
well_floor_z    = -11.6;       // battery well floor (bay 9.0 below the PCB underside allowed, shared with the pocket)
pocket_floor_z  = -11.6;       // cradle floor, cradle stack.json floor_z
floor_t         = 2.5;         // floor under the deepest well; the underside is flat everywhere
floor_z_key     = -pcb_t - under_pcb_clear;          // -4.6
base_z          = min(well_floor_z, pocket_floor_z) - floor_t;   // -14.1

// ---------------------------------------------------------------- PCB fastening
// Default: M2 heat-set inserts (brass, M2 x 3 mm, OD about 3.5) in the standoffs and the cap
// bosses, M2 x 5 / x 6 machine screws from the top (head max 3.5 mm, under the keycaps).
// "pilot": 1.6 mm pilots for M2 self-tapping screws instead.
pcb_screws      = "insert";    // "insert" | "pilot"
insert_hole_d   = 3.2;
insert_depth    = 4.0;
standoff_d      = 6.0;         // leaves 1.4 mm around the insert hole
standoff_pilot_d = 1.6;        // only used for pcb_screws == "pilot"
standoff_h      = -pcb_t - floor_z_key;              // 3.0
screw_hole_d    = (pcb_screws == "insert") ? insert_hole_d : standoff_pilot_d;
screw_hole_depth = (pcb_screws == "insert") ? insert_depth : 6.0;
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
box_skirt_gap   = 0.3;         // skirt stops this above the PCB top
box_rebate      = 2.0;         // inner part of the tall walls lowered to box_roof_under_z for the cap plate
box_fit         = 0.15;        // clearance between the cap plate and the rebate
boss_in         = 0.5;         // boss screw axis this far inside the wall's inner face
boss_skin       = 1.4;         // material around the insert hole
usb_cut         = [11, 5.8];   // width, height; the cut ends at box_roof_under_z
switch_slot     = [7, 3.0];    // slide switch lever: width along the wall, height under the PCB
reset_hole_d    = 3.0;         // through the floor under RB1
led_window      = [3, 3];      // width along the wall, height; in the inner (-x) wall
led_offset_y    = 8.0;         // from the controller board's USB end
led_z           = 3.5;         // bottom of the window

// ---------------------------------------------------------------- owner wordmark
// Grid and rectangles in logo_data.scad (scripts/gen_logo.py). The relief is engraved, not
// raised: the box cap and the tray both print with the engraved face on the bed. Grooves are
// one cell wide, so nothing bridges further than logo_cell.
logo_on_cap     = true;
logo_on_floor   = true;
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
foot_recess     = 0.5;

// ---------------------------------------------------------------- lid
// Two plates per half joined by a pin hinge along x = hinge_x (data.scad): the outer plate
// (pinky side, carries the ball window and the four roof magnets) and the inner plate
// (controller and thumb side). Closed it is the transport cover; folded by hinge_fold_deg it
// goes under the half as a tenting stand, the outer plate roof-up against the floor magnets and
// the inner plate as the leg. See docs/11-case.md section 7.
cap_top_z       = 11.0;        // Choc V1 keycap top
lid_clear       = 3.0;         // roof underside over the caps; also room for the hinge strip
lid_roof_t      = 3.0;         // takes the 2.4 mm magnet pockets plus the 0.6 mm skin
lid_lip_t       = 1.0;         // inner lip that holds the lid on the tray by friction
lid_lip_depth   = 3.0;         // how far the lip reaches into the tray below the rim
lid_fit         = 0.15;        // clearance between the lip and the inner wall face
lid_mode        = "window";    // "window" (ball looks through a hole smaller than itself) | "flat" (roof over the ball) | "dome"
ball_window_d   = 16.0;        // through the roof at the ball centre; < ball_d keeps the ball in the cup
lid_box_clear   = 0.3;         // lid skirt around the controller box walls

// ---------------------------------------------------------------- lid hinge and tenting foot
tent_deg        = 15;          // tilt of the half on the folded lid, inner edge up; the stop is cut for 2 x this
hinge_fold_deg  = 2 * tent_deg; // fold shown by lid_folded / lid_foot; the stop faces meet at exactly 2 x tent_deg
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
ball_d          = 19.05;       // 25 mm fallback: -D ball_d=25 -D notch_apothem=16.5 -D pocket_d=35
notch_apothem   = 15.0;        // PCB notch octagon (layout cradle_diameter / 2 + 1)
pocket_d        = 32.0;        // round pocket wall above the PCB plane (cradle 28 + 2 x 2 wall)
pocket_wall     = 2.0;
cradle_d        = 28.0;        // cradle clearance circle above the PCB plane
ball_top_z      = 17.1;        // cradle stack.json ball_top_above_pcb_top (19.05 mm ball)
case_screw_d    = 2.2;         // clearance holes for the M2 x 10 case screws from below
case_screw_cb_d = 4.5;         // counterbore so 2 mm of floor remain under the cradle
case_screw_cb_h = floor_t - 2.0;
fpc_clear       = 0.5;         // clearance around J1 and the FFC corridor on the key side

// ---------------------------------------------------------------- rendering
$fn             = 64;
eps             = 0.01;
