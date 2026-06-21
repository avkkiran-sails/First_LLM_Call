from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class LifecycleState(TypedDict):
    """State demonstrating graph lifecycle."""
    input_text: str
    processed: bool
    output: str

def validate_input(state: LifecycleState) -> dict:
    """Validate the input text."""
    text = state["input_text"]
    if not text or len(text) < 3:
        return {"output": "Invalid input: too short", "processed": False}
    return {"processed": True}

def process_text(state: LifecycleState) -> dict:
    """Process the validated text."""
    text = state["input_text"]
    result = text.upper()
    return {"output": f"Processed: {result}"}

# PHASE 1: Definition
lifecycle_graph = StateGraph(LifecycleState)
lifecycle_graph.add_node("validate", validate_input)
lifecycle_graph.add_node("process", process_text)
lifecycle_graph.add_edge(START, "validate")
lifecycle_graph.add_edge("validate", "process")
lifecycle_graph.add_edge("process", END)

# PHASE 2: Compilation
checkpointer = MemorySaver()
compiled_graph = lifecycle_graph.compile(checkpointer=checkpointer)

# PHASE 3: Execution
config = {"configurable": {"thread_id": "lifecycle-demo-001"}}
initial = {"input_text": "hello world", "processed": False, "output": ""}

result = compiled_graph.invoke(initial, config)
print(f"Processed: {result['processed']}")
print(f"Output: {result['output']}")

# Verify checkpoint was saved
state_history = list(compiled_graph.get_state_history(config))
print(f"Checkpoints: {state_history}")
print(f"Checkpoint count: {len(state_history)}")