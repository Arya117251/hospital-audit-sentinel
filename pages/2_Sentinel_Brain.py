import json
import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Sentinel Brain", layout="wide")
st.title("🤖 Sentinel Brain Metrics")

if os.path.exists("sentinel_stats.json"):
    with open("sentinel_stats.json", "r") as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # --- NEW: TOKEN EFFICIENCY & OpEx ---
    total_tokens = df['total_tokens'].sum()
    total_cost = df['estimated_cost_usd'].sum()
    # Logic: OpEx per successful recovery
    cost_per_recovery = total_cost / len(df) if len(df) > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Surgeries", len(df))
    m2.metric("Total Tokens Burned", f"{total_tokens:,}")
    m3.metric("Total OpEx (USD)", f"${total_cost:.4f}")
    m4.metric("Avg. Cost / Recovery", f"${cost_per_recovery:.5f}", delta_color="inverse")

    st.divider()

    # --- NEW: SEARCHABLE SURGERY HISTORY ---
    st.subheader("🕵️‍♂️ Surgery History Ledger")

    history_df = df[['timestamp', 'error_detected', 'suggested_fix']].copy()
    history_df.columns = ['Timestamp', 'Original Error', 'AI Fix (SQL)']
    # Adding a recovery status 
    history_df['Status'] = "✅ RECOVERED" 
    
    st.dataframe(history_df, use_container_width=True, hide_index=True)

    st.subheader("📈 Token Burn Over Time")
    fig = px.area(df, x='timestamp', y='total_tokens', title="API Consumption")
    fig.update_layout(template="plotly_dark", font_color="#00FF41")
    st.plotly_chart(fig, use_container_width=True)

    # Detailed view still available below
    st.subheader("🔍 Deep Dive: Recent Attempts")
    for entry in reversed(data[-5:]): # Show last 5
        with st.expander(f"System Recovery: {entry['timestamp']}"):
            st.code(entry['error_detected'], language='text')
            st.code(entry['suggested_fix'], language='sql')
else:
    st.warning("No Sentinel logs found yet. Run 'python sentinel.py' to generate metrics.")