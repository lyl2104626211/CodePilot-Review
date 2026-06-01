# 模型与上下文策略

## 模型选择策略

### 两层架构

1. **快速模型** (FallbackLLMClient)
   - 使用场景：无 API Key 或 Demo 模式
   - 实现方式：基于 PR 文件路径、增删行数、模块类型做规则判断
   - 确定性输出：同一输入始终返回相同结果
   - 优点：不依赖外部 API，零延迟，稳定可演示

2. **强推理模型** (OpenAICompatibleLLMClient)
   - 使用场景：配置 MODEL_API_KEY 后自动启用
   - 默认模型：deepseek-v4-pro
   - 兼容任意 OpenAI 兼容 API（DashScope、vLLM 等）
   - 参数：temperature=0.3, max_tokens=4096
   - JSON 提取失败时自动重试一次

### 切换逻辑

`review_service.py` 中的 `_create_llm_client()` 工厂函数：
```python
if settings.model_api_key:
    return OpenAICompatibleLLMClient(...)  # 真实模型
return FallbackLLMClient()  # 规则降级
```

### Prompt 设计原则

- **中文输出**：所有 Prompt 要求中文，贴合国内开发者习惯
- **结构化 JSON**：每个 Prompt 附完整输出 Schema
- **证据驱动**：要求每条 risk finding 包含 evidence 和 reasoning
- **反幻觉**：明确要求"不要编造 diff 中不存在的业务背景"

## 上下文获取策略

### 数据来源优先级

1. **PR diff** (最高优先级) — 变更的精确内容
2. **变更文件元数据** — 路径、状态、增删行数
3. **文件内容摘要** (预留) — GitHub API 获取当前文件内容
4. **关联测试文件** — 路径模式推测可能相关的测试
5. **PR 元数据** — 标题、作者、分支信息

### 上下文预算控制

- 单文件 patch 上限：6,000 字符
- 总上下文上限：24,000 字符
- 超出预算时 patch 置空但保留文件元数据
- 二进制文件（图片、字体、压缩包等）自动跳过

### 文件分类

通过路径模式匹配，不依赖 AST 解析：
- `backend`: 后端代码 (app/, services/, .py)
- `frontend`: 前端代码 (frontend/, .vue, .tsx, .css)
- `tests`: 测试文件 (test_, tests/, __tests__)
- `config`: 配置文件 (.toml, .yaml, .env)
- `docs`: 文档 (.md, docs/)
- `unknown`: 其他

## 误报与漏报控制

### 三道护栏

1. **置信度过滤** (guardrail_check)
   - 默认隐藏 confidence < 0.45 的发现
   - 前端可手动切换 LOW CONF 显示

2. **证据约束**
   - critical/high 级别的发现必须有明确代码证据
   - evidence 字段少于 10 字符的自动过滤

3. **去重检查**
   - 按标题归一化去重
   - 避免 LLM 生成多个相同的发现

### 报告可信度说明

- 使用 FallbackLLM 时前端显示 warning："当前为规则兜底分析"
- 低置信度发现明确标注 confidence 百分比
- 每个发现包含 evidence 和 reasoning，供人工验证

## 延迟优化

- 文件级 patch 截断控制 Token 消耗
- LLM 调用分离为 3 个独立节点（summary / risks / suggestions）
  便于第 3 天接入流式输出后分别推送部分结果
- Demo 模式 4 节点链路零网络依赖，响应时间 < 50ms

## 未来扩展

- 引入 AST 解析获取函数/类级别上下文
- 多模型交叉验证降低误报
- 模型输出缓存减少重复分析
- 支持代码调用链分析
- 异步流式输出（SSE/WebSocket）
