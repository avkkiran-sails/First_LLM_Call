import asyncio
from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END

class AsyncState(TypedDict):
    query: str
    search_results: list[str]
    llm_response: str
    processing_log: Annotated[list[str], add]

async def async_search(state: AsyncState) -> dict:
    await asyncio.sleep(0.1)  # simulated network I/O
    query = state["query"]
    return {
        "search_results": [f"Result 1 for {query}", f"Result 2 for {query}"],
        "processing_log": [f"search completed for: {query}"],
    }

async def async_llm_call(state: AsyncState) -> dict:
    await asyncio.sleep(0.2)  # simulated LLM round trip
    n = len(state["search_results"])
    return {
        "llm_response": f"Based on {n} results, the answer is...",
        "processing_log": ["llm response generated"],
    }

async def async_finalize(state: AsyncState) -> dict:
    return {
        "processing_log": [f"workflow complete ({len(state['processing_log'])} entries)"],
    }

graph = StateGraph(AsyncState)
graph.add_node("search", async_search)
graph.add_node("llm", async_llm_call)
graph.add_node("finalize", async_finalize)
graph.add_edge(START, "search")
graph.add_edge("search", "llm")
graph.add_edge("llm", "finalize")
graph.add_edge("finalize", END)
compiled = graph.compile()

async def main() -> AsyncState:
    return await compiled.ainvoke({
        "query": "LangGraph tutorial",
        "search_results": [],
        "llm_response": "",
        "processing_log": ["workflow started"],
    })

result = asyncio.run(main())
print(result["llm_response"])
print(result["processing_log"])