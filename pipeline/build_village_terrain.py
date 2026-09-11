"""Build terrain summaries for exact-ID Nilgiris village polygons only."""

from __future__ import annotations

import argparse
from pathlib import Path

from terrain.village_processing import VillageTerrainError, build_village_terrain_features, write_village_terrain_features


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarise a local DEM for exact-ID village polygons.")
    parser.add_argument("--dem", type=Path, default=Path("data/processed/dem_nilgiris_mosaic.tif"))
    parser.add_argument("--villages", type=Path, default=Path("data/processed/nilgiris_villages.csv"))
    parser.add_argument("--kmz", type=Path, default=Path("data/raw/admin/vb_soi_tn.kmz"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/terrain_features_villages.csv"))
    arguments = parser.parse_args()
    try:
        features = build_village_terrain_features(arguments.dem, arguments.villages, arguments.kmz)
        write_village_terrain_features(features, arguments.output)
    except VillageTerrainError as error:
        print(f"Village terrain pipeline failed: {error}")
        return 1
    print(f"Wrote {len(features)} exact-village terrain rows to: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
