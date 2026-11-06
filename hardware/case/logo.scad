// k0d3ball35 printed case - the owner wordmark as a relief
//
// The cell grid comes from logo_data.scad (scripts/gen_logo.py reads docs/images/logo.png),
// the millimetres from params.scad: one cell is logo_cell wide and logo_cell * logo_stretch
// tall. Cell y counts from the top of the artwork, so the rows are flipped here.
//
// The relief is cut into a face rather than raised from it: both the box cap and the tray
// print with that face on the bed, where raised lines would need support. The grooves are one
// cell wide, which bridges at logo_depth without a bridge longer than logo_cell.

function logo_cell_y(cell) = cell * logo_stretch;
function logo_size(cell) = [logo_grid[0] * cell, logo_grid[1] * logo_cell_y(cell)];
// engraved floor area: what the print has to bridge, in one-cell wide strips
function logo_area(cell) = (logo_invert ? logo_grid[0] * logo_grid[1] - logo_ink_cells : logo_ink_cells)
                           * cell * logo_cell_y(cell);

module logo_ink_2d(cell) {
    cy = logo_cell_y(cell);
    for (r = logo_rects)
        translate([r[0] * cell, (logo_grid[1] - r[1] - r[3]) * cy])
            square([r[2] * cell, r[3] * cy]);
}

// the wordmark centred on the origin; logo_invert engraves the field instead of the lines,
// which leaves the lines standing proud of it
module logo_2d(cell) {
    sz = logo_size(cell);
    translate([-sz[0] / 2, -sz[1] / 2])
        if (logo_invert) difference() { square(sz); logo_ink_2d(cell); }
        else logo_ink_2d(cell);
}

// case.scad mirrors the whole left half once, so the wordmark is mirrored back here. The
// mirror sits outside the rotation: the two mirrors then cancel and leave a pure rotation,
// so the logo reads the same way round on both halves.
module logo_placed_2d(rot, cell) {
    if (half == "left" && mirror_left) mirror([1, 0, 0]) rotate(rot) logo_2d(cell);
    else rotate(rot) logo_2d(cell);
}

// groove to subtract from the face at z_top, cut depth deep into it
module logo_cut(pos, rot, cell, z_top, depth)
    translate([pos[0], pos[1], z_top - depth])
        linear_extrude(depth + eps)
            logo_placed_2d(rot, cell);
