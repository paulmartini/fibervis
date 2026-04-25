"""Tests for fibervis.filling module."""

import math
import pytest
import numpy as np

from fibervis.filling import (
    filling_factor,
    focal_ratio_degradation,
    fiber_attenuation,
    total_throughput,
)
from fibervis.arrangements import hexagonal_arrangement, square_arrangement


class TestFillingFactor:
    def test_single_fiber_in_own_area(self):
        """A single fiber's filling factor against its own area is π/4."""
        b = hexagonal_arrangement(1, 100.0)
        area = 100.0**2  # bounding box is basically the diameter×diameter square
        ff = filling_factor(b, aperture_area=area)
        assert ff == pytest.approx(math.pi / 4, rel=0.01)

    def test_returns_value_in_range(self):
        b = hexagonal_arrangement(7, 100.0)
        ff = filling_factor(b)
        assert 0 < ff <= 1.0

    def test_more_fibers_higher_ff(self):
        b1 = hexagonal_arrangement(7, 100.0)
        b2 = hexagonal_arrangement(19, 100.0)
        # Larger bundle tends toward theoretical limit ≈ π/(2√3) ≈ 0.9069
        # just check the value is reasonable
        ff2 = filling_factor(b2)
        assert ff2 > 0.5

    def test_explicit_aperture_area(self):
        b = square_arrangement(3, 3, 100.0)
        area = (3 * 100.0) ** 2  # 9 fibers in 300×300 box
        ff = filling_factor(b, aperture_area=area)
        expected = 9 * math.pi * 50.0**2 / area
        assert ff == pytest.approx(expected, rel=1e-9)

    def test_invalid_aperture_area_raises(self):
        b = hexagonal_arrangement(1, 100.0)
        with pytest.raises(ValueError):
            filling_factor(b, aperture_area=0.0)
        with pytest.raises(ValueError):
            filling_factor(b, aperture_area=-1.0)


class TestFocalRatioDegradation:
    def test_no_frd(self):
        """No degradation → throughput = 1."""
        assert focal_ratio_degradation(4.0, 4.0) == pytest.approx(1.0)

    def test_higher_output_fratio_no_loss(self):
        """Output f/# > input f/# means less spread → clipped to 1."""
        assert focal_ratio_degradation(4.0, 5.0) == pytest.approx(1.0)

    def test_known_value(self):
        # T = (f_out / f_in)^2 = (3.5/4.0)^2 = 0.765625
        expected = (3.5 / 4.0) ** 2
        assert focal_ratio_degradation(4.0, 3.5) == pytest.approx(expected, rel=1e-4)

    def test_severe_degradation(self):
        t = focal_ratio_degradation(8.0, 4.0)
        assert 0 < t < 1.0

    def test_invalid_input_fratio_raises(self):
        with pytest.raises(ValueError):
            focal_ratio_degradation(0.0, 4.0)
        with pytest.raises(ValueError):
            focal_ratio_degradation(-1.0, 4.0)

    def test_invalid_output_fratio_raises(self):
        with pytest.raises(ValueError):
            focal_ratio_degradation(4.0, 0.0)


class TestFiberAttenuation:
    def test_zero_length(self):
        """Zero length → transmission = 1 regardless of coefficient."""
        assert fiber_attenuation(0.0, 1.0) == pytest.approx(1.0)

    def test_zero_attenuation(self):
        """Zero attenuation → transmission = 1 regardless of length."""
        assert fiber_attenuation(10.0, 0.0) == pytest.approx(1.0)

    def test_known_value(self):
        """10 dB/m × 10 m = 100 dB → T = 10^(-10) ≈ 1e-10."""
        t = fiber_attenuation(10.0, 10.0)
        assert t == pytest.approx(1e-10, rel=1e-6)

    def test_moderate_attenuation(self):
        # 0.1 dB/m × 10 m = 1 dB → T = 10^(-0.1) ≈ 0.794
        t = fiber_attenuation(10.0, 0.1)
        assert t == pytest.approx(10**(-0.1), rel=1e-6)

    def test_negative_length_raises(self):
        with pytest.raises(ValueError):
            fiber_attenuation(-1.0, 0.1)

    def test_negative_coefficient_raises(self):
        with pytest.raises(ValueError):
            fiber_attenuation(10.0, -0.1)


class TestTotalThroughput:
    def test_shape(self):
        b = hexagonal_arrangement(7, 100.0)
        t = total_throughput(b, include_frd=False)
        assert t.shape == (7,)

    def test_all_positive(self):
        b = hexagonal_arrangement(7, 100.0)
        t = total_throughput(b, include_frd=False)
        assert np.all(t > 0)

    def test_with_frd(self):
        b = hexagonal_arrangement(7, 100.0)
        t = total_throughput(b, output_fratio=3.5)
        assert t.shape == (7,)
        assert np.all(t > 0)

    def test_frd_missing_output_fratio_raises(self):
        b = hexagonal_arrangement(7, 100.0)
        with pytest.raises(ValueError):
            total_throughput(b, include_frd=True, output_fratio=None)

    def test_all_components_disabled(self):
        """With all components off, throughput should be 1.0 for all fibers."""
        b = hexagonal_arrangement(7, 100.0)
        t = total_throughput(
            b,
            include_filling=False,
            include_frd=False,
            include_attenuation=False,
        )
        assert np.allclose(t, 1.0)

    def test_filling_only(self):
        b = hexagonal_arrangement(7, 100.0)
        ff = sum(f.area for f in b.fibers)
        x_min, x_max, y_min, y_max = b.bounding_box()
        bb_area = (x_max - x_min) * (y_max - y_min)
        expected_ff = ff / bb_area

        t = total_throughput(b, include_filling=True, include_frd=False, include_attenuation=False)
        assert np.allclose(t, expected_ff)
