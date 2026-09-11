"""Build a settlement-day feature table without creating event associations."""

from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pandas as pd

try:  # Supports both ``python -m pipeline...`` and existing script entry points.
    from pipeline.events.processing import OUTPUT_COLUMNS as EVENT_COLUMNS
    from pipeline.events.processing import validate_events
    from pipeline.rainfall.processing import OUTPUT_COLUMNS as RAINFALL_COLUMNS
    from pipeline.terrain.processing import REQUIRED_SETTLEMENT_COLUMNS
except ModuleNotFoundError:  # pragma: no cover - exercised by the CLI process.
    from events.processing import OUTPUT_COLUMNS as EVENT_COLUMNS
    from events.processing import validate_events
    from rainfall.processing import OUTPUT_COLUMNS as RAINFALL_COLUMNS
    from terrain.processing import REQUIRED_SETTLEMENT_COLUMNS

TERRAIN_COLUMNS = (*REQUIRED_SETTLEMENT_COLUMNS, "elevation_m", "slope_deg")
IDENTITY_COLUMNS = (*REQUIRED_SETTLEMENT_COLUMNS,)
OUTPUT_COLUMNS = (
    *IDENTITY_COLUMNS, "elevation_m", "slope_deg", "date", "rainfall_1d_mm",
    "rainfall_3d_mm", "rainfall_7d_mm", "imd_grid_latitude", "imd_grid_longitude",
    "settlement_input_classification", "terrain_source_classification", "rainfall_source_classification",
)


class IntegrationPipelineError(ValueError):
    """Raised when derived inputs cannot be integrated without altering evidence."""


def _read_csv(path: Path, description: str) -> pd.DataFrame:
    if not path.is_file():
        raise IntegrationPipelineError(f"{description} CSV was not found: {path}")
    try:
        # ``NA`` is a literal, meaningful History value in the supplied event
        # inventory, so do not silently coerce it to a missing value on load.
        return pd.read_csv(path, keep_default_na=False)
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise IntegrationPipelineError(f"Unable to read {description} CSV '{path}': {error}") from error


def _require_columns(frame: pd.DataFrame, columns: tuple[str, ...], description: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise IntegrationPipelineError(f"{description} table is missing required columns: " + ", ".join(missing))


def _validate_identity(frame: pd.DataFrame, description: str) -> pd.DataFrame:
    result = frame.copy()
    for column in ("settlement_id", "settlement_name", "region", "district"):
        result[column] = result[column].astype("string").str.strip()
        if result[column].isna().any() or result[column].eq("").any():
            raise IntegrationPipelineError(f"{description} has missing '{column}' values.")
    for column, lower, upper in (("latitude", -90.0, 90.0), ("longitude", -180.0, 180.0)):
        result[column] = pd.to_numeric(result[column], errors="coerce")
        if result[column].isna().any() or not np.isfinite(result[column]).all():
            raise IntegrationPipelineError(f"{description} has invalid '{column}' values.")
        if not result[column].between(lower, upper).all():
            raise IntegrationPipelineError(f"{description} has out-of-range '{column}' values.")
    return result


def validate_terrain_features(terrain: pd.DataFrame) -> pd.DataFrame:
    """Validate static DEM-derived features without filling any missing values."""
    _require_columns(terrain, TERRAIN_COLUMNS, "Terrain")
    result = _validate_identity(terrain.loc[:, TERRAIN_COLUMNS], "Terrain table")
    if result["settlement_id"].duplicated().any():
        raise IntegrationPipelineError("Terrain table has duplicate settlement_id values.")
    for column in ("elevation_m", "slope_deg"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
        if result[column].isna().any() or not np.isfinite(result[column]).all():
            raise IntegrationPipelineError(f"Terrain table has missing or invalid '{column}' values.")
    if (result["slope_deg"] < 0).any() or (result["slope_deg"] > 90).any():
        raise IntegrationPipelineError("Terrain table slope_deg values must be between 0 and 90.")
    return result


def validate_rainfall_features(rainfall: pd.DataFrame) -> pd.DataFrame:
    """Validate daily real-IMD derived features while retaining allowed rolling nulls."""
    _require_columns(rainfall, RAINFALL_COLUMNS, "Rainfall")
    result = _validate_identity(rainfall.loc[:, RAINFALL_COLUMNS], "Rainfall table")
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    if result["date"].isna().any():
        raise IntegrationPipelineError("Rainfall table has invalid 'date' values.")
    if result.duplicated(["settlement_id", "date"]).any():
        raise IntegrationPipelineError("Rainfall table has duplicate settlement_id/date rows.")
    for column in ("rainfall_1d_mm", "imd_grid_latitude", "imd_grid_longitude"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
        if result[column].isna().any() or not np.isfinite(result[column]).all():
            raise IntegrationPipelineError(f"Rainfall table has missing or invalid '{column}' values.")
    for column in ("rainfall_3d_mm", "rainfall_7d_mm"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
        if (~result[column].isna() & ~np.isfinite(result[column])).any():
            raise IntegrationPipelineError(f"Rainfall table has invalid '{column}' values.")
    if not result["imd_grid_latitude"].between(-90, 90).all() or not result["imd_grid_longitude"].between(-180, 180).all():
        raise IntegrationPipelineError("Rainfall table has invalid IMD grid coordinates.")
    return result


def validate_event_inventory(events: pd.DataFrame) -> dict[str, object]:
    """Validate the standalone real inventory; deliberately do not associate its rows."""
    _require_columns(events, EVENT_COLUMNS, "Event inventory")
    report = validate_events(events)
    if report.record_count == 0 or report.missing_coordinates or report.invalid_coordinates:
        raise IntegrationPipelineError("Event inventory has missing or invalid source coordinates.")
    return asdict(report)


def _verify_shared_settlement_identity(terrain: pd.DataFrame, rainfall: pd.DataFrame) -> None:
    terrain_identity = terrain.loc[:, IDENTITY_COLUMNS].set_index("settlement_id").sort_index()
    rainfall_identity = rainfall.loc[:, IDENTITY_COLUMNS].drop_duplicates("settlement_id").set_index("settlement_id").sort_index()
    if not terrain_identity.index.equals(rainfall_identity.index):
        raise IntegrationPipelineError("Terrain and rainfall tables do not contain the same settlement IDs.")
    if not terrain_identity.equals(rainfall_identity):
        raise IntegrationPipelineError("Terrain and rainfall settlement identity fields do not match exactly.")


def build_settlement_daily_features(terrain: pd.DataFrame, rainfall: pd.DataFrame) -> pd.DataFrame:
    """Attach static terrain values to each same-settlement daily rainfall observation."""
    terrain = validate_terrain_features(terrain)
    rainfall = validate_rainfall_features(rainfall)
    _verify_shared_settlement_identity(terrain, rainfall)
    merged = rainfall.merge(terrain.loc[:, ("settlement_id", "elevation_m", "slope_deg")], on="settlement_id", how="left", validate="many_to_one")
    if merged[["elevation_m", "slope_deg"]].isna().any().any():
        raise IntegrationPipelineError("Terrain join left missing derived terrain values.")
    merged["settlement_input_classification"] = "DEMO"
    merged["terrain_source_classification"] = "REAL_DERIVED_FROM_SRTM"
    merged["rainfall_source_classification"] = "REAL_DERIVED_FROM_IMD"
    return merged.loc[:, OUTPUT_COLUMNS].sort_values(["settlement_id", "date"], kind="stable").reset_index(drop=True)


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_integration(terrain_path: Path, rainfall_path: Path, events_path: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    """Load three artifacts; events are validated but never joined to settlement-day rows."""
    terrain = _read_csv(terrain_path, "Terrain features")
    rainfall = _read_csv(rainfall_path, "Rainfall features")
    events = _read_csv(events_path, "Landslide event inventory")
    daily_features = build_settlement_daily_features(terrain, rainfall)
    event_validation = validate_event_inventory(events)
    provenance = {
        "integration_phase": "Phase 1 derived-feature integration",
        "settlement_daily_features_role": "DEMO settlement-day feature table; not a prediction or label table",
        "settlement_input_classification": "DEMO",
        "terrain_source_classification": "REAL_DERIVED_FROM_SRTM",
        "rainfall_source_classification": "REAL_DERIVED_FROM_IMD",
        "event_inventory_classification": "REAL_GSI_NLFC_SUPPLIED_INVENTORY",
        "event_inventory_role": "Validated standalone inventory; not joined, geocoded, distance-matched, dated, or labelled",
        "inputs": {
            "terrain_features": {"path": str(terrain_path).replace("\\", "/"), "sha256": _file_sha256(terrain_path), "record_count": len(terrain)},
            "rainfall_features": {"path": str(rainfall_path).replace("\\", "/"), "sha256": _file_sha256(rainfall_path), "record_count": len(rainfall)},
            "landslide_events": {"path": str(events_path).replace("\\", "/"), "sha256": _file_sha256(events_path), "record_count": len(events)},
        },
        "output_record_count": len(daily_features), "event_validation": event_validation,
    }
    return daily_features, provenance


def write_integration_outputs(daily_features: pd.DataFrame, provenance: dict[str, object], output_path: Path, provenance_path: Path) -> None:
    """Write deterministic derived outputs, leaving all three input artifacts unchanged."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    daily_features.to_csv(output_path, index=False, date_format="%Y-%m-%d")
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
