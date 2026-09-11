# Rainfall data provenance and processing

## Current source data

`data/raw/rainfall/RF25_ind2024_rfp25.nc` is **REAL DATA**: the IMD 0.25° daily gridded rainfall NetCDF dataset for 2024. It is an unchanged source input and is never overwritten by this pipeline.

- Dataset file: `RF25_ind2024_rfp25.nc`
- Provider: India Meteorological Department (IMD), Climate Research and Services, Pune
- Format: NetCDF
- Variable: `RAINFALL`
- Units: millimetres (`mm`)
- Coordinates: `TIME`, `LATITUDE`, `LONGITUDE`
- Time span: 2024-01-01 through 2024-12-31 (daily; 366 observations)
- Spatial grid: 0.25° latitude/longitude (approximately 25 km; actual ground distance varies by latitude)

## DEMO settlement input

`data/demo/settlements_demo.csv` contains exactly two **DEMO** locations. They are not official villages/wards and are not a complete Nilgiris settlement list. The pipeline does not create or add settlement locations.

## Extraction method

For each input settlement, the pipeline first verifies that its WGS84 latitude/longitude is within the IMD grid domain. It then uses xarray nearest-neighbour coordinate selection (`.sel(..., method="nearest")`) independently for latitude and longitude. The selected `imd_grid_latitude` and `imd_grid_longitude` are recorded for traceability.

The output `data/processed/rainfall_features.csv` is **DERIVED DATA**. Its daily rainfall values are selected directly from the real IMD `RAINFALL` variable; no values are generated, substituted, or obtained from another weather source.

## Derived rainfall features

- `rainfall_1d_mm`: IMD rainfall for the selected cell on that calendar date, in mm.
- `rainfall_3d_mm`: trailing three-calendar-day total, including the current date, in mm.
- `rainfall_7d_mm`: trailing seven-calendar-day total, including the current date, in mm.

Rolling totals use `min_periods` equal to the window length. The first two days for the 3-day total and first six days for the 7-day total are therefore missing. If any source daily value is missing, all rolling windows containing it remain missing; the pipeline does not fill missing data.

## Limitations

The 0.25° grid is much coarser than village/ward scale. Nearest-cell assignment is a transparent first-stage association, not a claim that rainfall was measured at the DEMO location. This pipeline processes historical 2024 IMD data only; it is not live rainfall and does not create predictions or warnings.
