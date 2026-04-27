"""Lenslet geometry helpers and plotting utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, RegularPolygon


def hexagon_circumradius(pitch: float) -> float:
    """Return circumradius of touching regular hexagons for a given pitch."""

    if pitch <= 0:
        raise ValueError("pitch must be positive.")
    return pitch / np.sqrt(3.0)


def draw_lenslet_triplet(
    pitch: float,
    output_path: str,
    dpi: int = 200,
    show: bool = False,
) -> Tuple[plt.Figure, plt.Axes]:
    """Create and save the lenslet triplet schematic."""

    centers = _lenslet_centers(pitch)
    hex_radius = hexagon_circumradius(pitch)
    circle_radius = 0.5 * pitch

    fig, ax = plt.subplots(figsize=(8, 7))

    for x_coord, y_coord in centers:
        hexagon = RegularPolygon(
            (x_coord, y_coord),
            numVertices=6,
            radius=hex_radius,
            orientation=0.0,
            facecolor="none",
            edgecolor="black",
            linewidth=2.0,
        )
        circle = Circle(
            (x_coord, y_coord),
            radius=circle_radius,
            facecolor="none",
            edgecolor="tab:blue",
            linewidth=1.8,
        )
        ax.add_patch(hexagon)
        ax.add_patch(circle)

    top_left, top_right = centers[0], centers[1]
    arrow_y = hex_radius * 1.25
    ax.annotate(
        "",
        xy=(top_left[0], arrow_y),
        xytext=(top_right[0], arrow_y),
        arrowprops={"arrowstyle": "<->", "lw": 1.8, "color": "tab:red"},
    )
    ax.text(
        0.0,
        arrow_y + 0.08 * pitch,
        f"{pitch:g} microns center-to-center",
        ha="center",
        va="bottom",
        color="tab:red",
        fontsize=12,
    )

    margin = 0.9 * pitch
    x_min = float(np.min(centers[:, 0]) - hex_radius - margin / 2.0)
    x_max = float(np.max(centers[:, 0]) + hex_radius + margin / 2.0)
    y_min = float(np.min(centers[:, 1]) - hex_radius - margin / 2.5)
    y_max = float(np.max(centers[:, 1]) + hex_radius + margin / 1.8)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.tight_layout()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=dpi, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig, ax


def _lenslet_centers(pitch: float) -> np.ndarray:
    """Return centers for two top lenslets and one centered below."""

    if pitch <= 0:
        raise ValueError("pitch must be positive.")

    half_sep = 0.5 * pitch
    vertical_drop = np.sqrt(3.0) * half_sep
    return np.array(
        [
            (-half_sep, 0.0),
            (half_sep, 0.0),
            (0.0, -vertical_drop),
        ]
    )
