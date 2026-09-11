# Nilgiris village-boundary resolution

**Phase:** 6B — village-boundary modelling units only  
**Status:** **PARTIALLY_RESOLVED**

## Decision

The available local SOI-attributed KMZ provides a **maximum defensible boundary subset of 40 Nilgiris village polygons**. Each has a unique geometry and is reconciled to exactly one of the 102 Village Master records using all three matching authoritative identifier values: village (`vlcode = village_lgd_code`), district (`dtcode = district_lgd_code = 587`), and taluk/subdistrict (`sdcode = taluk_lgd_code`).

It does **not** resolve a complete boundary layer for the 102-record Village Master universe. The remaining 62 Village Master IDs and 18 KMZ IDs have no supported counterpart. No names, points, centroids, nearest features, or coordinate relationships were used to manufacture a correspondence. Consequently, the 40 polygons are an auditable spatial subset only; they are not approval to begin modelling, labels, or event linkage.

## Local sources inspected

| Source | What it establishes | Result |
| --- | --- | --- |
| `data/raw/admin/Village Master.xlsx` / `data/processed/nilgiris_villages.csv` | Authoritative administrative ID population supplied to the project: 102 Nilgiris records, district LGD 587, six taluk LGD codes (5754–5759), unique village LGD codes. It contains no geometry. | 102 candidate administrative units. |
| `data/raw/admin/vb_soi_tn.kmz` | 58 Nilgiris polygon features selected only by exact district value; source attribute says `src_agency = Survey of India (SOI)`. The archive does not supply a separate release/version, publication date, licence, or field dictionary. | 58 geometrically valid local polygons; source metadata is insufficient to establish complete/current coverage. |
| Existing spatial and identifier audits | Exact code reconciliation and KML integrity checks, including no invalid Nilgiris geometries and no duplicate Nilgiris `vlcode` values. | 40 exact three-code matches; no evidence-based reconciliation for the residual records. |

## Identifier and polygon result

| Measure | Count |
| --- | ---: |
| Village Master administrative records | 102 |
| Nilgiris KMZ polygon features | 58 |
| Nilgiris KMZ geometries passing the existing validity check | 58 |
| Exact authoritative three-code reconciliations | **40** |
| Valid, reconciled boundary polygons — maximum defensible modelling-unit subset | **40** |
| Village Master-only records | **62** |
| KMZ-only records | **18** |

The 40-code intersection is one-to-one and all those records agree on district and taluk code. The residual counts are retained as separate source populations. In particular, a common district/taluk domain is not a village identity and is not enough to join a remaining record.

## CRS

The local spatial source is KML/KMZ. KML specifies geographic coordinates in longitude, latitude, optional altitude order on WGS 84; the KMZ has no additional CRS declaration. Thus the **58 local polygon geometries use the KML WGS 84 geographic convention** (commonly represented as EPSG:4326 for two-dimensional use). This establishes the coordinate convention of the existing geometry only. It does not establish its production CRS, positional accuracy, or boundary vintage.

## Official sources checked in this phase

1. **Survey of India (SOI), Village Boundary Data Base of Entire India.** The official page currently provides a Tamil Nadu vector-data download. The linked file endpoint is `https://surveyofindia.gov.in/documents/TAMILNADU.zip`; its HTTP response reports a ZIP asset, last modified **20 January 2026**, 29,479,075 bytes. The page itself was last updated **10 September 2026**. The SOI Online Maps FAQ identifies the Village Boundary Database as downloadable Shapefile and Geodatabase products, but access is subject to registration category and applicable policy.

   This is the leading authoritative acquisition route. However, the public catalogue/page does not state the archive's field dictionary, Nilgiris feature count, exact LGD field mapping, CRS, boundary vintage/validity period, or licence terms. A temporary download attempt in this phase did not yield a valid inspectable archive, and no external file was copied into the project. Therefore the 2026 SOI release cannot honestly be claimed to cover or reconcile the 102 supplied Village Master IDs.

2. **Tamil Nadu GIS / TNeGA Revenue Village Spatial Extent Generic API.** Its official specification accepts district, taluk, and village LGD-code parameters, demonstrating an LGD-aware service. Its success response is an `extent` (bounding box), not polygon geometry, and the specification does not give a spatial-reference statement, source version/vintage, full feature schema, or licence. It cannot replace a boundary layer.

3. **Ministry of Panchayati Raj LGD catalogue on data.gov.in.** It is an official directory of revenue entities, updated **11 September 2026** when inspected. It can provide an identifier reference after date/version alignment, but it does not provide village polygon geometry and cannot resolve the boundary gap on its own.

## What is still required for a complete resolution

Obtain an inspectable SOI Tamil Nadu Village Boundary Database release, or an equally authoritative TNGIS vector/WFS release, together with its delivery metadata/readme. Before accepting it, record its source URL/accession, download date and hash, licence, release and boundary vintage/validity period, CRS, and data dictionary. Then, without any name-based matching, verify that every Nilgiris feature has a unique authoritative village identifier and that all 102 Village Master LGD codes reconcile exactly (including agreeing district and taluk codes). An official crosswalk is required if the release uses a different valid administrative version or scope.

Until those conditions are met, the unexplained 62/18 difference remains a coverage/vintage blocker. Neither the 40-polygon subset nor the 58 unqualified KMZ features may be presented as a complete Nilgiris village-boundary universe.
