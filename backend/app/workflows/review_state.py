from typing import TypedDict

from app.context.models import ReviewContext
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
    # fetch_pr 节点输出（Mock 或 GitHub Provider）
    pr_snapshot: PullRequestSnapshot
    # collect_context 节点输出
    review_context: ReviewContext
    # generate_summary 节点输出
    summary: ReviewSummary
    # detect_risks 节点输出
    findings: list[RiskFinding]
    # generate_suggestions 节点输出
    suggestions: list[ReviewSuggestion]
    test_recommendations: list[str]
    # 进度事件和警告
    warnings: list[str]
    provider_name: str | None
    model_name: str | None
    # assemble_report 节点输出
    report: ReviewReport
    # 错误短路：任意节点设置后，后续节点跳过执行
    error_message: str
