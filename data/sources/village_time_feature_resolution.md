# Village-time feature resolution

**Phase:** 6E — feature table only  
**Status:** completed restricted feature artifact; no target or model was created.

## Scope and resolution

`data/processed/village_time_features.csv` contains daily feature observations for exactly the **40** Nilgiris village polygons whose KMZ `vlcode`, `dtcode`, and `sdcode` agree exactly with the validated Village Master LGD identifiers. It contains no event identifier, event count, target, negative class, risk score, prediction, or ML output.

The table joins these inputs only:

- the 40 exact-ID polygons in `data/raw/admin/vb_soi_tn.kmz`, with administrative identifiers/names from `data/processed/nilgiris_villages.csv`;
- terrain summaries in `data/processed/terrain_features_villages.csv`;
- daily IMD `RAINFALL` values from `data/raw/rainfall/RF25_ind2017_rfp25.nc`, `RF25_ind2019_rfp25.nc`, `RF25_ind2022_rfp25.nc`, `RF25_ind2023_rfp25.nc`, and `RF25_ind2024_rfp25.nc`.

For each validated polygon, a Shapely interior representative point was calculated from that same polygon. The nearest IMD 0.25-degree grid cell to that point supplies the daily value and recorded grid coordinates. This is an IMD-grid association, not a nearest-village, nearest-event, name, fuzzy, or spatial-linkage procedure. Seven distinct IMD cells are represented. The rolling sums are trailing calendar-day sums and restart for every source year. No rainfall or terrain value was imputed.

The source/provenance columns in every row retain the year-specific rainfall file, the association method, the terrain artifact, and the validated-polygon source. Existing IMD file hashes and grid metadata are recorded in `data/processed/historical_rainfall_provenance.json`; the prior historical DEMO table was not used as a village substitute.

## Reproduction

Run from the repository root:

```powershell
python pipeline/build_village_time_features.py
```

The builder validates the exact 40-polygon population, terrain-ID alignment, per-year calendar coverage, one row per village/date, daily-rainfall completeness, leading rolling-null counts, and constant terrain values within each village. It writes only the derived Phase 6E output.

## Validation results

| Check | Result |
| --- | ---: |
| Villages | 40 |
| Total village-date rows | 73,040 |
| Duplicate village/date rows | 0 |
| Missing administrative, IMD-grid, terrain, or provenance values | 0 |
| Distinct selected IMD grid cells | 7 |
| Missing daily rainfall values | 0 |
| Rolling 3-day nulls | 400 |
| Rolling 7-day nulls | 1,200 |

| Year | Date coverage | Rows | Rows per date | 3-day nulls | 7-day nulls |
| --- | --- | ---: | ---: | ---: | ---: |
| 2017 | 2017-01-01 to 2017-12-31 | 14,600 | 40 | 80 | 240 |
| 2019 | 2019-01-01 to 2019-12-31 | 14,600 | 40 | 80 | 240 |
| 2022 | 2022-01-01 to 2022-12-31 | 14,600 | 40 | 80 | 240 |
| 2023 | 2023-01-01 to 2023-12-31 | 14,600 | 40 | 80 | 240 |
| 2024 | 2024-01-01 to 2024-12-31 | 14,640 | 40 | 80 | 240 |

The 400 and 1,200 rolling nulls are expected and intentionally preserved: respectively the first two and first six dates for each of 40 villages in each of five independently processed years. They are not missing-data fixes or imputed values.

## Event coverage audit only

Phase 6D's conditional exact-containment linkage was consulted only to describe future temporal feasibility. Its already-extracted explicitly dated linked records within this table's source years are: 2017: 2, 2019: 36, 2022: 15, 2023: 56, and 2024: 4. This information is not present in the feature CSV and did not affect any row, rainfall value, or feature selection. The linkage remains conditional on the limitations documented in `event_village_linkage_resolution.md`; it must not be converted to a target at this phase.

## Boundaries

This artifact is a restricted, real-data feature table for the validated 40-polygon subset, not a complete Nilgiris village universe. It does not establish event-coordinate certainty, observation completeness, non-events, a target, or a basis for ML. Raw files were not modified.
