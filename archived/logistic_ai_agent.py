from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
from datetime import datetime
import json

load_dotenv()

# Mock API Outputs
MOCK_TRACKING_DATA = {
    "AWB-12345": {"status": "En Route", "location": "Kuala Lumpur"},
    "AWB-67890": {"status": "Delivered", "location": "Ampang Jaya"},
}

MOCK_RESCHEDULE_ALLOWED = {
    "AWB-12345": True,
    "AWB-67890": False,
}

MOCK_RESCHEDULE_DATES = {
    "AWB-12345": ["2025-05-15", "2025-05-16", "2025-05-17"],
}

MOCK_RESCHEDULE_CONFIRMATION = {
    "AWB-12345": {"original_date": "2025-05-12", "new_date": "2025-05-15", "status": "Rescheduled"}
}

# Pydantic Model for Output


class LogisticsResponse(BaseModel):
    ''' Pydantic Set up. Output will follow this model. '''
    response: str
    tools_used: list[str]

# Tool 1: Tracking Tool


def mock_track_shipment(tracking_number: str) -> str:
    """Mocks fetching the tracking status of a shipment."""
    if tracking_number in MOCK_TRACKING_DATA:
        data = MOCK_TRACKING_DATA[tracking_number]
        return f"Shipment {tracking_number} is currently '{data['status']}' in '{data['location']}'."
    else:
        return f"Tracking number '{tracking_number}' not found."


tracking_tool = Tool(
    name="track_shipment",
    func=mock_track_shipment,
    description="Use this tool to find the current status and location of a shipment. Input should be the tracking number (e.g., AWB-12345).",
)

# Tool 2: Rescheduling Check Tool


def mock_check_reschedule_availability(tracking_number: str) -> str:
    """Mocks checking if rescheduling is allowed for a shipment."""
    if tracking_number in MOCK_RESCHEDULE_ALLOWED:
        if MOCK_RESCHEDULE_ALLOWED[tracking_number]:
            return "Rescheduling is allowed for this shipment."
        else:
            return "Rescheduling is not allowed for this shipment."
    else:
        return f"Tracking number '{tracking_number}' not found."


reschedule_check_tool = Tool(
    name="check_reschedule_availability",
    func=mock_check_reschedule_availability,
    description="Use this tool to determine if rescheduling is allowed for a given shipment tracking number.",
)

# Tool 3: Rescheduling Window Check Tool


def mock_get_reschedule_dates(tracking_number: str) -> str:
    """Mocks getting available rescheduling dates for a shipment."""
    if tracking_number in MOCK_RESCHEDULE_DATES and MOCK_RESCHEDULE_ALLOWED.get(tracking_number, False):
        dates = MOCK_RESCHEDULE_DATES[tracking_number]
        return f"Available rescheduling dates are: {', '.join(dates)}."
    elif tracking_number not in MOCK_RESCHEDULE_ALLOWED:
        return f"Tracking number '{tracking_number}' not found."
    else:
        return "Rescheduling is not allowed for this shipment."


reschedule_dates_tool = Tool(
    name="get_reschedule_dates",
    func=mock_get_reschedule_dates,
    description="Use this tool to get the available dates for rescheduling a shipment, given the tracking number and confirming that rescheduling is allowed.",
)

# Tool 4: Rescheduling Confirm Tool


def mock_confirm_reschedule(tracking_number: str, new_date: str) -> str:
    """Mocks confirming the rescheduling of a shipment."""
    if tracking_number in MOCK_RESCHEDULE_DATES and new_date in MOCK_RESCHEDULE_DATES[tracking_number] and MOCK_RESCHEDULE_ALLOWED.get(tracking_number, False):
        confirmation = MOCK_RESCHEDULE_CONFIRMATION.get(tracking_number, {})
        confirmation["new_date"] = new_date
        return f"Shipment {tracking_number} has been successfully rescheduled to {new_date}."
    elif tracking_number not in MOCK_RESCHEDULE_ALLOWED:
        return f"Tracking number '{tracking_number}' not found."
    elif not MOCK_RESCHEDULE_ALLOWED.get(tracking_number, False):
        return "Rescheduling is not allowed for this shipment."
    else:
        return f"The requested date '{new_date}' is not available for rescheduling."


confirm_reschedule_tool = Tool(
    name="confirm_reschedule",
    func=mock_confirm_reschedule,
    description="Use this tool to confirm the rescheduling of a shipment to a specific date, given the tracking number and a valid rescheduling date.",
)

# LLM Setup
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Prompt Setup
parser = PydanticOutputParser(pydantic_object=LogisticsResponse)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a helpful logistics assistant. When the user asks for information about shipments, "
         "explain which tool you are using and what the tool's output is before providing the final answer. "
         "Use the relevant tool to retrieve the information. "
         "Your final response should be a concise answer to the user's query, and you must indicate which tools you used. "
         "Format your final response in the following JSON format:\n{format_instructions}"),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

# Agent Setup
tools = [tracking_tool, reschedule_check_tool,
         reschedule_dates_tool, confirm_reschedule_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# User Interaction
query = input("How can I help you with your shipment today? ")
raw_response = agent_executor.invoke({"query": query})

try:
    structured_response = parser.parse(raw_response.get("output"))
    print("\n--- Structured Response ---")
    print(structured_response)
    print("\n- Final Response:", structured_response.response)
    print("- Tools Used:", structured_response.tools_used)
except Exception as e:
    print("Error parsing response:", e)
    print("Raw Response:", raw_response)
