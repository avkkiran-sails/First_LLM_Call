from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    """Shared state contract for every node in the graph."""
    question: str
    draft: str
    final: str

def draft_node(state: AgentState) -> dict:
    """First node: read the question, produce a draft answer."""
    return {"draft": f"Draft answer for: {state['question']}"}

def finalize_node(state: AgentState) -> dict:
    """Second node: polish the draft into a final answer."""
    return {"final": state["draft"].replace("Draft", "Final")}

# 1. Instantiate with the schema
graph = StateGraph(AgentState)

# 2. Register nodes
graph.add_node("draft", draft_node)
graph.add_node("finalize", finalize_node)

# 3. Wire edges: START -> draft -> finalize -> END
graph.add_edge(START, "draft")
graph.add_edge("draft", "finalize")
graph.add_edge("finalize", END)

# 4. Compile and invoke
app = graph.compile()
result = app.invoke({"question": "What is a StateGraph?"})
print(result)