# Terrain data provenance and processing

## Current status

Four real SRTM GL1 source tiles have been supplied locally. The derived mosaic `data/processed/dem_nilgiris_mosaic.tif` is created from those tiles without resampling or clipping.

`data/processed/terrain_features.csv` is a **DERIVED DATA** feature table generated from that real SRTM mosaic for the two points in `data/demo/settlements_demo.csv`. Its `elevation_m` and `slope_deg` values are derived from real SRTM elevations; only the settlement input locations are DEMO data.

## Intended source

The source dataset is the Shuttle Radar Topography Mission **SRTM GL1** DEM. The supplied source location is OpenTopography's public S3 distribution: `s3://raster/SRTM_GL1/SRTM_GL1_srtm/`, accessed through `https://opentopography.s3.sdsc.edu`. The pipeline does not download data or bypass any authentication requirement.

The real source tiles supplied for the Nilgiris demonstration coverage are:

- `N10E076.tif`
- `N10E077.tif`
- `N11E076.tif`
- `N11E077.tif`

They are preserved unchanged in `data/raw/dem/`. The mosaic is a **DERIVED DATA** product, not a new source dataset.

## Mosaic processing

Run the reusable command from the repository root in PowerShell:

```powershell
python pipeline/terrain/mosaic_dem.py --input-dir data/raw/dem --output data/processed/dem_nilgiris_mosaic.tif
```

The command validates that each input is a readable single-band GeoTIFF with matching CRS, resolution, data type, and nodata value. It uses `rasterio.merge.merge` with the native source grid and `method="first"`; no resampling or clipping occurs. Nodata is preserved. Existing output files are not overwritten automatically.

## Expected inputs

- **DEM:** a readable, single-band GeoTIFF elevation raster. For multi-tile coverage, first generate a derived mosaic with `mosaic_dem.py`, then pass its path to the terrain extractor. A DEM must have a CRS, dimensions of at least 2 × 2, and documented source, acquisition/version, licence, CRS, resolution, and nodata value.
- **Settlements:** a verified CSV at `data/raw/settlements/settlements.csv` by default with `settlement_id`, `settlement_name`, `latitude`, `longitude`, `region`, and `district`. Coordinates are WGS84 (EPSG:4326).

Paths can be overridden with `python pipeline/build_terrain.py --dem <path> --settlements <path>`.

## CRS and resolution

Settlement points are transformed from EPSG:4326 into the DEM CRS before sampling. Projected DEMs must use metre-based linear units. Geographic DEMs are supported by converting degree resolution to approximate metres at each raster row; for high-precision analysis, use an appropriate local projected DEM/CRS.

## Derived features

The output `data/processed/terrain_features.csv` contains the validated settlement columns plus:

- `elevation_m` — band-1 elevation sampled at the settlement's DEM pixel. Units are assumed to be metres only when the selected DEM's provenance documents that vertical unit.
- `slope_deg` — slope in **degrees**, calculated from neighbouring DEM elevation pixels using horizontal pixel dimensions in metres: `atan(sqrt((dz/dx)^2 + (dz/dy)^2))`.

For the current demonstration extraction, the pipeline reads the real mosaic at each DEMO settlement coordinate, samples the corresponding elevation pixel, and associates the DEM-calculated slope in degrees. It does not create, interpolate, or substitute terrain values for missing data.

No elevation or slope values are manufactured. Coordinates outside raster coverage, nodata elevation, or nodata-affected slope values cause the pipeline to stop with an error.

## Limitations

Pixel sampling is not a substitute for village/ward boundary statistics. Resolution, vertical datum, voids/nodata, and DEM source quality affect results. This Phase 1A pipeline derives only elevation and slope; it does not process rainfall, events, predictions, or warnings.
