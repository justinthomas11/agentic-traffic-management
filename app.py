"""
Main Streamlit Application Entry Point.
Implements multi-page routing and global configuration.
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard.styles import apply_custom_styles
from dashboard.components import page_footer

# Configure Streamlit page
st.set_page_config(
    page_title="Agentic Traffic Management",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global CSS
apply_custom_styles()

# Define Pages
pages = {
    "🏠 Overview": "dashboard/page_overview.py",
    "📊 Decoupling Analysis": "dashboard/page_decoupling.py",
    "🔲 Grid Simulation": "dashboard/page_grid_sim.py",
    "🤖 ML Predictor": "dashboard/page_ml_model.py",
    "🚦 SUMO Engine": "dashboard/page_sumo.py",
    "🏆 Agent Comparison": "dashboard/page_agent_comparison.py"
}

# Sidebar Navigation
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h2 style='font-size: 1.5rem; margin-bottom: 0;'>Agentic Traffic</h2>
        <span style='color: #10b981; font-weight: 600;'>Control Center</span>
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown("### Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()), label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='color: #94a3b8; font-size: 0.8rem;'>
        <b>Status:</b> System Online<br>
        <b>Engine:</b> SUMO 1.19+<br>
        <b>AI Core:</b> Stable-Baselines3
    </div>
    """, 
    unsafe_allow_html=True
)

# Dynamic Page Loading
# Since Streamlit natively supports multipage apps via a `pages/` directory,
# but we want tight control and a unified style, we load modules dynamically.
page_path = pages[selection]

if selection == "🏠 Overview":
    import dashboard.page_overview as current_page
elif selection == "📊 Decoupling Analysis":
    import dashboard.page_decoupling as current_page
elif selection == "🔲 Grid Simulation":
    import dashboard.page_grid_sim as current_page
elif selection == "🤖 ML Predictor":
    import dashboard.page_ml_model as current_page
elif selection == "🚦 SUMO Engine":
    import dashboard.page_sumo as current_page
elif selection == "🏆 Agent Comparison":
    import dashboard.page_agent_comparison as current_page

# Run the selected page
current_page.show()

# Global Footer
page_footer()
