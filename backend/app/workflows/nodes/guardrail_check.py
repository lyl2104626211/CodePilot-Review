"""节点：质量护栏 —— 过滤低质量、无证据、重复的 findings"""
from app.core.logger import logger
from app.workflows.review_state import ReviewGraphState


# 默认最低置信度阈值
MIN_CONFIDENCE_THRESHOLD = 0.45


def guardrail_check_node(confidence_threshold: float = MIN_CONFIDENCE_THRESHOLD):
    """节点7（新）：质量护栏自检

    过滤规则：
    1. 低置信度过滤（confidence < threshold）
    2. 无证据过滤（critical/high 必须有 evidence）
    3. 重复标题去重

    Args:
        confidence_threshold: 置信度阈值，默认 0.45
    """

    def node(state: ReviewGraphState) -> ReviewGraphState:
        if state.get("error_message"):
            logger.debug("[工作流] guardrail_check 节点跳过（前置错误） | task_id={}", state.get("task_id"))
            return state

        findings = state.get("findings", [])
        if not findings:
            return state

        logger.debug("[工作流] guardrail_check 节点开始 | task_id={} before_count={}",
                    state.get("task_id"), len(findings))

        filtered = []
        seen_titles: set[str] = set()
        removed_count = 0

        for f in findings:
            # 规则1: 置信度过滤
            if f.confidence < confidence_threshold:
                logger.debug("[工作流] guardrail 过滤（低置信度） | id={} confidence={}", f.id, f.confidence)
                removed_count += 1
                continue

            # 规则2: high/critical 必须有 evidence
            if f.severity.value in ("critical", "high") and (not f.evidence or len(f.evidence.strip()) < 10):
                logger.debug("[工作流] guardrail 过滤（缺少evidence） | id={} severity={}", f.id, f.severity.value)
                removed_count += 1
                continue

            # 规则3: 标题去重
            normalized_title = f.title.strip().lower()
            if normalized_title in seen_titles:
                logger.debug("[工作流] guardrail 过滤（重复标题） | id={} title={}", f.id, f.title)
                removed_count += 1
                continue
            seen_titles.add(normalized_title)

            filtered.append(f)

        state["findings"] = filtered
        logger.info("[工作流] guardrail_check 节点完成 | task_id={} before={} after={} removed={}",
                    state.get("task_id"), len(findings), len(filtered), removed_count)

        return state

    return node
