from typing import TypedDict
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    messages: list[str]
    result: str | None

class GraphConfig(TypedDict):
    model_name: str
    temperature: float
    max_tool_calls: int

def call_model(state: AgentState, config: RunnableConfig) -> dict:
    cfg = config.get("configurable", {})
    model = cfg.get("model_name", "gpt-4o-mini")
    budget = cfg.get("max_tool_calls", 3)
    reply = run_agent_turn(state["messages"], model, budget)
    return {"messages": [reply], "result": reply}

builder = StateGraph(AgentState, config_schema=GraphConfig)
graph = builder.compile()

# one deployed graph, two tiers:
graph.invoke(state, config={"configurable": {"model_name": "gpt-4o", "max_tool_calls": 8}})
graph.invoke(state, config={"configurable": {"model_name": "gpt-4o-mini", "max_tool_calls": 2}})