# Phase A1: Target Observation Framework and ML Feasibility Resolution

**Phase:** A1 — Target Observation Framework & ML Feasibility Resolution  
**Project:** FloodGuard (Nilgiris Disaster Intelligence Prototype — Hackathon Problem Statement #14)  
**Overall Final Gate:** **CONDITIONAL_ML** (Restricted to spatial susceptibility with declared PU assumptions; daily time-series ML remains **BLOCKED**)

---

## 1. Executive Summary

This resolution investigates whether the machine-learning target blockers identified in Phases 7 and 12 can be resolved without fabricating official data, falsifying positive/negative labels, or violating scientific integrity rules.

Four candidate target formulations were evaluated against the verified FloodGuard evidence base:
1. **Option A: Daily Binary Village-Event Target ($y_{v,t} \in \{0, 1\}$)** — **NOT_DEFENSIBLE (BLOCKED)**
2. **Option B: Episodic Event-Window Target ($y_{v,W} \in \{0, 1\}$)** — **NOT_DEFENSIBLE (BLOCKED)**
3. **Option C: Spatial Village Susceptibility Target ($y_v \in \{0, 1\}$ or Relative Ranking)** — **CONDITIONALLY_DEFENSIBLE (CONDITIONAL_ML)**
4. **Option D: Deterministic Multi-Criteria Hazard Index Fallback ($I_v \in [0, 100]$)** — **DEFENSIBLE (ACTIVE BASELINE)**

---

## 2. Evidence Base Inspected

The evaluation inspected the complete verified FloodGuard evidence base:
- **Administrative Units:** 40 valid, non-overlapping village polygons reconciled with exact 3-code LGD matching (`vlcode`, `dtcode=587`, `sdcode`) from Survey of India KMZ and Village Master.
- **Topographic Base:** SRTM 30m Digital Elevation Model mosaic covering Nilgiris with zonal mean elevation ($E_v$) and slope ($S_v$) computed for all 40 polygons.
- **Meteorological Base:** IMD 0.25° daily gridded rainfall across 5 calendar years (2017, 2019, 2022, 2023, 2024), providing 73,040 village-date observations of 1-day, 3-day trailing, and 7-day trailing precipitation.
- **Landslide Inventory:** 772 official GSI/NLFC landslide event points.
- **Spatial Containment:** 349 event points strictly contained within the 40 village polygons under WGS 84 coordinate interpretation (423 unlinked; 0 boundary/ambiguous).
- **Temporal Alignment:** 137 of the 349 linked records have unambiguous ISO dates; **113 records** fall within the 5 IMD feature years, mapping to **20 unique village-date occurrences**.
- **Documentary Context:** Nilgiris District Disaster Management Plan (DDMP) Table 2.5 (29 rain stations), Table 2.6 (35 proposed ARGs), Table 5.3 (77 August-2019 GSI records), and Table 5.5 (283 vulnerable planning locations).

---

## 3. Comprehensive Target Design Evaluation

### Target Option A: Daily Binary Village-Event Target ($y_{v,t} \in \{0, 1\}$)
- **Definition:** Daily classification where $y_{v,t} = 1$ if a landslide occurred in village polygon $v$ on calendar date $t$, and $y_{v,t} = 0$ otherwise.
- **Positive-Label Feasibility:** 113 candidate records across 20 village-dates. These records represent real historical incidents, but their assignment to specific village polygons remains conditional on uncertified release-specific CRS metadata.
- **Negative-Label Feasibility: ABSENT (0 Verified Observations).** There is no exhaustive daily surveillance register. The 73,020 unrecorded village-dates represent unmonitored or unrecorded periods, not verified non-events. Labeling unrecorded dates as `y=0` is synthetic label fabrication.
- **Classification: NOT_DEFENSIBLE.**
- **Gate:** **BLOCKED.**

---

### Target Option B: Episodic Event-Window Target ($y_{v,W} \in \{0, 1\}$)
- **Definition:** Aggregating observation units into multi-day extreme rainfall episodes (e.g. August 6–9 2019 monsoon cloudburst, November 22–23 2023 storm) for village $v$ during window $W$.
- **Positive-Label Feasibility:** Captures clustered incident reports during documented major regional triggers.
- **Negative-Label Feasibility: ABSENT.** While extreme storm windows restrict the temporal domain, unrecorded villages during a storm cannot be certified as zero-landslide areas due to reporting biases (landslides on forested hillslopes or unpopulated tea estates frequently go unrecorded in road-centric inventories).
- **Classification: NOT_DEFENSIBLE.**
- **Gate:** **BLOCKED.**

---

### Target Option C: Spatial Village Susceptibility Target ($y_v \in \{0, 1\}$ or Relative Ranking)
- **Definition:** Spatial classification or ranking of the 40 validated villages based on cumulative verified historical event presence:
  - $y_v = 1$: Villages with verified conditional historical landslide presence ($\ge 1$ strictly contained GSI event; 25 villages, 349 total events).
  - $y_v = 0$ / Unlabeled: Villages with no recorded GSI events in the inventory (15 villages).
- **Positive-Label Feasibility: STRONG (Conditional).** 25 villages contain confirmed historical landslide evidence from official GSI records.
- **Negative-Label Feasibility: POSITIVE-UNLABELED (PU) INTERPRETATION ONLY.** The 15 zero-event villages must NOT be claimed as "immune" or "certified non-hazardous"; they are strictly **Unlabeled / No Recorded Evidence** units.
- **Modelling Validity:** Standard binary classification cannot treat 0 as a true negative, but a **Positive-Unlabeled (PU) Susceptibility Model** or a **Spatial Group-Validated Susceptibility Classifier** (with explicit PU weighting or ranking loss) is scientifically sound under explicitly declared hackathon assumptions.
- **Classification: CONDITIONALLY_DEFENSIBLE.**
- **Gate:** **CONDITIONAL_ML.**

---

### Target Option D: Deterministic Multi-Criteria Hazard Index Fallback ($I_v \in [0, 100]$)
- **Definition:** The fixed Phase 8 composite formula combining min-max normalized SRTM terrain ($T_v$), IMD 7-day 95th-percentile rainfall ($R_v$), and conditional log-transformed GSI event evidence ($H_v$):
  $$I_v = 100 \times \left(0.35 T_v + 0.40 N(R_v) + 0.25 H_v\right)$$
- **Defensibility: COMPLETE.** Fully reproducible, deterministic, requires no negative-label fabrication, involves no fitted parameters, and clearly conveys relative multi-criteria hazard context.
- **Classification: DEFENSIBLE.**
- **Gate:** **ACTIVE BASELINE.**

---

## 4. Technical Analysis of Critical Dimensions

### 4.1 Coordinate Reference System (CRS) & Datum
- **Schema Level:** Official Government of India NIDM guidelines (Annexure II) and GSI field incident reports establish the national inventory schema standard as **WGS 1984 Datum in decimal degrees (EPSG:4326)**.
- **Release Level:** The supplied 772-row PDF lacks an embedded EPSG certificate.
- **Required Assumption:** All spatial containment operations proceed under the documented national standard (WGS 84 / EPSG:4326), acknowledging that exact release-specific positional accuracy (e.g. ±15m GPS vs. map pick) is uncertified.

### 4.2 Event Date Semantics
- 382 records have explicit dates, 137 are linked to validated polygons, and 113 fall in the 5 IMD years.
- GSI date fields represent "Reported History Date" (incident date). Undated records (212 linked) must remain strictly excluded from temporal models, but remain fully valid for cumulative spatial susceptibility (Target C) and descriptive indexing (Target D).

### 4.3 Observation-Framework & Negative-Label Reality
- GSI landslide inventories are incident-driven event registries, not exhaustive spatio-temporal census surveys.
- Therefore, the absence of an event record in a village polygon or on a specific date means **unobserved / unrecorded**, never verified absence.
- Any ML methodology must formally use **Positive-Unlabeled (PU) Learning** or **Spatial Susceptibility Ranking**, explicitly prohibiting naive binary cross-entropy with unweighted negative labels.

### 4.4 Leakage Risks & Governance Protocols
1. **Spatial Autocorrelation Leakage:** Neighboring villages share contiguous slopes and identical 0.25° IMD grid cells.
   - *Mandatory Protocol:* **Leave-One-Taluk-Out (LOTO) / GroupKFold Cross-Validation** across the 6 Nilgiris taluks (*Udhagamandalam, Coonoor, Kotagiri, Gudalur, Pandalur, Kundah*). Random train/test splits are strictly prohibited.
2. **Temporal Lookahead Leakage:** Trailing feature windows only ($T-1, T-3, T-7$).
3. **Multi-Event Inflation:** Grouping multiple events per village to avoid duplicating spatial features.

---

## 5. Summary Evaluation Matrix

| Target Option | Formulation | Positive Labels | Negative Labels | Scientific Defensibility | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **A. Daily Binary Time-Series** | $y_{v,t} \in \{0, 1\}$ | 113 events (20 village-days) | 0 (73,020 unknown) | **NOT_DEFENSIBLE** | **BLOCKED** |
| **B. Episodic Storm Window** | $y_{v,W} \in \{0, 1\}$ | Clustered storm events | 0 (Unrecorded ≠ Non-event) | **NOT_DEFENSIBLE** | **BLOCKED** |
| **C. Spatial Susceptibility (PU)** | $y_v \in \{1, \text{Unlabeled}\}$ | 25 villages with events | 15 Unlabeled villages | **CONDITIONALLY_DEFENSIBLE** | **CONDITIONAL_ML** |
| **D. Multi-Criteria Hazard Index** | $I_v \in [0, 100]$ | 349 containment counts | Not required (descriptive) | **DEFENSIBLE** | **ACTIVE BASELINE** |

---

## 6. Recommended Hackathon Protocol (Phase A2 Proposal)

If the project proceeds to machine learning for Problem Statement #14, the **ONLY scientifically defensible path** is **Option C (Spatial Village Susceptibility under Positive-Unlabeled Framework)**:

1. **Dataset Definition:** 40 validated Nilgiris villages with aggregated SRTM terrain (mean elevation, mean slope, relief) and 5-year historical IMD rainfall quantiles (7D P95, 3D P95, annual max).
2. **Target Definition:** Positive ($y=1$, 25 villages with verified GSI landslide history) vs. Unlabeled ($y=0$, 15 villages with no recorded GSI events).
3. **Model Formulation:** XGBoost / Random Forest Susceptibility Classifier trained with spatial GroupKFold (by Taluk) and evaluated using Ranking / PR-AUC metrics rather than raw accuracy.
4. **Validation:** Strict Leave-One-Taluk-Out (6 folds) ensuring no geographic leakage.
5. **Transparency & UI Labels:** Model output must be explicitly presented as **"Demonstration Spatial Susceptibility Score"** (not a live warning or real-time prediction).

---

## 7. Final Gate Decision

- **Daily Time-Series Supervised ML:** **BLOCKED**
- **Spatial Susceptibility ML (Option C):** **CONDITIONAL_ML** (Approved for Phase A2 dataset build under explicit PU and GroupKFold protocols)
- **Deterministic Multi-Criteria Baseline:** **DEFENSIBLE (ACTIVE)**

---
*No raw data, feature tables, or dashboard files were modified in Phase A1. Awaiting explicit user approval before Phase A2.*
