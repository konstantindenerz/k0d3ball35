---
title: Project website with tabs for the real 3D files, PCBs, keymap and BOM
type: feature
priority: P2
status: done
area: doc
created: 2026-11-10
---

# Project website with tabs for the real 3D files, PCBs, keymap and BOM

## Context

`docs/` is the GitHub Pages site. Until now it was one generated page, the 3D exploded view
(`doc-exploded-view-3d`), with the case STLs inlined as base64 (3.5 MB). The exploded view is a
good overview, but it is stylised: nobody can look at the real printed parts, the boards or the
keymap on the page. The site becomes a project page with one tab ("sheet") per area.

## Decisions

- Tabs: Overview, Explorer (the exploded view), Case, Trackball, PCBs, Keymap. A Build & BOM tab
  was built and dropped again: the page shows the 3D files and links to the markdown instead of
  repeating it (BOM, build guide, roadmap and tickets stay in the repository).
- The page is static: hand-written `docs/index.html`, one ES module per tab in `docs/js/tabs/`,
  shared viewer in `docs/js/viewer.js`, data files in `docs/data/` written by `docs/build.py`
  (`make site`). No bundler; three.js from jsDelivr, pinned.
- 3D files are not copied into `docs/`: the published page loads them from
  raw.githubusercontent.com (main), localhost loads them from the working tree
  (`make site-serve`). `?ref=<branch>` previews a pushed branch.

## Acceptance criteria

- [x] Shell, router, title block, shared viewer, `make site`, `make site-serve`
- [x] Explorer ported, case meshes fetched instead of embedded
- [x] Case tab: every printable STL with size, volume, download
- [x] Trackball tab: cradle variants, retainer, ball, stack heights
- [x] PCBs tab: KiCad GLB per board, layer view, fab downloads (`make pcb-3d`)
- [x] Keymap tab generated from the ZMK keymap
- [x] Overview links to the markdown (BOM, build guide, firmware, roadmap, issues) instead of repeating it
- [x] Overview tab
- [x] `tests/test_site.py` covers the data, the asset paths and the shell
- [x] README, `spec/11-case.md` and `hardware/case/README.md` point at the new targets
- [x] Merged to main, so the published page shows the tabs (2026-11-10)
