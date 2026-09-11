# FloodGuard project guidance

## Scope and architecture

FloodGuard is a village/ward-level flood and landslide risk assessment system for hilly, high-risk regions. Nilgiris District, Tamil Nadu is the current demonstration region only; all region-specific inputs must be configurable so additional regions can be supported without core rewrites.

The project structure separates the FastAPI service (`backend/`), browser client (`frontend/`), source and processed data (`data/`), reproducible data pipelines (`pipeline/`), model artifacts (`model/`), tests, and documentation.

The intended flow is:

`raw data -> validation -> GIS processing -> feature engineering -> feature table -> spatial validation -> model -> FastAPI -> frontend map`

## Four-phase development plan

1. **Foundation + data pipeline:** project foundation; terrain, rainfall, and historical-event ingestion/processing; provenance; and a model-ready feature table. No ML model.
2. **ML + spatial validation:** define a target from real event data, train XGBoost, validate using spatial/group-based splits, and save reproducible artifacts.
3. **Backend + dashboard:** integrate the trained model into FastAPI and a Leaflet dashboard using a public/OpenStreetMap-compatible basemap.
4. **Integration + hackathon ready:** end-to-end verification, provenance and validation review, UX/error handling, documentation, and demo preparation.

Only perform work explicitly requested for the active phase. Do not begin later phases automatically.

## Data integrity rules

- Never fabricate official data or historical flood/landslide events.
- Preserve source and provenance documentation for every real dataset.
- If an official dataset is unavailable for automated download, implement a documented ingestion interface rather than a fabricated substitute.
- Any development sample must be explicitly labelled `DEMO`; it must never be presented as official or live data.
- Rainfall scenarios are simulations and must always be labelled **Rainfall Scenario**, never live rainfall.
- Do not silently fall back to fake data and do not hide errors.

## Modelling and product rules

- Do not implement ML until Phase 2 and do not hard-code predictions in the frontend.
- Use actual features only (for example rainfall, antecedent rainfall, elevation, slope, and validated historical evidence).
- Use spatial/group-based validation, such as leave-one-taluk-out where appropriate; do not rely only on random splits.
- Do not claim exact flood prediction, guaranteed warnings, or real-time capability without a verified live source.
- The base map must not depend on Mapbox or another API-key map provider.
- Keep ESP32 soil-moisture integration optional and outside the core system.
