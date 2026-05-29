from enum import Enum


class TaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class RiskSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class RiskCategory(str, Enum):
    correctness = "correctness"
    security = "security"
    performance = "performance"
    compatibility = "compatibility"
    observability = "observability"
    data_handling = "data_handling"
    missing_tests = "missing_tests"
