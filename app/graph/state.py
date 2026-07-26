"""
state.py — Shared state that flows through every node in the LangGraph.

All fields are Optional so each node only touches what it owns.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.clinic import ClinicLead
from app.schemas.request import ClinicSearchRequest


class AgentState(BaseModel):
    """
    The single mutable object passed between LangGraph nodes.
    Each node reads what it needs and writes what it produces.
    """

    # ── Input ────────────────────────────────────────────────────────────────
    request: Optional[ClinicSearchRequest] = None

    # ── Raw data from tools (Saddia's layer) ─────────────────────────────────
    raw_google_maps_results: List[Dict[str, Any]] = Field(default_factory=list)
    raw_web_search_results: List[Dict[str, Any]] = Field(default_factory=list)

    # ── Extracted & cleaned leads (Print On Demand's layer) ──────────────────
    extracted_leads: List[ClinicLead] = Field(default_factory=list)
    deduplicated_leads: List[ClinicLead] = Field(default_factory=list)
    validated_leads: List[ClinicLead] = Field(default_factory=list)

    # ── Workflow control ──────────────────────────────────────────────────────
    current_location_index: int = 0          # which city we're currently processing
    current_clinic_type_index: int = 0       # which clinic type we're processing
    iteration: int = 0                       # total search cycles run
    should_continue_search: bool = True      # set False when quota met or exhausted

    # ── Agent reasoning (LangChain messages) ─────────────────────────────────
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    agent_scratchpad: str = ""

    # ── Errors & metadata ────────────────────────────────────────────────────
    errors: List[str] = Field(default_factory=list)
    run_id: Optional[str] = None
    summary: str = ""

    model_config = ConfigDict(arbitrary_types_allowed=True)
