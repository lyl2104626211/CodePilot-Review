# CodePilot Review 第 3 天详细开发文档

## 1. 第 3 天目标

第 3 天目标是在第 2 天“可分析真实 GitHub PR”的基础上，把项目打磨成一个适合最终展示和答辩的完整作品。重点不再是继续堆复杂模型能力，而是补齐用户闭环：用户能看到清晰的分析进度，能理解每条风险的证据来源，能选择建议并生成 GitHub 风格的模拟 Review 评论，能复制或导出评论内容，并且 README、进度文档、Demo 脚本和验收材料完整。

第 3 天完成后，项目应具备以下能力：

- 后端支持任务进度查询，前端能展示更细的分析状态。
- 用户可以从 AI 生成的建议中勾选要采纳的项。
- 系统可以把建议转换成 GitHub Review 风格的模拟评论。
- 评论支持复制、预览和导出，暂不真实提交到 GitHub。
- 前端补齐空状态、错误状态、加载状态、warnings 和报告质量说明。
- 后端增加报告质量评分或置信度摘要，辅助降低误报观感。
- README 最终版包含项目介绍、功能说明、架构图、启动步骤、环境变量、Demo 流程、PR 记录和依赖声明。
- `PROGRESS.md` 更新 Day3 完成项。
- 所有后端测试、前端 typecheck 和 build 通过。
- 最终演示链路稳定：Demo 模式必定可用，GitHub 模式可分析公开 PR。

## 2. 第 3 天范围

### 2.1 必须完成

- 任务状态和进度 API 完善。
- 前端进度展示体验增强。
- Review 建议选择功能。
- GitHub 风格模拟 Review 评论生成。
- Review 评论复制和导出。
- 报告质量护栏展示，包括 warnings、低置信度说明、fallback 说明。
- 前端页面最终打磨，包括移动端基础适配。
- README 最终版。
- PROGRESS 更新 Day3 状态和 PR 记录。
- Demo 脚本和最终验收清单。
- 后端和前端测试检查。

### 2.2 可选完成

- SSE 实时进度流。
- 报告 Markdown 导出。
- 简单历史记录列表。
- GitHub 真实评论发布开关。

如果时间紧，优先完成“模拟 Review 评论”和“最终交付材料”。真实发布 GitHub Review 评论有权限和误操作风险，可以不做，或只保留架构设计说明。

### 2.3 不建议完成

- 多用户登录。
- 数据库持久化。
- 企业级规则配置中心。
- 复杂 AST 调用链分析。
- 自动 merge、自动 approve、自动提交真实 review。

这些功能会拉长实现时间，也不是三天作品的核心验收点。

## 3. 第 3 天推荐方案

推荐采用“稳定演示优先”的收尾方案：

```text
真实 PR 分析能力
  -> 进度和质量说明
  -> 用户选择建议
  -> 生成模拟 GitHub Review 评论
  -> 复制/导出
  -> README + Demo 完成交付
```

这个方案的优势：

- 直接对应题目要求里的“Review 建议生成”和“使用体验”。
- 避免真实 GitHub 评论发布带来的 Token 权限、误发评论、接口限制等风险。
- 能让评委看到完整产品闭环，而不是只看到模型输出列表。
- 便于答辩解释：当前实现模拟发布，后续可扩展为真实 GitHub Review API。

备选方案：

| 方案 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- |
| 做真实 GitHub Review 发布 | 产品闭环更真实 | Token 权限高，误操作风险大，测试复杂 | 不推荐 Day3 必做 |
| 只继续优化 LLM Prompt | 实现简单 | 用户体验变化不明显 | 只能作为辅助 |
| 模拟 Review 评论 + 交付打磨 | 稳定、可展示、贴合题目 | 真实发布能力暂缺 | 推荐 |

## 4. Day3 目录结构增量

后端增量：

```text
backend/
├── app/
│   ├── schemas/
│   │   └── review.py                 # 增加 Review comment/selection 模型
│   ├── services/
│   │   ├── review_comment_service.py # 模拟 Review 评论生成服务
│   │   └── review_quality.py         # 报告质量摘要和展示用指标
│   ├── api/
│   │   └── reviews.py                # 增加 status/comments/export 接口
│   └── storage/
│       └── memory_store.py           # 保存 selected suggestions/comment drafts
└── tests/
    ├── test_review_comments.py
    ├── test_review_status.py
    └── test_review_export.py
```

前端增量：

```text
frontend/src/
├── components/
│   ├── ReviewCommentComposer.vue     # 建议选择和评论生成
│   ├── ReviewCommentPreview.vue      # GitHub 风格评论预览
│   ├── ReportQualityPanel.vue        # warnings/置信度/fallback 说明
│   ├── EmptyState.vue                # 空状态
│   └── ErrorState.vue                # 错误状态
├── api/
│   └── reviews.ts                    # 增加 status/comment/export API
└── types/
    └── review.ts                     # 增加 comment/status/export 类型
```

文档增量：

```text
docs/
├── plans/
│   └── day3-development.md
├── demo-script.md                    # 最终演示脚本
└── final-checklist.md                # 提交前验收清单
```

## 5. 后端功能设计

### 5.1 任务状态 API

第 2 天已经有基础状态和 warnings，Day3 需要把状态查询变成前端稳定可用的接口。

接口：

```http
GET /api/reviews/{task_id}/status
```

响应：

```json
{
  "task_id": "task_xxx",
  "status": "succeeded",
  "current_node": "assemble_report",
  "progress_events": [
    {
      "node": "parse_pr_url",
      "status": "succeeded",
      "message": "PR URL 解析完成",
      "timestamp": "2026-06-01T10:00:00Z"
    }
  ],
  "warnings": []
}
```

实现要点：

- `MemoryTaskStore` 保存 `progress_events`。
- 任务失败时也能查询 status。
- 前端创建任务后可以轮询 status，直到 `succeeded` 或 `failed`。
- 如果当前工作流仍是同步执行，也可以先返回完整进度列表，前端照样能展示。

### 5.2 模拟 Review 评论模型

新增模型：

```python
class ReviewCommentDraft(BaseModel):
    id: str
    suggestion_id: str
    finding_id: str | None = None
    file_path: str | None = None
    line: int | None = None
    body: str
    severity: RiskSeverity | None = None
    blocking: bool = False

class CreateReviewCommentsRequest(BaseModel):
    suggestion_ids: list[str]
    include_summary: bool = True
    include_test_recommendations: bool = True

class CreateReviewCommentsResponse(BaseModel):
    task_id: str
    comments: list[ReviewCommentDraft]
    markdown: str
```

字段说明：

- `suggestion_id`：来自 AI 生成的建议，方便前端映射勾选项。
- `finding_id`：如果建议绑定了风险，就关联风险。
- `file_path` 和 `line`：模拟 GitHub inline comment 的位置。
- `body`：最终可以复制到 GitHub 的评论正文。
- `blocking`：是否建议阻塞合并。
- `markdown`：完整 Review 总评 Markdown。

### 5.3 模拟 Review 评论生成服务

文件：`backend/app/services/review_comment_service.py`

核心函数：

```python
def create_review_comment_drafts(
    report: ReviewReport,
    suggestion_ids: list[str],
    include_summary: bool = True,
    include_test_recommendations: bool = True,
) -> CreateReviewCommentsResponse:
    ...
```

生成规则：

- 只允许选择当前 report 中存在的 suggestion。
- 每条 comment 都要保留原 suggestion 的 rationale 和 suggested_fix。
- 如果 suggestion 绑定 finding，则补充 severity、evidence、confidence。
- blocking 为 true 的建议在正文中标注“建议合并前处理”。
- 非 blocking 建议标注“可作为改进项”。
- 如果用户没有选择任何 suggestion，返回 422。

评论正文模板：

```markdown
### Review 建议：{title}

位置：`{file_path}:{line}`

问题证据：
{evidence}

建议：
{comment}

原因：
{rationale}

建议修改：
{suggested_fix}

置信度：{confidence}
```

总评 Markdown 模板：

```markdown
# CodePilot Review 模拟评审

## PR 总结
{summary.overview}

## 建议处理项
- [ ] {comment title}

## 测试建议
- {test recommendation}

> 本评论由 CodePilot Review 生成，当前为模拟发布结果，需人工确认后再提交到 GitHub。
```

### 5.4 评论生成 API

新增接口：

```http
POST /api/reviews/{task_id}/comments
Content-Type: application/json
```

请求：

```json
{
  "suggestion_ids": ["suggestion_001", "suggestion_003"],
  "include_summary": true,
  "include_test_recommendations": true
}
```

响应：

```json
{
  "task_id": "task_xxx",
  "comments": [
    {
      "id": "comment_001",
      "suggestion_id": "suggestion_001",
      "finding_id": "risk_001",
      "file_path": "backend/app/services/review_service.py",
      "line": 42,
      "body": "### Review 建议：任务失败状态缺失\n...",
      "severity": "medium",
      "blocking": false
    }
  ],
  "markdown": "# CodePilot Review 模拟评审\n..."
}
```

错误处理：

| 场景 | 状态码 | 说明 |
| --- | --- | --- |
| task 不存在 | 404 | `Review task not found.` |
| report 未成功生成 | 409 | `Review report is not ready.` |
| suggestion_ids 为空 | 422 | `At least one suggestion must be selected.` |
| suggestion_id 不存在 | 422 | `Unknown suggestion id.` |

### 5.5 Markdown 导出接口

可选接口：

```http
GET /api/reviews/{task_id}/export.md
```

用途：

- 导出完整 Review 报告。
- Demo 录制时可以展示“报告可沉淀”的能力。

如果时间紧，可以只在前端基于 `comments.markdown` 做下载，不必后端新增接口。

### 5.6 报告质量摘要

新增轻量质量摘要，不重新调用模型。

模型：

```python
class ReportQualitySummary(BaseModel):
    total_findings: int
    high_confidence_findings: int
    low_confidence_findings: int
    blocking_suggestions: int
    warning_count: int
    fallback_used: bool
    notes: list[str]
```

生成规则：

- `confidence >= 0.7` 记为高置信度。
- `confidence < 0.5` 记为低置信度。
- warnings 不为空时展示“部分上下文或模型能力降级”。
- 如果使用 fallback，明确提示“当前为规则兜底分析，结果应作为演示或初筛参考”。

这个功能的价值是让评委看到系统考虑了误报、漏报和模型失败，不是盲目相信 AI 输出。

## 6. 前端功能设计

### 6.1 页面主流程

Day3 前端完整流程：

```text
输入 PR URL
  -> 选择 Demo/GitHub 模式
  -> 点击开始分析
  -> 展示进度时间线
  -> 展示 PR 元数据、总结、风险、建议
  -> 用户勾选建议
  -> 点击生成模拟 Review 评论
  -> 预览 GitHub 风格评论
  -> 复制 Markdown 或导出
```

### 6.2 `ReviewCommentComposer.vue`

职责：

- 展示所有 `suggestions`。
- 支持逐条勾选。
- 支持全选和清空。
- 显示 blocking 建议数量。
- 触发生成模拟评论。

Props：

```ts
suggestions: ReviewSuggestion[]
loading: boolean
```

Emits：

```ts
generate: [suggestionIds: string[]]
```

交互规则：

- 没有 suggestions 时显示空状态。
- 未选择任何建议时禁用“生成评论”按钮。
- blocking 建议用醒目标识，但不要用过度警告样式。

### 6.3 `ReviewCommentPreview.vue`

职责：

- 展示生成后的 comment drafts。
- 展示完整 Markdown 总评。
- 支持复制单条评论。
- 支持复制完整 Markdown。
- 支持下载 `.md` 文件。

Props：

```ts
comments: ReviewCommentDraft[]
markdown: string
```

本地下载实现：

```ts
function downloadMarkdown(markdown: string) {
  const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'codepilot-review.md'
  link.click()
  URL.revokeObjectURL(url)
}
```

复制实现：

```ts
await navigator.clipboard.writeText(markdown)
```

要处理 clipboard 不可用的情况，显示“复制失败，请手动选择文本”。

### 6.4 `ReportQualityPanel.vue`

职责：

- 展示 warnings。
- 展示 findings 数量、低置信度数量、blocking 建议数量。
- 展示 fallback 说明。
- 告诉用户“AI 结果需要人工确认”。

注意：不要写成大段说明文，使用简短状态项即可。

### 6.5 空状态和错误状态

新增 `EmptyState.vue`：

- 没有报告时展示轻量提示。
- 没有 findings 时展示“未发现明确风险”。
- 没有 suggestions 时展示“暂无可生成评论的建议”。

新增 `ErrorState.vue`：

- 展示错误标题和错误详情。
- 提供“重新分析”入口。
- GitHub Token/权限错误要提示检查 `.env`。

### 6.6 移动端适配

基础规则：

- 输入框和按钮在小屏下垂直排列。
- 风险卡片不要横向溢出。
- 长路径使用换行或 `word-break: break-all`。
- 操作按钮保持 44px 左右的可点击高度。
- 不做复杂响应式布局，保证能看、能点、不卡即可。

## 7. 前后端请求结构

### 7.1 创建分析任务

```ts
export async function createReviewTask(
  url: string,
  mode: ReviewMode,
): Promise<CreateReviewTaskResponse>
```

请求：

```json
{
  "url": "https://github.com/owner/repo/pull/123",
  "mode": "github"
}
```

### 7.2 查询分析报告

```ts
export async function getReviewReport(taskId: string): Promise<ReviewReport>
```

### 7.3 查询任务状态

```ts
export async function getReviewStatus(taskId: string): Promise<ReviewTaskStatus>
```

### 7.4 生成模拟评论

```ts
export async function createReviewComments(
  taskId: string,
  suggestionIds: string[],
): Promise<CreateReviewCommentsResponse>
```

请求：

```json
{
  "suggestion_ids": ["suggestion_001"],
  "include_summary": true,
  "include_test_recommendations": true
}
```

响应：

```ts
export interface ReviewCommentDraft {
  id: string
  suggestion_id: string
  finding_id?: string
  file_path?: string
  line?: number
  body: string
  severity?: RiskFinding['severity']
  blocking: boolean
}

export interface CreateReviewCommentsResponse {
  task_id: string
  comments: ReviewCommentDraft[]
  markdown: string
}
```

## 8. LangGraph 与 Day3 的关系

Day3 不需要大改 LangGraph 主流程，重点是复用 Day2 的 9 节点输出。

当前主流程：

```text
parse_pr_url
  -> fetch_pr
  -> collect_context
  -> generate_summary
  -> detect_risks
  -> generate_suggestions
  -> guardrail_check
  -> assemble_report
```

Day3 增强方式：

- 不把“评论生成”硬塞进主 Review Graph。
- 评论生成作为 report 之后的独立 service/API。
- 原因：评论生成依赖用户选择，是交互步骤，不是自动分析步骤。

推荐结构：

```text
Review Graph 负责分析
  -> 输出 ReviewReport

ReviewCommentService 负责发布前整理
  -> 输入 ReviewReport + selected suggestion ids
  -> 输出 GitHub 风格模拟评论
```

这种拆分更好解释：

- LangGraph 解决 AI 分析编排。
- Service 解决用户选择后的确定性格式转换。
- 后续如果接真实 GitHub Review API，只需要替换发布层。

## 9. 实现顺序

### Step 1：确认 Day2 基线

输出：

- 确认 Day2 分支都已合并或当前开发分支包含 Day2 代码。
- 确认后端测试通过。
- 确认前端 typecheck/build 通过。

命令：

```bash
cd backend
uv run pytest tests/ -v

cd ../frontend
npm run typecheck
npm run build
```

验收：

- 后端测试全部通过。
- 前端构建通过。
- Demo 模式可用。
- GitHub 模式至少能获取真实公开 PR。

### Step 2：新增 Review 评论模型

输出：

- 更新 `backend/app/schemas/review.py`
- 增加 `ReviewCommentDraft`
- 增加 `CreateReviewCommentsRequest`
- 增加 `CreateReviewCommentsResponse`

验收：

- Pydantic 模型字段完整。
- 前端可以根据字段直接渲染评论预览。
- 单元测试能构造合法响应。

### Step 3：实现 ReviewCommentService

输出：

- `backend/app/services/review_comment_service.py`
- `backend/tests/test_review_comments.py`

验收：

- 能根据选中的 suggestion 生成 comments。
- suggestion_id 不存在时抛出业务错误。
- 空 selection 返回明确错误。
- blocking 建议在 Markdown 中有明确标识。
- 生成的 markdown 包含 PR 总结和测试建议。

### Step 4：新增评论生成 API

输出：

- 更新 `backend/app/api/reviews.py`
- 可选更新 `backend/app/storage/memory_store.py`

验收：

- `POST /api/reviews/{task_id}/comments` 可用。
- task 不存在返回 404。
- report 未完成返回 409。
- selection 非法返回 422。
- 成功返回 comments 和 markdown。

### Step 5：完善任务状态 API

输出：

- 更新 `backend/app/api/reviews.py`
- 更新 status response schema。
- 新增或补充 `backend/tests/test_review_status.py`

验收：

- 成功任务可查询完整 progress events。
- 失败任务也可查询错误状态。
- 前端能用同一接口渲染时间线。

### Step 6：前端类型和 API 封装

输出：

- 更新 `frontend/src/types/review.ts`
- 更新 `frontend/src/api/reviews.ts`

验收：

- TypeScript 类型覆盖 comment/status。
- API 错误能转换成用户可读信息。
- `npm run typecheck` 通过。

### Step 7：实现评论选择和预览组件

输出：

- `ReviewCommentComposer.vue`
- `ReviewCommentPreview.vue`
- 更新 `App.vue`

验收：

- 用户可以勾选建议。
- 未勾选时不能生成评论。
- 点击生成后展示评论预览。
- 可以复制完整 Markdown。
- 可以下载 Markdown。

### Step 8：实现质量摘要和状态组件

输出：

- `ReportQualityPanel.vue`
- `EmptyState.vue`
- `ErrorState.vue`
- 更新 `ProgressTimeline.vue`

验收：

- warnings 明确可见。
- fallback 和低置信度说明明确。
- 无 findings 时不是空白。
- GitHub API 错误展示友好提示。

### Step 9：前端样式收尾

输出：

- 更新 `App.vue` 和组件 CSS。

验收：

- 页面结构清晰。
- 按钮、输入框、过滤器、评论预览不重叠。
- 小屏下输入区和评论区可正常阅读。
- 长文件路径不会撑破布局。

### Step 10：最终文档收尾

输出：

- 更新 `README.md`
- 更新 `PROGRESS.md`
- 新增 `docs/demo-script.md`
- 新增 `docs/final-checklist.md`

验收：

- README 能让别人从零启动项目。
- README 明确声明 Demo/GitHub 模式。
- README 明确声明第三方依赖和模型配置。
- Demo 脚本包含演示用 PR URL、讲解词和失败兜底方案。
- final checklist 覆盖测试、构建、PR、视频、README。

## 10. 测试计划

### 10.1 后端测试

必须通过：

```bash
cd backend
uv run pytest tests/ -v
```

新增测试：

`test_review_comments.py`

- 根据 selected suggestion 生成 comment drafts。
- 生成完整 markdown。
- 空 selection 返回错误。
- unknown suggestion id 返回错误。
- blocking suggestion 正确标记。

`test_review_status.py`

- succeeded task status 查询。
- failed task status 查询。
- missing task 返回 404。
- progress_events 顺序稳定。

`test_review_export.py`（可选）

- export markdown 包含 summary、findings、suggestions、test recommendations。
- missing task 返回 404。

### 10.2 前端检查

必须通过：

```bash
cd frontend
npm run typecheck
npm run build
```

手动验收：

- Demo 模式输入合法 PR URL，报告完整展示。
- GitHub 模式输入公开 PR URL，能看到真实 PR 元数据。
- 风险过滤为空时不回退显示全部。
- 切换模式后提示文案正确。
- 可勾选建议并生成模拟 Review 评论。
- 可复制完整 Markdown。
- 可下载 Markdown。
- 错误状态、空状态和 warnings 可见。

## 11. 错误处理设计

| 场景 | 前端表现 | 后端处理 |
| --- | --- | --- |
| PR URL 为空 | 禁用提交或提示输入 URL | 不发请求 |
| GitHub PR 不存在 | 显示 PR not found | task failed 或 404 |
| GitHub Token 无权限 | 提示检查 Token/仓库权限 | provider error 映射 |
| GitHub rate limit | 提示稍后重试或配置 Token | provider error 映射 |
| LLM 无 Key | 显示 fallback 说明 | 使用 FallbackLLM |
| 无风险发现 | 显示“未发现明确风险” | findings 为空 |
| 无建议 | 禁用生成评论 | comments API 不调用 |
| suggestion id 不存在 | 显示建议已失效，请重新分析 | 422 |
| clipboard 不可用 | 提示手动复制 | 前端 fallback |

## 12. Day3 建议 PR 拆分

### PR-011 Review comments API

内容：

- 增加 Review 评论相关 Schema。
- 增加 `ReviewCommentService`。
- 增加评论生成 API。
- 增加单元测试。

PR 描述重点：

- 功能描述：支持根据用户选择的建议生成 GitHub 风格模拟 Review 评论。
- 实现思路：复用 ReviewReport，不重新调用模型，用确定性模板生成评论草稿和 Markdown。
- 测试方式：覆盖正常生成、空选择、未知 suggestion、blocking 标记。

### PR-012 Frontend comment composer

内容：

- 增加建议勾选组件。
- 增加评论预览组件。
- 增加复制和下载 Markdown。
- 更新前端 API 类型。

PR 描述重点：

- 功能描述：用户可以选择建议并生成可复制的模拟 Review 评论。
- 实现思路：前端维护 selected suggestion ids，调用 comments API 后展示 drafts 和 markdown。
- 测试方式：typecheck、build、手动验证复制/下载。

### PR-013 Status and quality UX polish

内容：

- 完善任务状态展示。
- 增加报告质量摘要。
- 增加空状态、错误状态、warnings 展示。
- 修复移动端布局和长路径溢出。

PR 描述重点：

- 功能描述：提升分析过程和结果可信度展示。
- 实现思路：把 progress、warnings、confidence、fallback 信息集中展示，让用户理解 AI 输出边界。
- 测试方式：typecheck、build、Demo/GitHub 模式手动验证。

### PR-014 Final docs and demo assets

内容：

- README 最终版。
- PROGRESS Day3 更新。
- `docs/demo-script.md`
- `docs/final-checklist.md`

PR 描述重点：

- 功能描述：补齐最终提交材料和演示说明。
- 实现思路：按比赛要求整理功能、架构、启动方式、PR 记录、依赖声明和 Demo 脚本。
- 测试方式：按 README 从零启动，执行最终 checklist。

## 13. README 最终版结构

README 建议结构：

```text
# CodePilot Review

## 项目简介
## 选题说明
## 核心功能
## Demo 效果
## 技术架构
## LangGraph 工作流
## 模型选择与 fallback 策略
## 上下文获取方式
## 误报与漏报控制
## 本地启动
## 环境变量
## 使用流程
## PR 规则与开发记录
## 第三方依赖声明
## 已知限制
## 未来扩展方向
```

必须明确说明：

- Demo 模式无需 Token。
- GitHub 模式公开仓库可无 Token，私有仓库需 `GITHUB_TOKEN`。
- 模型 API Key 缺失时会使用 fallback。
- 当前是模拟 Review 发布，不会真实评论到 GitHub。
- 真实 GitHub Review 发布是未来扩展方向。

## 14. Demo 脚本设计

文件：`docs/demo-script.md`

建议演示流程：

1. 打开首页，说明 CodePilot Review 是 AI PR Review 助手。
2. 选择 Demo 模式，输入示例 PR URL，展示稳定报告。
3. 切换 GitHub 模式，输入公开 PR URL，展示真实 PR 元数据和 diff 分析。
4. 讲解 LangGraph 流程：解析、获取 PR、上下文、总结、风险、建议、护栏、报告。
5. 展示风险列表，说明 severity、evidence、confidence。
6. 勾选几条建议，生成模拟 GitHub Review 评论。
7. 复制 Markdown，说明可粘贴到 GitHub PR Review。
8. 打开 README，说明模型选择、上下文获取、误报控制和未来扩展。

兜底方案：

- 如果 GitHub API 限流，切回 Demo 模式。
- 如果模型 API 不可用，展示 fallback warning。
- 如果网络失败，使用提前准备的截图或录屏片段。

## 15. 最终验收清单

文件：`docs/final-checklist.md`

建议内容：

```markdown
# CodePilot Review 最终验收清单

## 代码检查
- [ ] 后端测试通过
- [ ] 前端 typecheck 通过
- [ ] 前端 build 通过
- [ ] Demo 模式可用
- [ ] GitHub 模式可用
- [ ] 评论生成可用

## 文档检查
- [ ] README 最终版完成
- [ ] PROGRESS 更新 Day3
- [ ] Demo 脚本完成
- [ ] 第三方依赖声明完成
- [ ] 环境变量说明完成

## 比赛规则检查
- [ ] 所有功能通过小粒度 PR 提交
- [ ] PR 标题和描述完整
- [ ] 主分支保持可运行
- [ ] 没有最后一天一次性大提交
- [ ] 公开仓库可访问
- [ ] Demo 视频可播放
```

## 16. 第 3 天完成标准

第 3 天结束前，必须满足：

- 后端所有测试通过。
- 前端 typecheck 和 build 通过。
- Demo 模式稳定可演示。
- GitHub 模式可以分析公开 PR，失败时有明确错误。
- 用户可以选择 Review 建议。
- 系统可以生成 GitHub 风格模拟 Review 评论。
- 评论可以复制或导出 Markdown。
- warnings、fallback、confidence、低置信度风险都有可见说明。
- README 最终版完整。
- PROGRESS 标记 Day3 完成。
- Demo 脚本和最终验收清单完成。
- PR 拆分符合比赛要求，每个 PR 有清晰标题、功能描述、实现思路和测试方式。

## 17. 后续扩展方向

Day3 结束后，可以在答辩或 README 中说明未来扩展：

- 接入真实 GitHub Review API，支持人工确认后发布 inline comments。
- 引入持久化数据库，保存历史 Review 记录。
- 支持组织级规则配置，如安全规则、测试覆盖规则、代码风格规则。
- 增加 AST/调用链上下文，提高复杂代码理解能力。
- 增加多模型交叉验证，降低误报和漏报。
- 支持 GitLab、Gitee 等更多代码托管平台。
- 支持 IDE 插件或 GitHub App 形态。

