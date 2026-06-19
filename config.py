"""
Central configuration for the Agentic Traffic Management project.
All paths, model hyperparameters, and simulation constants are defined here.
"""

import os
from pathlib import Path

# ============================================================
# PROJECT PATHS
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
REPORTS_DIR = PROJECT_ROOT / "reports"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"
SUMO_CONFIG_DIR = PROJECT_ROOT / "sumo_config"

# Create directories if they don't exist
for d in [MODELS_DIR, RESULTS_DIR, SUMO_CONFIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============================================================
# DATASET FILES
# ============================================================
DC_TRAVEL_TIMES_CSV = DATASETS_DIR / "Travel_Times - Washington DC.csv"

# Generated intermediate CSVs
DC_CONGESTION_CSV = RESULTS_DIR / "Travel_Times_DC_with_congestion.csv"
DC_EMISSIONS_CSV = RESULTS_DIR / "Travel_Times_DC_with_congestion_emissions.csv"
GRID_SIGNALIZED_CSV = RESULTS_DIR / "grid_signalized_4way.csv"
GRID_SIGNALIZED_DECOUPLING_CSV = RESULTS_DIR / "grid_signalized_4way_decoupling.csv"
GRID_UNSIGNALIZED_CSV = RESULTS_DIR / "grid_unsignalized_decoupling.csv"
GRID_HIGH_VOLUME_CSV = RESULTS_DIR / "grid_high_volume_decoupling.csv"
ML_DATASET_CSV = RESULTS_DIR / "ml_dataset_xgboost.csv"
XGBOOST_MODEL_PATH = MODELS_DIR / "xgboost_decoupling_model.pkl"

# ============================================================
# DC REAL-WORLD ASSUMPTIONS
# ============================================================
DC_DISTANCE_KM = 1.0           # Average OD distance in central DC
DC_FREE_FLOW_SPEED = 60        # km/hr (urban free-flow speed)

# ============================================================
# EMISSION MODEL CONSTANTS (quadratic speed-emission model)
# CO2 (g/km) = a + b * speed + c * speed^2
# ============================================================
EMISSION_A = 300    # constant term
EMISSION_B = -5     # linear speed term
EMISSION_C = 0.1    # quadratic speed term

# ============================================================
# GRID SIMULATION PARAMETERS
# ============================================================
GRID_SIZE = 5                   # 5x5 grid
BLOCK_LENGTH_KM = 0.1          # 100 meters per block
GRID_SPEED_LIMIT = 40          # km/hr (urban)
TRIPS_PER_TYPE = 50            # samples per trip type
RANDOM_SEED = 42

# OD trip types: name -> number of intersections traversed
OD_TRIPS = {
    "short": 2,
    "medium": 4,
    "long": 6,
}

# Delay ranges per intersection type (seconds)
DELAY_SIGNALIZED = (20, 40)
DELAY_UNSIGNALIZED = (5, 15)
DELAY_HIGH_VOLUME = (50, 90)

# ============================================================
# XGBOOST HYPERPARAMETERS
# ============================================================
XGBOOST_PARAMS = {
    "n_estimators": 150,
    "max_depth": 4,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "eval_metric": "logloss",
}

# ============================================================
# SUMO CONFIGURATION
# ============================================================
SUMO_HOME = os.environ.get("SUMO_HOME", r"C:\Program Files\Eclipse\Sumo")
SUMO_BINARY = os.path.join(SUMO_HOME, "bin", "sumo")
SUMO_GUI_BINARY = os.path.join(SUMO_HOME, "bin", "sumo-gui")

# SUMO network files
SUMO_NET_FILE = SUMO_CONFIG_DIR / "grid.net.xml"
SUMO_ROUTE_FILE = SUMO_CONFIG_DIR / "grid.rou.xml"
SUMO_CFG_FILE = SUMO_CONFIG_DIR / "grid.sumocfg"
SUMO_ADD_FILE = SUMO_CONFIG_DIR / "grid.add.xml"

# Simulation parameters
SUMO_SIM_STEPS = 3600          # 1 hour of simulation
SUMO_STEP_LENGTH = 1.0         # seconds per simulation step

# ============================================================
# RL AGENT CONFIGURATION
# ============================================================
RL_CONFIG = {
    "algorithm": "PPO",         # PPO or DQN
    "total_timesteps": 50_000,  # Quick demo training
    "learning_rate": 3e-4,
    "gamma": 0.99,              # discount factor
    "n_steps": 256,             # steps per update (PPO)
    "batch_size": 64,
    "delta_time": 5,            # seconds between agent actions
    "min_green": 8,             # minimum green phase duration
    "max_green": 50,            # maximum green phase duration
}

# Reward weights
REWARD_WEIGHTS = {
    "waiting_time": -0.4,       # penalize waiting
    "co2_emissions": -0.4,      # penalize emissions
    "throughput": 0.1,          # reward throughput
    "decoupling_bonus": 0.1,   # reward decoupling
}
