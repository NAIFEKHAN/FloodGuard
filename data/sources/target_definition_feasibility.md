# Phase 3 target definition and evidence-linkage feasibility audit

**Artifact class:** feasibility/audit documentation only. This is **not** a modelling dataset, target table, event label table, prediction, score, or warning product.

**Audit scope:** existing local FloodGuard artifacts were inspected without changing raw data. No events were geocoded, assigned to settlements, distance-matched, date-inferred, or converted into non-event observations. No modelling units, labels, risk scores, or ML models were created.

## Local spatial-data inventory

The project contains:

- Four real SRTM GL1 tiles and the real-derived `data/processed/dem_nilgiris_mosaic.tif` (EPSG:4326; bounds 75.99986111111112 to 78.0001388888889 longitude and 9.999861111111112 to 12.00013888888889 latitude; 1 arc-second grid).
- The real IMD 2024 NetCDF, with daily latitude/longitude coordinate arrays (6.5 to 38.5 latitude and 66.5 to 100.0 longitude) and a 0.25-degree grid.
- `terrain_features.csv` and `settlement_daily_features.csv`, each based only on the two locations in `data/demo/settlements_demo.csv`.
- The 772-row real GSI/NLFC Nilgiri landslide inventory, with source-provided latitude and longitude columns.

The project does **not** contain an official settlement dataset, village/ward/taluk/district boundary vector layer, GeoJSON, GeoPackage, shapefile component set, administrative-code lookup, or spatial metadata describing an administrative geometry. `data/raw/settlements/` is empty. The two DEMO settlement points are explicitly excluded from modelling units and labels.

The DEM is a raster measurement grid, not an authoritative administrative-unit layer. The IMD coordinate grid is an authoritative rainfall observation grid, but no local polygon/cell-boundary product or approved unit design is present. Therefore neither is adopted as a target unit in this phase.

## Event-evidence audit

Source audited: `data/processed/landslide_events.csv`. Counts use the existing pipeline's conservative `history_category` rules.

| Measure | Result |
| --- | ---: |
| Total source records | 772 |
| Explicit, unambiguous dates | 382 |
| Year-only history | 5 |
| Ambiguous history | 30 |
| `NA` history | 355 |
| Records with invalid or missing coordinates | 0 |
| Latitude extent | 11.210556 to 11.550000 |
| Longitude extent | 76.24763889 to 76.95066827 |
| Coordinate groups with more than one record | 19 |
| Records in those repeated-coordinate groups | 45 |
| Largest repeated-coordinate group | 5 records |
| Explicit-date range | 2017-09-10 to 2026-01-12 |

Repeated coordinates are reported as source-coordinate co-location only; they are not deduplicated and do not establish duplicate events.

Explicit source dates by year:

| Year | Records |
| --- | ---: |
| 2017 | 4 |
| 2019 | 83 |
| 2022 | 34 |
| 2023 | 182 |
| 2024 | 9 |
| 2025 | 59 |
| 2026 | 11 |

The nine explicitly dated 2024 records occur on six source dates: 2024-06-26, 2024-07-03, 2024-07-16, 2024-07-19, 2024-07-30, and 2024-08-29. `NA`, year-only, and ambiguous History values are unknown temporal evidence; none is interpreted as a non-event or assigned a date.

## Spatial feasibility decision

All 772 source coordinates fall within the SRTM mosaic **if** they are interpreted as EPSG:4326 geographic coordinates, as the existing pipeline does. However, the supplied PDF provenance does not document a coordinate reference system or datum. This is insufficient to make a new event-to-unit linkage defensible without confirming the coordinate reference/datum from the data provider or authoritative metadata.

There is no legitimate local administrative polygon layer for point-in-polygon allocation. The only local candidate point units are the two DEMO settlements, which are prohibited from use. A nearest settlement, nearest cell centre, or distance threshold would be an arbitrary association and is not permitted.

An IMD rainfall-grid-cell design is a possible future candidate only after a written unit specification establishes the actual cell geometry, coordinate reference/datum, edge convention, event-point assignment rule, terrain aggregation method, and suitability of its roughly 0.25-degree scale for a landslide question. It is not adopted here. Likewise, DEM pixels are not an appropriate default event target unit: they are measurement pixels, do not supply an observational non-event process, and would create extreme class imbalance without a validated study design.

## Temporal feasibility decision

The local IMD series is complete only for 2024. It can be paired, in principle, only with the nine explicit 2024 source records—and only after the spatial-unit and event-coordinate-reference issues are resolved. It cannot be used to label the 373 explicitly dated records outside 2024, and it cannot provide dates for the remaining 390 records without defensible dates.

Nine records on six days are not sufficient temporal event evidence for a supervised training target, especially because the project has no verified observation/monitoring frame establishing that other unit-days are true non-events. Rainfall availability alone does not establish negative labels. The leading nulls in existing 3-day and 7-day rainfall features must remain missing; they are not to be filled.

## Required real data before target-dataset design

### 1. Authoritative spatial-unit geometry and identifiers

**Preferred source:** Survey of India (SoI) Village Boundary Database for Tamil Nadu/Nilgiris, or SoI state administrative boundaries up to taluk level if the approved modelling question supports that coarser unit. SoI documents both village-level and taluk-level administrative boundary products and identifies SoI digital boundaries as the standard for political/administrative boundaries. See [SoI Administrative Boundary Data Base](https://surveyofindia.gov.in/pages/administrative-boundary-data-base-abdb-) and the [SoI Online Maps Portal product description](https://onlinemaps.surveyofindia.gov.in/AboutPortal.aspx).

**Minimum fields:** stable unit ID/code; unit name; unit type; parent district and taluk/sub-district codes/names; valid geometry (polygon or multipolygon); CRS and datum; source/version/publication date; licence; and validity period or boundary vintage.

**Use:** after validation, source event points may be assigned by a documented point-in-polygon operation, never proximity. This creates a reproducible spatial unit only if the event coordinate reference/datum is confirmed compatible. A versioned boundary layer also permits terrain aggregation within the same polygons.

### 2. Authoritative event metadata sufficient for supervised outcomes

**Preferred source:** a corrected/complete GSI/NLFC inventory release or written provider metadata for the supplied inventory.

**Minimum fields:** stable event ID; source coordinate CRS/datum; event latitude/longitude or authoritative geometry; occurrence date (ISO day, or documented precision); reporting/observation date if distinct; event-type definition; provenance/version; and documented geographic/temporal coverage and completeness.

**Use:** retain only records whose date precision supports the proposed unit-day (or explicitly coarsened unit-period) outcome. Confirming CRS/datum is necessary before any spatial overlay. Missing dates remain unknown, rather than negative.

### 3. Rainfall and observation coverage for the selected study period

**Preferred source:** IMD daily gridded rainfall for every date in the approved event study period, with version, units, coordinate arrays/CRS, missing-value convention, and provenance retained.

**Minimum fields:** daily date; grid coordinates or grid geometry; rainfall value and units; missing-data flags; dataset version; and coverage metadata. A defensible target also requires a documented event-observation/completeness frame for the selected units and dates, so unrecorded unit-days are not silently asserted to be non-events.

**Use:** compute antecedent rainfall only from observed daily values for dated events and comparable, demonstrably observed unit-days. Align rainfall cells to the approved modelling unit with a documented spatial aggregation method.

## Research-quality outcome

**Outcome: 2. ADDITIONAL REAL DATA REQUIRED.**

The project has real terrain, rainfall, and event evidence, but no approved authoritative modelling-unit geometry, no independently documented event coordinate reference/datum, no adequate multi-year rainfall overlap, and no verified non-event observation frame. Therefore **ML is currently not allowed**. This outcome is not a conclusion that unknown records are negative or that a future target is impossible; it identifies the real evidence required before target-dataset design can be approved.
