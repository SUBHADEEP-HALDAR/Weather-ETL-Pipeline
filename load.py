"""LOAD: write clean rows into SQLite using an upsert (safe to re-run)."""
import logging
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

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

RUNS_SCHEMA = """
CREATE TABLE IF NOT EXISTS etl_runs (
    run_at        TEXT NOT NULL,
    cities_ok     INTEGER,
    cities_failed INTEGER,
    rows_loaded   INTEGER
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


def init_db(conn: sqlite3.Connection) -> None:
    """Create the tables if they don't exist yet."""
    conn.execute(SCHEMA)
    conn.execute(RUNS_SCHEMA)


def get_connection() -> sqlite3.Connection:
    config.DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    init_db(conn)
    return conn


def log_run(conn: sqlite3.Connection, cities_ok: int, cities_failed: int,
            rows_loaded: int, run_at: str | None = None) -> None:
    """Record one pipeline run so the dashboard can show when data was last updated."""
    if run_at is None:
        run_at = datetime.now(ZoneInfo(config.TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
    with conn:
        conn.execute(
            "INSERT INTO etl_runs (run_at, cities_ok, cities_failed, rows_loaded) VALUES (?, ?, ?, ?)",
            (run_at, cities_ok, cities_failed, rows_loaded),
        )


def load(df: pd.DataFrame, conn: sqlite3.Connection) -> int:
    rows = list(df.itertuples(index=False, name=None))
    with conn:  # commits on success, rolls back on error
        conn.executemany(UPSERT, rows)
    log.info("Loaded %d rows", len(rows))
    return len(rows)
