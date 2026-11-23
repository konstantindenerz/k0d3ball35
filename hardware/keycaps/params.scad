// k0d3ball35 printed keycaps - parameters
// All dimensions in mm. Cap frame: x across the key (the 17.4 mm side, the two stem legs side by
// side), y away from the user, z up, z = 0 the flat underside of the cap top that rests on the
// switch slider. keycaps.scad turns the cap onto its back face for the export (print frame).
//
// Override on the command line, e.g.
//   openscad --backend manifold -D part=\"finger\" -D stem_fit=0.15 -o keycap-1u.stl keycaps.scad
//
// The switch numbers are Kailh's drawing of the Choc V1 (PG1350, CPG135001D01): the slider top
// stands 3.0 mm over the housing top, the housing top 5.0 mm over the PCB, the 15 x 15 flange
// reaches +3.0. The envelope every case check uses is hardware/case/params.scad (cap_size,
// cap_skirt_z, cap_top_z); tests/test_keycaps.py keeps these caps inside it.

// ---------------------------------------------------------------- selection
part            = "finger";    // finger | homing | thumb | fit_test | display
stem_fit        = 0.10;        // taken off the leg width and length: FDM 0.4 nozzle start value;
                               // the fit test prints 0.00 to 0.25, keep the loosest that holds

// ---------------------------------------------------------------- switch (Choc V1)
plane_z         = 8.0;         // slider top over the PCB top at rest: where z = 0 of the cap sits
switch_travel   = 3.0;         // total travel
flange_top_z    = 3.0;         // top of the 15 x 15 flange over the PCB top
housing_w       = 13.8;        // upper housing, square
leg_w           = 1.20;        // slider sockets, nominal: across (x)
leg_l           = 3.00;        //                          along (y)
leg_dx          = 5.70;        // centre to centre, along x
leg_h           = 3.0;         // leg length below the plane
leg_r           = 0.15;        // corner radius of the leg section
leg_tip         = 0.2;         // 45 degree chamfer at the tip, finds the socket

// ---------------------------------------------------------------- cap body
cap_w           = 17.4;        // footprint, 0.1 under the 17.5 x 16.5 envelope: 0.6 mm to the
cap_d           = 16.4;        // neighbours instead of 0.5, room for an elephant's foot
cap_r           = 1.0;         // vertical corner radius
cap_wall        = 1.0;         // side wall, two to three perimeters of a 0.4 nozzle
skirt           = 1.3;         // skirt bottom below the plane: +6.7 at rest, +3.7 pressed
top_h           = 2.6;         // top edge over the plane: +10.6, under cap_top_z 11.0
inner_r         = 0.5;         // corner radius of the cavity

// finger caps: a cylindrical dish across x (the axis runs along y)
dish_depth      = 0.6;
dish_chord      = 15.0;        // width of the dish at the top surface
finger_edge_r   = 1.0;         // top edge round-over
// homing caps (index home row, F and J): a rounded bar in the dish towards the user
bar_len         = 5.0;
bar_w           = 1.0;
bar_h           = 0.5;         // over the dish bottom
bar_y           = -4.5;        // towards the user
// thumb caps: flat top, no dish, large round-over for the side of the thumb
thumb_edge_r    = 1.5;

// ---------------------------------------------------------------- fit test
fit_steps       = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25];   // stem_fit per tab, tab n has n notches
tab_w           = 12.0;        // across x
tab_d           = 7.0;         // along y
tab_t           = 1.6;         // plate thickness over the plane
tab_pitch       = 15.0;        // tab to tab along x on the bed
tab_bridge      = 1.0;         // height of the bridges that hold the tabs together (snap them off)
notch           = 0.8;         // notch width and depth in the top edge of a tab
notch_pitch     = 1.5;

$fn             = 48;
