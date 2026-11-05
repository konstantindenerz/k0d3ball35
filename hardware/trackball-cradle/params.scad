// k0d3ball36 trackball cradle - parameters
// All dimensions in mm. Coordinate system: z up, z = 0 is the TOP surface of the
// main PCB, the ball centre is on the z axis. +x points outward (towards the pinky
// side of the right half), +y points towards the user.
//
// Override on the command line, e.g.
//   openscad -D ball_d=34 -D part=\"cradle\" -o cradle-34mm.stl cradle.scad

// ---------------------------------------------------------------- ball & bearings
ball_d          = 25;      // trackball diameter (25 default, 34 option)
ball_gap        = 0.4;     // radial clearance between ball and cup wall
bearing_d       = 2.0;     // ZrO2 / Si3N4 ceramic ball diameter
bearing_fit     = 0.05;    // press-fit interference per side (seat = bearing_d - 2*fit)
bearing_depth   = 0.6;     // how far the bearing centre sits behind the cup inner surface
bearing_elev    = 35;      // degrees below the equator where the bearings touch the ball
bearing_az      = [60, 180, 300];  // azimuths (deg); keep 0 deg free for a tilted sensor

// ---------------------------------------------------------------- sensor stack (PMW3610 + LM18-LSI)
// From the PMW3610DM-SUDU datasheet, figure 4 (assembly drawing, mouse orientation):
//   Z, lens reference plane to tracking surface: 2.2 min / 2.4 typ / 2.6 max
//   lens reference plane to sensor-PCB underside : 3.40 (gap between PCB and base plate)
//   sensor PCB thickness                          : 1.60
//   top of sensor package above the PCB           : 1.65 (9.05 - 7.40)
lens_z          = 2.4;     // ball surface to lens reference plane (datasheet typ.)
lens_h          = 3.4;     // lens reference plane to sensor PCB (lens side)
lens_l          = 21.5;    // LM18-LSI body length  (cavity gets +1.0 clearance)
lens_w          = 11.5;    // LM18-LSI body width   (cavity gets +1.0 clearance)
sensor_pcb_l    = 25;      // sensor daughterboard, axis of the two M2 holes (hardware/sensor-pcb)
sensor_pcb_w    = 26;      // sensor daughterboard, axis of the lens / sensor body
sensor_pcb_t    = 1.6;
sensor_hole_sp  = 20;      // M2 mounting hole spacing along the long axis
sensor_pins_h   = 1.65 + 0.6;  // tallest part on the component side (sensor top 9.05 - 7.40 = 1.65) + margin
sensor_angle    = 0;       // 0 = sensor straight below the ball; >0 tilts it towards +x (deg from vertical)
sensor_az       = 0;       // azimuth of the tilt direction (deg)

// ---------------------------------------------------------------- main PCB interface
pcb_t           = 1.6;     // main PCB thickness
pcb_cutout_d    = ball_d + 5;   // main PCB cutout: 30 for 25 mm (docs/01-design-spec.md section 5), 39 for 34 mm
flange_d        = ball_d + 15;  // flange under the PCB (40 for 25 mm)
flange_t        = 2.0;
flange_hole_bcd = ball_d + 11;  // bolt circle of the three M2 flange screws (36 for 25 mm)
flange_hole_az  = [90, 210, 330];
flange_pilot_d  = 1.6;     // pilot hole for M2 self-tapping screws (use 3.2 for heat-set inserts)
depth_below_pcb = 10.0;    // lowest point of cradle + sensor board below the main PCB underside

// ---------------------------------------------------------------- cup & retainer
wall            = 1.6;     // cup wall thickness
rim_drop        = 1.0;     // cup rim this far below the equator (finger clearance)
housing_wall    = 2.0;     // walls around the sensor board / lens cavity
retainer_t      = 1.2;     // retainer base ring thickness
retainer_claws  = [30, 150, 270];  // claw azimuths; keep the thumb approach side free
claw_w          = 6;       // claw width (tangential)
claw_h          = 4.8;     // claw height above the base ring
claw_grip       = 0.7;     // radial overlap of the claw tip over the ball silhouette
peg_d           = 1.8;     // retainer pegs (press fit into rim holes of peg_d + 0.1)
peg_h           = 3;

// ---------------------------------------------------------------- rendering
$fn             = 96;
part            = "assembly";  // cradle | retainer | assembly | cutout2d | sensor_dummy
