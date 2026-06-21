from typing import TypedDict
from langgraph.graph import StateGraph, END

class GraphState(TypedDict):
    input: str
    processed: str
    result: str

def preprocess(state: GraphState) -> dict:
    print(f"[preprocess] received: '{state['input']}'")
    return {"processed": state["input"].strip().lower()}

def generate(state: GraphState) -> dict:
    print(f"[generate] working on: '{state['processed']}'")
    return {"result": f"Answer: {state['processed']}"}

builder = StateGraph(GraphState)
builder.add_node("preprocess", preprocess)
builder.add_node("generate", generate)
builder.set_entry_point("preprocess")
builder.add_edge("preprocess", "generate")
builder.add_edge("generate", END)

graph = builder.compile()   # static validation — no nodes execute yet

initial = {"input": "  Hello World  ", "processed": "", "result": ""}

# Stream to inspect each node's contribution in order
for step in graph.stream(initial):
    node_name, output = next(iter(step.items()))
    print(f"[{node_name}] emitted: {output}")

# Or invoke to get only the final merged state
# final = graph.invoke(initial)
# print("Final state:", final)