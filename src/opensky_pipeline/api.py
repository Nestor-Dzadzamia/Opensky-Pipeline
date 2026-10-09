from httpx2 import AsyncClient
from opensky_pipeline import config

async def fetch_data(client: AsyncClient, token: str) -> dict:
    response = await client.get(
        config.STATES_URL,
        params=config.GEORGIAN_AIRPORT_COORDINATES,
        headers={"Authorization": f"Bearer {token}"},
    )

    response.raise_for_status()
    return response.json()
