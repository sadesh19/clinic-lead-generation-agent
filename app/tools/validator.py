"""
validator.py — LangChain tool interface for clinic lead validation.
================================================================
OWNER: @~Print On Demand (Data Processing team)
================================================================
Print On Demand: implement the _run() method below. It receives
a raw clinic dict and must return an enriched dict with:
- cleaned phone_number
- correct automation_status  (Manual / Semi Automated / Automated)
- correct appointment_method
- assigned lead_priority     (High / Medium / Low)

Do NOT change the class name, method signature, or return format
— the agent depends on them.
"""
from typing import Any, Dict, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ValidatorInput(BaseModel):
    clinic_data: Dict[str, Any] = Field(..., description="Raw clinic dict to validate and enrich")


class ValidatorTool(BaseTool):
    """Validate and enrich a raw clinic lead dict."""

    name: str = "validate_clinic_lead"
    description: str = (
        "Validates a raw clinic data dict: cleans phone number, "
        "determines automation status and appointment method, "
        "and assigns lead priority. Returns the enriched dict."
    )
    args_schema: Type[BaseModel] = ValidatorInput

    def _run(self, clinic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ── PRINT ON DEMAND: implement this ────────────────────────────────────

        Input: raw clinic dict (may have messy phone, missing fields, etc.)

        Must return the same dict enriched with:
        {
            "phone_number":      str,   # cleaned, with country code
            "automation_status": str,   # "Manual" | "Semi Automated" | "Automated"
            "appointment_method":str,   # "Phone Calls" | "WhatsApp" | "Website Booking Form"
                                        # | "Online Booking System" | "Social Media Messages"
            "lead_priority":     str,   # "High" | "Medium" | "Low"
            "notes":             str,   # any issues found
        }

        Automation rules (from requirements doc):
          Manual        → calls only, no chatbot, no online booking
          Semi Automated→ website form available, email confirmations
          Automated     → online booking system, chatbot, CRM, reminders

        Priority rules:
          High   → Manual clinic with rating >= 4.0  (best AI upsell target)
          Medium → Manual clinic any rating, OR Semi Automated with rating >= 4.0
          Low    → Already Automated
        ───────────────────────────────────────────────────────────────────────
        """
        raise NotImplementedError("@~Print On Demand: implement ValidatorTool._run()")

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Use synchronous _run.")
