import httpx

from app.core.config import settings
from app.core.logger import logger
from app.providers.errors import (
    GitHubNotFoundError,
    GitHubProviderError,
    GitHubRateLimitError,
    GitHubUnauthorizedError,
)
from app.schemas.github import ParsedPullRequest, PullRequestFile, PullRequestSnapshot

GITHUB_API_BASE = "https://api.github.com"


class GitHubProvider:
    """真实 GitHub API Provider

    调用 GitHub REST API 获取 PR 元数据、变更文件和 diff。
    支持公开仓库（无需 Token）和私有仓库（需配置 Token）。
    """

    def __init__(self, token: str | None = None, timeout_seconds: int = 30):
        self._token = token or settings.github_token or None
        self._timeout = timeout_seconds
        headers: dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodePilot-Review",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        self._client = httpx.AsyncClient(
            base_url=GITHUB_API_BASE,
            headers=headers,
            timeout=httpx.Timeout(timeout_seconds),
        )

    async def get_pull_request(self, ref: ParsedPullRequest) -> PullRequestSnapshot:
        """获取 PR 完整快照：元数据 + diff + 文件列表"""
        owner, repo, number = ref.owner, ref.repo, ref.number
        logger.info("GitHub API 获取 PR | owner={} repo={} number={}", owner, repo, number)

        try:
            pr_data, files_data, commits_data = await self._fetch_pr_data(owner, repo, number)
        except GitHubProviderError:
            raise
        except Exception as e:
            logger.error("GitHub API 请求异常 | error={}", str(e))
            raise GitHubProviderError(f"GitHub API request failed: {e}") from e

        return self._to_snapshot(pr_data, files_data, commits_data)

    async def close(self):
        """关闭 HTTP 客户端"""
        await self._client.aclose()

    async def _fetch_pr_data(self, owner: str, repo: str, number: int):
        """并发请求 PR 三个接口"""
        async def get(path: str) -> dict:
            response = await self._client.get(path)
            return self._handle_response(response)

        import asyncio
        pr_data, files_data, commits_data = await asyncio.gather(
            get(f"/repos/{owner}/{repo}/pulls/{number}"),
            get(f"/repos/{owner}/{repo}/pulls/{number}/files"),
            get(f"/repos/{owner}/{repo}/pulls/{number}/commits"),
        )
        return pr_data, files_data, commits_data

    def _handle_response(self, response: httpx.Response) -> dict:
        """统一处理 HTTP 响应和错误状态码"""
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            raise GitHubNotFoundError(
                f"Pull request not found. Check the URL and try again."
            )
        if response.status_code in (401, 403):
            if "rate limit" in response.text.lower():
                raise GitHubRateLimitError(
                    "GitHub API rate limit exceeded. Please configure a GITHUB_TOKEN or try later."
                )
            raise GitHubUnauthorizedError(
                "Access denied. The repository may be private. Please configure a valid GITHUB_TOKEN."
            )
        raise GitHubProviderError(
            f"GitHub API returned status {response.status_code}: {response.text[:200]}"
        )

    def _to_snapshot(
        self,
        pr_data: dict,
        files_data: list[dict],
        commits_data: list[dict],
    ) -> PullRequestSnapshot:
        """将 GitHub API JSON 转换为内部 PullRequestSnapshot 模型

        owner/repo 取自 base.repo（目标仓库），而非 head.repo。
        这样 fork PR 也能正确返回目标仓库而非 fork 仓库。
        """
        files = [
            PullRequestFile(
                path=f.get("filename", ""),
                status=f.get("status", "unknown"),
                additions=f.get("additions", 0),
                deletions=f.get("deletions", 0),
                patch=f.get("patch"),
            )
            for f in files_data
        ]

        total_additions = sum(f.additions for f in files)
        total_deletions = sum(f.deletions for f in files)

        head = pr_data.get("head", {})
        base = pr_data.get("base", {})
        user = pr_data.get("user", {})

        # 使用 base.repo 而非 head.repo：fork PR 时 head 指向 fork 仓库，
        # base 才是 URL 中的目标仓库
        base_repo = base.get("repo", {})

        return PullRequestSnapshot(
            owner=base_repo.get("owner", {}).get("login", ""),
            repo=base_repo.get("name", ""),
            number=pr_data.get("number", 0),
            title=pr_data.get("title", ""),
            author=user.get("login", "unknown"),
            base_branch=base.get("ref", ""),
            head_branch=head.get("ref", ""),
            changed_files=pr_data.get("changed_files", len(files)),
            additions=pr_data.get("additions", total_additions),
            deletions=pr_data.get("deletions", total_deletions),
            commit_count=pr_data.get("commits", len(commits_data)),
            files=files,
        )

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str = "main") -> str | None:
        """获取指定文件的原始内容（为 Context Collector 预留）"""
        try:
            response = await self._client.get(
                f"/repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref},
            )
            if response.status_code == 200:
                import base64
                data = response.json()
                content = data.get("content", "")
                return base64.b64decode(content).decode("utf-8", errors="replace")
            return None
        except Exception:
            return None
