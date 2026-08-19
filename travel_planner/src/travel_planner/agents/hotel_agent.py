import logging
from typing import Any, Dict, List

from src.travel_planner.services.free_travel_apis import TravelApiError, search_hotels
from src.travel_planner.state.TripState import TripState

logger = logging.getLogger(__name__)


def hotel_search_tool(state: TripState) -> List[Dict[str, Any]]:
    """
    Search for live hotel offers through the Amadeus free test API.
    """
    return search_hotels(
        destination=state.destination,
        check_in=state.departure_date,
        check_out=state.return_date,
        travelers=state.no_of_travelers,
        budget=state.budget,
    )


def hotel_agent(state: TripState) -> TripState:
    """Hotel agent for Sprint 4. It stores hotel options in state."""
    logger.info("Hotel agent started")

    if not state.destination:
        logger.warning("No destination available. Hotel search cannot proceed.")
        state.hotel_results = []
        return state

    try:
        hotel_options = hotel_search_tool(state)
    except TravelApiError as exc:
        logger.error("Hotel search failed: %s", exc)
        state.hotel_results = []
        return state
    state.hotel_results = hotel_options

    logger.info("Hotel search completed")
    logger.debug(f"Hotel options: {hotel_options}")
    return state
