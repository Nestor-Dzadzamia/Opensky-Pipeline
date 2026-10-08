CREATE SCHEMA IF NOT EXISTS flight_tracker;

CREATE TABLE IF NOT EXISTS flight_tracker.aircraft_positions (
    icao24        TEXT,
    callsign      TEXT,
    position_time TIMESTAMPTZ,
    longitude     DOUBLE PRECISION NOT NULL,
    latitude      DOUBLE PRECISION NOT NULL,
    altitude      DOUBLE PRECISION,
    speed         DOUBLE PRECISION,
    heading       DOUBLE PRECISION,
    on_ground     BOOLEAN,

    PRIMARY KEY (icao24, position_time)
);
