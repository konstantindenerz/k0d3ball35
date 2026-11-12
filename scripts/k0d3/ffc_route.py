# SPDX-License-Identifier: MIT
"""Length of the 6-way FFC from the sensor module to J1 on the right PCB.

The route (spec/08-trackball-module.md section 2): the cable leaves the module's FH19C in the
board plane out of the module's short end on the key side, runs round the cradle cup as an
upright band, twists flat and lies down on the PCB into J1. Everything here comes from files:
the cradle's stack.json and params.scad, and the layout (ball centre, J1 mouth).

Insertion depths, the two values that do not come from our own geometry:
- FH19C on the module: 2.3 mm, the cable outline in the maker's drawing
  (github.com/sekigon-gonnoc/small-mouse-sensor-module, img/size.png)
- FH12-6S on the PCB: 4.5 mm, KiCad's Hirose_FH12-6S-0.5SH footprint body is 5.6 mm deep
  from the slider face to the rear wall
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

from .geometry import Layout

ROOT = Path(__file__).resolve().parents[2]
CRADLE = ROOT / "hardware" / "trackball-cradle"

INSERT_MODULE = 2.3     # FH19C, maker drawing
INSERT_J1 = 4.5         # FH12-6S, KiCad footprint body depth 5.6 minus the rear wall
LEADS = 3.0             # straight run into each connector and the 90 degree twist before J1
BAND_CLEAR = 0.4        # the band's centre line from the cup envelope (0.3 gap + half the twist)


def _param(name: str) -> float:
    m = re.search(rf"^{name}\s*=\s*(-?[\d.]+)", (CRADLE / "params.scad").read_text(), re.M)
    if m is None:
        raise ValueError(f"params.scad: no numeric {name}")
    return float(m.group(1))


@dataclass
class Route:
    module_mouth: tuple[float, float, float]   # relative to the ball axis, z over the PCB top
    sweep_deg: float                           # how far round the cup
    band_top_z: float                          # highest point of the upright band
    insert_module: float
    exit: float                                # straight out through the sleeve's end-wall slot
    path: float                                # from the wall to J1's mouth
    leads: float
    insert_j1: float

    @property
    def total(self) -> float:
        return self.insert_module + self.exit + self.path + self.leads + self.insert_j1


def _around(a: tuple[float, float], b: tuple[float, float], r: float) -> tuple[float, float]:
    """Shortest plan path from a to b round a circle of radius r at the origin, and the sweep."""
    da, db = math.hypot(*a), math.hypot(*b)
    d = abs(math.atan2(a[1], a[0]) - math.atan2(b[1], b[0])) % (2 * math.pi)
    d = min(d, 2 * math.pi - d)
    arc = d - math.acos(r / da) - math.acos(r / db)
    if arc <= 0:
        return math.dist(a, b), math.degrees(d)
    return math.sqrt(da * da - r * r) + math.sqrt(db * db - r * r) + r * arc, math.degrees(d)


def _stack() -> dict:
    return json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]


def _module_end(s: dict) -> tuple[tuple[float, float], tuple[float, float], float]:
    """The cable at the module, relative to the ball axis: its mouth in the FH19C, the point
    where it leaves the sleeve's end wall, and its height over the PCB top."""
    th, az = math.radians(s["sensor_angle"]), math.radians(s["window_az"])
    L = s["sensor_pcb_plane_dist"]
    # the cable mouth in the sensor frame: the connector-side board end, at the cable's height
    conn_end = _param("conn_end")
    y_end = conn_end * (_param("sensor_pcb_l") - _param("lens_far"))
    # the cable first runs straight along the board through the end-wall slot, to the tab's face
    y_wall = conn_end * s["housing_y"] / 2                # the sleeve tab is housing_y wide
    z_loc = -L + 0.35 + 0.075
    along = -z_loc * math.sin(th)                       # x = 0 on the board's centre line
    z = s["ball_centre_z"] + z_loc * math.cos(th)
    # the sensor frame turns about z so that the window sits at window_az: along -> window_az,
    # local +y -> window_az + 90 deg turned by the frame (sensor_az = window_az + 180)
    sensor_az = az + math.pi
    mouth = (along * math.cos(az) - y_end * math.sin(sensor_az), along * math.sin(az) + y_end * math.cos(sensor_az))
    wall = (along * math.cos(az) - y_wall * math.sin(sensor_az), along * math.sin(az) + y_wall * math.cos(sensor_az))
    return mouth, wall, z


def route(layout: Layout) -> Route:
    s = _stack()
    mouth, (mx, my), z = _module_end(s)
    exit_len = math.dist(mouth, (mx, my))
    bx, by = layout.ball_center
    jx, jy = layout.fpc_mouth()
    rho = s["cup_outer_d"] / 2 + BAND_CLEAR
    plan, sweep = _around((mx, my), (jx - bx, jy - by), rho)
    climb = max(0.0, 0.6 - z)                           # up to the cable height in J1 on the PCB top
    band_top = max(z, 0.6) + _param("ffc_w") / 2
    return Route((round(mouth[0], 3), round(mouth[1], 3), round(z, 3)), sweep, band_top, INSERT_MODULE,
                 exit_len, math.hypot(plan, climb), LEADS, INSERT_J1)


# Slack. No stocked 6-way 0.5 mm type B cable comes between 30 mm (shorter than the route) and
# 50 mm, so the cable is 50 mm and the rest is laid as an S-fold of the upright band in the free
# corner of the pocket beside J1's mouth, towards the thumb, under the pocket cover. The zone is
# relative to the ball axis, layout frame; tests/test_ffc_route.py checks that it is free (cradle
# mesh, PCB outline, pocket opening, cover) and that the fold holds the slack.
SLACK_ZONE = (-14.0, -15.4, -9.0, -6.0)    # x0, y0, x1, y1 relative to the ball centre
SLACK_Z = (-1.6, 1.9)                     # the band stands on the tray shelf at the PCB underside
FOLD_PITCH = 1.2                          # leg to leg, a 0.6 mm bend radius per fold


def slack_capacity() -> float:
    """Extra cable an S-fold in SLACK_ZONE can take: legs along y, FOLD_PITCH apart, each running
    from the zone's key-side edge to the cup envelope (or the zone's far edge), minus one leg the
    straight route would use anyway, plus the folds."""
    s = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]
    rho = s["cup_outer_d"] / 2 + BAND_CLEAR + 0.3
    x0, y0, x1, y1 = SLACK_ZONE
    legs = []
    x = x0 + FOLD_PITCH / 2
    while x <= x1:
        top = y1 if abs(x) >= rho else min(y1, -math.sqrt(rho * rho - x * x))
        legs.append(max(0.0, top - y0))
        x += FOLD_PITCH
    if len(legs) < 2:
        return 0.0
    bends = (len(legs) - 1) * math.pi * FOLD_PITCH / 2
    return sum(legs) - min(legs) + bends


# ---------------------------------------------------------------- the cable as it lies
# route() above is the shortest way and gives the length to buy. path() is the whole 50 mm cable
# as the build guide lays it, for the drawings and for the interference test: a nominal lay, the
# real cable is put in by hand. A flat cable bends only across its width, so the upright band
# changes direction in plan only, and the flat end into J1 is straight in plan.
ARC_END_DEG = 50.0      # the band follows the cup this far before it leaves for the fold
J1_CABLE_Z = 0.6        # the cable in J1 over the PCB top (as in route())
EXIT_BEND = 1.0         # bend radius where the band leaves the sleeve and turns round the cup


def _fillet(points: list[tuple[float, float]], radii: list[float], step_deg: float = 15.0) -> list[tuple[float, float]]:
    """The polyline with its inner corners rounded (radii[i] belongs to points[i + 1])."""
    out = [points[0]]
    for i in range(1, len(points) - 1):
        (ax, ay), (px, py), (cx, cy) = points[i - 1], points[i], points[i + 1]
        r = radii[i - 1]
        u = ((ax - px) / math.dist(points[i - 1], points[i]), (ay - py) / math.dist(points[i - 1], points[i]))
        w = ((cx - px) / math.dist(points[i + 1], points[i]), (cy - py) / math.dist(points[i + 1], points[i]))
        turn = math.pi - math.acos(max(-1.0, min(1.0, u[0] * w[0] + u[1] * w[1])))
        if r <= 0 or turn < 1e-6:
            out.append(points[i])
            continue
        t = r * math.tan(turn / 2)
        assert t <= math.dist(points[i - 1], points[i]) + 1e-6 and t <= math.dist(points[i + 1], points[i]) + 1e-6, \
            f"corner {points[i]} has no room for a {r} mm bend"
        p0 = (px + u[0] * t, py + u[1] * t)
        side = 1.0 if u[0] * w[1] - u[1] * w[0] < 0 else -1.0      # centre left (+) or right of the travel
        d = (-u[0], -u[1])
        centre = (p0[0] - side * d[1] * r, p0[1] + side * d[0] * r)
        a0 = math.atan2(p0[1] - centre[1], p0[0] - centre[0])
        n = max(2, math.ceil(math.degrees(turn) / step_deg))
        out += [(centre[0] + r * math.cos(a0 + side * turn * k / n), centre[1] + r * math.sin(a0 + side * turn * k / n))
                for k in range(n + 1)]
    out.append(points[-1])
    return out


def path(layout: Layout) -> list[tuple[float, float, float, float]]:
    """The centre line of the cable from its end in the module to its end in J1, layout frame:
    (x, y, z over the PCB top, roll in degrees). Roll is how far the band leans from upright about
    its own direction: 0 upright, 90 flat. The length is the cable of the layout (fpc.cable_length):
    the fold's depth is solved for it."""
    s = _stack()
    if s["window_az"] != 0.0 or layout.cfg["fpc"]["rotation"] != 0:
        raise NotImplementedError("path() is drawn for the sensor at +x and J1's mouth towards the ball")
    (m0x, m0y), (wx, wy), zm = _module_end(s)
    bx, by = layout.ball_center
    jx, jy = layout.fpc_mouth()[0] - bx, layout.fpc_mouth()[1] - by
    rho = s["cup_outer_d"] / 2 + BAND_CLEAR
    lean = 90.0 - s["sensor_angle"]                     # the board's lean carries on in the cable
    z_band = (SLACK_Z[0] + SLACK_Z[1]) / 2
    length = layout.cfg["fpc"]["cable_length"]

    # round the cup: tangent from the sleeve wall, then clockwise (seen from above) to ARC_END_DEG
    a_w = math.atan2(wy, wx)
    a1 = a_w - math.acos(rho / math.hypot(wx, wy))
    a2 = a1 - math.radians(ARC_END_DEG)
    arc = [(rho * math.cos(a1 + (a2 - a1) * k / 8), rho * math.sin(a1 + (a2 - a1) * k / 8)) for k in range(9)]
    head = (math.sin(a2), -math.cos(a2))                # the band's direction where it leaves the cup

    def line_y(x: float) -> float:
        return arc[-1][1] + (x - arc[-1][0]) / head[0] * head[1]

    # the S-fold: down, up, down, FOLD_PITCH apart, the last leg straight above J1's mouth
    x3, x2, x1 = jx, jx - FOLD_PITCH, jx - 2 * FOLD_PITCH
    y_top = line_y(x3) - FOLD_PITCH                     # the upper bend stays under the incoming band
    y_lead = jy + LEADS                                 # here the band starts to twist flat

    def lay(y_bot: float) -> list[tuple[float, float, float, float]]:
        r = FOLD_PITCH / 2
        head_pts = _fillet([(m0x, m0y + INSERT_MODULE), (wx, wy), arc[0]], [EXIT_BEND])
        fold = _fillet([arc[-1], (x1, line_y(x1)), (x1, y_bot), (x2, y_bot), (x2, y_top), (x3, y_top), (x3, y_lead)],
                       [r, r, r, r, r])
        plan = head_pts + arc[1:] + fold[1:]
        n_exit = 2                                      # end in the FH19C and the sleeve wall: still in the board plane
        n_fold = len(head_pts) + len(arc) - 1           # first point of the fold run (the arc's end)
        run = [0.0]
        for a, b in zip(plan, plan[1:]):
            run.append(run[-1] + math.dist(a, b))
        s_wall, s_arc, s_fold = run[n_exit - 1], run[len(head_pts) - 1], run[n_fold]
        pts = []
        for (x, y), d in zip(plan, run):
            if d <= s_wall:
                pts.append((x, y, zm, lean))
            elif d < s_fold:                            # climbing to the shelf, upright by the cup
                k = (d - s_wall) / (s_fold - s_wall)
                pts.append((x, y, zm + (z_band - zm) * k, lean * max(0.0, 1 - (d - s_wall) / (s_arc - s_wall))))
            else:
                pts.append((x, y, z_band, 0.0))
        for k in range(1, 7):                           # the twist over the lead, onto the board
            pts.append((x3, y_lead + (jy - y_lead) * k / 6, z_band + (J1_CABLE_Z - z_band) * k / 6, 90.0 * k / 6))
        pts.append((x3, jy - INSERT_J1, J1_CABLE_Z, 90.0))
        return pts

    def total(pts) -> float:
        return sum(math.dist(a[:3], b[:3]) for a, b in zip(pts, pts[1:]))

    lo, hi = SLACK_ZONE[1] + 0.3, y_top - FOLD_PITCH    # deepest and shallowest fold
    if not total(lay(hi)) <= length <= total(lay(lo)):
        raise ValueError(f"a {length} mm cable does not fit the fold: {total(lay(hi)):.1f} to {total(lay(lo)):.1f} mm")
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if total(lay(mid)) < length else (mid, hi)
    return [(round(x + bx, 3), round(y + by, 3), round(z, 3), round(roll, 2)) for x, y, z, roll in lay((lo + hi) / 2)]
