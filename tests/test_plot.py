"""Tests for fibervis.plot module."""

import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fibervis.plot import (
    plot_arrangement,
    plot_slit,
    plot_throughput,
    plot_filling_factor,
)
from fibervis.arrangements import hexagonal_arrangement, square_arrangement
from fibervis.slit import linear_slit, curved_slit


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


class TestPlotArrangement:
    def test_returns_fig_ax(self):
        b = hexagonal_arrangement(7, 100.0)
        fig, ax = plot_arrangement(b)
        assert fig is not None
        assert ax is not None

    def test_accepts_existing_ax(self):
        b = hexagonal_arrangement(7, 100.0)
        _, existing_ax = plt.subplots()
        fig, ax = plot_arrangement(b, ax=existing_ax)
        assert ax is existing_ax

    def test_show_index(self):
        b = hexagonal_arrangement(7, 100.0)
        fig, ax = plot_arrangement(b, show_index=True)
        # There should be text annotations
        assert len(ax.texts) == 7

    def test_number_of_patches(self):
        b = hexagonal_arrangement(7, 100.0)
        fig, ax = plot_arrangement(b)
        # Each fiber is one Circle patch
        assert len(ax.patches) == 7


class TestPlotSlit:
    def test_returns_fig_ax(self):
        s = linear_slit(10, 100.0)
        fig, ax = plot_slit(s)
        assert fig is not None
        assert ax is not None

    def test_accepts_existing_ax(self):
        s = linear_slit(5, 100.0)
        _, existing_ax = plt.subplots()
        fig, ax = plot_slit(s, ax=existing_ax)
        assert ax is existing_ax

    def test_patch_count(self):
        n = 5
        s = linear_slit(n, 100.0)
        fig, ax = plot_slit(s)
        # 1 background rectangle + n fiber circles
        assert len(ax.patches) == n + 1

    def test_curved_slit(self):
        s = curved_slit(8, 100.0, radius=5000.0)
        fig, ax = plot_slit(s)
        assert len(ax.patches) == 8 + 1


class TestPlotThroughput:
    def test_returns_fig_ax(self):
        fig, ax = plot_throughput([1, 2, 3], [0.8, 0.85, 0.9])
        assert fig is not None
        assert ax is not None

    def test_line_plotted(self):
        fig, ax = plot_throughput([1, 2, 3], [0.8, 0.85, 0.9])
        assert len(ax.lines) == 1

    def test_with_label(self):
        fig, ax = plot_throughput([1, 2, 3], [0.8, 0.85, 0.9], label="test")
        assert ax.get_legend() is not None


class TestPlotFillingFactor:
    def test_returns_fig_ax(self):
        bundles = {
            "hex": hexagonal_arrangement(7, 100.0),
            "square": square_arrangement(3, 3, 100.0),
        }
        fig, ax = plot_filling_factor(bundles)
        assert fig is not None
        assert ax is not None

    def test_bar_count(self):
        bundles = {
            "hex": hexagonal_arrangement(7, 100.0),
            "square": square_arrangement(3, 3, 100.0),
        }
        fig, ax = plot_filling_factor(bundles)
        assert len(ax.patches) == 2

    def test_custom_aperture_areas(self):
        bundles = {"hex": hexagonal_arrangement(7, 100.0)}
        areas = {"hex": 50000.0}
        fig, ax = plot_filling_factor(bundles, aperture_areas=areas)
        assert fig is not None
