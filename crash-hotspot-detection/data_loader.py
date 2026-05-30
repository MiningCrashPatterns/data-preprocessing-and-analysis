from typing import Optional
import re
import pandas as pd
import streamlit as st

CO_LAT_MIN, CO_LAT_MAX = 36.5, 41.2
CO_LON_MIN, CO_LON_MAX = -109.1, -101.0

def _extract_hour_from_name(val: Optional[str]) -> Optional[int]:
    if not isinstance(val, str):
        return None
    s = val.strip().lower()
    if not s or "unknown" in s or s == "nan":
        return None

    m = re.search(r"(\d{1,2})", s)
    if not m:
        return None

    h12 = int(m.group(1))
    if "pm" in s and h12 < 12:
        return h12 + 12
    if "am" in s and h12 == 12:
        return 0
    return h12

def _categorize_part_of_day(hour: Optional[float]) -> str:
    if hour is None or pd.isna(hour):
        return "Unknown"
    try:
        h = int(hour)
    except Exception:
        return "Unknown"

    if 0 <= h <= 5:
        return "Night"
    if 6 <= h <= 11:
        return "Morning"
    if 12 <= h <= 17:
        return "Afternoon"
    if 18 <= h <= 23:
        return "Evening"
    return "Unknown"

def _season_from_monthname(name: Optional[str]) -> str:
    if not isinstance(name, str):
        return "Unknown"
    s = name.strip().lower()
    if not s:
        return "Unknown"
    key = s[:3]

    if key in ("dec", "jan", "feb"):
        return "Winter"
    if key in ("mar", "apr", "may"):
        return "Spring"
    if key in ("jun", "jul", "aug"):
        return "Summer"
    if key in ("sep", "oct", "nov"):
        return "Fall"
    return "Unknown"

def _weather_group(name: Optional[str]) -> str:
    if not isinstance(name, str):
        return "Other / Unknown"
    s = name.upper()
    if "CLEAR" in s:
        return "Clear"
    if "RAIN" in s or "DRIZZLE" in s or "SHOWER" in s:
        return "Rain"
    if "SNOW" in s or "SLEET" in s or "ICE" in s or "HAIL" in s:
        return "Snow / Ice"
    if "FOG" in s or "SMOKE" in s or "MIST" in s:
        return "Fog / Smoke"
    return "Other / Unknown"

def _route_group(name: Optional[str]) -> str:
    if not isinstance(name, str):
        return "Other / Unknown"
    s = name.upper()
    if "INTERSTATE" in s or s.startswith("I-"):
        return "Interstate"
    if "U.S." in s or "US " in s:
        return "US Highway"
    if "STATE" in s or "ST RT" in s or "ST. RT" in s:
        return "State Highway"
    if "COUNTY" in s:
        return "County Road"
    if "CITY" in s or "URBAN" in s or "TOWN" in s:
        return "City Street"
    if "LOCAL" in s:
        return "Local Road"
    if "RAMP" in s:
        return "Ramp"
    if "PRIVATE" in s or "DRIVEWAY" in s:
        return "Private Road"
    return "Other / Unknown"

@st.cache_data
def load_and_prepare_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    required = ["LATITUDE", "LONGITUD", "YEAR", "FATALS"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Missing required columns in CSV: {missing}")
        st.stop()

    for col in ["LATITUDE", "LONGITUD", "YEAR", "FATALS"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["LATITUDE", "LONGITUD"])
    df = df[
        df["LATITUDE"].between(CO_LAT_MIN, CO_LAT_MAX)
        & df["LONGITUD"].between(CO_LON_MIN, CO_LON_MAX)
    ]

    if df.empty:
        return df

    for col in ["DAY_WEEKNAME", "WEATHERNAME", "COUNTYNAME", "CITYNAME", "ROUTENAME", "MONTHNAME"]:
        if col not in df.columns:
            df[col] = "Unknown"
        df[col] = df[col].fillna("Unknown")

    if "HOURNAME" in df.columns:
        df["HOUR"] = df["HOURNAME"].apply(_extract_hour_from_name)
    else:
        df["HOUR"] = pd.NA
    df["PART_OF_DAY"] = df["HOUR"].apply(_categorize_part_of_day)

    df["SEASON"] = df["MONTHNAME"].apply(_season_from_monthname)

    df["WEATHER_MAJOR"] = df["WEATHERNAME"].apply(_weather_group)
    df["ROUTE_GROUP"] = df["ROUTENAME"].apply(_route_group)

    return df