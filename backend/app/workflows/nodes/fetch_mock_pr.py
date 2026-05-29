from app.providers.base import PullRequestProvider
from app.workflows.review_state import ReviewGraphState


def fetch_mock_pr_node(provider: PullRequestProvider):
    """节点2：获取 PR 快照（通过闭包注入 Provider）

    调用 Provider 获取 PR 元数据和 diff。
    第 1 天使用 MockGitHubProvider 返回固定数据，
    第 2 天替换为 GitHubProvider 走真实 API。
    """
    async def node(state: ReviewGraphState) -> ReviewGraphState:
        # 前置节点出错则短路
        if state.get("error_message"):
            return state
        try:
            snapshot = await provider.get_pull_request(state["parsed_pr"])
            state["pr_snapshot"] = snapshot
        except Exception as e:
            state["error_message"] = str(e)
        return state

    return node
