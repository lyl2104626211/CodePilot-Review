from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, reviews
from app.core.config import settings
from app.core.logger import logger


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例"""
    logger.info(
        "正在创建 FastAPI 应用 | name={} version={} env={} demo_mode={}",
        settings.app_name, settings.app_version, settings.app_env, settings.demo_mode,
    )
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    # CORS 中间件：允许前端跨域访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由，统一 /api 前缀
    app.include_router(health.router, prefix="/api")
    app.include_router(reviews.router, prefix="/api")

    return app


# 模块级 app 实例，供 uvicorn 直接引用
app = create_app()
