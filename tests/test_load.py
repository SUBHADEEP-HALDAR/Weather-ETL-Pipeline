import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import load


def test_run_log_records_a_run():
    conn = sqlite3.connect(":memory:")
    load.init_db(conn)
    load.log_run(conn, cities_ok=4, cities_failed=1, rows_loaded=192, run_at="2026-10-11 10:05:00")
    row = conn.execute(
        "SELECT run_at, cities_ok, cities_failed, rows_loaded FROM etl_runs"
    ).fetchone()
    assert row == ("2026-10-11 10:05:00", 4, 1, 192)
