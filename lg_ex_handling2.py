from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

class ErrorHandlingState(TypedDict):
    """State with error tracking."""
    input_data: str
    processed_data: Optional[str]
    error: Optional[str]
    error_count: int
    success: bool

def validate_input(state: ErrorHandlingState) -> dict:
    """Validate input with error handling."""
    try:
        data = state["input_data"]
        if not data:
            return {
                "error": "Input data is empty",
                "error_count": state["error_count"] + 1,
                "success": False
            }
        if len(data) < 3:
            return {
                "error": "Input data too short (min 3 chars)",
                "error_count": state["error_count"] + 1,
                "success": False
            }
        return {"error": None, "success": True}
    except Exception as e:
        return {
            "error": f"Validation exception: {str(e)}",
            "error_count": state["error_count"] + 1,
            "success": False
        }

def process_data(state: ErrorHandlingState) -> dict:
    """Process data if validation succeeded."""
    if not state["success"]:
        return {}  # Skip processing on prior error

    try:
        data = state["input_data"]
        # Simulate processing that might fail
        if "error" in data.lower():
            raise ValueError("Data contains forbidden word 'error'")
        processed = data.upper()
        return {"processed_data": processed}
    except ValueError as e:
        return {
            "error": str(e),
            "error_count": state["error_count"] + 1,
            "success": False
        }
    except Exception as e:
        return {
            "error": f"Processing exception: {str(e)}",
            "error_count": state["error_count"] + 1,
            "success": False
        }

def finalize_result(state: ErrorHandlingState) -> dict:
    """Finalize with error summary."""
    if state["error"]:
        return {"processed_data": f"FAILED: {state['error']}"}
    return {}

# Build error-handling graph
error_graph = StateGraph(ErrorHandlingState)
error_graph.add_node("validate", validate_input)
error_graph.add_node("process", process_data)
error_graph.add_node("finalize", finalize_result)

error_graph.add_edge(START, "validate")
error_graph.add_edge("validate", "process")
error_graph.add_edge("process", "finalize")
error_graph.add_edge("finalize", END)

compiled_error = error_graph.compile()

# Test with valid input
valid_result = compiled_error.invoke({
    "input_data": "valid input",
    "processed_data": None,
    "error": None,
    "error_count": 0,
    "success": False
})
print(f"Valid - Processed: {valid_result['processed_data']}, Error: {valid_result['error']}")

# Test with invalid input
invalid_result = compiled_error.invoke({
    "input_data": "",
    "processed_data": None,
    "error": None,
    "error_count": 0,
    "success": False
})
print(f"Invalid - Processed: {invalid_result['processed_data']}, Error: {invalid_result['error']}")