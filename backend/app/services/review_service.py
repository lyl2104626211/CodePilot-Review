import uuid

from app.core.logger import logger
from app.llm.fallback import FallbackLLMClient
from app.providers.github import GitHubProvider
from app.providers.mock_github import MockGitHubProvider
from app.schemas.review import CreateReviewTaskRequest, CreateReviewTaskResponse, ReviewReport
from app.schemas.common import TaskStatus
from app.storage.memory_store import MemoryTaskStore
from app.workflows.review_graph import build_demo_graph, build_review_graph

# 模块级单例：demo 模式共用一份编译好的 graph
store = MemoryTaskStore()
demo_graph = build_demo_graph(MockGitHubProvider())
# LLM 降级客户端：GitHub 模式下默认使用（后续可通过配置切换为真实 API）
fallback_llm = FallbackLLMClient()


async def create_review_task(request: CreateReviewTaskRequest) -> CreateReviewTaskResponse:
    """创建并执行 Review 任务

    流程：
    1. 生成唯一 task_id
    2. 根据 mode 选择 Provider 和 Graph（demo 用 4 节点，github 用 9 节点）
    3. 异步执行工作流
    4. 将结果存入 MemoryTaskStore
    5. 返回 task_id 和状态
    """
    task_id = f"task_{uuid.uuid4().hex[:24]}"
    logger.info("开始执行 Review 工作流 | task_id={} url={} mode={}", task_id, request.url, request.mode)

    # 根据模式构建对应的 graph
    github_provider = None
    if request.mode == "github":
        github_provider = GitHubProvider()
        try:
            review_graph = build_review_graph(github_provider, fallback_llm)
        except Exception as e:
            logger.error("GitHub Provider 初始化失败 | task_id={} error={}", task_id, str(e))
            await github_provider.close()
            error_report = ReviewReport(
                task_id=task_id,
                status=TaskStatus.failed,
                error_message=f"Failed to initialize GitHub client: {e}",
            )
            store.save(error_report)
            return CreateReviewTaskResponse(task_id=task_id, status=TaskStatus.failed)
    else:
        review_graph = demo_graph

    # 工作流初始状态
    state = {
        "task_id": task_id,
        "url": request.url,
        "mode": request.mode,
        "warnings": [],
    }

    try:
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

        # 附加 warnings 到 report（如果有）
        if result.get("warnings"):
            # report.warnings 字段暂未在 ReviewReport 中，仅在日志中记录
            logger.info("Review 工作流包含警告 | task_id={} warnings={}",
                        task_id, result["warnings"])

        store.save(report)
        logger.info("Review 工作流执行成功 | task_id={} findings_count={} suggestions_count={}",
                    task_id, len(report.findings), len(report.suggestions))
        return CreateReviewTaskResponse(task_id=task_id, status=TaskStatus.succeeded)
    finally:
        if github_provider is not None:
            await github_provider.close()
            logger.debug("GitHub Provider 已关闭 | task_id={}", task_id)


async def get_review_result(task_id: str) -> ReviewReport | None:
    """根据 task_id 查询 Review 报告，不存在时返回 None"""
    logger.debug("从存储查询任务 | task_id={}", task_id)
    result = store.get(task_id)
    if result:
        logger.debug("存储命中 | task_id={}", task_id)
    else:
        logger.debug("存储未命中 | task_id={}", task_id)
    return result
