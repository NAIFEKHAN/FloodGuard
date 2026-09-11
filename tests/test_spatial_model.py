"""Tests for Phase A Spatial Susceptibility Machine Learning artifacts and validation."""

from pathlib import Path
import json
import pandas as pd
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data/processed"
MODEL_DIR = ROOT / "model/artifacts"


def test_spatial_dataset_structure_and_integrity() -> None:
    dataset_path = DATA_PROCESSED / "ml_spatial_dataset.csv"
    assert dataset_path.exists(), "ml_spatial_dataset.csv does not exist"

    df = pd.read_csv(dataset_path)
    assert len(df) == 40, f"Expected exactly 40 village records, got {len(df)}"
    assert df["village_lgd_code"].nunique() == 40, "Village LGD codes must be unique"
    assert (df["label_s"] == 1).sum() == 25, "Expected 25 positive villages"
    assert (df["label_s"] == 0).sum() == 15, "Expected 15 unlabeled villages"
    assert df["taluk_name_en"].nunique() == 6, "Expected 6 taluk groups"
    assert not df.isnull().any().any(), "Dataset must not contain null values"


def test_spatial_model_artifact_loading_and_scoring() -> None:
    model_path = MODEL_DIR / "spatial_susceptibility_xgboost.json"
    assert model_path.exists(), "spatial_susceptibility_xgboost.json does not exist"

    model = XGBClassifier()
    model.load_model(str(model_path))

    dataset_path = DATA_PROCESSED / "ml_spatial_dataset.csv"
    df = pd.read_csv(dataset_path)

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

    preds = model.predict_proba(df[feature_cols].values)[:, 1]
    assert len(preds) == 40, "Predictions count must match 40 villages"
    assert (preds >= 0.0).all() and (preds <= 1.0).all(), "Predictions must be in [0, 1]"


def test_spatial_validation_metrics_exist_and_meet_thresholds() -> None:
    metrics_path = MODEL_DIR / "spatial_validation_metrics.json"
    assert metrics_path.exists(), "spatial_validation_metrics.json does not exist"

    data = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert data["gate_status"] == "CONDITIONAL_ML"
    assert data["sample_size"] == 40
    assert data["labeled_positive_count"] == 25
    assert data["unlabeled_count"] == 15
    assert data["negative_labels_created"] == 0

    xgb_metrics = data["model_comparison"]["pu_xgboost"]
    assert xgb_metrics["loto_roc_auc"] >= 0.80, f"Expected ROC-AUC >= 0.80, got {xgb_metrics['loto_roc_auc']}"
    assert xgb_metrics["loto_pr_auc"] >= 0.85, f"Expected PR-AUC >= 0.85, got {xgb_metrics['loto_pr_auc']}"
