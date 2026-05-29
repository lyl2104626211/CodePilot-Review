from app.core.logger import logger
from app.schemas.common import TaskStatus
from app.schemas.review import ReviewReport
from app.workflows.review_state import ReviewGraphState


def assemble_report_node(state: ReviewGraphState) -> ReviewGraphState:
    """节点4：组装最终 ReviewReport

    将前序节点产出的 summary、findings、suggestions、test_recommendations
    以及 PR 快照拼装为完整的 ReviewReport，写入 state["report"]。
    """
    if state.get("error_message"):
        logger.debug("[工作流] assemble_report 节点跳过（前置错误） | task_id={}", state.get("task_id"))
        return state

    logger.debug("[工作流] assemble_report 节点开始 | task_id={}", state.get("task_id"))

    state["report"] = ReviewReport(
        task_id=state["task_id"],
        status=TaskStatus.succeeded,
        pr=state["pr_snapshot"],
        summary=state["summary"],
        findings=state.get("findings", []),
        suggestions=state.get("suggestions", []),
        test_recommendations=state.get("test_recommendations", []),
        warnings=state.get("warnings", []),
    )

    logger.info("[工作流] assemble_report 节点完成，报告已生成 | task_id={}", state.get("task_id"))
    return state
