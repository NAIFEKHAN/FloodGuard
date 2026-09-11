# Phase A: Conditional Spatial Susceptibility Machine Learning Resolution

**Phase:** A — Conditional Spatial Susceptibility ML  
**Decision Gate:** **CONDITIONAL_ML** (Approved under strict Positive-Unlabeled and Leave-One-Taluk-Out spatial validation rules)  
**Modelling Universe:** Exactly 40 validated Nilgiris village polygons  

---

## 1. Executive Summary

In adherence to the findings of Phase A1 and FloodGuard data integrity rules:
- **Daily supervised time-series ML remains BLOCKED** due to the absence of an exhaustive daily non-event surveillance register (which would require fabricating 73,020 negative labels).
- **Spatial village-level susceptibility modeling is CONDITIONALLY DEFENSIBLE** when formulated under a **Positive-Unlabeled (PU) spatial learning framework** evaluated with strict **Leave-One-Taluk-Out (LOTO) spatial cross-validation**.

This resolution documents the mathematical formulation, dataset construction, spatial cross-validation across the 6 Nilgiris administrative taluks, model comparison (PU Logistic Regression, PU Random Forest, and PU XGBoost), feature importances, leakage controls, and operational disclaimers.

---

## 2. Evidence Base & Dataset Construction

The spatial ML dataset (`data/processed/ml_spatial_dataset.csv`) is built strictly from the 40 validated village polygons with no external or synthetic samples:

### 2.1 Spatial Units & Identifiers
- Exactly 40 unique village polygons reconciled with three-code authoritative matching: `village_lgd_code`, `district_lgd_code = 587`, and `taluk_lgd_code` across 6 taluks.
- Residual records (62 Village Master-only and 18 KMZ-only) remain excluded without nearest-neighbor or fuzzy imputation.

### 2.2 Input Features (8 Engineered Predictors)
1. **Topographic Features (SRTM 30m DEM):**
   - `elevation_mean_m`: Zonal mean elevation (m)
   - `elevation_range_m`: Relief / elevation span within polygon ($E_{\max} - E_{\min}$)
   - `slope_mean_deg`: Zonal mean slope (degrees)
   - `slope_max_deg`: Maximum steepness within polygon (degrees)
2. **Meteorological Features (IMD 0.25° Gridded 2017, 2019, 2022–2024):**
   - `rainfall_7d_p95_mm`: Historical 95th-percentile of 7-day trailing rainfall (chronic saturation threshold)
   - `rainfall_3d_p95_mm`: Historical 95th-percentile of 3-day trailing rainfall
   - `rainfall_1d_max_mm`: Maximum single-day rainfall intensity observed across 5 years
   - `rainfall_annual_mean_mm`: 5-year average annual cumulative rainfall

### 2.3 Positive-Unlabeled (PU) Target Formulation
- **Labeled Positives ($s = 1$):** **25 villages** with verified historical landslide occurrence from official GSI/NLFC inventory records strictly contained within the polygon boundary (totaling 349 contained events).
- **Unlabeled ($s = 0$):** **15 villages** with zero recorded GSI events in the inventory.
- **Zero Negative Fabrication:** The 15 unlabeled villages are explicitly designated as `UNLABELED` (not certified safe / not $y=0$). In PU learning loss functions, unlabeled samples receive a calibrated sample weight $w_U = \frac{N_{\text{pos}}}{N_{\text{unl}}}$ rather than being treated as true negatives.

---

## 3. Spatial Validation Strategy (Mandatory Protocol)

Standard random train/test splits (e.g. `train_test_split`) are **strictly prohibited** because spatial autocorrelation across adjacent village polygons sharing identical 0.25° IMD grid cells and continuous mountain terrain would cause severe optimistic bias.

### Leave-One-Taluk-Out (LOTO) 6-Fold Group Validation:
The dataset is partitioned into 6 spatial folds corresponding to the 6 Nilgiris administrative taluks:

| Fold | Holdout Taluk | Total Villages | Labeled Positives ($s=1$) | Unlabeled ($s=0$) | Training Set Size |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | **Kotagiri** | 14 | 7 | 7 | 26 villages |
| **2** | **Udhagai (Udhagamandalam)** | 10 | 7 | 3 | 30 villages |
| **3** | **Kundah** | 5 | 5 | 0 | 35 villages |
| **4** | **Pandalur** | 4 | 2 | 2 | 36 villages |
| **5** | **Coonoor** | 4 | 4 | 0 | 36 villages |
| **6** | **Gudalur** | 3 | 0 | 3 | 37 villages |
| **Total** | **6 Taluks** | **40** | **25 (62.5%)** | **15 (37.5%)** | **All 40 Out-of-Fold** |

In each fold, the model is trained entirely on the other 5 taluks and evaluated exclusively on the held-out taluk. Every single village receives an out-of-fold prediction when its entire geographic district is completely withheld.

---

## 4. Model Comparison & Validation Results

Three model architectures were trained and evaluated on out-of-fold spatial predictions:

| Model Architecture | Formulation / Hyperparameters | Out-of-Fold ROC-AUC | Out-of-Fold PR-AUC | Brier Loss Score |
| :--- | :--- | :---: | :---: | :---: |
| **PU Logistic Regression** | Standardized linear, $L_2$ reg ($C=0.5$), PU weights | **0.8347** | **0.8939** | **0.1588** |
| **PU Random Forest** | 50 trees, `max_depth=2`, PU sample weights | **0.8720** | **0.9301** | **0.1623** |
| **PU XGBoost Classifier** | 35 trees, `max_depth=2`, $\eta=0.08$, PU weights | **0.8747** | **0.9426** | **0.1766** |

### Selected Primary Model: PU-Weighted XGBoost
- **LOTO Out-of-Fold PR-AUC:** **0.9426** (high precision in ranking verified susceptible zones)
- **LOTO Out-of-Fold ROC-AUC:** **0.8747** (strong discriminative ability across unseen geographic clusters)

### Feature Importance Breakdown (XGBoost):
1. `elevation_mean_m` (**57.2%**): Identifies the elevated plateau and escarpment zone as the primary structural susceptibility domain.
2. `rainfall_7d_p95_mm` (**16.5%**): Captures persistent, high-volume multi-day monsoon antecedent saturation.
3. `slope_mean_deg` (**11.4%**): Steep terrain gravitational shear stress.
4. `rainfall_1d_max_mm` (**8.2%**): Extreme cloudburst / single-day trigger intensity.
5. `slope_max_deg` (**6.7%**): Localized cliff / scarp presence.

---

## 5. Leakage Prevention Checks

| Leakage Risk | Mitigation Implemented | Validation Status |
| :--- | :--- | :---: |
| **Spatial Autocorrelation** | Full taluk-level spatial holdouts (LOTO); no neighboring village in train & test simultaneously | **PASSED** |
| **Temporal Lookahead** | Features derived strictly from 5-year historical aggregates | **PASSED** |
| **Label Leakage** | Historical event counts excluded from feature matrix; used only as target evidence $s$ | **PASSED** |
| **Multi-Event Row Inflation** | Dataset aggregated to 1 row per village polygon ($N=40$) | **PASSED** |
| **Negative Fabrication** | $s=0$ villages weighted as Unlabeled under PU loss; never labeled $y=0$ | **PASSED** |

---

## 6. Generated Project Artifacts

1. **Spatial ML Dataset:** [data/processed/ml_spatial_dataset.csv](file:///c:/Users/naife/Downloads/floodguard_v2/data/processed/ml_spatial_dataset.csv) (40 rows, 8 features, target, provenance)
2. **Model Predictions Table:** [data/processed/ml_village_susceptibility_scores.csv](file:///c:/Users/naife/Downloads/floodguard_v2/data/processed/ml_village_susceptibility_scores.csv) (LOTO out-of-fold and calibrated susceptibility scores)
3. **Reproducible Training Pipeline:** [pipeline/train_spatial_model.py](file:///c:/Users/naife/Downloads/floodguard_v2/pipeline/train_spatial_model.py)
4. **Trained Model JSON:** [model/artifacts/spatial_susceptibility_xgboost.json](file:///c:/Users/naife/Downloads/floodguard_v2/model/artifacts/spatial_susceptibility_xgboost.json)
5. **Spatial Validation Metadata:** [model/artifacts/spatial_validation_metrics.json](file:///c:/Users/naife/Downloads/floodguard_v2/model/artifacts/spatial_validation_metrics.json)

---

## 7. Mandatory Governance & Operational Disclaimers

1. **Not a Live Warning System:** Model scores represent static **spatial terrain and climatological susceptibility**, not a real-time landslide warning or flood prediction.
2. **Positive-Unlabeled Caveat:** A low or zero susceptibility score in an unlabeled village reflects an absence of recorded GSI inventory evidence, not guaranteed immunity.
3. **No Operational Extrapolation:** The model is calibrated specifically for the 40 validated Nilgiris polygons and must not be extrapolated to unvalidated regions without authoritative spatial boundaries.
