"""Create a full, strict-containment event-to-village linkage artifact."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from spatial.event_village_audit import exact_code_records, link_events, read_nilgiris_kmz


ROOT = Path(__file__).resolve().parents[1]


def build_linkage(events_path: Path, villages_path: Path, kmz_path: Path) -> pd.DataFrame:
    """Preserve every event column while adding only exact-polygon containment results."""
    events = pd.read_csv(events_path, dtype=str, keep_default_na=False)
    villages = pd.read_csv(villages_path, dtype=str, keep_default_na=False)
    numeric_events = events.copy()
    numeric_events["latitude"] = pd.to_numeric(numeric_events["latitude"], errors="raise")
    numeric_events["longitude"] = pd.to_numeric(numeric_events["longitude"], errors="raise")
    exact = exact_code_records(read_nilgiris_kmz(kmz_path), villages)
    audit = link_events(numeric_events, exact)
    if len(audit) != len(events):
        raise ValueError("Strict-containment audit did not return one result for every event.")
    result = events.copy()
    result["spatial_linkage_status"] = audit["spatial_match_status"].to_numpy()
    result["matched_village_lgd_code"] = audit["matched_village_lgd_code"].to_numpy()
    village_names = villages.set_index("village_lgd_code")["village_name_en"]
    result["matched_village_name_en"] = result["matched_village_lgd_code"].map(village_names).fillna("")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Link events only by strict containment in exact-ID village polygons.")
    parser.add_argument("--events", type=Path, default=ROOT / "data/processed/landslide_events.csv")
    parser.add_argument("--villages", type=Path, default=ROOT / "data/processed/nilgiris_villages.csv")
    parser.add_argument("--kmz", type=Path, default=ROOT / "data/raw/admin/vb_soi_tn.kmz")
    parser.add_argument("--output", type=Path, default=ROOT / "data/processed/event_village_linkage.csv")
    arguments = parser.parse_args()
    linkage = build_linkage(arguments.events, arguments.villages, arguments.kmz)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    linkage.to_csv(arguments.output, index=False)
    linked = int((linkage["spatial_linkage_status"] == "EXACT_POLYGON_MATCH").sum())
    print(f"Wrote {len(linkage)} event rows; strict links: {linked}; unlinked: {len(linkage) - linked}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
