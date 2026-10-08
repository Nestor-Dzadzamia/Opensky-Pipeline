from pathlib import Path
from typing import LiteralString, cast
import psycopg
from opensky_pipeline import config


SCHEMA_PATH = Path(__file__).parent / "sql" /"schema.sql"

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
    print("schema initialized")