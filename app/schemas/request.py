"""
request.py — Schema for user input to the agent.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from app.utils.constants import CLINIC_TYPES, TARGET_LOCATIONS


class ClinicSearchRequest(BaseModel):
    """What the user provides to kick off a lead-generation run."""

    locations: List[str] = Field(
        default_factory=list,
        description=(
            "List of cities or countries to search. "
            f"Supported: {list(TARGET_LOCATIONS.keys())} and their cities."
        ),
        examples=[["London", "Dubai"]],
    )
    clinic_types: List[str] = Field(
        default_factory=lambda: CLINIC_TYPES,
        description=f"Clinic specialisations to target. Options: {CLINIC_TYPES}",
        examples=[["Dental Clinic", "Skin Clinic"]],
    )
    min_rating: Optional[float] = Field(
        default=None,
        ge=1.0,
        le=5.0,
        description="Minimum Google rating to include (1.0–5.0).",
    )
    max_results: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Maximum number of verified leads to return.",
    )
    automation_filter: Optional[str] = Field(
        default=None,
        description="Only return clinics with this automation status: Manual | Semi Automated | Automated",
    )
    keywords: Optional[List[str]] = Field(
        default=None,
        description="Extra search keywords (e.g. ['botox', 'hair transplant']).",
    )
