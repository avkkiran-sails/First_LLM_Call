from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from datetime import datetime

class InitializableState(TypedDict):
    """State with various initialization requirements."""
    # Always required
    session_id: str
    created_at: str

    # Optional with defaults
    user_id: Optional[str]
    preferences: dict

    # Computed during execution
    step_count: int
    last_updated: str
    result: Optional[str]

def create_default_state(session_id: str, user_id: Optional[str] = None) -> InitializableState:
    """Factory function for creating properly initialized state."""
    now = datetime.now().isoformat()
    return {
        "session_id": session_id,
        "created_at": now,
        "user_id": user_id,
        "preferences": {},
        "step_count": 0,
        "last_updated": now,
        "result": None
    }

def create_state_with_context(
    session_id: str,
    context: dict
) -> InitializableState:
    """Create state with preloaded context."""
    now = datetime.now().isoformat()
    return {
        "session_id": session_id,
        "created_at": now,
        "user_id": context.get("user_id"),
        "preferences": context.get("preferences", {}),
        "step_count": 0,
        "last_updated": now,
        "result": None
    }

def process_step(state: InitializableState) -> dict:
    """Process a workflow step."""
    now = datetime.now().isoformat()
    return {
        "step_count": state["step_count"] + 1,
        "last_updated": now
    }

def complete_workflow(state: InitializableState) -> dict:
    """Complete the workflow."""
    return {
        "result": f"Completed in {state['step_count']} steps"
    }

# Build graph
init_graph = StateGraph(InitializableState)
init_graph.add_node("process", process_step)
init_graph.add_node("complete", complete_workflow)
init_graph.add_edge(START, "process")
init_graph.add_edge("process", "complete")
init_graph.add_edge("complete", END)
compiled_init = init_graph.compile()

# Use factory function for initialization
default_state = create_default_state("sess-001")
result_default = compiled_init.invoke(default_state)
print(f"Default init result: {result_default['result']}")

# Use context-aware initialization
context = {"user_id": "user-123", "preferences": {"theme": "dark"}}
context_state = create_state_with_context("sess-002", context)
result_context = compiled_init.invoke(context_state)
print(f"Context init result: {result_context['result']}")
print(f"User preferences: {result_context['preferences']}")