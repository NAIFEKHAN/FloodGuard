"""Tests for bounded official Village Master extraction."""

from pathlib import Path

import pandas as pd
import pytest

from pipeline.admin.processing import AdminPipelineError, OUTPUT_COLUMNS, SOURCE_COLUMNS, build_nilgiris_villages, extract_nilgiris_villages


def source_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "dcode": 12, "tcode": 3, "vcode": 7, "lgddcode": 590, "lgdtcode": 5901,
        "lgdvcode": 910001, "dname": "The Nilgiris", "dtname": "நீலகிரி",
        "tname": "Udhagamandalam", "ttname": "உதகமண்டலம்", "vname": "Test Village",
        "vtname": "சோதனை கிராமம்",
    }
    row.update(overrides)
    return row


def test_extracts_nilgiris_using_actual_district_field_and_preserves_lgd_codes() -> None:
    source = pd.DataFrame([source_row(), source_row(dname=" Nilgiris ", lgdvcode=910002), source_row(dname="Coimbatore")], columns=SOURCE_COLUMNS)
    result = extract_nilgiris_villages(source)
    assert list(result.columns) == list(OUTPUT_COLUMNS)
    assert len(result) == 2
    assert result["district_lgd_code"].tolist() == ["590", "590"]
    assert result["taluk_lgd_code"].tolist() == ["5901", "5901"]
    assert result["village_lgd_code"].tolist() == ["910001", "910002"]
    assert result.loc[0, "village_name_ta"] == "சோதனை கிராமம்"


def test_rejects_missing_required_source_column() -> None:
    with pytest.raises(AdminPipelineError, match="missing required columns"):
        extract_nilgiris_villages(pd.DataFrame([source_row()]).drop(columns="lgdvcode"))


def test_reads_excel_and_reports_input_and_filtered_counts(tmp_path: Path) -> None:
    workbook_path = tmp_path / "Village Master.xlsx"
    pd.DataFrame([source_row(), source_row(dname="Other District")], columns=SOURCE_COLUMNS).to_excel(workbook_path, sheet_name="Sheet1", index=False)
    villages, report = build_nilgiris_villages(workbook_path)
    assert len(villages) == 1
    assert report.input_record_count == 2
    assert report.nilgiris_record_count == 1
    assert report.sheet_name == "Sheet1"
    assert report.selected_source_columns == SOURCE_COLUMNS


def test_supplied_village_master_extracts_only_the_verified_nilgiris_records() -> None:
    villages, report = build_nilgiris_villages(Path("data/raw/admin/Village Master.xlsx"))

    assert report.input_record_count == 17_192
    assert report.nilgiris_record_count == 102
    assert set(villages["district_name_en"]) == {"The Nilgiris"}
    assert set(villages["district_lgd_code"]) == {"587"}
    assert not villages["village_lgd_code"].duplicated().any()
