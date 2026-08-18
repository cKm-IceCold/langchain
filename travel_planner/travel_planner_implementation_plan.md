# Travel Planner Agent – Implementation Plan

## 1. Ready-to-use project structure

```text
travel_planner/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── pyproject.toml
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── db.py
│   ├── state.py
│   ├── schemas.py
│   ├── prompts.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── flight_search.py
│   │   ├── hotel_search.py
│   │   ├── activity_search.py
│   │   ├── weather_tool.py
│   │   └── budget_tool.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── coordinator.py
│   │   ├── flight_agent.py
│   │   ├── hotel_agent.py
│   │   ├── activity_agent.py
│   │   └── budget_agent.py
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── trip_planner.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   ├── search_service.py
│   │   └── llm_service.py
│   └── utils/
│       ├── __init__.py
│       ├── validation.py
│       ├── formatting.py
│       └── logging.py
├── data/
│   ├── trips.db
│   └── seed_data.sql
├── tests/
│   ├── __init__.py
│   ├── test_state.py
│   ├── test_tools.py
│   ├── test_agents.py
│   └── test_workflow.py
└── notebooks/
    └── travel_planner_demo.ipynb
```

### Expected responsibilities

- app/main.py
  - app startup
  - agent orchestration entry point

- app/config.py
  - environment variables
  - model names
  - API keys

- app/state.py
  - TripState definition

- app/tools/
  - all external skills and API wrappers

- app/agents/
  - specialist agent definitions

- app/workflows/
  - the coordinator flow and orchestration logic

- app/db.py
  - database connection and session management

- data/
  - local SQLite database and seed scripts

- tests/
  - focus on agent behavior, tool failures, and state updates

---

## 2. Database schema

For the first version, SQLite is the easiest choice because it is lightweight, local, and simple for development. Later you can move to PostgreSQL if you need more scale and production features.

### Recommended database tables

#### users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### trips
```sql
CREATE TABLE trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    destination TEXT NOT NULL,
    departure_city TEXT,
    start_date TEXT,
    end_date TEXT,
    travelers INTEGER DEFAULT 1,
    budget REAL,
    trip_type TEXT,
    preferences TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### trip_flights
```sql
CREATE TABLE trip_flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    airline TEXT,
    departure_airport TEXT,
    arrival_airport TEXT,
    departure_time TEXT,
    arrival_time TEXT,
    duration TEXT,
    price REAL,
    rating REAL,
    raw_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);
```

#### trip_hotels
```sql
CREATE TABLE trip_hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    hotel_name TEXT,
    location TEXT,
    price_per_night REAL,
    rating REAL,
    amenities TEXT,
    raw_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);
```

#### trip_activities
```sql
CREATE TABLE trip_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    price REAL,
    day_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);
```

#### trip_budget
```sql
CREATE TABLE trip_budget (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    estimated_total REAL,
    flights_cost REAL,
    hotel_cost REAL,
    activities_cost REAL,
    status TEXT DEFAULT 'within_budget',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);
```

### Why this schema works

- supports MVP trip planning quickly
- keeps the core planning objects separate
- allows ranking and comparison of multiple flight/hotel options
- makes expansion to saved history and user personalization easier

### Suggested ORM layer

For Python, use either:
- SQLAlchemy ORM
- or direct sqlite3 wrapper

For a cleaner dev experience, SQLAlchemy is recommended.

---

## 3. Implementation order for Sprints 1–5

This is the exact build order I recommend for moving from MVP to a working multi-agent travel planner.

### Sprint 1 — Foundation and environment setup

#### Goal
Set up the project and model integration.

#### Tasks
- create project folders
- install dependencies
- configure environment variables
- create base LLM client connection
- create basic app entrypoint
- set up logging and config

#### Deliverable
A working Python app that can call an LLM and respond to a simple prompt.

#### Example result
The app can do:

```python
response = chat_model.invoke("Plan a trip to Paris")
print(response)
```

#### Acceptance criteria
- project runs locally
- env keys are loaded correctly
- model call works

---

### Sprint 2 — State model and orchestrator

#### Goal
Create the shared memory and coordinator logic.

#### Tasks
- define `TripState`
- define trip data schema
- create `CoordinatorAgent`
- parse a user request into structured data
- update state after extracting fields

#### Example state
```python
TripState = {
    "destination": "Lisbon",
    "departure_city": "London",
    "start_date": "2026-09-12",
    "end_date": "2026-09-18",
    "travelers": 2,
    "budget": 1200,
    "trip_type": "leisure",
    "preferences": "food, museums, scenic neighborhoods"
}
```

#### Deliverable
The system can accept a trip request and convert it into structured travel information.

#### Acceptance criteria
- state is populated correctly
- coordinator identifies missing fields
- coordinator knows when to delegate work

---

### Sprint 3 — Flight agent and tool integration

#### Goal
Add the first real specialist agent.

#### Tasks
- build `flight_search` tool
- create `FlightAgent`
- connect to external flight API or mock/sandbox data first
- rank results by price, time, and convenience
- return a shortlist

#### Tool behavior
The flight agent should be able to:
- search flights from departure city to destination
- compare best routes
- filter by budget and trip timing

#### Deliverable
The workflow can recommend a few flight options.

#### Acceptance criteria
- flight tool works reliably
- output is ranked
- errors are handled gracefully

---

### Sprint 4 — Hotel and activity agents

#### Goal
Expand planning beyond flights.

#### Tasks
- create `hotel_search` tool
- create `HotelAgent`
- create `activity_search` tool
- create `ActivityAgent`
- generate a 2–5 day activity plan

#### Deliverable
The app can produce a meaningful itinerary with hotel and activity suggestions.

#### Acceptance criteria
- hotel options reflect destination and budget
- activity suggestions fit user interests
- itinerary is structured and coherent

---

### Sprint 5 — Budget agent and full trip summary

#### Goal
Close the loop with cost validation and final itinerary generation.

#### Tasks
- create `budget_tool`
- create `BudgetAgent`
- total estimated costs
- compare against budget
- generate final response summary

#### Final output example
```text
Trip Plan for Lisbon

Flights:
- Option A: London -> Lisbon, $220, 3h 15m

Hotels:
- Budget Hotel: $90/night
- Boutique Stay: $140/night

Activities:
- Day 1: Alfama walking tour
- Day 2: Sintra day trip
- Day 3: food tour

Estimated total: $1,180
Budget status: within budget
```

#### Deliverable
A complete MVP travel planner that can plan a trip in one run.

#### Acceptance criteria
- user request completes end-to-end
- itinerary is coherent
- budget and options are included
- no major orchestration failures

---

## 4. Recommended development sequence for the first 5 sprints

If you want the cleanest path, do this in order:

1. app setup and environment
2. coordinator and TripState
3. flight tool and flight agent
4. hotel + activities
5. budget + final summary

This order creates the fastest path to a realistic MVP without building too much complexity too early.

---

## 5. Suggested milestone checkpoints

### Milestone A: Agent can respond
- model works
- prompt flow functions

### Milestone B: Structured trip data
- input parsing works
- state is maintained

### Milestone C: Real planning tools work
- flight agent works
- hotel agent works
- activity agent works

### Milestone D: MVP ready
- full itinerary returned
- budget included
- final answer is usable

---

## 6. Best next step

Start with Sprint 1 and Sprint 2 first, because the design is only strong if the coordinator and state model are solid. Once those are working, the specialist agents can be added cleanly without rewriting the architecture.

This is the right order for building a reliable multi-agent travel planner.
