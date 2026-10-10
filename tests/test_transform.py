import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from transform import transform


def fake_raw():
    return {"hourly": {
        "time": ["2026-10-10T00:00", "2026-10-10T01:00", "2026-10-10T01:00", "2026-10-10T02:00", "2026-10-10T03:00"],
        "temperature_2m": [25.0, 26.0, 26.0, None, 99.0],
        "relative_humidity_2m": [80, 78, 78, 70, 60],
        "precipitation": [0.0, 1.2, 1.2, 0.0, 0.0],
        "wind_speed_10m": [5.0, 6.0, 6.0, 4.0, 3.0],
    }}


def test_removes_duplicates_nulls_and_outliers():
    df = transform("Kolkata", fake_raw())
    assert len(df) == 2  # 1 duplicate, 1 null temp, 1 impossible temp removed


def test_derived_columns():
    df = transform("Kolkata", fake_raw())
    assert df.loc[0, "temp_f"] == 77.0
    assert df.loc[1, "is_rainy"] == 1
    assert (df["city"] == "Kolkata").all()
