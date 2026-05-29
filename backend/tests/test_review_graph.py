"""LangGraph Review 工作流直接测试"""
import pytest

from app.providers.mock_github import MockGitHubProvider
from app.schemas.common import TaskStatus
from app.workflows.review_graph import build_review_graph


@pytest.fixture
def provider():
    """创建 Mock Provider 供工作流使用"""
    return MockGitHubProvider()


@pytest.fixture
def graph(provider):
    """构建编译后的工作流"""
    return build_review_graph(provider)


@pytest.mark.asyncio
async def test_demo_workflow_succeeds(graph):
    """验证 Demo 模式下合法 URL 能产出成功报告"""
    state = {
        "task_id": "test_task_001",
        "url": "https://github.com/acme/codepilot/pull/12",
        "mode": "demo",
    }
    result = await graph.ainvoke(state)

    assert "error_message" not in result or result["error_message"] is None
    assert "report" in result
    report = result["report"]
    assert report.status == TaskStatus.succeeded
    assert report.pr is not None
    assert report.pr.title == "Add async review task creation"
    assert report.summary is not None
    assert len(report.summary.overview) > 0
    assert len(report.findings) == 1
    assert len(report.suggestions) == 1
    assert len(report.test_recommendations) == 3


@pytest.mark.asyncio
async def test_invalid_url_fails(graph):
    """验证非法 URL 不会产出 succeeded 报告，且包含 error_message"""
    state = {
        "task_id": "test_task_002",
        "url": "not-a-valid-url",
        "mode": "demo",
    }
    result = await graph.ainvoke(state)

    assert result.get("error_message") is not None
    # 应该没有生成 report
    assert "report" not in result or result["report"] is None


@pytest.mark.asyncio
async def test_non_github_url_fails(graph):
    """验证非 GitHub 域名返回错误"""
    state = {
        "task_id": "test_task_003",
        "url": "https://gitlab.com/acme/codepilot/pull/12",
        "mode": "demo",
    }
    result = await graph.ainvoke(state)

    assert result.get("error_message") is not None
    assert "GitHub" in result["error_message"]


@pytest.mark.asyncio
async def test_workflow_includes_pr_metadata(graph):
    """验证工作流产出的 report 包含正确的 PR 元数据"""
    state = {
        "task_id": "test_task_004",
        "url": "https://github.com/acme/codepilot/pull/42",
        "mode": "demo",
    }
    result = await graph.ainvoke(state)

    report = result["report"]
    pr = report.pr
    assert pr.owner == "acme"
    assert pr.repo == "codepilot"
    assert pr.number == 42
    assert pr.changed_files == 3
    assert pr.additions == 128
    assert pr.deletions == 24
