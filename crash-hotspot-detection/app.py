import streamlit as st
from data_loader import load_and_prepare_data
from hotspot_page import render_hotspot_page 
from dbscan_page import render_dbscan_page

DATA_PATH = "Colorado_Data_2015_2023_Cleaned.csv"

def main():
    st.set_page_config(
        page_title="Colorado Crash Hotspot Explorer",
        page_icon="🚗",
        layout="wide",
    )

    df = load_and_prepare_data(DATA_PATH)

    if df.empty:
        st.error("No data available for Colorado crashes (2015–2023) after cleaning.")
        return

    view_option = st.sidebar.radio(
        "Choose View",
        ("Crash Heatmap", "Crash Hotspots")
    )

    if view_option == "Crash Heatmap":
        render_hotspot_page(df)
    else:
        render_dbscan_page(df)

if __name__ == "__main__":
    main()