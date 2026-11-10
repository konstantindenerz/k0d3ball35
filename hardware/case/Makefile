# k0d3ball35 printed case build
# Requires OpenSCAD 2025.x or newer with the Manifold backend (tested with 2026.10.11,
# `brew install --cask openscad@snapshot`) and the repository venv for the data generator.
#
# data.scad is generated from the layout (scripts/gen_case.py) and committed; `make data`
# refreshes it. The left half is mirrored inside case.scad, both halves share the sources.

OPENSCAD ?= $(shell command -v openscad 2>/dev/null || echo /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD)
OSC       = $(OPENSCAD) --backend manifold
PYTHON   ?= ../../.venv/bin/python
# cameras look at the exported (print frame) scene: y and the turn about z are those of the
# layout-frame view mirrored in y (target y -> -y, rot_z -> 180 - rot_z)
CAM_ASM   = --camera=-10,-30,0,55,0,155,400 --imgsize=1400,1000 --colorscheme=Tomorrow
CAM_SEC   = --camera=-13,-66,0,75,0,30,230 --imgsize=1400,1000 --colorscheme=Tomorrow
CAM_BOX   = --camera=-58,-22,5,60,0,240,150 --imgsize=1400,1000 --colorscheme=Tomorrow
CAM_FOOT  = --camera=-70,-30,10,78,0,155,460 --imgsize=1400,1000 --colorscheme=Tomorrow
CAM_FOLD  = --camera=-31,-30,10,60,0,140,260 --imgsize=1400,1000 --colorscheme=Tomorrow
CAM_HINGE = --camera=-31,9,14,70,0,180,60 --imgsize=1400,1000 --colorscheme=Tomorrow
CAM_BOT   = --camera=-10,-30,-10,125,0,155,400 --imgsize=1400,1000 --colorscheme=Tomorrow
CAM_CAP   = --camera=-59.5,-21.9,8.7,0,0,0,170 --imgsize=700,1200 --colorscheme=Tomorrow
SRC       = case.scad params.scad data.scad logo_data.scad common.scad logo.scad tray.scad lid.scad
LEFT      = -D 'half="left"'
RIGHT     = -D 'half="right"'

STL = stl/tray-left.stl stl/tray-right.stl stl/box-cap-left.stl stl/box-cap-right.stl \
      stl/lid-left.stl stl/lid-right.stl stl/lid-outer-left.stl stl/lid-outer-right.stl \
      stl/lid-inner-left.stl stl/lid-inner-right.stl stl/lid-folded-left.stl stl/lid-folded-right.stl \
      stl/pocket-test-right.stl
DXF = dxf/floor-left.dxf dxf/floor-right.dxf
PNG = preview/assembly-left.png preview/assembly-right.png preview/section-right.png \
      preview/lid-on-right.png preview/lid-foot-right.png preview/lid-folded-right.png \
      preview/lid-hinge-right.png preview/box-right.png \
      preview/tray-bottom-right.png preview/cap-logo-right.png

.PHONY: all data logo stls dxfs previews stack clean
all: data logo stls dxfs previews stack
stls: $(STL)
dxfs: $(DXF)
previews: $(PNG)

data: data.scad
data.scad: ../../scripts/gen_case.py ../../scripts/k0d3/geometry.py ../layout/k0d3ball35.yaml
	cd ../.. && PYTHONPATH=scripts $(subst ../../,,$(PYTHON)) scripts/gen_case.py

# one run writes logo_data.scad and the vector master spec/images/logo.svg; only the first is
# a target here, grouped targets would need make 4.3 and this repo builds with Apple's 3.81
logo: logo_data.scad
logo_data.scad: ../../scripts/gen_logo.py ../../spec/images/logo.png
	cd ../.. && $(subst ../../,,$(PYTHON)) scripts/gen_logo.py

stl dxf preview:
	@mkdir -p $@

stl/tray-left.stl: $(SRC) | stl
	$(OSC) -D 'part="tray"' $(LEFT) -o $@ case.scad
stl/tray-right.stl: $(SRC) | stl
	$(OSC) -D 'part="tray"' $(RIGHT) -o $@ case.scad
stl/box-cap-left.stl: $(SRC) | stl
	$(OSC) -D 'part="box_cap"' $(LEFT) -o $@ case.scad
stl/box-cap-right.stl: $(SRC) | stl
	$(OSC) -D 'part="box_cap"' $(RIGHT) -o $@ case.scad
stl/lid-left.stl: $(SRC) | stl
	$(OSC) -D 'part="lid"' $(LEFT) -o $@ case.scad
stl/lid-right.stl: $(SRC) | stl
	$(OSC) -D 'part="lid"' $(RIGHT) -o $@ case.scad
stl/lid-outer-left.stl: $(SRC) | stl
	$(OSC) -D 'part="lid_outer"' $(LEFT) -o $@ case.scad
stl/lid-outer-right.stl: $(SRC) | stl
	$(OSC) -D 'part="lid_outer"' $(RIGHT) -o $@ case.scad
stl/lid-inner-left.stl: $(SRC) | stl
	$(OSC) -D 'part="lid_inner"' $(LEFT) -o $@ case.scad
stl/lid-inner-right.stl: $(SRC) | stl
	$(OSC) -D 'part="lid_inner"' $(RIGHT) -o $@ case.scad
stl/lid-folded-left.stl: $(SRC) | stl
	$(OSC) -D 'part="lid_folded"' $(LEFT) -o $@ case.scad
stl/lid-folded-right.stl: $(SRC) | stl
	$(OSC) -D 'part="lid_folded"' $(RIGHT) -o $@ case.scad
stl/pocket-test-right.stl: $(SRC) | stl
	$(OSC) -D 'part="pocket_test"' $(RIGHT) -o $@ case.scad

dxf/floor-left.dxf: $(SRC) | dxf
	$(OSC) -D 'part="floor2d"' $(LEFT) -o $@ case.scad
dxf/floor-right.dxf: $(SRC) | dxf
	$(OSC) -D 'part="floor2d"' $(RIGHT) -o $@ case.scad

preview/assembly-left.png: $(SRC) | preview
	$(OSC) --render -D 'part="assembly"' $(LEFT) $(CAM_ASM) -o $@ case.scad
preview/assembly-right.png: $(SRC) | preview
	$(OSC) --render -D 'part="assembly"' $(RIGHT) $(CAM_ASM) -o $@ case.scad
preview/section-right.png: $(SRC) | preview
	$(OSC) --render -D 'part="section"' $(RIGHT) $(CAM_SEC) -o $@ case.scad
preview/lid-on-right.png: $(SRC) | preview
	$(OSC) --render -D 'part="lid_on"' $(RIGHT) $(CAM_ASM) -o $@ case.scad
preview/lid-foot-right.png: $(SRC) | preview
	$(OSC) --render -D 'part="lid_foot"' $(RIGHT) $(CAM_FOOT) -o $@ case.scad
preview/lid-folded-right.png: $(SRC) | preview
	$(OSC) --render -D 'part="lid_folded"' $(RIGHT) $(CAM_FOLD) -o $@ case.scad
preview/lid-hinge-right.png: $(SRC) | preview
	$(OSC) --render -D 'part="lid"' $(RIGHT) $(CAM_HINGE) -o $@ case.scad
preview/tray-bottom-right.png: $(SRC) | preview
	$(OSC) --render -D 'part="tray"' $(RIGHT) $(CAM_BOT) -o $@ case.scad
preview/cap-logo-right.png: $(SRC) | preview
	$(OSC) --render -D 'part="box_cap"' $(RIGHT) $(CAM_CAP) -o $@ case.scad
preview/box-right.png: $(SRC) | preview
	$(OSC) --render -D 'part="assembly"' $(RIGHT) $(CAM_BOX) -o $@ case.scad

stack: stack.json
stack.json: $(SRC) stack.py
	$(PYTHON) stack.py $(OPENSCAD)

clean:
	rm -rf build stl dxf preview stack.json
