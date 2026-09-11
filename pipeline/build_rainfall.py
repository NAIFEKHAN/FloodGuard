"""Command-line entry point for IMD daily rainfall feature extraction."""

from __future__ import annotations

import argparse
from pathlib import Path

from rainfall.processing import RainfallPipelineError, build_rainfall_features, write_rainfall_features


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract daily and antecedent rainfall from a local IMD NetCDF file."
    )
    parser.add_argument(
        "--netcdf",
        type=Path,
        default=Path("data/raw/rainfall/RF25_ind2024_rfp25.nc"),
        help="Local IMD NetCDF path.",
    )
    parser.add_argument(
        "--settlements",
        type=Path,
        default=Path("data/demo/settlements_demo.csv"),
        help="Settlement CSV path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/rainfall_features.csv"),
        help="Derived CSV output path.",
    )
    return parser.parse_args()


def main() -> int:
    """Build features and print an actionable error when source data is unusable."""
    arguments = parse_arguments()
    try:
        features = build_rainfall_features(arguments.netcdf, arguments.settlements)
        write_rainfall_features(features, arguments.output)
    except RainfallPipelineError as error:
        print(f"Rainfall pipeline failed: {error}")
        return 1

    print(f"Wrote {len(features)} rainfall feature rows to: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
