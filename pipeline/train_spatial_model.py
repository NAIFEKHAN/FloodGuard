"""Pipeline script to build the spatial ML dataset and train the spatial susceptibility model.

Uses a Positive-Unlabeled (PU) spatial learning formulation with Leave-One-Taluk-Out (LOTO)
spatial cross-validation across the 6 Nilgiris taluks.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data/processed"
MODEL_DIR = ROOT / "model/artifacts"


def build_spatial_dataset() -> pd.DataFrame:
    """Aggregate terrain and historical rainfall features for the 40 validated villages."""
    tf_path = DATA_PROCESSED / "terrain_features_villages.csv"
    vtf_path = DATA_PROCESSED / "village_time_features.csv"
    ev_path = DATA_PROCESSED / "experimental_hazard_index.csv"
    vm_path = DATA_PROCESSED / "nilgiris_villages.csv"

    tf = pd.read_csv(tf_path)
    vtf = pd.read_csv(vtf_path)
    ev = pd.read_csv(ev_path)
    vm = pd.read_csv(vm_path)

    # 1. Aggregate 5-year historical rainfall features per village
    rain_agg = vtf.groupby("village_lgd_code").agg(
        rainfall_7d_p95_mm=("rainfall_7d_mm", lambda x: float(np.nanpercentile(x, 95))),
        rainfall_3d_p95_mm=("rainfall_3d_mm", lambda x: float(np.nanpercentile(x, 95))),
        rainfall_1d_max_mm=("rainfall_1d_mm", "max"),
        rainfall_annual_mean_mm=("rainfall_1d_mm", lambda x: float(x.sum() / 5.0)),
    ).reset_index()

    # 2. Merge terrain summaries
    df = tf[
        [
            "village_lgd_code",
            "district_lgd_code",
            "taluk_lgd_code",
            "village_name_en",
            "elevation_mean_m",
            "elevation_min_m",
            "elevation_max_m",
            "slope_mean_deg",
            "slope_max_deg",
        ]
    ].merge(rain_agg, on="village_lgd_code")

    df["elevation_range_m"] = df["elevation_max_m"] - df["elevation_min_m"]

    # 3. Merge event evidence, baseline hazard index, and administrative taluk names
    df = df.merge(
        ev[["village_lgd_code", "conditional_strict_linked_event_count", "experimental_hazard_index_0_100"]],
        on="village_lgd_code",
    )
    df = df.merge(
        vm[["village_lgd_code", "taluk_name_en"]].drop_duplicates(),
        on="village_lgd_code",
        how="left",
    )

    # 4. Define PU target: 1 = Labeled Positive (has GSI event evidence), 0 = Unlabeled (no recorded event)
    df["label_s"] = (df["conditional_strict_linked_event_count"] > 0).astype(int)
    df["pu_status"] = np.where(df["label_s"] == 1, "POSITIVE", "UNLABELED")

    # 5. Add Provenance
    df["terrain_feature_source"] = "data/processed/terrain_features_villages.csv (SRTM 30m DEM)"
    df["rainfall_feature_source"] = "data/processed/village_time_features.csv (IMD 0.25deg gridded 2017,2019,2022-2024)"
    df["event_evidence_source"] = "data/processed/event_village_linkage.csv (GSI/NLFC National Inventory)"
    df["boundary_source"] = "data/raw/admin/vb_soi_tn.kmz (40 exact LGD polygon matches)"

    # Validation checks
    assert len(df) == 40, f"Expected 40 village records, got {len(df)}"
    assert df["village_lgd_code"].nunique() == 40, "Duplicate village LGD codes found"
    assert (df["label_s"] == 1).sum() == 25, f"Expected 25 positive villages, got {(df['label_s'] == 1).sum()}"
    assert (df["label_s"] == 0).sum() == 15, f"Expected 15 unlabeled villages, got {(df['label_s'] == 0).sum()}"
    assert df["taluk_name_en"].nunique() == 6, f"Expected 6 taluks, got {df['taluk_name_en'].nunique()}"
    assert not df.isnull().any().any(), "Unexpected missing values in spatial dataset"

    return df


def train_and_evaluate_spatial_models(df: pd.DataFrame) -> dict[str, object]:
    """Train models using 6-fold Leave-One-Taluk-Out (LOTO) spatial cross-validation."""
    feature_cols = [
        "elevation_mean_m",
        "elevation_range_m",
        "slope_mean_deg",
        "slope_max_deg",
        "rainfall_7d_p95_mm",
        "rainfall_3d_p95_mm",
        "rainfall_1d_max_mm",
        "rainfall_annual_mean_mm",
    ]

    taluks = sorted(df["taluk_name_en"].unique())
    y_true = df["label_s"].values

    models = {
        "pu_logistic_regression": {
            "name": "PU-Weighted Logistic Regression",
            "oof_preds": np.zeros(len(df)),
        },
        "pu_random_forest": {
            "name": "PU-Weighted Random Forest",
            "oof_preds": np.zeros(len(df)),
        },
        "pu_xgboost": {
            "name": "PU-Weighted XGBoost Classifier",
            "oof_preds": np.zeros(len(df)),
        },
    }

    fold_details = []

    for fold_idx, holdout_taluk in enumerate(taluks, 1):
        train_mask = (df["taluk_name_en"] != holdout_taluk).values
        test_mask = (df["taluk_name_en"] == holdout_taluk).values

        X_train = df.loc[train_mask, feature_cols].values
        y_train = df.loc[train_mask, "label_s"].values
        X_test = df.loc[test_mask, feature_cols].values
        y_test = df.loc[test_mask, "label_s"].values

        # Compute PU sample weights: positive instances = 1.0, unlabeled instances = n_pos / n_unl
        n_pos = int(np.sum(y_train == 1))
        n_unl = int(np.sum(y_train == 0))
        w_unl = float(n_pos / max(n_unl, 1))
        sample_weights = np.where(y_train == 1, 1.0, w_unl)

        # Standardize features for linear model
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        # 1. PU Logistic Regression
        m_lr = LogisticRegression(C=0.5, random_state=42, max_iter=200)
        m_lr.fit(X_train_s, y_train, sample_weight=sample_weights)
        models["pu_logistic_regression"]["oof_preds"][test_mask] = m_lr.predict_proba(X_test_s)[:, 1]

        # 2. PU Random Forest
        m_rf = RandomForestClassifier(n_estimators=50, max_depth=2, random_state=42)
        m_rf.fit(X_train, y_train, sample_weight=sample_weights)
        models["pu_random_forest"]["oof_preds"][test_mask] = m_rf.predict_proba(X_test)[:, 1]

        # 3. PU XGBoost
        m_xgb = XGBClassifier(
            n_estimators=35,
            max_depth=2,
            learning_rate=0.08,
            random_state=42,
            eval_metric="logloss",
        )
        m_xgb.fit(X_train, y_train, sample_weight=sample_weights)
        models["pu_xgboost"]["oof_preds"][test_mask] = m_xgb.predict_proba(X_test)[:, 1]

        fold_details.append(
            {
                "fold": fold_idx,
                "holdout_taluk": holdout_taluk,
                "train_samples": int(np.sum(train_mask)),
                "test_samples": int(np.sum(test_mask)),
                "test_positives": int(np.sum(y_test == 1)),
                "test_unlabeled": int(np.sum(y_test == 0)),
            }
        )

    # Compute overall out-of-fold metrics
    metrics = {}
    for m_key, m_info in models.items():
        preds = m_info["oof_preds"]
        roc_auc = float(roc_auc_score(y_true, preds))
        pr_auc = float(average_precision_score(y_true, preds))
        brier = float(brier_score_loss(y_true, preds))

        metrics[m_key] = {
            "model_name": m_info["name"],
            "loto_roc_auc": round(roc_auc, 4),
            "loto_pr_auc": round(pr_auc, 4),
            "loto_brier_score": round(brier, 4),
        }

    # Train Final Production Model on all 40 villages
    total_pos = int(np.sum(y_true == 1))
    total_unl = int(np.sum(y_true == 0))
    full_weights = np.where(y_true == 1, 1.0, float(total_pos / total_unl))

    final_xgb = XGBClassifier(
        n_estimators=35,
        max_depth=2,
        learning_rate=0.08,
        random_state=42,
        eval_metric="logloss",
    )
    final_xgb.fit(df[feature_cols].values, y_true, sample_weight=full_weights)

    feature_importances = {
        feat: round(float(imp), 4)
        for feat, imp in zip(feature_cols, final_xgb.feature_importances_)
    }

    # Generate model susceptibility scores (0-100 scale)
    final_preds = final_xgb.predict_proba(df[feature_cols].values)[:, 1]
    df["ml_susceptibility_raw"] = final_preds
    df["ml_susceptibility_0_100"] = np.round(final_preds * 100.0, 2)
    df["ml_loto_oof_score_0_100"] = np.round(models["pu_xgboost"]["oof_preds"] * 100.0, 2)

    return {
        "features": feature_cols,
        "metrics": metrics,
        "fold_details": fold_details,
        "feature_importances": feature_importances,
        "scored_df": df,
        "final_model": final_xgb,
    }


def main() -> None:
    """Build dataset, run spatial cross-validation, and serialize artifacts."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print("Building spatial ML dataset for 40 validated villages...")
    df = build_spatial_dataset()

    dataset_out = DATA_PROCESSED / "ml_spatial_dataset.csv"
    df.to_csv(dataset_out, index=False)
    print(f"Saved: {dataset_out}")

    print("\nRunning Leave-One-Taluk-Out (LOTO) Spatial Validation...")
    results = train_and_evaluate_spatial_models(df)

    scored_df = results["scored_df"]
    scores_out = DATA_PROCESSED / "ml_village_susceptibility_scores.csv"
    scored_df[
        [
            "village_lgd_code",
            "taluk_name_en",
            "village_name_en",
            "pu_status",
            "conditional_strict_linked_event_count",
            "ml_loto_oof_score_0_100",
            "ml_susceptibility_0_100",
            "experimental_hazard_index_0_100",
        ]
    ].to_csv(scores_out, index=False)
    print(f"Saved: {scores_out}")

    # Save Final XGBoost Model in JSON format
    model_json_path = MODEL_DIR / "spatial_susceptibility_xgboost.json"
    results["final_model"].save_model(str(model_json_path))
    print(f"Saved: {model_json_path}")

    # Save Validation Report JSON
    metadata = {
        "gate_status": "CONDITIONAL_ML",
        "formulation": "Positive-Unlabeled (PU) Spatial Village Susceptibility",
        "sample_size": 40,
        "labeled_positive_count": 25,
        "unlabeled_count": 15,
        "negative_labels_created": 0,
        "spatial_validation_method": "6-Fold Leave-One-Taluk-Out (LOTO) GroupKFold",
        "taluk_groups": ["Kotagiri", "Udhagai", "Kundah", "Pandalur", "Coonoor", "Gudalur"],
        "features": results["features"],
        "feature_importances": results["feature_importances"],
        "model_comparison": results["metrics"],
        "fold_details": results["fold_details"],
        "governance_note": "Scores represent spatial demonstration susceptibility ranking, not live operational flood/landslide predictions or calibrated probabilities.",
    }

    metrics_out = MODEL_DIR / "spatial_validation_metrics.json"
    metrics_out.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved: {metrics_out}")

    print("\n=== LOTO Spatial Validation Summary ===")
    for k, v in results["metrics"].items():
        print(f"{v['model_name']}: ROC-AUC={v['loto_roc_auc']}, PR-AUC={v['loto_pr_auc']}, Brier={v['loto_brier_score']}")
    print("\nFeature Importances:")
    for f, imp in results["feature_importances"].items():
        print(f"  {f}: {imp * 100:.1f}%")


if __name__ == "__main__":
    main()
