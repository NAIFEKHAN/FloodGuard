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
def get_status() -> dict[str, str]:
    return {"ml_status": "PENDING_VALIDATION", "reason": "No complete reconciled modelling-unit geometry, event CRS/datum, or non-event observation frame.", "risk_scores": "NOT_AVAILABLE"}
