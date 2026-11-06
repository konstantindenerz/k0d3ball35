# k0d3ball35 build entry points.
# Override tool paths on the command line, e.g. `make drc KICAD_CLI=kicad-cli`.

KICAD_CLI ?= /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PY        ?= .venv/bin/python
KPY       ?= /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
JAVA      ?= java
FREEROUTING_JAR ?= $(BUILD)/freerouting.jar
FREEROUTING_URL := https://github.com/freerouting/freerouting/releases/download/v2.5.0/freerouting-2.5.0.jar

# The two main PCBs; `make route HALVES=right` builds one half only.
HALVES    ?= left right

LAYOUT     := hardware/layout/k0d3ball35.yaml
LAYOUT_OUT := hardware/layout/output
HALF_SCHS  := $(foreach h,$(HALVES),hardware/$(h)-pcb/k0d3ball35-$(h).kicad_sch)
HALF_PCBS  := $(foreach h,$(HALVES),hardware/$(h)-pcb/k0d3ball35-$(h).kicad_pcb)
SENSOR_DIR := hardware/sensor-pcb
SENSOR_SCH := $(SENSOR_DIR)/k0d3ball35-sensor.kicad_sch
SENSOR_PCB := $(SENSOR_DIR)/k0d3ball35-sensor.kicad_pcb
BUILD      := build

SCHS := $(wildcard $(HALF_SCHS) $(SENSOR_SCH))
PCBS := $(wildcard $(HALF_PCBS) $(SENSOR_PCB))

.PHONY: all layout sch pcb route board erc drc gerbers freerouting-jar firmware test issues docs-check case-data case-logo case exploded clean help

all: layout board erc drc gerbers

help:
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

layout: ## Generate points-<half>.json, outline-<half>.dxf and previews from the layout yaml
	$(PY) scripts/gen_layout.py

sch: ## Generate the schematics of both halves from the layout and the design spec
	$(PY) scripts/gen_schematic.py $(HALVES)

pcb: ## Place footprints and assign nets on both main PCBs
	$(PY) scripts/gen_pcb.py $(HALVES)

route: ## Regenerate, autoroute (freerouting) and verify the main PCBs; retries until DRC is clean
	KICAD_CLI=$(KICAD_CLI) KPY=$(KPY) PY=$(PY) JAVA=$(JAVA) FREEROUTING_JAR=$(FREEROUTING_JAR) scripts/build_board.sh $(HALVES)

board: route ## Alias for route

freerouting-jar: ## Download freerouting 2.5.0 into build/
	@mkdir -p $(BUILD)
	@test -f $(FREEROUTING_JAR) || curl -sL -o $(FREEROUTING_JAR) $(FREEROUTING_URL)
	@ls -la $(FREEROUTING_JAR)

erc: ## Electrical rules check on every schematic
	@mkdir -p $(BUILD)
	@for s in $(SCHS); do \
	  echo "ERC $$s"; \
	  $(KICAD_CLI) sch erc --exit-code-violations --severity-error --format json \
	    -o $(BUILD)/$$(basename $$s .kicad_sch).erc.json $$s || exit 1; \
	done

drc: ## Design rules check with schematic parity on every PCB
	@mkdir -p $(BUILD)
	@for p in $(PCBS); do \
	  echo "DRC $$p"; \
	  $(KICAD_CLI) pcb drc --exit-code-violations --severity-error --schematic-parity --format json \
	    -o $(BUILD)/$$(basename $$p .kicad_pcb).drc.json $$p || exit 1; \
	done

gerbers: ## Export gerbers, drill files, zip, STEP, renders, schematic PDF, BOM and position file per half
	KICAD_CLI=$(KICAD_CLI) scripts/export.sh $(HALVES)

firmware: ## Build ZMK firmware locally with docker (CI is the reference build)
	@if command -v docker >/dev/null 2>&1; then \
	  scripts/build_firmware.sh; \
	else \
	  echo "docker not found. Firmware is built by .github/workflows/firmware.yml;"; \
	  echo "see docs/05-firmware.md for a local west setup."; \
	fi

test: ## Run the test suite
	$(PY) -m pytest -q

issues: ## Regenerate issues/README.md from the ticket frontmatter
	$(PY) scripts/issues.py

case-data: ## Regenerate hardware/case/data.scad (layout facts for the printed case)
	$(MAKE) -C hardware/case data PYTHON=../../$(PY)

case-logo: ## Regenerate logo_data.scad and docs/images/logo.svg from docs/images/logo.png
	$(MAKE) -C hardware/case logo PYTHON=../../$(PY)

case: ## Render the printed case: STLs, floor DXFs, previews and stack.json (needs OpenSCAD)
	$(MAKE) -C hardware/case all PYTHON=../../$(PY)

exploded: ## Rebuild docs/exploded-view/index.html (embeds the case STLs; run after `make case`)
	$(PY) docs/exploded-view/build.py

docs-check: ## Run only the documentation and ticket checks
	$(PY) -m pytest -q tests/test_docs.py tests/test_issues.py tests/test_license.py

clean:
	rm -rf $(BUILD) .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
