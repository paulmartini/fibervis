import csv

import numpy as np
import pytest

from fibervis import IFULayout, design_fiber_spectrograph


def test_offsets_are_centered_and_ordered() -> None:
    layout = IFULayout(n_fibers=7, fiber_diameter=1.0, separation_ratio=1.1)

    offsets = layout.offsets()
    distances = layout.distances()

    assert offsets.shape == (7, 2)
    np.testing.assert_allclose(offsets[0], [0.0, 0.0])
    assert np.all(distances[:-1] <= distances[1:])
    assert np.count_nonzero(np.isclose(distances, 1.1)) == 6


def test_metrics_match_expected_areas() -> None:
    layout = IFULayout(n_fibers=7, fiber_diameter=1.0, separation_ratio=1.1)

    metrics = layout.metrics()

    assert metrics.fiber_radius == pytest.approx(0.5)
    assert metrics.pitch == pytest.approx(1.1)
    assert metrics.fov_radius == pytest.approx(1.6)
    assert metrics.active_area == pytest.approx(7 * np.pi * 0.5**2)
    assert metrics.fov_area == pytest.approx(np.pi * 1.6**2)
    assert metrics.fill_factor == pytest.approx(metrics.active_area / metrics.fov_area)


def test_sky_coordinates_use_small_angle_projection() -> None:
    layout = IFULayout(
        n_fibers=2,
        fiber_diameter=1.0,
        separation_ratio=1.0,
        center_ra=10.0,
        center_dec=30.0,
    )

    sky = layout.sky_coordinates()
    offsets = layout.offsets()

    assert sky.shape == (2, 2)
    np.testing.assert_allclose(sky[:, 0], 10.0 + offsets[:, 0] / 3600.0 / np.cos(np.radians(30.0)))
    np.testing.assert_allclose(sky[:, 1], 30.0 + offsets[:, 1] / 3600.0)


def test_write_csv_includes_requested_columns(tmp_path) -> None:
    layout = IFULayout(
        n_fibers=3,
        fiber_diameter=1.0,
        separation_ratio=1.1,
        center_ra=125.0,
        center_dec=19.0,
    )
    csv_path = tmp_path / "ifu_coords.csv"

    layout.write_csv(str(csv_path), extra_columns={"color": ["white", "white", "white"]})

    with csv_path.open(newline="", encoding="utf-8") as file_obj:
        rows = list(csv.DictReader(file_obj))

    assert len(rows) == 3
    assert {"fiber_id", "x_arcsec", "y_arcsec", "ra_deg", "dec_deg", "color"}.issubset(rows[0])


def test_compatibility_function_returns_layout() -> None:
    layout = design_fiber_spectrograph(5, 1.0, 1.1)

    assert isinstance(layout, IFULayout)
    assert layout.offsets().shape == (5, 2)
