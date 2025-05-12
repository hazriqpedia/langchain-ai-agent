import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool  # Keeping user's original import for Tool
from langchain.memory import ConversationBufferMemory
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables from .env file
load_dotenv()

# Set up basic logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Mock API Outputs (Unchanged)
MOCK_TRACKING_DATA = {
    "AWB-12345": {"status": "En Route", "location": "Kuala Lumpur"},
    "AWB-67890": {"status": "Delivered", "location": "Ampang Jaya"},
    "AWB-1234": {"status": "En Route", "location": "Petaling Jaya"}
}
MOCK_RESCHEDULE_ALLOWED = {
    "AWB-12345": True,
    "AWB-67890": False,
    "AWB-1234": False
}
MOCK_RESCHEDULE_DATES = {
    "AWB-12345": ["2025-05-15", "2025-05-16", "2025-05-17"],
}
MOCK_RESCHEDULE_CONFIRMATION = {  # This can be used by mock_confirm_reschedule if you want to simulate state change
    "AWB-12345": {"original_date": "2025-05-12", "new_date": "", "status": "Pending Reschedule"},
}

# Mock Tools (Functions are mostly unchanged, ensure they return simple strings)


def mock_track_shipment(tracking_number: str) -> str:
    logging.info(
        f"Calling mock_track_shipment with tracking_number: {tracking_number}")
    if tracking_number in MOCK_TRACKING_DATA:
        data = MOCK_TRACKING_DATA[tracking_number]
        # Improved phrasing
        result = f"Your shipment AWB-{tracking_number} is currently '{data['status']}' in '{data['location']}'."
        logging.info(f"mock_track_shipment result: {result}")
        return result
    else:
        result = f"I'm sorry, tracking number '{tracking_number}' not found."
        logging.info(f"mock_track_shipment result: {result}")
        return result


tracking_tool = Tool(
    name="track_shipment",
    func=mock_track_shipment,
    description="Use this tool to get the current status and location of a shipment given its tracking number (e.g., AWB-XXXXX).",
)


def mock_check_reschedule_availability(tracking_number: str) -> str:
    logging.info(
        f"Calling mock_check_reschedule_availability with tracking_number: {tracking_number}")
    if tracking_number in MOCK_RESCHEDULE_ALLOWED:
        if MOCK_RESCHEDULE_ALLOWED[tracking_number]:
            # Improved
            result = "Yes, you can reschedule this shipment. Please provide the new date (YYYY-MM-DD) and destination postal code."
            logging.info(
                f"mock_check_reschedule_availability result: {result}")
            return result
        else:
            result = "I'm sorry, rescheduling is not allowed for this shipment."
            logging.info(
                f"mock_check_reschedule_availability result: {result}")
            return result
    else:
        result = f"I'm sorry, tracking number '{tracking_number}' not found."
        logging.info(f"mock_check_reschedule_availability result: {result}")
        return result


reschedule_check_tool = Tool(
    name="check_reschedule_availability",
    func=mock_check_reschedule_availability,
    description="Use this tool to determine if rescheduling is allowed for a given shipment tracking number. Typically used if a user asks if they can reschedule their shipment.",
)


def mock_get_reschedule_dates(tracking_number: str) -> str:
    logging.info(
        f"Calling mock_get_reschedule_dates with tracking_number: {tracking_number}")
    if tracking_number in MOCK_RESCHEDULE_DATES and MOCK_RESCHEDULE_ALLOWED.get(tracking_number, False):
        dates = MOCK_RESCHEDULE_DATES[tracking_number]
        # Improved
        result = f"Available rescheduling dates for shipment AWB-{tracking_number} are: {', '.join(dates)}."
        logging.info(f"mock_get_reschedule_dates result: {result}")
        return result
    elif tracking_number not in MOCK_RESCHEDULE_ALLOWED:  # or tracking_number not in MOCK_RESCHEDULE_DATES
        result = f"I'm sorry, tracking number '{tracking_number}' not found or no specific dates available."
        logging.info(f"mock_get_reschedule_dates result: {result}")
        return result
    else:  # Not allowed
        result = "I'm sorry, rescheduling is not allowed for this shipment, so no dates can be provided."
        logging.info(f"mock_get_reschedule_dates result: {result}")
        return result


reschedule_dates_tool = Tool(
    name="get_reschedule_dates",
    func=mock_get_reschedule_dates,
    description="Use this tool to get the available dates for rescheduling a shipment, given the tracking number. Only use if rescheduling is confirmed to be allowed or if the user explicitly asks for available dates.",
)


def mock_confirm_reschedule(tracking_number: str, new_date: str, postal_code: str) -> str:
    logging.info(
        f"Calling mock_confirm_reschedule with tracking_number: {tracking_number}, new_date: {new_date}, postal_code: {postal_code}"
    )
    if not MOCK_RESCHEDULE_ALLOWED.get(tracking_number, False):
        result = "I'm sorry, rescheduling is not allowed for this shipment."
        logging.info(f"mock_confirm_reschedule result: {result}")
        return result
    if tracking_number in MOCK_RESCHEDULE_DATES and new_date in MOCK_RESCHEDULE_DATES.get(tracking_number, []):
        # Simulate update
        if tracking_number in MOCK_RESCHEDULE_CONFIRMATION:
            MOCK_RESCHEDULE_CONFIRMATION[tracking_number]["new_date"] = new_date
            MOCK_RESCHEDULE_CONFIRMATION[tracking_number]["status"] = "Rescheduled"
        # Improved
        result = f"Okay, I've rescheduled your shipment AWB-{tracking_number} to {new_date} for delivery to postal code {postal_code}."
        logging.info(f"mock_confirm_reschedule result: {result}")
        return result
    elif tracking_number not in MOCK_TRACKING_DATA:  # Check if AWB even exists broadly
        result = f"I'm sorry, tracking number '{tracking_number}' not found."
        logging.info(f"mock_confirm_reschedule result: {result}")
        return result
    else:  # Date not available or other issue
        result = f"I'm sorry, the requested date '{new_date}' is not available or suitable for rescheduling shipment {tracking_number}. Please try get_reschedule_dates to see available options."
        logging.info(f"mock_confirm_reschedule result: {result}")
        return result


confirm_reschedule_tool = Tool(
    name="confirm_reschedule",
    func=mock_confirm_reschedule,
    description="Use this tool to confirm the rescheduling of a shipment. This requires the tracking number, the new desired date (in-MM-DD format), and the destination postal code. Ensure the user has provided all three pieces of information and that rescheduling is allowed for the shipment.",
)

# LLM Setup
# Replace "gemini-1.5-flash-latest" with your specific model if needed e.g. "gemini-pro" or user's "gemini-2.0-flash"
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest", convert_system_message_to_human=False)

# Prompt Setup
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a helpful and friendly logistics assistant. "
         "Your primary goal is to assist users with their shipment queries. "
         "Respond to the user in a way that does not reveal the names of the tools being used.  Focus on providing clear and concise information to the user. "
         "Always refer to the conversation history (chat_history) to understand context, such as a tracking number that was mentioned earlier, especially if the user says 'it' or asks a follow-up question. "
         "If a tracking number is needed for a tool and has been provided in the current query or previous messages, use it. "
         "If a tracking number is needed for a tool and has not been provided in the current query or previous messages, politely ask the user for it. "
         # Added AWB format
         "An AWB number is a tracking number with the format AWB- followed by 5 digits (e.g., AWB-12345). "
         "When the user provides a request to reschedule a shipment,  ask for the new date and postal code, if you do not have both. "
         "If the user provides both the new date and postal code in the same input, extract those values and use them with the 'confirm_reschedule' tool."
         "If the user provides the date and requests a reschedule, but does not provide the postal code, ask for the postal code. "
         "Be clear and concise in your responses. Do not mention the tool names to the user."
         ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}")
    ]
)

# Memory Setup
memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

# Agent Setup
tools = [tracking_tool, reschedule_check_tool,
         reschedule_dates_tool, confirm_reschedule_tool]

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=False,  # Keep verbose=True for logging
    handle_parsing_errors=True,  # Helps agent recover from malformed tool calls from LLM
    max_iterations=5,  # Prevents potential infinite loops
)

# Chat Loop
print("AI 🤖: Hello 👋! How can I help you with your shipment 📦 today?")
while True:
    user_input = input("User 🔠 : ")
    if user_input.lower() == "exit":
        print("AI: Exiting chat. Goodbye!")
        break

    try:
        response = agent_executor.invoke({"query": user_input})

        # The 'output' key contains the agent's natural language response.
        ai_message = response['output']
        print(f"AI 🤖: {ai_message}")

        # Log the raw response for debugging
        logging.debug(f"Agent Response: {response}")

    except Exception as e:
        # Log full traceback
        logging.error(f"Error during agent execution: {e}", exc_info=True)
        print(
            f"AI: I'm sorry, I encountered an issue while processing your request. Please try again. (Error: {type(e).__name__})")
