import logging
from typing import Any, Dict, List

from src.travel_planner.state.TripState import TripState

logger = logging.getLogger(__name__)


def activity_search_tool(state: TripState) -> List[Dict[str, Any]]:
    """
    Return itinerary suggestions based on the trip type and preferences.
    """
    destination = state.destination or "Paris"
    trip_type = (state.trip_type or "relaxation").lower()
    preferences = state.preferences or []

    base_activities = [
        {
            "name": f"City walk around {destination}",
            "cost": 25.0,
            "category": "exploration",
            "duration": "2 hours",
        },
        {
            "name": "Local food tasting",
            "cost": 35.0,
            "category": "food",
            "duration": "1.5 hours",
        },
        {
            "name": "Sunset viewpoint visit",
            "cost": 18.0,
            "category": "scenic",
            "duration": "1 hour",
        },
    ]

    if trip_type == "adventure":
        base_activities = [
            {"name": "Hiking trail session", "cost": 45.0, "category": "adventure", "duration": "3 hours"},
            {"name": "Kayaking or water activity", "cost": 60.0, "category": "adventure", "duration": "2 hours"},
            {"name": "City exploration challenge", "cost": 30.0, "category": "exploration", "duration": "2 hours"},
        ]
    elif trip_type == "cultural":
        base_activities = [
            {"name": "Museum and gallery tour", "cost": 40.0, "category": "culture", "duration": "2 hours"},
            {"name": "Historic district walk", "cost": 20.0, "category": "culture", "duration": "1.5 hours"},
            {"name": "Traditional cooking class", "cost": 55.0, "category": "food", "duration": "2 hours"},
        ]
    elif trip_type == "family":
        base_activities = [
            {"name": "Family-friendly park visit", "cost": 22.0, "category": "family", "duration": "2 hours"},
            {"name": "Interactive science or museum visit", "cost": 35.0, "category": "family", "duration": "2 hours"},
            {"name": "Boat ride or scenic sightseeing", "cost": 50.0, "category": "family", "duration": "1.5 hours"},
        ]

    if preferences:
        matching = []
        for activity in base_activities:
            text = f"{activity['name']} {activity['category']}".lower()
            if any(pref.lower() in text for pref in preferences):
                matching.append(activity)
        if matching:
            base_activities = matching

    return base_activities


def activity_agent(state: TripState) -> TripState:
    """Activity agent for Sprint 5. It stores itinerary suggestions in state."""
    logger.info("Activity agent started")

    if not state.destination:
        logger.warning("No destination available. Activity suggestions cannot proceed.")
        state.activities = []
        return state

    suggestions = activity_search_tool(state)
    state.activities = suggestions

    logger.info("Activity suggestions completed")
    logger.debug(f"Activities: {suggestions}")
    return state
