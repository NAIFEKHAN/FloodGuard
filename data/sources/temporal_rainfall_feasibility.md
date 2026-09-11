# Temporal rainfall feasibility audit

**Artifact class:** scientific feasibility audit only. No label, target, prediction, score, synthetic negative sample, or modelling dataset was created.

## Inputs and method

- `data/processed/landslide_events.csv`: 772 supplied GSI/NLFC records. Only the already-populated, unambiguous ISO `reported_history_date` field was used.
- `data/raw/rainfall/RF25_ind2024_rfp25.nc`: the sole locally present IMD NetCDF source.
- `data/processed/rainfall_features.csv`: existing 2024 feature output, inspected but not altered.

The date test did not turn a year-only, ambiguous, or `NA` history into a date. For the locally overlapping 2024 events only, the event coordinate was evaluated against the existing rainfall pipeline’s documented grid selection: xarray nearest-cell selection independently on WGS84-interpreted `LATITUDE` and `LONGITUDE`, followed by extraction on the exact reported date. This is a feasibility check only, not a final event/rainfall or event/village linkage; it uses no station, interpolation, alternative source, missing-value substitution, or coordinate adjustment.

## Current rainfall source and processing

| Item | Finding |
| --- | --- |
| Local source file | `RF25_ind2024_rfp25.nc` (25,501,532 bytes) |
| Local date coverage | 2024-01-01 through 2024-12-31; 366 daily steps |
| Variable / units | `RAINFALL`, `float32`, `mm` |
| Dimensions | `TIME` × `LATITUDE` × `LONGITUDE` = 366 × 129 × 135 |
| Grid coordinates | Latitude 6.5–38.5; longitude 66.5–100.0; 0.25° increments |
| Missing-value rule | Existing processing retains source missing values; trailing 3-/7-day totals remain missing until their full calendar window is present and no values are filled. |

`rainfall_features.csv` has 732 rows because the existing, unchanged pipeline selected nearest IMD grid cells for two **DEMO** settlement coordinates for each 2024 date and calculated direct 1-day and trailing 3-/7-day totals. It is not a village/event modelling table. The source NetCDF contains missing cells; no missing value was invented. For every locally overlapping 2024 event below, the selected same-day grid value was finite.

## Explicit event-date audit

| Year | Explicit events | Unique explicit event dates |
| --- | ---: | ---: |
| 2017 | 4 | 2 |
| 2019 | 83 | 5 |
| 2022 | 34 | 5 |
| 2023 | 182 | 1 |
| 2024 | 9 | 6 |
| 2025 | 59 | 11 |
| 2026 | 11 | 2 |
| **Total** | **382** | **32** |

The explicit date range is 2017-09-10 through 2026-01-12. The remaining 390 records are date-unknown for this audit: 5 year-only histories, 30 ambiguous histories, and 355 `NA` histories.

## Historical availability requirement

The event years required for all explicit-date records are **2017, 2019, 2022, 2023, 2024, 2025, and 2026**. Only 2024 is locally available. IMD’s documented 0.25° daily archive covers 1901–2024, so the same official product may potentially supply the currently absent 2017, 2019, 2022, and 2023 files after separately obtaining and validating those official inputs. No such files exist in this project directory.

2025 and 2026 are not available from the documented archive coverage through 2024 and must not be fabricated, substituted, or silently omitted. Required but locally missing years are therefore **2017, 2019, 2022, 2023, 2025, and 2026**; the first four are potentially obtainable from the documented archive, while the latter two remain unavailable under that product scope.

## Temporal classification result

| Status | Records | Unique event dates |
| --- | ---: | ---: |
| `RAINFALL_DATE_AVAILABLE` | 9 | 6 |
| `RAINFALL_DATE_NOT_AVAILABLE` | 373 | 26 |
| `EVENT_DATE_UNKNOWN` | 390 | — |
| **Total** | **772** | — |

The nine potentially usable records are all explicit 2024 events. Their selected 2024 grid-date values were finite. `RAINFALL_DATE_NOT_AVAILABLE` means the explicitly reported date is outside the locally available 2024 source coverage; it is not a non-event or negative class. `EVENT_DATE_UNKNOWN` includes all year-only, ambiguous, and `NA` histories and has not been converted into a date.

## Inherited spatial/CRS limitations

The Phase 4 audit found 349 events inside exact-code-compatible polygons under a WGS84 interpretation, while 423 were spatially unmatched; event-coordinate CRS/datum remains independently undocumented and boundary reconciliation is incomplete. This temporal check does not resolve those limitations. Grid selection is performed only under the same provisional WGS84 coordinate interpretation and does not create a final spatial association.

## Conclusion and next requirement

Historical IMD rainfall is **not yet sufficient** for the next modelling phase. The 2024 feasibility result shows the documented grid method can provide finite same-day rainfall for the nine locally overlapping explicit events, but 373 explicit events lack local source-year coverage and 390 records have no usable explicit date.

Next, obtain the official IMD 0.25° daily NetCDF files for **2017, 2019, 2022, and 2023**, retain their provenance, and validate their variable, units, dates, grid structure, and missingness using the existing rainfall rules. Do not attempt 2025/2026 substitution. ML remains blocked until those temporal gaps, the event-coordinate CRS/datum evidence, and authoritative village-boundary reconciliation are resolved.
