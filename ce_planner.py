from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class AgentState(TypedDict):
    next_action: Literal["call_tool", "ask_clarification", "finish"]
    tool_result: str

def planner_router(state: AgentState) -> str:
    return state["next_action"]

route_map = {
    "call_tool": "tool_executor",
    "ask_clarification": "clarifier",
    "finish": END,
}

# define planner node
def planner_node(state: AgentState) -> AgentState:
    return {**state, "tool_result": "Planning completed."}

#define tool executor node with a sample print statement
def tool_executor_node(state: AgentState) -> AgentState:
    return {**state, "tool_result": "Tool executed."}

#define clarifier node with a sample print statement
def clarifier_node(state: AgentState) -> AgentState:
    return {**state, "tool_result": "Asked for clarification."} 


graph = StateGraph(AgentState)

graph.add_conditional_edges("planner", planner_router, route_map)

graph.add_node("planner", planner_node)  # Identity node for routing
graph.add_node("tool_executor", tool_executor_node)
graph.add_node("clarifier", clarifier_node)
graph.set_entry_point("planner")
graph.add_edge("tool_executor", END)
graph.add_edge("clarifier", END)

app = graph.compile()
result = app.invoke({"next_action": "call_tool", "tool_result": ""})
print(result["tool_result"])  # Tool executed.

result = app.invoke({"next_action": "ask_clarification", "tool_result": ""})
print(result["tool_result"])  # Asked for clarification.

result = app.invoke({"next_action": "finish", "tool_result": ""})
print(result["tool_result"])  # Finish.