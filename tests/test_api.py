import pytest


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "mongo" in data
    assert "qdrant" in data
    assert "cache" in data
    assert data["qdrant"]["connected"] is True


@pytest.mark.asyncio
async def test_recommend_endpoint(async_client):
    response = await async_client.post(
        "/api/recommend",
        json={"query": "moisturizer for dry skin under 800", "top_k": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["input_type"] == "text"
    assert len(data["recommendations"]) == 5
    assert data["latency_ms"] > 0
