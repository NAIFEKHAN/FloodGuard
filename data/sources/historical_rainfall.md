# Historical IMD rainfall processing

This bounded processing phase applies the existing IMD rainfall method independently to approved source years 2017, 2019, 2022, 2023, and 2024. It produces `data/processed/historical_rainfall_features.csv` only for the two existing **DEMO** settlement coordinates. It is not an official village dataset, event linkage, label table, prediction, score, or model input.

Run from the repository root:

```powershell
python pipeline/build_historical_rainfall.py
```

The command reads the five approved `RF25_indYYYY_rfp25.nc` source files and writes a combined, date-sorted feature table plus `historical_rainfall_provenance.json`. Provenance records source filenames, SHA-256 hashes, years, record counts, grid dimensions/ranges, variable units, and source date ranges. Before it writes the combined artifact, it compares its 2024 rows with the prior `rainfall_features.csv`; a mismatch stops the command without replacing the historical artifact.

The method is unchanged from the existing 2024 processor: each DEMO point is selected from its nearest IMD grid cell using xarray coordinate selection; daily rainfall comes directly from `RAINFALL`; 3- and 7-day totals are trailing calendar-day rolling sums. No interpolation, alternate source, or missing-value imputation occurs. Each source year begins a fresh rolling window, so its initial two 3-day and initial six 7-day values remain null.

## Validated derived artifact

`historical_rainfall_features.csv` contains 3,652 DEMO settlement-day rows. Both existing DEMO settlement coordinates select IMD cell **11.50, 76.75**. The source grids are compatible: 129 latitude cells from 6.5 to 38.5 and 135 longitude cells from 66.5 to 100.0, at 0.25-degree spacing.

| Year | Date coverage | Rows |
| --- | --- | ---: |
| 2017 | 2017-01-01 to 2017-12-31 | 730 |
| 2019 | 2019-01-01 to 2019-12-31 | 730 |
| 2022 | 2022-01-01 to 2022-12-31 | 730 |
| 2023 | 2023-01-01 to 2023-12-31 | 730 |
| 2024 | 2024-01-01 to 2024-12-31 | 732 |

There are zero missing selected daily rainfall values. The 20 null 3-day totals and 60 null 7-day totals are exactly the expected leading rolling-window nulls: two and six respectively for each of two DEMO settlements in each of five independently processed years. They are retained as nulls, never imputed. The 732 parameterized 2024 rows match the existing 2024 feature output in every output field.
