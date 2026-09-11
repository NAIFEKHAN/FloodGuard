"""Tests for the foundation API endpoints."""

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_check_returns_service_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "FloodGuard API"}


def test_experimental_hazard_index_returns_the_restricted_40_village_artifact() -> None:
    response = client.get("/api/experimental-hazard-index")

    assert response.status_code == 200
    payload = response.json()
    assert payload["classification"] == "EXPERIMENTAL_HAZARD_INDEX_NOT_ML_NOT_A_PREDICTION"
    assert payload["record_count"] == 40
    assert len(payload["records"]) == 40
    assert len({record["village_lgd_code"] for record in payload["records"]}) == 40
