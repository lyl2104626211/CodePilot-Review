from app.services.pr_parser import PRParseError, parse_github_pr_url
from app.workflows.review_state import ReviewGraphState


def parse_pr_url_node(state: ReviewGraphState) -> ReviewGraphState:
    """节点1：解析 GitHub PR URL

    将用户输入的 URL 解析为 ParsedPullRequest，写入 state["parsed_pr"]。
    解析失败时设置 error_message，后续节点检测到后短路跳过。
    """
    try:
        parsed = parse_github_pr_url(state["url"])
        state["parsed_pr"] = parsed
    except PRParseError as e:
        state["error_message"] = str(e)
    return state
