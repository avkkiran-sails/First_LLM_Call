from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

class RouterState(TypedDict):
    """State for conditional routing demonstration."""
    input_text: str
    category: str
    result: str

def categorize(state: RouterState) -> dict:
    """Categorize the input text."""
    text = state["input_text"].lower()
    if "urgent" in text or "emergency" in text:
        return {"category": "urgent"}
    elif "question" in text or "help" in text:
        return {"category": "question"}
    else:
        return {"category": "general"}

def handle_urgent(state: RouterState) -> dict:
    """Handle urgent requests."""
    return {"result": f"URGENT HANDLING: {state['input_text']}"}

def handle_question(state: RouterState) -> dict:
    """Handle questions."""
    return {"result": f"Question response: {state['input_text']}"}

def handle_general(state: RouterState) -> dict:
    """Handle general requests."""
    return {"result": f"General response: {state['input_text']}"}

def route_by_category(state: RouterState) -> str:
    """Routing function that returns the category."""
    return state["category"]

# Build graph with conditional routing
router_graph = StateGraph(RouterState)
router_graph.add_node("categorize", categorize)
router_graph.add_node("urgent", handle_urgent)
router_graph.add_node("question", handle_question)
router_graph.add_node("general", handle_general)

router_graph.add_edge(START, "categorize")
router_graph.add_conditional_edges(
    "categorize",
    route_by_category,
    {
        "urgent": "urgent",
        "question": "question",
        "general": "general"
    }
)
router_graph.add_edge("urgent", END)
router_graph.add_edge("question", END)
router_graph.add_edge("general", END)

compiled_router = router_graph.compile()

# Test with different inputs
urgent_result = compiled_router.invoke({
    "input_text": "URGENT: Server is down!",
    "category": "",
    "result": ""
})
print(f"Urgent: {urgent_result['result']}")

question_result = compiled_router.invoke({
    "input_text": "I have a question about billing",
    "category": "",
    "result": ""
})
print(f"Question: {question_result['result']}")

question_result = compiled_router.invoke({
    "input_text": "This is general feedback",
    "category": "",
    "result": ""
})
print(f"Question: {question_result['result']}")