from app.schemas.common import RiskCategory, RiskSeverity
from app.schemas.review import ReviewSuggestion, ReviewSummary, RiskFinding
from app.workflows.review_state import ReviewGraphState


def generate_mock_review_node(state: ReviewGraphState) -> ReviewGraphState:
    if state.get("error_message"):
        return state

    state["summary"] = ReviewSummary(
        overview="本 PR 新增了 Review 任务创建接口和基础任务状态管理。",
        changed_modules=["backend api", "review service", "tests"],
        reviewer_focus=["任务状态是否可靠", "异常处理是否完整", "测试是否覆盖失败分支"],
    )

    state["findings"] = [
        RiskFinding(
            id="risk_001",
            severity=RiskSeverity.medium,
            category=RiskCategory.correctness,
            file_path="backend/app/services/review_service.py",
            line=42,
            title="任务状态更新缺少失败分支",
            evidence="create_review_task only marks succeeded in demo path.",
            reasoning="后续接入真实异步分析后，如果 Provider 或模型调用失败，任务可能停留在 running。",
            confidence=0.82,
        )
    ]

    state["suggestions"] = [
        ReviewSuggestion(
            id="suggestion_001",
            finding_id="risk_001",
            file_path="backend/app/services/review_service.py",
            comment="建议为 Review 任务增加统一异常捕获，并在失败时写入 failed 状态和错误信息。",
            rationale="这样前端可以展示明确失败原因，避免用户长时间等待。",
            suggested_fix="在 create_review_task 外层包装 try/except，并将错误保存到 task.error_message。",
            blocking=False,
        )
    ]

    state["test_recommendations"] = [
        "增加非法 PR URL 的解析失败测试。",
        "增加任务不存在时返回 404 的测试。",
        "增加 Mock Provider 返回固定 PR 元数据的测试。",
    ]

    return state
