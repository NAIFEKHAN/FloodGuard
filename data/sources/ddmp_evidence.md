# Nilgiris DDMP evidence extraction

**Source:** `data/raw/disaster/Nilgiris-DDMP.pdf` (630 PDF pages). This is a source-faithful extraction only. It does not create event links, village identities, CRS assumptions, labels, negative samples, predictions, or models.

## Extracted structured tables

| Derived DDMP-only artifact | Source table/pages | Records | Notes |
| --- | --- | ---: | --- |
| `data/processed/disaster/ddmp_proposed_arg_stations.csv` | Table 2.6, PDF pages 16–17 | 35 | Proposed Automatic Rainguage Stations; values are transcribed as printed. |
| `data/processed/disaster/ddmp_aws_stations.csv` | List of Automatic Weather Stations, PDF page 17 | 4 | The DDMP gives block, latitude, longitude, address/location, and remarks. It gives no AWS station name/code field; the CSV leaves that field blank rather than inventing one. |
| `data/processed/disaster/ddmp_vulnerable_location_summary.csv` | Table 5.5, PDF page 102 | 7 | Six taluks plus the printed total. These are official vulnerability classifications only, never ML labels or negative-sample evidence. |

The DDMP prints an August-2019 GSI table with 77 rows (Table 5.3, PDF pages 71–75), but no event CSV was created: its multi-page visual table uses DMS strings, irregular typography, and source text errors. Creating an automated row-level CSV without a table-validation workflow risked altering or joining fields. The original table remains the authoritative record for the listed place, latitude, longitude, nature of slide, and damage text; it has not been merged with `landslide_events.csv`.

## Rain-gauge evidence

Table 2.5 (PDF page 15) states that the district has **29 rainfall registering stations** and lists: Udhagamandalam, Masinagudi, Naduvattam, Glenmorgan, Kallatti, Kundah Bridge, Balacola, Geddai, Emerald, Avalanchi, Kinnakorai, Upperbhavani, Coonoor, Coonoor Rural, Yedappalli, Burliar, Ketti, Hulical, Kotagiri, Denad, Kodanad, Gudalur, O’ Valley, Upper Gudalur, Devala, Cherumulli, Padanthorai, Pandalur, and Cherangode. The table gives no station codes or coordinates, so none were inferred.

Table 2.6 explicitly labels the 35 coordinate/code records as **“Proposed Automatic Rainguage Stations.”** The extracted CSV preserves the DDMP’s taluk, village, building name, coordinates, and station codes. It does not assert commissioning status, datum, sensor history, or rainfall availability.

## AWS evidence

The DDMP’s AWS list has four records: Udhagai, Coonoor, Gudalur, and Kotagiri. Their printed coordinate/address/remark fields are retained in the AWS CSV. The document does not supply AWS identifiers, CRS/datum, temporal coverage, or measurement completeness; those properties must not be inferred.

## August 2019 GSI table

Table 5.3 is headed **“Summary of Landslide during August 2019 recorded by GSI.”** It supplies 77 numbered records with exactly these columns: place name, latitude, longitude, nature of slide, and damage to life or property (PDF pages 71–75).

The surrounding DDMP narrative (PDF page 76) states that South West Monsoon rainfall began from **05.05.2019 onwards** and that, during **06.08.2019 to 09.08.2019**, average rainfall was about 642 mm. It calls the second week of August 2019 the period of unprecedented high rainfall. This is a narrative event window for the table context; the table does not print an individual occurrence date for each of its 77 rows. The coordinate strings remain source text, not converted coordinates, and no CRS/datum is stated by this DDMP table.

## Historical landslide/disaster chronology stated in the DDMP

| DDMP section | Explicit stated date/window or period | Stated occurrence summary |
| --- | --- | --- |
| North-East Monsoon 1978–79 | 4–5 Nov 1978; 12–29 Nov 1979; named incidents 15, 16, 19 and 20 Nov 1979 | Flood/landslide disaster chronology around Ootacamund, Manthada, Kookalthorai, Coonoor, Doddacombai, and Selas. |
| North-East Monsoon 1990 | 25.10.1990 | Heavy rains/flash floods at Pegumbahallah / Geddai Camp. |
| North-East Monsoon 1993 | 10–12 Nov 1993; cloudburst 11.11.1993 | Coonoor/Kotagiri/Udhagamandalam heavy rain; Marapalam cloudburst impacts. |
| North-East Monsoon 1998 | 09.12.1998–14.12.1998 | Boulder/earthslip effects on Coonoor–Mettupalayam road. |
| North-East Monsoon 2001 | night of 26 Dec 2001 | Landslides near Pudukadu and transport damage. |
| North-East Monsoon 2006 | late hours of 14.11.2006 | Numerous reported landslides. |
| North-East Monsoon 2009 | 2009 (no daily date stated in this section) | Around 1,150 landslips and stated impacts. |
| Summer rainfall 2015 | 07.03.2015 | Coonoor flooding and minor landslips. |
| North-East Monsoon 2017 | 2017 (no daily date stated) | Damage table only. |
| South-West Monsoon 2018 | 2018 (no daily date stated) | Damage table only. |
| South-West Monsoon 2019 | from 05.05.2019; 06.08.2019–09.08.2019 | Heavy-rainfall and damage narrative; GSI August table above. |
| North-East Monsoon 2019 | early hours of 17.11.2019 | Coonoor rain, landslides, uprooted trees, and flash flood narrative. |
| South-West Monsoon 2020 | 03.08.2020–09.08.2020 | Heavy-rainfall and damage narrative. |
| South-West / North-East Monsoon 2022 | 12.07.2022–15.07.2022; 08.08.2022–12.08.2022; 12–14.12.2022 | Gudalur rainfall impacts and later Coonoor/Udhagai events. |
| North-East Monsoon 2023 | 22.11.2023 to 23.11.2023 | Mettukal hamlet rainfall and landslip figure. |
| Site-specific GSI study | 17.07.2024 | Govt. Hospital Complex, Upper Gudalur landslide figure/study statement. |

The chronology is documentary context only. It has not been converted into new inventory records, reconciled with existing records, or used for target labels.

## Official vulnerable-location classification

Table 5.5, **“Abstract of Vulnerable Locations,”** preserves the following classifications exactly:

| Taluk | Very Highly Vulnerable | Highly Vulnerable | Medium Vulnerable | Low Vulnerable | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Udhagai | 12 | 18 | 35 | 8 | 73 |
| Kundah | 7 | 10 | 13 | 13 | 43 |
| Coonoor | 19 | 25 | 5 | 21 | 70 |
| Kotagiri | 27 | 35 | 15 | 4 | 81 |
| Gudalur | 2 | 1 | 1 | 1 | 6 |
| Pandalur | 1 | 0 | 8 | 1 | 10 |
| **Total** | **68** | **89** | **77** | **48** | **283** |

The narrative preceding Table 4.1 (PDF page 51) says 283 areas were identified based on legacy data and classified into four categories. Detailed vulnerable-hamlet tables appear on PDF pages 103–118, including a “Newly identified vulnerable areas – Based on recent landslide events” table. The DDMP does not establish these classes as observed event/non-event outcomes, monitoring coverage, or probability labels. They must not be used as supervised ML targets, negative samples, or fabricated risk scores.

## Scientific limitations retained

- The DDMP does not state the CRS/datum for the printed station, GSI-event, or vulnerable-location coordinates.
- A location/village name in this document is not treated as an LGD identity or linked to project boundary data.
- The GSI August-2019 rows remain independent from the existing 772-event inventory.
- No chronology entry is inferred beyond its stated date precision.
- DDMP vulnerability classes are planning classifications, not an event observation frame and not evidence that unlisted areas/times are negative.
