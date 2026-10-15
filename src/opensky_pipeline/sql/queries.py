from typing import LiteralString

# language=postgresql
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

# language=postgresql
SQL_SCHEMA_CREATION: LiteralString = """
    CREATE SCHEMA IF NOT EXISTS flight_tracker;

    CREATE TABLE IF NOT EXISTS flight_tracker.aircraft_positions (
        icao24        text,
        callsign      text,
        position_time timestamptz,
        longitude     double precision  not null,
        latitude      double precision  not null,
        geo_altitude  double precision,
        speed         double precision,
        heading       double precision,
        on_ground     boolean,
    
        primary key (icao24, position_time)
    );
"""
