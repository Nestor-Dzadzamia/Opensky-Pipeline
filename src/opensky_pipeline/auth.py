from httpx2 import AsyncClient

from opensky_pipeline.config import Config


def get_opensky_client(config: Config) -> AsyncClient:
    return AsyncClient(timeout=config.REQUEST_TIMEOUT)

async def get_token(client: AsyncClient, config: Config) -> str:
    response = await client.post(
        config.TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": config.OPENSKY_CLIENT_ID,
            "client_secret": config.OPENSKY_CLIENT_SECRET.get_secret_value(),
        },
    )
    response.raise_for_status()
    token = response.json()["access_token"]

    return token
