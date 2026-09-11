# Landslide-event source provenance and processing

## Source

`data/raw/events/landslide_report.pdf` is the supplied landslide-inventory source. The PDF's table header reads **`LANDSLIDE INVENTORY (Field vaidated)`** (including the source spelling). It was supplied to this project as GSI/NLFC inventory material. Its embedded PDF metadata identifies only `pypdf` as producer; the source file itself does not provide a publisher, version, publication date, or original URL. Those missing provenance details must not be invented.

## Nilgiri extraction

`pipeline/build_events.py` reads only PDF pages **693–717** (one-based PDF page numbering) and selects rows whose printed State and District values are `Tamil Nadu` and `Nilgiri`. It produces `data/processed/landslide_events.csv`, a **DERIVED DATA** table of **772** directly tabulated inventory rows.

Run it from the repository root:

```powershell
python pipeline/build_events.py
```

The pipeline uses pypdf layout extraction and the table's printed coordinates to anchor trailing fields. It preserves values as source text wherever practical, normalising PDF layout whitespace only. Wrapped source rows are retained as `source_row_text`; no record is generated from a name, location, or nearby record.

## Output fields

- `inventory_serial` — printed table serial number.
- `slide_no` — printed source slide/reference number, retained verbatim where present.
- `state`, `district` — printed administrative labels.
- `slide_name`, `location_description` — printed source text; blank source fields remain blank.
- `latitude`, `longitude` — coordinates printed directly in the PDF, never geocoded or inferred.
- `material_involved`, `movement_type` — printed source classifications.
- `history_raw` — verbatim History field after layout-whitespace normalisation; `NA` remains `NA`.
- `reported_history_date` — ISO date only if `history_raw` contains exactly one complete, unambiguous date. A slide number is never used to derive a date. Year-only, month-year, ranges, and multi-date text remain unconverted.
- `source_pdf_path`, `source_pdf_page`, `source_table_label`, `source_row_text` — audit/provenance fields preserving the local source, one-based page, table label, and recovered row text.

## Validation

The extractor checks the expected 772-row count, duplicate serial/reference numbers, coordinate presence and geographic validity, state/district presence, History categories, and source page/path fields. The observed Nilgiri coordinate envelope is latitude **11.210556–11.550000** and longitude **76.24763889–76.95066827**. Rows are not silently discarded for being outside that expected envelope; they are reported for investigation.

## Limitations and data classification

The PDF's `History` values are heterogeneous: many are `NA`, some are year-only or otherwise ambiguous, and only explicit unambiguous complete dates can populate `reported_history_date`. The table is an inventory record, not a guarantee of occurrence time, completeness, or current conditions.

The extracted rows are **REAL** supplied GSI/NLFC inventory information: their coordinates, material, movement, and History information come directly from the PDF. `data/demo/settlements_demo.csv` contains exactly two **DEMO** settlement locations. This phase creates no linkage, matching, distance calculation, geocoding, rainfall join, risk score, prediction, or other relationship between DEMO settlements and the real inventory records.
