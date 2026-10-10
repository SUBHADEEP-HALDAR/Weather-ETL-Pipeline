#"""Run the full ETL: python main.py"""
import logging
import sys

import config
import extract
import load
import transform


def setup_logging() -> None:
    config.LOG_PATH.parent.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(config.LOG_PATH), logging.StreamHandler()],
    )


def run() -> int:
    log = logging.getLogger("main")
    conn = load.get_connection()
    failures = 0
    for city, (lat, lon) in config.CITIES.items():
        try:
            raw = extract.fetch_city(city, lat, lon)
            df = transform.transform(city, raw)
            load.load(df, conn)
        except Exception:
            failures += 1
            log.exception("Pipeline failed for %s", city)  # one city failing must not stop the rest
    conn.close()
    log.info("Done. %d/%d cities failed", failures, len(config.CITIES))
    return 1 if failures else 0


if __name__ == "__main__":
    setup_logging()
    sys.exit(run())
