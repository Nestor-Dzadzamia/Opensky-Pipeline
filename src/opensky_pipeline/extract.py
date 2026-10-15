from httpx2 import AsyncClient
from opensky_pipeline.config import Config

async def fetch_data(client: AsyncClient, token: str, config: Config) -> dict:
    response = await client.get(
        config.STATES_URL,
        params=config.GEORGIAN_AIRPORT_COORDINATES.model_dump(),
        headers={"Authorization": f"Bearer {token}"},
    )

    response.raise_for_status()
    return response.json()