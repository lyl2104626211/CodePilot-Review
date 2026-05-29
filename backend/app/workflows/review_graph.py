from langgraph.graph import END, START, StateGraph

from app.llm.base import LLMClient
from app.providers.base import PullRequestProvider
from app.workflows.nodes import (
    assemble_report_node,
    fetch_mock_pr_node,
    generate_mock_review_node,
    parse_pr_url_node,
    collect_context_node,
    generate_summary_node,
    detect_risks_node,
    generate_suggestions_node,
    guardrail_check_node,
)
from app.workflows.review_state import ReviewGraphState


def build_demo_graph(provider: PullRequestProvider):
    """构建 Demo 模式工作流（4 节点）

    链路：START → parse_pr_url → fetch_mock_pr → generate_mock_review → assemble_report → END
    使用 Mock Provider 和固定分析结果，无需 GitHub Token 和 LLM API。
    """
    graph = StateGraph(ReviewGraphState)

    graph.add_node("parse_pr_url", parse_pr_url_node)
    graph.add_node("fetch_pr", fetch_mock_pr_node(provider))
    graph.add_node("generate_mock_review", generate_mock_review_node)
    graph.add_node("assemble_report", assemble_report_node)

    graph.add_edge(START, "parse_pr_url")
    graph.add_edge("parse_pr_url", "fetch_pr")
    graph.add_edge("fetch_pr", "generate_mock_review")
    graph.add_edge("generate_mock_review", "assemble_report")
    graph.add_edge("assemble_report", END)

    return graph.compile()


def build_review_graph(provider: PullRequestProvider, llm: LLMClient):
    """构建完整 Review 工作流（9 节点）

    链路：
    START → parse_pr_url → fetch_pr → collect_context
    → generate_summary → detect_risks → generate_suggestions
    → guardrail_check → assemble_report → END

    第 1 天 Demo 模式使用 build_demo_graph（4 节点），
    第 2 天 GitHub 模式使用本函数（9 节点）。
    """
    graph = StateGraph(ReviewGraphState)

    # 注册节点
    graph.add_node("parse_pr_url", parse_pr_url_node)
    graph.add_node("fetch_pr", fetch_mock_pr_node(provider))
    graph.add_node("collect_context", collect_context_node)
    graph.add_node("generate_summary", generate_summary_node(llm))
    graph.add_node("detect_risks", detect_risks_node(llm))
    graph.add_node("generate_suggestions", generate_suggestions_node(llm))
    graph.add_node("guardrail_check", guardrail_check_node())
    graph.add_node("assemble_report", assemble_report_node)

    # 线性链路
    graph.add_edge(START, "parse_pr_url")
    graph.add_edge("parse_pr_url", "fetch_pr")
    graph.add_edge("fetch_pr", "collect_context")
    graph.add_edge("collect_context", "generate_summary")
    graph.add_edge("generate_summary", "detect_risks")
    graph.add_edge("detect_risks", "generate_suggestions")
    graph.add_edge("generate_suggestions", "guardrail_check")
    graph.add_edge("guardrail_check", "assemble_report")
    graph.add_edge("assemble_report", END)

    return graph.compile()
