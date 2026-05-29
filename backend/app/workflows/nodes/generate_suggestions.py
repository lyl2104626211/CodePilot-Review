"""节点：生成 Review 建议"""
import json

from app.context.models import ReviewContext
from app.core.logger import logger
from app.llm.base import LLMClient, LLMError
from app.llm.prompts import SUGGESTION_SYSTEM, build_suggestion_prompt
from app.schemas.review import ReviewSuggestion
from app.workflows.review_state import ReviewGraphState


def generate_suggestions_node(llm: LLMClient):
    """节点6（新）：通过 LLM 生成 Review 建议和测试建议

    Args:
        llm: LLM 客户端
    """

    async def node(state: ReviewGraphState) -> ReviewGraphState:
        if state.get("error_message"):
            logger.debug("[工作流] generate_suggestions 节点跳过（前置错误） | task_id={}", state.get("task_id"))
            return state

        logger.debug("[工作流] generate_suggestions 节点开始 | task_id={}", state.get("task_id"))

        try:
            # 序列化 findings 供 prompt 使用
            findings_data = [
                {
                    "id": f.id,
                    "severity": f.severity.value,
                    "category": f.category.value,
                    "file_path": f.file_path,
                    "title": f.title,
                    "reasoning": f.reasoning,
                }
                for f in state.get("findings", [])
            ]
            findings_json = json.dumps(findings_data, ensure_ascii=False, indent=2)

            user_prompt = build_suggestion_prompt(
                findings_json=findings_json,
                files_context=""  # 已有 findings，context 可以省略
            )

            result = await llm.generate_json(
                system_prompt=SUGGESTION_SYSTEM,
                user_prompt=user_prompt,
                schema_name="suggestions",
            )

            raw_suggestions = result.get("suggestions", [])
            suggestions = []
            for i, rs in enumerate(raw_suggestions):
                suggestions.append(ReviewSuggestion(
                    id=rs.get("id", f"suggestion_{i+1:03d}"),
                    finding_id=rs.get("finding_id"),
                    file_path=rs.get("file_path"),
                    comment=rs.get("comment", ""),
                    rationale=rs.get("rationale", ""),
                    suggested_fix=rs.get("suggested_fix", ""),
                    blocking=bool(rs.get("blocking", False)),
                ))

            state["suggestions"] = suggestions
            state["test_recommendations"] = result.get("test_recommendations", [])

            logger.debug("[工作流] generate_suggestions 节点完成 | task_id={} suggestions={} test_recs={}",
                        state.get("task_id"), len(suggestions), len(state["test_recommendations"]))
        except LLMError as e:
            logger.error("[工作流] generate_suggestions LLM 调用失败 | task_id={} error={}",
                        state.get("task_id"), str(e))
            state["suggestions"] = []
            state["test_recommendations"] = []
            state.setdefault("warnings", []).append(f"Suggestion generation failed: {e}")

        return state

    return node
