import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dashboard.components import render_header
from src.visualization import plot_decoupling_scatter_interactive, plot_speed_comparison_interactive

def show():
    render_header("Decoupling Analysis", "Emission-Congestion decoupling regimes across network types.")
    
    if not config.ML_DATASET_CSV.exists():
        st.warning("⚠️ Decoupling dataset not found. Please run `run_pipeline.py` first.")
        return
        
    # Load individual datasets to get un-encoded types
    try:
        df_dc = pd.read_csv(config.DC_EMISSIONS_CSV)
        df_sig = pd.read_csv(config.GRID_SIGNALIZED_DECOUPLING_CSV)
        df_unsig = pd.read_csv(config.GRID_UNSIGNALIZED_CSV)
        df_hv = pd.read_csv(config.GRID_HIGH_VOLUME_CSV)
    except FileNotFoundError:
        st.error("Missing some grid CSVs. Run the full pipeline first.")
        return
        
    network_map = {
        "Real-World (Washington DC)": (df_dc, "congestion_index", "co2_g_per_km"),
        "Grid (Signalized)": (df_sig, "average_speed_kmh", "co2_g_per_km"),
        "Grid (Unsignalized)": (df_unsig, "average_speed_kmh", "co2_g_per_km"),
        "Grid (High Volume)": (df_hv, "average_speed_kmh", "co2_g_per_km"),
    }
    
    st.markdown("### Regime Visualization")
    
    selected_network = st.selectbox("Select Network Type", list(network_map.keys()))
    
    df, x_col, y_col = network_map[selected_network]
    
    # Calculate delta columns if they don't exist
    if "delta_congestion" not in df.columns and "delta_speed" not in df.columns:
        st.warning("Delta metrics not pre-computed for this dataset.")
    else:
        actual_x_col = "delta_congestion" if "delta_congestion" in df.columns else "delta_speed"
        fig = plot_decoupling_scatter_interactive(df, actual_x_col, "delta_emission", f"Decoupling: {selected_network}")
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("### Cross-Network Performance Comparison")
    
    # Create comparison df on the fly
    def ext(d, name):
        return pd.DataFrame({
            "case": name, 
            "average_speed_kmh": d.get("average_speed_kmh", d.get("average_speed_kmph", 0)), 
            "co2_g_per_km": d.get("co2_g_per_km", 0)
        })
        
    df_compare = pd.concat([
        ext(df_dc, "Washington DC"),
        ext(df_sig, "Signalized"),
        ext(df_unsig, "Unsignalized"),
        ext(df_hv, "High Volume")
    ])
    
    fig2 = plot_speed_comparison_interactive(df_compare)
    st.plotly_chart(fig2, use_container_width=True)
