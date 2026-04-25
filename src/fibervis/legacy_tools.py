"""Legacy Survey cutout URL and download helpers."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Tuple
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
    """Return a Legacy Survey cutout URL."""

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


def download_cutout_file(
    ra: float,
    dec: float,
    file_type: str,
    output_path: str | Path,
    overwrite: bool = False,
    layer: str = DEFAULT_LAYER,
    pixscale: float = DEFAULT_PIXSCALE,
) -> Path:
    """Download one Legacy Survey cutout file and return its output path."""

    path = Path(output_path)
    url = build_cutout_url(ra, dec, file_type, layer=layer, pixscale=pixscale)
    download_file(url, path, overwrite=overwrite)
    return path


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


def _append_suffix(path: Path, suffix: str) -> Path:
    """Append an output suffix without treating coordinate decimals as suffixes."""

    return path.parent / f"{path.name}{suffix}"
