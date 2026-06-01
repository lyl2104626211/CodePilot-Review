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

            # ===== PR 数据详细日志（控制台 + 文件） =====
            logger.info("=" * 60)
            logger.info("[PR 数据] 标题: {}", snapshot.title)
            logger.info("[PR 数据] 作者: {}", snapshot.author)
            logger.info("[PR 数据] 分支: {} -> {}", snapshot.head_branch, snapshot.base_branch)
            logger.info("[PR 数据] 文件数: {} | +{} -{} | commits: {}",
                        snapshot.changed_files, snapshot.additions,
                        snapshot.deletions, snapshot.commit_count)
            logger.info("[PR 数据] 变更文件列表:")
            for i, f in enumerate(snapshot.files):
                logger.info("[PR 数据]   {}. {} ({}) +{} -{}",
                            i + 1, f.path, f.status, f.additions, f.deletions)
                if f.patch:
                    # 截取前 500 字符，避免日志过长
                    patch_preview = f.patch[:500]
                    if len(f.patch) > 500:
                        patch_preview += f"\n... [截断, 共 {len(f.patch)} 字符]"
                    logger.info("[PR 数据]     diff:\n{}", patch_preview)
            logger.info("=" * 60)
        except Exception as e:
            logger.error("[工作流] fetch_mock_pr 节点失败 | task_id={} error={}", state.get("task_id"), str(e))
            state["error_message"] = str(e)
        return state

    return node
