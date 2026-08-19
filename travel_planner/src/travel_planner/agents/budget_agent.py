import logging
from typing import Dict, List, Tuple

from src.travel_planner.state.TripState import TripState

logger = logging.getLogger(__name__)


def calculate_trip_cost(state: TripState) -> Tuple[Dict[str, float], List[str]]:
    """Calculate the cheapest known plan from the search results."""
    flight_cost = float(state.flight_results[0].get("price", 0)) if state.flight_results else 0.0
    hotel_cost = float(state.hotel_results[0].get("total_price", 0)) if state.hotel_results else 0.0
    priced_activities = [
        float(activity["cost"])
        for activity in (state.activities or [])
        if isinstance(activity.get("cost"), (int, float))
    ]
    activities_cost = sum(priced_activities)
    unknown_activity_prices = len(priced_activities) != len(state.activities or [])

    breakdown = {
        "flights": flight_cost,
        "hotels": hotel_cost,
        "activities": activities_cost,
    }
    notes = []
    if unknown_activity_prices:
        notes.append("Activity prices are unavailable, so the total excludes them.")
    if not state.flight_results:
        notes.append("No flight offer was found; flight cost is excluded.")
    if not state.hotel_results:
        notes.append("No hotel offer was found; hotel cost is excluded.")
    return breakdown, notes


def budget_agent(state: TripState) -> TripState:
    """Validate the estimated trip cost against the user's budget."""
    logger.info("Budget agent started")

    breakdown, notes = calculate_trip_cost(state)
    state.cost_breakdown = breakdown
    state.total_cost = sum(breakdown.values())
    state.cost_data_complete = bool(state.flight_results and state.hotel_results)
    state.is_within_budget = state.cost_data_complete and (state.budget <= 0 or state.total_cost <= state.budget)
    state.cost_saving_recommendations = []

    if not state.cost_data_complete:
        state.budget_status = "incomplete"
        state.budget_message = "The estimate is incomplete because required travel results are missing."
    elif state.budget <= 0:
        state.budget_status = "no_budget"
        state.budget_message = "No budget was provided; showing the estimated known costs."
    elif state.is_within_budget:
        state.budget_status = "within_budget"
        remaining = state.budget - state.total_cost
        state.budget_message = f"The known estimated cost is within budget, with ${remaining:,.2f} remaining."
    else:
        state.budget_status = "over_budget"
        overage = state.total_cost - state.budget
        state.budget_message = f"The known estimated cost exceeds budget by ${overage:,.2f}."
        if state.flight_results and len(state.flight_results) > 1:
            state.cost_saving_recommendations.append("Compare the available flight options for a lower fare.")
        if state.hotel_results and len(state.hotel_results) > 1:
            state.cost_saving_recommendations.append("Compare the available hotel options for a lower total stay cost.")

    state.budget_message = f"{state.budget_message} {' '.join(notes)}".strip()
    logger.info("Budget validation completed: %s", state.budget_message)
    return state