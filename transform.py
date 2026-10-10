"""TRANSFORM: turn the raw API JSON into a clean DataFrame."""
import logging

import pandas as pd

log = logging.getLogger(__name__)

COLUMN_MAP = {
    "time": "timestamp",
    "temperature_2m": "temp_c",
    "relative_humidity_2m": "humidity_pct",
    "precipitation": "precip_mm",
    "wind_speed_10m": "wind_kmh",
}


def transform(city: str, raw: dict) -> pd.DataFrame:
    df = pd.DataFrame(raw["hourly"]).rename(columns=COLUMN_MAP)

    # types
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for col in ["temp_c", "humidity_pct", "precip_mm", "wind_kmh"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # cleaning
    before = len(df)
    df = df.dropna(subset=["temp_c"]).drop_duplicates(subset=["timestamp"])
    df = df[df["temp_c"].between(-60, 60) & df["humidity_pct"].between(0, 100)]
    dropped = before - len(df)
    if dropped:
        log.warning("%s: dropped %d bad rows", city, dropped)

    # derived columns
    df["city"] = city
    df["temp_f"] = (df["temp_c"] * 9 / 5 + 32).round(1)
    df["is_rainy"] = (df["precip_mm"] > 0).astype(int)

    # SQLite has no datetime type, so store ISO text
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")

    return df[["city", "timestamp", "temp_c", "temp_f", "humidity_pct",
               "precip_mm", "wind_kmh", "is_rainy"]].reset_index(drop=True)
