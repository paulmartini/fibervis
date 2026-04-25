import matplotlib
import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

matplotlib.use("Agg")

from fibervis import IFULayout
from fibervis.fits_rgb import (
    image_extent_arcsec,
    make_rgb_from_fits,
    mean_pixel_scale_arcsec,
    save_fiber_overlay_png,
)


def test_make_rgb_from_cube_fits(tmp_path) -> None:
    fits_path = tmp_path / "cube.fits"
    cube = np.stack(
        [
            np.ones((8, 8)),
            np.full((8, 8), 2.0),
            np.full((8, 8), 3.0),
        ]
    )
    fits.PrimaryHDU(cube, header=_test_wcs_header()).writeto(fits_path)

    rgb, header = make_rgb_from_fits(str(fits_path), minimum=0.0)

    assert rgb.shape == (8, 8, 3)
    assert header["CTYPE1"] == "RA---TAN"


def test_make_rgb_from_multi_extension_fits(tmp_path) -> None:
    fits_path = tmp_path / "multi_extension.fits"
    hdus = fits.HDUList(
        [
            fits.PrimaryHDU(header=_test_wcs_header()),
            fits.ImageHDU(np.ones((6, 6)), name="G"),
            fits.ImageHDU(np.full((6, 6), 2.0), name="R"),
            fits.ImageHDU(np.full((6, 6), 3.0), name="Z"),
        ]
    )
    hdus.writeto(fits_path)

    rgb, _ = make_rgb_from_fits(str(fits_path), red="Z", green="R", blue="G", minimum=0.0)

    assert rgb.shape == (6, 6, 3)


def test_image_extent_uses_wcs_pixel_scale() -> None:
    header = _test_wcs_header(pixel_scale_deg=0.001)

    assert mean_pixel_scale_arcsec(header) == pytest.approx(3.6)
    assert image_extent_arcsec(header, 125.0, 19.0, (10, 10)) == pytest.approx(
        (-14.4, 21.6, -14.4, 21.6)
    )


def test_save_fiber_overlay_png_writes_file(tmp_path) -> None:
    fits_path = tmp_path / "cube.fits"
    output_path = tmp_path / "overlay.png"
    cube = np.stack(
        [
            np.ones((16, 16)),
            np.full((16, 16), 2.0),
            np.full((16, 16), 3.0),
        ]
    )
    fits.PrimaryHDU(cube, header=_test_wcs_header(crpix=(8.0, 8.0))).writeto(fits_path)
    layout = IFULayout(7, 1.0, 1.1, center_ra=125.0, center_dec=19.0)

    fig, _ = save_fiber_overlay_png(
        str(fits_path),
        str(output_path),
        layout,
        minimum=0.0,
        show_stats=False,
        dpi=50,
    )
    fig.clf()

    assert output_path.exists()


def _test_wcs_header(
    crpix: tuple[float, float] = (5.0, 5.0),
    pixel_scale_deg: float = 1.0 / 3600.0,
) -> fits.Header:
    wcs = WCS(naxis=2)
    wcs.wcs.crpix = list(crpix)
    wcs.wcs.cdelt = np.array([-pixel_scale_deg, pixel_scale_deg])
    wcs.wcs.crval = [125.0, 19.0]
    wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    return wcs.to_header()
