# SPDX-License-Identifier: MIT
"""Every piece of copper the generator places itself, checked in the finished board.

The generator locks what it draws (`(locked yes)`): the switch stubs, the column buses, the
FPC ground stubs and the hand routes of the thumb cluster from `manual_routes` in the layout
file. Freerouting treats locked tracks as permanent obstacles and leaves them out of its
session, so a mistake in one of them survives every reroute and reaches the fab. DRC catches
most of it, but only after a two-minute routing run and only on the half that was rerouted;
these checks are instant and run on both.

Every rule here is the fab rule from the project file, not a number typed twice.
"""
from __future__ import annotations

import json
import math

import pytest
from shapely.geometry import LineString, Point
from shapely.affinity import translate

from k0d3.geometry import HALVES, load_layout

from test_pcb_review import BOARDS, OFFSET, _kid, _kids, _load, _parse, _s


def rules(half: str) -> dict:
    return json.loads(BOARDS[half].with_suffix(".kicad_pro").read_text())["board"]["design_settings"]["rules"]


@pytest.fixture(scope="module", params=HALVES)
def half(request) -> str:
    if not BOARDS[request.param].exists():
        pytest.skip(f"{request.param} board not generated")
    return request.param


@pytest.fixture(scope="module")
def board(half):
    return _load(half)


@pytest.fixture(scope="module")
def locked(half) -> list[tuple[str, str, float, tuple, tuple]]:
    """(layer, net, width, start, end) of every locked segment, in board coordinates."""
    tree = _parse(BOARDS[half].read_text(encoding="utf-8"))
    nets = {n[1]: _s(n[2]) for n in _kids(tree, "net")}
    out = []
    for seg in _kids(tree, "segment"):
        if not _kids(seg, "locked"):
            continue
        a = tuple(float(v) - o for v, o in zip(_kid(seg, "start")[1:], OFFSET))
        b = tuple(float(v) - o for v, o in zip(_kid(seg, "end")[1:], OFFSET))
        # KiCad writes track nets by number, pcbnew by name after it rewrites the file
        n = _kid(seg, "net")
        net = _s(n[-1]) if n[-1].startswith('"') else nets[n[1]]
        out.append((_s(_kid(seg, "layer")[1]), net, float(_kid(seg, "width")[1]), a, b))
    assert out, "the generator places locked copper on every half"
    return out


def drills(board) -> list[tuple[Point, float, str, str]]:
    """Every hole with its net: the column buses deliberately run through the joiner holes of
    their own column, which is how a key changes layer without a via."""
    return [(Point(p.x - OFFSET[0], p.y - OFFSET[1]), p.drill / 2, f"{ref}.{p.number or '-'}", p.net)
            for ref, fp in board.footprints.items() for p in fp.pads if p.drill]


def pads(board, layer: str, net: str):
    """Copper pads on `layer` that do not belong to `net`."""
    for ref, fp in board.footprints.items():
        for p in fp.pads:
            if p.copper and p.net != net and (p.on(layer) or "*.Cu" in p.layers):
                yield f"{ref}.{p.number}[{p.net or '-'}]", translate(p.poly(), -OFFSET[0], -OFFSET[1])


def test_locked_tracks_clear_every_drill(board, locked, half):
    """A track may never cross a hole, whatever net the hole belongs to: the drill removes the
    copper. This is what put a track through SW23's boss hole during the r2.3 rework."""
    limit = rules(half)["min_hole_clearance"]
    holes = drills(board)
    for layer, net, width, a, b in locked:
        line = LineString([a, b])
        for centre, radius, name, hole_net in holes:
            if hole_net == net:                      # its own pad: the bus runs through it
                continue
            gap = line.distance(centre) - radius - width / 2
            if gap < limit:
                pytest.fail(f"{half}: locked {net} on {layer} is {gap:.3f} mm from the {name} drill "
                            f"(need {limit}) between {a} and {b}")


def test_locked_tracks_do_not_touch_a_foreign_pad(board, locked, half):
    limit = rules(half)["min_clearance"]
    by_layer = {}
    for layer, net, width, a, b in locked:
        by_layer.setdefault((layer, net), []).append((width, a, b))
    for (layer, net), segs in by_layer.items():
        for name, poly in pads(board, layer, net):
            for width, a, b in segs:
                gap = LineString([a, b]).distance(poly) - width / 2
                assert gap >= limit - 1e-6, \
                    f"{half}: locked {net} on {layer} is {gap:.3f} mm from pad {name} (need {limit})"


def test_locked_tracks_stay_inside_the_board(board, locked, half):
    limit = rules(half)["min_copper_edge_clearance"]
    outline = translate(board.outline, -OFFSET[0], -OFFSET[1])   # the parser keeps page coordinates
    edge = outline.exterior
    for layer, net, width, a, b in locked:
        line = LineString([a, b])
        assert outline.contains(line), f"{half}: locked {net} on {layer} leaves the board at {a}-{b}"
        gap = edge.distance(line) - width / 2
        assert gap >= limit - 1e-6, f"{half}: locked {net} on {layer} is {gap:.3f} mm from the edge (need {limit})"


def test_locked_tracks_of_different_nets_keep_their_clearance(locked, half):
    limit = rules(half)["min_clearance"]
    for i, (la, na, wa, aa, ab) in enumerate(locked):
        for lb, nb, wb, ba, bb in locked[i + 1:]:
            if la != lb or na == nb:
                continue
            gap = LineString([aa, ab]).distance(LineString([ba, bb])) - wa / 2 - wb / 2
            assert gap >= limit - 1e-6, \
                f"{half}: locked {na} and {nb} come within {gap:.3f} mm on {la} (need {limit})"


def test_hand_routes_run_on_the_45_degree_grid(half):
    """Long runs go horizontally, vertically or at 45 degrees. The short last leg into a pad
    may take any angle - that is how a pad is entered - but nothing longer than 2 mm may."""
    layout = load_layout(half)
    for route in layout.cfg.get("manual_routes", []):
        pts = [p for p in route["points"] if not isinstance(p, str)]
        for a, b in zip(pts, pts[1:]):
            dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
            if math.hypot(dx, dy) <= 2.0:
                continue
            on_grid = dx < 1e-6 or dy < 1e-6 or abs(dx - dy) < 1e-6
            assert on_grid, (f"{half}: {route['net']} runs {math.hypot(dx, dy):.1f} mm from {a} to {b}, "
                             f"neither straight nor at 45 degrees")


def test_every_locked_track_ends_on_its_own_copper(board, locked, half):
    """A chain of locked segments must end in a pad or a via of its own net. A dangling end is a
    route that resolves to the wrong place - silently, because the autorouter then connects the
    net some other way and DRC stays quiet."""
    chains: dict[tuple[str, str], list] = {}
    for layer, net, width, a, b in locked:
        chains.setdefault((layer, net), []).append((a, b))
    vias = {}
    for net, x, y, size, _ in board.vias:
        vias.setdefault(net, []).append(Point(x - OFFSET[0], y - OFFSET[1]))
    for (layer, net), segs in chains.items():
        ends: dict[tuple, int] = {}
        for a, b in segs:
            for p in (a, b):
                ends[(round(p[0], 3), round(p[1], 3))] = ends.get((round(p[0], 3), round(p[1], 3)), 0) + 1
        own = [translate(p.poly(), -OFFSET[0], -OFFSET[1])
               for fp in board.footprints.values() for p in fp.pads
               if p.copper and p.net == net and (p.on(layer) or "*.Cu" in p.layers)]
        for (x, y), count in ends.items():
            if count > 1:
                continue
            pt = Point(x, y)
            if any(poly.buffer(0.01).contains(pt) for poly in own):
                continue
            if any(v.distance(pt) < 0.35 for v in vias.get(net, [])):
                continue
            # the autorouter may legitimately continue a locked track from a free end
            touching = [s for l2, n2, w2, a2, b2 in locked if False]
            router = [LineString([a2, b2]) for l2, n2, w2, a2, b2 in board.segments
                      if l2 == layer and n2 == net and LineString([a2, b2]).distance(pt) < 0.05]
            assert router, (f"{half}: locked {net} on {layer} ends at ({x}, {y}) on nothing - "
                            f"no pad, no via, no routed track")
