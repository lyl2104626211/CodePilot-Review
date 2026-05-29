# CodePilot Review 第 1 天详细开发文档

## 1. 第 1 天目标

第 1 天目标是完成一个可运行、可演示、可持续迭代的项目基础版本。该版本不追求完整 AI Review 能力，但从第一天就引入 LangGraph 节点工作流骨架，优先打通产品主链路：用户打开前端页面，输入 GitHub PR URL，后端通过 LangGraph 执行 URL 解析、Mock PR 获取、Mock 分析和报告保存，前端展示基础 Dashboard。

第 1 天完成后，项目应具备以下能力：

- 后端 FastAPI 服务可启动。
- 前端 Vite + Vue 3 页面可启动。
- 支持 GitHub PR URL 解析。
- 支持健康检查、版本信息、PR URL 解析、基于 LangGraph 的 Mock Review 任务创建和任务结果查询。
- 前端有完整工作台页面，包括 URL 输入、PR 元数据预览、分析按钮、基础结果展示。
- README 包含项目介绍和本地启动方式。
- 具备第 2 天接入真实 GitHub API、LLM 分析和流式进度的 LangGraph 节点边界。

## 2. 第 1 天范围

### 2.1 必须完成

- 项目目录初始化。
- 后端 FastAPI 基础结构。
- 前端 Vue 3 + Vite 基础结构。
- Pydantic Schema 定义。
- PR URL 解析函数。
- Mock GitHub Provider。
- LangGraph Review Workflow 骨架。
- Mock Review Service。
- 前端基础 Dashboard。
- README 初版。
- 后端基础测试。
- 前端 typecheck 脚本。

### 2.2 暂不完成

- 真实 GitHub API 调用。
- 真实 LLM 调用。
- 复杂 LangGraph 分支、并行和人工中断流程。
- SSE 或 WebSocket 流式输出。
- 真实 GitHub Review 评论发布。
- 复杂代码上下文提取。

第 1 天保留完整工作流接口形状，实现确定性的最小 LangGraph 节点链路，不实现复杂 AI 分析逻辑。

## 3. 技术选型

### 3.1 后端

- Python 3.11+
- FastAPI
- Pydantic v2
- Uvicorn
- pytest
- httpx
- python-dotenv 或 pydantic-settings
- LangGraph

### 3.2 前端

- Vue 3
- Vite
- TypeScript
- Pinia 可选，第 1 天可以先不用
- CSS Modules 或普通 CSS，第 1 天优先简单可维护

### 3.3 后续预留

- OpenAI 兼容模型接口或 DashScope：第 2 天接入 LLM Client。
- GitHub REST API：第 2 天接入真实 Provider。
- SSE 或 WebSocket：第 2 天将 LangGraph 节点状态流式推送给前端。

## 4. 推荐目录结构

```text
codepilot-review/
├── README.md
├── .env.example
├── agents/
│   ├── prd.json
│   └── prd.md
├── docs/
│   └── plans/
│       └── day1-development.md
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   └── reviews.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── common.py
│   │   │   ├── github.py
│   │   │   └── review.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── pr_parser.py
│   │   │   └── review_service.py
│   │   ├── workflows/
│   │   │   ├── __init__.py
│   │   │   ├── review_graph.py
│   │   │   └── review_state.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── mock_github.py
│   │   └── storage/
│   │       ├── __init__.py
│   │       └── memory_store.py
│   └── tests/
│       ├── test_health.py
│       ├── test_pr_parser.py
│       └── test_reviews.py
└── frontend/
    ├── package.json
    ├── index.html
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── main.ts
        ├── App.vue
        ├── api/
        │   └── reviews.ts
        ├── components/
        │   ├── PrInputPanel.vue
        │   ├── PrMetaPanel.vue
        │   ├── ReviewSummary.vue
        │   ├── RiskList.vue
        │   └── SuggestionList.vue
        ├── types/
        │   └── review.ts
        └── styles/
            └── app.css
```

## 5. 后端架构设计

### 5.1 分层职责

| 层级 | 目录 | 职责 |
| --- | --- | --- |
| API 层 | `backend/app/api` | 接收 HTTP 请求，做轻量参数校验，调用 service |
| Schema 层 | `backend/app/schemas` | 定义请求、响应、内部数据结构 |
| Service 层 | `backend/app/services` | 编排业务逻辑，如 URL 解析、任务创建、Mock 分析 |
| Workflow 层 | `backend/app/workflows` | 使用 LangGraph 编排 Review 节点，输出结构化报告 |
| Provider 层 | `backend/app/providers` | 屏蔽 GitHub 数据来源，后续可替换为真实 GitHub API |
| Storage 层 | `backend/app/storage` | 保存 Review 任务状态和结果，第 1 天使用内存 |
| Core 层 | `backend/app/core` | 管理配置、常量和应用启动参数 |

### 5.2 第 1 天模块说明

#### `app/main.py`

负责创建 FastAPI 应用，注册路由，配置 CORS。

核心函数：

```python
def create_app() -> FastAPI:
    app = FastAPI(title="CodePilot Review", version=settings.app_version)
    app.add_middleware(...)
    app.include_router(health_router, prefix="/api")
    app.include_router(review_router, prefix="/api")
    return app
```

#### `app/core/config.py`

负责读取环境变量。

核心配置：

- `APP_NAME`
- `APP_VERSION`
- `APP_ENV`
- `FRONTEND_ORIGIN`
- `GITHUB_TOKEN`
- `MODEL_PROVIDER`
- `MODEL_NAME`
- `REQUEST_TIMEOUT_SECONDS`
- `DEMO_MODE`

#### `app/services/pr_parser.py`

负责解析 GitHub PR URL。

核心函数：

```python
def parse_github_pr_url(url: str) -> ParsedPullRequest:
    ...
```

解析规则：

- 支持 `https://github.com/{owner}/{repo}/pull/{number}`
- owner 不能为空
- repo 不能为空
- number 必须是正整数
- URL path 后面多余斜杠可容忍
- 非 GitHub 域名直接拒绝

#### `app/providers/base.py`

定义 Provider 抽象接口，方便第 2 天接入真实 GitHub。

核心接口：

```python
class PullRequestProvider(Protocol):
    async def get_pull_request(self, ref: ParsedPullRequest) -> PullRequestSnapshot:
        ...
```

#### `app/providers/mock_github.py`

返回稳定的 Mock PR 数据，用于第 1 天演示。

Mock 数据建议包含：

- PR 标题：`Add async review task creation`
- 作者：`demo-user`
- base 分支：`main`
- head 分支：`feature/review-task`
- changed files：3 个
- additions：128
- deletions：24
- 文件类型：后端接口、服务逻辑、测试文件

#### `app/services/review_service.py`

负责创建 Review 任务，调用 LangGraph Review Workflow，并保存基础分析结果。

第 1 天不调用 LLM，Workflow 内部节点返回固定但合理的分析结构。

核心函数：

```python
async def create_review_task(request: CreateReviewTaskRequest) -> ReviewTask:
    ...

async def get_review_result(task_id: str) -> ReviewReport:
    ...
```

#### `app/workflows/review_state.py`

定义 LangGraph 在节点之间传递的状态。第 1 天状态字段保持简单，但必须覆盖后续接入真实 GitHub 和 LLM 所需的关键位置。

核心模型：

```python
class ReviewGraphState(TypedDict, total=False):
    task_id: str
    url: str
    mode: str
    parsed_pr: ParsedPullRequest
    pr_snapshot: PullRequestSnapshot
    summary: ReviewSummary
    findings: list[RiskFinding]
    suggestions: list[ReviewSuggestion]
    test_recommendations: list[str]
    report: ReviewReport
    error_message: str
```

#### `app/workflows/review_graph.py`

定义第 1 天最小 LangGraph 节点工作流。

节点设计：

```text
START
  -> parse_pr_url
  -> fetch_mock_pr
  -> generate_mock_review
  -> assemble_report
END
```

节点职责：

- `parse_pr_url`：调用 `parse_github_pr_url`，把 URL 解析为 `ParsedPullRequest`。
- `fetch_mock_pr`：调用 `MockGitHubProvider`，返回 `PullRequestSnapshot`。
- `generate_mock_review`：基于 Mock PR 文件生成固定 summary、findings、suggestions 和 test recommendations。
- `assemble_report`：组装 `ReviewReport`，交给 service 保存。

核心函数：

```python
def build_review_graph(provider: PullRequestProvider) -> CompiledStateGraph:
    graph = StateGraph(ReviewGraphState)
    graph.add_node("parse_pr_url", parse_pr_url_node)
    graph.add_node("fetch_mock_pr", fetch_mock_pr_node(provider))
    graph.add_node("generate_mock_review", generate_mock_review_node)
    graph.add_node("assemble_report", assemble_report_node)
    graph.add_edge(START, "parse_pr_url")
    graph.add_edge("parse_pr_url", "fetch_mock_pr")
    graph.add_edge("fetch_mock_pr", "generate_mock_review")
    graph.add_edge("generate_mock_review", "assemble_report")
    graph.add_edge("assemble_report", END)
    return graph.compile()
```

第 2 天可以保留节点名，只替换实现：

- `fetch_mock_pr` 改为 `fetch_github_pr`。
- `generate_mock_review` 拆分为 `collect_context`、`generate_summary`、`detect_risks`、`generate_suggestions`。
- `assemble_report` 增加 guardrail 自检。

#### `app/storage/memory_store.py`

使用 dict 保存任务。

核心函数：

```python
class MemoryTaskStore:
    def save(self, task: ReviewTask) -> None:
        ...

    def get(self, task_id: str) -> ReviewTask | None:
        ...
```

## 6. 后端数据模型

### 6.1 通用枚举

```python
class TaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"

class RiskSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class RiskCategory(str, Enum):
    correctness = "correctness"
    security = "security"
    performance = "performance"
    compatibility = "compatibility"
    observability = "observability"
    data_handling = "data_handling"
    missing_tests = "missing_tests"
```

### 6.2 PR 解析模型

```python
class ParsedPullRequest(BaseModel):
    owner: str
    repo: str
    number: int
    url: HttpUrl
```

### 6.3 PR 元数据模型

```python
class PullRequestFile(BaseModel):
    path: str
    status: str
    additions: int
    deletions: int
    patch: str | None = None

class PullRequestSnapshot(BaseModel):
    owner: str
    repo: str
    number: int
    title: str
    author: str
    base_branch: str
    head_branch: str
    changed_files: int
    additions: int
    deletions: int
    commit_count: int
    files: list[PullRequestFile]
```

### 6.4 Review 请求模型

```python
class ParsePullRequestRequest(BaseModel):
    url: str

class CreateReviewTaskRequest(BaseModel):
    url: str
    mode: Literal["demo", "github"] = "demo"

class CreateReviewTaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
```

### 6.5 Review 报告模型

```python
class ReviewSummary(BaseModel):
    overview: str
    changed_modules: list[str]
    reviewer_focus: list[str]

class RiskFinding(BaseModel):
    id: str
    severity: RiskSeverity
    category: RiskCategory
    file_path: str
    line: int | None = None
    title: str
    evidence: str
    reasoning: str
    confidence: float

class ReviewSuggestion(BaseModel):
    id: str
    finding_id: str | None = None
    file_path: str | None = None
    comment: str
    rationale: str
    suggested_fix: str
    blocking: bool

class ReviewReport(BaseModel):
    task_id: str
    status: TaskStatus
    pr: PullRequestSnapshot
    summary: ReviewSummary
    findings: list[RiskFinding]
    suggestions: list[ReviewSuggestion]
    test_recommendations: list[str]
```

## 7. API 设计

### 7.1 健康检查

```http
GET /api/health
```

响应：

```json
{
  "status": "ok"
}
```

### 7.2 版本信息

```http
GET /api/version
```

响应：

```json
{
  "name": "CodePilot Review",
  "version": "0.1.0",
  "env": "development"
}
```

### 7.3 解析 PR URL

```http
POST /api/reviews/parse
Content-Type: application/json
```

请求：

```json
{
  "url": "https://github.com/acme/codepilot/pull/12"
}
```

成功响应：

```json
{
  "owner": "acme",
  "repo": "codepilot",
  "number": 12,
  "url": "https://github.com/acme/codepilot/pull/12"
}
```

失败响应：

```json
{
  "detail": "Only GitHub pull request URLs are supported."
}
```

### 7.4 创建 Review 任务

```http
POST /api/reviews
Content-Type: application/json
```

请求：

```json
{
  "url": "https://github.com/acme/codepilot/pull/12",
  "mode": "demo"
}
```

响应：

```json
{
  "task_id": "task_01HZ0000000000000000000000",
  "status": "succeeded"
}
```

第 1 天为了演示顺畅，任务可以通过 LangGraph 同步执行完成并直接标记为 `succeeded`。第 2 天再将同一套节点执行过程改造成异步任务和流式进度。

### 7.5 查询 Review 结果

```http
GET /api/reviews/{task_id}
```

响应：

```json
{
  "task_id": "task_01HZ0000000000000000000000",
  "status": "succeeded",
  "pr": {
    "owner": "acme",
    "repo": "codepilot",
    "number": 12,
    "title": "Add async review task creation",
    "author": "demo-user",
    "base_branch": "main",
    "head_branch": "feature/review-task",
    "changed_files": 3,
    "additions": 128,
    "deletions": 24,
    "commit_count": 4,
    "files": []
  },
  "summary": {
    "overview": "本 PR 新增了 Review 任务创建接口和基础任务状态管理。",
    "changed_modules": ["backend api", "review service", "tests"],
    "reviewer_focus": ["任务状态是否可靠", "异常处理是否完整", "测试是否覆盖失败分支"]
  },
  "findings": [
    {
      "id": "risk_001",
      "severity": "medium",
      "category": "correctness",
      "file_path": "backend/app/services/review_service.py",
      "line": 42,
      "title": "任务状态更新缺少失败分支",
      "evidence": "create_review_task only marks succeeded in demo path.",
      "reasoning": "后续接入真实异步分析后，如果 Provider 或模型调用失败，任务可能停留在 running。",
      "confidence": 0.82
    }
  ],
  "suggestions": [
    {
      "id": "suggestion_001",
      "finding_id": "risk_001",
      "file_path": "backend/app/services/review_service.py",
      "comment": "建议为 Review 任务增加统一异常捕获，并在失败时写入 failed 状态和错误信息。",
      "rationale": "这样前端可以展示明确失败原因，避免用户长时间等待。",
      "suggested_fix": "在 create_review_task 外层包装 try/except，并将错误保存到 task.error_message。",
      "blocking": false
    }
  ],
  "test_recommendations": [
    "增加非法 PR URL 的解析失败测试。",
    "增加任务不存在时返回 404 的测试。",
    "增加 Mock Provider 返回固定 PR 元数据的测试。"
  ]
}
```

## 8. 前端架构设计

### 8.1 页面结构

第 1 天只做一个主页面 `App.vue`，不引入路由。

页面区域：

- 顶部标题栏：项目名、简短副标题。
- 输入区：PR URL 输入框、Demo Mode 标识、开始分析按钮。
- 元数据区：展示 owner、repo、PR number、标题、作者、分支、增删行。
- 摘要区：展示 overview、changed modules、reviewer focus。
- 风险区：展示 severity、category、file path、line、title、reasoning、confidence。
- 建议区：展示 comment、rationale、suggested fix、blocking。
- 测试建议区：展示推荐补充的测试点。

### 8.2 前端组件职责

#### `PrInputPanel.vue`

职责：

- 输入 PR URL。
- 点击开始分析。
- 展示基本校验错误。

Props：

- `loading: boolean`
- `error?: string`

Emits：

- `submit(url: string)`

#### `PrMetaPanel.vue`

职责：

- 展示 PR 元数据。
- 当暂无数据时不渲染或显示轻量空状态。

Props：

- `pr: PullRequestSnapshot | null`

#### `ReviewSummary.vue`

职责：

- 展示 PR 总览、变更模块和评审重点。

Props：

- `summary: ReviewSummary | null`

#### `RiskList.vue`

职责：

- 展示风险列表。
- 第 1 天可以先不做复杂筛选，只用 severity 颜色区分。

Props：

- `findings: RiskFinding[]`

#### `SuggestionList.vue`

职责：

- 展示 Review 建议和测试建议。

Props：

- `suggestions: ReviewSuggestion[]`
- `testRecommendations: string[]`

### 8.3 前端 API 封装

文件：`frontend/src/api/reviews.ts`

核心函数：

```ts
export async function createReviewTask(url: string): Promise<CreateReviewTaskResponse> {
  const response = await fetch("/api/reviews", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, mode: "demo" }),
  });
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function getReviewReport(taskId: string): Promise<ReviewReport> {
  const response = await fetch(`/api/reviews/${taskId}`);
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}
```

第 1 天建议使用 Vite dev server proxy：

```ts
server: {
  proxy: {
    "/api": "http://localhost:8000"
  }
}
```

## 9. 第 1 天功能实现顺序

### Step 1：初始化后端项目

输出：

- `backend/pyproject.toml`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/api/health.py`

验收：

- `GET /api/health` 返回 `{"status":"ok"}`。
- `GET /api/version` 返回项目版本。

### Step 2：定义 Schema

输出：

- `schemas/common.py`
- `schemas/github.py`
- `schemas/review.py`

验收：

- 所有 API 响应都使用 Pydantic 模型。
- 前后端字段命名稳定。

### Step 3：实现 PR URL 解析

输出：

- `services/pr_parser.py`
- `tests/test_pr_parser.py`

验收：

- 合法 GitHub PR URL 可解析。
- 非 GitHub URL 被拒绝。
- 缺少 `/pull/{number}` 被拒绝。
- PR number 非正整数被拒绝。

### Step 4：实现 Mock Provider

输出：

- `providers/base.py`
- `providers/mock_github.py`

验收：

- Mock Provider 根据 ParsedPullRequest 返回固定 PR 快照。
- PR 快照包含 changed files、additions、deletions 和 files。

### Step 5：实现 LangGraph Review Workflow

输出：

- `workflows/review_state.py`
- `workflows/review_graph.py`
- `tests/test_review_graph.py`

验收：

- Workflow 包含 `parse_pr_url`、`fetch_mock_pr`、`generate_mock_review`、`assemble_report` 四个节点。
- 合法 URL 输入后，Workflow 输出完整 `ReviewReport`。
- 非法 URL 输入后，Workflow 返回可被 API 转换为 422 的错误。
- Mock Provider 可通过依赖注入传入 graph，方便第 2 天替换真实 Provider。

### Step 6：实现 Review Service 和 API

输出：

- `services/review_service.py`
- `storage/memory_store.py`
- `api/reviews.py`

验收：

- `POST /api/reviews` 创建任务，并调用 LangGraph Workflow 生成报告。
- `GET /api/reviews/{task_id}` 返回 Mock ReviewReport。
- 任务不存在时返回 404。

### Step 7：初始化前端项目

输出：

- `frontend/package.json`
- `frontend/src/main.ts`
- `frontend/src/App.vue`
- `frontend/src/styles/app.css`

验收：

- 前端 dev server 可启动。
- 页面能看到 CodePilot Review 工作台。

### Step 8：实现前端 Dashboard

输出：

- `components/PrInputPanel.vue`
- `components/PrMetaPanel.vue`
- `components/ReviewSummary.vue`
- `components/RiskList.vue`
- `components/SuggestionList.vue`
- `api/reviews.ts`
- `types/review.ts`

验收：

- 输入 PR URL 后能调用后端创建任务。
- 自动查询任务结果并渲染。
- 错误信息可展示。

### Step 9：补充 README 初版

输出：

- `README.md`
- `.env.example`

验收：

- README 包含项目介绍。
- README 包含后端启动命令。
- README 包含前端启动命令。
- README 说明第 1 天 Demo Mode 使用 Mock 数据。

## 10. 错误处理设计

### 10.1 后端错误

| 场景 | HTTP 状态码 | 响应 |
| --- | --- | --- |
| PR URL 格式错误 | 422 | `Invalid GitHub PR URL.` |
| 非 GitHub 域名 | 422 | `Only GitHub pull request URLs are supported.` |
| PR number 非法 | 422 | `Pull request number must be a positive integer.` |
| task_id 不存在 | 404 | `Review task not found.` |
| 未知异常 | 500 | `Internal server error.` |

### 10.2 前端错误

- 输入为空：按钮禁用或显示 `请输入 GitHub PR URL`。
- 后端 422：展示后端返回的 detail。
- 后端 404：展示 `未找到分析任务，请重新发起分析`。
- 网络失败：展示 `无法连接后端服务，请确认服务已启动`。

## 11. 测试计划

### 11.1 后端测试

`test_health.py`

- health endpoint returns ok。
- version endpoint returns app name and version。

`test_pr_parser.py`

- parse valid GitHub PR URL。
- reject non-GitHub URL。
- reject URL without pull segment。
- reject non-number PR id。

`test_reviews.py`

- create review task with valid URL。
- get review report by task ID。
- return 404 for missing task。
- return validation error for invalid URL。

`test_review_graph.py`

- graph returns report for valid demo PR URL。
- graph writes parsed PR into state。
- graph calls Mock Provider and includes PR metadata in report。
- graph returns deterministic mock summary, findings, suggestions, and test recommendations。
- graph handles invalid PR URL without producing a succeeded report。

### 11.2 前端检查

- `npm run typecheck`
- `npm run build`
- 手动输入合法 URL，确认页面渲染 Mock 报告。
- 手动输入非法 URL，确认错误提示。

## 12. 第 1 天建议 PR 拆分

为了符合比赛“持续 PR 和 commit”的规则，第 1 天建议拆成 4 个 PR。

### PR-001 Project foundation

内容：

- 初始化后端和前端目录。
- 增加 health/version 接口。
- 增加 README 初版。

PR 描述重点：

- 功能描述：创建项目基础结构。
- 实现思路：FastAPI + Vue 3 分离式架构。
- 测试方式：health endpoint、本地启动。

### PR-002 PR URL parser and schemas

内容：

- 增加 Pydantic Schema。
- 实现 GitHub PR URL 解析。
- 增加 parser 单元测试。

PR 描述重点：

- 功能描述：支持解析 GitHub PR URL。
- 实现思路：使用 URL parser 提取 owner、repo、PR number。
- 测试方式：合法 URL、非法 URL、非 GitHub URL。

### PR-003 Mock review API

内容：

- 增加 Provider 抽象。
- 增加 Mock GitHub Provider。
- 增加 LangGraph Review Workflow 骨架。
- 增加 Review Service。
- 增加创建任务和查询报告接口。

PR 描述重点：

- 功能描述：提供 Demo Mode Review API，并通过 LangGraph 节点链路生成报告。
- 实现思路：使用 `parse_pr_url -> fetch_mock_pr -> generate_mock_review -> assemble_report` 四节点工作流，结合内存任务存储保存结果。
- 测试方式：Workflow 输出、创建任务、查询结果、任务不存在。

### PR-004 Frontend review workspace

内容：

- 增加前端 API 封装。
- 增加输入面板、元数据面板、摘要、风险和建议组件。
- 接入 Mock Review API。

PR 描述重点：

- 功能描述：完成第 1 天可演示页面。
- 实现思路：单页 Dashboard，输入 URL 后调用后端渲染报告。
- 测试方式：本地启动前后端，输入 Demo PR URL 验证完整流程。

## 13. 第 1 天完成标准

第 1 天结束前，必须满足：

- 后端服务可以启动。
- 前端页面可以启动。
- 输入 `https://github.com/acme/codepilot/pull/12` 后可以看到完整 Mock Review 报告。
- README 能让评委或同学按步骤启动项目。
- 至少有 3 到 4 个小粒度 PR 记录。
- 主分支合并后保持可运行。
- 已经有 LangGraph 节点工作流骨架，但没有把第 2 天才做的真实 GitHub、LLM 和复杂上下文能力硬塞进第 1 天。

## 14. 第 2 天承接点

第 1 天结束后，第 2 天可以自然扩展：

- 将 `MockGitHubProvider` 替换或并行为 `GitHubProvider`。
- 扩展第 1 天已有 LangGraph Workflow，将 `fetch_mock_pr` 替换为真实 GitHub 获取节点。
- 将固定 summary、findings、suggestions 节点改为 LLM 结构化生成节点。
- 将任务状态从同步成功改为 queued、running、succeeded、failed。
- 增加 SSE 或 WebSocket 输出节点进度。
- 增加上下文收集器，从 changed files 中提取附近函数和相关测试文件。
