from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/version")
async def version():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
    }
