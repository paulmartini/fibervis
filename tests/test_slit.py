"""Tests for fibervis.slit module."""

import math
import pytest
import numpy as np

from fibervis.slit import SlitHead, linear_slit, curved_slit
from fibervis.fiber import Fiber, FiberBundle


class TestSlitHead:
    def _make_slit(self, n=5):
        return linear_slit(n, 100.0)

    def test_n_fibers(self):
        s = self._make_slit(5)
        assert s.n_fibers == 5

    def test_slit_width_default(self):
        s = self._make_slit(5)
        assert s.slit_width == 100.0

    def test_slit_width_custom(self):
        bundle = linear_slit(5, 100.0).bundle
        s = SlitHead(bundle, slit_width=120.0)
        assert s.slit_width == 120.0

    def test_slit_length_positive(self):
        s = self._make_slit(5)
        assert s.slit_length > 0

    def test_slit_length_increases_with_n(self):
        s5 = linear_slit(5, 100.0)
        s10 = linear_slit(10, 100.0)
        assert s10.slit_length > s5.slit_length

    def test_dispersion_direction_linear(self):
        """Linear slit along y → fibers spread in y → dispersion direction is x."""
        s = linear_slit(5, 100.0)
        assert s.dispersion_direction() == "x"

    def test_name(self):
        s = linear_slit(5, 100.0, name="test_slit")
        assert s.name == "test_slit"

    def test_repr(self):
        s = self._make_slit(5)
        r = repr(s)
        assert "SlitHead" in r
        assert "5" in r

    def test_invalid_slit_width_raises(self):
        bundle = linear_slit(5, 100.0).bundle
        with pytest.raises(ValueError):
            SlitHead(bundle, slit_width=0.0)
        with pytest.raises(ValueError):
            SlitHead(bundle, slit_width=-10.0)


class TestLinearSlit:
    def test_n_fibers(self):
        s = linear_slit(10, 100.0)
        assert s.n_fibers == 10

    def test_returns_slit_head(self):
        s = linear_slit(5, 100.0)
        assert isinstance(s, SlitHead)

    def test_fibers_along_y(self):
        s = linear_slit(3, 100.0)
        # All x positions should be 0 (centred)
        assert np.allclose(s.bundle.x, 0.0)

    def test_symmetric_about_origin(self):
        s = linear_slit(5, 100.0)
        ys = s.bundle.y
        assert ys[len(ys) // 2] == pytest.approx(0.0, abs=1e-9)

    def test_spacing_equals_diameter_default(self):
        d = 100.0
        s = linear_slit(3, d)
        ys = s.bundle.y
        gaps = np.diff(ys)
        assert np.allclose(gaps, d)

    def test_custom_spacing(self):
        d = 100.0
        spacing = 120.0
        s = linear_slit(3, d, spacing=spacing)
        ys = s.bundle.y
        gaps = np.diff(ys)
        assert np.allclose(gaps, spacing)

    def test_custom_center(self):
        s = linear_slit(1, 100.0, center=(50.0, 100.0))
        assert s.bundle.x[0] == pytest.approx(50.0)
        assert s.bundle.y[0] == pytest.approx(100.0)

    def test_invalid_n_fibers_raises(self):
        with pytest.raises(ValueError):
            linear_slit(0, 100.0)

    def test_invalid_diameter_raises(self):
        with pytest.raises(ValueError):
            linear_slit(5, -100.0)

    def test_spacing_less_than_diameter_raises(self):
        with pytest.raises(ValueError):
            linear_slit(5, 100.0, spacing=50.0)


class TestCurvedSlit:
    def test_n_fibers(self):
        s = curved_slit(10, 100.0, radius=5000.0)
        assert s.n_fibers == 10

    def test_returns_slit_head(self):
        s = curved_slit(5, 100.0, radius=3000.0)
        assert isinstance(s, SlitHead)

    def test_radii_on_arc(self):
        """All fibre positions should be at the same distance from centre."""
        radius = 5000.0
        s = curved_slit(10, 100.0, radius=radius)
        cx, cy = s.bundle.centroid()
        # Centre of the arc is at (0, 0) by default
        bundle = s.bundle
        dists = np.sqrt(bundle.x**2 + bundle.y**2)
        assert np.allclose(dists, radius, rtol=1e-6)

    def test_custom_arc_angle(self):
        s = curved_slit(5, 100.0, radius=5000.0, arc_angle=10.0)
        assert s.n_fibers == 5

    def test_single_fiber(self):
        s = curved_slit(1, 100.0, radius=5000.0)
        assert s.n_fibers == 1

    def test_invalid_n_fibers_raises(self):
        with pytest.raises(ValueError):
            curved_slit(0, 100.0, radius=5000.0)

    def test_invalid_diameter_raises(self):
        with pytest.raises(ValueError):
            curved_slit(5, 0.0, radius=5000.0)

    def test_invalid_radius_raises(self):
        with pytest.raises(ValueError):
            curved_slit(5, 100.0, radius=0.0)

    def test_negative_arc_angle_raises(self):
        with pytest.raises(ValueError):
            curved_slit(5, 100.0, radius=5000.0, arc_angle=-5.0)
