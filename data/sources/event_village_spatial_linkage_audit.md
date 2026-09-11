# Event-to-village spatial linkage feasibility audit

**Artifact class:** scientific feasibility audit only. This report does not create a modelling dataset, ML target, risk score, prediction, negative sample, or final administrative linkage.

## Question and method

The question was whether the supplied GSI/NLFC coordinates can be directly associated with official Nilgiris villages using the supplied SOI/TNGIS polygons. The test used only the 40 polygons for which all of the following are exact: KMZ `vlcode = Village Master village_lgd_code`, KMZ `dtcode = district_lgd_code = 587`, and KMZ `sdcode = taluk_lgd_code`.

For each of the 772 original inventory coordinates, a point was formed as `(longitude, latitude)` and tested for strict containment in those eligible polygons. A point on a polygon boundary, or in more than one polygon, would be classified `AMBIGUOUS_GEOMETRY`. All other non-contained points are `NO_EXACT_POLYGON_MATCH`. The test did not use nearest villages or polygons, distance thresholds, buffers, fuzzy or name matching, reverse geocoding, coordinate shifting, or any inferred boundary/event relationship.

## Sources

- `data/raw/admin/vb_soi_tn.kmz`: SOI/TNGIS village-boundary KMZ.
- `data/processed/nilgiris_villages.csv`: 102 TNGIS Village Master records.
- `data/processed/landslide_events.csv`: 772 real supplied GSI/NLFC Nilgiris landslide inventory records.

All inputs were read without modification. The DEMO settlement/day table was not used.

## Geometry, attributes, and CRS audit

The KML uses its standard geographic coordinate ordering, longitude then latitude, with WGS84 geographic interpretation. There is no separate CRS declaration in the KMZ. All 58 exact-district Nilgiris placemarks are polygonal `MultiGeometry` features: 57 have one polygon component and one has two components, for 59 polygon components total. All 58 resulting geometries are valid; none is missing or invalid.

Relevant KMZ identifiers are `dtcode` (district), `sdcode` (subdistrict/taluk), and `vlcode` (village). Relevant displayed names are `district`, `subdistric`, and `village`; additional available fields include `id`, `objectid`, `block`/`bkcode`, `state`/`stcode`, `gram_panchayat_name`/`gram_panchayat_code`, `src_agency`, and area/population/service attributes. The Nilgiris records all have `dtcode = 587`; their `sdcode` values span the six preserved taluk LGD codes 5754–5759. Nilgiris `vlcode` is nonblank and unique: there are no duplicate village identifiers in this subset.

The event PDF does not independently document the event-coordinate CRS or datum. Accordingly, the results below mean only **“coordinate falls inside polygon under the current WGS84 interpretation.”** They are not official verification that the event-coordinate datum is compatible with the KML datum.

## Exact identifier compatibility

| Comparison | Result |
| --- | ---: |
| Village Master records | 102 |
| Nilgiris KMZ spatial records | 58 |
| Exact code-compatible polygons | 40 |
| Village Master only | 62 |
| KMZ only | 18 |

The 40 eligible polygons have exact village, district, and taluk-code agreement. The remaining records were not merged. Their pattern is consistent with a possible administrative scope and/or vintage difference (for example, KMZ-only town/municipality-style units), but the available data does not establish a record-by-record correspondence. No name-based resolution was performed.

## Polygon integrity and overlaps

No positive-area overlap was found among the 58 Nilgiris geometries or among the 40 exact-compatible polygons. Shared boundaries are not treated as overlaps. The one multipart placemark was retained as multipart; no geometry was repaired, simplified, or altered.

## Pure point-in-polygon result

| Status | Event records |
| --- | ---: |
| `EXACT_POLYGON_MATCH` | 349 |
| `NO_EXACT_POLYGON_MATCH` | 423 |
| `AMBIGUOUS_GEOMETRY` | 0 |
| Total input records | 772 |

For the 349 `EXACT_POLYGON_MATCH` records, the matched value is the official Village Master LGD code of the exact-compatible containing polygon. The 423 unmatched records are preserved as unmatched; they are not negative samples, non-events, or evidence of absence. An optional diagnostic export, if created by `pipeline/build_event_village_audit.py`, uses only original event identifiers/source fields plus `spatial_match_status` and `matched_village_lgd_code`; it is not a modelling dataset.

## Scientific limitations and recommendation

The result demonstrates a direct spatial containment relationship for 349 events under the current WGS84 interpretation and for only the exact-code-compatible subset of village polygons. It does **not** establish official CRS/datum compatibility for the event coordinates, complete coverage of the 102 official Village Master units, a temporal relationship, a negative class, or a complete modelling target.

**Recommendation: do not proceed to ML.** Obtain (1) authoritative CRS/datum documentation for the GSI/NLFC coordinates and (2) an authoritative boundary-vintage/LGD crosswalk or replacement boundary release that explains all 62 Village Master-only and 18 KMZ-only records. Re-run the same exact-code, no-inference containment audit after that evidence is available. Do not substitute an artificial linkage.
