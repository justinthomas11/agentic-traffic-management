import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dashboard.components import render_header, glass_card

def show():
    render_header(
        "Agentic Traffic Management", 
        "AI-Driven Congestion and Emission Decoupling Analysis"
    )
    
    st.markdown("""
    Welcome to the Control Center. This platform analyzes the relationship between traffic congestion 
    and CO₂ emissions, utilizing real-world data from Washington DC and agentic SUMO simulations.
    """)
    
    # Check if data exists
    if not config.DC_EMISSIONS_CSV.exists():
        st.warning("⚠️ Processed datasets not found. Please run `run_pipeline.py` first.")
        return
        
    df = pd.read_csv(config.DC_EMISSIONS_CSV)
    
    st.markdown("### 📊 Washington DC Network Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Trips", value=f"{len(df):,}")
    with col2:
        st.metric(label="Avg Speed", value=f"{df['average_speed_kmh'].mean():.1f} km/h")
    with col3:
        st.metric(label="Avg CO₂", value=f"{df['co2_g_per_km'].mean():.1f} g/km")
    with col4:
        st.metric(label="Congestion Index", value=f"{df['congestion_index'].mean():.2f}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        glass_card(
            "Target Objective", 
            "The goal of agentic control is to achieve <b>Decoupling</b> — where congestion may remain stable or slightly increase, but emissions drop significantly due to smoother flow and reduced stop-and-go waves."
        )
    with c2:
        glass_card(
            "System Architecture", 
            "• <b>Data:</b> Washington DC Uber Movement<br>"
            "• <b>Simulation:</b> Eclipse SUMO 1.19+<br>"
            "• <b>Intelligence:</b> Stable-Baselines3 (PPO/DQN)<br>"
            "• <b>Prediction:</b> XGBoost Classifier"
        )
