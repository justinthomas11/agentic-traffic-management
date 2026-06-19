import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dashboard.components import render_header
from src.grid_simulation import GridSimulator

def show():
    render_header("Interactive Grid Simulation", "Synthesize traffic data with custom parameters.")
    
    st.markdown("""
    Adjust the parameters below to instantly generate a synthetic dataset representing a 
    grid network, and visualize the resulting speed and emission characteristics.
    """)
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("**Network Properties**")
        grid_size = st.slider("Grid Size", 3, 10, 5)
        speed_limit = st.slider("Speed Limit (km/h)", 20, 80, 40)
        
    with c2:
        st.markdown("**Intersection Delay (sec)**")
        delay_min = st.slider("Min Delay", 0, 60, 20)
        delay_max = st.slider("Max Delay", delay_min, 120, max(40, delay_min+10))
        
    with c3:
        st.markdown("**Demand**")
        trips = st.slider("Trips per OD pair", 10, 200, 50)
        
    if st.button("Generate & Simulate", type="primary"):
        with st.spinner("Generating grid simulation..."):
            sim = GridSimulator(
                name="Custom Streamlit Grid",
                delay_range=(delay_min, delay_max),
                grid_size=grid_size,
                speed_limit=speed_limit,
                trips_per_type=trips
            )
            df = sim.generate_with_decoupling()
            
            st.success(f"Generated {len(df)} trips successfully!")
            
            st.markdown("### Results Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Speed", f"{df['average_speed_kmph'].mean():.1f} km/h")
            with col2:
                st.metric("Avg CO2", f"{df['co2_g_per_km'].mean():.1f} g/km")
                
            st.dataframe(df.head(10), use_container_width=True)
            
            # Show decoupling distribution
            st.markdown("### Decoupling Regimes")
            dist = df["decoupling_type"].value_counts(normalize=True) * 100
            
            import plotly.express as px
            from dashboard.styles import get_decoupling_color_map
            # need to handle color map mapping via a separate file or inline
            
            fig = px.pie(
                values=dist.values, 
                names=dist.index, 
                title="Decoupling Distribution",
                template="plotly_dark",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
