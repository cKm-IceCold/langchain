"""
SPRINT 2: COORDINATOR GRAPH
============================
This is the LangGraph workflow for Sprint 2.

Flow:
    START → [Coordinator] → END

The coordinator parses the user's request and fills the state.
Future sprints will extend this to add more agents in the pipeline.

Production considerations:
- Clean graph structure (one node, clear entry/exit)
- Proper error handling at LLM level
- State validation between steps
- Logging for debugging
"""

import logging
from langgraph.graph import StateGraph, START, END

from src.travel_planner.state.TripState import TripState
from src.travel_planner.agents.coordinator import coordinator_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# BUILD THE SPRINT 2 GRAPH
# ============================================================

def create_sprint2_graph():
    """
    Creates the coordinator graph for Sprint 2.
    
    This is a simple graph with one node:
    - START → coordinator_agent → END
    
    The coordinator takes raw user input and returns structured trip data.
    
    Returns:
        CompiledStateGraph: A compiled LangGraph ready to invoke
    """
    
    # Initialize the state graph
    builder = StateGraph(TripState)
    
    # Add the coordinator node (the only node in Sprint 2)
    builder.add_node("coordinator", coordinator_agent)
    
    # Add edges to define the flow
    builder.add_edge(START, "coordinator")  # Start -> Coordinator
    builder.add_edge("coordinator", END)     # Coordinator -> End
    
    # Compile the graph into a runnable workflow
    graph = builder.compile()
    
    logger.info("Sprint 2 Graph created successfully")
    
    return graph


# ============================================================
# TEST / EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    """
    Run this file to test the Sprint 2 coordinator graph.
    
    Example usage:
        python sprint2_graph.py
    """
    
    # Create the graph
    graph = create_sprint2_graph()
    
    print("\n" + "="*80)
    print("SPRINT 2 COORDINATOR GRAPH - TEST SUITE")
    print("="*80)
    
    # Test Case 1: Detailed request
    print("\n" + "-"*80)
    print("TEST 1: Detailed Trip Request")
    print("-"*80)
    
    trip_request_1 = TripState(
        user_request="""
        I want to plan a trip to Tokyo with my partner for 10 days in March 2025.
        We're traveling from New York and we have a budget of $4000.
        We're interested in cultural experiences, Japanese gardens, and trying local food.
        It's an adventure-focused trip.
        """
    )
    
    result_1 = graph.invoke(trip_request_1)
    
    # Display results (result is a dict from LangGraph)
    print(f"\nPARSED RESULTS:")
    print(f"   Destination: {result_1.get('destination', 'N/A')}")
    print(f"   From: {result_1.get('departure_city', 'N/A')}")
    print(f"   Dates: {result_1.get('departure_date', 'N/A')} -> {result_1.get('return_date', 'N/A')}")
    print(f"   Travelers: {result_1.get('no_of_travelers', 'N/A')}")
    print(f"   Budget: ${result_1.get('budget', 0):,.2f}")
    print(f"   Trip Type: {result_1.get('trip_type', 'N/A')}")
    print(f"   Preferences: {result_1.get('preferences', [])}")
    
    # Test Case 2: Minimal/casual request
    print("\n" + "-"*80)
    print("TEST 2: Casual/Short Request")
    print("-"*80)
    
    trip_request_2 = TripState(
        user_request="I want to go to Paris with my family next month. Budget around $5000."
    )
    
    result_2 = graph.invoke(trip_request_2)
    
    print(f"\nPARSED RESULTS:")
    print(f"   Destination: {result_2.get('destination', 'N/A')}")
    print(f"   From: {result_2.get('departure_city', 'N/A')}")
    print(f"   Dates: {result_2.get('departure_date', 'N/A')} -> {result_2.get('return_date', 'N/A')}")
    print(f"   Travelers: {result_2.get('no_of_travelers', 'N/A')}")
    print(f"   Budget: ${result_2.get('budget', 0):,.2f}")
    print(f"   Trip Type: {result_2.get('trip_type', 'N/A')}")
    print(f"   Preferences: {result_2.get('preferences', [])}")
    
    # Test Case 3: Very minimal request
    print("\n" + "-"*80)
    print("TEST 3: Minimal Request")
    print("-"*80)
    
    trip_request_3 = TripState(
        user_request="Weekend trip to Miami"
    )
    
    result_3 = graph.invoke(trip_request_3)
    
    print(f"\nPARSED RESULTS:")
    print(f"   Destination: {result_3.get('destination', 'N/A')}")
    print(f"   From: {result_3.get('departure_city', 'N/A')}")
    print(f"   Dates: {result_3.get('departure_date', 'N/A')} -> {result_3.get('return_date', 'N/A')}")
    print(f"   Travelers: {result_3.get('no_of_travelers', 'N/A')}")
    print(f"   Budget: ${result_3.get('budget', 0):,.2f}")
    print(f"   Trip Type: {result_3.get('trip_type', 'N/A')}")
    print(f"   Preferences: {result_3.get('preferences', [])}")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)
