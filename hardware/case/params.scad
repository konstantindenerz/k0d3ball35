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
part            = "assembly";  // tray | box_cap | lid | lid_dome | pocket_test | assembly | section | floor2d
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

// ---------------------------------------------------------------- magnets and feet
// Magnets only hold the lid-as-foot: four in the tray floor (from below) and four in the lid
// roof (from the roof underside, closed by magnet_skin on top). The lid on top holds by its lip.
magnet_d        = 6.2;         // 6 x 2 mm neodymium discs
magnet_h        = 2.2;
magnet_skin     = 0.6;         // roof left above the lid magnets (lid_roof_t - magnet_h - magnet_pocket_extra)
magnet_pocket_extra = 0.2;     // pocket depth = magnet_h + this (glue film)
foot_d          = 10.5;        // rubber feet recess
foot_recess     = 0.5;

// ---------------------------------------------------------------- lid
cap_top_z       = 11.0;        // Choc V1 keycap top
lid_clear       = 1.0;
lid_roof_t      = 3.0;         // takes the 2.4 mm magnet pockets plus the 0.6 mm skin
lid_lip_t       = 1.0;         // inner lip that holds the lid on the tray by friction
lid_lip_depth   = 3.0;         // how far the lip reaches into the tray below the rim
lid_fit         = 0.15;        // clearance between the lip and the inner wall face
lid_mode        = "flat";      // "flat" | "dome" (dome only matters for the ball half)
tent_wedge_deg  = 0;           // > 0 adds a wedge to the lid roof so the lid-as-foot tents the half
lid_box_clear   = 0.3;         // lid skirt around the controller box walls

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
