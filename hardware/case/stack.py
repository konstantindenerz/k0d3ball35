#!/usr/bin/env python3
"""Run OpenSCAD on case.scad for both halves (and the 25 mm fallback) and collect the STACK
echo values into stack.json. Usage: ./stack.py [openscad-binary]"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VARIANTS = {
    "left": {"half": "left"},
    "right": {"half": "right"},
    "right-25mm": {"half": "right", "ball_d": 25, "notch_apothem": 16.5, "pocket_d": 35, "ball_top_z": 23.05},
}


def find_openscad(arg=None):
    for cand in [arg, shutil.which("openscad"), "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"]:
        if cand and Path(cand).exists():
            return cand
    raise SystemExit("openscad not found")


def define(key, value):
    return f'{key}="{value}"' if isinstance(value, str) else f"{key}={value}"


def stack_for(binary, overrides):
    cmd = [binary, "--backend", "manifold", "-D", 'part="tray"']
    for k, v in overrides.items():
        cmd += ["-D", define(k, v)]
    out = HERE / "build" / "stack.echo"
    out.parent.mkdir(exist_ok=True)
    cmd += ["-o", str(out), str(HERE / "case.scad")]
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
        print(f"{name:10s} base {v['base_z']:.1f}, key floor {v['floor_z_key']:.1f}, rim {v['rim_z']:.1f}, "
              f"box top {v['box_top_z']:.1f}, lid roof under {v['lid_roof_under_z']:.1f}, lid top {v['lid_top_z']:.1f}, "
              f"ball {'yes' if v['has_ball'] else 'no'}")


if __name__ == "__main__":
    main()
