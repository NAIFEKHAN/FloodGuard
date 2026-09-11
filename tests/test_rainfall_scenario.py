"""Unit tests for Phase B Rainfall Scenario Engine."""

from pathlib import Path
import hashlib
import pandas as pd
import numpy as np
from pipeline.run_rainfall_scenario import (
    load_model_and_dataset,
    evaluate_scenario,
    run_all_presets,
    classify_scenario_tier,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data/processed"


def test_scenario_engine_evaluates_all_40_villages() -> None:
    model, df = load_model_and_dataset()
    assert len(df) == 40

    res = evaluate_scenario(df, model, scenario_key="heavy")
    assert len(res) == 40
    assert res["village_lgd_code"].nunique() == 40
    assert not res.isnull().any().any(), "Scenario results must not contain NaN"
    assert np.all(np.isfinite(res["scenario_susceptibility_0_100"])), "Scenario scores must be finite"


def test_scenario_engine_does_not_mutate_source_dataset() -> None:
    dataset_path = DATA_PROCESSED / "ml_spatial_dataset.csv"
    initial_bytes = dataset_path.read_bytes()
    initial_hash = hashlib.sha256(initial_bytes).hexdigest()

    model, df = load_model_and_dataset()
    _ = evaluate_scenario(df, model, scenario_key="extreme", multiplier=3.0)

    post_bytes = dataset_path.read_bytes()
    post_hash = hashlib.sha256(post_bytes).hexdigest()

    assert initial_hash == post_hash, "Source dataset ml_spatial_dataset.csv was mutated during scenario execution!"


def test_scenario_rainfall_variation_and_static_terrain() -> None:
    model, df = load_model_and_dataset()

    res_mod = evaluate_scenario(df, model, scenario_key="moderate")
    res_ext = evaluate_scenario(df, model, scenario_key="extreme")

    # Static terrain must be identical
    np.testing.assert_array_equal(res_mod["elevation_mean_m"], res_ext["elevation_mean_m"])
    np.testing.assert_array_equal(res_mod["slope_mean_deg"], res_ext["slope_mean_deg"])

    # Rainfall-dependent features must vary
    assert (res_ext["scenario_rainfall_7d_p95_mm"] > res_mod["scenario_rainfall_7d_p95_mm"]).all()

    # Extreme scenario mean score must exceed moderate scenario mean score
    assert res_ext["scenario_susceptibility_0_100"].mean() > res_mod["scenario_susceptibility_0_100"].mean()


def test_preset_scenarios_and_tier_classification() -> None:
    composite_df = run_all_presets()

    assert len(composite_df) == 160  # 40 villages * 4 presets
    assert set(composite_df["scenario_key"].unique()) == {"moderate", "baseline", "heavy", "extreme"}

    for _, row in composite_df.iterrows():
        score = row["scenario_susceptibility_0_100"]
        tier = row["scenario_tier"]
        expected_tier = classify_scenario_tier(score)
        assert tier == expected_tier, f"Tier mismatch for score {score}: expected {expected_tier}, got {tier}"
