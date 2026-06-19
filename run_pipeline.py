"""
End-to-End Execution Pipeline
Runs the entire data processing, grid simulation, and ML training pipeline.
"""

import os
from pathlib import Path
import sys

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from src.data_processing import run_dc_pipeline
from src.grid_simulation import run_all_grid_simulations
from src.ml_model import run_ml_pipeline
from src.sumo_network import build_full_scenario


def main():
    print("=" * 80)
    print("🚦 AGENTIC TRAFFIC MANAGEMENT — PIPELINE RUNNER 🚦")
    print("=" * 80)

    # 1. Check datasets
    if not config.DC_TRAVEL_TIMES_CSV.exists():
        print(f"\n❌ ERROR: Dataset not found at {config.DC_TRAVEL_TIMES_CSV}")
        print("Please ensure the raw data is in the datasets/ directory.")
        sys.exit(1)

    # 2. Run DC Data Processing
    print("\n[1/3] Processing Real-World Washington DC Data...")
    df_dc = run_dc_pipeline()

    # 3. Run Grid Simulations
    print("\n[2/3] Running Synthetic Grid Simulations...")
    grid_results = run_all_grid_simulations()

    # 4. Run ML Pipeline
    print("\n[3/4] Training Decoupling ML Model...")
    model, metrics = run_ml_pipeline()

    # 5. Build SUMO Scenario
    print("\n[4/4] Building SUMO Simulation Environment...")
    build_full_scenario()

    print("\n" + "=" * 80)
    print("✅ PIPELINE COMPLETE!")
    print(f"Check the {config.RESULTS_DIR.name}/ directory for output CSVs.")
    print(f"Check the {config.MODELS_DIR.name}/ directory for the trained model.")
    print("=" * 80)


if __name__ == "__main__":
    main()
