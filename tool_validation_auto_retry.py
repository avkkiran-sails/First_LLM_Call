import json
import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()

# 1. Define the State (the "memory" of our graph)
class State(TypedDict):
    # add_messages appends new messages to the existing list
    messages: Annotated[list[BaseMessage], add_messages]

# 2. Define the Tool with Validation Logic
@tool
def book_flight(destination: str, seat_class: str):
    """Books a flight to a destination."""
    # Validation logic
    valid_classes = ["economy", "business", "first"]
    if seat_class.lower() not in valid_classes:
        return f"Error: '{seat_class}' is invalid. You must choose from: {', '.join(valid_classes)}."
    
    return f"Success! Flight to {destination} booked in {seat_class} class."

tools = [book_flight]
# We bind the tools to the model
model = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY")).bind_tools(tools)

# 3. Define the Nodes
def call_model(state: State):
    """The Agent node that decides what to do."""
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# ToolNode is a prebuilt node that executes the @tool functions
tool_node = ToolNode(tools)

# 4. Define the Routing Logic (The "Loop" Control)
def router(state: State):
    """
    Determines where the graph goes next.
    """
    last_message = state["messages"][-1]
    
    # If the LLM didn't call a tool, we are finished
    if not last_message.tool_calls:
        return END
    
    # If a tool was called, we proceed to the tools node
    return "tools"

def validate_output(state: State):
    """
    This edge checks if the tool execution was successful.
    If 'Error' is in the message, it returns to 'agent' to retry.
    """
    last_message = state["messages"][-1]
    
    if isinstance(last_message, ToolMessage) and "Error" in last_message.content:
        print(f"\n--- VALIDATION FAILED: Retrying... ---\n")
        return "agent"
    
    return END

# 5. Build the Graph
workflow = StateGraph(State)

# Add our nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entry point
workflow.set_entry_point("agent")

# Logic: After agent, check if we need to call tools
workflow.add_conditional_edges("agent", router)

# Logic: After tools, check if validation passed or if we need to loop back
workflow.add_conditional_edges("tools", validate_output)

# Compile the graph
app = workflow.compile()

# 6. Execute
# We intentionally provide a wrong 'seat_class' (Luxury) to trigger the loop
inputs = {"allowed_objects":'messages',"messages": [HumanMessage(content="Book me a first class flight to Tokyo")]}

for event in app.stream(inputs):
    for value in event.values():
        last_msg = value["messages"][-1]
        print(f"Node: {list(event.keys())[0]}")
        print(f"Content: {last_msg.content if hasattr(last_msg, 'content') else 'Tool Call'}\n")