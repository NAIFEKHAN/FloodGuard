"""Offline tests using explicitly synthetic TEST FIXTURE rasters only."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import from_origin

from pipeline.terrain.processing import (
    TerrainPipelineError,
    build_terrain_features,
    read_dem_metadata,
    validate_settlements,
)


def write_test_fixture_dem(path: Path, *, crs: str = "EPSG:4326") -> None:
    """Create a synthetic TEST FIXTURE raster; never a production or DEMO data source."""
    values = np.array(
        [[100.0, 110.0, 120.0], [100.0, 110.0, 120.0], [100.0, 110.0, 120.0]],
        dtype="int16",
    )
    transform = (
        from_origin(0, 3, 1, 1)
        if crs == "EPSG:4326"
        else from_origin(0, 3000, 1000, 1000)
    )
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=3,
        width=3,
        count=1,
        dtype="float32",
        crs=crs,
        transform=transform,
        nodata=-9999,
    ) as fixture:
        fixture.write(values.astype("int16"), 1)


def write_settlements(path: Path, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def test_settlement_validation_rejects_missing_required_column() -> None:
    with pytest.raises(TerrainPipelineError, match="missing required columns"):
        validate_settlements(pd.DataFrame({"settlement_id": ["one"]}))


def test_dem_metadata_is_read_from_test_fixture(tmp_path: Path) -> None:
    dem_path = tmp_path / "test_fixture_dem.tif"
    write_test_fixture_dem(dem_path)

    metadata = read_dem_metadata(dem_path)

    assert metadata.crs == "EPSG:4326"
    assert metadata.resolution_x == 1
    assert metadata.resolution_y == 1
    assert metadata.nodata == -9999
    assert (metadata.width, metadata.height) == (3, 3)


def test_extracts_elevation_and_degree_slope_structure(tmp_path: Path) -> None:
    dem_path = tmp_path / "test_fixture_dem.tif"
    settlements_path = tmp_path / "settlements.csv"
    write_test_fixture_dem(dem_path)
    write_settlements(
        settlements_path,
        [
            {
                "settlement_id": "TEST-001",
                "settlement_name": "Test point",
                "latitude": 1.5,
                "longitude": 1.5,
                "region": "Test region",
                "district": "Test district",
            }
        ],
    )

    features = build_terrain_features(dem_path, settlements_path)

    assert list(features.columns) == [
        "settlement_id",
        "settlement_name",
        "latitude",
        "longitude",
        "region",
        "district",
        "elevation_m",
        "slope_deg",
    ]
    assert features.loc[0, "elevation_m"] == 110
    assert 0 < features.loc[0, "slope_deg"] < 90


def test_transforms_wgs84_points_to_projected_dem_crs(tmp_path: Path) -> None:
    dem_path = tmp_path / "projected_test_fixture_dem.tif"
    settlements_path = tmp_path / "settlements.csv"
    write_test_fixture_dem(dem_path, crs="EPSG:3857")
    # EPSG:3857 coordinates (1500 m, 1500 m) converted to WGS84 for the input CSV.
    longitude = 1500 / 111_319.49079327357
    latitude = np.degrees(np.arctan(np.sinh(1500 / 6_378_137.0)))
    write_settlements(
        settlements_path,
        [
            {
                "settlement_id": "TEST-3857",
                "settlement_name": "Projected test point",
                "latitude": latitude,
                "longitude": longitude,
                "region": "Test region",
                "district": "Test district",
            }
        ],
    )

    features = build_terrain_features(dem_path, settlements_path)

    assert features.loc[0, "elevation_m"] == 110
