from datetime import UTC, datetime

import pandas as pd

STATE_COLUMNS = (
    "icao24", "callsign", "origin_country", "time_position", "last_contact",
    "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
    "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
    "spi", "position_source",
)


def parse_states(response_json: dict) -> tuple[list[dict], int]:
    data = pd.DataFrame(response_json.get("states") or [], columns=STATE_COLUMNS)
    data = data.astype(object).where(data.notna(), None)
    rows = []
    skipped = 0

    for row in data.itertuples(index=False):
        icao24, time_position, longitude, latitude = row.icao24, row.time_position, row.longitude, row.latitude
        if icao24 is None or time_position is None or longitude is None or latitude is None:
            skipped += 1
            continue

        rows.append({
            "icao24": icao24,
            "callsign": (row.callsign or "").strip() or None,
            "position_time": datetime.fromtimestamp(time_position, tz=UTC),
            "longitude": longitude,
            "latitude": latitude,
            "geo_altitude": row.geo_altitude,
            "speed": row.velocity,
            "heading": row.true_track,
            "on_ground": row.on_ground,
        })

    return rows, skipped