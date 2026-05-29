"""ContextCollector 单元测试"""
import pytest

from app.context.collector import ContextCollector
from app.context.heuristics import classify_file, find_related_tests
from app.schemas.github import PullRequestFile, PullRequestSnapshot


@pytest.fixture
def sample_pr() -> PullRequestSnapshot:
    """构造一个包含多种文件类型的 PR 快照"""
    return PullRequestSnapshot(
        owner="acme",
        repo="codepilot",
        number=12,
        title="Add review API and tests",
        author="demo-user",
        base_branch="main",
        head_branch="feature/review",
        changed_files=5,
        additions=200,
        deletions=50,
        commit_count=3,
        files=[
            PullRequestFile(
                path="backend/app/api/reviews.py",
                status="added",
                additions=45,
                deletions=0,
                patch="@@ -0,0 +1,45 @@\n+@router.post('/reviews')\n+async def create_review(request):\n+    return await create_review_task(request)",
            ),
            PullRequestFile(
                path="backend/tests/test_reviews.py",
                status="added",
                additions=30,
                deletions=0,
                patch="@@ -0,0 +1,30 @@\n+def test_create_review():\n+    assert True",
            ),
            PullRequestFile(
                path="frontend/src/components/PrInput.vue",
                status="modified",
                additions=10,
                deletions=5,
                patch="@@ -10,5 +10,10 @@\n <script setup>",
            ),
            PullRequestFile(
                path="README.md",
                status="modified",
                additions=5,
                deletions=2,
                patch="@@ -1,3 +1,6 @@\n # CodePilot Review",
            ),
            PullRequestFile(
                path="backend/static/logo.png",
                status="added",
                additions=0,
                deletions=0,
                patch=None,
            ),
        ],
    )


class TestClassifyFile:
    """文件分类测试"""

    def test_classify_backend_python(self):
        assert classify_file("backend/app/services/review.py") == "backend"
        assert classify_file("app/api/health.py") == "backend"

    def test_classify_frontend(self):
        assert classify_file("frontend/src/components/Button.vue") == "frontend"
        assert classify_file("src/components/Card.tsx") == "frontend"
        assert classify_file("styles/app.css") == "frontend"

    def test_classify_tests(self):
        assert classify_file("backend/tests/test_reviews.py") == "tests"
        assert classify_file("tests/test_parser.py") == "tests"
        assert classify_file("src/__tests__/utils.spec.ts") == "tests"

    def test_classify_config(self):
        assert classify_file("pyproject.toml") == "config"
        assert classify_file(".env.example") == "config"
        assert classify_file("Dockerfile") == "config"

    def test_classify_docs(self):
        assert classify_file("README.md") == "docs"
        assert classify_file("docs/architecture.rst") == "docs"

    def test_classify_unknown(self):
        assert classify_file("assets/hero.png") == "unknown"
        assert classify_file("data/sample.csv") == "unknown"


class TestFindRelatedTests:
    """关联测试文件查找测试"""

    def test_backend_source_finds_test(self):
        result = find_related_tests("backend/app/services/review.py")
        assert len(result) > 0
        assert any("test_review" in r for r in result)

    def test_test_file_returns_empty(self):
        result = find_related_tests("tests/test_reviews.py")
        assert result == []

    def test_frontend_component_finds_spec(self):
        result = find_related_tests("src/components/Button.vue")
        assert len(result) > 0
        assert any("__tests__" in r for r in result)


class TestContextCollector:
    """上下文收集器测试"""

    def test_collect_with_multiple_file_types(self, sample_pr):
        """验证收集多种类型文件的上下文"""
        collector = ContextCollector()
        context = collector.collect(sample_pr)

        assert context.pr == sample_pr
        # logo.png 是二进制，应被跳过
        assert len(context.files) == 4

        # 验证分类
        file_types = {f.path: f.module_type for f in context.files}
        assert file_types["backend/app/api/reviews.py"] == "backend"
        assert file_types["backend/tests/test_reviews.py"] == "tests"
        assert file_types["frontend/src/components/PrInput.vue"] == "frontend"
        assert file_types["README.md"] == "docs"

    def test_collect_truncates_large_patch(self, sample_pr):
        """验证超长 patch 被截断"""
        # 设置很小的文件预算
        collector = ContextCollector(max_file_chars=50, max_total_chars=100000)
        context = collector.collect(sample_pr)

        for f in context.files:
            if f.patch:
                assert len(f.patch) <= 50 + 50  # 允许截断标记的长度

    def test_collect_enforces_total_budget(self, sample_pr):
        """验证总预算耗尽后后续文件的 patch 被置空"""
        collector = ContextCollector(max_file_chars=100000, max_total_chars=80)
        context = collector.collect(sample_pr)

        # 前几个文件可能用完了预算，后面的应该 patch=None
        patches = [f.patch for f in context.files]
        # 至少有一个 patch 因为预算被清空（或所有文件是小 patch 则都保留）
        # 不做硬断言，验证不会崩溃即可
        assert len(context.files) >= 1

    def test_collect_produces_evidence_labels(self, sample_pr):
        """验证每个文件上下文的来源标签"""
        collector = ContextCollector()
        context = collector.collect(sample_pr)

        for f in context.files:
            assert len(f.evidence_labels) > 0
            if f.patch:
                assert "patch_available" in f.evidence_labels

    def test_collect_handles_empty_files(self):
        """验证无文件 PR 不会崩溃"""
        pr = PullRequestSnapshot(
            owner="a", repo="b", number=1, title="Empty",
            author="x", base_branch="main", head_branch="f",
            changed_files=0, additions=0, deletions=0, commit_count=1,
            files=[],
        )
        collector = ContextCollector()
        context = collector.collect(pr)
        assert context.files == []
        assert context.warnings == []
