from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    input: str
    result: str
    error: str

def risky_node(state: AgentState) -> dict:
    try:
        data = state["input"]
        if not data:
            raise ValueError("Input cannot be empty")
        return {"result": f"Processed: {data}", "error": ""}
    except Exception as exc:
        return {"result": "", "error": str(exc)}

def route_on_error(state: AgentState) -> str:
    return "handle_error" if state.get("error") else "success"

def handle_error_node(state: AgentState) -> dict:
    print(f"Recovering from error: {state['error']}")
    return {}

def success_node(state: AgentState) -> dict:
    print(f"Result: {state['result']}")
    return {}

graph = StateGraph(AgentState)
graph.add_node("risky", risky_node)
graph.add_node("handle_error", handle_error_node)
graph.add_node("success", success_node)

graph.set_entry_point("risky")
graph.add_conditional_edges(
    "risky",
    route_on_error,
    {"handle_error": "handle_error", "success": "success"},
)
graph.add_edge("handle_error", END)
graph.add_edge("success", END)

app = graph.compile()

# Trigger the error branch
result = app.invoke({"input": "", "result": "", "error": ""})
print(result)

# Trigger the success branch
result = app.invoke({"input": "Hello, LangGraph!", "result": "", "error": ""})
print(result)