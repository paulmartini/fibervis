"""Create RGB FITS images and overlay IFU fiber geometry."""

from __future__ import annotations

from typing import Dict, Optional, Sequence, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.visualization import make_lupton_rgb
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
from matplotlib.axes import Axes
from matplotlib.patches import Circle

from .fiber_layout import IFULayout

BandSpec = Union[int, str]


def make_rgb_from_fits(
    fits_path: str,
    red: BandSpec = 2,
    green: BandSpec = 1,
    blue: BandSpec = 0,
    scales: Tuple[float, float, float] = (1.0, 1.5, 2.5),
    minimum: Union[str, Sequence[float], float] = "median",
    q: float = 10.0,
    stretch: float = 0.2,
    image_hdu: BandSpec = 0,
) -> Tuple[np.ndarray, fits.Header]:
    """Read a FITS file and return a Lupton RGB image plus WCS header.

    The function supports both a three-dimensional image cube in
    ``image_hdu`` and true multi-extension FITS files where ``red``,
    ``green``, and ``blue`` identify separate HDUs by index or name.

    Parameters
    ----------
    fits_path
        Input FITS file.
    red, green, blue
        Cube plane indices or HDU identifiers for RGB channels.
    scales
        Multiplicative scale factors for red, green, and blue channels.
    minimum
        ``"median"`` to subtract each channel median, a scalar, or a
        three-element sequence passed to ``make_lupton_rgb``.
    q, stretch
        Lupton RGB contrast parameters.
    image_hdu
        HDU containing the image cube or the WCS header.
    """

    with fits.open(fits_path) as hdul:
        header = hdul[image_hdu].header.copy()
        red_data = _read_channel(hdul, red, image_hdu=image_hdu)
        green_data = _read_channel(hdul, green, image_hdu=image_hdu)
        blue_data = _read_channel(hdul, blue, image_hdu=image_hdu)

    channels = (
        np.asarray(red_data, dtype=float) * scales[0],
        np.asarray(green_data, dtype=float) * scales[1],
        np.asarray(blue_data, dtype=float) * scales[2],
    )
    channel_minimum = _channel_minimum(channels, minimum)
    rgb = make_lupton_rgb(
        channels[0],
        channels[1],
        channels[2],
        minimum=channel_minimum,
        Q=q,
        stretch=stretch,
    )
    return rgb, header


def save_rgb_png(
    fits_path: str,
    output_path: str,
    **rgb_kwargs: object,
) -> np.ndarray:
    """Create a FITS RGB image and save it as a PNG.

    Additional keyword arguments are passed to :func:`make_rgb_from_fits`.
    The RGB array is returned for reuse or testing.
    """

    rgb, _ = make_rgb_from_fits(fits_path, **rgb_kwargs)
    plt.imsave(output_path, rgb)
    return rgb


def save_fiber_overlay_png(
    fits_path: str,
    output_path: str,
    layout: IFULayout,
    center_ra: Optional[float] = None,
    center_dec: Optional[float] = None,
    zoom_factor: float = 2.25,
    figsize: Tuple[float, float] = (8.0, 8.0),
    fiber_kwargs: Optional[Dict[str, object]] = None,
    show_stats: bool = True,
    title: Optional[str] = None,
    dpi: int = 150,
    **rgb_kwargs: object,
) -> Tuple[plt.Figure, Axes]:
    """Create a FITS RGB PNG with an IFU layout overlaid.

    The image is plotted in arcseconds relative to ``center_ra`` and
    ``center_dec``. If either center is omitted, the values stored on
    ``layout`` are used.
    """

    rgb, header = make_rgb_from_fits(fits_path, **rgb_kwargs)
    center = _resolve_center(layout, center_ra, center_dec)
    extent = image_extent_arcsec(header, center[0], center[1], rgb.shape[:2])

    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(rgb, origin="lower", extent=extent)
    overlay_fibers(ax, layout, fiber_kwargs=fiber_kwargs)

    metrics = layout.metrics()
    limit = metrics.fov_radius * zoom_factor
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_xlabel(r"$\Delta$ RA (arcsec)")
    ax.set_ylabel(r"$\Delta$ Dec (arcsec)")
    ax.tick_params(axis="both", labelsize=12)

    if title is None:
        title = f"IFU Overlay ({layout.n_fibers} fibers)"
    ax.set_title(title)

    if show_stats:
        ax.text(
            0.05,
            0.95,
            metrics.stats_text(),
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.5},
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    return fig, ax


def overlay_fibers(
    ax: Axes,
    layout: IFULayout,
    fiber_kwargs: Optional[Dict[str, object]] = None,
    mark_center: bool = True,
) -> Axes:
    """Overlay IFU fibers on an axis in local arcsecond coordinates."""

    style = {
        "edgecolor": "white",
        "facecolor": "none",
        "alpha": 0.3,
        "linewidth": 0.75,
    }
    if fiber_kwargs:
        style.update(fiber_kwargs)

    for fiber_index, (x_offset, y_offset) in enumerate(layout.offsets()):
        ax.add_patch(Circle((x_offset, y_offset), layout.fiber_radius, **style))
        if mark_center and fiber_index == 0:
            ax.plot(
                x_offset,
                y_offset,
                marker="+",
                color=style.get("edgecolor", "white"),
                markersize=8,
                alpha=0.8,
            )
    return ax


def image_extent_arcsec(
    header: fits.Header,
    center_ra: float,
    center_dec: float,
    image_shape: Tuple[int, int],
) -> Tuple[float, float, float, float]:
    """Return matplotlib image extent in arcseconds from a sky center."""

    wcs = WCS(header).celestial
    center_x, center_y = wcs.world_to_pixel_values(center_ra, center_dec)
    pixel_scale = mean_pixel_scale_arcsec(header)
    image_height, image_width = image_shape

    return (
        (0.0 - center_x) * pixel_scale,
        (image_width - center_x) * pixel_scale,
        (0.0 - center_y) * pixel_scale,
        (image_height - center_y) * pixel_scale,
    )


def mean_pixel_scale_arcsec(header: fits.Header) -> float:
    """Return the mean celestial pixel scale in arcseconds per pixel."""

    wcs = WCS(header).celestial
    pixel_scales_deg = np.abs(proj_plane_pixel_scales(wcs))
    return float(np.mean(pixel_scales_deg) * 3600.0)


def _read_channel(
    hdul: fits.HDUList,
    band: BandSpec,
    image_hdu: BandSpec = 0,
) -> np.ndarray:
    """Read one channel from a cube HDU or from a separate image HDU."""

    image_data = hdul[image_hdu].data
    if image_data is not None and np.ndim(image_data) == 3 and isinstance(band, int):
        return np.asarray(image_data[band, :, :], dtype=float)

    channel_data = hdul[band].data
    if channel_data is None:
        raise ValueError(f"HDU {band!r} does not contain image data.")
    if np.ndim(channel_data) != 2:
        raise ValueError(f"HDU {band!r} must contain a 2-D image.")
    return np.asarray(channel_data, dtype=float)


def _channel_minimum(
    channels: Tuple[np.ndarray, np.ndarray, np.ndarray],
    minimum: Union[str, Sequence[float], float],
) -> Union[Sequence[float], float]:
    """Normalize the supported minimum options for Lupton RGB rendering."""

    if isinstance(minimum, str) and minimum == "median":
        return [float(np.nanmedian(channel)) for channel in channels]
    return minimum


def _resolve_center(
    layout: IFULayout,
    center_ra: Optional[float],
    center_dec: Optional[float],
) -> Tuple[float, float]:
    """Resolve an overlay center from explicit values or the layout."""

    ra = layout.center_ra if center_ra is None else center_ra
    dec = layout.center_dec if center_dec is None else center_dec
    if ra is None or dec is None:
        raise ValueError("center_ra and center_dec are required for FITS overlays.")
    return ra, dec

def sdss_rgb(imgs, bands, scales=None,
             m=0.02, Q=20):
    '''
      *imgs*:   list of 2-d numpy arrays of image pixels (float)
      *bands*:  list of strings with the band names, eg ['g', 'r',' 'z']
      *scales*: dict from band name to (plane, scale), where *plane* is the RGB plane,
                and *scale* multiplies the image pixels
      *m*:      float, an offset added so that pixels containing 0.0 map to a gray value
                rather than black.
      *Q*:      arcsinh scaling value (larger = stronger stretch)

      Returns: H x W x 3 RGB array, floating-point, between 0.0 and 1.0.

      This is from https://github.com/legacysurvey/imagine/blob/17056890452a5769869d779a55b1487877532e5d/map/views.py#L5993
    '''
    
    import numpy as np
    rgbscales = {'u': (2,1.5), #1.0,
                 'g': (2,2.5),
                 'r': (1,1.5),
                 'i': (0,1.0),
                 'z': (0,0.4), #0.3
                 }
    if scales is not None:
        rgbscales.update(scales)

    I = 0
    for img,band in zip(imgs, bands):
        plane,scale = rgbscales[band]
        img = np.maximum(0, img * scale + m)
        I = I + img
    I /= len(bands)

    Q = 20
    fI = np.arcsinh(Q * I) / np.sqrt(Q)
    I += (I == 0.) * 1e-6
    H,W = I.shape
    rgb = np.zeros((H,W,3), np.float32)
    for img,band in zip(imgs, bands):
        plane,scale = rgbscales[band]
        rgb[:,:,plane] = (img * scale + m) * fI / I

    # We saturate to white, while the original SDSS (Lupton et al) color mapping
    # saturates to the color of the object... more scientifically informative, but
    # some say, not as pretty.
    # Can do the SDSS version with something along these lines:
    # # maxrgb = reduce(np.maximum, [R,G,B])
    # # J = (maxrgb > 1.)
    # # R[J] = R[J]/maxrgb[J]
    # # G[J] = G[J]/maxrgb[J]
    # # B[J] = B[J]/maxrgb[J]
    # rgb = np.dstack((R,G,B))
        
    rgb = np.clip(rgb, 0, 1)
    return rgb

def dr2_rgb(rimgs, bands, **ignored):
    ''' also from legacysurvey code in views.py '''
    return sdss_rgb(rimgs, bands, scales=dict(g=(2,6.0), r=(1,3.4), z=(0,2.2)), m=0.03)

