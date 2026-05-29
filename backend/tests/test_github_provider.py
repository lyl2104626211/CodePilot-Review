"""GitHubProvider 单元测试（mock GitHub API 响应）"""
import json

import httpx
import pytest

from app.providers.errors import (
    GitHubNotFoundError,
    GitHubRateLimitError,
    GitHubUnauthorizedError,
)
from app.providers.github import GitHubProvider
from app.schemas.github import ParsedPullRequest

# 模拟 GitHub API 返回的真实 JSON 结构
MOCK_PR_DATA = {
    "number": 12,
    "title": "Add async review task creation",
    "user": {"login": "demo-user"},
    "head": {
        "ref": "feature/review-task",
        "repo": {
            "name": "codepilot",
            "owner": {"login": "acme"},
        },
    },
    "base": {"ref": "main"},
    "changed_files": 3,
    "additions": 128,
    "deletions": 24,
    "commits": 4,
}

MOCK_FILES_DATA = [
    {
        "filename": "backend/app/api/reviews.py",
        "status": "added",
        "additions": 45,
        "deletions": 0,
        "patch": "@@ -0,0 +1,45 @@\n+@router.post('/reviews')\n+async def create_review(...)",
    },
    {
        "filename": "backend/app/services/review_service.py",
        "status": "modified",
        "additions": 63,
        "deletions": 12,
        "patch": "@@ -10,6 +10,57 @@\n+async def create_review_task(...)",
    },
]

MOCK_COMMITS_DATA = [{"sha": "abc123"}, {"sha": "def456"}, {"sha": "ghi789"}, {"sha": "jkl012"}]


def _make_mock_transport(status_map: dict[str, tuple[int, object]]):
    """构造 httpx.MockTransport，按 URL 路径精确匹配返回不同的 mock 响应"""

    async def handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        for path_suffix, (status, body) in status_map.items():
            if url_str.endswith(path_suffix):
                content = json.dumps(body).encode() if isinstance(body, (dict, list)) else str(body).encode()
                return httpx.Response(status, content=content, request=request)
        return httpx.Response(404, content=json.dumps({"message": "Not Found"}).encode(), request=request)

    return httpx.MockTransport(handler)


@pytest.fixture
def valid_pr_ref():
    return ParsedPullRequest(
        owner="acme",
        repo="codepilot",
        number=12,
        url="https://github.com/acme/codepilot/pull/12",  # type: ignore[arg-type]
    )


@pytest.mark.asyncio
async def test_fetch_pr_success(valid_pr_ref):
    """验证成功获取 PR 并转换为 PullRequestSnapshot"""
    status_map = {
        f"/repos/{valid_pr_ref.owner}/{valid_pr_ref.repo}/pulls/{valid_pr_ref.number}/files": (200, MOCK_FILES_DATA),
        f"/repos/{valid_pr_ref.owner}/{valid_pr_ref.repo}/pulls/{valid_pr_ref.number}/commits": (200, MOCK_COMMITS_DATA),
        f"/repos/{valid_pr_ref.owner}/{valid_pr_ref.repo}/pulls/{valid_pr_ref.number}": (200, MOCK_PR_DATA),
    }
    transport = _make_mock_transport(status_map)
    provider = GitHubProvider(timeout_seconds=5)
    provider._client = httpx.AsyncClient(transport=transport, base_url="https://api.github.com")

    snapshot = await provider.get_pull_request(valid_pr_ref)

    assert snapshot.owner == "acme"
    assert snapshot.repo == "codepilot"
    assert snapshot.number == 12
    assert snapshot.title == "Add async review task creation"
    assert snapshot.author == "demo-user"
    assert snapshot.base_branch == "main"
    assert snapshot.head_branch == "feature/review-task"
    assert snapshot.changed_files == 3
    assert snapshot.additions == 128
    assert snapshot.deletions == 24
    assert snapshot.commit_count == 4
    assert len(snapshot.files) == 2
    assert snapshot.files[0].path == "backend/app/api/reviews.py"
    assert snapshot.files[0].status == "added"
    assert snapshot.files[0].patch is not None

    await provider.close()


@pytest.mark.asyncio
async def test_fetch_pr_not_found(valid_pr_ref):
    """验证 PR 不存在时抛出 GitHubNotFoundError"""
    # 空 status_map 导致所有请求返回 404
    transport = _make_mock_transport({})
    provider = GitHubProvider(timeout_seconds=5)
    provider._client = httpx.AsyncClient(transport=transport, base_url="https://api.github.com")

    with pytest.raises(GitHubNotFoundError):
        await provider.get_pull_request(valid_pr_ref)

    await provider.close()


@pytest.mark.asyncio
async def test_fetch_pr_unauthorized(valid_pr_ref):
    """验证无权限时抛出 GitHubUnauthorizedError"""
    status_map = {
        f"/repos/{valid_pr_ref.owner}/{valid_pr_ref.repo}/pulls/{valid_pr_ref.number}": (401, {"message": "Bad credentials"}),
    }
    transport = _make_mock_transport(status_map)
    provider = GitHubProvider(timeout_seconds=5)
    provider._client = httpx.AsyncClient(transport=transport, base_url="https://api.github.com")

    with pytest.raises(GitHubUnauthorizedError):
        await provider.get_pull_request(valid_pr_ref)

    await provider.close()


@pytest.mark.asyncio
async def test_fetch_pr_rate_limit(valid_pr_ref):
    """验证限流时抛出 GitHubRateLimitError"""
    status_map = {
        f"/repos/{valid_pr_ref.owner}/{valid_pr_ref.repo}/pulls/{valid_pr_ref.number}": (403, {"message": "API rate limit exceeded"}),
    }
    transport = _make_mock_transport(status_map)
    provider = GitHubProvider(timeout_seconds=5)
    provider._client = httpx.AsyncClient(transport=transport, base_url="https://api.github.com")

    with pytest.raises(GitHubRateLimitError):
        await provider.get_pull_request(valid_pr_ref)

    await provider.close()


@pytest.mark.asyncio
async def test_patch_field_preserved(valid_pr_ref):
    """验证 patch、additions、deletions 字段正确保留"""
    status_map = {
        f"/repos/{valid_pr_ref.owner}/{valid_pr_ref.repo}/pulls/{valid_pr_ref.number}/files": (200, MOCK_FILES_DATA),
        f"/repos/{valid_pr_ref.owner}/{valid_pr_ref.repo}/pulls/{valid_pr_ref.number}/commits": (200, MOCK_COMMITS_DATA),
        f"/repos/{valid_pr_ref.owner}/{valid_pr_ref.repo}/pulls/{valid_pr_ref.number}": (200, MOCK_PR_DATA),
    }
    transport = _make_mock_transport(status_map)
    provider = GitHubProvider(timeout_seconds=5)
    provider._client = httpx.AsyncClient(transport=transport, base_url="https://api.github.com")

    snapshot = await provider.get_pull_request(valid_pr_ref)

    first_file = snapshot.files[0]
    assert first_file.additions == 45
    assert first_file.deletions == 0
    assert "reviews" in first_file.patch

    second_file = snapshot.files[1]
    assert second_file.additions == 63
    assert second_file.deletions == 12
    assert second_file.path == "backend/app/services/review_service.py"
    assert "create_review_task" in second_file.patch

    await provider.close()
