"""
search_service.py — Thin wrapper the agent nodes use to call search tools.
================================================================
OWNER: @~Saddia (Data Collection team)
================================================================
Saddia: this file calls YOUR tools. You don't need to edit it —
just implement the _run() methods in:
  app/tools/google_maps.py
  app/tools/web_search.py
  app/tools/scraper.py
"""
from typing import Any, Dict, List, Optional
from app.tools.google_maps import GoogleMapsTool
from app.tools.web_search import WebSearchTool
from app.tools.scraper import WebScraperTool
from app.utils.logger import get_logger

logger = get_logger(__name__)

_gmaps = GoogleMapsTool()
_web = WebSearchTool()
_scraper = WebScraperTool()


class SearchService:
    """Unified interface used by the agent graph to call data collection tools."""

    def search_clinics_google_maps(
        self,
        query: str,
        city: str,
        country: str,
        clinic_type: str,
        min_rating: Optional[float] = None,
        max_results: int = 20,
    ) -> List[Dict[str, Any]]:
        return _gmaps._run(
            query=query, city=city, country=country,
            clinic_type=clinic_type, min_rating=min_rating, max_results=max_results,
        )

    def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        return _web._run(query=query, max_results=max_results)

    def scrape_website(self, url: str) -> Dict[str, Any]:
        return _scraper._run(url=url)
