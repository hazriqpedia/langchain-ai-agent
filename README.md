# langchain-ai-agent

## What is Langchain?

LangChain is a framework for developing applications powered by large language models (LLMs). More at: https://python.langchain.com/docs/introduction/ .

## What is AI Agent?

An AI agent is a software system that uses artificial intelligence to autonomously interact with its environment, collect data, and perform tasks to achieve specific goals. Unlike traditional AI chatbots that primarily respond to user inputs, AI agents can make decisions, take actions, and even learn and adapt over time to optimize their performance.

---

## 1️⃣ Langchain without Agent

This Python script demonstrates a basic use case of the Langchain library with a Google Gemini language model. It takes a user's research query as input and prints the raw response from the language model.

**Note:** This script does **not** use a Langchain Agent. It directly interacts with the language model.

### Run

```
python ./langchain_without_agent.py
```

### Sample:

```
python ./langchain_without_agent.py
What I can help you research? How old is malaysia?
Response from LLM:  Malaysia was formed on **September 16, 1963**. So, as of today, October 26, 2023, Malaysia is **60 years old**.
```

## 2️⃣ Research Assistance AI Agent

Tools created in this project: `search_tool`, `wikipedia_tool`, `save_tool`.

### Run

```
python ./research_assistance.py
```

### Sample:

```
python ./research_assistance.py
What I can help you research? South Asia Countries and its population


> Entering new AgentExecutor chain...

{"topic": "South Asia Countries and their Population", "result": "Here's a summary of South Asian countries and their estimated populations:\n\n*   **India:** Approximately 1.4 billion\n*   **Pakistan:** Approximately 231.4 million\n*   **Bangladesh:** Approximately 169.8 million\n*   **Nepal:** Approximately 30.5 million\n*   **Sri Lanka:** Approximately 21.4 million\n*   **Afghanistan:** Approximately 40.2 million\n*   **Bhutan:** Approximately 777,540\n*   **Maldives:** Approximately 521,175", "summary": "This provides a list of South Asian countries and their approximate populations, offering a general overview of the region's demographics.", "sources": ["Search engine results", "Wikipedia"], "tools_used": ["search", "wikipedia"]}


> Finished chain.
> topic='South Asia Countries and their Population' result="Here's a summary of South Asian countries and their estimated populations:\n\n* **India:** Approximately 1.4 billion\n* **Pakistan:** Approximately 231.4 million\n* **Bangladesh:** Approximately 169.8 million\n* **Nepal:** Approximately 30.5 million\n* **Sri Lanka:** Approximately 21.4 million\n* **Afghanistan:** Approximately 40.2 million\n* **Bhutan:** Approximately 777,540\n* **Maldives:** Approximately 521,175" summary="This provides a list of South Asian countries and their approximate populations, offering a general overview of the region's demographics." sources=['Search engine results', 'Wikipedia'] tools_used=['search', 'wikipedia']

- Topic: South Asia Countries and their Population
- Summary: This provides a list of South Asian countries and their approximate populations, offering a general overview of the region's demographics.

```

### Installation

```
# Use the pipfile or....

pipenv install langchain wikipedia langchain-community langchain-google-genai python-dotenv pydantic duckduckgo-search
```

This is a based on: https://www.youtube.com/watch?v=bTMPwUgLZf0

## 2️⃣ Logistic AI Agent

This Python script implements an AI agent designed to assist with logistics-related tasks, specifically shipment tracking and rescheduling.

### Run

```
python ./logistic_ai_agent.py
```

### Tools

The agent has access to the following tools:

- `track_shipment`: Retrieves the current status and location of a shipment.
- `check_reschedule_availability`: Checks if a shipment can be rescheduled.
- `get_reschedule_dates`: Gets the available dates for rescheduling a shipment.
- `confirm_reschedule`: Confirms the rescheduling of a shipment.

### Sample

```
AI 🤖: Hello 👋! How can I help you with your shipment 📦 today?

User ➡️: I want to track my parcel
AI 🤖: Could you please provide the tracking number? It should be in the format AWB-XXXXX.

User ➡️: WB-12345
AI 🤖: I am sorry, but the tracking number should start with "AWB-". Could you please provide the correct tracking number?

User ➡️: Track AWB-12345
-- logger: Calling mock_track_shipment with tracking_number: AWB-12345
-- logger: mock_track_shipment result: Your shipment AWB-AWB-12345 is currently 'En Route' in 'Kuala Lumpur'.
AI 🤖: Your shipment AWB-12345 is currently 'En Route' in 'Kuala Lumpur'.

User ➡️: Can I reschedule it?
-- logger: Calling mock_check_reschedule_availability with tracking_number: AWB-12345
-- logger: mock_check_reschedule_availability result: Yes, you can reschedule this shipment. Please provide the new date (YYYY-MM-DD) and destination postal code.
AI 🤖: Yes, you can reschedule this shipment. Please provide the new date (YYYY-MM-DD) and destination postal code.

User ➡️: Ok, reschedule it to 2025-05-15.
AI 🤖: I will need the postal code to reschedule your shipment. Could you please provide it?

User ➡️: Postcode 56000.
-- logger: Calling mock_confirm_reschedule with tracking_number: AWB-12345, new_date: 2025-05-15, postal_code: 56000
-- logger: mock_confirm_reschedule result: Okay, I've rescheduled your shipment AWB-AWB-12345 to 2025-05-15 for delivery to postal code 56000.
AI 🤖: Okay, I've rescheduled your shipment AWB-12345 to 2025-05-15 for delivery to postal code 56000.
```

### Technical Details

- **LLM:** The agent uses the `ChatGoogleGenerativeAI` model.
- **Prompt Engineering:** The agent uses a carefully designed prompt to guide the LLM's behavior and ensure it provides accurate and helpful responses.
- **Mock API:** The script includes mock functions to simulate interactions with external APIs for tracking and rescheduling.
- **Error Handling:** The script includes error handling to catch exceptions during agent execution and provide informative error messages to the user.
- **Logging:** The script uses the `logging` module to log important information and debugging messages.
