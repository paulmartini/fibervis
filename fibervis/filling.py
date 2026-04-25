"""
Filling factor, focal-ratio degradation, and throughput calculations.

Functions
---------
filling_factor
    Fraction of the survey area covered by fiber cores.
focal_ratio_degradation
    Throughput loss due to focal-ratio degradation (FRD).
fiber_attenuation
    Transmission along a fiber of given length.
total_throughput
    Combined transmission accounting for FRD and bulk attenuation.
"""

from __future__ import annotations

import math

import numpy as np

from .fiber import Fiber, FiberBundle


def filling_factor(bundle: FiberBundle, aperture_area: float | None = None) -> float:
    """Compute the filling factor of a fiber bundle.

    The filling factor is the fraction of the *aperture area* covered by the
    fiber cores.

    Parameters
    ----------
    bundle : :class:`~fibervis.fiber.FiberBundle`
        Bundle whose positions and diameters define the fiber layout.
    aperture_area : float, optional
        Total aperture area (same units² as the fiber positions).
        If *None*, the bounding box of the bundle (including half a fiber
        diameter on each edge) is used.

    Returns
    -------
    float
        Filling factor in the range (0, 1].

    Examples
    --------
    >>> from fibervis import hexagonal_arrangement, filling_factor
    >>> bundle = hexagonal_arrangement(7, 100.0)
    >>> ff = filling_factor(bundle)
    >>> 0 < ff <= 1
    True
    """
    fiber_area_total = sum(f.area for f in bundle.fibers)

    if aperture_area is None:
        x_min, x_max, y_min, y_max = bundle.bounding_box()
        aperture_area = (x_max - x_min) * (y_max - y_min)

    if aperture_area <= 0:
        raise ValueError(
            f"aperture_area must be positive, got {aperture_area}"
        )

    return fiber_area_total / aperture_area


def focal_ratio_degradation(
    input_fratio: float,
    output_fratio: float,
) -> float:
    """Throughput loss due to focal-ratio degradation (FRD).

    FRD causes a fiber to output light at a larger cone angle than the
    input, leading to light that falls outside the collimator acceptance
    cone.  The throughput *T* is estimated as the ratio of the solid angles
    of the input and output cones (paraxial approximation):

    .. math::

        T = \\left(\\frac{f_{\\text{out}}}{f_{\\text{in}}}\\right)^{2}
            \\quad\\text{clipped to }[0,\\,1]

    Parameters
    ----------
    input_fratio : float
        Focal ratio at which the fiber is illuminated (must be positive).
    output_fratio : float
        Effective output focal ratio after FRD (must be positive).

    Returns
    -------
    float
        Throughput fraction in the range [0, 1].

    Notes
    -----
    When ``output_fratio >= input_fratio`` (no degradation), the function
    returns 1.0.

    Examples
    --------
    >>> round(focal_ratio_degradation(4.0, 3.5), 4)
    0.7656
    """
    if input_fratio <= 0:
        raise ValueError(
            f"input_fratio must be positive, got {input_fratio}"
        )
    if output_fratio <= 0:
        raise ValueError(
            f"output_fratio must be positive, got {output_fratio}"
        )

    # Solid-angle ratio: proportional to (1/f)^2
    # FRD widens the output cone (smaller output f/#).
    # Throughput = captured_solid_angle / output_solid_angle = (f_out/f_in)^2
    throughput = (output_fratio / input_fratio) ** 2
    return min(float(throughput), 1.0)


def fiber_attenuation(
    length: float,
    attenuation_coeff: float,
) -> float:
    """Transmission of a fiber as a function of length.

    Uses the standard Beer-Lambert (exponential) law expressed in decibels:

    .. math::

        T = 10^{-\\alpha L / 10}

    where :math:`\\alpha` is the attenuation coefficient in dB m⁻¹ and
    :math:`L` is the fiber length in metres.

    Parameters
    ----------
    length : float
        Fiber length in metres (must be non-negative).
    attenuation_coeff : float
        Bulk attenuation in dB m⁻¹ (must be non-negative).

    Returns
    -------
    float
        Transmission fraction in the range (0, 1].

    Examples
    --------
    >>> round(fiber_attenuation(10.0, 0.1), 6)
    0.794328
    """
    if length < 0:
        raise ValueError(f"length must be non-negative, got {length}")
    if attenuation_coeff < 0:
        raise ValueError(
            f"attenuation_coeff must be non-negative, got {attenuation_coeff}"
        )

    return float(10.0 ** (-attenuation_coeff * length / 10.0))


def total_throughput(
    bundle: FiberBundle,
    *,
    output_fratio: float | None = None,
    aperture_area: float | None = None,
    include_filling: bool = True,
    include_frd: bool = True,
    include_attenuation: bool = True,
) -> np.ndarray:
    """Compute the total throughput for each fiber in a bundle.

    The combined throughput is the product of:

    * **Filling factor** (if *include_filling* is True): fraction of the
      aperture covered by each fiber.
    * **FRD loss** (if *include_frd* is True and *output_fratio* is given).
    * **Bulk attenuation** (if *include_attenuation* is True): uses
      ``fiber.length`` and ``fiber.attenuation``.

    Parameters
    ----------
    bundle : :class:`~fibervis.fiber.FiberBundle`
        The fiber bundle to evaluate.
    output_fratio : float, optional
        Effective output focal ratio after FRD.  Required when
        *include_frd* is True; ignored otherwise.
    aperture_area : float, optional
        Total aperture area for the filling-factor calculation.  If *None*,
        the bundle bounding box is used.
    include_filling : bool, optional
        Whether to include the geometric filling factor.  Default is True.
    include_frd : bool, optional
        Whether to include FRD loss.  Default is True.
    include_attenuation : bool, optional
        Whether to include bulk fiber attenuation.  Default is True.

    Returns
    -------
    numpy.ndarray
        Array of per-fiber throughput values, shape ``(N,)``.

    Examples
    --------
    >>> from fibervis import hexagonal_arrangement, total_throughput
    >>> bundle = hexagonal_arrangement(7, 100.0)
    >>> t = total_throughput(bundle, include_frd=False)
    >>> t.shape
    (7,)
    >>> (t > 0).all()
    True
    """
    n = bundle.n_fibers
    throughputs = np.ones(n, dtype=float)

    if include_filling:
        ff = filling_factor(bundle, aperture_area=aperture_area)
        throughputs *= ff

    if include_frd:
        if output_fratio is None:
            raise ValueError(
                "output_fratio must be provided when include_frd is True"
            )
        for i, fiber in enumerate(bundle.fibers):
            throughputs[i] *= focal_ratio_degradation(
                fiber.focal_ratio, output_fratio
            )

    if include_attenuation:
        for i, fiber in enumerate(bundle.fibers):
            throughputs[i] *= fiber_attenuation(
                fiber.length, fiber.attenuation
            )

    return throughputs
