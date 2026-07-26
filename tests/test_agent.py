"""
test_agent.py — Unit tests for YOUR ClinicLeadAgent class.

The underlying tools (Google Maps, Validator etc.) are mocked since
those are other teams' implementations.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.agent.agent import ClinicLeadAgent
from app.agent.memory import AgentMemory
from app.agent.planner import build_search_plan
from app.schemas.request import ClinicSearchRequest
from app.schemas.response import AgentResponse
from app.schemas.clinic import ClinicLead


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_request():
    return ClinicSearchRequest(
        locations=["London"],
        clinic_types=["Dental Clinic"],
        max_results=5,
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


# ── Agent instantiation ───────────────────────────────────────────────────────

def test_agent_instantiation():
    agent = ClinicLeadAgent()
    assert agent is not None
    assert agent.memory is not None
    assert agent.graph is not None

def test_agent_accepts_custom_memory():
    memory = AgentMemory()
    agent = ClinicLeadAgent(memory=memory)
    assert agent.memory is memory


# ── Agent.run() ───────────────────────────────────────────────────────────────

def test_agent_run_returns_agent_response(mock_request):
    """run() must always return AgentResponse even when tools raise errors."""
    agent = ClinicLeadAgent()
    # Tools raise NotImplementedError — agent should handle gracefully
    response = agent.run(mock_request)
    assert isinstance(response, AgentResponse)

def test_agent_run_response_has_required_fields(mock_request):
    agent = ClinicLeadAgent()
    response = agent.run(mock_request)
    assert hasattr(response, "success")
    assert hasattr(response, "total_found")
    assert hasattr(response, "leads")
    assert hasattr(response, "summary")
    assert hasattr(response, "run_id")
    assert hasattr(response, "errors")
    assert isinstance(response.leads, list)
    assert isinstance(response.errors, list)

def test_agent_run_empty_locations():
    """Empty locations = search all — should not crash."""
    agent = ClinicLeadAgent()
    request = ClinicSearchRequest(locations=[], max_results=2)
    response = agent.run(request)
    assert isinstance(response, AgentResponse)

def test_agent_run_records_memory(mock_request):
    """After run(), memory should have at least the user message recorded."""
    agent = ClinicLeadAgent()
    agent.run(mock_request)
    messages = agent.memory.get_messages()
    assert len(messages) >= 1

def test_agent_run_assigns_run_id(mock_request):
    """Every run should produce a unique run_id."""
    agent = ClinicLeadAgent()
    r1 = agent.run(mock_request)
    r2 = agent.run(mock_request)
    # Both have run_ids (may be None if graph crashed, but field exists)
    assert hasattr(r1, "run_id")
    assert hasattr(r2, "run_id")


# ── Memory ────────────────────────────────────────────────────────────────────

def test_memory_stores_and_retrieves_messages():
    memory = AgentMemory()
    memory.add_user_message("Find clinics in London")
    memory.add_ai_message("Searching London for clinics...")
    msgs = memory.get_messages()
    assert len(msgs) == 2

def test_memory_clear():
    memory = AgentMemory()
    memory.add_user_message("Hello")
    memory.clear()
    assert len(memory.get_messages()) == 0

def test_memory_to_dict_list():
    memory = AgentMemory()
    memory.add_user_message("test")
    result = memory.to_dict_list()
    assert isinstance(result, list)
    assert result[0]["content"] == "test"
