"""
response.py — Agent response schema returned to the caller.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.clinic import ClinicLead


class AgentResponse(BaseModel):
    """Final output from the clinic lead generation agent."""

    success: bool
    total_found: int = 0
    leads: List[ClinicLead] = Field(default_factory=list)
    summary: str = ""
    errors: List[str] = Field(default_factory=list)
    run_id: Optional[str] = None
