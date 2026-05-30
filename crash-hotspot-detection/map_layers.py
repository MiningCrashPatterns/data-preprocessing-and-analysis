import plotly.graph_objects as go
import plotly.express as px

def build_hotspot_figure(df, filters_dict, overlay=True):
    COLORADO_CENTER = (39.0, -105.5)

    if filters_dict["city"] != "All cities":
        focus = df[df["CITYNAME"] == filters_dict["city"]]
        lat, lon = float(focus["LATITUDE"].mean()), float(focus["LONGITUD"].mean())
        zoom = 11.5
    elif filters_dict["county"] != "All counties":
        focus = df[df["COUNTYNAME"] == filters_dict["county"]]
        lat, lon = float(focus["LATITUDE"].mean()), float(focus["LONGITUD"].mean())
        zoom = 9.9
    else:
        lat, lon, zoom = COLORADO_CENTER[0], COLORADO_CENTER[1], 6.7

    global_min_fatal = df["FATALS"].min()
    global_max_fatal = df["FATALS"].max()

    df["FATALS_CLIPPED"] = df["FATALS"].clip(lower=global_min_fatal, upper=global_max_fatal)

    color_scale = ["#ffe5e5", "#ff0000"]

    fig = px.density_mapbox(
        df,
        lat="LATITUDE",
        lon="LONGITUD",
        z="FATALS_CLIPPED",
        radius=40,
        opacity=0.90,
        center={"lat": lat, "lon": lon},
        zoom=zoom,
        mapbox_style="open-street-map",
        color_continuous_scale=color_scale,
        range_color=[global_min_fatal, global_max_fatal],
    )

    fig.update_layout(
        title="Crash Density Heatmap (All Fatal Crashes from 2015 to 2023)",
        title_x=0.5,
        margin=dict(l=0, r=0, t=40, b=0),
        height=750,
        mapbox=dict(center=dict(lat=lat, lon=lon), zoom=zoom, style="open-street-map"),
    )

    if overlay:
        fig.add_scattermapbox(
            lat=df["LATITUDE"],
            lon=df["LONGITUD"],
            mode="markers",
            marker=dict(size=7, color="rgba(200,0,0,0.85)"),
            hoverinfo="text",
            hovertext=df.apply(
                lambda r: (
                    f"Year: {int(r.YEAR)} | FATALS: {int(r.FATALS)}<br>"
                    f"{r.COUNTYNAME}, {r.CITYNAME}<br>"
                    f"Weather: {r.WEATHERNAME}<br>"
                    f"Road: {r.ROUTENAME}"
                ),
                axis=1,
            ),
            name="Crashes",
        )

    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Crash Density",
            tickvals=[],
            ticktext=[],
        )
    )

    return fig
