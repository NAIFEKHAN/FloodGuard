# Final pre-ML evidence audit

**Audit type:** read-only evidence review. This document creates no labels, negative samples, event-to-village links, training table, model, prediction, or score.

## 1. Executive conclusion

**Can we scientifically construct the supervised ML dataset now? No.**

FloodGuard has real, auditable terrain, rainfall, administrative, boundary, and landslide-inventory inputs. The historical IMD expansion materially improves temporal rainfall availability, but it does not establish a valid supervised outcome. There is no approved complete spatial modelling-unit layer; the available village boundaries are unreconciled; the inventory coordinates have no independently documented CRS/datum; and there is no documented observation/monitoring frame from which `no_event = 0` can be asserted. Absence of an inventory record is not evidence of a non-event.

Accordingly, **supervised ML dataset creation is not approved**. The two DEMO settlements and their derived terrain/rainfall table must not be promoted to a modelling population.

## 2. Dataset inventory

| Evidence | Current audited state | Role and limitation |
| --- | --- | --- |
| SRTM GL1 terrain | Four real tiles and a Nilgiris mosaic; `terrain_features.csv` covers two DEMO points | Real-derived terrain, not terrain aggregation for approved modelling units. |
| IMD rainfall | Official daily 0.25-degree NetCDF sources for 2017, 2019, 2022, 2023, and 2024; 3,652 DEMO settlement-day rows | Real rainfall with hashes and retained rolling nulls; derived features are only for two DEMO points. |
| Landslide inventory | 772 supplied GSI/NLFC Nilgiris records | Real positive-event evidence at source-record level, but not yet verified unit-time target evidence. |
| Village Master | 102 Nilgiris administrative records, district LGD 587, six taluk codes | Administrative IDs/names only; no usable geometry by itself. |
| SOI/TNGIS KMZ | 58 Nilgiris polygons out of 17,119 statewide features | 40 exact code-compatible with Village Master; 62 Village Master-only and 18 KMZ-only records remain unreconciled. |
| Existing audits and provenance | Source documentation, source-row/page fields, hashes, validations, and tests exist | Reproducible processing is stronger than target validity; it does not fill missing scientific evidence. |

## 3. Spatial readiness assessment

There is no approved spatial modelling population. The only fully derived terrain/rainfall observations use two explicitly **DEMO** settlement points. They are not official villages and cannot define the study units.

The Village Master supplies 102 administrative identifiers but no boundaries. The supplied KMZ has 58 Nilgiris polygon features; 40 have exact compatible village, district, and taluk codes, while 62 Village Master IDs and 18 KMZ IDs have no established counterpart. The 40 exact matches are auditable subset evidence, not a complete village boundary universe.

The prior strict point-in-polygon audit found 349 of 772 inventory coordinates inside these 40 eligible polygons, 423 unmatched, and zero ambiguous geometry matches. It used no proximity, buffer, name, or geocoding rule. However, the event PDF does not independently document coordinate CRS/datum. Thus the 349 results mean only **inside an eligible polygon under the current WGS84 interpretation**, not verified event-to-village assignments.

## 4. Temporal readiness assessment

The five approved IMD sources have full daily coverage for their stated years: 2017, 2019, 2022, 2023 (365 days each), and 2024 (366 days). Their schemas and 0.25-degree grids are compatible. Historical processing retained the original nearest-grid method, performed no interpolation or imputation, and retained expected rolling-window nulls.

Of 382 explicit, unambiguous inventory dates, 312 occur in the available rainfall years: 4 in 2017, 83 in 2019, 34 in 2022, 182 in 2023, and 9 in 2024. The remaining 70 explicit dates occur in 2025 (59) and 2026 (11), for which no approved local rainfall source exists. A further 390 inventory records have no usable exact event date: 5 year-only, 30 ambiguous, and 355 `NA`. They remain unknown.

The available years therefore provide **partial temporal overlap**, not sufficient target-time coverage for the full supplied inventory. In addition, the 312 overlap records occur on only 19 unique explicit dates (the 2023 records are all on one recorded date), which limits independent event-time variation. Temporal overlap alone cannot create labels, particularly before spatial-unit and observation-frame issues are resolved.

## 5. Event-label readiness assessment

The inventory provides real event records and 382 exact source dates. It can support future positive-label construction only after a study unit, coordinate CRS/datum compatibility, event-time precision policy, and duplicate/multiple-event handling policy are defined and justified.

It cannot now support a unit-day `event = 1` target. The project has no approved complete unit geometry, and the 349 provisional containment results are not CRS-verified. The 390 records without exact dates cannot be placed in a daily target; they must remain unknown rather than being excluded silently or converted to another date precision.

## 6. Negative-sample feasibility

**Negative labels cannot yet be created.** The project has no documented surveillance, reporting completeness, inventory inclusion rule, or observation window demonstrating that a unit-day without an inventory record was observed and had no landslide. Consequently, an unrecorded village/day, grid cell/day, or DEM pixel/day cannot be assigned `no_event = 0`.

Neither the 423 unmatched records nor the 390 date-unknown records are negative evidence. Nor can locations outside a provisional polygon, days lacking a report, or DEMO settlement-days be used as artificial controls. Creating negatives from any of those conditions would manufacture the target class.

## 7. Data leakage considerations

No current feature table contains event labels, which prevents present label leakage. The existing processing also keeps event inventory separate from the DEMO terrain/rainfall integration table and preserves null rolling windows rather than imputing them.

If target design is later approved, leakage control must be specified before modelling: derive rainfall and terrain using only the approved unit definition; ensure antecedent windows end on or before the target date; prevent duplicate/co-located or repeated event records from crossing splits; and use spatial/group-based validation (for example, held-out taluks or other justified spatial groups) with an appropriate temporal holdout. Random row-level splitting would be unsuitable for spatially autocorrelated unit-day data. These are future design requirements, not a basis to begin ML now.

## 8. Provenance and reproducibility assessment

Processing is substantially reproducible: raw paths are retained; the event extractor preserves PDF page, table, and row text; terrain/rainfall pipelines validate inputs; historical rainfall provenance stores each source filename, SHA-256, dimensions, dates, units, grid range, and derived row count; and the suite currently covers processing and audit behavior with synthetic fixtures.

Provenance is nevertheless incomplete for target construction. The supplied event PDF lacks independently documented publisher/version/original URL and, critically, coordinate CRS/datum. The boundary source lacks the authoritative version/vintage reconciliation needed to explain the 62/18 identifier mismatch. Reproducible execution cannot substitute for those missing source facts.

## 9. Requirement assessment

| Requirement | Status | Evidence and decision |
| --- | --- | --- |
| A. Spatial modelling unit | **BLOCKED** | No approved complete spatial unit layer; two DEMO points are prohibited as modelling population. |
| B. Village identifier compatibility | **PARTIALLY_READY** | 40 exact code-compatible records; 62 Village Master-only and 18 KMZ-only records remain unexplained. |
| C. Village boundary completeness | **BLOCKED** | KMZ cannot be established as complete for the 102-record Village Master universe. |
| D. Event coordinate CRS/datum | **BLOCKED** | Event PDF does not independently document CRS/datum; WGS84 interpretation is provisional only. |
| E. Event occurrence dates | **PARTIALLY_READY** | 382 explicit unambiguous dates; 390 records remain date-unknown and cannot enter a daily target. |
| F. Historical rainfall coverage | **PARTIALLY_READY** | Approved daily sources overlap 312 explicit records, but not 2025/2026 events; derived features cover only DEMO points. |
| G. Terrain coverage | **PARTIALLY_READY** | Real SRTM mosaic exists, but terrain is not aggregated to approved modelling units. |
| H. Definition of positive events | **BLOCKED** | Real inventory exists, but no CRS-verified unit-time target definition or positive-event assignment policy exists. |
| I. Definition of negative/non-event samples | **BLOCKED** | No defensible non-event evidence or rule; negatives must not be manufactured. |
| J. Observation/monitoring completeness | **BLOCKED** | No documented surveillance/reporting completeness frame for unit-days. |
| K. Prevention of data leakage | **PARTIALLY_READY** | Current tables are separated and no labels exist; a target-specific spatial/temporal split protocol is not yet defined. |
| L. Temporal alignment between rainfall and events | **PARTIALLY_READY** | 312 explicitly dated records overlap approved IMD years; alignment to valid units is not established and 70 explicit records lack rainfall years. |
| M. Spatial alignment between rainfall, terrain, villages and events | **BLOCKED** | No approved unit geometry, incomplete boundary reconciliation, and unverified event datum prevent defensible alignment. |
| N. Reproducibility/provenance | **PARTIALLY_READY** | Strong processing provenance/hashes/tests exist, but critical event CRS and boundary-vintage evidence is absent. |

## 10. Exact remaining blockers

1. An authoritative, versioned boundary layer or official crosswalk that defines the complete approved modelling-unit population and explains all 62 Village Master-only and 18 KMZ-only identifiers.
2. Authoritative GSI/NLFC/provider documentation of the supplied inventory coordinate CRS/datum, sufficient to verify compatibility with the approved unit geometry.
3. A written target specification: unit type, target time resolution, event definition, treatment of multiple/repeated records, inclusion rules, and handling of date precision.
4. A documented observation/monitoring and reporting-completeness frame that makes recorded absence a defensible `no_event = 0` statement for specified units and dates.
5. Approved rainfall coverage for every selected study-period date, or an explicitly restricted study period justified before target construction. The current local sources do not cover explicit 2025/2026 records.
6. A documented spatial aggregation/alignment method for IMD grid rainfall and SRTM terrain to the approved units, including CRS, geometry, and edge conventions.
7. A pre-specified spatial and temporal validation/leakage-control protocol for the eventual target dataset.

## 11. Minimum additional real data/evidence required

- An authoritative Nilgiris modelling-unit boundary release with stable IDs, CRS/datum, source/version/vintage, validity period, and licence; or an official crosswalk/replacement release reconciling the two current administrative sources.
- Written authoritative metadata for the GSI/NLFC inventory identifying coordinate CRS/datum, event definition, date semantics/precision, coverage, and reporting completeness.
- A real, documented observation frame (for example, systematic landslide monitoring/reporting coverage) that identifies the units and dates where non-occurrence can be asserted.
- Official rainfall for all dates retained in the approved study design, with the same provenance and missing-value controls; no substitute or imputed data for unavailable years.
- An approved written unit-to-grid and unit-to-terrain aggregation specification after the authoritative geometry and coordinate references are available.

## 12. Recommendation for the next phase

Do **not** begin ML, label creation, negative sampling, or event-to-village reassignment. The next bounded phase should obtain and document the authoritative boundary-version/LGD reconciliation and event-coordinate CRS/datum evidence. In parallel, obtain a documented observation-completeness frame capable of supporting non-event labels. Only after those facts are available should the project conduct a new read-only target-definition review; it should then decide whether a restricted, fully observed study period with complete rainfall coverage can be justified.
