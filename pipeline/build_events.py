"""Command-line entry point for Nilgiri landslide-inventory extraction."""

from __future__ import annotations

import argparse
from pathlib import Path

from events.processing import EventPipelineError, build_event_table, write_event_table


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract directly tabulated Tamil Nadu/Nilgiri landslide inventory records."
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=Path("data/raw/events/landslide_report.pdf"),
        help="Supplied landslide inventory PDF path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/landslide_events.csv"),
        help="Derived CSV output path.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        events, validation = build_event_table(arguments.pdf)
        write_event_table(events, arguments.output)
    except EventPipelineError as error:
        print(f"Event extraction failed: {error}")
        return 1
    print(f"Wrote {validation.record_count} event rows to: {arguments.output}")
    print(validation)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
