from app.core.logger import logger
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
            logger.debug("[工作流] fetch_mock_pr 节点跳过（前置错误） | task_id={} error={}",
                        state.get("task_id"), state["error_message"])
            return state

        logger.debug("[工作流] fetch_mock_pr 节点开始 | task_id={} owner={} repo={} number={}",
                    state.get("task_id"),
                    state["parsed_pr"].owner,
                    state["parsed_pr"].repo,
                    state["parsed_pr"].number)
        try:
            snapshot = await provider.get_pull_request(state["parsed_pr"])
            state["pr_snapshot"] = snapshot
            logger.debug("[工作流] fetch_mock_pr 节点完成 | task_id={} title={} files={}",
                        state.get("task_id"), snapshot.title, snapshot.changed_files)
        except Exception as e:
            logger.error("[工作流] fetch_mock_pr 节点失败 | task_id={} error={}", state.get("task_id"), str(e))
            state["error_message"] = str(e)
        return state

    return node
