from pydantic import BaseModel, HttpUrl


class ParsedPullRequest(BaseModel):
    owner: str
    repo: str
    number: int
    url: HttpUrl


class PullRequestFile(BaseModel):
    path: str
    status: str
    additions: int
    deletions: int
    patch: str | None = None


class PullRequestSnapshot(BaseModel):
    owner: str
    repo: str
    number: int
    title: str
    author: str
    base_branch: str
    head_branch: str
    changed_files: int
    additions: int
    deletions: int
    commit_count: int
    files: list[PullRequestFile]
