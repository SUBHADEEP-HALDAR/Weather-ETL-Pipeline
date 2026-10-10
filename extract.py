"""EXTRACT: fetch raw JSON from the Open-Meteo API and keep a copy on disk."""
import json
import logging
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config

log = logging.getLogger(__name__)


def _session() -> requests.Session:
    """Session that retries on temporary failures (429 / 5xx)."""
    retry = Retry(total=3, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


def fetch_city(city: str, lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(config.HOURLY_FIELDS),
        "past_days": 1,
        "forecast_days": 1,
        "timezone": config.TIMEZONE,
    }
    log.info("Fetching %s", city)
    resp = _session().get(config.API_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    _save_raw(city, data)
    return data


def _save_raw(city: str, data: dict) -> None:
    """Keep the untouched response so you can re-process it later."""
    config.RAW_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = config.RAW_DIR / f"{city.lower()}_{stamp}.json"
    path.write_text(json.dumps(data))
