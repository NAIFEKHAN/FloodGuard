# Administrative village-master provenance and preparation

## Source

`data/raw/admin/Village Master.xlsx` is the supplied **REAL administrative source workbook**. It is not modified by this project.

- Source file path: `data/raw/admin/Village Master.xlsx`
- Source filename: `Village Master.xlsx`
- Workbook sheet used: `Sheet1`
- Worksheet data-row count before filtering: **17,192**
- Nilgiris output record count: **102**

The workbook has one sheet, `Sheet1`, and the following source columns:

```text
dcode, tcode, vcode, lgddcode, lgdtcode, lgdvcode,
dname, dtname, tname, ttname, vname, vtname
```

`dname` is the official English district-name field used for selection. In the supplied workbook, the matching official value is `The Nilgiris`; the extraction also accepts a whitespace/case-normalised `Nilgiris` value to make the documented filter explicit and reproducible.

## Derived output

`data/processed/nilgiris_villages.csv` is **DERIVED ADMINISTRATIVE DATA**, not a boundary dataset, settlement-coordinate dataset, event dataset, target/label table, prediction, or model input.

It preserves these source fields under explicit output names:

| Output column | Source workbook column | Meaning |
| --- | --- | --- |
| `district_code` | `dcode` | Source district code |
| `taluk_code` | `tcode` | Source taluk code |
| `village_code` | `vcode` | Source village code |
| `district_lgd_code` | `lgddcode` | Official district LGD identifier |
| `taluk_lgd_code` | `lgdtcode` | Official taluk LGD identifier |
| `village_lgd_code` | `lgdvcode` | Official village LGD identifier |
| `district_name_en` / `district_name_ta` | `dname` / `dtname` | Official English/Tamil district names |
| `taluk_name_en` / `taluk_name_ta` | `tname` / `ttname` | Official English/Tamil taluk names |
| `village_name_en` / `village_name_ta` | `vname` / `vtname` | Official English/Tamil village names |

The 102 extracted rows have district LGD code `587`, cover six supplied taluk LGD codes (`5754` through `5759`), have no missing preserved name/LGD fields, and have no duplicate village LGD codes.

## Processing and limits

Run from the repository root:

```powershell
python pipeline/build_admin.py
```

The extraction reads only `Sheet1`, selects rows where trimmed/case-folded `dname` is `the nilgiris` or `nilgiris`, trims surrounding whitespace from text fields, and serialises numeric source codes as integer text so identifiers are not written in floating-point notation. No names are translated, replaced, geocoded, or used to infer coordinates or geometry. The worksheet includes one embedded repeated header row among its data rows; it does not match the district filter and is not included in the 102 output records.

This source supplies administrative identifiers and names only. It supplies no village polygons, coordinates, boundary metadata, event linkage, event date, non-event evidence, target labels, rainfall association, or modelling evidence. GSI/NLFC landslide records remain independent and must not be matched to these villages without a separately approved, scientifically valid spatial-linkage phase.
