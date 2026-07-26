"""
web_search.py — LangChain tool interface for web search.
================================================================
OWNER: @~Saddia (Data Collection team)
================================================================
Saddia: implement the _run() method below using TavilySearchResults
from langchain_community. Do NOT change the class name, method
signature, or return format — the agent depends on them.
"""
from typing import Any, Dict, List, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WebSearchInput(BaseModel):
    query: str = Field(..., description="Web search query for finding clinic information")
    max_results: int = Field(default=5, description="Number of results to return")


class WebSearchTool(BaseTool):
    """Perform a web search to find additional clinic information."""

    name: str = "web_search"
    description: str = (
        "Search the web for clinic contact details, social media, and booking methods. "
        "Use to supplement Google Maps data."
    )
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        ── SADDIA: implement this ──────────────────────────────────────────────

        Use TavilySearchResults (or SerpAPI) to search the web.

        Required return format (each dict must have these keys):
        {
            "title":   str,
            "url":     str,
            "content": str,   # snippet / summary of the page
        }
        ───────────────────────────────────────────────────────────────────────
        """
        raise NotImplementedError("@~Saddia: implement WebSearchTool._run()")

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Use synchronous _run.")
