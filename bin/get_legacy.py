#!/usr/bin/env python3
"""Download Legacy Survey JPEG and FITS cutouts for a sky position."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fibervis.legacy_tools import DEFAULT_LAYER, DEFAULT_PIXSCALE, download_cutouts


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


if __name__ == "__main__":
    raise SystemExit(main())
