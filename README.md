# CodePilot Review

AI 辅助 GitHub PR Review 工具 — 输入 PR 链接，自动获取变更、生成总结、识别风险、输出 Review 建议。

**选题方向**：题目三 — AI PR Review 助手

## 产品概述

CodePilot Review 面向开发者和代码评审者，帮助快速理解 PR 变更意图、发现潜在风险、生成有证据支撑的 Review 建议。它不是替代人工 Review，而是评审前置助手。

### 核心功能

- GitHub PR URL 解析与 PR 元数据获取
- PR diff 与代码上下文收集（文件分类、关联测试识别、上下文预算控制）
- 基于 LangGraph 的 AI 工作流（9 节点完整链路）
- LLM 驱动的 PR 变更总结、风险识别、Review 建议和测试建议
- Demo 模式（Mock 数据 + Fallback 规则分析，无需 Token 或 API Key）
- GitHub 模式（真实 GitHub API + 可选 DeepSeek/OpenAI 兼容模型）
- 前端 Dashboard：模式切换、进度展示、风险过滤

### 目标用户

- 后端、前端、全栈开发者
- 需要频繁 Review PR 的团队成员
- 开源项目维护者

## 架构概览

```text
codepilot-review/
├── backend/              # FastAPI + LangGraph
│   ├── app/api/          # REST API 层
│   ├── app/schemas/      # Pydantic 数据模型
│   ├── app/services/     # 业务逻辑
│   ├── app/workflows/    # LangGraph 工作流 (9 节点)
│   │   └── nodes/        # 每个节点一个文件
│   ├── app/providers/    # GitHub Provider (Mock + 真实)
│   ├── app/context/      # 代码上下文收集器
│   ├── app/llm/          # LLM 客户端 (Fallback + OpenAI 兼容)
│   └── app/storage/      # 任务存储
├── frontend/             # Vue 3 + Vite + TypeScript
│   └── src/
│       ├── api/          # API 封装
│       ├── components/   # 8 个 UI 组件
│       └── types/        # TypeScript 类型
├── agents/               # 项目 PRD
└── docs/                 # 每日开发计划
```

## 两种运行模式

| 特性 | Demo 模式 | GitHub 模式 |
|------|----------|------------|
| PR 数据 | Mock 固定数据 | 真实 GitHub API |
| AI 分析 | Fallback 规则判断 | LLM 模型（需 API Key）或 Fallback |
| GitHub Token | 不需要 | 公开仓库不需要，私有仓库需要 |
| 模型 API Key | 不需要 | 可选，未配置时自动降级为 Fallback |
| 工作流 | 4 节点 | 9 节点完整链路 |

## 使用流程

1. 打开 CodePilot Review 工作台
2. 选择 Demo 或 GitHub 模式
3. 输入 GitHub PR URL（如 `https://github.com/owner/repo/pull/12`）
4. 系统解析 PR，获取 diff 和代码上下文
5. AI 工作流生成总结、风险识别、Review 建议和测试建议
6. 在 Dashboard 中查看结构化评审报告，按严重程度过滤风险

## 本地开发

### 环境要求

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/)（Python 包管理）

### 后端启动

```bash
cd backend
cp ../.env.example .env
uv sync
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

服务运行在 `http://localhost:8000`

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

页面运行在 `http://localhost:5173`，通过 Vite proxy 转发 `/api` 请求到后端。

### 运行测试

```bash
# 后端测试
cd backend
uv sync --extra dev
.venv/Scripts/python.exe -m pytest tests/ -v

# 前端类型检查
cd frontend
npm run typecheck
```

## 环境变量配置

参考 `.env.example` 文件：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `GITHUB_TOKEN` | GitHub Token（私有仓库需要） | 空 |
| `MODEL_PROVIDER` | 模型供应商 | `deepseek` |
| `MODEL_NAME` | 模型名称 | `deepseek-v4-pro` |
| `MODEL_BASE_URL` | 模型 API 地址 | `https://api.deepseek.com/v1` |
| `MODEL_API_KEY` | 模型 API Key（不配置则用 Fallback） | 空 |
| `DEMO_MODE` | Demo 模式开关 | `true` |

## 第三方依赖

### 后端

| 依赖 | 用途 |
|------|------|
| FastAPI | Web 框架 |
| Uvicorn | ASGI 服务器 |
| Pydantic v2 | 数据校验与 Schema |
| pydantic-settings | 环境变量管理 |
| LangGraph | AI 工作流编排 |
| loguru | 日志管理 |
| httpx | HTTP 客户端 |

### 前端

| 依赖 | 用途 |
|------|------|
| Vue 3 | 前端框架 |
| Vite | 构建工具 |
| TypeScript | 类型系统 |

### 外部服务

- GitHub REST API — PR 数据获取
- DeepSeek API（或任意 OpenAI 兼容接口）— AI 分析（可选，不配置则使用 Fallback）

## Day 2 完成进度

- [x] 真实 GitHub Provider（公开/私有仓库，错误映射）
- [x] 代码上下文收集器（文件分类、关联测试、预算控制）
- [x] LLM 层（Fallback 规则 + OpenAI 兼容客户端 + Prompt 模板）
- [x] 9 节点 LangGraph 工作流（collect_context → generate_summary → detect_risks → generate_suggestions → guardrail_check）
- [x] 质量护栏（低置信度/无证据/重复标题过滤）
- [x] 前端模式切换、进度展示、风险过滤
- [x] 后端 42 个测试全部通过
- [x] 前端 typecheck 通过
