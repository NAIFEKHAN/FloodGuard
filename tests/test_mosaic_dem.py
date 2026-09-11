"""Offline tests for DEM mosaic validation using synthetic TEST FIXTURE rasters only."""

from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from pipeline.terrain.mosaic_dem import DemMosaicError, create_dem_mosaic, validate_compatible_tiles


def write_test_fixture_tile(
    path: Path, *, west: float, crs: str = "EPSG:4326", nodata: int = -9999
) -> None:
    """Create a synthetic TEST FIXTURE tile; it is never source or DEMO terrain data."""
    values = np.array([[10, 20], [30, 40]], dtype="int16")
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=2,
        width=2,
        count=1,
        dtype="int16",
        crs=crs,
        transform=from_origin(west, 2, 1, 1),
        nodata=nodata,
    ) as fixture:
        fixture.write(values, 1)


def test_mosaics_compatible_test_fixture_tiles_without_resampling(tmp_path: Path) -> None:
    first = tmp_path / "first.tif"
    second = tmp_path / "second.tif"
    output = tmp_path / "mosaic.tif"
    write_test_fixture_tile(first, west=0)
    write_test_fixture_tile(second, west=2)

    metadata = create_dem_mosaic([first, second], output)

    assert output.is_file()
    assert metadata.crs == "EPSG:4326"
    assert metadata.resolution == (1.0, 1.0)
    assert (metadata.width, metadata.height) == (4, 2)
    assert metadata.nodata == -9999
    with rasterio.open(output) as mosaic:
        assert mosaic.read(1).tolist() == [[10, 20, 10, 20], [30, 40, 30, 40]]


def test_rejects_incompatible_tile_metadata(tmp_path: Path) -> None:
    first = tmp_path / "first.tif"
    incompatible = tmp_path / "incompatible.tif"
    write_test_fixture_tile(first, west=0)
    write_test_fixture_tile(incompatible, west=2, nodata=-32768)

    with pytest.raises(DemMosaicError, match="incompatible"):
        validate_compatible_tiles([first, incompatible])


def test_refuses_to_overwrite_existing_mosaic(tmp_path: Path) -> None:
    source = tmp_path / "source.tif"
    output = tmp_path / "existing.tif"
    write_test_fixture_tile(source, west=0)
    output.write_bytes(b"existing file")

    with pytest.raises(DemMosaicError, match="will not be overwritten"):
        create_dem_mosaic([source], output)
