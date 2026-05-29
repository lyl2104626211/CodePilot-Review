from langgraph.graph import END, START, StateGraph

from app.providers.base import PullRequestProvider
from app.workflows.nodes import (
    assemble_report_node,
    fetch_mock_pr_node,
    generate_mock_review_node,
    parse_pr_url_node,
)
from app.workflows.review_state import ReviewGraphState


def build_review_graph(provider: PullRequestProvider):
    graph = StateGraph(ReviewGraphState)

    graph.add_node("parse_pr_url", parse_pr_url_node)
    graph.add_node("fetch_mock_pr", fetch_mock_pr_node(provider))
    graph.add_node("generate_mock_review", generate_mock_review_node)
    graph.add_node("assemble_report", assemble_report_node)

    graph.add_edge(START, "parse_pr_url")
    graph.add_edge("parse_pr_url", "fetch_mock_pr")
    graph.add_edge("fetch_mock_pr", "generate_mock_review")
    graph.add_edge("generate_mock_review", "assemble_report")
    graph.add_edge("assemble_report", END)

    return graph.compile()
