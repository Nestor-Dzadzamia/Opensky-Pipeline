from httpx2 import AsyncClient, HTTPStatusError, RequestError

from opensky_pipeline.auth import get_opensky_client, get_token
from opensky_pipeline.config import Config
from opensky_pipeline.extract import fetch_data
from opensky_pipeline.grafana.geomap_dashboard import create_dashboard
from opensky_pipeline.load import DatabaseManager
from opensky_pipeline.transform import parse_states
from opensky_pipeline.util.logger import logger


async def etl_pipeline(config: Config, client: AsyncClient):
    db_manager = DatabaseManager(config)

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


async def setup_dashboard(config: Config, client: AsyncClient):
    try:
        url = await create_dashboard(config, client)
        logger.info("dashboard ready: %s", url)
    except HTTPStatusError as e:
        logger.error("Grafana returned HTTP %d: %s", e.response.status_code, e.response.text)
    except RequestError as e:
        logger.error("network error calling Grafana: %r", e)


async def run_etl_create_dashboard():
    config = Config()
    async with get_opensky_client(config) as client:
        await etl_pipeline(config, client)
        await setup_dashboard(config, client)