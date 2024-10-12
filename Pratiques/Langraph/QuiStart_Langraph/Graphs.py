from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import os
#from langchain_experimental.llms.ollama_functions import OllamaFunctions


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

os.environ["TAVILY_API_KEY"] = "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"
tool = TavilySearchResults(max_results=3)
tools = [tool]
llm = ChatOpenAI(api_key="ollama",model="llama3.1:8b",base_url="http://localhost:11434/v1")
llm_with_tools = llm.bind_tools(tools)


def LLM_function(state: State):
    #print("Sate :",state)
    #print(f"State Messages : ",state["messages"])
    prompt = state["messages"] # List of Messages
    response = llm_with_tools.invoke(prompt)
    return {"messages": [response]}


graph_builder.add_node("LLM", LLM_function)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges("LLM",tools_condition,)
graph_builder.add_edge("tools", "LLM")
graph_builder.add_edge(START, "LLM")


memory = SqliteSaver.from_conn_string(":memory:")
graph1 = graph_builder.compile(
    checkpointer=memory,
    # This is new!
    interrupt_before=["tools"],
    # Note: can also interrupt **after** actions, if desired.
    # interrupt_after=["tools"]
)

graph2 = graph_builder.compile(
    checkpointer=memory,
    # This is new!
    #interrupt_before=["tools"],
    # Note: can also interrupt **after** actions, if desired.
    # interrupt_after=["tools"]
)

graph3 = graph_builder.compile()