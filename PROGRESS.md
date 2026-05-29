# CodePilot Review — 项目进度

## 当前状态

| 项目 | 状态 |
|------|------|
| 第 1 天 (Day 1) | 🟡 进行中 |
| 第 2 天 (Day 2) | ⚪ 待定 |
| 第 3 天 (Day 3) | ⚪ 待定 |

## PR 记录

| PR 编号 | 标题 | 状态 | 日期 |
|---------|------|------|------|
| PR-001 | feat: initialize CodePilot Review project foundation | ✅ 已合并 | 2026-05-29 |

## 第 1 天待办

- [x] 初始化 Git 仓库 + 关联远程
- [x] 后端 FastAPI 项目 (health/version API, CORS, config)
- [x] Pydantic Schema (common, github, review)
- [x] GitHub PR URL 解析 + 单元测试
- [x] Mock GitHub Provider
- [x] LangGraph Workflow 骨架 (4 nodes in `workflows/nodes/`)
- [x] Review Service + Memory Store
- [x] Review API (POST /api/reviews, GET /api/reviews/{id}, POST /api/reviews/parse)
- [x] 前端 Vue 3 + Vite + TypeScript Dashboard
- [x] 前端 5 组件 (PrInputPanel, PrMetaPanel, ReviewSummary, RiskList, SuggestionList)
- [x] README 初版 + .env.example + .gitignore
- [x] 后端 11 个测试通过
- [x] 前端 typecheck 通过
- [x] Push 到远程 `git@github.com:lyl2104626211/CodePilot-Review.git`

## 技术信息

| 项目 | 说明 |
|------|------|
| 远程仓库 | `git@github.com:lyl2104626211/CodePilot-Review.git` |
| Python 包管理 | uv |
| 大模型 | deepseek-v4-pro (dpv4pro) |

## 备注

- 项目开始日期：2026-05-29
- 每次 PR 务必 push 到远程，不能只提交本地
- 详细 PRD：[agents/prd.md](agents/prd.md) / [agents/prd.json](agents/prd.json)
- Day 1 详细计划：[docs/plans/day1-development.md](docs/plans/day1-development.md)
