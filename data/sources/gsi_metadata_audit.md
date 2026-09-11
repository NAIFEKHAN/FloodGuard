# GSI/NLFC landslide-inventory metadata audit

**Scope:** read-only review of the supplied `data/processed/landslide_events.csv` provenance against official Geological Survey of India / National Landslide Forecasting Centre (GSI/NLFC) public sources only. No coordinate reference is inferred from coordinate values, display format, KML compatibility, or web-map defaults. No dataset, event linkage, label, prediction, or model was created or changed.

**Local inventory under review:** 772 Nilgiri rows extracted from the supplied `data/raw/events/landslide_report.pdf`. The source PDF identifies only `pypdf` as producer and does not state a publisher, release/version, publication date, original download URL, CRS/datum, coverage/completeness statement, or field dictionary that can be tied to this specific file.

## Decision summary

| Requested metadata item | Status | Decision |
| --- | --- | --- |
| CRS / datum | **BLOCKED** | No reviewed official GSI/NLFC source states the CRS, EPSG code, datum, axis convention, or positional accuracy for the supplied inventory release. |
| Coordinate meaning | **PARTIALLY_READY** | Official current reporting materials distinguish latitude and longitude as landslide-report fields, but no reviewed source defines those fields for this supplied historical PDF or confirms capture method/accuracy. |
| Event date / date range | **PARTIALLY_READY** | The current official form distinguishes occurrence date/time and occurrence date range. It does not establish that the local PDF's heterogeneous `History` field has those same semantics. |
| Dataset coverage | **BLOCKED** | Official sources describe a national inventory/repository and a field-validated portal product, but do not document geographical coverage, time coverage, inclusion rule, detection threshold, or reporting completeness for this 772-row Nilgiri extract. |
| Dataset version / source | **PARTIALLY_READY** | GSI/NLFC is an official provider of a portal product labelled “Landslide Inventory (Field Validated),” but no official release identifier, issue date, file hash, version, download URL, or source-to-file correspondence was found for the supplied PDF. |

## Official evidence reviewed

1. The [GSI/NLFC Bhusanket portal](https://bhusanket.gsi.gov.in/) is hosted by GSI and currently presents a downloadable product labelled **“Landslide Inventory (Field Validated).”** This establishes an official provider and current product label, but the page’s disclaimer says the information is periodically updated and does not guarantee completeness or currency. It does not expose release-specific CRS, datum, field definitions, coverage, or version metadata for the supplied PDF.

2. The [GSI/NLFC FAQ](https://bhusanket.gsi.gov.in/faq.html) describes a landslide inventory as a georeferenced spatial database in which each landslide has spatial and temporal attributes, and describes the Web-based National Landslide Incidence Inventory as a national repository initiative. This is programme-level context. It does not document the coordinate reference, data dictionary, version, completeness, or date semantics of the local inventory file.

3. The [GSI/NLFC public landslide reporting form](https://bhusanket.gsi.gov.in/LandslideReport.html) has separate inputs for latitude, longitude, occurrence date/time, source of information, and occurrence date range. It supports the conclusion that the current reporting workflow distinguishes these concepts. It is not evidence that the historical PDF’s latitude/longitude or `History` field uses the same definitions, precision, datum, or validation rules.

4. The [GSI project-metadata page](https://bhusanket.gsi.gov.in/projectMetadata.html) requests project location latitude/longitude, study period, and number of landslides studied. It confirms that GSI project documentation can record those items, but it is a submission template for project metadata, not metadata for the supplied inventory release.

## Item-by-item assessment

### CRS / datum — BLOCKED

No reviewed official GSI/NLFC page specifies an EPSG code, geographic datum, projected CRS, axis order, coordinate-capture method, or expected positional accuracy for the supplied inventory PDF. The public form’s latitude and longitude labels and the FAQ’s use of “georeferenced” do not identify a datum. Accordingly, its coordinates cannot be treated as CRS-compatible with the SOI/TNGIS KMZ, IMD grid, SRTM mosaic, or any proposed village geometry.

**Required evidence:** written GSI/NLFC confirmation applying specifically to the supplied inventory release, including CRS/EPSG, datum, axis convention, coordinate semantics, capture method, precision/accuracy, and release/version identifier.

### Coordinate meaning — PARTIALLY_READY

The current public form makes latitude and longitude mandatory report fields and associates them with a landslide report. This is authoritative evidence of the current portal’s intended reporting concepts. It does not establish whether the local PDF’s values are point locations of the crown, body, toe, road impact, settlement impact, reporter location, or another reference point; nor does it establish their accuracy or datum.

**Permitted conclusion:** the local fields are source-provided coordinate values.  
**Not permitted:** calling them validated event centroids/points or assigning them to villages, polygons, cells, or terrain pixels.

### Event date and date range — PARTIALLY_READY

The official current reporting form separately records occurrence date/time and occurrence date range. This supports preserving date precision and not collapsing a range into a single day. The local source’s `History` field cannot be assumed to be an occurrence date, reporting date, date range, or validation date merely because it includes date-like text. Existing conservative processing correctly keeps only a single complete, unambiguous source date in `reported_history_date`; year-only, ambiguous, and `NA` values remain unknown.

**Required evidence:** a release-specific field dictionary defining `History`, date, date range, occurrence date, reporting date, and validation date, plus any rules used to populate them.

### Dataset coverage — BLOCKED

The official FAQ describes an intended national repository, while the portal publishes a current field-validated inventory product. Neither reviewed source documents a complete observation frame for the supplied file: no inventory inclusion criteria, geographic coverage boundary, study period, reporting pathway, validation threshold, detection limit, update cut-off, or false-negative/completeness statement was found. The portal disclaimer explicitly prevents treating its displayed information as guaranteed complete or current.

**Consequence:** absence of a record cannot establish `no landslide` for a village, pixel, grid cell, or date.

### Dataset version / source — PARTIALLY_READY

The official portal establishes GSI/NLFC as the provider of a current product bearing the same general “Field Validated” inventory label. The supplied PDF has no authoritative source URL or release metadata tying it to a particular portal download, database snapshot, field season, publication date, or version. The current portal count must not be substituted for the supplied 772-row inventory or used to infer its coverage/version.

**Required evidence:** provider confirmation of the supplied file’s provenance, release/version date, persistent download URL or accession identifier, record-count scope, update cut-off, and any revision history.

## Final conclusion

The reviewed official material improves programme-level understanding but does **not** close the metadata gates for the supplied inventory. CRS/datum and coverage remain **BLOCKED**. Coordinate and date concepts, and provider/product identity, are only **PARTIALLY_READY** because the available documentation concerns current GSI/NLFC workflows or products rather than this exact historical PDF release.

Do not conduct event-village linkage, target construction, negative sampling, or ML until the required release-specific GSI/NLFC documentation is obtained.
