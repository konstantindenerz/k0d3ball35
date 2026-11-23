# k0d3ball35 printed keycaps build
# Requires OpenSCAD 2025.x or newer with the Manifold backend (tested with 2026.10.11,
# `brew install --cask openscad@snapshot`).
#
# After the fit test: set stem_fit in params.scad to the tab that fits and run make again, so the
# committed STLs stay what the sources say (tests/test_keycaps.py renders and compares them).

OPENSCAD ?= $(shell command -v openscad 2>/dev/null || echo /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD)
OSC       = $(OPENSCAD) --backend manifold
CAM       = --camera=0,0,0,50,0,15,115 --imgsize=1200,700 --colorscheme=Tomorrow

STL = stl/keycap-1u.stl stl/keycap-1u-homing.stl stl/keycap-thumb.stl stl/keycap-fit-test.stl
PNG = preview/keycaps.png

.PHONY: all stls previews clean
all: stls previews
stls: $(STL)
previews: $(PNG)

stl preview:
	@mkdir -p $@

stl/keycap-1u.stl: keycaps.scad params.scad | stl
	$(OSC) -D 'part="finger"' -o $@ $<
stl/keycap-1u-homing.stl: keycaps.scad params.scad | stl
	$(OSC) -D 'part="homing"' -o $@ $<
stl/keycap-thumb.stl: keycaps.scad params.scad | stl
	$(OSC) -D 'part="thumb"'  -o $@ $<
# the ladder sets its own fits
stl/keycap-fit-test.stl: keycaps.scad params.scad | stl
	$(OSC) -D 'part="fit_test"' -o $@ $<

preview/keycaps.png: keycaps.scad params.scad | preview
	$(OSC) --render -D 'part="display"' $(CAM) -o $@ $<

clean:
	rm -rf stl preview
