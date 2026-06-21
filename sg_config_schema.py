from typing import TypedDict
from langgraph.graph import StateGraph

# 1. State schema — persisted across every node execution
class AgentState(TypedDict):
    messages: list[str]
    result: str | None

# 2. Config schema — injected at runtime, not stored in state
class GraphConfig(TypedDict):
    model_name: str
    temperature: float

# 3. Wire up the graph with both schemas
builder = StateGraph(AgentState, context_schema=GraphConfig)

from langchain_core.runnables import RunnableConfig

def call_model(state: AgentState, config: RunnableConfig) -> AgentState:
    cfg = config.get("configurable", {})
    model_name  = cfg.get("model_name", "gpt-4o-mini")
    temperature = cfg.get("temperature", 0.7)

    # Use config values instead of hardcoded constants
    response = f"[{model_name} @ t={temperature}] echo: {state['messages'][-1]}"
    return {"messages": state["messages"], "result": response}

builder.add_node("call_model", call_model)
builder.set_entry_point("call_model")
builder.set_finish_point("call_model")

graph = builder.compile()

# Invoke with runtime config
output = graph.invoke(
    {"messages": ["Hello"], "result": None},
    config={"configurable": {"model_name": "gpt-4o", "temperature": 0.2}},
)
print(output["result"])