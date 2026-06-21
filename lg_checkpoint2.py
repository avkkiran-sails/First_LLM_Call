from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from operator import add

class CheckpointState(TypedDict):
    """State for checkpoint demonstration."""
    task_id: str
    steps_completed: Annotated[list[str], add]
    current_step: int
    total_steps: int
    is_complete: bool

def execute_step(state: CheckpointState) -> dict:
    """Execute one step of the task."""
    current = state["current_step"]
    step_name = f"Step {current}"
    return {
        "steps_completed": [step_name],
        "current_step": current + 1,
        "is_complete": current + 1 >= state["total_steps"]
    }

def should_continue(state: CheckpointState) -> str:
    """Determine if more steps needed."""
    if state["is_complete"]:
        return "end"
    return "continue"

# Build graph with conditional loop
checkpoint_graph = StateGraph(CheckpointState)
checkpoint_graph.add_node("execute", execute_step)
checkpoint_graph.add_edge(START, "execute")
checkpoint_graph.add_conditional_edges(
    "execute",
    should_continue,
    {"continue": "execute", "end": END}
)

# Compile with checkpointer
memory = MemorySaver()
compiled_checkpoint = checkpoint_graph.compile(checkpointer=memory)

# Execute partial workflow
config = {"configurable": {"thread_id": "checkpoint-demo-001"}}
initial_state = {
    "task_id": "task-001",
    "steps_completed": [],
    "current_step": 0,
    "total_steps": 5,
    "is_complete": False
}

# Run first execution
result = compiled_checkpoint.invoke(initial_state, config)
print(f"Completed steps: {result['steps_completed']}")

# Simulate resuming from checkpoint
# In real scenario, this would happen after restart
saved_state = compiled_checkpoint.get_state(config)
print(f"Saved state current_step: {saved_state.values['current_step']}")

# Resume with modified parameters (e.g., adding more steps)
# First update the state
compiled_checkpoint.update_state(
    config,
    {"total_steps": 8, "is_complete": False}
)

# Continue execution
resumed_result = compiled_checkpoint.invoke(None, config)
print(f"After resume - steps: {resumed_result['steps_completed']}")