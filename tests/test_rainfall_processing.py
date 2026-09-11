"""Offline rainfall tests using synthetic TEST FIXTURE NetCDF files only."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from pipeline.rainfall.processing import (
    RainfallPipelineError,
    build_historical_rainfall_features,
    build_rainfall_features,
    extract_rainfall_features,
    validate_imd_dataset,
    validate_settlements,
)


def fixture_settlements(latitude: float = 10.1, longitude: float = 76.1) -> pd.DataFrame:
    """Return TEST FIXTURE settlement rows; never production or DEMO evidence."""
    return pd.DataFrame(
        [
            {
                "settlement_id": "TEST-001",
                "settlement_name": "Test location",
                "latitude": latitude,
                "longitude": longitude,
                "region": "Test region",
                "district": "Test district",
            }
        ]
    )


def fixture_dataset(*, missing_day: int | None = None, year: int = 2024) -> xr.Dataset:
    """Return a synthetic TEST FIXTURE daily NetCDF structure for unit tests."""
    time = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")
    values = np.zeros((len(time), 2, 2), dtype=np.float32)
    values[:, 0, 0] = np.arange(1, len(time) + 1, dtype=np.float32)
    values[:, 1, 1] = np.arange(101, len(time) + 101, dtype=np.float32)
    if missing_day is not None:
        values[missing_day, 0, 0] = np.nan
    return xr.Dataset(
        {"RAINFALL": (("TIME", "LATITUDE", "LONGITUDE"), values, {"units": "mm"})},
        coords={"TIME": time, "LATITUDE": [10.0, 11.0], "LONGITUDE": [76.0, 77.0]},
    )


def test_validates_expected_imd_netcdf_structure() -> None:
    validate_imd_dataset(fixture_dataset())


def test_rejects_missing_rainfall_variable() -> None:
    dataset = fixture_dataset().drop_vars("RAINFALL")
    with pytest.raises(RainfallPipelineError, match="missing required variable"):
        validate_imd_dataset(dataset)


def test_extracts_nearest_grid_daily_and_rolling_rainfall() -> None:
    features = extract_rainfall_features(fixture_dataset(), fixture_settlements())

    assert len(features) == 366
    assert features.loc[0, "imd_grid_latitude"] == 10
    assert features.loc[0, "imd_grid_longitude"] == 76
    assert features.loc[0, "rainfall_1d_mm"] == 1
    assert pd.isna(features.loc[1, "rainfall_3d_mm"])
    assert features.loc[2, "rainfall_3d_mm"] == 6
    assert pd.isna(features.loc[5, "rainfall_7d_mm"])
    assert features.loc[6, "rainfall_7d_mm"] == 28


def test_nearest_grid_selection_can_choose_upper_coordinate() -> None:
    features = extract_rainfall_features(fixture_dataset(), fixture_settlements(10.9, 76.9))

    assert features.loc[0, "imd_grid_latitude"] == 11
    assert features.loc[0, "imd_grid_longitude"] == 77
    assert features.loc[0, "rainfall_1d_mm"] == 101


def test_missing_daily_rainfall_is_not_filled() -> None:
    features = extract_rainfall_features(fixture_dataset(missing_day=3), fixture_settlements())

    assert pd.isna(features.loc[3, "rainfall_1d_mm"])
    assert pd.isna(features.loc[3, "rainfall_3d_mm"])
    assert pd.isna(features.loc[3, "rainfall_7d_mm"])


def test_rejects_invalid_or_outside_settlement_coordinates() -> None:
    invalid = fixture_settlements(latitude=95)
    with pytest.raises(RainfallPipelineError, match="between -90 and 90"):
        validate_settlements(invalid)

    outside = fixture_settlements(latitude=12)
    with pytest.raises(RainfallPipelineError, match="outside IMD latitude coverage"):
        extract_rainfall_features(fixture_dataset(), outside)


def test_build_from_test_fixture_netcdf_file(tmp_path: Path) -> None:
    netcdf_path = tmp_path / "test_fixture_imd.nc"
    settlements_path = tmp_path / "settlements.csv"
    fixture_dataset().to_netcdf(netcdf_path)
    fixture_settlements().to_csv(settlements_path, index=False)

    features = build_rainfall_features(netcdf_path, settlements_path)

    assert len(features) == 366
    assert list(features.columns) == [
        "settlement_id", "settlement_name", "latitude", "longitude", "region", "district",
        "date", "rainfall_1d_mm", "rainfall_3d_mm", "rainfall_7d_mm",
        "imd_grid_latitude", "imd_grid_longitude",
    ]


def test_historical_processing_parameterizes_year_and_resets_rolling_windows(tmp_path: Path) -> None:
    settlements_path = tmp_path / "settlements.csv"
    first_path = tmp_path / "imd_2023.nc"
    second_path = tmp_path / "imd_2024.nc"
    fixture_settlements().to_csv(settlements_path, index=False)
    fixture_dataset(year=2023).to_netcdf(first_path)
    fixture_dataset(year=2024).to_netcdf(second_path)

    features = build_historical_rainfall_features({2023: first_path, 2024: second_path}, settlements_path)

    assert len(features) == 365 + 366
    assert features["date"].min() == pd.Timestamp("2023-01-01")
    assert features["date"].max() == pd.Timestamp("2024-12-31")
    first_2024 = features.loc[features["date"] == pd.Timestamp("2024-01-01")].iloc[0]
    assert pd.isna(first_2024["rainfall_3d_mm"])
    assert pd.isna(first_2024["rainfall_7d_mm"])
