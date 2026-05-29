from app.schemas.review import ReviewReport


class MemoryTaskStore:
    def __init__(self):
        self._tasks: dict[str, ReviewReport] = {}

    def save(self, report: ReviewReport) -> None:
        self._tasks[report.task_id] = report

    def get(self, task_id: str) -> ReviewReport | None:
        return self._tasks.get(task_id)
