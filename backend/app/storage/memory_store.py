from app.core.logger import logger
from app.schemas.review import ReviewReport


class MemoryTaskStore:
    """内存任务存储（MVP 方案）

    使用 dict 保存 Review 报告，key 为 task_id。
    MVP 阶段够用，后续可替换为 Redis 或数据库。
    """

    def __init__(self):
        self._tasks: dict[str, ReviewReport] = {}
        logger.debug("MemoryTaskStore 已初始化")

    def save(self, report: ReviewReport) -> None:
        """保存 Review 报告，同 task_id 会覆盖"""
        logger.debug("任务存储保存 | task_id={} status={}", report.task_id, report.status.value)
        self._tasks[report.task_id] = report

    def get(self, task_id: str) -> ReviewReport | None:
        """根据 task_id 获取报告，不存在返回 None"""
        result = self._tasks.get(task_id)
        logger.debug("任务存储查询 | task_id={} hit={}", task_id, result is not None)
        return result
