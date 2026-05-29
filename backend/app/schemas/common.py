from enum import Enum


class TaskStatus(str, Enum):
    """Review 任务状态枚举"""
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class RiskSeverity(str, Enum):
    """风险严重程度枚举"""
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class RiskCategory(str, Enum):
    """风险类别枚举"""
    correctness = "correctness"
    security = "security"
    performance = "performance"
    compatibility = "compatibility"
    observability = "observability"
    data_handling = "data_handling"
    missing_tests = "missing_tests"
