import asyncio
import json

from opensky_pipeline.auth import get_opensky_client, get_token
from opensky_pipeline.config import Config
from opensky_pipeline.extract import fetch_data
from opensky_pipeline.transform import parse_states


async def main():
    config = Config()
    client = get_opensky_client(config)
    token = await get_token(client, config)
    response = await fetch_data(client, token, config)
    parse_states(response)

    print(json.dumps(response, indent=4))

if __name__ == '__main__':
    asyncio.run(main())
