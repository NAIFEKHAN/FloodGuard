"""Temporal feasibility classifications for supplied event dates; not a modelling join."""
from __future__ import annotations

import pandas as pd


TEMPORAL_COLUMNS = (
    "inventory_serial", "slide_no", "reported_history_date", "event_year",
    "rainfall_year_available", "temporal_status", "source_pdf_page",
)


def classify_event_dates(events: pd.DataFrame, available_dates: set[pd.Timestamp]) -> pd.DataFrame:
    """Classify only explicit ISO ``reported_history_date`` values.

    Blank dates—including year-only and ambiguous source histories—remain unknown.
    An available date must be present in the supplied rainfall date set; this function
    does not interpolate, infer dates, or treat unavailable rainfall as a non-event.
    """
    date_set = {pd.Timestamp(value).normalize() for value in available_dates}
    output: list[dict[str, object]] = []
    for _, event in events.iterrows():
        raw = str(event.get("reported_history_date", "") or "").strip()
        date = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
        row = {name: event.get(name, "") for name in ("inventory_serial", "slide_no", "reported_history_date", "source_pdf_page")}
        if pd.isna(date):
            row.update(event_year="", rainfall_year_available=False, temporal_status="EVENT_DATE_UNKNOWN")
        else:
            normalized = pd.Timestamp(date).normalize()
            row.update(
                event_year=int(normalized.year),
                rainfall_year_available=normalized.year in {item.year for item in date_set},
                temporal_status="RAINFALL_DATE_AVAILABLE" if normalized in date_set else "RAINFALL_DATE_NOT_AVAILABLE",
            )
        output.append(row)
    return pd.DataFrame(output, columns=TEMPORAL_COLUMNS)


def explicit_date_year_audit(events: pd.DataFrame) -> pd.DataFrame:
    """Return explicit-date counts only; source history text is never converted to a date."""
    dates = pd.to_datetime(events["reported_history_date"], format="%Y-%m-%d", errors="coerce")
    valid = pd.DataFrame({"date": dates.dropna()})
    if valid.empty:
        return pd.DataFrame(columns=("year", "number_of_explicit_events", "number_of_unique_event_dates"))
    result = valid.groupby(valid["date"].dt.year).agg(
        number_of_explicit_events=("date", "size"), number_of_unique_event_dates=("date", "nunique")
    ).reset_index(names="year")
    return result
