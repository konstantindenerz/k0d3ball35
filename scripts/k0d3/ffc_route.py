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


def route(layout: Layout) -> Route:
    s = json.loads((CRADLE / "stack.json").read_text())["variants"]["19mm-pocket"]
    th, az = math.radians(s["sensor_angle"]), math.radians(s["window_az"])
    L = s["sensor_pcb_plane_dist"]
    # the cable mouth in the sensor frame: the connector-side board end, at the cable's height
    conn_end = _param("conn_end")
    y_end = conn_end * (_param("sensor_pcb_l") - _param("lens_far"))
    # the cable first runs straight along the board through the end-wall slot, to the tab's face
    y_wall = conn_end * s["housing_y"] / 2                # the sleeve tab is housing_y wide
    exit_len = abs(y_wall - y_end)
    z_loc = -L + 0.35 + 0.075
    along = -z_loc * math.sin(th)                       # x = 0 on the board's centre line
    z = s["ball_centre_z"] + z_loc * math.cos(th)
    # the sensor frame turns about z so that the window sits at window_az: along -> window_az,
    # local +y -> window_az + 90 deg turned by the frame (sensor_az = window_az + 180)
    sensor_az = az + math.pi
    mouth = (along * math.cos(az) - y_end * math.sin(sensor_az), along * math.sin(az) + y_end * math.cos(sensor_az))
    mx = along * math.cos(az) - y_wall * math.sin(sensor_az)
    my = along * math.sin(az) + y_wall * math.cos(sensor_az)
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
