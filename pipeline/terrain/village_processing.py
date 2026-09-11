"""Exact-ID village-polygon terrain summaries from a local DEM."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask, geometry_window
from rasterio.transform import xy
from rasterio.warp import transform_geom
from shapely.geometry import mapping

from spatial.event_village_audit import exact_code_records, read_nilgiris_kmz
from terrain.processing import TerrainPipelineError, read_dem_metadata


VILLAGE_TERRAIN_COLUMNS = (
    "village_lgd_code", "district_lgd_code", "taluk_lgd_code", "village_name_en",
    "dem_valid_cell_count", "elevation_mean_m", "elevation_min_m", "elevation_max_m",
    "slope_mean_deg", "slope_min_deg", "slope_max_deg",
)


class VillageTerrainError(TerrainPipelineError):
    """Raised when exact village polygons cannot safely receive DEM summaries."""


def _slope_degrees(elevation: np.ndarray, transform, geographic: bool) -> np.ndarray:
    """Calculate degree slope for a padded DEM window using the project slope method."""
    resolution_x = abs(transform.a)
    resolution_y = abs(transform.e)
    if resolution_x == 0 or resolution_y == 0:
        raise VillageTerrainError("DEM has invalid zero raster resolution.")
    if geographic:
        rows = np.arange(elevation.shape[0])
        _, latitudes = xy(transform, rows, np.zeros(elevation.shape[0]), offset="center")
        metres_x = 111_320.0 * np.cos(np.deg2rad(np.asarray(latitudes))) * resolution_x
        metres_y = 110_574.0 * resolution_y
        if (metres_x <= 0).any() or metres_y <= 0:
            raise VillageTerrainError("DEM geographic resolution cannot be converted to metres.")
    else:
        metres_x = np.full(elevation.shape[0], resolution_x, dtype=float)
        metres_y = resolution_y
    with np.errstate(invalid="ignore"):
        rise_run_y = np.gradient(elevation, axis=0) / metres_y
        rise_run_x = np.gradient(elevation, axis=1) / metres_x[:, np.newaxis]
        return np.degrees(np.arctan(np.hypot(rise_run_x, rise_run_y)))


def _padded_window(dataset: rasterio.io.DatasetReader, geometry: dict) -> rasterio.windows.Window:
    core = geometry_window(dataset, [geometry]).round_offsets().round_lengths()
    left = max(0, int(core.col_off) - 1)
    top = max(0, int(core.row_off) - 1)
    right = min(dataset.width, int(core.col_off + core.width) + 1)
    bottom = min(dataset.height, int(core.row_off + core.height) + 1)
    if right - left < 2 or bottom - top < 2:
        raise VillageTerrainError("Village polygon cannot receive slope at the DEM edge.")
    return rasterio.windows.Window(left, top, right - left, bottom - top)


def build_village_terrain_features(dem_path: Path, villages_path: Path, kmz_path: Path) -> pd.DataFrame:
    """Summarise elevation and DEM-derived slope for exact-ID Nilgiris village polygons.

    A cell contributes only when its centre is within the polygon and both its elevation and
    slope are finite. The one-cell padding is used solely to calculate slope at selected cells.
    """
    required = ("village_lgd_code", "district_lgd_code", "taluk_lgd_code", "village_name_en")
    villages = pd.read_csv(villages_path, dtype=str)
    missing = [column for column in required if column not in villages.columns]
    if missing:
        raise VillageTerrainError("Village table is missing required columns: " + ", ".join(missing))
    if villages.loc[:, required].isna().any().any() or (villages.loc[:, required] == "").any().any():
        raise VillageTerrainError("Village table has a missing required identifier or name.")
    if villages["village_lgd_code"].duplicated().any():
        raise VillageTerrainError("Village table has duplicate village LGD codes.")

    records = exact_code_records(read_nilgiris_kmz(kmz_path), villages)
    if not records:
        raise VillageTerrainError("No exact village/KMZ code matches were found.")
    codes = [record.attributes.get("vlcode", "") for record in records]
    if len(codes) != len(set(codes)):
        raise VillageTerrainError("Exact village/KMZ matches contain duplicate village codes.")
    if any(record.geometry is None or not record.geometry.is_valid for record in records):
        raise VillageTerrainError("An exact village/KMZ match has missing or invalid geometry.")

    read_dem_metadata(dem_path)
    village_by_code = villages.set_index("village_lgd_code")
    rows: list[dict[str, object]] = []
    with rasterio.open(dem_path) as dataset:
        for record in sorted(records, key=lambda item: item.attributes["vlcode"]):
            code = record.attributes["vlcode"]
            geometry = transform_geom("EPSG:4326", dataset.crs, mapping(record.geometry), precision=-1)
            try:
                window = _padded_window(dataset, geometry)
            except ValueError as error:
                raise VillageTerrainError(f"Village '{code}' is outside DEM coverage.") from error
            elevation = dataset.read(1, window=window, masked=True).astype(float).filled(np.nan)
            slope = _slope_degrees(elevation, dataset.window_transform(window), dataset.crs.is_geographic)
            inside = geometry_mask([geometry], out_shape=elevation.shape, transform=dataset.window_transform(window), invert=True, all_touched=False)
            valid = inside & np.isfinite(elevation) & np.isfinite(slope)
            if not valid.any():
                raise VillageTerrainError(f"Village '{code}' has no finite elevation/slope DEM cells.")
            elevations = elevation[valid]
            slopes = slope[valid]
            village = village_by_code.loc[code]
            rows.append({
                "village_lgd_code": code,
                "district_lgd_code": village["district_lgd_code"],
                "taluk_lgd_code": village["taluk_lgd_code"],
                "village_name_en": village["village_name_en"],
                "dem_valid_cell_count": int(valid.sum()),
                "elevation_mean_m": float(elevations.mean()),
                "elevation_min_m": float(elevations.min()),
                "elevation_max_m": float(elevations.max()),
                "slope_mean_deg": float(slopes.mean()),
                "slope_min_deg": float(slopes.min()),
                "slope_max_deg": float(slopes.max()),
            })
    return pd.DataFrame(rows, columns=VILLAGE_TERRAIN_COLUMNS)


def write_village_terrain_features(features: pd.DataFrame, output_path: Path) -> None:
    """Write exact-village terrain summaries without changing source inputs."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
