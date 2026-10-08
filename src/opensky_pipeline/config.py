import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def _require_env_variable(variable: str) -> str:
    value = os.environ.get(variable)
    if not value:
        raise ValueError(f"Missing environment variable:  {variable}")
    return value


OPENSKY_CLIENT_ID = _require_env_variable("OPENSKY_CLIENT_ID")
OPENSKY_CLIENT_SECRET = _require_env_variable("OPENSKY_CLIENT_SECRET")
TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
STATES_URL = "https://opensky-network.org/api/states/all"
REQUEST_TIMEOUT = 10

ISTANBUL_AIRPORT_COORDINATES = {"lamin": 40.27, "lomin": 27.73, "lamax": 42.27, "lomax": 29.73}

DB_HOST = _require_env_variable("DB_HOST")
DB_PORT = int(_require_env_variable("DB_PORT"))
DB_NAME = _require_env_variable("DB_NAME")
DB_USER = _require_env_variable("DB_USER")
DB_PASSWORD = _require_env_variable("DB_PASSWORD")