"""节点：收集代码上下文"""
from app.context.collector import ContextCollector
from app.core.logger import logger
from app.workflows.review_state import ReviewGraphState

collector = ContextCollector()


def collect_context_node(state: ReviewGraphState) -> ReviewGraphState:
    """节点3（新）：从 PR 快照收集文件上下文

    调用 ContextCollector 将 pr_snapshot 的 files 转换为带分类标签
    和关联测试路径的 FileContext 列表，存入 state["review_context"]。
    """
    if state.get("error_message"):
        logger.debug("[工作流] collect_context 节点跳过（前置错误） | task_id={}", state.get("task_id"))
        return state

    logger.debug("[工作流] collect_context 节点开始 | task_id={}", state.get("task_id"))

    try:
        context = collector.collect(state["pr_snapshot"])
        state["review_context"] = context

        if context.warnings:
            existing = state.get("warnings", [])
            existing.extend(context.warnings)
            state["warnings"] = existing

        logger.debug("[工作流] collect_context 节点完成 | task_id={} files={} warnings={}",
                     state.get("task_id"), len(context.files), len(context.warnings))
    except Exception as e:
        logger.error("[工作流] collect_context 节点失败 | task_id={} error={}", state.get("task_id"), str(e))
        state["error_message"] = str(e)

    return state
