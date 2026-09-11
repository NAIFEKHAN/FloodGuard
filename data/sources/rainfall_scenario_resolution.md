# Phase B: Rainfall Scenario Engine Resolution

**Phase:** B — Rainfall Scenario Engine  
**Status:** **DEFENSIBLE (MATHEMATICALLY COMPATIBLE)**  
**Target Scope:** 40 validated Nilgiris village polygons  
**Model Architecture:** Phase A Positive-Unlabeled (PU) Spatial XGBoost Classifier  

---

## 1. Executive Summary

The Phase B Rainfall Scenario Engine provides deterministic simulation capability over the 40 validated Nilgiris village polygons. 

The engine enables evaluating how spatial susceptibility shifts when regional precipitation varies (e.g. subdued monsoon, baseline climatology, heavy surge, extreme 2019-equivalent cloudburst, or custom parameters) while **strictly keeping static topography constant** and **never mutating underlying source datasets**.

All scenario outputs are explicitly classified as **Demonstration Scenarios**, strictly distinguished from live operational emergency alerts or calibrated hazard forecasts.

---

## 2. Model Compatibility Analysis

The Phase A primary model (`model/artifacts/spatial_susceptibility_xgboost.json`) was trained on 8 continuous features partitioned into two functional classes:

### 2.1 Static Terrain Features (Held Constant Per Village)
These features represent the permanent physical landscape and are **never modified** during scenario execution:
1. `elevation_mean_m` (Zonal mean elevation, m)
2. `elevation_range_m` (Zonal relief span, $E_{\max} - E_{\min}$, m)
3. `slope_mean_deg` (Zonal mean slope gradient, degrees)
4. `slope_max_deg` (Maximum cliff/scarp gradient, degrees)

### 2.2 Rainfall-Dependent Features (Dynamically Scaled in Scenario Copy)
These features capture the antecedent and peak saturation dynamics and are varied within the in-memory scenario feature vector:
1. `rainfall_7d_p95_mm` (7-day trailing antecedent saturation threshold, mm)
2. `rainfall_3d_p95_mm` (3-day trailing antecedent surge threshold, mm)
3. `rainfall_1d_max_mm` (Peak single-day cloudburst intensity, mm)
4. `rainfall_annual_mean_mm` (Seasonal/annual cumulative baseline scale, mm)

---

## 3. Preset Scenario Specifications

| Scenario Key | Scenario Name | Rainfall Scaling Factor | Meteorological Interpretation |
| :--- | :--- | :---: | :--- |
| `moderate` | **Moderate / Normal Monsoon** | **0.70x** (-30%) | Below-average monsoon; subdued antecedent saturation. |
| `baseline` | **Historical Baseline** | **1.00x** (0%) | Verified 5-year historical IMD climatology (2017, 2019, 2022–2024). |
| `heavy` | **Heavy Monsoon Surge** | **1.50x** (+50%) | Active monsoon trough; sustained multi-day regional downpour. |
| `extreme` | **Extreme Cloudburst** | **2.20x** (+120%) | Regional catastrophic trigger equivalent to the August 2019 disaster event. |

Custom scenarios can also be simulated via arbitrary multiplier ($\alpha \in [0.1, 5.0]$) or explicit overrides for $R_{1D}$ and $R_{7D}$.

---

## 4. Scenario vs. Baseline Susceptibility Results

Evaluation across all 40 validated villages demonstrates a smooth, monotonic risk response:

| Scenario | Mean Village Susceptibility (0–100) | High Tier ($\ge 60$) Count | Medium Tier (30–59.9) Count | Low Tier ($< 30$) Count |
| :--- | :---: | :---: | :---: | :---: |
| **Moderate (0.70x)** | **50.43** | 12 | 23 | 5 |
| **Baseline (1.00x)** | **59.10** | 19 | 20 | 1 |
| **Heavy (1.50x)** | **65.49** | 25 | 15 | 0 |
| **Extreme (2.20x)** | **69.45** | 30 | 10 | 0 |

### Sample Village Trajectories:
- **Ebbanad 1 (Udhagai):** Moderate = `19.3` (Low) ➔ Baseline = `47.3` (Medium) ➔ Heavy = `50.3` (Medium) ➔ Extreme = `67.4` (High).
- **Cherangode1 (Pandalur):** Moderate = `46.7` (Medium) ➔ Baseline = `64.2` (High) ➔ Heavy = `64.2` (High) ➔ Extreme = `64.2` (High plateau due to dominant steep terrain).

---

## 5. Relative Demonstration Categorization

Scenario scores ($S_{\text{scen}} \in [0, 100]$) are categorized into relative visual tiers:
- **HIGH ($\ge 60.0$):** High susceptibility under the simulated precipitation regime.
- **MEDIUM ($30.0 - 59.9$):** Moderate susceptibility; requires compounding steep terrain.
- **LOW ($< 30.0$):** Relatively subdued susceptibility under the specified scenario.

> **Governance Notice:** High, Medium, and Low are relative display tiers intended for comparative spatial exploration. They do **not** represent official disaster management warning levels or evacuation triggers.

---

## 6. Scientific & Data Integrity Guarantees

1. **Zero Source Mutation:** `ml_spatial_dataset.csv`, `village_time_features.csv`, raw IMD NetCDFs, and SRTM DEMs remain completely unaltered.
2. **Deterministic Reproducibility:** Fixed model parameters and linear feature transforms ensure identical outputs across repeated runs.
3. **No Unlabeled Conversion:** Unlabeled villages ($s=0$) maintain their original `pu_status = UNLABELED` metadata in the output table.

---

## 7. Produced Artifacts

1. **Simulation Engine Script:** [pipeline/run_rainfall_scenario.py](file:///c:/Users/naife/Downloads/floodguard_v2/pipeline/run_rainfall_scenario.py)
2. **Scenario Results Dataset:** [data/processed/rainfall_scenario_results.csv](file:///c:/Users/naife/Downloads/floodguard_v2/data/processed/rainfall_scenario_results.csv) (160 rows: 40 villages $\times$ 4 preset scenarios)
3. **Unit Tests:** [tests/test_rainfall_scenario.py](file:///c:/Users/naife/Downloads/floodguard_v2/tests/test_rainfall_scenario.py)
