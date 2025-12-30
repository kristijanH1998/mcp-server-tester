import pytest

pytestmark = pytest.mark.asyncio

async def test_register_server(client):
    resp = await client.post(
        "/servers",
        json={"url": "http://127.0.0.1:8001"}
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert "url" in data

    servers = await client.get("/servers")
    assert len(servers.json()) == 2
