import streamlit as st

st.set_page_config(
    page_title="Hospital Sentinel HUD",
    page_icon="🛰️",
    layout="wide"
)

# Cyberpunk CSS
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #00FF41; }
    .stMetric { border: 1px solid #00FF41; background-color: #161B22; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Hospital Audit & Sentinel AI")
st.sidebar.title("🛰️ NAVIGATION")
st.sidebar.info("Data Engineering & LLM Observability")

col1, col2 = st.columns(2)
with col1:
    st.header("🛠️ Pipeline Status")
    st.success("BigQuery: CONNECTED")
    st.success("dbt Models: MATERIALIZED")
with col2:
    st.header("🧠 AI Status")
    st.info("Sentinel: ACTIVE")
    st.write("Monitoring 201.9k rows for schema drift.")

st.markdown("---")
st.write("👈 Select a page in the sidebar to view **Analysis** or **AI Metrics**.")