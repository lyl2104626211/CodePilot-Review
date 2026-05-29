from app.core.logger import logger
from app.services.pr_parser import PRParseError, parse_github_pr_url
from app.workflows.review_state import ReviewGraphState


def parse_pr_url_node(state: ReviewGraphState) -> ReviewGraphState:
    """节点1：解析 GitHub PR URL

    将用户输入的 URL 解析为 ParsedPullRequest，写入 state["parsed_pr"]。
    解析失败时设置 error_message，后续节点检测到后短路跳过。
    """
    logger.debug("[工作流] parse_pr_url 节点开始 | task_id={} url={}", state.get("task_id"), state["url"])
    try:
        parsed = parse_github_pr_url(state["url"])
        state["parsed_pr"] = parsed
        logger.debug("[工作流] parse_pr_url 节点完成 | task_id={} owner={} repo={} number={}",
                     state.get("task_id"), parsed.owner, parsed.repo, parsed.number)
    except PRParseError as e:
        logger.warning("[工作流] parse_pr_url 节点失败 | task_id={} error={}", state.get("task_id"), str(e))
        state["error_message"] = str(e)
    return state
