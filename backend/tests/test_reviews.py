from httpx import ASGITransport, AsyncClient

from app.main import create_app


async def test_create_review_task_with_valid_url():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/reviews",
            json={"url": "https://github.com/acme/codepilot/pull/12", "mode": "demo"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "succeeded"


async def test_get_review_report():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/api/reviews",
            json={"url": "https://github.com/acme/codepilot/pull/12", "mode": "demo"},
        )
        task_id = create_resp.json()["task_id"]

        get_resp = await client.get(f"/api/reviews/{task_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["task_id"] == task_id
    assert data["status"] == "succeeded"
    assert data["pr"]["title"] == "Add async review task creation"
    assert len(data["findings"]) > 0
    assert len(data["suggestions"]) > 0
    assert len(data["test_recommendations"]) > 0


async def test_get_review_not_found():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/reviews/nonexistent")
    assert response.status_code == 404


async def test_create_review_with_invalid_url():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/reviews",
            json={"url": "not-a-valid-url", "mode": "demo"},
        )
    assert response.status_code == 422
