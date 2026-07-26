"""
google_maps.py — LangChain tool interface for Google Maps Places API.
================================================================
OWNER: @~Saddia (Data Collection team)
================================================================
Saddia: implement the _run() method below using the googlemaps
Python client. Do NOT change the class name, method signature,
or return format — the agent depends on them.
"""
from typing import Any, Dict, List, Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleMapsInput(BaseModel):
    query: str = Field(..., description="Search query e.g. 'Dental Clinic in London, UK'")
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country name")
    clinic_type: str = Field(..., description="Type of clinic to search for")
    min_rating: Optional[float] = Field(default=None, description="Minimum Google rating filter")
    max_results: int = Field(default=20, description="Max number of places to return")


class GoogleMapsTool(BaseTool):
    """Search Google Maps for clinics in a given location."""

    name: str = "google_maps_search"
    description: str = (
        "Search Google Maps for clinics by type and location. "
        "Returns clinic names, addresses, phone numbers, ratings, and website URLs."
    )
    args_schema: Type[BaseModel] = GoogleMapsInput

    def _run(
        self,
        query: str,
        city: str,
        country: str,
        clinic_type: str,
        min_rating: Optional[float] = None,
        max_results: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        ── SADDIA: implement this ──────────────────────────────────────────────

        Use the googlemaps client to search for clinics and return a list.

        Required return format (each dict must have these keys):
        {
            "clinic_name":   str,        # e.g. "Bright Smile Dental"
            "address":       str,        # full address
            "phone_number":  str,        # with country code e.g. "+44..."
            "website_url":   str|None,
            "google_rating": float|None,
            "reviews_count": int|None,
            "place_id":      str,        # Google place ID
        }
        ───────────────────────────────────────────────────────────────────────
        """
        raise NotImplementedError("@~Saddia: implement GoogleMapsTool._run()")

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Use synchronous _run.")
