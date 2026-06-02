"""模拟 Review 评论生成服务 — 将用户选择的建议转换为 GitHub 风格评论"""
from app.core.logger import logger
from app.schemas.review import (
    CreateReviewCommentsRequest,
    CreateReviewCommentsResponse,
    ReviewCommentDraft,
    ReviewReport,
)


class CommentServiceError(ValueError):
    """评论生成异常"""
    pass


def create_review_comment_drafts(
    report: ReviewReport,
    request: CreateReviewCommentsRequest,
) -> CreateReviewCommentsResponse:
    """根据选中的 suggestion 生成 GitHub 风格模拟评论

    Args:
        report: 已生成的 ReviewReport
        request: 用户选择的 suggestion_ids + 渲染选项

    Returns:
        CreateReviewCommentsResponse: comments 列表 + 完整 markdown

    Raises:
        CommentServiceError: selection 非法时抛出
    """
    # 校验
    if not request.suggestion_ids:
        raise CommentServiceError("At least one suggestion must be selected.")

    suggestion_map = {s.id: s for s in report.suggestions}
    finding_map = {f.id: f for f in report.findings}

    for sid in request.suggestion_ids:
        if sid not in suggestion_map:
            raise CommentServiceError(f"Unknown suggestion id: {sid}")

    # 构建文件 → patch 映射
    file_patches: dict[str, str] = {}
    if report.pr and report.pr.files:
        for pf in report.pr.files:
            if pf.patch:
                file_patches[pf.path] = pf.patch

    # 生成单条评论
    comments: list[ReviewCommentDraft] = []
    for i, sid in enumerate(request.suggestion_ids):
        s = suggestion_map[sid]
        finding = finding_map.get(s.finding_id) if s.finding_id else None
        original_patch = file_patches.get(s.file_path or "", "")

        body = _render_comment_body(s, finding, original_patch)

        comments.append(ReviewCommentDraft(
            id=f"comment_{i + 1:03d}",
            suggestion_id=s.id,
            finding_id=s.finding_id,
            file_path=s.file_path,
            line=None,
            body=body,
            severity=finding.severity if finding else None,
            blocking=s.blocking,
        ))

    # 生成完整 Markdown
    markdown = _render_markdown(
        report, comments,
        include_summary=request.include_summary,
        include_test_recommendations=request.include_test_recommendations,
    )

    logger.info("模拟评论生成完成 | task_id={} comments={}", report.task_id, len(comments))

    return CreateReviewCommentsResponse(
        task_id=report.task_id,
        comments=comments,
        markdown=markdown,
    )


def _render_comment_body(suggestion, finding, original_patch: str = "") -> str:
    """渲染单条评论正文（GitHub 风格 Markdown）"""
    lines = []

    # 标题 + 位置
    if finding:
        lines.append(f"**Review 建议：{finding.title}**")
    else:
        preview = suggestion.comment[:60] if suggestion.comment else "(no comment)"
        lines.append(f"**Review 建议：{preview}**")

    if suggestion.file_path:
        lines.append(f"\n位置：`{suggestion.file_path}`")

    # 问题说明（evidence + 分析 + 原因合并）
    parts = []
    if finding and finding.evidence:
        parts.append(finding.evidence)
    parts.append(suggestion.comment)
    parts.append(suggestion.rationale)
    lines.append(f"\n**问题说明**\n" + "；".join(parts))

    # 代码对比：原始 → 建议，紧挨着
    original_code = _extract_original_code(suggestion, finding, original_patch)
    fix_code = _extract_fix_code(suggestion.suggested_fix)

    if original_code or fix_code:
        lines.append("\n---")
        lines.append("**代码对比**")
        lines.append("")

        if original_code:
            lines.append("修改前：")
            lines.append("```")
            lines.append(original_code.strip())
            lines.append("```")
            lines.append("")

        if fix_code:
            lines.append("修改后：")
            lines.append("```python")
            lines.append(fix_code.strip())
            lines.append("```")
        elif not fix_code and suggestion.suggested_fix:
            lines.append(f"\n**修改后**\n{suggestion.suggested_fix}")
        lines.append("---")

    # 元信息
    if finding:
        lines.append(f"\n> 置信度：{finding.confidence:.0%} | 严重程度：{finding.severity.value}")

    if suggestion.blocking:
        lines.append("\n> 建议合并前处理")

    return "\n".join(lines)


def _extract_original_code(suggestion, finding, patch: str) -> str:
    """从 finding evidence 或 PR patch 中提取原始代码片段"""
    # 优先从 evidence 中提取代码块
    if finding and finding.evidence:
        ev = finding.evidence.strip()
        # 如果 evidence 本身就像代码（含缩进/换行/关键字），直接返回
        if "\n" in ev and len(ev) > 20:
            return ev
        # 如果是短文本描述，不当作代码返回

    # 从 PR patch 中提取相关片段
    if patch:
        trimmed = patch.strip()
        if trimmed:
            # 完整展示 patch 内容（diff 格式），不截断
            return trimmed

    return ""


def _extract_fix_code(suggested_fix: str) -> str:
    """判断 suggested_fix 是否包含代码，有则提取"""
    sf = suggested_fix.strip()
    # 如果包含代码特征（缩进、def、try、return 等关键字），作为代码返回
    code_indicators = ["def ", "try:", "    ", "\t", "return ", "if ", "for ", "while ",
                       "import ", "class ", "except", "@", "self."]
    if any(ind in sf for ind in code_indicators):
        return sf
    # 如果 suggest_fix 有多行且有明显的代码结构
    if "\n" in sf and len(sf) > 40:
        return sf
    return ""


def _render_markdown(report, comments, include_summary=True, include_test_recommendations=True) -> str:
    """渲染完整 Review Markdown 总评"""
    lines = ["# CodePilot Review 模拟评审", ""]

    if include_summary and report.summary:
        lines.append("## PR 总结")
        lines.append(report.summary.overview)
        lines.append("")

    lines.append("## 建议处理项")
    for c in comments:
        tag = "阻塞合并" if c.blocking else "建议修复"
        lines.append(f"- [{tag}] {c.suggestion_id}")
    lines.append("")

    if include_test_recommendations and report.test_recommendations:
        lines.append("## 测试建议")
        for t in report.test_recommendations:
            lines.append(f"- {t}")
        lines.append("")

    lines.append("---")
    lines.append("> 本评论由 CodePilot Review 生成，当前为模拟发布结果，需人工确认后再提交到 GitHub。")

    return "\n".join(lines)


def get_report_quality(report: ReviewReport) -> "ReportQualitySummary":
    """从 ReviewReport 提取质量摘要"""
    from app.schemas.review import ReportQualitySummary

    findings = report.findings
    suggestions = report.suggestions

    high = sum(1 for f in findings if f.confidence >= 0.7)
    low = sum(1 for f in findings if f.confidence < 0.5)
    blocking = sum(1 for s in suggestions if s.blocking)

    notes = []
    if low > 0:
        notes.append(f"{low} 条低置信度发现已在前端默认隐藏，可手动查看")
    if report.warnings:
        notes.append("分析过程中存在警告，部分上下文或模型能力降级")
    if blocking > 0:
        notes.append(f"{blocking} 条建议建议在合并前处理")

    return ReportQualitySummary(
        total_findings=len(findings),
        high_confidence_findings=high,
        low_confidence_findings=low,
        blocking_suggestions=blocking,
        warning_count=len(report.warnings),
        fallback_used=len(report.warnings) > 0,
        notes=notes,
    )
