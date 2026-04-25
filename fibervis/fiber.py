"""
Core fiber classes.

Classes
-------
Fiber
    Represents a single optical fiber with physical and optical properties.
FiberBundle
    An ordered collection of :class:`Fiber` objects with associated
    (x, y) positions in an arbitrary coordinate system.
"""

import math

import numpy as np


class Fiber:
    """A single optical fiber used in an astronomical spectrograph.

    Parameters
    ----------
    diameter : float
        Physical diameter of the fiber core in microns.
    focal_ratio : float
        Focal ratio (f-number) at which the fiber is illuminated.
        Must be positive.
    length : float, optional
        Physical length of the fiber in metres.  Default is 1.0.
    attenuation : float, optional
        Bulk attenuation coefficient in dB m⁻¹.  Default is 0.0.
    name : str, optional
        Human-readable identifier for the fiber.

    Attributes
    ----------
    diameter : float
    focal_ratio : float
    length : float
    attenuation : float
    name : str
    """

    def __init__(
        self,
        diameter: float,
        focal_ratio: float,
        length: float = 1.0,
        attenuation: float = 0.0,
        name: str = "",
    ) -> None:
        if diameter <= 0:
            raise ValueError(f"diameter must be positive, got {diameter}")
        if focal_ratio <= 0:
            raise ValueError(f"focal_ratio must be positive, got {focal_ratio}")
        if length < 0:
            raise ValueError(f"length must be non-negative, got {length}")
        if attenuation < 0:
            raise ValueError(
                f"attenuation must be non-negative, got {attenuation}"
            )

        self.diameter = float(diameter)
        self.focal_ratio = float(focal_ratio)
        self.length = float(length)
        self.attenuation = float(attenuation)
        self.name = str(name)

    @property
    def radius(self) -> float:
        """Half the fiber diameter (microns)."""
        return self.diameter / 2.0

    @property
    def area(self) -> float:
        """Cross-sectional area of the fiber core (microns²)."""
        return math.pi * self.radius**2

    @property
    def numerical_aperture(self) -> float:
        """Numerical aperture derived from the focal ratio.

        NA = 1 / (2 * f)  (paraxial approximation).
        """
        return 1.0 / (2.0 * self.focal_ratio)

    @property
    def acceptance_angle(self) -> float:
        """Half-angle acceptance cone in degrees (paraxial)."""
        return math.degrees(math.asin(self.numerical_aperture))

    def sky_diameter(self, plate_scale: float) -> float:
        """Diameter subtended on the sky.

        Parameters
        ----------
        plate_scale : float
            Plate scale of the telescope focal plane in arcseconds per micron.

        Returns
        -------
        float
            Angular diameter in arcseconds.
        """
        if plate_scale <= 0:
            raise ValueError(
                f"plate_scale must be positive, got {plate_scale}"
            )
        return self.diameter * plate_scale

    def sky_area(self, plate_scale: float) -> float:
        """Solid angle subtended on the sky.

        Parameters
        ----------
        plate_scale : float
            Plate scale in arcseconds per micron.

        Returns
        -------
        float
            Solid angle in arcseconds².
        """
        return self.area * plate_scale**2

    def __repr__(self) -> str:
        return (
            f"Fiber(diameter={self.diameter}, focal_ratio={self.focal_ratio}, "
            f"length={self.length}, attenuation={self.attenuation}, "
            f"name='{self.name}')"
        )


class FiberBundle:
    """An ordered collection of fibers with associated positions.

    Parameters
    ----------
    fibers : list of :class:`Fiber`
        The fibers in the bundle.
    x : array-like of float
        x-coordinates of fiber centres (same units as the coordinate system
        being used, e.g. microns at the focal plane or arcseconds on sky).
    y : array-like of float
        y-coordinates of fiber centres.

    Attributes
    ----------
    fibers : list of :class:`Fiber`
    x : numpy.ndarray
    y : numpy.ndarray
    """

    def __init__(self, fibers, x, y) -> None:
        fibers = list(fibers)
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        if len(fibers) != len(x) or len(fibers) != len(y):
            raise ValueError(
                "fibers, x, and y must all have the same length; got "
                f"{len(fibers)}, {len(x)}, {len(y)}"
            )

        self.fibers = fibers
        self.x = x
        self.y = y

    def __len__(self) -> int:
        return len(self.fibers)

    def __getitem__(self, index):
        return self.fibers[index], self.x[index], self.y[index]

    def __iter__(self):
        return zip(self.fibers, self.x, self.y)

    @property
    def n_fibers(self) -> int:
        """Number of fibers in the bundle."""
        return len(self.fibers)

    @property
    def positions(self) -> np.ndarray:
        """Array of shape (N, 2) with (x, y) fiber centre positions."""
        return np.column_stack([self.x, self.y])

    @property
    def diameters(self) -> np.ndarray:
        """Array of core diameters for each fiber."""
        return np.array([f.diameter for f in self.fibers])

    def bounding_box(self):
        """Bounding box that contains all fiber centres.

        Returns
        -------
        tuple of float
            ``(x_min, x_max, y_min, y_max)``
        """
        radii = self.diameters / 2.0
        return (
            float(np.min(self.x - radii)),
            float(np.max(self.x + radii)),
            float(np.min(self.y - radii)),
            float(np.max(self.y + radii)),
        )

    def centroid(self):
        """Geometric centroid of all fiber centre positions.

        Returns
        -------
        tuple of float
            ``(x_centroid, y_centroid)``
        """
        return float(np.mean(self.x)), float(np.mean(self.y))

    def __repr__(self) -> str:
        return f"FiberBundle(n_fibers={self.n_fibers})"
