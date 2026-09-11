"""Reusable, local-DEM terrain feature extraction functions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj.exceptions import ProjError
import rasterio


REQUIRED_SETTLEMENT_COLUMNS = (
    "settlement_id",
    "settlement_name",
    "latitude",
    "longitude",
    "region",
    "district",
)


class TerrainPipelineError(ValueError):
    """Raised when terrain inputs cannot safely produce feature values."""


@dataclass(frozen=True)
class DemMetadata:
    """The metadata recorded from a validated single-band DEM."""

    crs: str
    resolution_x: float
    resolution_y: float
    bounds: tuple[float, float, float, float]
    nodata: float | None
    width: int
    height: int


def validate_settlements(settlements: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize settlement points expressed as WGS84 latitude/longitude."""
    missing = [column for column in REQUIRED_SETTLEMENT_COLUMNS if column not in settlements.columns]
    if missing:
        raise TerrainPipelineError(
            "Settlement input is missing required columns: " + ", ".join(missing)
        )
    if settlements.empty:
        raise TerrainPipelineError("Settlement input contains no rows.")

    validated = settlements.loc[:, REQUIRED_SETTLEMENT_COLUMNS].copy()
    for column in ("settlement_id", "settlement_name", "region", "district"):
        validated[column] = validated[column].astype("string").str.strip()
        if validated[column].isna().any() or (validated[column] == "").any():
            raise TerrainPipelineError(f"Settlement input has missing values in '{column}'.")

    if validated["settlement_id"].duplicated().any():
        raise TerrainPipelineError("Settlement input contains duplicate settlement_id values.")

    for column in ("latitude", "longitude"):
        validated[column] = pd.to_numeric(validated[column], errors="coerce")
        if validated[column].isna().any() or not np.isfinite(validated[column]).all():
            raise TerrainPipelineError(f"Settlement input has invalid '{column}' values.")

    if not validated["latitude"].between(-90, 90).all():
        raise TerrainPipelineError("Settlement latitude values must be between -90 and 90.")
    if not validated["longitude"].between(-180, 180).all():
        raise TerrainPipelineError("Settlement longitude values must be between -180 and 180.")
    return validated


def load_settlements(path: Path) -> pd.DataFrame:
    """Load and validate a UTF-8 settlement CSV."""
    if not path.is_file():
        raise TerrainPipelineError(f"Settlement CSV was not found: {path}")
    try:
        settlements = pd.read_csv(path)
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise TerrainPipelineError(f"Unable to read settlement CSV '{path}': {error}") from error
    return validate_settlements(settlements)


def read_dem_metadata(path: Path) -> DemMetadata:
    """Open a DEM and return required metadata after basic raster validation."""
    if not path.is_file():
        raise TerrainPipelineError(f"DEM file was not found: {path}")
    try:
        with rasterio.open(path) as dataset:
            if dataset.crs is None:
                raise TerrainPipelineError("DEM has no CRS; a CRS is required for terrain processing.")
            if dataset.count < 1 or dataset.width < 2 or dataset.height < 2:
                raise TerrainPipelineError("DEM must have at least one band and dimensions of at least 2 by 2.")
            return DemMetadata(
                crs=dataset.crs.to_string(),
                resolution_x=abs(dataset.transform.a),
                resolution_y=abs(dataset.transform.e),
                bounds=(dataset.bounds.left, dataset.bounds.bottom, dataset.bounds.right, dataset.bounds.top),
                nodata=dataset.nodata,
                width=dataset.width,
                height=dataset.height,
            )
    except TerrainPipelineError:
        raise
    except rasterio.errors.RasterioError as error:
        raise TerrainPipelineError(f"Unable to open DEM '{path}': {error}") from error


def _metres_per_pixel(dataset: rasterio.io.DatasetReader) -> tuple[np.ndarray, float]:
    """Return east-west (per raster row) and north-south pixel dimensions in metres."""
    resolution_x = abs(dataset.transform.a)
    resolution_y = abs(dataset.transform.e)
    if resolution_x == 0 or resolution_y == 0:
        raise TerrainPipelineError("DEM has invalid zero raster resolution.")

    if dataset.crs.is_geographic:
        rows = np.arange(dataset.height)
        _, latitudes = rasterio.transform.xy(
            dataset.transform, rows, np.zeros(dataset.height), offset="center"
        )
        latitude_radians = np.deg2rad(np.asarray(latitudes, dtype=float))
        metres_x = 111_320.0 * np.cos(latitude_radians) * resolution_x
        metres_y = 110_574.0 * resolution_y
        if (metres_x <= 0).any() or metres_y <= 0:
            raise TerrainPipelineError("DEM geographic resolution cannot be converted to metres.")
        return metres_x, metres_y

    linear_units = (dataset.crs.linear_units or "").lower()
    if linear_units not in {"metre", "meter", "metres", "meters", "m"}:
        raise TerrainPipelineError(
            f"DEM CRS linear unit '{linear_units or 'unknown'}' is not supported; use metres."
        )
    return np.full(dataset.height, resolution_x, dtype=float), resolution_y


def calculate_slope_degrees(dataset: rasterio.io.DatasetReader) -> np.ndarray:
    """Calculate raster slope in degrees from DEM elevations and pixel dimensions in metres."""
    elevation = dataset.read(1, masked=True).astype(float).filled(np.nan)
    metres_x, metres_y = _metres_per_pixel(dataset)
    with np.errstate(invalid="ignore"):
        rise_run_y = np.gradient(elevation, axis=0) / metres_y
        rise_run_x = np.gradient(elevation, axis=1) / metres_x[:, np.newaxis]
        return np.degrees(np.arctan(np.hypot(rise_run_x, rise_run_y)))


def build_terrain_features(dem_path: Path, settlements_path: Path) -> pd.DataFrame:
    """Extract elevation and DEM-derived slope for validated WGS84 settlement points."""
    settlements = load_settlements(settlements_path)
    read_dem_metadata(dem_path)

    try:
        with rasterio.open(dem_path) as dataset:
            try:
                points = gpd.GeoDataFrame(
                    settlements,
                    geometry=gpd.points_from_xy(settlements.longitude, settlements.latitude),
                    crs="EPSG:4326",
                ).to_crs(dataset.crs)
            except ProjError as error:
                raise TerrainPipelineError(
                    f"DEM CRS '{dataset.crs}' cannot be used to transform settlement coordinates."
                ) from error
            slope = calculate_slope_degrees(dataset)
            elevation = dataset.read(1, masked=True).astype(float).filled(np.nan)

            extracted_elevation: list[float] = []
            extracted_slope: list[float] = []
            for settlement, point in zip(settlements.itertuples(index=False), points.geometry, strict=True):
                try:
                    row, column = dataset.index(point.x, point.y)
                except (ValueError, TypeError) as error:
                    raise TerrainPipelineError(
                        f"Settlement '{settlement.settlement_id}' has coordinates that cannot be mapped to the DEM."
                    ) from error
                if not (0 <= row < dataset.height and 0 <= column < dataset.width):
                    raise TerrainPipelineError(
                        f"Settlement '{settlement.settlement_id}' is outside DEM coverage."
                    )
                elevation_value = elevation[row, column]
                if not np.isfinite(elevation_value):
                    raise TerrainPipelineError(
                        f"Settlement '{settlement.settlement_id}' samples DEM nodata for elevation."
                    )
                slope_value = slope[row, column]
                if not np.isfinite(slope_value):
                    raise TerrainPipelineError(
                        f"Settlement '{settlement.settlement_id}' cannot receive slope because surrounding DEM values include nodata."
                    )
                extracted_elevation.append(float(elevation_value))
                extracted_slope.append(float(slope_value))
    except TerrainPipelineError:
        raise
    except rasterio.errors.RasterioError as error:
        raise TerrainPipelineError(f"Unable to process DEM '{dem_path}': {error}") from error

    result = settlements.copy()
    result["elevation_m"] = extracted_elevation
    result["slope_deg"] = extracted_slope
    return result


def write_terrain_features(features: pd.DataFrame, output_path: Path) -> None:
    """Write a terrain feature table, creating its output directory when necessary."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
