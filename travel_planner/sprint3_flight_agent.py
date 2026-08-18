import logging
from langgraph.graph import StateGraph, START, END

from src.travel_planner.agents.flight_agent import flight_agent
from src.travel_planner.state.TripState import TripState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sprint3_graph():
    """Create a graph for Sprint 3 where coordinator feeds flight agent."""
    builder = StateGraph(TripState)
    builder.add_node("flight_agent", flight_agent)
    builder.add_edge(START, "flight_agent")
    builder.add_edge("flight_agent", END)
    return builder.compile()


if __name__ == "__main__":
    graph = create_sprint3_graph()

    state = TripState(
        user_request="I want to go to Paris next month. Budget is $500.",
        destination="Paris",
        departure_city="Lagos",
        departure_date="2025-09-10",
        return_date="2025-09-16",
        no_of_travelers=1,
        budget=500.0,
        trip_type="relaxation",
    )

    result = graph.invoke(state)
    print(result.flight_results)
