# Phase 12 ML Dataset and Spatial Validation Gate Resolution

**Phase:** 12 — ML Dataset Readiness and Spatial Validation Gate  
**Gate Decision:** **BLOCKED** — Supervised ML training dataset cannot be defensibly constructed.  
**Dataset Action:** No `data/processed/ml_dataset.csv` or `pipeline/build_ml_dataset.py` created.

---

## 1. Summary of Gate Decision

A rigorous inspection of the FloodGuard evidence base confirms that **a supervised machine-learning training dataset cannot be defensibly constructed from the current evidence**.

While the project has successfully built and validated reproducible terrain features, 5 years of IMD daily gridded rainfall, a 772-record GSI/NLFC landslide inventory, and a 40-village polygon administrative subset, the essential scientific requirements for a supervised learning target remain unfulfilled. Creating a binary target column (e.g. `landslide_event` in `{0, 1}`) would require either assuming unverified positive-event semantics or fabricating non-event negative labels from absence.

In accordance with FloodGuard data integrity rules:
- No positive labels are invented or assumed from conditional spatial containment.
- No negative labels are fabricated from the absence of inventory records.
- No ML model is trained, and no pseudo-predictions or risk scores are generated.

---

## 2. Determination of the Five Core Evaluation Questions

### Question 1: Can a defensible village-date target be created?
**No. (Decision: BLOCKED).**

A defensible supervised target requires:
1. Validated positive instances where the event outcome occurred on a specific date within a defined spatial unit under verified coordinate datum and point semantics.
2. Validated negative instances where the observation frame establishes that the unit was monitored and confirmed free of events on that date.

Neither requirement is satisfied:
- **Positive limitations:** The 772 GSI/NLFC landslide records are standalone inventory points without release-specific CRS/datum verification, point semantics (crown vs. toe vs. road-cut), or positional accuracy statements. Strict polygon containment within the 40 village boundaries is conditional on an uncertified WGS 84 interpretation.
- **Negative limitations:** There is zero surveillance or monitoring documentation establishing that an unrecorded village-date represents a true absence of landslides. Treating unrecorded village-dates as `0` would constitute systematic negative-label fabrication.

---

### Question 2: What exact evidence supports the candidate instances?

The candidate evidence consists of:
1. **Historical Landslide Records (GSI/NLFC):**
   - 772 source records in `data/processed/landslide_events.csv`.
   - 349 records fall within the 40 validated village polygons under conditional WGS 84 containment (`event_village_linkage.csv`).
   - 137 of those 349 records retain an explicit, unambiguous ISO date (`reported_history_date`).
   - **113 records** occur within the five approved IMD rainfall calendar years (2017, 2019, 2022, 2023, 2024), mapping to **20 unique village-date combinations**.
   - 24 explicitly dated linked records occur in 2025 (outside local IMD rainfall coverage).
   - 212 linked records lack explicit calendar dates and cannot be assigned to any daily observation.
2. **Spatiotemporal Feature Observations (`village_time_features.csv`):**
   - 73,040 daily feature rows across 40 validated village polygons for 2017, 2019, 2022, 2023, and 2024.
   - Contains daily IMD rainfall (1D, 3D trailing sum, 7D trailing sum) and SRTM 30m DEM terrain attributes (mean elevation and mean slope).
   - Trailing rolling nulls (400 for 3D, 1,200 for 7D) are strictly preserved without imputation.
3. **Absence Evidence:**
   - **0 verified non-event observations.** Neither the District Disaster Management Plan (DDMP), Survey of India (SOI), IMD, nor GSI provides an exhaustive daily monitoring log certifying non-occurrence for any village polygon.

---

### Question 3: What observations are usable?

- **Usable for Supervised ML Training (`target ∈ {0, 1}`):** **0 observations.**
- **Usable for Audit & Multi-Criteria Descriptive Display:**
  - The 113 explicitly dated, conditionally linked GSI records are preserved as an **audit candidate set**.
  - The 73,040 village-time feature rows are usable for descriptive baseline exploration, historical rainfall quantile analysis, and deterministic multi-criteria index calculation (as implemented in the Phase 8 Experimental Hazard Index).

---

### Question 4: What leakage-control and validation strategy is possible?

If an authoritative target and observation frame are established in a future phase, the only scientifically defensible validation protocol is:

1. **Spatial Grouped Validation (Leave-One-Taluk-Out / GroupKFold):**
   - Grouping observations by the 6 administrative taluks (Udhagamandalam, Coonoor, Kotagiri, Gudalur, Pandalur, Kundah).
   - Splitting by taluk ensures the model is evaluated on unseen geographic clusters, preventing spatial autocorrelation leakage between neighboring villages sharing identical 0.25° IMD rainfall grid cells or contiguous SRTM terrain.
2. **Temporal Validation Holdouts (Year-Based Separation):**
   - Temporal partition (e.g. Training: 2017, 2019, 2022; Validation: 2023; Test: 2024).
   - Evaluates generalization across distinct monsoon seasons and prevents temporal lookahead leakage.
3. **Antecedent Rainfall Window Isolation:**
   - Features must use strictly trailing windows ($T-1, T-3, T-7$) ending on or before the observation date. Same-day post-event rainfall must be excluded to prevent label leakage.
4. **Co-Located and Multi-Event Handling:**
   - Clustering or deduplicating multiple GSI records occurring on the same date within the same village polygon to prevent duplicate inflated feature-target pairs.
5. **Strict Prohibition:**
   - Standard random row splitting (e.g. `train_test_split(shuffle=True)`) is **strictly prohibited** due to severe spatial and temporal feature leakage.

---

### Question 5: What blockers remain before ML readiness?

The following five blocking requirements must be resolved with authoritative external evidence before supervised ML dataset creation can proceed:

1. **Authoritative Non-Event Observation Frame:**
   - Official documentation from district disaster management authorities or GSI defining an exhaustive surveillance framework, reporting completeness, and explicit conditions under which an unrecorded village-date is certified as a non-event (`y = 0`).
2. **Release-Specific GSI Event Metadata & CRS Certification:**
   - Official GSI/NLFC release documentation confirming the exact coordinate reference system / datum (WGS 84), coordinate capture semantics (headscarp crown vs. deposit toe vs. road intersection), positional accuracy, and duplicate/revision policies for the supplied 772-record inventory.
3. **Reconciled Modelling-Unit Boundary Universe:**
   - Complete, authoritative administrative boundaries reconciling the current 62 Village Master-only records and 18 KMZ-only records to establish the full Nilgiris unit population.
4. **Target Formulation Specification:**
   - Documented policy for handling multi-event occurrences, date precision cutoffs, and whether the target is binary occurrence, hazard susceptibility tier, or event count.
5. **Temporal Feature Alignment:**
   - Continuous IMD rainfall coverage for all study dates (specifically resolving rainfall sources for 2025/2026 events if included in the target window).

---

## 3. Dataset Gate Status Summary Table

| Gate Component | Status | Verified Evidence | Blocker / Limitation |
| :--- | :---: | :--- | :--- |
| **Spatial Unit Geometry** | PARTIAL | 40 exact-LGD matched polygons | 62 Master-only & 18 KMZ-only records unlinked |
| **Event Coordinate CRS** | PARTIAL | GSI schema specifies WGS84 | Local PDF release lacks version/datum certificate |
| **Event Dates** | PARTIAL | 137 linked explicit dates | 212 linked records lack calendar dates |
| **Feature Coverage** | COMPLETE | 73,040 daily rows (5 years) | Restricted to 40 validated polygons |
| **Positive Target (`y=1`)** | CANDIDATE ONLY | 113 dated events (20 village-dates) | Linkage is conditional on uncertified WGS84 |
| **Negative Target (`y=0`)** | **ABSENT** | 0 verified non-event observations | No surveillance register; absence ≠ non-event |
| **Overall ML Dataset Gate** | **BLOCKED** | Evidence preserved for audit | **Supervised ML dataset cannot be created** |

---

## 4. Conclusion

In strict adherence to the project rules and the results of Phases 6A–6E, 7, and 8, **FloodGuard maintains a BLOCKED decision for Phase 12**. 

No synthetic labels will be generated, no `ml_dataset.csv` is produced, and no model training is initiated. The 73,040 feature rows and 772 inventory points remain preserved with complete provenance documentation.
