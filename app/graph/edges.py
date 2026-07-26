"""
edges.py — Conditional routing logic for the LangGraph workflow.
"""
from app.graph.state import AgentState


def should_continue_or_finish(state: AgentState) -> str:
    """
    After check_quota:
    - If more leads needed and iterations remain → loop back to search
    - Otherwise → proceed to summarise
    """
    if state.should_continue_search:
        return "continue_search"
    return "finish"
