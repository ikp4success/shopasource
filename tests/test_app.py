import os

import pytest

# Ensure config picks up test API key before app imports
os.environ.setdefault("API_KEY", "testkey")
os.environ.setdefault("ENV_CONFIGURATION", "debug")
os.environ.setdefault("DB_USER", "admin")
os.environ.setdefault("DB_PASS", "admin")
os.environ.setdefault("DB_DOMAIN", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "shopasource")

from support import config as support_config
from webapp.app import app


@pytest.mark.asyncio
async def test_health():
    client = app.test_client()
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = await resp.get_json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_openapi():
    client = app.test_client()
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    data = await resp.get_json()
    assert "openapi" in data


@pytest.mark.asyncio
async def test_get_result_missing_job_id():
    client = app.test_client()
    headers = {"X-API-Key": support_config.API_KEY}
    resp = await client.get("/api/get_result", headers=headers)
    assert resp.status_code == 400
    data = await resp.get_json()
    assert data["status"] == "missing_parameter"
