#!/usr/bin/env python3
"""Create a DR2 RGB PNG and overlay fiber coordinates from CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fibervis.fiber_layout import IFULayout
from fibervis.fits_rgb import save_csv_fiber_overlay_png
from fibervis.legacy_tools import DEFAULT_LAYER, DEFAULT_PIXSCALE, download_cutout_file


def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Create an RGB PNG from a 3-channel FITS file and overlay fibers "
            "from a CSV produced by bin/write_fiber_layout.py."
        )
    )
    parser.add_argument("fits_file", help="Input FITS file.")
    parser.add_argument("fiber_csv", help="Fiber coordinate CSV file.")
    parser.add_argument("output_png", help="Output PNG file.")
    parser.add_argument(
        "--get-fits",
        "--get_fits",
        "--getfits",
        action="store_true",
        help=(
            "Download the FITS cutout into fits_file before rendering. "
            "Requires --center-ra and --center-dec."
        ),
    )
    parser.add_argument(
        "--write-layout",
        "--write_layout",
        "--writelayout",
        action="store_true",
        help=(
            "Generate fiber_csv before rendering. "
            "Requires --n-fibers, --fiber-diameter, and --separation-ratio."
        ),
    )
    parser.add_argument(
        "--center-ra",
        type=float,
        default=None,
        help=(
            "Center RA in degrees; required if CSV uses x_arcsec/y_arcsec, "
            "and required with --get-fits."
        ),
    )
    parser.add_argument(
        "--center-dec",
        type=float,
        default=None,
        help=(
            "Center Dec in degrees; required if CSV uses x_arcsec/y_arcsec, "
            "and required with --get-fits."
        ),
    )
    parser.add_argument(
        "--n-fibers",
        type=int,
        default=None,
        help="Fiber count for --write-layout.",
    )
    parser.add_argument(
        "--fiber-diameter",
        type=float,
        default=None,
        help="Fiber diameter in arcseconds for --write-layout.",
    )
    parser.add_argument(
        "--separation-ratio",
        type=float,
        default=None,
        help="Center spacing / diameter for --write-layout.",
    )
    parser.add_argument(
        "--layer",
        default=DEFAULT_LAYER,
        help=f"Legacy Survey layer for --get-fits (default: {DEFAULT_LAYER}).",
    )
    parser.add_argument(
        "--pixscale",
        type=float,
        default=DEFAULT_PIXSCALE,
        help=(
            "Legacy Survey pixel scale (arcsec/pixel) for --get-fits "
            f"(default: {DEFAULT_PIXSCALE})."
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files when using --get-fits or --write-layout.",
    )
    parser.add_argument(
        "--image-hdu",
        type=int,
        default=0,
        help="Image HDU index containing the 3-channel data and WCS (default: 0).",
    )
    parser.add_argument(
        "--g-band",
        type=int,
        default=0,
        help="Band index or HDU for g channel (default: 0).",
    )
    parser.add_argument(
        "--r-band",
        type=int,
        default=1,
        help="Band index or HDU for r channel (default: 1).",
    )
    parser.add_argument(
        "--z-band",
        type=int,
        default=2,
        help="Band index or HDU for z channel (default: 2).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional plot title.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Output PNG DPI (default: 150).",
    )
    parser.add_argument(
        "--no-stats",
        action="store_true",
        help="Suppress the layout stats text box in the upper-left corner.",
    )
    return parser.parse_args(args)


def main(args: Iterable[str] | None = None) -> int:
    """Run the command-line interface."""

    parsed = parse_args(args)
    try:
        _validate_args(parsed)
    except ValueError as exc:
        raise SystemExit(f"Error: {exc}") from exc

    if parsed.get_fits:
        download_cutout_file(
            parsed.center_ra,
            parsed.center_dec,
            "fits",
            parsed.fits_file,
            overwrite=parsed.overwrite,
            layer=parsed.layer,
            pixscale=parsed.pixscale,
        )
        print(f"Downloaded FITS: {parsed.fits_file}")

    if parsed.write_layout:
        layout = IFULayout(
            n_fibers=parsed.n_fibers,
            fiber_diameter=parsed.fiber_diameter,
            separation_ratio=parsed.separation_ratio,
            center_ra=parsed.center_ra,
            center_dec=parsed.center_dec,
        )
        rows = layout.csv_rows(center_ra=parsed.center_ra, center_dec=parsed.center_dec)
        _write_rows_to_csv(parsed.fiber_csv, rows, overwrite=parsed.overwrite)
        print(f"Wrote fiber CSV: {parsed.fiber_csv}")

    save_csv_fiber_overlay_png(
        fits_path=parsed.fits_file,
        csv_path=parsed.fiber_csv,
        output_path=parsed.output_png,
        center_ra=parsed.center_ra,
        center_dec=parsed.center_dec,
        image_hdu=parsed.image_hdu,
        g=parsed.g_band,
        r=parsed.r_band,
        z=parsed.z_band,
        title=parsed.title,
        dpi=parsed.dpi,
        show_stats=not parsed.no_stats,
    )
    print(f"Wrote overlay PNG: {parsed.output_png}")
    return 0


def _validate_args(parsed: argparse.Namespace) -> None:
    """Validate cross-argument requirements."""

    has_ra = parsed.center_ra is not None
    has_dec = parsed.center_dec is not None
    if has_ra != has_dec:
        raise ValueError("center_ra and center_dec must be provided together.")

    if parsed.get_fits and not (has_ra and has_dec):
        raise ValueError("--get-fits requires --center-ra and --center-dec.")

    if parsed.write_layout:
        missing = [
            flag
            for flag, value in (
                ("--n-fibers", parsed.n_fibers),
                ("--fiber-diameter", parsed.fiber_diameter),
                ("--separation-ratio", parsed.separation_ratio),
            )
            if value is None
        ]
        if missing:
            raise ValueError(f"--write-layout requires {', '.join(missing)}.")


def _write_rows_to_csv(path: str, rows: list[dict[str, float]], overwrite: bool = False) -> None:
    """Write row dictionaries to a CSV file."""

    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"{output_path} already exists; use --overwrite to replace it.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("No rows were generated for CSV output.")

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
