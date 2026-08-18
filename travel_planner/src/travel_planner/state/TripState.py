from typing import Optional, List
from pydantic import BaseModel, Field


class TripState(BaseModel):
    """
    Centralized state for the entire trip planning workflow.
    
    Fields are organized by workflow stage:
    - Input: user_request (raw user input for Sprint 2)
    - Extracted by Coordinator: destination, dates, budget, preferences, etc.
    - Results from Agents: flight_results, hotel_results, activities
    - Final: final_plan
    """
    
    # ===== INPUT (Sprint 2 - Coordinator starts here) =====
    user_request: str = Field(default="", description="Raw user input for trip planning")
    
    # ===== EXTRACTED BY COORDINATOR (Sprint 2 Output) =====
    destination: str = Field(default="", description="Where the traveler wants to go")
    departure_city: str = Field(default="", description="Where the traveler is leaving from")
    departure_date: str = Field(default="", description="When the trip starts (YYYY-MM-DD)")
    return_date: str = Field(default="", description="When the trip ends (YYYY-MM-DD)")
    no_of_travelers: int = Field(default=1, description="Number of people traveling")
    budget: float = Field(default=0.0, description="Total budget in USD")
    trip_type: str = Field(default="", description="Type: relaxation, adventure, cultural, business, etc.")
    preferences: List[str] = Field(default_factory=list, description="Activities/interests: beaches, hiking, food, etc.")
    
    # ===== COORDINATOR PROCESSING =====
    coordinator_summary: str = Field(default="", description="Summary of extracted data from user request")
    
    # ===== RESULTS FROM AGENTS (Sprints 3-6) =====
    flight_results: Optional[List[dict]] = Field(default=None, description="List of flight options")
    hotel_results: Optional[List[dict]] = Field(default=None, description="List of hotel options")
    activities: Optional[List[dict]] = Field(default=None, description="Suggested activities/itinerary")
    
    # ===== VALIDATION & FINAL OUTPUT (Sprint 6 onwards) =====
    total_cost: float = Field(default=0.0, description="Total estimated cost")
    is_within_budget: bool = Field(default=True, description="Whether plan fits budget")
    final_plan: str = Field(default="", description="Final formatted trip plan")
    
    class Config:
        arbitrary_types_allowed = True
