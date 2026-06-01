# CodePilot Review

AI 辅助 GitHub PR Review 工具 — 输入 PR 链接，自动获取变更、生成总结、识别风险、输出 Review 建议并生成模拟 GitHub 评论。

**选题方向**：题目三 — AI PR Review 助手

## 产品概述

CodePilot Review 面向开发者和代码评审者，帮助快速理解 PR 变更意图、发现潜在风险、生成有证据支撑的 Review 建议。它不是替代人工 Review，而是评审前置助手。

**完整闭环**：输入 PR URL → 分析进度展示 → 结构化报告（总结/风险/建议）→ 勾选建议 → 生成 GitHub 风格模拟评论 → 复制/导出 Markdown。

### 核心功能

- GitHub PR URL 解析，自动获取 PR 元数据、diff、变更文件
- 代码上下文收集（文件分类、关联测试识别、上下文预算控制）
- LangGraph 9 节点 AI 工作流：解析 → 获取 → 上下文 → 总结 → 风险 → 建议 → 护栏 → 报告
- LLM 驱动的 PR 总结、风险识别（7 类）、Review 建议和测试建议
- **模拟 GitHub Review 评论生成**：勾选建议 → 生成评论草稿 → 复制/下载 Markdown
- 报告质量摘要：置信度分布、阻塞建议数、fallback 说明
- 质量护栏：低置信度过滤、证据检查、标题去重
- 两种运行模式：Demo（零配置 Mock） / GitHub（真实 API + AI 模型）
- Terminal Noir 深色工业风前端界面

### 目标用户

- 后端、前端、全栈开发者
- 需要频繁 Review PR 的团队成员
- 开源项目维护者

## 两种运行模式

| 特性 | Demo 模式 | GitHub 模式 |
|------|----------|------------|
| PR 数据 | Mock 固定数据 | 真实 GitHub REST API |
| AI 分析 | Fallback 规则判断 | LLM 模型（需 API Key）或 Fallback |
| GitHub Token | 不需要 | 公开仓库不需要，私有仓库需要 GITHUB_TOKEN |
| 模型 API Key | 不需要 | 可选，未配置时自动降级为 Fallback |
| 工作流节点 | 4 节点 | 9 节点完整链路 |
| 评论生成 | 支持 | 支持 |

## 技术架构

```text
codepilot-review/
├── backend/               # FastAPI + LangGraph
│   ├── app/api/           # REST API (health, reviews, parse, comments, export)
│   ├── app/schemas/       # Pydantic 数据模型
│   ├── app/services/      # 业务逻辑 (pr_parser, review_service, review_comment_service)
│   ├── app/workflows/     # LangGraph 工作流 (9 节点)
│   │   └── nodes/         # 每个节点一个文件，职责单一
│   ├── app/providers/     # GitHub Provider (Mock + 真实 GitHub API)
│   ├── app/context/       # 代码上下文收集器（文件分类 + 关联测试）
│   ├── app/llm/           # LLM 客户端 (Fallback 规则 + OpenAI 兼容)
│   ├── app/storage/       # 内存任务存储
│   └── tests/             # 52 个单元测试
├── frontend/              # Vue 3 + Vite + TypeScript
│   └── src/
│       ├── api/           # API 封装 (6 个接口)
│       ├── components/    # 13 个 UI 组件
│       └── types/         # TypeScript 类型定义
├── agents/                # 项目 PRD
├── docs/                  # 开发计划 + 演示脚本 + 验收清单
└── README.md
```

## LangGraph 工作流

```
Demo 模式 (4 节点):
  parse_pr_url → fetch_pr (Mock) → generate_mock_review → assemble_report

GitHub 模式 (9 节点):
  parse_pr_url → fetch_pr (GitHub API) → collect_context
  → generate_summary (LLM) → detect_risks (LLM) → generate_suggestions (LLM)
  → guardrail_check → assemble_report
```

评论生成独立于 Review Graph，作为报告产出的用户交互步骤，不混入自动分析流程。

## 模型选择与 Fallback 策略

系统通过 `_create_llm_client()` 工厂函数自动选择 LLM 客户端：

- **配置 MODEL_API_KEY** → 使用 OpenAI 兼容客户端（DeepSeek / DashScope / vLLM 等）
- **未配置 API Key** → 使用 FallbackLLMClient（基于 PR 文件路径和变更类型的规则判断）

Fallback 输出虽不如模型精细，但结构完整，前端可正常渲染。所有 Fallback 情况会在报告中标注 warning。

详见 [模型与上下文策略文档](docs/model-context-strategy.md)。

## 本地启动

### 环境要求

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/)

### 后端

```bash
cd backend
cp ../.env.example .env
uv sync
uv sync --extra dev
uv run uvicorn app.main:app --reload
# → http://localhost:8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 运行测试

```bash
cd backend
uv sync --extra dev
.venv/Scripts/python.exe -m pytest tests/ -v   # 52 tests

cd frontend
npm run typecheck   # vue-tsc --noEmit
npm run build       # vite build
```

## 环境变量

参考 `.env.example`：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `GITHUB_TOKEN` | GitHub Token（私有仓库需要） | 空 |
| `MODEL_BASE_URL` | 模型 API 地址 | `https://api.deepseek.com/v1` |
| `MODEL_API_KEY` | 模型 API Key（不配置则用 Fallback） | 空 |
| `MODEL_NAME` | 模型名称 | `deepseek-v4-pro` |
| `DEMO_MODE` | Demo 模式开关 | `true` |

## API 接口一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/version` | 版本信息 |
| POST | `/api/reviews/parse` | 解析 PR URL |
| POST | `/api/reviews` | 创建 Review 任务 |
| GET | `/api/reviews/{id}` | 查询完整报告 |
| GET | `/api/reviews/{id}/status` | 查询任务状态 |
| GET | `/api/reviews/{id}/quality` | 报告质量摘要 |
| POST | `/api/reviews/{id}/comments` | 生成模拟评论 |
| GET | `/api/reviews/{id}/export.md` | 导出 Markdown |

## 第三方依赖

### 后端

| 依赖 | 用途 |
|------|------|
| FastAPI | Web 框架 |
| Uvicorn | ASGI 服务器 |
| Pydantic v2 | 数据校验 |
| pydantic-settings | 环境变量管理 |
| LangGraph | AI 工作流编排 |
| loguru | 日志管理（控制台 + 文件双输出） |
| httpx | HTTP 客户端 |

### 前端

| 依赖 | 用途 |
|------|------|
| Vue 3 | 前端框架 |
| Vite | 构建工具 |
| TypeScript | 类型系统 |

### 外部服务

- **GitHub REST API** — PR 数据获取（公开仓库无需 Token）
- **DeepSeek API**（或任意 OpenAI 兼容接口）— AI 分析（可选，不配置则 Fallback）

## 已知限制

- 当前模拟 Review 评论不会真实提交到 GitHub（设计选择，避免误操作）
- 上下文收集基于路径模式匹配，不使用 AST 解析
- 内存任务存储，重启后历史记录丢失
- 未实现 SSE/WebSocket 实时流式进度

## 未来扩展

- 接入真实 GitHub Review API，支持人工确认后发布 inline comments
- SSE/WebSocket 实时流式进度推送
- 持久化数据库存储历史 Review
- AST/调用链级别代码上下文增强
- 多模型交叉验证降低误报
- GitLab、Gitee 多平台支持
- 组织级 Review 规则配置
- CI 集成自动触发分析

## 开发记录

- Day 1 (5/29): 项目初始化、Mock 全链路、前端 Dashboard
- Day 2 (5/29-30): 真实 GitHub Provider、上下文收集器、LLM 分析节点、9 节点工作流、前端集成
- Day 3 (5/30): 模拟评论生成、质量摘要、状态组件、文档收尾、最终打磨

详细 PR 记录见 [PROGRESS.md](PROGRESS.md)。演示脚本见 [docs/demo-script.md](docs/demo-script.md)。
