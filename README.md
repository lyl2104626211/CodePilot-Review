# CodePilot Review

AI 辅助 GitHub PR Review 工具 — 输入 PR 链接，自动获取变更、生成总结、识别风险、输出 Review 建议。

**选题方向**：题目三 — AI PR Review 助手

## 产品概述

CodePilot Review 面向开发者和代码评审者，帮助快速理解 PR 变更意图、发现潜在风险、生成有证据支撑的 Review 建议。它不是替代人工 Review，而是评审前置助手。

### 核心功能

- GitHub PR URL 解析与 PR 元数据获取
- PR diff 与代码上下文收集
- 基于 AI 工作流的 PR 变更总结
- 多维度风险代码识别（正确性、安全、性能、兼容性等）
- 可执行的 Review 建议与测试建议
- 流式分析进度展示
- Demo 模式（Mock 数据，无需 GitHub Token 或模型 API）

### 目标用户

- 后端、前端、全栈开发者
- 需要频繁 Review PR 的团队成员
- 开源项目维护者

## 架构概览

```text
codepilot-review/
├── backend/          # FastAPI + LangGraph
│   ├── app/api/      # REST API 层
│   ├── app/schemas/  # Pydantic 数据模型
│   ├── app/services/ # 业务逻辑
│   ├── app/workflows/# LangGraph 工作流
│   ├── app/providers/# GitHub Provider（含 Mock）
│   └── app/storage/  # 任务存储
├── frontend/         # Vue 3 + Vite + TypeScript
│   └── src/
│       ├── api/      # API 封装
│       ├── components/# UI 组件
│       └── types/    # TypeScript 类型
├── agents/           # 项目 PRD
└── docs/             # 每日开发计划
```

## 使用流程

1. 打开 CodePilot Review 工作台
2. 输入 GitHub PR URL（如 `https://github.com/acme/codepilot/pull/12`）
3. 系统解析 PR 并获取 diff 和上下文
4. AI 工作流生成总结、风险识别、Review 建议
5. 在 Dashboard 中查看结构化评审报告

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

### Demo 模式

第 1 天默认为 Demo 模式，使用 Mock 数据。无需配置 GitHub Token 或模型 API，输入任意合法格式的 GitHub PR URL 即可看到完整的 Mock Review 报告。

## 第三方依赖

### 后端

| 依赖 | 用途 |
|------|------|
| FastAPI | Web 框架 |
| Uvicorn | ASGI 服务器 |
| Pydantic v2 | 数据校验与 Schema |
| pydantic-settings | 环境变量管理 |
| LangGraph | AI 工作流编排 |
| httpx | HTTP 客户端（测试与 API 调用） |
| pytest | 测试框架 |
| pytest-asyncio | 异步测试支持 |

### 前端

| 依赖 | 用途 |
|------|------|
| Vue 3 | 前端框架 |
| Vite | 构建工具 |
| TypeScript | 类型系统 |

### 外部服务（后续接入）

- GitHub REST API — PR 数据获取
- DeepSeek API (deepseek-v4-pro) — AI 分析

## 第 1 天进度

- [x] 项目初始化，Git 仓库与目录结构
- [x] 后端 FastAPI 基础 (health/version API, CORS)
- [x] Pydantic Schema 定义
- [x] GitHub PR URL 解析
- [x] Mock GitHub Provider
- [x] LangGraph Review Workflow 骨架
- [x] Review API (创建任务 + 查询报告)
- [x] 前端 Vue 3 Dashboard
- [x] 后端 11 个测试全部通过
- [x] 前端 typecheck 通过
