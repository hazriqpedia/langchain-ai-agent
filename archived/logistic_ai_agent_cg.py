from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from datetime import datetime
import json

load_dotenv()

# ---------------- Mock Data ----------------

MOCK_TRACKING_DATA = {
    "AWB-12345": {"status": "En Route", "location": "Kuala Lumpur", "postal_code": "56000"},
    "AWB-67890": {"status": "Delivered", "location": "Ampang Jaya", "postal_code": "68000"},
}

MOCK_RESCHEDULE_ALLOWED = {
    "AWB-12345": True,
    "AWB-67890": False,
}

MOCK_RESCHEDULE_DATES = {
    "AWB-12345": ["2025-05-15", "2025-05-16", "2025-05-17"],
}

MOCK_RESCHEDULE_CONFIRMATION = {
    "AWB-12345": {"original_date": "2025-05-12", "new_date": "", "status": "Pending"}
}

# ---------------- Pydantic Output ----------------


class LogisticsResponse(BaseModel):
    response: str
    tools_used: list[str]

# ---------------- Tool Functions ----------------


# Acts like in-memory variable to share AWB between tools
context_memory = {"awb": None}


def mock_track_shipment(tracking_number: str) -> str:
    context_memory["awb"] = tracking_number  # Save to memory manually
    if tracking_number in MOCK_TRACKING_DATA:
        data = MOCK_TRACKING_DATA[tracking_number]
        return f"Shipment {tracking_number} is currently '{data['status']}' in '{data['location']}'."
    return f"Tracking number '{tracking_number}' not found."


def mock_check_reschedule_availability(_: str) -> str:
    tracking_number = context_memory.get("awb")
    if not tracking_number:
        return "Tracking number not found in memory."
    allowed = MOCK_RESCHEDULE_ALLOWED.get(tracking_number, False)
    return "Rescheduling is allowed." if allowed else "Rescheduling is not allowed."


def mock_get_reschedule_dates(_: str) -> str:
    tracking_number = context_memory.get("awb")
    if not tracking_number:
        return "Tracking number not found in memory."
    if MOCK_RESCHEDULE_ALLOWED.get(tracking_number, False):
        dates = MOCK_RESCHEDULE_DATES.get(tracking_number, [])
        return f"Available dates: {', '.join(dates)}" if dates else "No dates available."
    return "Rescheduling not allowed."


def mock_confirm_reschedule(info: str) -> str:
    tracking_number = context_memory.get("awb")
    if not tracking_number:
        return "Tracking number not found in memory."

    try:
        # Parse from natural language
        parts = info.lower().split()
        date = next((p for p in parts if p.startswith("2025-")), None)
        postcode = next(
            (p for p in parts if p.isdigit() and len(p) == 5), None)
        if not date or not postcode:
            return "Please provide a valid date and 5-digit postcode."

        # Validate postcode
        correct_postcode = MOCK_TRACKING_DATA[tracking_number]["postal_code"]
        if postcode != correct_postcode:
            return "Postal code verification failed."

        if date not in MOCK_RESCHEDULE_DATES.get(tracking_number, []):
            return f"{date} is not available for rescheduling."

        MOCK_RESCHEDULE_CONFIRMATION[tracking_number]["new_date"] = date
        MOCK_RESCHEDULE_CONFIRMATION[tracking_number]["status"] = "Rescheduled"
        return f"Shipment {tracking_number} successfully rescheduled to {date}."

    except Exception as e:
        return f"Failed to confirm rescheduling: {str(e)}"

# ---------------- Tool Wrappers ----------------


tools = [
    Tool(name="track_shipment", func=mock_track_shipment,
         description="Use to track shipment. Input is tracking number."),
    Tool(name="check_reschedule_availability", func=mock_check_reschedule_availability,
         description="Use to check if rescheduling is allowed. No input."),
    Tool(name="get_reschedule_dates", func=mock_get_reschedule_dates,
         description="Get available rescheduling dates. No input."),
    Tool(name="confirm_reschedule", func=mock_confirm_reschedule,
         description="Confirm reschedule. Input includes date and postal code.")
]

# ---------------- LLM + Memory Setup ----------------

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

parser = PydanticOutputParser(pydantic_object=LogisticsResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a helpful logistics assistant. "
         "You must wrap your final answer in valid JSON format based on these instructions:\n"
         "{format_instructions}\n"
         "Example:\n"
         "{ \"response\": \"...your answer...\", \"tools_used\": [\"tool_name\"] }"
         ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(
    agent=agent, tools=tools, memory=memory, verbose=True)

# ---------------- Run Chat Loop ----------------

print("\n📦 Logistics Assistant Chat (type 'exit' to quit)\n")
while True:
    user_input = input("You: ")
    if user_input.strip().lower() in ["exit", "quit"]:
        break

    result = agent_executor.invoke({"input": user_input})
    try:
        parsed = parser.parse(result["output"])
        print("\n--- Response ---")
        print(parsed.response)
        print("Tools used:", parsed.tools_used)
    except Exception as e:
        print("⚠️ Could not parse response.")
        print(result["output"])
