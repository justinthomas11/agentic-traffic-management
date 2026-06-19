"""
ML Model Module
Handles dataset preparation, XGBoost training, evaluation, and persistence
for the emission-congestion decoupling classifier.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
)
from xgboost import XGBClassifier
import joblib


def prepare_ml_dataset(
    df_dc=None,
    df_grid=None,
    df_unsig=None,
    df_hv=None,
):
    """
    Combine all datasets into a single ML-ready dataset.
    Handles column standardization, encoding, and label creation.
    """
    # Load from saved files if not provided
    if df_dc is None:
        df_dc = pd.read_csv(config.DC_EMISSIONS_CSV)
    if df_grid is None:
        df_grid = pd.read_csv(config.GRID_SIGNALIZED_DECOUPLING_CSV)
    if df_unsig is None:
        df_unsig = pd.read_csv(config.GRID_UNSIGNALIZED_CSV)
    if df_hv is None:
        df_hv = pd.read_csv(config.GRID_HIGH_VOLUME_CSV)

    # Add identifiers
    df_dc["network_type"] = "Real_DC"
    df_grid["network_type"] = "Grid_Signalized"
    df_unsig["network_type"] = "Grid_Unsignalized"
    df_hv["network_type"] = "Grid_HighVolume"

    df_dc["intersection_type"] = "Urban_Mixed"
    df_grid["intersection_type"] = "Signalized"
    df_unsig["intersection_type"] = "Unsignalized"
    df_hv["intersection_type"] = "HighVolume"

    # Standardize speed column name
    for df in [df_grid, df_unsig]:
        if "average_speed_kmph" in df.columns:
            df.rename(columns={"average_speed_kmph": "average_speed_kmh"}, inplace=True)

    # Select available columns
    selected_columns = [
        "average_speed_kmh",
        "congestion_index",
        "total_delay_sec",
        "num_intersections",
        "distance_km",
        "intersection_type",
        "network_type",
        "decoupling_type",
    ]

    def select_available(df, cols):
        return df[[c for c in cols if c in df.columns]]

    df_dc_sel = select_available(df_dc, selected_columns)
    df_grid_sel = select_available(df_grid, selected_columns)
    df_unsig_sel = select_available(df_unsig, selected_columns)
    df_hv_sel = select_available(df_hv, selected_columns)

    # Combine
    df_ml = pd.concat(
        [df_dc_sel, df_grid_sel, df_unsig_sel, df_hv_sel],
        ignore_index=True,
    )

    # Create binary label
    df_ml["decoupled_label"] = df_ml["decoupling_type"].apply(
        lambda x: 1 if pd.notna(x) and "Decoupled" in str(x) else 0
    )

    # One-hot encode categoricals
    df_ml_encoded = pd.get_dummies(
        df_ml,
        columns=["intersection_type", "network_type"],
        drop_first=True,
    )

    # Fill NaN and clean
    df_ml_encoded = df_ml_encoded.fillna(0)

    # Save
    df_ml_encoded.to_csv(config.ML_DATASET_CSV, index=False)
    print(f"ML dataset prepared: {df_ml_encoded.shape}")
    print(f"Label distribution:\n{df_ml_encoded['decoupled_label'].value_counts()}")

    return df_ml_encoded


def train_xgboost(df_ml_encoded=None, params=None):
    """
    Train XGBoost classifier for decoupling prediction.

    Returns: (model, X_train, X_test, y_train, y_test, y_pred)
    """
    if df_ml_encoded is None:
        df_ml_encoded = pd.read_csv(config.ML_DATASET_CSV)

    params = params or config.XGBOOST_PARAMS

    # Separate features and target
    drop_cols = ["decoupling_type", "decoupled_label"]
    feature_cols = [c for c in df_ml_encoded.columns if c not in drop_cols]
    X = df_ml_encoded[feature_cols]
    y = df_ml_encoded["decoupled_label"]

    print(f"Features: {X.shape[1]}, Samples: {X.shape[0]}")
    print(f"Feature columns: {list(X.columns)}")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=params.get("random_state", 42)
    )

    # Train
    model = XGBClassifier(**params)
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)

    return model, X_train, X_test, y_train, y_test, y_pred


def evaluate_model(model, X_test, y_test, y_pred):
    """Print evaluation metrics and return results dict."""
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    print("\n" + "=" * 60)
    print("XGBoost Model Evaluation")
    print("=" * 60)
    print(f"Accuracy: {acc:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print(f"Confusion Matrix:\n{cm}")

    # Feature importance
    importance_df = pd.DataFrame({
        "feature": X_test.columns,
        "importance": model.feature_importances_,
    }).sort_values(by="importance", ascending=False)

    print(f"\nTop Features:")
    print(importance_df.head(10).to_string(index=False))

    return {
        "accuracy": acc,
        "classification_report": report,
        "confusion_matrix": cm,
        "feature_importance": importance_df,
    }


def save_model(model, filepath=None):
    """Save trained model to disk."""
    filepath = filepath or config.XGBOOST_MODEL_PATH
    filepath.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, filepath)
    print(f"Model saved to: {filepath}")


def load_model(filepath=None):
    """Load trained model from disk."""
    filepath = filepath or config.XGBOOST_MODEL_PATH
    model = joblib.load(filepath)
    print(f"Model loaded from: {filepath}")
    return model


def run_ml_pipeline():
    """Run the complete ML pipeline."""
    print("\n" + "=" * 60)
    print("Running ML Pipeline")
    print("=" * 60)

    # Prepare dataset
    df_ml = prepare_ml_dataset()

    # Train model
    model, X_train, X_test, y_train, y_test, y_pred = train_xgboost(df_ml)

    # Evaluate
    results = evaluate_model(model, X_test, y_test, y_pred)

    # Save
    save_model(model)

    return model, results


if __name__ == "__main__":
    model, results = run_ml_pipeline()
