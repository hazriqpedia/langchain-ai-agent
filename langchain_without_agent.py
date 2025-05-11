from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# LLM Set Up; Gemini is using GOOGLE_API_KEY env var.
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Get Input from user
query = input("What I can help you research? ")

# Call LLM to get response
response = llm.invoke(query)

print('Response from LLM: ', response.content)
