import logging
from typing import Any, Dict, List

from src.travel_planner.state.TripState import TripState

logger = logging.getLogger(__name__)


def hotel_search_tool(state: TripState) -> List[Dict[str, Any]]:
    """
    Return a shortlist of hotel options based on the trip state.

    This is a structured placeholder for Sprint 4. The next step would be to
    replace this with a real API or search provider.
    """
    destination = state.destination or "Paris"
    departure_date = state.departure_date or "2025-09-10"
    return_date = state.return_date or "2025-09-16"
    budget = state.budget or 0.0

    hotels = [
        {
            "name": "City Crest Inn",
            "price_per_night": 110.0,
            "rating": 4.4,
            "location": f"Central {destination}",
            "check_in": departure_date,
            "check_out": return_date,
            "stay_type": "budget-friendly",
        },
        {
            "name": "Harbor Light Hotel",
            "price_per_night": 148.0,
            "rating": 4.6,
            "location": f"Near the waterfront in {destination}",
            "check_in": departure_date,
            "check_out": return_date,
            "stay_type": "mid-range",
        },
        {
            "name": "Grand Emerald Suites",
            "price_per_night": 210.0,
            "rating": 4.8,
            "location": f"Luxury district in {destination}",
            "check_in": departure_date,
            "check_out": return_date,
            "stay_type": "premium",
        },
    ]

    if budget > 0:
        hotels = [hotel for hotel in hotels if hotel["price_per_night"] <= (budget / max(1, state.no_of_travelers))]

    hotels.sort(key=lambda item: item["price_per_night"])
    return hotels


def hotel_agent(state: TripState) -> TripState:
    """Hotel agent for Sprint 4. It stores hotel options in state."""
    logger.info("Hotel agent started")

    if not state.destination:
        logger.warning("No destination available. Hotel search cannot proceed.")
        state.hotel_results = []
        return state

    hotel_options = hotel_search_tool(state)
    state.hotel_results = hotel_options

    if hotel_options:
        state.total_cost = float(state.total_cost + (hotel_options[0]["price_per_night"] * 5))

    logger.info("Hotel search completed")
    logger.debug(f"Hotel options: {hotel_options}")
    return state
