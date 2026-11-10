#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Write docs/img/share-card.jpg, the 1200 x 630 preview a link to the project page unfolds into.

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

OUT = REPO / "docs" / "img" / "share-card.jpg"
RENDER = REPO / "spec" / "images" / "concept-render.png"

SIZE = (1200, 630)             # the size every scraper expects; og:image:width/height say so too
MARGIN = 64
INK = "#F7F5F0"
MUTED = "#D8D2C6"
SANS = "Helvetica,Arial,sans-serif"

TITLE = "k0d3ball35"
SUBTITLE = "Wireless split keyboard · 35 Choc keys · 19 mm trackball"
BYLINE = "Designed and built by Konstantin Denerz"


def cover(src: Path, size: tuple[int, int]) -> str:
    """`src` scaled to cover `size` and centre-cropped, as a data URI.

    Cropping here rather than in the SVG keeps the embedded image at the card's own resolution:
    letting the renderer scale a 1536 x 1024 original would carry about three times the pixels
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
    """The owner wordmark, baseline-left at (x, y), from the same grid as the case engraving."""
    w, h = logo.size(cell)
    paths = []
    for poly in logo.polygons(cell):
        pts = " L ".join(f"{x + w / 2 + px:.2f},{y + h / 2 + py:.2f}" for px, py in poly)
        paths.append(f'<path d="M {pts} Z" fill="{INK}"/>')
    return "".join(paths)


def build() -> str:
    w, h = SIZE
    img = cover(RENDER, SIZE)
    mark_cell = 3.2
    mark_w, mark_h = logo.size(mark_cell)
    base = h - MARGIN
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" \
width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#11100E" stop-opacity="0"/>
  <stop offset="0.5" stop-color="#11100E" stop-opacity="0.5"/>
  <stop offset="0.78" stop-color="#11100E" stop-opacity="0.86"/>
  <stop offset="1" stop-color="#11100E" stop-opacity="0.94"/>
</linearGradient></defs>
<image x="0" y="0" width="{w}" height="{h}" xlink:href="{img}"/>
<rect x="0" y="{h * 0.40:.0f}" width="{w}" height="{h * 0.60:.0f}" fill="url(#fade)"/>
<text x="{MARGIN}" y="{base - 96:.0f}" font-family="{SANS}" font-size="78" font-weight="700" \
fill="{INK}" letter-spacing="-1.5">{TITLE}</text>
<text x="{MARGIN}" y="{base - 52:.0f}" font-family="{SANS}" font-size="27" font-weight="500" \
fill="{INK}">{SUBTITLE}</text>
<text x="{MARGIN}" y="{base - 8:.0f}" font-family="{SANS}" font-size="22" font-weight="400" \
fill="{MUTED}">{BYLINE}</text>
{wordmark(mark_cell, w - MARGIN - mark_w, base - mark_h - 4)}
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
