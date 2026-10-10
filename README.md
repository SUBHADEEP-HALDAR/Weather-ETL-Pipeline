# Weather ETL Pipeline

Daily ETL that pulls hourly weather for several Indian cities from the Open-Meteo API,
cleans it with Pandas, and upserts it into SQLite (idempotent: re-running never creates duplicates).

## Pipeline
API -> extract.py (raw JSON saved to raw/) -> transform.py (clean + derive) -> load.py (SQLite upsert)

## Run
    pip install -r requirements.txt
    python main.py
    pytest

## Query the data
    sqlite3 data/weather.db "SELECT city, ROUND(AVG(temp_c),1) FROM weather GROUP BY city;"

## Roadmap
- [ ] Schedule daily with GitHub Actions
- [ ] Migrate SQLite -> PostgreSQL (SQLAlchemy)
- [ ] Data-quality report
