"""
SPRINT 2: COORDINATOR AGENT
============================
The Coordinator extracts structured trip data from a user's free-form request.

Role: Parser / Input Processor
Input: user_request (messy text)
Output: Updated TripState with destination, budget, dates, preferences, etc.

This follows production patterns:
- Type hints for all functions
- Error handling with fallbacks
- Structured logging
- Docstrings for clarity
- Uses LangChain's built-in parsing
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from src.travel_planner.state.TripState import TripState

# ============================================================
# SETUP & CONFIGURATION
# ============================================================

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM (use environment variable for API key)
LLM = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,  # Lower temp for deterministic parsing
    api_key=os.getenv("GOOGLE_API_KEY"),
)


# ============================================================
# COORDINATOR AGENT FUNCTION
# ============================================================

def coordinator_agent(state: TripState) -> TripState:
    """
    Main coordinator function for Sprint 2.
    
    Workflow:
        1. Check if user_request exists
        2. Extract structured data from the request using LLM
        3. Update state with extracted data
        4. Create a summary for logging
        5. Return updated state
    
    Args:
        state (TripState): Input state with user_request field
        
    Returns:
        TripState: Updated state with extracted trip data
    """
    
    logger.info("="*70)
    logger.info("COORDINATOR AGENT STARTED")
    logger.info("="*70)
    
    # Validation: Check if user provided a request
    if not state.user_request or state.user_request.strip() == "":
        logger.warning("No user request provided. Returning empty state.")
        state.coordinator_summary = "Error: No user request provided"
        return state
    
    logger.info(f"User Request: {state.user_request[:100]}...")
    
    # Step 1: Extract trip data from user request
    try:
        extracted_data = extract_trip_data_from_request(state.user_request)
        logger.info("Successfully extracted trip data")
    except Exception as e:
        logger.error(f"Failed to extract data: {e}")
        state.coordinator_summary = f"Error during extraction: {str(e)}"
        return state
    
    # Step 2: Update state with extracted data
    try:
        state = update_state_with_extracted_data(state, extracted_data)
        logger.info("Successfully updated state with extracted data")
    except Exception as e:
        logger.error(f"Failed to update state: {e}")
        state.coordinator_summary = f"Error updating state: {str(e)}"
        return state
    
    # Step 3: Create summary for transparency
    state.coordinator_summary = create_summary(state)
    
    logger.info("COORDINATOR AGENT COMPLETED SUCCESSFULLY")
    logger.info(state.coordinator_summary)
    
    return state


# ============================================================
# HELPER FUNCTION 1: Extract data using LLM
# ============================================================

def extract_trip_data_from_request(user_request: str) -> Dict[str, Any]:
    """
    Use ChatGPT to parse a user's trip request and return structured JSON.
    
    The LLM is given clear instructions to extract:
    - destination
    - departure_city
    - departure_date
    - return_date
    - no_of_travelers
    - budget
    - trip_type
    - preferences
    
    Args:
        user_request (str): Raw user input
        
    Returns:
        Dict: Extracted data as JSON
        
    Raises:
        OutputParserException: If LLM response is not valid JSON
    """
    
    # Create the extraction prompt
    # This prompt tells the LLM exactly what we need and how to format it
    extraction_prompt = ChatPromptTemplate.from_template("""
You are a travel planning assistant. Your job is to extract structured trip information from a user's request.

USER REQUEST:
{user_request}

Extract the following information. Follow these rules:
1. If a field is not mentioned, use a sensible default
2. For dates: Try to infer from context (e.g., "next weekend" → calculate dates). Format as YYYY-MM-DD if possible
3. For destination: Must be a valid city/country name
4. For budget: Return as a float number (e.g., 3000.0)
5. For trip_type: Choose from: relaxation, adventure, cultural, business, family, luxury, budget
6. For preferences: Return as a list of strings (e.g., ["beaches", "hiking"])

Return ONLY valid JSON with these exact fields:
{{
    "destination": "string (required)",
    "departure_city": "string (default: 'unspecified' if not given)",
    "departure_date": "YYYY-MM-DD format or best guess",
    "return_date": "YYYY-MM-DD format or best guess",
    "no_of_travelers": "integer (default: 1)",
    "budget": "float in USD (default: 0.0)",
    "trip_type": "string (default: 'general')",
    "preferences": "list of strings (default: [])"
}}

Do not include any text before or after the JSON. Return ONLY the JSON object.
""")
    
    try:
        # Create the parsing chain
        parser = JsonOutputParser()
        chain = extraction_prompt | LLM | parser
        
        # Invoke the chain
        extracted_data = chain.invoke({"user_request": user_request})
        
        logger.debug(f"Extracted data: {extracted_data}")
        return extracted_data
        
    except OutputParserException as e:
        logger.error(f"Failed to parse LLM output as JSON: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}")
        raise


# ============================================================
# HELPER FUNCTION 2: Update state with extracted data
# ============================================================

def update_state_with_extracted_data(
    state: TripState, 
    extracted_data: Dict[str, Any]
) -> TripState:
    """
    Update the TripState object with data extracted from the LLM.
    
    This function:
    - Safely extracts values from the dict
    - Applies type conversions
    - Validates ranges (e.g., budget > 0)
    - Provides fallbacks for missing fields
    
    Args:
        state (TripState): The state object to update
        extracted_data (Dict): Extracted data from LLM
        
    Returns:
        TripState: Updated state
    """
    
    # Safely extract each field with type conversion and validation
    
    state.destination = str(extracted_data.get("destination", "")).strip()
    
    state.departure_city = str(extracted_data.get("departure_city", "unspecified")).strip()
    
    state.departure_date = str(extracted_data.get("departure_date", "")).strip()
    
    state.return_date = str(extracted_data.get("return_date", "")).strip()
    
    # Convert to int with validation
    try:
        no_travelers = int(extracted_data.get("no_of_travelers", 1))
        state.no_of_travelers = max(1, no_travelers)  # Ensure at least 1 traveler
    except (ValueError, TypeError):
        state.no_of_travelers = 1
    
    # Convert budget to float with validation
    try:
        budget = float(extracted_data.get("budget", 0.0))
        state.budget = max(0.0, budget)  # Ensure non-negative
    except (ValueError, TypeError):
        state.budget = 0.0
    
    state.trip_type = str(extracted_data.get("trip_type", "general")).strip().lower()
    
    # Handle preferences (should be a list)
    prefs = extracted_data.get("preferences", [])
    if isinstance(prefs, list):
        state.preferences = [str(p).strip() for p in prefs]
    else:
        state.preferences = []
    
    logger.debug(f"State updated: dest={state.destination}, budget={state.budget}, travelers={state.no_of_travelers}")
    
    return state


# ============================================================
# HELPER FUNCTION 3: Create a summary for logging/display
# ============================================================

def create_summary(state: TripState) -> str:
    """
    Create a human-readable summary of the extracted trip data.
    
    Args:
        state (TripState): The updated state
        
    Returns:
        str: Formatted summary
    """
    
    summary = f"""
TRIP DETAILS EXTRACTED & PARSED:
================================================================
Destination:          {state.destination or "Not specified"}
Departure City:       {state.departure_city or "Not specified"}
Departure Date:       {state.departure_date or "Not specified"}
Return Date:          {state.return_date or "Not specified"}
Number of Travelers:  {state.no_of_travelers}
Budget:               ${state.budget:,.2f}
Trip Type:            {state.trip_type or "General"}
Preferences:          {', '.join(state.preferences) if state.preferences else "None specified"}
================================================================

Next Step: Passing to Flight Agent (Sprint 3)
"""
    return summary
