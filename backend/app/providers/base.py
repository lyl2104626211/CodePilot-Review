from typing import Protocol

from app.schemas.github import ParsedPullRequest, PullRequestSnapshot


class PullRequestProvider(Protocol):
    async def get_pull_request(self, ref: ParsedPullRequest) -> PullRequestSnapshot:
        ...
