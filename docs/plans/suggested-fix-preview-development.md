# CodePilot Review 增强功能开发文档：AI Suggested Fix Preview

## 1. 功能背景

CodePilot Review 当前已经具备 GitHub PR 获取、diff 上下文收集、LLM 结构化分析、风险识别、Review 建议生成和模拟 Review 评论能力。现阶段的问题是：AI 输出的建议仍然以文字为主，用户需要自己理解建议、定位代码、手动修改。对于简历项目来说，这已经能证明“会调用模型做分析”，但还不足以体现“能把 AI 输出转化为开发者可执行工作流”。

因此新增 **AI Suggested Fix Preview** 功能：系统在生成 Review 建议后，可以进一步针对某条建议生成局部代码修改方案，并以 diff 形式展示给用户。用户不需要马上接受修改，也不会自动改动仓库代码，而是先看到“修改前/修改后/差异预览”，再决定是否复制、参考或后续应用。

这个功能的核心价值：

- 让 Review 建议更具体，不停留在泛泛文字层面。
- 帮助开发者快速理解 AI 建议到底要怎么改。
- 展示项目对 LLM 输出可信度、patch 安全性和人工确认流程的考虑。
- 在简历中体现“AI + 工程工作流 + 代码 diff 处理”的能力。

## 2. 功能目标

### 2.1 第一阶段目标

第一阶段只实现 **Suggested Fix Diff Preview**，不自动修改本地文件，不自动提交代码，不自动推送分支。

完成后用户可以：

- 在 Review 建议列表中选择一条或多条建议。
- 点击“生成修复预览”。
- 后端根据 suggestion、finding、PR diff、文件上下文调用 LLM 生成局部修复方案。
- 系统返回原始代码片段、建议代码片段和 unified diff。
- 前端展示 diff 预览。
- 用户可以复制 GitHub Suggestion 格式或复制 unified diff。
- 系统明确提示“该修复由 AI 生成，需要人工确认后应用”。

### 2.2 第二阶段目标

第二阶段增加 patch 安全校验：

- 校验 `original_code` 是否存在于当前文件内容中。
- 校验 patch 是否只修改 PR 涉及文件。
- 校验 patch 修改范围是否过大。
- 校验 patch 是否包含危险操作，比如删除整个文件、清空大段代码、修改环境变量或密钥文件。
- 输出 `applicable` 和 `validation_warnings`。

### 2.3 第三阶段目标

第三阶段可选实现 patch 应用到临时工作区：

- 用户确认后，把 patch 应用到临时目录。
- 后端生成真实 `git diff`。
- 用户复制 patch 或下载 `.patch` 文件。
- 暂不做自动 commit、push、创建 PR。

## 3. 非目标

本功能第一阶段不做以下内容：

- 不直接修改用户本地仓库文件。
- 不自动提交 commit。
- 不自动 push 到 GitHub。
- 不自动创建修复 PR。
- 不对整个项目做全量代码重写。
- 不保证 AI patch 一定可以直接应用。
- 不把所有 finding 都强制生成 patch。

这些能力可以作为后续扩展，但第一阶段重点是“可信的修复预览”和“可解释的 diff 展示”。

## 4. 推荐技术方案

推荐方案：**LLM 生成局部修复代码 + 后端生成 unified diff + 前端 diff 预览**。

流程：

```text
ReviewReport
  -> 用户选择 Suggestion
  -> PatchSuggestionService 收集 suggestion/finding/file context
  -> LLM 生成 original_code 和 suggested_code
  -> 后端用 difflib 生成 unified diff
  -> PatchValidator 做基础校验
  -> 前端展示 Diff Preview
```

不推荐让 LLM 直接生成完整 unified diff 作为唯一结果。原因是 LLM 直接写 diff 容易出现行号、上下文、`+/-` 格式错误。更稳的方式是让 LLM 输出结构化 JSON：

```json
{
  "file_path": "backend/app/services/review_service.py",
  "original_code": "...",
  "suggested_code": "...",
  "explanation": "..."
}
```

然后后端用确定性代码生成 diff。

## 5. 用户故事

### 用户故事 1：查看建议修复

作为开发者，我希望在看到 AI Review 建议后，可以进一步查看建议修改的代码 diff，这样我能更快判断这条建议是否值得采纳。

验收标准：

- 用户可以在 suggestion 上点击“生成修复预览”。
- 系统返回对应文件的修改前代码和修改后代码。
- 页面展示 diff。
- 页面明确显示该 patch 是 AI 生成的预览。

### 用户故事 2：复制 GitHub Suggestion

作为 Review 人，我希望可以复制 GitHub Suggestion 格式的代码块，这样我可以直接粘贴到 GitHub Review 评论里。

验收标准：

- 每个 patch 提供“复制 GitHub Suggestion”按钮。
- 复制内容格式类似：

```markdown
```suggestion
suggested code here
```
```

- 复制成功后有反馈。
- 复制失败时提示手动复制。

### 用户故事 3：复制 unified diff

作为开发者，我希望可以复制 unified diff，这样我可以保存 patch 或在其他工具里查看。

验收标准：

- 每个 patch 提供“复制 Diff”按钮。
- 复制内容包含 `---`、`+++`、`@@`、`+`、`-`。
- diff 只包含目标文件的局部修改。

### 用户故事 4：识别不可应用 patch

作为开发者，我希望系统告诉我 AI 生成的 patch 是否可能无法直接应用，避免我盲目复制错误修改。

验收标准：

- 如果找不到 `original_code`，`applicable=false`。
- 如果 patch 修改范围过大，显示 warning。
- 如果目标文件不是 PR changed file，显示 warning。
- 不可应用 patch 仍可预览，但不能标记为“可直接应用”。

## 6. 后端架构设计

### 6.1 新增目录结构

```text
backend/
├── app/
│   ├── schemas/
│   │   └── patch.py
│   ├── services/
│   │   ├── patch_suggestion_service.py
│   │   └── patch_validator.py
│   ├── llm/
│   │   └── prompts.py
│   └── api/
│       └── reviews.py
└── tests/
    ├── test_patch_suggestion_service.py
    ├── test_patch_validator.py
    └── test_suggested_patches_api.py
```

### 6.2 数据模型

文件：`backend/app/schemas/patch.py`

```python
from typing import Literal
from pydantic import BaseModel, Field


class CreateSuggestedPatchesRequest(BaseModel):
    suggestion_ids: list[str] = Field(min_length=1, max_length=5)


class SuggestedPatch(BaseModel):
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
    task_id: str
    patches: list[SuggestedPatch]
    warnings: list[str] = []
```

### 6.3 字段说明

| 字段 | 说明 |
| --- | --- |
| `suggestion_id` | 用户选择的 Review 建议 ID |
| `finding_id` | 关联的风险 ID，可为空 |
| `file_path` | 建议修改的文件 |
| `start_line/end_line` | 建议修改的大致行号 |
| `original_code` | 原始代码片段 |
| `suggested_code` | 建议修改后的代码片段 |
| `unified_diff` | 后端生成的 diff |
| `github_suggestion` | 可复制到 GitHub Review 的 suggestion block |
| `explanation` | 为什么这样改 |
| `applicable` | 是否可能可以应用 |
| `validation_warnings` | 校验警告 |
| `safety_notes` | 安全提示 |

## 7. API 设计

### 7.1 生成 Suggested Patches

```http
POST /api/reviews/{task_id}/suggested-patches
Content-Type: application/json
```

请求：

```json
{
  "suggestion_ids": ["suggestion_001"]
}
```

响应：

```json
{
  "task_id": "task_xxx",
  "patches": [
    {
      "id": "patch_001",
      "suggestion_id": "suggestion_001",
      "finding_id": "risk_001",
      "file_path": "backend/app/services/review_service.py",
      "start_line": 42,
      "end_line": 55,
      "patch_type": "unified_diff",
      "original_code": "result = await graph.ainvoke(state)",
      "suggested_code": "try:\n    result = await graph.ainvoke(state)\nexcept Exception as exc:\n    task.status = \"failed\"\n    task.error_message = str(exc)\n    raise",
      "unified_diff": "--- backend/app/services/review_service.py\n+++ backend/app/services/review_service.py\n@@ -1 +1,6 @@\n-result = await graph.ainvoke(state)\n+try:\n+    result = await graph.ainvoke(state)\n+except Exception as exc:\n+    task.status = \"failed\"\n+    task.error_message = str(exc)\n+    raise",
      "github_suggestion": "```suggestion\ntry:\n    result = await graph.ainvoke(state)\nexcept Exception as exc:\n    task.status = \"failed\"\n    task.error_message = str(exc)\n    raise\n```",
      "explanation": "为任务执行增加异常捕获，避免失败时任务状态停留在 running。",
      "applicable": true,
      "validation_warnings": [],
      "safety_notes": ["AI 生成的修复建议需要人工确认后应用。"]
    }
  ],
  "warnings": []
}
```

### 7.2 错误响应

| 场景 | HTTP 状态码 | 说明 |
| --- | --- | --- |
| task 不存在 | 404 | `Review task not found.` |
| report 未生成 | 409 | `Review report is not ready.` |
| suggestion_ids 为空 | 422 | Pydantic 校验失败 |
| suggestion_id 不存在 | 422 | `Unknown suggestion id.` |
| suggestion 没有关联文件 | 422 或返回 `patch_type=none` | 无法生成代码 patch |
| LLM 失败 | 200 + warning 或 503 | 第一阶段建议 fallback 为 `patch_type=none` |

## 8. PatchSuggestionService 设计

文件：`backend/app/services/patch_suggestion_service.py`

核心职责：

- 根据 `task_id` 获取 `ReviewReport` 和 `ReviewContext`。
- 根据 `suggestion_ids` 找到对应 suggestion。
- 找到 suggestion 关联的 finding。
- 确定目标文件、行号、evidence 和上下文。
- 调用 LLM 生成结构化 patch proposal。
- 使用后端代码生成 unified diff。
- 调用 `PatchValidator` 做基础校验。
- 返回 `SuggestedPatch`。

核心函数：

```python
class PatchSuggestionService:
    def __init__(self, llm: LLMClient, validator: PatchValidator):
        self.llm = llm
        self.validator = validator

    async def create_patches(
        self,
        report: ReviewReport,
        review_context: ReviewContext | None,
        suggestion_ids: list[str],
    ) -> CreateSuggestedPatchesResponse:
        ...
```

处理逻辑：

```text
for suggestion_id in suggestion_ids:
  1. 查找 suggestion
  2. 查找关联 finding
  3. 判断是否有 file_path
  4. 找到对应 FileContext
  5. 构造 patch prompt
  6. LLM 返回 original_code / suggested_code
  7. difflib 生成 unified diff
  8. validator 校验可应用性
  9. 组装 SuggestedPatch
```

## 9. Prompt 设计

### 9.1 输入内容

Patch Prompt 应包含：

- PR 标题。
- 文件路径。
- Review suggestion。
- Risk finding。
- evidence。
- reasoning。
- 原始 patch。
- 文件上下文片段。
- 约束规则。

### 9.2 Prompt 要求

LLM 必须输出 JSON：

```json
{
  "file_path": "string",
  "start_line": 1,
  "end_line": 10,
  "original_code": "string",
  "suggested_code": "string",
  "explanation": "string"
}
```

约束：

- 只修改与 suggestion 直接相关的代码。
- 不重写整个文件。
- 不引入未出现过的新框架。
- 不删除无关逻辑。
- 不修改密钥、环境变量、锁文件。
- 如果无法给出可靠 patch，返回空 `original_code` 和 `suggested_code`，并在 explanation 中说明原因。

### 9.3 Prompt 模板

```text
你是一个谨慎的代码评审助手。请基于 PR diff 和上下文，为指定 Review 建议生成一个最小范围的代码修复预览。

要求：
1. 只修改与建议直接相关的代码。
2. 不重写整个文件。
3. 不编造不存在的 API。
4. 如果上下文不足以生成可靠代码，返回空 original_code 和 suggested_code，并说明原因。
5. 输出必须是 JSON。

PR 标题：
{pr_title}

目标文件：
{file_path}

Review 建议：
{suggestion.comment}

建议原因：
{suggestion.rationale}

建议修复：
{suggestion.suggested_fix}

风险证据：
{finding.evidence}

风险推理：
{finding.reasoning}

相关 diff：
{file_context.patch}

文件上下文：
{file_context.content_excerpt}

输出 JSON schema：
{
  "file_path": "string",
  "start_line": number | null,
  "end_line": number | null,
  "original_code": "string",
  "suggested_code": "string",
  "explanation": "string"
}
```

## 10. Diff 生成设计

后端不要完全依赖 LLM 生成 diff，而是使用 Python 标准库 `difflib`。

核心函数：

```python
import difflib


def build_unified_diff(file_path: str, original_code: str, suggested_code: str) -> str:
    original_lines = original_code.splitlines(keepends=True)
    suggested_lines = suggested_code.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            original_lines,
            suggested_lines,
            fromfile=file_path,
            tofile=file_path,
            lineterm="",
        )
    )
```

GitHub Suggestion 生成：

```python
def build_github_suggestion(suggested_code: str) -> str:
    return f"```suggestion\n{suggested_code.rstrip()}\n```"
```

注意：

- `unified_diff` 仅用于展示，不表示一定可以直接 `git apply`。
- 第一阶段不需要行号完全精准。
- 第二阶段再增强 patch 可应用性校验。

## 11. PatchValidator 设计

文件：`backend/app/services/patch_validator.py`

第一阶段基础校验：

```python
class PatchValidator:
    def validate(
        self,
        patch: SuggestedPatch,
        file_context: FileContext | None,
        changed_file_paths: set[str],
    ) -> SuggestedPatch:
        ...
```

校验规则：

- `file_path` 必须在 PR changed files 中。
- `original_code` 和 `suggested_code` 都不能为空。
- `original_code` 不应等于 `suggested_code`。
- 如果有 `content_excerpt`，检查 `original_code` 是否出现在其中。
- 修改行数不超过 80 行。
- 不允许修改 `.env`、lock 文件、图片、二进制文件。
- 不允许 suggested_code 为空但 original_code 不为空。

返回：

- 所有校验通过：`applicable=true`。
- 有警告但仍可展示：`applicable=false`，写入 `validation_warnings`。
- 严重问题：`patch_type=none`，只返回 explanation。

## 12. 前端设计

### 12.1 新增组件

```text
frontend/src/components/
├── SuggestedPatchPanel.vue
├── DiffViewer.vue
└── PatchActions.vue
```

### 12.2 `SuggestedPatchPanel.vue`

职责：

- 接收 suggestions。
- 允许用户选择一条或多条 suggestion。
- 调用 `createSuggestedPatches`。
- 展示 patch 生成状态。
- 渲染 `DiffViewer`。

Props：

```ts
taskId: string
suggestions: ReviewSuggestion[]
```

状态：

```ts
const selectedSuggestionIds = ref<string[]>([])
const patches = ref<SuggestedPatch[]>([])
const loading = ref(false)
const error = ref('')
```

交互：

- 每条 suggestion 上有复选框。
- 按钮：`生成修复预览`。
- 未选择 suggestion 时按钮禁用。
- patch 生成中展示 loading。
- patch 生成失败展示错误。

### 12.3 `DiffViewer.vue`

职责：

- 展示 unified diff。
- 对新增行、删除行、上下文行做颜色区分。
- 展示文件路径和 applicable 状态。

简单渲染规则：

```ts
function getLineClass(line: string) {
  if (line.startsWith('+') && !line.startsWith('+++')) return 'added'
  if (line.startsWith('-') && !line.startsWith('---')) return 'removed'
  if (line.startsWith('@@')) return 'hunk'
  return 'context'
}
```

展示状态：

- `applicable=true`：显示“可能可应用”。
- `applicable=false`：显示“仅供参考”。
- 有 `validation_warnings`：显示 warning 列表。

### 12.4 `PatchActions.vue`

职责：

- 复制 GitHub Suggestion。
- 复制 Unified Diff。
- 复制 suggested code。

错误处理：

- Clipboard API 不可用时提示手动复制。
- 复制成功显示短暂提示。

## 13. 前端 API 类型

文件：`frontend/src/types/review.ts` 或新增 `frontend/src/types/patch.ts`

```ts
export interface SuggestedPatch {
  id: string
  suggestion_id: string
  finding_id?: string
  file_path: string
  start_line?: number
  end_line?: number
  patch_type: 'github_suggestion' | 'unified_diff' | 'none'
  original_code?: string
  suggested_code?: string
  unified_diff?: string
  github_suggestion?: string
  explanation: string
  applicable: boolean
  validation_warnings: string[]
  safety_notes: string[]
}

export interface CreateSuggestedPatchesResponse {
  task_id: string
  patches: SuggestedPatch[]
  warnings: string[]
}
```

API：

```ts
export async function createSuggestedPatches(
  taskId: string,
  suggestionIds: string[],
): Promise<CreateSuggestedPatchesResponse> {
  const response = await fetch(`/api/reviews/${taskId}/suggested-patches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ suggestion_ids: suggestionIds }),
  })
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}
```

## 14. 与现有模块的关系

### 14.1 与 ReviewSuggestion 的关系

`ReviewSuggestion` 仍然是文字建议的主模型。`SuggestedPatch` 是它的增强结果。

```text
ReviewSuggestion
  -> SuggestedPatch
```

不是每条 suggestion 都必须有 patch。例如：

- 文档建议可以生成 patch。
- 测试建议可能只返回 explanation。
- 架构建议可能不适合生成具体代码 patch。

### 14.2 与 LangGraph 的关系

第一阶段不把 patch 生成放入主 Review Graph。

原因：

- Review Graph 负责自动分析。
- Suggested Patch 依赖用户选择，是交互式后续动作。
- 避免每次分析都生成大量 patch，拖慢响应速度。

结构：

```text
Review Graph
  -> ReviewReport
  -> User selects suggestions
  -> PatchSuggestionService
  -> SuggestedPatch[]
```

后续如果要做自动修复 Agent，可以单独建一个 Fix Graph：

```text
select_suggestion
  -> collect_patch_context
  -> generate_patch
  -> validate_patch
  -> preview_patch
```

## 15. 实现顺序

### Step 1：新增 Patch Schema

输出：

- `backend/app/schemas/patch.py`

验收：

- `CreateSuggestedPatchesRequest` 校验 suggestion 数量。
- `SuggestedPatch` 字段完整。
- `CreateSuggestedPatchesResponse` 可序列化。

### Step 2：实现 Diff Builder

输出：

- `backend/app/services/patch_suggestion_service.py`
- `build_unified_diff`
- `build_github_suggestion`

验收：

- 输入 original/suggested code 能生成 unified diff。
- 输入 suggested code 能生成 GitHub suggestion block。
- 单元测试覆盖新增、删除、替换三种情况。

### Step 3：实现 PatchValidator

输出：

- `backend/app/services/patch_validator.py`
- `backend/tests/test_patch_validator.py`

验收：

- 目标文件不在 changed files 中会 warning。
- original_code 找不到会 `applicable=false`。
- suggested_code 为空会 `applicable=false`。
- 修改范围过大会 warning。

### Step 4：实现 PatchSuggestionService

输出：

- `PatchSuggestionService.create_patches`
- LLM prompt
- fallback 行为

验收：

- 能根据 suggestion 生成 patch。
- suggestion 不存在返回错误。
- suggestion 没有 file_path 时返回 `patch_type=none`。
- LLM 失败时不影响原始 ReviewReport。

### Step 5：新增后端 API

输出：

- `POST /api/reviews/{task_id}/suggested-patches`
- `backend/tests/test_suggested_patches_api.py`

验收：

- task 不存在返回 404。
- report 未完成返回 409。
- suggestion_ids 为空返回 422。
- 成功返回 patches。

### Step 6：前端 API 和类型

输出：

- `frontend/src/types/patch.ts`
- `frontend/src/api/reviews.ts`

验收：

- TypeScript 类型通过。
- API 错误能展示。

### Step 7：前端 Diff 展示

输出：

- `SuggestedPatchPanel.vue`
- `DiffViewer.vue`
- `PatchActions.vue`
- 更新 `App.vue`

验收：

- 用户可以选择 suggestion。
- 可以生成 patch preview。
- 可以复制 GitHub Suggestion。
- 可以复制 unified diff。
- diff 样式区分新增/删除/上下文。

### Step 8：补充 README 和简历说明

输出：

- README 增加 AI Suggested Fix Preview 说明。
- `docs/plans/suggested-fix-preview-development.md`
- 可选：`docs/resume-project-notes.md`

验收：

- README 说明该功能不会自动修改代码。
- README 说明 patch 需要人工确认。
- 简历描述突出 diff preview 和 patch validation。

## 16. 测试计划

### 16.1 后端测试

`test_patch_suggestion_service.py`

- 正常 suggestion 生成 patch。
- LLM 返回空代码时生成 `patch_type=none`。
- unknown suggestion id 报错。
- 生成 GitHub suggestion block。
- 生成 unified diff。

`test_patch_validator.py`

- changed file 校验。
- original_code 存在校验。
- 修改范围校验。
- forbidden file 校验。
- applicable 状态校验。

`test_suggested_patches_api.py`

- API 成功返回 patches。
- task 不存在返回 404。
- report 未完成返回 409。
- 空 suggestion_ids 返回 422。

### 16.2 前端检查

必须通过：

```bash
cd frontend
npm run typecheck
npm run build
```

手动验收：

- 分析一个 Demo PR。
- 选择一条 suggestion。
- 生成 patch preview。
- 复制 GitHub Suggestion。
- 复制 unified diff。
- 验证不可应用 patch 有 warning。

## 17. 风险与控制

| 风险 | 控制方式 |
| --- | --- |
| LLM 生成不存在的代码 | validator 校验 original_code 是否出现在上下文中 |
| patch 修改范围过大 | 限制最大修改行数 |
| patch 误改无关文件 | 限制 file_path 必须在 changed files 中 |
| 用户以为系统已改代码 | UI 明确标注“预览，不会自动修改” |
| LLM 输出 JSON 格式错误 | Pydantic 校验，失败返回 patch_type=none |
| 生成速度慢 | 用户选择后按需生成，不放入主 Review 流程 |

## 18. 完成标准

第一阶段完成标准：

- 后端有 `POST /api/reviews/{task_id}/suggested-patches`。
- 能根据 suggestion 生成 `SuggestedPatch`。
- 能生成 unified diff。
- 能生成 GitHub Suggestion block。
- 前端能展示 diff preview。
- 前端能复制 suggestion/diff。
- 不会自动修改本地文件。
- README 明确说明该功能是 AI 修复预览。
- 后端测试、前端 typecheck、前端 build 通过。

## 19. 简历表述建议

可以写成：

```text
实现 AI Suggested Fix Preview：基于 PR diff、风险证据和 Review 建议生成局部修复代码片段，由后端使用 difflib 生成 unified diff，并在前端提供 GitHub Suggestion/Unified Diff 预览与复制；设计 PatchValidator 校验目标文件、原始代码匹配和修改范围，降低 LLM 幻觉和误改风险。
```

也可以压缩成一条：

```text
实现 AI 修复建议 Diff 预览能力，将模型生成的 Review 建议转化为可复制的 GitHub Suggestion 和 Unified Diff，并通过 patch 校验降低误改风险。
```

## 20. 后续扩展

后续可以继续扩展：

- 临时工作区应用 patch。
- 下载 `.patch` 文件。
- 一键创建修复分支。
- 人工确认后提交 commit。
- 创建修复 PR。
- 多模型 patch 交叉验证。
- 引入 tree-sitter 做函数级上下文定位。

