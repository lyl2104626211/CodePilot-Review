from typing import TypedDict

from app.schemas.github import ParsedPullRequest, PullRequestSnapshot
from app.schemas.review import ReviewReport, ReviewSuggestion, ReviewSummary, RiskFinding


class ReviewGraphState(TypedDict, total=False):
    """LangGraph 工作流的状态类型

    节点间通过此 TypedDict 传递数据。total=False 表示所有字段可选，
    各节点按需填充对应字段，未填充的字段访问时为 undefined。
    """
    task_id: str
    url: str
    mode: str
    # parse_pr_url 节点输出
    parsed_pr: ParsedPullRequest
    # fetch_mock_pr / fetch_github_pr 节点输出
    pr_snapshot: PullRequestSnapshot
    # generate_mock_review / LLM 节点输出
    summary: ReviewSummary
    findings: list[RiskFinding]
    suggestions: list[ReviewSuggestion]
    test_recommendations: list[str]
    # assemble_report 节点输出
    report: ReviewReport
    # 错误短路：任意节点设置后，后续节点跳过执行
    error_message: str
