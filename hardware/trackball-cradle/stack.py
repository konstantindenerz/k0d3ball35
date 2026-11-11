#!/usr/bin/env python3
"""Run OpenSCAD on cradle.scad for several variants and collect the STACK echo
values into stack.json. Usage: ./stack.py [openscad-binary]"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
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


def stack_for(binary, overrides):
    cmd = [binary, "--backend", "manifold", "-D", 'part="cradle"']
    for k, v in overrides.items():
        cmd += ["-D", define(k, v)]
    out = HERE / "build" / "stack.echo"
    out.parent.mkdir(exist_ok=True)
    cmd += ["-o", str(out), str(HERE / "cradle.scad")]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    values = {}
    for line in out.read_text().splitlines():
        m = re.search(r'STACK (\w+)=(-?[\d.]+)', line)
        if m:
            values[m.group(1)] = float(m.group(2))
    return values


def main():
    binary = find_openscad(sys.argv[1] if len(sys.argv) > 1 else None)
    version = subprocess.run([binary, "--version"], capture_output=True, text=True)
    data = {"openscad": (version.stdout + version.stderr).strip(), "variants": {}}
    for name, ov in VARIANTS.items():
        data["variants"][name] = stack_for(binary, ov)
    (HERE / "stack.json").write_text(json.dumps(data, indent=2) + "\n")
    for name, v in data["variants"].items():
        print(f"{name:12s} ball top +{v['ball_top_above_pcb_top']:.1f} mm, "
              f"lowest point {min(v['lowest_plastic_z'], v['lowest_sensor_board_z']):.1f} mm, "
              f"envelope above PCB {v['envelope_d_above_pcb']:.1f} mm, "
              f"footprint {v['footprint_x']:.0f} x {v['footprint_y']:.0f} mm"
              + (f", case screws {v['case_screw_sp']:.0f} mm apart" if "case_screw_sp" in v else ""))


if __name__ == "__main__":
    main()
