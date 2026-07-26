"""
test_graph.py — Unit tests for YOUR LangGraph nodes and workflow.
"""
import pytest
from unittest.mock import patch
from app.graph.state import AgentState
from app.graph.nodes import (
    node_parse_request,
    node_plan_search,
    node_deduplicate,
    node_check_quota,
    node_summarise,
    node_validate_leads,
)
from app.graph.edges import should_continue_or_finish
from app.schemas.request import ClinicSearchRequest
from app.schemas.clinic import ClinicLead


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def base_state():
    return AgentState(
        request=ClinicSearchRequest(
            locations=["London"],
            clinic_types=["Dental Clinic"],
            max_results=10,
        )
    )

@pytest.fixture
def sample_lead():
    return ClinicLead(
        lead_id="LEAD-0001",
        clinic_name="Test Dental",
        clinic_type="Dental Clinic",
        country="United Kingdom",
        city="London",
        address="1 Test St, London",
        phone_number="+441234567890",
        appointment_method="Phone Calls",
        automation_status="Manual",
        lead_priority="High",
    )


# ── Node: parse_request ───────────────────────────────────────────────────────

def test_node_parse_request_assigns_run_id(base_state):
    result = node_parse_request(base_state)
    assert "run_id" in result
    assert len(result["run_id"]) > 0


# ── Node: plan_search ─────────────────────────────────────────────────────────

def test_node_plan_search_creates_messages(base_state):
    base_state.run_id = "TEST01"
    result = node_plan_search(base_state)
    assert "messages" in result
    assert len(result["messages"]) > 0

def test_node_plan_search_messages_contain_system_prompt(base_state):
    base_state.run_id = "TEST01"
    result = node_plan_search(base_state)
    roles = [m["role"] for m in result["messages"]]
    assert "system" in roles


# ── Node: deduplicate ─────────────────────────────────────────────────────────

def test_node_deduplicate_removes_same_phone(base_state, sample_lead):
    lead2 = sample_lead.model_copy(update={"lead_id": "LEAD-0002"})
    base_state.extracted_leads = [sample_lead, lead2]
    result = node_deduplicate(base_state)
    assert len(result["deduplicated_leads"]) == 1

def test_node_deduplicate_keeps_different_clinics(base_state, sample_lead):
    lead2 = ClinicLead(
        lead_id="LEAD-0002",
        clinic_name="Another Clinic",
        clinic_type="Skin Clinic",
        country="United Kingdom",
        city="Manchester",
        address="2 Other St, Manchester",
        phone_number="+449876543210",
        appointment_method="Phone Calls",
        automation_status="Manual",
    )
    base_state.extracted_leads = [sample_lead, lead2]
    result = node_deduplicate(base_state)
    assert len(result["deduplicated_leads"]) == 2

def test_node_deduplicate_empty_input(base_state):
    base_state.extracted_leads = []
    result = node_deduplicate(base_state)
    assert result["deduplicated_leads"] == []


# ── Node: validate_leads ──────────────────────────────────────────────────────

def test_node_validate_leads_calls_validator(base_state, sample_lead):
    """validate_leads must call ValidatorTool; mock it to return the same lead dict."""
    base_state.deduplicated_leads = [sample_lead]
    base_state.run_id = "TEST01"

    with patch("app.graph.nodes._validator_tool._run", return_value=sample_lead.model_dump()):
        result = node_validate_leads(base_state)

    assert len(result["validated_leads"]) == 1

def test_node_validate_leads_applies_min_rating_filter(base_state, sample_lead):
    """Leads below min_rating should be filtered out."""
    base_state.request.min_rating = 4.5
    low_rated = sample_lead.model_copy(update={"google_rating": 3.0})
    base_state.deduplicated_leads = [low_rated]
    base_state.run_id = "TEST01"

    result = node_validate_leads(base_state)
    assert len(result["validated_leads"]) == 0


# ── Node: check_quota ─────────────────────────────────────────────────────────

def test_node_check_quota_continue_when_below_target(base_state, sample_lead):
    base_state.validated_leads = [sample_lead]  # only 1, need 10
    base_state.raw_google_maps_results = [{"clinic_name": "Test"}]  # simulate data present
    base_state.run_id = "TEST01"
    base_state.iteration = 0
    result = node_check_quota(base_state)
    assert result["should_continue_search"] is True

def test_node_check_quota_finish_when_quota_met(base_state, sample_lead):
    base_state.validated_leads = [sample_lead] * 10  # equals max_results
    base_state.run_id = "TEST01"
    base_state.iteration = 0
    result = node_check_quota(base_state)
    assert result["should_continue_search"] is False

def test_node_check_quota_finish_when_max_iterations_reached(base_state, sample_lead):
    from config import config
    base_state.validated_leads = []
    base_state.run_id = "TEST01"
    base_state.iteration = config.AGENT_MAX_ITERATIONS  # already at limit
    result = node_check_quota(base_state)
    assert result["should_continue_search"] is False

def test_node_check_quota_increments_iteration(base_state, sample_lead):
    base_state.validated_leads = []
    base_state.run_id = "TEST01"
    base_state.iteration = 2
    result = node_check_quota(base_state)
    assert result["iteration"] == 3


# ── Node: summarise ───────────────────────────────────────────────────────────

def test_node_summarise_generates_text(base_state, sample_lead):
    base_state.validated_leads = [sample_lead]
    base_state.run_id = "TEST01"
    base_state.iteration = 1
    result = node_summarise(base_state)
    assert "summary" in result
    assert "TEST01" in result["summary"]

def test_node_summarise_counts_correctly(base_state, sample_lead):
    base_state.validated_leads = [sample_lead] * 3
    base_state.run_id = "TEST02"
    base_state.iteration = 2
    result = node_summarise(base_state)
    assert "3" in result["summary"]

def test_node_summarise_empty_leads(base_state):
    base_state.validated_leads = []
    base_state.run_id = "TEST03"
    base_state.iteration = 1
    result = node_summarise(base_state)
    assert result["summary"] != ""


# ── Edges ─────────────────────────────────────────────────────────────────────

def test_edge_routes_to_continue(base_state):
    base_state.should_continue_search = True
    assert should_continue_or_finish(base_state) == "continue_search"

def test_edge_routes_to_finish(base_state):
    base_state.should_continue_search = False
    assert should_continue_or_finish(base_state) == "finish"
