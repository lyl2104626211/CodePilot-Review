from app.services.pr_parser import PRParseError, parse_github_pr_url
from app.workflows.review_state import ReviewGraphState


def parse_pr_url_node(state: ReviewGraphState) -> ReviewGraphState:
    try:
        parsed = parse_github_pr_url(state["url"])
        state["parsed_pr"] = parsed
    except PRParseError as e:
        state["error_message"] = str(e)
    return state
