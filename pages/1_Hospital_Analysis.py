import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
import os

# --- 1. DYNAMIC PATHING ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY_PATH = os.path.join(BASE_DIR, "creds.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

st.set_page_config(page_title="Hospital Audit", layout="wide")
st.title("🏥 Hospital Price Variance Audit")

# --- 2. DATA ENGINE ---
@st.cache_data
def get_hospital_data():
    client = bigquery.Client()
    query = """
        SELECT provider_name, provider_city, average_covered_charges, average_total_payments,
        (average_covered_charges - average_total_payments) as price_variance,
        SAFE_DIVIDE(average_covered_charges, average_total_payments) as markup_ratio
        FROM `drug-moa-project.cms_medicare.fct_hospital_audit`
        ORDER BY price_variance DESC
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)

# --- 3. UI RENDERING ---
try:
    df = get_hospital_data()
    
    # --- HIGH-LEVEL KPIs ---
    avg_markup = df['markup_ratio'].mean()
    total_variance = df['price_variance'].sum()
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Avg. Markup Factor", f"{avg_markup:.2f}x", help="Ratio of Charges vs. Medicare Payments")
    kpi2.metric("Total Audit Variance", f"${total_variance/1e6:.1f}M")
    kpi3.metric("Hospitals Audited", len(df))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Top 20 Hospital Markups")
        fig_bar = px.bar(
            df.head(20), x='price_variance', y='provider_name', orientation='h',
            color='price_variance', color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(template="plotly_dark", font_color="#00FF41", showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # --- THE EFFICIENCY FRONTIER ---
        st.subheader("🎯 The Efficiency Frontier")
        fig_scatter = px.scatter(
            df, x='average_total_payments', y='price_variance',
            color='provider_city', hover_name='provider_name',
            title="Reimbursement vs. Markup (Outlier Detection)",
            labels={'average_total_payments': 'Medicare Payment ($)', 'price_variance': 'Markup ($)'}
        )
        fig_scatter.update_layout(template="plotly_dark")
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("📋 Audit Ledger (Searchable)")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Failed to connect to BigQuery: {e}")
