import json
import os
import requests
from dotenv import load_dotenv, find_dotenv

def main() -> None:
    load_dotenv(find_dotenv())

    CLIENT_ID = os.environ.get("OPENSKY_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("OPENSKY_CLIENT_SECRET")

    response = requests.post(
        "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
    )


    response.raise_for_status()
    token = response.json()["access_token"]



    lat = 41.269269
    long = 28.731754

    lamin = lat - 1
    lamax = lat + 1
    lomin = long - 1
    lomax = long + 1

    data = requests.get(
        f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(json.dumps(data.json(), indent=4))

if __name__ == '__main__':

    main()