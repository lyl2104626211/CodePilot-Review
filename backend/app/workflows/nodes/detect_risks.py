"""节点：风险代码检测"""
from app.context.models import ReviewContext
from app.core.logger import logger
from app.llm.base import LLMClient, LLMError
from app.llm.prompts import RISK_SYSTEM, build_risk_prompt
from app.schemas.common import RiskCategory, RiskSeverity
from app.schemas.review import RiskFinding
from app.workflows.review_state import ReviewGraphState


def detect_risks_node(llm: LLMClient):
    """节点5（新）：通过 LLM 识别风险代码

    Args:
        llm: LLM 客户端
    """

    async def node(state: ReviewGraphState) -> ReviewGraphState:
        if state.get("error_message"):
            logger.debug("[工作流] detect_risks 节点跳过（前置错误） | task_id={}", state.get("task_id"))
            return state

        logger.debug("[工作流] detect_risks 节点开始 | task_id={}", state.get("task_id"))

        try:
            ctx: ReviewContext | None = state.get("review_context")

            # 构建文件上下文文本
            parts = []
            if ctx:
                for f in ctx.files:
                    parts.append(f"文件: {f.path} [{f.module_type}] ({f.status}, +{f.additions} -{f.deletions})")
                    if f.patch:
                        parts.append(f.patch[:4000])  # 每个文件最多 4000 字符
                    parts.append("---")

            files_context = "\n".join(parts[:20000])  # 总限制
            user_prompt = build_risk_prompt(files_context)

            result = await llm.generate_json(
                system_prompt=RISK_SYSTEM,
                user_prompt=user_prompt,
                schema_name="risk_findings",
            )

            raw_findings = result.get("findings", [])
            findings = []
            for i, rf in enumerate(raw_findings):
                try:
                    findings.append(RiskFinding(
                        id=rf.get("id", f"risk_{i+1:03d}"),
                        severity=RiskSeverity(rf.get("severity", "medium")),
                        category=RiskCategory(rf.get("category", "correctness")),
                        file_path=rf.get("file_path", ""),
                        line=rf.get("line"),
                        title=rf.get("title", ""),
                        evidence=rf.get("evidence", ""),
                        reasoning=rf.get("reasoning", ""),
                        confidence=float(rf.get("confidence", 0.5)),
                    ))
                except (ValueError, TypeError) as e:
                    logger.warning("[工作流] 单条 finding 解析失败，已跳过 | error={}", str(e))
                    continue

            state["findings"] = findings
            logger.debug("[工作流] detect_risks 节点完成 | task_id={} findings={}",
                        state.get("task_id"), len(findings))
        except (LLMError, ValueError, TypeError) as e:
            logger.error("[工作流] detect_risks 生成失败 | task_id={} error={}",
                        state.get("task_id"), str(e))
            state["findings"] = []
            state.setdefault("warnings", []).append(f"Risk detection failed, returning empty findings: {e}")

        return state

    return node
