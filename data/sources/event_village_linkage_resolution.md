# Strict event-to-village containment resolution

**Phase:** 6D — spatial linkage only  
**Status:** **PARTIALLY_RESOLVED**

## Decision and scope

`data/processed/event_village_linkage.csv` is a reproducible, **conditional spatial-containment** artifact. It retains all 772 original GSI/NLFC event columns and adds only `spatial_linkage_status`, `matched_village_lgd_code`, and `matched_village_name_en`. It is not a label table, target, negative sample, risk score, prediction, ML input, or certification of event administrative identity.

The containment result is conditional because Phase 6A established WGS 1984 decimal-degree evidence for the matching GSI inventory schema, but could not certify the CRS/datum, positional accuracy, or coordinate semantics of this exact 772-row PDF release. The village polygons use the KML WGS 84 geographic convention. Therefore a link means only: **the supplied coordinate is strictly contained by one of the 40 exact-ID polygons under that WGS 84 interpretation.** It does not confirm that the point is an accurately located event centroid or that its datum is release-certified compatible with the polygon geometry.

## Reproducible method

Run from the repository root:

```powershell
python pipeline/build_event_village_linkage.py
```

The command reads, without modification:

- `data/processed/landslide_events.csv` — 772 source-derived event rows;
- `data/processed/nilgiris_villages.csv` — Village Master identifiers; and
- `data/raw/admin/vb_soi_tn.kmz` — local SOI-attributed polygon geometry.

A polygon participates only when all three identifiers agree exactly: KMZ `vlcode` equals Village Master `village_lgd_code`, KMZ `dtcode` equals district LGD 587, and KMZ `sdcode` equals the corresponding Village Master taluk LGD code. This yields the same 40 valid exact-ID polygons used for Phase 6C terrain summaries. Each event point is formed only as `(longitude, latitude)` and evaluated with strict `contains`. Boundary touches or multiple containing polygons would be classified `AMBIGUOUS_GEOMETRY` and receive no village ID.

No nearest polygon, buffer, distance threshold, fuzzy/name matching, geocoding, coordinate shift, event-date inference, or use of the 62 Village Master-only / 18 KMZ-only records occurs. No raw event, boundary, rainfall, or terrain input was modified.

## Geometry and unit validation

| Check | Result |
| --- | ---: |
| Exact-ID village polygons eligible | 40 |
| Valid eligible geometries | 40 |
| Invalid/missing eligible geometries | 0 |
| Positive-area overlaps among eligible polygons | 0 |
| Village Master-only records used | 0 / 62 |
| KMZ-only records used | 0 / 18 |

## Linkage result

| Status | Events |
| --- | ---: |
| `EXACT_POLYGON_MATCH` (linked) | 349 |
| `NO_EXACT_POLYGON_MATCH` (unlinked) | 423 |
| `AMBIGUOUS_GEOMETRY` | 0 |
| **Total source events** | **772** |

Unlinked events are preserved in the output with blank matched-village fields. They are not non-events, negative evidence, or evidence that a village has zero landslides.

## Events per eligible village

All 40 exact-ID villages appear below. **15** have zero strictly contained supplied records; zero is a result of this restricted containment operation only, not a no-event assertion.

| Village LGD | Village | Linked events |
| --- | --- | ---: |
| 635080 | Erumad 1 | 0 |
| 635081 | Moonnad 1 | 0 |
| 635082 | Nelliyalam 1 | 9 |
| 635083 | Cherangode1 | 11 |
| 635084 | Nellakotta | 0 |
| 635085 | Mudumalai | 0 |
| 635086 | Sreemadurai | 0 |
| 635087 | Masinagudi | 0 |
| 635088 | Kadanad 1 | 0 |
| 635089 | Ebbanad 1 | 2 |
| 635090 | Kookal | 0 |
| 635091 | Kagguchi 1 | 10 |
| 635092 | Thuneri | 4 |
| 635093 | Hullathy | 4 |
| 635094 | Nanjand1 | 35 |
| 635095 | Udhagai - Rural | 2 |
| 635096 | Thummanatty 1 | 10 |
| 635097 | Hallimoyar | 0 |
| 635098 | Kallampalayam | 0 |
| 635099 | Kodanad | 2 |
| 635100 | Nedugula-I | 3 |
| 635101 | Denad-I | 2 |
| 635102 | Nandhipuram | 0 |
| 635103 | Aracode | 0 |
| 635104 | Kokodu | 0 |
| 635105 | Kadinamala | 0 |
| 635106 | Kengarai 1 | 0 |
| 635107 | Konavakorai-I | 15 |
| 635108 | Naduhatty-1 | 15 |
| 635109 | Kotagiri -1 | 2 |
| 635110 | Jackanarai | 22 |
| 635111 | Yedapally | 5 |
| 635112 | Burliar | 41 |
| 635113 | Coonoor Rural | 36 |
| 635114 | Melur 1 | 1 |
| 635117 | Ithalar 1 | 42 |
| 635118 | Mulligoor | 31 |
| 635119 | Balacola-1 | 27 |
| 635120 | Mel-Kundah | 15 |
| 635121 | Kinnakorai | 3 |

## Date preservation and year distribution

The source's existing `reported_history_date` was retained unchanged. Of the 349 linked events, **137** have a nonblank, already extracted unambiguous ISO date; **212** do not. No date was parsed from another source field or inferred. The dated-linked-event distribution is:

| Year | Events |
| --- | ---: |
| 2017 | 2 |
| 2019 | 36 |
| 2022 | 15 |
| 2023 | 56 |
| 2024 | 4 |
| 2025 | 24 |
| **Total dated linked events** | **137** |

## Output integrity and remaining limitations

The output has 772 rows, preserves the 16 original event columns verbatim, contains 349 nonblank matched IDs/names, and has SHA-256 `5e373c70d6c2eec8ab1121087217da5b4032c82680a9d928c0b124cd79f0204c`.

This phase does not resolve the event PDF's release-specific CRS/datum and positional-quality blocker, the incomplete 102-village boundary population, date completeness, event inventory coverage, or an observation frame for non-events. It must not be used to create ML labels or to assert that an unlinked event, a zero-count village, or an undated record represents absence.
