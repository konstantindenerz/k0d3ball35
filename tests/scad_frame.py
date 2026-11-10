# SPDX-License-Identifier: MIT
"""Back from the print frame of the exported files to the layout frame of the SCAD sources.

hardware/case/case.scad and hardware/trackball-cradle/cradle.scad model in the layout frame
(x outward, y towards the user, z up). That frame is left-handed, so the export flips y once and
the STL and DXF files are the real parts in the print frame (x outward, y away from the user,
z up; issues/mech-case-stl-mirrored.md). The tests compare the geometry with layout data, so they
undo that flip here, in one place. tests/test_case_handedness.py checks the files in the print
frame itself.
"""
from __future__ import annotations

import numpy as np

FLIP_Y = np.diag([1.0, -1.0, 1.0, 1.0])


def load_layout_frame(path):
    """An exported STL as a trimesh mesh in the layout frame. trimesh reverses the faces for the
    negative determinant, so normals, volume and watertightness stay what they were."""
    import trimesh

    mesh = trimesh.load(path, force="mesh")
    mesh.apply_transform(FLIP_Y)
    return mesh


def layout_y(y: float) -> float:
    """A y read from an exported DXF, in the layout frame."""
    return -y
