# CodePilot Review 最终验收清单

## 代码检查

- [ ] 后端测试通过 (`cd backend && .venv/Scripts/python.exe -m pytest tests/ -v`)
- [ ] 前端 typecheck 通过 (`cd frontend && npm run typecheck`)
- [ ] 前端 build 通过 (`cd frontend && npm run build`)
- [ ] Demo 模式稳定可用（Mock Provider + FallbackLLM）
- [ ] GitHub 模式可分析公开 PR（GitHubProvider + LLM）
- [ ] 评论生成可用（勾选建议 + 生成 markdown）
- [ ] Markdown 导出可用（COPY + DOWNLOAD）

## 文档检查

- [ ] README 最终版完成（包含选题、功能、架构、启动、配置、依赖、扩展）
- [ ] PROGRESS 更新 Day3 状态和 PR 记录
- [ ] `docs/demo-script.md` 演示脚本完成
- [ ] `docs/final-checklist.md` 验收清单完成（本文件）
- [ ] `.env.example` 包含所有环境变量
- [ ] README 明确声明 Demo / GitHub 模式差异
- [ ] README 明确声明第三方依赖和外部服务
- [ ] README 明确 Fallback 行为和模型配置

## 比赛规则检查

- [ ] 所有功能通过 PR 提交（3 天共 10+ 个 PR）
- [ ] 每个 PR 标题和描述完整（标题 + 功能描述 + 实现思路 + 测试方式）
- [ ] 主分支合并后保持可运行
- [ ] commit 时间在比赛周期内
- [ ] 没有最后一天一次性大提交
- [ ] 公开仓库可访问
- [ ] README 声明了所有第三方依赖
- [ ] 如有复用代码，已在 PR 或 README 注明来源

## 作品核心检查

- [ ] 支持 GitHub PR URL 输入和解析
- [ ] 支持 Demo 模式和 GitHub 模式
- [ ] 能获取真实 PR 元数据、diff、变更文件
- [ ] 能生成 PR 变更总结
- [ ] 能识别风险代码并分类（severity + category + evidence + confidence）
- [ ] 能生成可执行的 Review 建议和测试建议
- [ ] 有质量护栏（低置信度过滤、证据检查）
- [ ] 有进度展示（时间线）
- [ ] 有风险过滤
- [ ] 有模拟 Review 评论生成
- [ ] 有 Markdown 复制/下载
- [ ] 有错误状态、空状态、warnings 展示
- [ ] 已完成 Demo 视频录制

## 作品亮点（答辩重点）

1. **LangGraph 9 节点工作流** — 每个节点独立可替换，可观测
2. **Provider 双实现** — Mock + GitHub 无缝切换
3. **LLM 双模式** — API Key 自动切换 + Fallback 规则降级
4. **质量护栏** — 置信度/证据/去重三道过滤
5. **上下文增强** — 文件分类 + 关联测试识别 + 预算控制
6. **Terminal Noir 设计** — 深色工业风，专业开发者工具感
7. **模拟 Review 评论** — GitHub 风格预览 + 复制/导出
