from fastapi import APIRouter, HTTPException

from app.core.logger import logger
from app.schemas.github import ParsedPullRequest
from app.schemas.review import (
    CreateReviewCommentsRequest,
    CreateReviewCommentsResponse,
    CreateReviewTaskRequest,
    CreateReviewTaskResponse,
    ParsePullRequestRequest,
    ReviewReport,
    ReviewTaskStatus,
)
from app.services.pr_parser import PRParseError, parse_github_pr_url
from app.services.review_comment_service import (
    CommentServiceError,
    create_review_comment_drafts,
    get_report_quality,
)
from app.services.review_service import create_review_task, get_review_result, store

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/parse", response_model=ParsedPullRequest)
async def parse_pr_url(request: ParsePullRequestRequest):
    """解析 GitHub PR URL，返回 owner、repo、number 等元数据"""
    logger.info("收到 PR URL 解析请求 | url={}", request.url)
    try:
        result = parse_github_pr_url(request.url)
        logger.debug("PR URL 解析成功 | owner={} repo={} number={}", result.owner, result.repo, result.number)
        return result
    except PRParseError as e:
        logger.warning("PR URL 解析失败 | url={} error={}", request.url, str(e))
        raise HTTPException(status_code=422, detail=str(e))


@router.post("", response_model=CreateReviewTaskResponse)
async def create_review(request: CreateReviewTaskRequest):
    """创建 Review 任务：先校验 URL 格式，再通过 LangGraph 工作流执行分析"""
    logger.info("收到 Review 任务创建请求 | url={} mode={}", request.url, request.mode)
    try:
        parse_github_pr_url(request.url)
    except PRParseError as e:
        logger.warning("Review 任务 URL 校验失败 | url={} error={}", request.url, str(e))
        raise HTTPException(status_code=422, detail=str(e))
    return await create_review_task(request)


@router.get("/{task_id}/status", response_model=ReviewTaskStatus)
async def get_review_status(task_id: str):
    """查询 Review 任务状态（Day 3 新增）"""
    logger.debug("查询任务状态 | task_id={}", task_id)
    result = await get_review_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Review task not found.")
    return ReviewTaskStatus(
        task_id=result.task_id,
        status=result.status,
        progress_events=_build_progress_events(result),
        warnings=result.warnings,
    )


@router.get("/{task_id}/quality")
async def get_review_quality(task_id: str):
    """查询报告质量摘要（Day 3 新增）"""
    result = await get_review_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Review task not found.")
    if result.status.value == "failed":
        raise HTTPException(status_code=409, detail="Review report is not ready.")
    return get_report_quality(result)


@router.post("/{task_id}/comments", response_model=CreateReviewCommentsResponse)
async def create_comments(task_id: str, request: CreateReviewCommentsRequest):
    """生成模拟 GitHub Review 评论（Day 3 新增）"""
    result = await get_review_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Review task not found.")
    if result.status.value == "failed":
        raise HTTPException(status_code=409, detail="Review report is not ready.")
    try:
        return create_review_comment_drafts(result, request)
    except CommentServiceError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{task_id}/export.md")
async def export_review_markdown(task_id: str):
    """导出完整 Review 报告为 Markdown（Day 3 新增）"""
    from fastapi.responses import PlainTextResponse

    result = await get_review_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Review task not found.")
    if result.status.value == "failed":
        raise HTTPException(status_code=409, detail="Review report is not ready.")

    # 生成完整报告 markdown
    lines = [f"# CodePilot Review Report", f"", f"**Task ID**: {result.task_id}", ""]

    if result.pr:
        lines.append(f"## PR: {result.pr.title}")
        lines.append(f"- Author: {result.pr.author}")
        lines.append(f"- Branch: {result.pr.head_branch} -> {result.pr.base_branch}")
        lines.append(f"- Files: {result.pr.changed_files} | +{result.pr.additions} -{result.pr.deletions}")
        lines.append("")

    if result.summary:
        lines.append("## Summary")
        lines.append(result.summary.overview)
        lines.append("")

    if result.findings:
        lines.append("## Risk Findings")
        for f in result.findings:
            lines.append(f"### [{f.severity.value}] {f.title}")
            lines.append(f"- File: `{f.file_path}`")
            lines.append(f"- Category: {f.category.value} | Confidence: {f.confidence:.0%}")
            lines.append(f"- Evidence: {f.evidence}")
            lines.append(f"- Reasoning: {f.reasoning}")
            lines.append("")

    if result.suggestions:
        lines.append("## Suggestions")
        for s in result.suggestions:
            lines.append(f"### {s.comment[:80]}")
            lines.append(f"- Rationale: {s.rationale}")
            lines.append(f"- Fix: {s.suggested_fix}")
            lines.append(f"- Blocking: {s.blocking}")
            lines.append("")

    if result.test_recommendations:
        lines.append("## Test Recommendations")
        for t in result.test_recommendations:
            lines.append(f"- {t}")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by CodePilot Review*")

    return PlainTextResponse("\n".join(lines), media_type="text/markdown; charset=utf-8")


@router.get("/{task_id}", response_model=ReviewReport)
async def get_review(task_id: str):
    """根据 task_id 查询完整 Review 报告"""
    logger.debug("查询 Review 报告 | task_id={}", task_id)
    result = await get_review_result(task_id)
    if result is None:
        logger.warning("Review 任务不存在 | task_id={}", task_id)
        raise HTTPException(status_code=404, detail="Review task not found.")
    logger.info("Review 报告查询成功 | task_id={} status={}", task_id, result.status.value)
    return result


def _build_progress_events(report: ReviewReport) -> list[dict]:
    """根据报告状态构造进度事件列表"""
    if report.status.value == "failed":
        return [{"node": "error", "status": "failed", "message": report.error_message or "Unknown error"}]
    nodes = ["parse_pr_url", "fetch_pr", "collect_context", "generate_summary",
             "detect_risks", "generate_suggestions", "guardrail_check", "assemble_report"]
    return [{"node": n, "status": "succeeded", "message": f"{n} completed"} for n in nodes]
