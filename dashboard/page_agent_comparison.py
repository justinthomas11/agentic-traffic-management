import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dashboard.components import render_header

def show():
    render_header("Agent Comparison", "Benchmark RL agents against fixed and actuated baselines.")
    
    comp_file = config.RESULTS_DIR / "agent_comparison.csv"
    
    if not comp_file.exists():
        st.warning("⚠️ Agent comparison results not found. Please run `src/agents/experiment.py` first.")
        
        st.markdown("### Run Experiment Now")
        if st.button("Execute Benchmarks", type="primary"):
            with st.spinner("Running agent simulations (this may take a few minutes)..."):
                from src.agents.experiment import AgentExperiment
                exp = AgentExperiment()
                df = exp.run_all()
                st.success("Benchmarks complete!")
                st.rerun()
        return
        
    df = pd.read_csv(comp_file)
    
    st.markdown("### Overall Performance")
    
    # KPIs for RL Agent vs Baseline (Fixed)
    rl_row = df[df["Agent"].str.contains("RL")].iloc[0] if len(df[df["Agent"].str.contains("RL")]) > 0 else None
    fixed_row = df[df["Agent"].str.contains("Fixed")].iloc[0] if len(df[df["Agent"].str.contains("Fixed")]) > 0 else None
    
    if rl_row is not None and fixed_row is not None:
        c1, c2, c3 = st.columns(3)
        
        speed_imp = ((rl_row['Avg Speed (km/h)'] - fixed_row['Avg Speed (km/h)']) / fixed_row['Avg Speed (km/h)']) * 100
        wait_imp = ((fixed_row['Total Wait Time (s)'] - rl_row['Total Wait Time (s)']) / fixed_row['Total Wait Time (s)']) * 100
        co2_imp = ((fixed_row['Total CO2 (kg)'] - rl_row['Total CO2 (kg)']) / fixed_row['Total CO2 (kg)']) * 100
        
        c1.metric("RL Speed Improvement", f"{speed_imp:+.1f}%")
        c2.metric("RL Wait Reduction", f"{wait_imp:+.1f}%")
        c3.metric("RL Emission Reduction", f"{co2_imp:+.1f}%")
        
    st.markdown("---")
    
    # Bar charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(
            df, x="Agent", y="Avg Speed (km/h)", 
            color="Agent", title="Average Network Speed",
            template="plotly_dark"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        fig2 = px.bar(
            df, x="Agent", y="Total CO2 (kg)", 
            color="Agent", title="Total Network Emissions",
            template="plotly_dark"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
    st.markdown("### Raw Results")
    st.dataframe(df, use_container_width=True)
