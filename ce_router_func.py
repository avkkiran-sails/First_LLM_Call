from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    intent: str
    result: str

def router(state: State) -> str:
    intent = state.get("intent", "")
    if intent == "summarize":
        return "summarize"
    elif intent == "translate":
        return "translate"
    return "fallback"

def classify_node(state: State) -> State:
    return state  # intent already populated by the caller

def summarize_node(state: State) -> State:
    return {**state, "result": "Summary produced."}

def translate_node(state: State) -> State:
    return {**state, "result": "Translation produced."}

def fallback_node(state: State) -> State:
    return {**state, "result": "Unrecognized intent."}

route_map = {
    "summarize": "summarize_node",
    "translate": "translate_node",
    "fallback":  "fallback_node",
}

graph = StateGraph(State)
graph.add_node("classify_node", classify_node)
graph.add_node("summarize_node", summarize_node)
graph.add_node("translate_node", translate_node)
graph.add_node("fallback_node", fallback_node)
graph.set_entry_point("classify_node")
graph.add_conditional_edges("classify_node", router, route_map)
graph.add_edge("summarize_node", END)
graph.add_edge("translate_node", END)
graph.add_edge("fallback_node", END)

app = graph.compile()
result = app.invoke({"intent": "summarize", "result": ""})
print(result["result"])  # Summary produced.

result = app.invoke({"intent": "translate", "result": ""})
print(result["result"])  # Translation produced.