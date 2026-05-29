from httpx import ASGITransport, AsyncClient

from app.main import create_app


async def test_health_endpoint():
    """验证 /api/health 返回 {"status": "ok"}"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_version_endpoint():
    """验证 /api/version 返回应用名称、版本号和环境"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "CodePilot Review"
    assert "version" in data
    assert data["env"] == "development"
