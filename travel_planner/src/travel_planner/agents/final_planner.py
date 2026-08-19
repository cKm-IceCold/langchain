import logging

from src.travel_planner.state.TripState import TripState

logger = logging.getLogger(__name__)


def final_planner(state: TripState) -> TripState:
    """Create a transparent, deterministic summary from the completed state."""
    flight = state.flight_results[0] if state.flight_results else None
    hotel = state.hotel_results[0] if state.hotel_results else None
    activities = state.activities or []

    lines = [
        f"Trip to {state.destination or 'an unspecified destination'}",
        f"Dates: {state.departure_date or 'unspecified'} to {state.return_date or 'unspecified'}",
        f"Travelers: {state.no_of_travelers}",
    ]
    if flight:
        lines.append(f"Flight: {flight.get('airline', 'Unknown airline')} for ${flight.get('price', 0):,.2f}")
    else:
        lines.append("Flight: no offer returned")
    if hotel:
        lines.append(f"Hotel: {hotel.get('name', 'Unknown hotel')} for ${hotel.get('total_price', 0):,.2f} total")
    else:
        lines.append("Hotel: no offer returned")
    lines.append(f"Activities found: {len(activities)}")
    lines.append(f"Estimated known cost: ${state.total_cost:,.2f}")
    lines.append(f"Budget status: {state.budget_status}")
    if state.budget_message:
        lines.append(state.budget_message)
    if state.cost_saving_recommendations:
        lines.append("Recommendations: " + " ".join(state.cost_saving_recommendations))

    state.final_plan = "\n".join(lines)
    logger.info("Final plan created")
    return state