from typing import Literal

from pydantic import BaseModel

from app.schemas.common import RiskCategory, RiskSeverity, TaskStatus
from app.schemas.github import ParsedPullRequest, PullRequestSnapshot


class ParsePullRequestRequest(BaseModel):
    url: str


class CreateReviewTaskRequest(BaseModel):
    url: str
    mode: Literal["demo", "github"] = "demo"


class CreateReviewTaskResponse(BaseModel):
    task_id: str
    status: TaskStatus


class ReviewSummary(BaseModel):
    overview: str
    changed_modules: list[str]
    reviewer_focus: list[str]


class RiskFinding(BaseModel):
    id: str
    severity: RiskSeverity
    category: RiskCategory
    file_path: str
    line: int | None = None
    title: str
    evidence: str
    reasoning: str
    confidence: float


class ReviewSuggestion(BaseModel):
    id: str
    finding_id: str | None = None
    file_path: str | None = None
    comment: str
    rationale: str
    suggested_fix: str
    blocking: bool


class ReviewReport(BaseModel):
    task_id: str
    status: TaskStatus
    pr: PullRequestSnapshot | None = None
    summary: ReviewSummary | None = None
    findings: list[RiskFinding] = []
    suggestions: list[ReviewSuggestion] = []
    test_recommendations: list[str] = []
    error_message: str | None = None
