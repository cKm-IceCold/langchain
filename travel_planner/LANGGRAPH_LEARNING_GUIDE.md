# LangGraph Learning Guide for Travel Planner

## What is LangGraph? (Simple Explanation)

**LangChain** helps you talk to LLMs and use tools.
**LangGraph** helps you coordinate WHEN and HOW to use those tools in a workflow.

### Analogy
- **LangChain** = "I can call an LLM, or search the web, or run Python code"
- **LangGraph** = "First search the web, then call an LLM with results, then decide: if X then Y, else Z"

---

## Core LangGraph Concepts

### 1. **State** (The Data Container)
```python
from pydantic import BaseModel

class TravelState(BaseModel):
    destination: str
    budget: float
    flights_found: bool
    plan: str
```
- This is like a shared variable that all nodes can read/modify
- It flows through your entire workflow
- Kind of like the `run_variables` in LangChain's LCEL chains

### 2. **Nodes** (The Workers)
```python
def search_flights(state: TravelState) -> TravelState:
    # Do work here
    state.flights_found = True
    return state
```
- Each node is a function that takes `State` → returns `State`
- Does one specific job
- Similar to a "tool" or "step" in LangChain, but more structured

### 3. **Edges** (The Connections)
```python
builder.add_edge("search_flights", "search_hotels")
# Means: After search_flights finishes, run search_hotels
```
- Connect nodes in sequence
- Linear flow: A → B → C

### 4. **Conditional Edges** (The Decisions) ⭐ THE POWER OF LANGGRAPH
```python
builder.add_conditional_edges(
    "check_budget",
    lambda state: "within_budget" if state.total_cost <= state.budget else "over_budget",
    {
        "within_budget": "finalize_plan",
        "over_budget": "renegotiate",
    }
)
# Means: Based on a decision, go to different nodes
```
- This is where LangGraph shines!
- Instead of linear flow, you can branch: "if X then do Y, else do Z"
- Can even loop back: check → adjust → check again

---

## LangChain vs LangGraph

| Task | LangChain | LangGraph |
|------|-----------|-----------|
| Call an LLM | ✅ Perfect | ✅ Uses LangChain internally |
| Chain operations | ✅ LCEL chains | ✅ Better (more control) |
| Conditional logic | 🤔 Possible (hacky) | ✅ Clean conditional_edges |
| Loop/retry logic | 🤔 Possible (hacky) | ✅ Built-in |
| State management | 🤔 Run variables | ✅ Structured with Pydantic |
| Multi-agent coordination | 🤔 Complex | ✅ Designed for this |

---

## How to Build a LangGraph in 5 Steps

### Step 1: Define Your State
```python
class MyState(BaseModel):
    input_field: str
    processing_result: str
```

### Step 2: Create Node Functions
```python
def process_step(state: MyState) -> MyState:
    state.processing_result = "done"
    return state
```

### Step 3: Instantiate StateGraph
```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(MyState)
```

### Step 4: Add Nodes and Edges
```python
builder.add_node("process", process_step)
builder.add_edge(START, "process")
builder.add_edge("process", END)
```

### Step 5: Compile and Invoke
```python
graph = builder.compile()
result = graph.invoke(MyState(input_field="hello"))
```

---

## Your Travel Planner Workflow

Here's how to think about your project:

```
USER INPUT
    ↓
[Input Processing] → Gather destination, budget, dates
    ↓
[Search Node 1] → Find flights
    ↓
[Search Node 2] → Find hotels
    ↓
[Search Node 3] → Find activities
    ↓
[Validation Node] ← Decision point!
    ├─ If within budget → [Finalize]
    └─ If over budget → [Re-negotiate] ↻ (loop back to validation)
    ↓
[Coordinator] → Combine all results
    ↓
FINAL TRIP PLAN
```

In LangGraph:
- **Nodes**: search_flights, search_hotels, search_activities, validate, renegotiate, finalize
- **State**: TravelState (budget, destination, dates, costs, plan)
- **Edges**: Linear flow (search → search → search)
- **Conditional Edges**: After validate → if OK go to finalize, else go to renegotiate → back to validate

---

## How to Test LangGraph Locally

1. Install: `uv pip install langgraph langchain`
2. Run the examples: `python simple_example.py`
3. See the workflow execute step-by-step

---

## Common Mistakes to Avoid

❌ **Don't**: Make nodes too big (one node = one task)
✅ **Do**: Break into smaller focused nodes

❌ **Don't**: Forget to return state from node functions
✅ **Do**: Always `return state` (modified)

❌ **Don't**: Put LLM logic directly in nodes
✅ **Do**: Separate LangChain LLM calls from LangGraph node logic

---

## Real Travel Planner Example Structure

```
src/
├── state.py          # Define TravelState (like TripState)
├── nodes/
│   ├── search_flights.py
│   ├── search_hotels.py
│   ├── search_activities.py
│   └── validate.py
├── graph.py          # Build the LangGraph workflow
└── main.py           # Invoke the graph
```

Each node file can have LangChain logic (LLM calls, tools, etc.)
The graph.py orchestrates them all.

---

## Next Steps for Your Learning

1. **Run the examples**: Execute `simple_example.py` and `conditional_routing_example.py`
2. **Modify the examples**: Change costs, add more nodes, test edge cases
3. **Add LLM calls**: Instead of fake data, use LangChain to call an LLM
4. **Expand to real workflow**: Build your 4-agent Travel Planner
5. **Add persistence**: Save state to database

---

## Quick Reference: Key Classes and Functions

```python
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

# 1. Define state
class State(BaseModel):
    field: type

# 2. Create builder
builder = StateGraph(State)

# 3. Add nodes (functions)
builder.add_node("name", function)

# 4. Connect nodes
builder.add_edge(START, "name")
builder.add_edge("name1", "name2")

# 5. Add decisions
builder.add_conditional_edges(
    "source_node",
    decision_function,
    {"option1": "target1", "option2": "target2"}
)

# 6. Compile
graph = builder.compile()

# 7. Run
result = graph.invoke(State(...))
```

---

## Resources

- LangGraph Docs: https://langchain-ai.github.io/langgraph/
- LangChain Docs: https://python.langchain.com/
- GitHub Examples: https://github.com/langchain-ai/langgraph/tree/main/examples
