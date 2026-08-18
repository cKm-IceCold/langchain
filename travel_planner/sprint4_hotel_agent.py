import logging
from langgraph.graph import StateGraph, START, END

from src.travel_planner.agents.hotel_agent import hotel_agent
from src.travel_planner.state.TripState import TripState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sprint4_graph():
    builder = StateGraph(TripState)
    builder.add_node("hotel_agent", hotel_agent)
    builder.add_edge(START, "hotel_agent")
    builder.add_edge("hotel_agent", END)
    return builder.compile()


if __name__ == "__main__":
    graph = create_sprint4_graph()
    state = TripState(
        user_request="Plan a hotel stay in Paris for a family trip.",
        destination="Paris",
        departure_city="Lagos",
        departure_date="2025-09-10",
        return_date="2025-09-16",
        no_of_travelers=3,
        budget=700.0,
        trip_type="family",
    )
    result = graph.invoke(state)
    print(result.get("hotel_results", []))
