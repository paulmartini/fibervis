"""
Fiber arrangement functions.

Functions
---------
hexagonal_arrangement
    Pack fibers in a close-packed hexagonal (honeycomb) lattice.
square_arrangement
    Pack fibers in a square grid.
annular_arrangement
    Place fibers in concentric rings.
custom_arrangement
    Build a bundle from user-supplied (x, y) positions.
sky_projection
    Convert a focal-plane :class:`~fibervis.fiber.FiberBundle` to on-sky
    coordinates using a telescope plate scale.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from .fiber import Fiber, FiberBundle


def hexagonal_arrangement(
    n_fibers: int,
    fiber_diameter: float,
    focal_ratio: float = 4.0,
    cladding: float = 0.0,
    *,
    center: tuple[float, float] = (0.0, 0.0),
) -> FiberBundle:
    """Create a close-packed hexagonal fiber arrangement.

    Fibers are placed row by row in a hexagonal close-packed lattice,
    filling positions from the centre outward until *n_fibers* are placed.

    Parameters
    ----------
    n_fibers : int
        Number of fibers to place.
    fiber_diameter : float
        Core diameter of each fiber (microns).
    focal_ratio : float, optional
        Focal ratio for every fiber.  Default is 4.0.
    cladding : float, optional
        Extra cladding thickness (microns) around each core that sets the
        centre-to-centre pitch.  Default is 0.0 (fibres touching).
    center : tuple of float, optional
        (x, y) coordinate of the pattern centre.  Default is (0, 0).

    Returns
    -------
    :class:`~fibervis.fiber.FiberBundle`

    Examples
    --------
    >>> bundle = hexagonal_arrangement(7, 100.0)
    >>> bundle.n_fibers
    7
    """
    if n_fibers <= 0:
        raise ValueError(f"n_fibers must be positive, got {n_fibers}")
    if fiber_diameter <= 0:
        raise ValueError(
            f"fiber_diameter must be positive, got {fiber_diameter}"
        )
    if cladding < 0:
        raise ValueError(f"cladding must be non-negative, got {cladding}")

    pitch = fiber_diameter + cladding  # centre-to-centre distance

    # Generate a large hexagonal grid and keep the closest n_fibers points.
    n_side = math.ceil(math.sqrt(n_fibers)) + 2
    candidates: list[tuple[float, float]] = []

    for row in range(-n_side, n_side + 1):
        for col in range(-n_side, n_side + 1):
            # Hexagonal grid: every other row is offset by pitch/2
            x = col * pitch + (pitch / 2.0 if row % 2 != 0 else 0.0)
            y = row * pitch * math.sqrt(3) / 2.0
            candidates.append((x, y))

    # Sort by distance from origin and keep n_fibers closest (with ties kept)
    candidates.sort(key=lambda p: p[0] ** 2 + p[1] ** 2)
    selected = candidates[:n_fibers]

    cx, cy = center
    xs = np.array([p[0] + cx for p in selected])
    ys = np.array([p[1] + cy for p in selected])

    fibers = [Fiber(fiber_diameter, focal_ratio) for _ in range(n_fibers)]
    return FiberBundle(fibers, xs, ys)


def square_arrangement(
    n_cols: int,
    n_rows: int,
    fiber_diameter: float,
    focal_ratio: float = 4.0,
    cladding: float = 0.0,
    *,
    center: tuple[float, float] = (0.0, 0.0),
) -> FiberBundle:
    """Create a square-grid fiber arrangement.

    Parameters
    ----------
    n_cols : int
        Number of columns.
    n_rows : int
        Number of rows.
    fiber_diameter : float
        Core diameter of each fiber (microns).
    focal_ratio : float, optional
        Focal ratio for every fiber.  Default is 4.0.
    cladding : float, optional
        Extra cladding thickness (microns).  Default is 0.0.
    center : tuple of float, optional
        (x, y) coordinate of the pattern centre.  Default is (0, 0).

    Returns
    -------
    :class:`~fibervis.fiber.FiberBundle`

    Examples
    --------
    >>> bundle = square_arrangement(3, 3, 100.0)
    >>> bundle.n_fibers
    9
    """
    if n_cols <= 0 or n_rows <= 0:
        raise ValueError("n_cols and n_rows must be positive integers")
    if fiber_diameter <= 0:
        raise ValueError(
            f"fiber_diameter must be positive, got {fiber_diameter}"
        )
    if cladding < 0:
        raise ValueError(f"cladding must be non-negative, got {cladding}")

    pitch = fiber_diameter + cladding
    cx, cy = center

    xs, ys = [], []
    for row in range(n_rows):
        for col in range(n_cols):
            xs.append(col * pitch - (n_cols - 1) * pitch / 2.0 + cx)
            ys.append(row * pitch - (n_rows - 1) * pitch / 2.0 + cy)

    n_fibers = n_cols * n_rows
    fibers = [Fiber(fiber_diameter, focal_ratio) for _ in range(n_fibers)]
    return FiberBundle(fibers, np.array(xs), np.array(ys))


def annular_arrangement(
    n_rings: int,
    fiber_diameter: float,
    focal_ratio: float = 4.0,
    cladding: float = 0.0,
    *,
    center_fiber: bool = True,
    center: tuple[float, float] = (0.0, 0.0),
) -> FiberBundle:
    """Create a concentric-ring (annular) fiber arrangement.

    The first ring has 6 fibers, the second 12, the k-th ring has 6k fibers,
    following the standard hexagonal close-packed shell pattern.

    Parameters
    ----------
    n_rings : int
        Number of annular rings (not counting the optional central fiber).
    fiber_diameter : float
        Core diameter of each fiber (microns).
    focal_ratio : float, optional
        Focal ratio for every fiber.  Default is 4.0.
    cladding : float, optional
        Extra cladding thickness (microns).  Default is 0.0.
    center_fiber : bool, optional
        Whether to include a single fiber at the centre.  Default is True.
    center : tuple of float, optional
        (x, y) coordinate of the pattern centre.  Default is (0, 0).

    Returns
    -------
    :class:`~fibervis.fiber.FiberBundle`

    Examples
    --------
    >>> bundle = annular_arrangement(1, 100.0)
    >>> bundle.n_fibers
    7
    """
    if n_rings < 0:
        raise ValueError(f"n_rings must be non-negative, got {n_rings}")
    if fiber_diameter <= 0:
        raise ValueError(
            f"fiber_diameter must be positive, got {fiber_diameter}"
        )

    pitch = fiber_diameter + cladding
    cx, cy = center
    xs: list[float] = []
    ys: list[float] = []

    if center_fiber:
        xs.append(cx)
        ys.append(cy)

    for ring in range(1, n_rings + 1):
        radius = ring * pitch
        n_in_ring = 6 * ring
        for i in range(n_in_ring):
            angle = 2.0 * math.pi * i / n_in_ring
            xs.append(radius * math.cos(angle) + cx)
            ys.append(radius * math.sin(angle) + cy)

    n_fibers = len(xs)
    fibers = [Fiber(fiber_diameter, focal_ratio) for _ in range(n_fibers)]
    return FiberBundle(fibers, np.array(xs, dtype=float), np.array(ys, dtype=float))


def custom_arrangement(
    x: Sequence[float],
    y: Sequence[float],
    fiber_diameter: float,
    focal_ratio: float = 4.0,
) -> FiberBundle:
    """Build a :class:`~fibervis.fiber.FiberBundle` from user-supplied positions.

    Parameters
    ----------
    x : sequence of float
        x-coordinates of fiber centres.
    y : sequence of float
        y-coordinates of fiber centres (must match length of *x*).
    fiber_diameter : float
        Core diameter of each fiber (microns).
    focal_ratio : float, optional
        Focal ratio for every fiber.  Default is 4.0.

    Returns
    -------
    :class:`~fibervis.fiber.FiberBundle`

    Examples
    --------
    >>> bundle = custom_arrangement([0, 1, 2], [0, 0, 0], 100.0)
    >>> bundle.n_fibers
    3
    """
    x = list(x)
    y = list(y)
    if len(x) != len(y):
        raise ValueError(
            f"x and y must have the same length, got {len(x)} and {len(y)}"
        )
    if fiber_diameter <= 0:
        raise ValueError(
            f"fiber_diameter must be positive, got {fiber_diameter}"
        )

    n_fibers = len(x)
    fibers = [Fiber(fiber_diameter, focal_ratio) for _ in range(n_fibers)]
    return FiberBundle(fibers, np.array(x, dtype=float), np.array(y, dtype=float))


def sky_projection(
    bundle: FiberBundle,
    plate_scale: float,
) -> FiberBundle:
    """Project a focal-plane fiber bundle to on-sky angular coordinates.

    Each fiber centre position (in microns at the focal plane) is multiplied
    by *plate_scale* to produce positions in arcseconds.  A new
    :class:`~fibervis.fiber.FiberBundle` is returned with the same fibers but
    sky-coordinate positions.

    Parameters
    ----------
    bundle : :class:`~fibervis.fiber.FiberBundle`
        Input bundle with positions in microns at the focal plane.
    plate_scale : float
        Plate scale in arcseconds per micron (must be positive).

    Returns
    -------
    :class:`~fibervis.fiber.FiberBundle`
        New bundle with positions in arcseconds.

    Examples
    --------
    >>> from fibervis import hexagonal_arrangement, sky_projection
    >>> bundle = hexagonal_arrangement(7, 100.0)
    >>> sky = sky_projection(bundle, 0.2)
    >>> round(sky.x[0], 1)
    0.0
    """
    if plate_scale <= 0:
        raise ValueError(
            f"plate_scale must be positive, got {plate_scale}"
        )

    return FiberBundle(
        list(bundle.fibers),
        bundle.x * plate_scale,
        bundle.y * plate_scale,
    )
