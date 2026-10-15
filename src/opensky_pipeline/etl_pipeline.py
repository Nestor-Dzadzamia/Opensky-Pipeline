from opensky_pipeline.auth import get_opensky_client, get_token
from opensky_pipeline.config import Config
from opensky_pipeline.extract import fetch_data
from opensky_pipeline.load import DatabaseManager
from opensky_pipeline.util.logger import logger
from opensky_pipeline.transform import parse_states


async def etl_pipeline():
    config = Config()
    db_manager = DatabaseManager(config)

    async with get_opensky_client(config) as client:
        token = await get_token(client, config)
        response_json = await fetch_data(client, token, config)

    rows, skipped = parse_states(response_json)

    inserted = db_manager.insert_data(rows)
    logger.info(
        "fetched=%d parsed=%d skipped=%d inserted=%d duplicates=%d",
        len(response_json.get("states") or []),
        len(rows),
        skipped,
        inserted,
        len(rows) - inserted,
        )