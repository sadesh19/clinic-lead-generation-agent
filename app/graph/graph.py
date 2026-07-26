"""
graph.py — Builds and compiles the LangGraph workflow for clinic lead generation.

Workflow:
                         ┌─────────────────────────────────────────┐
                         │                                         │
  parse_request → plan_search → search_google_maps → search_web   │
       → extract_leads → deduplicate → validate_leads             │
       → check_quota ──(continue)──────────────────────────────────┘
                    └──(finish)──→ summarise → END
"""
from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.edges import should_continue_or_finish
from app.graph.nodes import (
    node_parse_request,
    node_plan_search,
    node_search_google_maps,
    node_search_web,
    node_extract_leads,
    node_deduplicate,
    node_validate_leads,
    node_check_quota,
    node_summarise,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_graph():
    """Construct and compile the LangGraph state machine."""
    builder = StateGraph(AgentState)

    # ── Register nodes ────────────────────────────────────────────────────────
    builder.add_node("parse_request", node_parse_request)
    builder.add_node("plan_search", node_plan_search)
    builder.add_node("search_google_maps", node_search_google_maps)
    builder.add_node("search_web", node_search_web)
    builder.add_node("extract_leads", node_extract_leads)
    builder.add_node("deduplicate", node_deduplicate)
    builder.add_node("validate_leads", node_validate_leads)
    builder.add_node("check_quota", node_check_quota)
    builder.add_node("summarise", node_summarise)

    # ── Define edges (linear pipeline with one conditional branch) ────────────
    builder.set_entry_point("parse_request")
    builder.add_edge("parse_request", "plan_search")
    builder.add_edge("plan_search", "search_google_maps")
    builder.add_edge("search_google_maps", "search_web")
    builder.add_edge("search_web", "extract_leads")
    builder.add_edge("extract_leads", "deduplicate")
    builder.add_edge("deduplicate", "validate_leads")
    builder.add_edge("validate_leads", "check_quota")

    # Conditional: loop back to search more or finish
    builder.add_conditional_edges(
        "check_quota",
        should_continue_or_finish,
        {
            "continue_search": "search_google_maps",   # re-run search phase
            "finish": "summarise",
        },
    )

    builder.add_edge("summarise", END)

    graph = builder.compile()
    logger.info("LangGraph workflow compiled successfully.")
    return graph


# Module-level compiled graph (import and use directly)
clinic_graph = build_graph()
