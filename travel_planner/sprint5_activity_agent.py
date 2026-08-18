import logging
from langgraph.graph import StateGraph, START, END

from src.travel_planner.agents.activity_agent import activity_agent
from src.travel_planner.state.TripState import TripState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sprint5_graph():
    builder = StateGraph(TripState)
    builder.add_node("activity_agent", activity_agent)
    builder.add_edge(START, "activity_agent")
    builder.add_edge("activity_agent", END)
    return builder.compile()


if __name__ == "__main__":
    graph = create_sprint5_graph()
    state = TripState(
        user_request="I want a cultural trip with museums and local food.",
        destination="Paris",
        departure_city="Lagos",
        departure_date="2025-09-10",
        return_date="2025-09-16",
        no_of_travelers=2,
        budget=800.0,
        trip_type="cultural",
        preferences=["museums", "food", "history"],
    )
    result = graph.invoke(state)
    print(result.get("activities", []))
