import re
from urllib.parse import urlparse

from app.schemas.github import ParsedPullRequest

GITHUB_PR_PATTERN = re.compile(r"^/[\w.-]+/[\w.-]+/pull/(\d+)/?$")


class PRParseError(ValueError):
    pass


def parse_github_pr_url(url: str) -> ParsedPullRequest:
    parsed = urlparse(url)

    if parsed.hostname != "github.com":
        raise PRParseError("Only GitHub pull request URLs are supported.")

    match = GITHUB_PR_PATTERN.match(parsed.path)
    if not match:
        raise PRParseError(
            "Invalid GitHub PR URL. Expected format: https://github.com/{owner}/{repo}/pull/{number}"
        )

    path_parts = parsed.path.strip("/").split("/")
    owner = path_parts[0]
    repo = path_parts[1]
    number = int(match.group(1))

    if number <= 0:
        raise PRParseError("Pull request number must be a positive integer.")

    return ParsedPullRequest(
        owner=owner,
        repo=repo,
        number=number,
        url=url,  # type: ignore[arg-type]
    )
