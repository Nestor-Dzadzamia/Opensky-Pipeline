
import psycopg2
from psycopg2.extensions import connection

from opensky_pipeline.config import Config
from opensky_pipeline.sql import queries


class DatabaseManager:
    def __init__(self, config: Config):
        self._config = config

        schema_sql = queries.SQL_SCHEMA_CREATION
        with self.connect_to_db(self._config) as conn, conn.cursor() as cur:
            cur.execute(schema_sql)

    def insert_data(self, rows: list[dict]) -> int:
        if not rows:
            return 0
        with self.connect_to_db(self._config) as conn, conn.cursor() as cursor:
            cursor.executemany(queries.SQL_INSERT, rows)
            return cursor.rowcount

    @staticmethod
    def connect_to_db(config: Config) -> connection:
        return psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            connect_timeout=10
        )