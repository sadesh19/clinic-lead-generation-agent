"""
nodes.py — Every node in the LangGraph workflow.

Each function receives AgentState and returns a partial AgentState dict
(only the fields it modifies).

Node order:
  parse_request → plan_search → search_google_maps → search_web
  → extract_leads → deduplicate → validate_leads → check_quota → summarise
"""
import uuid
import json
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.graph.state import AgentState
from app.agent.prompts import (
    SYSTEM_PROMPT, PLANNER_PROMPT, EXTRACTION_PROMPT
)
from app.agent.planner import build_search_plan, next_search_query
from app.schemas.clinic import ClinicLead
from app.tools.google_maps import GoogleMapsTool
from app.tools.web_search import WebSearchTool
from app.tools.scraper import WebScraperTool
from app.tools.validator import ValidatorTool
from app.utils.logger import get_logger
from app.utils.helpers import clean_phone, normalise_url
from config import config

logger = get_logger(__name__)

# Shared tool instances
_gmaps_tool = GoogleMapsTool()
_web_tool = WebSearchTool()
_scraper_tool = WebScraperTool()
_validator_tool = ValidatorTool()


# ── Node 1: parse_request ─────────────────────────────────────────────────────

def node_parse_request(state: AgentState) -> Dict[str, Any]:
    """
    Entry node. Assigns a run_id and logs the incoming request.
    """
    run_id = str(uuid.uuid4())[:8].upper()
    logger.info("[%s] Starting clinic lead generation run.", run_id)
    logger.info(
        "[%s] Request: locations=%s, types=%s, max=%d",
        run_id,
        state.request.locations if state.request else "all",
        state.request.clinic_types if state.request else "all",
        state.request.max_results if state.request else 100,
    )
    return {"run_id": run_id}


# ── Node 2: plan_search ───────────────────────────────────────────────────────

def node_plan_search(state: AgentState) -> Dict[str, Any]:
    """
    Build the ordered search plan and store it in state.messages as context.
    """
    plan = build_search_plan(state.request, already_collected=len(state.validated_leads))

    plan_summary = "\n".join(
        f"{i+1}. {clinic_type} in {city}, {country}"
        for i, (country, city, clinic_type) in enumerate(plan[:20])  # show first 20
    )
    logger.info("[%s] Search plan (first 20):\n%s", state.run_id, plan_summary)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Search plan created. Starting search for {state.request.max_results} leads."},
        {"role": "assistant", "content": f"Plan ready. Will search {len(plan)} location-type combinations."},
    ]
    return {"messages": messages}


# ── Node 3: search_google_maps ────────────────────────────────────────────────

def node_search_google_maps(state: AgentState) -> Dict[str, Any]:
    """
    Execute Google Maps searches for all planned (location, clinic_type) pairs.
    Stops early if max_results already collected.
    """
    if not state.request:
        return {}

    plan = build_search_plan(state.request, already_collected=len(state.validated_leads))
    all_results: List[Dict[str, Any]] = list(state.raw_google_maps_results)
    errors: List[str] = list(state.errors)

    needed = state.request.max_results - len(state.validated_leads)
    if needed <= 0:
        logger.info("[%s] Quota already met. Skipping Google Maps search.", state.run_id)
        return {"should_continue_search": False}

    for country, city, clinic_type in plan:
        if len(all_results) >= needed * 3:  # collect 3x raw to allow for filtering
            break
        query = next_search_query(country, city, clinic_type)
        logger.info("[%s] Google Maps search: %s", state.run_id, query)
        try:
            results = _gmaps_tool._run(
                query=query,
                city=city,
                country=country,
                clinic_type=clinic_type,
                min_rating=state.request.min_rating,
                max_results=20,
            )
            # Tag each result with metadata
            for r in results:
                r["_country"] = country
                r["_city"] = city
                r["_clinic_type"] = clinic_type
            all_results.extend(results)
            logger.debug("[%s] Got %d results for '%s'", state.run_id, len(results), query)
        except Exception as e:
            err = f"Google Maps error for '{query}': {e}"
            logger.error(err)
            errors.append(err)

    return {"raw_google_maps_results": all_results, "errors": errors}


# ── Node 4: search_web ────────────────────────────────────────────────────────

def node_search_web(state: AgentState) -> Dict[str, Any]:
    """
    Supplement Google Maps with web search for enrichment (emails, social links).
    """
    if not state.request:
        return {}

    all_results: List[Dict[str, Any]] = list(state.raw_web_search_results)
    errors: List[str] = list(state.errors)

    # Only run web search for top locations to avoid hitting API limits
    plan = build_search_plan(state.request)
    sampled = plan[:10]  # top 10 combinations only for web enrichment

    for country, city, clinic_type in sampled:
        query = f"{clinic_type} {city} {country} contact email appointment booking"
        logger.info("[%s] Web search: %s", state.run_id, query)
        try:
            results = _web_tool._run(query=query, max_results=5)
            all_results.extend(results)
        except Exception as e:
            err = f"Web search error for '{query}': {e}"
            logger.warning(err)
            errors.append(err)

    return {"raw_web_search_results": all_results, "errors": errors}


# ── Node 5: extract_leads ─────────────────────────────────────────────────────

def node_extract_leads(state: AgentState) -> Dict[str, Any]:
    """
    Use LLM to extract structured ClinicLead objects from raw tool outputs.
    """
    llm = ChatOpenAI(
        model=config.OPENAI_MODEL,
        api_key=config.OPENAI_API_KEY,
        temperature=0,
    )

    raw_data = state.raw_google_maps_results + state.raw_web_search_results
    if not raw_data:
        logger.warning("[%s] No raw data to extract leads from.", state.run_id)
        return {"extracted_leads": []}

    # Chunk to avoid token limits
    chunk_size = 20
    extracted: List[ClinicLead] = []
    lead_counter = len(state.validated_leads) + 1

    for i in range(0, len(raw_data), chunk_size):
        chunk = raw_data[i : i + chunk_size]
        prompt = EXTRACTION_PROMPT.format(
            clinic_types=", ".join(state.request.clinic_types),
            raw_data=json.dumps(chunk, indent=2, default=str),
        )
        try:
            response = llm.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ])
            content = response.content.strip()

            # Parse JSON from LLM response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            clinics_raw = json.loads(content)
            for raw_clinic in clinics_raw:
                if not raw_clinic.get("clinic_name") or not raw_clinic.get("phone_number"):
                    continue
                raw_clinic["lead_id"] = f"LEAD-{lead_counter:04d}"
                raw_clinic["phone_number"] = clean_phone(raw_clinic.get("phone_number", ""))
                raw_clinic["website_url"] = normalise_url(raw_clinic.get("website_url"))
                raw_clinic["website_available"] = bool(raw_clinic.get("website_url"))
                raw_clinic.setdefault("appointment_method", "Phone Calls")
                raw_clinic.setdefault("automation_status", "Manual")
                raw_clinic.setdefault("notes", "")
                raw_clinic.setdefault("call_status", "Not Called")
                raw_clinic.setdefault("social_media_links", [])

                try:
                    lead = ClinicLead(**raw_clinic)
                    extracted.append(lead)
                    lead_counter += 1
                except Exception as ve:
                    logger.debug("ClinicLead validation failed: %s | data: %s", ve, raw_clinic)

        except json.JSONDecodeError as je:
            logger.warning("[%s] LLM returned non-JSON: %s", state.run_id, je)
        except Exception as e:
            logger.error("[%s] Extraction error: %s", state.run_id, e)

    logger.info("[%s] Extracted %d raw leads.", state.run_id, len(extracted))
    return {"extracted_leads": extracted}


# ── Node 6: deduplicate ───────────────────────────────────────────────────────

def node_deduplicate(state: AgentState) -> Dict[str, Any]:
    """
    Remove duplicate clinics by phone number (primary key) and clinic name+city.
    Owned conceptually by: @~Print On Demand
    """
    seen_phones: set = set()
    seen_name_city: set = set()
    deduped: List[ClinicLead] = []

    for lead in state.extracted_leads:
        phone_key = lead.phone_number.replace("+", "").replace(" ", "")
        name_city_key = f"{lead.clinic_name.lower().strip()}_{lead.city.lower().strip()}"

        if phone_key in seen_phones or name_city_key in seen_name_city:
            logger.debug("Duplicate removed: %s (%s)", lead.clinic_name, lead.city)
            continue

        seen_phones.add(phone_key)
        seen_name_city.add(name_city_key)
        deduped.append(lead)

    logger.info("[%s] After dedup: %d leads (was %d).", state.run_id, len(deduped), len(state.extracted_leads))
    return {"deduplicated_leads": deduped}


# ── Node 7: validate_leads ────────────────────────────────────────────────────

def node_validate_leads(state: AgentState) -> Dict[str, Any]:
    """
    Run each lead through the validator tool to enrich and quality-check it.
    Also applies min_rating filter if specified.
    """
    validated: List[ClinicLead] = list(state.validated_leads)
    errors: List[str] = list(state.errors)
    min_rating = state.request.min_rating if state.request else None
    automation_filter = state.request.automation_filter if state.request else None

    for lead in state.deduplicated_leads:
        # Rating filter
        if min_rating and lead.google_rating and lead.google_rating < min_rating:
            logger.debug("Filtered by rating: %s (%.1f < %.1f)", lead.clinic_name, lead.google_rating, min_rating)
            continue

        # Automation filter
        if automation_filter and lead.automation_status != automation_filter:
            continue

        try:
            enriched_data = _validator_tool._run(clinic_data=lead.model_dump())
            validated_lead = ClinicLead(**enriched_data)
            validated.append(validated_lead)
        except Exception as e:
            err = f"Validation error for '{lead.clinic_name}': {e}"
            logger.warning(err)
            errors.append(err)

    logger.info("[%s] Validated leads: %d", state.run_id, len(validated))
    return {"validated_leads": validated, "errors": errors}


# ── Node 8: check_quota ───────────────────────────────────────────────────────

def node_check_quota(state: AgentState) -> Dict[str, Any]:
    """
    Decide whether to loop back and search more, or proceed to summary.
    Stops immediately if tools returned no data (stubs not implemented yet).
    """
    target = state.request.max_results if state.request else 100
    current = len(state.validated_leads)
    iteration = state.iteration + 1

    logger.info(
        "[%s] Iteration %d: %d/%d leads collected.",
        state.run_id, iteration, current, target
    )

    # Quota met or max iterations reached
    if current >= target or iteration >= config.AGENT_MAX_ITERATIONS:
        should_continue = False
    # Tools not implemented — no point looping, stop after first attempt
    elif not state.raw_google_maps_results and not state.raw_web_search_results:
        logger.info(
            "[%s] No data returned from search tools (not yet implemented). Stopping early.",
            state.run_id,
        )
        should_continue = False
    else:
        should_continue = True

    return {"iteration": iteration, "should_continue_search": should_continue}


# ── Node 9: summarise ─────────────────────────────────────────────────────────

def node_summarise(state: AgentState) -> Dict[str, Any]:
    """
    Generate a human-readable summary of the run.
    """
    leads = state.validated_leads
    total = len(leads)
    target = state.request.max_results if state.request else 100

    by_country: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    by_priority: Dict[str, int] = {}

    for lead in leads:
        by_country[lead.country] = by_country.get(lead.country, 0) + 1
        by_status[lead.automation_status] = by_status.get(lead.automation_status, 0) + 1
        by_priority[lead.lead_priority] = by_priority.get(lead.lead_priority, 0) + 1

    country_breakdown = ", ".join(f"{c}: {n}" for c, n in sorted(by_country.items()))
    status_breakdown = ", ".join(f"{s}: {n}" for s, n in sorted(by_status.items()))
    priority_breakdown = ", ".join(f"{p}: {n}" for p, n in sorted(by_priority.items()))

    summary = (
        f"Run [{state.run_id}] complete. "
        f"Collected {total}/{target} verified leads in {state.iteration} iteration(s). "
        f"Countries: {country_breakdown}. "
        f"Automation: {status_breakdown}. "
        f"Priority: {priority_breakdown}."
    )
    logger.info(summary)
    return {"summary": summary}
