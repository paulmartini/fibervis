"""Fiber layout and sky-projection utilities for integral field units.

The main entry point is :class:`IFULayout`, which generates a hexagonal
fiber bundle centered on the origin. Offsets are expressed in arcseconds,
matching the units used in the original notebook.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Circle


@dataclass(frozen=True)
class LayoutMetrics:
    """Derived quantities for an IFU layout."""

    n_fibers: int
    fiber_radius: float
    pitch: float
    fov_radius: float
    active_area: float
    fov_area: float
    fill_factor: float
    total_area: float
    total_area_units: str

    def stats_text(self) -> str:
        """Return a compact multi-line summary suitable for plot labels."""

        return (
            f"Total Fibers: {self.n_fibers}\n"
            f"Pitch: {self.pitch:.3g} arcsec\n"
            f"FOV Radius: {self.fov_radius:.2f} arcsec\n"
            f"Fill Factor: {self.fill_factor:.1%}\n"
            f"Total Area: {self.total_area:.1f} {self.total_area_units}"
        )


@dataclass(frozen=True)
class IFULayout:
    """Hexagonal IFU fiber layout.

    Parameters
    ----------
    n_fibers
        Number of fibers to include in the bundle.
    fiber_diameter
        Fiber active diameter in arcseconds.
    separation_ratio
        Center-to-center pitch divided by ``fiber_diameter``. A value of
        ``1.0`` means touching fibers; larger values include spacing.
    center_ra, center_dec
        Optional sky center in degrees. These are only needed when converting
        local offsets to absolute RA/Dec coordinates.
    """

    n_fibers: int
    fiber_diameter: float
    separation_ratio: float
    center_ra: Optional[float] = None
    center_dec: Optional[float] = None

    def __post_init__(self) -> None:
        if self.n_fibers <= 0:
            raise ValueError("n_fibers must be positive.")
        if self.fiber_diameter <= 0:
            raise ValueError("fiber_diameter must be positive.")
        if self.separation_ratio <= 0:
            raise ValueError("separation_ratio must be positive.")

    @property
    def fiber_radius(self) -> float:
        """Fiber radius in arcseconds."""

        return self.fiber_diameter / 2.0

    @property
    def pitch(self) -> float:
        """Center-to-center fiber spacing in arcseconds."""

        return self.fiber_diameter * self.separation_ratio

    def offsets(self) -> np.ndarray:
        """Return fiber center offsets as an ``(N, 2)`` array.

        The first column is the RA-like tangent-plane offset and the second
        column is the Dec-like offset, both in arcseconds from the IFU center.
        Fibers are ordered from the center outward.
        """

        grid_radius = int(np.ceil(np.sqrt(self.n_fibers))) + 2
        candidates = []

        for q in range(-grid_radius, grid_radius + 1):
            for r in range(-grid_radius, grid_radius + 1):
                x_offset = self.pitch * (q + r / 2.0)
                y_offset = self.pitch * (np.sqrt(3.0) / 2.0 * r)
                distance = np.hypot(x_offset, y_offset)
                candidates.append((distance, x_offset, y_offset))

        candidates.sort(key=lambda item: (item[0], item[1], item[2]))
        selected = candidates[: self.n_fibers]
        return np.array([(x_offset, y_offset) for _, x_offset, y_offset in selected])

    def distances(self) -> np.ndarray:
        """Return fiber center distances from the IFU center in arcseconds."""

        return np.hypot(*self.offsets().T)

    def sky_coordinates(
        self,
        center_ra: Optional[float] = None,
        center_dec: Optional[float] = None,
    ) -> np.ndarray:
        """Return approximate fiber centers as ``(RA, Dec)`` degrees.

        The conversion uses the standard small-angle approximation:
        ``dDec = y / 3600`` and ``dRA = x / (3600 * cos(dec))``.
        """

        ra0 = self.center_ra if center_ra is None else center_ra
        dec0 = self.center_dec if center_dec is None else center_dec
        if ra0 is None or dec0 is None:
            raise ValueError("center_ra and center_dec are required for sky coordinates.")

        cos_dec = np.cos(np.radians(dec0))
        if np.isclose(cos_dec, 0.0):
            raise ValueError("RA offsets are undefined at the celestial poles.")

        offsets = self.offsets()
        ra = ra0 + offsets[:, 0] / 3600.0 / cos_dec
        dec = dec0 + offsets[:, 1] / 3600.0
        return np.column_stack((ra, dec))

    def metrics(self) -> LayoutMetrics:
        """Compute field-of-view, area, and fill-factor metrics."""

        max_center_distance = float(np.max(self.distances()))
        fov_radius = max_center_distance + self.fiber_radius
        active_area = self.n_fibers * np.pi * self.fiber_radius**2
        fov_area = np.pi * fov_radius**2
        total_area, total_area_units = _scaled_area(active_area)

        return LayoutMetrics(
            n_fibers=self.n_fibers,
            fiber_radius=self.fiber_radius,
            pitch=self.pitch,
            fov_radius=fov_radius,
            active_area=active_area,
            fov_area=fov_area,
            fill_factor=active_area / fov_area,
            total_area=total_area,
            total_area_units=total_area_units,
        )

    def as_dict(self, include_sky: bool = False) -> Dict[str, np.ndarray]:
        """Return fiber data as numpy arrays keyed by column name."""

        offsets = self.offsets()
        data = {
            "fiber_id": np.arange(self.n_fibers),
            "x_arcsec": offsets[:, 0],
            "y_arcsec": offsets[:, 1],
            "distance_arcsec": np.hypot(offsets[:, 0], offsets[:, 1]),
        }
        if include_sky:
            sky = self.sky_coordinates()
            data["ra_deg"] = sky[:, 0]
            data["dec_deg"] = sky[:, 1]
        return data

    def write_csv(
        self,
        csv_path: str,
        include_sky: bool = True,
        extra_columns: Optional[Dict[str, Sequence[object]]] = None,
    ) -> None:
        """Write fiber coordinates to a CSV file.

        Parameters
        ----------
        csv_path
            Output CSV path.
        include_sky
            Include RA/Dec columns. Requires a layout center.
        extra_columns
            Optional additional columns. Each sequence must have
            ``n_fibers`` elements.
        """

        data = self.as_dict(include_sky=include_sky)
        if extra_columns:
            for key, values in extra_columns.items():
                if len(values) != self.n_fibers:
                    raise ValueError(f"Column {key!r} must contain {self.n_fibers} values.")
                data[key] = np.asarray(values)

        fieldnames = list(data.keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as file_obj:
            writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
            writer.writeheader()
            for row_index in range(self.n_fibers):
                writer.writerow({key: values[row_index] for key, values in data.items()})

    def plot(
        self,
        ax: Optional[Axes] = None,
        fiber_kwargs: Optional[Dict[str, object]] = None,
        fov_kwargs: Optional[Dict[str, object]] = None,
        show_stats: bool = True,
    ) -> Tuple[plt.Figure, Axes]:
        """Plot the IFU layout in local arcsecond coordinates."""

        if ax is None:
            fig, ax = plt.subplots(figsize=(9, 9))
        else:
            fig = ax.figure

        fiber_style = {
            "edgecolor": "black",
            "facecolor": "cornflowerblue",
            "alpha": 0.7,
            "linewidth": 1.0,
            "zorder": 2,
        }
        if fiber_kwargs:
            fiber_style.update(fiber_kwargs)

        for fiber_index, (x_offset, y_offset) in enumerate(self.offsets()):
            ax.add_patch(Circle((x_offset, y_offset), self.fiber_radius, **fiber_style))
            if fiber_index == 0:
                ax.text(
                    x_offset,
                    y_offset,
                    "+",
                    color="white",
                    ha="center",
                    va="center",
                    fontsize=12,
                    zorder=3,
                )

        metrics = self.metrics()
        fov_style = {
            "edgecolor": "red",
            "facecolor": "none",
            "linestyle": "--",
            "linewidth": 2.0,
            "zorder": 3,
        }
        if fov_kwargs:
            fov_style.update(fov_kwargs)
        ax.add_patch(Circle((0.0, 0.0), metrics.fov_radius, **fov_style))

        limit = metrics.fov_radius * 1.1
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_aspect("equal")
        ax.set_xlabel("Distance (arcsec)")
        ax.set_ylabel("Distance (arcsec)")
        ax.grid(True, linestyle=":", alpha=0.4)

        if show_stats:
            ax.text(
                0.05,
                0.95,
                metrics.stats_text(),
                transform=ax.transAxes,
                fontsize=12,
                verticalalignment="top",
                bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9},
            )

        fig.tight_layout()
        return fig, ax


def design_fiber_spectrograph(
    n_fibers: int,
    fiber_diameter: float,
    separation_ratio: float,
    ra_cen: Optional[float] = None,
    dec_cen: Optional[float] = None,
    write_csv: bool = False,
    csv_file: str = "ifu_coords.csv",
    plot: bool = False,
) -> IFULayout:
    """Create an :class:`IFULayout` using the notebook's original API.

    Unlike the notebook function, this returns the reusable layout object.
    Set ``plot=True`` to also display the layout, and ``write_csv=True`` to
    write the fiber coordinate table.
    """

    layout = IFULayout(
        n_fibers=n_fibers,
        fiber_diameter=fiber_diameter,
        separation_ratio=separation_ratio,
        center_ra=ra_cen,
        center_dec=dec_cen,
    )
    if write_csv:
        layout.write_csv(csv_file, include_sky=ra_cen is not None and dec_cen is not None)
    if plot:
        layout.plot()
        plt.show()
    return layout


def _scaled_area(area_arcsec2: float) -> Tuple[float, str]:
    """Scale square arcseconds to a readable angular-area unit."""

    if area_arcsec2 <= 3600.0:
        return area_arcsec2, "arcsec^2"

    area = area_arcsec2 / 3600.0
    if area <= 3600.0:
        return area, "arcmin^2"

    return area / 3600.0, "deg^2"

