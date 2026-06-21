from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

class FallbackState(TypedDict):
    """State with potential for unexpected values."""
    input_type: str
    processed: bool
    result: str
    error: str

def classify_input(state: FallbackState) -> dict:
    """Classify input - may produce unexpected types."""
    input_val = state.get("input_type", "")
    # Simulate various classifications including unexpected ones
    known_types = ["text", "image", "audio", "video"]
    if input_val in known_types:
        return {"input_type": input_val}
    return {"input_type": input_val}  # May be unexpected

def process_text(state: FallbackState) -> dict:
    return {"result": "Processed as text", "processed": True}

def process_image(state: FallbackState) -> dict:
    return {"result": "Processed as image", "processed": True}

def process_audio(state: FallbackState) -> dict:
    return {"result": "Processed as audio", "processed": True}

def fallback_handler(state: FallbackState) -> dict:
    """Handle unknown or unexpected input types."""
    return {
        "result": f"Fallback: Unhandled type '{state['input_type']}'",
        "error": f"No handler for type: {state['input_type']}",
        "processed": False
    }

def route_with_fallback(state: FallbackState) -> str:
    """Routing function with built-in fallback."""
    input_type = state.get("input_type", "")

    # Define known routes
    known_routes = {"text", "image", "audio"}

    # Return type if known, otherwise fallback
    if input_type in known_routes:
        return input_type
    return "fallback"

# Build graph with fallback route
fallback_graph = StateGraph(FallbackState)
fallback_graph.add_node("classify", classify_input)
fallback_graph.add_node("text", process_text)
fallback_graph.add_node("image", process_image)
fallback_graph.add_node("audio", process_audio)
fallback_graph.add_node("fallback", fallback_handler)

fallback_graph.add_edge(START, "classify")
fallback_graph.add_conditional_edges(
    "classify",
    route_with_fallback,
    {
        "text": "text",
        "image": "image",
        "audio": "audio",
        "fallback": "fallback"
    }
)

for node in ["text", "image", "audio", "fallback"]:
    fallback_graph.add_edge(node, END)

compiled_fallback = fallback_graph.compile()

# Test with unknown type
unknown_result = compiled_fallback.invoke({
    "input_type": "hologram",
    "processed": False,
    "result": "",
    "error": ""
})
print(f"Unknown type result: {unknown_result['result']}")
print(f"Error: {unknown_result['error']}")