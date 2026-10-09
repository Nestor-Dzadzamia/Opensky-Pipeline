from pathlib import Path
from typing import LiteralString, cast
import psycopg
from opensky_pipeline import config


SCHEMA_PATH = Path(__file__).parent / "sql" /"schema.sql"

SQL_INSERT: LiteralString = """
    INSERT INTO flight_tracker.aircraft_positions (
        icao24, callsign, position_time, longitude, latitude, geo_altitude, speed, heading, on_ground
    ) 
    VALUES (
        %(icao24)s, %(callsign)s, %(position_time)s, %(longitude)s, %(latitude)s,
        %(geo_altitude)s, %(speed)s, %(heading)s, %(on_ground)s
    )
    ON CONFLICT (icao24, position_time) DO NOTHING
"""

def connect_to_db() -> psycopg.Connection:
    return psycopg.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        connect_timeout=10,
    )

def init_db() -> None:
    schema_sql = SCHEMA_PATH.read_text()
    with connect_to_db() as conn:
        conn.execute(cast(LiteralString,schema_sql))
    print("schema initialized") # aq dalogva unda amis


def insert_data(rows: list[dict]) -> int:
    if not rows:
        return 0
    with connect_to_db() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(SQL_INSERT, rows)
            return cursor.rowcount