from fastapi import APIRouter, HTTPException

from app.schemas.review import (
    CreateReviewTaskRequest,
    CreateReviewTaskResponse,
    ParsePullRequestRequest,
    ReviewReport,
)
from app.services.pr_parser import PRParseError, parse_github_pr_url
from app.services.review_service import create_review_task, get_review_result

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/parse", response_model=dict)
async def parse_pr_url(request: ParsePullRequestRequest):
    try:
        parsed = parse_github_pr_url(request.url)
        return parsed.model_dump()
    except PRParseError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("", response_model=CreateReviewTaskResponse)
async def create_review(request: CreateReviewTaskRequest):
    try:
        parse_github_pr_url(request.url)
    except PRParseError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return await create_review_task(request)


@router.get("/{task_id}", response_model=ReviewReport)
async def get_review(task_id: str):
    result = await get_review_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Review task not found.")
    return result
