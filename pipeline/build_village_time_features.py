"""Command-line entry point for the bounded Phase 6E feature table."""

from __future__ import annotations

import argparse
from pathlib import Path

from rainfall.processing import RainfallPipelineError
from village_time_features import VillageTimeFeatureError, build_village_time_features, write_village_time_features


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the 40-village, five-year Phase 6E feature table.")
    parser.add_argument("--villages", type=Path, default=ROOT / "data/processed/nilgiris_villages.csv")
    parser.add_argument("--kmz", type=Path, default=ROOT / "data/raw/admin/vb_soi_tn.kmz")
    parser.add_argument("--terrain", type=Path, default=ROOT / "data/processed/terrain_features_villages.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/village_time_features.csv")
    arguments = parser.parse_args()
    try:
        features = build_village_time_features(arguments.villages, arguments.kmz, arguments.terrain)
        write_village_time_features(features, arguments.output)
    except (OSError, RainfallPipelineError, VillageTimeFeatureError) as error:
        print(f"Village-time feature processing failed: {error}")
        return 1
    print(f"Wrote {len(features)} village-day feature rows for {features['village_lgd_code'].nunique()} villages: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
