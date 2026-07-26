"""
scraper.py — LangChain tool interface for website scraping.
================================================================
OWNER: @~Saddia (Data Collection team)
================================================================
Saddia: implement the _run() method below using requests +
BeautifulSoup. Do NOT change the class name, method signature,
or return format — the agent depends on them.
"""
from typing import Any, Dict, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScraperInput(BaseModel):
    url: str = Field(..., description="The clinic website URL to scrape")


class WebScraperTool(BaseTool):
    """Scrape a clinic website to extract contact and booking information."""

    name: str = "website_scraper"
    description: str = (
        "Scrape a clinic website to extract email, social media links, "
        "booking method, and doctor/owner name."
    )
    args_schema: Type[BaseModel] = ScraperInput

    def _run(self, url: str) -> Dict[str, Any]:
        """
        ── SADDIA: implement this ──────────────────────────────────────────────

        Scrape the given URL and return extracted clinic data.

        Required return format (all keys required, use None if not found):
        {
            "email":            str|None,
            "social_links":     list[str],   # Instagram/Facebook URLs
            "has_online_booking": bool,
            "booking_platforms":  list[str], # e.g. ["Doctify", "Calendly"]
            "doctor_name":      str|None,
            "raw_text_snippet": str,         # first ~500 chars of page text
        }
        ───────────────────────────────────────────────────────────────────────
        """
        raise NotImplementedError("@~Saddia: implement WebScraperTool._run()")

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Use synchronous _run.")
