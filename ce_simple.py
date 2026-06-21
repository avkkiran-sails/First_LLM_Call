from langgraph.graph import StateGraph, END
from typing import TypedDict

class GraphState(TypedDict):
    query: str
    needs_search: bool

def should_search(state: GraphState) -> str:
    """Condition function: returns next node name or END."""
    if state["needs_search"]:
        return "search"
    return END

def classify(state: GraphState) -> GraphState:
    state["needs_search"] = "weather" in state["query"].lower()
    return state

def search(state: GraphState) -> GraphState:
    print(f"Searching for: {state['query']}")
    return state

builder = StateGraph(GraphState)
builder.add_node("classify", classify)
builder.add_node("search", search)
builder.set_entry_point("classify")
builder.add_conditional_edges("classify", should_search)
graph = builder.compile()

# "classify" sets needs_search=True → routes to "search"
graph.invoke({"query": "what is the weather in Paris", "needs_search": False})

# "classify" sets needs_search=False → routes to END
graph.invoke({"query": "tell me a joke", "needs_search": False})