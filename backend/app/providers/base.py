from typing import Protocol

from app.schemas.github import ParsedPullRequest, PullRequestSnapshot


class PullRequestProvider(Protocol):
    """GitHub Provider 抽象接口

    第 1 天使用 MockGitHubProvider 实现，第 2 天用真实 GitHub API 替换。
    通过依赖注入传入 review_graph builder，实现无感切换。
    """
    async def get_pull_request(self, ref: ParsedPullRequest) -> PullRequestSnapshot:
        """根据 PR 标识获取 PR 快照（元数据 + diff + 文件列表）"""
        ...
