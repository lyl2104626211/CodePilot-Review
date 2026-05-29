"""节点：生成 PR 变更总结"""
from app.context.models import ReviewContext
from app.core.logger import logger
from app.llm.base import LLMClient, LLMError
from app.llm.prompts import SUMMARY_SYSTEM, build_summary_prompt
from app.schemas.review import ReviewSummary
from app.workflows.review_state import ReviewGraphState


def generate_summary_node(llm: LLMClient):
    """节点4（新）：通过 LLM 生成 PR 变更总结

    Args:
        llm: LLM 客户端（Fallback 或 OpenAI 兼容）
    """

    async def node(state: ReviewGraphState) -> ReviewGraphState:
        if state.get("error_message"):
            logger.debug("[工作流] generate_summary 节点跳过（前置错误） | task_id={}", state.get("task_id"))
            return state

        logger.debug("[工作流] generate_summary 节点开始 | task_id={}", state.get("task_id"))

        try:
            pr = state["pr_snapshot"]
            ctx: ReviewContext | None = state.get("review_context")

            # 构建文件摘要供 prompt 使用
            files_lines = []
            if ctx:
                for f in ctx.files:
                    files_lines.append(
                        f"- [{f.module_type}] {f.path} ({f.status}, +{f.additions} -{f.deletions})"
                    )
            else:
                for f in pr.files:
                    files_lines.append(f"- {f.path} ({f.status}, +{f.additions} -{f.deletions})")

            files_summary = "\n".join(files_lines[:50])  # 最多 50 个文件

            user_prompt = build_summary_prompt(
                pr_title=pr.title,
                pr_author=pr.author,
                base_branch=pr.base_branch,
                head_branch=pr.head_branch,
                files_summary=files_summary,
                additions=pr.additions,
                deletions=pr.deletions,
            )

            result = await llm.generate_json(
                system_prompt=SUMMARY_SYSTEM,
                user_prompt=user_prompt,
                schema_name="summary",
            )

            state["summary"] = ReviewSummary(
                overview=result.get("overview", "无法生成总结"),
                changed_modules=result.get("changed_modules", []),
                reviewer_focus=result.get("reviewer_focus", []),
            )

            logger.debug("[工作流] generate_summary 节点完成 | task_id={}", state.get("task_id"))
        except (LLMError, ValueError, TypeError) as e:
            logger.error("[工作流] generate_summary 生成失败 | task_id={} error={}",
                        state.get("task_id"), str(e))
            # LLM 失败或输出格式异常时使用降级总结
            state["summary"] = ReviewSummary(
                overview=f"本 PR 对 {state['pr_snapshot'].changed_files} 个文件进行了变更。",
                changed_modules=["backend", "tests"],
                reviewer_focus=["请人工确认变更的正确性和完整性"],
            )
            state.setdefault("warnings", []).append(f"Summary generation failed, using fallback: {e}")

        return state

    return node
