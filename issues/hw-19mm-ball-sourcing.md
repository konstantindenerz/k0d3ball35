---
title: Secure a repeatable supply of 19.05 mm trackballs and test their surface
type: task
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Secure a repeatable supply of 19.05 mm trackballs and test their surface

## Context

r2 uses a 19.05 mm (3/4 inch) ball (r1: 25 mm, see `docs/00-feasibility.md` section 4a for the
research). Sources: 3/4 inch POM (Delrin) bearing balls, grade G1/G2, a few euros per pack of 10 to
20 on Amazon or AliExpress (what torabo-tsuki LP ships as its 19.05 mm option); the PandaKB TB19
phenolic ball made for split keyboards (11.90 USD); precision ball suppliers such as kugel-winnie.de.
POM balls are industrial parts, so the surface finish varies between suppliers, and some plastics
track badly on optical sensors (`hw-ball-colour-tracking-test`). A 19 mm ball also tracks
differently than 25 mm: the same finger travel rotates it more and it has almost no inertia, so the
default CPI is higher (`fw-cpi-tuning-19mm`).

## Acceptance criteria

- [ ] A pack of 3/4 inch POM balls and one PandaKB TB19 on hand before the first cradle print
- [ ] Three balls from the pack and the TB19 tested on the sensor board: cursor path straight, no dropouts, note which surface tracks best
- [x] `docs/03-bom.md` lists at least two sources with price and a note on surface finish
- [ ] Decision recorded whether the 25 mm pocket cradle ships as a fallback (see `hw-25mm-cradle-fallback`)

## Notes

Renamed from hw-25mm-ball-sourcing on 2026-11-06. Avoid glossy white and translucent balls; a matte
or lightly textured POM ball is the target.
