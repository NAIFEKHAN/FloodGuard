# SRTM terrain expansion for exact-ID village polygons

**Phase:** 6C — terrain features only  
**Status:** **PARTIALLY_RESOLVED**

## Result

`data/processed/terrain_features_villages.csv` contains **40** terrain records. They are the complete set of the exact village/district/taluk LGD-code reconciliations established in Phase 6B, not a replacement for the unresolved 102-record Village Master population. The 62 Village Master-only records and 18 KMZ-only records are excluded.

All 40 selected polygons are valid, have no positive-area overlaps, and have finite SRTM elevation and slope cells. This resolves terrain extraction for the maximum currently defensible spatial subset. It remains **PARTIALLY_RESOLVED** because no complete, authoritative, reconciled 102-village boundary layer exists.

## Inputs and provenance

| Input | Provenance / use |
| --- | --- |
| `data/raw/admin/vb_soi_tn.kmz` | Existing SOI-attributed local KMZ. It supplies the polygon geometry only after exact three-code reconciliation. It is read without modification. |
| `data/processed/nilgiris_villages.csv` | Derived from the supplied official Village Master. It supplies village, district, and taluk LGD identifiers plus the preserved English name. |
| `data/raw/dem/N10E076.tif`, `N10E077.tif`, `N11E076.tif`, `N11E077.tif` | Supplied, unchanged SRTM GL1 source tiles. The documented source is OpenTopography's public S3 SRTM GL1 distribution. |
| `data/processed/dem_nilgiris_mosaic.tif` | Existing derived mosaic made from those four tiles without resampling or clipping. SHA-256: `a0fb028feb301ab6338460fdb052f4902cf2dcfe7fab2f837b81b31bfd00606f`. |

The mosaic is one-band `int16`, has nodata value `-32768`, dimensions 7,201 × 7,201 cells, and bounds 75.99986111111112–78.0001388888889 longitude and 9.999861111111112–12.00013888888889 latitude. Its CRS is **EPSG:4326** and its cell size is 0.0002777777777777778 degree (one arc-second, approximately 30 m; metre spacing varies with latitude). All 40 exact polygons intersected it and produced valid cells.

## Exact spatial-unit validation

| Check | Result |
| --- | ---: |
| Exact village/KMZ records retained | 40 |
| Valid geometries | 40 |
| Invalid or missing geometries | 0 |
| Multipart records | 1 |
| Polygon components | 41 |
| Positive-area polygon overlaps | 0 |
| Village Master-only records used | 0 / 62 |
| KMZ-only records used | 0 / 18 |
| Polygons with at least one finite joint elevation/slope cell | 40 / 40 |

An eligible record required exact equality of `vlcode` and `village_lgd_code`, with agreeing `dtcode = district_lgd_code = 587` and `sdcode = taluk_lgd_code`. No displayed names, centroids, nearest geometry, event coordinates, or other inference participated.

## Method

The reusable command is:

```powershell
python pipeline/build_village_terrain.py
```

The command reads the existing mosaic and the 40 exact polygons, then applies a polygon mask with `all_touched=False`: a DEM cell contributes only if its centre lies inside the polygon. It computes slope in degrees from neighbouring DEM elevations using the same formula as the existing point-terrain pipeline, `atan(sqrt((dz/dx)^2 + (dz/dy)^2))`, with geographic pixel dimensions converted to metres at each raster row. A one-cell surrounding window is read only to calculate the slope of selected interior cells; it does not add cells outside the polygon to any summary.

For each polygon, the output reports the count of cells with both finite elevation and finite slope, then mean, minimum, and maximum elevation (metres) and slope (degrees). No values were interpolated, filled, estimated, sampled from a point, or derived from an unmatched unit. The existing DEMO-point table remains unchanged and separate.

## Output validation

`terrain_features_villages.csv` SHA-256: `22569f272079f8c09f2d845ac78721115d8e4547688de349e6f4f71b3a97fe1c`.

| Field | Minimum | Maximum | Missing values |
| --- | ---: | ---: | ---: |
| `dem_valid_cell_count` | 356 | 207,874 | 0 |
| `elevation_mean_m` | 311.182584 | 2,248.827619 | 0 |
| `elevation_min_m` | 282 | 2,005 | 0 |
| `elevation_max_m` | 322 | 2,634 | 0 |
| `slope_mean_deg` | 2.842312 | 29.198969 | 0 |
| `slope_min_deg` | 0 | 2.833355 | 0 |
| `slope_max_deg` | 10.152108 | 79.589567 | 0 |

There are 40 rows, no duplicate village LGD codes, no missing output fields, and no slope value outside 0–90 degrees. The `min`/`max` values in a column can belong to different polygons; they are validation summaries, not a claim that every polygon has the displayed interval.

## Limitations retained

This is a terrain-only polygon summary, not an event linkage, label table, prediction, risk score, or ML input. It does not resolve the incomplete village-boundary population, the event-coordinate provenance limitations, terrain vertical-accuracy limitations, or a non-event observation frame. Do not assign the resulting 40 records to the 62 unmatched Village Master IDs or use their absence as evidence of any kind.
