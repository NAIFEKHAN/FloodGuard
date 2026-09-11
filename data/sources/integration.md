# Phase 1 integration provenance

`pipeline/build_integration.py` creates `data/processed/settlement_daily_features.csv` and `data/processed/integration_provenance.json` from the existing processed artifacts. It does not download data and does not alter the SRTM tiles/mosaic, IMD NetCDF, supplied PDF, or their existing processed CSVs.

## Permitted integration

The output is a 2024 daily table created by an exact `settlement_id` join between:

- `terrain_features.csv`: real SRTM-derived elevation and slope at the two existing **DEMO** settlement coordinates.
- `rainfall_features.csv`: real IMD daily/rolling rainfall selected at those same two **DEMO** settlement coordinates.

It contains one row per existing settlement-date observation. `settlement_input_classification=DEMO`; terrain and rainfall source-classification fields explicitly identify their real sources. The table is derived data, not an official settlement dataset, prediction, score, warning, target, or ML label table.

## Event inventory boundary

`landslide_events.csv` is a 772-row **REAL** supplied GSI/NLFC inventory. The integration script validates it and records its file hash, record count, and coordinate-validation report in `integration_provenance.json`. It deliberately does **not** put event rows into the settlement-day table and does not create an event-to-settlement relationship.

No distance threshold, geocoding, date inference, rainfall association, label, score, or prediction is used. The real event coordinates and original source fields remain solely in `landslide_events.csv`.

## Reproducibility and validation

Run from the repository root:

```powershell
python pipeline/build_integration.py
```

The script requires the complete source schemas; validates settlement identity equality, geographic coordinate ranges, finite terrain and required daily-rainfall values, unique settlement-date records, valid IMD-grid coordinates, and the standalone event-coordinate checks. The known leading nulls in 3-day and 7-day rainfall totals are retained, never filled. Output ordering is stable by `settlement_id`, then date. SHA-256 hashes in the provenance JSON identify the exact processed inputs used.
