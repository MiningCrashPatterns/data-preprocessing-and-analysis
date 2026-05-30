import streamlit as st
import pandas as pd
from sklearn.cluster import DBSCAN
import plotly.graph_objects as go
from filters_hotspot import hotspot_sidebar_filters, apply_hotspot_filters

def apply_dbscan_clustering(df, eps=0.1, min_samples=5):
    """Apply DBSCAN clustering on the data"""
    # Ensure there are valid LATITUDE and LONGITUD data points
    coordinates = df[["LATITUDE", "LONGITUD"]].dropna().values

    if coordinates.shape[0] == 0:
        st.error("No valid data points for clustering (LATITUDE and LONGITUD contain NaN).")
        return df

    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
    df['cluster'] = dbscan.fit_predict(coordinates)

    # Handle the case if DBSCAN didn't find any valid clusters
    if 'cluster' not in df.columns:
        st.error("No clusters found after DBSCAN.")
        return df

    # Add fatalities to each cluster
    df['fatalities'] = df.groupby('cluster')['FATALS'].transform('sum')

    # Categorize each zone based on fatalities
    def categorize_zone(fatalities):
        if fatalities >= 100:
            return "Danger", "red"
        elif 50 <= fatalities < 100:
            return "Mild", "yellow"
        else:
            return "Low Danger", "green"

    df['zone_label'], df['zone_color'] = zip(*df['fatalities'].apply(categorize_zone))

    return df

def dbscan_filters():
    """Sidebar filter for DBSCAN clustering"""
    st.sidebar.header("🔧 DBSCAN Clustering Filters")

    eps = st.sidebar.slider("🌀 Radius (eps)", 0.02, 0.5, 0.1, 0.01)
    min_samples = st.sidebar.slider("⚙️ Minimum Samples (min_samples)", 1, 20, 5, 1)

    show_outliers = st.sidebar.checkbox("Show Outliers", value=True)

    filters_dict = {
        "eps": eps,
        "min_samples": min_samples,
        "show_outliers": show_outliers
    }

    return filters_dict

def render_map_and_metrics_with_dbscan(df, filters_dict, col1, col2, show_outliers):
    with col1:
        st.subheader("🗺️ Crash Hotspots (DBSCAN Clustering)")

        if df.empty:
            st.info("No crashes match the current filters.")
            return

        # Create the cluster summary
        cluster_summary = df.groupby('cluster').agg(
            fatalities=('fatalities', 'first'),
            zone_label=('zone_label', 'first'),
            zone_color=('zone_color', 'first'),
            lat=('LATITUDE', 'mean'),
            lon=('LONGITUD', 'mean')
        ).reset_index()

        # Sort clusters in ascending order based on the cluster id
        cluster_summary = cluster_summary.sort_values(by='cluster')

        # Marker Size for all top clusters
        marker_size = 25  # Uniform size for all markers

        # Filter to show only top 10 clusters based on the number of fatalities
        top_clusters = cluster_summary.nlargest(10, "fatalities")

        # Assign cluster names (Cluster 1, Cluster 2, etc.)
        top_clusters['cluster_name'] = ['Cluster ' + str(i+1) for i in range(len(top_clusters))]

        # Create the scatter mapbox plot for DBSCAN clusters
        fig = go.Figure(go.Scattermapbox(
            lat=top_clusters['lat'],
            lon=top_clusters['lon'],
            mode='markers',
            marker=dict(
                size=marker_size,  # Uniform marker size for clusters
                color=top_clusters['zone_color'],  # Color based on zone
                opacity=0.7
            ),
            text=top_clusters.apply(
                lambda row: (
                    f"{row['cluster_name']}<br>"  # Name clusters as 1 to 10
                    f"Fatalities: {row['fatalities']}<br>"
                    f"Zone: {row['zone_label']}"
                ),
                axis=1
            ),
            hoverinfo="text",
        ))

        # Increase the height of the map
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=df['LATITUDE'].mean(), lon=df['LONGITUD'].mean()),
                zoom=7
            ),
            title="Crash Hotspots (DBSCAN Clustering -> All Fatal Crashes from 2015 to 2023)",
            title_x=0.5,
            margin={"r":0,"t":40,"l":0,"b":0},
            height=800  # Increased height for the map
        )

        # Outliers: Ensure they are plotted with a distinct color and size
        if show_outliers:  # Check if outliers should be shown
            outliers = df[df['cluster'] == -1]  # Select the outliers (cluster == -1)
            if not outliers.empty:
                fig.add_trace(go.Scattermapbox(
                    lat=outliers['LATITUDE'],
                    lon=outliers['LONGITUD'],
                    mode='markers',
                    marker=dict(
                        size=5,  # Smaller size for outliers
                        color="black",  # Set outliers to black color
                        opacity=1
                    ),
                    text=outliers.apply(
                        lambda row: f"Outlier<br>Lat: {row['LATITUDE']}<br>Lon: {row['LONGITUD']}",
                        axis=1
                    ),
                    hoverinfo="text",
                    name="Outliers"
                ))

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📊 Cluster Metrics")

        # Create a summary of the clusters
        cluster_summary = df.groupby('cluster').agg(
            crashes=('LATITUDE', 'size'),
            fatalities=('FATALS', 'sum'),
            zone_label=('zone_label', 'first')
        ).reset_index()

        # Handle the case based on county or city
        if filters_dict["county"] != "All counties":
            top_n = 5
        elif filters_dict["city"] != "All cities":
            top_n = 3
        else:
            top_n = 10

        # Limit to top N clusters
        top_clusters = cluster_summary.nlargest(top_n, "crashes")

        # Add cluster names
        top_clusters['cluster_name'] = ['Cluster ' + str(i+1) for i in range(len(top_clusters))]

        # Color the zone_label column based on its value
        def color_zone_label(zone):
            if zone == "Danger":
                return f"<span style='color:red'>{zone}</span>"
            elif zone == "Mild":
                return f"<span style='color:yellow'>{zone}</span>"
            else:
                return f"<span style='color:green'>{zone}</span>"

        top_clusters['zone_label'] = top_clusters['zone_label'].apply(color_zone_label)

        # Display the top N clusters in a table
        st.write(f"Top {top_n} Crash Hotspots:")
        st.markdown(top_clusters[['cluster_name', 'zone_label', 'fatalities']].to_html(escape=False), unsafe_allow_html=True)

    st.markdown("---")

def render_dbscan_page(df: pd.DataFrame):
    st.markdown(
        """
        <h1>🚗 Colorado Crash Hotspot with DBSCAN Clustering</h1>
        <p>Identify crash hotspots across Colorado using DBSCAN (2015–2023)</p>
        """,
        unsafe_allow_html=True,
    )

    filters_dict = hotspot_sidebar_filters(df)
    filtered = apply_hotspot_filters(df, filters_dict)

    # Check if any data remains after filtering
    if filtered.empty:
        st.error("No data points match the current filters. Please adjust the filters and try again.")
        return

    filters_dict_dbscan = dbscan_filters()
    eps = filters_dict_dbscan["eps"]
    min_samples = filters_dict_dbscan["min_samples"]
    show_outliers = filters_dict_dbscan["show_outliers"]  # Get show_outliers directly

    # Apply DBSCAN clustering
    clustered_df = apply_dbscan_clustering(filtered, eps, min_samples)

    # Ensure the 'cluster' column is present before proceeding
    if 'cluster' not in clustered_df.columns:
        st.error("Clustering failed. No valid clusters found.")
        return

    # Handle outliers only if "Show Outliers" is toggled on
    if not show_outliers:
        clustered_df = clustered_df[clustered_df['cluster'] != -1]  # Remove outliers

    # Generate map and metrics based on the filtered and clustered data
    col1, col2 = st.columns([3, 1])

    render_map_and_metrics_with_dbscan(clustered_df, filters_dict, col1, col2, show_outliers)  # Pass show_outliers as argument

