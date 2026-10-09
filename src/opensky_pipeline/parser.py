from datetime import datetime, timezone

def parse_states(response_json: dict) -> tuple[list[dict], int]:
    rows = []
    skipped = 0

    for state in response_json.get("states") or []:
        icao24, time_position, longitude, latitude = state[0], state[3], state[5], state[6]
        if icao24 is None or time_position is None or longitude is None or latitude is None:
            skipped += 1
            continue

        rows.append({
            "icao24": icao24,
            "callsign": (state[1] or "").strip() or None,
            "position_time": datetime.fromtimestamp(time_position, tz=timezone.utc),
            "longitude": longitude,
            "latitude": latitude,
            "geo_altitude": state[13],
            "speed": state[9],
            "heading": state[10],
            "on_ground": state[8],
        })

    return rows, skipped