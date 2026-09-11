# Experimental hazard index

**Phase:** 8 — hackathon demonstration only  
**Method version:** `phase_8_experimental_v1`  
**Classification:** descriptive experimental index; **not** a supervised model, prediction, probability, warning, label, or validated risk score.

## Purpose and scope

`data/processed/experimental_hazard_index.csv` gives one reproducible, relative index for each of the **40** Phase 6E exact-LGD-code-compatible village polygons. It is intended only to make the available, heterogeneous evidence visible in a hackathon demonstration while Phase 7's supervised-ML decision remains **BLOCKED**.

The index has no target column, no classifier, no fitted parameters, no imputation, and no predictive-accuracy claim. It does not expand beyond the validated 40-polygon subset, re-run spatial matching, use a nearest village/event, apply a buffer, fuzzy/name match, or infer an event CRS. The existing linkage is read only as a conditional audit artifact.

## Evidence classes kept distinct

| Class | Input | Use in this artifact | Not interpreted as |
| --- | --- | --- | --- |
| Terrain features | `terrain_features_villages.csv` | `elevation_mean_m`, `slope_mean_deg` | A measured failure mechanism or label |
| Historical rainfall features | `village_time_features.csv` | Historical 95th percentile of `rainfall_7d_mm` for 2017, 2019, 2022, 2023, 2024 | Live rainfall, forecast, or station observation |
| Observed historical event evidence | `event_village_linkage.csv` | Count of existing `EXACT_POLYGON_MATCH` records per village | Validated positive label, event rate, or no-event evidence |
| Derived output | `experimental_hazard_index_0_100` | Transparent relative combination of the three descriptive components | Probability, prediction, calibrated risk, warning, or ML score |

The strict-containment count is particularly limited: it is conditional on the existing WGS 84 interpretation, while the supplied GSI/NLFC release still lacks release-specific CRS/datum, point semantics, positional accuracy, and completeness documentation. A count of zero is **not** absence of historical events and is not a negative label.

## Inputs and deterministic calculation

The builder reads only the three processed artifacts above. It requires exactly 40 unique and exactly aligned LGD codes in terrain and village-time data. It uses the existing linkage status verbatim; it does not inspect source coordinates or generate a new association.

### 1. Historical rainfall summary

For village \(v\), let \(R_{v,d}^{(7)}\) be `rainfall_7d_mm` from the 73,040-row Phase 6E feature table. The rainfall feature is:

\[
R_v = P_{95}\{R_{v,d}^{(7)} : R_{v,d}^{(7)}\ \text{is non-null}\}.
\]

The calculation uses Pandas' deterministic linear quantile interpolation. It covers the five approved calendar years only. The 1,200 leading 7-day rolling-window nulls are retained in the source feature table and excluded from the quantile solely because no complete seven-day antecedent window exists; they are never filled or replaced.

### 2. Terrain component

Let \(E_v\) be `elevation_mean_m` and \(S_v\) be `slope_mean_deg`. For each feature \(x\), the across-40-village min-max normalization is:

\[
N(x_v) = \frac{x_v - \min_{u \in V}x_u}{\max_{u \in V}x_u - \min_{u \in V}x_u}, \quad V=40\ \text{validated villages}.
\]

\[
T_v = 0.50N(E_v) + 0.50N(S_v).
\]

This equal weighting is a transparent demonstration choice, not an empirically learned or scientifically calibrated terrain susceptibility relationship.

### 3. Conditional historical-event-evidence component

Let \(C_v\) be the number of records whose existing `spatial_linkage_status` is exactly `EXACT_POLYGON_MATCH` and whose existing `matched_village_lgd_code` equals village \(v\). Counts use all 349 such existing records; their dates are not used, no missing date is filled, and no target is created. To reduce the visual dominance of a high count while preserving rank order:

\[
H_v = N(\log(1+C_v)).
\]

`H_v` is conditional historical evidence only. It must not be used as an outcome, label, validation set, or assertion that a zero-count village had no event.

### 4. Experimental index

\[
I_v = 100\left(0.35T_v + 0.40N(R_v) + 0.25H_v\right).
\]

The weights are fixed, sum to one, and are neither fitted nor tuned against events. The 0–100 scale is only a weighted relative display scale over this fixed 40-village subset. It has no absolute threshold and must not be compared with an index rebuilt for a different village population, rainfall period, method version, or weights.

## Output fields

| Field group | Fields |
| --- | --- |
| Validated administrative identity | `village_lgd_code`, `district_lgd_code`, `taluk_lgd_code`, `village_name_en` |
| Original evidence values | `elevation_mean_m`, `slope_mean_deg`, `historical_rainfall_7d_p95_mm`, `conditional_strict_linked_event_count` |
| Transparent components | `elevation_mean_minmax`, `slope_mean_minmax`, `terrain_component`, `rainfall_7d_p95_minmax`, `conditional_event_evidence_minmax` |
| Derived display value | `experimental_hazard_index_0_100` |
| Row-level provenance | `rainfall_feature_source`, `terrain_feature_source`, `event_evidence_source`, `event_evidence_qualification`, `index_method_version` |

## Reproduction and validation

Run from the repository root:

```powershell
python pipeline/build_experimental_hazard_index.py
```

The builder validates: exactly 40 unique villages in the terrain input and output; 40 aligned village IDs in village-time features; no duplicate village-date rows; required fields; finite/non-null output values; normalized components in [0, 1]; index values in [0, 100]; and exact reconstruction of the documented weighted formula to floating-point tolerance.

Current output validation:

| Check | Result |
| --- | ---: |
| Output village records / unique village IDs | 40 / 40 |
| Duplicate village IDs | 0 |
| Missing output values | 0 |
| Conditional strict-linkage counts represented | 349 |
| Historical rainfall 7-day p95 range | 96.921155 to 266.981593 mm |
| Experimental index range | 0.000000 to 68.844151 |
| Maximum formula reconstruction difference | 7.11e-15 |

## Limitations and required interpretation

- It is an experimental relative display, not a forecast, real-time product, probability, calibrated hazard estimate, or operational warning.
- IMD rainfall is historical 0.25-degree grid rainfall associated in Phase 6E with a polygon interior representative point. It is not a village rain gauge measurement and is not live rainfall.
- Elevation and slope summaries are limited DEM-derived attributes. The arbitrary equal terrain weighting does not establish causality.
- The event-count component inherits every Phase 6D/7 limitation. It cannot validate the index and cannot support a positive label, negative label, rate, or accuracy claim.
- The 40 polygons are a restricted exact-ID subset, not a complete Nilgiris village universe; the result must not be generalized to unmatched villages or other regions.
- DDMP ARG/AWS/rain-gauge listings and vulnerability material were reviewed as methodology context only. They are not operational/completeness evidence and are not input fields.
- Phase 7 remains authoritative: supervised ML and target construction are blocked pending release-specific event metadata, approved unit geometry, and a documented observation frame.

Raw data, rainfall features, terrain features, and event records were not modified.
