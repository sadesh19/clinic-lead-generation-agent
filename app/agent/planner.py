"""
planner.py — Generates a search plan for the agent.

Decides which (location, clinic_type) pairs to query and in what order,
based on the user's request and how many leads have been collected so far.
"""
from typing import List, Tuple
from app.schemas.request import ClinicSearchRequest
from app.utils.constants import TARGET_LOCATIONS
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_search_plan(
    request: ClinicSearchRequest,
    already_collected: int = 0,
) -> List[Tuple[str, str, str]]:
    """
    Returns an ordered list of (country, city, clinic_type) tuples to search.

    Priority:
      1. UK cities first (primary market)
      2. UAE (premium market)
      3. Pakistan
      4. Australia

    The list is exhaustive enough to reach `request.max_results` even if
    individual searches return few results.
    """
    # Resolve requested locations to (country, city) pairs
    location_pairs: List[Tuple[str, str]] = []

    # Build a lookup: city_lower -> (country, city)
    city_lookup: dict = {}
    for country, cities in TARGET_LOCATIONS.items():
        for city in cities:
            city_lookup[city.lower()] = (country, city)
        city_lookup[country.lower()] = (country, None)  # country-level

    if not request.locations:
        # Default: all supported locations in priority order
        priority_order = ["United Kingdom", "UAE", "Pakistan", "Australia"]
        for country in priority_order:
            for city in TARGET_LOCATIONS.get(country, []):
                location_pairs.append((country, city))
    else:
        for loc in request.locations:
            match = city_lookup.get(loc.lower())
            if match:
                country, city = match
                if city:
                    location_pairs.append((country, city))
                else:
                    # whole country requested
                    for c in TARGET_LOCATIONS.get(country, []):
                        location_pairs.append((country, c))
            else:
                # Unknown location — try it anyway with "Unknown" country
                logger.warning("Location '%s' not in TARGET_LOCATIONS, adding as-is.", loc)
                location_pairs.append(("Unknown", loc))

    # Build full plan: every (location, clinic_type) combination
    plan: List[Tuple[str, str, str]] = []
    for country, city in location_pairs:
        for clinic_type in request.clinic_types:
            plan.append((country, city, clinic_type))

    logger.info(
        "Search plan built: %d combinations for %d target leads (have %d already).",
        len(plan),
        request.max_results,
        already_collected,
    )
    return plan


def next_search_query(country: str, city: str, clinic_type: str) -> str:
    """Format a human-readable search query string."""
    return f"{clinic_type} in {city}, {country}"
