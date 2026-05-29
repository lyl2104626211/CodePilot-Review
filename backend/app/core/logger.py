import sys
from pathlib import Path

from loguru import logger

# 日志文件目录
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 移除默认 handler
logger.remove()

# 控制台输出：彩色格式，开发友好
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

# 文件输出：每日轮转，保留 7 天，压缩归档
logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="00:00",       # 每天午夜轮转
    retention="7 days",     # 保留 7 天
    compression="zip",      # 归档时压缩
    encoding="utf-8",
    enqueue=True,           # 多进程安全
)

# 错误日志单独存储一份，方便快速排查
logger.add(
    LOG_DIR / "error_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="00:00",
    retention="30 days",    # 错误日志保留更久
    compression="zip",
    encoding="utf-8",
    enqueue=True,
)

__all__ = ["logger"]
