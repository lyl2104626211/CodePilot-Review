from httpx import ASGITransport, AsyncClient

from app.main import create_app


async def test_create_review_task_with_valid_url():
    """验证合法 URL 能成功创建 Review 任务并返回 succeeded 状态"""
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
    """验证创建任务后能查询到完整的 Mock ReviewReport"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 先创建任务
        create_resp = await client.post(
            "/api/reviews",
            json={"url": "https://github.com/acme/codepilot/pull/12", "mode": "demo"},
        )
        task_id = create_resp.json()["task_id"]

        # 再查询报告
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
    """验证查询不存在的 task_id 返回 404"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/reviews/nonexistent")
    assert response.status_code == 404


async def test_create_review_with_invalid_url():
    """验证非法 URL 创建任务时返回 422"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/reviews",
            json={"url": "not-a-valid-url", "mode": "demo"},
        )
    assert response.status_code == 422


async def test_create_review_github_mode_returns_failed():
    """验证 GitHub 模式暂未接入时返回 failed 状态和明确提示"""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/reviews",
            json={"url": "https://github.com/acme/codepilot/pull/12", "mode": "github"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"

        # 查询报告确认 error_message 存在
        task_id = data["task_id"]
        get_resp = await client.get(f"/api/reviews/{task_id}")
        report = get_resp.json()
        assert report["status"] == "failed"
        assert "github" in report["error_message"].lower()
