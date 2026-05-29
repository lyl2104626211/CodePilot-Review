from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，自动从 .env 文件和环境变量读取"""

    app_name: str = "CodePilot Review"
    app_version: str = "0.1.0"
    app_env: str = "development"

    # 前端地址，用于 CORS 白名单
    frontend_origin: str = "http://localhost:5173"

    # GitHub Token，第 2 天接入真实 API 时需要
    github_token: str = ""
    # 模型配置：供应商 + 模型名称，第 2 天接入 LLM 时使用
    model_provider: str = "deepseek"
    model_name: str = "deepseek-v4-pro"
    model_base_url: str = "https://api.deepseek.com/v1"
    model_api_key: str = ""
    request_timeout_seconds: int = 120

    # Demo 模式：True 时使用 Mock Provider，无需 Token 和模型 API
    demo_mode: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# 模块级单例，全局共享一份配置
settings = Settings()
