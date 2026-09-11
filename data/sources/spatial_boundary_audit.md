# Spatial boundary compatibility audit: Tamil Nadu SOI village KMZ

**Artifact class:** inspection/audit documentation only. No spatial features, event-to-village associations, labels, modelling data, scores, predictions, or dashboard outputs were created.

## Source inspected

- Source path: `data/raw/admin/vb_soi_tn.kmz`
- Container: KMZ (ZIP), 31,235,350 bytes
- Embedded member: `doc.kml`, 396,450,349 bytes uncompressed
- KML namespace: `http://www.opengis.net/kml/2.2`
- Feature representation: 17,119 KML `Placemark` features
- Source attribution field: `src_agency = Survey of India (SOI)`

## Coordinate reference and geometry audit

KML coordinates use the KML geographic coordinate convention: longitude, latitude, optional altitude in WGS 84 longitude/latitude order. The file contains no separate CRS declaration; its observed coordinate bounds are longitude **76.23332289573452 to 80.36002129827175** and latitude **8.07675451652265 to 13.564575506026328**, consistent with Tamil Nadu geographic coverage.

Every placemark has a KML `MultiGeometry` containing polygon geometry:

| Polygon components per placemark | Feature count |
| --- | ---: |
| 1 | 16,842 |
| 2 | 210 |
| 3 | 36 |
| 4 | 16 |
| 5 | 7 |
| 6 | 3 |
| 7 | 1 |
| 10 | 1 |
| 11 | 1 |
| 13 | 1 |
| 16 | 1 |

Thus the source is polygonal: 16,842 features are single-polygon geometries and 277 have multiple polygon components. Basic polygon validity checks (closed coordinate rings, parseable coordinates, non-empty valid Shapely polygons) found **5 invalid geometries** across the state dataset (placemark sequence numbers 74, 2913, 5034, 7151, and 9413). None of the 58 Nilgiris features is invalid.

## KML attribute schema

The following fields are present. Attribute-name whitespace was trimmed only for reporting; values were not altered.

```text
id, objectid_1, objectid, village, vlcode,
gram_panchayat_name, gram_panchayat_code, block, bkcode,
subdistric, sdcode, sub_district_head_quarter,
district, dtcode, district_head_quarter, state, stcode, uqcode, country,
total_urban_rural, total_households, total_population_village, avg_household,
total_geographical_area, total_male_population_village,
total_female_population_village, tapwater_treated_status,
tapwater_untreated_status, covered_well_status, covered_well_function_year,
covered_well_functioning_summer, uncovered_well_status,
uncovered_well_function_year, uncovered_well_function_summer, handpump_status,
hand_pump_function_summer, tubewell_borehole_status,
tube_wells_borehole_function_year, tube_wells_borehole_function_Summer,
tube_wel_1, spring_status, spring_functioning_all_round_year,
spring_functioning_summer_month, river_canal_status, tank_pond_lake_status,
others_status, closed_drainage_status, open_drainage_status,
village_pin_code_status, forest_area, area_under_non_agricultural_use,
barren_uncultivable_land, permanent_pastures_grazing, land_under_miscellaneous,
culturable_waste_land, fallows_land_other_than_current, current_fallows_area,
net_area_sown, total_unirrigated_land, area_irrigated_by_source, canals_area,
wells_tube_wells_area, tanks_lakes_area, waterfall_area,
other_source_specify_area, nearest_town_name,
nearest_town_distance_from_village, shape_leng, shape_length, shape_area,
ds_name, src_agency, state_name
```

Fields relevant to compatibility are `district`/`dtcode`, `subdistric`/`sdcode`, and `village`/`vlcode`. The KMZ does not expose fields named `lgddcode`, `lgdtcode`, or `lgdvcode`; the value comparison below establishes the compatibility of its equivalent code fields only for the observed records.

## Nilgiris filter

The KML `district` field was filtered using only trimmed, case-folded exact values `The Nilgiris` and `Nilgiris`. The actual matched value is `The Nilgiris`.

- Nilgiris spatial features: **58**
- Nilgiris `dtcode`: **587** for all 58 features
- Nilgiris `sdcode` distribution: 5754: 5; 5755: 6; 5756: 13; 5757: 16; 5758: 11; 5759: 7
- Nilgiris blank `vlcode` values: 0
- Nilgiris duplicate `vlcode` groups: 0
- Nilgiris invalid geometries: 0

## Identifier compatibility with Village Master

Compared source: `data/processed/nilgiris_villages.csv` (102 official Village Master records).

| Identifier comparison | Result |
| --- | ---: |
| Village Master rows | 102 |
| Village Master district LGD code | 587 |
| Village Master taluk LGD-code set | 5754, 5755, 5756, 5757, 5758, 5759 |
| Nilgiris KMZ records | 58 |
| KMZ `dtcode = 587` | 58 / 58 |
| KMZ `sdcode` belongs to Village Master taluk-LGD set | 58 / 58 |
| Exact `vlcode = village_lgd_code` matches | **40** |
| Exact matched records with agreeing district code | 40 / 40 |
| Exact matched records with agreeing taluk/subdistrict code | 40 / 40 |
| Village Master records unmatched by `vlcode` | **62** |
| KMZ records unmatched by `vlcode` | **18** |

The identifier evidence supports that `dtcode`, `sdcode`, and `vlcode` are compatible with the corresponding Village Master LGD-code domains for the 40 exact village-code matches. It does **not** establish equivalence for the 62/18 unmatched records.

The state-wide KMZ has 11 duplicate nonblank `vlcode` groups involving 38 records (including code `999999`, which occurs 18 times). This duplicate condition does not occur in the Nilgiris subset. `nilgiris_villages.csv` has no duplicate `village_lgd_code` values.

## Unmatched identifier lists

Village Master `village_lgd_code` values not present as Nilgiris KMZ `vlcode`:

```text
910517, 931891, 931894, 931899, 931900, 931911, 931913, 931915, 931919, 931931,
931939, 931944, 931946, 931966, 931967, 931970, 931972, 931974, 931975, 931981,
931984, 931986, 931988, 931991, 932008, 932010, 932013, 932015, 932018, 932021,
932022, 932030, 932033, 932036, 932037, 932039, 932041, 932044, 932045, 932046,
932048, 932079, 932081, 932084, 932085, 932087, 932090, 932092, 932093, 932095,
932097, 932099, 932101, 932102, 932104, 932105, 932106, 932108, 932110, 932112,
932113, 932131
```

Nilgiris KMZ `vlcode` values not present in Village Master `village_lgd_code`:

```text
252594, 252595, 252597, 252598, 252599, 252600, 252601, 252602, 252603, 252605,
252607, 252608, 252609, 252610, 252920, 277302, 635115, 635116
```

## Names and code differences

Identifier comparison is possible and was used first. No fuzzy matching, automatic name matching, geocoding, or geometry/name inference was performed for unmatched records.

Among the 40 exact `vlcode` matches, only 11 have exactly identical displayed English village names and 26 have exactly identical displayed English taluk names. These display-name differences may reflect spelling, formatting, or source-version changes, but they are not resolved by this audit and did not affect identifier matching. No name-based candidates are reported because identifier comparison is available but incomplete; a name-based procedure would require separate approval and rules.

## Recommendation and gate

**Boundary compatibility is partially verified, not complete.** The 40 exact, code-consistent village matches are auditable, but the mismatch between 102 Village Master rows and 58 KMZ features requires authoritative reconciliation before this source can serve as a complete modelling-unit boundary layer.

Next phase should be a bounded **authoritative boundary-version and LGD-code reconciliation**: obtain/verify source vintage and metadata, explain the 62 Village Master-only and 18 KMZ-only codes, and determine whether they represent boundary changes, excluded urban/other units, or different administrative scopes. Revalidate the five state-wide invalid geometries from their original authoritative source; do not silently repair them.

No event-to-village linkage, target-label construction, or ML is allowed on the basis of this audit alone.
