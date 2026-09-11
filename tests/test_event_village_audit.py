"""Synthetic-only tests for exact-code point-in-polygon audit behavior."""
import pandas as pd
from shapely.geometry import Polygon

from pipeline.spatial.event_village_audit import SpatialRecord, exact_code_records, link_events


def record(code: str = "100") -> SpatialRecord:
    return SpatialRecord({"vlcode": code, "dtcode": "587", "sdcode": "5756"}, Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]), 1)


def villages() -> pd.DataFrame:
    return pd.DataFrame([{ "village_lgd_code": "100", "district_lgd_code": "587", "taluk_lgd_code": "5756" }])


def events() -> pd.DataFrame:
    return pd.DataFrame([{ "inventory_serial": "1", "slide_no": "a", "latitude": 0.5, "longitude": 0.5, "reported_history_date": "", "source_pdf_page": "1" }, { "inventory_serial": "2", "slide_no": "b", "latitude": 2.0, "longitude": 2.0, "reported_history_date": "", "source_pdf_page": "1" }])


def test_exact_identifier_matching_rejects_district_or_taluk_mismatch() -> None:
    assert exact_code_records([record(), SpatialRecord({"vlcode":"100","dtcode":"587","sdcode":"999"}, record().geometry, 1)], villages()) == [record()]


def test_point_inside_and_outside_polygon_are_classified_without_inference() -> None:
    result = link_events(events(), [record()])
    assert result["spatial_match_status"].tolist() == ["EXACT_POLYGON_MATCH", "NO_EXACT_POLYGON_MATCH"]
    assert result["matched_village_lgd_code"].tolist() == ["100", ""]


def test_unmatched_events_are_preserved() -> None:
    result = link_events(events(), [])
    assert len(result) == len(events())
    assert set(result["spatial_match_status"]) == {"NO_EXACT_POLYGON_MATCH"}
