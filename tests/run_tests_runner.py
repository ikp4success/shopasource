import asyncio
import os

os.environ.setdefault("API_KEY", "testkey")
os.environ.setdefault("ENV_CONFIGURATION", "debug")
os.environ.setdefault("DB_USER", "admin")
os.environ.setdefault("DB_PASS", "admin")
os.environ.setdefault("DB_DOMAIN", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "shopasource")

import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from support import config as support_config
from webapp.app import app


async def run_checks():
    client = app.test_client()

    resp = await client.get("/health")
    print("/health status:", resp.status_code)
    data = await resp.get_json()
    print("/health json:", data)

    resp = await client.get("/openapi.json")
    print("/openapi.json status:", resp.status_code)
    data = await resp.get_json()
    print("/openapi.json keys:", list(data.keys()))

    resp = await client.get(
        "/api/get_result", headers={"X-API-Key": support_config.API_KEY}
    )
    print("/api/get_result status:", resp.status_code)
    data = await resp.get_json()
    print("/api/get_result json:", data)


if __name__ == "__main__":
    asyncio.run(run_checks())
