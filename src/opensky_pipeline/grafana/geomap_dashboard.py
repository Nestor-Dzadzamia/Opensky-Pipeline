import json
from httpx2 import AsyncClient
from opensky_pipeline.config import Config

async def create_dashboard(config: Config, client: AsyncClient) -> str:
    dashboard = json.loads(config.DASHBOARD_FILE.read_text(encoding="utf-8"))
    name = dashboard["metadata"]["name"]
    grafana_url = config.GRAFANA_URL.rstrip("/")
    base_url = f"{grafana_url}{config.DASHBOARDS_PATH}"
    headers = {"Authorization": f"Bearer {config.GRAFANA_TOKEN.get_secret_value()}"}

    existing = await client.get(f"{base_url}/{name}", headers=headers)
    if existing.status_code == 404:
        response = await client.post(base_url, json=dashboard, headers=headers)
    else:
        existing.raise_for_status()
        dashboard["metadata"]["resourceVersion"] = existing.json()["metadata"]["resourceVersion"]
        response = await client.put(f"{base_url}/{name}", json=dashboard, headers=headers)

    response.raise_for_status()
    return f"{grafana_url}/d/{name}"

