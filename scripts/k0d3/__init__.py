# SPDX-License-Identifier: MIT
"""Design generators for the k0d3ball36 keyboard.

geometry  - key positions, outline and clearance checks from hardware/layout/k0d3ball36.yaml
netlist   - matrix / controller / connector nets shared by schematic and PCB
sexpr     - tiny helpers to emit KiCad s-expressions
footprints- reversible footprints emitted straight into the PCB file
schematic - KiCad 10 schematic generator
pcb       - KiCad 10 board generator (unrouted)
"""
