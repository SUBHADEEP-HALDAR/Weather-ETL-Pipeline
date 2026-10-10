"""Live dashboard for the weather ETL pipeline.  Run locally: streamlit run app.py"""
import sqlite3

import pandas as pd
import streamlit as st

import config

REPO_URL = "https://github.com/SUBHADEEP-HALDAR/weather-etl-pipeline"

st.set_page_config(page_title="Weather ETL Dashboard", page_icon="🌦️", layout="wide")


@st.cache_data(ttl=600)
def load_data() -> pd.DataFrame:
    conn = sqlite3.connect(config.DB_PATH)
    try:
        return pd.read_sql(
            "SELECT * FROM weather ORDER BY timestamp", conn, parse_dates=["timestamp"]
        )
    finally:
        conn.close()


st.title("🌦️ Weather ETL Dashboard")
st.caption(
    "Data is collected automatically every day by an ETL pipeline "
    "(Open-Meteo API → Pandas → SQLite → GitHub Actions)."
)

try:
    df = load_data()
except Exception:
    st.error("No data found yet. Run the pipeline (python main.py) first.")
    st.stop()

if df.empty:
    st.warning("The database is empty. Run the pipeline first.")
    st.stop()

# ---- sidebar filters ----
all_cities = sorted(df["city"].unique())
cities = st.sidebar.multiselect("Cities", all_cities, default=all_cities)
st.sidebar.markdown(f"[View source code on GitHub]({REPO_URL})")
if not cities:
    st.info("Select at least one city in the sidebar.")
    st.stop()

view = df[df["city"].isin(cities)]

st.caption(f"Data covers {view['timestamp'].min():%d %b %Y %H:%M} to "
           f"{view['timestamp'].max():%d %b %Y %H:%M} (IST)  |  {len(view)} rows")

# ---- summary metrics per city ----
st.subheader("Summary")
cols = st.columns(len(cities))
for col, city in zip(cols, cities):
    c = view[view["city"] == city]
    with col:
        st.markdown(f"**{city}**")
        st.metric("Avg temp", f"{c['temp_c'].mean():.1f} °C")
        st.metric("Max temp", f"{c['temp_c'].max():.1f} °C")
        st.metric("Total rain", f"{c['precip_mm'].sum():.1f} mm")

# ---- charts ----
def pivot(column: str) -> pd.DataFrame:
    return view.pivot_table(index="timestamp", columns="city", values=column)

st.subheader("Temperature (°C)")
st.line_chart(pivot("temp_c"))

left, right = st.columns(2)
with left:
    st.subheader("Humidity (%)")
    st.line_chart(pivot("humidity_pct"))
with right:
    st.subheader("Rainfall (mm)")
    st.bar_chart(pivot("precip_mm"))

st.subheader("Wind speed (km/h)")
st.line_chart(pivot("wind_kmh"))

with st.expander("See raw data"):
    st.dataframe(view.sort_values("timestamp", ascending=False), use_container_width=True)
