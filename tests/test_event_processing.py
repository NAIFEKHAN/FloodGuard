"""Tests for direct extraction of the supplied Nilgiri inventory PDF."""

from pathlib import Path

from pipeline.events.processing import (
    EXPECTED_RECORD_COUNT,
    OUTPUT_COLUMNS,
    SOURCE_PDF_PATH,
    build_event_table,
    history_category,
    validate_events,
)


SOURCE_PDF = Path(SOURCE_PDF_PATH)


def test_history_dates_require_one_complete_unambiguous_source_date() -> None:
    assert history_category("NA") == "na"
    assert history_category("2019") == "year_only"
    assert history_category("October 2014") == "ambiguous"
    assert history_category("02 November 2013, October 2014") == "ambiguous"
    assert history_category("27 May 2025") == "explicit_date"
    assert history_category("2026-01-12") == "explicit_date"


def test_extracts_only_direct_nilgiri_rows_from_supplied_pdf() -> None:
    events, report = build_event_table(SOURCE_PDF)

    assert len(events) == EXPECTED_RECORD_COUNT
    assert list(events.columns) == list(OUTPUT_COLUMNS)
    assert set(events["state"]) == {"Tamil Nadu"}
    assert set(events["district"]) == {"Nilgiri"}
    assert events["source_pdf_page"].between(693, 717).all()
    assert (events["source_pdf_path"] == SOURCE_PDF_PATH).all()
    assert events["source_row_text"].str.len().gt(0).all()
    assert report.duplicate_inventory_serials == 0
    assert report.missing_coordinates == 0
    assert report.invalid_coordinates == 0
    assert report.outside_expected_range == 0


def test_validation_reports_duplicate_slide_numbers_without_removing_rows() -> None:
    events, _ = build_event_table(SOURCE_PDF)
    duplicate = events.copy()
    duplicate.loc[1, "slide_no"] = duplicate.loc[0, "slide_no"]

    report = validate_events(duplicate)

    assert len(duplicate) == EXPECTED_RECORD_COUNT
    assert report.duplicate_slide_nos == 1
