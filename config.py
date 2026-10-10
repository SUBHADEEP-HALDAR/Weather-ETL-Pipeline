"""Central settings for the ETL pipeline."""
from pathlib import Path

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "raw"
DB_PATH = BASE_DIR / "data" / "weather.db"
LOG_PATH = BASE_DIR / "logs" / "etl.log"

API_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY_FIELDS = ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"]

CITIES = {
    "Kolkata": (22.57, 88.36),
    "Durgapur": (23.52, 87.31),
    "Bardhaman": (23.23, 87.86),
    "Delhi": (28.61, 77.21),
    "Mumbai": (19.08, 72.88),
}
TIMEZONE = "Asia/Kolkata"
