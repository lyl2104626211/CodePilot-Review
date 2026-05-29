from fastapi import APIRouter, HTTPException

from app.core.logger import logger
from app.schemas.github import ParsedPullRequest
from app.schemas.review import (
    CreateReviewTaskRequest,
    CreateReviewTaskResponse,
    ParsePullRequestRequest,
    ReviewReport,
)
from app.services.pr_parser import PRParseError, parse_github_pr_url
from app.services.review_service import create_review_task, get_review_result

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


@router.get("/{task_id}", response_model=ReviewReport)
async def get_review(task_id: str):
    """根据 task_id 查询 Review 报告"""
    logger.debug("查询 Review 报告 | task_id={}", task_id)
    result = await get_review_result(task_id)
    if result is None:
        logger.warning("Review 任务不存在 | task_id={}", task_id)
        raise HTTPException(status_code=404, detail="Review task not found.")
    logger.info("Review 报告查询成功 | task_id={} status={}", task_id, result.status.value)
    return result
