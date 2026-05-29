"""GitHub Provider 异常类型"""


class GitHubProviderError(Exception):
    """GitHub API 调用异常基类"""
    pass


class GitHubNotFoundError(GitHubProviderError):
    """PR 或仓库不存在 (HTTP 404)"""
    pass


class GitHubUnauthorizedError(GitHubProviderError):
    """Token 无效或无权限访问 (HTTP 401/403)"""
    pass


class GitHubRateLimitError(GitHubProviderError):
    """API 限流 (HTTP 403 + rate limit)"""
    pass
