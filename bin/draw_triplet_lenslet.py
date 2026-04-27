#!/usr/bin/env python3
"""Plot a three-lenslet IFU schematic with spacing annotation."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fibervis.lenslet import draw_lenslet_triplet


def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Create a schematic of three touching hexagonal lenslets "
            "(two on top, one centered below) with inscribed circles."
        )
    )
    parser.add_argument(
        "-o",
        "--output",
        default="lenslet_triplet.png",
        help="Output PNG file path (default: lenslet_triplet.png).",
    )
    parser.add_argument(
        "--pitch",
        type=float,
        default=330.0,
        help="Label for center-to-center separation between the top lenslets in microns.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Output DPI (default: 200).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the plot interactively after writing the PNG.",
    )
    return parser.parse_args(args)


def main(args: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""

    parsed = parse_args(args)
    draw_lenslet_triplet(
        pitch=parsed.pitch,
        output_path=parsed.output,
        dpi=parsed.dpi,
        show=parsed.show,
    )
    print(f"Wrote lenslet schematic: {parsed.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
