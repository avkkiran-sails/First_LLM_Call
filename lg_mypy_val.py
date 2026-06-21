from typing import TypedDict, Optional, Literal, Annotated
import operator

class ConversationMessage(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str

class AgentMemory(TypedDict):
    facts: list[str]
    preferences: dict[str, str]
    last_interaction: Optional[str]

class ComprehensiveAgentState(TypedDict):
    messages: Annotated[list[ConversationMessage], operator.add]
    current_input: str
    memory: AgentMemory
    current_phase: Literal["input", "reasoning", "action", "output"]
    iteration_count: int
    max_iterations: int
    error: Optional[str]
    should_continue: bool

initial_state: ComprehensiveAgentState = {
    "messages": [],
    "current_input": "",
    "memory": {
        "facts": [],
        "preferences": {},
        "last_interaction": None,
    },
    "current_phase": "input",
    "iteration_count": 0,
    "max_iterations": 10,
    "error": None,
    "should_continue": True,
}

print(f"State fields: {list(initial_state.keys())}")