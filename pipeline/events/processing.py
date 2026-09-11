"""Extract directly tabulated Nilgiri inventory records from the supplied PDF."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re

import pandas as pd
from pypdf import PdfReader


SOURCE_TABLE_LABEL = "LANDSLIDE INVENTORY (Field vaidated)"
PDF_PAGE_START = 693
PDF_PAGE_END = 717
EXPECTED_RECORD_COUNT = 772
SOURCE_PDF_PATH = "data/raw/events/landslide_report.pdf"
OUTPUT_COLUMNS = (
    "inventory_serial",
    "slide_no",
    "state",
    "district",
    "slide_name",
    "location_description",
    "latitude",
    "longitude",
    "material_involved",
    "movement_type",
    "history_raw",
    "reported_history_date",
    "source_pdf_path",
    "source_pdf_page",
    "source_table_label",
    "source_row_text",
)

# These offsets correspond to the common fixed-width table layout recovered
# with pypdf. Individual PDF rows may shift horizontally, so source State and
# District text is used to calculate a row-specific offset below.
FIELD_SLICES = {
    "inventory_serial": (0, 11),
    "slide_no": (11, 48),
    "state": (44, 75),
    "district": (75, 112),
    "slide_name": (112, 154),
    "location_description": (154, 214),
    "latitude": (214, 232),
    "longitude": (232, 250),
    "material_involved": (250, 277),
    "movement_type": (277, 303),
    "history_raw": (303, None),
}
ROW_START = re.compile(r"^[ \t]*(\d+)[ \t]+", re.MULTILINE)
COORDINATE_PAIR = re.compile(r"(?P<latitude>\d{1,2}\.\d+)\s+(?P<longitude>\d{2,3}\.\d+)")
YEAR_ONLY = re.compile(r"^\d{4}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DAY_MONTH_YEAR = re.compile(
    r"^(\d{1,2})(?:st|nd|rd|th)?\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+(\d{4})(?:\s+at\s+.+)?$",
    re.IGNORECASE,
)


class EventPipelineError(ValueError):
    """Raised when the supplied source cannot safely form the expected inventory."""


@dataclass(frozen=True)
class EventValidation:
    """Validation facts for the extracted records; no records are discarded."""

    record_count: int
    duplicate_inventory_serials: int
    duplicate_slide_nos: int
    latitude_min: float | None
    latitude_max: float | None
    longitude_min: float | None
    longitude_max: float | None
    invalid_coordinates: int
    missing_coordinates: int
    missing_state: int
    missing_district: int
    history_na: int
    explicit_dates: int
    year_only_history: int
    ambiguous_history: int
    missing_source_pages: int
    incorrect_source_paths: int
    outside_expected_range: int


def _clean(value: str) -> str:
    """Retain source wording while normalising PDF layout whitespace only."""
    return " ".join(value.split())


def _field_value(lines: list[str], field: str) -> str:
    start, end = FIELD_SLICES[field]
    pieces = [_clean(line[start:end]) for line in lines]
    return _clean(" ".join(piece for piece in pieces if piece))


def _join_wrapped_source_fragments(fragments: list[str]) -> str:
    """Rejoin a PDF line wrap only when it visibly split a word or hyphen token."""
    result = ""
    for fragment in (_clean(fragment) for fragment in fragments):
        if not fragment:
            continue
        if not result:
            result = fragment
            continue
        previous_word = result.rsplit(" ", maxsplit=1)[-1]
        if result.endswith("-") or (len(previous_word) == 1 and previous_word.islower() and fragment[0].islower()):
            result += fragment
        else:
            result += " " + fragment
    return result


def _parse_reported_history_date(history: str) -> str:
    """Return ISO date only for one complete, unambiguous source date."""
    history = history.strip()
    if ISO_DATE.fullmatch(history):
        return history
    match = DAY_MONTH_YEAR.fullmatch(history)
    if not match:
        return ""
    day, month, year = match.groups()
    try:
        return datetime.strptime(f"{day} {month} {year}", "%d %B %Y").date().isoformat()
    except ValueError:
        return ""


def history_category(history: str) -> str:
    """Classify a retained source History value without adding temporal claims."""
    if history == "NA":
        return "na"
    if _parse_reported_history_date(history):
        return "explicit_date"
    if YEAR_ONLY.fullmatch(history):
        return "year_only"
    return "ambiguous"


def _iter_page_records(page_text: str) -> list[list[str]]:
    """Group each fixed-width source row with its wrapped continuation lines."""
    starts = list(ROW_START.finditer(page_text))
    records: list[list[str]] = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(page_text)
        lines = page_text[match.start() : end].splitlines()
        if lines:
            records.append(lines)
    return records


def _parse_row_values(lines: list[str]) -> dict[str, str]:
    """Read a table row, anchoring its trailing classifications on source coordinates.

    A few source rows have narrower early columns (for example numeric Slide_No
    values), so their coordinate and trailing fields shift left of the nominal
    fixed-width offsets. Coordinates are still explicitly printed in every
    selected source row and provide a safer anchor than padding width.
    """
    values = {field: _field_value(lines, field) for field in FIELD_SLICES}
    first_line = lines[0]
    if "Tamil Nadu" in first_line and "Nilgiri" in first_line:
        state_start = first_line.index("Tamil Nadu")
        offset = state_start - FIELD_SLICES["state"][0]
        slide_name_start = FIELD_SLICES["slide_name"][0] + offset
        location_start = FIELD_SLICES["location_description"][0] + offset
        values["slide_no"] = _clean(
            " ".join(
                [first_line[FIELD_SLICES["slide_no"][0] : state_start]]
                + [line[FIELD_SLICES["slide_no"][0] : location_start] for line in lines[1:]]
            )
        )
        values["slide_name"] = _clean(
            " ".join(
                [first_line[slide_name_start:location_start]]
                + [line[slide_name_start:location_start] for line in lines[1:]]
            )
        )
        # These are literal values printed in the source row, rather than a
        # geographic lookup or a normalisation of the source classification.
        values["state"] = "Tamil Nadu"
        values["district"] = "Nilgiri"
    pairs = list(COORDINATE_PAIR.finditer(first_line))
    if not pairs:
        return values
    coordinate_match = pairs[-1]
    values["latitude"] = coordinate_match.group("latitude")
    values["longitude"] = coordinate_match.group("longitude")
    if "Tamil Nadu" in first_line and "Nilgiri" in first_line:
        values["location_description"] = _join_wrapped_source_fragments(
            [first_line[location_start:coordinate_match.start()]] + [line[location_start:] for line in lines[1:]]
        )
    else:
        values["location_description"] = _clean(first_line[FIELD_SLICES["location_description"][0] : coordinate_match.start()])
    trailing = re.split(r"\s{2,}", first_line[coordinate_match.end() :].strip(), maxsplit=2)
    if len(trailing) == 3:
        values["material_involved"], values["movement_type"], values["history_raw"] = map(_clean, trailing)
    return values


def extract_nilgiri_events(pdf_path: Path) -> pd.DataFrame:
    """Read the specified PDF pages and retain only direct Tamil Nadu/Nilgiri rows."""
    if not pdf_path.is_file():
        raise EventPipelineError(f"Landslide source PDF was not found: {pdf_path}")
    try:
        reader = PdfReader(pdf_path)
    except Exception as error:  # pypdf uses several source-specific exception classes.
        raise EventPipelineError(f"Unable to read landslide source PDF '{pdf_path}': {error}") from error
    if len(reader.pages) < PDF_PAGE_END:
        raise EventPipelineError(
            f"Landslide source PDF has {len(reader.pages)} pages; pages {PDF_PAGE_START}-{PDF_PAGE_END} are required."
        )

    extracted: list[dict[str, object]] = []
    for pdf_page in range(PDF_PAGE_START, PDF_PAGE_END + 1):
        page_text = reader.pages[pdf_page - 1].extract_text(extraction_mode="layout") or ""
        for lines in _iter_page_records(page_text):
            values = _parse_row_values(lines)
            if values["state"] != "Tamil Nadu" or values["district"] != "Nilgiri":
                continue
            try:
                latitude = float(values["latitude"])
                longitude = float(values["longitude"])
                inventory_serial = int(values["inventory_serial"])
            except ValueError as error:
                raise EventPipelineError(
                    f"Unable to parse required direct source values on PDF page {pdf_page}: {values}"
                ) from error
            history = values["history_raw"]
            extracted.append(
                {
                    "inventory_serial": inventory_serial,
                    "slide_no": values["slide_no"],
                    "state": values["state"],
                    "district": values["district"],
                    "slide_name": values["slide_name"],
                    "location_description": values["location_description"],
                    "latitude": latitude,
                    "longitude": longitude,
                    "material_involved": values["material_involved"],
                    "movement_type": values["movement_type"],
                    "history_raw": history,
                    "reported_history_date": _parse_reported_history_date(history),
                    "source_pdf_path": SOURCE_PDF_PATH,
                    "source_pdf_page": pdf_page,
                    "source_table_label": SOURCE_TABLE_LABEL,
                    "source_row_text": _clean(" ".join(lines)),
                }
            )
    events = pd.DataFrame(extracted, columns=OUTPUT_COLUMNS)
    if len(events) != EXPECTED_RECORD_COUNT:
        raise EventPipelineError(
            f"Expected {EXPECTED_RECORD_COUNT} Tamil Nadu/Nilgiri records on PDF pages "
            f"{PDF_PAGE_START}-{PDF_PAGE_END}; extracted {len(events)}."
        )
    return events


def validate_events(events: pd.DataFrame) -> EventValidation:
    """Report source-table integrity checks without filtering or changing rows."""
    missing = [column for column in OUTPUT_COLUMNS if column not in events.columns]
    if missing:
        raise EventPipelineError("Event table is missing required columns: " + ", ".join(missing))
    latitude = pd.to_numeric(events["latitude"], errors="coerce")
    longitude = pd.to_numeric(events["longitude"], errors="coerce")
    missing_coordinates = int(latitude.isna().sum() + longitude.isna().sum() - (latitude.isna() & longitude.isna()).sum())
    invalid_coordinates = int(
        ((latitude.notna() & ~latitude.between(-90, 90)) | (longitude.notna() & ~longitude.between(-180, 180))).sum()
    )
    present_slide_nos = events["slide_no"].fillna("").astype(str).str.strip()
    present_slide_nos = present_slide_nos[present_slide_nos != ""]
    categories = events["history_raw"].fillna("").astype(str).map(history_category)
    outside = int(
        (~latitude.between(11.210556, 11.55) | ~longitude.between(76.24763889, 76.95066827)).sum()
    )
    return EventValidation(
        record_count=len(events),
        duplicate_inventory_serials=int(events["inventory_serial"].duplicated().sum()),
        duplicate_slide_nos=int(present_slide_nos.duplicated().sum()),
        latitude_min=None if latitude.empty else float(latitude.min()),
        latitude_max=None if latitude.empty else float(latitude.max()),
        longitude_min=None if longitude.empty else float(longitude.min()),
        longitude_max=None if longitude.empty else float(longitude.max()),
        invalid_coordinates=invalid_coordinates,
        missing_coordinates=missing_coordinates,
        missing_state=int(events["state"].fillna("").astype(str).str.strip().eq("").sum()),
        missing_district=int(events["district"].fillna("").astype(str).str.strip().eq("").sum()),
        history_na=int((categories == "na").sum()),
        explicit_dates=int((categories == "explicit_date").sum()),
        year_only_history=int((categories == "year_only").sum()),
        ambiguous_history=int((categories == "ambiguous").sum()),
        missing_source_pages=int(pd.to_numeric(events["source_pdf_page"], errors="coerce").isna().sum()),
        incorrect_source_paths=int((events["source_pdf_path"] != SOURCE_PDF_PATH).sum()),
        outside_expected_range=outside,
    )


def build_event_table(pdf_path: Path) -> tuple[pd.DataFrame, EventValidation]:
    """Extract and validate the supplied source PDF, without any spatial matching."""
    events = extract_nilgiri_events(pdf_path)
    return events, validate_events(events)


def write_event_table(events: pd.DataFrame, output_path: Path) -> None:
    """Write the derived CSV while leaving the raw source PDF unchanged."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    events.to_csv(output_path, index=False, date_format="%Y-%m-%d")
