"""
extraction_service.py — Converts raw tool outputs into ClinicLead objects.
================================================================
OWNER: @~Abdullah Suleman (Database & Output team)
================================================================
Abdullah: implement the extract_and_validate() method below.
It receives raw dicts from the search tools and must return
a list of validated ClinicLead objects ready to store in MongoDB.

Also add your MongoDB storage logic here (store_leads_to_mongo,
export_to_csv, export_to_excel, export_to_json).
"""
from typing import Any, Dict, List
from app.schemas.clinic import ClinicLead
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ExtractionService:
    """
    Converts raw search results into validated ClinicLead objects
    and stores/exports them.
    """

    def extract_and_validate(
        self,
        raw_clinics: List[Dict[str, Any]],
        start_index: int = 1,
    ) -> List[ClinicLead]:
        """
        ── ABDULLAH: implement this ────────────────────────────────────────────

        Input: list of raw dicts from Google Maps / web search tools.
        Each dict may have: clinic_name, address, phone_number, website_url,
                            google_rating, reviews_count, _country, _city,
                            _clinic_type (tagged by the agent).

        Steps to implement:
          1. Skip records missing clinic_name or phone_number
          2. Assign lead_id e.g. LEAD-0001, LEAD-0002 ...
          3. Call ValidatorTool._run() to clean/enrich each record
          4. Create and return ClinicLead(**enriched_data) objects

        Returns: List[ClinicLead]
        ────────────────────────────────────────────────────────────────────────
        """
        raise NotImplementedError("@~Abdullah: implement ExtractionService.extract_and_validate()")

    def store_leads_to_mongo(self, leads: List[ClinicLead]) -> int:
        """
        ── ABDULLAH: implement this ────────────────────────────────────────────
        Store leads in MongoDB. Return number of documents inserted.
        Use MONGODB_URI and MONGODB_DB from config.py.
        ────────────────────────────────────────────────────────────────────────
        """
        raise NotImplementedError("@~Abdullah: implement store_leads_to_mongo()")

    def export_to_csv(self, leads: List[ClinicLead], filepath: str) -> None:
        """── ABDULLAH: export leads to CSV using pandas ──"""
        raise NotImplementedError("@~Abdullah: implement export_to_csv()")

    def export_to_excel(self, leads: List[ClinicLead], filepath: str) -> None:
        """── ABDULLAH: export leads to Excel (.xlsx) using pandas ──"""
        raise NotImplementedError("@~Abdullah: implement export_to_excel()")

    def export_to_json(self, leads: List[ClinicLead], filepath: str) -> None:
        """── ABDULLAH: export leads to JSON file ──"""
        raise NotImplementedError("@~Abdullah: implement export_to_json()")
