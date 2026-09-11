"""Tests for bounded integration using synthetic TEST FIXTURE tables only."""

from pathlib import Path

import pandas as pd
import pytest

from pipeline.events.processing import OUTPUT_COLUMNS as EVENT_COLUMNS
from pipeline.integration.processing import (
    IntegrationPipelineError,
    build_integration,
    build_settlement_daily_features,
)


def terrain_fixture() -> pd.DataFrame:
    return pd.DataFrame([{"settlement_id": "TEST-001", "settlement_name": "Test point", "latitude": 11.0, "longitude": 76.0, "region": "Test region", "district": "Test district", "elevation_m": 1000.0, "slope_deg": 20.0}])


def rainfall_fixture() -> pd.DataFrame:
    return pd.DataFrame([
        {"settlement_id": "TEST-001", "settlement_name": "Test point", "latitude": 11.0, "longitude": 76.0, "region": "Test region", "district": "Test district", "date": "2024-01-01", "rainfall_1d_mm": 1.0, "rainfall_3d_mm": None, "rainfall_7d_mm": None, "imd_grid_latitude": 11.0, "imd_grid_longitude": 76.0},
        {"settlement_id": "TEST-001", "settlement_name": "Test point", "latitude": 11.0, "longitude": 76.0, "region": "Test region", "district": "Test district", "date": "2024-01-02", "rainfall_1d_mm": 2.0, "rainfall_3d_mm": None, "rainfall_7d_mm": None, "imd_grid_latitude": 11.0, "imd_grid_longitude": 76.0},
    ])


def event_fixture() -> pd.DataFrame:
    row = {column: "" for column in EVENT_COLUMNS}
    row.update({"inventory_serial": 1, "slide_no": "TEST/1", "state": "Test State", "district": "Test district", "latitude": 11.0, "longitude": 76.0, "history_raw": "NA", "source_pdf_path": "test.pdf", "source_pdf_page": 1, "source_table_label": "TEST", "source_row_text": "synthetic test fixture"})
    return pd.DataFrame([row])


def test_builds_daily_features_only_for_matching_test_fixture_settlement() -> None:
    features = build_settlement_daily_features(terrain_fixture(), rainfall_fixture())
    assert len(features) == 2
    assert features["elevation_m"].tolist() == [1000.0, 1000.0]
    assert features["settlement_input_classification"].unique().tolist() == ["DEMO"]
    assert features["terrain_source_classification"].unique().tolist() == ["REAL_DERIVED_FROM_SRTM"]
    assert features["rainfall_source_classification"].unique().tolist() == ["REAL_DERIVED_FROM_IMD"]


def test_rejects_mismatched_settlement_identity() -> None:
    rainfall = rainfall_fixture()
    rainfall.loc[0, "latitude"] = 11.1
    with pytest.raises(IntegrationPipelineError, match="identity fields do not match"):
        build_settlement_daily_features(terrain_fixture(), rainfall)


def test_build_integration_validates_but_does_not_join_test_fixture_events(tmp_path: Path) -> None:
    terrain_path, rainfall_path, events_path = tmp_path / "terrain.csv", tmp_path / "rainfall.csv", tmp_path / "events.csv"
    terrain_fixture().to_csv(terrain_path, index=False)
    rainfall_fixture().to_csv(rainfall_path, index=False)
    event_fixture().to_csv(events_path, index=False)
    features, provenance = build_integration(terrain_path, rainfall_path, events_path)
    assert len(features) == 2
    assert "inventory_serial" not in features.columns
    assert provenance["inputs"]["landslide_events"]["record_count"] == 1
    assert "not joined" in provenance["event_inventory_role"]
