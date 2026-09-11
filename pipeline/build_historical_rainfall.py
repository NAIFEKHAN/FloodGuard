"""Reproducibly process approved historical IMD NetCDF files for DEMO settlements."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from rainfall.processing import (
    OUTPUT_COLUMNS,
    RainfallPipelineError,
    build_historical_rainfall_features,
    write_rainfall_features,
)


DEFAULT_YEAR_FILES = {
    2017: Path("data/raw/rainfall/RF25_ind2017_rfp25.nc"),
    2019: Path("data/raw/rainfall/RF25_ind2019_rfp25.nc"),
    2022: Path("data/raw/rainfall/RF25_ind2022_rfp25.nc"),
    2023: Path("data/raw/rainfall/RF25_ind2023_rfp25.nc"),
    2024: Path("data/raw/rainfall/RF25_ind2024_rfp25.nc"),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_metadata(year_files: dict[int, Path], features: pd.DataFrame) -> dict[str, object]:
    sources: list[dict[str, object]] = []
    for year, path in sorted(year_files.items()):
        with xr.open_dataset(path) as dataset:
            sources.append({
                "year": year, "path": str(path).replace("\\", "/"), "sha256": _sha256(path),
                "dimensions": {name: int(size) for name, size in dataset.sizes.items()},
                "variable": "RAINFALL", "units": str(dataset["RAINFALL"].attrs.get("units", "")),
                "latitude_range": [float(dataset["LATITUDE"].min()), float(dataset["LATITUDE"].max())],
                "longitude_range": [float(dataset["LONGITUDE"].min()), float(dataset["LONGITUDE"].max())],
                "date_range": [str(pd.Timestamp(dataset["TIME"].values[0]).date()), str(pd.Timestamp(dataset["TIME"].values[-1]).date())],
                "record_count": int(features[features["date"].dt.year == year].shape[0]),
            })
    return {
        "artifact_classification": "REAL_DERIVED_FROM_IMD_FOR_DEMO_SETTLEMENTS_ONLY",
        "methodology": "Existing nearest IMD grid-cell selection and 1/3/7-day rolling sums; no interpolation or imputation.",
        "settlement_input_classification": "DEMO",
        "sources": sources,
        "total_record_count": int(len(features)),
    }


def _verify_2024_compatibility(features: pd.DataFrame, baseline_path: Path) -> None:
    """Refuse to replace a historical artifact if its 2024 values differ from the prior output."""
    if not baseline_path.is_file():
        raise RainfallPipelineError(f"Existing 2024 rainfall feature output was not found: {baseline_path}")
    try:
        baseline = pd.read_csv(baseline_path, parse_dates=["date"])
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise RainfallPipelineError(
            f"Unable to read existing 2024 rainfall feature output '{baseline_path}': {error}"
        ) from error

    current = features.loc[features["date"].dt.year == 2024, OUTPUT_COLUMNS]
    required = set(OUTPUT_COLUMNS)
    if not required.issubset(baseline.columns):
        raise RainfallPipelineError("Existing 2024 rainfall feature output has an incompatible schema.")
    baseline = baseline.loc[:, OUTPUT_COLUMNS]
    current = current.sort_values(["settlement_id", "date"], kind="stable").reset_index(drop=True)
    baseline = baseline.sort_values(["settlement_id", "date"], kind="stable").reset_index(drop=True)
    try:
        identity_columns = ("settlement_id", "settlement_name", "region", "district", "date")
        pd.testing.assert_frame_equal(
            current.loc[:, identity_columns], baseline.loc[:, identity_columns], check_dtype=False
        )
        numeric_columns = tuple(column for column in OUTPUT_COLUMNS if column not in identity_columns)
        if not np.allclose(
            current.loc[:, numeric_columns].to_numpy(dtype=float),
            baseline.loc[:, numeric_columns].to_numpy(dtype=float),
            rtol=0.0,
            atol=1e-12,
            equal_nan=True,
        ):
            raise AssertionError("Numeric rainfall output differs beyond CSV floating-point precision.")
    except AssertionError as error:
        raise RainfallPipelineError(
            "Parameterised 2024 rainfall values differ from the previous output; "
            "historical output was not overwritten."
        ) from error


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process approved IMD years without changing the rainfall methodology.")
    parser.add_argument("--settlements", type=Path, default=Path("data/demo/settlements_demo.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/historical_rainfall_features.csv"))
    parser.add_argument("--provenance", type=Path, default=Path("data/processed/historical_rainfall_provenance.json"))
    parser.add_argument("--baseline-2024", type=Path, default=Path("data/processed/rainfall_features.csv"))
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        features = build_historical_rainfall_features(DEFAULT_YEAR_FILES, arguments.settlements)
        _verify_2024_compatibility(features, arguments.baseline_2024)
        write_rainfall_features(features, arguments.output)
        arguments.provenance.parent.mkdir(parents=True, exist_ok=True)
        arguments.provenance.write_text(json.dumps(_source_metadata(DEFAULT_YEAR_FILES, features), indent=2) + "\n", encoding="utf-8")
    except (OSError, RainfallPipelineError) as error:
        print(f"Historical rainfall processing failed: {error}")
        return 1
    print(f"Wrote {len(features)} DEMO settlement-day rainfall rows to: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
