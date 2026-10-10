"""LOAD: write clean rows into SQLite using an upsert (safe to re-run)."""
import logging
import sqlite3

import pandas as pd

import config

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS weather (
    city         TEXT NOT NULL,
    timestamp    TEXT NOT NULL,
    temp_c       REAL,
    temp_f       REAL,
    humidity_pct REAL,
    precip_mm    REAL,
    wind_kmh     REAL,
    is_rainy     INTEGER,
    PRIMARY KEY (city, timestamp)
);
"""

UPSERT = """
INSERT INTO weather (city, timestamp, temp_c, temp_f, humidity_pct, precip_mm, wind_kmh, is_rainy)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(city, timestamp) DO UPDATE SET
    temp_c=excluded.temp_c, temp_f=excluded.temp_f,
    humidity_pct=excluded.humidity_pct, precip_mm=excluded.precip_mm,
    wind_kmh=excluded.wind_kmh, is_rainy=excluded.is_rainy;
"""


def get_connection() -> sqlite3.Connection:
    config.DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute(SCHEMA)
    return conn


def load(df: pd.DataFrame, conn: sqlite3.Connection) -> int:
    rows = list(df.itertuples(index=False, name=None))
    with conn:  # commits on success, rolls back on error
        conn.executemany(UPSERT, rows)
    log.info("Loaded %d rows", len(rows))
    return len(rows)
