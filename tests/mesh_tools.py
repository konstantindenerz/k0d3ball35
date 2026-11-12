# SPDX-License-Identifier: MIT
"""Mesh checks that need neither scipy nor networkx (trimesh's own split() and section() do).

Used by the print-part tests: count the loose bodies of an STL, find edges that are not shared
by exactly two faces, and cut a horizontal section as a shapely geometry.
"""
from __future__ import annotations

from collections import Counter

import numpy as np


def bodies(mesh) -> list[int]:
    """Face count of every connected body, largest first."""
    parent = list(range(len(mesh.vertices)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b, c in mesh.faces:
        ra = find(a)
        parent[find(b)] = ra
        parent[find(c)] = ra
    count = Counter(find(f[0]) for f in mesh.faces)
    return sorted(count.values(), reverse=True)


def bad_edges(mesh) -> list[tuple[tuple[float, ...], tuple[float, ...]]]:
    """Edges not shared by exactly two faces (open or non-manifold), as vertex pairs."""
    f = mesh.faces
    f = f[(f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])]
    e = np.sort(np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1)
    uniq, n = np.unique(e, axis=0, return_counts=True)
    v = mesh.vertices
    return [(tuple(v[a].round(3)), tuple(v[b].round(3))) for a, b in uniq[n != 2]]


def section(mesh, z: float):
    """The solid cross-section at height z as a shapely (Multi)Polygon (even-odd nesting)."""
    import trimesh
    from shapely.geometry import MultiLineString, Polygon
    from shapely.ops import polygonize, unary_union

    lines = trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, z])
    lines = np.round(lines[:, :, :2], 5)
    lines = [l for l in lines if not (l[0] == l[1]).all()]
    if not lines:
        return Polygon()
    faces = list(polygonize(unary_union(MultiLineString(lines))))
    filled = [Polygon(f.exterior) for f in faces]
    solid = []
    for i, f in enumerate(faces):
        p = f.representative_point()
        depth = sum(1 for j, g in enumerate(filled) if j != i and g.contains(p))
        if depth % 2 == 0:
            solid.append(f)
    return unary_union(solid)
