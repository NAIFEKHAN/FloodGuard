"""Create a DEM mosaic from compatible local GeoTIFF source tiles."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path

import rasterio
from rasterio.merge import merge


class DemMosaicError(ValueError):
    """Raised when DEM tiles cannot safely be mosaicked without alteration."""


@dataclass(frozen=True)
class TileMetadata:
    """Metadata required to verify a DEM tile is compatible with its peers."""

    path: Path
    crs: str
    resolution: tuple[float, float]
    width: int
    height: int
    count: int
    dtype: str
    nodata: float | None
    bounds: tuple[float, float, float, float]


def read_tile_metadata(path: Path) -> TileMetadata:
    """Read the metadata needed for compatibility checks from one GeoTIFF."""
    if not path.is_file():
        raise DemMosaicError(f"DEM tile was not found: {path}")
    try:
        with rasterio.open(path) as dataset:
            if dataset.crs is None:
                raise DemMosaicError(f"DEM tile has no CRS: {path}")
            if dataset.count != 1:
                raise DemMosaicError(
                    f"DEM tile must be single-band for this pipeline: {path} has {dataset.count} bands."
                )
            if dataset.width < 2 or dataset.height < 2:
                raise DemMosaicError(f"DEM tile is too small to be a valid terrain raster: {path}")
            return TileMetadata(
                path=path,
                crs=dataset.crs.to_string(),
                resolution=dataset.res,
                width=dataset.width,
                height=dataset.height,
                count=dataset.count,
                dtype=dataset.dtypes[0],
                nodata=dataset.nodata,
                bounds=(dataset.bounds.left, dataset.bounds.bottom, dataset.bounds.right, dataset.bounds.top),
            )
    except DemMosaicError:
        raise
    except rasterio.errors.RasterioError as error:
        raise DemMosaicError(f"Unable to open DEM tile '{path}': {error}") from error


def validate_compatible_tiles(paths: list[Path]) -> list[TileMetadata]:
    """Confirm tiles share CRS, resolution, band type, and nodata representation."""
    if not paths:
        raise DemMosaicError("No GeoTIFF DEM tiles were found.")
    metadata = [read_tile_metadata(path) for path in paths]
    reference = metadata[0]
    for tile in metadata[1:]:
        differences: list[str] = []
        for attribute in ("crs", "resolution", "count", "dtype", "nodata"):
            if getattr(tile, attribute) != getattr(reference, attribute):
                differences.append(
                    f"{attribute} ({getattr(tile, attribute)!r} != {getattr(reference, attribute)!r})"
                )
        if differences:
            raise DemMosaicError(
                f"DEM tile '{tile.path.name}' is incompatible with '{reference.path.name}': "
                + ", ".join(differences)
            )
    return metadata


def find_dem_tiles(input_dir: Path, pattern: str = "*.tif") -> list[Path]:
    """Return a deterministic list of GeoTIFF inputs from a directory."""
    if not input_dir.is_dir():
        raise DemMosaicError(f"DEM input directory was not found: {input_dir}")
    tiles = sorted(path for path in input_dir.glob(pattern) if path.is_file())
    if not tiles:
        raise DemMosaicError(f"No DEM files matching '{pattern}' were found in: {input_dir}")
    return tiles


def create_dem_mosaic(input_tiles: list[Path], output_path: Path) -> TileMetadata:
    """Mosaic compatible tiles without resampling and write a derived GeoTIFF."""
    metadata = validate_compatible_tiles(input_tiles)
    if output_path.exists():
        raise DemMosaicError(
            f"Output already exists and will not be overwritten automatically: {output_path}"
        )

    try:
        with ExitStack() as stack:
            datasets = [stack.enter_context(rasterio.open(path)) for path in input_tiles]
            mosaic, transform = merge(datasets, nodata=metadata[0].nodata, method="first")
            profile = datasets[0].profile.copy()

        profile.update(
            height=mosaic.shape[1],
            width=mosaic.shape[2],
            transform=transform,
            count=1,
            nodata=metadata[0].nodata,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(output_path, "w", **profile) as destination:
            destination.write(mosaic)
    except rasterio.errors.RasterioError as error:
        raise DemMosaicError(f"Unable to create DEM mosaic '{output_path}': {error}") from error

    return read_tile_metadata(output_path)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line configuration without region-specific assumptions."""
    parser = argparse.ArgumentParser(description="Mosaic compatible local DEM GeoTIFF tiles.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing input DEM GeoTIFF tiles.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path for the derived mosaic GeoTIFF; existing files are never overwritten.",
    )
    parser.add_argument(
        "--pattern",
        default="*.tif",
        help="Input filename pattern (default: *.tif).",
    )
    return parser.parse_args()


def main() -> int:
    """Create a mosaic and print its metadata for reproducible verification."""
    arguments = parse_arguments()
    try:
        tiles = find_dem_tiles(arguments.input_dir, arguments.pattern)
        mosaic = create_dem_mosaic(tiles, arguments.output)
    except DemMosaicError as error:
        print(f"DEM mosaic failed: {error}")
        return 1

    print(f"Mosaicked {len(tiles)} tile(s) into: {mosaic.path}")
    print(f"CRS: {mosaic.crs}")
    print(f"Resolution: {mosaic.resolution}")
    print(f"Dimensions: {mosaic.width} x {mosaic.height}")
    print(f"Bounds: {mosaic.bounds}")
    print(f"Nodata: {mosaic.nodata}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
