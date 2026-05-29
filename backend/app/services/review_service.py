import uuid

from app.providers.mock_github import MockGitHubProvider
from app.schemas.review import CreateReviewTaskRequest, CreateReviewTaskResponse, ReviewReport
from app.schemas.common import TaskStatus
from app.storage.memory_store import MemoryTaskStore
from app.workflows.review_graph import build_review_graph

store = MemoryTaskStore()
mock_provider = MockGitHubProvider()
review_graph = build_review_graph(mock_provider)


async def create_review_task(request: CreateReviewTaskRequest) -> CreateReviewTaskResponse:
    task_id = f"task_{uuid.uuid4().hex[:24]}"

    state = {
        "task_id": task_id,
        "url": request.url,
        "mode": request.mode,
    }

    result = await review_graph.ainvoke(state)

    if result.get("error_message"):
        error_report = ReviewReport(
            task_id=task_id,
            status=TaskStatus.failed,
            error_message=result["error_message"],
        )
        store.save(error_report)
        return CreateReviewTaskResponse(task_id=task_id, status=TaskStatus.failed)

    report = result["report"]
    store.save(report)
    return CreateReviewTaskResponse(task_id=task_id, status=TaskStatus.succeeded)


async def get_review_result(task_id: str) -> ReviewReport | None:
    return store.get(task_id)
