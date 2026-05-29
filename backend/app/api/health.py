from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """健康检查接口：返回服务运行状态"""
    return {"status": "ok"}


@router.get("/version")
async def version():
    """版本信息接口：返回应用名称、版本号和环境"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
    }
