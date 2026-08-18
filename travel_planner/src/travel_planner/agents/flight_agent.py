import logging
from typing import Any, Dict, List

from src.travel_planner.state.TripState import TripState

logger = logging.getLogger(__name__)


def flight_search_tool(state: TripState) -> List[Dict[str, Any]]:
    """
    Search for sample flight options for a trip.

    This is a placeholder tool for Sprint 3. The goal is to test the
    LangGraph pattern and state flow before we integrate a real flight API.
    """
    destination = state.destination or "Paris"
    departure_city = state.departure_city or "Lagos"
    departure_date = state.departure_date or "2025-01-10"
    return_date = state.return_date or "2025-01-15"
    budget = state.budget or 0.0

    flights = [
        {
            "airline": "SkyJet",
            "price": 420.0,
            "departure_time": "08:30",
            "arrival_time": "14:10",
            "duration": "5h 40m",
            "route": f"{departure_city} -> {destination}",
            "departure_date": departure_date,
            "return_date": return_date,
        },
        {
            "airline": "BlueWave",
            "price": 510.0,
            "departure_time": "12:15",
            "arrival_time": "18:20",
            "duration": "6h 05m",
            "route": f"{departure_city} -> {destination}",
            "departure_date": departure_date,
            "return_date": return_date,
        },
        {
            "airline": "NorthAir",
            "price": 610.0,
            "departure_time": "19:40",
            "arrival_time": "02:05",
            "duration": "6h 25m",
            "route": f"{departure_city} -> {destination}",
            "departure_date": departure_date,
            "return_date": return_date,
        },
    ]

    if budget > 0:
        flights = [flight for flight in flights if flight["price"] <= budget]

    flights.sort(key=lambda item: item["price"])
    return flights


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

    flight_options = flight_search_tool(state)
    state.flight_results = flight_options

    if flight_options:
        state.total_cost = float(flight_options[0]["price"])

    logger.info("Flight search completed")
    logger.debug(f"Flight options: {flight_options}")
    return state
