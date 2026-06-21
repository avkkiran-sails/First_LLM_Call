from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# Define routing decisions as a Literal type
RoutingDecision = Literal["process", "skip", "error", "retry"]

class TypedRoutingState(TypedDict):
    """State with typed routing decision."""
    data: str
    decision: RoutingDecision
    attempts: int
    max_attempts: int
    output: str

def evaluate_data(state: TypedRoutingState) -> dict:
    """Evaluate data and determine routing decision."""
    data = state["data"]
    attempts = state["attempts"]

    if not data:
        return {"decision": "skip"}
    if "error" in data.lower():
        return {"decision": "error"}
    if attempts >= state["max_attempts"]:
        return {"decision": "error"}
    if len(data) < 3:
        return {"decision": "retry", "attempts": attempts + 1}
    return {"decision": "process"}

def process_data(state: TypedRoutingState) -> dict:
    """Process valid data."""
    return {"output": f"Processed: {state['data'].upper()}"}

def skip_processing(state: TypedRoutingState) -> dict:
    """Handle skipped data."""
    return {"output": "Skipped: No data provided"}

def handle_error(state: TypedRoutingState) -> dict:
    """Handle error cases."""
    return {"output": f"Error handling data: {state['data']}"}

def retry_processing(state: TypedRoutingState) -> dict:
    """Prepare for retry."""
    return {"data": state["data"] + "_retry", "decision": "process"}

def get_routing_decision(state: TypedRoutingState) -> RoutingDecision:
    """Type-safe routing function."""
    return state["decision"]

# Build graph with comprehensive route map
typed_graph = StateGraph(TypedRoutingState)
typed_graph.add_node("evaluate", evaluate_data)
typed_graph.add_node("process", process_data)
typed_graph.add_node("skip", skip_processing)
typed_graph.add_node("error", handle_error)
typed_graph.add_node("retry", retry_processing)

typed_graph.add_edge(START, "evaluate")
typed_graph.add_conditional_edges(
    "evaluate",
    get_routing_decision,
    {
        "process": "process",
        "skip": "skip",
        "error": "error",
        "retry": "retry"
    }
)

# Retry loops back to evaluate
typed_graph.add_edge("retry", "evaluate")
typed_graph.add_edge("process", END)
typed_graph.add_edge("skip", END)
typed_graph.add_edge("error", END)

compiled_typed = typed_graph.compile()

# Test various routing paths
result_process = compiled_typed.invoke({
    "data": "valid data",
    "decision": "process",
    "attempts": 0,
    "max_attempts": 3,
    "output": ""
})
print(f"Process path: {result_process['output']}")

result_skip = compiled_typed.invoke({
    "data": "", # Empty data triggers skip
    "decision": "skip",
    "attempts": 0,
    "max_attempts": 3,
    "output": ""
})
print(f"Skip path: {result_skip['output']}")

result_error = compiled_typed.invoke({
    "data": "error data",   # Data containing "error" triggers error handling
    "decision": "error",
    "attempts": 0,
    "max_attempts": 3,
    "output": ""
})
print(f"Error path: {result_error['output']}")

result_retry = compiled_typed.invoke({
    "data": "short data",   # Data too short triggers retry
    "decision": "retry",
    "attempts": 0,
    "max_attempts": 3,
    "output": ""
})
print(f"Retry path: {result_retry['output']}")
