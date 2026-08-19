import logging
from typing import Any, Dict, List

from src.travel_planner.services.free_travel_apis import TravelApiError, search_activities
from src.travel_planner.state.TripState import TripState

logger = logging.getLogger(__name__)


def activity_search_tool(state: TripState) -> List[Dict[str, Any]]:
    """
    Search real places through the public OpenStreetMap Nominatim API.
    """
    return search_activities(state.destination, state.preferences)


def activity_agent(state: TripState) -> TripState:
    """Activity agent for Sprint 5. It stores itinerary suggestions in state."""
    logger.info("Activity agent started")

    if not state.destination:
        logger.warning("No destination available. Activity suggestions cannot proceed.")
        state.activities = []
        return state

    try:
        suggestions = activity_search_tool(state)
    except TravelApiError as exc:
        logger.error("Activity search failed: %s", exc)
        state.activities = []
        return state
    state.activities = suggestions

    logger.info("Activity suggestions completed")
    logger.debug(f"Activities: {suggestions}")
    return state
