"""Tests for fibervis.fiber module."""

import math
import pytest
import numpy as np

from fibervis.fiber import Fiber, FiberBundle


# ---------------------------------------------------------------------------
# Fiber tests
# ---------------------------------------------------------------------------

class TestFiber:
    def test_basic_construction(self):
        f = Fiber(diameter=100.0, focal_ratio=4.0)
        assert f.diameter == 100.0
        assert f.focal_ratio == 4.0
        assert f.length == 1.0
        assert f.attenuation == 0.0
        assert f.name == ""

    def test_full_construction(self):
        f = Fiber(200.0, 3.0, length=15.0, attenuation=0.05, name="sky")
        assert f.length == 15.0
        assert f.attenuation == 0.05
        assert f.name == "sky"

    def test_radius(self):
        f = Fiber(100.0, 4.0)
        assert f.radius == 50.0

    def test_area(self):
        f = Fiber(100.0, 4.0)
        assert math.isclose(f.area, math.pi * 50.0**2, rel_tol=1e-10)

    def test_numerical_aperture(self):
        f = Fiber(100.0, 4.0)
        assert math.isclose(f.numerical_aperture, 1 / 8, rel_tol=1e-10)

    def test_acceptance_angle(self):
        f = Fiber(100.0, 4.0)
        na = f.numerical_aperture
        expected = math.degrees(math.asin(na))
        assert math.isclose(f.acceptance_angle, expected, rel_tol=1e-10)

    def test_sky_diameter(self):
        f = Fiber(100.0, 4.0)
        assert f.sky_diameter(0.2) == pytest.approx(20.0)

    def test_sky_area(self):
        f = Fiber(100.0, 4.0)
        assert math.isclose(
            f.sky_area(0.2), f.area * 0.04, rel_tol=1e-10
        )

    # Validation errors
    def test_negative_diameter_raises(self):
        with pytest.raises(ValueError):
            Fiber(-1.0, 4.0)

    def test_zero_diameter_raises(self):
        with pytest.raises(ValueError):
            Fiber(0.0, 4.0)

    def test_negative_focal_ratio_raises(self):
        with pytest.raises(ValueError):
            Fiber(100.0, -1.0)

    def test_negative_length_raises(self):
        with pytest.raises(ValueError):
            Fiber(100.0, 4.0, length=-1.0)

    def test_negative_attenuation_raises(self):
        with pytest.raises(ValueError):
            Fiber(100.0, 4.0, attenuation=-0.1)

    def test_invalid_plate_scale_raises(self):
        f = Fiber(100.0, 4.0)
        with pytest.raises(ValueError):
            f.sky_diameter(0.0)

    def test_repr(self):
        f = Fiber(100.0, 4.0)
        assert "Fiber" in repr(f)
        assert "100.0" in repr(f)


# ---------------------------------------------------------------------------
# FiberBundle tests
# ---------------------------------------------------------------------------

class TestFiberBundle:
    def _make_bundle(self, n=3):
        fibers = [Fiber(100.0, 4.0) for _ in range(n)]
        x = np.arange(n, dtype=float) * 110.0
        y = np.zeros(n)
        return FiberBundle(fibers, x, y)

    def test_length(self):
        b = self._make_bundle(5)
        assert len(b) == 5

    def test_n_fibers(self):
        b = self._make_bundle(7)
        assert b.n_fibers == 7

    def test_positions_shape(self):
        b = self._make_bundle(4)
        pos = b.positions
        assert pos.shape == (4, 2)

    def test_diameters(self):
        b = self._make_bundle(3)
        assert np.all(b.diameters == 100.0)

    def test_bounding_box(self):
        b = self._make_bundle(3)
        x_min, x_max, y_min, y_max = b.bounding_box()
        assert x_min < x_max
        assert y_min < y_max

    def test_centroid(self):
        b = self._make_bundle(3)
        cx, cy = b.centroid()
        assert cx == pytest.approx(110.0)  # [0, 110, 220] → mean = 110
        assert cy == pytest.approx(0.0)

    def test_mismatched_lengths_raises(self):
        fibers = [Fiber(100.0, 4.0)]
        with pytest.raises(ValueError):
            FiberBundle(fibers, [0.0, 1.0], [0.0])

    def test_iter(self):
        b = self._make_bundle(2)
        items = list(b)
        assert len(items) == 2
        fiber0, x0, y0 = items[0]
        assert isinstance(fiber0, Fiber)

    def test_getitem(self):
        b = self._make_bundle(2)
        fiber, x, y = b[0]
        assert isinstance(fiber, Fiber)
        assert x == pytest.approx(0.0)

    def test_repr(self):
        b = self._make_bundle(3)
        assert "FiberBundle" in repr(b)
        assert "3" in repr(b)
