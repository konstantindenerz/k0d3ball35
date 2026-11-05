---
title: Secure a repeatable supply of 25 mm trackballs
type: task
priority: P1
status: open
area: hw
created: 2026-11-05
---

# Secure a repeatable supply of 25 mm trackballs

## Context

The design uses a 25 mm ball. Consumer 25 mm balls are rare: Perixx PERIPRO-305 (Perixx GmbH, EU store,
about 12 EUR, frequently out of stock) and Elecom M-B25SV / M-B25RD (released 2024 for the Relacon, eBay
imports). Industrial alternatives are 25 mm POM or ceramic bearing balls from AliExpress, as used in the
reference build from the video. A 25 mm ball also tracks differently than 34 mm: the same finger travel
rotates it more, so the default CPI must be lower (see fw-cpi-tuning-25mm).

## Acceptance criteria

- [ ] Two 25 mm balls on hand before the first cradle print (one consumer polished ball, one POM or ceramic)
- [ ] `docs/03-bom.md` lists at least two sources with price and a note on surface finish (matte polished tracks better than glossy)
- [ ] Decision recorded whether the 34 mm cradle ships as a fallback (see hw-34mm-cradle-option)

## Notes

Keyball 34 to 25 mm conversion reports mention twitchy tracking; the ball surface matters as much as the diameter.
