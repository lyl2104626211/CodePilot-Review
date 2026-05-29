from app.providers.base import PullRequestProvider
from app.workflows.review_state import ReviewGraphState


def fetch_mock_pr_node(provider: PullRequestProvider):
    async def node(state: ReviewGraphState) -> ReviewGraphState:
        if state.get("error_message"):
            return state
        try:
            snapshot = await provider.get_pull_request(state["parsed_pr"])
            state["pr_snapshot"] = snapshot
        except Exception as e:
            state["error_message"] = str(e)
        return state

    return node
