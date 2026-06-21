from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from operator import add


# Define tools using LangGraph's @tool decorator
@tool
def get_weather(location: str, units: str = "celsius") -> str:
    """
    Get current weather for a location.

    Args:
        location: City and country (e.g., 'London, UK')
        units: Temperature units ('celsius' or 'fahrenheit')

    Returns:
        Weather description string
    """
    # Mock implementation
    return f"Weather in {location}: 22 degrees {units}"


@tool
def search_web(query: str) -> str:
    """
    Search the web for information.

    Args:
        query: Search query string

    Returns:
        Search results summary
    """
    # Mock implementation
    return f"Search results for: {query}"


# Define the graph state
class AgentState(TypedDict):
    messages: Annotated[list, add]


# Create the LangGraph agent
def create_langgraph_agent():
    """
    Create a tool-calling agent using LangGraph.

    This demonstrates how LangGraph abstracts the manual
    loop and dispatching you learned earlier.

    Returns:
        Compiled StateGraph agent
    """
    # Initialize LLM with tools bound
    tools = [get_weather, search_web]
    llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)

    # Define the agent node

    def agent_node(state: AgentState):
        messages = state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response]}

    # Create the graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    # Set entry point
    graph.set_entry_point("agent")

    # Add conditional edge for tool calling
    graph.add_conditional_edges(
        "agent",
        tools_condition,  # Built-in condition for tool calls
        {
            "tools": "tools",
            END: END
        }
    )

    # Tools always return to agent
    graph.add_edge("tools", "agent")

    return graph.compile()


# Main execution
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from langchain_core.messages import HumanMessage
    
    load_dotenv()
    
    # Create the agent
    agent = create_langgraph_agent()
    
    # Initial message
    initial_message = "What's the weather in New York and search for AI news"
    
    # Run the agent
    print(f"User: {initial_message}\n")
    
    state = {
        "messages": [HumanMessage(content=initial_message)]
    }
    
    # Execute the graph
    output = agent.invoke(state)
    
    # Print results
    print("Agent Results:")
    print("=" * 50)
    for message in output["messages"]:
        print(f"\n{message.__class__.__name__}:")
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print(f"Tool calls: {message.tool_calls}")
        if hasattr(message, 'content'):
            print(f"Content: {message.content}")
