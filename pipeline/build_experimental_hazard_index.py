"""Build a transparent, non-predictive Phase 8 hazard-index demonstration."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ADMIN = ("village_lgd_code", "district_lgd_code", "taluk_lgd_code", "village_name_en")
OUTPUT_COLUMNS = (
    *ADMIN,
    "elevation_mean_m", "slope_mean_deg", "historical_rainfall_7d_p95_mm",
    "conditional_strict_linked_event_count",
    "elevation_mean_minmax", "slope_mean_minmax", "terrain_component",
    "rainfall_7d_p95_minmax", "conditional_event_evidence_minmax",
    "experimental_hazard_index_0_100",
    "rainfall_feature_source", "terrain_feature_source", "event_evidence_source",
    "event_evidence_qualification", "index_method_version",
)


class ExperimentalHazardIndexError(ValueError):
    """Raised when the restricted experimental index cannot be built safely."""


def _minmax(series: pd.Series, name: str) -> pd.Series:
    minimum, maximum = float(series.min()), float(series.max())
    if not np.isfinite(minimum) or not np.isfinite(maximum) or maximum <= minimum:
        raise ExperimentalHazardIndexError(f"'{name}' cannot be min-max normalized across the 40 villages.")
    return (series - minimum) / (maximum - minimum)


def build_experimental_hazard_index(
    terrain_path: Path, village_time_path: Path, linkage_path: Path,
) -> pd.DataFrame:
    """Produce a descriptive index, not a target, score of event probability, or prediction."""
    terrain = pd.read_csv(terrain_path, dtype={column: str for column in ADMIN})
    time = pd.read_csv(village_time_path, dtype={"village_lgd_code": str}, parse_dates=["date"])
    linkage = pd.read_csv(linkage_path, dtype=str, keep_default_na=False)
    required_terrain = [*ADMIN, "elevation_mean_m", "slope_mean_deg"]
    required_time = [*ADMIN, "date", "rainfall_7d_mm"]
    required_linkage = ["spatial_linkage_status", "matched_village_lgd_code"]
    for frame, required, label in ((terrain, required_terrain, "terrain"), (time, required_time, "village-time"), (linkage, required_linkage, "linkage")):
        missing = set(required).difference(frame.columns)
        if missing:
            raise ExperimentalHazardIndexError(f"{label} input is missing: {', '.join(sorted(missing))}")
    if len(terrain) != 40 or terrain["village_lgd_code"].duplicated().any():
        raise ExperimentalHazardIndexError("Terrain input must contain exactly 40 unique validated villages.")
    if time["village_lgd_code"].nunique() != 40 or time.duplicated(["village_lgd_code", "date"]).any():
        raise ExperimentalHazardIndexError("Village-time input must contain one row per date for exactly 40 villages.")
    codes = set(terrain["village_lgd_code"])
    if set(time["village_lgd_code"]) != codes:
        raise ExperimentalHazardIndexError("Terrain and village-time village identifiers do not align.")
    if terrain.loc[:, required_terrain].isna().any().any():
        raise ExperimentalHazardIndexError("Terrain input has missing required values.")

    rainfall = time.groupby("village_lgd_code", as_index=False)["rainfall_7d_mm"].quantile(0.95, interpolation="linear")
    rainfall = rainfall.rename(columns={"rainfall_7d_mm": "historical_rainfall_7d_p95_mm"})
    if rainfall["historical_rainfall_7d_p95_mm"].isna().any():
        raise ExperimentalHazardIndexError("Rainfall p95 calculation produced missing values.")
    counts = linkage.loc[linkage["spatial_linkage_status"].eq("EXACT_POLYGON_MATCH")].groupby("matched_village_lgd_code").size()
    result = terrain.loc[:, required_terrain].merge(rainfall, on="village_lgd_code", how="left", validate="one_to_one")
    result["conditional_strict_linked_event_count"] = result["village_lgd_code"].map(counts).fillna(0).astype(int)

    result["elevation_mean_minmax"] = _minmax(result["elevation_mean_m"], "elevation_mean_m")
    result["slope_mean_minmax"] = _minmax(result["slope_mean_deg"], "slope_mean_deg")
    result["terrain_component"] = 0.50 * result["elevation_mean_minmax"] + 0.50 * result["slope_mean_minmax"]
    result["rainfall_7d_p95_minmax"] = _minmax(result["historical_rainfall_7d_p95_mm"], "historical_rainfall_7d_p95_mm")
    result["conditional_event_evidence_minmax"] = _minmax(np.log1p(result["conditional_strict_linked_event_count"]), "log1p(conditional_strict_linked_event_count)")
    result["experimental_hazard_index_0_100"] = 100 * (
        0.35 * result["terrain_component"]
        + 0.40 * result["rainfall_7d_p95_minmax"]
        + 0.25 * result["conditional_event_evidence_minmax"]
    )
    result["rainfall_feature_source"] = "data/processed/village_time_features.csv; 2017, 2019, 2022, 2023, 2024 IMD rainfall_7d_mm"
    result["terrain_feature_source"] = "data/processed/terrain_features_villages.csv"
    result["event_evidence_source"] = "data/processed/event_village_linkage.csv"
    result["event_evidence_qualification"] = "conditional strict-containment count; not a validated positive label or absence-based negative"
    result["index_method_version"] = "phase_8_experimental_v1"
    validate_experimental_hazard_index(result)
    return result.loc[:, OUTPUT_COLUMNS].sort_values("village_lgd_code", kind="stable").reset_index(drop=True)


def validate_experimental_hazard_index(index: pd.DataFrame) -> None:
    """Check the cardinality, alignment, finite values, and deterministic formula bounds."""
    if len(index) != 40 or index["village_lgd_code"].nunique() != 40:
        raise ExperimentalHazardIndexError("Output must contain exactly 40 unique village records.")
    numeric = (
        "elevation_mean_m", "slope_mean_deg", "historical_rainfall_7d_p95_mm",
        "conditional_strict_linked_event_count", "elevation_mean_minmax", "slope_mean_minmax",
        "terrain_component", "rainfall_7d_p95_minmax", "conditional_event_evidence_minmax",
        "experimental_hazard_index_0_100",
    )
    if index.loc[:, numeric].isna().any().any() or not np.isfinite(index.loc[:, numeric].to_numpy(dtype=float)).all():
        raise ExperimentalHazardIndexError("Output contains missing or non-finite numeric values.")
    normalized = ("elevation_mean_minmax", "slope_mean_minmax", "terrain_component", "rainfall_7d_p95_minmax", "conditional_event_evidence_minmax")
    if ((index.loc[:, normalized] < 0) | (index.loc[:, normalized] > 1)).any().any():
        raise ExperimentalHazardIndexError("A normalized component is outside [0, 1].")
    if not index["experimental_hazard_index_0_100"].between(0, 100).all():
        raise ExperimentalHazardIndexError("Experimental index is outside [0, 100].")
    expected = 100 * (0.35 * index["terrain_component"] + 0.40 * index["rainfall_7d_p95_minmax"] + 0.25 * index["conditional_event_evidence_minmax"])
    if not np.allclose(index["experimental_hazard_index_0_100"], expected, rtol=0, atol=1e-12):
        raise ExperimentalHazardIndexError("Experimental index does not match the documented formula.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the restricted, non-predictive Phase 8 hazard index.")
    parser.add_argument("--terrain", type=Path, default=ROOT / "data/processed/terrain_features_villages.csv")
    parser.add_argument("--village-time", type=Path, default=ROOT / "data/processed/village_time_features.csv")
    parser.add_argument("--linkage", type=Path, default=ROOT / "data/processed/event_village_linkage.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/experimental_hazard_index.csv")
    arguments = parser.parse_args()
    try:
        index = build_experimental_hazard_index(arguments.terrain, arguments.village_time, arguments.linkage)
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        index.to_csv(arguments.output, index=False)
    except (OSError, pd.errors.ParserError, ExperimentalHazardIndexError) as error:
        print(f"Experimental hazard-index processing failed: {error}")
        return 1
    print(f"Wrote {len(index)} experimental index rows for {index['village_lgd_code'].nunique()} villages: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
