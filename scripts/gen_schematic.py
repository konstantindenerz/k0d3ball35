#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the schematic and project files of one or both halves.

    scripts/gen_schematic.py [left|right ...]      (default: both)

Writes hardware/<half>-pcb/k0d3ball35-<half>.kicad_sch, .kicad_pro, the library tables
pointing at the shared hardware/lib/, and regenerates hardware/lib/k0d3ball35-main.kicad_sym.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from k0d3.geometry import HALVES, REPO, load_layout  # noqa: E402
from k0d3.netlist import LIB, build_components  # noqa: E402
from k0d3.pcb import project_json  # noqa: E402
from k0d3.schematic import build_schematic, symbols  # noqa: E402

LIB_DIR = REPO / "hardware" / "lib"

SYM_LIB_TABLE = ('(sym_lib_table\n  (version 7)\n'
                 f'  (lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/../lib/{LIB}-main.kicad_sym")(options "")(descr "{LIB} main PCB symbols"))\n)\n')
FP_LIB_TABLE = ('(fp_lib_table\n  (version 7)\n'
                f'  (lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/../lib/{LIB}.pretty")(options "")(descr "{LIB} project footprints"))\n)\n')


def board_dir(half: str) -> Path:
    return REPO / "hardware" / f"{half}-pcb"


def board_name(half: str) -> str:
    return f"{LIB}-{half}"


def write_symbol_library() -> Path:
    lib = LIB_DIR / f"{LIB}-main.kicad_sym"
    lib.parent.mkdir(parents=True, exist_ok=True)
    lib.write_text(f"(kicad_symbol_lib (version 20231120) (generator \"{LIB}\") (generator_version \"1.0\")\n"
                   + "\n".join(sym.sexpr().replace(f'(symbol "{LIB}:{sym.name}"', f'(symbol "{sym.name}"', 1) for sym in symbols().values()) + "\n)\n")
    return lib


def generate(half: str) -> int:
    layout = load_layout(half)
    comps = build_components(layout)
    out = board_dir(half)
    out.mkdir(parents=True, exist_ok=True)
    name = board_name(half)
    (out / f"{name}.kicad_sch").write_text(build_schematic(comps, half, layout.cfg["revision"]))
    (out / f"{name}.kicad_pro").write_text(project_json(name, comps, half))
    (out / "sym-lib-table").write_text(SYM_LIB_TABLE)
    (out / "fp-lib-table").write_text(FP_LIB_TABLE)
    print(f"wrote {out / (name + '.kicad_sch')} with {len(comps)} components")
    return len(comps)


def main(argv: list[str]) -> int:
    halves = argv or list(HALVES)
    bad = [h for h in halves if h not in HALVES]
    if bad:
        print(f"unknown half {bad}, expected one of {HALVES}", file=sys.stderr)
        return 2
    write_symbol_library()
    for half in halves:
        generate(half)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
