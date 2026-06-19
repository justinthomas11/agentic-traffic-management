"""
Premium CSS styling and theme configuration for the Streamlit dashboard.
Focuses on dark glassmorphism, micro-animations, and vibrant gradients.
"""

import streamlit as st


def apply_custom_styles():
    """Injects custom CSS into the Streamlit app."""
    
    css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }

    /* Main Background gradient */
    .stApp {
        background: radial-gradient(circle at top left, #1a1a2e, #16213e, #0f3460);
        color: #e2e8f0;
    }

    /* Glassmorphism Containers (DataFrames, Plotly charts) */
    .stDataFrame, .stPlotlyChart {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .stPlotlyChart:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 40px rgba(139, 92, 246, 0.15);
    }

    /* Metric Cards (KPIs) */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid rgba(255,255,255,0.05);
        border-top: 1px solid rgba(255,255,255,0.2);
        border-left: 1px solid rgba(255,255,255,0.2);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.3s ease-in-out;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(59, 130, 246, 0.2);
        border-top: 1px solid rgba(59, 130, 246, 0.5);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #fff;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 500;
        color: #94a3b8;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
    }

    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
    }
    
    /* Input Fields (Sliders, Selectboxes) */
    .stSlider > div, .stSelectbox > div {
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Tooltips / Info boxes */
    div.stAlert {
        background-color: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-left: 4px solid #3b82f6;
        color: #e2e8f0;
        border-radius: 8px;
    }
    
    /* Animations */
    @keyframes fadein {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    
    .main .block-container {
        animation: fadein 0.6s ease-out;
    }
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
