"""AI Suggested Fix Preview — 数据模型"""
from typing import Literal

from pydantic import BaseModel, Field


class CreateSuggestedPatchesRequest(BaseModel):
    """生成修复预览请求"""
    suggestion_ids: list[str] = Field(min_length=1, max_length=5)


class SuggestedPatch(BaseModel):
    """单条修复预览"""
    id: str
    suggestion_id: str
    finding_id: str | None = None
    file_path: str
    start_line: int | None = None
    end_line: int | None = None
    patch_type: Literal["github_suggestion", "unified_diff", "none"] = "unified_diff"
    original_code: str | None = None
    suggested_code: str | None = None
    unified_diff: str | None = None
    github_suggestion: str | None = None
    explanation: str
    applicable: bool = False
    validation_warnings: list[str] = []
    safety_notes: list[str] = []


class CreateSuggestedPatchesResponse(BaseModel):
    """生成修复预览响应"""
    task_id: str
    patches: list[SuggestedPatch]
    warnings: list[str] = []
