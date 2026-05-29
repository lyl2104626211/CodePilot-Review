from app.schemas.common import TaskStatus
from app.schemas.review import ReviewReport
from app.workflows.review_state import ReviewGraphState


def assemble_report_node(state: ReviewGraphState) -> ReviewGraphState:
    if state.get("error_message"):
        return state

    state["report"] = ReviewReport(
        task_id=state["task_id"],
        status=TaskStatus.succeeded,
        pr=state["pr_snapshot"],
        summary=state["summary"],
        findings=state["findings"],
        suggestions=state["suggestions"],
        test_recommendations=state["test_recommendations"],
    )

    return state
