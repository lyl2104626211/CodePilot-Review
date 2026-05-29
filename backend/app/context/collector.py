"""上下文收集器：将 PR 文件列表转换为带上下文标签的 ReviewContext"""
from app.context.heuristics import classify_file, find_related_tests
from app.context.models import FileContext, ReviewContext
from app.core.logger import logger
from app.schemas.github import PullRequestFile, PullRequestSnapshot

# 每个文件最多保留的 patch 字符数
MAX_FILE_CONTEXT_CHARS = 6000
# 总上下文最多保留的字符数
MAX_TOTAL_CONTEXT_CHARS = 24000


class ContextCollector:
    """从 PR 变更文件收集分析上下文

    第 2 天不做 AST 解析，纯路径模式匹配 + patch 截断。
    后续可接入文件内容读取和 AST 函数提取。
    """

    def __init__(
        self,
        max_file_chars: int = MAX_FILE_CONTEXT_CHARS,
        max_total_chars: int = MAX_TOTAL_CONTEXT_CHARS,
    ):
        self.max_file_chars = max_file_chars
        self.max_total_chars = max_total_chars

    def collect(self, pr: PullRequestSnapshot, file_contents: dict[str, str] | None = None) -> ReviewContext:
        """收集 PR 所有变更文件的上下文

        Args:
            pr: PR 快照（含文件列表和 patch）
            file_contents: 可选的文件内容映射 {path: content}，预留接口

        Returns:
            ReviewContext: 包含所有文件上下文和警告信息
        """
        file_contents = file_contents or {}
        files: list[FileContext] = []
        warnings: list[str] = []
        total_chars = 0

        for pf in pr.files:
            try:
                fc = self._build_file_context(pf, file_contents, total_chars)
                if fc is not None:
                    files.append(fc)
                    total_chars += len(fc.patch or "")
            except Exception as e:
                logger.warning("文件上下文收集失败 | path={} error={}", pf.path, str(e))
                warnings.append(f"Failed to collect context for {pf.path}: {e}")

        logger.info("上下文收集完成 | total_files={} total_chars={} warnings={}",
                    len(files), total_chars, len(warnings))

        return ReviewContext(pr=pr, files=files, warnings=warnings)

    def _build_file_context(
        self,
        pf: PullRequestFile,
        file_contents: dict[str, str],
        current_total_chars: int,
    ) -> FileContext | None:
        """构建单个文件的上下文信息

        Returns:
            FileContext 或 None（超出预算或无法处理时跳过）
        """
        # 跳过二进制文件和超大文件
        if self._is_binary(pf):
            return None

        # patch 截断
        patch = self._truncate_patch(pf.patch)

        # 超出总预算时仍保留文件元信息，但 patch 置空并标记 warning
        if current_total_chars + len(patch or "") > self.max_total_chars:
            patch = None

        # 文件内容摘要（预留）
        content_excerpt = None
        if pf.path in file_contents:
            content = file_contents[pf.path]
            content_excerpt = content[:self.max_file_chars] if len(content) > self.max_file_chars else content

        # 分类和关联
        module_type = classify_file(pf.path, pf.status)
        related_tests = find_related_tests(pf.path)

        # 来源标签
        labels = []
        if patch:
            labels.append("patch_available")
        if content_excerpt:
            labels.append("content_available")
        if related_tests:
            labels.append("related_tests_found")
        if module_type != "unknown":
            labels.append(f"module_{module_type}")

        return FileContext(
            path=pf.path,
            module_type=module_type,
            status=pf.status,
            additions=pf.additions,
            deletions=pf.deletions,
            patch=patch,
            content_excerpt=content_excerpt,
            related_test_paths=related_tests,
            evidence_labels=labels,
        )

    def _truncate_patch(self, patch: str | None) -> str | None:
        """截断过长的 patch 内容"""
        if patch is None:
            return None
        if len(patch) <= self.max_file_chars:
            return patch
        return patch[:self.max_file_chars] + f"\n... [truncated, {len(patch) - self.max_file_chars} chars omitted]"

    @staticmethod
    def _is_binary(pf: PullRequestFile) -> bool:
        """判断文件是否可能是二进制文件（通过路径和 patch 判断）"""
        binary_extensions = {
            ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
            ".woff", ".woff2", ".ttf", ".eot",
            ".pdf", ".zip", ".gz", ".tar", ".7z",
            ".mp4", ".mp3", ".mov", ".avi",
            ".pyc", ".pyo", ".class", ".jar",
            ".lock", "package-lock.json", "yarn.lock",
        }
        path_lower = pf.path.lower()
        for ext in binary_extensions:
            if path_lower.endswith(ext) or ext in path_lower:
                return True
        # 有文件状态但没有 patch 可能是二进制
        if pf.status in ("modified", "added") and not pf.patch:
            return True
        return False
