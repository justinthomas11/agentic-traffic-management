"""
Visualization Module
Provides functions for plotting decoupling analysis, speed comparisons,
and ML model evaluation metrics. Uses Plotly for interactive Streamlit charts
and Matplotlib for static fallbacks.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


# ============================================================
# MATPLOTLIB (STATIC) PLOTS
# ============================================================

def plot_decoupling_scatter_static(df, x_col, y_col, title):
    """Static scatter plot for decoupling analysis."""
    plt.figure(figsize=(7, 6))
    plt.scatter(df[x_col], df[y_col], alpha=0.5)
    plt.axhline(0, linestyle="--", color="black", alpha=0.3)
    plt.axvline(0, linestyle="--", color="black", alpha=0.3)
    plt.xlabel(x_col.replace("_", " ").title())
    plt.ylabel(y_col.replace("_", " ").title())
    plt.title(title)
    plt.grid(True, alpha=0.2)
    return plt.gcf()


def plot_confusion_matrix_static(cm, title="XGBoost Confusion Matrix"):
    """Static heatmap for confusion matrix."""
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(title)
    return plt.gcf()


def plot_feature_importance_static(importance_df, title="Feature Importance"):
    """Static horizontal bar chart for feature importance."""
    plt.figure(figsize=(8, 6))
    sns.barplot(x="importance", y="feature", data=importance_df, palette="viridis")
    plt.title(title)
    plt.xlabel("Importance Score")
    plt.ylabel("Feature")
    return plt.gcf()


# ============================================================
# PLOTLY (INTERACTIVE) PLOTS FOR STREAMLIT
# ============================================================

def get_decoupling_color_map():
    """Standardized color map for decoupling regimes."""
    return {
        "Decoupled (GOOD)": "#10b981",  # Emerald green
        "Decoupled (BAD)": "#ef4444",   # Red
        "Coupled": "#f59e0b",           # Amber
        "Decoupled": "#10b981",         # Emerald green (DC variant)
        "Other": "#6b7280",             # Gray
    }


def plot_decoupling_scatter_interactive(df, x_col, y_col, title):
    """Interactive scatter plot using Plotly."""
    color_map = get_decoupling_color_map()
    
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color="decoupling_type",
        color_discrete_map=color_map,
        title=title,
        opacity=0.7,
        hover_data=["average_speed_kmh", "co2_g_per_km"] if "average_speed_kmh" in df.columns else None,
        template="plotly_dark",
    )
    
    # Add quadrant lines
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
    fig.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
    
    fig.update_layout(
        xaxis_title="Change in Speed (Congestion Reduction) ->" if "speed" in x_col else "Change in Congestion ->",
        yaxis_title="Change in Emissions ->",
        legend_title="Regime",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_speed_comparison_interactive(df_compare):
    """Interactive bar chart for speed/emissions across networks."""
    summary = df_compare.groupby("case").agg({
        "average_speed_kmh": "mean",
        "co2_g_per_km": "mean"
    }).round(2).reset_index()

    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=summary["case"],
        y=summary["average_speed_kmh"],
        name="Avg Speed (km/h)",
        marker_color="#3b82f6"  # Blue
    ))
    
    fig.add_trace(go.Bar(
        x=summary["case"],
        y=summary["co2_g_per_km"],
        name="Avg CO2 (g/km)",
        marker_color="#8b5cf6"  # Purple
    ))

    fig.update_layout(
        title="Network Performance Comparison",
        barmode="group",
        template="plotly_dark",
        xaxis_title="Network Type",
        yaxis_title="Value",
        legend_title="Metric",
    )
    return fig


def plot_feature_importance_interactive(importance_df):
    """Interactive bar chart for ML feature importance."""
    fig = px.bar(
        importance_df.sort_values("importance", ascending=True),
        x="importance",
        y="feature",
        orientation="h",
        title="XGBoost Feature Importance",
        template="plotly_dark",
        color="importance",
        color_continuous_scale="Viridis",
    )
    fig.update_layout(
        xaxis_title="Importance Score",
        yaxis_title="",
        coloraxis_showscale=False,
    )
    return fig
