import streamlit as st
import pandas as pd
from filters_hotspot import hotspot_sidebar_filters, apply_hotspot_filters
from map_layers import build_hotspot_figure

def render_map_and_metrics(df, filters_dict, col1, col2):
    """Shared code to render both the map and metrics."""
    with col1:
        st.subheader("🗺️ Crash Heatmap")

        if df.empty:
            st.info("No crashes match the current filters.")
            return

        fig = build_hotspot_figure(df, filters_dict, overlay=filters_dict["overlay"])

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📊 Current View")

        if not df.empty:
            st.metric("Total Crashes", f"{len(df):,}")
            fatalities = int(df["FATALS"].sum()) if not df.empty else 0
            st.metric("Total Fatalities", f"{fatalities:,}")
            
            y_min = int(df["YEAR"].min())
            y_max = int(df["YEAR"].max())
            st.metric("Year Range", f"{y_min}–{y_max}")
        else:
            st.metric("Total Crashes", "—")
            st.metric("Total Fatalities", "—")
            st.metric("Year Range", "—")

    st.markdown("---")

def render_hotspot_page(df: pd.DataFrame):
    """Render the heatmap page"""
    st.markdown(
        """
        <h1>🚗 Colorado Fatal Crashes Hotspot Explorer - Data Mining Project</h1>
        <p>Fatal crash density across Colorado (2015–2023)</p>
        """,
        unsafe_allow_html=True,
    )

    filters_dict = hotspot_sidebar_filters(df)
    filtered = apply_hotspot_filters(df, filters_dict)

    col1, col2 = st.columns([3, 1])

    render_map_and_metrics(filtered, filters_dict, col1, col2)