# CodePilot Review 第 2 天详细开发文档

## 1. 第 2 天目标

第 2 天目标是在第 1 天可运行 Mock 闭环的基础上，把系统升级为“可分析真实 GitHub PR 的 AI Review 原型”。核心变化是：从固定 Mock 数据转向真实 PR 元数据与 diff 获取，从固定 Mock 分析转向 LLM 结构化生成，同时增加代码上下文收集和基础进度事件，为第 3 天的体验打磨、模拟评论发布和 Demo 录制做准备。

第 2 天完成后，项目应具备以下能力：

- 输入公开 GitHub PR URL 后，可通过 GitHub API 获取真实 PR 元数据、changed files、patch、增删行数和提交数。
- 支持 Demo 模式和 GitHub 模式，GitHub 模式缺少 Token 时仍可访问公开仓库，私有仓库需要 Token。
- LangGraph 工作流从 4 个 Mock 节点扩展为真实分析节点链路。
- 系统能基于 diff 和文件上下文生成 PR 总结、风险发现、Review 建议和测试建议。
- 模型输出使用 Pydantic Schema 做结构化约束，失败时有降级结果。
- 后端能记录节点进度，前端能展示基础分析阶段。
- README 补充 GitHub Token、模型配置和 Day2 使用说明。

## 2. 第 2 天范围

### 2.1 必须完成

- 修补 Day1 遗留项：补 `test_review_graph.py`，补前端 `typecheck` 脚本。
- 新增真实 `GitHubProvider`。
- 新增 `ContextCollector`，收集 changed files、patch、文件内容和相关测试文件线索。
- 扩展 Review Graph 节点。
- 新增 LLM Client 抽象和 Demo/Fallback LLM。
- 新增结构化 Prompt 与输出解析。
- 生成真实 PR summary、risk findings、suggestions、test recommendations。
- 增加任务状态与节点进度记录。
- 前端展示当前分析阶段和真实 GitHub 模式入口。
- README 更新 Day2 配置与运行说明。
- 后端测试覆盖 GitHub Provider Mock、Context Collector、LLM fallback、Workflow。

### 2.2 暂不完成

- 真实 GitHub inline review 评论提交。
- 复杂多文件并行分析。
- 完整 SSE/WebSocket 流式输出体验。
- 企业级规则配置。
- 多用户任务存储。
- 复杂 AST 调用链分析。

第 2 天允许先用轮询或一次性状态查询展示进度，SSE/WebSocket 可以作为第 3 天增强。

## 3. 第 2 天技术方案

### 3.1 推荐方案

采用“真实 GitHub Provider + 上下文收集 + LLM 结构化节点 + 进度事件”的增量方案。

原因：

- 不推翻 Day1 架构，只替换和拆分节点。
- 能展示真实 PR 分析效果，作品完整度明显提升。
- LangGraph 节点清晰，方便答辩解释模型选择、上下文获取和误报控制。
- 即使模型或 GitHub Token 不稳定，也能用 Demo/Fallback 模式保证演示不断。

### 3.2 备选方案与取舍

| 方案 | 优点 | 缺点 | 结论 |
| --- | --- | --- | --- |
| 只接 GitHub API，不接 LLM | 稳定、快 | AI Review 亮点不足 | 不推荐作为 Day2 终态 |
| 直接接 LLM，不收集上下文 | 实现快 | 输出容易泛泛而谈，误报高 | 只可作为临时过渡 |
| GitHub + Context + LLM 结构化输出 | 功能完整，贴合题目 | 实现量适中 | 推荐 |

## 4. Day2 推荐目录结构增量

```text
backend/
├── app/
│   ├── providers/
│   │   ├── github.py              # 真实 GitHub API Provider
│   │   └── errors.py              # Provider 异常类型
│   ├── context/
│   │   ├── __init__.py
│   │   ├── collector.py           # 上下文收集器
│   │   ├── heuristics.py          # 文件分类、相关测试文件识别
│   │   └── models.py              # Context 数据模型
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py                # LLM Client Protocol
│   │   ├── fallback.py            # 无 Key 时可用的 deterministic fallback
│   │   ├── openai_compatible.py   # OpenAI 兼容接口客户端
│   │   └── prompts.py             # Summary/Risk/Suggestion Prompt
│   ├── workflows/
│   │   ├── nodes/
│   │   │   ├── fetch_pr.py
│   │   │   ├── collect_context.py
│   │   │   ├── generate_summary.py
│   │   │   ├── detect_risks.py
│   │   │   ├── generate_suggestions.py
│   │   │   └── guardrail_check.py
│   │   └── progress.py            # 节点进度事件模型
│   └── storage/
│       └── memory_store.py        # 扩展保存 status/progress/report
└── tests/
    ├── test_review_graph.py
    ├── test_github_provider.py
    ├── test_context_collector.py
    └── test_llm_fallback.py
```

前端增量：

```text
frontend/src/
├── components/
│   ├── ProgressTimeline.vue       # 节点进度展示
│   ├── ModeSelector.vue           # demo/github 模式切换
│   └── FindingFilters.vue         # 严重程度/类别过滤
└── types/
    └── review.ts                  # 增加 progress/status 类型
```

## 5. 后端架构升级

### 5.1 Provider 层

第 1 天只有 `MockGitHubProvider`，第 2 天新增 `GitHubProvider`，两者都实现同一个 `PullRequestProvider` Protocol。

核心职责：

- 根据 `ParsedPullRequest` 获取 PR 元数据。
- 获取 changed files 和 patch。
- 获取 PR commits 数量。
- 获取 changed file 当前内容。
- 将 GitHub API 响应转换为内部 `PullRequestSnapshot`。
- 将 GitHub API 错误转换为业务异常。

建议新增异常：

```python
class GitHubProviderError(Exception):
    pass

class GitHubNotFoundError(GitHubProviderError):
    pass

class GitHubUnauthorizedError(GitHubProviderError):
    pass

class GitHubRateLimitError(GitHubProviderError):
    pass
```

真实接口建议：

```python
class GitHubProvider:
    def __init__(self, token: str | None, timeout_seconds: int = 30):
        ...

    async def get_pull_request(self, ref: ParsedPullRequest) -> PullRequestSnapshot:
        ...

    async def get_file_content(self, ref: ParsedPullRequest, path: str, ref_name: str) -> str | None:
        ...
```

GitHub API 路径：

```text
GET /repos/{owner}/{repo}/pulls/{pull_number}
GET /repos/{owner}/{repo}/pulls/{pull_number}/files
GET /repos/{owner}/{repo}/pulls/{pull_number}/commits
GET /repos/{owner}/{repo}/contents/{path}?ref={head_sha}
```

### 5.2 Context 层

第 2 天不做复杂 AST，只做轻量上下文增强。

上下文来源：

- changed file path、status、additions、deletions、patch。
- changed file 当前内容，限制最大字符数。
- patch 附近 hunk 信息。
- 根据路径识别相关测试文件。
- 根据路径识别模块类型：backend、frontend、tests、config、docs、unknown。

上下文模型：

```python
class FileContext(BaseModel):
    path: str
    module_type: str
    status: str
    additions: int
    deletions: int
    patch: str | None
    content_excerpt: str | None
    related_test_paths: list[str] = []
    evidence_labels: list[str] = []

class ReviewContext(BaseModel):
    pr: PullRequestSnapshot
    files: list[FileContext]
    warnings: list[str] = []
```

收集规则：

- 每个文件最多保留 `MAX_FILE_CONTEXT_CHARS = 6000`。
- 总上下文最多保留 `MAX_TOTAL_CONTEXT_CHARS = 24000`。
- 优先保留 patch，再保留文件内容摘要。
- 跳过二进制文件、超大文件和删除文件内容读取。
- 文件读取失败时写入 warning，不中断整个分析。

### 5.3 LLM 层

新增 LLM Client 抽象，避免业务节点直接依赖某个模型供应商。

```python
class LLMClient(Protocol):
    async def generate_json(self, prompt: str, schema_name: str) -> dict:
        ...
```

Day2 推荐支持两个实现：

- `FallbackLLMClient`：无 API Key 时返回确定性分析结果，保证 Demo 可用。
- `OpenAICompatibleLLMClient`：调用 OpenAI 兼容接口，如 DeepSeek、DashScope、vLLM。

环境变量建议：

```text
MODEL_PROVIDER=deepseek
MODEL_NAME=deepseek-chat
MODEL_BASE_URL=https://api.deepseek.com/v1
MODEL_API_KEY=
LLM_TIMEOUT_SECONDS=60
LLM_FALLBACK=true
```

输出策略：

- summary、risks、suggestions 分三个节点生成。
- 每个节点要求输出 JSON。
- 用 Pydantic 校验 JSON。
- 校验失败重试一次。
- 再失败则使用 fallback 结果，并在 report warnings 中提示。

## 6. LangGraph 工作流升级

### 6.1 Day1 工作流

```text
START
  -> parse_pr_url
  -> fetch_mock_pr
  -> generate_mock_review
  -> assemble_report
END
```

### 6.2 Day2 工作流

```text
START
  -> parse_pr_url
  -> select_provider
  -> fetch_pr
  -> collect_context
  -> generate_summary
  -> detect_risks
  -> generate_suggestions
  -> guardrail_check
  -> assemble_report
END
```

节点职责：

- `parse_pr_url`：复用 Day1 解析逻辑。
- `select_provider`：根据 `mode` 选择 `MockGitHubProvider` 或 `GitHubProvider`。
- `fetch_pr`：获取真实或 Mock PR 快照。
- `collect_context`：读取文件内容和构造 ReviewContext。
- `generate_summary`：生成 PR 总结和 reviewer focus。
- `detect_risks`：生成风险发现。
- `generate_suggestions`：针对 findings 生成 Review 建议和测试建议。
- `guardrail_check`：过滤无证据、低置信度、重复或过于宽泛的 findings。
- `assemble_report`：组装最终 `ReviewReport`。

### 6.3 状态模型扩展

`ReviewGraphState` 建议扩展：

```python
class ReviewGraphState(TypedDict, total=False):
    task_id: str
    url: str
    mode: str
    parsed_pr: ParsedPullRequest
    provider_name: str
    pr_snapshot: PullRequestSnapshot
    review_context: ReviewContext
    summary: ReviewSummary
    findings: list[RiskFinding]
    suggestions: list[ReviewSuggestion]
    test_recommendations: list[str]
    progress_events: list[ReviewProgressEvent]
    warnings: list[str]
    report: ReviewReport
    error_message: str
```

### 6.4 进度事件

Day2 可以先不做真正 SSE，但后端要记录节点事件，为 Day3 流式输出做准备。

```python
class ReviewProgressEvent(BaseModel):
    node: str
    status: Literal["pending", "running", "succeeded", "failed", "skipped"]
    message: str
    timestamp: datetime
```

API 可新增：

```http
GET /api/reviews/{task_id}/status
```

响应：

```json
{
  "task_id": "task_xxx",
  "status": "succeeded",
  "current_node": "assemble_report",
  "progress_events": []
}
```

## 7. API 设计增量

### 7.1 创建任务请求

继续使用：

```http
POST /api/reviews
```

请求：

```json
{
  "url": "https://github.com/owner/repo/pull/123",
  "mode": "github"
}
```

规则：

- `mode=demo`：使用 Mock Provider 和 fallback LLM，稳定演示。
- `mode=github`：使用真实 GitHub Provider。
- 如果 `mode=github` 且 GitHub API 失败，返回 `failed` task，不静默回退为 Mock。
- 如果模型失败但 PR 获取成功，可以 fallback LLM 并在 warnings 中说明。

### 7.2 查询任务状态

```http
GET /api/reviews/{task_id}/status
```

用途：

- 前端显示分析阶段。
- 第 3 天升级 SSE 时复用同一套事件结构。

### 7.3 查询完整报告

```http
GET /api/reviews/{task_id}
```

响应继续返回 `ReviewReport`，建议新增字段：

```python
warnings: list[str] = []
provider_name: str | None = None
model_name: str | None = None
```

## 8. Prompt 与结构化输出设计

### 8.1 Summary Prompt

输入：

- PR title、author、base/head branch。
- changed file list。
- additions/deletions。
- ReviewContext 摘要。

输出：

```json
{
  "overview": "string",
  "changed_modules": ["string"],
  "reviewer_focus": ["string"]
}
```

要求：

- 中文输出。
- 不要编造 diff 中不存在的业务背景。
- reviewer_focus 控制在 3 到 5 条。

### 8.2 Risk Prompt

输出：

```json
{
  "findings": [
    {
      "id": "risk_001",
      "severity": "medium",
      "category": "correctness",
      "file_path": "backend/app/api/reviews.py",
      "line": 42,
      "title": "string",
      "evidence": "string",
      "reasoning": "string",
      "confidence": 0.82
    }
  ]
}
```

要求：

- 只基于 diff 和 context 给结论。
- high/critical 必须有明确证据。
- 无明显风险时返回空数组。
- 不输出泛泛建议，比如“建议优化代码质量”。

### 8.3 Suggestion Prompt

输入：

- findings。
- ReviewContext。

输出：

```json
{
  "suggestions": [
    {
      "id": "suggestion_001",
      "finding_id": "risk_001",
      "file_path": "backend/app/services/review_service.py",
      "comment": "string",
      "rationale": "string",
      "suggested_fix": "string",
      "blocking": false
    }
  ],
  "test_recommendations": ["string"]
}
```

要求：

- 每条建议尽量绑定 finding。
- comment 可以直接作为 GitHub Review 评论草稿。
- 测试建议要具体到场景。

## 9. 前端功能增量

### 9.1 模式切换

新增 `ModeSelector.vue`：

- `Demo Mode`：稳定 Mock 数据。
- `GitHub Mode`：真实 GitHub PR。

说明：

- Demo Mode 默认选中。
- GitHub Mode 下提示“公开仓库无需 Token，私有仓库需配置 GITHUB_TOKEN”。

### 9.2 进度展示

新增 `ProgressTimeline.vue`，展示节点状态：

```text
URL 解析
PR 获取
上下文收集
总结生成
风险识别
建议生成
质量检查
报告组装
```

Day2 可以通过创建任务后立即查询状态/报告展示；Day3 再升级为 SSE 实时推送。

### 9.3 风险过滤

新增 `FindingFilters.vue`：

- 按 severity 过滤。
- 按 category 过滤。
- 默认隐藏低置信度风险。

如果时间紧，Day2 只实现 severity 过滤，category 过滤放 Day3。

## 10. 实现顺序

### Step 1：补 Day1 缺口

输出：

- `backend/tests/test_review_graph.py`
- `frontend/package.json` 增加 `typecheck`

验收：

- 直接测试 LangGraph 能输出 report。
- 直接测试非法 URL 不会生成 succeeded report。
- `npm run typecheck` 可执行。

### Step 2：新增 GitHubProvider

输出：

- `providers/github.py`
- `providers/errors.py`
- `tests/test_github_provider.py`

验收：

- 使用 httpx mock 或 monkeypatch 模拟 GitHub API。
- 成功将 GitHub API 响应转换为 `PullRequestSnapshot`。
- 404 转换为 `GitHubNotFoundError`。
- 401/403 转换为 `GitHubUnauthorizedError` 或 `GitHubRateLimitError`。
- patch、additions、deletions、changed_files 字段正确。

### Step 3：新增 ContextCollector

输出：

- `context/models.py`
- `context/heuristics.py`
- `context/collector.py`
- `tests/test_context_collector.py`

验收：

- 能将 PR files 转换为 `ReviewContext`。
- 能识别 backend/frontend/tests/config/docs。
- 能识别相关测试路径候选。
- 能限制单文件和总上下文长度。
- 文件内容获取失败时写 warnings，不中断。

### Step 4：新增 LLM Client 与 Prompt

输出：

- `llm/base.py`
- `llm/fallback.py`
- `llm/openai_compatible.py`
- `llm/prompts.py`
- `tests/test_llm_fallback.py`

验收：

- Fallback LLM 能返回合法 summary/findings/suggestions。
- OpenAI 兼容客户端支持 base_url、api_key、model。
- JSON 解析失败时有明确异常或 fallback。
- Pydantic 校验失败时不会导致服务崩溃。

### Step 5：扩展 LangGraph Workflow

输出：

- `workflows/nodes/fetch_pr.py`
- `workflows/nodes/collect_context.py`
- `workflows/nodes/generate_summary.py`
- `workflows/nodes/detect_risks.py`
- `workflows/nodes/generate_suggestions.py`
- `workflows/nodes/guardrail_check.py`
- 更新 `review_graph.py`
- 更新 `review_state.py`

验收：

- Demo Mode 仍可稳定返回报告。
- GitHub Mode 可调用真实或测试 Provider。
- LLM 失败时返回 fallback 分析和 warnings。
- 低置信度或无证据 finding 被过滤。
- 工作流状态包含 progress_events。

### Step 6：扩展 API 和 Store

输出：

- 更新 `memory_store.py`
- 更新 `api/reviews.py`
- 更新 `schemas/review.py`

验收：

- 创建任务后保存 status、progress_events、report。
- `GET /api/reviews/{task_id}/status` 返回任务状态。
- `GET /api/reviews/{task_id}` 继续兼容 Day1 前端。
- 失败任务返回 error_message 和 warnings。

### Step 7：前端接入 Day2 能力

输出：

- `ModeSelector.vue`
- `ProgressTimeline.vue`
- `FindingFilters.vue`
- 更新 `App.vue`
- 更新 `api/reviews.ts`
- 更新 `types/review.ts`

验收：

- 可选择 Demo/GitHub 模式。
- 能展示节点进度或阶段状态。
- 能展示 warnings。
- 能按 severity 过滤 findings。
- `npm run typecheck` 通过。
- `npm run build` 通过。

### Step 8：README 和进度文档更新

输出：

- 更新 `README.md`
- 更新 `PROGRESS.md`
- 可选新增 `docs/model-context-strategy.md`

验收：

- README 说明 GitHub Token 配置。
- README 说明模型配置和 fallback 行为。
- README 说明 Demo Mode 与 GitHub Mode 差异。
- README 声明新增依赖。
- PROGRESS 记录 Day2 PR 和完成项。

## 11. 测试计划

### 11.1 后端测试

必须通过：

```bash
cd backend
uv run pytest tests/ -v
```

新增测试：

- `test_review_graph.py`
  - demo workflow succeeds。
  - invalid URL fails。
  - workflow includes progress events。
  - fallback LLM produces valid report。

- `test_github_provider.py`
  - fetch PR metadata success。
  - fetch PR files success。
  - map 404/401/403/rate limit。
  - preserve patch and line-related fields。

- `test_context_collector.py`
  - classify files。
  - collect patch and content excerpt。
  - enforce context budget。
  - collect warnings on content failure。

- `test_llm_fallback.py`
  - fallback summary schema valid。
  - fallback findings schema valid。
  - fallback suggestions schema valid。

### 11.2 前端检查

必须通过：

```bash
cd frontend
npm run typecheck
npm run build
```

手动验证：

- Demo Mode 输入 `https://github.com/acme/codepilot/pull/12` 能返回报告。
- GitHub Mode 输入公开 PR URL 能返回真实 PR 元数据。
- 缺少或错误 URL 显示错误。
- 进度区域不空白。
- findings 过滤生效。

## 12. 错误处理设计

| 场景 | 处理 |
| --- | --- |
| GitHub PR 不存在 | task failed，error_message 显示 PR not found |
| GitHub API 401/403 | task failed，提示检查 Token 或权限 |
| GitHub rate limit | task failed，提示稍后重试或配置 Token |
| 文件内容读取失败 | 写入 warnings，继续分析 patch |
| LLM API 无 Key | 使用 Fallback LLM，写入 warning |
| LLM JSON 格式错误 | 重试一次，失败后 fallback |
| finding 缺少 evidence | guardrail 删除该 finding |
| 上下文超限 | 截断并写入 warning |

## 13. 第 2 天建议 PR 拆分

### PR-005 Day1 quality fixes

内容：

- 补 `test_review_graph.py`。
- 补 `npm run typecheck` 脚本。
- 修正 `github` 模式暂未接入时的提示或行为。

PR 描述重点：

- 功能描述：补齐 Day1 验收缺口。
- 实现思路：增加 graph 直接测试和前端脚本。
- 测试方式：后端 pytest、前端 typecheck。

### PR-006 Real GitHub Provider

内容：

- 新增 `GitHubProvider`。
- 新增 Provider 错误类型。
- 新增 Provider 单元测试。

PR 描述重点：

- 功能描述：支持从 GitHub API 获取真实 PR 元数据和 diff。
- 实现思路：封装 GitHub REST API，并转换为内部 `PullRequestSnapshot`。
- 测试方式：mock GitHub API 响应，覆盖成功和异常场景。

### PR-007 Context collector

内容：

- 新增上下文模型和收集器。
- 增加文件分类、相关测试路径识别和上下文预算。
- 新增单元测试。

PR 描述重点：

- 功能描述：为 AI Review 补充 diff 之外的代码上下文。
- 实现思路：以 patch 为核心，结合文件内容摘要和路径启发式。
- 测试方式：不同文件类型、超长内容、读取失败。

### PR-008 LLM structured review nodes

内容：

- 新增 LLM Client。
- 新增 Prompt。
- 新增 summary/risk/suggestion 节点。
- 新增 fallback 和 guardrail。

PR 描述重点：

- 功能描述：将 Mock Review 替换为 LLM 结构化分析。
- 实现思路：分节点生成 summary、findings、suggestions，并用 Pydantic 校验。
- 测试方式：fallback 输出、结构校验、低质量 finding 过滤。

### PR-009 Day2 frontend integration

内容：

- 增加模式切换。
- 增加进度展示。
- 增加 findings 过滤。
- 展示 warnings。

PR 描述重点：

- 功能描述：前端支持 Day2 真实 PR 分析流程展示。
- 实现思路：扩展 API 类型和 Dashboard 组件。
- 测试方式：typecheck、build、Demo/GitHub 手动验证。

### PR-010 README and progress update

内容：

- 更新 README。
- 更新 PROGRESS。
- 补模型与上下文策略说明。

PR 描述重点：

- 功能描述：完善 Day2 使用和交付说明。
- 实现思路：补充环境变量、模式说明、依赖声明和已完成能力。
- 测试方式：按 README 本地启动。

## 14. 第 2 天完成标准

第 2 天结束前，必须满足：

- `npm run typecheck` 和 `npm run build` 通过。
- `uv run pytest tests/ -v` 通过。
- Demo Mode 仍然稳定可用。
- GitHub Mode 至少能分析一个公开仓库 PR 的真实元数据和 diff。
- Review 报告由 LLM 或 fallback 结构化生成，不再完全依赖固定 Mock 文案。
- 报告里包含 summary、findings、suggestions、test recommendations。
- findings 包含 severity、category、file_path、evidence、reasoning、confidence。
- 前端能展示分析阶段、warnings 和过滤后的风险列表。
- README 说明 GitHub Token、模型配置、fallback 行为和 Day2 能力。
- 至少产生 4 到 6 个小粒度 PR，且每个 PR 描述包含功能描述、实现思路、测试方式。

## 15. 第 3 天承接点

第 2 天完成后，第 3 天重点做：

- SSE 或 WebSocket 实时进度流。
- 模拟 GitHub Review 评论发布。
- UI 细节、空状态、错误状态和移动端适配。
- 质量自检和误报控制增强。
- README 最终版、Demo 脚本和 Demo 视频录制。
- 最终有效性检查清单。
