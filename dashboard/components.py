"""
Reusable Streamlit components.
"""
import streamlit as st


def render_header(title, subtitle=None):
    """Render a premium header with gradient text."""
    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='color: #94a3b8; font-size: 1.1rem;'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin-top: 0.5rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)


def glass_card(title, content):
    """Render content inside a CSS glassmorphism card (requires raw HTML/CSS fallback if st.container doesn't trigger it)."""
    html = f"""
    <div style="
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    ">
        <h3 style="margin-top: 0; font-size: 1.2rem; color: #e2e8f0;">{title}</h3>
        <p style="color: #cbd5e1; margin-bottom: 0;">{content}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def page_footer():
    """Render a footer at the bottom of the page."""
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; color: #64748b; font-size: 0.9rem;'>
            Agentic Traffic Management Framework &copy; 2024 <br>
            <i>Powered by SUMO, XGBoost, and Stable-Baselines3</i>
        </div>
        """, 
        unsafe_allow_html=True
    )
