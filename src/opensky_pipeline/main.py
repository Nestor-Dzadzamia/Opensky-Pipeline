import asyncio
import sys

import psycopg2
from httpx2 import HTTPStatusError, RequestError

from opensky_pipeline.etl_pipeline import etl_pipeline
from opensky_pipeline.util.logger import logger
from opensky_pipeline.util.logger import setup_logging_config


def main():
    setup_logging_config()

    logger.info("run started")
    try:
        asyncio.run(etl_pipeline())
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
    except psycopg2.OperationalError as e:
        logger.error("database error: %s", e)
        sys.exit(1)
    except Exception:
        logger.exception("unexpected error")
        sys.exit(1)
    logger.info("run finished")
