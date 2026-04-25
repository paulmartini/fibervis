#!/usr/bin/env python3
"""Write fiber layout coordinates to a CSV file."""

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


def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Write an IFU fiber layout CSV. "
            "Without center coordinates, output columns are x_arcsec/y_arcsec. "
            "With center_ra and center_dec, output columns are ra_deg/dec_deg."
        )
    )
    parser.add_argument(
        "output_csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--n-fibers",
        type=int,
        required=True,
        help="Number of fibers in the bundle.",
    )
    parser.add_argument(
        "--fiber-diameter",
        type=float,
        required=True,
        help="Fiber diameter in arcseconds.",
    )
    parser.add_argument(
        "--separation-ratio",
        type=float,
        required=True,
        help="Center-to-center spacing divided by fiber diameter.",
    )
    parser.add_argument(
        "--center-ra",
        type=float,
        default=None,
        help="Optional center right ascension in degrees.",
    )
    parser.add_argument(
        "--center-dec",
        type=float,
        default=None,
        help="Optional center declination in degrees.",
    )
    return parser.parse_args(args)


def write_rows_to_csv(path: str, rows: list[dict[str, float]]) -> None:
    """Write row dictionaries to a CSV file."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("No rows were generated for CSV output.")

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main(args: Iterable[str] | None = None) -> int:
    """Run the command-line interface."""

    parsed = parse_args(args)
    layout = IFULayout(
        n_fibers=parsed.n_fibers,
        fiber_diameter=parsed.fiber_diameter,
        separation_ratio=parsed.separation_ratio,
        center_ra=parsed.center_ra,
        center_dec=parsed.center_dec,
    )
    rows = layout.csv_rows(center_ra=parsed.center_ra, center_dec=parsed.center_dec)
    write_rows_to_csv(parsed.output_csv, rows)
    print(f"Wrote {len(rows)} fibers to {parsed.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
