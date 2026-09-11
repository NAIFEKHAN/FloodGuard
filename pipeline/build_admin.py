"""Command-line entry point for bounded Nilgiris village-master preparation."""

from __future__ import annotations

import argparse
from pathlib import Path

from admin.processing import AdminPipelineError, build_nilgiris_villages, write_nilgiris_villages


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract official Nilgiris village-master records without spatial matching.")
    parser.add_argument("--input", type=Path, default=Path("data/raw/admin/Village Master.xlsx"))
    parser.add_argument("--sheet", default="Sheet1")
    parser.add_argument("--output", type=Path, default=Path("data/processed/nilgiris_villages.csv"))
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        villages, report = build_nilgiris_villages(arguments.input, arguments.sheet)
        write_nilgiris_villages(villages, arguments.output)
    except AdminPipelineError as error:
        print(f"Administrative extraction failed: {error}")
        return 1
    print(f"Read {report.input_record_count} worksheet records from {report.source_filename} ({report.sheet_name}).")
    print(f"Wrote {report.nilgiris_record_count} Nilgiris village records to: {arguments.output}")
    print("No event linkage, geocoding, geometry, labels, or modelling data was created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
