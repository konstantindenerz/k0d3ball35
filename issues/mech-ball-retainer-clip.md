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

Design (all in `hardware/trackball-cradle/cradle.scad`, parameters `retainer_*` in `params.scad`),
as rebuilt for r2.4:

- A ring that sits on a 0.8 mm 45 degree chamfer on the outer edge of the cup rim, with a short
  skirt down the outside of the cup and a 3 mm collar above the rim.
- Two claws: pieces of a spherical shell 0.4 mm off the ball, 6 mm wide, at +-80 degrees from +x,
  rising to 0.525 R above the ball centre (5.0 mm, +9.43 mm over the PCB). Above the rim a
  156 degree sector around the thumb keys is free.
- Four snap fingers at 270, 300, 330 and 0 degrees, rooted in the collar above the rim (the ball
  dropped 3.15 mm in r2.4 and the skirt alone is too short to bend a finger in): strain 0.0185
  against the 0.025 limit. Widths 2/3/3/2 mm, so the ring fits one way only.
- The skirt is relieved over the tilted sensor sleeve (a 113 degree sector, 0.8 mm clear); the
  collar bridges it and carries the claw on that side. Cost: that stretch of collar is a ~15 mm
  unsupported overhang, so the clip prints with supports there.

Why two claws: a parameter sweep with a configuration-space flood fill showed that the cup, whose
rim sits only 1 mm below the equator, already stops the ball moving sideways unless it lifts a
long way, so two claws that stop the lift are enough. A third claw on the far side added nothing;
claws at +-70 degrees held clearly worse than at +-80 to +-90. +-80 keeps the claws further from
the thumb than +-90 for about the same hold.

## Acceptance criteria

- [x] `part = "retainer"` renders a watertight ring for the 19.05 mm ball, `stl/retainer-19mm.stl`
- [x] The cradle carries the rim chamfer and the four finger pockets, still has nothing above the
      rim, and works unchanged without the ring; ring and cradle do not overlap (`part = "clash"`
      renders empty)
- [x] `retention.py` (`make retention`, `retention.json`): ball trapped, at least
      0.5 mm guaranteed tolerance (0.67 mm, after subtracting the analysis grid error);
      the open cup without the ring lets the ball out in the same analysis (negative control)
- [x] Claws 0.39 mm from the ball at rest; pulling the ring straight up never brings a claw closer;
      vertical play 0.82 mm (analytic 0.85)
- [x] Thumb side open: no ring material above the rim within the 156 degree sector, thumb keys at
      least 60 degrees from the nearest claw edge
- [x] Fits the case: 1.1 mm inside the 28 mm pocket, 5.1 mm under the closed lid roof, finger tips
      1.0 mm above the PCB top (clear of the FFC gap), 0.8 mm from the sensor sleeve
- [x] Snap finger strain 1.85 percent against the 2.5 percent limit (PETG recommended)
- [x] `tests/test_retainer.py`; a mutation with the claws moved to the thumb side fails it
- [ ] Test print in PETG with the cradle, supports under the relieved collar: clips on and off by hand, ball stays in upside down and
      when shaken, the ball never touches a claw, long thumb swipes in every direction do not
      catch a claw; tune `retainer_nub` if the snap is too hard or rattles
- [ ] Decide after the test print whether the retainer is the default for the right half

## Notes

Retention numbers are for the geometry; the comfort of the claws under a real thumb and the snap
force can only be judged on a print. The analysis grid (0.2 mm) inflates obstacles by up to
0.17 mm and can miss a passage that narrow, so the grid's critical tolerance (1.02 mm) is reduced
by 0.2 x sqrt(3) = 0.35 mm to the guaranteed 0.67 mm; finer grids converge to about 0.8 mm.
Related: `mech-case-lid` (transport cover), `mech-trackball-cradle`, `mech-case-ball-pocket`.

2026-11-11 (r2.4): rebuilt for the lower ball and the tilted sensor sleeve: fingers moved into a
collar above the rim (in the old skirt the strain would have been 0.35), skirt relieved over the
sleeve, fingers at 270/300/330/0. Mesh watertight, `tests/test_retainer.py` 14 of 14 green.

2026-11-11 (pocket cover bezel): the clip moved from the cup rim onto the case's pocket cover.
The cover had to keep a 26.5 mm hole (plus a funnel) only so the cup-mounted ring could pass,
which left a 5 mm ring round the ball; the user wanted the gap small. The cover is now a bezel
over the cup rim (20.55 mm hole, 0.75 mm round the ball), and the clip is a flat C-ring on the
cover with the same two claws, held by two split snap pins in two 2.4 mm holes of the cover
(`hardware/case/tray.scad` `pocket_clip`, parameters `clip_*` in `hardware/case/params.scad`,
`stl/pocket-clip-right.stl`, centred on the ball). The cradle lost the finger pockets, the
`retainer_*` parameters and `retainer-19mm.stl`; `retention.py` moved to `hardware/case/` and
reads the cradle STL from there. Same result: trapped with 0.67 mm guaranteed tolerance, 0.39 mm
off the ball at rest, pull-off never closer, 156 degrees open, pins 0.82 mm from the cradle,
prong strain 2.2 percent (the first cut was 3.4 percent, the test caught it: slit widened to
0.9 mm, undercut 0.12 mm). It prints pins down with supports under the ring. Open: the snap
force on a print (`clip_pin_barb`), the 1.2 mm cover plate's stiffness.
