import asyncio
import logging
import sys
from pathlib import Path

import psycopg
from httpx2 import AsyncClient, HTTPStatusError, RequestError

from opensky_pipeline.api import fetch_data
from opensky_pipeline.auth import get_opensky_client, get_token
from opensky_pipeline.db import insert_data
from opensky_pipeline.parser import parse_states

LOG_FILE = Path(__file__).resolve().parents[2] / "logs" / "pipeline.log"

logger = logging.getLogger("opensky_pipeline")


def setup_logging_config() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
    )


async def fetch_with_token_retry(client: AsyncClient) -> dict:
    token = await get_token(client)
    try:
        return await fetch_data(client, token)
    except HTTPStatusError as e:
        if e.response.status_code == 401:
            logger.warning(
                "token rejected (401 status code), fetching a new one and retrying once"
            )
            token = await get_token(client)
            return await fetch_data(client, token)
        raise


async def run() -> None:
    async with get_opensky_client() as client:
        response_json = await fetch_with_token_retry(client)

    rows, skipped = parse_states(response_json)
    inserted = insert_data(rows)
    logger.info(
        "fetched=%d parsed=%d skipped=%d inserted=%d duplicates=%d",
        len(response_json.get("states") or []),
        len(rows),
        skipped,
        inserted,
        len(rows) - inserted,
    )


def main() -> None:
    setup_logging_config()
    logger.info("run started")
    try:
        asyncio.run(run())
    except HTTPStatusError as e:
        status = e.response.status_code
        if status == 429:
            retry_after = e.response.headers.get("X-Rate-Limit-Retry-After-Seconds", "unknown")
            logger.warning("Rate limited (429), retry after %s seconds", retry_after)
        else:
            logger.error("OpenSky returned HTTP %d for %s", status, e.request.url)
        sys.exit(1)
    except RequestError as e:
        logger.error("network error calling OpenSky: %r", e)
        sys.exit(1)
    except psycopg.OperationalError as e:
        logger.error("database error: %s", e)
        sys.exit(1)
    except Exception:
        logger.exception("unexpected error")
        sys.exit(1)
    logger.info("run finished")