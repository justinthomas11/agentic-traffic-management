"""
Data Processing Module
Handles loading the Washington DC travel time dataset, computing congestion
metrics, emissions, and decoupling analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def load_dc_data(filepath=None):
    """Load the Washington DC travel times CSV."""
    filepath = filepath or config.DC_TRAVEL_TIMES_CSV
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows from {filepath.name}")
    return df


def compute_congestion_metrics(df, distance_km=None, free_flow_speed=None):
    """
    Compute congestion metrics from travel time data.

    Adds columns: travel_time_sec, average_speed_kmh, free_flow_time_sec,
                  delay_sec, congestion_index
    """
    distance_km = distance_km or config.DC_DISTANCE_KM
    free_flow_speed = free_flow_speed or config.DC_FREE_FLOW_SPEED

    df = df.copy()
    df["travel_time_sec"] = df["Mean Travel Time (Seconds)"]
    df["average_speed_kmh"] = (distance_km / df["travel_time_sec"]) * 3600
    df["free_flow_time_sec"] = (distance_km / free_flow_speed) * 3600
    df["delay_sec"] = df["travel_time_sec"] - df["free_flow_time_sec"]
    df["congestion_index"] = (free_flow_speed - df["average_speed_kmh"]) / free_flow_speed

    print(f"Congestion metrics computed. Mean congestion index: {df['congestion_index'].mean():.3f}")
    return df


def compute_emissions(df, a=None, b=None, c=None, distance_km=None):
    """
    Compute CO2 emissions using quadratic speed-emission model.
    CO2 (g/km) = a + b * speed + c * speed^2

    Adds columns: co2_g_per_km, co2_g_per_trip
    """
    a = a if a is not None else config.EMISSION_A
    b = b if b is not None else config.EMISSION_B
    c = c if c is not None else config.EMISSION_C
    distance_km = distance_km or config.DC_DISTANCE_KM

    df = df.copy()

    # Determine speed column name
    speed_col = "average_speed_kmh" if "average_speed_kmh" in df.columns else "average_speed_kmph"

    df["co2_g_per_km"] = a + b * df[speed_col] + c * (df[speed_col] ** 2)
    df["co2_g_per_trip"] = df["co2_g_per_km"] * distance_km

    print(f"Emissions computed. Mean CO2: {df['co2_g_per_km'].mean():.1f} g/km")
    return df


def compute_decoupling(df, speed_col="average_speed_kmh"):
    """
    Compute emission-congestion decoupling analysis.

    Uses median as baseline, computes percentage changes, decoupling index,
    and classifies into regimes: Coupled, Decoupled (GOOD), Decoupled (BAD).

    Adds columns: delta_congestion/delta_speed, delta_emission,
                  decoupling_index, decoupling_type
    """
    df = df.copy()

    # Determine which baseline to use
    if "congestion_index" in df.columns:
        # DC real-world data
        baseline_metric = df["congestion_index"].median()
        baseline_emission = df["co2_g_per_km"].median()

        df["delta_congestion"] = (df["congestion_index"] - baseline_metric) / baseline_metric
        df["delta_emission"] = (df["co2_g_per_km"] - baseline_emission) / baseline_emission
        df["decoupling_index"] = df["delta_emission"] / df["delta_congestion"]

        # Clean numerical issues
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna(subset=["decoupling_index"])

        def classify(row):
            if row["delta_congestion"] < 0 and row["delta_emission"] < 0:
                return "Coupled"
            elif row["delta_congestion"] < 0 and row["delta_emission"] > 0:
                return "Decoupled"
            else:
                return "Other"

        df["decoupling_type"] = df.apply(classify, axis=1)
    else:
        # Grid simulation data (uses speed instead of congestion_index)
        baseline_speed = df[speed_col].median()
        baseline_emission = df["co2_g_per_km"].median()

        df["delta_speed"] = (df[speed_col] - baseline_speed) / baseline_speed
        df["delta_emission"] = (df["co2_g_per_km"] - baseline_emission) / baseline_emission
        df["decoupling_index"] = df["delta_emission"] / df["delta_speed"]

        # Clean numerical issues
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna(subset=["decoupling_index"])

        def classify_grid(row):
            if row["delta_speed"] > 0 and row["delta_emission"] < 0:
                return "Decoupled (GOOD)"
            elif row["delta_speed"] > 0 and row["delta_emission"] > 0:
                return "Decoupled (BAD)"
            else:
                return "Coupled"

        df["decoupling_type"] = df.apply(classify_grid, axis=1)

    decoupling_dist = df["decoupling_type"].value_counts(normalize=True) * 100
    print(f"Decoupling analysis complete:")
    for regime, pct in decoupling_dist.items():
        print(f"  {regime}: {pct:.1f}%")

    return df


def run_dc_pipeline():
    """Run the full DC data processing pipeline and save intermediate results."""
    # Step 1: Load raw data
    df = load_dc_data()

    # Step 2: Compute congestion metrics
    df = compute_congestion_metrics(df)
    df.to_csv(config.DC_CONGESTION_CSV, index=False)
    print(f"Saved: {config.DC_CONGESTION_CSV.name}")

    # Step 3: Compute emissions
    df = compute_emissions(df)
    df.to_csv(config.DC_EMISSIONS_CSV, index=False)
    print(f"Saved: {config.DC_EMISSIONS_CSV.name}")

    # Step 4: Decoupling analysis
    df = compute_decoupling(df)

    return df


if __name__ == "__main__":
    df = run_dc_pipeline()
    print(f"\nFinal dataset shape: {df.shape}")
    print(df[["average_speed_kmh", "co2_g_per_km", "congestion_index", "decoupling_type"]].head())
