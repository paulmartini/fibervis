"""Tests for fibervis.arrangements module."""

import math
import pytest
import numpy as np

from fibervis.arrangements import (
    hexagonal_arrangement,
    square_arrangement,
    annular_arrangement,
    custom_arrangement,
    sky_projection,
)
from fibervis.fiber import FiberBundle


class TestHexagonalArrangement:
    def test_returns_fiber_bundle(self):
        b = hexagonal_arrangement(7, 100.0)
        assert isinstance(b, FiberBundle)

    def test_n_fibers(self):
        for n in [1, 7, 19]:
            b = hexagonal_arrangement(n, 100.0)
            assert b.n_fibers == n

    def test_center_at_origin(self):
        b = hexagonal_arrangement(1, 100.0)
        assert b.x[0] == pytest.approx(0.0)
        assert b.y[0] == pytest.approx(0.0)

    def test_custom_center(self):
        b = hexagonal_arrangement(1, 100.0, center=(50.0, 80.0))
        assert b.x[0] == pytest.approx(50.0)
        assert b.y[0] == pytest.approx(80.0)

    def test_diameter_set(self):
        b = hexagonal_arrangement(7, 150.0)
        for f in b.fibers:
            assert f.diameter == 150.0

    def test_pitch_with_cladding(self):
        d = 100.0
        clad = 10.0
        b = hexagonal_arrangement(7, d, cladding=clad)
        # All inter-neighbour distances should be ≥ pitch
        pitch = d + clad
        xs, ys = b.x, b.y
        min_dist = float("inf")
        for i in range(len(xs)):
            for j in range(i + 1, len(xs)):
                dist = math.hypot(xs[i] - xs[j], ys[i] - ys[j])
                if dist < min_dist:
                    min_dist = dist
        assert min_dist == pytest.approx(pitch, rel=0.01)

    def test_invalid_n_fibers_raises(self):
        with pytest.raises(ValueError):
            hexagonal_arrangement(0, 100.0)

    def test_invalid_diameter_raises(self):
        with pytest.raises(ValueError):
            hexagonal_arrangement(7, -10.0)

    def test_invalid_cladding_raises(self):
        with pytest.raises(ValueError):
            hexagonal_arrangement(7, 100.0, cladding=-1.0)


class TestSquareArrangement:
    def test_n_fibers(self):
        b = square_arrangement(3, 3, 100.0)
        assert b.n_fibers == 9

    def test_returns_fiber_bundle(self):
        b = square_arrangement(2, 2, 100.0)
        assert isinstance(b, FiberBundle)

    def test_pitch(self):
        d = 100.0
        b = square_arrangement(2, 2, d)
        # All adjacent fibers should be exactly d apart
        assert abs(b.x[1] - b.x[0]) == pytest.approx(d)

    def test_center_symmetry(self):
        b = square_arrangement(3, 3, 100.0)
        cx, cy = b.centroid()
        assert cx == pytest.approx(0.0, abs=1e-9)
        assert cy == pytest.approx(0.0, abs=1e-9)

    def test_custom_center(self):
        b = square_arrangement(1, 1, 100.0, center=(10.0, 20.0))
        assert b.x[0] == pytest.approx(10.0)
        assert b.y[0] == pytest.approx(20.0)

    def test_invalid_cols_raises(self):
        with pytest.raises(ValueError):
            square_arrangement(0, 3, 100.0)

    def test_invalid_diameter_raises(self):
        with pytest.raises(ValueError):
            square_arrangement(3, 3, 0.0)


class TestAnnularArrangement:
    def test_center_only(self):
        b = annular_arrangement(0, 100.0, center_fiber=True)
        assert b.n_fibers == 1

    def test_one_ring_with_center(self):
        b = annular_arrangement(1, 100.0)
        assert b.n_fibers == 7  # 1 + 6

    def test_two_rings_with_center(self):
        b = annular_arrangement(2, 100.0)
        assert b.n_fibers == 19  # 1 + 6 + 12

    def test_no_center_fiber(self):
        b = annular_arrangement(1, 100.0, center_fiber=False)
        assert b.n_fibers == 6

    def test_ring_radii(self):
        d = 100.0
        b = annular_arrangement(2, d)
        # Second ring positions should be at radius ≈ 2*d from centre
        x, y = b.x, b.y
        distances = np.sqrt(x**2 + y**2)
        ring2_mask = distances > 1.5 * d
        ring2_radii = distances[ring2_mask]
        assert np.allclose(ring2_radii, 2.0 * d, rtol=0.01)

    def test_invalid_n_rings_raises(self):
        with pytest.raises(ValueError):
            annular_arrangement(-1, 100.0)

    def test_invalid_diameter_raises(self):
        with pytest.raises(ValueError):
            annular_arrangement(1, 0.0)


class TestCustomArrangement:
    def test_basic(self):
        b = custom_arrangement([0, 1, 2], [0, 0, 0], 100.0)
        assert b.n_fibers == 3

    def test_positions(self):
        b = custom_arrangement([5.0], [7.0], 100.0)
        assert b.x[0] == pytest.approx(5.0)
        assert b.y[0] == pytest.approx(7.0)

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            custom_arrangement([0, 1], [0], 100.0)

    def test_invalid_diameter_raises(self):
        with pytest.raises(ValueError):
            custom_arrangement([0], [0], 0.0)


class TestSkyProjection:
    def test_scales_positions(self):
        b = hexagonal_arrangement(7, 100.0)
        plate_scale = 0.2  # arcsec/micron
        sky = sky_projection(b, plate_scale)
        assert np.allclose(sky.x, b.x * plate_scale)
        assert np.allclose(sky.y, b.y * plate_scale)

    def test_same_n_fibers(self):
        b = hexagonal_arrangement(7, 100.0)
        sky = sky_projection(b, 0.2)
        assert sky.n_fibers == b.n_fibers

    def test_invalid_plate_scale_raises(self):
        b = hexagonal_arrangement(7, 100.0)
        with pytest.raises(ValueError):
            sky_projection(b, 0.0)
        with pytest.raises(ValueError):
            sky_projection(b, -0.1)
