import logging

from langgraph.graph import END, START, StateGraph

from src.travel_planner.agents.activity_agent import activity_agent
from src.travel_planner.agents.budget_agent import budget_agent
from src.travel_planner.agents.coordinator import coordinator_agent
from src.travel_planner.agents.flight_agent import flight_agent
from src.travel_planner.agents.hotel_agent import hotel_agent
from src.travel_planner.agents.final_planner import final_planner
from src.travel_planner.state.TripState import TripState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_full_travel_graph():
    """Create the complete coordinator-to-itinerary travel workflow."""
    builder = StateGraph(TripState)

    builder.add_node("coordinator", coordinator_agent)
    builder.add_node("flight_agent", flight_agent)
    builder.add_node("hotel_agent", hotel_agent)
    builder.add_node("activity_agent", activity_agent)
    builder.add_node("budget_agent", budget_agent)
    builder.add_node("final_planner", final_planner)

    builder.add_edge(START, "coordinator")
    builder.add_edge("coordinator", "flight_agent")
    builder.add_edge("flight_agent", "hotel_agent")
    builder.add_edge("hotel_agent", "activity_agent")
    builder.add_edge("activity_agent", "budget_agent")
    builder.add_edge("budget_agent", "final_planner")
    builder.add_edge("final_planner", END)

    return builder.compile()


def print_workflow_result(result: dict) -> None:
    """Print the important outputs produced by the complete workflow."""
    print("\n" + "=" * 80)
    print("FULL TRAVEL WORKFLOW RESULT")
    print("=" * 80)
    print(f"Destination: {result.get('destination', 'N/A')}")
    print(f"Departure city: {result.get('departure_city', 'N/A')}")
    print(f"Dates: {result.get('departure_date', 'N/A')} -> {result.get('return_date', 'N/A')}")
    print(f"Travelers: {result.get('no_of_travelers', 'N/A')}")
    print(f"Budget: ${result.get('budget', 0):,.2f}")
    print(f"Trip type: {result.get('trip_type', 'N/A')}")
    print(f"Preferences: {result.get('preferences', [])}")
    print(f"\nFlights: {result.get('flight_results', [])}")
    print(f"\nHotels: {result.get('hotel_results', [])}")
    print(f"\nActivities: {result.get('activities', [])}")
    print(f"\nCost breakdown: {result.get('cost_breakdown', {})}")
    print(f"Estimated total cost: ${result.get('total_cost', 0):,.2f}")
    print(f"Within budget: {result.get('is_within_budget', False)}")
    print(f"Budget status: {result.get('budget_status', 'unknown')}")
    print(f"Budget message: {result.get('budget_message', 'N/A')}")
    print(f"Cost-saving recommendations: {result.get('cost_saving_recommendations', [])}")
    print(f"\nFinal plan:\n{result.get('final_plan', 'N/A')}")


if __name__ == "__main__":
    graph = create_full_travel_graph()
    initial_state = TripState(
        user_request=(
            "Plan a 6-day cultural trip to Paris from Lagos for 2 people "
            "in September 2026 with a budget of $2500. We enjoy museums and food."
        )
    )

    workflow_result = graph.invoke(initial_state)
    print_workflow_result(workflow_result)
