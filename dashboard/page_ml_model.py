import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dashboard.components import render_header
from src.ml_model import load_model, evaluate_model
from src.visualization import plot_confusion_matrix_static, plot_feature_importance_interactive

def show():
    render_header("Machine Learning Predictor", "XGBoost Classification for Decoupling Prediction")
    
    if not config.XGBOOST_MODEL_PATH.exists():
        st.warning("⚠️ Trained model not found. Please run `run_pipeline.py` first.")
        return
        
    model = load_model()
    
    st.markdown("""
    Use the sliders below to adjust traffic characteristics and predict whether the resulting
    state will be **Decoupled** (emissions dropping despite congestion) or **Coupled** (emissions rising with congestion).
    """)
    
    # Interactive Prediction
    st.markdown("### Live Prediction")
    
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1:
            speed = st.slider("Average Speed (km/h)", 5.0, 80.0, 30.0)
            congestion = st.slider("Congestion Index", 0.0, 1.0, 0.5)
        with c2:
            delay = st.slider("Total Delay (sec)", 0.0, 500.0, 100.0)
            intersections = st.slider("Num Intersections", 1, 10, 4)
        with c3:
            distance = st.slider("Distance (km)", 0.5, 20.0, 2.0)
            
    # Dummy encoding features to match training setup
    # Model expects: average_speed_kmh, congestion_index, total_delay_sec, 
    # num_intersections, distance_km, plus one-hot encoded intersection/network types.
    # We will build a dummy dataframe with zeros for the one-hots, then set a default.
    
    expected_features = model.feature_names_in_
    input_dict = {f: 0 for f in expected_features}
    
    input_dict["average_speed_kmh"] = speed
    input_dict["congestion_index"] = congestion
    input_dict["total_delay_sec"] = delay
    input_dict["num_intersections"] = intersections
    input_dict["distance_km"] = distance
    
    # Default to Signalized Grid
    if "intersection_type_Signalized" in input_dict:
        input_dict["intersection_type_Signalized"] = 1
    if "network_type_Grid_Signalized" in input_dict:
        input_dict["network_type_Grid_Signalized"] = 1
        
    input_df = pd.DataFrame([input_dict])
    
    pred = model.predict(input_df)[0]
    prob = model.predict_proba(input_df)[0]
    
    st.markdown("<br>", unsafe_allow_html=True)
    if pred == 1:
        st.success(f"**Prediction: DECOUPLED** (Confidence: {prob[1]:.1%})")
        st.markdown("Emission levels are optimized relative to the congestion state.")
    else:
        st.error(f"**Prediction: COUPLED** (Confidence: {prob[0]:.1%})")
        st.markdown("Emission levels are deteriorating alongside traffic flow.")
        
    st.markdown("---")
    st.markdown("### Model Insights")
    
    importance_df = pd.DataFrame({
        "feature": expected_features,
        "importance": model.feature_importances_
    })
    
    fig = plot_feature_importance_interactive(importance_df)
    st.plotly_chart(fig, use_container_width=True)
