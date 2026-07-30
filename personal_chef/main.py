from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from langgraph.checkpoint.memory import InMemorySaver

from tavily import TavilyClient

load_dotenv()

# --------------------
# MODEL
# --------------------

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
)

# --------------------
# TAVILY
# --------------------

tavily_client = TavilyClient()


@tool
def web_search(query: str) -> str:
    """
    Search the web for recipes, ingredients,
    cooking techniques, and food trends.
    """
    results = tavily_client.search(
        query=query,
        max_results=5
    )

    return str(results)


# --------------------
# MEMORY
# --------------------

checkpointer = InMemorySaver()

# --------------------
# SYSTEM PROMPT
# --------------------

SYSTEM_PROMPT = """
You are a helpful personal chef.

Responsibilities:
- Suggest meals based on ingredients.
- Remember user food preferences.
- Remember dietary restrictions and allergies.
- Use web_search only when current or external information is needed.
- For common recipes, answer directly without searching.

Always explain your reasoning clearly.
"""

# --------------------
# AGENT
# --------------------

agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)

# --------------------
# CONFIG
# --------------------

config = {
    "configurable": {
        "thread_id": "chef-user-1"
    }
}

# --------------------
# CHAT LOOP
# --------------------

while True:

    user_input = input("\nYou: ")

    if user_input.lower() in ["quit", "exit"]:
        break

    response = agent.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ]
        },
        config=config,
    )

    print(
        "\nChef:",
        response["messages"][-1].content
    )