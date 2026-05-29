"""Fallback LLM Client 单元测试"""
import pytest

from app.llm.fallback import FallbackLLMClient


@pytest.fixture
def llm():
    return FallbackLLMClient()


class TestFallbackSummary:
    """Fallback Summary 生成测试"""

    @pytest.mark.asyncio
    async def test_summary_schema_valid(self, llm):
        result = await llm.generate_json("system", "user prompt about backend changes", "summary")
        assert "overview" in result
        assert "changed_modules" in result
        assert "reviewer_focus" in result
        assert len(result["overview"]) > 0
        assert len(result["changed_modules"]) > 0
        assert len(result["reviewer_focus"]) > 0

    @pytest.mark.asyncio
    async def test_summary_is_deterministic(self, llm):
        r1 = await llm.generate_json("system", "test prompt", "summary")
        r2 = await llm.generate_json("system", "test prompt", "summary")
        assert r1["overview"] == r2["overview"]


class TestFallbackFindings:
    """Fallback Findings 生成测试"""

    @pytest.mark.asyncio
    async def test_findings_schema_valid(self, llm):
        result = await llm.generate_json("system", "backend added new file", "risk_findings")
        assert "findings" in result
        assert isinstance(result["findings"], list)
        for f in result["findings"]:
            assert "id" in f
            assert "severity" in f
            assert "category" in f
            assert "title" in f
            assert "evidence" in f
            assert "confidence" in f

    @pytest.mark.asyncio
    async def test_findings_detect_missing_tests(self, llm):
        result = await llm.generate_json("system", "backend added modifications", "risk_findings")
        findings = result["findings"]
        assert len(findings) > 0

    @pytest.mark.asyncio
    async def test_findings_never_empty(self, llm):
        result = await llm.generate_json("system", "minor change", "risk_findings")
        assert len(result["findings"]) > 0


class TestFallbackSuggestions:
    """Fallback Suggestions 生成测试"""

    @pytest.mark.asyncio
    async def test_suggestions_schema_valid(self, llm):
        result = await llm.generate_json("system", "findings about missing tests", "suggestions")
        assert "suggestions" in result
        assert "test_recommendations" in result
        assert isinstance(result["suggestions"], list)
        assert len(result["suggestions"]) > 0
        for s in result["suggestions"]:
            assert "id" in s
            assert "comment" in s
            assert "rationale" in s
            assert "suggested_fix" in s
        assert len(result["test_recommendations"]) > 0
