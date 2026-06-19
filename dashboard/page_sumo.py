import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dashboard.components import render_header, glass_card

def show():
    render_header("SUMO Engine Control", "Launch and monitor SUMO micro-simulations directly.")
    
    c1, c2 = st.columns([2, 1])
    
    with c2:
        glass_card("Engine Status", "Ready to Launch")
        use_gui = st.checkbox("Launch SUMO GUI", value=True)
        max_steps = st.number_input("Max Steps", min_value=100, max_value=3600, value=1000)
        
        if st.button("Launch SUMO", type="primary", use_container_width=True):
            st.session_state["sumo_running"] = True
            
    with c1:
        st.markdown("### Simulation Configuration")
        st.code(f"""
        # grid.sumocfg
        <configuration>
            <input>
                <net-file value="grid.net.xml"/>
                <route-files value="grid.rou.xml"/>
                <additional-files value="grid.add.xml"/>
            </input>
            <time>
                <begin value="0"/>
                <end value="{max_steps}"/>
            </time>
        </configuration>
        """, language="xml")
        
    if st.session_state.get("sumo_running", False):
        st.markdown("---")
        st.info("Running simulation in background... Please check the SUMO GUI window if enabled.")
        
        # In a real app, this would be an async subprocess call feeding a live chart.
        # For simplicity in Streamlit without callbacks, we run a short sync test.
        with st.spinner("Executing via TraCI..."):
            from src.sumo_simulation import SUMOSimulation
            try:
                sim = SUMOSimulation(use_gui=use_gui)
                sim.start()
                df = sim.run(max_steps=max_steps)
                st.success("Simulation Complete!")
                
                st.line_chart(df.set_index("step")[["total_waiting_time_s", "avg_speed_kmh"]])
                
            except Exception as e:
                st.error(f"Execution failed: {e}")
                
        st.session_state["sumo_running"] = False
