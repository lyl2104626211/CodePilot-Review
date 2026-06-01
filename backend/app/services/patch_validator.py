"""PatchValidator — 校验 LLM 生成的修复代码"""
from app.core.logger import logger
from app.schemas.patch import SuggestedPatch


# 不允许生成 patch 的文件类型
FORBIDDEN_FILE_EXTENSIONS = {".env", ".json", ".lock", ".yaml", ".yml", ".toml"}
FORBIDDEN_FILE_NAMES = {"package-lock.json", "yarn.lock", "poetry.lock", "uv.lock",
                        "pnpm-lock.yaml", ".gitignore", "Dockerfile", ".dockerignore"}
MAX_MODIFIED_LINES = 80


class PatchValidator:
    """修复代码校验器

    第一阶段的校验规则：
    1. file_path 必须在 PR changed files 中
    2. original_code 和 suggested_code 都不能为空
    3. original_code 不应等于 suggested_code
    4. 修改行数不超过 80 行
    5. 不允许修改敏感文件（.env、lock 文件等）
    """

    def validate(
        self,
        patch: SuggestedPatch,
        changed_file_paths: set[str],
        content_excerpt: str | None = None,
    ) -> SuggestedPatch:
        warnings: list[str] = []
        applicable = True

        # 规则1: file_path 必须在 changed files 中
        if patch.file_path not in changed_file_paths:
            warnings.append(f"目标文件 {patch.file_path} 不在 PR 变更文件列表中，patch 可能无法直接应用")
            applicable = False

        # 规则2: original_code 和 suggested_code 不能都为空
        if not patch.original_code or not patch.suggested_code:
            warnings.append("原始代码或建议代码为空，无法生成有效 patch")
            return self._finalize(patch, False, warnings)

        # 规则3: original_code 不应等于 suggested_code
        if patch.original_code.strip() == patch.suggested_code.strip():
            warnings.append("建议代码与原始代码相同，patch 无实际变更")
            applicable = False

        # 规则4: 修改行数不超过 80 行
        original_lines = patch.original_code.splitlines()
        suggested_lines = patch.suggested_code.splitlines()
        changed_lines = abs(len(suggested_lines) - len(original_lines)) + len(original_lines)
        if changed_lines > MAX_MODIFIED_LINES:
            warnings.append(f"patch 涉及 {changed_lines} 行，超过 {MAX_MODIFIED_LINES} 行限制，修改范围过大")

        # 规则5: 不允许修改敏感文件
        path_lower = patch.file_path.lower()
        for ext in FORBIDDEN_FILE_EXTENSIONS:
            if path_lower.endswith(ext):
                warnings.append(f"目标文件类型 {ext} 不适合自动生成 patch")
                applicable = False
                break
        for name in FORBIDDEN_FILE_NAMES:
            if name in path_lower:
                warnings.append(f"目标文件 {name} 不适合自动生成 patch")
                applicable = False
                break

        # 规则6: 如果提供了 content_excerpt，检查 original_code 是否在其中
        if content_excerpt and patch.original_code.strip() not in content_excerpt:
            # 尝试宽松匹配（忽略缩进差异）
            if patch.original_code.strip() not in content_excerpt.replace(" ", ""):
                warnings.append("在当前文件内容中未找到匹配的原始代码，patch 可能无法直接应用")
                applicable = False

        return self._finalize(patch, applicable, warnings)

    def _finalize(self, patch: SuggestedPatch, applicable: bool, warnings: list[str]) -> SuggestedPatch:
        patch.applicable = applicable
        patch.validation_warnings = warnings
        if not applicable and not patch.original_code:
            patch.patch_type = "none"
        return patch
