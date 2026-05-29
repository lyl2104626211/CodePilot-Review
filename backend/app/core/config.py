from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CodePilot Review"
    app_version: str = "0.1.0"
    app_env: str = "development"

    frontend_origin: str = "http://localhost:5173"

    github_token: str = ""
    model_provider: str = "deepseek"
    model_name: str = "deepseek-v4-pro"
    request_timeout_seconds: int = 120

    demo_mode: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
