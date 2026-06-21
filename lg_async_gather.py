import asyncio
from operator import add
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    tool_calls: list[dict]
    tool_results: Annotated[list[dict], add]

async def call_tool(spec: dict) -> dict:
    await asyncio.sleep(0.2)
    return {"name": spec["name"], "output": f"result-{spec['name']}"}

async def dispatch_tools(state: AgentState) -> dict:
    results = await asyncio.gather(*(call_tool(s) for s in state["tool_calls"]))
    return {"tool_results": results}

graph = StateGraph(AgentState)
graph.add_node("dispatch", dispatch_tools)
graph.add_edge(START, "dispatch")
graph.add_edge("dispatch", END)
compiled = graph.compile()

async def main():
    result = await compiled.ainvoke({
        "tool_calls": [{"name": "A"}, {"name": "B"}, {"name": "C"}],
        "tool_results": []
    })
    print(result["tool_results"])

asyncio.run(main())