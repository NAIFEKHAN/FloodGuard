"""Synthetic-only tests for temporal feasibility classifications."""
import pandas as pd

from pipeline.spatial.temporal_rainfall_audit import classify_event_dates, explicit_date_year_audit


def source_events() -> pd.DataFrame:
    return pd.DataFrame([
        {"inventory_serial":"1", "slide_no":"a", "reported_history_date":"2024-07-01", "history_raw":"1 July 2024", "source_pdf_page":"1"},
        {"inventory_serial":"2", "slide_no":"b", "reported_history_date":"", "history_raw":"2019", "source_pdf_page":"1"},
        {"inventory_serial":"3", "slide_no":"c", "reported_history_date":"", "history_raw":"October 2014", "source_pdf_page":"1"},
        {"inventory_serial":"4", "slide_no":"d", "reported_history_date":"", "history_raw":"NA", "source_pdf_page":"1"},
        {"inventory_serial":"5", "slide_no":"e", "reported_history_date":"2023-11-23", "history_raw":"23 November 2023", "source_pdf_page":"1"},
    ])


def test_explicit_date_and_rainfall_availability_classification() -> None:
    result = classify_event_dates(source_events(), {pd.Timestamp("2024-07-01")})
    assert result["temporal_status"].tolist() == ["RAINFALL_DATE_AVAILABLE", "EVENT_DATE_UNKNOWN", "EVENT_DATE_UNKNOWN", "EVENT_DATE_UNKNOWN", "RAINFALL_DATE_NOT_AVAILABLE"]
    assert result["rainfall_year_available"].tolist() == [True, False, False, False, False]


def test_year_only_and_ambiguous_histories_remain_unknown() -> None:
    result = classify_event_dates(source_events(), {pd.Timestamp("2019-01-01"), pd.Timestamp("2014-10-01")})
    assert result.loc[1:3, "temporal_status"].tolist() == ["EVENT_DATE_UNKNOWN"] * 3
    assert result.loc[1:3, "event_year"].tolist() == [""] * 3


def test_year_audit_uses_explicit_dates_only() -> None:
    result = explicit_date_year_audit(source_events())
    assert result.to_dict("records") == [
        {"year": 2023, "number_of_explicit_events": 1, "number_of_unique_event_dates": 1},
        {"year": 2024, "number_of_explicit_events": 1, "number_of_unique_event_dates": 1},
    ]
