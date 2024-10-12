from langchain_fireworks import ChatFireworks
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

model = ChatFireworks(api_key=os.getenv("FIREWORKS_API_KEY"),model="accounts/fireworks/models/mixtral-8x22b-instruct",temperature=0.7)
tools = [TavilySearchResults(max_results=2)]

graph = create_react_agent(model, tools)


