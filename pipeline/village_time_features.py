"""Build the Phase 6E village-day feature table from validated inputs only."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pandas as pd

from rainfall.processing import RainfallPipelineError, extract_rainfall_features, open_and_validate_imd_dataset
from spatial.event_village_audit import exact_code_records, read_nilgiris_kmz


YEAR_FILES = {
    2017: Path("data/raw/rainfall/RF25_ind2017_rfp25.nc"),
    2019: Path("data/raw/rainfall/RF25_ind2019_rfp25.nc"),
    2022: Path("data/raw/rainfall/RF25_ind2022_rfp25.nc"),
    2023: Path("data/raw/rainfall/RF25_ind2023_rfp25.nc"),
    2024: Path("data/raw/rainfall/RF25_ind2024_rfp25.nc"),
}

ADMIN_COLUMNS = ("village_lgd_code", "district_lgd_code", "taluk_lgd_code", "village_name_en")
TERRAIN_COLUMNS = (
    "dem_valid_cell_count", "elevation_mean_m", "elevation_min_m", "elevation_max_m",
    "slope_mean_deg", "slope_min_deg", "slope_max_deg",
)
OUTPUT_COLUMNS = (
    *ADMIN_COLUMNS, "date", "rainfall_1d_mm", "rainfall_3d_mm", "rainfall_7d_mm",
    "imd_grid_latitude", "imd_grid_longitude", *TERRAIN_COLUMNS,
    "rainfall_source", "rainfall_assignment_method", "terrain_source", "polygon_source",
)


class VillageTimeFeatureError(ValueError):
    """Raised when the restricted village-time table cannot be constructed safely."""


def validated_village_points(villages_path: Path, kmz_path: Path) -> pd.DataFrame:
    """Return one interior representative point for each exact-ID eligible polygon.

    ``representative_point`` is guaranteed to be within its own supplied polygon.  It is
    used solely to select the coarse IMD grid cell, never to match an event or village.
    """
    villages = pd.read_csv(villages_path, dtype=str)
    missing = [column for column in ADMIN_COLUMNS if column not in villages.columns]
    if missing:
        raise VillageTimeFeatureError("Village master is missing: " + ", ".join(missing))
    records = exact_code_records(read_nilgiris_kmz(kmz_path), villages)
    if len(records) != 40:
        raise VillageTimeFeatureError(f"Expected exactly 40 eligible polygons; found {len(records)}.")
    by_code = villages.set_index("village_lgd_code")
    rows: list[dict[str, object]] = []
    for record in sorted(records, key=lambda item: item.attributes["vlcode"]):
        code = record.attributes["vlcode"]
        if record.geometry is None or not record.geometry.is_valid or record.geometry.is_empty:
            raise VillageTimeFeatureError(f"Eligible village '{code}' lacks a valid polygon.")
        point = record.geometry.representative_point()
        village = by_code.loc[code]
        rows.append({
            "village_lgd_code": code,
            "district_lgd_code": village["district_lgd_code"],
            "taluk_lgd_code": village["taluk_lgd_code"],
            "village_name_en": village["village_name_en"],
            "latitude": float(point.y), "longitude": float(point.x),
        })
    points = pd.DataFrame(rows)
    if points["village_lgd_code"].duplicated().any() or len(points) != 40:
        raise VillageTimeFeatureError("Eligible polygons do not provide 40 unique village identifiers.")
    return points


def _rainfall_for_year(year: int, path: Path, points: pd.DataFrame) -> pd.DataFrame:
    settlements = points.rename(columns={"village_lgd_code": "settlement_id", "village_name_en": "settlement_name"}).copy()
    settlements["region"] = "Tamil Nadu"
    settlements["district"] = "The Nilgiris"
    dataset = open_and_validate_imd_dataset(path, year)
    try:
        rainfall = extract_rainfall_features(dataset, settlements, year)
    finally:
        dataset.close()
    return rainfall.rename(columns={"settlement_id": "village_lgd_code"})


def build_village_time_features(
    villages_path: Path, kmz_path: Path, terrain_path: Path, year_files: Mapping[int, Path] = YEAR_FILES,
) -> pd.DataFrame:
    """Construct a no-label, no-imputation village-day table for the five approved years."""
    points = validated_village_points(villages_path, kmz_path)
    terrain = pd.read_csv(terrain_path, dtype={column: str for column in ADMIN_COLUMNS})
    missing = [column for column in (*ADMIN_COLUMNS, *TERRAIN_COLUMNS) if column not in terrain.columns]
    if missing:
        raise VillageTimeFeatureError("Terrain table is missing: " + ", ".join(missing))
    if len(terrain) != 40 or terrain["village_lgd_code"].duplicated().any():
        raise VillageTimeFeatureError("Terrain table must have exactly 40 unique village rows.")
    if set(terrain["village_lgd_code"]) != set(points["village_lgd_code"]):
        raise VillageTimeFeatureError("Terrain and eligible-polygon village identifiers do not align.")
    if terrain.loc[:, [*ADMIN_COLUMNS, *TERRAIN_COLUMNS]].isna().any().any():
        raise VillageTimeFeatureError("Terrain table has missing required values.")

    frames = [_rainfall_for_year(int(year), Path(path), points) for year, path in sorted(year_files.items())]
    rainfall = pd.concat(frames, ignore_index=True)
    rainfall = rainfall.drop(columns=["settlement_name", "latitude", "longitude", "region", "district"])
    result = rainfall.merge(terrain.loc[:, [*ADMIN_COLUMNS, *TERRAIN_COLUMNS]], on="village_lgd_code", how="left", validate="many_to_one")
    result["rainfall_source"] = result["date"].dt.year.map(lambda year: f"data/raw/rainfall/RF25_ind{year}_rfp25.nc")
    result["rainfall_assignment_method"] = "nearest_IMD_grid_cell_to_validated_polygon_interior_point"
    result["terrain_source"] = "data/processed/terrain_features_villages.csv"
    result["polygon_source"] = "data/raw/admin/vb_soi_tn.kmz (exact LGD-code-compatible polygons)"
    validate_village_time_features(result, year_files)
    return result.loc[:, OUTPUT_COLUMNS].sort_values(["village_lgd_code", "date"], kind="stable").reset_index(drop=True)


def validate_village_time_features(features: pd.DataFrame, year_files: Mapping[int, Path] = YEAR_FILES) -> None:
    """Enforce Phase 6E cardinality, coverage, null, and alignment invariants."""
    if not set(ADMIN_COLUMNS).issubset(features.columns):
        raise VillageTimeFeatureError("Village-time table has an incompatible administrative schema.")
    if features["village_lgd_code"].nunique() != 40:
        raise VillageTimeFeatureError("Village-time table must contain exactly 40 villages.")
    if features.duplicated(["village_lgd_code", "date"]).any():
        raise VillageTimeFeatureError("Village-time table has duplicate village-date rows.")
    dates = pd.to_datetime(features["date"], errors="coerce")
    if dates.isna().any():
        raise VillageTimeFeatureError("Village-time table has invalid dates.")
    for year in sorted(year_files):
        expected_dates = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")
        subset = features.loc[dates.dt.year == year]
        if len(subset) != 40 * len(expected_dates):
            raise VillageTimeFeatureError(f"Year {year} does not have 40 rows per calendar date.")
        if set(pd.to_datetime(subset["date"])) != set(expected_dates):
            raise VillageTimeFeatureError(f"Year {year} does not have complete calendar coverage.")
        if subset["rainfall_1d_mm"].isna().any():
            raise VillageTimeFeatureError(f"Year {year} has missing daily IMD rainfall.")
        if int(subset["rainfall_3d_mm"].isna().sum()) != 80 or int(subset["rainfall_7d_mm"].isna().sum()) != 240:
            raise VillageTimeFeatureError(f"Year {year} rolling-window null counts are not preserved.")
    if len(features) != 40 * sum(366 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 365 for year in year_files):
        raise VillageTimeFeatureError("Village-time table has an unexpected total row count.")
    if features.loc[:, [*ADMIN_COLUMNS, *TERRAIN_COLUMNS, "imd_grid_latitude", "imd_grid_longitude"]].isna().any().any():
        raise VillageTimeFeatureError("Village-time table has missing administrative, terrain, or IMD-grid values.")
    if features.groupby("village_lgd_code", dropna=False)[list(TERRAIN_COLUMNS)].nunique(dropna=False).gt(1).any().any():
        raise VillageTimeFeatureError("Terrain values are not constant within a village.")


def write_village_time_features(features: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False, date_format="%Y-%m-%d")
