import re
from urllib.parse import urlparse

from app.core.logger import logger
from app.schemas.github import ParsedPullRequest

# 匹配 GitHub PR URL 路径：/owner/repo/pull/number
GITHUB_PR_PATTERN = re.compile(r"^/[\w.-]+/[\w.-]+/pull/(\d+)/?$")


class PRParseError(ValueError):
    """PR URL 解析错误"""
    pass


def parse_github_pr_url(url: str) -> ParsedPullRequest:
    """解析 GitHub PR URL，提取 owner、repo、PR number

    Args:
        url: 完整的 GitHub PR URL，如 https://github.com/acme/codepilot/pull/12

    Returns:
        ParsedPullRequest: 包含 owner, repo, number, url

    Raises:
        PRParseError: URL 格式不合法时抛出
    """
    logger.debug("开始解析 PR URL | url={}", url)
    parsed = urlparse(url)

    # 只允许 GitHub 域名
    if parsed.hostname != "github.com":
        logger.warning("非 GitHub 域名被拒绝 | hostname={} url={}", parsed.hostname, url)
        raise PRParseError("Only GitHub pull request URLs are supported.")

    # 正则匹配 /owner/repo/pull/number 格式
    match = GITHUB_PR_PATTERN.match(parsed.path)
    if not match:
        logger.warning("PR URL 路径格式不匹配 | path={} url={}", parsed.path, url)
        raise PRParseError(
            "Invalid GitHub PR URL. Expected format: https://github.com/{owner}/{repo}/pull/{number}"
        )

    # 从路径中提取 owner 和 repo（正则已验证结构，拆解安全）
    path_parts = parsed.path.strip("/").split("/")
    owner = path_parts[0]
    repo = path_parts[1]
    number = int(match.group(1))

    # 安全守卫：理论上正则 \d+ 不会匹配到 0 或负数，但保留此检查防止极端情况
    if number <= 0:
        logger.error("PR 编号异常为非正数 | number={} url={}", number, url)
        raise PRParseError("Pull request number must be a positive integer.")

    result = ParsedPullRequest(
        owner=owner,
        repo=repo,
        number=number,
        url=url,  # type: ignore[arg-type]  # Pydantic 自动将 str 转为 HttpUrl
    )
    logger.debug("PR URL 解析完成 | owner={} repo={} number={}", owner, repo, number)
    return result
