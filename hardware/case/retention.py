#!/usr/bin/env python3
"""Does the retainer clip on the pocket cover keep the ball in, and does it stay off the ball?

Renders the cradle (hardware/trackball-cradle) and the clip (hardware/case, part pocket_clip, both
centred on the ball) with OpenSCAD, samples both meshes densely and asks, in the configuration
space of the ball centre, whether the ball can find a way out:

* every position of the ball centre is "free" when the ball (radius R - margin) touches no
  sampled surface point; the free set is computed for the whole neighbourhood at once by
  dilating the point cloud with a ball kernel (FFT convolution on a 0.2 mm grid),
* a flood fill from the resting position (the ball centred in the cup) tells whether the free
  region the ball is in reaches the space above everything, i.e. whether it can leave,
* `margin` shrinks the ball, which is the same as making cup and claws looser by that much; the
  largest margin at which the ball is still trapped is the tolerance the design has against
  print error, a slightly small ball and claws that flex.

The same run measures what the thumb and the sensor see: the gap between the claws and the ball
at rest, how far the ball can rattle, and whether pulling the clip straight up ever brings a claw
closer to the ball (it must not, or taking the clip off would drag the ball along).

Usage: ./retention.py [openscad-binary]   (writes retention.json next to this file)
Only numpy and trimesh are needed (no scipy).
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CRADLE_SCAD = HERE.parent / "trackball-cradle" / "cradle.scad"
CASE_SCAD = HERE / "case.scad"
GRID = 0.2                 # mm, configuration-space grid
SAMPLE = 0.12              # mm, surface sampling pitch
VARIANTS = {
    "19mm-pocket": {"ball_d": 19.05},
}


def find_openscad(arg=None):
    for cand in [arg, shutil.which("openscad"), "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"]:
        if cand and Path(cand).exists():
            return cand
    raise SystemExit("openscad not found")


def define(key, value):
    return f'{key}="{value}"' if isinstance(value, str) else f"{key}={value}"


def render(binary, part, overrides, out, scad=CRADLE_SCAD):
    cmd = [binary, "--backend", "manifold", "-D", f'part="{part}"']
    for k, v in overrides.items():
        cmd += ["-D", define(k, v)]
    cmd += ["-o", str(out), str(scad)]
    res = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return {m.group(1): float(m.group(2)) for m in re.finditer(r"STACK (\w+)=(-?[\d.]+)", res.stderr + res.stdout)}


def sample_surface(mesh, pitch=SAMPLE):
    """Deterministic surface sampling: a barycentric grid on every triangle, plus the vertices."""
    tris = mesh.triangles
    out = [mesh.vertices]
    edges = np.max(np.linalg.norm(tris[:, [1, 2, 0]] - tris, axis=2), axis=1)
    n_all = np.maximum(1, np.ceil(edges / pitch).astype(int))
    for n in np.unique(n_all):
        sel = tris[n_all == n]
        i, j = np.meshgrid(np.arange(n + 1), np.arange(n + 1), indexing="ij")
        keep = (i + j) <= n
        a, b = i[keep] / n, j[keep] / n
        c = 1 - a - b
        pts = (a[None, :, None] * sel[:, None, 0] + b[None, :, None] * sel[:, None, 1]
               + c[None, :, None] * sel[:, None, 2])
        out.append(pts.reshape(-1, 3))
    return np.concatenate(out)


def free_space(points, radius, lo, hi):
    """Boolean grid of ball-centre positions whose ball of `radius` touches no point."""
    shape = np.ceil((hi - lo) / GRID).astype(int)
    occ = np.zeros(shape)
    idx = np.round((points - lo) / GRID).astype(int)
    idx = idx[(idx >= 0).all(1) & (idx < shape).all(1)]
    occ[idx[:, 0], idx[:, 1], idx[:, 2]] = 1
    g = [np.fft.fftfreq(n, 1 / n) * GRID for n in shape]
    x, y, z = np.meshgrid(*g, indexing="ij")
    ker = ((x ** 2 + y ** 2 + z ** 2) <= radius ** 2).astype(float)
    conv = np.fft.irfftn(np.fft.rfftn(occ) * np.fft.rfftn(ker), s=list(shape), axes=(0, 1, 2))
    return conv < 0.5


def flood(free, start):
    """Region reachable from `start`; returns (escaped, reach)."""
    reach = np.zeros(free.shape, bool)
    reach[start] = True
    front = reach.copy()
    while front.any():
        new = np.zeros(free.shape, bool)
        new[1:] |= front[:-1]
        new[:-1] |= front[1:]
        new[:, 1:] |= front[:, :-1]
        new[:, :-1] |= front[:, 1:]
        new[:, :, 1:] |= front[:, :, :-1]
        new[:, :, :-1] |= front[:, :, 1:]
        new &= free & ~reach
        reach |= new
        front = new
        if reach[:, :, -1].any():          # above every obstacle: the ball is out
            return True, reach
    return False, reach


class Trap:
    """Ball-centre configuration space for one set of obstacle points; origin = ball centre."""

    def __init__(self, points, ball_r):
        self.points = points
        self.ball_r = ball_r
        top = points[:, 2].max()
        span = np.abs(points[:, :2]).max()
        # Grid of ball-centre positions. Along every axis it is at least as long as the point
        # cloud plus one ball diameter, so the circular FFT convolution never folds an obstacle
        # back into the grid; the top layer lies a ball radius above every obstacle, so a centre
        # that reaches it is out.
        self.lo = np.array([-span - ball_r, -span - ball_r, points[:, 2].min() - ball_r])
        self.hi = np.array([span + ball_r, span + ball_r, top + ball_r + 1.0])

    def trapped(self, margin):
        free = free_space(self.points, self.ball_r - margin, self.lo, self.hi)
        start = tuple(np.round((0 - self.lo) / GRID).astype(int))
        assert free[start], "the resting position collides: the model is wrong"
        escaped, reach = flood(free, start)
        if escaped:
            return False, None
        cells = np.argwhere(reach) * GRID + self.lo
        return True, {"lift": float(cells[:, 2].max()), "lateral": float(np.hypot(cells[:, 0], cells[:, 1]).max())}

    def critical_margin(self, hi=2.0, steps=7):
        if not self.trapped(0.0)[0]:
            return 0.0
        lo = 0.0
        for _ in range(steps):
            mid = (lo + hi) / 2
            if self.trapped(mid)[0]:
                lo = mid
            else:
                hi = mid
        return lo


def analyse(binary, name, overrides, build):
    import trimesh

    build.mkdir(exist_ok=True)
    stack = render(binary, "cradle", overrides, build / f"cradle-{name}.stl")
    case = render(binary, "pocket_clip", {"half": "right"}, build / f"clip-{name}.stl", CASE_SCAD)
    zc = stack["ball_centre_z"]
    R = stack["ball_d"] / 2
    centre = np.array([0, 0, zc])
    cradle = trimesh.load(build / f"cradle-{name}.stl", force="mesh")
    clip = trimesh.load(build / f"clip-{name}.stl", force="mesh")
    cp = sample_surface(cradle) - centre
    rp = sample_surface(clip) - centre
    # only the part of the cradle around the ball matters (cup and rim)
    cp = cp[(np.hypot(cp[:, 0], cp[:, 1]) < 16) & (cp[:, 2] > -R - 2)]

    out = {"ball_d": stack["ball_d"], "ball_centre_z": zc}
    open_cup = Trap(cp, R)
    out["without_clip_trapped"] = open_cup.trapped(0.0)[0]
    both = Trap(np.concatenate([cp, rp]), R)
    out["trapped"] = both.trapped(0.0)[0]
    # On the grid, points are snapped by up to GRID * sqrt(3) / 2 and a continuous escape path
    # becomes a chain of cells up to that far off it, so the grid can call a ball trapped that
    # really escapes with up to GRID * sqrt(3) of extra looseness. critical_margin is the grid
    # value, guaranteed_margin the bound that holds for the real geometry.
    out["critical_margin"] = both.critical_margin()
    out["guaranteed_margin"] = max(0.0, out["critical_margin"] - GRID * 3 ** 0.5)
    # exact vertical play of the centred ball before it touches a claw (no grid involved)
    allp = np.concatenate([cp, rp])
    lift = 0.0
    while lift < R and (np.linalg.norm(allp - [0, 0, lift + 0.01], axis=1) - R).min() > 0:
        lift += 0.01
    out["ball_lift_play"] = round(lift, 2)

    dist = np.linalg.norm(rp, axis=1) - R
    out["rest_gap"] = float(dist.min())
    # pulling the clip straight up: the closest claw point to the resting ball, per lift height
    lifts = np.arange(0, 2 * R + 2, 0.25)
    gaps = [float((np.linalg.norm(rp + [0, 0, d], axis=1) - R).min()) for d in lifts]
    out["pull_off_min_gap"] = min(gaps)

    az = np.degrees(np.arctan2(rp[:, 1], rp[:, 0]))
    out["clip_max_abs_az"] = float(np.abs(az).max())
    out["open_sector_deg"] = 360 - 2 * out["clip_max_abs_az"]
    out["clip_top_z"] = float(rp[:, 2].max() + zc)
    out["clip_bottom_z"] = float(rp[:, 2].min() + zc)
    out["clip_outer_r"] = float(np.hypot(rp[:, 0], rp[:, 1]).max())
    # the pins reach down beside the cup: their clearance to the cradle
    pins = rp[rp[:, 2] + zc < case["cover_z0"]]
    near = cp[(cp[:, 2] + zc > pins[:, 2].min() + zc - 1)] if len(pins) else cp[:0]
    d2 = min(float(np.min(((pins[i:i + 2000, None, :] - near[None, :, :]) ** 2).sum(-1)))
             for i in range(0, len(pins), 2000)) if len(pins) and len(near) else None
    out["pin_cradle_clearance"] = d2 ** 0.5 if d2 is not None else None
    return out


def main():
    binary = find_openscad(sys.argv[1] if len(sys.argv) > 1 else None)
    build = HERE / "build"
    data = {"grid_mm": GRID, "sample_mm": SAMPLE, "variants": {}}
    for name, ov in VARIANTS.items():
        res = analyse(binary, name, ov, build)
        data["variants"][name] = res
        print(f"{name:12s} trapped={res['trapped']} (open cup trapped={res['without_clip_trapped']}), "
              f"tolerance {res['critical_margin']:.2f} mm, rest gap {res['rest_gap']:.2f}, "
              f"guaranteed {res['guaranteed_margin']:.2f} mm, play up {res['ball_lift_play']:.2f}, "
              f"pull-off gap {res['pull_off_min_gap']:.2f}, open sector {res['open_sector_deg']:.0f} deg, "
              f"pin clearance to the cradle {res['pin_cradle_clearance']}")
        sys.stdout.flush()
    (HERE / "retention.json").write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
