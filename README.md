# OpenSky Pipeline

A small data pipeline that collects live aircraft positions around Tbilisi International Airport (TBS) from the [OpenSky Network API](https://openskynetwork.github.io/opensky-api/rest.html) and stores them in PostgreSQL. Cron runs it once a minute, so the table keeps growing on its own.

Each run does the same few things:

1. Gets an OAuth2 access token from OpenSky
2. Asks `/states/all` for every aircraft inside the bounding box
3. Cleans up the response (skips broken rows, fixes types)
4. Inserts the rows into PostgreSQL, ignoring anything already stored
5. Writes a short summary to the log

```
2026-10-12 10:52:01 INFO run started
2026-10-12 10:52:02 INFO fetched=3 parsed=3 skipped=0 inserted=1 duplicates=2
2026-10-12 10:52:02 INFO run finished
```

## The region

The bounding box is 1 degree in every direction around Tbilisi International Airport:

| | min | max |
|---|---|---|
| latitude | 40.67 | 42.67 |
| longitude | 43.95 | 45.95 |

<img width="1428" height="866" alt="image" src="https://github.com/user-attachments/assets/5799c92c-2050-4a2b-9e93-f2b517ca8b2a" />


That's 4 square degrees, well under the 25 sq° limit, so every call costs 1 API credit.

Fair warning: Tbilisi is not a huge hub, and OpenSky depends on volunteer receivers, which are sparse in the Caucasus. A typical call returns somewhere between 3 and 16 aircraft. Most of them are flights crossing Georgia between Europe and Asia at cruising altitude, plus whatever is landing at or leaving TBS. A box over Frankfurt or Istanbul would give a lot more rows. Switching is just a matter of changing the coordinates in `config.py`.

## Project layout

```
src/opensky_pipeline/
├── config.py      settings from .env, URLs, bounding box
├── auth.py        OAuth2 token (client credentials flow)
├── api.py         calls /states/all
├── parser.py      turns raw state vectors into clean rows
├── db.py          connection, schema setup, batch insert
├── main.py        runs everything, logging and error handling
└── sql/
    └── schema.sql the table definition
```

HTTP calls are async and go through one shared `httpx2` client per run. The database side uses `psycopg` 3.

## Setup

You'll need Python 3.13+, [uv](https://docs.astral.sh/uv/), PostgreSQL, and a free OpenSky account.

### 1. Install

```bash
git clone https://github.com/Nestor-Dzadzamia/Opensky-Pipeline.git
cd Opensky-Pipeline
uv sync
```

### 2. OpenSky credentials

Log in to opensky-network.org, open the Account page and create an API client. You'll get a client ID and a client secret.

### 3. Database

Create a dedicated user and a database owned by it. `--pwprompt` asks for the password, so it doesn't end up in your shell history.

```bash
createuser --pwprompt opensky_app
createdb --owner=opensky_app opensky
```

### 4. Environment

```bash
cp .env.example .env
```

Then fill in `.env` with your OpenSky client ID and secret and the database password you just set. `.env` is gitignored, so secrets never get committed.

### 5. Create the table

```bash
uv run opensky-init-db
```

It's safe to run again. Everything in `schema.sql` uses `IF NOT EXISTS`.

## Running it

Once by hand:

```bash
uv run opensky-pipeline
```

### Every minute with cron

Open your crontab:

```bash
crontab -e
```

and add this line (change the path to wherever you cloned the repo):

```
* * * * * /Users/nestordzadzamia/Projects/Opensky-Pipeline/.venv/bin/opensky-pipeline >> /Users/nestordzadzamia/Projects/Opensky-Pipeline/logs/cron.log 2>&1
```

A few notes on why it looks like this:

- Cron runs with an almost empty environment. No Homebrew in `PATH`, no activated venv, and the working directory is your home folder. So the line uses absolute paths only.
- `.venv/bin/opensky-pipeline` is the launcher uv generates from `pyproject.toml`. Its first line points at the venv's Python, so the venv doesn't need to be activated.
- The code finds `.env`, `schema.sql` and the log folder relative to its own files, so it doesn't care which directory cron starts it from.
- `>> logs/cron.log 2>&1` keeps anything printed before logging is set up, like a missing variable in `.env`.

Credit math: one call per minute is 1,440 calls a day. A standard OpenSky account gets 4,000 credits a day for `/states`, so there's plenty of room.

If you run this on a laptop, keep in mind cron doesn't run while the machine is asleep, and missed minutes are not made up later. `caffeinate -s` keeps a plugged-in Mac awake.

To stop it, run `crontab -e` again and delete the line.

## The table

`flight_tracker.aircraft_positions`, one row per position report:

| column | type | from the API (index) | notes |
|---|---|---|---|
| `icao24` | text | `icao24` (0) | the aircraft's transponder address |
| `callsign` | text | `callsign` (1) | trailing spaces trimmed, empty becomes NULL |
| `position_time` | timestamptz | `time_position` (3) | when the position was recorded, stored in UTC |
| `longitude` | double precision | `longitude` (5) | required |
| `latitude` | double precision | `latitude` (6) | required |
| `geo_altitude` | double precision | `geo_altitude` (13) | GPS altitude in meters, often NULL on the ground |
| `speed` | double precision | `velocity` (9) | ground speed in m/s |
| `heading` | double precision | `true_track` (10) | degrees clockwise from north |
| `on_ground` | boolean | `on_ground` (8) | |

Some choices worth explaining:

- **Altitude.** OpenSky gives two: barometric (index 7) and geometric (index 13). I store the geometric one, which comes from GPS.
- **Heading.** OpenSky doesn't send the direction the nose points. `true_track` is the direction the plane is actually moving over the ground, which is the closest thing available.
- **Time.** I use `time_position`, not `last_contact`. A plane can keep sending messages while its position hasn't updated for minutes. `last_contact` would keep changing in that case and make the same old position look like new data.
- **Time zones.** psql shows timestamps in your local time zone. The stored value is the same instant either way. Run `SET timezone = 'UTC';` if you want to see UTC.

## Duplicates

The primary key is `(icao24, position_time)`: one aircraft can't be in two places at the same moment. Inserts use `ON CONFLICT (icao24, position_time) DO NOTHING`, so if the same report comes back on the next call, Postgres just skips it. That happens a lot. Parked planes and planes whose position hasn't refreshed show up in several calls in a row.

The run summary reports how many rows were new and how many were duplicates. Running the pipeline twice in the same second gives this:

```
fetched=9 parsed=9 skipped=0 inserted=8 duplicates=1
fetched=9 parsed=9 skipped=0 inserted=0 duplicates=9
```

## Error handling

| what goes wrong | what happens |
|---|---|
| No internet, DNS failure | logged as a network error, run exits with code 1 |
| OpenSky too slow | requests time out after 10 seconds instead of hanging |
| Expired or rejected token (401) | fetch a new token and retry once |
| Rate limit (429) | log how long OpenSky says to wait, then exit. The next cron run tries again a minute later |
| Other HTTP errors (5xx and so on) | logged with the status code, exit 1 |
| Database down | logged, exit 1. Connecting gives up after 10 seconds |
| No aircraft in the box (`states` is null) | nothing to insert, the run still finishes normally |
| Missing aircraft ID, time or coordinates | that row is skipped and counted as `skipped` |
| Missing callsign, altitude, speed or heading | the row is kept and those columns are NULL |
| Missing setting in `.env` | the program stops at startup and names the variable |

Each run fetches a fresh token. Tokens last about 30 minutes and a run takes about a second, so expiry is really only a problem if OpenSky rejects a token early. The 401 retry covers that case.

## Logs

- `logs/pipeline.log` gets one block per run, with the summary line or the error.
- `logs/cron.log` gets everything cron sees, including crashes that happen before logging starts.

Both are gitignored.

## Checking the data

Make sure cron really runs every minute. Each hour should show close to 60:

```bash
grep "run finished" logs/pipeline.log | cut -c1-13 | uniq -c
```

Look for errors and warnings (0 means none):

```bash
grep -cE " (ERROR|WARNING) " logs/pipeline.log
```
