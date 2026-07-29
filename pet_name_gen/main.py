from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv ()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1,
    timeout=10000,
    max_retries=6,
    max_tokens=10000
)

messages = [
    SystemMessage(
        content="You are an expert at creating funny African pet names and all five should be from different African Languages."
    ),
    HumanMessage(
        content="Suggest Five Names of a Female Golden Retriever"
    ),
]

response = model.invoke(messages)

print(response.content)
#print(type[(model), (messages), (response)])
