import uuid

from app.core.logger import logger
from app.providers.mock_github import MockGitHubProvider
from app.schemas.review import CreateReviewTaskRequest, CreateReviewTaskResponse, ReviewReport
from app.schemas.common import TaskStatus
from app.storage.memory_store import MemoryTaskStore
from app.workflows.review_graph import build_review_graph

# 模块级单例：第 2 天 Demo 模式关闭时，需要替换 provider 注入
store = MemoryTaskStore()
demo_graph = build_review_graph(MockGitHubProvider())


async def create_review_task(request: CreateReviewTaskRequest) -> CreateReviewTaskResponse:
    """创建并执行 Review 任务

    流程：
    1. 生成唯一 task_id
    2. 根据 mode 选择 Provider（demo 用 Mock，github 待接入）
    3. 异步执行工作流（parse → fetch → review → assemble）
    4. 将结果存入 MemoryTaskStore
    5. 返回 task_id 和状态
    """
    task_id = f"task_{uuid.uuid4().hex[:24]}"
    logger.info("开始执行 Review 工作流 | task_id={} url={} mode={}", task_id, request.url, request.mode)

    # 模式路由：github 模式暂未接入真实 GitHub Provider
    if request.mode == "github":
        logger.warning("GitHub 模式暂未接入 | task_id={}", task_id)
        error_report = ReviewReport(
            task_id=task_id,
            status=TaskStatus.failed,
            error_message="GitHub mode is not yet available. Please use demo mode or wait for Day 2 integration.",
        )
        store.save(error_report)
        return CreateReviewTaskResponse(task_id=task_id, status=TaskStatus.failed)

    review_graph = demo_graph

    # 工作流初始状态：只需 task_id, url, mode
    state = {
        "task_id": task_id,
        "url": request.url,
        "mode": request.mode,
    }

    logger.debug("调用 LangGraph 工作流 | task_id={}", task_id)
    result = await review_graph.ainvoke(state)
    logger.debug("LangGraph 工作流返回 | task_id={} has_error={} has_report={}",
                 task_id,
                 "error_message" in result and result["error_message"] is not None,
                 "report" in result and result["report"] is not None)

    # 工作流中任意节点设置了 error_message 即视为失败
    if result.get("error_message"):
        logger.error("Review 工作流执行失败 | task_id={} error={}", task_id, result["error_message"])
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
        logger.error("Review 工作流未产出报告 | task_id={}", task_id)
        error_report = ReviewReport(
            task_id=task_id,
            status=TaskStatus.failed,
            error_message="Workflow completed but produced no report.",
        )
        store.save(error_report)
        return CreateReviewTaskResponse(task_id=task_id, status=TaskStatus.failed)

    store.save(report)
    logger.info("Review 工作流执行成功 | task_id={} findings_count={} suggestions_count={}",
                task_id, len(report.findings), len(report.suggestions))
    return CreateReviewTaskResponse(task_id=task_id, status=TaskStatus.succeeded)


async def get_review_result(task_id: str) -> ReviewReport | None:
    """根据 task_id 查询 Review 报告，不存在时返回 None"""
    logger.debug("从存储查询任务 | task_id={}", task_id)
    result = store.get(task_id)
    if result:
        logger.debug("存储命中 | task_id={}", task_id)
    else:
        logger.debug("存储未命中 | task_id={}", task_id)
    return result
