from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from research_assistance_tools import search_tool, wikipedia_tool, save_tool

load_dotenv()


class ResearchResponse(BaseModel):
    ''' Pydantic Set up. Output will folow this model. '''
    topic: str
    result: str
    summary: str
    sources: list[str]
    tools_used: list[str]


# LLM Set Up; Gemini is using GOOGLE_API_KEY env var.
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

parser = PydanticOutputParser(pydantic_object=ResearchResponse)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a research assistant that will help generate a research paper. Answer the user query and use necessery tools. Wrap the output in this format and provide no other text\n{format_instructions}"),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

# Set Available Tools
tools = [search_tool, wikipedia_tool, save_tool]

# Create AI Agent
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

query = input("What I can help you research? ")

# Invoke AI Agent
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
raw_response = agent_executor.invoke({"query": query})

# print(raw_response)

try:
    # Try to parse the raw response
    structured_response = parser.parse(raw_response.get("output"))
    print(structured_response)
    print('- Topic: ', structured_response.topic)
    print('- Summary: ', structured_response.summary)
except Exception as e:
    print("Error parsing: ", e, " Raw Response: ", raw_response)
