import streamlit as st
import pandas as pd

def _weather_label(raw: str) -> str:
    if raw == "Clear":
        return "☀️ Clear"
    if raw == "Rain":
        return "🌧️ Rain"
    if raw == "Snow / Ice":
        return "❄️ Snow / Ice"
    if raw == "Fog / Smoke":
        return "🌫️ Fog / Smoke"
    return "🌪️ Other / Unknown"

def _route_label(raw: str) -> str:
    if raw == "Interstate":
        return "🛣️ Interstate"
    if raw == "US Highway":
        return "🛣️ US Highway"
    if raw == "State Highway":
        return "🛣️ State Highway"
    if raw == "County Road":
        return "🛤️ County Road"
    if raw == "City Street":
        return "🏙️ City Street"
    if raw == "Local Road":
        return "🚗 Local Road"
    if raw == "Ramp":
        return "↗️ Ramp"
    if raw == "Private Road":
        return "🚧 Private Road"
    return "❓ Other / Unknown"

def hotspot_sidebar_filters(df: pd.DataFrame) -> dict:
    st.sidebar.markdown("<h3 style='margin-bottom:4px;'>🧭 Filters</h3>", unsafe_allow_html=True)

    year_series = df["YEAR"].dropna()
    year_min, year_max = int(year_series.min()), int(year_series.max())

    fat_series = df["FATALS"].dropna()
    fat_min, fat_max = int(fat_series.min()), int(fat_series.max())

    pod_values = sorted([p for p in df["PART_OF_DAY"].dropna().unique() if p != "Unknown"])

    month_order = [
        "January", "February", "March", "April", "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]
    month_values = sorted(
        [m for m in df["MONTHNAME"].dropna().unique() if m != "Unknown"],
        key=lambda x: month_order.index(x)
    )

    season_order = ["Winter", "Spring", "Summer", "Fall"]
    season_values = sorted(
        [s for s in df["SEASON"].dropna().unique() if s != "Unknown"],
        key=lambda x: season_order.index(x)
    )

    weather_order = ["Clear", "Rain", "Snow / Ice", "Fog / Smoke"]
    weather_raw_values = sorted(
        df["WEATHER_MAJOR"].dropna().unique().tolist(),
        key=lambda x: weather_order.index(x) if x in weather_order else len(weather_order)
    )

    time_order = ["Morning", "Afternoon", "Evening", "Night"]
    pod_values = sorted(
        [p for p in pod_values if p != "Unknown"],
        key=lambda x: time_order.index(x)
    )

    route_raw_values = sorted(df["ROUTE_GROUP"].dropna().unique().tolist())
    county_values = sorted(df["COUNTYNAME"].dropna().unique().tolist())

    pod_label_map = {
        "Night": "🌙 Night (12am–5am)",
        "Morning": "🌅 Morning (6am–11am)",
        "Afternoon": "🌞 Afternoon (12pm–5pm)",
        "Evening": "🌆 Evening (6pm–11pm)",
    }
    season_label_map = {
        "Winter": "❄️ Winter (Dec–Feb)",
        "Spring": "🌱 Spring (Mar–May)",
        "Summer": "☀️ Summer (Jun–Aug)",
        "Fall": "🍂 Fall (Sep–Nov)",
    }

    s = st.session_state
    if "filters_initialized" not in s:
        s.year_range = (year_min, year_max)
        s.pod_select = "All times"
        s.month_select = "All months"
        s.season_select = "All seasons"
        s.weather_select = "All weather"
        s.route_select = "All roads"
        s.county_select = "All counties"
        s.city_select = "All cities"
        s.fat_range = (fat_min, fat_max)
        s.overlay_points = True
        s.filters_initialized = True

    if st.sidebar.button("🧹 Clear all filters"):
        s.year_range = (year_min, year_max)
        s.pod_select = "All times"
        s.month_select = "All months"
        s.season_select = "All seasons"
        s.weather_select = "All weather"
        s.route_select = "All roads"
        s.county_select = "All counties"
        s.city_select = "All cities"
        s.fat_range = (fat_min, fat_max)
        s.overlay_points = True

    year_range = st.sidebar.slider(
        "📅 Year range",
        min_value=year_min,
        max_value=year_max,
        key="year_range",
    )

    pod_display_options = ["All times"]
    display_to_pod_raw = {"All times": None}
    for raw in pod_values:
        label = pod_label_map.get(raw, raw)
        pod_display_options.append(label)
        display_to_pod_raw[label] = raw

    selected_pod_disp = st.sidebar.selectbox(
        "⏱️ Time of day",
        options=pod_display_options,
        key="pod_select",
    )
    selected_pod_raw = display_to_pod_raw[selected_pod_disp]

    month_display_options = ["All months"] + month_values
    display_to_month_raw = {"All months": None}
    for m in month_values:
        display_to_month_raw[m] = m

    selected_month_disp = st.sidebar.selectbox(
        "📆 Month",
        options=month_display_options,
        key="month_select",
    )
    selected_month_raw = display_to_month_raw[selected_month_disp]

    season_display_options = ["All seasons"]
    display_to_season_raw = {"All seasons": None}
    for s_val in season_values:
        label = season_label_map.get(s_val, s_val)
        season_display_options.append(label)
        display_to_season_raw[label] = s_val

    selected_season_disp = st.sidebar.selectbox(
        "🍂 Season",
        options=season_display_options,
        key="season_select",
    )
    selected_season_raw = display_to_season_raw[selected_season_disp]

    weather_label_map = {raw: _weather_label(raw) for raw in weather_raw_values}
    weather_display = ["All weather"]
    display_to_weather_raw = {"All weather": None}
    for raw in weather_raw_values:
        label = weather_label_map[raw]
        weather_display.append(label)
        display_to_weather_raw[label] = raw

    selected_weather_disp = st.sidebar.selectbox(
        "🌦️ Weather",
        options=weather_display,
        key="weather_select",
    )
    selected_weather_raw = display_to_weather_raw[selected_weather_disp]

    route_label_map = {raw: _route_label(raw) for raw in route_raw_values}
    route_display = ["All roads"]
    display_to_route_raw = {"All roads": None}
    for raw in route_raw_values:
        label = route_label_map[raw]
        route_display.append(label)
        display_to_route_raw[label] = raw

    selected_route_disp = st.sidebar.selectbox(
        "🛣️ Road type",
        options=route_display,
        key="route_select",
    )
    selected_route_raw = display_to_route_raw[selected_route_disp]

    fat_range = st.sidebar.slider(
        "☠️ Fatalities per crash",
        min_value=fat_min,
        max_value=fat_max,
        key="fat_range",
    )

    county_options = ["All counties"] + county_values
    selected_county = st.sidebar.selectbox(
        "🏞️ County",
        options=county_options,
        key="county_select",
    )

    if selected_county != "All counties":
        city_subset = df[df["COUNTYNAME"] == selected_county]
    else:
        city_subset = df
    city_values = sorted(city_subset["CITYNAME"].dropna().unique().tolist())
    city_options = ["All cities"] + city_values

    selected_city = st.sidebar.selectbox(
        "🏙️ City",
        options=city_options,
        key="city_select",
    )

    overlay = st.sidebar.checkbox(
        "🧊 Show individual crash points",
        key="overlay_points",
    )

    return dict(
        year_range=year_range,
        part_of_day=selected_pod_raw,
        month=selected_month_raw,
        season=selected_season_raw,
        weather_raw=selected_weather_raw,
        route_raw=selected_route_raw,
        fat_range=fat_range,
        county=selected_county,
        city=selected_city,
        overlay=overlay,
    )

def apply_hotspot_filters(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    if df.empty:
        return df

    mask = df["YEAR"].between(f["year_range"][0], f["year_range"][1])

    if f["part_of_day"] is not None:
        mask &= df["PART_OF_DAY"] == f["part_of_day"]

    if f["month"] is not None:
        mask &= df["MONTHNAME"] == f["month"]

    if f["season"] is not None:
        mask &= df["SEASON"] == f["season"]

    if f["weather_raw"] is not None:
        mask &= df["WEATHER_MAJOR"] == f["weather_raw"]

    if f["route_raw"] is not None:
        mask &= df["ROUTE_GROUP"] == f["route_raw"]

    mask &= df["FATALS"].between(f["fat_range"][0], f["fat_range"][1])

    if f["county"] != "All counties":
        mask &= df["COUNTYNAME"] == f["county"]

    if f["city"] != "All cities":
        mask &= df["CITYNAME"] == f["city"]

    return df[mask].copy()
