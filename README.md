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
