#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write docs/img/share-card-cafe.jpg, the 1200 x 630 preview a link to the project page unfolds into.

Without it a link posted to LinkedIn, Mastodon, Slack or Discord is a bare URL: those scrapers
read `og:image` out of the page head and nothing else, they do not run JavaScript and they do not
look at the 3D viewer. The card is therefore the only part of this project most people will ever
see, which is why it names the maker.

Built as SVG and rasterised with cairosvg, the same path `scripts/gen_print_check.py` uses, so
there is no new dependency. The wordmark comes from `k0d3.logo`, the one source the case
engraving and the PCB silkscreen also read - the artwork is never copied.

The result is committed. It is not regenerated in CI: text rendering depends on the fonts
installed, so a rebuild elsewhere would differ byte for byte without anything being wrong.
`tests/test_site.py` checks the artefact instead - that it exists, that it is an image of exactly the
size the page claims, and that `og:image` points at it.

Usage: scripts/gen_share_card.py [OUT.jpg]
"""
from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

from k0d3 import logo
from k0d3.geometry import REPO

# A new card gets a new name: LinkedIn, Slack and co. cache og:image by URL for days, so
# overwriting the old file would keep showing the old picture in fresh link previews.
OUT = REPO / "docs" / "img" / "share-card-cafe.jpg"
RENDER = REPO / "spec" / "images" / "concept-render.png"

SIZE = (1200, 630)             # the size every scraper expects; og:image:width/height say so too
PAD = 48                       # inner margin of the text panel
PHOTO_W = 840                  # the 4:3 render at the card's height of 630
PANEL = "#11100E"
INK = "#F7F5F0"
MUTED = "#D8D2C6"
SANS = "Helvetica,Arial,sans-serif"

TITLE = "k0d3ball35"
SUBTITLE = ("Wireless split keyboard", "35 Choc keys", "19 mm trackball")
BYLINE = ("Designed and built by", "Konstantin Denerz")


def fit(src: Path, size: tuple[int, int]) -> str:
    """`src` scaled to cover `size` and centre-cropped, as a data URI.

    Scaling here rather than in the SVG keeps the embedded image at the card's own resolution:
    letting the renderer scale the 1448 x 1086 original would carry about three times the pixels
    into the PNG for no visible gain.
    """
    from PIL import Image

    im = Image.open(src).convert("RGB")
    scale = max(size[0] / im.width, size[1] / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left, top = (im.width - size[0]) // 2, (im.height - size[1]) // 2
    im = im.crop((left, top, left + size[0], top + size[1]))
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def wordmark(cell: float, x: float, y: float) -> str:
    """The owner wordmark, top-left at (x, y), from the same grid as the case engraving."""
    w, h = logo.size(cell)
    paths = []
    for poly in logo.polygons(cell):
        pts = " L ".join(f"{x + w / 2 + px:.2f},{y + h / 2 + py:.2f}" for px, py in poly)
        paths.append(f'<path d="M {pts} Z" fill="{INK}"/>')
    return "".join(paths)


def lines(x: float, y: float, step: float, size: int, weight: int, fill: str, texts) -> str:
    return "".join(f'<text x="{x}" y="{y + i * step:.0f}" font-family="{SANS}" font-size="{size}" '
                   f'font-weight="{weight}" fill="{fill}">{t}</text>' for i, t in enumerate(texts))


def build() -> str:
    """Text panel on the left, the whole render on the right.

    The render is 4:3 and the keyboard fills its lower half, so a full-bleed 1200 x 630 crop would
    either cut the scene or put the title over the keys. At the card's height the render is
    PHOTO_W wide; the rest is a plain panel the text cannot hide anything on.
    """
    w, h = SIZE
    photo_x = w - PHOTO_W
    mark_cell = 2.6
    _, mark_h = logo.size(mark_cell)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" \
width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{PANEL}" stop-opacity="1"/>
  <stop offset="1" stop-color="{PANEL}" stop-opacity="0"/>
</linearGradient></defs>
<rect width="{w}" height="{h}" fill="{PANEL}"/>
<image x="{photo_x}" y="0" width="{PHOTO_W}" height="{h}" xlink:href="{fit(RENDER, (PHOTO_W, h))}"/>
<rect x="{photo_x}" y="0" width="60" height="{h}" fill="url(#fade)"/>
<text x="{PAD}" y="150" font-family="{SANS}" font-size="58" font-weight="700" fill="{INK}" \
letter-spacing="-1.5">{TITLE}</text>
{lines(PAD, 200, 37, 27, 500, INK, SUBTITLE)}
{lines(PAD, 318, 28, 22, 400, MUTED, BYLINE)}
{wordmark(mark_cell, PAD, h - PAD - mark_h)}
</svg>
"""


def write(out: Path = OUT) -> Path:
    """Rasterise the card and save it as JPEG.

    JPEG, not PNG, because the card is three quarters photograph: the same image is 119 KB here
    against 895 KB as a PNG, and every scraper fetches it before it can show anything. Quality 86
    leaves no visible artefact on the type at this size.
    """
    import cairosvg                       # optional dependency, as in gen_print_check
    from PIL import Image

    png = cairosvg.svg2png(bytestring=build().encode(),
                           output_width=SIZE[0], output_height=SIZE[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.open(io.BytesIO(png)).convert("RGB").save(
        out, format="JPEG", quality=86, optimize=True, progressive=True)
    return out


def main(argv: list[str]) -> int:
    out = Path(argv[1]) if len(argv) > 1 else OUT
    print("wrote", write(out).relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
