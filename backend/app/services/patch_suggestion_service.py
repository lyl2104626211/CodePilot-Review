"""PatchSuggestionService — 根据用户选择的 suggestion 生成 AI 代码修复预览"""
import difflib

from app.core.logger import logger
from app.llm.base import LLMClient, LLMError
from app.llm.prompts import PATCH_SYSTEM, build_patch_prompt
from app.schemas.patch import CreateSuggestedPatchesResponse, SuggestedPatch
from app.schemas.review import ReviewReport


class PatchServiceError(ValueError):
    """修复生成异常"""
    pass


def build_unified_diff(file_path: str, original_code: str, suggested_code: str) -> str:
    """使用 difflib 生成 unified diff"""
    original_lines = original_code.splitlines(keepends=True)
    suggested_lines = suggested_code.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            original_lines, suggested_lines,
            fromfile=file_path, tofile=file_path, lineterm="",
        )
    )


def build_github_suggestion(suggested_code: str) -> str:
    """生成 GitHub Suggestion 格式"""
    return f"```suggestion\n{suggested_code.rstrip()}\n```"


class PatchSuggestionService:
    """修复预览生成服务

    流程：
    1. 查找 suggestion 和关联 finding
    2. 构造 patch prompt
    3. LLM 生成 original_code / suggested_code
    4. difflib 生成 unified diff
    5. PatchValidator 校验
    """

    def __init__(self, llm: LLMClient, validator):
        self.llm = llm
        self.validator = validator

    async def create_patches(
        self, report: ReviewReport, suggestion_ids: list[str],
    ) -> CreateSuggestedPatchesResponse:
        """为选中的 suggestion 生成修复预览"""
        suggestion_map = {s.id: s for s in report.suggestions}
        finding_map = {f.id: f for f in report.findings}
        changed_files = {f.path for f in report.pr.files} if report.pr else set()
        warnings: list[str] = []

        # 校验 suggestion_ids
        for sid in suggestion_ids:
            if sid not in suggestion_map:
                raise PatchServiceError(f"Unknown suggestion id: {sid}")

        patches: list[SuggestedPatch] = []
        for i, sid in enumerate(suggestion_ids):
            s = suggestion_map[sid]
            finding = finding_map.get(s.finding_id) if s.finding_id else None

            if not s.file_path:
                patches.append(self._no_patch(sid, s.finding_id, s.comment,
                                              "suggestion 未关联文件路径，无法生成代码修复"))
                continue

            try:
                patch = await self._generate_patch(report, s, finding, changed_files, i)
                patches.append(patch)
            except Exception as e:
                logger.error("patch 生成失败 | suggestion_id={} error={}", sid, str(e))
                warnings.append(f"Failed to generate patch for {sid}: {e}")
                patches.append(self._no_patch(sid, s.finding_id, s.comment,
                                              f"LLM 生成失败: {e}"))

        logger.info("修复预览生成完成 | task_id={} patches={} warnings={}",
                    report.task_id, len(patches), len(warnings))

        return CreateSuggestedPatchesResponse(
            task_id=report.task_id, patches=patches, warnings=warnings,
        )

    async def _generate_patch(self, report, s, finding, changed_files, index) -> SuggestedPatch:
        """调用 LLM 生成单条修补建议"""
        # 获取文件上下文
        file_patch = ""
        content_excerpt = ""
        if report.pr:
            for f in report.pr.files:
                if f.path == s.file_path:
                    file_patch = f.patch or ""
                    break

        # 构造 prompt
        user_prompt = build_patch_prompt(
            pr_title=report.pr.title if report.pr else "",
            file_path=s.file_path or "",
            suggestion_comment=s.comment,
            suggestion_rationale=s.rationale,
            suggested_fix=s.suggested_fix,
            finding_evidence=finding.evidence if finding else "",
            finding_reasoning=finding.reasoning if finding else "",
            patch=file_patch,
            content_excerpt=content_excerpt,
        )

        # ===== Prompt 日志 =====
        logger.info("[Patch Prompt] System:\n{}", PATCH_SYSTEM)
        logger.info("[Patch Prompt] User:\n{}", user_prompt)

        result = await self.llm.generate_json(
            system_prompt=PATCH_SYSTEM,
            user_prompt=user_prompt,
            schema_name="patch",
        )

        logger.info("[Patch 响应] LLM 输出:\n{}",
                    __import__("json").dumps(result, ensure_ascii=False, indent=2))

        original_code = result.get("original_code", "")
        suggested_code = result.get("suggested_code", "")

        # 构造 patch
        patch = SuggestedPatch(
            id=f"patch_{index + 1:03d}",
            suggestion_id=s.id,
            finding_id=s.finding_id,
            file_path=s.file_path or "",
            start_line=result.get("start_line"),
            end_line=result.get("end_line"),
            original_code=original_code,
            suggested_code=suggested_code,
            explanation=result.get("explanation", "无法生成修复代码"),
            safety_notes=["AI 生成的修复建议需要人工确认后应用。"],
        )

        # 生成 diff
        if original_code and suggested_code:
            try:
                patch.unified_diff = build_unified_diff(
                    patch.file_path, original_code, suggested_code,
                )
                patch.github_suggestion = build_github_suggestion(suggested_code)
                patch.patch_type = "unified_diff"
            except Exception as e:
                logger.error("diff 生成失败 | error={}", str(e))
                patch.patch_type = "none"

        # 校验
        patch = self.validator.validate(patch, changed_files, content_excerpt)

        return patch

    def _no_patch(self, suggestion_id: str, finding_id: str | None,
                  comment: str, explanation: str) -> SuggestedPatch:
        """返回空 patch（无法生成修复时）"""
        return SuggestedPatch(
            id=f"patch_{suggestion_id}",
            suggestion_id=suggestion_id,
            finding_id=finding_id,
            file_path="",
            patch_type="none",
            explanation=explanation,
            applicable=False,
            safety_notes=["AI 生成的修复建议需要人工确认后应用。"],
        )
