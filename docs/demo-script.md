# CodePilot Review Demo 脚本

## 演示目标

展示 CodePilot Review 从输入 PR URL 到生成结构化 Review 建议的完整闭环。

总时长：5-8 分钟

## 演示环境准备

- 后端服务已启动: `cd backend && uv run uvicorn app.main:app --reload`
- 前端服务已启动: `cd frontend && npm run dev`
- 浏览器打开 `http://localhost:5173`

## Demo 流程

### 1. 打开首页（30 秒）

- 展示 Terminal Noir 风格界面
- 说明 CodePilot Review 是 AI PR Review 助手
- 左侧边栏、顶栏 MOCK/LIVE 模式切换

### 2. Demo 模式演示（1.5 分钟）

- 选择 MOCK 模式
- 输入示例 PR URL: `https://github.com/acme/codepilot/pull/12`
- 点击 Run Review
- 展示 8 阶段进度条动画
- 展示分析结果：
  - PR DETAILS 元数据
  - SUMMARY 变更总结
  - RISKS 风险列表（severity/category/evidence/confidence）
  - SUGGESTIONS 建议列表
  - TESTS 测试建议

### 3. 风险过滤和质量摘要（30 秒）

- 展示 SEV 过滤按钮，按严重程度筛选
- 展示 LOW CONF 开关，隐藏低置信度发现
- 展示质量摘要面板（High Conf / Low Conf / Blocking 数量）

### 4. GitHub 模式演示（1.5 分钟）

- 切换到 LIVE 模式
- 输入真实公开 PR URL，如 `https://github.com/tiangolo/fastapi/pull/10000` 或类似
- 系统从 GitHub API 获取真实 PR 元数据、diff
- 展示真实 PR 标题、作者、分支、文件变更
- 展示 LLM 生成的结构化分析结果
- 若 GitHub API 失败/限流，展示错误状态和兜底方案

### 5. 模拟 Review 评论（1.5 分钟）

- 在 SUGGESTIONS 区域勾选若干条建议
- 点击 GENERATE 生成模拟 GitHub Review 评论
- 展示 GitHub 风格评论预览（深色代码仓库风格）
- 展示每条评论的 BLOCK/SUGGEST 标记
- 点击 COPY MD 复制完整 Markdown
- 点击 DOWNLOAD 下载 .md 文件
- 说明：当前为模拟发布，后续可扩展为真实 GitHub Review API

### 6. 技术亮点讲解（1 分钟）

- LangGraph 9 节点工作流
- Provider 抽象（Mock + GitHub 双实现）
- LLM 客户端工厂（API Key 自动切换 + Fallback 降级）
- 上下文收集器（文件分类、关联测试、预算控制）
- 质量护栏（低置信度过滤、证据检查、标题去重）

### 7. 扩展方向（30 秒）

- 真实 GitHub inline review 发布
- GitLab / Gitee 多平台支持
- 组织级 Review 规则配置
- CI 集成自动触发分析
- 持久化历史 Review 记录

## 失败兜底方案

| 场景 | 兜底 |
|------|------|
| GitHub API 限流 | 切回 Demo 模式，展示 Mock 数据 |
| LLM API 不可用 | FallbackLLM 自动生效，展示 warning 说明 |
| 网络故障 | 使用提前录制的截图/视频片段 |
| 前端崩溃 | 刷新页面，重新输入 URL |

## Demo 用 PR URL 备选

- Mock: `https://github.com/acme/codepilot/pull/12` (稳定)
- 公开 PR (小): `https://github.com/psf/requests/pull/6000`
- 公开 PR (中): `https://github.com/tiangolo/fastapi/pull/10060`
