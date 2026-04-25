"""
fibervis — Tools for visualizing fiber systems for astronomical spectrographs.

Modules
-------
fiber
    Core :class:`Fiber` and :class:`FiberBundle` classes.
arrangements
    Functions to create hexagonal, square, annular, and custom fiber
    arrangements and to project them on the sky.
filling
    Calculations of filling factor, focal-ratio degradation, fiber
    attenuation, and overall throughput.
slit
    :class:`SlitHead` layout and design-drawing utilities.
plot
    High-level plotting helpers that wrap Matplotlib.
"""

from .fiber import Fiber, FiberBundle
from .arrangements import (
    hexagonal_arrangement,
    square_arrangement,
    annular_arrangement,
    custom_arrangement,
    sky_projection,
)
from .filling import (
    filling_factor,
    focal_ratio_degradation,
    fiber_attenuation,
    total_throughput,
)
from .slit import SlitHead, linear_slit, curved_slit
from .plot import (
    plot_arrangement,
    plot_slit,
    plot_throughput,
    plot_filling_factor,
)

__version__ = "0.1.0"
__author__ = "Paul Martini"

__all__ = [
    # fiber
    "Fiber",
    "FiberBundle",
    # arrangements
    "hexagonal_arrangement",
    "square_arrangement",
    "annular_arrangement",
    "custom_arrangement",
    "sky_projection",
    # filling
    "filling_factor",
    "focal_ratio_degradation",
    "fiber_attenuation",
    "total_throughput",
    # slit
    "SlitHead",
    "linear_slit",
    "curved_slit",
    # plot
    "plot_arrangement",
    "plot_slit",
    "plot_throughput",
    "plot_filling_factor",
]
