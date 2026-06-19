"""
Grid Simulation Module
Simulates OD trips on grid-based intersection networks with configurable
delay models for signalized, unsignalized, and high-volume intersections.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from src.data_processing import compute_emissions, compute_decoupling


class GridSimulator:
    """
    Simulates traffic on a grid network with parameterized intersection delays.
    """

    def __init__(
        self,
        name,
        delay_range,
        grid_size=None,
        block_length_km=None,
        speed_limit=None,
        od_trips=None,
        trips_per_type=None,
        seed=None,
    ):
        self.name = name
        self.delay_min, self.delay_max = delay_range
        self.grid_size = grid_size or config.GRID_SIZE
        self.block_length_km = block_length_km or config.BLOCK_LENGTH_KM
        self.speed_limit = speed_limit or config.GRID_SPEED_LIMIT
        self.od_trips = od_trips or config.OD_TRIPS
        self.trips_per_type = trips_per_type or config.TRIPS_PER_TYPE
        self.seed = seed or config.RANDOM_SEED

    def generate(self):
        """Generate grid OD trip dataset with random intersection delays."""
        np.random.seed(self.seed)
        grid_data = []

        for trip_type, num_intersections in self.od_trips.items():
            distance_km = num_intersections * self.block_length_km

            for _ in range(self.trips_per_type):
                # Random delay per intersection
                delay_per_intersection = np.random.uniform(
                    self.delay_min, self.delay_max
                )
                total_delay = num_intersections * delay_per_intersection

                # Cruise time (no intersection delay)
                cruise_time_sec = (distance_km / self.speed_limit) * 3600

                # Total travel time
                total_time_sec = cruise_time_sec + total_delay

                grid_data.append([
                    trip_type,
                    num_intersections,
                    distance_km,
                    total_delay,
                    total_time_sec,
                ])

        df = pd.DataFrame(
            grid_data,
            columns=[
                "trip_type",
                "num_intersections",
                "distance_km",
                "total_delay_sec",
                "total_travel_time_sec",
            ],
        )

        # Compute speed
        df["average_speed_kmph"] = (df["distance_km"] / df["total_travel_time_sec"]) * 3600

        # Compute emissions
        df = compute_emissions(df)

        print(f"[{self.name}] Generated {len(df)} trips")
        print(f"  Delay range: [{self.delay_min}, {self.delay_max}] sec/intersection")
        print(f"  Mean speed: {df['average_speed_kmph'].mean():.2f} km/h")
        print(f"  Mean CO2: {df['co2_g_per_km'].mean():.1f} g/km")

        return df

    def generate_with_decoupling(self):
        """Generate grid data and compute decoupling analysis."""
        df = self.generate()
        df = compute_decoupling(df, speed_col="average_speed_kmph")
        return df


def create_all_simulators():
    """Create simulators for all three intersection types."""
    return {
        "signalized": GridSimulator(
            name="Grid Signalized (4-way)",
            delay_range=config.DELAY_SIGNALIZED,
        ),
        "unsignalized": GridSimulator(
            name="Grid Unsignalized",
            delay_range=config.DELAY_UNSIGNALIZED,
        ),
        "high_volume": GridSimulator(
            name="Grid High Volume",
            delay_range=config.DELAY_HIGH_VOLUME,
        ),
    }


def run_all_grid_simulations():
    """Run all three grid simulations and save results."""
    simulators = create_all_simulators()
    results = {}

    # Signalized
    print("\n" + "=" * 60)
    df_sig = simulators["signalized"].generate()
    df_sig.to_csv(config.GRID_SIGNALIZED_CSV, index=False)
    df_sig = simulators["signalized"].generate_with_decoupling()
    df_sig.to_csv(config.GRID_SIGNALIZED_DECOUPLING_CSV, index=False)
    results["signalized"] = df_sig

    # Unsignalized
    print("\n" + "=" * 60)
    df_unsig = simulators["unsignalized"].generate_with_decoupling()
    df_unsig.to_csv(config.GRID_UNSIGNALIZED_CSV, index=False)
    results["unsignalized"] = df_unsig

    # High Volume
    print("\n" + "=" * 60)
    df_hv = simulators["high_volume"].generate_with_decoupling()
    df_hv.to_csv(config.GRID_HIGH_VOLUME_CSV, index=False)
    results["high_volume"] = df_hv

    print("\n" + "=" * 60)
    print("All grid simulations complete.")
    return results


if __name__ == "__main__":
    results = run_all_grid_simulations()
    for name, df in results.items():
        print(f"\n{name}: {df.shape}")
        print(df.groupby("trip_type")[["average_speed_kmph", "co2_g_per_km"]].mean())
