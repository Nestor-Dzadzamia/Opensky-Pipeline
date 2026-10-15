from pathlib import Path

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class CoordinateBox(BaseModel):
    lamin: float
    lomin: float
    lamax: float
    lomax: float

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= PROJECT_ROOT / '.env',
        env_ignore_empty=True,
        extra="ignore",
    )

    OPENSKY_CLIENT_ID: str
    OPENSKY_CLIENT_SECRET: SecretStr

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr

    TOKEN_URL: str = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
    STATES_URL: str = "https://opensky-network.org/api/states/all"
    REQUEST_TIMEOUT: int = 10

    GEORGIAN_AIRPORT_COORDINATES: CoordinateBox = CoordinateBox(
        lamin=40.67, lomin=43.95, lamax=42.67, lomax=45.95
    )