"""
High-level Matplotlib plotting helpers.

Functions
---------
plot_arrangement
    Draw fiber circles for a sky-projection or focal-plane arrangement.
plot_slit
    Draw a design view of a slit head.
plot_throughput
    Plot throughput as a function of wavelength or fiber length.
plot_filling_factor
    Bar chart or annotation of the filling factor.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .fiber import FiberBundle
from .slit import SlitHead
from .filling import filling_factor

# Use a non-interactive backend by default so the module can be imported
# in headless environments.
matplotlib.use("Agg")


def plot_arrangement(
    bundle: FiberBundle,
    ax: Axes | None = None,
    *,
    facecolor: str = "steelblue",
    edgecolor: str = "black",
    alpha: float = 0.6,
    show_index: bool = False,
    xlabel: str = "x",
    ylabel: str = "y",
    title: str = "Fiber arrangement",
    scale_label: str = "",
) -> tuple[Figure, Axes]:
    """Draw the fiber positions as circles.

    Parameters
    ----------
    bundle : :class:`~fibervis.fiber.FiberBundle`
        Bundle to visualise.
    ax : :class:`matplotlib.axes.Axes`, optional
        Existing axes to draw on.  If *None*, a new figure is created.
    facecolor : str, optional
        Fill colour for the fiber circles.  Default is ``'steelblue'``.
    edgecolor : str, optional
        Edge colour.  Default is ``'black'``.
    alpha : float, optional
        Transparency of the circles.  Default is 0.6.
    show_index : bool, optional
        If True, annotate each fiber with its index.  Default is False.
    xlabel : str, optional
        Label for the x-axis.  Default is ``'x'``.
    ylabel : str, optional
        Label for the y-axis.  Default is ``'y'``.
    title : str, optional
        Axes title.
    scale_label : str, optional
        If provided, a scale bar label is added to the bottom of the axes.

    Returns
    -------
    fig, ax : tuple[:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`]
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    else:
        fig = ax.get_figure()

    for i, (fiber, x, y) in enumerate(bundle):
        circle = mpatches.Circle(
            (x, y),
            radius=fiber.radius,
            facecolor=facecolor,
            edgecolor=edgecolor,
            alpha=alpha,
        )
        ax.add_patch(circle)
        if show_index:
            ax.text(
                x, y, str(i), ha="center", va="center", fontsize=6
            )

    ax.set_aspect("equal")
    ax.autoscale_view()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    if scale_label:
        ax.annotate(
            scale_label,
            xy=(0.5, 0.02),
            xycoords="axes fraction",
            ha="center",
            fontsize=9,
        )

    return fig, ax


def plot_slit(
    slit: SlitHead,
    ax: Axes | None = None,
    *,
    fiber_color: str = "steelblue",
    slit_color: str = "gold",
    slit_alpha: float = 0.25,
    alpha: float = 0.7,
    show_index: bool = False,
    title: str | None = None,
) -> tuple[Figure, Axes]:
    """Draw a design view of a slit head.

    The slit aperture is shown as a semi-transparent rectangle spanning the
    full slit length and *slit_width*.  The fiber cores are overlaid as
    circles.

    Parameters
    ----------
    slit : :class:`~fibervis.slit.SlitHead`
        The slit head to visualise.
    ax : :class:`matplotlib.axes.Axes`, optional
        Existing axes.  If *None*, a new figure is created.
    fiber_color : str, optional
        Fill colour for the fiber circles.
    slit_color : str, optional
        Fill colour for the slit aperture rectangle.
    slit_alpha : float, optional
        Transparency of the slit aperture.
    alpha : float, optional
        Transparency of the fiber circles.
    show_index : bool, optional
        Annotate each fiber with its integer index.
    title : str, optional
        Axes title.  Defaults to the slit head's ``name`` attribute.

    Returns
    -------
    fig, ax : tuple[:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`]
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(4, 8))
    else:
        fig = ax.get_figure()

    bundle = slit.bundle
    half_width = slit.slit_width / 2.0

    # Determine the y-extent of the slit from the actual fiber positions.
    _, _, y_min_bb, y_max_bb = bundle.bounding_box()
    slit_draw_length = y_max_bb - y_min_bb

    # Draw slit aperture background
    rect = mpatches.Rectangle(
        (-half_width, y_min_bb),
        slit.slit_width,
        slit_draw_length,
        facecolor=slit_color,
        edgecolor="goldenrod",
        alpha=slit_alpha,
        zorder=0,
    )
    ax.add_patch(rect)

    # Draw fibers
    for i, (fiber, x, y) in enumerate(bundle):
        circle = mpatches.Circle(
            (x, y),
            radius=fiber.radius,
            facecolor=fiber_color,
            edgecolor="black",
            linewidth=0.5,
            alpha=alpha,
            zorder=1,
        )
        ax.add_patch(circle)
        if show_index:
            ax.text(x, y, str(i), ha="center", va="center", fontsize=5, zorder=2)

    ax.set_aspect("equal")
    ax.autoscale_view()
    ax.set_xlabel("x (µm)")
    ax.set_ylabel("y (µm)")
    ax.set_title(title if title is not None else slit.name or "Slit head")

    return fig, ax


def plot_throughput(
    x: Sequence[float],
    throughputs: Sequence[float],
    ax: Axes | None = None,
    *,
    xlabel: str = "Value",
    ylabel: str = "Throughput",
    title: str = "Fiber throughput",
    label: str | None = None,
    color: str = "steelblue",
) -> tuple[Figure, Axes]:
    """Plot throughput as a function of an independent variable.

    Parameters
    ----------
    x : sequence of float
        Independent variable values (e.g., wavelengths in nm or fiber
        lengths in m).
    throughputs : sequence of float
        Corresponding throughput values (0–1).
    ax : :class:`matplotlib.axes.Axes`, optional
        Existing axes.
    xlabel, ylabel, title : str
        Axis labels and title.
    label : str, optional
        Legend label for the plotted line.
    color : str, optional
        Line colour.

    Returns
    -------
    fig, ax : tuple
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))
    else:
        fig = ax.get_figure()

    ax.plot(x, throughputs, color=color, label=label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_ylim(0, 1.05)
    if label is not None:
        ax.legend()

    return fig, ax


def plot_filling_factor(
    bundles: dict[str, FiberBundle],
    ax: Axes | None = None,
    *,
    aperture_areas: dict[str, float] | None = None,
    color: str = "steelblue",
    title: str = "Filling factor by arrangement",
) -> tuple[Figure, Axes]:
    """Bar chart of filling factors for one or more bundles.

    Parameters
    ----------
    bundles : dict mapping str to :class:`~fibervis.fiber.FiberBundle`
        A mapping of arrangement name → bundle.
    ax : :class:`matplotlib.axes.Axes`, optional
        Existing axes.
    aperture_areas : dict mapping str to float, optional
        Aperture area to use for each bundle name.  If *None*, the bounding
        box area is used for every bundle.
    color : str, optional
        Bar colour.
    title : str, optional
        Axes title.

    Returns
    -------
    fig, ax : tuple
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))
    else:
        fig = ax.get_figure()

    names = list(bundles.keys())
    ffs = []
    for name, bundle in bundles.items():
        area = None if aperture_areas is None else aperture_areas.get(name)
        ffs.append(filling_factor(bundle, aperture_area=area))

    bars = ax.bar(names, ffs, color=color, edgecolor="black")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Filling factor")
    ax.set_title(title)

    for bar, ff in zip(bars, ffs):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 0.01,
            f"{ff:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    return fig, ax
