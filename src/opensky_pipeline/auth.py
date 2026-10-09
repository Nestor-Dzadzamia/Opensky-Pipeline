from httpx2 import AsyncClient
from opensky_pipeline import config

def get_opensky_client() -> AsyncClient:
    return AsyncClient(timeout=config.REQUEST_TIMEOUT)

async def get_token(client: AsyncClient) -> str:
    response = await client.post(
        config.TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": config.OPENSKY_CLIENT_ID,
            "client_secret": config.OPENSKY_CLIENT_SECRET,
        },
    )
    response.raise_for_status()
    token = response.json()["access_token"]

    return token
