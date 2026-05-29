"""OpenAI 兼容接口的 LLM 客户端

支持 DeepSeek、DashScope、vLLM 等所有 OpenAI 兼容 API。
"""
import json

import httpx

from app.core.config import settings
from app.core.logger import logger
from app.llm.base import LLMError


class OpenAICompatibleLLMClient:
    """OpenAI 兼容 LLM 客户端

    配置通过环境变量：
    - MODEL_BASE_URL: API 地址（默认 https://api.deepseek.com/v1）
    - MODEL_API_KEY: API Key
    - MODEL_NAME: 模型名称（默认 deepseek-chat）
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: int = 60,
    ):
        self._base_url = (base_url or settings.model_base_url).rstrip("/")
        self._api_key = api_key or settings.model_api_key
        self._model = model or settings.model_name
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(timeout_seconds),
        )

    async def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str = "") -> dict:
        """调用 LLM 生成结构化 JSON

        流程：
        1. 发送 Chat Completion 请求
        2. 从响应中提取 JSON
        3. 解析 JSON 失败时重试一次
        4. 仍失败则抛出 LLMError
        """
        logger.info("LLM 调用开始 | model={} schema={}", self._model, schema_name)

        for attempt in range(2):
            try:
                response = await self._client.post(
                    "/chat/completions",
                    json={
                        "model": self._model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4096,
                    },
                )

                if response.status_code != 200:
                    logger.warning("LLM API 返回非 200 | status={} body={}",
                                  response.status_code, response.text[:300])
                    if attempt == 0:
                        continue
                    raise LLMError(f"LLM API error: status={response.status_code}")

                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                # 尝试提取 JSON（可能被 markdown 代码块包裹）
                result = self._extract_json(content)
                if result:
                    logger.info("LLM 调用成功 | model={} schema={}", self._model, schema_name)
                    return result

                logger.warning("LLM 返回内容无法解析为 JSON | attempt={} content={}",
                              attempt + 1, content[:200])
            except LLMError:
                raise
            except Exception as e:
                logger.error("LLM 调用异常 | attempt={} error={}", attempt + 1, str(e))
                if attempt == 0:
                    continue
                raise LLMError(f"LLM call failed after retries: {e}") from e

        raise LLMError(f"Failed to generate valid JSON for schema: {schema_name}")

    async def close(self):
        """关闭 HTTP 客户端"""
        await self._client.aclose()

    @staticmethod
    def _extract_json(content: str) -> dict | None:
        """从 LLM 输出中提取 JSON 对象

        处理三种常见情况：
        1. 纯 JSON: {"key": "value"}
        2. Markdown 代码块: ```json\n{...}\n```
        3. 无标记代码块: ```\n{...}\n```
        """
        content = content.strip()

        # 移除 markdown 代码块标记
        if content.startswith("```"):
            # 找到第一个换行符之后的内容
            first_newline = content.find("\n")
            if first_newline != -1:
                content = content[first_newline + 1:]
            # 移除结尾的 ```
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        # 尝试找到 JSON 对象的起止位置
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            content = content[start:end + 1]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None
