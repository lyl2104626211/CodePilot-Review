from typing import Literal

from pydantic import BaseModel

from app.schemas.common import RiskCategory, RiskSeverity, TaskStatus
from app.schemas.github import ParsedPullRequest, PullRequestSnapshot


class ParsePullRequestRequest(BaseModel):
    """PR URL 解析请求"""
    url: str


class CreateReviewTaskRequest(BaseModel):
    """创建 Review 任务请求"""
    url: str
    mode: Literal["demo", "github"] = "demo"  # demo 模式用 Mock 数据，github 模式走真实 API


class CreateReviewTaskResponse(BaseModel):
    """创建 Review 任务响应"""
    task_id: str
    status: TaskStatus


class ReviewSummary(BaseModel):
    """PR 变更总结"""
    overview: str                    # 总览描述
    changed_modules: list[str]       # 涉及的模块列表
    reviewer_focus: list[str]        # 评审者需要重点关注的事项


class RiskFinding(BaseModel):
    """单条风险发现"""
    id: str                          # 唯一标识
    severity: RiskSeverity           # 严重程度
    category: RiskCategory           # 风险类别
    file_path: str                   # 风险所在文件
    line: int | None = None          # 风险所在行号
    title: str                       # 风险标题
    evidence: str                    # 代码证据
    reasoning: str                   # 分析推理
    confidence: float                # 置信度 0-1


class ReviewSuggestion(BaseModel):
    """单条 Review 建议"""
    id: str                          # 唯一标识
    finding_id: str | None = None    # 关联的风险发现 ID
    file_path: str | None = None     # 建议对应的文件路径
    comment: str                     # 评论正文
    rationale: str                   # 建议理由
    suggested_fix: str               # 建议的修复方式
    blocking: bool                   # 是否阻塞合并


class ReviewReport(BaseModel):
    """完整的 Review 报告"""
    task_id: str
    status: TaskStatus
    # 失败时 pr 和 summary 为 None，所以允许空值
    pr: PullRequestSnapshot | None = None
    summary: ReviewSummary | None = None
    findings: list[RiskFinding] = []
    suggestions: list[ReviewSuggestion] = []
    test_recommendations: list[str] = []
    warnings: list[str] = []
    error_message: str | None = None


# ===== Day 3: 模拟评论与质量摘要模型 =====


class ReviewCommentDraft(BaseModel):
    """单条模拟 Review 评论草稿"""
    id: str                          # comment_001
    suggestion_id: str               # 关联的 suggestion
    finding_id: str | None = None    # 关联的 risk finding
    file_path: str | None = None     # 文件路径（模拟 inline comment 位置）
    line: int | None = None          # 行号
    body: str                        # 完整评论正文（Markdown）
    severity: RiskSeverity | None = None
    blocking: bool = False


class CreateReviewCommentsRequest(BaseModel):
    """生成模拟评论请求"""
    suggestion_ids: list[str]
    include_summary: bool = True
    include_test_recommendations: bool = True


class CreateReviewCommentsResponse(BaseModel):
    """生成模拟评论响应"""
    task_id: str
    comments: list[ReviewCommentDraft]
    markdown: str                    # 完整 Review Markdown


class ReviewTaskStatus(BaseModel):
    """任务状态信息"""
    task_id: str
    status: TaskStatus
    progress_events: list[dict] = []
    warnings: list[str] = []


class ReportQualitySummary(BaseModel):
    """报告质量摘要"""
    total_findings: int
    high_confidence_findings: int    # confidence >= 0.7
    low_confidence_findings: int     # confidence < 0.5
    blocking_suggestions: int
    warning_count: int
    fallback_used: bool
    notes: list[str]
