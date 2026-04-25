"""
Slit-head layout and design-drawing utilities.

A *slit head* is the assembly at the entrance of the spectrograph where
the fibers are arranged in a (pseudo-)slit.  This module provides classes
and functions to define, compute, and visualise slit-head geometries.

Classes
-------
SlitHead
    Encapsulates a complete slit-head layout.

Functions
---------
linear_slit
    Evenly spaced fibers along a straight line.
curved_slit
    Fibers placed along a circular arc.
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from .fiber import Fiber, FiberBundle


class SlitHead:
    """A fiber slit-head assembly.

    A slit head holds fibers arranged along a (possibly curved) slit.
    The positions are stored as a :class:`~fibervis.fiber.FiberBundle` whose
    coordinate system is the slit-head plane (microns, origin at centre of
    slit).

    Parameters
    ----------
    bundle : :class:`~fibervis.fiber.FiberBundle`
        Fibers and their (x, y) positions in the slit-head plane.
    slit_width : float, optional
        Physical width of the slit opening in microns.  If *None*, the
        width is taken as the diameter of the first fiber in the bundle.
    name : str, optional
        Human-readable label for the slit head.

    Attributes
    ----------
    bundle : :class:`~fibervis.fiber.FiberBundle`
    slit_width : float
    name : str
    """

    def __init__(
        self,
        bundle: FiberBundle,
        slit_width: float | None = None,
        name: str = "",
    ) -> None:
        self.bundle = bundle
        if slit_width is None:
            slit_width = bundle.fibers[0].diameter
        if slit_width <= 0:
            raise ValueError(
                f"slit_width must be positive, got {slit_width}"
            )
        self.slit_width = float(slit_width)
        self.name = str(name)

    @property
    def n_fibers(self) -> int:
        """Number of fibers in this slit head."""
        return self.bundle.n_fibers

    @property
    def slit_length(self) -> float:
        """Physical length of the slit (extent of the fibre positions plus
        one fibre diameter at each end)."""
        if self.n_fibers == 0:
            return 0.0
        diameters = self.bundle.diameters
        y_min = float(np.min(self.bundle.y) - diameters[np.argmin(self.bundle.y)] / 2.0)
        y_max = float(np.max(self.bundle.y) + diameters[np.argmax(self.bundle.y)] / 2.0)
        return y_max - y_min

    def dispersion_direction(self) -> str:
        """Return the principal dispersion direction ('x' or 'y').

        The dispersion direction is the axis with the *smaller* spread of
        fiber centre positions (i.e., fibers are aligned perpendicular to
        dispersion).
        """
        spread_x = np.ptp(self.bundle.x) if self.n_fibers > 1 else 0.0
        spread_y = np.ptp(self.bundle.y) if self.n_fibers > 1 else 0.0
        return "x" if spread_x <= spread_y else "y"

    def __repr__(self) -> str:
        return (
            f"SlitHead(n_fibers={self.n_fibers}, "
            f"slit_width={self.slit_width}, name='{self.name}')"
        )


def linear_slit(
    n_fibers: int,
    fiber_diameter: float,
    focal_ratio: float = 4.0,
    spacing: float | None = None,
    *,
    center: tuple[float, float] = (0.0, 0.0),
    name: str = "",
) -> SlitHead:
    """Create a straight (linear) slit with evenly spaced fibers.

    Fibers are placed along the y-axis.

    Parameters
    ----------
    n_fibers : int
        Number of fibers in the slit.
    fiber_diameter : float
        Core diameter of each fiber (microns).
    focal_ratio : float, optional
        Focal ratio at which each fiber exits.  Default is 4.0.
    spacing : float, optional
        Centre-to-centre spacing between adjacent fibers (microns).  If
        *None*, fibers are touching (spacing = fiber_diameter).
    center : tuple of float, optional
        (x, y) coordinate of the slit centre.  Default is (0, 0).
    name : str, optional
        Label for the slit head.

    Returns
    -------
    :class:`SlitHead`

    Examples
    --------
    >>> slit = linear_slit(10, 100.0)
    >>> slit.n_fibers
    10
    """
    if n_fibers <= 0:
        raise ValueError(f"n_fibers must be positive, got {n_fibers}")
    if fiber_diameter <= 0:
        raise ValueError(
            f"fiber_diameter must be positive, got {fiber_diameter}"
        )
    if spacing is None:
        spacing = fiber_diameter
    if spacing < fiber_diameter:
        raise ValueError(
            f"spacing ({spacing}) must be >= fiber_diameter ({fiber_diameter})"
        )

    cx, cy = center
    total_length = (n_fibers - 1) * spacing
    ys = np.linspace(-total_length / 2.0, total_length / 2.0, n_fibers) + cy
    xs = np.full(n_fibers, cx)

    fibers = [Fiber(fiber_diameter, focal_ratio) for _ in range(n_fibers)]
    bundle = FiberBundle(fibers, xs, ys)
    return SlitHead(bundle, slit_width=fiber_diameter, name=name)


def curved_slit(
    n_fibers: int,
    fiber_diameter: float,
    radius: float,
    focal_ratio: float = 4.0,
    *,
    arc_angle: float | None = None,
    center: tuple[float, float] = (0.0, 0.0),
    name: str = "",
) -> SlitHead:
    """Create a curved (circular-arc) slit with evenly spaced fibers.

    Fibers are placed along a circular arc of radius *radius*.  The arc
    subtends *arc_angle* degrees symmetrically about the top of the circle
    (12 o'clock position).

    Parameters
    ----------
    n_fibers : int
        Number of fibers.
    fiber_diameter : float
        Core diameter of each fiber (microns).
    radius : float
        Radius of curvature of the slit (microns).
    focal_ratio : float, optional
        Focal ratio at which each fiber exits.  Default is 4.0.
    arc_angle : float, optional
        Total arc angle in degrees.  If *None*, a chord spacing equal to
        *fiber_diameter* is used to determine the arc length.
    center : tuple of float, optional
        (x, y) centre of the arc.  Default is (0, 0).
    name : str, optional
        Label for the slit head.

    Returns
    -------
    :class:`SlitHead`

    Examples
    --------
    >>> slit = curved_slit(10, 100.0, radius=5000.0)
    >>> slit.n_fibers
    10
    """
    if n_fibers <= 0:
        raise ValueError(f"n_fibers must be positive, got {n_fibers}")
    if fiber_diameter <= 0:
        raise ValueError(
            f"fiber_diameter must be positive, got {fiber_diameter}"
        )
    if radius <= 0:
        raise ValueError(f"radius must be positive, got {radius}")

    if arc_angle is None:
        # Chord length = fiber_diameter → arc_angle per fiber
        half_chord = fiber_diameter / 2.0
        if half_chord > radius:
            raise ValueError(
                "fiber_diameter is larger than 2 × radius; "
                "fibers do not fit on the arc"
            )
        angle_per_fiber = 2.0 * math.degrees(math.asin(half_chord / radius))
        arc_angle = (n_fibers - 1) * angle_per_fiber if n_fibers > 1 else 0.0

    if arc_angle < 0:
        raise ValueError(f"arc_angle must be non-negative, got {arc_angle}")

    cx, cy = center
    # Place fibers symmetrically about 90° (pointing up along +y)
    start_angle = 90.0 + arc_angle / 2.0
    end_angle = 90.0 - arc_angle / 2.0

    angles_deg = np.linspace(start_angle, end_angle, n_fibers)
    angles_rad = np.deg2rad(angles_deg)

    xs = radius * np.cos(angles_rad) + cx
    ys = radius * np.sin(angles_rad) + cy

    fibers = [Fiber(fiber_diameter, focal_ratio) for _ in range(n_fibers)]
    bundle = FiberBundle(fibers, xs, ys)
    return SlitHead(bundle, slit_width=fiber_diameter, name=name)
