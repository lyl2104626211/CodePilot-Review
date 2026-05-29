"""LLM Client 抽象接口"""
from typing import Protocol


class LLMClient(Protocol):
    """LLM 客户端协议

    业务节点通过此接口调用模型，不依赖具体供应商。
    第 2 天有两个实现：
    - FallbackLLMClient: 无 API Key 时的确定性降级
    - OpenAICompatibleLLMClient: 调用 DeepSeek / DashScope 等兼容接口
    """

    async def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str = "") -> dict:
        """生成结构化 JSON 输出

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词（包含 PR 数据）
            schema_name: 输出 schema 名称，供日志和缓存标识

        Returns:
            dict: 解析后的 JSON 字典

        Raises:
            LLMError: 调用失败时抛出
        """
        ...


class LLMError(Exception):
    """LLM 调用异常"""
    pass
