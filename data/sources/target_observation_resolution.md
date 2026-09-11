# Target and observation-framework resolution

**Phase:** 7 — read-only target readiness decision  
**Decision:** **BLOCKED**

## Scope and preserved evidence

This resolution inspects, without modifying, the Phase 6D strict-containment linkage, the Phase 6E 40-village daily feature table, DDMP evidence extraction, and the prior CRS, boundary, temporal, and pre-ML audits. It creates no target column, label file, negative sample, event reassignment, score, prediction, or model.

The following prior limitations remain in force:

- The 40 villages are the restricted exact-LGD-code-compatible polygon subset, not a reconciled complete Nilgiris village universe.
- Strict containment is conditional on a WGS 84 interpretation. The supplied 772-row GSI/NLFC PDF still lacks release-specific CRS/datum confirmation, coordinate semantics, positional accuracy, and release/completeness rules.
- A missing inventory record has never been shown to mean a monitored, observed non-event.

## Positive-observation assessment

The linkage retains 349 `EXACT_POLYGON_MATCH` records under the conditional spatial interpretation. Of those, 137 retain an already-extracted explicit ISO `reported_history_date`; 212 have no usable exact date and cannot be a daily observation. The dated-linked records are:

| Year | Conditional linked records with explicit date | In Phase 6E rainfall period? |
| --- | ---: | --- |
| 2017 | 2 | Yes |
| 2019 | 36 | Yes |
| 2022 | 15 | Yes |
| 2023 | 56 | Yes |
| 2024 | 4 | Yes |
| 2025 | 24 | No |
| **Total** | **137** | **113 in the feature period** |

The 113 Phase-6E-period records align by their *conditional* matched LGD code and explicit date with 20 distinct conditional village-date combinations in `village_time_features.csv`. They have real source event records, explicit retained dates, a strict-containment result, and available feature rows. They are therefore a useful **audit candidate set only**.

**Defensible positive village-date observations: 0.** No linked event, including those 113 candidates, may be promoted to `event = 1` yet. The supplied event release is not tied authoritatively to a CRS/datum and point semantics compatible with the polygons; containment therefore does not establish a defensible village assignment. The record date is preserved source text but its release-specific occurrence-date semantics remain undocumented. The 24 dated 2025 records lack Phase 6E rainfall coverage; the 212 date-unknown linked records must remain temporally unknown. No DDMP narrative/window was used to fill or replace any date.

## Negative-observation assessment

**Defensible non-event village-date observations: 0.** There is no documented surveillance, reporting-completeness, inclusion, or observation-period evidence that covers any one of the 40 village polygons on any date and permits a conclusion that an absent inventory record means `no_event = 0`.

In particular, none of the following is negative evidence:

- a Phase 6E village-date with no linked event;
- the 423 inventory records without conditional exact-polygon containment;
- a linked record with unknown date;
- a village with no linked record;
- a day outside available IMD years; or
- a DDMP station/location, vulnerability class, or chronology entry.

Accordingly, neither standard supervised classification nor case-control sampling can be constructed from the current artifacts without fabricating negatives.

## DDMP ARG/AWS/rainfall evidence and observation framework

The DDMP provides useful documentary context but does **not** establish a valid landslide observation framework:

| DDMP evidence | What it establishes | What it does not establish |
| --- | --- | --- |
| 29 rainfall-registering stations (Table 2.5) | A stated district station list | Station coordinates/codes, operation dates, data series, completeness, or landslide monitoring coverage |
| 35 **proposed** ARG stations (Table 2.6) | Proposed locations/codes as printed | Commissioning, operation, datum, observations, availability, or coverage |
| 4 AWS location records | Printed locations/remarks | Station identifier, coordinate datum, period of operation, measurements, completeness, or event/non-event ascertainment |
| Rainfall/event chronology and August-2019 narrative | Documentary rainfall and incident context at the printed temporal precision | A per-village daily event outcome, systematic detection, or absence evidence |
| Vulnerable-location classes | Planning classification based on legacy material | Observed outcomes, probability labels, or non-event observations |

The DDMP explicitly leaves station CRS/datum, operational status, sensor history, temporal coverage, rainfall observations, and completeness unstated. It also contains no village-day landslide surveillance protocol or reporting-completeness statement. It cannot support either positive village-date assignment or a negative-label observation frame.

## Readiness decision

**BLOCKED** — not `READY_FOR_SUPERVISED_ML` and not `READY_FOR_ALTERNATIVE_MODEL`.

No defensible binary/count/survival target has both valid positive village-date observations and a documented observation frame for non-events. An alternative supervised formulation would still require a defined outcome and observation frame; none is currently available. Unsupervised descriptive work would be a materially different scope and is not authorised by this phase.

## Minimum remaining evidence before a new target review

1. **Authoritative modelling-unit geometry:** versioned Nilgiris boundaries with stable IDs, CRS/datum, validity/vintage, and an official reconciliation/crosswalk for the current 62 Village Master-only and 18 KMZ-only records; alternatively, a formally justified restricted unit population.
2. **Release-specific event documentation:** GSI/NLFC/provider confirmation tying the supplied PDF to a release/version and stating coordinate CRS/datum, axis order, point semantics, positional accuracy, date-field semantics, duplicate/correction rules, inclusion criteria, spatial/temporal coverage, and update cut-off.
3. **An observation frame:** documented systematic landslide detection/reporting/validation coverage identifying the exact units, dates, reporting pathways, completeness/false-negative limitations, and conditions under which an unrecorded unit-date can be classified as non-event.
4. **A written target specification:** outcome definition, unit and time resolution, treatment of multiple reports/duplicate coordinates, inclusion/exclusion rules, date-precision handling, and linkage procedure after the first two evidence gates are satisfied.
5. **Study-period feature coverage:** retain or obtain documented rainfall for every date selected by the approved target design; the current feature table covers only 2017, 2019, 2022, 2023, and 2024. Do not invent coverage for 2025/2026.
6. **Pre-specified validation protocol:** spatial/group and temporal holdouts, leakage controls for repeated/co-located reports and antecedent rainfall windows, and an assessment of sample independence after an actual target exists.

Until this evidence is obtained and reviewed, retain the 113 records only as conditional audit candidates and retain every other village-date as outcome-unknown. Do not train ML or generate risk scores.
