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
    """构建 LangGraph Review 工作流

    节点链路（线性）：
    START → parse_pr_url → fetch_mock_pr → generate_mock_review → assemble_report → END

    第 2 天扩展方向：
    - fetch_mock_pr 替换为 fetch_github_pr（真实 GitHub API）
    - generate_mock_review 拆分为 collect_context → generate_summary → detect_risks → generate_suggestions
    - assemble_report 后增加 guardrail 自检节点
    """
    graph = StateGraph(ReviewGraphState)

    # 注册节点
    graph.add_node("parse_pr_url", parse_pr_url_node)
    graph.add_node("fetch_mock_pr", fetch_mock_pr_node(provider))
    graph.add_node("generate_mock_review", generate_mock_review_node)
    graph.add_node("assemble_report", assemble_report_node)

    # 线性链路
    graph.add_edge(START, "parse_pr_url")
    graph.add_edge("parse_pr_url", "fetch_mock_pr")
    graph.add_edge("fetch_mock_pr", "generate_mock_review")
    graph.add_edge("generate_mock_review", "assemble_report")
    graph.add_edge("assemble_report", END)

    return graph.compile()
