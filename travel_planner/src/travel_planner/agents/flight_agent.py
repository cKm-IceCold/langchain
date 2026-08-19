import logging
from typing import Any, Dict, List

from src.travel_planner.services.free_travel_apis import TravelApiError, search_flights
from src.travel_planner.state.TripState import TripState

logger = logging.getLogger(__name__)


def flight_search_tool(state: TripState) -> List[Dict[str, Any]]:
    """
    Search for live flight offers through the Amadeus free test API.
    """
    return search_flights(
        departure_city=state.departure_city,
        destination=state.destination,
        departure_date=state.departure_date,
        return_date=state.return_date,
        travelers=state.no_of_travelers,
        budget=state.budget,
    )


def flight_agent(state: TripState) -> TripState:
    """
    Flight agent for Sprint 3.

    It uses a tool-like function to search for flights and stores the best options
    into the state so the next agent can consume them.
    """
    logger.info("Flight agent started")

    if not state.destination:
        logger.warning("No destination available. Flight search cannot proceed.")
        state.flight_results = []
        return state

    try:
        flight_options = flight_search_tool(state)
    except TravelApiError as exc:
        logger.error("Flight search failed: %s", exc)
        state.flight_results = []
        return state
    state.flight_results = flight_options

    if flight_options:
        state.total_cost = float(flight_options[0]["price"])

    logger.info("Flight search completed")
    logger.debug(f"Flight options: {flight_options}")
    return state
