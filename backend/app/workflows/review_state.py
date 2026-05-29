from typing import TypedDict

from app.schemas.github import ParsedPullRequest, PullRequestSnapshot
from app.schemas.review import ReviewReport, ReviewSuggestion, ReviewSummary, RiskFinding


class ReviewGraphState(TypedDict, total=False):
    task_id: str
    url: str
    mode: str
    parsed_pr: ParsedPullRequest
    pr_snapshot: PullRequestSnapshot
    summary: ReviewSummary
    findings: list[RiskFinding]
    suggestions: list[ReviewSuggestion]
    test_recommendations: list[str]
    report: ReviewReport
    error_message: str
