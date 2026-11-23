// k0d3ball35 printed keycaps: low profile 1u caps for Kailh Choc V1 (PG1350), 18 x 17 spacing
//
// One cap body for the whole board in three tops: a shallow cylindrical dish on the finger keys,
// the same with a rounded bar on the two index home keys (F and J), and a flat, well rounded top
// on the thumb keys. Two stem legs fit the slider's 1.2 x 3.0 sockets; stem_fit takes a little
// off both so an FDM print goes on without cracking the slider.
//
//   part = "finger"    one finger cap        (print frame)
//   part = "homing"    one homing cap        (print frame)
//   part = "thumb"     one thumb cap         (print frame)
//   part = "fit_test"  six stem tabs, stem_fit 0.00 to 0.25, joined by snap-off bridges
//   part = "display"   the three caps side by side in the cap frame, for the preview
//
// Print frame: each cap stands on its back face (the side away from the user), z up. The legs
// lie flat, so the layers run along them and they do not break off at the root; they need
// support underneath, nothing else does. The cap frame (params.scad) is the print frame
// translated: x stays, cap z = print y, cap y = print z - cap_d / 2 (the page relies on that).
//
// See params.scad for every dimension and README.md for printing and the fit test.

include <params.scad>

eps = 0.01;

module rrect(w, d, r) {
  rr = min(r, w / 2 - eps, d / 2 - eps);
  offset(r = rr) square([w - 2 * rr, d - 2 * rr], center = true);
}

// stand a part of depth d (along y) on its back face
module print_frame(d) {
  translate([0, 0, d / 2]) rotate([-90, 0, 0]) children();
}

// ---------------------------------------------------------------- cap
// outer body: straight walls from the skirt up, the top edge rounded with radius er
module outer(er) {
  steps = 16;
  hull() {
    translate([0, 0, -skirt]) linear_extrude(top_h - er + skirt) rrect(cap_w, cap_d, cap_r);
    for (i = [1:steps]) {
      a = 90 * i / steps;
      inset = er * (1 - cos(a));
      translate([0, 0, top_h - er + er * sin(a) - eps])
        linear_extrude(eps) rrect(cap_w - 2 * inset, cap_d - 2 * inset, max(cap_r - inset, 0.05));
    }
  }
}

module cavity() {
  translate([0, 0, -skirt - 1]) linear_extrude(skirt + 1) rrect(cap_w - 2 * cap_wall, cap_d - 2 * cap_wall, inner_r);
}

dish_R = (dish_chord * dish_chord / 4 + dish_depth * dish_depth) / (2 * dish_depth);
dish_bottom = top_h - dish_depth;

// cylinder segment along y: the dish surface is z = dish_bottom + R - sqrt(R^2 - x^2)
module dish() {
  half = cap_w / 2 + 1;
  pts = [for (x = [-half:0.2:half + eps]) [x, dish_bottom + dish_R - sqrt(dish_R * dish_R - x * x)]];
  rotate([90, 0, 0]) linear_extrude(cap_d + 2, center = true)
    polygon(concat(pts, [[half, top_h + 2], [-half, top_h + 2]]));
}

module bar() {
  z = dish_bottom + bar_h - bar_w / 2;
  hull() for (s = [-1, 1]) translate([s * (bar_len - bar_w) / 2, bar_y, z]) sphere(d = bar_w, $fn = 24);
}

// one stem leg below the plane, 0.5 into the top plate; chamfered tip
module leg(fit) {
  w = leg_w - fit;
  l = leg_l - fit;
  hull() {
    translate([0, 0, -leg_h + leg_tip]) linear_extrude(leg_h - leg_tip + 0.5) rrect(w, l, leg_r);
    translate([0, 0, -leg_h]) linear_extrude(eps) rrect(w - 2 * leg_tip, l - 2 * leg_tip, 0.05);
  }
}

module legs(fit) {
  for (s = [-1, 1]) translate([s * leg_dx / 2, 0, 0]) leg(fit);
}

module cap(kind) {
  difference() {
    outer(kind == "thumb" ? thumb_edge_r : finger_edge_r);
    cavity();
    if (kind != "thumb") dish();
  }
  if (kind == "homing") bar();
  legs(stem_fit);
}

// ---------------------------------------------------------------- fit test
// a plate with two legs; n notches in the edge towards the user (on top when printed)
module tab(fit, n) {
  difference() {
    linear_extrude(tab_t) rrect(tab_w, tab_d, 0.8);
    for (i = [0:n - 1])
      translate([(i - (n - 1) / 2) * notch_pitch - notch / 2, -tab_d / 2 - eps, -1]) cube([notch, notch + eps, tab_t + 2]);
  }
  legs(fit);
}

module fit_test() {
  n = len(fit_steps);
  x0 = -(n - 1) / 2 * tab_pitch;
  for (i = [0:n - 1]) translate([x0 + i * tab_pitch, 0, 0]) print_frame(tab_d) tab(fit_steps[i], i + 1);
  // bridges on the bed between neighbouring tabs, 1 mm into each
  for (i = [0:n - 2])
    translate([x0 + i * tab_pitch + tab_w / 2 - 1, 0, 0]) cube([tab_pitch - tab_w + 2, tab_t, tab_bridge]);
}

// ---------------------------------------------------------------- dispatch
if (part == "finger" || part == "homing" || part == "thumb") print_frame(cap_d) cap(part);
else if (part == "fit_test") fit_test();
else if (part == "display") {
  for (k = [["finger", -20], ["homing", 0], ["thumb", 20]]) translate([k[1], 0, 0]) cap(k[0]);
}
else assert(false, str("unknown part ", part));
