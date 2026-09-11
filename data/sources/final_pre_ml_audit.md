# Final pre-ML readiness audit

**Audit type:** final read-only review of the current FloodGuard evidence base. This audit creates no training dataset, labels, negative samples, event-to-village links, predictions, risk scores, or model.

## Final decision

## BLOCKED — not ready for supervised village-time ML

FloodGuard has real, reproducible terrain, rainfall, event-inventory, administrative, spatial-boundary, and DDMP evidence. It cannot yet defensibly construct a village-time supervised dataset because the complete modelling-unit geometry, GSI/NLFC event-coordinate CRS/datum, and a complete observation/non-event framework are absent. These are target-validity requirements, not processing gaps that can be filled by assumptions.

The two existing terrain/rainfall locations are explicitly **DEMO** points. They are not official village modelling units and must not be promoted to a training population.

## Evidence reviewed

| Input | Current evidence | Audit finding |
| --- | --- | --- |
| SRTM terrain | Four supplied SRTM GL1 tiles, a derived Nilgiris mosaic, and two DEMO-point terrain records | Real terrain evidence; not yet aggregated to approved modelling units. |
| IMD rainfall | Daily 0.25-degree sources for 2017, 2019, 2022, 2023, and 2024; 3,652 DEMO settlement-day records | Real, complete source-year coverage with no interpolation/imputation; not yet aligned to approved modelling units. |
| GSI/NLFC inventory | 772 supplied Nilgiri records; 382 explicit unambiguous dates; 390 date-unknown records | Real positive-event evidence at source-record level, not a verified village-time target. |
| Village Master | 102 Nilgiris administrative records | Official identifiers/names, but no geometry on their own. |
| SOI/TNGIS KMZ | 58 Nilgiris polygon features; 40 exact LGD-code matches; 62 Village Master-only and 18 KMZ-only records | A partial spatial framework only; unmatched records remain unmatched. |
| DDMP | 35 proposed ARG, 4 AWS, 77 August-2019 GSI records, disaster chronology, and printed vulnerable-location classifications | Official documentary evidence; not a village-event linkage, surveillance register, or ML-label source. |

## Requirement assessment

| Requirement | Status | Evidence-based conclusion |
| --- | --- | --- |
| 1. Spatial modelling-unit readiness | **BLOCKED** | No authoritative, complete, reconciled village modelling-unit layer exists. The 40 exact matches are a validated subset, not the 102-unit population. |
| 2. Event-coordinate CRS readiness | **BLOCKED** | The supplied GSI/NLFC inventory PDF does not document the coordinate CRS/datum. Its coordinates must not be treated as verified compatible with the KMZ or any future unit layer. |
| 3. Event-date readiness | **PARTIALLY_READY** | 382 records have explicit unambiguous dates; 5 are year-only, 30 ambiguous, and 355 `NA`. The 390 date-unknown records cannot enter a daily target. |
| 4. Rainfall temporal coverage | **PARTIALLY_READY** | Complete daily IMD coverage exists for 2017, 2019, 2022, 2023, and 2024. It overlaps 312 explicitly dated inventory records, but not 59 explicit 2025 or 11 explicit 2026 records; rainfall features currently cover DEMO points only. |
| 5. Terrain coverage | **PARTIALLY_READY** | The real SRTM mosaic covers the demonstration area and supports DEMO-point sampling. Unit-level terrain statistics require approved geometry and an approved aggregation specification. |
| 6. Target/label definition | **BLOCKED** | No CRS-verified event-to-unit assignment, target time resolution, positive-event inclusion policy, or treatment of repeated/co-located records has been approved. DDMP vulnerability classes are planning classifications, not outcomes. |
| 7. Negative/observation framework | **BLOCKED** | No documented, geographically complete and time-bounded monitoring/reporting frame establishes that an unrecorded village-day was observed and had no event. Missing inventory records, unmatched points, and unlisted DDMP locations are not negatives. |
| 8. Leakage risks | **PARTIALLY_READY** | Current event and DEMO feature tables remain separate, so no present label leakage exists. A future target requires a pre-specified spatial/group and temporal validation protocol, antecedent-feature cutoff rule, and controls for repeated/co-located records. Random row splitting is not defensible. |
| 9. Required feature alignment | **BLOCKED** | Rainfall grids, SRTM terrain, event points, and village units cannot be aligned until the authoritative unit geometry and compatible event-coordinate reference are available. No unit-to-grid or unit-to-terrain aggregation method is approved. |

## Detailed gates

### Spatial framework

The Village Master has 102 records and the Nilgiris KMZ has 58 features. Only 40 have exact compatible village, district, and taluk LGD codes; 62 Village Master records and 18 KMZ features lack an established counterpart. The existing strict containment audit reported 349 inventory points within the 40 exact polygons, 423 unmatched, and zero ambiguous matches. That is a diagnostic result under the current WGS84 interpretation only, not a verified event-to-village linkage, because the event coordinate CRS/datum is not documented. No fuzzy matching, proximity, buffer, name matching, or forced reconciliation is permitted.

### Event evidence and dates

The 772 GSI/NLFC rows are valid standalone historical-event evidence. Their date categories are: 382 explicit unambiguous, 5 year-only, 30 ambiguous, and 355 `NA`. Explicit records in available IMD years total 312: 4 in 2017, 83 in 2019, 34 in 2022, 182 in 2023, and 9 in 2024. The 70 other explicitly dated records occur in 2025–2026 and do not have an approved local rainfall source. This partial overlap does not create a target, especially where unit linkage and non-event evidence are blocked.

### Rainfall and terrain features

Historical IMD processing is reproducible for the five approved years: 3,652 DEMO settlement-day rows; 730 rows for each non-leap year and 732 for 2024. The expected 20 leading 3-day and 60 leading 7-day rolling nulls are retained; no values were interpolated or imputed. SRTM elevation and slope are real-derived only for two DEMO point locations. Neither artifact is a village-time feature table.

### DDMP evidence

The DDMP supports provenance and historical context only. Its Table 5.3 contains 77 printed GSI August-2019 records without individual occurrence dates per row; it must not be silently merged with the 772-row inventory. Table 5.5 prints 283 vulnerable locations, although its printed class totals add to 282; this discrepancy remains unreconciled. DDMP classifications cannot serve as positive labels, negative labels, risk scores, or a substitute for a complete observation frame.

## Exact remaining requirements before reconsidering ML

1. An authoritative, versioned and CRS-documented modelling-unit boundary layer, or an official crosswalk/replacement release that reconciles all 62 Village Master-only and 18 KMZ-only records and defines the complete study population.
2. Written authoritative GSI/NLFC metadata for this inventory release: coordinate CRS/datum, coordinate semantics/accuracy, event definition, date semantics, version, and geographic/temporal coverage.
3. A written target specification defining the approved unit, time resolution, positive-event rule, duplicate/repeated-record treatment, inclusion criteria, and handling of incomplete date precision.
4. A documented spatially and temporally complete observation/reporting framework that makes `no_event = 0` defensible for stated units and dates. Without it, no negative labels may be created.
5. An approved study-period decision with official rainfall coverage for every retained date. The current local IMD sources do not cover explicit 2025–2026 inventory dates.
6. A documented, reproducible unit-to-IMD-grid and unit-to-SRTM aggregation method, including geometry, coordinate references, edge rules, and missing-data handling.
7. A pre-specified leakage-control and validation plan using justified spatial/group-based and temporal separation; it must be defined before any model fitting.

## Audit conclusion

**BLOCKED — do not begin ML.** The project is ready to preserve and extend real evidence, but not to create a village-time supervised dataset. No label creation, negative sampling, event-to-village assignment, prediction, or model training is justified until every blocking requirement above is met with authoritative evidence.
