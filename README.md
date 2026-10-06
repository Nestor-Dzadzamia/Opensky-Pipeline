# Opensky-Pipeline
Scheduled ETL that pulls live ADS-B aircraft states from the OpenSky API and loads them into PostgreSQL with deduplication, retry/backoff on rate limits, and logging.
