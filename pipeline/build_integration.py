"""Command-line entry point for the bounded Phase 1 integration layer."""
from __future__ import annotations
import argparse
from pathlib import Path
from integration.processing import IntegrationPipelineError, build_integration, write_integration_outputs

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Integrate terrain and rainfall without event matching or labels.")
    parser.add_argument("--terrain", type=Path, default=Path("data/processed/terrain_features.csv"))
    parser.add_argument("--rainfall", type=Path, default=Path("data/processed/rainfall_features.csv"))
    parser.add_argument("--events", type=Path, default=Path("data/processed/landslide_events.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/settlement_daily_features.csv"))
    parser.add_argument("--provenance", type=Path, default=Path("data/processed/integration_provenance.json"))
    return parser.parse_args()

def main() -> int:
    arguments = parse_arguments()
    try:
        features, provenance = build_integration(arguments.terrain, arguments.rainfall, arguments.events)
        write_integration_outputs(features, provenance, arguments.output, arguments.provenance)
    except IntegrationPipelineError as error:
        print(f"Integration pipeline failed: {error}")
        return 1
    print(f"Wrote {len(features)} settlement-day feature rows to: {arguments.output}")
    print(f"Wrote provenance to: {arguments.provenance}")
    print("The event inventory was validated as a standalone real source and was not joined.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
