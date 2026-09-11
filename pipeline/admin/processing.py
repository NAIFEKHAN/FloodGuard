"""Extract official Nilgiris village-master records without spatial inference."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


SOURCE_SHEET = "Sheet1"
DISTRICT_COLUMN = "dname"
NILGIRIS_DISTRICT_NAMES = frozenset({"the nilgiris", "nilgiris"})
SOURCE_COLUMNS = (
    "dcode", "tcode", "vcode", "lgddcode", "lgdtcode", "lgdvcode",
    "dname", "dtname", "tname", "ttname", "vname", "vtname",
)
OUTPUT_COLUMNS = (
    "district_code", "taluk_code", "village_code", "district_lgd_code",
    "taluk_lgd_code", "village_lgd_code", "district_name_en",
    "district_name_ta", "taluk_name_en", "taluk_name_ta", "village_name_en",
    "village_name_ta",
)


class AdminPipelineError(ValueError):
    """Raised when an official administrative workbook cannot be extracted safely."""


@dataclass(frozen=True)
class AdminExtractionReport:
    """Facts recorded about one source workbook extraction."""

    source_path: str
    source_filename: str
    sheet_name: str
    input_record_count: int
    nilgiris_record_count: int
    selected_source_columns: tuple[str, ...]


def _normalise_text(value: object) -> str:
    """Trim source text only; do not transliterate, geocode, or replace names."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def _normalise_code(value: object, column: str) -> str:
    """Preserve the official code value as text, rejecting blank/non-integral values."""
    text = _normalise_text(value)
    if not text:
        raise AdminPipelineError(f"Source column '{column}' contains a blank code value.")
    try:
        number = float(text)
    except ValueError as error:
        raise AdminPipelineError(f"Source column '{column}' has a non-numeric code value: {text!r}.") from error
    if not number.is_integer() or number < 0:
        raise AdminPipelineError(f"Source column '{column}' has an invalid official code value: {text!r}.")
    return str(int(number))


def load_village_master(path: Path, sheet_name: str = SOURCE_SHEET) -> pd.DataFrame:
    """Read the specified Excel worksheet without changing the source workbook."""
    if not path.is_file():
        raise AdminPipelineError(f"Village Master workbook was not found: {path}")
    try:
        workbook = pd.ExcelFile(path, engine="openpyxl")
    except (OSError, ValueError, ImportError) as error:
        raise AdminPipelineError(f"Unable to read Village Master workbook '{path}': {error}") from error
    if sheet_name not in workbook.sheet_names:
        raise AdminPipelineError(
            f"Village Master workbook does not contain required sheet '{sheet_name}'; "
            f"available sheets: {', '.join(workbook.sheet_names)}."
        )
    try:
        return pd.read_excel(workbook, sheet_name=sheet_name, dtype=object, engine="openpyxl")
    except (OSError, ValueError) as error:
        raise AdminPipelineError(f"Unable to read worksheet '{sheet_name}': {error}") from error


def extract_nilgiris_villages(source: pd.DataFrame) -> pd.DataFrame:
    """Select actual Nilgiris rows by official district name, without spatial operations."""
    missing = [column for column in SOURCE_COLUMNS if column not in source.columns]
    if missing:
        raise AdminPipelineError("Village Master worksheet is missing required columns: " + ", ".join(missing))

    selected = source.loc[:, SOURCE_COLUMNS].copy()
    district_key = selected[DISTRICT_COLUMN].map(_normalise_text).str.casefold()
    filtered = selected.loc[district_key.isin(NILGIRIS_DISTRICT_NAMES)].copy()
    if filtered.empty:
        raise AdminPipelineError("Village Master worksheet contains no rows for The Nilgiris/Nilgiris.")

    result = pd.DataFrame(index=filtered.index)
    source_to_output = dict(zip(SOURCE_COLUMNS, OUTPUT_COLUMNS, strict=True))
    code_columns = {"dcode", "tcode", "vcode", "lgddcode", "lgdtcode", "lgdvcode"}
    for source_column, output_column in source_to_output.items():
        if source_column in code_columns:
            result[output_column] = filtered[source_column].map(lambda value: _normalise_code(value, source_column))
        else:
            result[output_column] = filtered[source_column].map(_normalise_text)
    return result.loc[:, OUTPUT_COLUMNS].reset_index(drop=True)


def build_nilgiris_villages(path: Path, sheet_name: str = SOURCE_SHEET) -> tuple[pd.DataFrame, AdminExtractionReport]:
    """Load and extract Nilgiris records while retaining audit facts for provenance."""
    source = load_village_master(path, sheet_name)
    villages = extract_nilgiris_villages(source)
    return villages, AdminExtractionReport(
        source_path=str(path).replace("\\", "/"), source_filename=path.name,
        sheet_name=sheet_name, input_record_count=len(source),
        nilgiris_record_count=len(villages), selected_source_columns=SOURCE_COLUMNS,
    )


def write_nilgiris_villages(villages: pd.DataFrame, output_path: Path) -> None:
    """Write a derived administrative table without altering the Excel source."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    villages.to_csv(output_path, index=False, encoding="utf-8")
