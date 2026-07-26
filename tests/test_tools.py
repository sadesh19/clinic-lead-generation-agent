"""
test_tools.py — Tests for YOUR layer: planner logic and tool interfaces.

NOTE: The actual tool implementations (GoogleMapsTool, WebSearchTool,
ValidatorTool etc.) are owned by other teams. We only test:
  - that the tool classes instantiate with the correct name/schema
  - that they raise NotImplementedError (confirming stubs are in place)
  - the planner logic, which is fully yours
"""
import pytest
from app.tools.google_maps import GoogleMapsTool
from app.tools.web_search import WebSearchTool
from app.tools.scraper import WebScraperTool
from app.tools.validator import ValidatorTool
from app.agent.planner import build_search_plan, next_search_query
from app.schemas.request import ClinicSearchRequest


# ── Tool interface tests (yours — verify contracts are correct) ───────────────

def test_google_maps_tool_has_correct_name():
    tool = GoogleMapsTool()
    assert tool.name == "google_maps_search"

def test_web_search_tool_has_correct_name():
    tool = WebSearchTool()
    assert tool.name == "web_search"

def test_scraper_tool_has_correct_name():
    tool = WebScraperTool()
    assert tool.name == "website_scraper"

def test_validator_tool_has_correct_name():
    tool = ValidatorTool()
    assert tool.name == "validate_clinic_lead"

def test_google_maps_tool_raises_not_implemented():
    """Confirms stub is in place — Saddia must implement this."""
    tool = GoogleMapsTool()
    with pytest.raises(NotImplementedError):
        tool._run(query="Dental Clinic London", city="London",
                  country="UK", clinic_type="Dental Clinic")

def test_web_search_tool_raises_not_implemented():
    """Confirms stub is in place — Saddia must implement this."""
    tool = WebSearchTool()
    with pytest.raises(NotImplementedError):
        tool._run(query="Dental Clinic London")

def test_scraper_tool_raises_not_implemented():
    """Confirms stub is in place — Saddia must implement this."""
    tool = WebScraperTool()
    with pytest.raises(NotImplementedError):
        tool._run(url="https://example.com")

def test_validator_tool_raises_not_implemented():
    """Confirms stub is in place — Print On Demand must implement this."""
    tool = ValidatorTool()
    with pytest.raises(NotImplementedError):
        tool._run(clinic_data={"clinic_name": "Test", "phone_number": "+44123"})


# ── Planner tests (100% yours) ────────────────────────────────────────────────

def test_planner_builds_plan_for_all_locations():
    request = ClinicSearchRequest(locations=[], clinic_types=["Dental Clinic"])
    plan = build_search_plan(request)
    # 5 UK + 3 UAE + 4 PK + 3 AU = 15 cities × 1 type
    assert len(plan) >= 14

def test_planner_filters_to_requested_locations():
    request = ClinicSearchRequest(
        locations=["London"], clinic_types=["Dental Clinic", "Skin Clinic"]
    )
    plan = build_search_plan(request)
    assert len(plan) == 2   # 1 city × 2 types
    assert all(city == "London" for _, city, _ in plan)

def test_planner_uk_first_in_default_plan():
    request = ClinicSearchRequest(locations=[], clinic_types=["Dental Clinic"])
    plan = build_search_plan(request)
    assert plan[0][0] == "United Kingdom"

def test_planner_multiple_clinic_types():
    request = ClinicSearchRequest(
        locations=["Dubai"],
        clinic_types=["Dental Clinic", "Aesthetic Clinic", "Skin Clinic"],
    )
    plan = build_search_plan(request)
    assert len(plan) == 3   # 1 city × 3 types
    assert all(city == "Dubai" for _, city, _ in plan)

def test_planner_unknown_location_included():
    """Unknown cities should be added rather than silently dropped."""
    request = ClinicSearchRequest(
        locations=["NewCity123"], clinic_types=["Dental Clinic"]
    )
    plan = build_search_plan(request)
    assert len(plan) == 1
    assert plan[0][1] == "NewCity123"

def test_next_search_query_format():
    query = next_search_query("United Kingdom", "London", "Dental Clinic")
    assert "Dental Clinic" in query
    assert "London" in query
    assert "United Kingdom" in query
