from pathlib import Path

import logging

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
