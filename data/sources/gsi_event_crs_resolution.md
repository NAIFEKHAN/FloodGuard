# GSI/NLFC event CRS and datum resolution

**Phase:** 6A — event CRS/datum only  
**Status:** **PARTIALLY_RESOLVED**

## Authoritative determination

**The CRS/datum of this exact 772-row PDF release cannot be authoritatively established from
the supplied file and publicly reviewed release metadata.** The result is therefore
**PARTIALLY_RESOLVED**, not `RESOLVED`.

Authoritative Government of India and GSI/NLFC documentation establishes the convention for
the matching GSI landslide-inventory schema: `Latitude` and `Longitude` are decimal degrees
on the **WGS 1984 datum**. For two-dimensional geographic coordinates, that convention is
represented as **WGS 84 / EPSG:4326**. The local source table has the corresponding header
sequence (`Slide_No`, State, District, Slide_Name, NH/SH/Locality, Latitude, Longitude,
Material Involved, Movement Type, History).

That is authoritative schema-level evidence, but it does **not** prove that the supplied PDF
is an identified release governed by that schema. The file has no issuer, release/version,
download URL, field dictionary, capture-method statement, or accuracy statement. It would
therefore be an unsupported assumption to certify WGS 84 / EPSG:4326 as the CRS of every
record in this particular file. This note does not claim that any point is an accurate
landslide centroid or has stated positional accuracy.

This conclusion is based on the field specification, not on coordinate ranges, map display,
or a spatial relationship with any other dataset.

## Authoritative evidence used

1. The Government of India National Institute of Disaster Management's *Compendium on
   National Landslide Risk Management Strategy*, Annexure II, **"Detailed geo-parametric
   attributes for landslide inventory"**, defines:
   
   - field 7 `Latitude`: "Lat in decimal degree (using WGS 1984 Datum)"; and
   - field 8 `Longitude`: "Long in decimal degree (using WGS 1984 Datum)".

   The same annexure defines the GSI-style `Slide No.` pattern and the surrounding inventory
   fields.  Official source: <https://nidm.gov.in/pdf/guidelines/new/CompendiumNLRMS.pdf>
   (Annexure II, PDF page 46 as indexed by the official document).

2. A GSI/NLFC-hosted field incident report independently labels its 42-point
   geo-parametric inventory fields as `Latitude` and `Longitude` with **"WGS 1984 Datum"**.
   Official source: <https://bhusanket.gsi.gov.in/Output/LS_Incidence_Report/2021/Landslides%20at%20Bhairabkunda%2C%20Udalguri%20District%2C%20Arunachal%20Pradesh%20%2828th%20April%2021%29.pdf>.
   This corroborates that the formal inventory field specification is used in GSI/NLFC
   reporting.  That report concerns a different incident and is not represented as the
   release record for the local PDF.

3. The supplied source PDF, `data/raw/events/landslide_report.pdf`, pages 693--717, prints
   the matching table header and field sequence (directly rechecked in this phase). Its
   embedded metadata contains only `/Producer: pypdf`; it does not itself state a CRS/datum.
   The processed extraction
   preserves those printed latitude and longitude columns in
   `data/processed/landslide_events.csv`.

4. The supplied Nilgiris DDMP, `data/raw/disaster/Nilgiris-DDMP.pdf`, has no CRS/datum
   statement for its separately printed coordinates.  Its GSI August-2019 table is a
   different 77-row documentary table and was not used to establish, match, or validate the
   772-row inventory.

The prior `gsi_metadata_audit.md` remains correct on the narrower evidence then available:
it found no **release-specific** CRS declaration in the local PDF or the reviewed current
portal pages.  Items 1--2 above add authoritative documentation for the inventory schema,
but do not retroactively supply a release identifier for the local file.

## Validation of the 772 extracted coordinates

Because the exact-release CRS remains unresolved, this is **conditional numeric validation**,
not a validation of CRS correctness or spatial position. It tests the 772 extracted values
against the documented GSI schema's decimal-degree WGS 1984 domain and printed column order.
It did not compare points with village boundaries, DDMP records, terrain, rainfall, geocoders,
imagery, or maps.

| Check | Result |
| --- | ---: |
| CSV rows | 772 |
| Blank `latitude` values | 0 |
| Blank `longitude` values | 0 |
| Numeric parse failures | 0 |
| Values outside WGS 84 geographic-domain limits (`latitude` -90..90; `longitude` -180..180) | 0 |
| Latitude range | 11.210556 to 11.550000 |
| Longitude range | 76.24763889 to 76.95066827 |
| Unique latitude/longitude pairs | 746 |
| CSV SHA-256 | `b3371db8fefdc5a37304d1ccc7f03bed064212c6e2ce930cdf70f3c2f8336dff` |

All 772 rows pass the **conditional** numerical/domain validation for the documented
`Latitude`, then `Longitude`, WGS 1984 decimal-degree schema. The 26 repeated
coordinate-pair occurrences are retained source values; repetition is not treated as an error
without release-specific duplicate rules. Passing this check establishes neither the CRS of
the supplied release, event-location accuracy, nor compatibility with a particular boundary
vintage.

## Remaining blocker

The datum is sufficiently documented for the **inventory-schema convention**, but not for the
exact local release. The following evidence is required for a fully release-resolved result:

- GSI/NLFC confirmation, accession, persistent source URL, or release/version record that
  ties `data/raw/events/landslide_report.pdf` (SHA-256
  `3ec13c41230ef7436b7169f6a828e38db429e4c2b5aa054de51821423af5ce2a`) to that
  specification;
- a release-specific data dictionary confirming the exact coordinate semantics (for example,
  crown, body, toe, road-impact point, or another reference location);
- coordinate capture method, observation/validation date, precision, stated horizontal
  accuracy, and any transformation history; and
- release-specific duplicate, correction, and completeness rules.

Until this is supplied, the result must not be elevated to a release-specific positional
accuracy certification and must not be used to perform event--village linkage, create labels,
or make model/risk claims.
