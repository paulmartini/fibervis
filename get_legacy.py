#!/usr/bin/env python3
"""Download Legacy Survey JPEG and FITS cutouts for a sky position."""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path
from typing import Iterable, Tuple
from urllib.parse import urlencode
from urllib.request import urlretrieve

BASE_URL = "https://www.legacysurvey.org/viewer"
DEFAULT_LAYER = "ls-dr9"
DEFAULT_PIXSCALE = 0.25


def build_cutout_url(
    ra: float,
    dec: float,
    file_type: str,
    layer: str = DEFAULT_LAYER,
    pixscale: float = DEFAULT_PIXSCALE,
) -> str:
    """Return a Legacy Survey cutout URL.

    Parameters
    ----------
    ra, dec
        Sky coordinates in degrees.
    file_type
        Either ``"jpg"`` or ``"fits"``.
    layer
        Legacy Survey viewer layer.
    pixscale
        Pixel scale in arcseconds per pixel.
    """

    if file_type not in {"jpg", "fits"}:
        raise ValueError("file_type must be 'jpg' or 'fits'.")

    query = urlencode({"ra": ra, "dec": dec, "layer": layer, "pixscale": pixscale})
    return f"{BASE_URL}/cutout.{file_type}?{query}"


def cutout_output_paths(
    ra: float,
    dec: float,
    output: str | None = None,
) -> Tuple[Path, Path]:
    """Return ``(jpg_path, fits_path)`` for the requested output basename."""

    if output is None:
        stem = Path(f"cutout_{ra:.4f}_{dec:.4f}")
    else:
        output_path = Path(output)
        stem = (
            output_path.with_suffix("")
            if output_path.suffix.lower() in {".jpg", ".jpeg", ".fits"}
            else output_path
        )

    return _append_suffix(stem, ".jpg"), _append_suffix(stem, ".fits")


def download_file(url: str, output_path: Path, overwrite: bool = False) -> bool:
    """Download ``url`` to ``output_path``.

    Returns ``True`` when a download occurred and ``False`` when an existing
    file was left unchanged.
    """

    if output_path.exists() and not overwrite:
        warnings.warn(
            f"{output_path} already exists; use --overwrite to replace it.",
            UserWarning,
            stacklevel=2,
        )
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, output_path)
    return True


def download_cutouts(
    ra: float,
    dec: float,
    output: str | None = None,
    overwrite: bool = False,
    layer: str = DEFAULT_LAYER,
    pixscale: float = DEFAULT_PIXSCALE,
) -> Tuple[Path, Path]:
    """Download both JPEG and FITS cutouts and return their paths."""

    jpg_path, fits_path = cutout_output_paths(ra, dec, output)
    downloads = (
        ("jpg", jpg_path),
        ("fits", fits_path),
    )

    for file_type, output_path in downloads:
        url = build_cutout_url(ra, dec, file_type, layer=layer, pixscale=pixscale)
        downloaded = download_file(url, output_path, overwrite=overwrite)
        status = "Downloaded" if downloaded else "Skipped"
        print(f"{status}: {output_path}")

    return jpg_path, fits_path


def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Download Legacy Survey JPEG and FITS cutouts for a sky position."
    )
    parser.add_argument("ra", type=float, help="Right ascension in degrees.")
    parser.add_argument("dec", type=float, help="Declination in degrees.")
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Optional output basename. The script writes '<basename>.jpg' and "
            "'<basename>.fits'. If a suffix is supplied, it is replaced."
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing output files. By default existing files are not downloaded.",
    )
    parser.add_argument(
        "--layer",
        default=DEFAULT_LAYER,
        help=f"Legacy Survey layer to request. Default: {DEFAULT_LAYER}.",
    )
    parser.add_argument(
        "--pixscale",
        type=float,
        default=DEFAULT_PIXSCALE,
        help=f"Pixel scale in arcseconds per pixel. Default: {DEFAULT_PIXSCALE}.",
    )
    return parser.parse_args(args)


def main(args: Iterable[str] | None = None) -> int:
    """Run the command-line interface."""

    parsed = parse_args(args)
    download_cutouts(
        parsed.ra,
        parsed.dec,
        output=parsed.output,
        overwrite=parsed.overwrite,
        layer=parsed.layer,
        pixscale=parsed.pixscale,
    )
    return 0


def _append_suffix(path: Path, suffix: str) -> Path:
    """Append an output suffix without treating coordinate decimals as suffixes."""

    return path.parent / f"{path.name}{suffix}"


if __name__ == "__main__":
    raise SystemExit(main())
