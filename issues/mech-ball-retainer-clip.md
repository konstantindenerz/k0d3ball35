---
title: Optional clip-on ball retainer with two claws away from the thumb
type: feature
priority: P2
status: in-progress
area: mech
created: 2026-11-10
---

# Optional clip-on ball retainer with two claws away from the thumb

## Context

The cradle cup is open by design: the rim stops 1 mm below the ball equator, the ball rests on
three bearings by gravity, the thumb reaches the equator (`hardware/trackball-cradle/README.md`,
"Ball retention"). The claw ring of r1 was removed on 2026-11-06 in favour of the case lid
(`mech-case-lid`), which only helps while it is on. Two things brought the retainer back:

- The Keychron Orca echo (19 mm ball, thumb trackball) had to add retaining tabs after its
  mock-up lost the ball; hands-on reviews also criticise its raised ring on the thumb side.
- Keyball owners report the stock holder lets the ball pop out on long swipes (T1 in
  `spec/10-lessons-from-keyball.md`).

So the retainer must hold the ball when the half is turned over, never touch it in use, keep the
thumb side as open as the bare cup, and come off by hand so the ball can be cleaned.

Design (all in `hardware/trackball-cradle/cradle.scad`, parameters `retainer_*` in `params.scad`):

- A ring that sits on a 0.8 mm 45 degree chamfer on the outer edge of the cup rim, flush with
  the rim top, with a skirt down the outside of the cup.
- Two claws: pieces of a spherical shell 0.4 mm off the ball, 6 mm wide, at +-80 degrees from +x,
  rising to 0.525 R above the ball centre (5.0 mm, +12.6 mm over the PCB for the 19 mm ball).
  The thumb keys sit at -171 and 180 degrees seen from the ball; above the rim a 159 degree
  sector around them is free.
- Four snap fingers (0.8 mm, slit free, 0.25 mm undercut, 30 degree release face) click into
  pockets in the cup wall. The fingers at 30/330 degrees are 3 mm wide, the ones at 150/210
  degrees 2 mm, so the ring only fits one way round. Arches clear the bearing bosses.

Why two claws: a parameter sweep with a configuration-space flood fill showed that the cup, whose
rim sits only 1 mm below the equator, already stops the ball moving sideways unless it lifts a
long way, so two claws that stop the lift are enough. A third claw on the far side added nothing;
claws at +-70 degrees held clearly worse than at +-80 to +-90. +-80 keeps the claws further from
the thumb than +-90 for about the same hold.

## Acceptance criteria

- [x] `part = "retainer"` renders a watertight ring for the 19.05 mm and the 25 mm ball (the 25 mm
      ring is the same for the pocket and the cutout mount); STLs in `hardware/trackball-cradle/stl/`
- [x] The cradle carries the rim chamfer and the four finger pockets, still has nothing above the
      rim, and works unchanged without the ring; ring and cradle do not overlap (`part = "clash"`
      renders empty for all three variants)
- [x] `retention.py` (`make retention`, `retention.json`): ball trapped in all variants, at least
      0.5 mm guaranteed tolerance (19 mm: 0.67 mm, after subtracting the analysis grid error);
      the open cup without the ring lets the ball out in the same analysis (negative control)
- [x] Claws 0.39 mm from the ball at rest; pulling the ring straight up never brings a claw closer;
      vertical play 0.82 mm (analytic 0.85)
- [x] Thumb side open: no ring material above the rim within the 159 degree sector, thumb keys at
      least 60 degrees from the nearest claw edge
- [x] Fits the case: 1.1 mm inside the 28 mm pocket, 1.4 mm under the closed lid roof, clear of the
      lid hinge strip, 1.8 mm from the FFC corridor, 1.0 mm from the bearing bosses
- [x] Snap finger strain 2.3 percent (PETG recommended), finger tips above the PCB top
- [x] `tests/test_retainer.py`; a mutation with the claws moved to the thumb side fails it
- [ ] Test print in PETG with the cradle: clips on and off by hand, ball stays in upside down and
      when shaken, the ball never touches a claw, long thumb swipes in every direction do not
      catch a claw; tune `retainer_nub` if the snap is too hard or rattles
- [ ] Decide after the test print whether the retainer is the default for the right half

## Notes

Retention numbers are for the geometry; the comfort of the claws under a real thumb and the snap
force can only be judged on a print. The analysis grid (0.2 mm) inflates obstacles by up to
0.17 mm and can miss a passage that narrow, so the grid's critical tolerance (1.02 mm) is reduced
by 0.2 x sqrt(3) = 0.35 mm to the guaranteed 0.67 mm; finer grids converge to about 0.8 mm.
Related: `mech-case-lid` (transport cover), `mech-trackball-cradle`, `mech-case-ball-pocket`.
