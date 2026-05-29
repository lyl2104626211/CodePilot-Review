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

        # 检查是否有新增文件没有对应测试
        has_new_backend = "backend" in _prompt and ("added" in _prompt or "new file" in _prompt.lower())
        has_tests = "test" in _prompt.lower()

        if has_new_backend and not has_tests:
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

        # 检查 patch 大小
        if "modifications" in _prompt.lower():
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
