# CodePilot Review — 项目进度

## 当前状态

| 项目 | 状态 |
|------|------|
| 第 1 天 (Day 1) | ✅ 已完成 |
| 第 2 天 (Day 2) | ✅ 已完成 |
| 第 3 天 (Day 3) | ⚪ 待定 |

## PR 记录

| PR 编号 | 标题 | 状态 | 日期 |
|---------|------|------|------|
| PR-001 | feat: initialize CodePilot Review project foundation | ✅ 已合并 | 2026-05-29 |
| PR-005 | 修复: Day1 质量补全 | 🔵 待合并 | 2026-05-29 |
| PR-006 | 新增: 真实 GitHub Provider | 🔵 待合并 | 2026-05-29 |
| PR-007 | 新增: 代码上下文收集器 | 🔵 待合并 | 2026-05-29 |
| PR-008 | 新增: LLM 结构化分析节点与工作流重构 | 🔵 待合并 | 2026-05-29 |
| PR-009 | 新增: Day2 前端集成 | 🔵 待合并 | 2026-05-29 |

## Day 2 完成项

- [x] 真实 GitHub Provider（公开/私有仓库，异常映射）
- [x] Provider 异常体系（NotFound / Unauthorized / RateLimit / ProviderError）
- [x] fork PR owner/repo 映射修复（使用 base.repo）
- [x] GitHubProvider 连接关闭（try/finally）
- [x] 代码上下文收集器（文件分类、关联测试、预算控制、二进制跳过）
- [x] LLM 层（Protocol 抽象 + Fallback 规则 + OpenAI 兼容 + 三套 Prompt）
- [x] LLM 客户端工厂函数（根据 MODEL_API_KEY 自动选择）
- [x] 9 节点 LangGraph 工作流
- [x] 质量护栏节点（低置信度/无证据/重复标题过滤）
- [x] LLM 节点异常健壮性（LLMError + ValueError + TypeError 三层兜底）
- [x] 前端模式切换组件（Demo / GitHub）
- [x] 前端进度时间线组件
- [x] 前端风险过滤组件（严重程度 + 低置信度隐藏）
- [x] ReviewReport 新增 warnings 字段
- [x] .env.example 补充 MODEL_BASE_URL / MODEL_API_KEY
- [x] 后端 42 个测试全部通过
- [x] 前端 typecheck 通过

## 技术信息

| 项目 | 说明 |
|------|------|
| 远程仓库 | `git@github.com:lyl2104626211/CodePilot-Review.git` |
| Python 包管理 | uv |
| 大模型 | deepseek-v4-pro (dpv4pro) |
| 日志 | loguru（控制台 + 文件双输出） |

## 备注

- 项目开始日期：2026-05-29
- 详细 PRD：[agents/prd.md](agents/prd.md) / [agents/prd.json](agents/prd.json)
- Day 1 计划：[docs/plans/day1-development.md](docs/plans/day1-development.md)
- Day 2 计划：[docs/plans/day2-development.md](docs/plans/day2-development.md)
