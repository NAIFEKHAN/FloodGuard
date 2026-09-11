"""Command-line entry point for local DEM terrain feature extraction."""

from __future__ import annotations

import argparse
from pathlib import Path

from terrain.processing import TerrainPipelineError, build_terrain_features, write_terrain_features


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract elevation and slope from a local DEM for settlement points."
    )
    parser.add_argument(
        "--dem",
        type=Path,
        default=Path("data/raw/dem/dem.tif"),
        help="Local GeoTIFF DEM path (default: data/raw/dem/dem.tif).",
    )
    parser.add_argument(
        "--settlements",
        type=Path,
        default=Path("data/raw/settlements/settlements.csv"),
        help="Settlement CSV path (default: data/raw/settlements/settlements.csv).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/terrain_features.csv"),
        help="Derived CSV output path (default: data/processed/terrain_features.csv).",
    )
    return parser.parse_args()


def main() -> int:
    """Run terrain extraction and report an actionable error rather than inventing values."""
    arguments = parse_arguments()
    try:
        features = build_terrain_features(arguments.dem, arguments.settlements)
        write_terrain_features(features, arguments.output)
    except TerrainPipelineError as error:
        print(f"Terrain pipeline failed: {error}")
        return 1

    print(f"Wrote {len(features)} terrain feature rows to: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
