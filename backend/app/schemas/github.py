from pydantic import BaseModel, HttpUrl


class ParsedPullRequest(BaseModel):
    """解析后的 PR 标识信息"""
    owner: str       # 仓库所有者
    repo: str        # 仓库名
    number: int      # PR 编号
    url: HttpUrl     # 原始 URL，Pydantic HttpUrl 自动校验格式


class PullRequestFile(BaseModel):
    """PR 中单个变更文件"""
    path: str                # 文件路径
    status: str              # 变更类型：added / modified / removed
    additions: int           # 新增行数
    deletions: int           # 删除行数
    patch: str | None = None # unified diff 补丁内容，可能为空


class PullRequestSnapshot(BaseModel):
    """PR 完整快照：元数据 + 文件列表"""
    owner: str
    repo: str
    number: int
    title: str               # PR 标题
    author: str              # 提交者
    base_branch: str         # 目标分支
    head_branch: str         # 源分支
    changed_files: int       # 变更文件数
    additions: int           # 总新增行数
    deletions: int           # 总删除行数
    commit_count: int        # 提交数
    files: list[PullRequestFile]
