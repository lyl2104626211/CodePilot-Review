"""PatchValidator 单元测试"""
import pytest
from app.schemas.patch import SuggestedPatch
from app.services.patch_validator import PatchValidator


def make_patch(file_path="backend/app/api/reviews.py", original="result = await graph.ainvoke(state)",
               suggested="try:\n    result = await graph.ainvoke(state)\nexcept Exception as exc:\n    pass"):
    return SuggestedPatch(
        id="patch_001", suggestion_id="s_001", finding_id="risk_001",
        file_path=file_path, start_line=10, end_line=12,
        original_code=original, suggested_code=suggested,
        explanation="Add error handling", applicable=True,
    )


class TestPatchValidator:
    def test_file_in_changed_files(self):
        v = PatchValidator()
        p = make_patch()
        result = v.validate(p, {"backend/app/api/reviews.py"})
        assert result.applicable is True

    def test_file_not_in_changed_files(self):
        v = PatchValidator()
        p = make_patch(file_path="frontend/src/App.vue")
        result = v.validate(p, {"backend/app/api/reviews.py"})
        assert result.applicable is False
        assert any("不在 PR 变更文件列表" in w for w in result.validation_warnings)

    def test_empty_original_code(self):
        v = PatchValidator()
        p = make_patch(original="")
        result = v.validate(p, {"backend/app/api/reviews.py"})
        assert result.applicable is False

    def test_same_code_no_change(self):
        v = PatchValidator()
        p = make_patch(suggested="result = await graph.ainvoke(state)")
        result = v.validate(p, {"backend/app/api/reviews.py"})
        assert result.applicable is False

    def test_modification_too_large(self):
        v = PatchValidator()
        big_code = "\n".join(f"line_{i}" for i in range(100))
        p = make_patch(original=big_code, suggested=big_code + "\nnew_line")
        result = v.validate(p, {"backend/app/api/reviews.py"})
        assert any("修改范围过大" in w for w in result.validation_warnings)

    def test_forbidden_env_file(self):
        v = PatchValidator()
        p = make_patch(file_path=".env")
        result = v.validate(p, {".env"})
        assert result.applicable is False
        assert any(".env" in w for w in result.validation_warnings)

    def test_forbidden_lock_file(self):
        v = PatchValidator()
        p = make_patch(file_path="uv.lock")
        result = v.validate(p, {"uv.lock"})
        assert result.applicable is False

    def test_original_code_not_in_excerpt(self):
        v = PatchValidator()
        p = make_patch(original="some_unrelated_code")
        result = v.validate(p, {"backend/app/api/reviews.py"}, content_excerpt="def foo(): pass")
        assert result.applicable is False
