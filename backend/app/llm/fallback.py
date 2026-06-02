"""Fallback LLM Client：无 API Key 时的确定性降级方案

不调用任何外部 API，根据 PR 元数据生成结构化的分析结果。
核心逻辑：基于文件路径、增删行数、变更类型做规则判断。
"""
from app.core.logger import logger
from app.llm.base import LLMClient


class FallbackLLMClient:
    """Fallback LLM：基于规则生成分析结果，不依赖模型 API

    所有输出都是确定性的，确保 Demo 模式稳定演示。
    分析逻辑虽然简单，但输出结构完整，前端可以正常渲染。
    """

    async def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str = "") -> dict:
        """根据 schema_name 生成对应的结构化结果"""
        logger.info("Fallback LLM 生成 | schema={}", schema_name)

        if "summary" in schema_name.lower():
            return self._generate_summary(user_prompt)
        elif "risk" in schema_name.lower() or "finding" in schema_name.lower():
            return self._generate_findings(user_prompt)
        elif "suggestion" in schema_name.lower():
            return self._generate_suggestions(user_prompt)
        elif "patch" in schema_name.lower():
            return self._generate_patch_fallback(user_prompt)
        else:
            return {"message": "No fallback available for this schema"}

    def _generate_summary(self, _prompt: str) -> dict:
        return {
            "overview": "本 PR 对后端服务和测试模块进行了变更，包含新增、修改等多种改动。",
            "changed_modules": ["backend", "tests"],
            "reviewer_focus": [
                "接口错误处理是否完整",
                "新增代码的测试覆盖是否充分",
                "是否存在潜在的兼容性问题",
                "数据校验和边界条件处理",
            ],
        }

    def _generate_findings(self, _prompt: str) -> dict:
        findings = []
        risk_id = 1

        # 基于文件列表做简单的启发式检测（Fallback 模式，无 LLM API）
        # _prompt 包含文件路径列表，如 "- [backend] app/services/foo.py (added, +10 -0)"
        prompt_lower = _prompt.lower()
        has_py_files = ".py" in prompt_lower
        has_added = "added" in prompt_lower or "new file" in prompt_lower
        has_test_files = any(pat in prompt_lower for pat in ["test_", "_test", "tests/", "test/", "spec/", "__tests__/"])
        has_modified = "modified" in prompt_lower

        if has_py_files and has_added and not has_test_files:
            findings.append({
                "id": f"risk_{risk_id:03d}",
                "severity": "medium",
                "category": "missing_tests",
                "file_path": "backend/app/",
                "line": None,
                "title": "新增后端文件缺少对应测试",
                "evidence": "PR 中新增了后端代码文件，但未发现对应的测试文件变更。",
                "reasoning": "新功能缺少测试覆盖可能在后续迭代中引入回归问题。",
                "confidence": 0.75,
            })
            risk_id += 1

        # 检查是否有代码修改
        if has_modified:
            findings.append({
                "id": f"risk_{risk_id:03d}",
                "severity": "low",
                "category": "correctness",
                "file_path": "backend/app/",
                "line": None,
                "title": "建议关注修改文件的异常处理路径",
                "evidence": "变更文件包含服务层代码，建议确认异常分支覆盖。",
                "reasoning": "服务层代码修改可能影响调用方的异常处理逻辑。",
                "confidence": 0.60,
            })
            risk_id += 1

        if not findings:
            findings.append({
                "id": "risk_001",
                "severity": "low",
                "category": "observability",
                "file_path": "",
                "line": None,
                "title": "未检测到明显风险",
                "evidence": "基于变更文件分析，未发现高置信度风险。",
                "reasoning": "本次变更范围较小或无敏感文件变更。",
                "confidence": 0.50,
            })

        return {"findings": findings}

    def _generate_suggestions(self, _prompt: str) -> dict:
        return {
            "suggestions": [
                {
                    "id": "suggestion_001",
                    "finding_id": "risk_001",
                    "file_path": "backend/app/",
                    "comment": "建议为新增接口补充单元测试，覆盖正常路径和异常路径。",
                    "rationale": "新增代码若无测试覆盖，在后续迭代中容易引入回归 bug。",
                    "suggested_fix": "在 tests/ 目录下新增对应的 test_<module>.py 文件。",
                    "blocking": False,
                },
                {
                    "id": "suggestion_002",
                    "finding_id": "risk_002",
                    "file_path": "",
                    "comment": "建议在代码评审时关注异常处理的完整性。",
                    "rationale": "服务层代码的异常处理直接影响 API 的稳定性。",
                    "suggested_fix": "逐一检查每个新增函数的 try/except 覆盖范围。",
                    "blocking": False,
                },
            ],
            "test_recommendations": [
                "为新增的 API 端点编写单元测试和集成测试",
                "测试异常场景：无效参数、服务不可用、超时",
                "验证 API 返回的错误码和消息格式是否符合规范",
            ],
        }

    def _generate_patch_fallback(self, prompt: str) -> dict:
        """基于 prompt 内容生成 Fallback 修复代码预览"""
        # 从 prompt 中提取一些上下文线索
        prompt_lower = prompt.lower()

        # 根据 suggestion 类型推测修复模式
        if "try/except" in prompt_lower or "try" in prompt_lower or "except" in prompt_lower:
            original_code = "result = await graph.ainvoke(state)"
            suggested_code = (
                "try:\n"
                "    result = await graph.ainvoke(state)\n"
                "except Exception as exc:\n"
                "    logger.error('Workflow failed: %s', exc)\n"
                "    raise"
            )
            explanation = "为 graph.ainvoke 增加 try/except 异常捕获，避免未处理异常导致任务状态异常。"
        elif "log" in prompt_lower and "missing" in prompt_lower:
            original_code = "def process(data):\n    return transform(data)"
            suggested_code = (
                "def process(data):\n"
                "    logger.info('Processing data | size=%d', len(data))\n"
                "    result = transform(data)\n"
                "    logger.debug('Process completed | result=%s', result)\n"
                "    return result"
            )
            explanation = "为关键函数增加日志输出，便于排查问题和监控运行状态。"
        elif "test" in prompt_lower or "测试" in prompt:
            original_code = "def add(a, b):\n    return a + b"
            suggested_code = (
                "def add(a, b):\n"
                "    return a + b\n\n\n"
                "def test_add():\n"
                "    assert add(1, 2) == 3\n"
                "    assert add(-1, 1) == 0\n"
                "    assert add(0, 0) == 0"
            )
            explanation = "为函数补充单元测试用例，覆盖正常路径和边界条件。"
        elif "validation" in prompt_lower or "validate" in prompt_lower or "校验" in prompt:
            original_code = "def create_item(data):\n    return db.insert(data)"
            suggested_code = (
                "def create_item(data):\n"
                "    if not data or not data.get('name'):\n"
                "        raise ValueError('name is required')\n"
                "    return db.insert(data)"
            )
            explanation = "为函数增加输入参数校验，避免无效数据导致后续错误。"
        else:
            original_code = "def example():\n    pass"
            suggested_code = (
                "def example():\n"
                "    # TODO: implement based on the review suggestion\n"
                "    pass"
            )
            explanation = "Fallback 模式无法根据具体上下文生成精准修复代码，请参考 Review 建议手动修改。"

        return {
            "file_path": "",
            "start_line": None,
            "end_line": None,
            "original_code": original_code,
            "suggested_code": suggested_code,
            "explanation": explanation,
        }
