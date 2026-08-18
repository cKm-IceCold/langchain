"""
SIMPLE LANGGRAPH EXAMPLE
========================
This teaches you the basics with a Travel Planner workflow.
Think of it as: Gather Info → Search → Validate → Return Plan
"""

from pydantic import BaseModel
from typing import Literal
from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. DEFINE STATE (Shared data across the workflow)
# ============================================================
class TravelState(BaseModel):
    """This is what flows through your workflow"""
    destination: str = ""
    budget: float = 0.0
    num_days: int = 0
    flights_found: bool = False
    hotels_found: bool = False
    total_cost: float = 0.0
    plan: str = ""


# ============================================================
# 2. DEFINE NODES (Functions that do the work)
# ============================================================

def search_flights(state: TravelState) -> TravelState:
    """Node 1: Pretend to search for flights"""
    print(f"🔍 Searching flights for {state.destination}...")
    state.flights_found = True
    state.total_cost += 500.0  # Simulate flight cost
    return state


def search_hotels(state: TravelState) -> TravelState:
    """Node 2: Pretend to search for hotels"""
    print(f"🏨 Searching hotels in {state.destination} for {state.num_days} days...")
    state.hotels_found = True
    state.total_cost += (100.0 * state.num_days)  # $100/night
    return state


def validate_budget(state: TravelState) -> TravelState:
    """Node 3: Check if plan fits budget"""
    print(f"💰 Validating budget: Total cost ${state.total_cost} vs Budget ${state.budget}")
    if state.total_cost <= state.budget:
        state.plan = f"✅ Plan within budget! Total: ${state.total_cost}"
    else:
        state.plan = f"⚠️ Plan exceeds budget by ${state.total_cost - state.budget}"
    return state


def finalize_plan(state: TravelState) -> TravelState:
    """Node 4: Generate final trip plan"""
    print("📋 Finalizing your trip plan...")
    state.plan += f"\n- Destination: {state.destination}\n- Duration: {state.num_days} days\n- Total Cost: ${state.total_cost}"
    return state


# ============================================================
# 3. BUILD THE GRAPH (Connect nodes with edges)
# ============================================================

def create_travel_graph():
    """Assemble the workflow"""
    builder = StateGraph(TravelState)
    
    # Add nodes (like adding steps to a recipe)
    builder.add_node("search_flights", search_flights)
    builder.add_node("search_hotels", search_hotels)
    builder.add_node("validate_budget", validate_budget)
    builder.add_node("finalize_plan", finalize_plan)
    
    # Add edges (connect the steps - START → node1 → node2 → node3 → END)
    builder.add_edge(START, "search_flights")
    builder.add_edge("search_flights", "search_hotels")
    builder.add_edge("search_hotels", "validate_budget")
    builder.add_edge("validate_budget", "finalize_plan")
    builder.add_edge("finalize_plan", END)
    
    # Compile the graph
    graph = builder.compile()
    return graph


# ============================================================
# 4. RUN IT
# ============================================================

if __name__ == "__main__":
    # Create the graph
    travel_graph = create_travel_graph()
    
    # Create initial state
    trip = TravelState(
        destination="Paris",
        budget=2000.0,
        num_days=7
    )
    
    print("=" * 60)
    print("🌍 STARTING TRIP PLANNING WORKFLOW")
    print("=" * 60)
    
    # Run the graph with the state
    result = travel_graph.invoke(trip)
    
    print("\n" + "=" * 60)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 60)
    print(result.plan)
