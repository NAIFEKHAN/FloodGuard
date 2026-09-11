"""Extract daily and antecedent rainfall features from an IMD NetCDF file."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


REQUIRED_SETTLEMENT_COLUMNS = (
    "settlement_id",
    "settlement_name",
    "latitude",
    "longitude",
    "region",
    "district",
)
REQUIRED_COORDINATES = ("TIME", "LATITUDE", "LONGITUDE")
RAINFALL_VARIABLE = "RAINFALL"
OUTPUT_COLUMNS = (
    *REQUIRED_SETTLEMENT_COLUMNS,
    "date",
    "rainfall_1d_mm",
    "rainfall_3d_mm",
    "rainfall_7d_mm",
    "imd_grid_latitude",
    "imd_grid_longitude",
)


class RainfallPipelineError(ValueError):
    """Raised when inputs cannot safely produce IMD rainfall features."""


def validate_settlements(settlements: pd.DataFrame) -> pd.DataFrame:
    """Validate settlement points expressed as WGS84 latitude/longitude."""
    missing = [column for column in REQUIRED_SETTLEMENT_COLUMNS if column not in settlements.columns]
    if missing:
        raise RainfallPipelineError(
            "Settlement input is missing required columns: " + ", ".join(missing)
        )
    if settlements.empty:
        raise RainfallPipelineError("Settlement input contains no rows.")

    validated = settlements.loc[:, REQUIRED_SETTLEMENT_COLUMNS].copy()
    for column in ("settlement_id", "settlement_name", "region", "district"):
        validated[column] = validated[column].astype("string").str.strip()
        if validated[column].isna().any() or (validated[column] == "").any():
            raise RainfallPipelineError(f"Settlement input has missing values in '{column}'.")
    if validated["settlement_id"].duplicated().any():
        raise RainfallPipelineError("Settlement input contains duplicate settlement_id values.")

    for column in ("latitude", "longitude"):
        validated[column] = pd.to_numeric(validated[column], errors="coerce")
        if validated[column].isna().any() or not np.isfinite(validated[column]).all():
            raise RainfallPipelineError(f"Settlement input has invalid '{column}' values.")
    if not validated["latitude"].between(-90, 90).all():
        raise RainfallPipelineError("Settlement latitude values must be between -90 and 90.")
    if not validated["longitude"].between(-180, 180).all():
        raise RainfallPipelineError("Settlement longitude values must be between -180 and 180.")
    return validated


def load_settlements(path: Path) -> pd.DataFrame:
    """Load and validate a settlement CSV without changing its contents."""
    if not path.is_file():
        raise RainfallPipelineError(f"Settlement CSV was not found: {path}")
    try:
        return validate_settlements(pd.read_csv(path))
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise RainfallPipelineError(f"Unable to read settlement CSV '{path}': {error}") from error


def validate_imd_dataset(dataset: xr.Dataset, expected_year: int = 2024) -> None:
    """Validate the expected IMD daily rainfall structure and coordinate domain."""
    if RAINFALL_VARIABLE not in dataset.data_vars:
        raise RainfallPipelineError(f"NetCDF is missing required variable '{RAINFALL_VARIABLE}'.")
    missing = [name for name in REQUIRED_COORDINATES if name not in dataset.coords]
    if missing:
        raise RainfallPipelineError("NetCDF is missing required coordinates: " + ", ".join(missing))

    rainfall = dataset[RAINFALL_VARIABLE]
    expected_dimensions = set(REQUIRED_COORDINATES)
    if set(rainfall.dims) != expected_dimensions:
        raise RainfallPipelineError(
            f"'{RAINFALL_VARIABLE}' must use dimensions {sorted(expected_dimensions)}; "
            f"received {list(rainfall.dims)}."
        )
    if str(rainfall.attrs.get("units", "")).strip().lower() != "mm":
        raise RainfallPipelineError("IMD rainfall units must be 'mm'.")

    time = pd.DatetimeIndex(pd.to_datetime(dataset["TIME"].values))
    if time.empty or time.isna().any() or time.has_duplicates or not time.is_monotonic_increasing:
        raise RainfallPipelineError("TIME coordinate must contain unique, increasing valid dates.")
    expected_days = pd.date_range(f"{expected_year}-01-01", f"{expected_year}-12-31", freq="D")
    if not expected_days.isin(time).all():
        raise RainfallPipelineError(f"TIME coordinate does not cover every calendar day of {expected_year}.")

    for name, lower, upper in (("LATITUDE", -90.0, 90.0), ("LONGITUDE", -180.0, 180.0)):
        values = np.asarray(dataset[name].values, dtype=float)
        if values.size == 0 or not np.isfinite(values).all():
            raise RainfallPipelineError(f"{name} coordinate must contain finite numeric values.")
        if not np.all(np.diff(values) > 0):
            raise RainfallPipelineError(f"{name} coordinate must be strictly increasing.")
        if not ((values >= lower) & (values <= upper)).all():
            raise RainfallPipelineError(f"{name} coordinate values are outside valid geographic bounds.")


def open_and_validate_imd_dataset(path: Path, expected_year: int = 2024) -> xr.Dataset:
    """Open a local IMD NetCDF file and validate it; callers must close the result."""
    if not path.is_file():
        raise RainfallPipelineError(f"IMD rainfall NetCDF was not found: {path}")
    try:
        dataset = xr.open_dataset(path)
    except (OSError, ValueError) as error:
        raise RainfallPipelineError(f"Unable to open IMD rainfall NetCDF '{path}': {error}") from error
    try:
        validate_imd_dataset(dataset, expected_year)
    except Exception:
        dataset.close()
        raise
    return dataset


def _validate_coverage(settlements: pd.DataFrame, dataset: xr.Dataset) -> None:
    """Reject settlements outside the available IMD coordinate domain before selection."""
    latitudes = dataset["LATITUDE"].values
    longitudes = dataset["LONGITUDE"].values
    for settlement in settlements.itertuples(index=False):
        if not (latitudes.min() <= settlement.latitude <= latitudes.max()):
            raise RainfallPipelineError(
                f"Settlement '{settlement.settlement_id}' is outside IMD latitude coverage."
            )
        if not (longitudes.min() <= settlement.longitude <= longitudes.max()):
            raise RainfallPipelineError(
                f"Settlement '{settlement.settlement_id}' is outside IMD longitude coverage."
            )


def extract_rainfall_features(dataset: xr.Dataset, settlements: pd.DataFrame, expected_year: int = 2024) -> pd.DataFrame:
    """Select each point's nearest grid cell and calculate calendar-day rolling rainfall.

    Rolling 3- and 7-day values require all days in their respective calendar window.
    Thus, the first 2/6 days and any window containing missing IMD rainfall remain missing.
    """
    validate_imd_dataset(dataset, expected_year)
    settlements = validate_settlements(settlements)
    _validate_coverage(settlements, dataset)
    feature_frames: list[pd.DataFrame] = []

    for settlement in settlements.itertuples(index=False):
        selected = dataset[RAINFALL_VARIABLE].sel(
            LATITUDE=settlement.latitude,
            LONGITUDE=settlement.longitude,
            method="nearest",
        )
        values = np.asarray(selected.values, dtype=float)
        dates = pd.to_datetime(selected["TIME"].values)
        frame = pd.DataFrame(
            {
                "settlement_id": settlement.settlement_id,
                "settlement_name": settlement.settlement_name,
                "latitude": settlement.latitude,
                "longitude": settlement.longitude,
                "region": settlement.region,
                "district": settlement.district,
                "date": dates,
                "rainfall_1d_mm": values,
                "imd_grid_latitude": float(selected["LATITUDE"].item()),
                "imd_grid_longitude": float(selected["LONGITUDE"].item()),
            }
        )
        frame["rainfall_3d_mm"] = frame["rainfall_1d_mm"].rolling(3, min_periods=3).sum()
        frame["rainfall_7d_mm"] = frame["rainfall_1d_mm"].rolling(7, min_periods=7).sum()
        feature_frames.append(frame.loc[:, OUTPUT_COLUMNS])

    return pd.concat(feature_frames, ignore_index=True)


def build_rainfall_features(netcdf_path: Path, settlements_path: Path, expected_year: int = 2024) -> pd.DataFrame:
    """Load real IMD rainfall and a settlement CSV, returning derived observations."""
    settlements = load_settlements(settlements_path)
    dataset = open_and_validate_imd_dataset(netcdf_path, expected_year)
    try:
        return extract_rainfall_features(dataset, settlements, expected_year)
    finally:
        dataset.close()


def build_historical_rainfall_features(netcdf_by_year: Mapping[int, Path], settlements_path: Path) -> pd.DataFrame:
    """Apply the unchanged rainfall method independently to approved calendar years.

    Each year starts a new rolling window: prior-year rainfall is neither assumed nor
    carried into the first 3-/7-day values of the next source file.
    """
    if not netcdf_by_year:
        raise RainfallPipelineError("At least one IMD year/file mapping is required.")
    settlements = load_settlements(settlements_path)
    frames: list[pd.DataFrame] = []
    for year, path in sorted(netcdf_by_year.items()):
        dataset = open_and_validate_imd_dataset(path, int(year))
        try:
            frames.append(extract_rainfall_features(dataset, settlements, int(year)))
        finally:
            dataset.close()
    result = pd.concat(frames, ignore_index=True)
    if result.duplicated(["settlement_id", "date"]).any():
        raise RainfallPipelineError("Historical rainfall inputs produced duplicate settlement-date rows.")
    return result.sort_values(["settlement_id", "date"], kind="stable").reset_index(drop=True)


def write_rainfall_features(features: pd.DataFrame, output_path: Path) -> None:
    """Write the derived feature table without modifying source inputs."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False, date_format="%Y-%m-%d")
