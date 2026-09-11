# Nilgiris DDMP evidence register

**Authoritative source:** `data/raw/disaster/Nilgiris-DDMP.pdf` (630 pages; SHA-256 `fe7affb36e70148c607ea1d291ad67999af7ad23cb7e5f27a7168f9d0ec50ea1`). The reproducible extractor is `pipeline/extract_ddmp_evidence.py`.

This register preserves only what is explicitly stated by the supplied PDF. It is not a spatial dataset, an event-to-village join, a target/label file, or a prediction input.

| Evidence item | Explicit DDMP count | Source pages | Preservation decision |
| --- | ---: | --- | --- |
| Proposed Automatic Rainguage Stations (Table 2.6) | 35 | 16–17 | Existing source-faithful station CSV is retained; no commissioning status, CRS/datum, temporal coverage, or rainfall availability is inferred. |
| Automatic Weather Stations list | 4 | 17 | Existing source-faithful AWS CSV is retained; no station identifier, CRS/datum, temporal coverage, or rainfall availability is inferred. |
| “Summary of Landslide during August 2019 recorded by GSI” (Table 5.3) | 77 | 71–75 | Preserved as page-faithful source evidence. No row CSV is added because the printed multi-page layout and extracted typography would require normalising fields, coordinates, and page-break text. |
| August 2019 DDMP rainfall narrative | — | 76 | The narrative states SW monsoon rainfall from 05.05.2019 onward and 642 mm during 06.08.2019–09.08.2019. It does not give an individual occurrence date for every Table 5.3 row. |
| Historical disaster chronology | — | DDMP historical-disaster section; 76–82 for later entries | Kept as documentary chronology only. Stated period/date precision is not expanded into event dates or inventory rows. |
| Abstract of Vulnerable Locations (Table 5.5) | 283 (printed) | 102 | Official planning classifications: VHV 68, HV 89, MV 77, LV 48. The printed class totals sum to 282 while the table prints 283; the discrepancy is preserved, not reconciled. |
| Detailed vulnerable-hamlet tables corresponding to Table 5.5 | 283 | 103–116 | Preserved as page-faithful source evidence. No row CSV is added because a reliable row/field transcription cannot be made from the PDF layout without interpretation. |

## Official vulnerable-location classification total

| Taluk | Very Highly Vulnerable | Highly Vulnerable | Medium Vulnerable | Low Vulnerable | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Udhagai | 12 | 18 | 35 | 8 | 73 |
| Kundah | 7 | 10 | 13 | 13 | 43 |
| Coonoor | 19 | 25 | 5 | 21 | 70 |
| Kotagiri | 27 | 35 | 15 | 4 | 81 |
| Gudalur | 2 | 1 | 1 | 1 | 6 |
| Pandalur | 1 | 0 | 8 | 1 | 10 |
| **Total** | **68** | **89** | **77** | **48** | **283** |

## Limits

- The PDF does not state a CRS or datum for printed coordinates. None is assumed.
- GSI Table 5.3 rows are not merged with the project landslide inventory.
- Vulnerability classes are official planning classifications, not observed outcomes, negative evidence, or ML labels.
- Table 5.5 prints a 283 grand total but its four printed class totals add to 282. No missing record or classification is inferred to resolve this.
- Location and village text remains independent from project administrative/boundary data.
- `pipeline/extract_ddmp_evidence.py` extracts the cited pages into `data/sources/ddmp_pdf_evidence_extract.md` when run in an environment that permits programmatic workspace writes.
