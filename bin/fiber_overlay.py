#!/usr/bin/env python3
"""Create a DR2 RGB PNG and overlay fiber coordinates from CSV."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fibervis.fits_rgb import save_csv_fiber_overlay_png


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
        "--center-ra",
        type=float,
        default=None,
        help="Center RA in degrees; required if CSV uses x_arcsec/y_arcsec.",
    )
    parser.add_argument(
        "--center-dec",
        type=float,
        default=None,
        help="Center Dec in degrees; required if CSV uses x_arcsec/y_arcsec.",
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


if __name__ == "__main__":
    raise SystemExit(main())
