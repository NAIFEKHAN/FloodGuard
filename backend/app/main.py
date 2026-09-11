"""Evidence-only FastAPI service for the FloodGuard demonstration dashboard."""

from __future__ import annotations

import csv
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
FRONTEND = ROOT / "frontend"

app = FastAPI(title="FloodGuard Evidence Dashboard API", version="0.3.0")
app.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")
app.mount("/data", StaticFiles(directory=DATA), name="data")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@lru_cache(maxsize=1)
def villages() -> list[dict[str, str]]:
    return read_csv(DATA / "processed/nilgiris_villages.csv")


@lru_cache(maxsize=1)
def rainfall() -> list[dict[str, str]]:
    return read_csv(DATA / "processed/historical_rainfall_features.csv")


@lru_cache(maxsize=1)
def terrain() -> list[dict[str, str]]:
    return read_csv(DATA / "processed/terrain_features.csv")


@lru_cache(maxsize=1)
def events() -> list[dict[str, str]]:
    return read_csv(DATA / "processed/landslide_events.csv")


@lru_cache(maxsize=1)
def experimental_hazard_index() -> list[dict[str, str]]:
    rows = read_csv(DATA / "processed/experimental_hazard_index.csv")
    if len(rows) != 40 or len({row["village_lgd_code"] for row in rows}) != 40:
        raise RuntimeError("Experimental hazard-index artifact must contain exactly 40 unique validated villages.")
    return rows


@lru_cache(maxsize=1)
def ddmp_manifest() -> dict[str, object]:
    return json.loads((DATA / "processed/disaster/ddmp_evidence_manifest.json").read_text(encoding="utf-8"))


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "FloodGuard API"}


@app.get("/api/villages")
def get_villages(limit: int = Query(default=102, ge=1, le=102)) -> dict[str, object]:
    rows = villages()
    return {"classification": "REAL_ADMINISTRATIVE_RECORDS_NOT_MODELLING_UNITS", "record_count": len(rows), "exact_spatial_matches": 40, "village_master_only": 62, "kmz_only": 18, "records": rows[:limit]}


@app.get("/api/rainfall/summary")
def rainfall_summary() -> dict[str, object]:
    rows = rainfall()
    by_year = Counter(row["date"][:4] for row in rows)
    return {"classification": "REAL_IMD_DERIVED_FOR_DEMO_SETTLEMENTS_ONLY", "record_count": len(rows), "years": [{"year": year, "record_count": by_year[year]} for year in sorted(by_year)], "rolling_nulls": {"three_day": 20, "seven_day": 60}, "imputation": "none"}


@app.get("/api/rainfall")
def get_rainfall(year: int = Query(..., ge=2017, le=2024)) -> dict[str, object]:
    rows = [row for row in rainfall() if row["date"].startswith(f"{year}-")]
    if not rows:
        raise HTTPException(status_code=404, detail="No validated local rainfall source for that year.")
    return {"year": year, "classification": "DEMO_SETTLEMENT_FEATURES", "records": rows}


@app.get("/api/terrain")
def get_terrain() -> dict[str, object]:
    return {"classification": "REAL_SRTM_DERIVED_FOR_DEMO_SETTLEMENTS_ONLY", "records": terrain()}


@app.get("/api/events")
def get_events() -> dict[str, object]:
    rows = events()
    categories = Counter("explicit" if row["reported_history_date"] else "year_only" if row["history_raw"].strip().isdigit() else "na" if row["history_raw"].strip().upper() == "NA" else "ambiguous" for row in rows)
    return {"classification": "REAL_GSI_NLFC_STANDALONE_INVENTORY", "record_count": len(rows), "date_categories": categories, "records": rows, "warning": "Records are independent evidence points, not village assignments or model labels."}


@app.get("/api/ddmp")
def get_ddmp() -> dict[str, object]:
    return {"classification": "OFFICIAL_DDMP_DOCUMENTARY_EVIDENCE_NOT_ML_LABELS", "manifest": ddmp_manifest(), "arg_stations": read_csv(DATA / "processed/disaster/ddmp_proposed_arg_stations.csv"), "aws_stations": read_csv(DATA / "processed/disaster/ddmp_aws_stations.csv"), "vulnerability_summary": read_csv(DATA / "processed/disaster/ddmp_vulnerable_location_summary.csv")}


@app.get("/api/experimental-hazard-index")
def get_experimental_hazard_index() -> dict[str, object]:
    """Return the fixed Phase 8 descriptive index without recalculation or inference."""
    rows = experimental_hazard_index()
    return {
        "classification": "EXPERIMENTAL_HAZARD_INDEX_NOT_ML_NOT_A_PREDICTION",
        "record_count": len(rows),
        "warning": "A relative, fixed-method demonstration index for 40 validated villages only; not a prediction, probability, warning, label, or calibrated risk score.",
        "records": rows,
    }


@app.get("/api/status")
def get_status() -> dict[str, object]:
    return {
        "ml_status": "CONDITIONAL_SPATIAL_SUSCEPTIBILITY_MODEL",
        "model_type": "Positive-Unlabeled (PU) Spatial XGBoost",
        "validation": "6-Fold Leave-One-Taluk-Out (LOTO) Group Cross-Validation",
        "loto_roc_auc": 0.8747,
        "loto_pr_auc": 0.9426,
        "susceptibility_scores": "AVAILABLE",
        "scenario_engine": "AVAILABLE",
        "warning": "Demonstration spatial susceptibility ranking, not live operational flood/landslide predictions or calibrated probabilities.",
    }


@lru_cache(maxsize=1)
def spatial_dataset() -> list[dict[str, str]]:
    rows = read_csv(DATA / "processed/ml_spatial_dataset.csv")
    if len(rows) != 40:
        raise RuntimeError("Spatial ML dataset must contain exactly 40 unique validated villages.")
    return rows


@lru_cache(maxsize=1)
def ml_model():
    from xgboost import XGBClassifier
    model_path = ROOT / "model/artifacts/spatial_susceptibility_xgboost.json"
    if not model_path.exists():
        raise RuntimeError(f"Model artifact not found at {model_path}")
    model = XGBClassifier()
    model.load_model(str(model_path))
    return model


@app.get("/api/ml-susceptibility")
def get_ml_susceptibility() -> dict[str, object]:
    """Return the Phase A Spatial Susceptibility model scores and evidence for 40 validated villages."""
    rows = read_csv(DATA / "processed/ml_village_susceptibility_scores.csv")
    if len(rows) != 40:
        raise RuntimeError("ML village susceptibility table must contain exactly 40 validated villages.")
    
    pos_count = sum(1 for r in rows if r["pu_status"] == "POSITIVE")
    unl_count = sum(1 for r in rows if r["pu_status"] == "UNLABELED")

    return {
        "classification": "SPATIAL_VILLAGE_SUSCEPTIBILITY_PU_MODEL",
        "record_count": len(rows),
        "labeled_positive_count": pos_count,
        "unlabeled_count": unl_count,
        "spatial_validation": "6-Fold Leave-One-Taluk-Out (LOTO)",
        "metrics": {"loto_roc_auc": 0.8747, "loto_pr_auc": 0.9426, "loto_brier_score": 0.1766},
        "warning": "Demonstration spatial susceptibility ranking; not a real-time warning, evacuation trigger, or calibrated flood probability.",
        "records": rows,
    }


@app.get("/api/rainfall-scenario")
def get_rainfall_scenario(
    scenario: str = Query(default="baseline", description="Preset scenario (moderate, baseline, heavy, extreme, custom)"),
    multiplier: float | None = Query(default=None, ge=0.1, le=5.0, description="Custom rainfall multiplier (0.1 to 5.0)"),
    r1d: float | None = Query(default=None, ge=0.0, le=500.0, description="Custom 1-day rainfall override (mm)"),
    r7d: float | None = Query(default=None, ge=0.0, le=1500.0, description="Custom 7-day rainfall override (mm)"),
) -> dict[str, object]:
    """Execute dynamic non-destructive rainfall scenario simulation over the 40 validated villages."""
    from pipeline.run_rainfall_scenario import evaluate_scenario, PRESET_SCENARIOS
    import pandas as pd

    model = ml_model()
    df_raw = pd.DataFrame(spatial_dataset())
    
    # Cast numeric feature columns
    num_cols = [
        "elevation_mean_m", "elevation_range_m", "slope_mean_deg", "slope_max_deg",
        "rainfall_7d_p95_mm", "rainfall_3d_p95_mm", "rainfall_1d_max_mm", "rainfall_annual_mean_mm"
    ]
    for c in num_cols:
        df_raw[c] = df_raw[c].astype(float)

    results_df = evaluate_scenario(
        df_raw,
        model,
        scenario_key=scenario,
        multiplier=multiplier,
        custom_rainfall_1d_mm=r1d,
        custom_rainfall_7d_mm=r7d,
    )

    records = results_df.to_dict(orient="records")
    tier_counts = Counter(r["scenario_tier"] for r in records)

    scenario_name = PRESET_SCENARIOS.get(scenario, {}).get("name", f"Custom ({multiplier or 1.0}x)")
    factor = multiplier if multiplier is not None else PRESET_SCENARIOS.get(scenario, {}).get("multiplier", 1.0)

    return {
        "classification": "RAINFALL_SCENARIO_DEMONSTRATION_SIMULATION",
        "scenario_key": scenario,
        "scenario_name": scenario_name,
        "rainfall_factor": factor,
        "record_count": len(records),
        "high_tier_count": tier_counts.get("HIGH", 0),
        "medium_tier_count": tier_counts.get("MEDIUM", 0),
        "low_tier_count": tier_counts.get("LOW", 0),
        "warning": "Demonstration scenario output under simulated precipitation; not a live forecast, official alert, or evacuation instruction.",
        "records": records,
    }

