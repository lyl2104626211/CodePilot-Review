"""上下文数据模型"""
from pydantic import BaseModel

from app.schemas.github import PullRequestSnapshot


class FileContext(BaseModel):
    """单个变更文件的上下文信息"""
    path: str                        # 文件路径
    module_type: str                 # 模块类型: backend/frontend/tests/config/docs/unknown
    status: str                      # 变更类型: added/modified/removed
    additions: int                   # 新增行数
    deletions: int                   # 删除行数
    patch: str | None = None         # unified diff 补丁
    content_excerpt: str | None = None  # 文件内容摘要（后续接入）
    related_test_paths: list[str] = []  # 关联的测试文件路径
    evidence_labels: list[str] = []     # 来源标签


class ReviewContext(BaseModel):
    """Review 分析的完整上下文"""
    pr: PullRequestSnapshot          # PR 元数据
    files: list[FileContext]         # 变更文件上下文列表
    warnings: list[str] = []         # 收集过程中的警告信息
