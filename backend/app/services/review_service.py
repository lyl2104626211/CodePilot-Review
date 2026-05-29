import uuid

from app.providers.mock_github import MockGitHubProvider
from app.schemas.review import CreateReviewTaskRequest, CreateReviewTaskResponse, ReviewReport
from app.schemas.common import TaskStatus
from app.storage.memory_store import MemoryTaskStore
from app.workflows.review_graph import build_review_graph

# 模块级单例：第 2 天 Demo 模式关闭时，需要替换 provider 注入
store = MemoryTaskStore()
mock_provider = MockGitHubProvider()
review_graph = build_review_graph(mock_provider)


async def create_review_task(request: CreateReviewTaskRequest) -> CreateReviewTaskResponse:
    """创建并执行 Review 任务

    流程：
    1. 生成唯一 task_id
    2. 构造 LangGraph 初始状态
    3. 异步执行工作流（parse → fetch → review → assemble）
    4. 将结果存入 MemoryTaskStore
    5. 返回 task_id 和状态
    """
    task_id = f"task_{uuid.uuid4().hex[:24]}"

    # 工作流初始状态：只需 task_id, url, mode
    state = {
        "task_id": task_id,
        "url": request.url,
        "mode": request.mode,
    }

    result = await review_graph.ainvoke(state)

    # 工作流中任意节点设置了 error_message 即视为失败
    if result.get("error_message"):
        error_report = ReviewReport(
            task_id=task_id,
            status=TaskStatus.failed,
            error_message=result["error_message"],
        )
        store.save(error_report)
        return CreateReviewTaskResponse(task_id=task_id, status=TaskStatus.failed)

    # 安全守卫：如果工作流异常既无错误也无 report，返回失败
    report = result.get("report")
    if report is None:
        error_report = ReviewReport(
            task_id=task_id,
            status=TaskStatus.failed,
            error_message="Workflow completed but produced no report.",
        )
        store.save(error_report)
        return CreateReviewTaskResponse(task_id=task_id, status=TaskStatus.failed)

    store.save(report)
    return CreateReviewTaskResponse(task_id=task_id, status=TaskStatus.succeeded)


async def get_review_result(task_id: str) -> ReviewReport | None:
    """根据 task_id 查询 Review 报告，不存在时返回 None"""
    return store.get(task_id)
