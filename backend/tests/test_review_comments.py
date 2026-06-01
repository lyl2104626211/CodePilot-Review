"""模拟 Review 评论测试"""
import pytest

from app.schemas.common import RiskCategory, RiskSeverity, TaskStatus
from app.schemas.github import PullRequestSnapshot
from app.schemas.review import (
    CreateReviewCommentsRequest,
    ReviewCommentDraft,
    ReviewReport,
    ReviewSummary,
    ReviewSuggestion,
    RiskFinding,
)
from app.services.review_comment_service import (
    CommentServiceError,
    create_review_comment_drafts,
    get_report_quality,
)


@pytest.fixture
def sample_report():
    """构造一个包含 findings 和 suggestions 的测试报告"""
    return ReviewReport(
        task_id="test_task",
        status=TaskStatus.succeeded,
        pr=PullRequestSnapshot(
            owner="a", repo="b", number=1, title="Test PR",
            author="x", base_branch="main", head_branch="f",
            changed_files=1, additions=10, deletions=2, commit_count=1, files=[],
        ),
        summary=ReviewSummary(
            overview="Test summary",
            changed_modules=["backend"],
            reviewer_focus=["error handling"],
        ),
        findings=[
            RiskFinding(id="risk_001", severity=RiskSeverity.medium, category=RiskCategory.correctness,
                        file_path="a.py", line=10, title="Missing error check",
                        evidence="no try/except", reasoning="may crash", confidence=0.8),
            RiskFinding(id="risk_002", severity=RiskSeverity.low, category=RiskCategory.observability,
                        file_path="b.py", line=None, title="No logging",
                        evidence="no log calls", reasoning="hard to debug", confidence=0.3),
        ],
        suggestions=[
            ReviewSuggestion(id="s_001", finding_id="risk_001", file_path="a.py",
                             comment="Add try/except", rationale="prevent crash",
                             suggested_fix="wrap in try/except", blocking=True),
            ReviewSuggestion(id="s_002", finding_id="risk_002", file_path="b.py",
                             comment="Add logging", rationale="improve debugging",
                             suggested_fix="add log calls", blocking=False),
        ],
        test_recommendations=["Test error path", "Test logging output"],
    )


class TestCommentGeneration:
    """评论生成测试"""

    def test_generate_with_valid_selection(self, sample_report):
        req = CreateReviewCommentsRequest(suggestion_ids=["s_001"])
        resp = create_review_comment_drafts(sample_report, req)
        assert len(resp.comments) == 1
        assert resp.comments[0].suggestion_id == "s_001"
        assert resp.comments[0].blocking is True
        assert "try/except" in resp.comments[0].body
        assert "CodePilot Review" in resp.markdown

    def test_generate_multiple_suggestions(self, sample_report):
        req = CreateReviewCommentsRequest(suggestion_ids=["s_001", "s_002"])
        resp = create_review_comment_drafts(sample_report, req)
        assert len(resp.comments) == 2
        assert resp.comments[0].blocking is True
        assert resp.comments[1].blocking is False

    def test_empty_selection_raises(self, sample_report):
        req = CreateReviewCommentsRequest(suggestion_ids=[])
        with pytest.raises(CommentServiceError, match="At least one suggestion"):
            create_review_comment_drafts(sample_report, req)

    def test_unknown_suggestion_raises(self, sample_report):
        req = CreateReviewCommentsRequest(suggestion_ids=["nonexistent"])
        with pytest.raises(CommentServiceError, match="Unknown suggestion"):
            create_review_comment_drafts(sample_report, req)

    def test_blocking_suggestion_tagged(self, sample_report):
        req = CreateReviewCommentsRequest(suggestion_ids=["s_001"])
        resp = create_review_comment_drafts(sample_report, req)
        assert resp.comments[0].blocking is True
        assert "阻塞合并" in resp.markdown

    def test_markdown_includes_summary(self, sample_report):
        req = CreateReviewCommentsRequest(suggestion_ids=["s_001"], include_summary=True)
        resp = create_review_comment_drafts(sample_report, req)
        assert "Test summary" in resp.markdown

    def test_markdown_includes_test_recs(self, sample_report):
        req = CreateReviewCommentsRequest(suggestion_ids=["s_001"], include_test_recommendations=True)
        resp = create_review_comment_drafts(sample_report, req)
        assert "Test error path" in resp.markdown

    def test_markdown_excludes_summary_when_disabled(self, sample_report):
        req = CreateReviewCommentsRequest(suggestion_ids=["s_001"], include_summary=False)
        resp = create_review_comment_drafts(sample_report, req)
        assert "Test summary" not in resp.markdown


class TestReportQuality:
    """质量摘要测试"""

    def test_quality_summary(self, sample_report):
        q = get_report_quality(sample_report)
        assert q["total_findings"] == 2
        assert q["high_confidence_findings"] == 1
        assert q["low_confidence_findings"] == 1
        assert q["blocking_suggestions"] == 1

    def test_quality_empty_report(self):
        empty = ReviewReport(task_id="t", status=TaskStatus.succeeded)
        q = get_report_quality(empty)
        assert q["total_findings"] == 0
        assert q["high_confidence_findings"] == 0
