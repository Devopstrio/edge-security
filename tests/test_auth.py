import pytest
from httpx import ASGITransport, AsyncClient

from edgesecurity.database import init_db
from edgesecurity.main import app


@pytest.fixture(autouse=True)
async def setup_db() -> None:
    await init_db()
    
    # Seed a test node
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/api/v1/_internal/seed-node", params={"node_id": "test-node-1", "raw_secret": "test-secret-123"})

@pytest.mark.asyncio
async def test_issue_token_success() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/token", json={
            "node_id": "test-node-1",
            "hardware_secret": "test-secret-123"
        })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_issue_token_failure() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/token", json={
            "node_id": "test-node-1",
            "hardware_secret": "wrong-secret"
        })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_verify_token() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Get token
        token_resp = await ac.post("/api/v1/auth/token", json={
            "node_id": "test-node-1",
            "hardware_secret": "test-secret-123"
        })
        token = token_resp.json()["access_token"]
        
        # 2. Verify token
        verify_resp = await ac.post("/api/v1/auth/verify", json={"token": token})
        
    assert verify_resp.status_code == 200
    assert verify_resp.json()["is_valid"] is True
    assert verify_resp.json()["node_id"] == "test-node-1"

@pytest.mark.asyncio
async def test_generate_api_key() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/keys/generate", json={
            "service_name": "fleet-api",
            "role": "admin"
        })
    assert response.status_code == 200
    assert "api_key" in response.json()
    assert len(response.json()["api_key"]) > 20
