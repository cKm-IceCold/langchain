"""
CONDITIONAL ROUTING IN LANGGRAPH
==================================
This shows how to make decisions IN the workflow.
Example: "If budget exceeded, renegotiate; else finalize"
"""

from pydantic import BaseModel
from typing import Literal
from langgraph.graph import StateGraph, START, END


class TravelState(BaseModel):
    """Travel planning state"""
    destination: str = ""
    budget: float = 0.0
    num_days: int = 0
    flights_cost: float = 0.0
    hotels_cost: float = 0.0
    total_cost: float = 0.0
    renegotiation_count: int = 0
    plan: str = ""


# ============================================================
# NODES
# ============================================================

def search_flights(state: TravelState) -> TravelState:
    """Search for flights"""
    print(f"✈️  Searching flights to {state.destination}...")
    state.flights_cost = 600.0
    state.total_cost = state.flights_cost + state.hotels_cost
    print(f"   Flight cost: ${state.flights_cost}")
    return state


def search_hotels(state: TravelState) -> TravelState:
    """Search for hotels"""
    print(f"🏨 Searching hotels for {state.num_days} nights...")
    state.hotels_cost = 150.0 * state.num_days
    state.total_cost = state.flights_cost + state.hotels_cost
    print(f"   Hotel cost: ${state.hotels_cost}")
    return state


def check_budget(state: TravelState) -> Literal["within_budget", "over_budget"]:
    """
    This is a ROUTING NODE - it returns a decision (not a modified state)
    Decision: Which path to take next?
    """
    print(f"💰 Checking budget: ${state.total_cost} vs Budget: ${state.budget}")
    if state.total_cost <= state.budget:
        print("   ✅ WITHIN BUDGET - proceeding to finalize")
        return "within_budget"
    else:
        print(f"   ⚠️  OVER BUDGET by ${state.total_cost - state.budget}")
        return "over_budget"


def renegotiate_plan(state: TravelState) -> TravelState:
    """If over budget, reduce costs"""
    print("🔄 RENEGOTIATING: Reducing hotel quality...")
    state.renegotiation_count += 1
    state.hotels_cost *= 0.7  # Cut hotel costs by 30%
    state.total_cost = state.flights_cost + state.hotels_cost
    print(f"   New hotel cost: ${state.hotels_cost:.2f}")
    print(f"   New total: ${state.total_cost:.2f}")
    return state


def finalize_plan(state: TravelState) -> TravelState:
    """Generate final trip plan"""
    print("📋 FINALIZING TRIP PLAN...")
    state.plan = f"""
    ✅ TRIP APPROVED!
    Destination: {state.destination}
    Duration: {state.num_days} days
    Flights: ${state.flights_cost:.2f}
    Hotels: ${state.hotels_cost:.2f}
    TOTAL: ${state.total_cost:.2f}
    Budget: ${state.budget:.2f}
    Renegotiations needed: {state.renegotiation_count}
    """
    return state


# ============================================================
# BUILD GRAPH WITH CONDITIONAL ROUTING
# ============================================================

def create_smart_travel_graph():
    """Build workflow with decision points"""
    builder = StateGraph(TravelState)
    
    # Add nodes
    builder.add_node("search_flights", search_flights)
    builder.add_node("search_hotels", search_hotels)
    builder.add_node("check_budget", check_budget)  # Returns a decision
    builder.add_node("renegotiate_plan", renegotiate_plan)
    builder.add_node("finalize_plan", finalize_plan)
    
    # Add edges (linear flow)
    builder.add_edge(START, "search_flights")
    builder.add_edge("search_flights", "search_hotels")
    builder.add_edge("search_hotels", "check_budget")
    
    # Add CONDITIONAL edges (routing)
    # "check_budget" returns "within_budget" or "over_budget" → direct to different nodes
    builder.add_conditional_edges(
        "check_budget",
        lambda state: check_budget(state),  # The routing function
        {
            "within_budget": "finalize_plan",   # If budget OK → finalize
            "over_budget": "renegotiate_plan",  # If over → renegotiate
        }
    )
    
    # After renegotiate, check budget again (loop back)
    builder.add_edge("renegotiate_plan", "check_budget")
    
    # Finalize → End
    builder.add_edge("finalize_plan", END)
    
    graph = builder.compile()
    return graph


# ============================================================
# RUN IT
# ============================================================

if __name__ == "__main__":
    graph = create_smart_travel_graph()
    
    # Test Case 1: Budget is tight
    print("\n" + "="*70)
    print("SCENARIO 1: TIGHT BUDGET (will need renegotiation)")
    print("="*70)
    trip1 = TravelState(
        destination="Paris",
        budget=1200.0,  # Too tight!
        num_days=7
    )
    result1 = graph.invoke(trip1)
    print(result1.plan)
    
    # Test Case 2: Budget is comfortable
    print("\n" + "="*70)
    print("SCENARIO 2: COMFORTABLE BUDGET (first try works)")
    print("="*70)
    trip2 = TravelState(
        destination="Barcelona",
        budget=2500.0,  # Plenty of room
        num_days=5
    )
    result2 = graph.invoke(trip2)
    print(result2.plan)
