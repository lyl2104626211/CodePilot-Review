"""PatchSuggestionService 单元测试"""
import pytest
from app.schemas.patch import CreateSuggestedPatchesResponse, SuggestedPatch
from app.schemas.common import RiskCategory, RiskSeverity, TaskStatus
from app.schemas.github import PullRequestFile, PullRequestSnapshot
from app.schemas.review import ReviewReport, ReviewSuggestion, ReviewSummary, RiskFinding
from app.services.patch_suggestion_service import (
    build_github_suggestion,
    build_unified_diff,
    PatchSuggestionService,
    PatchServiceError,
)
from app.services.patch_validator import PatchValidator
from app.llm.fallback import FallbackLLMClient


@pytest.fixture
def sample_report():
    return ReviewReport(
        task_id="test_task",
        status=TaskStatus.succeeded,
        pr=PullRequestSnapshot(
            owner="a", repo="b", number=1, title="Add async review",
            author="x", base_branch="main", head_branch="feat",
            changed_files=2, additions=50, deletions=10, commit_count=2,
            files=[
                PullRequestFile(path="backend/app/api/reviews.py", status="modified",
                                additions=30, deletions=5,
                                patch="@@ -40,5 +40,10 @@\n-result = await graph.ainvoke(state)\n+try:\n+    result = await graph.ainvoke(state)\n+except Exception as exc:\n+    pass"),
            ],
        ),
        summary=ReviewSummary(overview="Add async review", changed_modules=["backend"], reviewer_focus=["error handling"]),
        findings=[
            RiskFinding(id="risk_001", severity=RiskSeverity.medium, category=RiskCategory.correctness,
                        file_path="backend/app/api/reviews.py", line=42, title="Missing error check",
                        evidence="no try/except", reasoning="may crash", confidence=0.8),
        ],
        suggestions=[
            ReviewSuggestion(id="s_001", finding_id="risk_001", file_path="backend/app/api/reviews.py",
                             comment="Add try/except around graph.ainvoke",
                             rationale="prevent unhandled exceptions",
                             suggested_fix="wrap in try/except", blocking=True),
        ],
    )


class TestDiffBuilder:
    def test_unified_diff_add(self):
        diff = build_unified_diff("a.py", "line1\n", "line1\nline2\n")
        assert "---" in diff
        assert "+++" in diff
        assert "+line2" in diff

    def test_unified_diff_remove(self):
        diff = build_unified_diff("a.py", "line1\nline2\n", "line1\n")
        assert "-line2" in diff

    def test_unified_diff_modify(self):
        diff = build_unified_diff("a.py", "old\n", "new\n")
        assert "-old" in diff
        assert "+new" in diff

    def test_github_suggestion(self):
        sug = build_github_suggestion("print('hello')")
        assert "```suggestion" in sug
        assert "print('hello')" in sug


class TestPatchSuggestionService:
    @pytest.mark.asyncio
    async def test_create_patches_success(self, sample_report):
        llm = FallbackLLMClient()
        validator = PatchValidator()
        service = PatchSuggestionService(llm, validator)
        resp = await service.create_patches(sample_report, ["s_001"])

        assert isinstance(resp, CreateSuggestedPatchesResponse)
        assert len(resp.patches) == 1
        p = resp.patches[0]
        assert p.suggestion_id == "s_001"
        assert p.file_path == "backend/app/api/reviews.py"

    @pytest.mark.asyncio
    async def test_create_patches_unknown_suggestion(self, sample_report):
        llm = FallbackLLMClient()
        validator = PatchValidator()
        service = PatchSuggestionService(llm, validator)
        with pytest.raises(PatchServiceError, match="Unknown suggestion"):
            await service.create_patches(sample_report, ["nonexistent"])

    @pytest.mark.asyncio
    async def test_patch_fallback_returns_safe_output(self, sample_report):
        llm = FallbackLLMClient()
        validator = PatchValidator()
        service = PatchSuggestionService(llm, validator)
        resp = await service.create_patches(sample_report, ["s_001"])
        p = resp.patches[0]
        assert p.explanation
        assert "AI 生成" in p.safety_notes[0]
