"""Create an exact-code-only event/village spatial feasibility audit."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from spatial.event_village_audit import exact_code_records, geometry_summary, link_events, overlap_pairs, read_nilgiris_kmz


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    villages = pd.read_csv(ROOT / "data/processed/nilgiris_villages.csv", dtype=str)
    events = pd.read_csv(ROOT / "data/processed/landslide_events.csv", dtype=str)
    events["latitude"] = pd.to_numeric(events["latitude"])
    events["longitude"] = pd.to_numeric(events["longitude"])
    records = read_nilgiris_kmz(ROOT / "data/raw/admin/vb_soi_tn.kmz")
    exact = exact_code_records(records, villages)
    audit = link_events(events, exact)
    audit.to_csv(ROOT / "data/processed/event_village_linkage_audit.csv", index=False)
    summary, overlaps = geometry_summary(records), overlap_pairs(exact)
    counts = audit["spatial_match_status"].value_counts().to_dict()
    exact_codes = {record.attributes["vlcode"] for record in exact}
    kmz_codes = {record.attributes.get("vlcode", "") for record in records}
    village_codes = set(villages["village_lgd_code"])
    report = f"""# Event-to-village spatial linkage feasibility audit

**Artifact class:** diagnostic audit only. `event_village_linkage_audit.csv` is not a modelling dataset, label table, target, score, prediction, or final administrative linkage.

## Method

This audit read the original KMZ and processed CSVs without modifying them. Nilgiris KMZ placemarks were selected only by exact district value (`The Nilgiris`/`Nilgiris`). A polygon was eligible only when its KMZ `vlcode` exactly equalled a Village Master `village_lgd_code` **and** its `dtcode`/`sdcode` equalled the corresponding Village Master district/taluk LGD codes. For each event, the WGS84-order point `(longitude, latitude)` was tested with strict point-in-polygon containment against those eligible polygons only. Boundary touches and multiple containing polygons are `AMBIGUOUS_GEOMETRY`; all other events are `NO_EXACT_POLYGON_MATCH`. No nearest feature, buffer, distance, name match, geocoding, coordinate shift, or inference was used.

## Sources and CRS limitation

- `data/raw/admin/vb_soi_tn.kmz`: KML geographic longitude/latitude convention, WGS84 interpretation; 58 exact-district Nilgiris records.
- `data/processed/nilgiris_villages.csv`: 102 TNGIS Village Master records.
- `data/processed/landslide_events.csv`: 772 supplied GSI/NLFC inventory records.

KML’s coordinate convention supports the WGS84 interpretation of the polygons. The event PDF does **not** independently document its coordinate reference system or datum. Thus a result below means only **“coordinate falls inside polygon under the current WGS84 interpretation”**; it is not official verification of event CRS/datum compatibility.

## Geometry and identifier audit

| Measure | Result |
| --- | ---: |
| Nilgiris spatial records | {summary['records']} |
| Valid geometries | {summary['valid']} |
| Invalid/missing geometries | {summary['invalid']} |
| Multipart placemarks | {summary['multipart']} |
| Polygon components | {summary['polygon_parts']} |
| Exact code-compatible village polygons | {len(exact)} |
| Village Master only | {len(village_codes - kmz_codes)} |
| KMZ only | {len(kmz_codes - village_codes)} |
| Positive-area overlaps among exact polygons | {len(overlaps)} |

KMZ identifiers available for this test are `dtcode`, `sdcode`, and `vlcode`, with names in `district`, `subdistric`, and `village`. They correspond to the Village Master code domains only for the exact matches. The unmatched 62 Village Master and 18 KMZ records must not be merged: their different scope/vintage is plausible (including KMZ town/municipality-style names), but not established record-by-record by this audit.

## Point-in-polygon feasibility result

| Status | Events |
| --- | ---: |
| `EXACT_POLYGON_MATCH` | {counts.get('EXACT_POLYGON_MATCH', 0)} |
| `NO_EXACT_POLYGON_MATCH` | {counts.get('NO_EXACT_POLYGON_MATCH', 0)} |
| `AMBIGUOUS_GEOMETRY` | {counts.get('AMBIGUOUS_GEOMETRY', 0)} |
| Total | {len(audit)} |

The diagnostic CSV preserves all 772 inventory rows with only original identifying/source fields plus the audit status and, only for direct eligible-polygon containment, `matched_village_lgd_code`. It does not interpret an unmatched point as a negative sample or non-event.

## Recommendation

The available evidence is **insufficient to proceed to modelling**. Direct containment can be audited for the exact-code-compatible subset, but it does not establish CRS compatibility for events and cannot provide complete coverage of the 102 official Village Master units. Before ML or any final event-to-village linkage, obtain authoritative event CRS/datum documentation and an authoritative boundary-vintage/LGD crosswalk or boundary release explaining all 62 Village Master-only and 18 KMZ-only records. Do not create an alternative inferred linkage.
"""
    (ROOT / "data/sources/event_village_spatial_linkage_audit.md").write_text(report, encoding="utf-8")
    print(f"Exact polygons: {len(exact)}; linked: {counts.get('EXACT_POLYGON_MATCH', 0)}; unmatched: {counts.get('NO_EXACT_POLYGON_MATCH', 0)}; ambiguous: {counts.get('AMBIGUOUS_GEOMETRY', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
