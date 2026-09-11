# FloodGuard

FloodGuard is a planned village/ward-level flood and landslide risk assessment system for hilly, high-risk regions. Nilgiris District, Tamil Nadu is the current demonstration region; it is not a limitation of the system design.

## Problem

Flash floods and landslides in hilly terrain can have very short warning times. Rainfall alone does not describe local risk: terrain and historical evidence also influence the vulnerability of a specific village or ward.

## Proposed solution

FloodGuard will combine traceable IMD gridded rainfall, public DEM-derived terrain features, and historical flood/landslide information from appropriate ISRO/NRSC/Bhuvan (and, where appropriate, GSI) sources. The resulting feature dataset will later support spatially validated machine-learning risk scoring and an interactive map. Rainfall scenario results will be clearly presented as simulations, not live observations.

## Architecture

```text
Raw data
  -> validation and provenance
  -> GIS processing / feature engineering
  -> model-ready feature table
  -> spatial validation and ML model
  -> FastAPI
  -> frontend risk map
```

The repository keeps these concerns separate:

- `backend/` — FastAPI application
- `frontend/` — static HTML, CSS, and JavaScript
- `data/` — raw, processed, demo, and source/provenance materials
- `pipeline/` — rainfall, terrain, events, and spatial processing
- `model/` — reproducible model artifacts (future phase)
- `tests/` and `docs/` — verification and supporting documentation

## Data sources (future pipeline)

- **Rainfall:** IMD gridded rainfall data
- **Terrain:** SRTM or another suitable public DEM, used for elevation and justified terrain features such as slope
- **Historical events:** ISRO/NRSC/Bhuvan flood and landslide information; GSI sources where appropriate
- **Boundaries:** reliable official or public administrative/geographical sources

No external datasets are downloaded or included in this foundation task. Each real dataset added later must include its provenance. When an official source cannot be ingested automatically, FloodGuard will document an ingestion interface instead of inventing data.

## Four development phases

1. **Foundation + data pipeline** — scaffold and documentation; reproducible rainfall, terrain, and event pipelines; a model-ready feature dataset. No ML model.
2. **ML + spatial validation** — target definition from real events, XGBoost training, spatial/group-based validation, metrics, and artifacts.
3. **Backend + dashboard** — model-backed APIs and a Leaflet-based dashboard using a public/OpenStreetMap-compatible basemap.
4. **Integration + hackathon ready** — end-to-end testing, UX improvements, provenance and validation checks, reproducible documentation, and demo preparation.

## Current foundation

The backend currently exposes a health endpoint only:

```text
GET /health -> {"status": "ok", "service": "FloodGuard API"}
```

The frontend is a deliberately minimal development page. It contains no map, datasets, scenarios, model, predictions, or mock risk values.

## Run locally (PowerShell)

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Then open `http://127.0.0.1:8000/health`. Run tests with:

```powershell
python -m pytest
```

Open `frontend/index.html` directly in a browser for the static development page.

## Limitations

FloodGuard is not an operational warning system. It does not currently use live rainfall, real datasets, GIS processing, an ML model, predictions, or a final risk dashboard. Future risk outputs must not be described as exact predictions or guaranteed warnings.
